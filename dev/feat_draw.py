"""BoardPlus: smart pen (hand-drawn line / arrow / rectangle / triangle / circle become clean shapes),
simpler toolbars (lasso instead of the separate shape tools), question images moved into "show students",
and the page controls moved into the bottom toolbar."""
import json

ADD_I18N = {
    "قلم ذكي: ارسم شكلًا باليد ويتعدّل تلقائيًا (خط، سهم، مستطيل، مثلث، دائرة)": "Smart pen: draw a shape by hand and it is straightened (line, arrow, rectangle, triangle, circle)",
    "صورة سؤال على السبورة": "Question image on the board", "من جهازك": "From your device", "لصق صورة منسوخة": "Paste a copied image",
    "عرض للطلاب: صورة سؤال، صوت، فيديو، رابط، باوربوينت": "Show students: question image, audio, video, link, PowerPoint",
    "أو اعرض لهم": "Or show them",
}

CSS = r"""
#tTools .pager{position:static;box-shadow:none;border:0;background:transparent;padding:0;gap:2px}
#tTools .pager button{width:36px;height:36px}
#tTools .pager .pl{width:auto;font-size:13px;padding:0 6px}
.shimg{display:flex;gap:8px;flex-wrap:wrap}
.shimg .btn{flex:1;min-width:150px;justify-content:center}
.showsrc h4{margin:4px 0 0;font-size:14px;color:var(--muted)}
"""

ICON = '    <symbol id="i-smart" viewBox="0 0 24 24"><path d="M4 20l4-1 9.5-9.5-3-3L5 16l-1 4z"/><path d="M13 8l3 3"/><path d="M19 2.5v4M17 4.5h4"/></symbol>\n'

JS = r"""
/* ======================= smart pen: hand-drawn shapes become clean shapes ======================= */
function rdp(P, eps) {
  if (P.length < 3) return P.slice();
  const [ax, ay] = P[0], [bx, by] = P[P.length - 1], L = Math.hypot(bx - ax, by - ay) || 1;
  let k = 0, dm = 0;
  for (let i = 1; i < P.length - 1; i++) { const [x, y] = P[i]; const d = L > 1 ? Math.abs((by - ay) * x - (bx - ax) * y + bx * ay - by * ax) / L : Math.hypot(x - ax, y - ay); if (d > dm) { dm = d; k = i } }
  if (dm <= eps) return [P[0], P[P.length - 1]];
  const A = rdp(P.slice(0, k + 1), eps), B = rdp(P.slice(k), eps); return A.slice(0, -1).concat(B);
}
function recognizeShape(p) {
  const n = p.length / 2; if (n < 5) return null;
  const P = []; let L = 0, a = 1e9, b = 1e9, c = -1e9, d = -1e9;
  for (let i = 0; i < p.length; i += 2) { const x = p[i], y = p[i + 1]; if (i) L += Math.hypot(x - p[i - 2], y - p[i - 1]); a = Math.min(a, x); c = Math.max(c, x); b = Math.min(b, y); d = Math.max(d, y); P.push([x, y]) }
  const w = c - a, h = d - b, diag = Math.hypot(w, h); if (diag < 24 || L < 24) return null;
  const [x0, y0] = P[0], [x1, y1] = P[P.length - 1], gap = Math.hypot(x1 - x0, y1 - y0);
  if (gap > Math.max(.2 * diag, 22) || L < 1.8 * diag) {
    if (gap / L > .92) return { t: 'line', p: [x0, y0, x1, y1] };
    let fi = 0, fd = 0, Ls = 0, Lf = 0;                                     // arrow: straight shaft, then a short head
    for (let i = 1; i < P.length; i++) { Ls += Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); const dd = Math.hypot(P[i][0] - x0, P[i][1] - y0); if (dd > fd) { fd = dd; fi = i; Lf = Ls } }
    const tail = L - Lf;
    if (fd > 40 && fd / Lf > .9 && tail > .07 * fd && tail < .9 * fd && fi < P.length - 2) return { t: 'arrow', p: [x0, y0, P[fi][0], P[fi][1]] };
    return null;
  }
  let V = rdp(P.concat([P[0]]), .07 * diag); V = V.slice(0, -1);
  if (V.length > 1 && Math.hypot(V[0][0] - V[V.length - 1][0], V[0][1] - V[V.length - 1][1]) < .12 * diag) V.pop();
  const ang = i => { const A = V[(i + V.length - 1) % V.length], B = V[i], C = V[(i + 1) % V.length]; const u = [A[0] - B[0], A[1] - B[1]], v = [C[0] - B[0], C[1] - B[1]]; return Math.acos(Math.max(-1, Math.min(1, (u[0] * v[0] + u[1] * v[1]) / ((Math.hypot(...u) * Math.hypot(...v)) || 1)))) * 180 / Math.PI };
  if (V.length === 3) return { t: 'poly', p: V.flat() };
  if (V.length === 4 && [0, 1, 2, 3].every(i => Math.abs(ang(i) - 90) < 24)) {
    const e = Math.atan2(V[1][1] - V[0][1], V[1][0] - V[0][0]) * 180 / Math.PI, off = Math.abs(((e % 90) + 90) % 90);
    if (off < 14 || off > 76) return { t: 'rect', p: [a, b, c, d] };
    return { t: 'poly', p: V.flat() };
  }
  const cx = (a + c) / 2, cy = (b + d) / 2, rx = Math.max(w / 2, 1), ry = Math.max(h / 2, 1);
  let err = 0; for (const [x, y] of P) err += Math.abs(Math.hypot((x - cx) / rx, (y - cy) / ry) - 1); err /= P.length;
  if (err < .17) { if (Math.abs(w - h) < .14 * Math.max(w, h)) { const r = (w + h) / 4; return { t: 'ell', p: [cx - r, cy - r, cx + r, cy + r] } } return { t: 'ell', p: [a, b, c, d] } }
  if (V.length >= 4 && V.length <= 6) return { t: 'poly', p: V.flat() };
  return null;
}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, '    <symbol id="i-img" viewBox', ICON + '    <symbol id="i-img" viewBox')
    # draw closed polygons
    s = rep(s, "    case 'rect': ctx.strokeRect(", "    case 'poly': { ctx.beginPath(); for (let i = 0; i < p.length; i += 2) i ? ctx.lineTo(p[i] * k, p[i + 1] * k) : ctx.moveTo(p[i] * k, p[i + 1] * k); ctx.closePath(); ctx.stroke(); break }\n    case 'rect': ctx.strokeRect(")
    # smart tool: draw like a pen, then replace by the recognised shape when the pen lifts
    s = rep(s, "    const shape = ['line', 'arrow', 'rect', 'ell'].includes(t.t);\n    const s = { t: t.t, c: t.c, w: t.w, p: shape ? [x, y, x, y] : [x, y] };\n    const id = uid(); this.cur = { id, s, shape };",
            "    const shape = ['line', 'arrow', 'rect', 'ell'].includes(t.t), smart = t.t === 'smart';\n    const s = { t: smart ? 'pen' : t.t, c: t.c, w: t.w, p: shape ? [x, y, x, y] : [x, y] };\n    const id = uid(); this.cur = { id, s, shape, smart };")
    s = rep(s, "    const { id, s } = this.cur; this.cur = null; this.sink.write(id, s); this.hist.push(id);",
            "    let { id, s, smart } = this.cur; this.cur = null;\n"
            "    if (smart) { const r = recognizeShape(s.p); if (r) { s = { t: r.t, c: s.c, w: s.w, p: r.p.map(v => Math.round(v)) }; this.map.set(id, s); this.mark(this.target) } }\n"
            "    this.sink.write(id, s); this.hist.push(id);")
    s = rep(s, "pen: 'قلم', hl: 'قلم تظليل',", "pen: 'قلم', smart: 'قلم ذكي: ارسم شكلًا باليد ويتعدّل تلقائيًا (خط، سهم، مستطيل، مثلث، دائرة)', hl: 'قلم تظليل',")
    # toolbars: one smart pen instead of line / arrow / rectangle / circle
    s = rep(s, "    tools: ['pen', 'hl', 'er', 'text', 'line', 'arrow', 'rect', 'ell'],\n    colors: ['#15213a', '#2f5bd3', '#e0242f', '#1f9d55', '#e07b16', '#7b3fc4'],",
            "    tools: ['pen', 'smart', 'hl', 'er', 'lasso', 'text'],\n    colors: ['#15213a', '#2f5bd3', '#e0242f', '#1f9d55', '#e07b16', '#7b3fc4'],")
    s = rep(s, "    tools: ['pen', 'hl', 'er', 'text', 'arrow', 'ell', 'cut'], stamps: true,", "    tools: ['pen', 'smart', 'hl', 'er', 'text', 'cut', 'lasso'], stamps: true,")
    s = rep(s, "    tools: ['pen', 'hl', 'er', 'text', 'line', 'arrow', 'rect', 'ell'],\n    colors: ['#15213a', '#2f5bd3', '#1f9d55', '#7b3fc4', '#e07b16'],",
            "    tools: ['pen', 'smart', 'hl', 'er', 'lasso', 'text'],\n    colors: ['#15213a', '#2f5bd3', '#1f9d55', '#7b3fc4', '#e07b16'],")
    # question image buttons move into "show students"
    s = rep(s, "      { icon: 'img', label: 'إضافة صورة سؤال', onClick: pickImage },\n      { icon: 'paste', label: 'لصق صورة منسوخة', onClick: pasteImage },\n", "")
    s = rep(s, "{ icon: 'show', label: 'عرض للطلاب: صوت، فيديو، رابط، باوربوينت',", "{ icon: 'show', label: 'عرض للطلاب: صورة سؤال، صوت، فيديو، رابط، باوربوينت',")
    s = rep(s, "    <div class=\"drop\" id=\"shDrop\" tabindex=\"0\" role=\"button\">",
            "    <h4>صورة سؤال على السبورة</h4><div class=\"shimg\"><button class=\"btn\" id=\"shImg\">${svgI('img')} من جهازك</button><button class=\"btn\" id=\"shPaste\">${svgI('paste')} لصق صورة منسوخة</button></div>\n"
            "    <h4>أو اعرض لهم</h4><div class=\"drop\" id=\"shDrop\" tabindex=\"0\" role=\"button\">")
    s = rep(s, "    const err = v.querySelector('#shErr'), prog = v.querySelector('#shProg');",
            "    const err = v.querySelector('#shErr'), prog = v.querySelector('#shProg');\n"
            "    v.querySelector('#shImg').onclick = () => { close(); pickImage() }; v.querySelector('#shPaste').onclick = () => { close(); pasteImage() };")
    # page controls live in the bottom toolbar now
    s = rep(s, "  tBoard = new Board($('#tBoard'), { layers: ['bg', 't'], target: 't', tool: tTool.get,",
            "  { const sp = document.createElement('span'); sp.className = 'sep'; $('#tTools').append(sp, $('#tPager')) }\n  tBoard = new Board($('#tBoard'), { layers: ['bg', 't'], target: 't', tool: tTool.get,")
    # recordings: the lasso never opens the player; deleting with it on a student's board also removes the recording data
    s = rep(s, "    if (t.t !== 'cut') { const hit = mediaAt(this, x, y);", "    if (t.t !== 'cut' && t.t !== 'lasso') { const hit = mediaAt(this, x, y);")
    s = rep(s, "  if (Object.keys(up).length) DB.update(`sessions/${T.code}/sb/${T.focus}`, up);",
            "  if (Object.keys(up).length) DB.update(`sessions/${T.code}/sb/${T.focus}`, up);\n  A.del.forEach(v => { if (v && v.t === 'media') DB.remove(`sessions/${T.code}/media/${T.focus}/${v.mid}`) });")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
