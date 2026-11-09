"""BoardPlus feature: students record audio or video and post it on their board.
Applied by make_board.py to the page source (string in, string out).

Data layout in a session room:
  sb/<sid>/<id>                    the board item  {t:'media', k:'a'|'v', mid, sid, x, y, d}
  media/<sid>/<mid>                {m: mime, n: chunks, d: seconds, c0..c9: base64 chunks}
Media is kept out of sb/ so board subscriptions never download it; it is fetched only when played.
"""
import json

ADD_I18N = {
    "تسجيل صوت": "Record audio", "تسجيل فيديو": "Record video", "تسجيل صوتي": "Voice note", "فيديو": "Video",
    "اضغط للتشغيل": "Tap to play", "ابدأ التسجيل": "Start recording", "إيقاف": "Stop", "إعادة التسجيل": "Record again",
    "إضافة للسبورة": "Add to my board", "إلغاء": "Cancel", "جاري التسجيل": "Recording",
    "اضغط على سبورتك في المكان اللي تبي تحط فيه التسجيل": "Tap your board where you want to put the recording",
    "اسمح للموقع باستخدام الميكروفون": "Allow the site to use the microphone", "اسمح للموقع باستخدام الكاميرا والميكروفون": "Allow the site to use the camera and microphone",
    "جهازك لا يدعم التسجيل من المتصفح": "Your device can't record from the browser", "التسجيل كبير، سجّل مقطعًا أقصر": "The recording is too big, record a shorter one",
    "جاري الرفع…": "Uploading…", "جاري التحميل…": "Loading…", "تعذر تشغيل التسجيل": "Couldn't play the recording", "تعذر رفع التسجيل. تأكد من الإنترنت": "Couldn't upload the recording. Check your internet",
    "حذف التسجيل": "Delete recording", "حذف هذا التسجيل؟": "Delete this recording?", "سيختفي من السبورة.": "It will be removed from the board.", "حذف": "Delete",
    "تم حذف التسجيل": "Recording deleted", "وصلت للحد الأقصى من التسجيلات في هذه الحصة": "You reached the recording limit for this class",
    "السبورة مقفلة الآن": "The board is locked now", "الحد الأقصى": "Max", "ثانية": "sec", "إغلاق": "Close",
}

CSS = r"""
.recdlg{display:flex;flex-direction:column;gap:12px;align-items:stretch}
.recdlg video,.recdlg audio{width:100%;border-radius:12px;background:#0f172a}
.recdlg video{aspect-ratio:4/3;object-fit:cover}
.recdlg .rstat{display:flex;align-items:center;justify-content:center;gap:10px;font-weight:700;font-size:18px;min-height:30px}
.recdlg .rdot{width:14px;height:14px;border-radius:50%;background:var(--red);animation:rpulse 1s infinite}
@keyframes rpulse{50%{opacity:.25}}
.recdlg .rbig{display:flex;align-items:center;justify-content:center;gap:8px;min-height:54px;font-size:17px}
.recdlg .mic{font-size:54px;text-align:center;line-height:1.2}
.board.placing .ov{cursor:copy}
.mplay{display:flex;flex-direction:column;gap:12px}
.mplay video{width:100%;max-height:62vh;border-radius:12px;background:#000}
.mplay audio{width:100%}
"""

ICONS = '''    <symbol id="i-mic" viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3M8.5 21h7"/></symbol>
    <symbol id="i-cam" viewBox="0 0 24 24"><rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3z"/></symbol>
'''

JS = r"""
/* ======================= student voice / video notes ======================= */
const MEDIA = { a: { max: 60, w: 330, h: 96 }, v: { max: 20, w: 330, h: 96 } }, MEDIA_CHUNK = 200000, MEDIA_MAX_B64 = 1900000;
const mediaCache = new Map();
const curCode = () => ROLE === 't' ? T.code : S.code;
const fmtDur = d => { d = Math.max(0, Math.round(d || 0)); return Math.floor(d / 60) + ':' + String(d % 60).padStart(2, '0') };
function drawMedia(ctx, s, k) {
  const M = MEDIA[s.k] || MEDIA.a, x = s.x * k, y = s.y * k, w = M.w * k, h = M.h * k, r = 18 * k;
  ctx.save(); ctx.globalAlpha = 1;
  ctx.fillStyle = s.k === 'v' ? '#f3ecff' : '#e8f0ff'; ctx.strokeStyle = s.k === 'v' ? '#7b3fc4' : '#2f5bd3'; ctx.lineWidth = 3 * k;
  ctx.beginPath(); ctx.roundRect ? ctx.roundRect(x, y, w, h, r) : ctx.rect(x, y, w, h); ctx.fill(); ctx.stroke();
  const cx = x + h / 2, cy = y + h / 2, cr = h * .32;
  ctx.fillStyle = ctx.strokeStyle; ctx.beginPath(); ctx.arc(cx, cy, cr, 0, 7); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(cx - cr * .32, cy - cr * .45); ctx.lineTo(cx + cr * .5, cy); ctx.lineTo(cx - cr * .32, cy + cr * .45); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#15213a'; ctx.textBaseline = 'middle'; ctx.direction = EN ? 'ltr' : 'rtl'; ctx.textAlign = EN ? 'left' : 'right';
  const tx = EN ? x + h + 6 * k : x + w - 18 * k;
  ctx.font = `700 ${30 * k}px "Readex Pro","IBM Plex Sans Arabic",sans-serif`;
  ctx.fillText((s.k === 'v' ? '🎥 ' : '🎤 ') + (s.k === 'v' ? (EN ? 'Video' : 'فيديو') : (EN ? 'Voice note' : 'تسجيل صوتي')), tx, y + h * .38);
  ctx.font = `500 ${22 * k}px "Readex Pro","IBM Plex Sans Arabic",sans-serif`; ctx.fillStyle = '#5b6b85';
  ctx.fillText(fmtDur(s.d) + ' · ' + (EN ? 'Tap to play' : 'اضغط للتشغيل'), tx, y + h * .72);
  ctx.restore();
}
function mediaBox(s) { const M = MEDIA[s.k] || MEDIA.a; return [s.x, s.y, s.x + M.w, s.y + M.h] }
function mediaAt(bd, x, y) {
  for (const [n, l] of Object.entries(bd.L)) {
    if (n === 'bg' || !l.data) continue;
    for (const [id, s] of l.data) if (s && s.t === 'media') { const b = mediaBox(s); if (x >= b[0] && x <= b[2] && y >= b[1] && y <= b[3]) return { id, s, layer: n } }
  }
  return null;
}
async function mediaSrc(s) {
  if (mediaCache.has(s.mid)) return mediaCache.get(s.mid);
  const base = `sessions/${curCode()}/media/${s.sid}/${s.mid}`;
  const n = await DB.get(base + '/n'), m = await DB.get(base + '/m'); if (!n || !m) return null;
  let b64 = ''; for (let i = 0; i < n; i++) { const c = await DB.get(base + '/c' + i); if (typeof c !== 'string') return null; b64 += c }
  const bin = atob(b64), u8 = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
  const url = URL.createObjectURL(new Blob([u8], { type: m })); mediaCache.set(s.mid, url); return url;
}
function playMedia(hit, bd) {
  const { s, id } = hit, mine = ROLE === 's' && s.sid === S.sid && bd === S.board, canDel = mine || (ROLE === 't' && bd === fBoard);
  modal(`<div class="mplay"><h3>${s.k === 'v' ? '🎥 فيديو' : '🎤 تسجيل صوتي'}${ROLE === 't' && T.st.get(s.sid) ? ' · ' + esc(T.st.get(s.sid).info.name || '') : ''}</h3>
    <div id="mpBody" class="muted" style="text-align:center;padding:18px">جاري التحميل…</div>
    <div class="row">${canDel ? '<button class="btn danger" id="mpDel">حذف التسجيل</button>' : ''}<button class="btn pri" data-close>إغلاق</button></div></div>`, async (v, close) => {
    const del = v.querySelector('#mpDel');
    if (del) del.onclick = async () => { close(); if (await ask('حذف هذا التسجيل؟', 'سيختفي من السبورة.', 'حذف')) removeMedia(bd, id, s) };
    const src = await mediaSrc(s).catch(() => null), body = v.querySelector('#mpBody'); if (!body) return;
    if (!src) { body.textContent = 'تعذر تشغيل التسجيل'; return }
    const el = document.createElement(s.k === 'v' ? 'video' : 'audio'); el.controls = true; el.autoplay = true; el.playsInline = true; el.src = src;
    body.replaceWith(el);
    new MutationObserver((m, o) => { if (!v.isConnected) { o.disconnect(); try { el.pause() } catch (e) {} } }).observe(document.body, { childList: true });
  });
}
function removeMedia(bd, id, s) {
  if (bd === S.board) { const old = S.mine.get(id); S.mine.delete(id); bd.mark('s'); DB.remove(`sessions/${S.code}/sb/${S.sid}/${id}`); if (old) bd.record({ undo: () => { S.mine.set(id, old); bd.mark('s'); DB.set(`sessions/${S.code}/sb/${S.sid}/${id}`, old) }, redo: () => { S.mine.delete(id); bd.mark('s'); DB.remove(`sessions/${S.code}/sb/${S.sid}/${id}`) } }) }
  else { DB.remove(`sessions/${T.code}/sb/${s.sid}/${id}`); DB.remove(`sessions/${T.code}/media/${s.sid}/${s.mid}`) }
  toast('تم حذف التسجيل');
}
function pickMime(k) {
  const L = k === 'v' ? ['video/webm;codecs=vp8,opus', 'video/webm', 'video/mp4'] : ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg'];
  return L.find(t => window.MediaRecorder && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)) || '';
}
const blobB64 = b => new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(String(r.result).split(',')[1] || ''); r.onerror = rej; r.readAsDataURL(b) });
function recordMedia(k) {
  if (!S.code || !S.sid) return;
  if (S.board.locked) return toast('السبورة مقفلة الآن');
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) return toast('جهازك لا يدعم التسجيل من المتصفح', true);
  if ([...S.mine.values()].filter(x => x && x.t === 'media').length >= 6) return toast('وصلت للحد الأقصى من التسجيلات في هذه الحصة', true);
  const max = MEDIA[k].max;
  let stream = null, rec = null, chunks = [], blob = null, t0 = 0, tick = 0, dur = 0;
  modal(`<div class="recdlg"><h3>${k === 'v' ? '🎥 تسجيل فيديو' : '🎤 تسجيل صوت'}</h3>
    ${k === 'v' ? '<video id="rcLive" muted playsinline autoplay></video>' : '<div class="mic" id="rcMic">🎤</div>'}
    <div class="rstat" id="rcStat"><span class="muted">الحد الأقصى ${max} ثانية</span></div>
    <div class="row" id="rcBtns"><button class="btn" data-close>إلغاء</button><button class="btn pri rbig" id="rcGo" disabled>⏺ ابدأ التسجيل</button></div></div>`, async (v, close) => {
    const $v = q => v.querySelector(q), stat = $v('#rcStat'), go = $v('#rcGo');
    const stop = () => { clearInterval(tick); try { rec && rec.state !== 'inactive' && rec.stop() } catch (e) {} };
    const release = () => { stop(); stream && stream.getTracks().forEach(t => t.stop()) };
    new MutationObserver((m, o) => { if (!v.isConnected) { o.disconnect(); release() } }).observe(document.body, { childList: true });
    try {
      stream = await navigator.mediaDevices.getUserMedia(k === 'v' ? { audio: true, video: { width: { ideal: 480 }, height: { ideal: 360 }, facingMode: 'user', frameRate: { ideal: 20 } } } : { audio: true });
    } catch (e) { stat.innerHTML = `<span style="color:var(--red)">${k === 'v' ? 'اسمح للموقع باستخدام الكاميرا والميكروفون' : 'اسمح للموقع باستخدام الميكروفون'}</span>`; return }
    if (!v.isConnected) return release();
    if (k === 'v') $v('#rcLive').srcObject = stream;
    go.disabled = false;
    const start = () => {
      chunks = []; blob = null; const mime = pickMime(k);
      try { rec = new MediaRecorder(stream, { ...(mime ? { mimeType: mime } : {}), audioBitsPerSecond: 32000, ...(k === 'v' ? { videoBitsPerSecond: 300000 } : {}) }) } catch (e) { rec = new MediaRecorder(stream) }
      rec.ondataavailable = e => e.data && e.data.size && chunks.push(e.data);
      rec.onstop = () => { dur = Math.min(max, (performance.now() - t0) / 1000); blob = new Blob(chunks, { type: (rec.mimeType || mime || (k === 'v' ? 'video/webm' : 'audio/webm')).split(';')[0] }); review() };
      rec.start(1000); t0 = performance.now();
      go.innerHTML = '⏹ إيقاف'; go.onclick = stop;
      const upd = () => { const e = (performance.now() - t0) / 1000; stat.innerHTML = `<span class="rdot"></span>جاري التسجيل ${fmtDur(e)} / ${fmtDur(max)}`; if (e >= max) stop() };
      upd(); tick = setInterval(upd, 250);
    };
    const review = () => {
      if (!v.isConnected) return;
      const url = URL.createObjectURL(blob), el = document.createElement(k === 'v' ? 'video' : 'audio'); el.controls = true; el.playsInline = true; el.src = url;
      const live = k === 'v' ? $v('#rcLive') : $v('#rcMic'); live.replaceWith(el); el.id = k === 'v' ? 'rcLive' : 'rcMic';
      if (k === 'v') { stream.getVideoTracks().forEach(t => t.enabled = false) }
      stat.textContent = fmtDur(dur);
      $v('#rcBtns').innerHTML = '<button class="btn" id="rcAgain">إعادة التسجيل</button><button class="btn pri rbig" id="rcAdd">✓ إضافة للسبورة</button>';
      $v('#rcAgain').onclick = () => {
        URL.revokeObjectURL(url);
        if (k === 'v') { stream.getVideoTracks().forEach(t => t.enabled = true); const lv = document.createElement('video'); lv.id = 'rcLive'; lv.muted = true; lv.playsInline = true; lv.autoplay = true; lv.srcObject = stream; el.replaceWith(lv) }
        else { const m = document.createElement('div'); m.className = 'mic'; m.id = 'rcMic'; m.textContent = '🎤'; el.replaceWith(m) }
        $v('#rcBtns').innerHTML = '<button class="btn" data-close>إلغاء</button><button class="btn pri rbig" id="rcGo">⏺ ابدأ التسجيل</button>';
        $v('#rcGo').onclick = start; stat.innerHTML = `<span class="muted">الحد الأقصى ${max} ثانية</span>`;
      };
      $v('#rcAdd').onclick = async () => {
        const btn = $v('#rcAdd'); btn.disabled = true; btn.textContent = 'جاري الرفع…';
        try {
          const b64 = await blobB64(blob); if (b64.length > MEDIA_MAX_B64) { btn.disabled = false; btn.textContent = '✓ إضافة للسبورة'; return toast('التسجيل كبير، سجّل مقطعًا أقصر', true) }
          const mid = 'm' + uid(), base = `sessions/${S.code}/media/${S.sid}/${mid}`, n = Math.ceil(b64.length / MEDIA_CHUNK) || 1;
          for (let i = 0; i < n; i++) await DB.set(base + '/c' + i, b64.slice(i * MEDIA_CHUNK, (i + 1) * MEDIA_CHUNK));
          await DB.update(base, { m: blob.type, n, d: Math.round(dur) });
          mediaCache.set(mid, url); release(); close();
          startPlacing({ t: 'media', k, mid, sid: S.sid, d: Math.round(dur) });
        } catch (e) { btn.disabled = false; btn.textContent = '✓ إضافة للسبورة'; toast('تعذر رفع التسجيل. تأكد من الإنترنت', true) }
      };
    };
    go.onclick = start;
  });
}
function startPlacing(item) {
  const bd = S.board; bd.placing = item; bd.host.classList.add('placing');
  toast('اضغط على سبورتك في المكان اللي تبي تحط فيه التسجيل');
}
"""


def apply(s, rep):
    """s: page source; rep(old, new): replace-once helper bound to s by the caller (returns new s)."""
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, '    <symbol id="i-img" viewBox', ICONS + '    <symbol id="i-img" viewBox')
    # draw + box
    s = rep(s, "function drawStroke(ctx, s, k) {\n  if (!s || !s.t) return;", "function drawStroke(ctx, s, k) {\n  if (!s || !s.t) return;\n  if (s.t === 'media') return drawMedia(ctx, s, k);")
    s = rep(s, "function strokeBox(s) {\n", "function strokeBox(s) {\n  if (s.t === 'media') return mediaBox(s);\n")
    # Board: tap a card to play; place a new recording where the student taps
    s = rep(s, "    const t = this.tool(); const [x, y] = this.pt(e);\n",
            "    const t = this.tool(); const [x, y] = this.pt(e);\n"
            "    if (this.placing) { e.preventDefault(); const it = this.placing, M = MEDIA[it.k] || MEDIA.a; this.placing = null; this.host.classList.remove('placing'); it.x = Math.round(Math.max(0, Math.min(W - M.w, x - M.w / 2))); it.y = Math.round(Math.max(0, Math.min(H - M.h, y - M.h / 2))); this.commit(uid(), it); return }\n"
            "    if (t.t !== 'cut') { const hit = mediaAt(this, x, y); if (hit) { e.preventDefault(); return playMedia(hit, this) } }\n")
    # student toolbar buttons
    s = rep(s, "    extras: [\n      { icon: 'trash', label: 'مسح حلي',",
            "    extras: [\n      { icon: 'mic', label: 'تسجيل صوت', color: '#2f5bd3', onClick: () => recordMedia('a') },\n      { icon: 'cam', label: 'تسجيل فيديو', color: '#7b3fc4', onClick: () => recordMedia('v') },\n      { icon: 'trash', label: 'مسح حلي',")
    s = rep(s, "DB.remove(`sessions/${S.code}/sb/${S.sid}`); S.board.clearHist()", "DB.remove(`sessions/${S.code}/sb/${S.sid}`); DB.remove(`sessions/${S.code}/media/${S.sid}`); S.board.clearHist()")
    # teacher selection also removes the recordings' data
    s = rep(s, "  if (n) DB.update(`sessions/${T.code}/sb/${T.focus}`, del);",
            "  if (n) DB.update(`sessions/${T.code}/sb/${T.focus}`, del);\n  Object.keys(del).forEach(id => { const v = s.strokes.get(id); if (v && v.t === 'media') DB.remove(`sessions/${T.code}/media/${T.focus}/${v.mid}`) });")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
