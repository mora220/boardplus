import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
U = 'http://localhost:8787/'
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    for vw in [(390, 800), (1366, 700)]:
      c = await b.new_context(viewport={'width': vw[0], 'height': vw[1]}); await c.route('**/www.gstatic.com/**', lambda r: r.abort())
      t = await c.new_page(); t.on('pageerror', lambda e: errs.append(str(e)))
      await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher'); await t.click('#gSign'); await t.wait_for_timeout(300)
      await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk'); await t.wait_for_timeout(1500)
      vis = lambda: t.evaluate("['#aiSrc','#aiTopic','#aiShot'].map(q=>{const e=document.querySelector(q);return e?q+':'+(e.offsetParent!==null):q+':none'}).join(' ')")
      btn = t.locator('#tTools use[href="#i-ai"] >> xpath=../..')
      if not await btn.is_visible():
        await t.click('#tTools .more, #tTools [data-more]') if await t.locator('#tTools .more').count() else None
      await btn.click(); await t.wait_for_timeout(300)
      print(vw, 'open:', await vis()); await t.screenshot(path=SP + f'dbg_open_{vw[0]}.png'); print(await t.evaluate("JSON.stringify([...document.querySelectorAll('#aiSrc button, .aih')].map(e=>{const r=e.getBoundingClientRect();return [e.textContent.trim().slice(0,12),Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]}))"))
      for i in range(4): await t.wait_for_timeout(500); print('  t+%.1fs' % ((i+1)*.5), await vis())
      await t.click('#aiSrc [data-s="topic"]'); await t.wait_for_timeout(300); print('  topic:', await vis())
      await t.wait_for_timeout(1500); print('  topic later:', await vis())
      await t.click('#aiMode [data-m="copy"]'); await t.wait_for_timeout(300); print('  copy:', await vis())
      await t.click('#aiSrc [data-s="img"]'); await t.wait_for_timeout(300); print('  img:', await vis())
      await t.screenshot(path=SP + f'dbg_ai_{vw[0]}.png')
      await c.close()
    print('errors', errs[:4]); await b.close()
asyncio.run(main())
