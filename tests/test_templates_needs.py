"""needs.json in its strict form: fixed keys, niches and names from fixed lists — and the script that brings a
free-worded file into it without guessing: what the strict form cannot say is kept word for word in `notes` and
listed as lost."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


N = _load('swarmsite_normalise_needs', ROOT / 'scripts' / 'normalise_needs.py')
R = _load('swarmsite_templates_registry', ROOT / 'lib' / 'templates' / 'registry.py')
S = _load('swarmsite_templates_select', ROOT / 'lib' / 'templates' / 'select.py')
A = _load('swarmsite_templates_adapt', ROOT / 'lib' / 'templates' / 'adapt.py')
FIX = ROOT / 'tests' / 'fixtures' / 'templates'
PRODUCT, PLACE = (json.loads((FIX / (n + '.json')).read_text(encoding='utf-8')) for n in ('tallyfern', 'casaolmo'))


def test_the_strict_schema_names_the_niches_and_blocks_of_the_contract():
    assert N.NICHES == ['software', 'app', 'restaurant', 'hotel', 'clinic', 'law', 'service', 'shop', 'school', 'person', 'corporate', 'nonprofit', 'venue']
    assert N.SCHEMA['additionalProperties'] is False and set(N.KEYS) == {'niche', 'photos_min', 'photos_large_min', 'screens_min', 'phones_ok', 'needs', 'needs_any', 'min', 'max', 'drops', 'hard', 'holds_without_pictures', 'motif', 'notes'}
    assert len(N.NAMES) == len(set(N.NAMES))
    data = set(A.schema()['properties'])
    for name in N.NAMES:                                              # every name leads to a block the data schema knows
        head = name.split('.')[0]
        assert head in data or head in ('made', 'screens', 'phones', 'photos', 'video') or head in A.schema()['properties']['place']['properties'], name
    for block in ('team', 'catalogue', 'locations', 'credentials', 'contact', 'projects', 'steps', 'plans', 'faq', 'menu', 'spaces', 'hours'):
        assert block in N.NAMES


def test_a_free_worded_file_becomes_the_strict_form_and_says_what_it_lost():
    free = {'niche': ['an app a person downloads or signs up to', 'software sold to companies', 'restaurant', 'venue', 'zeppelin tours'],
            'photos_min': 2, 'photos_large_min': 1, 'screens_min': 2, 'phones_ok': True, 'holds_without_pictures': False, 'motif': "the client's own photographs (no made pictures)",
            'needs': ['steps', 'hero.text2', 'steps.items[].img (one upright picture per step)', 'steps (3+ items with k, each with its own picture)', 'media.made.land', 'place.address',
                      'menu or spaces', 'statement or hero.text (the opening needs one)', '8 or more product pictures in all', '3 upright pictures (phones or covers)', 'features (at least 3)',
                      'steps (2-8 items with a picture each)', 'links (3 or 4)', '2 landscape photographs at least 1440 px wide', 'catalogue or place.menu with priced items', 'one wide photograph',
                      'hero.title and hero.text', 'a calm client'],
            'drops': ['figures', 'links[].d', 'media.screens, media.phones, media.video', 'place.since, cuisine, price_range', 'hero.note (the reference has no place for it)', 'photographs beyond the slots'],
            'notes': 'One remark.', 'measured': {'a client': 'holds'}, 'tiles_min': 4, 'step_pictures_min': 2}
    strict, lost = N.normalise(free)
    assert N.validate(strict) == []
    assert strict['niche'] == ['app', 'software', 'restaurant', 'venue'] and strict['motif'] == 'photos'
    assert (strict['photos_min'], strict['photos_large_min'], strict['screens_min'], strict['phones_ok'], strict['holds_without_pictures']) == (2, 2, 2, True, False), 'two photographs at least 1440 wide are two large ones'
    assert strict['needs'] == ['steps', 'hero.text2', 'steps.img', 'steps.k', 'made.land', 'address', 'features', 'links', 'hero.title', 'hero.text']
    assert strict['needs_any'] == [['menu', 'spaces'], ['statement', 'hero.text']], 'an either/or is one of, not two needs'
    assert strict['min'] == {'steps': 3, 'pictures': 8, 'upright': 3, 'features': 3, 'links': 3, 'steps.img': 2} and strict['max'] == {'steps': 8, 'links': 4}
    assert strict['drops'] == ['figures', 'links.d', 'screens', 'phones', 'video', 'since', 'cuisine', 'price_range', 'hero.note']
    said = ' | '.join(lost)
    for part in ("niche not in the fixed list: 'zeppelin tours'", "an either/or whose ways are not each one plain name: 'catalogue or place.menu with priced items'", "a count or size of pictures the strict keys cannot say: 'one wide photograph'",
                 'a width above 1400 px (1440)', "not a name of the fixed list: 'a calm client'", "'photographs beyond the slots'", 'tiles_min = 4'):
        assert part in said, part
    assert len(lost) == 7, lost
    assert 'menu' not in strict['needs'] and 'spaces' not in strict['needs'] and 'catalogue' not in strict['needs'], 'an either/or is not turned into two needs'
    notes = '\n'.join(strict['notes'])
    for kept in ('One remark.', 'catalogue or place.menu with priced items', 'one wide photograph', 'zeppelin tours', 'measured: {"a client": "holds"}', 'tiles_min: 4', "the client's own photographs (no made pictures)"):
        assert kept in notes, kept
    assert set(strict) <= set(N.KEYS)
    # twice the same; the free file untouched
    assert N.normalise(free) == (strict, lost) and free['needs'][0] == 'steps'


def test_what_is_wrong_in_a_strict_file_is_named():
    good = {'niche': ['software'], 'photos_min': 0, 'photos_large_min': 0, 'screens_min': 1, 'phones_ok': True, 'needs': ['steps'], 'holds_without_pictures': False, 'motif': 'land'}
    assert N.validate(good) == [] and N.validate({**good, 'niche': ['restaurant', 'hotel', 'venue'], 'drops': ['figures'], 'notes': ['a remark'], 'needs_any': [['menu', 'spaces']], 'min': {'steps': 3, 'pictures': 8}, 'max': {'steps': 8}}) == []
    bad = N.validate({**good, 'niche': ['software', 'zeppelin'], 'screens_min': '2', 'phones_ok': 'yes', 'needs': ['steps', 'menu or spaces'], 'motif': 'landscape', 'measured': {}, 'notes': 'one string',
                      'needs_any': [['menu'], ['menu', 'weather']], 'min': {'weather': 2, 'steps': 0}, 'max': 'eight'})
    for part in ("niche: 'zeppelin'", 'screens_min: not a count', 'phones_ok: not true/false', "needs: 'menu or spaces'", "motif: 'landscape'", "unknown key 'measured'", 'notes: not a list',
                 "needs_any: ['menu']", "needs_any: ['menu', 'weather']", "min: 'weather' cannot be counted", 'min: steps is not a count', 'max: not a table of counts'):
        assert any(part in b for b in bad), (part, bad)
    assert any("no 'motif'" in b for b in N.validate({k: v for k, v in good.items() if k != 'motif'})) and any('niche: empty' in b for b in N.validate({**good, 'niche': []}))
    strict, lost = N.normalise({'niche': ['zeppelin tours'], 'needs': 'steps'})
    assert strict['niche'] == [] and any('no niche of the fixed list' in x for x in lost) and N.validate(strict) != []
    assert N.normalise({})[0]['motif'] == 'none' and N.niche_of('person') == ['person'] and N.niche_of('an app a person downloads') == ['app']


def test_the_librarys_own_needs_files_come_through_and_selection_reads_the_strict_form(tmp_path):
    """Whatever needs.json the library holds today normalises to a valid strict file — and a library whose files are
    the strict ones selects as before for the fixture clients, wherever the strict form lost nothing."""
    same = []
    for t in R.list_templates():
        if t['needs'] is None:
            continue
        strict, lost = N.normalise(t['needs'])
        assert N.validate(strict) == [], (t['slug'], N.validate(strict))
        (tmp_path / t['slug']).mkdir()
        (tmp_path / t['slug'] / 'render.py').write_text("def render(d):\n    return '<!doctype html><html><body><h1>x</h1></body></html>'\n", encoding='utf-8')
        (tmp_path / t['slug'] / 'needs.json').write_text(json.dumps(strict), encoding='utf-8')
        if not [x for x in lost if x.startswith(('needs', 'niche', 'a count'))] and 'made.land' not in json.dumps(t['needs']):
            same.append(t['slug'])
    # a candidate (chosen or in reserve) of the library is one of the strict library, and the other way round
    offered = lambda d, promised, root=None: {c['slug'] for k in ('chosen', 'reserve') for c in S.select(d, promised=promised, root=root, limit=99)[k]}
    for d in (PRODUCT, PLACE):
        for promised in ((), ('made',)):
            a, b = offered(d, promised), offered(d, promised, tmp_path)
            for slug in same:
                assert (slug in a) == (slug in b), (slug, promised)


def test_selection_reads_every_strict_name_and_the_fixed_niches(tmp_path):
    P = S.client(PRODUCT)['pics']
    for name in N.NAMES:
        ok, pending, problem = S.need_met(name, PRODUCT, P)
        assert problem == '', name
    met = lambda n, d: S.need_met(n, d, S.client(d)['pics'])[0]
    assert met('steps.img', PRODUCT) and met('steps.k', PRODUCT) and met('plans.rows', PRODUCT) and met('links.d', PRODUCT) and met('features.d', PRODUCT) and met('figures.l', PRODUCT) and met('video', PRODUCT)
    assert not met('team', PRODUCT) and not met('catalogue', PRODUCT) and not met('menu', PRODUCT) and not met('made.land', PRODUCT) and not met('photos', PRODUCT)
    assert met('address', PLACE) and met('hours', PLACE) and met('menu', PLACE) and met('menu.items', PLACE) and met('spaces.img', PLACE) and met('steps.img', PLACE) and met('photos', PLACE) and met('since', PLACE)
    assert not met('plans', PLACE) and not met('screens', PLACE) and not met('steps.cta', PLACE)
    no_img = {**PLACE, 'place': {**PLACE['place'], 'spaces': [{'title': 'El patio'}]}}
    assert met('spaces', no_img) and not met('spaces.img', no_img)
    team = {**PLACE, 'team': {'items': [{'name': 'Ana', 'img': 'media/a.jpg'}, {'name': 'Luis'}]}, 'catalogue': {'groups': [{'t': 'Cursos', 'items': [{'name': 'A1', 'price': '90 €'}]}]}}
    assert met('team', team) and not met('team.img', team) and met('catalogue', team) and not met('catalogue.img', team)
    # the fixed niche words: a template for clinics is not offered to a restaurant, one for restaurants not to a hotel
    need = lambda niche: {'niche': niche, 'photos_min': 0, 'photos_large_min': 0, 'screens_min': 0, 'phones_ok': True, 'needs': [], 'holds_without_pictures': True, 'motif': 'photos'}
    for slug, niche in (('forclinics', ['clinic', 'law']), ('forrestaurants', ['restaurant']), ('forhotels', ['hotel']), ('forsoftware', ['software']), ('forapps', ['app']), ('forplaces', ['a place with a door'])):
        (tmp_path / slug).mkdir()
        (tmp_path / slug / 'render.py').write_text("def render(d):\n    return '<!doctype html><html><body><h1>x</h1></body></html>'\n", encoding='utf-8')
        (tmp_path / slug / 'needs.json').write_text(json.dumps(need(niche)), encoding='utf-8')
    pick = lambda d: [c['slug'] for c in S.select(d, root=tmp_path, limit=6)['chosen'] if not c['fallback']]   # a neighbour's only fills a shortfall, marked
    assert pick(PLACE) == ['forrestaurants', 'forplaces'] and pick({**PLACE, 'kind': 'hotel'}) == ['forhotels', 'forplaces'], 'a template for restaurants is not offered to a hotel'
    assert pick({**PLACE, 'kind': 'venue'}) == ['forplaces'] and S.client({'kind': 'venue'})['niche'] == ['venue', 'place']
    (tmp_path / 'forrestaurants' / 'needs.json').write_text(json.dumps(need(['restaurant', 'hotel', 'venue'])), encoding='utf-8')
    assert pick({**PLACE, 'kind': 'hotel'})[0:2] == ['forhotels', 'forrestaurants'] or set(pick({**PLACE, 'kind': 'hotel'})) == {'forhotels', 'forrestaurants', 'forplaces'}, 'unless it lists hotel'
    assert 'forrestaurants' in pick({**PLACE, 'kind': 'venue'})
    (tmp_path / 'forrestaurants' / 'needs.json').write_text(json.dumps(need(['restaurant'])), encoding='utf-8')
    # one of, at least, at most — against the restaurant: menu and rooms, 3 steps with pictures, 5 photographs of which 2 are 1400 wide
    fit = lambda **kw: S.fits({**need(['restaurant']), **kw}, S.client(PLACE), PLACE)[0]
    assert fit(needs_any=[['plans', 'menu'], ['team', 'spaces', 'faq']]) == [] and fit(needs_any=[['plans', 'faq']]) == ['needs one of plans, faq']
    assert fit(min={'steps': 3, 'steps.img': 3, 'photos': 5, 'photos.large': 2, 'pictures': 5, 'upright': 1, 'spaces': 3, 'menu': 7, 'figures': 4}, max={'steps': 3}) == []
    assert fit(min={'steps': 4}) == ['at least steps 4, the client has 3'] and fit(max={'photos': 4}) == ['at most photos 4, the client has 5'] and fit(photos_large_min=2) == [] and fit(photos_large_min=3) == ['photos_large_min 3, the client has 2']
    assert fit(min={'weather': 1})[0].startswith('a need this step cannot read') and fit(needs_any=[['menu', 'a calm client']])[0].startswith('a need this step cannot read') and fit(min='three')[0].startswith('a need this step cannot read')
    assert S.count('catalogue', {'catalogue': {'groups': [{'items': [{'name': 'a'}, {'name': 'b'}]}, {'items': [{'name': 'c'}]}]}}, S.client({})['pics']) == 3 and S.count('team', {'team': {'groups': [{'items': [{'name': 'a'}]}]}}, S.client({})['pics']) == 1
    page = {'hero': {'title': 'T', 'text': 'One line under it.'}}                       # the least that is a page (select.empty)
    assert pick({**page, 'kind': 'clinic'}) == ['forclinics'] and pick({**page, 'kind': 'law'}) == ['forclinics'] and pick({**page, 'kind': 'school'}) == []
    assert pick({'kind': 'clinic', 'hero': {'title': 'T'}}) == [] and 'nothing else' in S.select({'kind': 'clinic', 'hero': {'title': 'T'}}, root=tmp_path)['rejected'][0]['why']
    assert pick(PRODUCT) == ['forapps', 'forsoftware'] and pick({**PRODUCT, 'media': {}}) == ['forsoftware', 'forapps']
    assert S.client({'kind': 'cafe'})['niche'] == ['restaurant', 'place'] and S.client({'kind': 'person'})['niche'] == ['person']
