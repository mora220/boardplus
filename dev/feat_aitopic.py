"""BoardPlus feature: AI quiz from a lesson name (subject + grade + lesson), not only from a photo."""
import json

ADD_I18N = {
    "كويز فوري بالذكاء الاصطناعي": "Instant AI quiz", "من صورة": "From a photo", "من اسم الدرس": "From a lesson name",
    "المادة": "Subject", "اسم الدرس": "Lesson name", "ملاحظات (اختياري)": "Notes (optional)",
    "مثال: رياضيات": "e.g. Math", "مثال: القسمة على عدد من رقمين": "e.g. Dividing by a two-digit number",
    "مثال: المنهج السعودي، ركّز على المسائل اللفظية": "e.g. US curriculum, focus on word problems",
    "اكتب اسم الدرس أولًا.": "Type the lesson name first.",
    "ما قدرت أطلع أسئلة صالحة. جرّب مرة ثانية أو وضّح اسم الدرس.": "Couldn't get valid questions. Try again or make the lesson name clearer.",
    "الأسئلة من معلومات الذكاء الاصطناعي العامة عن الدرس، راجعها قبل البدء.": "Questions come from the AI's general knowledge of the lesson. Review them before you start.",
    "والصق الطلب فقط.": "and paste the request only.",
}

TOPIC_PROMPT = r"""
function aiTopicPrompt(n, type, level, t) {
  const kindsEn = ({ mix: 'questions mixing multiple choice and true/false', mc: 'multiple-choice questions', tf: 'true/false questions' })[type] || 'questions';
  const kindsAr = { mix: 'متنوعة بين اختيار من متعدد وصح وخطأ', mc: 'من نوع اختيار من متعدد', tf: 'من نوع صح وخطأ' }[type] || 'متنوعة';
  if (EN) return `You are an expert teacher. Write ${n} ${kindsEn} for ${level || 'primary school'} students${t.subj ? ` in ${t.subj}` : ''} about the lesson: "${t.lesson}".${t.notes ? `\nTeacher notes: ${t.notes}` : ''}
- Cover the main ideas and skills of this lesson as it is usually taught at this grade, from easy to slightly harder.
- Write in the language of the lesson name.
- Keep each question short and clear (under 25 words) with short options.
- Multiple choice: exactly 4 options, only one correct, plausible distractors.
- True/false: write a full statement; mix true and false statements.
- If there is any calculation, compute it carefully and double-check the answer.
- Do not put letters or numbers before the options.
Return JSON only, no other text, in this shape:
[{"type":"mc","q":"question text","options":["...","...","...","..."],"answer":0},{"type":"tf","q":"statement","answer":true}]`;
  return `أنت معلم خبير. اكتب ${n} أسئلة ${kindsAr} لطلاب ${level || 'المرحلة الابتدائية'}${t.subj ? ` في مادة ${t.subj}` : ''} عن درس: «${t.lesson}».${t.notes ? `\nملاحظات المعلم: ${t.notes}` : ''}
- غطِّ الأفكار والمهارات الأساسية لهذا الدرس كما يُدرَّس عادةً في هذا الصف، وتدرّج من السهل إلى الأصعب قليلًا.
- اكتب بلغة اسم الدرس.
- السؤال قصير وواضح (أقل من 25 كلمة)، والخيارات قصيرة.
- اختيار من متعدد: 4 خيارات بالضبط، خيار واحد صحيح فقط، والخيارات الخاطئة معقولة ومتقاربة.
- صح وخطأ: اكتب عبارة كاملة، ونوّع بين العبارات الصحيحة والخاطئة.
- إن وُجدت عمليات حسابية فاحسبها بدقة وتحقق من الإجابة مرتين.
- لا تضع حروفًا أو أرقامًا قبل الخيارات.
أعد JSON فقط دون أي نص آخر، بهذا الشكل:
[{"type":"mc","q":"نص السؤال","options":["...","...","...","..."],"answer":0},{"type":"tf","q":"نص العبارة","answer":true}]`;
}
"""

CSS = """
.dlg .seg,.dlg .aimode,.dlg .aitopic,.dlg .aigrid,.dlg .drop{flex-shrink:0}
.aisrc{align-self:stretch!important;display:flex;margin-bottom:6px;padding:4px}
.aisrc button{flex:1;padding:11px 10px!important;font-size:15px!important;font-weight:700;display:inline-flex;align-items:center;justify-content:center;gap:6px}
.aisrc button .ico{width:18px;height:18px}
.aitopic{display:grid;grid-template-columns:1fr 2fr;gap:10px}
.aitopic label{display:flex;flex-direction:column;gap:4px;font-size:13px;font-weight:600;color:var(--muted)}
.aitopic .full{grid-column:1/-1}
.aitopic small{grid-column:1/-1;color:var(--muted);font-size:12px}
@media (max-width:560px){.aitopic{grid-template-columns:1fr}}
"""


def apply(s, rep):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, "function parseAIList(txt) {", TOPIC_PROMPT.strip() + "\nfunction parseAIList(txt) {")
    s = rep(s, "{ icon: 'ai', label: 'كويز فوري من صورة',", "{ icon: 'ai', label: 'كويز فوري بالذكاء الاصطناعي',")
    # dialog: source switch + lesson fields
    s = rep(s, """  let mode = ls.get('rb_ai_mode2') || 'gemini';""", """  let mode = ls.get('rb_ai_mode2') || 'gemini', src = ls.get('rb_ai_src') || 'img';""")
    s = rep(s, """  modal(`<h3 class="aih">${svgI('ai')}كويز فوري من صورة</h3>
    <div class="seg aimode" id="aiMode">""", """  modal(`<h3 class="aih">${svgI('ai')}كويز فوري بالذكاء الاصطناعي</h3>
    <div class="seg aimode aisrc" id="aiSrc"><button data-s="img">${svgI('img')} من صورة</button><button data-s="topic">✏️ من اسم الدرس</button></div>
    <div class="seg aimode" id="aiMode">""")
    s = rep(s, """    <div class="aigrid">
      <label>عدد الأسئلة""", """    <div class="aitopic" id="aiTopic">
      <label>المادة<input class="inp" id="aiSubj" placeholder="مثال: رياضيات" value="${esc(ls.get('rb_ai_subj') || '')}"></label>
      <label>اسم الدرس<input class="inp" id="aiLesson" placeholder="مثال: القسمة على عدد من رقمين" value="${esc(ls.get('rb_ai_lesson') || '')}"></label>
      <label class="full">ملاحظات (اختياري)<input class="inp" id="aiNotes" placeholder="مثال: المنهج السعودي، ركّز على المسائل اللفظية"></label>
      <small>الأسئلة من معلومات الذكاء الاصطناعي العامة عن الدرس، راجعها قبل البدء.</small>
    </div>
    <div class="aigrid">
      <label>عدد الأسئلة""")
    s = rep(s, """<div class="step"><b>2</b><div>افتح <a href="https://claude.ai/new" target="_blank" rel="noopener">محادثة جديدة في Claude</a>، والصق الطلب وأرفق صورة الدرس.</div></div>""",
            """<div class="step"><b>2</b><div>افتح <a href="https://claude.ai/new" target="_blank" rel="noopener">محادثة جديدة في Claude</a>، والصق الطلب <span id="aiStep2">وأرفق صورة الدرس.</span></div></div>""")
    s = rep(s, """      $v('#aiGem').hidden = m !== 'gemini'; $v('#aiCl').hidden = m !== 'claude'; $v('#aiFree').hidden = m !== 'copy'; $v('#aiShot').hidden = m === 'copy';""",
            """      $v('#aiGem').hidden = m !== 'gemini'; $v('#aiCl').hidden = m !== 'claude'; $v('#aiFree').hidden = m !== 'copy'; $v('#aiShot').hidden = m === 'copy' || src === 'topic';
      $v('#aiTopic').hidden = src !== 'topic'; $v('#aiStep2').textContent = src === 'topic' ? 'والصق الطلب فقط.' : 'وأرفق صورة الدرس.';""")
    s = rep(s, """    $v('#aiMode').onclick = e => { const b = e.target.closest('button'); if (b) setMode(b.dataset.m) };
    setMode(mode);""", """    $v('#aiMode').onclick = e => { const b = e.target.closest('button'); if (b) setMode(b.dataset.m) };
    const setSrc = x => { src = x; ls.set('rb_ai_src', x); v.querySelectorAll('#aiSrc button').forEach(b => b.classList.toggle('on', b.dataset.s === x)); setMode(mode); if (x === 'topic') setTimeout(() => $v('#aiLesson').focus(), 30) };
    $v('#aiSrc').onclick = e => { const b = e.target.closest('button'); if (b) setSrc(b.dataset.s) };
    const topic = () => ({ subj: $v('#aiSubj').value.trim(), lesson: $v('#aiLesson').value.trim(), notes: $v('#aiNotes').value.trim() });
    setSrc(src);""")
    s = rep(s, """      if (!f || !/^image\\//.test(f.type)) return; if (mode === 'copy') setMode('gemini');""",
            """      if (!f || !/^image\\//.test(f.type)) return; if (src === 'topic') setSrc('img'); if (mode === 'copy') setMode('gemini');""")
    s = rep(s, """      const o = opts(), txt = aiPrompt(o.n, o.type, o.level);""",
            """      const o = opts(); if (src === 'topic' && !topic().lesson) { $v('#aiErr').textContent = 'اكتب اسم الدرس أولًا.'; return }
      const txt = src === 'topic' ? aiTopicPrompt(o.n, o.type, o.level, topic()) : aiPrompt(o.n, o.type, o.level);""")
    s = rep(s, """      if (!made.length) throw { msg: 'ما قدرت أطلع أسئلة صالحة من هذه الصورة. جرّب صورة أوضح للدرس.' };""",
            """      if (!made.length) throw { msg: src === 'topic' ? 'ما قدرت أطلع أسئلة صالحة. جرّب مرة ثانية أو وضّح اسم الدرس.' : 'ما قدرت أطلع أسئلة صالحة من هذه الصورة. جرّب صورة أوضح للدرس.' };""")
    s = rep(s, """          if (!shot) throw { msg: 'الصق صورة الدرس أولًا (Ctrl + V) أو ارفعها.' };""",
            """          const tp = src === 'topic' ? topic() : null;
          if (tp) { if (!tp.lesson) throw { msg: 'اكتب اسم الدرس أولًا.' }; ls.set('rb_ai_subj', tp.subj); ls.set('rb_ai_lesson', tp.lesson) }
          else if (!shot) throw { msg: 'الصق صورة الدرس أولًا (Ctrl + V) أو ارفعها.' };""")
    s = rep(s, """          qs = mode === 'gemini' ? await geminiGenerate(shot, o.n, o.type, o.level, key) : await aiGenerate(shot, o.n, o.type, o.level, key);""",
            """          qs = mode === 'gemini' ? await geminiGenerate(tp ? null : shot, o.n, o.type, o.level, key, tp) : await aiGenerate(tp ? null : shot, o.n, o.type, o.level, key, tp);""")
    # generators: image is optional
    s = rep(s, """async function geminiGenerate(shot, n, type, level, key) {
  const prompt = aiPrompt(n, type, level), [meta, b64] = shot.split(','), mt = (meta.match(/data:(.*?);/) || [])[1] || 'image/jpeg';""",
            """async function geminiGenerate(shot, n, type, level, key, tp) {
  const prompt = tp ? aiTopicPrompt(n, type, level, tp) : aiPrompt(n, type, level), [meta, b64] = shot ? shot.split(',') : ['', ''], mt = (meta.match(/data:(.*?);/) || [])[1] || 'image/jpeg';""")
    s = rep(s, """body: JSON.stringify({ contents: [{ role: 'user', parts: [{ inlineData: { mimeType: mt, data: b64 } }, { text: prompt }] }], generationConfig: { temperature: 0.4, responseMimeType: 'application/json' } })""",
            """body: JSON.stringify({ contents: [{ role: 'user', parts: [...(shot ? [{ inlineData: { mimeType: mt, data: b64 } }] : []), { text: prompt }] }], generationConfig: { temperature: tp ? 0.6 : 0.4, responseMimeType: 'application/json' } })""")
    s = rep(s, """async function aiGenerate(shot, n, type, level, key) {
  const prompt = aiPrompt(n, type, level);
  const [meta, b64] = shot.split(','); const mt = (meta.match(/data:(.*?);/) || [])[1] || 'image/jpeg';""",
            """async function aiGenerate(shot, n, type, level, key, tp) {
  const prompt = tp ? aiTopicPrompt(n, type, level, tp) : aiPrompt(n, type, level);
  const [meta, b64] = shot ? shot.split(',') : ['', '']; const mt = (meta.match(/data:(.*?);/) || [])[1] || 'image/jpeg';""")
    s = rep(s, """messages: [{ role: 'user', content: [{ type: 'image', source: { type: 'base64', media_type: mt, data: b64 } }, { type: 'text', text: prompt }] }] })""",
            """messages: [{ role: 'user', content: [...(shot ? [{ type: 'image', source: { type: 'base64', media_type: mt, data: b64 } }] : []), { type: 'text', text: prompt }] }] })""")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    return s
