import asyncio, math
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
U = 'http://localhost:8787/'
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    async def ctx():
        c = await b.new_context(viewport={'width': 1366, 'height': 860}); await c.route('**/www.gstatic.com/**', lambda r: r.abort()); return c
    t = await (await ctx()).new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher'); await t.click('#gSign'); await t.wait_for_timeout(300)
    await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk'); await t.wait_for_timeout(1500); code = (await t.inner_text('#tCode')).strip()
    s = await (await ctx()).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e)))
    await s.goto(U); await s.fill('#jCode', code); await s.wait_for_timeout(500); await s.fill('#jName', 'Omar'); await s.click('#jGo'); await s.wait_for_timeout(1200)
    print('teacher tools:', await t.evaluate("[...document.querySelectorAll('#tTools [data-t]')].map(b=>b.dataset.t).join(',')"), '| pager in toolbar:', await t.evaluate("!!document.querySelector('#tTools #tPager')"))
    print('extras:', await t.evaluate("[...document.querySelectorAll('#tTools [data-x]')].map(b=>b.title.slice(0,22))"))
    bb = await t.locator('#tBoard .ov').bounding_box(); X = lambda x: bb['x'] + x / 1600 * bb['width']; Y = lambda y: bb['y'] + y / 1000 * bb['height']
    async def stroke(pts):
      await t.mouse.move(X(pts[0][0]), Y(pts[0][1])); await t.mouse.down()
      for x, y in pts[1:]: await t.mouse.move(X(x), Y(y), steps=3)
      await t.mouse.up(); await t.wait_for_timeout(300)
    await t.click('#tTools [data-t="smart"]')
    import random; random.seed(3); j = lambda: random.uniform(-6, 6)
    line = [(100 + i * 25 + j(), 120 + i * 6 + j()) for i in range(16)]
    rect = [(500 + i * 25 + j(), 100 + j()) for i in range(10)] + [(750 + j(), 100 + i * 20 + j()) for i in range(10)] + [(750 - i * 25 + j(), 300 + j()) for i in range(10)] + [(500 + j(), 300 - i * 20 + j()) for i in range(11)]
    circ = [(1100 + 120 * math.cos(a / 30 * 6.283) + j(), 220 + 110 * math.sin(a / 30 * 6.283) + j()) for a in range(32)]
    tri = [(200 + i * 20 + j(), 700 - i * 30 + j()) for i in range(10)] + [(400 + i * 20 + j(), 400 + i * 30 + j()) for i in range(10)] + [(600 - i * 40 + j(), 700 + j()) for i in range(11)]
    arrow = [(800 + i * 30 + j() / 3, 600 + j() / 3) for i in range(15)] + [(1220 - i * 12, 600 - i * 10) for i in range(6)]
    scribble = [(1000 + 100 * math.sin(i / 3) + i * 4, 800 + 50 * math.cos(i / 2)) for i in range(40)]
    for sh in [line, rect, circ, tri, arrow, scribble]: await stroke(sh)
    print('recognized:', await t.evaluate("[...T.tMap.values()].map(s=>s.t)"))
    await t.screenshot(path=SP + 'smart.png')
    print('student sees:', await s.evaluate("[...S.tMap.values()].map(s=>s.t)"))
    # show dialog has image buttons
    await t.click('#tTools use[href="#i-show"] >> xpath=../..'); await t.wait_for_timeout(300)
    print('show dialog image buttons:', await t.locator('#shImg').count(), await t.locator('#shPaste').count()); await t.screenshot(path=SP + 'show_dlg.png'); await t.click('.showsrc [data-close]')
    # paste image + crop
    await t.evaluate('''()=>{const c=document.createElement('canvas');c.width=800;c.height=500;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,800,500);x.fillStyle='#000';x.font='bold 60px sans-serif';x.fillText('QUESTION 1',60,200);
      return new Promise(r=>c.toBlob(bl=>{const dt=new DataTransfer();dt.items.add(new File([bl],'q.png',{type:'image/png'}));document.body.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true}));r()}))}'''); await t.wait_for_timeout(1500)
    await t.click('.imgbar [data-z="crop"]'); r = await t.evaluate('curRect()')
    await t.mouse.move(X(r['x'] + 20), Y(r['y'] + 20)); await t.mouse.down(); await t.mouse.move(X(r['x'] + r['w'] * .7), Y(r['y'] + r['h'] * .6), steps=5); await t.mouse.up()
    await t.click('.imgbar [data-z="cropok"]'); await t.wait_for_timeout(1500)
    print('after crop img', await t.evaluate('[T.bg.img.width,T.bg.img.height]'), '| student img', await s.evaluate('[S.bg.img&&S.bg.img.width,S.bg.img&&S.bg.img.height]'), '| student tr', await s.evaluate('JSON.stringify(S.bg.tr)'))
    await t.click('.imgbar [data-z="done"]')
    # lasso half of the line
    await t.click('#tTools [data-t="lasso"]'); n0 = await t.evaluate('T.tMap.size')
    await stroke([(150 + 70 * math.cos(a / 12 * 6.283), 130 + 70 * math.sin(a / 12 * 6.283)) for a in range(13)])
    if await t.locator('.lmenu').count(): await t.locator('.lmenu button').first.click(); await t.wait_for_timeout(500)
    print('lasso strokes', n0, '->', await t.evaluate('T.tMap.size'))
    # page add from toolbar
    await t.click('#tTools #pgAdd'); await t.wait_for_timeout(2500); print('page label:', await t.inner_text('#pgLbl'), '| strokes on new page', await t.evaluate('T.tMap.size'))
    await t.screenshot(path=SP + 'toolbar.png', clip={'x': 0, 'y': 760, 'width': 1366, 'height': 100})
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
