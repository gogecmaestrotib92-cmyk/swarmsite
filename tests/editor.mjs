// The editor's server half (server/editor.mjs) without a database, a bucket or Chrome: the job's kept data, the patch
// replayed by the real lib/templates/edit.py, the gate's answer in the visitor's words, a photograph added while
// editing, edits kept beside the data — and who may keep them.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { spawn } from 'node:child_process'; import { fileURLToPath } from 'node:url';
import { makeEditor, mayKeep, editable, opsProblem, MAX_OPS } from '../server/editor.mjs';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'); const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'editor-'));
const py = process.env.PYTHON || 'python3';
const python = args => new Promise((ok, no) => { const p = spawn(py, args, { cwd: root }); let out = '', err = ''; p.stdout.on('data', d => { out += d; }); p.stderr.on('data', d => { err += d; }); p.on('close', c => c === 0 ? ok(out) : no(new Error(err.slice(-300)))); });
const ID = '55555555-5555-4555-8555-555555555555', UP = '0b1e2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d.png';
try {
  const data = fs.readFileSync(path.join(root, 'tests/fixtures/templates/tallyfern.json'));
  const priv = new Map([[`${ID}/data.json`, data], [`uploads/${UP}`, fs.readFileSync(path.join(root, 'web/favicon.png'))]]), pub = new Map(), gated = [];
  let gateAnswer = { ok: true, failed: [], checks: {} };
  const E = makeEditor({ readPrivate: async k => priv.get(k) || null, writePrivate: async (k, b) => { priv.set(k, b); }, publishPublic: async (l, k, t) => { pub.set(k, { t, bytes: fs.statSync(l).size }); return 'https://storage.example/previews/' + k; },
    publicBase: k => 'https://storage.example/previews/' + k, python, gate: async f => { gated.push(fs.readFileSync(f, 'utf8')); return gateAnswer; }, tmp: () => tmp });
  const row = { id: ID, status: 'done', user_id: null, result: { templates: { variants: [{ slug: 'griffin' }, { slug: 'maze' }], store: { data: `${ID}/data.json`, variants: {} } } } };

  // what the editor shows, after the edits sent
  const ops = [{ op: 'text', path: 'hero.title', value: 'Closed by six, every evening' }, { op: 'hide', block: 'faq' }, { op: 'text', path: 'kind', value: 'x' }];
  const d = await E.describe(row, 'griffin', ops);
  assert.ok(d.fields.some(f => f.path === 'hero.title' && f.value === 'Closed by six, every evening') && !d.blocks.includes('faq') && d.refused.length === 1 && d.palettes.length >= 2 && d.movable.length === 0);
  // the colours offered are those of a tone the job measured this design to hold; a job made before that was measured
  // offers the tone its page was made in (this client's is dark), and an edit to a light ground does not change what was measured
  assert.ok(d.tone === 'dark' && d.palettes.every(p => p.tone === 'dark'), 'an unmeasured design offers its own tone only');
  const both = { ...row, result: { templates: { ...row.result.templates, variants: [{ slug: 'griffin', tones: ['dark', 'light'] }, { slug: 'maze', tones: ['dark'] }] } } };
  const dk = [{ op: 'palette', ground: '#ffffff', ink: '#151515', accent: '#151515' }];
  const pg = (await E.describe(both, 'griffin', dk)).palettes, pm = await E.describe(both, 'maze', dk);
  assert.ok(pg.some(p => p.tone === 'dark') && pg.some(p => p.tone === 'light') && pm.tone === 'dark' && pm.palettes.length && pm.palettes.every(p => p.tone === 'dark'));
  // the edited page, its media where the preview's are; the same edits on the other design
  for (const slug of ['griffin', 'maze']) { const html = await E.render(row, slug, ops);
    assert.ok(html.includes('Closed by six, every evening') && html.includes(`https://storage.example/previews/${ID}/t/media/`), slug); }
  // the readability gate, said in the visitor's words
  assert.deepEqual(await E.check(row, 'griffin', ops), { ok: true, failed: [], unread: [], overlap: 0, sideways: 0, unseen: [] });
  gateAnswer = { ok: false, failed: ['legible'], checks: { legible: [{ at: 'm', ratio: 2.14, text: 'Closed by six, every evening' }], overlap: [], sideways: [] } };
  const c = await E.check(row, 'griffin', ops);
  assert.equal(c.ok, false); assert.deepEqual(c.unread, [{ text: 'Closed by six, every evening', ratio: 2.14, at: 'm' }]);
  assert.ok(gated.at(-1).includes('Closed by six, every evening'), 'the gate judged the edited page');
  // a photograph added while editing: measured, published beside the preview's media, offered as theirs
  const op = await E.photo(row, UP);
  assert.deepEqual(op, { op: 'photo', src: `media/upload/${UP}`, w: 64, h: 64 }); assert.ok(pub.has(`${ID}/t/media/upload/${UP}`));
  await assert.rejects(E.photo(row, '../../x.png'), /not an upload/); await assert.rejects(E.photo(row, UP.replace('0b', '0c')), /gone/);
  // kept beside the data, read back as the patch
  assert.deepEqual(await E.saved(row), []); await E.save(row, ops); assert.deepEqual(await E.saved(row), ops);
  // a job that keeps no data has nothing to edit
  await assert.rejects(E.render({ ...row, result: { templates: { variants: [], store: { data: `${ID}/none.json` } } } }, 'griffin', []), e => e.status === 404);
  // the shape of a patch; who may keep edits; which designs may be edited
  assert.equal(opsProblem([]), ''); assert.ok(opsProblem({}) && opsProblem([{ op: 'eval' }]) && opsProblem([null]) && opsProblem(Array(MAX_OPS + 1).fill({ op: 'hide', block: 'faq' })));
  assert.equal(mayKeep({ user: null, row }).status, 401); assert.deepEqual(mayKeep({ user: { id: 'u1' }, row }), { status: 200, claim: true });
  assert.equal(mayKeep({ user: { id: 'u2' }, row: { ...row, user_id: 'u1' } }).status, 403); assert.deepEqual(mayKeep({ user: { id: 'u1' }, row: { ...row, user_id: 'u1' } }), { status: 200, claim: false });
  assert.ok(editable(row, 'griffin') && !editable(row, 'cerebrium') && !editable({ ...row, status: 'running' }, 'griffin') && !editable(row, '../griffin') && !editable({ ...row, result: { templates: { variants: [{ slug: 'griffin' }] } } }, 'griffin'));
  // a picture that can no longer be seen is passed on by its name
  gateAnswer = { ok: false, failed: ['unseen'], checks: { unseen: [{ at: 'd', file: 'logo.svg', alt: 'Tallyfern', shows: 12.7 }], legible: [] } };
  assert.deepEqual((await E.check(row, 'griffin', [])).unseen, [{ alt: 'Tallyfern', at: 'd' }]);
  // the gate's own answer when a page fails: it exits 1 and prints why. That is an answer, never "the tool did not run"
  // (production, 2026-11-13: every failing check came back as failed: ['tool'], because a helper threw away what a
  // non-zero exit had printed). Run for real, in Chrome, on a page with a line nobody can read.
  { const { gateAnswer: answer, runGate } = await import('../server/editor.mjs'); const bad = path.join(tmp, 'unreadable.html');
    fs.writeFileSync(bad, '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><body style="margin:0;background:#fff;font:20px Arial"><h1 style="color:#111;margin:40px">A page</h1><p style="color:#fdfdfd;margin:40px">Nobody can read this line on a white ground.</p></body></html>');
    const got = await runGate(bad, { root }); assert.equal(got.ok, false); assert.ok(got.failed.includes('legible') && !got.failed.includes('tool'), 'a failing page is answered with its reason: ' + JSON.stringify(got.failed));
    assert.ok((got.checks.legible || []).some(x => /Nobody can read/.test(x.text)), 'and names the line');
    assert.deepEqual(answer(''), { ok: false, failed: ['tool'] }, 'only a gate that printed nothing did not run'); assert.deepEqual(answer('noise\n{"page":"x","ok":true,"failed":[]}\n').ok, true); }
  // the server's wiring
  const src = fs.readFileSync(path.join(root, 'server/index.mjs'), 'utf8');
  for (const r of ["app.post('/t/:id/:slug/describe'", "app.post('/t/:id/:slug/render'", "app.post('/t/:id/:slug/check'", "app.post('/t/:id/photos'", "app.put('/t/:id/edits'"]) assert.ok(src.includes(r), r);
  assert.ok(/gate: file => runGate\(file, \{ root: ROOT \}\)/.test(src), 'the worker reads the gate through runGate, which keeps the answer of a failing page');
  assert.ok(/mayKeep\(\{ user, row \}\)/.test(src) && /editLimited\(clientIp\(req\), 'r', 600\)/.test(src) && /editLimited\(clientIp\(req\), 'c', 120\)/.test(src), 'keeping needs an account; trying is rate-limited');
  console.log('Editor: edits replayed on both designs, the gate in the visitor\'s words, a photograph added, edits kept beside the data, and who may keep them');
} finally { fs.rmSync(tmp, { recursive: true, force: true }); }
