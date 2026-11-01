"""Install the locally source-built standard-Chromium XHS fork, verifying pinned digests."""
import hashlib,json,shutil,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve();source=root/'dev'/'vendor'/'xhsmcp';build=root/'dev'/'_build'/'xhsmcp';target=root/'release'/'engines'/'xhsmcp'/'v2.5.5-omni'
meta=json.loads((source/'BUILD.json').read_text());target.mkdir(parents=True,exist_ok=True)
for name,expected in meta['binary_sha256'].items():
    file=build/name
    if hashlib.sha256(file.read_bytes()).hexdigest()!=expected:raise ValueError('Engine binary checksum mismatch')
    shutil.copy2(file,target/name)
shutil.copytree(source,target/'source',dirs_exist_ok=True);shutil.copy2(source/'BUILD.json',target/'BUILD.json');shutil.copy2(source/'LICENSE',target/'LICENSE')
print('Source-built XHS engine installed; uses bundled standard Chromium; no browser download')
