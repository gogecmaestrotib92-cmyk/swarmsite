import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'texture-fallbacks-'));
const python = process.env.PYTHON || 'python3';
const fixture = String.raw`
import base64, io, json, os, sys
from PIL import Image, ImageDraw
root = sys.argv[1]
base = json.load(open('tests/direction.sample.json'))
source = json.load(open('tests/images.sample.json'))
hero = next(i for i in source if i['id'] == 'waiter'); hero['detail'] = True
def data(image):
    buffer = io.BytesIO(); image.save(buffer, 'JPEG')
    return 'data:image/jpeg;base64,' + base64.b64encode(buffer.getvalue()).decode()
texture = {'id': 'texture', 'w': 1000, 'h': 600, 'bg': True, 'lum': 15, 'detail': True,
           'data': data(Image.new('RGB', (1000, 600), (15, 15, 15)))}
dark_image = Image.new('RGB', (1000, 600), (10, 10, 10))
ImageDraw.Draw(dark_image).rectangle((250, 150, 750, 450), fill=(70, 70, 70))
dark = {'id': 'dark-photo', 'w': 1000, 'h': 600, 'bg': True, 'lum': 25, 'detail': True, 'data': data(dark_image)}
ui_shot = {**dark, 'id': 'ui-shot', 'shot': True, 'bg': False}
cases = ['story', 'story-assigned', 'lead', 'lead-assigned', 'lead-explicit', 'sticky', 'sticky-positive', 'hero', 'hero-assigned', 'hero-positive', 'hero-ui']
for name in cases:
    folder = os.path.join(root, name); os.mkdir(folder)
    direction = json.loads(json.dumps(base)); fact = next(b for b in direction['beats'] if b['type'] == 'facts')
    direction['kind'] = 'place'; direction['hero']['media'] = 'waiter'; fact.pop('image', None)
    if name.startswith('hero'):
        direction['beats'] = []
        direction['hero']['media'] = 'texture' if name == 'hero-assigned' else 'ui-shot' if name == 'hero-ui' else ''
        if name == 'hero-ui': direction['kind'] = 'software'
        images = [ui_shot] if name == 'hero-ui' else [texture, dark] if name == 'hero-positive' else [texture]
    else:
        direction['beats'] = [fact]
        fact['ui'] = {'move': 'story' if name.startswith('story') else 'cards' if name.startswith('lead') else 'sticky-product'}
        if name.endswith('assigned') or name == 'sticky': fact['image'] = 'texture'
        if name == 'sticky-positive': fact['image'] = 'dark-photo'
        if name == 'lead-explicit': fact['ui']['lead'] = 'texture'
        images = [hero, texture, dark]
    for filename, obj in [('direction.json', direction), ('images.json', images)]:
        with open(os.path.join(folder, filename), 'w') as output: json.dump(obj, output)
`;
const expected = {
  'story': ['dark-photo'], 'story-assigned': ['dark-photo'],
  'lead': ['dark-photo'], 'lead-assigned': ['dark-photo'], 'lead-explicit': [],
  'sticky': [], 'sticky-positive': ['dark-photo', 'dark-photo'],
  'hero': [], 'hero-assigned': [], 'hero-positive': ['dark-photo'], 'hero-ui': ['ui-shot'],
};

let browser;
try {
  const setup = spawnSync(python, ['-c', fixture, dir], { encoding: 'utf8' });
  assert.equal(setup.status, 0, setup.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const [name, want] of Object.entries(expected)) {
    const folder = path.join(dir, name); const html = path.join(folder, 'page.html');
    const blueprint = name === 'hero-ui' ? 'butter' : 'white-desert';
    const rendered = spawnSync(python, ['lib/render/render_bp.py', folder, blueprint, html], { encoding: 'utf8' });
    assert.equal(rendered.status, 0, rendered.stderr);
    const images = JSON.parse(fs.readFileSync(path.join(folder, 'images.json')));
    const byData = new Map(images.map(image => [image.data, image.id]));
    for (const width of [390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      await page.route(/^https?:\/\//, route => route.abort());
      await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
      const section = page.locator(name.startsWith('hero') ? '#top' : '#mk');
      const actual = (await section.locator('img').evaluateAll(elements => elements.map(el => el.getAttribute('src')))).map(src => byData.get(src));
      assert.deepEqual(actual, want, `${name} at ${width}px`);
      if (!name.startsWith('hero')) assert.match(await section.textContent(), /170\+/);
      await page.close();
    }
  }
  console.log('Texture fallback checks passed on desktop and mobile');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
