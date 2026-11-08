import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'hero-software-'));
let browser;
try {
  for (const name of ['images', 'assets']) fs.copyFileSync(`tests/${name}.sample.json`, path.join(dir, `${name}.json`));
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.kind = 'software';
  direction.hero.media = 'waiter';
  direction.hero.ui = { move: 'split' };
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  const html = path.join(dir, 'page.html');
  const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'butter', html], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    const image = await page.locator('.hero.split .product-shot img').evaluate(el => {
      const rect = el.getBoundingClientRect();
      return { ratio: rect.width / rect.height, natural: el.naturalWidth / el.naturalHeight, fit: getComputedStyle(el).objectFit };
    });
    assert.equal(image.fit, 'contain');
    assert.ok(Math.abs(image.ratio - image.natural) < 0.02, `${width}: product screenshot should not be cropped or distorted`);
    await page.close();
  }
  direction.kind = 'product';
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  const productHtml = path.join(dir, 'product.html');
  const productRender = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'butter', productHtml], { encoding: 'utf8' });
  assert.equal(productRender.status, 0, productRender.stderr);
  const productPage = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await productPage.route(/^https?:\/\//, route => route.abort());
  await productPage.goto(`${pathToFileURL(productHtml)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
  assert.equal(await productPage.locator('.hero.split .product-shot').count(), 0, 'product photography keeps its existing framing');
  assert.equal(await productPage.locator('.hero.split .shotframe img').evaluate(el => getComputedStyle(el).objectFit), 'cover');
  await productPage.close();
  console.log('Software hero keeps the full product screenshot at mobile and desktop widths');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
