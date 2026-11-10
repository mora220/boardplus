import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
U = 'http://localhost:8787/'
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); errs = []
    async def ctx():
        c = await b.new_context(viewport={'width': 1366, 'height': 860}); await c.route('**/www.gstatic.com/**', lambda r: r.abort())
        await c.route('**/youtube-nocookie.com/**', lambda r: r.fulfill(body='<h1>YT</h1>', content_type='text/html'))
        await c.route('**/view.officeapps.live.com/**', lambda r: r.fulfill(body='<h1>OFFICE</h1>', content_type='text/html'))
        return c
    t = await (await ctx()).new_page(); t.on('pageerror', lambda e: errs.append('T:' + str(e)))
    await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher'); await t.click('#gSign'); await t.wait_for_timeout(300)
    await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk'); await t.wait_for_timeout(1500); code = (await t.inner_text('#tCode')).strip()
    s = await (await ctx()).new_page(); s.on('pageerror', lambda e: errs.append('S:' + str(e))); await s.set_viewport_size({'width': 900, 'height': 800})
    await s.goto(U); await s.fill('#jCode', code); await s.wait_for_timeout(600); await s.fill('#jName', 'Sara'); await s.click('#jGo'); await s.wait_for_timeout(1500)
    # English lines background
    await t.click('#tTools use[href="#i-bg"] >> xpath=../..'); await t.wait_for_timeout(300); await t.click('[data-b="en"]'); await t.wait_for_timeout(800)
    print('student bg:', await s.evaluate('S.bg.type'))
    # upload audio
    open_show = lambda: t.click('#tTools use[href="#i-show"] >> xpath=../..')
    await open_show(); await t.wait_for_timeout(300)
    async with t.expect_file_chooser() as fc: await t.click('#shDrop')
    await (await fc.value).set_files(SP + 'listen.wav'); await t.wait_for_timeout(3000)
    src = await s.evaluate("(document.querySelector('.showov audio')||{}).src")
    print('student audio src:', src)
    r = await t.request.get(src, headers={'range': 'bytes=100-199'}); print('range request:', r.status, r.headers.get('content-range'), len(await r.body()))
    await t.screenshot(path=SP + 'show_audio_t.png'); await s.screenshot(path=SP + 'show_audio_s.png')
    await t.evaluate("document.querySelector('.showov audio').play()"); await t.wait_for_timeout(2500)
    print('student playing:', await s.evaluate("(a=>[!a.paused, Math.round(a.currentTime*10)/10])(document.querySelector('.showov audio'))"), '| teacher time', await t.evaluate("Math.round(document.querySelector('.showov audio').currentTime*10)/10"))
    await t.evaluate("(a=>{a.pause(); a.currentTime=12})(document.querySelector('.showov audio'))"); await t.wait_for_timeout(1500)
    print('after teacher pause+seek, student:', await s.evaluate("(a=>[a.paused, Math.round(a.currentTime)])(document.querySelector('.showov audio'))"))
    # youtube link
    await open_show(); await t.wait_for_timeout(300); await t.fill('#shUrl', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30'); await t.click('#shGo'); await t.wait_for_timeout(1500)
    print('student iframe:', await s.evaluate("(document.querySelector('.showov iframe')||{}).src"))
    await s.screenshot(path=SP + 'show_yt_s.png')
    await s.click('.showov [data-a="mini"]'); await s.wait_for_timeout(300); await s.screenshot(path=SP + 'show_yt_mini.png')
    # pptx upload
    await open_show(); await t.wait_for_timeout(300)
    async with t.expect_file_chooser() as fc: await t.click('#shDrop')
    await (await fc.value).set_files(SP + 'lesson.pptx'); await t.wait_for_timeout(2500)
    print('pptx iframe:', (await s.evaluate("(document.querySelector('.showov iframe')||{}).src"))[:110])
    # end
    await t.click('.showov [data-a="end"]'); await t.wait_for_timeout(1000)
    print('closed for student:', await s.evaluate("document.querySelector('.showov').hidden"))
    await t.screenshot(path=SP + 'show_en_bg.png')
    print('errors:', errs[:6]); await b.close()
asyncio.run(main())
