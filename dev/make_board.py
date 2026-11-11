#!/usr/bin/env python3
"""Build public/index.html (BoardPlus) from the ragabboard source (dev/board_src.html)."""
import re, json, pathlib
D = pathlib.Path(__file__).resolve().parent
s = (D / 'board_src.html').read_text()

def rep(a, b, cnt=1):
    global s
    n = s.count(a)
    assert n == cnt, (n, a[:90])
    s = s.replace(a, b)

def rep_block(start, end, new):
    global s
    a = s.index(start); b = s.index(end, a)
    s = s[:a] + new + s[b:]

# ---------------- head ----------------
T = 'BoardPlus | شوف حل كل طالب لحظة بلحظة وصحّحه فورًا'
DESC = 'سبورة الحصة التفاعلية: كل طالب يحل على سبورته وأنت تشوف وتصحح لحظيًا، مع كويز فوري بالذكاء الاصطناعي وألعاب ولوحة صدارة وعرض صوت وفيديو. الطلاب يدخلون بالكود بدون حساب.'
head_end = s.index('<meta name="claude:viewport-fit-sides" content="cover">')
s = f'''<title>{T}</title>
<meta name="description" content="{DESC}">
<meta property="og:title" content="{T}">
<meta property="og:image" content="https://boardplus.mawhibax.com/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:description" content="{DESC}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="application-name" content="BoardPlus">
<meta name="apple-mobile-web-app-title" content="BoardPlus">
<meta name="theme-color" content="#2f5bd3">
''' + s[head_end:]

# ---------------- scripts ----------------
rep('<script src="https://cdn.jsdelivr.net/npm/firebase@10.12.2/firebase-database-compat.js"></script>\n', '')
rep('<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>\n<script src="rt.js"></script>')

# ---------------- config ----------------
rep_block('/* =====================================================================\n   إعدادات Firebase', '/* ------------------------------------------------------------------ */',
'''/* =====================================================================
   BoardPlus — إعدادات Firebase (لتسجيل دخول المعلمين بحساب Google فقط)
   Firebase Console > Project settings > Your apps > Web app > firebaseConfig
   ===================================================================== */
const FIREBASE_CONFIG = {
  apiKey: "AIzaSyCNBATKcMAjup5Nf5BPKiqK5ly55ZKOI3o",
  authDomain: "boardplus-eb6b1.firebaseapp.com",
  projectId: "boardplus-eb6b1",
  appId: "1:74599234097:web:3afc6aeff702e4cde6b310"
};
const APP_NAME = 'BoardPlus';

''')

# ---------------- data layer ----------------
CLOUD = r'''function cloudRT() {
  const route = p => {
    const s = String(p || '').split('/').filter(Boolean);
    if (s[0] === 'sessions') return ['s:' + s[1], s.slice(2).join('/')];
    if (s[0] === 'banks') return ['b:' + s[1], s.slice(2).join('/')];
    if (s[0] === 'ragabcation' && s[1] === 'sessions') return ['g:' + s[2], s.slice(3).join('/')];
    return ['d', s.join('/')];
  };
  const R = p => { const [r, x] = route(p); return [RT.room(r), x] };
  let fa = null;
  if (FIREBASE_CONFIG.apiKey && window.firebase) {
    firebase.initializeApp(FIREBASE_CONFIG); fa = firebase.auth();
    RT.setToken(async () => fa.currentUser ? fa.currentUser.getIdToken() : '');
    fa.getRedirectResult().catch(() => {});
  } else if (DEV_HOST) RT.setToken(async () => ss.get('bu_dev') || '');
  const devUser = () => { const t = ss.get('bu_dev'); return t ? { uid: t.split(':')[1] } : null };
  return {
    mode: 'cloud',
    set: (p, v) => { const [r, x] = R(p); return r.set(x, v) },
    update: (p, o) => { const [r, x] = R(p); return r.update(x, o) },
    remove: p => { const [r, x] = R(p); return r.remove(x) },
    get: p => { const [r, x] = route(p); return RT.get(r, x) },
    onValue(p, cb) { const [r, x] = R(p); return r.onValue(x, cb) },
    onChild(p, h) { const [r, x] = R(p); return r.onChild(x, h) },
    onDisconnect(p, v) { const [r, x] = R(p); r.onDisconnect(x, v) },
    cancelDisconnect(p) { const [r, x] = R(p); r.cancelDisconnect(x) },
    connected: cb => RT.onConnected(cb),
    now: () => RT.now(),
    ts: () => RT.TS(),
    authReady: fa ? new Promise(res => { const u = fa.onAuthStateChanged(x => { u(); res(x ? { uid: x.uid } : null) }) }) : Promise.resolve(devUser()),
    user: () => fa ? (fa.currentUser ? { uid: fa.currentUser.uid } : null) : devUser(),
    async signIn() {
      if (fa) {
        const p = new firebase.auth.GoogleAuthProvider(); p.setCustomParameters({ prompt: 'select_account' });
        try { const c = await fa.signInWithPopup(p); return { uid: c.user.uid } }
        catch (e) { if (e && (e.code === 'auth/popup-blocked' || e.code === 'auth/operation-not-supported-in-this-environment')) { await fa.signInWithRedirect(p); return null } throw e }
      }
      if (DEV_HOST) {
        const email = await askText('Dev login (email)', ss.get('bu_dev_email') || 'teacher@test.dev', 'Login'); if (!email) return null;
        ss.set('bu_dev_email', email); const id = 'u' + (await sha(email)).slice(0, 12);
        ss.set('bu_dev', `dev:${id}:${email}:${encodeURIComponent(email.split('@')[0])}`); return { uid: id };
      }
      throw { code: 'no-config' };
    },
    signOut: () => { ss.del('bu_dev'); return fa ? fa.signOut() : Promise.resolve() },
    me: () => RT.api('me'),
    newSession: async () => (await RT.api('session', { lang: LANG })).code
  };
}
'''
rep_block('function cloudDB(cfg) {', 'function localDB() {', CLOUD)

rep_block("    authReady: Promise.resolve((() => { try { return JSON.parse(ss.get('rb_local_user') || 'null') } catch (e) { return null } })()),",
          "  };\n}\nlet DB;",
r'''    authReady: Promise.resolve(ss.get('bu_demo') ? { uid: 'demo' } : null),
    user: () => ss.get('bu_demo') ? { uid: 'demo' } : null,
    async signIn() { ss.set('bu_demo', '1'); return { uid: 'demo' } },
    signOut: () => { ss.del('bu_demo'); return Promise.resolve() },
    async me() {
      const p = getAt('teachers/demo') || { name: EN ? 'Demo teacher' : 'معلم تجريبي', email: 'demo@boardplus', photo: '', created: Date.now(), active: true, sessions: 0 };
      await write([['teachers/demo', { ...p, last: Date.now() }]]);
      return { uid: 'demo', ...p, admin: true };
    },
    async newSession() {
      let code; for (let i = 0; i < 25; i++) { code = String(100000 + Math.floor(Math.random() * 900000)); if (!getAt(`sessions/${code}/meta`)) break }
      await write([[`sessions/${code}/meta`, { active: true, created: Date.now(), locked: false, bgType: 'grid', timerEnd: 0, owner: 'demo' }], [`sessions/${code}/tinfo`, { name: ME.name, photo: ME.photo || '', lang: LANG }]]);
      const st = getAt('stats') || {}, day = new Date().toISOString().slice(0, 10);
      await write([['stats/sessions', (st.sessions || 0) + 1], [`stats/days/${day}`, ((st.days || {})[day] || 0) + 1], [`stats/months/${day.slice(0, 7)}`, ((st.months || {})[day.slice(0, 7)] || 0) + 1]]);
      return code;
    }
'''
)
rep("  const KEY = 'ragabboard_local_v1'; let tree = {};", "  const KEY = 'boardplus_local_v1'; let tree = {};")
rep("  let bc = null; try { bc = new BroadcastChannel('ragabboard_v1') } catch (e) {}", "  let bc = null; try { bc = new BroadcastChannel('boardplus_v1') } catch (e) {}")
rep_block("let DB;\nconst PREVIEW_ONLY", "/* ======================= drawing", r'''let DB;
const PREVIEW_ONLY = /claude|anthropic/.test(location.hostname) || location.protocol === 'file:';   // Claude preview: works offline in this browser only
const DEV_HOST = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) && !FIREBASE_CONFIG.apiKey;
async function sha(s) { const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)); return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('') }
try { DB = PREVIEW_ONLY ? localDB() : cloudRT() } catch (e) { console.error(e); DB = localDB() }

''')
rep("async function sha(s) { const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)); return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('') }\n$('#adminCard')",
    "$('#adminCard')")

# ---------------- landing page ----------------
LOGO = '<svg class="bulogo" viewBox="0 0 48 48" aria-hidden="true"><rect x="2" y="2" width="44" height="44" rx="12" fill="#2f5bd3"/><rect x="10" y="12" width="28" height="19" rx="3" fill="#fff"/><path d="M15 25l5 4 10-11" fill="none" stroke="#e0242f" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M24 34.5v8M20 38.5h8" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
WORD = 'Board<b>Plus</b>'
rep('<div class="word" style="position:relative">ragab<b>board</b><i>', f'<div class="word wlogo" style="position:relative">{LOGO}<span>{WORD}</span><i>')
rep_block('    <div class="hero">\n      <div class="who">', '    <form class="card" id="joinCard"', '''    <div class="hero">
      <div style="display:flex;flex-direction:column;gap:14px">
        <p class="hello">سبورة الحصة التفاعلية · مجانية لكل معلم</p>
        <h1>كل طالب على سبورته، وأنت تصحح لهم <em>مباشرة<svg viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true"><path d="M2 7 C 30 2, 65 10, 98 4" fill="none" stroke="#e0242f" stroke-width="3" stroke-linecap="round"/></svg></em></h1>
        <p class="lead">اكتب السؤال أو الصق صورته، والطلاب يحلّون على أجهزتهم في نفس اللحظة. تشوف كل الحلول قدامك، وتصحح بالقلم الأحمر، وتسوي كويز أو لعبة من صورة الدرس خلال ثواني.</p>
      </div>
      <ul class="tips">
        <li><span class="ti"><svg class="ico"><use href="#i-board"/></svg></span>الطلاب يدخلون بكود الحصة أو QR، بدون حسابات</li>
        <li><span class="ti"><svg class="ico"><use href="#i-pen"/></svg></span>تصحيح مباشر بالقلم الأحمر والأختام ونقاط الصدارة</li>
        <li><span class="ti"><svg class="ico"><use href="#i-ai"/></svg></span>كويز وألعاب جاهزة من صورة الدرس بالذكاء الاصطناعي</li>
        <li><span class="ti"><svg class="ico"><use href="#i-users"/></svg></span>عربي وإنجليزي، ويشتغل على الجوال والآيباد واللابتوب</li>
      </ul>
      <div class="herocta"><button class="btn pri big" type="button" id="heroTeacher"><span>ابدأ كمعلم مجانًا</span></button><span class="muted">دخول بحساب Google · بدون بطاقة</span></div>
    </div>

''')
rep('<div class="welcome"><span class="wave"><svg class="ico"><use href="#i-board"/></svg></span><div><h2>ادخل سبورتك</h2><p class="hint" style="margin:0">الكود موجود على شاشة الأستاذ</p></div></div>',
    '<div class="welcome"><span class="wave"><svg class="ico"><use href="#i-board"/></svg></span><div><h2>أنا طالب</h2><p class="hint" style="margin:0">الكود موجود على شاشة المعلم</p></div></div>')
rep('<div class="tlink"><button type="button" id="toTeacher">دخول المعلم</button></div>', '<div class="tlink"><button type="button" id="toTeacher">أنا معلم ← دخول بحساب Google</button></div>')
G = '<svg viewBox="0 0 48 48" width="20" height="20" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/><path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg>'
rep_block('    <form class="card" id="adminCard" autocomplete="off" hidden>', '  </div>\n  <div class="foot gut">', f'''    <div class="card" id="adminCard" hidden>
      <div class="welcome"><span class="wave"><svg class="ico"><use href="#i-users"/></svg></span><div><h2>دخول المعلم</h2><p class="hint" style="margin:0">سجّل بحساب Google وابدأ أول حصة خلال دقيقة</p></div></div>
      <button class="btn big gbtn" type="button" id="gSign">{G}<span>المتابعة بحساب Google</span></button>
      <p class="err" id="aErr"></p>
      <p class="hint small">نعرض اسمك وصورتك من Google لطلابك داخل الحصة فقط.</p>
      <button class="switch" type="button" id="toStudent">→ أنا طالب</button>
    </div>
''')
rep('<div class="foot gut">ragabboard · إعداد الأستاذ محمد رجب</div>', '<div class="foot gut">BoardPlus · فكرة وتطوير أ. محمد رجب</div>')

rep_block("  const h = new Date().getHours();\n  $('#hello')", "})();\n$('#toTeacher')", "")
# ---------------- teacher / student headers ----------------
rep('<div class="brand"><img class="ava" src="__AVATAR__" alt=""><div><div class="word">ragab<b>board</b></div><div class="sub">لوحة المعلم</div></div></div>',
    f'<div class="brand"><img class="ava" src="" alt=""><div><div class="word">{WORD}</div><div class="sub tname"><span id="tName">لوحة المعلم</span><button class="namebtn" id="tNameEdit" type="button" title="تعديل اسمك اللي يظهر للطلاب" aria-label="تعديل اسمك">✎</button></div></div></div>')
rep('<div class="credit">ragabboard · إعداد الأستاذ محمد رجب</div>', '<div class="credit">BoardPlus · فكرة وتطوير أ. محمد رجب</div>')
rep('<div class="brand"><img class="ava" src="__AVATAR__" alt=""><div class="hide-sm"><div class="word">ragab<b>board</b></div><div class="sub">إعداد أ. محمد رجب</div></div></div>',
    f'<div class="brand"><img class="ava" src="" alt=""><div class="hide-sm"><div class="word">{WORD}</div></div></div>')
rep('<div class="banner gut" id="demoBanner" hidden>وضع التجربة: السبورة تتزامن بين نوافذ نفس المتصفح فقط. افتح الرابط في نافذة ثانية وجرّب كطالب. لتشغيلها لطلابك على أجهزتهم أضف إعدادات Firebase في أعلى الملف.</div>',
    '<div class="banner gut" id="demoBanner" hidden>معاينة: السبورة هنا تتزامن بين نوافذ هذا المتصفح فقط. على الموقع المنشور تشتغل بين كل الأجهزة.</div>')

# ---------------- login flow ----------------
rep("$('#toTeacher').onclick = () => { $('#joinCard').hidden = true; $('#adminCard').hidden = false; $('#aUser').focus() };",
    "$('#toTeacher').onclick = () => { $('#joinCard').hidden = true; $('#adminCard').hidden = false; $('#gSign').focus() };\n$('#heroTeacher').onclick = () => { $('#toTeacher').click(); $('#adminCard').scrollIntoView({ behavior: 'smooth', block: 'center' }) };")
rep_block("$('#adminCard').addEventListener('submit', async e => {", "$('#joinCard').addEventListener('submit'", r'''$('#gSign').onclick = async () => {
  const btn = $('#gSign'), err = $('#aErr'); err.textContent = ''; btn.disabled = true;
  try {
    let u = DB.user(); if (!u) u = await DB.signIn();
    if (!u) { btn.disabled = false; return }
    try { await resolveUser(u) } catch (x) { if (x.code !== 'pending') await DB.signOut(); throw x }
  } catch (x) {
    btn.disabled = false; const c = x && x.code || '';
    if (c === 'auth/popup-closed-by-user' || c === 'auth/cancelled-popup-request') return;
    err.textContent = c === 'pending' ? 'تم تسجيلك ✓ حسابك بانتظار موافقة الإدارة. جرّب الدخول بعد ما يتم تفعيله.'
      : c === 'disabled' ? 'تم إيقاف هذا الحساب. تواصل مع إدارة BoardPlus.'
      : c === 'no-config' ? 'تسجيل الدخول غير مُعدّ بعد في هذا الموقع.'
      : c === 'auth/unauthorized-domain' ? 'هذا الرابط غير مضاف في Firebase (Authorized domains).'
      : c === 'auth/network-request-failed' || c === 'ERR' ? 'تعذر الاتصال. تأكد من الإنترنت.'
      : 'تعذر تسجيل الدخول. حاول مرة ثانية.';
    return;
  }
  btn.disabled = false;
  ss.set('rb_admin', '1'); teacherStart();
};
''')

# ---------------- sessions ----------------
rep_block("async function teacherStart() {", "function detach() {", r'''async function teacherStart() {
  ROLE = 't';
  show('teacher'); initTeacherUI(); applyTeacherBrand();
  let code = ls.get('rb_code_' + ME.uid);
  try {
    if (code) { const m = await DB.get(`sessions/${code}/meta`); if (!m || !m.active || (m.owner && m.owner !== ME.uid)) code = null }
    attach(code || await createSession());
  } catch (e) {
    console.error(e); toast(e && (e.code === 'pending' || e.code === 'inactive') ? 'حسابك غير مفعّل حاليًا' : 'تعذر إنشاء الحصة. تأكد من الإنترنت وحاول مرة ثانية.', true);
    ss.del('rb_admin'); show('home'); $('#toTeacher').click();
  }
}
async function createSession() {
  const code = await DB.newSession();
  ls.set('rb_code_' + ME.uid, code); return code;
}
''')
rep("if (!ME.admin && ME.uid) DB.set(`teachers/${ME.uid}/live`, { code, at: DB.now() }).catch(() => {});", "if (ME.uid) DB.set(`teachers/${ME.uid}/live`, { code, at: DB.now() }).catch(() => {});")
rep("$('#tOut').onclick = () => { if (!ME.admin && ME.uid) DB.remove(`teachers/${ME.uid}/live`);", "$('#tOut').onclick = () => { if (ME.uid) DB.remove(`teachers/${ME.uid}/live`).catch(() => {});")
rep("toast('لا يوجد اتصال بقاعدة البيانات. تأكد من رابط databaseURL والإنترنت.', true)", "toast('انقطع الاتصال بالسيرفر. نحاول نرجع تلقائيًا…', true)")

# ---------------- accounts ----------------
rep_block("/* ======================= accounts: admin + teachers ======================= */", "async function lookupTeacher(code) {", r'''/* ======================= accounts: Google sign-in teachers + admin ======================= */
const ADMIN_NAME = EN ? 'Teacher' : 'المعلم';
const ME = { uid: '', admin: false, name: '', photo: '' };
const BANK = () => `banks/${ME.uid || 'none'}`;
const _avCache = {};
function initialAvatar(name) {
  const n = String(name || '؟').replace(/^(الأستاذة|الأستاذ|الاستاذة|الاستاذ|أ\.|المعلمة|المعلم|Mr\.?|Mrs\.?|Ms\.?|Dr\.?)\s*/i, '').trim(), ch = (n[0] || '؟').toUpperCase();
  if (_avCache[n]) return _avCache[n];
  const c = document.createElement('canvas'); c.width = c.height = 120; const x = c.getContext('2d');
  const cols = ['#2f5bd3', '#1f9d55', '#e07b16', '#7b3fc4', '#d1435b', '#0e8fa3']; let h = 0; for (const k of n) h = (h * 31 + k.charCodeAt(0)) >>> 0;
  x.fillStyle = cols[h % cols.length]; x.fillRect(0, 0, 120, 120); x.fillStyle = '#fff';
  x.font = '700 60px "Readex Pro","IBM Plex Sans Arabic",sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(ch, 60, 64);
  return _avCache[n] = c.toDataURL('image/png');
}
const photoOf = (name, photo) => photo || initialAvatar(name);
async function resolveUser(user) {
  if (!user) throw { code: 'login' };
  const p = await DB.me();
  if (!p.active) throw { code: p.pending ? 'pending' : 'disabled' };
  Object.assign(ME, { uid: p.uid || user.uid, admin: !!p.admin, name: p.name || ADMIN_NAME, photo: p.photo || '' });
}
function applyTeacherBrand() {
  $('#teacher .brand .ava').src = photoOf(ME.name, ME.photo); $('#teacher .brand .ava').alt = ME.name;
  $('#tName').textContent = ME.name;
  $('#tAdmin').hidden = !ME.admin;
  $('#tNameEdit').onclick = async () => {
    const n = await askText('اسمك اللي يظهر للطلاب', ME.name, 'حفظ'); if (!n || n === ME.name) return;
    ME.name = n.slice(0, 40); applyTeacherBrand();
    DB.update(`teachers/${ME.uid}`, { name: ME.name }).catch(() => {});
    if (T.code) DB.update(`sessions/${T.code}/tinfo`, { name: ME.name }).catch(() => {});
    toast('تم تغيير اسمك');
  };
}
async function openTeachers() {
  if (!ME.admin) return;
  const uns = []; let list = {}, settings = {}, stats = {}, q = '';
  const day = new Date().toISOString().slice(0, 10), mon = day.slice(0, 7);
  const fmtD = t => t ? new Intl.DateTimeFormat(EN ? 'en-GB' : 'ar-SA', { day: 'numeric', month: 'short' }).format(new Date(t)) : '—';
  modal(`<h3 class="aih">${svgI('users')}لوحة الإدارة</h3>
    <div class="astats" id="aStats"></div>
    <label class="aiauto"><input type="checkbox" id="aApprove"> المعلمين الجدد يحتاجون موافقتي قبل ما يبدأون</label>
    <input class="inp" id="aSearch" placeholder="ابحث باسم المعلم أو بريده" autocomplete="off">
    <div class="tlist" id="tList"><span class="muted">جارٍ التحميل…</span></div>
    <div class="row"><button class="btn" data-close>إغلاق</button></div>`,
  (v, close) => {
    v.querySelector('.dlg').classList.add('wide');
    const $v = x => v.querySelector(x);
    const drawStats = () => {
      const tiles = [[stats.teachers || Object.keys(list).length, 'معلم مسجل'], [(stats.days || {})[day] || 0, 'حصة اليوم'], [(stats.months || {})[mon] || 0, 'حصة هذا الشهر'], [stats.sessions || 0, 'كل الحصص']];
      $v('#aStats').innerHTML = tiles.map(([n, l]) => `<div class="atile"><b class="num">${n}</b><span>${l}</span></div>`).join('');
    };
    const draw = () => {
      drawStats();
      const rows = Object.entries(list).filter(([, t]) => t && t.name && (!q || (t.name + ' ' + (t.email || '')).toLowerCase().includes(q)))
        .sort((a, b) => (!!a[1].active - !!b[1].active) || ((b[1].last || 0) - (a[1].last || 0)));
      $v('#tList').innerHTML = rows.length ? rows.map(([id, t]) => {
        const live = t.live && t.live.code && DB.now() - (t.live.at || 0) < 6 * 3600e3;
        const st = t.active ? ['ok', 'نشط'] : t.suspended ? ['bad', 'موقوف'] : ['demo', 'بانتظار الموافقة'];
        return `<div class="trow${t.active ? '' : ' off'}" data-uid="${id}"><img class="tav" src="${photoOf(t.name, t.photo)}" alt="" referrerpolicy="no-referrer">
          <div class="tinfo"><b>${esc(t.name)}</b><span dir="ltr">${esc(t.email || '')}</span><span>${t.sessions || 0} حصة · آخر دخول ${fmtD(t.last)}</span></div>
          ${live ? `<span class="pill tlive">في حصة · ${esc(t.live.code)}</span>` : ''}
          <span class="pill ${st[0]}"><span class="dot"></span>${st[1]}</span>
          <button class="btn" data-act="toggle">${t.active ? 'إيقاف' : 'تفعيل'}</button>
          <button class="btn icon danger" data-act="del" title="حذف المعلم" aria-label="حذف">${svgI('trash')}</button></div>`;
      }).join('') : `<div class="empty"><b>${q ? 'ما في نتائج' : 'ما سجّل أي معلم بعد'}</b><span>أي معلم يدخل بحساب Google يظهر هنا.</span></div>`;
    };
    uns.push(DB.onValue('teachers', x => { list = x || {}; draw() }));
    uns.push(DB.onValue('settings', x => { settings = x || {}; $v('#aApprove').checked = settings.approve === true }));
    uns.push(DB.onValue('stats', x => { stats = x || {}; drawStats() }));
    new MutationObserver((m, o) => { if (!v.isConnected) { o.disconnect(); uns.forEach(u => u && u()) } }).observe(document.body, { childList: true });
    $v('#aApprove').onchange = e => { DB.set('settings/approve', e.target.checked ? true : null); toast(e.target.checked ? 'المعلمين الجدد بينتظرون موافقتك' : 'أي معلم يقدر يبدأ مباشرة') };
    $v('#aSearch').oninput = e => { q = e.target.value.trim().toLowerCase(); draw() };
    $v('#tList').onclick = async e => {
      const b = e.target.closest('[data-act]'); if (!b) return; const id = b.closest('.trow').dataset.uid, t = list[id]; if (!t) return;
      if (b.dataset.act === 'toggle') { DB.update(`teachers/${id}`, { active: !t.active, suspended: t.active ? true : null }); toast(t.active ? `تم إيقاف ${t.name}` : `تم تفعيل ${t.name}`) }
      else if (b.dataset.act === 'del' && await ask(`حذف ${esc(t.name)}؟`, 'يُحذف من القائمة. لو دخل مرة ثانية بحساب Google يتسجل من جديد.', 'حذف')) DB.remove(`teachers/${id}`);
    };
  });
}
''')
rep("const ti = (await DB.get(`sessions/${code}/tinfo`)) || {}, nm = ti.name || ADMIN_NAME;", "const ti = (await DB.get(`sessions/${code}/tinfo`)) || {}, nm = ti.name || ADMIN_NAME;")
rep("box.innerHTML = `<img src=\"${photoOf(nm, ti.photo, !ti.name)}\" alt=\"\">", "box.innerHTML = `<img src=\"${photoOf(nm, ti.photo)}\" alt=\"\" referrerpolicy=\"no-referrer\">")
rep("$('#student .brand .ava').src = photoOf(nm, ti.photo, !ti.name);", "$('#student .brand .ava').src = photoOf(nm, ti.photo);")

# ---------------- games ----------------
rep("const QUIZRAGAB_URL = 'quizragab.html';   // ارفع ملف quizragab.html بجانب index.html", "const QUIZRAGAB_URL = 'games.html';")
rep("/* ======================= QuizRagab games inside ragabboard ======================= */", "/* ======================= games inside the board ======================= */")
s = s.replace("ألعاب QuizRagab", "ألعاب BoardPlus")

# ---------------- CSS additions ----------------
rep(".board.drop{", """.wlogo{display:flex;align-items:center;gap:8px}.wlogo .bulogo{width:30px;height:30px}
.home-top .word{font-size:24px}
.herocta{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.herocta .muted{color:var(--muted);font-size:13px}
.gbtn{background:#fff;color:#1f1f1f;border:1px solid #dadce0;gap:12px;font-weight:600}
.gbtn:hover{background:#f7f8fa}
.hint.small{font-size:12px}
.tname{display:flex;align-items:center;gap:4px}
.namebtn{border:0;background:transparent;color:var(--muted);font-size:13px;padding:0 4px;border-radius:6px;cursor:pointer}
.namebtn:hover{color:var(--accent);background:var(--accent-soft)}
.astats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.atile{background:var(--surface-2);border:1px solid var(--line);border-radius:12px;padding:10px;display:flex;flex-direction:column;gap:2px}
.atile b{font-size:22px;font-family:var(--f-display)}.atile span{font-size:12px;color:var(--muted)}
.pill.demo{background:var(--hand-soft);border-color:var(--hand)}
@media (max-width:520px){.astats{grid-template-columns:repeat(2,minmax(0,1fr))}}
.board.drop{""")

# ---------------- i18n additions ----------------
ADD = {
 'سبورة الحصة التفاعلية · مجانية لكل معلم': 'The interactive class board · free for every teacher',
 'كل طالب على سبورته، وأنت تصحح لهم': 'Every student on their own board, and you correct them',
 'مباشرة': 'live',
 'اكتب السؤال أو الصق صورته، والطلاب يحلّون على أجهزتهم في نفس اللحظة. تشوف كل الحلول قدامك، وتصحح بالقلم الأحمر، وتسوي كويز أو لعبة من صورة الدرس خلال ثواني': 'Write the question or paste its picture, and students solve it on their devices at the same moment. See every answer, correct with the red pen, and turn a lesson photo into a quiz or game in seconds',
 'الطلاب يدخلون بكود الحصة أو QR، بدون حسابات': 'Students join with a class code or QR, no accounts',
 'تصحيح مباشر بالقلم الأحمر والأختام ونقاط الصدارة': 'Live red-pen correction, stamps and leaderboard points',
 'كويز وألعاب جاهزة من صورة الدرس بالذكاء الاصطناعي': 'Ready quizzes and games from a lesson photo with AI',
 'عربي وإنجليزي، ويشتغل على الجوال والآيباد واللابتوب': 'Arabic and English, on phones, iPads and laptops',
 'ابدأ كمعلم مجانًا': 'Start free as a teacher', 'دخول بحساب Google · بدون بطاقة': 'Sign in with Google · no card needed',
 'أنا طالب': "I'm a student", 'الكود موجود على شاشة المعلم': "The code is on your teacher's screen",
 'أنا معلم ← دخول بحساب Google': "I'm a teacher → sign in with Google", 'سجّل بحساب Google وابدأ أول حصة خلال دقيقة': 'Sign in with Google and start your first class in a minute',
 'المتابعة بحساب Google': 'Continue with Google', 'نعرض اسمك وصورتك من Google لطلابك داخل الحصة فقط': 'Your Google name and photo are shown only to your students in class',
 'BoardPlus · فكرة وتطوير أ. محمد رجب': 'BoardPlus · created by Mohamed Ragab',
 'معاينة: السبورة هنا تتزامن بين نوافذ هذا المتصفح فقط. على الموقع المنشور تشتغل بين كل الأجهزة': 'Preview: the board here only syncs between windows of this browser. On the published site it works across all devices',
 'تعديل اسمك اللي يظهر للطلاب': 'Edit the name students see', 'تعديل اسمك': 'Edit your name', 'اسمك اللي يظهر للطلاب': 'Your name as students see it', 'تم تغيير اسمك': 'Name updated',
 'تم تسجيلك ✓ حسابك بانتظار موافقة الإدارة. جرّب الدخول بعد ما يتم تفعيله': "You're registered ✓ Your account is waiting for approval. Try again once it's activated",
 'تم إيقاف هذا الحساب. تواصل مع إدارة BoardPlus': 'This account is suspended. Contact BoardPlus',
 'تسجيل الدخول غير مُعدّ بعد في هذا الموقع': "Sign-in isn't set up on this site yet",
 'هذا الرابط غير مضاف في Firebase (Authorized domains)': "This address isn't added in Firebase (Authorized domains)",
 'تعذر الاتصال. تأكد من الإنترنت': "Couldn't connect. Check your internet", 'تعذر تسجيل الدخول. حاول مرة ثانية': "Couldn't sign in. Try again",
 'حسابك غير مفعّل حاليًا': "Your account isn't active right now", 'تعذر إنشاء الحصة. تأكد من الإنترنت وحاول مرة ثانية': "Couldn't create the class. Check your internet and try again",
 'انقطع الاتصال بالسيرفر. نحاول نرجع تلقائيًا…': 'Lost connection to the server. Reconnecting…',
 'لوحة الإدارة': 'Admin dashboard', 'معلم مسجل': 'teachers', 'حصة اليوم': 'classes today', 'حصة هذا الشهر': 'classes this month', 'كل الحصص': 'all classes',
 'المعلمين الجدد يحتاجون موافقتي قبل ما يبدأون': 'New teachers need my approval before they start', 'ابحث باسم المعلم أو بريده': 'Search by teacher name or email',
 'بانتظار الموافقة': 'Pending approval', 'حصة · آخر دخول': 'classes · last seen', 'ما في نتائج': 'No results', 'ما سجّل أي معلم بعد': 'No teachers yet',
 'أي معلم يدخل بحساب Google يظهر هنا': 'Any teacher who signs in with Google shows up here', 'المعلمين الجدد بينتظرون موافقتك': 'New teachers will wait for your approval',
 'أي معلم يقدر يبدأ مباشرة': 'Any teacher can start right away', 'يُحذف من القائمة. لو دخل مرة ثانية بحساب Google يتسجل من جديد': "They're removed from the list. If they sign in again with Google they register again",
 'ألعاب BoardPlus': 'BoardPlus games', 'المعلم': 'Teacher', 'معلم تجريبي': 'Demo teacher',
}
add_js = json.dumps(ADD, ensure_ascii=False)[1:-1]
rep('const I18N = {', 'const I18N = {' + add_js + ',')
rep('"سبورة الأستاذ محمد رجب التفاعلية":"Mr. Mohamed Ragab\'s Interactive Board",', '')
rep('"BoardPlus | سبورة تفاعلية مجانية للمعلمين"' if False else 'const I18N = {', 'const I18N = {"BoardPlus | سبورة تفاعلية مجانية للمعلمين":"BoardPlus | Free interactive whiteboard for teachers",')

# student voice / video notes
import feat_media
def _r1(src, a, b):
    assert src.count(a) == 1, (src.count(a), a[:80]); return src.replace(a, b)
s = feat_media.apply(s, _r1)
import feat_pages
s = feat_pages.apply(s, _r1)
import feat_aitopic
s = feat_aitopic.apply(s, _r1)
import feat_show
s = feat_show.apply(s, _r1)
import feat_admin
s = feat_admin.apply(s, _r1)

# sanity: no leftovers
for bad in ['__AVATAR__', 'ADMIN_HASH', 'ADMIN_EMAIL', 'emailOf(', 'createUser', 'AVATAR_SRC', 'quizragab.html', "'teacher/q"]:
    assert bad not in s, bad

skel = '''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
'''
i = s.index('</style>') + len('</style>')
out = skel + s[:i] + '\n</head>\n<body>\n' + s[i:] + '\n</body>\n</html>\n'
(D.parent / 'public' / 'index.html').write_text(out)
(D / 'preview.html').write_text(s)          # same page without the document skeleton (for the Claude preview)
print('index.html', len(out))
