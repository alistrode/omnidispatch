"""Read-only browser checks against the installed workbench, with no platform write."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from omnidispatch.browser_desktop import browser_binary
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent.parent
checks=[];errors=[]
groups={'core':['小红书','B 站','视频号','YouTube','X'],'short':['抖音','快手','西瓜视频','好看视频','微博'],'long':['腾讯视频','优酷','爱奇艺','搜狐视频'],'community':['贴吧','知乎','豆瓣','微博','微信公众号'],'writing':['头条号','简书','掘金','CSDN','百家号']}
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=str(browser_binary(root)),headless=True,chromium_sandbox=True)
    page=browser.new_page(viewport={'width':1404,'height':845});page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8791/',wait_until='networkidle')
    for group,expected in groups.items():
        page.evaluate('hash=>location.hash=hash','#/?group='+group)
        page.wait_for_function("id=>document.querySelector('#platform-groups [aria-current=page]')?.getAttribute('href')==='#/?group='+id",arg=group)
        page.wait_for_function("expected=>expected.every(x=>[...document.querySelectorAll('#canvas .node .nm')].some(n=>n.textContent===x))",arg=expected)
        labels=page.locator('#canvas .node .nm').all_text_contents()
        assert all(x in labels for x in expected),(group,labels)
        size=page.evaluate('({height:innerHeight,scroll:document.documentElement.scrollHeight})')
        assert size['scroll']<=size['height']+2,(group,size)
        checks.append({'group':group,'platforms':expected,'one_screen':True})
    page.evaluate("location.hash='#/accounts'");page.wait_for_selector('#page select')
    names=page.locator('#page select').all_text_contents()
    assert all(any(x in n for n in names) for x in ['贴吧','知乎','豆瓣','优酷','快手'])
    page.evaluate("location.hash='#/jobs'");page.wait_for_selector('select:has(option[value="comment"])')
    page.locator('select:has(option[value="comment"])').select_option('comment')
    assert page.locator('input[type=url]').is_visible()
    page.locator('select:has(option[value="comment"])').select_option('reply')
    assert page.get_by_placeholder('目标评论 ID / 楼层').is_visible() or page.get_by_placeholder('要回复的实际帖子 ID（不是楼层）').is_visible()
    assert not errors,errors
    browser.close()
print(json.dumps({'groups':checks,'account_platform_choices':True,'comment_target_form':True,'reply_target_form':True,'page_errors':errors,'external_publications':0},ensure_ascii=False))
