/* What a browser says about a picture the words stand on, and about a picture's real size.
   A section's picture is replaced by a nearly white photograph and made the backdrop: under a soft veil the light words
   do not read against what is really behind them and picmeasure.mjs says so; under a deep veil they do. A first screen on
   a backdrop is measured the same way. A tilted print is measured at its laid-out size, not at its turned bounding box. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const python = process.env.PYTHON || 'python3';
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-picture-measure-'));
const run = (cmd, args) => { const r = spawnSync(cmd, args, { encoding: 'utf8', maxBuffer: 1 << 28, env: { ...process.env, LIVETEST: '1' } }); assert.equal(r.status, 0, r.stderr || r.stdout); return r.stdout; };
try {
  for (const name of ['direction', 'images', 'inventory', 'assets']) { const src = `tests/${name}.sample.json`; if (fs.existsSync(src)) fs.copyFileSync(src, path.join(dir, `${name}.json`)); }
  const direction = JSON.parse(fs.readFileSync(path.join(dir, 'direction.json'), 'utf8')); direction.kind = 'place'; fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  const page = path.join(dir, 'page.html'); run(python, ['lib/render/render_bp.py', dir, 'tengile', page]);

  // draw: the "mk" section in the form asked for, on a picture of the colour and size asked for; optionally the first screen on its own photograph
  const draw = (entry, colour, size, hero, out) => run(python, ['-c', `
import base64, io, json, sys
sys.path.insert(0, 'lib/compose')
import content as C, pictures as P, render_ir as IR, sections as S
from PIL import Image
page = open(sys.argv[1], encoding='utf-8').read(); images = json.load(open(sys.argv[2]))
entry, colour, size, hero = json.loads(sys.argv[4]), json.loads(sys.argv[5]), json.loads(sys.argv[6]), json.loads(sys.argv[7])
mk = next(s for s in S.sections(page) if s['id'] == 'mk'); old = S.from_picture(page[mk['span'][0]:mk['span'][1]])['picture']['src']
buf = io.BytesIO(); Image.new('RGB', tuple(size), tuple(colour)).save(buf, 'JPEG', quality=50)
page = page.replace(old, 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode())
if hero:
    c = C.from_page(page, images)
    nodes = [{'id': 'bg', 't': 'media', 'src': 'hero.picture', 'bleed': 'full', 'scrim': True, 'at': {'col': [1, 13], 'row': [1, 5], 'z': 0}}]
    nodes += [{'id': 'cat', 't': 'text', 'src': 'hero.category', 'as': 'label', 'at': {'col': [1, 7], 'row': 1}}] if 'hero.category' in c['text'] else []
    nodes += [{'id': 'fact', 't': 'text', 'src': 'hero.fact', 'as': 'label', 'at': {'col': [8, 13], 'row': 1}}] if 'hero.fact' in c['text'] else []
    nodes += [{'id': 'h1', 't': 'text', 'src': 'hero.h1', 'as': 'h1', 'at': {'col': [1, 10], 'row': 2}}]
    nodes += [{'id': 'lede', 't': 'text', 'src': 'hero.lede', 'as': 'lede', 'at': {'col': [1, 7], 'row': 3}}] if 'hero.lede' in c['text'] else []
    nodes += [{'id': 'go', 't': 'actions', 'src': sorted(c['actions']), 'at': {'col': [1, 7], 'row': 4}}] if c['actions'] else []
    page, report = IR.transplant(page, {'ir': '0.2', 'hero': {'height': 'screen', 'rows': ['auto', '1fr', 'auto', 'auto'], 'nodes': nodes}}, images)
    assert report['drawn'], report['errors']
page, report = P.transplant(page, {'ir': '0.2', 'pictures': [entry]}, [])
assert report['drawn'], report['errors']
open(sys.argv[3], 'w', encoding='utf-8').write(page)
`, page, path.join(dir, 'images.json'), out, JSON.stringify(entry), JSON.stringify(colour), JSON.stringify(size), JSON.stringify(hero)]);
  const measure = file => JSON.parse(run('node', ['lib/compose/picmeasure.mjs', file]).trim().split('\n').pop());
  const of = (seen, view, id) => seen[view].find(s => s.id === id);

  // light words on a nearly white photograph under a soft veil: not readable, and the measurement says so
  const soft = path.join(dir, 'soft.html'); draw({ section: 'mk', form: 'backdrop', place: 'center', scrim: 'soft', height: 'lg' }, [246, 244, 240], [1600, 1100], false, soft);
  const pale = measure(soft); const mk = of(pale, 'desktop', 'mk');
  assert.equal(mk.form, 'backdrop'); assert.ok(mk.contrast && mk.contrast.ratio < mk.contrast.need, `the words do not read: ${JSON.stringify(mk.contrast)}`);
  assert.ok(mk.contrast.text.length > 0); assert.ok(Math.abs(mk.scale - Math.max(1440 / 1600, 702 / 1100)) < 0.03, `a backdrop is drawn at the size of its section: ${mk.scale}`);
  assert.equal(mk.limit, 1.35); assert.equal(mk.heading_out, 0); assert.ok(of(pale, 'mobile', 'mk').contrast, 'on a phone the words still stand on the picture and are measured there');
  assert.equal(pale.desktop.find(s => s.form === 'hero-backdrop'), undefined, 'a first screen that is not on a backdrop is not an entry');

  // the same picture under a deep veil: readable. And the first screen on its own photograph is measured the same way.
  const deep = path.join(dir, 'deep.html'); draw({ section: 'mk', form: 'backdrop', place: 'center', scrim: 'deep', height: 'lg' }, [246, 244, 240], [1600, 1100], true, deep);
  const dark = measure(deep); const read = of(dark, 'desktop', 'mk');
  assert.ok(read.contrast.ratio >= read.contrast.need, `under a deep veil the words read: ${JSON.stringify(read.contrast)}`); assert.ok(read.contrast.ratio > mk.contrast.ratio + 2);
  const hero = dark.desktop.find(s => s.form === 'hero-backdrop');
  assert.ok(hero && hero.id === 'top' && hero.contrast && hero.contrast.ratio > 1, `the first screen's words are measured against its backdrop: ${JSON.stringify(hero)}`);
  assert.ok(Math.abs(hero.scale - Math.max(1440 / 1344, 900 / 896)) < 0.04, `the backdrop fills the first screen: ${hero.scale}`);
  const phone = dark.mobile.find(s => s.form === 'hero-backdrop'); assert.ok(phone && phone.scale < 1 && phone.scale > 0.6, `on a phone the backdrop still fills the first screen: ${JSON.stringify(phone)}`);

  // a small print, turned four degrees: measured at its laid-out size, so it is within its pixels on both screens; beside the words, not under them
  const print = path.join(dir, 'print.html'); draw({ section: 'mk', form: 'offset', side: 'left', cols: 5, frame: 'paper', tilt: 4, title: 'lg' }, [120, 110, 100], [418, 315], false, print);
  const turned = measure(print);
  for (const view of ['desktop', 'mobile']) { const s = of(turned, view, 'mk'); assert.ok(s.scale <= 1.351, `${view}: ${s.scale}`); assert.equal(s.contrast, null); assert.equal(s.overlap, 0); }
  assert.ok(of(turned, 'desktop', 'mk').scale > 1.1, 'a small picture is drawn near the limit, not past it');
  // a picture that dissolves into its section, the words reaching two columns into it: they are measured against what is really under them there
  const reach = path.join(dir, 'reach.html'); draw({ section: 'mk', form: 'bleed', side: 'right', cols: 7, overlap: 2 }, [236, 232, 226], [1600, 1100], false, reach);   // a light picture on the light section: it may dissolve
  const into = of(measure(reach), 'desktop', 'mk');
  assert.ok(into.contrast && into.contrast.ratio > 1, `words in a dissolved edge are measured: ${JSON.stringify(into)}`); assert.equal(into.overlap, 0, 'reaching into a dissolved edge is not lying on the picture');
  const beside = path.join(dir, 'beside.html'); draw({ section: 'mk', form: 'bleed', side: 'right', cols: 6, edge: 'hard' }, [30, 28, 26], [1600, 1100], false, beside);
  assert.equal(of(measure(beside), 'desktop', 'mk').contrast, null, 'words beside a hard edge stand on the section, not on the picture');
  console.log('compose-picture-measure: ok', JSON.stringify({ soft: mk.contrast.ratio, deep: read.contrast.ratio, hero: hero.contrast.ratio, print: of(turned, 'desktop', 'mk').scale }));
} finally { fs.rmSync(dir, { recursive: true, force: true }); }
