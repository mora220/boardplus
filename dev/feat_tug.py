"""BoardPlus quiz modes, round two:
  * Tug of war (شد الحبل): the self-paced quiz played by two teams. Every correct answer is a pull for the team
    (a quick one pulls twice); the rope moves by each team's average pull, so team sizes do not matter. A team that
    pulls the knot over its line wins at once; otherwise the stronger team wins when everyone finishes or the
    teacher ends it. The teacher's screen is a full stadium scene for screen sharing.
  * Privacy on the shared screen of the self-paced quiz: only the top five places with their total points, no
    right / wrong counts per student.
  * More sound and cheering for students: crowd cheers, streak calls, kind words after a wrong answer, and a
    countdown in the last five seconds.
Data: sq.mode = 'race' | 'tug', sq.team = {sid: 'r' | 'b'}, sq.win = 'r' | 'b' | 'd' when a tug ends."""
import re

CSS = r"""
#qTug{background:linear-gradient(135deg,#e63946,#2f6fe0);border-color:transparent;color:#fff}
/* ---------- cheering ---------- */
.fx-say{position:absolute;left:50%;top:24%;translate:-50% 0;z-index:40;pointer-events:none;white-space:nowrap;font:900 clamp(28px,6vw,52px)/1.1 var(--f-display);color:#fff;
  text-shadow:0 4px 0 rgba(0,0,0,.25),0 0 24px rgba(255,255,255,.35);animation:fxSay 1.6s cubic-bezier(.2,1.4,.4,1) forwards}
.fx-say.hot{color:#ffd166}.fx-say.no{font-size:clamp(22px,4.6vw,36px);color:#fff}
@keyframes fxSay{0%{transform:scale(.3) rotate(-8deg);opacity:0}18%{transform:scale(1.12) rotate(2deg);opacity:1}30%{transform:scale(1) rotate(0)}80%{opacity:1}100%{transform:translateY(-40px) scale(.95);opacity:0}}
/* ---------- self-paced board: top five only ---------- */
.rlb5{display:flex;flex-direction:column;align-items:center;gap:10px;padding-top:6px}
.rstat{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.rstat span{background:rgba(255,255,255,.12);border-radius:99px;padding:8px 18px;font-weight:700;font-size:17px}
.r5h{margin:8px 0 2px;font-size:24px}
.r5{width:min(640px,94%);display:flex;align-items:center;gap:14px;padding:14px 20px;border-radius:18px;background:rgba(255,255,255,.12);font-size:22px;animation:rpop .35s ease-out both}
.r5 b{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.r5 .m{font-size:30px;width:44px;text-align:center}
.r5 .pts{font:900 24px var(--f-display);color:#ffd166}
.r5.p1{background:linear-gradient(90deg,rgba(242,176,30,.45),rgba(242,176,30,.15))}
.r5.p2{background:linear-gradient(90deg,rgba(207,216,227,.35),rgba(207,216,227,.1))}
.r5.p3{background:linear-gradient(90deg,rgba(208,139,76,.38),rgba(208,139,76,.12))}
.r5e{opacity:.75;font-size:19px}.r5n{opacity:.7;font-size:14px;margin-top:6px}
.race .podium.dn div{width:190px}
.race .podium.dn small{font-size:16px}
/* ---------- tug of war: the stadium (teacher) ---------- */
.race.tugon{background:#7cc6ff}
.tug{position:absolute;inset:0;direction:ltr;overflow:hidden;font-family:inherit;user-select:none}
.tug .tg-sky{position:absolute;inset:0 0 40% 0;background:linear-gradient(#5cb8ff,#bfe6ff)}
.tg-sun{position:absolute;top:7%;left:8%;width:90px;height:90px;border-radius:50%;background:radial-gradient(circle,#fff6c2,#ffd23f 60%,rgba(255,210,63,0) 72%);animation:tgSun 6s ease-in-out infinite}
@keyframes tgSun{50%{transform:scale(1.08)}}
.tg-cloud{position:absolute;height:34px;border-radius:40px;background:#fff;opacity:.9;animation:tgCloud linear infinite}
.tg-cloud::before,.tg-cloud::after{content:"";position:absolute;background:#fff;border-radius:50%}
.tg-cloud::before{width:46px;height:46px;top:-22px;left:18px}.tg-cloud::after{width:34px;height:34px;top:-14px;left:52px}
@keyframes tgCloud{from{transform:translateX(-160px)}to{transform:translateX(110vw)}}
.tg-crowd{position:absolute;left:0;right:0;top:33%;height:24%;background:linear-gradient(#5a3e8c,#3d2766)}
.tg-crowd svg{position:absolute;inset:0;width:100%;height:100%}
.tg-crowd .row{animation:tgBob 1.1s ease-in-out infinite}
.tg-crowd .row.r2{animation-delay:-.4s}.tg-crowd .row.r3{animation-delay:-.75s}
.tug.loud .tg-crowd .row{animation-duration:.45s}
@keyframes tgBob{50%{transform:translateY(-5px)}}
.tg-field{position:absolute;left:0;right:0;bottom:0;top:55%;background:repeating-linear-gradient(90deg,#48b04a 0 9%,#3fa142 9% 18%)}
.tg-field::before{content:"";position:absolute;inset:0;background:linear-gradient(rgba(0,0,0,.12),transparent 30%)}
.tg-mud{position:absolute;left:50%;top:58%;width:16%;height:30%;translate:-50% -50%;border-radius:50%;background:radial-gradient(ellipse,#5b3a1e,#7a4e2a 55%,#8d5b31 70%,rgba(141,91,49,0) 72%)}
.tg-mud i{position:absolute;width:10px;height:6px;border-radius:50%;background:#a36a3a;opacity:.8}
.tg-line{position:absolute;top:8%;bottom:6%;width:6px;translate:-50% 0;background:repeating-linear-gradient(#fff 0 14px,transparent 14px 24px);opacity:.85}
.tg-line b{position:absolute;top:-30px;left:50%;translate:-50% 0;white-space:nowrap;font-size:13px;font-weight:800;color:#fff;padding:3px 10px;border-radius:99px}
.tg-line.l b{background:#e63946}.tg-line.r b{background:#2f6fe0}
.tg-mid{position:absolute;left:50%;top:10%;bottom:8%;width:3px;translate:-50% 0;background:rgba(255,255,255,.55)}
.tg-move{position:absolute;inset:0;transition:transform 1.1s cubic-bezier(.3,1.5,.5,1)}
.tg-rope{position:absolute;left:3%;right:3%;top:44%;height:14px;border-radius:8px;translate:0 -50%;
  background:repeating-linear-gradient(115deg,#d9a35b 0 8px,#b9803c 8px 14px,#e8bd7b 14px 18px);box-shadow:0 3px 0 rgba(0,0,0,.18),inset 0 2px 0 rgba(255,255,255,.35)}
.tg-knot{position:absolute;left:50%;top:44%;translate:-50% -100%;display:flex;flex-direction:column;align-items:center}
.tg-knot .flag{width:16px;height:46px;background:linear-gradient(#ffd23f,#ff8f1f);clip-path:polygon(0 0,100% 12%,100% 88%,0 100%);animation:tgFlag .6s ease-in-out infinite alternate;transform-origin:50% 100%}
.tg-knot .knot{width:26px;height:26px;margin-top:-4px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#ffe08a,#c98a1e);box-shadow:0 0 0 4px rgba(255,255,255,.5),0 0 22px #ffd23f}
@keyframes tgFlag{from{transform:skewY(-6deg)}to{transform:skewY(6deg)}}
.tg-team{position:absolute;top:44%;display:flex;align-items:flex-end;translate:0 -56%}
.tg-team.r{right:54%;flex-direction:row}
.tg-team.b{left:54%;flex-direction:row-reverse}
.tg-team .tp{overflow:visible;width:clamp(56px,7.2vw,104px);height:auto;margin:0 -10px;filter:drop-shadow(0 6px 4px rgba(0,0,0,.25))}
.tg-team .tp .bd{transform-origin:40px 112px;animation:tgStrain .5s ease-in-out infinite alternate}
.tg-team .tp:nth-child(2n) .bd{animation-delay:-.25s}
.tg-team.b .tp{transform:scaleX(-1)}
@keyframes tgStrain{from{transform:rotate(-20deg)}to{transform:rotate(-27deg)}}
.tg-team.heave .tp .bd{animation:tgHeave .45s ease-out}
@keyframes tgHeave{30%{transform:rotate(-38deg) translateX(-6px)}100%{transform:rotate(-22deg)}}
.tg-team .more{align-self:center;margin:0 14px;background:rgba(0,0,0,.45);color:#fff;font-weight:800;border-radius:99px;padding:4px 12px;font-size:16px;direction:rtl}
.tg-team.fall .tp .bd{animation:tgFall 1.1s ease-in forwards}
@keyframes tgFall{40%{transform:rotate(25deg) translateX(30px)}100%{transform:rotate(78deg) translate(40px,10px)}}
.tg-team.fall .tp ellipse:first-child{display:none}
.tg-team.jump .tp{animation:tgJump .55s ease-in-out infinite alternate}
.tg-team.b.jump .tp{animation-name:tgJumpB}
@keyframes tgJump{to{transform:translateY(-26px)}}
@keyframes tgJumpB{from{transform:scaleX(-1)}to{transform:scaleX(-1) translateY(-26px)}}
.tg-dust{position:absolute;width:16px;height:16px;border-radius:50%;background:rgba(150,110,60,.55);pointer-events:none;animation:tgDust .9s ease-out forwards}
@keyframes tgDust{to{transform:translate(var(--dx),-30px) scale(2.4);opacity:0}}
.tg-pop{position:absolute;z-index:6;direction:rtl;white-space:nowrap;pointer-events:none;font:900 24px var(--f-display);color:#fff;padding:6px 14px;border-radius:99px;box-shadow:0 8px 18px rgba(0,0,0,.25);animation:tgPop 2.2s ease-out forwards}
.tg-pop.r{background:#e63946}.tg-pop.b{background:#2f6fe0}
@keyframes tgPop{0%{transform:translateY(20px) scale(.5);opacity:0}15%{transform:none;opacity:1}75%{opacity:1}100%{transform:translateY(-90px);opacity:0}}
.tg-ban{position:absolute;left:50%;top:40%;translate:-50% -50%;z-index:8;direction:rtl;white-space:nowrap;pointer-events:none;font:900 clamp(30px,5vw,64px)/1.1 var(--f-display);color:#fff;
  text-shadow:0 5px 0 rgba(0,0,0,.25);-webkit-text-stroke:2px rgba(0,0,0,.15);animation:fxSay 2.2s cubic-bezier(.2,1.4,.4,1) forwards}
.tg-hud{position:absolute;top:0;left:0;right:0;z-index:5;display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:start;padding:12px 14px;direction:ltr}
.tg-pan{direction:rtl;border-radius:18px;padding:10px 14px;color:#fff;box-shadow:0 10px 24px -10px rgba(0,0,0,.5);display:flex;flex-direction:column;gap:6px;max-width:340px}
.tg-pan.r{background:linear-gradient(135deg,#e63946,#9d1c26)}
.tg-pan.b{background:linear-gradient(135deg,#2f6fe0,#173f8f);justify-self:end}
.tg-pan h3{margin:0;font-size:22px;display:flex;gap:8px;align-items:center}
.tg-pan .okc{background:#fff;color:#137a3f;border-radius:99px;padding:2px 12px;font:900 20px var(--f-display);box-shadow:0 2px 0 rgba(0,0,0,.15)}
.tg-pan h3 small{margin-inline-start:auto;font-size:15px;opacity:.9}
.tg-pow{height:12px;border-radius:99px;background:rgba(255,255,255,.25);overflow:hidden}
.tg-pow i{display:block;height:100%;width:0;border-radius:99px;background:linear-gradient(90deg,#ffd166,#fff);transition:width .8s}
.tg-pan .st{display:flex;gap:12px;font-size:15px;font-weight:700;opacity:.95}
.tg-mid2{direction:rtl;text-align:center;color:#fff;display:flex;flex-direction:column;gap:6px;align-items:center}
.tg-mid2 .t{font:900 26px var(--f-display);text-shadow:0 3px 0 rgba(0,0,0,.2)}
.tg-mid2 .p{background:rgba(0,0,0,.35);border-radius:99px;padding:5px 14px;font-weight:700}
.tg-act{position:absolute;bottom:14px;left:50%;translate:-50% 0;z-index:7;display:flex;gap:10px;direction:rtl}
.tg-act .rbtn{box-shadow:0 8px 20px rgba(0,0,0,.25)}
.tg-win{position:absolute;inset:0;z-index:9;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;direction:rtl;color:#fff;
  background:radial-gradient(circle at 50% 40%,rgba(0,0,0,.25),rgba(0,0,0,.72));animation:rpop .5s ease-out}
.tg-win .cup{font-size:110px;line-height:1;animation:tgCup 1.2s ease-in-out infinite alternate;filter:drop-shadow(0 10px 20px rgba(255,210,63,.6))}
@keyframes tgCup{from{transform:rotate(-6deg) scale(1)}to{transform:rotate(6deg) scale(1.08)}}
.tg-win h1{margin:0;font:900 clamp(34px,5vw,62px)/1.1 var(--f-display);text-shadow:0 5px 0 rgba(0,0,0,.3)}
.tg-win h1.r{color:#ffb3b9}.tg-win h1.b{color:#b8d2ff}
.tg-win .sc{font:900 26px var(--f-display);opacity:.95}
.tg-win .t5{display:flex;flex-direction:column;gap:6px;width:min(520px,92vw)}
.tg-win .t5 div{display:flex;gap:10px;align-items:center;background:rgba(255,255,255,.14);border-radius:14px;padding:8px 14px;font-size:19px;font-weight:700}
.tg-win .t5 b{flex:1}.tg-win .t5 .pts{color:#ffd166;font-family:var(--f-display)}
.tg-win .t5 .dot{width:12px;height:12px;border-radius:50%}
/* ---------- tug of war: the student ---------- */
.race.tg-r{background:linear-gradient(160deg,#5c0f17,#b3202c 55%,#5c0f17)}
.race.tg-b{background:linear-gradient(160deg,#0d2457,#1f56c7 55%,#0d2457)}
.tgp.r{background:#e63946!important}.tgp.b{background:#2f6fe0!important}
.tgm{flex:1;min-width:70px;height:18px;position:relative;border-radius:99px;background:linear-gradient(90deg,#e63946 0 50%,#2f6fe0 50% 100%);box-shadow:inset 0 0 0 2px rgba(255,255,255,.35);direction:ltr}
.tgm b{position:absolute;top:50%;translate:-50% -50%;font-size:20px;transition:left .8s cubic-bezier(.3,1.5,.5,1);filter:drop-shadow(0 2px 2px rgba(0,0,0,.4))}
.tghi{display:flex;flex-direction:column;align-items:center;gap:6px}
.tghi .tm{font:900 clamp(30px,7vw,48px)/1.1 var(--f-display);padding:10px 28px;border-radius:22px;box-shadow:0 10px 30px rgba(0,0,0,.3)}
.tghi .tm.r{background:#e63946}.tghi .tm.b{background:#2f6fe0}.tghi .tm.x{background:rgba(255,255,255,.15);font-size:22px}
@media (max-width:560px){.tgp .rgn{display:none}.race.tg-r .rtop .pill2:last-child,.race.tg-b .rtop .pill2:last-child{display:none}}
.race .center .tgres{font:900 clamp(30px,7vw,46px)/1.15 var(--f-display);margin:0}
"""

JS = r"""
/* ======================= sound and cheering ======================= */
const FX = {
  noise(dur, f, q, vol, t0 = 0, rise = .15) {
    const a = audio(); if (!a) return; const n = Math.round(a.sampleRate * dur), b = a.createBuffer(1, n, a.sampleRate), d = b.getChannelData(0); for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    const s = a.createBufferSource(), bp = a.createBiquadFilter(), g = a.createGain(), t = a.currentTime + t0; s.buffer = b; bp.type = 'bandpass'; bp.frequency.value = f; bp.Q.value = q;
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + rise); g.gain.exponentialRampToValueAtTime(.0001, t + dur); s.connect(bp).connect(g).connect(a.destination); s.start(t); s.stop(t + dur + .05);
  },
  cheer(d = 1.3, v = .3) { this.noise(d, 1100, .6, v, 0, .25); this.noise(d * .85, 2300, 1.1, v * .5, .06, .3); for (let t = 0; t < d * .7; t += .07 + Math.random() * .06) this.noise(.05, 2600 + Math.random() * 1400, 3, v * .55, t, .005) },
  aww() { this.noise(.9, 480, 1.4, .14, 0, .25); SFX.tone(330, 0, .25, .09, 'triangle'); SFX.tone(262, .22, .5, .09, 'triangle') },
  heave() { SFX.tone(85, 0, .28, .32, 'sine'); SFX.tone(150, .02, .1, .1, 'square'); this.noise(.3, 650, 2, .14, 0, .04) },
  whistle(d = .55) {
    const a = audio(); if (!a) return; const o = a.createOscillator(), l = a.createOscillator(), lg = a.createGain(), g = a.createGain(), t = a.currentTime;
    o.frequency.value = 2850; l.frequency.value = 26; lg.gain.value = 160; l.connect(lg).connect(o.frequency);
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(.14, t + .03); g.gain.setValueAtTime(.14, t + d - .06); g.gain.exponentialRampToValueAtTime(.0001, t + d);
    o.connect(g).connect(a.destination); o.start(t); l.start(t); o.stop(t + d + .05); l.stop(t + d + .05);
  },
  drum(d = 1.4) { for (let t = 0; t < d; t += .055) SFX.tone(65 + Math.random() * 25, t, .08, .1 + (t / d) * .16, 'triangle') },
  fanfare() { [[523, 0, .14], [659, .13, .14], [784, .26, .14], [1047, .39, .3], [784, .66, .12], [1047, .78, .6]].forEach(([f, t, d]) => SFX.tone(f, t, d, .15, 'square')) },
  streak(n) { [0, 1, 2, 3].slice(0, Math.min(4, n - 1)).forEach(i => SFX.tone(660 * Math.pow(1.26, i), i * .07, .14, .12, 'square')) },
  last: -1,
  count(rem) { const s = Math.ceil(rem); if (s !== this.last) { this.last = s; if (s >= 1 && s <= 5) SFX.tick(s <= 3) } },
  OK: ['ممتاز! 🌟', 'بطل! 💪', 'رائع يا نجم! ⭐', 'عبقري! 🧠', 'أحسنت! 👏', 'كده الشغل! 🔥', 'ما شاء الله! 🌟', 'إجابة ذهبية! 🥇'],
  NO: ['ولا يهمك، اللي جاي ليك 💪', 'قرّبت! ركّز في اللي جاي 🎯', 'حاول تاني، أنت قدها 🌱', 'عادي، الأبطال بيتعلموا 💡'],
  say(host, text, cls) { if (!host) return; const b = document.createElement('div'); b.className = 'fx-say ' + (cls || ''); b.textContent = text; host.appendChild(b); setTimeout(() => b.remove(), 1650) },
  react(v, host) {
    const tug = RACE.sq && RACE.sq.mode === 'tug';
    if (v.ok) {
      const s = v.s || 1; this.cheer(s >= 3 ? 1.7 : 1.1, s >= 3 ? .36 : .26); if (s >= 2) this.streak(s); if (s >= 4) setTimeout(() => this.fanfare(), 250); if (tug) this.heave();
      this.say(host, tug && s < 3 ? pick(['💪 شدّة قوية لفريقك!', '🪢 شُدّ! فريقك يتقدّم', ...this.OK]) : s >= 5 ? `⚡ لا أحد يوقفك! ×${s}` : s >= 3 ? `🔥 سلسلة نارية ×${s}` : pick(this.OK), s >= 3 ? 'hot' : 'ok');
    } else { this.aww(); this.say(host, v.c ? pick(this.NO) : '⏰ الوقت خلص… اللي جاي أسرع 💨', 'no') }
  }
};

/* ======================= self-paced board on a shared screen: top five only ======================= */
function racePodium(tot, names) {
  const dl = denseRank(tot.filter(x => x.pts > 0).map(x => ({ ...x, t: x.pts }))), g = [1, 2, 3].map(p => dl.filter(x => x.pl === p));
  return `<div class="podium dn">${[1, 0, 2].filter(i => g[i].length).map(i => `<div class="p${i + 1}"><span>${medal(i)}</span>${g[i].map(x => esc(names(x.sid))).join('، ')}<small>${g[i][0].pts.toLocaleString()}</small></div>`).join('')}</div>`;
}
function raceTop5(tot, names) {
  const t5 = denseRank(tot.filter(x => x.pts > 0).map(x => ({ ...x, t: x.pts }))).filter(x => x.pl <= 5);
  return `<h3 class="r5h">🏆 الخمسة الأوائل</h3>${t5.length ? t5.map((x, j) => `<div class="r5 p${x.pl}" style="animation-delay:${j * .05}s"><span class="m">${medal(x.pl - 1)}</span><b>${esc(names(x.sid))}</b><span class="pts">${x.pts.toLocaleString()}</span></div>`).join('') : '<p class="r5e">لم يجب أحد بعد…</p>'}
    <p class="r5n">🔒 يظهر الخمسة الأوائل فقط · كل طالب يرى ترتيبه ونقاطه على جهازه</p>`;
}

/* ======================= tug of war ======================= */
const TEAMS = { r: { n: 'الفريق الأحمر', e: '🔴', c: '#e63946' }, b: { n: 'الفريق الأزرق', e: '🔵', c: '#2f6fe0' } };
const TUG = { id: null, seen: null, lead: 0, near: 0, ending: false, asg: new Set(), last: 0 };
function tugSplit() {
  const ids = [...T.st.keys()].filter(sid => { const s = T.st.get(sid); return s && s.info && s.info.name }).sort(() => Math.random() - .5), team = {};
  ids.forEach((sid, i) => team[sid] = i % 2 ? 'b' : 'r'); return team;
}
function tugState(sq, a) {
  const team = sq.team || {}, n = sq.n || 0, S2 = { r: { sz: 0, p: 0, ok: 0, fin: 0 }, b: { sz: 0, p: 0, ok: 0, fin: 0 } };
  for (const [sid, t] of Object.entries(team)) {
    const x = S2[t]; if (!x) continue; x.sz++; let k = 0;
    for (const [j, v] of Object.entries((a || {})[sid] || {})) if (/^\d+$/.test(j) && v) { k++; if (v.ok) { x.ok++; x.p += v.p || 1 } }
    if (k >= n) x.fin++;
  }
  const pw = t => S2[t].sz ? S2[t].p / S2[t].sz : 0, diff = pw('b') - pw('r'), W = Math.max(3, n * .9);
  return { S: S2, diff, W, off: Math.max(-1, Math.min(1, diff / W)), pr: pw('r'), pb: pw('b'), all: S2.r.sz + S2.b.sz > 0 && S2.r.fin === S2.r.sz && S2.b.fin === S2.b.sz };
}
function tgPerson(c, i) {
  const skin = ['#f2c9a0', '#d9a77a', '#b97d4f', '#f6d5b5', '#8d5a37'][i % 5], hair = ['#2b1a10', '#4a2c17', '#111', '#6b3e1e', '#2b1a10'][i % 5];
  return `<svg class="tp" viewBox="0 0 80 120"><ellipse cx="40" cy="116" rx="26" ry="4" fill="rgba(0,0,0,.18)"/><g class="bd">
    <path d="M40 76 L60 112 M40 76 L26 114" stroke="#26324a" stroke-width="10" stroke-linecap="round" fill="none"/>
    <ellipse cx="62" cy="114" rx="8" ry="4" fill="#111"/><ellipse cx="25" cy="115" rx="8" ry="4" fill="#111"/>
    <rect x="28" y="38" width="24" height="42" rx="10" fill="${c}"/><text x="40" y="66" font-size="15" font-weight="900" fill="#fff" text-anchor="middle" font-family="sans-serif">${i + 1}</text>
    <path d="M47 48 L78 64 M44 54 L78 70" stroke="${skin}" stroke-width="7" stroke-linecap="round"/>
    <circle cx="40" cy="25" r="13" fill="${skin}"/><path d="M27 23 Q30 9 42 11 Q53 12 53 22 Q46 16 34 19 Z" fill="${hair}"/>
    <rect x="27" y="19" width="26" height="5" rx="2" fill="${c}" opacity=".9"/><circle cx="47" cy="27" r="2" fill="#222"/><path d="M45 34 L51 33" stroke="#7a2d1b" stroke-width="2" stroke-linecap="round"/></g></svg>`;
}
function tgCrowd() {
  const cols = ['#e63946', '#2f6fe0', '#ffd166', '#f1faee', '#ff8fab', '#8ecae6', '#e63946', '#2f6fe0'], rows = [[18, 26], [36, 22], [56, 18]];
  return `<svg viewBox="0 0 1000 100" preserveAspectRatio="none">${rows.map(([y, sp], r) => `<g class="row r${r + 1}">${Array.from({ length: Math.ceil(1000 / sp) + 1 }, (_, i) => { const x = i * sp + (r % 2) * sp / 2, c = cols[(i * 7 + r * 3) % cols.length]; return `<rect x="${x - 7}" y="${y + 9}" width="14" height="40" rx="6" fill="${c}"/><circle cx="${x}" cy="${y + 4}" r="6" fill="#f2c9a0"/>` }).join('')}</g>`).join('')}</svg>`;
}
function tugBuild(el, sq) {
  el.classList.add('tugon'); el.dataset.tug = sq.id; TUG.id = sq.id; TUG.seen = null; TUG.lead = 0; TUG.near = 0; TUG.ending = false; TUG.asg.clear(); TUG.last = 0;
  el.innerHTML = `<div class="tug" id="tugS">
    <div class="tg-sky"><div class="tg-sun"></div><div class="tg-cloud" style="top:12%;width:110px;animation-duration:48s"></div><div class="tg-cloud" style="top:22%;width:80px;animation-duration:66s;animation-delay:-30s"></div><div class="tg-cloud" style="top:6%;width:96px;animation-duration:58s;animation-delay:-12s"></div></div>
    <div class="tg-crowd">${tgCrowd()}</div>
    <div class="tg-field"><div class="tg-mud">${Array.from({ length: 7 }, (_, i) => `<i style="left:${15 + i * 11}%;top:${30 + (i % 3) * 18}%"></i>`).join('')}</div><div class="tg-mid"></div>
      <div class="tg-line l" id="tgLl"><b>🏁 خط فوز الأحمر</b></div><div class="tg-line r" id="tgLr"><b>🏁 خط فوز الأزرق</b></div>
      <div class="tg-move" id="tgMove"><div class="tg-rope"></div><div class="tg-team r" id="tgR"></div><div class="tg-team b" id="tgB"></div><div class="tg-knot"><div class="flag"></div><div class="knot"></div></div></div></div>
    <div class="tg-hud"><div class="tg-pan r" id="tgPr"></div><div class="tg-mid2" id="tgMid"></div><div class="tg-pan b" id="tgPb"></div></div>
    <div class="tg-act" id="tgAct"></div><div id="tgFx"></div></div>`;
  FX.whistle(.7); setTimeout(() => tugBanner('🪢 ابدأوا الشد!'), 200); FX.cheer(1.6, .3);
}
function tugBanner(t) { const fx = $('#tgFx'); if (!fx) return; fx.querySelectorAll('.tg-ban').forEach(x => x.remove()); const b = document.createElement('div'); b.className = 'tg-ban'; b.textContent = t; fx.appendChild(b); setTimeout(() => b.remove(), 2300) }
function tugPull(t, name, p) {
  const tm = $(t === 'r' ? '#tgR' : '#tgB'), fx = $('#tgFx'), sc = $('#tugS'); if (!tm || !fx) return;
  tm.classList.remove('heave'); void tm.offsetWidth; tm.classList.add('heave');
  const r = tm.getBoundingClientRect(), S0 = sc.getBoundingClientRect();
  for (let i = 0; i < 6; i++) { const d = document.createElement('i'); d.className = 'tg-dust'; d.style.left = (r.left - S0.left + Math.random() * r.width) + 'px'; d.style.top = (r.bottom - S0.top - 10) + 'px'; d.style.setProperty('--dx', (t === 'r' ? -1 : 1) * (10 + Math.random() * 30) + 'px'); fx.appendChild(d); setTimeout(() => d.remove(), 950) }
  const pp = document.createElement('div'); pp.className = 'tg-pop ' + t; pp.textContent = `${p > 1 ? '⚡ +2' : '💪 +1'} ${name}`;
  pp.style.left = (r.left - S0.left + r.width * (.2 + Math.random() * .5)) + 'px'; pp.style.top = (r.top - S0.top - 40 - Math.random() * 40) + 'px'; fx.appendChild(pp); setTimeout(() => pp.remove(), 2300);
  const now = Date.now(); if (now - TUG.last > 260) { TUG.last = now; FX.heave(); FX.cheer(.9, .18) }
  sc.classList.add('loud'); clearTimeout(TUG.lt); TUG.lt = setTimeout(() => sc.classList.remove('loud'), 1400);
}
async function tugFinish(win, auto) {
  const sq = RACE.sq; if (!sq || sq.st !== 'run' || TUG.ending) return;
  if (!auto && !(await ask('إنهاء شد الحبل؟', 'يفوز الفريق المتقدم الآن، وتُضاف نقاط كل طالب إلى لوحة الصدارة.', 'إنهاء'))) return;
  if (RACE.sq !== sq || sq.st !== 'run') return; TUG.ending = true;
  const b = `sessions/${T.code}`, up = {};
  for (const [sid, m] of Object.entries(RACE.a || {})) { let p = 0; for (const [k, v] of Object.entries(m || {})) if (/^\d+$/.test(k) && v) p += v.p || 0; if (p) up[`${sid}/${sq.id}`] = p }
  if (Object.keys(up).length) await DB.update(b + '/qpts', up);
  if (!win) { const st = tugState(sq, RACE.a); win = Math.abs(st.diff) < 1e-9 ? 'd' : st.diff > 0 ? 'b' : 'r' }
  await DB.update(b + '/sq', { st: 'end', win });
}
function drawTugT(el) {
  const sq = RACE.sq; if (el.dataset.tug !== sq.id || !el.querySelector('#tugS')) tugBuild(el, sq);
  const st = tugState(sq, RACE.a), team = sq.team || {}, end = sq.st === 'end', names = sid => { const s = T.st.get(sid); return s ? s.info.name : '—' };
  // students who joined after the start join the smaller team
  if (!end) { const cnt = { r: st.S.r.sz, b: st.S.b.sz }; for (const sid of T.st.keys()) { const s = T.st.get(sid); if (!team[sid] && s && s.info && s.info.name && !TUG.asg.has(sid)) { const t = cnt.r <= cnt.b ? 'r' : 'b'; cnt[t]++; TUG.asg.add(sid); DB.set(`sessions/${T.code}/sq/team/${sid}`, t) } } }
  // pulls since the last update
  const seen = TUG.seen; TUG.seen = new Set();
  for (const [sid, m] of Object.entries(RACE.a || {})) for (const [j, v] of Object.entries(m || {})) if (/^\d+$/.test(j) && v) { const k = sid + ':' + j; TUG.seen.add(k); if (seen && !seen.has(k) && v.ok && team[sid] && !end) tugPull(team[sid], names(sid), v.p || 1) }
  // the rope
  const maxS = 26, off = end && sq.win && sq.win !== 'd' ? (sq.win === 'b' ? 1 : -1) * 1.15 : st.off;
  $('#tgMove').style.transform = `translateX(${off * maxS}%)`;
  $('#tgLl').style.left = (50 - maxS) + '%'; $('#tgLr').style.left = (50 + maxS) + '%';
  const people = (t, sz) => { const k = Math.min(Math.max(sz, 1), 5); return Array.from({ length: k }, (_, i) => tgPerson(TEAMS[t].c, i)).join('') + (sz > 5 ? `<span class="more">+${sz - 5}</span>` : '') };
  ['r', 'b'].forEach(t => {
    const tm = $(t === 'r' ? '#tgR' : '#tgB'), sz = st.S[t].sz; if (tm.dataset.sz !== String(Math.min(Math.max(sz, 1), 5)) + '/' + sz) { tm.dataset.sz = String(Math.min(Math.max(sz, 1), 5)) + '/' + sz; tm.innerHTML = people(t, sz) }
    tm.classList.toggle('fall', end && sq.win && sq.win !== 'd' && sq.win !== t); tm.classList.toggle('jump', end && sq.win === t);
    const p = $(t === 'r' ? '#tgPr' : '#tgPb'), pw = t === 'r' ? st.pr : st.pb, X = st.S[t];
    p.innerHTML = `<h3>${TEAMS[t].e} ${TEAMS[t].n}<span class="okc" title="عدد الإجابات الصحيحة للفريق">✓ ${X.ok}</span><small>👥 ${X.sz}</small></h3><div class="tg-pow"><i style="width:${Math.min(100, pw / Math.max(st.W, 1) * 100)}%"></i></div>
      <div class="st"><span>💪 قوة الشد ${pw.toFixed(1)}</span><span>🏁 ${X.fin}/${X.sz}</span></div>`;
  });
  $('#tgMid').innerHTML = `<div class="t">🪢 شد الحبل</div><div class="p">${esc(sq.title || '')} · ${sq.n} أسئلة</div>`;
  $('#tgAct').innerHTML = end ? '' : '<button class="rbtn red" id="rcEnd">⏹ إنهاء</button><button class="rbtn" id="rcHide">إغلاق مؤقت</button>';
  const c = el.querySelector('#rcEnd'); if (c) c.onclick = () => tugFinish(null, false);
  const h = el.querySelector('#rcHide'); if (h) h.onclick = () => { RACE.open = false; el.hidden = true; drawRaceFab() };
  const x = el.querySelector('#rcClose'); if (x) x.onclick = closeRace;
  if (!end) {
    // commentary
    const lead = Math.abs(st.diff) < 1e-9 ? 0 : st.diff > 0 ? 1 : -1;
    if (seen && lead !== TUG.lead && lead) tugBanner(lead > 0 ? '🔵 الأزرق يتقدّم!' : '🔴 الأحمر يتقدّم!');
    TUG.lead = lead;
    const near = Math.abs(st.off) >= .7 ? (st.off > 0 ? 1 : -1) : 0;
    if (near && near !== TUG.near) { tugBanner(near > 0 ? '🔥 الأزرق قرّب يكسب!' : '🔥 الأحمر قرّب يكسب!'); FX.drum(1.4) }
    TUG.near = near;
    if (Math.abs(st.diff) >= st.W) tugFinish(st.diff > 0 ? 'b' : 'r', true);
    else if (st.all) setTimeout(() => { if (RACE.sq === sq && tugState(sq, RACE.a).all) tugFinish(null, true) }, 1500);
    const w0 = el.querySelector('.tg-win'); if (w0) w0.remove();
  } else if (!el.querySelector('.tg-win')) {
    const tot = raceTotals(RACE.a), t5 = denseRank(tot.filter(x => x.pts > 0).map(x => ({ ...x, t: x.pts }))).filter(x => x.pl <= 5), w = sq.win;
    const ov = document.createElement('div'); ov.className = 'tg-win';
    ov.innerHTML = `<div class="cup">${w === 'd' ? '🤝' : '🏆'}</div><h1 class="${w}">${w === 'd' ? 'تعادل! الفريقان أبطال' : `فاز ${TEAMS[w].n}! ${TEAMS[w].e}`}</h1>
      <div class="sc">💪 ${st.pr.toFixed(1)} 🔴 · 🔵 ${st.pb.toFixed(1)}</div>
      ${t5.length ? `<div class="t5">${t5.map(x => `<div><span>${medal(x.pl - 1)}</span><i class="dot" style="background:${(TEAMS[team[x.sid]] || {}).c || '#999'}"></i><b>${esc(names(x.sid))}</b><span class="pts">${x.pts.toLocaleString()}</span></div>`).join('')}</div>` : ''}
      <button class="rbtn" id="tgOk">إغلاق</button>`;
    el.querySelector('#tugS').appendChild(ov); ov.querySelector('#tgOk').onclick = closeRace;
    FX.whistle(.9); setTimeout(() => { FX.fanfare(); FX.cheer(2.6, .38); SFX.applause(); confetti() }, 600); setTimeout(confetti, 1500);
  }
}
/* the student */
function tugTop(sq) {
  const tm = (sq.team || {})[S.sid], st = tugState(sq, RACE.a);
  return `<span class="pill2 tgp ${tm || ''}">${tm ? TEAMS[tm].e + ' <span class="rgn">' + TEAMS[tm].n + '</span>' : '⏳'}</span><span class="tgm" title="الحبل"><b style="left:${50 + st.off * 42}%">🪢</b></span>`;
}
function tugHello(sq) {
  const tm = (sq.team || {})[S.sid];
  return `<div class="tghi"><h1>🪢 شد الحبل!</h1>${tm ? `<div class="tm ${tm}">أنت في ${TEAMS[tm].n} ${TEAMS[tm].e}</div><p>كل إجابة صحيحة = شدّة لفريقك 💪 والسريعة = شدّتين ⚡</p>` : '<div class="tm x">⏳ المعلم يوزّعك على فريق…</div>'}</div>`;
}
function tugResult(sq) {
  const tm = (sq.team || {})[S.sid], w = sq.win; if (!w) return '';
  if (w === 'd') return '<p class="tgres">🤝 تعادل! الفريقان أبطال</p>';
  if (tm === w) { setTimeout(() => { confetti(); FX.fanfare(); FX.cheer(2, .32) }, 200); return `<p class="tgres">🏆 فاز فريقك! ${TEAMS[w].e}</p>` }
  return `<p class="tgres">💪 فاز ${TEAMS[w].n} هالمرة</p><p>المرة الجاية فريقك يشدّ أقوى!</p>`;
}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    # the quiz builder: three ways to play
    s = rep(s, '    <button class="btn" id="qRace" title="كويز السباق: كل طالب يحل الأسئلة بسرعته">🏁 <span>كل طالب بسرعته</span></button>\n',
            '    <button class="btn" id="qRace" title="كويز السباق: كل طالب يحل الأسئلة بسرعته">🏁 <span>كل طالب بسرعته</span></button>\n'
            '    <button class="btn" id="qTug" title="شد الحبل: فريقان، وكل إجابة صحيحة تشد الحبل لفريقك">🪢 <span>شد الحبل</span></button>\n')
    s = rep(s, "  $('#qRace').onclick = () => startRace();", "  $('#qRace').onclick = () => startRace();\n  $('#qTug').onclick = () => startRace(null, 'tug');")
    s = rep(s, "async function startRace(only) {", "async function startRace(only, mode) {")
    s = rep(s, "title: setName(curSet()) });\n  closeBuilder(); RACE.open = true; drawRaceT();",
            "title: setName(curSet()), mode: mode || 'race', team: mode === 'tug' ? tugSplit() : null });\n  closeBuilder(); RACE.open = true; drawRaceT();")
    # the teacher's board: tug scene, or the top five
    m = re.findall(r"  el\.hidden = false; const tot = raceTotals\(RACE\.a\).*?\n(?=  const c = el\.querySelector\('#rcEnd'\))", s, re.S)
    assert len(m) == 1, len(m)
    s = s.replace(m[0], r"""  el.hidden = false;
  if (sq.mode === 'tug') return drawTugT(el);
  el.classList.remove('tugon'); el.dataset.tug = '';
  const tot = raceTotals(RACE.a), n = sq.n || 0, names = sid => { const s = T.st.get(sid); return s ? s.info.name : '—' };
  const all = [...T.st.keys()], seen = new Set(tot.map(x => x.sid)); all.forEach(sid => { if (!seen.has(sid)) tot.push({ sid, pts: 0, ok: 0, n: 0, t: 0, go: false }) });
  const fin = tot.filter(x => x.n >= n).length, go = tot.filter(x => x.go).length, end = sq.st === 'end';
  el.innerHTML = `<div class="rtop"><b>🏁 ${esc(sq.title || '')} · كل طالب بسرعته</b><span class="grow"></span>
      ${end ? '<button class="rbtn" id="rcClose">إغلاق</button>' : '<button class="rbtn red" id="rcEnd">⏹ إنهاء الكويز</button><button class="rbtn" id="rcHide">إغلاق</button>'}</div>
    ${end ? racePodium(tot, names) : ''}
    <div class="lb rlb5"><div class="rstat"><span>👥 بدأ ${go} من ${tot.length}</span><span>🏁 أنهى ${fin}</span></div>${raceTop5(tot, names)}</div>`;
""")
    # end of the tug when a team pulls too far is decided by the teacher's device; the race end keeps its own button
    # the student: team, rope meter, start and result
    s = rep(s, "<span class=\"grow\"></span>${my.pts ?", "${sq.mode === 'tug' ? tugTop(sq) : '<span class=\"grow\"></span>'}${my.pts ?")
    s = rep(s, "  el.hidden = false; el.onclick = e => {", "  el.hidden = false; { const tm = sq.mode === 'tug' ? (sq.team || {})[S.sid] : ''; el.classList.toggle('tg-r', tm === 'r'); el.classList.toggle('tg-b', tm === 'b') } el.onclick = e => {")
    s = rep(s, "<h1>🏁 استعد!</h1><p>${n} أسئلة · جاوب بسرعة واجمع نقاط أكثر</p>", "${sq.mode === 'tug' ? tugHello(sq) : `<h1>🏁 استعد!</h1><p>${n} أسئلة · جاوب بسرعة واجمع نقاط أكثر</p>`}")
    s = rep(s, "    el.innerHTML = top + `<div class=\"center\">${key === 'end' ?", "    el.innerHTML = top + `<div class=\"center\">${sq.mode === 'tug' && key === 'end' ? tugResult(sq) : ''}${key === 'end' ?")
    s = rep(s, "    if (key === 'end' && me >= 0 && me < 3) { confetti(); SFX.applause() }", "    if (key === 'end' && me >= 0 && me < 3 && sq.mode !== 'tug') { confetti(); SFX.applause() }")
    # the team's lead changes while a student waits on the done screen: keep the rope meter live
    # cheering: usual buttons
    s = rep(s, "  v.ok ? SFX.chime() : SFX.tone(220, 0, .35, .18, 'sawtooth');\n  el.appendChild(d); RACE.fb = true;",
            "  v.ok ? SFX.chime() : SFX.tone(220, 0, .35, .18, 'sawtooth');\n  el.appendChild(d); RACE.fb = true; FX.react(v, el);")
    s = rep(s, "    btns.forEach(b => b.disabled = false); const t0 = raceT0(i);\n    RACE.tick = setInterval(() => { const left = 1 - (performance.now() - t0) / 1000 / lim; bar.style.transform = `scaleX(${Math.max(0, left)})`; if (left <= 0) send('') }, 100);",
            "    btns.forEach(b => b.disabled = false); const t0 = raceT0(i); FX.last = -1; gmSnd('whoosh');\n    RACE.tick = setInterval(() => { const left = 1 - (performance.now() - t0) / 1000 / lim; bar.style.transform = `scaleX(${Math.max(0, left)})`; FX.count(left * lim); if (left <= 0) send('') }, 100);")
    # cheering: games
    s = rep(s, "    el.querySelector('.rg-world').appendChild(m);\n", "    el.querySelector('.rg-world').appendChild(m); FX.react(v, el.querySelector('.rg-world'));\n")
    s = rep(s, "    const t0 = raceT0(i);\n    RACE.tick = setInterval(() => { const left = 1 - (performance.now() - t0) / 1000 / lim; bar.style.transform = `scaleX(${Math.max(0, left)})`; if (left <= 0) choose(null) }, 100);",
            "    const t0 = raceT0(i); FX.last = -1; gmSnd('whoosh');\n    RACE.tick = setInterval(() => { const left = 1 - (performance.now() - t0) / 1000 / lim; bar.style.transform = `scaleX(${Math.max(0, left)})`; FX.count(left * lim); if (left <= 0) choose(null) }, 100);")
    s = rep(s, "    setTimeout(() => { RACE.fb = false; drawRaceS() }, v.ok ? 1000 : 1700);", "    setTimeout(() => { RACE.fb = false; drawRaceS() }, v.ok ? 1500 : 1900);")
    return s
