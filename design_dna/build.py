#!/usr/bin/env python3
"""build.py — the Design DNA library, generated from the blueprint files. No network, no model.

Reads   lib/blueprints/<id>.bp.json      the normalised blueprint the renderer uses
        lib/blueprints/raw/<id>.json     the capture it was normalised from (absent for an authored blueprint)
        design_dna/evidence.json         hand-written: screenshot folders and known caveats, each with the files that show it
        lib/render/render_bp.py          font_for, the face that ships for a source face (imported, never copied)
        lib/typography/fonts.json        licence notes
Writes  design_dna/references/<id>.json  one record per blueprint; the shape is design_dna/schema.json
        design_dna/README.md             only the tables between the GENERATED markers

Usage   python3 design_dna/build.py            write
        python3 design_dna/build.py --check    exit 1 when a file on disk differs from what would be written

The one rule: a value in a record is copied or computed from a named field of the blueprint or of the raw capture and
says where from, or it is null. Nothing is written from knowledge of the original website.

How that is kept:
- lib/blueprint/normalize.py fills gaps with defaults (weight 400, leading 1.05/1.1, align start, x 0, gutter 40, a
  viewport 1440 wide, h2 = display). A blueprint value whose raw field is absent is written as null here and named in
  `not_recorded`. For a blueprint with no raw file nothing can be told apart, so the whole record is `authored`.
- `role` and `note` are hand annotations in the raw file (lib/blueprint/extract.js emits neither). Roles are carried as
  labels; notes are carried only as {"kind": "prose", "source": <pointer>} and are withheld when they quote source text.
- Tracking is computed from the raw letter-spacing and font size: the blueprint rounds letter-spacing to whole pixels first.
- Fractions (head.x, head.wf, media.wf, media.xf) are the blueprint's own: pixels over the viewport width. Only three
  captures record that width; for the others normalize.py assumes 1440 and `composition.fraction_base` says so.
- Heading and button text in the raw files is third-party source text and is never read into a record.
- Principles, needs and temper tags come from the rules at the bottom of this file. A rule fires only on values that
  are present in the record, and its statement names its threshold.

Same input, same bytes: keys are sorted, floats are rounded to a fixed number of places, nothing depends on time or
on dictionary order.
"""
import hashlib, importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BP_DIR = 'lib/blueprints'
RAW_DIR = 'lib/blueprints/raw'
OUT_DIR = 'design_dna/references'
EVIDENCE = 'design_dna/evidence.json'
README = 'design_dna/README.md'
FONTS = 'lib/typography/fonts.json'
RECIPES = 'lib/templates/recipes.py'
RENDERER = 'lib/render/render_bp.py'
NORMALIZER = 'lib/blueprint/normalize.py'
SCHEMA_VERSION = 1
ASSUMED_VW = 1440          # normalize.py: W = raw.get('vw', 1440)
LEVELS = ('display', 'h2', 'h3', 'body', 'label')
NOTE_QUOTE_MIN = 12        # a note that quotes this many characters of a source heading, button or label is withheld
# captured_at, dpr and mobile are written as null / "missing" because no capture holds them. If one ever does, the
# build stops instead of going on saying so.
UNREAD_CAPTURE_FIELDS = ('dpr', 'devicePixelRatio', 'date', 'captured_at', 'capturedAt', 'capture_date', 'mobile', 'viewports')

# Thresholds. Every one is repeated in the statement of the rule that uses it.
T = {
    'scale_high': 7.0, 'scale_low': 3.0,            # largest heading px ÷ body px
    'weight_light': 300, 'weight_heavy': 700,       # CSS font-weight of the largest heading
    'tracking_tight': -0.02,                        # em
    'leading_tight': 0.95,                          # line-height ÷ font-size
    'offset_x': 0.30, 'offset_share': 0.25, 'offset_min': 2,
    'bleed_wf': 0.98, 'bleed_share': 0.30,
    'large_wf': 0.20,                               # a "large" medium is at least this share of the viewport width
    'portrait_ar': 0.9, 'landscape_ar': 1.2, 'orientation_share': 0.6, 'orientation_min': 3,
    'still_ar_min': 0.4, 'still_ar_max': 2.5,       # outside this a still is a strip or a wordmark, not a picture
    'image_led': 0.6, 'type_led': 0.25,
    'dark_lum': 0.3,                                # the same cut normalize.py uses for colour.mode
    'long_screens': 15.0, 'short_screens': 6.0,
}


class BuildError(Exception):
    pass


# ── files and pointers ───────────────────────────────────────────────────────────────────────────────────────────────
def P(rel_path, root=None):
    return os.path.join(root or ROOT, rel_path)


def read_json(rel_path, root=None):
    with open(P(rel_path, root), encoding='utf-8') as f:
        return json.load(f)


def sha256_file(rel_path, root=None):
    with open(P(rel_path, root), 'rb') as f:
        return 'sha256:' + hashlib.sha256(f.read()).hexdigest()


def sha256_json(value):
    return 'sha256:' + hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def ptr(path, *tokens):
    """A file pointer: repo-relative path + '#' + RFC 6901 JSON pointer."""
    return path + '#' + ''.join('/' + str(t).replace('~', '~0').replace('/', '~1') for t in tokens)


def resolve_file_pointer(ref, root=None):
    """'path#/a/0/b' → the value. Raises KeyError when the file or the pointer does not resolve."""
    path, _, frag = ref.partition('#')
    if not os.path.isfile(P(path, root)): raise KeyError('no such file: ' + path)
    cur = read_json(path, root)
    if frag in ('', '/'): return cur
    if not frag.startswith('/'): raise KeyError('not a JSON pointer: ' + ref)
    for tok in frag[1:].split('/'):
        tok = tok.replace('~1', '/').replace('~0', '~')
        if isinstance(cur, list):
            if not tok.isdigit() or int(tok) >= len(cur): raise KeyError('pointer does not resolve: ' + ref)
            cur = cur[int(tok)]
        elif isinstance(cur, dict):
            if tok not in cur: raise KeyError('pointer does not resolve: ' + ref)
            cur = cur[tok]
        else:
            raise KeyError('pointer does not resolve: ' + ref)
    return cur


_STEP = re.compile(r'([A-Za-z0-9_\-]+)|\[(\d+)\]')


def resolve_internal(record, pointer):
    """'composition.sections[2].media[0].ar' → the value inside the record. Raises KeyError when it does not resolve."""
    cur = record; pos = 0
    if not isinstance(pointer, str) or not pointer: raise KeyError('empty pointer')
    while pos < len(pointer):
        if pointer[pos] == '.': pos += 1; continue
        m = _STEP.match(pointer, pos)
        if not m: raise KeyError('bad pointer: ' + pointer)
        key, idx = m.group(1), m.group(2)
        if key is not None:
            if not isinstance(cur, dict) or key not in cur: raise KeyError('pointer does not resolve: ' + pointer)
            cur = cur[key]
        else:
            if not isinstance(cur, list) or int(idx) >= len(cur): raise KeyError('pointer does not resolve: ' + pointer)
            cur = cur[int(idx)]
        pos = m.end()
    return cur


def load_module(name, rel_path, root=None):
    spec = importlib.util.spec_from_file_location(name, P(rel_path, root))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


_cache = {}


def renderer_font_for():
    """font_for from the renderer itself, so the mapping can never be a second copy."""
    if 'font_for' not in _cache:
        _cache['font_for'] = load_module('design_dna_render_bp', RENDERER).font_for
    return _cache['font_for']


def delivery(face):
    """What ships for a source face: (face, class, is_generic_fallback), straight from font_for."""
    font_for = renderer_font_for()
    name, cls = font_for(face)
    missed = font_for(face, fallback=('\x00', '\x00'))[0] == '\x00'
    return name, cls, missed


def recipe_ids():
    if 'recipes' not in _cache:
        _cache['recipes'] = sorted(load_module('design_dna_recipes', RECIPES).RECIPES)
    return _cache['recipes']


def blueprint_ids(root=None):
    return sorted(f[:-len('.bp.json')] for f in os.listdir(P(BP_DIR, root)) if f.endswith('.bp.json'))


def raw_source_texts(raw):
    """Every heading, button and label text (and the page title) in one raw capture: third-party source text."""
    out = []
    if isinstance(raw.get('title'), str): out.append(raw['title'])
    for h in raw.get('unassignedHeadings') or []:
        if isinstance(h, dict) and isinstance(h.get('text'), str): out.append(h['text'])
    for s in raw.get('sections') or []:
        for key in ('heads', 'btns', 'labels'):
            for item in s.get(key) or []:
                if isinstance(item, dict) and isinstance(item.get('text'), str): out.append(item['text'])
    return [t for t in out if t.strip()]


def all_source_texts(root=None):
    out = []
    for name in sorted(os.listdir(P(RAW_DIR, root))):
        if name.endswith('.json'): out += raw_source_texts(read_json(RAW_DIR + '/' + name, root))
    return out


# ── small numeric helpers ────────────────────────────────────────────────────────────────────────────────────────────
def lum(hex_colour):
    h = hex_colour.lstrip('#'); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def num(x):
    """A number the way a statement prints it: 15.0 → '15', 0.375 → '0.38'."""
    s = ('%.2f' % x).rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


def pct(x):
    """A share the way a statement prints it: 0.3 → '30%'."""
    return num(x * 100) + '%'


def weight_of(el):
    tok = str(el.get('w', '')).split()
    return int(tok[0]) if tok and tok[0].isdigit() else None


def tracking_em(ls, px):
    """Raw letter-spacing ('-2.4px', '-2%', 'normal') → em. None when absent or unreadable."""
    if ls is None or not px: return None
    s = str(ls).strip()
    try:
        if s == 'normal': return 0.0
        if s.endswith('%'): return round(float(s[:-1]) / 100, 4)
        if s.endswith('em'): return round(float(s[:-2]), 4)
        return round(float(s.replace('px', '')) / px, 4)
    except ValueError:
        return None


def leading_of(el):
    v = el.get('lh')
    if v is None or str(v) == 'NaN': return None
    try: return float(v)
    except ValueError: return None


def computed(value, how, evidence, matched=None, **extra):
    out = {'value': value, 'how': how, 'evidence': evidence}
    if matched is not None: out['matched'] = matched
    out.update(extra)
    return out


def share(count, of):
    return round(count / of, 2) if of else None


# ── typography ───────────────────────────────────────────────────────────────────────────────────────────────────────
def locate_type(raw):
    """Which raw element each blueprint type level was taken from: the selection normalize.type_roles makes, kept as
    (list name, section index, element index, element). The result is checked against the blueprint by the caller."""
    secs = raw['sections']
    def every(key):
        return [(key, si, ei, el) for si, s in enumerate(secs) for ei, el in enumerate(s.get(key, [])) if el.get('px')]
    heads = sorted(every('heads'), key=lambda t: -t[3]['px'])
    paras = sorted(every('paras'), key=lambda t: -t[3].get('words', 0))
    labels = every('labels')
    out = dict.fromkeys(LEVELS)
    if heads: out['display'] = heads[0]
    dpx = heads[0][3]['px'] if heads else 999
    h2s = [t for t in heads if 28 <= t[3]['px'] < dpx]
    if h2s: out['h2'] = h2s[0]
    h2px = h2s[0][3]['px'] if h2s else (dpx if heads else 40)
    h3s = [t for t in heads if 16 <= t[3]['px'] < h2px]
    if h3s: out['h3'] = h3s[0]
    if paras: out['body'] = paras[0]
    small = [t for t in heads if t[3]['px'] <= 16 and t[3].get('tt') == 'uppercase']
    if labels: out['label'] = labels[0]
    elif small: out['label'] = small[0]
    return out


def face_fields(face):
    name, cls, missed = delivery(face)
    return {'source_face': face, 'delivery_face': name, 'delivery_class': cls, 'delivery_fallback': missed}


def type_level_measured(ref, level, bp_level, located, bp_path, raw_path):
    key, si, ei, el = located
    if el.get('px') != bp_level.get('px') or el.get('fam') != bp_level.get('fam'):
        raise BuildError('%s: %s#/type/%s is not what %s takes from the capture (%s px %s); re-run the normaliser or '
                         'record this reference as authored' % (ref, bp_path, level, NORMALIZER, el.get('px'), el.get('fam')))
    out = face_fields(el.get('fam'))
    out.update({'px': el['px'], 'weight': weight_of(el), 'tracking': tracking_em(el.get('ls'), el['px']),
                'leading': leading_of(el), 'case': el.get('tt')})
    out['not_recorded'] = sorted(k for k in ('weight', 'tracking', 'leading', 'case') if out[k] is None)
    out['source'] = {'blueprint': ptr(bp_path, 'type', level), 'raw': ptr(raw_path, 'sections', si, key, ei)}
    return out


def type_level_authored(level, bp_level, bp_path):
    out = face_fields(bp_level.get('fam'))
    out.update({'px': bp_level.get('px'), 'weight': bp_level.get('w'), 'tracking': bp_level.get('ls'),
                'leading': bp_level.get('lh'), 'case': bp_level.get('tt')})
    out['not_recorded'] = sorted(k for k in ('weight', 'tracking', 'leading', 'case') if out[k] is None)
    out['source'] = {'blueprint': ptr(bp_path, 'type', level), 'raw': None}
    return out


def build_typography(ref, bp, raw, bp_path, raw_path):
    typ = {'basis': 'measured' if raw else 'authored', 'levels_missing': {}}
    located = locate_type(raw) if raw else {}
    for level in LEVELS:
        bp_level = (bp.get('type') or {}).get(level)
        if not raw:
            typ[level] = type_level_authored(level, bp_level, bp_path) if bp_level else None
            if not bp_level: typ['levels_missing'][level] = 'not-in-blueprint'
        elif located.get(level) and bp_level:
            typ[level] = type_level_measured(ref, level, bp_level, located[level], bp_path, raw_path)
        elif bp_level and level == 'h2' and bp_level == bp['type'].get('display'):
            typ[level] = None; typ['levels_missing'][level] = 'blueprint-copies-display'   # normalize.py: h2 = display when no heading sits between 28px and the display size
        elif not bp_level and not located.get(level):
            typ[level] = None; typ['levels_missing'][level] = 'not-in-capture'
        else:
            raise BuildError('%s: %s#/type/%s cannot be traced to the capture' % (ref, bp_path, level))
    if raw and isinstance(raw.get('fonts'), list):
        typ['families'] = {'value': list(raw['fonts']), 'source': ptr(raw_path, 'fonts')}
    else:
        typ['families'] = None
    d, b, h2 = typ['display'], typ['body'], typ['h2']
    typ['ratios'] = {
        'display_to_body': computed(round(d['px'] / b['px'], 2), 'display px ÷ body px', ['typography.display.px', 'typography.body.px'])
        if d and b and d['px'] and b['px'] else None,
        'display_to_h2': computed(round(d['px'] / h2['px'], 2), 'display px ÷ h2 px', ['typography.display.px', 'typography.h2.px'])
        if d and h2 and d['px'] and h2['px'] else None,
    }
    return typ


# ── composition ──────────────────────────────────────────────────────────────────────────────────────────────────────
def build_grid(bp, raw, bp_path, raw_path):
    """frame, gutter, container, col in px. normalize.py invents a frame (= gutter) and a gutter (40) when the capture has
    none; those come out null here. These four are written into the raw file by hand (extract.js emits only maxw)."""
    g = bp.get('grid') or {}; keys = ('frame', 'gutter', 'container', 'col')
    out = {}; fields = {}
    for k in keys:
        if not raw: out[k] = g.get(k)
        elif raw.get(k) is not None: out[k] = raw[k]; fields[k] = ptr(raw_path, k)
        elif k == 'container' and raw.get('maxw'): out[k] = raw['maxw'][0]; fields[k] = ptr(raw_path, 'maxw', 0)
        else: out[k] = None
        if out[k] is not None and out[k] != g.get(k):
            raise BuildError('%s#/grid/%s is %r but the capture says %r' % (bp_path, k, g.get(k), out[k]))
    out['not_recorded'] = sorted(k for k in keys if out[k] is None)
    out['source'] = {'blueprint': ptr(bp_path, 'grid'), 'raw': raw_path}
    out['raw_fields'] = fields
    return out


def build_surface(bp, raw, bp_path, raw_path):
    paper = (bp.get('colour') or {}).get('paper')
    src = {'blueprint': ptr(bp_path, 'colour', 'paper'), 'raw': None}
    if raw:
        pal = [(i, p) for i, p in enumerate(raw.get('palette') or []) if p.get('h')]
        if not pal: return None          # normalize.py would have written its default '#ffffff'
        i, top = sorted(pal, key=lambda t: -t[1].get('share', 0))[0]
        if top['h'] != paper: raise BuildError('%s#/colour/paper is not the largest-share colour in the capture' % bp_path)
        src['raw'] = ptr(raw_path, 'palette', i)
    if not paper: return None
    L = lum(paper)
    return {'paper': paper, 'paper_luminance': round(L, 3), 'mode': 'dark' if L < T['dark_lum'] else 'light', 'source': src}


def build_head(bps, raws, bp_sec_ptr, raw_sec_ptr):
    bh = bps.get('head')
    if not bh: return None
    if raws is None:
        out = {'px': bh.get('px'), 'weight': bh.get('w'), 'tracking': bh.get('ls'), 'leading': bh.get('lh'), 'case': bh.get('tt'),
               'align': bh.get('al'), 'x': bh.get('x'), 'y': bh.get('y'), 'wf': bh.get('wf'), 'source': bp_sec_ptr + '/head'}
    else:
        if not raws.get('heads'): raise BuildError('%s/head has no heading behind it in the capture' % bp_sec_ptr)
        h0 = raws['heads'][0]; hr = h0.get('rect') or {}; r = raws.get('rect') or {}
        out = {'px': h0.get('px'), 'weight': weight_of(h0), 'tracking': tracking_em(h0.get('ls'), h0.get('px')), 'leading': leading_of(h0),
               'case': h0.get('tt'), 'align': h0.get('al'),
               'x': bh.get('x') if 'x' in hr else None,
               'y': bh.get('y') if ('y' in hr and 'y' in r and r.get('h')) else None,
               'wf': bh.get('wf') if 'w' in hr else None,
               'source': raw_sec_ptr + '/heads/0'}
        if out['px'] != bh.get('px'): raise BuildError('%s/head/px does not match the capture' % bp_sec_ptr)
    out['not_recorded'] = sorted(k for k in ('px', 'weight', 'tracking', 'leading', 'case', 'align', 'x', 'y', 'wf') if out[k] is None)
    return out


def build_media(bps, raws, bp_sec_ptr, raw_sec_ptr):
    bm = bps.get('media') or []
    if raws is None:
        return [{'ar': m.get('ar'), 'wf': m.get('wf'), 'xf': m.get('xf'), 'bleed': bool(m.get('bleed')), 'kind': 'video' if m.get('video') else None,
                 'source': '%s/media/%d' % (bp_sec_ptr, j)} for j, m in enumerate(bm)]
    kept = [(k, im) for k, im in enumerate(raws.get('imgs') or []) if im.get('w') and im.get('h') and im['w'] > 100][:4]   # the filter normalize.py applies
    if len(kept) != len(bm): raise BuildError('%s/media does not line up with the capture' % bp_sec_ptr)
    kinds = {'VIDEO': 'video', 'IMG': 'image', 'CANVAS': 'canvas'}
    return [{'ar': m.get('ar'), 'wf': m.get('wf'), 'xf': m.get('xf') if 'x' in im else None,
             'bleed': im.get('bleed') is True,                 # extract.js drops false values, so an absent flag reads as false
             'kind': kinds.get(im.get('tag')),                  # null when the capture did not record the tag
             'source': '%s/imgs/%d' % (raw_sec_ptr, k)} for m, (k, im) in zip(bm, kept)]


def build_sections(bp, raw, bp_path, raw_path):
    bsecs = bp.get('sections') or []
    rsecs = raw['sections'] if raw else [None] * len(bsecs)
    if len(bsecs) != len(rsecs): raise BuildError('%s has %d sections, the capture has %d' % (bp_path, len(bsecs), len(rsecs)))
    out = []
    for i, (bps, raws) in enumerate(zip(bsecs, rsecs)):
        bsp = ptr(bp_path, 'sections', i); rsp = ptr(raw_path, 'sections', i) if raw else None
        if raws is None:
            sec = {'role': bps.get('role'), 'screens': bps.get('screens'), 'bg': None, 'sticky': None}
        else:
            sized = bool((raws.get('rect') or {}).get('h')) or 'screens' in raws
            sec = {'role': raws.get('role'),                                    # a hand annotation; null when absent
                   'screens': bps.get('screens') if sized else None,
                   'bg': raws.get('bg') if isinstance(raws.get('bg'), str) else None,
                   'sticky': True if raws.get('sticky') is True else None}
        sec['head'] = build_head(bps, raws, bsp, rsp)
        sec['media'] = build_media(bps, raws, bsp, rsp)
        sec['source'] = {'blueprint': bsp, 'raw': rsp}
        out.append(sec)
    return out


def S(i, tail=''):
    return 'composition.sections[%d]%s' % (i, ('.' + tail) if tail else '')


def is_bleed(m):
    return m['bleed'] is True or (m['wf'] is not None and m['wf'] >= T['bleed_wf'])


def is_large(m):
    return m['wf'] is not None and m['wf'] >= T['large_wf']


def is_large_still(m):
    return is_large(m) and m['kind'] not in ('video', 'canvas') and m['ar'] is not None and T['still_ar_min'] <= m['ar'] <= T['still_ar_max']


def build_composition(ref, bp, raw, bp_path, raw_path):
    secs = build_sections(bp, raw, bp_path, raw_path)
    comp = {'basis': 'measured' if raw else 'authored',
            'grid': build_grid(bp, raw, bp_path, raw_path),
            'surface': build_surface(bp, raw, bp_path, raw_path),
            'sections': secs}
    if raw:
        comp['fraction_base'] = ({'w': raw['vw'], 'basis': 'recorded', 'source': ptr(raw_path, 'vw')} if raw.get('vw')
                                 else {'w': ASSUMED_VW, 'basis': 'assumed', 'source': NORMALIZER})
    else:
        comp['fraction_base'] = None
    sized = [(i, s['screens']) for i, s in enumerate(secs) if s['screens'] is not None]
    placed = [(i, s['head']['x']) for i, s in enumerate(secs) if s['head'] and s['head']['x'] is not None]
    offset = [i for i, x in placed if x >= T['offset_x']]
    bleeds = []
    for i, s in enumerate(secs):
        j = next((j for j, m in enumerate(s['media']) if is_bleed(m)), None)
        if j is not None: bleeds.append(S(i, 'media[%d].%s' % (j, 'bleed' if s['media'][j]['bleed'] else 'wf')))
    page = bp.get('screens') if (not raw or raw.get('screens') is not None) else None
    comp['summary'] = {
        'sections': computed(len(secs), 'number of sections in the record', ['composition.sections']),
        'page_screens': None if page is None else {'value': page, 'source': {'blueprint': ptr(bp_path, 'screens'), 'raw': ptr(raw_path, 'screens') if raw else None}},
        'sections_screens_total': computed(round(sum(v for _, v in sized), 2), 'sum of section heights in screens; sections can overlap or leave gaps, so this is not the page length',
                                           [S(i, 'screens') for i, _ in sized]),
        'pacing': computed([v for _, v in sized], 'section heights in screens, in page order', [S(i, 'screens') for i, _ in sized]),
        'offset_heading_share': computed(share(len(offset), len(placed)), 'headings whose left edge is at or right of %s of the viewport width ÷ headings with a recorded position' % pct(T['offset_x']),
                                         [S(i, 'head.x') for i, _ in placed], [S(i, 'head.x') for i in offset], count=len(offset), of=len(placed)),
        'bleed_section_share': computed(share(len(bleeds), len(secs)), 'sections holding a medium flagged bleed in the capture or at least %s of the viewport wide ÷ all sections' % pct(T['bleed_wf']),
                                        ['composition.sections'], bleeds, count=len(bleeds), of=len(secs)),
    }
    return comp


def build_imagery(comp):
    secs = comp['sections']
    every = [(i, j, m) for i, s in enumerate(secs) for j, m in enumerate(s['media'])]
    large = [(i, j, m) for i, j, m in every if is_large(m) and m['ar'] is not None]
    portrait = [(i, j) for i, j, m in large if m['ar'] <= T['portrait_ar']]
    landscape = [(i, j) for i, j, m in large if m['ar'] >= T['landscape_ar']]
    stills = []
    for i, s in enumerate(secs):
        j = next((j for j, m in enumerate(s['media']) if is_large_still(m)), None)
        if j is not None: stills.append(S(i, 'media[%d]' % j))
    M = lambda pairs, tail: [S(i, 'media[%d].%s' % (j, tail)) for i, j in pairs]
    first_video = next((j for j, m in enumerate(secs[0]['media']) if m['kind'] == 'video'), None) if secs else None
    return {
        'basis': comp['basis'],
        'media_recorded': computed(len(every), 'media elements kept in the record: wider than 100px, at most 4 per section', ['composition.sections']),
        'aspects': computed(sorted({m['ar'] for _, _, m in large}), 'distinct aspect ratios (width ÷ height) of large media; large = at least %s of the viewport width' % pct(T['large_wf']),
                            M([(i, j) for i, j, _ in large], 'ar')),
        'portrait_share': computed(share(len(portrait), len(large)), 'large media with aspect ≤ %s ÷ large media' % num(T['portrait_ar']),
                                   M([(i, j) for i, j, _ in large], 'ar'), M(portrait, 'ar'), count=len(portrait), of=len(large)),
        'landscape_share': computed(share(len(landscape), len(large)), 'large media with aspect ≥ %s ÷ large media' % num(T['landscape_ar']),
                                    M([(i, j) for i, j, _ in large], 'ar'), M(landscape, 'ar'), count=len(landscape), of=len(large)),
        'image_sections': computed(len(stills), 'sections holding at least one large still: not tagged video or canvas, aspect between %s and %s' % (num(T['still_ar_min']), num(T['still_ar_max'])),
                                   ['composition.sections'], stills, of=len(secs), share=share(len(stills), len(secs))),
        'video_first_section': computed(first_video is not None, 'the first section holds a medium the capture tagged VIDEO',
                                        [S(0, 'media')] if secs else ['composition.sections'], [S(0, 'media[%d].kind' % first_video)] if first_video is not None else []),
    }


# ── prose, motion, experience ────────────────────────────────────────────────────────────────────────────────────────
def prose(text, source, source_texts):
    """Hand-written prose that already exists in a file, carried with its pointer. Withheld when it quotes source text."""
    quoted = any(len(t) >= NOTE_QUOTE_MIN and t in text for t in source_texts)
    return {'kind': 'prose', 'source': source, 'text': None if quoted else text, 'withheld': 'quotes-source-text' if quoted else None}


def build_motion(bp, raw, bp_path, raw_path, source_texts):
    m = (raw or {}).get('motion') or {}
    idea = (bp.get('motion') or {}).get('idea')
    out = {'libs': m.get('libs') if isinstance(m.get('libs'), dict) else None,
           'transitions': m.get('transitions') if isinstance(m.get('transitions'), list) else None,
           'keyframes': m.get('keyframes') if isinstance(m.get('keyframes'), list) else None,
           'animated': m.get('animated') if isinstance(m.get('animated'), int) else None,
           'tracked': m.get('tracked') if isinstance(m.get('tracked'), int) else None,
           'custom_cursor': True if m.get('customCursor') is True else None,
           'source': ptr(raw_path, 'motion') if m else None,
           'note': prose(idea, ptr(bp_path, 'motion', 'idea'), source_texts) if idea else None,
           'not_measured': ['scroll', 'pinning', 'sequence', 'interaction', 'reduced-motion']}
    return out


def build_experience(bp, comp, bp_path, source_texts):
    notes = [dict(prose(s['note'], ptr(bp_path, 'sections', i, 'note'), source_texts), section=i)
             for i, s in enumerate(bp.get('sections') or []) if s.get('note')]
    return {'pacing_screens': {'value': comp['summary']['pacing']['value'], 'evidence': ['composition.summary.pacing']},
            'section_notes': notes,
            'not_measured': ['narrative', 'interaction', 'mobile']}


# ── evidence, rights ─────────────────────────────────────────────────────────────────────────────────────────────────
def differing_paths(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        return [p for k in sorted(set(a) | set(b)) for p in (differing_paths(a[k], b[k], path + '/' + k) if k in a and k in b else [path + '/' + k])]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in differing_paths(x, y, '%s/%d' % (path, i))]
    return [] if a == b else [path or '/']


def build_evidence(ref, ev, bp, bp_path, raw_path, root=None):
    shots = ev.get('screenshots') or {}
    files = []
    if shots.get('dir'):
        if not os.path.isdir(P(shots['dir'], root)): raise BuildError('%s: screenshot folder %s does not exist' % (ref, shots['dir']))
        files = sorted(shots['dir'] + '/' + f for f in os.listdir(P(shots['dir'], root)) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')))
    caveats = []
    for c in ev.get('caveats') or []:
        try: values = [resolve_file_pointer(p, root) for p in c['shown_by']]
        except KeyError as err: raise BuildError('%s: caveat %s: %s' % (ref, c.get('code'), err))
        if c.get('expect') == 'differ' and not (len(values) == 2 and values[0] != values[1]):
            raise BuildError('%s: caveat %s says two values differ; the files say they do not' % (ref, c['code']))
        if c.get('expect') == 'number-not-in-text' and not (len(values) == 2 and isinstance(values[0], str) and isinstance(values[1], (int, float))
                                                              and not re.search(r'(?<![\d.])%s\s*px' % re.escape(num(values[1])), values[0])):
            raise BuildError('%s: caveat %s says a measured size is absent from a profile text; the files say otherwise' % (ref, c['code']))
        shown = [v if isinstance(v, (int, float)) and not isinstance(v, bool) or (isinstance(v, str) and re.match(r'https?://\S+$', v)) else None for v in values]
        caveats.append({'code': c['code'], 'shown_by': list(c['shown_by']), 'values': shown})
    mirrors = None
    if ev.get('mirrors'):
        other_path = '%s/%s.bp.json' % (BP_DIR, ev['mirrors'])
        mirrors = {'id': ev['mirrors'], 'blueprint': other_path, 'differs_at': differing_paths(bp, read_json(other_path, root))}
    return {'blueprint': bp_path, 'raw': raw_path,
            'screenshots': {'dir': shots.get('dir'), 'profile': shots.get('profile'), 'desktop': [], 'mobile': [], 'unclassified': files},
            'scroll_capture': None, 'mirrors': mirrors, 'caveats': caveats}


def licence_lookup(root=None):
    data = read_json(FONTS, root); table = {}
    for name, note in (data.get('_meta', {}).get('seen_on_winners_licensed') or {}).items():
        for face in re.sub(r'\s*\([^)]*\)\s*$', '', name).split(' / '):
            table.setdefault(face.strip().lower(), (note, ptr(FONTS, '_meta', 'seen_on_winners_licensed', name)))
    for i, f in enumerate(data.get('fonts') or []):
        if f.get('name') and f.get('license'): table[f['name'].strip().lower()] = (f['license'], ptr(FONTS, 'fonts', i, 'license'))
    return table


def build_rights(typ, root=None):
    table = licence_lookup(root); faces = set()
    for level in LEVELS:
        lv = typ.get(level)
        if not lv: continue
        if lv['source_face']: faces.add(('source', lv['source_face']))
        faces.add(('delivery', lv['delivery_face']))
    fonts = []
    for role, face in sorted(faces):
        note, src = table.get(face.strip().lower(), ('unknown', None))
        fonts.append({'face': face, 'role': role, 'licence': note, 'source': src})
    return {'screenshots': 'research-only', 'source_text': 'excluded', 'fonts': fonts}


# ── rules: principles ────────────────────────────────────────────────────────────────────────────────────────────────
# A rule reads the record, returns None or (statement, evidence[, confidence]). Evidence is pointers into the record;
# every pointer must hold a value. Confidence is "measured" unless the rule rests on a hand annotation ("observed").
def rule_scale_contrast_high(rec):
    r = rec['typography']['ratios']['display_to_body']
    if r and r['value'] >= T['scale_high']:
        return ('The largest measured heading is %s× the body size (%spx over %spx). Threshold: ratio ≥ %s.'
                % (num(r['value']), rec['typography']['display']['px'], rec['typography']['body']['px'], num(T['scale_high'])),
                ['typography.ratios.display_to_body', 'typography.display.px', 'typography.body.px'])


def rule_scale_contrast_low(rec):
    r = rec['typography']['ratios']['display_to_body']
    if r and r['value'] <= T['scale_low']:
        return ('The largest measured heading is only %s× the body size (%spx over %spx). Threshold: ratio ≤ %s.'
                % (num(r['value']), rec['typography']['display']['px'], rec['typography']['body']['px'], num(T['scale_low'])),
                ['typography.ratios.display_to_body', 'typography.display.px', 'typography.body.px'])


def rule_display_light_weight(rec):
    d = rec['typography']['display']
    if d and d['weight'] is not None and d['weight'] <= T['weight_light']:
        return ('The largest measured heading is set light, weight %d. Threshold: weight ≤ %d.' % (d['weight'], T['weight_light']), ['typography.display.weight'])


def rule_display_heavy_weight(rec):
    d = rec['typography']['display']
    if d and d['weight'] is not None and d['weight'] >= T['weight_heavy']:
        return ('The largest measured heading is set heavy, weight %d. Threshold: weight ≥ %d.' % (d['weight'], T['weight_heavy']), ['typography.display.weight'])


def rule_display_uppercase(rec):
    d = rec['typography']['display']
    if d and d['case'] == 'uppercase':
        return ('The largest measured heading is set in uppercase. Threshold: text-transform uppercase recorded in the capture.', ['typography.display.case'])


def rule_tight_tracking(rec):
    d = rec['typography']['display']
    if d and d['tracking'] is not None and d['tracking'] <= T['tracking_tight']:
        return ('The largest measured heading is tracked tight, %sem at %spx. Threshold: ≤ %sem.' % (('%.4f' % d['tracking']).rstrip('0').rstrip('.'), d['px'], num(T['tracking_tight'])),
                ['typography.display.tracking', 'typography.display.px'])


def rule_tight_leading(rec):
    d = rec['typography']['display']
    if d and d['leading'] is not None and d['leading'] <= T['leading_tight']:
        return ('The largest measured heading has a line height of %s. Threshold: ≤ %s.' % (num(d['leading']), num(T['leading_tight'])), ['typography.display.leading'])


def rule_single_family(rec):
    f = rec['typography']['families']
    if f and len(f['value']) == 1:
        return ('One type family was recorded on the whole page. Threshold: exactly one family in the capture\'s font list.', ['typography.families.value'])


def rule_offset_headings(rec):
    s = rec['composition']['summary']['offset_heading_share']
    if s['value'] is not None and s['value'] >= T['offset_share'] and s['count'] >= T['offset_min']:
        return ('%d of %d headings with a recorded position start at or right of %s of the viewport width. Threshold: share ≥ %s and at least %d headings.'
                % (s['count'], s['of'], pct(T['offset_x']), pct(T['offset_share']), T['offset_min']),
                ['composition.summary.offset_heading_share'] + s['matched'])


def rule_full_bleed_media(rec):
    s = rec['composition']['summary']['bleed_section_share']
    if s['value'] is not None and s['value'] >= T['bleed_share']:
        return ('%d of %d sections hold a medium that spans the viewport (flagged bleed in the capture, or at least %s of the viewport wide). Threshold: share ≥ %s.'
                % (s['count'], s['of'], pct(T['bleed_wf']), pct(T['bleed_share'])),
                ['composition.summary.bleed_section_share'] + s['matched'])


def _orientation(rec, key, word, cut):
    s = rec['imagery'][key]
    if s['value'] is not None and s['value'] >= T['orientation_share'] and s['of'] >= T['orientation_min']:
        return ('%d of %d large media are %s (%s; large = at least %s of the viewport width). Threshold: share ≥ %s and at least %d large media.'
                % (s['count'], s['of'], word, cut, pct(T['large_wf']), pct(T['orientation_share']), T['orientation_min']),
                ['imagery.' + key] + s['matched'])


def rule_portrait_media(rec):
    return _orientation(rec, 'portrait_share', 'portrait', 'aspect ≤ %s' % num(T['portrait_ar']))


def rule_landscape_media(rec):
    return _orientation(rec, 'landscape_share', 'landscape', 'aspect ≥ %s' % num(T['landscape_ar']))


def rule_image_led(rec):
    s = rec['imagery']['image_sections']
    if s['share'] is not None and s['share'] >= T['image_led']:
        return ('%d of %d sections hold a large still image. Threshold: share ≥ %s.' % (s['value'], s['of'], pct(T['image_led'])), ['imagery.image_sections'] + s['matched'])


def rule_type_led(rec):
    s = rec['imagery']['image_sections']
    if s['share'] is not None and s['share'] <= T['type_led']:
        return ('%d of %d sections hold a large still image. Threshold: share ≤ %s.' % (s['value'], s['of'], pct(T['type_led'])), ['imagery.image_sections', 'composition.sections'])


def rule_video_first_section(rec):
    s = rec['imagery']['video_first_section']
    if s['value'] is True:
        return ('The first measured section holds a video element. Threshold: a medium tagged VIDEO in the first section of the capture.', ['imagery.video_first_section'] + s['matched'])


def rule_pinned_sections(rec):
    secs = rec['composition']['sections']
    by_role = [i for i, s in enumerate(secs) if s['role'] and re.search(r'pinned|sticky', s['role'])]
    by_flag = [i for i, s in enumerate(secs) if s['sticky'] is True]
    hit = sorted(set(by_role) | set(by_flag))
    if not hit: return None
    sized = [(secs[i]['screens'], i) for i in hit if secs[i]['screens'] is not None]
    tall = max(sized)[1] if sized else None
    ev = [S(i, 'role') for i in by_role] + [S(i, 'sticky') for i in by_flag] + ([S(tall, 'screens')] if tall is not None else [])
    text = '%d of %d sections are marked pinned or sticky: %d by a role name written into the capture by hand, %d by the capture\'s sticky flag' % (len(hit), len(secs), len(by_role), len(by_flag))
    if tall is not None: text += '; the tallest of them runs %s screens' % num(secs[tall]['screens'])
    return (text + '. Threshold: at least one such section. The scroll behaviour itself was not measured.', ev, 'measured' if by_flag else 'observed')


def rule_dark_page(rec):
    s = rec['composition']['surface']
    if s and s['mode'] == 'dark':
        return ('The page surface is dark: the background colour with the largest share, %s, has relative luminance %s. Threshold: luminance < %s.'
                % (s['paper'], num(s['paper_luminance']), num(T['dark_lum'])), ['composition.surface.paper', 'composition.surface.paper_luminance'])


def rule_long_page(rec):
    p = rec['composition']['summary']['page_screens']
    if p and p['value'] >= T['long_screens']:
        return ('The page runs %s screens at the capture height. Threshold: ≥ %s screens.' % (num(p['value']), num(T['long_screens'])), ['composition.summary.page_screens.value'])


def rule_short_page(rec):
    p = rec['composition']['summary']['page_screens']
    if p and p['value'] <= T['short_screens']:
        return ('The page runs %s screens at the capture height. Threshold: ≤ %s screens.' % (num(p['value']), num(T['short_screens'])), ['composition.summary.page_screens.value'])


# (principle id, temper tag, rule). The temper tag is what retrieval matches a brand's temper list against.
RULES = [
    ('scale-contrast-high', 'high-contrast-type', rule_scale_contrast_high),
    ('scale-contrast-low', 'even-type', rule_scale_contrast_low),
    ('display-light-weight', 'light-weight', rule_display_light_weight),
    ('display-heavy-weight', 'heavy-weight', rule_display_heavy_weight),
    ('display-uppercase', 'uppercase', rule_display_uppercase),
    ('tight-tracking', 'tight-tracking', rule_tight_tracking),
    ('tight-leading', 'tight-leading', rule_tight_leading),
    ('single-family', 'one-family', rule_single_family),
    ('offset-headings', 'asymmetric', rule_offset_headings),
    ('full-bleed-media', 'full-bleed', rule_full_bleed_media),
    ('portrait-media', 'portrait-imagery', rule_portrait_media),
    ('landscape-media', 'landscape-imagery', rule_landscape_media),
    ('image-led', 'image-led', rule_image_led),
    ('type-led', 'type-led', rule_type_led),
    ('video-first-section', 'video-led', rule_video_first_section),
    ('pinned-sections', 'pinned', rule_pinned_sections),
    ('dark-page', 'dark', rule_dark_page),
    ('long-page', 'long', rule_long_page),
    ('short-page', 'compact', rule_short_page),
]
RULE_NAMES = [fn.__name__ for _, _, fn in RULES]
TEMPER_TAGS = [tag for _, tag, _ in RULES]


def derive_principles(rec):
    out = []
    for pid, _, fn in RULES:
        hit = fn(rec)
        if not hit: continue
        out.append({'id': pid, 'statement': hit[0], 'evidence': hit[1], 'derived_by': 'rule',
                    'confidence': hit[2] if len(hit) > 2 else 'measured', 'rule': fn.__name__})
    return out


def derive_needs(rec):
    """What a brand has to bring for this layout: one still per image-bearing section, and a video when the page opens on one.
    The capture does not say whether a still is a photograph, a product screenshot or an illustration."""
    return {'images_min': rec['imagery']['image_sections']['value'], 'video': rec['imagery']['video_first_section']['value'],
            'derived_by': 'rule', 'rule': 'derive_needs', 'evidence': ['imagery.image_sections', 'imagery.video_first_section']}


def derive_temper(principles):
    tags = {pid: tag for pid, tag, _ in RULES}
    return [{'tag': tags[p['id']], 'derived_by': 'rule', 'rule': p['rule'], 'principle': p['id']} for p in principles]


# ── one record ───────────────────────────────────────────────────────────────────────────────────────────────────────
def completeness(rec, raw):
    if not raw:
        return {'typography': 'authored', 'composition': 'authored', 'imagery': 'authored', 'motion': 'authored', 'experience': 'authored',
                'mobile': 'missing', 'screenshots': 'unverified' if rec['evidence']['screenshots']['unclassified'] else 'missing'}
    typ = rec['typography']; mo = rec['motion']
    has_prose = bool(mo['note']) or bool(rec['experience']['section_notes'])
    return {
        'typography': 'measured' if typ['display'] and typ['body'] else ('partial' if any(typ[l] for l in LEVELS) else 'missing'),
        'composition': 'measured-desktop' if rec['composition']['sections'] else 'missing',
        'imagery': 'measured-desktop' if rec['imagery']['media_recorded']['value'] else 'missing',
        'motion': 'partial' if (mo['transitions'] or mo['keyframes'] or mo['libs']) else ('prose-only' if mo['note'] else 'missing'),
        'experience': 'prose-only' if has_prose else 'missing',
        'mobile': 'missing',                 # no raw file holds a second viewport
        'screenshots': 'unverified' if rec['evidence']['screenshots']['unclassified'] else 'missing',
    }


def build_record(ref, ev, source_texts, root=None):
    bp_path = '%s/%s.bp.json' % (BP_DIR, ref); raw_path = '%s/%s.json' % (RAW_DIR, ref)
    bp = read_json(bp_path, root)
    raw = read_json(raw_path, root) if os.path.isfile(P(raw_path, root)) else None
    if raw is None: raw_path = None
    if bp.get('id') != ref: raise BuildError('%s: id inside the file is %r' % (bp_path, bp.get('id')))
    if raw is not None and raw.get('url') != bp.get('source'): raise BuildError('%s: source differs from the capture url' % bp_path)
    unread = sorted(set(raw or {}) & set(UNREAD_CAPTURE_FIELDS))
    if unread: raise BuildError('%s records %s; teach build.py, schema.json and validate.py to carry it before building' % (raw_path, ', '.join(unread)))
    src = bp.get('source'); is_url = isinstance(src, str) and re.match(r'https?://\S+$', src) is not None
    rec = {'schema_version': SCHEMA_VERSION, 'id': ref}
    rec['source'] = {'url': src if is_url else None,
                     'url_source': ptr(bp_path, 'source') if is_url else None,
                     'description': prose(src, ptr(bp_path, 'source'), source_texts) if (src and not is_url) else None,
                     'captured_at': None,
                     'viewport': {'w': (raw or {}).get('vw'), 'h': (raw or {}).get('vh'),
                                  'w_source': ptr(raw_path, 'vw') if raw and raw.get('vw') else None,
                                  'h_source': ptr(raw_path, 'vh') if raw and raw.get('vh') else None},
                     'dpr': None}
    rec['evidence'] = build_evidence(ref, ev, bp, bp_path, raw_path, root)
    rec['built_from'] = {bp_path: sha256_file(bp_path, root), ptr(EVIDENCE, 'references', ref): sha256_json(ev)}
    if raw is not None: rec['built_from'][raw_path] = sha256_file(raw_path, root)
    rec['typography'] = build_typography(ref, bp, raw, bp_path, raw_path)
    rec['composition'] = build_composition(ref, bp, raw, bp_path, raw_path)
    rec['imagery'] = build_imagery(rec['composition'])
    rec['motion'] = build_motion(bp, raw, bp_path, raw_path, source_texts)
    rec['experience'] = build_experience(bp, rec['composition'], bp_path, source_texts)
    rec['completeness'] = completeness(rec, raw)
    if raw is None: rec['status'] = 'authored'
    elif rec['typography']['display'] and rec['composition']['sections']: rec['status'] = 'measured-desktop'
    else: rec['status'] = 'incomplete'
    measured = rec['status'] != 'authored'
    rec['principles'] = derive_principles(rec) if measured else []        # nothing was measured for an authored blueprint
    rec['fits'] = {'kinds': [bp['class']] if bp.get('class') else [], 'kinds_source': ptr(bp_path, 'class'),
                   'archetype': bp.get('archetype') or None, 'archetype_source': ptr(bp_path, 'archetype') if bp.get('archetype') else None,
                   'also': [],                                             # no rule derives a second kind yet; retrieval scores other kinds by needs and temper
                   'needs': derive_needs(rec) if measured else None,
                   'temper': derive_temper(rec['principles'])}
    rec['rights'] = build_rights(rec['typography'], root)
    rec['implementation'] = {'recipe': '%s#%s' % (RECIPES, ref) if ref in recipe_ids() else None, 'ir_seeds': []}
    return rec


def dump(record):
    return json.dumps(record, indent=1, sort_keys=True, ensure_ascii=False) + '\n'


# ── the README tables ────────────────────────────────────────────────────────────────────────────────────────────────
BEGIN = '<!-- GENERATED by design_dna/build.py: do not edit between these markers -->'
END = '<!-- /GENERATED -->'


def tables(records):
    L = ['### Completeness', '',
         '| Reference | Status | Viewport w × h | Typography | Composition | Imagery | Motion | Experience | Mobile | Screenshots | Principles |',
         '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in records:
        c = r['completeness']; v = r['source']['viewport']
        lv = [l for l in LEVELS if r['typography'][l]]
        L.append('| %s | %s | %s × %s | %s (%d of 5 levels) | %s | %s | %s | %s | %s | %s | %d |' % (
            r['id'], r['status'], v['w'] if v['w'] else 'not recorded', v['h'] if v['h'] else 'not recorded',
            c['typography'], len(lv), c['composition'], c['imagery'], c['motion'], c['experience'], c['mobile'],
            c['screenshots'] + (' (%d files)' % len(r['evidence']['screenshots']['unclassified']) if r['evidence']['screenshots']['unclassified'] else ''),
            len(r['principles'])))
    L += ['', 'Capture date and device pixel ratio: not recorded for any reference.', '',
          '### Rules and where they fired', '', '| Principle | Rule in build.py | Temper tag | Fired on | References |', '|---|---|---|---|---|']
    for pid, tag, fn in RULES:
        hit = [r['id'] for r in records if any(p['id'] == pid for p in r['principles'])]
        L.append('| %s | `%s` | %s | %d | %s |' % (pid, fn.__name__, tag, len(hit), ', '.join(hit) if hit else 'none'))
    L += ['', '### What a brand has to bring', '', '| Reference | Kind | Surface | Image-bearing sections (`needs.images_min`) | Video in first section | Caveats |', '|---|---|---|---|---|---|']
    for r in records:
        n = r['fits']['needs']; s = r['composition']['surface']
        L.append('| %s | %s | %s | %s | %s | %s |' % (r['id'], ', '.join(r['fits']['kinds']), s['mode'] if s else 'not recorded',
                                                    n['images_min'] if n else 'not derived (authored)', ('yes' if n['video'] else 'no') if n else 'not derived (authored)',
                                                    ', '.join(c['code'] for c in r['evidence']['caveats']) or 'none'))
    faces = {}
    for r in records:
        for level in LEVELS:
            lv = r['typography'][level]
            if lv and lv['source_face']: faces.setdefault((lv['source_face'], lv['delivery_face'], lv['delivery_class'], lv['delivery_fallback']), set()).add(r['id'])
    licence = {(f['role'], f['face']): f['licence'] for r in records for f in r['rights']['fonts']}
    L += ['', '### Faces: what was measured and what ships', '', '| Source face | Ships as (`font_for`) | Class | Mapping in the renderer | Licence note, source face | Licence note, shipped face | References |', '|---|---|---|---|---|---|---|']
    for (face, ships, cls, missed), ids in sorted(faces.items(), key=lambda kv: (kv[0][0].lower(), kv[0][1])):
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (face, ships, cls, 'none: generic fallback' if missed else 'mapped', licence[('source', face)], licence[('delivery', ships)], ', '.join(sorted(ids))))
    return '\n'.join(L)


def with_tables(readme_text, records):
    if BEGIN not in readme_text or END not in readme_text: raise BuildError('%s has lost its GENERATED markers' % README)
    head, rest = readme_text.split(BEGIN, 1); _, tail = rest.split(END, 1)
    return head + BEGIN + '\n' + tables(records) + '\n' + END + tail


# ── all of it ────────────────────────────────────────────────────────────────────────────────────────────────────────
def build_records(root=None):
    ids = blueprint_ids(root); ev = read_json(EVIDENCE, root).get('references') or {}
    if sorted(ev) != ids:
        raise BuildError('%s must list exactly the blueprints: missing %s, unknown %s' % (EVIDENCE, sorted(set(ids) - set(ev)), sorted(set(ev) - set(ids))))
    texts = all_source_texts(root)
    return [build_record(ref, ev[ref], texts, root) for ref in ids]


def generate(root=None):
    """Every file this build owns, as {repo-relative path: text}. Writes nothing."""
    records = build_records(root)
    out = {'%s/%s.json' % (OUT_DIR, r['id']): dump(r) for r in records}
    with open(P(README, root), encoding='utf-8') as f: out[README] = with_tables(f.read(), records)
    return out


def stale(root=None):
    """Paths whose content on disk differs from the build, plus record files no blueprint stands behind."""
    want = generate(root); bad = []
    for path, text in sorted(want.items()):
        try:
            with open(P(path, root), encoding='utf-8') as f: same = f.read() == text
        except FileNotFoundError: same = False
        if not same: bad.append(path)
    if os.path.isdir(P(OUT_DIR, root)):
        bad += sorted('%s/%s' % (OUT_DIR, f) for f in os.listdir(P(OUT_DIR, root)) if f.endswith('.json') and '%s/%s' % (OUT_DIR, f) not in want)
    return bad


def main(argv):
    try:
        if '--check' in argv:
            bad = stale()
            for path in bad: print('stale: ' + path)
            print('design_dna: %s' % ('up to date' if not bad else '%d file(s) differ; run python3 design_dna/build.py' % len(bad)))
            return 1 if bad else 0
        want = generate()
        os.makedirs(P(OUT_DIR), exist_ok=True)
        for f in os.listdir(P(OUT_DIR)):
            if f.endswith('.json') and '%s/%s' % (OUT_DIR, f) not in want: os.remove(P('%s/%s' % (OUT_DIR, f)))
        for path, text in sorted(want.items()):
            with open(P(path), 'w', encoding='utf-8') as f: f.write(text)
        print('design_dna: wrote %d records and the README tables' % (len(want) - 1))
        return 0
    except BuildError as err:
        print('design_dna: build failed: %s' % err, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
