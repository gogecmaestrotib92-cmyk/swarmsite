/* nav-account.js — the front page's link to the visitor's account, in one self-contained tag:
     <script src="/js/nav-account.js" defer></script>
   It adds "Sign in" (or "Your projects") to the page's own navigation — the bar's right-hand group, and the full-screen
   menu when the page has one — so it takes whatever the navigation looks like. A first-time visitor pays nothing for it:
   the account library is fetched only when this browser already holds a session. */
(() => {
  const load = src => new Promise(done => { const s = document.createElement('script'); s.src = src; s.onload = () => done(true); s.onerror = () => done(false); document.head.appendChild(s); });
  const run = async () => {
    const group = document.querySelector('.nav .grp:last-of-type'); if (!group) return;
    if (!window.SWARMSITE_SUPABASE) await load('/config.js');
    const cfg = window.SWARMSITE_SUPABASE || {}; if (!cfg.url || !cfg.anon) return;   // no accounts on this deployment: no link
    const menu = document.querySelector('.dv-menu, #menu nav'), cta = group.querySelector('.pill');
    const style = document.createElement('style'); style.textContent = '.nav .grp a{white-space:nowrap}' + (menu ? '@media(max-width:820px){.nav .grp a.nav-acct{display:none}}'   /* a page with a full-screen menu carries the link there on a phone */
      : '@media(max-width:480px){.nav .grp:has(.nav-acct) a[href="#faq"]{display:none}.nav .grp a:not(.brand){padding-inline:11px}}');   /* one without: the bar gives up its least needed link so the rest stays on one line */ document.head.appendChild(style);
    const inBar = document.createElement('a'); inBar.className = 'nav-acct'; inBar.id = 'account'; group.insertBefore(inBar, cta || null);
    const links = [inBar]; if (menu) { const inMenu = document.createElement('a'); menu.insertBefore(inMenu, menu.querySelector('.btn')); links.push(inMenu); }
    const show = signed => links.forEach(a => { a.textContent = signed ? 'Your projects' : 'Sign in'; a.href = signed ? '/dashboard' : '/login'; });
    show(false);
    let held = false; try { held = Object.keys(localStorage).some(k => /^sb-.+-auth-token$/.test(k)); } catch {}
    if (!held) return;
    if (!(window.supabase && window.supabase.createClient)) await load('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.min.js');
    if (!window.Auth) await load('/js/auth.js');
    if (!window.Auth || !Auth.enabled) return;
    show(!!(await Auth.session())); Auth.onChange(s => show(!!s));
  };
  if (document.readyState === 'loading') addEventListener('DOMContentLoaded', run); else run();
})();
