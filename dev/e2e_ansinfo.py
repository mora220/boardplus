import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
RB = len(sys.argv) > 1 and sys.argv[1] == 'rb'
U = 'http://localhost:8790/index.html' if RB else 'http://localhost:8787/'
PASTE = """async txt => { const cv = document.createElement('canvas'); cv.width = 600; cv.height = 300; const x = cv.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0,0,600,300); x.fillStyle='#000'; x.font='48px sans-serif'; x.fillText(txt,40,170);
  const b = await new Promise(r => cv.toBlob(r, 'image/png')); const dt = new DataTransfer(); dt.items.add(new File([b], 'q.png', {type:'image/png'}));
  document.querySelector('#qzBuild').dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true})) }"""
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []; shared = None
    async def ctx(w=1366, h=860):
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
    await t.click('#tCls'); await t.wait_for_timeout(400); await t.click('#clsAdd'); await t.wait_for_timeout(300)
    await t.fill('#ceName', 'خامس أ'); await t.fill('#ceNames', 'سارة\nعمر\nيوسف\nمنى'); await t.click('#ceOk'); await t.wait_for_timeout(600); await t.click('#clsOk'); await t.wait_for_timeout(700)
    code = (await t.inner_text('#tCode')).strip(); S = []
    for nm in ['سارة', 'عمر', 'يوسف', 'منى']:
      s = await (await ctx(420, 820)).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e))); await s.goto(U)
      if RB: await s.evaluate("c=>{localStorage.removeItem('rb_sid_'+c)}", code)
      await s.fill('#jCode', code); await s.wait_for_timeout(1200); await s.locator('#jList .jn', has_text=nm).click(); await s.click('#jGo'); await s.wait_for_timeout(900); S.append(s)
    await t.bring_to_front(); await t.click('#tQuiz'); await t.wait_for_timeout(500)
    for i, (txt, a) in enumerate([('7 x 8 = ?', 'B'), ('9 x 6 = ?', 'A')]):
      await t.evaluate(PASTE, txt); await t.wait_for_timeout(900); await t.locator('.qcard').nth(i).locator(f'[data-set="{a}"]').click(); await t.wait_for_timeout(300)
    on_bg = await t.evaluate("getComputedStyle(document.querySelector('.qcard .abcd button.on')).backgroundColor")
    off_bg = await t.evaluate("getComputedStyle(document.querySelector('.qcard .abcd button:not(.on)')).backgroundColor")
    print('hidden: correct looks like others:', on_bg == off_bg); await t.screenshot(path=SP + ('rb_' if RB else '') + 'ans_hidden.png')
    await t.click('#qAns'); await t.wait_for_timeout(200)
    print('shown: correct highlighted:', await t.evaluate("getComputedStyle(document.querySelector('.qcard .abcd button.on')).backgroundColor") != off_bg, await t.inner_text('#qAns'))
    await t.click('#qClose'); await t.wait_for_timeout(300)
    sids = await t.evaluate("JSON.stringify([...T.st.keys()])"); import json; sids = json.loads(sids)
    await t.evaluate("ids => DB.update(`sessions/${T.code}/qpts`, {[ids[0]+'/x']:5,[ids[1]+'/x']:5,[ids[2]+'/x']:3})", sids); await t.wait_for_timeout(800)
    await t.evaluate("openTeacherLB()"); await t.wait_for_timeout(800)
    print('teacher info:', await t.inner_text('#lbInfo'), '| teacher rank visible:', await t.locator('#lbMe').is_visible())
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'lb_info.png')
    await t.click('#lbShow'); await t.wait_for_timeout(1500)
    for s in S: print('student:', await s.inner_text('#lbMe'))
    await S[3].screenshot(path=SP + ('rb_' if RB else '') + 'lb_student.png')
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
