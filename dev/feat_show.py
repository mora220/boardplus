"""BoardPlus feature: the teacher shows audio, video, a web link, YouTube or PowerPoint/PDF on everyone's board,
plus an English four-line handwriting background.

Live state (teacher writes, everyone reads):  sessions/<code>/show = {k, src, name, open, playing, t, at}
  k: 'audio' | 'video' (synced playback) | 'yt' | 'web' | 'office' | 'pdf' (embedded frame)
Uploaded files are kept by the room outside the live tree and served at /api/file/<code>/<id>/<name>.
"""
import json

ADD_I18N = {
    "عرض للطلاب: صوت، فيديو، رابط، باوربوينت": "Show students: audio, video, link, PowerPoint", "عرض للطلاب": "Show students",
    "ارفع ملفًا": "Upload a file", "أو الصق رابطًا": "Or paste a link", "صوت، فيديو، باوربوينت أو PDF": "Audio, video, PowerPoint or PDF",
    "اعرض الرابط": "Show the link", "رابط يوتيوب، صفحة ويب، ملف صوت أو فيديو، أو عرض Google Slides": "A YouTube link, web page, audio or video file, or Google Slides",
    "جاري الرفع": "Uploading", "تعذر رفع الملف": "Couldn't upload the file", "الملف كبير، الحد الأقصى": "The file is too big, the limit is",
    "نوع الملف غير مدعوم": "This file type isn't supported", "الرابط غير صحيح": "The link isn't valid",
    "إنهاء العرض": "End showing", "تصغير": "Minimize", "تكبير": "Expand", "اضغط للتشغيل 🔊": "Tap to play 🔊",
    "لو الصفحة ما ظهرت، افتحها في تبويب جديد": "If the page doesn't appear, open it in a new tab", "افتح": "Open",
    "التشغيل والإيقاف من عندك يظهر عند كل الطلاب": "Play, pause and seek here and it happens for every student",
    "إنجليزي (4 سطور)": "English (4 lines)", "مربعات": "Grid", "سطور": "Lines", "نقاط": "Dots", "بيضاء": "Blank",
    "ميجا": "MB",
}

CSS = r"""
.showov{position:absolute;inset:10px;z-index:8;display:flex;flex-direction:column;background:var(--surface);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);overflow:hidden}
.showov[hidden]{display:none}
.showov .sh{display:flex;align-items:center;gap:8px;padding:6px 8px 6px 12px;border-bottom:1px solid var(--line);background:var(--surface-2);min-height:44px}
.showov .sh b{flex:1;min-width:0;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.showov .sh button,.showov .sh a{height:34px;border-radius:10px;border:1px solid var(--line);background:var(--surface);padding:0 10px;font:inherit;font-size:13px;font-weight:600;color:var(--ink);cursor:pointer;display:inline-flex;align-items:center;gap:4px;text-decoration:none;white-space:nowrap}
.showov .sh .end{background:var(--red);border-color:var(--red);color:#fff}
.showov .sb{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;background:#0f172a;position:relative}
.showov iframe{width:100%;height:100%;border:0;background:#fff}
.showov video{max-width:100%;max-height:100%;width:100%;height:100%;background:#000}
.showov .note{position:absolute;bottom:8px;left:50%;transform:translateX(-50%);background:rgba(15,23,42,.8);color:#fff;font-size:12px;border-radius:99px;padding:4px 12px;pointer-events:none;white-space:nowrap}
.showov .tap{position:absolute;inset:0;display:grid;place-items:center;background:rgba(15,23,42,.55);border:0;color:#fff;font:inherit;font-size:20px;font-weight:700;cursor:pointer}
.showov.audio{inset:10px 10px auto 10px;background:var(--surface)}
.showov.audio .sb{background:var(--surface);padding:8px 12px}
.showov.audio audio{width:100%}
.showov.mini:not(.audio){inset:auto 12px 12px auto;width:min(380px,60%);height:min(250px,50%)}
.showsrc{display:flex;flex-direction:column;gap:12px}
.showsrc .drop{border:2px dashed var(--line);border-radius:14px;padding:22px;text-align:center;cursor:pointer;font-weight:600;color:var(--muted)}
.showsrc .drop:hover{border-color:var(--accent);color:var(--accent)}
.showsrc .prog{height:8px;border-radius:99px;background:var(--surface-2);overflow:hidden}
.showsrc .prog i{display:block;height:100%;width:0;background:var(--accent);transition:width .2s}
"""

ICON = '    <symbol id="i-show" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="13" rx="2"/><path d="M10 8.5v5l4.5-2.5z"/><path d="M8 21h8M12 17v4"/></symbol>\n'

ENGLISH_BG = r"""  else if (type === 'en') {      // English handwriting lines: top, dashed middle, red base line, descender line
    const gap = 30, per = 4 * gap + 34; ctx.save(); ctx.lineWidth = Math.max(1, 1.6 * k);
    ctx.strokeStyle = '#f2b8c0'; ctx.beginPath(); ctx.moveTo(70 * k, 0); ctx.lineTo(70 * k, h); ctx.stroke();
    for (let y = 46; y + 3 * gap < H; y += per) {
      const ln = (yy, c, dash) => { ctx.strokeStyle = c; ctx.setLineDash(dash ? [10 * k, 8 * k] : []); ctx.beginPath(); ctx.moveTo(0, yy * k); ctx.lineTo(w, yy * k); ctx.stroke() };
      ln(y, '#9fb6e3'); ln(y + gap, '#b9c8e8', true); ln(y + 2 * gap, '#e0242f'); ln(y + 3 * gap, '#9fb6e3');
    }
    ctx.setLineDash([]); ctx.restore();
  }
"""

JS = r"""
/* ======================= show to students: audio, video, links, PowerPoint ======================= */
const SHOW_MAX = 40 * 1024 * 1024;
function showKind(url) {
  let u; try { u = new URL(url) } catch (e) { return null }
  if (!/^https?:$/.test(u.protocol)) return null;
  const h = u.hostname.replace(/^www\.|^m\./, ''), p = u.pathname.toLowerCase();
  const yt = h === 'youtu.be' ? u.pathname.slice(1) : /youtube\.com$/.test(h) ? (u.searchParams.get('v') || (p.match(/\/(?:shorts|embed|live)\/([\w-]{6,})/) || [])[1]) : null;
  if (yt) { const st = parseInt(u.searchParams.get('t') || u.searchParams.get('start') || '0', 10) || 0; return { k: 'yt', src: `https://www.youtube-nocookie.com/embed/${yt.split(/[?&/]/)[0]}?rel=0&playsinline=1&modestbranding=1${st ? '&start=' + st : ''}` } }
  if (/\.(mp3|m4a|wav|ogg|oga|aac|opus)$/.test(p)) return { k: 'audio', src: url };
  if (/\.(mp4|webm|mov|m4v)$/.test(p)) return { k: 'video', src: url };
  if (/\.(pptx?|ppsx?|docx?|xlsx?)$/.test(p)) return { k: 'office', src: 'https://view.officeapps.live.com/op/embed.aspx?src=' + encodeURIComponent(url) };
  if (/\.pdf$/.test(p)) return { k: 'pdf', src: url };
  if (h === 'docs.google.com' && /\/presentation\/d\//.test(p)) return { k: 'web', src: url.replace(/\/(edit|view|present)[^?#]*.*$/, '/embed?start=false&loop=false') };
  if (h === 'drive.google.com' && /\/file\/d\//.test(p)) return { k: 'web', src: url.replace(/\/(view|edit)[^?#]*.*$/, '/preview') };
  return { k: 'web', src: url };
}
function fileKind(f) {
  const n = (f.name || '').toLowerCase(), t = f.type || '';
  if (/^audio\//.test(t) || /\.(mp3|m4a|wav|ogg|aac|opus)$/.test(n)) return 'audio';
  if (/^video\//.test(t) || /\.(mp4|webm|mov|m4v)$/.test(n)) return 'video';
  if (/\.(pptx?|ppsx?|docx?|xlsx?)$/.test(n)) return 'office';
  if (t === 'application/pdf' || /\.pdf$/.test(n)) return 'pdf';
  return null;
}
async function uploadShow(f, onProg) {
  const t = RT.token ? await RT.token() : '';
  return new Promise((res, rej) => {
    const x = new XMLHttpRequest(), q = new URLSearchParams({ room: 's:' + T.code, name: f.name.slice(0, 120), type: f.type || 'application/octet-stream' });
    x.open('POST', new URL('api/upload?' + q, location.href)); if (t) x.setRequestHeader('authorization', 'Bearer ' + t);
    x.upload.onprogress = e => e.lengthComputable && onProg(e.loaded / e.total);
    x.onload = () => { let j = {}; try { j = JSON.parse(x.responseText) } catch (e) {} x.status === 200 && j.url ? res(new URL(j.url, location.href).href) : rej(j.error || x.status) };
    x.onerror = () => rej('net'); x.send(f);
  });
}
function openShow() {
  if (!T.code) return;
  modal(`<div class="showsrc"><h3>${svgI('show')} عرض للطلاب</h3>
    <div class="drop" id="shDrop" tabindex="0" role="button">📁 ارفع ملفًا<br><small>صوت، فيديو، باوربوينت أو PDF · الحد الأقصى ${SHOW_MAX / 1048576} ميجا</small></div>
    <div class="prog" id="shProg" hidden><i></i></div>
    <label style="font-weight:600">أو الصق رابطًا<input class="inp" id="shUrl" dir="ltr" placeholder="https://..."></label>
    <small class="muted">رابط يوتيوب، صفحة ويب، ملف صوت أو فيديو، أو عرض Google Slides</small>
    <p class="err" id="shErr"></p>
    <div class="row"><button class="btn" data-close>إلغاء</button><button class="btn pri" id="shGo">اعرض الرابط</button></div></div>`, (v, close) => {
    const err = v.querySelector('#shErr'), prog = v.querySelector('#shProg');
    const start = (k, src, name) => { DB.set(`sessions/${T.code}/show`, { k, src, name: String(name || '').slice(0, 120), open: true, playing: false, t: 0, at: DB.ts() }); close() };
    v.querySelector('#shDrop').onclick = () => {
      const inp = document.createElement('input'); inp.type = 'file'; inp.accept = 'audio/*,video/*,.mp3,.m4a,.wav,.mp4,.webm,.mov,.ppt,.pptx,.pps,.ppsx,.pdf,.doc,.docx';
      inp.onchange = async () => {
        const f = inp.files[0]; if (!f) return; err.textContent = '';
        const k = fileKind(f); if (!k) return err.textContent = 'نوع الملف غير مدعوم';
        if (f.size > SHOW_MAX) return err.textContent = `الملف كبير، الحد الأقصى ${SHOW_MAX / 1048576} ميجا`;
        prog.hidden = false; const bar = prog.firstElementChild;
        try {
          const url = await uploadShow(f, p => bar.style.width = Math.round(p * 100) + '%');
          start(k, k === 'office' ? 'https://view.officeapps.live.com/op/embed.aspx?src=' + encodeURIComponent(url) : url, f.name);
        } catch (e) { prog.hidden = true; err.textContent = e === 'big' ? `الملف كبير، الحد الأقصى ${SHOW_MAX / 1048576} ميجا` : 'تعذر رفع الملف' }
      };
      inp.click();
    };
    v.querySelector('#shGo').onclick = () => {
      const u = v.querySelector('#shUrl').value.trim(), r = showKind(u); if (!r) return err.textContent = 'الرابط غير صحيح';
      let nm = u; try { nm = new URL(u).hostname.replace(/^www\./, '') } catch (e) {}
      start(r.k, r.src, nm);
    };
  });
}
/* the panel, shared by teacher and students */
function showPanel(stage, isT) {
  const ov = document.createElement('div'); ov.className = 'showov'; ov.hidden = true; stage.style.position = 'relative'; stage.appendChild(ov);
  let cur = null, el = null, mini = false, applying = false;
  const send = () => { if (!isT || !el || applying) return; DB.update(`sessions/${T.code}/show`, { playing: !el.paused, t: el.currentTime || 0, at: DB.ts() }) };
  const head = s => `<div class="sh"><b>${s.k === 'audio' ? '🎧' : s.k === 'video' || s.k === 'yt' ? '🎬' : s.k === 'office' ? '📊' : s.k === 'pdf' ? '📄' : '🌐'} ${esc(s.name || '')}</b>
    ${s.k === 'web' || s.k === 'pdf' ? `<a href="${esc(s.src)}" target="_blank" rel="noopener">↗ افتح</a>` : ''}
    ${s.k !== 'audio' ? `<button data-a="mini">${mini ? 'تكبير' : 'تصغير'}</button>` : ''}${isT ? '<button class="end" data-a="end">✕ إنهاء العرض</button>' : ''}</div>`;
  ov.onclick = e => {
    const a = e.target.closest('[data-a]'); if (!a) return;
    if (a.dataset.a === 'mini') { mini = !mini; ov.classList.toggle('mini', mini); a.textContent = mini ? 'تكبير' : 'تصغير' }
    if (a.dataset.a === 'end') DB.remove(`sessions/${T.code}/show`);
  };
  const sync = s => {
    if (!el || isT) return; applying = true;
    const target = (s.t || 0) + (s.playing && s.at ? Math.max(0, (DB.now() - s.at) / 1000) : 0);
    if (Math.abs((el.currentTime || 0) - target) > 1.5) { try { el.currentTime = target } catch (e) {} }
    if (s.playing) { el.play().then(() => { const b = ov.querySelector('.tap'); b && b.remove() }).catch(() => { if (!ov.querySelector('.tap')) { const b = document.createElement('button'); b.className = 'tap'; b.textContent = 'اضغط للتشغيل 🔊'; b.onclick = () => { b.remove(); sync(cur) }; ov.querySelector('.sb').appendChild(b) } }) }
    else el.pause();
    setTimeout(() => applying = false, 300);
  };
  return s => {
    if (!s || !s.open || !s.src) { ov.hidden = true; ov.innerHTML = ''; cur = null; el = null; return }
    const same = cur && cur.src === s.src && cur.k === s.k; cur = s;
    if (same) return sync(s);
    ov.hidden = false; ov.className = 'showov' + (s.k === 'audio' ? ' audio' : '') + (mini ? ' mini' : '');
    let body;
    if (s.k === 'audio' || s.k === 'video') body = `<${s.k === 'audio' ? 'audio' : 'video'} controls playsinline preload="auto" src="${esc(s.src)}"></${s.k === 'audio' ? 'audio' : 'video'}>`;
    else body = `<iframe src="${esc(s.src)}" allow="autoplay; fullscreen; encrypted-media; picture-in-picture" allowfullscreen referrerpolicy="no-referrer-when-downgrade"></iframe>${s.k === 'web' ? '<span class="note">لو الصفحة ما ظهرت، افتحها في تبويب جديد</span>' : ''}`;
    ov.innerHTML = head(s) + `<div class="sb">${body}</div>` + (isT && (s.k === 'audio' || s.k === 'video') ? '' : '');
    el = ov.querySelector('audio,video');
    if (el) {
      if (isT) { ['play', 'pause', 'seeked'].forEach(ev => el.addEventListener(ev, send)); ov.querySelector('.sh b').title = 'التشغيل والإيقاف من عندك يظهر عند كل الطلاب' }
      else el.addEventListener('loadedmetadata', () => sync(cur), { once: true });
      sync(s);
    }
  };
}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, '    <symbol id="i-img" viewBox', ICON + '    <symbol id="i-img" viewBox')
    # English lines background
    s = rep(s, "  else if (type === 'dots') {", ENGLISH_BG + "  else if (type === 'dots') {")
    s = rep(s, "  const opts = [['grid', 'مربعات'], ['lines', 'سطور'], ['dots', 'نقاط'], ['plain', 'بيضاء']];",
            "  const opts = [['grid', 'مربعات'], ['lines', 'سطور'], ['en', 'إنجليزي (4 سطور)'], ['dots', 'نقاط'], ['plain', 'بيضاء']];")
    # teacher toolbar button
    s = rep(s, "      { icon: 'bg', label: 'خلفية السبورة', onClick: pickBg },",
            "      { icon: 'bg', label: 'خلفية السبورة', onClick: pickBg },\n      { icon: 'show', label: 'عرض للطلاب: صوت، فيديو، رابط، باوربوينت', color: '#0e9f6e', onClick: openShow },")
    # wire panels: teacher
    s = rep(s, "  tBoard.set('bg', T.bg); tBoard.set('t', T.tMap);",
            "  tBoard.set('bg', T.bg); tBoard.set('t', T.tMap);\n  T.showP = showPanel($('#tBoard').parentElement, true);")
    s = rep(s, "  S.board.set('bg', S.bg); S.board.set('t', S.tMap); S.board.set('s', S.mine); S.board.set('m', S.marks);",
            "  S.board.set('bg', S.bg); S.board.set('t', S.tMap); S.board.set('s', S.mine); S.board.set('m', S.marks);\n  S.showP = showPanel($('#sBoard').parentElement, false);")
    s = rep(s, "  T.unsubs.push(DB.onValue(b + '/pts', v => { T.pts = v || {}; refreshScores() }));",
            "  T.unsubs.push(DB.onValue(b + '/show', v => T.showP && T.showP(v)));\n  T.unsubs.push(DB.onValue(b + '/pts', v => { T.pts = v || {}; refreshScores() }));")
    s = rep(s, "  S.unsubs.push(DB.onValue(b + '/bgImg', async src => { S.bg.img = await loadImg(src); S.board.mark('bg') }));",
            "  S.unsubs.push(DB.onValue(b + '/bgImg', async src => { S.bg.img = await loadImg(src); S.board.mark('bg') }));\n  S.unsubs.push(DB.onValue(b + '/show', v => S.showP && S.showP(v)));")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
