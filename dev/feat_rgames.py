"""Race quiz as games: in the self-paced quiz every student chooses how to answer — the usual buttons, or one of the
four adventures from the Mawhiba training site (penalty kicks, river crossing, balloon hunter, galaxy gates).
The answer itself is the move; the room still marks it (the key never reaches the student), then the game plays
the result. The student can change the game at any time with 🎮."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GAMES_JS = open(os.path.join(HERE, 'rgames_src.js'), encoding='utf-8').read()
GAMES_CSS = open(os.path.join(HERE, 'rgames.css'), encoding='utf-8').read()

CSS = r"""
.rg-world{position:relative;flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden;user-select:none;-webkit-user-select:none;color:#fff}
.rg-q{position:relative;z-index:3;flex:0 0 38%;min-height:0;display:grid;place-items:center;padding:8px 12px 4px}
.rg-q img{display:block;max-width:100%;max-height:100%;width:auto;height:auto;border-radius:14px;box-shadow:0 10px 26px -10px rgba(0,0,0,.6);background:#fff}
.rg-world .gm-arena{flex:1 1 0;min-height:220px}
.gx-opt.rgl{justify-content:center;font:900 clamp(26px,5vw,40px)/1.2 var(--f-display)}
.gx-opt.rgl .val{flex:none;text-align:center}
.rg-wait{height:100%;display:grid;place-items:center;font-size:40px}
.rg-res{position:absolute;z-index:12;left:50%;top:calc(38% - 18px);translate:-50% 0;padding:10px 22px;border-radius:999px;font-weight:800;font-size:20px;color:#fff;white-space:nowrap;animation:rpop .25s ease-out;box-shadow:0 10px 24px rgba(0,0,0,.35)}
.rg-res.ok{background:#1f9d55}.rg-res.no{background:#e0244f}
.rg-cards{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;width:min(1000px,100%)}
.rg-cards .gm-card .art{height:86px}
.rg-cards .gm-card b{font-size:15px}
.rg-cards .gm-card .txt{padding:8px 10px 10px}
.gm-card.on{box-shadow:0 0 0 4px #ffd166,0 14px 30px -12px #000}
.race .center.rgs{justify-content:flex-start;overflow:auto;padding-top:14px}
.race .center.rgs h1{font-size:36px}
.rg-modal{position:absolute;inset:0;z-index:20;background:rgba(20,10,40,.9);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;padding:16px;overflow:auto}
.rg-modal h2{margin:0}
.rgsw{border:0;cursor:pointer;color:#fff;font:inherit}
@media (max-width:560px){.rgsw .rgn{display:none}.race .rtop{gap:6px;padding-inline:10px}.race .pill2{padding:6px 10px}}
@media (max-width:760px){.rg-cards{grid-template-columns:repeat(2,minmax(0,1fr))}.rg-cards .gm-card .art{height:70px}}
"""

JS = r"""
/* ======================= race quiz as games (from the Mawhiba training site) ======================= */
const RG_TX = {
  games: {
    penalty: { n: 'ركلات الترجيح', tip: 'اضغط على الخانة لتسدّد' },
    river: { n: 'عبور النهر', tip: 'اضغط على الورقة لتقفز' },
    balloons: { n: 'صيّاد البالونات', tip: 'صوّب واضغط على البالون لتطلق السهم' },
    space: { n: 'بوابات المجرّة', tip: 'اضغط على المسار ثم «انطلق»' }
  },
  penalty: { goal: 'جوووول! ⚽', save: 'تصدّى الحارس! 🧤', you: 'أنت', keeper: 'الحارس', win: (g, v) => `فزت ${g} – ${v} 🏆`, draw: (g, v) => `تعادل ${g} – ${v}`, lose: (g, v) => `الحارس فاز ${v} – ${g}` },
  river: { safe: 'قفزة آمنة! 🌿', sink: 'غرقت الورقة! 💦', bank: '🏁 الضفة الأخرى', total: n => `عبرت النهر ${n} مرة` },
  balloons: { pop: 'إصابة! 🎯', storm: 'بالون خاطئ! ⛈️', miss: 'صوّب على بالون!', total: n => `أصبت ${n} بالون صحيح` },
  space: { go: 'انطلق 🚀', warp: 'قفزة ضوئية! ✨', boom: 'بوابة خاطئة! 💥', total: n => `${n} قفزات ضوئية ناجحة`, out: 'انتهى الوقت!' }
};
const RG_EN = { 'ركلات الترجيح': 'Penalty Shootout', 'عبور النهر': 'River Crossing', 'صيّاد البالونات': 'Balloon Hunter', 'بوابات المجرّة': 'Galaxy Gates', 'اضغط على الخانة لتسدّد': 'Tap a zone to shoot', 'اضغط على الورقة لتقفز': 'Tap a pad to jump', 'صوّب واضغط على البالون لتطلق السهم': 'Aim and tap a balloon to shoot', 'اضغط على المسار ثم «انطلق»': 'Tap a lane, then “Launch”', 'جوووول! ⚽': 'GOAL! ⚽', 'تصدّى الحارس! 🧤': 'Saved by the keeper! 🧤', 'أنت': 'You', 'الحارس': 'Keeper', 'قفزة آمنة! 🌿': 'Safe jump! 🌿', 'غرقت الورقة! 💦': 'The pad sank! 💦', '🏁 الضفة الأخرى': '🏁 Far bank', 'إصابة! 🎯': 'Hit! 🎯', 'بالون خاطئ! ⛈️': 'Wrong balloon! ⛈️', 'صوّب على بالون!': 'Aim at a balloon!', 'انطلق 🚀': 'Launch 🚀', 'قفزة ضوئية! ✨': 'Light jump! ✨', 'بوابة خاطئة! 💥': 'Wrong gate! 💥' };
const gt = (k, ...a) => { const v = k.split('.').reduce((o, x) => o && o[x], RG_TX); const r = typeof v === 'function' ? v(...a) : v; return EN && RG_EN[r] ? RG_EN[r] : r };
const pick = a => a[Math.floor(Math.random() * a.length)];
const GM = { timers: [], mute: false };
const gmWait = ms => new Promise(r => GM.timers.push(setTimeout(r, ms)));
""" + GAMES_JS + r"""
const RG = { gid: ls.get('bp_rgame') || 'classic', d: {}, choose: null };
const RG_LIST = [{ id: 'classic', c1: '#8a4fd6', c2: '#3b1a6e', art: `<svg viewBox="0 0 300 128" preserveAspectRatio="xMidYMid slice"><rect width="300" height="128" fill="#4a1f7a"/><g font-size="26" font-weight="900" fill="#fff" text-anchor="middle"><rect x="18" y="20" width="126" height="40" rx="10" fill="#2d70ae"/><rect x="156" y="20" width="126" height="40" rx="10" fill="#2d9da6"/><rect x="18" y="70" width="126" height="40" rx="10" fill="#efa929"/><rect x="156" y="70" width="126" height="40" rx="10" fill="#d5546d"/><text x="81" y="49">أ</text><text x="219" y="49">ب</text><text x="81" y="99">ج</text><text x="219" y="99">د</text></g></svg>` }, ...GM_GAMES];
const rgName = id => id === 'classic' ? 'الأزرار العادية' : gt('games.' + id + '.n');
const rgCards = () => `<div class="rg-cards">${RG_LIST.map(g => `<button type="button" class="gm-card${RG.gid === g.id ? ' on' : ''}" data-rg="${g.id}" style="--c1:${g.c1};--c2:${g.c2}"><span class="art">${g.art}</span><span class="txt"><b>${rgName(g.id)}</b></span></button>`).join('')}</div>`;
function rgBind(box, after) {
  box.querySelectorAll('[data-rg]').forEach(b => b.onclick = () => {
    RG.gid = b.dataset.rg; ls.set('bp_rgame', RG.gid); box.querySelectorAll('[data-rg]').forEach(x => x.classList.toggle('on', x === b)); gmSnd('tap'); after && after();
  });
}
function rgSwitch(el) {
  if (RACE.fb || RACE.wait != null || el.querySelector('.rg-modal')) return;
  const m = document.createElement('div'); m.className = 'rg-modal';
  m.innerHTML = `<h2>🎮 اختر لعبتك</h2>${rgCards()}<button type="button" class="rbtn">إغلاق</button>`;
  el.appendChild(m); m.querySelector('.rbtn').onclick = () => m.remove();
  rgBind(m, () => { m.remove(); if (RACE.fb || RACE.wait != null) return; el.dataset.k = ''; drawRaceS() });
}
function raceT0(i) { const k = (RACE.sq && RACE.sq.id) + ':' + i; RACE.t0s = RACE.t0s || {}; return RACE.t0s[k] || (RACE.t0s[k] = performance.now()) }
function gmChoose(k) { if (RG.choose) RG.choose(k) }
function rgQuestion(el, top, i, kind, lim, key, n) {
  const G = GMG[RG.gid], letters = KIND_OPTS(kind);
  el.innerHTML = top + `<div class="tbar"><i></i></div><div class="rg-world g-${RG.gid}"><div class="gm-bg">${G.bg ? G.bg() : ''}</div><div class="rg-q"><img alt="سؤال ${i + 1}"></div><div class="gm-arena" id="rgArena"><div class="rg-wait">⏳</div></div></div>`;
  const img = el.querySelector('.rg-q img'), bar = el.querySelector('.tbar i'), ar = el.querySelector('#rgArena');
  const q = { o: letters.map(c => optLabel(c, kind)), a: -1 };
  const s = { gid: RG.gid, G, d: RG.d[RG.gid] || (RG.d[RG.gid] = {}), busy: false, ans: [], i: 0, qs: [q], gain: 0 };
  let sent = false;
  const choose = async k => {
    if (sent || el.dataset.k !== key || s.busy) return; sent = true; s.busy = true; s.ans[0] = k == null ? -1 : k; clearInterval(RACE.tick); RG.choose = null;
    ar.querySelectorAll('.gx-opt').forEach(b => b.disabled = true); const tip = ar.querySelector('.gm-tip'); if (tip) tip.remove();
    RACE.fb = true; RACE.wait = i;
    const res = new Promise(r => { RACE.gw = r });
    DB.set(`sessions/${S.code}/sqa/${S.sid}/${i}`, { c: k == null ? '' : letters[k] }).catch(() => { RACE.wait = null; RACE.gw = null; RACE.fb = false; el.dataset.k = ''; drawRaceS() });
    const v = await res; if (el.dataset.k !== key) return;
    q.a = letters.indexOf(v.k); s.gain = v.pts || 0;
    if (k == null) { gmBanner(ar, '⏰ انتهى الوقت'); gmSnd('lose') }
    else { try { await G.resolve(ar, s, k, !!v.ok, q) } catch (e) { console.warn(e) } }
    ar.querySelectorAll('.gx-opt').forEach(b => { const j = +b.dataset.opt; b.classList.add(j === q.a ? 'ok' : j === k ? 'no' : 'dim') });
    const m = document.createElement('div'); m.className = 'rg-res ' + (v.ok ? 'ok' : 'no');
    m.textContent = v.ok ? `✓ صح! +${(v.pts || 0).toLocaleString()}${v.s > 1 ? ` · 🔥 ×${v.s}` : ''}` : `الإجابة الصحيحة: ${optLabel(v.k, kind)}`;
    el.querySelector('.rg-world').appendChild(m);
    setTimeout(() => { RACE.fb = false; drawRaceS() }, v.ok ? 1000 : 1700);
  };
  raceImg(i).then(src => {
    if (el.dataset.k !== key) return; if (src) img.src = src; if (i + 1 < n) raceImg(i + 1);
    ar.innerHTML = ''; RG.choose = choose; G.round(ar, s, q);
    const t0 = raceT0(i);
    RACE.tick = setInterval(() => { const left = 1 - (performance.now() - t0) / 1000 / lim; bar.style.transform = `scaleX(${Math.max(0, left)})`; if (left <= 0) choose(null) }, 100);
  });
}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', GAMES_CSS.strip() + '\n' + CSS.strip() + '\n.selbox{')
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    # 🎮 in the student's top bar
    s = rep(s, "  const top = `<div class=\"rtop\"><span class=\"pill2\">${Math.min(i + 1, n)} / ${n}</span><span class=\"grow\"></span>",
            "  const top = `<div class=\"rtop\"><span class=\"pill2\">${Math.min(i + 1, n)} / ${n}</span>${mine.go && i < n && sq.st !== 'end' ? `<button type=\"button\" class=\"pill2 rgsw\" data-rgsw title=\"غيّر اللعبة\">🎮 <span class=\"rgn\">${rgName(RG.gid)}</span></button>` : ''}<span class=\"grow\"></span>")
    s = rep(s, "  el.hidden = false;\n  if (RACE.fb) return;", "  el.hidden = false; el.onclick = e => { if (e.target.closest('[data-rgsw]')) rgSwitch(el) };\n  if (RACE.fb) return;")
    # the start screen: choose how to play
    s = rep(s, "    el.innerHTML = top + `<div class=\"center\"><h1>🏁 استعد!</h1><p>${n} أسئلة · جاوب بسرعة واجمع نقاط أكثر</p><button class=\"rbtn big\" id=\"rsGo\">ابدأ 🚀</button></div>`;",
            "    el.innerHTML = top + `<div class=\"center rgs\"><h1>🏁 استعد!</h1><p>${n} أسئلة · جاوب بسرعة واجمع نقاط أكثر</p><p><b>🎮 اختر طريقة اللعب</b></p>${rgCards()}<button class=\"rbtn big\" id=\"rsGo\">ابدأ 🚀</button></div>`;\n    rgBind(el);")
    # a question: the chosen game, or the usual buttons
    s = rep(s, "  const kind = (sq.kind || [])[i] || 'mc', lim = +((sq.lim || [])[i]) || 30;\n",
            "  const kind = (sq.kind || [])[i] || 'mc', lim = +((sq.lim || [])[i]) || 30;\n  if (RG.gid !== 'classic' && GMG[RG.gid]) return rgQuestion(el, top, i, kind, lim, key, n);\n")
    s = rep(s, "    btns.forEach(b => b.disabled = false); const t0 = performance.now();", "    btns.forEach(b => b.disabled = false); const t0 = raceT0(i);")
    # the room's mark goes to the game when a game is waiting for it
    s = rep(s, "if (r && r.at) { RACE.wait = null; raceFeedback(r); return }", "if (r && r.at) { RACE.wait = null; if (RACE.gw) { const f = RACE.gw; RACE.gw = null; f(r) } else raceFeedback(r); return }")
    return s
