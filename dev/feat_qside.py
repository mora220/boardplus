"""Teacher quiz screen for screen sharing: the question in the middle, big, with the students who answered
on one side and those who have not answered yet on the other."""

CSS = r"""
.qside{display:none}
@media (min-width:900px){
  #qzRun .qz-body{display:grid;grid-template-columns:minmax(150px,220px) minmax(0,1fr) minmax(150px,220px);grid-template-rows:minmax(0,1fr) auto;max-width:none;gap:12px}
  #qzRun #rStage{grid-column:2;grid-row:1;min-height:0}
  #qzRun #rOpts{grid-column:2;grid-row:2}
  #qzRun #rWho{display:none}
  #qzRun #rRankW{grid-column:1/4;grid-row:1/3}
  #qzRun .qside{display:flex;flex-direction:column;gap:6px;grid-row:1/3;min-height:0;overflow:auto;border-radius:16px;padding:10px;border:1.5px solid var(--line);background:var(--surface)}
  #qzRun .qside[hidden]{display:none}
  #qzRun .qdone{grid-column:1;border-color:var(--ok);background:var(--ok-soft)}
  #qzRun .qnot{grid-column:3}
}
.qside h4{margin:0 0 4px;font-size:15px;display:flex;align-items:center;gap:6px;position:sticky;top:-10px;background:inherit;padding-block:4px}
.qside h4 b{margin-inline-start:auto;font-size:20px;font-family:var(--f-display)}
.qn{font-size:15px;font-weight:700;border-radius:10px;padding:6px 10px;background:var(--surface);border:1px solid var(--line);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;animation:qnIn .35s ease}
.qnot .qn{color:var(--muted);font-weight:600}
.qn.ok{background:#e3f6ea;border-color:var(--ok)}
.qn.bad{background:#fdecee;border-color:#e2697a}
@keyframes qnIn{from{transform:scale(.85);opacity:0}to{transform:none;opacity:1}}
"""

JS_RENDER = r"""
  { const st = [...T.st.values()].filter(s => s.info && s.info.name), dn = st.filter(s => A[s.sid]).sort((x, y) => (A[x.sid].at || 0) - (A[y.sid].at || 0)), nt = st.filter(s => !A[s.sid]);
    $('#rDone').innerHTML = `<h4>✅ أجابوا <b>${dn.length}</b></h4>` + dn.map(s => `<span class="qn">${esc(s.info.name)}</span>`).join('');
    $('#rNot').innerHTML = `<h4>⏳ لم يجيبوا <b>${nt.length}</b></h4>` + nt.map(s => `<span class="qn">${esc(s.info.name)}</span>`).join('');
    $('#rDone').hidden = $('#rNot').hidden = rank; }
"""


def apply(s, rep, target):
    s = rep(s, '.whoans{display:flex;flex-wrap:wrap;gap:8px;flex:none}', '.whoans{display:flex;flex-wrap:wrap;gap:8px;flex:none}\n' + CSS.strip())
    s = rep(s, '    <div class="whoans" id="rWho"></div>', '    <div class="whoans" id="rWho"></div>\n    <aside class="qside qdone" id="rDone"></aside><aside class="qside qnot" id="rNot"></aside>')
    a = "}).join('') || '<span class=\"ach none\">لا يوجد طلاب في الجلسة</span>';\n"
    s = rep(s, a, a + JS_RENDER.strip('\n') + '\n')
    if target == 'rb':   # the question opens big (full screen) as soon as the quiz starts
        s = rep(s, "  closeBuilder(); $('#qzRun').hidden = false; showQuestion(0);", "  closeBuilder(); $('#qzRun').hidden = false; showQuestion(0); quizBig($('#qzRun'), $('#rFull'), true);")
    else:
        s = rep(s, "  closeBuilder(); $('#qzRun').hidden = false; showQuestion(0);", "  closeBuilder(); $('#qzRun').hidden = false; showQuestion(0); try { if (!document.fullscreenElement && innerWidth >= 900) document.documentElement.requestFullscreen().catch(() => {}) } catch (e) {}")
    return s
