"""Deploy the locally tested source, keeping private state and browser runtimes intact."""
import datetime,shutil,sys,zipfile
from pathlib import Path
root=Path(sys.argv[1]).resolve();dev=root/'dev';release=root/'release'
backup=root/'backups'/('OmniDispatch_before_platform_expansion_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip')
with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED) as z:
    for file in (release/'omnidispatch').rglob('*'):
        if file.is_file() and '__pycache__' not in file.parts:z.write(file,'release/'+file.relative_to(release).as_posix())
    for file in [release/'OmniDispatch.exe',release/'Start.cmd',release/'README.md']:
        if file.exists():z.write(file,'release/'+file.name)
for name in ['omnidispatch','scripts']:
    shutil.copytree(dev/name,release/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ['README.md','THIRD-PARTY.md','DESIGN.md']:shutil.copy2(dev/name,release/name)
print('Locally tested application source deployed; runtime and private state preserved')
