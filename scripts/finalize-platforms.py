"""Register installed platform channels locally; leave every new capability unverified."""
from pathlib import Path
from omnidispatch.db import Database
from omnidispatch.catalog import seed
from omnidispatch.platform_specs import PLATFORM_SPECS
from omnidispatch.local_engines import configure_channel
root=Path(__file__).resolve().parent.parent;state=root/'state';db=Database('sqlite:///'+str(state/'hub.db'));db.initialize()
with db.tx() as s:seed(s)
for platform in PLATFORM_SPECS:configure_channel(state,db,'desktopweb-'+platform,'v1')
for platform in ['douyin','kuaishou']:configure_channel(state,db,'spreado-'+platform,'v1.2.0')
for platform in ['douyin','kuaishou','baijiahao','weibo','zhihu','xiaohongshu','tencent','youtube']:configure_channel(state,db,'sau-'+platform,'3847fff')
db.engine.dispose()
print('Installed desktop and community publishing channels registered; no channel was marked live or enabled')
