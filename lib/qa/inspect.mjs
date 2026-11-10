/* inspect.mjs — look at a design reference the way a browser sees it, and write down only what was measured.

     node lib/qa/inspect.mjs <id> <url> [--out <dir>]
     → <dir>/<id>/evidence.json and screenshots (the load at three moments, five scroll positions, the full page)
       at 1440×900 and at 390×844. About two minutes a page.
     node lib/qa/inspect.mjs <id> <url> --quick --evidence <file>
     → the same readings in about 45 seconds and no screenshots: shorter waits, fewer scroll steps. This is the form
       the loop runs on the page that is about to ship (lib/qa/measure.py); lib/qa/standard.py turns the readings
       into findings. `design_dna/inspect.mjs` is the same program under the address the research documents name.

   Everything in evidence.json is a reading taken in this run, in headless Chrome, at the time written in the file:
     type      every style text is actually set in, with how many characters it carries and where
     geometry  the first screen, the edges blocks align to, the sections in order with the space around their content
     pictures  how each is sized, cropped, bled, rounded, shadowed, and whether words stand on it
     surfaces  how many filled boxes, shadows and hairlines the page uses, and how its buttons are drawn
     motion    what moved while the page loaded and while it was scrolled in steps: fades and travels with their
               durations, what was held in place and for how long, what moved at a different rate from the page,
               what moved sideways, what changed size; what a pointer changes; what "reduce motion" changes
     lab       load timings of this one run (not field data)
   Nothing is inferred from the reference's name or from a description of it. A reading that could not be taken is null
   and `failed` says why. `method` in the file states the thresholds every motion reading used.

   Screenshots and evidence are third-party material kept for study: --out defaults to bench/runs/_research/references,
   which git ignores. They are never shipped and never copied into a generated page. */
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2); const [id, url] = args;
const flag = name => { const i = args.indexOf(name); return i < 0 ? null : args[i + 1]; };
if (!id || !url) { console.error('usage: node design_dna/inspect.mjs <id> <url> [--out <dir>]'); process.exit(2); }
const QUICK = args.includes('--quick'), evidenceFile = flag('--evidence'), SHOTS = !QUICK;
const out = path.join(flag('--out') || 'bench/runs/_research/references', id); if (SHOTS || !evidenceFile) fs.mkdirSync(out, { recursive: true });
// how long each part waits: a full reading for research, a quick one for a page inside a job's time limit
const PACE = QUICK ? { load: 3600, idle: 2500, pause: 800, steps: { desktop: 8, mobile: 6 }, calm: 3600 } : { load: 6000, idle: 12000, pause: 1200, steps: { desktop: 20, mobile: 16 }, calm: 6000 };
const CONSENT = '[data-dna-consent]';   // what the page marks, below, as a consent banner or a pop-up: left out of every reading
const NAMED = '[id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],[id*="onetrust" i],[class*="klaviyo" i],[aria-modal="true"]';
const VIEWS = [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844 }]];
const PHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';
const METHOD = {
  sampling: 'every animation frame, each heading, paragraph, list item, picture, button and every element inside a heading that is on screen: time, scroll position, top, left, width, opacity (its own times six ancestors)',
  scroll: `steps of 0.6 screen (desktop: wheel events; phone: a touch gesture), ${PACE.pause / 1000} s pause after each, at most ${PACE.steps.desktop} steps on desktop and ${PACE.steps.mobile} on a phone`,
  fade: 'opacity from ≤ 0.2 to ≥ 0.9; the duration runs from where the rise starts to where it ends',
  travel: 'movement relative to the document of 6 – 240 px in total while the page is not scrolling, lasting 50 ms – 3 s (a one-frame jump is a layout shift, not a travel; more than 240 px is counted as a long move, not a reveal)',
  held: 'top on screen unchanged (within 3% of the scroll step) while the page scrolls ≥ 0.4 screen; held for ≥ 75% of all scrolling is "fixed throughout"',
  parallax: 'position relative to the document changing in ≥ 60% of at least 10 scrolling frames; the rate is the median of that change per pixel scrolled (0 = moves with the page, 1 = held)',
  sideways: 'left edge moving ≥ 0.25 screen width in total while scrolling; "drifting" is ≥ 80 px of sideways movement while not scrolling',
  scale: 'width changing by ≥ 6% (≥ 16 px) while scrolling, or by ≥ 3% (≥ 8 px) while not scrolling',
  scroll_lag: 'milliseconds between the last input of a step and the last frame in which the scroll position changed; compare with baseline_lag_ms, the same on an empty tall page',
};

/* ---- in the page, before its own scripts: load timings and the frame sampler ------------------------------------ */
const INIT = named => {
  if (window.top !== window || window.__dna) return;
  const consent = '[data-dna-consent]';
  const D = window.__dna = { lcp: null, cls: 0 };
  try {
    new PerformanceObserver(list => { for (const e of list.getEntries()) D.lcp = { ms: Math.round(e.startTime), tag: e.element ? e.element.tagName.toLowerCase() : null, px: Math.round(e.size) }; }).observe({ type: 'largest-contentful-paint', buffered: true });
    new PerformanceObserver(list => { for (const e of list.getEntries()) if (!e.hadRecentInput) D.cls += e.value; }).observe({ type: 'layout-shift', buffered: true });
  } catch {}
  const SEL = 'h1,h2,h3,h4,p,li,blockquote,img,video,canvas,figure,button,h1 *,h2 *,h3 *';
  const opacity = el => {
    let o = 1;
    for (let n = el, i = 0; n && n.nodeType === 1 && i < 7; n = n.parentElement, i++) { const cs = getComputedStyle(n); if (cs.visibility === 'hidden') return 0; o *= +cs.opacity; if (o < 0.01) return 0; }
    return Math.round(o * 100) / 100;
  };
  // a consent banner is recognised by what it is (fixed, short, asks about cookies, has a button) and taken out of the
  // picture without being answered: nothing is accepted on the visitor's behalf
  D.consent = () => {
    if (!document.body) return;
    const mark = (el, hide) => { el.setAttribute('data-dna-consent', ''); if (hide) el.style.setProperty('visibility', 'hidden', 'important'); };
    for (const el of document.querySelectorAll(named)) {   // named like one — but a wrapper of the page that happens to carry the word is not a banner
      if (el === document.body || el === document.documentElement || el.hasAttribute('data-dna-consent') || el.closest(consent)) continue;
      if (el.getBoundingClientRect().height > innerHeight * 1.2 || el.querySelector('main')) continue;
      mark(el, getComputedStyle(el).position === 'fixed');
    }
    for (const el of document.querySelectorAll('body div,body section,body aside,body dialog,body form')) {   // or behaving like one
      if (el.hasAttribute('data-dna-consent') || el.closest(consent)) continue;
      const cs = getComputedStyle(el); if (cs.position !== 'fixed' || cs.display === 'none') continue;
      const text = (el.innerText || '').trim(); if (text.length < 40 || text.length > 2500 || !/cookie|consent|gdpr/i.test(text) || !el.querySelector('button,a,[role=button]')) continue;
      mark(el, true);
    }
  };
  let run = null;
  D.start = () => {
    if (run) run.on = false;
    const seen = new Map(), began = performance.now(), state = run = { on: true, poked: 0, moved: 0 };
    let near = [], asked = -1e9, frames = 0, travelled = 0, lastY = scrollY, looked = -1e9;
    const tick = () => {
      if (!state.on) return;
      const now = performance.now(), t = Math.round(now - began), y = scrollY, vh = innerHeight, vw = innerWidth; frames++;
      if (Math.abs(y - lastY) >= 0.5) { travelled += Math.abs(y - lastY); state.moved = t; }
      lastY = y;
      if (t < 7000 && t - looked > 900) { looked = t; D.consent(); }
      if (now - asked > 300) {
        asked = now; near = [];
        for (const el of document.querySelectorAll(SEL)) {
          if (near.length >= 500) break;
          const r = el.getBoundingClientRect();
          if (r.bottom > -vh * 0.5 && r.top < vh * 1.5 && r.width >= 8 && r.height >= 8 && !el.closest(consent)) near.push(el);
        }
      }
      for (const el of near) {
        const r = el.getBoundingClientRect(); if (r.bottom <= 0 || r.top >= vh || r.right <= 0 || r.left >= vw) continue;
        let s = seen.get(el); if (!s) seen.set(el, s = []);
        if (s.length < 1600) s.push([t, y, r.top, r.left, r.width, opacity(el)]);
      }
      requestAnimationFrame(tick);
    };
    state.now = () => Math.round(performance.now() - began);
    state.finish = () => { state.on = false; return D.summary(seen, { began_ms: Math.round(began), ms: state.now(), frames, travelled_px: Math.round(travelled) }); };
    requestAnimationFrame(tick);
  };
  D.finish = () => (run ? run.finish() : null);
  D.poke = () => { if (run) run.poked = run.now(); };
  D.lag = () => (run ? Math.max(0, run.moved - run.poked) : null);

  D.summary = (seen, session) => {
    const vh = innerHeight, vw = innerWidth;
    const at = (a, p) => { const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
    const quart = a => (a.length ? [at(a, 0.25), at(a, 0.5), at(a, 0.75)].map(v => Math.round(v * 100) / 100) : null);
    const what = el => { const tag = el.tagName.toLowerCase(), host = el.closest('h1,h2,h3'); return host && host !== el ? `${host.tagName.toLowerCase()} › ${tag}` : tag; };
    const words = el => ((el.innerText || el.getAttribute('alt') || '') + '').replace(/\s+/g, ' ').trim().slice(0, 36);
    const masked = el => { for (let n = el.parentElement, i = 0; n && i < 4; n = n.parentElement, i++) if (/hidden|clip/.test(getComputedStyle(n).overflow)) return true; return false; };
    const rows = new Map();
    for (const [el, s] of seen) {
      if (s.length < 4) continue;
      const row = { fade: null, shift: null };
      let lo = -1, hi = -1;
      for (let i = 0; i < s.length; i++) { if (s[i][5] <= 0.2) lo = i; else if (lo >= 0 && s[i][5] >= 0.9) { hi = i; break; } }
      if (hi > 0) {
        let a = lo; while (a > 0 && s[a - 1][5] < s[a][5]) a--;
        let b = hi; while (b < s.length - 1 && s[b + 1][5] > s[b][5]) b++;
        let gap = false; for (let i = a + 1; i <= b; i++) if (s[i][0] - s[i - 1][0] > 250) gap = true;
        if (!gap) row.fade = { at: s[a][0], ms: s[b][0] - s[a][0], from: s[a][5] };
      }
      let shift = 0, from = null, to = null, pinned = 0, scrolled = 0, moving = 0, side = 0, drift = 0, grow = 0, settle = 0; const rates = [];
      for (let i = 1; i < s.length; i++) {
        if (s[i][0] - s[i - 1][0] > 250) continue;
        const dy = s[i][1] - s[i - 1][1], dtop = s[i][2] - s[i - 1][2], ddoc = dtop + dy, dleft = s[i][3] - s[i - 1][3], dw = s[i][4] - s[i - 1][4];
        if (Math.abs(dy) < 0.5) { if (Math.abs(ddoc) >= 0.3) { shift += ddoc; if (from === null) from = s[i - 1][0]; to = s[i][0]; } drift += Math.abs(dleft); settle += dw; }
        else { moving++; scrolled += Math.abs(dy); const slack = Math.max(0.6, 0.03 * Math.abs(dy)); if (Math.abs(dtop) <= slack) pinned += Math.abs(dy); else if (Math.abs(ddoc) > slack) rates.push(ddoc / dy); side += dleft; grow += dw; }
      }
      if (Math.abs(shift) >= 6 && to - from >= 50 && to - from <= 3000) { if (Math.abs(shift) <= 240) row.shift = { at: from, ms: to - from, px: Math.round(shift) }; else row.moved = Math.round(shift); }
      Object.assign(row, { pinned, scrolled, moving, side, drift, grow, settle, width: s[0][4], rate: rates.length >= 10 && rates.length >= 0.6 * moving ? at(rates, 0.5) : null });
      rows.set(el, row);
    }
    // an element that only shows its ancestor's reveal is not counted again
    const own = (el, row, key) => { for (let n = el.parentElement, i = 0; n && i < 5; n = n.parentElement, i++) { const up = rows.get(n); if (up && up[key] && Math.abs(up[key].at - row[key].at) <= 40) return false; } return true; };
    const reveals = [];
    for (const [el, row] of rows) {
      const fade = row.fade && own(el, row, 'fade') ? row.fade : null, shift = row.shift && own(el, row, 'shift') ? row.shift : null;
      if (!fade && !shift) continue;
      reveals.push({ el, at: fade ? fade.at : shift.at, fade_ms: fade ? fade.ms : null, from_opacity: fade ? fade.from : null, travel_px: shift ? shift.px : null, travel_ms: shift ? shift.ms : null, masked: !!shift && !fade && masked(el) });
    }
    reveals.sort((a, b) => a.at - b.at);
    const groups = new Map(); for (const r of reveals) { const p = r.el.parentElement; groups.set(p, [...(groups.get(p) || []), r.at]); }
    const gaps = []; let together = 0, staggered = 0;
    for (const g of groups.values()) { if (g.length < 3) continue; let any = false; for (let i = 1; i < g.length; i++) { const d = g[i] - g[i - 1]; if (d <= 20) together++; else if (d <= 600) { gaps.push(d); any = true; } } if (any) staggered++; }
    const kinds = {}; for (const r of reveals) { const k = what(r.el); kinds[k] = (kinds[k] || 0) + 1; }
    const show = r => ({ what: what(r.el), words: words(r.el), at_ms: r.at, fade_ms: r.fade_ms, from_opacity: r.from_opacity, travel_px: r.travel_px, travel_ms: r.travel_ms, masked: r.masked });
    const ends = reveals.map(r => r.at + Math.max(r.fade_ms || 0, r.travel_ms || 0)), h1 = reveals.filter(r => what(r.el).startsWith('h1'));
    const total = Math.max(1, session.travelled_px), held = [...rows].filter(([, r]) => r.pinned >= vh * 0.4);
    const pins = held.filter(([, r]) => r.pinned < total * 0.75).sort((a, b) => b[1].pinned - a[1].pinned), spans = {};
    for (const [, r] of pins) { const k = (Math.round(r.pinned / vh * 2) / 2).toFixed(1); spans[k] = (spans[k] || 0) + 1; }
    const par = [...rows].filter(([, r]) => r.rate !== null && Math.abs(r.rate) >= 0.04 && Math.abs(r.rate) <= 0.95);
    const across = [...rows].filter(([, r]) => Math.abs(r.side) >= vw * 0.25).sort((a, b) => Math.abs(b[1].side) - Math.abs(a[1].side));
    const scaled = [...rows].filter(([, r]) => Math.abs(r.grow) >= Math.max(16, 0.06 * r.width)), settled = [...rows].filter(([, r]) => Math.abs(r.settle) >= Math.max(8, 0.03 * r.width));
    const size = ([el, r], key) => ({ what: what(el), words: words(el), from_px: Math.round(r.width), to_px: Math.round(r.width + r[key]) });
    return {
      session, elements_followed: rows.size,
      reveals: { elements: reveals.length, fades: reveals.filter(r => r.fade_ms !== null).length, fade_ms: quart(reveals.filter(r => r.fade_ms !== null).map(r => r.fade_ms)),
        travels: reveals.filter(r => r.travel_px !== null).length, travel_px: quart(reveals.filter(r => r.travel_px !== null).map(r => Math.abs(r.travel_px))), travel_ms: quart(reveals.filter(r => r.travel_ms !== null).map(r => r.travel_ms)),
        upward: reveals.filter(r => r.travel_px < 0).length, masked: reveals.filter(r => r.masked).length, by_kind: kinds, stagger: { groups: staggered, gap_ms: quart(gaps), revealed_together: together },
        last_settles_ms: ends.length ? Math.max(...ends) : null, h1_settles_ms: h1.length ? Math.max(...h1.map(r => r.at + Math.max(r.fade_ms || 0, r.travel_ms || 0))) : null, examples: reveals.slice(0, 10).map(show) },
      held: { fixed_throughout: held.length - pins.length, elements: pins.length, screens: spans, examples: pins.slice(0, 5).map(([el, r]) => ({ what: what(el), words: words(el), screens: Math.round(r.pinned / vh * 10) / 10 })) },
      parallax: { elements: par.length, rate: quart(par.map(([, r]) => r.rate)), examples: par.slice(0, 5).map(([el, r]) => ({ what: what(el), words: words(el), rate: Math.round(r.rate * 100) / 100 })) },
      sideways: { with_scroll: across.slice(0, 5).map(([el, r]) => ({ what: what(el), words: words(el), screens_wide: Math.round(r.side / vw * 100) / 100, per_px_scrolled: Math.round(r.side / Math.max(1, r.scrolled) * 100) / 100 })), elements_with_scroll: across.length, drifting: [...rows].filter(([, r]) => r.drift >= 80).length },
      long_moves_while_still: [...rows].filter(([, r]) => r.moved).length,
      scale: { with_scroll: scaled.length, with_scroll_examples: scaled.slice(0, 4).map(e => size(e, 'grow')), settling: settled.length, settling_examples: settled.slice(0, 4).map(e => size(e, 'settle')) },
    };
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => D.start(), { once: true }); else D.start();
};

/* ---- in the page, at rest at the top: what is laid out ---------------------------------------------------------- */
const READ = consent => {
  const vw = innerWidth, vh = innerHeight, sy = scrollY;
  const r2 = (v, n = 2) => Math.round(v * 10 ** n) / 10 ** n, rect = el => el.getBoundingClientRect();
  const clear = c => !c || /rgba\(0, 0, 0, 0\)|transparent/.test(c);
  const mid = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
  const shown = el => { const r = rect(el); if (r.width < 2 || r.height < 2) return false; const cs = getComputedStyle(el); return cs.visibility !== 'hidden' && cs.display !== 'none' && !el.closest(consent); };
  if (window.__dna) window.__dna.consent();
  // words a visitor sees: a copy tucked into one pixel for screen readers is not counted a second time
  const tucked = [...document.querySelectorAll('body *')].filter(el => { if (!el.textContent.trim()) return false; const r = rect(el), d = getComputedStyle(el).display; return (r.width <= 2 || r.height <= 2) && d !== 'none' && d !== 'contents' && d !== 'inline'; });
  const said = el => { let text = el.innerText || ''; for (const t of tucked) if (el !== t && el.contains(t)) text = text.replace(t.innerText || '\u0000', ' '); return text.replace(/\s+/g, ' ').trim(); };
  const lines = el => {
    const range = document.createRange(); range.selectNodeContents(el);
    const tops = [...range.getClientRects()].filter(r => r.width > 1 && r.height > 4).map(r => r.top).sort((a, b) => a - b), gap = parseFloat(getComputedStyle(el).fontSize) * 0.5;
    let n = tops.length ? 1 : 0; for (let i = 1; i < tops.length; i++) if (tops[i] - tops[i - 1] > gap) n++;
    return Math.max(1, n);
  };
  const box = el => { const r = rect(el); return { x: r2(r.left / vw, 3), y: r2((r.top + sy) / vh, 3), w: r2(r.width / vw, 3), h: r2(r.height / vh, 3) }; };

  // type: every style text is set in, by the characters it carries
  const groups = new Map(), walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let node;
  const asked = new Map(), split = new Set();   // per family, the letters beyond ASCII it is asked to draw; and accents that arrive as a separate mark
  while ((node = walk.nextNode())) {
    const text = node.textContent.replace(/\s+/g, ' ').trim(), el = node.parentElement;
    if (!text || !el || /^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|OPTION)$/.test(el.tagName) || !shown(el)) continue;
    const cs = getComputedStyle(el), px = parseFloat(cs.fontSize); if (!px) continue;
    const leading = cs.lineHeight === 'normal' ? null : r2(parseFloat(cs.lineHeight) / px), tracking = cs.letterSpacing === 'normal' ? 0 : r2(parseFloat(cs.letterSpacing) / px, 3);
    const family = cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), key = [family, r2(px, 1), cs.fontWeight, cs.fontStyle, cs.textTransform, tracking, leading].join('|');
    let g = groups.get(key);
    if (!g) { const host = el.closest('h1,h2,h3,h4,p,li,a,button') || el; groups.set(key, g = { family, px: r2(px, 1), vw: r2(px / vw * 100, 2), weight: +cs.fontWeight, style: cs.fontStyle, transform: cs.textTransform, tracking_em: tracking, leading, wrap: cs.textWrap || null, features: cs.fontFeatureSettings === 'normal' ? null : cs.fontFeatureSettings, chars: 0, where: {}, sample: said(host).slice(0, 44) }); }
    const nearest = el.closest('h1,h2,h3,h4,h5,button,a,blockquote,figcaption,label,li,p'), zone = el.closest('nav,header,footer');
    const where = (zone ? zone.tagName.toLowerCase() + ' ' : '') + (nearest ? nearest.tagName.toLowerCase() : el.tagName.toLowerCase());
    g.chars += text.length; g.where[where] = (g.where[where] || 0) + 1;
    if (/[^\x00-\x7f]/.test(text)) {
      let set = asked.get(family); if (!set) asked.set(family, set = new Set());
      for (const ch of text) if (ch > '\x7f' && /\p{L}/u.test(ch) && set.size < 80) set.add(ch);
      for (const m of text.matchAll(/\p{L}\p{M}+/gu)) if (m[0].normalize('NFC').length < m[0].length && split.size < 20) split.add(m[0]);
    }
  }
  // a letter is drawn by its face when its width does not depend on which fallback stands behind the face
  const pen = document.createElement('canvas').getContext('2d'), wide = (family, fallback, ch) => { pen.font = `72px "${family}", ${fallback}`; return pen.measureText(ch).width; };
  const letters = [...asked].filter(([family]) => !/^(-apple-system|system-ui|ui-|sans-serif$|serif$|monospace$|BlinkMacSystemFont)/i.test(family))
    .map(([family, set]) => ({ family, asked: set.size, not_drawn_by_it: [...set].filter(ch => wide(family, 'monospace', ch) !== wide(family, 'serif', ch)) }));
  const all = [...groups.values()].filter(g => g.chars >= 3), keep = new Set([...[...all].sort((a, b) => b.px - a.px).slice(0, 7), ...[...all].sort((a, b) => b.chars - a.chars).slice(0, 17)]);
  const type = [...keep].sort((a, b) => b.px - a.px || b.chars - a.chars);
  const paragraphs = [...document.querySelectorAll('p')].filter(p => shown(p) && said(p).length >= 110).sort((a, b) => said(b).length - said(a).length).slice(0, 5)
    .map(p => { const n = lines(p), chars = said(p).length, px = parseFloat(getComputedStyle(p).fontSize); return { chars, lines: n, per_line: Math.round(chars / n), width_px: Math.round(rect(p).width), px, width_em: r2(rect(p).width / px, 1) }; });
  const largest = h => Math.max(...[h, ...[...h.querySelectorAll('*')].slice(0, 60)].map(n => parseFloat(getComputedStyle(n).fontSize) || 0));
  const head = h => { const text = said(h); return { px: r2(largest(h), 1), lines: lines(h), words: text.split(' ').filter(Boolean).length, chars: text.length, align: getComputedStyle(h).textAlign, ...box(h) }; };
  const h1 = [...document.querySelectorAll('h1')].find(shown), h2s = [...document.querySelectorAll('h2')].filter(shown).map(head);

  // the first screen
  const inFirst = el => { const r = rect(el); return r.top + sy < vh && r.bottom + sy > 0 && r.left < vw && r.right > 0; };
  const firstPictures = [...document.querySelectorAll('img,video,canvas')].filter(m => shown(m) && inFirst(m) && rect(m).width >= 160 && rect(m).height >= 120)
    .map(m => { const r = rect(m); return { m, area: (Math.min(r.bottom + sy, vh) - Math.max(r.top + sy, 0)) * (Math.min(r.right, vw) - Math.max(r.left, 0)) }; }).sort((a, b) => b.area - a.area);
  const firstText = [...document.querySelectorAll('h1,h2,h3,p,a,button')].filter(el => shown(el) && inFirst(el) && rect(el).left >= 0 && rect(el).right <= vw + 1 && said(el)).map(rect);
  const filledButton = el => { const r = rect(el); return !clear(getComputedStyle(el).backgroundColor) && r.height >= 28 && r.height <= 90 && r.width >= 60 && r.width <= 420; };
  const bar = document.querySelector('header, nav'), barStyle = bar ? getComputedStyle(bar) : null;
  const first_screen = {
    h1: h1 ? head(h1) : null,
    largest_picture: firstPictures.length ? { kind: firstPictures[0].m.tagName.toLowerCase(), ...box(firstPictures[0].m), share_of_screen: r2(firstPictures[0].area / (vw * vh)) } : null, pictures: firstPictures.length,
    text_spans: firstText.length ? { from_x: r2(Math.min(...firstText.map(r => r.left)) / vw, 3), to_x: r2(Math.max(...firstText.map(r => r.right)) / vw, 3), from_y: r2((Math.min(...firstText.map(r => r.top)) + sy) / vh, 3), to_y: r2(Math.min(vh, Math.max(...firstText.map(r => r.bottom)) + sy) / vh, 3) } : null,
    filled_buttons: [...document.querySelectorAll('a,button')].filter(el => shown(el) && inFirst(el) && filledButton(el)).length,
    bar: bar ? { height_px: Math.round(rect(bar).height), position: barStyle.position, blend: barStyle.mixBlendMode, ground: barStyle.backgroundColor, links: [...bar.querySelectorAll('a')].filter(a => shown(a) && rect(a).right <= vw && rect(a).left >= 0).length } : null,
  };

  // the edges blocks align to
  const tally = {}; let centred = 0, blocksOfText = 0;
  for (const el of document.querySelectorAll('h1,h2,h3,h4,p,li,img,video,figure')) {
    if (!shown(el)) continue; const r = rect(el); if (r.left < 0 || r.right > vw + 1 || r.width < 40) continue;
    const k = Math.round(r.left / vw * 100); tally[k] = (tally[k] || 0) + 1;
    if (/^(H[1-4]|P)$/.test(el.tagName)) { blocksOfText++; if (getComputedStyle(el).textAlign === 'center') centred++; }
  }
  const edges = Object.entries(tally).filter(([, n]) => n >= 3).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([k, n]) => ({ at: +k / 100, blocks: n })).sort((a, b) => a.at - b.at);
  const declared = {}; for (const el of [...document.querySelectorAll('body *')].slice(0, 6000)) { const cs = getComputedStyle(el); if (!cs.display.includes('grid')) continue; const n = cs.gridTemplateColumns.split(' ').filter(Boolean).length; if (n > 1 && rect(el).width > vw * 0.4) declared[n] = (declared[n] || 0) + 1; }

  // sections, in order
  const tall = el => { if (/^(SCRIPT|STYLE|NOSCRIPT|LINK|TEMPLATE|SVG|CANVAS|IMG|VIDEO|IFRAME)$/i.test(el.tagName)) return false; const cs = getComputedStyle(el); if (cs.display === 'none' || cs.position === 'fixed' || el.closest(consent)) return false; const r = rect(el); return r.height >= 120 && r.width >= vw * 0.6; };
  const explode = (el, depth) => {
    const kids = [...el.children].filter(tall), h = rect(el).height, covered = kids.reduce((a, k) => a + rect(k).height, 0);
    if (depth < 10 && kids.length && (el === document.body || (kids.length === 1 && covered >= h * 0.7) || (kids.length >= 2 && h > vh * 1.6 && covered >= h * 0.6))) return kids.flatMap(k => explode(k, depth + 1));
    return [el];
  };
  const lift = el => { let n = el; while (n.parentElement && n.parentElement !== document.body && [...n.parentElement.children].filter(tall).length === 1 && rect(n.parentElement).height <= rect(n).height * 1.5) n = n.parentElement; return n; };
  const groundOf = el => { for (let n = el; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor; if (!clear(c)) return c; } return 'rgb(255, 255, 255)'; };
  const blocks = [...new Set(explode(document.body, 0).map(lift))].sort((a, b) => rect(a).top - rect(b).top).slice(0, 44);
  const sections = blocks.map(el => {
    const r = rect(el), cs = getComputedStyle(el);
    const pictures = [...el.querySelectorAll('img,video,canvas')].filter(m => shown(m) && rect(m).width >= 160 && rect(m).height >= 100);
    const ground = pictures.find(m => rect(m).width >= r.width * 0.85 && rect(m).height >= r.height * 0.85);
    const content = [...el.querySelectorAll('h1,h2,h3,h4,p,li,img,video,button')].filter(n => n !== ground && shown(n) && rect(n).height > 6).map(rect).filter(b => b.bottom > r.top && b.top < r.bottom);
    const texts = [...el.querySelectorAll('h1,h2,h3,h4,p')].filter(n => shown(n) && rect(n).width >= 80 && rect(n).left >= 0 && rect(n).right <= vw + 1);
    const heading = [...el.querySelectorAll('h1,h2,h3')].find(shown), chars = said(el).length;
    return { tag: el.tagName.toLowerCase(), top_screens: r2((r.top + sy) / vh), screens: r2(r.height / vh), ground: groundOf(el), ground_is_picture: !!ground, ink: heading ? getComputedStyle(heading).color : cs.color,
      space_above_content_px: content.length ? Math.round(Math.min(...content.map(b => b.top)) - r.top) : null, space_below_content_px: content.length ? Math.round(r.bottom - Math.max(...content.map(b => b.bottom))) : null,
      heading: heading ? { px: r2(largest(heading), 1), lines: lines(heading), words: said(heading).split(' ').filter(Boolean).length, tag: heading.tagName.toLowerCase() } : null,
      text_columns: new Set(texts.map(n => Math.round(rect(n).left / vw * 50))).size, text_from_x: texts.length ? r2(Math.min(...texts.map(n => rect(n).left)) / vw, 3) : null, text_to_x: texts.length ? r2(Math.max(...texts.map(n => rect(n).right)) / vw, 3) : null,
      centred: texts.length ? r2(texts.filter(n => getComputedStyle(n).textAlign === 'center').length / texts.length) : null, chars, chars_per_screen: Math.round(chars / Math.max(0.2, r.height / vh)),
      pictures: pictures.length, pictures_bleed: pictures.filter(m => rect(m).left <= 1 && rect(m).right >= vw - 1).length, videos: pictures.filter(m => m.tagName === 'VIDEO').length,
      sticky_inside: [...el.querySelectorAll('*')].slice(0, 1500).filter(n => getComputedStyle(n).position === 'sticky').length, words: (heading ? said(heading) : said(el)).slice(0, 44) };
  });

  // pictures
  const textRects = [...document.querySelectorAll('h1,h2,h3,h4,p')].filter(n => shown(n) && said(n)).map(rect);
  const natural = m => (m.naturalWidth ? [m.naturalWidth, m.naturalHeight] : m.videoWidth ? [m.videoWidth, m.videoHeight] : null);
  const pictures = [...document.querySelectorAll('img,video')].filter(m => shown(m) && rect(m).width >= 160 && rect(m).height >= 100).slice(0, 44).map(m => {
    const r = rect(m), cs = getComputedStyle(m), holder = m.closest('figure,picture,a,div') || m, hs = getComputedStyle(holder), nat = natural(m);
    const radius = cs.borderRadius !== '0px' ? cs.borderRadius : hs.overflow !== 'visible' ? hs.borderRadius : '0px';
    return { kind: m.tagName.toLowerCase(), top_screens: r2((r.top + sy) / vh), w_px: Math.round(r.width), h_px: Math.round(r.height), ratio: r2(r.width / r.height), width_share: r2(r.width / vw), x: r2(r.left / vw, 3), bleeds: r.left <= 1 && r.right >= vw - 1,
      fit: cs.objectFit, own_ratio: nat ? r2(nat[0] / nat[1]) : null, cropped: nat ? Math.abs(nat[0] / nat[1] - r.width / r.height) > 0.06 : null, drawn_over_pixels: nat ? r2(r.width / nat[0]) : null, radius, shadow: cs.boxShadow !== 'none' || hs.boxShadow !== 'none',
      filter: cs.filter !== 'none' ? cs.filter : null, blend: cs.mixBlendMode !== 'normal' ? cs.mixBlendMode : null, masked: (cs.maskImage && cs.maskImage !== 'none') || (hs.maskImage && hs.maskImage !== 'none') || false,
      words_on_it: textRects.some(t => { const cx = t.left + t.width / 2, cy = t.top + t.height / 2; return cx > r.left && cx < r.right && cy > r.top && cy < r.bottom; }), playing: m.tagName === 'VIDEO' ? !m.paused : null };
  });
  let backgrounds = 0, gradients = 0, shadows = 0, hairlines = 0, boxes = 0, drawn = 0; const radii = {};
  const thinPseudo = (el, which, r) => {   // a rule drawn by ::before or ::after: at most 1.5 px of ground or border, at least a quarter of the screen wide
    const cs = getComputedStyle(el, which); if (!cs.content || cs.content === 'none' || cs.display === 'none') return false;
    const h = parseFloat(cs.height), w = parseFloat(cs.width), top = parseFloat(cs.borderTopWidth), bottom = parseFloat(cs.borderBottomWidth);
    const thin = (h > 0 && h <= 1.5 && !clear(cs.backgroundColor)) || (!(h > 2) && ((top > 0 && top <= 1.5) || (bottom > 0 && bottom <= 1.5)));
    return thin && (w >= vw * 0.25 || (!(w > 0) && r.width >= vw * 0.25));
  };
  for (const el of [...document.querySelectorAll('body *')].slice(0, 7000)) {
    const r = rect(el); if (r.width < 100 || r.height < 1) continue; const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden' || el.closest(consent)) continue;
    const top = parseFloat(cs.borderTopWidth), bottom = parseFloat(cs.borderBottomWidth), left = parseFloat(cs.borderLeftWidth);
    if (((top > 0 && top <= 1.5) || (bottom > 0 && bottom <= 1.5) || (r.height <= 1.5 && !clear(cs.backgroundColor))) && left === 0 && r.width >= vw * 0.25) hairlines++;
    if (thinPseudo(el, '::before', r)) drawn++; if (thinPseudo(el, '::after', r)) drawn++;
    if (r.height < 60) continue;
    if (/url\(/.test(cs.backgroundImage) && r.width >= 200 && r.height >= 160) backgrounds++;
    if (/gradient\(/.test(cs.backgroundImage) && r.width >= 200) gradients++;
    if (cs.boxShadow !== 'none') shadows++;
    if ((!clear(cs.backgroundColor) || (top > 0 && left > 0)) && r.width >= 160 && r.width < vw * 0.9 && r.height >= 80 && r.height < vh * 1.2) { boxes++; radii[cs.borderTopLeftRadius] = (radii[cs.borderTopLeftRadius] || 0) + 1; }
  }
  const buttons = {}; for (const el of document.querySelectorAll('a,button')) {
    if (!shown(el) || !filledButton(el)) continue; const cs = getComputedStyle(el);
    const key = [cs.backgroundColor, cs.color, cs.borderTopLeftRadius, Math.round(rect(el).height), parseFloat(cs.fontSize), cs.textTransform].join(' | '); buttons[key] = (buttons[key] || 0) + 1;
  }
  const outlined = [...document.querySelectorAll('a,button')].filter(el => shown(el) && clear(getComputedStyle(el).backgroundColor) && parseFloat(getComputedStyle(el).borderTopWidth) > 0 && parseFloat(getComputedStyle(el).borderLeftWidth) > 0 && rect(el).height >= 28 && rect(el).height <= 90).length;

  // colour: grounds by the page area their sections cover, inks by the characters set in them
  const area = {}, ink = {}; for (const s of sections) area[s.ground] = (area[s.ground] || 0) + s.screens;
  const walk2 = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while ((node = walk2.nextNode())) { const text = node.textContent.trim(), el = node.parentElement; if (!text || !el || !shown(el) || /^(SCRIPT|STYLE|NOSCRIPT)$/.test(el.tagName)) continue; const c = getComputedStyle(el).color; ink[c] = (ink[c] || 0) + text.length; }
  const share = (o, n) => { const sum = Object.values(o).reduce((a, b) => a + b, 0) || 1; return Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n).map(([colour, v]) => ({ colour, share: r2(v / sum) })); };

  // motion that is declared, and what the page is built with
  const seconds = {}, eases = {}; let keyframed = 0;
  for (const el of [...document.querySelectorAll('body *')].slice(0, 6000)) {
    const cs = getComputedStyle(el), dur = cs.transitionDuration.split(',').map(parseFloat).filter(v => v > 0);
    if (dur.length) { const d = Math.max(...dur); seconds[d] = (seconds[d] || 0) + 1; const e = cs.transitionTimingFunction.split(/,(?![^(]*\))/)[0].trim(); eases[e] = (eases[e] || 0) + 1; }
    if (cs.animationName !== 'none') keyframed++;
  }
  let reduced = 0, unread = 0, sheets = 0;
  for (const sheet of document.styleSheets) { sheets++; try { for (const rule of sheet.cssRules) if (rule.media && /prefers-reduced-motion/.test(rule.conditionText || rule.media.mediaText)) reduced++; } catch { unread++; } }
  const html = document.documentElement, has = sel => !!document.querySelector(sel);
  const built = { gsap: !!window.gsap, scroll_trigger: !!window.ScrollTrigger, lenis: !!window.lenis || !!window.Lenis || html.classList.contains('lenis') || has('[data-lenis-prevent]'), locomotive: !!window.LocomotiveScroll || has('[data-scroll-container]'),
    three: !!window.THREE, barba: !!window.barba, swiper: !!window.Swiper || has('.swiper'), webflow: !!window.Webflow || html.hasAttribute('data-wf-site'), framer: has('[data-framer-name],[data-framer-component-type]'), shopify: !!window.Shopify,
    next: !!window.__NEXT_DATA__ || has('#__next') || !!window.next, nuxt: !!window.__NUXT__ || has('#__nuxt'), wordpress: has('link[href*="wp-content"],script[src*="wp-content"],link[href*="wp-includes"]'),
    canvases: document.querySelectorAll('canvas').length, videos: document.querySelectorAll('video').length, generator: document.querySelector('meta[name=generator]')?.content || null };
  // targets: every link and button a finger must hit, by its smaller side
  const hit = [...document.querySelectorAll('a[href],button,summary,[role=button]')].filter(el => shown(el) && said(el)).map(el => { const r = rect(el); return Math.min(r.width, r.height); });
  const targets = { counted: hit.length, under_24_px: hit.filter(v => v < 24).length, under_44_px: hit.filter(v => v < 44).length };
  const menu = !![...document.querySelectorAll('button,[role=button],a')].filter(shown).find(b => /menu|burger|hamburger/i.test((b.getAttribute('aria-label') || '') + ' ' + (typeof b.className === 'string' ? b.className : '') + ' ' + said(b).slice(0, 12)));

  return { viewport: [vw, vh], page_screens: r2(html.scrollHeight / vh), dom_elements: document.querySelectorAll('*').length,
    type, letters: { by_family: letters, accents_as_separate_marks: [...split] }, families_loaded: [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, '')))].slice(0, 12), paragraphs,
    headings: { h1: h1 ? head(h1) : null, h2: h2s.length ? { count: h2s.length, px: mid(h2s.map(h => h.px)), lines: mid(h2s.map(h => h.lines)), words: mid(h2s.map(h => h.words)) } : null },
    first_screen, alignment: { edges, text_centred_share: blocksOfText ? r2(centred / blocksOfText) : null, grids_declared: declared }, sections, pictures,
    surfaces: { filled_or_framed_boxes: boxes, box_radii: Object.entries(radii).sort((a, b) => b[1] - a[1]).slice(0, 4), shadows, hairlines, rules: { on_elements: hairlines, by_pseudo_elements: drawn, hr: [...document.querySelectorAll('hr')].filter(h => shown(h) && rect(h).width >= vw * 0.25).length }, css_background_pictures: backgrounds, gradients,
      filled_buttons: Object.entries(buttons).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([k, n]) => ({ 'ground | ink | radius | height | px | case': k, count: n })), outlined_buttons: outlined },
    colour: { grounds: share(area, 6), inks: share(ink, 6) },
    motion_declared: { transition_seconds: seconds, easings: Object.entries(eases).sort((a, b) => b[1] - a[1]).slice(0, 5), elements_with_keyframes: keyframed, animations_running: document.getAnimations().filter(a => a.playState === 'running').length,
      reduced_motion_rules: reduced, stylesheets: sheets, stylesheets_unreadable: unread },
    built_with: built, navigation: { menu_button: menu, cursor: getComputedStyle(document.body).cursor }, targets };
};

/* ---- what a pointer changes ------------------------------------------------------------------------------------- */
const PROPS = ['color', 'backgroundColor', 'borderTopColor', 'transform', 'opacity', 'boxShadow', 'textDecorationLine', 'letterSpacing', 'filter', 'clipPath', 'backgroundPosition', 'width'];
const hover = async page => {
  const picked = await page.evaluate(consent => {
    const ok = el => { const r = el.getBoundingClientRect(), cs = getComputedStyle(el); return r.width > 30 && r.height > 14 && r.top >= 0 && r.bottom <= innerHeight && r.left >= 0 && r.right <= innerWidth && cs.visibility !== 'hidden' && +cs.opacity > 0.5 && !el.closest(consent); };
    const links = [...document.querySelectorAll('a,button')].filter(ok), filled = links.filter(el => !/rgba\(0, 0, 0, 0\)|transparent/.test(getComputedStyle(el).backgroundColor));
    const plain = links.filter(el => !filled.includes(el) && (el.innerText || '').trim().length > 1 && !el.querySelector('img,video')), pictured = links.filter(el => el.querySelector('img,video'));
    const chosen = [[filled[0], 'filled button'], [plain[0], 'text link'], [plain[Math.floor(plain.length / 2)], 'text link'], [pictured[0], 'picture link']].filter(([el]) => el);
    return [...new Map(chosen).entries()].map(([el, on], i) => { el.setAttribute('data-dna-hover', String(i)); return on; });
  }, CONSENT);
  const read = i => page.evaluate(([i, props]) => {
    const el = document.querySelector(`[data-dna-hover="${i}"]`); if (!el) return null;
    const take = (n, pseudo) => { const cs = getComputedStyle(n, pseudo); return Object.fromEntries(props.map(p => [p, cs[p]])); }, r = el.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2, words: (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 30), self: take(el), inside: [...el.querySelectorAll('*')].slice(0, 8).map(n => take(n)), pseudo: [take(el, '::before'), take(el, '::after')], transition_s: getComputedStyle(el).transitionDuration };
  }, [i, PROPS]);
  const results = [];
  for (const [i, on] of picked.entries()) {
    try {
      await page.mouse.move(3, 3); await page.waitForTimeout(350); const before = await read(i); if (!before) continue;
      await page.mouse.move(before.x, before.y, { steps: 6 }); await page.waitForTimeout(650); const after = await read(i); if (!after) continue;
      const diff = (a, b) => Object.fromEntries(PROPS.filter(p => a[p] !== b[p]).map(p => [p, [a[p], b[p]]]));
      const names = (a, b) => [...new Set(a.flatMap((x, k) => (b[k] ? PROPS.filter(p => x[p] !== b[k][p]) : [])))];
      results.push({ on, words: before.words, changed: diff(before.self, after.self), inside_changed: names(before.inside, after.inside), pseudo_changed: names(before.pseudo, after.pseudo), transition_s: before.transition_s });
    } catch (e) { results.push({ on, failed: String(e.message).slice(0, 80) }); }
  }
  await page.mouse.move(3, 3);
  return results;
};

/* ---- scroll the page in steps, sampling every frame --------------------------------------------------------------- */
const drive = async (page, cdp, name, vp, total, cap, pause = 1200) => {
  const step = Math.round(vp.height * 0.6), steps = Math.max(8, Math.min(cap, Math.ceil(total / step))), lags = []; let driver = name === 'desktop' ? 'wheel' : 'touch', ignored = null;
  if (name === 'desktop') await page.mouse.move(vp.width / 2, vp.height / 2);
  for (let i = 0; i < steps; i++) {
    if (driver === 'touch') {
      const done = await Promise.race([cdp.send('Input.synthesizeScrollGesture', { x: Math.round(vp.width / 2), y: Math.round(vp.height * 0.72), yDistance: -step, speed: 1800, gestureSourceType: 'touch' }).then(() => true, () => false), new Promise(r => setTimeout(() => r(false), 5000))]);
      if (!done) driver = 'script';
    }
    if (driver === 'wheel') for (let k = 0; k < 6; k++) { await page.mouse.wheel(0, step / 6); await page.waitForTimeout(24); }
    if (driver === 'script') await page.evaluate(d => window.scrollBy({ top: d, behavior: 'smooth' }), step);
    await page.evaluate(() => window.__dna.poke()); await page.waitForTimeout(pause);
    lags.push(await page.evaluate(() => window.__dna.lag()));
    // a page that does not answer the wheel or the finger (scrolling locked, or handled by its own script) is moved by script instead, and the reading says so
    if (i === 1 && driver !== 'script' && total > 200 && (await page.evaluate(() => scrollY)) < 2) { ignored = driver; driver = 'script'; }
  }
  return { driver, input_ignored: ignored, steps, step_px: step, lag_ms: lags };
};

const mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', chromePath = process.env.CHROME_PATH || (fs.existsSync(mac) ? mac : '/usr/bin/google-chrome');
const browser = await chromium.launch({ executablePath: fs.existsSync(chromePath) ? chromePath : undefined, args: ['--no-sandbox'] });

if (args.includes('--surfaces')) {   // a second, short visit: only the surfaces of the laid-out page at 1440, added to the evidence already on disk under `supplement`
  const file = path.join(out, 'evidence.json'), kept = JSON.parse(fs.readFileSync(file, 'utf8'));
  const ctx = await browser.newContext({ viewport: VIEWS[0][1], deviceScaleFactor: 1 }); await ctx.addInitScript(INIT, NAMED); const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }); await page.waitForTimeout(3500); await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  const height = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight);
  for (let y = 0; y < height; y += 800) { await page.evaluate(to => window.scrollTo(0, to), y); await page.waitForTimeout(140); }
  await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(800);
  const read = await page.evaluate(READ, CONSENT);
  kept.supplement = { measured: new Date().toISOString(), view: 'desktop', note: 'a second visit, for rules drawn by pseudo-elements and <hr>, which the first reading did not count', surfaces: read.surfaces };
  fs.writeFileSync(file, JSON.stringify(kept, null, 1)); await browser.close();
  console.log(JSON.stringify({ id, rules: read.surfaces.rules, shadows: read.surfaces.shadows, boxes: read.surfaces.filled_or_framed_boxes })); process.exit(0);
}
const evidence = { id, url, measured: new Date().toISOString(), tool: 'lib/qa/inspect.mjs', profile: QUICK ? 'quick' : 'full', browser: `headless Chrome ${browser.version()}`, method: METHOD, views: {}, failed: [] };
const note = (where, e) => evidence.failed.push(`${where}: ${String(e && e.message ? e.message : e).slice(0, 160)}`);

for (const [name, vp] of VIEWS) {
  const phone = name === 'mobile';
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, userAgent: phone ? PHONE : undefined, isMobile: phone, hasTouch: phone });
  await ctx.addInitScript(INIT, NAMED);
  const page = await ctx.newPage(), cdp = await ctx.newCDPSession(page), view = { status: null }; let bytes = 0, requests = 0;
  await cdp.send('Network.enable'); cdp.on('Network.requestWillBeSent', () => { requests++; }); cdp.on('Network.loadingFinished', e => { bytes += e.encodedDataLength || 0; });
  const shot = file => (SHOTS ? page.screenshot({ path: path.join(out, file), type: 'jpeg', quality: 62 }).catch(() => {}) : null);
  try {
    const began = Date.now(), response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }); view.status = response ? response.status() : null; view.final_url = page.url();
    const until = async ms => { const left = ms - (Date.now() - began); if (left > 0) await page.waitForTimeout(left); };
    if (SHOTS) { await page.waitForTimeout(350); await shot(`${name}-load-0.35s.jpg`); await page.waitForTimeout(900); await shot(`${name}-load-1.25s.jpg`); await page.waitForTimeout(2250); await shot(`${name}-load-3.5s.jpg`); }
    await until(PACE.load); view.load = await page.evaluate(() => ({ ...window.__dna.finish(), animations_running: document.getAnimations().filter(a => a.playState === 'running').length })).catch(e => { note(`${name} load sampling`, e); return null; });
    await page.waitForLoadState('networkidle', { timeout: PACE.idle }).catch(() => {});
    view.lab = { note: 'one run, headless Chrome, this machine and connection: indicative, not field data', lcp: await page.evaluate(() => window.__dna.lcp), cls_on_load: +(await page.evaluate(() => window.__dna.cls)).toFixed(3), requests, transferred_bytes: Math.round(bytes) };

    const total = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight);
    await page.evaluate(() => window.__dna.start());
    const driven = await drive(page, cdp, name, vp, total, PACE.steps[name], PACE.pause).catch(e => { note(`${name} scroll drive`, e); return null; });
    const sampled = await page.evaluate(() => window.__dna.finish()).catch(e => { note(`${name} scroll sampling`, e); return null; });
    view.scroll = sampled && driven ? { ...driven, page_scrolls_natively: sampled.session.travelled_px > 40, ...sampled } : null;

    const height = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight);   // walk the rest, so what loads late is there to read
    for (let y = await page.evaluate(() => scrollY); y < height; y += Math.round(vp.height * 0.9)) { await page.evaluate(to => window.scrollTo(0, to), y); await page.waitForTimeout(140); }
    if (SHOTS) for (const part of [0, 25, 50, 75, 100]) { await page.evaluate(to => window.scrollTo(0, to), Math.round(height * part / 100)); await page.waitForTimeout(1000); if (!phone || part % 50 === 0) await shot(`${name}-scroll-${part}.jpg`); }
    await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(800);
    Object.assign(view, await page.evaluate(READ, CONSENT));
    if (!phone) view.pointer = await hover(page).catch(e => { note('pointer', e); return null; });
    if (SHOTS) await page.screenshot({ path: path.join(out, `${name}-full.jpg`), type: 'jpeg', quality: 55, fullPage: true }).catch(e => note(`${name} full-page screenshot`, e));
  } catch (e) { note(name, e); }
  evidence.views[name] = view; await ctx.close();
}

// the same page for a visitor who asked for less motion, and the lag of plain scrolling in this browser
try {
  const ctx = await browser.newContext({ viewport: VIEWS[0][1], deviceScaleFactor: 1, reducedMotion: 'reduce' }); await ctx.addInitScript(INIT, NAMED); const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }); await page.waitForTimeout(PACE.calm);
  const calm = await page.evaluate(() => ({ ...window.__dna.finish(), animations_running: document.getAnimations().filter(a => a.playState === 'running').length }));
  const normal = evidence.views.desktop.load;
  evidence.reduced_motion = { asked_with: `prefers-reduced-motion: reduce, desktop, first ${PACE.calm / 1000} s`, reveals_on_load: calm.reveals.elements, reveals_on_load_normally: normal ? normal.reveals.elements : null, animations_running: calm.animations_running, animations_running_normally: normal ? normal.animations_running : null };
  if (!QUICK) { const blank = await ctx.newPage(); await blank.goto('data:text/html,<body style="margin:0;height:9000px">'); await blank.waitForTimeout(300); await blank.mouse.move(700, 450); const lags = [];
  for (let i = 0; i < 3; i++) { for (let k = 0; k < 6; k++) { await blank.mouse.wheel(0, 90); await blank.waitForTimeout(24); } await blank.evaluate(() => window.__dna.poke()); await blank.waitForTimeout(700); lags.push(await blank.evaluate(() => window.__dna.lag())); }
  evidence.baseline_lag_ms = lags; }
  await ctx.close();
} catch (e) { note('reduced motion and baseline', e); }

await browser.close();
fs.writeFileSync(evidenceFile || path.join(out, 'evidence.json'), JSON.stringify(evidence, null, 1));
console.log(JSON.stringify({ id, desktop: evidence.views.desktop?.status ?? null, mobile: evidence.views.mobile?.status ?? null, failed: evidence.failed, out }));
