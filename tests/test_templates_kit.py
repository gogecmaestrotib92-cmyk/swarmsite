"""kit.py — the design kit is cut from the package's page and loses nothing of it (the look itself is measured in a
browser by lib/qa/kit_compare.mjs; here: the cut, the addresses, the files)."""
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


K = _load('swarmsite_templates_kit', ROOT / 'lib' / 'templates' / 'kit.py')
R = _load('swarmsite_templates_registry', ROOT / 'lib' / 'templates' / 'registry.py')
FIX = ROOT / 'tests' / 'fixtures' / 'templates'
PAGE = '''<!doctype html><html lang="sr" style="--bg:#0c0d10;--ink:#f5f4ef;color-scheme:dark"><head><meta charset="utf-8"><title>T</title>
<style data-fonts="local">@font-face{font-family:"Inter";src:url(fonts/a.woff2) format("woff2")}</style><style>body{background:var(--bg)}.hero{background:url("media/sky.webp")}</style></head>
<body class="b"><header class="top"><a href="https://client.example/prices">Prices</a><img src="media/logo.svg" alt=""></header>
<main id="m"><section class="hero"><h1>One <em>line</em></h1><img src="media/a.webp" srcset="media/a.webp 1x, media/a2.webp 2x" alt=""><p>Open<br>text</section>
<section class="hero" style="background-image:url(media/b.webp)"><h2>Two</h2></section></main>
<footer class="foot"><p>End</p></footer><script>window.x=1</script><script type="application/ld+json">{"a":1}</script></body></html>'''


def test_the_page_is_cut_into_its_parts_in_order_and_each_is_whole():
    p = K.parts(PAGE)
    assert [s['name'] for s in p['sections']] == ['top', 'hero', 'hero-2', 'foot'] and [s['inside'] for s in p['sections']] == [False, True, True, False]
    assert p['sections'][1]['html'].startswith('<section class="hero">') and p['sections'][1]['html'].endswith('</section>') and '<h2>' not in p['sections'][1]['html']
    assert p['tokens'] == [('--bg', '#0c0d10'), ('--ink', '#f5f4ef')] and p['html_style'] == 'color-scheme:dark' and p['lang'] == 'sr'
    assert p['js'] == ['window.x=1'] and p['wrap'] == {'tag': 'main', 'attrs': 'id="m"'} and p['body_attrs'] == 'class="b"'
    assert ''.join(s['html'] for s in p['sections']) in re.sub(r'</?main[^>]*>|\n', '', PAGE)        # nothing of the body is left out or written twice


def test_addresses_are_written_from_where_each_file_stands_and_a_clients_link_is_left_alone():
    f = {k: v.decode() for k, v in K.kit(PAGE, name='Tally').items()}
    assert sorted(f) == ['design/DESIGN.md', 'design/design.css', 'design/design.js', 'design/kit.json', 'design/page.html', 'design/sections/01-top.html',
                         'design/sections/02-hero.html', 'design/sections/03-hero-2.html', 'design/sections/04-foot.html', 'design/tokens.css']
    assert 'url(../fonts/a.woff2)' in f['design/design.css'] and 'url("../media/sky.webp")' in f['design/design.css']
    one = f['design/sections/02-hero.html']
    assert 'src="../../media/a.webp"' in one and 'srcset="../../media/a.webp 1x, ../../media/a2.webp 2x"' in one and 'href="../design.css"' in one and 'src="../design.js"' in one
    assert '<main id="m">' in one and one.count('<section') == 1 and '<body class="b">' in one and 'lang="sr"' in one and 'style="color-scheme:dark"' in one
    assert 'url(../../media/b.webp)' in f['design/sections/03-hero-2.html']
    whole = f['design/page.html']
    assert 'href="https://client.example/prices"' in whole and 'src="../media/logo.svg"' in whole and whole.count('<section') == 2 and whole.index('class="top"') < whole.index('<main') < whole.index('class="foot"')
    assert '--bg: #0c0d10;' in f['design/tokens.css'] and whole.index('design.css') < whole.index('tokens.css')
    assert 'ld+json' not in f['design/design.js'] and json.loads(f['design/kit.json'])['sections'] == ['01-top', '02-hero', '03-hero-2', '04-foot']


def test_the_guide_names_the_tokens_the_faces_and_the_sections_and_never_the_template():
    md = K.kit(PAGE, name='Tally', measured={'type': [{'role': 'Main heading', 'on': 'h1', 'family': 'Inter', 'size': 44, 'weight': '400', 'line': 1, 'tracking': '0', 'count': 1, 'example': 'One line'}], 'radii': [{'value': '10px', 'count': 3}], 'width': {'content': 1200}})['design/DESIGN.md'].decode()
    for must in ('`--bg`', '**Inter**', '`sections/02-hero.html` | One line', '| Main heading | `h1` | Inter | 44 px', '`10px` (3×)', '1200 px wide', 'For the AI tool'):
        assert must in md, must


def test_a_page_with_nothing_to_take_is_refused():
    with pytest.raises(K.KitError):
        K.parts('<html><head></head></html>')
    with pytest.raises(K.KitError):
        K.parts('<html><body><script>1</script></body></html>')


@pytest.mark.parametrize('slug', R.slugs())
def test_every_template_of_the_library_can_be_cut_and_no_file_carries_its_name(slug):
    d = json.loads((FIX / 'tallyfern.json').read_text(encoding='utf-8'))
    try:
        page = R.render(slug, d, '')
    except Exception as err:                                          # a template this client cannot fill is not the kit's matter
        pytest.skip('does not render the product fixture: %s' % str(err)[:80])
    f = K.kit(page, name=d['brand']['name'])
    names = json.loads(f['design/kit.json'])['sections']
    assert len(names) >= 2, names
    assert not any(slug in k for k in f) and slug not in f['design/DESIGN.md'].decode()


def test_a_right_to_left_page_keeps_its_direction_in_every_file_of_the_download():
    page = PAGE.replace('<html ', '<html dir="rtl" ', 1)
    assert 'dir="rtl"' in page and K.parts(page)['dir'] == 'rtl' and K.parts(PAGE)['dir'] == ''
    docs = [v.decode() for k, v in K.kit(page, name='x').items() if k.endswith('.html')]
    assert docs and all('dir="rtl"' in t.split('<head>')[0] for t in docs), 'each page of the download opens right to left'
    assert not any('dir=' in v.decode().split('<head>')[0] for k, v in K.kit(PAGE, name='x').items() if k.endswith('.html'))
