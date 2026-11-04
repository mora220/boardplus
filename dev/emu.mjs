// Minimal local emulator of the Cloudflare Worker + Durable Object APIs used by src/worker.js.
// Used only for testing in this environment (wrangler can't be installed here).
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { DatabaseSync } from 'node:sqlite';
const require = createRequire(import.meta.url);
const { WebSocketServer } = require('/opt/npm-tools/node_modules/ws');

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const PORT = +(process.env.PORT || 8787);

/* ---- runtime globals ---- */
const NativeResponse = globalThis.Response;
class CFResponse extends NativeResponse {
  constructor(body, init = {}) {
    if (init.status === 101) { super(null, { status: 200 }); this._s = 101; this._ws = init.webSocket } else super(body, init);
  }
  get status() { return this._s || super.status }
  get webSocket() { return this._ws || null }
}
globalThis.Response = CFResponse;
globalThis.WebSocketRequestResponsePair = class { constructor(req, res) { this.request = req; this.response = res } };

class SrvEnd {            // the Durable Object side of a WebSocketPair
  constructor() { this.real = null; this.attach = null; this.mode = null; this.listeners = {}; this.closedWith = null; this.buf = []; this.owner = null }
  accept() { this.mode = 'accept' }
  addEventListener(t, f) { (this.listeners[t] ||= []).push(f) }
  send(s) { if (this.closedWith) throw new Error('closed'); if (this.real) this.real.send(s); else this.buf.push(s) }
  close(code = 1000, reason = '') { if (this.closedWith) return; this.closedWith = [code, reason]; if (this.real) { try { this.real.close(code, reason) } catch (e) {} } }
  serializeAttachment(v) { this.attach = JSON.stringify(v) }
  deserializeAttachment() { return this.attach ? JSON.parse(this.attach) : null }
}
globalThis.WebSocketPair = class { constructor() { const s = new SrvEnd(); const c = { _srv: s }; this[0] = c; this[1] = s } };

/* ---- Durable Object host ---- */
class DurableObject { constructor(ctx, env) { this.ctx = ctx; this.env = env } }
globalThis.__CF = { DurableObject };

const src = fs.readFileSync(path.join(ROOT, 'src/worker.js'), 'utf8').replace(/import\s*\{\s*DurableObject\s*\}\s*from\s*'cloudflare:workers';/, 'const { DurableObject } = globalThis.__CF;');
const tmp = path.join(ROOT, 'dev/.worker.mjs'); fs.writeFileSync(tmp, src);
const mod = await import(tmp + '?' + Date.now());
const RoomClass = mod.Room;

const hosts = new Map();      // name -> { db, sockets:Set<SrvEnd>, inst, ready, auto, alarm }
const STATS = { constructs: 0 };
function host(name) {
  let h = hosts.get(name);
  if (!h) { h = { name, db: new DatabaseSync(':memory:'), sockets: new Set(), inst: null, ready: null, auto: null, alarm: null }; hosts.set(name, h) }
  if (!h.inst) {
    const ctx = {
      storage: {
        sql: { exec(q, ...b) { const st = h.db.prepare(q); if (/^\s*select/i.test(q)) { const rows = st.all(...b); return { toArray: () => rows, one: () => rows[0], [Symbol.iterator]: () => rows[Symbol.iterator]() } } st.run(...b); return { toArray: () => [], one: () => undefined, [Symbol.iterator]: () => [][Symbol.iterator]() } } },
        async setAlarm(t) { h.alarm = t }, async deleteAlarm() { h.alarm = null }, async getAlarm() { return h.alarm },
        async deleteAll() { h.db.exec('DROP TABLE IF EXISTS kv'); h.db.exec('CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)') }
      },
      blockConcurrencyWhile(fn) { h.ready = Promise.resolve().then(fn); return h.ready },
      acceptWebSocket(ws) { ws.mode = 'hib'; ws.owner = h; h.sockets.add(ws) },
      getWebSockets() { return [...h.sockets].filter(s => !s.closedWith) },
      setWebSocketAutoResponse(p) { h.auto = p }
    };
    STATS.constructs++;
    h.inst = new RoomClass(ctx, ENV);
  }
  return h;
}
async function inst(name) { const h = host(name); await h.ready; return h.inst }
const ENV = {
  FIREBASE_PROJECT_ID: 'demo', DEV_AUTH: '1', ADMIN_EMAILS: process.env.ADMIN_EMAILS || 'admin@test.dev',
  ROOM: { idFromName: n => n, get: id => ({ fetch: async req => (await inst(id)).fetch(req) }) },
  ASSETS: { async fetch(req) {
    let p = decodeURIComponent(new URL(req.url).pathname); if (p.endsWith('/')) p += 'index.html';
    const f = path.join(ROOT, 'public', p);
    if (!f.startsWith(path.join(ROOT, 'public')) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) return new NativeResponse('not found', { status: 404 });
    const ext = path.extname(f), types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.json': 'application/json', '.png': 'image/png' };
    return new NativeResponse(fs.readFileSync(f), { headers: { 'content-type': types[ext] || 'application/octet-stream' } });
  } }
};

/* ---- test hooks ---- */
async function hibernate(name) { const h = hosts.get(name); if (h && h.inst) { if (h.inst.flushT) { clearTimeout(h.inst.flushT); h.inst.flush() } h.inst = null } }
async function fireAlarm(name) { const h = hosts.get(name); if (h) { const i = await inst(name); await i.alarm() } }

/* ---- HTTP + WebSocket server ---- */
const wss = new WebSocketServer({ noServer: true });
function toRequest(req, body) {
  const url = 'http://localhost:' + PORT + req.url;
  const headers = new Headers(); for (const [k, v] of Object.entries(req.headers)) if (typeof v === 'string') headers.set(k, v);
  return new Request(url, { method: req.method, headers, body: body && body.length ? body : undefined });
}
const server = http.createServer(async (req, res) => {
  try {
    if (req.url.startsWith('/__test/')) {
      const u = new URL(req.url, 'http://x'), name = u.searchParams.get('room');
      if (u.pathname === '/__test/hibernate') await hibernate(name);
      if (u.pathname === '/__test/alarm') await fireAlarm(name);
      if (u.pathname === '/__test/dump') { const h = hosts.get(name); res.end(JSON.stringify(h ? h.db.prepare('select k, length(v) as n from kv').all() : [])); return }
      if (u.pathname === '/__test/stats') { res.end(JSON.stringify(STATS)); return }
      res.end('ok'); return;
    }
    const chunks = []; for await (const c of req) chunks.push(c);
    const r = await mod.default.fetch(toRequest(req, Buffer.concat(chunks)), ENV);
    res.writeHead(r.status, Object.fromEntries(r.headers));
    res.end(Buffer.from(await r.arrayBuffer()));
  } catch (e) { console.error(e); res.writeHead(500); res.end(String(e)) }
});
server.on('upgrade', async (req, socket, head) => {
  try {
    const r = await mod.default.fetch(toRequest(req), ENV);
    if (r.status !== 101) { socket.write(`HTTP/1.1 ${r.status} X\r\n\r\n`); socket.destroy(); return }
    const srv = r.webSocket._srv;
    wss.handleUpgrade(req, socket, head, real => {
      srv.real = real;
      if (srv.closedWith) { real.close(...srv.closedWith); return }
      for (const m of srv.buf) real.send(m); srv.buf = [];
      real.on('message', async (data, isBin) => {
        const text = isBin ? data : data.toString();
        if (srv.mode === 'hib') {
          const h = srv.owner;
          if (h.auto && text === h.auto.request) { real.send(h.auto.response); return }
          const i = await inst(h.name); await i.webSocketMessage(srv, text);
        } else (srv.listeners.message || []).forEach(f => f({ data: text }));
      });
      real.on('close', async (code, reason) => {
        if (srv.mode === 'hib') { const h = srv.owner; srv.closedWith = srv.closedWith || [code, String(reason)]; const i = await inst(h.name); await i.webSocketClose(srv, code, String(reason), true); h.sockets.delete(srv) }
      });
    });
  } catch (e) { console.error(e); socket.destroy() }
});
server.listen(PORT, () => console.log('emulator on http://localhost:' + PORT));
