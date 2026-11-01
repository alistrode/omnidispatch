"""Verify a clean extracted bundle with its own interpreter, without contacting platforms."""
import os,sys,subprocess,tempfile,zipfile,json
from pathlib import Path
archive=Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix='omni-portable-',dir=archive.parent.parent/'dev'/'_state') as folder:
    with zipfile.ZipFile(archive) as z:z.extractall(folder)
    root=Path(folder)/'OmniDispatch'
    script=root/'check_imports.py'
    script.write_text("from pathlib import Path\nfrom omnidispatch.app import create_app\nimport omnidispatch,sys,json\np=Path(__file__).parent\napp=create_app(p/'check-state',database_url='sqlite:///'+str(p/'check-state'/'hub.db'),background=False)\nassert Path(omnidispatch.__file__).resolve().is_relative_to(p)\napp.state.db.engine.dispose()\nprint(json.dumps({'portable_import':True,'python':sys.version.split()[0],'local_state_created':True}))\n",encoding='utf-8')
    result=subprocess.run([str(root/'runtime'/'python.exe'),str(script)],cwd=root,capture_output=True,timeout=90,env={**os.environ,'PYTHONUTF8':'1'})
    print(result.stdout.decode('utf-8','replace'))
    if result.returncode:raise RuntimeError(result.stderr.decode('utf-8','replace'))
    engine=subprocess.run([str(root/'engines'/'sau'/'runtime'/'python.exe'),str(root/'engines'/'sau'/'source'/'omni_sau_cli.py'),'--help'],cwd=root,capture_output=True,timeout=60,env={**os.environ,'PYTHONUTF8':'1','OMNI_SAU_WORK':str(root/'check-sau')})
    if engine.returncode:raise RuntimeError(engine.stderr.decode('utf-8','replace'))
    assert b'zhihu' in engine.stdout and b'douyin' in engine.stdout
    print(json.dumps({'portable_community_engine':True,'isolated_python':True}))

    smoke=subprocess.run([str(root/'engines/xhsmcp/v2.5.5-omni/omni-browser-smoke.exe')],cwd=root,capture_output=True,timeout=60,env={**os.environ,'OMNI_XHS_BROWSER':str(root/'engines/browser/chromium-cft/chrome-win64/chrome.exe')})
    if smoke.returncode:raise RuntimeError(smoke.stderr.decode('utf-8','replace'))
    assert b'"bundled_standard_chromium":true' in smoke.stdout
    print(json.dumps({'portable_xhs_browser':True,'external_publications':0}))
