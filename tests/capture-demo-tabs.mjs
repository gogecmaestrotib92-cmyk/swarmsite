// A product page that shows its product behind tabs (role="tablist" over a framed panel) gives one screen for each tab,
// each different, cut to the screen's own box, with the line the page sets under it as its caption — and the page's
// sticky bar is not in the picture. (A coaching product showed six screens behind tabs and we took one: 2026-11-15.)
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-tabs-'));
const screen = (name, hue) => `<div role="tabpanel" id="p-${name}" ${name === 'Plays' ? '' : 'hidden'}><div class="scr" style="background:linear-gradient(135deg,hsl(${hue} 60% 22%),hsl(${hue + 40} 70% 12%))"><b>${name} board</b><table><tr><td>12</td><td>34</td><td>56</td></tr><tr><td>7</td><td>8</td><td>9</td></tr></table><button>Run</button></div><p class="cap">The ${name.toLowerCase()} of the week, in one place.</p></div>`;
const names = ['Plays', 'Practice', 'Scouting', 'Video'];
const page = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Courtline</title>
<style>body{margin:0;font:17px/1.5 Arial;background:#fff}header{position:sticky;top:0;background:#fa0;height:60px;z-index:9}section{padding:60px 120px}
.demo{width:900px;margin:0 auto}[role=tablist]{display:flex;gap:8px;height:44px}[role=tab]{padding:8px 14px}.scr{width:900px;height:520px;border-radius:14px;color:#fff;padding:24px;box-sizing:border-box}.scr b{font-size:40px}.cap{margin:8px 0 0}</style></head><body>
<header>Courtline — sticky bar</header>
<main><section><h1>Courtline keeps a coaching staff on one page</h1><p>Draw the play once, link the film to it, and take the plan to practice. Everything a staff prepares in a week stays together, and nothing is rebuilt for the next opponent.</p><p>It runs in a browser, on the bus and in the gym, and every coach sees the same board.</p></section>
<section><h2>Inside Courtline</h2><div class="demo"><div role="tablist">${names.map((n, i) => `<button role="tab" aria-controls="p-${n}" aria-selected="${i === 0}">${n}</button>`).join('')}</div>${names.map((n, i) => screen(n, i * 70)).join('')}</div></section>
<section><h2>What a week looks like</h2><p>Monday the film, Tuesday the plan, Friday the bench sheet. The staff works from the same page all week and prints what the players need.</p></section></main>
<script>document.querySelectorAll('[role=tab]').forEach(t => t.addEventListener('click', () => { document.querySelectorAll('[role=tab]').forEach(x => x.setAttribute('aria-selected', x === t)); document.querySelectorAll('[role=tabpanel]').forEach(p => p.hidden = p.id !== t.getAttribute('aria-controls')); }));</script></body></html>`;
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); res.end(page); });
try {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const url = `http://127.0.0.1:${server.address().port}/`;
  const child = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--out', dir], { stdio: ['ignore', 'ignore', 'pipe'] });
  let error = ''; child.stderr.on('data', chunk => { error += chunk; });
  const code = await new Promise((resolve, reject) => { child.on('error', reject); child.on('close', resolve); });
  assert.equal(code, 0, error);
  const slug = url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  const images = JSON.parse(fs.readFileSync(path.join(dir, slug, 'images.json'), 'utf8'));
  const tabs = images.filter(i => String(i.id).startsWith('tab'));
  assert.deepEqual(tabs.map(t => t.state), names, 'one screen for each tab of the demo, in its order');
  assert.ok(tabs.every(t => t.shot && t.w === 900 && t.h === 520), 'cut to the screen\'s own box: ' + JSON.stringify(tabs.map(t => [t.w, t.h])));
  assert.ok(tabs.every((t, i) => t.caption === `The ${names[i].toLowerCase()} of the week, in one place.`), 'the line the page sets under a screen is its caption: ' + JSON.stringify(tabs.map(t => t.caption)));
  assert.equal(new Set(tabs.map(t => t.data)).size, names.length, 'each a different picture');
  console.log(`Capture takes one screen for each of the ${tabs.length} tabs of a product demo, with its caption`);
} finally {
  await new Promise(resolve => server.close(resolve));
  fs.rmSync(dir, { recursive: true, force: true });
}
