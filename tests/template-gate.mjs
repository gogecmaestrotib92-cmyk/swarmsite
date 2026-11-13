// The template gate passes a sound page and names what is wrong with a page that may not be shown: it scrolls sideways,
// a line cannot be read on what is behind it, one line lies over another, a script fails, a picture is squeezed, two h1,
// the headline is not on the first screen at load, a line runs off the screen's edge.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { spawnSync } from 'node:child_process'; import { fileURLToPath } from 'node:url';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'); const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'tgate-'));
try {
  // a 2×1 picture, as a data address, so the page asks nobody for anything (two greys: a picture with something in it, not a bare ground)
  const PIC = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"><rect width="400" height="200" fill="#7a7a7a"/><rect x="200" width="200" height="200" fill="#626262"/></svg>');
  // a see-through picture: dark bars and nothing behind them
  const CLEAR = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="240">' + [0, 1, 2, 3, 4].map(i => '<rect x="' + (30 + i * 75) + '" y="40" width="36" height="160" fill="#0a0a0a"/>').join('') + '</svg>');
  const page = (body, css = '') => `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;font:18px/1.5 Arial,sans-serif;background:#fff;color:#111}section{padding:40px 24px;max-width:900px}h1{font:700 44px/1.1 Arial,sans-serif;margin:0 0 16px}img{display:block;max-width:100%;height:auto}${css}</style></head><body>${body}</body></html>`;
  const sound = '<section><h1>The books of a stall</h1><p>Photograph each receipt and the ledger keeps itself. Ten minutes on a Sunday closes the week.</p><img src="' + PIC + '" width="400" height="200" alt=""></section>';
  const pages = {
    sound: page(sound + '<section style="background:#111;color:#f5f5f5"><h2>On a dark band</h2><p>Light ink on a dark ground reads as well.</p><details><summary>Does it read handwriting?</summary><p style="color:#fff">A closed answer is not on screen.</p></details></section>'),
    sideways: page(sound + '<section><div style="display:flex;gap:20px;width:1700px"><div style="width:520px">Stall</div><div style="width:520px">Row</div><div style="width:520px">Market</div></div></section>'),
    unreadable: page(sound + '<section><p style="color:#f2f2f2">Pale grey words on a white ground cannot be read.</p><p style="color:#999;font-size:30px">Large pale words pass at three to one? Not these.</p></section>'),
    picture: page('<section style="position:relative;background:url(' + PIC + ') center/cover;min-height:300px"><h1 style="color:#8a8a8a">A grey heading on a grey picture</h1></section>'),
    overlap: page(sound + '<section style="position:relative;height:200px"><p style="position:absolute;top:40px;left:24px;margin:0">The first line of a paragraph that stands here.</p><p style="position:absolute;top:46px;left:30px;margin:0">Another line set on top of it by mistake.</p></section>'),
    covered: page(sound + '<section style="position:relative;height:220px"><p style="position:absolute;top:40px;left:24px;margin:0">A line that a card slides over.</p><div style="position:absolute;top:20px;left:0;right:0;background:#fff;padding:24px"><p style="margin:0">The card has its own ground: this is not one line over another.</p></div></section>'),
    // a heading only for screen readers (1px, clipped) that sits where visible text is: not on screen, so no overlap
    hidden: page(sound + '<section style="position:relative"><p style="margin:0">A quotation that stands where the hidden headings are.</p><h2 style="position:absolute;top:42px;left:24px;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;margin:0">The sea decides the day</h2><h2 style="position:absolute;top:42px;left:24px;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap;margin:0;color:#fafafa">A second one, clipped by path</h2></section>'),
    // a fixed bar that covers only a corner of a line at this scroll position: the line is judged where it is free, not against the bar
    corner: page('<div style="position:fixed;top:0;left:0;width:150px;height:30px;background:#111;z-index:5"></div><section style="padding-top:12px"><h1>The books of a stall</h1><p>Photograph each receipt and the ledger keeps itself. Ten minutes on a Sunday closes the week.</p></section>'),
    // a logo fitted with object-fit:contain keeps its own shape: not distorted
    contained: page(sound + '<section><img src="' + PIC + '" style="width:120px;height:120px;object-fit:contain" alt=""></section>'),
    // footer links that roll: each holds a visible label and a copy below it, cut away by overflow:hidden — the cut copy is not a line under the next link;
    // and a very wide, short picture at its own ratio but a fractional width is not distorted
    rolled: page(sound + '<footer style="padding:24px">' + ['Pricing', 'Changelog', 'Careers', 'Contact'].map(w => '<a href="#" style="display:block;overflow:hidden;height:22px;line-height:22px;color:#111;text-decoration:none"><span style="display:block">' + w + '</span><span aria-hidden="true" style="display:block">' + w + '</span></a>').join('') + '<img src="' + 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="480" height="131"><rect width="480" height="131" fill="#7a7a7a"/></svg>') + '" style="width:153.3px;height:auto" alt=""></footer>'),
    // a see-through diagram with dark ink on a dark ground, and a dark logo on a dark bar: what they show cannot be seen
    unseen: page(sound + '<section style="background:#000;color:#f5f5f5"><h2>How it works</h2><p>Four steps, drawn.</p><img src="' + CLEAR + '" width="400" height="240" alt="steps"></section>'),
    darklogo: page('<header style="background:#0b0b0d;padding:16px 24px"><img src="' + CLEAR + '" width="100" height="60" alt="mark"></header>' + sound),
    // the same diagram on a light ground, and on a dark ground under its own white plate: seen
    seen: page(sound + '<section><img src="' + CLEAR + '" width="400" height="240" alt="steps"></section><section style="background:#000;color:#f5f5f5"><h2>How it works</h2><p>Four steps, drawn.</p><img src="' + CLEAR + '" width="400" height="240" style="background:#fff" alt="steps"></section>'),
    script: page(sound + '<script>nothingOfTheKind()</script>'),
    squeezed: page(sound + '<section><img src="' + PIC + '" style="width:300px;height:300px;max-width:none" alt=""><img src="' + PIC + '" style="width:300px;height:300px;object-fit:cover" alt=""></section>'),
    twoh1: page(sound + '<section><h1>A second first heading</h1></section>'),
    // a screen of dark ground with the text in one narrow column and nothing beside it: the empty half a picture slot leaves
    blank: page(sound + '<section style="max-width:none;min-height:1800px;background:#0b0b0d;color:#f5f5f5"><h2>Three ways in</h2><p style="max-width:360px">One match, the whole slate, your own bet.</p><div style="height:1500px;margin-left:50%;background:radial-gradient(#0b0b0d,#0c0c0e)"></div></section><section style="max-width:none"><p>The end.</p></section>'),
    // the same column beside a picture that has something in it, and beside a drawn panel: not blank
    full: page(sound + '<section style="max-width:none;display:grid;grid-template-columns:1fr 2fr;gap:24px;background:#0b0b0d;color:#f5f5f5;min-height:900px"><div><h2>Three ways in</h2><p>One match, the whole slate, your own bet.</p></div><img src="' + 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="900">' + Array.from({ length: 30 }, (_, i) => '<rect x="0" y="' + i * 30 + '" width="600" height="15" fill="#' + (i % 2 ? '2af6a0' : '444444') + '"/>').join('') + '</svg>') + '" style="width:100%;height:900px;object-fit:cover" alt=""></section><section style="max-width:none"><p>The end.</p></section>'),
    // the first screen must show the headline at load: here it waits for a scroll (as a pinned opening that sets it letter by letter)
    late: page('<section style="min-height:100vh;background:#222"></section><section><h1 id="h" style="opacity:0">Set only once scrolled</h1><p>Photograph each receipt and the ledger keeps itself.</p></section><section style="min-height:100vh"></section>'
      + '<script>addEventListener("scroll",function(){document.getElementById("h").style.opacity=1})</script>'),
    // a headline set a span a letter, standing at load: read letter by letter, and it passes
    letters: page('<section><h1>' + 'The books of a stall'.split(' ').map(w => '<span style="display:inline-block;white-space:nowrap">' + [...w].map(c => '<span>' + c + '</span>').join('') + '</span>').join(' ') + '</h1><p>Photograph each receipt and the ledger keeps itself.</p></section>'),
    // a line the screen's left edge cuts, with nothing of the page clipping it
    cut: page(sound + '<section><p style="margin-left:-240px;white-space:nowrap">Once a day the price is checked against the books of the stall.</p></section>'),
    phone: page(sound + '<section><p style="min-width:560px">A block that is fine on a desk and too wide for a phone.</p></section>'),
    // what the reading must NOT fail: text on a path, a strip moved by script, the faded edges of a masked strip, a closed answer, a page that moves when it loads
    moving: page(sound
      + '<section><svg viewBox="0 0 600 160" width="600" height="160" style="max-width:100%;height:auto"><path id="arc" d="M20 140 Q300 -40 580 140" fill="none"/><text font-size="22" fill="#111"><textPath href="#arc">Words set along a curve are read letter by letter</textPath></text></svg></section>'
      + '<section style="overflow:hidden;padding:0"><div id="run" style="display:flex;gap:40px;white-space:nowrap;padding:20px 0;will-change:transform">' + '<span>Stalls keep their books here</span>'.repeat(12) + '</div></section>'
      + '<section style="overflow:hidden;padding:0;background:#111"><div style="display:flex;gap:40px;white-space:nowrap;padding:20px 0;color:#f5f5f5;-webkit-mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent);mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent)">' + '<span>No card to begin</span>'.repeat(14) + '</div></section>'
      + '<section><details><summary>Is the answer hidden?</summary><p style="color:#fdfdfd">Yes, until it is opened: white on white, and not on screen.</p></details></section>'
      + '<script>let x=0;const el=document.getElementById("run");(function go(){x-=1.2;el.style.transform="translateX("+(x%400)+"px)";requestAnimationFrame(go)})()</script>',
      'section{margin:0 auto}h1{animation:rise 1.1s cubic-bezier(.16,1,.3,1) both}@keyframes rise{from{opacity:0;transform:translateY(110px)}to{opacity:1;transform:none}}'),
  };
  const files = Object.entries(pages).map(([n, html]) => { const f = path.join(dir, n + '.html'); fs.writeFileSync(f, html); return f; });
  const r = spawnSync('node', [path.join(root, 'lib/qa/template_gate.mjs'), ...files], { encoding: 'utf8', timeout: 175000 });
  assert.ok(r.status === 1, 'one page fails → exit 1; got ' + r.status + ' ' + (r.stderr || '').slice(0, 300));
  if (process.env.GATE_DEBUG) console.log(r.stdout);
  const out = Object.fromEntries(r.stdout.trim().split('\n').map(l => JSON.parse(l)).map(x => [path.basename(x.page, '.html'), x]));
  assert.deepEqual(Object.keys(out).sort(), Object.keys(pages).sort(), 'one line of JSON for each page');

  assert.ok(out.sound.ok && out.sound.failed.length === 0 && out.sound.line_readings > 6, 'a sound page passes, and its lines were read: ' + JSON.stringify(out.sound.checks));
  assert.deepEqual(out.sound.widths, ['1440x900', '390x844', '1920x1080', '1024x768', '768x1024'], 'legible at 1440 and 390; every other check at 1920, 1024 and 768 too');
  assert.ok(out.sound.timing.d.screens >= 1 && out.sound.timing.m.screens >= 1 && out.sound.ms < 30000, 'a still page (five widths, three pages side by side) is not kept waiting: ' + out.sound.ms + ' ms');
  assert.deepEqual(r.stdout.trim().split('\n').map(l => path.basename(JSON.parse(l).page, '.html')), Object.keys(pages), 'pages are gated side by side and answered in the order given');
  assert.ok(out.moving.ok, 'text on a path, a strip moved by script, the faded edge of a masked strip, a closed answer and a heading that rises on load are read without a false FAIL: ' + JSON.stringify(out.moving.checks));
  assert.ok(out.moving.line_readings > out.sound.line_readings, 'and they were read, not skipped');
  assert.ok(!JSON.stringify(out.sound).includes('closed answer'), 'a closed answer is not judged');

  assert.deepEqual(out.sideways.failed.filter(k => k !== 'cut'), ['sideways']);
  assert.ok(out.sideways.checks.sideways.some(s => s.at === 'd' && s.px > 200 && s.page_width > 1700) && out.sideways.checks.sideways.some(s => s.at === 'm'), 'it says where and by how much');
  assert.deepEqual(out.phone.failed.filter(k => k !== 'cut'), ['sideways']); assert.deepEqual(out.phone.checks.sideways.map(s => s.at), ['m'], 'wide only on the phone: named for the phone alone');

  assert.deepEqual(out.unreadable.failed, ['legible']);
  const txt = out.unreadable.checks.legible.map(l => l.text.slice(0, 10));
  assert.ok(txt.includes('Pale grey ') && txt.includes('Large pale') && out.unreadable.checks.legible.every(l => l.ratio < 4.5), 'both pale lines are named with their contrast; large text has its own limit and these fail it too');
  assert.ok(!txt.includes('Photograph'), 'the lines that read are not named');
  assert.deepEqual(out.picture.failed, ['legible', 'first'], 'ink is judged against the pixels behind it, a picture included — and that headline does not read on the first screen');
  assert.deepEqual(out.late.failed.filter(k => k !== 'blank'), ['first'],   // (its bare screens are blank too)
    'a headline that waits for a scroll fails the first screen: ' + JSON.stringify(out.late.checks));
  assert.deepEqual(out.late.checks.first.map(f => f.at).sort(), ['d', 'm', 't1024', 't768', 'w1920'], 'at every width');
  assert.ok(out.letters.ok && out.letters.line_readings >= 6, 'a headline set a span a letter is read letter by letter and passes: ' + JSON.stringify(out.letters.checks));
  assert.deepEqual(out.cut.failed, ['cut']); assert.ok(out.cut.checks.cut.some(c => c.at === 'd' && c.left < 0 && /Once a day/.test(c.text)), 'the line the edge cuts is named, with where it starts');

  assert.deepEqual(out.overlap.failed.filter(k => k !== 'legible'), ['overlap']);
  assert.ok(out.overlap.checks.overlap.some(o => /first line/.test(o.under) && /Another line/.test(o.upon)), 'which line lies under which');
  assert.ok(out.corner.ok, 'a line whose corner is under a fixed bar is not scored against the bar: ' + JSON.stringify(out.corner.checks));
  assert.ok(out.contained.ok, 'a picture fitted with object-fit:contain is not distorted: ' + JSON.stringify(out.contained.checks));
  assert.ok(out.rolled.ok, 'text cut away by an overflow ancestor is not on screen; a wide picture at its own ratio is not distorted: ' + JSON.stringify(out.rolled.checks));
  assert.ok(out.hidden.ok, 'a screen-reader-only heading (clip rect or clip-path inset) is not read as a line on screen: ' + JSON.stringify(out.hidden.checks));
  assert.ok(out.covered.ok, 'a card with its own ground over a line is not an overlap: ' + JSON.stringify(out.covered.checks));

  assert.deepEqual(out.script.failed, ['errors']); assert.ok(/nothingOfTheKind/.test(out.script.checks.errors[0].text));
  assert.deepEqual(out.squeezed.failed.filter(k => k !== 'blank'), ['distorted']);   // (two small pictures stacked in a wide column leave its side empty: blank too)
  assert.equal(out.squeezed.checks.distorted.filter(d => d.at === 'd').length, 1, 'a squeezed picture is named once; a cropped one (cover) is not');
  assert.deepEqual(out.twoh1.failed, ['h1']); assert.equal(out.twoh1.checks.h1[0].count, 2);
  assert.ok(out.unseen.failed.includes('unseen') && out.unseen.checks.unseen.some(u => u.alt === 'steps' && u.shows < 14 && u.holds >= 24), 'dark ink of a see-through picture on a dark ground is not seen: ' + JSON.stringify(out.unseen.checks));
  assert.ok(out.darklogo.failed.includes('unseen') && out.darklogo.checks.unseen.some(u => u.alt === 'mark'), 'a dark logo on a dark bar is not seen: ' + JSON.stringify(out.darklogo.checks));
  assert.ok(!out.seen.failed.includes('unseen'), 'the same picture on a light ground or on its own plate is seen: ' + JSON.stringify(out.seen.checks.unseen));
  assert.ok(!out.sound.failed.includes('unseen') && !out.contained.failed.includes('unseen'), 'a picture that fills its place is seen');
  assert.deepEqual(out.blank.failed, ['blank'], 'a screen of bare ground beside one column of text is blank: ' + JSON.stringify(out.blank.checks));
  assert.ok(out.blank.checks.blank.some(b => b.at === 'd' && b.share >= .35 && b.w >= 500), 'it says where the empty region is and how much of the screen it takes');
  assert.ok(out.full.ok, 'the same column beside a picture is not blank: ' + JSON.stringify(out.full.checks));
  const { largestEmpty } = await import(path.join(root, 'lib/qa/template_gate.mjs'));
  assert.deepEqual(largestEmpty([[0, 1, 1, 0], [0, 1, 1, 1], [1, 1, 1, 1]].map(r => r.map(Boolean))), { a: 6, x: 1, y: 0, w: 2, h: 3 }, 'the largest empty rectangle of a grid');
  assert.equal(largestEmpty([[0, 0], [0, 0]].map(r => r.map(Boolean))).a, 0);

  // a page that is not there: the tool says so and does not call it shown
  const gone = spawnSync('node', [path.join(root, 'lib/qa/template_gate.mjs'), path.join(dir, 'nothing.html')], { encoding: 'utf8', timeout: 60000 });
  const g = JSON.parse(gone.stdout.trim().split('\n').pop());
  assert.ok(gone.status === 1 && g.ok === false, 'a missing page is not ok');
  assert.equal(spawnSync('node', [path.join(root, 'lib/qa/template_gate.mjs')], { encoding: 'utf8' }).status, 2, 'no page given: usage, exit 2');
  console.log('The template gate passes a sound page (and one that moves) and names sideways scroll, unreadable lines, overlap, script errors, squeezed pictures, a second h1, a headline missing from the first screen, a line the edge of the screen cuts and a screen left blank');
} finally { fs.rmSync(dir, { recursive: true, force: true }); }
