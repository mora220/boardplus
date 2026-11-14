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
    print('tools:', await t.evaluate("[...document.querySelectorAll('#tTools [data-t]')].map(b=>b.dataset.t).join(',')"), '| student has cal:', await s.locator('#sTools [data-t="cal"]').count())
    await t.click('#tTools [data-t="cal"]')
    bb = await t.locator('#tBoard .ov').bounding_box(); X = lambda x: bb['x'] + x / 1600 * bb['width']; Y = lambda y: bb['y'] + y / 1000 * bb['height']
    async def stroke(pts):
      await t.mouse.move(X(pts[0][0]), Y(pts[0][1])); await t.mouse.down()
      for x, y in pts[1:]: await t.mouse.move(X(x), Y(y), steps=2)
      await t.mouse.up(); await t.wait_for_timeout(200)
    # baa-like bowl: down-right curve then flat base then up
    ba = [(1100, 300)] + [(1100 - 300 * (a / 20), 300 + 120 * math.sin(a / 20 * math.pi)) for a in range(21)] + [(780, 260)]
    await stroke(ba); await stroke([(1000, 470), (1000, 480)])            # dot
    await stroke([(650, 150), (650, 420)])                                  # alif (vertical)
    await stroke([(150 + i * 25, 600 + 15 * math.sin(i / 3)) for i in range(40)])   # long horizontal
    cir = [(400 + 90 * math.cos(a / 24 * 6.283), 800 + 70 * math.sin(a / 24 * 6.283)) for a in range(25)]
    await stroke(cir)
    print('strokes:', await t.evaluate("[...T.tMap.values()].map(s=>s.t).join(',')"))
    await t.wait_for_timeout(600); await t.screenshot(path=SP + 'cal_t.png'); await s.screenshot(path=SP + 'cal_s.png')
    print('student sees:', await s.evaluate("[...S.tMap.values()].map(s=>s.t).join(',')"))
    print('errors:', errs[:5]); await b.close()
asyncio.run(main())
