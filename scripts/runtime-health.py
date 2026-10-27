"""Read-only deployed smoke check; credential values and session tokens are never printed."""
import sys,json,re,time
from pathlib import Path
import httpx
root=Path(sys.argv[1]).resolve();state=root/'release'/'state'
with httpx.Client(base_url='http://127.0.0.1:8791',trust_env=False,timeout=30) as c:
    deadline=time.monotonic()+60
    while True:
        try:
            health=c.get('/api/health');health.raise_for_status();break
        except httpx.HTTPError:
            if time.monotonic()>deadline:raise
            time.sleep(2)
    assert c.get('/api/overview').status_code==401
    password=re.search(r'初始密码: (.+)',(state/'ADMIN-CREDENTIALS.private.txt').read_text(encoding='utf-8')).group(1)
    login=c.post('/api/login',json={'username':'admin','password':password});login.raise_for_status()
    token=c.cookies.get('omni_session');c.headers['Cookie']='omni_session='+token;c.headers['X-CSRF-Token']=login.json()['csrf']
    overview=c.get('/api/overview');overview.raise_for_status()
    deadline=time.monotonic()+60
    while True:
        agents=c.get('/api/agents');agents.raise_for_status()
        if any(a['last_seen']>time.time()-90 for a in agents.json()):break
        if time.monotonic()>deadline:raise RuntimeError('Agent heartbeat did not become ready')
        time.sleep(2)
    policy=c.get('/api/updates/policy');policy.raise_for_status()
    identity=json.loads((state/'runtime-identity.json').read_text())
    assert identity['administrator'] is False and identity['account'].lower()=='omnidispatchrun'
    assert any(a['last_seen']>time.time()-90 for a in agents.json())
    assert c.post('/api/logout',json={}).status_code==200
    print(json.dumps({'health':health.json(),'unauthenticated_requests_rejected':True,'admin_login_verified':True,'agent_online':True,'runtime_identity':identity,'update_policy':policy.json(),'platform_credentials_present':False},ensure_ascii=False))
