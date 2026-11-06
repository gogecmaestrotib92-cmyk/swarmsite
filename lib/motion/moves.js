/* MOVES v2 — the motion vocabulary of the winners, each tuned in the kitchen-sink page.
   Usage: load gsap + ScrollTrigger (+ Lenis optional) then Moves.init(). Elements opt in with data-move="name [name]".
   Names: masked-line-reveal, word-blur-in, letter-reveal, highlight-swipe, text-scrub, number-scramble,
          pinned-steps, pinned-zoom, card-deck-peel, draw-on-scroll, marquee, mask-switch, rotating-headline,
          hotspot-pills, fade-rise, stagger-in, clip-reveal, parallax, scale-settle, hero-intro, giant-scrub
   Layers that need no attribute: smooth scroll (Lenis), hover layer (buttons/cards/links), nav hide-on-scroll ([data-nav]).
   Design rules: ease out = expo.out / power4.out; reveal 1.0–1.4s; stagger .05–.08; nothing bounces; everything rests under prefers-reduced-motion. */
(function (global) {
  'use strict';
  const prefersReduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const EASE = 'expo.out', EASE_IN = 'power3.in', DUR = 1.2;
  const splitWords = el => { if (el.dataset.split) return; const out = []; const walk = (n, extra) => { n.childNodes.forEach(c => { if (c.nodeType === 3) { c.textContent.replace(/\s+([.,;:!?…»”])/g, '$1').split(/(\s+)/).forEach(w => { if (!w) return; out.push(/\s+/.test(w) ? ' ' : `<span class="mv-w${extra ? ' ' + extra : ''}">${w}</span>`); }); } else if (c.tagName === 'BR') out.push('<br>'); else walk(c, (extra ? extra + ' ' : '') + (c.className || '')); }); }; walk(el, ''); el.innerHTML = out.join('').replace(/<\/span><span class="mv-w">([.,;:!?…»”)]+)<\/span>/g, '$1</span>'); el.dataset.split = 'w'; };
  const splitLines = el => {
    if (el.dataset.split === 'l') return; splitWords(el);
    const ws = [...el.querySelectorAll('.mv-w')]; let lines = [], cur = [], top = null;
    ws.forEach(w => { if (top === null || Math.abs(w.offsetTop - top) < 4) { cur.push(w); top = w.offsetTop; } else { lines.push(cur); cur = [w]; top = w.offsetTop; } });
    if (cur.length) lines.push(cur);
    el.innerHTML = ''; lines.forEach(l => { const wrap = document.createElement('span'); wrap.className = 'mv-line'; const inner = document.createElement('span'); inner.className = 'mv-line-in'; l.forEach((w, i) => { inner.appendChild(w); if (i < l.length - 1) inner.appendChild(document.createTextNode(' ')); }); wrap.appendChild(inner); el.appendChild(wrap); el.appendChild(document.createTextNode(' ')); });
    el.dataset.split = 'l';
  };
  const splitChars = el => { if (el.dataset.split) return; el.innerHTML = el.textContent.split('').map(c => c === ' ' ? ' ' : `<span class="mv-c">${c}</span>`).join(''); el.dataset.split = 'c'; };
  const ST = () => global.ScrollTrigger; const g = () => global.gsap;
  const isMobile = () => innerWidth < 700 || (matchMedia('(pointer: coarse)').matches && innerWidth < 1024);
  // On phones a pinned moment is a trap (address bar resize, no wheel inertia); winners swap them for static stacks.
  const MOBILE_SUBS = { 'pinned-steps': 'stacked-steps', 'pinned-zoom': 'clip-reveal', 'card-deck-peel': 'stagger-in', 'letter-reveal': 'masked-line-reveal', 'mask-switch': 'fade-rise', 'giant-scrub': 'fade-rise', 'hero-intro': 'hero-intro', 'text-scrub': 'word-blur-in' };
  const once = (el, start = 'top 85%') => ({ trigger: el, start, once: true });

  const moves = {
    // Aspen/Heron: lines rise inside clipped containers, slight rotation settles
    'masked-line-reveal'(el) { splitLines(el); g().fromTo(el.querySelectorAll('.mv-line-in'), { yPercent: 110, rotate: 2, transformOrigin: '0 100%' }, { yPercent: 0, rotate: 0, duration: DUR, ease: EASE, stagger: .07, scrollTrigger: once(el) }); },
    // Butter: words sharpen from blur
    'word-blur-in'(el) { splitWords(el); g().fromTo(el.querySelectorAll('.mv-w'), { opacity: 0, filter: 'blur(12px)', y: 10 }, { opacity: 1, filter: 'blur(0px)', y: 0, duration: 1, ease: 'power3.out', stagger: .045, scrollTrigger: once(el) }); },
    // Sharplink: letters arrive one by one with a skew that straightens
    'letter-reveal'(el) { splitChars(el); g().fromTo(el.querySelectorAll('.mv-c'), { opacity: 0, yPercent: 40, skewX: -8 }, { opacity: 1, yPercent: 0, skewX: 0, duration: .9, stagger: .02, ease: EASE, scrollTrigger: once(el) }); },
    // Wembi: highlighter grows behind <mark>
    'highlight-swipe'(el) { el.querySelectorAll('mark').forEach(m => { m.classList.add('mv-mark'); const o = { w: 0 }; g().to(o, { w: 100, duration: .9, ease: 'power3.inOut', onUpdate: () => m.style.setProperty('--mv-sw', o.w + '%'), scrollTrigger: { trigger: m, start: 'top 80%', once: true } }); }); },
    // Wembi/ICOMAT: words colour in with the scroll
    'text-scrub'(el) { splitWords(el); const ws = el.querySelectorAll('.mv-w'); g().set(ws, { opacity: .18 }); g().to(ws, { opacity: 1, stagger: .02, ease: 'none', scrollTrigger: { trigger: el, start: 'top 78%', end: 'bottom 40%', scrub: .4 } }); },
    // DeepBook: digits scramble then settle, left to right, keeping $ % + , .
    'number-scramble'(el) {
      const final = el.textContent.trim(); const m = final.match(/^([^\d-]*)(-?[\d.,]+)(.*)$/); if (!m) return; const [_, pre, num, suf] = m; const digits = num.replace(/[^\d]/g, '').length || 1;
      let frame = 0; const total = 34; const chars = '0123456789';
      const tick = () => { frame++; if (frame > total) { el.textContent = final; return; } const prog = frame / total; let out = ''; for (let i = 0, d = 0; i < num.length; i++) { const ch = num[i]; if (/\d/.test(ch)) { out += (d / digits) < prog * 1.15 - .15 ? ch : chars[Math.floor(Math.random() * 10)]; d++; } else out += ch; } el.textContent = pre + out + suf; requestAnimationFrame(() => setTimeout(tick, 22)); };
      el.style.fontVariantNumeric = 'tabular-nums'; ST().create({ trigger: el, start: 'top 88%', once: true, onEnter: tick });
    },
    // Heron/Cerebrium: pin, step through items; panels crossfade + rise
    'pinned-steps'(el) {
      const steps = [...el.querySelectorAll('[data-step]')], panels = [...el.querySelectorAll('[data-panel]')]; if (!steps.length) return; const n = steps.length; let cur = -1;
      const setActive = i => { if (i === cur) return; cur = i; steps.forEach((s, j) => s.classList.toggle('is-active', j === i)); panels.forEach((p, j) => { if (j === i) { p.classList.add('is-active'); g().fromTo(p, { opacity: 0, y: 24, scale: .98 }, { opacity: 1, y: 0, scale: 1, duration: .7, ease: EASE, overwrite: true }); } else p.classList.remove('is-active'); }); };
      setActive(0);
      ST().create({ trigger: el, start: 'top top+=72', end: () => '+=' + (n * 70) + '%', pin: true, scrub: true, onUpdate: s => setActive(Math.min(n - 1, Math.floor(s.progress * n))) });
    },
    // Illoca: pin and dolly into an image
    'pinned-zoom'(el) { const img = el.querySelector('img, video, .mv-zoom-target') || el; g().set(img, { transformOrigin: el.dataset.origin || '50% 50%' }); g().to(img, { scale: +(el.dataset.zoom || 1.8), ease: 'none', scrollTrigger: { trigger: el, start: 'top top', end: '+=120%', pin: true, scrub: .5 } }); },
    // Maxima: cards stacked, peel away on scroll
    'card-deck-peel'(el) {
      const cards = [...el.children]; cards.forEach((c, i) => g().set(c, { rotate: (i % 2 ? 1 : -1) * (1 + i * .7), zIndex: cards.length - i, position: 'absolute', top: 0, left: 0, right: 0 }));
      el.style.position = 'relative'; const tl = g().timeline({ scrollTrigger: { trigger: el, start: 'top top+=80', end: () => '+=' + (cards.length * 60) + '%', pin: true, scrub: .3 } });
      cards.slice(0, -1).forEach((c, i) => tl.to(c, { yPercent: -125, rotate: (i % 2 ? 1 : -1) * 9, ease: 'power1.in' }));
    },
    // Heron: SVG strokes draw as you scroll
    'draw-on-scroll'(el) { const paths = el.querySelectorAll('path, line, polyline, circle, rect'); paths.forEach(p => { const L = p.getTotalLength ? p.getTotalLength() : 1000; g().set(p, { strokeDasharray: L, strokeDashoffset: L }); }); g().to(paths, { strokeDashoffset: 0, ease: 'none', stagger: .05, scrollTrigger: { trigger: el, start: 'top 80%', end: 'bottom 40%', scrub: .5 } }); },
    // Cerebrium/Butter: slow marquee, pauses on hover
    'marquee'(el) { const track = el.firstElementChild; if (!track) return; track.innerHTML += track.innerHTML; const tw = g().to(track, { xPercent: -50, duration: +(el.dataset.duration || 40), ease: 'none', repeat: -1 }); el.addEventListener('mouseenter', () => g().to(tw, { timeScale: .15, duration: .6 })); el.addEventListener('mouseleave', () => g().to(tw, { timeScale: 1, duration: .6 })); },
    // Moto/Shader: next world opens through a circle
    'mask-switch'(el) { g().fromTo(el, { clipPath: 'circle(0% at 50% 50%)' }, { clipPath: 'circle(142% at 50% 50%)', ease: 'none', scrollTrigger: { trigger: el, start: 'top 90%', end: 'top 15%', scrub: .5 } }); },
    // DeepBook: alternating phrases [data-phrases='["a","b"]']
    'rotating-headline'(el) { const ph = JSON.parse(el.dataset.phrases || '[]'); if (!ph.length) return; let i = 0; el.style.display = 'inline-block'; el.style.overflow = 'hidden'; el.style.verticalAlign = 'bottom'; setInterval(() => { i = (i + 1) % ph.length; g().to(el, { yPercent: -100, opacity: 0, duration: .4, ease: EASE_IN, onComplete: () => { el.textContent = ph[i]; g().fromTo(el, { yPercent: 100, opacity: 0 }, { yPercent: 0, opacity: 1, duration: .7, ease: EASE }); } }); }, +(el.dataset.every || 2800)); },
    // ICOMAT/Moto: pills pop over an image
    'hotspot-pills'(el) { g().from(el.querySelectorAll('.pill'), { scale: .7, opacity: 0, duration: .6, ease: 'power3.out', stagger: .12, scrollTrigger: { trigger: el, start: 'top 70%', once: true } }); },
    // universal: fade + rise
    'fade-rise'(el) { g().from(el, { opacity: 0, y: 24, duration: 1, ease: EASE, scrollTrigger: { trigger: el, start: 'top 88%', once: true } }); },
    // universal: children arrive staggered (cards, cells, rows). [data-stagger=".06"]
    'stagger-in'(el) { g().from(el.children, { opacity: 0, y: 28, duration: 1, ease: EASE, stagger: +(el.dataset.stagger || .07), scrollTrigger: once(el, 'top 85%') }); },
    // ICOMAT/Illoca: image reveals with a clip from the bottom while it settles from a slight zoom
    'clip-reveal'(el) { const img = el.querySelector('img, video') || el; g().set(el, { clipPath: 'inset(100% 0 0 0)' }); g().set(img, { scale: 1.18 }); const tl = g().timeline({ scrollTrigger: once(el, 'top 80%') }); tl.to(el, { clipPath: 'inset(0% 0 0 0)', duration: 1.3, ease: EASE }).to(img, { scale: 1, duration: 1.6, ease: EASE }, 0); },
    // Shader/Moto: background image drifts slower than the page. [data-parallax="-14"] (percent)
    'parallax'(el) { const t = el.querySelector('img, video') || el; g().fromTo(t, { yPercent: -(+(el.dataset.parallax || 12)) }, { yPercent: +(el.dataset.parallax || 12), ease: 'none', scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: .6 } }); },
    // Butter: big things settle from 1.04 → 1 as they enter
    'scale-settle'(el) { g().from(el, { scale: 1.05, opacity: 0, duration: 1.4, ease: EASE, scrollTrigger: once(el, 'top 85%') }); },
    // hero on load: label → h1 lines → lede → buttons → artefact, one choreography
    'hero-intro'(el) {
      const tl = g().timeline({ delay: .1 }); const lbl = el.querySelectorAll('.label, .cat > *'), h1 = el.querySelector('h1'), rest = el.querySelectorAll('.lede, .ctas, .pills, p'), art = el.querySelectorAll('.artefact, .card, .frame');
      if (lbl.length) tl.from(lbl, { opacity: 0, y: 10, duration: .8, ease: EASE, stagger: .08 }, 0);
      if (h1) { splitLines(h1); tl.fromTo(h1.querySelectorAll('.mv-line-in'), { yPercent: 110, rotate: 2, transformOrigin: '0 100%' }, { yPercent: 0, rotate: 0, duration: 1.3, ease: EASE, stagger: .08 }, .15); }
      if (rest.length) tl.from(rest, { opacity: 0, y: 18, duration: 1, ease: EASE, stagger: .08 }, .55);
      if (art.length) tl.from(art[0], { opacity: 0, y: 30, scale: .98, duration: 1.4, ease: EASE }, .45);
    },
    // mobile stand-in for pinned-steps: every step with its panel, stacked, each pair reveals as it enters
    'stacked-steps'(el) {
      const steps = [...el.querySelectorAll('[data-step]')], panels = [...el.querySelectorAll('[data-panel]')]; el.classList.add('mv-stacked');
      steps.forEach((s, i) => { s.classList.add('is-active'); const p = panels[i]; if (p) { p.classList.add('is-active'); s.insertAdjacentElement('afterend', p); g().from(p, { opacity: 0, y: 24, duration: 1, ease: EASE, scrollTrigger: once(p, 'top 88%') }); } g().from(s, { opacity: 0, y: 16, duration: .9, ease: EASE, scrollTrigger: once(s, 'top 90%') }); });
    },
    // ending: giant wordmark slides up and tightens as it enters
    'giant-scrub'(el) { g().fromTo(el, { yPercent: 35, letterSpacing: '.02em' }, { yPercent: 0, letterSpacing: '-.04em', ease: 'none', scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom bottom', scrub: .4 } }); }
  };

  const CSS = `.mv-line{display:block;overflow:hidden;line-height:inherit;padding:.1em 0;margin:-.1em 0}.mv-line-in{display:block;will-change:transform}.mv-w,.mv-c{display:inline-block}
  mark.mv-mark{background:none;color:inherit;position:relative;padding:0 .08em;margin:0 -.08em;z-index:0}
  mark.mv-mark::before{content:"";position:absolute;inset:0;width:var(--mv-sw,0%);background:var(--mv-highlight,#BEFF8B);z-index:-1;border-radius:.08em}
  [data-move~="pinned-steps"] [data-step]{opacity:.28;transition:opacity .4s}[data-move~="pinned-steps"] [data-step].is-active{opacity:1}
  [data-move~="pinned-steps"] [data-panel]{display:none}[data-move~="pinned-steps"] [data-panel].is-active{display:block}
  .mv-stacked{display:block!important;min-height:0!important}.mv-stacked .steps{display:block!important}.mv-stacked [data-step]{opacity:1!important;margin:28px 0 12px}.mv-stacked [data-panel]{display:block!important;margin-bottom:8px}.mv-stacked .panels{display:none}
  html.mv-mobile [data-move~="parallax"] img{height:112%}
  [data-move~="marquee"]{overflow:hidden;white-space:nowrap}[data-move~="marquee"]>*{display:inline-flex;gap:64px;will-change:transform}
  [data-move~="clip-reveal"]{overflow:hidden}[data-move~="clip-reveal"] img{display:block;will-change:transform}
  [data-move~="parallax"]{overflow:hidden}[data-move~="parallax"] img{will-change:transform;height:124%;object-fit:cover;width:100%}
  /* hover layer (taste-skill rule 5): buttons step, linked cards lift, underlines draw */
  html.mv-hover .btn,html.mv-hover .pillb,html.mv-hover .cta{transition:transform .35s cubic-bezier(.2,.8,.2,1),background-color .25s,color .25s,border-color .25s}
  html.mv-hover .btn:hover,html.mv-hover .pillb:hover,html.mv-hover .cta:hover{transform:translateY(-2px)}html.mv-hover .btn:active,html.mv-hover .pillb:active{transform:translateY(0) scale(.98)}
  html.mv-hover a.card,html.mv-hover .cells>a,html.mv-hover .tile[href],html.mv-hover .rows li[href]{transition:transform .4s cubic-bezier(.2,.8,.2,1)}html.mv-hover a.card:hover,html.mv-hover .cells>a:hover{transform:translateY(-2px)}
  html.mv-hover .link{background-image:linear-gradient(currentColor,currentColor);background-size:0% 1px;background-repeat:no-repeat;background-position:0 100%;transition:background-size .4s cubic-bezier(.2,.8,.2,1);border-bottom:0!important;padding-bottom:2px}html.mv-hover .link:hover{background-size:100% 1px}
  [data-nav]{transition:transform .45s cubic-bezier(.2,.8,.2,1)}[data-nav].is-hidden{transform:translateY(-110%)}
  html.lenis,html.lenis body{height:auto}.lenis.lenis-smooth{scroll-behavior:auto!important}.lenis.lenis-stopped{overflow:hidden}`;

  const Moves = {
    init(root = document) {
      if (!g()) { console.warn('Moves: gsap missing'); return; }
      if (ST() && g().registerPlugin) g().registerPlugin(ST());
      if (!document.getElementById('mv-css')) { const s = document.createElement('style'); s.id = 'mv-css'; s.textContent = CSS; document.head.appendChild(s); }
      document.documentElement.classList.add('mv-hover');
      if (prefersReduced) return;
      // smooth scroll first, so ScrollTrigger measures through it
      if (global.Lenis && !global.__lenis) { const lenis = new global.Lenis({ lerp: isMobile() ? .12 : .085, wheelMultiplier: 1, smoothWheel: true, syncTouch: false }); global.__lenis = lenis; lenis.on('scroll', () => ST() && ST().update()); g().ticker.add(t => lenis.raf(t * 1000)); g().ticker.lagSmoothing(0); }
      const mob = isMobile(); document.documentElement.classList.toggle('mv-mobile', mob);
      root.querySelectorAll('[data-move]').forEach(el => { el.dataset.move.split(/\s+/).forEach(name => { if (mob && MOBILE_SUBS[name]) name = MOBILE_SUBS[name]; const fn = moves[name]; if (fn) { try { fn(el); } catch (e) { console.warn('move failed', name, e); } } }); });
      // nav hides on scroll down, returns on scroll up
      const nav = root.querySelector('[data-nav]'); if (nav && ST()) { ST().create({ start: 'top -120', onUpdate: s => nav.classList.toggle('is-hidden', s.direction === 1), onLeaveBack: () => nav.classList.remove('is-hidden') }); }
      setTimeout(() => ST() && ST().refresh(), 400);
      // layout settles late (fonts, data-URI images, Lenis): refresh again, and never leave a reveal stuck invisible
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => ST() && ST().refresh());
      addEventListener('load', () => setTimeout(() => ST() && ST().refresh(), 600));
      setTimeout(() => { if (!ST()) return; ST().refresh(); ST().getAll().forEach(t => { if (t.vars && t.vars.once && t.trigger && t.trigger.getBoundingClientRect().top < innerHeight * .9 && !t.isActive && t.progress === 0) { try { t.animation && t.animation.progress(1); } catch (e) {} } }); }, 3500);
    },
    list: Object.keys(moves)
  };
  global.Moves = Moves;
})(window);
