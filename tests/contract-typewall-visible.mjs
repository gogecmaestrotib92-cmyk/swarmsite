import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-typewall-'));
try {
  const cases = [
    ['visible', '', '<h2 class="tw">Bright idea</h2><p class="tw-caption">Details here</p>', false],
    ['hidden', 'visibility:hidden', '<h2 class="tw">Bright idea</h2><p class="tw-caption">Details here</p>', true],
    ['missing', '', '<p class="tw-caption">Details here</p>', true],
    ['hidden-caption', '', '<h2 class="tw">Bright idea</h2><p class="tw-caption" style="visibility:hidden">Details here</p>', true],
    ['covered', '', '<h2 class="tw">Bright idea</h2><p class="tw-caption">Details here</p><div style="position:fixed;inset:0;z-index:10"></div>', true],
    ['oversized', 'height:150vh', '<h2 class="tw">Bright idea</h2><p class="tw-caption">Details here</p>', true],
  ];
  for (const [name, style, content, expectEmpty] of cases) {
    const html = path.join(dir, `${name}.html`);
    fs.writeFileSync(html, `<!doctype html><style>html,body{margin:0}.typewall{height:150vh}.tw-sticky{position:sticky;top:0;height:100vh;display:flex;align-items:center;justify-content:center;flex-direction:column}.tw{font-size:40px}.tw-caption{font-size:18px}</style><section class="sec typewall"><div class="tw-sticky" style="${style}">${content}</div></section>`);
    const result = spawnSync(process.execPath, ['lib/qa/contract.mjs', html, '--dir', dir], {
      encoding: 'utf8', env: { ...process.env, LIVETEST: '1' }, timeout: 120000,
    });
    assert.equal(result.status, 0, result.stderr || result.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    for (const viewport of ['desktop', 'mobile']) {
      assert.equal(report.failed.some(item => item.id === `${viewport}-no-empty-screens`), expectEmpty, `${name} at ${viewport}`);
    }
  }
  console.log('Contract distinguishes a visible type-wall from missing or hidden content');
} finally {
  fs.rmSync(dir, { recursive: true, force: true });
}
