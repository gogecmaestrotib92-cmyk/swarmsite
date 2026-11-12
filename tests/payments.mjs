// Payment with Stripe (server/payments.mjs), with a stubbed Stripe client: a Checkout Session for one design of one job,
// the webhook's signature checked, a paid design let through the download and publish gates, a repeated event harmless,
// and without keys the server exactly as before (402, no address to pay at, no button). Then the chooser's button.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module';
import { configured, payGate, paidBy, stripeOf, checkout, webhook, withPaid, returnUrls } from '../server/payments.mjs';
import { mayDownload } from '../server/templates.mjs';
const root = process.cwd(), { chromium } = createRequire(path.join(root, 'package.json'))('playwright');
const ID = '88888888-8888-4888-8888-888888888888', me = { id: 'u1', email: 'visitor@example.com' }, other = { id: 'u2' };
const ENV = { STRIPE_SECRET_KEY: 'sk_test_stub', STRIPE_PRICE_ID: 'price_stub', STRIPE_WEBHOOK_SECRET: 'whsec_stub', PUBLIC_APP: 'https://swarmsite.si' };
const row = (paid = {}) => ({ id: ID, status: 'done', user_id: null, result: { paid, templates: { variants: [{ slug: 'griffin', package: 'ready' }] } } });

// 1 · without keys: exactly as before
assert.equal(configured({}), false); assert.equal(configured({ STRIPE_SECRET_KEY: 'x' }), false, 'a key without a price is not switched on'); assert.equal(configured(ENV), true);
assert.deepEqual(payGate({ env: {}, row: row(), slug: 'griffin', user: me }), { status: 402, body: { error: 'Payment is needed to download this page.', pay: true } }, 'no address to pay at, so no button');
assert.deepEqual(mayDownload({ user: me, job: row(), slug: 'griffin', env: {} }), { status: 402, body: { error: 'Payment is needed to download this page.', pay: true } });
assert.equal(await stripeOf({}), null, 'no key: the Stripe package is not even loaded');
// with keys: the 402 says where to pay
assert.deepEqual(payGate({ env: ENV, row: row(), slug: 'griffin', user: me, what: 'download or publish' }).body, { error: 'Payment is needed to download or publish this page.', pay: true, pay_url: '/pay', job: ID, slug: 'v1' }, 'the 402 names the design by its id, never its template');
assert.equal(payGate({ env: { ...ENV, PACKAGES_FREE: '1' }, row: row(), slug: 'griffin', user: me }), null, 'PACKAGES_FREE=1 still lets everything through');

// 2 · the client, loaded only with a key
let made = null; const S = await stripeOf(ENV, async () => ({ default: class { constructor(k) { made = k; } } }));
assert.ok(S && made === 'sk_test_stub');

// 3 · a Checkout Session for one design of one job
const sessions = [];
const stub = { checkout: { sessions: { create: async p => { sessions.push(p); return { id: 'cs_test_1', url: 'https://checkout.stripe.com/c/pay/cs_test_1' }; } } },
  webhooks: { constructEvent: (raw, sig, secret) => { if (sig !== 'good' || secret !== 'whsec_stub') throw new Error('No signatures found'); return JSON.parse(Buffer.isBuffer(raw) ? raw.toString() : raw); } } };
// the server hands checkout the design's id (v1), so Stripe, the receipt and the return address never name the template
assert.deepEqual(await checkout({ stripe: stub, env: ENV, row: row(), slug: 'v1', user: me, from: 'edit' }), { url: 'https://checkout.stripe.com/c/pay/cs_test_1', id: 'cs_test_1' });
assert.deepEqual(sessions[0], { mode: 'payment', line_items: [{ price: 'price_stub', quantity: 1 }], client_reference_id: `${ID}:v1`, customer_email: 'visitor@example.com',
  metadata: { job: ID, slug: 'v1', user: 'u1' }, success_url: `https://swarmsite.si/edit?job=${ID}&slug=v1&paid=v1`, cancel_url: `https://swarmsite.si/edit?job=${ID}&slug=v1&paid=0` });
assert.equal(returnUrls(ENV, row(), 'v1', 'app').success_url, `https://swarmsite.si/app?job=${ID}&paid=v1`);

// 4 · the webhook: signature, paid sessions only, metadata that matches, idempotent
const event = (o, type = 'checkout.session.completed') => Buffer.from(JSON.stringify({ type, data: { object: { id: 'cs_test_1', payment_status: 'paid', client_reference_id: `${ID}:griffin`, metadata: { job: ID, slug: 'griffin', user: 'u1' }, ...o } } }));
const marks = []; const markPaid = async m => { marks.push(m); };
assert.deepEqual(await webhook({ stripe: stub, env: ENV, raw: event({}), signature: 'forged', markPaid }), { status: 400, body: { error: 'bad signature' } }); assert.equal(marks.length, 0, 'a forged event marks nothing');
assert.deepEqual(await webhook({ stripe: stub, env: ENV, raw: event({}), signature: 'good', markPaid }), { status: 200, body: { received: true, paid: true } });
assert.deepEqual(marks, [{ job: ID, slug: 'griffin', user: 'u1', session: 'cs_test_1' }]);
assert.deepEqual((await webhook({ stripe: stub, env: ENV, raw: event({ payment_status: 'unpaid' }), signature: 'good', markPaid })).body, { received: true, paid: false }, 'a delayed payment waits for its success event');
assert.deepEqual((await webhook({ stripe: stub, env: ENV, raw: event({}, 'checkout.session.async_payment_succeeded'), signature: 'good', markPaid })).body, { received: true, paid: true });
assert.deepEqual((await webhook({ stripe: stub, env: ENV, raw: event({ metadata: { job: ID, slug: 'maze', user: 'u1' } }), signature: 'good', markPaid })).body, { received: true, ignored: true }, 'metadata that does not match the reference is ignored');
assert.deepEqual((await webhook({ stripe: stub, env: ENV, raw: event({}, 'invoice.paid'), signature: 'good', markPaid })).body, { received: true });
assert.equal(marks.length, 2);
// the record: written once; the same event again changes nothing
const first = withPaid(row().result, { slug: 'griffin', user: 'u1', session: 'cs_test_1', at: '2026-11-12T18:00:00Z' });
assert.deepEqual(first.paid, { griffin: { user: 'u1', session: 'cs_test_1', at: '2026-11-12T18:00:00Z' } }); assert.ok(first.templates, 'the rest of the record stays');
assert.equal(withPaid(first, { slug: 'griffin', user: 'u1', session: 'cs_test_1', at: 'later' }), null, 'a repeated webhook writes nothing');

// 5 · paid unlocks the download and publish, for that account and that design only
const paid = { ...row(), result: first };
assert.ok(paidBy(paid, 'griffin', me) && !paidBy(paid, 'griffin', other) && !paidBy(paid, 'maze', me) && !paidBy(paid, 'griffin', null));
assert.deepEqual(mayDownload({ user: me, job: paid, slug: 'griffin', env: ENV }), { status: 200 });
assert.equal(mayDownload({ user: other, job: paid, slug: 'griffin', env: ENV }).status, 402);
assert.equal(payGate({ env: ENV, row: paid, slug: 'griffin', user: me, what: 'download or publish' }), null);

// 6 · the server's wiring
const src = fs.readFileSync(path.join(root, 'server/index.mjs'), 'utf8');
assert.ok(/req\.path === '\/stripe\/webhook' \? next\(\) : json\(req, res, next\)/.test(src) && /app\.post\('\/stripe\/webhook', express\.raw\(/.test(src), 'the webhook gets its raw body');
assert.ok(/if \(!payConfigured\(process\.env\)\) return res\.status\(503\)/.test(src) && /if \(!process\.env\.STRIPE_SECRET_KEY \|\| !process\.env\.STRIPE_WEBHOOK_SECRET\) return res\.status\(503\)/.test(src), 'off without keys');
assert.ok(/const pay = payGate\(\{ env: process\.env, row, slug: req\.tslug, user, what: 'download or publish' \}\)/.test(src), 'publish passes the same gate');
assert.ok(/checkout\(\{ stripe: await stripe\(\), env: process\.env, row, slug: publicOf\(row, tslug\)/.test(src) && /const tslug = internalSlug\(row, slug\); if \(!tslug\) return;/.test(src), 'Stripe is told the design\'s id; the webhook turns it back');
assert.ok(!/console\.(log|warn)\([^)]*(STRIPE_SECRET_KEY|STRIPE_WEBHOOK_SECRET|signature|email)/.test(src), 'no key, signature or email in a log line');
assert.ok(JSON.parse(fs.readFileSync(path.join(root, 'server/package.json'), 'utf8')).dependencies.stripe, 'the official package, installed by the server\'s build');

// 7 · the chooser: a 402 with an address to pay at shows "Pay and download", which goes to Checkout
const html = fs.readFileSync(path.join(root, 'web/app.html'), 'utf8');
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  for (const withPay of [true, false]) {
    const state = { pay: null, checkout: false }; const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    await page.route('**/*', async r => { const u = new URL(r.request().url()), m = r.request().method(); const json = (o, s = 200) => r.fulfill({ status: s, headers: { 'access-control-allow-origin': '*' }, contentType: 'application/json', body: JSON.stringify(o) });
      if (r.request().headers()['access-control-request-method']) return r.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'POST' } });
      if (u.hostname === 'app.test' && u.pathname === '/app') return r.fulfill({ contentType: 'text/html', body: html });
      if (u.pathname === '/config.js') return r.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test'" });
      if (u.pathname === '/js/swarm2.js') return r.fulfill({ contentType: 'application/javascript', body: 'window.Swarm2={mount:()=>({stop(){},phase(){},push(){},setPage(){}})}' });
      if (u.pathname === `/jobs/${ID}`) return json({ id: ID, url: 'https://x.example', status: 'done', created_at: new Date().toISOString(), steps: [], result: { templates: { variants: [{ slug: 'v1', id: 'v1', name: 'Design 1', approach: '', url: `https://api.test/t/${ID}/v1`, package: 'ready' }], store: true } } });
      if (u.pathname === `/t/${ID}/v1/package`) return json(withPay ? { error: 'Payment is needed to download this page.', pay: true, pay_url: '/pay', job: ID, slug: 'v1' } : { error: 'Payment is needed to download this page.', pay: true }, 402);
      if (u.pathname === '/pay' && m === 'POST') { state.pay = JSON.parse(r.request().postData()); return json({ url: 'https://checkout.stripe.test/c/pay/cs_test_1', id: 'cs_test_1' }); }
      if (u.hostname === 'checkout.stripe.test') { state.checkout = true; return r.fulfill({ contentType: 'text/html', body: '<p>checkout</p>' }); }
      if (u.pathname.startsWith(`/t/${ID}/`)) return r.fulfill({ contentType: 'text/html', body: '<h1>page</h1>' });
      return r.abort(); });
    await page.goto(`https://app.test/app?job=${ID}`);
    await page.locator('#choose.on').waitFor({ timeout: 10000 });
    await page.locator('.card .pickb').first().click(); await page.locator('#download').click();
    if (withPay) {
      await page.locator('#payGo:not([hidden])').waitFor({ timeout: 8000 }); assert.ok(await page.locator('#download').isHidden());
      await page.locator('#payGo').click(); await page.waitForFunction(() => location.hostname === 'checkout.stripe.test', null, { timeout: 8000 });
      assert.deepEqual(state.pay, { job: ID, slug: 'v1', from: 'app' }); assert.ok(state.checkout);
    } else {
      await page.waitForFunction(() => /Payment comes before the download/.test(document.querySelector('#chooseNote').textContent), null, { timeout: 8000 });
      assert.ok(await page.locator('#payGo').isHidden(), 'no keys: no pay button, as before');
    }
    await page.close();
  }
} finally { await browser.close(); }
console.log('Payments: Checkout Session for one design, webhook signature checked, paid lets that account through, a repeated event harmless, no keys = as before; the chooser\'s pay button');
