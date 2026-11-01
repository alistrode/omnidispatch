"""Translate bounded publishing intents to the reviewed social-auto-upload CLI."""
import json,os,subprocess
from pathlib import Path
from .adapters import PreflightError,safe_write
from .platform_specs import allowed_url
PLATFORMS={'douyin','kuaishou','xiaohongshu','tencent','baijiahao','weibo','youtube','zhihu'}
ALLOWED={'tags','category','video_mark','originality','visibility','tid','collection'}
def validate(adapter):
    j=adapter.job;p=adapter.payload;platform=j['platform'];opts=p.get('options',{})
    if platform not in PLATFORMS:raise PreflightError('engine_incompatible','此社区引擎尚未接入该平台')
    if p.get('action','publish')!='publish':raise PreflightError('engine_incompatible','此引擎不支持评论，请选桌面评论通道')
    platform_allowed=({'visibility'} if platform=='youtube' else set()) | ({'category','video_mark','originality'} if platform=='zhihu' and p['kind']=='video' else set()) | ({'tags','collection'} if platform in {'douyin','tencent','baijiahao'} else {'tags'} if platform!='zhihu' else set())
    if set(opts)-platform_allowed:raise PreflightError('invalid_input','此社区引擎不支持所选参数')
    if p['kind']=='text' and platform!='zhihu':raise PreflightError('invalid_input','此引擎的文字发布当前只接入知乎')
    if p['kind']=='images':raise PreflightError('invalid_input','此版本社区通道先使用单视频或知乎文章；图文请选择桌面通道')
    if p['kind']=='video' and len(adapter.files)!=1:raise PreflightError('invalid_input','请选择一个视频素材')
    if not adapter.credential.get('browser_state') or adapter.credential.get('account_alias')!=j['account_id']:raise PreflightError('auth_expired','请在该通道绑定此账号的浏览器登录态')
    if platform=='zhihu':
        if not adapter.credential.get('upstream_identity'):raise PreflightError('auth_expired','请重新登录，保存社区引擎要求的知乎页头身份')
        if p['kind']=='video' and not all(opts.get(x) for x in ('category','video_mark','originality')):raise PreflightError('invalid_input','知乎视频必须填写 category、video_mark、originality')

def publish(adapter):
    validate(adapter);work=adapter.work;platform=adapter.job['platform'];payload=adapter.payload;opts=payload.get('options',{})
    folder=work/'cookies';folder.mkdir(exist_ok=True);cookie=folder/(platform+'_'+adapter.job['account_id']+'.json')
    safe_write(cookie,adapter.credential['browser_state'])
    if adapter.credential.get('upstream_identity'):safe_write(cookie.with_suffix('.identity.json'),adapter.credential['upstream_identity'])
    args=[platform,'upload-article' if payload['kind']=='text' else 'upload-video','--account',adapter.job['account_id'],'--title',payload['title']]
    if payload['kind']=='text':
        body=work/'article.txt';body.write_text(payload.get('description') or payload['title'],encoding='utf-8');args+=['--content-file',str(body)]
    else:args+=['--file',str(adapter.files[0]),'--desc',payload.get('description','')]
    mapping={'tags':'--tags','category':'--category','video_mark':'--video-mark','originality':'--originality','visibility':'--visibility','collection':'--collection'}
    for key,value in opts.items():
        if key not in mapping:raise PreflightError('invalid_input','此通道没有实现该参数')
        args.extend([mapping[key],','.join(value) if isinstance(value,list) else str(value)])
    args+=['--headless']
    root=Path(__file__).resolve().parent.parent;browsers=list((root/'engines'/'browser').rglob('chrome.exe'))
    if not browsers:raise PreflightError('engine_missing','缺少内置浏览器')
    env={**os.environ,'OMNI_SAU_WORK':str(work),'OMNI_BROWSER_PATH':str(browsers[0]),'PYTHONUTF8':'1'}
    output=work/'upstream.private.log'
    with output.open('wb') as log:
        child=subprocess.Popen([*adapter.cfg['argv'],*args],cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,shell=False)
        try:child.wait(timeout=1200)
        except BaseException:child.kill();child.wait();raise
    # Only the community engine's structured publication evidence can succeed.
    for path in folder.rglob('*.json'):
        if path==cookie or path.name.endswith('.identity.json'):continue
        try:result=json.loads(path.read_text(encoding='utf-8'))
        except (ValueError,UnicodeError):continue
        url=result.get('url') or result.get('post_url')
        if result.get('success') is True and result.get('status')=='published' and url and allowed_url(platform,url):return {'ok':True,'remote_id':url}
    return {'ok':False,'error_class':'unknown'}
