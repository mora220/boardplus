import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
U = 'http://localhost:8787/'
PASTE = '''(t)=>{const c=document.createElement('canvas');c.width=1000;c.height=600;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,1000,600);x.fillStyle='#000';x.font='bold 70px sans-serif';x.fillText(t,80,320);
  return new Promise(r=>c.toBlob(bl=>{const dt=new DataTransfer();dt.items.add(new File([bl],'q.png',{type:'image/png'}));document.body.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true}));r()}))}'''
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    async def ctx(w=1366, h=860):
        c = await b.new_context(viewport={'width': 683 if w > 1000 else 600, 'height': 430 if w > 1000 else 430}); await c.route('**/www.gstatic.com/**', lambda r: r.abort()); return c
    t = await (await ctx()).new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher'); await t.click('#gSign'); await t.wait_for_timeout(300)
    await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk'); await t.wait_for_timeout(1500); code = (await t.inner_text('#tCode')).strip()
    st = []
    for nm in ['سارة', 'عمر', 'يوسف', 'منى']:
      s = await (await ctx(400, 820)).new_page(); s.on('pageerror', lambda e, nm=nm: errs.append(nm + ':' + str(e)))
      await s.goto(U); await s.fill('#jCode', code); await s.wait_for_timeout(500); await s.fill('#jName', nm); await s.click('#jGo'); await s.wait_for_timeout(900); st.append(s)
    await t.bring_to_front(); await t.click('#tQuiz'); await t.wait_for_timeout(500)
    Q = [('7 x 8 = ?', 'B'), ('9 x 6 = ?', 'A'), ('8 x 8 = ?', 'D'), ('6 x 6 = ?', 'C')]
    for i, (txt, a) in enumerate(Q):
      await t.evaluate(PASTE, txt); await t.wait_for_timeout(900); await t.locator('.qcard').nth(i).locator(f'[data-set="{a}"]').click(); await t.wait_for_timeout(250)
    print('buttons:', await t.locator('#qzBuild header .btn').all_inner_texts())
    await t.click('#qTug'); await t.wait_for_timeout(2500)
    team = await t.evaluate("JSON.stringify(RACE.sq.team)"); print('team:', team)
    await st[0].screenshot(path=SP + 'sp_tug_s_start.png')
    for s in st: await s.click('#rsGo'); await s.wait_for_timeout(200)
    await t.wait_for_timeout(1500); await t.screenshot(path=SP + 'sp_tug_t0.png'); await st[0].screenshot(path=SP + 'sp_stu_q.png'); await st[0].screenshot(path=SP + 'sp_tug_s0.png'); print('errs so far', errs)
    sids = await t.evaluate("JSON.stringify(Object.fromEntries([...T.st].map(([k,v])=>[v.info.name,k])))")
    import json; sids = json.loads(sids); team = json.loads(team)
    reds = [i for i, nm in enumerate(['سارة', 'عمر', 'يوسف', 'منى']) if team[sids[nm]] == 'r']
    print('reds:', reds)
    # the red team answers right, the blue team wrong
    for q in range(4):
      for i, s in enumerate(st):
        right = Q[q][1] if i in reds else ('A' if Q[q][1] != 'A' else 'B')
        try: await s.click(f'.ropt[data-c="{right}"]', timeout=3000)
        except Exception: print('  (no question for', i, 'at q', q, ')')
      await t.wait_for_timeout(700)
      if q == 0:
        await t.wait_for_timeout(800); await t.screenshot(path=SP + 'sp_an_t.png')
        print('q chips:', [x.replace('\n', ' ') for x in await t.locator('#tgAn .anqs .anq').all_inner_texts()])
        print('students:', [x.replace('\n', ' ') for x in await t.locator('#tgAn .anst').all_inner_texts()])
        await t.click('#tgAn .anqs [data-rq="0"]'); await t.wait_for_timeout(800)
        bb = await t.locator('.rq-view .rqb').bounding_box()
        await t.mouse.move(bb['x'] + 200, bb['y'] + 200); await t.mouse.down(); await t.mouse.move(bb['x'] + 420, bb['y'] + 260, steps=10); await t.mouse.up()
        await t.click('.rq-view [data-a="rev"]'); await t.wait_for_timeout(300)
        print('view head:', (await t.inner_text('.rq-view .rqh')).replace('\n', ' '), '| opts:', (await t.inner_text('.rq-view .rqopts')).replace('\n', ' '))
        await t.screenshot(path=SP + 'sp_an_view.png'); await t.click('.rq-view [data-a="x"]')
      await t.wait_for_timeout(1300)
    await t.wait_for_timeout(2500)
    print('sq:', await t.evaluate("JSON.stringify({st:RACE.sq.st, win:RACE.sq.win})"), 'state:', await t.evaluate("JSON.stringify(tugState(RACE.sq,RACE.a))"))
    await t.screenshot(path=SP + 'sp_tug_end.png'); await st[reds[0]].screenshot(path=SP + 'sp_tug_s_win.png')
    if await t.locator('#tgHard').count():
      await t.click('#tgHard'); await t.wait_for_timeout(800); print('hard view:', (await t.inner_text('.rq-view .rqh')).replace('\n', ' ')[:80]); await t.screenshot(path=SP + 'sp_an_hard.png'); await t.click('.rq-view [data-a="x"]')
    await t.screenshot(path=SP + 'sp_an_end.png')
    print('student end:', (await st[reds[0]].inner_text('#raceS .center')).replace('\n', ' ')[:120])
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
