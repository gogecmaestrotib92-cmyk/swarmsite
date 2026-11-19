// The guides (web/blog, written by scripts/seo.py) are held to what the landing is held to: no layout break at five
// widths, nothing missing, nothing that does not answer, readable on a phone without scrolling sideways.
//   node tests/blog-layout.mjs
import assert from 'node:assert/strict'; import fs from 'node:fs'; import http from 'node:http'; import path from 'node:path'; import { spawn } from 'node:child_process'; import { fileURLToPath } from 'node:url'; import { chromium } from 'playwright';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'); const web = path.join(root, 'web');
const TYPES = { html: 'text/html; charset=utf-8', css: 'text/css', js: 'text/javascript', webp: 'image/webp', png: 'image/png', jpg: 'image/jpeg', json: 'application/json', txt: 'text/plain', xml: 'text/xml' };
// addresses as web/vercel.json serves them (cleanUrls, no trailing slash): /blog is blog/index.html, /blog/x is blog/x.html, anything else is 404.html
const server = http.createServer((req, res) => { const name = decodeURIComponent(req.url.split('?')[0]); const f = path.join(web, name);
  const file = [f, f + '.html', path.join(f, 'index.html')].find(x => x.startsWith(web) && fs.existsSync(x) && fs.statSync(x).isFile());
  if (!file) { res.writeHead(404, { 'content-type': TYPES.html }); fs.createReadStream(path.join(web, '404.html')).pipe(res); return; }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file).slice(1)] || 'application/octet-stream' }); fs.createReadStream(file).pipe(res); });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const base = `http://127.0.0.1:${server.address().port}`;
const failures = []; const check = (ok, what) => { if (!ok) failures.push(what); };
const pages = ['/blog', ...fs.readdirSync(path.join(web, 'blog')).filter(f => f.endsWith('.html') && f !== 'index.html').map(f => '/blog/' + f.slice(0, -5))];
assert.ok(pages.length >= 4, 'the blog and at least three guides');

// 1. The layout gate on every page of the blog.
const gate = url => new Promise(done => { const p = spawn('node', [path.join(root, 'lib/qa/layout.mjs'), url], { env: { ...process.env, LIVETEST: '1' } }); let out = '', err = ''; p.stdout.on('data', d => out += d); p.stderr.on('data', d => err += d); p.on('close', status => done({ status, out, err })); });
for (const u of pages) { const lay = await gate(base + u); assert.equal(lay.status, 0, lay.err); const breaks = JSON.parse(lay.out.trim().split('\n').pop()).breaks;
  check(breaks.length === 0, `${u}: layout breaks ${JSON.stringify(breaks.map(b => `${b.kind}@${b.section} ${b.widths} “${b.text}” ${b.detail}`))}`); }

const b = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
const open = async width => { const ctx = await b.newContext({ viewport: { width, height: width < 600 ? 844 : 900 }, hasTouch: width < 600, isMobile: width < 600 }); const p = await ctx.newPage();
  const errors = []; p.on('pageerror', e => errors.push(String(e))); p.on('response', r => { if (r.status() >= 400 && r.url().startsWith(base)) errors.push(`${r.status()} ${r.url().slice(base.length)}`); });
  await p.route(/^https?:\/\/(?!127\.0\.0\.1)/, r => r.abort()); return { p, errors, ctx }; };

// 2. Scrolled from top to bottom at a desk and a phone: no error, no file missing, every picture drawn, one h1, no sideways
//    scroll, nothing wider than the screen but what is made to scroll; on a phone every target a finger can hit, text no smaller than 12 px.
for (const u of pages) for (const width of [1440, 390]) { const { p, errors, ctx } = await open(width); await p.goto(base + u); await p.waitForTimeout(300);
  const H = await p.evaluate(() => document.documentElement.scrollHeight); for (let y = 0; y <= H; y += 600) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(40); } await p.waitForTimeout(500);
  const m = await p.evaluate(() => ({ h1: document.querySelectorAll('h1').length, side: document.documentElement.scrollWidth > innerWidth + 1,
    blank: [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.getAttribute('src')),
    wide: [...document.querySelectorAll('main *')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 1 && (r.right > innerWidth + 1 || r.left < -1) && !e.closest('.tw, pre'); }).map(e => e.tagName + '.' + e.className).slice(0, 4),
    small: innerWidth > 600 ? [] : [...document.querySelectorAll('a, button, input')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 1 && (r.height < 24 || r.width < 24) && !e.closest('.body p, .body li, .body td, .body cite, .skip'); }).map(e => (e.textContent || e.placeholder || '').trim().slice(0, 24)),
    tiny: [...document.querySelectorAll('main p, main li, main td, main th, main span, main a, main time')].filter(e => e.getBoundingClientRect().width > 1 && parseFloat(getComputedStyle(e).fontSize) < 12).map(e => e.textContent.trim().slice(0, 24)).slice(0, 4) }));
  check(errors.length === 0, `${u} ${width}: errors ${JSON.stringify(errors)}`); check(m.h1 === 1, `${u} ${width}: ${m.h1} h1`); check(!m.side, `${u} ${width}: the page scrolls sideways`);
  check(m.blank.length === 0, `${u} ${width}: pictures not drawn ${JSON.stringify(m.blank)}`); check(m.wide.length === 0, `${u} ${width}: wider than the screen ${JSON.stringify(m.wide)}`);
  check(m.small.length === 0, `${u} ${width}: targets under 24 px ${JSON.stringify(m.small)}`); check(m.tiny.length === 0, `${u} ${width}: text under 12 px ${JSON.stringify(m.tiny)}`); await ctx.close(); }

// 3. What a guide offers answers: its contents list travels to the section, the field leads to the app with the address typed,
//    the links to other guides and to the front page open a page that is there; on a phone the menu opens, closes on Escape and leads on.
{ const { p, ctx } = await open(1440); const guide = pages[1]; await p.goto(base + guide);
  const first = await p.evaluate(() => document.querySelector('.toc a').getAttribute('href')); await p.click('.toc a'); await p.waitForTimeout(300);
  check(await p.evaluate(id => { const r = document.querySelector(id).getBoundingClientRect(); return r.top >= 60 && r.top < innerHeight / 2; }, first), 'a contents link does not bring its heading under the bar');
  await p.fill('.cta input', 'https://example.com/shop'); await Promise.all([p.waitForURL(/\/app\?url=/), p.click('.cta button')]);
  check(new URL(p.url()).searchParams.get('url') === 'example.com/shop', 'the field does not lead to /app with the address: ' + p.url());
  const links = new Set(); for (const u of pages) { await p.goto(base + u); (await p.evaluate(() => [...document.querySelectorAll('a[href^="/"]')].map(a => a.getAttribute('href').split('#')[0]))).forEach(h => links.add(h)); }
  for (const h of links) { const r = await p.request.get(base + h); check(r.status() === 200, `a link of the blog leads nowhere: ${h} (${r.status()})`); }
  const nf = await p.goto(base + '/blog/no-such-guide'); check(nf.status() === 404 && await p.locator('a[href="/blog"]').count() > 0, 'an address that is not there does not answer 404 with a way onward'); await ctx.close(); }
{ const { p, ctx } = await open(390); await p.goto(base + pages[1]); const hidden = () => p.evaluate(() => document.getElementById('menu').hidden);
  check(await hidden(), 'the menu is open before it is asked for'); await p.click('.burger'); check(!(await hidden()) && await p.getAttribute('.burger', 'aria-expanded') === 'true', 'the menu does not open');
  await p.keyboard.press('Escape'); check(await hidden(), 'Escape does not close the menu'); await p.click('.burger'); await Promise.all([p.waitForURL(u => new URL(u).pathname === '/blog'), p.click('#menu a[href="/blog"]')]); await ctx.close(); }
await b.close(); server.close();
if (failures.length) { console.error(failures.join('\n')); process.exit(1); }
console.log('blog-layout: ok', pages.length, 'pages');
