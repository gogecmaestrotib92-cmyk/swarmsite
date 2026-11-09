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
  // A cookie or consent banner is the visitor's chore, not the page's content: its words are kept apart (copy.consent) —
  // out of the copy, the word count, the headings, the button list and the sections. Two signals are required: the element is
  // named like a banner (id, class or label) AND its own text asks for a decision about cookies or privacy. A bakery's
  // "cookie-box" section has the name but not the ask, and stays content. Never the page itself: not body/main, nothing
  // that holds the h1, nothing that is most of the page.
  const CONSENT_NAME = '[id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],[id*="gdpr" i],[class*="gdpr" i],[aria-label*="cookie" i],[aria-label*="consent" i],[id*="onetrust" i],[id*="cookiebot" i],[class*="cmplz" i],[id*="didomi" i],[class*="iubenda" i]';
  const CONSENT_ASK = /(accept|agree|allow|reject|decline|preferences|aceptar|acepto|rechazar|configurar|akzeptieren|ablehnen|zustimmen|einstellungen|accepter|refuser|param[eè]tres|accetta|rifiuta|aceitar|recusar|prihvat|odbij|slažem|podešavanja|sprejmi|zavrni)/i;
  const CONSENT_TOPIC = /(cookie|kolači|kolaci|piškot|keks|privac|datenschutz|gdpr|rgpd|consent)/i;
  const wholeText = txt(document.body);
  const consentCandidates = q(CONSENT_NAME).filter(vis).filter(el => {
    if (el === document.body || el === document.documentElement || el.matches('main,[role=main],#__next,#root,#app') || el.querySelector('h1,main,[role=main]')) return false;
    const t = txt(el); return t.length >= 20 && t.length <= 4000 && t.length <= wholeText.length * .75 && CONSENT_ASK.test(t) && CONSENT_TOPIC.test(t);
  });
  const consentEls = consentCandidates.filter(el => !consentCandidates.some(o => o !== el && o.contains(el)));
  const inConsent = el => consentEls.some(c => c === el || c.contains(el));
  let bodyText = wholeText; for (const block of consentEls.map(txt)) bodyText = bodyText.split(block).join(' ');
  bodyText = bodyText.replace(/\s+/g, ' ').trim();
  const consentText = consentEls.map(txt).join(' ').slice(0, 4000);
  const headings = q('h1,h2,h3').filter(vis).filter(h => !inConsent(h)).map(h => ({ tag: h.tagName, text: txt(h).slice(0, 100), words: words(txt(h)) }));
  const buttons = [...new Set(q('a,button').filter(vis).filter(b => !inConsent(b)).map(txt).filter(t => t && t.length < 40 && /[a-z]/i.test(t)))];
  const fragmentNavigable = href => {
    let target; try { target = new URL(href, location.href); } catch { return false; }
    if (!target.hash) return null;
    if (target.origin !== location.origin || target.pathname !== location.pathname || target.search !== location.search) return false;
    let id; try { id = decodeURIComponent(target.hash.slice(1)); } catch { return false; }
    const node = document.getElementById(id) || document.getElementsByName(id)[0];
    if (!node || node.closest('[role="dialog"], [aria-modal="true"], dialog')) return false;
    for (let el = node; el; el = el.parentElement) {
      const style = cs(el);
      if (el.hidden || el.getAttribute('aria-hidden') === 'true' || style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) <= .05) return false;
    }
    return true;
  };
  const actions = q('a[href]').filter(vis).map(a => ({ text: txt(a).slice(0, 100), href: a.href, fragment_navigable: fragmentNavigable(a.href), region: a.closest('form') ? 'form' : a.closest('[role=application],[data-demo]') ? 'demo' : a.closest('nav,header') ? 'nav' : a.closest('footer') ? 'footer' : 'main' }))
    .filter(a => a.text && /^(https?:|mailto:|tel:)/i.test(a.href)).slice(0, 100);
  const forms = q('form').filter(vis).map(form => {
    const source = new URL(location.href); if (form.id) source.hash = form.id;
    const submit = form.querySelector('button[type="submit"], input[type="submit"], button:not([type])');
    return { source_url: source.href, text: submit ? (txt(submit) || submit.value || '').slice(0, 100) : '' };
  }).slice(0, 10);

  // Keep the source's actual page structure separately from the visual audit.
  // Huge layout wrappers and nested <header>s are not independent sections.
  // These records are evidence for planning/coverage, not generated pages.
  const sourceBlocks = q('section, main > article, main > [role="region"]')
    .filter(vis)
    .filter(el => !inConsent(el))
    .filter(el => !el.closest('nav,header,footer,dialog,[role="dialog"]'))
    .filter(el => el.getBoundingClientRect().height > 80);
  const belongsToBlock = (parent, block) => {
    for (let el = parent; el && el !== block; el = el.parentElement) {
      if (el.matches('section, main > article, main > [role="region"]')) return false;
    }
    return block.contains(parent);
  };
  // Read accordion content already present in the DOM; never click controls,
  // submit forms or pretend an asynchronously loaded answer was observed.
  const disclosureText = el => { const copy = el.cloneNode(true); copy.querySelectorAll('script,style,template,noscript').forEach(x => x.remove()); return (copy.textContent || '').replace(/\s+/g, ' ').trim(); };
  // Other closed panels are evidence candidates, not automatically verified
  // facts. Read only unique, explicitly associated panels in this same section;
  // never click a control or follow its links during this pass.
  const excludedEvidence = 'nav,header,footer,dialog,[role="dialog"],form,script,style,template,noscript';
  const evidenceText = el => {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const parts = [];
    while (walker.nextNode()) {
      const parent = walker.currentNode.parentElement;
      if (parent && !parent.closest(excludedEvidence)) parts.push(walker.currentNode.textContent);
    }
    return parts.join(' ').replace(/\s+/g, ' ').trim();
  };
  const evidenceLinks = el => [...el.querySelectorAll('a[href]')].filter(a => !a.closest(excludedEvidence)).map(a => {
    let url; try { url = new URL(a.getAttribute('href'), location.href); } catch { return null; }
    if (!/^https?:$/.test(url.protocol)) return null;
    const label = evidenceText(a); return label ? { label: label.slice(0, 160), url: url.href } : null;
  }).filter(Boolean);
  const candidatePanels = (block, ownOnly = false) => {
    const items = []; let count = 0;
    for (const trigger of block.querySelectorAll('[aria-expanded]')) {
      if (!vis(trigger) || trigger.closest('details,' + excludedEvidence) || ownOnly && !belongsToBlock(trigger, block)) continue;
      const label = txt(trigger) || trigger.getAttribute('aria-label') || ''; if (!label) continue;
      const controlled = (trigger.getAttribute('aria-controls') || '').trim().split(/\s+/).filter(Boolean);
      let matches = [];
      if (controlled.length === 1) matches = [...document.querySelectorAll('[id]')].filter(el => el.id === controlled[0]);
      else if (!controlled.length && trigger.id) matches = [...block.querySelectorAll('[aria-labelledby][role="region"]')].filter(el => el.getAttribute('aria-labelledby').split(/\s+/).includes(trigger.id));
      const panel = matches.length === 1 && block.contains(matches[0]) && !matches[0].closest(excludedEvidence) && (!ownOnly || belongsToBlock(matches[0], block)) ? matches[0] : null;
      const content = panel ? evidenceText(panel) : ''; const links = panel ? evidenceLinks(panel) : [];
      count++;
      if (items.length < 20) items.push({ trigger: label.slice(0, 500), triggerTruncated: label.length > 500,
        panelId: panel?.id || null, association: panel ? (controlled.length ? 'aria-controls' : 'aria-labelledby') : null,
        status: panel && content ? 'candidate' : 'unavailable', text: content.slice(0, 2000), textTruncated: content.length > 2000,
        links: links.slice(0, 20), linksTruncated: links.length > 20 });
    }
    return { panels: items, panelsTruncated: count > items.length };
  };
  const evidenceVisible = el => {
    if (!vis(el)) return false;
    for (let p = el; p; p = p.parentElement) {
      const style = cs(p);
      if (p.hidden || p.hasAttribute('inert') || p.getAttribute('aria-hidden') === 'true' || style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) <= .05) return false;
    }
    return true;
  };
  // Versioned source-section link evidence: retain only real visible links
  // from content, never UI mockups or hidden navigation/form controls.
  const sectionActions = (block, ownOnly = false) => {
    const excluded = 'nav,footer,dialog,[role="dialog"],form,[role="application"],[data-demo],[data-testid*="mock" i],[data-testid*="demo" i],[inert],[aria-hidden="true"],figure';
    const list = []; let count = 0, excludedCount = 0; const seen = new Set();
    for (const a of block.querySelectorAll('a[href]')) {
      if (ownOnly && !belongsToBlock(a, block) || !evidenceVisible(a)) continue;
      // A section's own header is part of its content, unlike a site header.
      // Any ambiguous/non-section header remains excluded.
      const header = a.closest('header');
      if (a.closest(excluded) || header && !(block.contains(header) && header.closest('section') === block)) { excludedCount++; continue; }
      const raw = a.getAttribute('href'); if (!raw || /[\x00-\x20\x7f]/.test(raw)) { excludedCount++; continue; }
      let u; try { u = new URL(raw, location.href); } catch { excludedCount++; continue; }
      if (!/^https?:$/.test(u.protocol) || !u.hostname || u.username || u.password) { excludedCount++; continue; }
      const hostname = u.hostname.toLowerCase().replace(/\.+$/, '');
      if (hostname === 'localhost' || /\.(localhost|local|internal)$/.test(hostname) || /^\d+\.\d+\.\d+\.\d+$/.test(hostname) || hostname.includes(':')) { excludedCount++; continue; }
      // Original in-page anchors are not rebuilt section IDs.
      if (u.origin === location.origin && u.pathname === location.pathname && u.search === location.search) { excludedCount++; continue; }
      const label = txt(a) || a.getAttribute('aria-label') || ''; if (!label || label.length > 160) { excludedCount++; continue; }
      const key = label + '\n' + u.href; if (seen.has(key)) continue; seen.add(key); count++;
      if (list.length < 20) list.push({ label, url: u.href });
    }
    return { sourceActionsVersion: 1, sourceActions: list, sourceActionsFound: count, sourceActionsExcluded: excludedCount, sourceActionsTruncated: count > list.length };
  };
  // Text in separate rendered blocks or flex/grid items needs a boundary, but
  // inline formatting can split a single word across text nodes. Preserve the
  // original adjacency unless the layout itself creates a visible separation.
  const evidenceTextBoundary = (previous, current) => {
    let common = previous.parentElement;
    while (common && !common.contains(current)) common = common.parentElement;
    if (!common) return false;
    const branch = node => { while (node.parentNode && node.parentNode !== common) node = node.parentNode; return node; };
    const before = branch(previous), after = branch(current);
    if (before === after) return false;
    if (/^(?:inline-)?(?:flex|grid)$/.test(cs(common).display)) return true;
    const separated = node => node.nodeType === Node.ELEMENT_NODE &&
      (node.tagName === 'BR' || /^(?:block|flow-root|list-item|table|flex|grid)$/.test(cs(node).display));
    if (separated(before) || separated(after)) return true;
    for (let node = before.nextSibling; node && node !== after; node = node.nextSibling) if (separated(node)) return true;
    return false;
  };
  const visibleEvidenceText = (el, excludeLinks = false) => {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const parts = []; let previous = null;
    while (walker.nextNode()) {
      const parent = walker.currentNode.parentElement;
      if (parent && !parent.closest(excludedEvidence) && (!excludeLinks || !parent.closest('a')) && evidenceVisible(parent)) {
        if (previous && evidenceTextBoundary(previous, walker.currentNode)) parts.push(' ');
        parts.push(walker.currentNode.textContent); previous = walker.currentNode;
      }
    }
    return parts.join('').replace(/\s+/g, ' ').trim();
  };
  const testimonialCandidates = (block, ownOnly = false) => {
    const items = []; let count = 0;
    for (const figure of block.querySelectorAll('figure')) {
      if (!evidenceVisible(figure) || figure.closest(excludedEvidence) || ownOnly && !belongsToBlock(figure, block)) continue;
      // A figure may contain an entire carousel. Pair only the unique visible
      // quote/caption; hidden slides and ambiguous pairings are not guessed.
      const quotes = [...figure.querySelectorAll('blockquote')].filter(q => q.closest('figure') === figure && evidenceVisible(q));
      const captions = [...figure.querySelectorAll('figcaption')].filter(c => c.closest('figure') === figure && evidenceVisible(c));
      if (quotes.length !== 1 || captions.length !== 1) continue;
      const text = visibleEvidenceText(quotes[0]); if (!text) continue;
      const attribution = visibleEvidenceText(captions[0], true);
      // Use the same layout-aware text extraction for visible link labels;
      // inserting spaces blindly can split an inline-formatted word and lose
      // its real destination during the provenance check.
      const links = [...captions[0].querySelectorAll('a[href]')].filter(a => !a.closest(excludedEvidence) && evidenceVisible(a)).map(a => {
        let url; try { url = new URL(a.getAttribute('href'), location.href); } catch { return null; }
        if (!/^https?:$/.test(url.protocol)) return null;
        const label = visibleEvidenceText(a); return label ? { label: label.slice(0, 160), url: url.href } : null;
      }).filter(Boolean);
      count++;
      if (items.length < 40) items.push({ text: text.slice(0, 2000), textTruncated: text.length > 2000,
        attribution: attribution.slice(0, 500), attributionTruncated: attribution.length > 500,
        links: links.slice(0, 10), linksTruncated: links.length > 10, status: 'candidate' });
    }
    return { testimonials: items, testimonialsTruncated: count > items.length };
  };
  const disclosures = (block, ownOnly = false) => {
    const items = []; let count = 0;
    const context = (block.getAttribute('aria-label') || '') + ' ' + (block.querySelector('h1,h2,h3')?.textContent || '');
    const isFaq = /\bfaq\b|frequently asked|questions and answers|preguntas frecuentes|questions fréquentes/i.test(context);
    const add = (question, answer) => { if (!question || (!isFaq && !/\?\s*$/.test(question))) return; count++; if (items.length < 20) items.push({ question: question.slice(0, 500), answer: answer.slice(0, 1200),
      status: answer ? 'readable' : 'unavailable', questionTruncated: question.length > 500, answerTruncated: answer.length > 1200 }); };
    for (const detail of block.querySelectorAll('details')) {
      if (ownOnly && !belongsToBlock(detail, block)) continue;
      const summary = detail.querySelector(':scope > summary'); if (!summary || !vis(summary)) continue;
      const copy = detail.cloneNode(true); copy.querySelector(':scope > summary')?.remove();
      add(txt(summary), disclosureText(copy));
    }
    for (const trigger of block.querySelectorAll('[aria-expanded]')) {
      if (!vis(trigger) || trigger.closest('details') || ownOnly && !belongsToBlock(trigger, block)) continue;
      let panel = trigger.hasAttribute('aria-controls') ? document.getElementById(trigger.getAttribute('aria-controls')) : null;
      if (!panel && trigger.id) {
        const matches = [...block.querySelectorAll('[aria-labelledby][role="region"]')].filter(el => el.getAttribute('aria-labelledby').split(/\s+/).includes(trigger.id));
        if (matches.length === 1) panel = matches[0];
      }
      const answer = panel && block.contains(panel) ? disclosureText(panel) : '';
      add(txt(trigger) || trigger.getAttribute('aria-label') || '', answer);
    }
    if (isFaq) for (const heading of block.querySelectorAll('h3,h4')) {
      if (!vis(heading) || heading.closest('details,[aria-expanded]') || heading.querySelector('[aria-expanded]') || ownOnly && !belongsToBlock(heading, block)) continue;
      const question = txt(heading), sibling = heading.nextElementSibling;
      if (question && /\?\s*$/.test(question) && sibling && !/^H[1-6]$/.test(sibling.tagName) && vis(sibling)) add(question, disclosureText(sibling));
    }
    return { faq: items, faqTruncated: count > items.length };
  };
  const sourceSections = sourceBlocks.map((el, i) => {
    const heading = [...el.querySelectorAll('h1,h2,h3')].find(h => vis(h) && belongsToBlock(h, el));
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const chunks = [];
    while (walker.nextNode()) { const p = walker.currentNode.parentElement; if (p && vis(p) && belongsToBlock(p, el)) chunks.push(walker.currentNode.textContent); }
    const content = chunks.join(' ').replace(/\s+/g, ' ').trim();
    const title = heading ? txt(heading).slice(0, 160) : (el.getAttribute('aria-label') || el.id || '').slice(0, 160);
    const hrefs = [...el.querySelectorAll('a[href]')].filter(a => vis(a) && belongsToBlock(a, el)).map(a => ({ label: txt(a).slice(0, 100), url: a.href }))
      .filter(a => a.label && /^https?:/i.test(a.url)).slice(0, 20);
    return { id: `home-${i + 1}`, title, headingLevel: heading ? heading.tagName : null, _top: el.getBoundingClientRect().top + scrollY, ...disclosures(el, true), ...candidatePanels(el, true), ...testimonialCandidates(el, true), ...sectionActions(el, true),
      labelSource: heading ? 'heading' : el.getAttribute('aria-label') ? 'aria-label' : 'id', text: content.slice(0, 8000),
      textTruncated: content.length > 8000, kind: el.querySelector('details,[aria-expanded]') ? 'disclosure' : heading ? 'section' : 'unheaded', sourceUrl: location.href, links: hrefs };
  }).filter(el => el.title && (words(el.text) >= 3 || el.faq.length));
  // Many production sites use divs instead of semantic sections. Preserve
  // visible H2 topics that were not already collected, including topics after
  // the legacy body-text cutoff, without inventing a page or its content.
  const norm = s => String(s || '').toLocaleLowerCase().replace(/\s+/g, ' ').trim();
  const knownHeadings = new Set(sourceSections.filter(s => s.headingLevel).map(s => norm(s.title)));
  // Some sites have no H2 at all and use H3 for their visible topics. Keep
  // those as heading evidence only when no stronger section structure was
  // found; do not mislabel every card on a structured page as a section.
  const fallbackHeading = sourceSections.length === 0 && !q('h2').some(vis) ? 'h3' : 'h2';
  for (const [i, heading] of q(fallbackHeading).entries()) {
    if (!vis(heading) || heading.closest('nav,footer,dialog,[role="dialog"]')) continue;
    const title = txt(heading).slice(0, 160); const key = norm(title); if (!title || knownHeadings.has(key)) continue;
    knownHeadings.add(key);
    let container = heading.parentElement; const parent = container?.parentElement;
    if (container && txt(container).length < title.length + 16 && parent && !parent.matches('main,body') && parent.querySelectorAll(fallbackHeading).length === 1 && txt(parent).length <= 2200) container = parent;
    const full = container && container.querySelectorAll(fallbackHeading).length === 1 ? txt(container) : title;
    sourceSections.push({ id: `home-heading-${i + 1}`, title, headingLevel: heading.tagName, labelSource: 'heading', text: full.slice(0, 8000), ...disclosures(container || heading), ...candidatePanels(container || heading), ...testimonialCandidates(container || heading), ...sectionActions(container || heading),
      textTruncated: full.length > 8000, kind: 'heading', sourceUrl: location.href, links: [], _top: heading.getBoundingClientRect().top + scrollY });
  }
  sourceSections.sort((a, b) => a._top - b._top); sourceSections.forEach(s => delete s._top);
  const routes = []; const seenRoutes = new Set(); let routeCount = 0;
  for (const a of q('a[href]').filter(vis)) {
    const label = txt(a).slice(0, 100); if (!label) continue;
    let target; try { target = new URL(a.href, location.href); } catch { continue; }
    if (!/^https?:$/.test(target.protocol) || target.origin !== location.origin) continue;
    // Section anchors are tracked as content, not independent pages.
    if (target.pathname === location.pathname && target.search === location.search) continue;
    target.hash = ''; if (seenRoutes.has(target.href)) continue; seenRoutes.add(target.href); routeCount++;
    if (routes.length < 5000) routes.push({ url: target.href, label, status: 'discovered', reason: 'Visible link; not yet inspected' });
  }
  const metaContent = name => document.querySelector(`meta[name="${name}" i]`)?.getAttribute('content')?.trim().slice(0, 1000) || null;
  const linkHref = el => { try { const u = new URL(el.getAttribute('href'), location.href); return /^https?:$/.test(u.protocol) ? u.href : null; } catch { return null; } };
  const canonicalElement = document.querySelector('link[rel~="canonical" i][href]');
  const alternates = q('link[rel~="alternate" i][hreflang][href]').map(el => ({ lang: el.getAttribute('hreflang').slice(0, 64), href: linkHref(el) })).filter(x => x.href).slice(0, 30);
  const jsonLd = q('script[type="application/ld+json" i]'); const types = new Set(); let invalidJsonLd = 0;
  const collectTypes = (v, depth = 0) => { if (!v || depth > 8 || typeof v !== 'object') return; if (Array.isArray(v)) { v.slice(0, 100).forEach(x => collectTypes(x, depth + 1)); return; }
    const t = v['@type']; (Array.isArray(t) ? t : [t]).filter(x => typeof x === 'string').forEach(x => types.add(x.slice(0, 100))); if (v['@graph']) collectTypes(v['@graph'], depth + 1); };
  jsonLd.slice(0, 30).forEach(el => { try { collectTypes(JSON.parse(el.textContent)); } catch { invalidJsonLd++; } });
  // the SEO-safe rebuild carries these over verbatim: structured data as written, og tags, the exact title
  const property = name => document.querySelector(`meta[property="${name}" i]`)?.getAttribute('content')?.trim().slice(0, 1000) || null;
  let ldBudget = 24000; const jsonLdRaw = jsonLd.map(el => (el.textContent || '').trim()).filter(t => { try { JSON.parse(t); } catch { return false; } if (t.length > ldBudget) return false; ldBudget -= t.length; return true; });
  const seo = { title: document.title.slice(0, 300), description: metaContent('description'), canonical: canonicalElement ? linkHref(canonicalElement) : null,
    robots: metaContent('robots'), hreflang: alternates, og: { title: property('og:title'), description: property('og:description'), image: property('og:image'), type: property('og:type') },
    structuredData: { jsonLdCount: jsonLd.length, invalidJsonLd, types: [...types].slice(0, 30), raw: jsonLdRaw } };

  return {
    url: location.href, title: document.title, lang: document.documentElement.lang || null,
    viewport: { w: innerWidth, h: innerHeight }, pageHeight: document.documentElement.scrollHeight,
    sections, sectionCount: sections.length, actions, forms, seo,
    sourceCoverage: { faqCatalogVersion: 1, sections: sourceSections.slice(0, 500), sectionsFound: sourceSections.length, sectionLimit: 500,
      sectionsTruncated: sourceSections.length > 500, routes, routesFound: routeCount, routesTruncated: routeCount > routes.length },
    copy: { totalWords: words(bodyText), headings, headingCount: headings.length, h1: h1 ? txt(h1) : null, h1Words: h1 ? words(txt(h1)) : 0, buttons: buttons.slice(0, 30), text: bodyText.slice(0, 40000), ...(consentText ? { consent: consentText } : {}) },
    typography: { fonts: [...new Set(typoTop.map(t => t.font))], h1: h1s ? { font: fam(h1), size: Math.round(parseFloat(h1s.fontSize)), weight: h1s.fontWeight, lh: (parseFloat(h1s.lineHeight) / parseFloat(h1s.fontSize)).toFixed(2), ls: h1s.letterSpacing, tt: h1s.textTransform } : null, samples: typoTop },
    colors: { bg: top(bg, 8), text: top(fg, 6), buttons: top(accent, 6) },
    brand: { logo: logo ? (logo.currentSrc || logo.src) : null, logoSvg: logoSvg ? logoSvg.outerHTML.slice(0, 2000) : null, nav, navCount: nav.length, hasFooter: !!footer, footerWords: footer ? words(txt(footer)) : 0, footerLinks: footer ? footer.querySelectorAll('a').length : 0 },
    media: { imgCount: imgs.length, bigImgs: bigImgs.slice(0, 20), video: q('video').length, svg: q('svg').length, canvas: q('canvas').length },
    tech: { libs: Object.entries(libs).filter(x => x[1]).map(x => x[0]), anim }
  };
})();
