// A see-through picture keeps what it shows when the capture stores it as JPEG: dark ink is laid on a white plate,
// light ink on a near-black one. Left alone, its clear parts turn black and dark lettering is gone (owner, 2026-11-13).
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-clear-'));
const svg = ink => `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="600">${Array.from({ length: 6 }, (_, i) => `<rect x="${80 + i * 150}" y="120" width="60" height="360" fill="${ink}"/>`).join('')}</svg>`;
const server = http.createServer((req, res) => {
  if (req.url === '/dark.svg' || req.url === '/light.svg' || req.url === '/solid.svg') {
    res.writeHead(200, { 'content-type': 'image/svg+xml' });
    res.end(req.url === '/solid.svg' ? '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="600"><rect width="1000" height="600" fill="#b46637"/></svg>' : svg(req.url === '/dark.svg' ? '#0a0a0a' : '#f4f4f4'));
    return;
  }
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><html><head><meta charset="utf-8"><title>Local studio</title><style>.visual{width:800px;height:480px;background-size:cover}</style></head><body><nav><a href="/">Home</a></nav><main><h1>Local studio</h1><p>${'A small studio that draws how a thing works, step by step, for people who make tools. '.repeat(8)}</p><h2>How it works</h2><p>${'Each drawing is delivered as a picture with nothing behind it. '.repeat(6)}</p>${['/dark.svg', '/light.svg', '/solid.svg'].map(s => `<div class="visual" style="background-image:url('${s}')"></div>`).join('')}</main></body></html>`);
});

try {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const url = `http://127.0.0.1:${server.address().port}/`;
  const child = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--out', dir], { stdio: ['ignore', 'ignore', 'pipe'] });
  let error = '';
  child.stderr.on('data', chunk => { error += chunk; });
  const code = await new Promise((resolve, reject) => { child.on('error', reject); child.on('close', resolve); });
  assert.equal(code, 0, error);
  const slug = url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  const images = JSON.parse(fs.readFileSync(path.join(dir, slug, 'images.json'), 'utf8'));
  const of = name => images.find(i => i.data && !i.shot && new URL(i.src).pathname === name);
  const dark = of('/dark.svg'), light = of('/light.svg'), solid = of('/solid.svg');
  assert.ok(dark && light && solid, 'the three pictures were captured');
  assert.equal(dark.plate, '#ffffff', 'dark ink on a clear ground is laid on white');
  assert.ok(dark.lum > 150, `dark ink on white is a light picture, not a black one (lum ${dark.lum})`);
  assert.equal(light.plate, '#111111', 'light ink on a clear ground is laid on near-black');
  assert.ok(light.lum < 100, `light ink keeps a dark ground (lum ${light.lum})`);
  assert.equal(solid.plate, undefined, 'a picture with no clear part is left as it is');
  console.log('Capture lays a see-through picture on a plate its ink reads on');
} finally {
  await new Promise(resolve => server.close(resolve));
  fs.rmSync(dir, { recursive: true, force: true });
}
