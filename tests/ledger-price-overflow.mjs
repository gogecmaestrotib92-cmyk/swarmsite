import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ledger-price-overflow-'));
const python = process.env.PYTHON || 'python3';
const items = [['Premium', '1 000 000 000 €'], ['Basic', '10 €'], ['Extended', '99999999999999999999 €']];
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.kind = 'product';
  direction.beats = [{ id: 'prices', type: 'ledger', h2: 'Prices', items }];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), fs.readFileSync('tests/images.sample.json'));
  const output = path.join(dir, 'page.html');
  const render = spawnSync(python, ['lib/render/render_bp.py', dir, 'crav', output], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [240, 320, 390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(output)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    const rows = await page.locator('#prices .rows li').evaluateAll(nodes => nodes.map(node => {
      const price = node.querySelector('b'), range = document.createRange(); range.selectNodeContents(price);
      const rects = [...range.getClientRects()];
      const bounds = price.getBoundingClientRect(), row = node.getBoundingClientRect();
      return { name: node.querySelector('span').textContent, price: price.textContent,
        clipped: rects.some(rect => rect.left < -1 || rect.right > innerWidth + 1),
        lines: rects.length, right: bounds.right, rowRight: row.right };
    }));
    assert.equal(rows.length, items.length);
    for (let i = 0; i < items.length; i++) {
      assert.deepEqual([rows[i].name, rows[i].price], items[i], `${width}: full item ${i}`);
      assert.equal(rows[i].clipped, false, `${width}: price ${i} is visible`);
    }
    assert.equal(rows[1].lines, 1, `${width}: ordinary price stays on one line`);
    assert.ok(Math.abs(rows[1].right - rows[1].rowRight) <= 1, `${width}: ordinary price remains right aligned`);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.close();
  }
  console.log('Long prices wrap without clipping and ordinary prices stay aligned');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
