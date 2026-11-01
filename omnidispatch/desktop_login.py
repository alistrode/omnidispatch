"""Run interactive logins in the signed-in desktop session, never in a Windows service."""
import argparse,json,os,socket,subprocess,time
from pathlib import Path
from .db import Database
from .local_engines import account_config,atomic_json,file_lock,read_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--state',required=True);p.add_argument('--channel',required=True);p.add_argument('--account',required=True)
    a=p.parse_args();state=Path(a.state).resolve();db=Database(f'sqlite:///{state/"hub.db"}')
    cfg,folder=account_config(state,db,a.channel,a.account);folder.mkdir(parents=True,exist_ok=True)
    with file_lock(folder/'login.lock'):
        status=folder/'login-status.json';atomic_json(status,{'state':'waiting','at':time.time()})
        from .windows_job import WindowsJob
        owned=WindowsJob()
        try:
            child_env=dict(os.environ)
            if cfg['adapter']=='xhsmcp':
                from .browser_provision import bundled_xhs_browser
                child_env['OMNI_XHS_BROWSER']=bundled_xhs_browser()
            binary=Path(cfg['argv'][0]);flags=subprocess.CREATE_NEW_CONSOLE if os.name=='nt' and cfg['adapter']=='biliup' else 0
            command=[str(binary),'login'] if cfg['adapter']=='biliup' else [str(binary.parent/'xiaohongshu-login.exe')]
            if cfg['adapter']=='spreado':command=[*cfg['argv'],'login','shipinhao' if a.channel.endswith('-tencent') else a.channel.split('-',1)[1],'--cookies',str(folder/'cookies.json')]
            if not Path(command[0]).is_file():raise ValueError('缺少扫码登录助手')
            # Private cwd isolates upstream's cookies.json for every account.
            with (folder/'login.private.log').open('ab') as log:
                process=subprocess.Popen(command,cwd=folder,env=child_env,creationflags=flags,stdout=None if flags else log,stderr=None if flags else subprocess.STDOUT)
                owned.add(process)
                code=process.wait(timeout=600)
            if code or not (folder/'cookies.json').exists():raise ValueError('登录未完成，请重新扫码')
            if cfg['adapter']=='xhsmcp':start_instance(state,a.channel,a.account,cfg,folder)
            atomic_json(status,{'state':'ready','at':time.time()})
        except Exception as e:
            if 'process' in locals() and process.poll() is None:process.terminate()
            atomic_json(status,{'state':'failed','message':str(e) if isinstance(e,ValueError) else '扫码未完成，请重试','at':time.time()})
        finally:owned.close();db.engine.dispose()

def start_instance(state,channel,account,cfg,folder):
    import httpx
    with file_lock(state/'instances.lock'):
        instances=read_json(state/'engine-instances.json');item=instances.setdefault(channel,{}).get(account)
        if item:
            try:
                if httpx.get(item['endpoint']+'/api/v1/login/status',timeout=3,trust_env=False).status_code==200:return
            except httpx.HTTPError:pass
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        # The persistent supervisor owns the process Job Object, including Chromium.
        # Register the desired loopback instance; never leave an unowned browser service.
        item={'endpoint':'http://127.0.0.1:'+str(port),'instance_account':account,'cwd':str(folder),'pid':None}
        instances[channel][account]=item;atomic_json(state/'engine-instances.json',instances)
    for _ in range(60):
        try:
            if httpx.get(item['endpoint']+'/api/v1/login/status',timeout=2,trust_env=False).status_code==200:return
        except httpx.HTTPError:pass
        time.sleep(1)
    raise ValueError('小红书服务启动超时，请检查本机后台节点')
if __name__=='__main__':main()
