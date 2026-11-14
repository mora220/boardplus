"""Attendance and participation, for BoardPlus and ragabboard.
Every class is recorded for the teacher (who joined, and their points), and the teacher prints or exports a
report for any period (this week by default), with absences when a class name list is used.
Records: <bank>/att/<YYYYMMDD_code> = {d, code, cls:{id,name,names}|null, s:[{n, p}]}"""
import json

ADD_I18N = {
    "كشف الحضور والمشاركة": "Attendance and participation", "هذا الأسبوع": "This week", "الأسبوع الماضي": "Last week", "هذا الشهر": "This month",
    "كل الحصص": "All classes", "الاسم": "Name", "الحضور": "Attendance", "مجموع النقاط": "Total points", "طباعة": "Print", "تنزيل Excel": "Download Excel",
    "غائب": "Absent", "لا توجد حصص في هذه الفترة": "No classes in this period", "حصة": "class", "حصص": "classes",
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
.att .tot{font-weight:800;background:var(--surface-2)}
"""

JS = r"""
/* ======================= attendance and participation ======================= */
const ATT = { last: '', t: 0, start: 0 };
const dKey = t => { const d = new Date(t); return d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0') };
function attSync(force) {
  if (ROLE !== 't' || !T.code || T.watch || !T.st || !T.st.size) return;
  const now = Date.now(); if (!force && now - ATT.t < 4000) { clearTimeout(ATT.tm); ATT.tm = setTimeout(() => attSync(true), 4200); return } ATT.t = now;
  if (ATT.code !== T.code) { ATT.code = T.code; ATT.last = ''; ATT.start = +(ls.get('rb_att_' + T.code) || 0) || now; ls.set('rb_att_' + T.code, ATT.start) }
  const by = new Map(); T.st.forEach((s, sid) => { const n = String((s.info && s.info.name) || '').trim(); if (!n) return; by.set(n, Math.max(by.get(n) || 0, scoreOf(sid))) });
  const cl = T.clist && T.clist.names ? { id: T.clist.id || '', name: T.clist.name || '', names: T.clist.names } : null;
  const rec = { d: ATT.start, code: T.code, cls: cl, s: [...by].map(([n, p]) => ({ n, p })) };
  const js = JSON.stringify(rec); if (js === ATT.last) return; ATT.last = js;
  DB.set(`${BANK()}/att/${dKey(ATT.start)}_${T.code}`, rec).catch(() => { ATT.last = '' });
}
function weekRange(off) { const d = new Date(); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() - d.getDay() + off * 7); const e = new Date(d); e.setDate(e.getDate() + 6); return [d, e] }   // Sunday .. Saturday
async function openAttendance() {
  attSync(true);
  const all = (await DB.get(BANK() + '/att').catch(() => null)) || {}, now = Date.now();
  const old = Object.keys(all).filter(k => now - (all[k] && all[k].d || 0) > 200 * 864e5); old.forEach(k => { DB.remove(`${BANK()}/att/${k}`); delete all[k] });
  const recs = Object.values(all).filter(r => r && r.d).sort((a, b) => a.d - b.d);
  const classes = new Map(); recs.forEach(r => { if (r.cls && r.cls.id) classes.set(r.cls.id, r.cls.name || 'الفصل') });
  const iso = d => new Date(d.getTime() - d.getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
  let [from, to] = weekRange(0), cls = T.clist && T.clist.id && classes.has(T.clist.id) ? T.clist.id : '';
  const fmtD = t => new Intl.DateTimeFormat(EN ? 'en-GB' : 'ar-SA', { weekday: 'short', day: 'numeric', month: 'numeric' }).format(new Date(t));
  const fmtT = t => new Intl.DateTimeFormat(EN ? 'en-GB' : 'ar-SA', { hour: 'numeric', minute: '2-digit' }).format(new Date(t));
  const build = () => {
    const a = from.getTime(), b = to.getTime() + 864e5 - 1;
    const rs = recs.filter(r => r.d >= a && r.d <= b && (!cls || (r.cls && r.cls.id === cls)));
    const names = new Set(); rs.forEach(r => { (r.cls && r.cls.names || []).forEach(n => names.add(n)); (r.s || []).forEach(x => names.add(x.n)) });
    const rows = [...names].sort((x, y) => x.localeCompare(y, 'ar')).map(n => {
      let pres = 0, tot = 0; const cells = rs.map(r => { const hit = (r.s || []).find(x => x.n === n); if (hit) { pres++; tot += hit.p || 0; return { c: 'pr', v: hit.p ? hit.p : '✓' } } return (r.cls && (r.cls.names || []).includes(n)) ? { c: 'ab', v: 'غ' } : { c: '', v: '—' } });
      return { n, cells, pres, tot };
    });
    return { rs, rows };
  };
  const table = ({ rs, rows }) => rs.length ? `<table class="att"><thead><tr><th>الاسم</th>${rs.map(r => `<th>${fmtD(r.d)}<br><small>${fmtT(r.d)}</small></th>`).join('')}<th>الحضور</th><th>مجموع النقاط</th></tr></thead>
    <tbody>${rows.map(x => `<tr><td>${esc(x.n)}</td>${x.cells.map(c => `<td class="${c.c}">${c.v}</td>`).join('')}<td class="tot">${x.pres}/${rs.length}</td><td class="tot">${x.tot}</td></tr>`).join('')}</tbody></table>`
    : `<p class="muted" style="padding:20px;text-align:center">لا توجد حصص في هذه الفترة</p>`;
  modal(`<h3>📊 كشف الحضور والمشاركة</h3>
    <div class="atttop"><div class="seg" id="atR"><button data-r="0" class="on">هذا الأسبوع</button><button data-r="-1">الأسبوع الماضي</button><button data-r="m">هذا الشهر</button></div>
      <input type="date" class="inp" id="atA"><span>→</span><input type="date" class="inp" id="atB">
      <select class="inp" id="atC"><option value="">كل الحصص</option>${[...classes].map(([id, n]) => `<option value="${id}">${esc(n)}</option>`).join('')}</select></div>
    <div class="attwrap" id="atT"></div>
    <div class="row"><button class="btn" data-close>إغلاق</button><button class="btn" id="atX">⬇ تنزيل Excel</button><button class="btn pri" id="atP">🖨 طباعة</button></div>`, (v, close) => {
    v.querySelector('.dlg').classList.add('attdlg');
    const $v = q => v.querySelector(q);
    const draw = () => { $v('#atA').value = iso(from); $v('#atB').value = iso(to); $v('#atC').value = cls; $v('#atT').innerHTML = table(build()) };
    $v('#atR').onclick = e => { const b = e.target.closest('[data-r]'); if (!b) return; v.querySelectorAll('#atR button').forEach(x => x.classList.toggle('on', x === b)); if (b.dataset.r === 'm') { from = new Date(); from.setHours(0, 0, 0, 0); from.setDate(1); to = new Date(from.getFullYear(), from.getMonth() + 1, 0) } else [from, to] = weekRange(+b.dataset.r); draw() };
    $v('#atA').onchange = e => { if (e.target.value) { from = new Date(e.target.value + 'T00:00'); draw() } };
    $v('#atB').onchange = e => { if (e.target.value) { to = new Date(e.target.value + 'T00:00'); draw() } };
    $v('#atC').onchange = e => { cls = e.target.value; draw() };
    const title = () => `كشف الحضور والمشاركة${cls ? ' · ' + classes.get(cls) : ''} · ${iso(from)} → ${iso(to)}`;
    $v('#atP').onclick = () => {
      const f = document.createElement('iframe'); f.style.cssText = 'position:fixed;width:0;height:0;border:0;left:-9999px'; document.body.appendChild(f);
      const d = f.contentDocument; d.open(); d.write(`<!doctype html><html dir="${EN ? 'ltr' : 'rtl'}"><head><meta charset="utf-8"><title>${esc(title())}</title><style>
        body{font-family:"IBM Plex Sans Arabic",Tahoma,sans-serif;margin:18px;color:#111}h2{margin:0 0 4px;font-size:18px}p{margin:0 0 12px;color:#555;font-size:12px}
        table{border-collapse:collapse;width:100%;font-size:11px}th,td{border:1px solid #999;padding:4px 5px;text-align:center}th{background:#eef2f8}td:first-child{text-align:start;white-space:nowrap}
        .pr{background:#e8f7ee}.ab{background:#fdecee;color:#c0182c;font-weight:700}.tot{font-weight:700;background:#f3f4f6}@page{size:landscape;margin:10mm}</style></head>
        <body><h2>${esc(title())}</h2><p>${esc(ME.name || '')} · BoardPlus</p>${table(build())}</body></html>`); d.close();
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
    s = rep(s, "      { icon: 'clist', label: 'قائمة أسماء الفصل', onClick: openClassList },\n",
            "      { icon: 'clist', label: 'قائمة أسماء الفصل', onClick: openClassList },\n      { icon: 'trophy', label: 'كشف الحضور والمشاركة', color: '#1f9d55', onClick: openAttendance },\n")
    # the teacher keeps the class list of the session in memory, and records joins as well as points
    s = rep(s, "  T.unsubs.push(DB.onValue(b + '/pts', v => { T.pts = v || {}; refreshScores() }));",
            "  T.unsubs.push(DB.onValue(b + '/clist', v => { T.clist = v || null; attSync() }));\n  T.unsubs.push(DB.onValue(b + '/pts', v => { T.pts = v || {}; refreshScores() }));\n  clearInterval(ATT.iv); ATT.iv = setInterval(() => attSync(), 30000);")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
