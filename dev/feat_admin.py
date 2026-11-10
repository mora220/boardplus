"""BoardPlus feature: the admin opens any live class in the teacher view (not as a student),
and the admin list shows the time of each teacher's last sign-in."""
import json

ADD_I18N = {
    "دخول الحصة": "Open class", "ادخل حصة بالكود": "Open a class by code", "كود الحصة": "Class code", "دخول كمدير": "Open as admin",
    "أنت داخل حصة": "You are viewing the class of", "كمدير": "as admin", "رجوع لحصتي": "Back to my class",
    "ما لقيت حصة شغالة بهذا الكود": "No running class with this code", "هذه حصتك": "This is your own class",
    "غير متاح وأنت داخل حصة معلم آخر": "Not available while you are in another teacher's class",
}

CSS = r"""
.watchbar{position:sticky;top:0;z-index:30;display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;padding:8px 14px;background:#fff4d6;border-bottom:1px solid #f0d58a;color:#6b4e00;font-weight:600;font-size:14px}
.watchbar[hidden]{display:none}
.watchbar button{height:34px;border-radius:10px;border:1px solid #d9b24c;background:#fff;color:#6b4e00;font:inherit;font-weight:700;padding:0 12px;cursor:pointer}
.awatch{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.awatch .inp{max-width:170px;text-align:center;letter-spacing:3px}
body.watching #tNew{opacity:.35;pointer-events:none}
"""

JS = r"""
/* ======================= admin: open any class in the teacher view ======================= */
async function watchSession(code, name) {
  if (!ME.admin || !/^\d{6}$/.test(code || '')) return;
  if (code === T.code && !T.watch) return toast('هذه حصتك');
  const m = await DB.get(`sessions/${code}/meta`).catch(() => null);
  if (!m || !m.active) return toast('ما لقيت حصة شغالة بهذا الكود', true);
  if (!name) { const ti = await DB.get(`sessions/${code}/tinfo`).catch(() => null); name = (ti && ti.name) || '' }
  detach(); T.watch = { code, name }; document.body.classList.add('watching');
  $('#watchBar').hidden = false; $('#watchName').textContent = name ? `${name} (${code})` : code;
  attach(code, true);
}
async function unwatch() {
  if (!T.watch) return; detach(); T.watch = null; document.body.classList.remove('watching'); $('#watchBar').hidden = true;
  let code = ls.get('rb_code_' + ME.uid);
  if (code) { const m = await DB.get(`sessions/${code}/meta`).catch(() => null); if (!m || !m.active || (m.owner && m.owner !== ME.uid)) code = null }
  attach(code || await createSession());
}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    # banner above the teacher screen
    s = rep(s, '<section id="teacher"', '<div class="watchbar" id="watchBar" hidden>👁 <span>أنت داخل حصة <b id="watchName"></b> كمدير</span><button id="watchBack">رجوع لحصتي</button></div>\n<section id="teacher"')
    s = rep(s, "  $('#tNew').onclick = async () => {", "  $('#watchBack').onclick = unwatch;\n  $('#tNew').onclick = async () => { if (T.watch) return toast('غير متاح وأنت داخل حصة معلم آخر');")
    s = rep(s, "  $('#tOut').onclick = () => {", "  $('#tOut').onclick = () => { if (T.watch) { T.watch = null; document.body.classList.remove('watching'); $('#watchBar').hidden = true }")
    # attach(code, watch): an admin watching changes nothing about the other teacher's class
    s = rep(s, "function attach(code) {\n  T.code = code; DB.update(`sessions/${code}/tinfo`, { lang: LANG }).catch(() => {}); if (ME.uid) DB.set(`teachers/${ME.uid}/live`, { code, at: DB.now() }).catch(() => {});",
            "function attach(code, watch) {\n  T.code = code; if (!watch) { DB.update(`sessions/${code}/tinfo`, { lang: LANG }).catch(() => {}); if (ME.uid) DB.set(`teachers/${ME.uid}/live`, { code, at: DB.now() }).catch(() => {}) }")
    s = rep(s, "    if (q && ['q', 'r', 'p', 'k'].includes(q.st) && !QZ.run) DB.remove(b + '/quiz');   // quiz interrupted by a reload",
            "    if (q && ['q', 'r', 'p', 'k'].includes(q.st) && !QZ.run && !T.watch) DB.remove(b + '/quiz');   // quiz interrupted by a reload (never touch another teacher's running quiz)")
    s = rep(s, "    if (T.code) DB.update(`sessions/${T.code}/tinfo`, { name: ME.name }).catch(() => {});",
            "    if (T.code && !T.watch) DB.update(`sessions/${T.code}/tinfo`, { name: ME.name }).catch(() => {});")
    # admin list: last sign-in with time, open-class button, open by code
    s = rep(s, "  const fmtD = t => t ? new Intl.DateTimeFormat(EN ? 'en-GB' : 'ar-SA', { day: 'numeric', month: 'short' }).format(new Date(t)) : '—';",
            "  const fmtD = t => t ? new Intl.DateTimeFormat(EN ? 'en-GB' : 'ar-SA', { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' }).format(new Date(t)) : '—';")
    s = rep(s, "    <input class=\"inp\" id=\"aSearch\" placeholder=\"ابحث باسم المعلم أو بريده\" autocomplete=\"off\">",
            "    <div class=\"awatch\"><b>ادخل حصة بالكود</b><input class=\"inp num\" id=\"aCode\" inputmode=\"numeric\" maxlength=\"6\" placeholder=\"كود الحصة\"><button class=\"btn pri\" id=\"aWatch\">👁 دخول كمدير</button></div>\n"
            "    <input class=\"inp\" id=\"aSearch\" placeholder=\"ابحث باسم المعلم أو بريده\" autocomplete=\"off\">")
    s = rep(s, "          ${live ? `<span class=\"pill tlive\">في حصة · ${esc(t.live.code)}</span>` : ''}",
            "          ${live ? `<span class=\"pill tlive\">في حصة · ${esc(t.live.code)}</span>${id === ME.uid ? '' : `<button class=\"btn pri\" data-act=\"watch\" data-code=\"${esc(t.live.code)}\">👁 دخول الحصة</button>`}` : ''}")
    s = rep(s, "      if (b.dataset.act === 'toggle') {",
            "      if (b.dataset.act === 'watch') { close(); watchSession(b.dataset.code, t.name); return }\n      if (b.dataset.act === 'toggle') {")
    s = rep(s, "    $v('#aSearch').oninput = e => { q = e.target.value.trim().toLowerCase(); draw() };",
            "    $v('#aSearch').oninput = e => { q = e.target.value.trim().toLowerCase(); draw() };\n"
            "    $v('#aWatch').onclick = () => { const c = $v('#aCode').value.replace(/\\D/g, ''); if (c.length !== 6) return toast('ما لقيت حصة شغالة بهذا الكود', true); close(); watchSession(c) };\n"
            "    $v('#aCode').onkeydown = e => { if (e.key === 'Enter') $v('#aWatch').click() };")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
