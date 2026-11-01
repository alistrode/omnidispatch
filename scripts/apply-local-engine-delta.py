"""Apply a checksum-bound BSDIFF40 update to our own local build artifacts only."""
import bz2,hashlib,json,os,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve();build=root/'dev/_build/xhsmcp';patches=root/'dev/_build/xhs-delta'
def digest(b):return hashlib.sha256(b).hexdigest()
def number(b):
    if len(b)!=8:raise ValueError('Truncated offset')
    value=int.from_bytes(b,'little')&0x7fffffffffffffff
    return -value if b[7]&128 else value
for name,record in json.loads((patches/'manifest.json').read_text()).items():
    if Path(name).name!=name or not name.endswith('.exe'):raise ValueError('Invalid artifact')
    target=build/name;old=target.read_bytes()
    if digest(old)==record['new']:continue
    if digest(old)!=record['old']:raise ValueError('Existing build checksum mismatch')
    patch=(patches/(name+'.bsdiff')).read_bytes()
    if digest(patch)!=record['patch'] or patch[:8]!=b'BSDIFF40':raise ValueError('Patch mismatch')
    c,d,size=(number(patch[n:n+8]) for n in [8,16,24])
    if min(c,d,size)<0 or size>100*1024**2:raise ValueError('Invalid patch size')
    control=bz2.decompress(patch[32:32+c]);diff=bz2.decompress(patch[32+c:32+c+d]);extra=bz2.decompress(patch[32+c+d:])
    new=bytearray();oldpos=ci=di=ei=0
    while len(new)<size:
        x,y,z=(number(control[ci+n:ci+n+8]) for n in [0,8,16]);ci+=24
        if x<0 or y<0 or len(new)+x+y>size or di+x>len(diff) or ei+y>len(extra):raise ValueError('Invalid patch span')
        new.extend(((diff[di+i]+(old[oldpos+i] if 0<=oldpos+i<len(old) else 0))&255) for i in range(x));di+=x;oldpos+=x
        new.extend(extra[ei:ei+y]);ei+=y;oldpos+=z
    if digest(new)!=record['new']:raise ValueError('Updated binary checksum mismatch')
    temporary=target.with_suffix('.updated');temporary.write_bytes(new);os.replace(temporary,target)
    print(json.dumps({'updated_local_build':name,'sha256':record['new']}))
