/* cleanup.mjs — photographs visitors uploaded (uploads/ in the private packages bucket) are not kept for ever.
   Removed: an upload older than DAYS whose job is older than DAYS and has nobody's package — no account downloaded it,
   kept edits on it or published it (each of those makes the job someone's: jobs.user_id) — and an upload no job
   names at all (sent, then never used). Kept: everything of a job that is someone's, and anything younger than DAYS.
   Payment is not built; once it is, a paid job is someone's too, by the same field.

   Runs in the worker once on boot and then every 24 h. It logs counts only, never a file name or anything of a visitor.
   Everything is passed in, so it is tested without a bucket or a database:
     deps: { listUploads() → [{name, created_at}], jobs(sinceIso) → [{id, created_at, user_id, options}],
             editsOf(id) → ops | null, remove(names[]), now(), log(text) } */
import { UPLOAD } from './templates.mjs';

export const DAYS = 14;
const DAY = 86400e3;

// the uploads a job names: its form's photographs and logo, and photographs added while editing (kept edits)
export function named(job, ops) {
  const f = job?.options?.form || {}; const out = new Set();
  for (const p of Array.isArray(f.photos) ? f.photos : []) if (UPLOAD.test(String(p?.file || ''))) out.add(p.file);
  if (UPLOAD.test(String(f.logo?.file || ''))) out.add(f.logo.file);
  for (const o of Array.isArray(ops) ? ops : []) { const m = /^media\/upload\/(.+)$/.exec(String(o?.op === 'photo' ? o.src : '')); if (m && UPLOAD.test(m[1])) out.add(m[1]); }
  return out;
}

// which uploads go: pure, so the rule is tested on its own
export function removals({ uploads, jobs, edits = new Map(), now, days = DAYS }) {
  const cut = now - days * DAY, keep = new Set(), seen = new Set();
  for (const j of jobs) {
    const files = named(j, edits.get(j.id)); for (const f of files) seen.add(f);
    if (j.user_id || Date.parse(j.created_at) > cut) for (const f of files) keep.add(f);   // someone's, or still young
  }
  return uploads.filter(u => UPLOAD.test(u.name) && Date.parse(u.created_at) < cut && !keep.has(u.name)).map(u => u.name);
}

export async function runCleanup(deps, days = DAYS) {
  const now = deps.now();
  const uploads = await deps.listUploads();
  if (!uploads.length) { deps.log('cleanup: 0 uploads'); return { removed: 0, kept: 0 }; }
  // every job that could name an upload: anything since the oldest upload, one day either side
  const oldest = Math.min(...uploads.map(u => Date.parse(u.created_at)).filter(Number.isFinite));
  const jobs = await deps.jobs(new Date(oldest - DAY).toISOString());
  const edits = new Map();
  for (const j of jobs) if (j.user_id) { const ops = await deps.editsOf(j.id); if (ops) edits.set(j.id, ops); }
  const gone = removals({ uploads, jobs, edits, now, days });
  for (let i = 0; i < gone.length; i += 100) await deps.remove(gone.slice(i, i + 100));
  deps.log(`cleanup: ${gone.length} uploads removed, ${uploads.length - gone.length} kept`);
  return { removed: gone.length, kept: uploads.length - gone.length };
}
