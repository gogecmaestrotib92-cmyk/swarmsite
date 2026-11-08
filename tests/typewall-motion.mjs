import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'typewall-motion-'));
let browser;
try {
  for (const name of ['direction', 'images', 'assets']) fs.copyFileSync(`tests/${name}.sample.json`, path.join(dir, `${name}.json`));
  const direction = JSON.parse(fs.readFileSync(path.join(dir, 'direction.json')));
  const steps = direction.beats.find(beat => beat.type === 'steps');
  steps.ui = { ...steps.ui, move: 'pinned-sequence' };
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  const html = path.join(dir, 'page.html');
  const render = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [390, 1440]) {
    for (const mode of ['normal', 'nomotion', 'reduced']) {
      const noMotion = mode !== 'normal';
      const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: mode === 'reduced' ? 'reduce' : 'no-preference' });
      await page.route(/^https?:\/\//, route => route.abort());
      await page.route('**/gsap.min.js', route => route.fulfill({ path: 'node_modules/gsap/dist/gsap.min.js', contentType: 'application/javascript' }));
      await page.route('**/ScrollTrigger.min.js', route => route.fulfill({ path: 'node_modules/gsap/dist/ScrollTrigger.min.js', contentType: 'application/javascript' }));
      await page.goto(`${pathToFileURL(html)}${mode === 'nomotion' ? '?nomotion=1' : ''}`, { waitUntil: 'load' });
      const slides = await page.locator('.ps-s').evaluateAll(elements => elements.map(el => {
        const rect = el.getBoundingClientRect();
        const style = getComputedStyle(el);
        return { top: rect.top, bottom: rect.bottom, position: style.position, opacity: Number(style.opacity) };
      }));
      assert.ok(slides.length >= 2, `${width}: pinned steps`);
      if (noMotion) {
        assert.ok(slides.every(slide => slide.position === 'static' && slide.opacity === 1 && slide.bottom > slide.top), `${width}: all pinned steps visible`);
        for (let i = 1; i < slides.length; i++) assert.ok(slides[i].top >= slides[i - 1].bottom, `${width}: pinned steps overlap`);
      } else {
        assert.ok(slides.every(slide => slide.position === 'absolute'), `${width}: animated pinned steps`);
      }
      const animation = await page.locator('.mq-track').evaluate(el => getComputedStyle(el).animationName);
      assert.equal(animation, noMotion ? 'none' : 'mq', `${width}: marquee animation`);
      const wall = page.locator('[data-sig="typewall"]');
      const metrics = await wall.evaluate(el => ({ top: el.getBoundingClientRect().top + scrollY, height: el.getBoundingClientRect().height }));
      const counts = [];
      for (const ratio of [0, .5, 1]) {
        await page.evaluate(({ top, height, ratio }) => scrollTo(0, top + Math.max(0, height - innerHeight) * ratio), { ...metrics, ratio });
        await page.waitForTimeout(250);
        counts.push(await wall.locator('.tw-w.on').count());
      }
      const state = await wall.evaluate(el => ({ animated: el.classList.contains('tw-animated'), total: el.querySelectorAll('.tw-w').length,
        trigger: !!window.ScrollTrigger?.getAll().find(trigger => trigger.trigger === el) }));
      assert.ok(state.total >= 3, `${width}: type-wall words`);
      if (noMotion) {
        assert.equal(state.animated, false);
        assert.equal(state.trigger, false);
        assert.deepEqual(counts, [state.total, state.total, state.total]);
      } else {
        assert.equal(state.animated, true);
        assert.equal(state.trigger, true);
        assert.ok(counts[0] < counts[1] && counts[1] < counts[2], `${width}: word activation ${counts}`);
        assert.equal(counts[2], state.total);
      }
      await page.close();
    }
  }
  console.log('Type-wall motion checks passed');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
