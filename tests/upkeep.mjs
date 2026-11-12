// Upkeep of the template path's private bucket, with stubbed clients: on boot the bucket must exist and be private
// (created when missing; templates mode refused when it is public), and visitors' uploaded photographs are removed
// once their job is 14 days old and nobody's — logged as counts only.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { ensurePrivateBucket } from '../server/bucket.mjs';
import { removals, runCleanup, named, DAYS } from '../server/cleanup.mjs';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');

// 1 · the bucket
const storage = buckets => { const made = []; return { made, getBucket: async n => buckets[n] ? { data: buckets[n], error: null } : { data: null, error: { message: 'Bucket not found' } },
  createBucket: async (n, o) => { made.push([n, o]); buckets[n] = { name: n, public: o.public }; return { data: { name: n }, error: null } } }; };
let log = []; let s = storage({ packages: { name: 'packages', public: false } });
assert.deepEqual(await ensurePrivateBucket(s, 'packages', t => log.push(t)), { ok: true, created: false }); assert.deepEqual(log, ['bucket packages ok']); assert.deepEqual(s.made, []);
log = []; s = storage({});
assert.deepEqual(await ensurePrivateBucket(s, 'packages', t => log.push(t)), { ok: true, created: true }); assert.deepEqual(s.made, [['packages', { public: false }]]); assert.deepEqual(log, ['bucket packages created']);
log = []; s = storage({ packages: { name: 'packages', public: true } });
assert.deepEqual(await ensurePrivateBucket(s, 'packages', t => log.push(t)), { ok: false, why: 'public' }); assert.match(log[0], /public: templates mode refused/); assert.deepEqual(s.made, [], 'a public bucket is never touched, only refused');
log = []; assert.equal((await ensurePrivateBucket({ getBucket: async () => ({ error: { message: 'x' } }), createBucket: async () => ({ error: { message: 'denied' } }) }, 'packages', t => log.push(t))).ok, false);
log = []; assert.equal((await ensurePrivateBucket({ getBucket: async () => { throw new Error('network'); } }, 'packages', t => log.push(t))).why, 'check');
const src = fs.readFileSync(path.join(root, 'server/index.mjs'), 'utf8');
assert.ok(/let TEMPLATES = templatesEnabled\(process\.env\)/.test(src) && /ensurePrivateBucket\(sb\.storage, PACKAGE_BUCKET\)/.test(src) && /if \(!ok\) TEMPLATES = false/.test(src), 'templates mode is switched off when the bucket is not private; the old engine works on');
assert.ok(/if \(!TEMPLATES\) throw new Error\('templates mode is off on this worker/.test(src), 'a template job is failed, not run, when the mode was refused');

// 2 · the uploads
const U = n => `0b1e2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c${String(n).padStart(2, '0')}.jpg`, now = Date.parse('2026-12-01T00:00:00Z'), ago = d => new Date(now - d * 86400e3).toISOString();
const jobs = [
  { id: 'old-anon', created_at: ago(30), user_id: null, options: { form: { photos: [{ file: U(1) }], logo: { file: U(2) } } } },
  { id: 'old-owned', created_at: ago(30), user_id: 'u1', options: { form: { photos: [{ file: U(3) }] } } },
  { id: 'young', created_at: ago(3), user_id: null, options: { form: { photos: [{ file: U(4) }] } } },
  { id: 'old-owned-edited', created_at: ago(40), user_id: 'u2', options: {} },
];
const edits = new Map([['old-owned-edited', [{ op: 'photo', src: `media/upload/${U(5)}`, w: 10, h: 10 }, { op: 'text', path: 'hero.title', value: 'x' }]]]);
const uploads = [U(1), U(2), U(3), U(4), U(5), U(6), U(7)].map((name, i) => ({ name, created_at: ago(i === 6 ? 2 : 31) })).concat([{ name: 'readme.txt', created_at: ago(99) }]);
assert.deepEqual([...named(jobs[0])], [U(1), U(2)]); assert.deepEqual([...named(jobs[3], edits.get('old-owned-edited'))], [U(5)]);
assert.deepEqual(removals({ uploads, jobs, edits, now }), [U(1), U(2), U(6)],
  'gone: an old nobody\'s job\'s photographs, and an old upload no job names; kept: someone\'s (downloaded, kept edits), a young job\'s, a young upload, and anything that is not an upload');
assert.equal(DAYS, 14);
const removed = [], logged = [];
const r = await runCleanup({ listUploads: async () => uploads, jobs: async since => { assert.ok(Date.parse(since) <= now - 31 * 86400e3); return jobs; }, editsOf: async id => edits.get(id) || null,
  remove: async names => { removed.push(...names); }, now: () => now, log: t => logged.push(t) });
assert.deepEqual(r, { removed: 3, kept: 5 }); assert.deepEqual(removed, [U(1), U(2), U(6)]);
assert.deepEqual(logged, ['cleanup: 3 uploads removed, 5 kept'], 'counts only: no file name, nothing of a visitor');
assert.ok(/runCleanup\(/.test(src) && /setInterval\(.*86400e3\)/s.test(src), 'on boot, then every 24 h');
console.log('Upkeep: the packages bucket made private or templates mode refused; uploads of nobody\'s jobs older than 14 days removed, counts only');
