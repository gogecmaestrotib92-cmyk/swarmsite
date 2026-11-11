/* The pages of an account, in a browser, against a stand-in for Supabase and for our API:
   - without accounts configured, the sign-in page says so and the dashboard does not pretend;
   - the dashboard sends a visitor who is not signed in to /login and comes back afterwards;
   - signed in, it lists the visitor's projects with the token attached, and a site's address is text, never markup;
   - a "next" that points at another site is ignored. */
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
async function open(pagePath, { configured = true, signedIn = false, methods = "['github','google','email']" } = {}) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } }); const seen = { auth: [], gone: [] };
  await page.route('**/*', async r => { const q = r.request(), u = new URL(q.url());
    if (u.hostname === 'cdn.jsdelivr.net') return r.fulfill({ contentType: 'application/javascript', body: stub(signedIn) });
    if (u.hostname === 'api.test') { seen.auth.push(q.headers().authorization || ''); if (!signedIn) return r.fulfill({ status: 401, contentType: 'application/json', body: '{"error":"sign in"}' });
      return r.fulfill({ contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(u.pathname === '/me' ? { id: 'u1', email: 'person@example.com', previews: { used: 2, free: 3, left: 1, allowed: true } } : jobs) }); }
    if (u.hostname !== 'app.test') return r.fulfill({ status: 204, body: '' });
    if (u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: `window.SWARMSITE_API='https://api.test';window.SWARMSITE_SUPABASE=${configured ? "{url:'https://sb.test',anon:'public-anon-key'}" : "{url:'',anon:''}"};window.SWARMSITE_LOGIN=${methods};` });
    if (u.pathname === '/js/auth.js') return r.fulfill({ contentType: 'application/javascript', body: file('js/auth.js') });
    if (u.pathname === '/login') return r.fulfill({ contentType: 'text/html', body: file('login.html') });
    if (u.pathname === '/dashboard') return r.fulfill({ contentType: 'text/html', body: file('dashboard.html') });
    seen.gone.push(u.pathname + u.search); return r.fulfill({ contentType: 'text/html', body: '<title>elsewhere</title>' }); });
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
  assert.match(await t.page.locator('#meterText').textContent(), /2 of 3 free previews used/); assert.equal(await t.page.locator('#who').textContent(), 'person@example.com'); assert.equal(await t.page.locator('#empty').isVisible(), false);
  await t.page.click('#out'); await t.page.waitForTimeout(200); assert.ok(t.seen.gone.includes('/'), 'signing out leaves for the front page'); assert.deepEqual(t.errors, []); await t.page.close();
  console.log('Account pages: sign-in, the dashboard and their guards work in a browser');
} finally { await browser.close(); }
