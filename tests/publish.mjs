// Publishing on <name>.swarmsite.si and the download with the edits (server/publish.mjs), without a bucket, Chrome or
// Vercel. The package step (lib/templates/edit.py package --verify) is tested in tests/test_templates_edit.py; here,
// what the server does with its verdict: only a verified package is kept, and only its files go up, then the alias.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { runPublish, runRepackage, editedPackage, editsHash, nameProblem, deploy, DOMAIN } from '../server/publish.mjs';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'); const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'publish-'));
const ID = '77777777-7777-4777-8777-777777777777', OPS = [{ op: 'text', path: 'hero.title', value: 'Closed by six' }];
try {
  // names
  assert.equal(nameProblem('casa-fern'), ''); assert.equal(nameProblem('tallyfern2'), '');
  for (const bad of ['', 'ab', 'Casa', 'casa_fern', '-casa', 'casa-', 'ca--sa', 'a'.repeat(41), 'www', 'api', 'app', 'casa.fern', 'xn--ab'.replace('xn--', 'x--')]) assert.ok(nameProblem(bad), bad);
  assert.equal(DOMAIN, 'swarmsite.si');

  function world({ verdict = 'ok', vercel = 'ok', held = null } = {}) {
    const priv = new Map([[`${ID}/data.json`, Buffer.from('{"brand":{"name":"Tallyfern"},"hero":{"title":"x"}}')]]); if (held) priv.set('names/casa-fern.json', Buffer.from(JSON.stringify(held)));
    const states = [], calls = [], py = [];
    const python = async args => { py.push(args[1]);
      if (args[1] === 'package') { const zip = args[args.indexOf('--zip') + 1]; assert.ok(args.includes('--verify'), 'never without the comparison'); assert.equal(args[args.indexOf('--media-from') + 1], `https://storage.example/previews/${ID}/t/`);
        assert.deepEqual(JSON.parse(fs.readFileSync(args[args.indexOf('--ops') + 1], 'utf8')), OPS, 'the edits kept are the edits packaged');
        if (verdict !== 'ok') return JSON.stringify({ ok: false, why: ['d: 2 of 8 screens differ by more than 0.50 %'] }); fs.writeFileSync(zip, 'PK-zip'); return JSON.stringify({ ok: true, why: [], bytes: 6 }); }
      if (args[1] === 'files') return JSON.stringify({ files: [{ file: 'index.html', data: 'PGgxPg==' }, { file: 'media/a.jpg', data: 'AAA=' }, { file: 'fonts/f.woff2', data: 'AAA=' }, { file: 'data.json', data: 'e30=' }, { file: 'README.txt', data: 'eA==' }] });
      throw new Error('unexpected ' + args.join(' ')); };
    let polls = 0;
    const fetch = async (url, init) => { calls.push({ url, method: init.method, body: init.body ? JSON.parse(init.body) : null, auth: init.headers.authorization });
      const ok = (o, status = 200) => ({ ok: status < 400, status, json: async () => o });
      if (vercel === 'down') return ok({ error: { message: 'Not authorized' } }, 403);
      if (url.includes('/v13/deployments?') || url.endsWith('/v13/deployments')) return ok({ id: 'dpl_1', readyState: 'QUEUED' });
      if (url.includes('/v13/deployments/dpl_1')) return ok({ readyState: ++polls < 2 ? 'BUILDING' : vercel === 'error' ? 'ERROR' : 'READY' });
      if (url.includes('/v2/deployments/dpl_1/aliases')) return ok({ alias: init.body && JSON.parse(init.body).alias });
      return ok({}, 404); };
    const deps = { row: { id: ID, result: { templates: { store: { data: `${ID}/data.json`, variants: {} } } } }, slug: 'griffin', name: 'casa-fern', user: { id: 'u1' }, edits: async () => OPS,
      readPrivate: async k => priv.get(k) || null, writePrivate: async (k, b) => { priv.set(k, Buffer.from(b)); }, publicBase: k => 'https://storage.example/previews/' + k,
      python, fetch, env: { VERCEL_TOKEN: 'test-token', VERCEL_TEAM_ID: 'team_1' }, tmp: () => tmp, save: async s => { states.push(s); }, sleep: async () => {} };
    return { deps, priv, states, calls, py };
  }

  // 1 · a publish that goes through: name claimed, package verified and kept, the same files up, the alias, live
  let w = world(); let r = await runPublish(w.deps);
  assert.deepEqual(r, { ok: true, url: 'https://casa-fern.swarmsite.si' });
  assert.deepEqual(w.states.map(s => s.status), ['packaging', 'deploying', 'live']);
  const hash = editsHash(OPS), key = `${ID}/griffin.edited-${hash}.zip`;
  assert.equal(String(w.priv.get(key)), 'PK-zip', 'the verified package is kept: it is also the download'); assert.deepEqual(JSON.parse(w.priv.get('names/casa-fern.json')).job, ID);
  const dep = w.calls[0];
  assert.equal(dep.method, 'POST'); assert.match(dep.url, /^https:\/\/api\.vercel\.com\/v13\/deployments\?teamId=team_1$/); assert.equal(dep.auth, 'Bearer test-token');
  assert.deepEqual(dep.body.files.map(f => f.file), ['index.html', 'media/a.jpg', 'fonts/f.woff2'], 'the page and what it loads; the package\'s data.json and README stay in the download');
  assert.ok(dep.body.files.every(f => f.encoding === 'base64') && dep.body.target === 'production' && dep.body.name === 'swarmsite-sites');
  assert.deepEqual(w.calls.at(-1).body, { alias: 'casa-fern.swarmsite.si' }); assert.match(w.calls.at(-1).url, /\/v2\/deployments\/dpl_1\/aliases\?teamId=team_1$/);
  assert.equal(w.states.at(-1).url, 'https://casa-fern.swarmsite.si'); assert.equal(w.states.at(-1).hash, hash);
  // the download hands out that package while the edits stay as they were
  const result = { publish: w.states.at(-1) };
  assert.equal(editedPackage(result, 'griffin', hash), key); assert.equal(editedPackage(result, 'griffin', editsHash([])), null, 'other edits: not this package'); assert.equal(editedPackage(result, 'maze', hash), null);

  // 2 · a package that does not match its page is never published
  w = world({ verdict: 'refused' }); r = await runPublish(w.deps);
  assert.equal(r.ok, false); assert.deepEqual(w.states.map(s => s.status), ['packaging', 'refused']); assert.equal(w.calls.length, 0, 'nothing sent to Vercel'); assert.ok(![...w.priv.keys()].some(k => k.endsWith('.zip')));
  assert.equal(editedPackage({ publish: w.states.at(-1) }, 'griffin', hash), null);
  // 3 · a name another job holds
  w = world({ held: { job: 'another-job' } }); r = await runPublish(w.deps);
  assert.deepEqual(w.states.map(s => [s.status, s.why?.[0]]), [['refused', 'That name is taken.']]); assert.equal(w.py.length, 0);
  // the same job may publish again under its own name
  w = world({ held: { job: ID } }); assert.equal((await runPublish(w.deps)).ok, true);
  // 4 · Vercel refusing, or a deployment that fails: the state says so; the verified package stays the download
  w = world({ vercel: 'down' }); r = await runPublish(w.deps);
  assert.deepEqual(w.states.map(s => s.status), ['packaging', 'deploying', 'failed']); assert.match(w.states.at(-1).why[0], /vercel 403: Not authorized/); assert.equal(editedPackage({ publish: w.states.at(-1) }, 'griffin', hash), key);
  w = world({ vercel: 'error' }); r = await runPublish(w.deps); assert.match(w.states.at(-1).why[0], /deployment error/);
  // 5 · the download with the edits, without publishing
  w = world(); r = await runRepackage(w.deps);
  assert.deepEqual(w.states.map(s => s.status), ['packaging', 'ready']); assert.equal(editedPackage({ edited: w.states.at(-1) }, 'griffin', hash), key); assert.equal(w.calls.length, 0);
  await assert.rejects(deploy({ files: [], name: 'x', env: { VERCEL_TOKEN: 't' }, fetch: async () => ({ ok: false, status: 500, json: async () => ({}) }) }), /vercel 500/);

  // 6 · the server: off without a token, the payment hook, an account, the download asks for the edited package
  const src = fs.readFileSync(path.join(root, 'server/index.mjs'), 'utf8');
  assert.ok(/if \(!process\.env\.VERCEL_TOKEN\) return res\.status\(503\)/.test(src), 'publishing is off until the owner sets the token');
  assert.ok(/const g = await pubGate\(req, res\)/.test(src) && /mayKeep\(\{ user, row \}\); if \(may\.status !== 200\)/.test(src) && /process\.env\.PACKAGES_FREE !== '1'\) \{ res\.status\(402\)/.test(src), 'an account, then the payment hook');
  assert.ok(/editedPackage\(row\.result, req\.params\.slug, editsHash\(kept\)\)/.test(src) && /prepare: true/.test(src), 'with kept edits, the download is their verified package, or it asks to prepare one');
  console.log('Publish: name rules, a verified package kept and deployed file for file, the alias, refused and failed states, the download with the edits, the server\'s gates');
} finally { fs.rmSync(tmp, { recursive: true, force: true }); }
