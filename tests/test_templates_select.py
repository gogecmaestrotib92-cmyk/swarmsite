"""Selection: up to three templates of the client's niche whose needs the data meets, differing in approach where the
library allows; a client with no usable picture gets only templates that hold without pictures; a template without a
needs.json is never offered; the same data gives the same three."""
import copy
import importlib.util
import json
import subprocess
import sys
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
S = _load('swarmsite_templates_select', ROOT / 'lib' / 'templates' / 'select.py')
PRODUCT, BOOKS, PLACE = (json.loads((FIX / (n + '.json')).read_text(encoding='utf-8')) for n in ('tallyfern', 'quillmoor', 'casaolmo'))
PAGE = "def render(d):\n    return '<!doctype html><html><body><h1>' + d['hero']['title'] + '</h1></body></html>'\n"


def library(tmp_path, **templates):
    """a library of made-up templates: name → needs dict, or None for a template without needs.json"""
    for slug, needs in templates.items():
        (tmp_path / slug).mkdir(parents=True)
        (tmp_path / slug / 'render.py').write_text(PAGE, encoding='utf-8')
        if needs is not None:
            (tmp_path / slug / 'needs.json').write_text(needs if isinstance(needs, str) else json.dumps(needs), encoding='utf-8')
    return tmp_path


def need(niche, **kw):
    return {'niche': niche if isinstance(niche, list) else [niche], 'photos_min': 0, 'photos_large_min': 0, 'screens_min': 0, 'phones_ok': True, 'needs': [],
            'holds_without_pictures': False, 'motif': 'land', **kw}


def chosen(d, lib, **kw):
    return [c['slug'] for c in S.select(d, root=lib, **kw)['chosen']]


def why(d, lib, slug, **kw):
    return next(r['why'] for r in S.select(d, root=lib, **kw)['rejected'] if r['slug'] == slug)


def test_three_of_the_clients_niche_whose_needs_are_met(tmp_path):
    lib = library(tmp_path,
                  alpha=need('software sold to companies', screens_min=2, needs=['steps', 'plans']),
                  bravo=need('an app a person downloads or signs up to', needs=['steps', 'figures'], motif='sky'),
                  carol=need('software product', needs=['faq'], holds_without_pictures=True),
                  delta=need('software product', screens_min=9),                                   # more screens than the client has
                  echo=need('restaurants and hotels', photos_min=1),                               # another niche
                  foxtrot=need('software product', needs=['quotes']),                              # a block the client has not
                  golf=None)                                                                       # not measured: no needs.json
    r = S.select(PRODUCT, root=lib)
    assert r['niche'][0] == 'app' and r['pictures'] == 9
    assert [c['slug'] for c in r['chosen']] == ['bravo', 'alpha', 'carol']                         # the client has phone screens: the app template leads
    assert all(c['why'] and c['approach'] for c in r['chosen'])
    rej = {x['slug']: x['why'] for x in r['rejected']}
    assert 'screens_min 9, the client has 8' in rej['delta'] and 'niche' in rej['echo'] and 'place' in rej['echo']
    assert rej['foxtrot'] == 'fits without needs quotes, but 3 template(s) come before it', 'a soft miss is a reserve, behind every template that meets everything'
    assert {c['slug'] for c in r['reserve']} == {'delta', 'foxtrot'} and all(c['missing'] for c in r['reserve'])
    assert 'no needs.json' in rej['golf'], 'a template without needs.json is not selectable, and the answer says so'
    assert set(rej) | {c['slug'] for c in r['chosen']} == set(R.slugs(lib)), 'every template of the library is accounted for'
    # the light product without phones: software for companies leads; it has no faq: carol is the third, shown without one
    r = S.select(BOOKS, root=lib)
    assert [c['slug'] for c in r['chosen']] == ['alpha', 'bravo', 'carol'] and not r['fallback']
    assert r['chosen'][2]['missing'] == ['needs faq'] and r['chosen'][2]['drops'] == ['faq'] and 'shown without what it misses: needs faq' in r['chosen'][2]['why']
    assert r['chosen'][0]['missing'] == [] and r['chosen'][0]['drops'] == []


def test_the_same_data_gives_the_same_three_and_nothing_is_changed(tmp_path):
    lib = library(tmp_path, **{n: need('software product', motif=m) for n, m in (('zulu', 'land'), ('alpha', 'land'), ('mike', 'sky'), ('bravo', 'sheet'), ('kilo', 'land'))})
    kept = copy.deepcopy(PRODUCT)
    first = S.select(PRODUCT, root=lib)
    assert PRODUCT == kept
    for _ in range(3):
        assert S.select(copy.deepcopy(kept), root=lib) == first
    assert json.loads(json.dumps(first)) == first
    assert [c['slug'] for c in first['chosen']] == ['alpha', 'bravo', 'mike'], 'equal fits are taken by name; one of each approach before a second of any'
    assert chosen(PRODUCT, lib, limit=5) == ['alpha', 'bravo', 'mike', 'kilo', 'zulu'] and chosen(PRODUCT, lib, limit=1) == ['alpha']


def test_they_differ_in_approach_where_the_library_allows(tmp_path):
    lib = library(tmp_path,
                  a1=need('software product', screens_min=2), a2=need('software product', screens_min=2), a3=need('software product', screens_min=3),
                  b1=need('software product', needs=['steps.items[].img (one picture per step)']), c1=need('software product', holds_without_pictures=True, motif='sky'))
    r = S.select(PRODUCT, root=lib)
    assert [c['slug'] for c in r['chosen']] == ['b1', 'a1', 'c1'] and len({c['approach'] for c in r['chosen']}) == 3
    # where it does not allow it, the best three still come
    only = library(tmp_path / 'same', a1=need('software product', screens_min=2), a2=need('software product', screens_min=2), a3=need('software product', screens_min=3), a4=need('software product', screens_min=2))
    r = S.select(PRODUCT, root=only)
    assert [c['slug'] for c in r['chosen']] == ['a1', 'a2', 'a3'] and len({c['approach'] for c in r['chosen']}) == 1
    assert S.approach(need('x', approach='a held walk')) == 'a held walk' and S.approach(need('x', photos_large_min=2, motif='')) == 'no motif · photographs'


def test_a_client_without_usable_pictures_gets_only_templates_that_hold_without_them(tmp_path):
    lib = library(tmp_path, typeled=need('software product', holds_without_pictures=True), pictured=need('software product'), screens=need('software product', screens_min=1))
    bare = {k: v for k, v in PRODUCT.items() if k != 'media'}
    bare['steps'] = {**PRODUCT['steps'], 'items': [{k: v for k, v in i.items() if k != 'img'} for i in PRODUCT['steps']['items']]}
    r = S.select(bare, root=lib)
    assert r['pictures'] == 0 and [c['slug'] for c in r['chosen']] == ['typeled']
    assert 'no usable picture' in why(bare, lib, 'pictured') and 'screens_min 1, the client has 0' in why(bare, lib, 'screens')
    # a picture too small to use is not a usable picture; pictures without stated sizes are
    tiny = {**bare, 'media': {'photos': [{'src': 'media/dot.png', 'w': 60, 'h': 60}]}}
    assert S.select(tiny, root=lib)['pictures'] == 0 and chosen(tiny, lib) == ['typeled']
    assert S.select({**bare, 'media': {'photos': [{'src': 'media/a.jpg'}]}}, root=lib)['pictures'] == 1
    assert chosen(PRODUCT, lib) == ['pictured', 'typeled', 'screens'], 'with pictures all three fit; the type-led one comes second as the other approach'


def test_three_are_filled_first_from_full_fits_then_from_soft_misses_never_from_hard_ones(tmp_path):
    """Owner's rule (2026-11-12): every visitor is shown three designs of their niche. A soft need missed is a section
    dropped; a hard one keeps the template out."""
    lib = library(tmp_path,
                  full=need('software product', needs=['steps']),
                  nofeat=need('software product', needs=['steps', 'features'], motif='sky'),                 # one soft miss
                  twomiss=need('software product', needs=['features', 'close'], screens_min=2, motif='sheet'),  # two soft misses
                  stepsimg=need('software product', needs=['steps', 'steps.img'], motif='blur'),            # a part of every item
                  nohero=need('software product', needs=['hero.kicker']),                                   # hard: the opening
                  shop=need('software product', needs=['catalogue']),                                       # hard: a block of the niche
                  photos=need('software product', photos_min=4, hard=['photos']),                          # hard: the sweep found it breaks with fewer
                  fewer=need('software product', photos_min=4, motif='field'),                              # soft: three of four
                  fewest=need('software product', photos_min=12, motif='field'),                            # soft, further short: after fewer
                  strict=need('software product', needs=['features'], hard=['features']))                   # soft made hard by the template
    d = json.loads((FIX / 'pagewright.json').read_text(encoding='utf-8'))
    r = S.select(d, root=lib)
    assert [c['slug'] for c in r['chosen']] == ['full', 'nofeat', 'stepsimg'] and [c['slug'] for c in r['reserve']] == ['fewer', 'twomiss', 'fewest']
    by = {c['slug']: c for c in r['chosen'] + r['reserve']}
    assert by['full']['missing'] == [] and by['nofeat']['drops'] == ['features'] and by['stepsimg']['drops'] == ['steps.img']
    assert by['twomiss']['missing'] == ['screens_min 2, the client has 0', 'needs features', 'needs close'] and by['twomiss']['drops'] == ['features', 'close'], 'missing screens: nothing to take out'
    rej = {x['slug']: x['why'] for x in r['rejected']}
    assert rej['nohero'] == 'needs hero.kicker' and rej['shop'] == 'needs catalogue' and rej['photos'] == 'photos_min 4, the client has 3' and rej['strict'] == 'needs features'
    assert not r['fallback'] and not any(c['fallback'] for c in r['chosen']) and by['fewer']['missing'] == ['photos_min 4, the client has 3']
    # a template that holds without pictures leaves out the photograph slots it cannot fill; `hard: [photos]` says it cannot
    held = S.assess(need('software product', photos_min=12), S.client(d), d)
    assert held['hard'] == [] and held['soft'] == [{'why': 'photos_min 12, the client has 3', 'drop': '', 'short': .75}]
    bare = {**d, 'media': {'photos': []}}
    assert S.assess(need('software product', photos_min=2), S.client(bare), bare)['hard'] == ['the client has no usable picture and the template does not hold without pictures']
    # one of several: a slot a soft section may fill is a slot the page can drop; one of hard ones is hard
    assert S.is_soft('features') and S.is_soft('steps.items[].img (one each)') and S.is_soft('media.made.land') and S.is_soft('close.title')
    assert not S.is_soft('hero.title') and not S.is_soft('address') and not S.is_soft('catalogue') and not S.is_soft('8 or more product pictures')
    assert not S.is_soft('steps.img', {'hard': ['steps']}) and not S.is_soft('features', {'hard': ['features']}) and S.is_soft('close', {'hard': ['features']})
    a = S.assess(need('software product', needs_any=[['catalogue', 'features']]), S.client(d), d)
    assert a['hard'] == [] and [m['drop'] for m in a['soft'] if m['drop']] == ['features']
    a = S.assess(need('software product', needs_any=[['address', 'phone']]), S.client(d), d)
    assert a['hard'] == ['needs one of address, phone'] and a['soft'] == []


def test_a_missed_soft_section_is_taken_out_never_made_up():
    d = copy.deepcopy(BOOKS)
    v = S.without(d, ['features', 'steps.img', 'close', 'links.d', 'screens'])
    assert d == BOOKS, 'the data given is not changed'
    assert 'features' not in v and 'close' not in v and v['steps']['items'] and not any('img' in i for i in v['steps']['items'])
    assert v['links'] and not any('d' in x for x in v['links']) and v['media'] == BOOKS['media'] and v['plans'] == BOOKS['plans']
    assert S.without(d, []) is d and S.without(d, ['hero', 'catalogue']) == d, 'only soft sections are ever taken out'


def test_a_niche_short_of_three_is_filled_from_its_nearest_group_and_says_so(tmp_path):
    lib = library(tmp_path, inn=need('restaurant', photos_min=1), lodge=need('hotel', photos_min=1, motif='sky'), hall=need('venue', photos_min=1, needs=['faq'], motif='sheet'),
                  desk=need('law', photos_min=1), shopfront=need('shop', photos_min=1))
    r = S.select(PLACE, root=lib)
    assert [(c['slug'], c['fallback'], c['niche']) for c in r['chosen']] == [('inn', False, 'restaurant'), ('lodge', True, 'hotel'), ('hall', True, 'venue')] and r['fallback']
    assert "not the client's niche, the nearest: niche hotel" in r['chosen'][1]['why']
    assert 'niche' in why(PLACE, lib, 'desk') and 'niche' in why(PLACE, lib, 'shopfront'), 'a restaurant is never shown a law firm to make up the three'
    # the client's own niche comes first, a soft miss of its own before a neighbour that fits whole
    lib2 = library(tmp_path / 'b', inn=need('restaurant', photos_min=1), inn2=need('restaurant', photos_min=1, needs=['plans'], motif='sky'), lodge=need('hotel', photos_min=1, motif='sheet'))
    r = S.select(PLACE, root=lib2)
    assert [(c['slug'], c['fallback']) for c in r['chosen']] == [('inn', False), ('inn2', False), ('lodge', True)]
    assert S.NEAR['software'] == ['app'] and set(S.NEAR['service']) >= {'clinic', 'law', 'corporate', 'person', 'nonprofit', 'shop'}
    for a, near in S.NEAR.items():                                   # the groups go both ways
        for b in near:
            if b in S.NEAR and a in S.FIXED:
                assert a in S.NEAR[b], (a, b)


def test_every_test_client_and_the_production_case_get_three_of_their_niche_from_the_library():
    """The real library: every fixture — and pagewright, modelled on the job that got none (software, no features, no
    close, no screens, three photographs) — gets three chosen, and a reserve behind them when the library has one."""
    for f in sorted(FIX.glob('*.json')):
        d = json.loads(f.read_text(encoding='utf-8'))
        r = S.select(d)
        assert len(r['chosen']) == 3, (f.stem, [x['why'] for x in r['rejected']][:5])
        assert len({c['slug'] for c in r['chosen']}) == 3
    r = S.select(json.loads((FIX / 'pagewright.json').read_text(encoding='utf-8')))
    assert not r['fallback'] and all(c['niche'] in ('software', 'saas', 'app') for c in r['chosen']) and len(r['reserve']) >= 2
    assert any('features' in c['drops'] for c in r['chosen']), 'shown without the features it does not have'


def test_a_place_gets_place_templates_and_its_own_needs_are_read(tmp_path):
    lib = library(tmp_path,
                  inn=need('restaurants, hotels: places with a door', photos_min=5, needs=['menu', 'hours']),
                  lodge=need('hospitality-travel', photos_large_min=3),                             # the restaurant has two photographs 1400 wide
                  rooms=need('a place', photos_min=1, needs=['spaces', 'booking']),
                  product=need('software product'))
    r = S.select(PLACE, root=lib)
    assert r['niche'] == ['restaurant', 'place'] and [c['slug'] for c in r['chosen']] == ['inn', 'rooms', 'lodge']
    assert r['chosen'][2]['missing'] == ['photos_large_min 3, the client has 2'], 'two of three large photographs: offered last, saying so'
    assert 'niche' in why(PLACE, lib, 'product')
    no_photos = {**PLACE, 'media': {'photos': []}}
    assert chosen(no_photos, lib) == [] and 'no usable picture' in why(no_photos, lib, 'inn'), 'none of them holds without pictures'
    closed = {**PLACE, 'place': {**PLACE['place'], 'hours': [], 'menu': {'h': 'https://x.example/carta', 'sections': [], 'lists': []}}}
    assert why(closed, lib, 'inn') == 'needs menu; needs hours', 'a link to a menu is not a menu to show; hours not stated are not hours'
    assert chosen(PRODUCT, lib) == ['product']


def test_a_template_made_for_the_clients_niche_comes_before_one_that_only_also_holds_for_it(tmp_path):
    """The first niche of a needs.json is what the template was made for; the later ones are where it also holds.
    Among equal fits: made for the client's niche, then made for a kin of it (another kind of place for a place),
    then one that lists the niche only later — whatever the names, and however many needs each one meets."""
    hotel = {**PLACE, 'kind': 'hotel'}
    lib = library(tmp_path,
                  aclinic=need(['clinic', 'hotel', 'service'], needs=['hours', 'menu', 'since']),   # meets more needs, sorts first by name
                  bschool=need(['school', 'law', 'hotel'], needs=['hours', 'menu']),
                  rooms=need(['hotel', 'restaurant'], motif='sky'),
                  tables=need(['restaurant', 'hotel', 'venue'], motif='sheet'))
    assert chosen(hotel, lib) == ['rooms', 'tables', 'aclinic']
    assert chosen(hotel, lib, limit=4) == ['rooms', 'tables', 'aclinic', 'bschool']
    assert chosen(PLACE, lib) == ['tables', 'rooms', 'aclinic'], 'for a restaurant the restaurant page leads and the hotel page is its kin'
    assert S.select(PLACE, root=lib)['chosen'][2]['fallback'], 'the third, a clinic page that holds for a hotel, fills in from the nearest niche'
    assert [S.select(hotel, root=lib, limit=4) == S.select(hotel, root=lib, limit=4) for _ in range(3)] == [True] * 3
    # a client of one fixed niche: a page made for law before a clinic page that also lists law
    law = {**PLACE, 'kind': 'law'}
    lib2 = library(tmp_path / 'law', aclinic=need(['clinic', 'law'], needs=['hours', 'menu']), firm=need(['law', 'clinic']))
    assert chosen(law, lib2) == ['firm', 'aclinic']


def test_needs_are_read_strictly_and_an_unreadable_one_keeps_the_template_out(tmp_path):
    P = S.client(PRODUCT)['pics']
    met = lambda n, d=PRODUCT, promised=(): S.need_met(n, d, S.client(d)['pics'], promised)
    for n in ('steps', 'features', 'figures', 'plans', 'faq', 'links', 'statement', 'close', 'trust', 'hero', 'hero.text2', 'video', 'media.video',
              'steps.items[].img (one upright screen or picture per step, 3-4 steps)', 'steps (2-8 items with a picture each)', 'steps (3+ items with k, each with its own picture)',
              'steps (items with a picture)', 'figures (the dock bar)', '8 or more product pictures in all (screens, phones, photos) for the pinned wall',
              '3 upright pictures (phones or covers) for the device card'):
        assert met(n) == (True, False, ''), n
    for n in ('quotes', 'logos', 'menu', 'spaces', 'hours', 'photos', 'made.land', 'media.made.field', 'steps (4+ items)', 'steps (5-8 items with a picture each)',
              '9 or more product pictures', '5 upright pictures'):
        assert met(n) == (False, False, ''), n
    assert met('faq', BOOKS) == (False, False, '') and met('video', BOOKS) == (False, False, '') and met('3 upright pictures', BOOKS)[0]
    stepless = {**PRODUCT, 'steps': {**PRODUCT['steps'], 'items': [dict(PRODUCT['steps']['items'][0]), {'title': 'no picture, no k'}]}}
    assert met('steps', stepless)[0] and not met('steps (items with a picture)', stepless)[0] and not met('steps.items[].img', stepless)[0] and not met('steps (2+ items with k)', stepless)[0]
    # one of several, and a given item of a list
    for n in ('quotes or faq', 'menu or steps (3+ items)', 'media.screens[0] or media.video (the pinned window of the opening)', 'media.screens[3]', 'spaces or steps.items (3, each with a picture)',
              'links (3 or more, each with a sentence `d` or a photograph of its own)'):
        assert met(n) == (True, False, ''), n
    for n in ('quotes or logos', 'media.screens[4]', 'menu or spaces', 'address or phone', 'place.menu.sections or place.cuisine (the changing heading)', 'links (5 or more)'):
        assert met(n) == (False, False, ''), n
    assert met('made.land or quotes', promised=('made',)) == (True, True, '') and met('made.land or faq', promised=('made',)) == (True, False, '')
    assert met('faq or a calm client')[2] and met('weather or faq')[2]
    assert met('address or phone', PLACE) == (True, False, '') and met('menu or spaces', PLACE)[0] and met('hours', PLACE)[0] and met('since', PLACE)[0]
    for n in ('a calm client', 'Steps', 'weather', 'steps and features', '', None, 42):
        assert met(n)[2].startswith('a need this step cannot read'), n
    # made pictures: in the data, or promised by a later stage — then the variant says what it waits for
    assert met('made.land', promised=('made',)) == (True, True, '')
    with_made = {**PRODUCT, 'media': {**PRODUCT['media'], 'made': {'land': [{'src': 'media/tallyfern/made/land-0.jpg', 'w': 2400, 'h': 1200, 'tone': 'dark'}]}}}
    assert met('made.land', with_made) == (True, False, '') and met('made.blur', with_made) == (False, False, '') and met('made.blur', with_made, ('made',)) == (True, True, '')
    lib = library(tmp_path, made=need('software product', needs=['steps', 'made.land']), vague=need('software product', needs=['a calm client']),
                  odd=need('software product', gadgets_min=2), worded=need('software product', screens_min='two'), nameless=need([]), broken='{"niche": [', unknown=need('zeppelin tours'))
    # made pictures are soft: without them the template is still offered, after every one that has them, and says so
    r = S.select(PRODUCT, root=lib)
    assert [(c['slug'], c['missing'], c['drops']) for c in r['chosen']] == [('made', ['needs made.land'], [])] and chosen(with_made, lib) == ['made']
    assert S.select(with_made, root=lib)['chosen'][0]['missing'] == []
    r = S.select(PRODUCT, root=lib, promised=('made',))
    assert [(c['slug'], c['pending'], c['missing']) for c in r['chosen']] == [('made', ['made.land'], [])] and 'waits for made.land' in r['chosen'][0]['why']
    assert 'cannot read' in why(PRODUCT, lib, 'vague') and 'gadgets_min' in why(PRODUCT, lib, 'odd'), 'a need that cannot be read is hard: it keeps the template out'
    assert 'not a number' in why(PRODUCT, lib, 'worded') and 'no niche' in why(PRODUCT, lib, 'nameless') and 'not a JSON object' in why(PRODUCT, lib, 'broken')
    assert 'does not know' in why(PRODUCT, lib, 'unknown')
    assert P['screens'] and P['phones'] and P['video']


def test_niches_named_in_free_words_are_read_by_their_telling_words():
    T = S.niche_tags
    assert T('an app a person downloads or signs up to') == ['app'] and T('consumer-app') == ['app'] and T('software with phone screens') == ['app', 'software']
    assert T('saas-b2b') == ['saas'] and T('software sold to companies') == ['saas', 'software'] and T('platform / API') == ['saas'] and T('AI product') == ['software']
    assert T('restaurants, drinks, products sold directly')[0] == 'place' and T('hospitality-travel') == ['place'] and T('lodges, trips, places to stay')[0] == 'place'
    assert T('zeppelin tours') == [] and T(None) == []
    C = lambda **d: S.client(d)['niche']
    assert C(kind='software', media={'phones': [{'src': 'a.jpg'}]})[0] == 'app' and C(kind='software')[0] == 'software'
    assert C(kind='restaurant') == ['restaurant', 'place'] and C(kind='software', place={'hours': []}) == ['software', 'saas', 'app'] and C(kind='hotel') == ['hotel', 'place'] and C(kind='venue') == ['venue', 'place'] and C(kind='') == [] and C() == []
    assert C(kind='', place={'address': {'city': 'Leganés'}}) == ['place']


def test_the_real_library_is_answered_for_whole():
    """Whatever is in lib/templates today: every template is either chosen or has its reason, a template without
    needs.json is never chosen, and nothing but a registered template is named."""
    for d in (PRODUCT, BOOKS, PLACE, {'brand': {'name': 'A'}, 'hero': {'title': 'T'}}):
        for promised in ((), ('made',)):
            r = S.select(d, promised=promised)
            names = [c['slug'] for c in r['chosen']] + [x['slug'] for x in r['rejected']]
            assert {c['slug'] for c in r['reserve']} <= {x['slug'] for x in r['rejected']}, 'a reserve is listed with its reason too'
            assert sorted(names) == R.slugs() and len(r['chosen']) <= 3
            assert all(R.needs(c['slug']) is not None for c in r['chosen'])
            for c in r['chosen'] + r['reserve']:
                assert R.audit(c['slug'], {'client': S.without(d, c['drops'])}) == []
    assert 'no needs.json' in next((x['why'] for x in S.select(PRODUCT)['rejected'] if R.needs(x['slug']) is None), 'no needs.json')


def test_the_file_named_select_does_not_stand_in_for_the_standard_librarys():
    """lib/render/render_bp.py puts lib/templates first on sys.path. A plain `import select` after that must still be
    the standard library's (selectors, subprocess and sockets depend on it)."""
    code = ("import sys; sys.path.insert(0, %r); import select, selectors, subprocess; "
            "assert hasattr(select, 'select') and select.select([], [], [], 0) == ([], [], []), select; "
            "assert not hasattr(select, 'niche_tags'); s = selectors.DefaultSelector(); s.close(); "
            "print(subprocess.run([sys.executable, '-c', 'print(1)'], capture_output=True, text=True).stdout.strip())") % str(ROOT / 'lib' / 'templates')
    out = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0 and out.stdout.strip() == '1', out.stderr[-400:]
