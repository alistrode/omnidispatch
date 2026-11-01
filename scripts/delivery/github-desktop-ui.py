"""Drive visible GitHub Desktop controls over a loopback-only Electron inspection port.
Never reads account stores, OAuth tokens, passwords, or browser credentials. No Git/API push.
"""
import argparse,json,re,sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def redact(text):
    text=re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)\b','[credential redacted]',text)
    return re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[email redacted]',text)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--request');parser.add_argument('--port',type=int,default=9337);args=parser.parse_args()
    request=json.loads(Path(args.request).read_text(encoding='utf-8-sig')) if args.request else {'action':'inspect'}
    with sync_playwright() as playwright:
        browser=playwright.chromium.connect_over_cdp(f'http://127.0.0.1:{args.port}',timeout=20000)
        pages=[page for context in browser.contexts for page in context.pages if not page.url.startswith('devtools:')]
        if not pages:raise RuntimeError('GitHub Desktop has no visible renderer')
        page=next((page for page in pages if 'index.html' in page.url),pages[0]);page.set_default_timeout(15000)
        action=request.get('action','inspect')
        if action in {'click','fill','check','select'}:
            if 'role' in request:locator=page.get_by_role(request['role'],name=request.get('name'),exact=request.get('exact',True))
            elif 'label' in request:locator=page.get_by_label(request['label'],exact=request.get('exact',True))
            elif 'placeholder' in request:locator=page.get_by_placeholder(request['placeholder'],exact=request.get('exact',True))
            else:locator=page.locator(request['selector'])
            if 'index' in request:locator=locator.nth(request['index'])
            if action=='click':locator.click()
            elif action=='fill':locator.fill(request['text'])
            elif action=='check':locator.set_checked(request['checked'])
            else:locator.select_option(request['value'])
        elif action=='press':page.keyboard.press(request['key'])
        elif action=='screenshot':page.screenshot(path=request['path'])
        elif action!='inspect':raise ValueError('Unsupported UI operation')
        page.wait_for_timeout(request.get('settle_ms',600))
        controls=page.locator('input,textarea,select').evaluate_all("nodes=>nodes.map(n=>({tag:n.tagName,type:n.type,id:n.id,placeholder:n.getAttribute('placeholder'),label:n.getAttribute('aria-label'),disabled:n.disabled,valueLength:(n.value||'').length}))")
        links=page.locator('a').evaluate_all("nodes=>nodes.map(n=>{let u;try{u=new URL(n.href)}catch{}return {text:(n.innerText||'').trim(),role:n.getAttribute('role'),host:u?.host,path:u?.pathname}})")
        print(json.dumps({'links':links,'title':page.title(),'text':redact(page.locator('body').inner_text())[:14000],'controls':controls},ensure_ascii=False))
        # Disconnect the inspection client; do not close Desktop or any of its windows.
if __name__=='__main__':main()
