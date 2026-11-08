import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'hero-layout-'));
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  for (const name of ['images', 'assets']) fs.copyFileSync(`tests/${name}.sample.json`, path.join(dir, `${name}.json`));
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.hero.h1 = 'Partiendo el <em>bacalao</em> Supercalifragilisticexpialidocious';
  for (const move of ['photo', 'poster', 'split', 'centre']) {
    direction.hero.ui = { move };
    fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
    const html = path.join(dir, `${move}.html`);
    const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    for (const width of [320, 390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      await page.route(/^https?:\/\//, route => route.abort());
      await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
      const problems = await page.locator('#top h1').evaluate(heading => {
        const walker = document.createTreeWalker(heading, NodeFilter.SHOW_TEXT), problems = [];
        while (walker.nextNode()) {
          const range = document.createRange(); range.selectNodeContents(walker.currentNode);
          for (const rect of range.getClientRects()) if (rect.width > 1 && (rect.left < -1 || rect.right > innerWidth + 1)) problems.push(walker.currentNode.textContent);
        }
        return problems;
      });
      assert.deepEqual(problems, [], `${move} hero overflow at ${width}`);
      await page.close();
    }
  }
  console.log('Hero headings fit at mobile and desktop widths with fallback fonts');
} finally {
  await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
