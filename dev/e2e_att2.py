import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
RB = len(sys.argv) > 1 and sys.argv[1] == 'rb'
U = 'http://localhost:8790/index.html' if RB else 'http://localhost:8787/'
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
    async def addc(n, ns):
      await t.click('#clsAdd'); await t.wait_for_timeout(300); await t.fill('#ceName', n); await t.fill('#ceNames', ns); await t.click('#ceOk'); await t.wait_for_timeout(600)
    await t.click('#tCls'); await t.wait_for_timeout(500); await addc('خامس أ', 'سارة\nعمر\nيوسف'); await addc('خامس ب', 'علي\nمنى')
    await t.locator('.clsi', has_text='خامس أ').click(); await t.click('#clsOk'); await t.wait_for_timeout(800)
    async def join(nm):
      code = (await t.inner_text('#tCode')).strip()
      s = await (await ctx(420, 820)).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e)))
      await s.goto(U)
      if RB: await s.evaluate("c=>{localStorage.removeItem('rb_sid_'+c)}", code)
      await s.fill('#jCode', code); await s.wait_for_timeout(1500); await s.locator('#jList .jn', has_text=nm).click(); await s.click('#jGo'); await s.wait_for_timeout(1200)
    await join('سارة'); await join('عمر'); await t.bring_to_front(); await t.wait_for_timeout(5000)
    print('A st:', await t.evaluate("async()=>[T.st.size, ATT.code, ATT.skip, JSON.stringify(await DB.get(BANK()+'/att'))]"))
    await t.click('#tNew'); await t.wait_for_timeout(400)
    if await t.locator('#askOk').count(): await t.click('#askOk')
    await t.wait_for_timeout(1800); await t.locator('.clsi', has_text='خامس ب').click(); await t.click('#clsOk'); await t.wait_for_timeout(800)
    await join('علي'); await t.bring_to_front(); await t.wait_for_timeout(5500)
    ext = lambda ic: t.click(f'#tTools use[href="#i-{ic}"] >> xpath=../..')
    await ext('trophy'); await t.wait_for_timeout(1200)
    print("att:", await t.evaluate("async()=>JSON.stringify(Object.values(await DB.get(BANK()+'/att')||{}).map(r=>[r.code,r.cls&&r.cls.name,(r.s||[]).length]))"))
    print('class B:', [r.replace('\t', '|') for r in await t.locator('#atT tr').all_inner_texts()])
    await t.select_option('#atC', label='👥 خامس أ'); await t.wait_for_timeout(400)
    print('class A:', [r.replace('\t', '|') for r in await t.locator('#atT tr').all_inner_texts()])
    await t.locator('#atT td.ab').first.click(); await t.wait_for_timeout(600)
    print('A after marking يوسف present:', [r.replace('\t', '|') for r in await t.locator('#atT tr').all_inner_texts()])
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'att2.png')
    await t.click('.attdel'); await t.wait_for_timeout(300); await t.click('#askOk'); await t.wait_for_timeout(800)
    print('A after delete:', [r.replace('\t', '|') for r in await t.locator('#atT tr').all_inner_texts()])
    await t.select_option('#atC', label='👥 خامس ب'); await t.wait_for_timeout(400); await t.locator('#atT td.ab').first.click(); await t.wait_for_timeout(600)
    await t.evaluate("()=>{ATT.t=0; attSync(true)}"); await t.wait_for_timeout(800)
    print('live B after manual + sync:', await t.evaluate("async()=>JSON.stringify(Object.values(await DB.get(BANK()+'/att')).map(r=>[r.cls.name, r.man]))"))
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
