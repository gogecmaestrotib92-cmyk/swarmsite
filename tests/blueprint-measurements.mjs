import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-blueprint-measurements-'));
const extractor = fs.readFileSync('lib/blueprint/extract.js', 'utf8');
let browser;
try {
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [390, 1024, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 600 }, reducedMotion: 'reduce' });
    await page.setContent(`<!doctype html><style>body{margin:0}section{height:1600px}h1{margin:0 0 0 20vw}#lazy{height:0}</style>
      <section><h1>Reference headline</h1><p>Visible content to measure.</p></section><section id="lazy"><h2>Lazy section</h2></section>
      <script>window.addEventListener('scroll',()=>{if(scrollY>100)document.querySelector('#lazy').style.height='1200px'},{once:true})</script>`);
    const initial = await page.evaluate(() => document.documentElement.scrollHeight);
    await page.evaluate(extractor);
    const text = await page.locator('#bpout pre').textContent();
    const raw = JSON.parse(text.replace(/^BPSTART/, '').replace(/BPEND$/, ''));
    // The output article itself is added after measurement; exclude it from
    // the independent final-height comparison.
    const actual = await page.evaluate(() => { document.getElementById('bpout').remove(); return document.documentElement.scrollHeight; });
    assert.equal(raw.vw, width);
    assert.ok(actual > initial, 'the fixture must grow during the scroll pass');
    assert.equal(raw.pageH, actual, `final page height at ${width}px`);
    const input = path.join(dir, `raw-${width}.json`);
    fs.writeFileSync(input, JSON.stringify(raw));
    const code = `import importlib.util,json\ns=importlib.util.spec_from_file_location('norm',${JSON.stringify(path.resolve('lib/blueprint/normalize.py'))});m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=${JSON.stringify(dir)};x=m.normalize(${JSON.stringify(input)});print(json.dumps(x['sections'][0]['head']))`;
    const result = spawnSync(process.env.PYTHON || 'python3', ['-c', code], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(JSON.parse(result.stdout).x, .2, `normalized heading x at ${width}px`);
    await page.close();
  }
  console.log('Blueprint viewport and post-scroll page height measured at three widths');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
