import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-empty-sections-'));
try {
  const numbers = '<div class="nums"><div><b class="num">2012</b><p>years serving</p></div><div><b class="num">30</b><p>guests</p></div></div>';
  const cards = '<div class="grid"><div class="card"><h3>2012</h3><p>years serving</p></div><div class="card"><h3>30</h3><p>guests</p></div></div>';
  const cases = [
    ['numbers', `<section class="sec numbers">${numbers}</section>`, false],
    ['hidden-numbers', `<section class="sec numbers" style="visibility:hidden">${numbers}</section>`, true],
    ['incomplete-numbers', '<section class="sec numbers"><div class="nums"><div><b class="num">2012</b></div></div></section>', true],
    ['cards', `<section class="sec cards">${cards}</section>`, false],
    ['hidden-cards', `<section class="sec cards" style="visibility:hidden">${cards}</section>`, true],
    ['cta', '<section class="sec cta"><h2>Reserve a table</h2><a class="btn" href="https://example.test/reserve">Reserve</a></section>', false],
    ['mostly-visible-cta', '<section class="sec cta" style="position:relative;top:150px"><h2>Reserve a table</h2><a class="btn" href="https://example.test/reserve">Reserve</a></section>', false],
    ['barely-visible-cta', '<section class="sec cta" style="position:relative;top:-500px;justify-content:flex-end"><h2>Reserve a table</h2><a class="btn" href="https://example.test/reserve">Reserve</a></section>', true],
    ['broken-cta', '<section class="sec cta"><h2>Reserve a table</h2><a class="btn" href="#missing">Reserve</a></section>', true],
    ['hidden-cta', '<section class="sec cta"><h2>Reserve a table</h2><a class="btn" href="https://example.test/reserve" style="display:none">Reserve</a></section>', true],
    ['obscured-cta', '<section class="sec cta"><h2>Reserve a table</h2><a class="btn" href="https://example.test/reserve">Reserve</a></section><div class="overlay"></div>', true],
    ['oversized-cta', '<section class="sec cta" style="height:250vh"><h2>Reserve a table</h2><a class="btn" href="https://example.test/reserve">Reserve</a></section>', true],
    ['blank', '<section class="sec"></section>', true],
  ];
  for (const [name, body, expectEmpty] of cases) {
    const html = path.join(dir, `${name}.html`);
    fs.writeFileSync(html, `<!doctype html><style>html,body{margin:0;height:100%} body{display:flex;align-items:center;justify-content:center}.sec{height:650px;width:100%;display:flex;align-items:center;justify-content:center;flex-direction:column}.nums,.grid{display:flex;gap:40px}.num{font-size:96px}.nums p,.card p{margin:0}.cta h2{font-size:40px}.btn{display:inline-block;padding:10px}.overlay{position:fixed;inset:0;z-index:10}</style>${body}`);
    const result = spawnSync(process.execPath, ['lib/qa/contract.mjs', html, '--dir', dir], {
      encoding: 'utf8', env: { ...process.env, LIVETEST: '1' }, timeout: 120000,
    });
    assert.equal(result.status, 0, result.stderr || result.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    for (const viewport of ['desktop', 'mobile']) {
      assert.equal(report.failed.some(item => item.id === `${viewport}-no-empty-screens`), expectEmpty, `${name} at ${viewport}`);
    }
  }
  console.log('Contract distinguishes visible compact sections from empty or broken screens');
} finally {
  fs.rmSync(dir, { recursive: true, force: true });
}
