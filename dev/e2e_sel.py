import asyncio
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
    bb = await t.locator('#tBoard .ov').bounding_box(); X = lambda x: bb['x'] + x / 1600 * bb['width']; Y = lambda y: bb['y'] + y / 1000 * bb['height']
    # text with a bigger size
    await t.click('#tTools [data-t="text"]'); print('size control visible:', await t.is_visible('#tTools .tsz'))
    for _ in range(3): await t.click('#tTools [data-zs="+"]')
    print('size now:', await t.inner_text('#tTools .tsz .zv'))
    await t.mouse.click(X(200), Y(150)); await t.wait_for_timeout(300); await t.keyboard.type('الدرس الأول: الكسور'); await t.keyboard.press('Enter'); await t.wait_for_timeout(500)
    await t.click('#tTools [data-t="pen"]')
    await t.mouse.move(X(300), Y(500)); await t.mouse.down(); await t.mouse.move(X(600), Y(560), steps=8); await t.mouse.move(X(700), Y(450), steps=6); await t.mouse.up(); await t.wait_for_timeout(400)
    items = await t.evaluate("JSON.stringify([...T.tMap.values()].map(s=>[s.t, s.z||'', s.x||s.p[0]]))"); print('items:', items)
    # move mode: drag the text
    await t.click('#tTools use[href="#i-move"] >> xpath=../..'); await t.wait_for_timeout(300)
    tx = await t.evaluate("(()=>{const s=[...T.tMap.values()].find(s=>s.t==='text');const b=strokeBox(s);return [(b[0]+b[2])/2,(b[1]+b[3])/2]})()")
    await t.mouse.move(X(tx[0]), Y(tx[1])); await t.mouse.down(); await t.mouse.move(X(tx[0] + 300), Y(tx[1] + 200), steps=8); await t.mouse.up(); await t.wait_for_timeout(800)
    print('text moved to:', await t.evaluate("(s=>[s.x,s.y])([...T.tMap.values()].find(s=>s.t==='text'))"), '| student sees:', await s.evaluate("(s=>[s.x,s.y])([...S.tMap.values()].find(s=>s.t==='text'))"))
    await t.screenshot(path=SP + 'sel1.png')
    # drag the pen stroke by touching its line
    await t.mouse.move(X(450), Y(530)); await t.mouse.down(); await t.mouse.move(X(450), Y(780), steps=6); await t.mouse.up(); await t.wait_for_timeout(600)
    print('pen first point:', await t.evaluate("[...T.tMap.values()].find(s=>s.t==='pen').p.slice(0,2)"))
    # band select both, enlarge, then undo
    await t.mouse.move(X(20), Y(20)); await t.mouse.down(); await t.mouse.move(X(1580), Y(980), steps=6); await t.mouse.up(); await t.wait_for_timeout(300)
    print('selected:', await t.evaluate('SEL.ids.size'))
    await t.click('.selbar [data-sa="+"]'); await t.wait_for_timeout(400)
    print('text size after A+:', await t.evaluate("[...T.tMap.values()].find(s=>s.t==='text').z"))
    await t.screenshot(path=SP + 'sel2.png')
    await t.keyboard.press('Control+z'); await t.wait_for_timeout(400); print('after undo:', await t.evaluate("[...T.tMap.values()].find(s=>s.t==='text').z"))
    await t.keyboard.press('Delete'); await t.wait_for_timeout(500); print('after delete:', await t.evaluate('T.tMap.size'), '| student:', await s.evaluate('S.tMap.size'))
    print('errors:', errs[:5]); await b.close()
asyncio.run(main())
