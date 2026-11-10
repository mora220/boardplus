/* BoardPlus realtime client: talks to the Cloudflare rooms over WebSockets.
   API per room: set, update, remove, get, onValue, onChild, onDisconnect, cancelDisconnect. */
(function () {
  const RT = window.RT = {};
  let tokenFn = async () => '', off = 0;
  RT.setToken = f => { tokenFn = f };
  RT.token = async () => { try { return (await tokenFn()) || '' } catch (e) { return '' } };
  RT.now = () => Date.now() + off;
  RT.TS = () => ({ '.sv': 'timestamp' });
  const rooms = new Map(), connL = new Set();
  const split = p => String(p == null ? '' : p).split('/').filter(Boolean);
  const clone = v => v == null ? null : JSON.parse(JSON.stringify(v));
  const isObj = v => v && typeof v === 'object';
  function setIn(root, s, v) {
    if (!s.length) return v == null ? null : clone(v);
    const top = isObj(root) ? root : {}; let o = top; const stack = [];
    for (let i = 0; i < s.length - 1; i++) { const k = s[i]; if (!isObj(o[k])) o[k] = {}; stack.push([o, k]); o = o[k] }
    const last = s[s.length - 1];
    if (v == null) { delete o[last]; for (let i = stack.length - 1; i >= 0; i--) { const [p, k] = stack[i]; if (Object.keys(p[k]).length === 0) delete p[k]; else break } }
    else o[last] = clone(v);
    return Object.keys(top).length ? top : null;
  }
  function state() { let ok = true; rooms.forEach(r => { if (!r.dead && r.wanted() && !r.open) ok = false }); return ok }
  let lastState = null;
  function emitConn() { const s = state(); if (s === lastState) return; lastState = s; connL.forEach(f => { try { f(s) } catch (e) {} }) }
  RT.onConnected = f => { connL.add(f); try { f(state()) } catch (e) {} return () => connL.delete(f) };
  const wsBase = () => { const u = new URL('api/ws', location.href); u.protocol = u.protocol === 'https:' ? 'wss:' : 'ws:'; return u };

  class Room {
    constructor(name) { this.name = name; this.subs = new Map(); this.nid = 1; this.rid = 1; this.pend = new Map(); this.ods = new Map(); this.open = false; this.dead = false; this.back = 400; this.connect() }
    wanted() { return this.subs.size > 0 || this.pend.size > 0 || this.ods.size > 0 }
    async connect() {
      if (this.dead) return;
      let t = ''; try { t = (await tokenFn()) || '' } catch (e) {}
      const u = wsBase(); u.searchParams.set('room', this.name); if (t) u.searchParams.set('t', t);
      let ws; try { ws = this.ws = new WebSocket(u) } catch (e) { return this.retry() }
      ws.onopen = () => {
        this.open = true; this.back = 400;
        this.subs.forEach((s, i) => this.raw({ o: 'sub', i, p: s.p }));
        this.ods.forEach((v, p) => this.raw({ o: 'od', p, v }));
        this.pend.forEach(x => this.raw(x.m));
        clearInterval(this.pi); this.pi = setInterval(() => { try { ws.send('ping') } catch (e) {} }, 25000);
        emitConn();
      };
      ws.onmessage = e => this.msg(e.data);
      ws.onclose = e => {
        clearInterval(this.pi); this.open = false;
        if (e.code === 4403 || e.code === 4404) { this.dead = true; rooms.delete(this.name); this.pend.forEach(x => x.rej({ code: 'PERMISSION_DENIED', message: e.reason })); this.pend.clear(); emitConn(); return }
        if (this.idle) return;
        emitConn(); this.retry();
      };
    }
    retry() { setTimeout(() => this.connect(), this.back); this.back = Math.min(this.back * 2, 8000) }
    raw(m) { if (this.open) { try { this.ws.send(JSON.stringify(m)) } catch (e) {} } }
    msg(d) {
      if (d === 'pong') return;
      let m; try { m = JSON.parse(d) } catch (e) { return }
      if (m.t === 'hi') { off = m.now - Date.now(); this.role = m.role; return }
      if (m.t === 'resync') { this.subs.forEach((s, i) => this.raw({ o: 'sub', i, p: s.p })); this.ods.forEach((v, p) => this.raw({ o: 'od', p, v })); return }
      if (m.t === 'ok' || m.t === 'err') {
        if (m.i != null) { const s = this.subs.get(m.i); if (s && s.err) s.err({ code: m.e }); return }
        const x = this.pend.get(m.r); if (!x) return; this.pend.delete(m.r);
        m.t === 'ok' ? x.res(m.v === undefined ? null : m.v) : x.rej({ code: m.e || 'ERR', message: m.e });
        this.maybeIdle(); return;
      }
      const s = this.subs.get(m.i); if (!s) return;
      if (m.t === 'snap') { const old = s.has ? s.c : undefined; s.c = m.v == null ? null : m.v; s.has = true; this.fire(s, old); return }
      if (m.t === 'w' && s.has) {
        let full = false; const keys = new Set(); let old = {};
        if (s.mode === 'child') {
          for (const [rel] of m.ops) { const rs = split(rel); if (!rs.length) { full = true; break } keys.add(rs[0]) }
          if (full) old = clone(s.c); else { const cur = isObj(s.c) ? s.c : {}; keys.forEach(k => { old[k] = cur[k] === undefined ? undefined : clone(cur[k]) }) }
        }
        for (const [rel, v] of m.ops) s.c = setIn(s.c, split(rel), v);
        if (s.mode === 'value') s.cb(clone(s.c));
        else if (full) this.fire(s, old);
        else { const c = isObj(s.c) ? s.c : {}; keys.forEach(k => { const was = old[k] !== undefined && old[k] !== null, now = c[k] !== undefined; if (was && !now) s.h.remove && s.h.remove(k); else if (!was && now) s.h.add && s.h.add(k, clone(c[k])); else if (now) s.h.change && s.h.change(k, clone(c[k])) }) }
      }
    }
    fire(s, old) {
      if (s.mode === 'value') { if (old === undefined || JSON.stringify(old) !== JSON.stringify(s.c)) s.cb(clone(s.c)); return }
      const o = isObj(old) ? old : {}, c = isObj(s.c) ? s.c : {};
      for (const k in o) if (!(k in c)) s.h.remove && s.h.remove(k);
      for (const k in c) { if (!(k in o)) s.h.add && s.h.add(k, clone(c[k])); else if (JSON.stringify(o[k]) !== JSON.stringify(c[k])) s.h.change && s.h.change(k, clone(c[k])) }
    }
    sub(p, mode, f) {
      const i = this.nid++, s = { p: split(p).join('/'), mode, cb: mode === 'value' ? f : null, h: mode === 'child' ? f : null, c: null, has: false };
      this.subs.set(i, s); this.idle = false; clearTimeout(this.idleT); this.raw({ o: 'sub', i, p: s.p });
      return () => { if (!this.subs.delete(i)) return; this.raw({ o: 'uns', i }); this.maybeIdle() };
    }
    req(m) { return new Promise((res, rej) => { const r = this.rid++; m.r = r; this.pend.set(r, { m, res, rej }); this.idle = false; clearTimeout(this.idleT); this.raw(m) }) }
    maybeIdle() {
      clearTimeout(this.idleT);
      this.idleT = setTimeout(() => { if (!this.wanted() && this.ws) { this.idle = true; this.dead = true; rooms.delete(this.name); try { this.ws.close(1000) } catch (e) {} emitConn() } }, 20000);
    }
    set(p, v) { return this.req({ o: 's', p: split(p).join('/'), v: v === undefined ? null : v }) }
    update(p, o) { return this.req({ o: 'u', p: split(p).join('/'), v: o || {} }) }
    remove(p) { return this.set(p, null) }
    get(p) { return this.req({ o: 'g', p: split(p).join('/') }) }
    onValue(p, cb) { return this.sub(p, 'value', cb) }
    onChild(p, h) { return this.sub(p, 'child', h || {}) }
    onDisconnect(p, v) { const k = split(p).join('/'); this.ods.set(k, v); this.raw({ o: 'od', p: k, v }) }
    cancelDisconnect(p) { const k = split(p).join('/'); this.ods.delete(k); this.raw({ o: 'odc', p: k }) }
  }
  RT.room = name => { let r = rooms.get(name); if (!r || r.dead) { r = new Room(name); rooms.set(name, r) } return r };
  RT.get = async (room, p) => {
    const r = rooms.get(room); if (r && r.open && !r.dead) return r.get(p);
    let t = ''; try { t = (await tokenFn()) || '' } catch (e) {}
    const res = await fetch(new URL('api/get?room=' + encodeURIComponent(room) + '&path=' + encodeURIComponent(split(p).join('/')), location.href), { headers: t ? { authorization: 'Bearer ' + t } : {} });
    const j = await res.json().catch(() => ({}));
    if (!res.ok) throw { code: res.status === 403 ? 'PERMISSION_DENIED' : 'ERR', message: j.error || res.status };
    return j.v == null ? null : j.v;
  };
  RT.api = async (path, body) => {
    let t = ''; try { t = (await tokenFn()) || '' } catch (e) {}
    const res = await fetch(new URL('api/' + path, location.href), { method: 'POST', headers: { 'content-type': 'application/json', ...(t ? { authorization: 'Bearer ' + t } : {}) }, body: JSON.stringify(body || {}) });
    const j = await res.json().catch(() => ({}));
    if (!res.ok) throw { code: j.error || ('HTTP_' + res.status), status: res.status };
    return j;
  };
})();
