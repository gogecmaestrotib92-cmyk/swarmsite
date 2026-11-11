/* contract.mjs — THE CONTRACT. Mechanically checkable promises every page must keep, graded on the real render.
   Not taste: geometry, sizes, duplicates, limits. The critic grades taste; this grades the contract.
   node lib/qa/contract.mjs out/<slug>/bp-x.html --dir out/<slug>  → writes <dir>/contract.json and prints a JSON summary */
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path';
const args = process.argv.slice(2); const file = path.resolve(args[0]); const dir = args[args.indexOf('--dir') + 1] || path.dirname(file);
const chromePath = process.env.CHROME_PATH || '/usr/bin/google-chrome'; const exe = fs.existsSync(chromePath) ? chromePath : undefined;
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu'].concat(process.env.LIVETEST ? ['--proxy-server=direct://', '--proxy-bypass-list=*'] : []) });
const items = []; const add = (id, ok, detail, weight = 1) => items.push({ id, ok: !!ok, detail: String(detail || '').slice(0, 160), weight });

for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844, deviceScaleFactor: 2 }]]) {
  const ctx = await browser.newContext({ viewport: vp, reducedMotion: 'reduce' }); const page = await ctx.newPage(); await page.route(/^https?:\/\//, r => /fonts\.gstatic|fonts\.googleapis|cdnjs|unpkg/.test(r.request().url()) && process.env.LIVETEST ? r.abort() : r.continue()).catch(() => {});
  await page.goto('file://' + file + '?nomotion=1'); await page.waitForTimeout(500);
  await page.addStyleTag({ content: '[data-move],.sec *:not(.ps-s):not(.sp-f):not(.ps-s *):not(.sp-f *){opacity:1!important;transform:none!important;clip-path:none!important;filter:none!important}' }).catch(() => {});
  if (await page.locator('#sw-skip').count()) await page.click('#sw-skip', { timeout: 1000 }).catch(() => {});
  await page.waitForTimeout(300);
  const r = await page.evaluate(async () => {
    const W = innerWidth, H = innerHeight; const out = {};
    const txt = e => (e.innerText || '').trim();
    // What a control says: its accessible name. A label doubled for a hover effect is hidden from readers and carries the name once.
    const said = e => { const own = e.getAttribute('aria-label'); if (own) return own; const c = e.cloneNode(true); c.querySelectorAll('[aria-hidden="true"]').forEach(x => x.remove()); return c.textContent || ''; };
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
    const h1 = document.querySelector('h1'); const h1w = h1 ? txt(h1).split(/\s+/).filter(Boolean).length : 0; // The size and the lines are read off the words themselves: a headline set by a span inside the h1 is as large as that
    // span makes it, and a line is a row of words wherever the boxes around them end.
    const h1px = () => { let px = 0; const w = document.createTreeWalker(h1, NodeFilter.SHOW_TEXT); while (w.nextNode()) if (w.currentNode.textContent.trim()) px = Math.max(px, parseFloat(getComputedStyle(w.currentNode.parentElement).fontSize) || 0); return px || parseFloat(getComputedStyle(h1).fontSize); };
    const h1lines = () => { const rows = []; const w = document.createTreeWalker(h1, NodeFilter.SHOW_TEXT); while (w.nextNode()) { if (!w.currentNode.textContent.trim()) continue; const range = document.createRange(); range.selectNodeContents(w.currentNode); for (const r of range.getClientRects()) { if (r.width < 1 || r.height < 1) continue; const mid = (r.top + r.bottom) / 2; if (!rows.some(y => Math.abs(y - mid) < r.height * .5)) rows.push(mid); } } return rows.length; };
    out.h1 = { words: h1w, px: h1 ? h1px() : 0, lines: h1 ? h1lines() : 0 };
    // 2 — first screen: a picture or a framed product visible?
    const imgs = [...document.querySelectorAll('img')].filter(vis);
    // A figure that lays several pictures on each other (pages of a document, covers) is one visual: it registers by the
    // room its pictures take together, as long as each of them is a picture in its own right and not an icon in a row.
    const stacks = [...document.querySelectorAll('figure')].map(f => [...f.querySelectorAll('img')].filter(vis).map(i => i.getBoundingClientRect())).filter(g => g.length > 1 && g.every(r => r.width >= W * .15 && r.height >= 120));
    const together = g => ({ top: Math.min(...g.map(r => r.top)), bottom: Math.max(...g.map(r => r.bottom)), width: Math.max(...g.map(r => r.right)) - Math.min(...g.map(r => r.left)) });
    // what counts is the part of the picture inside the first screen: a picture whose top edge alone shows above the fold is not seen
    out.firstScreenImage = imgs.some(i => { const r = i.getBoundingClientRect(); return Math.min(H, r.bottom) - Math.max(0, r.top) >= 120 && r.width >= W * .3; })
      || stacks.some(g => { const r = together(g); return r.top < H && r.bottom > 0 && r.width >= W * .3; });
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
    for (const el of document.querySelectorAll(':is(.sec, .sc) :is(h1, h2, h3, h4, h5, p, li, a, button, .lab), .sec .card .num')) {
      if (el.closest('.mq-track, .rail, .dv-rail, .dv-kinetic, .dv-tick, [aria-hidden="true"]')) continue;
      // This generated provenance label is intentionally clipped to one pixel
      // for screen readers. Do not exempt visible labels or their actual links.
      const ownStyle = getComputedStyle(el);
      if (el.classList.contains('source-actions-label') && ownStyle.position === 'absolute' &&
          ownStyle.clip === 'rect(0px, 0px, 0px, 0px)' && el.offsetWidth <= 1 && el.offsetHeight <= 1) continue;
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
        const card = el.matches('.card .num') ? el.closest('.card')?.getBoundingClientRect() : null;
        if ([...range.getClientRects()].some(rect => rect.width > 1 && rect.height > 1 && (rect.left < -2 || rect.right > W + 2 || (card && (rect.left < card.left - 2 || rect.right > card.right + 2))))) {
          clipped.push((el.closest('section, footer')?.id || el.tagName.toLowerCase()) + ': ' + textNode.textContent.trim().slice(0, 45));
          break;
        }
      }
      if (clipped.length >= 5) break;
    }
    out.clippedText = clipped;
    out.overflowX = document.documentElement.scrollWidth > W + 2 || clipped.length > 0;
    // 6 — compare the primary destination in nav, hero and closing CTA only.
    // Individual source-backed sections can have different, legitimate actions.
    const primarySelector = 'a.btn:not(.ghost):not(.quiet)[href]';
    const closing = [...document.querySelectorAll('section.sec.cta, footer.sc.close')].at(-1);
    const primaryLinks = [document.querySelector('nav.nav, header.bar'), document.querySelector('section.hero, section.sc.open'), closing]
      .map(region => region && [...region.querySelectorAll(primarySelector)].find(vis)).filter(Boolean);
    const destination = (link, visited = new Set()) => {
      const href = (link.getAttribute('href') || '').trim();
      if (href.startsWith('#') && href.length > 1) {
        const id = href.slice(1); if (visited.has(id)) return href;
        visited.add(id); const section = document.getElementById(id);
        const next = section && [...section.querySelectorAll(primarySelector)].find(vis);
        return next ? destination(next, visited) : href;
      }
      try { const u = new URL(href, 'https://contract.invalid/'); u.hash = ''; u.pathname = u.pathname.replace(/\/$/, '') || '/'; return u.href; }
      catch { return href; }
    };
    out.ctas = [...new Set(primaryLinks.map(link => destination(link)).filter(Boolean))];
    // one page, one ask: every solid button on the page (nav, hero, sections, closing) must say one of at most two things
    out.ctaTexts = [...new Set([...document.querySelectorAll('a.btn:not(.ghost):not(.quiet), button.btn:not(.ghost):not(.quiet)')].filter(vis).map(a => said(a).replace(/\s+/g, ' ').replace(/[→↗]/g, '').trim().toLowerCase()).filter(t => t && t.length < 60))];
    out.actionableCta = [...document.querySelectorAll('a.btn:not(.ghost):not(.quiet)')].filter(vis).some(a => {
      const href = a.getAttribute('href') || '';
      if (href.startsWith('#')) return href.length > 1 && !!document.getElementById(href.slice(1));
      return /^(https?:\/\/|mailto:|tel:)/i.test(href);
    });
    // 7 — h2 word counts
    out.h2 = [...document.querySelectorAll('h2.h2, .sc h2')].filter(vis).map(h => txt(h).split(/\s+/).filter(Boolean).length);
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
    for (const p of [...document.querySelectorAll(':is(.sec, .sc) :is(p, li)')].filter(vis).slice(0, 200)) {
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
    const sections = [...document.querySelectorAll('body > section, body > footer, body > main > section')];
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
  if (!m) { add('one-cta', r.ctas.length <= 1 && (r.ctaTexts || []).length <= 2, (r.ctaTexts || []).length > 2 ? `${r.ctaTexts.length} different button texts: ${r.ctaTexts.slice(0, 4).join(' | ')}` : (r.ctas.join(' | ') || 'no comparable primary destinations'), 2); add('h2-short', r.h2.every(n => n <= 7), `h2 words: ${r.h2.join(',')}`); add('page-length', r.pageScreens >= 4 && r.pageScreens <= 16, `${r.pageScreens} screens (promise: 4–16)`, 2); add('sections', r.sections >= 5 && r.sections <= 12 && r.emptySections.length === 0 && r.duplicateSections.length === 0, r.emptySections.length ? `empty sections: ${r.emptySections.join(', ')}` : r.duplicateSections.length ? `duplicate sections: ${r.duplicateSections.join(', ')}` : r.sections < 5 || r.sections > 12 ? `${r.sections} sections (promise: 5–12)` : r.duplicateSections.length ? `duplicate sections: ${r.duplicateSections.slice(0, 4).join(', ')}` : `${r.sections} sections`); }
  add(`${name}-sticky-frames`, r.sticky.every(s => s.frames >= 2 && s.frames === s.rows && s.frameW >= 300), JSON.stringify(r.sticky) || 'none', 2);
  add(`${name}-pinned-slides`, r.pinned.every(s => s.slides >= 2 && s.slides <= 5), JSON.stringify(r.pinned) || 'none');
  add(`${name}-contrast`, r.lowContrast.length === 0, r.lowContrast.join(' / ') || 'ok', 3);
  await ctx.close();
}
await browser.close();
// ---- SEO-safe promises: measured on the HTML itself (no viewport), only when the brief asked for this mode ----
let seo = null;
try {
  const J = f => { try { return JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')); } catch { return null; } };
  const brief = J('brief.json') || {}, inv = J('inventory.json') || {};
  const safe = !['free', 'studio', 'creative'].includes(String(brief.mode || '').toLowerCase());
  if (safe && inv && inv.copy) {
    const html = fs.readFileSync(file, 'utf8'); const text = html.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/g, ' ').replace(/<[^>]+>/g, ' ').toLowerCase();
    const STOP = new Set('a an and are as at be by for from has have in is it its of on or that the this to was were will with your you our we us y o u e el la los las un una de del al en con por para que es son como su sus se lo le más mas sin sobre entre i na za od do sa je su da ne ili ali kao što to te ta ova ovaj ove ovo und der die das ein eine mit von zu für auf im ist sind et le les des du une au aux dans pour par sur est sont'.split(' '));
    const words = t => (String(t || '').toLowerCase().match(/\p{L}{3,}/gu) || []).filter(w => !STOP.has(w));  // \p{L}: JS \w is ASCII-only, and the sites are not
    const pageWords = new Set(words(text));
    // 1. words: every content word of the source's sections is on the page (archive included)
    const src = new Set(words((inv.sourceCoverage?.sections || []).map(x => (x.title || '') + ' ' + (x.text || '')).join(' ') + ' ' + (inv.copy.text || '').slice(0, 40000)));
    // A word that stood only on the source's links and buttons ("cart", "close", "navigation") is graded with the links, below, not as text.
    const count = list => list.reduce((m, w) => m.set(w, (m.get(w) || 0) + 1), new Map());
    const inText = count(words((inv.copy.text || '').slice(0, 40000))), onControls = count(words((inv.actions || []).map(a => a.text || '').join(' ')));
    for (const w of [...src]) if (onControls.has(w) && (inText.get(w) || 0) <= onControls.get(w)) src.delete(w);
    const lostWords = [...src].filter(w => !pageWords.has(w)); const kept = src.size - lostWords.length; const textShare = src.size ? kept / src.size : 1;
    // 2. h1 keywords
    const h1 = inv.copy.h1 || ''; const h1kw = [...new Set(words(h1))].slice(0, 8); const h1new = (html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i) || [, ''])[1].replace(/<[^>]+>/g, ' ').toLowerCase();
    const h1kept = h1kw.filter(k => h1new.includes(k) || (k.length >= 6 && h1new.includes(k.slice(0, 5)))); const h1Share = h1kw.length ? h1kept.length / h1kw.length : 1;
    // 3. internal links
    let host = ''; try { host = new URL(inv.url).hostname.replace(/^www\./, ''); } catch {}
    // hrefs are written entity-escaped in HTML (a query string's & is &amp;): compare them decoded
    const decode = h => h.replace(/&amp;/g, '&').replace(/&#x26;|&#38;/gi, '&').replace(/&quot;/g, '"').replace(/&#39;|&#x27;/gi, "'");
    // A place on a page (…/post/#respond) is not another page: both sides are compared without it.
    const bare = h => h.replace(/#.*$/, '').replace(/\/$/, '');
    const hrefs = new Set([...html.matchAll(/href="([^"]+)"/g)].map(m => bare(decode(m[1]))));
    // an anchor on the source page itself (https://site/#faq, a skip link) is not a page of the site: a rebuilt page has its own anchors.
    // The renderer's own list (lib/seo.py internal_links) leaves these out; the promise is graded on the same definition.
    const samePageAnchor = href => { try { const u = new URL(href), p = new URL(inv.url); return (!!u.hash || /#$/.test(href)) && u.hostname.replace(/^www\./, '') === p.hostname.replace(/^www\./, '') && u.pathname.replace(/\/$/, '') === p.pathname.replace(/\/$/, '') && u.search === p.search; } catch { return false; } };
    // The controls of a shop (cart, checkout, the customer's account) are not pages: lib/seo.py utility_link leaves them out of the page, and the promise is graded on the same list.
    const UTILITY = new Set(['cart', 'basket', 'checkout', 'wishlist', 'my-account', 'cesta', 'carrito', 'carro', 'mi-cuenta', 'warenkorb', 'kasse', 'mein-konto', 'panier', 'mon-compte', 'carrello', 'il-mio-account', 'winkelwagen', 'kosarica', 'korpa', 'moj-nalog', 'moj-racun']);
    const utilityLink = href => { try { const u = new URL(href); const segments = u.pathname.split('/').filter(Boolean).map(x => x.toLowerCase()); return (segments.length > 0 && UTILITY.has(segments[segments.length - 1])) || u.search.toLowerCase().includes('add-to-cart='); } catch { return false; } };
    const links = [...new Map((inv.actions || []).filter(a => /^https?:/.test(a.href || '') && !['form', 'demo'].includes(a.region) && !samePageAnchor(a.href) && !utilityLink(a.href)).filter(a => { try { const u = new URL(a.href); return !u.username && u.hostname.includes('.') && u.hostname.replace(/^www\./, '') === host; } catch { return false; } }).map(a => [bare(a.href), a])).keys()];
    const linksKept = links.filter(h => hrefs.has(h)).length;
    // 4. meta
    const s = inv.seo || {}; const meta = { title: !!html.match(/<title>[^<]+<\/title>/), description: !s.description || html.includes('name="description"'), canonical: !s.canonical || html.includes('rel="canonical"'), jsonld: !(s.structuredData?.raw || []).length || html.includes('application/ld+json') };
    // On a source of a hundred words every word is most of a point: a handful lost is named, not failed.
    add('seo-text-kept', textShare >= .95 || lostWords.length <= 6, `${Math.round(textShare * 100)}% of the source's words are on the page` + (lostWords.length ? ` · lost: ${lostWords.slice(0, 12).join(', ')}` : ''), 3);
    add('seo-h1-keywords', h1Share >= .5, h1kw.length ? `h1 keeps ${h1kept.length}/${h1kw.length} keywords of "${h1.slice(0, 60)}"` : 'source has no h1', 3);
    add('seo-links-kept', linksKept === links.length, `${linksKept}/${links.length} internal links kept`, 2);
    add('seo-meta', Object.values(meta).every(Boolean), Object.entries(meta).filter(([, v]) => !v).map(([k]) => k + ' missing').join(', ') || 'title, description, canonical, structured data carried over', 2);
    seo = { mode: 'seo-safe', text_kept: +textShare.toFixed(3), words_lost: lostWords.slice(0, 40), h1_keywords: { source: h1kw, kept: h1kept }, links: { total: links.length, kept: linksKept, lost: links.filter(h => !hrefs.has(h)).slice(0, 20) }, meta };
  } else if (inv && inv.copy) seo = { mode: 'free' };
} catch (e) { console.warn('seo check', e.message); }
const total = items.reduce((p, i) => p + i.weight, 0); const got = items.filter(i => i.ok).reduce((p, i) => p + i.weight, 0);
const rep = { score: Math.round(100 * got / total), passed: items.filter(i => i.ok).length, failed: items.filter(i => !i.ok).map(i => ({ id: i.id, detail: i.detail, weight: i.weight })), items, seo };
fs.writeFileSync(path.join(dir, 'contract.json'), JSON.stringify(rep, null, 1)); console.log(JSON.stringify({ score: rep.score, passed: rep.passed, failed: rep.failed.map(f => f.id + ': ' + f.detail) }));
