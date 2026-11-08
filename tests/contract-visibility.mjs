import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-visibility-'));
try {
  for (const [name, style, expectEmpty] of [
    ['hidden', '.content { opacity: 0 }', true],
    ['offscreen', '.content { position: relative; left: 200vw }', true],
    ['visible', '', false],
  ]) {
    const html = path.join(dir, `${name}.html`);
    fs.writeFileSync(html, `<!doctype html><style>body { margin: 0 } p { height: 3000px; margin: 0 } ${style}</style><button id="sw-skip">skip</button><div class="content"><p>Page content</p></div>`);
    const result = spawnSync(process.execPath, ['lib/qa/contract.mjs', html, '--dir', dir], {
      encoding: 'utf8',
      env: { ...process.env, LIVETEST: '1' },
      timeout: 120000,
    });
    assert.equal(result.status, 0, result.stderr || result.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    for (const viewport of ['desktop', 'mobile']) {
      assert.equal(report.failed.some(item => item.id === `${viewport}-no-empty-screens`), expectEmpty, `${name} at ${viewport}`);
    }
  }
  console.log('Contract visibility checks passed');
} finally {
  fs.rmSync(dir, { recursive: true, force: true });
}
