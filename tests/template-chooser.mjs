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
      if (u.hostname === 'api.test' && /^\/t\/[^/]+\/[a-z0-9]+\/package$/.test(u.pathname)) { state.asked.push(u.pathname); return r.fulfill({ status: 402, contentType: 'application/json', body: JSON.stringify({ error: 'Payment is needed', pay: true }) }); }
      if (u.hostname === 'api.test' && u.pathname.startsWith(`/t/${id}/`)) return r.fulfill({ contentType: 'text/html', body: `<!doctype html><body style="margin:0;font:40px Arial"><h1>${u.pathname.split('/').pop()}</h1><p style="height:2000px">page</p></body>` });
      return r.abort(); });
    await page.goto('https://app.test/app?url=tallyfern.example');
    await page.locator('#go').click();
    await page.locator('#choose.on').waitFor({ timeout: 10000 });
    assert.equal(state.posted?.options?.engine, 'templates', 'the job asks for the template path where the server has it on');
    assert.equal(state.posted.options.mode, 'seo-safe', 'the brief keeps its own SEO choice');
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
    assert.deepEqual(state.asked, [`/t/${id}/v2/package`], 'the download asks the package endpoint, which answers with the payment hook');
    await page.locator('.card').nth(2).locator('.pickb').click(); assert.ok(await page.locator('#download').isDisabled() && /did not match the preview/.test(await page.locator('#chooseNote').textContent()));
    await page.locator('.card').nth(0).locator('.pickb').click(); assert.ok(await page.locator('#download').isDisabled() && /being prepared/.test(await page.locator('#chooseNote').textContent()));
    // the job finishes: the package that was being prepared is ready, the choice is kept, the cards are not rebuilt
    const before = await page.locator('.card .shot iframe').first().evaluate(f => f.dataset.stamp = 'kept');
    state.job = { ...state.job, status: 'done', steps: steps.map(s => ({ ...s, status: 'done' })), result: { ...state.job.result, seconds: 74, templates: { ...state.job.result.templates, variants: [variant('griffin', 'ready', 0), variant('maze', 'ready', 1), variant('cerebrium', 'refused', 2)] } } };
    await page.waitForFunction(() => !document.querySelector('#download').disabled, null, { timeout: 8000 });
    assert.equal(await page.locator('.card.picked').getAttribute('data-slug'), 'v1');
    assert.equal(await page.locator('.card .shot iframe').first().evaluate(f => f.dataset.stamp), 'kept', 'the previews are not reloaded on every poll');
    assert.ok(!(await page.locator('#result.on').count()), 'the old single-preview view stays out of the way');
    await page.close();
  }
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
