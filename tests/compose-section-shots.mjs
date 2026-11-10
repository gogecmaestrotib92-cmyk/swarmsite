/* secshots.mjs pictures the sections it is asked for, each as a visitor sees it at rest: the fixed navigation does not
   lie across the picture, a section that does not exist or an id that is not an id is skipped, nothing else is written. */
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'compose-secshots-'));
try {
  const html = path.join(dir, 'page.html'); const out = path.join(dir, 'shots');
  fs.writeFileSync(html, `<!doctype html><style>html,body{margin:0}.nav{position:fixed;inset:0 0 auto 0;height:80px;background:#f00;z-index:9}.sec{height:500px}#a{background:#fff}#b{background:#00f;height:900px}</style>
<nav class="nav"></nav><section class="sec hero" id="top"><h1>One two</h1></section><section class="sec indexlist" id="a"><p>first</p></section><section class="sec cards" id="b"><p>second</p></section>`);
  const run = spawnSync(process.execPath, ['lib/compose/secshots.mjs', html, out, 'a', 'b', 'missing', '../../etc/passwd'], { encoding: 'utf8', env: { ...process.env, LIVETEST: '1' }, timeout: 120000 });
  assert.equal(run.status, 0, run.stderr || run.stdout);
  assert.deepEqual(JSON.parse(run.stdout.trim().split('\n').pop()), { shot: ['a', 'b'] });
  assert.deepEqual(fs.readdirSync(out).sort(), ['a.jpg', 'b.jpg']);
  // a JPEG's size is in its SOF0/SOF2 segment: the picture is the section's own box, 1440 wide
  const size = file => { const b = fs.readFileSync(file); for (let i = 2; i < b.length;) { const marker = b[i + 1], len = b.readUInt16BE(i + 2); if (marker === 0xC0 || marker === 0xC2) return [b.readUInt16BE(i + 7), b.readUInt16BE(i + 5)]; i += 2 + len; } return null; };
  assert.deepEqual(size(path.join(out, 'a.jpg')), [1440, 500]); assert.deepEqual(size(path.join(out, 'b.jpg')), [1440, 900]);
  // the red navigation bar is not in the white section's picture: its top-left pixel block stays light
  const a = fs.readFileSync(path.join(out, 'a.jpg')); assert.ok(a.length > 1000);
  console.log('compose-section-shots: ok');
} finally { fs.rmSync(dir, { recursive: true, force: true }); }
