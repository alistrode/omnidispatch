import json,time,threading,tempfile,logging,os
from pathlib import Path
from urllib.parse import urlsplit
import httpx
from .adapters import Adapter,PreflightError,check
log=logging.getLogger('omni.agent')
class AgentRunner:
    def __init__(self,config):
        self.path=Path(config).resolve();self.config=json.loads(self.path.read_text(encoding='utf-8-sig'));self.stop=threading.Event()
        hub=self.config['hub'].rstrip('/');u=urlsplit(hub)
        if u.scheme!='https' and not (u.scheme=='http' and u.hostname in {'localhost','127.0.0.1','::1'}):raise ValueError('Hub 必须使用 HTTPS；仅本机允许 HTTP')
        self.client=httpx.Client(base_url=hub,headers={'Authorization':'Bearer '+self.config['token']},timeout=40,follow_redirects=False)
        self.work=Path(self.config.get('work',self.path.parent/'jobs')).resolve();self.work.mkdir(parents=True,exist_ok=True)
    def post(self,path,data=None):
        response=self.client.post(path,json=data or {});response.raise_for_status();return response.json()
    def capabilities(self):
        result={}
        for key,cfg in self.config.get('channels',{}).items():
            result[key]={**check(cfg),'version':cfg.get('version'),'egress_modes':['direct','trusted-static','resin'] if cfg['adapter'] in {'xapi','biliup'} else ['direct']}
        return {'channels':result,'platform':os.name,'adapter_protocol':1}
    def run(self,once=False):
        failures=0
        try:
            while not self.stop.is_set():
                try:
                    self.post('/agent/heartbeat',{'capabilities':self.capabilities()})
                    job=self.post('/agent/claim')['job']
                    if job:self.execute(job)
                    failures=0
                except Exception as e:
                    failures+=1;log.warning('Agent communication failed: %s',type(e).__name__)
                if once:return
                self.stop.wait(min(60,2**min(failures,6)) if failures else 5)
        finally:self.client.close()
    def execute(self,job):
        generation={'generation':job['generation']};prefix='/agent/jobs/'+job['id'];lost=threading.Event();done=threading.Event()
        def keepalive():
            while not done.wait(20):
                try:self.post(prefix+'/heartbeat',generation)
                except Exception:lost.set();return
        thread=threading.Thread(target=keepalive,daemon=True);thread.start();submitted=False
        try:
            cfg=self.config['channels'].get(job['channel'])
            if not cfg:raise PreflightError('engine_missing','通道配置不存在')
            with tempfile.TemporaryDirectory(prefix=job['id']+'-',dir=self.work) as folder:
                work=Path(folder);files=[]
                for index,asset in enumerate(job['payload'].get('assets',[])):
                    # Download only job-scoped objects from the authenticated Hub, never arbitrary content URLs.
                    target=work/(str(index)+'.'+('mp4' if job['payload']['kind']=='video' else 'jpg'));size=0
                    with self.client.stream('GET',f'/agent/assets/{asset}',params={'job_id':job['id'],'generation':job['generation']}) as response:
                        response.raise_for_status()
                        with target.open('xb') as f:
                            for chunk in response.iter_bytes(1024*1024):
                                size+=len(chunk)
                                if size>2*1024**3:raise PreflightError('invalid_input','素材过大')
                                f.write(chunk)
                    files.append(target)
                adapter=Adapter(cfg,job,files,work);adapter.preflight()
                if lost.is_set():return
                # Critical boundary: if this request's response is lost, DO NOT invoke adapter.publish.
                self.post(prefix+'/submitting',generation);submitted=True
                result=adapter.publish()
                if not lost.is_set():self.post(prefix+'/result',{**generation,'result':result})
        except PreflightError as e:
            if not lost.is_set():
                try:self.post(prefix+'/result',{**generation,'result':{'ok':False,'error_class':e.kind,'definitely_not_submitted':not submitted}})
                except Exception:pass
        except Exception as e:
            log.warning('Job %s interrupted: %s',job['id'],type(e).__name__)
            if not lost.is_set():
                try:self.post(prefix+'/result',{**generation,'result':{'ok':False,'error_class':'engine_crash','definitely_not_submitted':not submitted}})
                except Exception:pass
        finally:done.set();thread.join(timeout=2)
