import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ledger-sticky-scroll-'));
const python = process.env.PYTHON || 'python3';
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.kind = 'place';
  direction.hero.media = 'waiter';
  const items = Array.from({ length: 12 }, (_, i) => [`Dish ${i + 1}`, `${i + 10} €`]);
  direction.beats = [{ id: 'menu', type: 'ledger', h2: 'Our menu', lede: 'Our dishes',
    image: 'long-table', items, ui: { move: 'sticky-product' } }];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), fs.readFileSync('tests/images.sample.json'));
  const output = path.join(dir, 'page.html');
  const render = spawnSync(python, ['lib/render/render_bp.py', dir, 'white-desert', output], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const [width, density, reducedMotion] of [[1440, 1, 'no-preference'], [1440, 1.5, 'no-preference'], [1440, 2, 'no-preference'], [1440, 2.5, 'no-preference'], [1440, 1, 'reduce'], [390, 2, 'no-preference']]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: density, reducedMotion });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(pathToFileURL(output).href, { waitUntil: 'domcontentloaded' });
    const section = page.locator('#menu');
    const offset = await section.evaluate(el => el.offsetTop);
    const measure = async delta => {
      await page.evaluate(y => scrollTo(0, y), offset + delta);
      await page.waitForTimeout(80);
      return section.evaluate(el => {
        const photo = el.querySelector('.ledger-visual'), image = photo.querySelector('img');
        const p = photo.getBoundingClientRect(), rows = el.querySelector('.rows').getBoundingClientRect();
        return { top: p.top, bottom: p.bottom, width: p.width, height: p.height, rowsTop: rows.top,
          position: getComputedStyle(photo).position, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight,
          count: el.querySelectorAll('.rows li').length, docWidth: document.documentElement.scrollWidth };
      });
    };
    const first = await measure(200);
    const second = await measure(350);
    assert.equal(first.count, items.length, `${width}/${density}: all prices`);
    assert.ok(first.docWidth <= width + 1, `${width}/${density}: no horizontal overflow`);
    assert.ok(first.width <= first.naturalWidth * 1.35 + 2, `${width}/${density}: image width stays within its pixels`);  // CSS pixels: a photograph is not halved on retina
    assert.ok(first.height <= first.naturalHeight * 1.35 + 2, `${width}/${density}: image height stays within its pixels`);
    if (width === 1440 && reducedMotion === 'no-preference') {
      assert.equal(first.position, 'sticky');
      assert.ok(Math.abs(first.top - second.top) < 2, 'the photograph stays pinned during real scrolling');
    } else {
      assert.equal(first.position, 'static', `${width}/${reducedMotion}: static photo fallback`);
      assert.ok(second.top < first.top - 100, `${width}/${reducedMotion}: photograph scrolls normally`);
      if (width === 390) assert.ok(first.bottom < first.rowsTop, 'mobile photo precedes the price list');
    }
    await page.close();
  }
  console.log('Ledger photograph pins while prices scroll and falls back cleanly on mobile and reduced motion');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
