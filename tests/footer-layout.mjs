import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'footer-layout-'));
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  for (const name of ['images', 'assets']) fs.copyFileSync(`tests/${name}.sample.json`, path.join(dir, `${name}.json`));
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.ending.cols = [
    ['Address', ['Avenue Example 17']],
    ['Hours', ['Lunes a viernes 08:00–0:00', 'Sábados y domingos 09:30–02:00']],
    ['Contact', ['long.restaurant.contact.address@example.com']],
  ];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  const html = path.join(dir, 'page.html');
  const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  for (const width of [390, 768, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 844 } });
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    const items = await page.locator('#end .fcols li').evaluateAll(elements => elements.map(element => {
      const range = document.createRange(); range.selectNodeContents(element);
      return { text: element.textContent, rects: [...range.getClientRects()].map(rect => ({ left: rect.left, right: rect.right })) };
    }));
    assert.ok(items.length >= 4);
    for (const item of items) {
      assert.ok(item.rects.length, `${width}: missing ${item.text}`);
      for (const rect of item.rects) assert.ok(rect.left >= -1 && rect.right <= width + 1, `${width}: clipped ${item.text}: ${JSON.stringify(rect)}`);
    }
    await page.close();
  }
  console.log('Footer layout checks passed');
} finally {
  await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
