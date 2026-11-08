import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-actions-'));
try {
  for (const [name, action, expected] of [
    ['missing', '', false],
    ['broken', '<a class="btn" href="#missing">Reserve</a>', false],
    ['internal', '<a class="btn" href="#contact">Reserve</a><div id="contact">Contact</div>', true],
    ['external', '<a class="btn" href="https://example.test/reserve">Reserve</a>', true],
  ]) {
    const html = path.join(dir, `${name}.html`);
    fs.writeFileSync(html, `<!doctype html><button id="sw-skip">skip</button>${action}`);
    const result = spawnSync(process.execPath, ['lib/qa/contract.mjs', html, '--dir', dir], {
      encoding: 'utf8', env: { ...process.env, LIVETEST: '1' }, timeout: 120000,
    });
    assert.equal(result.status, 0, result.stderr || result.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    for (const viewport of ['desktop', 'mobile']) {
      assert.equal(report.failed.some(item => item.id === `${viewport}-actionable-cta`), !expected, `${name} at ${viewport}`);
    }
  }
  console.log('Contract action checks passed');
} finally {
  fs.rmSync(dir, { recursive: true, force: true });
}
