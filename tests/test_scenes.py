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


def test_a_collage_takes_three_pictures_and_no_plan_gets_a_drawn_underline():
    import scenes as SC
    px = 'data:image/png;base64,iVBORw0KGgo='
    images = {k: {'id': k, 'data': px, 'w': w, 'h': 800} for k, w in (('a', 1000), ('b', 1600), ('c', 1200))}
    def plan(pics, **more): return {'brand': {'name': 'X', 'accent': '#2a8f5a'}, **more, 'scenes': [{'scene': 'open-statement', 'slots': {'h1': 'A place / for *everyone*'}}, {'scene': 'collage', 'slots': {'h2': 'Three / *rooms*', 'pictures': [{'image': k} for k in pics]}}, {'scene': 'close', 'slots': {'line': 'Come by'}}]}
    two = SC.page(plan('ab'), images); three = SC.page(plan('abc', mark='drawn'), images); plain = SC.page(plan('abc'), images)
    assert 'class="sc collage"' not in two, 'two pictures do not make a collage: the scene stands down'
    grid = three.split('class="co"')[1]
    assert grid.count('<figure') == 3 and grid.index('width="1600"') < grid.index('width="1200"') < grid.index('width="1000"'), 'the widest picture is the ground the others lie on'
    assert 'mark-drawn' not in three.split('<body')[1][:120] and 'stroke-dashoffset' not in three, 'the stroke under the marked phrase is not offered, whatever a plan asks'
    assert '<em class="dv-draw">everyone<svg' in plain and 'em svg{display:none}' in plain, 'without the plan asking, the stroke is in the markup and not shown'


def test_a_heading_given_more_rows_than_it_holds_is_set_in_fewer():
    import scenes as SC
    five = SC.lines('Parque Butarque / s/n / 28918 / Leganés / Madrid', 'h2', 3)
    assert five.count('class="dv-ln"') == 3 and '--lr:3' in five and 'Leganés' in five and 'Madrid' in five
    assert SC.lines('First row / second row / third row', 'h2').count('class="dv-ln"') == 3


def test_an_address_is_sized_to_the_column_it_stands_in_and_its_longest_row():
    import scenes as SC
    row = SC.lines('Calle Cooperación 11 / 28922 Alcorcón / Madrid', 'h2', 3)
    assert '--lc:20' in row and '--lw:11' in row, 'the longest row is known beside the longest word'
    plan = {'brand': {'name': 'X', 'accent': '#2a8f5a'}, 'scenes': [{'scene': 'open-statement', 'slots': {'h1': 'A / line'}}, {'scene': 'visit', 'slots': {'where': 'Calle Cooperación 11 / 28922 Alcorcón / Madrid', 'rows': [{'k': 'Hours', 'v': '12–24'}]}}, {'scene': 'close', 'slots': {'line': 'Come', 'wordmark': True}}]}
    page = SC.page(plan, {})
    assert '.visit .h2{font-size:min(' in page and '100cqw / var(--lc' in page and 'container-type:inline-size' in page
    assert 'class="dv-endmark"' not in page, 'a one-letter name gets no wordmark'
    named = SC.page({**plan, 'brand': {'name': 'Bálamo', 'accent': '#2a8f5a'}}, {})
    assert 'class="dv-endmark"' in named and 'margin-bottom:0}' in named and 'class="dv-endmark low"' in SC.page({**plan, 'brand': {'name': 'Papagayo', 'accent': '#2a8f5a'}}, {})


def test_software_is_set_quietly_with_its_product_in_a_frame_and_its_plans_as_the_client_states_them():
    import scenes as SC, studio as ST
    px = 'data:image/png;base64,iVBORw0KGgo='
    images = {'wide': {'id': 'wide', 'data': px, 'w': 1440, 'h': 820, 'shot': True}, 'phone': {'id': 'phone', 'data': px, 'w': 390, 'h': 844}, 'cover': {'id': 'cover', 'data': px, 'w': 800, 'h': 1193}}
    def plan(pid, **more): return {'brand': {'name': 'X', 'accent': '#3b5bff'}, 'scale': 'product', **more, 'scenes': [
        {'scene': 'open-product', 'slots': {'h1': 'A quiet / *line*', 'lede': 'One sentence that says what the product does for the people who use it every day.', 'image': pid}},
        {'scene': 'plans', 'slots': {'h2': 'Plans', 'plans': [{'name': 'Free', 'price': '$0', 'points': ['One']}, {'name': 'Pro', 'price': '$20', 'per': '/ month', 'marked': True, 'points': ['Two']}]}},
        {'scene': 'compare', 'slots': {'h2': 'Compare', 'columns': ['Free', 'Pro'], 'groups': [{'title': 'Core', 'rows': [{'name': 'Seats', 'values': ['1', '10']}, {'name': 'Export', 'values': ['no', 'yes']}, {'name': 'Broken row', 'values': ['yes']}]}]}},
        {'scene': 'close', 'slots': {'line': 'Start'}}]}
    wide, phone = SC.page(plan('wide'), images), SC.page(plan('phone'), images)
    assert 'scale-product' in wide.split('<body')[1][:90] and 'class="dv-window dv-lift"' in wide and 'class="dv-phone"' not in wide.split('<body')[1]
    assert 'class="dv-phone"' in phone and 'open-prod centre' in phone, 'a phone screen stands in a phone, centred'
    assert wide.count('class="pl') >= 2 and wide.count('is-marked') >= 1 and '$20' in wide and '<th scope="row">Seats</th><td>1</td><td>10</td>' in wide
    assert 'aria-label="no">—' in wide and 'aria-label="yes">✓' in wide and 'Broken row' not in wide, 'a row without a value for every column is not drawn'
    bad = ST.check(plan('cover'), SC.page(plan('cover'), images), {'links': []}, set(), images)
    assert any('photograph or a cover' in x for x in bad['pictures']) and any('one value for each column' in x for x in bad['structure'])
    assert 'class="sc plans"' not in SC.page({**plan('wide'), 'scenes': [{'scene': 'plans', 'slots': {'plans': [{'name': 'Only', 'price': '$1'}]}}]}, images), 'one plan is not a choice: the scene stands down'


def test_the_plans_character_is_on_the_page_and_the_product_can_stand_in_the_clients_own_world():
    import scenes as SC, studio as ST
    px = 'data:image/png;base64,iVBORw0KGgo='
    images = {'shot': {'id': 'shot', 'data': px, 'w': 1440, 'h': 820, 'shot': True}, 'stadium': {'id': 'stadium', 'data': px, 'w': 1400, 'h': 594}, 'small': {'id': 'small', 'data': px, 'w': 600, 'h': 400}}
    def plan(ground, character): return {'brand': {'name': 'X', 'accent': '#2af6a0'}, 'scale': 'product', 'character': character, 'scheme': 'night', 'scenes': [{'scene': 'open-product', 'slots': {'h1': 'Match / *analysis*', 'lede': 'A sentence about what the product does for the people who use it, long enough to count as words.', 'image': 'shot', 'ground': ground}}, {'scene': 'close', 'slots': {'line': 'Start'}}]}
    loud, calm = SC.page(plan('stadium', 'energetic'), images), SC.page(plan(None, 'calm'), images)
    assert 'scale-product ch-energetic' in loud.split('<body')[1][:120] and 'class="op-ground"' in loud and 'has-ground' in loud.split('<body')[1]
    assert 'ch-calm' in calm.split('<body')[1][:120] and 'class="op-ground"' not in calm
    assert '.dv .ch-calm .ft[data-rise]:not(.is-in)' in calm and 'translateY(22px)' in calm and 'translateY(40px) scale(.985)' in calm, 'cards arrive on every page; how far and how long follows the character'
    assert any('ground behind the product' in x for x in ST.check(plan('small', 'energetic'), SC.page(plan('small', 'energetic'), images), {'links': []}, set(), images)['pictures'])


def test_features_hold_the_real_interface_and_a_plan_is_sent_back_for_what_its_first_screen_owes():
    import scenes as SC, studio as ST
    px = 'data:image/png;base64,iVBORw0KGgo='
    images = {**{f's{k}': {'id': f's{k}', 'data': px, 'w': 1440, 'h': 800, 'shot': True} for k in range(1, 5)}, 'phone': {'id': 'phone', 'data': px, 'w': 390, 'h': 844, 'shot': True}, 'stadium': {'id': 'stadium', 'data': px, 'w': 1400, 'h': 594}}
    ev = {'links': [], 'kind': 'software', 'h1': 'AI sports match analysis', 'seo_safe': True}
    feats = {'scene': 'features', 'slots': {'h2': 'What / it does', 'items': [{'title': 'Prices', 'say': 'A sentence about prices that is long enough to be a sentence.', 'image': 's2'}, {'title': 'Record', 'say': 'A sentence about the record kept in public.', 'image': 's3'}, {'title': 'On the phone', 'say': 'The same on the phone.', 'image': 'phone'}]}}
    def plan(opening): return {'brand': {'name': 'X', 'accent': '#2af6a0'}, 'scale': 'product', 'character': 'energetic', 'scheme': 'night', 'scenes': [opening, feats, {'scene': 'close', 'slots': {'line': 'Start'}}]}
    good = plan({'scene': 'open-product', 'slots': {'h1': 'Sports match / *analysis* first', 'lede': 'A sentence about what the product does for the people who use it, long enough to count.', 'image': 's1', 'ground': 'stadium'}})
    page = SC.page(good, images); bad = ST.check(good, page, ev, set(), images)
    assert page.count('class="ft ft-') == 3 and 'class="ft-pic ft-phone"' in page and '--w:1440px' in page and not bad['structure'] and not bad['pictures'], bad
    words = plan({'scene': 'open-statement', 'slots': {'h1': 'Never place / a bad bet', 'lede': 'A sentence about what the product does for the people who use it, long enough to count.'}})
    found = ST.check(words, SC.page(words, images), ev, set(), images)['structure']
    assert any('opens on "open-product"' in x for x in found) and any('found by' in x for x in found), found
    bare = plan({'scene': 'open-product', 'slots': {'h1': 'Sports match / analysis', 'lede': 'A sentence about what the product does for the people who use it, long enough to count.', 'image': 's1'}})
    assert any('stadium' in x and 'ground' in x for x in ST.check(bare, SC.page(bare, images), ev, set(), images)['pictures'])
    place = {'brand': {'name': 'X', 'accent': '#2a8f5a'}, 'scenes': [{'scene': 'open-statement', 'slots': {'h1': 'A place / for all', 'lede': 'A sentence about the place and the people who come to it, long enough to count as words.'}}, {'scene': 'close', 'slots': {'line': 'Come'}}]}
    assert any('shows no picture' in x for x in ST.check(place, SC.page(place, images), {'links': []}, set(), {'stadium': images['stadium']})['structure']), 'a client with a wide photograph does not open on words alone'
    assert not any('shows no picture' in x for x in ST.check(place, SC.page(place, {}), {'links': []}, set(), {})['structure']), 'a client with no picture may'


def test_a_scene_can_slide_over_the_one_before_it_once_or_twice_and_never_first():
    import scenes as SC, studio as ST
    def plan(*covers): return {'brand': {'name': 'X', 'accent': '#3b5bff'}, 'scenes': [{'scene': 'open-statement', 'cover': 0 in covers, 'slots': {'h1': 'A line / of words', 'lede': 'A sentence long enough to be counted among the words of a page that says something to its reader.'}},
        {'scene': 'statement', 'cover': 1 in covers, 'slots': {'text': 'A thesis of some length that the page is built around, said once and early so that the rest can lean on it without repeating it.'}},
        {'scene': 'ledger', 'cover': 2 in covers, 'slots': {'h2': 'Facts', 'rows': [{'k': 'One', 'v': 'First'}, {'k': 'Two', 'v': 'Second'}]}}, {'scene': 'close', 'slots': {'line': 'End'}}]}
    page = SC.page(plan(1), {})
    assert page.count('<section class="dv-cover ') == 1 and 'dv-covered' in page, 'the scene is marked and the device that holds the one before it is on the page'
    assert '<section class="dv-cover ' not in SC.page(plan(), {}) and not any('"cover"' in x for x in ST.check(plan(1), page, {'links': []}, set(), {})['structure'])
    assert '<section class="dv-cover ' not in SC.page(plan(0), {}).split('id="top"')[0][-60:], 'the first scene has nothing to slide over'
    for wrong in (plan(0), plan(1, 2)): assert any('"cover"' in x for x in ST.check(wrong, SC.page(wrong, {}), {'links': []}, set(), {})['structure'])


PX = 'data:image/png;base64,iVBORw0KGgo='
PARTS = {**{f's{k}': {'id': f's{k}', 'data': PX, 'w': 1440, 'h': 800, 'shot': True} for k in range(1, 6)}, 'photo': {'id': 'photo', 'data': PX, 'w': 1400, 'h': 800},
         **{f'logo{k}': {'id': f'logo{k}', 'data': PX, 'w': 120, 'h': 30, 'logo': True, 'alt': f'L{k}'} for k in range(1, 6)}}
LEDE = 'A sentence about what the product does for the people who use it, long enough to count among the words of a page.'


def soft_plan(*scenes, opening=None, close=None, **more):
    return {'brand': {'name': 'Example', 'accent': '#3b5bff'}, 'scale': 'product', 'character': 'calm', **more,
            'scenes': [opening or {'scene': 'open-product', 'slots': {'h1': 'A quiet / *line*', 'lede': LEDE, 'image': 's1'}}, *scenes, close or {'scene': 'close', 'slots': {'line': 'Start / now'}}]}


def test_the_close_has_forms_a_mark_beside_its_columns_and_a_name_tone_on_tone():
    import scenes as SC, studio as ST
    cols = [{'title': 'Product', 'links': [{'label': 'Pricing', 'url': 'https://x.test/p'}]}]
    def close(**s): return SC.page(soft_plan(close={'scene': 'close', 'slots': {'line': 'Start / now', 'columns': cols, **s}}), PARTS).split('<footer')[1]
    centre, card, split, left = close(form='centre', tone='paper', wordmark='faint'), close(form='card', ground='photo'), close(form='split'), close()
    assert 'close-centre"' in centre.split('>')[0] and ' night' not in centre.split('>')[0] and ' faint" style=' in centre and '<p class="foot-mark">Example</p>' in centre
    assert 'close-card night' in card and 'class="cta-ground"' in card and 'close-split' in split and 'close-left night' in left and 'dv-endmark' not in left.split('</footer>')[0]
    assert 'close-centre' in close(form='card', ground='s1') and 'close-centre' in close(form='card'), 'a card needs a photograph to lie on: without one the call is centred'
    bad = soft_plan(close={'scene': 'close', 'slots': {'line': 'Start', 'form': 'card', 'ground': 's1'}})
    assert any('"close" as a card' in x for x in ST.check(bad, SC.page(bad, PARTS), {'links': [], 'kind': 'software'}, set(), PARTS)['pictures'])


def test_plans_carry_the_clients_tag_and_both_prices_behind_a_switch():
    import scenes as SC, studio as ST
    def plans(**s): return {'scene': 'plans', 'slots': {'h2': 'Plans', 'plans': [{'name': 'Free', 'price': '$0'}, {'name': 'Pro', 'price': '$20', 'per': '/ month', 'price_b': '$16', 'per_b': '/ month, yearly', 'tag': 'Most popular', 'marked': True}, {'name': 'Team', 'price': '$90', **s.pop('team', {})}], **s}}
    both = SC.page(soft_plan(plans(switch=['Monthly', 'Yearly'])), PARTS)
    assert 'class="dv-switch"' in both and '<span class="sw-a">$20<small>/ month</small></span><span class="sw-b">$16<small>/ month, yearly</small></span>' in both and '<span class="pl-tag">Most popular</span>' in both and 'data-switch' in both
    assert 'class="dv-switch"' not in SC.page(soft_plan(plans()), PARTS).split('<body')[1], 'no switch unless the plan asks for one'
    half = soft_plan(plans(switch=['Monthly', 'Yearly']))
    assert any('second price on every paid plan' in x for x in ST.check(half, SC.page(half, PARTS), {'links': [], 'kind': 'software'}, set(), PARTS)['structure']), 'Team has one price: the switch is refused'


def test_the_parts_of_a_software_page_each_draw_and_stand_down_without_their_material():
    import scenes as SC, studio as ST
    U = 'https://x.test/'
    page = SC.page(soft_plan(
        {'scene': 'logos', 'slots': {'label': 'Trusted by teams'}},
        {'scene': 'tabs', 'slots': {'tabs': [{'word': 'Read', 'title': 'One', 'say': 'First.', 'image': 's2'}, {'word': 'Decide', 'title': 'Two', 'say': 'Second.', 'image': 's3'}]}},
        {'scene': 'lines', 'slots': {'h2': 'Parts', 'rows': [{'title': 'Prices', 'say': 'A.', 'image': 's4', 'links': [{'label': 'More', 'url': U + 'a'}]}, {'title': 'Record', 'say': 'B.', 'image': 's5'}]}},
        {'scene': 'chips', 'slots': {'items': [f'Name {k}' for k in range(10)]}},
        {'scene': 'quote', 'slots': {'text': 'Said exactly so.', 'name': 'A. Person', 'role': 'Head'}},
        {'scene': 'cases', 'slots': {'h2': 'Customers', 'items': [{'title': 'What happened.', 'who': 'Acme', 'image': 'photo', 'url': U + 's1'}, {'figure': '3', 'title': 'Another.', 'who': 'Globex'}]}},
        {'scene': 'code', 'slots': {'h2': 'Build', 'code': 'curl https://api.x.test/v1/matches', 'ground': 'photo'}},
        {'scene': 'reads', 'slots': {'h2': 'Reading', 'items': [{'kind': 'Guide', 'title': 'One', 'url': U + 'r1'}, {'kind': 'Note', 'title': 'Two', 'url': U + 'r2'}]}},
        {'scene': 'ways', 'slots': {'h2': 'Next', 'items': [{'title': 'Pricing', 'url': U + 'p'}, {'title': 'Docs', 'url': U + 'd'}]}},
        opening={'scene': 'open-product', 'slots': {'h1': 'A quiet / *line*', 'lede': LEDE, 'image': 's1', 'align': 'beside', 'news': {'label': 'New', 'text': 'One thing', 'url': U + 'n'}}},
        guides=True, nav=[{'label': 'Product', 'links': [{'label': 'Docs', 'url': U + 'd'}]}, {'label': 'Pricing', 'url': U + 'p'}]), PARTS)
    body = page.split('<body')[1]
    for mark in ('open-prod beside', 'class="news"', 'class="lg-row"', 'class="dv-tabs"', 'role="tab"', 'class="ln-list"', 'dv-tick ch-row back', 'class="q1"', 'class="cs has-pic"', 'class="cs-fig">3<', 'class="dv-window cd-win"', 'class="cd-ground"', 'class="rd-grid"', 'class="ways-grid"', 'class="bar-dd"', ' guides'):
        assert mark in body, mark
    assert body.count('<li><img') == 5 and page.count('aria-haspopup') == 1 and body.split('id="menu"')[1].split('</nav>')[0].count('<a ') == 3, 'the phone menu lists a panel\'s links flat'
    bare = SC.page(soft_plan({'scene': 'logos', 'slots': {}}, {'scene': 'tabs', 'slots': {'tabs': [{'word': 'One', 'image': 's2'}]}}, {'scene': 'chips', 'slots': {'items': ['a', 'b']}}, {'scene': 'quote', 'slots': {'text': 'No name'}}, {'scene': 'ways', 'slots': {'items': [{'title': 'One', 'url': U}]}}, {'scene': 'code', 'slots': {'code': 'x'}}), {k: v for k, v in PARTS.items() if not v.get('logo')}).split('<body')[1]
    for gone in ('lg-row', 'dv-tabs"', 'ch-row', 'class="q1"', 'ways-grid', 'cd-win'): assert gone not in bare, gone + ': a part without its material is not drawn'
    cluster = SC.page(soft_plan(opening={'scene': 'open-product', 'slots': {'h1': 'A / line', 'lede': LEDE, 'image': 's1', 'more': ['s2', 's3']}}), PARTS)
    assert 'open-prod cluster' in cluster and cluster.count('class="cl cl-') == 3
    made = soft_plan({'scene': 'logos', 'slots': {}}, {'scene': 'code', 'slots': {'h2': 'Build', 'code': 'curl https://api.invented.test/never-published'}})
    found = ST.check(made, SC.page(made, PARTS), {'links': [], 'kind': 'software', 'sections': [{'text': 'curl https://api.x.test/v1/matches'}]}, set(), PARTS)['structure']
    assert any('"logos" needs' in x for x in found) and any('"code": the code must be the client' in x for x in found), found


def test_what_a_clients_material_obliges_is_said_before_the_first_try_and_a_ground_may_be_soft():
    import scenes as SC, studio as ST
    images = {'s1': {'id': 's1', 'data': PX, 'w': 1440, 'h': 800, 'shot': True}, 'night': {'id': 'night', 'data': PX, 'w': 1400, 'h': 594, 'soft': True}, 'logo1': {'id': 'logo1', 'data': PX, 'w': 120, 'h': 30, 'logo': True}}
    ev = {'links': [], 'kind': 'software', 'h1': 'AI sports match analysis', 'seo_safe': True}
    shots, photos, grounds, words = ST.owed(ev, images)
    assert shots == ['s1'] and photos == [] and grounds == ['night'] and words == ['sports', 'match', 'analysis'], 'a soft photograph cannot open a page, and can lie behind the product'
    told = ST.briefing(ev, images)
    assert 'open-product' in told and "['night']" in told and 'at least 2 of' in told and 'sent back' in told
    assert ST.briefing({'links': [], 'kind': 'place'}, {}) == '', 'nothing owed, nothing said'
    plan = soft_plan(opening={'scene': 'open-product', 'slots': {'h1': 'Sports match / *analysis*', 'lede': LEDE, 'image': 's1', 'ground': 'night'}})
    bad = ST.check(plan, SC.page(plan, images), ev, set(), images)
    assert not bad['pictures'] and not any('open' in x or 'headline' in x for x in bad['structure']), bad
    assert 'mark' not in ST.TOOL['input_schema']['properties']
