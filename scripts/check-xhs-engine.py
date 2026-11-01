"""Exercise the patched Go browser on data: only, then a loopback service health check."""
import json,os,socket,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
root=Path(sys.argv[1]).resolve();release=root/'release';sys.path.insert(0,str(release))
from omnidispatch.windows_job import WindowsJob
browser=release/'engines/browser/chromium-cft/chrome-win64/chrome.exe'
env={**os.environ,'OMNI_XHS_BROWSER':str(browser)}
owned=WindowsJob()
with tempfile.TemporaryDirectory(prefix='xhs-local-',dir=root/'dev/_state') as folder:
    p=subprocess.Popen([str(root/'dev/_build/xhsmcp/omni-browser-smoke.exe')],cwd=folder,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE);owned.add(p)
    out,err=p.communicate(timeout=60)
    if p.returncode:raise RuntimeError(err.decode('utf-8','replace'))
    assert b'"bundled_standard_chromium":true' in out
    print(out.decode('utf-8','replace'))
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    with (Path(folder)/'service.log').open('wb') as log:
        p=subprocess.Popen([str(release/'engines/xhsmcp/v2.5.5-omni/xiaohongshu-mcp.exe'),'-port','127.0.0.1:'+str(port)],cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT);owned.add(p)
        for _ in range(30):
            try:
                with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/health',timeout=2) as response:
                    assert response.status==200;break
            except OSError:time.sleep(.5)
        else:raise RuntimeError('XHS loopback health failed')
        p.terminate();p.wait(timeout=10)
print(json.dumps({'xhs_loopback_service':True,'standard_chromium_sandbox':True,'external_publications':0}))

owned.close()
