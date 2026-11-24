"""registry.py — the library of reference templates: list them, load one, render a client's data through it.

A template is a folder `lib/templates/<slug>/` holding `render.py` with one pure function `render(d: dict) -> str`
(a whole page, inline CSS and JS, no client and no model call — see CONTRACT in the research folder and each NOTES.md),
`NOTES.md` (what was measured on the reference and how the data fills it) and, once it has been measured on the test
clients, `needs.json` (the least a client must have for the template to be offered). `recipes.py` beside this file is the
OLD pipeline's recipe table and has nothing to do with these folders.

    list_templates() -> [{'slug', 'has_needs', 'needs', 'selectable', 'why'}]   every folder with a render.py
    load(slug)       -> the template's module (cached)
    needs(slug)      -> its needs.json as a dict, or None
    render(slug, d, media_base=None) -> str      (tablet=False: without the desk composition from 768 px, tablet.py)

Media. A template writes every media path of the data behind the fixed prefix '../../' (a page built into
`<slug>/out/` reaches `media/…` two folders up). `media_base` replaces that prefix for the paths the DATA names — and
only for those — so the same render serves a preview address (`media_base='https://…/jobs/<id>/'`) and a package
(`media_base=''`, pictures beside index.html). None keeps the template's own output, byte for byte. A template file is
never rewritten for this: the folder stays an exact copy of what was measured and gated.
"""
import html
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_MEDIA_BASE = '../../'
SLUG = re.compile(r'^[a-z0-9][a-z0-9_-]{0,63}$')
_REMOTE = re.compile(r'^(?:[a-z][a-z0-9+.-]*:|//|#)', re.I)       # http:, https:, data:, blob:, //host, #anchor
_MEDIA_KEYS = {'src', 'poster', 'img', 'logo'}
_MEDIA_EXT = re.compile(r'\.(?:jpe?g|png|webp|avif|gif|svg|mp4|webm|mov)(?:\?[^\s]*)?$', re.I)
_modules = {}


class TemplateError(Exception):
    """A slug that is not a template, a template that does not load, a media path that could not be re-based."""


def _dir(slug, root=None):
    if not isinstance(slug, str) or not SLUG.match(slug):
        raise TemplateError('not a template slug: %r' % (slug,))
    return Path(root or HERE) / slug


def slugs(root=None):
    base = Path(root or HERE)
    return sorted(p.name for p in base.iterdir() if p.is_dir() and SLUG.match(p.name) and (p / 'render.py').is_file())


def needs(slug, root=None):
    """needs.json of a template, or None when it has none or the file is not a JSON object"""
    p = _dir(slug, root) / 'needs.json'
    if not p.is_file():
        return None
    try:
        v = json.loads(p.read_text(encoding='utf-8'))
    except ValueError:
        return None
    return v if isinstance(v, dict) else None


def list_templates(root=None):
    out = []
    for s in slugs(root):
        n = needs(s, root)
        has = (_dir(s, root) / 'needs.json').is_file()
        why = '' if n is not None else ('needs.json is not a JSON object' if has else 'no needs.json: not measured on the test clients yet')
        out.append({'slug': s, 'has_needs': n is not None, 'needs': n, 'selectable': n is not None, 'why': why,
                    'notes': (_dir(s, root) / 'NOTES.md').is_file()})
    return out


def load(slug, root=None):
    d = _dir(slug, root)
    key = str(d)
    if key in _modules:
        return _modules[key]
    f = d / 'render.py'
    if not f.is_file():
        raise TemplateError('no template %r in %s' % (slug, d.parent))
    spec = importlib.util.spec_from_file_location('swarmsite_template_' + re.sub(r'\W', '_', slug), f)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as ex:                                     # a template that does not import is a template that is not there
        raise TemplateError('template %r does not load: %s' % (slug, ex)) from ex
    if not callable(getattr(mod, 'render', None)):
        raise TemplateError('template %r has no render(d)' % slug)
    _modules[key] = mod
    return mod


def media_paths(d):
    """Every local media path the data names (the files a page built from it may ask for), in first-seen order."""
    seen = {}

    def walk(v, key=None):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, k)
        elif isinstance(v, list):
            for x in v:
                walk(x, key)
        elif isinstance(v, str) and v.strip() and not _REMOTE.match(v.strip()) and (key in _MEDIA_KEYS or (_MEDIA_EXT.search(v.strip()) and ' ' not in v.strip())):
            seen.setdefault(v.strip(), None)
    walk(d)
    return list(seen)


def rebase(page, d, media_base):
    """The page with '../../<path>' turned into '<media_base><path>' for each media path of the data. Returns
    (page, used) — `used` is the list of data paths the page really asks for."""
    paths = media_paths(d)
    if not paths:
        return page, []
    forms = {}
    for p in paths:
        for f in {p, html.escape(p, quote=True)}:
            forms[DEFAULT_MEDIA_BASE + f] = p
    rx = re.compile('|'.join(re.escape(k) for k in sorted(forms, key=len, reverse=True)) + r'(?![\w./-])')
    used = {}

    def sub(m):
        p = forms[m.group(0)]
        used.setdefault(p, None)
        return html.escape(media_base, quote=True) + m.group(0)[len(DEFAULT_MEDIA_BASE):]
    return rx.sub(sub, page), list(used)


def _page(slug, d, root=None, tablet=True):
    """the template's page with what the template has no place for added under its sections (more.py): the client's
    leftover sections in their own words, and the photographs the page did not ask for"""
    d = _subject(d)
    page = load(slug, root).render(d)
    if not isinstance(page, str):
        raise TemplateError('template %r returned %s, not a page' % (slug, type(page).__name__))
    def part(name):
        key = 'swarmsite_templates_' + name
        if key not in sys.modules:
            spec = importlib.util.spec_from_file_location(key, HERE / (name + '.py'))
            mod = importlib.util.module_from_spec(spec)
            sys.modules[key] = mod
            spec.loader.exec_module(mod)
        return sys.modules[key]
    page = part('more').add(d, page)
    # A headline's lines are of a like length: no word left alone on a line ("Your team. / Your / game plan.", owner's
    # review 2026-11-15). Sixteen templates did not ask for it. It stands first in <head>, so a template that sets
    # its own wrapping keeps it.
    i = page.find('<head')
    j = page.find('>', i) if i >= 0 else -1
    if j >= 0 and 'data-sw-wrap' not in page:
        page = page[:j + 1] + '<style data-sw-wrap>h1,h2,h3{text-wrap:balance}</style>' + page[j + 1:]
    # a library picture stands in the client's own accent (pictures.tint): one filter for every prepared picture of the page
    m = re.search(r'media/library/[a-z0-9-]+/([a-z0-9-]+)/', page)
    accent = (d.get('palette') or {}).get('accent') if isinstance(d.get('palette'), dict) else None
    if m and accent and 'data-sw-art' not in page:
        P = part('pictures')
        _, pals = P.library(root)
        f = P.tint(accent, m.group(1), pals) if pals else ''
        if f and j >= 0:
            page = page[:j + 1] + '<style data-sw-art>img[src*="media/library/"]{filter:%s}</style>' % f + page[j + 1:]
    page = _phones(d, page)
    page = _readable(d, page)
    # a template measured to hold it (needs.json "tablet": "desk", written only after tablet.py --sweep passed for it)
    # stands in its desk composition from 768 px, drawn smaller to fit — the look the client chose (owner, 2026-11-22)
    if tablet and (needs(slug, root) or {}).get('tablet') == 'desk':
        page = part('tablet').desk(page)
    # every page answers a hand the same way: a press, an anchor below a bar that stays, solid bars when the system asks
    # for less transparency or more contrast — each only where the template has not said it (feel.py, owner 2026-11-23)
    page = part('feel').add(page)
    return _direction(page)


# Words written from right to left are set from right to left. No template said so: a Persian restaurant's three
# designs (a visitor's job, 2026-11-22) stood with their lines ranged left, the full stop at the wrong end of every
# sentence and the words of a mixed line out of order ("VIP سالن و رزرو"), though the client's own page was dir="rtl".
# It is read off the page's words, not off the language code (a page may state none, or the wrong one): when most of
# its letters are of a right-to-left script (Hebrew, Arabic, Syriac, Thaana, N'Ko and their forms), every line takes
# its direction from its own first letter (unicode-bidi: plaintext) — it begins at the right, its stop ends it, a
# Latin name inside it keeps its place, and a line of Latin on the same page still runs from the left.
# The design itself is not mirrored. Measured the same day, 48 templates on one restaurant set in Persian: with
# <html dir="rtl"> 18 of them gained a failure at the gate (pages scrolling sideways, strips and pinned scenes built
# on left-to-right offsets left blank, a script error) and 12 stood; with the lines alone turned, 25 stood against
# 19 with nothing done. A template that states a direction of its own is left to it. The gate holds it (`ltr`).
RTL_LETTER = re.compile('[\u0590-\u08ff\ufb1d-\ufdff\ufe70-\ufefc]')
RTL_CSS = '<style data-sw-bidi>body,body *{unicode-bidi:plaintext}</style>'


def reads_rtl(text):
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and 2 * sum(1 for c in letters if RTL_LETTER.match(c)) > len(letters)


def _direction(page):
    m = re.search(r'<html\b[^>]*>', page)
    if not m or re.search(r'\bdir\s*=', m.group(0)) or 'data-sw-bidi' in page:
        return page
    words = re.sub(r'(?is)<(script|style|svg)\b.*?</\1>|<[^>]+>|&[a-z#0-9]+;', ' ', page[m.end():])
    i = page.find('<head')
    j = page.find('>', i) if i >= 0 else -1
    return page[:j + 1] + RTL_CSS + page[j + 1:] if j >= 0 and reads_rtl(words) else page


# A product's screen stands whole in the frame made for it — a phone in a phone, a window in a window: its sides and
# its top are never cut. For three days (2026-11-15 to 2026-11-18) a screen whose box came out under 45 % of its own
# width was drawn larger inside the same box and cropped to its busiest part, so its letters would read; on a real
# client (an invoicing product, the owner on his phone, 2026-11-18) every such frame held half a headline —
# "ks. Get paid soo" in a phone, "CK FRIDAY" in a window — and read as a broken page. Photographed both ways, the
# whole screen was the better picture in every frame. A screen that is too small to read is a matter of the frame's
# size, which is the template's; it is never mended by cutting the screen. The page still carries the list of its
# product screens with the width each was drawn in (`sw-detail`): the gate reads it to know which pictures are
# screens (`sliced`, lib/qa/template_gate.mjs).
# Where a template shows part of a screen on purpose (a small window of another shape), the part is chosen on
# capture's map of detail with the app's own frame taken out (`_subject`): the one most evenly full of the product —
# a cell counts up to CAP — whose edge cuts the least (RING). clicky/render.py `busiest` is that rule.
CAP, RING = 20, .25


def _frame(grids):
    """for maps of one shape (three or more screens of one product): the box of each [x0, y0, x1, y1] past the app's
    own frame — the columns and rows at its edges that say the same on most of the screens (a side menu, a top bar,
    a notice), or nothing at all. None where a screen has no such frame or would lose more than half of itself."""
    n, R, C = len(grids), len(grids[0]), len(grids[0][0])
    out = []
    for g in grids:
        def same(r, c):
            vs = sorted(x[r][c] for x in grids)
            md = (vs[(n - 1) // 2] + vs[n // 2]) / 2
            tol = max(3, .25 * md)
            return abs(g[r][c] - md) <= tol and sum(1 for v in vs if abs(v - md) <= tol) * 3 >= n * 2
        S = [[same(r, c) for c in range(C)] for r in range(R)]
        # a column or row with nothing on it is no frame: an empty margin stays with the screen
        col = lambda c: sum(S[r][c] for r in range(R)) >= .85 * R and sum(1 for r in range(R) if g[r][c] >= 6) >= 2
        x0, x1 = 0, C
        while x0 < C // 2 and col(x0):
            x0 += 1
        while x1 > C // 2 and col(x1 - 1):
            x1 -= 1

        def row(r):
            busy = [c for c in range(x0, x1) if g[r][c] >= 6]
            return len(busy) >= 2 and sum(S[r][c] for c in busy) >= .7 * len(busy)
        y0, y1 = 0, R
        while y0 < R // 3 and row(y0):
            y0 += 1
        while y1 > R - R // 3 and row(y1 - 1):
            y1 -= 1
        keep = (x1 - x0) * 2 >= C and (y1 - y0) * 2 >= R and (x0, y0, x1, y1) != (0, 0, C, R)
        out.append([x0, y0, x1, y1] if keep else None)
    return out


def _subject(d):
    """the data with each product screen's map of detail cleared where the app's own frame is (`_frame`), so no
    template shows a menu for a product. A copy where anything changes; the caller's dict is not touched."""
    md = d.get('media') if isinstance(d.get('media'), dict) else None
    if not md:
        return d
    new = {}
    for kind in ('screens', 'phones'):
        ms = md.get(kind) if isinstance(md.get(kind), list) else []
        shapes = {}
        for i, m in enumerate(ms):
            g = m.get('detail') if isinstance(m, dict) else None
            if isinstance(g, list) and g and g[0] and all(isinstance(r, list) and len(r) == len(g[0]) and all(isinstance(v, (int, float)) for v in r) for r in g):
                shapes.setdefault((len(g), len(g[0])), []).append(i)
        for idx in shapes.values():
            if len(idx) < 3:
                continue
            for i, box in zip(idx, _frame([ms[i]['detail'] for i in idx])):
                if box:
                    x0, y0, x1, y1 = box
                    g = [[v if x0 <= c < x1 and y0 <= r < y1 else 0 for c, v in enumerate(row)] for r, row in enumerate(ms[i]['detail'])]
                    new.setdefault(kind, list(ms))[i] = {**ms[i], 'detail': g}
    return {**d, 'media': {**md, **new}} if new else d


# On a phone a desk screen cannot be read whatever its frame: 1440 px of interface in at most 358 px is a quarter of its
# size, letters 3 px high (measured on the seventeen software designs, 2026-11-18: every desk screen stood at 9–25 % at
# 390). The client's own phone capture of the same page can: 390 px of interface in 264 px is two thirds. So where the
# data has both captures of one page (`page`, lib/pipeline/product.mjs), a desk screen's picture is offered with the
# phone capture as its source up to NARROW px (a <picture>, no script; `display:contents`, so the design's own rules
# still lay the <img> out), drawn whole at PHONE_W px at most in a frame freed of the desk screen's proportion.
# A design says otherwise on the <img> itself: data-sw-ph="fit" where its frame is already upright on a phone (the
# capture fits inside it), data-sw-ph="no" where the picture is held and moved by the scroll at the desk screen's shape.
NARROW, PHONE_W = 720, 264
PHONE_CSS = ('picture.sw-ph{display:contents}@media(max-width:%dpx){picture.sw-ph>img{position:static!important;display:block!important;width:auto!important;height:auto!important;'
             'max-width:min(100%%,%dpx)!important;max-height:none!important;min-width:0!important;min-height:0!important;aspect-ratio:var(--ph)!important;object-fit:fill!important;'
             'margin-inline:auto!important;transform:none!important;border-radius:22px!important}'
             'picture.sw-ph.fit>img{max-height:100%%!important}:has(>picture.sw-ph:not(.fit)){aspect-ratio:auto!important;height:auto!important;max-height:none!important;min-height:0!important;flex-basis:auto!important}}') % (NARROW, PHONE_W)


def _phones(d, page):
    """each desk screen's <img> wrapped in a <picture> whose source, on a narrow screen, is the phone capture of the same page"""
    md = d.get('media') if isinstance(d.get('media'), dict) else {}
    by_page = {}
    for m in md.get('phones') or []:
        if isinstance(m, dict) and m.get('src') and m.get('page') and isinstance(m.get('w'), (int, float)) and isinstance(m.get('h'), (int, float)) and m['h'] > m['w']:
            by_page.setdefault(str(m['page']), m)
    pair = {str(m['src']): by_page[str(m['page'])] for m in md.get('screens') or [] if isinstance(m, dict) and m.get('src') and str(m.get('page')) in by_page}
    if not pair or '<picture class="sw-ph' in page:
        return page
    forms = {DEFAULT_MEDIA_BASE + f: ph for src, ph in pair.items() for f in {src, html.escape(src, quote=True)}}
    rx = re.compile(r'<img\b(?![^>]*data-sw-ph="no")[^>]*?\bsrc="(%s)"[^>]*>' % '|'.join(re.escape(k) for k in sorted(forms, key=len, reverse=True)))
    hit = []

    def sub(m):
        ph = forms[m.group(1)]
        hit.append(1)
        return '<picture class="sw-ph%s" style="--ph:%d/%d"><source media="(max-width:%dpx)" srcset="%s" width="%d" height="%d">%s</picture>' % (
            ' fit' if 'data-sw-ph="fit"' in m.group(0) else '', ph['w'], ph['h'], NARROW, html.escape(DEFAULT_MEDIA_BASE + str(ph['src']), quote=True), ph['w'], ph['h'], m.group(0))
    # never inside a <picture> the design wrote itself, a <noscript> or a script
    out, at = [], 0
    for blk in re.finditer(r'<(picture|script|style|noscript)\b.*?</\1\s*>', page, re.S | re.I):
        out.append(rx.sub(sub, page[at:blk.start()]))
        out.append(blk.group(0))
        at = blk.end()
    out.append(rx.sub(sub, page[at:]))
    if not hit:
        return page
    page = ''.join(out)
    j = page.find('>', page.find('<head'))
    return page[:j + 1] + '<style data-sw-ph>%s</style>' % PHONE_CSS + page[j + 1:] if j > 0 else page


def _readable(d, page):
    """the page's list of its product screens — each desk screen and phone screen the data names, with the width it was
    drawn in — for the gate, which holds every one of them to standing whole in its frame"""
    md = d.get('media') if isinstance(d.get('media'), dict) else {}
    maps = {}
    for kind in ('screens', 'phones'):
        for m in md.get(kind) or []:
            src = str((m or {}).get('src') or '') if isinstance(m, dict) else ''
            if src and isinstance(m.get('w'), (int, float)):
                # its width as the page set it: a desk screen was photographed in a page at most 1440 wide, a phone in
                # one 390 wide drawn at 2 (lib/pipeline/product.mjs)
                maps[src.rsplit('/', 1)[-1]] = {'c': min(int(m['w']), 1440) if kind == 'screens' else max(1, round(m['w'] / 2))}
    if not maps or 'id="sw-detail"' in page:
        return page
    k = page.rfind('</body>')
    if k < 0:
        return page
    blob = json.dumps(maps, separators=(',', ':')).replace('</', '<\\/')
    return page[:k] + '<script type="application/json" id="sw-detail">%s</script>' % blob + page[k:]


def render(slug, d, media_base=None, root=None, tablet=True):
    """One page from one template and one client's data. Pure: the same input gives the same bytes; `d` is not changed
    by the call as far as this function is concerned (the template gets the caller's dict — templates only read it)."""
    if not isinstance(d, dict):
        raise TemplateError('data must be a dict')
    page = _page(slug, d, root, tablet)
    if media_base is None or media_base == DEFAULT_MEDIA_BASE:
        return page
    return rebase(page, d, media_base)[0]


def media_used(slug, d, root=None):
    """The data's media paths the rendered page asks for — what a package has to carry, and nothing else."""
    return rebase(_page(slug, d, root), d, '')[1]


# ───────────────────────── what every template must hold before it is in the library (tests and the import script)
_FORBIDDEN = {'anthropic', 'openai', 'requests', 'httpx', 'urllib', 'http', 'socket', 'subprocess', 'aiohttp', 'os', 'pathlib',
              'shutil', 'random', 'time', 'datetime', 'secrets', 'uuid', 'tempfile', 'glob', 'io', 'pickle', 'ctypes', 'multiprocessing', 'threading'}
_VISIBLE = re.compile(r'<(script|style)\b.*?</\1\s*>', re.S | re.I)


def imports(slug, root=None):
    """top-level module names a template's render.py imports (read from its source, nothing is run)"""
    import ast
    tree = ast.parse((_dir(slug, root) / 'render.py').read_text(encoding='utf-8'))
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out.update(a.name.split('.')[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            out.add((n.module or '.').split('.')[0])
        elif isinstance(n, ast.Call) and getattr(n.func, 'id', '') in ('__import__', 'open', 'exec', 'eval', 'input'):
            out.add(n.func.id + '()')
    return out


def audit(slug, clients, root=None, limit_ms=50.0):
    """Problems of one template over the given clients ({name: data}); empty list = it may be in the library.
    Pure function with no reach outside (no network, files, clock or chance — so no model call can hide in it), each
    client renders to one page with exactly one h1 and no 'None'/'undefined' in what a visitor reads, in under
    `limit_ms` (best of five), twice the same, and every media path of the data can be re-based."""
    import copy
    import time
    bad = []
    try:
        reach = sorted(i for i in imports(slug, root) if i in _FORBIDDEN or i.endswith('()'))
    except (SyntaxError, OSError, TemplateError) as ex:
        return ['render.py cannot be read as a template: %s' % ex]
    if reach:
        bad.append('render.py reaches outside a pure function: ' + ', '.join(reach))
    try:
        mod = load(slug, root)
    except TemplateError as ex:
        return bad + [str(ex)]
    for name, d in clients.items():
        before = copy.deepcopy(d)
        try:
            mod.render(copy.deepcopy(d))                        # first call may build caches
            ms = None
            for _ in range(5):                                  # the render's own cost: the best of five, so a busy machine is not measured
                t = time.perf_counter()
                page = mod.render(d)
                took = (time.perf_counter() - t) * 1000
                ms = took if ms is None else min(ms, took)
        except Exception as ex:
            bad.append('%s: render raised %s: %s' % (name, type(ex).__name__, ex))
            continue
        if not isinstance(page, str) or '</html>' not in page.lower():
            bad.append('%s: not a whole page' % name)
            continue
        if d != before:
            bad.append('%s: render changed the data it was given' % name)
        if mod.render(copy.deepcopy(before)) != page:
            bad.append('%s: two renders of the same data differ' % name)
        if ms > limit_ms:
            bad.append('%s: %.1f ms, over %.0f' % (name, ms, limit_ms))
        h1 = len(re.findall(r'<h1[\s>]', page, re.I))
        if h1 != 1:
            bad.append('%s: %d h1' % (name, h1))
        seen = _VISIBLE.sub(' ', page)
        said = json.dumps(d, ensure_ascii=False)
        for word in ('None', 'undefined', 'NaN'):
            if re.search(r'(?<![\w-])%s(?![\w-])' % word, seen) and not re.search(r'(?<![\w-])%s(?![\w-])' % word, said):
                bad.append('%s: %r stands in the page' % (name, word))
        moved, used = rebase(page, d, 'MEDIA-BASE/')
        left = [p for p in media_paths(d) if (DEFAULT_MEDIA_BASE + p) in moved or (DEFAULT_MEDIA_BASE + html.escape(p, quote=True)) in moved]
        if left:
            bad.append('%s: media not re-based: %s' % (name, ', '.join(left[:3])))
        if DEFAULT_MEDIA_BASE in _VISIBLE.sub(' ', moved):
            bad.append('%s: a path outside the data stays behind %r' % (name, DEFAULT_MEDIA_BASE))
    return bad


if __name__ == '__main__':                                    # python3 lib/templates/registry.py [slug data.json [media_base]]
    if len(sys.argv) < 3:
        for t in list_templates():
            print('%-14s %s' % (t['slug'], 'selectable' if t['selectable'] else 'not selectable — ' + t['why']))
    else:
        sys.stdout.write(render(sys.argv[1], json.loads(Path(sys.argv[2]).read_text(encoding='utf-8')), sys.argv[3] if len(sys.argv) > 3 else None))
