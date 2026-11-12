"""select.py — for one client's data, the up-to-three templates to show it in.

    select(d, limit=3, promised=(), root=None) -> {
        'niche': [...],                 what the client is, most telling first
        'pictures': n,                  the client's own usable pictures (screens, phones, photographs, a film)
        'chosen':   [{'slug', 'approach', 'why', 'pending'}],   in the order to show them
        'rejected': [{'slug', 'why'}],                          every other template of the library, with the reason
    }

Deterministic: the same data and the same library give the same three, in the same order. No model call.

A template is offered only when
  · it has a `needs.json` (a template without one has not been measured on the test clients: it is NOT selectable);
  · one of its niches is the client's;
  · the client's data meets every need it states — counts of photographs and screens, and each named block;
  · and, when the client has no usable picture at all, it says `holds_without_pictures`.
Among those, the three are taken so that they differ in approach where the library allows it.

What a needs.json may say (the vocabulary this file reads — a need it cannot read keeps the template out, with the
reason, rather than being waved through):
  niche: [..]                    one of the fixed words of needs.schema.json (software, app, restaurant, hotel, clinic,
                                 law, service, shop, school, person, corporate, nonprofit) — then exactly that — or
                                 free words, read by the telling words in NICHES below
  photos_min, photos_large_min   photographs in media.photos; large = at least 1600 px wide
  screens_min, phones_ok         product screens in media.screens (+ media.phones when phones_ok)
  step_pictures_min              steps.items that carry a picture
  holds_without_pictures, motif, approach (optional: names the approach outright)
  needs: [..]                    each entry starts with a block of the data — steps, features, figures, plans, faq, links,
                                 statement, close, trust, quotes, logos, video, menu, spaces, hours, booking, hero.text2,
                                 steps.items[].img, made.land / media.made.land, … — optionally followed by words in
                                 brackets: "(3+ items …)", "(2-8 items …)", "… with a picture", "… with k". Also read:
                                 "8 or more product pictures …", "3 upright pictures …", one of several
                                 ("menu or spaces", "media.screens[0] or media.video").
Made pictures (`media.made.*`) are made per client in a later stage. With promised=('made',) a need for them counts as
met and is listed under the variant's `pending`; by default it must be in the data like any other need.
"""
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LARGE = 1600

if __name__ == 'select':
    # Reached by the bare name: lib/render/render_bp.py puts lib/templates first on sys.path (for recipes.py), and from
    # then on a plain `import select` — which the standard library's selectors, subprocess and socket do — would find
    # this file. Hand such an importer the standard library's module instead; this file is loaded by its path
    # (see _registry below, the tests, the server), never by `import select`.
    import importlib.machinery
    _spec = importlib.machinery.PathFinder.find_spec('select', [p for p in sys.path if Path(p or '.').resolve() != HERE])
    if _spec is not None:
        _std = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_std)
        sys.modules['select'] = _std


def _registry():
    key = 'swarmsite_templates_registry'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, HERE / 'registry.py')
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


# a niche is named in free words by whoever measured the template; these are the words that tell
NICHES = (
    ('place', r'\bplaces?\b|restaurant|hotel|venue|hospitality|lodge|caf[eé]|\bbar\b|shop with a door|food|drink|bakery|travel|stay'),
    ('app', r'consumer|an app a person|downloads|phone screens|\bapps?\b'),
    ('saas', r'saas|b2b|compan(?:y|ies)|platform|\bapi\b|fintech|analytics|research'),
    ('software', r'software|product|\btools?\b|\bai\b|desktop|web'),
    ('agency', r'agency|studio|service'),
    ('property', r'property|architect|residence|real estate'),
    ('person', r'one person|athlete|creators?\b|portfolio|personal site'),
    ('shop', r'\bshop\b|store|catalogue|e-?commerce'),
)
SOFTWARE = ('app', 'saas', 'software')
PLACE_KINDS = {'restaurant', 'cafe', 'bar', 'hotel', 'venue', 'place'}
# the fixed words of lib/templates/needs.schema.json (and of the data's `kind`): a niche written as one of them is
# that niche and nothing else — a template for restaurants is not offered to a hotel
FIXED = ('software', 'app', 'restaurant', 'hotel', 'clinic', 'law', 'service', 'shop', 'school', 'person', 'corporate', 'nonprofit')


def niche_tags(words):
    """the niches a niche entry names: itself when it is one of the fixed words, else the telling words of free text"""
    w = str(words or '').lower().strip()
    if w in FIXED:
        return [w]
    return [n for n, rx in NICHES if re.search(rx, w)]


def _n(v):
    """a size as a number; 0 when the data does not give one"""
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else 0


def _pics(d):
    m = d.get('media') if isinstance(d.get('media'), dict) else {}
    lst = lambda k: [x for x in m.get(k) or [] if isinstance(x, dict) and x.get('src')]
    return {'screens': lst('screens'), 'phones': lst('phones'), 'photos': lst('photos'), 'video': [m['video']] if isinstance(m.get('video'), dict) and m['video'].get('src') else []}


def client(d):
    """what the client is and has: niches (most telling first) and its own usable pictures"""
    p = _pics(d)
    kind = str(d.get('kind') or '').lower()
    if kind in ('restaurant', 'cafe', 'bar'):
        niche = ['restaurant', 'place']
    elif kind == 'hotel':
        niche = ['hotel', 'place']
    elif kind in ('software', 'app') or (kind not in FIXED and set(niche_tags(kind)) & set(SOFTWARE)):
        niche = ['app', 'software', 'saas'] if p['phones'] else ['software', 'saas', 'app']
    elif kind in FIXED:                                               # clinic, law, service, shop, school, person, corporate, nonprofit
        niche = [kind]
    elif _has(d.get('place')) or kind in PLACE_KINDS:
        niche = ['place']
    else:
        niche = [n for n in niche_tags(kind) if n not in SOFTWARE]
    usable = [x for k in ('screens', 'phones', 'photos') for x in p[k] if not (_n(x.get('w')) and _n(x.get('h')) and min(_n(x['w']), _n(x['h'])) < 200)] + p['video']
    return {'niche': niche, 'pictures': len(usable), 'pics': p}


def _get(d, path):
    """the values at a dotted path, as a list: one for a plain path, one for each item where `[]` follows a list
    (None where an item lacks the key); empty when the path leads nowhere"""
    cur = [d]
    for part in path.split('.'):
        m = re.match(r'^(.*?)(?:\[(\d*)\])?$', part)
        key, each, at = m.group(1), m.group(2) == '', int(m.group(2)) if m.group(2) else None
        nxt = []
        for c in cur:
            if isinstance(c, dict) and key in c:
                v = c[key]
                if at is not None:                                   # screens[0]: that one of the list, None when the list is shorter
                    v = v[at] if isinstance(v, list) and len(v) > at else None
                nxt += (v if isinstance(v, list) else [v]) if each else [v]
            elif each or isinstance(c, dict):
                nxt.append(None)
        cur = nxt
    return cur


def _has(v):
    """Is there something to show? A block that holds lists (steps, plans, a menu) is there when a list of it has an
    item — its heading alone is not a section; a block of plain lines (statement, close) when one of them is written."""
    if isinstance(v, dict):
        inner = [x for x in v.values() if isinstance(x, (list, dict))]
        return any(_has(x) for x in inner) if inner else any(_has(x) for x in v.values())
    if isinstance(v, list):
        return any(_has(x) for x in v)
    return v not in (None, '', False)


ALIASES = {'made': 'media.made', 'video': 'media.video', 'screens': 'media.screens', 'phones': 'media.phones', 'photos': 'media.photos',
           'menu': 'place.menu', 'spaces': 'place.spaces', 'hours': 'place.hours', 'booking': 'place.booking', 'events': 'place.events', 'address': 'place.address',
           'phone': 'place.phone', 'email': 'place.email', 'social': 'place.social', 'takeaway': 'place.takeaway', 'cuisine': 'place.cuisine', 'since': 'place.since',
           'price_range': 'place.price_range', 'notices': 'place.notices'}
BLOCKS = {'brand', 'nav', 'signin', 'cta', 'hero', 'trust', 'figures', 'statement', 'steps', 'features', 'media', 'plans', 'faq', 'quotes', 'logos', 'links', 'close', 'foot', 'place',
          'team', 'catalogue', 'locations', 'credentials', 'contact', 'projects'}
# the names of the strict form (needs.schema.json) that are a part of every item of a block
STRICT = {'steps.img': 'steps.items[].img', 'steps.k': 'steps.items[].k', 'steps.cta': 'steps.items[].cta', 'features.d': 'features.items[].d', 'links.d': 'links[].d', 'figures.l': 'figures[].l',
          'plans.rows': 'plans.items[].rows', 'spaces.img': 'place.spaces[].img', 'menu.items': 'place.menu.sections[].items', 'team.img': 'team.items[].img', 'catalogue.img': 'catalogue.groups[].items[].img'}


def _either(text):
    """'menu or spaces (rooms)' → ['menu', 'spaces (rooms)']: the ways a need may be met, split at an `or` that stands
    outside brackets"""
    parts, depth, start = [], 0, 0
    for m in re.finditer(r'[()]|\s+or\s+', text):
        if m.group(0) == '(':
            depth += 1
        elif m.group(0) == ')':
            depth = max(0, depth - 1)
        elif depth == 0:
            parts.append(text[start:m.start()].strip())
            start = m.end()
    return parts + [text[start:].strip()]


def need_met(need, d, pics, promised=()):
    """(met, pending, problem) for one entry of `needs`. problem is set when the entry cannot be read."""
    text = str(need or '').strip()
    m = re.match(r'^(\d+)\s+(?:or more\s+)?(upright|product)?\s*pictures?\b', text, re.I)
    if m:
        every = pics['screens'] + pics['phones'] + pics['photos']
        if (m.group(2) or '').lower() == 'upright':
            every = [x for x in every if _n(x.get('w')) and _n(x.get('h')) > _n(x.get('w'))]
        return len(every) >= int(m.group(1)), False, ''
    ways = _either(text)
    if len(ways) > 1:                                                # met when one of them is; unreadable when one of them is
        got = [need_met(w, d, pics, promised) for w in ways]
        problem = next((g[2] for g in got if g[2]), '')
        if problem:
            return False, False, 'a need this step cannot read: %r' % text[:80]
        plain = any(g[0] and not g[1] for g in got)
        return any(g[0] for g in got), not plain and any(g[1] for g in got), ''
    m = re.match(r'^([a-z_]+(?:\[\d*\])?(?:\.[a-z_0-9]+(?:\[\d*\])?)*)\s*(.*)$', text)
    if not m:
        return False, False, 'a need this step cannot read: %r' % text[:80]
    path, rest = m.group(1), m.group(2)
    path = STRICT.get(path, path)
    head = re.sub(r'\[\d*\]$', '', path.split('.')[0])
    if head in ALIASES:
        path = ALIASES[head] + path[len(head):]
    if re.sub(r'\[\d*\]$', '', path.split('.')[0]) not in BLOCKS:
        return False, False, 'a need this step cannot read: %r' % text[:80]
    if rest and not rest.startswith('('):
        return False, False, 'a need this step cannot read: %r' % text[:80]
    vals = _get(d, path)
    ok = bool(vals) and all(_has(v) for v in vals)
    if path == 'place.menu.sections[].items':                       # a menu with dishes: one section that lists them is enough
        ok = any(_has(v) for v in vals)
    if path == 'team.items[].img' and not vals:                      # people may stand in groups instead of one list
        vals = _get(d, 'team.groups[].items[].img')
        ok = bool(vals) and all(_has(v) for v in vals)
    if not ok and path.startswith('media.made') and 'made' in promised:
        return True, True, ''
    # words in brackets: how many items, and what each must carry
    block = _get(d, re.split(r'\[\d*\]', path)[0])
    block = block[0] if len(block) == 1 else None
    items = block.get('items') if isinstance(block, dict) and isinstance(block.get('items'), list) else (block if isinstance(block, list) else None)
    q = rest.lower()
    rng = re.search(r'(\d+)\s*[-–]\s*(\d+)\s+(?:items|steps)', q)
    least = re.search(r'(\d+)\s*\+\s*(?:items|steps)|(\d+)\s+or more', q)
    if items is not None:
        n = len(items)
        if rng and not int(rng.group(1)) <= n <= int(rng.group(2)):
            ok = False
        if least and n < int(least.group(1) or least.group(2)):
            ok = False
        if re.search(r'picture', q) and re.search(r'\beach\b|\bown\b|with a picture', q) and not all(isinstance(i, dict) and i.get('img') for i in items):
            ok = False
        if re.search(r'\bwith k\b', q) and not all(isinstance(i, dict) and i.get('k') for i in items):
            ok = False
    return ok, False, ''


def approach(n):
    """what kind of page a template is, as far as its needs.json tells: named outright, or its picture motif and
    what carries it — type alone, the product's screens, a picture to each step, the client's photographs."""
    if n.get('approach'):
        return str(n['approach'])
    needs = ' '.join(str(x) for x in n.get('needs') or []).lower()
    if n.get('holds_without_pictures'):
        lead = 'type'
    elif _n(n.get('photos_min')) or _n(n.get('photos_large_min')):
        lead = 'photographs'
    elif _n(n.get('step_pictures_min')) or re.search(r'steps[^,]*(?:img|picture)', needs):
        lead = 'step pictures'
    elif _n(n.get('screens_min')) >= 2:
        lead = 'screens'
    else:
        lead = 'one screen'
    return '%s · %s' % (n.get('motif') or 'no motif', lead)


def fits(n, c, d, promised=()):
    """(reasons it cannot be offered, pending, needs met) for one template's needs against one client"""
    why, pending, met = [], [], 0
    tags = [t for words in (n.get('niche') or []) for t in niche_tags(words)]
    if not n.get('niche'):
        why.append('its needs.json names no niche')
    elif not set(tags) & set(c['niche']):
        why.append('niche: it is for %s; the client is %s' % (', '.join(dict.fromkeys(tags)) or 'a niche this step does not know (%s)' % '; '.join(map(str, n['niche']))[:80], ', '.join(c['niche']) or 'of no known niche'))
    p = c['pics']
    counts = {'photos_min': len(p['photos']), 'photos_large_min': len([x for x in p['photos'] if _n(x.get('w')) >= LARGE]),
              'screens_min': len(p['screens']) + (len(p['phones']) if n.get('phones_ok') else 0),
              'step_pictures_min': len([i for i in ((d.get('steps') or {}).get('items') or []) if isinstance(i, dict) and i.get('img')])}
    for k, v in n.items():
        if k.endswith('_min'):
            if k not in counts:
                why.append('a need this step cannot read: %s' % k)
            elif not isinstance(v, int) or isinstance(v, bool):
                why.append('%s is not a number' % k)
            elif counts[k] < v:
                why.append('%s %d, the client has %d' % (k, v, counts[k]))
    if c['pictures'] == 0 and not n.get('holds_without_pictures'):
        why.append('the client has no usable picture and the template does not hold without pictures')
    for need in n.get('needs') or []:
        ok, pend, problem = need_met(need, d, p, promised)
        if problem:
            why.append(problem)
        elif not ok:
            why.append('needs %s' % str(need)[:70])
        else:
            met += 1
            if pend:
                pending.append(str(need))
    return why, pending, met


def select(d, limit=3, promised=(), root=None):
    R = _registry()
    c = client(d)
    ok, rejected = [], []
    for t in R.list_templates(root):
        if not t['selectable']:
            rejected.append({'slug': t['slug'], 'why': t['why']})
            continue
        n = t['needs']
        why, pending, met = fits(n, c, d, promised)
        if why:
            rejected.append({'slug': t['slug'], 'why': '; '.join(why)})
            continue
        tags = [x for words in n['niche'] for x in niche_tags(words)]
        rank = min(c['niche'].index(x) for x in tags if x in c['niche'])
        ok.append({'slug': t['slug'], 'approach': approach(n), 'pending': pending, '_key': (rank, -met, t['slug']),
                   'why': 'niche %s; %d need(s) met%s' % (c['niche'][rank], met, '; waits for ' + ', '.join(pending) if pending else '')})
    ok.sort(key=lambda x: x['_key'])
    chosen, seen = [], set()
    for x in ok:                                                     # first one of each approach, best first
        if len(chosen) < limit and x['approach'] not in seen:
            seen.add(x['approach'])
            chosen.append(x)
    for x in ok:                                                     # then the best of what is left
        if len(chosen) < limit and x not in chosen:
            chosen.append(x)
    for x in ok:
        if x not in chosen:
            rejected.append({'slug': x['slug'], 'why': 'fits, but %d fitting template(s) come before it' % limit})
    for x in chosen:
        x.pop('_key', None)
    return {'niche': c['niche'], 'pictures': c['pictures'], 'chosen': chosen, 'rejected': sorted(rejected, key=lambda r: r['slug'])}


if __name__ == '__main__':                                          # python3 lib/templates/select.py data.json [--promise-made]
    import json
    out = select(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')), promised=('made',) if '--promise-made' in sys.argv else ())
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write('\n')
