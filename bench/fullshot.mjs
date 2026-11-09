/* fullshot.mjs — one top-to-bottom picture of a built page per viewport, for side-by-side comparison.
   node bench/fullshot.mjs page.html --out <dir>   →  <dir>/desktop.jpg (1440 wide) and <dir>/mobile.jpg (390 wide)
   Motion is off (prefers-reduced-motion), so pinned and sticky sections lay out as static content and nothing is caught
   mid-animation; scroll-revealed elements are forced visible, the way lib/qa/shots.mjs does for the critic.
   Prints one JSON line: {"desktop": {"width", "height"}, "mobile": {...}}. */
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path';
const args = process.argv.slice(2); const file = path.resolve(args[0]);
const out = args.includes('--out') ? args[args.indexOf('--out') + 1] : path.dirname(file); fs.mkdirSync(out, { recursive: true });
const mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chromePath = process.env.CHROME_PATH || (fs.existsSync(mac) ? mac : '/usr/bin/google-chrome');
const browser = await chromium.launch({ executablePath: fs.existsSync(chromePath) ? chromePath : undefined, args: ['--no-sandbox', '--disable-gpu'] });
const MAX_PIXELS = 15000; // one screenshot taller than this in device pixels is cut by the browser: lower the density instead
const report = {};
for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844 }]]) {
  let scale = name === 'mobile' ? 2 : 1, height = 0;
  for (let attempt = 0; attempt < 2; attempt++) {
    const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: scale, reducedMotion: 'reduce' }); const page = await ctx.newPage();
    await page.goto('file://' + file + '?nomotion=1', { waitUntil: 'load' });
    await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {});
    if (await page.locator('#sw-skip').count()) await page.click('#sw-skip', { timeout: 1000 }).catch(() => {});
    // walk the page once so lazy pictures and scroll observers have fired, then come back to the top
    height = await page.evaluate(async () => { const step = innerHeight * .8; for (let y = 0; y < document.documentElement.scrollHeight; y += step) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); return document.documentElement.scrollHeight; });
    if (height * scale > MAX_PIXELS && scale > 1) { scale = 1; await ctx.close(); continue; }
    await page.addStyleTag({ content: '[data-move],.sec *:not(.ps-s):not(.sp-f):not(.ps-s *):not(.sp-f *){opacity:1!important;transform:none!important;clip-path:none!important;filter:none!important}' }).catch(() => {});
    await page.waitForTimeout(400);
    await page.screenshot({ path: path.join(out, `${name}.jpg`), fullPage: true, type: 'jpeg', quality: 74 });
    report[name] = { width: vp.width, height, scale };
    await ctx.close(); break;
  }
}
await browser.close(); console.log(JSON.stringify(report));
