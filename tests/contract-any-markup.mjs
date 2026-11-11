/* The contract reads a page, not one renderer's markup. A page composed from scenes was read as broken where it was not:
   - its headline is sized by a span inside the h1, and was read as 32 px on seven lines;
   - its sections stand inside <main>, and were counted as one;
   - a button whose label is doubled for a hover effect (hidden from readers, named once) was read as saying it twice;
   - a quiet second button counted as a second ask;
   - a link to a place on another page (…/post/#respond) and the bare home address with a trailing # were counted as lost pages;
   - words that stood only on the source's links and buttons ("cart", "close") were counted as lost text.
   And where words ARE lost, the report now names them. */
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-any-markup-'));
const said = 'A kitchen that cooks rice over vine wood for forty guests every evening beside the river. Private celebrations, weddings, baptisms, communions and company dinners are arranged by telephone a fortnight ahead.';
const inventory = {
  url: 'https://example.test/', title: 'Example', lang: 'en',
  copy: { h1: '', text: `SKIP TO NAVIGATION Menu Book ${said} Shopping cart Close Return to shop 1 Comment`, headings: [] }, seo: { title: 'Example' },
  sourceCoverage: { sections: [{ id: 's1', title: 'The kitchen', text: said }], routes: [] },
  actions: [
    { text: 'SKIP TO NAVIGATION', href: 'https://example.test/#nav', region: 'main' }, { text: 'Menu', href: 'https://example.test/menu/', region: 'nav' },
    { text: 'Book', href: 'https://example.test/book/', region: 'nav' }, { text: 'Close', href: 'https://example.test/#', region: 'main' },
    { text: 'Return to shop', href: 'https://example.test/menu/', region: 'main' }, { text: '1 Comment', href: 'https://example.test/news/first/#respond', region: 'footer' },
    { text: 'First news', href: 'https://example.test/news/first/', region: 'footer' },
  ],
};
const section = (id, body) => `<section class="sc" id="${id}"><div class="wrap">${body}</div></section>`;
const page = text => `<!doctype html><html lang="en"><head><title>Example</title><style>
  body{margin:0;font:16px/1.5 sans-serif}.sc{padding:80px 48px}.display{display:block;font-size:150px;line-height:.95}.dv-ln{display:block}
  .btn{display:inline-flex;min-height:54px;padding:0 24px;align-items:center;background:#161;color:#fff}.btn.quiet{background:none;color:inherit}
  .r{position:relative;display:inline-block;overflow:hidden}.r>span{display:block}.r>span+span{position:absolute;left:0;top:100%}img{display:block;width:70%;height:420px;background:#bbb}</style></head><body>
  <header class="bar"><a class="btn" href="https://example.test/book/" aria-label="Book"><span class="r" aria-hidden="true"><span>Book</span><span>Book</span></span></a></header>
  <main>
  <section class="sc open" id="top"><div class="wrap"><h1><span class="display"><span class="dv-ln"><span>Rice over</span></span> <span class="dv-ln"><span>vine wood</span></span></span></h1>
    <a class="btn" href="https://example.test/book/" aria-label="Book"><span class="r" aria-hidden="true"><span>Book</span><span>Book</span></span></a> <a class="btn quiet" href="https://example.test/menu/">Menu</a>
    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1200' height='700'/%3E" alt="" width="1200" height="700"></div></section>
  ${section('a', `<h2>The kitchen</h2><p>${text}</p>`)}${section('b', '<h2>The room</h2><p>Forty guests sit beside the river every evening, at long tables under the vine.</p>')}
  ${section('c', '<h2>The fire</h2><p>Vine wood burns slowly and gives the rice the smoke it is known for in this valley.</p>')}
  ${section('d', '<h2>News</h2><p><a href="https://example.test/news/first/">First news</a> from the kitchen, written when there is something to say.</p>')}
  </main><footer class="sc close"><div class="wrap"><h2>Come by</h2><a class="btn" href="https://example.test/book/">Book</a></div></footer></body></html>`;

function grade(html) {
  const file = path.join(dir, 'page.html'); fs.writeFileSync(file, html);
  fs.writeFileSync(path.join(dir, 'inventory.json'), JSON.stringify(inventory)); fs.writeFileSync(path.join(dir, 'brief.json'), JSON.stringify({ url: inventory.url }));
  const run = spawnSync(process.execPath, ['lib/qa/contract.mjs', file, '--dir', dir], { encoding: 'utf8', timeout: 120000, env: { ...process.env, LIVETEST: '1' } });
  assert.equal(run.status, 0, run.stderr || run.stdout);
  const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json'), 'utf8'));
  return { report, failed: Object.fromEntries(report.failed.map(f => [f.id, f.detail])) };
}

const whole = grade(page(said));
for (const id of ['h1-lines', 'h1-size', 'sections', 'one-cta', 'seo-links-kept', 'seo-text-kept', 'desktop-first-screen-visual'])
  assert.equal(whole.failed[id], undefined, `${id} is read wrongly on a page with other markup: ${whole.failed[id]}`);
assert.equal(whole.report.seo.links.total, 3, 'the menu, the booking page and the news post — not the place on the post, nor the home address with a #');
assert.deepEqual(whole.report.seo.words_lost, ['shopping', 'cart'], 'words that stood only on links and buttons (close, return, shop, comment, navigation) are not lost text; a scrap of the shop\'s own is named, and two words do not fail a page');

const thinned = grade(page('A kitchen.'));
assert.match(thinned.failed['seo-text-kept'] || '', /lost: .*(weddings|baptisms|telephone)/, 'a page that drops the source\'s words fails and names them');
console.log('contract-any-markup ok');
