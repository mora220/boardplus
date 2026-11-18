import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    c = await b.new_context(viewport={'width': 1366, 'height': 860}); await c.route('**/www.gstatic.com/**', lambda r: r.abort())
    t = await c.new_page(); t.on('pageerror', lambda e: errs.append(str(e)))
    await t.goto('http://localhost:8787/'); await t.wait_for_timeout(500); await t.click('#toTeacher'); await t.click('#gSign'); await t.wait_for_timeout(300); await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk'); await t.wait_for_timeout(1500)
    code = (await t.inner_text('#tCode')).strip(); S = []
    for vw in [(375, 560), (390, 664), (700, 360)]:
      c2 = await b.new_context(viewport={'width': vw[0], 'height': vw[1]}, is_mobile=vw[0] < 500, has_touch=True); s = await c2.new_page(); s.on('pageerror', lambda e: errs.append(str(e)))
      await s.goto('http://localhost:8787/'); await s.fill('#jCode', code); await s.wait_for_timeout(800); await s.fill('#jName', 'ط' + str(vw[0])); await s.click('#jGo'); await s.wait_for_timeout(900); S.append((vw, s))
    img = await t.evaluate("()=>{const c=document.createElement('canvas');c.width=800;c.height=450;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,800,450);x.fillStyle='#000';x.font='60px sans-serif';x.fillText('24 ÷ 6 = ?',220,240);return c.toDataURL('image/png')}")
    await t.evaluate("img=>startQuiz([{id:'q1',img,ans:'B',kind:'mc',lim:60}])", img); await t.wait_for_timeout(2500)
    for vw, s in S:
      vis = await s.evaluate("[...document.querySelectorAll('#qsOpts button')].map(b=>{const r=b.getBoundingClientRect();return r.bottom<=innerHeight+1 && r.top>=0})")
      print(vw, 'quiz options fully visible:', vis); await s.screenshot(path=SP + f'ph_quiz_{vw[0]}.png')
    await t.evaluate("closeQuiz && closeQuiz()") if await t.evaluate("typeof closeQuiz==='function'") else None
    print('errors:', errs[:4]); await b.close()
asyncio.run(main())
