"""Update discovery and fail-closed, separately signed version-slot staging."""
import base64,json,re,time,zipfile,stat,shutil,tempfile,os
from pathlib import Path,PurePosixPath
import httpx
from packaging.version import Version,InvalidVersion
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from sqlalchemy import select
from .db import Update,Channel,Job,Account,Credential,audit
from .catalog import SOURCES
IDENT=re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._+-]{0,100}$')
class Updates:
    def __init__(self,db,state):self.db=db;self.root=Path(state)/'engine-versions';self.root.mkdir(parents=True,exist_ok=True)
    async def discover(self):
        found=[]
        async with httpx.AsyncClient(timeout=25,follow_redirects=False,headers={'Accept':'application/vnd.github+json','User-Agent':'OmniDispatch/0.1'}) as client:
            for engine,repo in SOURCES.items():
                try:
                    response=await client.get(f'https://api.github.com/repos/{repo}/releases/latest')
                    if response.status_code==404:found.append({'engine':engine,'status':'no_release'});continue
                    response.raise_for_status();data=response.json();version=data['tag_name']
                    if not IDENT.fullmatch(version):raise ValueError('Invalid release version')
                    with self.db.tx() as s:
                        item=s.scalar(select(Update).where(Update.engine==engine,Update.version==version))
                        if not item:
                            s.add(Update(engine=engine,version=version,source=f'https://github.com/{repo}/releases/tag/{version}',data={'published_at':data.get('published_at'),'assets':[{'name':x['name'],'url':x['browser_download_url'],'size':x['size']} for x in data.get('assets',[])],'trust':'upstream_metadata_only'}))
                            audit(s,'update.discovered',engine,version=version)
                    found.append({'engine':engine,'version':version,'status':'available'})
                except Exception as e:found.append({'engine':engine,'status':'check_failed','error':type(e).__name__})
        return found
    def stage(self,update_id,archive,signature,public_key):
        """Trust root must be configured locally, never supplied by upload or upstream archive."""
        if not public_key:raise ValueError('尚未配置受信签名公钥；保持候选状态')
        raw=Path(archive).read_bytes()
        if len(raw)>512*1024*1024:raise ValueError('更新包超过 512 MiB')
        try:Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key,validate=True)).verify(base64.b64decode(signature,validate=True),raw)
        except InvalidSignature:raise ValueError('更新签名校验失败') from None
        with self.db.tx() as s:
            item=s.get(Update,update_id)
            if not item or item.state!='available':raise ValueError('更新不存在或状态不允许安装')
            if not IDENT.fullmatch(item.engine) or not IDENT.fullmatch(item.version):raise ValueError('非法版本路径')
            destination=self.root/item.engine/item.version
            if destination.exists():raise ValueError('此版本槽位已存在，拒绝覆盖')
            with tempfile.TemporaryDirectory(dir=self.root) as temp:
                with zipfile.ZipFile(archive) as z:
                    members=z.infolist();total=0;names=set()
                    if 'omni-engine.json' not in z.namelist() or z.getinfo('omni-engine.json').file_size>65536:raise ValueError('缺少合法大小的引擎 manifest')
                    if len(members)>20000:raise ValueError('压缩包条目过多')
                    for info in members:
                        p=PurePosixPath(info.filename);total+=info.file_size
                        name=info.filename.casefold()
                        if name in names or '\\' in info.filename or p.is_absolute() or '..' in p.parts or any(':' in part for part in p.parts) or stat.S_ISLNK(info.external_attr>>16):raise ValueError('压缩包包含不安全路径')
                        names.add(name)
                        if total>2*1024**3:raise ValueError('展开后超过 2 GiB')
                    z.extractall(temp)
                manifest=json.loads((Path(temp)/'omni-engine.json').read_text())
                if not isinstance(manifest,dict):raise ValueError('引擎 manifest 必须是对象')
                if manifest.get('executable'):
                    program=(Path(temp)/manifest['executable']).resolve()
                    if not program.is_relative_to(Path(temp).resolve()) or not program.is_file():raise ValueError('程序必须位于签名安装包内')
                if manifest.get('engine')!=item.engine or manifest.get('version')!=item.version or manifest.get('adapter_protocol')!=1:raise ValueError('引擎 manifest 不匹配')
                destination.parent.mkdir(parents=True,exist_ok=True);shutil.move(temp,destination)
            item.state='staged';item.data={**item.data,'signed':True,'manifest':manifest};audit(s,'update.staged',item.id)
    def transition(self,update_id,action):
        with self.db.tx() as s:
            item=s.get(Update,update_id,with_for_update=True)
            if not item:raise ValueError('更新不存在')
            if action=='canary':
                other=s.scalar(select(Update).where(Update.engine==item.engine,Update.state=='canary',Update.id!=item.id))
                if other:raise ValueError('同一引擎已有灰度版本，先完成或回滚')
                if item.state!='staged':raise ValueError('需先安装已签名版本')
                manifest=item.data.get('manifest',{})
                executable=manifest.get('executable')
                if not executable or not (self.root/item.engine/item.version/executable).is_file():raise ValueError('安装包未声明可运行的原生程序')
                accounts=s.scalars(select(Account).where(Account.canary_allowed==True)).all()
                if not accounts:raise ValueError('没有明确允许灰度的测试账号')
                bases=s.scalars(select(Channel).where(Channel.engine==item.engine)).all()
                bases=[c for c in bases if not c.capabilities.get('is_canary')]
                previous={c.id:{'version':c.version,'health':c.health,'enabled':c.enabled,'evidence':c.evidence} for c in bases}
                for base in bases:
                    cid=base.id+'--canary';clone=s.get(Channel,cid)
                    if not clone:clone=Channel(id=cid,engine=base.engine,platform=base.platform);s.add(clone)
                    clone.version=item.version;clone.priority=100;clone.enabled=True;clone.health='canary_ready';clone.failures=0;clone.open_until=0
                    clone.capabilities={**base.capabilities,'is_canary':True};clone.evidence={'source_channel':base.id}
                    for account in accounts:
                        original=s.scalar(select(Credential).where(Credential.account_id==account.id,Credential.channel_id==base.id))
                        existing=s.scalar(select(Credential).where(Credential.account_id==account.id,Credential.channel_id==cid))
                        if original and not existing:s.add(Credential(account_id=account.id,channel_id=cid,ciphertext=original.ciphertext,state=original.state))
                self._pointer(item.engine,item.version,'canary')
                item.state='canary';item.data={**item.data,'canary_started':time.time(),'live_successes':0,'live_failures':0,'by_channel':{},'previous':previous}
            elif action=='promote':
                if item.state!='canary' or time.time()-item.data.get('canary_started',time.time())<86400 or item.data.get('live_successes',0)<3:raise ValueError('需完成至少 24 小时灰度及 3 次真实成功发布')
                if item.data.get('live_failures',0):raise ValueError('灰度存在失败，需先处置')
                previous=item.data.get('previous',{})
                if not previous:raise ValueError('缺少旧版本快照')
                for cid,old in previous.items():
                    stats=item.data.get('by_channel',{}).get(cid+'--canary',{})
                    if old.get('enabled') and (stats.get('successes',0)<3 or stats.get('failures',0)):raise ValueError('每条在用通道均需三次成功灰度且无失败')
                for cid,old in previous.items():
                    channel=s.get(Channel,cid);clone=s.get(Channel,cid+'--canary')
                    if channel:
                        channel.version=item.version;channel.health='healthy' if old.get('enabled') else 'unverified';channel.enabled=old.get('enabled',False)
                        channel.evidence={'method':'canary_promotion','version':item.version,'at':time.time(),'samples':item.data.get('by_channel',{}).get(cid+'--canary',{})}
                    if clone:clone.enabled=False
                item.state='active';item.data={**item.data,'activated':time.time()}
                self._pointer(item.engine,item.version);self._clear_canary(item.engine)
            elif action=='rollback':
                if item.state not in {'active','canary'}:raise ValueError('该版本未激活')
                was_active=item.state=='active'
                for cid,old in item.data.get('previous',{}).items():
                    channel=s.get(Channel,cid);clone=s.get(Channel,cid+'--canary')
                    if channel and was_active and channel.version==item.version:
                        channel.version=old['version'];channel.enabled=old.get('enabled',False);channel.health=old.get('health','unverified');channel.evidence=old.get('evidence',{})
                    if clone:clone.enabled=False
                item.state='rolled_back';self._clear_canary(item.engine)
                previous={v['version'] for v in item.data.get('previous',{}).values()}
                if was_active and len(previous)==1:self._pointer(item.engine,previous.pop())
            else:raise ValueError('不支持的更新动作')
            audit(s,'update.'+action,item.id)
    def _clear_canary(self,engine):
        (self.root/engine/'canary.json').unlink(missing_ok=True)
    def _pointer(self,engine,version,name='active'):
        folder=self.root/engine;folder.mkdir(exist_ok=True)
        temp=folder/(name+'.tmp');temp.write_text(json.dumps({'version':version}));os.replace(temp,folder/(name+'.json'))

    async def sync_feed(self,url,public_key,auto_promote=False):
        """Optional publisher feed. Signed metadata, monotonic generation, same-origin artifacts."""
        from urllib.parse import urlsplit
        from .db import Setting
        import secrets
        if not url or not public_key:return {'enabled':False,'reason':'trusted_feed_not_configured'}
        origin=urlsplit(url)
        if origin.scheme!='https' or origin.username or origin.password:raise ValueError('更新源必须为不含用户凭证的 HTTPS 地址')
        key=Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key,validate=True))
        async with httpx.AsyncClient(timeout=60,follow_redirects=False) as client:
            response=await client.get(url);response.raise_for_status()
            if len(response.content)>2*1024*1024:raise ValueError('更新元数据过大')
            envelope=response.json();payload=base64.b64decode(envelope['payload'],validate=True)
            key.verify(base64.b64decode(envelope['signature'],validate=True),payload);feed=json.loads(payload)
            if not isinstance(feed.get('generation'),int) or not time.time()<feed.get('expires',0)<=time.time()+8*86400:raise ValueError('更新元数据过期或有效期过长')
            with self.db.tx() as s:
                old=s.get(Setting,'update_feed_generation')
                if old and feed['generation']<old.value['generation']:raise ValueError('拒绝回退的更新元数据')
                if old:old.value={'generation':feed['generation']}
                else:s.add(Setting(key='update_feed_generation',value={'generation':feed['generation']}))
            for release in feed.get('releases',[]):
                engine=release['engine'];version=release['version'];location=urlsplit(release['url'])
                if not IDENT.fullmatch(engine) or not IDENT.fullmatch(version):raise ValueError('非法更新标识')
                if location.scheme!='https' or location.netloc!=origin.netloc:raise ValueError('更新文件必须来自已配置更新源的同一 HTTPS 主机')
                with self.db.tx() as s:
                    item=s.scalar(select(Update).where(Update.engine==engine,Update.version==version))
                    if not item:item=Update(engine=engine,version=version,source=release['url'],data={'trust':'signed_publisher_feed'});s.add(item);s.flush()
                    identifier=item.id;state=item.state
                if state!='available' or release.get('auto_stage') is not True:continue
                temporary=self.root/('download-'+secrets.token_hex(12)+'.zip')
                try:
                    size=0
                    async with client.stream('GET',release['url']) as data:
                        data.raise_for_status()
                        with temporary.open('xb') as file:
                            async for chunk in data.aiter_bytes(1024*1024):
                                size+=len(chunk)
                                if size>512*1024**2:raise ValueError('更新包过大')
                                file.write(chunk)
                    if size!=release['bytes']:raise ValueError('更新包大小不符')
                    self.stage(identifier,temporary,release['signature'],public_key)
                    # Only compatible patch updates with no data/credential migrations may enter canary unattended.
                    with self.db.tx() as s:
                        item=s.get(Update,identifier);manifest=item.data.get('manifest',{})
                        current={c.version for c in s.scalars(select(Channel).where(Channel.engine==engine,Channel.enabled==True)) if not c.capabilities.get('is_canary')}
                    try:
                        new=Version(version);compatible=bool(current) and all(Version(v).release[:2]==new.release[:2] and Version(v)<new for v in current)
                    except InvalidVersion:compatible=False
                    if compatible and manifest.get('migration')=='none':
                        try:
                            self.transition(identifier,'canary')
                            with self.db.tx() as s:
                                item=s.get(Update,identifier);item.data={**item.data,'auto_eligible':True}
                        except ValueError:pass
                finally:temporary.unlink(missing_ok=True)
        if auto_promote:
            with self.db.tx() as s:canaries=[u.id for u in s.scalars(select(Update).where(Update.state=='canary')) if u.data.get('auto_eligible')]
            for identifier in canaries:
                try:self.transition(identifier,'promote')
                except ValueError:pass
        return {'enabled':True,'generation':feed['generation']}
