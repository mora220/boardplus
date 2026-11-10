import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
U = 'http://localhost:8787/'
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    async def ctx():
        c = await b.new_context(viewport={'width': 1366, 'height': 860}); await c.route('**/www.gstatic.com/**', lambda r: r.abort()); return c
    t = await (await ctx()).new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher'); await t.click('#gSign'); await t.wait_for_timeout(300)
    await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk'); await t.wait_for_timeout(1500); code = (await t.inner_text('#tCode')).strip()
    texts = ['My name is Sara. I like reading books and playing with my cat.', 'Yesterday I went to the park with my family. We had a picnic.', 'My favourite subject is English because I love stories.']
    for i, txt in enumerate(texts):
      s = await (await ctx()).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e))); await s.set_viewport_size({'width': 1000, 'height': 800})
      await s.goto(U); await s.fill('#jCode', code); await s.wait_for_timeout(500); await s.fill('#jName', ['Sara', 'Omar', 'Lina'][i]); await s.click('#jGo'); await s.wait_for_timeout(1200)
      await s.click('#sTools [data-t="text"]'); bb = await s.locator('#sBoard .ov').bounding_box(); await s.mouse.click(bb['x'] + 60, bb['y'] + 80); await s.wait_for_timeout(300)
      if i == 0: print('textarea attrs:', await s.evaluate("(t=>[t.spellcheck,t.getAttribute('autocorrect'),t.getAttribute('autocapitalize')])(document.querySelector('textarea.tx'))"))
      await s.keyboard.type(txt); await s.mouse.click(bb['x'] + 600, bb['y'] + 500); await s.wait_for_timeout(600)
    await t.wait_for_timeout(800); await t.click('#sizeSeg [data-c="3"]'); await t.wait_for_timeout(800); await t.screenshot(path=SP + 'big3.png')
    await t.click('#sizeSeg [data-c="2"]'); await t.wait_for_timeout(600); await t.screenshot(path=SP + 'big2.png')
    print('gridmode on:', await t.evaluate("document.body.classList.contains('gridmode')"))
    print('errors:', errs[:5]); await b.close()
asyncio.run(main())
