// The device library's demo page: no script error, nothing left hidden after scrolling through it, no layout break at five widths.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { spawnSync } from 'node:child_process'; import { fileURLToPath } from 'node:url'; import { chromium } from 'playwright';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'); const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'devices-')), 'demo.html');
const built = spawnSync(process.env.PYTHON || 'python3', [path.join(root, 'lib/devices/registry.py'), 'demo', file], { encoding: 'utf8' }); assert.equal(built.status, 0, built.stderr);
const lay = spawnSync('node', [path.join(root, 'lib/qa/layout.mjs'), file], { encoding: 'utf8', env: { ...process.env, LIVETEST: '1' } }); assert.equal(lay.status, 0, lay.stderr);
assert.deepEqual(JSON.parse(lay.stdout.trim().split('\n').pop()).breaks, [], 'the demo has no layout break');
const b = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
for (const [width, motion] of [[1440, 'no-preference'], [390, 'no-preference'], [1440, 'reduce']]) {
  const p = await b.newPage({ viewport: { width, height: 900 }, reducedMotion: motion }); const errors = []; p.on('pageerror', e => errors.push(String(e)));
  await p.route(/^https?:\/\//, r => r.abort()); await p.goto('file://' + file); const H = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y <= H; y += 600) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(50); }
  await p.waitForTimeout(500);
  const hidden = await p.evaluate(() => [...document.querySelectorAll('h1,h2,p,li,a,img')].filter(e => e.getBoundingClientRect().width > 2 && parseFloat(getComputedStyle(e).opacity) < .05 && !e.classList.contains('dv-peek-img') && !e.closest('.dv-menu:not(.is-open)'))   /* a closed menu is closed, not lost */.map(e => (e.textContent || '').slice(0, 30)));
  assert.deepEqual(errors, [], `${width}/${motion}: script errors`); assert.deepEqual(hidden, [], `${width}/${motion}: left hidden`);
  assert.equal(await p.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false, `${width}: sideways scroll`); await p.close(); }
{ const p = await b.newPage({ viewport: { width: 390, height: 800 } }); await p.route(/^https?:\/\//, r => r.abort()); await p.goto('file://' + file);
  await p.click('.dv-menu-btn'); await p.waitForTimeout(700); assert.equal(await p.locator('.dv-menu a').first().isVisible(), true, 'the menu opens and its links can be seen');
  await p.keyboard.press('Escape'); await p.waitForTimeout(400); assert.equal(await p.getAttribute('.dv-menu-btn', 'aria-expanded'), 'false', 'Escape closes the menu');
  await p.click('.dv-slides [data-step="1"]'); assert.match(await p.textContent('.dv-slides-n'), /^2 \/ 3$/, 'the slides step forward'); await p.close(); }
await b.close(); console.log('Device library: the demo runs clean at desktop, phone and reduced motion');
