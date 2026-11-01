"""Build a clean local ZIP; never distribute runtime state, tokens, cookies or raw logs."""
import hashlib,json,sys,zipfile
from pathlib import Path
root=Path(sys.argv[1]).resolve();output=root/'OmniDispatch-Desktop-Windows-x64.zip'
excluded={'state','logs','__pycache__','.git','examples','tests','scripts'}
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for file in root.rglob('*'):
        rel=file.relative_to(root)
        if not file.is_file() or file==output or any(part in excluded for part in rel.parts) or file.suffix.lower() in {'.pyc','.log'} or (len(rel.parts)==1 and file.suffix.lower() in {'.zip','.sha256'}) or file.name.endswith('.private.txt'):continue
        if rel.parts[:2]==('engines','browser') and len(rel.parts)>2 and rel.parts[2]!='chromium-cft':continue
        if 'desktop' in rel.parts and ('vendor' in rel.parts or file.suffix.lower() in {'.cs','.ps1'}):continue
        if rel.parts[:2]==('engines','xhsmcp') and len(rel.parts)>2 and rel.parts[2]!='v2.5.5-omni':continue
        z.write(file,'OmniDispatch/'+rel.as_posix())
with zipfile.ZipFile(output) as z:
    names=z.namelist()
    for required in ['OmniDispatch.exe','runtime/python.exe','runtime/python314.zip','desktop/webview2-runtime/msedgewebview2.exe','WebView2Loader.dll','omnidispatch/app.py','Start.cmd','engines/sau/runtime/python.exe','engines/sau/runtime/python312.zip','engines/browser/chromium-cft/chrome-win64/chrome.exe']:
        assert 'OmniDispatch/'+required in names,required
    for binary in ['xiaohongshu-mcp.exe','xiaohongshu-login.exe','omni-browser-smoke.exe']:
        assert 'OmniDispatch/engines/xhsmcp/v2.5.5-omni/'+binary in names,binary
    assert not any('/state/' in n or '/logs/' in n or 'cookies.json' in n for n in names)
    assert z.testzip() is None
hash=hashlib.sha256(output.read_bytes()).hexdigest()
(output.with_suffix('.sha256')).write_text(hash+'  '+output.name+'\n')
print(json.dumps({'archive':str(output),'bytes':output.stat().st_size,'files':len(names),'sha256':hash,'state_included':False}))
