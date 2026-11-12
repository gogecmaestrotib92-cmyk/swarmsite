/* A signed-in visitor's request is never held up by the account library (web/js/auth.js).
   Production, 2026-11-12: a signed-in visitor clicked "Start my preview" on /app and POST /jobs was never sent —
   Auth.api awaited client.auth.getSession(), which never answered. supabase-js 2.45.4 makes getSession() wait for its
   initialisation, and its initialisation awaits every onAuthStateChange listener (SIGNED_IN for a stored session);
   header.js and app.html listen with functions that call Auth.session() → getSession(): each waited for the other.
   Here: (1) that deadlock, modelled as the library does it, no longer happens — listeners run after the library lets go;
   (2) a getSession() that never answers costs at most the wait, then the token this browser holds (if still valid)
   or none, and the request goes out. */
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import vm from 'node:vm'; import { fileURLToPath } from 'node:url';

const SRC = fs.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'web', 'js', 'auth.js'), 'utf8');
const URL_ = 'https://abcdefgh.supabase.co', KEY = 'sb-abcdefgh-auth-token';

function page(client, { store = {}, wait } = {}) {
  const sent = [], opts = [];
  const localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
  const window = { SWARMSITE_SUPABASE: { url: URL_, anon: 'anon' }, SWARMSITE_API: 'https://api.test', ...(wait ? { SWARMSITE_AUTH_WAIT_MS: wait } : {}),
    supabase: { createClient: (u, k, o) => { opts.push(o); return client; } } };
  const ctx = vm.createContext({ window, localStorage, location: { origin: 'https://swarmsite.test' }, URL, setTimeout, clearTimeout, Promise, JSON, Date,
    fetch: async (url, init) => { sent.push({ url, auth: (init.headers || {}).authorization || null }); return { ok: true, status: 200 }; } });
  vm.runInContext(SRC, ctx);
  return { Auth: window.Auth, sent, opts };
}
const within = (ms, p) => Promise.race([p, new Promise((_, no) => setTimeout(() => no(new Error(`did not answer within ${ms} ms`)), ms))]);

// (1) the library as 2.45.4 has it: getSession waits for initialisation; initialisation notifies SIGNED_IN and awaits listeners
{
  const sess = { access_token: 'tok-live', user: { email: 'a@b.test' } };
  const listeners = []; let initDone; const initialised = new Promise(r => { initDone = r; });
  const client = { auth: {
    getSession: async () => { await initialised; return { data: { session: sess } }; },
    onAuthStateChange: cb => { listeners.push(cb); return { data: { subscription: {} } }; } } };
  const { Auth, sent } = page(client, { wait: 60000 });   // a long wait: this part must pass without the timeout
  const painted = [];
  Auth.onChange(async s => { painted.push(!!s); await Auth.session(); painted.push('session read'); });   // what header.js does
  // the library's _recoverAndRefresh: notify every listener and AWAIT them, then the initialisation resolves
  await within(1000, Promise.all(listeners.map(cb => cb('SIGNED_IN', sess)))); initDone();
  await within(1000, (async () => { while (painted.length < 2) await new Promise(r => setTimeout(r, 5)); })());
  assert.deepEqual(painted, [true, 'session read'], 'a listener that reads the session is not awaited inside the library');
  await within(1000, Auth.api('/jobs', { method: 'POST' }));
  assert.deepEqual(sent, [{ url: 'https://api.test/jobs', auth: 'Bearer tok-live' }], 'and the signed-in visitor\'s request goes out with their token');
}

// (0) the client is made with a lock of this tab's own, not navigator.locks: one stuck tab cannot hold up the others
{
  const { opts } = page({ auth: { getSession: async () => ({ data: { session: null } }), onAuthStateChange: () => ({}) } });
  const lock = opts[0]?.auth?.lock; assert.equal(typeof lock, 'function', 'auth.lock is given');
  const order = []; const a = lock('l', -1, async () => { order.push('a+'); await new Promise(r => setTimeout(r, 30)); order.push('a-'); return 1; });
  const b = lock('l', -1, async () => { order.push('b'); throw new Error('b fails'); }); const c = lock('l', -1, async () => { order.push('c'); return 3; });
  assert.equal(await a, 1); await assert.rejects(b); assert.equal(await c, 3); assert.deepEqual(order, ['a+', 'a-', 'b', 'c'], 'in order, one at a time, a failure does not stop the next');
}

// (2) a getSession() that never answers: the default wait is 3 s, and the request goes out after it
{
  assert.match(SRC, /SWARMSITE_AUTH_WAIT_MS \|\| 3000/, 'a session is waited for 3 seconds at most');
  const never = { auth: { getSession: () => new Promise(() => {}), onAuthStateChange: () => ({}) } };
  let { Auth, sent } = page(never, { wait: 150 });
  let t = Date.now(); assert.equal(await within(1000, Auth.session()), null, 'no session in hand: none'); assert.ok(Date.now() - t >= 140);
  await within(1000, Auth.api('/jobs', { method: 'POST' }));
  assert.deepEqual(sent, [{ url: 'https://api.test/jobs', auth: null }], 'POST /jobs is sent, without a token');
  // a token this browser holds and that is still valid is used (the server verifies it); an expired one is not
  const fresh = { access_token: 'tok-held', expires_at: Math.floor(Date.now() / 1000) + 3600 };
  ({ Auth, sent } = page(never, { wait: 150, store: { [KEY]: JSON.stringify(fresh) } }));
  await within(1000, Auth.api('/jobs', { method: 'POST' }));
  assert.deepEqual(sent, [{ url: 'https://api.test/jobs', auth: 'Bearer tok-held' }]);
  assert.equal(await within(1000, Auth.session()), null, 'but a page is drawn as for a visitor not signed in (the sign-in page shows its buttons)');
  // signing out does not wait for ever either, and leaves no token behind
  const store = { [KEY]: JSON.stringify(fresh) };
  ({ Auth } = page({ auth: { ...never.auth, signOut: () => new Promise(() => {}) } }, { wait: 150, store }));
  await within(1000, Auth.signOut()); assert.equal(store[KEY], undefined);
  ({ Auth, sent } = page(never, { wait: 150, store: { [KEY]: JSON.stringify({ ...fresh, expires_at: Math.floor(Date.now() / 1000) - 60 }) } }));
  await within(1000, Auth.api('/jobs', { method: 'POST' }));
  assert.deepEqual(sent, [{ url: 'https://api.test/jobs', auth: null }], 'an expired token is not sent');
  // a getSession() that fails answers none at once
  ({ Auth } = page({ auth: { getSession: async () => { throw new Error('x'); }, onAuthStateChange: () => ({}) } }, { wait: 60000 }));
  assert.equal(await within(500, Auth.session()), null);
}
console.log('Auth: listeners run outside the account library\'s lock, and a session that does not answer in 3 s never holds a request back');
