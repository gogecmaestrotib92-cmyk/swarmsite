"""lib/templates/job.py: a job folder (capture + reader) → data, media written from the capture, three variants
rendered twice (media beside the page for the gate and the package; media at the preview address for the visitor),
gated — a failing variant is not shown — and a package only for a variant that is shown. (The gate and the package
themselves are tested in their own files; here they are stand-ins.)"""
import importlib.util
import json
import subprocess
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


JOB = _load('swarmsite_templates_job', ROOT / 'lib' / 'templates' / 'job.py')
G = _load('swarmsite_templates_gate', ROOT / 'lib' / 'templates' / 'gate.py')
P = _load('swarmsite_templates_package', ROOT / 'lib' / 'templates' / 'package.py')


def capture(tmp_path, kind='product'):
    out = tmp_path / 'site'
    subprocess.run([sys.executable, str(ROOT / 'tests' / 'fixtures' / 'templates' / 'capture.py'), str(out), kind], check=True, capture_output=True)
    return out


def test_a_job_folder_becomes_gated_variants_with_their_media(tmp_path, monkeypatch):
    monkeypatch.setenv('SWARMSITE_LIBRARY', 'none')                 # this test is about the job's own media, not made pictures
    seen = []
    monkeypatch.setattr(G, 'check', lambda files, **kw: [seen.append([Path(f).name for f in files]) or {'page': str(f), 'ok': True, 'failed': [], 'checks': {}, 'ms': 5} for f in files])
    out = tmp_path / 'templates'
    r = JOB.build(capture(tmp_path), out, base='https://store.example/j/t/')
    assert 'griffin' in r['shown'] and len(r['shown']) <= 3 and [c['slug'] for c in r['chosen']] == r['shown'] and seen == [[s + '.html' for s in r['shown']]] * len(r['shown']) + [[s + '.tone.html' for s in r['shown']]] * len(r['shown'])  # one gate call for all, logged once a page; then one for the other tone
    assert r['niche'][0] == 'software' and any(x['slug'] == 'maze' for x in r['rejected']) and r['media'] == {'written': 3, 'missing': [], 'library': 0}   # the logo, the photograph, and the framed part of the page that stands as a screen
    assert set(r['timings_ms']) == {'adapt', 'media', 'select', 'render', 'gate', 'tones'}
    assert all(c['tones'] == ['light', 'dark'] for c in r['chosen']) and not list(out.glob('*.tone.html'))   # a light client whose designs also pass on a dark ground; the trial pages are not kept
    data = json.loads((out / 'data.json').read_text())
    assert data['brand']['name'] == 'Tallyfern' and not any(k.startswith('_') for k in data)
    assert (out / 'media' / 'logo.svg').read_bytes().startswith(b'<svg') and (out / 'media' / 'img1.jpg').is_file()
    local, pub = (out / 'griffin.html').read_text(), (out / 'pub' / 'griffin.html').read_text()
    assert '"media/logo.svg"' in local and 'https://store.example/j/t/media/logo.svg' in pub and '../../media' not in local + pub
    assert json.loads((out / 'templates.json').read_text()) == r and 'gaps' in json.loads((out / 'adapter.json').read_text())


def test_a_variant_that_fails_the_gate_is_not_shown(tmp_path, monkeypatch):
    monkeypatch.setattr(G, 'check', lambda files, **kw: [{'page': str(f), 'ok': False, 'failed': ['sideways'], 'checks': {'sideways': [{'at': 'd', 'px': 263}]}, 'ms': 5} for f in files])
    r = JOB.build(capture(tmp_path), tmp_path / 'templates')
    assert r['shown'] == [] and r['chosen'][0]['failed'] == ['sideways'] and r['chosen'][0]['gate'] == {'sideways': [{'at': 'd', 'px': 263}]}
    monkeypatch.setattr(G, 'check', lambda files, **kw: [{'page': str(f), 'ok': False, 'failed': ['tool'], 'error': 'no Chrome'} for f in files])
    r = JOB.build(capture(tmp_path / 'b'), tmp_path / 'b' / 'templates')
    assert r['shown'] == [] and r['chosen'][0]['error'] == 'no Chrome', 'a page that could not be checked is not shown'


def test_a_logo_that_cannot_be_seen_on_a_design_is_set_in_type_there(tmp_path, monkeypatch):
    """the gate's `unseen` naming only the logo: that design is rendered again with the name in type and gated again"""
    monkeypatch.setenv('SWARMSITE_LIBRARY', 'none')
    calls = []

    def check(files, **kw):
        calls.append([Path(f).name for f in files])
        res = []
        for f in files:
            dark = Path(f).name == 'griffin.html' and 'media/logo.svg' in Path(f).read_text()
            res.append({'page': str(f), 'ok': not dark, 'failed': ['unseen'] if dark else [],
                        'checks': {'unseen': [{'at': 'd', 'file': 'logo.svg', 'shows': 0, 'holds': 90}]} if dark else {}, 'ms': 5})
        return res
    monkeypatch.setattr(G, 'check', check)
    out = tmp_path / 'templates'
    r = JOB.build(capture(tmp_path), out)
    g = next(c for c in r['chosen'] if c['slug'] == 'griffin')
    assert 'griffin' in r['shown'] and g['logo'] == 'set in type' and g['failed'] == [] and calls[1] == ['griffin.html']
    assert 'media/logo.svg' not in (out / 'griffin.html').read_text() + (out / 'pub' / 'griffin.html').read_text() and 'Tallyfern' in (out / 'griffin.html').read_text()
    assert json.loads((out / 'griffin.data.json').read_text())['brand']['logo'] is None, 'the package and the editor read the design as shown'
    assert all('logo' not in c for c in r['chosen'] if c['slug'] != 'griffin') and json.loads((out / 'data.json').read_text())['brand']['logo'] == 'media/logo.svg'
    # another picture unseen, or anything else failing with it: the design is held back as before
    monkeypatch.setattr(G, 'check', lambda files, **kw: [{'page': str(f), 'ok': False, 'failed': ['unseen'], 'checks': {'unseen': [{'at': 'd', 'file': 'img1.jpg'}]}, 'ms': 5} for f in files])
    r = JOB.build(capture(tmp_path / 'b'), tmp_path / 'b' / 'templates')
    assert r['shown'] == [] and all('logo' not in c for c in r['chosen'])


def test_a_design_is_measured_on_the_other_tone_and_holds_only_what_passed(tmp_path, monkeypatch):
    """the editor offers a design the colours of a tone only where the job measured it: the tone the page was made in,
    and the other one when the design passes the gate under a palette of it (three designs of one real job failed
    every dark ground, 2026-11-13)"""
    monkeypatch.setenv('SWARMSITE_LIBRARY', 'none')
    dark = []

    def check(files, **kw):
        out = []
        for f in files:
            trial = Path(f).name.endswith('.tone.html')
            if trial:
                dark.append('#111111' in Path(f).read_text())
            bad = trial and Path(f).name.startswith('griffin')
            out.append({'page': str(f), 'ok': not bad, 'failed': ['legible'] if bad else [], 'checks': {}, 'ms': 5})
        return out
    monkeypatch.setattr(G, 'check', check)
    r = JOB.build(capture(tmp_path), tmp_path / 'templates')
    by = {c['slug']: c for c in r['chosen']}
    assert dark and all(dark), 'the trial page is the design on the dark ground the editor would offer'
    assert by['griffin']['tones'] == ['light'] and by['griffin']['tone_failed'] == ['legible']
    assert all(c['tones'] == ['light', 'dark'] and 'tone_failed' not in c for s, c in by.items() if s != 'griffin' and s in r['shown'])
    # a gate that could not run proves nothing: the other tone is not offered
    monkeypatch.setattr(G, 'check', lambda files, **kw: [{'page': str(f), 'ok': not Path(f).name.endswith('.tone.html'), 'failed': ['tool'] if Path(f).name.endswith('.tone.html') else [], 'checks': {}} for f in files])
    r = JOB.build(capture(tmp_path / 'b'), tmp_path / 'b' / 'templates')
    assert r['shown'] and all(c['tones'] == ['light'] for c in r['chosen'] if c['slug'] in r['shown'])


def test_a_site_nothing_fits_and_pictures_that_could_not_be_written(tmp_path, monkeypatch):
    monkeypatch.setattr(G, 'check', lambda files, **kw: [{'page': str(f), 'ok': True, 'failed': []} for f in files])
    r = JOB.build(capture(tmp_path, 'empty'), tmp_path / 'templates')
    assert r['chosen'] == [] and r['shown'] == [] and r['rejected']
    d = {'brand': {'name': 'A', 'logo': 'media/logo.svg'}, 'hero': {'title': 'T'}, 'steps': {'items': [{'title': 's', 'img': 'media/a.jpg'}]}, 'media': {'photos': [{'src': 'media/a.jpg'}, {'src': 'media/b.jpg'}]},
         '_media': {'media/logo.svg': {'from': 'assets.logo'}, 'media/a.jpg': {'from': 'images', 'id': 'x'}, 'media/b.jpg': {'from': 'images', 'id': 'b'}, '../escape.jpg': {'from': 'images', 'id': 'b'}}}
    seed = {'images': [{'id': 'b', 'data': 'data:image/jpeg;base64,/9j/'}], 'assets': {}}
    written, missing = JOB.write_media(seed, d, tmp_path / 'm')
    assert written == ['media/b.jpg'] and sorted(missing) == ['../escape.jpg', 'media/a.jpg', 'media/logo.svg'] and not (tmp_path / 'escape.jpg').exists()
    kept = JOB._drop(d, missing)
    assert kept['brand']['logo'] is None and kept['media']['photos'] == [{'src': 'media/b.jpg'}] and 'img' not in kept['steps']['items'][0], 'a page never asks for a file that is not there'


def test_a_package_only_for_a_variant_that_is_shown(tmp_path, monkeypatch):
    monkeypatch.setattr(G, 'check', lambda files, **kw: [{'page': str(f), 'ok': True, 'failed': []} for f in files])
    out = tmp_path / 'templates'
    JOB.build(capture(tmp_path), out)
    r = JOB.package(out, 'maze', tmp_path / 'maze.zip', verify=False)
    assert r['ok'] is False and 'not a variant this job shows' in r['why'][0] and not (tmp_path / 'maze.zip').exists()
    monkeypatch.setattr(P, 'fetch_cached', lambda url, cache=None: b"@font-face{font-family:x;src:url(https://fonts.gstatic.com/s/x.woff2)}" if 'googleapis' in url else b'wOF2')
    r = JOB.package(out, 'griffin', tmp_path / 'griffin.zip', verify=False)
    assert r['ok'] is True and r['bytes'] > 1000 and r['files'] >= 5 and (tmp_path / 'griffin.zip').is_file()
    monkeypatch.setattr(P, 'verify', lambda preview, z, w, **k: {'ok': False, 'why': ['m: the package is 4100 px high, the preview 4060']})
    r = JOB.package(out, 'griffin', tmp_path / 'g2.zip', verify=True)
    assert r['ok'] is False and 'px high' in r['why'][0], 'a package that does not look like its preview is refused'
