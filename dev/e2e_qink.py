import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
RB = len(sys.argv) > 1 and sys.argv[1] == 'rb'
U = 'http://localhost:8790/index.html' if RB else 'http://localhost:8787/'
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []; shared = None
    async def ctx(w=1366, h=768):
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
    code = (await t.inner_text('#tCode')).strip(); S = []
    for nm in ['سارة', 'عمر']:
      s = await (await ctx(420, 820)).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e))); await s.goto(U)
      if RB: await s.evaluate("c=>{localStorage.removeItem('rb_sid_'+c)}", code)
      await s.fill('#jCode', code); await s.wait_for_timeout(900); await s.fill('#jName', nm); await s.click('#jGo'); await s.wait_for_timeout(1000); S.append(s)
    await t.bring_to_front()
    img = await t.evaluate("()=>{const c=document.createElement('canvas');c.width=800;c.height=450;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,800,450);x.fillStyle='#123';x.font='bold 60px sans-serif';x.fillText('24 ÷ 6 = ?',220,240);return c.toDataURL('image/png')}")
    await t.evaluate("img=>startQuiz([{id:'q1',img,ans:'B',kind:'mc',lim:60},{id:'q2',img,ans:'A',kind:'mc',lim:60}])", img); await t.wait_for_timeout(2500)
    for s, o in [(S[0], 'B')]:
      await s.bring_to_front(); await s.click(f'#qsOpts button[data-o="{o}"]'); await s.wait_for_timeout(500)
    await t.bring_to_front(); await t.wait_for_timeout(1200)
    async def drag(x0, y0, x1, y1):
      await t.mouse.move(x0, y0); await t.mouse.down()
      for i in range(1, 15): await t.mouse.move(x0 + (x1 - x0) * i / 14, y0 + (y1 - y0) * i / 14)
      await t.mouse.up()
    ink = await t.evaluate("JSON.stringify(document.querySelector('#rInk').getBoundingClientRect())"); st = await t.evaluate("JSON.stringify(document.querySelector('#rStage').getBoundingClientRect())")
    print('ink bar:', ink, '\nstage:', st)
    await t.click('#rInk [data-it="cal"]'); await drag(100, 300, 600, 420)        # across the answered column and the question
    await t.click('#rInk [data-ic="#2f5bd3"]'); await drag(1200, 500, 1300, 300)
    print('full-screen strokes:', await t.evaluate('QI.map.size'))
    await t.click('#rInk [data-ink="full"]'); await t.click('#rInk [data-it="pen"]'); await t.click('#rInk [data-it="pen"]') if not await t.evaluate('QZ.inkOn') else None
    await drag(500, 450, 800, 450); await t.wait_for_timeout(1200)
    print('question strokes on student device:', await S[0].evaluate('S.qInk ? S.qInk.size : -1'))
    await t.click('#rInk [data-ink="full"]'); await t.click('#rInk [data-it="er"]'); await drag(100, 300, 600, 420)
    print('after eraser strokes:', await t.evaluate('QI.map.size'), 'inkOn', await t.evaluate('QZ.inkOn'))
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'qink.png')
    print('done:', await t.inner_text('#rDone'), '| not:', await t.inner_text('#rNot'))
    print('stage size:', await t.evaluate("JSON.stringify(document.querySelector('#rStage').getBoundingClientRect())"))
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'qside.png')
    await t.click('#rReveal'); await t.wait_for_timeout(1200); await t.screenshot(path=SP + ('rb_' if RB else '') + 'qside_rev.png')
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
