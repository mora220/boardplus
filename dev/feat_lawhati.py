"""Ideas from Lawhati, for BoardPlus and ragabboard:
  - graph of functions (y = x^2 - 4 ; sqrt(x) ...) as a movable board item
  - class name list: students pick their name instead of typing it
  - curtain: hide the board from students and reveal it step by step
  - laser pointer the students see, which leaves no ink
apply(s, rep, target) where target is 'bp' (BoardPlus) or 'rb' (ragabboard)."""
import json, re

ADD_I18N = {
    "رسم دالة": "Graph a function", "ارسم": "Draw", "الدالة": "Function", "من": "From", "إلى": "To",
    "اكتب الدالة كما تكتبها على الورق، وافصل بين أكثر من دالة بفاصلة منقوطة ;": "Type the function as on paper; separate several with a semicolon ;",
    "الدالة غير مفهومة": "The function isn't understood", "قائمة أسماء الفصل": "Class name list", "الفصل": "Class",
    "اسم الفصل": "Class name", "اكتب كل اسم في سطر": "One name per line", "حفظ وتفعيل في هذه الحصة": "Save and use in this class",
    "إيقاف القائمة (دخول حر)": "Turn off (free names)", "اختر اسمك": "Choose your name", "اختر اسمك من القائمة": "Choose your name from the list",
    "ستارة: أخفِ السبورة عن الطلاب واكشفها بالتدريج": "Curtain: hide the board from students and reveal it step by step",
    "اسحب لكشف السبورة للطلاب": "Drag to reveal the board to students", "مؤشر ليزر: يراه الطلاب ولا يكتب": "Laser pointer: students see it, it leaves no ink",
    "تم تفعيل قائمة الفصل": "Class list is on", "تم إيقاف قائمة الفصل": "Class list is off", "قوائم محفوظة": "Saved lists", "قائمة جديدة": "New list",
}

ICONS = '''    <symbol id="i-graph" viewBox="0 0 24 24"><path d="M3 12h18M12 3v18"/><path d="M5 20c3-9 5-13 7-13s4 4 7 13" /></symbol>
    <symbol id="i-clist" viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></symbol>
    <symbol id="i-curtain" viewBox="0 0 24 24"><path d="M3 3h18"/><path d="M5 3v14c2 0 3-3 3-7M19 3v14c-2 0-3-3-3-7"/><path d="M3 21h18" stroke-dasharray="2 2"/></symbol>
    <symbol id="i-laser" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3.5" fill="currentColor"/><circle cx="12" cy="12" r="7.5" opacity=".45"/><path d="M12 1.5v2.5M12 20v2.5M1.5 12H4M20 12h2.5"/></symbol>
'''

CSS = r"""
.gform{display:flex;flex-direction:column;gap:10px}
.gform .grow{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.gform .grow .inp{flex:1;min-width:0}
.gform .xr{width:80px;flex:none!important;text-align:center}
.gform canvas{width:100%;aspect-ratio:10/7;border:1px solid var(--line);border-radius:12px;background:#fff}
.gform .ex{display:flex;gap:6px;flex-wrap:wrap}
.gform .ex button{border:1px solid var(--line);background:var(--surface-2);border-radius:99px;padding:4px 12px;font:inherit;font-size:13px;direction:ltr;cursor:pointer}
.clform{display:flex;flex-direction:column;gap:10px}
.clform textarea{min-height:200px;resize:vertical;font:inherit;line-height:1.6}
.jlist{display:flex;flex-direction:column;gap:8px;margin-top:4px}
.jlist[hidden]{display:none}
.jlh{font-size:13px;font-weight:700;color:var(--muted)}
.jnames{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:6px;max-height:44vh;overflow:auto;padding:2px}
.jn{min-height:44px;border:1.5px solid var(--line);border-radius:12px;background:var(--surface);font:inherit;font-weight:600;font-size:15px;color:var(--ink);cursor:pointer;padding:6px 8px}
.jn.on{border-color:var(--accent);background:var(--accent);color:#fff}
.jn:disabled{opacity:.45;cursor:default}
.jn[hidden]{display:none}
.jpick{width:100%;height:48px;border-radius:12px;border:1.5px solid var(--line);background:var(--surface);font:inherit;font-size:16px;padding:0 12px;color:var(--ink)}
.curt{position:absolute;left:0;right:0;bottom:0;z-index:5;pointer-events:none;display:grid;place-items:center;font-size:42px;border-radius:inherit}
.curt.s{background:repeating-linear-gradient(90deg,#6b2342 0 26px,#7d2a4e 26px 52px);box-shadow:inset 0 10px 18px rgba(0,0,0,.35)}
.curt.t{background:rgba(107,35,66,.38);border-top:3px dashed #7d2a4e}
.curt .ch{position:absolute;top:-19px;left:50%;transform:translateX(-50%);pointer-events:auto;cursor:ns-resize;touch-action:none;background:#7d2a4e;color:#fff;border-radius:99px;padding:6px 16px;font-size:13px;font-weight:700;white-space:nowrap;box-shadow:var(--shadow)}
.laz{position:absolute;z-index:6;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;pointer-events:none;background:radial-gradient(circle,#fff 0 18%,#ff2d3d 32%,rgba(255,45,61,.35) 60%,transparent 72%);box-shadow:0 0 16px 6px rgba(255,45,61,.45);transition:left .06s linear,top .06s linear,opacity .4s}
"""

JS = r"""
/* ======================= class name list ======================= */
async function openClassList() {
  if (!T.code) return;
  const saved = (await DB.get(BANK() + '/classes').catch(() => null)) || {}, cur = (await DB.get(`sessions/${T.code}/clist`).catch(() => null)) || null;
  const ids = Object.keys(saved);
  modal(`<div class="clform"><h3>${svgI('clist')} قائمة أسماء الفصل</h3>
    ${ids.length ? `<label>قوائم محفوظة<select class="jpick" id="clSaved"><option value="">قائمة جديدة</option>${ids.map(id => `<option value="${id}">${esc(saved[id].name || 'الفصل')} (${(saved[id].names || []).length})</option>`).join('')}</select></label>` : ''}
    <label>اسم الفصل<input class="inp" id="clName" placeholder="مثال: خامس أ" value="${esc((cur && cur.name) || '')}"></label>
    <label>اكتب كل اسم في سطر<textarea class="inp" id="clNames">${esc(((cur && cur.names) || []).join('\n'))}</textarea></label>
    <p class="muted" style="margin:0">الطالب يختار اسمه من القائمة بدل ما يكتبه، فتطلع الأسماء صحيحة ومرتبة.</p>
    <div class="row">${cur ? '<button class="btn" id="clOff">إيقاف القائمة (دخول حر)</button>' : ''}<button class="btn" data-close>إلغاء</button><button class="btn pri" id="clGo">حفظ وتفعيل في هذه الحصة</button></div></div>`, (v, close) => {
    const $v = q => v.querySelector(q); let cid = (cur && cur.id) || '';
    const sel = $v('#clSaved'); if (sel) { if (cid && saved[cid]) sel.value = cid; sel.onchange = () => { cid = sel.value; const c = saved[cid]; $v('#clName').value = c ? c.name || '' : ''; $v('#clNames').value = c ? (c.names || []).join('\n') : '' } }
    const off = $v('#clOff'); if (off) off.onclick = () => { DB.remove(`sessions/${T.code}/clist`); close(); toast('تم إيقاف قائمة الفصل') };
    $v('#clGo').onclick = async () => {
      const names = [...new Set($v('#clNames').value.split(/\n+/).map(x => x.trim().replace(/\s+/g, ' ').slice(0, 30)).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'ar'));
      if (!names.length) return toast('اكتب الأسماء أولًا', true);
      const name = $v('#clName').value.trim().slice(0, 40) || 'الفصل'; cid = cid || 'c' + uid();
      await DB.set(`${BANK()}/classes/${cid}`, { name, names }).catch(() => {});
      await DB.set(`sessions/${T.code}/clist`, { id: cid, name, names }); close(); toast('تم تفعيل قائمة الفصل');
    };
  });
}
async function classPicker(code) {
  const inp = $('#jName'), go = $('#jGo'); let box = $('#jList');
  if (!go.dataset.t0) go.dataset.t0 = go.textContent;
  const free = () => { if (box) box.hidden = true; inp.hidden = false; go.textContent = go.dataset.t0 };
  const cl = /^\d{6}$/.test(code || '') ? await DB.get(`sessions/${code}/clist`).catch(() => null) : null;
  if ($('#jCode').value.replace(/\D/g, '') !== code) return;
  if (!cl || !cl.names || !cl.names.length || inp.readOnly) return free();
  const roster = (await DB.get(`sessions/${code}/roster`).catch(() => null)) || {}, used = new Set(Object.values(roster).filter(r => r && r.online).map(r => r.name));
  if (!box) { box = document.createElement('div'); box.id = 'jList'; box.className = 'jlist'; inp.after(box) }
  box.innerHTML = `<div class="jlh">👥 ${esc(cl.name || '')} · اختر اسمك ثم اضغط تأكيد</div>${cl.names.length > 12 ? '<input class="inp jsearch" placeholder="ابحث عن اسمك">' : ''}
    <div class="jnames">${cl.names.map(n => `<button type="button" class="jn" ${used.has(n) ? 'disabled' : ''} data-n="${esc(n)}">${esc(n)}${used.has(n) ? ' ✓' : ''}</button>`).join('')}</div>`;
  box.hidden = false; inp.hidden = true; inp.value = ''; go.textContent = 'تأكيد ✓';
  box.querySelectorAll('.jn').forEach(b => b.onclick = () => { box.querySelectorAll('.jn').forEach(x => x.classList.toggle('on', x === b)); inp.value = b.dataset.n; go.focus() });
  const q = box.querySelector('.jsearch'); if (q) q.oninput = () => { const t = q.value.trim(); box.querySelectorAll('.jn').forEach(b => b.hidden = !!t && !b.dataset.n.includes(t)) };
}
/* ======================= laser pointer ======================= */
const LZ = { t: 0, hide: 0 };
function laserAt(host, x, y) {
  if (!host) return; let d = host.querySelector('.laz'); if (!d) { d = document.createElement('div'); d.className = 'laz'; host.appendChild(d) }
  d.style.opacity = 1; d.style.left = x / W * 100 + '%'; d.style.top = y / H * 100 + '%';
  clearTimeout(d._h); d._h = setTimeout(() => d.style.opacity = 0, 1200);
}
function sendLaser(x, y) {
  laserAt($('#tBoard'), x, y); const n = performance.now();
  if (n - LZ.t > 55 && T.code) { LZ.t = n; DB.set(`sessions/${T.code}/laser`, { x: Math.round(x), y: Math.round(y), t: DB.now() }) }
}
"""


def apply(s, rep, target):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, '    <symbol id="i-img" viewBox', ICONS + '    <symbol id="i-img" viewBox')
    # graph item
    # teacher buttons
    s = rep(s, "      { icon: 'bg', label: 'خلفية السبورة', onClick: pickBg },\n",
            "      { icon: 'bg', label: 'خلفية السبورة', onClick: pickBg },\n"
            "      { icon: 'clist', label: 'قائمة أسماء الفصل', onClick: openClassList },\n")
    # laser tool on the teacher board
    m = re.search(r"    tools: \[([^\]]*'lasso'[^\]]*)\],\n    colors: \['#15213a', '#2f5bd3', '#e0242f'", s); assert m, 'teacher tools'
    s = s[:m.start(1)] + m.group(1).replace("'lasso'", "'lasso', 'laser'") + s[m.end(1):]
    s = rep(s, "lasso: 'قص حر: ارسم حول أي جزء لحذفه' };", "lasso: 'قص حر: ارسم حول أي جزء لحذفه', laser: 'مؤشر ليزر: يراه الطلاب ولا يكتب' };")
    s = rep(s, "    if (t.t === 'lasso') {", "    if (t.t === 'laser') { e.preventDefault(); this.ov.setPointerCapture(e.pointerId); this.pid = e.pointerId; this.laz = true; this.onLaser && this.onLaser(x, y); return }\n    if (t.t === 'lasso') {")
    s = rep(s, "    if (this.las && e.pointerId === this.pid) {\n      const P = this.las.pts",
            "    if (this.laz && e.pointerId === this.pid) { const [x, y] = this.pt(e); this.onLaser && this.onLaser(x, y); return }\n    if (this.las && e.pointerId === this.pid) {\n      const P = this.las.pts")
    s = rep(s, "    if (this.las && e.pointerId === this.pid) {\n      const { pts, svg } = this.las;",
            "    if (this.laz && e.pointerId === this.pid) { this.laz = false; return }\n    if (this.las && e.pointerId === this.pid) {\n      const { pts, svg } = this.las;")
    s = rep(s, "  constructor(host, { layers, target, tool, sink, onStamp, onCut, onErase, onLasso }) {\n    this.onStamp = onStamp; this.onCut = onCut; this.onErase = onErase; this.onLasso = onLasso;",
            "  constructor(host, { layers, target, tool, sink, onStamp, onCut, onErase, onLasso, onLaser }) {\n    this.onStamp = onStamp; this.onCut = onCut; this.onErase = onErase; this.onLasso = onLasso; this.onLaser = onLaser;")
    s = rep(s, "  tBoard = new Board($('#tBoard'), { layers: ['bg', 't'], target: 't', tool: tTool.get, onLasso: tLasso,",
            "  tBoard = new Board($('#tBoard'), { layers: ['bg', 't'], target: 't', tool: tTool.get, onLasso: tLasso, onLaser: sendLaser,")
    # curtain on both sides (from meta)
    # student: laser + leave clean
    s = rep(s, "  S.unsubs.push(DB.onValue(b + '/meta', mt => {", "  S.unsubs.push(DB.onValue(b + '/laser', v => { if (v && v.t && DB.now() - v.t < 4000) laserAt($('#sBoard'), v.x, v.y) }));\n  S.unsubs.push(DB.onValue(b + '/meta', mt => {")
    # join: pick the name from the class list
    if target == 'rb':
        s = rep(s, "  if (nm) { inp.value = nm; inp.readOnly = true;", "  if (nm) { const pk = $('#jList'); if (pk) pk.hidden = true; inp.hidden = false; inp.value = nm; inp.readOnly = true;")
    s = rep(s, "async function lookupTeacher(code) {\n", "async function lookupTeacher(code) {\n  classPicker(code);\n")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
