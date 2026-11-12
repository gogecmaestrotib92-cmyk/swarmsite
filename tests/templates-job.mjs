// The `templates` job mode, end to end without a database, a bucket or a model: a made-up capture → the reader (stub) →
// adapt, select, render, gate (real: lib/templates/job.py, Chrome) → the variants published and saved before the packages
// are made → packages uploaded to the private bucket only when they match their preview. And who may download.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { spawn, spawnSync } from 'node:child_process'; import { fileURLToPath } from 'node:url';
import { runTemplateJob, mayDownload, previewable, enabled, STEPS_T, STEPS_F, formProblem, imageType } from '../server/templates.mjs';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'); const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'tjob-'));
const py = process.env.PYTHON || 'python3';
// the worker's own `run`, cut down: a child process, its stdout, rejected on a non-zero exit
const real = (cmd, args, opts = {}) => new Promise((ok, no) => { const p = spawn(cmd, args, { cwd: root, env: { ...process.env, SWARM_JOB_DIR: opts.dir || '' } }); let out = '', err = '';
  p.stdout.on('data', d => { out += d; }); p.stderr.on('data', d => { err += d; }); p.on('close', c => c === 0 ? ok(out) : no(new Error(`${cmd} ${args[0]} exit ${c}: ${err.slice(-400)}`))); });
try {
  assert.equal(enabled({}), false, 'off unless the deployment says so'); assert.equal(enabled({ TEMPLATES_MODE: '1' }), true);
  assert.deepEqual(STEPS_T.map(s => s[0]), ['capture', 'read', 'choose', 'publish', 'package']);

  async function scenario({ capture = 'product', pkg = 'real-stub', form = null } = {}) {
    const jobRoot = fs.mkdtempSync(path.join(tmp, 'job-')), dir = path.join(jobRoot, 'site'), log = [], steps = [], events = [], saves = [], pub = new Map(), priv = new Map(), fetched = [];
    const job = { id: '22222222-2222-4222-8222-222222222222', url: form ? 'form:tallyfern-1a2b3c4d' : 'https://www.tallyfern.example/', options: { engine: 'templates', mode: 'seo-safe', ...(form ? { source: 'form', form } : {}) }, result: {} };
    const run = async (cmd, args, opts = {}) => { log.push(args[0] === '-c' ? 'reader' : args[0] + (args[1] === 'build' || args[1] === 'package' ? ' ' + args[1] : ''));
      if (args[0] === 'lib/pipeline/capture.mjs') { const r = spawnSync(py, ['tests/fixtures/templates/capture.py', dir, capture], { cwd: root, encoding: 'utf8' }); assert.equal(r.status, 0, r.stderr); fs.writeFileSync(path.join(dir, 'before-hero.jpg'), 'jpg'); opts.onLine?.('{"event":{"role":"Photos","text":"1 picture"}}'); return ''; }
      if (args[0] === '-c') { fs.writeFileSync(path.join(dir, 'budget.json'), JSON.stringify({ calls: 1, in: 21000, out: 2400, usd: 0.066 })); return '{"what":"A ledger for market stalls","n":3}'; }
      if (args[1] === 'build') return real(cmd, args, { dir });
      if (args[1] === 'package') { const zip = args[4];   // the package itself is tested in tests/test_templates_package.py; here: what the worker does with each verdict
        if (pkg === 'crash') throw new Error('python3 lib/templates/job.py exit 1: Traceback');
        if (pkg === 'refused') return JSON.stringify({ slug: args[3], ok: false, why: ['d: 1 of 8 screens differ by more than 0.50 %'] });
        fs.writeFileSync(zip, 'PK'); return JSON.stringify({ slug: args[3], ok: true, why: [], bytes: 2 }); }
      throw new Error('unexpected run ' + args.join(' ')); };
    const deps = { job, dir, jobRoot, run, self: 'https://api.example', chrome: '',
      upload: async (local, key, type) => { assert.ok(fs.existsSync(local), local); pub.set(key, { type, bytes: fs.statSync(local).size }); return 'https://storage.example/previews/' + key; },
      uploadPrivate: async (local, key, type) => { priv.set(key, { type }); },
      fetchUpload: async (file, local) => { fetched.push(file); fs.copyFileSync(path.join(root, 'web/favicon.png'), local); },
      publicBase: key => 'https://storage.example/previews/' + key,
      setStep: async (id, status) => { steps.push(`${id}:${status}`); }, emit: async evs => { events.push(...evs); },
      save: async r => { saves.push(JSON.parse(JSON.stringify({ variants: r.templates?.variants, packagesBefore: [...priv.keys()].filter(k => k.endsWith('.zip')).length }))); } };
    const result = await runTemplateJob(deps);
    return { result, log, steps, events, saves, pub, priv, dir, fetched };
  }

  // 0 · a site from nothing: the visitor's form and photographs in place of capture and reader — no paid call
  const UP = '0b1e2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d.png';
  const form = { name: 'Tallyfern', sentence: 'A ledger for market stalls that balances itself at closing time', kind: 'software', offers: [{ name: 'Counts the till' }, { name: 'Closes the day' }],
    steps: [{ title: 'Connect the card reader' }, { title: 'Close the day' }], figures: [{ v: '1 200', l: 'stalls use it' }, { v: '4 min', l: 'to close a day' }], photos: [{ file: UP, role: 'screen' }], contact: { phone: '12' } };
  assert.equal(formProblem(form), ''); assert.ok(formProblem({ ...form, name: ' ' }) && formProblem({ ...form, photos: [{ file: '../x.png' }] }) && formProblem({ ...form, logo: { file: 'http://x/y.png' } }) && formProblem(null));
  assert.deepEqual(STEPS_F.map(s => s[0]), ['form', 'choose', 'publish', 'package']);
  assert.equal(imageType(fs.readFileSync(path.join(root, 'web/favicon.png'))), 'png'); assert.equal(imageType(Buffer.from('<svg onload=alert(1)>')), ''); assert.equal(imageType(Buffer.from([0xff, 0xd8, 0xff, 0xe0, 0, 0, 0, 0, 0, 0, 0, 0])), 'jpg');
  // the library grows: which templates a client is shown is select's answer (tests/test_templates_select.py); here griffin is among them, up to three
  const shownOf = r => r.templates.variants.map(v => v.slug), packs = r => shownOf(r).map(() => 'lib/templates/job.py package');
  let x = await scenario({ form });
  assert.ok(shownOf(x.result).includes('griffin') && shownOf(x.result).length <= 3, shownOf(x.result).join());
  assert.deepEqual(x.log, ['lib/templates/job.py build', ...packs(x.result)], 'no capture and no reader: a form job makes no paid call');
  assert.deepEqual(x.steps, STEPS_F.flatMap(([id]) => [`${id}:running`, `${id}:done`])); assert.deepEqual(x.fetched, [UP]);
  assert.equal(x.result.source, 'form'); assert.equal(x.result.budget, null, 'nothing priced');
  assert.ok(x.result.templates.left_out.some(g => /contact\.phone/.test(g)), 'what the form left out is in the job, for the visitor');
  assert.ok([...x.pub.keys()].some(k => /\/t\/media\/upload\/photo-1\.png$/.test(k)), 'their photograph is published beside the preview');
  assert.ok([...x.priv.keys()].includes('22222222-2222-4222-8222-222222222222/data.json'), 'the form\'s data is kept in the same store as a captured site\'s');

  // 1 · a site a template fits
  x = await scenario();
  assert.ok(shownOf(x.result).includes('griffin') && shownOf(x.result).length <= 3, shownOf(x.result).join());
  assert.deepEqual(x.log, ['lib/pipeline/capture.mjs', 'reader', 'lib/templates/job.py build', ...packs(x.result)], 'one reader call, one build, one package for each variant shown');
  assert.deepEqual(x.steps, STEPS_T.flatMap(([id]) => [`${id}:running`, `${id}:done`]));
  const t = x.result.templates, shown = shownOf(x.result), gv = t.variants.find(v => v.slug === 'griffin');
  assert.equal(x.result.mode, 'templates');
  assert.equal(gv.url, 'https://api.example/t/22222222-2222-4222-8222-222222222222/griffin'); assert.ok(t.variants.every(v => v.package === 'ready'));
  assert.ok(t.rejected.some(r => r.slug === 'maze' && /screens_min/.test(r.why)), 'every other template, with its reason');
  assert.ok(x.pub.has('22222222-2222-4222-8222-222222222222/t/griffin.html') && x.pub.get('22222222-2222-4222-8222-222222222222/t/griffin.html').type === 'text/html');
  assert.ok([...x.pub.keys()].some(k => /\/t\/media\/logo\.svg$/.test(k)), 'the media the pages ask for are published beside them');
  const page = fs.readFileSync(path.join(x.dir, 'templates', 'pub', 'griffin.html'), 'utf8');
  assert.ok(page.includes('https://storage.example/previews/22222222-2222-4222-8222-222222222222/t/media/logo.svg') && !page.includes('../../media/'), 'the preview page asks for its media where they were published');
  assert.deepEqual([...x.priv.keys()], ['22222222-2222-4222-8222-222222222222/data.json', ...shown.map(s => `22222222-2222-4222-8222-222222222222/${s}.zip`)], 'the data store and the packages go to the private bucket, nowhere public');
  assert.deepEqual(t.store, { data: '22222222-2222-4222-8222-222222222222/data.json', variants: {} }, 'the job names where its data is kept (no library on this machine for this test: no variant data of its own)');
  assert.ok(![...x.pub.keys()].some(k => k.endsWith('.zip')));
  assert.equal(x.saves.length, 1); assert.deepEqual(x.saves[0].variants.map(v => [v.slug, v.package]), shown.map(s => [s, 'pending'])); assert.equal(x.saves[0].packagesBefore, 0, 'the previews are saved before any package is made');
  assert.deepEqual(x.result.budget, { calls: 1, in: 21000, out: 2400, usd: 0.066 }, 'what the visitor cost: the reader, from the job ledger');
  assert.ok(['adapt', 'select', 'render', 'gate'].every(k => typeof t.timings_ms[k] === 'number') && ['capture', 'read', 'choose', 'publish', 'package'].every(k => typeof t.timings_ms.steps[k] === 'number'), 'stage timings in the job record');
  assert.ok(x.result.beforeUrl && x.events.some(e => e.role === 'QA' && /griffin: every screen passes/.test(e.text)) && x.events.some(e => e.text === '1 picture'));

  // 2 · a package that does not match its preview, and one whose making crashes: the preview stays, the download does not
  x = await scenario({ pkg: 'refused' });
  assert.equal(x.result.templates.variants[0].package, 'refused'); assert.deepEqual(x.result.templates.variants[0].package_why, ['d: 1 of 8 screens differ by more than 0.50 %']); assert.ok(![...x.priv.keys()].some(k => k.endsWith('.zip')));
  x = await scenario({ pkg: 'crash' });
  assert.equal(x.result.templates.variants[0].package, 'refused'); assert.ok(/could not be made/.test(x.result.templates.variants[0].package_why[0])); assert.ok(![...x.priv.keys()].some(k => k.endsWith('.zip')));

  // 3 · a site no template fits: the job ends with no variant and says why — nothing is shown that was not fit to show
  x = await scenario({ capture: 'empty' });
  assert.deepEqual(x.result.templates.variants, []); assert.ok(x.result.templates.rejected.length >= 2); assert.ok(!x.log.includes('lib/templates/job.py package'));

  // 4 · who may see, who may download
  const row = { status: 'done', result: { templates: { variants: [{ slug: 'griffin', package: 'ready' }, { slug: 'maze', package: 'refused', package_why: ['x'] }, { slug: 'cerebrium', package: 'pending' }] } } };
  assert.ok(previewable(row, 'griffin') && previewable({ ...row, status: 'running' }, 'griffin'));
  assert.ok(!previewable(row, 'butter') && !previewable(row, '../griffin') && !previewable({ ...row, status: 'failed' }, 'griffin') && !previewable(null, 'griffin'));
  const me = { id: 'u1', email: 'a@b.example' };
  assert.equal(mayDownload({ user: null, job: row, slug: 'griffin', env: {} }).status, 401, 'a preview needs no account; a download does');
  assert.deepEqual(mayDownload({ user: me, job: row, slug: 'griffin', env: {} }), { status: 402, body: { error: 'Payment is needed to download this page.', pay: true } }, 'the payment hook: not built, so it asks for payment');
  assert.equal(mayDownload({ user: me, job: row, slug: 'griffin', env: { PACKAGES_FREE: '1' } }).status, 200);
  assert.equal(mayDownload({ user: me, job: row, slug: 'maze', env: { PACKAGES_FREE: '1' } }).status, 409, 'a refused package is never handed out');
  assert.ok(mayDownload({ user: me, job: row, slug: 'cerebrium', env: { PACKAGES_FREE: '1' } }).body.pending);
  assert.equal(mayDownload({ user: me, job: row, slug: 'butter', env: { PACKAGES_FREE: '1' } }).status, 404);

  // 5 · the server: off by default, previews open, packages behind sign-in and the hook, the old path untouched
  const src = fs.readFileSync(path.join(root, 'server/index.mjs'), 'utf8');
  assert.ok(/if \(mode && !TEMPLATES\) return res\.status\(400\)/.test(src) && /if \(!mode && AUTH\.require && !user\)/.test(src), 'templates mode: refused when off; no sign-in asked to start one');
  assert.ok(/app\.get\('\/t\/:id\/:slug', async/.test(src) && /app\.get\('\/t\/:id\/:slug\/package'/.test(src) && /mayDownload\(\{ user, job: row/.test(src) && /from\(PACKAGE_BUCKET\)\.download/.test(src));
  assert.ok(/if \(job\.options\?\.engine === 'templates'\) return processTemplates\(job\)/.test(src) && /canonicalUrl\(j\.url\) === key && \(j\.options\?\.engine === 'templates'/.test(src), 'the same site in the other mode is not handed back as this one');
  assert.ok(/app\.post\('\/uploads', express\.raw\(/.test(src) && /const ext = imageType\(/.test(src) && /from\(PACKAGE_BUCKET\)\.upload\(`uploads\/\$\{file\}`/.test(src), 'uploads: the file\'s own bytes say what it is; kept in the private bucket');
  assert.ok(/const fromForm = mode && req\.body\?\.options\?\.source === 'form'/.test(src) && /formProblem\(req\.body\?\.form\)/.test(src) && /fromForm \? STEPS_F : mode \? STEPS_T : STEPS/.test(src), 'a form job: only on the template path, its form checked, its own steps');
  console.log('Templates job: one reader call, three-variant build gated in Chrome, previews saved before packages, packages private and only when they match, a site nothing fits, and who may download');
} finally { fs.rmSync(tmp, { recursive: true, force: true }); }
