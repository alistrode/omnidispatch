"""Switch this local installation to the reviewed desktop engine configurations."""
from pathlib import Path
import json
from omnidispatch.local_engines import read_json,atomic_json,configure_channel
from omnidispatch.db import Database
root=Path(__file__).resolve().parent.parent;state=root/'state'
db=Database('sqlite:///'+str(state/'hub.db'))
for channel,version in [('spreado-tencent','v1.2.0'),('spreado-xiaohongshu','v1.2.0'),('xhsmcp-xiaohongshu','v2.5.5-omni')]:configure_channel(state,db,channel,version)
settings=read_json(state/'runtime-settings.json');settings.pop('cloudflared',None)
settings.setdefault('environment',{}).pop('OMNI_PUBLIC_ORIGIN',None);settings['environment']['OMNI_SECURE_COOKIE']='0'
atomic_json(state/'runtime-settings.json',settings)
db.engine.dispose()
print('Local desktop engine configuration saved; credentials preserved; public tunnel disabled')
