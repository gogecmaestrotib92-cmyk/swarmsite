/* extract.js — blueprint extractor. Runs inside a live site (via Chrome) and measures what a studio would measure:
   sections (rects, bg, padding, columns), type scale (family/size/weight/tracking/leading per role), spacing rhythm,
   images (fit/radius/filter/aspect), buttons, nav, motion libs + transform/opacity deltas across scroll positions.
   Output: compact JSON written into <article id="bpout"><pre> so it can be read as page text. No '?' in output keys. */
window.__bp = (async () => {
  const q = s => [...document.querySelectorAll(s)];
  const cs = e => getComputedStyle(e);
  const R = e => { const r = e.getBoundingClientRect(); return { x: Math.round(r.left), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height) }; };
  const vis = e => { const r = e.getBoundingClientRect(); const c = cs(e); return r.width > 4 && r.height > 4 && c.visibility !== 'hidden' && c.display !== 'none'; };
  const hex = c => { const m = (c || '').match(/\d+(\.\d+)?/g); if (!m || m.length < 3) return null; if (m[3] !== undefined && +m[3] === 0) return null; return '#' + [0, 1, 2].map(i => (+m[i]).toString(16).padStart(2, '0')).join(''); };
  const txt = e => (e.innerText || '').trim().replace(/\s+/g, ' ');
  const fam = f => (f || '').split(',')[0].replace(/["']/g, '').trim();
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const W = innerWidth, H = innerHeight;

  // 1) wake lazy content + record transform/opacity at 4 scroll positions for motion detection
  const total = document.documentElement.scrollHeight; const samples = {};
  const track = q('h1,h2,h3,p,img,video,section > div,[class*="card" i],[class*="item" i],button,a').filter(vis).slice(0, 400);
  const snap = (label) => track.forEach((e, i) => { const c = cs(e); (samples[i] = samples[i] || { tag: e.tagName, n: 0 })[label] = { t: c.transform, o: c.opacity, f: c.filter, cp: c.clipPath }; });
  snap('top');
  for (let y = 0; y < total; y += H * .5) { scrollTo(0, y); await sleep(140); }
  snap('end'); scrollTo(0, Math.min(total * .4, 3000)); await sleep(500); snap('mid'); scrollTo(0, 0); await sleep(400);
  const motion = { libs: { gsap: !!window.gsap, scrollTrigger: !!(window.ScrollTrigger || (window.gsap && gsap.plugins && gsap.plugins.scrollTrigger)), lenis: !!(window.Lenis || window.lenis || document.documentElement.classList.contains('lenis')), three: !!window.THREE, webgl: q('canvas').some(c => c.width > 200), locomotive: !!document.querySelector('[data-scroll-container]'), framer: !!document.querySelector('[data-framer-name]'), webflow: !!document.querySelector('[data-wf-page]') },
    customCursor: !!q('[class*="cursor" i]').find(e => cs(e).position === 'fixed' && e.getBoundingClientRect().width < 120),
    animated: Object.values(samples).filter(s => s.top && s.end && (s.top.t !== s.end.t || s.top.o !== s.end.o || s.top.f !== s.end.f || s.top.cp !== s.end.cp)).length, tracked: track.length,
    transitions: [...new Set(q('*').filter(vis).map(e => cs(e).transitionProperty + '|' + cs(e).transitionDuration + '|' + cs(e).transitionTimingFunction).filter(t => !t.startsWith('all|0s') && !t.startsWith('none')))].slice(0, 12),
    keyframes: [...document.styleSheets].flatMap(s => { try { return [...s.cssRules]; } catch { return []; } }).filter(r => r.type === 7).map(r => r.name).slice(0, 20) };

  // 2) sections = big blocks in document order
  const cands = q('main > *, body > *, main > * > *, body > * > *, section, header, footer').filter(vis).filter(e => { const r = e.getBoundingClientRect(); return r.height > 180 && r.width > W * .5; });
  const secs = []; cands.sort((a, b) => R(a).y - R(b).y);
  for (const e of cands) { const r = R(e); if (secs.some(s => Math.abs(s.rect.y - r.y) < 40 && Math.abs(s.rect.h - r.h) < 80)) continue; if (secs.some(s => s.el.contains(e) && R(s.el).h < r.h * 1.6)) continue; secs.push({ el: e, rect: r }); }
  const sections = secs.slice(0, 16).map((s, i) => {
    const e = s.el, c = cs(e), r = s.rect;
    const kids = [...e.children].filter(vis).map(R).filter(k => k.w > 40 && k.h > 20);
    // columns: distinct left edges among direct/2nd-level children
    const lefts = [...new Set([...e.querySelectorAll(':scope > *, :scope > * > *')].filter(vis).map(k => Math.round(k.getBoundingClientRect().left / 20) * 20))].sort((a, b) => a - b);
    const heads = [...e.querySelectorAll('h1,h2,h3')].filter(vis).slice(0, 3).map(h => { const hc = cs(h); return { tag: h.tagName, text: txt(h).slice(0, 80), px: Math.round(parseFloat(hc.fontSize)), fam: fam(hc.fontFamily), w: hc.fontWeight, ls: hc.letterSpacing, lh: (parseFloat(hc.lineHeight) / parseFloat(hc.fontSize)).toFixed(2), tt: hc.textTransform, it: hc.fontStyle, al: hc.textAlign, rect: R(h) } });
    const paras = [...e.querySelectorAll('p')].filter(vis).slice(0, 2).map(p => { const pc = cs(p); return { px: Math.round(parseFloat(pc.fontSize)), fam: fam(pc.fontFamily), lh: (parseFloat(pc.lineHeight) / parseFloat(pc.fontSize)).toFixed(2), maxw: Math.round(p.getBoundingClientRect().width), words: txt(p).split(' ').length } });
    const imgs = [...e.querySelectorAll('img,video,canvas')].filter(vis).slice(0, 4).map(im => { const ic = cs(im); const ir = R(im); return { tag: im.tagName, w: ir.w, h: ir.h, ar: +(ir.w / Math.max(1, ir.h)).toFixed(2), fit: ic.objectFit, br: ic.borderRadius, filter: ic.filter !== 'none' ? ic.filter : undefined, bleed: ir.w >= W - 8, x: ir.x } });
    const btns = [...e.querySelectorAll('a,button')].filter(vis).filter(b => { const bc = cs(b); return hex(bc.backgroundColor) || bc.borderStyle !== 'none' && parseFloat(bc.borderWidth) > 0; }).slice(0, 2).map(b => { const bc = cs(b); const br = R(b); return { text: txt(b).slice(0, 30), h: br.h, pad: bc.padding, br: bc.borderRadius, bg: hex(bc.backgroundColor), col: hex(bc.color), px: Math.round(parseFloat(bc.fontSize)), w: bc.fontWeight, tt: bc.textTransform, ls: bc.letterSpacing } });
    const labels = [...e.querySelectorAll('span,small,div,p')].filter(vis).filter(l => { const lc = cs(l); return parseFloat(lc.fontSize) <= 13 && (lc.textTransform === 'uppercase' || /mono/i.test(lc.fontFamily)) && txt(l).length > 1 && txt(l).length < 40 && l.children.length === 0; }).slice(0, 2).map(l => { const lc = cs(l); return { text: txt(l), px: Math.round(parseFloat(lc.fontSize)), fam: fam(lc.fontFamily), ls: lc.letterSpacing, tt: lc.textTransform, col: hex(lc.color) } });
    const bgImg = c.backgroundImage !== 'none';
    return { i: i + 1, tag: e.tagName.toLowerCase(), cls: (e.className && e.className.baseVal === undefined ? String(e.className) : '').split(' ').slice(0, 2).join(' '), rect: r, screens: +(r.h / H).toFixed(2), bg: hex(c.backgroundColor), bgImg, color: hex(c.color), padT: Math.round(parseFloat(c.paddingTop)), padB: Math.round(parseFloat(c.paddingBottom)), display: c.display, grid: c.gridTemplateColumns !== 'none' ? c.gridTemplateColumns.split(' ').length + ' cols' : undefined, cols: lefts.length, lefts: lefts.slice(0, 6), kids: kids.length, heads, paras, labels, imgs, btns, words: txt(e).split(' ').length, pos: c.position, sticky: !!e.querySelector('[style*="sticky"], .sticky') || c.position === 'sticky' };
  });

  // 3) page-level type scale + palette + nav
  const sizes = {}; q('h1,h2,h3,h4,p,a,span,li,button,div').filter(vis).filter(e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())).forEach(e => { const c = cs(e); const k = `${fam(c.fontFamily)}|${Math.round(parseFloat(c.fontSize))}|${c.fontWeight}`; sizes[k] = (sizes[k] || 0) + 1; });
  const scale = Object.entries(sizes).sort((a, b) => b[1] - a[1]).slice(0, 18).map(([k, n]) => ({ k, n }));
  const bgs = {}; q('*').filter(vis).forEach(e => { const b = hex(cs(e).backgroundColor); if (b) { const r = e.getBoundingClientRect(); bgs[b] = (bgs[b] || 0) + r.width * r.height; } });
  const palette = Object.entries(bgs).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([h, a]) => ({ h, share: +(a / (W * total)).toFixed(3) }));
  const nav = (() => { const n = document.querySelector('nav, header'); if (!n) return null; const c = cs(n); const links = [...n.querySelectorAll('a')].filter(vis); return { pos: c.position, h: Math.round(n.getBoundingClientRect().height), links: links.length, bg: hex(c.backgroundColor), blur: c.backdropFilter !== 'none' ? c.backdropFilter : undefined, mix: c.mixBlendMode !== 'normal' ? c.mixBlendMode : undefined, link: links[0] ? { px: Math.round(parseFloat(cs(links[0]).fontSize)), fam: fam(cs(links[0]).fontFamily), tt: cs(links[0]).textTransform, ls: cs(links[0]).letterSpacing } : null } })();
  const fonts = [...new Set(q('*').filter(vis).map(e => fam(cs(e).fontFamily)))].slice(0, 6);
  const out = { url: location.href, title: document.title.slice(0, 80), vw: W, vh: H, pageH: total, screens: +(total / H).toFixed(1), fonts, scale, palette, nav, motion, sections, maxw: (() => { const m = {}; q('main > *, section > *, section > * > *').filter(vis).forEach(e => { const w = Math.round(e.getBoundingClientRect().width / 10) * 10; if (w > W * .5 && w < W - 20) m[w] = (m[w] || 0) + 1; }); return Object.entries(m).sort((a, b) => b[1] - a[1]).slice(0, 3).map(x => +x[0]); })() };
  let json = JSON.stringify(out); json = json.replace(/\?/g, '%3F');
  let a = document.getElementById('bpout'); if (!a) { a = document.createElement('article'); a.id = 'bpout'; a.style.cssText = 'display:block;position:relative;width:100%;font-size:6px;line-height:1;color:#000;background:#fff;z-index:99999;word-break:break-all'; (document.querySelector('main') || document.body).prepend(a); }
  a.innerHTML = '<pre>BPSTART' + json + 'BPEND</pre>'; return 'ok ' + json.length;
})()
