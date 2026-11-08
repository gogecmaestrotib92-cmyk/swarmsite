import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-images-'));
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/missing/')) {
    res.writeHead(404); res.end(); return;
  }
  if (req.url.startsWith('/image/')) {
    res.writeHead(200, { 'content-type': 'image/svg+xml' });
    res.end('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="600"><rect width="1000" height="600" fill="#b46637"/></svg>');
    return;
  }
  const sources = req.url === '/details'
    ? ['/image/details.svg']
    : [...Array.from({ length: 9 }, (_, i) => `/missing/${i}.jpg`), ...Array.from({ length: 12 }, (_, i) => `/image/${i}.svg`)];
  const images = sources.map(src => `<div class="visual${src.startsWith('/missing/') ? ' missing' : ''}" style="background-image:url('${src}')"></div>`).join('');
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><html><head><meta charset="utf-8"><title>Local cafe</title><style>.visual{width:800px;height:240px;background-size:cover}.missing{height:10px}</style></head><body><nav><a href="/details">Product details</a></nav><main><h1>Our local cafe</h1><p>Visit our friendly neighbourhood cafe for fresh food and drinks. Our team serves breakfast and lunch each day with locally sourced ingredients and offers seasonal specials for everyone to enjoy.</p>${images}</main></body></html>`);
});

try {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const url = `http://127.0.0.1:${server.address().port}/`;
  const child = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--site-wide', '--out', dir], { stdio: ['ignore', 'ignore', 'pipe'] });
  let error = '';
  child.stderr.on('data', chunk => { error += chunk; });
  const code = await new Promise((resolve, reject) => { child.on('error', reject); child.on('close', resolve); });
  assert.equal(code, 0, error);
  const slug = url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  const images = JSON.parse(fs.readFileSync(path.join(dir, slug, 'images.json'), 'utf8'));
  const successful = images.filter(image => image.data);
  const urls = successful.filter(image => !image.shot).map(image => new URL(image.src).pathname);
  for (let i = 0; i < 12; i++) assert.ok(urls.includes(`/image/${i}.svg`), `missing source image ${i}`);
  assert.ok(urls.includes('/image/details.svg'), 'missing subpage source image');
  assert.ok(successful.filter(image => image.shot).length < 12, 'source images were redundantly captured as screenshots');
  assert.equal(new Set(images.map(image => image.id)).size, images.length, 'image IDs must be unique');
  console.log('Capture keeps later source images despite earlier failures and includes subpage visuals');
} finally {
  await new Promise(resolve => server.close(resolve));
  fs.rmSync(dir, { recursive: true, force: true });
}
