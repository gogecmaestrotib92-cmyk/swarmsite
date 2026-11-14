// blocks.js — run in the page (capture.mjs): the page as the browser lays it out, as a numbered list of blocks in
// reading order. The flat text of a page loses where one element ends and the next begins, and everything read from
// it afterwards is a guess (a passage cut at the client's own name, a list of labels refused, a button's word set
// before a sentence — 2026-11-13). Here nothing is guessed: a block is what the browser already knows it to be.
//
//   {i, kind, text, …}
//     kind   'h'      a heading (level 1–6: the element's own, or aria-level)
//            'p'      a run of text that is one block of the layout (inline links and emphasis are part of it)
//            'li'     an item of a list (list: the number of the list it belongs to)
//            'quote'  text inside a blockquote
//            'a'      a block that is nothing but one link or button (href where it has one)
//            'cap'    a figure's caption, a table cell, a label, a summary
//            'img'    a picture shown on the page (src, alt; text is its alt)
//     region 'main' | 'header' | 'nav' | 'footer' | 'aside' | 'form' | 'consent'  — by the page's own landmarks
//     x, y, w, h   where it stands on the page (px, page coordinates); px, bold: the size and weight it is set in
//     folded true  for the answer of a closed <details> (on the page, not showing)
//     dim    true  for words the page holds faded to nothing or marked aria-hidden (a reveal waiting for the scroll, a closed menu, a ticker's copy)
//     same   the number of an earlier block with the same kind and words (a carousel's copy, a repeated bar)
//
//   covers  the share of the page's visible words that stand in some block — the check that the list loses nothing.
// Only what the page prints, as it prints it; nothing is rewritten. At most 1,500 blocks.
(() => {
  const MAX = 1500, out = [], norm = s => String(s || '').replace(/\s+/g, ' ').trim();
  const shown = e => { for (let n = e; n && n.nodeType === 1; n = n.parentElement) { const c = getComputedStyle(n); if (c.display === 'none' || c.visibility === 'hidden') return false; } return true; };
  // on the page but not showing as it stands now: faded to nothing (a reveal that waits for the scroll, a closed menu) or marked as not to be read out
  const dim = e => { for (let n = e; n && n.nodeType === 1; n = n.parentElement) { if (+getComputedStyle(n).opacity === 0 || n.getAttribute('aria-hidden') === 'true') return true; } return false; };
  // only what runs in the line is part of the block around it; a box set in the line (inline-block, inline-flex: a button, a chip) is a block of its own
  const inline = e => /^(inline|contents|ruby)$/.test(getComputedStyle(e).display) && !/^(LI|TD|TH|DT|DD|SUMMARY|FIGCAPTION|BUTTON)$/.test(e.tagName);
  const holder = n => { let e = n.parentElement; while (e && e !== document.body && inline(e)) e = e.parentElement; return e || document.body; };
  // a <header> is the site's bar only where it is one: at the top of the page and no taller than a bar (a hero or a section's heading set in <header> is the page's own)
  const bar = l => { const r = l.getBoundingClientRect(); return r.top + scrollY < 300 && r.height <= 320; };
  const region = e => { if (e.closest('[id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],[id*="gdpr" i],[class*="gdpr" i],[aria-label*="cookie" i]')) return 'consent';
    const l = e.closest('nav,[role="navigation"],header,[role="banner"],footer,[role="contentinfo"],aside,[role="complementary"],form,main,[role="main"]'); if (!l) return 'main';
    const t = l.tagName, r = l.getAttribute('role') || '';
    return t === 'NAV' || r === 'navigation' ? 'nav' : t === 'HEADER' || r === 'banner' ? ((l.closest('main,article,section') && l.parentElement !== document.body) || !bar(l) ? 'main' : 'header') : t === 'FOOTER' || r === 'contentinfo' ? (l.closest('main,article') ? 'main' : 'footer') : t === 'ASIDE' || r === 'complementary' ? 'aside' : t === 'FORM' ? 'form' : 'main'; };
  const lists = new Map();
  const kindOf = e => { const h = e.closest('h1,h2,h3,h4,h5,h6,[role="heading"]');
    if (h) return { kind: 'h', level: /^H\d$/.test(h.tagName) ? +h.tagName[1] : Math.min(6, Math.max(1, +h.getAttribute('aria-level') || 2)) };
    if (e.closest('blockquote,q')) return { kind: 'quote' };
    const li = e.closest('li,dt,dd'); if (li) { const l = li.closest('ul,ol,dl'); if (l && !lists.has(l)) lists.set(l, lists.size + 1); return { kind: 'li', ...(l ? { list: lists.get(l) } : {}) }; }
    if (e.closest('figcaption,td,th,label,summary,caption')) return { kind: 'cap' };
    return { kind: 'p' }; };
  // every visible text node, gathered under the element that holds it as one block of the layout
  const held = new Map(), order = [];
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let t;
  while ((t = tw.nextNode())) { if (!t.nodeValue.trim()) { const g = held.get(holder(t)); if (g && t.nodeValue) g.parts.push(' '); continue; }   // white space between two words set in separate elements is the space between them
    const p = t.parentElement; if (!p || /^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|TITLE|OPTION|TEXTAREA)$/.test(p.tagName) || p.closest('svg')) continue;
    const folded = !!(p.closest('details:not([open])') && !p.closest('summary'));
    if (!folded && !shown(p)) continue;
    if (folded) { let ok = true; for (let n = p.closest('details'); n; n = n.parentElement) { if (n.nodeType !== 1) break; const c = getComputedStyle(n); if (c.display === 'none' || c.visibility === 'hidden') { ok = false; break; } } if (!ok) continue; }
    const e = holder(t); if (!held.has(e)) { held.set(e, { parts: [], folded }); order.push(e); }
    // the words as the page spaces them: text nodes are joined as they stand (emphasis inside a sentence adds no space); a line break between two is a space
    let br = false; for (let n = t; n && n !== e && !br; n = n.parentNode) { const ps = n.previousSibling; if (ps && ps.nodeType === 1 && ps.tagName === 'BR') br = true; else if (ps) break; }
    held.get(e).parts.push((br ? ' ' : '') + t.nodeValue); }
  const first = new Map();
  for (const e of order) { if (out.length >= MAX) break; const g = held.get(e), text = norm(g.parts.join('')); if (!text) continue;
    const r = e.getBoundingClientRect(), cs = getComputedStyle(e); if (!g.folded && (r.width < 1 || r.height < 1)) continue;
    let k = kindOf(e);
    // a block that is nothing but one link or button is a call, not a paragraph
    if (k.kind === 'p' || k.kind === 'li') { const a = e.matches('a[href],button,[role="button"]') ? e : (() => { const c = [...e.querySelectorAll('a[href],button,[role="button"]')]; return c.length === 1 && norm(c[0].innerText || c[0].textContent) === text ? c[0] : null; })();
      if (a && k.kind === 'p') k = { kind: 'a', ...(a.href ? { href: a.href } : {}) }; else if (a && a.href) k.href = a.href; }
    const key = k.kind + '|' + text.toLowerCase(), same = first.get(key);
    const b = { i: out.length, ...k, text: text.slice(0, 4000), region: region(e), x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height), px: Math.round(parseFloat(cs.fontSize) * 10) / 10, bold: +cs.fontWeight >= 600,
      ...(g.folded ? { folded: true } : {}), ...(dim(e) ? { dim: true } : {}), ...(same !== undefined ? { same } : {}) };
    if (same === undefined) first.set(key, b.i); out.push(b); }
  // the pictures shown on the page, each where it stands
  const pics = [];
  for (const im of document.images) { if (!shown(im)) continue; const r = im.getBoundingClientRect(); if (r.width < 80 || r.height < 60) continue; const src = im.currentSrc || im.src || ''; if (!src || src.startsWith('data:')) continue;
    pics.push({ kind: 'img', text: norm(im.alt), src, region: region(im), x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height) }); }
  for (const el of document.querySelectorAll('body *')) { if (pics.length >= 120) break; const bg = getComputedStyle(el).backgroundImage, m = bg && bg.match(/url\("?([^")]+)"?\)/); if (!m || m[1].startsWith('data:') || !shown(el)) continue;
    const r = el.getBoundingClientRect(); if (r.width < 280 || r.height < 180) continue; let src; try { src = new URL(m[1], location.href).href; } catch { continue; }
    pics.push({ kind: 'img', text: '', src, bg: true, region: region(el), x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height) }); }
  // one list in reading order: by where a block starts down the page, then across it; a picture before the words it stands level with
  const all = out.concat(pics.slice(0, 120)).map((b, n) => ({ b, n })).sort((p, q) => (p.b.y - q.b.y) || (p.b.x - q.b.x) || (p.n - q.n)).map(({ b }) => b);
  const renum = new Map(); all.forEach((b, n) => { if (b.i !== undefined) renum.set(b.i, n); });
  all.forEach((b, n) => { if (b.same !== undefined) b.same = renum.get(b.same); b.i = n; });
  // the check: of the words the page shows, how many stand in a block
  const words = s => norm(s).toLowerCase().split(' ').filter(Boolean), page = words(document.body.innerText), have = new Map();
  for (const b of all) if (b.kind !== 'img' && !b.folded) for (const w of words(b.text)) have.set(w, (have.get(w) || 0) + 1);
  // a closed menu's choices are a form's furniture, not the page's words: they are not counted either way
  const menu = new Map(); for (const o of document.querySelectorAll('select option')) for (const w of words(o.textContent)) menu.set(w, (menu.get(w) || 0) + 1);
  let hit = 0, total = 0; for (const w of page) { const n = have.get(w) || 0; if (n > 0) { hit++; total++; have.set(w, n - 1); } else if (menu.get(w) > 0) menu.set(w, menu.get(w) - 1); else total++; }
  return { url: location.href, lang: document.documentElement.lang || '', blocks: all, count: all.length, words: total, covers: total ? Math.round(hit / total * 1000) / 1000 : 1, capped: out.length >= MAX };
})()
