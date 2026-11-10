import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-claude/7249022e-f10e-578d-90c1-67166593e5d6/scratchpad/bp/'
U = 'http://localhost:8787/'
MOCK = '''()=>{ window.__req=[]; const of=window.fetch; window.fetch=async (u,o)=>{ u=String(u);
  if(u.includes('generativelanguage')){ window.__req.push([u,o&&o.body]);
    if(u.includes('/models?')) return new Response(JSON.stringify({models:[{name:'models/gemini-2.5-flash',supportedGenerationMethods:['generateContent']}]}),{status:200});
    const qs=[{type:'mc',q:'ناتج ٨٤ ÷ ١٢ = ؟',options:['٦','٧','٨','٩'],answer:1},{type:'tf',q:'ناتج ٩٦ ÷ ٣٢ = ٣',answer:true},{type:'mc',q:'ناتج ١٤٤ ÷ ١٢ = ؟',options:['١٠','١١','١٢','١٤'],answer:2}];
    return new Response(JSON.stringify({candidates:[{content:{parts:[{text:JSON.stringify(qs)}]}}]}),{status:200}) }
  return of(u,o) } }'''
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); errs = []
    c = await b.new_context(viewport={'width': 1366, 'height': 860}); await c.route('**/www.gstatic.com/**', lambda r: r.abort())
    t = await c.new_page(); t.on('pageerror', lambda e: errs.append(str(e)))
    await t.goto(U); await t.wait_for_timeout(500); await t.click('#toTeacher'); await t.click('#gSign'); await t.wait_for_timeout(300)
    await t.fill('#atxt', 'admin@test.dev'); await t.click('#atOk'); await t.wait_for_timeout(1500)
    await t.evaluate(MOCK)
    await t.click('#tTools use[href="#i-ai"] >> xpath=../..'); await t.wait_for_timeout(500)
    await t.click('#aiSrc [data-s="topic"]'); await t.wait_for_timeout(200)
    print('photo box hidden:', await t.evaluate("$('#aiShot').hidden"), '| topic box shown:', await t.evaluate("!$('#aiTopic').hidden"))
    await t.fill('#aiSubj', 'رياضيات'); await t.fill('#aiLesson', 'القسمة على عدد من رقمين'); await t.fill('#aiLevel', 'الصف الخامس')
    await t.fill('#gmKey', 'AIzaTEST'); await t.screenshot(path=SP + 'ai_topic.png')
    await t.uncheck('#aiAuto'); await t.click('#aiGo'); await t.wait_for_timeout(2000)
    req = await t.evaluate('window.__req'); gen = [json.loads(r[1]) for r in req if r[1]]
    parts = gen[0]['contents'][0]['parts']
    print('parts sent:', [list(x.keys())[0] for x in parts]); print('prompt starts:', parts[-1]['text'][:120].replace('\n', ' '))
    print('questions in bank:', await t.evaluate('DB.get(BANK()+"/qbank").then(v=>Object.keys(v||{}).length)'), '| dialog closed:', await t.evaluate("!document.querySelector('#aiGo')"))
    # empty lesson -> error
    await t.click('#tTools use[href="#i-ai"] >> xpath=../..'); await t.wait_for_timeout(400); await t.fill('#aiLesson', ''); await t.click('#aiGo'); await t.wait_for_timeout(400)
    print('empty lesson error:', await t.inner_text('#aiErr'))
    print('errors:', errs[:5]); await b.close()
asyncio.run(main())
