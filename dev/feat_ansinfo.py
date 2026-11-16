"""Shared screen care: the quiz builder hides the correct answers (a button shows them), and the leaderboard shows
the class, the day and the date for screenshots; each student sees his own place out of how many."""

CSS = r"""
#qzBuild.hideans .abcd button.on{background:var(--surface-2);border-color:var(--line);color:inherit}
#qzBuild.hideans .qa>span{visibility:hidden}
#qAns.on{background:var(--ok);border-color:var(--ok);color:#fff}
.lbinfo{text-align:center;font-weight:700;font-size:20px;color:var(--muted);margin:2px 0 6px}
.lbinfo b{color:var(--ink)}
"""

JS = r"""
/* ======================= hide the answers while the screen is shared ======================= */
function setAnsView(show) {
  QZ.showAns = !!show; $('#qzBuild').classList.toggle('hideans', !QZ.showAns);
  const b = $('#qAns'); b.classList.toggle('on', QZ.showAns); b.querySelector('span').textContent = QZ.showAns ? 'إخفاء الإجابات' : 'إظهار الإجابات'; b.firstChild.textContent = QZ.showAns ? '🙈 ' : '👁 ';
}
function lbInfoText() {
  const d = new Intl.DateTimeFormat(EN ? 'en-GB' : 'ar-SA-u-ca-gregory-nu-latn', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }).format(new Date());
  const cls = ROLE === 't' && T.clist && T.clist.name ? `<b>👥 ${esc(T.clist.name)}</b> · ` : '';
  return `${cls}📅 ${d}`;
}
"""


def apply(s, rep, target):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    # the builder: answers hidden by default, a button shows them
    s = rep(s, '    <button class="btn aibtn" id="qAI">', '    <button class="btn" id="qAns" type="button" title="الإجابات الصحيحة مخفية حتى لا تظهر في مشاركة الشاشة">👁 <span>إظهار الإجابات</span></button>\n    <button class="btn aibtn" id="qAI">')
    s = rep(s, "<section class=\"qz\" id=\"qzBuild\" hidden>", "<section class=\"qz hideans\" id=\"qzBuild\" hidden>")
    s = rep(s, "function startQuiz(only) {", "document.addEventListener('click', e => { const b = e.target.closest('#qAns'); if (b) setAnsView(!QZ.showAns); const a = e.target.closest('#qzBuild.hideans .abcd [data-set]'); if (a) setTimeout(() => toast('✓ حُفظت الإجابة (مخفية)'), 50) });\nfunction startQuiz(only) {")
    # the leaderboard: class, day and date; the student's place out of all
    s = rep(s, '<div class="qz-body gut"><div class="myrank" id="lbMe" hidden></div>', '<div class="qz-body gut"><div class="lbinfo" id="lbInfo"></div><div class="myrank" id="lbMe" hidden></div>')
    s = rep(s, "  const pod = $('#lbPod'), ul = $('#lbList'), mr = $('#lbMe');\n", "  const pod = $('#lbPod'), ul = $('#lbList'), mr = $('#lbMe'); $('#lbInfo').innerHTML = lbInfoText();\n")
    s = rep(s, "mr.hidden = !me; if (me) mr.textContent = mp === 1 ? '🥇 أنت في المركز الأول! ما شاء الله عليك' : mp && mp <= 3 ? `🎉 أنت في المركز ${mp}` : 'استمر، أنت قريب من القمة 💪';",
            "const all = list.length, my = mp || (new Set(dl.map(r => r.t)).size + 1);\n"
            "  mr.hidden = !me; if (me) mr.textContent = my === 1 ? `🥇 أنت في المركز الأول من ${all}! ما شاء الله عليك` : my <= 3 ? `🎉 ترتيبك ${my} من ${all}` : `ترتيبك ${my} من ${all} · استمر، أنت قريب من القمة 💪`;")
    return s
