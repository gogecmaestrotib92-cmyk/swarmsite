// The slots of one instance ask an empty queue once between them, and a burst of jobs is taken at once (server/poll.mjs).
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { makeClaimer } from '../server/poll.mjs';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'), src = fs.readFileSync(path.join(root, 'server/index.mjs'), 'utf8');

// 2 · the slots of one instance and the queue
{ let calls = 0, queue = 0; const sleep = ms => new Promise(r => setTimeout(r, ms));
  const C = makeClaimer({ idleMs: 60, claim: async () => { calls++; await sleep(3); return queue > 0 ? { id: queue-- } : null; } });
  const got = []; const slots = Array.from({ length: 8 }, async () => { got.push({ job: await C.next(), at: Date.now() }); });
  await sleep(400);
  assert.ok(calls >= 4 && calls <= 9, `an empty queue is asked once an interval by the instance, not by each of 8 slots: ${calls} questions in 400 ms of 60 ms intervals`);
  assert.equal(got.length, 0);
  queue = 8; const t = Date.now(); await Promise.all(slots);
  const late = Math.max(...got.map(g => g.at)) - t;
  assert.equal(new Set(got.map(g => g.job.id)).size, 8); assert.ok(late < 60 + 150, `eight jobs arriving together are all taken within about one interval, not one an interval: ${late} ms`);
  // a claim that fails is the caller's to hear of, and the next question is not blocked for ever
  let fail = true; const D = makeClaimer({ idleMs: 20, claim: async () => { if (fail) { fail = false; throw new Error('rpc down'); } return { id: 1 }; } });
  await assert.rejects(D.next(), /rpc down/); assert.deepEqual(await D.next(), { id: 1 });
  assert.ok(/const claimed = await CLAIMER\.next\(\);/.test(src) && src.indexOf('const CLAIMER = makeClaimer(') > src.indexOf('\nasync function loop()'), 'the worker\'s loop asks through it (and it stands after the loop: tests cut the source before it)'); }
console.log('Queue: one question to an empty queue for all the slots of an instance, and a burst taken as fast as the claims answer');
