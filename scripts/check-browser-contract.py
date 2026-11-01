"""Real bundled Chromium form checks on an in-memory local fixture; no platform writes."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from omnidispatch.browser_desktop import browser_binary,fill_editor,PANEL_JS
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent.parent
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=str(browser_binary(root)),headless=True,chromium_sandbox=True)
    page=browser.new_page();page.set_content('<input name="title" placeholder="标题"><textarea placeholder="评论"></textarea><div contenteditable="true"></div>')
    assert fill_editor(page,'Title',True)
    assert page.locator('input').input_value()=='Title'
    assert fill_editor(page,'<literal> & actual comment')
    assert page.locator('textarea').input_value()=='<literal> & actual comment'
    page.evaluate(PANEL_JS,{'name':'__test','title':'','body':'','login':False,'identity':'','action':'reply','target':'https://tieba.baidu.com/p/123 · 目标楼层 2'})
    assert page.locator('#__omni_panel').is_visible()
    assert '回复指定评论' in page.locator('#__omni_panel').inner_text()
    browser.close()
print(json.dumps({'bundled_browser':True,'title_fill':True,'comment_fill':True,'reply_target_visible':True,'external_publications':0}))
