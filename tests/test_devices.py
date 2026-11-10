"""Every device of the library says where it comes from, what it needs and when to use it, and carries its own code."""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'devices'))
import registry as R

FIELDS = ('id', 'name', 'kind', 'sees', 'needs', 'use', 'avoid', 'pairs', 'markup', 'css')


def test_every_device_is_complete():
    for d in R.DEVICES.values():
        assert all(d.get(k) not in (None, '') for k in FIELDS if k != 'pairs'), d['id']
        assert isinstance(d.get('pairs'), list) and all(p in R.DEVICES for p in d['pairs']), d['id']
        assert 'measured' in d and (d['measured'] is None or d['measured'].get('source')), d['id']
        if d['measured'] is None: assert d.get('seen'), f"{d['id']}: an unmeasured device says where it was seen and that it is unmeasured"


def test_no_device_hides_content_without_its_script():
    """Whatever is hidden to be revealed is hidden only under .dv — the class the script adds."""
    for d in R.DEVICES.values():
        for rule in re.findall(r'([^{}]+)\{([^{}]*)\}', d['css']):
            hides = re.search(r'opacity:\s*0(?![.\d])|transform:\s*(translateY\(1\d\d%|scaleX\(0\))', rule[1])
            if hides: assert rule[0].strip().startswith('.dv ') or 'dv-peek-img' in rule[0], f"{d['id']}: {rule[0].strip()} hides content without the script"


def test_bundle_carries_each_device_once_and_the_demo_uses_them():
    css, js = R.bundle(['line-rise', 'held-index'])
    assert css.count('.dv-held{display:grid') == 1 and '.dv-rail' not in css and 'dv-held' in js
    page = R.demo()
    assert all(f'id="{i}"' in page for i in ('line-rise', 'held-index', 'stack-cards', 'side-rail')) and page.count('<h1') == 1


def test_the_catalogue_is_what_a_builder_reads():
    cat = R.catalogue()
    assert len(cat) == len(R.DEVICES) and all('css' not in c and 'js' not in c and c['markup'] for c in cat)
