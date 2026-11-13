// "A site from nothing" (web/start.html): a few short steps, one on the screen at once, no chat. The visitor types what is true, adds photographs with one
// answer each, and lands in the chooser; the photographs go up one by one, then a template job with the form as its data.
// Nothing is sent that the visitor did not fill in; the name alone is enough. At 1440 and 390, with the server stubbed.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module';
const root = process.cwd(), { chromium } = createRequire(path.join(root, 'package.json'))('playwright');
const html = fs.readFileSync(path.join(root, 'web/start.html'), 'utf8'), id = '44444444-4444-4444-8444-444444444444';
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  for (const width of [1440, 390]) {
    const state = { uploads: [], job: null, landed: '' };
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route('**/*', async r => { const u = new URL(r.request().url()), m = r.request().method();
      if (u.hostname === 'app.test' && u.pathname === '/start') return r.fulfill({ contentType: 'text/html', body: html });
      if (u.hostname === 'app.test' && u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test'" });
      if (u.hostname === 'app.test' && u.pathname === '/app') { state.landed = u.search; return r.fulfill({ contentType: 'text/html', body: '<p>chooser</p>' }); }
      if (u.hostname === 'app.test' && u.pathname.startsWith('/fonts/')) return r.fulfill({ status: 404, body: '' });
      if (r.request().headers()['access-control-request-method']) return r.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'POST' } });
      if (u.hostname === 'api.test' && u.pathname === '/uploads' && m === 'POST') { const b = r.request().postDataBuffer(); state.uploads.push({ type: r.request().headers()['content-type'], bytes: b ? b.length : 0 });
        return r.fulfill({ headers: { 'access-control-allow-origin': '*' }, contentType: 'application/json', body: JSON.stringify({ file: `0b1e2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c${String(state.uploads.length).padStart(2, '0')}.jpg` }) }); }
      if (u.hostname === 'api.test' && u.pathname === '/jobs' && m === 'POST') { state.job = JSON.parse(r.request().postData()); return r.fulfill({ headers: { 'access-control-allow-origin': '*' }, contentType: 'application/json', body: JSON.stringify({ id }) }); }
      return r.abort(); });
    await page.goto('https://app.test/start');
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth - innerWidth), 0, 'no sideways scroll at ' + width);
    // the name is needed: nothing is sent without it
    assert.equal(await page.locator('.step:not([hidden])').count(), 1, 'one step on the screen'); assert.ok(await page.locator('#go').isHidden(), 'the last button waits for the last step');
    await page.locator('#next').click();
    assert.match(await page.locator('#status').textContent(), /name of the business is needed/); assert.equal(state.uploads.length + (state.job ? 1 : 0), 0); assert.equal(await page.locator('.step:not([hidden])').getAttribute('data-step'), '1', 'no further without a name');
    await page.locator('#name').fill('Casa Fern'); await page.locator('#sentence').fill('Rice dishes cooked over wood, by the river');
    if (width > 700) await page.locator('#kinds label', { hasText: 'Restaurant, café or bar' }).click(); else await page.locator('#kind').selectOption('restaurant');   // chips on a desk, the phone's own list on a phone
    assert.equal(await page.locator('#sentence').getAttribute('placeholder'), 'Rice dishes cooked over wood, by the river', 'the kind shapes the examples');
    // step 3 first here (what you offer), then back to the photographs: the steps can be taken in any order
    await page.locator('#next').click(); assert.equal(await page.locator('#next').textContent(), 'Skip this →', 'an empty step can be passed, and says so'); await page.locator('#next').click();
    assert.equal(await page.locator('#offers .offer label').first().evaluate(l => l.firstChild.textContent), 'Dish or drink', 'a restaurant is asked for dishes');
    await page.locator('#offers .o-name').first().fill('Arroz negro'); await page.locator('#offers .o-price').first().fill('18 €');
    await page.locator('#moreSteps > summary').click(); await page.locator('#addStep').click(); await page.locator('#steps .s-title').first().fill('Book a table');
    await page.locator('#back').click();
    await page.locator('#files').setInputFiles([path.join(root, 'web/before-960.webp'), path.join(root, 'web/after-960.webp')]);
    await page.locator('.ph').nth(1).waitFor();
    assert.equal(await page.locator('.ph').count(), 2);
    const opts = await page.locator('.ph .with').first().locator('option').allTextContents();
    assert.deepEqual(opts, ['Goes with… (optional)', 'Arroz negro', 'Step: Book a table'], 'a photograph can go with a line of the offer or a step');
    await page.locator('.ph .role').nth(0).selectOption('dish'); await page.locator('.ph .with').nth(0).selectOption('o0'); await page.locator('.ph .alt').nth(0).fill('Black rice in the pan');
    await page.locator('.ph .role').nth(1).selectOption('room');
    await page.locator('#next').click(); await page.locator('#next').click();
    assert.ok(await page.locator('#morePlace').evaluate(d => d.open), 'a restaurant is a place: its address and hours are open');
    await page.locator('#linkT').fill('Book a table'); await page.locator('#linkH').fill('casafern.example/book');
    await page.locator('#city').fill('Valencia'); await page.locator('#addHours').click();
    await page.locator('#hours .h-days').fill('Tue–Sun'); await page.locator('#hours .h-open').fill('13:00'); await page.locator('#hours .h-close').fill('23:00');
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth - innerWidth), 0, 'still no sideways scroll with every row added at ' + width);
    await page.locator('#next').click();
    const will = await page.locator('#haveEnd li').allTextContents();
    assert.deepEqual(will, ['Your name: Casa Fern', 'A first line, in your words', '2 photographs of yours', '1 line of what you offer', '1 step of how it works', 'A button: “Book a table”', 'Your address', 'Opening hours'], 'the last step says what the page will have, and only that');
    await page.locator('#go').click();
    await page.waitForFunction(() => location.pathname === '/app', null, { timeout: 15000 });
    assert.equal(state.landed, `?job=${id}`, 'the visitor lands in the chooser of their job');
    assert.equal(state.uploads.length, 2); assert.ok(state.uploads.every(u => /^image\/(jpeg|png|webp)$/.test(u.type) && u.bytes > 1000), JSON.stringify(state.uploads));
    const j = state.job; assert.deepEqual(j.options, { engine: 'templates', source: 'form' }); assert.equal(j.url, undefined, 'no address: the form is the site');
    const f = j.form;
    assert.equal(f.name, 'Casa Fern'); assert.equal(f.kind, 'restaurant'); assert.equal(f.accent, undefined, 'no colour unless they say they have one');
    assert.deepEqual(f.offers, [{ name: 'Arroz negro', price: '18 €', note: '' }]); assert.deepEqual(f.steps, [{ title: 'Book a table', text: '' }]); assert.deepEqual(f.figures, []);
    assert.deepEqual(f.photos.map(p => [p.role, p.offer, p.alt]), [['dish', 0, 'Black rice in the pan'], ['room', undefined, '']]);
    assert.ok(f.photos.every(p => /\.jpg$/.test(p.file)), 'each photograph is named by what the server gave back for it');
    assert.deepEqual(f.link, { t: 'Book a table', h: 'casafern.example/book' }); assert.deepEqual(f.contact.hours, [{ days: 'Tue–Sun', open: '13:00', close: '23:00' }]); assert.equal(f.contact.city, 'Valencia');
    await page.close();
  }
  console.log('Start form 1440/390: one step at a time, name required, the kind shapes what is asked, what the page will have is said before it is made, photographs sent one by one with their answer and pairing, the form as the job, the visitor lands in the chooser');
} finally { await browser.close(); }
