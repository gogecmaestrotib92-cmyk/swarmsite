/* product.mjs — the client's own product, photographed: for a software or app site, the pages behind its top bar
   (the matches, the picks, the editor, the dashboard) are its product screens. Each page the bar links to is opened at
   desk width (1440 × 900, drawn at 1.25) and at phone width (390 × 808, drawn at 2), cookie notices and chat bubbles
   put away, and its first screen is kept when it looks like a working product rather than a page of prose.

   productShots(browser, { home, links, deadline }) → { screens: [...], phones: [...], pages: [...] }
     links     [{url, label}] — the top bar's links of the home page, in the bar's order (geometry.json links)
     screens / phones  [{id, url, page, label, w, h, alt, score, data}]   data = JPEG data URI; alt = the page's own h1
                       or the bar's label for it — never words of ours
     pages     what was opened and why each was kept or not (for the record)

   What makes a page "product": per 1000 px² of its first screen, the controls, data cells, numbers and drawn charts
   it shows, against the words it sets in long paragraphs. A page that redirects to a sign-in, is mostly prose or is
   the home page again is not kept. Nothing here decides the kind of business: the adapter uses these only for a
   product (not a place, a clinic, a firm …). Bounded in time: every page gets a slice of `deadline`. */

const SKIP = /(?:^|\/)(?:log[-_]?in|sign[-_]?(?:in|up)|register|logout|checkout|cart|account|admin|privacy|terms|legal|cookies?|blog|news|press|careers?|jobs|contact|about|faq|help|support|docs?|download|affiliates?|partners?)(?:[\/._-]|$)|\.(?:pdf|zip|jpe?g|png|webp|gif|svg|mp4|xml|json)$/i;

// what is on the first screen: controls, data, numbers, drawings — and prose
const MEASURE = () => {
  const W = innerWidth, H = innerHeight, on = r => r.width > 4 && r.height > 4 && r.bottom > 0 && r.top < H && r.right > 0 && r.left < W;
  const vis = e => { const c = getComputedStyle(e); return c.visibility !== 'hidden' && c.display !== 'none' && +c.opacity > .2; };
  let ui = 0, cells = 0, nums = 0, art = 0, prose = 0, words = 0;
  for (const e of document.querySelectorAll('button, input, select, textarea, [role="tab"], [role="switch"], [role="slider"], [role="button"]')) { const r = e.getBoundingClientRect(); if (on(r) && vis(e)) ui++; }
  for (const e of document.querySelectorAll('td, th, [role="cell"], [role="gridcell"], li')) { const r = e.getBoundingClientRect(); if (on(r) && vis(e) && r.width < W * .6) cells++; }
  for (const e of document.querySelectorAll('canvas, svg, img, video')) { const r = e.getBoundingClientRect(); if (on(r) && vis(e) && r.width >= 40 && r.height >= 30) art++; }
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let t;
  while ((t = tw.nextNode())) { const s = t.nodeValue.trim(); if (!s) continue; const el = t.parentElement; if (!el || /^(SCRIPT|STYLE|NOSCRIPT)$/.test(el.tagName)) continue;
    const r = el.getBoundingClientRect(); if (!on(r) || !vis(el)) continue; const n = s.split(/\s+/).length; words += n;
    nums += (s.match(/(?:^|[\s(])[+−-]?[$€£]?\d[\d.,:]*%?(?=$|[\s)])/g) || []).length;
    if (n >= 22 && /^(P|LI|BLOCKQUOTE|DD)$/.test(el.tagName)) prose += n; }
  const h1 = document.querySelector('h1'); const title = (h1 && vis(h1) ? h1.innerText : '').replace(/\s+/g, ' ').trim().slice(0, 90);
  return { ui, cells, nums, art, prose, words, title, path: location.pathname, height: document.documentElement.scrollHeight };
};
const score = m => m.words < 15 ? -1 : +(m.ui * 1 + m.cells * .5 + m.nums * .6 + m.art * .8 - m.prose / 12).toFixed(1);

// cookie notices, consent walls and chat bubbles: refused where a button says so, else put out of the picture
const CLEAR = () => {
  const say = e => ((e.innerText || '') + ' ' + (e.id || '') + ' ' + (typeof e.className === 'string' ? e.className : '')).toLowerCase();
  for (const b of document.querySelectorAll('button, a[role="button"], [role="button"]')) { const s = (b.innerText || '').trim(); if (s.length < 40 && /^(reject|decline|refuse|only necessary|necessary only|reject all|decline all|use necessary)/i.test(s)) { try { b.click(); } catch {} } }
  for (const e of document.querySelectorAll('body *')) { const c = getComputedStyle(e); if (c.position !== 'fixed' && c.position !== 'sticky') continue; const r = e.getBoundingClientRect();
    if (/cookie|consent|gdpr|privacy|onetrust|cookiebot|didomi|usercentrics/.test(say(e)) && r.height < innerHeight * .9 && !(r.top < 5 && r.height < 120 && e.querySelector('nav, a[href="/"]'))) e.style.setProperty('display', 'none', 'important');
    if ((e.tagName === 'IFRAME' || /intercom|crisp|drift|hubspot|tawk|chat-widget|zendesk|launcher/.test(say(e))) && r.width < 480 && r.top > innerHeight * .4) e.style.setProperty('display', 'none', 'important'); }
};

async function shoot(browser, url, vp, deadline) {
  const ctx = await browser.newContext({ viewport: { width: vp.w, height: vp.h }, deviceScaleFactor: vp.dpr, isMobile: !!vp.mobile, hasTouch: !!vp.mobile,
    userAgent: vp.mobile ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' : undefined });
  try {
    const page = await ctx.newPage(); const left = () => Math.max(800, deadline - Date.now());
    const res = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: Math.min(12000, left()) });
    if (!res || !res.ok()) return { why: 'HTTP ' + (res ? res.status() : 'none') };
    await page.waitForLoadState('networkidle', { timeout: Math.min(5000, left()) }).catch(() => {});
    for (let i = 0; i < 12; i++) { const n = await page.evaluate(() => document.body.innerText.split(/\s+/).filter(Boolean).length).catch(() => 0); if (n >= 25) break; await page.waitForTimeout(400); }
    await page.evaluate(async () => { for (let y = 0; y < Math.min(document.body.scrollHeight, 3000); y += 600) { scrollTo(0, y); await new Promise(r => setTimeout(r, 80)); } scrollTo(0, 0); }).catch(() => {});
    await page.evaluate(CLEAR).catch(() => {}); await page.waitForTimeout(900); await page.evaluate(CLEAR).catch(() => {});
    const m = await page.evaluate(MEASURE);
    m.final = page.url();
    const buf = await page.screenshot({ type: 'jpeg', quality: 80 });
    return { m, data: 'data:image/jpeg;base64,' + buf.toString('base64'), w: Math.round(vp.w * vp.dpr), h: Math.round(vp.h * vp.dpr) };
  } catch (e) { return { why: String(e.message || e).slice(0, 90) }; } finally { await ctx.close().catch(() => {}); }
}

export async function productShots(browser, { home, links = [], deadline = Date.now() + 60000, max = 4 } = {}) {
  const out = { screens: [], phones: [], pages: [] };
  let origin; try { origin = new URL(home).origin; } catch { return out; }
  const homePath = new URL(home).pathname.replace(/\/+$/, '');
  const seen = new Set([homePath]), cands = [];
  for (const l of links) { let u; try { u = new URL(l.url, home); } catch { continue; } const p = u.pathname.replace(/\/+$/, '');
    if (u.origin.replace('://www.', '://') !== origin.replace('://www.', '://') || seen.has(p) || !p || SKIP.test(p) || u.hash && !p) continue; seen.add(p); cands.push({ url: u.origin + u.pathname, label: String(l.label || '').replace(/\s+/g, ' ').trim().slice(0, 60) }); }
  const kept = [];
  for (const c of cands.slice(0, 8)) {
    if (Date.now() > deadline - 4000 || kept.length >= max) break;
    const d = await shoot(browser, c.url, { w: 1440, h: 900, dpr: 1.25 }, deadline);
    if (!d.m) { out.pages.push({ url: c.url, kept: false, why: d.why }); continue; }
    const fp = new URL(d.m.final).pathname.replace(/\/+$/, '');
    const s = score(d.m), redirected = SKIP.test(fp) || fp === homePath;
    const ok = !redirected && s >= 12 && d.m.prose < d.m.words * .5;
    out.pages.push({ url: c.url, kept: ok, score: s, measured: { ui: d.m.ui, cells: d.m.cells, nums: d.m.nums, art: d.m.art, prose: d.m.prose, words: d.m.words }, ...(redirected ? { why: 'redirects to ' + fp } : {}) });
    if (!ok) continue;
    const alt = d.m.title || c.label;
    kept.push({ c, s, alt });
    out.screens.push({ id: 'screen' + kept.length, url: c.url, page: c.label, label: c.label, alt, score: s, w: d.w, h: d.h, data: d.data });
    if (Date.now() > deadline - 2500) break;                // the same page at phone width, at once: a desk screen and its phone stay a pair
    const p = await shoot(browser, c.url, { w: 390, h: 808, dpr: 2, mobile: true }, deadline);
    if (p.m && score(p.m) >= 4) out.phones.push({ id: 'phone' + (out.phones.length + 1), url: c.url, page: c.label, label: c.label, alt: p.m.title || alt, score: score(p.m), w: p.w, h: p.h, data: p.data });
  }
  return out;
}
