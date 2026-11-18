"""Small and split screens: the tug arena keeps a usable height and the analysis scrolls under it; the end/close
buttons stay in a fixed corner; the winners' screen covers the whole window and fits short heights; the question view
keeps all the options visible; the student's game area and buttons fit short windows."""

CSS = r"""
#raceT.tugon{overflow-y:auto;overflow-x:hidden}
#raceT.tugon .tug{position:relative;inset:auto;flex:0 0 auto;height:max(56vh,360px)}
#raceT.tugon .an{position:relative;inset:auto;flex:1 0 auto;overflow:visible}
#raceT .tg-act{position:fixed;left:14px;bottom:14px;translate:none;z-index:50;direction:rtl}
#raceT .tg-win{position:fixed;inset:0;z-index:55;overflow:auto;background:radial-gradient(circle at 50% 35%,rgba(40,20,80,.88),rgba(8,8,24,.96));justify-content:safe center;padding:16px 12px 24px;gap:8px}
#raceT .tg-win .cup{font-size:clamp(44px,13vh,110px)}
#raceT .tg-win h1{font-size:clamp(24px,min(5vw,7vh),62px);text-align:center}
#raceT .tg-win .sc{font-size:clamp(17px,3vh,26px)}
#raceT .tg-win .t5 div{padding:6px 12px;font-size:clamp(14px,2.4vh,19px)}
#raceT .tg-win .rbtn{height:auto;min-height:40px;white-space:normal}
@media (max-width:760px){
  .tg-hud{grid-template-columns:1fr 1fr;padding:8px}
  .tg-mid2{display:none}
  .tg-pan{padding:7px 10px;gap:4px}.tg-pan h3{font-size:16px}
  .tg-pan .st{font-size:12px;gap:8px;flex-wrap:wrap}
  .tg-line b{font-size:11px;padding:2px 7px}
}
@media (max-height:620px){
  .tg-pan .st{display:none}.tg-pan h3{font-size:16px}.tg-pan{padding:7px 10px}
  .tg-ban{font-size:clamp(22px,4vw,40px)}
  .tg-pop{font-size:17px}
}
/* the question view */
@media (max-width:820px){.rqb{grid-template-columns:minmax(0,1fr) 190px;grid-template-rows:none}.rqopts{flex-direction:column;flex-wrap:nowrap}.rqo{flex:none;min-width:0}}
@media (max-width:560px){.rqb{grid-template-columns:1fr;grid-template-rows:minmax(0,1fr) auto}.rqopts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}.rqo{grid-template-columns:1fr;text-align:center;padding:4px}.rqo .bar{display:none}.rqo em{font-size:11px}}
@media (max-height:600px){.rqo{padding:4px 8px;gap:4px}.rqo b{font-size:20px}.rqopts{gap:6px}.rqh{padding:6px 10px;gap:6px}.rqh b{font-size:16px}.rqh .rbtn{height:34px;padding:0 10px;font-size:14px}.rqs{padding:3px 8px;font-size:13px}.rqb{padding-top:50px}}
.rqbar{flex-wrap:nowrap!important;overflow-x:auto;max-width:calc(100% - 20px)}
/* the student: fit the real visible height on phones (the browser bars), keep all the options in view */
.race{height:100vh;height:100dvh;bottom:auto;padding-bottom:env(safe-area-inset-bottom,0px)}

@media (max-height:620px){.rg-q{flex-basis:30%}.rg-world .gm-arena{min-height:170px}.race .ropt{min-height:54px;font-size:26px}.race .ropts{gap:8px;padding:0 10px 10px}}
@media (max-height:620px) and (min-width:420px){.race .ropts{grid-template-columns:repeat(4,1fr)}}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, "el.querySelector('#tugS').appendChild(ov);", "el.appendChild(ov);")
    return s
