import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
RB = len(sys.argv) > 1 and sys.argv[1] == 'rb'
U = 'http://localhost:8790/index.html' if RB else 'http://localhost:8787/'
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    shared = None
    async def ctx(w=1366, h=860):
        nonlocal shared
        if RB and shared: return shared
        c = await b.new_context(viewport={'width': w, 'height': h})
        await c.route('**/www.gstatic.com/**', lambda r: r.abort()); await c.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
        if RB: shared = c
        return c
    t = await (await ctx()).new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher')
    if RB: await t.fill('#aUser', 'ragab'); await t.fill('#aPass', 'Ra26388'); await t.click('#adminCard button[type=submit]')
    else: await t.click('#gSign'); await t.wait_for_timeout(300); await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk')
    await t.wait_for_timeout(1500); code = (await t.inner_text('#tCode')).strip()
    ext = lambda ic: t.click(f'#tTools use[href="#i-{ic}"] >> xpath=../..')
    # class list
    await ext('clist'); await t.wait_for_timeout(500); await t.fill('#clName', 'خامس أ'); await t.fill('#clNames', 'يوسف أحمد\nسارة خالد\nعمر فهد'); await t.click('#clGo'); await t.wait_for_timeout(700)
    s = await (await ctx(420, 820)).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e)))
    await s.goto(U); await s.fill('#jCode', code); await s.wait_for_timeout(1500)
    print('picker shown:', await s.is_visible('#jPick'), '| options:', await s.locator('#jPick option').all_inner_texts())
    await s.screenshot(path=SP + ('rb_' if RB else '') + 'lw_pick.png')
    await s.select_option('#jPick', 'سارة خالد'); await s.click('#jGo'); await s.wait_for_timeout(1300)
    print('joined as:', (await t.evaluate("[...T.st.values()].map(x=>x.info.name)")))
    # graph
    await t.bring_to_front(); await ext('graph'); await t.wait_for_timeout(400); await t.fill('#gF', 'x^2 - 4 ; 2x + 1'); await t.wait_for_timeout(200)
    print('graph error text:', repr(await t.inner_text('#gErr'))); await t.click('#gGo'); await t.wait_for_timeout(800)
    print('graph item:', await t.evaluate("JSON.stringify([...T.tMap.values()].filter(x=>x.t==='graph').map(x=>x.f))"), '| student has:', await s.evaluate("[...S.tMap.values()].filter(x=>x.t==='graph').length"))
    print('parser:', await t.evaluate("['2x+1','x^2-4','sin(x)','sqrt(x)','2(x+1)','xsin(x)','alert(1)','constructor'].map(f=>{try{const g=compileFx(f);return f+'='+(+g(2).toFixed(3))}catch(e){return f+':X'}})"))
    # curtain
    await ext('curtain'); await t.wait_for_timeout(900)
    print('curtain on student:', await s.evaluate("(c=>c?c.style.top:null)(document.querySelector('#sBoard .curt'))"))
    h = await t.locator('#tBoard .curt .ch').bounding_box(); bb = await t.locator('#tBoard').bounding_box()
    await t.mouse.move(h['x'] + h['width'] / 2, h['y'] + h['height'] / 2); await t.mouse.down(); await t.mouse.move(h['x'] + h['width'] / 2, bb['y'] + bb['height'] * .6, steps=6); await t.mouse.up(); await t.wait_for_timeout(900)
    print('after reveal drag, student curtain top:', await s.evaluate("(c=>c?c.style.top:null)(document.querySelector('#sBoard .curt'))"))
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'lw_t.png'); await s.screenshot(path=SP + ('rb_' if RB else '') + 'lw_s.png')
    await ext('curtain'); await t.wait_for_timeout(700); print('curtain off for student:', await s.evaluate("!document.querySelector('#sBoard .curt')"))
    # laser
    await t.click('#tTools [data-t="laser"]'); n0 = await t.evaluate('T.tMap.size')
    await t.mouse.move(bb['x'] + 300, bb['y'] + 200); await t.mouse.down(); await t.mouse.move(bb['x'] + 500, bb['y'] + 300, steps=8); await t.mouse.up(); await t.wait_for_timeout(500)
    print('laser on student:', await s.evaluate("(d=>d?[d.style.left,d.style.opacity]:null)(document.querySelector('#sBoard .laz'))"), '| no ink:', await t.evaluate('T.tMap.size') == n0)
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
