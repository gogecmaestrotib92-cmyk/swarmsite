import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ledger-moves-'));
const python = process.env.PYTHON || 'python3';
let browser;
try {
  const base = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  const images = JSON.parse(fs.readFileSync('tests/images.sample.json'));
  base.kind = 'place';
  base.hero.media = 'waiter';
  const items = Array.from({ length: 12 }, (_, index) => [
    index === 3 ? `Long-${'dish'.repeat(30)}` : `Dish ${index + 1}`,
    index === 0 ? 'Free forever' : index === 11 ? 'Custom' : `${index + 10} €`,
  ]);
  fs.writeFileSync(path.join(dir, 'images.json'), JSON.stringify(images));
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const hasImage of [false, true]) {
    for (const move of ['cards', 'story', 'sticky-product', 'marquee']) {
      base.beats = [{ id: 'menu', type: 'ledger', h2: 'Our menu', label: 'Our menu', lede: 'Food and prices',
        items, image: hasImage ? 'long-table' : '', ui: { move, cols: 3 } }];
      fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(base));
      const html = path.join(dir, 'page.html');
      const render = spawnSync(python, ['lib/render/render_bp.py', dir, 'white-desert', html], { encoding: 'utf8' });
      assert.equal(render.status, 0, render.stderr);
      for (const width of [390, 1440]) {
        const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
        await page.route(/^https?:\/\//, route => route.abort());
        await page.goto(`${pathToFileURL(html)}?nomotion=1`, { waitUntil: 'domcontentloaded' });
        const section = page.locator('#menu');
        const entries = section.locator('.ledger-card-list li, .rows li');
        assert.equal(await entries.count(), items.length, `${move}, image ${hasImage}, ${width}: every price`);
        for (let index = 0; index < items.length; index++) {
          const text = await entries.nth(index).innerText();
          assert.ok(text.includes(items[index][0]) && text.includes(items[index][1]), `${move}, ${width}: item ${index + 1}`);
        }
        const result = await section.evaluate(el => {
          const grid = el.querySelector('.ledger-card-list');
          const ticker = el.querySelector('.ledger-ticker');
          const intro = el.querySelector('.ledger-intro');
          const textRects = [...el.querySelectorAll('.ledger-card-list li span, .ledger-card-list li b, .rows li span, .rows li b')]
            .flatMap(node => { const range = document.createRange(); range.selectNodeContents(node); return [...range.getClientRects()]; });
          return { width: document.documentElement.scrollWidth, viewport: innerWidth,
            textOverflow: textRects.some(rect => rect.left < -1 || rect.right > innerWidth + 1),
            cardColumns: grid ? getComputedStyle(grid).gridTemplateColumns.split(' ').length : 0,
            cardGap: grid ? parseFloat(getComputedStyle(grid).rowGap) : null,
            tickerHidden: ticker?.getAttribute('aria-hidden'),
            tickerAnimation: ticker ? getComputedStyle(ticker.querySelector('.mq-track')).animationName : null,
            sticky: intro ? getComputedStyle(intro).position : null,
            photoPosition: el.querySelector('.ledger-visual') ? getComputedStyle(el.querySelector('.ledger-visual')).position : null,
            photo: !!el.querySelector('.ledger-visual img'),
            repeatedLabel: [...el.querySelectorAll('.lab')].some(node => node.textContent.trim() === 'Our menu'),
            storyImage: el.querySelector('.ledger-story-media')?.getBoundingClientRect().toJSON(),
            storyRows: el.querySelector('.ledger-story-content .rows')?.getBoundingClientRect().toJSON(),
            cardsCopy: el.querySelector('.ledger-cards-copy')?.getBoundingClientRect().toJSON(),
            cardsImage: el.querySelector('.ledger-cards-intro .ledger-visual')?.getBoundingClientRect().toJSON(),
            pricesWrap: [...el.querySelectorAll('.rows b.price-short')].some(node => node.getClientRects().length !== 1 || node.scrollWidth > node.clientWidth) };
        });
        assert.ok(result.width <= width + 2, `${move}, ${width}: overflow`);
        assert.equal(result.textOverflow, false, `${move}, ${width}: clipped text`);
        assert.equal(result.photo, hasImage, `${move}, ${width}: assigned image`);
        assert.equal(result.repeatedLabel, false, `${move}, ${width}: duplicate eyebrow`);
        assert.equal(result.pricesWrap, false, `${move}, ${width}: prices fit on one line`);
        if (move === 'story' && hasImage) {
          assert.ok(result.storyImage && result.storyRows, `${width}: story has a separate image and list`);
          if (width === 1440) assert.ok(result.storyImage.left > result.storyRows.right, 'story image sits beside menu');
          else assert.ok(result.storyImage.top >= result.storyRows.bottom, 'story image follows menu on mobile');
        }
        if (move === 'cards') {
          assert.equal(result.cardColumns, width === 1440 ? 3 : 1);
          assert.equal(result.cardGap, width === 1440 ? 24 : 12, `${width}: compact card spacing`);
          if (hasImage) {
            if (width === 1440) assert.ok(result.cardsImage.left >= result.cardsCopy.right, 'card intro photo sits beside its copy on desktop');
            else assert.ok(result.cardsImage.top >= result.cardsCopy.bottom, 'card intro photo follows its copy on mobile');
          }
        }
        if (move === 'marquee') {
          assert.equal(result.tickerHidden, 'true');
          assert.equal(result.tickerAnimation, 'none');
        }
        if (move === 'sticky-product' && hasImage) assert.equal(result.photoPosition, 'static', `${width}: reduced motion photo`);
        await page.close();
      }
    }
  }
  console.log('Ledger variants preserve every item and adapt to screen and motion settings');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
