import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-runway-'));
try {
  for (const [name, panelStyle, panelContent, expectEmpty] of [
    ['visible-sticky', '', '<p>Visible sticky content</p>', false],
    ['hidden-sticky', 'visibility: hidden;', '<p>Hidden sticky content</p>', true],
    ['empty-sticky', '', '', true],
    ['empty-wrapper', '', '<figure style="height:100%"></figure><p></p>', true],
    ['offscreen-sticky', 'transform: translateX(200vw);', '<p>Offscreen sticky content</p>', true],
    ['not-sticky', 'position: relative;', '<p>Content scrolls away</p>', true],
  ]) {
    const html = path.join(dir, `${name}.html`);
    fs.writeFileSync(html, `<!doctype html><style>
      body { margin: 0 } section { height: 3000px }
      .ps-sticky { position: sticky; top: 0; height: 70vh; ${panelStyle} }
      p { height: 100%; margin: 0 }
    </style><button id="sw-skip">skip</button><section data-sig="pinned"><div class="ps-sticky">${panelContent}</div></section>`);
    const result = spawnSync(process.execPath, ['lib/qa/contract.mjs', html, '--dir', dir], {
      encoding: 'utf8', env: { ...process.env, LIVETEST: '1' }, timeout: 120000,
    });
    assert.equal(result.status, 0, result.stderr || result.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    for (const viewport of ['desktop', 'mobile']) {
      assert.equal(report.failed.some(item => item.id === `${viewport}-no-empty-screens`), expectEmpty, `${name} at ${viewport}`);
    }
  }
  console.log('Contract runway checks passed');
} finally {
  fs.rmSync(dir, { recursive: true, force: true });
}
