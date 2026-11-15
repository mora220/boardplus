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
        c = await b.new_context(viewport={'width': w, 'height': h}); await c.route('**/www.gstatic.com/**', lambda r: r.abort()); return c
    t = await (await ctx()).new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher'); await t.click('#gSign'); await t.wait_for_timeout(300)
    await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk'); await t.wait_for_timeout(1500); code = (await t.inner_text('#tCode')).strip()
    st = []
    for nm in ['Sara', 'Omar']:
      s = await (await ctx(400, 820)).new_page(); s.on('pageerror', lambda e, nm=nm: errs.append(nm + ':' + str(e)))
      await s.goto(U); await s.fill('#jCode', code); await s.wait_for_timeout(500); await s.fill('#jName', nm); await s.click('#jGo'); await s.wait_for_timeout(1000); st.append(s)
    s1, s2 = st
    await t.bring_to_front(); await t.click('#tQuiz'); await t.wait_for_timeout(500)
    for i, (txt, a) in enumerate([('7 x 8 = ?', 'B'), ('9 x 6 = ?', 'A'), ('8 x 8 = ?', 'D')]):
      await t.evaluate(PASTE, txt); await t.wait_for_timeout(900); await t.locator('.qcard').nth(i).locator(f'[data-set="{a}"]').click(); await t.wait_for_timeout(250)
    lim = t.locator('.qcard').nth(2).locator('[data-lim]'); await lim.fill('40'); await lim.dispatch_event('change'); await t.wait_for_timeout(300)
    await t.click('#qRace'); await t.wait_for_timeout(2500)
    print('teacher board open:', await t.evaluate("!$('#raceT').hidden"))
    print('student cannot read key:', await s1.evaluate(f"DB.get('sessions/{code}/sqk').then(v=>'LEAK '+JSON.stringify(v)).catch(e=>'denied')"))
    await s1.screenshot(path=SP + 'race_start.png')
    await s1.screenshot(path=SP + 'rg_start.png')
    await s1.click('[data-rg="penalty"]'); await s2.click('[data-rg="balloons"]')
    for s in st: await s.click('#rsGo'); await s.wait_for_timeout(300)
    await s1.wait_for_timeout(1500); await s1.screenshot(path=SP + 'rg_pen.png')
    print('s1 game:', await s1.evaluate("document.querySelector('.rg-world').className"), 'opts:', await s1.locator('.gx-opt').count())
    await s1.click('.gx-opt[data-opt="1"]', force=True); await s1.wait_for_timeout(1300); await s1.screenshot(path=SP + 'rg_pen2.png'); await s1.wait_for_timeout(1500)
    await s2.wait_for_timeout(300); await s2.screenshot(path=SP + 'rg_bal.png'); await s2.click('.bl-cell[data-cell="2"]', force=True); await s2.wait_for_timeout(3200)
    # s1 changes the game on question 2
    await s1.click('[data-rgsw]'); await s1.wait_for_timeout(300); await s1.click('.rg-modal [data-rg="river"]'); await s1.wait_for_timeout(1200)
    print('s1 now:', await s1.evaluate("document.querySelector('.rg-world').className"))
    await s1.screenshot(path=SP + 'rg_riv.png'); await s1.click('.gx-opt[data-opt="0"]', force=True); await s1.wait_for_timeout(3200)
    await s1.click('[data-rgsw]'); await s1.wait_for_timeout(300); await s1.click('.rg-modal [data-rg="space"]'); await s1.wait_for_timeout(1200)
    await s1.screenshot(path=SP + 'rg_sp.png'); await s1.click('.sp-lane[data-lane="3"]', force=True); await s1.wait_for_timeout(400); await s1.click('.sp-go'); await s1.wait_for_timeout(3200)
    print('s1 done:', (await s1.inner_text('#raceS .center')).replace('\n', ' ')[:100])
    await s2.click('[data-rgsw]'); await s2.wait_for_timeout(300); await s2.click('.rg-modal [data-rg="classic"]'); await s2.wait_for_timeout(1200)
    await s2.click('.ropt[data-c="A"]'); await s2.wait_for_timeout(2000)
    print('s1 records:', await s1.evaluate("JSON.stringify(Object.entries(RACE.a[S.sid]).filter(([k])=>/^\\d/.test(k)).map(([k,v])=>[k,v.c,v.ok,v.pts]))"))
    print('s2 records:', await s2.evaluate("JSON.stringify(Object.entries(RACE.a[S.sid]).filter(([k])=>/^\\d/.test(k)).map(([k,v])=>[k,v.c,v.ok,v.pts]))"))
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
