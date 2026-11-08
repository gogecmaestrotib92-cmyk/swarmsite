import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, headless: true });
try {
  const page = await browser.newPage();
  await page.route('https://source.example/', route => route.fulfill({contentType:'text/html; charset=utf-8', body:`<!doctype html><html><head><meta charset="utf-8"><style>section{min-height:160px}.grid{display:grid}.flex{display:flex;gap:10px}</style></head><body><main><h1>Testimonials</h1><section><h2>Reviews</h2>
    <figure><blockquote>Worth the re<strong>design</strong>, truly.</blockquote><figcaption><span class="grid"><b>Aria Minaei</b>CEO, Theatre.JS</span><span hidden>HIDDEN</span><a href="/story">Read story</a></figcaption></figure>
    <figure><blockquote>Clear <b>and</b> simple.</blockquote><figcaption>O’<strong>Neil</strong>, M.D.<span aria-hidden="true">HIDDEN</span><a href="/review">re<strong>view</strong><span hidden>HIDDEN LINK TEXT</span></a></figcaption></figure>
    <figure><blockquote>A useful tool.</blockquote><figcaption class="flex"><span>Jane</span><span>Founder</span><a href="/jane">Source</a></figcaption></figure>
    <figure><blockquote>Fine work.</blockquote><figcaption><div>John</div><div>Director</div></figcaption></figure>
    <figure><blockquote>Great service.</blockquote><figcaption><span>Riley<br>Designer</span></figcaption></figure>
  </section></main></body></html>`}));
  await page.goto('https://source.example/');
  const inv = await page.evaluate(fs.readFileSync('lib/audit/inventory.js', 'utf8'));
  const quotes = inv.sourceCoverage.sections.find(s=>s.title==='Reviews').testimonials;
  assert.deepEqual(quotes.map(q=>[q.text,q.attribution,q.links[0]?.url]), [
    ['Worth the redesign, truly.','Aria Minaei CEO, Theatre.JS','https://source.example/story'],
    ['Clear and simple.','O’Neil, M.D.','https://source.example/review'],
    ['A useful tool.','Jane Founder','https://source.example/jane'],
    ['Fine work.','John Director',undefined],
    ['Great service.','Riley Designer',undefined],
  ]);
  assert.equal(quotes[1].links[0].label, 'review', 'inline formatting does not split a source link label');
  console.log('Quote attributions preserve visual boundaries and inline typography');
} finally { await browser.close(); }
