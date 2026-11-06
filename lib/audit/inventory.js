/* AUDIT · inventory.js — runs in the client's page (via browser automation or a bookmarklet).
   Produces a JSON inventory of what the site HAS. No judgement here; diagnosis is a separate step. */
(() => {
  const q = s => [...document.querySelectorAll(s)];
  const cs = e => getComputedStyle(e);
  const fam = e => cs(e).fontFamily.split(',')[0].replace(/["']/g, '').trim();
  const txt = e => (e.innerText || '').replace(/\s+/g, ' ').trim();
  const words = s => s.split(/\s+/).filter(Boolean).length;
  const hex = s => { const m = (s || '').match(/\d+/g); if (!m) return s; return '#' + m.slice(0, 3).map(n => (+n).toString(16).padStart(2, '0')).join('') + (m[3] && m[3] !== '1' ? ' a' + m[3] : ''); };
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && cs(e).visibility !== 'hidden'; };

  // ---- sections (top-level beats) ----
  const root = document.querySelector('main') || document.body;
  let blocks = q('section, main > div, main > article, body > div > section, header, footer').filter(vis);
  if (blocks.length < 3) blocks = [...root.children].filter(vis);
  const sections = blocks.filter(b => b.getBoundingClientRect().height > 120).map((b, i) => {
    const h = b.querySelector('h1,h2,h3');
    const ctas = q('a,button').filter(x => b.contains(x) && vis(x)).map(x => txt(x)).filter(t => t && t.length < 40);
    const nums = (txt(b).match(/(?:[$€£¥]\s?)?\d[\d,.]*\s?(?:%|[kKmMbB]\b|\+|u\b)?/g) || []).filter(n => n.length > 1).slice(0, 12);
    return { i: i + 1, tag: b.tagName.toLowerCase(), id: b.id || null, h: Math.round(b.getBoundingClientRect().height), heading: h ? txt(h).slice(0, 90) : null, headingLevel: h ? h.tagName : null, words: words(txt(b)), ctas: [...new Set(ctas)].slice(0, 6), numbers: [...new Set(nums)], images: b.querySelectorAll('img,video,canvas,picture').length, svg: b.querySelectorAll('svg').length, bg: hex(cs(b).backgroundColor) };
  });

  // ---- typography ----
  const typo = {};
  q('h1,h2,h3,h4,p,a,button,li,span,small,label').filter(vis).slice(0, 800).forEach(e => {
    if (!txt(e) || e.children.length > 2) return; const c = cs(e);
    const k = `${e.tagName}|${fam(e)}|${c.fontWeight}|${Math.round(parseFloat(c.fontSize))}|${(parseFloat(c.lineHeight) / parseFloat(c.fontSize) || 0).toFixed(2)}|${c.letterSpacing}|${c.textTransform}`;
    typo[k] = (typo[k] || 0) + 1;
  });
  const typoTop = Object.entries(typo).sort((a, b) => b[1] - a[1]).slice(0, 25).map(([k, n]) => { const [tag, f, w, s, lh, ls, tt] = k.split('|'); return { tag, font: f, weight: +w, size: +s, lh: +lh, ls, tt, n }; });
  const h1 = document.querySelector('h1');
  const h1s = h1 ? cs(h1) : null;

  // ---- colours ----
  const bg = {}, fg = {}, accent = {};
  q('*').filter(vis).slice(0, 4000).forEach(e => {
    const c = cs(e); const b = c.backgroundColor; const r = e.getBoundingClientRect();
    if (b && !/, 0\)$/.test(b) && r.width * r.height > 4000) bg[hex(b)] = (bg[hex(b)] || 0) + Math.round(r.width * r.height / 10000);
    if (e.children.length === 0 && txt(e)) fg[hex(c.color)] = (fg[hex(c.color)] || 0) + 1;
    if (/^(A|BUTTON)$/.test(e.tagName) && b && !/, 0\)$/.test(b)) accent[hex(b)] = (accent[hex(b)] || 0) + 1;
  });
  const top = (o, n) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n).map(([k, v]) => ({ c: k, n: v }));

  // ---- nav / header / footer ----
  const nav = q('nav a, header a').filter(vis).map(txt).filter(t => t && t.length < 25);
  const footer = document.querySelector('footer');
  const logo = q('header img, nav img, a[href="/"] img, [class*="logo"] img').filter(vis)[0];
  const logoSvg = q('header svg, nav svg, a[href="/"] svg, [class*="logo"] svg').filter(vis)[0];

  // ---- media ----
  const imgs = q('img').filter(vis).map(e => ({ src: (e.currentSrc || e.src || '').split('?')[0].slice(-80), w: Math.round(e.getBoundingClientRect().width), h: Math.round(e.getBoundingClientRect().height), alt: (e.alt || '').slice(0, 60) })).filter(x => x.w > 40);
  const bigImgs = imgs.filter(x => x.w >= 400);

  // ---- motion / tech ----
  const all = q('*');
  const libs = { gsap: !!window.gsap, ScrollTrigger: !!window.ScrollTrigger, lenis: !!(window.Lenis || q('.lenis').length), framer: !!window.__framer_importFromPackage || !!q('[data-framer-name]').length, webflow: !!document.documentElement.getAttribute('data-wf-site'), next: !!q('#__next').length, nuxt: !!q('#__nuxt').length, react: !!q('[data-reactroot],#root').length, tailwind: !!q('[class*="flex "],[class*="grid-cols"]').length, three: !!q('canvas').length };
  const anim = { transitions: all.filter(e => cs(e).transitionDuration !== '0s').length, animations: all.filter(e => cs(e).animationName !== 'none').length, sticky: all.filter(e => cs(e).position === 'sticky').length, fixed: all.filter(e => cs(e).position === 'fixed').length };

  // ---- copy ----
  const bodyText = txt(document.body);
  const headings = q('h1,h2,h3').filter(vis).map(h => ({ tag: h.tagName, text: txt(h).slice(0, 100), words: words(txt(h)) }));
  const buttons = [...new Set(q('a,button').filter(vis).map(txt).filter(t => t && t.length < 40 && /[a-z]/i.test(t)))];

  return {
    url: location.href, title: document.title, lang: document.documentElement.lang || null,
    viewport: { w: innerWidth, h: innerHeight }, pageHeight: document.documentElement.scrollHeight,
    sections, sectionCount: sections.length,
    copy: { totalWords: words(bodyText), headings, headingCount: headings.length, h1: h1 ? txt(h1) : null, h1Words: h1 ? words(txt(h1)) : 0, buttons: buttons.slice(0, 30), text: bodyText.slice(0, 12000) },
    typography: { fonts: [...new Set(typoTop.map(t => t.font))], h1: h1s ? { font: fam(h1), size: Math.round(parseFloat(h1s.fontSize)), weight: h1s.fontWeight, lh: (parseFloat(h1s.lineHeight) / parseFloat(h1s.fontSize)).toFixed(2), ls: h1s.letterSpacing, tt: h1s.textTransform } : null, samples: typoTop },
    colors: { bg: top(bg, 8), text: top(fg, 6), buttons: top(accent, 6) },
    brand: { logo: logo ? (logo.currentSrc || logo.src) : null, logoSvg: logoSvg ? logoSvg.outerHTML.slice(0, 2000) : null, nav, navCount: nav.length, hasFooter: !!footer, footerWords: footer ? words(txt(footer)) : 0, footerLinks: footer ? footer.querySelectorAll('a').length : 0 },
    media: { imgCount: imgs.length, bigImgs: bigImgs.slice(0, 20), video: q('video').length, svg: q('svg').length, canvas: q('canvas').length },
    tech: { libs: Object.entries(libs).filter(x => x[1]).map(x => x[0]), anim }
  };
})();
