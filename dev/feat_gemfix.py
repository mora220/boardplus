"""Gemini: try reliable models first, and if one answers with nothing usable, move on to the next one."""
def apply(s, rep):
    s = rep(s, "  const cached = ls.get('rb_gm_model'); if (cached && models.includes(cached)) models = [cached, ...models.filter(m => m !== cached)];\n  if (!models.length) models = ['gemini-flash-latest', 'gemini-flash-lite-latest'];",
            "  const PREF = ['gemini-2.5-flash', 'gemini-flash-latest', 'gemini-2.0-flash', 'gemini-2.5-flash-lite', 'gemini-flash-lite-latest'];\n"
            "  models = [...PREF.filter(m => !models.length || models.includes(m)), ...models.filter(m => !PREF.includes(m))];\n"
            "  const cached = ls.get('rb_gm_model'); if (cached && models.includes(cached)) models = [cached, ...models.filter(m => m !== cached)];")
    s = rep(s, "  for (const model of models.slice(0, 4)) {", "  for (const model of models.slice(0, 6)) {")
    s = rep(s, "      ls.set('rb_gm_model', model); return parseAIList(txt);\n    }",
            "      try { const qs = parseAIList(txt); if (qs && qs.length) { ls.set('rb_gm_model', model); return qs } } catch (e) {}\n"
            "      if (ls.get('rb_gm_model') === model) ls.set('rb_gm_model', '');\n"
            "      last = { status: 200, t: 'empty or unreadable answer from ' + model, g: true }; continue;\n    }")
    s = rep(s, "    return `حصل خطأ من Gemini${e.status ? ` (${e.status})` : ''}. حاول مرة ثانية.`;",
            "    return `حصل خطأ من Gemini${e.status ? ` (${e.status})` : ''}. حاول مرة ثانية.` + (t ? `\\n${String(t).replace(/\\s+/g, ' ').slice(0, 160)}` : '');")
    s = rep(s, '.err{color:var(--red);font-size:14px;min-height:1.2em;margin:0}', '.err{color:var(--red);font-size:14px;min-height:1.2em;margin:0;white-space:pre-line;overflow-wrap:anywhere}')
    return s
