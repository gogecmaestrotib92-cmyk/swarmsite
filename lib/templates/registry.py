"""registry.py — the library of reference templates: list them, load one, render a client's data through it.

A template is a folder `lib/templates/<slug>/` holding `render.py` with one pure function `render(d: dict) -> str`
(a whole page, inline CSS and JS, no client and no model call — see CONTRACT in the research folder and each NOTES.md),
`NOTES.md` (what was measured on the reference and how the data fills it) and, once it has been measured on the test
clients, `needs.json` (the least a client must have for the template to be offered). `recipes.py` beside this file is the
OLD pipeline's recipe table and has nothing to do with these folders.

    list_templates() -> [{'slug', 'has_needs', 'needs', 'selectable', 'why'}]   every folder with a render.py
    load(slug)       -> the template's module (cached)
    needs(slug)      -> its needs.json as a dict, or None
    render(slug, d, media_base=None) -> str

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


def render(slug, d, media_base=None, root=None):
    """One page from one template and one client's data. Pure: the same input gives the same bytes; `d` is not changed
    by the call as far as this function is concerned (the template gets the caller's dict — templates only read it)."""
    if not isinstance(d, dict):
        raise TemplateError('data must be a dict')
    page = load(slug, root).render(d)
    if not isinstance(page, str):
        raise TemplateError('template %r returned %s, not a page' % (slug, type(page).__name__))
    if media_base is None or media_base == DEFAULT_MEDIA_BASE:
        return page
    return rebase(page, d, media_base)[0]


def media_used(slug, d, root=None):
    """The data's media paths the rendered page asks for — what a package has to carry, and nothing else."""
    return rebase(load(slug, root).render(d), d, '')[1]


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
