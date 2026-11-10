/* The headline of a composed first screen is sized from what a browser measures, not from an estimate.
   Draw a composition whose hand-broken headline is sized too large (a wrong measurement), see measure.mjs report the
   line that no longer stays on one line, write the real measurement into the composition, and see it fit. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const python = process.env.PYTHON || 'python3';
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-compose-measure-'));
const run = (cmd, args, input) => { const r = spawnSync(cmd, args, { encoding: 'utf8', input, maxBuffer: 1 << 28 }); assert.equal(r.status, 0, r.stderr || r.stdout); return r.stdout; };
try {
  for (const name of ['direction', 'images', 'inventory', 'assets']) { const src = `tests/${name}.sample.json`; if (fs.existsSync(src)) fs.copyFileSync(src, path.join(dir, `${name}.json`)); }
  const direction = JSON.parse(fs.readFileSync(path.join(dir, 'direction.json'), 'utf8')); direction.kind = 'place'; direction.hero.h1 = 'Bašta gde Beograd <em>slavi</em>';
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  const page = path.join(dir, 'page.html'); run(python, ['lib/render/render_bp.py', dir, 'tengile', page]);

  // the composition is drawn by the composition renderer; `fit` is whatever this test says it is
  const draw = (fit, out) => run(python, ['-c', `
import json, sys
sys.path.insert(0, 'lib/compose')
import content as C, render_ir as IR
page = open(sys.argv[1], encoding='utf-8').read(); images = json.load(open(sys.argv[2])); c = C.from_page(page, images)
nodes = [{'id': 'h1', 't': 'text', 'src': 'hero.h1', 'as': 'h1', 'size': 'mega', 'lines': [2, 2], 'indent': [0, 2], 'mark': 'outline', 'at': {'col': [1, 8], 'row': 1}}]
row = 2
for address in c['text']:
    if address != 'hero.h1': nodes.append({'id': 'n%d' % row, 't': 'text', 'src': address, 'as': 'lede' if address == 'hero.lede' else 'label', 'at': {'col': [1, 7], 'row': row}}); row += 1
nodes.append({'id': 'go', 't': 'actions', 'src': sorted(c['actions']), 'at': {'col': [1, 7], 'row': row}})
fit = json.loads(sys.argv[4])
if fit: nodes[0]['fit'] = fit
ir = {'ir': '0.2', 'hero': {'rows': ['auto'] * row, 'nodes': nodes}}
out, report = IR.transplant(page, ir, images)
assert report['drawn'], report['errors']
open(sys.argv[3], 'w', encoding='utf-8').write(out)
`, page, path.join(dir, 'images.json'), out, JSON.stringify(fit)]);
  const measure = file => JSON.parse(run('node', ['lib/compose/measure.mjs', file]).trim().split('\n').pop());

  const estimated = path.join(dir, 'estimated.html'); draw(null, estimated);
  const first = measure(estimated);
  assert.ok(first.fit && first.fit.line > first.fit.word && first.fit.word > 1, `the widest line is wider than the widest word: ${JSON.stringify(first.fit)}`);
  assert.equal(first.mobile.wrapped.length, 0, 'on a phone a long hand-broken headline wraps by itself and is not a broken line');

  // a measurement a third too small: the headline is drawn too large and its long line cannot stay on one line
  const wrong = path.join(dir, 'wrong.html'); draw({ line: +(first.fit.line * 0.68).toFixed(3), word: first.fit.word }, wrong);
  const broken = measure(wrong);
  assert.ok(broken.desktop.wrapped.length >= 1, `a line that does not fit is reported: ${JSON.stringify(broken.desktop)}`);
  assert.match(broken.desktop.wrapped[0].text, /\S/);
  assert.ok(Math.abs(broken.fit.line - first.fit.line) / first.fit.line < 0.02, 'the width of the words in em does not depend on the size they were drawn at');

  // the real measurement written into the composition: every line stays on its line, with almost no room to spare
  const fitted = path.join(dir, 'fitted.html'); draw(first.fit, fitted);
  const clean = measure(fitted);
  assert.deepEqual(clean.desktop.wrapped, [], JSON.stringify(clean.desktop));
  assert.ok(Math.abs(clean.fit.line - first.fit.line) / first.fit.line < 0.02);
  assert.ok(clean.desktop.actions_bottom > 0 && clean.desktop.fold === 900);

  // a page the production renderer built, with no composition, can still be asked where its first button ends
  const template = measure(page);
  assert.equal(template.fit, null); assert.ok(template.desktop.actions_bottom > 0); assert.deepEqual(template.desktop.wrapped, []);
  console.log('compose-hero-measure: ok', JSON.stringify({ fit: first.fit, wrapped_when_wrong: broken.desktop.wrapped.length }));
} finally { fs.rmSync(dir, { recursive: true, force: true }); }
