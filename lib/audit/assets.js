/* BRAND ASSETS — assets.js. Runs in the client's page (Playwright in production, browser automation in the demo).
   Finds and ranks the brand's logo, icon, colours and fonts, and returns them embedded (data URIs) so the
   renderer never depends on the client's hosting. Pure extraction — no judgement.

   Output: { logo:{src,data,type,w,h,kind,score,alternatives[]}, icon:{...}, wordmark:{text,font,weight,tt},
            palette:{fromLogo[], fromButtons[], fromBackgrounds[], brandAccent}, fonts:{faces[],display,body},
            social:{ogImage,title,description}, productShots:[{src,w,h,alt}] } */
(async () => {
  const q = s => [...document.querySelectorAll(s)];
  const cs = e => getComputedStyle(e);
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const abs = u => { try { return new URL(u, location.href).href; } catch { return null; } };
  const toData = async url => { try { const r = await fetch(url, { mode: 'cors' }); if (!r.ok) return null; const b = await r.blob(); if (b.size > 1_500_000) return null; return await new Promise(res => { const fr = new FileReader(); fr.onload = () => res({ data: fr.result, type: b.type, size: b.size }); fr.readAsDataURL(b); }); } catch { return null; } };
  const dims = data => new Promise(res => { const im = new Image(); im.onload = () => res({ w: im.naturalWidth, h: im.naturalHeight, img: im }); im.onerror = () => res({ w: 0, h: 0 }); im.src = data; });

  // ---- 1. logo candidates (ranked) ----
  const cands = [];
  const push = (src, kind, el, score) => { const u = abs(src); if (u && !cands.some(c => c.src === u)) cands.push({ src: u, kind, score, alt: el?.alt || el?.getAttribute?.('aria-label') || '', w: el ? Math.round(el.getBoundingClientRect().width) : 0 }); };
  q('header img, nav img, a[href="/"] img, [class*="logo" i] img, img[alt*="logo" i]').filter(vis).forEach(i => push(i.currentSrc || i.src, 'img', i, 10));
  q('header svg, nav svg, a[href="/"] svg, [class*="logo" i] svg').filter(vis).filter(s => s.getBoundingClientRect().width > 24).forEach(s => { const xml = new XMLSerializer().serializeToString(s); if (xml.length < 60000) cands.push({ src: 'inline-svg', kind: 'svg', score: 12, data: 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(xml))), type: 'image/svg+xml', w: Math.round(s.getBoundingClientRect().width), alt: s.getAttribute('aria-label') || '' }); });
  q('link[rel~="icon"], link[rel="apple-touch-icon"]').forEach(l => push(l.href, 'icon', null, /svg/.test(l.href) ? 7 : 5));
  const og = q('meta[property="og:image"]')[0]?.content; if (og) push(og, 'og', null, 2);
  // Next/Vercel image optimizer: unwrap to the original asset
  cands.forEach(c => { try { const u = new URL(c.src); if (u.pathname.includes('/_next/image') && u.searchParams.get('url')) c.src = abs(u.searchParams.get('url')); } catch {} });
  // fetch + measure; prefer vector, then larger, then header placement
  for (const c of cands) { if (!c.data) { const d = await toData(c.src); if (d) Object.assign(c, d); } if (c.data) { const m = await dims(c.data); c.nw = m.w; c.nh = m.h; c._img = m.img; } c.score += (c.type === 'image/svg+xml' ? 6 : 0) + Math.min(4, (c.nw || 0) / 100) + (c.kind === 'og' ? -6 : 0); }
  const ok = cands.filter(c => c.data).sort((a, b) => b.score - a.score);
  const logo = ok[0] || null; const icon = ok.find(c => c.kind === 'icon') || logo;

  // ---- 2. wordmark (if the "logo" is only a symbol, the brand name is typeset) ----
  const home = q('header a[href="/"], nav a[href="/"], a.logo, [class*="logo" i]').filter(vis)[0];
  const wmText = home ? (home.innerText || '').replace(/\s+/g, ' ').trim() : '';
  const wmEl = home ? ([...home.querySelectorAll('*')].find(e => e.children.length === 0 && e.textContent.trim()) || home) : null;
  const wordmark = wmText ? { text: wmText.slice(0, 40), font: cs(wmEl).fontFamily.split(',')[0].replace(/["']/g, ''), weight: cs(wmEl).fontWeight, tt: cs(wmEl).textTransform, size: Math.round(parseFloat(cs(wmEl).fontSize)) } : null;

  // ---- 3. colours from the logo pixels (dominant non-neutral hue) ----
  const hex = (r, g, b) => '#' + [r, g, b].map(n => n.toString(16).padStart(2, '0')).join('');
  const fromLogo = [];
  const src = logo?._img; if (src && src.naturalWidth) { try { const cv = document.createElement('canvas'); const S = 64; cv.width = S; cv.height = S; const ctx = cv.getContext('2d'); ctx.drawImage(src, 0, 0, S, S); const d = ctx.getImageData(0, 0, S, S).data; const bins = {}; for (let i = 0; i < d.length; i += 4) { const [r, g, b, a] = [d[i], d[i + 1], d[i + 2], d[i + 3]]; if (a < 128) continue; const mx = Math.max(r, g, b), mn = Math.min(r, g, b); const sat = mx ? (mx - mn) / mx : 0; if (sat < .25 || mx < 40) continue; const k = hex(r >> 4 << 4, g >> 4 << 4, b >> 4 << 4); bins[k] = (bins[k] || 0) + 1; } Object.entries(bins).sort((a, b) => b[1] - a[1]).slice(0, 4).forEach(([c, n]) => fromLogo.push({ c, n })); } catch {} }
  // colours from buttons/backgrounds (reuse inventory logic lightly)
  const tally = {}; q('a,button').filter(vis).forEach(e => { const b = cs(e).backgroundColor; const m = b.match(/\d+/g); if (!m || (m[3] !== undefined && +m[3] < .5)) return; const [r, g, b2] = m.map(Number); const mx = Math.max(r, g, b2), mn = Math.min(r, g, b2); if (mx && (mx - mn) / mx > .25) { const k = hex(r, g, b2); tally[k] = (tally[k] || 0) + 1; } });
  const fromButtons = Object.entries(tally).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([c, n]) => ({ c, n }));
  const brandAccent = (fromButtons[0] || fromLogo[0] || {}).c || null;

  // ---- 4. fonts actually loaded (names from @font-face, not just computed stacks) ----
  const faces = new Set(); try { for (const ss of document.styleSheets) { let rules; try { rules = ss.cssRules; } catch { continue; } for (const r of rules) if (r instanceof CSSFontFaceRule) faces.add(r.style.getPropertyValue('font-family').replace(/["']/g, '').trim()); } } catch {}
  const h1 = document.querySelector('h1'); const p = document.querySelector('p');
  const fonts = { faces: [...faces].filter(f => !/^__|fallback/i.test(f)), display: h1 ? cs(h1).fontFamily.split(',')[0].replace(/["']/g, '') : null, body: p ? cs(p).fontFamily.split(',')[0].replace(/["']/g, '') : null, isSystemBody: p ? /system-ui|-apple-system|segoe|arial|helvetica/i.test(cs(p).fontFamily) : null };

  // ---- 5. product shots / big imagery (not fetched here; URLs for the pipeline) ----
  const productShots = q('img, video').filter(vis).map(e => ({ src: abs(e.currentSrc || e.src || e.querySelector?.('source')?.src), w: Math.round(e.getBoundingClientRect().width), h: Math.round(e.getBoundingClientRect().height), alt: e.alt || '' })).filter(x => x.src && x.w >= 400).slice(0, 12);

  const social = { ogImage: og ? abs(og) : null, title: q('meta[property="og:title"]')[0]?.content || document.title, description: q('meta[name="description"]')[0]?.content || null, themeColor: q('meta[name="theme-color"]')[0]?.content || null };
  const strip = c => { const { _img, ...rest } = c; return rest; };
  return { logo: logo ? { ...strip(logo), alternatives: ok.slice(1, 4).map(c => ({ src: c.src, kind: c.kind, type: c.type, nw: c.nw, nh: c.nh })) } : null, icon: icon ? strip(icon) : null, wordmark, palette: { fromLogo, fromButtons, brandAccent, themeColor: social.themeColor }, fonts, social, productShots };
})();
