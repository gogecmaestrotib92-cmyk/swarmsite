"""seo.py — the SEO-safe mode: what a rebuild must carry over from a page that already ranks.
Two modes, chosen in the brief: 'seo-safe' (default: keep the words, the headings' keywords, every link, the meta and the structured data)
and 'free' (the studio redesign). Everything here is deterministic; the agents read the rules, the renderer and the contract enforce them."""
import json, os, re

STOP = set("""a an and are as at be by for from has have in is it its of on or that the this to was were will with your you our we us
i y o u e el la los las un una unos unas de del al en con por para que es son como su sus se lo le más mas sin sobre entre hasta
i u na za od do sa se je su da ne ili ali kao što sto to te ta taj ova ovaj ove ovo svoj svoje naš naše nas vas vaš vaše
und der die das ein eine mit von zu für auf im ist sind et le les des du un une au aux en dans pour par sur est sont""".split())

def mode(brief):
    m = str((brief or {}).get('mode') or '').lower()
    return 'free' if m in ('free', 'studio', 'creative') else 'seo-safe'

def words(text):
    return re.findall(r"[^\W\d_]{3,}", str(text or '').lower(), re.UNICODE)

def keywords(text, limit=8):
    """The content words of a heading, in order, without stopwords: what a page is ranking for."""
    out = []
    for w in words(text):
        if w in STOP or w in out: continue
        out.append(w)
    return out[:limit]

def keyword_coverage(source_heading, new_heading):
    """Share of the source heading's keywords that survive in the new one (or as a stem of ≥5 letters)."""
    src = keywords(source_heading); new = ' '.join(words(new_heading))
    if not src: return 1.0
    kept = sum(1 for k in src if k in new or (len(k) >= 6 and k[:5] in new))
    return kept / len(src)

def text_coverage(source_text, page_text):
    """Share of the source's distinct content words that appear on the page (the honest 'nothing was lost' number)."""
    src = {w for w in words(source_text) if w not in STOP}
    if not src: return 1.0
    page = set(words(page_text))
    return len(src & page) / len(src)

def source_sections(inventory):
    cov = (inventory or {}).get('sourceCoverage') or {}
    return [s for s in (cov.get('sections') or []) if isinstance(s, dict) and s.get('title')]

# The controls of a shop — its cart, its checkout, the customer's own account — are not pages a visitor reads or a search
# engine ranks, and a redesign has no place for them. Named by the last segment of the path, whole, in the languages the
# engine meets; a site's sign-up and sign-in stay links like any other (on a product site they are the point).
UTILITY_SEGMENTS = {'cart', 'basket', 'checkout', 'wishlist', 'my-account', 'cesta', 'carrito', 'carro', 'mi-cuenta', 'warenkorb', 'kasse', 'mein-konto', 'panier', 'mon-compte',
                    'carrello', 'il-mio-account', 'winkelwagen', 'kosarica', 'korpa', 'moj-nalog', 'moj-racun'}
COUNT_LABEL = re.compile(r'\d+(\s+(products?|productos?|items?|art[ií]culos?|articles?|produits?|produkte?|prodotti|proizvoda?|artikala?))?', re.I)


def utility_link(href):
    """Is this link a control of the site's shop — cart, checkout, the customer's account — rather than a page?"""
    try:
        from urllib.parse import urlparse
        u = urlparse(str(href))
    except Exception: return False
    segments = [x.lower() for x in u.path.split('/') if x]
    return bool(segments and segments[-1] in UTILITY_SEGMENTS) or 'add-to-cart=' in (u.query or '').lower()


def internal_links(inventory):
    """Every same-site link the source page offered: these keep the site's crawl paths and internal link equity."""
    url = (inventory or {}).get('url') or ''
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.lower().replace('www.', '')
    except Exception: host = ''
    seen, out = set(), []
    for a in (inventory or {}).get('actions') or []:
        href = str(a.get('href') or ''); text = ' '.join(str(a.get('text') or '').split())
        if not href.startswith('http') or '#' in href.split('/')[-1][:1]: continue
        if a.get('region') in ('form', 'demo'): continue  # a form's own buttons and demo widgets are not pages
        try: u = urlparse(href); h = u.netloc.lower().replace('www.', '')
        except Exception: continue
        if u.username or u.password or not u.hostname or '.' not in u.hostname: continue  # credentials in a URL or a local host never leave the capture
        if host and h != host: continue
        if utility_link(href): continue   # the shop's own controls are not pages
        key = href.rstrip('/')
        if key in seen: continue
        # an anchor whose text is the URL itself, empty, or only a count ("5 products" on a category tile) gets a readable
        # label from its path: /blog/pdf-design-tips → "Pdf design tips", /categorias/del-mar → "Del mar"
        if not text or re.fullmatch(r'(https?://)?[\w.-]+(/\S*)?', text) or COUNT_LABEL.fullmatch(text):
            seg = [x for x in u.path.split('/') if x and not re.fullmatch(r'\d+', x)]
            text = (seg[-1] if seg else h).replace('-', ' ').replace('_', ' ').strip()
            text = re.sub(r'\.[a-z]{2,5}$', '', text); text = text[:1].upper() + text[1:]
        if not text: continue
        seen.add(key); out.append({'href': href, 'text': text[:80]})
    return out[:60]

def rules_text(inventory):
    """The lines the director and the copywriter read in SEO-safe mode."""
    inv = inventory or {}; h1 = (inv.get('copy') or {}).get('h1') or ''; kws = keywords(h1)
    heads = [h.get('text') for h in ((inv.get('copy') or {}).get('headings') or []) if h.get('tag') in ('H1', 'H2')][:14]
    return '\n'.join([
        'SEO-SAFE MODE — this page already ranks; the rebuild must not cost it a single query:',
        f'- The h1 keeps the source h1\'s keywords {kws} (source h1: "{h1[:120]}"). You may add a stance or an <em>, never swap the subject.',
        '- Every source section with a heading becomes a beat whose h2 keeps that heading\'s keywords; use the source heading verbatim when it is ≤ 7 words. Source headings: ' + json.dumps(heads, ensure_ascii=False),
        '- Do not drop or paraphrase factual text (prices, hours, addresses, service names). Shorter is fine only when every fact survives; whatever you cannot place is kept for you in an archive section — never silently cut.',
        '- Keep the page\'s language exactly. Do not translate headings.',
    ])

def describe(inventory):
    inv = inventory or {}; seo = inv.get('seo') or {}
    return {'title': seo.get('title') or inv.get('title'), 'description': seo.get('description'), 'canonical': seo.get('canonical') or inv.get('url'),
            'robots': seo.get('robots'), 'hreflang': seo.get('hreflang') or [], 'og': seo.get('og') or {}, 'jsonld': (seo.get('structuredData') or {}).get('raw') or [],
            'h1': (inv.get('copy') or {}).get('h1') or '', 'links': internal_links(inv), 'sections': len(source_sections(inv))}
