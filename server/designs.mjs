/* designs.mjs — what a visitor calls a design. Owner's rule (2026-11-12): a visitor never sees the name of a reference
   site a template was rebuilt from — not in the chooser, an address, a file name, a page, an email or a payment.

   Inside the server a variant keeps its template's slug (it is what lib/templates renders). Outside it has
     an id     v1, v2, v3 — its place among the job's shown designs: the address /t/<job>/v1, the preview file, Stripe
     a name    "Design 1", "Design 2", "Design 3"
   publicJob() is the job as the web app reads it (GET /jobs/:id); internalSlug() turns an address back into the slug.

   A job made before ids existed has variants without `id`: its ids are their places, and its old addresses (which
   named the template) keep working; a job made since answers only to its ids. */
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';

const LIB = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'lib', 'templates');
// every template of the library: the words that must never reach a visitor in the server's own sentences
export const TEMPLATE_SLUGS = (() => { try { return fs.readdirSync(LIB, { withFileTypes: true }).filter(e => e.isDirectory() && fs.existsSync(path.join(LIB, e.name, 'render.py'))).map(e => e.name).sort(); } catch { return []; } })();
const SLUG_WORD = TEMPLATE_SLUGS.length ? new RegExp(`(?<![a-z0-9])(?:${TEMPLATE_SLUGS.map(s => s.replace(/[^a-z0-9]/gi, m => '\\' + m)).join('|')})(?![a-z0-9])`, 'gi') : null;

export const publicId = (v, i) => (v && typeof v.id === 'string' && v.id) || `v${i + 1}`;
export const designName = i => `Design ${i + 1}`;
export const PUBLIC_ID = /^v[1-9][0-9]?$/;

// a sentence the server wrote about a template (a refusal, a gate's verdict): the template's name taken out
export const scrub = text => SLUG_WORD ? String(text ?? '').replace(SLUG_WORD, 'the design') : String(text ?? '');

const variantsOf = row => row?.result?.templates?.variants || [];
// the slug behind an address's design id ('' when the job shows no such design)
export function internalSlug(row, id) {
  const vs = variantsOf(row), p = String(id || '');
  const i = vs.findIndex((v, k) => publicId(v, k) === p); if (i >= 0) return vs[i].slug;
  const j = vs.findIndex(v => !v.id && v.slug === p); return j >= 0 ? vs[j].slug : '';   // a job from before ids: its old links
}
// the design id of a slug of this job ('' when it shows no such design)
export function publicOf(row, slug) { const vs = variantsOf(row); const i = vs.findIndex(v => v.slug === slug); return i >= 0 ? publicId(vs[i], i) : ''; }
export function nameOf(row, slug) { const vs = variantsOf(row); const i = vs.findIndex(v => v.slug === slug); return i >= 0 ? (vs[i].name || designName(i)) : 'the design'; }

// a publish or "download with my edits" state as the visitor follows it: the design's id, and no private file name
const state = (row, s) => { if (!s || typeof s !== 'object') return s; const { package: _key, slug, why, ...rest } = s; return { ...rest, ...(slug !== undefined ? { slug: publicOf(row, slug) } : {}), ...(why ? { why: [].concat(why).map(scrub) } : {}) }; };

/* the job as GET /jobs/:id sends it: every design by id and name, the reasons without a template's name, the private
   store's file names left out. `slug` stays the field the pages read, now holding the design's id. */
export function publicJob(row) {
  if (!row || !row.result || typeof row.result !== 'object') return row;
  const r = { ...row.result }, t = r.templates;
  if (Array.isArray(r.events)) r.events = r.events.map(e => (e && e.role === 'QA' ? { ...e, text: scrub(e.text) } : e));
  if (t && typeof t === 'object') {
    const vs = Array.isArray(t.variants) ? t.variants : [];
    r.templates = {
      ...(t.niche ? { niche: t.niche } : {}), ...(t.pictures != null ? { pictures: t.pictures } : {}), ...(t.group ? { group: t.group } : {}), ...(t.media ? { media: t.media } : {}),
      ...(t.left_out ? { left_out: t.left_out } : {}), ...(t.timings_ms ? { timings_ms: t.timings_ms } : {}),
      store: !!t.store,   // the editor works on what a finished job kept; where it keeps it is the server's
      variants: vs.map((v, i) => { const id = publicId(v, i);
        return { slug: id, id, name: v.name || designName(i), url: String(v.url || '').replace(/\/[^/]*$/, '/' + id), approach: v.approach || '', why: scrub(v.why), package: v.package,
          ...(v.package_why ? { package_why: v.package_why.map(scrub) } : {}), ...(v.bytes != null ? { bytes: v.bytes } : {}), ...(/^https:\/\/[^\s"<>]+-cover\.jpg$/.test(String(v.cover || '')) ? { cover: v.cover } : {}), ...(v.made ? { made: { family: v.made.family, palette: v.made.palette } } : {}) }; }),
      rejected: (t.rejected || []).map((x, i) => ({ name: `Library design ${i + 1}`, why: scrub(x?.why) })),
      not_shown: (t.not_shown || []).map(x => ({ failed: (x?.failed || []).map(scrub) })),
    };
  }
  if (r.paid && typeof r.paid === 'object') r.paid = Object.fromEntries(Object.entries(r.paid).map(([k, v]) => [publicOf(row, k) || 'design', { at: v?.at }]));
  for (const k of ['edited', 'publish']) if (r[k]) r[k] = state(row, r[k]);
  return { ...row, result: r };
}

// the download's file name: the visitor's own site and the design's number, nothing else
export const downloadName = (row, slug) => {
  const host = (() => { try { return new URL(row.url).hostname.replace(/^www\./, '').replace(/[^a-z0-9.-]/gi, '') || 'site'; } catch { return 'site'; } })();
  return `${host}-${nameOf(row, slug).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'design'}.zip`;
};
