import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'photo-editorial-'));
const python = process.env.PYTHON || 'python3';
const fixture = String.raw`
import base64, io, json, os, sys
from PIL import Image
root = sys.argv[1]
def picture(id, w, h, color):
    b = io.BytesIO(); Image.new('RGB', (w, h), color).save(b, 'PNG')
    return {'id': id, 'w': w, 'h': h, 'detail': True,
            'data': 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()}
for name, kind, width, height, lede in [
    ('place', 'place', 960, 720, 'A welcoming room for celebrations and live events.'),
    ('boundary', 'place', 960, 720, 'A warm place for celebrations, with dinners, special gatherings, live events and memorable evenings for family and friends.'),
    ('portrait', 'place', 900, 1400, 'A welcoming room for celebrations and live events.'),
    ('small', 'place', 800, 600, 'A welcoming room for celebrations and live events.'),
    ('long', 'place', 960, 720, 'Long description. ' * 15),
    ('software', 'software', 960, 720, 'A welcoming room for celebrations and live events.')]:
    folder = os.path.join(root, name); os.mkdir(folder)
    d = json.load(open('tests/direction.sample.json'))
    d['kind'] = kind; d['hero']['media'] = 'hero'
    title = 'A special room for all celebrations' if name == 'boundary' else 'The room'
    d['beats'] = [{'id': 'room', 'type': 'photo', 'image': 'room', 'label': 'A PLACE TO GATHER',
                   'h2': title, 'lede': lede, 'cap': ['Thirty guests', 'Live events'],
                   'ui': {'move': 'story'}}]
    for file, value in [('direction.json', d), ('images.json', [picture('hero', 1400, 900, '#777'),
                                                                 picture('room', width, height, '#fff')])]:
        with open(os.path.join(folder, file), 'w') as f: json.dump(value, f)
`;

let browser;
try {
  const setup = spawnSync(python, ['-c', fixture, dir], { encoding: 'utf8' });
  assert.equal(setup.status, 0, setup.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const name of ['place', 'boundary', 'portrait', 'small', 'long', 'software']) {
    const folder = path.join(dir, name), html = path.join(folder, 'page.html');
    const render = spawnSync(python, ['lib/render/render_bp.py', folder, 'white-desert', html], { encoding: 'utf8' });
    assert.equal(render.status, 0, render.stderr);
    for (const { width, height, dpr } of [{ width: 1440, height: 900, dpr: 1 }, { width: 1000, height: 720, dpr: 1 }, { width: 1440, height: 900, dpr: 2 }, { width: 390, height: 844, dpr: 2 }]) {
      const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: dpr });
      await page.route(/^https?:\/\//, route => route.abort());
      await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
      const section = page.locator('#room');
      assert.equal(await section.locator('.st-v img').count(), 1);
      assert.equal(await section.evaluate(el => el.classList.contains('story-editorial')), ['place', 'boundary'].includes(name), `${name}: editorial eligibility`);
      for (const value of ['A PLACE TO GATHER', name === 'boundary' ? 'A special room for all celebrations' : 'The room', 'Thirty guests', 'Live events']) assert.ok((await section.innerText()).includes(value));
      assert.ok((await section.innerText()).includes(name === 'boundary' ? 'A warm place for celebrations' : name === 'long' ? 'Long description.' : 'A welcoming room for celebrations'), `${name}: description remains visible`);
      const metrics = await section.evaluate(async el => {
        const img = el.querySelector('img'); await img.decode();
        const figure = el.querySelector('figure').getBoundingClientRect();
        const text = el.querySelector('.st-t').getBoundingClientRect();
        const rects = [...el.querySelectorAll('.st-t .lab,.st-t .h2,.st-t .lede,.st-t li')].map(x => ({
          rect: x.getBoundingClientRect().toJSON(), color: getComputedStyle(x).color
        }));
        const textEl = el.querySelector('.st-t');
        return { naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight, figure: figure.toJSON(), text: text.toJSON(), rects,
          background: getComputedStyle(textEl).backgroundImage, scrim: getComputedStyle(textEl, '::before').backgroundImage,
          mask: getComputedStyle(textEl, '::before').maskImage, scrollWidth: document.documentElement.scrollWidth };
      });
      assert.equal(metrics.scrollWidth, width, `${name} ${width}: horizontal overflow`);
      assert.ok(metrics.figure.width * dpr <= metrics.naturalWidth * 1.35 + 2, `${name} ${width}: source stretched beyond DPR limit`);
      if (['place', 'boundary'].includes(name)) {
        if (width === 390 || metrics.figure.width <= 700) {
          assert.ok(Math.abs(metrics.figure.width / metrics.figure.height - metrics.naturalWidth / metrics.naturalHeight) < 0.01, 'compact layout shows the entire original image');
          assert.ok(metrics.text.top >= metrics.figure.bottom, 'compact layout places text after the image');
        } else {
          assert.ok(Math.abs(metrics.figure.width / metrics.figure.height - 1.6) < 0.01, 'desktop uses the editorial frame');
          assert.ok(metrics.figure.height <= height * .78 + 2, 'editorial image fits the viewport');
          assert.match(metrics.background + metrics.scrim, /rgba\(0, 0, 0, 0\.82\)/, 'black scrim remains under the text');
          for (const { rect, color } of metrics.rects) {
            assert.equal(color, 'rgb(255, 255, 255)', 'all overlay text is white');
            assert.ok(rect.top >= metrics.figure.top - 1 && rect.bottom <= metrics.figure.bottom + 1, 'all text remains inside the photo');
            assert.ok(rect.right <= metrics.text.right - 27, 'text stays within the solid part of the scrim');
          }
          // Sample the rendered scrim next to every text element over a pure white image.
          await section.locator('.st-t').scrollIntoViewIfNeeded();
          const points = await section.evaluate(el => [...el.querySelectorAll('.st-t .lab,.st-t .h2,.st-t .lede,.st-t li')].map(x => {
            const b = x.getBoundingClientRect(); return [Math.round(b.left - 6), Math.round((b.top + b.bottom) / 2)];
          }));
          const screenshot = path.join(dir, `contrast-${name}-${width}-${dpr}.png`);
          await page.screenshot({ path: screenshot });
          const sample = spawnSync(python, ['-c', 'import json,sys; from PIL import Image; im=Image.open(sys.argv[1]).convert("RGB"); print(json.dumps([im.getpixel(tuple(p)) for p in json.loads(sys.argv[2])]))', screenshot, JSON.stringify(points)], { encoding: 'utf8' });
          assert.equal(sample.status, 0, sample.stderr);
          for (const rgb of JSON.parse(sample.stdout)) {
            const linear = rgb.map(n => { const v = n / 255; return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; });
            const lum = .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2];
            assert.ok(1.05 / (lum + .05) >= 4.5, `rendered text contrast over white: ${rgb}`);
          }
        }
      }
      await page.close();
    }
  }
  console.log('Editorial photo eligibility, content, contrast, and responsive sizing checks passed');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
