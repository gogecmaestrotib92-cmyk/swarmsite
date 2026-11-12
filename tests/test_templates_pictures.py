"""Made pictures for a preview come from the prepared library: the family by what the client does (the owner's
families.json), the palette nearest the client's of the same tone, three previews three different families, and no made
pictures at all for places, clinics, law, services, shops, schools, people and nonprofits. Never a generation."""
import importlib.util
import json
import os
import struct
import subprocess
import sys
import zlib
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


PI = _load('swarmsite_templates_pictures', ROOT / 'lib' / 'templates' / 'pictures.py')
JOB = _load('swarmsite_templates_job', ROOT / 'lib' / 'templates' / 'job.py')
G = _load('swarmsite_templates_gate', ROOT / 'lib' / 'templates' / 'gate.py')
FAMILIES = ['nature', 'ribbon', 'space', 'material', 'tech']
SLOTS = ['wide-lead', 'mid', 'texture', 'soft', 'wide-quiet', 'glow', 'field', 'field', 'tile', 'tile']


def png(rgb):
    row = b'\x00' + bytes(rgb) * 4
    c = lambda k, d: struct.pack('>I', len(d)) + k + d + struct.pack('>I', zlib.crc32(k + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + c(b'IHDR', struct.pack('>IIBBBBB', 4, 4, 8, 2, 0, 0, 0)) + c(b'IDAT', zlib.compress(row * 4)) + c(b'IEND', b'')


@pytest.fixture
def lib(tmp_path):
    """a made-up library: five families, three palettes (two dark, one light), ten slots each; one family lacks one palette"""
    pals = [{'name': 'navy', 'tone': 'dark', 'ground': '#0a1226', 'accent': '#6f9be8'}, {'name': 'ink-mint', 'tone': 'dark', 'ground': '#0b0c0d', 'accent': '#3ce0a0'},
            {'name': 'warm-cream', 'tone': 'light', 'ground': '#f5eee1', 'accent': '#f37b18'}]
    rows = []
    for fam in FAMILIES:
        for p in pals:
            if fam == 'tech' and p['name'] == 'ink-mint':
                continue
            for i, slot in enumerate(SLOTS):
                rel = 'media/library/%s/%s/%s-%d.png' % (fam, p['name'], slot, i)
                f = tmp_path / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes(png((10 * i, 40, 90)))
                rows.append({'family': fam, 'palette': p['name'], 'slot': slot, 'kind': 'x', 'src': rel, 'w': 1344, 'h': 752, 'tone': p['tone'], 'mean': p['ground']})
    (tmp_path / 'media' / 'library' / 'library.json').write_text(json.dumps(rows))
    (tmp_path / 'media' / 'library' / 'palettes.json').write_text(json.dumps(pals))
    return tmp_path


def client(kind='software', ground='#0b0b0d', accent='#2af6a0', **kw):
    return {'brand': {'name': 'A'}, 'kind': kind, 'palette': {'ground': ground, 'accent': accent}, 'hero': {'title': kw.pop('title', 'One plain sentence')}, **kw}


def test_the_rules_are_the_owners_file_and_the_port_picks_as_the_research_tool_does(lib):
    assert json.loads((ROOT / 'lib' / 'templates' / 'families.json').read_text())['no_made'] == ['restaurant', 'hotel', 'shop', 'cafe', 'bar', 'venue', 'place', 'person', 'clinic', 'law', 'service', 'school', 'nonprofit']
    research = os.environ.get('SWARMSITE_TEMPLATES_SRC') or str(ROOT.parent.parent.parent / 'bench' / 'runs' / '_research' / 'templates')
    tool = Path(research) / 'tools' / 'library.py'
    if not tool.is_file():
        pytest.skip('the research folder is not on this machine')
    L = _load('research_library', tool)
    for d in (client(niche='sports betting analytics app'), client(niche='AI book publishing platform', ground='#ffffff', accent='#2563eb'), client(kind='corporate'), client(kind='restaurant'),
              client(niche='API for developers', ground='#f6efe2', accent='#f87a14'), client(niche='payroll for companies'), client(title='Something with no telling word')):
        assert PI.niche_group(d) == L.niche_group(d)
        assert PI.pick_three(d, research) == L.pick_three(d['palette'], d.get('kind'), 'x', d), d


def test_the_family_follows_what_the_client_does(lib):
    g = lambda **kw: PI.niche_group(client(**kw))[0]
    assert g(niche='sports betting analytics app') == 'life' and g(niche='AI book publishing platform') == 'creative' and g(niche='payroll and invoices for companies') == 'serious'
    assert g(niche='GPU cloud for developers') == 'technical' and g(kind='corporate') == 'corporate' and g(title='Nothing telling here') == 'default'
    assert g(niche='a tool', title='Coaching for your running habit') == 'life', 'the hero speaks where the niche says little'
    three = PI.pick_three(client(niche='sports betting analytics app'), lib)
    assert [m['family'] for m in three] == ['nature', 'ribbon', 'space'], 'life: nature, ribbon, space — three different families in the group\'s order'
    tech = PI.pick_three(client(niche='GPU cloud for developers'), lib)
    assert [m['family'] for m in tech] == ['tech', 'space', 'ribbon'] and [m['palette'] for m in tech] == ['navy', 'ink-mint', 'ink-mint'], 'tech lacks ink-mint: it takes its nearest dark palette'
    assert [m['family'] for m in PI.pick_three(client(niche='GPU cloud for developers', ground='#ffffff', accent='#2563eb'), lib)] == ['tech', 'space', 'ribbon']


@pytest.mark.parametrize('kind', ['restaurant', 'hotel', 'cafe', 'bar', 'venue', 'shop', 'clinic', 'law', 'service', 'school', 'person', 'nonprofit'])
def test_kinds_with_their_own_photographs_take_no_made_family(lib, kind):
    assert PI.pick_three(client(kind=kind, niche='sports software'), lib) == []


def test_the_palette_is_the_nearest_of_the_same_tone_and_the_slots_are_the_contracts(lib):
    m = PI.pick_three(client(niche='fitness app', ground='#0b0b0d', accent='#2af6a0'), lib)[0]
    assert (m['family'], m['palette']) == ('nature', 'ink-mint')
    assert PI.pick_three(client(niche='fitness app', ground='#0a1020', accent='#6f9be8'), lib)[0]['palette'] == 'navy'
    assert PI.pick_three(client(niche='fitness app', ground='#ffffff', accent='#000000'), lib)[0]['palette'] == 'warm-cream', 'a light page never gets a dark palette'
    assert [x['name'] for x in m['land']] == ['wide-lead', 'mid', 'texture', 'soft', 'soft', 'wide-quiet'] and m['land'][3] == m['land'][4]
    assert m['sky']['name'] == 'glow' and len(m['field']) == 2 and len(m['blur']) == 2 and m['blur'][0]['hue'] and 'sheet' not in m
    assert set(PI.files(m)) == {x['src'] for x in m['land'] + m['field'] + m['blur'] + [m['sky']]} and all(f.startswith('media/library/') for f in PI.files(m))
    assert PI.pick_three(client(), lib) == PI.pick_three(client(), lib), 'deterministic'
    one = PI.pick_three(client(niche='fitness app'), lib, rows=[r for r in PI.library(lib)[0] if r['family'] == 'space'], pals=PI.library(lib)[1])
    assert [m['family'] for m in one] == ['space', 'space', 'space'], 'fewer families than three: the order repeats'


def test_without_a_library_there_are_no_made_pictures(tmp_path, monkeypatch):
    monkeypatch.delenv('SWARMSITE_LIBRARY', raising=False)
    assert PI.library(tmp_path) == (None, None) or PI.root_of(tmp_path) is None
    (tmp_path / 'media' / 'library').mkdir(parents=True)
    (tmp_path / 'media' / 'library' / 'library.json').write_text('not json')
    assert PI.library(tmp_path) == (None, None) and PI.pick_three(client(), tmp_path / 'nowhere') == [] or PI.root_of(tmp_path / 'nowhere') is not None


def test_the_job_gives_three_variants_three_families_and_carries_their_files(tmp_path, lib, monkeypatch):
    monkeypatch.setattr(G, 'check', lambda files, **kw: [{'page': str(f), 'ok': True, 'failed': []} for f in files])
    site = tmp_path / 'site'
    subprocess.run([sys.executable, str(ROOT / 'tests' / 'fixtures' / 'templates' / 'capture.py'), str(site)], check=True, capture_output=True)
    out = tmp_path / 'templates'
    r = JOB.build(site, out, library=lib)
    assert r['group'] == 'life' or r['group'] in ('serious', 'default'), r['group']
    for c in r['chosen']:
        assert c['made']['family'] in FAMILIES
        v = json.loads((out / (c['slug'] + '.data.json')).read_text())
        assert v['media']['made']['family'] == c['made']['family'] and all((out / f).is_file() for f in PI.files(v['media']['made']))
        page = (out / (c['slug'] + '.html')).read_text()
        assert any(f in page for f in PI.files(v['media']['made'])) or 'made' not in json.dumps(R_needs(c['slug']))
    assert r['media']['library'] == len({f for c in r['chosen'] for f in PI.files(json.loads((out / (c['slug'] + '.data.json')).read_text())['media']['made'])})
    assert not json.loads((out / 'data.json').read_text())['media'].get('made'), 'the client\'s own data carries no made pictures; each variant\'s does'
    assert json.loads((out / 'data.json').read_text())['niche'], 'the reader\'s description of the business feeds the choice'


def R_needs(slug):
    R = _load('swarmsite_templates_registry', ROOT / 'lib' / 'templates' / 'registry.py')
    return R.needs(slug) or {}
