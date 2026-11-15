import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
RB = len(sys.argv) > 1 and sys.argv[1] == 'rb'
U = 'http://localhost:8790/index.html' if RB else 'http://localhost:8787/'
PASTE = """async c => { const cv = document.createElement('canvas'); cv.width = 400; cv.height = 300; const x = cv.getContext('2d'); x.fillStyle = c; x.fillRect(0,0,400,300); x.fillStyle='#fff'; x.font='80px sans-serif'; x.fillText(c,40,180);
  const b = await new Promise(r => cv.toBlob(r, 'image/png')); const dt = new DataTransfer(); dt.items.add(new File([b], 'a.png', {type:'image/png'}));
  document.body.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true})) }"""
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
    # class + students
    await t.click('#tCls'); await t.wait_for_timeout(500); await t.click('#clsAdd'); await t.wait_for_timeout(300)
    names = '\n'.join(['يوسف أحمد', 'سارة خالد', 'عمر فهد'] + [f'طالب {i}' for i in range(1, 15)])
    await t.fill('#ceName', 'خامس أ'); await t.fill('#ceNames', names); await t.click('#ceOk'); await t.wait_for_timeout(600); await t.click('#clsOk'); await t.wait_for_timeout(800)
    code = (await t.inner_text('#tCode')).strip()
    s = await (await ctx(420, 820)).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e)))
    await s.goto(U)
    if RB: await s.evaluate("c=>{localStorage.removeItem('rb_sid_'+c)}", code)
    await s.fill('#jCode', code); await s.wait_for_timeout(1500)
    print('search box:', await s.locator('.jsearch').count(), 'names:', await s.locator('#jList .jn').count(), 'input visible:', await s.locator('#jName').is_visible())
    # try to sneak in with a typed name
    await s.evaluate("()=>{const i=document.querySelector('#jName'); i.hidden=false; i.value='اسم غريب'}"); await s.click('#jGo'); await s.wait_for_timeout(1000)
    print('typed name blocked:', await s.inner_text('#jErr'), '| still on join:', await s.locator('#jCode').is_visible())
    await s.locator('#jList .jn', has_text='عمر فهد').click(); await s.click('#jGo'); await s.wait_for_timeout(1500)
    # teacher links him to another name
    await t.bring_to_front(); await t.wait_for_timeout(500)
    await t.locator('.sc', has_text='عمر').locator('.rn').click(); await t.wait_for_timeout(500)
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'link.png')
    await t.locator('.dlg .jn', has_text='يوسف أحمد').click(); await t.wait_for_timeout(1200)
    print('teacher cards:', await t.locator('.sc').all_inner_texts())
    print('student name:', await s.inner_text('#stName'))
    # images
    for c in ['red', 'blue', 'green']: await t.evaluate(PASTE, c); await t.wait_for_timeout(2000)
    print('teacher images:', await t.evaluate("()=>[(T.bg.more||[]).length, !!T.bg.img]"))
    print('student images:', await s.evaluate("()=>[(S.bg.more||[]).length, !!S.bg.img]"))
    await t.screenshot(path=SP + ('rb_' if RB else '') + 'imgs.png')
    # tap the first (red) image in move mode to bring it to the top
    act = await t.evaluate("()=>T.bg.img.src.length"); r = await t.evaluate("()=>{const m=T.bg.more[0];const r=bgRect(m.img,m.tr);return [r.x+r.w/2,r.y+r.h/2]}")
    if not await t.evaluate("()=>IE.on"): await t.evaluate("()=>imgEdit(true)")
    bb = await t.locator('#tBoard').bounding_box(); W, H = await t.evaluate("()=>[W,H]")
    await t.mouse.click(bb['x'] + r[0] / W * bb['width'], bb['y'] + r[1] / H * bb['height']); await t.wait_for_timeout(1500)
    print('after tap:', await t.evaluate("()=>[(T.bg.more||[]).length, T.bg.img.src.length !== %d]" % act))
    await t.evaluate("()=>delActive()"); await t.wait_for_timeout(1500)
    print('after delete:', await t.evaluate("()=>[(T.bg.more||[]).length, !!T.bg.img]"), await s.evaluate("()=>[(S.bg.more||[]).length, !!S.bg.img]"))
    await s.screenshot(path=SP + ('rb_' if RB else '') + 'imgs_s.png')
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
