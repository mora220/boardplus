const B='http://localhost:8787';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const tok=(uid,email,name)=>`dev:${uid}:${email}:${encodeURIComponent(name)}`;
async function api(p,t,body){ const r=await fetch(B+'/api/'+p,{method:'POST',headers:{'content-type':'application/json',authorization:'Bearer '+t},body:JSON.stringify(body||{})}); return [r.status, await r.json()] }
function sock(room,t){ return new Promise(res=>{ const u=new URL('ws://localhost:8787/api/ws'); u.searchParams.set('room',room); if(t) u.searchParams.set('t',t);
  const ws=new WebSocket(u); const msgs=[]; let rid=1; const pend={}; ws.onmessage=e=>{ if(e.data==='pong'){msgs.push('pong');return} const m=JSON.parse(e.data); msgs.push(m); if(m.r&&pend[m.r]) {pend[m.r](m); delete pend[m.r]} };
  ws.onclose=e=>{ws.closeCode=e.code}; ws.onopen=()=>res({ws,msgs,send(m){ws.send(JSON.stringify(m))},req(m){return new Promise(r=>{m.r=rid++;pend[m.r]=r;ws.send(JSON.stringify(m))})}}); ws.onerror=()=>{} }) }
const T=tok('t1','teach@x.com','Ahmed'), T2=tok('t2','b@x.com','Sara'), A=tok('adm','admin@test.dev','Boss');
let [st,me]=await api('me',T); console.log('me',st,me.name,me.active,me.admin);
let [st2,sess]=await api('session',T,{lang:'ar'}); console.log('session',st2,sess);
const code=sess.code, room='s:'+code;
const t=await sock(room,T); await sleep(100); console.log('teacher hi', t.msgs[0].role);
t.send({o:'sub',i:1,p:'roster'}); t.send({o:'sub',i:2,p:'meta'});
const s=await sock(room,''); await sleep(100); console.log('student hi', s.msgs[0].role);
console.log('student write meta (should fail):', (await s.req({o:'s',p:'meta/locked',v:true})).t);
console.log('student roster:', (await s.req({o:'s',p:'roster/k1',v:{name:'Yousef',online:true}})).t);
console.log('student sb:', (await s.req({o:'s',p:'sb/k1/st1',v:{t:'pen',p:[1,2,3,4]}})).t);
console.log('student sb for other (no roster) :', (await s.req({o:'s',p:'sb/zz/st1',v:{t:'pen'}})).t);
s.send({o:'od',p:'roster/k1',v:{online:false}});
await sleep(100); console.log('teacher got roster updates', t.msgs.filter(m=>m.i===1).map(m=>m.t+':'+JSON.stringify(m.v||m.ops)).join(' | '));
// other teacher cannot be teacher here
const t2=await sock(room,T2); await sleep(100); console.log('other teacher role', t2.msgs[0].role);
// quiz qa rule
await t.req({o:'u',p:'',v:{'quiz':{st:'q',qid:'q1'}}});
console.log('qa ok:', (await s.req({o:'s',p:'qa/q1/k1',v:{c:'B',at:{'.sv':'timestamp'}}})).t, 'qa again:', (await s.req({o:'s',p:'qa/q1/k1',v:{c:'A'}})).t);
console.log('qa value', JSON.stringify((await t.req({o:'g',p:'qa/q1/k1'})).v));
// hibernate → resync
t.msgs.length=0; await fetch(B+'/__test/hibernate?room='+room); await s.req({o:'s',p:'sb/k1/st2',v:{t:'pen',p:[5,6]}}); await sleep(150);
console.log('after hibernate, teacher got', t.msgs.map(m=>m.t).join(','));
console.log('stored rows', await (await fetch(B+'/__test/dump?room='+room)).text());
// student disconnect → onDisconnect online false
s.ws.close(); await sleep(200); console.log('roster after close', JSON.stringify((await t.req({o:'g',p:'roster/k1'})).v));
// bank gate
const b1=await sock('b:t1',T2); await sleep(150); console.log('bank other teacher close code', b1.ws.closeCode);
const b2=await sock('b:t1',T); await sleep(100); console.log('bank owner', (await b2.req({o:'s',p:'qbank/x',v:{img:'a',ans:'A'}})).t);
// dir: teacher can't read others / can't set active
const d=await sock('d',T); await sleep(100); console.log('dir read all (deny):', (await d.req({o:'g',p:'teachers'})).t, 'own:', (await d.req({o:'g',p:'teachers/t1/name'})).v, 'set active:', (await d.req({o:'s',p:'teachers/t1/active',v:true})).t, 'set name:', (await d.req({o:'s',p:'teachers/t1/name',v:'Ahmed Ali'})).t);
await api('me',A); const da=await sock('d',A); await sleep(100); const all=(await da.req({o:'g',p:''})).v; console.log('admin sees teachers', Object.keys(all.teachers), 'stats', JSON.stringify(all.stats));
// approval mode
await da.req({o:'s',p:'settings/approve',v:true}); let [, me3]=await api('me',tok('t3','c@x.com','New')); console.log('new teacher with approval', me3.active, me3.pending);
let [s3]=await api('session',tok('t3','c@x.com','New')); console.log('pending teacher create session status', s3);
// remove room root
await t.req({o:'s',p:'',v:null}); await sleep(100); console.log('after delete meta:', JSON.stringify((await t.req({o:'g',p:'meta'})).v));
console.log('ping:', await new Promise(r=>{ t.ws.onmessage=e=>r(e.data); t.ws.send('ping') }));
process.exit(0);
