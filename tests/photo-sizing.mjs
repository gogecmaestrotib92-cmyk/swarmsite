import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'photo-sizing-'));
const python = process.env.PYTHON || 'python3';
const fixture = String.raw`
import base64, io, json, os, sys
from PIL import Image
root = sys.argv[1]
direction = json.load(open('tests/direction.sample.json'))
direction['kind'] = 'place'
direction['hero']['media'] = 'hero'
direction['beats'] = [{'id':'salon', 'type':'photo', 'h2':'The Salon', 'lede':'A place to visit', 'image':'salon', 'ui':{'move':'cards'}}]
def image(id, width, value, metadata_width):
    im = Image.new('RGB', (width, 720))
    im.putdata([(value(x, y),) * 3 for y in range(720) for x in range(width)])
    b = io.BytesIO(); im.save(b, 'PNG')
    return {'id':id, 'w':metadata_width, 'h':720, 'data':'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()}
hero = image('hero', 1400, lambda x,y: 200 if (x // 120) % 2 else 70, 1400)
salon = image('salon', 984, lambda x,y: int(x * 200 / 983), 1200)
for name, obj in [('direction.json', direction), ('images.json', [hero, salon])]:
    with open(os.path.join(root, name), 'w') as f: json.dump(obj, f)
`;
let browser;
try {
  const setup = spawnSync(python, ['-c', fixture, dir], { encoding: 'utf8' });
  assert.equal(setup.status, 0, setup.stderr);
  const html = path.join(dir, 'page.html');
  const render = spawnSync(python, ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [390, 1440, 1920]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    const metrics = await page.locator('#salon img').evaluate(img => ({ natural: img.naturalWidth, width: img.getBoundingClientRect().width }));
    assert.equal(metrics.natural, 984);
    assert.ok(metrics.width <= metrics.natural * 1.35 + 1, `${width}: image upscaled to ${metrics.width}px`);
    await page.close();
  }
  console.log('Photo sizing checks passed');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
