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
  const client = on ? window.supabase.createClient(cfg.url, cfg.anon, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true } }) : null;
  const safeNext = next => { try { const u = new URL(next || '/dashboard', location.origin); return u.origin === location.origin ? u.pathname + u.search : '/dashboard'; } catch { return '/dashboard'; } };   // never send a signed-in visitor to another site
  const session = async () => { if (!client) return null; try { const { data } = await client.auth.getSession(); return data.session || null; } catch { return null; } };
  return {
    enabled: on, methods: Array.isArray(window.SWARMSITE_LOGIN) ? window.SWARMSITE_LOGIN : ['email'], safeNext, session,
    async email() { const s = await session(); return s && s.user ? s.user.email || null : null; },
    async api(path, init = {}) { const s = await session(); const headers = { ...(init.headers || {}) }; if (s && s.access_token) headers.authorization = 'Bearer ' + s.access_token; return fetch(API + path, { ...init, headers }); },
    signInEmail(email, next) { return client.auth.signInWithOtp({ email, options: { emailRedirectTo: location.origin + safeNext(next) } }); },
    signInWith(provider, next) { return client.auth.signInWithOAuth({ provider, options: { redirectTo: location.origin + safeNext(next) } }); },
    async signOut() { if (client) await client.auth.signOut(); },
    onChange(fn) { if (client) client.auth.onAuthStateChange((_event, s) => fn(s)); },
  };
})();
