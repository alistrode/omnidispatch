"""Offline publisher signing. Keep private key outside release/state and outside Git."""
import argparse,json,base64,time,os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PrivateFormat,PublicFormat,NoEncryption,load_pem_private_key
p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
k=sub.add_parser('keygen');k.add_argument('--directory',required=True)
s=sub.add_parser('sign');s.add_argument('--key',required=True);s.add_argument('--file',required=True)
f=sub.add_parser('feed');f.add_argument('--key',required=True);f.add_argument('--releases',required=True);f.add_argument('--output',required=True);f.add_argument('--generation',type=int,required=True)
a=p.parse_args()
if a.command=='keygen':
    root=Path(a.directory);root.mkdir(parents=True,exist_ok=True);private=root/'publisher.private.pem';public=root/'publisher.public.txt'
    if private.exists():raise SystemExit('Key already exists; refusing to replace trust root')
    key=Ed25519PrivateKey.generate();fd=os.open(private,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as file:file.write(key.private_bytes(Encoding.PEM,PrivateFormat.PKCS8,NoEncryption()))
    public.write_text(base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode());print('Publisher key generated; private key remains in the selected directory')
elif a.command=='sign':
    key=load_pem_private_key(Path(a.key).read_bytes(),password=None)
    destination=Path(a.file+'.signature');destination.write_text(base64.b64encode(key.sign(Path(a.file).read_bytes())).decode());print('Signature:',destination)
else:
    key=load_pem_private_key(Path(a.key).read_bytes(),password=None)
    payload=json.dumps({'generation':a.generation,'expires':time.time()+7*86400,'releases':json.loads(Path(a.releases).read_text())},separators=(',',':')).encode()
    Path(a.output).write_text(json.dumps({'payload':base64.b64encode(payload).decode(),'signature':base64.b64encode(key.sign(payload)).decode()}));print('Signed publisher feed written')
