/* measure.mjs — what only a browser knows about a first screen: how wide its headline really sets, and where things land.
   node lib/compose/measure.mjs page.html      → one JSON line
   {"fit": {"line": em, "word": em} | null,     the widest line (hand-broken headlines: scale and indent counted) and the
                                                widest word of the headline, in em of the headline's own size, in the face
                                                the page loads. A composition carries these as `fit` and is sized from them.
    "desktop": {"wrapped": [...], "actions_bottom": px, "fold": px}, "mobile": {...}}
   `wrapped` lists hand-broken lines that did not stay on one line; `actions_bottom` is where the first button ends.
   Works on any page with a hero; `fit` and `wrapped` need a composed one. Motion is off, as for the contract. */
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path';
const file = path.resolve(process.argv[2]);
const mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chromePath = process.env.CHROME_PATH || (fs.existsSync(mac) ? mac : '/usr/bin/google-chrome');
const browser = await chromium.launch({ executablePath: fs.existsSync(chromePath) ? chromePath : undefined, args: ['--no-sandbox', '--disable-gpu'].concat(process.env.LIVETEST ? ['--proxy-server=direct://', '--proxy-bypass-list=*'] : []) });
const out = { fit: null };
for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844 }]]) {
  const ctx = await browser.newContext({ viewport: vp }); const page = await ctx.newPage();
  await page.route(/^https?:\/\//, r => /fonts\.gstatic|fonts\.googleapis|cdnjs|unpkg/.test(r.request().url()) && process.env.LIVETEST ? r.abort() : r.continue()).catch(() => {});
  await page.goto('file://' + file + '?nomotion=1'); await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {}); await page.waitForTimeout(350);
  const seen = await page.evaluate(() => {
    const hero = document.querySelector('.sec.hero'); const h1 = hero && hero.querySelector('h1'); if (!h1) return null;
    const base = parseFloat(getComputedStyle(h1).fontSize) || 1; const lines = [...h1.querySelectorAll('.ir-l')];
    // a probe inside the headline inherits its face, weight, tracking and case: what it measures is what is drawn
    const probe = document.createElement('span'); probe.style.cssText = 'position:absolute;left:-99999px;top:0;white-space:nowrap;visibility:hidden;display:inline-block;padding:0';
    h1.appendChild(probe);
    const width = (html, scale) => { probe.style.fontSize = scale + 'em'; probe.innerHTML = html; return probe.getBoundingClientRect().width / base; };
    const escape = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;');
    const text = lines.length ? lines.map(l => l.textContent).join(' ') : [...h1.childNodes].filter(n => n !== probe).map(n => n.textContent).join('');
    const word = Math.max(0, ...text.split(/\s+/).filter(Boolean).map(w => width(escape(w), 1)));
    let line = word; const wrapped = [];
    if (lines.length) {
      line = 0;
      lines.forEach((l, i) => {
        const inner = l.querySelector('.mv-line-in') || l; const cs = getComputedStyle(l); const scale = (parseFloat(cs.fontSize) || base) / base;
        const style = l.getAttribute('style') || ''; const ind = /--ind:\s*([\d.]+)em/.exec(style); const ls = /--ls:\s*([\d.]+)/.exec(style);   // from the markup: on a phone the line may be drawn without them
        const declared = ls ? parseFloat(ls[1]) : 1;
        line = Math.max(line, width(inner.innerHTML, declared) + (ind ? parseFloat(ind[1]) * declared : 0));
        if (cs.display === 'block') { const rows = new Set([...inner.getClientRects()].map(r => Math.round(r.top))).size; if (rows > 1 || l.scrollWidth > l.clientWidth + 1) wrapped.push({ line: i + 1, text: l.textContent.trim(), rows, over: Math.max(0, l.scrollWidth - l.clientWidth) }); }
      });
    }
    probe.remove();
    const button = hero.querySelector('.btn'); const r = button && button.getBoundingClientRect();
    return { composed: hero.classList.contains('ir'), lined: lines.length > 0, line: +line.toFixed(3), word: +word.toFixed(3), px: Math.round(base), wrapped, actions_bottom: r ? Math.round(r.bottom + scrollY) : null, fold: innerHeight };
  });
  if (seen) {
    if (name === 'desktop' && seen.composed && seen.line > 0) out.fit = { line: seen.line, word: seen.word };
    out[name] = { wrapped: seen.wrapped, actions_bottom: seen.actions_bottom, fold: seen.fold, h1_px: seen.px };
  } else out[name] = null;
  await ctx.close();
}
await browser.close(); console.log(JSON.stringify(out));
