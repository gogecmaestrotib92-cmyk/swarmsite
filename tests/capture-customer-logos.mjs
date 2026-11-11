/* A page's row of customers' marks is kept as the page drew it, with the words set beside it — and nothing else is
   mistaken for it: not the client's own mark in the bar, not the networks in the footer, not three photographs. */
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-logos-'));
const mark = word => `<svg xmlns="http://www.w3.org/2000/svg" width="${word.length * 15 + 10}" height="30" viewBox="0 0 ${word.length * 15 + 10} 30"><text x="5" y="22" font-family="Arial" font-weight="700" font-size="22">${word}</text></svg>`;
const words = 'A tool that reads the price of a bet before it is placed, for people who follow more than one league and want the same view of each of them every morning.';
const page = row => `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Marks</title></head><body>
  <header><a href="/"><img src="/m/own.svg" width="120" height="30" alt="Own"></a><nav><a href="/pricing">Pricing</a></nav></header>
  <main><h1>The price, read first</h1><p>${words}</p>${row}
  <section><img src="/m/photo.svg" width="700" height="420" alt="A photograph"></section></main>
  <footer><a href="/x"><img src="/m/net1.svg" width="40" height="24" alt="x"></a><a href="/y"><img src="/m/net2.svg" width="40" height="24" alt="y"></a><a href="/z"><img src="/m/net3.svg" width="40" height="24" alt="z"></a><a href="/w"><img src="/m/net4.svg" width="40" height="24" alt="w"></a></footer></body></html>`;
const row = `<section><p>Trusted by 80+ teams</p><div style="display:flex;gap:40px;align-items:center">
  <img src="/m/northwind.svg" width="145" height="30" alt="Northwind"><img src="/m/acme.svg" width="70" height="30" alt="Acme">${mark('Globex').replace('<svg ', '<svg aria-label="Globex" ')}
  <img src="/m/initech.svg" width="115" height="30" alt="Initech"><img src="/m/hooli.svg" width="85" height="30" alt="Hooli"><img src="/m/acme.svg" width="70" height="30" alt="Acme"></div></section>`;
let body = page(row);
const server = http.createServer((req, res) => {
  const m = req.url.match(/^\/m\/([a-z0-9]+)\.svg$/);
  if (m) { res.writeHead(200, { 'content-type': 'image/svg+xml' }); res.end(m[1] === 'photo' ? '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="840"><rect width="1400" height="840" fill="#375"/><circle cx="500" cy="400" r="260" fill="#da3"/></svg>' : mark(m[1])); return; }
  if (req.url !== '/') { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); res.end(body);
});

async function capture() {
  const url = `http://127.0.0.1:${server.address().port}/`;
  const child = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--out', dir, '--no-linked-pictures'], { stdio: ['ignore', 'ignore', 'pipe'] });
  let error = ''; child.stderr.on('data', chunk => { error += chunk; });
  const code = await new Promise((resolve, reject) => { child.on('error', reject); child.on('close', resolve); });
  assert.equal(code, 0, error);
  const slug = url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  return JSON.parse(fs.readFileSync(path.join(dir, slug, 'logos.json'), 'utf8'));
}

try {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const found = await capture();
  assert.deepEqual(found.items.map(i => i.alt).sort(), ['Acme', 'Globex', 'Hooli', 'Initech', 'Northwind'], 'the five marks of the row, the repeated one once, an inline svg among them: ' + JSON.stringify(found.items.map(i => i.alt)));
  assert.ok(found.items.every(i => /^data:image\/svg\+xml/.test(i.data) && i.w >= 36 && i.h >= 12), 'each is kept as drawn, with its size');
  assert.match(found.label, /Trusted by 80\+ teams/, 'the words the page sets with them are kept: ' + found.label);
  body = page('<section><div style="display:flex;gap:40px"><img src="/m/northwind.svg" width="145" height="30" alt="Northwind"><img src="/m/acme.svg" width="70" height="30" alt="Acme"></div></section>');
  const few = await capture();
  assert.deepEqual(few.items, [], 'two marks are not a row of customers, and the networks in the footer are not customers');
  console.log('Capture keeps a page\'s row of customer logos, and only that');
} finally {
  await new Promise(resolve => server.close(resolve));
  fs.rmSync(dir, { recursive: true, force: true });
}
