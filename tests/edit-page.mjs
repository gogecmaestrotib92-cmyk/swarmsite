// The editor on the page (web/edit.html) at 1440 and 390. The server is stubbed, but the page is drawn by the real
// lib/templates/edit.py: a text clicked on the page is rewritten where it stands, a section hidden, a colour chosen,
// another design chosen with every edit kept, Undo, the readability check said in words, and keeping the edits
// asks for an account.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { spawnSync } from 'node:child_process'; import { createRequire } from 'node:module';
const root = process.cwd(), { chromium } = createRequire(path.join(root, 'package.json'))('playwright');
const html = fs.readFileSync(path.join(root, 'web/edit.html'), 'utf8'), id = '66666666-6666-4666-8666-666666666666';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'editpage-')); const data = path.join(tmp, 'd.json'); fs.copyFileSync(path.join(root, 'tests/fixtures/templates/tallyfern.json'), data);
const TPL = { v1: 'griffin', v2: 'maze' };   // what the server keeps behind each design's id
const TITLE = JSON.parse(fs.readFileSync(data, 'utf8')).hero.title;
const edit = (args, ops) => { const o = path.join(tmp, 'o.json'); fs.writeFileSync(o, JSON.stringify(ops || [])); const r = spawnSync(process.env.PYTHON || 'python3', ['lib/templates/edit.py', ...args(o)], { cwd: root, encoding: 'utf8' }); assert.equal(r.status, 0, r.stderr); return r.stdout; };
const until = async (f, what) => { for (let i = 0; i < 150; i++) { if (f()) return; await new Promise(r => setTimeout(r, 100)); } throw new Error('waited in vain for ' + what); };
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  for (const width of [1440, 390]) {
    const state = { renders: [], put: null, landed: '' };
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.route('**/*', async r => { const u = new URL(r.request().url()), m = r.request().method(), body = m === 'GET' ? null : JSON.parse(r.request().postData() || 'null');
      const json = (o, status = 200) => r.fulfill({ status, headers: { 'access-control-allow-origin': '*' }, contentType: 'application/json', body: JSON.stringify(o) });
      if (u.hostname === 'app.test' && u.pathname === '/edit') return r.fulfill({ contentType: 'text/html', body: html });
      if (u.hostname === 'app.test' && u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test'" });
      if (u.hostname === 'app.test' && u.pathname === '/login') { state.landed = u.search; return r.fulfill({ contentType: 'text/html', body: '<p>login</p>' }); }
      if (u.hostname === 'app.test' && u.pathname.startsWith('/vendor/')) return r.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(root, 'web', u.pathname)) });   // the UI SDK's elements (tabs, the dialog), served from the site itself
      if (r.request().headers()['access-control-request-method']) return r.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'POST, PUT' } });
      const t = u.pathname.match(/^\/t\/[0-9a-f-]{36}\/(v[0-9]+)\/(describe|render|check)$/);
      if (u.hostname === 'api.test' && t) { const [, pub, what] = t, slug = TPL[pub], ops = body?.ops ?? [];   // the page speaks of v1, v2; the server of templates
        if (what === 'describe') return json({ ...JSON.parse(edit(o => ['describe', data, '--ops', o, '--slug', slug], ops)), ops: body?.ops ?? [], variants: ['v1', 'v2'] });
        if (what === 'render') { state.renders.push({ slug, ops }); return r.fulfill({ headers: { 'access-control-allow-origin': '*' }, contentType: 'text/html', body: edit(o => ['render', data, slug, '--ops', o, '--base', 'https://storage.example/t/'], ops) }); }
        if (ops.some(o => o.op === 'text' && /Tool down/.test(o.value))) return json({ ok: false, failed: ['tool'], unread: [], overlap: 0, sideways: 0 });
        if (ops.at(-1)?.op === 'palette' && ops.at(-1).ground === '#111111') return json({ ok: false, failed: ['unseen'], unread: [], overlap: 0, sideways: 0 });
        const bad = ops.some(o => o.op === 'text' && /Unreadable/.test(o.value));
        return json(bad ? { ok: false, failed: ['legible'], unread: [{ text: 'Unreadable line here', ratio: 2.1, at: 'm' }], overlap: 0, sideways: 0 } : { ok: true, failed: [], unread: [], overlap: 0, sideways: 0 }); }
      if (u.hostname === 'api.test' && u.pathname === `/t/${id}/edits` && m === 'PUT') { state.put = body; return json({ error: 'Sign in to keep your edits.', login: true }, 401); }
      return r.abort(); });
    await page.goto(`https://app.test/edit?job=${id}&slug=v1`);
    const frame = page.frameLocator('#page');
    await frame.locator('h1').waitFor({ timeout: 15000 });
    await page.waitForFunction(() => /Every line reads/.test(document.querySelector('#status').textContent), null, { timeout: 10000 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth - innerWidth), 0, 'no sideways scroll at ' + width);
    await page.waitForFunction(() => !!customElements.get('ui-tabs') && !!customElements.get('ui-dialog'));
    // "Desktop" is a desk screen: the page is laid out 1440 wide and made smaller to fit, not squeezed into the phone layout
    if (width === 1440) assert.deepEqual(await page.evaluate(() => { const f = document.querySelector('#page'); return [f.contentWindow.innerWidth, f.getBoundingClientRect().right <= innerWidth]; }), [1440, true], 'the desktop view is 1440 wide and fits');
    else assert.ok(await page.evaluate(() => document.querySelector('#page').contentWindow.innerWidth <= 390), 'on a phone the page is the phone\'s width');
    // a text clicked on the page is rewritten where it stands
    await frame.locator('h1').click();
    assert.equal(await frame.locator('[contenteditable="plaintext-only"]').count(), 1, 'the clicked text is editable in place');
    await page.keyboard.press('ControlOrMeta+a'); await page.keyboard.type('Closed by six, every evening'); await page.keyboard.press('Enter');
    await page.waitForFunction(() => document.querySelector('#page').contentDocument?.querySelector('h1')?.textContent.includes('Closed by six'), null, { timeout: 10000 });
    assert.deepEqual(state.renders.at(-1).ops, [{ op: 'text', path: 'hero.title', value: 'Closed by six, every evening' }]);
    // the place on the page is kept when it is drawn again
    { await page.waitForTimeout(1400); const y0 = await page.evaluate(() => { const w = document.querySelector('#page').contentWindow; w.scrollTo(0, 900); return w.scrollY; }); await page.waitForTimeout(200);
      await page.locator('.tabs [data-tab="sections"]').click(); await page.locator('#blocks label', { hasText: /^Links$/ }).locator('input').uncheck(); await until(() => state.renders.at(-1).ops.some(o => o.op === 'hide' && o.block === 'links'), 'the section to be left out'); await page.waitForTimeout(1800);
      const y1 = await page.evaluate(() => document.querySelector('#page').contentWindow.scrollY); assert.ok(y0 > 300 && Math.abs(y1 - y0) < 40, `the page stays where the visitor was after an edit: ${y0} → ${y1}`);
      await page.locator('#undo').click(); await until(() => !state.renders.at(-1).ops.some(o => o.op === 'hide'), 'the section back'); await page.evaluate(() => document.querySelector('#page').contentWindow.scrollTo(0, 0)); await page.locator('.tabs [data-tab="text"]').click(); if (width < 900 && await page.locator('#panel.open').count()) await page.locator('.tabs [data-tab="text"]').click(); }
    // the tabs answer the keyboard as tabs do: one tab stop, the arrows move and choose
    if (width === 1440) { await page.locator('.tabs [data-tab="text"]').focus(); await page.keyboard.press('ArrowRight'); assert.equal(await page.locator('[data-pane]:not([hidden])').getAttribute('data-pane'), 'pictures', 'Right Arrow chooses the next tab'); assert.deepEqual(await page.locator('.tabs button').evaluateAll(bs => bs.map(b => b.tabIndex)), [-1, 0, -1, -1]); await page.keyboard.press('ArrowLeft'); }
    // the panel shows one thing at a time: four tabs, and the texts as a short list of the page's parts, the clicked one opened
    assert.deepEqual(await page.locator('.tabs [role=tab]').allTextContents(), ['Text', 'Pictures', 'Colours', 'Sections']);
    assert.equal(await page.locator('[data-pane]:not([hidden])').count(), 1, 'one pane at a time');
    assert.deepEqual(await page.locator('#fields details[open]').evaluateAll(ds => ds.map(d => d.dataset.block)), ['hero'], 'the part whose text was clicked is the one open');
    assert.ok(await page.locator('#fields details').count() >= 5 && await page.locator('#fields details').count() <= 24, 'the texts are grouped by part of the page');
    assert.ok(await page.evaluate(() => document.documentElement.scrollHeight <= innerHeight + 1), 'the editor itself never scrolls: the page and the panel do, each in its place');
    const cols = await page.evaluate(() => ({ shown: [...document.querySelectorAll('#fields textarea')].filter(t => t.checkVisibility()).length, all: document.querySelectorAll('#fields textarea').length, open: document.querySelectorAll('#fields details[open] textarea').length }));
    assert.ok(cols.shown < cols.all / 2 && cols.shown === (width > 900 ? cols.open : 0), JSON.stringify(cols) + ' at ' + width + ': ' + 'no long column of every text: only the open part shows its fields, and on a phone the sheet stays down while a text is typed on the page');
    assert.ok(await page.locator('#publish').count() === 0 && await page.locator('#prepare').isHidden() && await page.locator('#pubOpen').isVisible(), 'the download waits behind its one button');
    assert.equal(await page.locator('#pubOpen').textContent(), 'Download'); await page.locator('#pubOpen').click(); assert.ok(await page.locator('#prepare').isVisible() && await page.locator('#onlineStep').count() === 0 && !/publish|online|swarmsite\.si/i.test(await page.locator('#pubSheet').innerText()), 'the interface offers the download only: nothing about publishing is shown'); await page.locator('#pubClose').click();
    // a section hidden; a colour chosen; the panel's text field follows the page
    await page.locator('.tabs [data-tab="sections"]').click();
    await page.locator('#blocks label', { hasText: /^Questions$/ }).locator('input').uncheck();
    await page.waitForFunction(() => document.querySelectorAll('#blocks input:not(:checked)').length === 1);
    await page.locator('.tabs [data-tab="colours"]').click(); await page.locator('#palettes button').first().click();
    await until(() => state.renders.at(-1).ops.some(o => o.op === 'palette'), 'the colour to be rendered');
    const last = state.renders.at(-1).ops;
    assert.deepEqual(last.map(o => o.op), ['text', 'hide', 'palette']);
    assert.equal(await page.locator('#fields textarea').evaluateAll(ts => ts.find(t => t.closest('.f').dataset.path === 'hero.title')?.value), 'Closed by six, every evening');
    // a colour that does not hold is said as that, with a way back; a check that could not run is not said as the visitor's fault
    await page.locator('#palettes button[aria-label="Colours: ink"]').click(); await page.waitForFunction(() => /This colour does not hold/.test(document.querySelector('#status').textContent), null, { timeout: 10000 });
    assert.match(await page.locator('#unread').textContent(), /can no longer be seen/); await page.locator('#takeBack').click(); await until(() => state.renders.at(-1).ops.at(-1)?.ground !== '#111111', 'the colour taken back');
    await page.waitForFunction(() => /Every line reads/.test(document.querySelector('#status').textContent), null, { timeout: 10000 });
    // another design: every edit kept
    await page.locator('#designs button', { hasText: 'Design 2' }).click();
    await page.waitForFunction(() => document.querySelector('#page').contentDocument?.body?.textContent.includes('Closed by six'), null, { timeout: 10000 });
    assert.equal(state.renders.at(-1).slug, 'maze'); assert.deepEqual(state.renders.at(-1).ops, last);
    assert.ok(page.url().includes('slug=v2'));
    // Undo returns to the state before the last edit
    const n = state.renders.length; await page.locator('#undo').click();
    await until(() => state.renders.length > n, 'the page after Undo');
    assert.deepEqual((state.renders.at(-1).ops).map(o => o.op), ['text', 'hide']);
    // a line that no longer reads is named, with what to change
    await page.locator('.tabs [data-tab="text"]').click(); if (!(await page.locator('#fields details[data-block="hero"]').evaluate(d => d.open))) await page.locator('#fields details[data-block="hero"] > summary').click();
    const ta = page.locator('#fields .f[data-path="hero.title"] textarea'); await ta.fill('Unreadable on purpose'); await ta.blur();
    await page.waitForFunction(() => !document.querySelector('#unread').hidden, null, { timeout: 10000 });
    assert.match(await page.locator('#unread').textContent(), /reads at 2\.1:1 on a phone\. Choose another colour, or another picture/);
    await ta.fill('Tool down'); await ta.blur(); await page.waitForFunction(() => /could not run this time/.test(document.querySelector('#status').textContent), null, { timeout: 10000 });
    assert.ok(await page.locator('#unread').isHidden() && !(await page.locator('#status').getAttribute('class')).includes('bad'), 'a check that could not run names no line and blames no edit');
    await ta.fill('Unreadable on purpose'); await ta.blur(); await page.waitForFunction(() => !document.querySelector('#unread').hidden, null, { timeout: 10000 });
    // a picture is chosen from the visitor's own, shown as pictures
    await page.locator('.tabs [data-tab="pictures"]').click(); if (width < 900 && !(await page.locator('#panel.open').count())) await page.locator('.tabs [data-tab="pictures"]').click();
    if (await page.locator('#slots .slot').count()) { await page.locator('#slots .slot > button').first().click(); const picks = page.locator('#slots .picks button'); assert.ok(await picks.count() >= 1, 'a place opened shows the pictures to choose from');
      const other = page.locator('#slots .picks button[aria-pressed="false"]').first(); if (await other.count()) { const src = await other.getAttribute('data-src'); await other.click(); await until(() => state.renders.at(-1).ops.some(o => o.op === 'picture' && o.src === src), 'the picture to be drawn'); } }
    // keeping the edits needs an account: the visitor is sent to sign in, the edits wait for them
    await page.locator('#save').click();
    await page.waitForFunction(() => location.pathname === '/login', null, { timeout: 10000 });
    assert.ok(state.put && state.put.ops.some(o => o.value === 'Unreadable on purpose')); assert.match(decodeURIComponent(state.landed), /next=\/edit\?job=.*slug=v2/);
    await page.close();
  }
  // publishing is built and not offered (2026-11-13): it shows only where config.js switches it on, as here.
  // Signed in: the edits are kept first, then the site; only a state written after this start counts
  { const state = { put: 0, published: null, polls: 0 }; const t0 = new Date(Date.now() - 60e3).toISOString(), later = () => new Date(Date.now() + 1000).toISOString();
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    await page.route('**/*', async r => { const u = new URL(r.request().url()), m = r.request().method(), body = m === 'GET' ? null : JSON.parse(r.request().postData() || 'null');
      const json = (o, status = 200) => r.fulfill({ status, headers: { 'access-control-allow-origin': '*' }, contentType: 'application/json', body: JSON.stringify(o) });
      if (u.hostname === 'app.test' && u.pathname === '/edit') return r.fulfill({ contentType: 'text/html', body: html });
      if (u.hostname === 'app.test' && u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test';window.SWARMSITE_PUBLISH=true" });
      if (u.hostname === 'app.test' && u.pathname.startsWith('/vendor/')) return r.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(root, 'web', u.pathname)) });   // the UI SDK's elements (tabs, the dialog), served from the site itself
      if (r.request().headers()['access-control-request-method']) return r.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'POST, PUT' } });
      const t = u.pathname.match(/^\/t\/[0-9a-f-]{36}\/(v[0-9]+)\/(describe|render|check)$/);
      if (t) { const [, pub, what] = t, slug = TPL[pub], ops = body?.ops ?? [];
        if (what === 'describe') return json({ ...JSON.parse(edit(o => ['describe', data, '--ops', o, '--slug', slug], ops)), ops: body?.ops ?? [], variants: ['v1'] });
        if (what === 'render') return r.fulfill({ headers: { 'access-control-allow-origin': '*' }, contentType: 'text/html', body: edit(o => ['render', data, slug, '--ops', o], ops) });
        return json({ ok: true, failed: [], unread: [], overlap: 0, sideways: 0 }); }
      if (u.pathname === `/t/${id}/edits`) { state.put++; return json({ kept: body.ops.length }); }
      if (u.pathname === `/t/${id}/v1/publish`) { state.published = body; return json({ status: 'packaging', name: body.name, at: new Date().toISOString() }, 202); }
      if (u.pathname === `/t/${id}/v1/prepare`) { state.prepared = later(); return json({ status: 'packaging', at: state.prepared }, 202); }
      if (u.pathname === `/t/${id}/v1/package`) { state.asked = u.search; return json({ url: 'https://files.test/signed/design-1.zip?token=t', name: 'casa-fern-design-1.zip' }); }
      if (u.hostname === 'files.test') return r.fulfill({ contentType: 'application/zip', headers: { 'content-disposition': 'attachment; filename="casa-fern-design-1.zip"' }, body: Buffer.from('PK\u0005\u0006' + '\u0000'.repeat(18), 'latin1') });
      if (u.pathname === `/jobs/${id}` && state.prepared) return json({ id, status: 'done', result: { edited: { status: 'ready', slug: 'v1', at: state.prepared } } });
      if (u.pathname === `/jobs/${id}`) { state.polls++; return json({ id, status: 'done', result: { publish: state.polls < 2 ? { status: 'live', slug: 'v1', name: 'old', url: 'https://old.swarmsite.si', at: t0 } : state.polls < 3 ? { status: 'packaging', slug: 'v1', at: later() } : { status: 'live', slug: 'v1', name: 'casa-fern', url: 'https://casa-fern.swarmsite.si', at: later() } } }); }
      return r.abort(); });
    await page.goto(`https://app.test/edit?job=${id}&slug=v1`);
    await page.frameLocator('#page').locator('h1').waitFor({ timeout: 15000 });
    await page.locator('#fields details[data-block="hero"] > summary').click();
    const ta = page.locator('#fields .f[data-path="hero.title"] textarea'); await ta.fill('Closed by six'); await ta.blur();
    await page.locator('#pubOpen').click(); assert.ok(await page.locator('#pubSheet').isVisible() && await page.locator('#payGo').isHidden() && await page.locator('#getZip').isHidden(), 'the steps open; nothing is offered before it applies'); assert.equal(await page.locator('#pubOpen').textContent(), 'Publish or download');
    await page.locator('#siteName').fill('Casa Fern'); await page.locator('#publish').click();
    assert.match(await page.locator('#pubStatus').textContent(), /3 to 40 small letters/); assert.equal(state.published, null, 'a bad name is not sent');
    await page.locator('#siteName').fill('casa-fern'); await page.locator('#publish').click();
    await page.locator('#siteLink:not([hidden])').waitFor({ timeout: 20000 });
    assert.equal(await page.locator('#siteLink').getAttribute('href'), 'https://casa-fern.swarmsite.si', 'the old site of an earlier publish is not taken for this one');
    assert.deepEqual(state.published, { name: 'casa-fern' }); assert.equal(state.put, 1, 'the edits were kept before publishing');
    // the download: prepared, then fetched by the browser itself from the address the server hands out; the line says
    // it has started and keeps that address as a link (a phone ignores bytes a page hands it after a wait)
    await page.locator('#prepare').click(); await page.locator('#getZip:not([hidden])').waitFor({ timeout: 20000 });
    const dl = page.waitForEvent('download', { timeout: 10000 }); await page.locator('#getZip').click(); const got = await dl;
    assert.equal(got.suggestedFilename(), 'casa-fern-design-1.zip'); assert.equal(state.asked, '?link=1');
    await page.waitForFunction(() => /Your download has started/.test(document.querySelector('#pubStatus').textContent));
    assert.equal(await page.locator('#pubStatus #zipLink').getAttribute('href'), 'https://files.test/signed/design-1.zip?token=t'); assert.ok(await page.locator('#pubSheet').isVisible(), 'the editor is still there');
    await page.close(); }
  console.log('Edit page 1440/390: text edited where it stands, a section hidden, a colour, another design keeping every edit, Undo, an unreadable line named, keeping asks for an account; publish keeps the edits first and shows the new address; the download is fetched by the browser from the address handed out');
} finally { await browser.close(); fs.rmSync(tmp, { recursive: true, force: true }); }
