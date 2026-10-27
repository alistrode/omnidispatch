"""Install only pinned upstream assets. No latest URLs and no downloaded install scripts."""
import json,sys,zipfile,shutil,subprocess,tempfile,os
from pathlib import Path,PurePosixPath
from urllib.parse import urlsplit
import httpx
root=Path(__file__).resolve().parent.parent
lock=json.loads((root/'engines.lock.json').read_text())
destination=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root/'engines'
destination.mkdir(parents=True,exist_ok=True)
results=[]
for entry in lock['installable_windows']:
    target=destination/entry['engine']/entry['version']
    binary=target/entry['binary']
    if binary.exists():results.append({'engine':entry['engine'],'state':'present','version':entry['version']});continue
    target.mkdir(parents=True,exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(dir=destination) as temp:
            asset=Path(temp)/'asset'
            parsed=urlsplit(entry['url'])
            if parsed.scheme!='https' or parsed.hostname not in {'github.com','registry.npmjs.org'}:raise ValueError('Untrusted source')
            with httpx.Client(timeout=120,follow_redirects=True) as client,client.stream('GET',entry['url']) as response:
                response.raise_for_status();size=0
                with asset.open('wb') as f:
                    for chunk in response.iter_bytes(1024*1024):
                        size+=len(chunk)
                        if size>200*1024**2:raise ValueError('Asset exceeds limit')
                        f.write(chunk)
            if entry.get('size') and size!=entry['size']:raise ValueError('Size mismatch')
            if entry.get('archive')=='zip':
                with zipfile.ZipFile(asset) as z:
                    members=[m for m in z.namelist() if PurePosixPath(m).name==entry['binary']]
                    if len(members)!=1:raise ValueError('Binary ambiguous or missing')
                    with z.open(members[0]) as src,binary.open('xb') as dst:shutil.copyfileobj(src,dst)
            elif entry.get('archive')=='tgz':
                import tarfile
                with tarfile.open(asset) as t:
                    members=[m for m in t.getmembers() if PurePosixPath(m.name).name==entry['binary'] and m.isfile()]
                    if len(members)!=1:raise ValueError('Binary ambiguous or missing')
                    with t.extractfile(members[0]) as src,binary.open('xb') as dst:shutil.copyfileobj(src,dst)
            else:shutil.copy2(asset,binary)
            # Read-only preflight; it does not establish platform/account readiness.
            p=subprocess.run([str(binary),*entry.get('help_args',['--help'])],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30,shell=False)
            results.append({'engine':entry['engine'],'state':'installed' if p.returncode==0 else 'installed_check_failed','version':entry['version'],'check_exit':p.returncode,'trust':'upstream_https_unsigned'})
    except Exception as e:results.append({'engine':entry['engine'],'state':'failed','error':type(e).__name__,'version':entry['version']})
(destination/'installation-report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False))
