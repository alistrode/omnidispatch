"""Run large local packaging outside the short-lived SSH command, recording each phase."""
import contextlib,datetime,json,os,runpy,sys,traceback
from pathlib import Path
root=Path(sys.argv[1]).resolve();release=root/'release';folder=release/'logs';folder.mkdir(exist_ok=True)
status_file=folder/'package-status.json'
def status(phase,**extra):
    value={'phase':phase,'pid':os.getpid(),'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),**extra}
    temporary=status_file.with_suffix('.tmp');temporary.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8');os.replace(temporary,status_file)
try:
    with (folder/'package-check.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
        status('packaging');sys.argv=['package-desktop.py',str(release)];runpy.run_path(str(root/'dev'/'scripts'/'package-desktop.py'),run_name='__main__');log.flush()
        status('checking_extracted_bundle');sys.argv=['check-portable.py',str(release/'OmniDispatch-Desktop-Windows-x64.zip')];runpy.run_path(str(root/'dev'/'scripts'/'check-portable.py'),run_name='__main__');log.flush()
        status('complete',archive=str(release/'OmniDispatch-Desktop-Windows-x64.zip'))
except BaseException as error:
    status('failed',error=type(error).__name__,message=str(error));raise
