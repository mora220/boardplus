"""Phones and short windows: the student's quiz fits the real visible height (browser bars) and keeps the four
options in view."""

CSS = r"""
.qz{height:100vh;height:100dvh;bottom:auto;padding-bottom:env(safe-area-inset-bottom,0px)}
#qzStu .opts{position:sticky;bottom:0;z-index:5;background:var(--wall);padding-top:6px}
@media (max-width:640px){#qzStu .qstage{min-height:120px}#qzStu .opt{min-height:74px}}
@media (max-height:620px){#qzStu .qstage{min-height:90px}#qzStu .opt{min-height:56px}#qzStu .qz-body{padding-block:8px;gap:8px}}
@media (max-height:620px) and (min-width:420px){#qzStu .opts{grid-template-columns:repeat(4,minmax(0,1fr))}}
"""


def apply(s, rep, target):
    return rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
