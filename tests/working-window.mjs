/* The window a visitor watches while their preview is made. A job takes minutes; for most of them no event arrives.
   The owner saw a window that looked stopped, so this holds what makes it look alive and keeps it truthful:
   - agents are ON the page from the first seconds, with no event at all, and they are drawn (the form's own rule for
     pictures in the frame once gave every agent opacity 0 — they were there and nobody could see them);
   - an agent that only roams shows no finding: text beside an agent comes from a real event and nothing else;
   - the bar has one segment per step of the job, the clock counts from the job's own start, the tab's title says how far;
   - the bar and the clock are on the screen without scrolling, at a laptop and at a phone;
   - a dropped connection is said as that, not as a failed job, and taken back when the job answers again;
   - when the job ends, the light and the clock stop. */
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module';
const root = process.cwd(), { chromium } = createRequire(path.join(root, 'package.json'))('playwright');
const ID = '11111111-1111-4111-8111-111111111111', LABELS = ['Reading', 'Auditing', 'Art direction', 'Building', 'Checking', 'Publishing'];
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64');
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
async function open(width, height) {
  const state = { status: 'running', at: 2, events: [], down: false, started: Date.now() - 65000 };
  const job = () => ({ id: ID, url: 'https://river.test/', status: state.status, created_at: new Date(state.started).toISOString(), result: { events: state.events },
    steps: LABELS.map((label, i) => ({ id: 's' + i, label: label + ': detail', status: state.status === 'done' || i < state.at ? 'done' : i === state.at && state.status === 'running' ? 'running' : 'pending' })) });
  const page = await browser.newPage({ viewport: { width, height } }); const errors = []; page.on('pageerror', e => errors.push(String(e)));
  await page.route('**/*', async r => { const u = new URL(r.request().url());
    if (u.hostname === 'api.test') { if (state.down) return r.abort(); if (u.pathname.startsWith('/p/')) return r.fulfill({ contentType: 'text/html', body: '<p>preview</p>' }); return r.fulfill({ contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(job()) }); }
    if (u.hostname !== 'app.test') return r.fulfill({ status: 204, body: '' });
    if (u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test';window.SWARMSITE_SUPABASE={url:'',anon:''};" });
    if (u.pathname === '/app') return r.fulfill({ contentType: 'text/html', body: fs.readFileSync(path.join(root, 'web/app.html')) });
    if (/\.(webp|png|gif)$/.test(u.pathname)) return r.fulfill({ contentType: 'image/png', body: PNG });
    try { return r.fulfill({ contentType: u.pathname.endsWith('.css') ? 'text/css' : 'application/javascript', body: fs.readFileSync(path.join(root, 'web', u.pathname)) }); } catch { return r.fulfill({ status: 404, body: '' }); } });
  await page.goto(`https://app.test/app?url=river.test&job=${ID}`); await page.waitForTimeout(3200);
  return { page, state, errors };
}
const agents = page => page.evaluate(() => { const f = document.querySelector('#frame').getBoundingClientRect(); return [...document.querySelectorAll('#frame .s2-cur')].map(c => { const im = c.querySelector('.agent-photo'), r = (im || c).getBoundingClientRect(), cs = getComputedStyle(c);
  return { seen: cs.opacity === '1' && cs.display !== 'none' && (!im || getComputedStyle(im).opacity === '1') && r.width > 20 && r.right > f.left && r.left < f.right && r.bottom > f.top && r.top < f.bottom, x: Math.round(r.left), y: Math.round(r.top), says: c.querySelector('.tag s').textContent }; }); });
try {
  for (const [width, height, least] of [[1440, 900, 10], [390, 800, 6]]) {
    const { page, state, errors } = await open(width, height); const first = await agents(page);
    assert.ok(first.filter(a => a.seen).length >= least, `${width}: ${least}+ agents are on the page and drawn within three seconds, with no event: ${JSON.stringify(first.filter(a => a.seen).length)} of ${first.length}`);
    assert.ok(first.every(a => a.says === ''), 'an agent with no event of its own shows no finding: ' + JSON.stringify(first.map(a => a.says)));
    await page.waitForTimeout(2500); const later = await agents(page); const moved = later.filter((a, i) => Math.hypot(a.x - first[i].x, a.y - first[i].y) > 12).length;
    assert.ok(moved >= least - 2, `${width}: they keep moving while nothing arrives: ${moved} moved`);
    const hud = await page.evaluate(() => { const b = id => document.querySelector(id).getBoundingClientRect(), seg = [...document.querySelectorAll('#prog i')].map(i => i.className); return { seg, clock: document.querySelector('#clock').textContent, count: document.querySelector('#hudR').textContent, title: document.title, bar: b('#prog').bottom, clockBottom: b('#clock').bottom, vh: innerHeight, doc: document.documentElement.scrollWidth, vw: innerWidth, glow: getComputedStyle(document.querySelector('#work'), '::before').animationName, crew: [...document.querySelectorAll('.wk-robot')].filter(n => n.offsetParent).length }; });
    assert.deepEqual(hud.seg, ['done', 'done', 'run', '', '', ''], 'one segment per step, in the state the job reports'); assert.equal(hud.count, '2 / 6'); assert.match(hud.title, /^2\/6 · Working/);
    assert.match(hud.clock, /^01:(0[5-9]|1\d)$/, 'the clock counts from when the job was started, not from when the page was opened: ' + hud.clock);
    assert.ok(hud.clockBottom <= hud.vh && hud.bar <= hud.vh, `${width}: the bar and the clock are on the screen without scrolling ${JSON.stringify(hud)}`); assert.ok(hud.doc <= hud.vw, 'nothing is wider than the screen');
    assert.equal(hud.glow, 'wk-spin', 'the light travels round the frame while the job runs'); assert.ok(hud.crew >= 3, 'the crew looks over the edge');
    state.events = [{ role: 'Audit', text: '412 words · 7 sections' }]; await page.waitForTimeout(5200);
    assert.ok((await agents(page)).some(a => a.says === '412 words · 7 sections') || (await page.locator('#log').textContent()).includes('412 words'), 'a real event is shown as it came');
    state.down = true; await page.waitForTimeout(3600); assert.match(await page.locator('#micro').textContent(), /Connection lost/); assert.equal(await page.locator('#err').textContent(), '', 'a dropped connection is not reported as a failure');
    state.down = false; await page.waitForTimeout(3600); assert.doesNotMatch(await page.locator('#micro').textContent(), /Connection lost/, 'and is taken back when the job answers');
    state.status = 'done'; await page.waitForTimeout(3600); assert.equal(await page.locator('#work').getAttribute('class'), 'work is-still'); assert.match(await page.title(), /Preview ready/);
    const stopped = await page.locator('#clock').textContent(); await page.waitForTimeout(1300); assert.equal(await page.locator('#clock').textContent(), stopped, 'the clock stops with the job'); assert.deepEqual(errors, []); await page.close();
  }
  console.log('Working window: agents on the page and drawn from the start, progress, clock and connection told truthfully');
} finally { await browser.close(); }
