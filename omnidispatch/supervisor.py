"""Supervise only processes started by this workspace. No global process termination."""
import os,sys,subprocess,time,signal,socket,json,logging
from pathlib import Path

def main():
    root=Path(__file__).resolve().parent.parent;state=Path(os.getenv('OMNI_STATE',root/'state')).resolve();state.mkdir(exist_ok=True)
    lock=socket.socket();lock.bind(('127.0.0.1',8792));lock.listen(1)
    logging.basicConfig(filename=state/'supervisor.log',level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    env={**os.environ,'OMNI_STATE':str(state),'PYTHONUTF8':'1'}
    config=state/'runtime-settings.json'
    settings=json.loads(config.read_text(encoding="utf-8-sig")) if config.exists() else {}
    for key,value in settings.get('environment',{}).items():
        if key in {'OMNI_SECURE_COOKIE','OMNI_PUBLIC_ORIGIN','OMNI_DATABASE_URL','OMNI_UPDATE_PUBLIC_KEY'}:env[key]=str(value)
    commands={'hub':[sys.executable,'-m','omnidispatch.cli','--state',str(state),'serve','--port','8791'],
              'agent':[sys.executable,'-m','omnidispatch.cli','--state',str(state),'agent','--config',str(state/'agent.json')]}
    tunnel=settings.get('cloudflared')
    if tunnel and Path(tunnel).is_file():commands['tunnel']=[tunnel,'tunnel','--no-autoupdate','--protocol','http2','--url','http://127.0.0.1:8791']
    children={};streams={};stopping=False
    def stop(*_):
        nonlocal stopping
        stopping=True
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    try:
        while not stopping:
            for name,command in commands.items():
                if name not in children or children[name].poll() is not None:
                    if name in children:logging.warning('%s exited %s; restarting',name,children[name].returncode);streams[name].close()
                    streams[name]=(state/(name+'.log')).open('ab')
                    children[name]=subprocess.Popen(command,cwd=root,env=env,stdin=subprocess.DEVNULL,stdout=streams[name],stderr=subprocess.STDOUT)
                    logging.info('started %s pid=%s',name,children[name].pid)
            (state/'owned-processes.json').write_text(json.dumps({name:p.pid for name,p in children.items()}))
            time.sleep(3)
    finally:
        for p in children.values():
            if p.poll() is None:p.terminate()
        for p in children.values():
            try:p.wait(timeout=20)
            except subprocess.TimeoutExpired:p.kill()
        for f in streams.values():f.close()
        lock.close()
if __name__=='__main__':main()
