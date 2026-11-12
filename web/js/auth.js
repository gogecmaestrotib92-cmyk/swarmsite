/* auth.js — the visitor's account, in one small object. Needs supabase-js (loaded before this file) and the project's
   PUBLIC address and key in window.SWARMSITE_SUPABASE (web/config.js). Without them Auth.enabled is false and every page
   behaves as it did before accounts existed.

   Auth.enabled                   accounts are set up on this deployment
   Auth.session() / Auth.email()  the current session, the address signed in with (or null)
   Auth.api(path, init)           fetch on the Swarmsite API with the visitor's token attached when there is one
   Auth.signInEmail(email, next)  a sign-in link by e-mail        Auth.signInWith(provider, next)  GitHub, Google
   Auth.signOut()                                                 Auth.onChange(fn) */
window.Auth = (() => {
  const cfg = window.SWARMSITE_SUPABASE || {}; const API = window.SWARMSITE_API || '';
  const on = !!(cfg.url && cfg.anon && window.supabase && window.supabase.createClient);
  /* The library's default lock is navigator.locks, shared by every tab of the site: one tab stuck inside it (an old
     copy of this file deadlocked, below) left every other tab waiting too — the sign-in page drew no buttons. The lock
     here holds this tab's own auth calls in order and nothing else (a refresh in two tabs at once is allowed by the
     auth service's reuse interval). */
  let chain = Promise.resolve();
  const lock = (_name, _wait, fn) => { const run = chain.then(() => fn()); chain = run.catch(() => {}); return run; };
  const client = on ? window.supabase.createClient(cfg.url, cfg.anon, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, lock } }) : null;
  const safeNext = next => { try { const u = new URL(next || '/dashboard', location.origin); return u.origin === location.origin ? u.pathname + u.search : '/dashboard'; } catch { return '/dashboard'; } };   // never send a signed-in visitor to another site
  /* supabase-js runs getSession() behind its auth lock, and calls onAuthStateChange listeners while HOLDING that lock
     and awaiting them. A listener that awaits getSession() (header.js paint, app.html claim) waited for a lock that waited
     for it: every later getSession() hung for ever, so a signed-in visitor's "Start my preview" never sent POST /jobs.
     Listeners now run after the lock is let go (onChange), and a session that does not answer in WAIT ms is not waited
     for: it is none (a page draws itself as for a visitor not signed in), and a request to the API carries the token
     this browser holds if it is still valid (the server verifies it). Signing out does not wait for ever either. */
  const WAIT = +window.SWARMSITE_AUTH_WAIT_MS || 3000;
  const storageKey = (() => { try { return 'sb-' + new URL(cfg.url).hostname.split('.')[0] + '-auth-token'; } catch { return ''; } })();
  const held = () => { try { const s = JSON.parse(localStorage.getItem(storageKey) || 'null'); return s && s.access_token && (!s.expires_at || s.expires_at * 1000 > Date.now() + 10000) ? s : null; } catch { return null; } };
  const session = async () => {
    if (!client) return null; let timer;
    const late = new Promise(done => { timer = setTimeout(() => done(null), WAIT); });
    try { return await Promise.race([client.auth.getSession().then(r => (r && r.data && r.data.session) || null, () => null), late]); }
    catch { return null; } finally { clearTimeout(timer); }
  };
  return {
    enabled: on, methods: Array.isArray(window.SWARMSITE_LOGIN) ? window.SWARMSITE_LOGIN : ['email'], safeNext, session,
    async email() { const s = await session(); return s && s.user ? s.user.email || null : null; },
    async api(path, init = {}) { const s = (await session()) || held(); const headers = { ...(init.headers || {}) }; if (s && s.access_token) headers.authorization = 'Bearer ' + s.access_token; return fetch(API + path, { ...init, headers }); },
    signInEmail(email, next) { return client.auth.signInWithOtp({ email, options: { emailRedirectTo: location.origin + safeNext(next) } }); },
    signInWith(provider, next) { return client.auth.signInWithOAuth({ provider, options: { redirectTo: location.origin + safeNext(next) } }); },
    async signOut() { if (!client) return; try { await Promise.race([client.auth.signOut(), new Promise(r => setTimeout(r, WAIT))]); } catch {} try { localStorage.removeItem(storageKey); } catch {} },
    onChange(fn) { if (client) client.auth.onAuthStateChange((_event, s) => { setTimeout(() => fn(s), 0); }); },   // never awaited inside the auth lock
  };
})();
