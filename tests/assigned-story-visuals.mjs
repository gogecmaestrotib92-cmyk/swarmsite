import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-assigned-visuals-'));
const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json', 'utf8'));
const features = (prefix, n) => Array.from({ length: n }, (_, i) => ({ title: `${prefix} title ${i}`, body: `${prefix} detail ${i}` }));
const story = (id, image, n = 3) => ({ id, type: 'features', h2: id, image, features: features(id, n), ui: { move: 'story', lead: '' } });
const cards = (id, image) => ({ id, type: 'features', h2: id, image, features: features(id, 6), ui: { move: 'cards', cols: 3 } });
direction.kind = 'software';
direction.hero.media = 'hero';
direction.hero.ui = { move: 'split' };
direction.beats = [
  story('agents', 'agents-shot'), story('events', 'events-shot'), cards('apps', 'apps-shot'),
  story('edge-story', 'edge-story-shot'), cards('edge-card', 'edge-card-shot'),
  story('long', 'long-shot', 7),
  { ...story('lead-only', undefined, 7), ui: { move: 'story', lead: 'lead-shot' } },
  { ...story('individual', 'section-shot', 5), features: features('individual', 5).map((f, i) => ({ ...f, image: `individual-${i}` })), ui: { move: 'story', lead: 'section-shot' } },
  story('owner', 'owned-shot'), story('other-owner', 'owned-shot'),
  story('tiny-shot', 'tiny-shot'), story('tiny-photo', 'tiny-photo'), cards('tiny-card', 'tiny-card'),
  story('missing', 'missing-image'), story('blank', 'blank-shot'), story('symbolic', 'symbolic'),
  { ...cards('text-only', 'none-shot'), ui: { move: 'cards', lead: '', cols: 3 } },
  { ...cards('ticker', 'ticker-shot'), ui: { move: 'marquee', lead: '', cols: 1 } },
];
let browser;
try {
  browser = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  const setup = await browser.newPage();
  const images = await setup.evaluate(() => {
    function make(id, w, h, shot, options = {}) {
      const canvas = document.createElement('canvas'); canvas.width = w; canvas.height = h;
      const ctx = canvas.getContext('2d'); ctx.fillStyle = options.blank ? '#fff' : '#fafafa'; ctx.fillRect(0, 0, w, h);
      if (!options.blank) { ctx.fillStyle = '#234567'; ctx.fillRect(w * .1, h * .15, w * .35, h * .65); ctx.fillStyle = '#f4a145'; ctx.fillRect(w * .55, h * .2, w * .3, h * .45); }
      return { id, w: options.meta || w, h, shot, detail: true, src: options.svg ? 'https://source.example/logo.svg' : shot ? 'visual-shot' : 'https://source.example/photo.jpg', data: canvas.toDataURL('image/png') };
    }
    return [make('hero', 1200, 800, true), make('agents-shot', 600, 595, true), make('events-shot', 632, 537, true),
      make('apps-shot', 1000, 420, true), make('edge-story-shot', 500, 600, true, { meta: 100 }), make('edge-card-shot', 500, 600, true, { meta: 100 }),
      make('long-shot', 600, 595, true), make('lead-shot', 632, 537, true),
      make('owned-shot', 600, 595, true), make('tiny-shot', 499, 600, true, { meta: 1000 }),
      make('tiny-photo', 639, 480, false, { meta: 1000 }), make('tiny-card', 499, 600, true, { meta: 1000 }),
      make('blank-shot', 700, 600, true, { blank: true }), make('symbolic', 700, 600, true, { svg: true }), make('ticker-shot', 700, 600, true),
      make('none-shot', 700, 600, true), make('section-shot', 700, 600, true), make('place-photo', 800, 600, false), make('place-hero', 1200, 800, false), ...Array.from({ length: 5 }, (_, i) => make(`individual-${i}`, 750, 600, false))];
  });
  await setup.close();
  for (const [name, data] of [['direction.json', direction], ['images.json', images], ['inventory.json', {}]]) fs.writeFileSync(path.join(dir, name), JSON.stringify(data));
  const blueprints = fs.readdirSync('lib/blueprints').filter(name => name.endsWith('.bp.json'));
  for (const bpFile of blueprints) {
    const bp = bpFile.replace('.bp.json', '');
    const html = path.join(dir, `${bp}.html`);
    const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, bp, html], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    for (const [width, dpr] of [[390, 1], [390, 2], [390, 3], [1440, 1], [1440, 2], [1440, 3]]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: dpr, reducedMotion: 'reduce' });
      await page.goto(pathToFileURL(html).href + '?nomotion=1');
      for (const [id, imageId] of [['agents', 'agents-shot'], ['events', 'events-shot'], ['apps', 'apps-shot'], ['edge-story', 'edge-story-shot'], ['edge-card', 'edge-card-shot'], ['long', 'long-shot'], ['lead-only', 'lead-shot'], ['owner', 'owned-shot']]) {
        const section = page.locator(`#${id}`), img = section.locator('img');
        assert.equal(await img.count(), 1, `${bp} ${id} image at ${width}/${dpr}`);
        const info = await img.evaluate(el => { const r = el.getBoundingClientRect(); return { src: el.getAttribute('src'), w: r.width, h: r.height, nw: el.naturalWidth, nh: el.naturalHeight, fit: getComputedStyle(el).objectFit }; });
        assert.equal(info.src, images.find(x => x.id === imageId).data, `${bp} ${id} preserves the assigned source`);
        assert.ok(info.w * dpr <= info.nw + 1 && info.h * dpr <= info.nh + 1, `${bp} ${id} must not upscale`);
        assert.ok(Math.abs(info.w / info.h - info.nw / info.nh) < .02, `${bp} ${id} keeps the full aspect ratio`);
        assert.equal(info.fit, 'contain');
        for (const f of direction.beats.find(x => x.id === id).features) {
          assert.equal(await section.getByText(f.title, { exact: true }).count(), 1);
          assert.equal(await section.getByText(f.body, { exact: true }).count(), 1);
        }
      }
      const individual = page.locator('#individual .card');
      assert.equal(await individual.count(), 5, `${bp} individual cards`);
      for (let i = 0; i < 5; i++) {
        const card = individual.nth(i);
        assert.equal(await card.locator('img').getAttribute('src'), images.find(x => x.id === `individual-${i}`).data, `${bp} individual image ${i}`);
        assert.equal(await card.getByText(`individual title ${i}`, { exact: true }).count(), 1);
        assert.equal(await card.getByText(`individual detail ${i}`, { exact: true }).count(), 1);
      }
      for (const id of ['other-owner', 'tiny-shot', 'tiny-photo', 'tiny-card', 'missing', 'blank', 'symbolic', 'ticker', 'text-only']) {
        assert.equal(await page.locator(`#${id} img`).count(), 0, `${bp} ${id} must not substitute or steal an image`);
      }
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width, `${bp} horizontal overflow`);
      await page.close();
    }
  }
  for (const [kind, bp] of [['place', 'tengile'], ['service', 'aino']]) {
    const other = structuredClone(direction);
    other.kind = kind;
    other.hero.media = 'place-hero';
    other.beats = [story('place-long', undefined, 5), { ...story('place-lead-only', undefined), ui: { move: 'story', lead: 'events-shot' } }];
    fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(other));
    const html = path.join(dir, `${kind}.html`);
    const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, bp, html], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    for (const width of [390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
      await page.goto(pathToFileURL(html).href + '?nomotion=1');
      const section = page.locator('#place-long');
      assert.ok((await section.getAttribute('class')).split(' ').includes('cards'), `${kind} keeps the existing cards fallback`);
      assert.equal(await section.locator('.assigned-visual').count(), 0, `${kind} must not use the new product-shot layout`);
      for (const f of other.beats[0].features) {
        assert.equal(await section.getByText(f.title, { exact: true }).count(), 1);
        assert.equal(await section.getByText(f.body, { exact: true }).count(), 1);
      }
      const leadOnly = page.locator('#place-lead-only');
      assert.equal(await leadOnly.locator('img').count(), 1, `${kind} keeps its real photo fallback`);
      assert.equal(await leadOnly.locator('img').getAttribute('src'), images.find(x => x.id === 'place-photo').data, `${kind} must not substitute a UI screenshot`);
      await page.close();
    }
  }
  {
    const product = structuredClone(direction);
    product.kind = 'product';
    product.beats = [{ id: 'stickers', type: 'features', h2: 'Product', ui: {},
      features: features('sticker', 5).map((f, i) => ({ ...f, body: '', image: `individual-${i}` })) }];
    fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(product));
    const html = path.join(dir, 'product-stickers.html');
    const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'crav', html], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
    await page.goto(pathToFileURL(html).href + '?nomotion=1');
    assert.ok((await page.locator('#stickers').getAttribute('class')).split(' ').includes('stickers'), 'default CRAV sticker recipe is preserved');
    await page.close();
  }
  console.log('Assigned product shots survive with ownership, text and pixel bounds across 12 blueprints');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
