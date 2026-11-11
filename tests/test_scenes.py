"""Every scene draws from its slots alone, in every type system and palette scheme, and a palette never leaves text unreadable."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'studio'))
import scenes as S

PLAN = {'brand': {'name': 'Example', 'accent': '#2af6a0', 'night': '#0b0b0d'}, 'action': {'label': 'Start', 'url': 'https://x.test/'}, 'nav': [{'label': 'One', 'url': 'https://x.test/1'}],
        'scenes': [{'scene': 'open-statement', 'slots': {'kicker': 'A', 'h1': 'Never place / a *bad* bet', 'lede': 'L', 'facts': ['a', 'b', 'c', 'd']}},
                   {'scene': 'held-product', 'slots': {'label': 'L', 'items': [{'title': 'One', 'say': 's', 'panel': {'kind': 'rows', 'rows': [{'k': 'k', 'v': 'v'}]}}, {'title': 'Two', 'say': 's', 'panel': {'kind': 'bars', 'bars': [{'label': 'a', 'value': '1', 'share': .5}]}}, {'title': 'Three', 'say': 's', 'panel': {'kind': 'rows', 'rows': [{'k': 'k', 'v': 'v'}]}}]}},
                   {'scene': 'figures', 'slots': {'h2': 'Wins / and losses', 'figures': [{'value': '729', 'caption': 'c'}, {'value': '+6.28', 'unit': 'u', 'caption': 'c'}]}},
                   {'scene': 'rail', 'slots': {'words': 'Know the price'}}, {'scene': 'carte', 'slots': {'h2': 'The card', 'groups': [{'title': 'G', 'items': [{'name': 'Dish', 'price': '12 €'}]}]}},
                   {'scene': 'visit', 'slots': {'where': 'Street 1 / Town', 'rows': [{'k': 'Mon', 'v': '9–17'}]}}, {'scene': 'stack', 'slots': {'h2': 'Two plans', 'cards': [{'title': 'A', 'say': 's'}, {'title': 'B', 'say': 's'}]}},
                   {'scene': 'ledger', 'slots': {'h2': 'Answers', 'rows': [{'q': 'Q', 'a': 'A'}]}}, {'scene': 'index', 'slots': {'links': [{'label': 'L', 'url': 'https://x.test/2'}]}},
                   {'scene': 'statement', 'slots': {'text': 'One paragraph of the thesis that is read word by word as it passes.'}},
                   {'scene': 'steps', 'slots': {'h2': 'How / it goes', 'steps': [{'title': 'One', 'say': 's'}, {'title': 'Two', 'say': 's'}, {'title': 'Three', 'say': 's'}]}},
                   {'scene': 'voices', 'slots': {'quotes': [{'text': 'Good.', 'name': 'Ana'}]}}, {'scene': 'faq', 'slots': {'h2': 'Before', 'rows': [{'q': 'Q?', 'a': 'A.'}] * 6}},
                   {'scene': 'close', 'slots': {'line': 'Begin / today', 'legal': '©', 'wordmark': True}}]}


def test_a_scene_with_nothing_true_to_show_draws_nothing():
    page = S.page({**PLAN, 'scenes': [{'scene': 'open-statement', 'slots': {'h1': 'A'}}, {'scene': 'voices', 'slots': {'quotes': []}}, {'scene': 'close', 'slots': {'line': 'B'}}]}, {})
    assert 'voices' not in page.split('</style>')[-1]


def test_every_type_system_and_scheme_draws_the_page():
    for t in S.TYPE:
        for scheme in S.SCHEMES:
            page = S.page({**PLAN, 'type': t, 'scheme': scheme}, {})
            assert page.count('<h1') == 1 and page.count('<section') >= 8 and '<footer' in page and 'dv-held' in page and 'data-rise' in page, (t, scheme)


def test_text_is_readable_in_every_scheme_for_any_accent():
    for accent in ('#2af6a0', '#ffe600', '#0a2bff', '#ff488b', '#111111', '#f4f4f4'):
        for scheme in S.SCHEMES:
            p = S.palette(accent, '#0b0b0d', scheme)
            assert S.contrast(p['ink'], p['paper']) >= 7 and S.contrast(p['em'], p['paper']) >= 3 and S.contrast(p['on_accent'], p['accent']) >= 4.5 and S.contrast(p['mute'], p['paper']) >= 4.5, (accent, scheme, p)


def test_an_empty_slot_draws_nothing_and_a_picture_that_is_not_there_is_not_drawn():
    page = S.page({**PLAN, 'scenes': [{'scene': 'open-picture', 'slots': {'h1': 'A / line', 'image': 'missing'}}, {'scene': 'close', 'slots': {'line': 'End'}}]}, {})
    assert '<img' not in page and 'undefined' not in page and 'None' not in page


MORE = [{'scene': 'scatter', 'slots': {'h2': 'Recent / work', 'items': [{'image': f'p{k}', 'title': f'Piece {k}', 'tag': 'tag'} for k in range(4)]}},
        {'scene': 'bento', 'slots': {'h2': 'What / is here', 'tiles': [{'title': 'First', 'figure': '120', 'image': 'p0'}, {'title': 'Second', 'say': 's'}, {'title': 'Third'}, {'title': 'Fourth', 'say': 's'}]}},
        {'scene': 'kinetic-line', 'slots': {'rows': ['Made by', 'hand here']}}]
PICS = {f'p{k}': {'data': f'https://x.test/{k}.jpg', 'w': 1600, 'h': 1100} for k in range(4)}


def test_the_looser_scenes_draw_with_pictures_and_stay_whole_without_them():
    plan = {**PLAN, 'scenes': [PLAN['scenes'][0]] + MORE + [PLAN['scenes'][-1]]}
    for scheme in S.SCHEMES:
        page = S.page({**plan, 'scheme': scheme}, PICS)
        assert page.count('dv-k') >= 2 and page.count('dv-tilt') >= 3 and 'b-grid' in page and page.count('<img') >= 4, scheme
    bare = S.page(plan, {})
    assert '<img' not in bare and 'b-grid' in bare and 'undefined' not in bare and 'None' not in bare
    assert 'scatter' not in bare.split('</style>')[-1], 'a layout of pictures with no pictures is not drawn'


def test_a_kinetic_line_needs_two_rows_and_every_page_folds_over_its_footer():
    page = S.page({**PLAN, 'scenes': [PLAN['scenes'][0], {'scene': 'kinetic-line', 'slots': {'rows': ['Alone']}}, PLAN['scenes'][-1]]}, {})
    body = page.split('</style>')[-1]
    assert 'dv-kinetic' not in body and 'dv-sheet' in body and 'dv-under' in body and 'dv-grain' in body


def test_the_surface_that_leads_never_melts_into_the_page():
    """On a night page the night is the page itself: a tile drawn in it would vanish (seen on a real composition)."""
    for accent in ('#2af6a0', '#ffe600', '#0a2bff', '#ff488b', '#4a3fd8', '#7ab030'):
        for scheme in S.SCHEMES:
            p = S.palette(accent, '#0b0b0d', scheme)
            assert S.contrast(p['lead'], p['paper']) >= 2.2 and S.contrast(p['on_lead'], p['lead']) >= 4.5, (accent, scheme, p)
