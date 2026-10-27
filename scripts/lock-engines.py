"""Capture upstream release evidence. Requires authenticated gh CLI; emits no credentials."""
import subprocess,json,concurrent.futures
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from omnidispatch.catalog import SOURCES

def get(item):
    engine,repo=item
    response=subprocess.run(['gh','api',f'repos/{repo}/releases/latest'],capture_output=True,text=True)
    if response.returncode:return engine,{'repository':repo,'release':None,'state':'no_release_or_unavailable'}
    r=json.loads(response.stdout)
    return engine,{'repository':repo,'release':r.get('tag_name'),'published_at':r.get('published_at'),'assets':[{'name':a['name'],'url':a['browser_download_url'],'size':a['size']} for a in r.get('assets',[])]}
records=dict(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(get,SOURCES.items()))
install=[]
selection={'xhsmcp':('xiaohongshu-mcp-windows-amd64.exe',None),'ytuploader':('youtubeuploader_1.25.5_Windows_amd64.zip','youtubeuploader.exe'),'spreado':('spreado-windows-x64.exe',None),'resin':('resin-windows-amd64.zip','resin.exe')}
for engine,(name,binary) in selection.items():
    entry=records[engine];a=next(x for x in entry['assets'] if x['name']==name)
    install.append({'engine':engine,'version':entry['release'],'url':a['url'],'size':a['size'],'binary':binary or name,'archive':'zip' if binary else 'raw','help_args':['--help']})
install.append({'engine':'ffprobe','version':'5.1.0','url':'https://registry.npmjs.org/@ffprobe-installer/win32-x64/-/win32-x64-5.1.0.tgz','binary':'ffprobe.exe','archive':'tgz','help_args':['-version']})
(root:=Path(__file__).resolve().parent.parent/'engines.lock.json').write_text(json.dumps({'observed_date':'2026-10-27','sources':records,'installable_windows':install},ensure_ascii=False,indent=2))
print('Release evidence locked for',len(records),'upstreams; installable assets:',len(install))
