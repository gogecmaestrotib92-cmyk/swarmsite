/* shots.mjs — QA "look" step: opens a built page, skips the swarm, scrolls every section into view and
   screenshots it at 1440x900 and 390x844. node lib/qa/shots.mjs v3/c1.html --out shots/c1 */
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path';
const args = process.argv.slice(2); const file = path.resolve(args[0]); const out = args[args.indexOf('--out') + 1] || 'shots'; fs.mkdirSync(out, { recursive: true });
const only = args.includes('--desktop-only'); const WAIT = args.includes('--fast') ? 450 : 1400;
const chromePath = process.env.CHROME_PATH || '/usr/bin/google-chrome';
const exe = chromePath && fs.existsSync(chromePath) ? chromePath : undefined;
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu'].concat(process.env.LIVETEST ? ['--proxy-server=direct://', '--proxy-bypass-list=*'] : []) });
for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844, deviceScaleFactor: 2 }]].filter(([n]) => !only || n === 'desktop')) {
  const ctx = await browser.newContext({ viewport: vp }); const page = await ctx.newPage(); await page.route(/^https?:\/\//, r => /fonts\.gstatic|fonts\.googleapis|cdnjs|unpkg/.test(r.request().url()) && process.env.LIVETEST ? r.abort() : r.continue()).catch(() => {});
  await page.goto('file://' + file + '?nomotion=1'); await page.waitForTimeout(500); await page.addStyleTag({ content: '[data-move],.sec *:not(.ps-s):not(.sp-f):not(.ps-s *):not(.sp-f *){opacity:1!important;transform:none!important;clip-path:none!important;filter:none!important}' }).catch(() => {});
  if (await page.locator('#sw-skip').count()) await page.click('#sw-skip', { timeout: 1000 }).catch(() => {});
  await page.waitForTimeout(400);
  const secs = await page.$$eval('body > section, body > footer, body > .band, main > section', els => els.map((el, i) => ({ i, id: el.id || el.className.split(' ')[0] || el.tagName.toLowerCase() })));
  const sel = await page.$$('body > section, body > footer, body > .band, main > section');
  for (let i = 0; i < sel.length; i++) {
    // The capture URL disables motion, so these sections have no animation
    // runway. Starting partway through them clips their static content.
    await sel[i].evaluate(el => el.scrollIntoView({ block: 'start' })); await page.waitForTimeout(WAIT);
    await page.mouse.wheel(0, 1); await page.waitForTimeout(120);
    await page.screenshot({ path: path.join(out, `${name}-${String(i).padStart(2, '0')}-${secs[i].id}.png`) });
    // A static pinned sequence can be taller than a viewport. Capture up to
    // three representative slides, always including the first and last.
    const slides = await sel[i].$$('[data-sig="pinned"] .ps-s, :scope[data-sig="pinned"] .ps-s');
    const count = Math.min(3, slides.length);
    const indexes = [...new Set(Array.from({ length: count }, (_, n) =>
      count === 1 ? 0 : Math.round(n * (slides.length - 1) / (count - 1))))];
    for (const index of indexes) {
      await slides[index].evaluate(el => {
        el.scrollIntoView({ block: 'start' });
        // Static slides are not sections and do not inherit their anchor offset.
        const nav = document.querySelector('nav');
        if (nav && ['fixed', 'sticky'].includes(getComputedStyle(nav).position)) {
          const rect = nav.getBoundingClientRect();
          if (rect.top <= 0 && rect.bottom > 0) window.scrollBy(0, -rect.bottom - 10);
        }
      }); await page.waitForTimeout(WAIT);
      await page.screenshot({ path: path.join(out, `${name}-${String(i).padStart(2, '0')}-${secs[i].id}-slide-${String(index + 1).padStart(2, '0')}-of-${String(slides.length).padStart(2, '0')}.png`) });
    }
  }
  await ctx.close();
}
await browser.close(); console.log('shots →', out);
