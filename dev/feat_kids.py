"""BoardPlus kids: the student's whole screen in a cheerful, ClassDojo-like style.
  * Joining: a full-screen kid page (owl mascot in Lottie, six code boxes, name, and a monster buddy to pick).
    The home page keeps a small «أنا طالب» card that opens it; links/QR (#j-CODE) open it directly.
  * The student's board: the buddy and name in the header, a gold points capsule that counts up with a flying star,
    a big yellow hand button, a crayon-tray toolbar, a framed board on a playful wall.
  * Moments: a welcome card, a cheering monster with confetti when the teacher stamps the answer, a soft ding on a
    correction, a sleeping panda while the board is locked, a trophy / thumbs-up in the quiz, and a goodbye card.
  * Sounds are short Web-Audio blips (no files) with a mute button the student controls.
Fonts: Baloo Bhaijaan 2 (headings) + Tajawal (text). Libraries are self-hosted in public/kid (GSAP, lottie_light).
Every existing id and behaviour stays; this only restyles and adds hooks."""
import json, pathlib
D = pathlib.Path(__file__).resolve().parent
AVA_JS = (D / 'kid_ava.js').read_text()

STAR = ('<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 4.5l5.6 12 13 1.5-9.7 8.9 2.6 12.9L24 33.2l-11.5 6.6 2.6-12.9-9.7-8.9 13-1.5z" '
        'fill="#ffd23f" stroke="#f0a500" stroke-width="2.6" stroke-linejoin="round"/><path d="M17 17.5l3.5-.4" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".8"/></svg>')
LOGO = ('<svg class="bulogo" viewBox="0 0 48 48" aria-hidden="true"><rect x="2" y="2" width="44" height="44" rx="13" fill="#7c5cff"/>'
        '<rect x="9.5" y="11" width="29" height="20" rx="3.5" fill="#fff"/><path d="M15 21.5l4.6 4.2L29 15.6" fill="none" stroke="#ff5a6a" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="12" y="34.5" width="24" height="4" rx="2" fill="#fff" opacity=".55"/><rect x="31" y="32.6" width="9" height="7.8" rx="2" fill="#ffd23f"/></svg>')

# faint shapes on the classroom wall
WALL = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='260' height='260' viewBox='0 0 260 260'%3E"
        "%3Cg fill='none' stroke-width='3' stroke-linecap='round' stroke-linejoin='round' opacity='.55'%3E"
        "%3Cpath d='M30 40h18M39 31v18' stroke='%23c9bcff'/%3E%3Ccircle cx='200' cy='46' r='9' stroke='%23ffd27a'/%3E"
        "%3Cpath d='M118 120l9 16h-18z' stroke='%23a6e9cf'/%3E%3Cpath d='M214 170l12 12M226 170l-12 12' stroke='%23ffb3bd'/%3E"
        "%3Cpath d='M52 196l3.6 7.4 8.1.9-6 5.6 1.7 8-7.4-4.2-7.4 4.2 1.7-8-6-5.6 8.1-.9z' stroke='%23ffd27a'/%3E"
        "%3Crect x='150' y='224' width='16' height='16' rx='4' stroke='%23b8dcff'/%3E%3Cpath d='M96 30c6-6 12 6 18 0' stroke='%23b8dcff'/%3E"
        "%3C/g%3E%3C/svg%3E\")")

CSS = r"""
/* ===================== kids: the student's world ===================== */
:root{--k-f1:"Baloo Bhaijaan 2","Tajawal","IBM Plex Sans Arabic",system-ui,sans-serif;--k-f2:"Tajawal","Baloo Bhaijaan 2","IBM Plex Sans Arabic",system-ui,sans-serif;
  --k-ink:#2b2d55;--k-mut:#6b6f9a;--k-grape:#7c5cff;--k-grape-d:#5636e0;--k-grape-s:#efeaff;--k-sun:#ffc83d;--k-sun-d:#e39d00;--k-mint:#20c690;--k-coral:#ff6b6b;--k-sky:#3fa9f5;--k-ring:#e4dcff}
body.kid,.kj{--wall:#eef3ff;--surface:#fff;--surface-2:#f5f3ff;--ink:#2b2d55;--muted:#6b6f9a;--line:#e6e2f7;--accent:#7c5cff;--accent-2:#5636e0;--accent-soft:#efeaff;--accent-ink:#fff;
  --ok:#16b37c;--ok-soft:#e2f8ef;--red:#ff5a6a;--red-soft:#ffe8ea;--hand:#ffc83d;--hand-soft:#fff3cc;--paper:#fff;--f-display:var(--k-f1);color-scheme:light}
body.kid{font-family:var(--k-f2)}
.kava{display:block;width:100%;height:auto;overflow:visible}
.kava .kl{animation:kblink 5.5s infinite}
@keyframes kblink{0%,92%,100%{transform:scale(1,0)}95%{transform:scale(1,1)}}
.kbtn{border:0;cursor:pointer;font:inherit;display:inline-grid;place-items:center}

/* ---------- the kid join page ---------- */
.kj{position:fixed;inset:0;z-index:40;overflow:auto;overscroll-behavior:contain;color:var(--k-ink);font-family:var(--k-f2);
  background:radial-gradient(900px 520px at 90% -8%,#ffe7c2 0,transparent 62%),radial-gradient(800px 560px at -10% 108%,#d6f8e8 0,transparent 58%),linear-gradient(160deg,#e7f0ff 0%,#efe8ff 100%)}
.kj[hidden]{display:none}
body.kidj{overflow:hidden}
.kj-sky{position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:0}
.kj-sky i{position:absolute;display:block;font-style:normal;font-family:var(--k-f1);font-weight:800;line-height:1;opacity:.85;will-change:transform}
.kj-sky i svg{display:block;width:100%;height:100%}
.kj-top{position:relative;z-index:2;display:flex;align-items:center;gap:12px;padding-block:16px 6px;max-width:1120px;margin:0 auto}
.kj-top .word{font-family:var(--k-f1);font-size:24px;font-weight:800;color:var(--k-ink);display:flex;align-items:center;gap:8px}
.kj-top .word b{color:var(--k-grape)}
.kj-top .bulogo{width:34px;height:34px}
.kj-back{height:44px;padding:0 16px;border-radius:999px;background:#fff;color:var(--k-ink);font-family:var(--k-f1);font-weight:700;font-size:16px;box-shadow:0 3px 0 var(--k-ring);display:inline-flex;align-items:center;gap:6px}
.kj-back:active{transform:translateY(2px);box-shadow:0 1px 0 var(--k-ring)}
.ksnd{width:44px;height:44px;border-radius:50%;background:#fff;color:var(--k-grape);box-shadow:0 3px 0 var(--k-ring);flex:none}
.ksnd svg{width:22px;height:22px}
.ksnd.off{color:#a3a6c8}
.kj-top .grow{flex:1}
.kj-main{position:relative;z-index:2;max-width:1120px;margin:0 auto;display:grid;grid-template-columns:minmax(0,1fr) minmax(330px,460px);gap:clamp(18px,4vw,56px);align-items:center;padding-block:4px 40px;min-height:calc(100% - 80px)}
.kj-hero{display:flex;flex-direction:column;align-items:center;text-align:center;gap:4px}
.kj-h1{margin:0;font-family:var(--k-f1);font-weight:800;font-size:clamp(30px,4.4vw,54px);line-height:1.15;color:var(--k-ink);text-wrap:balance}
.kj-h1 span{color:var(--k-grape)}
.kj-bubble{position:relative;margin-top:18px;background:#fff;border-radius:24px;padding:12px 22px;font-family:var(--k-f1);font-weight:700;font-size:clamp(18px,2.1vw,24px);color:var(--k-ink);box-shadow:0 4px 0 var(--k-ring),0 20px 40px -24px rgba(76,52,180,.45);max-width:28ch;text-wrap:balance}
.kj-bubble::after{content:"";position:absolute;bottom:-12px;left:50%;width:24px;height:24px;background:#fff;transform:translateX(-50%) rotate(45deg);border-radius:4px;box-shadow:4px 4px 0 var(--k-ring)}
.kj-bubble b{color:var(--k-grape)}
.kj-owl{width:min(330px,62vw);aspect-ratio:1;margin-top:-6px}
.kj-owl:empty{background:no-repeat center/56% url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Ccircle cx='5' cy='5' r='4' fill='%23e8e2ff'/%3E%3C/svg%3E")}
#kjoin #joinCard{position:relative;background:#fff;border:0;border-radius:30px;padding:26px 24px 22px;box-shadow:0 7px 0 var(--k-ring),0 40px 70px -34px rgba(76,52,180,.55);display:flex;flex-direction:column;gap:14px;max-width:none;margin:0}
#kjoin #joinCard .welcome,#kjoin #joinCard .hx-tape,#kjoin #joinCard .tlink{display:none}
#kjoin #joinCard .field{margin:0}
#kjoin #joinCard label{display:block;font-family:var(--k-f1);font-weight:800;font-size:18px;color:var(--k-ink);margin:0 0 8px}
#kjoin #joinCard label .n{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--k-grape);color:#fff;font-size:15px;margin-inline-end:8px;vertical-align:1px}
.kj-code{position:relative;direction:ltr}
.kj-dig{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;pointer-events:none}
.kj-dig i{display:grid;place-items:center;height:64px;border-radius:16px;background:#f5f2ff;border:2.5px solid #e6dfff;font-style:normal;font-family:var(--k-f1);font-weight:800;font-size:34px;color:var(--k-ink);transition:border-color .15s,background .15s,box-shadow .15s}
.kj-dig i.fill{background:#fff;border-color:#cbbdff}
.kj-dig i.cur{border-color:var(--k-grape);box-shadow:0 0 0 4px #e6deff;background:#fff}
.kj-dig i.cur:empty::after{content:"";width:3px;height:30px;border-radius:2px;background:var(--k-grape);animation:kcaret 1s steps(2) infinite}
@keyframes kcaret{50%{opacity:0}}
#kjoin #jCode{position:absolute;inset:0;width:100%;height:100%;opacity:0;font-size:16px;border:0;padding:0;cursor:text;letter-spacing:0}
#kjoin .jteacher{margin-top:10px;border:0;background:#e5f9f0;border-radius:18px;padding:8px 12px;font-family:var(--k-f1);font-weight:700;font-size:16px;color:var(--k-ink);box-shadow:inset 0 0 0 2px #a8ebcf}
#kjoin .jteacher img{width:38px;height:38px;box-shadow:0 0 0 3px #fff}
#kjoin .jteacher i{width:28px;height:28px;border-radius:50%;background:var(--k-mint);color:#fff;display:grid;place-items:center;font-size:15px}
#kjoin .jteacher.bad{background:#fff0f1;box-shadow:inset 0 0 0 2px #ffc7cd}
.kj-namerow{position:relative}
#kjoin #jName{height:58px;border-radius:18px;border:2.5px solid #e6dfff;background:#f8f6ff;font-family:var(--k-f2);font-weight:700;font-size:19px;color:var(--k-ink);padding-inline:16px 64px;width:100%}
#kjoin #jName:focus{border-color:var(--k-grape);background:#fff;box-shadow:0 0 0 4px #e6deff}
#kjoin #jName::placeholder{color:#a3a6c8;font-weight:500}
.kj-me{position:absolute;inset-inline-end:8px;top:6px;width:46px;height:46px;border-radius:14px;background:var(--t,#efeaff);display:grid;place-items:center;pointer-events:none}
.kj-me .kava{width:42px}
.kj-namerow:has(#jName[hidden]) .kj-me{display:none}
.kj-avas{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px}
.kja{position:relative;aspect-ratio:1;border-radius:18px;border:0;background:var(--t);cursor:pointer;padding:4px;display:grid;place-items:center;box-shadow:inset 0 0 0 2.5px transparent;transition:box-shadow .15s,transform .15s}
.kja .kava{width:100%}
.kja:hover{transform:translateY(-2px)}
.kja.on{box-shadow:inset 0 0 0 3px var(--k-grape),0 4px 0 #d9ceff}
.kja.on::after{content:"✓";position:absolute;top:-6px;inset-inline-end:-6px;width:22px;height:22px;border-radius:50%;background:var(--k-grape);color:#fff;font-size:13px;font-weight:800;display:grid;place-items:center;box-shadow:0 0 0 2.5px #fff}
#kjoin .err{color:#e23d50;font-weight:700;font-size:15px;margin:0;min-height:0}
#kjoin .err:empty{display:none}
#kjoin #jGo{height:62px;border:0;border-radius:20px;background:linear-gradient(#8f74ff,#6c4cff);color:#fff;font-family:var(--k-f1);font-weight:800;font-size:22px;box-shadow:0 6px 0 var(--k-grape-d),0 22px 34px -18px rgba(86,54,224,.75);letter-spacing:0;margin-top:2px}
#kjoin #jGo:hover{filter:brightness(1.06)}
#kjoin #jGo:active{transform:translateY(4px);box-shadow:0 2px 0 var(--k-grape-d)}
#kjoin #jGo:disabled{filter:grayscale(.4) brightness(1.05);transform:none}
#kjoin .jlist .jlh{font-family:var(--k-f1);font-weight:700;color:var(--k-mut)}
#kjoin .jn{border:0;border-radius:16px;background:#f5f2ff;font-family:var(--k-f1);font-weight:700;font-size:16px;min-height:50px;box-shadow:inset 0 0 0 2px #e6dfff}
#kjoin .jn.on{background:var(--k-grape);color:#fff;box-shadow:0 4px 0 var(--k-grape-d)}
.kj-foot{text-align:center;color:var(--k-mut);font-size:13.5px;margin:2px 0 0}
@media (max-width:860px){
  .kj-main{grid-template-columns:1fr;gap:4px;padding-block:0 28px;min-height:0}
  .kj-hero{flex-direction:row;flex-wrap:wrap;justify-content:center;gap:0 8px}
  .kj-h1{width:100%;font-size:clamp(26px,7vw,36px)}
  .kj-owl{width:128px;margin:0;order:1}
  .kj-bubble{order:2;margin:0;font-size:17px;padding:10px 16px;max-width:calc(100% - 140px);text-align:start}
  .kj-bubble::after{bottom:auto;top:50%;left:-9px;transform:translateY(-50%) rotate(45deg);box-shadow:-3px 3px 0 var(--k-ring)}
  [dir="ltr"] .kj-bubble::after{left:-9px}
  [dir="rtl"] .kj-bubble::after{left:auto;right:-9px;box-shadow:3px -3px 0 var(--k-ring)}
}
@media (max-width:520px){
  .kj-top{padding-block:12px 2px}.kj-top .word span{display:none}
  #kjoin #joinCard{padding:20px 16px 18px;border-radius:26px}
  .kj-dig{gap:6px}.kj-dig i{height:54px;font-size:28px;border-radius:14px}
  .kj-avas{grid-template-columns:repeat(4,minmax(0,1fr))}
}
/* the home page keeps a small student card that opens the kid page */
#home #joinCard{display:none!important}
.kj-teaser{text-align:center;align-items:center;display:flex;flex-direction:column;gap:10px}
.kj-teaser[hidden]{display:none}
.kt-avas{display:flex;justify-content:center;margin:2px 0 4px}
.kt-avas span{width:68px;height:68px;border-radius:22px;display:grid;place-items:center;margin-inline:-6px;box-shadow:0 0 0 4px var(--surface)}
.kt-avas span:nth-child(2){transform:translateY(-8px) scale(1.12);z-index:1}
.kt-avas .kava{width:60px}
.kj-teaser h2{margin:0;font-size:24px}
.kj-teaser p{margin:0;color:var(--muted)}
.kj-teaser .btn.big{width:100%;margin-top:4px}

/* ---------- the student's board ---------- */
body.kid #student{background:linear-gradient(165deg,#e8f0ff 0%,#f1eaff 55%,#fff2e2 100%)}
:root body.kid #student .stage{background-color:transparent;background-image:""" + WALL + r""";background-size:260px 260px}
body.kid #student .top{background:transparent;border:0;box-shadow:none;padding-block:10px 4px;gap:10px;flex-wrap:nowrap}
.kme{display:flex;align-items:center;gap:10px;min-width:0;background:#fff;border-radius:999px;padding:5px 18px 5px 5px;box-shadow:0 3px 0 var(--k-ring)}
[dir="rtl"] .kme{padding:5px 5px 5px 18px}
.kme-ava{width:48px;height:48px;border-radius:50%;background:var(--t,#efeaff);display:grid;place-items:center;flex:none;overflow:visible}
.kme-ava .kava{width:46px;margin-top:-2px}
body.kid .who-s b{font-family:var(--k-f1);font-weight:800;font-size:18px;color:var(--k-ink)}
body.kid .who-s>span{display:flex;align-items:center;gap:5px;font-size:12.5px;color:var(--k-mut);font-weight:700;white-space:nowrap;overflow:hidden}
body.kid #student .brand{display:inline-flex}
body.kid #student .brand .ava{width:18px;height:18px;border-radius:50%;box-shadow:none}
body.kid .sclock{background:#fff;border-radius:16px;padding:4px 12px;box-shadow:0 3px 0 var(--k-ring)}
body.kid .sclock b{font-family:var(--k-f1);font-size:15px}
body.kid #sPts,body.kid #qsPts{display:none}
.kpts{display:inline-flex;align-items:center;gap:6px;height:44px;padding:0 14px 0 8px;border-radius:999px;background:linear-gradient(#ffdc6b,#ffc531);box-shadow:0 4px 0 var(--k-sun-d);color:#5b3b00;font-family:var(--k-f1);font-weight:800;font-size:21px;flex:none;position:relative}
[dir="rtl"] .kpts{padding:0 8px 0 14px}
.kpts svg{width:30px;height:30px;filter:drop-shadow(0 1px 0 rgba(160,100,0,.35))}
.kpts b{font-variant-numeric:tabular-nums;min-width:1ch;text-align:center}
.kplus{position:fixed;z-index:85;pointer-events:none;font-family:var(--k-f1);font-weight:800;font-size:24px;color:#e39d00;text-shadow:0 2px 0 #fff,0 0 8px #fff}
.kstar{position:fixed;left:0;top:0;width:48px;height:48px;z-index:86;pointer-events:none}
.kstar svg{width:100%;height:100%}
body.kid #sConn{background:#fff;border:0;box-shadow:0 3px 0 var(--k-ring);font-weight:700;height:36px}
body.kid #student .timer{font-family:var(--k-f1);font-weight:800;font-size:18px;border-radius:999px;padding:4px 14px;background:#fff;color:var(--k-grape);box-shadow:0 3px 0 var(--k-ring)}
body.kid #sHand{height:46px;padding:0 18px;border:0;border-radius:16px;background:linear-gradient(#ffd863,#ffc229);color:#5b3b00;box-shadow:0 4px 0 var(--k-sun-d);font-family:var(--k-f1);font-weight:800;font-size:17px;gap:6px;flex:none}
body.kid #sHand .ico{width:22px;height:22px;stroke-width:2.2;transform-origin:50% 90%}
body.kid #sHand:active{transform:translateY(3px);box-shadow:0 1px 0 var(--k-sun-d)}
body.kid #sHand.on{background:linear-gradient(#ff8e7e,#ff6262);color:#fff;box-shadow:0 4px 0 #d64545;animation:khand 1.5s ease-out infinite}
body.kid #sHand.on .ico{animation:kwave 1.1s ease-in-out infinite}
@keyframes khand{0%{box-shadow:0 4px 0 #d64545,0 0 0 0 rgba(255,98,98,.5)}100%{box-shadow:0 4px 0 #d64545,0 0 0 18px rgba(255,98,98,0)}}
@keyframes kwave{0%,100%{transform:rotate(0)}25%{transform:rotate(-18deg)}75%{transform:rotate(14deg)}}
:root body.kid #student .board{border-radius:22px;box-shadow:0 0 0 8px #fff,0 0 0 11px #dcd2ff,0 32px 54px -26px rgba(76,52,180,.55)}
:root body.kid #student .board.pulse{box-shadow:0 0 0 8px #fff,0 0 0 11px var(--red),0 32px 54px -26px rgba(255,90,106,.6)}
:root body.kid .tb{background:#fff;border:0;border-radius:24px;padding:7px 10px;gap:4px;box-shadow:0 6px 0 var(--k-ring),0 26px 40px -24px rgba(76,52,180,.5)}
body.kid .tb button{width:42px;height:42px;border-radius:14px;color:#4b4e7d}
body.kid .tb button:hover{background:#f3efff}
body.kid .tb button[data-t].on{background:linear-gradient(#8f74ff,#6c4cff);color:#fff;box-shadow:0 3px 0 var(--k-grape-d)}
body.kid .tb .ico{width:21px;height:21px}
body.kid .tb .sw{width:30px;height:30px;border:3px solid #fff;box-shadow:0 0 0 2px #e6e2f7;transition:transform .15s}
body.kid .tb button.on .sw{box-shadow:0 0 0 3px var(--k-grape);transform:scale(1.1)}
body.kid .tb .sep{background:#ece9f8;width:2px;border-radius:2px}
body.kid .lockveil{background:rgba(124,92,255,.16);backdrop-filter:blur(3px)}
body.kid .lockveil>div{flex-direction:column;gap:2px;border-radius:26px;padding:10px 26px 18px;font-family:var(--k-f1);font-weight:700;font-size:18px;box-shadow:0 6px 0 var(--k-ring),0 30px 50px -26px rgba(43,45,85,.5);text-align:center;max-width:92%}
body.kid .lockveil>div>svg.ico{display:none}
.kveil-a{display:block;width:150px;height:146px}
body.kid .toast{background:#fff;color:var(--k-ink);font-family:var(--k-f1);font-weight:700;font-size:16px;border-radius:18px;padding:10px 18px;box-shadow:0 5px 0 var(--k-ring),0 24px 40px -22px rgba(76,52,180,.55)}
body.kid .toast.red{color:#d8344a;box-shadow:0 5px 0 #ffd0d6,0 24px 40px -22px rgba(216,52,74,.45)}
body.kid .dlg{border-radius:26px;box-shadow:0 7px 0 var(--k-ring),0 40px 80px -30px rgba(43,45,85,.6)}
body.kid .dlg h3{font-family:var(--k-f1);font-weight:800}
body.kid .btn{font-family:var(--k-f1);font-weight:700;border-radius:14px}
body.kid .btn.pri{background:linear-gradient(#8f74ff,#6c4cff);border:0;box-shadow:0 4px 0 var(--k-grape-d)}
@media (max-width:760px){body.kid .sclock{display:none}}
@media (max-width:640px){
  body.kid #student .top{gap:7px;padding-block:8px 2px}
  .kme{padding:4px 12px 4px 4px;gap:8px}[dir="rtl"] .kme{padding:4px 4px 4px 12px}
  .kme-ava{width:40px;height:40px}.kme-ava .kava{width:38px}
  body.kid .who-s b{font-size:16px}
  body.kid #sConn{padding:0 9px}body.kid #sConn span:last-child{display:none}
  body.kid #sHand{padding:0 12px}body.kid #sHand span{display:none}
  .kpts{height:40px;font-size:19px}.kpts svg{width:26px;height:26px}
  .ksnd{width:40px;height:40px}
  body.kid .tb button{width:38px;height:38px}
}
@media (max-width:400px){body.kid #sConn{display:none}}

/* ---------- moments ---------- */
.kfx{position:fixed;inset:0;z-index:80;pointer-events:none;display:grid;place-items:center;padding:20px}
.kfx-conf{position:absolute;inset:0}
.kfx-card{position:relative;pointer-events:auto;cursor:pointer;display:flex;flex-direction:column;align-items:center;background:#fff;border-radius:32px;padding:0 34px 22px;min-width:250px;max-width:min(420px,92vw);text-align:center;
  box-shadow:0 8px 0 var(--k-ring),0 50px 90px -30px rgba(43,45,85,.6);font-family:var(--k-f1);color:var(--k-ink)}
.kfx-anim{width:190px;height:190px;margin-top:-96px}
.kfx-t{font-weight:800;font-size:32px;line-height:1.2;color:var(--k-grape);text-wrap:balance}
.kfx-s{font-weight:700;font-size:17px;color:var(--k-mut);margin-top:4px;text-wrap:balance}
.kfx.bad .kfx-t{color:#ff8a3d}
@media (min-width:900px){.kfx-card{padding:0 44px 28px;min-width:320px}.kfx-anim{width:250px;height:250px;margin-top:-125px}.kfx-t{font-size:40px}.kfx-s{font-size:19px}}

/* ---------- quiz & leaderboard ---------- */
body.kid #qzStu,body.kid #lbView{background:linear-gradient(165deg,#e8f0ff 0%,#f1eaff 55%,#fff2e2 100%)}
body.kid #qzStu .top,body.kid #lbView .top{background:transparent;border:0;box-shadow:none}
body.kid #qzStu .top{flex-wrap:nowrap;gap:10px}
body.kid #qzStu .qz-t{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block}
body.kid .qz-t{font-family:var(--k-f1);font-weight:800;font-size:19px;background:#fff;border-radius:999px;padding:6px 16px;box-shadow:0 3px 0 var(--k-ring);display:inline-flex;align-items:center;gap:8px;color:var(--k-ink)}
body.kid .qtime{width:60px;height:60px;min-width:0;padding:0;border-radius:50%;display:grid;place-items:center;background:#fff;color:var(--k-grape);box-shadow:inset 0 0 0 5px #e6deff,0 3px 0 var(--k-ring);font-size:26px;font-weight:800}
body.kid .qtime.low{background:var(--k-coral);color:#fff;box-shadow:inset 0 0 0 5px rgba(255,255,255,.35),0 3px 0 #d64545}
:root body.kid #qzStu .qstage{background:transparent}
body.kid #qsBoard{border-radius:22px;box-shadow:0 0 0 7px #fff,0 0 0 10px #dcd2ff,0 26px 44px -26px rgba(76,52,180,.5)}
body.kid #qzStu .opts{background:transparent}
body.kid .opt{--c:#7c5cff;--d:#5636e0;border-radius:22px;min-height:96px;box-shadow:0 7px 0 var(--d);background:linear-gradient(color-mix(in srgb,var(--c) 82%,#fff),var(--c))}
body.kid .opt[data-o="B"]{--c:#ff9638;--d:#d46b12}body.kid .opt[data-o="C"]{--c:#1fc58f;--d:#11946a}body.kid .opt[data-o="D"]{--c:#3fa9f5;--d:#1d7cc4}
body.kid .opt::before{content:"";position:absolute;width:90px;height:90px;border-radius:50%;background:rgba(255,255,255,.16);top:-30px;inset-inline-start:-24px}
body.kid .opt .ol{font-family:var(--k-f1);font-weight:800;font-size:44px;text-shadow:0 3px 0 rgba(0,0,0,.12)}
body.kid .opt:not(:disabled):active{transform:translateY(5px);box-shadow:0 2px 0 var(--d)}
body.kid .opt.chosen{box-shadow:0 7px 0 var(--d),0 0 0 5px #fff,0 0 0 9px var(--k-ink)}
body.kid .opt.right{box-shadow:0 7px 0 var(--d),0 0 0 5px #fff,0 0 0 9px var(--k-mint);animation:kpop .5s cubic-bezier(.3,1.6,.5,1)}
body.kid .opt.wrong{opacity:.55;animation:kshake .45s}
@keyframes kpop{0%{transform:scale(.92)}60%{transform:scale(1.06)}100%{transform:scale(1)}}
@keyframes kshake{0%,100%{transform:translateX(0)}20%{transform:translateX(-8px)}40%{transform:translateX(8px)}60%{transform:translateX(-5px)}80%{transform:translateX(5px)}}
body.kid .qmsg{font-family:var(--k-f1);font-weight:700;font-size:20px;align-self:center;background:#fff;border-radius:999px;padding:6px 20px;box-shadow:0 3px 0 var(--k-ring)}
body.kid .qmsg:empty{display:none}
body.kid .myrank{font-family:var(--k-f1);font-weight:800;font-size:24px;color:var(--k-grape)}
body.kid .lr{border:0;border-radius:18px;box-shadow:0 3px 0 var(--k-ring);padding:10px 16px}
body.kid .lr.me{background:#f1ecff;box-shadow:0 3px 0 #cbbdff,inset 0 0 0 2px var(--k-grape)}
body.kid .lr .lt{font-family:var(--k-f1);font-weight:800;color:var(--k-grape)}
body.kid .pd .pa{font-family:var(--k-f1)}
body.kid .pd .pn,body.kid .pd .pp{font-family:var(--k-f1);font-weight:700}

/* ---------- goodbye ---------- */
body.kid #ended{background:radial-gradient(800px 500px at 90% -10%,#ffe7c2 0,transparent 60%),linear-gradient(160deg,#e7f0ff,#efe8ff)}
body.kid .kend{max-width:440px;width:100%;text-align:center;align-items:center;display:flex;flex-direction:column;gap:8px;border:0;border-radius:32px;padding:0 26px 26px;box-shadow:0 8px 0 var(--k-ring),0 50px 90px -34px rgba(43,45,85,.55);margin-top:90px}
.kend-anim{width:200px;height:200px;margin-top:-100px}
body.kid .kend h2{font-family:var(--k-f1);font-weight:800;font-size:30px;margin:0;color:var(--k-ink)}
body.kid .kend .hint{font-size:17px;font-weight:700}
.kend-pts{display:flex;align-items:center;gap:8px;background:#fff6d6;border-radius:18px;padding:8px 16px;font-family:var(--k-f1);font-weight:800;font-size:19px;color:#7a5200;box-shadow:inset 0 0 0 2px #ffe08a}
.kend-pts[hidden]{display:none}
.kend-pts svg{width:30px;height:30px}
body.kid .kend .btn.big{width:100%;height:58px;font-size:19px;margin-top:6px}
body:not(.kid) .kend-anim{display:none}
"""

KJ_HTML = """<section id="kjoin" class="kj" hidden aria-label="دخول الطالب">
  <div class="kj-sky" id="kjSky" aria-hidden="true"></div>
  <header class="kj-top gut">
    <button class="kbtn kj-back" type="button" id="kjBack"><span aria-hidden="true">→</span> رجوع</button>
    <div class="grow"></div>
    <div class="word">""" + LOGO + """<span>Board<b>Plus</b></span></div>
    <div class="grow"></div>
    <button class="kbtn ksnd" type="button" id="kjSnd"></button>
  </header>
  <div class="kj-main gut">
    <div class="kj-hero">
      <h1 class="kj-h1">يلا نبدأ <span>الحصة!</span></h1>
      <div class="kj-bubble" id="kjSay" aria-live="polite">أهلًا! اكتب كود الحصة 👋</div>
      <div class="kj-owl" id="kjOwl" aria-hidden="true"></div>
    </div>
    <div class="kj-slot" id="kjSlot"></div>
  </div>
</section>
"""

TEASER = """<div class="card kj-teaser" id="kidTeaser">
      <span class="hx-tape" aria-hidden="true"></span>
      <div class="kt-avas" id="ktAvas" aria-hidden="true"></div>
      <h2>أنا طالب</h2>
      <p>عندك كود من معلمك؟ ادخل حصتك من هنا</p>
      <button class="btn pri big" type="button" id="ktGo">ادخل الحصة 🚀</button>
      <div class="tlink"><button type="button" id="ktTeacher">أنا معلم ← دخول بحساب Google</button></div>
    </div>
    """

STUDENT = """<section id="student" class="app" hidden>
  <header class="top gut">
    <div class="kme"><span class="kme-ava" id="kMeAva"></span><div class="who-s"><b id="stName"></b><span><span class="brand"><img class="ava" src="" alt=""></span><span id="stTeacher"></span><span aria-hidden="true">·</span><span class="num" id="stCode"></span></span></div></div>
    <div class="grow"></div>
    <span class="timer" id="sTimer" hidden></span>
    <div class="clock sclock" id="sClock"></div>
    <span class="pill starpill" id="sPts" title="نقاطك">⭐ 0</span>
    <span class="kpts" id="kPts" title="نقاطك">""" + STAR + """<b>0</b></span>
    <button class="kbtn ksnd" type="button" id="kSnd"></button>
    <span class="pill" id="sConn"><span class="dot"></span><span>...</span></span>
    <button class="btn hand" id="sHand"><svg class="ico"><use href="#i-hand"/></svg><span>ارفع يدك</span></button>
  </header>
  <div class="stage"><div id="sBoard"></div></div>
  <div class="tbwrap gut"><div class="tb" id="sTools"></div></div>
</section>

"""

ENDED = """<section id="ended" class="app" hidden>
  <div class="ended gut"><div class="card kend" style="max-width:440px">
    <div class="kend-anim" id="kEndAnim" aria-hidden="true"></div>
    <h2 id="endTitle">انتهت الجلسة</h2><p class="hint" id="endText" style="margin:0">شكرًا لمشاركتك.</p>
    <div class="kend-pts" id="kEndPts" hidden>""" + STAR + """<span></span></div>
    <button class="btn pri big" id="endBack">الرجوع للصفحة الرئيسية</button></div></div>
</section>

"""

JS = AVA_JS + r"""
/* ======================= kids: the student's world ======================= */
var KID = { muted: ls.get('bp_mute') === '1', ava: 0, lt: {}, fxT: 0, lib: null };
{ const a = parseInt(ls.get('bp_ava'), 10); KID.ava = a >= 0 && a < KID_AVA.n ? a : (Math.random() * KID_AVA.n | 0) }
window.KMUTE = KID.muted;
const KRM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const kGS = () => (!KRM && window.gsap) || null;
const KSTAR = __STAR__;
function kidLib() {
  return KID.lib || (KID.lib = new Promise((res, rej) => {
    if (window.lottie) return res(window.lottie);
    const s = document.createElement('script'); s.src = 'kid/lottie_light.min.js'; s.async = true;
    s.onload = () => window.lottie ? res(window.lottie) : rej(); s.onerror = () => { KID.lib = null; rej() }; document.head.appendChild(s);
  }));
}
function kidJson(n) { return KID.lt[n] || (KID.lt[n] = fetch('kid/' + n + '.json').then(r => { if (!r.ok) throw 0; return r.text() }).catch(e => { delete KID.lt[n]; throw e })) }
async function kidLottie(el, n, o = {}) {
  if (!el) return null;
  try {
    const [L, txt] = await Promise.all([kidLib(), kidJson(n)]); if (!el.isConnected) return null;
    if (el._kl) { try { el._kl.destroy() } catch (e) {} } el.innerHTML = '';
    const a = L.loadAnimation({ container: el, renderer: 'svg', loop: o.loop !== false, autoplay: !KRM && o.autoplay !== false, animationData: JSON.parse(txt), rendererSettings: { preserveAspectRatio: o.par || 'xMidYMid meet' } });
    if (KRM) a.addEventListener('DOMLoaded', () => a.goToAndStop(Math.floor(a.totalFrames * .6), true));
    el._kl = a; return a;
  } catch (e) { return null }
}
/* short, soft sounds (Web Audio, no files); the student can mute them */
const KSFX = {
  sweep(f1, f2, dur, vol = .12, type = 'sine', t0 = 0) {
    const a = audio(); if (!a) return; const o = a.createOscillator(), g = a.createGain(), t = a.currentTime + t0;
    o.type = type; o.frequency.setValueAtTime(f1, t); o.frequency.exponentialRampToValueAtTime(f2, t + dur);
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(vol, t + .008); g.gain.exponentialRampToValueAtTime(.0001, t + dur);
    o.connect(g).connect(a.destination); o.start(t); o.stop(t + dur + .05);
  },
  pop() { this.sweep(380, 1050, .11, .14) },
  tap() { this.sweep(1500, 950, .045, .05, 'triangle') },
  coin() { SFX.tone(988, 0, .09, .08, 'square'); SFX.tone(1319, .075, .34, .07, 'square') },
  ding() { SFX.tone(1568, 0, .9, .07); SFX.tone(2093, .015, .7, .035) },
  tada() { [523, 659, 784, 1047].forEach((f, i) => SFX.tone(f, i * .08, i === 3 ? .6 : .18, .09, 'triangle')); SFX.tone(1568, .34, .5, .04) },
  oops() { this.sweep(520, 340, .2, .09, 'triangle'); this.sweep(420, 270, .26, .07, 'triangle', .15) },
  whoosh() {
    const a = audio(); if (!a) return; const n = a.sampleRate * .42 | 0, b = a.createBuffer(1, n, a.sampleRate), d = b.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.sin(Math.PI * i / n);
    const s = a.createBufferSource(), f = a.createBiquadFilter(), g = a.createGain(); s.buffer = b; f.type = 'bandpass'; f.Q.value = 1.3;
    f.frequency.setValueAtTime(380, a.currentTime); f.frequency.exponentialRampToValueAtTime(2400, a.currentTime + .38); g.gain.value = .13;
    s.connect(f).connect(g).connect(a.destination); s.start();
  }
};
function kidSnd() {
  const on = !KID.muted;
  const h = on ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z" fill="currentColor"/><path d="M15.5 9a4 4 0 010 6M18 6.5a7.5 7.5 0 010 11"/></svg>'
    : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z" fill="currentColor"/><path d="M16 9.5l5 5M21 9.5l-5 5"/></svg>';
  document.querySelectorAll('.ksnd').forEach(b => { b.innerHTML = h; b.classList.toggle('off', !on); b.title = on ? 'إيقاف الأصوات' : 'تشغيل الأصوات'; b.setAttribute('aria-label', b.title) });
}
function kidMute() { KID.muted = !KID.muted; window.KMUTE = KID.muted; ls.set('bp_mute', KID.muted ? '1' : '0'); kidSnd(); KSFX.pop(); const g = kGS(); g && g.fromTo('.ksnd svg', { scale: .6 }, { scale: 1, duration: .5, ease: 'back.out(3)' }) }
const kAvaTint = i => KID_AVA.color(i)[2];
function kidMe() { const el = $('#kMeAva'); if (el) { el.innerHTML = KID_AVA.svg(KID.ava); el.style.setProperty('--t', kAvaTint(KID.ava)) } }

/* moments: a character on a card, optional confetti */
function kidBurst({ anim, title, sub, conf, ms = 2300, bad }) {
  const old = $('#kfx'); if (old) old.remove(); clearTimeout(KID.fxT);
  const fx = document.createElement('div'); fx.id = 'kfx'; fx.className = 'kfx' + (bad ? ' bad' : ''); fx.setAttribute('role', 'status');
  fx.innerHTML = (conf ? '<div class="kfx-conf"></div>' : '') + '<div class="kfx-card"><div class="kfx-anim"></div><div class="kfx-t"></div>' + (sub ? '<div class="kfx-s"></div>' : '') + '</div>';
  fx.querySelector('.kfx-t').textContent = title; if (sub) fx.querySelector('.kfx-s').textContent = sub;
  document.body.appendChild(fx);
  const card = fx.querySelector('.kfx-card'), g = kGS();
  if (conf) { if (KRM) {} else kidLottie(fx.querySelector('.kfx-conf'), 'confetti', { loop: false, par: 'xMidYMid slice' }).then(a => { if (!a) confetti() }) }
  kidLottie(fx.querySelector('.kfx-anim'), anim);
  if (g) g.fromTo(card, { scale: .35, y: 60, opacity: 0 }, { scale: 1, y: 0, opacity: 1, duration: .6, ease: 'back.out(1.7)' });
  const close = () => { clearTimeout(KID.fxT); if (!fx.isConnected) return; if (g) g.to(card, { scale: .6, y: 40, opacity: 0, duration: .28, ease: 'power2.in', onComplete: () => fx.remove() }); else fx.remove() };
  card.onclick = close; KID.fxT = setTimeout(close, ms);
}
function kidHello(name) {
  kidMe(); KSFX.whoosh(); const n = (name || '').split(' ')[0];
  kidBurst({ anim: 'owl', title: EN ? `Hi ${n}!` : `أهلًا يا ${n}!`, sub: EN ? 'Good luck with your answers ✨' : 'بالتوفيق في حلّك ✨', ms: 2400 });
}
function kidCheer() {
  SFX.applause();
  kidBurst({ anim: 'monster', title: praiseText(S.name), sub: EN ? 'Your teacher marked your answer ✓' : 'المعلم صحّح إجابتك ✓', conf: true, ms: 2800 });
}
function kidNote() { KSFX.ding() }
function kidQ(ok, pts) {
  if (ok) { kidBurst({ anim: 'trophy', title: EN ? 'Correct!' : 'إجابة صحيحة!', sub: EN ? 'Fast and right 🌟' : 'سريع وصح 🌟', conf: true, ms: 2600 }) }
  else { KSFX.oops(); kidBurst({ anim: 'thumbs', title: EN ? 'Nice try!' : 'محاولة حلوة!', sub: EN ? 'The next one is yours 💪' : 'الجاي لك إن شاء الله 💪', bad: true, ms: 2200 }) }
}
function kidVeil(veil) {
  const b = veil.firstElementChild; if (!b) return;
  const a = document.createElement('span'); a.className = 'kveil-a'; b.prepend(a);
  const txt = [...b.childNodes].find(n => n.nodeType === 3); if (txt) { const s = document.createElement('b'); s.textContent = txt.nodeValue; txt.replaceWith(s) }
  new MutationObserver(() => { if (!veil.hidden) { if (!a._kl) kidLottie(a, 'panda'); const g = kGS(); g && g.fromTo(b, { scale: .7, opacity: 0 }, { scale: 1, opacity: 1, duration: .45, ease: 'back.out(2)' }) } }).observe(veil, { attributes: true, attributeFilter: ['hidden'] });
}
/* points: a gold capsule that counts up, with a flying star */
function kidPts(src, dst) {
  if (!src || !dst) return; const out = dst.querySelector('b'), num = () => parseInt((src.textContent.match(/\d+/) || ['0'])[0], 10);
  let last = num(); out.textContent = last;
  new MutationObserver(() => {
    const v = num(); if (v === last) return; const d = v - last; last = v;
    const g = kGS(), live = S.ready && d > 0 && !dst.closest('[hidden]') && dst.offsetParent;
    if (!live || !g) { out.textContent = v; return }
    KSFX.coin();
    const r = dst.getBoundingClientRect(), st = document.createElement('div'); st.className = 'kstar'; st.innerHTML = KSTAR; document.body.appendChild(st);
    g.timeline({ onComplete: () => st.remove() })
      .fromTo(st, { x: innerWidth / 2 - 24, y: innerHeight / 2 - 24, scale: .2, rotation: -60, opacity: 0 }, { scale: 1.9, rotation: 0, opacity: 1, duration: .38, ease: 'back.out(2.2)' })
      .to(st, { x: r.left + r.width / 2 - 24, y: r.top + r.height / 2 - 24, scale: .55, rotation: 220, duration: .62, ease: 'power2.in' })
      .add(() => {
        const o = { n: v - d }; g.to(o, { n: v, duration: .5, ease: 'power1.out', onUpdate: () => out.textContent = Math.round(o.n) });
        g.fromTo(dst, { scale: 1.3 }, { scale: 1, duration: .6, ease: 'elastic.out(1,.35)' });
        const p = document.createElement('div'); p.className = 'kplus'; p.textContent = '+' + d; document.body.appendChild(p);
        g.fromTo(p, { x: r.left + r.width / 2 - 14, y: r.top + r.height, opacity: 1 }, { y: r.top + r.height + 34, opacity: 0, duration: 1, ease: 'power1.out', onComplete: () => p.remove() });
      });
  }).observe(src, { childList: true, characterData: true, subtree: true });
}
function kidEnd() {
  const t = (S.myPts ? (S.myPts.b || 0) + (S.myPts.q || 0) : 0), p = $('#kEndPts');
  p.hidden = !t; if (t) p.querySelector('span').textContent = EN ? `You collected ${t} point${t === 1 ? '' : 's'} today!` : (t === 1 ? 'جمعت اليوم نقطة واحدة!' : t === 2 ? 'جمعت اليوم نقطتين!' : `جمعت اليوم ${t} ${t <= 10 ? 'نقاط' : 'نقطة'}!`);
  kidLottie($('#kEndAnim'), 'owl'); SFX.chime();
  const g = kGS(); g && g.fromTo('.kend', { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: .6, ease: 'back.out(1.6)' });
}

/* ---------- the kid join page ---------- */
function kjSync() {
  const inp = $('#jCode'), v = inp.value, f = document.activeElement === inp;
  document.querySelectorAll('#kjDig i').forEach((d, i) => { d.textContent = v[i] || ''; d.classList.toggle('fill', !!v[i]); d.classList.toggle('cur', f && i === Math.min(v.length, 5)) });
}
function kjSay(html, snd) {
  const b = $('#kjSay'); if (b.innerHTML === html) return; b.innerHTML = html;
  const g = kGS(); g && g.fromTo(b, { scale: .82, opacity: .3 }, { scale: 1, opacity: 1, duration: .5, ease: 'back.out(2.4)' });
  if (snd) snd();
}
function kjMood() {
  const t = $('#jTeacher'), c = $('#jCode').value;
  if (t && !t.hidden && !t.classList.contains('bad') && c.length === 6) { const nm = (t.querySelector('b') || {}).textContent || ''; kjSay(EN ? `Class of <b>${esc(nm)}</b> 🎉 now your name` : `حصة <b>${esc(nm)}</b> 🎉 اكتب اسمك واختر صاحبك`, () => KSFX.ding()) }
  else if (t && !t.hidden && t.classList.contains('bad')) kjSay(EN ? 'Hmm… check the code with your teacher 🤔' : 'أمم… تأكد من الكود مع معلمك 🤔', () => KSFX.oops());
  else kjSay(EN ? 'Hi! Type your class code 👋' : 'أهلًا! اكتب كود الحصة 👋');
}
function kjAvas() {
  const box = $('#kjAvas'); if (!box) return;
  box.querySelectorAll('.kja').forEach(b => { const on = +b.dataset.i === KID.ava; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on) });
  const me = $('#kjMe'); if (me) { me.innerHTML = KID_AVA.svg(KID.ava); me.style.setProperty('--t', kAvaTint(KID.ava)) }
}
function kjSkyBuild() {
  const sky = $('#kjSky'); if (sky.childElementCount) return;
  const items = [['star', '#ffc83d', 8, 16, 44], ['+', '#7c5cff', 84, 12, 46], ['dot', '#ff8fb1', 14, 72, 26], ['×', '#20c690', 92, 64, 40], ['tri', '#3fa9f5', 6, 44, 34],
    ['÷', '#ff9638', 70, 86, 38], ['star', '#ff8fb1', 52, 6, 28], ['dot', '#ffc83d', 40, 92, 20], ['=', '#3fa9f5', 26, 90, 36], ['tri', '#20c690', 64, 28, 26], ['star', '#7c5cff', 96, 36, 24], ['dot', '#7c5cff', 78, 50, 16]];
  const SH = { star: '<svg viewBox="0 0 48 48"><path d="M24 4.5l5.6 12 13 1.5-9.7 8.9 2.6 12.9L24 33.2l-11.5 6.6 2.6-12.9-9.7-8.9 13-1.5z" fill="C"/></svg>', dot: '<svg viewBox="0 0 10 10"><circle cx="5" cy="5" r="5" fill="C"/></svg>', tri: '<svg viewBox="0 0 40 36"><path d="M20 3l17 30H3z" fill="none" stroke="C" stroke-width="5" stroke-linejoin="round"/></svg>' };
  items.forEach(([k, c, x, y, s], i) => {
    const e = document.createElement('i'); e.style.cssText = `left:${x}%;top:${y}%;width:${s}px;height:${s}px;font-size:${s * 1.1}px;color:${c}`;
    if (SH[k]) e.innerHTML = SH[k].replace(/C/g, c); else e.textContent = k; sky.appendChild(e);
    const g = kGS(); g && g.to(e, { y: (i % 2 ? -1 : 1) * (10 + i % 4 * 5), rotation: (i % 3 - 1) * 14, duration: 3 + i % 5 * .7, ease: 'sine.inOut', yoyo: true, repeat: -1, delay: -i * .4 });
  });
}
function kjOpen() {
  const k = $('#kjoin'); if (!k.hidden) return; k.hidden = false; document.body.classList.add('kidj');
  kjSkyBuild(); kjSync(); kjAvas(); kjMood(); kidSnd();
  const owl = $('#kjOwl'); if (!owl._kl) kidLottie(owl, 'owl');
  const g = kGS(); if (g) { g.fromTo('#kjoin #joinCard', { y: 50, opacity: 0 }, { y: 0, opacity: 1, duration: .6, ease: 'back.out(1.5)', clearProps: 'transform' }); g.fromTo('.kj-hero > *', { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: .5, stagger: .08, ease: 'back.out(1.6)' }) }
  setTimeout(() => { if (k.hidden) return; const c = $('#jCode'); (c.value.length === 6 && !$('#jName').hidden ? $('#jName') : c).focus({ preventScroll: true }); kjSync() }, 450);
}
function kjClose() { const k = $('#kjoin'); if (!k || k.hidden) return; k.hidden = true; document.body.classList.remove('kidj') }
(function kidInit() {
  // the student card on the home page opens the kid page; the real join form moves into it
  $('#kjSlot').appendChild($('#joinCard')); $('#joinCard').hidden = false;
  $('#ktAvas').innerHTML = [3, 0, 2].map(i => `<span style="background:${kAvaTint(i)}">${KID_AVA.svg(i)}</span>`).join('');
  $('#heroStudent').onclick = () => kjOpen();
  $('#ktGo').onclick = () => kjOpen();
  $('#ktTeacher').onclick = () => $('#toTeacher').click();
  $('#toTeacher').onclick = () => { $('#kidTeaser').hidden = true; $('#adminCard').hidden = false; $('#gSign').focus() };
  $('#toStudent').onclick = () => { $('#adminCard').hidden = true; $('#kidTeaser').hidden = false };
  $('#kjBack').onclick = () => { kjClose(); KSFX.tap(); if (/^#j-/.test(location.hash)) history.replaceState(null, '', location.href.split('#')[0]) };
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$('#kjoin').hidden && !document.querySelector('.veil')) $('#kjBack').click() });
  document.querySelectorAll('.ksnd').forEach(b => b.onclick = kidMute); kidSnd();
  // six code boxes over the real input
  const inp = $('#jCode'), wrap = document.createElement('div'); wrap.className = 'kj-code';
  inp.before(wrap); wrap.appendChild(inp); wrap.insertAdjacentHTML('afterbegin', '<div class="kj-dig" id="kjDig" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div>');
  inp.setAttribute('autocomplete', 'one-time-code');
  let lastLen = inp.value.length;
  inp.addEventListener('input', () => {
    kjSync(); const n = inp.value.length;
    if (n > lastLen) { KSFX.tap(); const d = document.querySelectorAll('#kjDig i')[n - 1], g = kGS(); d && g && g.fromTo(d, { scale: 1.25, y: -6 }, { scale: 1, y: 0, duration: .4, ease: 'back.out(3)' }) }
    lastLen = n; kjMood();
  });
  ['focus', 'blur', 'keyup', 'click'].forEach(ev => inp.addEventListener(ev, kjSync));
  // the name, with the chosen buddy beside it, and the buddy picker
  const nm = $('#jName'), row = document.createElement('div'); row.className = 'kj-namerow'; nm.before(row); row.appendChild(nm);
  row.insertAdjacentHTML('beforeend', '<span class="kj-me" id="kjMe" aria-hidden="true"></span>');
  nm.placeholder = 'اكتب اسمك هنا';
  const lb = document.querySelectorAll('#joinCard .field > label'); if (lb[0]) lb[0].innerHTML = '<span class="n">١</span>كود الحصة'; if (lb[1]) lb[1].innerHTML = '<span class="n">٢</span>اسمك';
  $('#jErr').insertAdjacentHTML('beforebegin', `<div class="field"><label><span class="n">٣</span>اختر صاحبك</label><div class="kj-avas" id="kjAvas">${Array.from({ length: KID_AVA.n }, (_, i) => `<button type="button" class="kja" data-i="${i}" aria-label="صاحب ${i + 1}" style="--t:${kAvaTint(i)}">${KID_AVA.svg(i)}</button>`).join('')}</div></div>`);
  $('#kjAvas').onclick = e => {
    const b = e.target.closest('.kja'); if (!b) return; KID.ava = +b.dataset.i; ls.set('bp_ava', KID.ava); kjAvas(); KSFX.pop();
    const g = kGS(); if (g) { g.fromTo(b.firstElementChild, { scale: .55, rotation: -14 }, { scale: 1, rotation: 0, duration: .7, ease: 'elastic.out(1,.4)' }); g.fromTo('#kjMe .kava', { scale: .4 }, { scale: 1, duration: .5, ease: 'back.out(3)' }) }
  };
  $('#joinCard').insertAdjacentHTML('beforeend', '<p class="kj-foot">ما تحتاج حساب، بس الكود واسمك</p>');
  // listen for the teacher's name and for errors
  new MutationObserver(kjMood).observe($('#jTeacher'), { childList: true, subtree: true, attributes: true, attributeFilter: ['hidden', 'class'] });
  new MutationObserver(() => { if ($('#jErr').textContent && !$('#kjoin').hidden) { KSFX.oops(); const g = kGS(); g && g.fromTo('#kjoin #joinCard', { x: -10 }, { x: 0, duration: .5, ease: 'elastic.out(1,.3)', clearProps: 'transform' }) } }).observe($('#jErr'), { childList: true, characterData: true, subtree: true });
  $('#joinCard').addEventListener('click', e => { if (e.target.closest('.jn')) KSFX.tap() });
  $('#joinCard').addEventListener('submit', () => { if ($('#jCode').value.length === 6 && $('#jName').value.trim()) KSFX.pop() }, true);
  // the student's board: sound on the hand, points, mute
  kidMe();
  $('#sHand').addEventListener('click', () => { KSFX.pop(); const g = kGS(); g && g.fromTo('#sHand .ico', { rotation: -30, scale: 1.4 }, { rotation: 0, scale: 1, duration: .7, ease: 'elastic.out(1,.35)' }) });
  $('#qsPts').insertAdjacentHTML('afterend', `<span class="kpts" id="kQPts">${KSTAR}<b>0</b></span>`);
  kidPts($('#sPts'), $('#kPts')); kidPts($('#qsPts'), $('#kQPts'));
  $('#qsOpts').addEventListener('click', e => { const b = e.target.closest('button[data-o]'); if (b && !b.disabled) KSFX.pop() }, true);
  // which screen is showing decides the kid look
  const show0 = show;
  show = function (id) {
    show0(id); const kid = id === 'student' || (id === 'ended' && ROLE === 's');
    document.body.classList.toggle('kid', kid); if (id !== 'home') kjClose();
    if (id === 'ended' && kid) kidEnd();
  };
  const eb = $('#endBack').onclick; $('#endBack').onclick = () => { const k = document.body.classList.contains('kid'); eb(); document.body.classList.remove('kid'); if (k) kjOpen() };
  // a class link or QR opens the kid page straight away
  if (/^#j-\d{6}$/.test(location.hash) || /[?&]code=\d{6}/.test(location.search)) setTimeout(() => { if (!$('#home').hidden) kjOpen() }, 0);
})();

"""

I18N_ADD = {
    "دخول الطالب": "Student sign-in", "الحصة!": "to class!",
    "أهلًا! اكتب كود الحصة 👋": "Hi! Type your class code 👋", "عندك كود من معلمك؟ ادخل حصتك من هنا": "Got a code from your teacher? Join your class here",
    "ادخل الحصة 🚀": "Join class 🚀", "اختر صاحبك": "Pick your buddy", "اكتب اسمك هنا": "Type your name here",
    "ما تحتاج حساب، بس الكود واسمك": "No account needed, just the code and your name", "إيقاف الأصوات": "Mute sounds", "تشغيل الأصوات": "Turn sounds on",
    "صاحب": "Buddy",
}


def apply(s, rep):
    # fonts and GSAP
    s = rep(s, 'family=IBM+Plex+Sans+Arabic', 'family=Baloo+Bhaijaan+2:wght@500;600;700;800&family=Tajawal:wght@400;500;700;800&family=IBM+Plex+Sans+Arabic')
    s = rep(s, '<script src="rt.js"></script>', '<script src="rt.js"></script>\n<script src="kid/gsap.min.js" defer></script>')
    # styles
    s = rep(s, '@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}\n</style>',
            '@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}\n' + CSS.strip() + '\n</style>')
    # home: a small student card; the real form moves to the kid page
    s = rep(s, '<form class="card" id="joinCard" autocomplete="off">', TEASER + '<form class="card" id="joinCard" autocomplete="off">')
    # the student screen and the goodbye screen
    a = s.index('<section id="student" class="app" hidden>'); b = s.index('<section id="ended"', a)
    s = s[:a] + KJ_HTML + '\n' + STUDENT + s[b:]
    a = s.index('<section id="ended" class="app" hidden>'); b = s.index('<!-- ================= QUIZ', a)
    s = s[:a] + ENDED + s[b:]
    # sounds respect the student's mute button
    s = rep(s, 'function audio() { try {', 'function audio() { if (window.KMUTE) return null; try {')
    # hooks into the student's moments
    s = rep(s, "SFX.applause(); confetti(); toast('👏 إجابة صحيحة! أحسنت')", "kidCheer()")
    s = rep(s, "toast('✍️ المعلم صحح على سبورتك', true);", "toast('✍️ المعلم صحح على سبورتك', true); kidNote();")
    s = rep(s, "S.veil = veil;", "S.veil = veil; kidVeil(veil);")
    s = rep(s, "toast(`أهلًا يا ${name.split(' ')[0]}، بالتوفيق في حلّك!`);", "kidHello(name);")
    s = rep(s, "await DB.set(rp, { name, online: true,", "await DB.set(rp, { name, ava: KID.ava, online: true,")
    s = rep(s, "if (q.st === 'r') { SFX.applause(); confetti() }", "if (q.st === 'r') { SFX.applause(); kidQ(true) }")
    s = rep(s, "else if (S.myAns) S.res = ", "else if (S.myAns && (q.st !== 'r' || kidQ(false) || 1)) S.res = ")
    # the code, before boot
    s = rep(s, '/* ======================= boot ======================= */', JS.replace('__STAR__', json.dumps(STAR)) + '/* ======================= boot ======================= */')
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(I18N_ADD, ensure_ascii=False)[1:-1] + ',')
    return s
