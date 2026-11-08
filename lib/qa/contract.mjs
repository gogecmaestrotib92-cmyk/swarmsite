/* contract.mjs — THE CONTRACT. Mechanically checkable promises every page must keep, graded on the real render.
   Not taste: geometry, sizes, duplicates, limits. The critic grades taste; this grades the contract.
   node lib/qa/contract.mjs out/<slug>/bp-x.html --dir out/<slug>  → writes <dir>/contract.json and prints a JSON summary */
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path';
const args = process.argv.slice(2); const file = path.resolve(args[0]); const dir = args[args.indexOf('--dir') + 1] || path.dirname(file);
const chromePath = process.env.CHROME_PATH || '/usr/bin/google-chrome'; const exe = fs.existsSync(chromePath) ? chromePath : undefined;
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu'].concat(process.env.LIVETEST ? ['--proxy-server=direct://', '--proxy-bypass-list=*'] : []) });
const items = []; const add = (id, ok, detail, weight = 1) => items.push({ id, ok: !!ok, detail: String(detail || '').slice(0, 160), weight });

for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844, deviceScaleFactor: 2 }]]) {
  const ctx = await browser.newContext({ viewport: vp }); const page = await ctx.newPage(); await page.route(/^https?:\/\//, r => /fonts\.gstatic|fonts\.googleapis|cdnjs|unpkg/.test(r.request().url()) && process.env.LIVETEST ? r.abort() : r.continue()).catch(() => {});
  await page.goto('file://' + file + '?nomotion=1'); await page.waitForTimeout(500);
  await page.addStyleTag({ content: '[data-move],.sec *:not(.ps-s):not(.sp-f):not(.ps-s *):not(.sp-f *){opacity:1!important;transform:none!important;clip-path:none!important;filter:none!important}' }).catch(() => {});
  if (await page.locator('#sw-skip').count()) await page.click('#sw-skip', { timeout: 1000 }).catch(() => {});
  await page.waitForTimeout(300);
  const r = await page.evaluate(async () => {
    const W = innerWidth, H = innerHeight; const out = {};
    const txt = e => (e.innerText || '').trim();
    const vis = e => {
      const r = e.getBoundingClientRect();
      if (r.width <= 2 || r.height <= 2 || r.right <= 0 || r.left >= W) return false;
      for (let node = e; node; node = node.parentElement) {
        const style = getComputedStyle(node);
        if (style.visibility === 'hidden' || parseFloat(style.opacity) <= .05) return false;
      }
      return true;
    };
    // 1 — h1
    const h1 = document.querySelector('h1'); const h1w = h1 ? txt(h1).split(/\s+/).filter(Boolean).length : 0; out.h1 = { words: h1w, px: h1 ? parseFloat(getComputedStyle(h1).fontSize) : 0, lines: h1 ? Math.round(h1.getBoundingClientRect().height / parseFloat(getComputedStyle(h1).lineHeight || getComputedStyle(h1).fontSize)) : 0 };
    // 2 — first screen: a picture or a framed product visible?
    const imgs = [...document.querySelectorAll('img')].filter(vis);
    out.firstScreenImage = imgs.some(i => { const r = i.getBoundingClientRect(); return r.top < H && r.bottom > 0 && r.width >= W * .3 && r.height >= 120; });
    // 3 — images: natural size vs box (never upscaled > 1.35x), never duplicated
    const seen = new Map(); const bad = []; let dup = 0;
    for (const i of imgs) { const r = i.getBoundingClientRect(); if (r.width < 120 || r.height < 80) continue; const nw = i.naturalWidth || 0; const sc = nw ? (r.width * devicePixelRatio) / nw : 1;
      if (nw && sc > 1.35 && r.width > 300) bad.push(`${Math.round(r.width)}px box from ${nw}px source (x${sc.toFixed(2)})`);
      const src = i.currentSrc || i.src || ''; const key = src.length + '|' + src.slice(-240) + '|' + (i.getAttribute('style') || ''); if (seen.has(key)) dup++; else seen.set(key, 1); }
    out.upscaled = bad; out.duplicateImages = dup;
    // 4 — empty screens: measure each viewport at its actual scroll position so
    // sticky panels count only while visible and only where they contain content.
    const ph = document.documentElement.scrollHeight; const empties = [];
    const content = [...document.querySelectorAll('img, video, h1, h2, h3, p, li, summary, blockquote, figcaption, button, a.btn, input, .lab, .gw, .mq-track, .num')];
    for (let y = 0; y + H <= ph + 1; y += H * .5) {
      window.scrollTo(0, y);
      await new Promise(requestAnimationFrame);
      const rows = new Array(20).fill(0);
      for (const node of content) {
        if (!vis(node)) continue;
        if (node.matches('img') && !node.naturalWidth) continue;
        if (node.matches('h1, h2, h3, p, li, summary, blockquote, figcaption, button, a.btn, .lab, .gw, .mq-track, .num') && !txt(node)) continue;
        const rect = node.getBoundingClientRect();
        const top = Math.max(0, rect.top), bottom = Math.min(H, rect.bottom);
        if (bottom <= top) continue;
        const first = Math.floor(top / (H / 20));
        const last = Math.min(19, Math.floor((bottom - 1) / (H / 20)));
        for (let row = first; row <= last; row++) rows[row] = 1;
      }
      const fill = rows.reduce((sum, row) => sum + row, 0) / 20;
      const fullyVisible = node => {
        if (!node || !vis(node) || !txt(node)) return false;
        const rect = node.getBoundingClientRect();
        if (rect.top < 0 || rect.bottom > H || rect.left < 0 || rect.right > W) return false;
        const top = document.elementFromPoint((rect.left + rect.right) / 2, (rect.top + rect.bottom) / 2);
        return !!top && (node === top || node.contains(top));
      };
      // A complete, legible short numbers or CTA section may intentionally use
      // whitespace. It must fit in this viewport and expose its real content.
      const completeSection = [...document.querySelectorAll('.sec.numbers, .sec.cards, .sec.cta, .sec.typewall')].some(section => {
        if (section.classList.contains('typewall')) {
          const panel = section.querySelector('.tw-sticky');
          if (!panel || !vis(panel)) return false;
          const panelRect = panel.getBoundingClientRect();
          const heading = panel.querySelector('.tw');
          const caption = panel.querySelector('.tw-caption');
          return panelRect.top >= 0 && panelRect.bottom <= H && panelRect.height <= H &&
            fullyVisible(heading) && (!caption || fullyVisible(caption));
        }
        const rect = section.getBoundingClientRect();
        const visibleHeight = Math.max(0, Math.min(H, rect.bottom) - Math.max(0, rect.top));
        if (rect.height > H || visibleHeight < rect.height * .75 || !vis(section)) return false;
        if (section.classList.contains('numbers')) {
          return [...section.querySelectorAll('.nums > *')].filter(item =>
            fullyVisible(item.querySelector('.num')) && fullyVisible(item.querySelector('p'))).length >= 2;
        }
        if (section.classList.contains('cards')) {
          return [...section.querySelectorAll('.grid > .card')].filter(card =>
            fullyVisible(card.querySelector('h2, h3, .num')) && fullyVisible(card.querySelector('p'))).length >= 2;
        }
        return [...section.querySelectorAll('h1, h2, h3')].some(fullyVisible) &&
          [...section.querySelectorAll('a.btn[href]')].some(link => {
            const href = link.getAttribute('href') || '';
            const usable = href.startsWith('#') ? href.length > 1 && !!document.getElementById(href.slice(1)) : /^(https?:\/\/|mailto:|tel:)/i.test(href);
            return usable && fullyVisible(link);
          });
      });
      if (fill < .45 && !completeSection) empties.push({ y: Math.round(y), fill: +fill.toFixed(2) });
    }
    window.scrollTo(0, 0);
    out.emptyScreens = empties; out.pageScreens = +(ph / H).toFixed(1);
    // 5 — overflow: overflow-x:clip can hide text without increasing scrollWidth.
    const clipped = [];
    const checkedText = new Set();
    for (const el of document.querySelectorAll('.sec h1, .sec h2, .sec h3, .sec h4, .sec h5, .sec p, .sec li, .sec a, .sec button, .sec .lab')) {
      if (el.closest('.mq-track, .rail, [aria-hidden="true"]')) continue;
      let hidden = false;
      for (let node = el; node; node = node.parentElement) {
        const style = getComputedStyle(node);
        if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) <= .05 ||
            (node !== document.documentElement && node !== document.body && /^(auto|scroll)$/.test(style.overflowX) && node.scrollWidth > node.clientWidth + 2)) {
          hidden = true; break;
        }
      }
      if (hidden) continue;
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const textNode = walker.currentNode;
        if (checkedText.has(textNode) || !textNode.textContent.trim()) continue;
        checkedText.add(textNode);
        const range = document.createRange(); range.selectNodeContents(textNode);
        if ([...range.getClientRects()].some(rect => rect.width > 1 && rect.height > 1 && (rect.left < -2 || rect.right > W + 2))) {
          clipped.push((el.closest('section, footer')?.id || el.tagName.toLowerCase()) + ': ' + textNode.textContent.trim().slice(0, 45));
          break;
        }
      }
      if (clipped.length >= 5) break;
    }
    out.clippedText = clipped;
    out.overflowX = document.documentElement.scrollWidth > W + 2 || clipped.length > 0;
    // 6 — CTA consistency
    const btns = [...document.querySelectorAll('a.btn:not(.ghost), button.btn')].filter(vis).map(b => txt(b).replace(/\s*→\s*$/, '').trim()).filter(Boolean); out.ctas = [...new Set(btns)];
    out.actionableCta = [...document.querySelectorAll('a.btn:not(.ghost)')].filter(vis).some(a => {
      const href = a.getAttribute('href') || '';
      if (href.startsWith('#')) return href.length > 1 && !!document.getElementById(href.slice(1));
      return /^(https?:\/\/|mailto:|tel:)/i.test(href);
    });
    // 7 — h2 word counts
    out.h2 = [...document.querySelectorAll('h2.h2')].filter(vis).map(h => txt(h).split(/\s+/).filter(Boolean).length);
    // 8 — signature moves present & well formed
    out.sticky = [...document.querySelectorAll('[data-sig="sticky"]')].map(s => ({ frames: s.querySelectorAll('.sp-f img').length, rows: s.querySelectorAll('.sp-row').length, frameW: Math.round((s.querySelector('.sp-stage')?.getBoundingClientRect().width) || 0) }));
    out.pinned = [...document.querySelectorAll('[data-sig="pinned"]')].map(s => ({ slides: s.querySelectorAll('.ps-s').length }));
    // 9 — contrast proxy. Canvas normalizes all computed CSS color formats,
    // including color(srgb ...) returned by color-mix(), to RGBA pixels.
    const colorCanvas = document.createElement('canvas'); colorCanvas.width = colorCanvas.height = 1;
    const colorContext = colorCanvas.getContext('2d', { willReadFrequently: true });
    const rgba = color => {
      colorContext.clearRect(0, 0, 1, 1);
      colorContext.fillStyle = color;
      colorContext.fillRect(0, 0, 1, 1);
      return [...colorContext.getImageData(0, 0, 1, 1).data];
    };
    const composite = (front, back) => {
      const alpha = front[3] / 255;
      return front.slice(0, 3).map((channel, index) => channel * alpha + back[index] * (1 - alpha));
    };
    const luminance = color => (color[0] * .2126 + color[1] * .7152 + color[2] * .0722) / 255;
    const lowc = [];
    for (const p of [...document.querySelectorAll('.sec p, .sec li')].filter(vis).slice(0, 200)) {
      const foreground = rgba(getComputedStyle(p).color);
      if (foreground[3] <= 12) continue;
      const layers = [];
      for (let node = p; node; node = node.parentElement) layers.push(rgba(getComputedStyle(node).backgroundColor));
      let background = [255, 255, 255];
      for (const layer of layers.reverse()) background = composite(layer, background);
      if (Math.abs(luminance(composite(foreground, background)) - luminance(background)) < .25) lowc.push(txt(p).slice(0, 30));
    }
    out.lowContrast = lowc.slice(0, 5);
    // 10 — meaningful sections, independent of how much source content a site has.
    // A hard upper limit silently rewards dropping legitimate offers and FAQs.
    const sections = [...document.querySelectorAll('body > section, body > footer')];
    out.sections = sections.length;
    out.emptySections = sections.filter(section => !txt(section) && ![...section.querySelectorAll('img,video,canvas,svg')].some(vis)).map(section => section.id || section.className || section.tagName).slice(0, 6);
    const seenSectionText = new Map(); out.duplicateSections = [];
    for (const [index, section] of sections.entries()) {
      // innerText excludes answers in closed details, so include their text in
      // the comparison to distinguish FAQs with the same questions but different answers.
      const detailsText = [...section.querySelectorAll('details')].map(d => d.textContent || '').join(' ');
      const content = (txt(section) + ' ' + detailsText).replace(/\s+/g, ' ').trim().toLocaleLowerCase();
      // Do not flag a repeated short CTA; require identical substantive text.
      if (content.length < 50) continue;
      if (seenSectionText.has(content)) out.duplicateSections.push(`${seenSectionText.get(content)} / ${section.id || index + 1}`);
      else seenSectionText.set(content, section.id || String(index + 1));
    }
    out.hasForm = !!document.querySelector('form input');
    return out; });
  const m = name === 'mobile';
  if (!m) { add('h1-words', r.h1.words >= 2 && r.h1.words <= 8, `${r.h1.words} words`, 2); add('h1-lines', r.h1.lines <= 3, `${r.h1.lines} lines`); add('h1-size', r.h1.px >= 48, `${Math.round(r.h1.px)}px`); }
  add(`${name}-first-screen-visual`, r.firstScreenImage, r.firstScreenImage ? 'a picture or product is visible in the first screen' : 'no visual in the first screen', 3);
  add(`${name}-no-upscaled-images`, r.upscaled.length === 0, r.upscaled.join('; ') || 'ok', 2);
  add(`${name}-no-duplicate-images`, r.duplicateImages === 0, r.duplicateImages ? `${r.duplicateImages} repeated picture(s)` : 'ok', 3);
  add(`${name}-no-empty-screens`, r.emptyScreens.length === 0, r.emptyScreens.length ? `${r.emptyScreens.length} half-empty screen(s) at y=${r.emptyScreens.map(e => e.y).slice(0, 4).join(',')}` : 'ok', 3);
  add(`${name}-no-overflow`, !r.overflowX, r.clippedText.length ? `clipped text: ${r.clippedText.join(' / ')}` : r.overflowX ? 'horizontal overflow' : 'ok', 2);
  add(`${name}-actionable-cta`, r.actionableCta, r.actionableCta ? 'primary action has a destination' : 'no primary action with a usable destination', 3);
  if (!m) { add('one-cta', r.ctas.length <= 2, r.ctas.join(' | '), 2); add('h2-short', r.h2.every(n => n <= 7), `h2 words: ${r.h2.join(',')}`); add('page-length', r.pageScreens >= 1, `${r.pageScreens} screens`, 2); add('sections', r.sections >= 1 && r.emptySections.length === 0 && r.duplicateSections.length === 0, r.emptySections.length ? `empty sections: ${r.emptySections.join(', ')}` : r.duplicateSections.length ? `duplicate sections: ${r.duplicateSections.slice(0, 4).join(', ')}` : `${r.sections} sections`); }
  add(`${name}-sticky-frames`, r.sticky.every(s => s.frames >= 2 && s.frames === s.rows && s.frameW >= 300), JSON.stringify(r.sticky) || 'none', 2);
  add(`${name}-pinned-slides`, r.pinned.every(s => s.slides >= 2 && s.slides <= 5), JSON.stringify(r.pinned) || 'none');
  add(`${name}-contrast`, r.lowContrast.length === 0, r.lowContrast.join(' / ') || 'ok', 3);
  await ctx.close();
}
await browser.close();
const total = items.reduce((p, i) => p + i.weight, 0); const got = items.filter(i => i.ok).reduce((p, i) => p + i.weight, 0);
const rep = { score: Math.round(100 * got / total), passed: items.filter(i => i.ok).length, failed: items.filter(i => !i.ok).map(i => ({ id: i.id, detail: i.detail, weight: i.weight })), items };
fs.writeFileSync(path.join(dir, 'contract.json'), JSON.stringify(rep, null, 1)); console.log(JSON.stringify({ score: rep.score, passed: rep.passed, failed: rep.failed.map(f => f.id + ': ' + f.detail) }));
