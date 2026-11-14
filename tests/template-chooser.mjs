// The chooser of the template path in web/app.html: the job is started with engine 'templates' where the server has
// it on; the three variants show as soon as they are in the job (side by side on a desk, stacked on a phone), each
// opens full screen, one is picked, and the download waits for its package, then asks for sign-in and payment.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module';
import { publicJob, TEMPLATE_SLUGS } from '../server/designs.mjs';   // the job is served as GET /jobs/:id serves it: by design id and name
const root = process.cwd(), { chromium } = createRequire(path.join(root, 'package.json'))('playwright');
const html = fs.readFileSync(path.join(root, 'web/app.html'), 'utf8'), id = '33333333-3333-4333-8333-333333333333';
const variant = (slug, pkg, i) => ({ slug, id: `v${i + 1}`, name: `Design ${i + 1}`, approach: 'land · screens', why: 'niche software', url: `https://api.test/t/${id}/v${i + 1}`, package: pkg });
const steps = ['capture', 'read', 'choose', 'publish', 'package'].map((s, i) => ({ id: s, label: s, status: i < 4 ? 'done' : 'running' }));
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  for (const width of [1440, 390]) {
    const state = { job: { id, url: 'https://www.tallyfern.example/', status: 'running', created_at: new Date().toISOString(), steps, result: { templates: { variants: [variant('griffin', 'pending', 0), variant('maze', 'ready', 1), variant('cerebrium', 'refused', 2)], rejected: [] }, events: [] } }, posted: null, asked: [] };
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route('**/*', async r => { const u = new URL(r.request().url());
      if (u.hostname === 'app.test' && u.pathname === '/app') return r.fulfill({ contentType: 'text/html', body: html });
      if (u.hostname === 'app.test' && u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test'" });
      if (u.hostname === 'app.test' && u.pathname === '/js/swarm2.js') return r.fulfill({ contentType: 'application/javascript', body: 'window.Swarm2={mount:()=>({stop(){},phase(){},push(){},setPage(){}})}' });
      if (u.hostname === 'api.test' && u.pathname === '/config') return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ auth: {}, templates: true }) });
      if (u.hostname === 'api.test' && u.pathname === '/jobs' && r.request().method() === 'POST') { state.posted = JSON.parse(r.request().postData()); return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ id }) }); }
      if (u.hostname === 'api.test' && u.pathname === `/jobs/${id}`) return r.fulfill({ contentType: 'application/json', body: JSON.stringify(publicJob(state.job)) });
      if (u.hostname === 'api.test' && /^\/t\/[^/]+\/[a-z0-9]+\/package$/.test(u.pathname)) { state.asked.push(u.pathname + u.search); return state.free ? r.fulfill({ contentType: 'application/json', body: JSON.stringify({ url: 'https://files.test/signed/design-1.zip?token=t', name: 'tallyfern-design-1.zip' }) }) : r.fulfill({ status: 402, contentType: 'application/json', body: JSON.stringify({ error: 'Payment is needed', pay: true }) }); }
      if (u.hostname === 'files.test') return r.fulfill({ contentType: 'application/zip', headers: { 'content-disposition': 'attachment; filename="tallyfern-design-1.zip"' }, body: Buffer.from('PK\u0005\u0006' + '\u0000'.repeat(18), 'latin1') });
      if (u.hostname === 'api.test' && u.pathname.startsWith(`/t/${id}/`)) return r.fulfill({ contentType: 'text/html', body: `<!doctype html><body style="margin:0;font:40px Arial"><h1>${u.pathname.split('/').pop()}</h1><p style="height:2000px">page</p></body>` });
      return r.abort(); });
    let briefSeen = false; await page.exposeFunction('__brief', () => { briefSeen = true; });
    await page.addInitScript(() => { new MutationObserver(() => { const b = document.querySelector('#brief'); if (b && !b.classList.contains('hide') && getComputedStyle(b).display !== 'none') window.__brief(); }).observe(document, { subtree: true, childList: true, attributes: true }); });
    await page.goto('https://app.test/app?url=tallyfern.example&niche=software&goal=Start%20a%20trial');   // "I have a site": the designs start at once, no brief
    await page.locator('#choose.on').waitFor({ timeout: 10000 });
    assert.equal(state.posted?.options?.engine, 'templates', 'the job asks for the template path where the server has it on');
    assert.deepEqual(state.posted.options, { engine: 'templates', niche: 'software', goal: 'Start a trial' }, 'only what the visitor gave beside the address; the old brief is not asked on the template path');
    assert.equal(briefSeen, false, 'the old brief is never shown on the template path');
    assert.equal(await page.locator('.card .how').count(), 0, 'nothing internal under a design\'s name');
    const cards = page.locator('.card'); assert.equal(await cards.count(), 3);
    const boxes = await cards.evaluateAll(cs => cs.map(c => { const r = c.getBoundingClientRect(); return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width) }; }));
    if (width === 1440) assert.ok(boxes.every(b => b.y === boxes[0].y) && boxes[0].x < boxes[1].x && boxes[1].x < boxes[2].x, 'side by side on a desk: ' + JSON.stringify(boxes));
    else assert.ok(boxes[0].y < boxes[1].y && boxes[1].y < boxes[2].y && boxes.every(b => b.x === boxes[0].x && b.w > 300), 'stacked on a phone: ' + JSON.stringify(boxes));
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth - innerWidth), 0, 'no sideways scroll');
    const shot = await page.locator('.card .shot').first().evaluate(s => ({ w: s.clientWidth, h: s.clientHeight, scale: new DOMMatrix(getComputedStyle(s.querySelector('iframe')).transform).a }));
    assert.ok(Math.abs(shot.scale - shot.w / 1440) < .01 && Math.abs(shot.h / shot.w - 900 / 1440) < .02, 'each card shows its design at desk width, scaled down whole: ' + JSON.stringify(shot));
    assert.deepEqual(await page.locator('.card .shot iframe').evaluateAll(fs => fs.map(f => new URL(f.src).pathname.split('/').pop())), ['v1', 'v2', 'v3']);
    const words = (await page.locator('#choose').innerText()) + ' ' + (await page.locator('#choose').innerHTML());
    assert.deepEqual(TEMPLATE_SLUGS.filter(s => new RegExp(`(?<![a-z0-9])${s}(?![a-z0-9])`, 'i').test(words)), [], 'the chooser names no template, in its words or its markup');
    assert.deepEqual(await page.locator('.card .name').allTextContents(), ['Design 1', 'Design 2', 'Design 3']);
    // full screen, at desk and phone width, and choosing from there
    await page.locator('.card').nth(1).locator('.open').click();
    assert.ok(await page.locator('#full.on').isVisible() && (await page.locator('#fullFrame').getAttribute('src')).endsWith('/v2'));
    await page.locator('#full .seg button[data-f="mobile"]').click(); assert.ok(await page.locator('#full.is-phone').count() === 1);
    await page.locator('#fullPick').click(); assert.ok(!(await page.locator('#full.on').count()), 'closed after choosing');
    assert.equal(await page.locator('.card.picked').getAttribute('data-slug'), 'v2'); assert.equal(await page.locator('.card.picked .pickb').getAttribute('aria-pressed'), 'true');
    // download: ready → asks; a refused package and one being prepared → not offered
    assert.equal(await page.locator('#download').isDisabled(), false);
    await page.locator('#download').click(); await page.waitForFunction(() => /Payment comes before the download/.test(document.querySelector('#chooseNote').textContent));
    assert.deepEqual(state.asked, [`/t/${id}/v2/package?link=1`], 'the download asks the package endpoint, which answers with the payment hook');
    await page.locator('.card').nth(2).locator('.pickb').click(); assert.ok(await page.locator('#download').isDisabled() && /did not match the preview/.test(await page.locator('#chooseNote').textContent()));
    await page.locator('.card').nth(0).locator('.pickb').click(); assert.ok(await page.locator('#download').isDisabled() && /being prepared/.test(await page.locator('#chooseNote').textContent()));
    // the job finishes: the package that was being prepared is ready, the choice is kept, the cards are not rebuilt
    const before = await page.locator('.card .shot iframe').first().evaluate(f => f.dataset.stamp = 'kept');
    state.job = { ...state.job, status: 'done', steps: steps.map(s => ({ ...s, status: 'done' })), result: { ...state.job.result, seconds: 74, templates: { ...state.job.result.templates, variants: [variant('griffin', 'ready', 0), variant('maze', 'ready', 1), variant('cerebrium', 'refused', 2)] } } };
    await page.waitForFunction(() => !document.querySelector('#download').disabled, null, { timeout: 8000 });
    assert.equal(await page.locator('.card.picked').getAttribute('data-slug'), 'v1');
    assert.equal(await page.locator('.card .shot iframe').first().evaluate(f => f.dataset.stamp), 'kept', 'the previews are not reloaded on every poll');
    assert.ok(!(await page.locator('#result.on').count()), 'the old single-preview view stays out of the way');
    // a design that may be downloaded: the browser itself fetches the file from the address the server hands out (a
    // phone ignores bytes handed to it by the page after a wait), the line says it has started and keeps that address as a link
    state.free = true; const dl = page.waitForEvent('download', { timeout: 10000 });
    await page.locator('#download').click(); const got = await dl;
    assert.equal(got.suggestedFilename(), 'tallyfern-design-1.zip'); assert.equal(got.url(), 'https://files.test/signed/design-1.zip?token=t');
    await page.waitForFunction(() => /Your download has started/.test(document.querySelector('#chooseNote').textContent) && !document.querySelector('#download').disabled);
    assert.equal(await page.locator('#chooseNote #zipLink').getAttribute('href'), 'https://files.test/signed/design-1.zip?token=t');
    await page.waitForTimeout(2600); assert.ok(await page.locator('#chooseNote #zipLink').count() === 1 && await page.locator('.choose.on').count() === 1, 'the line and its link stay through the next poll; the chooser is still there');
    await page.close();
  }
  // covers: a design with a cover shows that still once it has loaded, never its live page; until then the card says what it waits for.
  // And "I built a first version of my app": screenshots are uploaded as they are chosen, and the job carries their names.
  { const COVER = fs.readFileSync(path.join(root, 'web/favicon.png'));
    const st = { posted: null, ups: 0, coverHeld: true }; const vs = [0, 1, 2].map(i => ({ ...variant(['griffin', 'maze', 'cerebrium'][i], 'ready', i), cover: `https://store.test/p/${id}/t/v${i + 1}-cover.jpg` }));
    const job = { id, url: 'https://www.tallyfern.example/', status: 'done', created_at: new Date().toISOString(), steps: steps.map(s => ({ ...s, status: 'done' })), result: { templates: { variants: vs, rejected: [] }, events: [] } };
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    await page.route('**/*', async r => { const u = new URL(r.request().url());
      if (u.pathname === '/app') return r.fulfill({ contentType: 'text/html', body: html });
      if (u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test'" });
      if (u.pathname === '/js/swarm2.js') return r.fulfill({ contentType: 'application/javascript', body: 'window.Swarm2={mount:()=>({stop(){},phase(){},push(){},setPage(){}})}' });
      if (u.pathname === '/config') return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ auth: {}, templates: true }) });
      if (u.pathname === '/uploads') { st.ups++; return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ file: `0000000${st.ups}-4e5f-4a6b-8c7d-9e0f1a2b3c4d.png` }) }); }
      if (u.pathname === '/jobs' && r.request().method() === 'POST') { st.posted = JSON.parse(r.request().postData()); return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ id }) }); }
      if (u.pathname === `/jobs/${id}`) return r.fulfill({ contentType: 'application/json', body: JSON.stringify(publicJob(job)) });
      if (u.hostname === 'store.test') { while (st.coverHeld) await new Promise(ok => setTimeout(ok, 50)); return r.fulfill({ contentType: 'image/png', body: COVER }); }
      if (u.pathname.startsWith(`/t/${id}/`)) throw new Error('a card with a cover asked for its live page');
      return r.abort(); });
    await page.goto('https://app.test/app?url=tallyfern.example&with=screens');
    await page.locator('#shots').waitFor(); assert.match(await page.locator('#h').textContent(), /screenshots/i);
    await page.setInputFiles('#shotFiles', [path.join(root, 'web/logo/swarmsite-mark.png'), path.join(root, 'web/apple-touch-icon.png')]);
    await page.waitForFunction(() => !document.querySelector('#shotsGo').disabled && document.querySelectorAll('.thumb:not(.up)').length === 2);
    await page.locator('#shotsGo').click(); await page.locator('#choose.on').waitFor({ timeout: 10000 });
    assert.deepEqual({ ...st.posted.options, screens: [...(st.posted.options.screens || [])].sort() }, { engine: 'templates', screens: ['00000001-4e5f-4a6b-8c7d-9e0f1a2b3c4d.png', '00000002-4e5f-4a6b-8c7d-9e0f1a2b3c4d.png'] }, 'both screenshots go with the job, by the names the server gave them');
    assert.equal(await page.locator('.card .shot iframe').count(), 0, 'a card with a cover never loads its live page');
    assert.deepEqual(await page.locator('.card .state.busy').allTextContents(), Array(3).fill('Bringing in the cover…'), 'the line above each card says what that card waits for');
    assert.equal(await page.locator('.card .shot.ready').count(), 0, 'nothing half-drawn is shown while the covers come');
    assert.equal(await page.locator('#chooseMeta').count(), 0, 'nothing in the head says "ready" for all three while a card is not');
    assert.ok(await page.locator('.card').first().evaluate(c => c.querySelector('.state').getBoundingClientRect().bottom <= c.querySelector('.shot').getBoundingClientRect().top), 'the state stands above its cover');
    st.coverHeld = false; await page.waitForFunction(() => document.querySelectorAll('.card .shot.ready img.cover').length === 3, null, { timeout: 8000 });
    assert.deepEqual(await page.locator('.card .state.ok').allTextContents(), Array(3).fill('Ready'), 'each card says it is ready once its own cover and download are');
    assert.ok(await page.locator('#editGo').isHidden()); await page.locator('.card').nth(0).locator('.pickb').click();
    assert.equal(await page.locator('#editGo').isHidden(), true, 'Edit only once the job kept its data');
    await page.close(); }
  // a site no design fits
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.route('**/*', async r => { const u = new URL(r.request().url());
    if (u.pathname === '/app') return r.fulfill({ contentType: 'text/html', body: html });
    if (u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test'" });
    if (u.pathname === '/js/swarm2.js') return r.fulfill({ contentType: 'application/javascript', body: 'window.Swarm2={mount:()=>({stop(){},phase(){},push(){},setPage(){}})}' });
    if (u.pathname === `/jobs/${id}`) return r.fulfill({ contentType: 'application/json', body: JSON.stringify(publicJob({ id, url: 'https://x.example', status: 'done', created_at: new Date().toISOString(), steps: steps.map(s => ({ ...s, status: 'done' })), result: { templates: { variants: [], rejected: [{ slug: 'griffin', why: 'needs steps; needs features' }, { slug: 'maze', why: 'screens_min 2, the client has 0' }] } } })) });
    return r.abort(); });
  await page.goto(`https://app.test/app?url=x.example&job=${id}`);
  await page.locator('#choose.on').waitFor({ timeout: 10000 });
  assert.equal(await page.locator('.card').count(), 0); assert.match(await page.locator('#chooseH').textContent(), /No design fits/);
  assert.deepEqual(await page.locator('#chooseWhy li').allTextContents(), ['Library design 1: needs steps; needs features', 'Library design 2: screens_min 2, the client has 0']);
  assert.ok(await page.locator('.choose-foot').isHidden());
  await page.close();
  console.log('Chooser 1440/390: engine templates sent, three cards side by side / stacked, full screen, pick, download waits for its package then asks for payment, no fit explained');
} finally { await browser.close(); }
