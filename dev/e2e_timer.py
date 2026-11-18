import asyncio, sys
from playwright.async_api import async_playwright
RB = len(sys.argv) > 1 and sys.argv[1] == 'rb'
U = 'http://localhost:8790/index.html' if RB else 'http://localhost:8787/'
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    c = await b.new_context(viewport={'width': 1366, 'height': 860}); await c.route('**/www.gstatic.com/**', lambda r: r.abort()); await c.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
    t = await c.new_page(); t.on('pageerror', lambda e: errs.append(str(e)))
    await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher')
    if RB: await t.fill('#aUser', 'ragab'); await t.fill('#aPass', 'Ra26388'); await t.click('#adminCard button[type=submit]')
    else: await t.click('#gSign'); await t.wait_for_timeout(300); await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk')
    await t.wait_for_timeout(1500); await t.click('#tTimerBtn'); await t.wait_for_timeout(300)
    print('buttons:', await t.locator('.tgrid [data-m]').all_inner_texts())
    await t.click('.tgrid [data-m="1.5"]'); await t.wait_for_timeout(800)
    print('timer:', await t.inner_text('#tTimer'), '| left s:', await t.evaluate("(async()=>Math.round(((await DB.get(`sessions/${T.code}/meta/timerEnd`))-DB.now())/1000))()"))
    print('errors:', errs); await b.close()
asyncio.run(main())
