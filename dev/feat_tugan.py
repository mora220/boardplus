"""The teacher stays in charge of the learning during the self-paced quiz and the tug of war:
  * Under the arena (and under the top five in the self-paced quiz): a question analysis panel. Each student with how
    many questions he answered (no right/wrong per student), and one button per question with how many answered it
    right and wrong. Questions that most of the class got wrong are marked.
  * Tapping a question opens it big: the counts, how many chose each option, the correct answer only when the
    teacher shows it, and a pen (pen, calligraphy pen, eraser, colours, sizes) to explain and solve it on the screen.
  * When the race or the tug ends: the questions with the fewest right answers come first, with a button to go through
    them one by one."""

CSS = r"""
#raceT.tugon .tug{bottom:auto;height:56%}
#raceT.tugon .an{position:absolute;left:0;right:0;bottom:0;top:56%;overflow:auto;border-radius:0}
#raceT:not(.tugon){overflow:auto}
#raceT:not(.tugon) .an{margin:14px auto 24px;width:min(1180px,96%);flex:none}
.an{direction:rtl;color:#16233d;padding:14px 18px;border-radius:20px;
  background:#fbfcff;background-image:linear-gradient(rgba(47,91,211,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(47,91,211,.07) 1px,transparent 1px);background-size:22px 22px;box-shadow:0 -6px 24px rgba(0,0,0,.18)}
.an-h{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px}
.an-h h3{margin:0;font-size:21px;display:flex;align-items:center;gap:8px}
.an-h .k{background:#fff;border:1.5px solid #d6dff0;border-radius:99px;padding:5px 12px;font-weight:700;font-size:14.5px}
.an-h .k.ok{border-color:#1f9d55;color:#137a3f}.an-h .k b{font-size:17px}
.an-h .grow{flex:1}
.an-h .rbtn{background:#2f5bd3;color:#fff}
.an-h .rbtn.hd{background:#e0244f}
.an-sub{font-weight:800;font-size:14px;color:#5b6886;margin:10px 0 6px}
.anqs{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:8px}
.anq{all:unset;cursor:pointer;display:flex;flex-direction:column;gap:5px;background:#fff;border:1.5px solid #d6dff0;border-radius:14px;padding:8px 10px;box-shadow:0 2px 0 #e3e9f5;transition:transform .12s}
.anq:hover{transform:translateY(-2px);border-color:#2f5bd3}
.anq b{font-size:16px;display:flex;align-items:center;gap:6px}
.anq b i{font-style:normal;margin-inline-start:auto;font-size:13px;color:#5b6886}
.anq .bar{height:8px;border-radius:99px;background:#fde3e7;overflow:hidden}
.anq .bar i{display:block;height:100%;background:#1f9d55;border-radius:99px}
.anq.none .bar{background:#eef1f7}
.anq small{font-size:13px;font-weight:700;color:#5b6886}
.anq small .o{color:#137a3f}.anq small .x{color:#c0182c}
.anq.hard{border-color:#e0244f;box-shadow:0 2px 0 #f6c3cc}
.anq.hard b::after{content:"⚠️";font-size:13px}
.anss{display:flex;flex-wrap:wrap;gap:6px}
.anst{display:inline-flex;align-items:center;gap:6px;background:#fff;border:1px solid #d6dff0;border-radius:99px;padding:4px 10px;font-size:14px;font-weight:600}
.anst i{width:9px;height:9px;border-radius:50%;background:#94a3b8}
.anst b{font-size:12.5px;color:#5b6886;font-weight:800}
.anst.dn{border-color:#1f9d55}
.anhard{display:flex;gap:8px;flex-wrap:wrap;align-items:center;background:#fff3f5;border:1.5px dashed #e0244f;border-radius:14px;padding:8px 12px}
.anhard .anq{min-width:120px}
/* the question, big, with a pen */
.rq-view{position:fixed;inset:0;z-index:60;display:flex;flex-direction:column;direction:rtl;color:#16233d;background:#fbfcff;
  background-image:linear-gradient(rgba(47,91,211,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(47,91,211,.06) 1px,transparent 1px);background-size:24px 24px}
.rqh{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:10px 14px;background:#fff;border-bottom:1px solid #d6dff0}
.rqh b{font-size:20px}
.rqs{border-radius:99px;padding:5px 12px;font-weight:800;background:#eef2fb}
.rqs.ok{background:#e3f6ea;color:#137a3f}.rqs.no{background:#fde3e7;color:#c0182c}
.rqh .grow{flex:1}
.rqh .rbtn{background:#eef2fb;color:#16233d}
.rqh .rbtn.pri{background:#2f5bd3;color:#fff}.rqh .rbtn.red{background:#e0244f;color:#fff}
.rqh .rbtn:disabled{opacity:.4}
.rqb{position:relative;flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 250px;gap:16px;padding:58px 16px 16px}
.rqimg{display:grid;place-items:center;min-height:0}
.rqimg img{max-width:100%;max-height:100%;border-radius:14px;background:#fff;box-shadow:0 10px 30px -12px rgba(0,0,0,.35)}
.rqopts{display:flex;flex-direction:column;gap:10px;justify-content:center}
.rqo{display:grid;grid-template-columns:44px 1fr 34px;align-items:center;gap:8px;background:#fff;border:1.5px solid #d6dff0;border-radius:14px;padding:8px 10px}
.rqo b{font:900 26px var(--f-display);text-align:center}
.rqo .bar{height:12px;border-radius:99px;background:#eef1f7;overflow:hidden}
.rqo .bar i{display:block;height:100%;background:#8da2c8;border-radius:99px}
.rqo small{font-weight:800;font-size:16px;text-align:center}
.rqo.ans{border-color:#1f9d55;background:#e9f8ef}.rqo.ans .bar i{background:#1f9d55}
.rqo em{grid-column:1/-1;font-style:normal;font-weight:800;color:#137a3f;font-size:14px}
.rqcv{position:absolute;inset:0;width:100%;height:100%;z-index:3;touch-action:none;cursor:crosshair}
.rqbar{position:absolute;top:10px;left:50%;translate:-50% 0;inset-inline-end:auto;z-index:4;flex-wrap:wrap;justify-content:center;max-width:96%}
.rqbar .isep{width:1px;background:var(--line);margin:4px 3px}
.rqbar .isz{width:30px}.rqbar .isz i{display:block;margin:auto;border-radius:50%;background:currentColor}
.rqbar button.off{opacity:.45}
@media (max-width:820px){.rqb{grid-template-columns:1fr;grid-template-rows:minmax(0,1fr) auto}.rqopts{flex-direction:row;flex-wrap:wrap}.rqo{flex:1;min-width:130px}}
"""

JS = r"""
/* ======================= question analysis for the teacher ======================= */
function qStats(sq, a) {
  const n = sq.n || 0, st = Array.from({ length: n }, () => ({ ok: 0, no: 0, c: {} }));
  for (const m of Object.values(a || {})) for (const [j, v] of Object.entries(m || {})) if (/^\d+$/.test(j) && v && st[+j]) { const s = st[+j]; if (v.ok) s.ok++; else s.no++; if (v.c) s.c[v.c] = (s.c[v.c] || 0) + 1 }
  return st;
}
function hardOrder(sq, a) { const st = qStats(sq, a); return st.map((x, i) => ({ i, t: x.ok + x.no, pc: x.ok + x.no ? x.ok / (x.ok + x.no) : 1 })).filter(x => x.t).sort((p, q) => p.pc - q.pc || q.t - p.t).map(x => x.i) }
function anQ(x, i) {
  const t = x.ok + x.no, pc = t ? Math.round(x.ok / t * 100) : 0;
  return `<button class="anq${!t ? ' none' : pc < 50 ? ' hard' : ''}" data-rq="${i}" title="اضغط لعرض السؤال وشرحه"><b>س${i + 1}<i>${t ? pc + '%' : '—'}</i></b><span class="bar"><i style="width:${t ? pc : 0}%"></i></span><small><span class="o">✓ ${x.ok}</span> · <span class="x">✗ ${x.no}</span></small></button>`;
}
function anHTML(sq, a) {
  const st = qStats(sq, a), n = sq.n || 0, team = sq.team || {}, end = sq.st === 'end';
  const ok = st.reduce((s, x) => s + x.ok, 0), all = st.reduce((s, x) => s + x.ok + x.no, 0), acc = all ? Math.round(ok / all * 100) : 0;
  const studs = [...T.st.entries()].filter(([, s]) => s && s.info && s.info.name).map(([sid, s]) => {
    const k = Object.entries((a || {})[sid] || {}).filter(([j, v]) => /^\d+$/.test(j) && v).length, tm = sq.mode === 'tug' ? team[sid] : '';
    return { n: s.info.name, k, c: tm === 'r' ? '#e63946' : tm === 'b' ? '#2f6fe0' : '' };
  }).sort((x, y) => x.n.localeCompare(y.n, 'ar', { numeric: true }));
  const hard = hardOrder(sq, a).slice(0, 3);
  return `<div class="an-h"><h3>📐 تحليل الأسئلة</h3><span class="k">📘 ${esc(sq.title || '')}</span><span class="k">${n} أسئلة</span><span class="k ok">✓ دقة الفصل <b>${acc}%</b></span><span class="k">✍️ ${all} إجابة</span><span class="grow"></span>
      ${hard.length ? `<button class="rbtn hd" data-hard>📉 الأسئلة الأصعب</button>` : ''}<button class="rbtn" data-rq="0">🔍 استعراض الأسئلة</button></div>
    ${end && hard.length ? `<div class="an-sub">📉 الأسئلة الأقل إجابة صحيحة · اضغط لعرضها وحلّها</div><div class="anhard">${hard.map(i => anQ(st[i], i)).join('')}</div>` : ''}
    <div class="an-sub">📊 كل سؤال: عدد الإجابات الصحيحة والخاطئة</div><div class="anqs">${st.map(anQ).join('')}</div>
    <div class="an-sub">👥 الطلاب وعدد الأسئلة التي أجابوها</div><div class="anss">${studs.map(x => `<span class="anst${x.k >= n ? ' dn' : ''}"><i${x.c ? ` style="background:${x.c}"` : ''}></i>${esc(x.n)} <b>${x.k}/${n}</b></span>`).join('') || '<span class="anst">—</span>'}</div>`;
}
const RQ = { key: null, imgs: new Map(), ink: new Map(), pad: { t: 'pen', c: '#e0242f', k: 1 } };
function tImg(i) { const k = RACE.sq.id + ':' + i; if (!RQ.imgs.has(k)) RQ.imgs.set(k, DB.get(`sessions/${T.code}/sqi/${i}`).catch(() => null)); return RQ.imgs.get(k) }
function inkPad(box, map) {
  const P = RQ.pad, hist = [...map.keys()]; let cur = null;
  const bar = document.createElement('div'); bar.className = 'inkbar rqbar';
  bar.innerHTML = [['pen', 'قلم'], ['cal', 'قلم الخط العربي'], ['er', 'ممسحة']].map(([t, n]) => `<button data-pt="${t}" title="${n}">${svgI(t)}</button>`).join('') + '<i class="isep"></i>'
    + ['#e0242f', '#2f5bd3', '#1f9d55', '#15213a'].map(c => `<button data-pc="${c}" title="لون"><span class="sw" style="background:${c}"></span></button>`).join('') + '<i class="isep"></i>'
    + [[.6, 4, 'رفيع'], [1, 7, 'متوسط'], [1.8, 10, 'عريض'], [3, 14, 'عريض جدًا']].map(([k, d, n]) => `<button data-pk="${k}" class="isz" title="${n}"><i style="width:${d}px;height:${d}px"></i></button>`).join('') + '<i class="isep"></i>'
    + `<button data-pa="undo" title="تراجع">${svgI('undo')}</button><button data-pa="clear" title="مسح الكتابة">${svgI('trash')}</button>`;
  const cv = document.createElement('canvas'); cv.className = 'rqcv'; box.append(cv, bar);
  const sync = () => bar.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.pt === P.t || (P.t !== 'er' && b.dataset.pc === P.c) || (!!b.dataset.pk && +b.dataset.pk === P.k)));
  const size = () => { const r = cv.getBoundingClientRect(), d = Math.min(devicePixelRatio || 1, 2), w = Math.round(r.width * d), h = Math.round(r.height * d); if (w && (cv.width !== w || cv.height !== h)) { cv.width = w; cv.height = h } paint() };
  const paint = () => { const x = cv.getContext('2d'), d = cv.width / Math.max(1, cv.getBoundingClientRect().width); x.clearRect(0, 0, cv.width, cv.height); map.forEach(s => drawStroke(x, s, d)) };
  const pt = e => { const r = cv.getBoundingClientRect(); return [Math.round(e.clientX - r.left), Math.round(e.clientY - r.top)] };
  cv.addEventListener('pointerdown', e => { if (cur) return; e.preventDefault(); cv.setPointerCapture(e.pointerId); const id = 'k' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5);
    cur = { id, s: { t: P.t, c: P.c, w: (P.t === 'er' ? 16 : 4) * P.k, p: pt(e) } }; map.set(id, cur.s); paint() });
  cv.addEventListener('pointermove', e => { if (!cur) return; (e.getCoalescedEvents ? e.getCoalescedEvents() : [e]).forEach(ev => cur.s.p.push(...pt(ev))); paint() });
  ['pointerup', 'pointercancel'].forEach(t => cv.addEventListener(t, () => { if (cur) { hist.push(cur.id); cur = null } }));
  bar.onclick = e => {
    const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.pt) P.t = b.dataset.pt; else if (b.dataset.pc) { P.c = b.dataset.pc; if (P.t === 'er') P.t = 'pen' } else if (b.dataset.pk) P.k = +b.dataset.pk;
    else if (b.dataset.pa === 'undo') { const id = hist.pop(); if (id) { map.delete(id); paint() } } else if (b.dataset.pa === 'clear') { map.clear(); hist.length = 0; paint() }
    sync();
  };
  const ro = new ResizeObserver(size); ro.observe(cv); sync(); size();
  return { stop: () => ro.disconnect() };
}
async function rqOpen(i, order) {
  const sq = RACE.sq; if (!sq || !(sq.n > 0)) return; order = order && order.length ? order : [...Array(sq.n).keys()]; if (!order.includes(i)) i = order[0];
  if (!RQ.key || RQ.key.id !== sq.id) { RQ.key = { id: sq.id, v: (await DB.get(`sessions/${T.code}/sqk`).catch(() => null)) || {} }; RQ.ink.clear() }
  const el = $('#raceT'); el.querySelectorAll('.rq-view').forEach(x => { x._pad && x._pad.stop(); x.remove() });
  const v = document.createElement('div'); v.className = 'rq-view'; el.appendChild(v);
  let reveal = false; const kind = (sq.kind || [])[i] || 'mc', ans = RQ.key.v[i], pos = order.indexOf(i);
  const opts = () => { const x = qStats(sq, RACE.a)[i] || { ok: 0, no: 0, c: {} }, t = x.ok + x.no;
    return KIND_OPTS(kind).map(c => { const k = x.c[c] || 0, a = reveal && c === ans; return `<div class="rqo${a ? ' ans' : ''}"><b>${optLabel(c, kind)}</b><span class="bar"><i style="width:${t ? k / t * 100 : 0}%"></i></span><small>${k}</small>${a ? '<em>✓ الإجابة الصحيحة</em>' : ''}</div>` }).join('') };
  const head = () => { const x = qStats(sq, RACE.a)[i] || { ok: 0, no: 0 }, t = x.ok + x.no;
    return `<b>📐 السؤال ${i + 1} من ${sq.n}</b><span class="rqs ok">✓ ${x.ok} صحيحة</span><span class="rqs no">✗ ${x.no} خاطئة</span><span class="rqs">${t ? Math.round(x.ok / t * 100) + '% من الإجابات صحيحة' : 'لم يُجب أحد بعد'}</span><span class="grow"></span>
      <button class="rbtn pri" data-a="rev">${reveal ? '🙈 إخفاء الإجابة' : '👁 إظهار الإجابة'}</button><button class="rbtn" data-a="prev" ${pos <= 0 ? 'disabled' : ''}>→ السابق</button><button class="rbtn" data-a="next" ${pos >= order.length - 1 ? 'disabled' : ''}>التالي ←</button><button class="rbtn red" data-a="x">✕ إغلاق</button>` };
  v.innerHTML = `<div class="rqh">${head()}</div><div class="rqb"><div class="rqimg"><img alt="سؤال ${i + 1}"></div><div class="rqopts">${opts()}</div></div>`;
  tImg(i).then(src => { const im = v.querySelector('img'); if (src && im) im.src = src });
  const k = sq.id + ':' + i; if (!RQ.ink.has(k)) RQ.ink.set(k, new Map()); v._pad = inkPad(v.querySelector('.rqb'), RQ.ink.get(k));
  v._upd = () => { v.querySelector('.rqh').innerHTML = head(); v.querySelector('.rqopts').innerHTML = opts() };
  v.querySelector('.rqh').onclick = e => { const b = e.target.closest('[data-a]'); if (!b) return; const a = b.dataset.a;
    if (a === 'x') { v._pad.stop(); v.remove() } else if (a === 'rev') { reveal = !reveal; v._upd() } else if (a === 'prev' && pos > 0) { rqOpen(order[pos - 1], order) } else if (a === 'next' && pos < order.length - 1) { rqOpen(order[pos + 1], order) } };
}
document.addEventListener('click', e => {
  const q = e.target.closest('#raceT [data-rq]'); if (q && !q.closest('.rq-view')) { rqOpen(+q.dataset.rq, q.closest('.anhard') ? hardOrder(RACE.sq, RACE.a) : null); return }
  const h = e.target.closest('#raceT [data-hard]'); if (h) { const o = hardOrder(RACE.sq, RACE.a); if (o.length) rqOpen(o[0], o) }
});
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    # tug: the analysis under the arena
    s = rep(s, '<div class="tg-act" id="tgAct"></div><div id="tgFx"></div></div>`;', '<div class="tg-act" id="tgAct"></div><div id="tgFx"></div></div><div class="an" id="tgAn"></div>`;')
    s = rep(s, "  $('#tgMid').innerHTML = `<div class=\"t\">🪢 شد الحبل</div>", "  $('#tgAn').innerHTML = anHTML(sq, RACE.a); { const rv = el.querySelector('.rq-view'); if (rv && rv._upd) rv._upd() }\n  $('#tgMid').innerHTML = `<div class=\"t\">🪢 شد الحبل</div>")
    s = rep(s, "      <button class=\"rbtn\" id=\"tgOk\">إغلاق</button>`;", "      <div style=\"display:flex;gap:10px\"><button class=\"rbtn\" id=\"tgHard\" style=\"background:#e0244f\">📉 الأسئلة الأقل إجابة صحيحة</button><button class=\"rbtn\" id=\"tgOk\">إغلاق</button></div>`;")
    s = rep(s, "el.querySelector('#tugS').appendChild(ov); ov.querySelector('#tgOk').onclick = closeRace;",
            "el.querySelector('#tugS').appendChild(ov); ov.querySelector('#tgOk').onclick = closeRace; ov.querySelector('#tgHard').onclick = () => { ov.remove(); const o = hardOrder(sq, RACE.a); if (o.length) rqOpen(o[0], o); else toast('لا توجد إجابات بعد') };")
    # self-paced: the same analysis under the top five (the open question view stays open across updates)
    s = rep(s, "    <div class=\"lb rlb5\"><div class=\"rstat\"><span>👥 بدأ ${go} من ${tot.length}</span><span>🏁 أنهى ${fin}</span></div>${raceTop5(tot, names)}</div>`;",
            "    <div class=\"lb rlb5\"><div class=\"rstat\"><span>👥 بدأ ${go} من ${tot.length}</span><span>🏁 أنهى ${fin}</span></div>${raceTop5(tot, names)}</div>\n    <div class=\"an an-r\">${anHTML(sq, RACE.a)}</div>`;\n"
            "  { const rv = RACE.rv; if (rv && rv._sq === sq.id && rv.isConnected === false) { el.appendChild(rv); rv._upd && rv._upd() } }")
    s = rep(s, "  const el = $('#raceT'); el.querySelectorAll('.rq-view').forEach(x => { x._pad && x._pad.stop(); x.remove() });",
            "  const el = $('#raceT'); el.querySelectorAll('.rq-view').forEach(x => { x._pad && x._pad.stop(); x.remove() }); RACE.rv = null;")
    s = rep(s, "  const v = document.createElement('div'); v.className = 'rq-view'; el.appendChild(v);", "  const v = document.createElement('div'); v.className = 'rq-view'; el.appendChild(v); RACE.rv = v; v._sq = sq.id;")
    s = rep(s, "    if (a === 'x') { v._pad.stop(); v.remove() }", "    if (a === 'x') { v._pad.stop(); v.remove(); RACE.rv = null }")
    return s
