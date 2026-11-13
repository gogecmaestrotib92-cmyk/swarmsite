// covers.mjs — the cover of each design in the chooser: its first screen at 1440×900, photographed once it has come to
// rest (fonts loaded, every entrance animation finished; endless ones — a marquee, words on a path — are left running and
// caught where they stand). A scaled live page in a card was caught half-drawn (owner, 2026-11-12: a cover with the
// background and no headline); a still taken by the worker is the finished page every time.
//
//   node lib/templates/covers.mjs <out dir> <page.html> [more pages …] [--settle 6000]
//   → one JSON line: {covers: {<page name without .html>: <file in out dir>}, failed: {<name>: why}, ms}; exit 0 unless the tool could not run
import fs from 'node:fs'; import path from 'node:path'; import { launch } from '../qa/template_gate.mjs';

export async function covers(browser, pages, out, { settle = 6000 } = {}) {
  fs.mkdirSync(out, { recursive: true });
  const done = {}, failed = {};
  for (const page of pages) {
    const name = path.basename(page).replace(/\.html$/, ''), file = path.join(out, `${name}.jpg`);
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
    try {
      const p = await ctx.newPage();
      await p.goto(/^https?:/.test(page) ? page : 'file://' + path.resolve(page), { waitUntil: 'load', timeout: 30000 });
      await p.waitForTimeout(1200);   // a page that starts its entrance a moment after load has started it by now
      // at rest: the fonts are in and no animation that ends is still running (an endless one never ends and is not waited for)
      await p.waitForFunction(() => document.fonts.status === 'loaded' && document.getAnimations().every(a => { const t = a.effect?.getComputedTiming?.(); return a.playState !== 'running' || !t || t.endTime === Infinity || t.iterations === Infinity; }), null, { timeout: settle, polling: 100 }).catch(() => {});
      await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(400);
      await p.screenshot({ path: file, type: 'jpeg', quality: 82 });
      done[name] = path.basename(file);
    } catch (e) { failed[name] = String(e.message || e).slice(0, 200); }
    finally { await ctx.close(); }
  }
  return { covers: done, failed };
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  const a = process.argv.slice(2), i = a.indexOf('--settle'), settle = i >= 0 ? Number(a.splice(i, 2)[1]) || 6000 : 6000;
  const [out, ...pages] = a;
  if (!out || !pages.length) { console.error('usage: covers.mjs <out dir> <page.html> …'); process.exit(2); }
  const t0 = Date.now(); let b;
  try { b = await launch(); const r = await covers(b, pages, out, { settle }); console.log(JSON.stringify({ ...r, ms: Date.now() - t0 })); }
  catch (e) { console.error(String(e.stack || e)); process.exitCode = 2; }
  finally { if (b) await b.close(); }
}
