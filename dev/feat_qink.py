"""Pens on the teacher's quiz screen: the pen bar sits above the question (it no longer covers it), with a pen, the
Arabic calligraphy pen and an eraser, and the teacher can write on the whole quiz screen (seen through screen sharing)
or on the question only (seen on the students' devices)."""
import re
from feat_cal import DRAW as CAL_DRAW

BAR = ('<div class="inkbar" id="rInk">'
       '<button data-it="pen" title="قلم"><svg class="ico"><use href="#i-pen"/></svg></button>'
       '<button data-it="cal" title="قلم الخط العربي"><svg class="ico"><use href="#i-cal"/></svg></button>'
       '<button data-it="er" title="ممسحة"><svg class="ico"><use href="#i-er"/></svg></button><i class="isep"></i>'
       '<button data-ic="#e0242f" title="أحمر"><span class="sw" style="background:#e0242f"></span></button>'
       '<button data-ic="#2f5bd3" title="أزرق"><span class="sw" style="background:#2f5bd3"></span></button>'
       '<button data-ic="#1f9d55" title="أخضر"><span class="sw" style="background:#1f9d55"></span></button>'
       '<button data-ic="#15213a" title="أسود"><span class="sw" style="background:#15213a"></span></button><i class="isep"></i>'
       '<button data-ink="full" class="wide" title="مكان الكتابة: الشاشة كلها (تظهر في مشاركة الشاشة) أو السؤال فقط (يظهر على أجهزة الطلاب)"><span class="fl1">🖥 الشاشة كلها</span><span class="fl0">📱 على السؤال</span></button><i class="isep"></i>'
       '<button data-ink="undo" title="تراجع"><svg class="ico"><use href="#i-undo"/></svg></button>'
       '<button data-ink="clear" title="مسح الكتابة"><svg class="ico"><use href="#i-trash"/></svg></button></div>')

ICON = '    <symbol id="i-cal" viewBox="0 0 24 24"><path d="M15.5 3.5l5 5L10 19l-6 1.5L5.5 14.5z"/><path d="M5.5 14.5l4.5 4.5"/><path d="M13 6l5 5"/></symbol>\n'

CSS = r"""
#qzRun #rInk{position:relative;inset:auto;z-index:21;align-self:center;justify-self:center;width:max-content;max-width:100%;flex-wrap:wrap;justify-content:center;margin:0 auto}
#qzRun #rInk[hidden]{display:none}
#rInk .isep{width:1px;background:var(--line);margin:4px 3px}
#rInk button.wide{width:auto;padding:0 10px;font-size:13px;font-weight:700;white-space:nowrap}
#rInk .fl0{display:none}#rInk button.wide:not(.on) .fl1{display:none}#rInk button.wide:not(.on) .fl0{display:inline}
#qzRun .qz-body{position:relative}
#rOver{position:absolute;inset:0;width:100%;height:100%;z-index:20;pointer-events:none;touch-action:none}
#rOver.on{pointer-events:auto;cursor:crosshair}
"""

JS = r"""
/* ======================= quiz pens: whole screen or the question ======================= */
const QI = { t: 'pen', full: ls.get('rb_qfull') !== '0', map: new Map(), hist: [], qid: null, cur: null };
function qInkTool(full) { return { t: QI.t, c: QZ.inkC, w: QI.t === 'er' ? 7 : full ? (QI.t === 'cal' ? 4 : 4) : (QI.t === 'cal' ? 5 : 6) } }
function setInk(on) {
  QZ.inkOn = on; QZ.board.locked = !on || QI.full; $('#rBoard').classList.toggle('inkon', on && !QI.full);
  $('#rOver').classList.toggle('on', on && QI.full); if (on && QI.full) qOverSize();
  $('#rInk').querySelectorAll('button').forEach(b => b.classList.toggle('on', (on && b.dataset.it === QI.t) || (on && QI.t !== 'er' && b.dataset.ic === QZ.inkC) || (b.dataset.ink === 'full' && QI.full)));
}
function qOverSize() { const c = $('#rOver'), r = c.getBoundingClientRect(), d = Math.min(devicePixelRatio || 1, 2), w = Math.round(r.width * d), h = Math.round(r.height * d); if (w && (c.width !== w || c.height !== h)) { c.width = w; c.height = h } qOverDraw() }
function qOverDraw() { const c = $('#rOver'), x = c.getContext('2d'), d = c.width / Math.max(1, c.getBoundingClientRect().width); x.clearRect(0, 0, c.width, c.height); QI.map.forEach(s => drawStroke(x, s, d)) }
function qInkInit() {
  const ov = $('#rOver'), pt = e => { const r = ov.getBoundingClientRect(); return [Math.round(e.clientX - r.left), Math.round(e.clientY - r.top)] };
  ov.addEventListener('pointerdown', e => { if (!QZ.inkOn || !QI.full || QI.cur) return; e.preventDefault(); ov.setPointerCapture(e.pointerId); const id = 'o' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5); QI.cur = { id, s: { ...qInkTool(true), p: pt(e) } }; QI.map.set(id, QI.cur.s); qOverDraw() });
  ov.addEventListener('pointermove', e => { if (!QI.cur) return; (e.getCoalescedEvents ? e.getCoalescedEvents() : [e]).forEach(ev => QI.cur.s.p.push(...pt(ev))); qOverDraw() });
  ['pointerup', 'pointercancel'].forEach(t => ov.addEventListener(t, () => { if (QI.cur) { QI.hist.push(QI.cur.id); QI.cur = null } }));
  $('#rInk').onclick = e => {
    const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.ic) { QZ.inkC = b.dataset.ic; if (QI.t === 'er') QI.t = 'pen'; setInk(true) }
    else if (b.dataset.it) { if (QZ.inkOn && QI.t === b.dataset.it) setInk(false); else { QI.t = b.dataset.it; setInk(true) } }
    else if (b.dataset.ink === 'full') { QI.full = !QI.full; ls.set('rb_qfull', QI.full ? '1' : '0'); setInk(QZ.inkOn); toast(QI.full ? '🖥 الكتابة على الشاشة كلها، تظهر في مشاركة الشاشة' : '📱 الكتابة على السؤال، وتظهر على أجهزة الطلاب') }
    else if (b.dataset.ink === 'undo') { if (QI.full) { const id = QI.hist.pop(); if (id) { QI.map.delete(id); qOverDraw() } } else QZ.board.undo() }
    else if (b.dataset.ink === 'clear') { QI.map.clear(); QI.hist = []; qOverDraw(); if (QZ.run) { DB.remove(`sessions/${T.code}/qink/${QZ.run.qid}`); QZ.board.clearHist() } }
  };
  setInterval(() => { const q = QZ.run ? QZ.run.qid : null; if (q !== QI.qid) { QI.qid = q; QI.map.clear(); QI.hist = []; qOverDraw(); if (!q && QZ.inkOn) setInk(false) } }, 300);
  addEventListener('resize', () => { if (QI.map.size || QZ.inkOn) qOverSize() });
  setInk(false);
}
"""


def apply(s, rep, target):
    if target == 'rb':   # the calligraphy pen does not exist in ragabboard yet: drawing it is enough here
        s = rep(s, "    case 'pen': if (p.length >= 2) { trace(ctx, p, k); ctx.stroke() } break;\n",
                "    case 'pen': if (p.length >= 2) { trace(ctx, p, k); ctx.stroke() } break;\n" + CAL_DRAW)
        s = rep(s, '    <symbol id="i-img" viewBox', ICON + '    <symbol id="i-img" viewBox')
    m = re.findall(r'      <div class="inkbar" id="rInk">.*?</div>\n', s)
    assert len(m) == 1, len(m)
    s = s.replace(m[0], '')
    s = rep(s, '    <div class="stage qstage" id="rStage">', '    ' + BAR + '\n    <canvas id="rOver"></canvas>\n    <div class="stage qstage" id="rStage">')
    s = rep(s, ".inkbar .sw{", CSS.strip() + "\n.inkbar .sw{")
    s = rep(s, "tool: () => ({ t: 'pen', c: QZ.inkC, w: 6 })", "tool: () => qInkTool(false)")
    m = re.findall(r"  \$\('#rInk'\)\.onclick = e => \{\n.*?\n  \};\n", s, re.S)
    assert len(m) == 1 and len(m[0]) < 900, [len(x) for x in m]
    s = s.replace(m[0], "  qInkInit();\n")
    m = re.findall(r"function setInk\(on\) \{\n.*?\n\}\n", s, re.S)
    assert len(m) == 1 and len(m[0]) < 500, [len(x) for x in m]
    s = s.replace(m[0], '')
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    return s
