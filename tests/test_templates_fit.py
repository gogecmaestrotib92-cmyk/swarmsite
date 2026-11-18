"""lib/templates/fit.py: each slot of the contract holds what the slot is for, whichever hand filled it (adapter, reader,
assigned blocks, form). Found on 2026-11-17 reading six software sites beside their references: `18+` over `only` as a
figure, a question as a trust phrase in the logo row, `01 1` on a step, a heading cut into a figure, a card repeating
another section's heading, two paragraphs run together."""
import importlib.util
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


F = _load('swarmsite_templates_fit', ROOT / 'lib' / 'templates' / 'fit.py')


def test_a_steps_own_number_is_not_its_name():
    for k in ('1', '01', '3.', 'Step 2', 'STEP 02', '#4', '02)', 'Korak 1'):
        assert F.step_key(k, 'Choose your topic') == '', k
    assert F.step_key('01 — DRAW', 'Diagram the play. Once.') == 'DRAW'
    assert F.step_key('02 · Film', 'x') == 'Film' and F.step_key('One match', 'x') == 'One match'
    assert F.step_key('Pick a style', 'Pick a style') == '', 'the title again is not a name beside the title'
    assert F.step_key('24/7 support', 'x') == '24/7 support' and F.step_key('3D preview', 'x') == '3D preview', 'a name that starts with a number stands'
    d = {'steps': {'title': 'Three steps', 'items': [{'k': '1', 'title': 'Drop'}, {'k': '02 — PICK', 'title': 'Pick a style'}, {'title': 'Download'}]}}
    notes = F.fit(d)
    assert [s.get('k') for s in d['steps']['items']] == [None, 'PICK', None] and any('steps' in n for n in notes)


def test_a_figure_is_a_quantity_with_what_it_counts():
    ok = lambda v, l: F.figure({'v': v, 'l': l})[0]
    assert ok('42%', 'Hit rate') and ok('5,000', 'Runs a game') and ok('3+', 'Points apart') and ok('18+', 'sports covered') and ok('24h', 'Auto-delete')
    assert not ok('18+', 'only') and not ok('21+', '') and not ok('7', 'only') and not ok('', 'Hit rate')
    assert not ok('8', 'Book Types, One Platform'), 'a heading cut after its number'
    assert F.figure({'v': '18+', 'l': 'only'})[1] == '18+ only'


def test_a_trust_phrase_is_one_short_assurance():
    ok = lambda t: F.trust(t)[0]
    assert ok('No credit card required.') and ok('Free preview — no account needed') and ok('4.8★ ON G2') and ok('Files deleted after 24h')
    assert not ok('IS THIS BETTING ADVICE? No.') and not ok('Fast. Private. Yours to keep.') and not ok('We never share, sell or rent your data to anyone at all')
    assert F.trust('21+ only. Probabilities, not guarantees.') == (False, '21+ only. Probabilities, not guarantees.')


def test_an_age_notice_moves_to_the_legal_line_and_is_never_lost():
    d = {'figures': [{'v': '42%', 'l': 'Hit rate'}, {'v': '18+', 'l': 'only'}, {'v': '1.80', 'l': 'AVG ODDS'}], 'trust': ['No card', '18+. Play responsibly.'],
         'foot': {'legal': '© 2026 Tallyfern', 'links': []}}
    F.fit(d)
    assert [f['v'] for f in d['figures']] == ['42%', '1.80'] and d['trust'] == ['No card']
    assert d['foot']['legal'] == '© 2026 Tallyfern · 18+ only.', 'said once, though the page printed it twice'
    again = F.fit(d)
    assert d['foot']['legal'] == '© 2026 Tallyfern · 18+ only.' and not again, 'a second pass changes nothing'
    d = {'trust': ['21+ only. Probabilities, not guarantees.', 'Cancel anytime']}
    F.fit(d)
    assert d['foot']['legal'] == '21+ only. Probabilities, not guarantees.' and d['trust'] == ['Cancel anytime']
    d = {'figures': [{'v': '18+', 'l': 'only'}], 'foot': {'legal': 'For adults 18+ in licensed regions'}}
    F.fit(d)
    assert d['foot']['legal'] == 'For adults 18+ in licensed regions' and d['figures'] == []


def test_a_card_does_not_repeat_another_sections_heading():
    d = {'steps': {'title': 'Completely agentic, end to end.', 'items': [{'title': 'Something changes'}]},
         'links': [{'t': 'Completely agentic, end to end.', 'd': 'Something changes.', 'h': None}, {'t': 'something changes', 'd': 'x'}, {'t': 'The editor', 'd': 'Click and type.', 'h': 'https://x.example/docs'}]}
    F.fit(d)
    assert [x['t'] for x in d['links']] == ['The editor']


def test_two_sentences_run_together_get_their_space_and_addresses_are_left_alone():
    long = 'Upload directly from your device or point to a cloud URL.Plays are drawn in our editor.Recreate your playbook quickly.'
    d = {'faq': {'title': 'Before you ask.', 'items': [{'q': 'Can I import?', 'a': long}]},
         'hero': {'title': 'Built on Node.Js and friends', 'text': 'Works with developerhub.io and Next.js out of the box, on any plan you like.', 'primary': {'t': 'Start', 'h': 'https://x.example/a.Html?b=Yes.No'}},
         'brand': {'name': 'x', 'home': 'https://x.example/'}}
    F.fit(d)
    assert d['faq']['items'][0]['a'] == 'Upload directly from your device or point to a cloud URL. Plays are drawn in our editor. Recreate your playbook quickly.'
    assert d['hero']['text'] == 'Works with developerhub.io and Next.js out of the box, on any plan you like.'
    assert d['hero']['title'] == 'Built on Node.Js and friends' and d['hero']['primary']['h'] == 'https://x.example/a.Html?b=Yes.No'


def test_a_page_with_nothing_misplaced_is_left_as_it_is():
    d = {'trust': ['No card', 'Cancel anytime'], 'figures': [{'v': '27,000+', 'l': 'Docs written'}], 'steps': {'title': 'How', 'items': [{'k': 'DRAW', 'title': 'Diagram'}]},
         'links': [{'t': 'Docs', 'd': 'Read them.', 'h': 'https://x.example'}], 'foot': {'legal': '© 2026'}}
    import copy
    was = copy.deepcopy(d)
    assert F.fit(d) == [] and d == was
    assert F.fit({}) == []
