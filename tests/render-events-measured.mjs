/* The progress lines shown after a page is built are read off that page. Three of them used to be fixed sentences
   ("type scale set · h1 clamp(52px, 7.4vw, 124px)", "ending + contact written", "lenis on") whatever was built. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const source = fs.readFileSync('server/index.mjs', 'utf8');
const start = source.indexOf('function eventsRender(dir)'); const end = source.indexOf('function eventsQA(', start);
assert.ok(start > 0 && end > start, 'eventsRender not found in server/index.mjs');
const eventsRender = new Function('fs', 'path', source.slice(start, end) + '; return eventsRender;')(fs, path);

for (const fixed of ['type scale set', 'clamp(52px, 7.4vw, 124px)', 'ending + contact written', 'lenis on']) assert.ok(!source.slice(start, end).includes(fixed), `fixed sentence still in eventsRender: ${fixed}`);

// a real page from the renderer, on two blueprints with different display faces
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'events-'));
for (const name of ['direction', 'images', 'inventory', 'assets']) fs.copyFileSync(`tests/${name}.sample.json`, path.join(dir, `${name}.json`));
const seen = {};
for (const blueprint of ['butter', 'tengile']) {
  execFileSync('python3', ['lib/render/render_bp.py', dir, blueprint, path.join(dir, 'index.html')], { env: { ...process.env, LIVETEST: '1' } });
  const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
  const events = eventsRender(dir); const text = role => events.filter(e => e.role === role).map(e => e.text);
  const face = html.match(/--display:'([^']+)'/)[1];
  assert.ok(text('Type').some(t => t.includes(face)), `${blueprint}: the type line names the face on the page (${face}): ${JSON.stringify(text('Type'))}`);
  const pictures = (html.match(/<img /g) || []).length;
  assert.ok(text('Photos').some(t => t.startsWith(`${pictures} picture`)), `${blueprint}: picture count ${pictures}: ${JSON.stringify(text('Photos'))}`);
  const sections = (html.match(/<section[\s>]/g) || []).length;
  assert.ok(text('Render').includes(`${sections} sections built`), `${blueprint}: section count ${sections}`);
  assert.ok(text('Render').some(t => t.startsWith(`page ${Math.round(html.length / 1024)} KB`)), `${blueprint}: page weight`);
  assert.equal(text('Render').some(t => t.includes('smooth scroll on')), /<script src="[^"]*lenis/i.test(html), `${blueprint}: smooth scroll is reported only when its script is on the page`);
  for (const t of text('Motion')) assert.ok(/^moves: [a-z0-9-]+(, [a-z0-9-]+)*$/.test(t), `${blueprint}: only real move names: ${t}`);
  for (const e of events) { assert.ok(typeof e.role === 'string' && typeof e.text === 'string' && e.text.length <= 140, 'every event is a short role + text'); }
  seen[blueprint] = text('Type')[0];
}
assert.notEqual(seen.butter, seen.tengile, 'two blueprints with different faces produce different type lines');

// nothing to read: no invented lines
fs.rmSync(path.join(dir, 'index.html'));
const empty = eventsRender(dir);
assert.deepEqual(empty.map(e => e.role), ['Photos', 'Render']); assert.equal(empty[0].text, '0 pictures placed'); assert.equal(empty[1].text, 'page 0 KB');
fs.rmSync(dir, { recursive: true, force: true });
console.log('render events are measured');
