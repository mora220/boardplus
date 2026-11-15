"""Attendance and participation, for BoardPlus and ragabboard.
Every class is recorded for the teacher (who joined, and their points), and the teacher prints or exports a
report for any period (this week by default), with absences when a class name list is used.
Records: <bank>/att/<YYYYMMDD_code> = {d, code, cls:{id,name,names}|null, s:[{n, p}]}"""
import json

ADD_I18N = {
    "كشف الحضور والمشاركة": "Attendance and participation", "هذا الأسبوع": "This week", "الأسبوع الماضي": "Last week", "هذا الشهر": "This month",
    "كل الحصص": "All classes", "الاسم": "Name", "الحضور": "Attendance", "مجموع النقاط": "Total points", "طباعة": "Print", "تنزيل Excel": "Download Excel",
    "غائب": "Absent", "لا توجد حصص في هذه الفترة": "No classes in this period", "حصة": "class", "حصص": "classes", "حذف هذه الحصة من الكشف؟": "Delete this class from the report?", "تغيير إلى غائب؟": "Change to absent?", "اضغط على خانة الطالب لتغييره بين حاضر وغائب · 🗑 فوق التاريخ لحذف الحصة": "Tap a student's cell to switch present/absent · 🗑 above a date deletes that class",
}

CSS = r"""
.attdlg{width:min(1100px,94vw)!important;max-width:none!important}
.atttop{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.atttop .inp{width:auto}
.atttop .seg button.on{background:var(--accent);color:#fff}
.attwrap{overflow:auto;max-height:58vh;border:1px solid var(--line);border-radius:12px}
.att{border-collapse:collapse;width:100%;font-size:13px}
.att th,.att td{border:1px solid var(--line);padding:6px 8px;text-align:center;white-space:nowrap}
.att th{background:var(--surface-2);position:sticky;top:0;z-index:1;font-size:12px}
.att td:first-child,.att th:first-child{text-align:start;position:sticky;inset-inline-start:0;background:var(--surface);z-index:2}
.att th:first-child{z-index:3;background:var(--surface-2)}
.att .pr{background:#e8f7ee;color:#137a3f;font-weight:700}
.att .ab{background:#fdecee;color:#c0182c;font-weight:700}
.att td[data-k]{cursor:pointer}.att td[data-k]:hover{outline:2px solid var(--accent);outline-offset:-2px}
.att .mn{background:#fff6dd;color:#8a6100}
.attdel{border:0;background:none;cursor:pointer;font-size:13px;padding:0 2px;opacity:.6}.attdel:hover{opacity:1}
.att .tot{font-weight:800;background:var(--surface-2)}
"""

JS = r"""
/* ======================= attendance and participation ======================= */
const ATT = { last: '', t: 0, start: 0 };
const dKey = t => { const d = new Date(t); return d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0') };
function attSync(force) {
  if (ROLE !== 't' || !T.code || T.watch || !T.st || !T.st.size || ATT.skip === T.code) return;
  const now = Date.now(); if (!force && now - ATT.t < 4000) { clearTimeout(ATT.tm); ATT.tm = setTimeout(() => attSync(true), 4200); return } ATT.t = now;
  if (ATT.code !== T.code) { ATT.code = T.code; ATT.last = ''; ATT.start = +(ls.get('rb_att_' + T.code) || 0) || now; ls.set('rb_att_' + T.code, ATT.start); ATT.man = null; const c0 = T.code; DB.get(`${BANK()}/att/${dKey(ATT.start)}_${c0}/man`).then(v => { if (v && ATT.code === c0) { ATT.man = { ...v, ...(ATT.man || {}) }; ATT.last = ''; attSync(true) } }).catch(() => {}) }
  const by = new Map(); T.st.forEach((s, sid) => { const n = String((s.info && s.info.name) || '').trim(); if (!n) return; by.set(n, Math.max(by.get(n) || 0, scoreOf(sid))) });
  const cl = T.clist && T.clist.names ? { id: T.clist.id || '', name: T.clist.name || '', names: T.clist.names } : null;
  const rec = { d: ATT.start, code: T.code, cls: cl, s: [...by].map(([n, p]) => ({ n, p })), man: ATT.man || null };
  const js = JSON.stringify(rec); if (js === ATT.last) return; ATT.last = js;
  DB.set(`${BANK()}/att/${dKey(ATT.start)}_${T.code}`, rec).catch(() => { ATT.last = '' });
}
function weekRange(off) { const d = new Date(); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() - d.getDay() + off * 7); const e = new Date(d); e.setDate(e.getDate() + 6); return [d, e] }   // Sunday .. Saturday
async function openAttendance() {
  attSync(true);
  const [all0, saved] = await Promise.all([DB.get(BANK() + '/att').catch(() => null), DB.get(BANK() + '/classes').catch(() => null)]), all = all0 || {}, now = Date.now(), defs = saved || {};
  const old = Object.keys(all).filter(k => now - (all[k] && all[k].d || 0) > 200 * 864e5); old.forEach(k => { DB.remove(`${BANK()}/att/${k}`); delete all[k] });
  let recs = Object.entries(all).filter(([k, r]) => r && r.d).map(([k, r]) => ({ ...r, k })).sort((a, b) => a.d - b.d);
  const classes = new Map(); recs.forEach(r => { if (r.cls && r.cls.id) classes.set(r.cls.id, r.cls.name || 'الفصل') }); Object.entries(defs).forEach(([id, c]) => classes.set(id, (c && c.name) || 'الفصل'));
  const hasFree = recs.some(r => !r.cls || !r.cls.id);
  const pres = r => { const m = r.man || {}, out = new Map(); (r.s || []).forEach(x => { if (m[x.n] !== 0) out.set(x.n, { p: x.p || 0 }) }); Object.keys(m).forEach(n => { if (m[n] === 1 && !out.has(n)) out.set(n, { p: 0, man: 1 }) }); return out };
  const iso = d => new Date(d.getTime() - d.getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
  let [from, to] = weekRange(0), cls = T.clist && T.clist.id && classes.has(T.clist.id) ? T.clist.id : (classes.size ? [...classes.keys()][0] : 'free');
  const fmtD = t => new Intl.DateTimeFormat(EN ? 'en-GB' : 'ar-SA', { weekday: 'short', day: 'numeric', month: 'numeric' }).format(new Date(t));
  const fmtT = t => new Intl.DateTimeFormat(EN ? 'en-GB' : 'ar-SA', { hour: 'numeric', minute: '2-digit' }).format(new Date(t));
  const build = () => {
    const a = from.getTime(), b = to.getTime() + 864e5 - 1;
    const rs = recs.filter(r => r.d >= a && r.d <= b && (cls === 'free' ? !(r.cls && r.cls.id) : (r.cls && r.cls.id === cls)));
    let names = new Set();
    if (cls === 'free') rs.forEach(r => pres(r).forEach((v, n) => names.add(n)));
    else if (defs[cls] && defs[cls].names) names = new Set(defs[cls].names);        // only this class's students
    else rs.forEach(r => (r.cls.names || []).forEach(n => names.add(n)));
    const rows = [...names].sort((x, y) => x.localeCompare(y, 'ar', { numeric: true })).map(n => {
      let np = 0, tot = 0; const cells = rs.map(r => { const hit = pres(r).get(n); if (hit) { np++; tot += hit.p; return { c: 'pr' + (hit.man ? ' mn' : ''), v: hit.p ? hit.p : '✓', k: r.k, n } } return cls !== 'free' ? { c: 'ab', v: 'غ', k: r.k, n } : { c: '', v: '—' } });
      return { n, cells, pres: np, tot };
    });
    return { rs, rows };
  };
  const table = ({ rs, rows }, ed) => rs.length ? `<table class="att"><thead><tr><th>الاسم</th>${rs.map(r => `<th>${fmtD(r.d)}<br><small>${fmtT(r.d)}</small>${ed ? `<button class="attdel" data-del="${r.k}" title="حذف هذه الحصة">🗑</button>` : ''}</th>`).join('')}<th>الحضور</th><th>مجموع النقاط</th></tr></thead>
    <tbody>${rows.map(x => `<tr><td>${esc(x.n)}</td>${x.cells.map(c => `<td class="${c.c}"${ed && c.k ? ` data-k="${c.k}" data-n="${esc(c.n)}" title="اضغط لتغيير الحضور"` : ''}>${c.v}</td>`).join('')}<td class="tot">${x.pres}/${rs.length}</td><td class="tot">${x.tot}</td></tr>`).join('')}</tbody></table>`
    : `<p class="muted" style="padding:20px;text-align:center">لا توجد حصص في هذه الفترة</p>`;
  modal(`<h3>📊 كشف الحضور والمشاركة</h3>
    <div class="atttop"><div class="seg" id="atR"><button data-r="0" class="on">هذا الأسبوع</button><button data-r="-1">الأسبوع الماضي</button><button data-r="m">هذا الشهر</button></div>
      <input type="date" class="inp" id="atA"><span>→</span><input type="date" class="inp" id="atB">
      <select class="inp" id="atC">${[...classes].map(([id, n]) => `<option value="${id}">👥 ${esc(n)}</option>`).join('')}${hasFree || !classes.size ? '<option value="free">✍️ دخول حر</option>' : ''}</select></div>
    <p class="muted" style="margin:0;font-size:12.5px">اضغط على خانة الطالب لتغييره بين حاضر وغائب · 🗑 فوق التاريخ لحذف الحصة</p>
    <div id="atU"></div><div class="attwrap" id="atT"></div>
    <div class="row"><button class="btn" data-close>إغلاق</button><button class="btn" id="atX">⬇ تنزيل Excel</button><button class="btn pri" id="atP">🖨 طباعة</button></div>`, (v, close) => {
    v.querySelector('.dlg').classList.add('attdlg');
    const $v = q => v.querySelector(q);
    const draw = () => { $v('#atU').innerHTML = ATT.trash ? `<button class="btn" id="atUndo" type="button">↩ استرجاع آخر حصة محذوفة</button>` : ''; $v('#atA').value = iso(from); $v('#atB').value = iso(to); $v('#atC').value = cls; $v('#atT').innerHTML = table(build(), true) };
    if (ATT.trash === undefined) { try { ATT.trash = JSON.parse(ls.get('rb_att_trash') || 'null') } catch (x) { ATT.trash = null } }
    v.querySelector('.dlg').onclick = async e => {
      const del = e.target.closest('[data-del]'), td = e.target.closest('td[data-k]');
      if (del) { const r = recs.find(x => x.k === del.dataset.del); if (!r || !(await ask('حذف هذه الحصة من الكشف؟', `${fmtD(r.d)} ${fmtT(r.d)} · سيُحذف حضورها ومشاركتها`, 'حذف'))) return;
        await DB.remove(`${BANK()}/att/${r.k}`); if (r.code === T.code) { ATT.skip = T.code } recs = recs.filter(x => x !== r); const { k, ...rec } = r; ATT.trash = { k, rec }; try { ls.set('rb_att_trash', JSON.stringify(ATT.trash)) } catch (x) {} return draw() }
      if (e.target.closest('#atUndo')) { const t = ATT.trash; if (!t) return; await DB.set(`${BANK()}/att/${t.k}`, t.rec); if (t.rec.code === ATT.skip) ATT.skip = null; recs.push({ ...t.rec, k: t.k }); recs.sort((a, b) => a.d - b.d); ATT.trash = null; ls.set('rb_att_trash', ''); toast('رجعت الحصة إلى الكشف'); return draw() }
      if (!td) return; const r = recs.find(x => x.k === td.dataset.k), n = td.dataset.n; if (!r) return;
      const now = pres(r).get(n), m = { ...(r.man || {}) };
      if (now) { if (now.p && !(await ask('تغيير إلى غائب؟', `${n} · ستُحذف نقاطه في هذه الحصة (${now.p})`, 'غائب'))) return; m[n] = 0 } else m[n] = 1;
      r.man = m; await DB.set(`${BANK()}/att/${r.k}/man`, m); if (r.code === T.code && ATT.code === T.code) { ATT.man = m; ATT.last = '' } draw();
    };
    $v('#atR').onclick = e => { const b = e.target.closest('[data-r]'); if (!b) return; v.querySelectorAll('#atR button').forEach(x => x.classList.toggle('on', x === b)); if (b.dataset.r === 'm') { from = new Date(); from.setHours(0, 0, 0, 0); from.setDate(1); to = new Date(from.getFullYear(), from.getMonth() + 1, 0) } else [from, to] = weekRange(+b.dataset.r); draw() };
    $v('#atA').onchange = e => { if (e.target.value) { from = new Date(e.target.value + 'T00:00'); draw() } };
    $v('#atB').onchange = e => { if (e.target.value) { to = new Date(e.target.value + 'T00:00'); draw() } };
    $v('#atC').onchange = e => { cls = e.target.value; draw() };
    const title = () => `كشف الحضور والمشاركة · ${cls === 'free' ? 'دخول حر' : classes.get(cls)} · ${iso(from)} → ${iso(to)}`;
    $v('#atP').onclick = () => {
      const f = document.createElement('iframe'); f.style.cssText = 'position:fixed;width:0;height:0;border:0;left:-9999px'; document.body.appendChild(f);
      const d = f.contentDocument; d.open(); d.write(`<!doctype html><html dir="${EN ? 'ltr' : 'rtl'}"><head><meta charset="utf-8"><title>${esc(title())}</title><style>
        body{font-family:"IBM Plex Sans Arabic",Tahoma,sans-serif;margin:18px;color:#111}h2{margin:0 0 4px;font-size:18px}p{margin:0 0 12px;color:#555;font-size:12px}
        table{border-collapse:collapse;width:100%;font-size:11px}th,td{border:1px solid #999;padding:4px 5px;text-align:center}th{background:#eef2f8}td:first-child{text-align:start;white-space:nowrap}
        .pr{background:#e8f7ee}.ab{background:#fdecee;color:#c0182c;font-weight:700}.tot{font-weight:700;background:#f3f4f6}@page{size:landscape;margin:10mm}</style></head>
        <body><h2>${esc(title())}</h2><p>${esc(ME.name || '')}</p>${table(build(), false)}</body></html>`); d.close();
      setTimeout(() => { try { f.contentWindow.focus(); f.contentWindow.print() } catch (e) {} setTimeout(() => f.remove(), 2000) }, 400);
    };
    $v('#atX').onclick = () => {
      const { rs, rows } = build(), q = x => `"${String(x).replace(/"/g, '""')}"`;
      const csv = [['الاسم', ...rs.map(r => fmtD(r.d) + ' ' + fmtT(r.d)), 'الحضور', 'مجموع النقاط'].map(q).join(','), ...rows.map(x => [x.n, ...x.cells.map(c => c.v === '—' ? '' : c.v), `${x.pres}/${rs.length}`, x.tot].map(q).join(','))].join('\r\n');
      const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' })); a.download = `attendance_${iso(from)}_${iso(to)}.csv`; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 3000);
    };
    draw();
  });
}
"""


def apply(s, rep, target):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, "function refreshScores() {\n", "function refreshScores() {\n  attSync();\n")
    s = rep(s, "  T.st.set(sid, s);\n", "  T.st.set(sid, s); setTimeout(() => attSync(), 300);\n")
    s = rep(s, "      { icon: 'clist', label: 'قائمة أسماء الفصل', onClick: openClassList },\n",
            "      { icon: 'clist', label: 'قائمة أسماء الفصل', onClick: openClassList },\n      { icon: 'trophy', label: 'كشف الحضور والمشاركة', color: '#1f9d55', onClick: openAttendance },\n")
    # the teacher keeps the class list of the session in memory, and records joins as well as points
    s = rep(s, "  T.unsubs.push(DB.onValue(b + '/pts', v => { T.pts = v || {}; refreshScores() }));",
            "  T.unsubs.push(DB.onValue(b + '/clist', v => { T.clist = v || null; attSync() }));\n  T.unsubs.push(DB.onValue(b + '/pts', v => { T.pts = v || {}; refreshScores() }));\n  clearInterval(ATT.iv); ATT.iv = setInterval(() => attSync(), 30000);")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
