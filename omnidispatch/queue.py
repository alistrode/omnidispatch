"""Durable account-bound dispatch. Uncertain external side effects never auto-replay."""
import time
from sqlalchemy import select,delete
from .db import Job,Account,Credential,Channel,Agent,AccountLock,Attempt,Update,audit
class Conflict(ValueError):pass
class Queue:
    def __init__(self,db,vault,clock=time.time):self.db=db;self.vault=vault;self.clock=clock
    def enqueue(self,key,account_id,payload,due=None):
        with self.db.tx() as s:
            old=s.scalar(select(Job).where(Job.key==key))
            if old:
                if old.account_id!=account_id or old.payload!=payload:raise Conflict('幂等键已用于不同发布内容')
                return old
            account=s.get(Account,account_id)
            if not account:raise ValueError('账号不存在')
            if payload.get('kind') not in {'video','images','text'}:raise ValueError('素材类型无效')
            if not payload.get('title') or len(payload['title'])>300:raise ValueError('标题长度须为 1–300')
            if payload.get('kind')!='text' and not payload.get('assets'):raise ValueError('请先上传素材')
            job=Job(key=key,account_id=account_id,platform=account.platform,payload=payload,due=due if due is not None else self.clock())
            s.add(job);s.flush();audit(s,'job.queued',job.id,account_id=account_id)
            return job
    def expire(self,s):
        t=self.clock()
        for job in s.scalars(select(Job).where(Job.state.in_(['preparing','submitting']),Job.lease_until<t).with_for_update()):
            attempt=s.scalar(select(Attempt).where(Attempt.job_id==job.id,Attempt.generation==job.generation))
            if job.state=='submitting':
                job.state='needs_verify';job.reason='提交期间失去执行租约；核验平台结果后再处理'
            else:
                job.state='queued';job.reason='提交前执行租约过期，重新排队'
                s.execute(delete(AccountLock).where(AccountLock.job_id==job.id))
            if attempt:attempt.state=job.state;attempt.finished=t
            job.lease_until=0;audit(s,'lease.expired',job.id,state=job.state)
    def claim(self,agent_id):
        with self.db.tx() as s:
            self.expire(s)
            agent=s.get(Agent,agent_id)
            if not agent or not agent.enabled:raise Conflict('节点已撤销')
            agent.last_seen=self.clock()
            caps=agent.capabilities.get('channels',{})
            jobs=s.scalars(select(Job).where(Job.state.in_(['queued','retry_wait']),Job.due<=self.clock()).order_by(Job.due).with_for_update(skip_locked=True).limit(100)).all()
            for job in jobs:
                if s.get(AccountLock,job.account_id):continue
                account=s.scalar(select(Account).where(Account.id==job.account_id).with_for_update(skip_locked=True))
                if not account or account.state!='active' or account.cooldown_until>self.clock():continue
                if account.last_publish+account.min_interval>self.clock():continue
                if s.get(AccountLock,job.account_id):continue
                candidates=[]
                for channel in s.scalars(select(Channel).where(Channel.platform==job.platform,Channel.enabled==True)):
                    installed=caps.get(channel.id,{})
                    credential=s.scalar(select(Credential).where(Credential.account_id==account.id,Credential.channel_id==channel.id,Credential.state=='active'))
                    if not credential or channel.id in job.tried or channel.health=='unverified' or channel.open_until>self.clock():continue
                    if installed.get('version')!=channel.version or not installed.get('ready'):continue
                    if job.payload['kind'] not in channel.capabilities.get('media',[]):continue
                    if account.egress.get('mode','direct') not in installed.get('egress_modes',['direct']):continue
                    if channel.health=='broken' and channel.open_until==0:continue
                    update=s.scalar(select(Update).where(Update.engine==channel.engine,Update.version==channel.version,Update.state.in_(['staged','canary'])))
                    if update and (update.state!='canary' or not job.payload.get('canary') or not account.canary_allowed):continue
                    if job.payload.get('canary') and not account.canary_allowed:continue
                    candidates.append((channel,credential))
                if not candidates:
                    # May be another node's channel. Keep queue recoverable; dashboard explains blockers.
                    job.reason='等待已授权、已核验且版本匹配的通道与在线节点';continue
                candidates.sort(key=lambda x:(x[0].health=='degraded',-x[0].priority,x[0].id))
                channel,credential=candidates[0]
                s.add(AccountLock(account_id=account.id,job_id=job.id))
                job.generation+=1;job.agent_id=agent.id;job.state='preparing';job.lease_until=self.clock()+90
                job.channel_id=channel.id;job.engine_version=channel.version;job.reason=''
                s.add(Attempt(job_id=job.id,generation=job.generation,channel_id=channel.id,version=channel.version))
                audit(s,'job.leased',job.id,agent=agent.id,channel=channel.id,generation=job.generation)
                return {'id':job.id,'generation':job.generation,'channel':channel.id,'engine':channel.engine,'engine_version':channel.version,
                        'platform':job.platform,'payload':job.payload,'credential':self.vault.decrypt(credential.ciphertext),'egress':account.egress,'account_id':account.id}
        return None
    def owned(self,s,job_id,agent_id,generation):
        job=s.get(Job,job_id,with_for_update=True)
        agent=s.get(Agent,agent_id)
        if not agent or not agent.enabled:raise Conflict('节点已撤销')
        if not job or job.agent_id!=agent_id or job.generation!=generation or job.state not in {'preparing','submitting'} or job.lease_until<self.clock():raise Conflict('执行代次或租约已失效；禁止继续提交')
        return job
    def heartbeat(self,job_id,agent_id,generation):
        with self.db.tx() as s:
            job=self.owned(s,job_id,agent_id,generation);job.lease_until=self.clock()+90
            s.get(Agent,agent_id).last_seen=self.clock()
    def submitting(self,job_id,agent_id,generation):
        with self.db.tx() as s:
            job=self.owned(s,job_id,agent_id,generation)
            if job.state!='preparing':raise Conflict('提交意图已存在；禁止再次提交')
            job.state='submitting';job.lease_until=self.clock()+90
            attempt=s.scalar(select(Attempt).where(Attempt.job_id==job.id,Attempt.generation==generation));attempt.state='submitting'
            audit(s,'job.submitting',job.id,generation=generation)
    def complete(self,job_id,agent_id,generation,result):
        with self.db.tx() as s:
            job=self.owned(s,job_id,agent_id,generation)
            account=s.get(Account,job.account_id);channel=s.get(Channel,job.channel_id)
            attempt=s.scalar(select(Attempt).where(Attempt.job_id==job.id,Attempt.generation==generation))
            kind=result.get('error_class','unknown');remote_id=result.get('remote_id')
            if result.get('ok') and remote_id and job.state=='submitting':
                job.state='succeeded';job.remote_id=str(remote_id)[:300];job.reason='平台接受提交；后续审核与可见性以平台为准'
                account.last_publish=self.clock();channel.failures=0;channel.health='healthy';channel.open_until=0
            elif job.state=='submitting':
                # Even explicit-looking client errors can arrive after platform side effects.
                # Only adapter evidence of rejection is safe to retry; default is unknown.
                if result.get('definitely_not_submitted') is not True:
                    job.state='needs_verify';job.reason='平台提交结果未知；已阻止跨通道重发'
                else:self.failure(s,job,account,channel,kind)
            else:self.failure(s,job,account,channel,kind)
            attempt.state=job.state;attempt.error_class='' if job.state=='succeeded' else kind;attempt.finished=self.clock()
            job.lease_until=0
            if job.payload.get('canary') and account.canary_allowed:
                update=s.scalar(select(Update).where(Update.engine==channel.engine,Update.version==job.engine_version,Update.state=='canary').with_for_update())
                if update:
                    key='live_successes' if job.state=='succeeded' else 'live_failures'
                    update.data={**update.data,key:update.data.get(key,0)+1}
            # Keep account fenced when an unknown publish is awaiting reconciliation.
            if job.state!='needs_verify':s.execute(delete(AccountLock).where(AccountLock.job_id==job.id))
            audit(s,'job.result',job.id,state=job.state,error_class=attempt.error_class)
            return job.state
    def failure(self,s,job,account,channel,kind):
        if kind in {'engine_missing','engine_crash','engine_incompatible'}:
            job.tried=[*job.tried,channel.id];job.state='queued';job.reason='提交前通道故障；保留账号并切换候选通道'
            channel.failures+=1
            if channel.failures>=3:channel.health='broken';channel.open_until=self.clock()+300
            elif channel.failures>=2:channel.health='degraded'
        elif kind=='auth_expired':
            cred=s.scalar(select(Credential).where(Credential.account_id==account.id,Credential.channel_id==channel.id))
            if cred:cred.state='expired'
            job.state='needs_action';job.reason='该通道授权失效；请重新授权，发布账号保持不变'
        elif kind=='rate_limited':
            account.cooldown_until=self.clock()+300;job.due=account.cooldown_until;job.state='retry_wait';job.reason='平台限流，至少冷却五分钟'
        elif kind=='risk_control':
            account.state='cooling';account.cooldown_until=self.clock()+3600;job.state='needs_action';job.reason='平台要求人工处理；保留账号与出口'
        elif kind=='egress_unavailable':job.state='needs_action';job.reason='指定出口不可用；禁止直连回退'
        else:job.state='needs_action';job.reason='发布前检查未通过，请核对素材、参数或通道配置'
    def resolve(self,job_id,action,remote_id=None):
        with self.db.tx() as s:
            job=s.get(Job,job_id,with_for_update=True)
            if not job:raise ValueError('任务不存在')
            if action=='confirm_published':
                if job.state!='needs_verify' or not remote_id:raise Conflict('需提供实际平台作品 ID')
                job.state='succeeded';job.remote_id=remote_id;s.get(Account,job.account_id).last_publish=self.clock()
            elif action=='confirm_not_published':
                if job.state!='needs_verify':raise Conflict('任务未处于结果核验阶段')
                job.state='queued';job.tried=[];job.due=self.clock();job.reason='人工确认平台未发布，恢复排队'
            elif action=='retry':
                if job.state not in {'needs_action','failed','retry_wait'}:raise Conflict('当前状态不允许重试；未知结果须先核验')
                job.state='queued';job.tried=[];job.due=self.clock();job.reason=''
            elif action=='cancel':
                if job.state not in {'queued','retry_wait','needs_action'}:raise Conflict('正在提交或结果未知，须先核验')
                job.state='cancelled'
            else:raise ValueError('未知动作')
            s.execute(delete(AccountLock).where(AccountLock.job_id==job.id));audit(s,'job.'+action,job.id,remote_id=remote_id)
