// Who came and what they did is written down by us (server/track.mjs) and read by the owner alone (server/admin.mjs,
// web/admin.html): no address is kept, a crawler is not a visitor, a failed write never reaches a visitor, the numbers
// answer only to the deployment's key, a day with no record says so, and the page reads at 390 without naming a template.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module';
import { isBot, pageOf, refHost, visitorKey, cleanBeacon, makeTracker } from '../server/track.mjs';
import { makeAdminGate, adminToken, summarise } from '../server/admin.mjs';
import { TEMPLATE_SLUGS } from '../server/designs.mjs';
const root = process.cwd(), read = f => fs.readFileSync(path.join(root, f), 'utf8'), src = read('server/index.mjs');
const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1';
const J1 = '11111111-1111-4111-8111-111111111111', J2 = '22222222-2222-4222-8222-222222222222';
const req = (body, ip = '203.0.113.7', ua = UA) => ({ headers: { 'x-forwarded-for': ip, 'user-agent': ua }, body });

// 1 · what is kept of a visitor
{ assert.ok(!isBot(UA)); for (const ua of ['', 'curl/8.4.0', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/120.0 Safari/537.36', 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)', 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)']) assert.ok(isBot(ua), ua);
  assert.deepEqual(['/', '/index.html', '/app', '/app?job=' + J1, '/start', '/edit?job=x&slug=v1', '/blog/host-html-css-website', '/admin', '/x/y'].map(pageOf), ['landing', 'landing', 'app', 'app', 'start', 'edit', 'blog', 'other', 'other']);
  assert.equal(refHost('https://www.Google.com/search?q=someone+private'), 'google.com'); assert.equal(refHost('news.ycombinator.com'), 'news.ycombinator.com');
  for (const own of ['https://swarmsite.si/app', 'www.swarmsite.si', 'http://localhost:3000/', 'javascript:alert(1)', '<script>', 'a b.com', '']) assert.equal(refHost(own), '', own);
  const k = visitorKey('203.0.113.7', UA, 's', '2026-11-19');
  assert.match(k, /^[0-9a-f]{24}$/); assert.ok(!k.includes('203.0.113.7')); assert.equal(k, visitorKey('203.0.113.7', UA, 's', '2026-11-19'));
  assert.notEqual(k, visitorKey('203.0.113.7', UA, 's', '2026-11-20'), 'tomorrow the same person is another key'); assert.notEqual(k, visitorKey('203.0.113.8', UA, 's', '2026-11-19')); assert.notEqual(k, visitorKey('203.0.113.7', UA, 'other', '2026-11-19'));
  // a page may say two things; an address, a query, a name it made up are not kept
  assert.deepEqual(cleanBeacon(JSON.stringify({ n: 'visit', p: '/app?job=' + J1 + '&email=a@b.c', r: 'https://t.co/abc?u=me', s: 'Newsletter', m: 'email', c: 'launch 1', x: 'extra' })), { name: 'visit', page: 'app', ref: 't.co', src: 'newsletter', medium: 'email', campaign: 'launch 1', job: null });
  assert.equal(cleanBeacon(JSON.stringify({ n: 'visit', p: '/', s: '<img src=x>' })).src, null);
  for (const bad of ['', 'not json', '[]', '{"n":"download","p":"/"}', '{"n":"job_refused"}', '{"n":"design_opened","p":"/app"}', '{"n":"design_opened","j":"1 or 1=1"}', JSON.stringify({ n: 'visit', p: 'x'.repeat(3000) }), null, 7]) assert.equal(cleanBeacon(bad), null, String(bad).slice(0, 30));
  assert.equal(cleanBeacon({ n: 'design_opened', p: '/app', j: J1 }).job, J1); }

// 2 · recording: written a moment later in one insert, and never a visitor's problem
{ let clock = Date.parse('2026-11-19T10:00:00Z'), down = false; const written = [], warned = [];
  const T = makeTracker({ secret: 's', now: () => clock, timer: false, warn: t => warned.push(t), perVisitorPerHour: 5, maxBuffer: 50, insert: async rows => { if (down) throw new Error('relation "events" does not exist'); written.push(...rows); } });
  assert.equal(T.beacon(req(JSON.stringify({ n: 'visit', p: '/', r: 'https://www.google.com/' }))), true);
  assert.equal(written.length, 0, 'nothing is written while the visitor waits'); await T.flush();
  assert.equal(written.length, 1); const row = written[0];
  assert.deepEqual([row.name, row.page, row.ref, row.at], ['visit', 'landing', 'google.com', '2026-11-19T10:00:00.000Z']);
  assert.ok(!JSON.stringify(written).includes('203.0.113') && !JSON.stringify(written).includes('iPhone'), 'neither the address nor the browser is kept');
  assert.equal(row.visitor, visitorKey('203.0.113.7', UA, 's', '2026-11-19'));
  // a crawler is counted as one and not written; a body that is not ours is dropped
  assert.equal(T.beacon(req(JSON.stringify({ n: 'visit', p: '/' }), '198.51.100.1', 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)')), false);
  assert.equal(T.beacon(req('{"n":"paid"}')), false); assert.equal(T.beacon(undefined), false); assert.equal(T.beacon({}), false);
  // one address flooding: the sixth report in the hour is dropped, another address is not held back
  for (let i = 0; i < 9; i++) T.beacon(req(JSON.stringify({ n: 'visit', p: '/app' }), '198.51.100.9'));
  assert.equal(T.beacon(req(JSON.stringify({ n: 'visit', p: '/app' }), '198.51.100.10')), true); await T.flush();
  assert.equal(written.filter(r => r.visitor === visitorKey('198.51.100.9', UA, 's', '2026-11-19')).length, 5);
  // …also when it names another browser each time; and an instance writes no more page reports an hour than its ceiling
  for (let i = 0; i < 9; i++) T.beacon(req(JSON.stringify({ n: 'visit', p: '/' }), '198.51.100.20', UA + ' Build/' + i)); await T.flush();
  assert.equal(written.filter(r => r.page === 'landing' && r.ref === null && r.name === 'visit').length, 5, 'a new browser name is not a new allowance');
  { const w = []; const cap = makeTracker({ secret: 's', timer: false, perHour: 3, insert: async rows => { w.push(...rows); } }); for (let i = 0; i < 8; i++) cap.beacon(req(JSON.stringify({ n: 'visit', p: '/' }), '198.51.100.' + (30 + i))); await cap.flush(); assert.deepEqual([w.length, cap.counts().dropped], [3, 5]); }
  // the server's own events; an editor that draws the page fifty times is one row a job a day
  assert.equal(T.refused(req(null), 'rate_limit'), true); assert.equal(T.refused(req(null), 'something else'), true);
  for (let i = 0; i < 50; i++) T.once('edit', J1); T.once('edit', J2); T.record({ name: 'download', job: J1 }); T.record({ name: 'download', job: 'not-a-job' }); assert.equal(T.record({ name: 'made up' }), false); assert.equal(T.record(null), false);
  await T.flush(); const names = n => written.filter(r => r.name === n);
  assert.deepEqual(names('job_refused').map(r => r.detail), ['rate_limit', 'other']); assert.deepEqual(names('edit').map(r => r.job), [J1, J2]); assert.deepEqual(names('download').map(r => r.job), [J1, null]);
  clock += 86400e3; assert.equal(T.once('edit', J1), true, 'the next day it is written again'); await T.flush();
  // the database is away (or the table was never made): nothing throws, the rows are counted as not written and not kept
  down = true; const before = written.length; for (let i = 0; i < 3; i++) T.record({ name: 'download', job: J1 });
  await T.flush(); await T.flush(); assert.equal(written.length, before); const c = T.counts();
  assert.equal(c.failed, 3); assert.equal(c.waiting, 0); assert.equal(c.bots, 3, 'the crawler, and two requests with no browser named'); assert.ok(c.dropped >= 5 && c.recorded === before); assert.equal(warned.length, 1); assert.ok(!/203\.0|198\.51/.test(warned[0]));
  // a write that never comes back does not let memory grow: past the buffer's size, rows are dropped
  const stuck = makeTracker({ secret: 's', timer: false, maxBuffer: 10, insert: () => new Promise(() => {}) }); for (let i = 0; i < 25; i++) stuck.record({ name: 'download', job: J1 });
  assert.deepEqual([stuck.counts().waiting, stuck.counts().dropped], [10, 15]);
  // with its timer, a row is written without anyone asking
  const got = []; const live = makeTracker({ secret: 's', flushMs: 20, insert: async rows => { got.push(...rows); } }); live.record({ name: 'download', job: J1 }); await new Promise(r => setTimeout(r, 120)); assert.equal(got.length, 1); }

// 3 · who may read the numbers
{ const KEY = 'k'.repeat(24); let clock = 1e12;
  for (const env of [{}, { ADMIN_TOKEN: '' }, { ADMIN_TOKEN: 'short' }, { ADMIN_TOKEN: '   ' }]) { assert.equal(adminToken(env), '');
    const g = makeAdminGate({ env }); for (const authorization of ['', 'Bearer ', 'Bearer short', 'Bearer undefined', 'Bearer ' + KEY]) assert.equal(g({ ip: '1.1.1.1', authorization }).status, 503, 'no key set: nobody is let in'); }
  const gate = makeAdminGate({ env: { ADMIN_TOKEN: KEY }, now: () => clock });
  assert.equal(gate({ ip: '1.1.1.1', authorization: 'Bearer ' + KEY }).status, 200);
  for (const authorization of [undefined, '', KEY, 'Bearer', 'Bearer ' + KEY + 'x', 'Bearer ' + KEY.slice(0, 23), 'Basic ' + KEY, 'bearer  ']) assert.equal(gate({ ip: '2.2.2.2', authorization }).status, 401, String(authorization));
  for (let i = 0; i < 2; i++) gate({ ip: '2.2.2.2', authorization: 'Bearer wrong' });
  assert.equal(gate({ ip: '2.2.2.2', authorization: 'Bearer ' + KEY }).status, 429, 'ten wrong tries: even the right key waits'); assert.equal(gate({ ip: '3.3.3.3', authorization: 'Bearer ' + KEY }).status, 200);
  clock += 16 * 60e3; assert.equal(gate({ ip: '2.2.2.2', authorization: 'Bearer ' + KEY }).status, 200);
  assert.ok(!JSON.stringify(gate({ ip: '9.9.9.9', authorization: 'Bearer nope' })).includes(KEY));
  // the server: the gate stands before anything is read, the key is the deployment's, and it is in no file
  const route = src.slice(src.indexOf("app.get('/admin/stats'"), src.indexOf("app.get('/me'"));
  assert.ok(route.indexOf('if (gate.status !== 200) return res.status(gate.status)') > 0 && route.indexOf('if (gate.status !== 200)') < route.indexOf('sb.from('), 'refused before the database is asked');
  assert.ok(/'cache-control': 'no-store', 'x-robots-tag': 'noindex'/.test(route)); assert.ok(/makeAdminGate\(\{ env: process\.env \}\)/.test(src));
  for (const f of ['server/index.mjs', 'server/admin.mjs', 'web/admin.html', 'web/config.js', 'web/js/track.js']) assert.ok(!/ADMIN_TOKEN\s*[:=]\s*['"][^'"]/.test(read(f)), f + ' holds no key');
  // a visitor is answered before their report is looked at; the refusals of POST /jobs are written down
  assert.ok(/app\.post\('\/e', express\.text\(\{ type: \(\) => true, limit: '4kb' \}\), \(req, res\) => \{ res\.status\(204\)\.end\(\); TRACK\.beacon\(req\); \}\)/.test(src));
  for (const why of ['rate_limit', 'queue_full', 'day_budget']) assert.ok(src.includes(`TRACK.refused(req, '${why}')`), why);
  for (const name of ['download', 'edit_kept', 'pay_started']) assert.ok(src.includes(`name: '${name}'`), name); assert.ok(src.includes("TRACK.once('edit', row.id")); }

// 4 · the numbers: counts of rows, by the owner's day, and "no data" where nothing was recorded
{ const now = Date.parse('2026-11-19T12:00:00Z'), ev = (at, name, o = {}) => ({ at, name, page: null, visitor: null, ref: null, src: null, medium: null, campaign: null, job: null, detail: null, ...o });
  const events = [ev('2026-11-18T09:00:00Z', 'visit', { page: 'landing', visitor: 'a', ref: 'google.com' }), ev('2026-11-18T09:05:00Z', 'visit', { page: 'app', visitor: 'a', ref: 'google.com' }), ev('2026-11-18T10:00:00Z', 'visit', { page: 'landing', visitor: 'b', src: 'newsletter', campaign: 'launch' }),
    ev('2026-11-18T23:30:00Z', 'visit', { page: 'landing', visitor: 'c' }),   // half past midnight in Ljubljana: the 19th
    ev('2026-11-19T08:00:00Z', 'visit', { page: 'made-up', visitor: 'a' }), ev('2026-11-19T08:01:00Z', 'design_opened', { job: J1 }), ev('2026-11-19T08:02:00Z', 'design_opened', { job: J1 }), ev('2026-11-19T08:03:00Z', 'edit', { job: J1 }),
    ev('2026-11-19T08:04:00Z', 'edit_kept', { job: J1 }), ev('2026-11-19T08:05:00Z', 'pay_started', { job: J1 }), ev('2026-11-19T08:09:00Z', 'download', { job: J1 }), ev('2026-11-19T09:00:00Z', 'job_refused', { detail: 'rate_limit' }), ev('2026-11-19T09:01:00Z', 'job_refused', { detail: 'queue_full' }), ev('2026-11-01T09:00:00Z', 'visit', { visitor: 'old' })];
  const slug = TEMPLATE_SLUGS[0] || 'griffin';
  const jobs = [{ id: J1, created_at: '2026-11-19T07:50:00Z', status: 'done', error: null, url: 'https://www.example.com/', source: null }, { id: J2, created_at: '2026-11-19T07:55:00Z', status: 'failed', error: `python3 lib/templates/job.py exit 1:\n  ${slug} could not be fitted\n\n` + 'x'.repeat(900), url: 'form:bakery-1a2b3c4d', source: 'form' },
    { id: '33333333-3333-4333-8333-333333333333', created_at: '2026-11-17T10:00:00Z', status: 'failed', error: null, url: 'https://slow.example.org/page', source: null }, { id: '44444444-4444-4444-8444-444444444444', created_at: '2026-11-19T11:59:00Z', status: 'running', error: null, url: 'https://x.example', source: null }];
  const paid = [{ id: J1, paid: { [slug]: { user: 'u', session: 'cs_1', at: '2026-11-19T08:07:00Z' } } }, { id: 'old', paid: { a: { at: '2026-10-01T08:00:00Z' }, b: { at: 'not a time' } } }, { id: 'odd', paid: 'nonsense' }];
  const s = summarise({ events, jobs, paid, days: 3, now, tz: 'Europe/Ljubljana', firstEventAt: '2026-11-18T09:00:00Z' });
  assert.deepEqual(s.by_day.map(r => r.day), ['2026-11-17', '2026-11-18', '2026-11-19']); const [d17, d18, d19] = s.by_day;
  assert.deepEqual([d17.visitors, d17.views, d17.opened, d17.downloaded, d17.refused, d17.pages], [null, null, null, null, null, null], 'a day before recording began has no data, not zero');
  assert.deepEqual([d17.started, d17.failed, d17.paid], [1, 1, 0], 'jobs are counted for it all the same');
  assert.deepEqual([d18.visitors, d18.views, d18.pages.landing, d18.pages.app], [2, 3, 2, 1]); assert.deepEqual([d19.visitors, d19.views, d19.pages.other], [2, 2, 1]);
  assert.deepEqual([d19.started, d19.done, d19.failed, d19.waiting, d19.opened, d19.edited, d19.kept, d19.pay_started, d19.paid, d19.downloaded], [3, 1, 1, 1, 1, 1, 1, 1, 1, 1]); assert.deepEqual(d19.refused, { rate_limit: 1, queue_full: 1, day_budget: 0, other: 0 });
  assert.deepEqual(s.total, { views: 5, visitors: 4, started: 4, done: 1, failed: 2, waiting: 1, opened: 1, edited: 1, kept: 1, pay_started: 1, paid: 1, downloaded: 1 });
  assert.deepEqual(s.sources, [{ key: '(direct or unknown)', visitors: 3 }, { key: 'google.com', visitors: 1 }]); assert.deepEqual(s.campaigns, [{ key: 'newsletter / – / launch', visitors: 1 }]);
  assert.deepEqual(s.failed.map(f => [f.site, f.from]), [['form', 'form'], ['slow.example.org', 'address']]); assert.equal(s.failed[1].reason, 'no reason was written');
  assert.ok(s.failed[0].reason.length <= 240 && !/\n/.test(s.failed[0].reason) && !new RegExp(`\\b${slug}\\b`).test(JSON.stringify(s)), 'a reason is one short line and never names a template');
  // the table is not there: jobs and payments are still counted, and everything an event would say is null
  const bare = summarise({ events: null, jobs, paid, days: 3, now }); assert.equal(bare.events_readable, false);
  assert.deepEqual([bare.total.visitors, bare.total.views, bare.total.opened, bare.total.downloaded, bare.sources, bare.pages, bare.campaigns, bare.refused], [null, null, null, null, null, null, null, null]); assert.deepEqual([bare.total.started, bare.total.paid, bare.total.failed], [4, 1, 2]);
  // the table is there and empty: still no data, never a made-up zero
  const empty = summarise({ events: [], jobs: [], paid: [], days: 7, now }); assert.equal(empty.total.visitors, null); assert.equal(empty.total.started, 0); assert.equal(empty.by_day.length, 7); assert.deepEqual(empty.failed, []); }

// 5 · the pages: the script is ours, on every way in; the owner's page is linked from nowhere and kept out of search
{ const track = read('web/js/track.js'); assert.ok(!/cookie|sessionStorage|setItem|googletagmanager|google-analytics|plausible|posthog/i.test(track.replace(/\/\*[\s\S]*?\*\//g, '')), 'nothing is kept in the browser and nobody else is told');
  assert.ok(/swarmsite\\\.si\$\/\.test\(location\.hostname\) \|\| navigator\.webdriver\) return/.test(track), 'silent off swarmsite.si and in an automated browser');
  for (const p of ['index', 'app', 'start', 'edit', 'dashboard', 'login', 'blog/index']) assert.ok(read(`web/${p}.html`).includes('<script src="/js/track.js" defer></script>'), p);
  const admin = read('web/admin.html'); assert.ok(/<meta name="robots" content="noindex, nofollow">/.test(admin)); assert.ok(!admin.includes('innerHTML'), 'a failed job\'s reason is another site\'s text: written as text');
  const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(e => e.isDirectory() ? (['vendor', 'fonts'].includes(e.name) ? [] : walk(path.join(d, e.name))) : /\.(html|js|txt|xml|json)$/.test(e.name) ? [path.join(d, e.name)] : []);
  for (const f of walk(path.join(root, 'web'))) { const rel = path.relative(root, f); if (rel === 'web/admin.html' || rel === 'web/vercel.json') continue; assert.ok(!/["'(/]admin\b|\/admin\/stats/.test(fs.readFileSync(f, 'utf8')), rel + ' points at the owner\'s page'); }
  assert.ok(JSON.parse(read('web/vercel.json')).headers.some(h => h.source === '/admin' && h.headers.some(x => x.key === 'X-Robots-Tag' && /noindex/.test(x.value))));
  assert.ok(/enable row level security/.test(read('server/migrations/20261119_events.sql')) && !/\bip\b|address text|email/i.test(read('server/migrations/20261119_events.sql').replace(/--.*$/gm, ''))); }

// 6 · the owner's page in a browser, 390 wide and 1440: closed without the key, closed with a wrong one, readable with it
{ const { chromium } = createRequire(path.join(root, 'package.json'))('playwright'); const KEY = 'right-key-of-the-owner-1234', now = Date.parse('2026-11-19T12:00:00Z');
  const slug = TEMPLATE_SLUGS[0] || 'griffin', days = 14, events = [], jobs = [];
  for (let d = 0; d < 6; d++) { for (let v = 0; v < 3 + d * 7; v++) events.push({ at: new Date(now - d * 86400e3 - v * 60e3).toISOString(), name: 'visit', page: v % 3 ? 'landing' : 'app', visitor: 'v' + v, ref: v % 4 ? 'a-very-long-referring-host-name.example-domain-of-someone.co.uk' : null, src: v % 5 ? null : 'newsletter', campaign: v % 5 ? null : 'a campaign with a long name 2026' });
    jobs.push({ id: J1, created_at: new Date(now - d * 86400e3).toISOString(), status: d % 2 ? 'failed' : 'done', error: d % 2 ? `${slug} Traceback (most recent call last): <img src=x onerror=window.__xss=1> ` + 'word '.repeat(80) : null, url: 'https://a-site-with-a-very-long-host-name-that-does-not-break.example.com/', source: null }); }
  events.push({ at: new Date(now).toISOString(), name: 'job_refused', detail: 'rate_limit' }, { at: new Date(now).toISOString(), name: 'design_opened', job: J1 });
  const stats = { ...summarise({ events, jobs, paid: [], days, now, firstEventAt: events[events.length - 3].at }), notes: [], recording: { recorded: 12, failed: 0, dropped: 1, bots: 4, since: now - 3600e3, waiting: 0 } };
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  try { for (const width of [390, 1440]) {
    const asked = []; const page = await browser.newPage({ viewport: { width, height: 844 } }); const errors = []; page.on('pageerror', e => errors.push(String(e)));
    await page.route('**/*', async r => { const u = new URL(r.request().url());
      if (u.hostname === 'site.test' && u.pathname === '/admin') return r.fulfill({ contentType: 'text/html', body: read('web/admin.html') });
      if (u.hostname === 'site.test' && u.pathname === '/config.js') return r.fulfill({ contentType: 'text/javascript', body: 'window.SWARMSITE_API="http://api.test";' });
      if (u.hostname === 'api.test' && u.pathname === '/admin/stats') { if (r.request().method() === 'OPTIONS') return r.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': 'authorization' } });
        const a = r.request().headers().authorization || ''; asked.push(a); const ok = a === 'Bearer ' + KEY;
        return r.fulfill({ status: ok ? 200 : 401, headers: { 'access-control-allow-origin': '*' }, contentType: 'application/json', body: JSON.stringify(ok ? stats : { error: 'Wrong or missing key.' }) }); }
      return r.fulfill({ status: 404, body: '' }); });
    await page.goto('http://site.test/admin'); await page.waitForSelector('#gate:not([hidden])');
    assert.equal(asked.length, 0, 'without a key the page does not even ask'); assert.ok(await page.isHidden('#board')); assert.equal((await page.textContent('#tiles')).trim(), '');
    await page.fill('#key', 'a-wrong-key-12345678'); await page.click('#keyForm button'); await page.waitForSelector('#gateMsg:not([hidden])');
    assert.match(await page.textContent('#gateMsg'), /Pogrešan ključ/); assert.ok(await page.isHidden('#board')); assert.equal(await page.evaluate(() => localStorage.getItem('swarmsite_admin')), null, 'a wrong key is not kept');
    await page.fill('#key', KEY); await page.click('#keyForm button'); await page.waitForSelector('#board:not([hidden])');
    const text = await page.evaluate(() => document.body.innerText);
    for (const want of ['Da li neko dolazi?', 'Šta rade?', 'Šta je pošlo po zlu?', 'Posetilaca', 'Limit po adresi', 'nema podataka', 'Započeli plaćanje', 'newsletter']) assert.ok(text.includes(want), `${width}: ${want}`);
    assert.ok(!new RegExp(`\\b${slug}\\b`, 'i').test(text), 'no template is named'); assert.equal(await page.evaluate(() => window.__xss), undefined); assert.ok(text.includes('<img src=x'), 'a reason is shown as the text it is');
    const m = await page.evaluate(() => ({ sw: document.scrollingElement.scrollWidth, w: innerWidth, spill: [...document.querySelectorAll('.w *')].filter(e => !e.closest('.scroll') && e.getClientRects().length && (e.getBoundingClientRect().right > innerWidth + 0.5 || e.getBoundingClientRect().left < -0.5)).map(e => e.tagName + '.' + e.className).slice(0, 5),
      small: [...document.querySelectorAll('.w *')].filter(e => e.children.length === 0 && e.textContent.trim() && e.getClientRects().length && parseFloat(getComputedStyle(e).fontSize) < 12).length, taps: [...document.querySelectorAll('button')].filter(b => b.getClientRects().length && b.getBoundingClientRect().height < 44).length,
      bars: document.querySelectorAll('#cVisitors rect.b, #cVisitors rect.n').length, faint: document.querySelectorAll('#cVisitors rect.n').length, tiles: [...document.querySelectorAll('.tile b')].map(b => b.textContent) }));
    assert.ok(m.sw <= m.w, `${width}: the page is ${m.sw} wide`); assert.deepEqual(m.spill, [], `${width}: outside the screen`); assert.equal(m.small, 0, 'no text under 12 px'); assert.equal(m.taps, 0, 'every button is 44 px tall');
    assert.equal(m.bars, days); assert.ok(m.faint >= 5, 'days with no record are drawn as that'); assert.deepEqual(m.tiles, [String(stats.total.visitors), '6', '3', '0']);
    await page.locator('#cVisitors rect.hit').last().click(); assert.match(await page.textContent('#cVisitors .read'), /19\. 11\. — \d+ posetilaca/);
    assert.equal(await page.evaluate(() => localStorage.getItem('swarmsite_notrack')), '1', 'the owner is not a visitor from here on');
    await page.reload(); await page.waitForSelector('#board:not([hidden])'); await page.click('#forget'); await page.waitForSelector('#gate:not([hidden])'); assert.equal(await page.evaluate(() => localStorage.getItem('swarmsite_admin')), null);
    assert.deepEqual(errors, []); await page.close(); } }
  finally { await browser.close(); } }
console.log('tracking: no address kept, crawlers and floods dropped, a failed write is nobody\'s problem; the numbers answer only to the deployment\'s key; no record reads "no data"; the owner\'s page reads at 390');
