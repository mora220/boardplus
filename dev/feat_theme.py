"""BoardPlus theme: the kids' cheerful look, grown up for the whole site.
  * One palette (grape, sun, mint, coral, sky) and one type pair (Baloo Bhaijaan 2 + Tajawal) everywhere.
  * Teacher screen: a soft classroom wall, chunky chips in the header, a grape code badge, a rounded students panel
    whose cards carry each student's monster buddy, an owl waiting while the class is empty.
  * Quiz builder / runner / leaderboard, dialogs, toasts and buttons share the same parts.
  * New home page: hero with a live product picture (buddies, stamps, points) and the owl, start cards for teacher
    and student, features, the student screen, the games, three steps, and a closing band.
Runs after feat_kids (which supplies KID_AVA, kidLottie, kjOpen)."""
import json

LOGO = ('<svg class="bulogo" viewBox="0 0 48 48" aria-hidden="true"><rect x="2" y="2" width="44" height="44" rx="13" fill="#7c5cff"/>'
        '<rect x="9.5" y="11" width="29" height="20" rx="3.5" fill="#fff"/><path d="M15 21.5l4.6 4.2L29 15.6" fill="none" stroke="#ff5a6a" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="12" y="34.5" width="24" height="4" rx="2" fill="#fff" opacity=".55"/><rect x="31" y="32.6" width="9" height="7.8" rx="2" fill="#ffd23f"/></svg>')
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect x="2" y="2" width="44" height="44" rx="13" fill="#7c5cff"/>'
           '<rect x="9.5" y="11" width="29" height="20" rx="3.5" fill="#fff"/><path d="M15 21.5l4.6 4.2L29 15.6" fill="none" stroke="#ff5a6a" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
           '<rect x="12" y="34.5" width="24" height="4" rx="2" fill="#fff" opacity=".55"/><rect x="31" y="32.6" width="9" height="7.8" rx="2" fill="#ffd23f"/></svg>\n')
STAR = ('<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 4.5l5.6 12 13 1.5-9.7 8.9 2.6 12.9L24 33.2l-11.5 6.6 2.6-12.9-9.7-8.9 13-1.5z" '
        'fill="#ffd23f" stroke="#f0a500" stroke-width="2.6" stroke-linejoin="round"/></svg>')
ICO = lambda n: f'<svg class="ico"><use href="#i-{n}"/></svg>'

WALL = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='260' height='260' viewBox='0 0 260 260'%3E"
        "%3Cg fill='none' stroke-width='3' stroke-linecap='round' stroke-linejoin='round' opacity='.42'%3E"
        "%3Cpath d='M30 40h18M39 31v18' stroke='%23c9bcff'/%3E%3Ccircle cx='200' cy='46' r='9' stroke='%23ffd27a'/%3E"
        "%3Cpath d='M118 120l9 16h-18z' stroke='%23a6e9cf'/%3E%3Cpath d='M214 170l12 12M226 170l-12 12' stroke='%23ffb3bd'/%3E"
        "%3Cpath d='M52 196l3.6 7.4 8.1.9-6 5.6 1.7 8-7.4-4.2-7.4 4.2 1.7-8-6-5.6 8.1-.9z' stroke='%23ffd27a'/%3E"
        "%3Crect x='150' y='224' width='16' height='16' rx='4' stroke='%23b8dcff'/%3E%3C/g%3E%3C/svg%3E\")")

CSS = r"""
/* ===================== theme: one cheerful family for the whole site ===================== */
:root{
  --wall:#eff1fb; --surface:#ffffff; --surface-2:#f5f3ff; --ink:#2b2d55; --muted:#6b6f9a; --line:#e6e2f7;
  --accent:#7c5cff; --accent-2:#5636e0; --accent-soft:#efeaff; --accent-ink:#ffffff;
  --red:#ff4d5e; --red-soft:#ffe8ea; --ok:#16b37c; --ok-soft:#e2f8ef; --hand:#ffc83d; --hand-soft:#fff3cc; --hl:#ffd84d;
  --paper:#ffffff; --grid:#e8ebf6; --ring:#e4dcff;
  --shadow:0 3px 0 var(--ring),0 18px 34px -22px rgba(76,52,180,.45);
  --f-display:var(--k-f1); --f-body:var(--k-f2);
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --wall:#141229; --surface:#1d1a3a; --surface-2:#252148; --ink:#eceaff; --muted:#a8a4d2; --line:#332e5e; --ring:#2c275a;
  --accent:#a48bff; --accent-2:#7c5cff; --accent-soft:#2c2560; --accent-ink:#141229; --grid:#e8ebf6;
  --shadow:0 3px 0 #0e0c22,0 18px 34px -20px rgba(0,0,0,.7)}}
:root[data-theme="dark"]{
  --wall:#141229; --surface:#1d1a3a; --surface-2:#252148; --ink:#eceaff; --muted:#a8a4d2; --line:#332e5e; --ring:#2c275a;
  --accent:#a48bff; --accent-2:#7c5cff; --accent-soft:#2c2560; --accent-ink:#141229; --grid:#e8ebf6;
  --shadow:0 3px 0 #0e0c22,0 18px 34px -20px rgba(0,0,0,.7)}
body{font-family:var(--f-body)}

/* ---------- shared parts ---------- */
.btn{font-family:var(--f-display);font-weight:700;border-radius:14px;border:0;background:var(--surface);box-shadow:0 3px 0 var(--ring);color:var(--ink);transition:transform .1s,box-shadow .1s,filter .15s,background .15s}
.btn:hover{background:var(--surface);filter:brightness(1.03);border-color:transparent}
.btn:not(:disabled):active{transform:translateY(2px);box-shadow:0 1px 0 var(--ring)}
.btn.pri{background:linear-gradient(#8f74ff,#6c4cff);color:#fff;box-shadow:0 4px 0 var(--k-grape-d)}
.btn.pri:hover{background:linear-gradient(#8f74ff,#6c4cff);filter:brightness(1.07)}
.btn.pri:not(:disabled):active{box-shadow:0 1px 0 var(--k-grape-d)}
.btn.danger{color:#e23d50}
.btn.on{background:var(--accent-soft);color:var(--accent);box-shadow:0 3px 0 color-mix(in srgb,var(--accent) 35%,var(--ring))}
.btn.big{border-radius:18px;padding:15px 24px;font-size:18px}
.btn.icon{border-radius:14px}
.inp{border:2px solid var(--line);border-radius:14px;background:var(--surface)}
.inp:focus{border-color:var(--accent);box-shadow:0 0 0 4px var(--accent-soft)}
.pill{background:var(--surface);border:0;box-shadow:0 3px 0 var(--ring);font-weight:700}
.seg{background:var(--surface-2);border:0;border-radius:14px;padding:3px}
.seg button{border-radius:11px;font-family:var(--f-display);font-weight:700}
.seg button.on{background:var(--surface);color:var(--accent);box-shadow:0 2px 0 var(--ring)}
.veil{background:rgba(43,45,85,.4);backdrop-filter:blur(6px)}
.dlg{border-radius:26px;border:0;box-shadow:0 7px 0 var(--ring),0 40px 80px -30px rgba(43,45,85,.6)}
.dlg h3{font-family:var(--f-display);font-weight:800}
.toast{background:var(--surface);color:var(--ink);font-family:var(--f-display);font-weight:700;font-size:16px;border-radius:18px;padding:10px 18px;box-shadow:0 5px 0 var(--ring),0 24px 40px -22px rgba(76,52,180,.55)}
.toast.red{color:#d8344a;box-shadow:0 5px 0 #ffd0d6,0 24px 40px -22px rgba(216,52,74,.45)}
.word b{color:var(--accent)}
.card{border-radius:26px}
.ava{box-shadow:0 0 0 2.5px var(--surface),0 0 0 4.5px var(--ring)}

/* the toolbar is a crayon tray, the board sits in a soft frame (teacher, correction view) */
:root .tb{background:var(--surface);border:0;border-radius:24px;padding:7px 10px;gap:4px;box-shadow:0 6px 0 var(--ring),0 26px 40px -24px rgba(76,52,180,.5)}
.tb button{width:40px;height:40px;border-radius:14px;color:var(--ink)}
.tb button:hover{background:var(--surface-2)}
.tb button[data-t].on{background:linear-gradient(#8f74ff,#6c4cff);color:#fff;box-shadow:0 3px 0 var(--k-grape-d)}
.tb button.on{background:var(--accent-soft);color:var(--accent)}
.tb .sw{width:28px;height:28px;border:3px solid var(--surface);box-shadow:0 0 0 2px var(--line);transition:transform .15s}
.tb button.on .sw{box-shadow:0 0 0 3px var(--accent);transform:scale(1.1)}
.tb .sep{background:var(--line);width:2px;border-radius:2px}
.pager{border:0;background:var(--surface);border-radius:16px;box-shadow:0 3px 0 var(--ring)}
:root #teacher .stage,:root #focus .stage{background-color:transparent;background-image:""" + WALL + r""";background-size:260px 260px}
:root #teacher .board,:root #focus .board{border-radius:20px;box-shadow:0 0 0 7px var(--surface),0 0 0 10px var(--ring),0 30px 50px -26px rgba(76,52,180,.5)}

/* ---------- teacher screen ---------- */
#teacher,#focus{background:linear-gradient(165deg,#edf1ff 0%,#f3eeff 55%,#fff5e8 100%)}
:root[data-theme="dark"] #teacher,:root[data-theme="dark"] #focus{background:var(--wall)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) #teacher,:root:not([data-theme="light"]) #focus{background:var(--wall)}}
#teacher > .top,#focus > .top{background:transparent;border:0;box-shadow:none;padding-block:12px 6px;gap:10px}
#teacher .brand{background:var(--surface);border-radius:999px;padding:5px 16px 5px 5px;box-shadow:0 3px 0 var(--ring);gap:10px}
[dir="rtl"] #teacher .brand{padding:5px 5px 5px 16px}
#teacher .brand .ava{width:42px;height:42px}
#teacher .brand .word{font-size:19px;font-weight:800}
#teacher .clock{background:var(--surface);border-radius:16px;padding:4px 12px;box-shadow:0 3px 0 var(--ring)}
#teacher .clock b{font-family:var(--f-display);font-weight:800}
.codebox{background:linear-gradient(#8f74ff,#6c4cff);border:0;border-radius:18px;padding:5px 6px 5px 14px;box-shadow:0 4px 0 var(--k-grape-d);color:#fff}
[dir="rtl"] .codebox{padding:5px 14px 5px 6px}
.codebox .lbl{color:rgba(255,255,255,.82);font-weight:700}
.codebox .val{color:#fff;font-family:var(--f-display);font-weight:800;font-size:28px;letter-spacing:.16em}
.codebox .btn{background:rgba(255,255,255,.18);color:#fff;box-shadow:none}
.codebox .btn:hover{background:rgba(255,255,255,.3)}
.codebox .btn .ico{stroke:#fff}
#tCls{border:2px dashed var(--line);box-shadow:none;background:var(--surface)}
#tCls.on{border-style:solid;border-color:color-mix(in srgb,var(--accent) 40%,var(--line))}
.tgrp{background:var(--surface);border:0;border-radius:18px;padding:4px;gap:2px;box-shadow:0 3px 0 var(--ring)}
.tgrp .btn{box-shadow:none;background:transparent;border-radius:13px;padding:8px 11px}
.tgrp .btn:hover{background:var(--surface-2)}
.tgrp .btn.on{background:var(--accent-soft);color:var(--accent);box-shadow:none}
.tgrp .btn.warn.on{background:var(--red-soft);color:var(--red)}
#teacher .timer{font-family:var(--f-display);font-weight:800;border-radius:999px;box-shadow:0 3px 0 var(--ring)}
#teacher .tbody{gap:0}
#teacher .panel{margin:6px 12px 12px;border:0;border-radius:26px;box-shadow:0 5px 0 var(--ring),0 30px 50px -30px rgba(76,52,180,.45);overflow:hidden}
#teacher .panel-h{border-bottom:2px solid var(--surface-2);padding:14px 16px}
#teacher .panel-h h3{font-family:var(--f-display);font-weight:800;font-size:20px;display:flex;align-items:center;gap:6px}
#teacher .panel-h .count{background:var(--accent-soft);color:var(--accent);border-radius:999px;padding:0 10px;font-size:15px;font-weight:800;font-family:var(--f-display)}
#teacher .hcount{background:var(--hand-soft);color:#8a5a00;border-radius:999px;padding:0 10px;font-size:14px;font-weight:800}
.grid{gap:14px;padding:14px}
.sc{border:0;border-radius:20px;padding:7px;background:var(--surface);box-shadow:0 0 0 2px var(--surface-2),0 4px 0 var(--ring);transition:transform .15s,box-shadow .15s}
.sc:hover{transform:translateY(-3px);border-color:transparent;box-shadow:0 0 0 2px color-mix(in srgb,var(--accent) 40%,var(--surface-2)),0 7px 0 var(--ring)}
.sc canvas{border-radius:13px;box-shadow:0 0 0 2px var(--surface-2)}
.sc.raised{box-shadow:0 0 0 3px var(--hand),0 4px 0 #e8b000;animation:tRaise 1.6s ease-out infinite}
@keyframes tRaise{0%{box-shadow:0 0 0 3px var(--hand),0 4px 0 #e8b000,0 0 0 3px rgba(255,200,61,.5)}100%{box-shadow:0 0 0 3px var(--hand),0 4px 0 #e8b000,0 0 0 16px rgba(255,200,61,0)}}
.sc .hb{background:linear-gradient(#ffd863,#ffc229);color:#5b3b00;font-family:var(--f-display);font-weight:800;box-shadow:0 2px 0 #e39d00;border-radius:12px;padding:3px 9px;font-size:13px}
.sc .nm{font-family:var(--f-display);font-weight:700;font-size:15px;padding:6px 2px 1px;gap:7px}
.sc .sav{width:30px;height:30px;border-radius:50%;background:var(--t,var(--accent-soft));display:grid;place-items:center;flex:none;font-style:normal;font-size:14px;font-weight:800;color:var(--accent)}
.sc .sav .kava{width:30px}
.sc .st{width:9px;height:9px}
.sc{position:relative}
@media (hover:hover){
  .sc .rn,.sc .rm{position:absolute;top:13px;width:30px;height:30px;border-radius:10px;background:var(--surface);box-shadow:0 2px 0 var(--ring);opacity:0;transition:opacity .15s;z-index:2}
  .sc .rm{inset-inline-start:13px}.sc .rn{inset-inline-start:48px}
  .sc:hover .rn,.sc:hover .rm,.sc:focus-within .rn,.sc:focus-within .rm{opacity:1}
}
:root #teacher .stage{padding:22px}
.grid.bigcols .sc .sav{width:38px;height:38px}.grid.bigcols .sc .sav .kava{width:38px}
.empty{border:0;background:var(--surface-2);border-radius:24px;padding:16px 18px 22px;gap:6px}
.empty b{font-family:var(--f-display);font-weight:800;font-size:20px}
.eowl{width:150px;height:150px;margin:-6px auto -10px}
.empty .bigcode{font-family:var(--f-display);font-weight:800;color:#fff;background:linear-gradient(#8f74ff,#6c4cff);border-radius:18px;padding:6px 18px;box-shadow:0 4px 0 var(--k-grape-d);letter-spacing:.16em;margin:6px auto}
.credit{border-top:2px solid var(--surface-2)}
.mtabs .btn{box-shadow:0 3px 0 var(--ring)}
#focus .nm{font-family:var(--f-display);font-weight:800;font-size:19px;background:var(--surface);border-radius:999px;padding:6px 14px;box-shadow:0 3px 0 var(--ring)}
#focus .fhint{background:var(--red-soft);color:#d8344a;border-radius:999px;padding:4px 12px;font-weight:700;font-size:13px}
.fsbar .btn,.joinmini{box-shadow:0 3px 0 var(--ring)}

/* ---------- quiz (teacher) and leaderboard ---------- */
.qz{background:linear-gradient(165deg,#edf1ff 0%,#f3eeff 55%,#fff5e8 100%)}
:root[data-theme="dark"] .qz{background:var(--wall)}
.qz > .top{background:transparent;border:0;box-shadow:none}
.qz-t{font-family:var(--f-display);font-weight:800}
.opt{--c:#7c5cff;--d:#5636e0;border-radius:22px;box-shadow:0 7px 0 var(--d);background:linear-gradient(color-mix(in srgb,var(--c) 82%,#fff),var(--c))}
.opt[data-o="B"]{--c:#ff9638;--d:#d46b12}.opt[data-o="C"]{--c:#1fc58f;--d:#11946a}.opt[data-o="D"]{--c:#3fa9f5;--d:#1d7cc4}
.opt .ol{font-family:var(--f-display);font-weight:800}
.qtime{font-family:var(--f-display);font-weight:800;border-radius:16px;background:var(--surface);box-shadow:0 3px 0 var(--ring)}
.lr{border:0;border-radius:18px;box-shadow:0 3px 0 var(--ring)}
.lr .lt{font-family:var(--f-display);font-weight:800;color:var(--accent)}
.myrank{font-family:var(--f-display);font-weight:800}
.pd .pa{font-family:var(--f-display)}
.pd .pb{font-family:var(--f-display);font-weight:800}
#qRace{background:linear-gradient(#3b3f75,#2b2d55);color:#fff;box-shadow:0 4px 0 #17183a}
#qTug{background:linear-gradient(135deg,#ff6b6b,#7c5cff);color:#fff;box-shadow:0 4px 0 #5636e0}
.qcard,.qitem{border-radius:20px}
.ggames{gap:10px}
.ggame{border:0;border-radius:18px;background:var(--surface-2);box-shadow:0 3px 0 var(--ring);font-family:var(--f-display);transition:transform .15s}
.ggame:hover{transform:translateY(-2px)}
.ggame b{font-weight:800}
.ggame.on{background:var(--accent-soft);box-shadow:inset 0 0 0 3px var(--accent),0 3px 0 color-mix(in srgb,var(--accent) 45%,var(--ring))}
.gameov .top,.gameov > header{background:transparent}

/* ===================== home ===================== */
#home{background:#fbfaff;color:var(--k-ink);overflow-x:hidden}
:root[data-theme="dark"] #home{background:#fbfaff}
#home .doodles{display:none}
.h-wrap{max-width:1200px;margin:0 auto;width:100%}
.h-nav{position:sticky;top:0;z-index:20;background:rgba(251,250,255,.82);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid transparent;transition:border-color .2s,box-shadow .2s}
.h-nav.stuck{border-color:#ece8fb;box-shadow:0 10px 30px -24px rgba(76,52,180,.5)}
.h-nav .h-wrap{display:flex;align-items:center;gap:14px;padding-block:14px}
.h-logo{display:flex;align-items:center;gap:9px;font-family:var(--k-f1);font-weight:800;font-size:24px;color:var(--k-ink);direction:ltr;white-space:nowrap}
.h-logo b{color:var(--k-grape)}.h-logo .bulogo{width:36px;height:36px}
.h-links{display:flex;gap:4px;margin-inline-start:18px}
.h-links a{font-family:var(--k-f1);font-weight:700;font-size:16px;color:var(--k-mut);text-decoration:none;padding:8px 12px;border-radius:12px}
.h-links a:hover{background:#f1edff;color:var(--k-grape)}
.h-nav .grow{flex:1}
#home .datechip{background:#fff;border:0;box-shadow:0 3px 0 var(--k-ring);border-radius:14px;font-size:13px;color:var(--k-mut)}
#home .datechip b{color:var(--k-ink);font-family:var(--k-f1)}
#home .langbtn{background:#fff;border:0;box-shadow:0 3px 0 var(--k-ring);border-radius:14px;font-family:var(--k-f1);font-weight:700;color:var(--k-grape);padding:8px 14px;cursor:pointer}
.h-nav .btn.pri{padding:10px 18px}
.h-hero{position:relative;padding-block:clamp(26px,5vw,64px) clamp(30px,5vw,70px)}
.h-hero::before{content:"";position:absolute;inset:-120px -20vw 0;z-index:0;pointer-events:none;
  background:radial-gradient(520px 380px at 12% 30%,#efe8ff 0,transparent 70%),radial-gradient(480px 360px at 88% 10%,#fff0d9 0,transparent 70%),radial-gradient(420px 320px at 70% 90%,#dcf8ec 0,transparent 70%)}
.h-hero .h-wrap{position:relative;z-index:1;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:clamp(24px,4vw,60px);align-items:center}
.h-badge{display:inline-flex;align-items:center;gap:8px;background:#fff;border-radius:999px;padding:6px 14px 6px 8px;box-shadow:0 3px 0 var(--k-ring);font-family:var(--k-f1);font-weight:700;font-size:15px;color:var(--k-grape)}
[dir="rtl"] .h-badge{padding:6px 8px 6px 14px}
.h-badge i{font-style:normal;background:var(--k-grape);color:#fff;border-radius:999px;padding:1px 10px;font-size:13px}
.h-h1{margin:18px 0 0;font-family:var(--k-f1);font-weight:800;font-size:clamp(38px,5.4vw,68px);line-height:1.12;letter-spacing:-.01em;color:var(--k-ink);text-wrap:balance}
.h-h1 .hl{color:var(--k-grape);position:relative;white-space:nowrap}
.h-h1 .hl::after{content:"";position:absolute;inset-inline:-4px;bottom:.06em;height:.28em;background:#ffe27a;border-radius:8px;z-index:-1;transform:rotate(-1.2deg)}
.h-lead{margin:18px 0 0;font-size:clamp(16.5px,1.5vw,19px);line-height:1.85;color:#565a86;max-width:44ch;text-wrap:pretty}
.h-cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}
.h-cta .btn.big{font-size:19px;padding:16px 26px}
.h-ghost{background:#fff!important;color:var(--k-ink)!important}
.h-trust{display:flex;flex-wrap:wrap;gap:8px 18px;margin:22px 0 0;padding:0;list-style:none;color:var(--k-mut);font-weight:700;font-size:14.5px}
.h-trust li{display:flex;align-items:center;gap:6px}
.h-trust li::before{content:"✓";width:20px;height:20px;border-radius:50%;background:#dff7ee;color:#16a374;display:grid;place-items:center;font-size:12px;font-weight:800}
/* the product picture */
.h-pic{position:relative;padding:30px 10px 40px}
.h-screen{position:relative;background:#fff;border-radius:28px;box-shadow:0 8px 0 var(--k-ring),0 60px 90px -40px rgba(76,52,180,.55);overflow:hidden;transform:rotate(-1.2deg)}
[dir="ltr"] .h-screen{transform:rotate(1.2deg)}
.h-sbar{display:flex;align-items:center;gap:10px;padding:12px 16px;border-bottom:2px solid #f3f0ff}
.h-sbar .dots{display:flex;gap:6px;direction:ltr}.h-sbar .dots i{width:11px;height:11px;border-radius:50%;background:#ece8fb}
.h-sbar .dots i:nth-child(1){background:#ff8f8f}.h-sbar .dots i:nth-child(2){background:#ffd36b}.h-sbar .dots i:nth-child(3){background:#7ee0b5}
.h-code{margin-inline-start:auto;background:linear-gradient(#8f74ff,#6c4cff);color:#fff;border-radius:12px;padding:3px 12px;font-family:var(--k-f1);font-weight:800;font-size:15px;letter-spacing:.12em;box-shadow:0 3px 0 var(--k-grape-d)}
.h-cnt{background:#f5f2ff;color:var(--k-grape);border-radius:12px;padding:3px 12px;font-family:var(--k-f1);font-weight:800;font-size:14px}
.h-sin{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;padding:16px;background:linear-gradient(165deg,#f1f4ff,#f6f1ff)}
.h-t{background:#fff;border-radius:16px;padding:6px;box-shadow:0 3px 0 var(--k-ring)}
.h-t.raise{box-shadow:0 0 0 3px #ffc83d,0 3px 0 #e8b000}
.h-p{position:relative;aspect-ratio:16/11;border-radius:11px;background-color:#fff;background-image:linear-gradient(#eef1f8 1px,transparent 1px),linear-gradient(90deg,#eef1f8 1px,transparent 1px);background-size:12px 12px;display:grid;place-items:center;box-shadow:inset 0 0 0 2px #f3f0ff;overflow:hidden}
.h-w{font-family:"Aref Ruqaa",var(--k-f1);font-weight:700;font-size:clamp(14px,1.4vw,19px);color:#2b2d55;white-space:nowrap;direction:rtl}
.h-ok{position:absolute;inset-inline-start:6px;bottom:0;font-size:24px;font-weight:900;color:#ff4d5e;transform:rotate(-8deg)}
.h-fix{position:absolute;inset-inline-start:8px;top:1px;font-family:"Aref Ruqaa",serif;font-weight:700;font-size:19px;color:#ff4d5e;transform:rotate(-8deg)}
.h-st{position:absolute;inset-inline-start:4px;bottom:4px;font-family:"Aref Ruqaa",serif;font-weight:700;font-size:13px;color:#ff4d5e;border:2px solid #ff4d5e;border-radius:6px;padding:0 5px;transform:rotate(-10deg)}
.h-hand{position:absolute;inset-inline-end:5px;top:5px;background:linear-gradient(#ffd863,#ffc229);border-radius:99px;font-size:12px;padding:1px 7px;box-shadow:0 2px 0 #e39d00}
.h-n{display:flex;align-items:center;gap:6px;padding:6px 2px 1px;font-family:var(--k-f1);font-weight:700;font-size:13px;color:var(--k-ink)}
.h-n .av{width:24px;height:24px;border-radius:50%;display:grid;place-items:center;flex:none}
.h-n .av .kava{width:24px}
.h-float{position:absolute;z-index:2;display:flex;align-items:center;gap:8px;background:#fff;border-radius:18px;padding:8px 14px;box-shadow:0 5px 0 var(--k-ring),0 24px 40px -22px rgba(76,52,180,.55);font-family:var(--k-f1);font-weight:800;font-size:15px;color:var(--k-ink);white-space:nowrap}
.h-float svg{width:26px;height:26px}
.h-float.f1{top:6px;inset-inline-start:-4px}
.h-float.f2{top:-14px;inset-inline-end:60px;color:#5b3b00;background:linear-gradient(#ffdc6b,#ffc531);box-shadow:0 5px 0 var(--k-sun-d),0 24px 40px -22px rgba(160,100,0,.5)}
.h-float.f3{bottom:-6px;inset-inline-start:16%;color:#d8344a}
.h-owl{position:absolute;z-index:3;width:160px;height:160px;bottom:-34px;inset-inline-end:-34px}
/* start cards */
.h-sec{padding-block:clamp(40px,6vw,84px)}
.h-kicker{display:inline-block;font-family:var(--k-f1);font-weight:800;font-size:15px;color:var(--k-grape);background:#f1edff;border-radius:999px;padding:4px 14px}
.h-h2{margin:12px 0 0;font-family:var(--k-f1);font-weight:800;font-size:clamp(28px,3.4vw,44px);line-height:1.2;color:var(--k-ink);text-wrap:balance}
.h-sub{margin:10px 0 0;color:#5f638f;font-size:17px;line-height:1.8;max-width:56ch}
.h-head{text-align:center;display:flex;flex-direction:column;align-items:center;margin-bottom:36px}
.h-start{background:linear-gradient(180deg,#fbfaff,#f4f1ff)}
.h-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;max-width:960px;margin:0 auto}
#home .h-cards .card{position:relative;background:#fff;border:0;border-radius:28px;padding:28px 26px 24px;box-shadow:0 7px 0 var(--k-ring),0 40px 70px -40px rgba(76,52,180,.5);display:flex;flex-direction:column;gap:12px;margin:0;max-width:none;color:var(--k-ink)}
#home .h-cards .hx-tape{display:none}
#home #adminCard[hidden]{display:flex}
#home #adminCard .welcome{display:flex;gap:12px;align-items:center}
#home #adminCard .welcome .wave{width:54px;height:54px;border-radius:18px;background:linear-gradient(#8f74ff,#6c4cff);color:#fff;display:grid;place-items:center;box-shadow:0 4px 0 var(--k-grape-d)}
#home #adminCard h2,#home .kj-teaser h2{font-family:var(--k-f1);font-weight:800;font-size:24px}
#home #adminCard .gbtn{background:#fff;box-shadow:0 0 0 2px #ece8fb,0 4px 0 var(--k-ring);color:var(--k-ink);justify-content:center}
#home #adminCard .switch{display:none}
#home .kj-teaser{justify-content:center}
#home .kj-teaser .tlink{display:none}
#home .kt-avas span{box-shadow:0 0 0 4px #fff}
/* features */
.h-feat{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px}
.h-f{background:#fff;border-radius:24px;padding:22px 20px;box-shadow:0 5px 0 var(--k-ring),0 30px 50px -40px rgba(76,52,180,.5);display:flex;flex-direction:column;gap:8px;transition:transform .2s}
.h-f:hover{transform:translateY(-4px)}
.h-f .ic{width:52px;height:52px;border-radius:16px;display:grid;place-items:center;background:var(--c);box-shadow:0 4px 0 var(--d);margin-bottom:6px}
.h-f .ic .ico{width:26px;height:26px;stroke:#fff;stroke-width:2.2}
.h-f b{font-family:var(--k-f1);font-weight:800;font-size:19px;color:var(--k-ink)}
.h-f span{color:#5f638f;font-size:15px;line-height:1.7}
/* split rows */
.h-split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(24px,5vw,70px);align-items:center}
.h-list{list-style:none;margin:20px 0 0;padding:0;display:flex;flex-direction:column;gap:14px}
.h-list li{display:flex;gap:12px;align-items:flex-start;font-size:16.5px;line-height:1.7;color:#4b4f7c}
.h-list li b{color:var(--k-ink);font-family:var(--k-f1);font-weight:800}
.h-list li::before{content:"";flex:none;width:28px;height:28px;margin-top:1px;border-radius:10px;background:#efeaff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M6 12.5l4 4L18 8' fill='none' stroke='%237c5cff' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/18px no-repeat}
.h-phone{position:relative;width:min(320px,80%);margin:0 auto;aspect-ratio:9/17;border-radius:42px;background:#2b2d55;padding:12px;box-shadow:0 40px 80px -40px rgba(43,45,85,.7)}
.h-phone .scr{position:relative;height:100%;border-radius:32px;overflow:hidden;background:linear-gradient(165deg,#e8f0ff,#f1eaff 55%,#fff2e2);display:flex;flex-direction:column;align-items:center;padding:18px 14px;gap:10px}
.h-phone .row{display:flex;align-items:center;gap:8px;width:100%}
.h-phone .me{display:flex;align-items:center;gap:6px;background:#fff;border-radius:999px;padding:3px 10px 3px 3px;box-shadow:0 3px 0 var(--k-ring);font-family:var(--k-f1);font-weight:800;font-size:13px}
[dir="rtl"] .h-phone .me{padding:3px 3px 3px 10px}
.h-phone .me span{width:30px;height:30px;border-radius:50%;display:grid;place-items:center}.h-phone .me .kava{width:30px}
.h-phone .pts{margin-inline-start:auto;display:flex;align-items:center;gap:4px;background:linear-gradient(#ffdc6b,#ffc531);border-radius:999px;padding:3px 10px;box-shadow:0 3px 0 var(--k-sun-d);font-family:var(--k-f1);font-weight:800;color:#5b3b00}
.h-phone .pts svg{width:20px;height:20px}
.h-phone .bd{width:100%;flex:1;border-radius:18px;background:#fff;box-shadow:0 0 0 5px #fff,0 0 0 8px #dcd2ff;display:grid;place-items:center;position:relative}
.h-phone .bd .h-w{font-size:26px}
.h-phone .card2{position:absolute;inset-inline:10%;bottom:16%;background:#fff;border-radius:22px;box-shadow:0 6px 0 var(--k-ring),0 30px 50px -24px rgba(43,45,85,.5);text-align:center;padding:0 10px 12px;font-family:var(--k-f1)}
.h-phone .card2 .a{width:110px;height:110px;margin:-58px auto 0}
.h-phone .card2 b{display:block;font-size:22px;color:var(--k-grape);font-weight:800}
.h-phone .card2 small{color:var(--k-mut);font-weight:700}
.h-phone .tray{width:100%;height:40px;border-radius:16px;background:#fff;box-shadow:0 4px 0 var(--k-ring);display:flex;align-items:center;justify-content:center;gap:10px}
.h-phone .tray i{width:22px;height:22px;border-radius:8px;background:#efeaff}.h-phone .tray i:first-child{background:linear-gradient(#8f74ff,#6c4cff)}
/* games */
.h-games{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.h-g{position:relative;border-radius:26px;padding:24px 22px;color:#fff;min-height:200px;display:flex;flex-direction:column;justify-content:flex-end;gap:6px;overflow:hidden;box-shadow:0 7px 0 var(--d)}
.h-g::before{content:"";position:absolute;width:180px;height:180px;border-radius:50%;background:rgba(255,255,255,.14);top:-60px;inset-inline-end:-50px}
.h-g .em{position:absolute;top:18px;inset-inline-start:20px;font-size:54px;filter:drop-shadow(0 4px 0 rgba(0,0,0,.12))}
.h-g b{font-family:var(--k-f1);font-weight:800;font-size:24px;position:relative}
.h-g span{position:relative;opacity:.92;line-height:1.6}
/* steps */
.h-steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;counter-reset:st}
.h-steps li{counter-increment:st;background:#fff;border-radius:24px;padding:24px 22px;box-shadow:0 5px 0 var(--k-ring);display:flex;flex-direction:column;gap:6px;position:relative}
.h-steps li::before{content:counter(st);width:46px;height:46px;border-radius:16px;background:linear-gradient(#ffdc6b,#ffc531);box-shadow:0 4px 0 var(--k-sun-d);display:grid;place-items:center;font-family:var(--k-f1);font-weight:800;font-size:22px;color:#5b3b00;margin-bottom:6px}
.h-steps b{font-family:var(--k-f1);font-weight:800;font-size:19px;color:var(--k-ink)}
.h-steps span{color:#5f638f}
/* closing band */
.h-band{position:relative;border-radius:34px;background:linear-gradient(135deg,#8a6dff,#6a49ff 60%,#5a3be8);color:#fff;padding:clamp(28px,5vw,56px);display:flex;align-items:center;gap:30px;overflow:hidden;box-shadow:0 10px 0 #4a2fc4,0 50px 90px -40px rgba(76,52,180,.7)}
.h-band::before{content:"";position:absolute;inset:0;background:radial-gradient(300px 200px at 90% 0,rgba(255,255,255,.18),transparent 70%),radial-gradient(300px 200px at 0 100%,rgba(255,210,63,.25),transparent 70%)}
.h-band > *{position:relative}
.h-band h2{margin:0;font-family:var(--k-f1);font-weight:800;font-size:clamp(26px,3.2vw,40px);line-height:1.25}
.h-band p{margin:8px 0 18px;opacity:.9;font-size:17px}
.h-band .btn.big{background:#fff;color:var(--k-grape);box-shadow:0 5px 0 #d9ceff}
.h-band .bo{width:190px;height:190px;flex:none;margin-inline-start:auto}
.h-foot{padding-block:30px 40px;text-align:center;color:var(--k-mut);font-size:14px}
.h-foot .h-logo{justify-content:center;font-size:20px;margin-bottom:6px}
.h-rv{opacity:0;transform:translateY(24px)}
.h-rv.in{opacity:1;transform:none;transition:opacity .7s ease,transform .7s cubic-bezier(.2,.8,.3,1)}
@media (prefers-reduced-motion:reduce){.h-rv{opacity:1;transform:none}}
@media (max-width:1100px){.h-links{display:none}.h-feat{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:900px){
  .h-hero .h-wrap,.h-split{grid-template-columns:1fr}
  .h-pic{padding:34px 4px 40px}
  .h-cards,.h-games,.h-steps{grid-template-columns:1fr}
  .h-band{flex-direction:column;text-align:center}.h-band .bo{margin:0 auto;order:-1;width:150px;height:150px}
  #home .datechip{display:none}
  .h-split .h-phone{order:2}
}
@media (max-width:560px){
  .h-nav .btn.pri{display:none}
  .h-feat{grid-template-columns:1fr}
  .h-sin{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;padding:10px}
  .h-sin .h-t:nth-child(n+5){display:none}
  .h-owl{width:110px;height:110px;bottom:-24px;inset-inline-end:-10px}
  .h-float{font-size:13px;padding:6px 10px}.h-float.f1{top:0}
  .h-cta .btn{flex:1}
}
"""


def tile(name, ava, text, mark='', raise_=False):
    return (f'<div class="h-t{" raise" if raise_ else ""}"><div class="h-p"><span class="h-w">{text}</span>{mark}</div>'
            f'<div class="h-n"><span class="av" data-ava="{ava}"></span>{name}</div></div>')


SCREEN = ('<div class="h-screen" aria-hidden="true"><div class="h-sbar"><span class="dots"><i></i><i></i><i></i></span>'
          '<span class="h-cnt">٢٤ طالبًا</span><span class="h-code">٤٨٢٩١٥</span></div><div class="h-sin">'
          + tile('سارة', 0, '١٢ × ٤ = ٤٨', '<span class="h-ok">✓</span>')
          + tile('عمر', 3, '١٢ × ٤ = ٤٦', '<span class="h-fix">٤٨</span>')
          + tile('ريم', 5, '١٢ × ٤ = ٤٨', '<span class="h-st">ممتاز</span>')
          + tile('يوسف', 1, '٤٠ + ٨ = ٤٨')
          + tile('لين', 8, '١٢ × ٤ =', '<span class="h-hand">✋</span>', True)
          + tile('خالد', 6, '١٢ × ٤ = ٤٨', '<span class="h-ok">✓</span>')
          + '</div></div>')

FEATS = [
    ('board', '#7c5cff', '#5636e0', 'سبورة لكل طالب', 'كل طالب يحل على سبورته، وتشوف حلول الفصل كله قدامك لحظة بلحظة.'),
    ('pen', '#ff6b6b', '#d64545', 'تصحيح بالأحمر', 'افتح سبورة أي طالب وصحّح بالقلم الأحمر أو بختم «ممتاز»، ويوصله فورًا.'),
    ('quiz', '#ff9638', '#d46b12', 'كويز بثلاث طرق', 'سؤال للكل، أو كل طالب بسرعته، أو شد الحبل بين فريقين.'),
    ('ai', '#3fa9f5', '#1d7cc4', 'أسئلة من صورة الدرس', 'صوّر الدرس أو اكتب اسمه، وتطلع لك أسئلة جاهزة تراجعها قبل ما تبدأ.'),
    ('trophy', '#ffc531', '#e39d00', 'نقاط ولوحة صدارة', 'نقاط على كل ختم وإجابة، والخمسة الأوائل فقط على الشاشة حفاظًا على الخصوصية.'),
    ('clist', '#1fc58f', '#11946a', 'فصولي والحضور', 'قائمة أسماء لكل فصل، والطالب يختار اسمه، والحضور يتسجل لوحده.'),
    ('show', '#c86bfa', '#a148d8', 'اعرض أي شيء', 'صورة، صوت، فيديو، يوتيوب، أو باوربوينت وPDF يوصل لكل الطلاب.'),
    ('timer', '#2cc8cc', '#11999e', 'تحكم كامل', 'مؤقت للحل، قفل السبورات، ليزر، وصفحات للسبورة ترجع لها متى ما تحتاج.'),
]


def home(admin, form):
    feats = ''.join(f'<div class="h-f h-rv"><span class="ic" style="--c:{c};--d:{d}">{ICO(i)}</span><b>{t}</b><span>{x}</span></div>' for i, c, d, t, x in FEATS)
    return f"""<section id="home">
  <div class="doodles" aria-hidden="true" id="doodles"></div>
  <nav class="h-nav" id="hNav"><div class="h-wrap gut">
    <div class="h-logo">{LOGO}<span>Board<b>Plus</b></span></div>
    <div class="h-links"><a href="#hFeat">المزايا</a><a href="#hKids">شاشة الطالب</a><a href="#hGames">الألعاب</a><a href="#hSteps">كيف تبدأ</a></div>
    <div class="grow"></div>
    <div class="datechip" id="hDate" aria-live="off"></div><button class="langbtn" id="langHome" type="button"></button>
    <button class="btn pri" type="button" id="hNavGo">دخول المعلم</button>
  </div></nav>

  <header class="h-hero"><div class="h-wrap gut">
    <div class="h-copy">
      <span class="h-badge"><i>مجاني</i> لكل معلم ومعلمة</span>
      <h1 class="h-h1">حصة تفاعلية <span class="hl">يحبها طلابك</span></h1>
      <p class="h-lead">كل طالب يحل على سبورته وأنت تشوف الكل وتصحح مباشرة. كويزات وألعاب ونقاط تخلي الحصة ممتعة، حضوريًا أو أونلاين.</p>
      <div class="h-cta"><button class="btn pri big" type="button" id="heroTeacher"><span>ابدأ كمعلم مجانًا</span></button><button class="btn big h-ghost" type="button" id="heroStudent">عندي كود الحصة 🚀</button></div>
      <ul class="h-trust"><li>بدون بطاقة دفع</li><li>الطلاب بدون حسابات</li><li>عربي وإنجليزي</li></ul>
    </div>
    <div class="h-pic">
      <div class="h-owl" id="hOwl" aria-hidden="true"></div>
      {SCREEN}
      <div class="h-float f1" aria-hidden="true">✍️ تصحيح مباشر</div>
      <div class="h-float f2" aria-hidden="true">{STAR}+١ نقطة</div>
      <div class="h-float f3" aria-hidden="true">✋ لين رفعت يدها</div>
    </div>
  </div></header>

  <section class="h-sec h-start" id="hStart"><div class="h-wrap gut">
    <div class="h-head h-rv"><span class="h-kicker">ابدأ الآن</span><h2 class="h-h2">معلم أو طالب؟</h2></div>
    <div class="h-cards">
    {admin}
    {form}
    </div>
  </div></section>

  <section class="h-sec" id="hFeat"><div class="h-wrap gut">
    <div class="h-head h-rv"><span class="h-kicker">كل شي في مكان واحد</span><h2 class="h-h2">كل اللي تحتاجه في الحصة</h2><p class="h-sub">من السؤال الأول إلى لوحة الصدارة، بدون ما تنتقل بين مواقع.</p></div>
    <div class="h-feat">{feats}</div>
  </div></section>

  <section class="h-sec" id="hKids" style="background:linear-gradient(180deg,#fbfaff,#f3efff)"><div class="h-wrap gut h-split">
    <div class="h-phone h-rv" aria-hidden="true"><div class="scr">
      <div class="row"><div class="me"><span data-ava="4"></span>ليان</div><div class="pts">{STAR}٧</div></div>
      <div class="bd"><span class="h-w">٩٦ ÷ ٤ = ٢٤</span></div>
      <div class="tray"><i></i><i></i><i></i><i></i><i></i></div>
      <div class="card2"><div class="a" id="hMon"></div><b>برافو يا ليان!</b><small>المعلم صحّح إجابتك ✓</small></div>
    </div></div>
    <div class="h-rv">
      <span class="h-kicker">للطلاب</span>
      <h2 class="h-h2">شاشة يحبها الطالب من أول دخول</h2>
      <ul class="h-list">
        <li><span><b>يدخل بالكود أو QR</b> بدون حساب، ويختار صاحبه من شخصيات كيوت.</span></li>
        <li><span><b>يحتفل معك</b> كل ما ختمت على إجابته، ويجمع نقاط يشوفها تكبر.</span></li>
        <li><span><b>يرفع يده</b> بضغطة، ويسجل صوته أو فيديو يشرح حله.</span></li>
        <li><span><b>أصوات خفيفة</b> يتحكم فيها، وتصميم يناسب الجوال والآيباد.</span></li>
      </ul>
    </div>
  </div></section>

  <section class="h-sec" id="hGames"><div class="h-wrap gut">
    <div class="h-head h-rv"><span class="h-kicker">الألعاب</span><h2 class="h-h2">راجع الدرس وهم يلعبون</h2><p class="h-sub">حوّل أسئلتك لمسابقة خلال ثواني، والطلاب يلعبون من أجهزتهم.</p></div>
    <div class="h-games">
      <div class="h-g h-rv" style="background:linear-gradient(135deg,#ff7a7a,#7c5cff);--d:#5636e0"><span class="em">🪢</span><b>شد الحبل</b><span>فريقان، وكل إجابة صحيحة تشد الحبل لفريقك.</span></div>
      <div class="h-g h-rv" style="background:linear-gradient(135deg,#3fa9f5,#1fc58f);--d:#11946a"><span class="em">🏁</span><b>كل طالب بسرعته</b><span>كل طالب يحل الأسئلة بترتيبه، والأسرع والأدق يتصدر.</span></div>
      <div class="h-g h-rv" style="background:linear-gradient(135deg,#ffb23e,#ff7a3d);--d:#d46b12"><span class="em">🏆</span><b>كويز للجميع</b><span>سؤال واحد للكل بوقت محدد، والنتائج تظهر لحظيًا.</span></div>
    </div>
  </div></section>

  <section class="h-sec" id="hSteps" style="padding-top:0"><div class="h-wrap gut">
    <div class="h-head h-rv"><span class="h-kicker">سهل جدًا</span><h2 class="h-h2">تبدأ أول حصة خلال دقيقة</h2></div>
    <ol class="h-steps">
      <li class="h-rv"><b>سجّل بحساب Google</b><span>بدون نماذج ولا بطاقة.</span></li>
      <li class="h-rv"><b>اعرض الكود أو QR</b><span>الطلاب يدخلون من جوالاتهم بأسمائهم.</span></li>
      <li class="h-rv"><b>اكتب السؤال وصحّح</b><span>الحلول توصلك لحظة بلحظة.</span></li>
    </ol>
  </div></section>

  <section class="h-sec" style="padding-top:0"><div class="h-wrap gut">
    <div class="h-band h-rv"><div><h2>جاهز تخلي حصتك ممتعة؟</h2><p>مجاني بالكامل، ويشتغل على أي جهاز.</p><button class="btn big" type="button" id="heroTeacher2">ابدأ كمعلم مجانًا</button></div><div class="bo" id="hOwl2" aria-hidden="true"></div></div>
  </div></section>
  <footer class="h-foot gut"><div class="h-logo">{LOGO}<span>Board<b>Plus</b></span></div>فكرة وتطوير أ. محمد رجب</footer>
</section>

"""


JS = r"""
/* ======================= theme: home and teacher touches ======================= */
(function themeInit() {
  // home: buddies in the product picture, the owl, sticky nav, reveal on scroll
  document.querySelectorAll('#home [data-ava]').forEach(el => { const i = +el.dataset.ava; el.innerHTML = KID_AVA.svg(i); el.style.background = KID_AVA.color(i)[2] });
  const homeAnims = () => { if ($('#home').hidden) return; ['hOwl', 'hOwl2'].forEach(id => { const e = $('#' + id); if (e && !e._kl) kidLottie(e, 'owl') }); const m = $('#hMon'); if (m && !m._kl) kidLottie(m, 'monster') };
  setTimeout(homeAnims, 400);
  const nav = $('#hNav');
  addEventListener('scroll', () => nav.classList.toggle('stuck', scrollY > 8), { passive: true });
  const io = 'IntersectionObserver' in window ? new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target) } }), { rootMargin: '0px 0px -8% 0px' }) : null;
  document.querySelectorAll('.h-rv').forEach((el, i) => { el.style.transitionDelay = (i % 4) * 70 + 'ms'; io ? io.observe(el) : el.classList.add('in') });
  const g = kGS();
  if (g) {
    g.from('.h-copy > *', { y: 26, opacity: 0, duration: .7, stagger: .09, ease: 'back.out(1.5)', delay: .1 });
    g.from('.h-screen', { y: 40, opacity: 0, rotation: -4, duration: .9, ease: 'back.out(1.3)', delay: .2 });
    g.from('.h-sin .h-t', { scale: .6, opacity: 0, duration: .5, stagger: .07, ease: 'back.out(2)', delay: .5 });
    document.querySelectorAll('.h-float').forEach((f, i) => { g.from(f, { scale: 0, opacity: 0, duration: .5, ease: 'back.out(2.4)', delay: 1 + i * .25 }); g.to(f, { y: i % 2 ? 8 : -8, duration: 2.4 + i * .4, yoyo: true, repeat: -1, ease: 'sine.inOut', delay: 1.6 }) });
  }
  // start cards: both visible; buttons scroll to them
  $('#adminCard').hidden = false;
  const toT = () => { $('#adminCard').scrollIntoView({ behavior: 'smooth', block: 'center' }); setTimeout(() => $('#gSign').focus({ preventScroll: true }), 450); const k = kGS(); k && k.fromTo('#adminCard', { scale: .96 }, { scale: 1, duration: .6, ease: 'elastic.out(1,.4)', delay: .35 }) };
  $('#toTeacher').onclick = () => { kjClose(); $('#adminCard').hidden = false; toT() };
  $('#toStudent').onclick = () => kjOpen();
  $('#ktTeacher').onclick = toT;
  $('#heroTeacher').onclick = toT; $('#hNavGo').onclick = toT; $('#heroTeacher2').onclick = toT;
  document.querySelectorAll('.h-links a').forEach(a => a.onclick = e => { e.preventDefault(); const t = $(a.getAttribute('href')); t && t.scrollIntoView({ behavior: 'smooth', block: 'start' }) });
  const show1 = show; show = function (id) { show1(id); if (id === 'home') setTimeout(homeAnims, 50) };
})();
function stuAva(card, info) {
  const av = card.querySelector('.sav'); if (!av) return; const k = info.ava == null ? 'n:' + (info.name || '').trim()[0] : 'a:' + info.ava;
  if (av.dataset.k === k) return; av.dataset.k = k;
  if (info.ava == null || isNaN(+info.ava)) { av.textContent = (info.name || '؟').trim()[0] || '؟'; av.style.removeProperty('--t') }
  else { av.innerHTML = KID_AVA.svg(+info.ava); av.style.setProperty('--t', KID_AVA.color(+info.ava)[2]) }
}

"""

I18N_ADD = {
    "المزايا": "Features", "شاشة الطالب": "Student screen", "الألعاب": "Games", "كيف تبدأ": "How to start", "دخول المعلم": "Teacher sign-in",
    "مجاني": "Free", "لكل معلم ومعلمة": "for every teacher", "حصة تفاعلية": "Interactive lessons", "يحبها طلابك": "your students love",
    "كل طالب يحل على سبورته وأنت تشوف الكل وتصحح مباشرة. كويزات وألعاب ونقاط تخلي الحصة ممتعة، حضوريًا أو أونلاين.": "Every student solves on their own board while you see everyone and correct live. Quizzes, games and points make class fun, in person or online.",
    "عندي كود الحصة 🚀": "I have a class code 🚀", "بدون بطاقة دفع": "No card needed", "الطلاب بدون حسابات": "Students need no accounts", "عربي وإنجليزي": "Arabic and English",
    "٢٤ طالبًا": "24 students", "✍️ تصحيح مباشر": "✍️ Live correction", "+١ نقطة": "+1 point", "✋ لين رفعت يدها": "✋ Lin raised her hand",
    "ابدأ الآن": "Start now", "معلم أو طالب؟": "Teacher or student?", "كل شي في مكان واحد": "All in one place", "كل اللي تحتاجه في الحصة": "Everything you need in class",
    "من السؤال الأول إلى لوحة الصدارة، بدون ما تنتقل بين مواقع.": "From the first question to the leaderboard, without jumping between sites.",
    "سبورة لكل طالب": "A board for every student", "كل طالب يحل على سبورته، وتشوف حلول الفصل كله قدامك لحظة بلحظة.": "Each student solves on their own board, and you see the whole class live.",
    "تصحيح بالأحمر": "Red-pen correction", "افتح سبورة أي طالب وصحّح بالقلم الأحمر أو بختم «ممتاز»، ويوصله فورًا.": "Open any student's board and correct in red or stamp it, and they see it instantly.",
    "كويز بثلاث طرق": "Quizzes three ways", "سؤال للكل، أو كل طالب بسرعته، أو شد الحبل بين فريقين.": "One question for all, everyone at their own pace, or tug of war between two teams.",
    "أسئلة من صورة الدرس": "Questions from a lesson photo", "صوّر الدرس أو اكتب اسمه، وتطلع لك أسئلة جاهزة تراجعها قبل ما تبدأ.": "Snap the lesson or type its name and get ready questions to review first.",
    "نقاط ولوحة صدارة": "Points and leaderboard", "نقاط على كل ختم وإجابة، والخمسة الأوائل فقط على الشاشة حفاظًا على الخصوصية.": "Points for every stamp and answer; only the top five on screen for privacy.",
    "فصولي والحضور": "My classes and attendance", "قائمة أسماء لكل فصل، والطالب يختار اسمه، والحضور يتسجل لوحده.": "A name list per class; students pick their name and attendance records itself.",
    "اعرض أي شيء": "Show anything", "صورة، صوت، فيديو، يوتيوب، أو باوربوينت وPDF يوصل لكل الطلاب.": "Images, audio, video, YouTube, PowerPoint or PDF to every student.",
    "تحكم كامل": "Full control", "مؤقت للحل، قفل السبورات، ليزر، وصفحات للسبورة ترجع لها متى ما تحتاج.": "A timer, board lock, laser and pages you can go back to anytime.",
    "للطلاب": "For students", "شاشة يحبها الطالب من أول دخول": "A screen students love from the first visit",
    "يدخل بالكود أو QR": "Joins with a code or QR", "بدون حساب، ويختار صاحبه من شخصيات كيوت.": "with no account, and picks a cute buddy.",
    "يحتفل معك": "Celebrates with you", "كل ما ختمت على إجابته، ويجمع نقاط يشوفها تكبر.": "every time you stamp an answer, and watches their points grow.",
    "يرفع يده": "Raises a hand", "بضغطة، ويسجل صوته أو فيديو يشرح حله.": "in one tap, and records voice or video to explain.",
    "أصوات خفيفة": "Gentle sounds", "يتحكم فيها، وتصميم يناسب الجوال والآيباد.": "they control, on a design made for phones and iPads.",
    "برافو يا ليان!": "Bravo, Layan!", "المعلم صحّح إجابتك ✓": "Your teacher marked your answer ✓",
    "راجع الدرس وهم يلعبون": "Review the lesson while they play", "حوّل أسئلتك لمسابقة خلال ثواني، والطلاب يلعبون من أجهزتهم.": "Turn your questions into a game in seconds; students play on their devices.",
    "فريقان، وكل إجابة صحيحة تشد الحبل لفريقك.": "Two teams; every right answer pulls the rope your way.",
    "كل طالب بسرعته": "Everyone at their pace", "كل طالب يحل الأسئلة بترتيبه، والأسرع والأدق يتصدر.": "Each student works through the questions; the fastest and most accurate lead.",
    "كويز للجميع": "Quiz for all", "سؤال واحد للكل بوقت محدد، والنتائج تظهر لحظيًا.": "One timed question for everyone, with live results.",
    "سهل جدًا": "Super easy", "جاهز تخلي حصتك ممتعة؟": "Ready to make class fun?", "مجاني بالكامل، ويشتغل على أي جهاز.": "Completely free, on any device.",
    "بانتظار الطلاب": "Waiting for students",
}


def apply(s, rep):
    s = rep(s, '<meta name="theme-color" content="#1f4fd8">', '<meta name="theme-color" content="#7c5cff">')
    s = s.replace('\n</style>', '\n' + CSS.strip() + '\n</style>', 1)
    # the new home, keeping the real teacher card and the join form (which the kid page takes)
    a = s.index('<div class="card" id="adminCard" hidden>'); e = '<button class="switch" type="button" id="toStudent">→ أنا طالب</button>\n    </div>'
    b = s.index(e, a) + len(e); admin = s[a:b]
    a = s.index('<div class="card kj-teaser" id="kidTeaser">'); b = s.index('</form>', a) + len('</form>'); student = s[a:b]
    a = s.index('<section id="home">'); b = s.index('<!-- ================= TEACHER', a)
    s = s[:a] + home(admin, student) + s[b:]
    # teacher: buddies on the student cards, the owl while the class is empty
    s = rep(s, '<div class="nm"><i class="st"></i><span></span>', '<div class="nm"><i class="st"></i><b class="sav"></b><span></span>')
    s = rep(s, "s.card.querySelector('.st').classList.toggle('on', !!info.online);", "s.card.querySelector('.st').classList.toggle('on', !!info.online); stuAva(s.card, info);")
    s = rep(s, "e.innerHTML = `<b>بانتظار دخول الطلاب</b>", "e.innerHTML = `<div class=\"eowl\"></div><b>بانتظار دخول الطلاب</b>")
    s = rep(s, "e.onclick = ev => { const a = ev.target.closest('[data-a]');", "kidLottie(e.querySelector('.eowl'), 'owl'); e.onclick = ev => { const a = ev.target.closest('[data-a]');")
    s = rep(s, '/* ======================= boot ======================= */', JS + '/* ======================= boot ======================= */')
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(I18N_ADD, ensure_ascii=False)[1:-1] + ',')
    return s
