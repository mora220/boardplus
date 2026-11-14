"""BoardPlus: Arabic calligraphy pen (qalam). A flat, angled nib: thick across, thin along the nib."""
import json

ICON = '    <symbol id="i-cal" viewBox="0 0 24 24"><path d="M15.5 3.5l5 5L10 19l-6 1.5L5.5 14.5z"/><path d="M5.5 14.5l4.5 4.5"/><path d="M13 6l5 5"/></symbol>\n'

DRAW = r"""    case 'cal': {   // qalam: each segment is swept by a flat nib held at a fixed angle
      const r = Math.max(2.5, (s.w || 5) * 1.6) * k, nx = Math.cos(1.05) * r, ny = -Math.sin(1.05) * r;
      if (p.length === 2) { ctx.beginPath(); ctx.moveTo(p[0] * k + nx, p[1] * k + ny); ctx.lineTo(p[0] * k - nx, p[1] * k - ny); ctx.lineWidth = Math.max(1, 1.2 * k); ctx.stroke(); break }
      for (let i = 2; i < p.length; i += 2) {
        const ax = p[i - 2] * k, ay = p[i - 1] * k, bx = p[i] * k, by = p[i + 1] * k;
        ctx.beginPath(); ctx.moveTo(ax + nx, ay + ny); ctx.lineTo(bx + nx, by + ny); ctx.lineTo(bx - nx, by - ny); ctx.lineTo(ax - nx, ay - ny); ctx.closePath(); ctx.fill();
      }
      ctx.lineWidth = Math.max(.8, .9 * k); ctx.beginPath();
      for (let i = 0; i < p.length; i += 2) { ctx.moveTo(p[i] * k + nx, p[i + 1] * k + ny); ctx.lineTo(p[i] * k - nx, p[i + 1] * k - ny) } ctx.stroke();
      break;
    }
"""

ADD_I18N = {"قلم الخط العربي": "Arabic calligraphy pen"}


def apply(s, rep):
    s = rep(s, '    <symbol id="i-img" viewBox', ICON + '    <symbol id="i-img" viewBox')
    s = rep(s, "    case 'pen': if (p.length >= 2) { trace(ctx, p, k); ctx.stroke() } break;\n",
            "    case 'pen': if (p.length >= 2) { trace(ctx, p, k); ctx.stroke() } break;\n" + DRAW)
    s = rep(s, "pen: 'قلم', smart:", "pen: 'قلم', cal: 'قلم الخط العربي', smart:")
    s = rep(s, "    tools: ['pen', 'smart', 'hl', 'er', 'lasso', 'text'],\n    colors: ['#15213a', '#2f5bd3', '#e0242f',",
            "    tools: ['pen', 'cal', 'smart', 'hl', 'er', 'lasso', 'text'],\n    colors: ['#15213a', '#2f5bd3', '#e0242f',")
    s = rep(s, "    tools: ['pen', 'smart', 'hl', 'er', 'text', 'cut', 'lasso'], stamps: true,", "    tools: ['pen', 'cal', 'smart', 'hl', 'er', 'text', 'cut', 'lasso'], stamps: true,")
    s = rep(s, "    tools: ['pen', 'smart', 'hl', 'er', 'lasso', 'text'],\n    colors: ['#15213a', '#2f5bd3', '#1f9d55',",
            "    tools: ['pen', 'cal', 'smart', 'hl', 'er', 'lasso', 'text'],\n    colors: ['#15213a', '#2f5bd3', '#1f9d55',")
    s = rep(s, "    const free = (s.t === 'pen' || s.t === 'hl' || s.t === 'er') && s.p && s.p.length >= 4;",
            "    const free = (s.t === 'pen' || s.t === 'cal' || s.t === 'hl' || s.t === 'er') && s.p && s.p.length >= 4;")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
