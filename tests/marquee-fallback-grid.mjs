import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'marquee-fallback-grid-'));
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  const features = Array.from({ length: 6 }, (_, i) => ({ title: `Capability ${i + 1}`, body: `Description for capability ${i + 1}` }));
  const cells = Array.from({ length: 6 }, (_, i) => [`Metric ${i + 1}`, `${i + 1}%`, `A full explanation that must remain visible and has enough words to exceed twelve terms`]);
  direction.beats = [
    { id: 'features-ticker', type: 'features', h2: 'Features', features, ui: { move: 'marquee', cols: 1 } },
    { id: 'metrics-ticker', type: 'cells', h2: 'Metrics', cells, ui: { move: 'marquee', cols: 1 } },
    { id: 'intentional-single', type: 'features', h2: 'Editorial list', features, ui: { move: 'cards', cols: 1 } },
  ];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), '[]');
  const html = path.join(dir, 'page.html');
  const render = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'butter', html], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [1440, 390]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    for (const id of ['features-ticker', 'metrics-ticker', 'intentional-single']) {
      // a features beat with no picture of its own is set as the index (one hairline row per item); metric cells stay a card grid
      const section = page.locator(`#${id}`), cards = section.locator(id === 'metrics-ticker' ? '.grid > .card' : '.index-list > .index-row');
      assert.equal(await cards.count(), 6, `${id}: all items survived fallback`);
      const positions = await cards.evaluateAll(nodes => nodes.map(node => Math.round(node.getBoundingClientRect().x)));
      const expectedColumns = width === 390 || id !== 'metrics-ticker' ? 1 : 3;
      assert.equal(new Set(positions).size, expectedColumns, `${id} at ${width}px: correct grid columns`);
      for (const card of await cards.all()) {
        assert.ok(await card.isVisible());
        const box = await card.boundingBox();
        assert.ok(box && box.x >= -1 && box.x + box.width <= width + 1, `${id}: card fits viewport`);
      }
      const text = await section.innerText();
      for (const [i, item] of (id === 'metrics-ticker' ? cells : features).entries()) {
        const expected = id === 'metrics-ticker' ? [item[0], item[1], item[2]] : [item.title, item.body];
        for (const value of expected) assert.ok(text.includes(value), `${id}: item ${i + 1} retains ${value}`);
      }
    }
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width);
    await page.close();
  }
  console.log('Ticker fallbacks retain every item: metric cards in a responsive grid, picture-less features as the index');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
