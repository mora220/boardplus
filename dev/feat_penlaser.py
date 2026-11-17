"""Pen size in reach, and a PowerPoint-style laser.
  * Toolbars (teacher board and a student's board in the big view): the pen sizes sit in the toolbar itself
    (four sizes) instead of inside the colour pop-up. The quiz pen bar gets the same four sizes.
  * Laser: a thin bright dot that draws a thin red trail; each part of the trail fades two seconds after it was drawn.
    The teacher sends the points in small batches (sessions/<code>/laser = {s, p:[x,y,...], t}); students draw the same trail."""

CSS = r"""
.szwrap{position:relative;display:inline-flex}
.szbtn .szi,#rInk .iszb .szi{display:grid;place-items:center;width:24px;height:24px}
.szbtn .szi i,#rInk .iszb .szi i{display:block;border-radius:50%;background:currentColor}
.szpop{position:absolute;bottom:calc(100% + 10px);left:50%;transform:translateX(-50%);z-index:8;display:flex;align-items:center;gap:2px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:5px;box-shadow:var(--shadow);white-space:nowrap}
.szpop[hidden]{display:none}
.szpop .sz{width:34px;min-width:34px;padding:0}.szpop .sz i{margin:auto}
.szpop button[title]:hover::after{display:none}
#rInk .iszw{position:relative;display:inline-flex}
#rInk .iszw .szpop{bottom:auto;top:calc(100% + 8px);z-index:30}
#rInk .isz{width:34px;min-width:34px;padding:0}
#rInk .isz i{display:block;margin:auto;border-radius:50%;background:currentColor}
.lzc{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:6}
.laz{width:12px!important;height:12px!important;margin:-6px 0 0 -6px!important;background:radial-gradient(circle,#fff 0 24%,#ff2d3d 42%,rgba(255,45,61,.35) 70%,transparent 76%)!important;box-shadow:0 0 8px 3px rgba(255,45,61,.5)!important;z-index:7!important}
"""

JS = r"""
/* ======================= laser trail (fades after two seconds) ======================= */
const LZ2 = { hosts: new Map(), sid: 0, buf: [], ft: 0, LIFE: 2000 };
function lzHost(host) { let o = LZ2.hosts.get(host); if (!o || !o.cv.isConnected) { const cv = document.createElement('canvas'); cv.className = 'lzc'; host.appendChild(cv); o = { cv, segs: [], raf: 0 }; LZ2.hosts.set(host, o) } return o }
function laserAdd(host, s, pts) {
  if (!host || !pts || pts.length < 2) return; const o = lzHost(host), now = performance.now();
  let g = o.segs.find(z => z.s === s); if (!g) { g = { s, p: [] }; o.segs.push(g) }
  for (let i = 0; i + 1 < pts.length; i += 2) g.p.push([pts[i], pts[i + 1], now]);
  laserAt(host, pts[pts.length - 2], pts[pts.length - 1]);
  if (!o.raf) o.raf = requestAnimationFrame(() => lzDraw(host, o));
}
function lzDraw(host, o) {
  o.raf = 0; const cv = o.cv, r = host.getBoundingClientRect(), d = Math.min(devicePixelRatio || 1, 2), w = Math.round(r.width * d), h = Math.round(r.height * d);
  if (!w || !h) return; if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h }
  const x = cv.getContext('2d'), now = performance.now(), L = LZ2.LIFE, kx = w / W, ky = h / H;
  x.clearRect(0, 0, w, h); x.lineCap = x.lineJoin = 'round';
  o.segs.forEach(g => { while (g.p.length && now - g.p[0][2] >= L) g.p.shift() }); o.segs = o.segs.filter(g => g.p.length);
  for (const pass of [0, 1]) for (const g of o.segs) for (let i = 1; i < g.p.length; i++) {
    const a = g.p[i - 1], b = g.p[i]; x.globalAlpha = Math.max(0, Math.min(1, (L - (now - b[2])) / 450));
    x.strokeStyle = pass ? '#ff2d3d' : 'rgba(255,45,61,.28)'; x.lineWidth = (pass ? 2.6 : 8) * d;
    x.beginPath(); x.moveTo(a[0] * kx, a[1] * ky); x.lineTo(b[0] * kx, b[1] * ky); x.stroke();
  }
  x.globalAlpha = 1; if (o.segs.length) o.raf = requestAnimationFrame(() => lzDraw(host, o));
}
function lzFlush() { clearTimeout(LZ2.ft); if (LZ2.buf.length && T.code) { DB.set(`sessions/${T.code}/laser`, { s: LZ2.sid, p: LZ2.buf, t: DB.now() }); LZ2.buf = []; LZ.t = performance.now() } }
"""

QBTNS = ('<span class="iszw"><button data-iszb class="iszb" title="سُمك القلم"><span class="szi"><i></i></span></button><span class="szpop" hidden>'
         + ''.join(f'<button data-iw="{k}" class="isz" title="{n}"><i style="width:{d}px;height:{d}px"></i></button>' for k, d, n in [(0.6, 4, 'رفيع'), (1, 7, 'متوسط'), (1.8, 10, 'عريض'), (3, 14, 'عريض جدًا')])
         + '</span></span>')


def apply(s, rep, target):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    # toolbar: sizes in the bar
    s = rep(s, "    + '<span class=\"sep\"></span>' + [3, 6, 12].map(w => `<button data-w=\"${w}\" class=\"sz\" title=\"سُمك\" aria-label=\"سمك ${w}\"><i style=\"width:${4 + w * .9}px;height:${4 + w * .9}px\"></i></button>`).join('');",
            ";")
    s = rep(s, "<span class=\"palpop\" hidden>${pal}</span></span>`;",
            "<span class=\"palpop\" hidden>${pal}</span></span><span class=\"szwrap\"><button data-szb class=\"szbtn\" title=\"سُمك القلم\" aria-label=\"سُمك القلم\"><span class=\"szi\"><i></i></span></button><span class=\"szpop\" hidden>${[3, 6, 12, 20].map(w => `<button data-w=\"${w}\" class=\"sz\" title=\"سُمك القلم\" aria-label=\"سمك ${w}\"><i style=\"width:${3 + w * .55}px;height:${3 + w * .55}px\"></i></button>`).join('')}</span></span>`;")
    s = rep(s, "    if (b.dataset.pal !== undefined) { pop().hidden = !pop().hidden; return }",
            "    if (b.dataset.szb !== undefined) { const q = el.querySelector('.szpop'); q.hidden = !q.hidden; pop().hidden = true; return }\n    if (b.dataset.pal !== undefined) { pop().hidden = !pop().hidden; el.querySelector('.szpop').hidden = true; return }")
    s = rep(s, "    if (b.dataset.c || b.dataset.w) pop().hidden = true;", "    if (b.dataset.c || b.dataset.w) { pop().hidden = true; el.querySelector('.szpop').hidden = true }")
    s = rep(s, "  document.addEventListener('pointerdown', e => { const w = el.querySelector('.palwrap'); if (w && !w.contains(e.target)) pop().hidden = true });",
            "  document.addEventListener('pointerdown', e => { const w = el.querySelector('.palwrap'); if (w && !w.contains(e.target)) pop().hidden = true; const z = el.querySelector('.szwrap'); if (z && !z.contains(e.target)) z.querySelector('.szpop').hidden = true });")
    s = rep(s, "    const pb = el.querySelector('.palbtn .sw');", "    { const zi = el.querySelector('.szbtn .szi i'); if (zi) { const d = 3 + st.w * .55; zi.style.cssText = `width:${d}px;height:${d}px` } }\n    const pb = el.querySelector('.palbtn .sw');")
    # quiz pen bar: sizes
    s = rep(s, '<i class="isep"></i><button data-ink="full"', '<i class="isep"></i>' + QBTNS + '<i class="isep"></i><button data-ink="full"')
    s = rep(s, "const QI = { t: 'pen',", "const QI = { k: +(ls.get('rb_qk') || 1) || 1, t: 'pen',")
    s = rep(s, "function qInkTool(full) {", "function qInkTool(full) { const r = qInkTool0(full); r.w = Math.max(1, Math.round(r.w * (QI.k || 1) * 10) / 10); return r }\nfunction qInkTool0(full) {")
    s = rep(s, "(b.dataset.ink === 'full' && QI.full)));", "(b.dataset.ink === 'full' && QI.full) || (!!b.dataset.iw && +b.dataset.iw === QI.k)));")
    s = rep(s, "    if (b.dataset.ic) { QZ.inkC = b.dataset.ic;", "    if (b.dataset.iszb !== undefined) { const q = b.parentElement.querySelector('.szpop'); q.hidden = !q.hidden; return }\n    if (b.dataset.iw) { QI.k = +b.dataset.iw; ls.set('rb_qk', QI.k); b.closest('.szpop').hidden = true; if (QI.t === 'er') QI.t = 'pen'; setInk(true); return }\n    if (b.dataset.ic) { QZ.inkC = b.dataset.ic;")
    s = rep(s, "function qOverSize() {", "function qSzIcon() { const i = document.querySelector('#rInk .iszb .szi i'); if (i) { const d = 3 + 4 * (QI.k || 1) * .9; i.style.cssText = `width:${d}px;height:${d}px` } }\nfunction qOverSize() {")
    s = rep(s, "  QZ.inkOn = on; QZ.board.locked = !on || QI.full;", "  QZ.inkOn = on; qSzIcon(); QZ.board.locked = !on || QI.full;")
    # laser: a new trail on each press, batched sends
    s = rep(s, "this.laz = true; this.onLaser && this.onLaser(x, y); return }", "this.laz = true; this.onLaser && this.onLaser(x, y, true); return }")
    s = rep(s, """function sendLaser(x, y) {
  laserAt($('#tBoard'), x, y); const n = performance.now();
  if (n - LZ.t > 55 && T.code) { LZ.t = n; DB.set(`sessions/${T.code}/laser`, { x: Math.round(x), y: Math.round(y), t: DB.now() }) }
}""", """function sendLaser(x, y, down) {
  if (down) { lzFlush(); LZ2.sid = (LZ2.sid + 1) % 1e6 }
  laserAdd($('#tBoard'), 't' + LZ2.sid, [x, y]); LZ2.buf.push(Math.round(x), Math.round(y));
  if (performance.now() - LZ.t > 60) lzFlush(); else { clearTimeout(LZ2.ft); LZ2.ft = setTimeout(lzFlush, 70) }
}""")
    s = rep(s, "S.unsubs.push(DB.onValue(b + '/laser', v => { if (v && v.t && DB.now() - v.t < 4000) laserAt($('#sBoard'), v.x, v.y) }));",
            "S.unsubs.push(DB.onValue(b + '/laser', v => { if (v && v.t && DB.now() - v.t < 4000) { if (v.p) laserAdd($('#sBoard'), 's' + v.s, v.p); else laserAt($('#sBoard'), v.x, v.y) } }));")
    return s
