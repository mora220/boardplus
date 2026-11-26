"""BoardPlus redesign: a marker-and-whiteboard identity.
  * Home: the hero is a real whiteboard sheet (graph paper, frame, marker tray); a red tick and the teacher's
    Ruqaa note «ممتاز» are written on it once when the page opens. The join card is a sheet taped beside it.
    Below: the product itself, annotated with red-pen notes, then everything the teacher gets, then the three steps.
  * The app keeps every id and behaviour; only the look changes: marker-blue actions, paper surfaces, a marker-tray
    toolbar, quieter headers, softer student sheets and dialogs.
Palette: paper #FBFCFE, grid #E6ECF5, ink #17213B, marker blue #1F4FD8, correction red #E5313B, highlighter #FFD84D."""
import json, re

LOGO = ('<svg class="bulogo" viewBox="0 0 48 48" aria-hidden="true"><rect x="2" y="2" width="44" height="44" rx="13" fill="#1f4fd8"/>'
        '<rect x="9.5" y="11" width="29" height="20" rx="3.5" fill="#fff"/><path d="M15 21.5l4.6 4.2L29 15.6" fill="none" stroke="#e5313b" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="12" y="34.5" width="24" height="4" rx="2" fill="#fff" opacity=".55"/><rect x="31" y="32.6" width="9" height="7.8" rx="2" fill="#ffd84d"/></svg>')

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect x="2" y="2" width="44" height="44" rx="13" fill="#1f4fd8"/>'
           '<rect x="9.5" y="11" width="29" height="20" rx="3.5" fill="#fff"/><path d="M15 21.5l4.6 4.2L29 15.6" fill="none" stroke="#e5313b" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
           '<rect x="12" y="34.5" width="24" height="4" rx="2" fill="#fff" opacity=".55"/><rect x="31" y="32.6" width="9" height="7.8" rx="2" fill="#ffd84d"/></svg>\n')

TICK = '<svg class="hx-tick" viewBox="0 0 120 90" aria-hidden="true"><path d="M8 50 C 20 58, 30 70, 40 80 C 58 52, 82 24, 112 8" fill="none" stroke="#e5313b" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# a small student sheet in the product mock: a handwritten sum, its name, and an optional mark
def tile(name, sum_, mark=''):
    return f'<div class="hm-t"><div class="hm-p"><span class="hm-w">{sum_}</span>{mark}</div><div class="hm-n"><i></i>{name}</div></div>'

MOCK = ('<div class="hm" aria-hidden="true"><div class="hm-bar"><span class="hm-dots"><i></i><i></i><i></i></span><span class="hm-code">كود الحصة <b>٤٨٢٩١٥</b></span><span class="hm-cnt"><b>٢٤</b> طالبًا</span></div>'
        '<div class="hm-in"><div class="hm-board"><span class="hm-q">١٢ × ٤ = ؟</span><span class="hm-ql">اكتب الناتج على سبورتك</span></div><div class="hm-grid">'
        + tile('سارة', '١٢ × ٤ = ٤٨', '<span class="hm-ok">✓</span>')
        + tile('عمر', '١٢ × ٤ = ٤٦', '<span class="hm-fix">٤٨</span>')
        + tile('ريم', '١٢ × ٤ = ٤٨')
        + tile('يوسف', '٤٠ + ٨ = ٤٨', '<span class="hm-st">ممتاز</span>')
        + tile('لين', '١٢ × ٤ =', '<span class="hm-hand">✋</span>')
        + tile('خالد', '١٢ × ٤ = ٤٨')
        + '</div></div></div>')

HOME = r"""<section id="home">
  <div class="doodles" aria-hidden="true" id="doodles"></div>
  <nav class="home-top gut">
    <div class="word wlogo">""" + LOGO + r"""<span>Board<b>Plus</b></span></div>
    <div class="topr"><div class="datechip" id="hDate" aria-live="off"></div><button class="langbtn" id="langHome" type="button"></button></div>
  </nav>
  <div class="home-in gut">
    <div class="hx-board">
      <div class="hx-sheet">
        <h1 class="hx-h1">كل طالب يحل على سبورته، وأنت تصحح له مباشرة</h1>
        <div class="hx-mark" aria-hidden="true">""" + TICK + r"""<span class="hx-note">ممتاز</span></div>
        <p class="hx-lead">اكتب السؤال أو الصق صورته، والطلاب يحلّون على أجهزتهم في نفس اللحظة. تشوف كل الحلول قدامك، وتصحح بالقلم الأحمر، وتسوي كويز أو لعبة من صورة الدرس خلال ثواني.</p>
        <div class="hx-cta"><button class="btn pri big" type="button" id="heroTeacher"><span>ابدأ كمعلم مجانًا</span></button><button class="btn big hx-ghost" type="button" id="heroStudent">عندي كود الحصة</button></div>
        <p class="hx-fine">تدخل بحساب Google، بدون بطاقة دفع.</p>
      </div>
      <div class="hx-tray" aria-hidden="true"><i class="m1"></i><i class="m2"></i><i class="m3"></i><b class="er"></b></div>
    </div>

    <div class="hx-side">
    <form class="card" id="joinCard" autocomplete="off">
      <span class="hx-tape" aria-hidden="true"></span>
      <div class="welcome"><span class="wave"><svg class="ico"><use href="#i-board"/></svg></span><div><h2>أنا طالب</h2><p class="hint" style="margin:0">الكود موجود على شاشة المعلم</p></div></div>
      <div class="field"><label for="jCode">كود الجلسة</label>
        <input class="inp code num" id="jCode" inputmode="numeric" maxlength="6" placeholder="000000"><div class="jteacher" id="jTeacher" hidden></div></div>
      <div class="field"><label for="jName">اسمك</label>
        <input class="inp" id="jName" maxlength="30" placeholder="اكتب اسمك الأول والثاني"></div>
      <p class="err" id="jErr"></p>
      <button class="btn pri big" id="jGo" type="submit">يلا نبدأ</button>
      <div class="tlink"><button type="button" id="toTeacher">أنا معلم ← دخول بحساب Google</button></div>
    </form>

    <div class="card" id="adminCard" hidden>
      <span class="hx-tape" aria-hidden="true"></span>
      <div class="welcome"><span class="wave"><svg class="ico"><use href="#i-users"/></svg></span><div><h2>دخول المعلم</h2><p class="hint" style="margin:0">سجّل بحساب Google وابدأ أول حصة خلال دقيقة</p></div></div>
      <button class="btn big gbtn" type="button" id="gSign"><svg viewBox="0 0 48 48" width="20" height="20" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/><path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg><span>المتابعة بحساب Google</span></button>
      <p class="err" id="aErr"></p>
      <p class="hint small">نعرض اسمك وصورتك من Google لطلابك داخل الحصة فقط.</p>
      <button class="switch" type="button" id="toStudent">→ أنا طالب</button>
    </div>
    </div>
  </div>

  <section class="hx-show gut" aria-label="شكل الحصة">
    <h2 class="hx-h2">هكذا تبدو حصتك من شاشتك</h2>
    <div class="hx-stage">
      """ + MOCK + r"""
      <p class="hx-ann a1"><span>كل طالب يحل على سبورته، وتشوفها كلها معًا</span></p>
      <p class="hx-ann a2"><span>تصحح بالأحمر ويوصل للطالب فورًا</span></p>
      <p class="hx-ann a3"><span>يرفع يده لما يحتاجك</span></p>
    </div>
  </section>

  <section class="hx-more gut" aria-label="ماذا تجد في المنصة">
    <h2 class="hx-h2">وكل اللي تحتاجه في الحصة نفسها</h2>
    <ul class="hx-list">
      <li><b>كويز بثلاث طرق</b><span>سؤال للكل في نفس الوقت، أو كل طالب بسرعته، أو شد الحبل بين فريقين.</span></li>
      <li><b>أسئلة من صورة الدرس</b><span>صوّر الدرس أو اكتب اسمه، وتطلع لك أسئلة جاهزة تراجعها قبل ما تبدأ.</span></li>
      <li><b>تحليل كل سؤال</b><span>كم طالب جاوب صح وكم غلط، والأسئلة الأصعب تفتحها وتحلها بالقلم.</span></li>
      <li><b>فصولي وكشف الحضور</b><span>أسماء طلاب كل فصل، والطالب يختار اسمه، والحضور والمشاركة يتسجلون لوحدهم.</span></li>
      <li><b>لوحة الصدارة</b><span>نقاط الأختام والكويزات، والخمسة الأوائل فقط على شاشتك حفاظًا على خصوصية الطلاب.</span></li>
      <li><b>اعرض أي شيء</b><span>صورة، صوت، فيديو، يوتيوب، أو ملف باوربوينت وPDF يوصل لكل الطلاب.</span></li>
      <li><b>تحكم كامل</b><span>مؤقت للحل، قفل السبورات، ليزر، وصفحات للسبورة ترجع لها متى ما تحتاج.</span></li>
      <li><b>عربي وإنجليزي</b><span>يشتغل على الجوال والآيباد واللابتوب، والطلاب يدخلون بالكود أو QR بدون حسابات.</span></li>
    </ul>
  </section>

  <section class="hx-steps gut" aria-label="كيف تبدأ">
    <h2 class="hx-h2">تبدأ أول حصة خلال دقيقة</h2>
    <ol class="hx-ol">
      <li><b>سجّل بحساب Google</b><span>بدون نماذج ولا بطاقة.</span></li>
      <li><b>اعرض الكود أو QR</b><span>الطلاب يدخلون من جوالاتهم بأسمائهم.</span></li>
      <li><b>اكتب السؤال وصحّح</b><span>الحلول توصلك لحظة بلحظة.</span></li>
    </ol>
    <button class="btn pri big" type="button" id="heroTeacher2">ابدأ كمعلم مجانًا</button>
  </section>
  <div class="foot gut">BoardPlus · فكرة وتطوير أ. محمد رجب</div>
</section>"""

ADD_I18N = {
    "كل طالب يحل على سبورته، وأنت تصحح له مباشرة": "Every student solves on their own board, and you correct them live",
    "ممتاز": "Excellent", "عندي كود الحصة": "I have a class code", "تدخل بحساب Google، بدون بطاقة دفع.": "Sign in with Google, no card needed.",
    "شكل الحصة": "What a class looks like", "هكذا تبدو حصتك من شاشتك": "This is your class, from your screen",
    "كل طالب يحل على سبورته، وتشوفها كلها معًا": "Every student works on their own board, and you see them all",
    "تصحح بالأحمر ويوصل للطالب فورًا": "Correct in red and the student sees it at once", "يرفع يده لما يحتاجك": "Raises a hand when they need you",
    "ماذا تجد في المنصة": "What you get", "وكل اللي تحتاجه في الحصة نفسها": "And everything else you need, in the same class",
    "كويز بثلاث طرق": "Quizzes, three ways", "سؤال للكل في نفس الوقت، أو كل طالب بسرعته، أو شد الحبل بين فريقين.": "One question for everyone at once, each student at their own pace, or tug of war between two teams.",
    "أسئلة من صورة الدرس": "Questions from a lesson photo", "صوّر الدرس أو اكتب اسمه، وتطلع لك أسئلة جاهزة تراجعها قبل ما تبدأ.": "Snap the lesson or type its name, and get ready questions to review before you start.",
    "تحليل كل سؤال": "Every question analysed", "كم طالب جاوب صح وكم غلط، والأسئلة الأصعب تفتحها وتحلها بالقلم.": "How many got it right and wrong, and the hardest questions open big for you to solve with the pen.",
    "فصولي وكشف الحضور": "My classes and attendance", "أسماء طلاب كل فصل، والطالب يختار اسمه، والحضور والمشاركة يتسجلون لوحدهم.": "Each class's student names, students pick their name, and attendance and participation are recorded for you.",
    "لوحة الصدارة": "Leaderboard", "نقاط الأختام والكويزات، والخمسة الأوائل فقط على شاشتك حفاظًا على خصوصية الطلاب.": "Points from stamps and quizzes, with only the top five on your screen to protect students' privacy.",
    "اعرض أي شيء": "Show anything", "صورة، صوت، فيديو، يوتيوب، أو ملف باوربوينت وPDF يوصل لكل الطلاب.": "An image, audio, video, YouTube, or a PowerPoint or PDF file, sent to every student.",
    "تحكم كامل": "Full control", "مؤقت للحل، قفل السبورات، ليزر، وصفحات للسبورة ترجع لها متى ما تحتاج.": "A solving timer, board lock, a laser, and board pages you can go back to any time.",
    "عربي وإنجليزي": "Arabic and English", "يشتغل على الجوال والآيباد واللابتوب، والطلاب يدخلون بالكود أو QR بدون حسابات.": "Works on phones, iPads and laptops, and students join with the code or QR, no accounts.",
    "كيف تبدأ": "How to start", "تبدأ أول حصة خلال دقيقة": "Your first class in a minute",
    "سجّل بحساب Google": "Sign in with Google", "بدون نماذج ولا بطاقة.": "No forms, no card.",
    "اعرض الكود أو QR": "Show the code or QR", "الطلاب يدخلون من جوالاتهم بأسمائهم.": "Students join from their phones with their names.",
    "اكتب السؤال وصحّح": "Write the question and correct", "الحلول توصلك لحظة بلحظة.": "Answers reach you as they happen.",
    "كود الحصة": "Class code", "طالبًا": "students", "اكتب الناتج على سبورتك": "Write the answer on your board",
}

CSS = r"""
/* ===================== redesign: marker & whiteboard ===================== */
:root{
  --wall:#eef2f8; --surface:#ffffff; --surface-2:#f5f7fb; --ink:#17213b; --muted:#5d6985; --line:#dfe5ef;
  --accent:#1f4fd8; --accent-2:#163aa3; --accent-soft:#e7eefd; --accent-ink:#ffffff;
  --red:#e5313b; --red-soft:#fde8ea; --ok:#16a06a; --ok-soft:#e1f5ec; --hand:#f2b705; --hand-soft:#fff4cf; --hl:#ffd84d;
  --paper:#fbfcfe; --grid:#e6ecf5;
  --shadow:0 1px 0 rgba(23,33,59,.04),0 2px 6px rgba(23,33,59,.05),0 14px 30px -14px rgba(23,33,59,.22);
  --f-hand:"Aref Ruqaa","Readex Pro",serif; --r:10px;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --wall:#0d1322; --surface:#151d31; --surface-2:#1a2440; --ink:#e8edf7; --muted:#98a5c0; --line:#28344f;
  --accent:#7c9cff; --accent-2:#4d6fe0; --accent-soft:#1f2c52; --accent-ink:#0d1322; --paper:#ffffff; --grid:#e6ecf5;
  --shadow:0 1px 0 rgba(0,0,0,.25),0 14px 34px -14px rgba(0,0,0,.6)}}
:root[data-theme="dark"]{
  --wall:#0d1322; --surface:#151d31; --surface-2:#1a2440; --ink:#e8edf7; --muted:#98a5c0; --line:#28344f;
  --accent:#7c9cff; --accent-2:#4d6fe0; --accent-soft:#1f2c52; --accent-ink:#0d1322; --paper:#ffffff; --grid:#e6ecf5;
  --shadow:0 1px 0 rgba(0,0,0,.25),0 14px 34px -14px rgba(0,0,0,.6)}

/* ---------- shared controls ---------- */
.btn{border-radius:10px;font-weight:600;transition:background .15s,border-color .15s,box-shadow .15s,transform .1s}
.btn:hover{background:var(--surface);border-color:color-mix(in srgb,var(--accent) 40%,var(--line))}
.btn.pri{background:var(--accent);border-color:var(--accent);color:var(--accent-ink);box-shadow:0 2px 0 var(--accent-2)}
.btn.pri:hover{background:var(--accent);filter:brightness(1.08)}
.btn.pri:active{transform:translateY(2px);box-shadow:0 0 0 var(--accent-2)}
.btn.big{padding:14px 22px;border-radius:12px;font-size:16.5px}
.btn.on{background:var(--accent-soft);border-color:color-mix(in srgb,var(--accent) 55%,transparent);color:var(--accent)}
.btn.hand{border-color:color-mix(in srgb,var(--hand) 60%,var(--line))}
.btn.hand.on{background:var(--hand);border-color:var(--hand);color:#17213b;box-shadow:0 2px 0 #c79300}
.inp{border:1.5px solid var(--line);background:var(--surface);border-radius:10px}
.inp:focus{border-color:var(--accent);background:var(--surface);box-shadow:0 0 0 4px var(--accent-soft)}
.pill{background:var(--surface);border-color:var(--line)}
.seg{background:var(--surface-2);border:1px solid var(--line);border-radius:10px;padding:2px;gap:2px}
.seg button{border-radius:8px}
.seg button.on{background:var(--surface);color:var(--accent);box-shadow:0 1px 3px rgba(23,33,59,.16)}
.veil{background:rgba(13,19,34,.42);backdrop-filter:blur(6px)}
.dlg{border:0;border-radius:18px;padding:24px;box-shadow:0 2px 0 rgba(23,33,59,.04),0 30px 70px -24px rgba(13,19,34,.55)}
.toast{border-radius:12px;box-shadow:0 14px 30px -14px rgba(13,19,34,.6)}
.word{font-weight:700}
.word b{color:var(--accent);font-weight:700}
.word i{display:none}

/* ---------- app frame ---------- */
.top{background:var(--surface);border-bottom:1px solid var(--line);box-shadow:0 10px 24px -22px rgba(23,33,59,.5)}
.codebox{background:var(--accent-soft);border:1px solid color-mix(in srgb,var(--accent) 18%,transparent);border-radius:12px}
.codebox .lbl{color:color-mix(in srgb,var(--accent) 70%,var(--muted))}
.codebox .val{color:var(--accent)}
.codebox .btn{background:var(--surface);border-color:transparent}
.ava{box-shadow:0 0 0 2px var(--surface),0 0 0 3.5px color-mix(in srgb,var(--accent) 35%,var(--line))}
.board{border-radius:14px;box-shadow:0 0 0 1px var(--line),0 2px 4px rgba(23,33,59,.04),0 22px 44px -24px rgba(23,33,59,.4)}
/* the toolbar is a marker tray */
.tb{background:linear-gradient(#fbfcfe,#edf1f7);border:1px solid #d6dce8;border-radius:16px;padding:6px 8px;box-shadow:inset 0 1px 0 #fff,0 1px 0 rgba(23,33,59,.05),0 16px 30px -18px rgba(23,33,59,.45)}
.tb button{border-radius:10px}
.tb button:hover{background:rgba(31,79,216,.08)}
.tb button[data-t].on{background:var(--accent);color:#fff;box-shadow:0 2px 0 var(--accent-2)}
.tb .sep{background:#d6dce8}
:root[data-theme="dark"] .tb{background:linear-gradient(#1b2540,#141c31);border-color:#2b3756;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 16px 30px -18px rgba(0,0,0,.7)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .tb{background:linear-gradient(#1b2540,#141c31);border-color:#2b3756;box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 16px 30px -18px rgba(0,0,0,.7)}
  :root:not([data-theme="light"]) .tb .sep{background:#2b3756}}
:root[data-theme="dark"] .tb .sep{background:#2b3756}
.tb button[data-t].on .ico{stroke:#fff}
.pager{border-radius:14px;background:linear-gradient(#fbfcfe,#edf1f7);border-color:#d6dce8}
.panel{background:var(--surface)}
.panel-h h3{font-size:17px;font-weight:700}
.grid{gap:14px}
.sc{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:7px;box-shadow:0 1px 2px rgba(23,33,59,.05)}
.sc:hover{border-color:color-mix(in srgb,var(--accent) 50%,var(--line));box-shadow:var(--shadow)}
.sc canvas{border-radius:9px;box-shadow:0 0 0 1px var(--grid)}
.sc .st.on{box-shadow:0 0 0 3px var(--ok-soft)}
.empty{background:var(--surface);border:2px dashed color-mix(in srgb,var(--accent) 30%,var(--line));border-radius:16px}
.empty .bigcode{color:var(--accent)}
.timer{border-radius:10px}
.count{font-weight:700}

/* the app boards carry the same frame as the home board, on a dotted wall */
#teacher .stage,#focus .stage,#student .stage{padding:16px;background-image:radial-gradient(color-mix(in srgb,var(--ink) 10%,transparent) 1px,transparent 1.3px);background-size:18px 18px}
#teacher .board,#focus .board,#student .board{box-shadow:0 0 0 7px #d3dae6,0 0 0 8px #bcc5d4,0 26px 46px -24px rgba(23,33,59,.55)}
:root[data-theme="dark"] #teacher .board,:root[data-theme="dark"] #focus .board,:root[data-theme="dark"] #student .board{box-shadow:0 0 0 7px #2a3550,0 0 0 8px #3a4766,0 26px 46px -24px rgba(0,0,0,.7)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) #teacher .board,:root:not([data-theme="light"]) #focus .board,:root:not([data-theme="light"]) #student .board{box-shadow:0 0 0 7px #2a3550,0 0 0 8px #3a4766,0 26px 46px -24px rgba(0,0,0,.7)}}
.sc canvas{box-shadow:0 0 0 3px #e3e8f0}
/* the teacher's actions sit together in one group */
.tgrp{display:flex;align-items:center;gap:2px;background:var(--surface-2);border:1px solid var(--line);border-radius:12px;padding:3px;flex-wrap:wrap}
.tgrp .btn{border-color:transparent;background:transparent;padding:7px 10px;border-radius:9px}
.tgrp .btn:hover{background:var(--surface);border-color:transparent;box-shadow:0 1px 2px rgba(23,33,59,.12)}
.tgrp .btn.on{background:var(--surface);color:var(--accent);box-shadow:0 1px 2px rgba(23,33,59,.12)}
.tgrp .btn.warn.on{background:var(--red-soft);color:var(--red)}
#tCls{border-style:dashed}
#tCls.on{border-style:solid}
/* quiz: three ways to play, one family */
#qRace{background:#17213b;border-color:#17213b;color:#fff;box-shadow:0 2px 0 #000}
#qTug{box-shadow:0 2px 0 #7a1f4a}
#qzBuild .top,#qzRun .top,#qzStu .top,#lbView .top{box-shadow:0 10px 24px -22px rgba(23,33,59,.5)}
/* ---------- home ---------- */
#home{background:var(--wall)}
#home::before{display:none}
.doodles span{color:var(--accent);opacity:.06}
.home-top{max-width:1180px;padding-block:20px}
.wlogo{gap:10px}.wlogo .bulogo{width:34px;height:34px}
.home-top .word{font-size:25px}
.home-in{max-width:1180px;grid-template-columns:minmax(0,1.5fr) minmax(310px,.95fr);gap:0;align-items:center;padding-block:10px 56px}
.hx-board{position:relative;z-index:1;background:#c9d1de;border-radius:22px;padding:12px;box-shadow:inset 0 1px 0 #e3e8f0,0 2px 0 #b3bccb,0 30px 60px -30px rgba(23,33,59,.45)}
.hx-sheet{position:relative;border-radius:12px;padding:clamp(28px,4.4vw,56px) clamp(24px,4vw,52px) 44px;color:#17213b;
  background-color:var(--paper);background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:28px 28px;background-position:-1px -1px;
  box-shadow:inset 0 0 0 1px rgba(23,33,59,.06),inset 0 6px 14px -10px rgba(23,33,59,.25);display:flex;flex-direction:column;gap:18px}
.hx-h1{margin:0;font-family:var(--f-display);font-weight:700;font-size:clamp(34px,4.9vw,60px);line-height:1.18;letter-spacing:-.015em;color:#17213b;max-width:13.5em;text-wrap:balance}
.hx-mark{position:absolute;inset-inline-end:clamp(22px,4vw,56px);bottom:clamp(22px,2.4vw,34px);width:clamp(92px,9vw,118px);pointer-events:none;transform:rotate(-4deg)}
.hx-tick{display:block;width:100%;height:auto;overflow:visible}
.hx-tick path{stroke-dasharray:200;stroke-dashoffset:200;animation:hxDraw .55s cubic-bezier(.6,.1,.4,1) .55s forwards}
.hx-note{display:block;margin-top:-10px;text-align:center;font-family:var(--f-hand);font-weight:700;font-size:clamp(30px,3.6vw,44px);line-height:1;color:var(--red);opacity:0;transform:translateY(6px) rotate(-6deg);animation:hxNote .45s ease-out 1.05s forwards}
@keyframes hxDraw{to{stroke-dashoffset:0}}
@keyframes hxNote{to{opacity:1;transform:rotate(-6deg)}}
.hx-lead{margin:0;font-size:clamp(16px,1.5vw,18.5px);line-height:1.8;color:#4b5672;max-width:46ch;text-wrap:pretty}
.hx-cta{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:6px}
.hx-ghost{background:#fff;border:1.5px solid #c9d3e4;color:#17213b}
.hx-ghost:hover{background:#fff;border-color:#1f4fd8;color:#1f4fd8}
.hx-fine{margin:-4px 0 0;font-size:13.5px;color:#6a7591}
.hx-tray{position:absolute;bottom:-11px;inset-inline-start:12%;width:46%;height:16px;border-radius:5px 5px 9px 9px;background:linear-gradient(#e7ebf2,#b7c0cf);box-shadow:0 6px 10px -6px rgba(23,33,59,.45);display:flex;align-items:flex-start;gap:12px;padding:0 18px}
.hx-tray i{display:block;height:9px;width:64px;margin-top:-5px;border-radius:5px 2px 2px 5px;position:relative;box-shadow:inset 0 -2px 0 rgba(0,0,0,.15)}
.hx-tray i::after{content:"";position:absolute;inset-inline-end:-14px;top:1px;width:16px;height:7px;border-radius:2px 5px 5px 2px;background:#f3f5f9;box-shadow:inset 0 -2px 0 rgba(0,0,0,.08)}
.hx-tray .m1{background:#1f4fd8}.hx-tray .m2{background:#e5313b}.hx-tray .m3{background:#17213b}
.hx-tray .er{display:block;margin-inline-start:auto;margin-top:-9px;width:46px;height:14px;border-radius:4px;background:linear-gradient(#5b6578 0 55%,#efe7d6 55%)}
.hx-side{position:relative;z-index:2;margin-inline-start:-34px;display:flex;flex-direction:column}
.hx-side .card{position:relative;border:0;border-radius:6px 6px 16px 16px;padding:30px 26px 24px;box-shadow:0 1px 0 rgba(23,33,59,.05),0 3px 8px rgba(23,33,59,.06),0 34px 60px -30px rgba(23,33,59,.5)}
.hx-tape{position:absolute;top:-13px;left:50%;width:120px;height:26px;transform:translateX(-50%) rotate(-2.5deg);background:rgba(255,216,77,.72);box-shadow:0 1px 2px rgba(23,33,59,.12);border-radius:2px;
  -webkit-mask:linear-gradient(90deg,transparent 0 3px,#000 3px calc(100% - 3px),transparent 0);mask:linear-gradient(90deg,transparent 0 3px,#000 3px calc(100% - 3px),transparent 0)}
.hx-side .card .welcome .wave{background:var(--accent);color:#fff}
.hx-side .inp.code{font-size:32px;letter-spacing:.38em;padding:12px;background:var(--surface-2);border-style:dashed}
.hx-side .inp.code:focus{border-style:solid}
.hx-h2{margin:0 0 22px;font-family:var(--f-display);font-weight:700;font-size:clamp(24px,2.8vw,34px);letter-spacing:-.01em;text-wrap:balance}
.hx-show,.hx-more,.hx-steps{max-width:1180px;width:100%;margin:0 auto;padding-block:30px}
/* the product, annotated in red pen */
.hx-stage{position:relative;padding:8px 0 0}
.hm{background:var(--surface);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow);overflow:hidden;max-width:880px}
.hm-bar{display:flex;align-items:center;gap:14px;padding:10px 16px;border-bottom:1px solid var(--line);font-size:13px;color:var(--muted)}
.hm-dots{display:flex;gap:6px;direction:ltr}.hm-dots i{width:10px;height:10px;border-radius:50%;background:var(--line)}
.hm-code{margin-inline-start:auto;background:var(--accent-soft);color:var(--accent);border-radius:9px;padding:3px 10px}
.hm-code b{font-family:var(--f-display);letter-spacing:.12em;margin-inline-start:6px}
.hm-cnt{background:var(--surface-2);border-radius:9px;padding:3px 10px}
.hm-in{display:grid;grid-template-columns:1.05fr 1fr;gap:16px;padding:16px;background:var(--wall)}
.hm-board{background-color:#fbfcfe;background-image:linear-gradient(#e6ecf5 1px,transparent 1px),linear-gradient(90deg,#e6ecf5 1px,transparent 1px);background-size:22px 22px;border-radius:12px;box-shadow:0 0 0 1px var(--line);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;min-height:230px;color:#17213b}
.hm-q{font-family:var(--f-hand);font-size:44px;font-weight:700;color:#1f4fd8}
.hm-ql{font-size:13px;color:#5d6985}
.hm-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.hm-t{background:var(--surface);border-radius:10px;padding:5px;box-shadow:0 0 0 1px var(--line)}
.hm-p{position:relative;aspect-ratio:16/11;border-radius:7px;background-color:#fbfcfe;background-image:linear-gradient(#edf1f7 1px,transparent 1px),linear-gradient(90deg,#edf1f7 1px,transparent 1px);background-size:12px 12px;display:grid;place-items:center;overflow:hidden}
.hm-w{font-family:var(--f-hand);font-weight:700;font-size:clamp(13px,1.35vw,17px);color:#17213b;white-space:nowrap;direction:rtl}
.hm-ok{position:absolute;inset-inline-start:6px;bottom:0;font-size:24px;font-weight:900;color:#e5313b;transform:rotate(-8deg)}
.hm-fix{position:absolute;inset-inline-start:8px;top:2px;font-family:var(--f-hand);font-weight:700;font-size:18px;color:#e5313b;transform:rotate(-8deg)}
.hm-st{position:absolute;inset-inline-start:4px;bottom:3px;font-family:var(--f-hand);font-weight:700;font-size:13px;color:#e5313b;border:2px solid #e5313b;border-radius:6px;padding:0 5px;transform:rotate(-10deg);opacity:.9}
.hm-hand{position:absolute;inset-inline-end:4px;top:4px;background:#f2b705;border-radius:99px;font-size:12px;padding:1px 6px}
.hm-n{display:flex;align-items:center;gap:5px;font-size:12px;font-weight:600;padding:4px 2px 0;color:var(--ink)}
.hm-n i{width:7px;height:7px;border-radius:50%;background:var(--ok)}
.hx-ann{position:absolute;margin:0;font-family:var(--f-hand);font-weight:700;font-size:clamp(20px,2vw,26px);line-height:1.25;color:var(--red);max-width:230px}
.hx-ann span{display:block}
.hx-ann::before{content:"";position:absolute;width:64px;height:40px;border:3px solid var(--red);border-color:var(--red) transparent transparent transparent;border-radius:50%}
.hx-ann.a1{inset-inline-end:0;top:40px}.hx-ann.a1::before{inset-inline-start:-66px;top:4px;transform:rotate(-20deg)}
.hx-ann.a2{inset-inline-end:0;top:46%}.hx-ann.a2::before{inset-inline-start:-66px;top:6px;transform:rotate(10deg)}
.hx-ann.a3{inset-inline-end:40px;bottom:-6px}.hx-ann.a3::before{inset-inline-start:-66px;top:-14px;transform:rotate(-30deg)}
/* everything else: a ruled list, not cards */
.hx-list{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:48px}
.hx-list li{display:grid;grid-template-columns:28px 1fr;column-gap:12px;row-gap:3px;padding:16px 0;border-bottom:1px solid var(--line)}
.hx-list li::before{content:"";grid-row:1/3;width:22px;height:22px;margin-top:3px;background:no-repeat center/contain url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13.5l5.5 5L21 5' fill='none' stroke='%23e5313b' stroke-width='3.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")}
.hx-list b{font-family:var(--f-display);font-weight:600;font-size:17px}
.hx-list span{color:var(--muted);font-size:15px;line-height:1.7}
/* the three steps really are a sequence */
.hx-ol{list-style:none;margin:0 0 26px;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;counter-reset:st}
.hx-ol li{counter-increment:st;display:flex;flex-direction:column;gap:4px;padding-top:56px;position:relative}
.hx-ol li::before{content:counter(st);position:absolute;top:0;inset-inline-start:0;width:44px;height:44px;border-radius:50%;border:2.5px solid var(--accent);color:var(--accent);display:grid;place-items:center;font-family:var(--f-display);font-weight:700;font-size:20px}
.hx-ol li::after{content:"";position:absolute;top:22px;inset-inline-start:56px;inset-inline-end:-10px;border-top:2px dashed color-mix(in srgb,var(--accent) 35%,var(--line))}
.hx-ol li:last-child::after{display:none}
.hx-ol b{font-family:var(--f-display);font-weight:600;font-size:18px}
.hx-ol span{color:var(--muted)}
#home .foot{border-top:1px solid var(--line);margin-top:20px;padding-block:22px}
[dir="ltr"] .hx-mark{transform:rotate(4deg)}
[dir="ltr"] .hm-w{direction:ltr}
[dir="ltr"] .hx-note{font-size:clamp(22px,2.4vw,30px)}
.hm-cnt b{font-weight:600}
@media (max-width:1100px){.hx-ann{display:none}.hm{max-width:none}}
@media (max-width:900px){
  .home-in{grid-template-columns:1fr;gap:30px;padding-block:4px 30px}
  .hx-side{margin:0;order:2}
  .hx-board{order:1}
  .hx-h1{font-size:clamp(28px,7.4vw,40px);max-width:none;padding-inline-end:84px}
  .hx-mark{width:84px;top:16px;bottom:auto}.hx-note{font-size:28px}
  .hx-lead{font-size:15.5px}
  .hx-list{grid-template-columns:1fr}
  .hm-in{grid-template-columns:1fr}.hm-board{min-height:150px}
  .hx-ol{grid-template-columns:1fr;gap:12px}.hx-ol li{padding-top:0;padding-inline-start:58px;min-height:44px;justify-content:center}.hx-ol li::after{display:none}
}
@media (max-width:520px){
  .hx-board{padding:8px;border-radius:18px}
  .hx-sheet{padding:22px 18px 30px;gap:14px}
  .hx-lead{display:none}
  .hx-cta .btn{flex:1}
  .hx-tray{width:60%;inset-inline-start:8%}
  .hx-tray i{width:44px}
  .hm-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (prefers-reduced-motion:reduce){.hx-tick path{stroke-dashoffset:0}.hx-note{opacity:1;transform:rotate(-6deg)}}
"""

JS = r"""
$('#heroStudent').onclick = () => { if ($('#joinCard').hidden) $('#toStudent').click(); $('#joinCard').scrollIntoView({ behavior: 'smooth', block: 'center' }); setTimeout(() => $('#jCode').focus(), 350) };
$('#heroTeacher2').onclick = () => $('#heroTeacher').click();
"""


def apply(s, rep):
    s = rep(s, '    <button class="btn" id="tAdmin" title="المعلمين" hidden>', '    <div class="tgrp"><button class="btn" id="tAdmin" title="المعلمين" hidden>')
    s = rep(s, '<span class="hide-md">جلسة جديدة</span></button>\n', '<span class="hide-md">جلسة جديدة</span></button></div>\n')
    # the home page
    m = re.findall(r'<section id="home">.*?\n</section>', s, re.S)
    assert len(m) == 1, len(m)
    s = s.replace(m[0], HOME)
    # the look: after every other rule
    s = rep(s, "@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}\n</style>",
            CSS.strip() + "\n@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}\n</style>")
    s = rep(s, "$('#heroTeacher').onclick = () => {", JS.strip() + "\n$('#heroTeacher').onclick = () => {")
    s = rep(s, 'const I18N = {', 'const I18N = {' + json.dumps(ADD_I18N, ensure_ascii=False)[1:-1] + ',')
    s = s.replace('<meta name="theme-color" content="#2f5bd3">', '<meta name="theme-color" content="#1f4fd8">')
    return s
