#!/usr/bin/env python3
"""normalise_needs.py <needs.json | folder of templates> … [--out DIR] [--json] — a free-worded needs.json in the strict form.

The needs.json files beside the templates were written by many hands in free words ("an app a person downloads or
signs up to", "steps (2-8 items with a picture each)", "menu or spaces"). lib/templates/needs.schema.json is the
strict form: fixed keys, niches from one list, needs and drops from one list of names. This reads a free file and
writes the strict one — and lists, for each file, what it could NOT carry over, because the strict form has no way to
say it (a condition, a size it has no word for) or because the words are not known. An "either/or" becomes `needs_any`,
a count becomes `min` / `max`, a number of photographs at least 1400 px wide becomes `photos_large_min`. Nothing is
guessed into a need: what cannot be mapped goes into `notes`, word for word, and into the list.

    normalise(free: dict) -> (strict: dict, lost: [str])
    --out DIR   write <slug>.needs.json there (never beside the source: the research folder is not ours to write in)
    default     print one row per file: slug, niche, counts, needs, drops, what was lost
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / 'lib' / 'templates' / 'needs.schema.json').read_text(encoding='utf-8'))
NAMES = SCHEMA['definitions']['name']['enum']
NICHES = SCHEMA['properties']['niche']['items']['enum']
KEYS = list(SCHEMA['properties'])

# the telling words of a niche written freely → the fixed word. First match per row; a phrase may name several.
NICHE_WORDS = (
    ('app', r'consumer|an app a person|downloads|signs up|phone screens|\bapps?\b'),
    ('software', r'software|saas|platform|\bapi\b|\btools?\b|fintech|analytics|desktop|web product|\bai\b'),
    ('restaurant', r'restaurant|\bbar\b|caf[eé]|bakery|bistro|food|drink|wine'),
    ('hotel', r'hotel|guest ?house|b&b|lodge|hostel|rooms'),
    ('venue', r'venue|a place with a door'),
    ('clinic', r'clinic|dentist|doctor|medical|health practice'),
    ('law', r'\blaw\b|lawyer|solicitor|legal'),
    ('service', r'service|agency|practice|\bfirm\b|studio|joiner|builder|craft'),
    ('shop', r'\bshop\b|store|catalogue|e-?commerce'),
    ('school', r'school|course|academy|classes'),
    ('person', r'\bperson\b(?! downloads| signs)|athlete|portfolio|guide\b|creator'),
    ('corporate', r'corporate|industrial|trading|logistics|energy'),
    ('nonprofit', r'non-?profit|charity|foundation'),
)
# a need or a drop written freely → the fixed name
ALIASES = {
    'steps.items': 'steps', 'steps.items[].img': 'steps.img', 'steps.items[].k': 'steps.k', 'steps.items[].cta': 'steps.cta', 'steps.items[].text': 'steps',
    'features.items': 'features', 'features.items[].d': 'features.d', 'features.items[].t': 'features', 'links[].d': 'links.d', 'figures[].l': 'figures.l', 'figures[].v': 'figures',
    'plans.items': 'plans', 'plans.items[].rows': 'plans.rows', 'faq.items': 'faq',
    'media.video': 'video', 'media.screens': 'screens', 'media.phones': 'phones', 'media.photos': 'photos', 'media.screens[0]': 'screens',
    'media.made.land': 'made.land', 'media.made.blur': 'made.blur', 'media.made.sky': 'made.sky', 'media.made.sheet': 'made.sheet', 'media.made.field': 'made.field',
    'place.address': 'address', 'place.phone': 'phone', 'place.email': 'email', 'place.hours': 'hours', 'place.booking': 'booking', 'place.since': 'since', 'place.cuisine': 'cuisine',
    'place.price_range': 'price_range', 'place.takeaway': 'takeaway', 'place.social': 'social', 'place.menu': 'menu', 'place.menu.sections': 'menu', 'place.menu.sections[].items': 'menu.items',
    'place.spaces': 'spaces', 'place.spaces[].img': 'spaces.img', 'place.events': 'events', 'place.notices': 'notices', 'team.items': 'team', 'catalogue.groups': 'catalogue',
}
MOTIFS = (('photos', r"client's own photograph|own photographs|photographs of"), ('none', r'^none\b'), ('land', r'\bland\b'), ('sky', r'\bsky\b'), ('sheet', r'\bsheet\b'), ('blur', r'\bblur\b'), ('field', r'\bfield\b'))


def niche_of(words):
    w = str(words or '').lower().strip()
    if w in NICHES:
        return [w]
    return [n for n, rx in NICHE_WORDS if re.search(rx, w)]


def name_of(path):
    """the fixed name of one path of the data, or None"""
    p = str(path or '').strip().strip('`').lower()
    if p in ALIASES:
        return ALIASES[p]
    if p in NAMES:
        return p
    q = re.sub(r'\[\d*\]', '', p)
    return ALIASES.get(q) or (q if q in NAMES else None)


def _outside(text, sep):
    """split at `sep` standing outside brackets"""
    parts, depth, start = [], 0, 0
    for m in re.finditer(r'[()]|' + sep, text):
        if m.group(0) == '(':
            depth += 1
        elif m.group(0) == ')':
            depth = max(0, depth - 1)
        elif depth == 0:
            parts.append(text[start:m.start()].strip())
            start = m.end()
    return [p for p in parts + [text[start:].strip()] if p]


COUNTED = SCHEMA['definitions']['counted']['enum']
NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}


def _bounds(words):
    """(at least, at most) said in the words after a name: "(3 or more …)", "(2-8 items …)", "(3 or 4, each …)", "(3+ items …)",
    "(at least 4: …)", "(3, each with …)"; (None, None) when no number is said"""
    w = words.lower()
    m = re.search(r'(\d+)\s*[-–]\s*(\d+)', w) or re.search(r'\b(\d+) or (\d+)\b', w)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r'(\d+)\s*\+|(\d+) or more|at least (\d+)|\((\d+)[,)]', w)
    if m:
        return int(next(g for g in m.groups() if g)), None
    return None, None


def need_of(entry):
    """What one free entry of `needs` asks for, in the strict form:
    {'names': [...], 'any': [[...]], 'min': {...}, 'max': {...}, 'large': n, 'lost': [...]}"""
    text = str(entry or '').strip()
    out = {'names': [], 'any': [], 'min': {}, 'max': {}, 'large': 0, 'lost': []}
    if not text:
        return out
    m = re.match(r'^(?:at least )?(\d+|one|two|three|four|five|six)\b(?: or more)?\s+(.*)$', text, re.I)
    if m:                                                            # a count of pictures
        n, what = NUM.get(m.group(1).lower()) or int(m.group(1)), m.group(2).lower()
        wide = re.search(r'at least (\d{3,4})\s*(?:px|x)', what)
        if re.match(r'^upright\b', what):
            out['min']['upright'] = n
        elif re.match(r'^(?:product )?pictures?\b', what) and 'in all' in what:
            out['min']['pictures'] = n
        elif re.match(r'^(?:landscape |wide )?photographs?\b', what) and wide and int(wide.group(1)) >= 1400:
            out['large'] = n
            if int(wide.group(1)) > 1400:
                out['lost'].append('a width above 1400 px (%s) — kept as a large photograph, at least 1400: %r' % (wide.group(1), text))
        else:
            out['lost'].append('a count or size of pictures the strict keys cannot say: %r' % text)
        return out
    if not re.match(r'^[`a-z_]', text):
        out['lost'].append('not a name of the fixed list: %r' % text)
        return out
    ways = _outside(text, r'\s+or\s+')
    if len(ways) > 1:                                                # one of: every way must be one plain name
        group = []
        for w in ways:
            sub = need_of(w)
            if len(sub['names']) != 1 or sub['any'] or sub['min'] or sub['max'] or sub['lost']:
                out['lost'].append('an either/or whose ways are not each one plain name: %r' % text)
                return out
            group.append(sub['names'][0])
        out['any'].append(group)
        return out
    for part in _outside(text, r'\s+and\s+|,\s+and\s+'):
        m = re.match(r'^`?([a-z_]+(?:\[\d*\])?(?:\.[a-z_0-9]+(?:\[\d*\])?)*)`?\s*(.*)$', part)
        nm = name_of(m.group(1)) if m else None
        if not nm:
            return {**out, 'names': [], 'lost': ['not a name of the fixed list: %r' % text]}
        rest = m.group(2).strip()
        out['names'].append(nm)
        pictured = re.search(r'picture|\bimg\b|portrait', rest) and re.search(r'each|own|with a picture|with img|with portraits', rest) and nm in ('steps', 'spaces', 'team', 'catalogue')
        if pictured:
            out['names'].append(nm + '.img')
        if re.search(r'\bwith k\b', rest) and nm == 'steps':
            out['names'].append('steps.k')
        lo, hi = _bounds(rest)
        counted = 'steps' if nm == 'steps.img' else nm
        if lo is not None and counted in COUNTED:
            out['min'][counted] = lo
            if hi is not None:
                out['max'][counted] = hi
        elif lo is not None:
            out['lost'].append('a count of something the strict form does not count: %r' % part)
        elif rest and not rest.startswith(('(', '—', '-', ':')) and not pictured and not re.search(r'with k', rest):
            out['lost'].append('a condition in free words: %r' % part)
    out['names'] = list(dict.fromkeys(out['names']))
    return out


def normalise(free):
    lost, notes = [], []
    out = {}
    niche = []
    for w in free.get('niche') or []:
        got = niche_of(w)
        if not got:
            lost.append('niche not in the fixed list: %r' % w)
            notes.append('niche (as written): %s' % w)
        niche += got
    out['niche'] = list(dict.fromkeys(niche))
    for k in ('photos_min', 'photos_large_min', 'screens_min'):
        v = free.get(k)
        out[k] = v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else 0
        if k in free and out[k] != v:
            lost.append('%s is not a count: %r' % (k, v))
    out['phones_ok'] = bool(free.get('phones_ok'))
    needs, any_of, at_least, at_most = [], [], {}, {}
    for e in free.get('needs') or []:
        got = need_of(e)
        needs += got['names']
        any_of += [g for g in got['any'] if g not in any_of]
        for k, v in got['min'].items():
            at_least[k] = max(at_least.get(k, 0), v)
        for k, v in got['max'].items():
            at_most[k] = min(at_most.get(k, v), v)
        out['photos_large_min'] = max(out['photos_large_min'], got['large'])
        lost += ['needs: ' + g for g in got['lost']]
        if got['lost']:
            notes.append('needs (as written): %s' % e)
    if isinstance(free.get('step_pictures_min'), int) and free['step_pictures_min'] > 0:   # a stray key of one file: steps that carry a picture
        at_least['steps.img'] = max(at_least.get('steps.img', 0), free['step_pictures_min'])
    out['needs'] = list(dict.fromkeys(needs))
    if any_of:
        out['needs_any'] = any_of
    if at_least:
        out['min'] = at_least
    if at_most:
        out['max'] = at_most
    out['photos_min'] = max(out['photos_min'], out['photos_large_min'])
    drops = []
    raw = free.get('drops')
    for e in (raw if isinstance(raw, list) else [raw] if raw else []):
        head = re.split(r'\s*[(:—]|\s+-\s+|\s+(?:when|beyond|as|that|on|if|of)\s', str(e).strip(), maxsplit=1)[0]
        parts = [x for x in re.split(r',\s*|\s+and\s+|\s*/\s*', head) if x.strip()]
        got = [name_of(x) or name_of('place.' + x.strip()) for x in parts]
        if parts and all(got):                                       # "media.screens, media.phones, media.video" is three names
            drops += got
            if str(e).strip() != head:
                notes.append('drops (as written): %s' % e)
        else:
            lost.append('drops: not names of the fixed list: %r' % str(e)[:90])
            notes.append('drops (as written): %s' % e)
    if drops or 'drops' in free:
        out['drops'] = list(dict.fromkeys(drops))
    out['holds_without_pictures'] = bool(free.get('holds_without_pictures'))
    motif = next((n for n, rx in MOTIFS if re.search(rx, str(free.get('motif') or '').lower())), None)
    if motif is None:
        lost.append('motif not in the fixed list: %r' % free.get('motif'))
        motif = 'none'
    if str(free.get('motif')) != motif:
        notes.append('motif (as written): %s' % free.get('motif'))
    out['motif'] = motif
    v = free.get('notes')
    notes = ([str(x) for x in v] if isinstance(v, list) else [str(v)] if v else []) + notes
    extra = [k for k in free if k not in KEYS]
    for k in extra:                                                  # measurements and remarks under other keys: kept, as notes
        x = free[k]
        notes.append('%s: %s' % (k, x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)))
    counting = [k for k in extra if k.endswith('_min') and k != 'step_pictures_min']
    lost += ['a count the strict keys do not have: %s = %r' % (k, free[k]) for k in counting]
    if notes:
        out['notes'] = notes
    if not out['niche']:
        lost.append('no niche of the fixed list — the strict file is not valid until one is named')
    return out, lost


def validate(strict):
    """problems of a strict needs dict against needs.schema.json"""
    bad = ['unknown key %r' % k for k in strict if k not in KEYS] + ['no %r' % k for k in SCHEMA['required'] if k not in strict]
    P = SCHEMA['properties']
    for k, v in strict.items():
        s = P.get(k) or {}
        if s.get('type') == 'integer' and not (isinstance(v, int) and not isinstance(v, bool) and v >= 0):
            bad.append('%s: not a count' % k)
        if s.get('type') == 'boolean' and not isinstance(v, bool):
            bad.append('%s: not true/false' % k)
        if 'enum' in s and v not in s['enum']:
            bad.append('%s: %r is not one of the fixed words' % (k, v))
        if s.get('type') == 'array':
            if not isinstance(v, list):
                bad.append('%s: not a list' % k)
                continue
            allowed = NICHES if k == 'niche' else NAMES if k in ('needs', 'drops') else None
            if k == 'needs_any':
                continue
            bad += ['%s: %r is not one of the fixed words' % (k, x) for x in v if (allowed is not None and x not in allowed) or (allowed is None and not isinstance(x, str))]
            if len(v) < s.get('minItems', 0):
                bad.append('%s: empty' % k)
    for g in strict.get('needs_any') or [] if isinstance(strict.get('needs_any'), list) else []:
        if not isinstance(g, list) or len(g) < 2 or any(x not in NAMES for x in g):
            bad.append('needs_any: %r is not two or more of the fixed words' % (g,))
    for k in ('min', 'max'):
        v = strict.get(k)
        if v is None:
            continue
        if not isinstance(v, dict):
            bad.append('%s: not a table of counts' % k)
            continue
        bad += ['%s: %r cannot be counted' % (k, n) for n in v if n not in COUNTED]
        bad += ['%s: %s is not a count' % (k, n) for n, x in v.items() if not (isinstance(x, int) and not isinstance(x, bool) and x >= 1)]
    return bad


def files(args):
    out = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            out += sorted(p.glob('*/needs.json')) or ([p / 'needs.json'] if (p / 'needs.json').is_file() else [])
        else:
            out.append(p)
    return out


def main(argv):
    out_dir, as_json = None, '--json' in argv
    if '--out' in argv:
        i = argv.index('--out')
        out_dir = Path(argv[i + 1])
        del argv[i:i + 2]
    paths = files([a for a in argv if not a.startswith('--')])
    if not paths:
        raise SystemExit(__doc__)
    rows = []
    for p in paths:
        slug = p.parent.name
        try:
            free = json.loads(p.read_text(encoding='utf-8'))
            assert isinstance(free, dict)
        except (ValueError, AssertionError, OSError) as ex:
            rows.append({'slug': slug, 'error': 'not a JSON object: %s' % ex})
            continue
        strict, lost = normalise(free)
        bad = validate(strict)
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / (slug + '.needs.json')).write_text(json.dumps(strict, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        rows.append({'slug': slug, 'strict': strict, 'lost': lost, 'invalid': bad, 'entries': len(free.get('needs') or []) + len(free.get('drops') or []) if isinstance(free.get('drops'), list) else len(free.get('needs') or [])})
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        for r in rows:
            if 'error' in r:
                print('%-12s %s' % (r['slug'], r['error']))
                continue
            s = r['strict']
            print('%-12s niche %-24s photos %d/%d screens %d%s  %s  motif %-6s needs [%s]  drops %d  lost %d%s' % (
                r['slug'], ','.join(s['niche']) or '—', s['photos_min'], s['photos_large_min'], s['screens_min'], '+phones' if s['phones_ok'] else '',
                'holds bare' if s['holds_without_pictures'] else 'needs pictures', s['motif'], ', '.join(s['needs']), len(s.get('drops') or []), len(r['lost']), '  INVALID: ' + '; '.join(r['invalid']) if r['invalid'] else ''))
            for x in r['lost']:
                print('             · ' + x[:200])
        ok = [r for r in rows if 'strict' in r]
        kinds = {}
        for r in ok:
            for x in r['lost']:
                k = x.split(':')[0] + (': ' + x.split(': ')[1].split(' — ')[0].split(':')[0][:28] if x.startswith(('needs', 'drops')) else '')
                kinds[k] = kinds.get(k, 0) + 1
        print('\n%d files · %d carried over whole · %d strict files valid · what was lost, by kind:' % (len(rows), sum(1 for r in ok if not r['lost']), sum(1 for r in ok if not r['invalid'])))
        for k, n in sorted(kinds.items(), key=lambda kv: -kv[1]):
            print('  %3d  %s' % (n, k))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
