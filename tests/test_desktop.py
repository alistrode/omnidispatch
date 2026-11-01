"""Local desktop workflows; isolated fixtures, no external publication."""
import json,time
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select,func
from omnidispatch.app import create_app
from omnidispatch.db import Admin,Session,Account,Agent,Channel,Credential,Job,AccountLock
from omnidispatch.security import ph
from omnidispatch.local_engines import import_credential,atomic_json
@pytest.fixture
def app(tmp_path):
    application=create_app(tmp_path/'state',background=False)
    with application.state.db.tx() as s:s.add(Admin(username='admin',password=ph.hash('long-test-password')))
    yield application
    application.state.db.engine.dispose()
def client(app):return TestClient(app,base_url='http://127.0.0.1',client=('127.0.0.1',57000))
def login(c):
    r=c.post('/api/bootstrap');assert r.status_code==200
    c.headers['x-csrf-token']=r.json()['csrf']
def test_bootstrap_reuses_session_and_rejects_forwarded_origin(app):
    with client(app) as c:
        login(c);one=c.cookies.get('omni_session');login(c)
        assert c.cookies.get('omni_session')==one
        with app.state.db.tx() as s:assert s.scalar(select(func.count()).select_from(Session))==1
        assert c.post('/api/bootstrap',headers={'X-Forwarded-For':'192.0.2.1'}).status_code==401
        assert c.post('/api/bootstrap',headers={'Origin':'https://elsewhere.invalid'}).status_code==403
def test_bootstrap_ipv6_loopback(app):
    with TestClient(app,base_url='http://[::1]',client=('::1',57000)) as c:assert c.post('/api/bootstrap').status_code==200

def test_version_change_invalidates_previous_attestation(app):
    with app.state.db.tx() as s:
        ch=s.get(Channel,'xapi-x');ch.version='old';ch.health='healthy';ch.enabled=True;ch.evidence={'remote_id':'previous'}
    with client(app) as c:
        login(c);assert c.post('/api/channels/xapi-x',json={'version':'new','priority':50,'enabled':False}).status_code==200
    with app.state.db.tx() as s:
        ch=s.get(Channel,'xapi-x');assert ch.health=='unverified' and ch.evidence=={}

def test_explicit_verification_job_breaks_first_publish_deadlock(app):
    db=app.state.db;vault=app.state.vault;q=app.state.queue
    with db.tx() as s:
        ch=s.get(Channel,'xapi-x');ch.version='api-v2';ch.enabled=False
        a=Account(label='test',platform='x',state='active');s.add(a);s.flush();aid=a.id
        s.add(Credential(account_id=aid,channel_id=ch.id,ciphertext=vault.encrypt({'access_token':'test'})))
        n=Agent(label='test-node',token_hash=ph.hash('not-real'),capabilities={'channels':{ch.id:{'version':ch.version,'ready':True}}});s.add(n);s.flush();nid=n.id
    normal=q.enqueue('normal-job',aid,{'kind':'text','title':'Normal','assets':[]});assert q.claim(nid) is None
    trial=q.enqueue('verify-job',aid,{'kind':'text','title':'First verification','assets':[],'verification_channel':'xapi-x'})
    lease=q.claim(nid);assert lease['id']==trial.id
    q.submitting(trial.id,nid,lease['generation'])
    q.complete(trial.id,nid,lease['generation'],{'ok':False,'error_class':'engine_crash'})
    assert q.claim(nid) is None
    q.resolve(trial.id,'confirm_published','owner-attested-id')
    with db.tx() as s:
        ch=s.get(Channel,'xapi-x');assert ch.health=='healthy' and not ch.enabled
        assert ch.evidence['method']=='administrator_attestation'
        assert s.get(Job,normal.id).state=='queued'

def test_import_binds_exact_account_and_refuses_identity_swap(app,tmp_path):
    state=tmp_path/'state';engine=tmp_path/'engines'/'biliup'/'v1';engine.mkdir(parents=True);binary=engine/'biliup.exe';binary.write_bytes(b'fixture')
    atomic_json(state/'agent.json',{'token':'fixture','channels':{'biliup-bilibili':{'adapter':'biliup','argv':[str(binary)],'version':'v1'}}})
    with app.state.db.tx() as s:
        a=Account(label='First',platform='bilibili');b=Account(label='Second',platform='bilibili');s.add_all([a,b]);s.flush();aid=a.id;bid=b.id
    folder=state/'engine-accounts'/'biliup-bilibili'/bid;folder.mkdir(parents=True)
    def cookie(uid):return {'cookie_info':{'cookies':[{'name':k,'value':v} for k,v in {'SESSDATA':'private','bili_jct':'private','DedeUserID':uid}.items()]}}
    atomic_json(folder/'cookies.json',cookie('42'))
    import_credential(state,app.state.db,app.state.vault,'biliup-bilibili',bid)
    with app.state.db.tx() as s:
        assert s.scalar(select(Credential).where(Credential.account_id==aid)) is None
        assert s.get(Account,bid).state=='active'
    atomic_json(folder/'cookies.json',cookie('99'))
    with pytest.raises(ValueError,match='身份'):import_credential(state,app.state.db,app.state.vault,'biliup-bilibili',bid)

def test_import_requires_explicit_account_and_rejects_mismatch(app):
    with client(app) as c:
        login(c)
        assert c.post('/api/channels/biliup-bilibili/import-login',json={}).status_code==422
        assert c.post('/api/channels/biliup-bilibili/import-login',json={'account_id':'../escape'}).status_code==400

def test_enabling_requires_live_node_and_credential(app):
    with app.state.db.tx() as s:
        ch=s.get(Channel,'xapi-x');ch.version='api-v2';ch.health='healthy'
    with client(app) as c:
        login(c)
        assert c.post('/api/channels/xapi-x',json={'version':'api-v2','priority':50,'enabled':True}).status_code==400

def test_biliup_structured_remote_id_only(tmp_path,monkeypatch):
    import sys
    from omnidispatch.adapters import Adapter
    evidence=[b'INFO response: {"bvid":"BV1xx411c7mD"}\n',b'upload returned exit code zero, no platform id\n']
    class Process:
        returncode=0
        def __init__(self,args,**kwargs):kwargs['stdout'].write(evidence.pop(0))
        def wait(self,timeout):return 0
    monkeypatch.setattr('omnidispatch.adapters.subprocess.Popen',Process)
    job={'payload':{'title':'fixture','kind':'video','options':{'tid':1}},'credential':{'cookies':{'cookie_info':{}}},'egress':{}}
    def publish(folder):
        folder.mkdir();return Adapter({'adapter':'biliup','argv':[sys.executable]},job,[tmp_path/'fixture.mp4'],folder).publish()
    first=publish(tmp_path/'one');assert first['ok'] and first['remote_id']=='BV1xx411c7mD'
    second=publish(tmp_path/'two');assert not second['ok'] and not second['remote_id']
