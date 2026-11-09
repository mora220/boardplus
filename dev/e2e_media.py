import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
U = 'http://localhost:8787/'
async def login(pg, email):
    await pg.goto(U); await pg.wait_for_timeout(500)
    await pg.click('#toTeacher'); await pg.click('#gSign'); await pg.wait_for_timeout(300)
    await pg.fill('#atxt', email); await pg.click('#atOk'); await pg.wait_for_timeout(1500)
async def record(s, icon, secs):
    await s.click(f'#sTools use[href="#i-{icon}"] >> xpath=../..'); await s.wait_for_timeout(1200)
    await s.click('#rcGo'); await s.wait_for_timeout(secs * 1000)
    await s.click('#rcGo'); await s.wait_for_timeout(900)
    await s.screenshot(path=SP + f'rec_{icon}.png')
    await s.click('#rcAdd'); await s.wait_for_timeout(2500)
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(args=['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream', '--autoplay-policy=no-user-gesture-required']); errs = []
    async def ctx(**kw):
        c = await b.new_context(viewport={'width': 1366, 'height': 860}, permissions=['microphone', 'camera'], **kw); await c.route('**/www.gstatic.com/**', lambda r: r.abort()); return c
    ct, cs = await ctx(), await ctx()
    t = await ct.new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await login(t, 'admin@test.dev'); code = (await t.inner_text('#tCode')).strip(); print('code', code)
    s = await cs.new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e))); await s.set_viewport_size({'width': 900, 'height': 820})
    await s.goto(U); await s.fill('#jCode', code); await s.wait_for_timeout(600); await s.fill('#jName', 'يوسف'); await s.click('#jGo'); await s.wait_for_timeout(1500)
    bb = await s.locator('#sBoard .ov').bounding_box()
    # audio
    await record(s, 'mic', 3)
    print('placing mode:', await s.evaluate('!!S.board.placing'))
    await s.mouse.click(bb['x'] + bb['width'] * .3, bb['y'] + bb['height'] * .2); await s.wait_for_timeout(1200)
    # video
    await record(s, 'cam', 3)
    await s.mouse.click(bb['x'] + bb['width'] * .3, bb['y'] + bb['height'] * .5); await s.wait_for_timeout(1500)
    items = await s.evaluate("[...S.mine.values()].filter(x=>x.t==='media').map(x=>[x.k,x.d,x.x,x.y])"); print('student media items:', items)
    await s.screenshot(path=SP + 'stu_board.png')
    # student plays own audio
    await s.mouse.click(bb['x'] + bb['width'] * .3, bb['y'] + bb['height'] * .2); await s.wait_for_timeout(1500)
    print('student player:', await s.evaluate("(()=>{const a=document.querySelector('.mplay audio');return a?[a.src.slice(0,5), a.duration>0||a.readyState]:null})()"))
    await s.click('.mplay [data-close]')
    # teacher sees + plays
    await t.wait_for_timeout(800)
    print('teacher sees items:', await t.evaluate("[...[...T.st.values()][0].strokes.values()].filter(x=>x.t==='media').length"))
    await t.screenshot(path=SP + 't_grid.png')
    await t.click('.sc'); await t.wait_for_timeout(700); fb = await t.locator('#fBoard .ov').bounding_box()
    await t.mouse.click(fb['x'] + fb['width'] * .3, fb['y'] + fb['height'] * .5); await t.wait_for_timeout(3000)
    print('teacher video player:', await t.evaluate("(()=>{const v=document.querySelector('.mplay video');return v?[v.src.slice(0,5), v.readyState, v.videoWidth]:document.querySelector('#mpBody')&&document.querySelector('#mpBody').textContent})()"))
    await t.screenshot(path=SP + 't_play.png')
    await t.click('.mplay [data-close]')
    # teacher deletes the video with the select tool
    await t.click('#fTools [data-t="cut"]')
    await t.mouse.move(fb['x'] + fb['width'] * .25, fb['y'] + fb['height'] * .45); await t.mouse.down()
    await t.mouse.move(fb['x'] + fb['width'] * .35, fb['y'] + fb['height'] * .55, steps=5); await t.mouse.up(); await t.wait_for_timeout(1500)
    print('after teacher select-delete, student media:', await s.evaluate("[...S.mine.values()].filter(x=>x.t==='media').map(x=>x.k)"))
    r = await t.request.get(U + '__test/dump?room=s:' + code); dump = await r.json() if r.ok else {}
    med = (dump.get('media') or {}) if isinstance(dump, dict) else {}
    print('media blobs left on server:', {k: list(v.keys()) for k, v in med.items()} if med else med)
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
