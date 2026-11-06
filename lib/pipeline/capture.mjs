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
      list.push({ src: c.src, w: img.naturalWidth, h: img.naturalHeight, alt: c.alt, bg: !!c.bg, ratio: +(img.naturalWidth / img.naturalHeight).toFixed(2), sat: +(sat / n).toFixed(2), lum: Math.round(lum / n), heroGrade: img.naturalWidth / img.naturalHeight > 1.3 && img.naturalWidth >= 1200, data: cv.toDataURL('image/jpeg', .72) });
    } catch (e) { list.push({ src: c.src, w: c.w, h: c.h, alt: c.alt, error: String(e).slice(0, 80) }); } }
  return list; })()`;

const exe = chromePath && fs.existsSync(chromePath) ? chromePath : undefined; // falls back to Playwright's bundled Chromium
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu'] });
try {
  for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844, isMobile: true, deviceScaleFactor: 2 }]]) {
    const ctx = await browser.newContext({ viewport: vp, userAgent: name === 'mobile' ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1' : undefined });
    const page = await ctx.newPage(); await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(e => console.warn('goto:', e.message));
    // lazy content: scroll through
    await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += innerHeight) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } scrollTo(0, 0); });
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(out, `before-${name}.png`), fullPage: true });
    if (name === 'desktop') {
      await page.screenshot({ path: path.join(out, 'before-hero.jpg'), type: 'jpeg', quality: 80, clip: { x: 0, y: 0, width: 1440, height: 900 } });
      const inventory = await page.evaluate(inventorySrc); fs.writeFileSync(path.join(out, 'inventory.json'), JSON.stringify(inventory, null, 1));
      const assets = await page.evaluate(assetsSrc); fs.writeFileSync(path.join(out, 'assets.json'), JSON.stringify(assets, null, 1));
      const images = await page.evaluate(imagesSrc); fs.writeFileSync(path.join(out, 'images.json'), JSON.stringify(images));
      console.log(`inventory: ${inventory.sections?.length} sections, ${inventory.copy?.totalWords} words · logo: ${assets.logo ? assets.logo.src : 'none'} · images: ${images.filter(i => i.data).length} embedded (${images.filter(i => i.heroGrade).length} hero-grade)`);
    } else {
      const mob = await page.evaluate(() => ({ scrollW: document.documentElement.scrollWidth, innerW: innerWidth, h1px: (() => { const h = document.querySelector('h1'); return h ? parseFloat(getComputedStyle(h).fontSize) : null; })(), tapTargetsSmall: [...document.querySelectorAll('a,button')].filter(a => { const r = a.getBoundingClientRect(); return r.width && (r.height < 40 || r.width < 40); }).length }));
      fs.writeFileSync(path.join(out, 'mobile.json'), JSON.stringify(mob, null, 1)); console.log('mobile:', JSON.stringify(mob));
    }
    await ctx.close();
  }
} finally { await browser.close(); }
console.log('→', out);
