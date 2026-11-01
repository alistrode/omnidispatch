"""Install fixed official runtimes/dependencies for the selected community engine."""
import hashlib,json,shutil,sys,urllib.request,zipfile
from pathlib import Path
root=Path(sys.argv[1]).resolve();dev=root/'dev';engine=root/'release'/'engines'/'sau';rt=engine/'runtime';cache=dev/'.runtime-cache'/'sau';cache.mkdir(parents=True,exist_ok=True);rt.mkdir(parents=True,exist_ok=True)
url='https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip';archive=cache/'python-3.12.10-embed-amd64.zip'
if not archive.exists():
    with urllib.request.urlopen(url,timeout=90) as response,archive.open('wb') as out:shutil.copyfileobj(response,out)
if not (rt/'python.exe').exists():
    with zipfile.ZipFile(archive) as z:z.extractall(rt)
(rt/'python312._pth').write_text('python312.zip\n.\nLib\\site-packages\n..\\source\nimport site\n')
site=rt/'Lib'/'site-packages';site.mkdir(parents=True,exist_ok=True)
manifest=json.loads((dev/'desktop'/'sau-dependencies.json').read_text())
for item in manifest:
    file=cache/item['name']
    if not file.exists():
        with urllib.request.urlopen(item['url'],timeout=120) as response,file.open('wb') as out:shutil.copyfileobj(response,out)
    if hashlib.sha256(file.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Dependency digest mismatch')
    with zipfile.ZipFile(file) as z:z.extractall(site)
shutil.copytree(dev/'vendor'/'sau',engine/'source',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
(engine/'BUILD.json').write_text(json.dumps({'source':'https://github.com/dreammis/social-auto-upload','commit':'3847fff01f5434a8a32829833163cd6723cabc59','python_source':url,'python_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'wheels':manifest},indent=2))
print('Community source and isolated Python 3.12 runtime installed locally')
