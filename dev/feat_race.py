"""BoardPlus feature: self-paced quiz (like Wayground / Quizizz).
Every student gets all questions, one after another at their own speed, full screen, with a timer per question,
instant feedback, points for speed and streaks; the teacher watches a live ranking per question.

Room data (session):
  sq            {id, st:'run'|'end', n, at, lim:[], kind:[], title}     public
  sqi/<i>       question image                                         public (fetched one by one)
  sqk/<i>       correct letter                                         teacher only (the room never sends it to students)
  sqa/<sid>/go  {at}            the student pressed start
  sqa/<sid>/<i> {c} from the student; the room adds {at, ok, k, dt, pts, p, s}
"""
import json

ADD_I18N = {
    "كل طالب بسرعته": "Self-paced", "كويز السباق: كل طالب يحل الأسئلة بسرعته": "Race quiz: every student answers at their own pace",
    "إنهاء الكويز": "End quiz", "إغلاق": "Close", "لم يبدأ": "Not started", "أنهى": "Finished", "من": "of",
    "ابدأ 🚀": "Start 🚀", "استعد!": "Get ready!", "جاوب بسرعة واجمع نقاط أكثر": "Answer fast to earn more points",
    "صح!": "Correct!", "خطأ": "Wrong", "الإجابة الصحيحة": "Correct answer", "انتهى الوقت": "Time's up",
    "خلصت! 🎉": "Done! 🎉", "انتظر حتى ينهي المعلم الكويز": "Wait for the teacher to end the quiz", "ترتيبك": "Your rank",
    "نقطة": "pts", "إجابات صحيحة": "correct answers", "النتيجة النهائية": "Final results", "لوحة كويز السباق": "Race quiz board",
    "كويز السباق شغال": "Race quiz running", "سؤال": "Question", "فيه كويز سباق شغال الآن": "A race quiz is already running",
}

CSS = r"""
#qRace{background:#7b3fc4;border-color:#7b3fc4;color:#fff}
.race{position:fixed;inset:0;z-index:36;display:flex;flex-direction:column;background:linear-gradient(160deg,#2a1650,#4a1f7a 55%,#2a1650);color:#fff;font-family:inherit;overflow:hidden}
.race[hidden]{display:none}
.race .rtop{display:flex;align-items:center;gap:10px;padding:10px 14px;flex-shrink:0}
.race .rtop b{font-size:15px}
.race .pill2{background:rgba(255,255,255,.14);border-radius:99px;padding:6px 14px;font-weight:700;font-size:15px;white-space:nowrap}
.race .grow{flex:1}
.race .rbtn{height:40px;border:0;border-radius:12px;padding:0 16px;font:inherit;font-weight:700;cursor:pointer;background:#fff;color:#2a1650}
.race .rbtn.red{background:#e0244f;color:#fff}
.race .tbar{height:8px;background:rgba(255,255,255,.15);flex-shrink:0}
.race .tbar i{display:block;height:100%;width:100%;background:linear-gradient(90deg,#ffd166,#ef476f);transform-origin:right;transition:transform .2s linear}
[dir="ltr"] .race .tbar i{transform-origin:left}
.race .rqimg{flex:1;min-height:0;display:grid;place-items:center;padding:10px 14px;overflow:hidden}
.race .rqimg img{display:block;width:auto;height:auto;max-width:100%;max-height:100%;border-radius:14px;box-shadow:0 10px 30px rgba(0,0,0,.35)}
.race .ropts{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:0 14px 14px;flex-shrink:0}
.race .ropts.two{grid-template-columns:repeat(2,1fr)}
.race .ropt{min-height:86px;border:0;border-radius:16px;font:inherit;font-size:34px;font-weight:800;color:#fff;cursor:pointer;box-shadow:0 6px 0 rgba(0,0,0,.25);transition:transform .08s}
.race .ropt:active{transform:translateY(3px);box-shadow:0 3px 0 rgba(0,0,0,.25)}
.race .ropt:disabled{opacity:.55;cursor:default}
.race .o0{background:#2d70ae}.race .o1{background:#2d9da6}.race .o2{background:#efa929}.race .o3{background:#d5546d}
@media (max-width:640px){.race .ropts{grid-template-columns:repeat(2,1fr)}.race .ropt{min-height:70px;font-size:28px}}
.race .center{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;text-align:center;padding:20px}
.race .center h1{margin:0;font-size:44px}
.race .center p{margin:0;font-size:19px;opacity:.85}
.race .big{font-size:20px;height:62px;padding:0 44px;border-radius:18px;background:#ffd166;color:#2a1650}
.race .fb{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;font-size:46px;font-weight:800;z-index:3;animation:rpop .25s ease-out}
.race .fb small{font-size:22px;font-weight:700;opacity:.95}
.race .fb.ok{background:rgba(31,157,85,.94)}.race .fb.no{background:rgba(224,36,47,.94)}.race .fb.late{background:rgba(90,90,110,.94)}
@keyframes rpop{from{transform:scale(1.15);opacity:0}to{transform:none;opacity:1}}
.race .dots{display:flex;gap:4px;flex-wrap:wrap;justify-content:center}
.race .dots i{width:12px;height:12px;border-radius:50%;background:rgba(255,255,255,.25)}
.race .dots i.y{background:#2ecc71}.race .dots i.n{background:#ef476f}.race .dots i.c{background:#ffd166}
.race .lb{flex:1;overflow:auto;padding:4px 14px 18px}
.race table{width:100%;border-collapse:separate;border-spacing:0 6px}
.race td{background:rgba(255,255,255,.1);padding:8px 10px;font-weight:600;white-space:nowrap}
.race td:first-child{border-radius:0 12px 12px 0;width:44px;text-align:center;font-size:20px}
.race td:last-child{border-radius:12px 0 0 12px;text-align:center;font-size:18px;font-weight:800}
[dir="ltr"] .race td:first-child{border-radius:12px 0 0 12px}[dir="ltr"] .race td:last-child{border-radius:0 12px 12px 0}
.race td.cells{width:100%}
.race .cell{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:7px;margin:1px;font-size:13px;font-weight:800;background:rgba(255,255,255,.14)}
.race .cell.y{background:#2ecc71}.race .cell.n{background:#ef476f}.race .cell.c{outline:2px solid #ffd166}
.race tr.done td{background:rgba(46,204,113,.18)}
.race .podium{display:flex;align-items:flex-end;justify-content:center;gap:14px;padding:10px 0 4px;flex-shrink:0}
.race .podium div{width:150px;border-radius:16px 16px 0 0;background:rgba(255,255,255,.15);text-align:center;padding:10px 6px;display:flex;flex-direction:column;gap:4px;font-weight:700}
.race .podium .p1{height:150px;background:#f2b01e;color:#2a1650}.race .podium .p2{height:115px;background:#cfd8e3;color:#2a1650}.race .podium .p3{height:90px;background:#d08b4c}
.race .podium span{font-size:32px}
.racefab{position:fixed;bottom:84px;inset-inline-end:18px;z-index:30;border:0;border-radius:99px;background:#7b3fc4;color:#fff;font:inherit;font-weight:700;padding:12px 18px;box-shadow:var(--shadow);cursor:pointer}
.racefab[hidden]{display:none}
"""

JS = r"""
/* ======================= race quiz: every student at their own pace ======================= */
const RACE = { sq: null, a: {}, imgs: new Map() };
const raceTotals = a => Object.entries(a || {}).map(([sid, m]) => {
  let pts = 0, ok = 0, n = 0, t = 0; for (const [k, v] of Object.entries(m || {})) if (/^\d+$/.test(k) && v) { n++; pts += v.pts || 0; ok += v.ok ? 1 : 0; t = Math.max(t, v.at || 0) }
  return { sid, pts, ok, n, t, go: !!(m && m.go) };
}).sort((x, y) => y.pts - x.pts || y.ok - x.ok || x.t - y.t);
const medal = i => ['🥇', '🥈', '🥉'][i] || (i + 1);
function raceEl(id) { let e = $('#' + id); if (!e) { e = document.createElement('div'); e.id = id; e.className = 'race'; e.hidden = true; document.body.appendChild(e) } return e }
async function startRace(only) {
  if (QZ.run) return toast('فيه كويز شغال الآن', true);
  if (RACE.sq && RACE.sq.st === 'run') return toast('فيه كويز سباق شغال الآن', true);
  let src = Array.isArray(only) ? only : null;
  if (!src) { const list = setQuestions(); src = QZ.sel && QZ.sel.size ? list.filter(q => QZ.sel.has(q.id)) : list }
  if (!src.length) return toast('أضف سؤالًا واحدًا على الأقل', true);
  const miss = src.findIndex(q => !q.ans); if (miss >= 0) return toast(`حدد الإجابة الصحيحة للسؤال ${miss + 1}`, true);
  const b = `sessions/${T.code}`;
  await Promise.all([DB.set(b + '/sqa', null), DB.set(b + '/sqi', null), DB.set(b + '/sq', null)]);
  await DB.set(b + '/sqk', Object.fromEntries(src.map((q, i) => [i, q.ans])));
  await Promise.all(src.map((q, i) => DB.set(`${b}/sqi/${i}`, q.img)));
  await DB.set(b + '/sq', { id: 'r' + uid(), st: 'run', n: src.length, at: DB.ts(), lim: src.map(q => clampLim(q.lim || QZ.lim)), kind: src.map(q => q.kind || 'mc'), title: setName(curSet()) });
  closeBuilder(); RACE.open = true; drawRaceT();
}
async function endRace() {
  const sq = RACE.sq; if (!sq || sq.st !== 'run') return;
  if (!(await ask('إنهاء الكويز؟', 'يظهر الترتيب النهائي لكل الطلاب.', 'إنهاء الكويز'))) return;
  const b = `sessions/${T.code}`, up = {};
  for (const [sid, m] of Object.entries(RACE.a || {})) { let p = 0; for (const [k, v] of Object.entries(m || {})) if (/^\d+$/.test(k) && v) p += v.p || 0; if (p) up[`${sid}/${sq.id}`] = p }
  if (Object.keys(up).length) await DB.update(b + '/qpts', up);
  await DB.update(b + '/sq', { st: 'end' }); SFX.applause(); confetti();
}
function closeRace() {
  const b = `sessions/${T.code}`; RACE.open = false; raceEl('raceT').hidden = true;
  if (RACE.sq && RACE.sq.st === 'end') ['sq', 'sqi', 'sqk', 'sqa'].forEach(p => DB.remove(`${b}/${p}`));
  drawRaceFab();
}
function drawRaceFab() {
  let f = $('#raceFab'); if (!f) { f = document.createElement('button'); f.id = 'raceFab'; f.className = 'racefab'; f.textContent = '🏁 لوحة كويز السباق'; f.onclick = () => { RACE.open = true; drawRaceT() }; document.body.appendChild(f) }
  f.hidden = !(ROLE === 't' && RACE.sq && !RACE.open && $('#teacher') && !$('#teacher').hidden);
}
function drawRaceT() {
  drawRaceFab(); const el = raceEl('raceT'), sq = RACE.sq;
  if (!sq || !RACE.open) { el.hidden = true; return }
  el.hidden = false; const tot = raceTotals(RACE.a), n = sq.n || 0, names = sid => { const s = T.st.get(sid); return s ? s.info.name : '—' };
  const all = [...T.st.keys()], seen = new Set(tot.map(x => x.sid)); all.forEach(sid => { if (!seen.has(sid)) tot.push({ sid, pts: 0, ok: 0, n: 0, t: 0, go: false }) });
  const fin = tot.filter(x => x.n >= n).length, end = sq.st === 'end';
  const row = (x, i) => { const m = RACE.a[x.sid] || {}; return `<tr class="${x.n >= n ? 'done' : ''}"><td>${medal(i)}</td><td>${esc(names(x.sid))}</td>
    <td class="cells">${x.go ? Array.from({ length: n }, (_, j) => { const v = m[j]; return `<span class="cell ${v ? (v.ok ? 'y' : 'n') : j === x.n && !end ? 'c' : ''}" title="سؤال ${j + 1}${v ? ' · ' + v.dt + 'ث' : ''}">${v ? (v.ok ? '✓' : '✗') : j + 1}</span>` }).join('') : '<span style="opacity:.6">لم يبدأ</span>'}</td>
    <td>${x.ok}/${n}</td><td>${x.pts.toLocaleString()}</td></tr>` };
  el.innerHTML = `<div class="rtop"><b>🏁 ${esc(sq.title || '')} · كل طالب بسرعته</b><span class="grow"></span><span class="pill2">أنهى ${fin} من ${tot.length}</span>
      ${end ? '<button class="rbtn" id="rcClose">إغلاق</button>' : '<button class="rbtn red" id="rcEnd">⏹ إنهاء الكويز</button><button class="rbtn" id="rcHide">إغلاق</button>'}</div>
    ${end ? `<div class="podium">${[1, 0, 2].map(i => tot[i] ? `<div class="p${i + 1}"><span>${medal(i)}</span>${esc(names(tot[i].sid))}<small>${tot[i].pts.toLocaleString()}</small></div>` : '').join('')}</div>` : ''}
    <div class="lb"><table>${tot.map(row).join('')}</table></div>`;
  const c = el.querySelector('#rcEnd'); if (c) c.onclick = endRace;
  const h = el.querySelector('#rcHide'); if (h) h.onclick = () => { RACE.open = false; el.hidden = true; drawRaceFab() };
  const x = el.querySelector('#rcClose'); if (x) x.onclick = closeRace;
}
/* student side */
async function raceImg(i) {
  if (RACE.imgs.has(i)) return RACE.imgs.get(i);
  const p = DB.get(`sessions/${S.code}/sqi/${i}`).catch(() => null); RACE.imgs.set(i, p); const v = await p; if (!v) RACE.imgs.delete(i); return v;
}
function drawRaceS() {
  const el = raceEl('raceS'), sq = RACE.sq;
  if (!sq || ROLE !== 's') { el.hidden = true; el.dataset.k = ''; clearInterval(RACE.tick); return }
  const mine = (RACE.a || {})[S.sid] || {}, n = sq.n || 0; let i = 0; while (mine[i]) i++;
  const tot = raceTotals(RACE.a), me = tot.findIndex(x => x.sid === S.sid), my = tot[me] || { pts: 0, ok: 0 };
  const top = `<div class="rtop"><span class="pill2">${Math.min(i + 1, n)} / ${n}</span><span class="grow"></span>${my.pts ? `<span class="pill2">⭐ ${my.pts.toLocaleString()}</span>` : ''}${me >= 0 && mine.go ? `<span class="pill2">${medal(me)} ${me + 1} من ${tot.length}</span>` : ''}</div>`;
  el.hidden = false;
  if (RACE.fb) return;                                   // feedback on screen; it redraws when it ends
  let key;
  if (sq.st === 'end') key = 'end';
  else if (!mine.go) key = 'start';
  else if (i >= n) key = 'done';
  else key = 'q' + i;
  if (el.dataset.k === key) { const t = el.querySelector('.rtop'); if (t) t.outerHTML = top; return }
  el.dataset.k = key; clearInterval(RACE.tick);
  if (key === 'start') {
    el.innerHTML = top + `<div class="center"><h1>🏁 استعد!</h1><p>${n} أسئلة · جاوب بسرعة واجمع نقاط أكثر</p><button class="rbtn big" id="rsGo">ابدأ 🚀</button></div>`;
    el.querySelector('#rsGo').onclick = () => { audio(); try { document.documentElement.requestFullscreen && !document.fullscreenElement && document.documentElement.requestFullscreen().catch(() => {}) } catch (e) {} DB.set(`sessions/${S.code}/sqa/${S.sid}/go`, { at: DB.ts() }); raceImg(0) };
    return;
  }
  if (key === 'done' || key === 'end') {
    const dots = Array.from({ length: n }, (_, j) => `<i class="${mine[j] ? (mine[j].ok ? 'y' : 'n') : ''}"></i>`).join('');
    el.innerHTML = top + `<div class="center">${key === 'end' ? `<h1>${medal(me)}</h1><p style="font-size:24px">${me >= 0 ? `ترتيبك ${me + 1} من ${tot.length}` : ''}</p>` : '<h1>خلصت! 🎉</h1>'}
      <p style="font-size:30px;font-weight:800">⭐ ${my.pts.toLocaleString()} نقطة</p><p>${my.ok} / ${n} إجابات صحيحة</p><div class="dots">${dots}</div>
      ${key === 'done' ? '<p>انتظر حتى ينهي المعلم الكويز</p>' : ''}</div>`;
    if (key === 'end' && me >= 0 && me < 3) { confetti(); SFX.applause() }
    return;
  }
  const kind = (sq.kind || [])[i] || 'mc', lim = +((sq.lim || [])[i]) || 30;
  el.innerHTML = top + `<div class="tbar"><i></i></div><div class="rqimg"><img alt="سؤال ${i + 1}"></div>
    <div class="ropts${kind === 'tf' ? ' two' : ''}">${KIND_OPTS(kind).map((c, j) => `<button class="ropt o${j}" data-c="${c}" disabled>${optLabel(c, kind)}</button>`).join('')}</div>`;
  const img = el.querySelector('img'), bar = el.querySelector('.tbar i'), btns = [...el.querySelectorAll('.ropt')];
  let sent = false; const send = c => { if (sent) return; sent = true; clearInterval(RACE.tick); btns.forEach(b => b.disabled = true); RACE.wait = i; DB.set(`sessions/${S.code}/sqa/${S.sid}/${i}`, { c }).catch(() => { RACE.wait = null; el.dataset.k = ''; drawRaceS() }) };
  btns.forEach(b => b.onclick = () => send(b.dataset.c));
  raceImg(i).then(src => {
    if (el.dataset.k !== key) return; if (src) img.src = src; if (i + 1 < n) raceImg(i + 1);
    btns.forEach(b => b.disabled = false); const t0 = performance.now();
    RACE.tick = setInterval(() => { const left = 1 - (performance.now() - t0) / 1000 / lim; bar.style.transform = `scaleX(${Math.max(0, left)})`; if (left <= 0) send('') }, 100);
  });
}
function raceFeedback(v) {
  const el = raceEl('raceS'), d = document.createElement('div');
  d.className = 'fb ' + (v.ok ? 'ok' : v.c ? 'no' : 'late');
  d.innerHTML = v.ok ? `✓ صح!<small>+${(v.pts || 0).toLocaleString()}${v.s > 1 ? ` · 🔥 ×${v.s}` : ''}</small>` : `${v.c ? '✗ خطأ' : '⏰ انتهى الوقت'}<small>الإجابة الصحيحة: ${optLabel(v.k, (RACE.sq.kind || [])[RACE.wait] || 'mc')}</small>`;
  v.ok ? SFX.chime() : SFX.tone(220, 0, .35, .18, 'sawtooth');
  el.appendChild(d); RACE.fb = true;
  setTimeout(() => { RACE.fb = false; d.remove(); drawRaceS() }, 1300);
}
function raceSub(b, isT) {
  const un = [];
  un.push(DB.onValue(b + '/sq', v => { const was = RACE.sq && RACE.sq.id; RACE.sq = v || null; if (!v || v.id !== was) { RACE.imgs.clear(); RACE.fb = false; const s = $('#raceS'); if (s) s.dataset.k = '' } isT ? drawRaceT() : drawRaceS() }));
  un.push(DB.onValue(b + '/sqa', v => {
    RACE.a = v || {};
    if (!isT && RACE.wait != null) { const r = ((RACE.a[S.sid] || {})[RACE.wait]); if (r && r.at) { RACE.wait = null; raceFeedback(r); return } }
    isT ? drawRaceT() : drawRaceS();
  }));
  un.push(() => { RACE.sq = null; RACE.a = {}; RACE.open = false; RACE.wait = null; RACE.fb = false; clearInterval(RACE.tick); ['raceS', 'raceT'].forEach(id => { const e = $('#' + id); if (e) { e.hidden = true; e.dataset.k = '' } }); drawRaceFab() });
  return un;
}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, '    <button class="btn pri" id="qStart"><svg class="ico"><use href="#i-play"/></svg><span>ابدأ الكويز</span></button>',
            '    <button class="btn" id="qRace" title="كويز السباق: كل طالب يحل الأسئلة بسرعته">🏁 <span>كل طالب بسرعته</span></button>\n'
            '    <button class="btn pri" id="qStart"><svg class="ico"><use href="#i-play"/></svg><span>ابدأ الكويز</span></button>')
    s = rep(s, "  $('#qStart').onclick = () => startQuiz();", "  $('#qStart').onclick = () => startQuiz();\n  $('#qRace').onclick = () => startRace();")
    s = rep(s, "  T.unsubs.push(DB.onValue(b + '/show', v => T.showP && T.showP(v)));",
            "  T.unsubs.push(DB.onValue(b + '/show', v => T.showP && T.showP(v)));\n  RACE.open = false; T.unsubs.push(...raceSub(b, true));")
    s = rep(s, "  S.unsubs.push(DB.onValue(b + '/show', v => S.showP && S.showP(v)));",
            "  S.unsubs.push(DB.onValue(b + '/show', v => S.showP && S.showP(v)));\n  S.unsubs.push(...raceSub(b, false));")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
