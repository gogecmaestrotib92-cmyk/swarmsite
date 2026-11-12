// The template gate passes a sound page and names what is wrong with a page that may not be shown: it scrolls sideways,
// a line cannot be read on what is behind it, one line lies over another, a script fails, a picture is squeezed, two h1.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { spawnSync } from 'node:child_process'; import { fileURLToPath } from 'node:url';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'); const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'tgate-'));
try {
  // a 2×1 picture, as a data address, so the page asks nobody for anything
  const PIC = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"><rect width="400" height="200" fill="#7a7a7a"/></svg>');
  const page = (body, css = '') => `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;font:18px/1.5 Arial,sans-serif;background:#fff;color:#111}section{padding:40px 24px;max-width:900px}h1{font:700 44px/1.1 Arial,sans-serif;margin:0 0 16px}img{display:block;max-width:100%;height:auto}${css}</style></head><body>${body}</body></html>`;
  const sound = '<section><h1>The books of a stall</h1><p>Photograph each receipt and the ledger keeps itself. Ten minutes on a Sunday closes the week.</p><img src="' + PIC + '" width="400" height="200" alt=""></section>';
  const pages = {
    sound: page(sound + '<section style="background:#111;color:#f5f5f5"><h2>On a dark band</h2><p>Light ink on a dark ground reads as well.</p><details><summary>Does it read handwriting?</summary><p style="color:#fff">A closed answer is not on screen.</p></details></section>'),
    sideways: page(sound + '<section><div style="display:flex;gap:20px;width:1700px"><div style="width:520px">Stall</div><div style="width:520px">Row</div><div style="width:520px">Market</div></div></section>'),
    unreadable: page(sound + '<section><p style="color:#f2f2f2">Pale grey words on a white ground cannot be read.</p><p style="color:#999;font-size:30px">Large pale words pass at three to one? Not these.</p></section>'),
    picture: page('<section style="position:relative;background:url(' + PIC + ') center/cover;min-height:300px"><h1 style="color:#8a8a8a">A grey heading on a grey picture</h1></section>'),
    overlap: page(sound + '<section style="position:relative;height:200px"><p style="position:absolute;top:40px;left:24px;margin:0">The first line of a paragraph that stands here.</p><p style="position:absolute;top:46px;left:30px;margin:0">Another line set on top of it by mistake.</p></section>'),
    covered: page(sound + '<section style="position:relative;height:220px"><p style="position:absolute;top:40px;left:24px;margin:0">A line that a card slides over.</p><div style="position:absolute;top:20px;left:0;right:0;background:#fff;padding:24px"><p style="margin:0">The card has its own ground: this is not one line over another.</p></div></section>'),
    script: page(sound + '<script>nothingOfTheKind()</script>'),
    squeezed: page(sound + '<section><img src="' + PIC + '" style="width:300px;height:300px;max-width:none" alt=""><img src="' + PIC + '" style="width:300px;height:300px;object-fit:cover" alt=""></section>'),
    twoh1: page(sound + '<section><h1>A second first heading</h1></section>'),
    phone: page(sound + '<section><p style="min-width:560px">A block that is fine on a desk and too wide for a phone.</p></section>'),
  };
  const files = Object.entries(pages).map(([n, html]) => { const f = path.join(dir, n + '.html'); fs.writeFileSync(f, html); return f; });
  const r = spawnSync('node', [path.join(root, 'lib/qa/template_gate.mjs'), ...files, '--settle', '400', '--pause', '150'], { encoding: 'utf8', timeout: 170000 });
  assert.ok(r.status === 1, 'one page fails → exit 1; got ' + r.status + ' ' + (r.stderr || '').slice(0, 300));
  if (process.env.GATE_DEBUG) console.log(r.stdout);
  const out = Object.fromEntries(r.stdout.trim().split('\n').map(l => JSON.parse(l)).map(x => [path.basename(x.page, '.html'), x]));
  assert.deepEqual(Object.keys(out).sort(), Object.keys(pages).sort(), 'one line of JSON for each page');

  assert.ok(out.sound.ok && out.sound.failed.length === 0 && out.sound.line_readings > 6, 'a sound page passes, and its lines were read: ' + JSON.stringify(out.sound.checks));
  assert.deepEqual(out.sound.widths, ['1440x900', '390x844']);
  assert.ok(!JSON.stringify(out.sound).includes('closed answer'), 'a closed answer is not judged');

  assert.deepEqual(out.sideways.failed, ['sideways']);
  assert.ok(out.sideways.checks.sideways.some(s => s.at === 'd' && s.px > 200 && s.page_width > 1700) && out.sideways.checks.sideways.some(s => s.at === 'm'), 'it says where and by how much');
  assert.deepEqual(out.phone.failed, ['sideways']); assert.deepEqual(out.phone.checks.sideways.map(s => s.at), ['m'], 'wide only on the phone: named for the phone alone');

  assert.deepEqual(out.unreadable.failed, ['legible']);
  const txt = out.unreadable.checks.legible.map(l => l.text.slice(0, 10));
  assert.ok(txt.includes('Pale grey ') && txt.includes('Large pale') && out.unreadable.checks.legible.every(l => l.ratio < 4.5), 'both pale lines are named with their contrast; large text has its own limit and these fail it too');
  assert.ok(!txt.includes('Photograph'), 'the lines that read are not named');
  assert.deepEqual(out.picture.failed, ['legible'], 'ink is judged against the pixels behind it, a picture included');

  assert.deepEqual(out.overlap.failed.filter(k => k !== 'legible'), ['overlap']);
  assert.ok(out.overlap.checks.overlap.some(o => /first line/.test(o.under) && /Another line/.test(o.upon)), 'which line lies under which');
  assert.ok(out.covered.ok, 'a card with its own ground over a line is not an overlap: ' + JSON.stringify(out.covered.checks));

  assert.deepEqual(out.script.failed, ['errors']); assert.ok(/nothingOfTheKind/.test(out.script.checks.errors[0].text));
  assert.deepEqual(out.squeezed.failed, ['distorted']); assert.equal(out.squeezed.checks.distorted.filter(d => d.at === 'd').length, 1, 'a squeezed picture is named once; a cropped one (cover) is not');
  assert.deepEqual(out.twoh1.failed, ['h1']); assert.equal(out.twoh1.checks.h1[0].count, 2);

  // a page that is not there: the tool says so and does not call it shown
  const gone = spawnSync('node', [path.join(root, 'lib/qa/template_gate.mjs'), path.join(dir, 'nothing.html')], { encoding: 'utf8', timeout: 60000 });
  const g = JSON.parse(gone.stdout.trim().split('\n').pop());
  assert.ok(gone.status === 1 && g.ok === false, 'a missing page is not ok');
  assert.equal(spawnSync('node', [path.join(root, 'lib/qa/template_gate.mjs')], { encoding: 'utf8' }).status, 2, 'no page given: usage, exit 2');
  console.log('The template gate passes a sound page and names sideways scroll, unreadable lines, overlap, script errors, squeezed pictures and a second h1');
} finally { fs.rmSync(dir, { recursive: true, force: true }); }
