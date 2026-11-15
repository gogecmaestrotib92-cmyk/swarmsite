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


def _page(slug, d, root=None):
    """the template's page with what the template has no place for added under its sections (more.py): the client's
    leftover sections in their own words, and the photographs the page did not ask for"""
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
    page = _readable(d, page)
    return page


# A product's screen shown far under its own size is a smear (letters 3 px high), whatever the template: the windows
# design, then linearity, fluently, butter, griffin, supaste and dock were each measured showing screens at 13–44 % of
# their size on two software sites (owner, at full size beside the reference, 2026-11-15). Where a screen's box comes
# out under LOW of the screen's own width, the picture is shown at READ of its width inside the same box, moved to the
# part capture's map of detail (`detail`) says is busiest for that box's shape. At its own pixels the crop was too
# tight — half a headline in a small card read as broken text — so the same file is given that size (srcset with its
# own pixel width and `sizes`: the only candidate, so every browser draws it alike; sharp, nothing new to send), drawn
# with object-fit: none (a crop), and the box is held at the size the template gave it. Measured again on every resize, so a phone width gets its own crop.
LOW, READ = .45, .6
READABLE = ('(()=>{const D=JSON.parse(document.getElementById("sw-detail").textContent),LOW=%s,READ=%s;'
            'const name=s=>{const m=(s||"").match(/([^\\/?#]+)(?:[?#].*)?$/);return m&&m[1]};'
            'const busiest=(g,fw,fh)=>{const R=g.length,C=g[0].length,w=Math.max(1,Math.min(C,Math.round(fw*C))),h=Math.max(1,Math.min(R,Math.round(fh*R)));let b=-1,bx=0,by=0;'
            'for(let y=0;y+h<=R;y++)for(let x=0;x+w<=C;x++){let v=0;for(let r=y;r<y+h;r++)for(let c=x;c<x+w;c++)v+=g[r][c];if(v>b){b=v;bx=x;by=y}}return[(bx+w/2)/C,(by+h/2)/R]};'
            'const undo=im=>{if(!im.dataset.swDt)return;const o=JSON.parse(im.dataset.swDt);for(const k in o)im.style[k]=o[k];'
            'for(const[a,k]of[["srcset","swSs"],["sizes","swSz"]])if(im.dataset[k]!==undefined){if(im.dataset[k])im.setAttribute(a,im.dataset[k]);else im.removeAttribute(a);delete im.dataset[k]}delete im.dataset.swDt};'
            'const fit=()=>{const ims=[...document.images].filter(im=>D[name(im.getAttribute("src"))]&&im.naturalWidth);ims.forEach(undo);'
            'for(const im of ims){const e=D[name(im.getAttribute("src"))];'
            'if(!im.dataset.swNw){im.dataset.swNw=im.naturalWidth;im.dataset.swNh=im.naturalHeight}'
            'const bw=im.clientWidth,bh=im.clientHeight,nw=+im.dataset.swNw,nh=+im.dataset.swNh;'
            'if(bw<80||bh<60||bw/e.c>=LOW)continue;'
            'const d=Math.min(nw/(READ*e.c),nw/bw,nh/bh);if(d<=1.01&&nw<bw*1.2)continue;'
            'const iw=nw/d,ih=nh/d,[fx,fy]=busiest(e.g,bw/iw,bh/ih),x=Math.min(0,Math.max(bw-iw,bw/2-fx*iw)),y=Math.min(0,Math.max(bh-ih,bh/2-fy*ih));'
            'const s=im.style;im.dataset.swDt=JSON.stringify({objectFit:s.objectFit,objectPosition:s.objectPosition,width:s.width,height:s.height,maxWidth:s.maxWidth});'
            'im.dataset.swSs=im.getAttribute("srcset")||"";im.dataset.swSz=im.getAttribute("sizes")||"";'
            's.width=bw+"px";s.height=bh+"px";s.maxWidth="none";s.objectFit="none";s.objectPosition=Math.round(x)+"px "+Math.round(y)+"px";'
            'im.sizes=Math.round(iw)+"px";im.srcset=(im.currentSrc||im.src)+" "+nw+"w"}};'
            'let t;const later=()=>{clearTimeout(t);t=setTimeout(fit,120)};'
            'if(document.readyState==="complete")fit();else addEventListener("load",fit);addEventListener("resize",later);'
            'for(const im of document.images)if(!im.complete)im.addEventListener("load",later,{once:true})})()') % (LOW, READ)


def _readable(d, page):
    """the map of detail of each desk screen the data names, and the few lines that use it (see LOW above)"""
    md = d.get('media') if isinstance(d.get('media'), dict) else {}
    maps = {}
    for m in md.get('screens') or []:
        g, src = m.get('detail') if isinstance(m, dict) else None, str((m or {}).get('src') or '')
        if g and src and isinstance(m.get('w'), (int, float)):
            # its width as the page set it: a desk screen was photographed in a page at most 1440 wide
            maps[src.rsplit('/', 1)[-1]] = {'c': min(int(m['w']), 1440), 'g': g}
    if not maps or 'id="sw-detail"' in page:
        return page
    k = page.rfind('</body>')
    if k < 0:
        return page
    blob = json.dumps(maps, separators=(',', ':')).replace('</', '<\\/')
    return page[:k] + '<script type="application/json" id="sw-detail">%s</script><script data-sw-detail>%s</script>' % (blob, READABLE) + page[k:]


def render(slug, d, media_base=None, root=None):
    """One page from one template and one client's data. Pure: the same input gives the same bytes; `d` is not changed
    by the call as far as this function is concerned (the template gets the caller's dict — templates only read it)."""
    if not isinstance(d, dict):
        raise TemplateError('data must be a dict')
    page = _page(slug, d, root)
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
