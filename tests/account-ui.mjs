/* The pages of an account, in a browser, against a stand-in for Supabase and for our API:
   - without accounts configured, the sign-in page says so and the dashboard does not pretend;
   - the dashboard sends a visitor who is not signed in to /login and comes back afterwards;
   - signed in, it lists the visitor's projects with the token attached, and a site's address is text, never markup;
   - a "next" that points at another site is ignored;
   - a project is started on the dashboard itself, and the form without an address leads there (to the front page when
     nobody is signed in) — "Start a project" once led a signed-in visitor back to the landing page;
   - one header on the form, the dashboard and the sign-in page: what it offers follows from who is looking, the account
     panel opens and closes by pointer and by keyboard, and nothing in it leaves the screen on a phone;
   - the front page gets its account link from one tag, and fetches the account library only for a browser that holds a session. */
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module';
const root = process.cwd(), { chromium } = createRequire(path.join(root, 'package.json'))('playwright');
const file = name => fs.readFileSync(path.join(root, 'web', name), 'utf8');
const stub = signedIn => `window.__calls=[];window.supabase={createClient:(url,key)=>({auth:{
  getSession:async()=>({data:{session:${signedIn ? "{access_token:'tok-" + 'x'.repeat(30) + "',user:{email:'person@example.com'}}" : 'null'}}}),
  onAuthStateChange:()=>{}, signOut:async()=>{window.__calls.push(['out'])},
  signInWithOtp:async a=>{window.__calls.push(['otp',a]);return {error:null}}, signInWithOAuth:async a=>{window.__calls.push(['oauth',a]);return {error:null}}}})};`;
const jobs = [{ id: '11111111-1111-4111-8111-111111111111', url: 'https://www.river.test/', status: 'done', created_at: '2026-11-11T10:00:00Z', designs: 3, before: 'https://cdn.test/b.jpg' },
  { id: '22222222-2222-4222-8222-222222222222', url: 'https://x.test/"><img src=x onerror=window.__pwned=1>', status: 'failed', created_at: '2026-11-10T10:00:00Z', designs: 0, before: null }];
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
async function open(pagePath, { configured = true, signedIn = false, methods = "['github','google','email']", width = 1280, held = signedIn } = {}) {
  const page = await browser.newPage({ viewport: { width, height: 900 } }); const seen = { auth: [], gone: [], lib: 0 };
  if (held) await page.addInitScript(() => { try { localStorage.setItem('sb-test-auth-token', '{}'); } catch {} });   // what supabase-js leaves in a browser that has signed in
  await page.route('**/*', async r => { const q = r.request(), u = new URL(q.url());
    if (u.hostname === 'cdn.jsdelivr.net') seen.lib++;
    if (u.hostname === 'cdn.jsdelivr.net') return r.fulfill({ contentType: 'application/javascript', body: stub(signedIn) });
    if (u.hostname === 'api.test') { seen.auth.push(q.headers().authorization || ''); if (!signedIn) return r.fulfill({ status: 401, contentType: 'application/json', body: '{"error":"sign in"}' });
      return r.fulfill({ contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(u.pathname === '/me' ? { id: 'u1', email: 'person@example.com', previews: { used: 2, free: 3, left: 1, allowed: true } } : jobs) }); }
    if (u.hostname !== 'app.test') return r.fulfill({ status: 204, body: '' });
    if (u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: `window.SWARMSITE_API='https://api.test';window.SWARMSITE_SUPABASE=${configured ? "{url:'https://sb.test',anon:'public-anon-key'}" : "{url:'',anon:''}"};window.SWARMSITE_LOGIN=${methods};` });
    if (u.pathname === '/js/auth.js') return r.fulfill({ contentType: 'application/javascript', body: file('js/auth.js') });
    if (u.pathname === '/login') return r.fulfill({ contentType: 'text/html', body: file('login.html') });
    if (u.pathname === '/dashboard') return r.fulfill({ contentType: 'text/html', body: file('dashboard.html') });
    if (u.pathname === '/header.css') return r.fulfill({ contentType: 'text/css', body: file('header.css') });
    if (u.pathname.startsWith('/js/')) { try { return r.fulfill({ contentType: 'application/javascript', body: file(u.pathname.slice(1)) }); } catch { return r.fulfill({ status: 204, body: '' }); } }
    seen.gone.push(u.pathname + u.search);
    if (u.pathname === '/app') return r.fulfill({ contentType: 'text/html', body: file('app.html') });
    if (u.pathname === '/') return r.fulfill({ contentType: 'text/html', body: file('index.html') });
    return r.fulfill({ contentType: 'text/html', body: '<title>elsewhere</title>' }); });
  const errors = []; page.on('pageerror', e => errors.push(String(e)));
  await page.goto('https://app.test' + pagePath); await page.waitForTimeout(500);
  return { page, seen, errors };
}
try {
  let t = await open('/login', { configured: false });
  assert.equal(await t.page.locator('#off').isVisible(), true, 'without accounts configured the page says so'); assert.equal(await t.page.locator('#providers button').count(), 0); assert.deepEqual(t.errors, []); await t.page.close();

  t = await open('/dashboard', { signedIn: false });
  assert.match(t.page.url(), /\/login\?next=%2Fdashboard$/, 'not signed in: to the sign-in page, and back here afterwards: ' + t.page.url()); await t.page.close();

  t = await open('/login?next=https://evil.test/steal');
  assert.equal(await t.page.locator('#providers button').count(), 2); assert.equal(await t.page.locator('#byEmail').isVisible(), true);
  await t.page.fill('#email', 'person@example.com'); await t.page.click('#send'); await t.page.waitForTimeout(200);
  let calls = await t.page.evaluate(() => window.__calls);
  assert.equal(calls[0][0], 'otp'); assert.equal(calls[0][1].options.emailRedirectTo, 'https://app.test/dashboard', 'a "next" on another site is ignored: ' + JSON.stringify(calls[0][1]));
  assert.match(await t.page.locator('#note').textContent(), /Check person@example\.com/);
  await t.page.locator('#providers button').first().click(); await t.page.waitForTimeout(100); calls = await t.page.evaluate(() => window.__calls);
  assert.deepEqual(calls[1], ['oauth', { provider: 'github', options: { redirectTo: 'https://app.test/dashboard' } }]); assert.deepEqual(t.errors, []); await t.page.close();

  t = await open('/login?next=/app?url=https%3A%2F%2Fx.test', { methods: "['email']" });
  assert.equal(await t.page.locator('#providers button').count(), 0); assert.equal(await t.page.locator('#or').isVisible(), false, 'only e-mail offered: no "or"');
  await t.page.fill('#email', 'not-an-address'); await t.page.click('#send'); assert.match(await t.page.locator('#note').textContent(), /does not look like/); assert.deepEqual(await t.page.evaluate(() => window.__calls), []); await t.page.close();

  t = await open('/dashboard', { signedIn: true });
  assert.equal(await t.page.locator('.card').count(), 2); assert.ok(t.seen.auth.length >= 2 && t.seen.auth.every(a => a === 'Bearer tok-' + 'x'.repeat(30)), 'both requests carry the visitor\'s token');
  assert.equal(await t.page.locator('.card .site').first().textContent(), 'river.test'); assert.match(await t.page.locator('.card .state').first().textContent(), /Ready · 3 designs/);
  assert.match(await t.page.locator('.card').first().getAttribute('href'), /^\/app\?job=11111111-1111-4111-8111-111111111111&url=/);
  assert.equal(await t.page.evaluate(() => window.__pwned), undefined, 'an address is set as text: nothing in it runs'); assert.equal(await t.page.locator('.card img').count(), 0);
  assert.match(await t.page.locator('#meterText').textContent(), /2 of 3 free previews used/); assert.equal(await t.page.locator('#empty').isVisible(), false);
  /* the header: where you are, one action, and the account behind a chip */
  assert.equal(await t.page.locator('.hd [data-hd-projects]').getAttribute('aria-current'), 'page'); assert.equal(await t.page.locator('.hd-me').textContent(), 'p', 'the chip carries the initial');
  assert.equal(await t.page.locator('#hdPop').isVisible(), false, 'the panel is shut until asked for');
  await t.page.click('.hd-me'); await t.page.waitForTimeout(350); assert.equal(await t.page.locator('#hdPop').isVisible(), true); assert.equal(await t.page.locator('.hd-me').getAttribute('aria-expanded'), 'true');
  assert.equal(await t.page.locator('#who').textContent(), 'person@example.com'); assert.deepEqual(await t.page.locator('#hdPop .hd-row').allTextContents(), ['Your projects', 'New project', 'Sign out']);
  await t.page.keyboard.press('Escape'); await t.page.waitForTimeout(350); assert.equal(await t.page.locator('#hdPop').isVisible(), false, 'Escape shuts it'); assert.equal(await t.page.evaluate(() => document.activeElement.id), 'hdMe', 'and focus returns to the chip');
  await t.page.click('.hd-me'); await t.page.waitForTimeout(350); await t.page.mouse.click(700, 130); await t.page.waitForTimeout(350); assert.equal(await t.page.locator('#hdPop').isVisible(), false, 'so does a press elsewhere');
  await t.page.click('.hd-me'); await t.page.waitForTimeout(350); await t.page.click('#hdPop a[href="#new"]'); await t.page.waitForTimeout(350); assert.equal(await t.page.evaluate(() => document.activeElement.id), 'site', '"New project" in the panel leads to the field'); assert.equal(await t.page.locator('#hdPop').isVisible(), false);
  await t.page.click('.hd-me'); await t.page.waitForTimeout(350); await t.page.click('#out'); await t.page.waitForTimeout(200); assert.ok(t.seen.gone.includes('/'), 'signing out leaves for the front page'); assert.deepEqual(t.errors, []); await t.page.close();

  /* Starting a project: on the dashboard, with the address typed there. */
  t = await open('/dashboard', { signedIn: true });
  assert.equal(await t.page.locator('#new').isVisible(), true, 'the dashboard itself has the field a project starts from'); assert.equal(await t.page.locator('#listHead').isVisible(), true);
  await t.page.click('.hd-cta'); await t.page.waitForTimeout(150); assert.equal(await t.page.evaluate(() => document.activeElement.id), 'site', '"New project" puts the cursor in the address field');
  await t.page.click('#go'); await t.page.waitForTimeout(150); assert.match(t.page.url(), /\/dashboard/, 'no address: nothing starts'); assert.match(await t.page.locator('#newHelp').textContent(), /Type the address/);
  await t.page.fill('#site', ' https://River.test/menu '); await t.page.keyboard.press('Enter'); await t.page.waitForURL(/\/app\?url=/);
  assert.equal(new URL(t.page.url()).searchParams.get('url'), 'River.test/menu', 'the address goes to the form: ' + t.page.url());
  await t.page.waitForTimeout(400); assert.equal(await t.page.locator('.hd-cta').getAttribute('href'), '/dashboard#new', 'from the form, a new project is started among the projects'); assert.equal(await t.page.locator('.hd [data-hd-projects]').isVisible(), true); assert.equal(await t.page.locator('.hd-me').count(), 1);
  assert.deepEqual(t.errors, []); await t.page.close();

  t = await open('/app', { signedIn: true });
  assert.match(t.page.url(), /\/dashboard#new$/, 'the form without an address, signed in: to the projects, not the landing page: ' + t.page.url());
  await t.page.waitForTimeout(200); assert.equal(await t.page.evaluate(() => document.activeElement.id), 'site'); await t.page.close();
  t = await open('/app', { signedIn: false });
  assert.match(t.page.url(), /app\.test\/#top$/, 'the form without an address, nobody signed in: the front page: ' + t.page.url()); await t.page.close();
  t = await open('/app', { configured: false });
  assert.match(t.page.url(), /app\.test\/#top$/, 'and the same without accounts'); await t.page.close();

  /* The form's header for somebody not signed in: sign in, and come back to this very page. */
  t = await open('/app?url=river.test', { signedIn: false });
  assert.equal(await t.page.locator('.hd-cta').getAttribute('aria-label'), 'Sign in'); assert.equal(await t.page.locator('.hd-cta').getAttribute('href'), '/login?next=' + encodeURIComponent('/app?url=river.test')); assert.equal(await t.page.locator('.hd-me').count(), 0); assert.equal(await t.page.locator('.hd [data-hd-projects]').isVisible(), false); await t.page.close();
  t = await open('/app?url=river.test', { configured: false });
  assert.equal(await t.page.locator('.hd-cta').getAttribute('aria-label'), 'New project'); assert.equal(await t.page.locator('.hd-cta').getAttribute('href'), '/#top', 'without accounts the header offers no sign-in'); await t.page.close();
  /* On a phone nothing in the header or its panel leaves the screen, and every target can be pressed. */
  for (const width of [320, 360, 390]) for (const [where, signedIn] of [['/dashboard', true], ['/app?url=river.test', true], ['/app?url=river.test', false], ['/login', false]]) {
    t = await open(where, { signedIn, width }); if (signedIn) { await t.page.click('.hd-me'); await t.page.waitForTimeout(350); }
    const m = await t.page.evaluate(() => { const box = [...document.querySelectorAll('.hd a,.hd button,.hd-pop')].filter(n => n.offsetParent && getComputedStyle(n).visibility !== 'hidden').map(n => { const r = n.getBoundingClientRect(); return { l: r.left, r: r.right, h: r.height }; });
      return { doc: document.documentElement.scrollWidth, vw: innerWidth, left: Math.min(...box.map(b => b.l)), right: Math.max(...box.map(b => b.r)), low: Math.min(...box.map(b => b.h)) }; });
    assert.ok(m.doc <= m.vw && m.left >= 0 && m.right <= m.vw, `${where} at ${width}: the header stays on the screen ${JSON.stringify(m)}`); assert.ok(m.low >= 44, `${where} at ${width}: every target is at least 44 px tall ${JSON.stringify(m)}`); assert.deepEqual(t.errors, []); await t.page.close(); }

  /* The front page knows the visitor too. */
  t = await open('/', { signedIn: true });
  assert.equal(await t.page.locator('#account').textContent(), 'Your projects'); assert.equal(await t.page.locator('#account').getAttribute('href'), '/dashboard'); await t.page.close();
  t = await open('/', { signedIn: false });
  assert.equal(await t.page.locator('#account').textContent(), 'Sign in'); assert.equal(await t.page.locator('#account').getAttribute('href'), '/login'); assert.equal(t.seen.lib, 0, 'a first-time visitor does not fetch the account library'); await t.page.close();
  t = await open('/', { signedIn: false, held: true });
  assert.equal(await t.page.locator('#account').textContent(), 'Sign in', 'a session that is no longer good reads as signed out'); assert.ok(t.seen.lib >= 1); await t.page.close();
  t = await open('/', { configured: false });
  assert.equal(await t.page.locator('#account').count(), 0, 'without accounts the front page offers none'); await t.page.close();
  t = await open('/', { signedIn: true, width: 360 });
  const nav = await t.page.evaluate(() => { const a = [...document.querySelectorAll('.nav a')].filter(n => n.offsetParent).map(n => n.getBoundingClientRect()); return { doc: document.documentElement.scrollWidth, right: Math.max(...a.map(r => r.right)), tall: Math.max(...a.map(r => r.height)) }; });
  assert.ok(nav.doc <= 360 && nav.right <= 360 && nav.tall < 60, 'the front page\'s bar keeps to one line on a phone with the link in it: ' + JSON.stringify(nav)); await t.page.close();
  console.log('Account pages: sign-in, the dashboard, starting a project and their guards work in a browser');
} finally { await browser.close(); }
