// kit_compare.mjs — does the design kit hold the look of the preview? Measured, in two ways.
//
//   node lib/qa/kit_compare.mjs <unpacked package folder> [--tolerance 0.005] [--shots DIR] [--measure OUT.json]
//   → one JSON line: {ok, whole: {…package_compare's result for design/page.html against index.html…},
//                     sections: [{name, at, height_preview, height_alone, share, holds, why}], alone: {hold, of}, ms}
//   exit 0 when the page put together from the kit looks like the page, 1 when it does not, 2 when the tool could not run.
//
// The package's index.html is the page that was compared with the preview, so it stands in
// for the preview here.
//
//   whole     design/page.html — the page assembled from the kit's files and nothing else — against index.html, screen
//             by screen, by package_compare's own rule. This is what `ok` says: the parts lose nothing. (Every package
//             is held to this before it is delivered: package_compare reads design/page.html beside index.html. This
//             tool is the closer look — section by section — for whoever works on a template or on kit.py.)
//   sections  each design/sections/NN-name.html opened alone, photographed, against the same part cut out of the whole
//             page, at 1440 and 390. A section "holds" when it is the same height and differs in no more than the
//             tolerance of its pixels (read again one pixel up and down before it is said to differ: a part that starts on
//             a fraction of a pixel in the long page is drawn a pixel off). One that does not is reported, not refused: it tells the client (and us) which
//             parts lean on the page round them. A part that is fixed to the window is compared in the window.
//
// --measure writes what the page sets, read in the browser at 1440: the type roles (face, size, weight, line height,
// tracking, how often, an example), the corner radii in use, and the width the content runs to. kit.py puts these in
// DESIGN.md. They are readings of this page, not rules invented for it.
//
// Both pages are opened offline (only files of the package folder), motion at rest, fonts and lazy pictures loaded —
// the same state package_compare photographs.

import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { launch, compare } from './package_compare.mjs'; import { MEASURE } from './kit_measure.mjs';

const WIDTHS = [['d', 1440, 900], ['m', 390, 844]];
const REST = '*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important;caret-color:transparent!important}canvas,video{visibility:hidden!important}';
const TALLEST = 12000;   // a part taller than this is compared over its first 12 000 px
const DIFF = async ({ a, b }) => { const load = async s => { const im = new Image(); im.src = 'data:image/png;base64,' + s; await im.decode(); const c = document.createElement('canvas'); c.width = im.width; c.height = im.height; const g = c.getContext('2d', { willReadFrequently: true }); g.filter = 'blur(1px)'; g.drawImage(im, 0, 0); return g.getImageData(0, 0, c.width, c.height); };
  const A = await load(a), B = await load(b); if (A.width !== B.width || A.height !== B.height) return 1;
  let n = 0; for (let i = 0; i < A.data.length; i += 4) if (Math.abs(A.data[i] - B.data[i]) > 24 || Math.abs(A.data[i + 1] - B.data[i + 1]) > 24 || Math.abs(A.data[i + 2] - B.data[i + 2]) > 24) n++;
  return n / (A.data.length / 4); };
// the parts of a page, by the rule kit.py cuts it with: the children of <body>, and of <main> in their place
const PARTS = () => { const skip = new Set(['SCRIPT', 'STYLE', 'TEMPLATE', 'NOSCRIPT', 'LINK', 'META']); const out = [];
  for (const el of document.body.children) { if (skip.has(el.tagName)) continue;
    if (el.tagName === 'MAIN' && [...el.children].some(k => !skip.has(k.tagName))) { for (const k of el.children) if (!skip.has(k.tagName)) out.push(k); } else out.push(el); }
  return out; };

async function open(browser, url, root, w, h, outside) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, reducedMotion: 'reduce' }); const p = await ctx.newPage();
  await ctx.route('**/*', r => { const u = r.request().url(); if (u.startsWith(root) || u.startsWith('data:') || u.startsWith('blob:')) return r.continue(); if (!outside.includes(u)) outside.push(u); return r.abort(); });
  await p.addInitScript(() => { const raf = window.requestAnimationFrame.bind(window); let n = 0; window.requestAnimationFrame = cb => (++n > 240 ? 0 : raf(cb)); });
  await p.goto(url, { waitUntil: 'load', timeout: 60000 }); await p.addStyleTag({ content: REST });
  await p.evaluate(async () => { try { await document.fonts.ready; } catch {} for (let y = 0; y < document.documentElement.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } scrollTo(0, 0);
    await Promise.all([...document.images].filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 4000); }))); });
  await p.waitForTimeout(900); return { ctx, p };
}

// where each part stands in its document, and whether it is fixed to the window
const rects = p => p.evaluate(`(${PARTS})().map(el => { const r = el.getBoundingClientRect(), cs = getComputedStyle(el); return { x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height), fixed: cs.position === 'fixed' || cs.position === 'sticky' }; })`);
const hideFixed = (p, keep) => p.evaluate(`((keep) => (${PARTS})().forEach((el, i) => { const cs = getComputedStyle(el); if (i !== keep && (cs.position === 'fixed' || cs.position === 'sticky')) el.style.setProperty('visibility', 'hidden', 'important'); else el.style.removeProperty('visibility'); }))(${keep})`);
const shot = async (p, r, vw) => (await p.screenshot({ type: 'png', fullPage: true, clip: { x: 0, y: Math.max(0, r.y), width: vw, height: Math.max(1, Math.min(r.h, TALLEST)) } })).toString('base64');


if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2), opt = k => { const i = args.indexOf(k); return i === -1 ? '' : args.splice(i, 2)[1] || ''; };
  const tolerance = +(opt('--tolerance') || 0.005), shotsDir = opt('--shots'), measureOut = opt('--measure');
  if (args.length !== 1) { console.error('usage: node lib/qa/kit_compare.mjs <unpacked package folder> [--tolerance 0.005] [--shots DIR] [--measure OUT.json]'); process.exit(2); }
  const folder = path.resolve(args[0]), root = 'file://' + folder + '/', index = path.join(folder, 'index.html'), t0 = Date.now();
  let browser, code = 0;
  try {
    const kit = JSON.parse(fs.readFileSync(path.join(folder, 'design', 'kit.json'), 'utf8'));
    browser = await launch(); const dec = await browser.newPage(); const outside = [];
    if (measureOut) { const A = await open(browser, 'file://' + index, root, 1440, 900, outside); fs.writeFileSync(measureOut, JSON.stringify(await A.p.evaluate(MEASURE), null, 1)); await A.ctx.close(); }
    const whole = await compare(browser, index, path.join(folder, 'design', 'page.html'), { tolerance, root: folder, shotsDir: shotsDir ? path.join(shotsDir, 'whole') : '' });
    const sections = [];
    for (const [n, w, h] of WIDTHS) {
      const A = await open(browser, 'file://' + index, root, w, h, outside); const ra = await rects(A.p);
      for (let i = 0; i < kit.sections.length; i++) { const name = kit.sections[i], row = { name, at: n };
        const B = await open(browser, 'file://' + path.join(folder, 'design', 'sections', name + '.html'), root, w, h, outside);
        try { const rb = (await rects(B.p))[0], r = ra[i]; if (!r || !rb) { row.holds = false; row.why = 'the part was not found'; sections.push(row); continue; }
          row.height_preview = r.h; row.height_alone = rb.h; row.fixed = r.fixed;
          await hideFixed(A.p, r.fixed ? i : -1); await hideFixed(B.p, rb.fixed ? 0 : -1);
          const a = await shot(A.p, r.fixed ? { ...r, y: Math.max(0, Math.min(r.y, h - 1)) } : r, w), b = await shot(B.p, rb, w);
          if (shotsDir) { fs.mkdirSync(path.join(shotsDir, 'sections'), { recursive: true }); fs.writeFileSync(path.join(shotsDir, 'sections', `${n}-${name}-page.png`), Buffer.from(a, 'base64')); fs.writeFileSync(path.join(shotsDir, 'sections', `${n}-${name}-alone.png`), Buffer.from(b, 'base64')); }
          if (r.h !== rb.h) { row.share = null; row.holds = false; row.why = `alone it is ${rb.h} px high, in the page ${r.h}`; }
          else { let d = await dec.evaluate(DIFF, { a, b });
            // a part that starts on a fraction of a pixel in the long page is drawn a pixel higher or lower than alone: the same part, read one pixel off
            if (d > tolerance && !r.fixed) for (const dy of [-1, 1]) { const a2 = await shot(A.p, { ...r, y: r.y + dy }, w), d2 = await dec.evaluate(DIFF, { a: a2, b }); if (d2 < d) { d = d2; row.shifted = dy; } }
            row.share = +d.toFixed(5); row.holds = row.share <= tolerance; if (!row.holds) row.why = `${(row.share * 100).toFixed(2)} % of its pixels differ from its place in the page`; }
        } finally { await B.ctx.close(); }
        sections.push(row); }
      await A.ctx.close(); }
    const out = { ok: whole.ok, whole, sections, alone: { hold: sections.filter(s => s.holds).length, of: sections.length }, outside, ms: Date.now() - t0 };
    if (outside.length) { out.ok = false; }
    console.log(JSON.stringify(out)); code = out.ok ? 0 : 1;
  } catch (e) { console.error(String(e && e.stack || e).slice(0, 800)); code = 2; }
  finally { if (browser) await browser.close().catch(() => {}); }
  process.exit(code);
}
