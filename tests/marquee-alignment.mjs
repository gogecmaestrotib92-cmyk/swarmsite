import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'marquee-alignment-'));
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.beats = [{ id: 'ticker-facts', type: 'facts', h2: 'Facts', facts: [['First', 'Detail'], ['Zero', 0], ['Third', 'Another']], ui: { move: 'marquee' } }];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), '[]');
  const blueprints = fs.readdirSync('lib/blueprints').filter(n => n.endsWith('.bp.json')).map(n => n.replace('.bp.json', ''));
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const bp of blueprints) {
    const html = path.join(dir, `${bp}.html`);
    const rendered = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, bp, html], { encoding: 'utf8' });
    assert.equal(rendered.status, 0, `${bp}: ${rendered.stderr}`);
    for (const mode of ['nomotion', 'reduced']) {
      const page = await browser.newPage({ viewport: { width: 390, height: 844 }, reducedMotion: mode === 'reduced' ? 'reduce' : 'no-preference' });
      await page.route(/^https?:\/\//, route => route.abort());
      await page.goto(`${pathToFileURL(html)}${mode === 'nomotion' ? '?nomotion=1' : ''}`, { waitUntil: 'domcontentloaded' });
      for (const width of [390, 1440, 1920]) {
        await page.setViewportSize({ width, height: 900 });
        const check = await page.locator('#ticker-facts').evaluate(section => {
          const header = section.querySelector(':scope > .wrap');
          const list = section.querySelector('.marquee-static ul');
          const row = list?.querySelector('li');
          const rect = header?.getBoundingClientRect();
          const item = row?.getBoundingClientRect();
          return { headingEdge: rect && rect.left + parseFloat(getComputedStyle(header).paddingLeft),
            itemEdge: item?.left, rightEdge: item?.right, count: list?.querySelectorAll('li').length,
            visible: row && getComputedStyle(row).visibility === 'visible', scrollWidth: document.documentElement.scrollWidth,
            text: list?.innerText };
        });
        assert.ok(check.visible && check.count === 3, `${bp}/${mode}/${width}: every item is visible`);
        assert.ok(Math.abs(check.headingEdge - check.itemEdge) < 1, `${bp}/${mode}/${width}: ${JSON.stringify(check)}`);
        assert.ok(check.itemEdge >= 0 && check.rightEdge <= width + 1 && check.scrollWidth <= width + 1, `${bp}/${mode}/${width}: no overflow`);
        assert.match(check.text, /First/); assert.match(check.text, /Detail/); assert.match(check.text, /Zero/); assert.match(check.text, /Third/);
      }
      await page.close();
    }
  }
  console.log('Static marquee matches the shared page grid on 12 blueprints, desktop and phone');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
