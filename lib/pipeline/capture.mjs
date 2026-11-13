#!/usr/bin/env node
/* capture.mjs — step 1 of the pipeline. Opens the client's site server-side (Playwright), runs the
   browser-side audit modules (inventory.js, assets.js), downsizes the big images into data URIs,
   screenshots desktop + mobile, and writes everything to out/<slug>/.
   Usage: node lib/pipeline/capture.mjs https://example.com [--out out] [--chrome /path/to/chrome]
   Default: analyze only the submitted landing page; --site-wide opts into legacy link discovery.
   Output: out/<slug>/{inventory.json, assets.json, images.json, before-desktop.png, before-mobile.png, before-hero.jpg, cards.json (price cards and large figures, lib/audit/cards.js), product.json (the product's own pages at desk and phone width, lib/pipeline/product.mjs; --no-product skips it)} */
import { chromium } from 'playwright';
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { productShots } from './product.mjs';
const HERE = path.dirname(fileURLToPath(import.meta.url)); const ROOT = path.resolve(HERE, '..', '..');
const args = process.argv.slice(2); const url = args.find(a => !a.startsWith('--')); if (!url) { console.error('url required'); process.exit(1); }
const siteWide = args.includes('--site-wide');
const opt = (k, d) => { const i = args.indexOf(k); return i > -1 ? args[i + 1] : d; };
const outRoot = opt('--out', 'out'); const chromePath = opt('--chrome', process.env.CHROME_PATH || '/usr/bin/google-chrome');
const slug = url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
const out = path.join(outRoot, slug); fs.mkdirSync(out, { recursive: true });

const inventorySrc = fs.readFileSync(path.join(ROOT, 'lib/audit/inventory.js'), 'utf8');
const assetsSrc = fs.readFileSync(path.join(ROOT, 'lib/audit/assets.js'), 'utf8');
const cardsSrc = fs.readFileSync(path.join(ROOT, 'lib/audit/cards.js'), 'utf8');
// images.js — collect source images, not a handful of early page elements.
const imagesSrc = `(async () => {
  const seen = new Set(); const list = []; const failed = [];
  // An <img> names more files than the one the page loaded: the widest entry of its srcset (and of its <picture>), the file
  // a lazy loader holds back in data-src, and — on WordPress — the original behind a thumbnail name (photo-300x200.jpg).
  // Every candidate is tried; the file that decodes largest is the picture.
  const abs = u => { try { return new URL(u, location.href).href; } catch { return ''; } };
  const widest = set => String(set || '').split(',').map(x => x.trim().split(/\\s+/)).filter(x => x[0]).map(x => ({ u: abs(x[0]), w: parseFloat(x[1]) || 0 })).sort((p, q) => q.w - p.w).map(x => x.u);
  const original = u => /-\\d{2,4}x\\d{2,4}(\\.[a-z0-9]{3,4})(\\?.*)?$/i.test(u) ? u.replace(/-\\d{2,4}x\\d{2,4}(\\.[a-z0-9]{3,4})(\\?.*)?$/i, '$1') : '';
  const named = i => { const from = [i.currentSrc || i.src, ...widest(i.getAttribute('srcset')).slice(0, 1), abs(i.dataset.src || i.dataset.lazySrc || i.dataset.original || ''), ...widest(i.dataset.srcset || i.dataset.lazySrcset).slice(0, 1),
      ...[...(i.closest('picture') ? i.closest('picture').querySelectorAll('source') : [])].flatMap(x => widest(x.getAttribute('srcset') || x.dataset.srcset).slice(0, 1))].filter(u => u && !u.startsWith('data:'));
    return [...new Set([...from.map(original).filter(Boolean), ...from])].slice(0, 5); };
  const load = async u => { const img = new Image(); img.crossOrigin = 'anonymous'; img.src = u; await img.decode(); return img; };
  const largest = async urls => { let best = null, err = null; for (const u of urls) { try { const img = await load(u); if (!best || img.naturalWidth > best.img.naturalWidth) best = { img, src: u }; } catch (e) { err = e; } } if (!best) throw err || new Error('no file'); return best; };
  const cands = [...document.images].map(i => ({ el: i, src: [i.currentSrc, i.src].find(u => u && !u.startsWith('data:')) || named(i)[0] || '', urls: named(i), w: i.naturalWidth, h: i.naturalHeight, alt: i.alt || '' }))
    .filter(i => i.urls.length && (i.w >= 400 && i.h >= 280 || (i.urls.length > 1 || i.urls[0] !== (i.el.currentSrc || i.el.src)) && (i.el.getBoundingClientRect().width >= 200 || i.w < 2)) && !/logo|icon|avatar|sprite/i.test(i.src + ' ' + i.alt));   // a client's photographs are often 400–800 px wide (how wide each may be drawn is measured later, from its detail); a thumbnail or a lazy placeholder is kept while a larger file is named for it — the file's own size decides, below
  // a film's poster is a photograph the client chose: it is taken like any picture, and the film's own frame only when there is none
  for (const v of document.querySelectorAll('video[poster]')) { const u = abs(v.getAttribute('poster')); if (u && !u.startsWith('data:')) cands.push({ src: u, urls: [original(u), u].filter(Boolean), w: 0, h: 0, alt: v.getAttribute('aria-label') || '', poster: v.currentSrc || v.src || '' }); }
  for (const el of document.querySelectorAll('*')) { const bg = getComputedStyle(el).backgroundImage; const m = bg && bg.match(/url\\("?([^")]+)"?\\)/); if (m && !m[1].startsWith('data:')) { const r = el.getBoundingClientRect(); if (r.width >= 280 && r.height >= 180) { const u = new URL(m[1], location.href).href; cands.push({ src: u, urls: [original(u), u].filter(Boolean), w: Math.round(r.width), h: Math.round(r.height), alt: '', bg: true }); } } }   // a tile of a grid is narrow on the page and the picture behind it is not: the file's own size decides, below
  const file = u => String(u).split(/[?#]/)[0];   // the same file under another query string is the same picture
  for (const c of cands) { if (seen.has(file(c.src)) || list.length >= 20) continue; seen.add(file(c.src));
    try { const got = await largest(c.urls || [c.src]); const img = got.img; if (got.src !== c.src) { if (seen.has(file(got.src))) continue; seen.add(file(got.src)); c.src = got.src; }
      if ((c.bg || c.poster !== undefined) && (img.naturalWidth < 500 || img.naturalHeight < 300)) continue;   // a texture or an ornament, not a photograph
      if (!c.bg && c.poster === undefined && (img.naturalWidth < 400 || img.naturalHeight < 280)) continue;
      if (c.poster) seen.add(c.poster);   // the film this poster stands for gives no second picture of the same thing   // a texture or an ornament, not a photograph
      const scale = Math.min(1, 1400 / img.naturalWidth); const cv = document.createElement('canvas'); cv.width = Math.round(img.naturalWidth * scale); cv.height = Math.round(img.naturalHeight * scale);
      const cx = cv.getContext('2d'); cx.drawImage(img, 0, 0, cv.width, cv.height);
      // a see-through picture (a diagram, a cut-out) is kept as JPEG, which has no transparency: left alone its clear
      // parts turn black, and dark lettering on it is gone (owner, 2026-11-13: a steps diagram shown as a black square).
      // It is laid on a plate its own ink reads on — white under dark ink, near-black under light ink.
      let plate = '';
      { const a = cx.getImageData(0, 0, cv.width, cv.height).data; let clear = 0, ink = 0, m = 0, k = 0; for (let i = 0; i < a.length; i += 4 * 13) { k++; if (a[i + 3] < 128) clear++; else { ink += .2126 * a[i] + .7152 * a[i + 1] + .0722 * a[i + 2]; m++; } }
        if (clear / k > .02) { plate = m && ink / m >= 128 ? '#111111' : '#ffffff'; cx.globalCompositeOperation = 'destination-over'; cx.fillStyle = plate; cx.fillRect(0, 0, cv.width, cv.height); cx.globalCompositeOperation = 'source-over'; } }
      // hero-grade: landscape, not tiny, has saturation + midtones (not a flat colour block)
      const d = cx.getImageData(0, 0, cv.width, cv.height).data; let sat = 0, lum = 0, n = 0; const tones = new Map(); for (let i = 0; i < d.length; i += 4 * 97) { const r = d[i], g = d[i+1], b = d[i+2]; const mx = Math.max(r, g, b), mn = Math.min(r, g, b); sat += mx ? (mx - mn) / mx : 0; lum += (r + g + b) / 3; n++; const t = (r >> 4) << 8 | (g >> 4) << 4 | b >> 4; tones.set(t, (tones.get(t) || 0) + 1); }
      // a notice, a diagram or an ornament is not a photograph: it is nearly colourless on white, or two flat tones cover more than seven tenths of it AND it is light (a dish on a white plate reads .4–.6, a notice .8).
      // A dark photograph — a stadium at night, a bar — is mostly two dark tones too, and is a photograph: on production two of three stadium pictures were dropped as notices.
      const flat = [...tones.values()].sort((p, q) => q - p).slice(0, 2).reduce((p, q) => p + q, 0) / n;
      list.push({ id: 'img' + (list.length + 1), src: c.src, w: cv.width, h: cv.height, alt: c.alt, bg: !!c.bg, ...(c.poster !== undefined ? { poster: true } : {}), ...(plate ? { plate } : {}), ...((sat / n < .1 && lum / n > 185) || (flat > .7 && lum / n > 140) ? { plain: true } : {}), flat: +flat.toFixed(2), ratio: +(cv.width / cv.height).toFixed(2), sat: +(sat / n).toFixed(2), lum: Math.round(lum / n), heroGrade: cv.width / cv.height > 1.3 && cv.width >= 1200, data: cv.toDataURL('image/jpeg', .72) });
    } catch (e) { failed.push({ src: c.src, w: c.w, h: c.h, alt: c.alt, error: String(e).slice(0, 80) }); } }
  // a site that shows its place in film has its pictures there: one still of each of its own videos
  for (const v of document.querySelectorAll('video')) { if (list.length >= 20) break; const src = v.currentSrc || v.src || ''; if (!src || seen.has(src) || Math.max(v.videoWidth, v.videoHeight) < 480 || Math.min(v.videoWidth, v.videoHeight) < 320) continue; seen.add(src);
    try { if (v.readyState < 2) continue; const scale = Math.min(1, 1400 / v.videoWidth); const cv = document.createElement('canvas'); cv.width = Math.round(v.videoWidth * scale); cv.height = Math.round(v.videoHeight * scale); const cx = cv.getContext('2d'); cx.drawImage(v, 0, 0, cv.width, cv.height);
      const d = cx.getImageData(0, 0, cv.width, cv.height).data; let lum = 0, n = 0; for (let i = 0; i < d.length; i += 4 * 97) { lum += (d[i] + d[i+1] + d[i+2]) / 3; n++; }
      if (lum / n < 12) continue;   // a black frame says nothing
      list.push({ id: 'img' + (list.length + 1), src, w: cv.width, h: cv.height, alt: v.getAttribute('aria-label') || '', video: true, ratio: +(cv.width / cv.height).toFixed(2), lum: Math.round(lum / n), heroGrade: false, data: cv.toDataURL('image/jpeg', .78) });
    } catch (e) { /* a film served from another host without permission cannot be read: it is left out, not failed */ } }
  for (const item of failed.slice(0, Math.max(0, 20 - list.length))) list.push({ id: 'img' + (list.length + 1), ...item });
  return list; })()`;


// logos.js — the row of customers' marks a page shows ("trusted by"): four or more small wide marks under one near
// ancestor, outside the bar and the footer. Each is kept as the page drew it (an inline svg serialised, an image read
// back); the words the page sets with them are kept as the label. Nothing is looked up anywhere else.
const logosSrc = `(async () => {
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const like = e => { const r = e.getBoundingClientRect(); return r.width >= 36 && r.width <= 260 && r.height >= 12 && r.height <= 96 && r.width / r.height >= 1.1; };
  const marks = [...document.querySelectorAll('img, svg')].filter(e => vis(e) && like(e) && !e.closest('header, nav, footer, button, form, a.btn, [role="navigation"]'));
  const groups = new Map();
  for (const m of marks) { let a = m.parentElement; for (let k = 0; k < 4 && a; k++, a = a.parentElement) { const inside = marks.filter(x => a.contains(x)); if (inside.length >= 4) { if (!groups.has(a)) groups.set(a, inside); break; } } }
  let best = null;
  for (const [a, list] of groups) { const r = a.getBoundingClientRect(); if (r.height > innerHeight * 1.2) continue; if (!best || list.length > best.list.length || (list.length === best.list.length && r.height < best.r.height)) best = { a, list, r }; }
  if (!best) return { label: '', items: [] };
  const bare = best.a.cloneNode(true); bare.querySelectorAll('img, svg').forEach(x => x.remove());   // the words beside the marks, not the letters drawn inside them
  const own = (bare.textContent || '').replace(/\\s+/g, ' ').trim(); let label = own.length <= 90 ? own : '';
  for (let p = best.a.previousElementSibling, k = 0; k < 2 && p && !label; k++, p = p.previousElementSibling) { const t = (p.innerText || '').replace(/\\s+/g, ' ').trim(); if (t && t.length <= 90) label = t; }
  const items = [], seen = new Set();
  for (const m of best.list.slice(0, 20)) { const r = m.getBoundingClientRect();
    try { let data = '', alt = '';
      if (m.tagName.toLowerCase() === 'svg') { const c = m.cloneNode(true); c.setAttribute('xmlns', 'http://www.w3.org/2000/svg'); if (!c.getAttribute('viewBox')) c.setAttribute('viewBox', '0 0 ' + Math.round(r.width) + ' ' + Math.round(r.height)); c.style.color = '#000';
        const xml = new XMLSerializer().serializeToString(c); if (xml.length > 60000) continue; data = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(xml))); alt = m.getAttribute('aria-label') || (m.querySelector('title') || {}).textContent || ''; }
      else { const src = m.currentSrc || m.src; if (!src) continue; alt = m.alt || '';
        if (src.startsWith('data:')) data = src.length < 120000 ? src : '';
        else { const res = await fetch(src); const blob = await res.blob(); if (blob.size > 160000 || !/^image\\//.test(blob.type)) continue; data = await new Promise(ok => { const fr = new FileReader(); fr.onload = () => ok(fr.result); fr.readAsDataURL(blob); }); } }
      if (!data || seen.has(data.slice(-240))) continue; seen.add(data.slice(-240)); items.push({ data, w: Math.round(r.width), h: Math.round(r.height), alt: String(alt).trim().slice(0, 60) });
    } catch (e) { /* a mark served from another host without permission cannot be read back: it is left out */ } }
  return { label: label.slice(0, 90), items: items.length >= 4 ? items.slice(0, 12) : [] }; })()`;

// visual shots: the page's own VISUAL elements (framed UI, videos, canvases, big images, cards with shadows) — never a whole section with its nav and headline
async function visualShots(page, prefix, max = 10, knownSrcs = []) {
  const shots = [];
  try {
    await page.evaluate(srcs => { window.__swKnown = new Set(srcs); }, knownSrcs);
    await page.evaluate(() => { for (const el of document.querySelectorAll('body *')) { const cs = getComputedStyle(el); if (cs.position === 'fixed' || cs.position === 'sticky') { el.setAttribute('data-sw-hide', el.style.visibility || ''); el.style.visibility = 'hidden'; } } });
    const blocks = await page.evaluate((max) => {
      const W = innerWidth; const cands = [];
      for (const el of document.querySelectorAll('img, video, canvas, picture, svg, iframe, div, figure, section > div')) {
        const r = el.getBoundingClientRect(); if (r.width < 420 || r.height < 240 || r.width > W * .98 && r.height > innerHeight * 1.3) continue;
        const cs = getComputedStyle(el); const tag = el.tagName.toLowerCase();
        const background = cs.backgroundImage?.match(/url\("?([^"\)]+)"?\)/);
        const bgSrc = background ? new URL(background[1], location.href).href : '';
        if ((tag === 'img' && window.__swKnown.has(el.currentSrc || el.src)) || (tag === 'picture' && el.querySelector('img') && window.__swKnown.has(el.querySelector('img').currentSrc)) || (bgSrc && window.__swKnown.has(bgSrc))) continue; // already captured as a source image
        const media = ['img', 'video', 'canvas', 'picture', 'svg', 'iframe'].includes(tag) || (cs.backgroundImage && cs.backgroundImage !== 'none' && /url\(/.test(cs.backgroundImage));
        const framed = !media && (cs.boxShadow !== 'none' || (parseFloat(cs.borderRadius) >= 8 && cs.borderStyle !== 'none')) && el.querySelector('img, video, canvas, svg, table, input, button');
        const textHeavy = (el.innerText || '').trim().length > 600;
        if (!(media || framed) || textHeavy) continue;
        cands.push({ x: Math.round(r.left), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height), text: (el.getAttribute('alt') || el.getAttribute('aria-label') || (el.innerText || '').trim().slice(0, 50)), area: r.width * r.height });
      }
      const out = []; for (const c of cands.sort((p, q) => q.area - p.area)) { if (!out.some(o => Math.abs(o.y - c.y) < 60 && Math.abs(o.x - c.x) < 60) && !out.some(o => c.x >= o.x && c.y >= o.y && c.x + c.w <= o.x + o.w && c.y + c.h <= o.y + o.h)) out.push(c); }
      return out.sort((p, q) => p.y - q.y).slice(0, max); }, max);
    let k = 0;
    for (const b of blocks) { k++; const clipH = Math.min(b.h, 1000); await page.evaluate(y => scrollTo(0, Math.max(0, y - 40)), b.y); await page.waitForTimeout(450);
      const top = await page.evaluate(() => scrollY); const cy = b.y - top; if (cy < 0 || cy + clipH > 1600) continue;
      const buf = await page.screenshot({ type: 'jpeg', quality: 78, clip: { x: b.x, y: cy, width: Math.min(b.w, 1440 - b.x), height: clipH } });
      shots.push({ id: prefix + k, src: 'visual-shot', w: Math.min(b.w, 1440 - b.x), h: clipH, alt: b.text, ratio: +(b.w / clipH).toFixed(2), heroGrade: b.w >= 900, shot: true, data: 'data:image/jpeg;base64,' + buf.toString('base64') }); }
    await page.evaluate(() => { for (const el of document.querySelectorAll('[data-sw-hide]')) { el.style.visibility = el.getAttribute('data-sw-hide'); el.removeAttribute('data-sw-hide'); } scrollTo(0, 0); }); await page.waitForTimeout(300);
  } catch (e) { console.warn('shots:', e.message); }
  return shots;
}

const NOT_A_SITE = /checking the site connection security|checking your browser|just a moment|verify you are (a )?human|enable cookies|requires cookies|attention required|access denied|captcha|please wait while we verify|404 not found|this site can.t be reached|domain (is )?for sale|parked domain/i;
async function notASite(page) {
  try { const t = await page.evaluate(() => (document.title + ' ' + document.body.innerText).replace(/\s+/g, ' ').slice(0, 1200)); const words = t.split(' ').length;
    if (NOT_A_SITE.test(t) && words < 140) return `The site answered with a bot check or an error page instead of its content ("${t.slice(0, 90).trim()}…"), so there was nothing to read.`;
    if (words < 12) return 'The page loaded with almost no text, so there was nothing to read.'; return ''; } catch { return ''; }
}
const exe = chromePath && fs.existsSync(chromePath) ? chromePath : undefined; // falls back to Playwright's bundled Chromium
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu'] });

// geometry.js — real page-coordinate rects (1440 viewport) of the things the agents will visibly work on
const geometrySrc = `(() => {
  const R = e => { const r = e.getBoundingClientRect(); return { x: Math.round(r.left), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height) }; };
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 8 && r.height > 8 && getComputedStyle(e).visibility !== 'hidden'; };
  const t = e => (e.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 80);
  const h1 = [...document.querySelectorAll('h1')].filter(vis)[0]; const h2s = [...document.querySelectorAll('h2,h3')].filter(vis).slice(0, 12);
  const nav = document.querySelector('nav, header'); const links = nav ? [...nav.querySelectorAll('a')].filter(vis) : [];
  const ctas = [...document.querySelectorAll('a,button')].filter(vis).filter(e => /btn|button|cta/i.test(e.className + ' ' + e.getAttribute('role')) || getComputedStyle(e).backgroundColor !== 'rgba(0, 0, 0, 0)').slice(0, 8);
  const imgs = [...document.images].filter(vis).filter(i => i.getBoundingClientRect().width >= 200).slice(0, 12);
  const logo = document.querySelector('header img, nav img, [class*="logo" i] img, header svg, nav svg, [class*="logo" i] svg');
  const secs = [...document.querySelectorAll('section, main > div, body > div > div, footer, header')].filter(vis).filter(e => e.getBoundingClientRect().height > 160).slice(0, 14);
  return { pageHeight: Math.round(document.documentElement.scrollHeight), h1: h1 ? { rect: R(h1), text: t(h1), px: Math.round(parseFloat(getComputedStyle(h1).fontSize)) } : null,
    headings: h2s.map(e => ({ rect: R(e), text: t(e) })), nav: nav ? { rect: R(nav), links: links.length } : null, links: links.slice(0, 40).map(e => ({ rect: R(e), text: t(e) })),
    ctas: ctas.map(e => ({ rect: R(e), text: t(e) })), images: imgs.map(i => ({ rect: R(i), w: i.naturalWidth, h: i.naturalHeight })), logo: logo && vis(logo) ? R(logo) : null,
    sections: secs.map(e => ({ rect: R(e), words: t(e).split(' ').length })) };
})()`;

let navLinks = [], routeLinks = [];   // the top bar's links and every route the home page links to: where the product is photographed
try {
  for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844, isMobile: true, deviceScaleFactor: 2 }]]) {
    const ctx = await browser.newContext({ viewport: vp, userAgent: name === 'mobile' ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1' : undefined });
    const page = await ctx.newPage(); await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(e => console.warn('goto:', e.message));
    // preloaders: give the page up to 8 s to show real text before judging it
    for (let i = 0; i < 16; i++) { const n = await page.evaluate(() => document.body.innerText.split(/\s+/).filter(Boolean).length).catch(() => 0); if (n >= 30) break; await page.waitForTimeout(500); }
    // a bot check or an error page is not the site: refuse to build a site out of it and tell the owner why
    const blocked = await notASite(page);
    if (blocked) { fs.writeFileSync(path.join(out, 'blocked.json'), JSON.stringify({ url, reason: blocked })); console.error('BLOCKED:', blocked); await browser.close(); process.exit(3); }
    // lazy content: scroll through
    await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += innerHeight) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } scrollTo(0, 0); });
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(out, `before-${name}.png`), fullPage: true });
    if (name === 'desktop') {
      await page.screenshot({ path: path.join(out, 'before-hero.jpg'), type: 'jpeg', quality: 80, clip: { x: 0, y: 0, width: 1440, height: 900 } });
      const inventory = await page.evaluate(inventorySrc);
      navLinks = await page.evaluate(() => [...document.querySelectorAll('header a[href], nav a[href], [role="navigation"] a[href]')].map(a => ({ url: a.href, label: (a.innerText || a.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim() }))).catch(() => []);
      routeLinks = ((inventory.sourceCoverage || {}).routes || []).map(r => ({ url: r.url, label: r.label || '' }));
      inventory.copy.textTruncated = inventory.copy.totalWords > inventory.copy.text.split(/\s+/).filter(Boolean).length;
      const assets = await page.evaluate(assetsSrc); fs.writeFileSync(path.join(out, 'assets.json'), JSON.stringify(assets, null, 1));
      const images = await page.evaluate(imagesSrc); fs.writeFileSync(path.join(out, 'images.json'), JSON.stringify(images));
      try { fs.writeFileSync(path.join(out, 'cards.json'), JSON.stringify(await page.evaluate(cardsSrc))); } catch (e) { console.warn('cards:', e.message.slice(0, 80)); }
      try { const logos = await page.evaluate(logosSrc); fs.writeFileSync(path.join(out, 'logos.json'), JSON.stringify(logos)); if (logos.items.length) console.log(JSON.stringify({ event: { role: 'Photos', text: `${logos.items.length} customer logo(s) found` + (logos.label ? ` · “${logos.label.slice(0, 60)}”` : '') } })); } catch (e) { console.warn('logos:', e.message.slice(0, 80)); }
      // visual shots on the home page, then the product's own sub-pages (features, product, how it works…) for more distinct visuals
      const homeShots = await visualShots(page, 'shot', 10, images.filter(i => i.data).map(i => i.src));
      // Publish the real page before the potentially long site crawl so the
      // existing live agent view has something to work over while it runs.
      try {
        fs.writeFileSync(path.join(out, 'geometry.json'), JSON.stringify(await page.evaluate(geometrySrc)));
        const ph = Math.min(7000, await page.evaluate(() => document.documentElement.scrollHeight));
        const session = await page.context().newCDPSession(page);
        try { const shot = await session.send('Page.captureScreenshot', { format: 'jpeg', quality: 72, captureBeyondViewport: true, clip: { x: 0, y: 0, width: 1440, height: ph, scale: 1 } });
          fs.writeFileSync(path.join(out, 'before-full.jpg'), Buffer.from(shot.data, 'base64'));
        } finally { await session.detach(); }
        console.log(JSON.stringify({ captureReady: true }));
      } catch (e) { console.warn('early capture:', e.message); }
      const subVisuals = [];
      let all = images.concat(homeShots);
      try {
        if (!siteWide) {
          const coverage = inventory.sourceCoverage || {sections:[], routes:[]};
          inventory.sourcePages = [];
          for (const route of coverage.routes || []) { route.status = 'not_scanned'; route.reason = 'Only the submitted landing page is analyzed'; }
          coverage.scope = 'landing_page_only'; coverage.routeLimit = 0;
          coverage.contentTruncated = !!inventory.copy.textTruncated || (coverage.sections || []).some(s => s.textTruncated || s.faqTruncated || s.panelsTruncated || s.testimonialsTruncated);
          coverage.complete = !coverage.contentTruncated && !coverage.sectionsTruncated;
          inventory.sourceCoverage = coverage;
          console.log(JSON.stringify({event:{role:'Reader',text:`Reading the landing page · ${coverage.sections?.length || 0} sections`}}));
          // A site keeps its photographs on the pages behind the first one (the menu, the rooms, the work). Only the landing
          // page is read and rebuilt, but a few of the pages it links to are opened FOR THEIR PICTURES: nothing of their
          // text enters the inventory, the coverage stays what it was, and the whole visit is boxed in time.
          if (!args.includes('--no-linked-pictures')) {
            const home = new URL(page.url()); const until = Date.now() + Math.max(2000, Math.min(90000, Number(process.env.SWARM_PICTURE_PAGES_MS) || 40000));
            const skip = /(?:^|\/)(?:log[-_]?in|sign[-_]?(?:in|up)|register|logout|checkout|cart|cesta|carrito|account|mi-cuenta|admin|privacy|privacidad|legal|aviso|cookies?|terms|condiciones|politica)(?:[\/._-]|$)|\.(?:pdf|zip|jpe?g|png|webp|gif|svg|mp4|mp3|xml|json)$/i;
            const likely = r => /gallery|galer|photo|foto|espacio|space|room|habitac|sala|carta|menu|men[uú]|work|project|proyecto|portfolio|about|nosotros|event|product|service|servicio|shop|tienda|ponuda|galerija|o-nama|usluge/i.test(r.url + ' ' + r.label) ? 0 : 1;
            const seenPath = new Set([home.pathname.replace(/\/+$/, '')]); const linked = [];
            for (const r of coverage.routes || []) { let u; try { u = new URL(r.url, home); } catch { continue; } const key = u.pathname.replace(/\/+$/, '');
              if (u.origin !== home.origin || seenPath.has(key) || skip.test(u.pathname) || u.search) continue; seenPath.add(key); linked.push({ url: u.origin + u.pathname, label: String(r.label || '').slice(0, 60) }); }
            linked.sort((p, q) => likely(p) - likely(q)); let opened = 0; const tookFrom = [];
            for (const route of linked.slice(0, 6)) { if (Date.now() > until - 3000 || subVisuals.length >= 12) break; opened++;
              try { const response = await page.goto(route.url, { waitUntil: 'domcontentloaded', timeout: Math.max(1500, Math.min(9000, until - Date.now())) });
                if (!response || !response.ok() || new URL(page.url()).origin !== home.origin) continue;
                await page.waitForLoadState('networkidle', { timeout: Math.max(300, Math.min(1500, until - Date.now())) }).catch(() => {});
                await page.evaluate(async () => { for (let y = 0; y < Math.min(document.body.scrollHeight, 20000); y += innerHeight) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); });
                const sub = (await page.evaluate(imagesSrc)).filter(i => i.data && !i.video && !i.plain && !all.some(x => x.src === i.src)).sort((p, q) => q.w * q.h - p.w * p.h).slice(0, 4).map((i, n) => ({ ...i, id: `p${opened}-img${n + 1}`, page: route.label || new URL(route.url).pathname }));
                if (sub.length) { subVisuals.push(...sub); all = all.concat(sub); tookFrom.push({ url: route.url, pictures: sub.length }); }
              } catch (e) { console.warn('linked pictures:', route.url, e.message.slice(0, 80)); } }
            coverage.pictureRoutes = tookFrom;
            if (opened) { console.log(JSON.stringify({ event: { role: 'Photos', text: `${subVisuals.length} more picture(s) from ${tookFrom.length} of ${opened} linked page(s)` } }));
              await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {}); await page.waitForTimeout(400); }
          }
        } else {
        const homeUrl = page.url(); const homeOrigin = new URL(homeUrl).origin;
        const coverage = inventory.sourceCoverage || { sections: [], routes: [] };
        const homeRoutes = coverage.routes || []; const homeRoutesTruncated = !!coverage.routesTruncated;
        inventory.sourcePages = []; coverage.routes = []; coverage.routesFound = 0;
        const pageLimit = Math.max(1, Math.min(200, Number(process.env.SWARM_CRAWL_PAGE_LIMIT) || 50));
        const timeLimit = Math.max(1000, Math.min(480000, Number(process.env.SWARM_CRAWL_TIME_MS) || 210000));
        const deadline = Date.now() + timeLimit; const maxRoutes = 5000;
        coverage.routeLimit = pageLimit; coverage.timeLimitMs = timeLimit; coverage.routesTruncated = false;
        const canonical = value => { try { const u = new URL(value, homeUrl); if (u.origin !== homeOrigin || !/^https?:$/.test(u.protocol)) return '';
          u.hash = ''; for (const key of [...u.searchParams.keys()]) if (/^(utm_.+|gclid|fbclid)$/i.test(key)) u.searchParams.delete(key);
          u.searchParams.sort(); u.pathname = u.pathname.replace(/\/+$/, '') || '/'; return u.href; } catch { return ''; } };
        const homeKey = canonical(homeUrl), known = new Map(), queue = [];
        const excluded = value => { const u = new URL(value), p = u.pathname;
          if (/(?:^|\/)(?:log[-_]?in|sign[-_]?(?:in|up)|register|registration|logout|checkout|cart|account|admin|delete|remove|unsubscribe|cancel|reset)(?:[\/._-]|$)/i.test(p) ||
              [...u.searchParams.keys()].some(k => /^(?:add[-_]to[-_]cart|remove[-_]item|delete|unsubscribe|logout|action)$/i.test(k))) return 'Account or transactional route is not opened';
          if (/\.(?:pdf|zip|jpg|jpeg|png|webp|gif|svg|mp4|mp3|xml|json)$/i.test(p)) return 'Non-HTML asset is not opened'; return ''; };
        const priority = r => /menu|pricing|price|services|service|product|features|contact|about|cijene|usluge|kontakt|ponuda|carta|precios/i.test(r.url + ' ' + r.label) ? 0 : 1;
        const addRoutes = (routes, parent, truncated) => {
          if (truncated) coverage.routesTruncated = true;
          for (const item of routes || []) { const key = canonical(item.url); if (!key || key === homeKey || known.has(key)) continue;
            coverage.routesFound++; if (known.size >= maxRoutes) { coverage.routesTruncated = true; continue; }
            const reason = excluded(key); const route = { url: key, label: String(item.label || '').slice(0,100), discoveredFrom: parent,
              status: reason ? 'excluded' : 'pending', reason: reason || 'Discovered and awaiting capture' };
            known.set(key, route); coverage.routes.push(route); if (!reason) queue.push(route);
          }
        };
        addRoutes(homeRoutes, homeUrl, homeRoutesTruncated);
        inventory.sourceCoverage = coverage;
        const progress = text => console.log(JSON.stringify({ event: { role: 'Reader', text } }));
        progress('Checking site links and sitemaps');
        // Sitemap entries extend link discovery; only same-origin, bounded
        // sitemap files are fetched and redirects are not followed.
        const sitemapQueue = [new URL('/sitemap.xml', homeOrigin).href];
        try { const robots = await page.request.get(new URL('/robots.txt', homeOrigin).href, { timeout: 2500, maxRedirects: 0 });
          if (robots.ok()) for (const line of (await robots.text()).slice(0, 100000).split(/\r?\n/)) {
            const match = line.match(/^\s*sitemap\s*:\s*(\S+)/i); const candidate = match && canonical(match[1]);
            if (candidate && /\.xml$/i.test(new URL(candidate).pathname)) sitemapQueue.push(candidate);
          }
        } catch {};
        const sitemapSeen = new Set(); let sitemapFiles = 0;
        while (sitemapQueue.length && sitemapFiles < 5 && Date.now() < deadline) {
          const mapUrl = canonical(sitemapQueue.shift()); if (!mapUrl || sitemapSeen.has(mapUrl)) continue; sitemapSeen.add(mapUrl); sitemapFiles++;
          try { const res = await page.request.get(mapUrl, { timeout: Math.max(300, Math.min(2500, deadline - Date.now())), maxRedirects: 0 });
            if (!res.ok()) continue; const xml = await res.text(); if (xml.length > 2000000) { coverage.routesTruncated = true; continue; }
            const parsed = await page.evaluate(xml => { const doc = new DOMParser().parseFromString(xml, 'application/xml'); if (doc.querySelector('parsererror')) return null;
              const root = doc.documentElement.localName; if (root !== 'urlset' && root !== 'sitemapindex') return null;
              return { index: root === 'sitemapindex', urls: [...doc.getElementsByTagNameNS('*', 'loc')].slice(0, 5001).map(x => x.textContent.trim()) }; }, xml);
            if (!parsed) continue; if (parsed.urls.length > 5000) coverage.routesTruncated = true;
            if (parsed.index) for (const item of parsed.urls.slice(0,5000)) { const u = canonical(item); if (u && /\.xml$/i.test(new URL(u).pathname)) sitemapQueue.push(u); }
            else addRoutes(parsed.urls.slice(0,5000).map(u => ({url:u,label:''})), mapUrl, false);
          } catch {}
        }
        // Unvisited sitemap indexes are work for later batches, not evidence
        // that the discovered routes themselves were truncated.
        coverage.sitemapQueue = sitemapQueue;
        coverage.sitemapSeen = [...sitemapSeen];
        coverage.sitemapsAttempted = sitemapFiles;
        progress(`Mapping site · ${queue.length} pages discovered`);
        let attempted = 0;
        while (queue.length && attempted < pageLimit && Date.now() < deadline) {
          queue.sort((a,b) => priority(a) - priority(b)); const route = queue.shift(); attempted++; const pi = attempted;
          progress(`Reading page ${attempted} · ${route.label || new URL(route.url).pathname}`.slice(0,110));
          try { const response = await page.goto(route.url, { waitUntil: 'domcontentloaded', timeout: Math.max(1000, Math.min(12000, deadline - Date.now())) });
            if (!response || !response.ok() || new URL(page.url()).origin !== homeOrigin) { route.status = 'failed'; route.reason = response && !response.ok() ? `HTTP ${response.status()}` : 'Page failed or redirected outside the source site'; continue; }
            await page.waitForLoadState('networkidle', { timeout: Math.max(300, Math.min(1200, deadline - Date.now())) }).catch(() => {});
            await page.evaluate(async () => { for (let y = 0; y < Math.min(document.body.scrollHeight, 30000); y += innerHeight) { scrollTo(0, y); await new Promise(r => setTimeout(r, 50)); } scrollTo(0, 0); });
            const subText = await page.evaluate(() => (document.title + ' ' + document.body.innerText).replace(/\s+/g, ' ').slice(0, 1200));
            if (NOT_A_SITE.test(subText) && subText.split(' ').length < 140) { route.status = 'failed'; route.reason = 'Page returned a bot check or error'; continue; }
            if (subText.trim().split(/\s+/).filter(Boolean).length < 12) { route.status = 'failed'; route.reason = 'Page contained too little readable text'; continue; }
            const subInventory = await page.evaluate(inventorySrc);
            route.status = 'visited'; route.reason = 'Source content captured; not a generated page'; route.finalUrl = page.url();
            inventory.sourcePages.push({ url: page.url(), requestedUrl: route.url, title: subInventory.title, navLabel: route.label,
              copy: { ...subInventory.copy, text: subInventory.copy.text.slice(0, 40000), textTruncated: subInventory.copy.text.length > 40000 || subInventory.copy.totalWords > subInventory.copy.text.split(/\s+/).length },
              actions: subInventory.actions || [], forms: subInventory.forms || [], seo: subInventory.seo,
              sectionsFound: subInventory.sourceCoverage?.sectionsFound || 0, sectionsTruncated: !!subInventory.sourceCoverage?.sectionsTruncated,
              sections: (subInventory.sourceCoverage?.sections || []).map(s => ({ ...s, id: `p${pi}-${s.id}` })) });
            addRoutes(subInventory.sourceCoverage?.routes, page.url(), subInventory.sourceCoverage?.routesTruncated);
            if (pi <= 8) { try { const sub = (await page.evaluate(imagesSrc)).filter(i => i.data && !all.some(x => x.src === i.src)).slice(0, 4).map((i,n) => ({ ...i, id: `p${pi}-img${n+1}`, page: route.label }));
              const subShots = (await visualShots(page, `p${pi}-shot`, 4, all.filter(i => i.data).map(i => i.src))).map(x => ({ ...x, page: route.label }));
              subVisuals.push(...sub, ...subShots); all = all.concat(sub, subShots); } catch (e) { console.warn('subpage visuals:', e.message.slice(0,80)); } }
          } catch (e) { route.status = 'failed'; route.reason = 'Page could not be captured'; console.warn('sub', route.url, e.message.slice(0,80)); }
        }
        for (const route of queue) { route.status = 'limit'; route.reason = attempted >= pageLimit ? 'Page limit reached' : 'Time limit reached'; }
        coverage.attempted = attempted;
        coverage.contentTruncated = !!inventory.copy.textTruncated || (coverage.sections || []).some(s => s.textTruncated || s.faqTruncated || s.panelsTruncated || s.testimonialsTruncated) || inventory.sourcePages.some(p => p.copy.textTruncated || p.sectionsTruncated || p.sections.some(s => s.textTruncated || s.faqTruncated || s.panelsTruncated || s.testimonialsTruncated));
        coverage.complete = !coverage.sitemapQueue.length && !coverage.contentTruncated && !coverage.routesTruncated && !coverage.sectionsTruncated && !inventory.sourcePages.some(p => p.sectionsTruncated) && coverage.routes.every(r => r.status === 'visited' || r.status === 'excluded');
        coverage.scope = 'public same-origin links discovered from captured pages; account routes and non-HTML assets excluded';
        progress(`Site map · ${coverage.routes.filter(r => r.status === 'visited').length} read · ${coverage.routes.filter(r => r.status === 'failed' || r.status === 'limit').length} need review`);
        await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {}); await page.waitForTimeout(400);
        }
      } catch (e) {
        const coverage = inventory.sourceCoverage || {};
        coverage.complete = false; coverage.error = 'Site mapping stopped unexpectedly';
        for (const route of coverage.routes || []) if (route.status === 'pending') { route.status = 'limit'; route.reason = coverage.error; }
        console.log(JSON.stringify({ event: { role: 'Reader', text: 'Site mapping stopped; some pages need review' } }));
        console.warn('subpages:', e.message);
      }
      fs.writeFileSync(path.join(out, 'inventory.json'), JSON.stringify(inventory, null, 1));
      fs.writeFileSync(path.join(out, 'images.json'), JSON.stringify(images.concat(subVisuals, homeShots).slice(0, 28))); console.log('visuals:', all.length);
      // Returning from sampled subpages can restart the homepage's preloader
      // and lazy sections. Wake them before measuring and photographing it.
      try {
        for (let i = 0; i < 16; i++) { const n = await page.evaluate(() => document.body.innerText.split(/\s+/).filter(Boolean).length).catch(() => 0); if (n >= 30) break; await page.waitForTimeout(500); }
        await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += innerHeight) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } scrollTo(0, 0); });
        await page.waitForTimeout(600);
      } catch (e) { console.warn('home refresh:', e.message); }
      try { const geometry = await page.evaluate(geometrySrc); fs.writeFileSync(path.join(out, 'geometry.json'), JSON.stringify(geometry)); } catch (e) { console.warn('geometry:', e.message); }
      // full page as a JPEG the app can pan over (capped height, keeps 1440 width)
      try {
        const ph = Math.min(7000, await page.evaluate(() => document.documentElement.scrollHeight));
        // Playwright's clip is constrained to the viewport even for a taller
        // document. Capture beyond it so the preview can actually pan down.
        const session = await page.context().newCDPSession(page);
        try {
          const shot = await session.send('Page.captureScreenshot', { format: 'jpeg', quality: 72, captureBeyondViewport: true, clip: { x: 0, y: 0, width: 1440, height: ph, scale: 1 } });
          fs.writeFileSync(path.join(out, 'before-full.jpg'), Buffer.from(shot.data, 'base64'));
        } finally { await session.detach(); }
      } catch (e) { console.warn('full:', e.message); }
      console.log(`inventory: ${inventory.sections?.length} sections, ${inventory.copy?.totalWords} words · logo: ${assets.logo ? assets.logo.src : 'none'} · images: ${images.filter(i => i.data).length} embedded (${images.filter(i => i.heroGrade).length} hero-grade)`);
    } else {
      const mob = await page.evaluate(() => ({ scrollW: document.documentElement.scrollWidth, innerW: innerWidth, h1px: (() => { const h = document.querySelector('h1'); return h ? parseFloat(getComputedStyle(h).fontSize) : null; })(), tapTargetsSmall: [...document.querySelectorAll('a,button')].filter(a => { const r = a.getBoundingClientRect(); return r.width && (r.height < 40 || r.width < 40); }).length }));
      fs.writeFileSync(path.join(out, 'mobile.json'), JSON.stringify(mob, null, 1)); console.log('mobile:', JSON.stringify(mob));
    }
    await ctx.close();
  }
  // the product itself: the pages behind the top bar, at desk and phone width (lib/pipeline/product.mjs). Taken for every
  // site and used by the adapter only for a product; boxed in time like the linked pictures.
  if (!args.includes('--no-product') && !args.includes('--no-linked-pictures')) {   // --no-linked-pictures: no page behind the landing page is opened at all
    try { const ms = Math.max(5000, Math.min(120000, Number(process.env.SWARM_PRODUCT_MS) || 60000));
      const prod = await productShots(browser, { home: url, links: navLinks.concat(routeLinks), deadline: Date.now() + ms });
      fs.writeFileSync(path.join(out, 'product.json'), JSON.stringify(prod));
      console.log(JSON.stringify({ event: { role: 'Photos', text: `${prod.screens.length} product screen(s) and ${prod.phones.length} phone screen(s) from ${prod.pages.length} page(s)` } }));
    } catch (e) { console.warn('product:', String(e.message).slice(0, 120)); }
  }
} finally { await browser.close(); }
console.log('→', out);
