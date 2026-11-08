import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-photo-ui-story-'));
const direction = JSON.parse(fs.readFileSync(path.join(root, 'tests/direction.sample.json'), 'utf8'));
const cases = [
  { name: 'long', editorial: true },
  { name: 'unicode', editorial: true, unicode: true },
  { name: 'tall', editorial: true, image: 'tall' },
  { name: 'wide', editorial: true, image: 'wide' },
  { name: 'photo', editorial: false, image: 'photo' },
  { name: 'tiny', editorial: false, image: 'tiny' },
  { name: 'transparent', editorial: false, image: 'transparent' },
  { name: 'unreadable', editorial: false, image: 'unreadable' },
  { name: 'symbolic', editorial: false, image: 'symbolic' },
  { name: 'texture', editorial: false, image: 'texture' },
  { name: 'missing', editorial: false, image: 'missing' },
  { name: 'other-owner', editorial: false, image: 'hero' },
  { name: 'other-blueprint', editorial: true, blueprint: 'cerebrium' }, // a product component belongs to every software template
  { name: 'other-kind', editorial: false, kind: 'place' },
  { name: 'no-story', editorial: false, move: 'auto' },
];
const inventory = {
  actions: [{ text: 'Read docs', href: 'https://source.example/docs' }],
  sourceCoverage: { sections: [{ id: 's1', title: 'Source section', headingLevel: 'H2', kind: 'section',
    sourceActionsVersion: 1, sourceActions: [{ label: 'Original link', url: 'https://source.example/original' }] }] },
};
let browser;
try {
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  const setup = await browser.newPage();
  const images = await setup.evaluate(() => {
    function make(id, w, h, shot, options = {}) {
      const canvas = document.createElement('canvas'); canvas.width = w; canvas.height = h;
      const ctx = canvas.getContext('2d');
      if (!options.transparent) {
        ctx.fillStyle = options.texture ? '#111' : '#f8f8f8'; ctx.fillRect(0, 0, w, h);
        if (!options.texture) {
          ctx.fillStyle = '#235783'; ctx.fillRect(30, 20, w / 2, h / 2);
          ctx.fillStyle = '#e29324'; ctx.fillRect(w / 2, h / 2, w / 3, h / 3);
        }
      }
      return { id, w: options.metadataWidth || w, h, shot, detail: true, bg: !!options.texture,
        src: options.symbolic ? 'https://source.example/logo.svg' : shot ? 'visual-shot' : 'https://source.example/room.jpg',
        data: canvas.toDataURL('image/png') };
    }
    return [make('hero', 1000, 700, true), make('valid', 600, 595, true), make('tall', 600, 3000, true), make('wide', 1200, 300, true), make('photo', 800, 700, false),
      make('tiny', 499, 600, true, { metadataWidth: 700 }), make('transparent', 600, 595, true, { transparent: true }),
      make('symbolic', 600, 595, true, { symbolic: true }), make('texture', 600, 595, true, { texture: true }),
      { id: 'unreadable', w: 600, h: 595, shot: true, detail: true, src: 'visual-shot', data: 'data:image/png;base64,Zm9v' }];
  });
  await setup.close();
  for (const c of cases) {
    const d = structuredClone(direction);
    d.kind = c.kind || 'software'; d.hero.media = 'hero'; d.hero.ui = { move: 'split' };
    const headline = c.unicode ? '🧭'.repeat(40) : 'A calendar for everyone';
    const lede = c.unicode ? 'Ж'.repeat(100) : 'Every detail is preserved across the full story. '.repeat(5);
    d.beats = [
      { id: 'target', type: 'photo', label: 'Verified', h2: headline, lede, image: c.image || 'valid',
        cap: ['First original caption', 'Second original caption'], source_sections: ['s1'], band: 'dark',
        ui: { move: c.move || 'story' }, cta: 'Read docs', cta_href: 'https://source.example/docs' },
      { id: 'after', type: 'faq', h2: 'Questions', items: [['Question?', 'Verified answer.']] },
    ];
    for (const [name, value] of [['direction', d], ['images', images], ['inventory', inventory]]) {
      fs.writeFileSync(path.join(dir, `${name}.json`), JSON.stringify(value));
    }
    const html = path.join(dir, `${c.name}.html`);
    const result = spawnSync(process.env.PYTHON || 'python3',
      [path.join(root, 'lib/render/render_bp.py'), dir, c.blueprint || 'butter', html], { encoding: 'utf8' });
    assert.equal(result.status, 0, `${c.name}: ${result.stderr}`);
    for (const width of c.unicode ? [390, 920, 1440] : [390, 1440]) {
      for (const height of ['tall', 'wide'].includes(c.name) ? [600, 900] : [900])
      for (const dpr of ['long', 'tall', 'wide'].includes(c.name) ? [1, 2, 3] : [1]) {
        const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: dpr, reducedMotion: 'reduce' });
        await page.route(/^https?:/, route => route.abort());
        await page.goto(pathToFileURL(html).href + '?nomotion=1', { waitUntil: 'load' });
        const section = page.locator('#target');
        assert.equal(await section.count(), 1, `${c.name}: section retained`);
        assert.equal((await section.getAttribute('class')).split(/\s+/).includes('ui-photo-story'), c.editorial, `${c.name}: eligibility`);
        for (const text of [headline, lede, 'First original caption', 'Second original caption']) {
          assert.equal(await section.getByText(text, { exact: true }).count(), 1, `${c.name}: content preserved`);
        }
        for (const url of ['https://source.example/docs', 'https://source.example/original']) {
          const link = section.locator(`a[href="${url}"]`);
          assert.equal(await link.count(), 1, `${c.name}: link retained`);
          await link.click({ trial: true });
        }
        assert.equal(await page.locator('#after details').count(), 1, `${c.name}: following section retained`);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width, `${c.name}: no page overflow`);
        if (c.editorial) {
          const img = section.locator('img');
          assert.equal(await img.count(), 1);
          assert.equal(await img.getAttribute('src'), images.find(x => x.id === (c.image || 'valid')).data, `${c.name}: assigned screenshot`);
          const size = await img.evaluate(el => {
            const r = el.getBoundingClientRect();
            return { w: r.width, h: r.height, nw: el.naturalWidth, nh: el.naturalHeight, fit: getComputedStyle(el).objectFit };
          });
          assert.equal(size.fit, 'contain');
          assert.ok(size.h <= height * .92 + 1, `${c.name} ${width}×${height}/${dpr}: screenshot must fit within 92svh`);
          assert.ok(size.w * dpr <= size.nw + 1 && size.h * dpr <= size.nh + 1, `${c.name}: no pixel upscale`);
          assert.ok(Math.abs(size.w / size.h - size.nw / size.nh) < .02, `${c.name}: screenshot is not cropped`);
          for (const selector of ['h2', '.cap']) {
            const clipped = await section.locator(selector).evaluate(el => {
              const bounds = el.closest('.photo-caption').getBoundingClientRect();
              const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
              let count = 0;
              while (walker.nextNode()) {
                const node = walker.currentNode;
                for (let i = 0; i < node.length;) {
                  const cp = node.data.codePointAt(i), length = cp > 0xffff ? 2 : 1;
                  const range = document.createRange(); range.setStart(node, i); range.setEnd(node, i + length);
                  if (!/\s/u.test(String.fromCodePoint(cp))) for (const rect of range.getClientRects()) {
                    if (rect.left < Math.max(0, bounds.left) - 1 || rect.right > Math.min(innerWidth, bounds.right) + 1) count++;
                  }
                  i += length;
                }
              }
              return count;
            });
            assert.equal(clipped, 0, `${c.name} ${width}: ${selector} characters fit in the viewport`);
          }
        }
        if (c.name === 'other-owner') assert.equal(await section.locator('img').count(), 0, 'hero screenshot is not reused');
        await page.close();
      }
    }
  }
  console.log(`Butter photo UI story: ${cases.length} eligible/ineligible cases, responsive content, links, ownership and pixel bounds verified`);
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
