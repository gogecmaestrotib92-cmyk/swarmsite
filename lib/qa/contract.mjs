/* contract.mjs — THE CONTRACT. Mechanically checkable promises every page must keep, graded on the real render.
   Not taste: geometry, sizes, duplicates, limits. The critic grades taste; this grades the contract.
   node lib/qa/contract.mjs out/<slug>/bp-x.html --dir out/<slug>  → writes <dir>/contract.json and prints a JSON summary */
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path';
const args = process.argv.slice(2); const file = path.resolve(args[0]); const dir = args[args.indexOf('--dir') + 1] || path.dirname(file);
const chromePath = process.env.CHROME_PATH || '/usr/bin/google-chrome'; const exe = fs.existsSync(chromePath) ? chromePath : undefined;
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu'].concat(process.env.LIVETEST ? ['--proxy-server=direct://', '--proxy-bypass-list=*'] : []) });
const items = []; const add = (id, ok, detail, weight = 1) => items.push({ id, ok: !!ok, detail: String(detail || '').slice(0, 160), weight });

for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844, deviceScaleFactor: 2 }]]) {
  const ctx = await browser.newContext({ viewport: vp }); const page = await ctx.newPage(); await page.route(/^https?:\/\//, r => /fonts\.gstatic|fonts\.googleapis|cdnjs|unpkg/.test(r.request().url()) && process.env.LIVETEST ? r.abort() : r.continue()).catch(() => {});
  await page.goto('file://' + file + '?nomotion=1'); await page.waitForTimeout(500);
  await page.addStyleTag({ content: '[data-move],.sec *:not(.ps-s):not(.sp-f):not(.ps-s *):not(.sp-f *){opacity:1!important;transform:none!important;clip-path:none!important;filter:none!important}' }).catch(() => {});
  await page.click('#sw-skip').catch(() => {}); await page.waitForTimeout(300);
  const r = await page.evaluate(() => {
    const W = innerWidth, H = innerHeight; const out = {};
    const txt = e => (e.innerText || '').trim();
    const vis = e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 2 && r.height > 2 && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > .05; };
    // 1 — h1
    const h1 = document.querySelector('h1'); const h1w = h1 ? txt(h1).split(/\s+/).filter(Boolean).length : 0; out.h1 = { words: h1w, px: h1 ? parseFloat(getComputedStyle(h1).fontSize) : 0, lines: h1 ? Math.round(h1.getBoundingClientRect().height / parseFloat(getComputedStyle(h1).lineHeight || getComputedStyle(h1).fontSize)) : 0 };
    // 2 — first screen: a picture or a framed product visible?
    const imgs = [...document.querySelectorAll('img')].filter(vis);
    out.firstScreenImage = imgs.some(i => { const r = i.getBoundingClientRect(); return r.top < H && r.bottom > 0 && r.width >= W * .3 && r.height >= 120; });
    // 3 — images: natural size vs box (never upscaled > 1.35x), never duplicated
    const seen = new Map(); const bad = []; let dup = 0;
    for (const i of imgs) { const r = i.getBoundingClientRect(); if (r.width < 120 || r.height < 80) continue; const nw = i.naturalWidth || 0; const sc = nw ? (r.width * devicePixelRatio) / nw : 1;
      if (nw && sc > 1.35 && r.width > 300) bad.push(`${Math.round(r.width)}px box from ${nw}px source (x${sc.toFixed(2)})`);
      const src = i.currentSrc || i.src || ''; const key = src.length + '|' + src.slice(-240) + '|' + (i.getAttribute('style') || ''); if (seen.has(key)) dup++; else seen.set(key, 1); }
    out.upscaled = bad; out.duplicateImages = dup;
    // 4 — empty screens: walk the page in viewport-height slices and measure how much is covered by visible text/images
    const ph = document.documentElement.scrollHeight; const empties = []; const nodes = [...document.querySelectorAll('img, video, h1, h2, h3, p, li, button, a.btn, input, .lab, .gw, .mq-track, figure')].filter(vis).map(e => { const r = e.getBoundingClientRect(); return { top: r.top + scrollY, bottom: r.bottom + scrollY, left: r.left, w: r.width, h: r.height }; });
    // a pinned / sticky / type-wall runway keeps its panel on screen the whole way down: the panel counts along the full runway, not only where it sits now
    for (const sec of document.querySelectorAll('[data-sig="pinned"],[data-sig="typewall"],[data-sig="sticky"]')) { const r = sec.getBoundingClientRect(); const panel = sec.querySelector('.ps-sticky,.tw-sticky,.sp-sticky,.sp-f.on,.sp-frames') || sec; const pr = panel.getBoundingClientRect(); const covered = Math.min(1, Math.max(.5, pr.height / H)); nodes.push({ top: r.top + scrollY, bottom: r.bottom + scrollY, left: 0, w: innerWidth, h: r.height, runway: covered }); }
    for (let y = 0; y + H <= ph + 1; y += H * .5) { const rows = new Array(20).fill(0); for (const n of nodes) { const a = Math.max(y, n.top), b = Math.min(y + H, n.bottom); if (b <= a) continue; const s = Math.floor((a - y) / (H / 20)), e2 = Math.min(19, Math.floor((b - y - 1) / (H / 20))); for (let k = s; k <= e2; k++) rows[k] = 1; } const fill = rows.reduce((p, q) => p + q, 0) / 20; if (fill < .45) empties.push({ y: Math.round(y), fill: +fill.toFixed(2) }); }
    out.emptyScreens = empties; out.pageScreens = +(ph / H).toFixed(1);
    // 5 — overflow
    out.overflowX = document.documentElement.scrollWidth > W + 2;
    // 6 — CTA consistency
    const btns = [...document.querySelectorAll('a.btn:not(.ghost), button.btn')].filter(vis).map(b => txt(b).replace(/\s*→\s*$/, '').trim()).filter(Boolean); out.ctas = [...new Set(btns)];
    // 7 — h2 word counts
    out.h2 = [...document.querySelectorAll('h2.h2')].filter(vis).map(h => txt(h).split(/\s+/).filter(Boolean).length);
    // 8 — signature moves present & well formed
    out.sticky = [...document.querySelectorAll('[data-sig="sticky"]')].map(s => ({ frames: s.querySelectorAll('.sp-f img').length, rows: s.querySelectorAll('.sp-row').length, frameW: Math.round((s.querySelector('.sp-stage')?.getBoundingClientRect().width) || 0) }));
    out.pinned = [...document.querySelectorAll('[data-sig="pinned"]')].map(s => ({ slides: s.querySelectorAll('.ps-s').length }));
    // 9 — tiny text / contrast proxy: body text in a dark band must not be dark
    const lowc = []; for (const p of [...document.querySelectorAll('.sec p, .sec li')].filter(vis).slice(0, 200)) { const cs = getComputedStyle(p); const m = cs.color.match(/\d+/g); if (!m) continue; const lum = (+m[0] * .2126 + +m[1] * .7152 + +m[2] * .0722) / 255; let bg = p; let bgc = 'rgba(0, 0, 0, 0)'; while (bg && /rgba\(0, 0, 0, 0\)|transparent/.test(bgc)) { bgc = getComputedStyle(bg).backgroundColor; bg = bg.parentElement; } const b = (bgc.match(/\d+/g) || [255, 255, 255]); const blum = (+b[0] * .2126 + +b[1] * .7152 + +b[2] * .0722) / 255; const a = (m[3] !== undefined ? +m[3] : 1); if (a > .05 && Math.abs(lum - blum) < .25) lowc.push(txt(p).slice(0, 30)); }
    out.lowContrast = lowc.slice(0, 5);
    // 10 — sections count and the form
    out.sections = document.querySelectorAll('body > section, body > footer').length; out.hasForm = !!document.querySelector('form input');
    return out; });
  const m = name === 'mobile';
  if (!m) { add('h1-words', r.h1.words >= 2 && r.h1.words <= 8, `${r.h1.words} words`, 2); add('h1-lines', r.h1.lines <= 3, `${r.h1.lines} lines`); add('h1-size', r.h1.px >= 48, `${Math.round(r.h1.px)}px`); }
  add(`${name}-first-screen-visual`, r.firstScreenImage, r.firstScreenImage ? 'a picture or product is visible in the first screen' : 'no visual in the first screen', 3);
  add(`${name}-no-upscaled-images`, r.upscaled.length === 0, r.upscaled.join('; ') || 'ok', 2);
  add(`${name}-no-duplicate-images`, r.duplicateImages === 0, r.duplicateImages ? `${r.duplicateImages} repeated picture(s)` : 'ok', 3);
  add(`${name}-no-empty-screens`, r.emptyScreens.length === 0, r.emptyScreens.length ? `${r.emptyScreens.length} half-empty screen(s) at y=${r.emptyScreens.map(e => e.y).slice(0, 4).join(',')}` : 'ok', 3);
  add(`${name}-no-overflow`, !r.overflowX, r.overflowX ? 'horizontal overflow' : 'ok', 2);
  if (!m) { add('one-cta', r.ctas.length <= 2, r.ctas.join(' | '), 2); add('h2-short', r.h2.every(n => n <= 7), `h2 words: ${r.h2.join(',')}`); add('page-length', r.pageScreens >= 4 && r.pageScreens <= 14, `${r.pageScreens} screens`, 2); add('sections', r.sections >= 5 && r.sections <= 10, `${r.sections} sections`); }
  add(`${name}-sticky-frames`, r.sticky.every(s => s.frames >= 2 && s.frames === s.rows && s.frameW >= 300), JSON.stringify(r.sticky) || 'none', 2);
  add(`${name}-pinned-slides`, r.pinned.every(s => s.slides >= 2 && s.slides <= 5), JSON.stringify(r.pinned) || 'none');
  add(`${name}-contrast`, r.lowContrast.length === 0, r.lowContrast.join(' / ') || 'ok', 3);
  await ctx.close();
}
await browser.close();
const total = items.reduce((p, i) => p + i.weight, 0); const got = items.filter(i => i.ok).reduce((p, i) => p + i.weight, 0);
const rep = { score: Math.round(100 * got / total), passed: items.filter(i => i.ok).length, failed: items.filter(i => !i.ok).map(i => ({ id: i.id, detail: i.detail, weight: i.weight })), items };
fs.writeFileSync(path.join(dir, 'contract.json'), JSON.stringify(rep, null, 1)); console.log(JSON.stringify({ score: rep.score, passed: rep.passed, failed: rep.failed.map(f => f.id + ': ' + f.detail) }));
