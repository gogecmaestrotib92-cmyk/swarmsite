"""edit.py — the editor on the page (BRIEF-engine.md step 9): a visitor's edits as a patch over the job's data, never
over a template, so that a switch to another of the three designs keeps every edit. No model; nothing is written that
the visitor did not write or choose.

An edit is one operation; the patch is the list, replayed in order over the data (the job's data.json, or a variant's
own data.json when it carries made pictures):

    {"op": "text",    "path": "hero.title", "value": "…"}      a text the data already has, rewritten
    {"op": "picture", "path": "media.photos.0", "src": "…"}     a picture slot given another of the client's own
                                                                pictures (or a photograph they uploaded)
    {"op": "hide",    "block": "faq"}  /  {"op": "show", "block": "faq"}
    {"op": "move",    "block": "faq", "by": -1}                  only where the design says it may move (needs.json `movable`)
    {"op": "palette", "ground": "#…", "ink": "#…", "accent": "#…"}
    {"op": "photo",   "src": "media/upload/<uuid>.jpg", "w": …, "h": …}   a photograph uploaded while editing, now theirs

    apply(data, ops, slug=None) -> (data, refused: [{i, op, why}])     pure; `data` is not changed
    fields(data) -> [{path, value, block}]       every text the visitor may rewrite
    pictures(data) -> [{src, w, h}]              the client's own pictures, the only ones a slot may take
    slots(data) -> [{path, src}]                 every place a picture stands
    palettes(data) -> [{name, ground, ink, accent, tone}]   a few that read (ink on ground ≥ 7:1); tone: light | dark
    python3 lib/templates/edit.py render <data.json> <slug> [--ops ops.json] [--base URL]   → the page, on stdout
    python3 lib/templates/edit.py apply <data.json> <ops.json> [--slug S]                 → {data, refused}
    python3 lib/templates/edit.py describe <data.json> [--ops F] [--slug S]  → {fields, pictures, slots, blocks, palettes, refused, movable, tone}
    python3 lib/templates/edit.py measure <picture>                         → {w, h} of a JPEG, PNG or WebP
    python3 lib/templates/edit.py package <data.json> <slug> --ops F --media-from URL|DIR --zip Z [--verify]
                                    the edited page's package, compared offline with the edited page → {ok, why, bytes}
    python3 lib/templates/edit.py files <zip>                               → {files: [{file, data (base64)}]}
"""
import copy
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# keys that hold no words a visitor reads: addresses, sizes, kinds, classifiers — never edited as text
NOT_TEXT = {'src', 'h', 'href', 'img', 'logo', 'poster', 'home', 'kind', 'niche', 'lang', 'shape', 'role', 'page', 'w', 'count',
            'state', 'from', 'small', 'logo_wordmark', 'ground', 'ink', 'accent', 'extra', 'tone', 'name_key'}
# the blocks a visitor may hide; the name and the first line are the page itself
FIXED = {'brand', 'hero', 'kind', 'niche', 'lang', 'palette', 'media', 'character'}
MAX_TEXT = 600
TOP_NOT_TEXT = {'kind', 'niche', 'lang', 'palette', 'media', 'character'}   # classifiers and pictures, not words on the page
HEX = re.compile(r'^#[0-9a-fA-F]{6}$')
UPLOADED = re.compile(r'^media/upload/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.(jpg|png|webp)$')


def _parts(path):
    if not isinstance(path, str) or not path or len(path) > 200:
        return None
    out = []
    for p in path.split('.'):
        if re.fullmatch(r'\d{1,3}', p):
            out.append(int(p))
        elif re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,40}', p):
            out.append(p)
        else:
            return None
    return out


def _get(d, parts):
    for p in parts:
        if isinstance(p, int) and isinstance(d, list) and 0 <= p < len(d):
            d = d[p]
        elif isinstance(p, str) and isinstance(d, dict) and p in d:
            d = d[p]
        else:
            return None, False
    return d, True


def _set(d, parts, v):
    for p in parts[:-1]:
        d = d[p]
    d[parts[-1]] = v


def fields(d, at=(), block=None):
    """every text of the data a visitor may rewrite, in page order of the data"""
    out = []
    if isinstance(d, dict):
        for k, v in d.items():
            if k.startswith('_') or k in NOT_TEXT or (not at and k in TOP_NOT_TEXT):
                continue
            out += fields(v, at + (k,), block or k)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out += fields(v, at + (str(i),), block)
    elif isinstance(d, str) and d.strip() and at:
        out.append({'path': '.'.join(at), 'value': d, 'block': block})
    return out


def pictures(d):
    """the client's own pictures (never a made one): what a picture slot may be given"""
    seen, out = set(), []
    for key in ('photos', 'screens', 'phones'):
        for p in ((d.get('media') or {}).get(key) or []):
            if isinstance(p, dict) and isinstance(p.get('src'), str) and p['src'] not in seen and not p['src'].startswith('media/library/'):
                seen.add(p['src'])
                out.append({'src': p['src'], **{k: p[k] for k in ('w', 'h', 'alt') if k in p}})
    return out


def slots(d, at=()):
    """every place the data stands a picture: a picture object ({src, …}) or an `img` key"""
    out = []
    if isinstance(d, dict):
        if isinstance(d.get('src'), str) and at and at[0] == 'media' and len(at) >= 3 and at[1] in ('photos', 'screens', 'phones'):
            out.append({'path': '.'.join(at), 'src': d['src']})
        for k, v in d.items():
            if k == 'img' and isinstance(v, str):
                out.append({'path': '.'.join(at + (k,)), 'src': v})
            elif k != 'made':
                out += slots(v, at + (k,))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out += slots(v, at + (str(i),))
    return out


def _lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def tone(ground):
    """'dark' or 'light': which way a ground reads. A design is measured on the client's own tone; the other one is a
    different page (a logo drawn for a light bar, a picture with see-through edges, a card that was a shade of white)"""
    return 'dark' if HEX.match(ground or '') and _lum(ground) < .18 else 'light'


def palettes(d):
    """a few grounds the client's accent can stand on; each with ink that reads on it at 7:1 or better, and its tone.
    The accent is the client's own when they have one; it is kept only where it reads on the ground at 3:1 (a button,
    a large word)"""
    acc = ((d.get('palette') or {}).get('accent') or '').lower()
    out = []
    for name, ground, ink in (('white', '#ffffff', '#151515'), ('paper', '#f5f1e8', '#1b1813'), ('stone', '#e9e7e2', '#141414'),
                              ('ink', '#111111', '#f2f2ef'), ('night', '#0d1424', '#eef1f6'), ('forest', '#10201a', '#eef3ee')):
        a = acc if HEX.match(acc or '') and contrast(acc, ground) >= 3 else ink
        out.append({'name': name, 'ground': ground, 'ink': ink, 'accent': a, 'tone': tone(ground)})
    return [p for p in out if contrast(p['ink'], p['ground']) >= 7]


def other_tone(d):
    """the palette a job tries a design on to learn whether it holds in the tone the client's page is not: the first of
    `palettes` of the other tone -> {op} or None"""
    mine = tone((d.get('palette') or {}).get('ground') or '#ffffff')
    p = next((p for p in palettes(d) if p['tone'] != mine), None)
    return {'op': 'palette', 'ground': p['ground'], 'ink': p['ink'], 'accent': p['accent']} if p else None


def blocks(d):
    return [k for k in d if not k.startswith('_') and k not in FIXED]


def _registry():
    R = sys.modules.get('swarmsite_templates_registry')
    if R is None:
        spec = importlib.util.spec_from_file_location('swarmsite_templates_registry', HERE / 'registry.py')
        R = importlib.util.module_from_spec(spec)
        sys.modules['swarmsite_templates_registry'] = R
        spec.loader.exec_module(R)
    return R


def movable(slug):
    """the sections a design lets a visitor move (needs.json `movable`); none unless it says so"""
    if not slug:
        return []
    m = (_registry().needs(slug) or {}).get('movable')
    return [x for x in m if isinstance(x, str)] if isinstance(m, list) else []


def apply(data, ops, slug=None):
    """the data with every operation that may be applied, in order; the others refused with their reason"""
    d = copy.deepcopy(data)
    hidden, refused = {}, []
    own = {p['src']: p for p in pictures(data)}
    may_move = movable(slug)
    for i, op in enumerate(ops if isinstance(ops, list) else []):
        why = ''
        kind = op.get('op') if isinstance(op, dict) else None
        if kind == 'text':
            parts, v = _parts(op.get('path')), op.get('value')
            cur, ok = _get(d, parts) if parts else (None, False)
            if not ok or not isinstance(cur, str) or (parts and isinstance(parts[-1], str) and parts[-1] in NOT_TEXT) or (parts and parts[0] in TOP_NOT_TEXT):
                why = 'not a text of this page'
            elif not isinstance(v, str) or not v.strip():
                why = 'an empty text: hide the section instead'
            elif len(v) > MAX_TEXT:
                why = 'longer than %d characters' % MAX_TEXT
            else:
                _set(d, parts, re.sub(r'\s+', ' ', v).strip())
        elif kind == 'picture':
            parts, src = _parts(op.get('path')), op.get('src')
            cur, ok = _get(d, parts) if parts else (None, False)
            if src not in own:
                why = 'not one of the client\'s own pictures'
            elif ok and isinstance(cur, dict) and isinstance(cur.get('src'), str) and parts[0] == 'media':
                cur.update({k: v for k, v in own[src].items() if k in ('src', 'w', 'h')})
            elif ok and isinstance(cur, str) and parts[-1] == 'img':
                _set(d, parts, src)
            else:
                why = 'no picture stands there'
        elif kind in ('hide', 'show'):
            b = op.get('block')
            if not isinstance(b, str) or b in FIXED or b.startswith('_'):
                why = 'this part of the page cannot be hidden'
            elif kind == 'hide':
                if b in d:
                    hidden[b] = d.pop(b)
                elif b not in hidden:
                    why = 'no such section'
            else:
                if b in hidden:
                    d[b] = hidden.pop(b)
                elif b not in d:
                    why = 'no such section'
        elif kind == 'move':
            b, by = op.get('block'), op.get('by')
            if b not in may_move:
                why = 'this design keeps its own order'
            elif by not in (-1, 1):
                why = 'a section moves one place at a time'
            else:
                order = [k for k in d.get('_order') or blocks(d) if k in d]
                j = order.index(b) if b in order else -1
                if 0 <= j + by < len(order) and j >= 0:
                    order[j], order[j + by] = order[j + by], order[j]
                d['_order'] = order
        elif kind == 'photo':
            src, w, h = op.get('src'), op.get('w'), op.get('h')
            if not (isinstance(src, str) and UPLOADED.match(src)) or not all(isinstance(x, int) and not isinstance(x, bool) and 0 < x < 20000 for x in (w, h)):
                why = 'not a photograph uploaded here'
            elif src not in own:
                pic = {'src': src, 'w': w, 'h': h}
                d.setdefault('media', {}).setdefault('photos', []).append(pic)
                own[src] = pic
        elif kind == 'palette':
            g, ink, a = (op.get(k) for k in ('ground', 'ink', 'accent'))
            if not all(isinstance(x, str) and HEX.match(x) for x in (g, ink, a)):
                why = 'a colour is #rrggbb'
            elif contrast(ink, g) < 4.5:
                why = 'the text would not read on that ground (%.1f:1)' % contrast(ink, g)
            else:
                d['palette'] = {**(d.get('palette') or {}), 'ground': g.lower(), 'ink': ink.lower(), 'accent': a.lower()}
        else:
            why = 'not an edit'
        if why:
            refused.append({'i': i, 'op': kind, 'why': why})
    if '_order' in d and not d['_order']:
        d.pop('_order')
    return d, refused


def _package_mod():
    spec = importlib.util.spec_from_file_location('swarmsite_templates_package', HERE / 'package.py')
    P = sys.modules.get('swarmsite_templates_package')
    if P is None:
        P = importlib.util.module_from_spec(spec)
        sys.modules['swarmsite_templates_package'] = P
        spec.loader.exec_module(P)
    return P


def fetch_media(rels, media_from, into):
    """the pictures the edited page asks for, written under `into` from where the preview's are (an https address, or a
    folder); -> the ones that could not be had"""
    import shutil
    import urllib.request
    missing = []
    for rel in rels:
        if not rel.startswith('media/') or '..' in Path(rel).parts:
            missing.append(rel)
            continue
        to = Path(into) / rel
        to.parent.mkdir(parents=True, exist_ok=True)
        try:
            if re.match(r'^https://', str(media_from)):
                with urllib.request.urlopen(str(media_from) + rel, timeout=30) as r:
                    to.write_bytes(r.read(20_000_001)[:20_000_000])
            elif Path(media_from, rel).is_file():
                shutil.copyfile(Path(media_from, rel), to)
            else:
                missing.append(rel)
        except OSError:
            missing.append(rel)
    return missing


def package(data, slug, ops, media_from, zip_path, verify=True):
    """the package of the edited page: the same render the editor showed, its media and fonts beside it, then opened
    offline and compared with that page screen by screen. -> {ok, why, bytes, files}"""
    import tempfile
    P, R = _package_mod(), _registry()
    d, refused = apply(data, ops, slug)
    d = {k: v for k, v in d.items() if k != '_order'}
    with tempfile.TemporaryDirectory(prefix='edpkg-') as work:
        missing = fetch_media(R.media_used(slug, d), media_from, work)
        if missing:
            return {'ok': False, 'why': ['a picture of the page could not be had: %s' % missing[0]], 'refused': refused}
        try:
            rep = P.build(slug, d, work, zip_path)
        except (P.PackageError, OSError, ValueError) as ex:
            return {'ok': False, 'why': [str(ex)[:300]], 'refused': refused}
        res = {'ok': True, 'why': [], 'bytes': rep['bytes'], 'files': len(rep['files']), 'refused': refused}
        if verify:
            page = Path(work) / (slug + '.html')
            page.write_text(R.render(slug, d, ''), encoding='utf-8')
            with tempfile.TemporaryDirectory(prefix='edcmp-') as cmp:
                v = P.verify(page, zip_path, cmp)
            res.update(ok=bool(v.get('ok')), why=v.get('why') or [])
        return res


def zip_files(zip_path):
    """the files of a package, for an upload that sends them as they are"""
    import base64
    import zipfile
    out = []
    with zipfile.ZipFile(zip_path) as z:
        for i in z.infolist():
            if i.is_dir() or '..' in Path(i.filename).parts or i.filename.startswith('/'):
                continue
            out.append({'file': i.filename, 'data': base64.b64encode(z.read(i)).decode('ascii')})
    return out


def describe(d):
    return {'fields': fields(d), 'pictures': pictures(d), 'slots': slots(d), 'blocks': blocks(d), 'palettes': palettes(d)}


if __name__ == '__main__':
    a = sys.argv[1:]
    opt = lambda k, dflt=None: a[a.index(k) + 1] if k in a else dflt
    load = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    if a[:1] == ['render'] and len(a) >= 3:
        R = _registry()
        data, refused = apply(load(a[1]), load(opt('--ops')) if opt('--ops') else [], a[2])
        sys.stdout.write(R.render(a[2], {k: v for k, v in data.items() if k != '_order'}, opt('--base', '')))
        sys.stderr.write(json.dumps({'refused': refused}) + '\n')
    elif a[:1] == ['apply'] and len(a) >= 3:
        data, refused = apply(load(a[1]), load(a[2]), opt('--slug'))
        print(json.dumps({'data': data, 'refused': refused}, ensure_ascii=False))
    elif a[:1] == ['describe'] and len(a) >= 2:
        given = load(a[1])
        data, refused = apply(given, load(opt('--ops')) if opt('--ops') else [], opt('--slug'))
        # `tone`: the tone of the page as the job made it, before any edit — the one its designs were measured on
        print(json.dumps({**describe(data), 'refused': refused, 'movable': movable(opt('--slug')),
                          'tone': tone((given.get('palette') or {}).get('ground') or '#ffffff')}, ensure_ascii=False))
    elif a[:1] == ['package'] and len(a) >= 3:
        print(json.dumps(package(load(a[1]), a[2], load(opt('--ops')) if opt('--ops') else [], opt('--media-from', ''), opt('--zip'), verify='--verify' in a), ensure_ascii=False))
    elif a[:1] == ['files'] and len(a) >= 2:
        print(json.dumps({'files': zip_files(a[1])}))
    elif a[:1] == ['measure'] and len(a) >= 2:
        spec = importlib.util.spec_from_file_location('swarmsite_templates_form', HERE / 'form.py')
        F = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(F)
        wh = F.size(Path(a[1]).read_bytes()[:65536])
        print(json.dumps({'w': wh[0], 'h': wh[1]} if wh else {}))
    else:
        sys.exit(__doc__)
