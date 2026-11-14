"""The reader places the page's blocks by number (lib/templates/assign.py): it writes no word, and no word is lost."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'templates'))
import assign as A  # noqa: E402


def blocks():
    rows = [('a', 'Skip to content', 'main'), ('h', 'Millbrook Halt on the old north road', 'main'), ('p', 'At the crossing of the old north road stands our stop Millbrook Halt.', 'main'),
            ('a', 'Play', 'main'), ('h', 'Our services', 'main'), ('li', 'Cafe', 'main'), ('li', 'Free parking', 'main'), ('li', 'Showers', 'main'),
            ('h', 'Rooms for weddings', 'main'), ('p', 'A hall for two hundred guests, with its own kitchen and a garden behind it.', 'main'), ('img', 'The hall', 'main'),
            ('p', 'Open every day of the year.', 'main'), ('h', 'Come by', 'main'), ('a', 'Contact us', 'main'), ('p', '© Millbrook Halt Ltd', 'footer'), ('p', 'Open every day of the year.', 'main')]
    out = []
    for i, (k, t, r) in enumerate(rows):
        b = {'i': i, 'kind': k, 'text': t, 'region': r}
        if k == 'h':
            b['level'] = 1 if i == 1 else 2
        if k == 'li':
            b['list'] = 1
        if k == 'img':
            b.update(src='https://x.test/hall.jpg', w=800, h=500)
        out.append(b)
    out[15]['same'] = 11
    return out


RAW = {'hero': {'title': 1, 'text': [2]}, 'features': {'title': 4, 'items': [{'t': 5}, {'t': 6}, {'t': 7}]},
       'close': {'title': 12, 'button': 13}, 'skip': [{'n': [0, 3], 'why': 'interface'}]}


def test_numbers_become_the_blocks_own_words():
    r = A.resolve(RAW, blocks())
    assert r['page']['hero'] == {'title': 'Millbrook Halt on the old north road', 'text': 'At the crossing of the old north road stands our stop Millbrook Halt.'}
    assert [x['t'] for x in r['page']['features']['items']] == ['Cafe', 'Free parking', 'Showers']
    assert r['page']['close']['button'] == 'Contact us'


def test_what_is_placed_nowhere_is_carried_in_page_order_with_its_picture():
    r = A.resolve(RAW, blocks())
    assert [(s['title'], s['text'], s['imgs']) for s in r['rest']] == [
        ('Rooms for weddings', 'A hall for two hundred guests, with its own kitchen and a garden behind it.\n\nOpen every day of the year.', ['https://x.test/hall.jpg'])]
    m = r['measure']
    assert m['placed'] + m['rest'] + m['skipped'] == m['words'] and m['kept'] == 1, m     # the skipped blocks here are lone links, which are not counted as the page's words


def test_a_number_that_is_not_a_listed_block_or_is_used_twice_is_dropped():
    raw = {'hero': {'title': 1, 'text': [2, 99, 14, 'x', True]}, 'statement': {'title': 1, 'text': [9]}}
    r = A.resolve(raw, blocks())
    assert r['page']['hero']['text'] == 'At the crossing of the old north road stands our stop Millbrook Halt.'      # 99 is no block, 14 is the foot's
    assert 'statement' not in r['page'] and any(s['title'] == 'Rooms for weddings' and 'two hundred guests' in s['text'] for s in r['rest'])


def test_a_place_too_thin_gives_its_blocks_back():
    r = A.resolve({'hero': {'title': 1}, 'features': {'title': 4, 'items': [{'t': 5}, {'t': 6}]}}, blocks())
    assert 'features' not in r['page']
    assert any(s['title'] == 'Our services' and s['text'] == 'Cafe\nFree parking\nShowers' for s in r['rest'])


def test_skipped_words_are_counted_and_named_never_silent():
    r = A.resolve({'hero': {'title': 1}, 'skip': [{'n': [9], 'why': 'demo'}]}, blocks())
    m = r['measure']
    assert m['skipped'] == 15 and m['kept'] < 1 and m['skipped_blocks'][0]['i'] == 9 and m['skipped_blocks'][0]['why'] == 'demo'


def test_the_reader_is_shown_each_block_once_and_only_the_pages_own_regions():
    b = A.brief(blocks())
    assert '14 ' not in b.split('\n')[-1] and 'Millbrook Halt Ltd' not in b and b.count('Open every day of the year.') == 1
    assert '1 h1 "Millbrook Halt on the old north road"' in b and '5 li·1 "Cafe"' in b and '10 img 800x500 "The hall"' in b


def test_garbage_from_the_model_gives_an_empty_page_and_the_whole_rest():
    for raw in (None, [], 'x', {'hero': 'x', 'features': [1], 'quotes': {'q': 1}, 'skip': 'all'}):
        r = A.resolve(raw, blocks())
        assert r['page'] == {} and r['measure']['kept'] == 1
