"""Local engine configuration and account-isolated browser sessions."""
import contextlib,json,os,re,socket,tempfile,time
from pathlib import Path
from sqlalchemy import select
from .db import Account,Channel,Credential,audit
UUID=re.compile(r'^[a-f0-9-]{36}$')
CHANNEL=re.compile(r'^[a-z0-9-]{1,80}$')
@contextlib.contextmanager
def file_lock(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as f:
        if f.tell()==0:f.write(b'0');f.flush()
        f.seek(0)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(f.fileno(),msvcrt.LK_LOCK,1)
        else:
            import fcntl
            fcntl.flock(f,fcntl.LOCK_EX)
        try:yield
        finally:
            f.seek(0)
            if os.name=='nt':msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(f,fcntl.LOCK_UN)

def read_json(path,default=None):
    try:return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except FileNotFoundError:return {} if default is None else default

def atomic_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
    finally:Path(name).unlink(missing_ok=True)

def engine_root(state):return Path(state).resolve().parent/'engines'
def available_engines(state):
    root=engine_root(state);results=[]
    adapters={'biliup':('biliup-',),'xhsmcp':('xiaohongshu-mcp',),'spreado':('spreado',),'ytuploader':('youtubeuploader','ytuploader')}
    for engine,prefixes in adapters.items():
        base=root/engine
        if not base.exists():continue
        for version in sorted(base.iterdir()):
            if not version.is_dir():continue
            if engine=='xhsmcp' and version.name!='v2.5.5-omni':continue
            binaries=[f for f in version.rglob('*.exe') if any(f.name.lower().startswith(n) for n in prefixes) and 'login' not in f.name.lower()]
            if engine=='biliup':binaries=[f for f in version.rglob('*.exe') if f.name.lower().startswith('biliup')]
            if binaries:results.append({'engine':engine,'version':version.name,'path':str(sorted(binaries)[0]),'installed':True})
    source=root/'spreado'/'v1.2.0'/'source'/'spreado'
    runtime=root.parent/'runtime'/'python.exe'
    if source.is_dir() and runtime.is_file():
        results=[e for e in results if e['engine']!='spreado']
        results.append({'engine':'spreado','version':'v1.2.0','path':str(runtime),'argv':[str(runtime),'-m','omnidispatch.spreado_bridge'],'installed':True})
    sau=root/'sau'/'runtime'/'python.exe'
    wrapper=root/'sau'/'source'/'omni_sau_cli.py'
    if sau.is_file() and wrapper.is_file():results.append({'engine':'sau','version':'3847fff','path':str(sau),'argv':[str(sau),str(wrapper)],'installed':True})
    preferred=root/'browser'/'chromium-cft'/'chrome-win64'/'chrome.exe'
    browsers=[preferred] if preferred.is_file() else list((root/'browser').rglob('chrome.exe'))
    if browsers:results.append({'engine':'desktopweb','version':'v1','path':str(browsers[0]),'installed':True})
    results.append({'engine':'xapi','version':'api-v2','installed':True})
    return results

def configure_channel(state,db,channel_id,version,usage_acknowledged=False):
    state=Path(state)
    with db.tx() as s:
        channel=s.get(Channel,channel_id)
        if not channel or not channel.capabilities.get('implemented'):raise ValueError('此通道尚未实现')
        engine=channel.engine
    options=[e for e in available_engines(state) if e['engine']==engine and e['version']==version]
    if not options:raise ValueError('本机没有安装所选引擎版本')
    if engine=='biliup' and not usage_acknowledged:raise ValueError('请先阅读并确认 biliup 的用途限制')
    info=options[0]
    with file_lock(state/'configuration.lock'):
        cfg=read_json(state/'agent.json')
        if not cfg.get('token'):raise ValueError('本机节点尚未注册')
        previous=cfg.setdefault('channels',{}).get(channel_id,{})
        item={**previous,'adapter':engine,'version':version}
        if info.get('path'):item.update(argv=info.get('argv',[info['path']]),cwd=str(engine_root(state)/engine/version))
        if engine=='biliup':item['usage_acknowledged']=True
        ff=list((engine_root(state)/'ffprobe').rglob('ffprobe.exe'))
        if ff:item['ffprobe']=str(ff[0])
        if engine=='xhsmcp':item['endpoint']='http://127.0.0.1:18060'
        cfg['channels'][channel_id]=item
        atomic_json(state/'agent.json',cfg)
    with db.tx() as s:
        channel=s.get(Channel,channel_id)
        if channel.version!=version:channel.version=version;channel.enabled=False;channel.health='unverified';channel.evidence={}
        audit(s,'channel.local_configured',channel_id,version=version)
    return {'ok':True,'note':'节点将自动读取配置，无需手改文件或重启'}

def account_config(state,db,channel_id,account_id):
    state=Path(state)
    if not UUID.fullmatch(account_id) or not CHANNEL.fullmatch(channel_id):raise ValueError('账号或通道标识无效')
    with db.tx() as s:
        account=s.get(Account,account_id);channel=s.get(Channel,channel_id)
        if not account or not channel or channel.platform!=account.platform:raise ValueError('账号与通道平台不匹配')
        if account.state=='cooling':raise ValueError('账号已暂停，请先恢复')
    cfg=read_json(state/'agent.json').get('channels',{}).get(channel_id)
    if not cfg or cfg.get('adapter') not in {'biliup','xhsmcp','spreado','desktopweb','sau'}:raise ValueError('此通道尚未配置扫码引擎')
    argv=cfg.get('argv') or []
    if not argv or not Path(argv[0]).is_file():raise ValueError('扫码引擎不存在')
    bridge=cfg.get('adapter')=='spreado' and argv==[str(engine_root(state).parent/'runtime'/'python.exe'),'-m','omnidispatch.spreado_bridge']
    if not bridge and not Path(argv[0]).resolve().is_relative_to(engine_root(state).resolve()):raise ValueError('扫码程序必须位于本应用的 engines 目录')
    folder=state/'engine-accounts'/channel_id/account_id
    return cfg,folder

def configured_instances(state,channel_id):return list(read_json(Path(state)/'engine-instances.json').get(channel_id,{}).values())
def instance_config(state,cfg,channel_id,account_id):
    if cfg.get('adapter')!='xhsmcp':return cfg
    item=read_json(Path(state)/'engine-instances.json').get(channel_id,{}).get(account_id)
    if not item:raise ValueError('此账号尚未建立独立的小红书实例，请在桌面扫码登录')
    return {**cfg,**item}

def import_credential(state,db,vault,channel_id,account_id):
    cfg,folder=account_config(state,db,channel_id,account_id)
    cookies=folder/'cookies.json'
    if not cookies.is_file():raise ValueError('此账号还没有登录态，请先在桌面扫码')
    data=read_json(cookies)
    if not data:raise ValueError('登录态为空')
    if cfg['adapter']=='xhsmcp':
        import httpx
        instance=instance_config(state,cfg,channel_id,account_id)
        try:
            r=httpx.get(instance['endpoint']+'/api/v1/login/status',timeout=10,trust_env=False)
            result=r.json()
            if r.status_code!=200 or not result.get('success') or not result.get('data',{}).get('is_logged_in'):raise ValueError('小红书尚未登录成功')
        except httpx.HTTPError:raise ValueError('专属小红书实例未启动，请重新打开桌面登录')
        if not result.get('data',{}).get('user_id'):raise ValueError('引擎没有返回实际账号 ID，不能完成身份绑定')
        value={'instance_account':account_id,'platform_user_id':str(result['data']['user_id'])}
    elif cfg['adapter']=='spreado':
        if not isinstance(data,dict) or not isinstance(data.get('cookies'),list) or not data['cookies']:raise ValueError('浏览器登录态无效')
        value={'cookies':data}
    else:
        # Keep the exact upstream cookie envelope. Validate the required identity fields.
        entries=data.get('cookie_info',{}).get('cookies',[]) if isinstance(data,dict) else []
        by_name={x.get('name'):x.get('value') for x in entries}
        if not all(by_name.get(k) for k in ('SESSDATA','bili_jct','DedeUserID')):raise ValueError('B站登录态缺少必要 Cookie')
        value={'cookies':data,'platform_user_id':str(by_name['DedeUserID'])}
    with db.tx() as s:
        account=s.get(Account,account_id)
        old=s.scalar(select(Credential).where(Credential.account_id==account_id,Credential.channel_id==channel_id))
        if old and cfg['adapter'] in {'biliup','xhsmcp'}:
            prior=vault.decrypt(old.ciphertext).get('platform_user_id')
            if prior and prior!=value['platform_user_id']:raise ValueError('实际登录账号发生变化，请为新身份新建账号')
        if not old:old=Credential(account_id=account_id,channel_id=channel_id,ciphertext='');s.add(old)
        old.ciphertext=vault.encrypt(value);old.state='active';account.state='active'
        audit(s,'credential.imported_from_engine',account_id,channel=channel_id)
    return {'ok':True,'account':account_id}
