"""BoardPlus feature: several pages per class.
The page on screen always lives in the normal live paths (tStrokes, bgImg, meta/bgType, meta/imgT, sb/*, mk/*),
so students and every other feature keep working unchanged. Pages that are not on screen are kept as snapshots
under pages/<id>/{info, tStrokes, bgImg, sb/<sid>, mk/<sid>}. meta/pages = {order: [ids], cur: id}.
Points are stored separately (pts/, qpts/) so switching pages never changes anyone's score.
"""
import json

ADD_I18N = {
    "الصفحة السابقة": "Previous page", "الصفحة التالية": "Next page", "صفحة جديدة": "New page", "صفحات السبورة": "Board pages",
    "صفحة": "Page", "الحالية": "current", "حذف هذه الصفحة": "Delete this page", "حذف الصفحة؟": "Delete the page?",
    "سيُحذف كل ما فيها: كتابتك وصورة السؤال وحلول الطلاب في هذه الصفحة.": "Everything on it will be deleted: your writing, the question image and the students' work on this page.",
    "جاري فتح الصفحة…": "Opening the page…", "تعذر تغيير الصفحة. تأكد من الإنترنت": "Couldn't change the page. Check your internet",
    "انتقل المعلم إلى": "The teacher moved to", "كل صفحة لها كتابتها وصورتها وحلول الطلاب الخاصة بها. النقاط لا تتغير.": "Each page keeps its own writing, image and student work. Points don't change.",
}

CSS = r"""
#teacher .stage{position:relative}
.pager{position:absolute;bottom:12px;inset-inline-start:12px;z-index:6;display:flex;align-items:center;gap:2px;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:4px;box-shadow:var(--shadow)}
.pager button{width:36px;height:36px;border:0;border-radius:10px;background:transparent;color:var(--ink);font-size:20px;font-weight:700;cursor:pointer;display:grid;place-items:center}
.pager button:hover:not(:disabled){background:var(--surface-2)}
.pager button:disabled{opacity:.3;cursor:default}
.pager .pl{width:auto;padding:0 10px;font-size:14px;font-weight:700;white-space:nowrap}
.pager .pa{background:var(--accent);color:#fff}
.pager .pa:hover:not(:disabled){background:var(--accent);filter:brightness(1.08)}
[dir="rtl"] .pager #pgPrev,[dir="rtl"] .pager #pgNext{transform:scaleX(-1)}
.pager.busy{opacity:.6;pointer-events:none}
.pglist{display:flex;flex-direction:column;gap:6px;max-height:55vh;overflow:auto}
.pglist button{display:flex;justify-content:space-between;align-items:center;border:1.5px solid var(--line);border-radius:12px;background:var(--surface);padding:12px 14px;font:inherit;font-weight:600;color:var(--ink);cursor:pointer}
.pglist button.cur{border-color:var(--accent);background:var(--accent-soft,#eef3ff)}
"""

MARKUP_OLD = '<div class="stage"><div id="tBoard"></div></div>'
MARKUP_NEW = ('<div class="stage"><div id="tBoard"></div>'
              '<div class="pager" id="tPager"><button id="pgPrev" title="الصفحة السابقة" aria-label="الصفحة السابقة">‹</button>'
              '<button class="pl" id="pgLbl" title="صفحات السبورة">صفحة 1 / 1</button>'
              '<button id="pgNext" title="الصفحة التالية" aria-label="الصفحة التالية">›</button>'
              '<button class="pa" id="pgAdd" title="صفحة جديدة" aria-label="صفحة جديدة">+</button></div></div>')

JS = r"""
/* ======================= board pages ======================= */
const PG = { busy: false };
const pagesMeta = () => { const p = T.meta && T.meta.pages; return p && Array.isArray(p.order) && p.order.length ? { order: [...p.order], cur: p.order.includes(p.cur) ? p.cur : p.order[0] } : { order: ['p1'], cur: 'p1' } };
const mapObj = m => { const o = {}; m.forEach((v, k) => { if (v) o[k] = v }); return Object.keys(o).length ? o : null };
function renderPager() {
  const P = pagesMeta(), i = P.order.indexOf(P.cur);
  $('#pgLbl').textContent = `صفحة ${i + 1} / ${P.order.length}`;
  $('#pgPrev').disabled = i <= 0; $('#pgNext').disabled = i >= P.order.length - 1;
  $('#tPager').classList.toggle('busy', PG.busy);
}
async function savePage(id) {
  const p = `sessions/${T.code}/pages/${id}`, sids = [...T.st.keys()];
  await DB.set(p, { info: { bgType: T.bg.type || 'grid', imgT: T.bg.tr || null, at: DB.now(), sids } });
  const w = [DB.set(p + '/tStrokes', mapObj(T.tMap)), DB.set(p + '/bgImg', T.bg.img && T.bg.img.src ? T.bg.img.src : null)];
  T.st.forEach((s, sid) => { const a = mapObj(s.strokes), m = mapObj(s.marks); if (a) w.push(DB.set(`${p}/sb/${sid}`, a)); if (m) w.push(DB.set(`${p}/mk/${sid}`, m)) });
  await Promise.all(w);
}
async function loadPage(id, P) {
  const b = `sessions/${T.code}`, p = `${b}/pages/${id}`;
  const info = (await DB.get(p + '/info')) || {};
  const [ts, img] = await Promise.all([DB.get(p + '/tStrokes'), DB.get(p + '/bgImg')]);
  const sids = new Set([...T.st.keys(), ...(info.sids || [])]), w = [];
  for (const sid of sids) {
    const has = (info.sids || []).includes(sid);
    w.push((has ? DB.get(`${p}/sb/${sid}`) : Promise.resolve(null)).then(v => DB.set(`${b}/sb/${sid}`, v || null)));
    w.push((has ? DB.get(`${p}/mk/${sid}`) : Promise.resolve(null)).then(v => DB.set(`${b}/mk/${sid}`, v || null)));
  }
  w.push(DB.set(b + '/tStrokes', ts || null), DB.set(b + '/bgImg', img || null));
  await Promise.all(w);
  await DB.update(b + '/meta', { bgType: info.bgType || T.bg.type || 'grid', imgT: info.imgT || null, pages: P });
  DB.remove(p).catch(() => {});      // it is live again; the snapshot is rewritten when we leave the page
}
async function goPage(to, { order, save = true } = {}) {
  if (PG.busy || !T.code) return; const P = pagesMeta(); if (order) P.order = order;
  if (to === P.cur && !order) return;
  PG.busy = true; renderPager(); if (IE.on) imgEdit(false);
  const t = setTimeout(() => toast('جاري فتح الصفحة…'), 600);
  try {
    if (save) await savePage(P.cur);
    P.cur = to; await loadPage(to, P);
    tBoard.clearHist();
  } catch (e) { console.error(e); toast('تعذر تغيير الصفحة. تأكد من الإنترنت', true) }
  clearTimeout(t); PG.busy = false; renderPager();
}
function addPage() { const P = pagesMeta(), id = 'p' + uid(), i = P.order.indexOf(P.cur); P.order.splice(i + 1, 0, id); goPage(id, { order: P.order }) }
function stepPage(d) { const P = pagesMeta(), i = P.order.indexOf(P.cur) + d; if (i >= 0 && i < P.order.length) goPage(P.order[i]) }
function pagesMenu() {
  const P = pagesMeta();
  modal(`<h3>صفحات السبورة</h3><p class="muted" style="margin:0">كل صفحة لها كتابتها وصورتها وحلول الطلاب الخاصة بها. النقاط لا تتغير.</p>
    <div class="pglist">${P.order.map((id, i) => `<button data-pg="${id}" class="${id === P.cur ? 'cur' : ''}"><span>صفحة ${i + 1}</span>${id === P.cur ? '<small>الحالية</small>' : '<span>›</span>'}</button>`).join('')}</div>
    <div class="row"><button class="btn danger" id="pgDel">${svgI('trash')} حذف هذه الصفحة</button><button class="btn pri" id="pgNew">+ صفحة جديدة</button><button class="btn" data-close>إغلاق</button></div>`, (v, close) => {
    v.querySelectorAll('[data-pg]').forEach(b => b.onclick = () => { close(); goPage(b.dataset.pg) });
    v.querySelector('#pgNew').onclick = () => { close(); addPage() };
    v.querySelector('#pgDel').onclick = async () => {
      close(); if (!(await ask('حذف الصفحة؟', 'سيُحذف كل ما فيها: كتابتك وصورة السؤال وحلول الطلاب في هذه الصفحة.', 'حذف'))) return;
      const Q = pagesMeta(), i = Q.order.indexOf(Q.cur);
      if (Q.order.length === 1) { const b = `sessions/${T.code}`; DB.remove(b + '/tStrokes'); DB.remove(b + '/bgImg'); DB.remove(b + '/meta/imgT'); T.st.forEach((s, sid) => { DB.remove(`${b}/sb/${sid}`); DB.remove(`${b}/mk/${sid}`) }); tBoard.clearHist(); return }
      const order = Q.order.filter(x => x !== Q.cur); goPage(order[Math.max(0, i - 1)], { order, save: false });
    };
  });
}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, MARKUP_OLD, MARKUP_NEW)
    # teacher: keep the pager in sync with meta and wire its buttons
    s = rep(s, "    if (T.bg.type !== m.bgType) { T.bg.type = m.bgType; baseChanged() }\n",
            "    if (T.bg.type !== m.bgType) { T.bg.type = m.bgType; baseChanged() }\n    renderPager();\n")
    s = rep(s, "  tTool = makeToolbar($('#tTools'), {",
            "  $('#pgPrev').onclick = () => stepPage(-1); $('#pgNext').onclick = () => stepPage(1); $('#pgAdd').onclick = addPage; $('#pgLbl').onclick = pagesMenu;\n"
            "  tTool = makeToolbar($('#tTools'), {")
    # student: say which page the teacher opened and reset undo for the new page
    s = rep(s, "    S.meta = mt; S.board.locked = !!mt.locked; S.veil.hidden = !mt.locked;",
            "    { const pg = mt.pages && mt.pages.cur, ord = (mt.pages && mt.pages.order) || []; if (S.pgCur && pg && pg !== S.pgCur) { S.board.clearHist(); toast(`📄 انتقل المعلم إلى صفحة ${ord.indexOf(pg) + 1}`) } S.pgCur = pg || S.pgCur || 'p1' }\n"
            "    S.meta = mt; S.board.locked = !!mt.locked; S.veil.hidden = !mt.locked;")
    s = rep(s, "  ROLE = 's'; S.myPts = { b: 0, q: 0 };", "  S.pgCur = null; ROLE = 's'; S.myPts = { b: 0, q: 0 };")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
