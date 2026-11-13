"""lib/templates/more.py: what of a client's page a template has no place for is carried under the template's own
sections — the leftover sections whole, in the client's words, and the photographs the page did not ask for as one
strip — on every template, without a colour or a typeface of its own."""
import importlib.util
import json
import re
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


R = _load('swarmsite_templates_registry', ROOT / 'lib' / 'templates' / 'registry.py')
M = _load('swarmsite_templates_more', ROOT / 'lib' / 'templates' / 'more.py')
FIX = ROOT / 'tests' / 'fixtures' / 'templates'


def client(name='tallyfern'):
    return json.loads((FIX / (name + '.json')).read_text(encoding='utf-8'))


def test_no_leftovers_no_band():
    d = client()
    d.pop('more', None)
    page = '<main><img src="../../%s"></main><footer></footer>' % '"><img src="../../'.join(p['src'] for p in d['media'].get('photos') or [])
    assert M.band(d, page) == '' and M.add(d, page) == page


def test_leftover_sections_stand_whole_and_unused_photographs_are_one_strip():
    d = client()
    long = 'We keep the ledger for you. ' * 30
    d['more'] = {'sections': [{'title': 'How the week closes', 'text': long.strip()}, {'title': 'Who it is for <b>', 'text': 'Stall holders.\n\nAnd those who help them.'}, {'title': '', 'text': 'no heading: not set'}]}
    d['media']['photos'] = [{'src': 'media/p%d.jpg' % i, 'w': 1200, 'h': 800, 'alt': 'photo %d' % i} for i in range(1, 8)]
    page = '<main><section><h2>Ledger</h2><img src="../../media/p1.jpg"></section></main><footer>foot</footer>'
    out = M.add(d, page)
    assert out.index('data-more') < out.index('</main>') < out.index('<footer'), 'under the template\'s sections, above its foot'
    assert long.strip() in out and '<p>Stall holders.</p><p>And those who help them.</p>' in out and 'Who it is for &lt;b&gt;' in out and 'no heading' not in out
    strip = re.search(r'<div class="sw-strip"[^>]*>(.*?)</div>', out).group(1)
    shown = re.findall(r'src="\.\./\.\./(media/p\d\.jpg)"', strip)
    assert 'media/p1.jpg' not in shown and shown == ['media/p%d.jpg' % i for i in range(2, 8)], 'the photographs the page did not ask for, in order, a whole number of rows'
    css = re.search(r'<style>(.*?)</style>', out).group(1)
    assert not re.search(r'#[0-9a-f]{3,8}\b|rgb\(|font-family', css), 'no colour and no typeface of its own: the page\'s ground, ink and heading face'
    assert M.add(d, out.replace('</main>', '')).count('data-more') > out.count('data-more') - 3   # a page with no <main>: before its foot
    # short notes stand together as a grid; a passage, or a section with its own picture, is a row — its picture across the whole width under it
    notes = [{'title': 'Note %d' % i, 'text': 'A short line.'} for i in range(1, 4)]
    d2 = dict(d, more={'sections': [{'title': 'Alone', 'text': 'Short.'}, {'title': 'The yard', 'text': long.strip(), 'imgs': [{'src': 'media/p7.jpg', 'w': 1600, 'h': 900, 'alt': 'the yard'}]}] + notes})
    out2 = M.band(d2, page)
    assert out2.count('class="sw-more-grid"') == 1 and out2.count('<h3>') == 3 and out2.count('<h2>') == 2
    assert out2.index('The yard') < out2.index('class="sw-more-pic"') and 'media/p7.jpg' not in re.search(r'<div class="sw-strip"[^>]*>(.*?)</div>', out2).group(1), 'its own picture is not also in the strip'
    assert '<figure' not in M.band(dict(d2, more={'sections': [dict(d2['more']['sections'][1], imgs=[{'src': 'media/p1.jpg'}])]}), page), 'a picture the template already shows is not shown again'
    small = M.band(dict(d, more={'sections': [{'title': 'A cover', 'text': '', 'imgs': [{'src': 'media/p6.jpg', 'w': 600, 'h': 900}]}]}), page)
    assert 'class="sw-more-own" style="max-width:600px"' in small and '<figure class="sw-more-pic">' not in small, 'a small or upright picture stands at its own size'
    halls = M.band(dict(d, more={'sections': [{'title': 'The halls', 'text': '', 'imgs': [{'src': 'media/p%d.jpg' % i, 'w': 800, 'h': 600} for i in (5, 6, 7)]}]}), page)
    assert 'The halls' in halls and halls.count('media/p5.jpg') == 1 and 'style="--n:3;' in halls, 'a heading over its own pictures, no words: a section too'
    two = dict(d, more={}, media={**d['media'], 'photos': d['media']['photos'][:3]})
    assert M.band(two, page) == '', 'two photographs left are not a strip'


@pytest.mark.parametrize('slug', R.slugs())
def test_every_template_carries_the_band(slug):
    d = client()
    d['more'] = {'sections': [{'title': 'What the template has no place for', 'text': 'Carried under its sections.'}]}
    out = R.render(slug, d, '')
    assert 'What the template has no place for' in out and out.count('class="sw-more"') == 1 and out.index('class="sw-more"') < out.rindex('<footer')
    assert R.render(slug, d, '') == out, 'pure'


def test_the_band_reads_on_a_page_whose_own_ink_would_not(tmp_path):
    """a template whose body ink is its ground's colour (each of its sections sets its own): the band's words are set
    near-white or near-black by the ground they stand on — read by the gate on pixels, at both widths"""
    G = _load('swarmsite_templates_gate', ROOT / 'lib' / 'templates' / 'gate.py')
    d = {'more': {'sections': [{'title': 'What is left', 'text': 'Carried under the sections, in the words of the page. ' * 4}, {'title': 'A note', 'text': 'Short.'}, {'title': 'Another', 'text': 'Short too.'}]}, 'media': {}}
    for name, ground in (('dark', '#101214'), ('light', '#f4f1ea')):
        page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;font:18px/1.5 Arial;background:%s;color:%s}'
                'section.t{padding:80px 24px;color:%s}</style></head><body><main><section class="t"><h1>One heading here</h1><p>The template sets its own ink, a section at a time.</p></section></main><footer></footer></body></html>'
                % (ground, ground, '#f5f5f5' if name == 'dark' else '#111'))
        f = tmp_path / (name + '.html')
        f.write_text(M.add(d, page), encoding='utf-8')
        res = G.check([f])[0]
        assert res['failed'] != ['tool'] and 'legible' not in res['failed'], (name, res.get('checks', {}).get('legible'))
