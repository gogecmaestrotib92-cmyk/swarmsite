import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'nav-layout-'));
let browser;
try {
  for (const name of ['images', 'assets']) fs.copyFileSync(`tests/${name}.sample.json`, path.join(dir, `${name}.json`));
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.hero.cta = 'Reservar mesa';
  const form = direction.beats.find(beat => beat.type === 'form');
  form.cta = 'Reservar mesa'; form.cta_href = 'https://example.com/book';
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'inventory.json'), JSON.stringify({ actions: [{ text: 'Reservar mesa', href: 'https://example.com/book' }] }));
  const html = path.join(dir, 'page.html');
  const render = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [320, 360, 390, 430]) {
    const page = await browser.newPage({ viewport: { width, height: 844 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
    for (const label of ['Reservar mesa', 'Book an unforgettable evening for two', 'Extraordinarilylongreservationwordwithoutspaces']) {
      const measurement = await page.evaluate(label => {
        const button = document.querySelector('nav .btn');
        const logo = document.querySelector('nav .wrap > a:first-child');
        button.firstChild.textContent = label;
        const buttonRect = button.getBoundingClientRect(), logoRect = logo.getBoundingClientRect();
        const range = document.createRange(); range.selectNodeContents(button.firstChild);
        return { buttonLeft: buttonRect.left, buttonRight: buttonRect.right, logoRight: logoRect.right,
          scrollWidth: button.scrollWidth, clientWidth: button.clientWidth,
          rects: [...range.getClientRects()].map(rect => ({ left: rect.left, right: rect.right })) };
      }, label);
      assert.ok(measurement.buttonLeft >= measurement.logoRight - 1, `${width}: logo overlaps ${label}`);
      assert.ok(measurement.buttonRight <= width + 1 && measurement.scrollWidth <= measurement.clientWidth + 1, `${width}: button clipped for ${label}`);
      for (const rect of measurement.rects) assert.ok(rect.left >= 0 && rect.right <= width, `${width}: text clipped for ${label}`);
      if (label === 'Reservar mesa') assert.equal(measurement.rects.length, 1, `${width}: short label wraps`);
    }
    await page.locator('nav .btn').evaluate(el => { el.firstChild.textContent = 'Reservar mesa'; });
    const anchorLayout = await page.locator('section.sec[id]').nth(1).evaluate(el => {
      el.scrollIntoView({ block: 'start' });
      return { top: el.getBoundingClientRect().top, navBottom: document.querySelector('nav').getBoundingClientRect().bottom };
    });
    assert.ok(anchorLayout.top >= anchorLayout.navBottom - 1, `${width}: fixed navigation covers the anchored section`);
    await page.close();
  }
  console.log('Navigation layout checks passed');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
