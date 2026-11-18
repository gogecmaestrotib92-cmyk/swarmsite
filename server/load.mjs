/* load.mjs — what a worker's process tree is using: memory, processor time, how many browsers.

   A job is a chain of child processes (node capture, python build, node gate → Chrome and its helpers), so what a job
   costs is read from the tree under the worker, never from the worker's own process. Read from /proc on Linux (the
   deployed image), from `ps` elsewhere (a Mac). Where the container says so (cgroup v2: memory.peak, cpu.stat,
   memory.max, cpu.max) its own account is reported beside the tree's — that is the figure the host bills and kills by.

     processes()            → [{pid, ppid, rss (bytes), cpu (seconds, user + system), name}] of every process readable
     tree(rows, root)       → the rows that are `root` or descend from it
     makeSampler({root, everyMs, list}) → {start(), stop(), sample(), reset(), stats()}
     stats() → {now: {rss_mb, procs, browsers}, peak: {rss_mb, procs, browsers, at}, cpu_s, samples, since, cpus, cgroup}

   `cpu_s` is the processor time the tree spent since start()/reset(): each process's own counter, summed as it grows,
   so a process that has exited keeps what it had used when last seen (a process shorter than one interval is missed;
   the cgroup's figure, where there is one, misses nothing). No model, no network. */
import fs from 'node:fs'; import os from 'node:os'; import { execFileSync } from 'node:child_process';

const TICK = 100, PAGE = 4096;   // Linux: clock ticks a second and bytes a page, as every image we run on has them
const BROWSER = /chrom|headless_shell/i;

function fromProc() {
  const out = [];
  for (const d of fs.readdirSync('/proc')) {
    if (!/^\d+$/.test(d)) continue;
    try {
      const s = fs.readFileSync(`/proc/${d}/stat`, 'utf8'), close = s.lastIndexOf(')');   // the name may hold spaces and brackets
      const f = s.slice(close + 2).split(' ');   // f[0] is the state: field 3 of the file
      out.push({ pid: +d, ppid: +f[1], rss: +f[21] * PAGE, cpu: (+f[11] + +f[12]) / TICK, name: s.slice(s.indexOf('(') + 1, close) });
    } catch { /* gone between the listing and the read */ }
  }
  return out;
}
const seconds = t => { const m = /^(?:(\d+)-)?(?:(\d+):)?(\d+):(\d+(?:\.\d+)?)$/.exec(t); return m ? (+m[1] || 0) * 86400 + (+m[2] || 0) * 3600 + +m[3] * 60 + +m[4] : 0; };
export function parsePs(text) {
  return String(text).split('\n').map(l => /^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(.*)$/.exec(l)).filter(Boolean)
    .map(m => ({ pid: +m[1], ppid: +m[2], rss: +m[3] * 1024, cpu: seconds(m[4]), name: m[5].trim() }));
}
export function processes() {
  if (process.platform === 'linux' && fs.existsSync('/proc/self/stat')) return fromProc();
  try { return parsePs(execFileSync('ps', ['-A', '-o', 'pid=,ppid=,rss=,time=,comm='], { encoding: 'utf8', maxBuffer: 16e6 })); } catch { return []; }
}
export function tree(rows, root) {
  const kids = new Map(); for (const r of rows) { if (!kids.has(r.ppid)) kids.set(r.ppid, []); kids.get(r.ppid).push(r); }
  const out = [], seen = new Set(), todo = rows.filter(r => r.pid === root);
  while (todo.length) { const r = todo.pop(); if (seen.has(r.pid)) continue; seen.add(r.pid); out.push(r); todo.push(...(kids.get(r.pid) || [])); }
  return out;
}
// the container's own account (cgroup v2), where there is one
export function cgroup(base = '/sys/fs/cgroup') {
  const read = f => { try { return fs.readFileSync(`${base}/${f}`, 'utf8').trim(); } catch { return null; } };
  const mb = v => v && /^\d+$/.test(v) ? Math.round(+v / 1048576) : null;
  const cur = read('memory.current'); if (cur === null) return null;
  const usage = /usage_usec (\d+)/.exec(read('cpu.stat') || ''), max = (read('cpu.max') || '').split(' ');
  return { memory_mb: mb(cur), memory_peak_mb: mb(read('memory.peak')), memory_max_mb: mb(read('memory.max')),
    cpu_s: usage ? Math.round(+usage[1] / 1e4) / 100 : null, cpus_max: max.length === 2 && /^\d+$/.test(max[0]) ? Math.round(+max[0] / +max[1] * 100) / 100 : null };
}

export function makeSampler({ root = process.pid, everyMs = 1000, list = processes, now = () => Date.now(), group = cgroup } = {}) {
  let timer = null, last = new Map(), cpu = 0, samples = 0, since = now(), g0 = null;
  let cur = { rss_mb: 0, procs: 0, browsers: 0 }, peak = { ...cur, at: since };
  const sample = () => {
    const rows = tree(list(), root), seen = new Map();
    for (const r of rows) { const k = r.pid + ':' + r.name, was = last.get(k); cpu += Math.max(0, r.cpu - (was ?? r.cpu)); seen.set(k, r.cpu); }
    if (!samples) for (const [k, v] of seen) last.set(k, v);   // the first reading is where the count starts
    last = seen; samples++;
    cur = { rss_mb: Math.round(rows.reduce((a, r) => a + r.rss, 0) / 1048576), procs: rows.length, browsers: rows.filter(r => BROWSER.test(r.name)).length };
    if (cur.rss_mb > peak.rss_mb) peak = { ...cur, at: now() };
    return cur;
  };
  const reset = () => { cpu = 0; samples = 0; since = now(); last = new Map(); g0 = group(); sample(); peak = { ...cur, at: since }; };
  return {
    sample, reset,
    start() { if (timer) return; reset(); timer = setInterval(() => { try { sample(); } catch { /* a reading missed is a reading missed */ } }, everyMs); timer.unref?.(); },
    stop() { if (timer) clearInterval(timer); timer = null; },
    stats() { const g = group();
      return { now: cur, peak, cpu_s: Math.round(cpu * 100) / 100, samples, since, cpus: os.availableParallelism?.() || os.cpus().length,
        cgroup: g ? { ...g, cpu_s_since: g.cpu_s !== null && g0?.cpu_s != null ? Math.round((g.cpu_s - g0.cpu_s) * 100) / 100 : null } : null }; },
  };
}
