"""The editor's patch: edits are operations on the data, never on a design, so the same edits stand on each of the
three designs. Only the visitor's own words and pictures go in; what cannot be applied is refused with its reason."""
import copy
import importlib.util
import json
import struct
import subprocess
import sys
import zlib
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


E = _load('swarmsite_templates_edit', ROOT / 'lib' / 'templates' / 'edit.py')
R = E._registry()
D = json.loads((ROOT / 'tests' / 'fixtures' / 'templates' / 'tallyfern.json').read_text(encoding='utf-8'))
UP = 'media/upload/0b1e2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d.jpg'


def test_a_text_is_rewritten_where_the_data_has_it_and_nowhere_else():
    before = copy.deepcopy(D)
    d, refused = E.apply(D, [{'op': 'text', 'path': 'hero.title', 'value': '  The books of a stall,\r\n kept  in minutes '},
                             {'op': 'text', 'path': 'features.items.0.t', 'value': 'Receipts, read for you'}])
    assert refused == [] and D == before, 'the data given is not changed'
    assert d['hero']['title'] == 'The books of a stall, kept in minutes' and d['features']['items'][0]['t'] == 'Receipts, read for you'
    bad = [{'op': 'text', 'path': 'kind', 'value': 'restaurant'}, {'op': 'text', 'path': 'character', 'value': 'x'}, {'op': 'text', 'path': 'hero.primary.h', 'value': 'javascript:alert(1)'},
           {'op': 'text', 'path': 'media.screens.0.src', 'value': 'http://elsewhere/x.jpg'}, {'op': 'text', 'path': 'hero.nothing', 'value': 'x'}, {'op': 'text', 'path': 'hero.title', 'value': '   '},
           {'op': 'text', 'path': 'hero.title', 'value': 'x' * 601}, {'op': 'text', 'path': '__class__', 'value': 'x'}, {'op': 'text', 'path': 'nav.99.t', 'value': 'x'}, {'op': 'rm -rf'}, 'text']
    d, refused = E.apply(D, bad)
    assert d == D and [r['i'] for r in refused] == list(range(len(bad))), refused
    assert {f['path'] for f in E.fields(D)}.isdisjoint({'kind', 'niche', 'character', 'lang'}) and not any(f['path'].startswith(('media.', 'palette')) or f['path'].endswith('.h') for f in E.fields(D))


def test_a_picture_slot_takes_only_the_clients_own_pictures():
    own = [p['src'] for p in E.pictures(D)]
    slots = E.slots(D)
    assert own and slots and all(not s.startswith('media/library/') for s in own)
    step = next(s for s in slots if s['path'].endswith('.img'))
    screen = next(s for s in slots if s['path'].startswith('media.screens.'))
    d, refused = E.apply(D, [{'op': 'picture', 'path': step['path'], 'src': own[0]}, {'op': 'picture', 'path': screen['path'], 'src': own[-1]},
                             {'op': 'picture', 'path': screen['path'], 'src': 'https://elsewhere.example/x.jpg'}, {'op': 'picture', 'path': 'hero.title', 'src': own[0]}])
    assert [r['why'] for r in refused] == ["not one of the client's own pictures", 'no picture stands there']
    assert E._get(d, E._parts(step['path']))[0] == own[0]
    got = E._get(d, E._parts(screen['path']))[0]
    src = next(p for p in E.pictures(D) if p['src'] == own[-1])
    assert got['src'] == own[-1] and (got.get('w'), got.get('h')) == (src.get('w'), src.get('h')), 'the picture brings its own proportions'
    d, refused = E.apply(D, [{'op': 'photo', 'src': UP, 'w': 1600, 'h': 1000}, {'op': 'picture', 'path': screen['path'], 'src': UP},
                             {'op': 'photo', 'src': 'media/../../etc/passwd', 'w': 1, 'h': 1}, {'op': 'photo', 'src': UP.replace('.jpg', '.svg'), 'w': 1, 'h': 1}])
    assert [r['i'] for r in refused] == [2, 3] and E._get(d, E._parts(screen['path']))[0]['src'] == UP and d['media']['photos'][-1] == {'src': UP, 'w': 1600, 'h': 1000}


def test_sections_hide_and_show_but_the_page_itself_stays():
    d, refused = E.apply(D, [{'op': 'hide', 'block': 'faq'}, {'op': 'hide', 'block': 'plans'}, {'op': 'show', 'block': 'faq'}, {'op': 'hide', 'block': 'hero'},
                             {'op': 'hide', 'block': 'brand'}, {'op': 'hide', 'block': 'nowhere'}, {'op': 'move', 'block': 'faq', 'by': -1}])
    assert 'faq' in d and 'plans' not in d and d['faq'] == D['faq']
    assert [r['why'] for r in refused] == ['this part of the page cannot be hidden'] * 2 + ['no such section', 'this design keeps its own order']
    assert E.movable('griffin') == [] and E.movable('maze') == []


def test_colours_are_refused_when_the_text_would_not_read():
    d, refused = E.apply(D, [{'op': 'palette', 'ground': '#ffffff', 'ink': '#dddddd', 'accent': '#000000'}, {'op': 'palette', 'ground': 'red', 'ink': '#000000', 'accent': '#000000'}])
    assert d['palette'] == D['palette'] and len(refused) == 2 and 'would not read' in refused[0]['why']
    pals = E.palettes(D)
    assert len(pals) >= 4 and all(E.contrast(p['ink'], p['ground']) >= 7 for p in pals)
    assert all(p['accent'] == p['ink'] or E.contrast(p['accent'], p['ground']) >= 3 for p in pals), 'an accent that would not read is not offered on that ground'
    d, refused = E.apply(D, [{'op': 'palette', **{k: pals[0][k] for k in ('ground', 'ink', 'accent')}}])
    assert refused == [] and d['palette']['ground'] == pals[0]['ground'] and d['palette'].get('extra') == D['palette'].get('extra')


def test_switching_design_keeps_every_edit():
    ops = [{'op': 'text', 'path': 'hero.title', 'value': 'Closed by six, every evening'}, {'op': 'hide', 'block': 'faq'}]
    for slug in ('griffin', 'maze'):
        d, refused = E.apply(D, ops, slug)
        page = R.render(slug, d, '')
        assert refused == [] and 'Closed by six, every evening' in page and D['hero']['title'] not in page.split('<title>')[-1].split('</title>')[-1], slug


def test_the_command_line_renders_describes_and_measures(tmp_path):
    (tmp_path / 'd.json').write_text(json.dumps(D))
    (tmp_path / 'o.json').write_text(json.dumps([{'op': 'text', 'path': 'hero.title', 'value': 'Kept in an evening, by hand'}, {'op': 'hide', 'block': 'kind'}]))
    run = lambda *a: subprocess.run([sys.executable, str(ROOT / 'lib' / 'templates' / 'edit.py'), *a], capture_output=True, text=True, timeout=60)
    r = run('render', str(tmp_path / 'd.json'), 'griffin', '--ops', str(tmp_path / 'o.json'), '--base', 'https://store.example/j/t/')
    assert r.returncode == 0 and 'Kept in an evening, by hand' in r.stdout and 'https://store.example/j/t/media/' in r.stdout and '"refused"' in r.stderr
    j = json.loads(run('describe', str(tmp_path / 'd.json'), '--ops', str(tmp_path / 'o.json'), '--slug', 'griffin').stdout)
    assert set(j) >= {'fields', 'pictures', 'slots', 'blocks', 'palettes', 'refused', 'movable'} and j['refused'][0]['i'] == 1
    assert any(f['value'] == 'Kept in an evening, by hand' for f in j['fields'])
    c = lambda k, dd: struct.pack('>I', len(dd)) + k + dd + struct.pack('>I', zlib.crc32(k + dd) & 0xffffffff)
    (tmp_path / 'p.png').write_bytes(b'\x89PNG\r\n\x1a\n' + c(b'IHDR', struct.pack('>IIBBBBB', 640, 480, 8, 2, 0, 0, 0)) + c(b'IDAT', zlib.compress(b'\x00' * 1921 * 480)) + c(b'IEND', b''))
    assert json.loads(run('measure', str(tmp_path / 'p.png')).stdout) == {'w': 640, 'h': 480}
    (tmp_path / 'x.png').write_text('<svg/>')
    assert json.loads(run('measure', str(tmp_path / 'x.png')).stdout) == {}


def test_the_edited_page_is_packaged_whole_and_compared_with_itself_before_anything_is_handed_out(tmp_path):
    """the package publish and the download hand out: the edited render, its pictures and fonts, opened offline beside
    the edited page and compared screen by screen (Chrome; fonts from Google Fonts, cached)"""
    import base64
    c = lambda k, dd: struct.pack('>I', len(dd)) + k + dd + struct.pack('>I', zlib.crc32(k + dd) & 0xffffffff)
    pic = b'\x89PNG\r\n\x1a\n' + c(b'IHDR', struct.pack('>IIBBBBB', 120, 80, 8, 2, 0, 0, 0)) + c(b'IDAT', zlib.compress((b'\x00' + bytes((60, 90, 120)) * 120) * 80)) + c(b'IEND', b'')
    ops = [{'op': 'text', 'path': 'hero.title', 'value': 'Closed by six, every evening'}, {'op': 'hide', 'block': 'faq'}]
    d, _ = E.apply(D, ops, 'griffin')
    media = tmp_path / 'media-root'
    for rel in R.media_used('griffin', d):
        (media / rel).parent.mkdir(parents=True, exist_ok=True)
        (media / rel).write_bytes(b'<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><rect width="40" height="40" fill="#3c5a78"/></svg>' if rel.endswith('.svg') else pic)
    r = E.package(D, 'griffin', ops, str(media), str(tmp_path / 'g.zip'), verify=True)
    assert r['ok'], r['why']
    files = E.zip_files(tmp_path / 'g.zip')
    names = {f['file'] for f in files}
    assert 'index.html' in names and any(f.startswith('fonts/') for f in names) and set(R.media_used('griffin', d)) <= names
    page = base64.b64decode(next(f['data'] for f in files if f['file'] == 'index.html')).decode()
    assert 'Closed by six, every evening' in page, 'the package is the edited page'
    missing = E.package(D, 'griffin', ops, str(tmp_path / 'nowhere'), str(tmp_path / 'h.zip'), verify=False)
    assert not missing['ok'] and 'could not be had' in missing['why'][0], 'a picture that cannot be had refuses the package'
