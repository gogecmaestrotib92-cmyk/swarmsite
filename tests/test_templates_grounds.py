"""A client with no photograph is not left with a flat slab of colour: the templates such a client is shown hold a made
picture of the library as the ground of their opening (a backdrop, slots.py), and those come first when the client has
no photograph to speak of. A firm of accountants with none had three designs of flat colour and words (a visitor's
job, 2026-11-23); 12 of 20 visitors' jobs that week came with 0 or 1 picture."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / 'tests' / 'fixtures' / 'templates'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


R = _load('swarmsite_templates_registry_grounds', ROOT / 'lib' / 'templates' / 'registry.py')
SEL = _load('swarmsite_templates_select_grounds', ROOT / 'lib' / 'templates' / 'select.py')
SL = _load('swarmsite_templates_slots_grounds', ROOT / 'lib' / 'templates' / 'slots.py')
client = lambda name: json.loads((FIX / (name + '.json')).read_text(encoding='utf-8'))
LAND = {'src': 'media/library/nature/linen-with-navy/wide-lead.jpg', 'w': 1344, 'h': 752, 'tone': 'light', 'mean': '#cdc6c0', 'name': 'wide-lead'}


def bare(name, made=True):
    d = copy.deepcopy(client(name))
    m = d.setdefault('media', {})
    for k in ('photos', 'screens', 'phones', 'video'):
        m.pop(k, None)
    m['photos'] = []
    if made:
        m['made'] = {'family': 'nature', 'palette': 'linen-with-navy', 'land': [dict(LAND)]}
    else:
        m.pop('made', None)
    return d


@pytest.mark.parametrize('slug', ['iip', 'pcnw', 'bronxarts'])
def test_an_opening_with_no_photograph_stands_on_a_made_ground(slug):
    assert 'hero-backdrop' in SL.BACKDROPS[slug]
    page = R.render(slug, bare('wendholm'))
    uses = [u for u in SL.uses(page) if u['slot'] == 'hero-backdrop']
    assert len(uses) == 1 and uses[0]['src'].endswith(LAND['src']), 'the made picture is the ground of the opening'
    assert SL.undeclared(slug, page) == []
    assert 'hero-backdrop' not in R.render(slug, bare('wendholm', made=False)), 'no library, no ground: the page as it was'
    own = R.render(slug, copy.deepcopy(client('wendholm')))
    assert 'hero-backdrop' not in own, "a client's own photograph is never replaced by a made one"


def test_a_client_with_no_photograph_is_shown_the_templates_that_hold_a_ground_first():
    for name in ('wendholm', 'fernhollow', 'svetlinka'):          # a service, a clinic, a school
        got = [c['slug'] for c in SEL.select(bare(name), limit=3)['chosen']]
        assert all(s in SL.BACKDROPS for s in got), (name, got)
    # with photographs of its own the order is as it was: a ground is not what such a client is chosen by
    plain = [c['slug'] for c in SEL.select(copy.deepcopy(client('wendholm')), limit=3)['chosen']]
    assert plain == ['woodwrights', 'odyssee', 'innerflow']
    # a place takes no made picture (pictures.PLACES), so its order does not change with its photographs gone
    P = _load('swarmsite_templates_pictures_grounds', ROOT / 'lib' / 'templates' / 'pictures.py')
    assert {'restaurant', 'hotel', 'shop', 'cafe', 'bar', 'venue', 'place'} == P.PLACES
