"""Local visible browser workflows. Website submission remains an explicit desktop action."""
import argparse,json,os,secrets,tempfile,threading,time
from pathlib import Path
import httpx
from .platform_specs import PLATFORM_SPECS,allowed_url,destination,cookie_domain_allowed

class LocalAPI:
    def __init__(self):
        self.client=httpx.Client(base_url='http://127.0.0.1:8791',timeout=60,trust_env=False)
        r=self.client.post('/api/bootstrap');r.raise_for_status();self.client.headers['X-CSRF-Token']=r.json()['csrf']
    def request(self,path,body=None):
        r=self.client.get(path) if body is None else self.client.post(path,json=body);r.raise_for_status();return r.json()
    def close(self):self.client.close()

def browser_binary(root):
    preferred=Path(root)/'engines'/'browser'/'chromium-cft'/'chrome-win64'/'chrome.exe'
    if preferred.is_file():return preferred
    matches=list((Path(root)/'engines'/'browser').rglob('chrome.exe'))
    if not matches:raise ValueError('缺少随包提供的本机浏览器')
    return matches[0]

def filter_state(platform,state):
    hosts=PLATFORM_SPECS[platform]['hosts']
    return {'cookies':[c for c in state.get('cookies',[]) if cookie_domain_allowed(platform,c.get('domain',''))],
            'origins':[o for o in state.get('origins',[]) if allowed_url(platform,o.get('origin',''))]}

PANEL_JS=r'''({name,title,body,login,identity,action,target,metadata})=>{
const old=document.getElementById('__omni_panel');if(old)old.remove();
const box=document.createElement('aside');box.id='__omni_panel';box.style.cssText='position:fixed;right:18px;bottom:18px;width:340px;padding:18px;background:#fff9f5;color:#2b1a17;box-shadow:0 8px 40px #2b1a1733;border-radius:14px;z-index:2147483647;font:13px/1.6 system-ui';
const h=document.createElement('strong');h.textContent=login?'OmniDispatch · 绑定本机账号':'OmniDispatch · '+({'publish':'发布内容','comment':'评论原帖','reply':'回复指定评论'}[action]||action);box.append(h);
const info=document.createElement('p');info.textContent=login?'请先在此网站完成登录，再填写固定的平台账号 ID 或个人主页链接。':'网页由你确认提交。可先点网页中的目标输入框，再填入正文。不会自动点击发布。'+(target?' 目标：'+target:'');box.append(info);
if(metadata&&Object.keys(metadata).length){const details=document.createElement('details');const summary=document.createElement('summary');summary.textContent='本任务参数（在网页对应项确认）';const pre=document.createElement('pre');pre.style.cssText='max-height:100px;overflow:auto;white-space:pre-wrap';pre.textContent=JSON.stringify(metadata,null,2);details.append(summary,pre);box.append(details);}
const identityInput=document.createElement('input');identityInput.value=identity||'';identityInput.placeholder=login?'固定的平台用户 ID / 个人主页链接':'发布后的作品或草稿 HTTPS 链接';identityInput.style.cssText='width:100%;box-sizing:border-box;margin:6px 0;padding:8px';box.append(identityInput);
const msg=document.createElement('div');msg.style.cssText='max-height:70px;overflow:auto;color:#a65050';
const invoke=async(type)=>{try{const result=await window[name]({type,value:identityInput.value});msg.textContent=result&&result.message||'';}catch(e){msg.textContent=String(e.message||e);}};
for(const [type,label] of (login?[['save_login','保存此账号登录态']]:[['fill_title','填入标题'],['fill_body','填入正文'],['upload','填入本任务素材'],['show_assets','打开任务素材目录'],['published','已发布 · 记录链接'],['draft','已存草稿 · 记录链接'],['unknown','关闭并稍后核验']])){
const b=document.createElement('button');b.type='button';b.textContent=label;b.style.cssText='border:0;border-bottom:1px solid #e87c8d;background:transparent;color:#2b1a17;padding:6px;margin:2px;cursor:pointer';b.onclick=()=>invoke(type);box.append(b);}
box.append(msg);document.documentElement.append(box);
if(!window.__omniFocusInstalled){document.addEventListener('focusin',e=>{if(!e.target.closest('#__omni_panel')&&e.target.matches('input,textarea,[contenteditable=true],[role=textbox]'))window.__omniLastEditor=e.target;},true);window.__omniFocusInstalled=true;}
}'''

def fill_editor(page,text,title=False):
    selector='input[placeholder*=标题],textarea[placeholder*=标题],input[name=title],input[placeholder*=title i]' if title else 'textarea[placeholder*=正文],textarea[placeholder*=评论],textarea[placeholder*=内容],[contenteditable=true],[role=textbox],textarea'
    # A user-focused field wins. Never target our own control panel.
    focused=page.evaluate("""()=>{const e=window.__omniLastEditor;return !!(e&&e.isConnected&&!e.closest('#__omni_panel'));}""")
    if focused and not title:
        page.evaluate("""text=>{const e=window.__omniLastEditor;e.focus();if(e.isContentEditable){document.execCommand('selectAll',false,null);document.execCommand('insertText',false,text);}else{const proto=e.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(proto,'value').set.call(e,text);e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));}}""",text)
        return True
    for frame in page.frames:
        controls=frame.locator(selector)
        for i in range(min(controls.count(),15)):
            control=controls.nth(i)
            if not control.is_visible() or control.evaluate("e=>!!e.closest('#__omni_panel')"):continue
            try:control.fill(text,timeout=3000);return True
            except Exception:continue
    return False

def run_login(api,args,root):
    data=api.request('/api/desktop/accounts/'+args.account+'/'+args.channel)
    platform=data['platform'];spec=PLATFORM_SPECS[platform];outcome={};token='__omni_'+secrets.token_hex(10)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=str(browser_binary(root)),headless=False,chromium_sandbox=True)
        context=browser.new_context(storage_state=data['browser_state'] or None)
        page=context.new_page()
        def action(source,event):
            if event.get('type')!='save_login':return {}
            if not allowed_url(platform,page.url):return {'message':'请返回该平台页面后保存'}
            identity=str(event.get('value','')).strip()
            if not identity:return {'message':'请填写当前已登录账号的固定 ID 或主页链接'}
            state=filter_state(platform,context.storage_state());upstream_identity={}
            if platform=='zhihu' and args.channel.startswith('sau-'):
                image=page.locator("button.AppHeader-profileEntry img[alt^='点击打开'][alt$='的主页']")
                if image.count()!=1:return {'message':'请在知乎登录后进入创作中心，再保存账号绑定'}
                from urllib.parse import urlsplit
                label=image.get_attribute('alt') or '';upstream_identity={'name':label.removeprefix('点击打开').removesuffix('的主页').strip(),'avatar_path':urlsplit(image.get_attribute('src') or '').path}
            try:api.request('/api/desktop/accounts/'+args.account+'/'+args.channel,{'identity':identity,'browser_state':state,'upstream_identity':upstream_identity})
            except httpx.HTTPStatusError as e:return {'message':e.response.json().get('detail','保存失败')}
            outcome['done']=True;return {'message':'此账号登录态已加密保存，可返回桌面任务'}
        page.expose_binding(token,action)
        def panel():
            if not page.is_closed() and allowed_url(platform,page.url):
                page.evaluate(PANEL_JS,{'name':token,'login':True,'identity':data['identity'],'title':'','body':'','action':'publish','target':''})
        page.on('domcontentloaded',lambda:panel())
        page.goto(spec['home'],wait_until='domcontentloaded',timeout=90000);panel()
        end=time.time()+1200
        while time.time()<end and not outcome and not page.is_closed():page.wait_for_timeout(500)
        browser.close()
        if not outcome:raise ValueError('尚未保存账号登录态')

def run_job(api,args,root):
    job=api.request('/api/desktop/jobs/'+args.job+'/prepare',{});prefix='/api/desktop/jobs/'+job['id'];generation={'generation':job['generation']}
    payload=job['payload'];platform=job['platform'];url=job.get('desktop_resume_url') or destination(platform,payload);outcome={};done=threading.Event();lost=threading.Event()
    def heartbeat():
        while not done.wait(20):
            try:api.request(prefix+'/heartbeat',generation)
            except Exception:lost.set();return
    thread=threading.Thread(target=heartbeat,daemon=True);thread.start();submitted=False
    from playwright.sync_api import sync_playwright
    try:
        with tempfile.TemporaryDirectory(prefix='omni-desktop-') as folder,sync_playwright() as p:
            files=[]
            for identifier in payload.get('assets',[]):
                with api.client.stream('GET','/api/assets/'+identifier+'/file') as response:
                    response.raise_for_status();content_type=response.headers.get('content-type','');suffix=job.get('assets_meta',{}).get(identifier,{}).get('suffix','.mp4' if payload['kind']=='video' else '.png')
                    if suffix not in {'.mp4','.mov','.webm','.mkv','.png','.jpg','.jpeg','.webp'}:raise ValueError('素材扩展名无效')
                    target=Path(folder)/(identifier+suffix)
                    with target.open('xb') as f:
                        for chunk in response.iter_bytes(1024*1024):f.write(chunk)
                    files.append(str(target))
            browser=p.chromium.launch(executable_path=str(browser_binary(root)),headless=False,chromium_sandbox=True)
            context=browser.new_context(storage_state=job['credential'].get('browser_state') or None);page=context.new_page();token='__omni_'+secrets.token_hex(10)
            def action(source,event):
                if lost.is_set():return {'message':'执行租约失效，请返回桌面核验原任务'}
                if not allowed_url(platform,page.url):return {'message':'请先回到所选平台的编辑器或原帖'}
                kind=event.get('type')
                if kind in {'published','draft'}:
                    value=str(event.get('value','')).strip()
                    if not allowed_url(platform,value):return {'message':'请粘贴本平台的实际作品或草稿 HTTPS 链接'}
                    if kind=='draft' and payload.get('action','publish')!='publish':return {'message':'评论不能记为文章草稿'}
                    outcome.update(outcome=kind,remote_url=value);return {'message':'已记录，即将返回桌面'}
                if kind=='unknown':outcome.update(outcome='unknown',remote_url='');return {}
                if kind=='fill_title':return {'message':'已填入标题' if fill_editor(page,payload['title'],True) else '请先进入网页编辑器'}
                if kind=='fill_body' and payload.get('action')=='reply' and not page.evaluate("()=>!!(window.__omniLastEditor&&window.__omniLastEditor.isConnected)"):return {'message':'请先点击指定评论的回复输入框，再填入正文'}
                if kind=='fill_body':return {'message':'已填入正文' if fill_editor(page,payload.get('description') or payload['title']) else '请先点击目标评论、回复或正文编辑框'}
                if kind=='show_assets':
                    import subprocess
                    if os.name=='nt':subprocess.Popen(['explorer.exe',folder],shell=False)
                    return {'message':'已打开仅包含本任务素材的目录'}
                if kind=='upload':
                    if not files:return {'message':'本任务没有素材'}
                    candidates=[]
                    for frame in page.frames:
                        inputs=frame.locator('input[type=file]')
                        for i in range(inputs.count()):
                            control=inputs.nth(i);accept=(control.get_attribute('accept') or '').lower()
                            if payload['kind']=='video' and accept and not any(x in accept for x in ('video','mp4','*')):continue
                            if payload['kind']=='images' and accept and not any(x in accept for x in ('image','png','jpg','*')):continue
                            candidates.append(control)
                    if len(candidates)==1:
                        candidates[0].set_input_files(files,timeout=10000);return {'message':'本任务素材已交给平台上传'}
                    if len(candidates)>1:return {'message':'网页有多个上传框，请打开任务素材目录后在正确入口选择文件'}
                    return {'message':'请先在网页打开上传入口'}
                return {}
            page.expose_binding(token,action)
            def panel():
                if not page.is_closed() and allowed_url(platform,page.url):page.evaluate(PANEL_JS,{'name':token,'login':False,'identity':'','title':payload['title'],'body':payload.get('description',''),'action':payload.get('action','publish'),'metadata':payload.get('options',{}),'target':payload.get('target_url','')+(' · 回复 '+payload.get('target_comment_id','') if payload.get('action')=='reply' else '')})
            page.on('domcontentloaded',lambda:panel())
            page.goto(url,wait_until='domcontentloaded',timeout=90000)
            api.request(prefix+'/submitting',generation);submitted=True;panel()
            end=time.time()+5400
            while time.time()<end and not outcome and not lost.is_set() and not page.is_closed():page.wait_for_timeout(500)
            browser.close()
        if not outcome:outcome.update(outcome='unknown',remote_url='')
        if not lost.is_set():api.request(prefix+'/result',{**generation,**outcome})
    finally:
        done.set();thread.join(timeout=2)
        if not outcome and not lost.is_set() and submitted:
            try:api.request(prefix+'/result',{**generation,'outcome':'unknown','remote_url':''})
            except Exception:pass

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['login','job']);p.add_argument('--channel');p.add_argument('--account');p.add_argument('--job');args=p.parse_args()
    api=LocalAPI();root=Path(__file__).resolve().parent.parent
    try:
        if args.action=='login':run_login(api,args,root)
        else:run_job(api,args,root)
    finally:api.close()
if __name__=='__main__':main()
