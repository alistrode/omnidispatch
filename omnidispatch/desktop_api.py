"""Scoped local desktop sessions; browser helpers never need direct vault-file access."""
import time,json,secrets
from pathlib import Path
from pydantic import BaseModel,ConfigDict,Field
from fastapi import Depends,Request,HTTPException
from sqlalchemy import select
from .db import Account,Channel,Credential,Agent,Setting,Job,Asset,audit
from .security import ph
from .platform_specs import PLATFORM_SPECS,allowed_url,cookie_domain_allowed
class Strict(BaseModel):model_config=ConfigDict(extra='forbid')
class BrowserSession(Strict):identity:str=Field(min_length=1,max_length=300);browser_state:dict;upstream_identity:dict=Field(default_factory=dict)
class DesktopResult(Strict):generation:int;outcome:str;remote_url:str=''
class Generation(Strict):generation:int

def mount_desktop_routes(app,db,vault,queue,state,admin):
    def local(request:Request,user=Depends(admin)):
        if not request.client or request.client.host not in {'127.0.0.1','::1'}:raise HTTPException(403,'仅限本机桌面')
        return user
    def pair(s,account_id,channel_id):
        a=s.get(Account,account_id);c=s.get(Channel,channel_id)
        if not a or not c or a.platform!=c.platform or c.engine not in {'desktopweb','sau'}:raise ValueError('桌面账号与通道不匹配')
        return a,c
    @app.get('/api/desktop/accounts/{account_id}/{channel_id}')
    def session_read(account_id:str,channel_id:str,user=Depends(local)):
        with db.tx() as s:
            a,c=pair(s,account_id,channel_id);credential=s.scalar(select(Credential).where(Credential.account_id==a.id,Credential.channel_id==c.id,Credential.state=='active'))
            value=vault.decrypt(credential.ciphertext) if credential else {}
            return {'platform':a.platform,'label':a.label,'identity':value.get('identity',''),'browser_state':value.get('browser_state',{})}
    @app.post('/api/desktop/accounts/{account_id}/{channel_id}')
    def session_save(account_id:str,channel_id:str,data:BrowserSession,user=Depends(local)):
        if len(json.dumps(data.browser_state))>1000000:raise ValueError('登录态过大')
        with db.tx() as s:
            a,c=pair(s,account_id,channel_id)
            cookies=data.browser_state.get('cookies',[])
            if not cookies:raise ValueError('浏览器没有保存登录态，请先完成登录')
            domains=PLATFORM_SPECS[a.platform]['hosts']
            if any(not cookie_domain_allowed(a.platform,x.get('domain','')) for x in cookies):raise ValueError('登录态包含其他平台的 Cookie')
            credential=s.scalar(select(Credential).where(Credential.account_id==a.id,Credential.channel_id==c.id))
            if credential:
                previous=vault.decrypt(credential.ciphertext).get('identity')
                if previous and previous!=data.identity:raise ValueError('固定账号身份改变，请为新身份新建账号')
            else:credential=Credential(account_id=a.id,channel_id=c.id,ciphertext='');s.add(credential)
            credential.ciphertext=vault.encrypt({'browser_state':data.browser_state,'identity':data.identity,'account_alias':a.id,'upstream_identity':data.upstream_identity,'attestation':'desktop_user'});credential.state='active';a.state='active'
            audit(s,'credential.desktop_saved',a.id,channel=c.id,method='desktop_user_attestation')
        return {'ok':True}
    def desktop_agent(s):
        setting=s.get(Setting,'desktop_agent');agent=s.get(Agent,setting.value['id']) if setting else None
        if not agent:
            agent=Agent(label='本机桌面操作',token_hash=ph.hash(secrets.token_urlsafe(32)));s.add(agent);s.flush()
            if setting:setting.value={'id':agent.id}
            else:s.add(Setting(key='desktop_agent',value={'id':agent.id}))
        agent.enabled=True;agent.last_seen=time.time()
        agent.capabilities={'channels':{c.id:{'version':c.version,'ready':True} for c in s.scalars(select(Channel).where(Channel.engine=='desktopweb'))}}
        return agent.id
    @app.post('/api/desktop/jobs/{job_id}/prepare')
    def prepare(job_id:str,user=Depends(local)):
        with db.tx() as s:
            job=s.get(Job,job_id)
            if not job or job.state not in {'queued','retry_wait','needs_action','drafted'}:raise ValueError('任务正在执行或结果待核验，请先查看原任务')
            cid=job.payload.get('verification_channel') or 'desktopweb-'+job.platform
            channel=s.get(Channel,cid)
            resume=job.remote_id if job.remote_id and (job.state=='drafted' or job.payload.get('delivery')=='draft') and allowed_url(job.platform,job.remote_id) else None
            if not channel or channel.engine!='desktopweb':raise ValueError('该任务不是桌面通道任务')
            identity=desktop_agent(s)
        job=queue.claim(identity,job_id=job_id,desktop=True)
        if not job:raise ValueError('账号授权、通道版本或核验条件未满足；首次使用请选择该桌面通道的首次核验任务')
        if resume:job['desktop_resume_url']=resume
        with db.tx() as s:job['assets_meta']={identifier:{'suffix':Path(s.get(Asset,identifier).name).suffix.lower()} for identifier in job['payload'].get('assets',[]) if s.get(Asset,identifier)}
        return job
    def owner(job_id):
        with db.tx() as s:
            setting=s.get(Setting,'desktop_agent');job=s.get(Job,job_id)
            if not setting or not job or job.agent_id!=setting.value['id']:raise ValueError('任务未分配给本机桌面')
            return job.agent_id,job.platform
    @app.post('/api/desktop/jobs/{job_id}/heartbeat')
    def heartbeat(job_id:str,data:Generation,user=Depends(local)):
        identity,_=owner(job_id);queue.heartbeat(job_id,identity,data.generation);return {'ok':True}
    @app.post('/api/desktop/jobs/{job_id}/submitting')
    def submitting(job_id:str,data:Generation,user=Depends(local)):
        identity,_=owner(job_id);queue.submitting(job_id,identity,data.generation);return {'ok':True}
    @app.post('/api/desktop/jobs/{job_id}/result')
    def result(job_id:str,data:DesktopResult,user=Depends(local)):
        identity,platform=owner(job_id)
        if data.outcome not in {'published','draft','unknown'}:raise ValueError('操作结果无效')
        if data.outcome!='unknown' and not allowed_url(platform,data.remote_url):raise ValueError('请填写该平台的真实作品或草稿 HTTPS 链接')
        state=queue.complete(job_id,identity,data.generation,{'ok':data.outcome=='published','draft':data.outcome=='draft','remote_id':data.remote_url or None,'error_class':'unknown'})
        with db.tx() as s:
            job=s.get(Job,job_id)
            if state=='succeeded':
                c=s.get(Channel,job.channel_id);c.evidence={**c.evidence,'method':'desktop_user_attestation'}
            audit(s,'job.desktop_confirmed',job_id,outcome=data.outcome)
        return {'state':state}
