"""Assemble source and a clean Windows runtime from official embed ZIP + pinned wheels."""
import sys,zipfile,shutil,json
from pathlib import Path
source=Path(__file__).resolve().parent.parent
out=Path(sys.argv[1]);runtime=Path(sys.argv[2]);wheels=Path(sys.argv[3])
if out.exists():raise SystemExit('Output must not exist')
out.mkdir(parents=True)
for name in ['omnidispatch','config','scripts']:
    shutil.copytree(source/name,out/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ['Start.cmd','README.md','DESIGN.md','requirements.lock.txt','THIRD-PARTY.md']:
    if (source/name).exists():shutil.copy2(source/name,out/name)
rt=out/'runtime';rt.mkdir()
with zipfile.ZipFile(runtime) as z:z.extractall(rt)
site=rt/'Lib'/'site-packages';site.mkdir(parents=True)
for wheel in sorted(wheels.glob('*.whl')):
    # Test tools remain in the dev validation environment, not in the release.
    if wheel.name.startswith(('pytest-','iniconfig-','pluggy-','pygments-')):continue
    with zipfile.ZipFile(wheel) as z:z.extractall(site)
for p in rt.glob('python*._pth'):
    lines=p.read_text().replace('#import site','import site');p.write_text(lines+'\nLib\\site-packages\n..\n')
(out/'BUILD.json').write_text(json.dumps({'version':'0.1.0','python':'3.14.10','runtime_source':'https://www.python.org/ftp/python/3.14.10/python-3.14.10-embed-amd64.zip','wheel_files':[p.name for p in sorted(wheels.glob('*.whl'))],'test_tools_in_release':False},indent=2))
print('Portable runtime assembled:',out)
