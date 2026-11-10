import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
U = 'http://localhost:8787/'
async def login(pg, email):
    await pg.goto(U); await pg.wait_for_timeout(500); await pg.click('#toTeacher'); await pg.click('#gSign'); await pg.wait_for_timeout(300)
    await pg.fill('#atxt', email); await pg.click('#atOk'); await pg.wait_for_timeout(1500)
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    async def ctx():
        c = await b.new_context(viewport={'width': 1366, 'height': 860}); await c.route('**/www.gstatic.com/**', lambda r: r.abort()); return c
    t = await (await ctx()).new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await login(t, 'sara@school.sa'); tcode = (await t.inner_text('#tCode')).strip()
    s = await (await ctx()).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e)))
    await s.goto(U); await s.fill('#jCode', tcode); await s.wait_for_timeout(500); await s.fill('#jName', 'Omar'); await s.click('#jGo'); await s.wait_for_timeout(1200)
    bb = await s.locator('#sBoard .ov').bounding_box(); await s.mouse.move(bb['x'] + 100, bb['y'] + 100); await s.mouse.down(); await s.mouse.move(bb['x'] + 400, bb['y'] + 150, steps=6); await s.mouse.up(); await s.wait_for_timeout(600)
    a = await (await ctx()).new_page(); a.on('pageerror', lambda e: errs.append('A:' + str(e)))
    await login(a, 'admin@test.dev'); acode = (await a.inner_text('#tCode')).strip()
    await a.click('#tAdmin'); await a.wait_for_timeout(900)
    print('admin list:', [x.replace('\n', ' | ') for x in await a.locator('.trow').all_inner_texts()])
    await a.screenshot(path=SP + 'watch_list.png')
    await a.click('[data-act="watch"]'); await a.wait_for_timeout(1500)
    print('admin now on code', (await a.inner_text('#tCode')).strip(), '(teacher code', tcode, ') | bar:', await a.inner_text('#watchBar'))
    print('students seen by admin:', await a.inner_text('#sCount'), '| roster seen by teacher:', await t.inner_text('#sCount'))
    print('teacher live still points to teacher:', await t.evaluate(f"DB.get('teachers/'+ME.uid+'/live').then(v=>v&&v.code)"))
    await a.screenshot(path=SP + 'watch_view.png')
    await a.click('#watchBack'); await a.wait_for_timeout(1500)
    print('back to own:', (await a.inner_text('#tCode')).strip() == acode, '| bar hidden:', await a.evaluate("$('#watchBar').hidden"))
    # by code
    await a.click('#tAdmin'); await a.wait_for_timeout(600); await a.fill('#aCode', tcode); await a.click('#aWatch'); await a.wait_for_timeout(1500)
    print('by code ->', (await a.inner_text('#tCode')).strip())
    print('errors:', errs[:5]); await b.close()
asyncio.run(main())
