import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ledger-price-hierarchy-'));
const python = process.env.PYTHON || 'python3';
const plans = [['Individuals · Free', 'forever'], ['Teams · $12', 'per user/month'],
  ['Organizations · $28', 'per user/month'], ['Enterprise · Custom', 'annual pricing'],
  ['Consulting · €12,50', 'per booking'], ['Special · $7', 0], ['Release · 2026', 'per year'],
  ['Tier · $12 extra', 'details'], ['Offer · Free trials', 'conditions']];
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.kind = 'software';
  direction.beats = [{ id: 'pricing', type: 'ledger', h2: 'Plans and prices', items: plans,
    ui: { move: 'cards', cols: 4 } }];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), fs.readFileSync('tests/images.sample.json'));
  for (const blueprint of ['butter', 'crav']) {
    const output = path.join(dir, `${blueprint}.html`);
    const render = spawnSync(python, ['lib/render/render_bp.py', dir, blueprint, output], { encoding: 'utf8' });
    assert.equal(render.status, 0, render.stderr);
  }
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const blueprint of ['butter', 'crav']) for (const width of [320, 390, 1024, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(path.join(dir, `${blueprint}.html`))}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    const results = await page.locator('#pricing .ledger-card-list li').evaluateAll(nodes => nodes.map(node => {
      const amount = node.querySelector('.ledger-price b'), unit = node.querySelector('.ledger-price small');
      const text = node.querySelector('span'), price = node.querySelector('b');
      const range = document.createRange(); range.selectNodeContents(node);
      return { label: text.textContent, price: price.textContent, unit: unit?.textContent,
        separated: !!amount, amountSize: amount && parseFloat(getComputedStyle(amount).fontSize),
        unitSize: unit && parseFloat(getComputedStyle(unit).fontSize),
        clipped: [...range.getClientRects()].some(rect => rect.left < -1 || rect.right > innerWidth + 1) };
    }));
    assert.equal(results.length, plans.length);
    for (let i = 0; i < plans.length; i++) {
      const row = results[i];
      assert.equal(row.clipped, false, `${width}: item ${i} fits`);
      if (i < 6) {
        const [label, amount] = plans[i][0].split(' · ');
        assert.deepEqual([row.label, row.price, row.unit], [label, amount, String(plans[i][1])], `${width}: all content in item ${i}`);
        assert.ok(row.separated && row.amountSize > row.unitSize, `${width}: amount stands above its unit`);
      } else {
        assert.deepEqual([row.label, row.price], plans[i], `${width}: ambiguous label left unchanged`);
        assert.equal(row.separated, false, `${width}: no false price extraction`);
      }
    }
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.close();
  }
  console.log('Pricing hierarchy extracts only explicit amounts and preserves all other content');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
