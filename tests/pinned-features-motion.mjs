import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pinned-features-'));
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  const features = direction.beats.find(beat => beat.type === 'features');
  features.features = [
    // features pin only when most of them bring their own picture (a text-only pinned ladder falls back to cards)
    { title: '24/7 support', body: 'Real first detail', image: 'long-table' },
    { title: 'Second offer', body: 'Real second detail', image: 'basta-table' },
    { title: 'Third offer', body: 'Real third detail' },
    { title: 'Fourth offer', body: 'Real fourth detail' }
  ];
  features.image = 'long-table';
  features.ui = { move: 'pinned-sequence' };
  const images = JSON.parse(fs.readFileSync('tests/images.sample.json'));
  for (const image of images) image.detail = true;
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), JSON.stringify(images));
  const html = path.join(dir, 'page.html');
  const render = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });

  for (const width of [390, 1440]) {
    // ?nomotion=1 freezes the real layout for screenshots; only prefers-reduced-motion gets the static fallback layout
    for (const mode of ['normal', 'reduced']) {
      const page = await browser.newPage({
        viewport: { width, height: 900 },
        reducedMotion: mode === 'reduced' ? 'reduce' : 'no-preference'
      });
      await page.route(/^https?:\/\//, route => route.abort());
      await page.route('**/gsap.min.js', route => route.fulfill({ path: 'node_modules/gsap/dist/gsap.min.js', contentType: 'application/javascript' }));
      await page.route('**/ScrollTrigger.min.js', route => route.fulfill({ path: 'node_modules/gsap/dist/ScrollTrigger.min.js', contentType: 'application/javascript' }));
      await page.goto(`${pathToFileURL(html)}${mode === 'nomotion' ? '?nomotion=1' : ''}`, { waitUntil: 'load' });
      const section = page.locator(`#${features.id}`);
      assert.equal(await section.getAttribute('data-sig'), 'pinned');
      assert.equal(await section.locator('.ps-v img').count(), 2);
      const slides = await section.locator('.ps-s').evaluateAll(elements => elements.map(el => {
        const rect = el.getBoundingClientRect(), style = getComputedStyle(el);
        return { top: rect.top, bottom: rect.bottom, position: style.position,
          opacity: Number(style.opacity), title: el.querySelector('h3')?.textContent,
          description: el.querySelector('.lede')?.textContent };
      }));
      assert.equal(slides.length, 4);
      for (let i = 0; i < slides.length; i++) {
        assert.equal(slides[i].title, features.features[i].title);
        assert.equal(slides[i].description, features.features[i].body);
      }
      if (mode === 'normal') {
        assert.ok(slides.every(slide => slide.position === 'absolute'));
        const metrics = await section.evaluate(el => ({ top: el.getBoundingClientRect().top + scrollY, height: el.getBoundingClientRect().height }));
        const active = [];
        for (const ratio of [0, .4, .9]) {
          await page.evaluate(({ top, height, ratio }) => scrollTo(0, top + Math.max(0, height - innerHeight) * ratio), { ...metrics, ratio });
          await page.waitForTimeout(250);
          active.push(await section.locator('.ps-s.on').getAttribute('data-i'));
        }
        assert.deepEqual(active, ['0', '1', '3'], `${width}: pinned progression`);
      } else {
        assert.ok(slides.every(slide => slide.position === 'static' && slide.opacity === 1 && slide.bottom > slide.top));
        for (let i = 1; i < slides.length; i++) assert.ok(slides[i].top >= slides[i - 1].bottom);
      }
      await page.close();
    }
  }
  features.features[0].image = 'long-table';
  features.features[1].image = 'basta-table';
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  const withImages = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(withImages.status, 0, withImages.stderr);
  const retina = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  await retina.route(/^https?:\/\//, route => route.abort());
  await retina.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'load' });
  const pictures = await retina.locator(`#${features.id} .ps-s`).evaluateAll(slides => slides.map(slide => {
    const image = slide.querySelector('img');
    return image ? { natural: image.naturalWidth, width: image.getBoundingClientRect().width, dpr: devicePixelRatio } : null;
  }));
  assert.ok(pictures[0] && pictures[1]);
  assert.equal(pictures[2], null);
  assert.equal(pictures[3], null);
  for (const image of pictures.filter(Boolean)) assert.ok(image.width * image.dpr <= image.natural * 1.35 + 1);
  await retina.close();
  console.log('Pinned feature motion and static content passed');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
