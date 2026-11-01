"""Read-only live desktop geometry checks at three window sizes; preserve form contents."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from omnidispatch.browser_desktop import browser_binary
root=Path(sys.argv[1]).resolve();reports=[];errors=[]
routes=['#/accounts','#/agents','#/jobs','#/assets','#/updates','#/audit','#/settings']
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=str(browser_binary(root)),headless=True,chromium_sandbox=True)
    page=browser.new_page();page.goto('http://127.0.0.1:8791/',wait_until='networkidle')
    channels=page.request.get('http://127.0.0.1:8791/api/channels').json()
    routes.append('#/c/'+channels[0]['id'])
    page.on('pageerror',lambda e:errors.append(str(e)))
    for width,height in [(1404,845),(900,640),(1920,1080)]:
        page.set_viewport_size({'width':width,'height':height});page.goto('http://127.0.0.1:8791/',wait_until='networkidle')
        sizes=[]
        for route in routes:
            page.evaluate('h=>location.hash=h',route);page.wait_for_function('h=>document.querySelector("#page").dataset.route===h',arg=route)
            measure=page.evaluate('''()=>{const e=document.querySelector('#page'),t=e.querySelector('.p-title');return {route:location.hash,width:e.getBoundingClientRect().width,title:getComputedStyle(t).fontSize,scale:getComputedStyle(document.documentElement).getPropertyValue('--ui-scale'),overflow:document.documentElement.scrollWidth>innerWidth+2}}''')
            assert not measure['overflow'],measure;sizes.append(measure)
        assert max(x['width'] for x in sizes)-min(x['width'] for x in sizes)<2,sizes
        assert len({(x['title'],x['scale']) for x in sizes})==1,sizes
        page.evaluate("location.hash='#/accounts'");page.get_by_placeholder('账号名称').wait_for();page.get_by_placeholder('账号名称').fill('Unsaved geometry fixture')
        page.set_viewport_size({'width':width-40,'height':height-20});page.wait_for_timeout(300)
        assert page.get_by_placeholder('账号名称').input_value()=='Unsaved geometry fixture'
        page.set_viewport_size({'width':width,'height':height})
        for group in ['core','short','long','community','writing']:
            page.evaluate('h=>location.hash=h','#/?group='+group);page.wait_for_selector('#canvas .node');page.wait_for_timeout(250)
            size=page.evaluate('({height:innerHeight,scroll:document.documentElement.scrollHeight,width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
            assert size['scroll']<=size['height']+2,(group,size)
            assert size['scrollWidth']<=size['width']+2,(group,size)
            tree_width=page.locator('#canvas').bounding_box()['width']
            assert abs(tree_width-sizes[0]['width'])<2,(tree_width,sizes[0])
        reports.append({'viewport':[width,height],'pages':sizes,'tree_groups_one_screen':True,'unsaved_form_preserved':True})
    page.evaluate("""()=>{window.__originalFetch=window.fetch;window.fetch=async(...args)=>{if(args[0]==='/api/agents')await new Promise(r=>setTimeout(r,500));return window.__originalFetch(...args)};}""")
    page.keyboard.press('Alt+5');page.wait_for_timeout(60);page.keyboard.press('Alt+3');page.wait_for_timeout(750)
    assert page.locator('#page .p-title').inner_text()=='素材'
    assert page.locator('#app-nav a[aria-current=page]').get_attribute('href')=='#/assets'
    page.evaluate('()=>{window.fetch=window.__originalFetch;delete window.__originalFetch;}')
    catalog=page.request.get('http://127.0.0.1:8791/api/platforms').json()
    dense=[{'id':f'00000000-0000-4000-8000-{i+1:012d}','label':'Local '+item['label'],'platform':item['id'],'state':'active','credentials':[],'egress':{'mode':'direct'}} for i,item in enumerate(catalog)]
    page.route('**/api/accounts',lambda route:route.fulfill(json=dense))
    page.evaluate("location.hash='#/accounts'");page.wait_for_function("()=>document.querySelectorAll('#ptree .tree-band').length>1")
    assert page.locator('#ptree .pleaf').count()==23
    labels=page.locator('#ptree .node .nm').evaluate_all('(nodes)=>nodes.map(n=>({left:n.getBoundingClientRect().left,right:n.getBoundingClientRect().right,top:n.getBoundingClientRect().top}))')
    for i,a in enumerate(labels):
        for b in labels[i+1:]:
            if abs(a['top']-b['top'])<2:assert a['right']+3<=b['left'] or b['right']+3<=a['left'],(a,b)
    page.unroute('**/api/accounts')
    fixture=[{'id':'00000000-0000-4000-8000-000000000001','label':'Local draft fixture','platform':'x','state':'active','credentials':[],'egress':{'mode':'direct'}}]
    page.route('**/api/accounts',lambda route:route.fulfill(json=fixture))
    page.evaluate("location.hash='#/jobs'");page.get_by_placeholder('正文').wait_for();page.get_by_placeholder('正文').fill('Local unsent draft')
    page.get_by_placeholder('标题',exact=True).fill('Unsent title')
    page.keyboard.press('Alt+3');page.wait_for_function("()=>location.hash==='#/assets'")
    page.locator('#app-nav a[href="#/jobs"]').click();page.get_by_placeholder('正文').wait_for()
    assert page.get_by_placeholder('正文').input_value()=='Local unsent draft'
    assert page.get_by_placeholder('标题',exact=True).input_value()=='Unsent title'
    assert page.locator('#app-nav a[aria-current=page]').get_attribute('href')=='#/jobs'
    page.unroute('**/api/accounts')
    page.set_viewport_size({'width':1404,'height':845});page.evaluate("location.hash='#/accounts'");page.wait_for_function("()=>document.querySelector('#page').dataset.route==='#/accounts' && document.querySelector('#page .p-title')?.textContent==='账号'");page.wait_for_timeout(300);page.screenshot(path=str(root/'logs/proportions-accounts.png'))
    page.evaluate("location.hash='#/'");page.wait_for_selector('#canvas .node');page.wait_for_timeout(300);page.screenshot(path=str(root/'logs/proportions-tree.png'))
    browser.close()
assert not errors,errors
result={'uniform_proportions':reports,'page_errors':errors,'task_draft_preserved_on_navigation':True,'application_keyboard_navigation':True,'rapid_navigation_keeps_current_page':True,'dense_accounts_wrap_without_overlap':True,'external_publications':0}
(root/'logs/proportions-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
