"""Platform/intent contracts without making any external publication."""
import time,json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from omnidispatch.app import create_app
from omnidispatch.db import Admin,Account,Channel,Credential,Agent,Job
from omnidispatch.security import ph
from omnidispatch.platform_specs import PLATFORM_SPECS,allowed_url,validate_intent
from omnidispatch.browser_desktop import filter_state
@pytest.fixture
def application(tmp_path):
    app=create_app(tmp_path/'state',background=False)
    with app.state.db.tx() as s:s.add(Admin(username='admin',password=ph.hash('local-test-password')))
    yield app
    app.state.db.engine.dispose()

def login(app):
    c=TestClient(app,base_url='http://127.0.0.1',client=('127.0.0.1',8000))
    r=c.post('/api/bootstrap');c.headers['x-csrf-token']=r.json()['csrf'];return c
@pytest.mark.parametrize('platform',list(PLATFORM_SPECS))
def test_registered_destinations_have_scoped_https(platform):
    assert allowed_url(platform,PLATFORM_SPECS[platform]['home'])
    assert allowed_url(platform,PLATFORM_SPECS[platform]['compose'])
    assert not allowed_url(platform,'https://127.0.0.1/')
    assert not allowed_url(platform,'https://'+PLATFORM_SPECS[platform]['hosts'][0]+'.evil.invalid/')
    assert not allowed_url(platform,'https://user:password@'+PLATFORM_SPECS[platform]['hosts'][0]+'/')

def test_comment_and_reply_targets_are_required():
    base={'kind':'text','description':'A comment','action':'comment'}
    with pytest.raises(ValueError):validate_intent('tieba',base)
    with pytest.raises(ValueError):validate_intent('tieba',{**base,'target_url':'https://www.zhihu.com/question/1'})
    validate_intent('tieba',{**base,'target_url':'https://tieba.baidu.com/p/123'})
    with pytest.raises(ValueError):validate_intent('tieba',{**base,'action':'reply','target_url':'https://tieba.baidu.com/p/123'})
    with pytest.raises(ValueError):validate_intent('weixin',{**base,'target_url':'https://mp.weixin.qq.com/s/example'})

def test_browser_session_is_scoped_and_identity_cannot_silently_change(application):
    with application.state.db.tx() as s:
        a=Account(label='Tieba test',platform='tieba');s.add(a);s.flush();aid=a.id
    c=login(application);url='/api/desktop/accounts/'+aid+'/desktopweb-tieba'
    cookie={'name':'fixture','value':'not-real','domain':'.baidu.com','path':'/','expires':-1,'httpOnly':True,'secure':True,'sameSite':'Lax'}
    assert c.post(url,json={'identity':'user-1','browser_state':{'cookies':[cookie],'origins':[]}}).status_code==200
    assert c.post(url,json={'identity':'user-2','browser_state':{'cookies':[cookie],'origins':[]}}).status_code==400
    cookie['domain']='.evil.invalid'
    assert c.post(url,json={'identity':'user-1','browser_state':{'cookies':[cookie],'origins':[]}}).status_code==400
    c.close()

def test_comments_cannot_fall_through_to_a_post_only_channel(application):
    db=application.state.db;vault=application.state.vault;q=application.state.queue
    with db.tx() as s:
        a=Account(label='X test',platform='x',state='active');s.add(a);s.flush();aid=a.id
        first=s.get(Channel,'xapi-x');first.version='api-v2';first.health='healthy';first.enabled=True;first.capabilities={**first.capabilities,'actions':['publish']}
        desktop=s.get(Channel,'desktopweb-x');desktop.version='v1';desktop.health='healthy';desktop.enabled=True;desktop.evidence={'actions':['comment']}
        for ch in [first,desktop]:s.add(Credential(account_id=aid,channel_id=ch.id,ciphertext=vault.encrypt({'test':'fixture'})))
        n=Agent(label='test',token_hash=ph.hash('not-real'),capabilities={'channels':{first.id:{'version':first.version,'ready':True},desktop.id:{'version':desktop.version,'ready':True}}});s.add(n);s.flush();nid=n.id
    job=q.enqueue('comment-intent',aid,{'title':'comment','description':'body','kind':'text','action':'comment','target_url':'https://x.com/user/status/123','assets':[]})
    claimed=q.claim(nid);assert claimed['channel']=='desktopweb-x' and claimed['id']==job.id

def test_drafts_never_become_publication_success(application):
    db=application.state.db;q=application.state.queue;vault=application.state.vault
    with db.tx() as s:
        a=Account(label='text',platform='tieba',state='active');s.add(a);s.flush();aid=a.id
        ch=s.get(Channel,'desktopweb-tieba');ch.version='v1'
        s.add(Credential(account_id=aid,channel_id=ch.id,ciphertext=vault.encrypt({'test':'fixture'})))
        n=Agent(label='test',token_hash=ph.hash('not-real'),capabilities={'channels':{ch.id:{'version':'v1','ready':True}}});s.add(n);s.flush();nid=n.id
    job=q.enqueue('draft-intent',aid,{'title':'Draft','kind':'text','assets':[],'delivery':'draft','verification_channel':'desktopweb-tieba'})
    claim=q.claim(nid);q.submitting(job.id,nid,claim['generation'])
    assert q.complete(job.id,nid,claim['generation'],{'draft':True,'remote_id':'https://tieba.baidu.com/draft/1'})=='drafted'
    with db.tx() as s:
        assert s.get(Account,aid).last_publish==0
        assert s.get(Channel,'desktopweb-tieba').health=='unverified'

def test_browser_state_filter_drops_other_platforms():
    state={'cookies':[{'domain':'.zhihu.com','name':'a'},{'domain':'.weibo.com','name':'b'}],'origins':[{'origin':'https://www.zhihu.com'},{'origin':'https://evil.invalid'}]}
    filtered=filter_state('zhihu',state)
    assert len(filtered['cookies'])==1 and len(filtered['origins'])==1

def test_xhs_browser_is_resolved_from_bundle_without_user_cache(tmp_path,monkeypatch):
    import omnidispatch.browser_provision as module
    monkeypatch.setattr(module,'__file__',str(tmp_path/'app'/'omnidispatch'/'browser_provision.py'))
    monkeypatch.setenv('LOCALAPPDATA',str(tmp_path/'user-cache'))
    with pytest.raises(ValueError):module.bundled_xhs_browser()
    binary=tmp_path/'app'/'engines'/'browser'/'chromium-cft'/'chrome-win64'/'chrome.exe'
    binary.parent.mkdir(parents=True);binary.write_bytes(b'fixture')
    assert module.bundled_xhs_browser()==str(binary.resolve())
    assert not (tmp_path/'user-cache').exists()
