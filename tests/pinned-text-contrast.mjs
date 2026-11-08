import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pinned-text-contrast-'));
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.kind = 'software';
  direction.brand = { ...direction.brand, accent: '#242424', paper: '#FBFAF7', ink: '#111111' };
  direction.beats = ['dark', 'paper'].map(band => ({
    id: `steps-${band}`, type: 'steps', band, h2: 'One link, three steps',
    steps: ['Send one link with your free hours.', 'Let them pick the time.', 'It lands in the calendar.'],
    ui: { move: 'pinned-sequence' },
  }));
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'images.json'), '[]');
  const html = path.join(dir, 'page.html');
  const render = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'butter', html], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });

  for (const width of [390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'load' });
    for (const band of ['dark', 'paper']) {
      const section = page.locator(`#steps-${band}`);
      assert.equal(await section.getAttribute('data-sig'), 'pinned');
      const slides = section.locator('.ps-s');
      assert.equal(await slides.count(), 3);
      for (let i = 0; i < 3; i++) {
        const slide = slides.nth(i);
        assert.equal(await slide.locator('figure').count(), 0, 'fixture must exercise the no-visual layout');
        const metrics = await slide.evaluate(el => {
          const number = el.querySelector('.num'), heading = el.querySelector('h3');
          const section = el.closest('section');
          const rgb = color => {
            const match = color.match(/^rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)/);
            if (!match) throw new Error(`Unexpected CSS color: ${color}`);
            return match.slice(1, 4).map(Number);
          };
          const luminance = c => c.map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
            .reduce((sum, v, j) => sum + v * [.2126, .7152, .0722][j], 0);
          const sectionBackground = getComputedStyle(section).backgroundColor;
          const background = sectionBackground === 'rgba(0, 0, 0, 0)' ? getComputedStyle(document.body).backgroundColor : sectionBackground;
          const values = [luminance(rgb(getComputedStyle(number).color)), luminance(rgb(background))].sort((a, b) => a - b);
          return { text: heading.textContent, contrast: (values[1] + .05) / (values[0] + .05),
            headingWidth: heading.getBoundingClientRect().width, slideWidth: el.getBoundingClientRect().width,
            numberWidth: number.getBoundingClientRect().width, numberScrollWidth: number.scrollWidth,
            alignment: getComputedStyle(el.querySelector('.ps-t')).textAlign };
        });
        assert.equal(metrics.text, direction.beats[0].steps[i]);
        assert.ok(metrics.contrast >= 3, `${band} numeral contrast at ${width}px is ${metrics.contrast.toFixed(2)}:1`);
        assert.ok(metrics.headingWidth >= metrics.slideWidth * (width >= 1000 ? .55 : .6),
          `${band} no-visual text uses only ${Math.round(100 * metrics.headingWidth / metrics.slideWidth)}% of slide at ${width}px`);
        assert.equal(metrics.alignment, 'center', `${band} no-visual content should use a balanced layout at ${width}px`);
        assert.ok(metrics.numberScrollWidth <= metrics.numberWidth + 1, `${band} numeral overflows at ${width}px`);
      }
    }
    await page.close();
  }
  console.log('Pinned text without imagery has visible numerals and uses its available width');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
