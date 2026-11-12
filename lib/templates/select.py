"""select.py — for one client's data, the three templates to show it in.

    select(d, limit=3, promised=(), root=None) -> {
        'niche': [...],                 what the client is, most telling first
        'pictures': n,                  the client's own usable pictures (screens, phones, photographs, a film)
        'chosen':   [{'slug', 'approach', 'why', 'pending', 'drops', 'missing', 'niche', 'fallback'}],   in the order to show them
        'reserve':  [the same, in order: what the job takes next when a chosen one fails the gate]
        'fallback': True when a template of a neighbouring niche had to be taken to fill the three
        'rejected': [{'slug', 'why'}],                          every template not chosen, with the reason (reserve included)
    }
    without(d, drops) -> the data with those soft sections taken out (what a variant that misses them is rendered from)

Deterministic: the same data and the same library give the same three, in the same order. No model call.

Every visitor is shown three designs of their niche (owner's product rule, 2026-11-12). So a need is one of two kinds:
  · hard — the page cannot exist without it: the hero, a brand name, a place's address or phone, a shop's catalogue,
    a picture at all when it does not hold without one, and the photographs of a template whose needs.json names
    `photos` in `hard` (stress.py --sweep found it breaks with fewer, see PHOTOS below);
  · soft — a section the template drops whole when the client has none of it: SOFT below (features, close, steps and
    their pictures, plans, links, faq, statement, figures, trust, quotes, logos, product screens, made pictures).
    A template's needs.json may name in `hard` a soft one its page makes no sense without.
A template is a candidate when it has a needs.json (a template without one has not been measured: it is NOT
selectable), one of its niches is the client's and every hard need is met. The three are filled in this order, and
within each tier so that they differ in approach where the library allows: the candidates that meet every need; then
those that miss only soft needs — fewest missed first — rendered with those sections dropped (`drops`; nothing is
made up to fill one); then, only when still fewer than three, the same from the nearest niche group (NEAR), marked
`fallback`. Fewer photographs than a template was measured with (photos_min, photos_large_min) is a soft miss too,
ranked by how far short the client is; the gate in job.py decides whether each page is shown.
lib/templates/stress.py --sweep proves each template holds with each soft section absent.

What a needs.json may say (the vocabulary this file reads — a need it cannot read keeps the template out, with the
reason, rather than being waved through):
  niche: [..]                    one of the fixed words of needs.schema.json (software, app, restaurant, hotel, clinic,
                                 law, service, shop, school, person, corporate, nonprofit) — then exactly that — or
                                 free words, read by the telling words in NICHES below
  photos_min, photos_large_min   photographs in media.photos; large = at least 1400 px wide
  needs_any: [[a, b], …]         one of: each inner list is met by any one of its names
  min / max: {name: n}           how many: steps, steps.img, features, plans, faq, figures, links, photos, photos.large,
                                 screens, phones, pictures (all three), upright, spaces, menu, team, catalogue, projects …
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
LARGE = 1400                                                    # a large photograph: at least this wide (owner, 2026-11-12)
# soft: blocks of the data a template drops whole when the client has none of them (the name's first part decides:
# steps.img, close.title, media.made.land are soft). Everything else a needs.json names is hard.
SOFT = ('features', 'close', 'steps', 'plans', 'links', 'faq', 'statement', 'figures', 'trust', 'quotes', 'logos', 'screens', 'phones', 'video', 'made')
# a soft need that is one part of every item: missed, that part is taken off every item and the block stays
PARTS = {'steps.img': ('steps', 'img'), 'steps.k': ('steps', 'k'), 'steps.cta': ('steps', 'cta'), 'features.d': ('features', 'd'),
         'links.d': ('links', 'd'), 'figures.l': ('figures', 'l'), 'plans.rows': ('plans', 'rows')}
# PHOTOS. photos_min and photos_large_min are the counts a template was measured with, not what it cannot hold without
# (owner's coordinator, 2026-11-12: sunbeam asks for 15 and tengile for 11, and both pass the gate with none). Fewer is a
# soft miss, ranked by how far short (the share of the stated count missing). A template the sweep finds broken with
# fewer photographs names `photos` in `hard`; a client with no usable picture at all still gets only templates that
# say holds_without_pictures.
# the nearest niche group of each niche: where the three are filled from when the client's own niche has fewer
# (owner, 2026-11-12; school is not in his list and goes with service and nonprofit, the two it shares templates with)
NEAR = {'software': ['app'], 'app': ['software'], 'saas': ['software', 'app'],
        'clinic': ['service', 'law'], 'law': ['service', 'clinic'], 'service': ['clinic', 'law', 'corporate', 'person', 'nonprofit', 'shop', 'school'],
        'restaurant': ['hotel', 'venue'], 'hotel': ['restaurant', 'venue'], 'venue': ['restaurant', 'hotel'], 'place': ['restaurant', 'hotel', 'venue'],
        'corporate': ['service'], 'person': ['service'], 'nonprofit': ['service', 'school'], 'shop': ['service'], 'school': ['service', 'nonprofit']}

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
FIXED = ('software', 'app', 'restaurant', 'hotel', 'clinic', 'law', 'service', 'shop', 'school', 'person', 'corporate', 'nonprofit', 'venue')


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


def empty(d):
    """Why the data holds no page at all, or ''. A page needs a title to open with and one thing more to lay out — a
    line under the title, a section, a picture or a way to reach the business; a capture that yields less than that is
    a capture that failed, and it is the one case where no design is shown."""
    h = d.get('hero') if isinstance(d.get('hero'), dict) else {}
    if not _has(h.get('title')):
        return 'no hero title: the page has nothing to open with'
    more = [h.get('text'), h.get('text2'), h.get('kicker')] + [d.get(k) for k in SOFT if k not in ('screens', 'phones', 'video', 'made')] + \
           [d.get(k) for k in ('place', 'contact', 'team', 'catalogue', 'projects', 'locations', 'credentials')] + [x for v in _pics(d).values() for x in v]
    return '' if any(_has(x) for x in more) else 'the capture holds a title and nothing else: nothing to lay out'


def client(d):
    """what the client is and has: niches (most telling first) and its own usable pictures"""
    p = _pics(d)
    kind = str(d.get('kind') or '').lower()
    if kind in ('restaurant', 'cafe', 'bar'):
        niche = ['restaurant', 'place']
    elif kind in ('hotel', 'venue'):
        niche = [kind, 'place']
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


def _path(name):
    m = re.match(r'^([a-z_][a-z_.\[\]0-9]*)', str(name or '').strip())
    return m.group(1) if m else ''


def _root(name):
    """the block a need, a count or a part names: 'steps.items[].img (…)' → steps, 'media.made.land' → made;
    '8 or more product pictures' → pictures"""
    if re.match(r'^\d', str(name or '').strip()):
        return 'pictures'
    path = _path(name)
    parts = [re.sub(r'\[\d*\]$', '', x) for x in STRICT.get(path, path).split('.') if x]
    if parts[:1] == ['media']:
        parts = parts[1:]
    return parts[0] if parts else ''


def _strict(name):
    """the strict name of a part of every item ('steps.items[].img (…)' → 'steps.img'), else the name's root"""
    path = _path(name)
    for k, v in STRICT.items():
        if path in (k, v):
            return k
    return _root(name)


def is_soft(name, n=None):
    """Can the template drop its section when this need is missed? Soft by SOFT, unless its needs.json names the
    need (or its block) in `hard`."""
    hard = {str(x) for x in (n or {}).get('hard') or []}
    return _root(name) in SOFT and not ({_root(name), _strict(name), str(name)} & hard)


def _drop_of(name):
    """what is taken out of the data for a missed soft need: a part of every item ('steps.img') or a whole block
    ('features'); '' for pictures the client does not have (there is nothing to take out)"""
    st = _strict(name)
    if st in PARTS:
        return st
    r = _root(name)
    return '' if r in ('screens', 'phones', 'video', 'made') else r


def without(d, drops):
    """The data with the soft sections of `drops` taken out — whole blocks, or one part of every item — the way the
    adapter leaves a section it could not read: the key is not there. The input is not changed."""
    import copy
    if not drops:
        return d
    out = copy.deepcopy(d)
    for name in drops:
        if name in PARTS:
            block, key = PARTS[name]
            v = out.get(block)
            items = v.get('items') if isinstance(v, dict) else v if isinstance(v, list) else None
            for it in items or []:
                if isinstance(it, dict):
                    it.pop(key, None)
        elif name in SOFT:
            out.pop(name, None)
    return out


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


def count(name, d, pics):
    """how many of a countable thing the data holds; None for a name that cannot be counted"""
    name = str(name)
    every = pics['screens'] + pics['phones'] + pics['photos']
    if name == 'pictures':
        return len(every)
    if name == 'upright':
        return len([x for x in every if _n(x.get('w')) and _n(x.get('h')) > _n(x.get('w'))])
    if name == 'photos.large':
        return len([x for x in pics['photos'] if _n(x.get('w')) >= LARGE])
    if name in ('screens', 'phones', 'photos'):
        return len(pics[name])
    if name == 'steps.img':
        return len([v for v in _get(d, 'steps.items[].img') if v])
    if name == 'menu':
        return len([v for v in _get(d, 'place.menu.sections[]') if v])
    if name == 'catalogue':
        return len([v for v in _get(d, 'catalogue.groups[].items[]') if v])
    if name == 'team':
        return len([v for v in _get(d, 'team.items[]') + _get(d, 'team.groups[].items[]') if v])
    if name in ('steps', 'features', 'plans', 'faq'):
        return len([v for v in _get(d, name + '.items[]') if v])
    if name == 'spaces':
        return len([v for v in _get(d, 'place.spaces[]') if v])
    if name in ('figures', 'links', 'trust', 'quotes', 'logos', 'projects', 'locations', 'credentials'):
        return len([v for v in _get(d, name + '[]') if v])
    return None


def assess(n, c, d, promised=()):
    """one template's needs against one client: {'niche': reason or '', 'hard': [reasons], 'soft': [{'why', 'drop'}],
    'pending': [...], 'met': n}. A need that cannot be read is hard: it keeps the template out, with the reason."""
    hard, soft, pending, met = [], [], [], 0
    photos_hard = 'photos' in {str(x) for x in n.get('hard') or []}

    def miss(name, why):
        if _root(name) == 'photos' and not photos_hard:              # a count of photographs, as photos_min below
            soft.append({'why': why, 'drop': ''})
        elif is_soft(name, n):
            soft.append({'why': why, 'drop': _drop_of(name)})
        else:
            hard.append(why)
    niche = ''
    tags = [t for words in (n.get('niche') or []) for t in niche_tags(words)]
    if not n.get('niche'):
        hard.append('its needs.json names no niche')
    elif not set(tags) & set(c['niche']):
        niche = 'niche: it is for %s; the client is %s' % (', '.join(dict.fromkeys(tags)) or 'a niche this step does not know (%s)' % '; '.join(map(str, n['niche']))[:80], ', '.join(c['niche']) or 'of no known niche')
    p = c['pics']
    counts = {'photos_min': len(p['photos']), 'photos_large_min': len([x for x in p['photos'] if _n(x.get('w')) >= LARGE]),
              'screens_min': len(p['screens']) + (len(p['phones']) if n.get('phones_ok') else 0),
              'step_pictures_min': len([i for i in ((d.get('steps') or {}).get('items') or []) if isinstance(i, dict) and i.get('img')])}
    as_need = {'photos_min': 'photos', 'photos_large_min': 'photos', 'screens_min': 'screens', 'step_pictures_min': 'steps.img'}
    for k, v in n.items():
        if k.endswith('_min'):
            if k not in counts:
                hard.append('a need this step cannot read: %s' % k)
            elif not isinstance(v, int) or isinstance(v, bool):
                hard.append('%s is not a number' % k)
            elif counts[k] < v and k in ('photos_min', 'photos_large_min'):
                why = '%s %d, the client has %d' % (k, v, counts[k])
                if not photos_hard:
                    soft.append({'why': why, 'drop': '', 'short': (v - counts[k]) / v})   # the template leaves out the slots it cannot fill
                else:
                    hard.append(why)
            elif counts[k] < v:
                miss(as_need[k], '%s %d, the client has %d' % (k, v, counts[k]))
    if empty(d):                                                     # hard for every template: there is no page to make
        hard.append(empty(d))
    if c['pictures'] == 0 and not n.get('holds_without_pictures'):
        hard.append('the client has no usable picture and the template does not hold without pictures')
    for need in n.get('needs') or []:
        ok, pend, problem = need_met(need, d, p, promised)
        if problem:
            hard.append(problem)
        elif not ok:
            miss(need, 'needs %s' % str(need)[:70])
        else:
            met += 1
            if pend:
                pending.append(str(need))
    for group in n.get('needs_any') or []:                           # one of
        if not isinstance(group, list) or not group:
            hard.append('a need this step cannot read: needs_any %r' % (group,))
            continue
        got = [need_met(x, d, p, promised) for x in group]
        if any(g[2] for g in got):
            hard.append('a need this step cannot read: needs_any %s' % ' or '.join(map(str, group))[:70])
        elif not any(g[0] for g in got):
            why = 'needs one of %s' % ', '.join(map(str, group))[:70]
            if any(is_soft(x, n) for x in group):                    # a slot a soft section may fill is a slot the page can drop
                soft.append({'why': why, 'drop': ''})
                soft.extend({'why': '', 'drop': _drop_of(x)} for x in group if is_soft(x, n))
            else:
                hard.append(why)
        else:
            met += 1
            if not any(g[0] and not g[1] for g in got):
                pending.append(' or '.join(map(str, group)))
    for key, beyond in (('min', lambda have, want: have < want), ('max', lambda have, want: have > want)):
        limits = n.get(key) or {}
        if not isinstance(limits, dict):
            hard.append('a need this step cannot read: %s' % key)
            continue
        for name, want in limits.items():
            have = count(name, d, p)
            if have is None or not isinstance(want, int) or isinstance(want, bool):
                hard.append('a need this step cannot read: %s %s = %r' % (key, name, want))
            elif beyond(have, want):
                miss(name, '%s %s %d, the client has %d' % ('at least' if key == 'min' else 'at most', name, want, have))
    return {'niche': niche, 'hard': hard, 'soft': soft, 'pending': pending, 'met': met}


def fits(n, c, d, promised=()):
    """(every reason it does not fit as the data stands — niche, hard and soft —, pending, needs met): the strict
    reading, for a caller that asks whether nothing at all would be dropped"""
    a = assess(n, c, d, promised)
    return [x for x in [a['niche']] + a['hard'] + [m['why'] for m in a['soft']] if x], a['pending'], a['met']


def _near(niche):
    """the neighbouring niches of a client's, nearest first, none of its own; a client of no known niche is offered
    the service templates, the library's most general"""
    if not niche:
        return ['service']
    out = []
    for x in niche:
        out += [y for y in NEAR.get(x, []) if y not in niche and y not in out]
    return out


def lead(n, c, rank):
    """how squarely a template is made for this client, by the FIRST niche of its needs.json (the one it was made
    for; the later ones are where it also holds): 0 — its first niche is the client's niche; 1 — its first niche is
    of the client's kind all the same (another of the client's niches, or another kind of place for a place); 2 — the
    client's niche is only listed later. A clinic page that also holds for a hotel comes after a hotel page."""
    first = set(niche_tags((n.get('niche') or [''])[0]))
    if c['niche'][rank] in first:
        return 0
    kin = set(c['niche']) | (PLACE_KINDS if 'place' in c['niche'] else set())
    return 1 if first & kin else 2


def select(d, limit=3, promised=(), root=None):
    R = _registry()
    c = client(d)
    near = _near(c['niche'])
    cands, rejected = [], []
    for t in R.list_templates(root):
        if not t['selectable']:
            rejected.append({'slug': t['slug'], 'why': t['why']})
            continue
        n = t['needs']
        a = assess(n, c, d, promised)
        tags = [x for words in n['niche'] for x in niche_tags(words)]
        own = [x for x in tags if x in c['niche']]
        close = [x for x in tags if x in near]
        if a['hard'] or not (own or close):
            rejected.append({'slug': t['slug'], 'why': '; '.join(x for x in [a['niche']] + a['hard'] + [m['why'] for m in a['soft']] if x)})
            continue
        fallback = not own
        rank = min(c['niche'].index(x) for x in own) if own else min(near.index(x) for x in close)
        niche = c['niche'][rank] if own else near[rank]
        drops = list(dict.fromkeys(m['drop'] for m in a['soft'] if m['drop']))
        missing = [m['why'] for m in a['soft'] if m['why']]
        tier = 2 * fallback + (1 if missing else 0)
        ld = lead(n, c, rank) if own else 0                          # made for the client's niche before one that also holds
        why = '%sniche %s; %d need(s) met%s%s' % ("not the client's niche, the nearest: " if fallback else '', niche, a['met'],
                                              '; shown without what it misses: ' + ', '.join(missing) if missing else '',
                                              '; waits for ' + ', '.join(a['pending']) if a['pending'] else '')
        cands.append({'slug': t['slug'], 'approach': approach(n), 'pending': a['pending'], 'drops': drops, 'missing': missing, 'niche': niche,
                      'fallback': fallback, 'why': why, '_tier': tier, '_key': (tier, rank, ld, len(missing), round(sum(m.get('short', 0) for m in a['soft']), 3), -a['met'], t['slug'])})
    cands.sort(key=lambda x: x['_key'])
    order, seen = [], set()
    for tier in range(4):                                            # tier by tier; within one, one of each approach first
        here = [x for x in cands if x['_tier'] == tier]
        firsts = []
        for x in here:
            if x['approach'] not in seen:
                seen.add(x['approach'])
                firsts.append(x)
        order += firsts + [x for x in here if x not in firsts]
    chosen, reserve = order[:limit], order[limit:]
    for x in chosen + reserve:
        x.pop('_key', None)
        x.pop('_tier', None)
    for x in reserve:
        rejected.append({'slug': x['slug'], 'why': 'fits%s, but %d template(s) come before it' % (' without ' + ', '.join(x['missing']) if x['missing'] else '', limit)})
    return {'niche': c['niche'], 'pictures': c['pictures'], 'chosen': chosen, 'reserve': reserve, 'fallback': any(x['fallback'] for x in chosen),
            'rejected': sorted(rejected, key=lambda r: r['slug'])}


if __name__ == '__main__':                                          # python3 lib/templates/select.py data.json [--promise-made]
    import json
    out = select(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')), promised=('made',) if '--promise-made' in sys.argv else ())
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write('\n')
