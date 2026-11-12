"""The gate as a library call and the stress variants: a variant that fails is not shown, a page that could not be
checked has not passed, and a template is tried on clients it has not seen — 1, 3 and 5 plans, 2 and 9 features,
1 and 6 steps, a 12-word h1, a 40-character button, no questions, no photographs. (What the gate itself finds on a
page is tested in the browser: tests/template-gate.mjs.)"""
import copy
import importlib.util
import json
import os
import shutil
import struct
import sys
import zlib
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
A = _load('swarmsite_templates_adapt', ROOT / 'lib' / 'templates' / 'adapt.py')
G = _load('swarmsite_templates_gate', ROOT / 'lib' / 'templates' / 'gate.py')
S = _load('swarmsite_templates_stress', ROOT / 'lib' / 'templates' / 'stress.py')
PRODUCT, BOOKS, PLACE = (json.loads((FIX / (n + '.json')).read_text(encoding='utf-8')) for n in ('tallyfern', 'quillmoor', 'casaolmo'))


def test_the_variants_are_the_ones_the_contract_names_and_the_client_is_left_as_given():
    kept = copy.deepcopy(PRODUCT)
    v = S.variants(PRODUCT)
    assert PRODUCT == kept and list(v) == list(S.NAMES) and all(x is not None for x in v.values())
    count = lambda d, k: len(d[k]['items'])
    assert [count(v['plans-%d' % n], 'plans') for n in (1, 3, 5)] == [1, 3, 5]
    assert [count(v['features-%d' % n], 'features') for n in (2, 9)] == [2, 9] and [count(v['steps-%d' % n], 'steps') for n in (1, 6)] == [1, 6]
    names = [p['name'] for p in v['plans-5']['plans']['items']]
    assert names == ['Stall', 'Row', 'Stall 3', 'Row 4', 'Stall 5'] and len(set(names)) == 5, 'the client\'s own plans, repeated under numbered names'
    assert all(i.get('img') for i in v['steps-6']['steps']['items']) and len({i['title'] for i in v['steps-6']['steps']['items']}) == 6
    h1 = v['h1-12-words']['hero']['title']
    assert len(h1.split()) == 12 and h1.startswith(PRODUCT['hero']['title']), h1
    for spot in (v['button-40']['hero']['primary'], v['button-40']['cta'], v['button-40']['close']['cta']):
        assert 36 <= len(spot['t']) <= 40 and spot['h'], spot
    assert 'faq' not in v['no-faq'] and v['no-faq']['plans'] == PRODUCT['plans']
    # a product has no photographs to lose: it loses every picture instead, so the variant is never the client as given
    m = v['no-photographs']['media']
    assert m['screens'] == [] and m['phones'] == [] and m['video'] is None and not any('img' in i for i in v['no-photographs']['steps']['items'])
    for name, d in v.items():
        assert A.validate(d) == [], name
        assert d != PRODUCT, name


def test_a_client_without_a_block_has_no_variant_of_it():
    v = S.variants(PLACE)
    assert v['plans-1'] is None and v['plans-5'] is None and v['no-faq'] is None, 'a restaurant has no plans and no questions to vary'
    assert v['features-9'] is not None and v['steps-6'] is not None and v['h1-12-words'] is not None
    np = v['no-photographs']
    assert np['media']['photos'] == [] and not any('img' in i for i in np['steps']['items']) and not any('img' in s for s in np['place']['spaces'])
    assert np['place']['hours'] == PLACE['place']['hours'], 'only the pictures go'
    assert S.variants(BOOKS)['no-faq'] is None and S.variants(BOOKS)['no-photographs']['media']['screens'] == BOOKS['media']['screens'], 'photographs go, screens stay'
    bare = S.variants({'brand': {'name': 'A'}, 'hero': {'title': 'One plain sentence'}})
    assert all(x is None for x in bare.values()), 'nothing to vary, nothing invented to vary it with'


@pytest.mark.parametrize('client', ['tallyfern', 'quillmoor', 'casaolmo'])
def test_every_template_renders_every_variant(client):
    d = json.loads((FIX / (client + '.json')).read_text(encoding='utf-8'))
    made = {n: v for n, v in S.variants(d).items() if v is not None}
    assert len(made) >= 6
    for slug in R.slugs():
        assert R.audit(slug, made) == [], slug


def test_stand_in_pictures_keep_each_pictures_proportion(tmp_path):
    raw = S.png(40, 20, (10, 20, 30), (200, 210, 220))
    assert raw[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', raw[16:24]) == (40, 20)
    idat = raw[raw.index(b'IDAT') + 4:raw.index(b'IEND') - 8]
    px = zlib.decompress(idat)
    assert len(px) == 20 * (1 + 40 * 3) and px[1:4] == bytes((10, 20, 30)) and px[-3:] == bytes((200, 210, 220))
    written = S.stand_ins(PRODUCT, tmp_path)
    paths = R.media_paths(PRODUCT)
    assert set(written) == {p for p in paths if not p.endswith('.mp4')} and all((tmp_path / p).is_file() for p in written)
    size = lambda p: struct.unpack('>II', (tmp_path / p).read_bytes()[16:24])
    w, h = size('media/tallyfern/receipts-phone.jpg')
    assert abs(w / h - 780 / 1616) < .01 and max(w, h) == 480
    w, h = size('media/tallyfern/tour-poster.jpg')
    assert abs(w / h - 924 / 758) < .01
    assert '<svg' in (tmp_path / 'media/tallyfern/logo.svg').read_text()
    assert sum((tmp_path / p).stat().st_size for p in written) < 60000, 'stand-ins are small: they only hold a place'


def test_a_failing_variant_is_not_shown_and_an_unchecked_page_has_not_passed(tmp_path, monkeypatch):
    ok = {'slug': 'a', 'ok': True, 'failed': []}
    assert G.shown([ok, {'slug': 'b', 'ok': False, 'failed': ['sideways']}, {'slug': 'c', 'ok': True, 'failed': ['legible']}, {'slug': 'd'}, {'slug': 'e', 'ok': 'yes', 'failed': []}]) == [ok]
    assert G.check([]) == []
    page = tmp_path / 'p.html'
    page.write_text('<!doctype html><html><body><h1>T</h1></body></html>', encoding='utf-8')
    # the tool is not there / dies / prints nothing for a page / says ok and failed at once: none of these is a pass
    monkeypatch.setattr(G, 'TOOL', tmp_path / 'no-such-tool.mjs')
    r = G.check([page, tmp_path / 'q.html'])
    assert [x['ok'] for x in r] == [False, False] and all(x['failed'] == ['tool'] and x['error'] for x in r) and r[0]['page'] == str(page)
    fake = tmp_path / 'fake.mjs'
    monkeypatch.setattr(G, 'TOOL', fake)
    if shutil.which('node'):
        fake.write_text('const a = process.argv.slice(2); console.log("not json"); console.log(JSON.stringify({page: a[0], ok: true, failed: [], checks: {}})); console.log(JSON.stringify({page: a[1], ok: true, failed: ["legible"]}));', encoding='utf-8')
        r = G.check([page, tmp_path / 'q.html', tmp_path / 'r.html'])
        assert r[0]['ok'] is True and r[1]['ok'] is False and r[1]['failed'] == ['tool'] and r[2]['failed'] == ['tool']
    monkeypatch.setattr(G.subprocess, 'run', lambda *a, **k: (_ for _ in ()).throw(OSError('no node')))
    assert G.check([page])[0]['failed'] == ['tool']


def test_a_variant_is_charged_only_with_what_the_client_as_given_does_not_fail():
    base = {'ok': False, 'failed': ['legible'], 'checks': {'legible': [{'at': 'd', 'ratio': 2.1, 'text': 'pale tab'}], 'sideways': []}}
    same = {'ok': False, 'failed': ['legible'], 'checks': {'legible': [{'at': 'd', 'ratio': 2.0, 'text': 'pale tab'}]}}
    worse = {'ok': False, 'failed': ['legible', 'sideways'], 'checks': {'legible': [{'at': 'd', 'ratio': 2.1, 'text': 'pale tab'}, {'at': 'm', 'ratio': 1.4, 'text': 'pale tab'}], 'sideways': [{'at': 'd', 'px': 263}],
                                                               'overlap': [{'at': 'd', 'under': 'a', 'upon': 'b'}]}}
    assert S._new(base, same) == [] and sorted(S._new(base, worse)) == ['legible', 'overlap', 'sideways']
    assert S._new(base, {'ok': False, 'failed': ['tool'], 'error': 'x'}) == ['tool'] and S._new({}, {'ok': True, 'failed': [], 'checks': {}}) == []
    rep = {'maze': {'base': {'ok': True, 'failed': [], 'checks': {}}, 'fails': ['plans-3'], 'variants': {
        'plans-1': {'ok': True, 'failed': [], 'checks': {}, 'new': []}, 'no-faq': None,
        'plans-3': {'ok': False, 'failed': ['sideways'], 'checks': {'sideways': [{'at': 'd', 'px': 263}]}, 'new': ['sideways']}}}}
    t = S.table(rep)
    assert 'maze — as given: ok' in t and 'plans-3          FAILS  sideways 263px at d' in t and 'the client has nothing to vary' in t


@pytest.mark.skipif(not (shutil.which('node') and os.path.exists(os.environ.get('CHROME_PATH') or '/usr/bin/google-chrome')), reason='needs node and Chrome (CHROME_PATH)')
def test_the_gate_is_one_call_on_rendered_files(tmp_path):
    """render → files → gate → what may be shown. A still page that is sound passes; one that runs off the screen is
    not shown. (Short waits: these pages do not move.)"""
    good = '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:24px;font:18px Arial;color:#111;background:#fff}</style></head><body><h1>%s</h1><p>Ten minutes, then the market.</p>%s</body></html>'
    (tmp_path / 'lib' / 'sound').mkdir(parents=True)
    (tmp_path / 'lib' / 'wide').mkdir()
    (tmp_path / 'lib' / 'sound' / 'render.py').write_text("def render(d):\n    return %r %% (d['hero']['title'], '')\n" % good, encoding='utf-8')
    (tmp_path / 'lib' / 'wide' / 'render.py').write_text("def render(d):\n    return %r %% (d['hero']['title'], '<div style=\"width:1900px\">a plan row made for two</div>')\n" % good, encoding='utf-8')
    res = G.render_and_check(PRODUCT, ['sound', 'wide'], tmp_path / 'out', root=tmp_path / 'lib', settle=300, pause=120)
    assert [(x['slug'], x['ok'], x['failed']) for x in res] == [('sound', True, []), ('wide', False, ['sideways'])], res
    assert [x['slug'] for x in G.shown(res)] == ['sound'] and all(Path(x['file']).is_file() for x in res)
    assert res[1]['gate']['checks']['sideways'][0]['px'] > 0 and res[0]['gate']['line_readings'] > 0
