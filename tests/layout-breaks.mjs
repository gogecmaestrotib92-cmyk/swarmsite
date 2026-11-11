// The layout detector names broken typesetting on any page, at the widths where it shows, and passes a sound page.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { spawnSync } from 'node:child_process'; import { fileURLToPath } from 'node:url';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'); const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'layout-'));
const page = body => `<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;font:18px/1.4 Arial,sans-serif}h2{font:700 64px/1 Arial,sans-serif;margin:0}section{padding:40px}</style></head><body>${body}</body></html>`;
const run = (name, body, widths = '390,1440') => { const file = path.join(dir, name + '.html'); fs.writeFileSync(file, page(body));
  const r = spawnSync('node', [path.join(root, 'lib/qa/layout.mjs'), file, '--widths', widths], { encoding: 'utf8', env: { ...process.env, LIVETEST: '1' } });
  assert.equal(r.status, 0, r.stderr); return JSON.parse(r.stdout.trim().split('\n').pop()).breaks; };
const kinds = b => b.map(x => `${x.kind}@${x.section}`).sort();

let b = run('sound', '<section id="a"><h2>What could your book earn?</h2><p>Choose a book price and a monthly sales scenario. At eleven dollars and a hundred copies in one month, sales are a round number and your share is most of it.</p></section>', '768,1440');
assert.deepEqual(b, [], 'a sound page has no breaks');

b = run('stacked', '<section id="earn"><div style="width:230px"><h2>What could your book earn?</h2></div></section>', '1440');
assert.ok(kinds(b).includes('stacked-words@earn'), 'a heading a word to a line is named: ' + JSON.stringify(b));

b = run('split', '<section id="s"><div style="width:200px"><h2 style="overflow-wrap:anywhere">Basketball</h2></div></section>', '1440');
assert.ok(kinds(b).includes('split-word@s'), 'a word broken across lines is named');

b = run('thin', '<section id="t"><p style="width:110px">Choose a book price and a monthly sales scenario, then compare what each one would bring you over a month of ordinary sales.</p></section>', '1440');
assert.ok(kinds(b).includes('thin-column@t'), 'a paragraph in a sliver is named');

b = run('clipped', '<section id="c"><div style="width:300px;overflow:hidden"><h2 style="white-space:nowrap">A very long line indeed</h2></div></section>', '1440');
assert.ok(kinds(b).includes('clipped@c'), 'a heading cut off by its box is named');

b = run('off', '<section id="f"><figure style="width:200px;margin:0 0 0 250px"><figcaption style="display:flex;gap:16px"><b>Events</b><span style="white-space:nowrap">Celebrate with us here</span></figcaption></figure><div style="overflow-x:auto"><span style="white-space:nowrap;margin-left:500px">A strip the visitor scrolls sideways</span></div></section>', '390');
assert.deepEqual(kinds(b), ['clipped@f'], 'a label running off the screen is named, and a strip that scrolls sideways is not: ' + JSON.stringify(b));

b = run('overlap', '<section id="o"><h2>Create, publish</h2><p style="margin-top:-50px">Words that were pulled up under the heading by a negative margin and now lie across it.</p></section>', '1440');
assert.ok(kinds(b).includes('overlap@o'), 'a heading lying over text is named');

b = run('width', '<section id="w"><div style="width:min(100%,22vw)"><h2 style="font-size:40px">What could your book earn now?</h2></div></section>', '390,1440');
assert.deepEqual(b.find(x => x.kind === 'stacked-words')?.widths, [390], 'a break is reported with the widths it shows at');
b = run('dump', '<section id="d"><h2>Toolkit</h2><ul>' + Array.from({ length: 9 }, (_, i) => `<li><a href="https://x.test/${i}" style="text-decoration:underline">Explore page ${i}</a></li>`).join('') + '</ul></section>', '1440');
assert.ok(kinds(b).includes('link-dump@d'), 'a run of bare links standing in a section is named');
b = run('kept', '<section id="k"><h2>Toolkit</h2><details><summary>More in this section</summary><ul>' + Array.from({ length: 9 }, (_, i) => `<li><a href="https://x.test/${i}" style="text-decoration:underline">Explore page ${i}</a></li>`).join('') + '</ul></details></section>', '1440');
assert.deepEqual(b, [], 'the same links kept behind one row a reader opens are not a dump');
console.log('The layout detector names stacked, split, thin, clipped and overlapping text and passes a sound page');

// A name set across the end of the page is seen whole: cut below the line its letters stand on, it is named; standing on the edge, it is not.
const ending = (css, more = '') => `<section id="a" style="min-height:1400px"><h2>Above</h2><p>Enough words here to make a paragraph that is set at a readable measure on the page.</p></section><footer id="end" style="overflow:hidden;padding:0"><div style="font:700 300px/${css} Arial,sans-serif;white-space:nowrap;${more}">Name</div></footer>`;
b = run('cut-name', ending('.8', 'margin-bottom:-.3em'), '1440');
assert.ok(kinds(b).includes('cut-name@end'), 'a closing name cut through its letters is named: ' + JSON.stringify(b));
b = run('hidden-name', ending('1', 'opacity:0'), '1440');
assert.ok(kinds(b).includes('cut-name@end'), 'a closing name that never arrives is named');
b = run('whole-name', ending('1'), '1440');
assert.deepEqual(kinds(b), [], 'a closing name standing whole on the edge is sound: ' + JSON.stringify(b));

// A section of pictures is a composition of them: a tall picture beside a short one leaves a hole, and the hole is named; two that close the row are sound.
const pic = (w, h) => `<img alt="" width="${w}" height="${h}" style="display:block;width:${w}px;height:${h}px" src="data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><rect width="${w}" height="${h}" fill="#964"/></svg>`)}">`;
b = run('void', `<section id="work"><h2>Rooms</h2><div style="display:flex;gap:24px;align-items:flex-start">${pic(560, 900)}${pic(420, 280)}</div></section>`, '1440');
assert.deepEqual(kinds(b), ['void@work'], 'a hole beside a short picture is named: ' + JSON.stringify(b));
b = run('closed', `<section id="work"><h2>Rooms</h2><div style="display:flex;gap:24px">${pic(760, 480)}${pic(560, 480)}</div></section>`, '1440');
assert.deepEqual(kinds(b), [], 'two pictures that close their row are sound: ' + JSON.stringify(b));
