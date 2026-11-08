import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-metric-cards-'));
const d = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
const metrics = [
  ['Deel · ARR', '$1.5B+', 'From $500M'],
  ['Deel · page loads', '<2s', 'From 12s'],
  ['Deel · time saved', '6,000+', 'hours per week'],
  ['Retell AI · calls', '10M+', 'handled per month'],
  ['Storyblok · demos', '50%', 'more demo efficiency'],
];
const beat = (id, cells, extra = {}) => ({ id, type: 'cells', h2: id, cells, ui: { move: 'cards', cols: 1, lead: '' }, ...extra });
const long = metrics.map(x => [...x]); long[0][2] = 'One two three four five six seven eight nine ten eleven twelve thirteen';
const nonnumeric = metrics.map(x => [...x]); nonnumeric[0][1] = 'Enterprise';
d.beats = [beat('metrics', metrics), beat('long', long), beat('nonnumeric', nonnumeric),
  beat('image', metrics, { image: 'basta-table', ui: { move: 'cards', cols: 1 } }),
  beat('lead', metrics, { ui: { move: 'cards', cols: 1, lead: 'long-table' } }),
  { id: 'features', type: 'features', h2: 'features', features: metrics.map(x => ({ title: x[0], body: x[2] })), ui: { move: 'cards', cols: 1 } }];
fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(d));
fs.copyFileSync('tests/images.sample.json', path.join(dir, 'images.json'));
fs.copyFileSync('tests/inventory.sample.json', path.join(dir, 'inventory.json'));
let browser;
try {
  browser = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  const bps = fs.readdirSync('lib/blueprints').filter(name => name.endsWith('.bp.json'));
  for (const bp of bps) {
    const html = path.join(dir, 'page.html');
    const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, bp.replace('.bp.json', ''), html], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    for (const width of [390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
      await page.goto(pathToFileURL(html).href + '?nomotion=1');
      for (const id of ['metrics', 'long', 'nonnumeric', 'image', 'lead', 'features']) {
        const grid = page.locator(`#${id} .grid`);
        assert.equal(await grid.count(), 1, `${bp} ${id} renders cards`);
        const columns = await grid.evaluate(el => getComputedStyle(el).gridTemplateColumns.split(' ').length);
        assert.equal(columns, width > 900 && id === 'metrics' ? 2 : 1, `${bp} ${id} at ${width}`);
      }
      const cards = await page.locator('#metrics .card').allTextContents();
      assert.equal(await page.locator('#image img').count(), 1, `${bp} image remains visible`);
      assert.equal(await page.locator('#lead img').count(), 1, `${bp} lead remains visible`);
      assert.equal(cards.length, metrics.length);
      for (let i = 0; i < metrics.length; i++) for (const part of metrics[i]) assert.ok(cards[i].includes(part), `${bp} retains ${part}`);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width, `${bp} overflow at ${width}`);
      await page.close();
    }
  }
  console.log('Compact metrics use two desktop columns; narrative, images and mobile preserve one across 12 blueprints');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
