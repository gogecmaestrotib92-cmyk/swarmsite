import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-overflow-'));
try {
  for (const [name, content, expectFailure] of [
    ['clipped', '<p class="offscreen">Important text extends past the viewport</p>', true],
    ['normal', '<p>Important text wraps within the viewport</p>', false],
    ['scroller', '<div class="rail"><p class="offscreen">An intentionally scrollable item</p></div>', false],
    ['marquee', '<div class="mq-track"><p class="offscreen">An intentionally moving ticker</p></div>', false],
    ['hidden', '<div style="display:none"><p class="offscreen">Hidden content</p></div>', false],
    ['provenance', '<p class="source-actions-label" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)">Original links · A long provenance title</p><a href="https://example.com">Real link</a>', false],
    ['visible-provenance', '<p class="source-actions-label offscreen">Visible labels still need overflow checks</p>', true],
  ]) {
    const html = path.join(dir, `${name}.html`);
    fs.writeFileSync(html, `<!doctype html><style>html,body { margin:0; overflow-x:clip } .sec { height:920px } .offscreen { position:relative; left:95vw; width:max-content } .rail { overflow-x:auto; width:100% }</style><button id="sw-skip">skip</button><section class="sec" id="content">${content}</section>`);
    const result = spawnSync(process.execPath, ['lib/qa/contract.mjs', html, '--dir', dir], {
      encoding: 'utf8', env: { ...process.env, LIVETEST: '1' }, timeout: 120000,
    });
    assert.equal(result.status, 0, result.stderr || result.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    for (const viewport of ['desktop', 'mobile']) {
      assert.equal(report.failed.some(item => item.id === `${viewport}-no-overflow`), expectFailure, `${name} at ${viewport}`);
    }
  }
  console.log('Contract catches clipped text and ignores intentional scrolling');
} finally {
  fs.rmSync(dir, { recursive: true, force: true });
}
