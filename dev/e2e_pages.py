import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
U = 'http://localhost:8787/'
async def login(pg, email):
    await pg.goto(U); await pg.wait_for_timeout(500)
    await pg.click('#toTeacher'); await pg.click('#gSign'); await pg.wait_for_timeout(300)
    await pg.fill('#atxt', email); await pg.click('#atOk'); await pg.wait_for_timeout(1500)
async def draw(pg, sel, a, b):
    bb = await pg.locator(sel).bounding_box()
    await pg.mouse.move(bb['x'] + bb['width'] * a[0], bb['y'] + bb['height'] * a[1]); await pg.mouse.down()
    await pg.mouse.move(bb['x'] + bb['width'] * b[0], bb['y'] + bb['height'] * b[1], steps=8); await pg.mouse.up(); await pg.wait_for_timeout(500)
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    async def ctx():
        c = await b.new_context(viewport={'width': 1366, 'height': 860}); await c.route('**/www.gstatic.com/**', lambda r: r.abort()); return c
    t = await (await ctx()).new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await login(t, 'admin@test.dev'); code = (await t.inner_text('#tCode')).strip()
    s = await (await ctx()).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e))); await s.set_viewport_size({'width': 900, 'height': 800})
    await s.goto(U); await s.fill('#jCode', code); await s.wait_for_timeout(600); await s.fill('#jName', 'يوسف'); await s.click('#jGo'); await s.wait_for_timeout(1500)
    state = lambda: asyncio.gather(t.evaluate('T.tMap.size'), s.evaluate('S.mine.size'), t.inner_text('#pgLbl'), t.evaluate('!!T.bg.img'))
    # page 1: teacher stroke + image, student 2 strokes, teacher gives a ✓ stamp
    await draw(t, '#tBoard .ov', (.2, .3), (.6, .3))
    await t.evaluate('''()=>{const c=document.createElement('canvas');c.width=600;c.height=300;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,600,300);x.fillStyle='#000';x.font='bold 50px sans-serif';x.fillText('PAGE ONE',40,170);
      return new Promise(r=>c.toBlob(bl=>{const dt=new DataTransfer();dt.items.add(new File([bl],'q.png',{type:'image/png'}));document.body.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true}));r()}))}'''); await t.wait_for_timeout(1500)
    await t.keyboard.press('Escape')
    await draw(s, '#sBoard .ov', (.2, .7), (.6, .7)); await draw(s, '#sBoard .ov', (.2, .8), (.6, .8))
    await t.click('.sc'); await t.wait_for_timeout(500); fb = await t.locator('#fBoard .ov').bounding_box()
    await t.click('#fTools [data-st="ok"]'); await t.mouse.click(fb['x'] + fb['width'] * .8, fb['y'] + fb['height'] * .7); await t.wait_for_timeout(800); await t.click('#fClose')
    print('page1 [teacher strokes, student strokes, label, img]:', await state(), '| points', await s.inner_text('#sPts'))
    # new page
    await t.click('#pgAdd'); await t.wait_for_timeout(2500)
    print('new page:', await state(), '| student marks', await s.evaluate('S.marks ? S.marks.size : -1'))
    await draw(t, '#tBoard .ov', (.3, .5), (.5, .5)); await draw(s, '#sBoard .ov', (.3, .6), (.4, .6))
    print('page2 after writing:', await state())
    await t.screenshot(path=SP + 'pages_p2.png')
    # back to page 1
    await t.click('#pgPrev'); await t.wait_for_timeout(2500)
    print('back to page1:', await state(), '| points', await s.inner_text('#sPts'), '| student marks', await s.evaluate('S.marks ? S.marks.size : -1'))
    await t.screenshot(path=SP + 'pages_p1.png'); await s.screenshot(path=SP + 'pages_stu.png')
    await t.click('#pgNext'); await t.wait_for_timeout(2500)
    print('forward to page2:', await state())
    # delete page 2 via menu
    await t.click('#pgLbl'); await t.wait_for_timeout(400); await t.screenshot(path=SP + 'pages_menu.png')
    await t.click('#pgDel'); await t.wait_for_timeout(300); await t.click('#askOk'); await t.wait_for_timeout(2500)
    print('after deleting page2:', await state())
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
