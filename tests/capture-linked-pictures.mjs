/* A site keeps its photographs behind its first page, and names larger files than the ones it loads.
   On production a restaurant's landing page gave four pictures — a funding notice, one soft background and two frames
   of films — while its rooms were photographed on the pages it links to. The capture of a landing page now:
   - takes the largest file an <img> names: the widest srcset entry, a lazy loader's data-src, the original behind a
     WordPress thumbnail name (hall-300x200 → hall);
   - opens a few linked pages of the same site FOR THEIR PICTURES ONLY (never a legal page or a cart), and nothing of
     their text enters the inventory;
   - marks a notice as not a photograph, and does not take the same file twice under another query string. */
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-linked-'));
const photo = (w, h, hue) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">${Array.from({ length: 9 }, (_, k) => `<stop offset="${k / 8}" stop-color="hsl(${(hue + k * 37) % 360} 70% ${25 + k * 6}%)"/>`).join('')}</linearGradient></defs><rect width="${w}" height="${h}" fill="url(#g)"/>${Array.from({ length: 30 }, (_, k) => `<circle cx="${(k * 97) % w}" cy="${(k * 61) % h}" r="${20 + k * 3}" fill="hsl(${(hue + k * 23) % 360} 60% 50%)" opacity=".5"/>`).join('')}</svg>`;
const notice = '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="700"><rect width="900" height="700" fill="#fff"/><rect x="60" y="80" width="500" height="14" fill="#555"/><rect x="60" y="130" width="640" height="10" fill="#777"/></svg>';
const night = '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="680"><rect width="1600" height="680" fill="#0b0b0d"/><path d="M0 300 L800 180 L1600 300" stroke="#3a3a3a" stroke-width="26" fill="none"/><circle cx="800" cy="120" r="60" fill="#8a8a8a"/></svg>';   // a stadium at night: nearly all of it two dark tones
const opened = [];
const server = http.createServer((req, res) => {
  const url = req.url.split('?')[0]; const m = url.match(/^\/img\/([a-z]+?)(-(\d+)x(\d+))?\.svg$/);
  if (m) { res.writeHead(200, { 'content-type': 'image/svg+xml' }); const hue = { hall: 20, terrace: 140, cellar: 260, dish: 320, room: 60, bar: 200 }[m[1]] ?? 0;
    res.end(m[1] === 'notice' ? notice : m[1] === 'night' ? night : photo(m[3] ? +m[3] : 1600, m[4] ? +m[4] : 1000, hue)); return; }
  opened.push(url);
  const words = 'A restaurant by the river with a hall, a terrace and a cellar. We cook rice over vine wood for forty guests every evening and open the terrace from May to October for long lunches.';
  const pages = {
    '/': `<nav><a href="/rooms">Our rooms</a><a href="/legal">Legal notice</a><a href="/cart">Cart</a><a href="/news?page=2">News</a></nav><main><h1>The river restaurant</h1><p>${words}</p>
      <img src="/img/hall-300x200.svg" width="300" height="200" alt="The hall">
      <img src="/img/terrace-320x200.svg" srcset="/img/terrace-320x200.svg 320w, /img/terrace.svg 1600w" sizes="320px" width="320" height="200" alt="The terrace">
      <img src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" data-src="/img/cellar.svg" width="320" height="200" alt="The cellar">
      <img src="/img/notice.svg" width="900" height="700" alt=""><img src="/img/night.svg" width="800" height="340" alt="The stadium at night"><div style="width:600px;height:300px;background-image:url('/img/hall.svg?v=2')"></div></main>`,
    '/rooms': `<main><h1>Our rooms</h1><p>${words} The private room seats twelve and the bar opens at noon.</p><img src="/img/room.svg" width="800" height="500" alt="The private room"><img src="/img/bar.svg" width="800" height="500" alt="The bar"><img src="/img/hall.svg" width="800" height="500" alt="The hall again"></main>`,
    '/legal': `<main><h1>Legal</h1><p>${words}</p><img src="/img/dish.svg" width="800" height="500" alt=""></main>`,
  };
  if (!pages[url]) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); res.end(`<!doctype html><html lang="en"><head><meta charset="utf-8"><title>River restaurant</title></head><body>${pages[url]}</body></html>`);
});

try {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const url = `http://127.0.0.1:${server.address().port}/`;
  const child = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--out', dir], { stdio: ['ignore', 'ignore', 'pipe'] });
  let error = ''; child.stderr.on('data', chunk => { error += chunk; });
  const code = await new Promise((resolve, reject) => { child.on('error', reject); child.on('close', resolve); });
  assert.equal(code, 0, error);
  const slug = url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  const images = JSON.parse(fs.readFileSync(path.join(dir, slug, 'images.json'), 'utf8')).filter(i => i.data && !i.shot);
  const inventory = JSON.parse(fs.readFileSync(path.join(dir, slug, 'inventory.json'), 'utf8'));
  const by = name => images.filter(i => new URL(i.src).pathname === `/img/${name}.svg`);
  for (const name of ['hall', 'terrace', 'cellar']) { assert.equal(by(name).length, 1, `${name}: the large file is taken once: ` + JSON.stringify(images.map(i => i.src))); assert.ok(by(name)[0].w >= 1400, `${name} is taken at the size of its largest file, not of the thumbnail the page loaded (${by(name)[0].w} px)`); }
  assert.ok(by('notice')[0]?.plain, 'a notice on white is marked as not a photograph');
  assert.ok(!by('hall')[0].plain && !by('terrace')[0].plain, 'a photograph is not marked plain');
  assert.ok(by('night')[0] && !by('night')[0].plain, 'a dark photograph is a photograph: only a LIGHT flat picture is a notice (' + JSON.stringify(by('night')[0] && { flat: by('night')[0].flat, lum: by('night')[0].lum }) + ')');
  assert.deepEqual(images.filter(i => /^p\d+-img/.test(i.id)).map(i => new URL(i.src).pathname).sort(), ['/img/bar.svg', '/img/room.svg'], 'the linked page gives its own photographs, and not the one the landing page already had');
  assert.ok(images.find(i => i.id === 'p1-img1')?.page, 'a picture from a linked page says which page it stood on');
  assert.ok(!opened.includes('/legal') && !opened.includes('/cart') && !opened.includes('/news'), 'a legal page, a cart and a listing with a query are not opened for pictures: ' + opened);
  assert.equal(inventory.sourceCoverage.scope, 'landing_page_only'); assert.deepEqual(inventory.sourcePages, [], 'nothing of a linked page\'s text enters the inventory');
  assert.ok(!JSON.stringify(inventory.copy).includes('private room seats twelve'));
  assert.equal(new Set(images.map(i => i.id)).size, images.length, 'picture ids are unique');
  console.log('Capture of a landing page takes the largest files and the photographs of the pages it links to');
} finally {
  await new Promise(resolve => server.close(resolve));
  fs.rmSync(dir, { recursive: true, force: true });
}
