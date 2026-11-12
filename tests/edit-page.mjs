// The editor on the page (web/edit.html) at 1440 and 390. The server is stubbed, but the page is drawn by the real
// lib/templates/edit.py: a text clicked on the page is rewritten where it stands, a section hidden, a colour chosen,
// another design chosen with every edit kept, Undo, the readability check said in words, and keeping the edits
// asks for an account.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { spawnSync } from 'node:child_process'; import { createRequire } from 'node:module';
const root = process.cwd(), { chromium } = createRequire(path.join(root, 'package.json'))('playwright');
const html = fs.readFileSync(path.join(root, 'web/edit.html'), 'utf8'), id = '66666666-6666-4666-8666-666666666666';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'editpage-')); const data = path.join(tmp, 'd.json'); fs.copyFileSync(path.join(root, 'tests/fixtures/templates/tallyfern.json'), data);
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
      if (r.request().headers()['access-control-request-method']) return r.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'POST, PUT' } });
      const t = u.pathname.match(/^\/t\/[0-9a-f-]{36}\/([a-z]+)\/(describe|render|check)$/);
      if (u.hostname === 'api.test' && t) { const [, slug, what] = t, ops = body?.ops ?? [];
        if (what === 'describe') return json({ ...JSON.parse(edit(o => ['describe', data, '--ops', o, '--slug', slug], ops)), ops: body?.ops ?? [], variants: ['griffin', 'maze'] });
        if (what === 'render') { state.renders.push({ slug, ops }); return r.fulfill({ headers: { 'access-control-allow-origin': '*' }, contentType: 'text/html', body: edit(o => ['render', data, slug, '--ops', o, '--base', 'https://storage.example/t/'], ops) }); }
        const bad = ops.some(o => o.op === 'text' && /Unreadable/.test(o.value));
        return json(bad ? { ok: false, failed: ['legible'], unread: [{ text: 'Unreadable line here', ratio: 2.1, at: 'm' }], overlap: 0, sideways: 0 } : { ok: true, failed: [], unread: [], overlap: 0, sideways: 0 }); }
      if (u.hostname === 'api.test' && u.pathname === `/t/${id}/edits` && m === 'PUT') { state.put = body; return json({ error: 'Sign in to keep your edits.', login: true }, 401); }
      return r.abort(); });
    await page.goto(`https://app.test/edit?job=${id}&slug=griffin`);
    const frame = page.frameLocator('#page');
    await frame.locator('h1').waitFor({ timeout: 15000 });
    await page.waitForFunction(() => /Every line reads/.test(document.querySelector('#status').textContent), null, { timeout: 10000 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth - innerWidth), 0, 'no sideways scroll at ' + width);
    // a text clicked on the page is rewritten where it stands
    await frame.locator('h1').click();
    assert.equal(await frame.locator('[contenteditable="plaintext-only"]').count(), 1, 'the clicked text is editable in place');
    await page.keyboard.press('ControlOrMeta+a'); await page.keyboard.type('Closed by six, every evening'); await page.keyboard.press('Enter');
    await page.waitForFunction(() => document.querySelector('#page').contentDocument?.querySelector('h1')?.textContent.includes('Closed by six'), null, { timeout: 10000 });
    assert.deepEqual(state.renders.at(-1).ops, [{ op: 'text', path: 'hero.title', value: 'Closed by six, every evening' }]);
    // a section hidden; a colour chosen; the panel's text field follows the page
    await page.locator('#blocks label', { hasText: /^Questions$/ }).locator('input').uncheck();
    await page.waitForFunction(() => document.querySelectorAll('#blocks input:not(:checked)').length === 1);
    await page.locator('#palettes button').first().click();
    await until(() => state.renders.at(-1).ops.some(o => o.op === 'palette'), 'the colour to be rendered');
    const last = state.renders.at(-1).ops;
    assert.deepEqual(last.map(o => o.op), ['text', 'hide', 'palette']);
    assert.equal(await page.locator('#fields textarea').evaluateAll(ts => ts.find(t => t.closest('.f').dataset.path === 'hero.title')?.value), 'Closed by six, every evening');
    // another design: every edit kept
    await page.locator('#designs button', { hasText: 'Studio' }).click();
    await page.waitForFunction(() => document.querySelector('#page').contentDocument?.body?.textContent.includes('Closed by six'), null, { timeout: 10000 });
    assert.equal(state.renders.at(-1).slug, 'maze'); assert.deepEqual(state.renders.at(-1).ops, last);
    assert.ok(page.url().includes('slug=maze'));
    // Undo returns to the state before the last edit
    const n = state.renders.length; await page.locator('#undo').click();
    await until(() => state.renders.length > n, 'the page after Undo');
    assert.deepEqual((state.renders.at(-1).ops).map(o => o.op), ['text', 'hide']);
    // a line that no longer reads is named, with what to change
    const ta = page.locator('#fields .f[data-path="hero.title"] textarea'); await ta.fill('Unreadable on purpose'); await ta.blur();
    await page.waitForFunction(() => !document.querySelector('#unread').hidden, null, { timeout: 10000 });
    assert.match(await page.locator('#unread').textContent(), /reads at 2\.1:1 on a phone\. Choose another colour, or another picture/);
    // keeping the edits needs an account: the visitor is sent to sign in, the edits wait for them
    await page.locator('#save').click();
    await page.waitForFunction(() => location.pathname === '/login', null, { timeout: 10000 });
    assert.ok(state.put && state.put.ops.some(o => o.value === 'Unreadable on purpose')); assert.match(decodeURIComponent(state.landed), /next=\/edit\?job=.*slug=maze/);
    await page.close();
  }
  // publishing, signed in: the edits are kept first, then the site; only a state written after this start counts
  { const state = { put: 0, published: null, polls: 0 }; const t0 = new Date(Date.now() - 60e3).toISOString(), later = () => new Date(Date.now() + 1000).toISOString();
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    await page.route('**/*', async r => { const u = new URL(r.request().url()), m = r.request().method(), body = m === 'GET' ? null : JSON.parse(r.request().postData() || 'null');
      const json = (o, status = 200) => r.fulfill({ status, headers: { 'access-control-allow-origin': '*' }, contentType: 'application/json', body: JSON.stringify(o) });
      if (u.hostname === 'app.test' && u.pathname === '/edit') return r.fulfill({ contentType: 'text/html', body: html });
      if (u.hostname === 'app.test' && u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test'" });
      if (r.request().headers()['access-control-request-method']) return r.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'POST, PUT' } });
      const t = u.pathname.match(/^\/t\/[0-9a-f-]{36}\/([a-z]+)\/(describe|render|check)$/);
      if (t) { const [, slug, what] = t, ops = body?.ops ?? [];
        if (what === 'describe') return json({ ...JSON.parse(edit(o => ['describe', data, '--ops', o, '--slug', slug], ops)), ops: body?.ops ?? [], variants: ['griffin'] });
        if (what === 'render') return r.fulfill({ headers: { 'access-control-allow-origin': '*' }, contentType: 'text/html', body: edit(o => ['render', data, slug, '--ops', o], ops) });
        return json({ ok: true, failed: [], unread: [], overlap: 0, sideways: 0 }); }
      if (u.pathname === `/t/${id}/edits`) { state.put++; return json({ kept: body.ops.length }); }
      if (u.pathname === `/t/${id}/griffin/publish`) { state.published = body; return json({ status: 'packaging', name: body.name, at: new Date().toISOString() }, 202); }
      if (u.pathname === `/jobs/${id}`) { state.polls++; return json({ id, status: 'done', result: { publish: state.polls < 2 ? { status: 'live', slug: 'griffin', name: 'old', url: 'https://old.swarmsite.si', at: t0 } : state.polls < 3 ? { status: 'packaging', slug: 'griffin', at: later() } : { status: 'live', slug: 'griffin', name: 'casa-fern', url: 'https://casa-fern.swarmsite.si', at: later() } } }); }
      return r.abort(); });
    await page.goto(`https://app.test/edit?job=${id}&slug=griffin`);
    await page.frameLocator('#page').locator('h1').waitFor({ timeout: 15000 });
    const ta = page.locator('#fields .f[data-path="hero.title"] textarea'); await ta.fill('Closed by six'); await ta.blur();
    await page.locator('#siteName').fill('Casa Fern'); await page.locator('#publish').click();
    assert.match(await page.locator('#pubStatus').textContent(), /3 to 40 small letters/); assert.equal(state.published, null, 'a bad name is not sent');
    await page.locator('#siteName').fill('casa-fern'); await page.locator('#publish').click();
    await page.locator('#siteLink:not([hidden])').waitFor({ timeout: 20000 });
    assert.equal(await page.locator('#siteLink').getAttribute('href'), 'https://casa-fern.swarmsite.si', 'the old site of an earlier publish is not taken for this one');
    assert.deepEqual(state.published, { name: 'casa-fern' }); assert.equal(state.put, 1, 'the edits were kept before publishing');
    await page.close(); }
  console.log('Edit page 1440/390: text edited where it stands, a section hidden, a colour, another design keeping every edit, Undo, an unreadable line named, keeping asks for an account; publish keeps the edits first and shows the new address');
} finally { await browser.close(); fs.rmSync(tmp, { recursive: true, force: true }); }
