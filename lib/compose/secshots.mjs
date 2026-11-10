/* secshots.mjs — one picture of each named section of a page, at 1440 px, as a visitor sees it at rest.
   node lib/compose/secshots.mjs page.html <out dir> <section id> [<section id> …]   →  <out dir>/<id>.jpg
   Motion is off and scroll-revealed pieces are forced visible, the way the contract and the critic's screenshots do it;
   the fixed navigation is hidden so that it does not lie across the section. Prints {"shot": [ids]}. */
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path';
const [file, out, ...ids] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
const mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chromePath = process.env.CHROME_PATH || (fs.existsSync(mac) ? mac : '/usr/bin/google-chrome');
const browser = await chromium.launch({ executablePath: fs.existsSync(chromePath) ? chromePath : undefined, args: ['--no-sandbox', '--disable-gpu'].concat(process.env.LIVETEST ? ['--proxy-server=direct://', '--proxy-bypass-list=*'] : []) });
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } }); const page = await ctx.newPage();
await page.route(/^https?:\/\//, r => /fonts\.gstatic|fonts\.googleapis|cdnjs|unpkg/.test(r.request().url()) && process.env.LIVETEST ? r.abort() : r.continue()).catch(() => {});
await page.goto('file://' + path.resolve(file) + '?nomotion=1'); await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {}); await page.waitForTimeout(350);
await page.addStyleTag({ content: '[data-move],.sec *:not(.ps-s):not(.sp-f):not(.ps-s *):not(.sp-f *){opacity:1!important;transform:none!important;clip-path:none!important;filter:none!important}.nav{display:none!important}.sec.lc .lc-head{position:static!important}' }).catch(() => {});
const shot = [];
for (const id of ids) {
  if (!/^[A-Za-z0-9_-]{1,60}$/.test(id)) continue;
  const el = page.locator(`section[id="${id}"]`); if (!(await el.count())) continue;
  const box = await el.first().boundingBox(); if (!box || box.height < 4) continue;
  await page.screenshot({ path: path.join(out, id + '.jpg'), type: 'jpeg', quality: 76, fullPage: true, clip: { x: 0, y: box.y, width: 1440, height: Math.min(box.height, 2400) } });
  shot.push(id);
}
await browser.close(); console.log(JSON.stringify({ shot }));
