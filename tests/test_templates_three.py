"""Every visitor is shown three designs of their niche (owner's rule, 2026-11-12) — through the real gate.

Each test client, and pagewright (modelled on the production job that got none: software, no features, no close, no
product screens, three photographs), goes through lib/templates/job.py choose(): select's three, each rendered with
the soft sections it misses dropped, gated at 1440 and 390; a failure gives its slot to the next of the reserve.
Pictures are stand-ins at the data's own paths (stress.stand_ins), made pictures the library's own files."""
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / 'tests' / 'fixtures' / 'templates'
HAS_BROWSER = bool(shutil.which('node')) and os.path.exists(os.environ.get('CHROME_PATH') or '/usr/bin/google-chrome')


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


JOB = _load('swarmsite_templates_job', ROOT / 'lib' / 'templates' / 'job.py')
ST = _load('swarmsite_templates_stress', ROOT / 'lib' / 'templates' / 'stress.py')
CLIENTS = sorted(p.stem for p in FIX.glob('*.json'))


@pytest.mark.skipif(not HAS_BROWSER, reason='needs node and Chrome (CHROME_PATH)')
@pytest.mark.parametrize('client', CLIENTS)
def test_three_designs_of_the_clients_niche_pass_the_gate(client, tmp_path):
    d = json.loads((FIX / (client + '.json')).read_text(encoding='utf-8'))
    ST.stand_ins(d, tmp_path)
    r = JOB.choose(d, tmp_path)
    failed = {c['slug']: c['failed'] for c in r['chosen'] if c['slug'] not in r['shown']}
    assert len(r['shown']) == 3, (client, r['shown'], failed)
    by = {c['slug']: c for c in r['chosen']}
    for slug in r['shown']:
        assert by[slug]['ok'] is True and by[slug]['failed'] == []
        assert (tmp_path / (slug + '.html')).is_file() and (tmp_path / 'pub' / (slug + '.html')).is_file()
        if by[slug]['drops']:                                         # the page is made from the data without what it misses
            own = json.loads((tmp_path / (slug + '.data.json')).read_text(encoding='utf-8'))
            assert not any(k in own for k in by[slug]['drops'] if '.' not in k), slug
    if client == 'pagewright':
        assert not r['fallback'], 'a software client is shown software designs'
