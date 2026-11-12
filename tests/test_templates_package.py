"""The package: the preview's own page with its media and its fonts beside it, asking the network for nothing — and
refused when it does not look like the preview. Built without the network here (a stand-in font service); the two
real pairs (griffin × the product, maze × the restaurant) are built with Google's files and compared in Chrome where
the network and Chrome are there."""
import importlib.util
import json
import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / 'tests' / 'fixtures' / 'templates'


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load('swarmsite_templates_registry', ROOT / 'lib' / 'templates' / 'registry.py')
S = _load('swarmsite_templates_stress', ROOT / 'lib' / 'templates' / 'stress.py')
P = _load('swarmsite_templates_package', ROOT / 'lib' / 'templates' / 'package.py')
PRODUCT, PLACE = (json.loads((FIX / (n + '.json')).read_text(encoding='utf-8')) for n in ('tallyfern', 'casaolmo'))
CSS = """/* cyrillic */
@font-face { font-family: 'Inter Tight'; font-style: normal; font-weight: 300; src: url(https://fonts.gstatic.com/s/x/cyr.woff2) format('woff2'); unicode-range: U+0301, U+0400-045F; }
/* latin */
@font-face { font-family: 'Inter Tight'; font-style: normal; font-weight: 300; src: url(https://fonts.gstatic.com/s/x/lat.woff2) format('woff2'); unicode-range: U+0000-00FF, U+0131; }
/* latin, another weight */
@font-face { font-family: 'Inter Tight'; font-style: normal; font-weight: 400; src: url(https://fonts.gstatic.com/s/x/lat400.woff2) format('woff2'); unicode-range: U+0000-00FF; }
"""


def fonts(asked):
    def fetch(url):
        asked.append(url)
        return CSS.encode() if 'googleapis' in url else b'wOF2' + url.encode()
    return fetch


HAS_BROWSER = bool(shutil.which('node')) and os.path.exists(os.environ.get('CHROME_PATH') or '/usr/bin/google-chrome')


def online():
    try:
        urllib.request.urlopen(urllib.request.Request('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400', headers={'User-Agent': P.UA}), timeout=6).read(64)
        return True
    except Exception:
        return False


@pytest.mark.parametrize('slug,client', [('griffin', PRODUCT), ('maze', PLACE)])
def test_the_zip_holds_the_page_its_media_its_fonts_and_asks_for_nothing_outside(tmp_path, slug, client):
    S.stand_ins(client, tmp_path / 'src')
    for p in R.media_paths(client):                                   # the film is a file too
        if p.endswith('.mp4'):
            (tmp_path / 'src' / p).write_bytes(b'\x00\x00\x00\x18ftypmp42')
    asked = []
    rep = P.build(slug, {**client, '_media': {'not': 'in the package'}}, tmp_path / 'src', tmp_path / 'out' / 'site.zip', fetch=fonts(asked))
    with zipfile.ZipFile(rep['zip']) as z:
        names = sorted(z.namelist())
        page = z.read('index.html').decode('utf-8')
        data = json.loads(z.read('data.json'))
        readme = z.read('README.txt').decode('utf-8')
        assert z.testzip() is None
    assert names == rep['files'] and {'index.html', 'data.json', 'README.txt'} <= set(names)
    # the same render as the preview: the template's own page with only the addresses of media and fonts changed
    own = R.render(slug, client, '')
    strip = lambda s: __import__('re').sub(r'<link\b[^>]*fonts\.(?:googleapis|gstatic)\.com[^>]*>|<style data-fonts="local">.*?</style>', '', s, flags=__import__('re').S)
    assert strip(page) == strip(own)
    # media: only what the page asks for, each at the address the page uses
    used = R.media_used(slug, client)
    assert rep['media'] == sorted(used) and all(n in names for n in used) and all(('"%s"' % n in page) or (n in page) for n in used)
    assert len(used) <= len(R.media_paths(client)) and all(n.startswith('media/') for n in rep['media'])
    # fonts: the stylesheet is in the page, its files are in fonts/, only the faces for letters the page has
    assert 'fonts.googleapis.com' not in page and 'fonts.gstatic.com' not in page and '<style data-fonts="local">' in page
    assert len(rep['fonts']) == 2 and all(n.startswith('fonts/') and n.endswith('.woff2') and 'url(%s)' % n in page for n in rep['fonts'])
    assert not any('cyr.woff2' in u for u in asked), 'no Cyrillic on the page: its face is not fetched and not packed'
    assert P.outside(page) == [], 'nothing left that a browser would fetch from outside'
    assert 'href="https://' in page, 'the client\'s own links stay links'
    assert data == {k: v for k, v in client.items() if not k.startswith('_')} and client['brand']['name'] in readme and slug in readme
    # the same input gives the same zip
    again = P.build(slug, client, tmp_path / 'src', tmp_path / 'out' / 'again.zip', fetch=fonts([]))
    assert Path(again['zip']).read_bytes() == Path(rep['zip']).read_bytes()
    # and it unpacks into an empty folder only
    P.unpack(rep['zip'], tmp_path / 'unpacked')
    assert (tmp_path / 'unpacked' / 'index.html').is_file() and all((tmp_path / 'unpacked' / n).is_file() for n in names)
    with pytest.raises(P.PackageError):
        P.unpack(rep['zip'], tmp_path / 'unpacked')


def test_a_package_that_cannot_be_whole_is_refused(tmp_path):
    S.stand_ins(PLACE, tmp_path / 'src')
    used = R.media_used('griffin', PLACE)
    (tmp_path / 'src' / used[0]).unlink()
    with pytest.raises(P.PackageError, match='which is not in'):
        P.build('griffin', PLACE, tmp_path / 'src', tmp_path / 'a.zip', fetch=fonts([]))
    S.stand_ins(PLACE, tmp_path / 'src')
    with pytest.raises(P.PackageError, match='no face'):
        P.build('griffin', PLACE, tmp_path / 'src', tmp_path / 'b.zip', fetch=lambda url: b'/* nothing */')
    with pytest.raises(P.PackageError, match='could not fetch|not a Google Fonts'):
        P.fetch_cached('https://elsewhere.example/font.css', tmp_path / 'cache')
    assert not (tmp_path / 'a.zip').exists() and not (tmp_path / 'b.zip').exists()
    # a template that asks another host for a script or a picture: named, and refused
    lib = tmp_path / 'lib' / 'leaky'
    lib.mkdir(parents=True)
    lib.joinpath('render.py').write_text("def render(d):\n    return '<!doctype html><html><head><script src=\"https://cdn.example/x.js\"></script><style>body{background:url(//img.example/b.png)}</style></head><body><h1>' + d['hero']['title'] + '</h1><a href=\"https://client.example/\">home</a><img src=\"https://img.example/p.jpg\"></body></html>'\n", encoding='utf-8')
    with pytest.raises(P.PackageError) as ex:
        P.build('leaky', PLACE, tmp_path / 'src', tmp_path / 'c.zip', root=tmp_path / 'lib')
    assert 'cdn.example/x.js' in str(ex.value) and 'img.example/b.png' in str(ex.value) and 'img.example/p.jpg' in str(ex.value) and 'client.example' not in str(ex.value)
    assert P.outside('<a href="https://a.example">x</a><link rel="canonical" href="https://a.example/"><form action="https://a.example/send"></form>') == []
    assert P._in_range('U+0000-00FF, U+0131', {0x41}) and not P._in_range('U+0400-045F', {0x41}) and P._in_range('U+4??', {0x430}) and P._in_range('something else', {1})
    evil = tmp_path / 'evil.zip'
    with zipfile.ZipFile(evil, 'w') as z:
        z.writestr('../outside.txt', 'x')
    with pytest.raises(P.PackageError):
        P.unpack(evil, tmp_path / 'e')


def test_fonts_are_fetched_once_and_kept(tmp_path, monkeypatch):
    calls = []

    class Reply:
        def __init__(self, data): self.data = data
        def read(self): return self.data
        def __enter__(self): return self
        def __exit__(self, *a): return False
    monkeypatch.setattr(P.urllib.request, 'urlopen', lambda req, timeout=0: (calls.append(req.full_url), Reply(b'bytes of a face'))[1])
    url = 'https://fonts.gstatic.com/s/x/lat.woff2'
    assert P.fetch_cached(url, tmp_path) == b'bytes of a face' and P.fetch_cached(url, tmp_path) == b'bytes of a face'
    assert calls == [url] and len(list(tmp_path.iterdir())) == 1
    # Google answers a Mac with other font files than every other system; what was kept under another UA is not reused
    monkeypatch.setattr(P, 'UA', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/126.0')
    P.fetch_cached(url, tmp_path)
    assert calls == [url, url] and len(list(tmp_path.iterdir())) == 2


LINUX_WORKER_UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/140.0.0.0 Safari/537.36'


def test_the_package_carries_the_font_files_the_worker_browser_loads_for_the_preview():
    """The production worker compares in Linux headless Chromium. A package built with the files Google gives a Mac
    (unhinted) was drawn 28 px shorter there than the preview (hinted) and refused on every screen (job bc69c9d1,
    2026-11-12). The package asks with a UA that gets the same files as that browser."""
    assert 'Macintosh' not in P.UA and 'Mac OS' not in P.UA
    if not online():
        pytest.skip('Google Fonts cannot be reached from here')
    import re
    css = 'https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400&family=Geist+Mono:wght@400;600&display=swap'
    files = lambda ua: re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', urllib.request.urlopen(urllib.request.Request(css, headers={'User-Agent': ua}), timeout=10).read().decode())
    ours = files(P.UA)
    assert ours and ours == files(LINUX_WORKER_UA)


@pytest.mark.skipif(not HAS_BROWSER, reason='needs node and Chrome (CHROME_PATH)')
def test_a_package_that_does_not_look_like_the_preview_is_refused(tmp_path):
    """Offline, with a still made-up template: the package of the same page passes; one whose page was changed, one
    that asks the network for something, and one with a picture missing are refused, and the answer says why."""
    lib = tmp_path / 'lib' / 'still'
    lib.mkdir(parents=True)
    lib.joinpath('render.py').write_text(
        "def render(d):\n    return ('<!doctype html><html lang=\"en\"><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><style>body{margin:0;font:18px/1.5 Arial;color:#111;background:#fff}"
        "section{padding:60px 24px;min-height:700px}img{display:block;max-width:100%;height:auto}</style></head><body><section><h1>' + d['hero']['title'] + '</h1><p>' + d['hero']['text'] + '</p>"
        "<img src=\"../../' + d['media']['photos'][0]['src'] + '\" width=\"480\" height=\"322\" alt=\"\"></section><section style=\"background:#111;color:#eee\"><p>' + d['close']['title'] + '</p></section></body></html>')\n", encoding='utf-8')
    S.stand_ins(PLACE, tmp_path / 'src')
    preview = tmp_path / 'preview.html'
    preview.write_text(R.render('still', PLACE, (tmp_path / 'src').resolve().as_uri() + '/', root=tmp_path / 'lib'), encoding='utf-8')
    rep = P.build('still', PLACE, tmp_path / 'src', tmp_path / 'site.zip', root=tmp_path / 'lib')
    assert rep['fonts'] == [] and rep['media'] == ['media/casaolmo/arroz.jpg']
    res = P.verify(preview, rep['zip'], tmp_path / 'w1')
    assert res['ok'] and res['why'] == [] and res['outside'] == [] and [w['at'] for w in res['widths']] == ['d', 'm'] and all(w['worst'] == 0 and w['screens'] >= 2 for w in res['widths']), res

    def tampered(name, change):
        z2 = tmp_path / (name + '.zip')
        with zipfile.ZipFile(rep['zip']) as a, zipfile.ZipFile(z2, 'w') as b:
            for n in a.namelist():
                data = change(n, a.read(n))
                if data is not None:
                    b.writestr(n, data)
        return P.verify(preview, z2, tmp_path / ('w-' + name))
    res = tampered('recoloured', lambda n, x: x.replace(b'background:#111;color:#eee', b'background:#b00;color:#eee') if n == 'index.html' else x)
    assert not res['ok'] and any('screens differ' in w for w in res['why']), res['why']
    res = tampered('taller', lambda n, x: x.replace(b'min-height:700px', b'min-height:760px') if n == 'index.html' else x)
    assert not res['ok'] and any('px high' in w for w in res['why']), res['why']
    res = tampered('calls-out', lambda n, x: x.replace(b'</body>', b'<img src="https://tracker.example/p.gif" width="1" height="1" alt=""></body>') if n == 'index.html' else x)
    assert not res['ok'] and any('outside itself' in w and 'tracker.example' in w for w in res['why']), res['why']
    res = tampered('no-picture', lambda n, x: None if n.endswith('arroz.jpg') else x)
    assert not res['ok'] and any('did not load' in w for w in res['why']), res['why']
    gone = P.verify(preview, tmp_path / 'not-there.zip', tmp_path / 'w9')
    assert gone['ok'] is False and gone['why'], 'a package that cannot be opened is refused, not passed'


@pytest.mark.skipif(not HAS_BROWSER, reason='needs node and Chrome (CHROME_PATH)')
@pytest.mark.parametrize('slug,client', [('griffin', 'tallyfern'), ('maze', 'casaolmo')])
def test_the_real_templates_package_looks_like_its_preview(tmp_path, slug, client):
    """griffin × the product and maze × the restaurant, with Google's own font files: built, unpacked into an empty
    folder, opened offline at 1440 and 390 and compared with the preview screen by screen."""
    if not online():
        pytest.skip('Google Fonts cannot be reached from here')
    d = json.loads((FIX / (client + '.json')).read_text(encoding='utf-8'))
    S.stand_ins(d, tmp_path / 'src')
    for p in R.media_paths(d):
        if p.endswith('.mp4'):
            (tmp_path / 'src' / p).write_bytes(b'')
    preview = tmp_path / 'preview.html'
    preview.write_text(R.render(slug, d, (tmp_path / 'src').resolve().as_uri() + '/'), encoding='utf-8')
    rep = P.build(slug, d, tmp_path / 'src', tmp_path / 'site.zip')
    assert rep['fonts'] and P.outside(rep['page']) == []
    res = P.verify(preview, rep['zip'], tmp_path / 'work')
    assert res['ok'], res['why']
    assert res['outside'] == [] and all(w['height_preview'] == w['height_package'] and w['worst'] <= 0.005 and w['fonts_package'] for w in res['widths'])
