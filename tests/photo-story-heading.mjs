import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'photo-story-heading-'));
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  const images = JSON.parse(fs.readFileSync('tests/images.sample.json'));
  for (const image of images) image.detail = true;
  fs.writeFileSync(path.join(dir, 'images.json'), JSON.stringify(images));
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.beats.unshift({
    id: 'photo-story', type: 'photo', image: 'long-table',
    h2: 'Salón para celebraciones', lede: 'A room for gatherings.',
    cap: ['Thirty guests', 'Call to book'], ui: { move: 'story', h2_px: 96 }
  });
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  const html = path.join(dir, 'page.html');
  const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);

  for (const width of [320, 390, 768, 900, 901, 1024, 1440, 1920]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`);
    const heading = page.locator('#photo-story h2');
    assert.equal(await page.locator('#photo-story.story-photo').count(), 1);
    const result = await heading.evaluate(el => {
      const node = el.firstChild, start = node.textContent.toLowerCase().indexOf('celebraciones');
      const tops = [];
      for (let i = start; i < node.length; i++) {
        const range = document.createRange();
        range.setStart(node, i); range.setEnd(node, i + 1);
        tops.push(Math.round(range.getBoundingClientRect().top));
      }
      return { lines: new Set(tops).size, width: el.getBoundingClientRect().width };
    });
    assert.equal(result.lines, 1, `word split at ${width}px`);
    const overflow = await heading.evaluate(el => {
      el.textContent = 'Supercalifragilisticexpialidocious';
      const range = document.createRange();
      range.selectNodeContents(el);
      return [...range.getClientRects()].some(r => r.left < -1 || r.right > innerWidth + 1);
    });
    assert.equal(overflow, false, `long word overflowed at ${width}px`);
    await page.close();
  }
  console.log('Photo-story headings wrap cleanly at all tested widths');
} finally {
  await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
