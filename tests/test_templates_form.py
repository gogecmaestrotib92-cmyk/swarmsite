"""A site from nothing: the visitor's form and photographs become the same contract data a capture does, and nothing
is written that the visitor did not type. A made-up business throughout."""
import importlib.util
import json
import struct
import sys
import zlib
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


F = _load('swarmsite_templates_form', ROOT / 'lib' / 'templates' / 'form.py')
A = _load('swarmsite_templates_adapt', ROOT / 'lib' / 'templates' / 'adapt.py')
JOB = _load('swarmsite_templates_job', ROOT / 'lib' / 'templates' / 'job.py')
G = _load('swarmsite_templates_gate', ROOT / 'lib' / 'templates' / 'gate.py')


def png(w, h):
    c = lambda k, d: struct.pack('>I', len(d)) + k + d + struct.pack('>I', zlib.crc32(k + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + c(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + c(b'IDAT', zlib.compress((b'\x00' + b'\x80' * 3 * w) * h)) + c(b'IEND', b'')


def jpeg(w, h):
    return b'\xff\xd8\xff\xe0' + struct.pack('>H', 16) + b'JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00' + b'\xff\xc0' + struct.pack('>HBHHB', 17, 8, h, w, 3) + b'\x01\x11\x00\x02\x11\x01\x03\x11\x01' + b'\xff\xd9'


def webp(w, h):
    body = b'VP8X' + struct.pack('<I', 10) + b'\x00\x00\x00\x00' + (w - 1).to_bytes(3, 'little') + (h - 1).to_bytes(3, 'little')
    return b'RIFF' + struct.pack('<I', 4 + len(body)) + b'WEBP' + body


@pytest.fixture
def up(tmp_path):
    d = tmp_path / 'uploads'
    d.mkdir()
    (d / 'a.png').write_bytes(png(1600, 1000))
    (d / 'b.jpg').write_bytes(jpeg(900, 1200))
    (d / 'c.webp').write_bytes(webp(1440, 900))
    (d / 'evil.png').write_bytes(b'<script>not a picture</script>')
    return d


RESTAURANT = {'name': 'Casa Fern', 'sentence': 'Rice dishes cooked over wood, by the river', 'kind': 'restaurant', 'niche': 'family rice restaurant', 'accent': '#b5452a',
              'offers_title': 'Rices', 'offers': [{'name': 'Arroz negro', 'price': '18 €'}, {'name': 'Paella de verduras', 'price': '16 €', 'note': 'for two'}, {'name': ''}],
              'link': {'t': 'Book a table', 'h': 'casafern.example/book'},
              'contact': {'street': 'Calle del Río 4', 'city': 'Valencia', 'phone': '+34 600 111 222', 'email': 'mesa@casafern.example', 'hours': [{'days': 'Tue–Sun', 'open': '13:00', 'close': '23:00'}, {'days': 'Mon'}]},
              'photos': [{'file': 'a.png', 'role': 'dish', 'offer': 0, 'alt': 'Black rice in the pan'}, {'file': 'b.jpg', 'role': 'room'}, {'file': '../a.png', 'role': 'dish'}, {'file': 'evil.png'}]}


def test_the_sizes_of_a_picture_are_read_from_its_bytes():
    assert F.size(png(1600, 1000)) == (1600, 1000) and F.size(jpeg(900, 1200)) == (900, 1200) and F.size(webp(1440, 900)) == (1440, 900)
    assert F.size(b'GIF89a....') is None and F.size(b'') is None


def test_a_restaurant_form_is_a_place_with_its_menu_and_nothing_more(up):
    d, n = F.from_form(RESTAURANT, up)
    assert A.validate(d) == [], A.validate(d)
    assert d['brand'] == {'name': 'Casa Fern', 'logo': None} and d['hero']['title'] == 'Rice dishes cooked over wood, by the river'
    assert d['kind'] == 'restaurant' and d['niche'] == 'family rice restaurant' and d['palette']['accent'] == '#b5452a'
    assert d['hero']['primary'] == {'t': 'Book a table', 'h': 'https://casafern.example/book'} == d['place']['booking']
    assert d['place']['menu']['sections'] == [{'t': 'Rices', 'items': [{'name': 'Arroz negro', 'price': '18 €', 'img': 'media/upload/photo-1.png'}, {'name': 'Paella de verduras', 'price': '16 €', 'note': 'for two'}]}]
    assert d['place']['address'] == {'street': 'Calle del Río 4', 'city': 'Valencia'} and d['place']['phone'] == {'t': '+34 600 111 222', 'h': 'tel:+34600111222'}
    assert d['place']['hours'] == [{'days': 'Tue–Sun', 'open': '13:00', 'close': '23:00'}], 'a half-typed line of hours is left out, never completed'
    assert d['media']['photos'] == [{'src': 'media/upload/photo-1.png', 'w': 1600, 'h': 1000, 'role': 'dish', 'alt': 'Black rice in the pan'}, {'src': 'media/upload/photo-2.jpg', 'w': 900, 'h': 1200, 'role': 'room'}]
    assert n['media'] == {'media/upload/photo-1.png': 'a.png', 'media/upload/photo-2.jpg': 'b.jpg'}, 'a path outside the uploads and a file that is no picture are refused'
    assert any('photo 3' in g for g in n['gaps']) and any('photo 4' in g for g in n['gaps']) and any('"Mon"' in g for g in n['gaps'])
    assert not {'features', 'steps', 'figures', 'plans', 'faq', 'quotes', 'team', 'contact'} & set(d), 'no section the visitor did not fill'


def test_what_they_offer_goes_where_their_kind_of_business_keeps_it(up):
    soft, n = F.from_form({**RESTAURANT, 'kind': 'software', 'photos': [{'file': 'c.webp', 'role': 'screen', 'step': 1}],
                           'steps': [{'title': 'Connect'}, {'title': 'Count', 'text': 'Type the cash once.'}, {'title': ''}], 'figures': [{'v': '1 200', 'l': 'stalls'}, {'l': 'no number'}]}, up)
    assert A.validate(soft) == [] and soft['features']['items'][0] == {'t': 'Arroz negro'} and 'place' not in soft
    assert soft['media'] == {'screens': [{'src': 'media/upload/photo-1.webp', 'w': 1440, 'h': 900}]}, 'a screen of their software is a screen'
    assert soft['steps'] == {'items': [{'title': 'Connect'}, {'title': 'Count', 'text': 'Type the cash once.', 'img': 'media/upload/photo-1.webp'}]}
    assert soft['figures'] == [{'v': '1 200', 'l': 'stalls'}] and any('no number' in g for g in n['gaps'])
    assert soft['contact'] == {'phone': {'t': '+34 600 111 222', 'h': 'tel:+34600111222'}, 'email': 'mesa@casafern.example'} and soft['locations'][0]['address']['city'] == 'Valencia'
    assert any('prices were typed' in g for g in n['gaps']), 'a feature has no price: said, not shown'
    clinic, _ = F.from_form({**RESTAURANT, 'kind': 'clinic'}, up)
    assert A.validate(clinic) == [] and clinic['catalogue'] == {'title': 'Rices', 'groups': [{'items': clinic['catalogue']['groups'][0]['items']}]} and clinic['catalogue']['groups'][0]['items'][0]['price'] == '18 €'


def test_an_empty_field_is_a_section_left_out_and_said_so():
    d, n = F.from_form({'name': '  Ana   Ruiz ', 'kind': 'person', 'contact': {'email': 'not-an-address', 'phone': '12'}, 'link': {'t': 'Write to me'}, 'accent': 'red'})
    assert d == {'brand': {'name': 'Ana Ruiz', 'logo': None}, 'kind': 'person', 'niche': 'person', 'hero': {'title': 'Ana Ruiz'}} and A.validate(d) == []
    for words in ('hero.title', 'offers: none', 'media: no photographs', 'contact.email', 'contact.phone', 'link: a button needs both', 'contact: no way'):
        assert any(g.startswith(words) or words in g for g in n['gaps']), (words, n['gaps'])
    with pytest.raises(ValueError):
        F.from_form({'name': '   ', 'sentence': 'x'})
    d, n = F.from_form({'name': 'X', 'kind': 'spaceship'})
    assert 'kind' not in d and any('not one of the list' in g for g in n['gaps'])


def test_a_link_that_would_run_script_is_never_a_button():
    for h in ('javascript:alert(1)', 'data:text/html,<b>', 'https://a.example/"><script>', 'vbscript:x', 'not a link'):
        d, n = F.from_form({'name': 'X', 'link': {'t': 'Go', 'h': h}})
        assert 'primary' not in d['hero'], h
    assert F.from_form({'name': 'X', 'link': {'t': 'Call', 'h': 'tel:+34600111222'}})[0]['hero']['primary']['h'] == 'tel:+34600111222'


def test_the_job_builds_three_previews_from_a_form_as_from_a_capture(tmp_path, up, monkeypatch):
    monkeypatch.setattr(G, 'check', lambda files, **kw: [{'page': str(f), 'ok': True, 'failed': []} for f in files])
    form = {'name': 'Tallyfern', 'sentence': 'A ledger for market stalls that balances itself at closing time', 'kind': 'software',
            'offers': [{'name': 'Counts the till'}, {'name': 'Closes the day'}], 'steps': [{'title': 'Connect the card reader'}, {'title': 'Close the day'}],
            'figures': [{'v': '1 200', 'l': 'stalls use it'}, {'v': '4 min', 'l': 'to close a day'}], 'photos': [{'file': 'c.webp', 'role': 'screen'}, {'file': 'evil.png'}]}
    out = tmp_path / 'templates'
    r = JOB.build(tmp_path / 'job', out, form=form, photos=up)
    assert 'griffin' in r['shown'] and len(r['shown']) <= 3 and r['media'] == {'written': 1, 'missing': [], 'library': 0}
    assert (out / 'media' / 'upload' / 'photo-1.webp').read_bytes() == (up / 'c.webp').read_bytes()
    data = json.loads((out / 'data.json').read_text())
    assert data['brand']['name'] == 'Tallyfern' and data['media']['screens'][0]['src'] == 'media/upload/photo-1.webp'
    notes = json.loads((out / 'adapter.json').read_text())
    assert notes['source'] == 'form' and any('photo 2' in g for g in notes['gaps'])
    assert 'media/upload/photo-1.webp' in (out / 'griffin.html').read_text() and 'Tallyfern' in (out / 'griffin.html').read_text()


def test_screenshots_kind_and_goal_beside_an_address_are_the_visitors_own(tmp_path, up):
    """'I built a first version of my app': the visitor's screenshots go ahead of whatever the capture found — a tall one
    is a phone — the kind they name is the client's kind, and their words for the button replace the button's text only
    where the site has a button with an address. Nothing else is written."""
    (up / 'tall.png').write_bytes(png(390, 844))
    (up / 'tiny.png').write_bytes(png(120, 80))
    d = {'brand': {'name': 'Tallyfern'}, 'kind': 'service', 'cta': {'t': 'Sign up', 'h': 'https://x.example/up'}, 'hero': {'title': 'T', 'primary': {'t': 'Sign up', 'h': 'https://x.example/up'}},
         'media': {'screens': [{'src': 'media/img-1.png', 'w': 1200, 'h': 800}]}}
    out, notes = JOB.visitor(d, tmp_path / 'out', [up / 'c.webp', up / 'tall.png', up / 'tiny.png', up / 'evil.png'], 'software', '  Start   a free trial ')
    assert [x['src'] for x in out['media']['screens']] == ['media/upload/screen-1.webp', 'media/img-1.png']
    assert out['media']['phones'] == [{'src': 'media/upload/screen-2.png', 'w': 390, 'h': 844, 'alt': 'Tallyfern, screen 2'}]
    assert (tmp_path / 'out' / 'media' / 'upload' / 'screen-1.webp').read_bytes() == (up / 'c.webp').read_bytes()
    assert not (tmp_path / 'out' / 'media' / 'upload' / 'screen-3.png').exists(), 'a picture under 200 px is not a screen'
    assert out['kind'] == 'software' and out['cta']['t'] == 'Start a free trial' and out['hero']['primary']['t'] == 'Start a free trial'
    assert sum('screenshot' in n for n in notes) == 3 and d['kind'] == 'service', 'the data given is not changed in place'
    same, _ = JOB.visitor(d, tmp_path / 'o2', [], 'not-a-kind', '')
    assert same == d, 'an unknown kind and no goal change nothing'
    bare, said = JOB.visitor({'brand': {'name': 'X'}}, tmp_path / 'o3', [], '', 'Book a table')
    assert 'cta' not in bare and any('no button' in n for n in said), 'no button with an address: the goal is noted, never invented into one'
