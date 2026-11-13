// The agents on the working screen (web/js/swarm2.js): named cursors that act where the job reports something, and
// state nothing of their own. An event with a place is drawn at that place by the agent of its role, with the event's
// own words; a role without an agent on a small screen is taken by the first; with no event and no known place nothing
// is drawn on the page at all; an idle agent may only frame a place an event has already named, without words.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import { chromium } from 'playwright';
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  const page = await browser.newPage({ viewport: { width: 1100, height: 700 } }); const errors = []; page.on('pageerror', e => errors.push(String(e)));
  await page.setContent('<style>#frame{position:relative;width:1000px;height:562px;overflow:hidden;background:#333}#frame img{display:block;width:100%;height:auto}</style><div id="frame"><img id="image"></div>');
  await page.addScriptTag({ content: fs.readFileSync('web/js/swarm2.js', 'utf8') });
  await page.evaluate(async () => { const im = document.querySelector('#image'); im.src = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="2400"><rect width="100%" height="100%" fill="white"/></svg>'); await im.decode();
    window.sw = Swarm2.mount(document.querySelector('#frame'), { count: 4, roam: true, busy: 3 }); window.sw.setPage(im, 2400); });
  assert.deepEqual(await page.locator('.s2-cur .tag b').allTextContents(), ['Reader', 'Layout', 'Copy', 'Photos'], 'one agent per job, by name');
  await page.waitForTimeout(2500);
  assert.equal(await page.locator('.s2-x').count(), 0, 'nothing is drawn on the page before the job has reported anything');
  assert.deepEqual(await page.locator('.s2-cur .tag s').allTextContents(), ['', '', '', ''], 'an idle agent says nothing');
  await page.evaluate(() => window.sw.push([{ role: 'Layout', text: 'Section 1 · 40 words', rect: { x: 0, y: 80, w: 1440, h: 400 } }, { role: 'QA', text: 'Design 1: every screen passes' }, { role: 'Colour', text: 'Colours · #fbf7ee #d2552b' }]));
  await page.locator('.s2-scan.on').waitFor({ timeout: 6000 });
  const at = await page.evaluate(() => { const f = document.querySelector('#frame').getBoundingClientRect(), b = document.querySelector('.s2-scan').getBoundingClientRect(); return { x: Math.round(b.left - f.left), y: Math.round(b.top - f.top), w: Math.round(b.width) }; });
  assert.ok(Math.abs(at.x) <= 12 && Math.abs(at.y - 80 * 1000 / 1440) <= 12 && at.w >= 980, 'the section is framed where the job measured it: ' + JSON.stringify(at));
  await page.locator('.s2-cur .tag s').filter({ hasText: 'Section 1 · 40 words' }).first().waitFor({ timeout: 4000 });
  assert.equal(await page.locator('.s2-cur').filter({ hasText: 'Section 1 · 40 words' }).locator('.tag b').textContent(), 'Layout', 'by the agent whose job it is');
  await page.locator('.s2-stamp').filter({ hasText: '✓ passes' }).waitFor({ timeout: 12000 });   // a role with no agent here (QA) is taken by the first agent
  await page.locator('.s2-sw i').first().waitFor({ timeout: 12000 }); assert.equal(await page.locator('.s2-sw i').count(), 2, 'the colours the job read, as swatches');
  await page.locator('.s2-peek.on').first().waitFor({ timeout: 15000 });   // idle again: only the place already named, framed without words
  assert.equal(await page.locator('.s2-peek').first().textContent(), '');
  await page.evaluate(() => window.sw.pause(true)); await page.waitForTimeout(4500); const before = await page.locator('.s2-cur').evaluateAll(cs => cs.map(c => c.style.transform)); await page.waitForTimeout(1500);
  assert.deepEqual(await page.locator('.s2-cur').evaluateAll(cs => cs.map(c => c.style.transform)), before, 'paused agents stand still');
  assert.deepEqual(errors, []);
  console.log('Agents: one per job by name, nothing drawn before the job reports, a section framed where it was measured, a missing role taken by the first agent, idle agents only look');
} finally { await browser.close(); }
