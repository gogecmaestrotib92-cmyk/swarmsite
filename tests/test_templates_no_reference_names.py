"""Owner's rule (2026-11-12): a visitor never sees the name of a reference site a template was rebuilt from. Every
template, rendered for every test client (and with made pictures where the library gives them), and its package: no
template's slug and no word of a reference's name or domain in the page (text, comments, ids, classes, data-attributes,
meta), in the package's file names or in its text files. The job JSON the web app reads is tested in
tests/design-names.mjs and tests/templates-job.mjs."""
import importlib.util
import json
import re
import sys
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
PI = _load('swarmsite_templates_pictures', ROOT / 'lib' / 'templates' / 'pictures.py')
NAMES = json.loads((ROOT / 'tests' / 'fixtures' / 'reference_names.json').read_text(encoding='utf-8'))
SLUGS = sorted(t['slug'] for t in R.list_templates())
WORDS = sorted({w.lower() for k, v in NAMES.items() if k != '_' for w in v} | set(SLUGS))
CLIENTS = {f.stem: json.loads(f.read_text(encoding='utf-8')) for f in sorted(FIX.glob('*.json'))}
CLIENTS = {k: v for k, v in CLIENTS.items() if isinstance(v, dict) and v.get('brand')}


def leaks(text, client):
    """the reference words in `text` that the client's own data does not carry (a client may be called Griffin)"""
    own = json.dumps(client, ensure_ascii=False).lower()
    return sorted({w for w in WORDS if w not in own and re.search(r'(?<![a-z0-9])' + re.escape(w) + r'(?![a-z0-9])', text, re.I)})


def test_every_template_has_its_reference_names_listed():
    assert SLUGS and set(SLUGS) <= set(NAMES), 'a template without its reference names in tests/fixtures/reference_names.json: %s' % sorted(set(SLUGS) - set(NAMES))


def variants(client):
    yield 'as given', client
    three = PI.pick_three(client) if PI.root_of() else []
    for made in three[:1]:
        yield 'with made pictures', {**client, 'media': {**(client.get('media') or {}), 'made': made}}


@pytest.mark.parametrize('slug', SLUGS)
def test_no_rendered_page_names_a_reference(slug):
    found = {}
    for name, client in CLIENTS.items():
        for how, d in variants(client):
            for base in ('', 'https://storage.example/previews/j/t/'):
                hit = leaks(R.render(slug, d, base), client)
                if hit:
                    found['%s %s' % (name, how)] = hit
    assert not found, '%s names a reference in its page: %s' % (slug, found)


def _fonts(url):
    if 'googleapis' in url:
        return b"@font-face { font-family: 'X'; font-weight: 400; src: url(https://fonts.gstatic.com/s/x/lat.woff2) format('woff2'); unicode-range: U+0000-00FF; }"
    return b'wOF2'


@pytest.mark.parametrize('slug', SLUGS)
def test_no_package_names_a_reference_in_a_file_name_or_a_file(slug, tmp_path):
    name, client = 'tallyfern', CLIENTS['tallyfern']
    S.stand_ins(client, tmp_path / 'src')
    for p in R.media_paths(client):
        if not (tmp_path / 'src' / p).exists():
            (tmp_path / 'src' / p).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / 'src' / p).write_bytes(b'\x00')
    rep = P.build(slug, client, tmp_path / 'src', tmp_path / 'design.zip', fetch=_fonts)
    with zipfile.ZipFile(rep['zip']) as z:
        names = z.namelist()
        assert not leaks(' '.join(names), client), names
        for n in names:
            if n.endswith(('.html', '.txt', '.json', '.css', '.js', '.svg')):
                hit = leaks(z.read(n).decode('utf-8', 'replace'), client)
                assert not hit, '%s: %s names %s' % (slug, n, hit)
