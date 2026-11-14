// The ring under the working screen's heading (web/js/progress.js): how far a job is, by the time each step usually
// takes — and what the worker tells the page those times are (typicalOf, server/templates.mjs).
import assert from 'node:assert/strict'; import { createRequire } from 'node:module'; import fs from 'node:fs'; import path from 'node:path';
import { typicalOf, STEPS_T, STEPS_F } from '../server/templates.mjs';
const P = createRequire(import.meta.url)('../web/js/progress.js'), now = Date.parse('2026-11-14T10:00:00Z');
const job = (rows, status = 'running') => ({ status, steps: rows.map(([id, st, ago = 0]) => ({ id, status: st, at: new Date(now - ago * 1000).toISOString() })) });
const T = ['capture', 'read', 'choose', 'publish', 'package'], at = (i, ago) => job(T.map((id, k) => [id, k < i ? 'done' : k === i ? 'running' : 'pending', k === i ? ago : 0]));
const typ = { capture: 80, read: 20, choose: 80, publish: 20, package: 120 };   // the ring's whole is 200 s: up to the designs being shown

assert.deepEqual(P.of(job(T.map(id => [id, 'pending'])), typ, now), { pct: 0, done: false }, 'a job in the queue has not begun');
assert.equal(P.of(at(0, 40), typ, now).pct, 18, 'half the usual time of the first step: nine tenths of half its share');
assert.equal(P.of(at(1, 0), typ, now).pct, 40, 'a finished step counts whole');
assert.equal(P.of(at(2, 80), typ, now).pct, 86); assert.equal(P.of(at(3, 10), typ, now).pct, 94);
// a step that takes longer than usual creeps and never reaches its whole; the ring says 100 only when the designs are there
const slow = [80, 160, 600, 6000].map(s => P.of(at(0, s), typ, now).pct); assert.ok(slow.every((p, i) => i === 0 || p >= slow[i - 1]) && slow[0] === 36 && slow.at(-1) < 40, 'a slow step: ' + slow);
assert.ok(P.of(at(3, 100000), typ, now).pct === 99, 'never 100 before the work is done');
assert.deepEqual(P.of(at(4, 5), typ, now), { pct: 100, done: true }, 'the designs are shown once they are published: the downloads are not waited for');
assert.deepEqual(P.of(job(T.map(id => [id, 'done']), 'done'), typ, now), { pct: 100, done: true });
// what the worker does not say, the page's own figures stand in for; a step neither knows weighs as the others do; no clock, no guess
for (const [id] of [...STEPS_T, ...STEPS_F]) assert.ok(P.TYPICAL[id] > 0, id + ' has a usual time on the page');
assert.equal(P.of(at(0, 77), {}, now).pct, Math.floor(100 * .9 * 77 / (77 + 19 + 68 + 11)));
assert.equal(P.of({ status: 'running', steps: [{ id: 'a', status: 'done' }, { id: 'b', status: 'running' }, { id: 'c', status: 'pending' }] }, {}, now).pct, 33);
assert.deepEqual(P.of({ status: 'running', steps: [] }, typ, now), { pct: 0, done: false });
// the worker's usual times: medians of finished jobs' own timings; a step that did not run (0) or was read fewer than three times says nothing
assert.deepEqual(typicalOf([{ capture: 49000, read: 16000 }, { capture: 85000, read: 17000, form: 0 }, { capture: 79000, read: 23000, choose: 100000 }, null, { capture: 90000, 'bad id': 5000 }]), { capture: 82, read: 17 });
assert.deepEqual(typicalOf([]), {}); assert.deepEqual(typicalOf(null), {});
// the page carries the ring and its script, and draws it from the job it polls
const html = fs.readFileSync(path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'web', 'app.html'), 'utf8');
assert.ok(/id="ring"[^>]*role="progressbar"|role="progressbar"[^>]*id="ring"/.test(html.replace(/\n/g, ' ')) || /<div class="ring" id="ring" role="progressbar"/.test(html)); assert.ok(html.includes('<script src="/js/progress.js"></script>') && html.includes('Progress.of(job'));
console.log('Progress ring: by the usual time of each step, never back, never 100 before the designs; the worker\'s medians');
