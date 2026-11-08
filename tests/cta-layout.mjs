import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'cta-layout-'));
const python = process.env.PYTHON || 'python3';
const fixture = String.raw`
import base64, io, json, os, sys
from PIL import Image
root = sys.argv[1]
direction = json.load(open('tests/direction.sample.json'))
direction['kind'] = 'place'
direction['hero']['media'] = 'hero'
form = next(b for b in direction['beats'] if b['type'] == 'form')
form.update({'id': 'contact', 'h2': 'Reserve a table', 'cta': 'Book', 'cta_href': 'https://example.com/book', 'alt': ['Phone 555 0100', 'contact@example.com']})
direction['beats'] = [form]
inventory = {'url': 'https://example.com/', 'actions': [{'text': 'Book', 'href': 'https://example.com/book'}]}
def image(id, pixels, bg, lum):
    im = Image.new('RGB', (64, 64))
    im.putdata([(pixels(x, y),) * 3 for y in range(64) for x in range(64)])
    im = im.resize((1400, 900))
    buf = io.BytesIO(); im.save(buf, 'PNG')
    return {'id': id, 'w': 1400, 'h': 900, 'bg': bg, 'lum': lum, 'data': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}
hero = image('hero', lambda x, y: 220 if x % 8 < 4 else 130, False, 175)
texture = image('texture', lambda x, y: 10 if (x // 8) % 2 == 0 else 20, True, 15)
dark_photo = image('dark-photo', lambda x, y: int(x * 60 / 63), True, 30)
free_photo = image('free-photo', lambda x, y: 230 if (x // 8) % 2 == 0 else 70, False, 150)
duplicate = {**dark_photo, 'id': 'duplicate', 'bg': False}
for name, images in [('texture-only', [hero, texture]), ('photo-and-texture', [hero, texture, dark_photo]), ('free-and-reserved', [hero, free_photo, dark_photo]), ('duplicate-and-reserved', [hero, duplicate, dark_photo])]:
    folder = os.path.join(root, name); os.mkdir(folder)
    form['image'] = 'texture' if name == 'texture-only' else 'dark-photo'
    for filename, obj in [('direction.json', direction), ('images.json', images), ('inventory.json', inventory)]:
        with open(os.path.join(folder, filename), 'w') as f: json.dump(obj, f)
`;
let browser;
try {
  const setup = spawnSync(python, ['-c', fixture, dir], { encoding: 'utf8' });
  assert.equal(setup.status, 0, setup.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const name of ['texture-only', 'photo-and-texture', 'free-and-reserved', 'duplicate-and-reserved']) {
    const folder = path.join(dir, name);
    const html = path.join(folder, 'page.html');
    const render = spawnSync(python, ['lib/render/render_bp.py', folder, 'white-desert', html], { encoding: 'utf8' });
    assert.equal(render.status, 0, render.stderr);
    const images = JSON.parse(fs.readFileSync(path.join(folder, 'images.json')));
    for (const width of [390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 844 } });
      await page.route(/^https?:\/\//, route => route.abort());
      await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
      const section = page.locator('#contact');
      if (name === 'texture-only') {
        assert.equal(await section.locator('.ov-bg img').count(), 0, 'texture is not used as a CTA photograph');
      } else {
        assert.ok((await section.locator('.ov-bg img').getAttribute('src')) === images.find(i => i.id === 'dark-photo').data, 'dark photograph remains eligible');
        if (name === 'duplicate-and-reserved') assert.equal(await page.locator('section.photo:not(.hero) img').count(), 0, 'a duplicate of a reserved photo is not used as filler');
        if (name === 'free-and-reserved') {
          assert.equal(await page.locator('section.photo:not(.hero) img').count(), 0, 'a free photo does not create an unrequested filler section');
        }
        const layout = await section.evaluate(el => {
          const title = el.querySelector('.h2').getBoundingClientRect();
          const button = (el.querySelector('.ctas') || el.querySelector('.form')).getBoundingClientRect(); // a form beat with a real form page renders the form itself
          const labels = [...el.querySelectorAll('.alts .lab')];
          const section = el.getBoundingClientRect();
          const content = el.querySelector('.ov-in').getBoundingClientRect();
          return { gap: button.top - title.bottom, colors: labels.map(label => getComputedStyle(label).color), count: labels.length,
            fontSize: parseFloat(getComputedStyle(el.querySelector('.h2')).fontSize),
            centerOffset: Math.abs((section.top + section.bottom - content.top - content.bottom) / 2) };
        });
        assert.ok(layout.gap >= 16, `${width}: title and button spacing`);
        assert.ok(layout.fontSize >= 42, `${width}: short photo CTA title is prominent`);
        assert.ok(layout.centerOffset < 2, `${width}: CTA content is centered within photograph`);
        assert.equal(layout.count, 2);
        assert.ok(layout.colors.every(color => color === 'rgba(255, 255, 255, 0.9)'), `${width}: contact color ${layout.colors}`);
      }
      await page.close();
    }
  }
  console.log('CTA layout and visual selection checks passed');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
