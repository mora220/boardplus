"""BoardPlus Games in the same cheerful family as the board: grape brand, chunky buttons, soft wall, kid answer colours,
and the same short sounds on taps. Light theme only; the dark theme keeps its colours with a grape brand."""
CSS = r"""
/* ===== BoardPlus theme ===== */
:root{--bg:#f3f1ff;--surface:#fff;--surface-2:#f3efff;--ink:#2b2d55;--muted:#6b6f9a;--line:#e6e2f7;--brand:#7c5cff;--brand-ink:#fff;--sun:#ffc83d;--sun-ink:#5b3b00;
  --team-a:#3fa9f5;--team-b:#ff7a3d;--ok:#16b37c;--bad:#ff4d5e;--o1:#7c5cff;--o2:#ff9638;--o3:#1fc58f;--o4:#3fa9f5;--ring:#e4dcff;
  --shadow:0 4px 0 var(--ring),0 22px 38px -26px rgba(76,52,180,.5);--r:22px;--bgx:linear-gradient(165deg,#edf1ff 0%,#f3eeff 55%,#fff5e8 100%)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--brand:#a48bff;--brand-ink:#141229;--bg:#141229;--surface:#1d1a3a;--surface-2:#252148;--line:#332e5e;--ring:#2c275a;--bgx:var(--bg)}}
:root[data-theme="dark"]{--brand:#a48bff;--brand-ink:#141229;--bg:#141229;--surface:#1d1a3a;--surface-2:#252148;--line:#332e5e;--ring:#2c275a;--bgx:var(--bg)}
body{background:var(--bgx);background-attachment:fixed}
.bar{border-bottom:0}
.logo-pill{border-radius:16px;box-shadow:0 3px 0 var(--ring)}
.brand b{color:var(--brand)}
.icon-btn{border:0;box-shadow:0 3px 0 var(--ring);border-radius:14px}
.btn{font-family:var(--font-display);border-radius:16px;box-shadow:0 3px 0 var(--ring);background:var(--surface)}
.btn:not([disabled]):active{transform:translateY(2px);box-shadow:0 1px 0 var(--ring)}
.btn.primary{background:linear-gradient(#8f74ff,#6c4cff);color:#fff;box-shadow:0 4px 0 #5636e0}
.btn.sun{background:linear-gradient(#ffd863,#ffc229);box-shadow:0 4px 0 #e39d00}
.btn.danger{box-shadow:0 4px 0 #c9303f}
.in{border:2px solid var(--line);border-radius:14px}
.in:focus{border-color:var(--brand);box-shadow:0 0 0 4px color-mix(in srgb,var(--brand) 18%,transparent)}
.card,.qcard{border-radius:24px}
.hero{background:linear-gradient(135deg,#8a6dff,#6a49ff 60%,#5a3be8);color:#fff;box-shadow:0 8px 0 #4a2fc4,0 40px 70px -40px rgba(76,52,180,.7)}
.choice,.pick{border:0;border-radius:22px;box-shadow:0 0 0 2px var(--surface-2),0 4px 0 var(--ring);transition:transform .15s,box-shadow .15s}
.choice:hover,.pick:hover{transform:translateY(-3px)}
.choice .ic{box-shadow:0 4px 0 rgba(0,0,0,.12)}
.pick[aria-pressed="true"]{background:var(--surface-2);box-shadow:inset 0 0 0 3px var(--brand),0 4px 0 color-mix(in srgb,var(--brand) 45%,var(--ring))}
.sec-title .n{background:var(--brand);color:#fff;border-radius:12px}
.bigcode{color:var(--brand)}
.chip{background:var(--surface);box-shadow:0 3px 0 var(--ring)}
.clock,.pill{box-shadow:0 3px 0 var(--ring)}
.clock.low{background:var(--bad);color:#fff}
.opt{border-radius:20px;box-shadow:0 6px 0 rgba(0,0,0,.2);background-image:linear-gradient(rgba(255,255,255,.18),transparent)}
.opt:not([disabled]):active{transform:translateY(4px);box-shadow:0 2px 0 rgba(0,0,0,.2)}
.feedback{border-radius:18px;font-family:var(--font-display)}
details.card{box-shadow:var(--shadow)}
"""

def apply(s, rep):
    i = s.index('<style>\n/* Layout')
    j = s.index('</style>', i)
    return s[:j] + CSS.strip() + '\n' + s[j:]
