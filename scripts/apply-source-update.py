"""Local initial-deployment code update; never includes runtime/state or platform credentials."""
import sys,zipfile,shutil,datetime
from pathlib import Path,PurePosixPath
root=Path(sys.argv[1]).resolve();archive=Path(sys.argv[2]);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
backup=root/'backups'/('source-before-'+stamp+'.zip')
with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED) as z:
    for prefix,folder in [('dev',root/'dev'),('release/omnidispatch',root/'release'/'omnidispatch'),('release/scripts',root/'release'/'scripts')]:
        for p in folder.rglob('*'):
            if p.is_file() and not any(x in p.parts for x in ['__pycache__','validation-tools','node_modules','.pytest_cache','tests']):z.write(p,prefix+'/'+str(p.relative_to(folder)))
with zipfile.ZipFile(archive) as z:
    for info in z.infolist():
        p=PurePosixPath(info.filename)
        if not p.parts or p.parts[0]!='dev' or '..' in p.parts or '\\' in info.filename or ':' in info.filename or p.is_absolute():raise ValueError('Invalid source update path')
    z.extractall(root)
release=root/'release';dev=root/'dev'
shutil.rmtree(release/'omnidispatch'/'static')
for name in ['omnidispatch','scripts','config']:
    shutil.copytree(dev/name,release/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ['Start.cmd','README.md','DESIGN.md','THIRD-PARTY.md','engines.lock.json','requirements.lock.txt','requirements-runtime.lock.txt']:
    if (dev/name).exists():shutil.copy2(dev/name,release/name)
print('Source updated; previous application source backed up:',backup.name)
