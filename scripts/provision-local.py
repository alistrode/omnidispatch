"""Configure only this workspace's installed engines; never infer platform credentials."""
import sys,json,os,secrets,base64
from pathlib import Path
root=Path(sys.argv[1]).resolve();release=root/'release';state=release/'state';sys.path.insert(0,str(release))
from omnidispatch.db import Database,Channel
from omnidispatch.catalog import seed
from omnidispatch.security import new_token
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PrivateFormat,PublicFormat,NoEncryption
engines=release/'engines';records=json.loads((engines/'installation-report.json').read_text()) if (engines/'installation-report.json').exists() else []
lock=json.loads((release/'engines.lock.json').read_text());lookup={e['engine']:e for e in lock['installable_windows']}
agent_path=state/'agent.json';agent=json.loads(agent_path.read_text(encoding='utf-8-sig'));channels=agent.get('channels',{})
channels.setdefault('xapi-x',{'adapter':'xapi','version':'api-v2'})
ffprobe=engines/'ffprobe'/'5.1.0'/'ffprobe.exe'
for engine,platforms in [('ytuploader',['youtube']),('spreado',['xiaohongshu','tencent'])]:
    record=next((r for r in records if r['engine']==engine and r['state'] in {'installed','present'}),None)
    if not record:continue
    program=engines/engine/record['version']/lookup[engine]['binary']
    for platform in platforms:
        channels.setdefault(f'{engine}-{platform}',{'adapter':engine,'managed_engine':engine,'version':record['version'],'argv':[str(program)],'ffprobe':str(ffprobe)})
agent['channels']=channels;agent['versions_dir']=str(state/'engine-versions')
temp=state/'agent.json.new';temp.write_text(json.dumps(agent,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(temp,agent_path)
db=Database('sqlite:///'+str(state/'hub.db'));db.initialize()
with db.tx() as s:
    seed(s)
    for cid,cfg in channels.items():
        channel=s.get(Channel,cid)
        if channel and channel.version=='unconfigured':channel.version=cfg['version']
settings_path=state/'runtime-settings.json';settings=json.loads(settings_path.read_text(encoding='utf-8-sig'))
resin=next((r for r in records if r['engine']=='resin'),None)
if resin:
    program=engines/'resin'/resin['version']/'resin.exe'
    if program.exists():
        secret=state/'resin-secrets.private.json'
        if not secret.exists():secret.write_text(json.dumps({'admin_token':new_token(),'proxy_token':new_token()}),encoding='utf-8')
        settings['resin']=str(program)
keydir=root/'backups'/'update-signer-private';public=keydir/'publisher.public.txt';private=keydir/'publisher.private.pem'
# Caller must create the admin-only key directory ACL before this script runs.
if not private.exists():
    key=Ed25519PrivateKey.generate();private.write_bytes(key.private_bytes(Encoding.PEM,PrivateFormat.PKCS8,NoEncryption()));public.write_text(base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode())
settings.setdefault('environment',{})['OMNI_UPDATE_PUBLIC_KEY']=public.read_text().strip()
settings_path.write_text(json.dumps(settings,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'configured_channels':list(channels),'resin_gateway_installed':bool(resin),'publisher_trust_initialized':True,'platform_credentials_imported':False}))
