// composition.mjs — which composition does a page stand in at a width: its desk one or its phone one? Read, not judged.
//
//   node lib/qa/composition.mjs <page.html> [more pages …] [--widths 768,900]
//   → one JSON line: {"<absolute page path>": {desk: {"768": true, "900": false}, read: {"390": {...}, "768": {...}, …, "1440": {...}}}}
//
// A page is read at 390 and at 1440 — its two compositions as designed — and at each width asked about:
//   nav     links a visitor can see in the top 140 px (a folded menu shows one or two, an open one all of them)
//   share   the share of its text blocks and pictures that are narrower than 0.6 of the window (on a phone almost
//           everything runs the full width; at a desk most things stand in columns)
// A width stands in the desk composition when its menu is as open as at 1440 (asked only of a page whose menu differs
// between 390 and 1440) and its share is nearer to 1440's than to 390's. Used by lib/templates/tablet.py --sweep to
// decide whether a template may show its desk composition from 768 px. No model, no network.
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path';
const args = process.argv.slice(2); const wi = args.indexOf('--widths'); const ask = (wi === -1 ? '768,900' : args.splice(wi, 2)[1]).split(',').map(Number);
if (!args.length) { console.error('usage: node lib/qa/composition.mjs <page.html> [more pages …] [--widths 768,900]'); process.exit(2); }
const exe = process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH) ? process.env.CHROME_PATH : undefined;
const READ = () => { const z = parseFloat(document.documentElement.style.zoom) || 1;
  const vis = el => { const r = el.getBoundingClientRect(), cs = getComputedStyle(el); return r.width > 1 && r.height > 1 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > .05; };
  const nav = [...document.querySelectorAll('a')].filter(e => { if (!vis(e)) return false; const r = e.getBoundingClientRect(); return r.top + scrollY < 140 && r.width < innerWidth * .5 && r.left >= 0 && r.right <= innerWidth + 1; }).length;
  const blocks = [...document.querySelectorAll('h1,h2,h3,p,li,figure,img,video')].filter(e => vis(e) && e.getBoundingClientRect().width >= 60 * z && !e.closest('header,nav,footer'));
  return { nav, blocks: blocks.length, share: blocks.length ? +(blocks.filter(e => e.getBoundingClientRect().width < innerWidth * .6).length / blocks.length).toFixed(2) : 0, sideways: document.documentElement.scrollWidth * z > innerWidth + 1 }; };
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] }); const out = {}; let next = 0;
try { await Promise.all(Array.from({ length: Math.min(4, args.length) }, async () => { for (;;) { const i = next++; if (i >= args.length) return; const file = path.resolve(args[i]), read = {};
  for (const w of [390, ...ask, 1440]) { const ctx = await browser.newContext({ viewport: { width: w, height: w < 600 ? 844 : 900 }, reducedMotion: 'reduce' }); const p = await ctx.newPage();
    try { await p.goto('file://' + file, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(600); read[w] = await p.evaluate(READ); } catch (e) { read[w] = { error: String(e).slice(0, 120) }; } await ctx.close(); }
  const d = read[1440], m = read[390], desk = {};
  for (const w of ask) { const a = read[w]; if (!a || a.error || !d || d.error || !m || m.error) { desk[w] = false; continue; }
    const menu = d.nav > m.nav + 1 ? a.nav >= d.nav - 1 : true; desk[w] = menu && !a.sideways && Math.abs(a.share - d.share) <= Math.abs(a.share - m.share); }
  out[file] = { desk, read }; } })); }
finally { await browser.close().catch(() => {}); }
console.log(JSON.stringify(out));
