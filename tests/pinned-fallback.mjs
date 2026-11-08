import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pinned-fallback-'));
let browser;
try {
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  const generator = await browser.newPage();
  const images = await generator.evaluate(() => {
    function image(id, shot) {
      const canvas = document.createElement('canvas'); canvas.width = 1200; canvas.height = 300;
      const ctx = canvas.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, 1200, 300);
      ctx.fillStyle = '#e00'; ctx.fillRect(0, 0, 20, 300); ctx.fillStyle = '#00e'; ctx.fillRect(1180, 0, 20, 300);
      ctx.fillStyle = '#333'; ctx.font = '40px sans-serif'; ctx.fillText(id, 40, 70);
      return { id, w: 1200, h: 300, shot, detail: true, data: canvas.toDataURL('image/png') };
    }
    return [image('hero', false), image('assigned-ui', true), image('unrelated-ui', true)];
  });
  await generator.close();
  const d = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  d.kind = 'software'; d.hero.media = 'hero';
  const steps = ['First useful step', 'Second useful step', 'Third useful step'];
  d.beats = [
    { id: 'assigned', type: 'steps', h2: 'Assigned', steps, image: 'assigned-ui', note: 'A source note.', cta: 'Continue', cta_href: 'https://example.com/continue', ui: { move: 'pinned-sequence', cols: 1, lead: '' } },
    { id: 'unavailable', type: 'steps', h2: 'Unavailable', steps, image: 'missing', note: 'Another source note.', ui: { move: 'pinned-sequence', cols: 1, lead: '' } },
    { id: 'none', type: 'steps', h2: 'No image', steps, note: 'A third note.', ui: { move: 'pinned-sequence', cols: 1, lead: '' } },
  ];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(d));
  fs.writeFileSync(path.join(dir, 'images.json'), JSON.stringify(images));
  fs.writeFileSync(path.join(dir, 'inventory.json'), JSON.stringify({ actions: [{ text: 'Continue', href: 'https://example.com/continue' }] }));
  const html = path.join(dir, 'page.html');
  const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'butter', html], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  for (const width of [1440, 390]) for (const mode of ['no-preference', 'reduce']) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: mode });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}${mode === 'reduce' ? '?nomotion=1' : ''}`, { waitUntil: 'domcontentloaded' });
    for (const id of ['assigned', 'unavailable', 'none']) {
      const section = page.locator(`#${id}`), cards = section.locator('.grid > .card');
      assert.equal(await cards.count(), 3, `${id}: every step survives`);
      const positions = await cards.evaluateAll(nodes => nodes.map(el => Math.round(el.getBoundingClientRect().x)));
      assert.equal(new Set(positions).size, width === 1440 ? 3 : 1, `${id}: responsive fallback columns`);
      for (const text of steps) assert.ok((await section.innerText()).includes(text));
      assert.ok(await section.locator('.section-note').isVisible());
      assert.equal(await section.locator('figure.lead').count(), id === 'assigned' ? 1 : 0, `${id}: only the assigned and available image is shown`);
    }
    const figure = page.locator('#assigned figure.lead-shot');
    const image = await figure.locator('img').evaluate(el => {
      const r = el.getBoundingClientRect(), f = el.parentElement.getBoundingClientRect();
      return { width: r.width, height: r.height, naturalWidth: el.naturalWidth, naturalHeight: el.naturalHeight,
        inside: r.left >= f.left && r.right <= f.right && r.top >= f.top && r.bottom <= f.bottom, fit: getComputedStyle(el).objectFit };
    });
    assert.ok(image.inside && image.fit === 'contain', 'the entire assigned screenshot is shown');
    assert.ok(image.width <= image.naturalWidth && image.height <= image.naturalHeight, 'the screenshot is never upscaled');
    assert.ok(Math.abs(image.width / image.height - image.naturalWidth / image.naturalHeight) < .01, 'screenshot aspect ratio is preserved');
    const action = page.locator('#assigned').getByRole('link', { name: 'Continue' });
    assert.equal(await action.getAttribute('href'), 'https://example.com/continue');
    await action.click({ trial: true });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width);
    await page.close();
  }
  console.log('Pinned fallback retains responsive steps, source notes, actions and only the assigned image');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
