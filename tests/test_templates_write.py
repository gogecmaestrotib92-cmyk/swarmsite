"""The form path's writer (lib/templates/write.py): it may describe and invite, and may not state a fact. `merge` is
the guard: only fields the visitor left empty are filled, and a draft with a number they did not type, a claim of
rank or result, or a machine's filler word is dropped."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'templates'))
import form as F  # noqa: E402
import write as W  # noqa: E402

FORM = {'name': 'Tallyfern', 'sentence': 'The books of a stall, kept in an evening', 'kind': 'software', 'lang': 'en',
        'offers': [{'name': 'Receipts'}, {'name': 'Month on a page', 'note': 'Read the month on one page.'}, {'name': 'Export', 'price': '9'}]}
GOOD = {'lede': 'A ledger for people who run a market stall and would rather sell than do sums.',
        'about': {'title': 'Made for one stall or a row', 'text': 'Tallyfern keeps the books of a small stall. It is for traders who close the day tired and want the numbers in order by morning.'},
        'offers': [{'i': 0, 'note': 'Keep each receipt where you can find it again.'}, {'i': 1, 'note': 'Should not replace what they wrote.'}, {'i': 2, 'note': 'Send the month to your accountant.'}],
        'closing': {'title': 'Start with tonight\'s receipts.', 'text': 'Open a ledger and see the week take shape.'}}


def test_only_what_the_visitor_left_empty_is_filled_and_it_is_marked():
    m = W.merge(FORM, GOOD)
    assert m['draft']['written'] == ['lede', 'about', 'closing', 'offers.0.note', 'offers.2.note']
    assert [o.get('note') for o in m['offers']] == ['Keep each receipt where you can find it again.', 'Read the month on one page.', 'Send the month to your accountant.']
    assert m['sentence'] == FORM['sentence'] and FORM['offers'][0].get('note') is None, 'the typed form is not changed'
    d, notes = F.from_form(m)
    assert d['hero'] == {'title': FORM['sentence'], 'text': GOOD['lede']}
    assert d['statement'] == {'title': 'Made for one stall or a row', 'text': GOOD['about']['text']} and d['close']['title'] == "Start with tonight's receipts"
    assert notes['written'] == ['hero.text', 'statement', 'close', 'offers.0.note', 'offers.2.note'] and any(r.startswith('draft:') for r in notes['rules'])


def test_a_fact_the_visitor_did_not_type_is_not_written():
    bad = {'lede': 'Trusted by 4,210 stalls across the country.', 'about': {'title': 'The best ledger for stalls', 'text': 'It is a ledger.'},
           'offers': [{'i': 0, 'note': 'Saves 12 hours a month.'}, {'i': 2, 'note': 'A seamless export, guaranteed.'}, {'i': 9, 'note': 'No such offer.'}, {'i': True, 'note': 'x'}, 'x'],
           'closing': {'title': 'Join us today!', 'text': 'It costs 9 a month.'}}
    m = W.merge(FORM, bad)
    assert 'draft' not in m and [o.get('note') for o in m['offers']] == [None, 'Read the month on one page.', None]
    # a number the visitor did type may be said again; a text too long is cut at a sentence, never mid-word
    ok = W.merge(FORM, {'lede': 'Export costs 9 a month. ' + 'It keeps the books in order for the trader who would rather sell. ' * 4})
    assert ok['draft']['lede'].startswith('Export costs 9 a month.') and ok['draft']['lede'].endswith('.') and len(ok['draft']['lede']) <= W.CAP['lede']


def test_garbage_from_the_model_changes_nothing():
    for raw in (None, 'x', [], {'lede': 5, 'about': 'x', 'offers': {'i': 0}, 'closing': []}):
        assert W.merge(FORM, raw) == FORM
    d, notes = F.from_form(FORM)
    assert 'text' not in d['hero'] and 'statement' not in d and notes['written'] == []


def test_the_brief_says_which_offers_have_no_words_and_carries_no_draft():
    b = W.brief(W.merge(FORM, GOOD))
    assert '0. Receipts — described' in b and 'Tallyfern' in b and 'do not repeat it' in b
    assert '1. Month on a page — described: Read the month on one page.' in W.brief(FORM) and '0. Receipts — NOT described' in W.brief(FORM)
