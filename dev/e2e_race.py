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
    lim = t.locator('.qcard').nth(2).locator('[data-lim]'); await lim.fill('5'); await lim.dispatch_event('change'); await t.wait_for_timeout(300)
    await t.click('#qRace'); await t.wait_for_timeout(2500)
    print('teacher board open:', await t.evaluate("!$('#raceT').hidden"))
    print('student cannot read key:', await s1.evaluate(f"DB.get('sessions/{code}/sqk').then(v=>'LEAK '+JSON.stringify(v)).catch(e=>'denied')"))
    await s1.screenshot(path=SP + 'race_start.png')
    for s in st: await s.click('#rsGo'); await s.wait_for_timeout(300)
    await s1.wait_for_timeout(1200); await s1.screenshot(path=SP + 'race_q.png'); print('at point:', await s1.evaluate("(()=>{const e=document.elementFromPoint(200,120);return e.tagName+'#'+e.id+'.'+e.className+' parent:'+e.parentElement.className})()")); print('img box', await s1.evaluate("JSON.stringify(document.querySelector('#raceS img').getBoundingClientRect())"))
    await s1.click('.ropt[data-c="B"]'); await s1.wait_for_timeout(400); await s1.screenshot(path=SP + 'race_fb.png'); await s1.wait_for_timeout(1500)
    await s2.click('.ropt[data-c="C"]'); await s2.wait_for_timeout(1800)
    await s1.click('.ropt[data-c="A"]'); await s1.wait_for_timeout(1900)
    print('s1 on q3 top bar:', (await s1.inner_text('#raceS .rtop')).replace('\n', ' '))
    await s1.click('.ropt[data-c="D"]'); await s1.wait_for_timeout(1800)
    print('s1 done screen:', (await s1.inner_text('#raceS .center')).replace('\n', ' ')[:120])
    await s2.click('.ropt[data-c="A"]'); await s2.wait_for_timeout(1700)
    await s2.wait_for_timeout(7000)   # q3 lim 5s -> timeout
    print('s2 records:', await s2.evaluate("JSON.stringify(Object.entries(RACE.a[S.sid]).filter(([k])=>/^\\d/.test(k)).map(([k,v])=>[k,v.c,v.ok,v.pts]))"))
    await t.screenshot(path=SP + 'race_teacher.png')
    print('teacher table:', [r.replace('\n', ' ').replace('\t', ' ') for r in await t.locator('#raceT tr').all_inner_texts()])
    await t.click('#rcEnd'); await t.wait_for_timeout(300); await t.click('#askOk'); await t.wait_for_timeout(1500)
    print('s1 final:', (await s1.inner_text('#raceS .center')).replace('\n', ' ')[:80], '| qpts:', await t.evaluate('JSON.stringify(T.qpts)'))
    await t.screenshot(path=SP + 'race_end.png'); await s1.screenshot(path=SP + 'race_end_s.png')
    await t.click('#rcClose'); await t.wait_for_timeout(1000)
    print('closed for student:', await s1.evaluate("$('#raceS').hidden"))
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
