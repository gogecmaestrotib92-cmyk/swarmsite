"""The page's data completed from the capture's numbered blocks (lib/templates/fromblocks.py): a place the adapter
left empty is filled only by blocks that fit it whole, and what the data does not say yet is carried below."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'templates'))
import adapt  # noqa: E402
import fromblocks as F  # noqa: E402

LONG = ('Our hall seats two hundred guests. It has its own kitchen and a garden behind it. '
        'Coaches park at the door. The terrace looks over the old north road and the hills beyond it. We open it every day of the year.')


def seed(raw):
    rows = [('h', 'Millbrook Halt on the old north road'), ('p', 'At the crossing of the old north road stands our stop.'),
            ('h', 'Our services'), ('li', 'Cafe'), ('li', 'Free parking'), ('li', 'Showers'),
            ('h', 'Rooms for weddings'), ('p', LONG), ('p', 'Ask for the events desk.'),
            ('h', 'What drivers say'), ('quote', 'The best stop on the road, and the cleanest by far.'), ('p', 'A. Driver'),
            ('p', 'Demo label'), ('h', 'Opening hours'), ('li', 'Monday to Friday, from six in the morning until midnight'), ('li', 'Saturday and Sunday, all day and all night')]
    blocks = [{'i': i, 'kind': k, 'text': t, 'region': 'main', **({'level': 1 if i == 0 else 2} if k == 'h' else {}), **({'list': 1 if i < 6 else 2} if k == 'li' else {})} for i, (k, t) in enumerate(rows)]
    return {'blocks': {'blocks': blocks}, 'assign': {'raw': raw}}


def data():
    return {'brand': {'name': 'Millbrook Halt'}, 'hero': {'title': 'Millbrook Halt on the old north road', 'text': 'At the crossing of the old north road stands our stop.'},
            'statement': {'title': 'Rooms for weddings', 'text': 'Our hall seats two hundred guests. It has its own kitchen and a garden behind it.'},
            'more': {'sections': [{'title': 'Old', 'text': 'from the flat text'}]}, '_adapter': {}}


RAW = {'hero': {'title': 0, 'text': [1]}, 'features': {'title': 2, 'items': [{'t': 3}, {'t': 4}, {'t': 5}]},
       'quotes': [{'q': [10], 'name': 11}], 'skip': [{'n': [12], 'why': 'demo'}],
       'sections': [{'title': 6, 'text': [7, 8]}, {'title': 13, 'text': [14, 15]}]}


def run(d, raw=RAW):
    rules = []
    F.complete(d, seed(raw), adapt._key, adapt.sentences, lambda title: [], rules)
    return rules


def test_an_empty_place_is_filled_from_the_blocks_and_a_filled_one_is_left_alone():
    d = data()
    run(d)
    assert [i['t'] for i in d['features']['items']] == ['Cafe', 'Free parking', 'Showers'] and d['features']['title'] == 'Our services'
    assert d['quotes'][0]['q'] == 'The best stop on the road, and the cleanest by far.' and d['quotes'][0]['name'] == 'A. Driver'
    assert d['statement']['title'] == 'Rooms for weddings' and d['statement']['text'].endswith('behind it.')
    assert d['_adapter']['blocks']['filled'] == ['features', 'quotes']


def test_what_the_data_does_not_say_is_carried_below_once_and_in_page_order():
    d = data()
    run(d)
    secs = d['more']['sections']
    # the passage whose opening the statement says: the rest of it, under no second heading; what was skipped is not there
    assert secs[0] == {'title': '', 'text': 'Coaches park at the door. The terrace looks over the old north road and the hills beyond it. We open it every day of the year.\n\nAsk for the events desk.'}
    assert secs[1] == {'title': 'Opening hours', 'text': 'Monday to Friday, from six in the morning until midnight · Saturday and Sunday, all day and all night'}
    assert not any('Demo label' in s['text'] for s in secs)
    # what the adapter's own rules had carried and the blocks do not say stays, after them; what they do say is not doubled
    assert len(secs) == 3 and secs[2] == {'title': 'Old', 'text': 'from the flat text'}
    d2 = data()
    d2['more']['sections'].append({'title': 'Opening hours', 'text': 'Whatever the flat text made of it.'})
    run(d2)
    assert [s['title'] for s in d2['more']['sections']] == ['', 'Opening hours', 'Old']
    assert not any('two hundred guests' in s['text'] or 'Cafe' in s['text'] for s in secs), 'said once'


def test_blocks_that_do_not_fit_a_place_whole_are_not_cut_into_it():
    d = data()
    del d['statement']
    run(d, {'hero': {'title': 0}, 'statement': {'title': 6, 'text': [7, 8]}})        # two paragraphs: more than a statement holds
    assert 'statement' not in d
    sec = next(s for s in d['more']['sections'] if s['title'] == 'Rooms for weddings')
    assert sec['text'] == LONG + '\n\nAsk for the events desk.'


def test_no_placement_or_no_blocks_changes_nothing():
    for sd in ({}, {'blocks': {'blocks': []}, 'assign': {'raw': RAW}}, {'blocks': seed(RAW)['blocks'], 'assign': {}}):
        d = data()
        F.complete(d, sd, adapt._key, adapt.sentences, lambda t: [], [])
        assert d == data()


def test_the_result_is_valid_data():
    d = data()
    run(d)
    assert not [e for e in adapt.validate(d) if 'more' in e or 'features' in e or 'quotes' in e]
