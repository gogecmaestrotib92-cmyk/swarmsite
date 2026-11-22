// A picture the page carries inside itself (a data: address) is a picture like any other: a Persian school's only
// photograph was one and the capture read none, so its three designs were flat colour and words (a visitor's job,
// 2026-11-22). An <img> with no data-src must not be read as the page's own address either.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-inline-'));
// a photograph-like picture: many tones, made once in a browser and sent inline as a webp
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
const photo = await (await b.newPage()).evaluate(() => { const c = document.createElement('canvas'); c.width = 1600; c.height = 900; const g = c.getContext('2d');
  for (let i = 0; i < 400; i++) { g.fillStyle = `hsl(${(i * 37) % 360},${40 + i % 40}%,${25 + (i * 7) % 50}%)`; g.fillRect((i * 97) % 1600, (i * 53) % 900, 140, 90); } return c.toDataURL('image/webp', .8); });
await b.close();
const server = http.createServer((req, res) => {
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><title>Amal</title><style>img{width:1100px;height:auto;display:block}</style></head><body>
<header><a href="#/">Amal</a></header><main><h1>Focus, path, persistence</h1><p>A study camp and course advice in Shiraz for students who want to reach their goals.</p>
<img src="${photo}" alt="A student with headphones at a desk, a city beyond the window"></main></body></html>`);
});
try {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${server.address().port}/`;
  const child = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--out', dir, '--chrome', process.env.CHROME_PATH || ''], { stdio: ['ignore', 'ignore', 'pipe'] });
  let error = ''; child.stderr.on('data', d => { error += d; });
  const code = await new Promise(r => child.on('close', r));
  assert.equal(code, 0, error.slice(-800));
  const slug = fs.readdirSync(dir)[0];
  const images = JSON.parse(fs.readFileSync(path.join(dir, slug, 'images.json'), 'utf8')).filter(i => !i.shot);
  const own = images.find(i => /^inline:/.test(i.src));
  assert.ok(own && own.data && own.w >= 1000, 'the inline photograph is taken, with its pixels: ' + JSON.stringify(images.map(i => ({ src: String(i.src).slice(0, 40), w: i.w, data: !!i.data }))));
  assert.ok(!images.some(i => i.src === url), 'no picture is named by the page\'s own address');
  console.log('A picture the page carries inside itself is taken like any other, named by a fingerprint of its bytes');
} finally { server.close(); }
