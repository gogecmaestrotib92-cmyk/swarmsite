"""lib/templates/more.py: what of a client's page a template has no place for is carried under the template's own
sections — one even grid of short cards before the closing call, in the client's words, and the photographs the page did
not ask for as one strip — on every template, without a colour or a typeface of its own."""
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


def test_the_band_is_one_even_grid_of_short_cards_and_unused_photographs_are_one_strip():
    """Measured wide on 2026-11-17 (six software sites × three designs beside their references): the band was 46–66 %
    of a long page's words — 31 and 43 cards of every length after the closing call. It is one designed part: two,
    three, four or six cards, each a heading over a few lines; what is not a card is not on the page."""
    d = client()
    long = 'We keep the ledger for you. ' * 30
    note = lambda i: {'title': 'Note %d' % i, 'text': 'A line of the client\'s own that the template has no place for, number %d.' % i}
    d['more'] = {'sections': [{'title': 'How the week closes', 'text': long.strip()},                           # a passage
                              {'title': 'Who it is for <b>', 'text': 'Stall holders at the market.\n\nAnd those who help them.'},
                              {'title': '', 'text': 'What the opening goes on to say, a line without a heading.'},  # no heading
                              {'title': 'Open', 'text': 'Monday · Tuesday · Wednesday · every week of the year'},   # a run of labels
                              {'title': 'A heading that is a whole sentence and runs on past nine words', 'text': 'A line under a sentence set as a heading.'},
                              {'title': 'Short', 'text': 'Too short.'}, note(1), note(2)]}
    d['media']['photos'] = [{'src': 'media/p%d.jpg' % i, 'w': 1200, 'h': 800, 'alt': 'photo %d' % i} for i in range(1, 8)]
    page = '<main><section><h2>Ledger</h2><img src="../../media/p1.jpg"></section></main><footer>foot</footer>'
    out = M.add(d, page)
    assert out.index('data-more') < out.index('</main>') < out.index('<footer'), 'under the template\'s sections, above its foot'
    shown, held = M.cards(d)
    assert [x['title'] for x in shown] == ['Who it is for <b>', 'Note 1', 'Note 2'] and len(held) == 5, 'in page order; what is not a card is held'
    assert '<p>Stall holders at the market.</p><p>And those who help them.</p>' in out and 'Who it is for &lt;b&gt;' in out
    for gone in ('We keep the ledger', 'What the opening goes on', 'Monday', 'runs on past nine words', 'Too short.'):
        assert gone not in out, gone
    assert out.count('<article class="sw-card">') == 3 and 'style="--c:3"' in out and out.count('class="sw-cards') == 1
    assert not re.search(r'<div class="sw-more-in">\s*<p>', out) and all(k not in out.split('</style>')[1] for k in ('sw-lead', 'sw-wide', 'sw-chips', 'sw-col'))
    # the grid is even: 6, 4, 3 or 2 — never one card, never an odd row
    for have, show, cols in ((1, 0, 0), (2, 2, 2), (3, 3, 3), (4, 4, 2), (5, 4, 2), (6, 6, 3), (9, 6, 3), (40, 6, 3)):
        b = M.band({'more': {'sections': [note(i) for i in range(have)]}, 'media': {}}, page)
        assert b.count('<article') == show and (('style="--c:%d"' % cols) in b if show else b == ''), have
    assert 'sw-six' in M.band({'more': {'sections': [note(i) for i in range(6)]}, 'media': {}}, page)
    strip = re.search(r'<div class="sw-strip"[^>]*>(.*?)</div>', out).group(1)
    shown = re.findall(r'src="\.\./\.\./(media/p\d\.jpg)"', strip)
    assert 'media/p1.jpg' not in shown and shown == ['media/p%d.jpg' % i for i in range(2, 8)], 'the photographs the page did not ask for, in order, a whole number of rows'
    css = re.search(r'<style>(.*?)</style>', out).group(1)
    assert not re.search(r'#[0-9a-f]{3,8}\b|rgb\(|font-family', css), 'no colour and no typeface of its own: the page\'s ground, ink and heading face'
    assert M.add(d, out.replace('</main>', '')).count('data-more') > out.count('data-more') - 3   # a page with no <main>: before its foot
    # a strip is photographs that read: not one marked small, dim (near-black) or lettered (a crest, a flyer)
    marked = dict(d, media={**d['media'], 'photos': [dict(p, **({'small': True} if i == 1 else {'dim': True} if i == 2 else {'lettering': True} if i == 3 else {})) for i, p in enumerate(d['media']['photos'])]})
    strip = re.search(r'<div class="sw-strip"[^>]*>(.*?)</div>', M.band(marked, page)).group(1)
    assert re.findall(r'media/p\d\.jpg', strip) == ['media/p5.jpg', 'media/p6.jpg', 'media/p7.jpg']
    two = dict(d, more={}, media={**d['media'], 'photos': d['media']['photos'][:3]})
    assert M.band(two, page) == '', 'two photographs left are not a strip'


def test_the_band_stands_before_the_closing_call_not_after_it():
    """a page ends on its call and its foot: where the page's last section is a closing call (a link or a button, few
    words, no section inside it), the band is written before it; where it is something else, before the foot as before"""
    d = {'more': {'sections': [{'title': 'Note %d' % i, 'text': 'A line of the client\'s own that the template has no place for.'} for i in range(3)]}, 'media': {}}
    head = '<main><section class="a"><h2>Ledger</h2><p>%s</p></section>' % ('word ' * 80)
    call = '<section class="close"><h2>Start today</h2><a href="/go">Start</a></section>'
    out = M.add(d, head + call + '</main><footer>foot</footer>')
    assert out.index('class="a"') < out.index('data-more') < out.index('class="close"') < out.index('<footer')
    out = M.add(d, head + call + '<script>var x = "words in a script are not words";</script></main><footer>foot</footer>')
    assert out.index('data-more') < out.index('class="close"')
    for last in ('<section class="faq"><h2>Questions</h2><p>%s</p><a href="/x">More</a></section>' % ('word ' * 70),     # too many words to be a call
                 '<section class="figs"><h2>Numbers</h2><p>12 teams</p></section>',                                    # nothing to press
                 '<section class="wrap"><section class="close"><h2>Start</h2><a href="/go">Start</a></section><p>after</p></section>'):   # a section holding others
        out = M.add(d, head + last + '</main><footer>foot</footer>')
        assert out.index('data-more') > out.index(last[:22]) and out.index('data-more') < out.index('</main>'), last[:30]
    inside = '<section class="close"><h2>Start today</h2><a href="/go">Start</a><div class="w"><footer>foot</footer></div></section></main>'
    out = M.add(d, head + inside)
    assert out.index('class="a"') < out.index('data-more') < out.index('class="close"'), 'a foot inside the closing section: the band is before that section, not in it'
    out = M.add(d, head + call + '<p>A line after the call.</p></main><footer>foot</footer>')
    assert out.index('data-more') > out.index('class="close"'), 'words after the last section: it is not the page\'s end'


@pytest.mark.parametrize('slug', R.slugs())
def test_every_template_carries_the_band(slug):
    d = client()
    d['more'] = {'sections': [{'title': 'What the template has no place for', 'text': 'Carried under its sections, in the words of the page.'},
                              {'title': 'And a second thing', 'text': 'A card never stands alone: the grid is even.'}]}
    out = R.render(slug, d, '')
    assert 'What the template has no place for' in out and out.count('class="sw-more"') == 1 and out.index('class="sw-more"') < out.rindex('<footer')
    assert R.render(slug, d, '') == out, 'pure'


def test_the_band_reads_on_a_page_whose_own_ink_would_not(tmp_path):
    """a template whose body ink is its ground's colour (each of its sections sets its own): the band's words are set
    near-white or near-black by the ground they stand on — read by the gate on pixels, at both widths"""
    G = _load('swarmsite_templates_gate', ROOT / 'lib' / 'templates' / 'gate.py')
    d = {'more': {'sections': [{'title': 'What is left', 'text': 'Carried under the sections, in the words of the page. ' * 4}, {'title': 'A note', 'text': 'A short line of the page, long enough to be a card.'}, {'title': 'Another', 'text': 'A second short line of the page, also a card.'}]}, 'media': {}}
    for name, ground in (('dark', '#101214'), ('light', '#f4f1ea')):
        page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;font:18px/1.5 Arial;background:%s;color:%s}'
                'section.t{padding:80px 24px;color:%s}</style></head><body><main><section class="t"><h1>One heading here</h1><p>The template sets its own ink, a section at a time.</p></section></main><footer></footer></body></html>'
                % (ground, ground, '#f5f5f5' if name == 'dark' else '#111'))
        f = tmp_path / (name + '.html')
        f.write_text(M.add(d, page), encoding='utf-8')
        res = G.check([f])[0]
        assert res['failed'] != ['tool'] and 'legible' not in res['failed'], (name, res.get('checks', {}).get('legible'))
