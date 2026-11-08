import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'statement-layout-'));
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  for (const name of ['images', 'assets']) fs.copyFileSync(`tests/${name}.sample.json`, path.join(dir, `${name}.json`));
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  const quote = direction.beats.find(beat => beat.type === 'quote');
  quote.ui.move = 'cards';
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  for (const blueprint of ['white-desert', 'atelier']) {
    const html = path.join(dir, `${blueprint}.html`);
    const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, blueprint, html], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    for (const width of [1440, 390]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
      const measures = await page.locator('#q').evaluate(section => [...section.querySelectorAll('.wrap, h2, p')].map(el => {
        const rect = el.getBoundingClientRect();
        return { left: rect.left, right: rect.right, clientWidth: el.clientWidth, scrollWidth: el.scrollWidth };
      }));
      assert.ok(measures.length >= 2, `${blueprint} quote is present`);
      for (const measure of measures) {
        assert.ok(measure.left >= -1 && measure.right <= width + 1, `${blueprint} at ${width}: element outside viewport: ${JSON.stringify(measure)}`);
        assert.ok(measure.scrollWidth <= measure.clientWidth + 1, `${blueprint} at ${width}: overflowing text`);
      }
      await page.close();
    }
  }
  console.log('Statement layout checks passed');
} finally {
  await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
