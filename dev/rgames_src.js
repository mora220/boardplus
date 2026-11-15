/* ---- sound ---- */
const GSND = { ok: [[660, .1], [990, .2]], no: [[196, .28, "square", .06]], tap: [[520, .05, "triangle", .07]], boost: [[300, .07, "sawtooth", .05], [500, .07, "sawtooth", .05], [800, .07, "sawtooth", .05], [1200, .18, "sawtooth", .05]], win: [[523, .14], [659, .14], [784, .14], [1047, .4]], lose: [[392, .2], [330, .2], [262, .45]], hit: [[110, .2, "square", .09]], coin: [[988, .07], [1319, .22]], whoosh: [[900, .12, "triangle", .05], [500, .12, "triangle", .05]], kick: [[170, .09, "square", .1], [90, .12, "sine", .12]], pop: [[1000, .04, "square", .08], [320, .09, "square", .06]], splash: [[520, .08, "triangle", .07], [260, .22, "triangle", .07]] };
function gmSnd(k) {
  if (GM.mute) return;
  try {
    const C = GM.ac || (GM.ac = new (window.AudioContext || window.webkitAudioContext)()); if (C.state === "suspended") C.resume();
    let t0 = C.currentTime + .01;
    for (const [f, d, ty = "sine", v = .14] of GSND[k] || []) { const o = C.createOscillator(), g = C.createGain(); o.type = ty; o.frequency.value = f; g.gain.setValueAtTime(v, t0); g.gain.exponentialRampToValueAtTime(.0008, t0 + d); o.connect(g); g.connect(C.destination); o.start(t0); o.stop(t0 + d + .02); t0 += d * .85; }
  } catch (e) { }
}

/* ---- art ---- */
const gmRocket = (c1, c2) => `<svg viewBox="0 0 64 32" aria-hidden="true"><g class="fl"><path d="M15 10 Q-2 16 15 22 Q7 16 15 10Z" fill="#ffb02e"/><path d="M15 12.5 Q5 16 15 19.5Z" fill="#fff4b8"/></g><path d="M18 9 L9 2 H21 L29 9Z M18 23 L9 30 H21 L29 23Z" fill="${c2}"/><path d="M14 9 H44 Q58 11 63 16 Q58 21 44 23 H14 Q11 16 14 9Z" fill="${c1}"/><path d="M14 9 H44 Q58 11 63 16 H14 Q12 12 14 9Z" fill="rgba(255,255,255,.22)"/><circle cx="45" cy="16" r="4.6" fill="#bfe9ff" stroke="#fff" stroke-width="1.6"/></svg>`;
const gmBalloon = c => `<svg class="bl-b" viewBox="0 0 60 80" aria-hidden="true"><path d="M30 2C11 2 3 19 7 34c4 14 16 22 23 24 7-2 19-10 23-24C57 19 49 2 30 2Z" fill="${c}"/><ellipse cx="20" cy="20" rx="6" ry="10" fill="#fff" opacity=".4" transform="rotate(-20 20 20)"/><path d="M26 58h8l-4 7Z" fill="${c}"/><path d="M30 65q-5 7 0 15" stroke="#64748b" stroke-width="1.6" fill="none"/></svg>`;
const gmKeeper = `<svg viewBox="0 0 64 74" aria-hidden="true"><path d="M20 30 L6 8" stroke="#facc15" stroke-width="9" stroke-linecap="round"/><path d="M44 30 L58 8" stroke="#facc15" stroke-width="9" stroke-linecap="round"/><circle cx="6" cy="7" r="7" fill="#f97316" stroke="#fff" stroke-width="2"/><circle cx="58" cy="7" r="7" fill="#f97316" stroke="#fff" stroke-width="2"/><rect x="18" y="26" width="28" height="28" rx="9" fill="#facc15"/><path d="M24 54 L22 70 M40 54 L42 70" stroke="#1e293b" stroke-width="8" stroke-linecap="round"/><circle cx="32" cy="16" r="11" fill="#fcd9b6"/><path d="M21 14 Q32 0 43 14 Q32 8 21 14Z" fill="#1e293b"/><circle cx="28" cy="17" r="1.6" fill="#1e293b"/><circle cx="36" cy="17" r="1.6" fill="#1e293b"/><path d="M28 21.5 Q32 24 36 21.5" stroke="#1e293b" stroke-width="1.5" fill="none" stroke-linecap="round"/><text x="32" y="46" font-size="13" font-weight="900" text-anchor="middle" fill="#1e293b">1</text></svg>`;
const gmBow = `<svg viewBox="0 0 74 74" aria-hidden="true"><path d="M10 44 Q37 6 64 44" fill="none" stroke="#92400e" stroke-width="6" stroke-linecap="round"/><path d="M10 44 L37 52 L64 44" fill="none" stroke="#e2e8f0" stroke-width="2"/><path d="M37 60 V10" stroke="#78350f" stroke-width="4" stroke-linecap="round"/><path d="M37 2 L30 14 H44Z" fill="#475569"/><path d="M37 60 l-6 8 M37 60 l6 8" stroke="#dc2626" stroke-width="3" stroke-linecap="round"/></svg>`;
const gmIn = s => s.replace(/<\/?svg[^>]*>/g, "");
const GM_GAMES = [
  { id: "penalty", c1: "#16a34a", c2: "#14532d", art: `<svg viewBox="0 0 300 128" preserveAspectRatio="xMidYMid slice"><rect width="300" height="128" fill="#0369a1"/><rect y="70" width="300" height="58" fill="#16a34a"/><rect x="60" y="14" width="180" height="78" fill="rgba(255,255,255,.14)" stroke="#fff" stroke-width="6"/><path d="M150 17 V90 M63 53 H237" stroke="#fff" stroke-width="2" opacity=".7"/><g font-size="20" font-weight="900" fill="#fff" text-anchor="middle"><text x="105" y="42">أ</text><text x="195" y="42">ب</text><text x="105" y="80">ج</text><text x="195" y="80">د</text></g><g transform="translate(118 44) scale(.9)">${gmIn(gmKeeper)}</g><text x="216" y="120" font-size="30" text-anchor="middle">⚽</text></svg>` },
  { id: "river", c1: "#0891b2", c2: "#164e63", art: `<svg viewBox="0 0 300 128" preserveAspectRatio="xMidYMid slice"><rect width="300" height="128" fill="#0891b2"/><rect width="300" height="20" fill="#65a30d"/><rect y="108" width="300" height="20" fill="#65a30d"/><g fill="#a3e635" stroke="#3f6212" stroke-width="3"><ellipse cx="60" cy="62" rx="36" ry="22"/><ellipse cx="150" cy="70" rx="36" ry="22"/><ellipse cx="240" cy="58" rx="36" ry="22"/></g><g font-size="20" font-weight="900" fill="#14532d" text-anchor="middle"><text x="60" y="69">أ</text><text x="240" y="65">ج</text></g><text x="150" y="80" font-size="34" text-anchor="middle">🐸</text><text x="262" y="110" font-size="30" text-anchor="middle">🐊</text></svg>` },
  { id: "balloons", c1: "#0ea5e9", c2: "#075985", art: `<svg viewBox="0 0 300 128" preserveAspectRatio="xMidYMid slice"><rect width="300" height="128" fill="#7dd3fc"/><ellipse cx="60" cy="24" rx="36" ry="10" fill="#fff" opacity=".8"/><g transform="translate(40 14) scale(.95)">${gmIn(gmBalloon("#ef4444"))}</g><g transform="translate(110 30) scale(.95)">${gmIn(gmBalloon("#f59e0b"))}</g><g transform="translate(180 8) scale(.95)">${gmIn(gmBalloon("#22c55e"))}</g><g transform="translate(240 34) scale(.95)">${gmIn(gmBalloon("#8b5cf6"))}</g><g font-size="18" font-weight="900" fill="#fff" text-anchor="middle"><text x="68" y="48">أ</text><text x="138" y="64">ب</text><text x="208" y="42">ج</text><text x="268" y="68">د</text></g><g transform="translate(120 66) rotate(28 37 37) scale(.8)">${gmIn(gmBow)}</g></svg>` },
  { id: "space", c1: "#4f46e5", c2: "#1e1b4b", art: `<svg viewBox="0 0 300 128" preserveAspectRatio="xMidYMid slice"><rect width="300" height="128" fill="#141844"/><g fill="#fff" opacity=".8"><circle cx="30" cy="20" r="1.4"/><circle cx="120" cy="14" r="1"/><circle cx="270" cy="70" r="1"/><circle cx="60" cy="110" r="1.2"/><circle cx="150" cy="116" r="1"/></g><g fill="none" stroke-width="5"><ellipse cx="226" cy="26" rx="12" ry="18" stroke="#f472b6"/><ellipse cx="226" cy="64" rx="12" ry="18" stroke="#fde047"/><ellipse cx="226" cy="102" rx="12" ry="18" stroke="#34d399"/></g><g font-size="15" font-weight="900" fill="#fff" text-anchor="middle"><text x="226" y="31">أ</text><text x="226" y="69">ب</text><text x="226" y="107">ج</text></g><g transform="translate(56 40) scale(1.5)">${gmIn(gmRocket("#fde047", "#f59e0b"))}</g></svg>` }
];
const gmRTL = () => !EN;
const gmT = (x, y, sc = 1, r = 0) => `translate(${x}px,${y}px) translate(-50%,-50%) scale(${sc}) rotate(${r}deg)`;
function gmPos(el, ar) { const r = el.getBoundingClientRect(), R = ar.getBoundingClientRect(); return { x: r.left - R.left + r.width / 2, y: r.top - R.top + r.height / 2, w: r.width, h: r.height }; }
function gmActor(ar, cls, html, x, y) { const a = document.createElement("div"); a.className = "gx-actor " + cls; a.innerHTML = html; ar.appendChild(a); a._s = 1; a._r = 0; gmPut(a, x, y); return a; }
function gmPut(a, x, y, sc = a._s, r = a._r) { a._x = x; a._y = y; a._s = sc; a._r = r; a.style.transform = gmT(x, y, sc, r); }
function gmFly(a, x, y, ms, { arc = 0, scale = a._s, rot = a._r, ease = "ease-out" } = {}) {
  const x0 = a._x, y0 = a._y, s0 = a._s, r0 = a._r;
  const kf = [{ transform: gmT(x0, y0, s0, r0) }, { transform: gmT((x0 + x) / 2, (y0 + y) / 2 - arc, (s0 + scale) / 2 * (arc ? 1.18 : 1), (r0 + rot) / 2) }, { transform: gmT(x, y, scale, rot) }];
  gmPut(a, x, y, scale, rot);
  let an; try { an = a.animate(kf, { duration: ms, easing: ease }); } catch (e) { }
  return new Promise(res => { let done = false; const f = () => { if (!done) { done = true; res(); } }; if (an) an.onfinish = f; GM.timers.push(setTimeout(f, ms + 60)); });
}
function gmFloat(ar, x, y, txt, color) { const f = document.createElement("div"); f.className = "gm-float"; f.textContent = txt; f.style.left = x + "px"; f.style.top = y + "px"; if (color) f.style.color = color; ar.appendChild(f); GM.timers.push(setTimeout(() => f.remove(), 1300)); }
function gmBanner(ar, txt) { const b = document.createElement("div"); b.className = "gm-banner"; b.textContent = txt; ar.appendChild(b); GM.timers.push(setTimeout(() => b.remove(), 1400)); }
function gmShake(el) { el.classList.remove("gm-shake"); void el.offsetWidth; el.classList.add("gm-shake"); }
const gmStreakMul = s => Math.min(1 + .25 * Math.max(0, s.streak - 1), 2);
const gmOptEl = (ar, k) => ar.querySelector(`.gx-opt[data-opt="${k}"]`);
function gmOpt(q, i, cls) { return `<button type="button" class="gx-opt rgl ${cls}" data-opt="${i}"><span class="val">${q.o[i]}</span></button>`; }
const gmGrid = q => `opts-grid n${q.o.length}`;
/* ---- the four adventures ---- */
const GM_COLS = ["#ef4444", "#f59e0b", "#22c55e", "#8b5cf6", "#ec4899"];
const GMG = {
  /* ⚽ kick the ball into the answer */
  penalty: {
    bg: () => `<div class="pk-crowd"></div>`,
    round(ar, s, q) {
      const d = s.d; d.g = d.g || 0; d.v = d.v || 0;
      ar.innerHTML = `<div class="pk-goal"><div class="${gmGrid(q)}">${q.o.map((o, i) => gmOpt(q, i, "pk-zone")).join("")}</div></div><div class="pk-spot"></div>
      <div class="pk-board">${gt("penalty.you")} <b id="pkG">${d.g}</b>–<b id="pkV">${d.v}</b> ${gt("penalty.keeper")}</div><div class="gm-tip">${gt("games.penalty.tip")}</div>`;
      ar.querySelectorAll(".gx-opt").forEach(b => b.onclick = () => gmChoose(+b.dataset.opt));
      const g = gmPos(ar.querySelector(".pk-goal"), ar);
      d.kp = gmActor(ar, "pk-keeper", gmKeeper, g.x, g.y + g.h / 2 - 36);
      d.ball = gmActor(ar, "pk-ball", "⚽", ar.clientWidth / 2, ar.clientHeight - 48);
    },
    async resolve(ar, s, k, ok, q) {
      const d = s.d, el = gmOptEl(ar, k), z = gmPos(el, ar); let t = z;
      if (ok) { const o = pick([...ar.querySelectorAll(".gx-opt")].filter(b => +b.dataset.opt !== k)); if (o) t = gmPos(o, ar); }
      d.kp.classList.add("dive"); gmSnd("kick");
      const side = t.x < d.kp._x ? -1 : 1;
      await Promise.all([gmFly(d.ball, z.x, z.y, 520, { arc: 46, scale: .62, rot: 540 }), gmWait(160).then(() => gmFly(d.kp, t.x, t.y, 340, { rot: side * 62 }))]);
      if (ok) { d.g++; el.classList.add("goal"); gmSnd("win"); gmBanner(ar, gt("penalty.goal")); gmFloat(ar, z.x, z.y - 20, `+${s.gain}`, "#fde047"); }
      else { d.v++; gmSnd("hit"); gmBanner(ar, gt("penalty.save")); await gmFly(d.ball, z.x + (Math.random() < .5 ? -110 : 110), ar.clientHeight + 60, 560, { scale: 1, rot: 1100, ease: "ease-in" }); }
      ar.querySelector("#pkG").textContent = d.g; ar.querySelector("#pkV").textContent = d.v;
      await gmWait(650);
    },
    final(s) { const g = s.d.g || 0, v = s.d.v || 0; return g > v ? { win: true, medal: "🏆", title: gt("penalty.win", g, v) } : g === v ? { win: false, medal: "🤝", title: gt("penalty.draw", g, v) } : { win: false, medal: "🧤", title: gt("penalty.lose", g, v) }; }
  },
  /* 🐸 jump onto the answer */
  river: {
    round(ar, s, q) {
      const d = s.d; d.n = d.n || 0;
      ar.innerHTML = `<div class="rv-far">${gt("river.bank")}</div><div class="rv-pads ${gmGrid(q)}">${q.o.map((o, i) => gmOpt(q, i, "rv-pad")).join("")}</div><div class="rv-near"></div><div class="gm-tip">${gt("games.river.tip")}</div>`;
      ar.querySelectorAll(".gx-opt").forEach(b => b.onclick = () => gmChoose(+b.dataset.opt));
      const W = ar.clientWidth, H = ar.clientHeight;
      d.frog = gmActor(ar, "rv-frog", "🐸", W / 2, H - 44);
      d.croc = gmActor(ar, "rv-croc", "<span>🐊</span>", gmRTL() ? W - 22 : 22, H - 92);
    },
    ring(ar, x, y) { const r = document.createElement("div"); r.className = "rv-ring"; r.style.left = x + "px"; r.style.top = y + "px"; r.style.transform = "translate(-50%,-50%)"; ar.appendChild(r); GM.timers.push(setTimeout(() => r.remove(), 850)); },
    async resolve(ar, s, k, ok) {
      const d = s.d, pad = gmOptEl(ar, k), p = gmPos(pad, ar), W = ar.clientWidth, H = ar.clientHeight;
      gmSnd("whoosh"); await gmFly(d.frog, p.x, p.y - p.h * .28, 560, { arc: 90 }); this.ring(ar, p.x, p.y);
      if (ok) {
        d.n++; gmSnd("ok"); pad.classList.add("ok"); gmBanner(ar, gt("river.safe")); gmFloat(ar, p.x, p.y - 30, `+${s.gain}`, "#fde047");
        await gmWait(520); gmSnd("whoosh"); await gmFly(d.frog, W / 2, 20, 560, { arc: 60, scale: .8 });
      } else {
        gmSnd("splash"); pad.classList.add("sink"); gmFloat(ar, p.x, p.y - 20, "💦", "#fff"); gmBanner(ar, gt("river.sink"));
        await Promise.all([gmFly(d.croc, p.x, p.y, 520), gmWait(120).then(() => gmFly(d.frog, W / 2, H - 44, 620, { arc: 110 }))]);
        gmSnd("hit"); gmShake(d.croc.firstChild);
      }
      await gmWait(450);
    },
    final(s) { const n = s.d.n || 0, r = n / s.qs.length; return { win: r >= .7, medal: r >= .9 ? "👑" : r >= .6 ? "🐸" : "🐊", title: gt("river.total", n) }; }
  },
  /* 🏹 shoot the balloon that carries the answer */
  balloons: {
    bg: () => `<div class="bl-cloud" style="top:12%;animation-delay:-8s"></div><div class="bl-cloud" style="top:44%;animation-delay:-26s;transform:scale(.7)"></div>`,
    round(ar, s, q) {
      const d = s.d; d.n = d.n || 0;
      ar.innerHTML = `<div class="bl-grid ${gmGrid(q)}">${q.o.map((o, i) => `<div class="bl-cell" data-cell="${i}" style="--bc:${GM_COLS[i]}">${gmBalloon(GM_COLS[i])}${gmOpt(q, i, "")}</div>`).join("")}</div><div class="bl-aim" hidden></div><div class="gm-tip">${gt("games.balloons.tip")}</div>`;
      const W = ar.clientWidth, H = ar.clientHeight; d.bx = W / 2; d.by = H - 52;
      d.bow = gmActor(ar, "bl-bow", gmBow, d.bx, d.by);
      const aim = ar.querySelector(".bl-aim"); aim.style.left = d.bx + "px"; aim.style.top = d.by + "px";
      const pt = e => { const R = ar.getBoundingClientRect(); return { x: e.clientX - R.left, y: e.clientY - R.top }; };
      const point = (x, y, line) => { const a = Math.atan2(y - d.by, x - d.bx) * 180 / Math.PI; d.ang = a; d.bow.firstElementChild.style.transform = `rotate(${a + 90}deg)`; if (line) { aim.hidden = false; aim.style.width = Math.hypot(x - d.bx, y - d.by) + "px"; aim.style.transform = `rotate(${a}deg)`; } };
      d.point = point; point(d.bx, 0);
      ar.onpointermove = e => { if (s.busy || s.ans[s.i] != null) return; const p = pt(e); if (p.y < d.by - 20) point(p.x, p.y, true); };
      ar.onclick = e => {
        if (s.busy || s.ans[s.i] != null || e.target.closest(".gm-sheet")) return;
        const c = e.target.closest(".bl-cell");
        if (c) return gmChoose(+c.dataset.cell);
        const p = pt(e); if (p.y > d.by - 20) return; point(p.x, p.y); gmSnd("whoosh");
        const a = gmActor(ar, "bl-arrow", "<i></i>", d.bx, d.by); gmPut(a, d.bx, d.by, 1, d.ang);
        const L = Math.max(W, H) * 1.2, r = d.ang * Math.PI / 180; gmFly(a, d.bx + Math.cos(r) * L, d.by + Math.sin(r) * L, 520, { ease: "linear" }).then(() => a.remove());
        gmFloat(ar, p.x, p.y, gt("balloons.miss"), "#0f172a");
      };
    },
    burst(ar, x, y, c) { for (let i = 0; i < 12; i++) { const b = document.createElement("i"); b.className = "bl-bit"; b.style.background = i % 3 ? c : "#fff"; b.style.left = x + "px"; b.style.top = y + "px"; ar.appendChild(b); const a = i / 12 * 6.283, r = 40 + Math.random() * 46; try { b.animate([{ transform: "translate(-50%,-50%) scale(1)", opacity: 1 }, { transform: `translate(${Math.cos(a) * r}px,${Math.sin(a) * r + 24}px) scale(.3)`, opacity: 0 }], { duration: 560, easing: "ease-out", fill: "forwards" }); } catch (e) { } GM.timers.push(setTimeout(() => b.remove(), 600)); } },
    async resolve(ar, s, k, ok, q) {
      const d = s.d, cell = ar.querySelector(`[data-cell="${k}"]`), b = cell.querySelector(".bl-b"), p = gmPos(b, ar);
      ar.querySelector(".bl-aim").hidden = true; d.point(p.x, p.y); gmSnd("whoosh");
      const a = gmActor(ar, "bl-arrow", "<i></i>", d.bx, d.by); gmPut(a, d.bx, d.by, 1, d.ang);
      await gmFly(a, p.x, p.y, Math.max(200, Math.hypot(p.x - d.bx, p.y - d.by) * .7), { ease: "linear" }); a.remove();
      b.classList.add("pop"); gmSnd("pop"); this.burst(ar, p.x, p.y, GM_COLS[k]);
      if (ok) { d.n++; gmSnd("ok"); gmBanner(ar, gt("balloons.pop")); gmFloat(ar, p.x, p.y - 10, `+${s.gain}`, "#b45309"); }
      else { gmSnd("no"); cell.classList.add("fall"); gmBanner(ar, gt("balloons.storm")); const c = ar.querySelector(`[data-cell="${q.a}"]`); if (c) c.classList.add("glow"); }
      await gmWait(750);
    },
    final(s) { const n = s.d.n || 0, r = n / s.qs.length; return { win: r >= .7, medal: r >= .9 ? "🎯" : r >= .6 ? "🏹" : "🎈", title: gt("balloons.total", n) }; }
  },
  /* 🚀 steer the ship into the answer's gate */
  space: {
    round(ar, s, q) {
      const d = s.d; d.n = d.n || 0; d.lane = Math.min(1, q.o.length - 1);
      ar.innerHTML = `<div class="sp-bar"><span class="grow"></span><button type="button" class="sp-go">${gt("space.go")}</button></div>
      <div class="sp-lanes">${q.o.map((o, i) => `<div class="sp-lane" data-lane="${i}" style="--bc:${GM_COLS[i]}">${gmOpt(q, i, "sp-gate")}</div>`).join("")}</div>`;
      d.ship = gmActor(ar, "sp-ship", gmRocket("#fde047", "#f59e0b"), 0, 0);
      d.place = fly => { ar.querySelectorAll(".sp-lane").forEach(l => l.classList.toggle("on", +l.dataset.lane === d.lane)); const l = gmPos(ar.querySelector(`[data-lane="${d.lane}"]`), ar), x = d.ship.offsetWidth / 2 + 14; d.sx = gmRTL() ? ar.clientWidth - x : x; fly ? gmFly(d.ship, d.sx, l.y, 180) : gmPut(d.ship, d.sx, l.y); };
      d.place();
      d.go = () => gmChoose(d.lane);
      ar.querySelectorAll(".sp-lane").forEach(l => l.onclick = () => { if (s.busy || s.ans[s.i] != null) return; const i = +l.dataset.lane; if (i === d.lane) return d.go(); d.lane = i; gmSnd("tap"); d.place(true); });
      ar.querySelector(".sp-go").onclick = () => d.go();
    },
    key(e, s) {
      const d = s.d, n = s.qs[s.i].o.length;
      if (e.key === "ArrowUp" || e.key === "ArrowDown") { d.lane = Math.max(0, Math.min(n - 1, d.lane + (e.key === "ArrowUp" ? -1 : 1))); gmSnd("tap"); d.place(true); return true; }
      if (e.key === "Enter" || e.key === " ") { d.go(); return true; }
      return false;
    },
    async resolve(ar, s, k, ok) {
      const d = s.d, gate = gmOptEl(ar, k), g = gmPos(gate, ar), W = ar.clientWidth; const go = ar.querySelector(".sp-go"); if (go) go.remove();
      if (d.lane !== k) { d.lane = k; d.place(); }
      d.ship.classList.add("turbo"); gmSnd("boost");
      const edge = gmRTL() ? g.x + g.w / 2 - 30 : g.x - g.w / 2 + 30;
      await gmFly(d.ship, edge, g.y, 420, { ease: "ease-in" });
      if (ok) { d.n++; gate.classList.add("warp"); gmSnd("win"); gmBanner(ar, gt("space.warp")); gmFloat(ar, g.x, g.y - 10, `+${s.gain}`, "#fde047"); await gmFly(d.ship, gmRTL() ? -90 : W + 90, g.y, 420, { ease: "ease-in", scale: 1.3 }); }
      else { gate.classList.add("boom"); gmSnd("hit"); gmFloat(ar, edge, g.y, "💥", "#fff"); gmBanner(ar, gt("space.boom")); await gmFly(d.ship, d.sx, g.y, 620, { rot: gmRTL() ? 360 : -360 }); gmPut(d.ship, d.sx, g.y, 1, 0); }
      d.ship.classList.remove("turbo"); await gmWait(400);
    },
    final(s) { const n = s.d.n || 0, r = n / s.qs.length; return { win: r >= .7, medal: r >= .9 ? "🌟" : r >= .6 ? "🚀" : "🛰️", title: gt("space.total", n) }; }
  }
};
