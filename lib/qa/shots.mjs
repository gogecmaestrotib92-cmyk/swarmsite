/* shots.mjs — QA "look" step: opens a built page, skips the swarm, scrolls every section into view and
   screenshots it at 1440x900 and 390x844. node lib/qa/shots.mjs v3/c1.html --out shots/c1 */
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path';
const args = process.argv.slice(2); const file = path.resolve(args[0]); const out = args[args.indexOf('--out') + 1] || 'shots'; fs.mkdirSync(out, { recursive: true });
const chromePath = process.env.CHROME_PATH || '/usr/bin/google-chrome';
const browser = await chromium.launch({ executablePath: chromePath, args: ['--no-sandbox', '--disable-gpu'] });
for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844, deviceScaleFactor: 2 }]]) {
  const ctx = await browser.newContext({ viewport: vp }); const page = await ctx.newPage();
  await page.goto('file://' + file); await page.waitForTimeout(800);
  await page.click('#sw-skip').catch(() => {}); await page.waitForTimeout(1200);
  const secs = await page.$$eval('body > section, body > footer, body > .band, main > section', els => els.map((el, i) => ({ i, id: el.id || el.className.split(' ')[0] || el.tagName.toLowerCase() })));
  const sel = await page.$$('body > section, body > footer, body > .band, main > section');
  for (let i = 0; i < sel.length; i++) {
    await sel[i].evaluate(el => el.scrollIntoView({ block: 'start' })); await page.waitForTimeout(1400);
    await page.mouse.wheel(0, 1); await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(out, `${name}-${String(i).padStart(2, '0')}-${secs[i].id}.png`) });
  }
  await ctx.close();
}
await browser.close(); console.log('shots →', out);
