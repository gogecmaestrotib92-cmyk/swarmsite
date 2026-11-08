import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, headless: true });
try {
  const page = await browser.newPage();
  await page.route('https://source.example/', route => route.fulfill({contentType:'text/html', body:`<!doctype html><html lang="en"><head><title>Evidence</title><style>section{min-height:130px}</style></head><body>
    <nav><figure><blockquote>Navigation is not a review.</blockquote><figcaption>Not a customer</figcaption></figure></nav>
    <main><h1>Real source</h1>
      <section><h2>Customer stories</h2>
        <button id="customer1" aria-expanded="false" onclick="window.clicked = true">Customer One</button>
        <div role="region" id="case1" aria-labelledby="customer1" hidden>Reduced <b>10M+</b><span>calls</span><a href="/customers/one">Read story</a><script>excluded()</script><form>excluded private form</form></div>
        <button aria-expanded="false" aria-controls="case2" onclick="window.clicked = true">Customer Two</button>
        <div id="case2" hidden>Saved time <a href="javascript:alert(1)">bad URL</a><a href="https://outside.example/story">External story</a></div>
        <button aria-expanded="false" aria-controls="not-loaded">Not loaded</button>
        <button aria-expanded="false" aria-controls="duplicate">Ambiguous</button><div id="duplicate">First</div><div id="duplicate">Second</div>
      </section>
      <section><h2>Customer quotes</h2>
        <figure><blockquote>First <b>full</b> review<span aria-hidden="true">DEMO TEXT</span><span style="display:none">HIDDEN TEXT</span></blockquote><figcaption><span>Alice</span><span aria-hidden="true">DEMO AUTHOR</span><a href="/reviews/alice">Original review</a></figcaption></figure>
        <figure><blockquote>Second full review</blockquote><figcaption><span>Bob</span><a href="https://outside.example/bob">Original review</a></figcaption></figure>
        <figure hidden><blockquote>Hidden review</blockquote><figcaption>Hidden person</figcaption></figure>
        <figure><div><blockquote>Carousel visible</blockquote><figcaption>Visible person</figcaption></div><div aria-hidden="true"><blockquote>Carousel hidden</blockquote><figcaption>Hidden person</figcaption></div></figure>
        <figure><blockquote>Ambiguous one</blockquote><blockquote>Ambiguous two</blockquote><figcaption>Do not guess</figcaption></figure>
        <figure><blockquote>${'x'.repeat(2100)}</blockquote><figcaption>Long source</figcaption></figure>
      </section>
    </main></body></html>`}));
  await page.goto('https://source.example/');
  const inv = await page.evaluate(fs.readFileSync('lib/audit/inventory.js','utf8'));
  const stories = inv.sourceCoverage.sections.find(s=>s.title==='Customer stories');
  assert.deepEqual(stories.panels.map(p=>[p.trigger,p.status,p.association]), [
    ['Customer One','candidate','aria-labelledby'], ['Customer Two','candidate','aria-controls'],
    ['Not loaded','unavailable',null], ['Ambiguous','unavailable',null],
  ]);
  assert.match(stories.panels[0].text,/Reduced 10M\+ calls Read story/);
  assert.doesNotMatch(stories.panels[0].text,/excluded/);
  assert.deepEqual(stories.panels[0].links,[{label:'Read story',url:'https://source.example/customers/one'}]);
  assert.deepEqual(stories.panels[1].links,[{label:'External story',url:'https://outside.example/story'}]);
  assert.equal(await page.evaluate(()=>!!window.clicked),false,'no source controls are clicked');
  const quotes = inv.sourceCoverage.sections.find(s=>s.title==='Customer quotes').testimonials;
  assert.equal(quotes.length,4,'hidden or ambiguous reviews are never paired');
  assert.deepEqual(quotes.slice(0,3).map(q=>[q.text,q.attribution,q.links[0]?.url]),[
    ['First full review','Alice','https://source.example/reviews/alice'],
    ['Second full review','Bob','https://outside.example/bob'],
    ['Carousel visible','Visible person',undefined],
  ]);
  assert.equal(quotes[3].textTruncated,true,'the source evidence is explicitly marked when truncated');
  assert.ok(quotes.every(q=>q.status==='candidate'));
  console.log('Source review candidates and closed panels retain exact provenance without triggering controls');
} finally { await browser.close(); }
