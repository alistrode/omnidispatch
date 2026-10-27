from __future__ import annotations
import time, uuid
from contextlib import contextmanager
from sqlalchemy import create_engine, event, String, Text, Float, Integer, JSON, Boolean, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

def uid(): return str(uuid.uuid4())
def now(): return time.time()
class Base(DeclarativeBase): pass
class Record(Base):
    __abstract__ = True
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    created: Mapped[float] = mapped_column(Float, default=now)
class Setting(Base):
    __tablename__='settings'
    key: Mapped[str] = mapped_column(String(100),primary_key=True)
    value: Mapped[dict] = mapped_column(JSON,default=dict)
class Admin(Record):
    __tablename__='admins'
    username: Mapped[str] = mapped_column(String(80),unique=True)
    password: Mapped[str] = mapped_column(Text)
    totp: Mapped[str|None] = mapped_column(Text,nullable=True)
class Session(Record):
    __tablename__='sessions'
    admin_id: Mapped[str] = mapped_column(String(36),index=True)
    token_hash: Mapped[str] = mapped_column(Text)
    csrf: Mapped[str] = mapped_column(String(100))
    expires: Mapped[float] = mapped_column(Float)
class Recovery(Record):
    __tablename__='recovery_codes'
    admin_id: Mapped[str] = mapped_column(String(36),index=True)
    code_hash: Mapped[str] = mapped_column(Text)
class LoginGuard(Base):
    __tablename__='login_guards'
    key: Mapped[str] = mapped_column(String(200),primary_key=True)
    failures: Mapped[int] = mapped_column(Integer,default=0)
    until: Mapped[float] = mapped_column(Float,default=0)
class Account(Record):
    __tablename__='accounts'
    label: Mapped[str] = mapped_column(String(120))
    platform: Mapped[str] = mapped_column(String(30),index=True)
    state: Mapped[str] = mapped_column(String(30),default='pending')
    cooldown_until: Mapped[float] = mapped_column(Float,default=0)
    canary_allowed: Mapped[bool] = mapped_column(Boolean,default=False)
    min_interval: Mapped[int] = mapped_column(Integer,default=60)
    last_publish: Mapped[float] = mapped_column(Float,default=0)
    egress: Mapped[dict] = mapped_column(JSON,default=lambda:{'mode':'direct'})
class Credential(Record):
    __tablename__='credentials'
    __table_args__=(UniqueConstraint('account_id','channel_id'),)
    account_id: Mapped[str] = mapped_column(String(36),index=True)
    channel_id: Mapped[str] = mapped_column(String(80))
    ciphertext: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(30),default='active')
class Channel(Base):
    __tablename__='channels'
    id: Mapped[str] = mapped_column(String(80),primary_key=True)
    engine: Mapped[str] = mapped_column(String(80))
    platform: Mapped[str] = mapped_column(String(30),index=True)
    version: Mapped[str] = mapped_column(String(120),default='unconfigured')
    priority: Mapped[int] = mapped_column(Integer,default=50)
    enabled: Mapped[bool] = mapped_column(Boolean,default=False)
    health: Mapped[str] = mapped_column(String(30),default='unverified')
    failures: Mapped[int] = mapped_column(Integer,default=0)
    open_until: Mapped[float] = mapped_column(Float,default=0)
    capabilities: Mapped[dict] = mapped_column(JSON,default=dict)
    evidence: Mapped[dict] = mapped_column(JSON,default=dict)
class Asset(Record):
    __tablename__='assets'
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(20))
    size: Mapped[int] = mapped_column(Integer)
    path: Mapped[str] = mapped_column(Text)
class AssetUpload(Record):
    __tablename__='asset_uploads'
    owner: Mapped[str] = mapped_column(String(36),index=True)
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(20))
    size: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String(20),default='open')
    lease_until: Mapped[float] = mapped_column(Float,default=0)
class Job(Record):
    __tablename__='jobs'
    key: Mapped[str] = mapped_column(String(120),unique=True)
    account_id: Mapped[str] = mapped_column(String(36),index=True)
    platform: Mapped[str] = mapped_column(String(30))
    payload: Mapped[dict] = mapped_column(JSON)
    state: Mapped[str] = mapped_column(String(30),default='queued',index=True)
    due: Mapped[float] = mapped_column(Float,default=now,index=True)
    generation: Mapped[int] = mapped_column(Integer,default=0)
    agent_id: Mapped[str|None] = mapped_column(String(36),nullable=True)
    lease_until: Mapped[float] = mapped_column(Float,default=0)
    channel_id: Mapped[str|None] = mapped_column(String(80),nullable=True)
    engine_version: Mapped[str|None] = mapped_column(String(120),nullable=True)
    remote_id: Mapped[str|None] = mapped_column(String(300),nullable=True)
    reason: Mapped[str] = mapped_column(Text,default='')
    tried: Mapped[list] = mapped_column(JSON,default=list)
class AccountLock(Base):
    __tablename__='account_locks'
    account_id: Mapped[str] = mapped_column(String(36),primary_key=True)
    job_id: Mapped[str] = mapped_column(String(36),unique=True)
class Attempt(Record):
    __tablename__='attempts'
    __table_args__=(UniqueConstraint('job_id','generation'),)
    job_id: Mapped[str] = mapped_column(String(36),index=True)
    generation: Mapped[int] = mapped_column(Integer)
    channel_id: Mapped[str] = mapped_column(String(80))
    version: Mapped[str] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(30),default='preparing')
    error_class: Mapped[str] = mapped_column(String(40),default='')
    finished: Mapped[float|None] = mapped_column(Float,nullable=True)
class Agent(Record):
    __tablename__='agents'
    label: Mapped[str] = mapped_column(String(120))
    token_hash: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean,default=True)
    last_seen: Mapped[float] = mapped_column(Float,default=0)
    capabilities: Mapped[dict] = mapped_column(JSON,default=dict)
class Audit(Record):
    __tablename__='audit'
    event: Mapped[str] = mapped_column(String(100),index=True)
    subject: Mapped[str] = mapped_column(String(120))
    detail: Mapped[dict] = mapped_column(JSON,default=dict)
class Update(Record):
    __tablename__='updates'
    __table_args__=(UniqueConstraint('engine','version'),)
    engine: Mapped[str] = mapped_column(String(80))
    version: Mapped[str] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(30),default='available')
    source: Mapped[str] = mapped_column(Text)
    data: Mapped[dict] = mapped_column(JSON,default=dict)
class Database:
    def __init__(self,url):
        self.engine=create_engine(url,connect_args={'check_same_thread':False,'timeout':30} if url.startswith('sqlite') else {},pool_pre_ping=True)
        if url.startswith('sqlite'):
            @event.listens_for(self.engine,'connect')
            def setup(dbapi,_):
                dbapi.execute('PRAGMA journal_mode=WAL'); dbapi.execute('PRAGMA foreign_keys=ON'); dbapi.execute('PRAGMA busy_timeout=30000')
        self.factory=sessionmaker(self.engine,expire_on_commit=False)
    def initialize(self):
        Base.metadata.create_all(self.engine)
        with self.tx() as s:
            v=s.get(Setting,'schema')
            if v and v.value.get('version')!=1: raise RuntimeError('Unsupported database schema; migration required')
            if not v:s.add(Setting(key='schema',value={'version':1}))
    @contextmanager
    def tx(self):
        with self.factory() as s:
            try:
                if self.engine.dialect.name=='sqlite':s.connection().exec_driver_sql('BEGIN IMMEDIATE')
                yield s
                s.commit()
            except BaseException:
                s.rollback();raise

def audit(s,event,subject,**detail):s.add(Audit(event=event,subject=subject,detail=detail))
