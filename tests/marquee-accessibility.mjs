import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'marquee-accessibility-'));
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.beats = [{ id: 'ticker-facts', type: 'facts', h2: 'Facts', facts: [['First', 'Detail'], ['Zero', 0], ['Third', 'Another']], ui: { move: 'marquee' } }];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), '[]');
  const html = path.join(dir, 'page.html');
  const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const mode of ['normal', 'nomotion', 'reduced']) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 }, reducedMotion: mode === 'reduced' ? 'reduce' : 'no-preference' });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}${mode === 'nomotion' ? '?nomotion=1' : ''}`, { waitUntil: 'domcontentloaded' });
    const section = page.locator('#ticker-facts');
    assert.equal(await section.getAttribute('data-sig'), 'marquee');
    assert.equal(await section.locator('.mq').getAttribute('aria-hidden'), 'true');
    const rows = section.locator('.marquee-static li');
    assert.equal(await rows.count(), 3);
    for (const [index, parts] of [['First', 'Detail'], ['Zero', '0'], ['Third', 'Another']].entries()) {
      const row = rows.nth(index);
      for (const part of parts) assert.ok((await row.innerText()).includes(part));
      if (mode !== 'normal') {
        assert.ok(await row.isVisible(), `${mode}: item ${index + 1} visible`);
        const rect = await row.boundingBox();
        assert.ok(rect && rect.x >= -1 && rect.x + rect.width <= 391, `${mode}: item ${index + 1} fits viewport`);
      }
    }
    assert.equal(await section.locator('.mq').isVisible(), mode === 'normal');
    await page.close();
  }
  console.log('Marquee content remains accessible and reduced-motion items are visible');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
