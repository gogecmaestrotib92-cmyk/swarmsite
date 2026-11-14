// The capture writes the page as numbered blocks in reading order (lib/audit/blocks.js): what the browser lays out,
// not flat text. The cases are the ones flat text got wrong on real sites: a place's own name inside a sentence and
// again as a later heading, a list of bare labels, a button's word before a sentence, a closed answer, a hidden copy.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-blocks-'));
const PIC = '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500"><rect width="800" height="500" fill="#7a6a55"/><rect x="400" width="400" height="500" fill="#5c4d3c"/></svg>';
const page = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Millbrook Halt</title>
<style>body{margin:0;font:18px/1.5 Arial}section{padding:40px}.btn{display:inline-block;padding:10px 16px;background:#111;color:#fff}.off{display:none}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}</style></head><body>
<div id="cookie-bar"><p>We use cookies to count visits.</p><button>Accept</button></div>
<header><nav><a href="/">Home</a> <a href="/services">Services</a> <a href="/contact">Contact</a></nav></header>
<main>
<section><h1>Millbrook Halt on the old north road</h1>
<p>At the crossing of the old north road stands our stop <strong>Millbrook Halt</strong>. With easy access from the road, its wide building offers every service to the traveller.</p>
<p><a class="btn" href="/contact">Contact us</a></p>
<button aria-label="Play">Play</button>
<p>This stop has a bright building made for rest. Inside there are tables, a cafe, Self Service, a grill and shops with gifts.</p>
<img src="/hall.svg" width="800" height="500" alt="The hall"></section>
<section><h2>Our services</h2><ul><li>Cafe</li><li>Free parking</li><li>Showers</li><li>Self Service</li><li>Baby changing</li></ul></section>
<section><h2>What we offer</h2><div class="cards"><div><h3>Conveyancing</h3><p>A hassle-free service with an instant quote.</p><a href="/conveyancing">Learn more</a></div><div><h3>Wills</h3><p>Specialists in wills and estates.</p><a href="/wills">Learn more</a></div><div><div class="t">Disputes</div><p>We work to settle a dispute quickly.</p></div></div></section>
<section><h2>Millbrook Halt</h2><p>Open every day of the year, from six in the morning.</p><blockquote>The best stop on the road.</blockquote><p class="off">A copy that is not shown.</p>
<details><summary>Is there a shower?</summary><p>Yes, on the ground floor, free for drivers.</p></details></section>
<section><h2><span>Made</span> <span>by</span> <span>hand</span></h2><p style="opacity:0">Shown once the page is scrolled to it.</p>
<p><a class="btn" href="/adults">For adults</a><a class="btn" href="/children">For children</a></p><select><option>April 2019</option><option>March 2011</option></select></section>
</main>
<footer><p>© Millbrook Halt Ltd</p><a href="/privacy">Privacy</a></footer></body></html>`;
const server = http.createServer((req, res) => {
  if (req.url === '/hall.svg') { res.writeHead(200, { 'content-type': 'image/svg+xml' }); res.end(PIC); return; }
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); res.end(page);
});

try {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const url = `http://127.0.0.1:${server.address().port}/`;
  const child = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--out', dir], { stdio: ['ignore', 'ignore', 'pipe'] });
  let error = ''; child.stderr.on('data', chunk => { error += chunk; });
  const code = await new Promise((resolve, reject) => { child.on('error', reject); child.on('close', resolve); });
  assert.equal(code, 0, error);
  const slug = url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  const out = JSON.parse(fs.readFileSync(path.join(dir, slug, 'blocks.json'), 'utf8')), B = out.blocks;
  const find = (kind, re) => B.find(b => b.kind === kind && re.test(b.text));
  assert.ok(B.every((b, n) => b.i === n) && B.every((b, n) => !n || b.y >= B[n - 1].y), 'numbered in reading order, down the page');
  assert.ok(out.covers >= 0.95, `the blocks hold the page's visible words (covers ${out.covers})`);

  const h1 = find('h', /^Millbrook Halt on the old north road$/); assert.equal(h1.level, 1); assert.equal(h1.region, 'main');
  // the place's own name inside a sentence, with emphasis: one paragraph, whole
  const lead = find('p', /^At the crossing/); assert.ok(/stands our stop Millbrook Halt\. With easy access .* to the traveller\.$/.test(lead.text), lead.text);
  // a later heading of the same words is its own block and cut nothing above it
  const later = B.filter(b => b.kind === 'h' && b.text === 'Millbrook Halt'); assert.equal(later.length, 1); assert.equal(later[0].level, 2); assert.ok(later[0].y > lead.y);
  // an item's name inside a sentence stays in the sentence; the list item of the same words is an item
  assert.ok(/a cafe, Self Service, a grill and shops with gifts\.$/.test(find('p', /^This stop has/).text));
  const items = B.filter(b => b.kind === 'li'); assert.deepEqual(items.map(b => b.text), ['Cafe', 'Free parking', 'Showers', 'Self Service', 'Baby changing']); assert.equal(new Set(items.map(b => b.list)).size, 1, 'the labels are one list');
  // a block that is one link or button is a call with its address; a film control's word is its own block, not the start of the next sentence
  const call = find('a', /^Contact us$/); assert.ok(call.href.endsWith('/contact') && call.region === 'main');
  assert.ok(find('a', /^Play$/) && !/^Play /.test(find('p', /^This stop has/).text));
  // cards: a title that is a heading and one that is not; each sentence its own block beside its title
  assert.equal(find('h', /^Conveyancing$/).level, 3); assert.ok(find('p', /^Disputes$/) && find('p', /^We work to settle/));
  assert.ok(Math.abs(find('h', /^Conveyancing$/).y - find('h', /^Wills$/).y) < 4 && find('h', /^Wills$/).x > find('h', /^Conveyancing$/).x, 'cards side by side keep their places');
  assert.equal(find('quote', /best stop/).kind, 'quote');
  // not shown: not there; a closed answer: there, marked folded
  assert.ok(!B.some(b => /not shown/.test(b.text))); assert.equal(find('p', /^Yes, on the ground floor/).folded, true); assert.ok(find('cap', /^Is there a shower\?$/));
  // words set in separate elements keep the space between them; two buttons set side by side are two calls, not one word
  assert.ok(find('h', /^Made by hand$/)); assert.ok(find('a', /^For adults$/) && find('a', /^For children$/));
  // words the page holds faded until the scroll reaches them are there, marked; a closed menu's choices are not the page's words
  assert.equal(find('p', /^Shown once the page/).dim, true); assert.ok(!lead.dim && !B.some(b => /April 2019/.test(b.text)));
  // landmarks
  assert.ok(B.filter(b => b.region === 'nav').map(b => b.text).join(' ').includes('Services') && find('p', /^© Millbrook/).region === 'footer' && B.filter(b => b.region === 'consent').length >= 1);
  assert.ok(!B.some(b => b.region === 'main' && /cookies/.test(b.text)), 'a consent bar is not the page\'s own words');
  // a picture where it stands
  const pic = find('img', /^The hall$/); assert.ok(pic && pic.src.endsWith('/hall.svg') && pic.w >= 400 && pic.y > lead.y);
  // a word said twice as the same kind points at its first standing
  assert.ok(B.filter(b => b.kind === 'a' && b.text === 'Learn more').some(b => b.same !== undefined));
  console.log(`Capture writes the page as ${B.length} numbered blocks in reading order (covers ${out.covers})`);
} finally {
  await new Promise(resolve => server.close(resolve));
  fs.rmSync(dir, { recursive: true, force: true });
}
