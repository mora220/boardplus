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
        c = await b.new_context(viewport={'width': w, 'height': h})
        await c.route('**/www.gstatic.com/**', lambda r: r.abort()); await c.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
        if RB: shared = c
        return c
    t = await (await ctx()).new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher')
    if RB: await t.fill('#aUser', 'ragab'); await t.fill('#aPass', 'Ra26388'); await t.click('#adminCard button[type=submit]')
    else: await t.click('#gSign'); await t.wait_for_timeout(300); await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk')
    await t.wait_for_timeout(1500)
    code = (await t.inner_text('#tCode')).strip()
    s = await (await ctx(420, 820)).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e))); await s.goto(U)
    if RB: await s.evaluate("c=>{localStorage.removeItem('rb_sid_'+c)}", code)
    await s.fill('#jCode', code); await s.wait_for_timeout(900); await s.fill('#jName', 'سارة'); await s.click('#jGo'); await s.wait_for_timeout(1200)
    await t.bring_to_front()
    print('size buttons in teacher bar:', await t.locator('#tTools .szg .sz').count(), '| focus bar:', await t.locator('#fTools .szg .sz').count())
    await t.click('#tTools .szg [data-w="20"]'); print('tool w:', await t.evaluate('tTool.get().w'))
    # laser
    await t.click('#tTools [data-t="laser"]')
    bb = await t.locator('#tBoard').bounding_box()
    await t.mouse.move(bb['x'] + 300, bb['y'] + 200); await t.mouse.down()
    for i in range(30): await t.mouse.move(bb['x'] + 300 + i * 15, bb['y'] + 200 + (i % 10) * 12); await t.wait_for_timeout(16)
    await t.mouse.up(); await t.wait_for_timeout(500)
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'laser_t.png')
    n = await s.evaluate("(()=>{const o=LZ2.hosts.get(document.querySelector('#sBoard'));return o?o.segs.reduce((a,g)=>a+g.p.length,0):-1})()")
    print('student trail points:', n); await s.screenshot(path=SP + ('rb_' if RB else '') + 'laser_s.png')
    await s.wait_for_timeout(2600)
    print('after 2.6s:', await s.evaluate("(()=>{const o=LZ2.hosts.get(document.querySelector('#sBoard'));return o?o.segs.length:-1})()"), await t.evaluate("(()=>{const o=LZ2.hosts.get(document.querySelector('#tBoard'));return o?o.segs.length:-1})()"))
    # quiz pen sizes
    img = await t.evaluate("()=>{const c=document.createElement('canvas');c.width=800;c.height=450;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,800,450);return c.toDataURL('image/png')}")
    await t.evaluate("img=>startQuiz([{id:'q1',img,ans:'B',kind:'mc',lim:60}])", img); await t.wait_for_timeout(1500)
    print('quiz size buttons:', await t.locator('#rInk [data-iw]').count())
    await t.click('#rInk [data-iw="3"]'); await t.mouse.move(400, 400); await t.mouse.down(); await t.mouse.move(600, 420, steps=8); await t.mouse.up()
    print('quiz stroke w:', await t.evaluate('[...QI.map.values()].map(x=>x.w)'))
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'qsize.png')
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
