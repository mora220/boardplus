import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
RB = len(sys.argv) > 1 and sys.argv[1] == 'rb'
U = 'http://localhost:8790/index.html' if RB else 'http://localhost:8787/'
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []; shared = None
    async def ctx(w=1366, h=860):
        nonlocal shared
        if RB and shared: return shared
        c = await b.new_context(viewport={'width': w, 'height': h}, accept_downloads=True)
        await c.route('**/www.gstatic.com/**', lambda r: r.abort()); await c.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
        if RB: shared = c
        return c
    t = await (await ctx()).new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher')
    if RB: await t.fill('#aUser', 'ragab'); await t.fill('#aPass', 'Ra26388'); await t.click('#adminCard button[type=submit]')
    else: await t.click('#gSign'); await t.wait_for_timeout(300); await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk')
    await t.wait_for_timeout(1500)
    ext = lambda ic: t.click(f'#tTools use[href="#i-{ic}"] >> xpath=../..')
    print('graph/curtain buttons gone:', await t.locator('#tTools use[href="#i-graph"], #tTools use[href="#i-curtain"]').count() == 0)
    await ext('clist'); await t.wait_for_timeout(500); await t.fill('#clName', 'خامس أ'); await t.fill('#clNames', 'يوسف أحمد\nسارة خالد\nعمر فهد'); await t.click('#clGo'); await t.wait_for_timeout(700)
    async def join(nm):
      code = (await t.inner_text('#tCode')).strip()
      s = await (await ctx(420, 820)).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e)))
      if RB: await s.evaluate("c=>{localStorage.removeItem('rb_sid_'+c)}", code) if False else None
      await s.goto(U)
      if RB: await s.evaluate("c=>{localStorage.removeItem('rb_sid_'+c)}", code)
      await s.fill('#jCode', code); await s.wait_for_timeout(1500); await s.select_option('#jPick', nm); await s.click('#jGo'); await s.wait_for_timeout(1200); return s
    await join('سارة خالد'); await join('عمر فهد')
    await t.bring_to_front(); await t.wait_for_timeout(500)
    # stamp a point for Sara
    await t.locator('.sc', has_text='سارة').click(); await t.wait_for_timeout(500); fb = await t.locator('#fBoard .ov').bounding_box()
    await t.click('#fTools [data-st="ok"]'); await t.mouse.click(fb['x'] + fb['width'] * .5, fb['y'] + fb['height'] * .5); await t.wait_for_timeout(700); await t.click('#fClose'); await t.wait_for_timeout(5000)
    # second class: new session, only Yousef comes
    await t.click('#tNew'); await t.wait_for_timeout(400)
    if await t.locator('#askOk').count(): await t.click('#askOk')
    await t.wait_for_timeout(1500)
    await ext('clist'); await t.wait_for_timeout(500)
    if await t.locator('#clSaved').count(): await t.select_option('#clSaved', index=1)
    await t.click('#clGo'); await t.wait_for_timeout(700)
    await join('يوسف أحمد'); await t.bring_to_front(); await t.wait_for_timeout(5500)
    await ext('trophy'); await t.wait_for_timeout(1200)
    print('report rows:', [r.replace('\t', ' | ') for r in await t.locator('#atT tr').all_inner_texts()])
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'att.png')
    async with t.expect_download() as dl: await t.click('#atX')
    d = await dl.value; path = SP + ('rb_' if RB else '') + 'att.csv'; await d.save_as(path); print('csv lines:', open(path, encoding='utf-8-sig').read().count('\n') + 1)
    await t.click('#atP'); await t.wait_for_timeout(800)
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
