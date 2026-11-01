"""First-run setup for the local desktop bundle, reusing the existing supervisor."""
import os,subprocess,sys
from pathlib import Path

def main():
    root=Path(__file__).resolve().parent.parent;state=root/'state';state.mkdir(exist_ok=True)
    env={**os.environ,'PYTHONUTF8':'1','OMNI_STATE':str(state)}
    log=(state/'desktop-start.log').open('ab')
    for command in ('init','register-agent'):
        subprocess.run([sys.executable,'-m','omnidispatch.cli','--state',str(state),command],cwd=root,env=env,stdout=log,stderr=log,check=True)
    from .supervisor import main as supervise
    os.environ.update(env)
    try:supervise()
    except OSError as e:
        if getattr(e,'winerror',None)!=10048 and getattr(e,'errno',None)!=98:raise
if __name__=='__main__':main()
