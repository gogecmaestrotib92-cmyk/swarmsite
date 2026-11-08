import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ledger-actions-'));
const python = process.env.PYTHON || 'python3';
const primary = 'https://example.test/reserve?day=1&party=2';
const secondary = 'https://example.test/wine?red=1&white=2';
let browser;
try {
  const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  direction.kind = 'place';
  direction.hero.media = 'waiter';
  direction.beats = [{ id: 'menu', type: 'ledger', h2: 'Our menu', lede: 'Food and prices', band: 'dark',
    image: 'long-table', items: [['First dish', '10 €'], ['Second dish', '20 €']],
    cta: 'Reserve & dine', cta_href: primary, cta2: 'Wine & drinks', cta2_href: secondary }];
  fs.writeFileSync(path.join(dir, 'images.json'), fs.readFileSync('tests/images.sample.json'));
  fs.writeFileSync(path.join(dir, 'inventory.json'), JSON.stringify({
    forms: [{ text: 'Reserve & dine', source_url: primary }],
    sourcePages: [{ actions: [{ text: 'Wine & drinks', href: secondary }] }],
  }));
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const move of ['story', 'sticky-product', 'cards', 'marquee']) {
    direction.beats[0].ui = { move, cols: 3 };
    fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
    const output = path.join(dir, `${move}.html`);
    const render = spawnSync(python, ['lib/render/render_bp.py', dir, 'white-desert', output], { encoding: 'utf8' });
    assert.equal(render.status, 0, render.stderr);
    for (const width of [390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
      await page.route(/^https?:\/\//, route => {
        if (route.request().url().startsWith('https://example.test/')) return route.fulfill({ status: 200, body: 'Destination reached' });
        return route.abort();
      });
      await page.goto(`${pathToFileURL(output)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
      const links = page.locator('#menu .ctas a');
      assert.equal(await links.count(), 2, `${move}, ${width}: both captured actions`);
      const geometry = await links.evaluateAll(nodes => nodes.map(node => {
        const r = node.getBoundingClientRect(), s = getComputedStyle(node);
        const canvas = document.createElement('canvas'); canvas.width = canvas.height = 1;
        const ctx = canvas.getContext('2d');
        const paint = color => { ctx.fillStyle = color; ctx.fillRect(0, 0, 1, 1); };
        paint('white'); paint(getComputedStyle(node.closest('.sec')).backgroundColor); paint(s.backgroundColor);
        const bg = [...ctx.getImageData(0, 0, 1, 1).data].slice(0, 3);
        paint(s.color);
        const fg = [...ctx.getImageData(0, 0, 1, 1).data].slice(0, 3);
        const luminance = rgb => rgb.map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
          .reduce((total, value, index) => total + value * [.2126, .7152, .0722][index], 0);
        const levels = [luminance(bg), luminance(fg)].sort((a, b) => b - a);
        return { href: node.href, text: node.innerText.trim(), x: r.x, y: r.y, right: r.right,
          bottom: r.bottom, width: r.width, height: r.height, visible: s.visibility === 'visible' && s.display !== 'none',
          contrast: (levels[0] + .05) / (levels[1] + .05), fontSize: parseFloat(s.fontSize), fontWeight: parseInt(s.fontWeight) };
      }));
      assert.equal(geometry[0].href, primary);
      assert.equal(geometry[1].href, secondary);
      assert.ok(geometry[0].text.includes('Reserve & dine'));
      assert.ok(geometry[1].text.includes('Wine & drinks'));
      for (const rect of geometry) {
        assert.ok(rect.visible && rect.width > 0 && rect.height >= 40, `${move}, ${width}: visible touch target`);
        assert.ok(rect.x >= 0 && rect.right <= width + 1, `${move}, ${width}: action fits viewport`);
        const largeText = rect.fontSize >= 24 || (rect.fontSize >= 18.67 && rect.fontWeight >= 700);
        assert.ok(rect.contrast >= (largeText ? 3 : 4.5), `${move}, ${width}: action text contrast ${rect.contrast.toFixed(2)}`);
      }
      const [a, b] = geometry;
      assert.ok(a.right <= b.x + 1 || b.right <= a.x + 1 || a.bottom <= b.y + 1 || b.bottom <= a.y + 1,
        `${move}, ${width}: actions do not overlap`);
      for (const index of [0, 1]) {
        await links.nth(index).click();
        await page.waitForURL(index === 0 ? primary : secondary);
        await page.goto(`${pathToFileURL(output)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
      }
      await page.close();
    }
  }
  console.log('Ledger actions remain visible, distinct and clickable in every variant');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
