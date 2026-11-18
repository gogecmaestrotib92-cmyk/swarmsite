// Several instances of the worker share one queue, so the hourly limit of an address is counted where every instance sees it
// (server/limits.mjs), by a key that is not the address.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { ipKey, makeIpLimit } from '../server/limits.mjs';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'), src = fs.readFileSync(path.join(root, 'server/index.mjs'), 'utf8');

// 1 · the limit across instances
{ const k = ipKey('203.0.113.7', 'secret');
  assert.match(k, /^[0-9a-f]{32}$/); assert.equal(k, ipKey('203.0.113.7', 'secret')); assert.notEqual(k, ipKey('203.0.113.8', 'secret')); assert.notEqual(k, ipKey('203.0.113.7', 'other'));
  assert.ok(!k.includes('203'), 'the key is not the address');
  // two instances, one database: a job made through either is counted by both
  const db = []; let clock = 1e12, down = false; const warned = [];
  const inst = () => makeIpLimit({ perHour: 3, secret: 's', now: () => clock, warn: t => warned.push(t),
    countSince: async (key, since) => { if (down) throw new Error('database unreachable'); return db.filter(r => r.key === key && r.at >= Date.parse(since)).length; } });
  const A = inst(), B = inst(), start = async (I, ip) => { if (await I.limited(ip)) return false; db.push({ key: I.key(ip), at: clock }); return true; };
  assert.deepEqual([await start(A, '1.1.1.1'), await start(B, '1.1.1.1'), await start(A, '1.1.1.1')], [true, true, true]);
  assert.equal(await start(B, '1.1.1.1'), false, 'the fourth in an hour is refused by an instance that itself saw only one of them');
  assert.equal(await start(A, '1.1.1.1'), false); assert.equal(await start(B, '2.2.2.2'), true, 'another address is not held back');
  clock += 3601e3; assert.equal(await start(B, '1.1.1.1'), true, 'an hour later the address may start again');
  // the database cannot be asked: each instance falls back to its own count and says so — nobody is turned away for it, and the door is not open
  down = true; const C = inst(); assert.deepEqual([await C.limited('9.9.9.9'), await C.limited('9.9.9.9'), await C.limited('9.9.9.9'), await C.limited('9.9.9.9')], [false, false, false, true]);
  assert.ok(warned.length >= 3 && /this instance only/.test(warned[0]));
  // the server: the limit is the shared one, the key is ours and never the request's, and it does not leave with the job
  assert.ok(/if \(!user && await IP_LIMIT\.limited\(ip\)\)/.test(src) && !/ipHits|rateLimited\(/.test(src), 'POST /jobs asks the shared limit');
  assert.ok(/delete options\.ip_key; if \(!user\) options\.ip_key = IP_LIMIT\.key\(ip\)/.test(src), 'a key sent by the visitor is dropped; ours is set for a visitor not signed in');
  assert.ok(/filter\('options->>ip_key', 'eq', key\)/.test(src) && /\.gte\('created_at', since\)/.test(src));
  assert.ok(/delete data\.options;/.test(src), 'GET /jobs/:id does not hand the options out');
  assert.ok(/ip_key: undefined, url: job\.url/.test(src), 'the old engine\'s brief (a public artefact) does not carry it'); }
console.log('IP limit: counted across every instance of the worker, by a key that is not the address, and never an open door when the database cannot be asked');
