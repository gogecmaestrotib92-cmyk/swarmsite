#!/usr/bin/env node
/* loadtest.mjs — what N jobs at once cost: time per step for each job, and for the process tree the peak memory, the
   processor time and the most browsers alive at one moment. Three ways to run it; each says what it did not measure.

   1 · local — N template jobs at once in this process, through the worker's own flow (server/templates.mjs
       runTemplateJob) with the real build, gate, covers and package (Python, node, Chrome). No database, no bucket and
       no model: the capture is the made-up page of tests/fixtures/templates/capture.py and the reader is a stub, so
       `capture` and `read` are NOT measured here (take them from the worker's own records, or from `cmd` below).

         node scripts/loadtest.mjs local --at 1 [--out result.json]

   2 · cmd — one command, its whole process tree sampled (a real capture of a real address needs no model):

         node scripts/loadtest.mjs cmd -- node lib/pipeline/capture.mjs https://example.com --out /tmp/cap

   3 · worker — N real jobs sent at once to a running worker, timed from its own records (`steps`, `timings_ms`,
       `GET /load` when the worker runs with LOAD_STATS=1). This spends the worker's model credit and takes its slots:
       it does nothing without --yes. Jobs from one address are limited (JOBS_PER_IP_PER_HOUR, 3 unless set): raise it
       on the worker being measured. `--form` sends made-up forms (no reader call); `--urls file` one address a line.

         node scripts/loadtest.mjs worker https://<worker> --at 4 --form --yes [--out result.json]

   Each run prints one JSON document (and writes it with --out); `table` prints saved runs side by side:

         node scripts/loadtest.mjs table run1.json run2.json …                                                        */
import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { spawn } from 'node:child_process'; import { fileURLToPath } from 'node:url';
import { makeSampler } from '../server/load.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2), mode = argv.shift();
const opt = (k, d = '') => { const i = argv.indexOf(k); return i === -1 ? d : argv.splice(i, 2)[1] ?? d; };
const flag = k => { const i = argv.indexOf(k); if (i === -1) return false; argv.splice(i, 1); return true; };
const machine = () => ({ platform: `${process.platform} ${process.arch}`, cpus: os.availableParallelism?.() || os.cpus().length, memory_mb: Math.round(os.totalmem() / 1048576), cpu: os.cpus()[0]?.model || '' });
const r1 = n => Math.round(n * 10) / 10;
const finish = (doc, out) => { const text = JSON.stringify(doc, null, 1); if (out) fs.writeFileSync(out, text + '\n'); console.log(text); };

const child = (cmd, args, { env = {}, onLine } = {}) => new Promise((ok, no) => {
  const p = spawn(cmd, args, { cwd: ROOT, env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1', ...env } }); let out = '', err = '', buf = '';
  p.stdout.on('data', d => { out += d; if (onLine) { buf += d; const l = buf.split('\n'); buf = l.pop(); l.forEach(x => { try { onLine(x); } catch {} }); } }); p.stderr.on('data', d => { err += d; });
  p.on('error', no); p.on('close', c => c === 0 ? ok(out) : no(new Error(`${cmd} ${args[0]} exit ${c}: ${err.slice(-600)}`)));
});

async function local() {
  const at = Math.max(1, +opt('--at', '1')), out = opt('--out'), py = process.env.PYTHON || 'python3';
  const { runTemplateJob } = await import('../server/templates.mjs');
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'loadtest-')), sampler = makeSampler({ everyMs: 500 }), marks = [];
  const mark = (job, id, status) => { sampler.sample(); const s = sampler.stats(); marks.push({ job, id, status, t: Date.now(), cpu_s: s.cpu_s }); };
  const one = async n => {
    const jobRoot = fs.mkdtempSync(path.join(tmp, `job${n}-`)), dir = path.join(jobRoot, 'site'), calls = [];
    const job = { id: `00000000-0000-4000-8000-${String(n).padStart(12, '0')}`, url: `https://www.tallyfern-${n}.example/`, options: { engine: 'templates' }, result: {} };
    const run = async (cmd, args, opts = {}) => {
      const t = Date.now(), name = args[0] === '-c' ? 'reader (stub)' : path.basename(args[0]) + (args[0].endsWith('job.py') ? ' ' + args[1] : '');
      try {
        if (args[0] === 'lib/pipeline/capture.mjs') { await child(py, ['tests/fixtures/templates/capture.py', dir, 'product']); fs.writeFileSync(path.join(dir, 'before-hero.jpg'), 'jpg'); return ''; }
        if (args[0] === '-c') return '{"what":"A made-up page for the measurement","n":3}';
        return await child(cmd, args, { env: { SWARM_JOB_DIR: dir }, onLine: opts.onLine });
      } finally { calls.push({ name, ms: Date.now() - t }); }
    };
    const t0 = Date.now(); let result = null, error = '';
    try {
      result = await runTemplateJob({ job, dir, jobRoot, run, self: 'http://local', chrome: process.env.CHROME_PATH || '',
        upload: async (local, key) => { fs.statSync(local); return 'http://local/previews/' + key; }, uploadPrivate: async local => { fs.statSync(local); },
        fetchUpload: async () => { throw new Error('no uploads in a local run'); }, publicBase: key => 'http://local/previews/' + key,
        setStep: async (id, status) => mark(n, id, status), emit: async () => {}, save: async () => {} });
    } catch (e) { error = String(e.message || e).slice(0, 400); }
    const t = result?.templates || {};
    return { job: n, ok: !!result && !error, error, seconds: r1((Date.now() - t0) / 1000), steps_s: Object.fromEntries(Object.entries(t.timings_ms?.steps || {}).map(([k, v]) => [k, r1(v / 1000)])),
      build_s: Object.fromEntries(Object.entries(t.timings_ms || {}).filter(([k]) => k !== 'steps').map(([k, v]) => [k, r1(v / 1000)])),
      designs: (t.variants || []).length, packages: (t.variants || []).map(v => v.package), not_shown: (t.not_shown || []).map(v => v.failed), calls };
  };
  sampler.start(); const t0 = Date.now();
  const jobs = await Promise.all(Array.from({ length: at }, (_, i) => one(i + 1)));
  sampler.sample(); sampler.stop(); const s = sampler.stats(), wall = (Date.now() - t0) / 1000;
  // with one job the tree's processor time can be laid on its steps; with several at once the steps overlap and only the whole is said
  let per_step = null;
  if (at === 1) { per_step = {}; for (const m of marks.filter(m => m.status === 'running')) { const e = marks.find(x => x.id === m.id && x.status === 'done'); if (e) per_step[m.id] = { s: r1((e.t - m.t) / 1000), cpu_s: r1(e.cpu_s - m.cpu_s) }; } }
  fs.rmSync(tmp, { recursive: true, force: true });
  finish({ mode: 'local', at, when: new Date().toISOString(), machine: machine(), not_measured: ['capture (a made-up page stands in)', 'read (a stub stands in for the model call)', 'database and storage round trips'],
    wall_s: r1(wall), tree: { peak_rss_mb: s.peak.rss_mb, peak_processes: s.peak.procs, browsers_at_peak: s.peak.browsers, cpu_s: r1(s.cpu_s), average_cores: r1(s.cpu_s / wall), samples: s.samples }, per_step, jobs }, out);
  if (jobs.some(j => !j.ok)) process.exitCode = 1;
}

async function cmd() {
  const out = opt('--out'), i = argv.indexOf('--'), rest = i === -1 ? argv : argv.slice(i + 1);
  if (!rest.length) { console.error('usage: loadtest.mjs cmd [--out file] -- <command> [args …]'); process.exit(2); }
  const sampler = makeSampler({ everyMs: 500 }); sampler.start(); const t0 = Date.now(); let error = '';
  try { await child(rest[0], rest.slice(1)); } catch (e) { error = String(e.message || e).slice(0, 400); }
  sampler.sample(); sampler.stop(); const s = sampler.stats(), wall = (Date.now() - t0) / 1000;
  finish({ mode: 'cmd', command: rest.join(' '), when: new Date().toISOString(), machine: machine(), ok: !error, error, wall_s: r1(wall),
    tree: { peak_rss_mb: s.peak.rss_mb, peak_processes: s.peak.procs, browsers_at_peak: s.peak.browsers, cpu_s: r1(s.cpu_s), average_cores: r1(s.cpu_s / wall), samples: s.samples } }, out);
  if (error) process.exitCode = 1;
}

// a made-up business for a form job: a name is all a form needs, and no two jobs of a run share one (the same site is not queued twice)
export const madeUpForm = (n, tag) => ({ name: `Tallyfern ${tag} ${n}`, kind: 'software', sentence: 'A ledger for market stalls that balances itself at closing time',
  offers: [{ name: 'Counts the till' }, { name: 'Closes the day' }, { name: 'Sends the accountant a copy' }], steps: [{ title: 'Connect the card reader' }, { title: 'Close the day' }],
  figures: [{ v: '1 200', l: 'stalls use it' }, { v: '4 min', l: 'to close a day' }], contact: { email: 'hello@tallyfern.example' } });
// what one job's own record says of its time: waited in the queue, each step, and from sent to done
export function jobTimes(row, sentAt, doneAt) {
  const steps = Array.isArray(row?.steps) ? row.steps : [], first = steps.map(s => s.at).filter(Boolean).sort()[0];
  const t = row?.result?.templates?.timings_ms || {}, total = Number(row?.result?.seconds) || null;
  // the first step's mark is written when it ENDS as well; the queue wait is what is left of sent → done once the job's own seconds are taken away
  const whole = doneAt && sentAt ? (doneAt - sentAt) / 1000 : null;
  return { status: row?.status || 'unknown', error: row?.error ? String(row.error).slice(0, 200) : '', whole_s: whole === null ? null : r1(whole), job_s: total,
    queued_s: whole !== null && total !== null ? r1(Math.max(0, whole - total)) : null, first_mark: first || null,
    steps_s: Object.fromEntries(Object.entries(t.steps || {}).map(([k, v]) => [k, r1(v / 1000)])), build_s: Object.fromEntries(Object.entries(t).filter(([k]) => k !== 'steps').map(([k, v]) => [k, r1(v / 1000)])),
    designs: (row?.result?.templates?.variants || []).length, packages: (row?.result?.templates?.variants || []).map(v => v.package) };
}
async function worker() {
  const base = String(argv.shift() || '').replace(/\/+$/, ''), at = Math.max(1, +opt('--at', '1')), out = opt('--out'), urlsFile = opt('--urls'), form = flag('--form'), yes = flag('--yes'), maxMin = +opt('--minutes', '60');
  if (!/^https?:\/\//.test(base) || (!form && !urlsFile)) { console.error('usage: loadtest.mjs worker https://<worker> --at N (--form | --urls file) --yes [--minutes 60] [--out file]'); process.exit(2); }
  const urls = urlsFile ? fs.readFileSync(urlsFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean) : [];
  if (!form && urls.length < at) { console.error(`${at} jobs at once need ${at} different addresses; ${urlsFile} has ${urls.length}`); process.exit(2); }
  const J = async (p, init) => { const r = await fetch(base + p, init); let body = null; try { body = await r.json(); } catch {} return { status: r.status, body }; };
  if (!yes) { console.error(`This would start ${at} real job(s) on ${base} — ${form ? 'made-up forms (no reader call)' : 'the addresses of ' + urlsFile + ' (two model calls each)'}; they take the worker's slots from visitors. Add --yes to do it.`); process.exit(2); }
  const busy = [...((await J('/jobs?status=running')).body || []), ...((await J('/jobs?status=queued')).body || [])];
  const load0 = await J('/load?reset=1'), tag = Date.now().toString(36);
  const sentAt = Date.now();
  const sent = await Promise.all(Array.from({ length: at }, (_, i) => J('/jobs', { method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify(form ? { options: { engine: 'templates', source: 'form' }, form: madeUpForm(i + 1, tag) } : { url: urls[i], options: { engine: 'templates' } }) })));
  const jobs = sent.map((s, i) => ({ n: i + 1, id: s.body?.id || null, refused: s.body?.id ? '' : `${s.status} ${s.body?.error || ''}`.trim(), reused: !!s.body?.reused, row: null, doneAt: 0 }));
  const peaks = [];
  while (jobs.some(j => j.id && !j.doneAt) && Date.now() - sentAt < maxMin * 60e3) {
    await new Promise(r => setTimeout(r, 5000));
    for (const j of jobs.filter(j => j.id && !j.doneAt)) { const r = await J('/jobs/' + j.id).catch(() => null); if (r?.body?.status) { j.row = r.body; if (['done', 'failed'].includes(r.body.status)) j.doneAt = Date.now(); } }
    const l = await J('/load').catch(() => null); if (l?.status === 200) peaks.push(l.body);
  }
  const last = peaks[peaks.length - 1] || null;
  finish({ mode: 'worker', worker: base, at, kind: form ? 'form' : 'address', when: new Date(sentAt).toISOString(), others_in_the_queue_at_start: busy.length,
    wall_s: r1((Math.max(...jobs.map(j => j.doneAt || Date.now())) - sentAt) / 1000),
    load: last ? { note: 'GET /load answers for whichever instance took the request; with several instances this is one of them', cpus: last.cpus, peak: last.peak, cpu_s: last.cpu_s, cgroup: last.cgroup, slots: last.slots }
      : { note: load0.status === 200 ? 'no reading' : 'the worker does not serve /load (set LOAD_STATS=1 on it); memory and processor are to be read from the host\'s own metrics' },
    jobs: jobs.map(j => ({ job: j.n, id: j.id, refused: j.refused, reused: j.reused, ...(j.id ? jobTimes(j.row, sentAt, j.doneAt) : {}) })) }, out);
}

function table() {
  const rows = argv.map(f => JSON.parse(fs.readFileSync(f, 'utf8'))), med = v => { const a = v.filter(Number.isFinite).sort((x, y) => x - y); return a.length ? r1(a.length % 2 ? a[a.length >> 1] : (a[a.length / 2 - 1] + a[a.length / 2]) / 2) : null; };
  const steps = [...new Set(rows.flatMap(r => (r.jobs || []).flatMap(j => Object.keys(j.steps_s || {}))))];
  const head = ['run', 'at once', 'done', 'wall s', 'job s (median)', 'slowest s', ...steps.map(s => s + ' s'), 'peak MB', 'browsers', 'CPU s', 'avg cores'];
  const line = r => { const js = r.jobs || [], whole = js.map(j => j.whole_s ?? j.seconds), mem = r.tree?.peak_rss_mb ?? r.load?.cgroup?.memory_peak_mb ?? r.load?.peak?.rss_mb ?? '';
    return [r.mode, r.at ?? 1, `${js.filter(j => j.ok ?? j.status === 'done').length}/${js.length}`, r.wall_s, med(js.map(j => j.job_s ?? j.seconds)), whole.length ? Math.max(...whole.filter(Number.isFinite)) : '',
      ...steps.map(s => med(js.map(j => j.steps_s?.[s])) ?? ''), mem, r.tree?.browsers_at_peak ?? r.load?.peak?.browsers ?? '', r.tree?.cpu_s ?? r.load?.cgroup?.cpu_s_since ?? r.load?.cpu_s ?? '', r.tree?.average_cores ?? ''].join(' | '); };
  console.log(['| ' + head.join(' | ') + ' |', '|' + head.map(() => '---').join('|') + '|', ...rows.map(r => '| ' + line(r) + ' |')].join('\n'));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const go = { local, cmd, worker, table }[mode];
  if (!go) { console.error('usage: loadtest.mjs local --at N | cmd -- <command> | worker <address> --at N (--form | --urls file) --yes | table <run.json> …'); process.exit(2); }
  await go();
}
