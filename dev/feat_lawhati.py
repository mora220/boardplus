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
.jpick{width:100%;height:48px;border-radius:12px;border:1.5px solid var(--line);background:var(--surface);font:inherit;font-size:16px;padding:0 12px;color:var(--ink)}
.curt{position:absolute;left:0;right:0;bottom:0;z-index:5;pointer-events:none;display:grid;place-items:center;font-size:42px;border-radius:inherit}
.curt.s{background:repeating-linear-gradient(90deg,#6b2342 0 26px,#7d2a4e 26px 52px);box-shadow:inset 0 10px 18px rgba(0,0,0,.35)}
.curt.t{background:rgba(107,35,66,.38);border-top:3px dashed #7d2a4e}
.curt .ch{position:absolute;top:-19px;left:50%;transform:translateX(-50%);pointer-events:auto;cursor:ns-resize;touch-action:none;background:#7d2a4e;color:#fff;border-radius:99px;padding:6px 16px;font-size:13px;font-weight:700;white-space:nowrap;box-shadow:var(--shadow)}
.laz{position:absolute;z-index:6;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;pointer-events:none;background:radial-gradient(circle,#fff 0 18%,#ff2d3d 32%,rgba(255,45,61,.35) 60%,transparent 72%);box-shadow:0 0 16px 6px rgba(255,45,61,.45);transition:left .06s linear,top .06s linear,opacity .4s}
"""

JS = r"""
/* ======================= graph of functions ======================= */
const FXC = new Map();
function compileFx(src) {
  const key = String(src); if (FXC.has(key)) return FXC.get(key);
  let e = key.toLowerCase().replace(/[×]/g, '*').replace(/[÷]/g, '/').replace(/[−–]/g, '-').replace(/π/g, 'pi').replace(/√/g, 'sqrt').replace(/\s+/g, '').replace(/^y=|^f\(x\)=/, '');
  if (!e || !/^[0-9x+\-*/^().a-z,]*$/.test(e)) throw new Error('bad');
  const F = { sin: 'Math.sin', cos: 'Math.cos', tan: 'Math.tan', asin: 'Math.asin', acos: 'Math.acos', atan: 'Math.atan', sqrt: 'Math.sqrt', abs: 'Math.abs', ln: 'Math.log', log: 'Math.log10', exp: 'Math.exp' };
  const tk = e.match(/\d+\.?\d*|\.\d+|[a-z]+|[-+*/^(),]/g) || []; if (tk.join('') !== e) throw new Error('bad');
  let out = '', prev = '';
  const val = t => /^[\d.]/.test(t) || t === 'x' || t === 'pi' || t === 'e' || t === ')';
  for (let t of tk) {
    if (/^[a-z]+$/.test(t) && !F[t] && t !== 'x' && t !== 'pi' && t !== 'e') {
      const parts = t.match(/sqrt|asin|acos|atan|sin|cos|tan|abs|exp|ln|log|pi|x|e/g); if (!parts || parts.join('') !== t) throw new Error('bad');   // e.g. "2xsin"
      for (const q of parts) { if (val(prev) && (val(q) || F[q])) out += '*'; out += F[q] || (q === 'pi' ? 'Math.PI' : q === 'e' ? 'Math.E' : q); prev = q } continue;
    }
    const isStart = val(t) && t !== ')' || F[t] || t === '(';
    if (val(prev) && isStart) out += '*';
    out += t === '^' ? '**' : F[t] || (t === 'pi' ? 'Math.PI' : t === 'e' ? 'Math.E' : t); prev = t;
  }
  const fn = new Function('x', '"use strict";return (' + out + ')'); fn(1); FXC.set(key, fn); return fn;
}
const niceStep = r => { const p = Math.pow(10, Math.floor(Math.log10(r / 6))), m = r / 6 / p; return (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p };
function drawGraph(ctx, s, k) {
  const X = s.x * k, Y = s.y * k, Wd = (s.gw || 800) * k, Ht = (s.gh || 560) * k, x0 = +s.x0 || -10, x1 = +s.x1 > x0 ? +s.x1 : x0 + 20;
  const fs = String(s.f || '').split(';').map(t => t.trim()).filter(Boolean).slice(0, 4), cols = ['#2f5bd3', '#e0242f', '#1f9d55', '#7b3fc4'];
  const fns = fs.map(f => { try { return compileFx(f) } catch (e) { return null } }), N = Math.max(120, Math.round((s.gw || 800) * 1.2));
  let lo = Infinity, hi = -Infinity; const pts = fns.map(fn => { const a = []; for (let i = 0; i <= N; i++) { const x = x0 + (x1 - x0) * i / N; let y = NaN; try { y = fn ? fn(x) : NaN } catch (e) {} a.push(isFinite(y) ? y : NaN); if (isFinite(y) && Math.abs(y) < 1e6) { lo = Math.min(lo, y); hi = Math.max(hi, y) } } return a });
  if (!isFinite(lo)) { lo = -10; hi = 10 } lo = Math.min(lo, 0); hi = Math.max(hi, 0); if (hi - lo < 1e-6) { hi += 1; lo -= 1 }
  const pad = (hi - lo) * .08; lo -= pad; hi += pad;
  const sx = v => X + (v - x0) / (x1 - x0) * Wd, sy = v => Y + Ht - (v - lo) / (hi - lo) * Ht;
  ctx.save(); ctx.fillStyle = '#fff'; ctx.fillRect(X, Y, Wd, Ht); ctx.beginPath(); ctx.rect(X, Y, Wd, Ht); ctx.clip();
  const fz = Math.max(9, 15 * k); ctx.font = `500 ${fz}px "IBM Plex Sans Arabic",sans-serif`; ctx.direction = 'ltr';
  const gx = niceStep(x1 - x0), gy = niceStep(hi - lo);
  ctx.lineWidth = Math.max(1, k); ctx.strokeStyle = '#e3e8f3';
  for (let v = Math.ceil(x0 / gx) * gx; v <= x1; v += gx) { ctx.beginPath(); ctx.moveTo(sx(v), Y); ctx.lineTo(sx(v), Y + Ht); ctx.stroke() }
  for (let v = Math.ceil(lo / gy) * gy; v <= hi; v += gy) { ctx.beginPath(); ctx.moveTo(X, sy(v)); ctx.lineTo(X + Wd, sy(v)); ctx.stroke() }
  const ax = Math.min(Math.max(sx(0), X), X + Wd), ay = Math.min(Math.max(sy(0), Y), Y + Ht);
  ctx.strokeStyle = '#15213a'; ctx.lineWidth = Math.max(1.4, 2.2 * k); ctx.beginPath(); ctx.moveTo(X, ay); ctx.lineTo(X + Wd, ay); ctx.moveTo(ax, Y); ctx.lineTo(ax, Y + Ht); ctx.stroke();
  ctx.fillStyle = '#5b6b85'; ctx.textAlign = 'center'; ctx.textBaseline = 'top';
  const fmt = v => Math.abs(v) < 1e-9 ? '0' : +v.toPrecision(4) + '';
  for (let v = Math.ceil(x0 / gx) * gx; v <= x1; v += gx) if (Math.abs(v) > 1e-9) ctx.fillText(fmt(v), sx(v), Math.min(ay + 4 * k, Y + Ht - fz - 2));
  ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
  for (let v = Math.ceil(lo / gy) * gy; v <= hi; v += gy) if (Math.abs(v) > 1e-9) ctx.fillText(fmt(v), Math.max(ax - 5 * k, X + 4 * fz), sy(v));
  pts.forEach((a, j) => {
    ctx.strokeStyle = cols[j]; ctx.lineWidth = Math.max(2, 3.6 * k); ctx.lineJoin = 'round'; ctx.beginPath(); let on = false, py = 0;
    a.forEach((y, i) => { const x = x0 + (x1 - x0) * i / N; if (!isFinite(y) || (on && Math.abs(y - py) > (hi - lo) * 1.5)) { on = false; if (!isFinite(y)) return } const X1 = sx(x), Y1 = sy(y); on ? ctx.lineTo(X1, Y1) : ctx.moveTo(X1, Y1); on = true; py = y });
    ctx.stroke();
  });
  ctx.textAlign = 'left'; ctx.textBaseline = 'top'; ctx.font = `700 ${Math.max(10, 18 * k)}px "IBM Plex Sans Arabic",sans-serif`;
  fs.forEach((f, j) => { ctx.fillStyle = 'rgba(255,255,255,.85)'; const t = 'y = ' + f, w = ctx.measureText(t).width; ctx.fillRect(X + 8 * k, Y + (8 + j * 26) * k, w + 10 * k, 24 * k); ctx.fillStyle = fns[j] ? cols[j] : '#999'; ctx.fillText(t, X + 13 * k, Y + (10 + j * 26) * k) });
  ctx.restore(); ctx.save(); ctx.strokeStyle = '#c9d3e6'; ctx.lineWidth = Math.max(1, 1.5 * k); ctx.strokeRect(X, Y, Wd, Ht); ctx.restore();
}
function openGraph() {
  const last = ls.get('rb_fx') || 'x^2 - 4';
  modal(`<div class="gform"><h3>${svgI('graph')} رسم دالة</h3>
    <div class="grow"><b dir="ltr">y =</b><input class="inp" id="gF" dir="ltr" value="${esc(last)}" placeholder="x^2 - 4 ; 2x + 1"></div>
    <div class="ex">${['x^2 - 4', '2x + 1', 'sqrt(x)', '1/x', 'sin(x)', 'abs(x) ; -x + 3'].map(x => `<button data-ex="${esc(x)}">${esc(x)}</button>`).join('')}</div>
    <div class="grow"><span>من</span><input class="inp num xr" id="gA" value="${ls.get('rb_fxa') || -10}" dir="ltr"><span>إلى</span><input class="inp num xr" id="gB" value="${ls.get('rb_fxb') || 10}" dir="ltr"></div>
    <small class="muted">اكتب الدالة كما تكتبها على الورق، وافصل بين أكثر من دالة بفاصلة منقوطة ;</small>
    <canvas id="gPrev" width="500" height="350"></canvas><p class="err" id="gErr"></p>
    <div class="row"><button class="btn" data-close>إلغاء</button><button class="btn pri" id="gGo">${svgI('graph')} ارسم</button></div></div>`, (v, close) => {
    const $v = q => v.querySelector(q), item = () => ({ t: 'graph', x: Math.round((W - 820) / 2), y: Math.round((H - 560) / 2), gw: 820, gh: 560, f: $v('#gF').value.trim(), x0: +$v('#gA').value || -10, x1: +$v('#gB').value || 10 });
    const prev = () => { const it = item(), c = $v('#gPrev'), x = c.getContext('2d'); x.clearRect(0, 0, 500, 350); let ok = true; it.f.split(';').filter(t => t.trim()).forEach(f => { try { compileFx(f.trim()) } catch (e) { ok = false } }); $v('#gErr').textContent = ok && it.f ? '' : 'الدالة غير مفهومة'; drawGraph(x, { ...it, x: 0, y: 0, gw: 500, gh: 350 }, 1); return ok && !!it.f };
    ['#gF', '#gA', '#gB'].forEach(q => $v(q).addEventListener('input', prev));
    v.querySelectorAll('[data-ex]').forEach(b => b.onclick = () => { $v('#gF').value = b.dataset.ex; prev() });
    $v('#gGo').onclick = () => { if (!prev()) return; const it = item(); ls.set('rb_fx', it.f); ls.set('rb_fxa', it.x0); ls.set('rb_fxb', it.x1); tBoard.commit(uid(), it); close(); toast('📈 تم رسم الدالة') };
    $v('#gF').onkeydown = e => { if (e.key === 'Enter') $v('#gGo').click() };
    prev(); setTimeout(() => $v('#gF').focus(), 30);
  });
}
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
  let pk = $('#jPick'); const inp = $('#jName');
  const cl = /^\d{6}$/.test(code || '') ? await DB.get(`sessions/${code}/clist`).catch(() => null) : null;
  if ($('#jCode').value.replace(/\D/g, '') !== code) return;
  if (!cl || !cl.names || !cl.names.length || inp.readOnly) { if (pk) pk.hidden = true; inp.hidden = false; return }
  const roster = (await DB.get(`sessions/${code}/roster`).catch(() => null)) || {}, used = new Set(Object.values(roster).filter(r => r && r.online).map(r => r.name));
  if (!pk) { pk = document.createElement('select'); pk.id = 'jPick'; pk.className = 'jpick'; inp.after(pk); pk.onchange = () => { inp.value = pk.value } }
  pk.innerHTML = `<option value="" disabled selected>اختر اسمك من القائمة</option>` + cl.names.map(n => `<option ${used.has(n) ? 'disabled' : ''} value="${esc(n)}">${esc(n)}${used.has(n) ? ' ✓' : ''}</option>`).join('');
  pk.hidden = false; inp.hidden = true; inp.value = '';
}
/* ======================= curtain ======================= */
function drawCurtain(c, isT) {
  const host = isT ? $('#tBoard') : $('#sBoard'); if (!host) return; let el = host.querySelector('.curt');
  if (!c || !c.on) { if (el) el.remove(); return }
  if (!el) {
    el = document.createElement('div'); el.className = 'curt ' + (isT ? 't' : 's'); el.innerHTML = isT ? '<span class="ch">⇕ اسحب لكشف السبورة للطلاب</span>' : '🎭'; host.appendChild(el);
    if (isT) { const h = el.firstElementChild; let drag = false, lt = 0;
      h.addEventListener('pointerdown', e => { drag = true; h.setPointerCapture(e.pointerId); e.preventDefault() });
      h.addEventListener('pointermove', e => { if (!drag) return; const r = host.getBoundingClientRect(), y = Math.max(0, Math.min(1, (e.clientY - r.top) / r.height)); el.style.top = y * 100 + '%'; const n = performance.now(); if (n - lt > 90) { lt = n; DB.update(`sessions/${T.code}/meta/curtain`, { y: Math.round(y * 1000) / 1000 }) } });
      const up = e => { if (!drag) return; drag = false; const r = host.getBoundingClientRect(), y = Math.max(0, Math.min(1, (e.clientY - r.top) / r.height)); DB.update(`sessions/${T.code}/meta/curtain`, { y: Math.round(y * 1000) / 1000 }) };
      h.addEventListener('pointerup', up); h.addEventListener('pointercancel', up); }
  }
  if (!isT || !el.firstElementChild.hasPointerCapture) el.style.top = (Math.max(0, Math.min(1, +c.y || 0)) * 100) + '%';
}
function toggleCurtain() { if (!T.code) return; const on = !(T.meta && T.meta.curtain && T.meta.curtain.on); DB.update(`sessions/${T.code}/meta`, { curtain: on ? { on: true, y: 0.12 } : null }) }
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
    s = rep(s, "  if (s.t === 'media') return drawMedia(ctx, s, k);", "  if (s.t === 'media') return drawMedia(ctx, s, k);\n  if (s.t === 'graph') return drawGraph(ctx, s, k);") if target == 'bp' else \
        rep(s, "function drawStroke(ctx, s, k) {\n  if (!s || !s.t) return;", "function drawStroke(ctx, s, k) {\n  if (!s || !s.t) return;\n  if (s.t === 'graph') return drawGraph(ctx, s, k);")
    s = rep(s, "function strokeBox(s) {\n", "function strokeBox(s) {\n  if (s.t === 'graph') return [s.x, s.y, s.x + (s.gw || 800), s.y + (s.gh || 560)];\n")
    if target == 'bp':
        s = rep(s, "if (s.wd) o.wd = Math.round(s.wd * k) }", "if (s.wd) o.wd = Math.round(s.wd * k); if (s.gw) { o.gw = Math.round(s.gw * k); o.gh = Math.round(s.gh * k) } }")
    # teacher buttons
    s = rep(s, "      { icon: 'bg', label: 'خلفية السبورة', onClick: pickBg },\n",
            "      { icon: 'bg', label: 'خلفية السبورة', onClick: pickBg },\n"
            "      { icon: 'graph', label: 'رسم دالة', color: '#2f5bd3', onClick: openGraph },\n"
            "      { icon: 'curtain', label: 'ستارة: أخفِ السبورة عن الطلاب واكشفها بالتدريج', color: '#7d2a4e', onClick: toggleCurtain },\n"
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
    s = rep(s, "    if (T.bg.type !== m.bgType) { T.bg.type = m.bgType; baseChanged() }\n", "    if (T.bg.type !== m.bgType) { T.bg.type = m.bgType; baseChanged() }\n    drawCurtain(m.curtain, true);\n")
    s = rep(s, "    S.meta = mt; S.board.locked = !!mt.locked;", "    drawCurtain(mt.curtain, false);\n    S.meta = mt; S.board.locked = !!mt.locked;")
    # student: laser + leave clean
    s = rep(s, "  S.unsubs.push(DB.onValue(b + '/meta', mt => {", "  S.unsubs.push(DB.onValue(b + '/laser', v => { if (v && v.t && DB.now() - v.t < 4000) laserAt($('#sBoard'), v.x, v.y) }));\n  S.unsubs.push(() => drawCurtain(null, false));\n  S.unsubs.push(DB.onValue(b + '/meta', mt => {")
    # join: pick the name from the class list
    if target == 'rb':
        s = rep(s, "  if (nm) { inp.value = nm; inp.readOnly = true;", "  if (nm) { const pk = $('#jPick'); if (pk) pk.hidden = true; inp.hidden = false; inp.value = nm; inp.readOnly = true;")
    s = rep(s, "async function lookupTeacher(code) {\n", "async function lookupTeacher(code) {\n  classPicker(code);\n")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
