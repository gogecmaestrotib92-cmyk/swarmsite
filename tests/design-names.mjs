/* Owner's rule (2026-11-12): a visitor never sees the name of a reference site a template was rebuilt from.
   Production job bc69c9d1 showed them everywhere: /t/<job>/griffin, "griffin: every screen passes", the 25 rejected
   templates by name, the store's file names, the chooser's labels. Here, with that job's shape:
   - GET /jobs/:id (publicJob) names every design by its id (v1 …) and name (Design 1 …), and no template anywhere;
   - an address's id turns back into the template on the server, and a job from before ids keeps its old links;
   - the download's file name, the pages' own code (app, edit, dashboard, login, landing) name no template. */
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { publicJob, internalSlug, publicOf, downloadName, scrub, TEMPLATE_SLUGS, PUBLIC_ID } from '../server/designs.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REF = JSON.parse(fs.readFileSync(path.join(ROOT, 'tests/fixtures/reference_names.json'), 'utf8'));
const WORDS = [...new Set([...TEMPLATE_SLUGS, ...Object.entries(REF).filter(([k]) => k !== '_').flatMap(([, v]) => v)].map(w => w.toLowerCase()))];
const named = text => WORDS.filter(w => new RegExp(`(?<![a-z0-9])${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?![a-z0-9])`, 'i').test(text));
assert.ok(TEMPLATE_SLUGS.length >= 20 && TEMPLATE_SLUGS.includes('griffin'), 'the library is read');

const J = 'bc69c9d1-7d7b-4458-be36-b8cf3b87f787', API = 'https://swarmsite-production.up.railway.app';
const v = (slug, i, extra = {}) => ({ slug, id: `v${i + 1}`, name: `Design ${i + 1}`, url: `${API}/t/${J}/v${i + 1}`, why: 'niche software; 4 need(s) met', approach: 'land · type', package: 'refused',
  package_why: [`d: the package is 7202 px high, the preview 7230`, `${slug} is not a variant this job shows`], made: { family: 'nature', palette: 'forest-green' }, ...extra });
const row = { id: J, url: 'https://sportbotai.com', status: 'done', result: { mode: 'templates',
  events: [{ role: 'Reader', text: 'SportBot AI is an AI sports betting analysis tool' }, { role: 'QA', text: 'griffin: every screen passes' }, { role: 'QA', text: 'terminal: every screen passes' }],
  templates: { group: 'life', niche: ['software'], pictures: 5, media: { library: 31, missing: [], written: 6 },
    store: { data: `${J}/data.json`, variants: { griffin: `${J}/griffin.data.json`, terminal: `${J}/terminal.data.json` } },
    variants: [v('griffin', 0), v('terminal', 1), v('cerebrium', 2)],
    rejected: TEMPLATE_SLUGS.filter(s => !['griffin', 'terminal', 'cerebrium'].includes(s)).map(s => ({ slug: s, why: `niche: it is for shop; ${s} needs catalogue` })),
    not_shown: [{ slug: 'maze', failed: ['legible'] }], timings_ms: { gate: 19604 } },
  paid: { griffin: { user: 'u1', session: 'cs_live_1', at: '2026-11-12T19:00:00Z' } },
  edited: { status: 'ready', slug: 'terminal', hash: 'abc', package: `${J}/terminal.edited-abc.zip`, at: 't' },
  publish: { status: 'refused', slug: 'cerebrium', name: 'sportbot', why: ['cerebrium: 1 of 9 screens differ'], at: 't' } } };

const pub = publicJob(row), text = JSON.stringify(pub);
assert.deepEqual(named(text), [], 'the job as the web app reads it names no template: ' + named(text).join(', '));
const t = pub.result.templates;
assert.deepEqual(t.variants.map(x => [x.slug, x.id, x.name, x.url]), [0, 1, 2].map(i => [`v${i + 1}`, `v${i + 1}`, `Design ${i + 1}`, `${API}/t/${J}/v${i + 1}`]));
assert.equal(t.store, true, 'the editor still knows the job kept its data; where is the server\'s');
assert.ok(t.rejected.length === row.result.templates.rejected.length && t.rejected.every((r, i) => r.name === `Library design ${i + 1}` && /needs catalogue/.test(r.why)), 'why the others were not shown, without their names');
assert.deepEqual(pub.result.events.map(e => e.text), ['SportBot AI is an AI sports betting analysis tool', 'the design: every screen passes', 'the design: every screen passes']);
assert.deepEqual(Object.keys(pub.result.paid), ['v1']); assert.equal(pub.result.paid.v1.user, undefined, 'who paid stays on the server');
assert.deepEqual([pub.result.edited.slug, pub.result.edited.package, pub.result.publish.slug], ['v2', undefined, 'v3']);
assert.equal(pub.result.templates.media.library, 31); assert.deepEqual(t.variants[0].made, { family: 'nature', palette: 'forest-green' });
assert.equal(row.result.templates.variants[0].slug, 'griffin', 'the stored job is not changed');
assert.equal(publicJob(null), null); assert.deepEqual(publicJob({ id: 'x', status: 'queued' }), { id: 'x', status: 'queued' });

// the way back: an address's id → the template, for the server only
assert.equal(internalSlug(row, 'v1'), 'griffin'); assert.equal(internalSlug(row, 'v3'), 'cerebrium'); assert.equal(internalSlug(row, 'v4'), ''); assert.equal(internalSlug(null, 'v1'), '');
assert.equal(internalSlug(row, 'griffin'), '', 'a job made with ids answers only to them');
assert.equal(publicOf(row, 'terminal'), 'v2'); assert.equal(publicOf(row, 'maze'), '');
const old = { id: J, url: 'https://x.example', result: { templates: { variants: [{ slug: 'griffin', url: `${API}/t/${J}/griffin`, package: 'ready' }, { slug: 'maze', url: `${API}/t/${J}/maze`, package: 'ready' }] } } };
assert.equal(internalSlug(old, 'v2'), 'maze'); assert.equal(internalSlug(old, 'griffin'), 'griffin', 'a job from before ids keeps its old links');
assert.deepEqual(publicJob(old).result.templates.variants.map(x => [x.slug, x.name, x.url]), [['v1', 'Design 1', `${API}/t/${J}/v1`], ['v2', 'Design 2', `${API}/t/${J}/v2`]]);
assert.ok(PUBLIC_ID.test('v1') && PUBLIC_ID.test('v12') && !PUBLIC_ID.test('griffin'));

// file names and sentences
assert.equal(downloadName(row, 'griffin'), 'sportbotai.com-design-1.zip'); assert.equal(downloadName({ url: 'nonsense' }, 'x'), 'site-the-design.zip');
assert.equal(scrub('Griffin and maze-like terminal'), 'the design and the design-like the design');

// the pages' own code: what any visitor can read with "view source"
for (const f of ['app.html', 'edit.html', 'dashboard.html', 'login.html', 'index.html', 'start.html', 'js/auth.js', 'js/header.js', 'js/nav-account.js', 'llms.txt']) {
  const p = path.join(ROOT, 'web', f); if (!fs.existsSync(p)) continue;
  const hit = TEMPLATE_SLUGS.filter(s => !['terminal', 'maze', 'acme', 'recycle', 'fluently', 'chisel', 'omp', 'iip'].includes(s)).filter(s => new RegExp(`(?<![a-z0-9])${s}(?![a-z0-9])`, 'i').test(fs.readFileSync(p, 'utf8')));
  assert.deepEqual(hit, [], `web/${f} names a template`);
}
// the server answers GET /jobs/:id through publicJob, and turns every address's id back before it uses it
const src = fs.readFileSync(path.join(ROOT, 'server/index.mjs'), 'utf8');
assert.match(src, /res\.json\(publicJob\(data\)\)/);
assert.equal((src.match(/internalSlug\(row, req\.params\.slug\)/g) || []).length, 3, 'preview, package and the editor\'s routes');
assert.ok(!/req\.params\.slug\}/.test(src) && !/slug: req\.params\.slug/.test(src), 'no address part is used as a template or a file name');
console.log('Design names: the job, the addresses, the download and the pages name a design by its id and number, never by the reference behind it');
