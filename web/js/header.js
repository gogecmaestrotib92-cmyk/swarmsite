/* header.js — what the product's header does (styles: web/header.css). Needs js/auth.js before it.
   The markup is in the page: <header class="hd" data-hd data-hd-page="dashboard|app|login"> with a [data-hd-right] group
   that holds a plain "New project" link until this runs. Then the group says what the visitor can do next:
     signed in      "New project" (to the field on the dashboard) and the account chip — projects, a new one, sign out
     not signed in  "Sign in", coming back to this page afterwards
     no accounts    "New project", to the front page
   One place decides it, so the form, the dashboard and the sign-in page cannot disagree about where a link leads. */
(() => {
  const run = () => {
    const hd = document.querySelector('[data-hd]'); if (!hd) return;
    const page = hd.dataset.hdPage || '', right = hd.querySelector('[data-hd-right]'), projects = hd.querySelector('[data-hd-projects]'), A = window.Auth;
    const make = (tag, cls, text, attrs = {}) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; for (const k in attrs) n.setAttribute(k, attrs[k]); return n; };
    const cta = (text, href) => { const a = make('a', 'hd-cta', null, { href, 'aria-label': text }), r = make('span', 'hd-roll', null, { 'aria-hidden': 'true' }); r.append(make('span', '', text), make('span', '', text)); a.append(r); return a; };
    let shut = () => {};
    const account = email => {
      const initial = (email || '?').trim().charAt(0) || '?';
      const btn = make('button', 'hd-me', initial, { type: 'button', id: 'hdMe', 'aria-expanded': 'false', 'aria-controls': 'hdPop', 'aria-label': 'Account' + (email ? ': ' + email : '') });
      const pop = make('div', 'hd-pop', null, { id: 'hdPop' });
      const who = make('div', 'hd-who'), words = make('div'); words.append(make('small', '', 'Signed in'), make('b', '', email || 'Your account')); words.lastChild.id = 'who'; who.append(make('i', '', initial, { 'aria-hidden': 'true' }), words);
      const mine = make('a', 'hd-row', 'Your projects', { href: '/dashboard' }); if (page === 'dashboard') mine.setAttribute('aria-current', 'page');
      const fresh = make('a', 'hd-row', 'New project', { href: page === 'dashboard' ? '#new' : '/dashboard#new' });
      const out = make('button', 'hd-row hd-out', 'Sign out', { type: 'button', id: 'out' });
      pop.append(who, mine, fresh, out); [...pop.children].forEach((n, i) => n.style.setProperty('--i', i));
      const set = open => { pop.classList.toggle('is-open', open); btn.setAttribute('aria-expanded', String(open)); };
      shut = back => { if (btn.getAttribute('aria-expanded') === 'true') { set(false); if (back) btn.focus(); } };
      btn.onclick = () => set(btn.getAttribute('aria-expanded') !== 'true');
      fresh.addEventListener('click', () => shut());
      out.onclick = async () => { out.disabled = true; await A.signOut(); location.replace('/'); };
      return [btn, pop];
    };
    document.addEventListener('keydown', e => { if (e.key === 'Escape') shut(true); });
    document.addEventListener('pointerdown', e => { if (right && !right.contains(e.target)) shut(); });
    if (right) right.addEventListener('focusout', e => { if (e.relatedTarget && !right.contains(e.relatedTarget)) shut(); });
    const paint = async () => {
      if (!right) return;
      const on = !!(A && A.enabled), s = on ? await A.session() : null, here = location.pathname + location.search;
      shut(); if (projects) { projects.hidden = !s; if (page === 'dashboard') projects.setAttribute('aria-current', 'page'); }
      if (s) right.replaceChildren(cta('New project', page === 'dashboard' ? '#new' : '/dashboard#new'), ...account(s.user && s.user.email));
      else if (on && page !== 'login') right.replaceChildren(make('a', 'hd-item hd-wide', 'New project', { href: '/#top' }), cta('Sign in', '/login?next=' + encodeURIComponent(here)));
      else if (page === 'login') right.replaceChildren();
      else right.replaceChildren(cta('New project', '/#top'));
      hd.dataset.hdState = s ? 'in' : on ? 'out' : 'off';
    };
    paint(); if (A && A.enabled) A.onChange(paint);
  };
  if (document.readyState === 'loading') addEventListener('DOMContentLoaded', run); else run();
})();
