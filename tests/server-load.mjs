// Measuring a worker: the process tree's memory, processor time and browsers are read rightly (server/load.mjs), a worker serves
// them only where the deployment says so, and the load tool (scripts/loadtest.mjs) reads a job's times from its own record.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { parsePs, tree, makeSampler, processes } from '../server/load.mjs';
import { madeUpForm, jobTimes } from '../scripts/loadtest.mjs'; import { formProblem } from '../server/templates.mjs';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'), src = fs.readFileSync(path.join(root, 'server/index.mjs'), 'utf8');

// 3 · the process tree
{ const rows = parsePs('    1     0  19792  80:06.63 /sbin/launchd\n  500     1  1024   0:01.50 node\n  501   500  2048   1:02.25 /Applications/Google Chrome.app/Contents/MacOS/Google Chrome\n  502   501  4096 1-02:03:04 Google Chrome Helper (Renderer)\n  900     1  9999   0:09.00 other\n');
  assert.equal(rows.length, 5); assert.deepEqual(rows[2], { pid: 501, ppid: 500, rss: 2048 * 1024, cpu: 62.25, name: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  assert.equal(rows[3].cpu, 86400 + 2 * 3600 + 3 * 60 + 4);
  assert.deepEqual(tree(rows, 500).map(r => r.pid).sort(), [500, 501, 502], 'the worker and everything under it, nothing beside it');
  let list = [{ pid: 10, ppid: 1, rss: 100 * 1048576, cpu: 5, name: 'node' }], clock = 0;
  const S = makeSampler({ root: 10, list: () => list, now: () => clock, group: () => null }); S.reset();
  list = [...list.map(r => ({ ...r, cpu: 6 })), { pid: 11, ppid: 10, rss: 900 * 1048576, cpu: 2, name: 'chrome' }, { pid: 12, ppid: 11, rss: 500 * 1048576, cpu: 0.5, name: 'chrome' }]; clock = 1000; S.sample();
  list = [{ pid: 10, ppid: 1, rss: 100 * 1048576, cpu: 6.5, name: 'node' }, { pid: 11, ppid: 10, rss: 200 * 1048576, cpu: 4, name: 'chrome' }]; clock = 2000; S.sample();
  list = [{ pid: 10, ppid: 1, rss: 100 * 1048576, cpu: 6.5, name: 'node' }]; clock = 3000; S.sample();
  const st = S.stats();
  assert.deepEqual(st.peak, { rss_mb: 1500, procs: 3, browsers: 2, at: 1000 }, 'the peak is the largest moment, kept after the browsers are gone');
  assert.deepEqual(st.now, { rss_mb: 100, procs: 1, browsers: 0 });
  assert.equal(st.cpu_s, 3.5, 'processor time as it grew while watched: 1.5 of the worker, 2 of a browser seen twice; what a process had used before it was first seen is not counted');
  assert.equal(st.cgroup, null);
  const me = tree(processes(), process.pid); assert.ok(me.length >= 1 && me.find(r => r.pid === process.pid).rss > 10e6, 'this machine\'s processes are readable');
  assert.ok(/const LOAD = process\.env\.LOAD_STATS === '1' \?/.test(src) && /if \(!LOAD\) return res\.status\(404\)/.test(src), 'a worker is measured only where the deployment says so'); }

// 4 · the load tool: a made-up form the server accepts, no two alike; a job's times from its own record
{ assert.equal(formProblem(madeUpForm(1, 'x')), ''); assert.notEqual(madeUpForm(1, 'x').name, madeUpForm(2, 'x').name);
  const t = jobTimes({ status: 'done', steps: [{ id: 'form', at: '2026-11-18T10:00:30Z' }], result: { seconds: 120, templates: { variants: [{ package: 'ready' }, { package: 'refused' }], timings_ms: { gate: 40000, steps: { choose: 61000, package: 30500 } } } } }, 1000, 301000);
  assert.deepEqual([t.whole_s, t.job_s, t.queued_s, t.steps_s.choose, t.steps_s.package, t.build_s.gate, t.designs], [300, 120, 180, 61, 30.5, 40, 2]); assert.deepEqual(t.packages, ['ready', 'refused']);
  assert.equal(jobTimes(null, 0, 0).status, 'unknown'); }
console.log('Load: the process tree read rightly, served only on a worker that is being measured, a job timed from its own record');
