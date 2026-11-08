import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'photo-caption-'));
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  for (const name of ['images', 'assets']) fs.copyFileSync(`tests/${name}.sample.json`, path.join(dir, `${name}.json`));
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.beats.unshift({ id: 'photo-test', type: 'photo', image: 'long-table',
    h2: 'Salón y espectáculos Supercalifragilisticexpialidocious',
    lede: 'Un salón reservado con capacidad para 30 personas, para todo tipo de celebraciones y eventos.',
    cap: ['Salón para 30 personas', 'Grupos de más de 20: 910 51 45 04'] });
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  const html = path.join(dir, 'page.html');
  const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);

  for (const width of [320, 390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    const result = await page.locator('#photo-test').evaluate(section => {
      const heading = section.querySelector('.photo-caption h2');
      const elements = section.querySelectorAll('.photo-caption h2, .photo-caption p, .photo-caption li');
      const failures = [];
      for (const el of elements) {
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          const range = document.createRange(); range.selectNodeContents(walker.currentNode);
          for (const rect of range.getClientRects()) if (rect.width > 1 && (rect.left < -1 || rect.right > innerWidth + 1)) failures.push(walker.currentNode.textContent);
        }
      }
      return { heading: heading?.textContent, width: section.getBoundingClientRect().width, failures };
    });
    assert.match(result.heading || '', /Supercalifragilisticexpialidocious/);
    assert.equal(result.width, width);
    assert.deepEqual(result.failures, [], `photo caption overflow at ${width}`);
    await page.close();
  }
  console.log('Photo caption layout holds on desktop and mobile');
} finally {
  await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
