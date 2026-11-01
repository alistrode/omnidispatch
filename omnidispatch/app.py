from __future__ import annotations
import os,json,time,asyncio,secrets,contextlib,subprocess
from pathlib import Path
from collections import Counter
import pyotp
from fastapi import FastAPI,Request,HTTPException,UploadFile,File,Depends
from fastapi.responses import FileResponse,StreamingResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from sqlalchemy import select,delete,func
from pydantic import BaseModel,Field,ConfigDict
from .db import Database,Admin,Session,Recovery,LoginGuard,Account,Credential,Channel,Job,Attempt,Asset,AssetUpload,Agent,Audit,Update,audit,uid
from .catalog import seed,PLATFORMS
from .queue import Queue,Conflict
from .security import Vault,ph,verify,new_token
from .updates import Updates

def public(obj,exclude=()):return {c.name:getattr(obj,c.name) for c in obj.__table__.columns if c.name not in exclude}
class Strict(BaseModel):model_config=ConfigDict(extra='forbid')
class Login(Strict):username:str=Field(max_length=80);password:str=Field(max_length=300);totp:str=''
class AccountIn(Strict):label:str=Field(min_length=1,max_length=120);platform:str;min_interval:int=Field(default=60,ge=30,le=86400);egress:dict=Field(default_factory=lambda:{'mode':'direct'});canary_allowed:bool=False
class CredIn(Strict):channel_id:str;value:dict
class ChannelIn(Strict):version:str=Field(min_length=1,max_length=100);priority:int=Field(default=50,ge=0,le=100);enabled:bool=False
class JobIn(Strict):idempotency_key:str=Field(min_length=8,max_length=120);account_id:str;title:str=Field(min_length=1,max_length=300);description:str=Field(default='',max_length=10000);kind:str='video';assets:list[str]=Field(default_factory=list,max_length=20);due:float|None=None;options:dict=Field(default_factory=dict);canary:bool=False;verification_channel:str|None=None;action:str='publish';target_url:str='';target_comment_id:str='';delivery:str='published'
class UploadIn(Strict):name:str=Field(min_length=1,max_length=200);size:int=Field(gt=0,le=2*1024**3)
class Action(Strict):action:str;remote_id:str|None=None
class AccountSelection(Strict):account_id:str
class LocalChannelIn(Strict):version:str;usage_acknowledged:bool=False
class AgentIn(Strict):label:str=Field(min_length=1,max_length=120)
class Beat(Strict):capabilities:dict
class Generation(Strict):generation:int=Field(ge=1)
class Result(Generation):result:dict
class PasswordIn(Strict):current_password:str;password:str=Field(min_length=12,max_length=300)
class TotpIn(Strict):password:str;code:str=''

def create_app(state=None,database_url=None,*,background=True):
    state=Path(state or os.getenv('OMNI_STATE','state')).resolve();state.mkdir(parents=True,exist_ok=True)
    db=Database(database_url or os.getenv('OMNI_DATABASE_URL',f'sqlite:///{state / "hub.db"}'));db.initialize()
    vault=Vault(state);queue=Queue(db,vault);updates=Updates(db,state)
    with db.tx() as s:seed(s)
    async def maintenance():
        while True:
            try:
                with db.tx() as s:
                    queue.expire(s);s.execute(delete(Session).where(Session.expires<time.time()))
                    stale=s.scalars(select(AssetUpload).where(AssetUpload.state=='open',AssetUpload.created<time.time()-86400)).all()
                    stale_ids=[u.id for u in stale]
                    for upload in stale:s.delete(upload)
                import shutil
                for identifier in stale_ids:shutil.rmtree(state/'uploads'/identifier,ignore_errors=True)
            except Exception:pass
            await asyncio.sleep(10)
    async def update_loop():
        await asyncio.sleep(20)
        while True:
            try:
                feed=os.getenv('OMNI_UPDATE_FEED_URL','');public_key=os.getenv('OMNI_UPDATE_PUBLIC_KEY','')
                if feed:await updates.sync_feed(feed,public_key,os.getenv('OMNI_AUTO_PROMOTE','0')=='1')
                else:await updates.discover()
            except Exception as e:
                with db.tx() as s:audit(s,'update.check_failed','publisher',error_class=type(e).__name__)
            await asyncio.sleep((3600 if os.getenv('OMNI_UPDATE_FEED_URL') else 86400)+secrets.randbelow(300))
    @contextlib.asynccontextmanager
    async def lifespan(app):
        tasks=[asyncio.create_task(maintenance()),asyncio.create_task(update_loop())] if background else []
        yield
        for task in tasks:task.cancel()
        for task in tasks:
            with contextlib.suppress(asyncio.CancelledError):await task
        db.engine.dispose()
    app=FastAPI(title='OmniDispatch',version='0.1.0',lifespan=lifespan,docs_url=None,redoc_url=None)
    app.add_middleware(GZipMiddleware,minimum_size=1000)
    app.state.db=db;app.state.vault=vault;app.state.queue=queue
    secure=os.getenv('OMNI_SECURE_COOKIE','0')=='1'
    @app.middleware('http')
    async def headers(request,call_next):
        # Reject browser cross-site state changes even before authentication/CSRF checks.
        if request.method not in {'GET','HEAD','OPTIONS'}:
            origin=request.headers.get('origin')
            expected=os.getenv('OMNI_PUBLIC_ORIGIN',str(request.base_url).rstrip('/'))
            if origin and origin!=expected:return JSONResponse({'detail':'Origin 校验失败'},status_code=403)
        response=await call_next(request)
        response.headers.update({'X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','Referrer-Policy':'no-referrer','Cache-Control':'public, max-age=31536000, immutable' if request.url.path.startswith('/assets/') else 'no-store','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; frame-ancestors 'none'"})
        return response
    @app.exception_handler(Conflict)
    async def conflict(_,e):return JSONResponse({'detail':str(e)},status_code=409)
    @app.exception_handler(ValueError)
    async def invalid(_,e):return JSONResponse({'detail':str(e)},status_code=400)
    def admin(request:Request):
        token=request.cookies.get('omni_session','');parts=token.split('.',1)
        if len(parts)!=2:raise HTTPException(401,'请先登录')
        with db.tx() as s:
            session=s.get(Session,parts[0])
            if not session or session.expires<time.time() or not verify(session.token_hash,parts[1]):raise HTTPException(401,'会话已失效')
            if request.method not in {'GET','HEAD'} and not secrets.compare_digest(request.headers.get('x-csrf-token',''),session.csrf):raise HTTPException(403,'CSRF 校验失败')
            return session.admin_id
    def agent_auth(request:Request):
        raw=request.headers.get('authorization','').removeprefix('Bearer ');parts=raw.split('.',1)
        if len(parts)!=2:raise HTTPException(401,'节点认证失败')
        with db.tx() as s:
            agent=s.get(Agent,parts[0])
            if not agent or not agent.enabled or not verify(agent.token_hash,parts[1]):raise HTTPException(401,'节点已撤销或认证失败')
            return agent.id
    @app.get('/api/platforms')
    def platform_catalog(user=Depends(admin)):
        from .platform_specs import PLATFORM_SPECS
        return [{**value,'id':key} for key,value in PLATFORM_SPECS.items()]
    @app.get('/api/health')
    def health():return {'ok':True,'product':'omnidispatch','version':'1.1.0-desktop','platform_count':len(PLATFORMS),'database':db.engine.dialect.name}
    @app.post('/api/login')
    def login(data:Login,request:Request):
        ip=request.client.host if request.client else 'unknown';key=ip[:120]
        denied=False;token=None;csrf=None
        with db.tx() as s:
            guard=s.get(LoginGuard,key)
            if guard and guard.until>time.time():raise HTTPException(429,'登录尝试过多，请稍后再试')
            user=s.scalar(select(Admin).where(Admin.username==data.username))
            valid=verify(user.password if user else ph.hash('dummy-unavailable-password'),data.password)
            if user and user.totp and valid:
                second=pyotp.TOTP(vault.decrypt(user.totp)['secret']).verify(data.totp,valid_window=1)
                if not second:
                    for recovery in s.scalars(select(Recovery).where(Recovery.admin_id==user.id)):
                        if verify(recovery.code_hash,data.totp):second=True;s.delete(recovery);break
                valid=second
            if not user or not valid:
                if not guard:guard=LoginGuard(key=key,failures=0,until=0);s.add(guard)
                guard.failures+=1
                if guard.failures>=5:guard.until=time.time()+min(900,30*2**min(guard.failures-5,5))
                denied=True
            else:
                if guard:s.delete(guard)
                secret=new_token();csrf=new_token();session=Session(admin_id=user.id,token_hash=ph.hash(secret),csrf=csrf,expires=time.time()+43200)
                s.add(session);s.flush();token=session.id+'.'+secret;audit(s,'auth.login',user.id)
        if denied:raise HTTPException(401,'用户名、密码或验证码错误')
        response=JSONResponse({'csrf':csrf});response.set_cookie('omni_session',token,httponly=True,secure=secure,samesite='strict',max_age=43200);return response
    @app.post('/api/bootstrap')
    def bootstrap(request:Request):
        """本机直连自动发放会话；经隧道或带转发头的请求一律仍需口令。"""
        host=request.url.hostname or ''
        proxied=any(k.lower().startswith('cf-') for k in request.headers.keys()) or bool(request.headers.get('x-forwarded-for'))
        peer=request.client.host if request.client else ''
        if proxied or host not in {'127.0.0.1','localhost','::1'} or peer not in {'127.0.0.1','::1'}:
            raise HTTPException(401,'远程访问需要口令')
        with db.tx() as s:
            raw=request.cookies.get('omni_session','').split('.',1)
            previous=s.get(Session,raw[0]) if len(raw)==2 else None
            if previous and previous.expires>time.time() and verify(previous.token_hash,raw[1]):
                owner=s.get(Admin,previous.admin_id)
                if owner:return JSONResponse({'csrf':previous.csrf,'username':owner.username})
            account=s.scalar(select(Admin).limit(1))
            if not account:raise HTTPException(401,'尚未初始化管理员')
            secret=new_token();csrf=new_token()
            session=Session(admin_id=account.id,token_hash=ph.hash(secret),csrf=csrf,expires=time.time()+43200)
            s.add(session);s.flush()
            token=session.id+'.'+secret;name=account.username
            audit(s,'auth.bootstrap_local',account.id)
        response=JSONResponse({'csrf':csrf,'username':name})
        response.set_cookie('omni_session',token,httponly=True,secure=secure,samesite='strict',max_age=43200)
        return response
    from .local_engines import available_engines,configure_channel,account_config,import_credential
    def local_request(request):
        if not request.client or request.client.host not in {'127.0.0.1','::1'}:
            raise HTTPException(403,'此操作仅限本机桌面')
    @app.get('/api/local/channels')
    def local_channels(request:Request,user=Depends(admin)):
        local_request(request)
        return available_engines(state)
    @app.post('/api/local/channels/{channel_id}')
    def local_configure(channel_id:str,data:LocalChannelIn,request:Request,user=Depends(admin)):
        local_request(request)
        return configure_channel(state,db,channel_id,data.version,data.usage_acknowledged)
    @app.post('/api/channels/{channel_id}/login')
    def channel_login(channel_id:str,data:AccountSelection,request:Request,user=Depends(admin)):
        local_request(request)
        cfg,_=account_config(state,db,channel_id,data.account_id)
        return {'desktop_required':True,'engine':cfg['adapter'],'channel':channel_id,'account':data.account_id,
                'output':'在桌面窗口完成扫码，完成后导入该账号的登录态。'}
    @app.post('/api/channels/{channel_id}/import-login')
    def channel_import(channel_id:str,data:AccountSelection,request:Request,user=Depends(admin)):
        local_request(request)
        return import_credential(state,db,vault,channel_id,data.account_id)
    @app.get('/api/me')
    def me(request:Request,user=Depends(admin)):
        with db.tx() as s:
            session=s.get(Session,request.cookies['omni_session'].split('.')[0]);account=s.get(Admin,user)
            return {'username':account.username,'csrf':session.csrf,'totp_enabled':bool(account.totp)}
    @app.post('/api/logout')
    def logout(request:Request,user=Depends(admin)):
        with db.tx() as s:s.delete(s.get(Session,request.cookies['omni_session'].split('.')[0]))
        response=JSONResponse({'ok':True});response.delete_cookie('omni_session');return response
    @app.post('/api/password')
    def password(data:PasswordIn,user=Depends(admin)):
        with db.tx() as s:
            account=s.get(Admin,user)
            if not verify(account.password,data.current_password):raise HTTPException(403,'当前密码错误')
            account.password=ph.hash(data.password);s.execute(delete(Session).where(Session.admin_id==user));audit(s,'auth.password_changed',user)
        return {'ok':True}
    @app.post('/api/totp/setup')
    def totp_setup(data:TotpIn,user=Depends(admin)):
        from .db import Setting
        with db.tx() as s:
            account=s.get(Admin,user)
            if not verify(account.password,data.password):raise HTTPException(403,'密码错误')
            if account.totp:raise ValueError('已启用双因素认证')
            secret=pyotp.random_base32();record=s.get(Setting,'totp_pending')
            value={'ciphertext':vault.encrypt({'secret':secret}),'expires':time.time()+600}
            if record:record.value=value
            else:s.add(Setting(key='totp_pending',value=value))
            return {'secret':secret,'uri':pyotp.TOTP(secret).provisioning_uri(account.username,issuer_name='OmniDispatch')}
    @app.post('/api/totp/confirm')
    def totp_confirm(data:TotpIn,user=Depends(admin)):
        from .db import Setting
        with db.tx() as s:
            account=s.get(Admin,user);pending=s.get(Setting,'totp_pending')
            if not verify(account.password,data.password) or not pending or pending.value['expires']<time.time():raise HTTPException(403,'配置已失效')
            value=vault.decrypt(pending.value['ciphertext'])
            if not pyotp.TOTP(value['secret']).verify(data.code,valid_window=1):raise ValueError('验证码错误')
            account.totp=pending.value['ciphertext'];s.delete(pending);audit(s,'auth.totp_enabled',user)
            codes=[secrets.token_hex(10) for _ in range(8)]
            s.execute(delete(Recovery).where(Recovery.admin_id==user))
            for code in codes:s.add(Recovery(admin_id=user,code_hash=ph.hash(code)))
        return {'ok':True,'recovery_codes':codes}
    @app.get('/api/overview')
    def overview(user=Depends(admin)):
        with db.tx() as s:
            jobs=s.scalars(select(Job)).all();channels=[c for c in s.scalars(select(Channel)) if not c.capabilities.get('is_canary')];agents=s.scalars(select(Agent)).all()
            return {'jobs':dict(Counter(j.state for j in jobs)),'accounts':s.scalar(select(func.count()).select_from(Account)),
              'agents_online':sum(a.enabled and a.last_seen>time.time()-90 for a in agents),
              'platforms':[{'id':p,'label':label,'candidates':sum(c.platform==p for c in channels),'verified':sum(c.platform==p and c.enabled and c.health in {'healthy','degraded'} for c in channels),'fault_domains':len({c.capabilities.get('fault_domain') for c in channels if c.platform==p and c.enabled and c.health in {'healthy','degraded'}})} for p,label in PLATFORMS.items()]}
    @app.get('/api/accounts')
    def accounts(user=Depends(admin)):
        with db.tx() as s:
            return [{**public(a),'egress':{k:v for k,v in a.egress.items() if k!='secret'},'credentials':[public(c,('ciphertext',)) for c in s.scalars(select(Credential).where(Credential.account_id==a.id))]} for a in s.scalars(select(Account).order_by(Account.created.desc()))]
    @app.post('/api/accounts')
    def account_add(data:AccountIn,user=Depends(admin)):
        if data.platform not in PLATFORMS:raise ValueError('不支持的平台')
        if data.egress.get('mode','direct') not in {'direct','trusted-static','resin'}:raise ValueError('无效出口模式')
        if data.egress.get('mode')!='direct' and not data.egress.get('proxy'):raise ValueError('需配置明确代理地址')
        # Proxy passwords are credentials, kept encrypted; public binding is a reference.
        egress=data.egress
        if 'proxy' in egress:egress={**egress,'secret':vault.encrypt({'proxy':egress['proxy']})};egress.pop('proxy')
        with db.tx() as s:
            account=Account(label=data.label,platform=data.platform,min_interval=data.min_interval,egress=egress,canary_allowed=data.canary_allowed);s.add(account);s.flush();audit(s,'account.created',account.id);return public(account)
    @app.post('/api/accounts/{account_id}/credentials')
    def credential_add(account_id:str,data:CredIn,user=Depends(admin)):
        if len(json.dumps(data.value))>1_000_000:raise ValueError('凭证过大')
        with db.tx() as s:
            account=s.get(Account,account_id);channel=s.get(Channel,data.channel_id)
            if not account or not channel or channel.platform!=account.platform:raise ValueError('账号与通道平台不匹配')
            credential=s.scalar(select(Credential).where(Credential.account_id==account_id,Credential.channel_id==channel.id))
            if not credential:credential=Credential(account_id=account_id,channel_id=channel.id,ciphertext='');s.add(credential)
            credential.ciphertext=vault.encrypt(data.value);credential.state='active';account.state='active';audit(s,'credential.saved',account_id,channel=channel.id)
        return {'ok':True}
    @app.post('/api/accounts/{account_id}/state')
    def account_state(account_id:str,data:Action,user=Depends(admin)):
        if data.action not in {'active','cooling','pending'}:raise ValueError('无效状态')
        with db.tx() as s:
            account=s.get(Account,account_id)
            if not account:raise ValueError('账号不存在')
            account.state=data.action
            if data.action=='active':account.cooldown_until=0
            audit(s,'account.state',account.id,state=data.action)
        return {'ok':True}
    @app.get('/api/channels')
    def channels(user=Depends(admin)):
        with db.tx() as s:return [public(c) for c in s.scalars(select(Channel).order_by(Channel.platform,Channel.priority.desc()))]
    @app.post('/api/channels/{channel_id}')
    def channel_set(channel_id:str,data:ChannelIn,user=Depends(admin)):
        with db.tx() as s:
            channel=s.get(Channel,channel_id)
            if not channel:raise ValueError('通道不存在')
            if data.enabled and (channel.health=='unverified' or channel.version!=data.version):raise ValueError('须先由节点完成只读检查，再核验真实发布')
            if channel.version!=data.version:
                channel.health='unverified';channel.evidence={}
            if data.enabled:
                ready=any(a.enabled and a.last_seen>time.time()-90 and a.capabilities.get('channels',{}).get(channel_id,{}).get('ready') and a.capabilities.get('channels',{}).get(channel_id,{}).get('version')==data.version for a in s.scalars(select(Agent)))
                authorized=any(s.get(Account,c.account_id) and s.get(Account,c.account_id).state=='active' for c in s.scalars(select(Credential).where(Credential.channel_id==channel_id,Credential.state=='active')))
                if not ready or not authorized:raise ValueError('启用需要版本匹配的在线节点与有效账号授权')
            channel.version=data.version;channel.priority=data.priority;channel.enabled=data.enabled;audit(s,'channel.configured',channel.id,version=data.version,enabled=data.enabled)
        return {'ok':True}
    @app.post('/api/channels/{channel_id}/verify')
    def channel_verify(channel_id:str,data:Action,user=Depends(admin)):
        # Human attestation records the remote post identity; never label a fake as live.
        if data.action!='attest_live' or not data.remote_id:raise ValueError('需提供已核验的真实作品 ID')
        with db.tx() as s:
            channel=s.get(Channel,channel_id)
            if not channel or channel.version=='unconfigured':raise ValueError('先配置版本')
            ready=any(a.enabled and a.last_seen>time.time()-90 and a.capabilities.get('channels',{}).get(channel_id,{}).get('version')==channel.version and a.capabilities.get('channels',{}).get(channel_id,{}).get('ready') for a in s.scalars(select(Agent)))
            if not ready:raise ValueError('没有版本匹配且检查通过的在线节点')
            channel.health='healthy';channel.failures=0;channel.open_until=0;channel.evidence={'actions':['publish'],'method':'administrator_attestation','remote_id':data.remote_id,'at':time.time(),'version':channel.version}
            audit(s,'channel.live_attested',channel_id,remote_id=data.remote_id)
        return {'ok':True}
    chunk_size=8*1024*1024
    @app.post('/api/assets/uploads')
    def begin_upload(data:UploadIn,user=Depends(admin)):
        suffix=Path(data.name).suffix.lower()
        kind='images' if suffix in {'.jpg','.jpeg','.png','.webp'} else 'video' if suffix in {'.mp4','.mov','.webm','.mkv'} else None
        if not kind:raise ValueError('不支持的素材格式')
        with db.tx() as s:
            active=s.scalar(select(func.count()).select_from(AssetUpload).where(AssetUpload.owner==user,AssetUpload.state=='open'))
            if active>=10:raise ValueError('未完成上传过多，请先完成已有上传')
            upload=AssetUpload(owner=user,name=Path(data.name).name,size=data.size,kind=kind);s.add(upload);s.flush()
            folder=state/'uploads'/upload.id;folder.mkdir(parents=True)
            return {'id':upload.id,'chunk_size':chunk_size,'chunks':(data.size+chunk_size-1)//chunk_size}
    @app.put('/api/assets/uploads/{upload_id}/{index}')
    async def upload_chunk(upload_id:str,index:int,request:Request,user=Depends(admin)):
        with db.tx() as s:
            upload=s.get(AssetUpload,upload_id)
            if not upload or upload.owner!=user:raise HTTPException(404,'上传任务不存在')
            if upload.state!='open':raise Conflict('上传已完成或正在合并')
            count=(upload.size+chunk_size-1)//chunk_size
            if index<0 or index>=count:raise ValueError('无效分块编号')
            expected=min(chunk_size,upload.size-index*chunk_size)
        folder=state/'uploads'/upload_id;temporary=folder/(str(index)+'.'+uid()+'.part');target=folder/(str(index)+'.chunk');size=0
        try:
            with temporary.open('xb') as f:
                async for chunk in request.stream():
                    size+=len(chunk)
                    if size>expected:raise ValueError('分块大小超过约定')
                    f.write(chunk)
            if size!=expected:raise ValueError('分块大小不完整')
            if target.exists():
                import filecmp
                if not filecmp.cmp(target,temporary,shallow=False):raise Conflict('该编号已保存不同的分块内容')
            else:os.replace(temporary,target)
        finally:temporary.unlink(missing_ok=True)
        return {'ok':True,'index':index}
    @app.get('/api/assets/uploads/{upload_id}')
    def upload_status(upload_id:str,user=Depends(admin)):
        with db.tx() as s:
            upload=s.get(AssetUpload,upload_id)
            if not upload or upload.owner!=user:raise HTTPException(404,'上传任务不存在')
            folder=state/'uploads'/upload_id;count=(upload.size+chunk_size-1)//chunk_size
            present=[i for i in range(count) if (folder/(str(i)+'.chunk')).is_file() and (folder/(str(i)+'.chunk')).stat().st_size==min(chunk_size,upload.size-i*chunk_size)]
            return {'id':upload.id,'chunk_size':chunk_size,'chunks':count,'present':present,'state':upload.state}
    @app.delete('/api/assets/uploads/{upload_id}')
    def cancel_upload(upload_id:str,user=Depends(admin)):
        import shutil
        with db.tx() as s:
            upload=s.get(AssetUpload,upload_id,with_for_update=True)
            if not upload or upload.owner!=user:raise HTTPException(404,'上传任务不存在')
            if upload.state!='open':raise Conflict('合并中或已完成的素材不能取消')
            s.delete(upload)
        shutil.rmtree(state/'uploads'/upload_id,ignore_errors=True)
        return {'ok':True}
    @app.post('/api/assets/uploads/{upload_id}/complete')
    def finish_upload(upload_id:str,user=Depends(admin)):
        import shutil
        with db.tx() as s:
            upload=s.get(AssetUpload,upload_id,with_for_update=True)
            if not upload or upload.owner!=user:raise HTTPException(404,'上传任务不存在')
            if upload.state=='completed':return public(s.get(Asset,upload_id),('path',))
            if upload.state=='assembling' and upload.lease_until>time.time():raise Conflict('素材正在合并，请稍后查询')
            count=(upload.size+chunk_size-1)//chunk_size;folder=state/'uploads'/upload_id
            for index in range(count):
                part=folder/(str(index)+'.chunk')
                if not part.is_file() or part.stat().st_size!=min(chunk_size,upload.size-index*chunk_size):raise Conflict('素材分块尚未完整')
            upload.state='assembling';upload.lease_until=time.time()+600
            name,kind,size=upload.name,upload.kind,upload.size
        assets_dir=state/'assets';assets_dir.mkdir(exist_ok=True);target=assets_dir/(upload_id+Path(name).suffix.lower());temporary=assets_dir/(upload_id+'.'+uid()+'.assembling')
        try:
            # Large media copies deliberately run outside the queue database transaction.
            with temporary.open('xb') as output:
                for index in range(count):
                    with (folder/(str(index)+'.chunk')).open('rb') as source:shutil.copyfileobj(source,output,length=1024*1024)
            os.replace(temporary,target)
            with db.tx() as s:
                upload=s.get(AssetUpload,upload_id,with_for_update=True);asset=s.get(Asset,upload_id)
                if not asset:
                    asset=Asset(id=upload_id,name=name,kind=kind,size=size,path=str(target));s.add(asset);s.flush();audit(s,'asset.uploaded',asset.id,size=size,chunked=True)
                upload.state='completed';upload.lease_until=0;result=public(asset,('path',))
        except BaseException:
            with db.tx() as s:
                upload=s.get(AssetUpload,upload_id)
                if upload and upload.state=='assembling':upload.state='open';upload.lease_until=0
            raise
        finally:temporary.unlink(missing_ok=True)
        shutil.rmtree(folder,ignore_errors=True)
        return result
    @app.get('/api/assets')
    def assets(user=Depends(admin)):
        with db.tx() as s:return [public(a,('path',)) for a in s.scalars(select(Asset).order_by(Asset.created.desc()))]
    @app.post('/api/assets')
    async def upload(file:UploadFile=File(...),user=Depends(admin)):
        suffix=Path(file.filename or '').suffix.lower();kind='images' if suffix in {'.jpg','.jpeg','.png','.webp'} else 'video' if suffix in {'.mp4','.mov','.webm','.mkv'} else None
        if not kind:raise ValueError('仅接受常见图片和视频格式')
        folder=state/'assets';folder.mkdir(exist_ok=True);target=folder/(uid()+suffix);size=0
        try:
            with target.open('xb') as f:
                while chunk:=await file.read(1024*1024):
                    size+=len(chunk)
                    if size>2*1024**3:raise ValueError('单文件超过 2 GiB')
                    f.write(chunk)
            if not size:raise ValueError('空文件')
            with db.tx() as s:
                asset=Asset(name=Path(file.filename).name[:200],kind=kind,size=size,path=str(target));s.add(asset);s.flush();audit(s,'asset.uploaded',asset.id,size=size);return public(asset,('path',))
        except BaseException:target.unlink(missing_ok=True);raise
    @app.get('/api/jobs')
    def jobs(user=Depends(admin)):
        with db.tx() as s:return [public(j) for j in s.scalars(select(Job).order_by(Job.created.desc()).limit(500))]
    @app.post('/api/jobs')
    def job_add(data:JobIn,user=Depends(admin)):
        payload={'title':data.title,'description':data.description,'kind':data.kind,'assets':data.assets,'options':data.options,'canary':data.canary,'verification_channel':data.verification_channel,'action':data.action,'target_url':data.target_url,'target_comment_id':data.target_comment_id,'delivery':data.delivery}
        from .platform_specs import validate_intent
        with db.tx() as s:
            account=s.get(Account,data.account_id)
            if not account:raise ValueError('账号不存在')
            validate_intent(account.platform,payload)
            if data.verification_channel:
                channel=s.get(Channel,data.verification_channel);account=s.get(Account,data.account_id)
                if data.delivery=='draft' and channel and channel.engine!='desktopweb':raise ValueError('保存草稿请选择本机桌面通道')
                if not channel or not account or channel.platform!=account.platform or not channel.capabilities.get('implemented'):
                    raise ValueError('首次核验必须选择本账号平台的已实现通道')
            for asset_id in data.assets:
                asset=s.get(Asset,asset_id)
                if not asset or asset.kind!=data.kind:raise ValueError('素材不存在或类型不匹配')
        return public(queue.enqueue(data.idempotency_key,data.account_id,payload,data.due))
    @app.get('/api/jobs/{job_id}')
    def job_detail(job_id:str,user=Depends(admin)):
        with db.tx() as s:
            job=s.get(Job,job_id)
            if not job:raise HTTPException(404,'任务不存在')
            return {**public(job),'attempts':[public(a) for a in s.scalars(select(Attempt).where(Attempt.job_id==job_id).order_by(Attempt.generation))]}
    @app.post('/api/jobs/{job_id}/action')
    def job_action(job_id:str,data:Action,user=Depends(admin)):queue.resolve(job_id,data.action,data.remote_id);return {'ok':True}
    @app.get('/api/agents')
    def agents(user=Depends(admin)):
        with db.tx() as s:return [public(a,('token_hash',)) for a in s.scalars(select(Agent))]
    @app.post('/api/agents')
    def agent_add(data:AgentIn,user=Depends(admin)):
        token=new_token()
        with db.tx() as s:
            agent=Agent(label=data.label,token_hash=ph.hash(token));s.add(agent);s.flush();audit(s,'agent.created',agent.id);return {'id':agent.id,'token':agent.id+'.'+token}
    @app.post('/api/agents/{agent_id}/revoke')
    def agent_revoke(agent_id:str,user=Depends(admin)):
        with db.tx() as s:
            agent=s.get(Agent,agent_id)
            if not agent:raise ValueError('节点不存在')
            agent.enabled=False;audit(s,'agent.revoked',agent_id)
        return {'ok':True}
    @app.post('/agent/heartbeat')
    def agent_beat(data:Beat,identity=Depends(agent_auth)):
        if len(json.dumps(data.capabilities))>100000:raise ValueError('能力报文过大')
        with db.tx() as s:
            agent=s.get(Agent,identity);agent.last_seen=time.time();agent.capabilities=data.capabilities
        return {'ok':True}
    @app.post('/agent/claim')
    def claim(identity=Depends(agent_auth)):
        job=queue.claim(identity)
        if job:
            with db.tx() as s:job['assets_meta']={identifier:{'suffix':Path(s.get(Asset,identifier).name).suffix.lower()} for identifier in job['payload'].get('assets',[]) if s.get(Asset,identifier)}
        if job and 'secret' in job['egress']:job['egress']={**job['egress'],**vault.decrypt(job['egress']['secret'])};job['egress'].pop('secret',None)
        return {'job':job}
    @app.post('/agent/jobs/{job_id}/heartbeat')
    def job_beat(job_id:str,data:Generation,identity=Depends(agent_auth)):queue.heartbeat(job_id,identity,data.generation);return {'ok':True}
    @app.post('/agent/jobs/{job_id}/submitting')
    def job_submit(job_id:str,data:Generation,identity=Depends(agent_auth)):queue.submitting(job_id,identity,data.generation);return {'ok':True}
    @app.post('/agent/jobs/{job_id}/result')
    def job_result(job_id:str,data:Result,identity=Depends(agent_auth)):
        result={k:v for k,v in data.result.items() if k in {'ok','remote_id','error_class','definitely_not_submitted'}}
        return {'state':queue.complete(job_id,identity,data.generation,result)}
    @app.get('/agent/assets/{asset_id}')
    def agent_asset(asset_id:str,job_id:str,generation:int,identity=Depends(agent_auth)):
        with db.tx() as s:
            job=queue.owned(s,job_id,identity,generation)
            if asset_id not in job.payload.get('assets',[]):raise HTTPException(403,'素材不属于该任务')
            asset=s.get(Asset,asset_id)
            if not asset:raise HTTPException(404,'素材不存在')
            return FileResponse(asset.path,filename=asset.name)
    @app.get('/api/audit')
    def audits(after:float=0,user=Depends(admin)):
        with db.tx() as s:return [public(a) for a in s.scalars(select(Audit).where(Audit.created>after).order_by(Audit.created.desc()).limit(300))]
    @app.get('/api/events')
    async def events(request:Request,user=Depends(admin)):
        cursor=float(request.headers.get('last-event-id','0') or 0)
        async def stream():
            nonlocal cursor
            for _ in range(120):
                if await request.is_disconnected():return
                with db.tx() as s:items=s.scalars(select(Audit).where(Audit.created>cursor).order_by(Audit.created).limit(100)).all()
                for item in items:
                    cursor=item.created;yield f'id: {cursor}\ndata: {json.dumps(public(item),ensure_ascii=False)}\n\n'
                if not items:yield ': heartbeat\n\n'
                await asyncio.sleep(2)
        return StreamingResponse(stream(),media_type='text/event-stream',headers={'X-Accel-Buffering':'no'})
    @app.get('/api/updates/policy')
    def update_policy(user=Depends(admin)):
        return {'trusted_key_configured':bool(os.getenv('OMNI_UPDATE_PUBLIC_KEY')),'publisher_feed_configured':bool(os.getenv('OMNI_UPDATE_FEED_URL')),'auto_promote':os.getenv('OMNI_AUTO_PROMOTE','0')=='1','minimum_canary_hours':24,'minimum_successes_per_active_channel':3}
    @app.get('/api/updates')
    def update_list(user=Depends(admin)):
        with db.tx() as s:return [public(u) for u in s.scalars(select(Update).order_by(Update.created.desc()))]
    @app.post('/api/updates/check')
    async def update_check(user=Depends(admin)):return {'results':await updates.discover()}
    @app.post('/api/updates/{update_id}/action')
    def update_action(update_id:str,data:Action,user=Depends(admin)):updates.transition(update_id,data.action);return {'ok':True}
    @app.post('/api/updates/{update_id}/stage')
    async def update_stage(update_id:str,request:Request,file:UploadFile=File(...),user=Depends(admin)):
        temp=state/(uid()+'.zip')
        try:
            size=0
            with temp.open('xb') as f:
                while chunk:=await file.read(1024*1024):
                    size+=len(chunk)
                    if size>512*1024**2:raise ValueError('更新包过大')
                    f.write(chunk)
            updates.stage(update_id,temp,request.headers.get('x-update-signature',''),os.getenv('OMNI_UPDATE_PUBLIC_KEY',''))
        finally:temp.unlink(missing_ok=True)
        return {'ok':True}
    from .desktop_api import mount_desktop_routes
    mount_desktop_routes(app,db,vault,queue,state,admin)
    static=Path(__file__).parent/'static'
    if static.exists():app.mount('/',StaticFiles(directory=static,html=True),name='web')
    return app
