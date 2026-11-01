"""Apply reviewed source locally, preserving state and external identities."""
import datetime,hashlib,json,shutil,sys,urllib.request,zipfile
from pathlib import Path,PurePosixPath
root=Path(sys.argv[1]).resolve();archive=Path(sys.argv[2]).resolve();dev=root/'dev';release=root/'release'
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup=root/'backups'/('OmniDispatch_release_'+stamp+'_before-desktop.zip')
with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED) as z:
    for folder in ['omnidispatch','scripts','desktop']:
        for file in (release/folder).rglob('*'):
            if file.is_file() and '__pycache__' not in file.parts:z.write(file,'release/'+file.relative_to(release).as_posix())
    for file in release.iterdir():
        if file.is_file():z.write(file,'release/'+file.name)
with zipfile.ZipFile(archive) as z:
    for info in z.infolist():
        p=PurePosixPath(info.filename)
        if not p.parts or p.parts[0]!='dev' or '..' in p.parts or '\\' in info.filename or ':' in info.filename or p.is_absolute():raise ValueError('Unsafe archive path')
    z.extractall(root)
for name in ['omnidispatch','scripts','desktop','config']:
    shutil.copytree(dev/name,release/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ['Start.cmd','README.md','THIRD-PARTY.md']:shutil.copy2(dev/name,release/name)
engine=release/'engines'/'spreado'/'v1.2.0'
shutil.copytree(dev/'vendor'/'spreado'/'spreado',engine/'source'/'spreado',dirs_exist_ok=True)
shutil.copy2(dev/'vendor'/'spreado'/'LICENSE',engine/'LICENSE')
manifest=json.loads((dev/'desktop'/'spreado-dependencies.json').read_text())
wheel_cache=dev/'.runtime-cache'/'spreado-wheels';wheel_cache.mkdir(parents=True,exist_ok=True)
for item in manifest:
    wheel=wheel_cache/item['name']
    if not wheel.exists():
        with urllib.request.urlopen(item['url'],timeout=120) as r,wheel.open('wb') as out:shutil.copyfileobj(r,out)
    if hashlib.sha256(wheel.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Wheel digest mismatch: '+item['name'])
    if item['name'].startswith('typing_extensions-'):continue
    for rt in [release/'runtime',dev/'.runtime']:
        site=rt/'Lib'/'site-packages';site.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(wheel) as z:z.extractall(site)
print(json.dumps({'source_installed':True,'backup':str(backup),'wheel_count':len(manifest)}))
