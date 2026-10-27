import concurrent.futures,json,time,zipfile,base64,os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from sqlalchemy import select
from omnidispatch.db import Base,Database,Account,Credential,Channel,Agent,Job,Attempt,Admin,AccountLock,Update
from omnidispatch.security import Vault,ph
from omnidispatch.queue import Queue,Conflict
from omnidispatch.updates import Updates
from omnidispatch.app import create_app
@pytest.fixture
def system(tmp_path):
    url=os.getenv('OMNI_TEST_DATABASE_URL','sqlite:///'+str(tmp_path/'test.db'))
    db=Database(url)
    if url.startswith('postgresql'):
        assert url.endswith('/omni_test'),'Refusing non-test database'
        Base.metadata.drop_all(db.engine)
    db.initialize();vault=Vault(tmp_path);clock=[1000.]
    q=Queue(db,vault,lambda:clock[0])
    with db.tx() as s:
        a=Account(label='Brand',platform='x',state='active',min_interval=30);s.add(a);s.flush()
        for cid,priority in [('primary',90),('backup',50)]:
            s.add(Channel(id=cid,engine='xapi',platform='x',version='1',enabled=True,health='healthy',priority=priority,capabilities={'media':['text']}))
            s.add(Credential(account_id=a.id,channel_id=cid,ciphertext=vault.encrypt({'access_token':'test-only'})))
        agent=Agent(label='Node',token_hash=ph.hash('test-only'),capabilities={'channels':{c:{'version':'1','ready':True} for c in ['primary','backup']}});s.add(agent);s.flush();ids=(a.id,agent.id)
    yield db,q,ids,clock,vault
    db.engine.dispose()
def enqueue(q,a,key='request-123'):return q.enqueue(key,a,{'title':'Title','kind':'text','assets':[]})
def test_duplicate_intent_and_conflict(system):
    db,q,(a,n),clock,vault=system
    one=enqueue(q,a);two=enqueue(q,a)
    assert one.id==two.id
    with pytest.raises(Conflict):q.enqueue('request-123',a,{'title':'Different','kind':'text'})
    with db.tx() as s:assert len(s.scalars(select(Job)).all())==1
def test_failover_before_submit_retains_account(system):
    db,q,(a,n),clock,vault=system;j=enqueue(q,a);first=q.claim(n)
    assert first['channel']=='primary'
    assert q.complete(j.id,n,first['generation'],{'ok':False,'error_class':'engine_crash'})=='queued'
    second=q.claim(n);assert second['channel']=='backup' and second['account_id']==a
    with db.tx() as s:assert len(s.scalars(select(Attempt)).all())==2
def test_unknown_submission_never_replayed_and_blocks_account(system):
    db,q,(a,n),clock,vault=system;j=enqueue(q,a);other=enqueue(q,a,'request-456');leased=q.claim(n)
    q.submitting(j.id,n,leased['generation'])
    with pytest.raises(Conflict):q.submitting(j.id,n,leased['generation'])
    q.complete(j.id,n,leased['generation'],{'ok':False,'error_class':'engine_crash'})
    assert q.claim(n) is None
    with db.tx() as s:assert s.get(Job,j.id).state=='needs_verify' and s.get(AccountLock,a)
    with pytest.raises(Conflict):q.resolve(j.id,'retry')
    q.resolve(j.id,'confirm_published','remote-1')
    assert q.claim(n) is None # account publication pacing retained
    clock[0]+=31;assert q.claim(n)['id']==other.id
def test_lease_expiration_fences_old_agent(system):
    db,q,(a,n),clock,vault=system;j=enqueue(q,a);lease=q.claim(n);clock[0]+=91
    fresh=q.claim(n);assert fresh['generation']==2
    with pytest.raises(Conflict):q.submitting(j.id,n,1)
    q.submitting(j.id,n,2);clock[0]+=91
    assert q.claim(n) is None
    with db.tx() as s:assert s.get(Job,j.id).state=='needs_verify'
def test_parallel_claim_serializes_account(system):
    db,q,(a,n),clock,vault=system
    for i in range(5):enqueue(q,a,f'request-{i}')
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(lambda _:q.claim(n),range(5)))
    assert sum(r is not None for r in results)==1
@pytest.mark.parametrize('kind,state',[('auth_expired','needs_action'),('rate_limited','retry_wait'),('risk_control','needs_action'),('egress_unavailable','needs_action')])
def test_shared_failure_does_not_blindly_switch(system,kind,state):
    db,q,(a,n),clock,vault=system;j=enqueue(q,a);lease=q.claim(n)
    assert q.complete(j.id,n,lease['generation'],{'ok':False,'error_class':kind})==state
    assert q.claim(n) is None
    with db.tx() as s:assert s.get(Job,j.id).account_id==a and s.get(Channel,'primary').failures==0

def test_auth_csrf_redaction_and_agent_revoke(tmp_path):
    app=create_app(tmp_path,background=False)
    with app.state.db.tx() as s:s.add(Admin(username='admin',password=ph.hash('long-test-password')))
    with TestClient(app) as c:
        assert c.get('/api/accounts').status_code==401
        login=c.post('/api/login',json={'username':'admin','password':'long-test-password'});assert login.status_code==200
        assert c.post('/api/accounts',json={'label':'A','platform':'x'}).status_code==403
        c.headers['x-csrf-token']=login.json()['csrf']
        a=c.post('/api/accounts',json={'label':'A','platform':'x'}).json()
        assert c.post('/api/accounts/'+a['id']+'/credentials',json={'channel_id':'xapi-x','value':{'access_token':'TOP-SECRET'}}).status_code==200
        assert 'TOP-SECRET' not in c.get('/api/accounts').text
        assert 'TOP-SECRET' not in c.get('/api/audit').text
        created=c.post('/api/agents',json={'label':'Node'}).json();headers={'Authorization':'Bearer '+created['token']}
        assert c.post('/agent/heartbeat',json={'capabilities':{}},headers=headers).status_code==200
        c.post('/api/agents/'+created['id']+'/revoke',json={})
        assert c.post('/agent/claim',json={},headers=headers).status_code==401
        assert c.post('/api/logout',json={},headers={'Origin':'https://evil.invalid'}).status_code==403

def test_login_backoff_persisted(tmp_path):
    app=create_app(tmp_path,background=False)
    with TestClient(app) as c:
        for _ in range(5):assert c.post('/api/login',json={'username':'wrong','password':'wrong'}).status_code==401
        assert c.post('/api/login',json={'username':'wrong','password':'wrong'}).status_code==429

def test_signed_archive_rejects_traversal_and_empty_trust(system,tmp_path):
    db,q,ids,clock,vault=system;manager=Updates(db,tmp_path)
    with db.tx() as s:u=Update(engine='sau',version='1.2.3',source='https://github.com/dreammis/social-auto-upload');s.add(u);s.flush();identifier=u.id
    path=tmp_path/'bad.zip'
    with zipfile.ZipFile(path,'w') as z:z.writestr('../escape','bad')
    key=Ed25519PrivateKey.generate();public=base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode();signature=base64.b64encode(key.sign(path.read_bytes())).decode()
    with pytest.raises(ValueError):manager.stage(identifier,path,signature,'')
    with pytest.raises(ValueError):manager.stage(identifier,path,signature,public)
    assert not (tmp_path/'escape').exists()

def test_update_promote_requires_actual_observation(system,tmp_path):
    db,q,ids,clock,vault=system;manager=Updates(db,tmp_path)
    with db.tx() as s:u=Update(engine='sau',version='1.2.3',state='canary',source='https://github.com',data={'canary_started':time.time()-90000,'live_successes':0});s.add(u);s.flush();identifier=u.id
    with pytest.raises(ValueError):manager.transition(identifier,'promote')

def test_totp_recovery_is_one_time(tmp_path):
    import pyotp
    app=create_app(tmp_path,background=False)
    with app.state.db.tx() as s:s.add(Admin(username='admin',password=ph.hash('long-test-password')))
    with TestClient(app) as c:
        logged=c.post('/api/login',json={'username':'admin','password':'long-test-password'}).json();c.headers['x-csrf-token']=logged['csrf']
        setup=c.post('/api/totp/setup',json={'password':'long-test-password'}).json()
        enabled=c.post('/api/totp/confirm',json={'password':'long-test-password','code':pyotp.TOTP(setup['secret']).now()}).json()
        assert len(enabled['recovery_codes'])==8
        c.post('/api/logout',json={});code=enabled['recovery_codes'][0]
        assert c.post('/api/login',json={'username':'admin','password':'long-test-password','totp':code}).status_code==200
        assert c.post('/api/login',json={'username':'admin','password':'long-test-password','totp':code}).status_code==401

def test_staged_signature_does_not_activate_or_rewrite_old_task(system,tmp_path):
    db,q,(a,n),clock,vault=system;job=enqueue(q,a);lease=q.claim(n);manager=Updates(db,tmp_path)
    with db.tx() as s:u=Update(engine='xapi',version='2.0.0',source='https://github.com');s.add(u);s.flush();identifier=u.id
    archive=tmp_path/'valid.zip'
    with zipfile.ZipFile(archive,'w') as z:z.writestr('omni-engine.json',json.dumps({'engine':'xapi','version':'2.0.0','adapter_protocol':1}))
    key=Ed25519PrivateKey.generate();public=base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode();sig=base64.b64encode(key.sign(archive.read_bytes())).decode()
    manager.stage(identifier,archive,sig,public)
    with db.tx() as s:
        assert s.get(Update,identifier).state=='staged'
        assert s.get(Job,job.id).engine_version=='1'
        assert s.get(Channel,'primary').version=='1'
