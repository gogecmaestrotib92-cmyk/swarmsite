// package_compare.mjs — does the downloaded package look like the preview? Screen by screen, measured.
//
//   node lib/qa/package_compare.mjs <preview.html | http://address> <unpacked/index.html> [--tolerance 0.005] [--shots DIR]
//   → one JSON line: {ok, why: [...], widths: [{at, height_preview, height_package, screens, worst, differing: [...]}], outside: [...], ms}
//   exit 0 when the package may be delivered, 1 when it is refused, 2 when the tool could not run.
//
//   node lib/qa/package_compare.mjs <preview 1> <package 1> <preview 2> <package 2> … [--jobs 3]
//   → the designs of one job in ONE browser, up to `jobs` side by side: one JSON line for each pair, in the order given
//     (a pair that could not be compared is {ok: false, why: [...]}: a refusal of that pair, not of the others);
//     exit 0 when every package may be delivered, 1 when any is refused. With --shots, pair n writes to DIR/n.
//
// The two widths of a pair are read side by side, and a screen of the preview is photographed while the same screen of
// the package is: each page stands in its own context, so what one shows does not depend on the other. A job's three
// packages used to be three browsers one after another, most of that time spent waiting for pages to come to rest
// (measured 2026-11-18: 80 s of wall for 14 s of processor on one job).
//
// The package is opened OFFLINE: every request that is not a file of the package is refused and written down
// (`outside`) — a package that asks the network for anything is refused, whatever it looks like. Both pages are
// opened at 1440 and 390 with motion at rest (prefers-reduced-motion, animations and transitions off, script-driven
// motion held), fonts loaded, lazy pictures loaded, and photographed one screen at a time down the page. A screen
// differs by the share of its pixels whose colour is more than 24/255 away, both pictures blurred by one pixel first. Refused when the pages are not the same
// height, or any screen differs by more than the tolerance (default 0.5 % of its pixels).
// What moves by itself is not compared: <canvas> and <video> are covered with one flat tone in both pages.

import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';

const addr = t => /^https?:\/\//.test(t) ? t : 'file://' + path.resolve(t);
const WIDTHS = [['d', 1440, 900], ['m', 390, 844]];
const REST = '*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important;caret-color:transparent!important}canvas,video{visibility:hidden!important}';
// Both pictures are blurred by one pixel before they are compared. The browser smooths the rim of a letter a hair differently
// from one run to the next: the same package against the same preview gave 0 % nineteen times in twenty and 0.63 % of a phone
// screen once — every counted pixel on the rim of a glyph, nothing an eye can see (measured 2026-11-15). Blurred, that state reads
// 0.01 %; what is a difference still reads as one (a screen moved by one pixel 2.9 %, one line of text replaced 0.33 %).
const DIFF = async ({ a, b }) => { const load = async s => { const im = new Image(); im.src = 'data:image/png;base64,' + s; await im.decode(); const c = document.createElement('canvas'); c.width = im.width; c.height = im.height; const g = c.getContext('2d', { willReadFrequently: true }); g.filter = 'blur(1px)'; g.drawImage(im, 0, 0); return g.getImageData(0, 0, im.width, im.height); };
  const A = await load(a), B = await load(b); if (A.width !== B.width || A.height !== B.height) return 1;
  let n = 0; for (let i = 0; i < A.data.length; i += 4) if (Math.abs(A.data[i] - B.data[i]) > 24 || Math.abs(A.data[i + 1] - B.data[i + 1]) > 24 || Math.abs(A.data[i + 2] - B.data[i + 2]) > 24) n++;
  return n / (A.data.length / 4); };

export async function launch() {
  const chromePath = process.env.CHROME_PATH || '/usr/bin/google-chrome';
  return chromium.launch({ executablePath: chromePath && fs.existsSync(chromePath) ? chromePath : undefined, args: ['--no-sandbox'] });
}

// one preview against one unpacked package, in a browser that is already open
export async function compare(browser, previewArg, packArg, { tolerance = 0.005, shotsDir = '' } = {}) {
  const t0 = Date.now(), preview = addr(previewArg), pack = addr(packArg), packRoot = 'file://' + path.dirname(path.resolve(packArg)) + '/';
  const out = { ok: true, why: [], widths: [], outside: [], tolerance };
  if (shotsDir) fs.mkdirSync(shotsDir, { recursive: true });
  const rows = await Promise.all(WIDTHS.map(async ([n, w, h]) => {
    const why = [], made = [], dec = await browser.newPage();
    const open = async (url, offline) => { const ctx = await browser.newContext({ viewport: { width: w, height: h }, reducedMotion: 'reduce' }); made.push(ctx); const p = await ctx.newPage();
      if (offline) await ctx.route('**/*', r => { const u = r.request().url(); if (u.startsWith(packRoot) || u.startsWith('data:') || u.startsWith('blob:')) return r.continue(); if (!out.outside.includes(u)) out.outside.push(u); return r.abort(); });
      await p.addInitScript(() => { const raf = window.requestAnimationFrame.bind(window); let n = 0; window.requestAnimationFrame = cb => (++n > 240 ? 0 : raf(cb)); });   // script-driven motion comes to rest
      await p.goto(url, { waitUntil: 'load', timeout: 60000 }); await p.addStyleTag({ content: REST });
      await p.evaluate(async () => { try { await document.fonts.ready; } catch {} for (let y = 0; y < document.documentElement.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } scrollTo(0, 0);
        await Promise.all([...document.images].filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 4000); }))); });
      await p.waitForTimeout(1200); return { ctx, p }; };
    try {
      const [A, B] = await Promise.all([open(preview, false), open(pack, true)]);
      const size = p => p.evaluate(() => ({ H: document.documentElement.scrollHeight, fonts: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, '') + ' ' + f.weight).sort(), broken: [...document.images].filter(i => i.complete && !i.naturalWidth && i.getAttribute('src')).map(i => i.getAttribute('src').slice(-50)) }));
      const sa = await size(A.p), sb = await size(B.p);
      const row = { at: n, height_preview: sa.H, height_package: sb.H, screens: 0, worst: 0, differing: [], fonts_preview: [...new Set(sa.fonts)], fonts_package: [...new Set(sb.fonts)], pictures_missing_in_package: sb.broken };
      if (sa.H !== sb.H) why.push(`${n}: the package is ${sb.H} px high, the preview ${sa.H}`);
      if (sb.broken.length) why.push(`${n}: ${sb.broken.length} picture(s) of the package did not load: ${sb.broken.slice(0, 3).join(', ')}`);
      if (JSON.stringify(row.fonts_preview) !== JSON.stringify(row.fonts_package)) why.push(`${n}: the faces loaded differ — preview [${row.fonts_preview.join(', ')}], package [${row.fonts_package.join(', ')}]`);
      for (let y = 0, i = 0; y < Math.min(sa.H, sb.H) && i < 60; y += h, i++) {
        const shot = async (p, tag) => { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(350); const buf = await p.screenshot({ type: 'png' }); if (shotsDir) fs.writeFileSync(path.join(shotsDir, `${n}-${String(i).padStart(2, '0')}-${tag}.png`), buf); return buf.toString('base64'); };
        const [a, b] = await Promise.all([shot(A.p, 'preview'), shot(B.p, 'package')]);
        const d = await dec.evaluate(DIFF, { a, b }); row.screens++;
        if (d > row.worst) row.worst = +d.toFixed(5);
        if (d > tolerance) row.differing.push({ screen: i, y, share: +d.toFixed(5) });
      }
      if (row.differing.length) why.push(`${n}: ${row.differing.length} of ${row.screens} screens differ by more than ${(tolerance * 100).toFixed(2)} % of their pixels (worst ${(row.worst * 100).toFixed(2)} %, screen ${row.differing.sort((a, b) => b.share - a.share)[0].screen})`);
      return { row, why };
    } finally { for (const c of made) await c.close().catch(() => {}); await dec.close().catch(() => {}); }
  }));
  for (const r of rows) { out.widths.push(r.row); out.why.push(...r.why); }   // in the order of the widths, whichever finished first
  if (out.outside.length) out.why.push(`the package asks for ${out.outside.length} thing(s) outside itself: ${out.outside.slice(0, 3).join(', ')}`);
  out.ok = out.why.length === 0; out.ms = Date.now() - t0;
  return out;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2), opt = k => { const i = args.indexOf(k); return i === -1 ? '' : args.splice(i, 2)[1] || ''; };
  const tolerance = +(opt('--tolerance') || 0.005), shotsDir = opt('--shots'), jobs = Math.max(1, +(opt('--jobs') || 3));
  if (!args.length || args.length % 2) { console.error('usage: node lib/qa/package_compare.mjs <preview.html | http://address> <unpacked/index.html> [more pairs …] [--tolerance 0.005] [--shots DIR] [--jobs 3]'); process.exit(2); }
  const pairs = []; for (let i = 0; i < args.length; i += 2) pairs.push([args[i], args[i + 1]]);
  let browser, code = 0;
  try {
    browser = await launch();
    const results = new Array(pairs.length); let next = 0;
    await Promise.all(Array.from({ length: Math.min(jobs, pairs.length) }, async () => { for (;;) { const i = next++; if (i >= pairs.length) return;
      try { results[i] = await compare(browser, pairs[i][0], pairs[i][1], { tolerance, shotsDir: shotsDir && pairs.length > 1 ? path.join(shotsDir, String(i + 1)) : shotsDir }); }
      catch (e) { if (pairs.length === 1) throw e; results[i] = { ok: false, why: ['the comparison could not be made: ' + String(e).slice(0, 300)] }; } } }));
    for (const r of results) { if (!r.ok) code = 1; console.log(JSON.stringify(r)); }
  } catch (e) { console.error(String(e).slice(0, 500)); code = 2; }
  finally { if (browser) await browser.close().catch(() => {}); }
  process.exit(code);
}
