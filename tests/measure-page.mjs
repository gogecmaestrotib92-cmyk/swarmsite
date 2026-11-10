/* The page that is about to ship is measured in a browser while it loads, scrolls and moves (lib/qa/measure.py →
   lib/qa/inspect.mjs --quick), and the Standard's rules turn the readings into findings (lib/qa/standard.py).
   A sample page of ours: both viewports are read, the load and the scroll are sampled, the measured checks are there,
   our renderer honours reduce-motion (T-13 passes), and a finding carries its evidence. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const python = process.env.PYTHON || 'python3';
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-measure-'));
const run = (cmd, args) => { const r = spawnSync(cmd, args, { encoding: 'utf8', maxBuffer: 1 << 28, env: { ...process.env, LIVETEST: '1' } }); assert.equal(r.status, 0, r.stderr || r.stdout); return r.stdout; };
try {
  for (const name of ['direction', 'images', 'inventory', 'assets']) { const src = `tests/${name}.sample.json`; if (fs.existsSync(src)) fs.copyFileSync(src, path.join(dir, `${name}.json`)); }
  const page = path.join(dir, 'page.html'); run(python, ['lib/render/render_bp.py', dir, 'tengile', page]);
  const said = JSON.parse(run(python, ['lib/qa/measure.py', page, dir]).trim().split('\n').pop());
  const evidence = JSON.parse(fs.readFileSync(path.join(dir, 'measure.json'), 'utf8')), report = JSON.parse(fs.readFileSync(path.join(dir, 'findings.json'), 'utf8'));
  assert.equal(evidence.profile, 'quick'); assert.deepEqual(evidence.failed, []);
  for (const view of ['desktop', 'mobile']) {
    const v = evidence.views[view]; assert.ok(v.type.length > 3 && v.sections.length > 3, `${view}: type and sections are read`);
    assert.ok(v.load && v.load.session.frames > 30, `${view}: the load is sampled`); assert.ok(v.scroll && v.scroll.session.travelled_px > 1000, `${view}: the page is scrolled and sampled`);
    assert.ok(report.readings[view] && report.readings[view].ground_changes >= 0);
  }
  assert.ok(evidence.views.desktop.surfaces.rules && evidence.views.desktop.letters, 'rules and letters are read');
  const checks = Object.fromEntries(report.technical.map(c => [c.id, c.pass]));
  assert.equal(checks['T-13'], true, 'with reduce-motion asked for, nothing of ours reveals on load'); assert.ok('T-19' in checks && 'T-16' in checks);
  assert.ok(Array.isArray(report.findings) && report.findings.length === said.findings.length);
  for (const f of report.findings) { assert.ok(f.id && f.area && f.reason && f.correction && f.expectation && f.evidence.expected, JSON.stringify(f)); assert.equal(f.confidence, 'measured'); }
  console.log('measure-page: ok', JSON.stringify(said));
} finally { fs.rmSync(dir, { recursive: true, force: true }); }
