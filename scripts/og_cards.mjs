/* og_cards.mjs — the picture a shared link shows (og:image), 1200×630, one for each page that can be shared.
   Called by `python3 scripts/seo.py --cards` with the list on stdin: [{file, kicker, title, ground, tone, shot}].
   A card is the page's title in the site's display face beside one of our interface's screens on its made ground —
   the same picture the page opens with. Written to web/og/<file> as JPEG. Needs Chrome (CHROME_PATH) and the network
   for the three open-licence faces. */
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const WEB = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'web');
const list = JSON.parse(fs.readFileSync(0, 'utf8'));
const uri = (f, type) => `data:${type};base64,${fs.readFileSync(path.join(WEB, f)).toString('base64')}`;
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const page = c => `<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;1,400&family=Figtree:wght@500;600&family=Shrikhand&display=block" rel="stylesheet">
<style>*{box-sizing:border-box;margin:0}body{width:1200px;height:630px;background:#f4f2ec;color:#141414;font-family:Figtree,sans-serif;display:grid;grid-template-columns:560px 1fr;overflow:hidden}
.t{padding:56px 24px 52px 64px;display:flex;flex-direction:column}
.b{display:flex;align-items:center;gap:12px;font:400 30px/1 Shrikhand,serif}.b img{width:40px;height:40px;border-radius:50%}
.k{margin-top:auto;font:600 17px/1.3 Figtree;letter-spacing:.08em;text-transform:uppercase;color:#575755}
h1{margin-top:16px;font:400 ${c.title.length > 52 ? 54 : c.title.length > 36 ? 62 : 72}px/1 "EB Garamond",serif;letter-spacing:-.03em;text-wrap:balance}
.p{position:relative;margin:28px 28px 28px 0;border-radius:20px;overflow:hidden;display:flex;align-items:center;justify-content:center;padding:36px}
.p .g{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.p::after{content:"";position:absolute;inset:0;background:#f4f2ec;opacity:.18}
.p .s{position:relative;z-index:1;max-width:100%;max-height:100%;border-radius:6px;box-shadow:0 12px 40px rgba(0,0,0,.3)}</style>
<div class="t"><div class="b"><img src="${uri('logo/swarmsite-mark-192.webp', 'image/webp')}" alt="">swarmsite</div><p class="k">${esc(c.kicker)}</p><h1>${esc(c.title)}</h1></div>
<div class="p"><img class="g" src="${uri('visuals/' + c.ground + '.webp', 'image/webp')}" alt=""><img class="s" src="${uri('visuals/' + c.shot + '.webp', 'image/webp')}" alt=""></div>`;
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
const p = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
for (const c of list) {
  await p.setContent(page(c), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const faces = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/"/g, '')));
  for (const need of ['EB Garamond', 'Shrikhand', 'Figtree']) if (!faces.includes(need)) { console.error(`${c.file}: the face ${need} did not load — the card would be set in a fallback`); process.exit(1); }
  await p.screenshot({ path: path.join(WEB, 'og', c.file), type: 'jpeg', quality: 86 });
  console.log('card', c.file, Math.round(fs.statSync(path.join(WEB, 'og', c.file)).size / 1024) + ' KB');
}
await browser.close();
