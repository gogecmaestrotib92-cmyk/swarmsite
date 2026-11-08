import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ledger-layout-'));
const python = process.env.PYTHON || 'python3';
const fixture = String.raw`
import base64, io, json, os, sys
from PIL import Image
root = sys.argv[1]
direction = json.load(open('tests/direction.sample.json'))
direction['kind'] = 'place'; direction['hero']['media'] = 'hero'
items = [['First item', '20 €'], ['Second item', '21 €'], ['Third item', '22 €']]
direction['beats'] = [
    {'id':'no-photo', 'type':'ledger', 'h2':'Meat Menu', 'lede':'Grilled dishes', 'items':items, 'image':'screen'},
    {'id':'has-photo', 'type':'ledger', 'h2':'Fish Menu', 'lede':'Fresh dishes', 'items':items, 'image':'food'},
]
def image(id, value, shot=False):
    im = Image.new('RGB', (64, 64)); im.putdata([(value(x, y),) * 3 for y in range(64) for x in range(64)])
    im = im.resize((1000, 700)); buf = io.BytesIO(); im.save(buf, 'PNG')
    return {'id':id, 'w':1000, 'h':700, 'shot':shot, 'data':'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}
hero = image('hero', lambda x,y: 220 if (x // 4) % 2 else 60)
food = image('food', lambda x,y: int(x * 180 / 63))
screen = image('screen', lambda x,y: 230 if (x // 8) % 2 else 80, True)
for name, obj in [('direction.json',direction),('images.json',[hero,food,screen])]:
    with open(os.path.join(root,name),'w') as f: json.dump(obj,f)
`;
let browser;
try {
  const setup = spawnSync(python, ['-c', fixture, dir], { encoding: 'utf8' });
  assert.equal(setup.status, 0, setup.stderr);
  const html = path.join(dir, 'page.html');
  const render = spawnSync(python, ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    for (const [id, expectedPhoto] of [['no-photo', false], ['has-photo', true]]) {
      const section = page.locator(`#${id}`);
      assert.equal(await section.locator('.rows li').count(), 3, `${id} rows at ${width}`);
      assert.equal(await section.locator('.ledger-visual img').count(), expectedPhoto ? 1 : 0, `${id} visual at ${width}`);
      const layout = await section.locator('.two').evaluate(el => ({ columns: getComputedStyle(el).gridTemplateColumns.split(' ').length, noVisual: el.classList.contains('no-visual') }));
      assert.equal(layout.noVisual, !expectedPhoto);
      assert.equal(layout.columns, width === 1440 && expectedPhoto ? 2 : 1, `${id} columns at ${width}`);
    }
    await page.close();
  }
  console.log('Ledger layout checks passed');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
