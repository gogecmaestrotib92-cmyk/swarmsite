/* landing.js — what is the landing's own: links that travel, and the crew that builds the first screen.
   Everything that moves by the engine's devices is in index.html (<script id="dv-js">, from lib/devices/registry.py). */
(function () {
  'use strict';
  const D = document, R = D.documentElement, calm = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Links inside the page travel there; "Try it free" ends with the cursor in the field it asks for.
  D.addEventListener('click', e => {
    const a = e.target.closest && e.target.closest('a[href^="#"]'); if (!a || e.defaultPrevented || a.classList.contains('skip')) return;   // the skip link is the browser's own: it must move the reader, not only the page
    const t = D.getElementById(a.getAttribute('href').slice(1)); if (!t) return; e.preventDefault();
    const menu = D.querySelector('.dv-menu-btn[aria-expanded="true"]'); menu && menu.click();   // a link in the bar pressed while the menu stands open: the menu goes first, or the page travels unseen behind it
    const top = t.id === 'top' ? 0 : Math.max(0, t.getBoundingClientRect().top + scrollY - 88);
    scrollTo({ top, behavior: calm ? 'auto' : 'smooth' }); history.replaceState(null, '', a.getAttribute('href'));
    const to = t.id === 'top' && !a.classList.contains('brand') ? D.getElementById('url') : t; if (to) { if (to === t && to.tabIndex < 0) to.tabIndex = -1; to.focus({ preventScroll: true }); }   // a keyboard goes on from where the link led; "Try it free" ends in the field, the name only goes home
  });

  // The crew builds the first screen from nothing — the bar too — on a desk and on a phone — many at once, the headline first among the words so that it stands
  // within the Standard's 1.5 s (MOT-03) at a visitor's pace. The head of the page set .sw-pre, so nothing is seen and then taken away.
  if (R.classList.contains('sw-pre')) {
    // The first screen is built from nothing: headline, field, button, switch and the window (owner, 2026-11-11: the build is the page's show and is filmed).
    // Two paces: a visitor's, over in about three seconds, and /?film for recording the screen — slower.
    const asked = location.search.match(/[?&]film(?:=([\d.]+))?(?:&|$)/), film = !!asked, pace = film ? Math.min(3, Math.max(.3, +asked[1] || .8)) : 1.3;   // /?film=0.5 is slower still, /?film=1.2 quicker
    const start = () => { if (!R.classList.contains('sw-pre')) return;   // the three seconds ran out first and the first screen already stands: it is not taken away again
      try { if (window.Swarm && D.querySelector('.open')) new window.Swarm({ agents: 18, pool: innerWidth < 700 ? 7 : 11, speed: pace, delay: film ? 600 : 100, hud: false, noScroll: true, skin: 'character', sectionSelector: 'body', first: 'h1', boxSel: '.nav .grp, .nav .pill, .nav .dv-menu-btn, .urlbox, .urlbox .pill', keep: 'main > :not(.open), #closing, .dv-menu, .skip, .hero-crew, .dv-tick, .dv-roll .r' }).run(); } catch (e) {} R.classList.remove('sw-pre'); };
    let went = false; const once = () => { if (!went) { went = true; start(); } };
    (D.fonts && D.fonts.ready ? D.fonts.ready : Promise.resolve()).then(once); setTimeout(once, 700);
  }
})();
