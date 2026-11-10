// layout.mjs — is anything on this page broken as typesetting? Measured, at five widths, on any page.
//
//   node lib/qa/layout.mjs <page.html> [--widths 390,768,1100,1440,1920]   → one JSON line: {breaks: [...], widths, checked}
//
// The contract checks promises at 1440 and 390. This asks a different question, of every heading and paragraph, at the
// widths in between and beyond as well — because a column that is fine at 1440 was 186 px at 1800 on production:
//   stacked-words   a heading of five or more words on four or more lines, about one word to a line — a column of words, not a line
//   split-word      a word of a heading broken across two lines without a hyphen
//   lone-mark       a line of a heading that is only punctuation
//   thin-column     a paragraph set at fewer than 16 characters to the line
//   clipped         text cut off by the box that holds it, or running off the screen
//   overlap         a heading lying over other text
// Each break names its section (the nearest <section id>), so the loop can put that section back as it was.
// No model, no network beyond the page's own fonts. A break is a fact about the page, never a matter of taste.
import { chromium } from 'playwright'; import path from 'node:path';
const args = process.argv.slice(2); const file = path.resolve(args[0]);
const widths = (args.includes('--widths') ? args[args.indexOf('--widths') + 1] : '390,768,1100,1440,1920').split(',').map(Number);
const exe = process.env.CHROME_PATH || undefined;
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu'].concat(process.env.LIVETEST ? ['--proxy-server=direct://', '--proxy-bypass-list=*'] : []) });
const breaks = []; let checked = 0;
for (const width of widths) {
  const ctx = await browser.newContext({ viewport: { width, height: width < 600 ? 844 : 900 }, reducedMotion: 'reduce' }); const page = await ctx.newPage();
  await page.route(/^https?:\/\//, r => /fonts\.gstatic|fonts\.googleapis|cdnjs|unpkg/.test(r.request().url()) && process.env.LIVETEST ? r.abort() : r.continue()).catch(() => {});
  await page.goto('file://' + file + '?nomotion=1'); await page.waitForTimeout(400);
  await page.addStyleTag({ content: '[data-move],.sec *:not(.ps-s):not(.sp-f):not(.ps-s *):not(.sp-f *){opacity:1!important;transform:none!important;clip-path:none!important;filter:none!important}' }).catch(() => {});
  if (await page.locator('#sw-skip').count()) await page.click('#sw-skip', { timeout: 1000 }).catch(() => {});
  await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {}); await page.waitForTimeout(250);
  const found = await page.evaluate(() => {
    const W = innerWidth, out = []; let n = 0;
    const shown = el => { const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return false;
      for (let node = el; node; node = node.parentElement) { const s = getComputedStyle(node); if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) <= .05) return false; if (node.matches('details:not([open]) > :not(summary), [hidden], [aria-hidden="true"], .marquee, .mq, nav, .sr-only')) return false; }
      return true; };
    const where = el => { const s = el.closest('section[id],footer[id],header[id]'); return s ? s.id : null; };
    const say = el => (el.innerText || '').replace(/\s+/g, ' ').trim();
    // the words of an element with the line each one sits on: [{word, top, left, right, bottom, parts}]
    const words = el => { const list = []; const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let node;
      while ((node = walker.nextNode())) { if (!node.parentElement || !shown(node.parentElement)) continue; const re = /\S+/g; let m;
        while ((m = re.exec(node.data))) { const range = document.createRange(); range.setStart(node, m.index); range.setEnd(node, m.index + m[0].length);
          const rects = [...range.getClientRects()].filter(r => r.width > .5 && r.height > .5); if (!rects.length) continue;
          const tops = [...new Set(rects.map(r => Math.round(r.top)))]; const first = rects[0], last = rects[rects.length - 1];
          list.push({ word: m[0], top: first.top, bottom: first.bottom, left: first.left, right: first.right, parts: tops.length, lastRight: last.right }); } }
      return list; };
    const lines = ws => { const rows = []; for (const w of ws) { const row = rows.find(r => Math.abs(r.top - w.top) < Math.max(4, (w.bottom - w.top) * .45)); if (row) { row.words.push(w); row.left = Math.min(row.left, w.left); row.right = Math.max(row.right, w.right); row.bottom = Math.max(row.bottom, w.bottom); } else rows.push({ top: w.top, bottom: w.bottom, left: w.left, right: w.right, words: [w] }); } return rows.sort((a, b) => a.top - b.top); };
    const put = (kind, el, detail) => out.push({ kind, section: where(el), tag: el.tagName.toLowerCase(), text: say(el).slice(0, 70), detail });
    const heads = [...document.querySelectorAll('h1,h2,h3')].filter(shown);
    const headRows = new Map();
    for (const h of heads) { const ws = words(h); if (!ws.length) continue; n++; const rows = lines(ws); headRows.set(h, rows);
      const size = parseFloat(getComputedStyle(h).fontSize);
      // a word that was joined to its neighbour by markup (em, span) counts with it: "earn" + "?" is one word on one line or two
      if (ws.length >= 5 && rows.length >= 4 && ws.length / rows.length <= 1.5 && size >= 24) /* four words on four lines can be a poster; five and more is a column that is too narrow */ put('stacked-words', h, `${ws.length} words on ${rows.length} lines at ${Math.round(size)} px in ${Math.round(h.getBoundingClientRect().width)} px`);
      const split = ws.find(w => w.parts > 1 && !/[-‐‑­/]/.test(w.word)); if (split) put('split-word', h, `"${split.word}" is broken across lines`);
      const lone = rows.find(r => r.words.every(w => /^[^\p{L}\p{N}]+$/u.test(w.word)) && rows.length > 1); if (lone) put('lone-mark', h, `a line holds only "${lone.words.map(w => w.word).join(' ')}"`);
      for (const r of rows) if (r.right > W + 4 || r.left < -4) { put('clipped', h, `a line runs ${Math.round(Math.max(r.right - W, -r.left))} px off the screen`); break; }
      for (let box = h.parentElement; box && box !== document.body; box = box.parentElement) { const s = getComputedStyle(box); if (!/hidden|clip/.test(s.overflowX + s.overflowY)) continue; const b = box.getBoundingClientRect();
        const cut = rows.find(r => (/hidden|clip/.test(s.overflowX) && (r.right > b.right + 4 || r.left < b.left - 4)) || (/hidden|clip/.test(s.overflowY) && (r.bottom > b.bottom + 6 || r.top < b.top - 6)));
        if (cut && !box.matches('.mv-line,.ir-l,.dv-l') ) { put('clipped', h, 'a line is cut off by the box that holds it'); break; } } }
    for (const p of [...document.querySelectorAll('p,li,blockquote')].filter(shown)) { if (p.querySelector('p,li,ul,ol')) continue; const t = say(p); if (t.length < 90) continue; n++;
      const rows = lines(words(p)); if (rows.length < 4) continue; const per = t.length / rows.length;
      if (per < 16) put('thin-column', p, `${Math.round(per)} characters to the line over ${rows.length} lines in ${Math.round(p.getBoundingClientRect().width)} px`); }
    // a heading lying over other text: its lines against the lines of the text elements that are not its own
    const others = [...document.querySelectorAll('p,li,a.btn,button,h1,h2,h3,figcaption,.lab')].filter(shown);
    for (const [h, rows] of headRows) { const hs = where(h); const hr = h.getBoundingClientRect(); if (getComputedStyle(h).position === 'fixed') continue;
      for (const o of others) { if (o === h || o.contains(h) || h.contains(o) || where(o) !== hs) continue; const or = o.getBoundingClientRect();
        if (or.bottom <= hr.top || or.top >= hr.bottom || or.right <= hr.left || or.left >= hr.right) continue;
        const os = lines(words(o)); let over = 0;
        for (const a of rows) for (const b of os) { const w = Math.min(a.right, b.right) - Math.max(a.left, b.left), hgt = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top); if (w > 8 && hgt > Math.min(a.bottom - a.top, b.bottom - b.top) * .4) over += w * hgt; }
        if (over > 400) { put('overlap', h, `lies over "${say(o).slice(0, 40)}"`); break; } } }
    return { out, n };
  });
  checked += found.n; for (const b of found.out) breaks.push({ ...b, width });
  await ctx.close();
}
await browser.close();
// one break per (kind, section, text): the widths it shows at
const byKey = new Map();
for (const b of breaks) { const k = `${b.kind}|${b.section}|${b.text}`; const had = byKey.get(k); if (had) had.widths.push(b.width); else byKey.set(k, { kind: b.kind, section: b.section, tag: b.tag, text: b.text, detail: b.detail, widths: [b.width] }); }
console.log(JSON.stringify({ breaks: [...byKey.values()], widths, checked }));
