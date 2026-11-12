/* publish.mjs — one click puts a chosen design, with the visitor's edits, on <name>.swarmsite.si (BRIEF-engine.md step 10).
   What goes up is the package that was verified, never a fresh render: the edited data is packaged
   (lib/templates/edit.py package: the page, its media and fonts, nothing asked of the network), the package is opened
   offline beside the edited page and compared screen by screen, and only a package that matches is deployed — the
   same zip, file for file. The same verified package becomes the download.

   Vercel: one project for every published site (VERCEL_PROJECT, default "swarmsite-sites"); each publish is a
   production deployment of that site's files, then the alias <name>.swarmsite.si. The token and team are the
   owner's (VERCEL_TOKEN, VERCEL_TEAM_ID), set in Railway; without a token, publishing answers 503 and nothing else
   changes. The wildcard domain *.swarmsite.si must be on that Vercel team.

   Everything is passed in, so it is tested without a bucket, Chrome or Vercel:
     deps: { row, slug, name, user, edits() → the kept patch, readPrivate(key), writePrivate(key, buf, type), publicBase(key), python(args), fetch, env,
             tmp() → dir, save(state), sleep(ms) } */
import fs from 'node:fs'; import path from 'node:path'; import crypto from 'node:crypto';

export const DOMAIN = 'swarmsite.si';
export const RESERVED = new Set(['www', 'app', 'api', 'admin', 'mail', 'smtp', 'imap', 'ftp', 'dashboard', 'login', 'account', 'static', 'cdn', 'assets', 'docs', 'blog',
  'status', 'help', 'support', 'swarmsite', 'preview', 'previews', 'staging', 'dev', 'test', 'start', 'edit', 'billing', 'pay', 'secure', 'auth', 'oauth', 'ns1', 'ns2']);
export function nameProblem(name) {
  const n = String(name || '');
  if (!/^[a-z0-9](?:[a-z0-9-]{1,38}[a-z0-9])$/.test(n) || n.includes('--')) return 'A name is 3 to 40 small letters, digits and single dashes, starting and ending with a letter or digit.';
  if (RESERVED.has(n)) return 'That name is kept for Swarmsite itself.';
  return '';
}
const lastJson = out => String(out || '').trim().split('\n').reverse().map(l => { try { return JSON.parse(l); } catch { return null; } }).find(x => x && typeof x === 'object');
export const editsHash = ops => crypto.createHash('sha256').update(JSON.stringify(ops || [])).digest('hex').slice(0, 16);

// the verified package of the edited page: built, compared offline with the edited page, kept in the private bucket
export async function verifiedPackage(deps, ops) {
  const { row, slug } = deps; const s = row.result?.templates?.store || {}; const key = s.variants?.[slug] || s.data;
  const data = key && await deps.readPrivate(key); if (!data) return { ok: false, why: ['this job keeps no data'] };
  const dir = fs.mkdtempSync(path.join(deps.tmp(), 'pub-'));
  try {
    fs.writeFileSync(path.join(dir, 'data.json'), data); fs.writeFileSync(path.join(dir, 'ops.json'), JSON.stringify(ops || []));
    const zip = path.join(dir, `${slug}.zip`);
    const r = lastJson(await deps.python(['lib/templates/edit.py', 'package', path.join(dir, 'data.json'), slug, '--ops', path.join(dir, 'ops.json'), '--media-from', deps.publicBase(`${row.id}/t/`), '--zip', zip, '--verify'])) || { ok: false, why: ['the package step printed nothing'] };
    if (!r.ok || !fs.existsSync(zip)) return { ok: false, why: (r.why || []).slice(0, 3) };
    const hash = editsHash(ops), keyZip = `${row.id}/${slug}.edited-${hash}.zip`;
    await deps.writePrivate(keyZip, fs.readFileSync(zip), 'application/zip');
    const files = lastJson(await deps.python(['lib/templates/edit.py', 'files', zip])) || {};
    if (!(files.files || []).some(f => f.file === 'index.html')) return { ok: false, why: ['the package has no page'] };
    // the site is the page with what it loads; the package's data.json and README stay in the download only
    return { ok: true, bytes: r.bytes, key: keyZip, hash, files: files.files.filter(f => !['data.json', 'README.txt'].includes(f.file)) };
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
}

// a production deployment of the files, then its alias; -> {id, url}
export async function deploy({ files, name, env, fetch, sleep = ms => new Promise(r => setTimeout(r, ms)) }) {
  const team = env.VERCEL_TEAM_ID ? `?teamId=${encodeURIComponent(env.VERCEL_TEAM_ID)}` : '';
  const H = { authorization: `Bearer ${env.VERCEL_TOKEN}`, 'content-type': 'application/json' };
  const call = async (method, url, body) => { const r = await fetch(`https://api.vercel.com${url}${team}`, { method, headers: H, ...(body ? { body: JSON.stringify(body) } : {}) }); const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(`vercel ${r.status}: ${String(j.error?.message || '').slice(0, 160)}`); return j; };
  const d = await call('POST', '/v13/deployments', { name: env.VERCEL_PROJECT || 'swarmsite-sites', target: 'production', projectSettings: { framework: null }, files: files.map(f => ({ file: f.file, data: f.data, encoding: 'base64' })) });
  let state = d.readyState;
  for (let i = 0; state !== 'READY' && i < 60; i++) { if (state === 'ERROR' || state === 'CANCELED') throw new Error(`vercel deployment ${state.toLowerCase()}`); await sleep(2000); state = (await call('GET', `/v13/deployments/${d.id}`)).readyState; }
  if (state !== 'READY') throw new Error('vercel deployment did not become ready');
  await call('POST', `/v2/deployments/${d.id}/aliases`, { alias: `${name}.${DOMAIN}` });
  return { id: d.id, url: `https://${name}.${DOMAIN}` };
}

// one publish: the name claimed, the package verified, the same files deployed; the state saved at each turn
export async function runPublish(deps) {
  const { row, slug, name, user } = deps; const at = () => new Date().toISOString();
  const claim = `names/${name}.json`; const held = await deps.readPrivate(claim);
  if (held) { const h = JSON.parse(String(held)); if (h.job !== row.id) { await deps.save({ status: 'refused', slug, name, why: ['That name is taken.'], at: at() }); return { ok: false }; } }
  await deps.writePrivate(claim, Buffer.from(JSON.stringify({ job: row.id, user: user.id, at: at() })), 'application/json');
  await deps.save({ status: 'packaging', slug, name, at: at() });
  const ops = await deps.edits();
  const pkg = await verifiedPackage(deps, ops);
  if (!pkg.ok) { await deps.save({ status: 'refused', slug, name, why: pkg.why, at: at() }); return { ok: false }; }
  await deps.save({ status: 'deploying', slug, name, hash: pkg.hash, package: pkg.key, at: at() });
  try { const d = await deploy({ files: pkg.files, name, env: deps.env, fetch: deps.fetch, sleep: deps.sleep });
    await deps.save({ status: 'live', slug, name, url: d.url, deployment: d.id, hash: pkg.hash, package: pkg.key, bytes: pkg.bytes, at: at() }); return { ok: true, url: d.url }; }
  catch (e) { await deps.save({ status: 'failed', slug, name, why: [String(e.message).slice(0, 200)], hash: pkg.hash, package: pkg.key, at: at() }); return { ok: false }; }
}

// the download with the edits: the same verified package, made without publishing
export async function runRepackage(deps) {
  const { slug } = deps; const at = () => new Date().toISOString();
  await deps.save({ status: 'packaging', slug, at: at() });
  const ops = await deps.edits(); const pkg = await verifiedPackage(deps, ops);
  if (!pkg.ok) { await deps.save({ status: 'refused', slug, why: pkg.why, at: at() }); return { ok: false }; }
  await deps.save({ status: 'ready', slug, hash: pkg.hash, package: pkg.key, bytes: pkg.bytes, at: at() }); return { ok: true };
}

// which package a download of `slug` hands out: the verified package of the edits kept now, when there is one
export function editedPackage(result, slug, hash) {
  for (const s of [result?.edited, result?.publish]) if (s && s.slug === slug && s.hash === hash && s.package && ['ready', 'deploying', 'live', 'failed'].includes(s.status)) return s.package;
  return null;
}
