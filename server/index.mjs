/* Swarmsite server — API + worker in one process.
   POST /jobs {url}            → {id}
   GET  /jobs/:id              → {status, step, steps, result, error}
   Worker: polls `jobs` (status=queued) and runs the pipeline:
     capture (Playwright) → diagnose (py) → direct (LLM, py) → render (py) → qa (py) → upload (Supabase storage)
   Env: SUPABASE_URL, SUPABASE_SERVICE_KEY, ANTHROPIC_API_KEY, PORT, PUBLIC_ORIGIN (CORS), CHROME_PATH (optional) */
import express from 'express'; import cors from 'cors'; import { createClient } from '@supabase/supabase-js';
import { prepareAlternative, publishSelected, verifySelected, verifyAlternative } from './variant_snapshot.mjs';
import { saveCrawlCheckpoint, restoreCrawlCheckpoint } from './crawl_checkpoint.mjs';
import { spawn } from 'node:child_process'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import crypto from 'node:crypto';
import { makeUserOf, allowance, mine } from './auth.mjs';
import { STEPS_T, enabled as templatesEnabled, runTemplateJob, mayDownload, previewable } from './templates.mjs';
import { AsyncLocalStorage } from 'node:async_hooks';
const HERE = path.dirname(fileURLToPath(import.meta.url)); const ROOT = path.resolve(HERE, '..');
const sb = createClient(process.env.SUPABASE_URL || 'https://placeholder.supabase.co', process.env.SUPABASE_SERVICE_KEY || 'placeholder', { auth: { persistSession: false } });
const BUCKET = 'previews'; const OUT = path.join(ROOT, 'out');
// the template path (server/templates.mjs): off unless TEMPLATES_MODE=1; packages live in a bucket that is NOT public
const TEMPLATES = templatesEnabled(process.env); const PACKAGE_BUCKET = process.env.PACKAGE_BUCKET || 'packages';
const WORKER_ID = crypto.randomUUID();
const STEPS = [
  ['capture', 'Reading your landing page: text, photos, logo, colours'],
  ['diagnose', 'Auditing: words, sections, type, nav'],
  ['direct', 'Art direction: concept, beats, copy'],
  ['render', 'Building: type, photos, motion'],
  ['qa', 'Checking every screen at 1440 and 390'],
  ['upload', 'Publishing the preview'],
];

const app = express(); app.use(cors({ origin: process.env.PUBLIC_ORIGIN ? process.env.PUBLIC_ORIGIN.split(',') : true })); app.use(express.json({ limit: '1mb' }));
app.get('/', (_, res) => res.json({ ok: true, service: 'swarmsite', steps: STEPS.map(s => s[0]) }));
// ---- abuse and cost limits: a public endpoint that spends our model credit needs all three ----
// Per-IP guard against one person hammering the queue; the day and queue ceilings are abuse/cost sanity stops,
// not capacity limits — a burst of real visitors must queue, never be turned away (set them in Railway variables).
const RATE = { perIpPerHour: Number(process.env.JOBS_PER_IP_PER_HOUR || 3), perDay: Number(process.env.JOBS_PER_DAY || 5000), maxQueue: Number(process.env.JOBS_MAX_QUEUE || 2000) };
const JOB_MINUTES = Number(process.env.JOB_MINUTES || 4); // typical wall time of one job, for queue estimates
const NOTIFY = { key: process.env.RESEND_API_KEY || '', from: process.env.NOTIFY_FROM || 'Swarmsite <hello@swarmsite.si>' };
const ipHits = new Map(); // ip → [timestamps]; one worker process per instance, so in-memory is enough per instance
const clientIp = req => String(req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();
function rateLimited(ip) {
  const now = Date.now(), hits = (ipHits.get(ip) || []).filter(t => now - t < 3600e3); ipHits.set(ip, hits);
  if (ipHits.size > 5000) for (const [k, v] of ipHits) if (!v.length || now - v[v.length - 1] > 3600e3) ipHits.delete(k);
  if (hits.length >= RATE.perIpPerHour) return true; hits.push(now); return false;
}
// ---- accounts: a preview belongs to whoever started it. Off until the deployment says so (REQUIRE_LOGIN=1), so the public
// form keeps working exactly as before while the web side is being set up; a signed-in visitor's jobs are theirs either way.
const AUTH = { require: process.env.REQUIRE_LOGIN === '1', free: Math.max(0, Number(process.env.FREE_PREVIEWS_PER_USER || 3)) };
const userOf = makeUserOf(sb);
const usedBy = async userId => { const { count } = await sb.from('jobs').select('id', { count: 'exact', head: true }).eq('user_id', userId).neq('status', 'failed'); return count || 0; };
app.get('/config', (_, res) => res.json({ auth: { require: AUTH.require, free: AUTH.free }, templates: TEMPLATES }));
app.get('/me', async (req, res) => { const user = await userOf(req); if (!user) return res.status(401).json({ error: 'sign in' }); res.json({ id: user.id, email: user.email, previews: allowance({ used: await usedBy(user.id), free: AUTH.free }) }); });
app.get('/me/jobs', async (req, res) => {
  const user = await userOf(req); if (!user) return res.status(401).json({ error: 'sign in' });
  const { data, error } = await sb.from('jobs').select('id,url,status,step,created_at,result').eq('user_id', user.id).order('created_at', { ascending: false }).limit(60);
  if (error) return res.status(500).json({ error: 'could not list' });
  res.json((data || []).map(mine));
});
// A preview started before signing in becomes the visitor's own: its id is unguessable, and a job that already has an owner is never moved.
app.post('/jobs/:id/claim', async (req, res) => {
  if (!/^[0-9a-f-]{36}$/.test(req.params.id)) return res.status(400).end();
  const user = await userOf(req); if (!user) return res.status(401).json({ error: 'sign in' });
  const { data, error } = await sb.from('jobs').update({ user_id: user.id, email: user.email }).eq('id', req.params.id).is('user_id', null).select('id');
  if (error) return res.status(500).json({ error: 'could not claim' });
  res.json({ claimed: (data || []).length === 1 });
});
const canonicalUrl = url => { try { const u = new URL(url); u.hash = ''; u.hostname = u.hostname.toLowerCase().replace(/^www\./, ''); u.pathname = u.pathname.replace(/\/+$/, '') || '/'; return u.origin.replace(/^https?:\/\/www\./, m => m) + u.pathname + u.search; } catch { return url; } };
app.post('/jobs', async (req, res) => {
  let url = String(req.body?.url || '').trim(); if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
  try { new URL(url); } catch { return res.status(400).json({ error: 'bad url' }); }
  if (/localhost|127\.|10\.|192\.168\.|\.internal/i.test(url)) return res.status(400).json({ error: 'not allowed' });
  const user = await userOf(req);
  // the template path: three previews before sign-up and payment (owner, 2026-11-12); only its download needs an account
  // options.mode is the brief's SEO choice (seo-safe | free); which engine builds the page is options.engine
  const mode = req.body?.options?.engine === 'templates' ? 'templates' : '';
  if (mode && !TEMPLATES) return res.status(400).json({ error: 'templates mode is off' });
  if (!mode && AUTH.require && !user) return res.status(401).json({ error: 'Sign in to start a preview.', login: true });
  if (!mode && user) { const a = allowance({ used: await usedBy(user.id), free: AUTH.free }); if (AUTH.require && !a.allowed) return res.status(402).json({ error: `Your ${a.free} free preview${a.free === 1 ? ' is' : 's are'} used.`, previews: a }); }
  const ip = clientIp(req);
  if (!user && rateLimited(ip)) return res.status(429).json({ error: 'You have started several previews recently. Please wait an hour before starting another.' });
  // the same site already queued or running → hand back that job instead of paying twice
  const key = canonicalUrl(url);
  const { data: live } = await sb.from('jobs').select('id,url,status,created_at,options').in('status', ['queued', 'running']).order('created_at', { ascending: false }).limit(200);
  const same = (live || []).find(j => canonicalUrl(j.url) === key && (j.options?.engine === 'templates' ? 'templates' : '') === mode);
  if (same) return res.json({ id: same.id, reused: true });
  if ((live || []).length >= RATE.maxQueue) return res.status(503).json({ error: `The studio is full right now (${live.length} sites in the queue). Please try again in a few minutes.` });
  const since = new Date(Date.now() - 86400e3).toISOString();
  const { count } = await sb.from('jobs').select('id', { count: 'exact', head: true }).gte('created_at', since);
  if ((count || 0) >= RATE.perDay) return res.status(503).json({ error: 'Today\'s preview budget is used up. Please come back tomorrow.' });
  const options = { ...(req.body?.options || {}) }; const email = String(options.notify_email || '').trim().toLowerCase(); if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return res.status(400).json({ error: 'bad email' }); if (email) options.notify_email = email; else delete options.notify_email;
  if (mode) options.engine = mode; else delete options.engine;
  const { data, error } = await sb.from('jobs').insert({ url, options, steps: (mode ? STEPS_T : STEPS).map(([id, label]) => ({ id, label, status: 'pending' })), ...(user ? { user_id: user.id, email: user.email } : {}) }).select('id').single();
  if (error) return res.status(500).json({ error: error.message });
  res.json({ id: data.id });
});
app.get('/jobs', async (req, res) => { const st = req.query.status || 'running'; const { data } = await sb.from('jobs').select('id,url,status,step,created_at').eq('status', st).order('created_at', { ascending: false }).limit(20); res.json(data || []); });
app.get('/jobs/:id', async (req, res) => {
  const { data, error } = await sb.from('jobs').select('id,url,status,step,steps,result,error,created_at,options').eq('id', req.params.id).single();
  if (error) return res.status(404).json({ error: 'not found' });
  if (data.status === 'queued') {
    const { count } = await sb.from('jobs').select('id', { count: 'exact', head: true }).eq('status', 'queued').lt('created_at', data.created_at);
    const { count: running } = await sb.from('jobs').select('id', { count: 'exact', head: true }).eq('status', 'running').gt('lease_until', new Date().toISOString());
    // capacity = the slots we can see working right now (every replica's live leases), never less than this worker's own slots
    const capacity = Math.max(running || 0, WORKER_CONCURRENCY), ahead = (count || 0) + (running || 0);
    data.queue = { ahead, capacity, eta_min: Math.max(1, Math.ceil((ahead + 1) / capacity) * JOB_MINUTES) };
  }
  data.notify = { available: !!NOTIFY.key, email: data.options?.notify_email ? true : false }; delete data.options;
  res.json(data);
});
// "Email me the link": a person in a long queue should not have to keep the tab open.
app.post('/jobs/:id/notify', async (req, res) => {
  if (!/^[0-9a-f-]{36}$/.test(req.params.id)) return res.status(400).end();
  const email = String(req.body?.email || '').trim().toLowerCase(); if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return res.status(400).json({ error: 'bad email' });
  const { data, error } = await sb.from('jobs').select('id,status,options').eq('id', req.params.id).maybeSingle();
  if (error || !data) return res.status(404).json({ error: 'not found' });
  if (!['queued', 'running'].includes(data.status)) return res.status(409).json({ error: 'already finished' });
  const { error: e2 } = await sb.from('jobs').update({ options: { ...(data.options || {}), notify_email: email } }).eq('id', data.id);
  if (e2) return res.status(500).json({ error: e2.message });
  res.json({ ok: true, available: !!NOTIFY.key });
});
async function notifyDone(job, previewUrl) {
  const email = job.options?.notify_email; if (!email || !NOTIFY.key) return;
  const appUrl = `${process.env.PUBLIC_APP || 'https://swarmsite.si'}/app?url=${encodeURIComponent(String(job.url).replace(/^https?:\/\//, ''))}&job=${job.id}`;
  const host = (() => { try { return new URL(job.url).hostname.replace(/^www\./, ''); } catch { return job.url; } })();
  const html = `<p>Your redesigned landing page for <b>${host}</b> is ready.</p><p><a href="${appUrl}">Open your preview</a></p><p style="color:#777;font-size:13px">Your current website stays unchanged. The preview is private to this link.</p>`;
  const r = await fetch('https://api.resend.com/emails', { method: 'POST', headers: { authorization: 'Bearer ' + NOTIFY.key, 'content-type': 'application/json' }, body: JSON.stringify({ from: NOTIFY.from, to: [email], subject: `Your Swarmsite preview for ${host} is ready`, html }) });
  if (!r.ok) throw new Error('resend ' + r.status + ' ' + (await r.text()).slice(0, 200));
}
// Preview page: Supabase public storage serves HTML as text/plain (XSS guard), so we proxy it with the right type.
const SELF = process.env.PUBLIC_API || (process.env.RAILWAY_PUBLIC_DOMAIN ? 'https://' + process.env.RAILWAY_PUBLIC_DOMAIN : 'http://localhost:' + (process.env.PORT || 8080));
async function activePreview(id) {
  const { data, error } = await sb.from('jobs').select('status,result').eq('id', id).single();
  if (error || !data) throw new Error('preview metadata unavailable');
  if (data.status === 'failed') return {failed:true, version:'', blueprints:[], artifactsAvailable:false};
  if (data.status !== 'done') return null;
  const result = data.result || {}, v = result.previewVersion;
  if (v != null && (typeof v !== 'string' || !/^[0-9a-f]{32}$/.test(v) || !Array.isArray(result.blueprints))) throw new Error('invalid preview metadata');
  return {version:v || '', blueprints:result.blueprints, artifactsAvailable:result.artifactsAvailable};
}
app.get('/jobs/:id/art/:name', async (req, res) => {
  if (!/^[0-9a-f-]{36}$/.test(req.params.id) || !ARTS.includes(req.params.name)) return res.status(400).end();
  const requested = req.query.v == null ? '' : String(req.query.v); if (req.query.v != null && !/^[0-9a-f]{32}$/.test(requested)) return res.status(400).end();
  let active; try { active = await activePreview(req.params.id); } catch { return res.status(503).send('preview metadata unavailable'); }
  if (!active || (requested && requested !== active.version)) return res.status(404).send('preview not found');
  const version = active.version; const prefix = version ? `${req.params.id}/v-${version}` : req.params.id;
  const { data, error } = await sb.storage.from(BUCKET).download(`${prefix}/art/${req.params.name}`); if (error || !data) return res.status(404).send('no artefact');
  res.set({ 'content-type': req.params.name.endsWith('.html') ? 'text/plain; charset=utf-8' : 'application/json; charset=utf-8', 'access-control-allow-origin': '*', 'cache-control': 'no-store', 'x-robots-tag': 'noindex' }); res.send(Buffer.from(await data.arrayBuffer()));
});
app.get('/p/:id/draft', async (req, res) => {
  if (!/^[0-9a-f-]{36}$/.test(req.params.id)) return res.status(400).end();
  const { data: row, error } = await sb.from('jobs').select('status,result').eq('id', req.params.id).maybeSingle();
  if (error) return res.status(503).send('preview metadata unavailable');
  if (!row || !row.result?.draft) return res.status(404).send('no draft yet');
  if (row.status === 'done') return res.redirect(302, `/p/${req.params.id}`);
  if (row.status !== 'running') return res.status(404).send('no draft');
  const { data, error: e2 } = await sb.storage.from(BUCKET).download(`${req.params.id}/draft/index.html`);
  if (e2 || !data) return res.status(404).send('no draft');
  res.set({ 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-frame-options': 'ALLOWALL', 'x-robots-tag': 'noindex' });
  res.send(Buffer.from(await data.arrayBuffer()));
});
app.get('/p/:id', async (req, res) => {
  if (!/^[0-9a-f-]{36}$/.test(req.params.id)) return res.status(400).end();
  const bp = req.query.bp == null ? '' : String(req.query.bp); if (bp && !/^[a-z0-9-]{2,24}$/.test(bp)) return res.status(400).end();
  const requested = req.query.v == null ? '' : String(req.query.v); if (req.query.v != null && !/^[0-9a-f]{32}$/.test(requested)) return res.status(400).end();
  let active; try { active = await activePreview(req.params.id); } catch { return res.status(503).send('preview metadata unavailable'); }
  if (!active || (requested && requested !== active.version)) return res.status(404).send('preview not found');
  const version = active.version; const prefix = version ? `${req.params.id}/v-${version}` : req.params.id;
  if (active.failed) return res.status(404).send('preview not found');
  if (bp && Array.isArray(active.blueprints) && !active.blueprints.includes(bp)) return res.status(404).send('preview not found');
  const studioTag = req.query.s == null ? '' : String(req.query.s); if (req.query.s != null && !/^[a-z]$/.test(studioTag)) return res.status(400).end();
  const file = studioTag ? `studio-${studioTag}.html` : bp && !(version && bp === active.blueprints[0]) ? 'bp-' + bp + '.html' : 'index.html';
  const { data, error } = await sb.storage.from(BUCKET).download(`${prefix}/${file}`);
  if (error || !data) return res.status(404).send('preview not found');
  // These are temporary design previews, not the customer's published site.
  // Keep noindex at the HTTP layer so downloaded HTML remains publishable.
  res.set({ 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-frame-options': 'ALLOWALL', 'x-robots-tag': 'noindex' });
  res.send(Buffer.from(await data.arrayBuffer()));
});
// ---- the template path: a variant's preview page (open: no account), and its package (account + the payment hook) ----
app.get('/t/:id/:slug', async (req, res) => {
  if (!/^[0-9a-f-]{36}$/.test(req.params.id)) return res.status(400).end();
  const { data: row, error } = await sb.from('jobs').select('status,result').eq('id', req.params.id).maybeSingle();
  if (error) return res.status(503).send('preview metadata unavailable');
  if (!previewable(row, req.params.slug)) return res.status(404).send('preview not found');
  const { data, error: e2 } = await sb.storage.from(BUCKET).download(`${req.params.id}/t/${req.params.slug}.html`);
  if (e2 || !data) return res.status(404).send('preview not found');
  res.set({ 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-frame-options': 'ALLOWALL', 'x-robots-tag': 'noindex' });
  res.send(Buffer.from(await data.arrayBuffer()));
});
app.get('/t/:id/:slug/package', async (req, res) => {
  if (!/^[0-9a-f-]{36}$/.test(req.params.id)) return res.status(400).end();
  const user = await userOf(req);
  const { data: row, error } = await sb.from('jobs').select('id,url,status,result,user_id').eq('id', req.params.id).maybeSingle();
  if (error) return res.status(503).json({ error: 'unavailable' });
  if (!row || !previewable(row, req.params.slug)) return res.status(404).json({ error: 'not found' });
  const gate = mayDownload({ user, job: row, slug: req.params.slug, env: process.env });
  if (gate.status !== 200) return res.status(gate.status).json(gate.body);
  if (!row.user_id) await sb.from('jobs').update({ user_id: user.id, email: user.email }).eq('id', row.id).is('user_id', null);   // a downloaded page belongs to whoever downloaded it first
  const { data, error: e2 } = await sb.storage.from(PACKAGE_BUCKET).download(`${row.id}/${req.params.slug}.zip`);
  if (e2 || !data) return res.status(404).json({ error: 'package not found' });
  const host = (() => { try { return new URL(row.url).hostname.replace(/^www\./, '').replace(/[^a-z0-9.-]/gi, ''); } catch { return 'site'; } })();
  res.set({ 'content-type': 'application/zip', 'content-disposition': `attachment; filename="${host}-${req.params.slug}.zip"`, 'cache-control': 'no-store' });
  res.send(Buffer.from(await data.arrayBuffer()));
});
app.listen(process.env.PORT || 8080, () => console.log('api on', process.env.PORT || 8080));

// ---------- worker ----------
const JOB_CTX = new AsyncLocalStorage(); // the job a child process belongs to, per async chain: several jobs run at once in one worker
let CURRENT_JOB_DIR = ''; // fallback for code paths outside a job context (tests slice process_ without the loop)
const WORKER_CONCURRENCY = Math.max(1, Number(process.env.WORKER_CONCURRENCY || 2));
const run = (cmd, args, opts = {}) => new Promise((resolve, reject) => {
  const p = spawn(cmd, args, { cwd: ROOT, env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1', ...((JOB_CTX.getStore()?._dir || CURRENT_JOB_DIR) ? { SWARM_JOB_DIR: JOB_CTX.getStore()?._dir || CURRENT_JOB_DIR } : {}) }, ...opts }); let out = '', err = '';
  let buf = ''; p.stdout.on('data', d => { out += d; if (opts.onLine) { buf += d; const lines = buf.split('\n'); buf = lines.pop(); lines.forEach(l => { try { opts.onLine(l); } catch {} }); } }); p.stderr.on('data', d => err += d);
  const t = setTimeout(() => { p.kill('SIGKILL'); reject(new Error(cmd + ' timeout')); }, opts.timeoutMs || 300000);
  p.on('close', c => { clearTimeout(t); c === 0 ? resolve(out) : reject(new Error(`${cmd} ${args[0]} exit ${c}: ${err.slice(-800)}`)); });
});
const slugOf = url => url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
async function updateRunning(job, patch) {
  // A job may have been failed by a different worker during a deployment.
  // Never let a late update bring a terminal job back to life or overwrite it.
  let query = sb.from('jobs').update(patch).eq('id', job.id).eq('status', 'running');
  if (job._leaseOwner) query = query.eq('lease_owner', job._leaseOwner);
  const { data, error } = await query.select('id').maybeSingle();
  if (error) {
    const failure = new Error('job update failed: ' + (error.message || 'database error'));
    // These PostgreSQL errors explicitly reject/abort the transaction. A
    // network failure has an unknown outcome and must not be retried here.
    failure.retryableTransaction = ['40001', '40P01', '55P03', '57014', '53300', '57P03'].includes(String(error.code || '').toUpperCase());
    throw failure;
  }
  if (!data) throw new Error('job is no longer running');
}
async function updateWithRetry(job, patch) {
  // Retry only transactions explicitly rejected by PostgreSQL. The same
  // immutable patch is sent again; unknown network outcomes fail closed.
  for (let attempt = 0; ; attempt++) {
    try { await updateRunning(job, patch); return; }
    catch (error) {
      if (!error.retryableTransaction || attempt >= 2) throw error;
      await new Promise(resolve => setTimeout(resolve, 100 * (attempt + 1)));
    }
  }
}
async function setStep(job, id, status, note) {
  const steps = job.steps.map(s => s.id === id ? { ...s, status, at: new Date().toISOString(), note } : s); job.steps = steps;
  await updateWithRetry(job, { step: id, steps });
}
async function upload(local, remote, type) {
  const buf = fs.readFileSync(local); const { error } = await sb.storage.from(BUCKET).upload(remote, buf, { contentType: type, upsert: true }); if (error) throw error;
  return sb.storage.from(BUCKET).getPublicUrl(remote).data.publicUrl;
}

// ---- real events: what each step actually found / decided, with page rects where there are any ----
const J = f => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return null; } };
function emit(job, evs) {
  if (!evs.length) return Promise.resolve();
  // stdout event callbacks can arrive while earlier database writes are
  // pending. Queue them in order and retain errors for the caller to await.
  const next = (job._eventChain || Promise.resolve()).then(async () => {
    job._result = job._result || {};
    const events = (job._result.events || []).concat(evs.map(e => ({ ...e, at: Date.now() })));
    const excess = Math.max(0, events.length - 400);
    job._result.eventsOffset = Number(job._result.eventsOffset || 0) + excess;
    job._result.events = events.slice(excess);
    await updateWithRetry(job, { result: job._result });
  });
  job._eventChain = next;
  next.catch(() => {}); // onLine callbacks are not awaited by the child process.
  return next;
}
async function drainEvents(job) { if (job._eventChain) await job._eventChain; }
// Progressive delivery: the best page after each review round goes out as a draft the person can already
// look at while later rounds refine it. The draft lives outside the versioned preview tree and is only
// served while the job is still running; the finished, verified page replaces it.
async function publishDraft(job, draft) {
  if (!draft || !draft.path || !fs.existsSync(draft.path)) return;
  const next = (job._eventChain || Promise.resolve()).then(async () => {
    await upload(draft.path, `${job.id}/draft/index.html`, 'text/html');
    job._result = job._result || {};
    job._result.draft = { url: `${SELF}/p/${job.id}/draft?r=${Number(draft.round) || 0}`, round: Number(draft.round) || 0, score: Number(draft.score) || 0, at: Date.now() };
    await updateWithRetry(job, { result: job._result });
  });
  job._eventChain = next; next.catch(e => console.warn('draft', job.id, e.message)); return next;
}
function eventsCapture(dir) {
  const g = J(path.join(dir, 'geometry.json')) || {}; const inv = J(path.join(dir, 'inventory.json')) || {}; const as = J(path.join(dir, 'assets.json')) || {}; const ev = [];
  if (g.logo) ev.push({ role: 'Type', text: 'logo found', rect: g.logo });
  if (g.h1) ev.push({ role: 'Audit', text: `h1 · ${g.h1.px}px · "${g.h1.text.slice(0, 40)}"`, rect: g.h1.rect }); else ev.push({ role: 'Audit', text: 'no h1 on the page' });
  if (g.nav) ev.push({ role: 'Audit', text: `nav: ${g.nav.links} links`, rect: g.nav.rect });
  (g.images || []).slice(0, 8).forEach((im, i) => ev.push({ role: 'Photos', text: `photo ${i + 1} · ${im.w}×${im.h}${im.w >= 1200 ? ' · hero-grade' : ''}`, rect: im.rect }));
  (g.ctas || []).slice(0, 4).forEach(c => ev.push({ role: 'Copy', text: `cta: "${c.text.slice(0, 28)}"`, rect: c.rect }));
  (g.headings || []).slice(0, 6).forEach(h => ev.push({ role: 'Copy', text: `heading: "${h.text.slice(0, 36)}"`, rect: h.rect }));
  const cc = inv.colors; const cols = (Array.isArray(cc) ? cc : [...(cc?.bg || []), ...(cc?.buttons || [])]).slice(0, 3).map(c => typeof c === 'string' ? c : c.c).filter(Boolean); if (cols.length) ev.push({ role: 'Concept', text: `colours: ${cols.join(' ')}` });
  const fonts = (inv.typography?.families || inv.typography?.fonts || []).slice(0, 2).map(f => typeof f === 'string' ? f : f.family || f.name).filter(Boolean); if (fonts.length) ev.push({ role: 'Type', text: `fonts: ${fonts.join(', ')}` });
  ev.push({ role: 'Audit', text: `${inv.copy?.totalWords || '?'} words · ${(inv.sections || []).length} sections · ${Math.round((g.pageHeight || 0) / 900)} screens` });
  return ev;
}
function eventsDiagnose(dir) { const a = J(path.join(dir, 'audit.json')) || {}; const g = J(path.join(dir, 'geometry.json')) || {}; const ev = [];
  if (a.designScore != null) ev.push({ role: 'Audit', text: `design score ${a.designScore}/100` });
  (a.findings || []).slice(0, 8).forEach(f => ev.push({ role: f.severity === 'high' ? 'QA' : 'Audit', text: f.message.slice(0, 70), rect: /nav/.test(f.code) ? g.nav?.rect : /h1|headline/.test(f.code) ? g.h1?.rect : undefined }));
  const keep = Array.isArray(a.keep) ? a.keep : Object.entries(a.keep || {}).filter(([k, v]) => v && (Array.isArray(v) ? v.length : true) && k !== 'nav').map(([k, v]) => k === 'logo' ? 'their logo' : Array.isArray(v) ? `${k}: ${v[0]}` : typeof v === 'string' ? v : k); keep.slice(0, 3).forEach(k => ev.push({ role: 'Concept', text: `keep: ${String(k).slice(0, 50)}` }));
  return ev; }
function eventsDirect(dir) { const d = J(path.join(dir, 'direction.json')) || {}; const g = J(path.join(dir, 'geometry.json')) || {}; const ev = [];
  ev.push({ role: 'Concept', text: `concept ${d.concept} · ${d.kind} · ${d.voice}` }); if (d.blueprint) ev.push({ role: 'Concept', text: `blueprint: ${d.blueprint} · ${d.change || ''}` });
  if (d.brand) ev.push({ role: 'Type', text: `${d.brand.keep_font ? 'keeping' : 'replacing'} their font${d.brand.font_hint ? ' → ' + d.brand.font_hint : ''}` });
  if (d.hero) { ev.push({ role: 'Copy', text: `h1: "${String(d.hero.h1 || '').replace(/<[^>]+>/g, '')}"`, rect: g.h1?.rect }); if (d.hero.fact) ev.push({ role: 'Copy', text: `the fact: ${d.hero.fact}` }); if (d.hero.cta) ev.push({ role: 'Copy', text: `one action: ${d.hero.cta}` }); }
  (d.beats || []).forEach((b, i) => ev.push({ role: 'Concept', text: `beat ${i + 1}: ${b.type}${b.h2 ? ' — ' + b.h2.slice(0, 40) : ''}`, rect: g.sections?.[i + 1]?.rect }));
  (d.audit_notes || []).slice(0, 2).forEach(n => ev.push({ role: 'QA', text: `owner to confirm: ${String(n).slice(0, 60)}` }));
  return ev; }
function eventsRender(dir) { const html = (() => { try { return fs.readFileSync(path.join(dir, 'index.html'), 'utf8'); } catch { return ''; } })(); const moves = [...new Set([...html.matchAll(/data-move="([a-z][a-z0-9-]{1,40})"/g)].map(m => m[1]))]; // real move names on elements, not the placeholder inside the inlined script's own documentation
  // every line is read off the page that was built: nothing here is a fixed sentence
  const face = (html.match(/--display:'([^']{1,60})'/) || [])[1]; const heroSize = (html.match(/--hero-size:(clamp\([^)]{1,60}\))/) || [])[1];
  const sections = (html.match(/<section[\s>]/g) || []).length; const pictures = (html.match(/<img /g) || []).length; const smooth = /<script src="[^"]*lenis[^"]*"/i.test(html);
  const ev = [];
  if (moves.length) ev.push({ role: 'Motion', text: `moves: ${moves.slice(0, 5).join(', ')}` });
  if (face) ev.push({ role: 'Type', text: `display face ${face}${heroSize ? ' · h1 ' + heroSize : ''}`.slice(0, 120) });
  ev.push({ role: 'Photos', text: `${pictures} ${pictures === 1 ? 'picture' : 'pictures'} placed` });
  if (sections) ev.push({ role: 'Render', text: `${sections} sections built` });
  ev.push({ role: 'Render', text: `page ${Math.round(html.length / 1024)} KB${smooth ? ' · smooth scroll on' : ''}` });
  return ev; }
function eventsQA(qa) { return String(qa || '').split('\n').filter(Boolean).slice(0, 8).map(l => ({ role: 'QA', text: l.replace(/^\[(high|med|low)\]\s*/, '').slice(0, 70) })); }

const ARTS = ['brief.json', 'critic.json', 'contract.json', 'scores.json', 'fingerprint.json', 'composition.json', 'layout.json', 'coverage.json', 'factsheet.json', 'swarm.json', 'inventory.json', 'assets.json', 'images.json', 'geometry.json', 'audit.json', 'direction.json', 'mobile.json', 'findings.json', 'index.html'];
async function uploadArtefacts(job, dir, diagnostics = false) { let uploaded = true; for (const f of ARTS) { const fp = path.join(dir, f); if (fs.existsSync(fp)) { try { await upload(fp, `${job.id}/${!diagnostics && job._previewVersion ? `v-${job._previewVersion}/` : ''}art/${f}`, f.endsWith('.html') ? 'text/html' : 'application/json'); } catch (e) { uploaded = false; console.warn('art', f, e.message); } } } return uploaded; }
const BP = { software: ['butter', 'cerebrium', 'deepbook'], place: ['tengile', 'white-desert', 'belgrade-arbor', 'units'], service: ['lpas', 'aino', 'atelier'], product: ['crav', 'halfdays'] };
async function checkpointCrawl(job, dir) {
  await drainEvents(job);
  const old = job._result?.crawlCheckpoint;
  const checkpoint = await saveCrawlCheckpoint(sb.storage.from('crawl-checkpoints'), job.id, dir);
  job._result = { ...(job._result || {}), crawlCheckpoint: checkpoint };
  await updateWithRetry(job, { result: job._result });
  if (old?.key && old.key !== checkpoint.key) {
    const { error } = await sb.storage.from('crawl-checkpoints').remove([old.key]);
    if (error) console.warn('old checkpoint cleanup', job.id, error.message);
  }
}
async function runClaimed(job) {
  job._leaseOwner = WORKER_ID;
  const heartbeat = setInterval(async () => {
    try { await updateRunning(job, { lease_until: new Date(Date.now() + 120000).toISOString() }); }
    catch (e) { console.warn('lease heartbeat', job.id, e.message); }
  }, 30000);
  try { await process_(job); console.log('done', job.id); }
  catch (e) {
    // No in-flight progress write may arrive after the terminal update.
    try { await drainEvents(job); } catch {}
    const message = String(e?.message || 'Unknown error');
    // Anthropic includes a Python traceback and request details in this
    // confirmed billing error. Keep an actionable owner diagnostic while
    // returning a simple, non-sensitive message to the customer.
    const noAnthropicCredit = /your credit balance is too low to access the anthropic api/i.test(message);
    const overBudget = /job budget:/i.test(message);
    const retries = Number(job.retry_count || 0);
    // retry only what is ours to retry: the model provider or storage hiccuping — never the customer's site timing out or refusing us
    const ours = /anthropic|overloaded|rate.limit|HTTP (429|5\d\d)|status(?: code)?:? ?5\d\d|internal server error|econnreset|econnrefused|fetch failed|supabase|storage/i.test(message);
    const theirs = /capture\.mjs|source page|blocked\.json|bot check|node timeout/i.test(message);
    const retryable = !noAnthropicCredit && !overBudget && ours && !theirs;
    if (retryable && retries < 3) {
      job._result = job._result || {};
      const events=(job._result.events || []).concat([{role:'Reader', text:'Temporary error; resuming from the saved checkpoint', at:Date.now()}]);
      const excess=Math.max(0,events.length-400);job._result.eventsOffset=Number(job._result.eventsOffset || 0)+excess;job._result.events=events.slice(excess);
      try {
        await updateWithRetry(job, {status:'queued', lease_owner:null, lease_until:null, retry_count:retries+1,
          retry_after:new Date(Date.now()+Math.min(60000,5000*2**retries)).toISOString(), result:job._result, error:null});
        job._requeued = true; console.warn('retrying job', job.id, retries+1); return;
      } catch (retryError) { console.warn('retry scheduling failed', job.id, retryError.message); }
    }
    const publicError = noAnthropicCredit ? 'The AI service is temporarily unavailable. Please try again later.' : overBudget ? 'This site needed more work than one preview allows. We stopped to keep it fair; try a smaller page or contact us.' : message.slice(0, 2000);
    console.error('failed', job.id, noAnthropicCredit ? 'Anthropic API credit balance is too low; check provider billing.' : message);
    let markedFailed = false;
    try { await updateWithRetry(job, { status: 'failed', error: publicError }); markedFailed = true; job._terminalPersisted = true; }
    catch (updateError) { console.error('failed status update', job.id, updateError.message); }
    // If another actor already finalized this job, do not overwrite its
    // artifacts with files from this stale attempt.
    try { if (markedFailed && job._dir) job._artifactsUploaded = await uploadArtefacts(job, job._dir, true); } catch {}
  } finally {
    clearInterval(heartbeat);
    // Uploading artifacts is not enough: keep the local files until a terminal
    // status has also been confirmed by the database.
    if (job._jobRoot && (job._requeued || job._artifactsUploaded && job._terminalPersisted)) {
      try { fs.rmSync(job._jobRoot, { recursive: true, force: true }); }
      catch (e) { console.warn('job cleanup', job.id, e.message); }
    }
  }
}
async function process_(job) {
  if (job.options?.engine === 'templates') return processTemplates(job);
  const slug = slugOf(job.url);
  fs.mkdirSync(OUT, { recursive: true });
  const jobRoot = fs.mkdtempSync(path.join(OUT, `job-${job.id}-`));
  job._jobRoot = jobRoot;
  const dir = path.join(jobRoot, slug);
  job._dir = dir; CURRENT_JOB_DIR = dir;
  job._result = { ...(job.result || {}) };
  let restored = false;
  if (job._result.crawlCheckpoint) {
    await restoreCrawlCheckpoint(sb.storage.from('crawl-checkpoints'), job.id, job._result.crawlCheckpoint, dir);
    restored = true;
  }
  const t0 = Date.now(); const timed = async (id, fn) => { await setStep(job, id, 'running'); const s = Date.now(); const r = await fn(); await setStep(job, id, 'done', `${Math.round((Date.now() - s) / 1000)}s`); return r; };
  await timed('capture', async () => {
    try { if (!restored) await run('node', ['lib/pipeline/capture.mjs', job.url, '--out', jobRoot, '--chrome', process.env.CHROME_PATH || ''].filter(Boolean), { timeoutMs: 420000, onLine: line => {
      let item; try { item = JSON.parse(line); } catch { return; }
      if (item.event) emit(job, [item.event]);
      if (item.captureReady) {
        const next = (job._eventChain || Promise.resolve()).then(async () => {
          job._result = job._result || {};
          job._result.beforeUrl = await upload(path.join(dir, 'before-hero.jpg'), `${job.id}/before.jpg`, 'image/jpeg');
          if (fs.existsSync(path.join(dir, 'before-full.jpg'))) job._result.beforeFullUrl = await upload(path.join(dir, 'before-full.jpg'), `${job.id}/before-full.jpg`, 'image/jpeg');
          job._result.pageHeight = Math.min(7000, J(path.join(dir, 'geometry.json'))?.pageHeight || 900);
          await updateWithRetry(job, { result: job._result });
        });
        job._eventChain = next; next.catch(() => {});
      }
    } }); await drainEvents(job); }
    catch (e) { const bp = path.join(dir, 'blocked.json'); if (fs.existsSync(bp)) throw new Error(JSON.parse(fs.readFileSync(bp, 'utf8')).reason + ' Try the www/non-www address, or a page that is not behind the check.'); throw e; }
    if (fs.existsSync(path.join(dir, 'before-hero.jpg'))) { const beforeUrl = await upload(path.join(dir, 'before-hero.jpg'), `${job.id}/before.jpg`, 'image/jpeg'); job._result = { ...(job._result || {}), beforeUrl }; if (fs.existsSync(path.join(dir, 'before-full.jpg'))) { job._result.beforeFullUrl = await upload(path.join(dir, 'before-full.jpg'), `${job.id}/before-full.jpg`, 'image/jpeg'); const g = J(path.join(dir, 'geometry.json')); job._result.pageHeight = Math.min(7000, g?.pageHeight || 900); } await updateWithRetry(job, { result: job._result }); }
    if (restored) {
      // Older checkpoints may contain sampled subpages. The active product
      // scope is the submitted landing page, so do not feed those pages or
      // their visuals into the business interpretation.
      const invPath = path.join(dir, 'inventory.json'); const inv = J(invPath);
      if (!inv) throw new Error('Saved landing capture is missing');
      if (inv.sourceCoverage?.scope !== 'landing_page_only') {
        inv.sourcePages = []; const coverage = inv.sourceCoverage || {};
        for (const route of coverage.routes || []) { route.status = 'not_scanned'; route.reason = 'Only the submitted landing page is analyzed'; }
        coverage.scope = 'landing_page_only'; coverage.routeLimit = 0;
        coverage.sitemapQueue = [];
        coverage.contentTruncated = !!inv.copy?.textTruncated || (coverage.sections || []).some(s => s.textTruncated || s.faqTruncated || s.panelsTruncated || s.testimonialsTruncated);
        coverage.complete = !coverage.contentTruncated && !coverage.sectionsTruncated;
        inv.sourceCoverage = coverage; fs.writeFileSync(invPath, JSON.stringify(inv));
        const imagesPath = path.join(dir, 'images.json'); const images = J(imagesPath);
        if (Array.isArray(images)) fs.writeFileSync(imagesPath, JSON.stringify(images.filter(image => !image.page && !/^p[0-9]+-/.test(image.id || ''))));
        fs.rmSync(path.join(dir, 'site-analysis.json'), {force:true});
        await checkpointCrawl(job, dir);
      }
      await emit(job, [{ role: 'Reader', text: 'Resuming saved landing analysis' }]);
    } else await checkpointCrawl(job, dir);
    await emit(job, eventsCapture(dir));
  });
  await timed('diagnose', async () => { const out = await run('python3', ['-I', 'lib/audit/diagnose.py', path.join(dir, 'inventory.json')]); fs.writeFileSync(path.join(dir, 'audit.json'), out); }); await emit(job, eventsDiagnose(dir));
  fs.writeFileSync(path.join(dir, 'brief.json'), JSON.stringify({ ...(job.options || {}), url: job.url })); // the url seeds the house's colour pick for unbranded sites
  // Instant first version: their page poured into the house template, no model call. Published as draft round 0 so the
  // person has something to look at within seconds; the director and the swarm replace it. Never fatal.
  try {
    await run('python3', ['lib/direct/quick.py', dir], { timeoutMs: 20000 });
    const quickDir = J(path.join(dir, 'direction.json')) || {};
    const draft = path.join(dir, 'draft.html');
    await run('python3', ['lib/render/render_bp.py', dir, quickDir.blueprint || 'cerebrium', draft], { timeoutMs: 60000 });
    await publishDraft(job, { round: 0, score: 0, path: draft });
    await emit(job, [{ role: 'Render', text: `first version up · ${quickDir.blueprint || 'house'} template · ${(quickDir.beats || []).length} sections` }]);
  } catch (e) { console.warn('quick draft', job.id, e.message); }
  await timed('direct', async () => {
    // batched source analysis is for a multi-page crawl; on the default landing-page scope the Reader already sees every section once
    const invNow = J(path.join(dir, 'inventory.json')) || {}; const multiPage = (invNow.sourcePages || []).length > 0;
    while (multiPage) {
      let output;
      try { output = await run('python3', ['lib/swarm/site_map.py', dir, '3'], { timeoutMs: 240000, onLine: line => { try { const item=JSON.parse(line); if(item.event) emit(job,[item.event]); } catch {} } }); }
      catch (error) { if (fs.existsSync(path.join(dir, 'site-analysis.json'))) await checkpointCrawl(job, dir); throw error; }
      const analysis = output.trim().split('\n').map(line => { try { return JSON.parse(line).analysis; } catch { return null; } }).find(Boolean);
      if (!analysis) throw new Error('Source analysis did not report progress');
      await checkpointCrawl(job, dir);
      if (analysis.completed >= analysis.total) { if (!analysis.complete) await emit(job, [{role:'Reader', text:`Source analysis needs review · ${analysis.missing_pages} pages · ${analysis.missing_sections} sections`}]); break; }
    }
    await run('python3', ['-c', 'import sys; sys.path.insert(0, "lib/swarm"); import agents, json; f = agents.reader(sys.argv[1]); assert f, "reader did not produce a factsheet"; print(json.dumps({"what": f.get("what", ""), "n": len(f.get("facts", []))}))', dir], { timeoutMs: 180000 }).then(async o => { const f = JSON.parse(o.trim().split('\n').pop()); await emit(job, [{ role: 'Reader', text: String(f.what || '').slice(0, 120) }, { role: 'Reader', text: `${f.n} source facts` }]); });
    return run('python3', ['lib/direct/direct.py', dir, process.env.DIRECT_MODEL || 'claude-sonnet-5-5'], { timeoutMs: 240000 }); }); await emit(job, eventsDirect(dir));
  await timed('render', async () => {
    // one renderer: the winner's measured form + signature moves + this client's content (primary blueprint + one alternative)
    let kind = 'service', chosen = ''; try { const dd = JSON.parse(fs.readFileSync(path.join(dir, 'direction.json'), 'utf8')); kind = dd.kind || kind; chosen = dd.blueprint || ''; } catch {}
    const have = new Set(fs.readdirSync(path.join(ROOT, 'lib/blueprints')).filter(f => f.endsWith('.bp.json')).map(f => f.replace('.bp.json', '')));
    const picks = [...new Set([chosen, ...(BP[kind] || BP.service)])].filter(b => have.has(b)).slice(0, 2);
    job._bps = [];
    for (const bp of picks) { try { await run('python3', ['lib/render/render_bp.py', dir, bp, path.join(dir, `bp-${bp}.html`)], { timeoutMs: 120000 }); job._bps.push(bp); } catch (e) { console.warn('bp', bp, e.message.slice(0, 200)); } }
    // the swarm: Reader → UX → Copy → UI → Visual shape the document, then Critic ↔ owners loop until the score passes
    if (job._bps[0]) { try {
        const out = path.join(dir, `bp-${job._bps[0]}.html`);
        const o = await run('python3', ['lib/swarm/run.py', dir, job._bps[0], '--out', out, '--rounds', process.env.SWARM_ROUNDS || '3', '--target', process.env.SWARM_TARGET || '80', '--alt', job._bps[1] || ''], { timeoutMs: 900000, onLine: async l => { try { const j = JSON.parse(l); if (j.event) await emit(job, [j.event]); if (j.draft) await publishDraft(job, j.draft); } catch {} } });
        const last = o.trim().split('\n').map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
        const done = last.find(j => j.done)?.done; const crit = J(path.join(dir, 'critic.json'));
        if (!done?.best_blueprint || !done?.render_manifest || !job._bps.includes(done.best_blueprint)) throw new Error('selected blueprint identity unavailable');
        job._primary = done.best_blueprint; job._manifest = done.render_manifest; job._reviewedOut = out;
        job._critic = crit ? { score: crit.best ?? crit.score, taste: crit.taste ?? null, contract: crit.contract ?? null, axes: crit.axes ?? null, fixes: (crit.fixes || []).length, verdict: crit.verdict, rounds: done?.rounds } : null;
      } catch (e) { console.warn('swarm', e.message.slice(0, 300)); await emit(job, [{ role: 'QA', text: 'swarm loop failed: ' + e.message.slice(0, 80) }]); throw e; } }
    // the primary blueprint IS the page
    if (!job._primary) throw new Error('no blueprint rendered');
    const originalChoices = job._bps; const reviewed = job._reviewedOut;
    verifySelected({dir, root:ROOT, bp:job._primary, manifest:job._manifest, out:reviewed});
    fs.copyFileSync(reviewed, path.join(dir, 'index.html'));
    const alternate = originalChoices.find(bp => bp !== job._primary);
    if (alternate) { try { job._alternative = await prepareAlternative({dir, root:ROOT, primary:job._primary, alternate, manifest:job._manifest, out:reviewed, run}); }
      catch (e) { verifySelected({dir, root:ROOT, bp:job._primary, manifest:job._manifest, out:reviewed}); console.warn('alternative unavailable', e.message); } }
    job._bps = [job._primary, ...(job._alternative ? [job._alternative.bp] : [])];
  }); await emit(job, eventsRender(dir)); if (job._bps?.length) await emit(job, job._bps.map(b => ({ role: 'Concept', text: `blueprint variant: ${b}` })));
  let qa = null; await timed('qa', async () => { try { const o = await run('python3', ['lib/qa/check.py', path.join(dir, 'index.html')], { timeoutMs: 240000 }); qa = o.split('\n').filter(l => /QA score|\[(high|med|low)/.test(l)).join('\n'); } catch (e) { qa = 'qa skipped: ' + e.message.slice(0, 200); } }); await emit(job, eventsQA(qa));
  // Snapshot the result only after all previously queued progress is present.
  await drainEvents(job);
  const result = await timed('upload', async () => {
    const published = await publishSelected({dir, root:ROOT, primary:job._primary, alternate:job._alternative, manifest:job._manifest, out:path.join(dir, 'index.html'), jobId:job.id, upload});
    job._bps = published.blueprints; job._previewVersion = published.version; const previewUrl = `${SELF}/p/${job.id}?v=${published.version}`;
    // The studio composes three variants; the first clean one is the page, the others are published beside it (…/p/<id>?s=b).
    const studioLog = (J(path.join(dir, 'swarm.json')) || {}).studio || null; const studioOthers = [];
    if (studioLog?.kept) for (const tag of (Array.isArray(studioLog.others) ? studioLog.others : []).slice(0, 4)) { const f = path.join(dir, 'studio', `page-${tag}.html`);
      if (/^[a-z]$/.test(String(tag)) && fs.existsSync(f)) { try { await upload(f, `${job.id}/v-${published.version}/studio-${tag}.html`, 'text/html'); studioOthers.push(tag); } catch (e) { console.warn('studio variant not uploaded', tag, e.message); } } }
    job._studio = studioLog ? { kept: studioLog.kept || null, why: studioLog.why || null, variants: (studioLog.variants || []).map(v => ({ tag: v.tag, type: v.type, scheme: v.scheme, scenes: v.scenes, clean: !!v.clean })), others: studioOthers.map(tag => ({ tag, url: `${SELF}/p/${job.id}?v=${published.version}&s=${tag}` })) } : null;
    const beforeUrl = fs.existsSync(path.join(dir, 'before-hero.jpg')) ? await upload(path.join(dir, 'before-hero.jpg'), `${job.id}/before.jpg`, 'image/jpeg') : null;
    const direction = JSON.parse(fs.readFileSync(path.join(dir, 'direction.json'), 'utf8'));
    return { ...(job._result || {}), previewUrl, previewVersion:published.version, beforeUrl, qa, budget: J(path.join(dir, 'budget.json')), studio: job._studio || null, seo: (J(path.join(dir, 'contract.json')) || {}).seo || null, coverage: J(path.join(dir, 'coverage.json')), blueprints: job._bps || [], critic: job._critic || null, scores: J(path.join(dir, 'scores.json')), composition: (c => c ? { drawn: !!c.drawn, kept: !!c.kept, concept: c.concept ?? null, face: c.face ?? null, lists: c.lists?.drawn ? (c.lists.forms ?? null) : null, pictures: c.pictures?.drawn ? (c.pictures.forms ?? null) : null, words: c.words?.drawn ? (c.words.forms ?? null) : null, before: c.before ?? null, score: c.score ?? null, taste: c.taste ?? null, why: c.why ?? null } : null)(J(path.join(dir, 'composition.json'))), fingerprint: (f => f ? { hero: f.hero, body: f.body, digest: f.digest } : null)(J(path.join(dir, 'fingerprint.json'))), direction: { kind: direction.kind, concept: direction.concept, voice: direction.voice, brand: direction.brand, beats: direction.beats.map(b => b.type), audit_notes: direction.audit_notes }, seconds: Math.round((Date.now() - t0) / 1000) };
  });
  job._artifactsUploaded = await uploadArtefacts(job, dir);
  result.artifactsAvailable = job._artifactsUploaded; result.artifactsVersion = job._previewVersion;
  await drainEvents(job);
  verifySelected({dir, root:ROOT, bp:job._primary, manifest:job._manifest, out:path.join(dir, 'index.html')});
  if (result.blueprints.length > 1) verifyAlternative({root:ROOT, alternate:job._alternative});
  const checkpoint = result.crawlCheckpoint;
  delete result.crawlCheckpoint;
  await updateWithRetry(job, { status: 'done', step: 'done', result, slug, lease_owner: null, lease_until: null });
  job._terminalPersisted = true;
  try { const { data: fresh } = await sb.from('jobs').select('options').eq('id', job.id).maybeSingle(); job.options = fresh?.options || job.options; await notifyDone(job, result.previewUrl); } catch (e) { console.warn('notify', job.id, e.message); }
  if (job._result?.draft) { const { error } = await sb.storage.from(BUCKET).remove([`${job.id}/draft/index.html`]); if (error) console.warn('draft cleanup', job.id, error.message); }
  if (checkpoint?.key) { const { error } = await sb.storage.from('crawl-checkpoints').remove([checkpoint.key]); if (error) console.warn('checkpoint cleanup', job.id, error.message); }
}
async function loop() {
  const slot = loop.slots = (loop.slots || 0) + 1; // one loop per slot; stagger so they do not hammer the claim RPC together
  await new Promise(r => setTimeout(r, (slot - 1) * 700));
  while (true) {
    try {
      const { data, error } = await sb.rpc('claim_swarmsite_job', { p_worker_id: WORKER_ID, p_lease_seconds: 120 });
      if (error) throw error;
      const claimed = Array.isArray(data) ? data[0] : data;
      if (claimed) { console.log('job', claimed.id, claimed.url, 'slot', slot); await JOB_CTX.run(claimed, () => runClaimed(claimed)); }
      else await new Promise(r => setTimeout(r, 2500));
    } catch (e) { console.error('loop', e.message); await new Promise(r => setTimeout(r, 5000)); }
  }
}
// the template path's job (server/templates.mjs); kept outside the stretch from runClaimed to loop that the worker tests cut out
async function processTemplates(job) {
  const slug = slugOf(job.url);
  fs.mkdirSync(OUT, { recursive: true });
  const jobRoot = fs.mkdtempSync(path.join(OUT, `job-${job.id}-`)); job._jobRoot = jobRoot;
  const dir = path.join(jobRoot, slug); job._dir = dir; CURRENT_JOB_DIR = dir;
  job._result = { ...(job.result || {}) };
  const result = await runTemplateJob({ job, dir, jobRoot, run, upload, self: SELF, chrome: process.env.CHROME_PATH || '',
    uploadPrivate: async (local, key, type) => { const { error } = await sb.storage.from(PACKAGE_BUCKET).upload(key, fs.readFileSync(local), { contentType: type, upsert: true }); if (error) throw error; },
    publicBase: key => sb.storage.from(BUCKET).getPublicUrl(key).data.publicUrl,
    setStep: (id, status, note) => setStep(job, id, status, note),
    emit: evs => emit(job, evs),
    save: async r => { await drainEvents(job); job._result = { ...r, events: job._result?.events || [], eventsOffset: job._result?.eventsOffset || 0 }; await updateWithRetry(job, { result: job._result }); } });
  await drainEvents(job);
  const final = { ...result, events: job._result?.events || [], eventsOffset: job._result?.eventsOffset || 0 };
  job._artifactsUploaded = true;
  await updateWithRetry(job, { status: 'done', step: 'done', result: final, slug, lease_owner: null, lease_until: null });
  job._terminalPersisted = true;
  try { const { data: fresh } = await sb.from('jobs').select('options').eq('id', job.id).maybeSingle(); job.options = fresh?.options || job.options; await notifyDone(job, final.templates?.variants?.[0]?.url || ''); } catch (e) { console.warn('notify', job.id, e.message); }
}
if (process.env.SUPABASE_URL) { for (let i = 0; i < WORKER_CONCURRENCY; i++) loop(); console.log('worker', WORKER_ID, 'slots', WORKER_CONCURRENCY); } else console.warn('no SUPABASE_URL: worker idle');
