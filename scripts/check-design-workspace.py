"""Read-only design and interaction review of the real local desktop workspace."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from omnidispatch.browser_desktop import browser_binary
root=Path(sys.argv[1]).resolve();logs=root/'logs';logs.mkdir(exist_ok=True);errors=[];reports=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=str(browser_binary(root)),headless=True,chromium_sandbox=True)
    page=browser.new_page();page.set_default_timeout(45000);page.on('pageerror',lambda e:errors.append(str(e)))
    for width,height in [(1404,845),(900,640),(1920,1080)]:
        page.set_viewport_size({'width':width,'height':height});page.goto('http://127.0.0.1:8791/',wait_until='networkidle')
        page.wait_for_selector('#canvas .leaf');page.wait_for_selector('#scale .workspace-metric')
        metrics=page.locator('#scale strong').all_text_contents();assert len(metrics)==5
        assert page.locator('#app-nav a').count()==8
        assert page.locator('#app-nav .nav-label').count()==8
        icon_positions=page.locator('#app-nav .nav-icon').evaluate_all('(nodes)=>nodes.map(n=>n.getBoundingClientRect().left)');assert max(icon_positions)-min(icon_positions)<2,icon_positions
        assert page.locator('#canvas .node').count()==5
        assert page.locator('#canvas .leaf').count()==5
        assert page.locator('#canvas .leaf[tabindex="0"]').count()==5
        size=page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,height:innerHeight,scroll:document.documentElement.scrollHeight})')
        assert size['scrollWidth']<=width+2,size
        assert size['scroll']<=height+2,size
        page.screenshot(path=str(logs/f'design-home-{width}.png'))
        geometries=[]
        for route,title in [('#/accounts','账号'),('#/jobs','任务'),('#/assets','素材'),('#/agents','执行节点'),('#/updates','更新'),('#/audit','审计'),('#/settings','安全'),('#/p/xiaohongshu','小红书')]:
            page.evaluate('h=>location.hash=h',route)
            page.wait_for_function('([route,title])=>document.querySelector("#page").dataset.route===route && document.querySelector("#page .p-title")?.textContent===title',arg=[route,title])
            geo=page.evaluate('({width:document.querySelector("#page").getBoundingClientRect().width,title:getComputedStyle(document.querySelector(".p-title")).fontSize,overflow:document.documentElement.scrollWidth>innerWidth+2})')
            assert not geo['overflow'],(route,geo);geometries.append(geo)
            if width==1404 and route in ['#/accounts','#/jobs','#/p/xiaohongshu']:page.screenshot(path=str(logs/('design-'+route[2:].replace('/','-')+'.png')),full_page=True)
        assert max(g['width'] for g in geometries)-min(g['width'] for g in geometries)<2
        assert len({g['title'] for g in geometries})==1
        page.keyboard.press('Control+k');page.wait_for_selector('#command-palette[open]');page.locator('#command-search').fill('素材');page.keyboard.press('Enter');page.wait_for_function('()=>document.querySelector("#page").dataset.route==="#/assets"');assert not page.locator('#command-palette').is_visible()
        page.locator('.skip-link').evaluate('element=>element.click()');assert page.evaluate('location.hash')=='#/assets';assert page.evaluate('document.activeElement.id')=='main-content'
        reports.append({'viewport':[width,height],'home_one_screen':True,'same_page_width':True,'same_typography':True,'platform_page':True,'command_palette':True})
    page.evaluate("location.hash='#/jobs?compose=1'");page.get_by_placeholder('正文',exact=True).wait_for();page.get_by_placeholder('正文',exact=True).fill('Local design draft');page.get_by_placeholder('标题',exact=True).fill('Local draft title')
    assert page.locator('.job-composer .field').count()>10
    page.keyboard.press('Alt+3');page.wait_for_function('()=>document.querySelector("#page").dataset.route==="#/assets"')
    page.keyboard.press('Alt+2');page.get_by_placeholder('正文',exact=True).wait_for();assert page.get_by_placeholder('正文',exact=True).input_value()=='Local design draft'
    page.screenshot(path=str(logs/'design-compose.png'))
    action=page.locator('select:has(option[value="comment"])');action.select_option('reply');assert page.locator('input[type=url]').is_visible();assert page.get_by_placeholder('目标评论 ID / 楼层').is_visible() or page.get_by_placeholder('要回复的实际帖子 ID（不是楼层）').is_visible()
    page.set_viewport_size({'width':900,'height':640});page.wait_for_timeout(250);assert page.get_by_placeholder('正文',exact=True).input_value()=='Local design draft'
    page.evaluate("location.hash='#/p/douyin'");page.wait_for_selector('.channel-options .channel-option');page.locator('.channel-options .channel-option').first.click();page.wait_for_selector('#page .led');assert page.locator('#page .p-title').is_visible()
    browser.close()
assert not errors,errors
result={'design_workspace':reports,'draft_preserved':True,'comment_and_reply_forms':True,'channel_drilldown':True,'page_errors':errors,'external_publications':0}
(logs/'design-workspace-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
