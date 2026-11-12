"""pictures.py — `media.made` for a preview, from the picture library prepared in advance. Never a generation at preview
time (owner, 2026-11-12): a preview costs nothing and is instant; fresh pictures for one client only after they pay.

    library(root=None) -> (rows, palettes) | (None, None)      the library: <root>/media/library/{library.json, palettes.json}
    niche_group(d) -> (group name, family order)               which family group a client belongs to, from what it does
    families(d, rows, pals) -> [family …]                      the families it may take, in the niche's order; [] for a no-made kind
    pick_three(d, root=None) -> [made, made, made] | []        three DIFFERENT families for the three previews, in that order
    files(made) -> [media paths]                               the library files a made dict names

Ported from the research folder (tools/library.py and tools/families.json, as they stood at 14:02 on 2026-11-12) so
that the engine and the research builds choose alike; `families.json` beside this file is that file, unchanged.
- The family is chosen by what the client does, not by chance: the group with the most keyword hits in the client's
  `niche` (the reader's subtype), kind, kicker, title, text and statement title — ties to the earlier group; a
  corporate client has its own order; nothing matches → the default order.
- Places, clinics, law, services, shops, schools, people and nonprofits take no made family: they have their own
  photographs, and a generated landscape is not their dining room.
- Within a family, the library palette nearest the client's: same tone (dark | light, from the ground), then the
  smallest "redmean" distance on the ground plus 0.6 × the distance on the accent.
- The contract's fixed slot order: land[0] wide-lead (ridge) · land[1] mid (valley) · land[2] texture (water) ·
  land[3] = land[4] soft · land[5] wide-quiet · sky = glow · field[] · blur[] = tiles · no sheet.
Deterministic; no model; no network. The library is found at $SWARMSITE_LIBRARY (a folder that holds media/library),
else <repo>/media/library … and when there is none, every client gets no made pictures — the templates fall back to
their plain grounds, and those that need made pictures are not offered.
"""
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAM = json.loads((HERE / 'families.json').read_text(encoding='utf-8'))
NO_MADE = set(FAM['no_made']) | {'restaurant', 'hotel', 'shop', 'cafe', 'bar', 'venue', 'place', 'person'}
LAND = ['wide-lead', 'mid', 'texture', 'soft', 'soft', 'wide-quiet']


def _rgb(h):
    h = str(h or '#000000').lstrip('#')
    h = ''.join(c * 2 for c in h) if len(h) == 3 else h
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 0, 0)


def _lum(h):
    r, g, b = _rgb(h)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def _dist(a, b):
    """'redmean' weighted RGB distance"""
    (r1, g1, b1), (r2, g2, b2) = _rgb(a), _rgb(b)
    rm = (r1 + r2) / 2
    return ((2 + rm / 256) * (r1 - r2) ** 2 + 4 * (g1 - g2) ** 2 + (2 + (255 - rm) / 256) * (b1 - b2) ** 2) ** .5


def root_of(root=None):
    env = os.environ.get('SWARMSITE_LIBRARY')
    # SWARMSITE_LIBRARY=none: no library but one given by name (the repo's own copy is not looked for)
    for c in ((root,) if env == 'none' else (root, env, HERE.parent.parent)):
        if c and (Path(c) / 'media' / 'library' / 'library.json').is_file():
            return Path(c)
    return None


def library(root=None):
    r = root_of(root)
    if r is None:
        return None, None
    lib = r / 'media' / 'library'
    try:
        rows = json.loads((lib / 'library.json').read_text(encoding='utf-8'))
        pals = {p['name']: p for p in json.loads((lib / 'palettes.json').read_text(encoding='utf-8'))}
    except (OSError, ValueError, KeyError, TypeError):
        return None, None
    rows = [x for x in rows if isinstance(x, dict) and x.get('family') and x.get('palette') in pals and x.get('src')]
    return rows, pals


def _tone(palette):
    return palette.get('tone') or ('dark' if _lum(palette.get('ground')) < .45 else 'light')


def nearest(palette, family, rows, pals):
    """the library palette of `family` nearest the client's, of the same tone, with its distance; (None, inf) if none"""
    tone, best = _tone(palette), (None, float('inf'))
    for n in sorted({r['palette'] for r in rows if r['family'] == family}):
        p = pals[n]
        if p.get('tone') != tone:
            continue
        dd = _dist(palette.get('ground'), p.get('ground')) + .6 * _dist(palette.get('accent') or palette.get('ground'), p.get('accent'))
        if dd < best[1]:
            best = (n, dd)
    return best


def niche_group(d):
    """which family group a client belongs to, from what it says it does; (group name, family order)"""
    kind = str(d.get('kind') or '').lower()
    if kind == 'corporate':
        return 'corporate', FAM['corporate']
    h = d.get('hero') or {}
    text = ' '.join(str(x) for x in (d.get('niche'), d.get('subtype'), kind, h.get('kicker'), h.get('title'), h.get('text'), (d.get('statement') or {}).get('title')) if x).lower()
    words = re.findall(r'[a-z0-9]+', text)
    best = None
    for i, g in enumerate(FAM['groups']):
        n = sum(words.count(w) for w in g['words'])
        if n and (best is None or n > best[0]):
            best = (n, i)
    if best:
        g = FAM['groups'][best[1]]
        return g['name'], g['families']
    return 'default', FAM['default']


def families(d, rows, pals):
    if str(d.get('kind') or '').lower() in NO_MADE:                 # by what the client is: a corporate client with an address still takes made pictures
        return []
    pal = d.get('palette') or {}
    if not pal.get('ground'):
        return []
    return [f for f in niche_group(d)[1] if nearest(pal, f, rows, pals)[0]]


def _entry(r, name):
    return {'src': r['src'], 'w': r.get('w'), 'h': r.get('h'), 'tone': r.get('tone'), 'mean': r.get('mean'), 'name': name}


def build(family, lib_palette, rows):
    got = {}
    for r in rows:
        if r['family'] == family and r['palette'] == lib_palette:
            got.setdefault(r.get('slot'), []).append(r)
    for v in got.values():
        v.sort(key=lambda r: r['src'])
    out = {'family': family, 'palette': lib_palette}
    land = [_entry(got[s][0], s) for s in LAND if s in got]
    if land:
        out['land'] = land
    blur = [dict(_entry(r, 'tile-%d' % (i + 1)), hue=r.get('mean')) for i, r in enumerate(got.get('tile', []))]
    if blur:
        out['blur'] = blur
    field = [_entry(r, 'field-%d' % (i + 1)) for i, r in enumerate(got.get('field', []))]
    if field:
        out['field'] = field
    if 'glow' in got:
        out['sky'] = _entry(got['glow'][0], 'glow')
    return out


def pick_three(d, root=None, rows=None, pals=None):
    """three made dicts of three different families, in the niche's order; fewer families than three → the order
    repeats; a no-made kind, or no library → []"""
    if rows is None:
        rows, pals = library(root)
    if not rows:
        return []
    fams = families(d, rows, pals)
    out = [build(f, nearest(d['palette'], f, rows, pals)[0], rows) for f in fams[:3]]
    while out and len(out) < 3:
        out.append(out[len(out) % len(fams)])
    return out


def files(made):
    """every library path a made dict names"""
    out = []
    for k, v in (made or {}).items():
        for x in (v if isinstance(v, list) else [v] if isinstance(v, dict) else []):
            if isinstance(x, dict) and isinstance(x.get('src'), str):
                out.append(x['src'])
    return list(dict.fromkeys(out))


if __name__ == '__main__':                                        # python3 lib/templates/pictures.py data.json
    import sys
    d = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    print('group:', niche_group(d)[0])
    print([(m.get('family'), m.get('palette')) for m in pick_three(d)])
