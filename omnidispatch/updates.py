"""Update discovery and fail-closed, separately signed version-slot staging."""
import base64,json,re,time,zipfile,stat,shutil,tempfile,os
from pathlib import Path,PurePosixPath
import httpx
from packaging.version import Version,InvalidVersion
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from sqlalchemy import select
from .db import Update,Channel,Job,audit
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
        Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key,validate=True)).verify(base64.b64decode(signature,validate=True),raw)
        with self.db.tx() as s:
            item=s.get(Update,update_id)
            if not item or item.state!='available':raise ValueError('更新不存在或状态不允许安装')
            if not IDENT.fullmatch(item.engine) or not IDENT.fullmatch(item.version):raise ValueError('非法版本路径')
            destination=self.root/item.engine/item.version
            if destination.exists():raise ValueError('此版本槽位已存在，拒绝覆盖')
            with tempfile.TemporaryDirectory(dir=self.root) as temp:
                with zipfile.ZipFile(archive) as z:
                    members=z.infolist();total=0;names=set()
                    if len(members)>20000:raise ValueError('压缩包条目过多')
                    for info in members:
                        p=PurePosixPath(info.filename);total+=info.file_size
                        name=info.filename.casefold()
                        if name in names or '\\' in info.filename or p.is_absolute() or '..' in p.parts or any(':' in part for part in p.parts) or stat.S_ISLNK(info.external_attr>>16):raise ValueError('压缩包包含不安全路径')
                        names.add(name)
                        if total>2*1024**3:raise ValueError('展开后超过 2 GiB')
                    z.extractall(temp)
                manifest=json.loads((Path(temp)/'omni-engine.json').read_text())
                if manifest.get('engine')!=item.engine or manifest.get('version')!=item.version or manifest.get('adapter_protocol')!=1:raise ValueError('引擎 manifest 不匹配')
                destination.parent.mkdir(parents=True,exist_ok=True);shutil.move(temp,destination)
            item.state='staged';item.data={**item.data,'signed':True,'manifest':manifest};audit(s,'update.staged',item.id)
    def transition(self,update_id,action):
        with self.db.tx() as s:
            item=s.get(Update,update_id,with_for_update=True)
            if not item:raise ValueError('更新不存在')
            if action=='canary':
                if item.state!='staged':raise ValueError('需先安装已签名版本')
                item.state='canary';item.data={**item.data,'canary_started':time.time(),'live_successes':0}
            elif action=='promote':
                if item.state!='canary' or time.time()-item.data.get('canary_started',time.time())<86400 or item.data.get('live_successes',0)<3:raise ValueError('需完成至少 24 小时灰度及 3 次真实成功发布')
                if item.data.get('live_failures',0):raise ValueError('灰度存在失败，需先处置')
                channels=s.scalars(select(Channel).where(Channel.engine==item.engine)).all()
                previous={c.id:c.version for c in channels}
                # Routing only sees the new version on agents advertising readiness. In-flight jobs pin old version.
                for channel in channels:channel.version=item.version;channel.health='unverified';channel.enabled=False
                item.state='active';item.data={**item.data,'previous':previous,'activated':time.time()}
                self._pointer(item.engine,item.version)
            elif action=='rollback':
                if item.state not in {'active','canary'}:raise ValueError('该版本未激活')
                for cid,version in item.data.get('previous',{}).items():
                    channel=s.get(Channel,cid)
                    if channel and channel.version==item.version:channel.version=version;channel.enabled=False;channel.health='unverified'
                item.state='rolled_back'
                previous=set(item.data.get('previous',{}).values())
                if len(previous)==1:self._pointer(item.engine,previous.pop())
            else:raise ValueError('不支持的更新动作')
            audit(s,'update.'+action,item.id)
    def _pointer(self,engine,version):
        folder=self.root/engine;folder.mkdir(exist_ok=True)
        temp=folder/'active.tmp';temp.write_text(json.dumps({'version':version}));os.replace(temp,folder/'active.json')
