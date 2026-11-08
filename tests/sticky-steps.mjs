import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sticky-steps-'));
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.kind = 'software';
  const steps = ['Send one link with your free hours.', 'Let them pick the time.', "It lands in everyone's calendar, no reply needed."];
  direction.beats = [
    { id: 'steps', type: 'steps', h2: 'One link, three steps', steps, image: 'long-table', ui: { move: 'sticky-product' } },
    { id: 'features', type: 'features', h2: 'Features', features: [
      { title: 'Booking pages', body: 'Share a link.' }, { title: 'Workflows', body: 'Send reminders.' },
    ], image: 'basta-table', ui: { move: 'sticky-product' } },
  ];
  const images = JSON.parse(fs.readFileSync('tests/images.sample.json'));
  for (const image of images) image.detail = true;
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), JSON.stringify(images));
  const html = path.join(dir, 'page.html');
  const rendered = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'butter', html], { encoding: 'utf8' });
  assert.equal(rendered.status, 0, rendered.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    const rows = page.locator('#steps .sp-row');
    assert.equal(await rows.count(), steps.length, `sticky step rows at ${width}px`);
    const images = await page.locator('#steps .sp-stage img').evaluateAll(els => els.map(el => ({ fit: getComputedStyle(el).objectFit, scale: el.style.transform })));
    assert.ok(images.length && images.every(image => image.fit === 'contain' && image.scale === 'scale(1)'), `${width}: product screenshots must stay fully visible`);
    for (let i = 0; i < steps.length; i++) {
      const row = rows.nth(i), number = String(i + 1).padStart(2, '0');
      assert.equal(await row.locator('.lab').innerText(), number);
      assert.equal(await row.locator('h3').innerText(), steps[i], `step heading at ${width}px`);
      assert.equal(await row.getByText(number, { exact: true }).count(), 1, `duplicate step number at ${width}px`);
      assert.equal(await row.getByText(steps[i], { exact: true }).count(), 1, `duplicate step text at ${width}px`);
    }
    const feature = page.locator('#features .sp-row').first();
    assert.equal(await feature.locator('h3').innerText(), 'Booking pages');
    assert.equal(await feature.locator('p').innerText(), 'Share a link.');
    await page.close();
  }
  console.log('Sticky steps have one number and an accessible content heading');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
