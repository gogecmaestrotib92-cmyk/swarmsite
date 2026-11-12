"""package.py — the package a client downloads: the page of the preview, whole, asking the network for nothing.

    build(slug, d, media_root, out_zip, cache=None, fetch=None) -> {'zip', 'files', 'media', 'fonts', 'bytes', 'page'}
    verify(preview, out_zip, workdir, tolerance=0.005) -> the comparison (lib/qa/package_compare.mjs); ['ok'] says deliver or refuse
    python3 lib/templates/package.py <slug> <data.json> <media root> <out.zip> [--verify]

The zip holds
    index.html   the SAME render as the preview (registry.render), its media beside it under media/
    media/…      only the files the page asks for
    fonts/…      the files of the Google Fonts stylesheet the page links, for the letters the page has; the stylesheet
                 itself is written into the page as @font-face rules that point at them
    data.json    the client's data the page was rendered from
    README.txt
and no address outside itself that a browser would fetch (links to the client's own pages stay links). build()
refuses — PackageError — when a picture the page asks for is not in `media_root`, when a font cannot be had, or
when any outside request is left in the page.

Identical look is not assumed, it is measured: verify() unpacks the zip into an empty folder, opens it offline in
headless Chrome at 1440 and 390 beside the preview and compares screenshots screen by screen; a package that
differs by more than the tolerance, is of another height, loads other faces or asks for anything outside is refused.

Fonts are fetched once and kept (cache: $SWARMSITE_FONT_CACHE, else a folder in the system's temp directory). This is
the only network use of the template path, and it happens when a package is built, never when a page is rendered.
"""
import hashlib
import html
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / 'qa' / 'package_compare.mjs'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'   # the stylesheet a current browser gets: woff2, split by script
FONT_HOSTS = ('https://fonts.googleapis.com/', 'https://fonts.gstatic.com/')
README = """%(name)s — your new page

index.html   open it in a browser; put the whole folder on any web host as it is
media/       the pictures and films of the page
fonts/       the typefaces of the page (open licences; they travel with the page)
data.json    the words, links and pictures the page was made from

The page asks the internet for nothing: everything it shows is in this folder.
Template: %(slug)s. Made with Swarmsite.
"""


class PackageError(Exception):
    """the package cannot be built as promised"""


def _registry():
    key = 'swarmsite_templates_registry'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, HERE / 'registry.py')
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


def font_cache():
    d = Path(os.environ.get('SWARMSITE_FONT_CACHE') or Path(tempfile.gettempdir()) / 'swarmsite-fonts')
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch_cached(url, cache=None):
    """the bytes at a Google Fonts address, from the cache or fetched once"""
    if not url.startswith(FONT_HOSTS):
        raise PackageError('not a Google Fonts address: %s' % url[:80])
    f = Path(cache or font_cache()) / hashlib.sha256(url.encode()).hexdigest()[:32]
    if f.is_file() and f.stat().st_size:
        return f.read_bytes()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
            data = r.read()
    except Exception as ex:
        raise PackageError('could not fetch %s: %s' % (url[:80], ex)) from ex
    if not data:
        raise PackageError('nothing at %s' % url[:80])
    tmp = f.with_suffix('.part')
    tmp.write_bytes(data)
    tmp.replace(f)
    return data


def _in_range(spec, used):
    """does a unicode-range (U+0460-052F, U+20B4, U+4??) hold one of the code points the page uses"""
    for part in spec.split(','):
        m = re.match(r'^\s*U\+([0-9A-Fa-f?]{1,6})(?:-([0-9A-Fa-f]{1,6}))?\s*$', part)
        if not m:
            return True                                              # a range this cannot read: keep the face
        lo = int(m.group(1).replace('?', '0'), 16)
        hi = int(m.group(2), 16) if m.group(2) else int(m.group(1).replace('?', 'F'), 16)
        if any(lo <= c <= hi for c in used):
            return True
    return False


def localise_fonts(page, fetch=None, cache=None):
    """(page, {'fonts/<file>': bytes}) — every Google Fonts stylesheet the page links, written into the page as
    @font-face rules whose files are in fonts/. Only the faces for letters the page has are kept: the ones a browser
    would have fetched for it."""
    fetch = fetch or (lambda url: fetch_cached(url, cache))
    used = {ord(c) for c in html.unescape(page)}
    files = {}

    def one(m):
        tag = m.group(0)
        href = re.search(r'href=(["\'])(.*?)\1', tag)
        if not href or 'stylesheet' not in tag.lower():
            return ''                                                # a preconnect to the font hosts: nothing to connect to any more
        css = fetch(html.unescape(href.group(2)))
        css = css.decode('utf-8') if isinstance(css, bytes) else css
        rules = []
        for block in re.findall(r'@font-face\s*\{[^}]*\}', css):
            rng = re.search(r'unicode-range:\s*([^;}]+)', block)
            if rng and not _in_range(rng.group(1), used):
                continue

            def local(u):
                url = u.group(2)
                ext = (re.search(r'\.(woff2|woff|ttf|otf)(?:$|\?)', url) or [None, 'woff2'])[1]
                name = 'fonts/%s.%s' % (hashlib.sha256(url.encode()).hexdigest()[:16], ext)
                files[name] = fetch(url)
                return 'url(%s)' % name
            rules.append(re.sub(r'\s+', ' ', re.sub(r'url\((["\']?)(https://fonts\.gstatic\.com/[^)"\']+)\1\)', local, block)))
        if not rules:
            raise PackageError('the stylesheet %s gave no face for the page' % href.group(2)[:80])
        return '<style data-fonts="local">' + ''.join(rules) + '</style>'
    page = re.sub(r'<link\b[^>]*https://fonts\.(?:googleapis|gstatic)\.com[^>]*>', one, page)
    return page, files


def outside(page):
    """every address in the page that a browser would fetch from outside the package (a link a visitor may click is
    not one)"""
    found = []
    for tag, attrs in re.findall(r'<(\w+)\b([^>]*)>', re.sub(r'<(script|style)\b[^>]*>.*?</\1>', lambda m: m.group(0).split('>')[0] + '>', page, flags=re.S | re.I)):
        if tag.lower() in ('a', 'area'):
            continue
        if tag.lower() == 'link' and re.search(r'rel=["\']?(?:canonical|alternate|me|author|license|next|prev)\b', attrs, re.I):
            continue
        for m in re.finditer(r'\b(?:src|href|poster|srcset|data|action)=(["\'])\s*((?:https?:)?//[^"\']+)\1', attrs, re.I):
            if tag.lower() != 'form':
                found.append(html.unescape(m.group(2))[:120])
    for block in re.findall(r'<style\b[^>]*>(.*?)</style>', page, flags=re.S | re.I) + re.findall(r'style=(["\'])(.*?)\1', page, flags=re.S):
        css = block if isinstance(block, str) else block[1]
        found += [u[:120] for u in re.findall(r'url\(\s*["\']?((?:https?:)?//[^)"\']+)', css)] + [u[:120] for u in re.findall(r'@import\s+["\']((?:https?:)?//[^"\']+)', css)]
    return list(dict.fromkeys(found))


def build(slug, d, media_root, out_zip, cache=None, fetch=None, root=None):
    R = _registry()
    data = {k: v for k, v in d.items() if not k.startswith('_')}
    used = R.media_used(slug, data, root)
    nested = all(p.startswith('media/') for p in used)
    base = '' if nested else 'media/'
    page = R.render(slug, data, base, root=root)
    media = {}
    for p in used:
        if '..' in Path(p).parts or Path(p).is_absolute():
            raise PackageError('a media path that leaves the package: %s' % p)
        f = Path(media_root) / p
        if not f.is_file():
            raise PackageError('the page asks for %s, which is not in %s' % (p, media_root))
        media[base + p] = f.read_bytes()
    page, fonts = localise_fonts(page, fetch, cache)
    left = outside(page)
    if left:
        raise PackageError('the page still asks outside the package for: ' + ', '.join(left[:5]))
    name = (data.get('brand') or {}).get('name') or 'Your page'
    files = {'index.html': page.encode('utf-8'), 'data.json': (json.dumps(data, ensure_ascii=False, indent=1) + '\n').encode('utf-8'),
             'README.txt': (README % {'name': name, 'slug': slug}).encode('utf-8'), **media, **fonts}
    out_zip = Path(out_zip)
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as z:      # the same input gives the same zip, byte for byte
        for n in sorted(files):
            info = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED if n.rsplit('.', 1)[-1].lower() in ('jpg', 'jpeg', 'png', 'webp', 'avif', 'mp4', 'webm', 'woff2', 'woff') else zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, files[n])
    return {'zip': str(out_zip), 'files': sorted(files), 'media': sorted(media), 'fonts': sorted(fonts), 'bytes': out_zip.stat().st_size, 'page': page}


def unpack(out_zip, folder):
    """the zip into an EMPTY folder, nothing written outside it"""
    folder = Path(folder)
    if folder.exists() and any(folder.iterdir()):
        raise PackageError('%s is not empty' % folder)
    folder.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip) as z:
        for n in z.namelist():
            if n.startswith('/') or '..' in Path(n).parts:
                raise PackageError('a path in the zip that leaves the folder: %s' % n)
        z.extractall(folder)
    return folder


def verify(preview, out_zip, workdir, tolerance=0.005, shots=None, timeout=600):
    """Unpack into workdir/package (must be empty), open it offline beside the preview, compare. The result's 'ok' is
    the verdict: deliver, or refuse. A comparison that could not be made is a refusal."""
    try:
        folder = unpack(out_zip, Path(workdir) / 'package')
    except (PackageError, OSError, zipfile.BadZipFile) as ex:
        return {'ok': False, 'why': ['the package could not be unpacked: %s' % ex]}
    cmd = ['node', str(TOOL), str(preview), str(folder / 'index.html'), '--tolerance', str(tolerance)] + (['--shots', str(shots)] if shots else [])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        res = json.loads(r.stdout.strip().splitlines()[-1])
        assert isinstance(res.get('ok'), bool)
    except Exception as ex:
        err = locals().get('r')
        return {'ok': False, 'why': ['the comparison could not be made: %s %s' % (type(ex).__name__, (err.stderr if err is not None else str(ex))[-300:])]}
    return res


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) != 4:
        raise SystemExit(__doc__)
    slug, data_file, media_root, out = a
    d = json.loads(Path(data_file).read_text(encoding='utf-8'))
    try:
        rep = build(slug, d, media_root, out)
    except PackageError as ex:
        raise SystemExit('refused: %s' % ex)
    print('%s: %d files, %d media, %d font files, %.0f kB' % (rep['zip'], len(rep['files']), len(rep['media']), len(rep['fonts']), rep['bytes'] / 1000))
    if '--verify' in sys.argv:
        with tempfile.TemporaryDirectory(prefix='package-') as tmp:
            prev = Path(tmp) / 'preview.html'
            prev.write_text(_registry().render(slug, {k: v for k, v in d.items() if not k.startswith('_')}, Path(media_root).resolve().as_uri() + '/'), encoding='utf-8')
            res = verify(prev, out, tmp)
        print(json.dumps({k: v for k, v in res.items() if k != 'widths'}, ensure_ascii=False))
        for w in res.get('widths') or []:
            print('  %s: %d screens, worst %.2f %% of pixels, heights %s / %s' % (w['at'], w['screens'], w['worst'] * 100, w['height_preview'], w['height_package']))
        sys.exit(0 if res['ok'] else 1)
