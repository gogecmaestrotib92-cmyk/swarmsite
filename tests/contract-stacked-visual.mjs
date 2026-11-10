/* A figure that lays several pictures on each other is one first-screen visual: it registers by the room the pictures
   take together. A row of small icons in a figure does not, and neither does one small picture. */
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-stacked-visual-'));
const png = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
const img = (style) => `<img src="${png}" alt="" style="position:absolute;${style}">`;
try {
  const cases = [
    // [name, figure markup, a visual at 1440?]
    ['one-large', `<figure style="width:520px;height:400px">${img('left:0;top:0;width:520px;height:400px')}</figure>`, true],
    ['one-small', `<figure style="width:300px;height:400px">${img('left:0;top:0;width:300px;height:400px')}</figure>`, false],
    ['stack-of-two', `<figure style="width:560px;height:460px">${img('left:0;top:0;width:380px;height:400px')}${img('left:180px;top:60px;width:380px;height:400px')}</figure>`, true],
    ['fan-of-three', `<figure style="width:600px;height:460px">${img('left:0;top:20px;width:300px;height:400px')}${img('left:150px;top:0;width:300px;height:400px')}${img('left:300px;top:20px;width:300px;height:400px')}</figure>`, true],
    ['row-of-icons', `<figure style="width:600px;height:140px">${[0, 1, 2, 3].map(i => img(`left:${i * 150}px;top:0;width:130px;height:130px`)).join('')}</figure>`, false],
    ['narrow-stack', `<figure style="width:400px;height:460px">${img('left:0;top:0;width:260px;height:400px')}${img('left:140px;top:60px;width:260px;height:400px')}</figure>`, false],
  ];
  for (const [name, figure, expected] of cases) {
    const html = path.join(dir, `${name}.html`);
    fs.writeFileSync(html, `<!doctype html><style>html,body{margin:0}figure{position:relative;margin:40px}.sec{min-height:700px}</style><section class="sec hero"><h1>Two words</h1>${figure}<a class="btn" href="https://example.test/">Go</a></section>`);
    const result = spawnSync(process.execPath, ['lib/qa/contract.mjs', html, '--dir', dir], { encoding: 'utf8', env: { ...process.env, LIVETEST: '1' }, timeout: 120000 });
    assert.equal(result.status, 0, result.stderr || result.stdout);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json'), 'utf8'));
    const failed = report.failed.some(f => f.id === 'desktop-first-screen-visual');
    assert.equal(!failed, expected, `${name}: ${expected ? 'is' : 'is not'} a first-screen visual at 1440`);
  }
  console.log('contract-stacked-visual: ok');
} finally { fs.rmSync(dir, { recursive: true, force: true }); }
