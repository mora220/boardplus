"""Several images on the board: pasting or adding a new image keeps the earlier ones.
The image on top is the one being edited (bgImg + meta/imgT, as before); the others live in sessions/<code>/imgs/<id> = {src, tr, z}.
In move mode a tap on another image brings it to the top so it can be moved, resized, cropped or deleted."""

JS = r"""
/* ======================= several images on the board ======================= */
const IMGS = { raw: {}, cache: new Map() };
async function loadMore(raw) {
  const out = [];
  for (const [id, v] of Object.entries(raw || {}).sort((a, b) => ((a[1] && a[1].z) || 0) - ((b[1] && b[1].z) || 0))) {
    if (!v || !v.src) continue; let im = IMGS.cache.get(v.src); if (!im) { im = await loadImg(v.src); if (im) IMGS.cache.set(v.src, im) }
    if (im) out.push({ id, img: im, tr: v.tr || null });
  }
  return out;
}
function quadTr(img, n) {        // a quarter of the board, starting at the top right (the boards are Arabic first)
  const m = 24, cw = W / 2 - 2 * m, ch = H / 2 - 2 * m, w = Math.min(cw, ch * img.width / img.height), q = n % 4;
  return { x: Math.round((q % 2 ? 0 : W / 2) + m + (cw - w) / 2), y: Math.round((q > 1 ? H / 2 : 0) + m), w: Math.round(w) };
}
const fitTr = img => { const r = bgRect(img, null); return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.w) } };
async function stashActive() {    // the image on top joins the others, so a new image can be added
  if (!T.code || !T.bg.img || !T.bg.img.src) return 0;
  const n = (T.bg.more || []).length, tr = T.bg.tr && T.bg.tr.w ? T.bg.tr : quadTr(T.bg.img, 0);
  await DB.set(`sessions/${T.code}/imgs/i${uid()}`, { src: T.bg.img.src, tr, z: Date.now() });
  return n + 1;
}
function imgAt(p) {
  const a = curRect(); if (a && p[0] >= a.x && p[0] <= a.x + a.w && p[1] >= a.y && p[1] <= a.y + a.h) return null;
  const more = T.bg.more || [];
  for (let i = more.length - 1; i >= 0; i--) { const m = more[i], r = bgRect(m.img, m.tr); if (p[0] >= r.x && p[0] <= r.x + r.w && p[1] >= r.y && p[1] <= r.y + r.h) return m }
  return null;
}
function imgSwap(p) { const m = imgAt(p); if (!m) return false; pickImg(m); return true }
async function pickImg(m) {
  const b = `sessions/${T.code}`, w = { [`imgs/${m.id}`]: null, bgImg: m.img.src, 'meta/imgT': m.tr || null }, more = (T.bg.more || []).filter(x => x !== m);
  if (T.bg.img && T.bg.img.src) { const id = 'i' + uid(), tr = T.bg.tr && T.bg.tr.w ? T.bg.tr : fitTr(T.bg.img); w[`imgs/${id}`] = { src: T.bg.img.src, tr, z: Date.now() }; more.push({ id, img: T.bg.img, tr }) }
  T.bg.img = m.img; T.bg.tr = m.tr ? { ...m.tr } : null; T.bg.more = more; baseChanged(); IE.on && placeBox();
  try { await DB.update(b, w) } catch (e) { toast('تعذر تحديث الصورة', true) }
}
async function delActive() {
  const more = T.bg.more || [], top = more[more.length - 1], b = `sessions/${T.code}`;
  if (!top) { DB.remove(b + '/bgImg'); DB.remove(b + '/meta/imgT'); imgEdit(false); return }
  await DB.update(b, { bgImg: top.img.src, 'meta/imgT': top.tr || null, [`imgs/${top.id}`]: null });
}
"""


def apply(s, rep, target):
    # drawing: the other images first, then the one on top
    s = rep(s, 'function paintBg(ctx, k, type, img, tr) {', 'function paintBg(ctx, k, type, img, tr, more) {')
    s = rep(s, '  if (img && img.width) { const b = bgRect(img, tr); ctx.drawImage(img, b.x * k, b.y * k, b.w * k, b.h * k) }',
            '  (more || []).forEach(m => { if (m.img && m.img.width) { const b = bgRect(m.img, m.tr); ctx.drawImage(m.img, b.x * k, b.y * k, b.w * k, b.h * k) } });\n'
            '  if (img && img.width) { const b = bgRect(img, tr); ctx.drawImage(img, b.x * k, b.y * k, b.w * k, b.h * k) }')
    s = rep(s, 'paintBg(l.ctx, this.k, b.type, b.img, b.tr)', 'paintBg(l.ctx, this.k, b.type, b.img, b.tr, b.more)')
    s = rep(s, 'paintBg(c, TK, T.bg.type, T.bg.img, T.bg.tr)', 'paintBg(c, TK, T.bg.type, T.bg.img, T.bg.tr, T.bg.more)')
    # teacher and students listen to the other images
    s = rep(s, "  T.unsubs.push(DB.onValue(b + '/bgImg', async src => {",
            "  T.unsubs.push(DB.onValue(b + '/imgs', async v => { IMGS.raw = v || {}; const m = await loadMore(v); if (IMGS.raw !== (v || {}) && v) return; T.bg.more = m; baseChanged() }));\n"
            "  T.unsubs.push(DB.onValue(b + '/bgImg', async src => {")
    s = rep(s, "  S.unsubs.push(DB.onValue(b + '/bgImg', async src => {",
            "  S.unsubs.push(DB.onValue(b + '/imgs', async v => { S.bg.more = await loadMore(v); S.board.mark('bg') }));\n"
            "  S.unsubs.push(DB.onValue(b + '/bgImg', async src => {")
    s = rep(s, 'T.tMap.clear(); T.bg.img = null;', 'T.tMap.clear(); T.bg.img = null; T.bg.more = []; IMGS.raw = {};')
    s = rep(s, 'S.marks.clear(); S.bg.img = null;', 'S.marks.clear(); S.bg.img = null; S.bg.more = [];')
    # a new image keeps the earlier ones
    s = rep(s, "try { IE.pending = true; await DB.remove(`sessions/${T.code}/meta/imgT`); await DB.set(`sessions/${T.code}/bgImg`, c.toDataURL('image/jpeg', .82)); toast('ظهرت الصورة عند الطلاب. حرّكها أو كبّرها ثم اضغط «تم»') }",
            "try { IE.pending = true; const n = await stashActive(); if (n) await DB.set(`sessions/${T.code}/meta/imgT`, quadTr(c, n)); else await DB.remove(`sessions/${T.code}/meta/imgT`); await DB.set(`sessions/${T.code}/bgImg`, c.toDataURL('image/jpeg', .82)); toast(n ? 'أُضيفت الصورة بجانب الصور السابقة. اضغط على أي صورة لتحريكها أو تكبيرها' : 'ظهرت الصورة عند الطلاب. حرّكها أو كبّرها ثم اضغط «تم»') }")
    s = rep(s, "  const f = [...(e.clipboardData ? e.clipboardData.files : [])].find(x => x.type.startsWith('image/'));\n  if (f) { e.preventDefault(); setQuestionImage(f) }",
            "  const fs = [...(e.clipboardData ? e.clipboardData.files : [])].filter(x => x.type.startsWith('image/'));\n  if (fs.length) { e.preventDefault(); (async () => { for (const f of fs) { await setQuestionImage(f); await new Promise(r => setTimeout(r, 1500)) } })() }")
    # tap another image in move mode to bring it on top
    s = rep(s, "  el.addEventListener('pointerdown', e => {\n", "  el.addEventListener('pointerdown', e => {\n    if (!IE.crop && !IE.ptrs.size && !IE.sd && imgSwap(P(e))) { e.preventDefault(); return }\n")
    s = rep(s, "{ DB.remove(`sessions/${T.code}/bgImg`); DB.remove(`sessions/${T.code}/meta/imgT`); imgEdit(false) }", "{ delActive() }")
    # clearing the board, removing the image, and pages
    s = rep(s, "DB.remove(base() + '/bgImg'); DB.remove(base() + '/meta/imgT');", "DB.remove(base() + '/bgImg'); DB.remove(base() + '/imgs'); DB.remove(base() + '/meta/imgT');")
    s = rep(s, "if (b.dataset.b === 'noimg') { DB.remove(`sessions/${T.code}/bgImg`);", "if (b.dataset.b === 'noimg') { DB.remove(`sessions/${T.code}/bgImg`); DB.remove(`sessions/${T.code}/imgs`);")
    s = rep(s, "DB.remove(b + '/tStrokes'); DB.remove(b + '/bgImg');", "DB.remove(b + '/tStrokes'); DB.remove(b + '/bgImg'); DB.remove(b + '/imgs');")
    s = rep(s, "DB.set(p + '/bgImg', T.bg.img && T.bg.img.src ? T.bg.img.src : null)];", "DB.set(p + '/bgImg', T.bg.img && T.bg.img.src ? T.bg.img.src : null), DB.set(p + '/imgs', Object.keys(IMGS.raw).length ? IMGS.raw : null)];")
    s = rep(s, "const [ts, img] = await Promise.all([DB.get(p + '/tStrokes'), DB.get(p + '/bgImg')]);", "const [ts, img, ims] = await Promise.all([DB.get(p + '/tStrokes'), DB.get(p + '/bgImg'), DB.get(p + '/imgs')]);")
    s = rep(s, "w.push(DB.set(b + '/tStrokes', ts || null), DB.set(b + '/bgImg', img || null));", "w.push(DB.set(b + '/tStrokes', ts || null), DB.set(b + '/bgImg', img || null), DB.set(b + '/imgs', ims || null));")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    return s
