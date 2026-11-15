"""Quiz ranking for a shared screen: no right/wrong per student, only the top five after a question (each student
sees his own rank on his device), and the leaderboard shows three places; students with the same score share a place."""

CSS = r"""
.pn.many{white-space:normal;text-align:center;line-height:1.35;font-size:14px}
.pd .pc{font-size:12px;color:var(--muted);font-weight:700}
.rknote{text-align:center;color:var(--muted);font-size:13px;margin-top:6px}
"""

JS = r"""
/* ======================= places: equal scores share a place ======================= */
function denseRank(list) { let pl = 0, prev = null; return (list || []).map(r => { if (r.t !== prev) { pl++; prev = r.t } return { ...r, pl } }) }
const placeOf = (list, sid) => { const r = denseRank(list).find(x => x.sid === sid); return r ? r.pl : 0 };
"""


def apply(s, rep, target):
    s = rep(s, '.pd.me .pn{', CSS.strip() + '\n.pd.me .pn{')
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    # nobody sees who answered right or wrong: only who answered
    s = rep(s, "    if (!show) return `<span class=\"ach done\">${nm} ✓</span>`;", "    return `<span class=\"ach done\">${nm} ✓</span>`;")
    # rows show the place (ties share it)
    s = rep(s, "const i = j + off; return `<div class=\"lr rk-in${r.sid === me ? ' me' : ''}\"", "const i = r.pl ? r.pl - 1 : j + off; return `<div class=\"lr rk-in${r.sid === me ? ' me' : ''}\"")
    # teacher after a question: top five places only
    s = rep(s, "$('#rRank').innerHTML = rankHTML(runRank(), null)",
            "const top5 = denseRank(runRank()).filter(x => x.pl <= 5 && x.t > 0); $('#rRank').innerHTML = (top5.length ? rankHTML(top5, null) : '<div class=\"empty\"><b>لا توجد نقاط بعد</b></div>') + '<p class=\"rknote\">🔒 يظهر هنا الخمسة الأوائل فقط، وكل طالب يرى ترتيبه على جهازه</p>'")
    # student: his own place, and the top five
    s = rep(s, "$('#qsRankT').textContent = mi < 0 ? 'الترتيب الآن' : mi === 0 ?", "const pl = mi < 0 ? 0 : placeOf(lb, S.sid); $('#qsRankT').textContent = mi < 0 ? 'الترتيب الآن' : pl === 1 ?")
    s = rep(s, "`ترتيبك ${mi + 1} من ${lb.length} · السؤال الجاي فرصتك`", "`ترتيبك ${pl} · السؤال الجاي فرصتك`")
    s = rep(s, "$('#qsRank').innerHTML = rankHTML(lb.slice(0, 10), S.sid) + (mi >= 10 ? rankHTML([lb[mi]], S.sid, mi) : '');",
            "{ const dl = denseRank(lb), t5 = dl.filter(x => x.pl <= 5 && x.t > 0); $('#qsRank').innerHTML = rankHTML(t5, S.sid) + (mi >= 0 && !t5.some(x => x.sid === S.sid) ? rankHTML([dl[mi]], S.sid) : '') }")
    # leaderboard: three places, everyone with the same score in the same place, no full list
    s = rep(s, """  const top = list.slice(0, 3);
  pod.innerHTML = [1, 0, 2].filter(i => top[i]).map(i => { const r = top[i]; return `<div class="pd p${i + 1}${r.sid === me ? ' me' : ''}"><div class="pa">${esc((r.n.trim()[0]) || '؟')}</div><div class="pn">${esc(r.n)}</div><div class="pp">${r.t} نقطة</div><div class="pb">${i + 1}</div></div>` }).join('');
  ul.innerHTML = list.map((r, i) => `<div class="lr${r.sid === me ? ' me' : ''}"><span class="rk">${i + 1}</span><span class="ln">${esc(r.n)}</span><span class="lc">السبورة ${r.b}</span><span class="lc">الكويز ${r.q}</span><b class="lt">${r.t}</b></div>`).join('');
  const mi = me ? list.findIndex(r => r.sid === me) : -1;
  mr.hidden = mi < 0; if (mi >= 0) mr.textContent = mi === 0 ? '🥇 أنت الأول! ما شاء الله عليك' : `ترتيبك ${mi + 1} من ${list.length} · استمر، أنت قريب من القمة`;""",
"""  const dl = denseRank(list.filter(r => r.t > 0)), places = [1, 2, 3].map(pl => dl.filter(r => r.pl === pl));
  pod.innerHTML = [1, 0, 2].filter(i => places[i].length).map(i => { const g = places[i], mine = g.some(r => r.sid === me);
    return `<div class="pd p${i + 1}${mine ? ' me' : ''}"><div class="pa">${g.length > 1 ? '👥' : esc((g[0].n.trim()[0]) || '؟')}</div><div class="pn${g.length > 1 ? ' many' : ''}">${g.map(r => esc(r.n)).join('، ')}</div><div class="pp">${g[0].t} نقطة</div><div class="pb">${i + 1}</div></div>` }).join('');
  ul.innerHTML = '';
  const mp = me ? (dl.find(r => r.sid === me) || {}).pl || 0 : 0;
  mr.hidden = !me; if (me) mr.textContent = mp === 1 ? '🥇 أنت في المركز الأول! ما شاء الله عليك' : mp && mp <= 3 ? `🎉 أنت في المركز ${mp}` : 'استمر، أنت قريب من القمة 💪';""")
    return s
