import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'facts-cards-layout-'));
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.kind = 'place';
  const facts = [
    ['08:00', 'apertura de lunes a viernes'],
    ['02:00', 'cierre sábados y domingos'],
    ['30', 'personas en el salón reservado'],
  ];
  direction.beats = [{ id: 'horario', type: 'facts', h2: 'Horario', facts, ui: { move: 'cards', lead: '' } }];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), '[]');
  const html = path.join(dir, 'page.html');
  const render = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'tengile', html], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });

  for (const width of [390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    const cards = page.locator('#horario .card');
    assert.equal(await cards.count(), facts.length, `fact cards at ${width}px`);
    for (let i = 0; i < facts.length; i++) {
      const card = cards.nth(i);
      const value = card.getByText(facts[i][0], { exact: true });
      const label = card.getByText(facts[i][1], { exact: true });
      assert.equal(await value.count(), 1, `value ${facts[i][0]} at ${width}px`);
      assert.equal(await label.count(), 1, `label ${facts[i][1]} at ${width}px`);
      assert.equal(await card.locator('.lab').count(), 0, `no fabricated ordinal at ${width}px`);
      const valueSize = await value.evaluate(el => parseFloat(getComputedStyle(el).fontSize));
      const labelSize = await label.evaluate(el => parseFloat(getComputedStyle(el).fontSize));
      assert.ok(valueSize >= 36 && valueSize >= labelSize * 1.5,
        `${facts[i][0]} should be visually prominent at ${width}px (value ${valueSize}px, label ${labelSize}px)`);
      const overflowing = await card.evaluate(el => {
        const bounds = el.getBoundingClientRect();
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        const problems = [];
        while (walker.nextNode()) {
          const range = document.createRange();
          range.selectNodeContents(walker.currentNode);
          for (const rect of range.getClientRects()) {
            if (rect.width > 1 && (rect.left < bounds.left - 1 || rect.right > bounds.right + 1 || rect.left < -1 || rect.right > innerWidth + 1)) {
              problems.push(walker.currentNode.textContent);
            }
          }
        }
        return problems;
      });
      assert.deepEqual(overflowing, [], `fact text overflow at ${width}px`);
    }
    await page.close();
  }
  console.log('Coimbra facts remain legible and fit on mobile and desktop');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
