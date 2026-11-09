/* "Every internal link kept" must count the links a redesign can lose — pages of the same site — and count them right.
   Two things made the promise read as broken on real jobs when nothing was lost:
   - an anchor on the source page itself (https://site/#faq) is not a page and has no place on a rebuilt page;
   - a link with a query string is written &amp; in HTML and must be compared decoded. */
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-seo-links-'));
const words = 'Coaching software for basketball teams. Draw plays, share them with the roster and review film together after every game.';
const inventory = {
  url: 'https://example.test/', title: 'Example', lang: 'en',
  copy: { h1: 'Coaching software for basketball teams', text: words, headings: [{ tag: 'H1', text: 'Coaching software for basketball teams' }] },
  seo: { title: 'Example' },
  sourceCoverage: { sections: [{ id: 'home-1', title: 'Coaching software for basketball teams', text: words }], routes: [] },
  actions: [
    { text: 'Features', href: 'https://www.example.test/#features', region: 'nav' },          // an anchor on the source page itself
    { text: 'FAQ', href: 'https://example.test/#faq', region: 'nav' },                        // the same, without www
    { text: 'Skip to content', href: 'https://example.test/#content', region: 'main' },
    { text: 'Pricing', href: 'https://example.test/pricing', region: 'nav' },
    { text: 'Start', href: 'https://example.test/register?plan=pro&billing=monthly', region: 'main' },
    { text: 'Comments', href: 'https://example.test/blog/first-post#comments', region: 'main' },  // another page, with a fragment: a real link
    { text: 'About', href: 'https://example.test/about/', region: 'footer' },
    { text: 'Elsewhere', href: 'https://other.test/partner', region: 'footer' },              // another site: not ours to keep
  ],
};
const page = about => `<!doctype html><html lang="en"><head><title>Example</title><style>section{padding:40px}a.btn{display:inline-block;padding:10px}</style></head><body>
  <nav class="nav"><a href="#features">Features</a><a class="btn" href="https://example.test/register?plan=pro&amp;billing=monthly">Start</a></nav>
  <section class="sec hero" id="top"><h1>Coaching software for basketball teams</h1><p>${words}</p><a class="btn" href="https://example.test/register?plan=pro&amp;billing=monthly">Start</a></section>
  <section class="sec" id="features"><h2>Draw plays</h2><p>${words}</p><a href="https://example.test/pricing">Pricing</a> <a href="https://example.test/blog/first-post#comments">Comments</a>${about ? ' <a href="https://example.test/about">About</a>' : ''}</section>
  </body></html>`;

function grade(html) {
  const file = path.join(dir, 'page.html'); fs.writeFileSync(file, html);
  fs.writeFileSync(path.join(dir, 'inventory.json'), JSON.stringify(inventory)); fs.writeFileSync(path.join(dir, 'brief.json'), JSON.stringify({ url: inventory.url }));
  const run = spawnSync(process.execPath, ['lib/qa/contract.mjs', file, '--dir', dir], { encoding: 'utf8', timeout: 120000, env: { ...process.env, LIVETEST: '1' } });
  assert.equal(run.status, 0, run.stderr || run.error?.message);
  return JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
}

try {
  const kept = grade(page(true));
  const item = kept.items.find(x => x.id === 'seo-links-kept');
  assert.ok(item, 'the SEO-safe promises are graded by default');
  assert.equal(item.ok, true, item.detail);
  assert.equal(item.detail, '4/4 internal links kept', 'pricing, register (decoded), the blog post and about — not the three same-page anchors, not the other site');
  assert.deepEqual(kept.seo.links, { total: 4, kept: 4, lost: [] });

  const lost = grade(page(false));
  const failed = lost.failed.find(x => x.id === 'seo-links-kept');
  assert.ok(failed, 'a page of the site that the rebuild dropped is still a broken promise');
  assert.equal(failed.detail, '3/4 internal links kept');
  assert.deepEqual(lost.seo.links.lost, ['https://example.test/about'], 'the report names the page that was dropped');
  console.log('Internal links: same-page anchors are not links to keep, escaped query strings match, a dropped page is still caught');
} finally { fs.rmSync(dir, { recursive: true, force: true }); }
