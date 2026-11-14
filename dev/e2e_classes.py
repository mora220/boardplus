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
    print('chip:', await t.inner_text('#tCls'))
    await t.click('#tCls'); await t.wait_for_timeout(500); await t.click('#clsAdd'); await t.wait_for_timeout(300)
    await t.fill('#ceName', 'خامس أ'); await t.fill('#ceNames', 'يوسف أحمد\nسارة خالد\nعمر فهد'); await t.click('#ceOk'); await t.wait_for_timeout(600)
    await t.click('#clsAdd'); await t.wait_for_timeout(300); await t.fill('#ceName', 'خامس ب'); await t.fill('#ceNames', 'علي\nمنى'); await t.click('#ceOk'); await t.wait_for_timeout(600)
    print('modal rows:', await t.locator('.clsi').all_inner_texts())
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'cls_modal.png')
    await t.locator('.clsi', has_text='خامس أ').click(); await t.click('#clsOk'); await t.wait_for_timeout(800)
    print('chip:', await t.inner_text('#tCls'))
    async def join(nm=None, typed=None):
      code = (await t.inner_text('#tCode')).strip()
      s = await (await ctx(420, 820)).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e)))
      await s.goto(U)
      if RB: await s.evaluate("c=>{localStorage.removeItem('rb_sid_'+c)}", code)
      await s.fill('#jCode', code); await s.wait_for_timeout(1500)
      print('  list shown:', await s.locator('#jList .jn').count(), 'name input visible:', await s.locator('#jName').is_visible(), 'btn:', await s.inner_text('#jGo'))
      if nm: await s.screenshot(path=SP + ('rb_' if RB else '') + 'cls_student.png'); await s.locator('#jList .jn', has_text=nm).click()
      else: await s.fill('#jName', typed)
      await s.click('#jGo'); await s.wait_for_timeout(1200); return s
    await join('سارة خالد')
    s2 = await join('عمر فهد')
    # free entry
    await t.bring_to_front(); await t.click('#tCls'); await t.wait_for_timeout(500); await t.locator('.clsi[data-id=""]').click(); await t.click('#clsOk'); await t.wait_for_timeout(800)
    print('chip:', await t.inner_text('#tCls'))
    await join(typed='طالب حر')
    await t.bring_to_front(); await t.wait_for_timeout(800)
    print('teacher sees:', await t.locator('.sc .nm, .sc b, .sc .name').all_inner_texts())
    # new session asks for the class
    await t.click('#tNew'); await t.wait_for_timeout(400)
    if await t.locator('#askOk').count(): await t.click('#askOk')
    await t.wait_for_timeout(1800)
    print('asked:', await t.locator('.dlg h3', has_text='لأي فصل').count())
    await t.locator('.clsi', has_text='خامس ب').click(); await t.click('#clsOk'); await t.wait_for_timeout(800)
    print('chip:', await t.inner_text('#tCls'))
    await join('منى')
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
