/* =====================================================================
   BoardPlus realtime server — Cloudflare Worker + Durable Objects (SQLite)
   ---------------------------------------------------------------------
   Rooms (one Durable Object each):
     s:<6 digits>  a class session (board, quiz, leaderboard)
     g:<4 digits>  a QuizRagab game
     b:<uid>       a teacher's private question bank
     d             the teachers directory (profiles, settings, stats)
   Each room is a small JSON tree with Firebase-like set/update/subscribe,
   access rules per room kind, and debounced persistence to SQLite.
   ===================================================================== */
import { DurableObject } from 'cloudflare:workers';

const FLUSH_MS = 8000;                // how long writes wait before being saved
const EXPIRE_MS = 12 * 3600 * 1000;   // sessions and games are deleted 12h after they start
const CHUNK_MAX = 1500000;            // max characters stored in one row

/* ---------------- helpers ---------------- */
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
const segsOf = p => String(p || '').split('/').filter(Boolean);
function getIn(o, s) { for (const k of s) { if (o == null || typeof o !== 'object') return null; o = o[k] } return o === undefined ? null : o }
function setIn(root, s, v) {
  if (!s.length) return v == null ? null : v;
  const top = (root && typeof root === 'object') ? root : {};
  let o = top; const stack = [];
  for (let i = 0; i < s.length - 1; i++) { const k = s[i]; if (o[k] == null || typeof o[k] !== 'object') o[k] = {}; stack.push([o, k]); o = o[k] }
  const last = s[s.length - 1];
  if (v == null) {
    delete o[last];
    for (let i = stack.length - 1; i >= 0; i--) { const [p, k] = stack[i]; if (Object.keys(p[k]).length === 0) delete p[k]; else break }
  } else o[last] = v;
  return Object.keys(top).length ? top : null;
}
function clean(v) {                     // drop undefined/empty, keep JSON-safe values
  if (v == null) return null;
  if (typeof v !== 'object') return (typeof v === 'number' && !isFinite(v)) ? null : v;
  if (Array.isArray(v)) return v.map(clean);
  const o = {}; for (const k in v) { if (!k || k.includes('/') || k.startsWith('__')) continue; const c = clean(v[k]); if (c != null) o[k] = c }
  return Object.keys(o).length ? o : null;
}
function stamp(v, now) {                // {".sv":"timestamp"} → server time
  if (v && typeof v === 'object') { if (v['.sv'] === 'timestamp') return now; for (const k in v) v[k] = stamp(v[k], now) }
  return v;
}
const ROOM_RE = /^(s:\d{6}|g:\d{4}|b:[A-Za-z0-9_-]{1,128}|d)$/;

/* ---------------- Firebase ID token verification ---------------- */
let JWKS = null, JWKS_EXP = 0;
async function jwks() {
  if (JWKS && Date.now() < JWKS_EXP) return JWKS;
  const r = await fetch('https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com');
  if (!r.ok) throw new Error('jwks ' + r.status);
  const j = await r.json(), m = (r.headers.get('cache-control') || '').match(/max-age=(\d+)/);
  JWKS = j.keys || []; JWKS_EXP = Date.now() + (m ? +m[1] * 1000 : 3600e3);
  return JWKS;
}
const b64u = s => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4)), c => c.charCodeAt(0));
const dec = s => JSON.parse(new TextDecoder().decode(b64u(s)));
async function verify(token, env) {
  if (!token) return null;
  if (env.DEV_AUTH === '1' && token.startsWith('dev:')) {           // local testing only
    const [, uid, email, ...n] = token.split(':');
    return { uid, email: (email || '').toLowerCase(), name: decodeURIComponent(n.join(':') || uid), picture: '', verified: true };
  }
  const parts = token.split('.'); if (parts.length !== 3) return null;
  const [h, p, s] = parts; let head, pay;
  try { head = dec(h); pay = dec(p) } catch (e) { return null }
  const proj = env.FIREBASE_PROJECT_ID, now = Math.floor(Date.now() / 1000);
  if (head.alg !== 'RS256' || pay.aud !== proj || pay.iss !== 'https://securetoken.google.com/' + proj) return null;
  if (!pay.sub || pay.exp < now || pay.iat > now + 300) return null;
  const jwk = (await jwks()).find(k => k.kid === head.kid); if (!jwk) return null;
  const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
  const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64u(s), new TextEncoder().encode(h + '.' + p));
  if (!ok) return null;
  return { uid: pay.sub, email: String(pay.email || '').toLowerCase(), name: pay.name || '', picture: pay.picture || '', verified: !!pay.email_verified };
}
function isAdmin(id, env) {
  if (!id || !id.email || !id.verified) return false;
  return String(env.ADMIN_EMAILS || '').toLowerCase().split(/[\s,;]+/).filter(Boolean).includes(id.email);
}
const bearer = req => (req.headers.get('authorization') || '').replace(/^Bearer\s+/i, '');
function identHeaders(base, room, id, env) {
  const h = new Headers(base || {});
  h.set('X-Room', room); h.set('X-Uid', id ? id.uid : ''); h.set('X-Admin', isAdmin(id, env) ? '1' : '');
  return h;
}
function wsReject(code, reason) {       // close the socket with a clear code the client understands
  const pair = new WebSocketPair(); const [client, server] = Object.values(pair);
  server.accept(); server.close(code, reason);
  return new Response(null, { status: 101, webSocket: client });
}
const roomStub = (env, name) => env.ROOM.get(env.ROOM.idFromName(name));
function gate(room, id, env) {          // who may open a room at all
  if (!ROOM_RE.test(room)) return 'bad room';
  if (room === 'd' && !id) return 'login';
  if (room.startsWith('b:') && !(id && (id.uid === room.slice(2) || isAdmin(id, env)))) return 'forbidden';
  return '';
}

const FILE_MAX = 40 * 1024 * 1024, ROOM_FILES_MAX = 150 * 1024 * 1024, FILE_CHUNK = 1024 * 1024;   // files teachers show to students

/* ---------------- Worker entry ---------------- */
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (!url.pathname.startsWith('/api/')) return env.ASSETS.fetch(req);
    try {
      if (url.pathname === '/api/ws') {
        if ((req.headers.get('upgrade') || '').toLowerCase() !== 'websocket') return json({ error: 'expected websocket' }, 426);
        const room = url.searchParams.get('room') || '', id = await verify(url.searchParams.get('t') || '', env);
        const bad = gate(room, id, env); if (bad) return wsReject(4403, bad);
        return roomStub(env, room).fetch(new Request('https://room/ws', { headers: identHeaders(req.headers, room, id, env) }));
      }
      if (url.pathname === '/api/get') {
        const room = url.searchParams.get('room') || '', id = await verify(bearer(req), env);
        const bad = gate(room, id, env); if (bad) return json({ error: bad }, 403);
        return roomStub(env, room).fetch(new Request('https://room/get?path=' + encodeURIComponent(url.searchParams.get('path') || ''), { headers: identHeaders(null, room, id, env) }));
      }
      if (url.pathname === '/api/me' && req.method === 'POST') {
        const id = await verify(bearer(req), env); if (!id) return json({ error: 'login' }, 401);
        return roomStub(env, 'd').fetch(new Request('https://room/register', { method: 'POST', headers: identHeaders(null, 'd', id, env), body: JSON.stringify({ email: id.email, name: id.name, picture: id.picture }) }));
      }
      if (url.pathname === '/api/session' && req.method === 'POST') {
        const id = await verify(bearer(req), env); if (!id) return json({ error: 'login' }, 401);
        const body = await req.json().catch(() => ({}));
        const dir = roomStub(env, 'd'), h = identHeaders(null, 'd', id, env);
        const prof = await (await dir.fetch(new Request('https://room/register', { method: 'POST', headers: h, body: JSON.stringify({ email: id.email, name: id.name, picture: id.picture }) }))).json();
        if (!prof.active) return json({ error: prof.pending ? 'pending' : 'inactive' }, 403);
        const tinfo = { name: String(prof.name || id.name || '').slice(0, 60), photo: String(prof.photo || '').slice(0, 400000), lang: body.lang === 'en' ? 'en' : 'ar' };
        for (let i = 0; i < 12; i++) {
          const code = String(100000 + Math.floor(Math.random() * 900000)), name = 's:' + code;
          const r = await roomStub(env, name).fetch(new Request('https://room/init', { method: 'POST', headers: identHeaders(null, name, id, env), body: JSON.stringify({ owner: id.uid, tinfo }) }));
          if (r.status === 200) { await dir.fetch(new Request('https://room/stat', { method: 'POST', headers: h })); return json({ code }) }
        }
        return json({ error: 'busy' }, 503);
      }
      if (url.pathname === '/api/upload' && req.method === 'POST') {     // teacher uploads a file to show students
        const room = url.searchParams.get('room') || '', id = await verify(bearer(req), env);
        if (!/^s:\d{6}$/.test(room) || !id) return json({ error: 'login' }, 401);
        const len = +(req.headers.get('content-length') || 0); if (len > FILE_MAX) return json({ error: 'big' }, 413);
        const h = identHeaders(null, room, id, env); h.set('X-Name', (url.searchParams.get('name') || 'file').slice(0, 120)); h.set('X-Type', (url.searchParams.get('type') || 'application/octet-stream').slice(0, 100));
        return roomStub(env, room).fetch(new Request('https://room/upload', { method: 'POST', headers: h, body: await req.arrayBuffer() }));
      }
      if (url.pathname.startsWith('/api/file/')) {                         // /api/file/<code>/<id>/<name>  (public by unguessable id)
        const [code, fid] = url.pathname.split('/').slice(3);
        if (!/^\d{6}$/.test(code || '') || !/^[a-z0-9]{10,40}$/.test(fid || '')) return json({ error: 'not found' }, 404);
        const h = new Headers({ 'X-Room': 's:' + code }); const rg = req.headers.get('range'); if (rg) h.set('range', rg);
        return roomStub(env, 's:' + code).fetch(new Request('https://room/file?id=' + fid, { headers: h }));
      }
      return json({ error: 'not found' }, 404);
    } catch (e) { return json({ error: String(e && e.message || e) }, 500) }
  }
};

/* ---------------- the Room Durable Object ---------------- */
export class Room extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.tree = null; this.name = ''; this.subs = new Map(); this.dirty = new Set(); this.dirtyTop = new Set(); this.dirtyAll = false;
    this.flushT = null; this.alarmSet = false;
    try { ctx.setWebSocketAutoResponse(new WebSocketRequestResponsePair('ping', 'pong')) } catch (e) {}
    ctx.blockConcurrencyWhile(async () => {
      this.sql.exec('CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)');
      this.load();
      for (const ws of ctx.getWebSockets()) { try { ws.send('{"t":"resync"}') } catch (e) {} }   // woke from hibernation: ask clients to resubscribe
    });
  }
  fileTables() {
    if (this.ft) return; this.ft = true;
    this.sql.exec('CREATE TABLE IF NOT EXISTS fmeta (id TEXT PRIMARY KEY, name TEXT, type TEXT, size INTEGER)');
    this.sql.exec('CREATE TABLE IF NOT EXISTS fdata (id TEXT, i INTEGER, d BLOB, PRIMARY KEY (id, i))');
  }
  get kind() { return this.name ? (this.name === 'd' ? 'd' : this.name[0]) : '' }

  /* ----- storage ----- */
  load() {
    let t = null;
    for (const r of this.sql.exec('SELECT k, v FROM kv').toArray()) {
      if (r.k === '__name') { this.name = r.v; continue }
      if (r.k.startsWith('__')) continue;
      try { t = setIn(t, r.k.split(/[\/\u0000]/), JSON.parse(r.v)) } catch (e) {}
    }
    this.tree = t;
  }
  setName(n) { if (!this.name && n) { this.name = n; this.sql.exec('INSERT OR REPLACE INTO kv (k, v) VALUES (?, ?)', '__name', n) } }
  markDirty(segs) {
    if (!segs.length) this.dirtyAll = true;
    else if (segs.length === 1) this.dirtyTop.add(segs[0]);
    else this.dirty.add(segs[0] + '/' + segs[1]);
    if (!this.flushT) this.flushT = setTimeout(() => { this.flushT = null; this.flush() }, FLUSH_MS);
    if (!this.alarmSet && (this.kind === 's' || this.kind === 'g')) { this.alarmSet = true; this.ctx.storage.setAlarm(Date.now() + EXPIRE_MS) }
  }
  delPrefix(k, sep) { this.sql.exec('DELETE FROM kv WHERE k = ? OR substr(k, 1, ?) = ?', k, k.length + 1, k + sep) }
  put(k, v) {
    if (v == null) return;
    const s = JSON.stringify(v);
    if (s.length <= CHUNK_MAX || typeof v !== 'object') { this.sql.exec('INSERT OR REPLACE INTO kv (k, v) VALUES (?, ?)', k, s); return }
    for (const g in v) this.put(k + '\u0000' + g, v[g]);            // big branches (e.g. recordings) are split further, row by row
  }
  writeTop(n) {
    this.delPrefix(n, '/'); this.sql.exec('DELETE FROM kv WHERE substr(k, 1, ?) = ?', n.length + 1, n + '\u0000');
    const v = this.tree ? this.tree[n] : null; if (v == null) return;
    if (typeof v !== 'object') this.put(n, v); else for (const c in v) this.put(n + '/' + c, v[c]);
  }
  flush() {
    if (this.flushT) { clearTimeout(this.flushT); this.flushT = null }
    if (this.dirtyAll) {
      this.sql.exec("DELETE FROM kv WHERE substr(k, 1, 2) != '__'");
      for (const n in (this.tree || {})) this.writeTop(n);
    } else {
      for (const n of this.dirtyTop) this.writeTop(n);
      for (const key of this.dirty) {
        const [n, c] = key.split('/'); if (this.dirtyTop.has(n)) continue;
        this.sql.exec('DELETE FROM kv WHERE k = ?', n);
        this.delPrefix(key, '\u0000');
        this.put(key, getIn(this.tree, [n, c]));
      }
    }
    this.dirty.clear(); this.dirtyTop.clear(); this.dirtyAll = false;
  }
  async alarm() {
    if (this.ctx.getWebSockets().length) { await this.ctx.storage.setAlarm(Date.now() + 2 * 3600e3); return }
    this.tree = null; this.dirty.clear(); this.dirtyTop.clear(); this.dirtyAll = false;
    if (this.flushT) { clearTimeout(this.flushT); this.flushT = null }
    await this.ctx.storage.deleteAll(); this.ft = false;
    this.name = ''; this.alarmSet = false;
  }

  /* ----- access rules ----- */
  canRead(a, s) {
    if (this.kind !== 'd') return true;
    return !!a.adm || (s[0] === 'teachers' && s[1] === a.uid && !!a.uid);
  }
  canWrite(a, s, v) {
    const k = this.kind;
    if (k === 'g' || k === 'b') return true;           // games are open; banks are gated when the socket opens
    if (k === 'd') return !!a.adm || (s[0] === 'teachers' && s[1] === a.uid && s.length >= 3 && ['name', 'live', 'lang'].includes(s[2]) && JSON.stringify(v || '').length < 2000);
    if (a.role === 't') return true;                   // the session's teacher
    if (getIn(this.tree, ['meta', 'active']) !== true) return false;
    if (s[0] === 'roster' && s.length >= 2) {
      if (s.length === 2) return !!(v && typeof v === 'object' && typeof v.name === 'string' && v.name.trim() && v.name.length <= 30);
      if (!['name', 'online', 'hand', 'joined', 'renamed'].includes(s[2]) || s.length > 3) return false;
      return s[2] !== 'name' || (typeof v === 'string' && v.trim().length > 0 && v.length <= 30);
    }
    if (s[0] === 'sb' && s.length >= 2) return getIn(this.tree, ['roster', s[1]]) != null && JSON.stringify(v || '').length < 400000;
    if (s[0] === 'media' && s.length >= 2 && s.length <= 4) {          // student voice / video notes: media/<sid>/<mid>/<c0..c9|m|n|d>
      if (getIn(this.tree, ['roster', s[1]]) == null) return false;
      if (v == null) return true;                                      // a student may delete their own recordings
      const mine = getIn(this.tree, ['media', s[1]]) || {};
      if (s.length >= 3 && !mine[s[2]] && Object.keys(mine).length >= 12) return false;   // at most 12 recordings per student
      if (s.length === 4) return /^(c\d|m|n|d)$/.test(s[3]) && JSON.stringify(v).length <= 210000;
      if (s.length === 3) return typeof v === 'object' && Object.keys(v).every(k => /^(m|n|d)$/.test(k)) && JSON.stringify(v).length < 400;
      return false;
    }
    if (s[0] === 'qa' && s.length === 3) {
      const [, qid, sid] = s;
      return getIn(this.tree, ['quiz', 'st']) === 'q' && getIn(this.tree, ['quiz', 'qid']) === qid && getIn(this.tree, ['qa', qid, sid]) == null
        && getIn(this.tree, ['roster', sid]) != null && !!v && typeof v.c === 'string' && /^[ABCD]$/.test(v.c);
    }
    return false;
  }

  /* ----- applying writes + fan-out ----- */
  apply(a, writes) {             // writes: [[segs, value]] — all checked first, then applied together
    const now = Date.now();
    for (const w of writes) {
      w[1] = clean(stamp(w[1], now));
      if (this.kind === 's' && a.role !== 't' && w[0][0] === 'qa' && w[1]) w[1].at = now;
      if (a.internal) continue;
      if (!this.canWrite(a, w[0], w[1])) return false;
    }
    for (const [s, v] of writes) { this.tree = setIn(this.tree, s, v == null ? null : JSON.parse(JSON.stringify(v))); this.markDirty(s) }
    this.broadcast(writes);
    return true;
  }
  broadcast(writes) {
    for (const ws of this.ctx.getWebSockets()) {
      const subs = this.subs.get(ws); if (!subs || !subs.size) continue;
      for (const [i, S] of subs) {
        const ops = [];
        for (const [P, v] of writes) {
          if (S.length <= P.length && S.every((x, j) => x === P[j])) ops.push([P.slice(S.length).join('/'), v]);
          else if (P.length < S.length && P.every((x, j) => x === S[j])) ops.push(['', getIn(this.tree, S)]);
        }
        if (ops.length) { try { ws.send(JSON.stringify({ t: 'w', i, ops })) } catch (e) {} }
      }
    }
  }
  att(ws) { try { return ws.deserializeAttachment() || {} } catch (e) { return {} } }

  /* ----- HTTP (from the Worker only) ----- */
  async fetch(req) {
    const url = new URL(req.url), h = req.headers;
    this.setName(h.get('X-Room') || '');
    const who = { uid: h.get('X-Uid') || '', adm: h.get('X-Admin') === '1' };
    if (url.pathname === '/ws') {
      const pair = new WebSocketPair(); const [client, server] = Object.values(pair);
      let role = 'g';
      if (this.kind === 's') role = (who.adm || (who.uid && who.uid === getIn(this.tree, ['meta', 'owner']))) ? 't' : 's';
      else if (this.kind === 'b') role = 'o';
      else if (this.kind === 'd') role = who.adm ? 'a' : 'u';
      this.ctx.acceptWebSocket(server);
      server.serializeAttachment({ uid: who.uid, adm: who.adm, role, od: {} });
      server.send(JSON.stringify({ t: 'hi', now: Date.now(), role }));
      return new Response(null, { status: 101, webSocket: client });
    }
    if (url.pathname === '/get') {
      const s = segsOf(url.searchParams.get('path'));
      if (!this.canRead(who, s)) return json({ error: 'PERMISSION_DENIED' }, 403);
      return json({ v: getIn(this.tree, s) });
    }
    if (url.pathname === '/upload' && req.method === 'POST') {
      if (this.kind !== 's' || !getIn(this.tree, ['meta', 'active'])) return json({ error: 'no session' }, 404);
      if (!(who.adm || (who.uid && who.uid === getIn(this.tree, ['meta', 'owner'])))) return json({ error: 'forbidden' }, 403);
      const buf = new Uint8Array(await req.arrayBuffer()); if (!buf.length) return json({ error: 'empty' }, 400);
      if (buf.length > FILE_MAX) return json({ error: 'big' }, 413);
      this.fileTables();
      const used = this.sql.exec('SELECT COALESCE(SUM(size),0) AS n FROM fmeta').one().n;
      if (used + buf.length > ROOM_FILES_MAX) return json({ error: 'big' }, 413);
      const fid = crypto.randomUUID().replace(/-/g, '').slice(0, 24), name = h.get('X-Name') || 'file', type = h.get('X-Type') || 'application/octet-stream';
      for (let i = 0, k = 0; i < buf.length; i += FILE_CHUNK, k++) this.sql.exec('INSERT INTO fdata (id, i, d) VALUES (?, ?, ?)', fid, k, buf.slice(i, i + FILE_CHUNK).buffer);
      this.sql.exec('INSERT INTO fmeta (id, name, type, size) VALUES (?, ?, ?, ?)', fid, name, type, buf.length);
      const code = this.name.slice(2), safe = encodeURIComponent(name.replace(/[\/\\?#]/g, '_'));
      return json({ id: fid, url: `/api/file/${code}/${fid}/${safe}` });
    }
    if (url.pathname === '/file') {
      this.fileTables();
      const fid = url.searchParams.get('id') || '', m = this.sql.exec('SELECT type, size FROM fmeta WHERE id = ?', fid).toArray()[0];
      if (!m) return json({ error: 'not found' }, 404);
      let a = 0, b = m.size - 1, st = 200; const rg = /bytes=(\d*)-(\d*)/.exec(h.get('range') || '');
      if (rg) { if (rg[1]) { a = +rg[1]; if (rg[2]) b = Math.min(+rg[2], m.size - 1) } else if (rg[2]) a = Math.max(0, m.size - +rg[2]); if (a > b || a >= m.size) return new Response(null, { status: 416, headers: { 'content-range': `bytes */${m.size}` } }); st = 206 }
      const out = new Uint8Array(b - a + 1), c0 = Math.floor(a / FILE_CHUNK), c1 = Math.floor(b / FILE_CHUNK);
      for (const r of this.sql.exec('SELECT i, d FROM fdata WHERE id = ? AND i BETWEEN ? AND ? ORDER BY i', fid, c0, c1).toArray()) {
        const d = new Uint8Array(r.d), off = r.i * FILE_CHUNK, s0 = Math.max(a, off), s1 = Math.min(b + 1, off + d.length);
        if (s1 > s0) out.set(d.subarray(s0 - off, s1 - off), s0 - a);
      }
      const hd = { 'content-type': m.type, 'content-length': String(out.length), 'accept-ranges': 'bytes', 'cache-control': 'public, max-age=3600', 'access-control-allow-origin': '*' };
      if (st === 206) hd['content-range'] = `bytes ${a}-${b}/${m.size}`;
      return new Response(out, { status: st, headers: hd });
    }
    if (url.pathname === '/init' && req.method === 'POST') {            // new class session (s rooms)
      if (getIn(this.tree, ['meta', 'active'])) return json({ error: 'exists' }, 409);
      const b = await req.json();
      this.tree = { meta: { active: true, created: Date.now(), locked: false, bgType: 'grid', timerEnd: 0, owner: b.owner }, tinfo: clean(b.tinfo) || {} };
      this.markDirty([]); this.flush();
      return json({ ok: true });
    }
    if (url.pathname === '/register' && req.method === 'POST') {        // directory: create or refresh a teacher profile
      const b = await req.json(), uid = who.uid; if (!uid) return json({ error: 'login' }, 401);
      const cur = getIn(this.tree, ['teachers', uid]), now = Date.now();
      let p;
      if (!cur) {
        const approve = getIn(this.tree, ['settings', 'approve']) === true;
        p = { name: String(b.name || (b.email || '').split('@')[0] || 'Teacher').slice(0, 60), email: b.email || '', photo: b.picture || '', created: now, last: now, active: who.adm || !approve, sessions: 0 };
      } else {
        p = { ...cur, email: b.email || cur.email || '', last: now };
        if (b.picture && !cur.photoSet) p.photo = b.picture;
        if (who.adm) p.active = true;
      }
      this.apply({ internal: true }, [[['teachers', uid], p]]);
      if (!cur) this.apply({ internal: true }, [[['stats', 'teachers'], (getIn(this.tree, ['stats', 'teachers']) || 0) + 1]]);
      return json({ uid, ...p, admin: who.adm, pending: !p.active && !cur?.suspended && getIn(this.tree, ['settings', 'approve']) === true });
    }
    if (url.pathname === '/stat' && req.method === 'POST') {            // directory: count a new session
      const uid = who.uid, day = new Date().toISOString().slice(0, 10), mon = day.slice(0, 7);
      this.apply({ internal: true }, [
        [['teachers', uid, 'sessions'], (getIn(this.tree, ['teachers', uid, 'sessions']) || 0) + 1],
        [['stats', 'days', day], (getIn(this.tree, ['stats', 'days', day]) || 0) + 1],
        [['stats', 'months', mon], (getIn(this.tree, ['stats', 'months', mon]) || 0) + 1],
        [['stats', 'sessions'], (getIn(this.tree, ['stats', 'sessions']) || 0) + 1]
      ]);
      return json({ ok: true });
    }
    return json({ error: 'not found' }, 404);
  }

  /* ----- WebSocket messages ----- */
  async webSocketMessage(ws, raw) {
    if (typeof raw !== 'string' || raw === 'ping') return;
    let m; try { m = JSON.parse(raw) } catch (e) { return }
    const a = this.att(ws), s = segsOf(m.p);
    const reply = o => { try { ws.send(JSON.stringify(o)) } catch (e) {} };
    switch (m.o) {
      case 'sub': {
        if (!this.canRead(a, s)) return reply({ t: 'err', i: m.i, e: 'PERMISSION_DENIED' });
        if (!this.subs.has(ws)) this.subs.set(ws, new Map());
        this.subs.get(ws).set(m.i, s);
        return reply({ t: 'snap', i: m.i, v: getIn(this.tree, s) });
      }
      case 'uns': { const m2 = this.subs.get(ws); if (m2) m2.delete(m.i); return }
      case 'g': return reply(this.canRead(a, s) ? { t: 'ok', r: m.r, v: getIn(this.tree, s) } : { t: 'err', r: m.r, e: 'PERMISSION_DENIED' });
      case 's': return reply(this.apply(a, [[s, m.v]]) ? { t: 'ok', r: m.r } : { t: 'err', r: m.r, e: 'PERMISSION_DENIED' });
      case 'u': {
        const w = Object.entries(m.v && typeof m.v === 'object' ? m.v : {}).map(([k, v]) => [s.concat(segsOf(k)), v]);
        return reply(this.apply(a, w) ? { t: 'ok', r: m.r } : { t: 'err', r: m.r, e: 'PERMISSION_DENIED' });
      }
      case 'od': { a.od = a.od || {}; a.od[s.join('/')] = m.v; if (JSON.stringify(a).length < 1900) ws.serializeAttachment(a); return }
      case 'odc': { if (a.od) { delete a.od[s.join('/')]; ws.serializeAttachment(a) } return }
    }
  }
  closed(ws) {
    const a = this.att(ws); this.subs.delete(ws);
    for (const p in (a.od || {})) {
      const v = a.od[p], s = segsOf(p);
      const w = (v && typeof v === 'object') ? Object.entries(v).map(([k, x]) => [s.concat(segsOf(k)), x]) : [[s, v]];
      this.apply(a, w);
    }
  }
  async webSocketClose(ws, code) { this.closed(ws); try { ws.close(code === 1005 ? 1000 : code, 'bye') } catch (e) {} }
  async webSocketError(ws) { this.closed(ws) }
}
