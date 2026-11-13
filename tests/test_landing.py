"""Our own landing is built the way a client's page is now built: on a template of the library (its measured build:
web/css/site.css + web/css/landing.css + web/js/landing.js), with our words swapped in (owner, 2026-11-12). It states
only what the engine does, offers the three ways in, and never names the reference a template was rebuilt from.
(Before 2026-11-12 the landing carried the old engine's devices, lib/devices/registry.py; that test is retired with them.)"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), '..')
WEB = os.path.join(ROOT, 'web')
read = lambda *p: open(os.path.join(ROOT, *p), encoding='utf-8').read()
HTML = read('web', 'index.html')
BODY = HTML.split('<body>', 1)[1]
text = lambda h: ' '.join(re.sub(r'<[^>]+>', ' ', re.sub(r'<(svg|script|style)\b.*?</\1>', '', h, flags=re.S)).split())
WORDS = text(BODY)


def test_one_h1_and_every_picture_says_its_size():
    assert len(re.findall(r'<h1\b', BODY)) == 1
    for img in re.findall(r'<img\b[^>]*>', BODY):
        assert re.search(r'\bwidth="\d+"', img) and re.search(r'\bheight="\d+"', img), img


def test_it_is_the_templates_build_and_no_motion_library():
    assert '/css/site.css' in HTML and '/css/landing.css' in HTML and '/js/landing.js' in HTML
    assert not re.search(r'gsap|ScrollTrigger|lenis|moves\.js|swarm\.js', HTML)
    fonts = re.search(r'fonts\.googleapis\.com/css2\?([^"]+)', HTML).group(1)
    assert set(re.findall(r'family=([A-Za-z+]+)', fonts)) == {'EB+Garamond', 'Figtree', 'Shrikhand'}, 'open-licence faces only (all three SIL OFL)'


def test_the_three_ways_in_and_the_address_field_come_first():
    first = BODY.index('id="url"')
    assert BODY.index('<form') < BODY.index('</section>'), 'the address field is in the opening'
    ways = re.findall(r'data-way="(\w+)"[^>]*>([^<]+)<', BODY)
    assert ways == [('site', 'I have a site'), ('app', 'I built a first version of my app'), ('none', 'I don’t have a site')]
    assert BODY.index('data-way="site"') < first, 'the ways in, then the field'
    for h in ('/start', '/dashboard', '/login', '#faq', '#price', '#how'):
        assert f'href="{h}"' in BODY, h


def test_the_facts_it_states_are_the_engines_own():
    """what the page claims is read off the code that does it"""
    gate = read('lib', 'qa', 'template_gate.mjs')
    assert "['d', 1440, 900], ['m', 390, 844]" in gate and 'Checked on a desk screen and a phone' in WORDS
    assert re.search(r"def build\(job_dir, out, base='', limit=3\b", read('lib', 'templates', 'job.py')) and 'Three designs' in WORDS
    # hosting is not offered yet (owner, 2026-11-13): the offer is three designs, choose, edit, pay once, download. Publishing
    # stays in the server, unreachable from the pages: no page promises an address or says "publish", and the switch is off.
    for f in ('index.html', 'app.html', 'edit.html', 'start.html', 'login.html'):
        seen = text(read('web', f).split('<body>', 1)[1])
        assert not re.search(r'publish|name\.swarmsite\.si|put it online', seen, re.I), f
    assert 'SWARMSITE_PUBLISH' not in read('web', 'config.js') and 'window.SWARMSITE_PUBLISH===true' in read('web', 'edit.html')
    assert 'Download the HTML and CSS' in WORDS and '79 €' in WORDS
    assert 'prefers-reduced-motion:reduce' in read('web', 'css', 'landing.css') and 'Reduced motion respected' in WORDS
    assert re.search(r"SCREENS = 6\b", read('lib', 'templates', 'job.py')) and 'up to six screenshots' in WORDS


def test_it_never_names_a_reference():
    names = [d for d in os.listdir(os.path.join(ROOT, 'lib', 'templates')) if os.path.isdir(os.path.join(ROOT, 'lib', 'templates', d)) and not d.startswith('_')] + ['wisprflow', 'wispr']
    pages = [f for f in os.listdir(WEB) if f.endswith('.html')]
    loaded = {u.split('?')[0].lstrip('/') for p in pages for u in re.findall(r'(?:src|href)="(/[^"]+\.(?:css|js))', read('web', p))}   # what the pages load
    for f in pages + sorted(x for x in loaded if os.path.isfile(os.path.join(WEB, x))):
        src = read('web', f).lower()
        hit = [n for n in names if re.search(r'(?<![a-z0-9])%s(?![a-z0-9])' % re.escape(n), src)]
        assert not hit, f'{f} names {hit}'


def test_the_agents_on_the_stage_act_on_measured_places_of_a_made_up_page():
    """the landing's scene is the product's own agents (web/js/swarm2.js) fed the places measured on the made-up client's
    page — nothing about a real client, every place inside the picture it is drawn on"""
    import json
    assert '/js/swarm2.js' in HTML and 'id="live"' in HTML and 'made-up client' in WORDS
    d = json.loads(read('web', 'visuals', 'ui-page.json'))
    w, h = map(int, re.search(r'ui-page\.webp" width="(\d+)" height="(\d+)"', HTML).groups())
    assert abs(d['pageHeight'] - h * 1440 / w) < 8, 'the picture is the page the places were measured on'
    placed = [e for e in d['events'] if e.get('rect')]
    assert len(placed) >= 10 and all(0 <= e['rect']['x'] and e['rect']['x'] + e['rect']['w'] <= 1440 and e['rect']['y'] + min(e['rect']['h'], 420) <= d['pageHeight'] for e in placed)
    assert {e['role'] for e in d['events']} <= {'Reader', 'Layout', 'Copy', 'Photos', 'Type', 'Colour'}
