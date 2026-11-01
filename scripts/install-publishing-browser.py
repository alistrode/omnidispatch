"""Fetch the official Chrome for Testing archive using normal HTTPS."""
import hashlib,json,shutil,sys,urllib.request,zipfile
from pathlib import Path
root=Path(sys.argv[1]).resolve();cache=root/'dev'/'.runtime-cache'/'publishing-browser';cache.mkdir(parents=True,exist_ok=True)
url='https://storage.googleapis.com/chrome-for-testing-public/156.0.8078.4/win64/chrome-win64.zip'
archive=cache/'chrome-win64.zip'
if not archive.exists() or not zipfile.is_zipfile(archive):
    with urllib.request.urlopen(url,timeout=120) as r,archive.open('wb') as out:shutil.copyfileobj(r,out)
dest=root/'release'/'engines'/'browser'/'chromium-cft';dest.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(archive) as z:
    if z.testzip():raise ValueError('Browser archive is damaged')
    z.extractall(dest)
(dest/'BUILD.json').write_text(json.dumps({'source':url,'version':'156.0.8078.4','sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},indent=2))
print('Official publishing browser installed')
