"""Create a source-only local snapshot, excluding private state and bundled third-party code."""
import datetime,hashlib,json,sys,zipfile
from pathlib import Path
root=Path(sys.argv[1]).resolve();dev=root/'dev';stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
target=root/'backups'/('OmniDispatch_v'+stamp+'_after-change.zip')
excluded={'.runtime','.runtime-cache','validation-tools','_state','__pycache__','.pytest_cache','vendor','tests','config','node_modules','.git'}
with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as z:
    for file in dev.rglob('*'):
        rel=file.relative_to(dev)
        if not file.is_file() or any(x in excluded for x in rel.parts) or file.suffix.lower() in {'.pyc','.pyd','.dll','.exe','.log','.png','.zip'}:continue
        z.write(file,'dev/'+rel.as_posix())
with zipfile.ZipFile(target) as z:
    assert 'dev/omnidispatch/app.py' in z.namelist() and 'dev/desktop/OmniDispatch.cs' in z.namelist()
    assert z.testzip() is None
print(json.dumps({'source_snapshot':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'private_state_included':False}))
