import argparse,json,os,sys,secrets,logging,sqlite3,datetime
from pathlib import Path
from sqlalchemy import select,delete
from .db import Database,Admin,Agent,Session,Recovery,audit
from .security import ph,new_token,Vault

def main():
    p=argparse.ArgumentParser(prog='omnidispatch');p.add_argument('--state',default=os.getenv('OMNI_STATE','state'))
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('init');serve=sub.add_parser('serve');serve.add_argument('--host',default='127.0.0.1');serve.add_argument('--port',type=int,default=8791)
    agent=sub.add_parser('agent');agent.add_argument('--config',required=True);agent.add_argument('--once',action='store_true')
    sub.add_parser('backup');sub.add_parser('reset-admin');sub.add_parser('status');reg=sub.add_parser('register-agent');reg.add_argument('--label',default='本机 Windows 节点');reg.add_argument('--hub',default='http://127.0.0.1:8791')
    args=p.parse_args();state=Path(args.state).resolve();state.mkdir(parents=True,exist_ok=True)
    if args.command=='agent':
        from .agent import AgentRunner
        logging.basicConfig(level=logging.INFO);AgentRunner(args.config).run(args.once);return
    url=os.getenv('OMNI_DATABASE_URL',f'sqlite:///{state / "hub.db"}');db=Database(url);db.initialize();Vault(state)
    if args.command in {'init','reset-admin'}:
        secret=new_token()
        with db.tx() as s:
            admin=s.scalar(select(Admin))
            if args.command=='init' and admin:print('Already initialized; credentials unchanged.');return
            if not admin:admin=Admin(username='admin',password='');s.add(admin)
            admin.password=ph.hash(secret)
            if args.command=='reset-admin':admin.totp=None;s.execute(delete(Session));s.execute(delete(Recovery))
            audit(s,'auth.local_initialization',admin.username)
        credentials=state/'ADMIN-CREDENTIALS.private.txt'
        # Explicit local initialization; never print credential values to logs.
        credentials.write_text('OmniDispatch\n用户名: admin\n初始密码: '+secret+'\n登录后请修改密码。\n',encoding='utf-8');os.chmod(credentials,0o600)
        print('Initialized. Credentials stored in local private file:',credentials)
    elif args.command=='register-agent':
        target=state/'agent.json'
        if target.exists():print('Agent config exists; authorization unchanged.');return
        secret=new_token()
        with db.tx() as s:
            agent=Agent(label=args.label,token_hash=ph.hash(secret));s.add(agent);s.flush();token=agent.id+'.'+secret;audit(s,'agent.local_registered',agent.id)
        target.write_text(json.dumps({'hub':args.hub,'token':token,'work':str(state/'agent-jobs'),'channels':{}},ensure_ascii=False,indent=2),encoding='utf-8');os.chmod(target,0o600);print('Agent registered:',target)
    elif args.command=='serve':
        import uvicorn
        from .app import create_app
        uvicorn.run(create_app(state),host=args.host,port=args.port,proxy_headers=True,forwarded_allow_ips="127.0.0.1")
    elif args.command=='backup':
        if db.engine.dialect.name!='sqlite':raise SystemExit('PostgreSQL: use pg_dump and encrypted external backup storage')
        folder=state.parent/'backups';folder.mkdir(exist_ok=True);target=folder/('hub-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.sqlite3')
        with sqlite3.connect(state/'hub.db') as source,sqlite3.connect(target) as dest:
            source.backup(dest)
            if dest.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('Backup integrity check failed')
        os.chmod(target,0o600);print('Database backup verified:',target,'; vault.key must be backed up separately')
    elif args.command=='status':
        with db.tx() as s:print(json.dumps({'initialized':s.scalar(select(Admin)) is not None,'agents':len(s.scalars(select(Agent)).all()),'database':db.engine.dialect.name}))
if __name__=='__main__':main()
