// Our own landing is held to what a client's page is held to: no layout break at five widths, a headline that stands
// in time, nothing left hidden, nothing that does not answer — and no ground of one section lying over the next.
//   node tests/landing-layout.mjs            the landing in web/
//   LANDING_DIR=<folder> node tests/…        another copy of it (the one before a change, to see what a check names there)
import assert from 'node:assert/strict'; import fs from 'node:fs'; import http from 'node:http'; import path from 'node:path'; import { spawn } from 'node:child_process'; import { fileURLToPath } from 'node:url'; import { chromium } from 'playwright';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..'); const web = path.resolve(process.env.LANDING_DIR || path.join(root, 'web'));
const TYPES = { html: 'text/html; charset=utf-8', css: 'text/css', js: 'text/javascript', webp: 'image/webp', woff2: 'font/woff2', svg: 'image/svg+xml', gif: 'image/gif', png: 'image/png', jpg: 'image/jpeg', json: 'application/json', txt: 'text/plain', xml: 'text/xml' };
const server = http.createServer((req, res) => { const name = decodeURIComponent(req.url.split('?')[0]); let file = path.join(web, name.endsWith('/') ? name + 'index.html' : name); if (!path.extname(file) && fs.existsSync(file + '.html')) file += '.html';   // /app is app.html, as vercel.json's cleanUrls serves it
  if (!file.startsWith(web) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file).slice(1)] || 'application/octet-stream' }); fs.createReadStream(file).pipe(res); });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const url = `http://127.0.0.1:${server.address().port}/`;
const failures = []; const check = (ok, what) => { if (!ok) failures.push(what); };

// 1. The layout gate, as scripts/livetest.sh runs it on every blueprint. (Run beside this process: the page is served from it.)
const lay = await new Promise(done => { const p = spawn('node', [path.join(root, 'lib/qa/layout.mjs'), url], { env: { ...process.env, LIVETEST: '1' } }); let out = '', err = ''; p.stdout.on('data', d => out += d); p.stderr.on('data', d => err += d); p.on('close', status => done({ status, out, err })); });
assert.equal(lay.status, 0, lay.err); const breaks = JSON.parse(lay.out.trim().split('\n').pop()).breaks;
check(breaks.length === 0, 'layout breaks: ' + JSON.stringify(breaks.map(b => `${b.kind}@${b.section} ${b.widths} “${b.text}” ${b.detail}`)));

const b = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
const open = async (width, motion, height = 900) => { const ctx = await b.newContext({ viewport: { width, height }, reducedMotion: motion, hasTouch: width < 600, isMobile: width < 600 }); const p = await ctx.newPage();
  const errors = []; p.on('pageerror', e => errors.push(String(e))); p.on('response', r => { if (r.status() >= 400 && r.url().startsWith(url) && !/favicon/.test(r.url())) errors.push(`${r.status()} ${r.url().slice(url.length - 1)}`); });
  await p.route(/^https?:\/\/(?!127\.0\.0\.1)/, r => r.abort()); return { p, errors, ctx }; };

// 2. The headline stands whole within 1.5 s of the address being asked for and stays so (Standard MOT-03 / T-15), on a desk where the crew builds
//    the rest. Read inside the page, frame by frame for four seconds, as the last moment it was hidden, moving or incomplete: a headline that is
//    there at first and then taken away to be typed (the landing before this test) is late by this reading, and a slow test machine does not make a sound page late.
{ const { p, ctx } = await open(1440, 'no-preference');
  await p.addInitScript(() => { const whole = () => { const h = document.querySelector('h1'); if (!h || !/A better website\.\s*Built from yours\./.test(h.textContent.replace(/\s+/g, ' '))) return false;
      for (let n = h; n; n = n.parentElement) { const c = getComputedStyle(n); if (c.visibility === 'hidden' || c.display === 'none' || parseFloat(c.opacity) < .95) return false; }
      return [...h.querySelectorAll('*')].every(x => { const c = getComputedStyle(x); if (x.closest('svg')) return true; const m = c.transform; return c.visibility !== 'hidden' && parseFloat(c.opacity) > .95 && (m === 'none' || m === 'matrix(1, 0, 0, 1, 0, 0)'); }); };
    window.__late = 0; const tick = () => { const now = performance.now(); if (!whole()) window.__late = now; if (now < 4000) requestAnimationFrame(tick); }; requestAnimationFrame(tick); });
  await p.goto(url); await p.waitForTimeout(4300); const late = Math.round(await p.evaluate(() => window.__late));
  check(late <= 1500, `the headline is not standing whole until ${late} ms (asked: 1500)`); await ctx.close(); }

// 3. Scrolled from top to bottom at a desk, a phone and for a visitor who asked for less motion: no script error, no file missing, nothing left hidden, no sideways scroll.
for (const [width, motion] of [[1440, 'no-preference'], [390, 'no-preference'], [1440, 'reduce'], [390, 'reduce']]) {
  const { p, errors, ctx } = await open(width, motion, width < 600 ? 844 : 900); await p.goto(url); await p.waitForTimeout(width > 900 && motion !== 'reduce' ? 5500 : 800);   // the crew has finished
  const H = await p.evaluate(() => document.documentElement.scrollHeight); for (let y = 0; y <= H; y += 500) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(60); } await p.waitForTimeout(3200);   // the window has shown both of its states
  const hidden = await p.evaluate(() => [...document.querySelectorAll('h1,h2,h3,p,li,a,button,summary,input,img')].filter(e => { const r = e.getBoundingClientRect(); if (r.width < 2 || e.closest('.dv-menu:not(.is-open), .case-pane:not(.is-on), details:not([open]) > :not(summary), .pinned .st:not(.on) .tx, .pinned .vin, .pinned .kc, .pinned .vis, [hidden]')) return false;
    let seen = 1; for (let n = e; n && n !== document.body; n = n.parentElement) { const c = getComputedStyle(n); if (c.visibility === 'hidden') return true; seen *= parseFloat(c.opacity); } return seen < .05; }).map(e => (e.textContent || e.alt || e.tagName).trim().slice(0, 30))
    .concat([...document.querySelectorAll('.dv-ln > span')].filter(s => !/^(none|matrix\(1, 0, 0, 1, 0, 0\))$/.test(getComputedStyle(s).transform)).map(s => 'still behind its mask: ' + s.textContent.trim().slice(0, 24))));   // a line that never rose is hidden by its mask, not by opacity
  check(errors.length === 0, `${width}/${motion}: errors ${JSON.stringify(errors)}`); check(hidden.length === 0, `${width}/${motion}: left hidden ${JSON.stringify(hidden)}`);
  check(!(await p.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1)), `${width}/${motion}: the page scrolls sideways`); await ctx.close(); }

// 4. No painted box of a section reaches outside it. On the landing before this test a ground spilled 77 px over the next section
//    and a dark block stood on it short of both screen edges at 1920; lib/qa/layout.mjs reads typesetting and does not see grounds.
for (const width of [390, 1440, 1920]) { const { p, ctx } = await open(width, 'reduce', width < 600 ? 844 : 1000); await p.goto(url); await p.waitForTimeout(700);
  const spills = await p.evaluate(() => { const out = []; const painted = c => c.backgroundImage !== 'none' || !/^rgba\(0, 0, 0, 0\)$|^transparent$/.test(c.backgroundColor);
    for (const sec of document.querySelectorAll('main > section, body > section, body > footer')) { const s = sec.getBoundingClientRect();
      const within = (el, box) => { for (let n = el; n && n !== sec.parentElement; n = n.parentElement) { if (n !== el || box.self) { const c = getComputedStyle(n); if (/hidden|clip/.test(c.overflowY)) { const r = n.getBoundingClientRect(); box.top = Math.max(box.top, r.top); box.bottom = Math.min(box.bottom, r.bottom); } } } return box; };
      const judge = (el, box, name) => { box = within(el, box); if (box.bottom - box.top < 2 || box.right - box.left < 2) return; const over = Math.max(s.top - box.top, box.bottom - s.bottom); if (over > 2) out.push(`${name} of #${sec.id || sec.className} reaches ${Math.round(over)} px outside it`); };
      for (const el of sec.querySelectorAll('*')) { const c = getComputedStyle(el); if (c.display === 'none' || c.visibility === 'hidden' || c.position === 'fixed') continue; const r = el.getBoundingClientRect();
        if (painted(c)) judge(el, { top: r.top, bottom: r.bottom, left: r.left, right: r.right }, `<${el.tagName.toLowerCase()} class="${el.className}">`);
        for (const side of ['::before', '::after']) { const pc = getComputedStyle(el, side); if (pc.content === 'none' || pc.display === 'none' || pc.position !== 'absolute' || c.position === 'static' || !painted(pc)) continue;
          judge(el, { top: r.top + (parseFloat(pc.top) || 0), bottom: r.bottom - (parseFloat(pc.bottom) || 0), left: r.left + (parseFloat(pc.left) || 0), right: r.right - (parseFloat(pc.right) || 0), self: true }, `${side} of <${el.tagName.toLowerCase()} class="${el.className}">`); } } }
    return out; });
  check(spills.length === 0, `${width}: ${JSON.stringify(spills.slice(0, 4))}`); await ctx.close(); }

// 5. What the page offers answers: a link in the bar travels to its section; every link to #top ends in the address field; the field
//    leads to the app (with the way in the visitor chose); on a phone every target is big enough, and the menu opens, closes on Escape
//    and closes when one of its links is pressed. (Rewritten 2026-11-12 for the landing on the library template; the curtain foot is gone.)
{ const { p, ctx } = await open(1440, 'no-preference'); await p.goto(url); await p.waitForTimeout(1200);
  await p.click('.nvl a[href="#faq"]'); await p.waitForTimeout(1600); const top = Math.round(await p.evaluate(() => document.querySelector('#faq').getBoundingClientRect().top));
  check(top > 20 && top < 200, `the FAQ link does not travel to its section (the section stands ${top} px from the top)`);
  await p.evaluate(() => scrollTo(0, document.documentElement.scrollHeight)); await p.waitForTimeout(400); await p.click('.fi a[href="#site"]').catch(() => {}); await p.waitForTimeout(900);
  check(await p.evaluate(() => document.activeElement.id) === 'url', '"Paste your address" does not end in the address field');
  await p.fill('#url', 'https://example.com/'); await Promise.all([p.waitForURL(/\/app\?url=example\.com%2F$/, { timeout: 4000 }).catch(() => {}), p.press('#url', 'Enter')]); check(/\/app\?url=example\.com%2F$/.test(p.url()), 'the field does not lead to the app: ' + p.url());
  await p.goto(url); await p.waitForTimeout(600); await p.click('.ways [data-way="app"]'); await p.fill('#url', 'example.com'); await Promise.all([p.waitForURL(/with=screens/, { timeout: 4000 }).catch(() => {}), p.press('#url', 'Enter')]);
  check(/\/app\?url=example\.com&with=screens$/.test(p.url()), '"I built a first version of my app" does not lead to the screenshots: ' + p.url());
  await p.goto(url); await p.waitForTimeout(600); await p.click('.ways [data-way="none"]');
  check(await p.locator('#url').isHidden() && await p.locator('.alt a[href="/start"]').isVisible(), '"I don’t have a site" does not offer the form'); await ctx.close(); }
{ const { p, ctx } = await open(390, 'no-preference', 844); await p.goto(url); await p.waitForTimeout(600);
  const small = await p.evaluate(() => [...document.querySelectorAll('a,button,summary,input,select')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden' && !e.closest('[hidden]') && Math.min(r.width, r.height) < 24; }).map(e => e.textContent.trim().slice(0, 24)));
  check(small.length === 0, 'targets under 24 px on a phone (WCAG 2.5.8): ' + JSON.stringify(small));
  await p.click('.burger'); await p.waitForTimeout(300); check(await p.locator('#menu a').first().isVisible(), 'the phone menu does not open');
  await p.keyboard.press('Escape'); await p.waitForTimeout(200); check(await p.getAttribute('.burger', 'aria-expanded') === 'false', 'Escape does not close the phone menu');
  await p.click('.burger'); await p.waitForTimeout(300); await p.click('#menu a[href="#faq"]'); await p.waitForTimeout(300);
  check(await p.getAttribute('.burger', 'aria-expanded') === 'false', 'a link pressed in the phone menu leaves it open'); await ctx.close(); }

// 6. (The words on the ink ribbon, .rib, are ground-coloured on its stroke: a reading of computed colours cannot see a stroke, so they are
//    judged on pixels by lib/qa/template_gate.mjs's legible check instead.) Every word can be read on the ground it stands on — and so can what a visitor types, in both fields, the one on the night too
//    (4.5:1; 3:1 from 24 px). Read with motion off: nothing is half-lit and the crew is not building.
for (const width of [1440, 390]) { const { p, ctx } = await open(width, 'reduce', width < 600 ? 844 : 900); await p.goto(url); await p.waitForTimeout(700);
  const low = await p.evaluate(() => { const out = [];
    const lum = c => { const [r, g, b] = c.map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }); return .2126 * r + .7152 * g + .0722 * b; };
    const parse = s => { const m = String(s).match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(/[,\s\/]+/).filter(Boolean).map(Number); return { rgb: v.slice(0, 3), a: v[3] === undefined ? 1 : v[3] }; };
    const ground = el => { for (let n = el; n; n = n.parentElement) { const c = parse(getComputedStyle(n).backgroundColor); if (c && c.a > .5) return c.rgb; } return [255, 255, 255]; };
    const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walk.nextNode()) { const t = walk.currentNode, el = t.parentElement; if (!t.data.trim() || !el || el.closest('script,style,.dv-menu:not(.is-open),details:not([open]) > :not(summary),.rib,[hidden]')) continue;
      const cs = getComputedStyle(el), r = el.getBoundingClientRect(), ink = parse(cs.color); if (r.width < 2 || cs.visibility === 'hidden' || !ink) continue;
      const px = parseFloat(cs.fontSize), got = ratio(ink.rgb, ground(el)); if (got < (px >= 24 ? 3 : 4.5)) out.push(`“${t.data.trim().slice(0, 28)}” ${got.toFixed(1)}:1 at ${Math.round(px)} px`); }
    for (const f of document.querySelectorAll('input')) { const g = ground(f), typed = ratio(parse(getComputedStyle(f).color).rgb, g), hint = ratio(parse(getComputedStyle(f, '::placeholder').color).rgb, g);
      if (typed < 4.5) out.push(`what is typed into #${f.id} ${typed.toFixed(1)}:1`); if (hint < 4.5) out.push(`the hint in #${f.id} ${hint.toFixed(1)}:1`); }
    return out; });
  check(low.length === 0, `${width}: too faint to read ${JSON.stringify(low.slice(0, 8))}`); await ctx.close(); }
await b.close(); server.close();
assert.deepEqual(failures, [], failures.join('\n'));
console.log(`Landing (${path.relative(root, web) || web}): no layout break at five widths, the headline stands by 1.5 s, nothing hidden, nothing spilling, every word and every field readable, links, the field and the menu answer`);
