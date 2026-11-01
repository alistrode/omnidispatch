"""Explicit upstream interfaces. No arbitrary remote command templates or shell execution."""
from __future__ import annotations
import json,os,re,subprocess,tempfile,shutil
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import httpx
class PreflightError(Exception):
    def __init__(self,kind,message):self.kind=kind;super().__init__(message)
def safe_write(path,value):
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False)
def executable(cfg):
    argv=cfg.get('argv',[])
    if not isinstance(argv,list) or not argv or not all(isinstance(x,str) for x in argv):raise PreflightError('engine_missing','未配置固定引擎 argv')
    if not Path(argv[0]).is_file() and not shutil.which(argv[0]):raise PreflightError('engine_missing','找不到引擎程序')
    return argv

def check(cfg):
    try:
        if cfg.get('adapter')=='desktopweb':return {'ready':bool(cfg.get('argv') and Path(cfg['argv'][0]).is_file()),'note':'本机桌面填写与确认，不表示自动发布已验证'}
        if cfg.get('adapter')=='xapi':return {'ready':True,'note':'官方 HTTP API；账号授权独立校验'}
        if cfg.get('adapter') in {'xhsmcp','postiz'}:
            url=cfg.get('endpoint','');parsed=urlsplit(url)
            if parsed.scheme not in {'http','https'} or parsed.username or parsed.password:raise ValueError('非法端点')
            if parsed.scheme=='http' and parsed.hostname not in {'localhost','127.0.0.1','::1'}:raise ValueError('远端引擎必须 HTTPS')
            response=httpx.get(url.rstrip('/')+('/api/v1/login/status' if cfg['adapter']=='xhsmcp' else '/public/v1/integrations'),timeout=10,follow_redirects=False)
            return {'ready':response.status_code==200 and (cfg['adapter']!='xhsmcp' or response.json().get('success') is True),'note':'服务已响应；登录和真实发布单独核验'}
        argv=executable(cfg)
        if cfg.get('adapter')=='spreado':
            probe=subprocess.run([*argv,'list'],capture_output=True,timeout=15,shell=False,cwd=cfg.get('cwd'))
            output=(probe.stdout+probe.stderr).decode('utf-8','replace')
            if probe.returncode or not re.search(r'(xiaohongshu|shipinhao|tencent|小红书|视频号)',output,re.I):
                return {'ready':False,'note':'未发现已安装的平台适配器'}
        result=subprocess.run([*argv,'--help'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15,shell=False)
        return {'ready':result.returncode==0,'note':'只读帮助检查'}
    except Exception as e:return {'ready':False,'note':type(e).__name__}

class Adapter:
    def __init__(self,cfg,job,files,work):self.cfg=cfg;self.job=job;self.files=files;self.work=Path(work);self.payload=job['payload'];self.credential=job['credential']
    def preflight(self):
        adapter=self.cfg['adapter'];opts=self.payload.get('options',{})
        action=self.payload.get('action','publish')
        if action!='publish' and adapter not in {'xapi','xhsmcp'}:raise PreflightError('invalid_input','此引擎不能发表评论，请选择评论通道')
        allowed={'xapi':set(),'xhsmcp':{'topics','tags','xsec_token','target_user_id'},'ytuploader':{'visibility','tags','categoryId','madeForKids'},'biliup':{'tid','tags','copyright'},'sau':{'tags','category','video_mark','originality','visibility','tid','collection'},'spreado':{'tags'},'matrixmedia':{'phone','tags','short_title'},'postiz':{'integration_id'}}.get(adapter,set())
        if set(opts)-allowed:raise PreflightError('invalid_input','此通道未实现所选参数，拒绝静默丢失')
        if self.job['egress'].get('mode','direct')!='direct':
            # Until each adapter's whole subprocess/browser path is verified, fail closed.
            if adapter not in {'xapi','biliup'}:raise PreflightError('egress_unavailable','此适配器尚未验证完整代理链路')
            if not self.job['egress'].get('proxy'):raise PreflightError('egress_unavailable','缺少指定代理')
        if self.job['engine_version']!=self.cfg.get('version'):raise PreflightError('engine_incompatible','任务固定版本与本机配置不符')
        if adapter=='xapi':
            if self.payload['kind']!='text':raise PreflightError('invalid_input','X API 初版仅接受纯文本')
            if action!='publish':
                from .platform_specs import allowed_url
                target=self.payload.get('target_url','')
                match=re.search(r'/status/(\d+)',urlsplit(target).path)
                if not allowed_url('x',target) or not match:raise PreflightError('invalid_input','需提供 X 原帖的完整状态链接')
                self.reply_to=self.payload.get('target_comment_id') if action=='reply' else match.group(1)
                if not str(self.reply_to).isdigit():raise PreflightError('invalid_input','X 回复目标须为实际帖子 ID')
            if not self.credential.get('access_token') or not self.credential.get('user_id'):raise PreflightError('auth_expired','需用户 OAuth access_token 和预期 user_id')
            proxy=self.job['egress'].get('proxy')
            with httpx.Client(timeout=30,proxy=proxy,trust_env=not bool(proxy)) as client:
                identity=client.get('https://api.x.com/2/users/me',headers={'Authorization':'Bearer '+self.credential['access_token']})
            if identity.status_code!=200 or str(identity.json().get('data',{}).get('id'))!=str(self.credential['user_id']):raise PreflightError('auth_expired','实际 X 账号与固定授权身份不符或权限不足')
        elif adapter=='xhsmcp':
            if not self.payload.get('description','').strip():raise PreflightError('invalid_input','小红书正文不能为空')
            if action=='publish' and (self.payload['kind'] not in {'images','video'} or not self.files):raise PreflightError('invalid_input','小红书需要图片或单个视频')
            if self.payload['kind']=='video' and len(self.files)!=1:raise PreflightError('invalid_input','仅接受单视频')
            if not self.credential.get('instance_account'):raise PreflightError('auth_expired','需绑定独立 xhs-mcp 实例的账号标识')
            if self.credential.get('instance_account')!=self.cfg.get('instance_account'):raise PreflightError('auth_expired','xhs-mcp 实例账号不匹配')
            try:
                status=httpx.get(self.cfg['endpoint'].rstrip('/')+'/api/v1/login/status',timeout=30,trust_env=False)
                identity=status.json().get('data',{})
                if status.status_code!=200 or not identity.get('is_logged_in') or not self.credential.get('platform_user_id') or str(identity.get('user_id'))!=str(self.credential['platform_user_id']):raise PreflightError('auth_expired','小红书实际账号身份与绑定身份不符，请重新授权')
            except httpx.HTTPError:raise PreflightError('engine_missing','账号专属小红书服务不可达')
            if action!='publish':
                from .platform_specs import allowed_url
                target=self.payload.get('target_url','');parsed=urlsplit(target)
                match=re.search(r'/(?:explore|discovery/item)/(\w+)',parsed.path)
                if not allowed_url('xiaohongshu',target) or not match:raise PreflightError('invalid_input','需提供小红书笔记完整链接')
                token=opts.get('xsec_token') or parse_qs(parsed.query).get('xsec_token',[''])[0]
                if not token:raise PreflightError('invalid_input','原帖链接须包含有效 xsec_token')
                self.comment_body={'feed_id':match.group(1),'xsec_token':token,'content':self.payload['description']}
                if action=='reply':
                    if not self.payload.get('target_comment_id') or not opts.get('target_user_id'):raise PreflightError('invalid_input','回复须指定评论 ID 和 target_user_id')
                    self.comment_body.update(comment_id=self.payload['target_comment_id'],user_id=opts['target_user_id'])
            if action=='publish' and len(self.payload['title'])>20:raise PreflightError('invalid_input','小红书标题超过 20 字')
        elif adapter in {'sau','spreado','biliup','ytuploader','matrixmedia'}:
            executable(self.cfg)
            if adapter!='sau' and (self.payload['kind']!='video' or len(self.files)!=1):raise PreflightError('invalid_input','此 CLI 适配器只接受单视频')
            if adapter=='sau':
                from .sau_adapter import validate
                validate(self)
            elif adapter=='spreado' and not self.credential.get('cookies'):raise PreflightError('auth_expired','缺少独立 Cookie 状态')
            elif adapter=='biliup':
                if not self.cfg.get('usage_acknowledged'):raise PreflightError('engine_incompatible','需先确认上游用途限制')
                if not opts.get('tid'):raise PreflightError('invalid_input','B站分区 tid 为必填')
                if not self.credential.get('cookies'):raise PreflightError('auth_expired','缺少 B站 Cookie')
            elif adapter=='ytuploader':
                if not all(k in self.credential for k in ('client_secrets','token','channel_id')):raise PreflightError('auth_expired','缺少 YouTube OAuth 配置、令牌或预期频道 ID')
                token=self.credential['token'];secrets=self.credential['client_secrets'];oauth=secrets.get('installed',secrets.get('web',{}))
                with httpx.Client(timeout=30) as client:
                    refreshed=client.post('https://oauth2.googleapis.com/token',data={'client_id':oauth.get('client_id'),'client_secret':oauth.get('client_secret'),'refresh_token':token.get('refresh_token'),'grant_type':'refresh_token'})
                    if refreshed.status_code!=200:raise PreflightError('auth_expired','YouTube OAuth 刷新失败')
                    identity=client.get('https://www.googleapis.com/youtube/v3/channels',params={'part':'id','mine':'true'},headers={'Authorization':'Bearer '+refreshed.json()['access_token']})
                if identity.status_code!=200 or self.credential['channel_id'] not in [x['id'] for x in identity.json().get('items',[])]:raise PreflightError('auth_expired','实际 YouTube 频道与固定授权身份不符')
                if opts.get('visibility','private') not in {'private','unlisted','public'}:raise PreflightError('invalid_input','无效可见性')
            elif adapter=='matrixmedia':
                if self.credential.get('phone')!=opts.get('phone') or not opts.get('phone'):raise PreflightError('auth_expired','MatrixMedia 账号分组不匹配')
        elif adapter=='postiz':
            if not self.credential.get('api_key') or not opts.get('integration_id'):raise PreflightError('auth_expired','需配置 Postiz API key 与固定 integration ID')
            raise PreflightError('engine_incompatible','Postiz 上传/发布协议需按部署版本核验，尚未启用写入')
        else:raise PreflightError('engine_missing','适配器尚未实现')
        if self.payload['kind']=='video':
            ffprobe=self.cfg.get('ffprobe') or shutil.which('ffprobe')
            if not ffprobe:raise PreflightError('engine_missing','缺少 ffprobe；视频格式检查不跳过')
            p=subprocess.run([ffprobe,'-v','error','-show_entries','format=duration','-of','json',str(self.files[0])],capture_output=True,timeout=30,shell=False)
            try:
                if p.returncode or float(json.loads(p.stdout)['format']['duration'])<=0:raise ValueError()
            except Exception:raise PreflightError('invalid_input','视频无法解析或无有效时长')
    def publish(self):
        adapter=self.cfg['adapter'];opts=self.payload.get('options',{})
        if adapter=='sau':
            from .sau_adapter import publish
            return publish(self)
        if adapter=='xapi':
            replying=self.payload.get('action','publish')!='publish'
            text=self.payload['description'] if replying else self.payload['title']+ ('\n'+self.payload['description'] if self.payload.get('description') else '')
            body={'text':text}
            if replying:body['reply']={'in_reply_to_tweet_id':str(self.reply_to)}
            proxy=self.job['egress'].get('proxy')
            with httpx.Client(timeout=60,proxy=proxy,trust_env=not bool(proxy)) as client:
                r=client.post('https://api.x.com/2/tweets',headers={'Authorization':'Bearer '+self.credential['access_token']},json=body)
            if r.status_code in {401,403,429,400}:return {'ok':False,'error_class':{401:'auth_expired',403:'risk_control',429:'rate_limited',400:'invalid_input'}[r.status_code],'definitely_not_submitted':True}
            r.raise_for_status();remote=r.json().get('data',{}).get('id');return {'ok':bool(remote),'remote_id':remote}
        if adapter=='xhsmcp' and self.payload.get('action','publish')!='publish':
            path='/api/v1/feeds/comment/reply' if self.payload['action']=='reply' else '/api/v1/feeds/comment'
            with httpx.Client(timeout=180,trust_env=False) as client:response=client.post(self.cfg['endpoint'].rstrip('/')+path,json=self.comment_body)
            response.raise_for_status();data=response.json().get('data',{});identifier=data.get('comment_id')
            return {'ok':bool(identifier),'remote_id':identifier,'error_class':'unknown'}
        if adapter=='xhsmcp':
            body={'title':self.payload['title'],'content':self.payload.get('description',''),'tags':opts.get('topics',opts.get('tags',[]))}
            if self.payload['kind']=='images':body['images']=[str(f) for f in self.files];path='/api/v1/publish'
            else:body['video']=str(self.files[0]);path='/api/v1/publish_video'
            # Shared local filesystem is required; endpoint must point to this Agent's dedicated process.
            with httpx.Client(timeout=1200,trust_env=False) as client:r=client.post(self.cfg['endpoint'].rstrip('/')+path,json=body)
            r.raise_for_status();data=r.json().get('data',{});remote=data.get('post_id') or data.get('note_id')
            return {'ok':bool(remote),'remote_id':remote}
        argv=executable(self.cfg);cwd=self.cfg.get('cwd') or str(self.work)
        title=self.payload['title'];desc=self.payload.get('description','');video=str(self.files[0]);remote=None
        if adapter=='sau':
            args=[self.job['platform'],'upload-video','--account',self.job['account_id'],'--file',video,'--title',title,'--desc',desc]
            for key,value in opts.items():args.extend(['--'+key,str(','.join(value) if isinstance(value,list) else value)])
        elif adapter=='spreado':
            cookie=self.work/'cookies.json';safe_write(cookie,self.credential['cookies'])
            args=['upload','shipinhao' if self.job['platform']=='tencent' else self.job['platform'],'--video',video,'--title',title,'--content',desc,'--cookies',str(cookie)]
            if opts.get('tags'):args+=['--tags',','.join(opts['tags'])]
        elif adapter=='biliup':
            cookie=self.work/'cookies.json';safe_write(cookie,self.credential['cookies'])
            args=['-u',str(cookie)]
            if self.job['egress'].get('proxy'):args+=['--proxy',self.job['egress']['proxy']]
            args+=['upload','--title',title,'--desc',desc,'--tid',str(opts['tid']),'--tag',','.join(opts.get('tags',[])),'--copyright',str(opts.get('copyright',1)),video]
        elif adapter=='ytuploader':
            token=self.work/'request.token';secret=self.work/'client_secrets.json';out=self.work/'result.json'
            safe_write(token,self.credential['token']);safe_write(secret,self.credential['client_secrets'])
            args=['-filename',video,'-title',title,'-description',desc,'-cache',str(token),'-secrets',str(secret),'-metaJSONout',str(out),'-privacy',opts.get('visibility','private'),'-quiet']
            meta=self.work/'meta.json';safe_write(meta,{k:v for k,v in opts.items() if k in {'categoryId','madeForKids'}});args+=['-metaJSON',str(meta)]
            if opts.get('tags'):args+=['-tags',','.join(opts['tags'])]
        elif adapter=='matrixmedia':
            aliases={'bilibili':'blbl','xiaohongshu':'xhs','tencent':'sph'}
            args=['cli','publish','-p',aliases[self.job['platform']],'--phone',opts['phone'],'-f',video,'-t',title,'--description',desc]
            if opts.get('tags'):args+=['--tags',' '.join('#'+t.lstrip('#') for t in opts['tags'])]
            if opts.get('short_title'):args+=['--short-title',opts['short_title']]
        else:raise RuntimeError('Adapter not implemented')
        # Logs can contain credentials. Retain only bounded output in ephemeral private directory.
        output=self.work/'engine-output.private'
        with output.open('wb') as f:
            process=subprocess.Popen([*argv,*args],cwd=cwd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,shell=False)
            try:process.wait(timeout=1200)
            except BaseException:
                process.kill();process.wait();raise
        if adapter=='biliup' and process.returncode==0:
            with output.open('rb') as stream:
                stream.seek(max(0,output.stat().st_size-1024*1024))
                text=stream.read().decode('utf-8','replace')
            matches=re.findall(r'''["']?bvid["']?\s*[:=]\s*["']?(BV[0-9A-Za-z]{10})''',text)
            if matches:remote=matches[-1]
        if adapter=='ytuploader' and process.returncode==0 and out.exists():
            data=json.loads(out.read_text());remote=data.get('id')
        # Human-readable CLI "success" is not sufficient evidence of remote publication.
        return {'ok':bool(remote),'remote_id':remote,'error_class':'unknown'}
