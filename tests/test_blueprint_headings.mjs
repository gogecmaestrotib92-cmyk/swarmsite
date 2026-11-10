import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

// Isolate the measurements so the test exercises the semantic distinction:
// a captured label/body measurement must not become the generated H2, while
// a deliberately smaller heading above body scale remains blueprint-specific.
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-headings-'));
const lib = path.join(tmp, 'lib');
fs.cpSync('lib', lib, { recursive: true });
const fixture = path.join(tmp, 'fixture'); fs.mkdirSync(fixture);
const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
direction.beats = ['first', 'second'].map(id => ({ id, type: 'features', h2: `Heading ${id}`, features: [{ title: 'Feature', body: 'Description' }], ui: { move: 'cards' } }));
for (const [name, data] of [['direction.json', direction], ['inventory.json', {}], ['images.json', []]]) fs.writeFileSync(path.join(fixture, name), JSON.stringify(data));
const names = fs.readdirSync(path.join(lib, 'blueprints')).filter(n => n.endsWith('.bp.json'));
let browser;
try {
  browser = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const name of names) {
    const bpPath = path.join(lib, 'blueprints', name), bp = JSON.parse(fs.readFileSync(bpPath));
    const h2 = (bp.type.h2 || bp.type.display || {}).px || 48;
    const body = (bp.type.body || {}).px || 17, label = (bp.type.label || {}).px || 12;
    const bodyScale = Math.max(body, label);
    if (!(bodyScale < h2 * .75)) continue;
    const smaller = Math.min(96, Math.max(bodyScale + 2, Math.round(h2 * .8)));
    bp.sections = [bp.sections[0], { role: 'cards', head: { px: bodyScale, lh: 1.5, ls: .2, tt: 'uppercase', it: true } }, { role: 'cards', head: { px: smaller, lh: 1.1, tt: 'uppercase', it: true } }, bp.sections.at(-1)];
    fs.writeFileSync(bpPath, JSON.stringify(bp));
    const output = path.join(fixture, 'out.html');
    const result = spawnSync(process.env.PYTHON || 'python3', [path.join(lib, 'render/render_bp.py'), fixture, name.replace('.bp.json', ''), output], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    for (const width of [390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
      await page.goto(pathToFileURL(output).href + '?nomotion=1');
      const sizes = await page.locator('#first h2, #second h2').evaluateAll(els => els.map(el => parseFloat(getComputedStyle(el).fontSize)));
      const floor = width <= 600 ? 32 : 28;   // on a phone a section heading does not fall under 32 px (it outranks 18 px running text)
      const sizeAt = px => Math.max(floor, Math.max(Math.max(28, Math.floor(px * .45)), Math.min(px, Math.round(px / 14.4 * 100) / 100 * width / 100)));
      assert.equal(sizes.length, 2, `${name} headings`);
      assert.ok(Math.abs(sizes[0] - sizeAt(Math.min(h2, 96))) < .2, `${name} body-scale heading at ${width}: ${sizes[0]}`);
      assert.ok(Math.abs(sizes[1] - sizeAt(smaller)) < .2, `${name} intentional heading at ${width}: ${sizes[1]}`);
      const styles = await page.locator('#first h2, #second h2').evaluateAll(els => els.map(el => { const s = getComputedStyle(el); return { transform: s.textTransform, italic: s.fontStyle, weight: s.fontWeight }; }));
      const h2Type = bp.type.h2 || bp.type.display || {};
      assert.equal(styles[0].transform, h2Type.tt === 'uppercase' ? 'uppercase' : 'none', `${name} body measurement must not transfer uppercase`);
      assert.equal(styles[0].italic, h2Type.it ? 'italic' : 'normal', `${name} body measurement must not transfer italic`);
      assert.equal(styles[0].weight, String(h2Type.w || 400), `${name} H2 keeps blueprint weight`);
      assert.equal(styles[1].transform, 'uppercase', `${name} intentional heading keeps uppercase`);
      assert.equal(styles[1].italic, 'italic', `${name} intentional heading keeps italic`);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width, `${name} overflow at ${width}`);
      await page.close();
    }
  }
  console.log('Blueprint H2 hierarchy retains intentional size differences on desktop and mobile');
} finally {
  if (browser) await browser.close();
  fs.rmSync(tmp, { recursive: true, force: true });
}
