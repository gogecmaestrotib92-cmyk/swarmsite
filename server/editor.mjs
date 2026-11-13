/* editor.mjs — the editor on the page (BRIEF-engine.md step 9), the server's half. The edits are a patch over the job's
   data (lib/templates/edit.py), kept in the private bucket beside the data as <job>/edits.json, so that switching to
   another of the three designs keeps every edit. No model.

   Anyone who may see a preview may try edits on it (render and check answer with the edited page, nothing is kept);
   keeping them needs an account, and the first to keep edits on a job without an owner becomes its owner — as for the
   download. Everything is passed in, so the flow is tested without a database, a bucket or Chrome:
     deps: { readPrivate(key) → Buffer | null, writePrivate(key, buf, type), publishPublic(local, key, type) → url,
             publicBase(key) → url, python(args) → stdout, gate(file) → {ok, failed, checks}, tmp() → dir } */
import fs from 'node:fs'; import path from 'node:path'; import { spawn } from 'node:child_process';
import { SLUG, UPLOAD } from './templates.mjs';

/* The gate on one page (lib/qa/template_gate.mjs), for the editor's check. The gate exits 1 when the page fails — that is
   its answer, printed as a line of JSON, not a crash. (Until 2026-11-13 the worker ran it through a helper that rejects
   every non-zero exit and threw the answer away, so on production a failing page was always reported as failed: ['tool']
   and the editor could never name the line that did not read.) Only when nothing was printed did the tool not run. */
export const gateAnswer = out => String(out || '').trim().split('\n').reverse().map(l => { try { return JSON.parse(l); } catch { return null; } }).find(x => x && x.page) || { ok: false, failed: ['tool'] };
export const runGate = (file, { root, ms = 90000, node = 'node' } = {}) => new Promise(ok => { let out = ''; const p = spawn(node, ['lib/qa/template_gate.mjs', file], { cwd: root, env: process.env }); const t = setTimeout(() => p.kill('SIGKILL'), ms);
  p.stdout.on('data', d => { out += d; if (out.length > 8e6) p.kill('SIGKILL'); }); p.stderr.on('data', () => {}); p.on('error', () => { clearTimeout(t); ok(gateAnswer('')); }); p.on('close', () => { clearTimeout(t); ok(gateAnswer(out)); }); });

export const MAX_OPS = 400;
const OP = new Set(['text', 'picture', 'hide', 'show', 'move', 'palette', 'photo']);
const lastJson = out => String(out || '').trim().split('\n').reverse().map(l => { try { return JSON.parse(l); } catch { return null; } }).find(x => x && typeof x === 'object');

// the shape of a patch, before edit.py judges each operation against the data
export function opsProblem(ops) {
  if (!Array.isArray(ops)) return 'the edits are a list';
  if (ops.length > MAX_OPS) return `at most ${MAX_OPS} edits; keep them, then go on`;
  if (JSON.stringify(ops).length > 200000) return 'the edits are too long';
  if (ops.some(o => !o || typeof o !== 'object' || Array.isArray(o) || !OP.has(o.op))) return 'not an edit';
  return '';
}

export function makeEditor(deps) {
  const cache = new Map();   // data.json per store key: it does not change once the job has published
  const read = async key => { if (cache.has(key)) return cache.get(key); const b = await deps.readPrivate(key); if (!b) return null; const v = JSON.parse(String(b)); cache.set(key, v); if (cache.size > 60) cache.delete(cache.keys().next().value); return v; };
  const storeKey = (row, slug) => { const s = row?.result?.templates?.store || {}; return s.variants?.[slug] || s.data || null; };
  const withFiles = async (row, slug, ops, fn) => {
    const key = storeKey(row, slug); const data = key && await read(key); if (!data) { const e = new Error('this job keeps no data to edit'); e.status = 404; throw e; }
    const dir = fs.mkdtempSync(path.join(deps.tmp(), 'edit-'));
    try { fs.writeFileSync(path.join(dir, 'data.json'), JSON.stringify(data)); fs.writeFileSync(path.join(dir, 'ops.json'), JSON.stringify(ops || [])); return await fn(dir); }
    finally { fs.rmSync(dir, { recursive: true, force: true }); } };
  const saved = async row => { const b = await deps.readPrivate(`${row.id}/edits.json`); try { return b ? JSON.parse(String(b)).ops || [] : []; } catch { return []; } };

  return {
    saved,
    // what the editor shows: the page's texts, pictures, sections and colours after the edits, and what was refused
    async describe(row, slug, ops) {
      return withFiles(row, slug, ops, async dir => lastJson(await deps.python(['lib/templates/edit.py', 'describe', path.join(dir, 'data.json'), '--ops', path.join(dir, 'ops.json'), '--slug', slug])) || {});
    },
    // the edited page, its media where the preview's are
    async render(row, slug, ops) {
      return withFiles(row, slug, ops, async dir => String(await deps.python(['lib/templates/edit.py', 'render', path.join(dir, 'data.json'), slug, '--ops', path.join(dir, 'ops.json'), '--base', deps.publicBase(`${row.id}/t/`)])));
    },
    // the readability gate on the edited page: the lines that do not read, in the visitor's words
    async check(row, slug, ops) {
      return withFiles(row, slug, ops, async dir => {
        const f = path.join(dir, `${slug}.html`);
        fs.writeFileSync(f, String(await deps.python(['lib/templates/edit.py', 'render', path.join(dir, 'data.json'), slug, '--ops', path.join(dir, 'ops.json'), '--base', deps.publicBase(`${row.id}/t/`)])));
        const g = await deps.gate(f) || {}; const c = g.checks || {};
        return { ok: !!g.ok && !(g.failed || []).length, failed: g.failed || [], unread: (c.legible || []).slice(0, 12).map(x => ({ text: String(x.text || '').slice(0, 120), ratio: x.ratio, at: x.at })),
          overlap: (c.overlap || []).length, sideways: (c.sideways || []).length,
          unseen: (c.unseen || []).slice(0, 6).map(x => ({ alt: String(x.alt || '').slice(0, 80), at: x.at })) };   // a picture that cannot be seen where it stands, by the name the page gives it
      });
    },
    // a photograph the visitor uploads while editing: measured, published beside the preview's media, offered as their own
    async photo(row, file) {
      if (!UPLOAD.test(String(file || ''))) { const e = new Error('not an upload of this server'); e.status = 400; throw e; }
      const b = await deps.readPrivate(`uploads/${file}`); if (!b) { const e = new Error('the photograph is gone'); e.status = 404; throw e; }
      const dir = fs.mkdtempSync(path.join(deps.tmp(), 'photo-'));
      try { const f = path.join(dir, file); fs.writeFileSync(f, b);
        const wh = lastJson(await deps.python(['lib/templates/edit.py', 'measure', f])) || {}; if (!(wh.w > 0 && wh.h > 0)) { const e = new Error('not a picture that could be read'); e.status = 400; throw e; }
        const src = `media/upload/${file}`; await deps.publishPublic(f, `${row.id}/t/${src}`, file.endsWith('.png') ? 'image/png' : file.endsWith('.webp') ? 'image/webp' : 'image/jpeg');
        return { op: 'photo', src, w: wh.w, h: wh.h }; }
      finally { fs.rmSync(dir, { recursive: true, force: true }); } },
    async save(row, ops) { await deps.writePrivate(`${row.id}/edits.json`, Buffer.from(JSON.stringify({ ops, at: new Date().toISOString() })), 'application/json'); return { kept: ops.length }; },
  };
}

// who may keep edits: an account; the job's owner, or anyone while it has none (they become its owner)
export function mayKeep({ user, row }) {
  if (!user) return { status: 401, body: { error: 'Sign in to keep your edits.', login: true } };
  if (row?.user_id && row.user_id !== user.id) return { status: 403, body: { error: 'These designs belong to another account.' } };
  return { status: 200, claim: !row?.user_id };
}
export const editable = (row, slug) => !!row && SLUG.test(String(slug || '')) && row.status === 'done' && (row.result?.templates?.variants || []).some(v => v.slug === slug) && !!row.result?.templates?.store;
