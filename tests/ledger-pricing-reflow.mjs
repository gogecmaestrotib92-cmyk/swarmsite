import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ledger-pricing-'));
const python = process.env.PYTHON || 'python3';
const plans = [['Individuals', 'Free forever'], ['Teams', '$12 per user/month'],
  ['Organizations', '$28 per user/month'], ['Enterprise', 'Custom']];
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.kind = 'software';
  direction.beats = [{ id: 'pricing', type: 'ledger', h2: 'Plans and prices',
    lede: 'Billed yearly.', items: plans, ui: { move: 'cards', cols: 4 },
    cta: 'Start scheduling', cta_href: 'https://example.test/signup',
    cta2: 'Talk to sales', cta2_href: 'https://example.test/sales' }];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), fs.readFileSync('tests/images.sample.json'));
  fs.writeFileSync(path.join(dir, 'inventory.json'), JSON.stringify({ actions: [
    { text: 'Start scheduling', href: 'https://example.test/signup' },
    { text: 'Talk to sales', href: 'https://example.test/sales' },
  ] }));
  const output = path.join(dir, 'page.html');
  const render = spawnSync(python, ['lib/render/render_bp.py', dir, 'butter', output], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const [width, expectedColumns] of [[320, 1], [390, 1], [600, 1], [768, 2], [900, 2], [1024, 2], [1200, 4], [1440, 4], [1920, 4]]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(output)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    const pricing = page.locator('#pricing');
    const entries = pricing.locator('.ledger-card-list li');
    assert.equal(await entries.count(), plans.length);
    for (let i = 0; i < plans.length; i++) {
      assert.equal((await entries.nth(i).locator('span').textContent()).trim(), plans[i][0], `${width}: plan order`);
      assert.equal((await entries.nth(i).locator('b').textContent()).trim(), plans[i][1], `${width}: full price`);
    }
    const result = await pricing.evaluate(el => {
      const grid = el.querySelector('.ledger-card-list');
      const priceUnits = [...grid.querySelectorAll('li b')].filter(node => node.textContent.includes('user/month'));
      return { columns: getComputedStyle(grid).gridTemplateColumns.split(' ').length,
        units: priceUnits.map(node => { const range = document.createRange(), text = node.firstChild;
          const start = text.textContent.indexOf('user/month'); range.setStart(text, start); range.setEnd(text, start + 10);
          return range.getClientRects().length; }),
        docWidth: document.documentElement.scrollWidth, ctas: el.querySelectorAll('.ctas a').length };
    });
    assert.equal(result.columns, expectedColumns, `${width}: responsive card columns`);
    assert.deepEqual(result.units, [1, 1], `${width}: billing units stay intact`);
    assert.ok(result.docWidth <= width + 1, `${width}: no horizontal overflow`);
    assert.equal(result.ctas, 2, `${width}: both actions`);
    const longWord = await entries.first().locator('b').evaluate(node => {
      node.textContent = 'W'.repeat(140);
      const range = document.createRange(); range.selectNodeContents(node);
      return [...range.getClientRects()].some(rect => rect.left < -1 || rect.right > innerWidth + 1);
    });
    assert.equal(longWord, false, `${width}: unusually long price is not clipped`);
    await page.close();
  }
  console.log('Pricing cards preserve plan order and reflow cleanly across screen sizes');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
