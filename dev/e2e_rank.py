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
    for nm in ['سارة', 'عمر', 'يوسف', 'منى', 'علي', 'هند', 'خالد']:
      s = await (await ctx(420, 820)).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e))); await s.goto(U)
      if RB: await s.evaluate("c=>{localStorage.removeItem('rb_sid_'+c)}", code)
      await s.fill('#jCode', code); await s.wait_for_timeout(900); await s.fill('#jName', nm); await s.click('#jGo'); await s.wait_for_timeout(1000); S.append(s)
    await t.bring_to_front()
    img = await t.evaluate("()=>{const c=document.createElement('canvas');c.width=800;c.height=450;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,800,450);x.fillStyle='#123';x.font='bold 60px sans-serif';x.fillText('24 ÷ 6 = ?',220,240);return c.toDataURL('image/png')}")
    await t.evaluate("img=>startQuiz([{id:'q1',img,ans:'B',kind:'mc',lim:60},{id:'q2',img,ans:'A',kind:'mc',lim:60}])", img); await t.wait_for_timeout(2500)
    for s, o in [(S[0], 'B'), (S[1], 'A'), (S[2], 'B'), (S[3], 'B'), (S[4], 'C')]:
      await s.bring_to_front(); await s.click(f'#qsOpts button[data-o="{o}"]'); await s.wait_for_timeout(500)
    await t.bring_to_front(); await t.wait_for_timeout(1200)
    print('done:', await t.inner_text('#rDone'), '| not:', await t.inner_text('#rNot'))
    print('stage size:', await t.evaluate("JSON.stringify(document.querySelector('#rStage').getBoundingClientRect())"))
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'qside.png')
    await t.click('#rReveal'); await t.wait_for_timeout(1200)
    print('ok/bad marks shown:', await t.locator('#rDone .qn.ok, #rDone .qn.bad, #rWho .ach.ok, #rWho .ach.bad').count())
    await t.click('#rNext'); await t.wait_for_timeout(1500)
    print('rank rows:', [x.replace('\n',' ') for x in await t.locator('#rRank .lr').all_inner_texts()])
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'rank.png')
    print('student rank (عمر):', await S[1].inner_text('#qsRankT'), '| rows:', await S[1].locator('#qsRank .lr').count())
    await t.evaluate('finishQuiz()'); await t.wait_for_timeout(1500)
    print('podium:', [x.replace('\n',' ') for x in await t.locator('#lbPod .pd').all_inner_texts()], '| list rows:', await t.locator('#lbList .lr').count())
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'lb.png')
    print('student lb (عمر):', await S[1].inner_text('#lbMe'))
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
