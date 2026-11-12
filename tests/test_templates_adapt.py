"""The adapter turns what capture and the reader already produce into the data every template takes — and invents
nothing: every word it writes stands in the capture. Two made-up captures (a product, a restaurant) pin the rules and
run everywhere; the eight frozen real captures in bench/seed/ (not in git: third-party text and pictures) are checked
on a machine that has them."""
import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / 'tests' / 'fixtures' / 'templates'


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


A = _load('swarmsite_templates_adapt', ROOT / 'lib' / 'templates' / 'adapt.py')
R = _load('swarmsite_templates_registry', ROOT / 'lib' / 'templates' / 'registry.py')
PX = 'data:image/jpeg;base64,/9j/4AAQSkZJRg=='
SVG = 'data:image/svg+xml;base64,PHN2Zy8+'


def seed_dir():
    """bench/seed of this checkout, of $SWARMSITE_SEED, or of the main checkout when this is a worktree"""
    cands = [os.environ.get('SWARMSITE_SEED'), ROOT / 'bench' / 'seed']
    try:
        common = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True, text=True, timeout=10).stdout.strip()
        if common:
            cands.append(Path(common).parent / 'bench' / 'seed')
    except (OSError, subprocess.SubprocessError):
        pass
    return next((Path(c) for c in cands if c and Path(c).is_dir() and any(Path(c).glob('*/inventory.json'))), None)


def hand_dir():
    """the hand-made data files of the real test clients: third parties' own words, kept out of git like bench/seed.
    $SWARMSITE_TEMPLATES_SRC, this checkout's research folder, or the main checkout's when this is a worktree."""
    rel = Path('bench') / 'runs' / '_research' / 'templates'
    cands = [os.environ.get('SWARMSITE_TEMPLATES_SRC'), ROOT / rel]
    try:
        common = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True, text=True, timeout=10).stdout.strip()
        if common:
            cands.append(Path(common).parent / rel)
    except (OSError, subprocess.SubprocessError):
        pass
    return next((Path(c) / 'data' for c in cands if c and (Path(c) / 'data').is_dir()), None)


HAND = hand_dir()
SEEDS = seed_dir()
SEED_IDS = sorted(p.parent.name for p in SEEDS.glob('*/inventory.json')) if SEEDS else []
needs_seeds = pytest.mark.skipif(not SEEDS, reason='bench/seed is not on this machine (python3 bench/fetch.py brings it)')
_adapted = {}


def adapted(sid):
    if sid not in _adapted:
        seed = A.load_seed(SEEDS / sid)
        _adapted[sid] = (seed, A.adapt(seed))
    return _adapted[sid]


# ───────────────────────── two made-up captures
def product():
    sec = lambda i, level, title, text, actions=(), faq=(), kind='section': {
        'id': 'home-%d' % i, 'title': title, 'headingLevel': level, 'kind': kind, 'text': text, 'faq': list(faq), 'testimonials': [],
        'sourceActions': [{'label': l, 'url': u} for l, u in actions]}
    home = 'https://www.tallyfern.example/'
    acts = [('Skip to content', home + '#main'), ('TALLYFERN', home), ('LEDGER', home + 'ledger'), ('PRICING', home + 'pricing'), ('GUIDE', home + '#guide'),
            ('LOG IN', home + 'login'), ('START A LEDGER', home + 'signup'), ('START A LEDGER →', home + 'signup'), ('SEE A SAMPLE MONTH →', home + 'sample'),
            ('Terms', home + 'terms'), ('Privacy', home + 'privacy')]
    text = ('Skip to content TALLYFERN LEDGER PRICING GUIDE LOG IN START A LEDGER FOR MARKET STALLS The books of a stall, kept in an evening. '
            'Tallyfern reads your receipts and keeps the ledger. You check it once a week. Start a ledger → See a sample month → ✓ No card to begin ✓ Export to CSV ✓ One stall or ten '
            '4,210 stalls keep their books here A ledger is a habit, not a chore. Most stalls lose a morning a month to paper. Tallyfern asks for ten minutes on a Sunday. '
            'How it works Photograph Snap each receipt as you get it. Sort Tallyfern files it under stock, rent or pay. Close Read the month on one page and send it to your accountant. '
            'Plans Two plans, both without a contract. Stall €9 / month Row €29 / month Questions Does it read handwriting? Yes, and it marks what it could not read. '
            'Keep the books tonight. Ten minutes, then the market. Start a ledger → © 2026 Tallyfern Terms Privacy')
    inv = {'url': home, 'title': 'Tallyfern — the books of a stall', 'lang': 'en-GB',
           'copy': {'h1': 'THE BOOKS OF A STALL, KEPT IN AN EVENING.', 'text': text,
                    'headings': [{'tag': 'H1', 'text': 'THE BOOKS OF A STALL, KEPT IN AN EVENING.'}, {'tag': 'H2', 'text': 'A LEDGER IS A HABIT, NOT A CHORE.'},
                                 {'tag': 'H2', 'text': 'HOW IT WORKS'}, {'tag': 'H3', 'text': 'Photograph'}, {'tag': 'H3', 'text': 'Sort'}, {'tag': 'H3', 'text': 'Close'},
                                 {'tag': 'H2', 'text': 'PLANS'}, {'tag': 'H3', 'text': 'Stall'}, {'tag': 'H3', 'text': 'Row'}, {'tag': 'H2', 'text': 'QUESTIONS'},
                                 {'tag': 'H2', 'text': 'KEEP THE BOOKS TONIGHT.'}]},
           'actions': [{'text': t, 'href': h} for t, h in acts],
           'brand': {'nav': ['TALLYFERN', 'LEDGER', 'PRICING', 'GUIDE', 'LOG IN', 'START A LEDGER', 'Terms', 'Privacy']},
           'seo': {'description': 'Tallyfern reads your receipts and keeps the ledger.'},
           'colors': {'bg': [{'c': '#fbf7ee', 'n': 900}, {'c': '#1d2a22', 'n': 60}, {'c': '#000000 a0', 'n': 40}],
                      'text': [{'c': '#5b6a60', 'n': 80}, {'c': '#1d2a22', 'n': 70}, {'c': '#fbf7ee', 'n': 9}],
                      'buttons': [{'c': '#d2552b', 'n': 4}, {'c': '#fbf7ee', 'n': 2}]},
           'sourceCoverage': {'sections': [
               sec(1, 'H1', 'THE BOOKS OF A STALL, KEPT IN AN EVENING.', 'For market stalls The books of a stall, kept in an evening. Tallyfern reads your receipts and keeps the ledger. '
                   'You check it once a week. Start a ledger → See a sample month → ✓ No card to begin ✓ Export to CSV ✓ One stall or ten 4,210 stalls keep their books here',
                   [('START A LEDGER →', home + 'signup'), ('SEE A SAMPLE MONTH →', home + 'sample')]),
               sec(2, 'H2', 'A LEDGER IS A HABIT, NOT A CHORE.', 'A ledger is a habit, not a chore. Most stalls lose a morning a month to paper. Tallyfern asks for ten minutes on a Sunday. THIS WEEK 12 RECEIPTS'),
               sec(3, 'H2', 'HOW IT WORKS', 'How it works Three small things, in order. 01 Photograph Snap each receipt as you get it. 02 Sort Tallyfern files it under stock, rent or pay. '
                   '03 Close Read the month on one page and send it to your accountant.'),
               sec(4, 'H2', 'PLANS', 'Plans Two plans, both without a contract. Stall €9 / month Row €29 / month', [('CHOOSE STALL', home + 'signup?p=stall'), ('CHOOSE ROW', home + 'signup?p=row')]),
               sec(5, 'H2', 'QUESTIONS', 'Questions Does it read handwriting? Yes, and it marks what it could not read.', [],
                   [{'question': 'DOES IT READ HANDWRITING?', 'answer': 'Yes, and it marks what it could not read.'},
                    {'question': 'Half a question', 'answer': 'An answer the capture cut sho', 'answerTruncated': True}], 'disclosure'),
               sec(6, 'H2', 'KEEP THE BOOKS TONIGHT.', 'Keep the books tonight. Ten minutes, then the market. Start a ledger →', [('START A LEDGER →', home + 'signup')])]}}
    return {'inventory': inv,
            'geometry': {'nav': {'rect': {'x': 0, 'y': 0, 'w': 1440, 'h': 72}, 'links': 6},
                         'ctas': [{'text': 'Start a ledger', 'rect': {'y': 20}}, {'text': 'Start a ledger→', 'rect': {'y': 520}}, {'text': 'See a sample month→', 'rect': {'y': 520}}]},
            'assets': {'logo': {'src': home + 'img/tallyfern-logo.svg', 'alt': 'Tallyfern', 'data': SVG, 'nw': 180, 'nh': 40}, 'palette': {'brandAccent': '#d2552b', 'fromLogo': [{'c': '#1f8a57', 'n': 30}]}},
            'factsheet': {'what': 'Tallyfern is a bookkeeping tool for market stalls that reads receipts and keeps a ledger.', 'language': 'en',
                          'best_sentence': 'The books of a stall, kept in an evening.',
                          'facts': ['4,210 stalls keep their books here', '97% of receipts read without a correction', 'Founded by two stallholders in Leeds'],
                          'offers': [{'name': 'Stall', 'price': '€9/month (billed monthly)', 'note': 'For one stall'}, {'name': 'Row', 'price': '€29/month'},
                                     {'name': 'Market', 'price': '€99/month', 'note': 'The reader made this one up'}, {'name': 'Trial', 'price': 'Free'}],
                          'capabilities': ['Reads receipts with a phone camera'], 'contact': ['hello@tallyfern.example'], 'missing': ['Customer reviews']},
            'images': [{'id': 'img1', 'src': home + 'img/stall.jpg', 'w': 1600, 'h': 1000, 'alt': 'A fruit stall at dawn', 'data': PX},
                       {'id': 'img2', 'src': home + 'img/stall-800x500.jpg', 'w': 800, 'h': 500, 'alt': 'A fruit stall at dawn', 'data': PX},
                       {'id': 'shot1', 'src': 'visual-shot', 'w': 1200, 'h': 700, 'alt': 'The ledger\n\nNovember', 'shot': True, 'data': PX},
                       {'id': 'gen-a', 'src': 'commissioned', 'w': 1600, 'h': 1067, 'alt': 'A made picture', 'gen': True, 'data': PX},
                       {'id': 'crop-a', 'src': home + 'img/stall.jpg', 'w': 600, 'h': 400, 'alt': '', 'crop_of': 'img1', 'data': PX},
                       {'id': 'tiny', 'src': home + 'img/dot.png', 'w': 40, 'h': 40, 'alt': '', 'data': PX}]}


def restaurant():
    home = 'https://casaolmo.example/'
    acts = [('Teléfono 912 345 678 desde las 13:00h', 'tel:912345678'), ('RESERVAR', home + 'reservas/'), ('LA CARTA', home + 'carta/'), ('CONTACTO', home + 'contacto/'),
            ('AVISO LEGAL', home + 'aviso-legal/'), ('Aviso legal', home + '#'), ('6 platos', home + 'carta/arroces/'), ('4 platos', home + 'carta/de-la-huerta/'),
            ('Arroz del señoret', home + 'carta/arroces/arroz-del-senoret/'), ('Arroz negro', home + 'carta/arroces/arroz-negro/'),
            ('Instagram', 'https://www.instagram.com/casaolmo/'), ('Compartir', 'https://www.facebook.com/sharer.php?u=x'), ('PARA LLEVAR', home + 'para-llevar/')]
    text = ('Teléfono 912 345 678 desde las 13:00h RESERVAR LA CARTA CONTACTO Casa Olmo cocina de arroces DESDE 1987 Arroces a la leña en el barrio de Ruzafa RESERVAR LA CARTA '
            'ARROCES 6 platos DE LA HUERTA 4 platos Arroz del señoret 18,50 € Arroz negro 17,00 € Calle del Olmo 4 46006 Valencia hola@casaolmo.example '
            'Horario De martes a sábado 13:30h a 16:00h Domingos 13:30h a 17:00h')
    inv = {'url': home, 'title': 'Casa Olmo - Arroces en Ruzafa', 'lang': 'es', 'copy': {'h1': None, 'text': text, 'headings': [{'tag': 'H3', 'text': 'ARROCES'}, {'tag': 'H3', 'text': 'DE LA HUERTA'}]},
           'actions': [{'text': t, 'href': h} for t, h in acts], 'brand': {'nav': ['RESERVAR', 'LA CARTA', 'CONTACTO', 'AVISO LEGAL', 'RESERVAR']},
           'seo': {'description': 'Arroces a la leña en el barrio de Ruzafa.'},
           'colors': {'bg': [{'c': '#ffffff', 'n': 500}], 'text': [{'c': '#2b2b2b', 'n': 40}, {'c': '#9a9a9a', 'n': 30}], 'buttons': [{'c': '#b3541e', 'n': 2}, {'c': '#3b5998', 'n': 1}]},
           'sourceCoverage': {'sections': []}, 'sourcePages': []}
    return {'inventory': inv, 'geometry': {'nav': {'rect': {'y': 0, 'h': 90}, 'links': 4}, 'ctas': [{'text': 'Reservar', 'rect': {'y': 30}}]},
            'assets': {'logo': {'src': home + 'theme/lazy.svg', 'alt': 'Arroces', 'data': SVG, 'nw': 0, 'nh': 0}, 'palette': {'brandAccent': '#3b5998'}},
            'factsheet': {'what': 'Casa Olmo is a rice restaurant in Ruzafa, Valencia, open since 1987.', 'language': 'Spanish (es)',
                          'best_sentence': 'Casa Olmo cocina de arroces — Arroces a la leña en el barrio de Ruzafa',
                          'facts': ['Address: Calle del Olmo 4, 46006 Valencia', 'Hours: De martes a sábado 13:30h a 16:00h; Domingos 13:30h a 17:00h; Lunes 20:00h a 23:00h',
                                    'Structured data (not visible text): priceRange "20 - 40"; servesCuisine: Arroces, Mediterránea'],
                          'offers': [{'name': 'Arroz del señoret (arroz)', 'price': '18,50 € por persona'}, {'name': 'Arroz negro (arroz)', 'price': '17,00 €'}, {'name': 'Paella de bogavante', 'price': '32,00 €'}],
                          'contact': ['Phone: 912 345 678', 'Email: hola@casaolmo.example', 'Reservations: https://casaolmo.example/reservas/']},
            'images': [{'id': 'img1', 'src': home + 'up/sala.jpg', 'w': 1400, 'h': 900, 'alt': 'La sala', 'data': PX}, {'id': 'img2', 'src': home + 'up/arroz.jpg', 'w': 600, 'h': 400, 'alt': 'Arroz', 'data': PX}]}


# ───────────────────────── nothing is invented
OWN = {'h', 'home', 'src', 'logo', 'img', 'poster', 'ground', 'ink', 'accent', 'extra', 'lang', 'kind', 'niche', 'count', 'w', 'h', 'small', 'logo_wordmark'}   # niche: a classifier, never shown


def invented(d, seed):
    """every string of the data that does not stand in the capture (addresses of links, picture paths, colours and
    the like aside). Checked sentence by sentence: a paragraph may have had a button's label lifted out of it."""
    said = A.Corpus(A.capture_texts(seed))
    reader = A.Corpus([x for x in (seed.get('factsheet') or {}).get('facts') or [] if isinstance(x, str)])
    out = []

    def walk(v, path):
        key = path[-1] if path else ''
        if isinstance(v, dict):
            if path == ['figures'] or path == ['plans', 'items'] and v.get('per'):          # a number with its words, an amount with its term: read together
                a, b = (v['v'], v.get('l', '')) if path == ['figures'] else (v['price'], v['per'])
                if not said.says(a + b):
                    out.append(('.'.join(path), a + ' ' + b))
                v = {k: x for k, x in v.items() if k not in ('v', 'l', 'per')}
            for k, x in v.items():
                if not (k.startswith('_') or k in OWN):
                    walk(x, path + [k])
        elif isinstance(v, list):
            for x in v:
                walk(x, path)
        elif isinstance(v, str) and v.strip():
            where = '.'.join(path)
            if where == 'place.social.t' or where == 'place.phone.t' and said.says(re.sub(r'\D', '', v)):
                return
            if where in ('place.cuisine', 'place.price_range'):                     # the page's structured data, as the reader quotes it
                return None if reader.says(v) else out.append((where, v))
            if where == 'place.menu.sections.t' and any(A.slug(v) in A.slug(a.get('href') or '') for a in (seed.get('inventory') or {}).get('actions') or []):
                return
            for part in A.sentences(v) or [v]:
                if not said.says(part.rstrip('.')) and not said.says(part):
                    out.append((where, part))
    walk(d, [])
    return out


def test_the_schema_holds_the_hand_made_files_and_refuses_a_wrong_shape():
    files = sorted(FIX.glob('*.json'))
    assert len(files) == 3
    for f in files + (sorted(HAND.glob('*.json')) if HAND else []):               # the made-up clients, and the real ones where they are on the machine
        assert A.validate(json.loads(f.read_text(encoding='utf-8'))) == [], f.name
    assert A.validate({'brand': {'name': 'A'}, 'hero': {'title': 'T'}}) == []
    bad = A.validate({'brand': {'name': ''}, 'hero': {}, 'lang': 'English', 'palette': {'ground': 'white', 'ink': '#111'}, 'nav': [{'h': '/x'}], 'figures': [{'l': 'no value'}],
                      'media': {'photos': [{'w': 10}], 'video': {'poster': 'p.jpg'}}, 'faq': {'items': [{'q': 'Q'}]}, 'place': {'hours': [{'days': 'Mon'}], 'since': 'long ago', 'email': 'nope',
                                                                                                                         'menu': {'sections': [{'count': '5'}]}}})
    for where in ('$.brand.name', '$.hero', '$.lang', '$.palette.ground', '$.nav[0]', '$.figures[0]', '$.media.photos[0]', '$.media.video', '$.faq.items[0]',
                  '$.place.hours[0]', '$.place.since', '$.place.email', '$.place.menu.sections[0]'):
        assert any(b.startswith(where) for b in bad), where


def test_a_product_page_becomes_the_templates_data_in_the_clients_own_words():
    seed = product()
    d = A.adapt(copy.deepcopy(seed))
    assert A.validate(d) == [] and invented(d, seed) == []
    assert d['brand'] == {'name': 'Tallyfern', 'logo': 'media/logo.svg', 'home': 'https://www.tallyfern.example/', 'logo_wordmark': True}
    assert d['lang'] == 'en' and d['kind'] == 'software' and 'place' not in d
    # colours: the page's ground, its strongest common text colour, the colour of its buttons — never a see-through fill
    assert d['palette']['ground'] == '#fbf7ee' and d['palette']['ink'] == '#1d2a22' and d['palette']['accent'] == '#d2552b' and '#1f8a57' in d['palette']['extra']
    # the bar: capitals by style are set as the page's running text spells the words; the button is the call; a link into the old page is dropped and said so
    assert d['nav'] == [{'t': 'Ledger', 'h': 'https://www.tallyfern.example/ledger'}, {'t': 'Pricing', 'h': 'https://www.tallyfern.example/pricing'}]
    assert d['signin'] == {'t': 'Log in', 'h': 'https://www.tallyfern.example/login'} and d['cta'] == {'t': 'Start a ledger', 'h': 'https://www.tallyfern.example/signup'}
    assert any(g.startswith('nav: 1 link') and 'Guide' in g for g in d['_adapter']['gaps'])
    h = d['hero']
    assert h['title'] == 'The books of a stall, kept in an evening.' and h['kicker'] == 'For market stalls'
    assert h['text'] == 'Tallyfern reads your receipts and keeps the ledger.' and h['text2'] == 'You check it once a week.'
    assert h['primary'] == {'t': 'Start a ledger', 'h': 'https://www.tallyfern.example/signup'} and h['secondary']['t'] == 'See a sample month'
    assert d['trust'] == ['No card to begin', 'Export to CSV']                       # the third tick runs into the next element: left out, not guessed
    # a figure only when the reader lists it and the page prints it
    assert d['figures'] == [{'v': '4,210', 'l': 'stalls keep their books here'}]
    assert d['statement'] == {'title': 'A ledger is a habit, not a chore.', 'text': 'Most stalls lose a morning a month to paper. Tallyfern asks for ten minutes on a Sunday.'}
    assert d['steps']['title'] == 'How it works' and d['steps']['text'] == 'Three small things, in order.'
    assert [(i.get('k'), i['title'], i['text']) for i in d['steps']['items']] == [('01', 'Photograph', 'Snap each receipt as you get it.'), ('02', 'Sort', 'Tallyfern files it under stock, rent or pay.'),
                                                                                    ('03', 'Close', 'Read the month on one page and send it to your accountant.')]
    # plans: only what the page prints. 'Market €99' is the reader's alone; 'Trial: Free' is a claim, not a price
    assert d['plans']['title'] == 'Plans' and d['plans']['text'] == 'Two plans, both without a contract.'
    assert [(p['name'], p['price'], p.get('per'), p['cta']['t']) for p in d['plans']['items']] == [('Stall', '€9', '/month', 'Choose stall'), ('Row', '€29', '/month', 'Choose Row')]
    assert d['faq'] == {'title': 'Questions', 'items': [{'q': 'Does it read handwriting?', 'a': 'Yes, and it marks what it could not read.'}]}
    assert d['close'] == {'title': 'Keep the books tonight.', 'text': 'Ten minutes, then the market.', 'cta': {'t': 'Start a ledger', 'h': 'https://www.tallyfern.example/signup'}}
    assert d['foot']['legal'] == '© 2026 Tallyfern' and [x['t'] for x in d['foot']['links']] == ['Terms', 'Privacy']
    # pictures: the page's own images once each (the larger of two sizes), no made picture, no agent's crop, no shot placed as a screen
    assert d['media'] == {'screens': [], 'phones': [], 'video': None, 'photos': [{'src': 'media/img1.jpg', 'w': 1600, 'h': 1000, 'alt': 'A fruit stall at dawn'}]}
    assert d['_media'] == {'media/logo.svg': {'from': 'assets.logo'}, 'media/img1.jpg': {'from': 'images', 'id': 'img1'}}
    assert [s['id'] for s in d['_adapter']['candidates']['shots']] == ['shot1']
    gaps = ' '.join(d['_adapter']['gaps'])
    for named in ('character', 'hero.note', 'media.screens', 'media.video', 'steps.items[].img', 'plans.items[].rows', 'foot.text', 'quotes', 'logos'):
        assert named in gaps, named


def test_a_restaurant_gets_its_place_block_from_links_and_from_lines_the_page_confirms():
    seed = restaurant()
    d = A.adapt(copy.deepcopy(seed))
    assert A.validate(d) == [] and invented(d, seed) == []
    assert d['kind'] == 'restaurant' and d['brand']['name'] == 'Casa Olmo' and d['brand']['logo'] is None and 'signin' not in d and 'plans' not in d
    assert d['hero']['title'] == 'Casa Olmo cocina de arroces' and d['hero']['text'] == 'Arroces a la leña en el barrio de Ruzafa'
    assert d['cta'] == {'t': 'Reservar', 'h': 'https://casaolmo.example/reservas/'} == d['hero']['primary'] and d['hero']['secondary'] == {'t': 'La carta', 'h': 'https://casaolmo.example/carta/'}
    assert [n['t'] for n in d['nav']] == ['La carta', 'Contacto'] and d['foot']['links'] == [{'t': 'Aviso legal', 'h': 'https://casaolmo.example/aviso-legal/'}]
    assert d['palette']['accent'] == '#b3541e'                                       # the button colour, not the share button's blue the capture called the brand's
    p = d['place']
    assert p['address'] == {'street': 'Calle del Olmo 4', 'postcode': '46006', 'city': 'Valencia'}
    assert p['phone'] == {'t': '912 345 678', 'h': 'tel:912345678', 'note': 'desde las 13:00h'} and p['email'] == 'hola@casaolmo.example'
    # the reader's third line of hours is not on the page: it is left out, the two that are stay
    assert p['hours'] == [{'days': 'De martes a sábado', 'open': '13:30h', 'close': '16:00h'}, {'days': 'Domingos', 'open': '13:30h', 'close': '17:00h'}]
    assert p['booking'] == {'t': 'Reservar', 'h': 'https://casaolmo.example/reservas/'} and p['since'] == '1987' and p['takeaway']['h'].endswith('/para-llevar/')
    assert p['social'] == [{'t': 'Instagram', 'h': 'https://www.instagram.com/casaolmo/'}]                 # a share button is not the restaurant's page
    assert p['price_range'] == '20 - 40' and p['cuisine'] == ['Arroces', 'Mediterránea']
    m = p['menu']
    assert m['h'] == 'https://casaolmo.example/carta/'
    assert m['sections'][:2] == [{'t': 'Arroces', 'count': 6, 'h': 'https://casaolmo.example/carta/arroces/'}, {'t': 'De la huerta', 'count': 4, 'h': 'https://casaolmo.example/carta/de-la-huerta/'}]
    assert m['sections'][2]['t'] == 'Arroces' and [(i['name'], i['price']) for i in m['sections'][2]['items']] == [('Arroz del señoret', '18,50 €'), ('Arroz negro', '17,00 €')]
    assert 'Paella' not in json.dumps(d, ensure_ascii=False)                          # the reader's dish the page does not print
    assert d['media']['photos'][1] == {'src': 'media/img2.jpg', 'w': 600, 'h': 400, 'alt': 'Arroz', 'small': True} and all('role' not in x for x in d['media']['photos'])
    gaps = ' '.join(d['_adapter']['gaps'])
    for named in ('brand.logo', 'place.spaces', 'place.address.country', 'media.photos', 'sections: the capture cut the home page into no headed sections'):
        assert named in gaps, named


def links_of(v, key=''):
    if isinstance(v, dict):
        for k, x in v.items():
            if not k.startswith('_'):
                yield from links_of(x, k)
    elif isinstance(v, list):
        for x in v:
            yield from links_of(x, key)
    elif key in ('h', 'home') and isinstance(v, str):                 # a picture's h is its height
        yield v


def test_a_link_that_would_run_script_is_not_carried_into_our_page():
    seed = product()
    inv = seed['inventory']
    inv['actions'] = [{'text': 'LEDGER', 'href': 'javascript:alert(1)'}, {'text': 'PRICING', 'href': 'data:text/html,<script>alert(1)</script>'},
                      {'text': 'LOG IN', 'href': ' JaVaScRiPt:alert(2)'}, {'text': 'Terms', 'href': 'vbscript:x'}] + inv['actions'][6:]
    inv['sourceCoverage']['sections'][0]['sourceActions'] = [{'label': 'START A LEDGER →', 'url': 'javascript:steal()'}, {'label': 'SEE A SAMPLE MONTH →', 'url': inv['url'] + 'sample'}]
    inv['sourceCoverage']['sections'][3]['sourceActions'][0]['url'] = 'https://www.tallyfern.example/x" onmouseover="alert(1)'
    d = A.adapt(seed)
    links = list(links_of(d))
    assert links and all(A.safe_href(h) == h for h in links), [h for h in links if A.safe_href(h) != h]
    assert 'script' not in json.dumps(d).lower() and 'onmouseover' not in json.dumps(d)
    assert d['nav'] == [] and 'signin' not in d and d['hero']['primary']['t'] == 'See a sample month' and 'cta' not in d['plans']['items'][0]
    for ok in ('https://a.example/p?q=1#f', 'http://a.example', 'mailto:a@b.example', 'tel:+34 912 345 678', 'tel:916866315'):
        assert A.safe_href(ok) == ok
    for bad in ('javascript:alert(1)', 'data:text/html,x', '//evil.example', '/relative', '#top', 'tel:<script>', 'https://a.example/"><script>', '', None, 'ftp://a.example'):
        assert A.safe_href(bad) is None, bad
    for make in (product, restaurant):
        assert all(A.safe_href(h) == h for h in links_of(A.adapt(make())))


def test_the_adapter_is_a_pure_function_and_survives_an_empty_capture():
    for make in (product, restaurant):
        seed = make()
        kept = copy.deepcopy(seed)
        a, b = A.adapt(seed), A.adapt(copy.deepcopy(kept))
        assert seed == kept, 'the capture is not changed'
        assert json.dumps(a, ensure_ascii=False, sort_keys=True) == json.dumps(b, ensure_ascii=False, sort_keys=True)
    d = A.adapt({})
    assert A.validate(d) == [] and d['hero']['title'] == d['brand']['name'] and d['kind'] == '' and d['media']['photos'] == []
    assert any(g.startswith('kind:') for g in d['_adapter']['gaps'])
    d = A.adapt({'inventory': {'url': 'https://plain.example/', 'title': 'Plain Co', 'copy': {'h1': 'ONE LINE', 'text': 'ONE LINE'}}, 'images': [None, 'x', {'id': 'a'}]})
    assert A.validate(d) == [] and d['hero']['title'] == 'One line' and d['brand']['name'] == 'Plain Co'
    src = (ROOT / 'lib' / 'templates' / 'adapt.py').read_text(encoding='utf-8')
    assert not re.search(r'^\s*(?:import|from)\s+(?:anthropic|openai|requests|httpx|urllib\.request|socket|subprocess|random|time|datetime)\b', src, re.M), 'no model, no network, no clock, no chance'
    assert not re.search(r'sportbot|automateed|butarque|balamo|courtsensei|simscore|scanmysaas|pdfbeautifier', src, re.I), 'no rule names one site'


def test_text_rules_keep_running_text_and_drop_what_the_flattened_capture_ran_together():
    assert A.lead('One clear sentence. A second one! Then a label without an end') == 'One clear sentence. A second one!'
    assert A.lead('A tagline before a button', bounded=True) == 'A tagline before a button' and A.lead('A tagline before a button') == ''
    assert A.lead('Fine sentence. Léo CO-FOUNDER · POINT GUARD · 170+ EUROLEAGUE GAMES over a decade.') == 'Fine sentence.'
    assert A.lead('Fine sentence. Plays Practice Scouting Video Teams Live game is here.') == 'Fine sentence.'
    assert A.lead('Upload any finished document — PDF, DOCX, or TXT. No account needed.') == 'Upload any finished document — PDF, DOCX, or TXT. No account needed.'
    assert A.lead('Shipping with Cursor, Claude, Codex or Lovable? Run a scan.') == 'Shipping with Cursor, Claude, Codex or Lovable? Run a scan.'
    # the same rules on a page that is not in Latin letters, or uses č ć š ž đ
    assert A.sentences('Čuvamo knjige tezge. Šta nudimo? Žurite! Đaci plaćaju manje.') == ['Čuvamo knjige tezge.', 'Šta nudimo?', 'Žurite!', 'Đaci plaćaju manje.']
    assert A.lead('Водимо књиге ваше тезге за једно вече. Проверите их једном недељно. ПОЧНИТЕ ОДМАХ') == 'Водимо књиге ваше тезге за једно вече. Проверите их једном недељно.'
    assert A.lead('Добра реченица. Лео СУОСНИВАЧ · ПЛЕЈМЕЈКЕР · 170+ УТАКМИЦА ЕВРОЛИГЕ током деценије.') == 'Добра реченица.'
    assert A.caps_head('ЦЕНЕ, СА РАЗЛОГОМ Свака цена носи маржу кладионице.') == ('ЦЕНЕ, СА РАЗЛОГОМ', 'Свака цена носи маржу кладионице.')
    assert A.caps_head('PICKS, WITH THE WHY Rule-based picks against the price.') == ('PICKS, WITH THE WHY', 'Rule-based picks against the price.')
    assert A.caps_head('Start a ledger') is None and A.caps_head('产品 功能 说明 这是一个没有大小写的句子，不应被当作标签。') is None and A.caps_head('ONLY CAPITALS HERE') is None
    assert A.Corpus(['Водимо књиге. Ценовник је једноставан.']).recase('ЦЕНОВНИК') == 'Ценовник' and A.Corpus(['x']).recase('价格') == '价格'
    # two sizes of one file are one picture; two pictures behind one image service are two
    assert A._stem('https://a.example/up/IMG_0468-scaled-800x600.jpeg') == A._stem('https://a.example/up/IMG_0468-scaled.jpeg?id=13095') == 'https://a.example/up/IMG_0468'
    assert A._stem('https://a.example/_next/image?url=%2Fone.png&w=1080&q=75') == A._stem('https://a.example/_next/image?url=%2Fone.png&w=640&q=75') != A._stem('https://a.example/_next/image?url=%2Ftwo.png&w=1080&q=75')
    two = A.adapt({'images': [{'id': 'a', 'src': 'https://a.example/_next/image?url=%2Fone.png&w=1080&q=75', 'w': 1080, 'h': 600, 'data': PX}, {'id': 'b', 'src': 'https://a.example/_next/image?url=%2Ftwo.png&w=1080&q=75', 'w': 1080, 'h': 600, 'data': PX},
                              {'id': 'c', 'src': 'https://a.example/_next/image?url=%2Fone.png&w=1920&q=75', 'w': 1920, 'h': 1067, 'data': PX}, {'id': 'd', 'src': 'x', 'w': '900', 'h': None, 'data': PX}]})
    assert [(p['src'], p['w']) for p in two['media']['photos']] == [('media/c.jpg', 1920), ('media/b.jpg', 1080)] and set(two['_media']) == {'media/c.jpg', 'media/b.jpg'}
    assert A.strip_label('START NOW →') == 'START NOW' and A.strip_label('More >>') == 'More' and A.strip_label('La tarta «de queso»') == 'La tarta «de queso»'
    c = A.Corpus(['We cover the NBA and our AI Desk answers. Pricing is simple. GET STARTED', 'PDF in, pdf out'], ['Visita Virtual'])
    assert c.recase('AI DESK') == 'AI Desk' and c.recase('PRICING') == 'Pricing' and c.recase('NBA PRICING') == 'NBA Pricing' and c.recase('VISITA VIRTUAL') == 'Visita Virtual'
    assert c.recase('GET STARTED') == 'Get started' and c.recase('Already Mixed') == 'Already Mixed' and c.recase('ÚNICO') == 'Único'
    assert c.says('$0') is False and A.Corpus(['from $0.63 a day']).says('$0', whole=True) is False and A.Corpus(['it is $0 today']).says('$0', whole=True)
    assert A.kind_of({'what': 'Mesa is a booking platform for restaurants.'}, {}) == ('software', 'reader: what')
    assert A.kind_of({'what': 'Olmo is a family restaurant with an app for orders.'}, {})[0] == 'restaurant'
    assert A.kind_of({}, {'title': 'Hotel Sol | Rooms by the sea'})[0] == 'hotel' and A.kind_of({}, {}) == ('', '')


@pytest.mark.parametrize('make', [product, restaurant])
def test_every_template_renders_what_the_adapter_gives(make):
    d = A.adapt(make())
    for slug in R.slugs():
        assert R.audit(slug, {'adapted': d}) == [], slug
        page = R.render(slug, d, 'https://preview.example/job/')
        used = R.media_used(slug, d)                                  # a template need not show every picture; what it shows is re-based
        assert d['hero']['title'].split()[0] in page and all('https://preview.example/job/' + p in page for p in used), (slug, used)


# ───────────────────────── the eight frozen real captures
@needs_seeds
def test_all_eight_frozen_captures_are_here():
    assert len(SEED_IDS) >= 8, SEED_IDS


@needs_seeds
@pytest.mark.parametrize('sid', SEED_IDS)
def test_a_real_capture_gives_valid_data_with_nothing_invented(sid):
    seed, d = adapted(sid)
    assert A.validate(d) == []
    assert invented(d, seed) == []
    again = A.adapt(A.load_seed(SEEDS / sid))
    assert json.dumps(again, ensure_ascii=False, sort_keys=True) == json.dumps(d, ensure_ascii=False, sort_keys=True)
    assert d['brand']['name'] and d['hero']['title'] and d['lang'] and d['kind'] in ('software', 'restaurant')
    assert set(d['_media']) == set(R.media_paths({k: v for k, v in d.items() if not k.startswith('_')}))
    ids = {im.get('id') for im in seed['images'] if isinstance(im, dict)}
    assert all(m['from'] != 'images' or m['id'] in ids for m in d['_media'].values())
    assert not [p for p in d['media']['photos'] if re.search(r'gen-|shot', p['src'])], 'no made picture and no shot among the photographs'
    assert all(A.safe_href(h) == h for h in links_of(d))
    assert len(d['_adapter']['gaps']) >= 8


@needs_seeds
@pytest.mark.parametrize('sid', SEED_IDS)
def test_every_template_renders_a_real_adapted_capture(sid):
    _, d = adapted(sid)
    for slug in R.slugs():
        assert R.audit(slug, {sid: d}) == [], slug


@needs_seeds
def test_against_the_hand_made_files_the_facts_agree():
    """Where the hand-made data and the adapter both state a fact of the client, it is the same fact. (What the hand
    chose — which sentence leads, which plans to show — is compared and reported in the PR, not pinned here.)"""
    if not HAND or not all((HAND / (n + '.json')).is_file() for n in ('sportbot', 'automateed', 'butarque')):
        pytest.skip('the hand-made data files of the real test clients are not on this machine (they are not in git)')
    hand = {n: json.loads((HAND / (n + '.json')).read_text(encoding='utf-8')) for n in ('sportbot', 'automateed', 'butarque')}
    if 'restaurantebutarque' in SEED_IDS:
        mine, h = adapted('restaurantebutarque')[1], hand['butarque']
        hp = h['place']
        assert mine['brand']['name'] == h['brand']['name'] and mine['lang'] == h['lang'] and mine['kind'] == h['kind'] and mine['brand']['home'] == h['brand']['home']
        assert mine['hero']['title'] == h['hero']['title'] and mine['hero']['text'] == h['hero']['text']
        assert mine['palette']['ground'] == h['palette']['ground'] and mine['palette']['ink'] == h['palette']['ink'] and mine['palette']['accent'] == h['palette']['accent']
        for k in ('address', 'phone', 'email', 'hours', 'booking', 'since'):
            assert mine['place'][k] == hp[k], k
        assert mine['place']['menu']['h'] == hp['menu']['h']
        strip = lambda xs: [{k: v for k, v in x.items() if k != 'items' or v} for x in xs]
        assert strip(mine['place']['menu']['sections']) == strip(hp['menu']['sections'])
        assert [(x['count'], x['h']) for x in mine['place']['menu']['lists']] == [(x['count'], x['h']) for x in hp['menu']['lists']]
        assert mine['cta'] == h['cta'] and {n['h'].rstrip('/') for n in mine['nav']} == {n['h'].rstrip('/') for n in h['nav']}
    if 'sportbotai' in SEED_IDS:
        mine, h = adapted('sportbotai')[1], hand['sportbot']
        assert mine['brand']['name'] == h['brand']['name'] and mine['lang'] == h['lang'] and mine['kind'] == h['kind'] and mine['signin'] == h['signin']
        assert mine['palette']['ground'] == h['palette']['ground'] and mine['palette']['accent'] == h['palette']['accent']
        assert mine['statement']['title'].rstrip('.') == h['statement']['title'] and h['statement']['text'] in mine['statement']['text']
        assert mine['steps']['title'] == h['steps']['title'] and [(i['k'], i['title'], i['text']) for i in mine['steps']['items']] == [(i['k'], i['title'], i['text']) for i in h['steps']['items']]
        assert mine['features']['title'].rstrip('.') == h['features']['title'] and mine['features']['text'] == h['features']['text']
        assert [i['d'] for i in mine['features']['items']][:4] == [i['d'] for i in h['features']['items']][:4]
        assert {i['q'] for i in h['faq']['items']} <= {i['q'] for i in mine['faq']['items']} and mine['faq']['title'] == h['faq']['title']
        assert [(p['name'], p['price']) for p in mine['plans']['items']][:2] == [(p['name'], p['price']) for p in h['plans']['items']] and mine['plans']['text'] == h['plans']['text']
        assert mine['close']['title'] == h['close']['title'] and mine['foot']['legal'] == h['foot']['legal'] and set(h['trust'][:3]) >= set(mine['trust'])
    if 'automateed' in SEED_IDS:
        mine, h = adapted('automateed')[1], hand['automateed']
        assert mine['brand'] == {**h['brand'], 'logo': 'media/logo.svg'} and mine['hero']['title'] == h['hero']['title'] and mine['nav'] == h['nav'] and mine['signin'] == h['signin']
        assert {p['name'] for p in h['plans']['items']} <= {p['name'] for p in mine['plans']['items']}
