import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pinned-facts-test-'));
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  const facts = direction.beats.find(beat => beat.type === 'facts');
  facts.facts = [['2012', 'Opening year'], ['Madrid', 'Main location'],
    ['24/7 online service', 'Available every day'], ['123456789012345678901234567890', 'Long real identifier']];
  facts.image = 'long-table';
  facts.ui = { move: 'pinned-sequence' };
  const images = JSON.parse(fs.readFileSync('tests/images.sample.json'));
  for (const image of images) image.detail = true;
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), JSON.stringify(images));
  const html = path.join(dir, 'page.html');
  const renderer = process.env.PINNED_RENDERER || 'lib/render/render_bp.py';
  function renderPage() {
    fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
    const result = spawnSync(process.env.PYTHON || 'python3', [renderer, dir, 'white-desert', html], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
  }
  renderPage();
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });

  for (const width of [320, 390, 1440]) {
    for (const mode of ['normal', 'nomotion', 'reduced']) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: mode === 'reduced' ? 'reduce' : 'no-preference' });
      await page.route(/^https?:\/\//, route => route.abort());
      await page.route('**/gsap.min.js', route => route.fulfill({ path: 'node_modules/gsap/dist/gsap.min.js', contentType: 'application/javascript' }));
      await page.route('**/ScrollTrigger.min.js', route => route.fulfill({ path: 'node_modules/gsap/dist/ScrollTrigger.min.js', contentType: 'application/javascript' }));
      await page.goto(`${pathToFileURL(html)}${mode === 'nomotion' ? '?nomotion=1' : ''}`, { waitUntil: 'load' });
      const section = page.locator(`#${facts.id}`);
      assert.equal(await section.getAttribute('data-sig'), 'pinned');
      assert.equal(await section.locator('.ps-v img').count(), 0, 'section photo is not assigned to an individual fact');
      const slides = await section.locator('.ps-s').evaluateAll(elements => elements.map(el => {
        const rect = el.getBoundingClientRect(), style = getComputedStyle(el);
        return { top: rect.top, bottom: rect.bottom, position: style.position, opacity: Number(style.opacity), text: el.innerText,
          number: el.querySelector('.num')?.textContent };
      }));
      assert.equal(slides.length, facts.facts.length);
      for (let i = 0; i < slides.length; i++) {
        assert.ok(slides[i].text.includes(facts.facts[i][0]));
        assert.ok(slides[i].text.includes(facts.facts[i][1]));
      }
      assert.equal(slides[0].number, '2012');
      assert.equal(slides[1].number, undefined, 'non-numeric fact is not labeled with an invented number');
      if (mode === 'normal') {
        assert.ok(slides.every(slide => slide.position === 'absolute'));
        await page.waitForFunction(id => window.ScrollTrigger?.getAll().some(trigger => trigger.trigger?.id === id), facts.id);
        const metrics = await section.evaluate(el => ({ top: el.getBoundingClientRect().top + scrollY, height: el.getBoundingClientRect().height }));
        const active = [];
        for (const ratio of [0, .4, .9]) {
          await page.evaluate(({ top, height, ratio }) => scrollTo(0, top + Math.max(0, height - innerHeight) * ratio), { ...metrics, ratio });
          await page.waitForTimeout(250);
          active.push(await section.locator('.ps-s.on').getAttribute('data-i'));
        }
        assert.deepEqual(active, ['0', '1', '3']);
      } else {
        assert.ok(slides.every(slide => slide.position === 'static' && slide.opacity === 1 && slide.bottom > slide.top));
        for (let i = 1; i < slides.length; i++) assert.ok(slides[i].top >= slides[i - 1].bottom);
        const overflow = await section.locator('.ps-t').evaluateAll(elements => elements.some(el => {
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          while (walker.nextNode()) {
            const range = document.createRange(); range.selectNodeContents(walker.currentNode);
            if ([...range.getClientRects()].some(rect => rect.left < -1 || rect.right > innerWidth + 1)) return true;
          }
          return false;
        }));
        assert.equal(overflow, false, `${width}px static facts overflow`);
      }
      await page.close();
    }
  }
  for (const count of [1, 6, 9]) {
    facts.facts = Array.from({ length: count }, (_, i) => [String(i), `Original fact ${i}`]);
    renderPage();
    const page = await browser.newPage({ viewport: { width: 390, height: 900 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'load' });
    const section = page.locator(`#${facts.id}`);
    assert.notEqual(await section.getAttribute('data-sig'), 'pinned');
    for (let i = 0; i < count; i++) assert.ok((await section.innerText()).includes(`Original fact ${i}`));
    await page.close();
  }
  console.log('Pinned facts preserve content and motion across viewports');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
