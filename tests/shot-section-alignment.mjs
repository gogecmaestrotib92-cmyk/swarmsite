import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { chromium } from 'playwright';

const root = path.resolve(import.meta.dirname, '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-shot-alignment-'));
const html = path.join(tmp, 'page.html');
const out = path.join(tmp, 'shots');
const sections = ['ordinary', 'typewall', 'pinned', 'sticky'];
const chrome = process.env.CHROME_PATH || (process.platform === 'darwin'
  ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' : '/usr/bin/google-chrome');
try {
  fs.writeFileSync(html, `<!doctype html><style>
    html,body{margin:0} nav{position:fixed;top:0;height:90px;width:100%;background:black;z-index:5}
    section{height:100vh;background:white;box-sizing:border-box;padding:40px 20px;scroll-margin-top:100px}
    h2{margin:0;width:150px;height:100px;background:rgb(255,0,0)}
    section#pinned{height:auto} .ps-s{height:100vh;box-sizing:border-box;padding-top:40px}
    .ps-s b{display:block;width:150px;height:100px}
  </style><nav></nav><div style="height:120px"></div>${sections.map(id => `<section id="${id}" data-sig="${id}"><h2></h2>${id === 'pinned'
    ? '<div class="ps-s"><b style="background:red"></b></div><div class="ps-s"><b style="background:lime"></b></div><div class="ps-s"><b style="background:blue"></b></div>'
    : ''}</section>`).join('')}
  <section id="buffer"></section>`);
  execFileSync('node', [path.join(root, 'lib/qa/shots.mjs'), html, '--out', out, '--fast'],
    { env: { ...process.env, CHROME_PATH: chrome }, stdio: 'pipe' });
  const browser = await chromium.launch({ executablePath: fs.existsSync(chrome) ? chrome : undefined });
  try {
    const page = await browser.newPage();
    for (const viewport of ['desktop', 'mobile']) for (const [index, id] of sections.entries()) {
      const png = fs.readFileSync(path.join(out, `${viewport}-${String(index).padStart(2, '0')}-${id}.png`));
      const sample = await page.evaluate(async data => {
        const image = new Image(); image.src = 'data:image/png;base64,' + data;
        await image.decode();
        const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
        const context = canvas.getContext('2d'); context.drawImage(image, 0, 0);
        const scale = image.width / (image.width > 1000 ? 1440 : 390);
        return [...context.getImageData(30 * scale, 155 * scale, 1, 1).data];
      }, png.toString('base64'));
      assert.ok(sample[0] > 240 && sample[1] < 20 && sample[2] < 20,
        `${viewport} ${id} heading clipped, pixel=${sample}`);
    }
    for (const viewport of ['desktop', 'mobile']) for (const [index, channel] of [0, 1, 2].entries()) {
      const png = fs.readFileSync(path.join(out, `${viewport}-02-pinned-slide-${String(index + 1).padStart(2, '0')}-of-03.png`));
      const sample = await page.evaluate(async data => {
        const image = new Image(); image.src = 'data:image/png;base64,' + data; await image.decode();
        const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
        const context = canvas.getContext('2d'); context.drawImage(image, 0, 0);
        const scale = image.width / (image.width > 1000 ? 1440 : 390);
        return [...context.getImageData(30 * scale, 155 * scale, 1, 1).data];
      }, png.toString('base64'));
      assert.ok(sample[channel] > 240 && sample[(channel + 1) % 3] < 20 && sample[(channel + 2) % 3] < 20,
        `${viewport} pinned slide ${index + 1} missing, pixel=${sample}`);
    }
  } finally { await browser.close(); }
  console.log('All static section headings visible on desktop and mobile');
} finally { fs.rmSync(tmp, { recursive: true, force: true }); }
