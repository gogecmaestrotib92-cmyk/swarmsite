"""lib/templates/feel.py: every page answers a hand the same way, each behaviour only where the template has not set it."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


F = _load('swarmsite_templates_feel', ROOT / 'lib' / 'templates' / 'feel.py')
R = _load('swarmsite_templates_registry_feel', ROOT / 'lib' / 'templates' / 'registry.py')
PAGE = '<!doctype html><html><head><title>t</title><style>%s</style></head><body><a href="#x">x</a></body></html>'


def test_it_stands_first_in_head_once():
    out = F.add(PAGE % '')
    assert out.index('<style data-sw-feel>') < out.index('<title>') and out.count('data-sw-feel') == 2
    assert F.add(out) == out
    assert F.add('no head here') == 'no head here'


def test_a_templates_own_press_and_anchor_landing_stand():
    assert 'PRESS=true,ANCHOR=true' in F.add(PAGE % '.b{color:red}')
    assert 'PRESS=false' in F.add(PAGE % '.b:active{transform:scale(.97)}')
    assert 'ANCHOR=false' in F.add(PAGE % 'html{scroll-padding-top:80px}')


def test_every_template_carries_it():
    d = json.loads((ROOT / 'tests' / 'fixtures' / 'templates' / 'pagewright.json').read_text())
    for slug in R.slugs():
        assert '<script data-sw-feel>' in R.render(slug, d), slug
