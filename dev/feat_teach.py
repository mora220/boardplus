"""Teaching tools that make the class fairer and more thoughtful:
  * «من يجيب؟» — a fair random pick among the students who are online: nobody is picked twice until everyone has had
    a turn (per lesson). The name lands big on the teacher's screen for the class to see; the picked student gets a
    calm note on his own device («المعلم اختارك، جهّز إجابتك»). From there: pick again, open his board, or make groups.
  * Random groups of 2–5 from the students online, shown big for the class, reshuffled with one tap.
  * Share a solution with the class without the student's name: from a student's board, the teacher puts that work
    on everyone's board to discuss it (error analysis and peer learning), then removes it like any image.
Data: sessions/<code>/pick = {sid, t}"""
import json

ADD_I18N = {
    "من يجيب؟": "Who answers?", "اختيار طالب بعدل": "Pick a student fairly", "اختيار آخر": "Pick another", "افتح سبورته": "Open their board",
    "قسّم مجموعات": "Make groups", "مجموعات عشوائية": "Random groups", "أعد التوزيع": "Shuffle again", "طلاب في كل مجموعة": "students per group",
    "مجموعة": "Group", "لا يوجد طلاب متصلون الآن": "No students online right now", "المعلم اختارك": "Your teacher picked you",
    "جهّز إجابتك واكتبها على سبورتك": "Get your answer ready and write it on your board", "اعرض الحل للفصل": "Show to the class",
    "اعرض الحل للفصل؟": "Show this work to the class?", "يظهر حل الطالب على سبورتك وسبورات الطلاب بدون اسمه، لتناقشوه معًا.": "The work appears on your board and the students' boards without the name, so you can discuss it together.",
    "اعرض": "Show", "ظهر الحل للفصل بدون اسم. احذفه من زر الصورة بعد المناقشة": "The work is on everyone's board, without the name. Remove it from the image button after the discussion",
    "دور جديد: الكل له فرصة من جديد": "New round: everyone has a turn again",
    "كيف فهمتم؟": "Did you understand?", "فهمت": "I got it", "محتاج مثال كمان": "I need another example", "محتاج مساعدة": "I need help",
    "كيف فهمك الآن؟": "How well do you understand now?", "اختر بصراحة، إجابتك تروح للمعلم فقط": "Answer honestly, only your teacher sees it", "وصلت إجابتك للمعلم": "Your teacher got your answer",
    "👁 الأسماء": "👁 Names", "🙈 إخفاء الأسماء": "🙈 Hide names", "⏹ إنهاء": "⏹ End", "الأسماء مخفية حفاظًا على خصوصية الطلاب": "Names are hidden to protect students' privacy",
    "الكل فاهم 👏": "Everyone understood 👏", "👏 ممتاز!": "👏 Excellent!", "👍 تمام، المعلم بيوضح أكثر": "👍 OK, your teacher will explain more", "🤝 ولا يهمك، المعلم بيساعدك": "🤝 No worries, your teacher will help you",
}

CSS = r"""
#tPick{font-weight:700}
.pk-ov{position:fixed;inset:0;z-index:80;display:flex;align-items:center;justify-content:center;padding:18px;background:rgba(13,19,34,.62);backdrop-filter:blur(5px);animation:rpop .25s ease-out}
.pk-card{position:relative;width:min(760px,100%);max-height:100%;overflow:auto;border-radius:28px;padding:0;background:var(--surface);box-shadow:0 4px 0 var(--ring,var(--line)),0 40px 80px -30px rgba(0,0,0,.6)}
.pk-sheet{position:relative;border-radius:28px;padding:30px 26px 24px;color:var(--ink);text-align:center;background:radial-gradient(120% 80% at 50% 0%,var(--accent-soft),var(--surface) 70%);display:flex;flex-direction:column;align-items:center;gap:14px}
.pk-sheet h3{margin:0;font-family:var(--f-display);font-size:24px;color:var(--muted);font-weight:700}
.pk-reel{height:clamp(84px,14vh,130px);display:grid;place-items:center;width:100%;overflow:hidden}
.pk-name{font-family:var(--f-display);font-weight:800;font-size:clamp(46px,8vw,96px);line-height:1.15;color:var(--accent);white-space:nowrap;max-width:100%;overflow:hidden;text-overflow:ellipsis}
.pk-name.spin{color:var(--muted);animation:pkBlur .09s linear infinite}
.pk-name.done{animation:pkLand .5s cubic-bezier(.2,1.6,.4,1)}
@keyframes pkBlur{50%{transform:translateY(-6px)}}
@keyframes pkLand{0%{transform:scale(.6);opacity:.3}100%{transform:none;opacity:1}}
.pk-line{width:min(420px,70%);height:14px;margin-top:-10px;opacity:0}
.pk-line path{stroke-dasharray:500;stroke-dashoffset:500}
.pk-line.on{opacity:1}.pk-line.on path{animation:hxDraw .5s ease-out forwards}
.pk-left{font-size:14.5px;color:var(--muted);font-weight:600}
.pk-act{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}

.pk-x{position:absolute;top:18px;inset-inline-end:18px;z-index:2}
.gp-size{display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:center;font-weight:700;color:var(--muted)}
.gp-size button{min-width:44px}
.gp-size button.on{background:var(--accent)!important;color:var(--accent-ink)!important;border-color:var(--accent)!important}
.gp-grid{width:100%;display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;text-align:start}
.gp{background:var(--surface);border-radius:16px;padding:10px 12px;box-shadow:0 0 0 1.5px var(--line),0 3px 0 var(--ring,var(--line));border-top:6px solid var(--gc)}
.gp b{display:block;font-family:var(--f-display);font-size:15px;color:var(--gc);margin-bottom:4px}
.gp span{display:block;font-size:16px;font-weight:700;padding:2px 0;color:var(--ink)}
/* the picked student */
.pk-me{position:fixed;left:50%;top:max(14px,env(safe-area-inset-top));translate:-50% 0;z-index:90;width:min(420px,calc(100% - 24px));border-radius:16px;padding:14px 18px;
  background:var(--surface);color:var(--ink);box-shadow:0 0 0 3px var(--accent),0 24px 50px -20px rgba(13,19,34,.6);display:flex;gap:12px;align-items:center;animation:pkDrop .45s cubic-bezier(.2,1.4,.4,1)}
.pk-me .e{font-size:34px}.pk-me b{display:block;font-family:var(--f-display);font-size:20px}.pk-me span{font-size:14px;color:var(--muted)}
@keyframes pkDrop{from{transform:translateY(-30px);opacity:0}to{transform:none;opacity:1}}
#fShare{font-weight:700}
/* check for understanding */
.fl-card{position:fixed;inset-inline-start:16px;bottom:96px;z-index:45;width:min(330px,calc(100% - 32px));background:var(--surface);color:var(--ink);border-radius:16px;padding:14px 16px;box-shadow:0 0 0 1px var(--line),0 24px 50px -22px rgba(13,19,34,.55);animation:rpop .25s ease-out}
.fl-card h4{margin:0 0 10px;font-family:var(--f-display);font-size:17px;display:flex;align-items:center;gap:8px}
.fl-card h4 small{margin-inline-start:auto;font-family:inherit;font-size:13px;color:var(--muted);font-weight:600}
.fl-row{display:grid;grid-template-columns:auto 1fr 34px;align-items:center;gap:8px;margin:7px 0;font-weight:600;font-size:14.5px}
.fl-bar{height:12px;border-radius:99px;background:var(--surface-2);overflow:hidden}
.fl-bar i{display:block;height:100%;border-radius:99px;transition:width .5s}
.fl-row b{text-align:end;font-family:var(--f-display)}
.fl-names{font-size:13.5px;color:var(--muted);margin:6px 0 0;line-height:1.7}
.fl-names b{color:var(--ink)}
.fl-act{display:flex;gap:8px;margin-top:10px}
.fl-act .btn{flex:1;padding:8px}
.sc .fdot{position:absolute;top:10px;inset-inline-start:10px;width:16px;height:16px;border-radius:50%;box-shadow:0 0 0 3px var(--surface)}
.sc{position:relative}
.fl-sheet{position:fixed;left:0;right:0;bottom:0;z-index:85;background:var(--surface);color:var(--ink);border-radius:22px 22px 0 0;padding:18px 16px calc(18px + env(safe-area-inset-bottom));box-shadow:0 -20px 50px -20px rgba(13,19,34,.5);animation:flUp .35s cubic-bezier(.2,1.2,.4,1)}
@keyframes flUp{from{transform:translateY(100%)}to{transform:none}}
.fl-sheet h3{margin:0 0 4px;text-align:center;font-family:var(--f-display);font-size:20px}
.fl-sheet p{margin:0 0 14px;text-align:center;color:var(--muted);font-size:14px}
.fl-opts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;max-width:560px;margin:0 auto}
.fl-opts button{all:unset;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:6px;padding:14px 6px;border-radius:16px;text-align:center;font-weight:700;font-size:15px;border:2px solid var(--line);background:var(--surface)}
.fl-opts button .e{font-size:36px;line-height:1}
.fl-opts button:focus-visible{outline:3px solid var(--accent)}
.fl-opts .g{border-color:#9fdcbf;background:#effaf4}.fl-opts .y{border-color:#f5d77a;background:#fffaea}.fl-opts .r{border-color:#f3a6ad;background:#fff1f2}
:root[data-theme="dark"] .fl-opts button{color:#17213b}
#tFeel{font-weight:700}
.eqr{background:#fff;padding:8px;border-radius:12px;box-shadow:0 0 0 1px var(--line);margin:2px auto 4px;width:max-content}
.eqr img,.eqr canvas{display:block;width:128px!important;height:128px!important}
"""

JS = r"""
/* ======================= who answers? groups, and sharing a solution ======================= */
const PK = { used: null, code: null, timer: 0 };
function pkOnline() { return [...T.st.entries()].filter(([, s]) => s && s.info && s.info.name && s.info.online).map(([sid, s]) => ({ sid, n: s.info.name })) }
function pkUsed() { if (PK.code !== T.code) { PK.code = T.code; try { PK.used = new Set(JSON.parse(ls.get('bp_pick_' + T.code) || '[]')) } catch (e) { PK.used = new Set() } } return PK.used }
function pkSave() { try { ls.set('bp_pick_' + T.code, JSON.stringify([...PK.used])) } catch (e) {} }
function pkClose() { clearInterval(PK.timer); document.querySelectorAll('.pk-ov').forEach(x => x.remove()) }
function pkShell(inner) {
  pkClose(); const ov = document.createElement('div'); ov.className = 'pk-ov';
  ov.innerHTML = `<div class="pk-card"><button class="btn icon pk-x" type="button" aria-label="إغلاق">${svgI('x')}</button><div class="pk-sheet">${inner}</div></div>`;
  document.body.appendChild(ov); ov.querySelector('.pk-x').onclick = pkClose; ov.addEventListener('click', e => { if (e.target === ov) pkClose() });
  return ov;
}
function openPicker() {
  if (!T.code) return; const all = pkOnline();
  if (!all.length) return toast('لا يوجد طلاب متصلون الآن', true);
  const used = pkUsed(); let pool = all.filter(x => !used.has(x.sid)), round = false;
  if (!pool.length) { used.clear(); pool = all; round = true }
  const win = pool[Math.floor(Math.random() * pool.length)];
  const ov = pkShell(`<h3>🎯 من يجيب؟</h3><div class="pk-reel"><div class="pk-name spin">…</div></div>
    <svg class="pk-line" viewBox="0 0 420 14" preserveAspectRatio="none"><path d="M4 9 C 120 2, 260 14, 416 5" fill="none" stroke="var(--hl,#ffd84d)" stroke-width="7" stroke-linecap="round"/></svg>
    <div class="pk-left"></div><div class="pk-act" hidden><button class="btn pri" data-a="again">🎯 اختيار آخر</button><button class="btn" data-a="open">✍️ افتح سبورته</button><button class="btn" data-a="groups">👥 قسّم مجموعات</button></div>`);
  const nm = ov.querySelector('.pk-name'), names = all.map(x => x.n); let i = 0, n = 0, delay = 55;
  if (round) toast('دور جديد: الكل له فرصة من جديد');
  const step = () => {
    nm.textContent = names[i++ % names.length]; SFX.tick(false); n++;
    if (n > 18) delay *= 1.16;
    if (delay > 330 || names.length === 1) {
      nm.textContent = win.n; nm.classList.remove('spin'); nm.classList.add('done'); ov.querySelector('.pk-line').classList.add('on');
      SFX.chime(); if (typeof FX !== 'undefined') FX.cheer(.8, .16);
      used.add(win.sid); pkSave(); DB.set(`sessions/${T.code}/pick`, { sid: win.sid, t: DB.now() });
      const left = all.filter(x => !used.has(x.sid)).length;
      ov.querySelector('.pk-left').textContent = left ? `بقي ${left} من ${all.length} لم يأتِ دورهم بعد` : 'جاء دور كل الطلاب المتصلين، الاختيار القادم يبدأ دورًا جديدًا';
      const act = ov.querySelector('.pk-act'); act.hidden = false;
      act.onclick = e => { const b = e.target.closest('[data-a]'); if (!b) return; const a = b.dataset.a;
        if (a === 'again') openPicker(); else if (a === 'open') { pkClose(); openFocus(win.sid) } else if (a === 'groups') openGroups() };
      return;
    }
    PK.timer = setTimeout(step, delay);
  };
  step();
}
function openGroups(size) {
  const all = pkOnline(); if (all.length < 2) return toast('لا يوجد طلاب متصلون الآن', true);
  size = size || +(ls.get('bp_gsize') || 3) || 3;
  const sh = all.slice().sort(() => Math.random() - .5), k = Math.max(1, Math.round(sh.length / size)), groups = Array.from({ length: k }, () => []);
  sh.forEach((x, i) => groups[i % k].push(x.n));
  const cols = ['#1f4fd8', '#e5313b', '#16a06a', '#c47f00', '#7b3fc4', '#0e8fa3', '#d6336c', '#17213b'];
  const ov = pkShell(`<h3>👥 مجموعات عشوائية</h3>
    <div class="gp-size">${[2, 3, 4, 5].map(n => `<button class="btn${n === size ? ' on' : ''}" data-s="${n}">${n}</button>`).join('')}<span>طلاب في كل مجموعة</span></div>
    <div class="gp-grid">${groups.map((g, i) => `<div class="gp" style="--gc:${cols[i % cols.length]}"><b>مجموعة ${i + 1}</b>${g.map(n => `<span>${esc(n)}</span>`).join('')}</div>`).join('')}</div>
    <div class="pk-act"><button class="btn pri" data-a="re">🔀 أعد التوزيع</button><button class="btn" data-a="pick">🎯 من يجيب؟</button></div>`);
  ov.querySelector('.gp-size').onclick = e => { const b = e.target.closest('[data-s]'); if (!b) return; ls.set('bp_gsize', b.dataset.s); openGroups(+b.dataset.s) };
  ov.querySelector('.pk-act').onclick = e => { const b = e.target.closest('[data-a]'); if (!b) return; if (b.dataset.a === 're') openGroups(size); else openPicker() };
  SFX.chime();
}
async function shareSolution() {
  const s = T.st.get(T.focus); if (!s || !T.code) return;
  if (!(await ask('اعرض الحل للفصل؟', 'يظهر حل الطالب على سبورتك وسبورات الطلاب بدون اسمه، لتناقشوه معًا.', 'اعرض'))) return;
  const c = document.createElement('canvas'); c.width = W; c.height = H; const x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, W, H);
  try { paintBg(x, 1, T.bg.type, T.bg.img, T.bg.tr, T.bg.more) } catch (e) {}
  paintMap(x, s.strokes, 1);
  closeFocus();
  try { await stashActive(); await DB.remove(`sessions/${T.code}/meta/imgT`); await DB.set(`sessions/${T.code}/bgImg`, c.toDataURL('image/jpeg', .85)); toast('ظهر الحل للفصل بدون اسم. احذفه من زر الصورة بعد المناقشة') }
  catch (e) { toast('تعذر عرض الحل، حاول مرة ثانية', true) }
}
/* check for understanding: every student says how well they understood, privately */
const FL = { names: false, id: null };
const FL_OPTS = [['g', '🟢', 'فهمت', '#16a06a'], ['y', '🟡', 'محتاج مثال كمان', '#e0a800'], ['r', '🔴', 'محتاج مساعدة', '#e5313b']];
async function startFeel() {
  if (!T.code) return; const cur = await DB.get(`sessions/${T.code}/feel`).catch(() => null);
  if (cur && cur.id) { FL.id = cur.id; return feelRefresh(true) }
  FL.id = 'f' + uid(); FL.names = false; await DB.set(`sessions/${T.code}/feel`, { id: FL.id, t: DB.now() }); feelRefresh(true);
}
function feelRefresh(open) {
  let c = document.querySelector('.fl-card');
  const marks = () => T.st.forEach(s => { let d = s.card.querySelector('.fdot'); const f = FL.id && FL.names && s.info.feel && s.info.feel.id === FL.id ? s.info.feel.v : '';
    if (!f) { d && d.remove(); return } if (!d) { d = document.createElement('i'); d.className = 'fdot'; s.card.appendChild(d) } d.style.background = FL_OPTS.find(o => o[0] === f)[3] });
  if (!FL.id) { c && c.remove(); marks(); return }
  if (!c && !open) return;
  if (!c) { c = document.createElement('div'); c.className = 'fl-card'; document.body.appendChild(c) }
  const st = [...T.st.values()].filter(s => s.info && s.info.name), cnt = { g: [], y: [], r: [] };
  st.forEach(s => { const f = s.info.feel; if (f && f.id === FL.id && cnt[f.v]) cnt[f.v].push(s.info.name) });
  const done = cnt.g.length + cnt.y.length + cnt.r.length, wait = st.filter(s => s.info.online).length - done;
  c.innerHTML = `<h4>🚦 كيف فهمتم؟<small>${done} من ${st.length}</small></h4>
    ${FL_OPTS.map(([k, e, n, col]) => `<div class="fl-row"><span>${e} ${n}</span><span class="fl-bar"><i style="width:${done ? cnt[k].length / done * 100 : 0}%;background:${col}"></i></span><b>${cnt[k].length}</b></div>`).join('')}
    ${FL.names ? `<p class="fl-names">${cnt.r.length ? `<b>🔴 محتاج مساعدة:</b> ${cnt.r.map(esc).join('، ')}<br>` : ''}${cnt.y.length ? `<b>🟡 محتاج مثال:</b> ${cnt.y.map(esc).join('، ')}` : ''}${!cnt.r.length && !cnt.y.length ? 'الكل فاهم 👏' : ''}</p>` : `<p class="fl-names">${wait > 0 ? `⏳ ${wait} لم يجيبوا بعد · ` : ''}الأسماء مخفية حفاظًا على خصوصية الطلاب</p>`}
    <div class="fl-act"><button class="btn" data-a="names">${FL.names ? '🙈 إخفاء الأسماء' : '👁 الأسماء'}</button><button class="btn" data-a="end">⏹ إنهاء</button></div>`;
  c.onclick = async e => { const b = e.target.closest('[data-a]'); if (!b) return;
    if (b.dataset.a === 'names') { FL.names = !FL.names; feelRefresh() }
    else { await DB.remove(`sessions/${T.code}/feel`); FL.id = null; FL.names = false; c.remove(); marks() } };
  marks();
}
function feelAsk(v) {
  const old = document.querySelector('.fl-sheet');
  if (!v || !v.id) { old && old.remove(); return }
  if (S.feelId === v.id || old) return;
  const sh = document.createElement('div'); sh.className = 'fl-sheet'; sh.setAttribute('role', 'dialog');
  sh.innerHTML = `<h3>🚦 كيف فهمك الآن؟</h3><p>اختر بصراحة، إجابتك تروح للمعلم فقط</p><div class="fl-opts">${FL_OPTS.map(([k, e, n]) => `<button type="button" class="${k}" data-v="${k}"><span class="e">${e}</span>${n}</button>`).join('')}</div>`;
  document.body.appendChild(sh); SFX.chime();
  sh.onclick = async e => { const b = e.target.closest('[data-v]'); if (!b) return; S.feelId = v.id;
    try { await DB.update(`sessions/${S.code}/roster/${S.sid}`, { feel: { v: b.dataset.v, id: v.id } }) } catch (x) {}
    sh.innerHTML = `<h3>${b.dataset.v === 'g' ? '👏 ممتاز!' : b.dataset.v === 'y' ? '👍 تمام، المعلم بيوضح أكثر' : '🤝 ولا يهمك، المعلم بيساعدك'}</h3><p>وصلت إجابتك للمعلم</p>`; setTimeout(() => sh.remove(), 1800) };
}
function pickedMe(v) {
  if (!v || v.sid !== S.sid || !v.t || DB.now() - v.t > 15000 || PK.seen === v.t) return; PK.seen = v.t;
  document.querySelectorAll('.pk-me').forEach(x => x.remove());
  const d = document.createElement('div'); d.className = 'pk-me'; d.setAttribute('role', 'status');
  d.innerHTML = `<span class="e">🎯</span><div><b>المعلم اختارك</b><span>جهّز إجابتك واكتبها على سبورتك</span></div>`;
  document.body.appendChild(d); SFX.chime(); setTimeout(() => d.remove(), 6000); d.onclick = () => d.remove();
}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, '    <button class="btn" id="tNew" title="جلسة جديدة">',
            '    <button class="btn" id="tPick" title="اختيار طالب بعدل: لا يتكرر أحد حتى يأتي دور الجميع">🎯 <span class="hide-md">من يجيب؟</span></button>\n    <button class="btn" id="tNew" title="جلسة جديدة">')
    s = rep(s, '    <button class="btn danger" id="fWipe">',
            '    <button class="btn" id="fShare" title="يظهر حل الطالب على سبورات الجميع بدون اسمه">📢 <span class="hide-sm">اعرض الحل للفصل</span></button>\n    <button class="btn danger" id="fWipe">')
    s = rep(s, "  $('#tCls').onclick = () => openClasses();", "  $('#tCls').onclick = () => openClasses();\n  $('#tPick').onclick = openPicker; $('#fShare').onclick = shareSolution;")
    s = rep(s, "  S.unsubs.push(DB.onValue(b + '/laser',", "  S.unsubs.push(DB.onValue(b + '/pick', pickedMe));\n  S.unsubs.push(DB.onValue(b + '/feel', feelAsk));\n  S.unsubs.push(DB.onValue(b + '/laser',")
    s = rep(s, '    <button class="btn" id="tNew" title="جلسة جديدة">', '    <button class="btn" id="tFeel" title="كيف فهمتم؟ كل طالب يقيّم فهمه، والإجابات تصلك أنت فقط">🚦 <span class="hide-md">كيف فهمتم؟</span></button>\n    <button class="btn" id="tNew" title="جلسة جديدة">')
    s = rep(s, "  $('#tPick').onclick = openPicker;", "  $('#tPick').onclick = openPicker; $('#tFeel').onclick = startFeel;")
    s = rep(s, "  if (T.focus === sid) fillFocusHead();\n  sortCards();", "  if (T.focus === sid) fillFocusHead();\n  if (FL.id) feelRefresh();\n  sortCards();")
    # the waiting screen shows the QR itself, ready for the projector
    s = rep(s, "if (a.dataset.a === 'qr') showQR(); else addDemoStudents() };\n}\nfunction addStudent",
            "if (a.dataset.a === 'qr') showQR(); else addDemoStudents() };\n"
            "  { const q = document.createElement('div'); q.className = 'eqr'; e.querySelector('.bigcode').after(q); try { new QRCode(q, { text: joinLink(T.code), width: 300, height: 300, correctLevel: QRCode.CorrectLevel.M }) } catch (x) { q.remove() } }\n}\nfunction addStudent")
    # a new lesson ends the check
    s = rep(s, "T.tMap.clear(); T.bg.img = null;", "T.tMap.clear(); FL.id = null; document.querySelectorAll('.fl-card').forEach(x => x.remove()); T.bg.img = null;")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
