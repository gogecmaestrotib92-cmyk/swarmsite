/* Swarmsite server — API + worker in one process.
   POST /jobs {url}            → {id}
   GET  /jobs/:id              → {status, step, steps, result, error}
   Worker: polls `jobs` (status=queued) and runs the pipeline:
     capture (Playwright) → diagnose (py) → direct (LLM, py) → render (py) → qa (py) → upload (Supabase storage)
   Env: SUPABASE_URL, SUPABASE_SERVICE_KEY, ANTHROPIC_API_KEY, PORT, PUBLIC_ORIGIN (CORS), CHROME_PATH (optional) */
import express from 'express'; import cors from 'cors'; import { createClient } from '@supabase/supabase-js';
import { spawn } from 'node:child_process'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url)); const ROOT = path.resolve(HERE, '..');
const sb = createClient(process.env.SUPABASE_URL || 'https://placeholder.supabase.co', process.env.SUPABASE_SERVICE_KEY || 'placeholder', { auth: { persistSession: false } });
const BUCKET = 'previews'; const OUT = path.join(ROOT, 'out');
const STEPS = [
  ['capture', 'Reading your site: text, photos, logo, colours'],
  ['diagnose', 'Auditing: words, sections, type, nav'],
  ['direct', 'Art direction: concept, beats, copy'],
  ['render', 'Building: type, photos, motion'],
  ['qa', 'Checking every screen at 1440 and 390'],
  ['upload', 'Publishing the preview'],
];

const app = express(); app.use(cors({ origin: process.env.PUBLIC_ORIGIN ? process.env.PUBLIC_ORIGIN.split(',') : true })); app.use(express.json({ limit: '1mb' }));
app.get('/', (_, res) => res.json({ ok: true, service: 'swarmsite', steps: STEPS.map(s => s[0]) }));
app.post('/jobs', async (req, res) => {
  let url = String(req.body?.url || '').trim(); if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
  try { new URL(url); } catch { return res.status(400).json({ error: 'bad url' }); }
  if (/localhost|127\.|10\.|192\.168\.|\.internal/i.test(url)) return res.status(400).json({ error: 'not allowed' });
  const { data, error } = await sb.from('jobs').insert({ url, options: req.body?.options || {}, steps: STEPS.map(([id, label]) => ({ id, label, status: 'pending' })) }).select('id').single();
  if (error) return res.status(500).json({ error: error.message });
  res.json({ id: data.id });
});
app.get('/jobs/:id', async (req, res) => {
  const { data, error } = await sb.from('jobs').select('id,url,status,step,steps,result,error,created_at').eq('id', req.params.id).single();
  if (error) return res.status(404).json({ error: 'not found' }); res.json(data);
});
// Preview page: Supabase public storage serves HTML as text/plain (XSS guard), so we proxy it with the right type.
const SELF = process.env.PUBLIC_API || (process.env.RAILWAY_PUBLIC_DOMAIN ? 'https://' + process.env.RAILWAY_PUBLIC_DOMAIN : 'http://localhost:' + (process.env.PORT || 8080));
app.get('/p/:id', async (req, res) => {
  if (!/^[0-9a-f-]{36}$/.test(req.params.id)) return res.status(400).end();
  const { data, error } = await sb.storage.from(BUCKET).download(`${req.params.id}/index.html`);
  if (error || !data) return res.status(404).send('preview not found');
  res.set({ 'content-type': 'text/html; charset=utf-8', 'cache-control': 'public, max-age=300', 'x-frame-options': 'ALLOWALL' });
  res.send(Buffer.from(await data.arrayBuffer()));
});
app.listen(process.env.PORT || 8080, () => console.log('api on', process.env.PORT || 8080));

// ---------- worker ----------
const run = (cmd, args, opts = {}) => new Promise((resolve, reject) => {
  const p = spawn(cmd, args, { cwd: ROOT, env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }, ...opts }); let out = '', err = '';
  p.stdout.on('data', d => out += d); p.stderr.on('data', d => err += d);
  const t = setTimeout(() => { p.kill('SIGKILL'); reject(new Error(cmd + ' timeout')); }, opts.timeoutMs || 300000);
  p.on('close', c => { clearTimeout(t); c === 0 ? resolve(out) : reject(new Error(`${cmd} ${args[0]} exit ${c}: ${err.slice(-800)}`)); });
});
const slugOf = url => url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
async function setStep(job, id, status, note) {
  const steps = job.steps.map(s => s.id === id ? { ...s, status, at: new Date().toISOString(), note } : s); job.steps = steps;
  await sb.from('jobs').update({ step: id, steps, status: 'running' }).eq('id', job.id);
}
async function upload(local, remote, type) {
  const buf = fs.readFileSync(local); const { error } = await sb.storage.from(BUCKET).upload(remote, buf, { contentType: type, upsert: true }); if (error) throw error;
  return sb.storage.from(BUCKET).getPublicUrl(remote).data.publicUrl;
}
async function process_(job) {
  const slug = slugOf(job.url); const dir = path.join(OUT, slug); fs.mkdirSync(dir, { recursive: true });
  const t0 = Date.now(); const timed = async (id, fn) => { await setStep(job, id, 'running'); const s = Date.now(); const r = await fn(); await setStep(job, id, 'done', `${Math.round((Date.now() - s) / 1000)}s`); return r; };
  await timed('capture', async () => {
    await run('node', ['lib/pipeline/capture.mjs', job.url, '--out', 'out', '--chrome', process.env.CHROME_PATH || ''].filter(Boolean), { timeoutMs: 180000 });
    if (fs.existsSync(path.join(dir, 'before-hero.jpg'))) { const beforeUrl = await upload(path.join(dir, 'before-hero.jpg'), `${job.id}/before.jpg`, 'image/jpeg'); await sb.from('jobs').update({ result: { beforeUrl } }).eq('id', job.id); }
  });
  await timed('diagnose', async () => { const out = await run('python3', ['-I', 'lib/audit/diagnose.py', path.join(dir, 'inventory.json')]); fs.writeFileSync(path.join(dir, 'audit.json'), out); });
  await timed('direct', () => run('python3', ['lib/direct/direct.py', dir, process.env.DIRECT_MODEL || 'claude-sonnet-5-5'], { timeoutMs: 240000 }));
  await timed('render', () => run('python3', ['lib/render/render_beats.py', dir]));
  let qa = null; await timed('qa', async () => { try { const o = await run('python3', ['lib/qa/check.py', path.join(dir, 'index.html')], { timeoutMs: 240000 }); qa = o.split('\n').filter(l => /QA score|\[(high|med|low)/.test(l)).join('\n'); } catch (e) { qa = 'qa skipped: ' + e.message.slice(0, 200); } });
  const result = await timed('upload', async () => {
    await upload(path.join(dir, 'index.html'), `${job.id}/index.html`, 'text/html'); const previewUrl = `${SELF}/p/${job.id}`;
    const beforeUrl = fs.existsSync(path.join(dir, 'before-hero.jpg')) ? await upload(path.join(dir, 'before-hero.jpg'), `${job.id}/before.jpg`, 'image/jpeg') : null;
    const direction = JSON.parse(fs.readFileSync(path.join(dir, 'direction.json'), 'utf8'));
    return { previewUrl, beforeUrl, qa, direction: { kind: direction.kind, concept: direction.concept, voice: direction.voice, brand: direction.brand, beats: direction.beats.map(b => b.type), audit_notes: direction.audit_notes }, seconds: Math.round((Date.now() - t0) / 1000) };
  });
  await sb.from('jobs').update({ status: 'done', step: 'done', result, slug }).eq('id', job.id);
}
async function loop() {
  while (true) {
    try {
      const { data: job } = await sb.from('jobs').select('*').eq('status', 'queued').order('created_at').limit(1).maybeSingle();
      if (job) {
        const { data: claimed } = await sb.from('jobs').update({ status: 'running' }).eq('id', job.id).eq('status', 'queued').select('*').maybeSingle();
        if (claimed) { console.log('job', job.id, job.url); try { await process_(claimed); console.log('done', job.id); } catch (e) { console.error('failed', job.id, e.message); await sb.from('jobs').update({ status: 'failed', error: e.message.slice(0, 2000) }).eq('id', job.id); } }
      } else await new Promise(r => setTimeout(r, 2500));
    } catch (e) { console.error('loop', e.message); await new Promise(r => setTimeout(r, 5000)); }
  }
}
if (process.env.SUPABASE_URL) loop(); else console.warn('no SUPABASE_URL: worker idle');
