import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'photo-story-portrait-'));
const python = process.env.PYTHON || 'python3';
const fixture = String.raw`
import base64, io, json, os, sys
from PIL import Image, ImageDraw
root = sys.argv[1]
direction = json.load(open('tests/direction.sample.json'))
direction['kind'] = 'place'
direction['hero']['media'] = 'hero'
direction['beats'] = [{'id': 'portrait', 'type': 'photo', 'h2': 'A special room',
    'lede': 'A place for celebrations.', 'image': 'portrait', 'ui': {'move': 'story'}}]
def image(id, width, height):
    im = Image.new('RGB', (width, height), '#79583f')
    draw = ImageDraw.Draw(im)
    draw.rectangle((width // 4, height // 6, width * 3 // 4, height * 5 // 6), fill='#d2b896')
    buf = io.BytesIO(); im.save(buf, 'PNG')
    return {'id': id, 'w': width, 'h': height, 'detail': True,
        'data': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}
for name, value in [('direction.json', direction),
                    ('images.json', [image('hero', 1400, 900), image('portrait', 550, 1000)])]:
    with open(os.path.join(root, name), 'w') as f: json.dump(value, f)
`;

let browser;
try {
  const setup = spawnSync(python, ['-c', fixture, dir], { encoding: 'utf8' });
  assert.equal(setup.status, 0, setup.stderr);
  const html = path.join(dir, 'page.html');
  const render = spawnSync(python, ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const { width, height, dpr } of [{ width: 1440, height: 900, dpr: 1 }, { width: 390, height: 844, dpr: 2 }]) {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: dpr });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    const section = page.locator('#portrait.story-photo');
    assert.equal(await section.count(), 1);
    assert.match(await section.innerText(), /A special room/);
    assert.match(await section.innerText(), /A place for celebrations/);
    const metrics = await section.locator('img').evaluate(img => {
      const rect = img.getBoundingClientRect();
      return { width: rect.width, height: rect.height, naturalWidth: img.naturalWidth,
        naturalHeight: img.naturalHeight, pageWidth: document.documentElement.scrollWidth };
    });
    assert.equal(metrics.naturalWidth, 550);
    assert.equal(metrics.naturalHeight, 1000);
    assert.ok(Math.abs(metrics.width / metrics.height - 0.55) < 0.01, `${width}: portrait was cropped to ${metrics.width}x${metrics.height}`);
    assert.ok(metrics.height <= height * 0.78 + 2, `${width}: portrait exceeds the viewport height limit`);
    assert.ok(metrics.width * dpr <= metrics.naturalWidth * 1.35 + 2, `${width}: portrait is enlarged beyond its resolution limit`);
    assert.equal(metrics.pageWidth, width, `${width}: page overflows horizontally`);
    await page.close();
  }
  console.log('Portrait photo composition checks passed');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
