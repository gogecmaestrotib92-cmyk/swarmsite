// cards.js — run in the page (capture.mjs): the parts of a page that the flat text loses their borders in.
//   plans  each price card: the smallest box that holds exactly one price and a list — {name, price, per, line, rows, marked}
//   stats  each number set large with its label beside it — {v, l}
//   steps  each run of numbered marks (1, 2, 3 …) with a heading and a sentence of its own — {title, items: [{k, title, text}]}
// Only what the page prints, as it prints it; nothing is guessed or rewritten.
(() => {
  const vis = e => { const r = e.getBoundingClientRect(), c = getComputedStyle(e); return r.width > 0 && r.height > 0 && c.visibility !== 'hidden' && c.display !== 'none'; };
  const txt = e => (e.innerText || '').replace(/\s+/g, ' ').trim();
  const PRICE = /(?:[$€£]\s?\d[\d.,]*|\d[\d.,]*\s?(?:€|EUR|USD|kn|din|RSD))/;
  const prices = [...document.querySelectorAll('body *')].filter(e => vis(e) && !e.closest('nav, header, footer') && [...e.childNodes].some(n => n.nodeType === 3 && PRICE.test(n.nodeValue)) && txt(e).length <= 40);
  const plans = [], seen = new Set();
  const fs = e => parseFloat(getComputedStyle(e).fontSize) || 0;
  for (let p of prices) {
    // the card: the largest box round this price that holds no other price set as large (a price set small beside it,
    // "$0.63 a day", is not a second card), holds a list, and is not wider than half the screen
    let box = null;
    for (let a = p.parentElement, k = 0; a && a !== document.body && k < 9; a = a.parentElement, k++) {
      const big = fs(p) * .75;
      if (prices.some(x => x !== p && a.contains(x) && !x.contains(p) && !p.contains(x) && fs(x) >= big && txt(x).match(PRICE)[0] !== txt(p).match(PRICE)[0])) break;
      if (a.getBoundingClientRect().width > innerWidth * .55) break;
      if (a.querySelectorAll('li').length >= 2) box = a;
    }
    if (!box || seen.has(box) || box.querySelectorAll('li').length < 2) continue;
    seen.add(box);
    p = prices.filter(x => box.contains(x)).sort((a, b) => parseFloat(getComputedStyle(b).fontSize) - parseFloat(getComputedStyle(a).fontSize))[0] || p;   // the card's price is the one set largest in it
    const head = box.querySelector('h2, h3, h4, h5, [class*="name" i], [class*="title" i], strong, b');
    const name = head ? txt(head).slice(0, 40) : '';
    const priceText = txt(p);
    const m = priceText.match(PRICE);
    const per = (priceText.slice(m.index + m[0].length).trim() || (p.nextElementSibling && txt(p.nextElementSibling).length <= 30 ? txt(p.nextElementSibling) : '')).slice(0, 40);
    const rows = [...box.querySelectorAll('li')].filter(vis).map(txt).filter(t => t && t.length <= 160).slice(0, 12);
    const line = [...box.querySelectorAll('p')].filter(e => vis(e) && !e.contains(p) && !e.closest('li')).map(txt).find(t => t.length >= 8 && t.length <= 140 && !PRICE.test(t)) || '';
    const cs = getComputedStyle(box);
    plans.push({ box, name, price: m[0].replace(/\s+/g, ''), per, line, rows, bg: cs.backgroundColor, border: cs.borderColor, y: Math.round(box.getBoundingClientRect().top + scrollY) });
  }
  // a box inside a card (its own little price row with a list) is part of that card, not a card
  for (let i = plans.length - 1; i >= 0; i--) if (plans.some(q => q !== plans[i] && q.box.contains(plans[i].box))) plans.splice(i, 1);
  const boxes = plans.map(q => q.box); plans.forEach(q => delete q.box);
  // the plan the page marks: the one card whose ground differs from the others'
  const grounds = plans.map(p => p.bg);
  for (const p of plans) { p.marked = plans.length >= 2 && grounds.filter(g => g === p.bg).length === 1 && grounds.filter(g => g !== p.bg).length >= 1 && grounds.filter(g => g !== p.bg).every(g => g === grounds.find(x => x !== p.bg)); delete p.bg; delete p.border; }
  // numbers set large: the text of one element is a figure, its type at least 1.6 times the page's body size, a label of 1–12 words beside it
  const body = parseFloat(getComputedStyle(document.body).fontSize) || 16;
  const stats = [], took = new Set();
  for (const e of document.querySelectorAll('body *')) {
    if (!vis(e) || e.children.length || e.closest('nav, header, footer, li[class*="price" i], [aria-hidden="true"], [role="img"]')) continue;
    const v = txt(e); if (!/^[+−-]?[$€£]?\d[\d.,]*\s?(?:%|\+|k|K|M|x|×|h|s|m)?(?:\s?[–-]\s?\d[\d.,]*)?$/.test(v) || v.length > 12) continue;
    if (parseFloat(getComputedStyle(e).fontSize) < body * 1.6) continue;
    let lab = '';
    for (let a = e.parentElement, k = 0; a && k < 2 && !lab; a = a.parentElement, k++) { const t = txt(a).replace(v, '').trim(); if (t && t.split(' ').length <= 12) lab = t; }
    // a label in words; not a section's number (01), a bare decimal (odds in a mock-up), a price (the plans have those) or a figure inside a price card
    if (!lab || !/^[A-Za-zÀ-ÿ]/.test(lab) || (lab.match(/\d[\d.,]*/g) || []).length >= 2 || /^0\d$|^\d\.\d+$|[$€£]/.test(v) || boxes.some(b => b.contains(e)) || took.has(v + lab)) continue; took.add(v + lab);
    stats.push({ v, l: lab.slice(0, 90), y: Math.round(e.getBoundingClientRect().top + scrollY) });
  }
  // numbered steps: marks that read 1, 2, 3 … (or 01, Step 1) in the page's order, each in a small block of its own with
  // a heading and a sentence, the run no taller than two screens (a page whose sections are numbered is not a run of steps)
  const steps = [];
  const marks = [...document.querySelectorAll('body *')].filter(e => vis(e) && !e.children.length && /^(?:step\s*)?0?[1-9]\.?$/i.test(txt(e)) && !e.closest('nav, header, footer, [aria-hidden="true"], table, select'))
    .map(e => ({ e, n: +txt(e).replace(/\D/g, '') }));
  for (let i = 0; i < marks.length; i++) {
    if (marks[i].n !== 1) continue;
    const run = [marks[i]]; for (let j = i + 1; j < marks.length && marks[j].n === run.length + 1; j++) run.push(marks[j]);
    if (run.length < 3) continue;
    const items = [];
    for (const m of run) {
      let box = m.e.parentElement; while (box && box.parentElement && !run.some(o => o !== m && box.parentElement.contains(o.e))) box = box.parentElement;
      if (!box) break;
      const head = [...box.querySelectorAll('h2, h3, h4, h5, h6, strong, b, [class*="title" i], [class*="heading" i]')].find(h => vis(h) && h !== m.e && !h.contains(m.e) && txt(h).length >= 3 && txt(h).length <= 80);
      const title = head ? txt(head) : '';
      const body = [...box.querySelectorAll('p, div, span')].filter(p => vis(p) && !p.children.length && p !== m.e && (!head || !head.contains(p)) && txt(p).length >= 20 && txt(p).length <= 400).map(txt)[0] || '';
      const r = box.getBoundingClientRect();
      items.push({ k: txt(m.e), title, text: body, top: r.top + scrollY, bottom: r.bottom + scrollY });
    }
    // a later number that stands far below the run, or without a heading and a sentence, is not one of its steps
    while (items.length && (!items[items.length - 1].title || !items[items.length - 1].text || items[items.length - 1].bottom - items[0].top > 1800)) items.pop();
    if (items.length < 3 || items.length > 6 || items.some(x => !x.title || !x.text)) continue;
    // the heading the run stands under: the last h2/h3 before its first mark
    let title = ''; for (const h of document.querySelectorAll('h2, h3')) { if (vis(h) && (h.compareDocumentPosition(run[0].e) & Node.DOCUMENT_POSITION_FOLLOWING) && !items.some(x => x.title === txt(h))) title = txt(h).slice(0, 120); }
    steps.push({ title, items: items.map(({ k, title, text }) => ({ k, title, text })) });

  }
  return { plans: plans.slice(0, 8), stats: stats.slice(0, 12), steps: steps.slice(0, 3) };
})()
