"""BoardPlus: the move button now selects and moves handwriting and text too (and still moves the image);
free text size; sharper typed text."""
import json

ADD_I18N = {
    "تحريك: الصورة والكتابة والنصوص": "Move: image, handwriting and text", "حجم النص": "Text size", "أصغر": "Smaller", "أكبر": "Larger",
    "اضغط على أي كتابة أو نص واسحبه، أو اسحب على مكان فاضي لتحديد أكثر من عنصر": "Tap any writing or text and drag it, or drag on an empty spot to select several",
    "حذف المحدد": "Delete selection", "تكبير المحدد": "Enlarge selection", "تصغير المحدد": "Shrink selection", "اسحب لتكبير أو تصغير": "Drag to resize",
}

CSS = r"""
.imgedit .selbx{position:absolute;border:2px dashed #2f5bd3;border-radius:6px;background:rgba(47,91,211,.06);pointer-events:none}
.imgedit .selbx i{position:absolute;width:16px;height:16px;border-radius:50%;background:#fff;border:2.5px solid #2f5bd3;bottom:-9px;right:-9px;pointer-events:auto;cursor:nwse-resize;touch-action:none}
.imgedit .band{position:absolute;border:1.5px solid #2f5bd3;background:rgba(47,91,211,.1);pointer-events:none}
.selbar{position:absolute;z-index:6;display:flex;gap:2px;transform:translate(-50%,-100%);margin-top:-10px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:3px;box-shadow:var(--shadow)}
.selbar[hidden]{display:none}
.selbar button{width:36px;height:34px;border:0;border-radius:9px;background:transparent;color:var(--ink);font:inherit;font-weight:800;font-size:14px;cursor:pointer;display:grid;place-items:center}
.selbar button:hover{background:var(--surface-2)}
.selbar button.del{color:var(--red)}
.tsz{display:inline-flex;align-items:center;gap:2px;background:var(--surface-2);border-radius:10px;padding:2px 4px}
.tsz[hidden]{display:none}
.tsz button{min-width:30px;height:32px;font-weight:800}
.tsz b{min-width:28px;text-align:center;font-size:13px}
.board textarea.tx{font-family:"IBM Plex Sans Arabic","Readex Pro",sans-serif}
"""

JS = r"""
/* ======================= select & move handwriting and text (inside the move mode) ======================= */
const SEL = { ids: new Set(), bx: null, bar: null };
const FREE_T = ['pen', 'cal', 'hl', 'smart'];
function segDist(px, py, ax, ay, bx, by) { const dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy; let t = L ? ((px - ax) * dx + (py - ay) * dy) / L : 0; t = Math.max(0, Math.min(1, t)); return Math.hypot(px - ax - t * dx, py - ay - t * dy) }
function hitItem([x, y]) {
  const ents = [...T.tMap.entries()].reverse();
  for (const [id, s] of ents) {
    if (!s || s.t === 'er') continue; const b = strokeBox(s); if (!b || x < b[0] - 12 || x > b[2] + 12 || y < b[1] - 12 || y > b[3] + 12) continue;
    if (FREE_T.includes(s.t) && s.p && s.p.length >= 4) { const tol = Math.max(14, (s.w || 5) * (s.t === 'cal' ? 2 : s.t === 'hl' ? 2.2 : 1) + 8); for (let i = 2; i < s.p.length; i += 2) if (segDist(x, y, s.p[i - 2], s.p[i - 1], s.p[i], s.p[i + 1]) <= tol) return id; continue }
    return id;
  }
  return null;
}
function selBox() {
  let a = 1e9, b = 1e9, c = -1e9, d = -1e9, n = 0;
  SEL.ids.forEach(id => { const s = T.tMap.get(id), q = s && strokeBox(s); if (!q) return; n++; a = Math.min(a, q[0]); b = Math.min(b, q[1]); c = Math.max(c, q[2]); d = Math.max(d, q[3]) });
  return n ? [a, b, c, d] : null;
}
const inB = (q, [x, y], m = 0) => q && x >= q[0] - m && x <= q[2] + m && y >= q[1] - m && y <= q[3] + m;
function xform(s, f, k) {
  const o = { ...s }, R = v => Math.round(v * 10) / 10;
  if (Array.isArray(s.p)) { o.p = s.p.slice(); for (let i = 0; i < o.p.length; i += 2) { const [x, y] = f(s.p[i], s.p[i + 1]); o.p[i] = R(x); o.p[i + 1] = R(y) } }
  if (typeof s.x === 'number' && typeof s.y === 'number') { const [x, y] = f(s.x, s.y); o.x = R(x); o.y = R(y) }
  if (k !== 1 && s.t !== 'media') { if (s.w) o.w = Math.max(1, Math.min(90, R(s.w * k))); if (s.z) o.z = Math.max(10, Math.min(500, Math.round(s.z * k))); if (s.wd) o.wd = Math.round(s.wd * k) }
  return o;
}
function selSet(ids) { SEL.ids = new Set(ids); drawSel() }
function drawSel() {
  if (!IE.el) return;
  if (!SEL.bx) {
    SEL.bx = document.createElement('div'); SEL.bx.className = 'selbx'; SEL.bx.innerHTML = '<i data-sh="r" title="اسحب لتكبير أو تصغير"></i>'; IE.el.appendChild(SEL.bx);
    SEL.bar = document.createElement('div'); SEL.bar.className = 'selbar';
    SEL.bar.innerHTML = '<button data-sa="-" title="تصغير المحدد">A−</button><button data-sa="+" title="تكبير المحدد">A+</button><button class="del" data-sa="del" title="حذف المحدد">' + svgI('trash') + '</button>';
    IE.el.parentElement.appendChild(SEL.bar); SEL.bar.addEventListener('pointerdown', e => e.stopPropagation());
    SEL.bar.onclick = e => { const b = e.target.closest('[data-sa]'); if (!b) return; const a = b.dataset.sa; if (a === 'del') selDelete(); else selScale(a === '+' ? 1.2 : 1 / 1.2) };
  }
  const q = IE.on && SEL.ids.size ? selBox() : null; SEL.bx.hidden = SEL.bar.hidden = !q; if (!q) return;
  Object.assign(SEL.bx.style, { left: q[0] / W * 100 + '%', top: q[1] / H * 100 + '%', width: (q[2] - q[0]) / W * 100 + '%', height: (q[3] - q[1]) / H * 100 + '%' });
  Object.assign(SEL.bar.style, { left: (q[0] + q[2]) / 2 / W * 100 + '%', top: Math.max(6, q[1] / H * 100) + '%' });
}
function selCommit(before) {
  const after = new Map(); SEL.ids.forEach(id => { const s = T.tMap.get(id); if (s) after.set(id, s) });
  const put = m => { m.forEach((s, id) => { T.tMap.set(id, s); tBoard.sink.write(id, s) }); tBoard.mark('t'); drawSel() };
  put(after); tBoard.record({ undo: () => put(before), redo: () => put(after) });
}
function selScale(k) {
  const q = selBox(); if (!q) return; const cx = (q[0] + q[2]) / 2, cy = (q[1] + q[3]) / 2, before = new Map();
  SEL.ids.forEach(id => { const s = T.tMap.get(id); if (!s) return; before.set(id, s); T.tMap.set(id, xform(s, (x, y) => [cx + (x - cx) * k, cy + (y - cy) * k], k)) });
  selCommit(before);
}
function selDelete() {
  const gone = new Map(); SEL.ids.forEach(id => { const s = T.tMap.get(id); if (s) gone.set(id, s) }); if (!gone.size) return;
  const rm = () => { gone.forEach((s, id) => { T.tMap.delete(id); tBoard.sink.remove(id) }); tBoard.mark('t'); SEL.ids.clear(); drawSel() };
  rm(); tBoard.record({ undo: () => { gone.forEach((s, id) => { T.tMap.set(id, s); tBoard.sink.write(id, s) }); tBoard.mark('t') }, redo: rm });
}
function selDown(e, p) {
  const sh = e.target.dataset && e.target.dataset.sh; let mode = null;
  if (sh === 'r' && SEL.ids.size) mode = 'size';
  else if (SEL.ids.size && inB(selBox(), p, 6)) mode = 'move';
  else { const id = hitItem(p); if (id) { selSet([id]); mode = 'move' } }
  const r = curRect();
  if (!mode && !(r && p[0] >= r.x && p[0] <= r.x + r.w && p[1] >= r.y && p[1] <= r.y + r.h)) { selSet([]); mode = 'band' }
  if (!mode) { if (SEL.ids.size) selSet([]); return false }
  const orig = new Map(); SEL.ids.forEach(id => { const s = T.tMap.get(id); if (s) orig.set(id, s) });
  IE.sd = { mode, p0: p, pid: e.pointerId, orig, box: selBox(), moved: false };
  if (mode === 'band') { if (!IE.band) { IE.band = document.createElement('div'); IE.band.className = 'band'; IE.el.appendChild(IE.band) } IE.band.hidden = true }
  return true;
}
function selMove(p) {
  const d = IE.sd; d.moved = true;
  if (d.mode === 'band') { const a = Math.min(d.p0[0], p[0]), b = Math.min(d.p0[1], p[1]); IE.band.hidden = false; Object.assign(IE.band.style, { left: a / W * 100 + '%', top: b / H * 100 + '%', width: Math.abs(p[0] - d.p0[0]) / W * 100 + '%', height: Math.abs(p[1] - d.p0[1]) / H * 100 + '%' }); d.p1 = p; return }
  let f, k = 1;
  if (d.mode === 'move') { const dx = p[0] - d.p0[0], dy = p[1] - d.p0[1]; f = (x, y) => [x + dx, y + dy] }
  else { const [ax, ay] = [d.box[0], d.box[1]], k0 = Math.hypot(d.box[2] - ax, d.box[3] - ay) || 1; k = Math.max(.15, Math.min(8, Math.hypot(p[0] - ax, p[1] - ay) / k0)); f = (x, y) => [ax + (x - ax) * k, ay + (y - ay) * k] }
  d.orig.forEach((s, id) => T.tMap.set(id, xform(s, f, k))); tBoard.mark('t'); drawSel();
}
function selUp() {
  const d = IE.sd; IE.sd = null;
  if (d.mode === 'band') { if (IE.band) IE.band.hidden = true; if (!d.p1) return; const q = [Math.min(d.p0[0], d.p1[0]), Math.min(d.p0[1], d.p1[1]), Math.max(d.p0[0], d.p1[0]), Math.max(d.p0[1], d.p1[1])];
    const ids = []; T.tMap.forEach((s, id) => { if (!s || s.t === 'er') return; const b = strokeBox(s); if (b && inB(q, [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2])) ids.push(id) }); selSet(ids); return }
  if (d.moved) selCommit(d.orig);
}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    # sharper typed text: make sure the weight used on the board is loaded before drawing
    s = rep(s, """try { document.fonts.load('700 40px "Aref Ruqaa"').then(""", """try { Promise.all(['600 40px "IBM Plex Sans Arabic"', '700 40px "IBM Plex Sans Arabic"', '700 40px "Aref Ruqaa"'].map(f => document.fonts.load(f))).then(""")
    # free text size in the toolbar (shown while the text tool is on)
    s = rep(s, "  const st = { t: tools[0], c: colors[0], w: 6, k: 'ok' };", "  const st = { t: tools[0], c: colors[0], w: 6, k: 'ok', z: 44 }; const ZS = [20, 26, 32, 38, 44, 54, 64, 80, 100, 130, 170, 220];")
    s = rep(s, "  if (stamps) h += '<span class=\"sep\"></span>' + [['ok',",
            "  if (tools.includes('text')) h += '<span class=\"tsz\" hidden title=\"حجم النص\"><button data-zs=\"-\" title=\"أصغر\">A−</button><b class=\"zv\">44</b><button data-zs=\"+\" title=\"أكبر\">A+</button></span>';\n"
            "  if (stamps) h += '<span class=\"sep\"></span>' + [['ok',")
    s = rep(s, "    el.querySelectorAll('[data-w]').forEach(b => b.classList.toggle('on', st.w === +b.dataset.w));\n",
            "    el.querySelectorAll('[data-w]').forEach(b => b.classList.toggle('on', st.w === +b.dataset.w));\n"
            "    const tz = el.querySelector('.tsz'); if (tz) { tz.hidden = st.t !== 'text'; tz.querySelector('.zv').textContent = st.z }\n")
    s = rep(s, "    else if (b.dataset.w) st.w = +b.dataset.w;\n",
            "    else if (b.dataset.w) st.w = +b.dataset.w;\n"
            "    else if (b.dataset.zs) { const i = ZS.findIndex(v => v >= st.z); st.z = ZS[Math.max(0, Math.min(ZS.length - 1, (i < 0 ? ZS.length - 1 : i) + (b.dataset.zs === '+' ? 1 : -1)))] }\n")
    s = rep(s, "  sync(); st.get = () => ({ t: st.t, c: st.c, w: st.w, k: st.k }); return st;", "  sync(); st.get = () => ({ t: st.t, c: st.c, w: st.w, k: st.k, z: st.z }); return st;")
    s = rep(s, "    const z = { 3: 30, 6: 44, 12: 64 }[t.w] || 44; const css = this.host.clientWidth / W;", "    const z = t.z || { 3: 30, 6: 44, 12: 64 }[t.w] || 44; const css = this.host.clientWidth / W;")
    # move mode works without an image too
    s = rep(s, "{ icon: 'move', label: 'تحريك وتكبير الصورة', onClick: () => imgEdit(!IE.on) },", "{ icon: 'move', label: 'تحريك: الصورة والكتابة والنصوص', onClick: () => imgEdit(!IE.on) },")
    s = rep(s, "  if (on && !curRect()) { toast('الصق صورة السؤال أولًا (Ctrl + V)'); return }\n  IE.on = !!on; if (!IE.el) return; IE.el.hidden = IE.bar.hidden = !IE.on;",
            "  IE.on = !!on; if (!IE.el) return; IE.el.hidden = !IE.on; IE.bar.hidden = !IE.on || !curRect(); IE.box.hidden = !curRect();\n"
            "  if (IE.on) toast('اضغط على أي كتابة أو نص واسحبه، أو اسحب على مكان فاضي لتحديد أكثر من عنصر'); else { SEL.ids.clear(); IE.sd = null } drawSel();")
    s = rep(s, "function placeBox() {\n  const r = curRect(); if (!r || !IE.box) return;",
            "function placeBox() {\n  const r = curRect(); if (IE.box) IE.box.hidden = !r; if (IE.bar && IE.on) IE.bar.hidden = !r; if (!r || !IE.box) return;")
    s = rep(s, "T.bg.img = await loadImg(src); baseChanged(); if (!T.bg.img) imgEdit(false); else if (IE.pending)",
            "T.bg.img = await loadImg(src); baseChanged(); if (!T.bg.img) { if (IE.on) placeBox() } else if (IE.pending)")
    s = rep(s, "  el.addEventListener('pointerdown', e => {\n    const r = curRect(); if (!r) return; e.preventDefault(); el.setPointerCapture(e.pointerId);",
            "  el.addEventListener('pointerdown', e => {\n"
            "    if (!IE.crop && !IE.ptrs.size && selDown(e, P(e))) { e.preventDefault(); el.setPointerCapture(e.pointerId); return }\n"
            "    const r = curRect(); if (!r) return; e.preventDefault(); el.setPointerCapture(e.pointerId);")
    s = rep(s, "  el.addEventListener('pointermove', e => {\n    if (IE.crop) {",
            "  el.addEventListener('pointermove', e => {\n    if (IE.sd) { if (IE.sd.pid === e.pointerId && e.buttons) selMove(P(e)); return }\n    if (IE.crop) {")
    s = rep(s, "  const end = e => { if (IE.crop) {", "  const end = e => { if (IE.sd && IE.sd.pid === e.pointerId) { selUp(); return } if (IE.crop) {")
    s = rep(s, "    if (!IE.on || $('#teacher').hidden || /TEXTAREA|INPUT/.test(e.target.tagName)) return;\n    const r = curRect(); if (!r) return;",
            "    if (!IE.on || $('#teacher').hidden || /TEXTAREA|INPUT/.test(e.target.tagName)) return;\n"
            "    if (SEL.ids.size && !IE.crop) {\n"
            "      if (e.key === 'Delete' || e.key === 'Backspace') { e.preventDefault(); return selDelete() }\n"
            "      if (e.key === 'Escape') return selSet([]);\n"
            "      if (e.key.startsWith('Arrow')) { e.preventDefault(); const st = e.shiftKey ? 40 : 10, dx = { ArrowLeft: -st, ArrowRight: st }[e.key] || 0, dy = { ArrowUp: -st, ArrowDown: st }[e.key] || 0, before = new Map(); SEL.ids.forEach(id => { const s = T.tMap.get(id); if (s) { before.set(id, s); T.tMap.set(id, xform(s, (x, y) => [x + dx, y + dy], 1)) } }); return selCommit(before) }\n"
            "      if (e.key === '+' || e.key === '=') return selScale(1.2); if (e.key === '-') return selScale(1 / 1.2);\n"
            "    }\n"
            "    const r = curRect(); if (!r) { if (e.key === 'Escape') imgEdit(false); return }")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
