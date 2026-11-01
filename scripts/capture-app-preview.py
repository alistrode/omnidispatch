"""Capture stable local application surfaces after route and viewport settle."""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
from omnidispatch.browser_desktop import browser_binary
root=Path(sys.argv[1]).resolve()
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=str(browser_binary(root)),headless=True,chromium_sandbox=True)
    page=browser.new_page(viewport={'width':1404,'height':845})
    page.goto('http://127.0.0.1:8791/',wait_until='domcontentloaded',timeout=60000)
    page.evaluate("location.hash='#/?group=core'");page.wait_for_function("()=>document.querySelector('#platform-groups [aria-current=page]')?.getAttribute('href')==='#/?group=core'");page.wait_for_selector('#canvas .leaf',timeout=60000);page.wait_for_timeout(350)
    page.screenshot(path=str(root/'logs/final-app-home.png'))
    page.locator('#app-nav a[href="#/accounts"]').click()
    page.wait_for_function("()=>document.querySelector('#page .p-title')?.textContent==='账号' && document.querySelector('#page').dataset.route==='#/accounts'")
    page.wait_for_timeout(350);page.screenshot(path=str(root/'logs/final-app-accounts.png'))
    browser.close()
print('Stable local app previews captured')
