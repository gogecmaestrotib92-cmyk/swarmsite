// template_gate.mjs — may this rendered template page be shown? The gates of the template library, on any rendered file.
//
//   node lib/qa/template_gate.mjs <page.html | http://address> [more pages …] [--widths 1440x900,390x844] [--crops DIR]
//        [--settle 2500] [--pause 900]   the longest a page is given to come to rest after loading and after each scroll (ms)
//        [--jobs 3]                      pages gated side by side in the one browser (both widths of a page always are)
//        [--fixed]                       sleep those times in full after loading and after every scroll, as the research tools do
//   → one JSON line per page: {page, ok, failed: [...], checks: {...}, ms}; exit 0 when every page passes, 1 when one fails, 2 when the tool could not run.
//   import { gate } from './template_gate.mjs'  →  await gate(browser, target, {widths, crops, settle, pause, fixed})
//
// A page of the template library is a variant offered to a client. A variant that fails here is not shown.
// The checks are the ones the templates were built against (research tools shots.mjs and legible.mjs, as they stood on
// 2026-11-12 11:39), brought here as one call, plus `overlap`, which the stress run needs:
//   sideways    the page scrolls sideways (asked to scroll 400 px to the right, it moves)
//   errors      a script error on the page
//   distorted   a picture or film drawn out of its own proportion (object-fit: cover is a crop, contain and scale-down a fit; neither is a distortion)
//   h1          not exactly one h1
//   legible     a text line whose ink does not read on the pixels actually behind it. At every screen down the page (so a
//               fixed header is judged over each thing that passes under it): the glyphs are hidden, the screen is
//               photographed, and the ink is compared with what is rendered in the line's box; a line's score is the
//               contrast at the 3rd-worst percentile of its pixels. Limit 4.5:1, or 3:1 from 24 px (18.6 px bold). Any
//               CSS colour is read; animations are paused and requestAnimationFrame is held while a screen is read; a
//               closed <details> is not on screen; SVG text is judged glyph by glyph where each letter stands, by the
//               median; a line in the faded edge of a mask, or under something else, is judged where it stands free.
//   overlap     a line of text lying over another line of text with nothing opaque between them
//   blank       a screen with a large empty region — no text, no picture with anything in it, nothing drawn: BLANK_SHARE of the screen beside something, BLANK_BAND across it (see BLANK_READ)
// contract.mjs and layout.mjs are the old pipeline's graders and are not used or changed here.
// No model. No network beyond what the page itself asks for (its fonts).
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';

export const WIDTHS = [['d', 1440, 900], ['m', 390, 844]];

export async function launch() {
  const chromePath = process.env.CHROME_PATH || '/usr/bin/google-chrome';
  return chromium.launch({ executablePath: chromePath && fs.existsSync(chromePath) ? chromePath : undefined, args: ['--no-sandbox'] });   // as the research tools launch it, so a reading here is the reading there
}

// every visible text line of the screen as it stands now: its box, its ink, its size; and every place where one line lies over another
const READ = () => { const out = [], over = []; let G = 0;
  const cv = document.createElement('canvas'); cv.width = cv.height = 1; const cx = cv.getContext('2d', { willReadFrequently: true }), memo = new Map();
  const rgba = c => { if (memo.has(c)) return memo.get(c); cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; const a = d[3] / 255; const v = a ? [d[0], d[1], d[2], a] : [0, 0, 0, 0]; memo.set(c, v); return v; };
  const vis = el => { for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const c = getComputedStyle(e); if (c.visibility === 'hidden' || c.display === 'none' || +c.opacity < .4) return false;
    // clipped away (the usual screen-reader-only box: 1px, clip rect(0 0 0 0) or clip-path inset(50%)) is not on screen
    if (/rect\(0px,? 0px,? 0px,? 0px\)/.test(c.clip) || /^inset\(50%/.test(c.clipPath)) return false;
    if (c.overflow !== 'visible') { const b = e.getBoundingClientRect(); if (b.width <= 1 && b.height <= 1) return false; } } return true; };
  const held = el => { for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const c = getComputedStyle(e).position; if (c === 'fixed' || c === 'sticky') return 1; } return 0; };
  const own = el => [...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim().length >= 2);
  // a point of an element's text that an ancestor with overflow other than visible cuts away (the hidden copy of a rolling link) is not on screen
  const clipped = (el, x, y) => { for (let e = el.parentElement; e && e !== document.body && e !== document.documentElement; e = e.parentElement) { const c = getComputedStyle(e); if (c.overflowX !== 'visible' || c.overflowY !== 'visible') { const k = e.getBoundingClientRect(); if (x < k.left || x > k.right || y < k.top || y > k.bottom) return true; } } return false; };
  // what lies on top at a point of a line, when it is another element's text with nothing opaque of its own under it
  const upon = (el, x, y) => { const t = document.elementFromPoint(x, y); if (!t || t === el || el.contains(t) || t.contains(el)) return null;
    if (!own(t) || !vis(t) || /^(INPUT|TEXTAREA|SELECT|OPTION)$/.test(t.tagName)) return null;
    const hit = [...t.childNodes].some(n => { if (n.nodeType !== 3 || n.nodeValue.trim().length < 2) return false; const r = document.createRange(); r.selectNodeContents(n); return [...r.getClientRects()].some(q => x >= q.left && x <= q.right && y >= q.top && y <= q.bottom); });
    if (!hit || clipped(t, x, y)) return null;
    for (let e = t; e && !e.contains(el); e = e.parentElement) { const c = getComputedStyle(e); if (rgba(c.backgroundColor)[3] > .5 || (c.backgroundImage && c.backgroundImage !== 'none') || (c.backdropFilter && c.backdropFilter !== 'none')) return null; }
    return t; };
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let t;
  while ((t = tw.nextNode())) { const s = t.nodeValue.trim(); if (s.length < 2) continue; const el = t.parentElement; if (!el || /^(SCRIPT|STYLE|NOSCRIPT|TITLE)$/.test(el.tagName) || !vis(el)) continue;
    const dt = el.closest('details:not([open])'); if (dt && !el.closest('summary')) continue;   // a closed answer is not on screen
    if (el instanceof SVGTextContentElement) { const gid = ++G;   // text on a path or turned: judged glyph by glyph where each letter stands, ink = its fill
      const cs = getComputedStyle(el), m = rgba(cs.fill); if (m[3] < .3) continue; let M, n; try { M = el.getScreenCTM(); n = el.getNumberOfChars(); } catch { continue; } if (!M) continue;
      const px = parseFloat(cs.fontSize) * Math.hypot(M.a, M.b);
      for (let i = 0; i < n; i += 3) { let e; try { e = el.getExtentOfChar(i); } catch { continue; } const gx = e.x + e.width / 2, gy = e.y + e.height / 2, X = M.a * gx + M.c * gy + M.e, Y = M.b * gx + M.d * gy + M.f;
        if (X < 6 || Y < 6 || X > innerWidth - 6 || Y > innerHeight - 6) continue; const t2 = document.elementFromPoint(X, Y); if (!(t2 && (t2 === el || el.contains(t2) || t2.contains(el)))) continue;
        out.push({ x: X - 3, y: Y - 3, w: 6, h: 6, ink: m.slice(0, 3), a: m[3], px, bold: +cs.fontWeight >= 600, s: s.slice(0, 44), fixed: 0, grp: gid }); }
      continue; }
    const cs = getComputedStyle(el); const m = rgba(cs.color); if (m[3] < .3) continue;
    const r = document.createRange(); r.selectNodeContents(t);
    for (const q of r.getClientRects()) { if (q.width < 6 || q.height < 6 || q.bottom < 2 || q.top > innerHeight - 2 || q.right < 2 || q.left > innerWidth - 2) continue;
      // the line must be wholly on screen and uncovered at its centre and both ends (a line sliding under a header or
      // cut by a moving strip's mask is not judged in that position; it is judged where it stands free)
      if (q.top < 0 || q.bottom > innerHeight || q.left < 0 || q.right > innerWidth) continue;
      if (clipped(el, q.left + q.width / 2, q.top + q.height / 2)) continue;
      const free = (x, y) => { const k = document.elementFromPoint(x, y); return k && (k === el || el.contains(k) || k.contains(el)); };
      let faded = false; for (let a = el; a && a !== document.body; a = a.parentElement) { const ms = getComputedStyle(a); if ((ms.maskImage && ms.maskImage !== 'none') || (ms.webkitMaskImage && ms.webkitMaskImage !== 'none')) { const k = a.getBoundingClientRect(); if (q.left < k.left + k.width * .14 || q.right > k.right - k.width * .14 || q.top < k.top + k.height * .08 || q.bottom > k.bottom - k.height * .08) faded = true; break; } }
      if (faded) continue;
      const my = q.top + q.height / 2;
      if (!held(el)) { const top = upon(el, q.left + q.width / 2, my) || upon(el, q.left + Math.min(12, q.width / 4), my) || upon(el, q.right - Math.min(12, q.width / 4), my);
        if (top && !held(top)) over.push({ under: s.slice(0, 44), upon: (top.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 44), x: Math.round(q.left), y: Math.round(q.top + scrollY) }); }
      if (!free(q.left + q.width / 2, my) || !free(q.left + 3, my) || !free(q.right - 3, my) || !free(q.left + q.width / 2, q.top + 2) || !free(q.left + q.width / 2, q.bottom - 2)
        || !free(q.left + 3, q.top + 2) || !free(q.right - 3, q.top + 2) || !free(q.left + 3, q.bottom - 2) || !free(q.right - 3, q.bottom - 2)) continue;   // and at its four corners: a bar over one corner would be scored as the line's ground
      out.push({ x: q.left, y: q.top + q.height * .22, w: q.width, h: q.height * .56, ink: m.slice(0, 3), a: m[3], px: parseFloat(cs.fontSize), bold: +cs.fontWeight >= 600, s: s.slice(0, 44), fixed: held(el) }); } }
  return { boxes: out, over }; };

// the contrast of each box's ink against the photographed screen, at the 3rd-worst percentile of its pixels
const SCORE = async ({ png, boxes, blank }) => { const im = new Image(); im.src = 'data:image/png;base64,' + png; await im.decode(); const c = document.createElement('canvas'); c.width = im.width; c.height = im.height; const g = c.getContext('2d', { willReadFrequently: true }); g.drawImage(im, 0, 0);
  const L = v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }, lum = (r, gg, b) => .2126 * L(r) + .7152 * L(gg) + .0722 * L(b);
  const scores = boxes.map(bx => { const d = g.getImageData(Math.floor(bx.x), Math.floor(bx.y), Math.max(1, Math.floor(bx.w)), Math.max(1, Math.floor(bx.h))).data, cs = [];
    for (let i = 0; i < d.length; i += 4 * 3) { const bg = [d[i], d[i + 1], d[i + 2]], ink = bx.ink.map((v, k) => v * bx.a + bg[k] * (1 - bx.a)), a = lum(...ink), q = lum(...bg); cs.push((Math.max(a, q) + .05) / (Math.min(a, q) + .05)); }
    cs.sort((x, y) => x - y); return +cs[Math.floor(cs.length * .03)].toFixed(2); });
  return blank ? { scores, blank: window.__blank(g, im.width, im.height, blank) } : scores; };

// blank — a screen with a large empty region: no text, no picture with anything in it, nothing drawn. The way a template
// built round pictures fails when the client has none: half a screen of bare ground beside a column of text, a dark band
// with a star or two in it, a card that holds one number. Measured on the screen as photographed with its text hidden:
// the screen is cut into cells of BLANK_CELL px; a cell is filled when a line of text stands in it, a picture covers a
// third of it (a picture is "bare", and does not count, when its own pixels hardly vary: a near-black sky, a flat
// gradient), or its own pixels show something drawn (BLANK_INK of them away from the cell's mean: a rule, a border, a
// mark). The largest rectangle of empty cells, as a share of the screen, fails at BLANK_SHARE when it stands beside
// something (an empty half, an empty side of a grid) and at BLANK_BAND when it runs the whole width (the air between two
// sections is a band; more than half a screen of it is a hole). Only the screen down to the end of the page's content
// counts, and not its foot: the ground below a short page is not a hole in it, nor is the air of a foot.
export const BLANK_CELL = 36, BLANK_SHARE = 0.35, BLANK_BAND = 0.55, BLANK_INK = 0.02, BLANK_BARE = 8;
const BLANK_READ = () => { const text = [], pics = []; let bottom = 0;
  const vis = el => { for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const c = getComputedStyle(e); if (c.visibility === 'hidden' || c.display === 'none' || +c.opacity < .4) return false; } return true; };
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let t;
  while ((t = tw.nextNode())) { if (t.nodeValue.trim().length < 1) continue; const el = t.parentElement; if (!el || /^(SCRIPT|STYLE|NOSCRIPT|TITLE)$/.test(el.tagName) || !vis(el)) continue;
    if (el.closest('details:not([open])') && !el.closest('summary')) continue;
    const r = document.createRange(); r.selectNodeContents(t); for (const q of r.getClientRects()) if (q.width > 2 && q.height > 2 && q.bottom > 0 && q.top < innerHeight) text.push([q.left, q.top, q.right, q.bottom]); }
  for (const el of document.querySelectorAll('body *')) { const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
    const tag = el.tagName; const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' && cs.position !== 'sticky' && cs.display !== 'contents' && !/^(SCRIPT|STYLE)$/.test(tag)) bottom = Math.max(bottom, r.bottom);
    if (r.bottom < 0 || r.top > innerHeight) continue;
    const pic = /^(IMG|VIDEO|CANVAS|IFRAME|PICTURE)$/.test(tag) || (tag === 'svg' && r.width >= 24 && r.height >= 24) || /url\(/.test(cs.backgroundImage) || /^(INPUT|TEXTAREA|SELECT)$/.test(tag);
    if (pic && vis(el)) pics.push([Math.max(0, r.left), Math.max(0, r.top), Math.min(innerWidth, r.right), Math.min(innerHeight, r.bottom)]); }
  // the foot of a page is a list of links beside a mark: its air is not judged — the screen counts down to where the foot begins
  const ft = [...document.querySelectorAll("footer")].pop(); if (ft) { const t = ft.getBoundingClientRect().top; if (t < innerHeight) bottom = Math.min(bottom, Math.max(0, t)); }
  return { text, pics, bottom: Math.min(innerHeight, bottom) }; };
// run in the scoring page on the screen SCORE has already drawn (g), so the photograph is decoded once
const BLANK_SCORE = (g, W, H, { text, pics, bottom, cell, ink, bare }) => {
  // luminance at every second pixel each way: a rule or a mark of 2 px is still seen, at a quarter of the work
  const d = g.getImageData(0, 0, W, H).data, w2 = W >> 1, h2 = H >> 1, L = new Float32Array(w2 * h2);
  for (let y = 0; y < h2; y++) for (let x = 0; x < w2; x++) { const i = ((y * 2) * W + x * 2) * 4; L[y * w2 + x] = .2126 * d[i] + .7152 * d[i + 1] + .0722 * d[i + 2]; }
  const sd = ([x0, y0, x1, y1]) => { let s = 0, s2 = 0, n = 0; for (let y = Math.floor(y0 / 2); y < Math.min(h2, y1 / 2); y += 2) for (let x = Math.floor(x0 / 2); x < Math.min(w2, x1 / 2); x += 2) { const v = L[y * w2 + x]; s += v; s2 += v * v; n++; } return n ? Math.sqrt(Math.max(0, s2 / n - (s / n) ** 2)) : 0; };
  const full = pics.filter(p => (p[2] - p[0]) * (p[3] - p[1]) > 0 && sd(p) >= bare), lines = text.map(q => [q[0] - 6, q[1] - 6, q[2] + 6, q[3] + 6]);
  const C = Math.floor(W / cell), R = Math.floor(Math.min(H, bottom) / cell), empty = [], k2 = cell >> 1;
  const hits = (r, x0, y0, x1, y1, need) => r.some(q => { const w = Math.min(x1, q[2]) - Math.max(x0, q[0]), h = Math.min(y1, q[3]) - Math.max(y0, q[1]); return w > 0 && h > 0 && w * h >= need; });
  for (let r = 0; r < R; r++) { const row = []; for (let k = 0; k < C; k++) { const x0 = k * cell, y0 = r * cell, x1 = x0 + cell, y1 = y0 + cell;
    let fill = hits(lines, x0, y0, x1, y1, 1) || hits(full, x0, y0, x1, y1, cell * cell / 3);
    if (!fill) { const X = k * k2, Y = r * k2; let s = 0; for (let y = Y; y < Y + k2; y++) for (let x = X; x < X + k2; x++) s += L[y * w2 + x]; const m = s / (k2 * k2); let off = 0;
      for (let y = Y; y < Y + k2; y++) for (let x = X; x < X + k2; x++) if (Math.abs(L[y * w2 + x] - m) > 12) off++; fill = off / (k2 * k2) >= ink; }
    row.push(!fill); } empty.push(row); }
  return { empty, W, H }; };
// the largest rectangle of empty cells (row by row, the heights of empty columns as a histogram) → {a, x, y, w, h} in cells
export function largestEmpty(grid) { const R = grid.length, C = R ? grid[0].length : 0, hgt = new Array(C).fill(0); let best = { a: 0 };
  for (let r = 0; r < R; r++) { for (let k = 0; k < C; k++) hgt[k] = grid[r][k] ? hgt[k] + 1 : 0; const st = [];
    for (let k = 0; k <= C; k++) { const h = k < C ? hgt[k] : 0; let s = k; while (st.length && st[st.length - 1][1] >= h) { const [i, hh] = st.pop(); const a = hh * (k - i); if (a > best.a) best = { a, x: i, y: r - hh + 1, w: k - i, h: hh }; s = i; } st.push([s, h]); } }
  return best; }
// one screen → the empty region as a share of the screen ({share: 0} when there is none)
export function blankOf({ empty, W, H }, cell = BLANK_CELL) {
  const say = (b, dx = 0) => b.a ? { share: +(b.a * cell * cell / (W * H)).toFixed(2), x: (b.x + dx) * cell, y: b.y * cell, w: b.w * cell, h: b.h * cell } : { share: 0 };
  const C = empty.length ? empty[0].length : 0, all = largestEmpty(empty), band = say(all);
  if (!all.a || all.w < C * .9) return { ...band, fails: band.share >= BLANK_SHARE };
  if (band.share >= BLANK_BAND) return { ...band, band: true, fails: true };
  // a band of air that does not fail by itself may hide an empty side: the largest region that does not run the whole width
  const k = Math.ceil(C * .6), left = say(largestEmpty(empty.map(r => r.slice(0, k)))), right = say(largestEmpty(empty.map(r => r.slice(C - k))), C - k);
  const side = left.share >= right.share ? left : right;
  return { ...side, fails: side.share >= BLANK_SHARE }; }

// Has the screen come to rest? Waits for the page's own finite animations and transitions to end and for what is on
// screen to stop moving (the boxes and opacity of its text and pictures, read twice 70 ms apart; what runs for ever —
// a marquee — is left out), up to `cap` ms. Returns the ms it waited. This stands where the research tools sleep a
// fixed 2.5 s after loading and 0.9 s after every scroll: a still screen is read at once, a moving one gets its time.
const REST = async cap => { const t0 = performance.now(), nap = ms => new Promise(r => setTimeout(r, ms));
  const anims = () => { try { return document.getAnimations(); } catch { return []; } };
  const ends = a => { try { const t = a.effect && a.effect.getComputedTiming(); return t && isFinite(t.endTime); } catch { return true; } };
  const snap = () => { const forever = anims().filter(a => !ends(a)).map(a => a.effect && a.effect.target).filter(Boolean); let s = 0, n = 0;
    for (const el of document.querySelectorAll('h1,h2,h3,h4,p,li,a,button,img,video,figure,blockquote,summary,[class]>span')) { const r = el.getBoundingClientRect(); if (r.bottom < 0 || r.top > innerHeight || !r.width || !r.height) continue;
      if (forever.some(t => t === el || t.contains(el))) continue; s += r.left * 3 + r.top * 7 + r.width * 11 + r.height * 13 + (+getComputedStyle(el).opacity) * 1009; if (++n >= 300) break; }
    return Math.round(s * 4); };
  await nap(40); let last = snap(), same = 0;
  while (performance.now() - t0 < cap) { await nap(70); const now = snap(), busy = anims().some(a => a.playState === 'running' && ends(a)); same = now === last && !busy ? same + 1 : 0; last = now; if (same >= 2) break; }
  return Math.round(performance.now() - t0); };

export async function gate(browser, target, { widths = WIDTHS, crops = '', settle = 2500, pause = 900, fixed = false } = {}) {
  const t0 = Date.now(), url = /^https?:\/\//.test(target) ? target : 'file://' + path.resolve(target);
  const checks = { sideways: [], errors: [], distorted: [], h1: [], legible: [], overlap: [], blank: [] }; let lines = 0; const timing = {};
  const dec = await browser.newPage();
  await dec.evaluate(`window.__blank = ${BLANK_SCORE.toString()}`);
  try {
    await Promise.all(widths.map(async ([n, w, h]) => {              // both widths at once: one browser, a page each
      const p = await browser.newPage({ viewport: { width: w, height: h } }); const T = { load: 0, lazy: 0, rest: 0, read: 0, screens: 0 }; let t = Date.now(); timing[n] = T;
      try {
        p.on('pageerror', e => checks.errors.push({ at: n, text: String(e).slice(0, 160) }));
        // script-driven motion (requestAnimationFrame) is held while a screen is read and photographed, then let go
        await p.addInitScript(() => { const raf = window.requestAnimationFrame.bind(window), held = []; window.__hold = false;
          window.requestAnimationFrame = cb => window.__hold ? (held.push(cb), 0) : raf(cb);
          window.__release = () => { window.__hold = false; held.splice(0).forEach(cb => raf(cb)); }; });
        await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        if (fixed) await p.waitForTimeout(settle);                    // --fixed: the research tools' own waits, for a reading to set beside theirs
        else { await p.evaluate(async () => { const cap = ms => new Promise(r => setTimeout(r, ms)); await Promise.race([new Promise(r => document.readyState === 'complete' ? r() : addEventListener('load', r, { once: true })), cap(8000)]); try { await Promise.race([document.fonts.ready, cap(4000)]); } catch {} }); await p.evaluate(REST, settle); }
        T.load = Date.now() - t; t = Date.now();
        // lazy pictures: pass down the page once, then wait for the pictures that started to arrive
        const H = await p.evaluate(async ([step, nap]) => { for (let y = 0; y < document.documentElement.scrollHeight; y += step) { scrollTo(0, y); await new Promise(r => setTimeout(r, nap)); } scrollTo(0, 0); return document.documentElement.scrollHeight; }, fixed ? [500, 150] : [700, 40]);
        if (fixed) await p.waitForTimeout(300);
        else await p.evaluate(async () => { await Promise.race([Promise.all([...document.images].filter(i => !i.complete && i.getAttribute('src')).map(i => new Promise(r => { i.addEventListener('load', r, { once: true }); i.addEventListener('error', r, { once: true }); }))), new Promise(r => setTimeout(r, 3000))]); });
        T.lazy = Date.now() - t;
        const seen = new Map(), over = new Map();
        for (let y = 0; y < H; y += h - 80) {
          t = Date.now(); await p.evaluate(y => scrollTo(0, y), y); if (fixed) await p.waitForTimeout(pause); else await p.evaluate(REST, pause); T.rest += Date.now() - t; t = Date.now(); T.screens++;
          await p.evaluate(() => { window.__hold = true; }); const fz = await p.addStyleTag({ content: '*,*::before,*::after{animation-play-state:paused!important}' }); await p.waitForTimeout(fixed ? 80 : 30);
          const { boxes, over: ov } = await p.evaluate(READ);
          const bl = await p.evaluate(BLANK_READ);
          const st = await p.addStyleTag({ content: '*,*::before,*::after{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important;caret-color:transparent!important;transition:none!important}svg text,svg text *{fill:transparent!important;stroke:transparent!important}' });
          await p.waitForTimeout(fixed ? 120 : 40); const png = (await p.screenshot({ type: 'png' })).toString('base64'); await st.evaluate(e => e.remove());
          const sc = await dec.evaluate(SCORE, { png, boxes, blank: { ...bl, cell: BLANK_CELL, ink: BLANK_INK, bare: BLANK_BARE } }), res = sc.scores;
          { const { fails, ...b } = blankOf(sc.blank); if (fails && checks.blank.filter(x => x.at === n).length < 10) checks.blank.push({ at: n, scroll: y, ...b }); }
          { const by = new Map(); boxes.forEach((bx, i) => { if (bx.grp) (by.get(bx.grp) || by.set(bx.grp, []).get(bx.grp)).push(i); });
            for (const idx of by.values()) { const v = idx.map(i => res[i]).sort((a, b) => a - b), med = v[Math.floor(v.length / 2)]; idx.forEach((i, k) => { res[i] = k === 0 ? med : 99; }); } }
          const shots = [];
          boxes.forEach((bx, i) => { const lim = (bx.px >= 24 || (bx.px >= 18.6 && bx.bold)) ? 3 : 4.5, key = bx.s + '|' + (bx.fixed ? Math.round(y / 400) : ''); lines++;
            if (res[i] < lim && !(seen.get(key) <= res[i])) { seen.set(key, res[i]); shots.push([bx, n + '-' + key.replace(/[^a-z0-9]+/gi, '_').slice(0, 30)]); } });
          for (const o of ov) { const key = o.under + '|' + o.upon; if (!over.has(key)) over.set(key, o); }
          if (crops) for (const [bx, name] of shots) await p.screenshot({ path: path.join(crops, name + '.png'), clip: { x: Math.max(0, bx.x - 60), y: Math.max(0, bx.y - 60), width: Math.min(w - Math.max(0, bx.x - 60), bx.w + 120), height: Math.min(h - Math.max(0, bx.y - 60), bx.h + 120) } }).catch(() => {});
          await fz.evaluate(e => e.remove()); await p.evaluate(() => window.__release && window.__release()); T.read += Date.now() - t;
        }
        for (const [k, v] of [...seen].sort((a, b) => a[1] - b[1])) checks.legible.push({ at: n, ratio: v, text: k.split('|')[0] });
        for (const o of over.values()) checks.overlap.push({ at: n, ...o });
        // the checks of shots.mjs, last: asking the page to scroll sideways moves it
        const s = await p.evaluate(async () => { scrollTo(0, 0); await new Promise(r => setTimeout(r, 120)); scrollTo(400, scrollY); await new Promise(r => setTimeout(r, 150));
          const media = [...document.querySelectorAll('img,video')].filter(m => m.offsetParent && (m.naturalWidth || m.videoWidth));
          return { sideways: scrollX, docW: document.documentElement.scrollWidth, vw: innerWidth, h1: document.querySelectorAll('h1').length, height: document.documentElement.scrollHeight,
            distorted: media.filter(m => { const f = getComputedStyle(m).objectFit; const a = (m.naturalWidth || m.videoWidth) / (m.naturalHeight || m.videoHeight); const b = m.getBoundingClientRect(); return f !== 'cover' && f !== 'contain' && f !== 'scale-down' && b.height > 0 && Math.abs((b.width / b.height) / a - 1) > .03; }).map(m => (m.currentSrc || m.src || '').split('/').pop().slice(0, 60)) }; });
        if (s.sideways > 0) checks.sideways.push({ at: n, px: s.sideways, page_width: s.docW, screen: s.vw });
        if (s.h1 !== 1) checks.h1.push({ at: n, count: s.h1 });
        for (const d of s.distorted) checks.distorted.push({ at: n, file: d });
      } finally { await p.close(); }
    }));
  } finally { await dec.close(); }
  for (const k of Object.keys(checks)) checks[k].sort((a, b) => (a.at < b.at ? -1 : a.at > b.at ? 1 : 0));   // the widths ran side by side: findings in a fixed order
  const failed = Object.keys(checks).filter(k => checks[k].length);
  return { page: target, ok: failed.length === 0, failed, checks, line_readings: lines, widths: widths.map(([, w, h]) => `${w}x${h}`), ms: Date.now() - t0, timing };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2), opt = k => { const i = args.indexOf(k); return i === -1 ? '' : args.splice(i, 2)[1] || ''; };
  const ws = opt('--widths'), crops = opt('--crops'), settle = +(opt('--settle') || 2500), pause = +(opt('--pause') || 900), jobs = Math.max(1, +(opt('--jobs') || 3)); const fi = args.indexOf('--fixed'), fixed = fi !== -1; if (fixed) args.splice(fi, 1);
  const widths = ws ? ws.split(',').map(x => { const [w, h] = x.split('x').map(Number); return [w >= 700 ? 'd' + w : 'm' + w, w, h || 900]; }) : WIDTHS;
  if (!args.length) { console.error('usage: node lib/qa/template_gate.mjs <page.html | http://address> [more …] [--widths 1440x900,390x844] [--crops DIR]'); process.exit(2); }
  if (crops) fs.mkdirSync(crops, { recursive: true });
  let browser, bad = 0;
  try { browser = await launch();
    // up to `jobs` pages at a time in the one browser; the answers are printed in the order the pages were given
    const results = new Array(args.length); let next = 0;
    await Promise.all(Array.from({ length: Math.min(jobs, args.length) }, async () => { for (;;) { const i = next++; if (i >= args.length) return;
      try { results[i] = await gate(browser, args[i], { widths, crops, settle, pause, fixed }); } catch (e) { results[i] = { page: args[i], ok: false, failed: ['tool'], error: String(e).slice(0, 300) }; } } }));
    for (const r of results) { if (!r.ok) bad = 1; console.log(JSON.stringify(r)); }
  } catch (e) { console.error(String(e).slice(0, 400)); process.exit(2); } finally { if (browser) await browser.close(); }
  process.exit(bad);
}
