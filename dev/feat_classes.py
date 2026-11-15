"""Teacher classes: the teacher keeps their classes on their account, chooses the class for each lesson
(students then pick their name from a list) or free entry (students type their name)."""
import json

ADD_I18N = {
    "فصولي": "My classes", "فصولي وأسماء الطلاب": "My classes and student names", "فصل الحصة": "Class for this lesson", "دخول حر": "Free entry",
    "✍️ دخول حر: الطالب يكتب اسمه": "✍️ Free entry: students type their name", "إضافة فصل": "Add a class", "تعديل": "Edit",
    "لأي فصل هذه الحصة؟": "Which class is this lesson for?", "الطلاب يختارون أسماءهم من قائمة الفصل": "Students pick their name from the class list",
    "حذف الفصل؟": "Delete the class?", "تأكيد": "Confirm", "تأكيد ✓": "Confirm ✓", "اختر اسمك ثم اضغط تأكيد": "Choose your name, then press confirm",
    "ابحث عن اسمك": "Search for your name", "طالب": "students", "حفظ": "Save", "اربط الطالب باسمه": "Link the student to his name", "✍️ اكتب اسمًا آخر": "✍️ Type another name", "اختر اسمك من القائمة.": "Choose your name from the list.",
}

CSS = r"""
.clsbtn{max-width:190px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:700}
.clsbtn.on{background:#e8f0ff;border-color:#2f5bd3;color:#2f5bd3}
.clsl{display:flex;flex-direction:column;gap:8px;max-height:52vh;overflow:auto}
.clsi{display:flex;align-items:center;gap:8px;border:1.5px solid var(--line);border-radius:12px;padding:10px 12px;cursor:pointer;background:var(--surface)}
.clsi.on{border-color:var(--accent);background:var(--accent-soft,#eef3ff)}
.clsi input{width:18px;height:18px;accent-color:var(--accent)}
.clsi b{flex:1}
.clsi small{color:var(--muted)}
.clsi .btn{height:32px;padding:0 10px}
.clsi.lk{opacity:.55;cursor:not-allowed}
.clslock{margin:0;padding:8px 12px;border-radius:10px;background:#fff6dd;color:#7a5600;font-size:13px}
"""

JS = r"""
/* ======================= my classes ======================= */
async function loadClasses() { return (await DB.get(BANK() + '/classes').catch(() => null)) || {} }
function renderClsChip() {
  const b = $('#tCls'); if (!b) return; const c = T.clist && T.clist.names && T.clist.names.length ? T.clist : null;
  b.classList.toggle('on', !!c); $('#tClsName').textContent = c ? `👥 ${c.name || 'الفصل'}` : '✍️ دخول حر';
  b.title = c ? 'الطلاب يختارون أسماءهم من قائمة الفصل' : '✍️ دخول حر: الطالب يكتب اسمه';
}
const clsLocked = () => !!(T.st && T.st.size);       // once students are in, the lesson keeps its class (a new lesson for another class)
const curCls = () => (T.clist && T.clist.id) || '';
async function applyClass(id, all) {
  if (!T.code) return; if (clsLocked() && (id || '') !== curCls()) return toast('لا يمكن تغيير الفصل بعد دخول الطلاب. ابدأ حصة جديدة للفصل الآخر', true);
  if (!id) { await DB.remove(`sessions/${T.code}/clist`); ls.set('rb_lastcls', 'free'); return toast('✍️ دخول حر: الطالب يكتب اسمه') }
  const c = all[id]; if (!c) return; await DB.set(`sessions/${T.code}/clist`, { id, name: c.name || 'الفصل', names: c.names || [] }); ls.set('rb_lastcls', id);
  toast(`👥 ${c.name || 'الفصل'}`);
}
async function openClasses(opts = {}) {
  if (!T.code) return; const all = await loadClasses(), ids = Object.keys(all).sort((a, b) => String(all[a].name).localeCompare(String(all[b].name), 'ar'));
  let pick = clsLocked() ? curCls() : opts.pick !== undefined ? opts.pick : (T.clist && T.clist.id && all[T.clist.id] ? T.clist.id : (T.clist ? '' : ''));
  if (opts.ask) { const last = ls.get('rb_lastcls'); pick = last && last !== 'free' && all[last] ? last : '' }
  modal(`<h3>👥 ${opts.ask ? 'لأي فصل هذه الحصة؟' : 'فصولي'}</h3>
    ${clsLocked() && !opts.ask ? `<p class="clslock">🔒 فصل هذه الحصة ثابت بعد دخول الطلاب، حتى لا يختلط الحضور. لفصل آخر اضغط «حصة جديدة».</p>` : ''}
    <div class="clsl">${ids.map(id => `<label class="clsi ${pick === id ? 'on' : ''}" data-id="${id}"><input type="radio" name="cls" value="${id}" ${pick === id ? 'checked' : ''}><b>${esc(all[id].name || 'الفصل')}</b><small>${(all[id].names || []).length} طالب</small>
        <button class="btn" type="button" data-ed="${id}">✏️ تعديل</button><button class="btn" type="button" data-del="${id}" title="حذف">${svgI('trash')}</button></label>`).join('')}
      <label class="clsi ${!pick ? 'on' : ''}" data-id=""><input type="radio" name="cls" value="" ${!pick ? 'checked' : ''}><b>✍️ دخول حر: الطالب يكتب اسمه</b></label></div>
    <div class="row"><button class="btn" id="clsAdd">＋ إضافة فصل</button><span class="grow"></span><button class="btn" data-close>إلغاء</button><button class="btn pri" id="clsOk">تأكيد</button></div>`, (v, close) => {
    v.querySelectorAll('.clsi').forEach(l => l.onclick = e => { if (e.target.closest('[data-ed],[data-del]')) return; if (clsLocked() && l.dataset.id !== curCls()) { e.preventDefault(); return toast('لا يمكن تغيير الفصل بعد دخول الطلاب. ابدأ حصة جديدة للفصل الآخر', true) } pick = l.dataset.id; v.querySelectorAll('.clsi').forEach(x => { x.classList.toggle('on', x === l); x.querySelector('input').checked = x === l }) });
    if (clsLocked()) v.querySelectorAll('.clsi').forEach(l => { if (l.dataset.id !== curCls()) { l.classList.add('lk'); l.querySelector('input').disabled = true } });
    v.querySelectorAll('[data-ed]').forEach(b => b.onclick = e => { e.preventDefault(); close(); editClass(b.dataset.ed, all[b.dataset.ed]) });
    v.querySelectorAll('[data-del]').forEach(b => b.onclick = async e => { e.preventDefault(); const id = b.dataset.del; close(); if (await ask('حذف الفصل؟', all[id].name || '', 'حذف')) { await DB.remove(`${BANK()}/classes/${id}`); if (T.clist && T.clist.id === id) await DB.remove(`sessions/${T.code}/clist`) } openClasses() });
    v.querySelector('#clsAdd').onclick = () => { close(); editClass(null) };
    v.querySelector('#clsOk').onclick = async () => { close(); await applyClass(pick, all) };
  });
}
function editClass(id, c) {
  modal(`<div class="clform"><h3>👥 ${id ? 'تعديل' : 'إضافة فصل'}</h3>
    <label>اسم الفصل<input class="inp" id="ceName" placeholder="مثال: خامس أ" value="${esc((c && c.name) || '')}"></label>
    <label>اكتب كل اسم في سطر<textarea class="inp" id="ceNames">${esc(((c && c.names) || []).join('\n'))}</textarea></label>
    <div class="row"><button class="btn" data-close>إلغاء</button><button class="btn pri" id="ceOk">حفظ</button></div></div>`, (v, close) => {
    v.querySelector('#ceOk').onclick = async () => {
      const names = [...new Set(v.querySelector('#ceNames').value.split(/\n+/).map(x => x.trim().replace(/\s+/g, ' ').slice(0, 30)).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'ar', { numeric: true }));
      if (!names.length) return toast('اكتب الأسماء أولًا', true);
      const cid = id || 'c' + uid(), name = v.querySelector('#ceName').value.trim().slice(0, 40) || 'الفصل';
      await DB.set(`${BANK()}/classes/${cid}`, { name, names });
      if (T.clist && T.clist.id === cid) await DB.set(`sessions/${T.code}/clist`, { id: cid, name, names });
      close(); openClasses({ pick: cid });
    };
  });
}
function pickClassName(cur) {
  return new Promise(res => {
    const names = T.clist.names, taken = new Map(); T.st.forEach((x, sid) => { const n = x.info && x.info.name; if (n) taken.set(n, sid) });
    modal(`<h3>👥 اربط الطالب باسمه</h3><p class="muted">اسمه الآن: <b>${esc(cur || '')}</b> · اختر اسمه من قائمة ${esc(T.clist.name || 'الفصل')}</p>
      <div class="jnames" style="max-height:52vh;overflow:auto">${names.map(n => `<button type="button" class="jn ${n === cur ? 'on' : ''}" data-n="${esc(n)}">${esc(n)}${taken.has(n) && n !== cur ? ' ✓' : ''}</button>`).join('')}</div>
      <div class="row"><button class="btn" id="pcType">✍️ اكتب اسمًا آخر</button><span class="grow"></span><button class="btn" data-close>إلغاء</button></div>`, (v, close) => {
      let done = false; const fin = x => { if (done) return; done = true; close(); res(x) };
      v.querySelectorAll('.jn').forEach(b => b.onclick = () => fin(b.dataset.n));
      v.querySelector('#pcType').onclick = async () => { done = true; close(); res(await askText('اسم الطالب', cur, 'حفظ الاسم')) };
      v.querySelector('[data-close]').addEventListener('click', () => fin(null));
    });
  });
}
async function afterNewSession() {
  const all = await loadClasses(); if (!Object.keys(all).length) return;
  openClasses({ ask: true });
}
"""


def apply(s, rep, target):
    s = rep(s, '.selbox{', CSS.strip() + '\n.selbox{')
    s = rep(s, '    <span class="timer" id="tTimer" hidden></span>',
            '    <button class="btn clsbtn" id="tCls" type="button"><span id="tClsName">✍️ دخول حر</span></button>\n    <span class="timer" id="tTimer" hidden></span>')
    s = rep(s, "      { icon: 'clist', label: 'قائمة أسماء الفصل', onClick: openClassList },", "      { icon: 'clist', label: 'فصولي وأسماء الطلاب', onClick: () => openClasses() },")
    s = rep(s, "  T.unsubs.push(DB.onValue(b + '/clist', v => { T.clist = v || null; attSync() }));",
            "  T.unsubs.push(DB.onValue(b + '/clist', v => { T.clist = v || null; renderClsChip(); attSync() }));")
    # wire the chip, and ask for the class whenever a new lesson starts
    s = rep(s, "  $('#tNew').onclick = async () => {", "  $('#tCls').onclick = () => openClasses();\n  $('#tNew').onclick = async () => {")
    s = rep(s, "await DB.remove(`sessions/${old}`); attach(await createSession()) } };", "await DB.remove(`sessions/${old}`); attach(await createSession()); afterNewSession() } };")
    s = rep(s, "  attach(code || await createSession());\n", "  const fresh = !code; attach(code || await createSession()); if (fresh) afterNewSession();\n") if target == 'rb' else \
        rep(s, "    attach(code || await createSession());\n  } catch (e) {", "    const fresh = !code; attach(code || await createSession()); if (fresh) afterNewSession();\n  } catch (e) {")
    s = rep(s, "/* ======================= STUDENT ======================= */", JS.strip() + "\n\n/* ======================= STUDENT ======================= */")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    # the teacher links a student to his name from the class list
    s = rep(s, "  const name = await askText('اسم الطالب', s.info.name, 'حفظ الاسم'); if (!name || name === s.info.name) return;",
            "  const name = T.clist && T.clist.names && T.clist.names.length ? await pickClassName(s.info.name) : await askText('اسم الطالب', s.info.name, 'حفظ الاسم'); if (!name || name === s.info.name) return;")
    # with a class list on, a student can only join with a name from the list
    s = rep(s, "  if (!name) { err.textContent = 'اكتب اسمك قبل الدخول.'; $('#jName').focus(); return }\n",
            "  if (!name) { err.textContent = $('#jList') && !$('#jList').hidden ? 'اختر اسمك من القائمة.' : 'اكتب اسمك قبل الدخول.'; $('#jName').focus(); return }\n"
            "  if (/^\\d{6}$/.test(code) && !$('#jName').readOnly) { const cl = await DB.get(`sessions/${code}/clist`).catch(() => null); if (cl && cl.names && cl.names.length && !cl.names.includes(name)) { err.textContent = 'اختر اسمك من القائمة.'; classPicker(code); return } }\n")
    return s
