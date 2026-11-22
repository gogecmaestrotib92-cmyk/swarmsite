"""tablet.py — a template that was measured to hold it stands in its desk composition from 768 px (owner, 2026-11-22);
every other template, and every width outside 768–threshold, is what it was."""
import importlib.util
import json
import os
import re
import shutil
import subprocess
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


T = _load('swarmsite_templates_tablet', ROOT / 'lib' / 'templates' / 'tablet.py')
R = _load('swarmsite_templates_registry', ROOT / 'lib' / 'templates' / 'registry.py')
K = _load('swarmsite_templates_kit', ROOT / 'lib' / 'templates' / 'kit.py')
FIX = ROOT / 'tests' / 'fixtures' / 'templates'
PAGE = ('<!doctype html><html><head><style>.a{color:red}@media (min-width:1024px){.nav{display:flex}}@media (max-width: 1023px){.burger{display:block}}'
        '@media (max-width:600px){.x{y:z}}@media (min-width:1400px){.w{max-width:1200px}}@media (min-width:900px) and (max-width:1023px){.m{c:d}}</style></head>'
        '<body class="b"><main><h1>One</h1></main><script>var a=1</script></body></html>')
HAS_BROWSER = bool(shutil.which('node')) and os.path.exists(os.environ.get('CHROME_PATH') or '/usr/bin/google-chrome')


def test_the_desk_rules_start_at_768_and_only_the_rules_between_768_and_the_threshold_move():
    assert T.threshold(PAGE) == 1024
    out = T.desk(PAGE)
    css = re.search(r'<style>(.*?)</style>', out, re.S).group(1)
    assert '@media (min-width:768px){.nav{display:flex}}' in css and '@media (max-width:767px){.burger{display:block}}' in css
    assert '@media (max-width:600px){.x{y:z}}' in css and '@media (min-width:1400px){.w{max-width:1200px}}' in css, 'a phone rule and a wide-desk rule are left alone'
    assert '@media (min-width:768px) and (max-width:767px){.m{c:d}}' in css, 'a rule only for the in-between widths no longer applies anywhere'
    # the script that draws the page smaller is first in <body>, names the threshold, and acts only from 768 up to it
    assert re.search(r'<body class="b"><script data-sw-tablet>\(function\(\)\{var T=1024,', out) and 'w>=768&&w<T' in out and out.count('data-sw-tablet') == 1
    assert T.desk(out) == out, 'applied once'
    assert '.w{max-width:1200px}' in out and out.replace(re.search(r'<script data-sw-tablet>.*?</script>', out).group(0), '').count('<script>') == 1


def test_a_page_with_no_desk_threshold_in_reach_is_left_as_it_is():
    for page in ('<html><head><style>@media (max-width:600px){a{b:c}}</style></head><body></body></html>',
                 '<html><head><style>@media (min-width:1180px){a{b:c}}</style></head><body></body></html>',     # drawn at 0.65 on a tablet: nothing would read
                 '<html><head><style>@media (min-width:768px){a{b:c}}</style></head><body></body></html>'):       # already there
        assert T.threshold(page) is None and T.desk(page) == page


def test_only_templates_marked_in_their_needs_change_and_they_change_nowhere_else():
    d = json.loads((FIX / 'tallyfern.json').read_text(encoding='utf-8'))
    on = [t['slug'] for t in R.list_templates() if (t['needs'] or {}).get('tablet') == 'desk']
    assert len(on) >= 10 and all((t['needs'] or {}).get('tablet') in (None, 'desk') for t in R.list_templates())
    for slug in R.slugs():
        try:
            plain, page = R.render(slug, d, '', tablet=False), R.render(slug, d, '')
        except Exception:
            continue
        if slug not in on:
            assert page == plain and 'data-sw-tablet' not in page, slug
            continue
        t = T.threshold(plain)
        assert t and page == T.desk(plain) and 'data-sw-tablet' in page, slug
        # outside the styles' width rules and the one script, the page is byte for byte the template's
        strip = lambda s: re.sub(r'\((?:min|max)-width:\s*[0-9.]+px\)', '(w)', re.sub(r'<script data-sw-tablet>.*?</script>', '', s))
        assert strip(page) == strip(plain), slug
        assert 768 / t >= 0.69, '%s would be drawn at %.2f on a tablet' % (slug, 768 / t)


def test_the_design_kit_keeps_the_sizing_script_first_in_every_page_it_makes():
    d = json.loads((FIX / 'tallyfern.json').read_text(encoding='utf-8'))
    f = {k: v.decode() for k, v in K.kit(R.render('griffin', d, ''), name='Tally').items()}
    assert 'data-sw-tablet' not in f['design/design.js']
    for name in ('design/page.html', 'design/sections/02-open.html'):
        assert re.search(r'<body[^>]*><script data-sw-tablet>', f[name]), name
    assert '(min-width:768px)' in f['design/design.css']


@pytest.mark.skipif(not HAS_BROWSER, reason='needs node and Chrome (CHROME_PATH)')
def test_a_marked_template_stands_in_its_desk_composition_at_768_and_900_and_an_unmarked_one_is_read_as_it_was(tmp_path):
    S = _load('swarmsite_templates_stress', ROOT / 'lib' / 'templates' / 'stress.py')
    d = json.loads((FIX / 'tallyfern.json').read_text(encoding='utf-8'))
    S.stand_ins(d, tmp_path)
    base = tmp_path.resolve().as_uri() + '/'
    on, off = tmp_path / 'on.html', tmp_path / 'off.html'
    on.write_text(R.render('griffin', d, base), encoding='utf-8')
    off.write_text(R.render('griffin', d, base, tablet=False), encoding='utf-8')
    r = subprocess.run(['node', str(ROOT / 'lib' / 'qa' / 'composition.mjs'), str(on), str(off)], capture_output=True, text=True, timeout=300)
    res = json.loads(r.stdout.strip().splitlines()[-1])
    a, b = res[str(on.resolve())], res[str(off.resolve())]
    assert a['desk'] == {'768': True, '900': True}, a
    assert b['desk'] == {'768': False, '900': False}, b
    assert a['read']['1440'] == b['read']['1440'] and a['read']['390'] == b['read']['390'], 'the two compositions as designed are untouched'
