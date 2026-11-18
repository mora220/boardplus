import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    c = await b.new_context(viewport={'width': 1366, 'height': 860}); await c.route('**/www.gstatic.com/**', lambda r: r.abort())
    t = await c.new_page(); t.on('pageerror', lambda e: errs.append(str(e)))
    await t.goto('http://localhost:8787/'); await t.wait_for_timeout(500); await t.click('#toTeacher'); await t.click('#gSign'); await t.wait_for_timeout(300); await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk'); await t.wait_for_timeout(1500)
    code = (await t.inner_text('#tCode')).strip(); S = []
    for nm in ['سارة', 'عمر']:
      c2 = await b.new_context(viewport={'width': 420, 'height': 800}); s = await c2.new_page(); await s.goto('http://localhost:8787/'); await s.fill('#jCode', code); await s.wait_for_timeout(800); await s.fill('#jName', nm); await s.click('#jGo'); await s.wait_for_timeout(900); S.append((c2, s))
    await S[1][0].close(); await t.wait_for_timeout(2500)
    print('online:', await t.evaluate('onlineCount()'), 'all:', await t.evaluate('T.st.size'))
    img = await t.evaluate("()=>{const c=document.createElement('canvas');c.width=800;c.height=450;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,800,450);return c.toDataURL('image/png')}")
    await t.evaluate("img=>startQuiz([{id:'q1',img,ans:'B',kind:'mc',lim:15}])", img); await t.wait_for_timeout(2500)
    await S[0][1].click('#qsOpts button[data-o="B"]'); await t.wait_for_timeout(3000)
    print('phase after the online student answered:', await t.evaluate('QZ.run && QZ.run.phase'))
    await t.wait_for_timeout(12000); print('phase after the time:', await t.evaluate('QZ.run && QZ.run.phase'))
    print('errors:', errs); await b.close()
asyncio.run(main())
