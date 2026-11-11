
import { chromium } from 'playwright'; import fs from 'node:fs';
const [,, file, dir] = process.argv; fs.mkdirSync(dir, { recursive: true });
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox', '--disable-gpu'] }); const out = { errors: [], shots: [], blocked: 0 };
for (const [name, w, h, cap] of [['desktop', 1440, 900, 5], ['phone', 390, 844, 4]]) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1, reducedMotion: 'reduce' }); const p = await ctx.newPage();
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:') || u.startsWith('data:') || /^https:\/\/fonts\.(googleapis|gstatic)\.com\//.test(u)) return r.continue(); out.blocked++; return r.abort(); });
  p.on('pageerror', e => out.errors.push(name + ': ' + String(e).slice(0, 160))); p.on('console', m => { if (m.type() === 'error') out.errors.push(name + ' console: ' + m.text().slice(0, 160)); });
  await p.goto('file://' + file, { waitUntil: 'load' }); await p.evaluate(() => document.fonts && document.fonts.ready).catch(() => {}); await p.waitForTimeout(900);
  // a page is photographed as a visitor who scrolled through it would have it: pictures loaded, things that arrive on scroll arrived
  await p.evaluate(() => document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager'));
  for (let y = 0, h = await p.evaluate(() => document.documentElement.scrollHeight); y < h; y += 700) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(70); }
  await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(500);
  const H = await p.evaluate(() => document.documentElement.scrollHeight); out[name] = { height: H, overflow: await p.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1) };
  const step = name === 'desktop' ? 1800 : 1900; let n = 0;
  for (let y = 0; y < H && n < cap * 2; y += step, n++) { const f = `${dir}/${name}-${String(n).padStart(2, '0')}.jpg`; await p.screenshot({ path: f, clip: { x: 0, y, width: w, height: Math.min(step, H - y) }, fullPage: true, type: 'jpeg', quality: 70 }); out.shots.push(f); }
  await ctx.close(); }
await b.close(); console.log(JSON.stringify(out));
