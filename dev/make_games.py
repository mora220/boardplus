#!/usr/bin/env python3
"""Build public/games.html (BoardPlus Games) from the QuizRagab source (dev/games_src.html)."""
import re, json, pathlib
D = pathlib.Path(__file__).resolve().parent
s = (D / 'games_src.html').read_text()

def rep(a, b, cnt=1):
    global s
    n = s.count(a); assert n == cnt, (n, a[:90]); s = s.replace(a, b)
def rep_block(start, end, new):
    global s
    a = s.index(start); b = s.index(end, a); s = s[:a] + new + s[b:]

LOGO_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect x="2" y="2" width="44" height="44" rx="12" fill="#2f5bd3"/><rect x="10" y="12" width="28" height="19" rx="3" fill="#fff"/><path d="M15 25l5 4 10-11" fill="none" stroke="#e0242f" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M24 34.5v8M20 38.5h8" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
import base64
LOGO_URI = 'data:image/svg+xml;base64,' + base64.b64encode(LOGO_SVG.encode()).decode()

rep('<title>QuizRagab</title>', '<title>BoardPlus Games</title><link rel="icon" href="favicon.svg" type="image/svg+xml">')
s = re.sub(r'<div class="logo-pill"><img src="data:image/png;base64,[^"]+"', f'<div class="logo-pill"><img src="{LOGO_URI}"', s, count=1)
rep('<div class="brand"><b>QuizRagab</b><small>منصة الألعاب التفاعلية • وحدة القسمة • الصف الخامس</small></div>',
    '<div class="brand"><b>BoardPlus Games</b><small>ألعاب ومسابقات الحصة التفاعلية</small></div>')
s = re.sub(r'<div class="me"><img src="data:image/jpeg;base64,[^"]+"([^>]*)><span>[^<]*<br><b>[^<]*</b></span></div>',
           f'<div class="me"><img src="{LOGO_URI}" alt="BoardPlus"><span>من<br><b>BoardPlus</b></span></div>', s, count=1)
assert 'class="me"><img src="data:image/svg' in s
rep('<p class="foot">منصة QuizRagab (كويز رجب) من إعداد المعلم محمد رجب لطلاب مدارس منارات الرياض</p>', '<p class="foot">BoardPlus Games · فكرة وتطوير أ. محمد رجب</p>')
rep('<script>\n', '<script src="rt.js"></script>\n<script>\n', cnt=s.count('<script>\n'))   # rt.js before each inline script (harmless twice)
s = s.replace('<script src="rt.js"></script>\n<script>\n', '<script>\n', 1) if s.count('<script src="rt.js"></script>') > 1 else s

# credentials & firebase config are no longer used
rep("const ADMIN_USER = 'ragab';\nconst ADMIN_PASS = 'Ra26388';\n", '')
s = re.sub(r"const FIREBASE_CONFIG = \{.*?\};\n", 'const FIREBASE_CONFIG = null;\n', s, count=1, flags=re.S)

# store → BoardPlus rooms
rep_block('async function initStore(){', 'const sp = (code, rest', r'''async function initStore(){
  const PREVIEW = /claude|anthropic/.test(location.hostname) || location.protocol === 'file:' || !window.RT;
  if(PREVIEW) Store = makeDemo();
  else {
    const route = p => { const s = String(p).split('/').filter(Boolean); return [RT.room('g:' + s[2]), s.slice(3).join('/')] };
    const fail = e => { console.error(e); toast('تعذّر الحفظ. تأكد من الإنترنت.'); throw e };
    Store = {
      mode: 'firebase', cfgSrc: 'code',
      on(p, cb){ const [r, x] = route(p); return r.onValue(x, cb) },
      set: (p, v) => { const [r, x] = route(p); return r.set(x, clean(v)).catch(fail) },
      update: (p, o) => { const [r, x] = route(p); return r.update(x, clean(o)).catch(fail) },
      remove: p => { const [r, x] = route(p); return r.remove(x).catch(fail) },
      get: p => { const s = String(p).split('/').filter(Boolean); return RT.get('g:' + s[2], s.slice(3).join('/')) },
      now: () => RT.now(),
    };
  }
  const tag = $('#modeTag');
  if(Store.mode === 'demo'){ tag.hidden = false; tag.textContent = 'معاينة' }
}
''')
rep("function isTeacher(){ return teacherAuthed || ssGet('rc_admin') === '1' || ssGet('rb_admin') === '1' }", "function isTeacher(){ return ssGet('rb_admin') === '1' || (Store && Store.mode === 'demo' && ssGet('rc_admin') === '1') }")
rep_block('function showLogin(){', 'function settingsHTML(set){', r'''function showLogin(){
  if(isTeacher()) return showDash();
  mount('login', `
  <section class="card stack" style="max-width:460px;margin-inline:auto;text-align:center;align-items:center">
    <h2>للمعلمين</h2>
    <p class="muted" style="margin:0">سجّل دخولك في BoardPlus، وابدأ أي لعبة من زر الألعاب داخل سبورتك. طلابك يدخلونها تلقائيًا.</p>
    <div class="row" style="justify-content:center"><a class="btn primary big" href="./#teacher">الذهاب إلى BoardPlus</a>${Store.mode === 'demo' ? '<button class="btn ghost" type="button" id="demoT">تجربة هنا</button>' : ''}<button class="btn ghost" type="button" id="back">رجوع</button></div>
  </section>`);
  $('#back').onclick = showHome;
  const dt = $('#demoT'); if(dt) dt.onclick = () => { ssSet('rc_admin', '1'); showDash() };
}
''')
rep('<div class="row"><h2 class="spacer">أهلاً أستاذ محمد</h2>', '<div class="row"><h2 class="spacer">أهلًا بك</h2>')
rep('      <button class="btn ghost sm" id="cfgBtn" type="button">إعدادات الاتصال</button>\n', '')
rep("  $('#cfgBtn').onclick = showCfg;\n", '')
rep('متصل بقاعدة بيانات السبورة (ragabboard). الجلسات تعمل الآن على أجهزة الطلاب.', 'الألعاب متصلة، وتشتغل الآن على أجهزة الطلاب.')
rep('<div class="who"><img src="${TEACHER_PHOTO}" alt=""><div><b>المعلم محمد رجب</b><span>لطلاب مدارس منارات الرياض</span></div></div>',
    '<div class="who"><img src="${TEACHER_PHOTO}" alt=""><div><b>BoardPlus Games</b><span>ألعاب الحصة لكل معلم وطالب</span></div></div>')
rep('ألعاب ومسابقات تفاعلية مباشرة لأي درس: أسئلة وحدة القسمة الجاهزة، أو أسئلتك من رجب بورد ومن الذكاء الاصطناعي.', 'ألعاب ومسابقات تفاعلية مباشرة لأي درس: أسئلتك من BoardPlus ومن الذكاء الاصطناعي، أو أمثلة جاهزة في القسمة.')
rep("$('#logout').onclick = () => { teacherAuthed = false; try{ sessionStorage.removeItem('rc_admin') }catch(e){}", "$('#logout').onclick = () => { teacherAuthed = false; try{ sessionStorage.removeItem('rc_admin'); sessionStorage.removeItem('rb_admin') }catch(e){}")

ADD = {
 'ألعاب ومسابقات الحصة التفاعلية': 'Interactive class games and quizzes', 'BoardPlus Games · فكرة وتطوير أ. محمد رجب': 'BoardPlus Games · created by Mohamed Ragab',
 'من': 'by', 'للمعلمين': 'For teachers', 'سجّل دخولك في BoardPlus، وابدأ أي لعبة من زر الألعاب داخل سبورتك. طلابك يدخلونها تلقائيًا': 'Sign in to BoardPlus and start any game from the games button on your board. Your students join automatically',
 'الذهاب إلى BoardPlus': 'Go to BoardPlus', 'تجربة هنا': 'Try it here', 'أهلًا بك': 'Welcome', 'الألعاب متصلة، وتشتغل الآن على أجهزة الطلاب': 'Games are connected and work on student devices now',
 'ألعاب الحصة لكل معلم وطالب': 'Class games for every teacher and student', 'معاينة': 'Preview', 'تعذّر الحفظ. تأكد من الإنترنت': "Couldn't save. Check your internet",
 'ألعاب ومسابقات تفاعلية مباشرة لأي درس: أسئلتك من BoardPlus ومن الذكاء الاصطناعي، أو أمثلة جاهزة في القسمة': 'Live interactive games for any lesson: your questions from BoardPlus and AI, or ready-made division examples',
}
rep('const I18N = {', 'const I18N = {' + json.dumps(ADD, ensure_ascii=False)[1:-1] + ',')
s = re.sub(r"const DB_URL_FALLBACKS = \[.*?\];\n", 'const DB_URL_FALLBACKS = [];\n', s, count=1, flags=re.S)
for bad in ['Ra26388', "ADMIN_PASS", 'ragabboard-9fe26']:
    assert bad not in s, bad
(D.parent / 'public' / 'games.html').write_text(s)
print('games.html', len(s))
