"""Lasso cut + image crop/rotate/center (ported from ragabboard). Run with exec() on a namespace holding s."""
import json
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(n,a[:90]); s=s.replace(a,b)

# icons
rep('''    <symbol id="i-cut" viewBox="0 0 24 24">''','''    <symbol id="i-lasso" viewBox="0 0 24 24"><path d="M5.5 14.5C3.6 13.3 3 11.6 3 10.5 3 6.9 7 4 12 4s9 2.9 9 6.5S17 17 12 17c-1.3 0-2.6-.2-3.7-.5" stroke-dasharray="2.6 2.4"/><circle cx="7" cy="16.5" r="2"/><path d="M6 18.5c-.6 1.2-1.4 2-2.5 2.5"/></symbol>
    <symbol id="i-crop" viewBox="0 0 24 24"><path d="M6 2v14a2 2 0 0 0 2 2h14"/><path d="M18 22V8a2 2 0 0 0-2-2H2"/></symbol>
    <symbol id="i-rot" viewBox="0 0 24 24"><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v6h-6"/></symbol>
    <symbol id="i-center" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 7v10M7 12h10"/></symbol>
    <symbol id="i-cut" viewBox="0 0 24 24">''')

# CSS
rep(".selbox{", """.lasso{position:absolute;inset:0;width:100%;height:100%;z-index:3;pointer-events:none;overflow:visible}
.lasso polygon{fill:rgba(224,36,47,.1);stroke:var(--red);stroke-width:3;stroke-dasharray:10 7;vector-effect:non-scaling-stroke;stroke-linejoin:round}
.lmenu{position:absolute;z-index:7;transform:translate(-50%,-50%);display:flex;flex-direction:column;gap:4px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:6px;box-shadow:var(--shadow);min-width:190px}
.lmenu b{font-size:12px;color:var(--muted);padding:2px 6px}
.lmenu button{border:0;border-radius:9px;background:var(--surface-2);padding:8px 10px;font:inherit;font-weight:600;color:var(--ink);text-align:start;cursor:pointer}
.lmenu button:hover{background:var(--red-soft)}
.lmenu button.x{background:transparent;color:var(--muted);text-align:center}
.imgedit.cropping{cursor:crosshair}
.imgedit.cropping .ibox i{display:none}
.cropbox{position:absolute;border:2px solid #fff;outline:2px dashed #2f5bd3;box-shadow:0 0 0 9999px rgba(14,21,36,.45);pointer-events:none}
.imgbar .cg{display:none}
.imgbar.cropping > :not(.cg){display:none}
.imgbar.cropping .cg{display:inline-flex}
.imgbar span.cg{font-size:13px;color:var(--muted);padding:0 6px;white-space:nowrap}
.selbox{""")

# Board: lasso tool
rep("""  constructor(host, { layers, target, tool, sink, onStamp, onCut, onErase }) {
    this.onStamp = onStamp; this.onCut = onCut; this.onErase = onErase;""","""  constructor(host, { layers, target, tool, sink, onStamp, onCut, onErase, onLasso }) {
    this.onStamp = onStamp; this.onCut = onCut; this.onErase = onErase; this.onLasso = onLasso;""")
rep("""    if (t.t === 'stamp') { const sid = uid();""","""    if (t.t === 'lasso') {
      e.preventDefault(); this.ov.setPointerCapture(e.pointerId); this.pid = e.pointerId;
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.setAttribute('class', 'lasso'); svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('preserveAspectRatio', 'none');
      svg.innerHTML = '<polygon points=""/>'; this.host.appendChild(svg); this.las = { pts: [x, y], svg }; return;
    }
    if (t.t === 'stamp') { const sid = uid();""")
rep("""    if (this.sel && e.pointerId === this.pid) { const [x, y] = this.pt(e); this.sel.x1 = x; this.sel.y1 = y; this.drawSel(); return }""",
"""    if (this.sel && e.pointerId === this.pid) { const [x, y] = this.pt(e); this.sel.x1 = x; this.sel.y1 = y; this.drawSel(); return }
    if (this.las && e.pointerId === this.pid) {
      const P = this.las.pts, evs = e.getCoalescedEvents ? e.getCoalescedEvents() : [e];
      for (const ev of (evs.length ? evs : [e])) { const [x, y] = this.pt(ev), n = P.length; if ((x - P[n - 2]) ** 2 + (y - P[n - 1]) ** 2 >= 25) P.push(x, y) }
      this.las.svg.firstChild.setAttribute('points', P.join(' ')); return;
    }""")
rep("""      this.onCut && this.onCut(a, b, c, d); return;
    }""","""      this.onCut && this.onCut(a, b, c, d); return;
    }
    if (this.las && e.pointerId === this.pid) {
      const { pts, svg } = this.las; this.las = null; const done = () => svg.remove();
      let a = 1e9, c = -1e9, b = 1e9, d = -1e9; for (let i = 0; i < pts.length; i += 2) { a = Math.min(a, pts[i]); c = Math.max(c, pts[i]); b = Math.min(b, pts[i + 1]); d = Math.max(d, pts[i + 1]) }
      if (pts.length < 8 || (c - a < 12 && d - b < 12)) { done(); return toast('ارسم حول الجزء اللي تبي تحذفه') }
      if (this.onLasso) this.onLasso(pts, done, this); else done(); return;
    }""")
rep("""cut: 'تحديد وحذف كتابة الطالب' };""","""cut: 'تحديد وحذف كتابة الطالب', lasso: 'قص حر: ارسم حول أي جزء لحذفه' };""")
rep("""if (st.t === 'er' || st.t === 'stamp' || st.t === 'cut') st.t = 'pen'""","""if (st.t === 'er' || st.t === 'stamp' || st.t === 'cut' || st.t === 'lasso') st.t = 'pen'""")

# toolbars
rep("""  tBoard = new Board($('#tBoard'), { layers: ['bg', 't'], target: 't', tool: tTool.get, sink:""","""  tBoard = new Board($('#tBoard'), { layers: ['bg', 't'], target: 't', tool: tTool.get, onLasso: tLasso, sink:""")
rep("""tool: fTool.get, onStamp: autoPraise, onCut: cutStudent, onErase: eraseMarks, sink: {""","""tool: fTool.get, onStamp: autoPraise, onCut: cutStudent, onErase: eraseMarks, onLasso: fLasso, sink: {""")
rep("""  S.board = new Board($('#sBoard'), { layers: ['bg', 't', 's', 'm'], target: 's', tool: S.tool.get, sink:""","""  S.board = new Board($('#sBoard'), { layers: ['bg', 't', 's', 'm'], target: 's', tool: S.tool.get, onLasso: (P, done, bd) => { done(); if (!applyLasso(bd, P)) toast('ما في شيء داخل التحديد') }, sink:""")

# lasso logic (placed before cutStudent)
rep("""function cutStudent(x0, y0, x1, y1) {""",r"""/* ---------- قص حر (Lasso): يحذف ما داخل الشكل المرسوم، ويقطع الخطوط عند حدوده ---------- */
function inPoly(x, y, P) {
  let c = false;
  for (let i = 0, j = P.length - 2; i < P.length; j = i, i += 2) { const xi = P[i], yi = P[i + 1], xj = P[j], yj = P[j + 1]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c }
  return c;
}
function polyBox(P) { let a = 1e9, b = 1e9, c = -1e9, d = -1e9; for (let i = 0; i < P.length; i += 2) { a = Math.min(a, P[i]); c = Math.max(c, P[i]); b = Math.min(b, P[i + 1]); d = Math.max(d, P[i + 1]) } return [a, b, c, d] }
function lassoSplit(map, P) {
  const del = new Map(), add = [], bx = polyBox(P);
  (map || new Map()).forEach((s, id) => {
    if (!s) return; const sb = strokeBox(s); if (!sb || sb[2] < bx[0] || sb[0] > bx[2] || sb[3] < bx[1] || sb[1] > bx[3]) return;
    const free = (s.t === 'pen' || s.t === 'hl' || s.t === 'er') && s.p && s.p.length >= 4;
    if (free) {
      const runs = []; let cur = [], hit = false;
      for (let i = 0; i < s.p.length; i += 2) { if (inPoly(s.p[i], s.p[i + 1], P)) { hit = true; if (cur.length) runs.push(cur); cur = [] } else cur.push(s.p[i], s.p[i + 1]) }
      if (!hit) return; if (cur.length) runs.push(cur);
      del.set(id, s); runs.forEach((r, k) => { if (r.length >= 4) add.push([`${id}_${k}`, { ...s, p: r }]) });   // نفس ترتيب الرسم الأصلي
    } else {
      let hit = inPoly((sb[0] + sb[2]) / 2, (sb[1] + sb[3]) / 2, P);
      if (!hit && s.p) for (let i = 0; i < s.p.length; i += 2) if (inPoly(s.p[i], s.p[i + 1], P)) { hit = true; break }
      if (hit) del.set(id, s);
    }
  });
  return { del, add };
}
function lassoOps(bd, L) {
  const map = bd.map;
  const run = () => { L.del.forEach((v, id) => { map.delete(id); bd.sink.remove(id) }); L.add.forEach(([id, v]) => { map.set(id, v); bd.sink.write(id, v) }); bd.mark(bd.target) };
  const back = () => { L.add.forEach(([id]) => { map.delete(id); bd.sink.remove(id) }); L.del.forEach((v, id) => { map.set(id, v); bd.sink.write(id, v) }); bd.mark(bd.target) };
  return { run, back };
}
function applyLasso(bd, P) {
  const L = lassoSplit(bd.map, P); if (!L.del.size) return 0;
  const o = lassoOps(bd, L); o.run(); bd.record({ undo: o.back, redo: o.run }); return L.del.size;
}
function lassoMenu(bd, P, items, done) {
  const [a, b, c, d] = polyBox(P), m = document.createElement('div'); m.className = 'lmenu';
  m.style.left = Math.min(85, Math.max(15, (a + c) / 2 / W * 100)) + '%'; m.style.top = Math.min(85, Math.max(15, (b + d) / 2 / H * 100)) + '%';
  m.innerHTML = '<b>احذف من داخل التحديد:</b>' + items.map((x, i) => `<button data-i="${i}">${x[0]}</button>`).join('') + '<button class="x" data-i="x">إلغاء</button>';
  const close = () => { m.remove(); done(); document.removeEventListener('pointerdown', out, true) };
  const out = e => { if (!m.contains(e.target)) close() };
  m.onclick = e => { const k = e.target.closest('[data-i]'); if (!k) return; close(); if (k.dataset.i !== 'x') items[+k.dataset.i][1]() };
  bd.host.appendChild(m); setTimeout(() => document.addEventListener('pointerdown', out, true), 0);
}
function tLasso(P, done, bd) {
  const L = lassoSplit(T.tMap, P), r = curRect(), bx = polyBox(P);
  const imgHit = !!r && bx[0] < r.x + r.w && bx[2] > r.x && bx[1] < r.y + r.h && bx[3] > r.y;
  if (!L.del.size && !imgHit) { done(); return toast('ما في شيء داخل التحديد') }
  const cut = async withImg => {
    const o = lassoOps(bd, L); if (L.del.size) o.run();
    let prev = null, url = null; if (withImg) { url = await erasedImage(P); if (url) prev = await replaceImage(url, T.bg.tr, false) }
    if (L.del.size || prev) bd.record({ undo: () => { L.del.size && o.back(); prev && replaceImage(prev.url, prev.tr, false) }, redo: () => { L.del.size && o.run(); url && replaceImage(url, prev.tr, false) } });
    toast(withImg ? 'تم حذف الجزء المحدد (تقدر تتراجع)' : 'تم حذف الكتابة المحددة');
  };
  if (!imgHit) { done(); return cut(false) }
  lassoMenu(bd, P, [...(L.del.size ? [['✏️ كتابتي فقط (الصورة تبقى)', () => cut(false)]] : []), [L.del.size ? '🖼️ كتابتي + هذا الجزء من الصورة' : '🖼️ هذا الجزء من الصورة', () => cut(true)]], done);
}
function fLasso(P, done) {
  done(); const s = T.st.get(T.focus); if (!s) return;
  const A = lassoSplit(s.strokes, P), M = lassoSplit(s.marks, P);
  if (!A.del.size && !M.del.size) return toast('ما في شيء داخل التحديد');
  const up = {}; A.del.forEach((v, id) => up[id] = null); A.add.forEach(([id, v]) => up[id] = v);
  if (Object.keys(up).length) DB.update(`sessions/${T.code}/sb/${T.focus}`, up);
  const mup = {}; M.add.forEach(([id, v]) => mup[id] = v); if (Object.keys(mup).length) DB.update(`sessions/${T.code}/mk/${T.focus}`, mup);
  const lost = M.del.size ? removeMarks([...M.del.keys()], true) : 0;
  toast(lost ? `تم الحذف وخُصمت ${lost} نقطة` : 'تم حذف الجزء المحدد');
}
function cutStudent(x0, y0, x1, y1) {""")

# image helpers: replace / crop / rotate / erase
rep("""function curRect() { return T.bg.img && T.bg.img.width ? bgRect(T.bg.img, T.bg.tr) : null }""",r"""function curRect() { return T.bg.img && T.bg.img.width ? bgRect(T.bg.img, T.bg.tr) : null }
async function replaceImage(url, tr, record = true) {
  const prev = { url: T.bg.img && T.bg.img.src, tr: T.bg.tr ? { ...T.bg.tr } : null };
  const im = await loadImg(url); if (!im) { toast('تعذر تعديل الصورة', true); return null }
  T.bg.img = im; T.bg.tr = tr ? { ...tr } : null; baseChanged(); IE.on && placeBox();
  try { await DB.update(`sessions/${T.code}`, { bgImg: url, 'meta/imgT': tr ? { ...tr } : null }) } catch (e) { toast('تعذر رفع الصورة', true) }
  if (record && prev.url) tBoard.record({ undo: () => replaceImage(prev.url, prev.tr, false), redo: () => replaceImage(url, tr, false) });
  return prev;
}
const imgCanvas = (w, h) => { const c = document.createElement('canvas'); c.width = Math.max(1, Math.round(w)); c.height = Math.max(1, Math.round(h)); const x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, c.width, c.height); return [c, x] };
async function erasedImage(P) {
  const img = T.bg.img, r = curRect(); if (!img || !r) return null;
  const [c, x] = imgCanvas(img.width, img.height); x.drawImage(img, 0, 0);
  x.fillStyle = '#fff'; x.beginPath();
  for (let i = 0; i < P.length; i += 2) { const px = (P[i] - r.x) / r.w * img.width, py = (P[i + 1] - r.y) / r.h * img.height; i ? x.lineTo(px, py) : x.moveTo(px, py) }
  x.closePath(); x.fill(); return c.toDataURL('image/jpeg', .88);
}
async function rotateImg() {
  const img = T.bg.img, r = curRect(); if (!r) return;
  const [c, x] = imgCanvas(img.height, img.width); x.translate(c.width, 0); x.rotate(Math.PI / 2); x.drawImage(img, 0, 0);
  const cx = r.x + r.w / 2, cy = r.y + r.h / 2;
  await replaceImage(c.toDataURL('image/jpeg', .88), { x: Math.round(cx - r.h / 2), y: Math.round(cy - r.w / 2), w: Math.round(r.h) });
}
function cropMode(on) {
  IE.crop = !!on; IE.cr = null; IE.el.classList.toggle('cropping', IE.crop); IE.bar.classList.toggle('cropping', IE.crop);
  if (IE.cbox) IE.cbox.hidden = true;
}
function drawCrop() {
  const c = IE.cr; if (!IE.cbox) { IE.cbox = document.createElement('div'); IE.cbox.className = 'cropbox'; IE.el.appendChild(IE.cbox) }
  IE.cbox.hidden = !c; if (!c) return;
  Object.assign(IE.cbox.style, { left: Math.min(c.x0, c.x1) / W * 100 + '%', top: Math.min(c.y0, c.y1) / H * 100 + '%', width: Math.abs(c.x1 - c.x0) / W * 100 + '%', height: Math.abs(c.y1 - c.y0) / H * 100 + '%' });
}
async function applyCrop() {
  const r = curRect(), img = T.bg.img, c = IE.cr; if (!r) return;
  if (!c) return toast('اسحب على الصورة لتحديد الجزء اللي تبي تبقيه');
  const a = Math.max(Math.min(c.x0, c.x1), r.x), b = Math.max(Math.min(c.y0, c.y1), r.y), e = Math.min(Math.max(c.x0, c.x1), r.x + r.w), d = Math.min(Math.max(c.y0, c.y1), r.y + r.h);
  if (e - a < 20 || d - b < 20) return toast('الجزء المحدد صغير جدًا');
  const sx = (a - r.x) / r.w * img.width, sy = (b - r.y) / r.h * img.height, sw = (e - a) / r.w * img.width, sh = (d - b) / r.h * img.height;
  const [cv, x] = imgCanvas(sw, sh); x.drawImage(img, sx, sy, sw, sh, 0, 0, cv.width, cv.height);
  await replaceImage(cv.toDataURL('image/jpeg', .9), { x: Math.round(a), y: Math.round(b), w: Math.round(e - a) });
  cropMode(false); toast('تم قص الصورة ✂️ (تقدر تتراجع)');
}""")

# image bar buttons
rep("""    <button data-z="fit" title="ملء السبورة">${svgI('fit')}<span class="hide-sm">ملء السبورة</span></button><button data-z="del" class="del" title="حذف الصورة" aria-label="حذف الصورة">${svgI('trash')}</button><button data-z="done" class="done">تم</button>`;""",
"""    <button data-z="fit" title="ملء السبورة">${svgI('fit')}<span class="hide-sm">ملء السبورة</span></button><button data-z="center" title="توسيط الصورة" aria-label="توسيط الصورة">${svgI('center')}</button><button data-z="rot" title="تدوير ٩٠°" aria-label="تدوير">${svgI('rot')}</button><button data-z="crop" title="اقتصاص الصورة">${svgI('crop')}<span class="hide-sm">قص</span></button><button data-z="del" class="del" title="حذف الصورة" aria-label="حذف الصورة">${svgI('trash')}</button><button data-z="done" class="done">تم</button>
    <span class="cg">اسحب على الصورة لتحديد الجزء اللي تبيه</span><button class="cg done" data-z="cropok">قص ✓</button><button class="cg" data-z="cropno">إلغاء</button>`;""")
rep("""    else if (z === 'fit') {""","""    else if (z === 'crop') cropMode(true);
    else if (z === 'cropok') applyCrop();
    else if (z === 'cropno') cropMode(false);
    else if (z === 'rot') rotateImg();
    else if (z === 'center') { setRect({ x: (W - r.w) / 2, y: (H - r.h) / 2, w: r.w }); sendTr(true) }
    else if (z === 'fit') {""")
rep("""  el.addEventListener('pointerdown', e => {
    const r = curRect(); if (!r) return; e.preventDefault(); el.setPointerCapture(e.pointerId);""","""  el.addEventListener('pointerdown', e => {
    const r = curRect(); if (!r) return; e.preventDefault(); el.setPointerCapture(e.pointerId);
    if (IE.crop) { const p = P(e), cl = q => [Math.max(r.x, Math.min(r.x + r.w, q[0])), Math.max(r.y, Math.min(r.y + r.h, q[1]))], [x, y] = cl(p); IE.cr = { x0: x, y0: y, x1: x, y1: y, cl, pid: e.pointerId }; drawCrop(); return }""")
rep("""  el.addEventListener('pointermove', e => {
    if (!IE.drag""","""  el.addEventListener('pointermove', e => {
    if (IE.crop) { const c = IE.cr; if (c && c.pid === e.pointerId && e.buttons) { [c.x1, c.y1] = c.cl(P(e)); drawCrop() } return }
    if (!IE.drag""")
rep("""  const end = e => { if (!IE.ptrs.delete(e.pointerId)) return;""","""  const end = e => { if (IE.crop) { if (IE.cr) IE.cr.pid = null; return } if (!IE.ptrs.delete(e.pointerId)) return;""")
rep("""    if (e.key === 'Escape' || e.key === 'Enter') imgEdit(false);""","""    if (IE.crop) { if (e.key === 'Escape') cropMode(false); else if (e.key === 'Enter') applyCrop(); return }
    if (e.key === 'Escape' || e.key === 'Enter') imgEdit(false);""")
rep("""  if (IE.on) placeBox(); else { IE.drag = null; IE.ptrs.clear() }""","""  if (IE.on) placeBox(); else { IE.drag = null; IE.ptrs.clear(); IE.crop && cropMode(false) }""")

ADD={"قص حر: ارسم حول أي جزء لحذفه":"Free cut: draw around any part to delete it","ارسم حول الجزء اللي تبي تحذفه":"Draw around the part you want to delete","ما في شيء داخل التحديد":"Nothing inside the selection",
"احذف من داخل التحديد:":"Delete inside the selection:","✏️ كتابتي فقط (الصورة تبقى)":"✏️ My writing only (keep the image)","🖼️ كتابتي + هذا الجزء من الصورة":"🖼️ My writing + this part of the image","🖼️ هذا الجزء من الصورة":"🖼️ This part of the image",
"تم حذف الجزء المحدد (تقدر تتراجع)":"Selected part deleted (you can undo)","تم حذف الكتابة المحددة":"Selected writing deleted","توسيط الصورة":"Center the image","تدوير ٩٠°":"Rotate 90°","اقتصاص الصورة":"Crop the image","قص":"Crop",
"اسحب على الصورة لتحديد الجزء اللي تبيه":"Drag on the image to select the part to keep","قص ✓":"Crop ✓","اسحب على الصورة لتحديد الجزء اللي تبي تبقيه":"Drag on the image to select the part to keep","الجزء المحدد صغير جدًا":"The selection is too small",
"تم قص الصورة ✂️ (تقدر تتراجع)":"Image cropped ✂️ (you can undo)","تعذر تعديل الصورة":"Couldn't edit the image"}
a='const I18N = {'; s=s.replace(a, a+json.dumps(ADD,ensure_ascii=False)[1:-1]+',',1)

