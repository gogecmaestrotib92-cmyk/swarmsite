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
OWN = {'h', 'home', 'src', 'logo', 'img', 'poster', 'ground', 'ink', 'accent', 'extra', 'lang', 'kind', 'niche', 'count', 'w', 'h', 'small', 'logo_wordmark', 'shape', 'page'}   # niche: a classifier, never shown


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
            if where == 'plans.note':                                               # offers that are not cards: each the page's own name and its own price
                return out.extend((where, p) for p in v.split(' · ') if not (said.says(p.rsplit(' ', 1)[0]) and said.says(p.rsplit(' ', 1)[-1])))
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
    assert len(files) >= 12 and all('made-up client' in json.loads(f.read_text(encoding='utf-8'))['_note'] for f in files), 'a made-up client for software (2), restaurant, hotel, clinic, law, service, school, works, charity, person and shop at least'
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
    # the bar: capitals by style are set as the page's running text spells the words; the button is the call; a link to a
    # part of the client's own page stands and leads there (owner, 2026-11-22: "we swallow their menu tabs")
    assert d['nav'] == [{'t': 'Ledger', 'h': 'https://www.tallyfern.example/ledger'}, {'t': 'Pricing', 'h': 'https://www.tallyfern.example/pricing'}, {'t': 'Guide', 'h': 'https://www.tallyfern.example/#guide'}]
    assert d['signin'] == {'t': 'Log in', 'h': 'https://www.tallyfern.example/login'} and d['cta'] == {'t': 'Start a ledger', 'h': 'https://www.tallyfern.example/signup'}
    assert any(r.startswith('nav: 1 link') and 'Guide' in r for r in d['_adapter']['rules'])
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
    # pictures: the page's own images once each (the larger of two sizes), no made picture, no agent's crop; a framed part of
    # the home page with the build of a screen stands as a screen while the product's pages gave none — but never beside a step
    assert d['media'] == {'screens': [{'src': 'media/shot1.jpg', 'w': 1200, 'h': 700, 'alt': 'The ledger'}], 'phones': [], 'video': None,
                          'photos': [{'src': 'media/img1.jpg', 'w': 1600, 'h': 1000, 'alt': 'A fruit stall at dawn'}]}
    assert d['_media'] == {'media/logo.svg': {'from': 'assets.logo'}, 'media/img1.jpg': {'from': 'images', 'id': 'img1'}, 'media/shot1.jpg': {'from': 'images', 'id': 'shot1'}}
    assert [s['id'] for s in d['_adapter']['candidates']['shots']] == ['shot1'] and not any(i.get('img') for i in d['steps']['items'])
    gaps = ' '.join(d['_adapter']['gaps'])
    for named in ('character', 'hero.note', 'media.video', 'steps.items[].img', 'plans.items[].rows', 'foot.text', 'quotes', 'logos'):
        assert named in gaps, named


def test_a_product_gets_its_own_screens_its_price_cards_and_its_large_figures():
    """the pages behind the top bar photographed (capture product.json) become screens and phones, and each step takes the
    phone of the page its own call leads to; the page's price cards give each plan its list; a number set large with its
    label is a figure; a badge beside a link is not part of its name; a notice the capture marked plain is no photograph"""
    seed = product()
    home = 'https://www.tallyfern.example/'
    seed['inventory']['brand']['nav'][1] = 'LEDGER NEW'
    seed['inventory']['actions'].insert(2, {'text': 'LEDGER NEW', 'href': home + 'ledger'})
    sec = seed['inventory']['sourceCoverage']['sections'][2]
    sec['sourceActions'] = [{'label': 'Open the camera', 'url': home + 'camera'}, {'label': 'See the sorting', 'url': home + 'sort'}, {'label': 'Read a month', 'url': home + 'month/'}]
    sec['text'] = ('How it works Three small things, in order. 01 Photograph Snap each receipt as you get it. Open the camera 02 Sort Tallyfern files it under stock, rent or pay. '
                   'See the sorting 03 Close Read the month on one page and send it to your accountant. Read a month')
    seed['inventory']['copy']['text'] += ' Stall €9 / month For one stall Up to 200 receipts a month Export to CSV Row €29 / month Unlimited receipts Five people 12 hours saved each month'
    pages = [('month', 'Month'), ('camera', 'Camera'), ('sort', 'Sorting'), ('prices', 'Prices')]
    seed['product'] = {'screens': [{'id': 'screen%d' % i, 'url': home + p, 'alt': lab, 'w': 1800, 'h': 1125, 'data': PX} for i, (p, lab) in enumerate(pages)],
                       'phones': [{'id': 'phone%d' % i, 'url': home + p, 'alt': lab, 'w': 780, 'h': 1616, 'data': PX} for i, (p, lab) in enumerate(pages)]}
    seed['cards'] = {'plans': [{'name': 'Stall', 'price': '€9', 'per': '/ month', 'line': 'For one stall', 'rows': ['Up to 200 receipts a month', 'Export to CSV'], 'marked': False},
                               {'name': 'Row', 'price': '€29', 'per': '/ month', 'line': '', 'rows': ['Unlimited receipts', 'Five people', 'A line the page never printed'], 'marked': True}],
                     'stats': [{'v': '12', 'l': 'hours saved each month'}, {'v': '99', 'l': 'words nobody wrote'}]}
    seed['images'].append({'id': 'img3', 'src': home + 'img/notice.png', 'w': 900, 'h': 600, 'alt': 'Opening hours notice', 'plain': True, 'data': PX})
    d = A.adapt(copy.deepcopy(seed))
    assert A.validate(d) == [] and invented(d, seed) == []
    assert [n['t'] for n in d['nav']] == ['Ledger', 'Pricing', 'Guide']
    assert [s['src'] for s in d['media']['screens']] == ['media/screen-%d.jpg' % i for i in (1, 2, 3, 4)] and len(d['media']['phones']) == 4
    assert d['media']['screens'][0] == {'src': 'media/screen-1.jpg', 'w': 1800, 'h': 1125, 'alt': 'Month', 'page': '/month'}
    assert d['_media']['media/phone-3.jpg'] == {'from': 'product', 'kind': 'phones', 'index': 2}
    assert [(i['img'], i['shape']) for i in d['steps']['items']] == [('media/phone-2.jpg', 'phone'), ('media/phone-3.jpg', 'phone'), ('media/phone-1.jpg', 'phone')], 'each step: the phone of the page its call opens'
    assert not any(p['src'] == 'media/img3.png' for p in d['media']['photos']), 'a plain notice is not a photograph'
    st, row = d['plans']['items']
    assert st['rows'] == ['Up to 200 receipts a month', 'Export to CSV'] and st['line'] == 'For one stall' and not st.get('marked')
    assert row['rows'] == ['Unlimited receipts', 'Five people'] and row['marked'] is True, 'a row the page does not print is left out'
    assert {'v': '12', 'l': 'hours saved each month'} in d['figures'] and not any(f['v'] == '99' for f in d['figures'])
    # steps the page numbers itself (1 2 3 beside a heading and a sentence, not sub-headings): read from the capture's cards
    bare = product()
    bare['inventory']['copy']['headings'] = [h for h in bare['inventory']['copy']['headings'] if h['text'] not in ('Photograph', 'Sort', 'Close')]
    run = [{'k': '01', 'title': 'Photograph', 'text': 'Snap each receipt as you get it.'}, {'k': '02', 'title': 'Sort', 'text': 'Tallyfern files it under stock, rent or pay.'},
           {'k': '03', 'title': 'Close', 'text': 'Read the month on one page and send it to your accountant.'}]
    assert 'steps' not in A.adapt(copy.deepcopy(bare))
    bare['cards'] = {'steps': [{'title': 'A heading nobody set', 'items': run[:2] + [{'k': '3', 'title': 'Close', 'text': 'A sentence the page never printed.'}]}, {'title': 'How it works', 'items': run}]}
    got = A.adapt(copy.deepcopy(bare))
    assert got['steps']['title'] == 'How it works' and [(i['k'], i['title'], i['text']) for i in got['steps']['items']] == [(x['k'], x['title'], x['text']) for x in run] and invented(got, bare) == []
    # a block the adapter's rules cannot cut out is taken from the reader's `page` — only what stands on the page letter for letter
    marked = product()
    marked['inventory']['copy']['headings'] = [h for h in marked['inventory']['copy']['headings'] if h['text'] not in ('Photograph', 'Sort', 'Close')]
    marked['factsheet']['page'] = {'steps': {'title': 'How it works', 'text': 'Three small things, in order.', 'items': [
        {'title': 'Photograph', 'text': 'Snap each receipt as you get it.'}, {'title': 'Sort', 'text': 'Tallyfern files it under stock, rent or pay.'},
        {'title': 'Close', 'text': 'Read the month on one page and send it to your accountant.'}, {'title': 'Relax', 'text': 'A step the reader made up.'}]},
        'trust': ['Never seen on the page'], 'figures': [{'v': '12', 'l': 'markets the page never names'}], 'note': 'A note of the reader\'s own'}
    got = A.adapt(copy.deepcopy(marked))
    assert [i['title'] for i in got['steps']['items']] == ['Photograph', 'Sort', 'Close'] and got['steps']['title'] == 'How it works' and invented(got, marked) == []
    assert 'note' not in got['hero'] and got['figures'] == [{'v': '4,210', 'l': 'stalls keep their books here'}] and any('from the reader' in r for r in got['_adapter']['rules'])
    marked['factsheet']['page']['steps']['items'] = [{'title': 'Take a photo', 'text': 'Snap receipts.'}, {'title': 'Sorting', 'text': 'It files them.'}]
    assert 'steps' not in A.adapt(copy.deepcopy(marked)), 'reworded steps are not on the page: no block'
    # fewer screens of the product's pages than steps: the first steps show the product as the home page shows it
    # (a software page's pictures are its screens), a step past them keeps its words without one
    seed['product']['phones'] = seed['product']['phones'][:2]
    seed['product']['screens'] = seed['product']['screens'][:2]
    d = A.adapt(copy.deepcopy(seed))
    got = [i.get('img') for i in d['steps']['items']]
    assert len([g for g in got if g]) >= 2 and len(set(g for g in got if g)) == len([g for g in got if g]), got
    assert any(r.startswith('steps.items[].img:') and 'as the home page shows it' in r for r in d['_adapter']['rules'])


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
        used = R.media_used(slug, d)                                  # a template need not show every picture (one of another niche may take only the logo); what it shows is served from the job's base
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


def test_a_label_is_not_a_headline_and_one_statement_is_one_heading():
    """a page with no h1 whose first heading is a section's label ("Latest News"): the name is the headline, not the
    label; and a statement whose title is the headline again is not a second section — its text joins the opening"""
    say = 'With your help the animals that come to us are fed, treated and found a home that will keep them.'
    text = 'Latest News ' + say + ' Animals for adoption Cats Rabbits'
    inv = {'url': 'https://fernhollow.example/', 'title': 'Fernhollow Rescue', 'copy': {'text': text, 'headings': [{'text': 'Latest News'}, {'text': 'Animals for adoption'}]}}
    d = A.adapt({'inventory': inv})
    assert A.validate(d) == [] and d['hero']['title'] == 'Fernhollow Rescue', 'a two-word heading is a label: the name stands in'
    assert any('first heading is a label' in g for g in d['_adapter']['gaps'])
    d = A.adapt({'inventory': inv, 'factsheet': {'best_sentence': say, 'page': {'statement': {'title': 'Latest News', 'text': say}}}})
    assert d['hero']['title'] == 'Fernhollow Rescue' and d['hero']['text'] == say and 'statement' not in d, 'under the name, the sentence the reader singled out; not said twice'
    inv3 = {**inv, 'copy': {'text': text, 'headings': [{'text': 'A home for every animal'}, {'text': 'Latest News'}]}}
    assert A.adapt({'inventory': inv3})['hero']['title'] == 'A home for every animal', 'a first heading of three words or more stands in'
    # the headline said again as the statement's title: one heading, the text with the opening
    inv1 = {**inv, 'copy': {'h1': 'Latest News', 'text': text, 'headings': [{'text': 'Latest News'}]}}
    d = A.adapt({'inventory': inv1, 'factsheet': {'page': {'statement': {'title': 'Latest News', 'text': say}}}})
    assert A.validate(d) == [] and 'statement' not in d and d['hero']['title'] == 'Latest News' and say in (d['hero'].get('text'), d['hero'].get('text2'))
    assert any(r.startswith('statement: left out') for r in d['_adapter']['rules'])
    # any other block headed by the headline keeps its content and loses the heading
    seed = product()
    d0 = A.adapt(copy.deepcopy(seed))
    blk = next(k for k, b in d0.items() if k not in ('hero', 'brand', 'statement') and isinstance(b, dict) and b.get('title'))
    seed['inventory']['copy']['h1'] = d0[blk]['title']
    d1 = A.adapt(seed)
    assert A.validate(d1) == [] and 'title' not in d1[blk] and {k: v for k, v in d0[blk].items() if k != 'title'} == d1[blk] and any(r.startswith(blk + '.title: left out') for r in d1['_adapter']['rules'])
    # the short line beside the opening that is one of the page's figures is said once, as the figure
    fig = 'Latest News 35,411 people like this. ' + say
    d = A.adapt({'inventory': {**inv1, 'copy': {'h1': 'A home for every animal', 'text': fig, 'headings': []}}, 'factsheet': {'page': {'note': '35,411 people like this', 'figures': [{'v': '35,411', 'l': 'people like this'}]}}})
    assert (not d.get('figures')) or 'note' not in d['hero'], 'a figure is not also the note'
    assert d.get('figures') and d['figures'][0]['v'] == '35,411', 'the reader\'s figure is kept (else this case tests nothing)'
    # a statement with a heading of its own stays
    d = A.adapt({'inventory': {**inv1, 'copy': {'h1': 'A home for every animal', 'text': 'A home for every animal ' + text, 'headings': []}}, 'factsheet': {'page': {'statement': {'title': 'Latest News', 'text': say}}}})
    assert d.get('statement', {}).get('title') == 'Latest News'


def test_a_list_of_bare_labels_is_carried_and_the_data_says_what_of_the_page_it_holds():
    """a place that lists what it has as labels (no sentence each): the list stands as it stands on the page; and the
    adapter counts which of the page's sections reached the data"""
    labels = ['Cafe', 'Free parking', 'Showers', 'Shop', 'Baby changing']
    text = 'Millbrook Services on the old north road. Everything for a stop on the way. Our services ' + ' '.join(labels)
    inv = {'url': 'https://millbrook.example/', 'title': 'Millbrook Services', 'copy': {'h1': 'Millbrook Services on the old north road', 'text': text, 'headings': []}}
    fs = {'page': {'features': {'title': 'Our services', 'items': [{'t': x} for x in labels]}}}
    d = A.adapt({'inventory': inv, 'factsheet': fs})
    assert A.validate(d) == [] and [i['t'] for i in d['features']['items']] == labels and not any(i.get('d') for i in d['features']['items'])
    assert A.adapt({'inventory': inv, 'factsheet': {'page': {'features': {'title': 'Our services', 'items': [{'t': x} for x in labels[:3]]}}}}).get('features') is None, 'three bare labels are not yet a list'
    cv = d['_adapter']['coverage']
    assert set(cv) == {'sections', 'carried', 'left'} and cv['carried'] <= cv['sections'] and isinstance(cv['left'], list)


def test_a_headings_words_inside_a_sentence_are_not_a_border():
    """a later heading whose words also stand in running text (a place's own name) does not cut the passage there"""
    text = 'On the old north road stands our stop Millbrook Halt . It has a cafe and a shop. MILLBROOK HALT Open every day.'
    assert A.cut_at(text, ['MILLBROOK HALT'])[0] == 'On the old north road stands our stop Millbrook Halt . It has a cafe and a shop.'
    assert A.cut_at('A fine place. Millbrook Halt Open every day.', ['MILLBROOK HALT'])[0] == 'A fine place.', 'after a full stop it is the heading'
    assert A.cut_at('See the prices Our Plans Start free.', ['Our Plans'])[0] == 'See the prices', 'written as the heading is: the heading'
    assert A.cut_at('Inside there are tables, a cafe, Self Service, a grill and shops. Self Service Open all day.', ['Self Service'])[0] == 'Inside there are tables, a cafe, Self Service, a grill and shops.', 'after a comma it is an item of the sentence'


def test_the_states_of_a_product_demo_are_its_screens_each_once_in_the_demos_order():
    """capture photographs each tab of the page's own product demo (images.json: shot, state); those are the product's
    screens — all of them, in the demo's order, before any other framed part of the page"""
    seed = product()
    seed['product'] = {}
    px = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAAA//EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AN//Z'
    seed['images'] = [i for i in seed['images'] if not (isinstance(i, dict) and i.get('shot'))]
    seed['images'] += [{'id': 'shot1', 'src': 'visual-shot', 'shot': True, 'w': 1200, 'h': 800, 'alt': 'The ledger', 'data': px}]
    seed['images'] += [{'id': 'tab%d' % (n + 1), 'src': 'visual-shot', 'shot': True, 'state': name, 'alt': name, 'w': 900, 'h': 560, 'data': px} for n, name in enumerate(['Ledger', 'Receipts', 'Month', 'Export'])]
    d = A.adapt(copy.deepcopy(seed))
    assert [x['src'] for x in d['media']['screens']] == ['media/tab1.jpg', 'media/tab2.jpg', 'media/tab3.jpg', 'media/tab4.jpg'], d['media']['screens']
    assert [x['alt'] for x in d['media']['screens']] == ['Ledger', 'Receipts', 'Month', 'Export']
    assert any(r.startswith('media.screens: 4 state(s) of the page') for r in d['_adapter']['rules'])
    assert A.validate(d) == []


def test_a_trial_is_not_a_plan_a_close_is_said_once_and_a_buttons_label_is_not_a_cards_words():
    """what a thing on the client's page is decides where it stands (adapt._roles)"""
    cta = {'t': 'Start the trial', 'h': 'https://x.example/start'}
    d = {'brand': {'name': 'Courtline'}, 'hero': {'title': 'Your team. Your plan.'},
         'plans': {'title': 'One tool. One price.', 'items': [{'name': 'Head Coach', 'price': '€69', 'rows': []}, {'name': '14-day free trial', 'price': 'Free', 'cta': cta, 'rows': []}]},
         'close': {'title': 'One tool. One price.', 'text': 'x'},
         'links': [{'t': 'A practice', 'd': '2 pages · timed blocks and linked diagrams Open sample PDF', 'h': 'https://x.example/a.pdf'},
                   {'t': 'The opposition', 'd': '2 pages · 12 players and highlighted statistics Open sample PDF', 'h': 'https://x.example/b.pdf'}]}
    rules = []
    A._roles(d, rules)
    assert [p['name'] for p in d['plans']['items']] == ['Head Coach'] and d['plans']['items'][0]['cta'] == cta and d['plans']['note'] == '14-day free trial'
    assert 'close' not in d and [x['d'] for x in d['links']] == ['2 pages · timed blocks and linked diagrams', '2 pages · 12 players and highlighted statistics']
    assert len(rules) == 3 and A.validate(d) == []
    # the statement too: a heading that also heads a list is said once, and its sentence stands under the list's heading when that has none
    f = {'brand': {'name': 'P'}, 'hero': {'title': 'Your PDF, redesigned.'}, 'statement': {'title': '5 distinct art directions', 'text': 'Each is a complete visual system.'},
         'features': {'title': '5 distinct art directions', 'items': [{'t': 'Clinical'}, {'t': 'Editorial'}, {'t': 'Athletic'}]}, 'close': {'title': 'Try it', 'text': 'x'}}
    A._roles(f, [])
    assert 'statement' not in f and f['features']['text'] == 'Each is a complete visual system.' and f['close']['title'] == 'Try it'
    # a trial with a price is a plan; a list of only trials is left as it is; a close with its own heading stays; cards that end differently are not cut
    e = {'brand': {'name': 'C'}, 'hero': {'title': 'T'}, 'plans': {'items': [{'name': 'Trial month', 'price': '€9'}, {'name': 'Year', 'price': '€90'}]}, 'close': {'title': 'Start today'},
         'links': [{'t': 'a', 'd': 'Read the whole guide here'}, {'t': 'b', 'd': 'See every plan in detail'}]}
    before = json.loads(json.dumps(e))
    A._roles(e, [])
    assert e == before
    only = {'brand': {'name': 'C'}, 'hero': {'title': 'T'}, 'plans': {'items': [{'name': 'Free trial'}, {'name': 'Trial for teams'}]}}
    A._roles(only, [])
    assert len(only['plans']['items']) == 2


def test_a_page_a_product_makes_is_its_picture_though_the_capture_calls_it_plain():
    """a document tool's own "before" and "after" pages — large upright sheets the page shows with words of its own —
    are the product; a plain picture that is not such a sheet (a notice, a diagram) is still left out, and so is a sheet
    on a place's page (a menu photographed is not the restaurant)"""
    px = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAAA//EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AN//Z'
    seed = product()
    seed['product'] = {}
    seed['images'] = [{'id': 'img1', 'src': 'https://x.example/before.png', 'w': 1400, 'h': 1980, 'alt': 'Before — original document', 'plain': True, 'flat': .9, 'data': px},
                      {'id': 'img2', 'src': 'https://x.example/after.png', 'w': 1400, 'h': 1978, 'alt': 'After — the redesigned page', 'plain': True, 'flat': .96, 'data': px},
                      {'id': 'img3', 'src': 'https://x.example/notice.png', 'w': 1200, 'h': 400, 'alt': 'A notice about cookies', 'plain': True, 'flat': .97, 'data': px},
                      {'id': 'img4', 'src': 'https://x.example/blank.png', 'w': 1400, 'h': 1980, 'alt': '', 'plain': True, 'flat': .99, 'data': px}]
    d = A.adapt(copy.deepcopy(seed))
    assert [p['src'] for p in d['media']['photos']] == ['media/img1.jpg', 'media/img2.jpg'], d['media']['photos']
    assert A.validate(d) == []


def test_a_page_of_two_grounds_takes_the_one_its_own_theme_colour_agrees_with():
    """a dark product whose page is half dark, half pale: the ground is not whichever covers a few more boxes"""
    inv = {'colors': {'bg': [{'c': '#f7dbba', 'n': 1941}, {'c': '#14120f', 'n': 1727}, {'c': '#fbead1', 'n': 588}],
                      'text': [{'c': '#0a0806', 'n': 40}, {'c': '#ff4a1f', 'n': 33}, {'c': '#f7dbba', 'n': 26}], 'buttons': [{'c': '#ff4a1f', 'n': 1}]}}
    rules = []
    p = A.palette(inv, {'palette': {'themeColor': '#0D0F14'}}, [], rules)
    assert p['ground'] == '#14120f' and p['ink'] == '#f7dbba' and p['accent'] == '#ff4a1f' and any(r.startswith('palette.ground') for r in rules)
    # no theme colour, a theme colour of the first ground's tone, or a second ground that is a minor one: the first stays
    assert A.palette(inv, {}, [], [])['ground'] == '#f7dbba'
    assert A.palette(inv, {'palette': {'themeColor': '#fff8ee'}}, [], [])['ground'] == '#f7dbba'
    minor = {'colors': {**inv['colors'], 'bg': [{'c': '#f7dbba', 'n': 1941}, {'c': '#14120f', 'n': 400}]}}
    assert A.palette(minor, {'palette': {'themeColor': '#0D0F14'}}, [], [])['ground'] == '#f7dbba'


def test_the_screen_with_most_of_the_product_on_it_comes_first():
    """a template's opening takes the first screen; the capture's own score of each page says which shows most"""
    seed = product()
    home = 'https://www.tallyfern.example/'
    seed['product'] = {'screens': [{'id': 'screen%d' % i, 'url': home + p, 'alt': lab, 'w': 1800, 'h': 1125, 'data': PX, 'score': sc}
                                   for i, (p, lab, sc) in enumerate([('month', 'Month', 4.0), ('camera', 'Camera', 31.5), ('sort', 'Sorting', 12.0)])]}
    scr = seed['product']['screens']
    d = A.adapt(copy.deepcopy(seed))
    got = [m['src'] for m in d['media']['screens']][:3]
    assert got == ['media/screen-2.jpg', 'media/screen-3.jpg', 'media/screen-1.jpg'], got
    # how full the picture itself is comes before the page's count of controls: an empty state has every button and shows nothing
    for x, fill in zip(scr, (.41, .08, .39)):
        x['fill'] = fill
    got = [m['src'] for m in A.adapt(copy.deepcopy(seed))['media']['screens']]
    assert got[:2] == ['media/screen-3.jpg', 'media/screen-1.jpg'] and 'media/screen-2.jpg' not in got, 'fill 0.4, 0.4, 0.1: the two full ones by score; the empty one is not a picture of the product'
    # an empty state is not a picture of the product: under 15 % full it is left out where two fuller ones stand
    scr.append({'id': 'screen3', 'url': home + 'empty', 'alt': 'Empty', 'w': 1800, 'h': 1125, 'data': PX, 'score': 40.0, 'fill': .12})
    d2 = A.adapt(copy.deepcopy(seed))
    assert 'media/screen-4.jpg' not in [m['src'] for m in d2['media']['screens']] and any(r.startswith('media.screens: 2 screen(s) under 15') for r in d2['_adapter']['rules'])
    scr.pop()
    for x in scr:
        x.pop('score', None)
        x.pop('fill', None)
    assert [m['src'] for m in A.adapt(copy.deepcopy(seed))['media']['screens']][:3] == ['media/screen-1.jpg', 'media/screen-2.jpg', 'media/screen-3.jpg'], 'no score: the bar\'s own order'


def test_the_name_is_what_the_page_keeps_saying_not_the_shortest_part_of_its_title():
    """a Persian restaurant's title read `<what> <name> <branch> | Menu and booking`; its three designs were headed
    "Menu and booking" (a visitor's job, 2026-11-22)"""
    def name(title, texts, url='https://akbarjoojeh.example/', nav=(), actions=()):
        inv = {'url': url, 'title': title, 'brand': {'nav': list(nav)}, 'actions': [{'text': t, 'href': url} for t in actions]}
        return A.brand_name({}, inv, A.Corpus([title] + list(texts)))
    fa = ['درباره اکبر جوجه', 'خدمات رستوران اکبر جوجه', 'گالری اکبر جوجه 1', 'گالری اکبر جوجه 2', 'اکبر جوجه غذای اصلی و امضای رستوران ماست', '© ۱۴۰۵ اکبر جوجه شعبه مرکزی کرج', 'مشاهده منو و سفارش']
    got, why = name('رستوران اکبر جوجه شعبه مرکزی کرج | منو و رزرو', fa)
    assert got == 'اکبر جوجه' and 'says most' in why, (got, why)
    # a label of the menu is never the name, however often the page says it
    got, _ = name('Home | Olmo Tools', ['Home', 'Home', 'Home', 'Olmo Tools makes saws', 'About Olmo Tools', 'Olmo Tools Ltd'], url='https://x.example/', nav=['Home'])
    assert got == 'Olmo Tools'
    # the shortest part stands where the page says it as often as anything else of the title
    assert name('Tallyfern — Books for market stalls', ['Tallyfern keeps the books', 'Why Tallyfern', 'Tallyfern Ltd', 'Books for market stalls'], url='https://x.example/')[0] == 'Tallyfern'
    assert name('Casa Olmo - Arroces en Ruzafa', ['Casa Olmo cocina de arroces', 'Arroces a la leña', 'ARROCES', 'Arroz negro'], url='https://casaolmo.example/')[0] == 'Casa Olmo'
    # one common word said often is not a name: a single word counts only with a capital letter
    assert name('Fresh bread daily | Our bakery in town', ['bread', 'bread', 'bread and more bread', 'our bread', 'bread'], url='https://x.example/')[0] == 'Fresh bread daily'


def test_a_quote_is_signed_by_the_name_that_stands_beside_it_on_the_page():
    """a shop signs each customer's words after them with a dash; a reader paired every name with the words that
    follow it, and the last quote ran on through a signature into the next customer's (a visitor's job, 2026-11-22)"""
    L = 'I have used serums from many brands. This one feels so light on the skin, and my skin has never looked more alive.'
    V = 'The gold dissolves completely into my skin. I bought the serum for myself and now three friends want one.'
    E = 'I bought Oro for myself, and the fragrance is so amazing — everyone compliments me. A feeling you cannot resist.'
    names = ['— LUNA, LOS ANGELES', '— VANESSA, MIAMI', '— EMMA, NEW YORK']                 # headings, set in capitals by their style
    def page(order):
        run = ' '.join(order(q, n) for q, n in ((L, '— Luna, Los Angeles'), (V, '— Vanessa, Miami'), (E, '— Emma, New York')))
        return A.Corpus(['Worn by ' + run + ' ' + run + ' Join the Ritual'] + names)          # a carousel: its cards stand twice
    after = page(lambda q, n: q + ' ' + n)
    signs = A.signatures(after)
    assert signs == ['Luna, Los Angeles', 'Vanessa, Miami', 'Emma, New York'], 'as the page spells them, not as a style capitalises them'
    read = [(V, '— Luna, Los Angeles'), (E, '— Vanessa, Miami'), (L + ' — Luna, Los Angeles ' + V[:60], '— Emma, New York')]
    qs = [{'q': A._one_quote(q, signs), 'name': n, 'by': n} for q, n in read]
    assert qs[2]['q'] == L, 'a quote ends where a signature of the page begins'
    assert A._signed(qs, signs, after) == ('after', 3)
    assert [(x['name'], x['by']) for x in qs] == [('Vanessa, Miami',) * 2, ('Emma, New York',) * 2, ('Luna, Los Angeles',) * 2]
    # a page that signs before its quotes: the name before stands
    before = page(lambda q, n: n + ' ' + q)
    qs = [{'q': q, 'name': 'x', 'by': 'x'} for q in (L, V, E)]
    assert A._signed(qs, A.signatures(before), before) == ('before', 3) and [x['name'] for x in qs] == ['Luna, Los Angeles', 'Vanessa, Miami', 'Emma, New York']
    # a page that signs no quote with a dash: the reader's names are left alone
    plain = A.Corpus([L + ' ' + V + ' ' + E])
    qs = [{'q': L, 'name': 'Luna', 'by': 'Luna'}, {'q': V, 'name': 'Vanessa', 'by': 'Vanessa'}]
    assert A.signatures(plain) == [] and A._signed(qs, [], plain) is None and qs[0]['name'] == 'Luna' and A._one_quote(E, []) == E


def test_a_row_of_signed_cards_is_read_as_quotes_and_never_as_steps():
    """three customers' cards, each signed under its words with a dash, were taken for three steps named after the
    customers, each with the next customer's words (a visitor's job, 2026-11-22)"""
    L = 'I have used serums from many brands. This one feels so light on the skin, and my skin has never looked more alive.'
    V = 'The gold dissolves completely into my skin. I bought the serum for myself and now three friends want one.'
    E = 'I bought Oro for myself, and the fragrance is so amazing — everyone compliments me. A feeling you cannot resist.'
    run = '%s — Luna, Los Angeles %s — Vanessa, Miami %s — Emma, New York' % (L, V, E)
    def sec(text, kids):
        s = {'title': 'Worn by', 'text': text, 'kids': list(kids), 'quotes': [], 'used': ''}
        A._signed_cards(s)
        return s
    caps = ['— LUNA, LOS ANGELES', '— VANESSA, MIAMI', '— EMMA, NEW YORK']
    s = sec('Worn by ' + run + ' ' + run, caps)                       # a carousel: its cards stand twice
    assert [(q['attribution'], q['text']) for q in s['quotes']] == [('Luna, Los Angeles', L), ('Vanessa, Miami', V), ('Emma, New York', E)]
    assert s['kids'] == [] and s['used'] == 'quotes', 'no sub-heading is left for the steps to take'
    s = sec('Worn by — Luna, Los Angeles %s — Vanessa, Miami %s — Emma, New York %s' % (L, V, E), caps)
    assert [(q['attribution'], q['text']) for q in s['quotes']] == [('Luna, Los Angeles', L), ('Vanessa, Miami', V), ('Emma, New York', E)], 'signed above: each name over its own words'
    s = sec('How it works Photograph a receipt. — and more Sort it. Close the month.', ['Photograph', 'Sort', 'Close'])
    assert s['quotes'] == [] and s['kids'] == ['Photograph', 'Sort', 'Close'] and s['used'] == '', 'steps stay steps'
    s = sec('Worn by ' + run, caps + ['Our promise'])
    assert s['quotes'] == [] and len(s['kids']) == 4, 'a section that is not only signed cards is left as it is'


def test_a_product_sold_by_the_month_is_software_whoever_it_is_sold_to():
    """an autonomous front desk at $397/month for clinics was read as a clinic: three clinic designs, no picture of the
    product (a visitor's job, 2026-11-22)"""
    k = lambda what, title='': A.kind_of({'what': what}, {'title': title})[0]
    assert k('LadderFlow sells OmniDesk, a $397/month flat WhatsApp-based autonomous front desk that answers inquiries for dental clinics and medical practices.') == 'software'
    assert k('', 'LadderFlow — OmniDesk Autonomous Front Desk ($397/mo)') == 'software'
    assert k('Kerrisdale Dental is a dental clinic in Vancouver offering general and cosmetic dentistry.') == 'clinic', 'a clinic stays a clinic'
    assert k('Riverside Physio is a physiotherapy clinic; book through our app.') == 'clinic', 'a word for an app without a price by the month does not turn a clinic into software'
    assert k('Casa Olmo is a rice restaurant in Ruzafa.') == 'restaurant'


def test_a_one_page_sites_menu_stands_with_its_links_to_parts_of_the_page():
    """the menu of a one-page site leads to its own sections; it used to be left out and the header stood empty with no
    call (the owner, 2026-11-22)"""
    home = 'https://flow.example/'
    labs = ['5 Modules', '50 Features', 'Pricing', 'Book a call']
    inv = {'url': home, 'title': 'Flow — front desk', 'lang': 'en', 'copy': {'text': ' '.join(labs) + ' Stop losing clients', 'headings': [{'tag': 'H1', 'text': 'Stop losing clients'}]},
           'actions': [{'text': 'Skip to main content', 'href': home + '#main'}] + [{'text': t, 'href': home + '#' + t.split()[-1].lower()} for t in labs],
           'brand': {'nav': labs}, 'sourceCoverage': {'sections': []}, 'sourcePages': []}
    seed = {'inventory': inv, 'geometry': {'nav': {'rect': {'y': 0, 'h': 70}, 'links': 4}, 'ctas': [{'text': 'Book a call', 'rect': {'y': 20}}]}, 'assets': {}, 'images': []}
    d = A.adapt(seed)
    assert [n['t'] for n in d['nav']] == ['5 Modules', '50 Features', 'Pricing'] and d['cta']['t'] == 'Book a call' and d['cta']['h'] == home + '#call'
    assert all(n['h'].startswith(home + '#') for n in d['nav']) and not any('Skip' in n['t'] for n in d['nav'])
    assert any(r.startswith('nav:') and 'lead to parts of the client' in r for r in d['_adapter']['rules'])
