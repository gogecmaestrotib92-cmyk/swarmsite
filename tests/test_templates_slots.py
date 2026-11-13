"""A made (library) picture stands behind things, never as a thing to look at (owner, 2026-11-13): on every template and
every made-up client, a library picture appears only in a slot the template declares a backdrop (lib/templates/made_slots.json);
and the template the rule was found on sets the client's own pictures in its tiles and cards — or none."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / 'tests' / 'fixtures' / 'templates'


def _load(name):
    key = 'swarmsite_templates_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, ROOT / 'lib' / 'templates' / (name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


R, PI, SL = _load('registry'), _load('pictures'), _load('slots')
SOFT = json.loads((FIX / 'tallyfern.json').read_text(encoding='utf-8'))
THREE = PI.pick_three(SOFT, ROOT) if PI.root_of(ROOT) else []
needs_library = pytest.mark.skipif(not THREE, reason='the picture library (media/library) is not in this checkout')


def with_made(d, made):
    return {**d, 'media': {**(d.get('media') or {}), 'made': made}}


@needs_library
def test_a_library_picture_stands_only_in_a_slot_declared_a_backdrop():
    bad, seen = [], 0
    for fx in sorted(FIX.glob('*.json')):
        d = json.loads(fx.read_text(encoding='utf-8'))
        for made in THREE:                                           # the three families a job may give its three designs
            for t in R.list_templates():
                try:
                    html = R.render(t['slug'], with_made(d, made), '')
                except Exception:                                    # a template that does not hold for this client is not this test's matter
                    continue
                seen += len(SL.uses(html))
                bad += [(t['slug'], fx.name, u['slot'], u['src'].rsplit('/', 1)[-1]) for u in SL.undeclared(t['slug'], html)]
    assert seen > 500, 'the library pictures were really rendered and looked for'
    assert bad == [], 'a library picture in a slot that is not a declared backdrop: %s' % bad[:6]


def test_a_picture_without_a_mark_or_in_a_content_slot_is_named():
    page = ('<section data-slot="hero-backdrop"><img src="media/library/a/1.jpg"></section>'
            '<figure><img class="tile" src="media/library/a/2.jpg" data-slot="tile-3"></figure><p><img src="media/library/a/3.jpg"></p>'
            '<style>.x{background:url(media/library/a/4.jpg)}</style><img src="media/img1.jpg" data-slot="tile-1">')
    assert [(u['slot'], u['how']) for u in SL.uses(page)] == [('hero-backdrop', 'img'), ('tile', 'img'), ('?', 'img'), ('css-background', 'css')]
    SL.BACKDROPS['_test'] = ['hero-backdrop', 'css-background']
    try:
        assert [u['slot'] for u in SL.undeclared('_test', page)] == ['tile', '?'], 'the client\'s own picture is never named; a tile and an unmarked picture are'
    finally:
        del SL.BACKDROPS['_test']


@needs_library
def test_tiles_and_cards_take_the_clients_own_pictures_or_none():
    d = with_made(SOFT, THREE[0])
    assert d.get('hero', {}).get('text2') and (d.get('features') or {}).get('items'), 'the made-up client has the sentence the tiles stand in, and features for the cards'
    shots = [{'src': 'media/screen-%d.jpg' % i, 'w': 1800, 'h': 1125, 'alt': ''} for i in (1, 2, 3)]
    rich = {**d, 'media': {**d['media'], 'screens': shots, 'phones': [], 'photos': []}}
    html = R.render('butter', rich, '')
    assert html.count('data-slot="tile-own"') == 2 and 'data-slot="card-own"' in html and 'media/screen-1.jpg' in html
    assert not [u for u in SL.uses(html) if u['slot'] in ('tile-own', 'card-own', 'tile-blur', 'card-sky')], 'no library picture in a tile or a card'
    bare = R.render('butter', {**d, 'media': {**d['media'], 'screens': [], 'phones': [], 'photos': []}}, '')
    assert 'class="slot"' not in bare and 'data-slot="card-own"' not in bare and 'class="stm"' in bare, 'no picture of the client\'s own: the statement runs without tiles, the cards are words'
    assert SL.undeclared('butter', bare) == []
