// Every page answers a hand the same way (lib/templates/feel.py, owner 2026-11-23): a surface gives under a press and
// springs back, a bare link dims, an anchor lands below a bar that stays, and a blurred bar turns solid when the system
// asks for less transparency. Read in a real browser on a page made for it, then on a few templates for errors.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-feel-'));
const py = (code, ...args) => execFileSync('python3', ['-c', code, ...args], { cwd: root, encoding: 'utf8', maxBuffer: 1 << 26 });
const ADD = `import importlib.util,sys
s=importlib.util.spec_from_file_location('feel','lib/templates/feel.py');F=importlib.util.module_from_spec(s);s.loader.exec_module(F)
sys.stdout.write(F.add(sys.stdin.read()))`;
const add = page => execFileSync('python3', ['-c', ADD], { cwd: root, input: page, encoding: 'utf8' });

const made = add(`<!doctype html><html><head><meta charset="utf-8"><title>Feel</title><style>
body{margin:0;font:16px/1.5 sans-serif;background:#f4f2ec}
.bar{position:sticky;top:0;height:72px;display:flex;gap:24px;align-items:center;padding:0 24px;background:rgba(255,255,255,.6);backdrop-filter:blur(12px)}
.btn{display:inline-block;padding:14px 24px;background:#1b1530;color:#fff;border-radius:99px;text-decoration:none}
section{height:1400px;padding:24px}</style></head><body>
<nav class="bar"><a id="bare" href="#two">Two</a><a id="btn" class="btn" href="#two">Start</a></nav>
<section id="one"><p>One</p></section><section id="two"><h2>Two</h2></section></body></html>`);
fs.writeFileSync(path.join(dir, 'made.html'), made);
assert.equal(add(made), made, 'a page that has the layer is left as it is');

const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
try {
  const ctx = await b.newContext({ viewport: { width: 1200, height: 800 } }); const p = await ctx.newPage(); const errors = [];
  p.on('pageerror', e => errors.push(String(e)));
  await p.goto('file://' + path.join(dir, 'made.html')); await p.waitForTimeout(300);
  const at = async sel => { const r = await p.locator(sel).boundingBox(); return [r.x + r.width / 2, r.y + r.height / 2]; };
  await p.evaluate(() => addEventListener('click', e => { if (e.target.closest('[data-hold]')) e.preventDefault(); }, true));
  await p.evaluate(() => { document.getElementById('btn').setAttribute('data-hold', ''); document.getElementById('bare').setAttribute('data-hold', ''); });
  // a press: the button gives (6 px of its longer side at most, so .97 for a button), then springs back and leaves nothing behind
  let [x, y] = await at('#btn'); await p.mouse.move(x, y); await p.mouse.down(); await p.waitForTimeout(200);
  const held = +(await p.evaluate(() => getComputedStyle(document.getElementById('btn')).scale));
  assert.ok(held >= .969 && held < 1, `the button gives under a press (${held})`);
  await p.mouse.up(); await p.waitForTimeout(700);
  assert.equal(await p.evaluate(() => getComputedStyle(document.getElementById('btn')).scale + '/' + document.getElementById('btn').getAnimations().length), 'none/0', 'and springs back, nothing left running');
  // a bare word that is a link dims while held, and comes back
  [x, y] = await at('#bare'); await p.mouse.move(x, y); await p.mouse.down(); await p.waitForTimeout(150);
  assert.equal(await p.evaluate(() => getComputedStyle(document.getElementById('bare')).opacity), '0.55', 'a bare link dims');
  await p.mouse.up(); await p.waitForTimeout(500);
  assert.equal(await p.evaluate(() => getComputedStyle(document.getElementById('bare')).opacity), '1');
  // an anchor lands below the bar that stays at the top, not under it
  await p.evaluate(() => { document.getElementById('btn').removeAttribute('data-hold'); });
  [x, y] = await at('#btn'); await p.mouse.click(x, y); await p.waitForTimeout(600);
  const top = await p.evaluate(() => document.querySelector('#two h2').getBoundingClientRect().top);
  assert.ok(top >= 72, `the heading lands below the 72 px bar (${top})`);
  // asked for less transparency, the blurred bar is solid in its own colour
  const cdp = await ctx.newCDPSession(p); await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-transparency', value: 'reduce' }] });
  await p.reload(); await p.waitForTimeout(300);
  assert.deepEqual(await p.evaluate(() => { const s = getComputedStyle(document.querySelector('.bar')); return [s.backdropFilter, s.backgroundColor]; }), ['none', 'rgb(255, 255, 255)'], 'the bar turns solid');
  await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-transparency', value: 'no-preference' }] });
  await p.reload(); await p.waitForTimeout(300);
  assert.equal(await p.evaluate(() => getComputedStyle(document.querySelector('.bar')).backdropFilter), 'blur(12px)', 'and is left as drawn otherwise');
  assert.deepEqual(errors, []);
  await ctx.close();

  // a few templates of the library, each with a fixture client: the layer is there and throws nothing
  const pages = JSON.parse(py(`import importlib.util,json,sys
s=importlib.util.spec_from_file_location('reg','lib/templates/registry.py');R=importlib.util.module_from_spec(s);s.loader.exec_module(R)
d=json.load(open('tests/fixtures/templates/pagewright.json'));out={}
for slug in ['griffin','serus','writer','linearity','whitedesert','maze']:
  out[slug]=R.render(slug,d)
print(json.dumps(out))`));
  for (const [slug, page] of Object.entries(pages)) {
    assert.ok(page.includes('<script data-sw-feel>'), slug);
    fs.writeFileSync(path.join(dir, slug + '.html'), page);
    const q = await b.newPage({ viewport: { width: 1440, height: 900 } }); const errs = []; q.on('pageerror', e => errs.push(String(e)));
    await q.route(/^https?:/, r => r.abort()); await q.goto('file://' + path.join(dir, slug + '.html')); await q.waitForTimeout(600);
    await q.mouse.move(720, 450); await q.mouse.down(); await q.waitForTimeout(80); await q.mouse.up();
    assert.deepEqual(errs, [], slug); await q.close();
  }
} finally { await b.close(); fs.rmSync(dir, { recursive: true, force: true }); }
console.log('feel: a press gives and springs back, a bare link dims, an anchor lands below the bar, a blurred bar turns solid when asked; six templates carry it without an error');
