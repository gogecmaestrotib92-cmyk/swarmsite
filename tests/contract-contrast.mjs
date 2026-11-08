import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-contrast-'));
try {
  const cases = [
    { name: 'srgb-light', background: 'color(srgb 0.9 0.869804 0.817725)', foreground: '#120f0d', fails: false },
    { name: 'mixed-dark', background: 'color-mix(in srgb, #050505 90%, red)', foreground: '#191919', fails: true },
    { name: 'transparent-on-light', background: 'color-mix(in srgb, transparent 50%, white)', foreground: '#120f0d', fails: false },
    { name: 'translucent-text', background: 'white', foreground: 'rgba(0,0,0,.15)', fails: true },
    { name: 'white-on-dark', background: '#191919', foreground: 'white', fails: false },
  ];
  for (const test of cases) {
    const html = path.join(dir, `${test.name}.html`);
    fs.writeFileSync(html, `<!doctype html><html><body style="background:white"><section class="sec" style="background:${test.background};color:${test.foreground};min-height:100vh"><p>Actual page text that needs to be read clearly</p><ul><li>Business detail</li></ul></section></body></html>`);
    const result = spawnSync(process.execPath, ['lib/qa/contract.mjs', html, '--dir', dir], {
      encoding: 'utf8', env: { ...process.env, LIVETEST: '1' }, timeout: 120000,
    });
    assert.equal(result.status, 0, result.stderr || result.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    for (const viewport of ['desktop', 'mobile']) {
      assert.equal(report.failed.some(item => item.id === `${viewport}-contrast`), test.fails, `${test.name} at ${viewport}`);
    }
  }
  console.log('Contract checks computed colors and transparency');
} finally {
  fs.rmSync(dir, { recursive: true, force: true });
}
