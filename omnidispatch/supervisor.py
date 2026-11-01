"""Supervise only processes started by this workspace. No global process termination."""
import os,sys,subprocess,time,signal,socket,json,logging,getpass,re
from pathlib import Path
from .windows_job import WindowsJob

def main():
    root=Path(__file__).resolve().parent.parent;state=Path(os.getenv('OMNI_STATE',root/'state')).resolve();state.mkdir(exist_ok=True)
    lock=socket.socket();lock.bind(('127.0.0.1',8792));lock.listen(1)
    logging.basicConfig(filename=state/'supervisor.log',level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    env={**os.environ,'OMNI_STATE':str(state),'PYTHONUTF8':'1'}
    config=state/'runtime-settings.json'
    settings=json.loads(config.read_text(encoding="utf-8-sig")) if config.exists() else {}
    for key,value in settings.get('environment',{}).items():
        if key in {'OMNI_SECURE_COOKIE','OMNI_PUBLIC_ORIGIN','OMNI_DATABASE_URL','OMNI_UPDATE_PUBLIC_KEY','OMNI_UPDATE_FEED_URL','OMNI_AUTO_PROMOTE'}:env[key]=str(value)
    administrator=False
    if os.name=='nt':
        import ctypes
        administrator=bool(ctypes.windll.shell32.IsUserAnAdmin())
    (state/'runtime-identity.json').write_text(json.dumps({'account':getpass.getuser(),'administrator':administrator,'pid':os.getpid(),'platform':sys.platform}))
    commands={'hub':[sys.executable,'-m','omnidispatch.cli','--state',str(state),'serve','--port','8791'],
              'agent':[sys.executable,'-m','omnidispatch.cli','--state',str(state),'agent','--config',str(state/'agent.json')]}
    tunnel=settings.get('cloudflared')
    if tunnel and Path(tunnel).is_file():commands['tunnel']=[tunnel,'tunnel','--no-autoupdate','--protocol','http2','--url','http://127.0.0.1:8791']
    overrides={};working_directories={}
    resin=settings.get('resin')
    if resin and Path(resin).is_file():
        secrets=json.loads((state/'resin-secrets.private.json').read_text())
        commands['resin']=[resin]
        data=state/'resin'
        for name in ['state','cache','logs']:(data/name).mkdir(parents=True,exist_ok=True)
        overrides['resin']={'RESIN_ADMIN_TOKEN':secrets['admin_token'],'RESIN_PROXY_TOKEN':secrets['proxy_token'],'RESIN_LISTEN_ADDRESS':'127.0.0.1','RESIN_PORT':'2260','RESIN_STATE_DIR':str(data/'state'),'RESIN_CACHE_DIR':str(data/'cache'),'RESIN_LOG_DIR':str(data/'logs')}
    job_object=WindowsJob()
    children={};streams={};stopping=False;tunnel_offset=0;published_url=None
    def stop(*_):
        nonlocal stopping
        stopping=True
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    try:
        while not stopping:
            # Account browser services survive a normal desktop restart and are
            # recreated after a machine reboot without requiring another login.
            from .local_engines import read_json,UUID,CHANNEL
            from urllib.parse import urlsplit
            config=read_json(state/'agent.json');instances=read_json(state/'engine-instances.json')
            for channel,accounts in instances.items():
                base=config.get('channels',{}).get(channel,{})
                if not CHANNEL.fullmatch(channel) or base.get('adapter')!='xhsmcp':continue
                binary=Path((base.get('argv') or [''])[0]).resolve()
                if not binary.is_file() or not binary.is_relative_to((root/'engines').resolve()):continue
                for account,item in accounts.items():
                    if not UUID.fullmatch(account):continue
                    url=urlsplit(item.get('endpoint',''))
                    if url.scheme!='http' or url.hostname!='127.0.0.1' or not url.port:continue
                    name='xhs-'+channel+'-'+account
                    if name not in commands:
                        try:
                            with socket.create_connection(('127.0.0.1',url.port),timeout=.2):continue
                        except OSError:pass
                        folder=state/'engine-accounts'/channel/account
                        if not (folder/'cookies.json').is_file():continue
                        from .browser_provision import bundled_xhs_browser
                        overrides[name]={'OMNI_XHS_BROWSER':bundled_xhs_browser()}
                        commands[name]=[str(binary),'-port','127.0.0.1:'+str(url.port),'-headless=true']
                        working_directories[name]=folder
            for name,command in commands.items():
                if name not in children or children[name].poll() is not None:
                    if name in children:logging.warning('%s exited %s; restarting',name,children[name].returncode);streams[name].close()
                    streams[name]=(state/(name+'.log')).open('ab')
                    if name=='tunnel':
                        tunnel_offset=streams[name].tell();published_url=None
                        (state/'PUBLIC-URL.txt').unlink(missing_ok=True)
                    children[name]=subprocess.Popen(command,cwd=working_directories.get(name,root),env={**env,**overrides.get(name,{})},stdin=subprocess.DEVNULL,stdout=streams[name],stderr=subprocess.STDOUT)
                    job_object.add(children[name])
                    logging.info('started %s pid=%s',name,children[name].pid)
            if 'tunnel' in children and published_url is None:
                with (state/'tunnel.log').open('rb') as source:
                    source.seek(tunnel_offset);urls=re.findall(rb'https://[a-z0-9-]+\.trycloudflare\.com',source.read(1024*1024))
                if urls:
                    published_url=urls[-1].decode();(state/'PUBLIC-URL.txt').write_text(published_url+'\n')
            (state/'owned-processes.json').write_text(json.dumps({name:p.pid for name,p in children.items()}))
            time.sleep(3)
    finally:
        for p in children.values():
            if p.poll() is None:p.terminate()
        for p in children.values():
            try:p.wait(timeout=20)
            except subprocess.TimeoutExpired:p.kill()
        for f in streams.values():f.close()
        job_object.close();lock.close()
if __name__=='__main__':main()
