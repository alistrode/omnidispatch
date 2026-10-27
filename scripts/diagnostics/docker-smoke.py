import subprocess,re,json,time,uuid
import httpx
prefix=['env','-u','DOCKER_HOST','-u','DOCKER_CONTEXT','-u','DOCKER_TLS','-u','DOCKER_TLS_VERIFY','-u','DOCKER_CERT_PATH','docker','--host=unix:///var/run/docker.sock']
raw=subprocess.check_output(prefix+['exec','omni-hub-validation','cat','/app/state/ADMIN-CREDENTIALS.private.txt']).decode();password=re.search('初始密码: (.+)',raw).group(1)
with httpx.Client(base_url='http://127.0.0.1:58791',trust_env=False) as c:
 assert c.get('/api/health').json()['database']=='postgresql'
 assert c.get('/api/overview').status_code==401
 r=c.post('/api/login',json={'username':'admin','password':password});r.raise_for_status();c.headers['X-CSRF-Token']=r.json()['csrf']
 a=c.post('/api/accounts',json={'label':'Docker integration only','platform':'x'});a.raise_for_status()
 j=c.post('/api/jobs',json={'idempotency_key':str(uuid.uuid4()),'account_id':a.json()['id'],'title':'integration test - never publish','kind':'text'});j.raise_for_status()
 assert c.post('/api/jobs/'+j.json()['id']+'/action',json={'action':'cancel'}).status_code==200
 assert c.post('/api/logout',json={}).status_code==200
 print(json.dumps({'docker_hub_started':True,'database':'postgresql','authenticated_api_flow':True,'job_cancelled_without_publish':True,'container_uid':subprocess.check_output(prefix+['exec','omni-hub-validation','id','-u']).decode().strip()}))
