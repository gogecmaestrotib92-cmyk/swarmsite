/* The worker finds the picture library it makes pictures from, and says on boot how many it found.
   Production job bc69c9d1 (2026-11-12) reported `media.library 0` and `store.variants {}`: the image was built without
   media/ (server/Dockerfile copied lib/ but not media/), so lib/templates/pictures.py found no library and every client
   got no made pictures, silently. */
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path';
import { execFileSync } from 'node:child_process'; import { fileURLToPath } from 'node:url';
import { libraryCount } from '../server/templates.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// the image carries the library, at the place pictures.py looks for it (the repo root beside lib/)
const docker = fs.readFileSync(path.join(ROOT, 'server', 'Dockerfile'), 'utf8');
assert.match(docker, /^COPY media media$/m, 'the worker image copies media/ (the picture library)');
assert.match(docker, /^WORKDIR \/srv$/m); assert.match(docker, /^COPY lib lib$/m, 'media/ sits beside lib/, where pictures.py looks');
const ignore = path.join(ROOT, '.dockerignore');
if (fs.existsSync(ignore)) assert.ok(!/^\/?media\b/m.test(fs.readFileSync(ignore, 'utf8')), '.dockerignore does not leave the library out');

// the repo's library: every row names a file that is in the checkout, and is tracked (the image is built from git)
const here = libraryCount({}, ROOT);
assert.equal(here.root, ROOT); assert.ok(here.pictures >= 100, `the repo holds the library (${here.pictures} pictures)`); assert.equal(here.missing, 0, 'every picture the library names is there');
const rows = JSON.parse(fs.readFileSync(path.join(ROOT, 'media', 'library', 'library.json'), 'utf8'));
let tracked = null; try { tracked = new Set(execFileSync('git', ['ls-files', 'media/library'], { cwd: ROOT, encoding: 'utf8' }).split('\n').filter(Boolean)); } catch {}
if (tracked) { const untracked = rows.filter(r => r.src && !tracked.has(r.src)).map(r => r.src); assert.deepEqual(untracked.slice(0, 5), [], 'every library picture is committed'); }

// the same rule as pictures.root_of: $SWARMSITE_LIBRARY first, `none` switches it off, nothing found → 0
assert.deepEqual(libraryCount({ SWARMSITE_LIBRARY: 'none' }, ROOT), { root: null, pictures: 0, missing: 0 });
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'lib-')); fs.mkdirSync(path.join(tmp, 'media', 'library', 'a'), { recursive: true });
fs.writeFileSync(path.join(tmp, 'media', 'library', 'library.json'), JSON.stringify([{ family: 'a', palette: 'p', src: 'media/library/a/x.jpg' }, { family: 'a', palette: 'p', src: 'media/library/a/gone.jpg' }, { family: 'a' }]));
fs.writeFileSync(path.join(tmp, 'media', 'library', 'a', 'x.jpg'), 'x');
assert.deepEqual(libraryCount({ SWARMSITE_LIBRARY: tmp }, ROOT), { root: tmp, pictures: 2, missing: 1 });
assert.deepEqual(libraryCount({}, path.join(tmp, 'nowhere')), { root: null, pictures: 0, missing: 0 });

// the server says it on boot
const index = fs.readFileSync(path.join(ROOT, 'server', 'index.mjs'), 'utf8');
assert.match(index, /libraryCount\(process\.env, ROOT\)/); assert.match(index, /`library: \$\{lib\.pictures\} pictures/);
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`Library: ${here.pictures} pictures in the repo, all there and committed; the image copies them; the worker logs the count on boot`);
