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
    // every section is shot from its top (scroll-margin keeps the heading clear of a fixed nav); a pinned or sticky panel starts at the top of its runway, so its first frame is in this shot
    await sel[i].evaluate(el => el.scrollIntoView({ block: 'start' })); await page.waitForTimeout(WAIT);
    await page.mouse.wheel(0, 1); await page.waitForTimeout(120);
    await page.screenshot({ path: path.join(out, `${name}-${String(i).padStart(2, '0')}-${secs[i].id}.png`) });
    // a pinned sequence swaps frames in place: show up to three frames at the same scroll position (first, middle, last)
    const slides = await sel[i].$$('.ps-s');
    if (slides.length > 1) {
      const count = Math.min(3, slides.length);
      const indexes = [...new Set(Array.from({ length: count }, (_, n) => Math.round(n * (slides.length - 1) / (count - 1))))];
      for (const index of indexes) {
        // the frame is switched on in place (the real layout stacks frames inside the pinned panel) and brought into view (a static fallback lays them out one under another)
        await sel[i].evaluate((el, idx) => { el.querySelectorAll('.ps-s').forEach((s, n) => s.classList.toggle('on', n === idx)); el.querySelectorAll('.ps-dot').forEach((s, n) => s.classList.toggle('on', n === idx)); const f = el.querySelectorAll('.ps-s')[idx]; if (f) f.scrollIntoView({ block: 'start' }); }, index); await page.waitForTimeout(Math.min(WAIT, 500));
        await sel[i].evaluate(() => { const nav = document.querySelector('nav'); if (nav && ['fixed', 'sticky'].includes(getComputedStyle(nav).position)) { const r = nav.getBoundingClientRect(); if (r.top <= 0 && r.bottom > 0) window.scrollBy(0, -r.bottom - 10); } });
        await page.screenshot({ path: path.join(out, `${name}-${String(i).padStart(2, '0')}-${secs[i].id}-slide-${String(index + 1).padStart(2, '0')}-of-${String(slides.length).padStart(2, '0')}.png`) });
      }
    }
  }
  await ctx.close();
}
await browser.close(); console.log('shots →', out);
