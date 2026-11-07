#!/usr/bin/env node
/* capture.mjs — step 1 of the pipeline. Opens the client's site server-side (Playwright), runs the
   browser-side audit modules (inventory.js, assets.js), downsizes the big images into data URIs,
   screenshots desktop + mobile, and writes everything to out/<slug>/.
   Usage: node lib/pipeline/capture.mjs https://example.com [--out out] [--chrome /path/to/chrome]
   Output: out/<slug>/{inventory.json, assets.json, images.json, before-desktop.png, before-mobile.png, before-hero.jpg} */
import { chromium } from 'playwright';
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url)); const ROOT = path.resolve(HERE, '..', '..');
const args = process.argv.slice(2); const url = args.find(a => !a.startsWith('--')); if (!url) { console.error('url required'); process.exit(1); }
const opt = (k, d) => { const i = args.indexOf(k); return i > -1 ? args[i + 1] : d; };
const outRoot = opt('--out', 'out'); const chromePath = opt('--chrome', process.env.CHROME_PATH || '/usr/bin/google-chrome');
const slug = url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
const out = path.join(outRoot, slug); fs.mkdirSync(out, { recursive: true });

const inventorySrc = fs.readFileSync(path.join(ROOT, 'lib/audit/inventory.js'), 'utf8');
const assetsSrc = fs.readFileSync(path.join(ROOT, 'lib/audit/assets.js'), 'utf8');
// images.js — generic: every rendered image >= 800px wide, not a logo, downsized in-page to <= 1400px JPEG q.72
const imagesSrc = `(async () => {
  const seen = new Set(); const list = [];
  const cands = [...document.images].map(i => ({ el: i, src: i.currentSrc || i.src, w: i.naturalWidth, h: i.naturalHeight, alt: i.alt || '' }))
    .filter(i => i.src && i.w >= 800 && i.h >= 400 && !/logo|icon|avatar|sprite/i.test(i.src + ' ' + i.alt));
  for (const el of document.querySelectorAll('*')) { const bg = getComputedStyle(el).backgroundImage; const m = bg && bg.match(/url\\("?([^")]+)"?\\)/); if (m && !m[1].startsWith('data:')) { const r = el.getBoundingClientRect(); if (r.width >= 600) cands.push({ src: new URL(m[1], location.href).href, w: Math.round(r.width), h: Math.round(r.height), alt: '', bg: true }); } }
  for (const c of cands) { if (seen.has(c.src) || list.length >= 8) continue; seen.add(c.src);
    try { const img = new Image(); img.crossOrigin = 'anonymous'; img.src = c.src; await img.decode();
      const scale = Math.min(1, 1400 / img.naturalWidth); const cv = document.createElement('canvas'); cv.width = Math.round(img.naturalWidth * scale); cv.height = Math.round(img.naturalHeight * scale);
      const cx = cv.getContext('2d'); cx.drawImage(img, 0, 0, cv.width, cv.height);
      // hero-grade: landscape, not tiny, has saturation + midtones (not a flat colour block)
      const d = cx.getImageData(0, 0, cv.width, cv.height).data; let sat = 0, lum = 0, n = 0; for (let i = 0; i < d.length; i += 4 * 97) { const r = d[i], g = d[i+1], b = d[i+2]; const mx = Math.max(r, g, b), mn = Math.min(r, g, b); sat += mx ? (mx - mn) / mx : 0; lum += (r + g + b) / 3; n++; }
      list.push({ id: 'img' + (list.length + 1), src: c.src, w: img.naturalWidth, h: img.naturalHeight, alt: c.alt, bg: !!c.bg, ratio: +(img.naturalWidth / img.naturalHeight).toFixed(2), sat: +(sat / n).toFixed(2), lum: Math.round(lum / n), heroGrade: img.naturalWidth / img.naturalHeight > 1.3 && img.naturalWidth >= 1200, data: cv.toDataURL('image/jpeg', .72) });
    } catch (e) { list.push({ id: 'img' + (list.length + 1), src: c.src, w: c.w, h: c.h, alt: c.alt, error: String(e).slice(0, 80) }); } }
  return list; })()`;


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
        if ((tag === 'img' && window.__swKnown.has(el.currentSrc || el.src)) || (tag === 'picture' && el.querySelector('img') && window.__swKnown.has(el.querySelector('img').currentSrc))) continue; // already captured as a real image
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

try {
  for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844, isMobile: true, deviceScaleFactor: 2 }]]) {
    const ctx = await browser.newContext({ viewport: vp, userAgent: name === 'mobile' ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1' : undefined });
    const page = await ctx.newPage(); await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(e => console.warn('goto:', e.message));
    // a bot check or an error page is not the site: refuse to build a site out of it and tell the owner why
    const blocked = await notASite(page);
    if (blocked) { fs.writeFileSync(path.join(out, 'blocked.json'), JSON.stringify({ url, reason: blocked })); console.error('BLOCKED:', blocked); await browser.close(); process.exit(3); }
    // lazy content: scroll through
    await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += innerHeight) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } scrollTo(0, 0); });
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(out, `before-${name}.png`), fullPage: true });
    if (name === 'desktop') {
      await page.screenshot({ path: path.join(out, 'before-hero.jpg'), type: 'jpeg', quality: 80, clip: { x: 0, y: 0, width: 1440, height: 900 } });
      const inventory = await page.evaluate(inventorySrc); fs.writeFileSync(path.join(out, 'inventory.json'), JSON.stringify(inventory, null, 1));
      const assets = await page.evaluate(assetsSrc); fs.writeFileSync(path.join(out, 'assets.json'), JSON.stringify(assets, null, 1));
      const images = await page.evaluate(imagesSrc); fs.writeFileSync(path.join(out, 'images.json'), JSON.stringify(images));
      // visual shots on the home page, then the product's own sub-pages (features, product, how it works…) for more distinct visuals
      let all = images.concat(await visualShots(page, 'shot', 10, images.map(i => i.src)));
      try {
        const links = await page.evaluate(() => { const o = location.origin; const seen = new Set([location.href.replace(/[#?].*$/, '').replace(/\/$/, '')]); const out = [];
          for (const a of document.querySelectorAll('nav a, header a, [role=navigation] a, footer a')) { const h = (a.href || '').replace(/[#?].*$/, '').replace(/\/$/, ''); if (!h.startsWith(o) || seen.has(h) || /login|sign|register|blog|news|privacy|terms|legal|contact|careers|docs\b|\.pdf$/i.test(h)) continue; seen.add(h); out.push({ href: h, text: (a.textContent || '').trim().slice(0, 30) }); }
          return out.slice(0, 4); });
        let pi = 0;
        for (const l of links) { pi++; try { await page.goto(l.href, { waitUntil: 'networkidle', timeout: 30000 }); await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += innerHeight) { scrollTo(0, y); await new Promise(r => setTimeout(r, 100)); } scrollTo(0, 0); }); await page.waitForTimeout(400);
            const sub = (await page.evaluate(imagesSrc)).filter(i => i.data && !images.some(x => x.src === i.src)).slice(0, 4).map((i, n) => ({ ...i, id: `p${pi}-img${n + 1}`, page: l.text }));
            const subShots = (await visualShots(page, `p${pi}-shot`, 4, all.map(i => i.src))).map(x => ({ ...x, page: l.text }));
            all = all.concat(sub, subShots); console.log('sub-page', l.href, sub.length + subShots.length, 'visuals'); } catch (e) { console.warn('sub', l.href, e.message.slice(0, 80)); }
          if (all.length >= 26) break; }
        await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {}); await page.waitForTimeout(400);
      } catch (e) { console.warn('subpages:', e.message); }
      fs.writeFileSync(path.join(out, 'images.json'), JSON.stringify(all.slice(0, 28))); console.log('visuals:', all.length);
      try { const geometry = await page.evaluate(geometrySrc); fs.writeFileSync(path.join(out, 'geometry.json'), JSON.stringify(geometry)); } catch (e) { console.warn('geometry:', e.message); }
      // full page as a JPEG the app can pan over (capped height, keeps 1440 width)
      try { const ph = Math.min(7000, await page.evaluate(() => document.documentElement.scrollHeight)); await page.screenshot({ path: path.join(out, 'before-full.jpg'), type: 'jpeg', quality: 72, clip: { x: 0, y: 0, width: 1440, height: ph } }); } catch (e) { console.warn('full:', e.message); }
      console.log(`inventory: ${inventory.sections?.length} sections, ${inventory.copy?.totalWords} words · logo: ${assets.logo ? assets.logo.src : 'none'} · images: ${images.filter(i => i.data).length} embedded (${images.filter(i => i.heroGrade).length} hero-grade)`);
    } else {
      const mob = await page.evaluate(() => ({ scrollW: document.documentElement.scrollWidth, innerW: innerWidth, h1px: (() => { const h = document.querySelector('h1'); return h ? parseFloat(getComputedStyle(h).fontSize) : null; })(), tapTargetsSmall: [...document.querySelectorAll('a,button')].filter(a => { const r = a.getBoundingClientRect(); return r.width && (r.height < 40 || r.width < 40); }).length }));
      fs.writeFileSync(path.join(out, 'mobile.json'), JSON.stringify(mob, null, 1)); console.log('mobile:', JSON.stringify(mob));
    }
    await ctx.close();
  }
} finally { await browser.close(); }
console.log('→', out);
