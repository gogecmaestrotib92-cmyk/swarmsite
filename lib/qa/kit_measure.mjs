// kit_measure.mjs — what a page sets, read in the browser: the type in use (what it is on the page — heading, button,
// navigation, running text … — the element it is mostly set on, face, size,
// weight, line height, tracking, how often, an example), the corner radii in use, and the width the content runs to.
// Run in the page (page.evaluate(MEASURE)) at 1440. lib/templates/kit.py writes these into the package's
// design/DESIGN.md. They are readings of that one page, not rules invented for it.
export const MEASURE = () => { const vis = el => { const r = el.getBoundingClientRect(), cs = getComputedStyle(el); return r.width > 1 && r.height > 1 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > .05; };
  const own = el => [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').replace(/\s+/g, ' ').trim();
  const groups = new Map(), bodyChars = new Map();
  // what a piece of text is on the page, read from where it stands and how it is drawn — never from its size alone:
  // a heading by its element, a button by its painted box, navigation and foot by the region, a label by its capitals
  const painted = el => { const c = getComputedStyle(el); return (c.backgroundColor !== 'rgba(0, 0, 0, 0)' && c.backgroundColor !== 'transparent') || c.borderTopWidth !== '0px' || c.boxShadow !== 'none'; };
  const role = (el, cs, size) => { if (size >= 120) return 'Display word'; const h = el.closest('h1,h2,h3,h4,h5'); if (h) return h.tagName === 'H1' ? 'Main heading' : h.tagName === 'H2' ? 'Section heading' : 'Item heading';
    const act = el.closest('a,button,summary'); if (act && (painted(act) || painted(el)) && act.getBoundingClientRect().height < 90) return 'Button';
    if (el.closest('nav') || (el.closest('header') && act)) return 'Navigation'; if (el.closest('footer')) return 'Foot';
    if (act && act.tagName === 'SUMMARY') return 'Question'; if (act) return 'Link';
    if (cs.textTransform === 'uppercase' && size <= 15) return 'Label'; return 'text'; };
  for (const el of document.body.querySelectorAll('h1,h2,h3,h4,h5,p,li,a,button,span,div,blockquote,figcaption,dt,dd,label,small,strong,em')) { const t = own(el); if (t.length < 2 || !vis(el)) continue; const cs = getComputedStyle(el);
    const size = Math.round(parseFloat(cs.fontSize) * 10) / 10, family = cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), lh = parseFloat(cs.lineHeight), ls = parseFloat(cs.letterSpacing);
    const key = [family, size, cs.fontWeight, isNaN(lh) ? 'normal' : Math.round(lh / size * 100) / 100, isNaN(ls) ? 0 : Math.round(ls / size * 1000) / 1000].join('|');
    const g = groups.get(key) || { family, size, weight: cs.fontWeight, line: isNaN(lh) ? 'normal' : Math.round(lh / size * 100) / 100, tracking: isNaN(ls) || !ls ? '0' : (Math.round(ls / size * 1000) / 1000) + 'em', count: 0, chars: 0, tags: {}, roles: {}, example: '' };
    g.count++; g.chars += t.length; const tag = el.closest('h1,h2,h3,h4,button,a.btn,[class*="btn"]')?.tagName || el.tagName; g.tags[tag] = (g.tags[tag] || 0) + 1;
    const r = role(el, cs, size); g.roles[r] = (g.roles[r] || 0) + t.length; if (r === 'text') bodyChars.set(size, (bodyChars.get(size) || 0) + t.length); if (t.length > g.example.length && t.length < 90) g.example = t; groups.set(key, g); }
  const body = [...bodyChars.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] || 16;   // the size most of the running text is set in
  const label = g => { const top = Object.entries(g.roles).sort((a, b) => b[1] - a[1])[0][0]; return top !== 'text' ? top : g.size >= body * 1.9 ? 'Large statement' : g.size >= body * 1.15 ? 'Lead text' : g.size >= body * 0.97 ? 'Running text' : 'Small text'; };
  const on = g => Object.entries(g.tags).sort((a, b) => b[1] - a[1])[0][0].toLowerCase();
  const type = [...groups.values()].filter(g => g.count >= 2 || g.size >= 28).sort((a, b) => b.size - a.size || b.chars - a.chars).slice(0, 12).map(g => ({ role: label(g), on: on(g), family: g.family, size: g.size, weight: g.weight, line: g.line, tracking: g.tracking, count: g.count, example: g.example }));
  const radii = new Map(); for (const el of document.body.querySelectorAll('*')) { if (!vis(el)) continue; const cs = getComputedStyle(el), r = cs.borderTopLeftRadius; if (!r || r === '0px') continue; const painted = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || cs.borderTopWidth !== '0px' || cs.boxShadow !== 'none' || cs.overflow !== 'visible' || el.tagName === 'IMG'; if (!painted) continue; const rect = el.getBoundingClientRect(); const v = parseFloat(r) >= Math.min(rect.width, rect.height) / 2 - 1 ? 'full (pill or circle)' : Math.round(parseFloat(r)) + 'px'; radii.set(v, (radii.get(v) || 0) + 1); }
  const widths = new Map(); for (const el of document.body.querySelectorAll('h1,h2,h3,p,ul,ol,[class]')) { if (!vis(el)) continue; const w = Math.round(el.getBoundingClientRect().width); if (w < innerWidth * .5 || w > innerWidth - 16) continue; widths.set(w, (widths.get(w) || 0) + 1); }
  const content = [...widths.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] || null;
  return { at: innerWidth, type, radii: [...radii.entries()].sort((a, b) => b[1] - a[1]).map(([value, count]) => ({ value, count })), width: { content } }; };
