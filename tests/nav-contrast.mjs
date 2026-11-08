import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'nav-contrast-'));
let browser;
try {
  for (const name of ['images', 'assets']) fs.copyFileSync(`tests/${name}.sample.json`, path.join(dir, `${name}.json`));
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.kind = 'place';
  direction.brand.paper = '#f4ece0'; direction.brand.ink = '#111010'; direction.brand.accent = '#cea574';
  direction.hero.ui = { move: 'photo' };
  direction.hero.cta = 'Reservar mesa'; direction.hero.cta_href = 'https://example.com/book';
  direction.beats = [
    { id: 'dark', type: 'ledger', band: 'dark', h2: 'Bacalao', items: [['Fish', '20 €']], ui: { move: 'story' } },
    { id: 'light', type: 'ledger', band: 'paper', h2: 'Carnes', items: [['Meat', '25 €']], ui: { move: 'story' } },
  ];
  direction.nav.links = [['#dark', 'Bacalao'], ['#light', 'Carnes']];
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  fs.writeFileSync(path.join(dir, 'inventory.json'), JSON.stringify({ actions: [{ text: 'Reservar mesa', href: 'https://example.com/book' }] }));
  const html = path.join(dir, 'page.html');
  const render = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, 'tengile', html], { encoding: 'utf8' });
  assert.equal(render.status, 0, render.stderr);
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'load' });
    for (const id of ['dark', 'light']) {
      await page.locator(`#${id}`).evaluate(el => scrollTo(0, el.offsetTop + 120));
      await page.waitForTimeout(1100); // let the navigation's color transition finish
      const result = await page.evaluate(() => {
        const nav = document.querySelector('nav'), button = nav.querySelector('.btn'), link = nav.querySelector('.links a');
        const css = el => getComputedStyle(el);
        const rgb = color => {
          const match = color.match(/^rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)$/);
          if (!match) throw new Error(`Unexpected CSS color: ${color}`);
          return match.slice(1, 4).map(Number);
        };
        const contrast = (a, b) => {
          const luminance = c => c.map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
            .reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
          const [lo, hi] = [luminance(a), luminance(b)].sort((x, y) => x - y);
          return (hi + .05) / (lo + .05);
        };
        // The solid nav is 86% paper; test its contrast over both black and white.
        const paperProbe = document.createElement('i'); paperProbe.style.color = 'var(--paper)'; nav.appendChild(paperProbe);
        const paper = rgb(css(paperProbe).color); paperProbe.remove();
        const navColors = [0, 255].map(base => paper.map(channel => channel * .86 + base * .14));
        const buttonBackground = rgb(css(button).backgroundColor);
        return { solid: nav.classList.contains('solid'), linkDisplayed: css(link.parentElement).display !== 'none',
          linkContrast: Math.min(...navColors.map(bg => contrast(rgb(css(link).color), bg))),
          buttonTextContrast: contrast(rgb(css(button).color), buttonBackground),
          buttonSurfaceContrast: Math.min(...navColors.map(bg => contrast(buttonBackground, bg))) };
      });
      assert.equal(result.solid, true, `${id} section must activate solid navigation at ${width}px`);
      if (result.linkDisplayed) assert.ok(result.linkContrast >= 4.5, `${id} nav links at ${width}px: ${result.linkContrast}`);
      assert.ok(result.buttonTextContrast >= 4.5, `${id} CTA text at ${width}px: ${result.buttonTextContrast}`);
      assert.ok(result.buttonSurfaceContrast >= 3, `${id} CTA shape at ${width}px: ${result.buttonSurfaceContrast}`);
    }
    await page.close();
  }
  console.log('Solid navigation remains legible over dark and light sections');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
