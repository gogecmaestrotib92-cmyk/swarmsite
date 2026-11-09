"""quick.py — the instant first version: the captured page poured into the house template, no model call.

The real director (direct.py) takes about a minute; the swarm another two or three. This writes a deterministic
direction.json from inventory.json + audit.json + images.json in well under a second, so the worker can render and
publish a v0 the person looks at while the agents work. Everything here is the site's own words and pictures in
source order; nothing is invented, nothing is rewritten. The director overwrites direction.json when it finishes.

Usage: python3 quick.py <job dir>   → writes <dir>/direction.json, prints a one-line JSON summary
"""
import json, os, re, sys
from urllib.parse import urlparse

HOUSE = {'software': 'cerebrium', 'place': 'white-desert', 'service': 'atelier', 'product': 'halfdays'}
KIND = {'data_product': 'software', 'saas': 'software', 'restaurant': 'place', 'agency': 'service', 'services': 'service',
        'nonprofit': 'service', 'ecommerce': 'product', 'unknown': 'service'}
MODE = {'cerebrium': 'dark', 'white-desert': 'light', 'atelier': 'light', 'halfdays': 'light'}


def words(s): return len(str(s or '').split())


def cut(s, n):
    """First n words, cut at a sentence end when one comes early enough."""
    w = str(s or '').split()
    if len(w) <= n: return ' '.join(w)
    head = ' '.join(w[:n])
    m = re.search(r'^(.{%d,}?[.!?])\s' % max(10, len(head) // 2), head + ' ')
    return (m.group(1) if m else head.rstrip(',;:—-')).strip()


def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', str(text or '').strip()) if words(s) >= 3]


def brand_name(inv):
    t = str(inv.get('title') or '')
    for sep in (' — ', ' – ', ' | ', ' · ', ': '):
        if sep in t: t = t.split(sep)[0]; break
    t = t.strip()
    if 1 <= words(t) <= 4: return t
    host = (urlparse(inv.get('url') or '').hostname or '').replace('www.', '')
    return host.split('.')[0].capitalize() if host else (t or 'Site')


def pick_hero_image(images, kind):
    cands = [i for i in images if i.get('data') and not re.search(r'logo|icon|favicon|badge', str(i.get('alt') or '') + str(i.get('src') or ''), re.I)]
    if not cands: return ''
    def score(i):
        w, h = float(i.get('w') or 0), float(i.get('h') or 1)
        shot = bool(i.get('shot'))
        return (shot if kind == 'software' else not shot, bool(i.get('heroGrade')), w * h)
    cands.sort(key=score, reverse=True)
    best = cands[0]
    return best['id'] if float(best.get('w') or 0) >= 600 else ''


def quick(slug_dir):
    J = lambda n: json.load(open(os.path.join(slug_dir, n))) if os.path.exists(os.path.join(slug_dir, n)) else None
    inv = J('inventory.json') or {}; audit = J('audit.json') or {}; images = J('images.json') or []; brief = J('brief.json') or {}
    kind = KIND.get(str(audit.get('industry') or 'unknown'), 'service')
    bp = HOUSE[kind]
    name = brand_name(inv)
    copy = inv.get('copy') or {}; seo = inv.get('seo') or {}
    secs = [s for s in ((inv.get('sourceCoverage') or {}).get('sections') or []) if isinstance(s, dict) and s.get('title')]

    # ---- hero: their h1, their first paragraph, their first action
    h1 = (copy.get('h1') or '').strip() or (secs[0]['title'] if secs else '') or str(inv.get('title') or name)
    h1 = cut(h1, 8)
    hero_sec = next((s for s in secs if s.get('title') and (copy.get('h1') or '').strip() and s['title'].strip() == (copy.get('h1') or '').strip()), secs[0] if secs else None)
    lede = (seo.get('description') or '').strip()
    if not (12 <= words(lede) <= 40):
        body = hero_sec.get('text') if hero_sec else copy.get('text')
        body = re.sub(r'^\s*' + re.escape(h1) + r'\s*', '', str(body or ''))
        lede = cut(body, 28)
    actions = [a for a in (inv.get('actions') or []) if isinstance(a, dict) and a.get('text') and str(a.get('href') or '').startswith('http') and a.get('region') not in ('footer',)]
    buttons = [str(b).strip() for b in (copy.get('buttons') or []) if str(b).strip()]
    SKIP = r'(home|about|blog|faq|menu|contact|login|log ?in|sign ?in|skip to (main )?content|skip|privacy|terms|cookie|back to top|read more|learn more|next|previous|close)'
    def is_verb(t): t = str(t).strip(); return 1 <= words(t) <= 5 and not re.fullmatch(SKIP, t, re.I) and not re.search(r'^(https?://|#)', t)
    def rank(a):  # the nav's own button first, then short button labels, then any short action; never a price plan line
        t = a['text'].strip(); btn = any(t.lower() == b.lower() for b in buttons)
        return (a.get('region') != 'nav', not btn, bool(re.search(r'[$€£]|\d', t)), words(t))
    cands = sorted([a for a in actions if is_verb(a['text'])], key=rank)
    primary = cands[0] if cands else None
    bcands = sorted([b for b in buttons if is_verb(b)], key=lambda t: (bool(re.search(r'[$€£]|\d', t)), words(t)))
    cta = (primary or {}).get('text') or (bcands[0] if bcands else 'See more'); cta_href = (primary or {}).get('href') or inv.get('url') or ''
    cta = cta.strip()[:40]
    if cta.isupper(): cta = cta.capitalize()
    hero_img = pick_hero_image(images, kind)
    hero = {'category': cut(str(inv.get('title') or '').split(' — ')[-1], 8) if ' — ' in str(inv.get('title') or '') else '', 'fact': '',
            'h1': h1, 'lede': lede, 'cta': cta, 'cta_href': cta_href, 'cta2': '', 'cta2_href': '', 'media': hero_img,
            'ui': {'move': 'split' if hero_img else 'default', 'size': 'L', 'align': 'start'}}

    # ---- beats: their sections in their order, one register each
    used_imgs = {hero_img}
    free_imgs = [i['id'] for i in images if i.get('data') and i['id'] not in used_imgs and float(i.get('w') or 0) >= 700 and not re.search(r'logo|icon', str(i.get('alt') or '') + str(i.get('src') or ''), re.I)]
    beats, seen_ids = [], set()
    for s in secs:
        if hero_sec is not None and s is hero_sec: continue
        if len(beats) >= 7: break
        title = cut(str(s['title']), 7); text = str(s.get('text') or '')
        if words(text) < 6 and not s.get('faq'): continue
        bid = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:32] or f'beat-{len(beats) + 1}'
        while bid in seen_ids: bid += '-2'
        seen_ids.add(bid)
        faq = [[str(q.get('question') or q.get('q') or ''), str(q.get('answer') or q.get('a') or q.get('text') or '')] for q in (s.get('faq') or []) if isinstance(q, dict)]
        faq = [[q, a] for q, a in faq if q and a][:8]
        if len(faq) >= 2:
            beats.append({'id': bid, 'type': 'faq', 'label': 'FAQ', 'h2': title, 'items': faq, 'source_sections': [s['id']], 'ui': {'move': 'cards'}}); continue
        sents = sentences(re.sub(r'^\s*' + re.escape(str(s['title'])) + r'\s*', '', text))
        if re.search(r'\b(how|steps?|works?|process|way|kako|koraci|postupak|cómo|como|pasos|proceso|wie|ablauf|schritte|comment|étapes)\b', title, re.I) and 3 <= len(sents) <= 6:
            beats.append({'id': bid, 'type': 'steps', 'label': 'How it works', 'h2': title, 'steps': [cut(x, 14) for x in sents[:6]], 'note': '', 'source_sections': [s['id']], 'ui': {'move': 'cards'}}); continue
        if 3 <= len(sents) <= 6 and all(words(x) <= 24 for x in sents) and len(beats) % 2 == 1:
            feats = [{'title': cut(x, 3).rstrip('.,;:'), 'body': cut(x, 18)} for x in sents[:6]]
            beats.append({'id': bid, 'type': 'features', 'label': title, 'h2': title, 'lede': '', 'features': feats, 'source_sections': [s['id']], 'ui': {'move': 'cards', 'cols': 3}}); continue
        img = free_imgs.pop(0) if free_imgs else ''
        beat = {'id': bid, 'type': 'photo', 'label': '', 'h2': title, 'lede': cut(' '.join(sents) or text, 36), 'image': img, 'cap': [], 'source_sections': [s['id']],
                'ui': {'move': 'story', 'photo_layout': 'split'} if img else {'move': 'default'}}
        beats.append(beat)
    if not beats:  # a one-screen page: still a page
        beats.append({'id': 'about', 'type': 'photo', 'label': '', 'h2': name, 'lede': cut(copy.get('text') or lede, 36), 'image': free_imgs[0] if free_imgs else '', 'cap': [], 'ui': {'move': 'default'}})

    # nav labels only when a section title is naturally short; a two-word cut of a long headline reads as a mistake
    def nav_label(b):
        t = str(b.get('label') if b.get('type') in ('faq', 'steps') else b.get('h2') or '').strip().rstrip('.!?')
        if b.get('type') == 'faq': return 'FAQ'
        if 1 <= words(t) <= 2 and len(t) <= 16: return t.capitalize() if t.isupper() else t
        return ''
    nav_links = [[f'#{b["id"]}', nav_label(b)] for b in beats if nav_label(b)][:4]
    foot = [a for a in (inv.get('actions') or []) if isinstance(a, dict) and a.get('region') == 'footer' and a.get('text') and words(a['text']) <= 4]
    cols = []
    if foot: cols.append(['Site', [a['text'].strip() for a in foot[:6]]])
    ending = {'tag': h1, 'cols': cols, 'next': f'{cta} →', 'legal': f'© {name}'}
    d = {'blueprint': bp, 'change': 'restructure', 'kind': kind, 'concept': 'C2', 'mode': MODE[bp], 'voice': 'sans' if kind in ('software', 'product') else 'serif',
         'brand': {'name': name, 'badge': '', 'keep_font': bool(brief.get('keepFont')), 'font_hint': '', 'accent': '', 'paper': '', 'ink': ''},
         'nav': {'links': nav_links, 'cta': cta}, 'hero': hero, 'beats': beats, 'ending': ending,
         'audit_notes': ['Instant first version: the page poured into the house template in source order; the director and the swarm replace it.'],
         'quick': True}
    return d


if __name__ == '__main__':
    slug_dir = sys.argv[1]
    d = quick(slug_dir)
    json.dump(d, open(os.path.join(slug_dir, 'direction.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({'quick': {'blueprint': d['blueprint'], 'kind': d['kind'], 'beats': len(d['beats']), 'hero_media': d['hero']['media']}}))
