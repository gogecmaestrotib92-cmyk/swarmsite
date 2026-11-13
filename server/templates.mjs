/* templates.mjs — the `templates` job mode: a visitor's site → three variants of the template library → a package.
   Beside the old path, behind TEMPLATES_MODE=1 (off unless the deployment says so).

   capture (Playwright) → read (the reader: the ONE paid model call of this path) → choose (lib/templates/job.py build:
   adapt → select → render three → gate) → publish (the variants that passed the gate, as preview pages) → package
   (lib/templates/job.py package: zip + offline comparison with the preview; uploaded to a private bucket).

   A site from nothing (options.source = 'form'): form (the visitor's own words and photographs; lib/templates/form.py)
   in place of capture and read — the same choose, publish and package after it, and no paid call.

   The variants are written into the job's result as soon as they are published, so the chooser shows them while the
   packages are still being made. A preview needs no account (owner, 2026-11-12: previews before sign-up and payment);
   only a package does — sign-in, then `mayDownload` (the payment hook: not built, see below).

   Everything the worker needs is passed in (`deps`), so the flow is tested without a database, a bucket or a model. */
import fs from 'node:fs'; import path from 'node:path';
import { payGate } from './payments.mjs';
import { publicId, designName, scrub } from './designs.mjs';

export const STEPS_T = [
  ['capture', 'Reading your site: text, photos, logo, colours'],
  ['read', 'Writing down what the site says'],
  ['choose', 'Choosing three designs and checking every screen'],
  ['publish', 'Publishing the three previews'],
  ['package', 'Preparing the downloads'],
];

// a site from nothing (BRIEF-engine.md step 8): the visitor's form in place of capture and reader — no paid call at all
export const STEPS_F = [
  ['form', 'Reading what you told us and your photographs'],
  ['choose', 'Choosing three designs and checking every screen'],
  ['publish', 'Publishing the three previews'],
  ['package', 'Preparing the downloads'],
];
export const UPLOAD = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.(jpg|png|webp)$/;
// what an uploaded file is, from its first bytes (never from what the browser says it is)
export function imageType(buf) {
  if (!buf || buf.length < 12) return '';
  if (buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff) return 'jpg';
  if (buf.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) return 'png';
  if (buf.subarray(0, 4).toString('latin1') === 'RIFF' && buf.subarray(8, 12).toString('latin1') === 'WEBP') return 'webp';
  return '';
}
// the form a job may carry: the name is needed, everything else is optional; files only as uploads of this server
export function formProblem(form) {
  if (!form || typeof form !== 'object' || Array.isArray(form)) return 'the form is missing';
  if (!String(form.name || '').trim()) return 'the name of the business is needed';
  if (JSON.stringify(form).length > 200000) return 'the form is too long';
  const photos = form.photos ?? [];
  if (!Array.isArray(photos) || photos.length > 24) return 'at most 24 photographs';
  for (const p of photos) if (!p || !UPLOAD.test(String(p.file || ''))) return 'a photograph was not uploaded here';
  if (form.logo && !UPLOAD.test(String(form.logo.file || ''))) return 'the logo was not uploaded here';
  return '';
}
// what a visitor may add beside an address (web/app.html): up to six screenshots of their product (uploads of this
// server), the kind of business (one of the template niches) and what visitors should do (the button's words)
export const KINDS = ['software', 'app', 'restaurant', 'hotel', 'clinic', 'law', 'service', 'shop', 'school', 'person', 'corporate', 'nonprofit', 'venue'];
export function extrasProblem(o) {
  const s = o?.screens ?? [];
  if (!Array.isArray(s) || s.length > 6) return 'at most 6 screenshots';
  for (const f of s) if (!UPLOAD.test(String(f || ''))) return 'a screenshot was not uploaded here';
  if (o?.niche && !KINDS.includes(String(o.niche))) return 'unknown kind of business';
  if (o?.goal && String(o.goal).length > 80) return 'what visitors should do: at most 80 characters';
  return '';
}
// what the capture measured on the page (geometry.json: places in the page's own 1440-wide pixels), as events the
// working screen draws where they happened: the agents frame a section, read the headline, lift a picture. Only what
// was measured; a place without all four numbers is left out, and so is anything the capture did not find.
export function pageEvents(dir) {
  const J = f => { try { return JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')); } catch { return null; } };
  const g = J('geometry.json') || {}, inv = J('inventory.json') || {}, ev = [];
  const R = r => r && ['x', 'y', 'w', 'h'].every(k => Number.isFinite(r[k])) && r.w > 8 && r.h > 8 ? { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.w), h: Math.round(r.h) } : null;
  const say = (role, text, rect) => { const r = R(rect); if (r) ev.push({ role, text: String(text).replace(/\s+/g, ' ').slice(0, 90), rect: r }); };
  const q = t => `“${String(t || '').replace(/\s+/g, ' ').trim().slice(0, 40)}”`;
  if (g.nav) say('Reader', `Menu · ${Number(g.nav.links) || 0} links`, g.nav.rect);
  if (g.logo) say('Type', 'Logo found', g.logo);
  if (g.h1) say('Reader', `Headline · ${q(g.h1.text)}`, g.h1.rect);
  // a section is a band of the page, not the wrapper that holds all of it (production, automateed.com: "Section 1" was 38 903 px
  // high); a picture is one a visitor would call a picture, not the logo measured a second time
  const logo = R(g.logo), same = (a, b) => a && b && Math.abs(a.x - b.x) < 4 && Math.abs(a.y - b.y) < 4 && Math.abs(a.w - b.w) < 4;
  const secs = (g.sections || []).filter(x => R(x.rect) && x.rect.h <= 1800).slice(0, 8), imgs = (g.images || []).filter(x => R(x.rect) && x.rect.w >= 200 && x.rect.h >= 120 && !same(R(x.rect), logo)).slice(0, 6), heads = (g.headings || []).filter(x => R(x.rect) && x.text).slice(0, 5), ctas = (g.ctas || []).filter(x => R(x.rect) && x.text).slice(0, 3);
  for (let i = 0; i < Math.max(secs.length, imgs.length, heads.length, ctas.length); i++) {   // down the page together, not one kind after another
    if (secs[i]) say('Layout', `Section ${i + 1} · ${Number(secs[i].words) || 0} words`, secs[i].rect);
    if (heads[i]) say('Copy', `Heading · ${q(heads[i].text)}`, heads[i].rect);
    if (imgs[i]) say('Photos', `Picture ${i + 1} · ${Number(imgs[i].w) || 0}×${Number(imgs[i].h) || 0}`, imgs[i].rect);
    if (ctas[i]) say('Copy', `Button · ${q(ctas[i].text)}`, ctas[i].rect);
  }
  const cc = inv.colors, cols = [...new Set((Array.isArray(cc) ? cc : [...(cc?.bg || []), ...(cc?.buttons || [])]).map(c => typeof c === 'string' ? c : c?.c).filter(c => /^#[0-9a-f]{3,8}$/i.test(String(c))))].slice(0, 4);
  if (cols.length) ev.push({ role: 'Colour', text: `Colours · ${cols.join(' ')}` });
  const fonts = (inv.typography?.families || inv.typography?.fonts || []).map(f => typeof f === 'string' ? f : f?.family || f?.name).filter(Boolean).slice(0, 2);
  if (fonts.length) ev.push({ role: 'Type', text: `Typefaces · ${fonts.join(', ')}`.slice(0, 90) });
  return { events: ev, pageHeight: Number.isFinite(g.pageHeight) ? Math.max(900, Math.min(7000, Math.round(g.pageHeight))) : 0 };
}
export const formFiles = form => [...(form.photos || []).map(p => p.file), ...(form.logo?.file ? [form.logo.file] : [])].filter(f => UPLOAD.test(String(f)));

export const enabled = env => env.TEMPLATES_MODE === '1';

/* The picture library the build will find, found the way lib/templates/pictures.py root_of finds it ($SWARMSITE_LIBRARY,
   a folder that holds media/library; else the repo's; `none` switches it off), counted at boot: the image once shipped
   without media/ (Dockerfile) and every job said `library 0` without anyone being told.
   → { root, pictures: rows that name a family, a palette and a file, missing: of those, files that are not there } */
export function libraryCount(env, repoRoot) {
  const v = env.SWARMSITE_LIBRARY;
  for (const c of v === 'none' ? [] : [v, repoRoot]) {
    if (!c) continue;
    const lib = path.join(c, 'media', 'library'), f = path.join(lib, 'library.json');
    if (!fs.existsSync(f)) continue;
    let rows; try { rows = JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return { root: c, pictures: 0, missing: 0, error: 'library.json does not read' }; }
    rows = (Array.isArray(rows) ? rows : []).filter(r => r && r.family && r.palette && typeof r.src === 'string');
    return { root: c, pictures: rows.length, missing: rows.filter(r => !fs.existsSync(path.join(c, r.src))).length };
  }
  return { root: null, pictures: 0, missing: 0 };
}
export const SLUG = /^[a-z0-9][a-z0-9_-]{0,63}$/;
const READER = 'import sys; sys.path.insert(0, "lib/swarm"); import agents, json; f = agents.reader(sys.argv[1]); assert f, "reader did not produce a factsheet"; print(json.dumps({"what": f.get("what", ""), "n": len(f.get("facts", []))}))';
const lastJson = out => String(out || '').trim().split('\n').reverse().map(l => { try { return JSON.parse(l); } catch { return null; } }).find(x => x && typeof x === 'object');
const walk = (dir, base = dir) => fs.existsSync(dir) ? fs.readdirSync(dir, { withFileTypes: true }).flatMap(e => e.isDirectory() ? walk(path.join(dir, e.name), base) : [path.relative(base, path.join(dir, e.name))]) : [];
const TYPE = { '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.gif': 'image/gif', '.svg': 'image/svg+xml', '.avif': 'image/avif', '.mp4': 'video/mp4', '.webm': 'video/webm' };

/* deps: { job, dir, jobRoot, run, upload(local, key, type) → public url, uploadPrivate(local, key, type), publicBase(key) → url,
           self, setStep(id, status, note), emit(events), save(result), chrome, readerTimeoutMs,
           fetchUpload(file, local) — a form job's uploaded photograph, from the private bucket } */
export async function runTemplateJob(deps) {
  const { job, dir, jobRoot, run } = deps; const t0 = Date.now(); const timings = {};
  const result = { ...(job.result || {}), mode: 'templates' };
  const step = async (id, fn) => { await deps.setStep(id, 'running'); const s = Date.now(); const r = await fn(); timings[id] = Date.now() - s; await deps.setStep(id, 'done', `${Math.round(timings[id] / 1000)}s`); return r; };

  const fromForm = job.options?.source === 'form';
  const extra = [];
  if (fromForm) await step('form', async () => {   // the form and the photographs, written where the build reads them
    const form = job.options.form || {}; const photos = path.join(dir, 'uploads');
    fs.mkdirSync(photos, { recursive: true });
    for (const f of formFiles(form)) await deps.fetchUpload(f, path.join(photos, f));
    fs.writeFileSync(path.join(dir, 'form.json'), JSON.stringify(form));
    extra.push('--form', path.join(dir, 'form.json'), '--photos', photos);
    await deps.emit([{ role: 'Reader', text: `${formFiles(form).length} photograph${formFiles(form).length === 1 ? '' : 's'} from you` }]);
  });
  else await step('capture', async () => {
    try {
      await run('node', ['lib/pipeline/capture.mjs', job.url, '--out', jobRoot, ...(deps.chrome ? ['--chrome', deps.chrome] : [])], { timeoutMs: 420000, onLine: line => { const item = lastJson(line); if (item?.event) deps.emit([item.event]); } });
    } catch (e) { const bp = path.join(dir, 'blocked.json'); if (fs.existsSync(bp)) throw new Error(JSON.parse(fs.readFileSync(bp, 'utf8')).reason + ' Try the www/non-www address, or a page that is not behind the check.'); throw e; }
    if (fs.existsSync(path.join(dir, 'before-hero.jpg'))) result.beforeUrl = await deps.upload(path.join(dir, 'before-hero.jpg'), `${job.id}/before.jpg`, 'image/jpeg');
    // the whole page and where each thing stands on it: the working screen shows the agents going down the real page
    try { const pe = pageEvents(dir);
      if (fs.existsSync(path.join(dir, 'before-full.jpg')) && pe.pageHeight) { result.beforeFullUrl = await deps.upload(path.join(dir, 'before-full.jpg'), `${job.id}/before-full.jpg`, 'image/jpeg'); result.pageHeight = pe.pageHeight; }
      const seen = result.beforeFullUrl ? pe.events : pe.events.filter(e => !e.rect || e.rect.y + Math.min(e.rect.h, 200) <= 900);   // with only the first screen kept, only what stands on it
      if (result.beforeUrl || result.beforeFullUrl) await deps.save(result);   // the picture of the page is in the job before the events that are drawn on it (it used to arrive with the designs, when the working screen was already gone)
      if (seen.length) await deps.emit(seen);
    } catch { /* the pictures of the work are never worth the job */ }
    // "I built a first version of my app": their screenshots, fetched like a form's photographs, kept in their order
    const shots = (job.options?.screens || []).filter(f => UPLOAD.test(String(f))).slice(0, 6);
    if (shots.length) { const sd = path.join(dir, 'screens'); fs.mkdirSync(sd, { recursive: true });
      for (const [i, f] of shots.entries()) await deps.fetchUpload(f, path.join(sd, `${String(i + 1).padStart(2, '0')}-${f}`));
      extra.push('--screens', sd); await deps.emit([{ role: 'Reader', text: `${shots.length} screenshot${shots.length === 1 ? '' : 's'} from you` }]); }
    if (KINDS.includes(String(job.options?.niche || ''))) extra.push('--kind', String(job.options.niche));
    const goal = String(job.options?.goal || '').replace(/\s+/g, ' ').trim().slice(0, 40); if (goal) extra.push('--goal', goal);
  });
  if (!fromForm) await step('read', async () => {
    const f = lastJson(await run('python3', ['-c', READER, dir], { timeoutMs: deps.readerTimeoutMs || 180000 })) || {};
    await deps.emit([{ role: 'Reader', text: String(f.what || '').slice(0, 120) }, { role: 'Reader', text: `${Number(f.n) || 0} source facts` }]);
  });
  const tdir = path.join(dir, 'templates'); const base = deps.publicBase(`${job.id}/t/`);
  const built = await step('choose', async () => {
    const r = lastJson(await run('python3', ['lib/templates/job.py', 'build', dir, '--out', tdir, '--base', base, ...extra], { timeoutMs: 600000 }));
    if (!r || !Array.isArray(r.chosen) || !Array.isArray(r.shown)) throw new Error('templates build did not report');
    // in the visitor's words: a design by its number among those shown, never by the template it was made with
    const shownNo = r.shown.filter(s => SLUG.test(s));
    await deps.emit(r.chosen.map(c => { const n = shownNo.indexOf(c.slug); return { role: 'QA', text: n >= 0 && c.ok ? `${designName(n)}: every screen passes` : `A design was not shown — ${scrub((c.failed || []).join(', '))}` }; }));
    return r;
  });
  const variants = await step('publish', async () => {
    const shown = built.shown.filter(s => SLUG.test(s));
    for (const rel of walk(path.join(tdir, 'media'))) await deps.upload(path.join(tdir, 'media', rel), `${job.id}/t/media/${rel.split(path.sep).join('/')}`, TYPE[path.extname(rel).toLowerCase()] || 'application/octet-stream');
    const out = [];
    // a design's address, its preview file and everything a visitor sees name it by its id (v1 …) and its name (Design 1 …);
    // `slug` (the template) stays in the job for the server (server/designs.mjs, owner's rule of 2026-11-12)
    for (const [i, slug] of shown.entries()) {
      const id = publicId({}, i);
      await deps.upload(path.join(tdir, 'pub', `${slug}.html`), `${job.id}/t/${id}.html`, 'text/html');
      const c = built.chosen.find(x => x.slug === slug) || {};
      out.push({ slug, id, name: designName(i), approach: c.approach || '', why: c.why || '', url: `${deps.self}/t/${job.id}/${id}`, package: 'pending', ...(c.made ? { made: c.made } : {}),
        ...(c.drops?.length ? { drops: c.drops } : {}), ...(c.fallback ? { fallback: true, niche: c.niche } : {}) });
    }
    // each design's cover: its first screen photographed at rest (lib/templates/covers.mjs), so the chooser never shows a
    // page caught half-drawn. A cover that could not be taken leaves that card to its live preview — never the job.
    if (shown.length) try {
      const cd = path.join(tdir, 'covers'), r = lastJson(await run('node', ['lib/templates/covers.mjs', cd, ...shown.map(s => path.join(tdir, `${s}.html`))], { timeoutMs: 120000 })) || {};
      for (const v of out) { const f = r.covers?.[v.slug]; if (f && fs.existsSync(path.join(cd, f))) v.cover = await deps.upload(path.join(cd, f), `${job.id}/t/${v.id}-cover.jpg`, 'image/jpeg'); }
    } catch (e) { await deps.emit([{ role: 'QA', text: 'The covers could not be photographed; the previews are shown live' }]); }
    // the job's data store: the client's data, and each variant's own (with its family of made pictures), in the private
    // bucket. The "site from nothing" form will write the same data.json, and the editor will keep its edits as a patch
    // over it, so that a template can be switched keeping every edit (BRIEF-engine.md, steps 8 and 9).
    const store = { data: `${job.id}/data.json`, variants: {} };
    await deps.uploadPrivate(path.join(tdir, 'data.json'), store.data, 'application/json');
    for (const slug of shown) { const f = path.join(tdir, `${slug}.data.json`); if (fs.existsSync(f)) { store.variants[slug] = `${job.id}/${slug}.data.json`; await deps.uploadPrivate(f, store.variants[slug], 'application/json'); } }
    result.templates = { variants: out, niche: built.niche, pictures: built.pictures, not_shown: built.chosen.filter(c => !shown.includes(c.slug)).map(c => ({ slug: c.slug, failed: c.failed,
      // what the gate measured, so a design held back on the server can be traced from the job itself (three readings a check)
      where: Object.fromEntries(Object.entries(c.gate || {}).map(([k, v]) => [k, (Array.isArray(v) ? v : [v]).slice(0, 3)])) })),
      fallback: !!built.fallback,   // true: the client's own niche had fewer than three, a neighbouring niche's filled the rest
      rejected: (built.rejected || []).slice(0, 60), media: built.media, group: built.group || null, store, timings_ms: { ...built.timings_ms } };
    if (fromForm) {   // what the form left out, in the visitor's terms: an empty field is a section left out, said so
      result.source = 'form';
      try { result.templates.left_out = (JSON.parse(fs.readFileSync(path.join(tdir, 'adapter.json'), 'utf8')).gaps || []).slice(0, 30); } catch { result.templates.left_out = []; }
    }
    await deps.save(result);   // the chooser can show them now
    return out;
  });
  await step('package', async () => {
    for (const v of variants) {
      const zip = path.join(tdir, `${v.slug}.zip`); let r;
      try { r = lastJson(await run('python3', ['lib/templates/job.py', 'package', tdir, v.slug, zip, '--verify'], { timeoutMs: 240000 })); }
      catch (e) { r = { ok: false, why: ['the package could not be made: ' + String(e.message).slice(-200)] }; }   // a crash refuses the package, never the previews
      if (r?.ok && fs.existsSync(zip)) { await deps.uploadPrivate(zip, `${job.id}/${v.slug}.zip`, 'application/zip'); v.package = 'ready'; v.bytes = r.bytes; }
      else { v.package = 'refused'; v.package_why = (r?.why || []).slice(0, 3); }
    }
  });
  const ledger = (() => { try { return JSON.parse(fs.readFileSync(path.join(dir, 'budget.json'), 'utf8')); } catch { return null; } })();
  result.templates.timings_ms = { ...result.templates.timings_ms, steps: timings };
  result.budget = ledger;   // the reader's call, priced: what this visitor cost
  result.seconds = Math.round((Date.now() - t0) / 1000);
  return result;
}

/* Who may have a package. A preview is free and open; a package needs an account and, once payment exists, a paid
   order. The payment hook is this function: until payment is built it lets a signed-in visitor through only where
   the deployment says packages are free (PACKAGES_FREE=1, for testing), and otherwise answers 402 with pay: true —
   the place the checkout will hang. */
export function mayDownload({ user, job, slug, env }) {
  if (!user) return { status: 401, body: { error: 'Sign in to download your page.', login: true } };
  const v = (job?.result?.templates?.variants || []).find(x => x.slug === slug);
  if (!v) return { status: 404, body: { error: 'not found' } };
  if (v.package === 'pending') return { status: 409, body: { error: 'The download is still being prepared.', pending: true } };
  if (v.package !== 'ready') return { status: 409, body: { error: 'This design cannot be downloaded: its package did not match the preview.', why: (v.package_why || []).map(scrub) } };
  const pay = payGate({ env, row: job, slug, user });   // free for testing, paid by this account, or 402 with where to pay
  return pay || { status: 200 };
}

// the preview file of a design in the public bucket: by its id since ids exist, by the template before
export const previewKey = (row, id, slug) => { const vs = row?.result?.templates?.variants || []; const v = vs.find(x => x.slug === slug); return `${id}/t/${v && v.id ? v.id : slug}.html`; };

// which preview page of a job may be served
export function previewable(row, slug) {
  if (!row || !SLUG.test(String(slug || ''))) return false;
  if (!['running', 'done'].includes(row.status)) return false;
  return (row.result?.templates?.variants || []).some(v => v.slug === slug);
}
