"""Our own landing is built with the engine's devices and keeps their rules — the page that sells the engine is its first client."""
import os, re, sys
ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.join(ROOT, 'lib', 'devices'))
import landing_devices as L
import registry as R

HTML = open(L.PAGE, encoding='utf-8').read()
BODY = HTML.split('<body>', 1)[1].split('<script id="dv-js">', 1)[0]   # the markup alone: no library code, no page script
# how a device shows in markup — the hook its own contract (`markup`) names
HOOK = {'line-rise': 'dv-lines', 'rise-stagger': 'data-rise', 'fact-ticker': 'dv-tick', 'scramble': 'dv-scramble', 'depth': 'dv-depth', 'eased-scroll': 'data-eased-scroll', 'overlay-menu': 'dv-menu-btn',
        'read-along': 'dv-read', 'roll': 'dv-roll', 'progress': 'dv-progress', 'bar-tuck': 'dv-tuck', 'grain': 'dv-grain', 'draw': 'dv-draw', 'cover': 'dv-cover',
        'curtain-foot': 'dv-under', 'magnet': 'dv-magnet'}
text = lambda h: ' '.join(re.sub(r'<[^>]+>', ' ', re.sub(r'<svg.*?</svg>', '', h, flags=re.S)).split())


def test_the_landing_carries_the_librarys_code_and_not_a_copy_gone_stale():
    assert L.filled(HTML) == HTML, 'web/index.html differs from lib/devices/registry.py — run python3 scripts/landing_devices.py'


def test_every_device_it_names_is_used_and_every_device_it_uses_is_named():
    named = L.devices(HTML)
    assert sorted(named) == sorted(HOOK), 'a device was added or dropped: give it its hook in this test'
    for i in named: assert HOOK[i] in HTML.split('<script id="dv-js">', 1)[0].replace(R.bundle(named)[0], ''), f'{i} is named and never used'
    for hook in set(re.findall(r'\bdv-[a-z]+(?:-[a-z]+)?\b', BODY)) - {'dv-ln', 'dv-menu', 'dv-sheet', 'dv-js', 'dv-css'}:   # parts of a device named by its main hook: a row of a headline, the menu of its button, the sheet of a curtain footer, the phone of `frame`
        assert hook in HOOK.values(), f'the markup uses {hook}, whose device the page does not name'


def test_no_motion_library_is_loaded_beside_the_devices():
    """The devices are our own code so that a generated page owes nothing to a library's terms; the landing shows the same."""
    assert not re.search(r'gsap|ScrollTrigger|lenis|moves\.js', HTML)


def test_it_keeps_the_rules_each_device_states():
    assert len(re.findall(r'<h1\b', BODY)) == 1
    assert 1 <= BODY.count('dv-lines') <= 3, 'line-rise: the first screen and one or two statements, not more than three times a page'
    labels = [text(m) for m in re.findall(r'<span class="dv-scramble">(.*?)</span>', BODY)]
    assert 2 <= len(labels) <= 5 and all(len(l) <= 24 for l in labels), f'scramble: two to five labels of at most 24 characters: {labels}'
    ticks = re.findall(r'class="dv-tick[^"]*"><ul>(.*?)</ul>', BODY, re.S); facts = [text(f) for f in re.findall(r'<li>(.*?)</li>', ticks[0])] if ticks else []
    assert len(ticks) == 1 and 4 <= len(facts) <= 8 and all(len(f) < 40 for f in facts), f'fact-ticker: once, four to eight facts under 40 characters: {facts}'
    read = re.findall(r'<p class="[^"]*\bdv-read\b[^"]*">(.*?)</p>', BODY, re.S)
    assert len(read) == 1 and 20 <= len(text(read[0]).split()) <= 60, 'read-along: one paragraph of 20–60 words, once'
    assert 1 <= BODY.count('dv-draw') <= 2 and BODY.count('dv-magnet') <= 2 and BODY.count('dv-cover') <= 2
    assert BODY.count('class="dv-progress"') == 1 and BODY.count('class="dv-grain"') == 1 and '<main id="main" class="dv-sheet">' in BODY


def test_every_picture_says_its_size_so_nothing_jumps_when_it_arrives():
    for img in re.findall(r'<img\b[^>]*>', BODY): assert re.search(r'\bwidth="\d+"', img) and re.search(r'\bheight="\d+"', img), img


def test_the_facts_it_states_are_the_engines_own():
    """What the ticker claims is read off the code that does it, so the page cannot go on saying it after the engine stops."""
    layout = open(os.path.join(ROOT, 'lib', 'qa', 'layout.mjs'), encoding='utf-8').read()
    assert "'390,768,1100,1440,1920'" in layout and 'Checked at five screen widths' in BODY
    studio = open(os.path.join(ROOT, 'lib', 'studio', 'studio.py'), encoding='utf-8').read()
    assert re.search(r"if '--variants' in args else 3\b", studio) and 'Up to three designs to compare' in BODY   # the number a job composes when it is not told otherwise — the code, not its usage line
    assert 'prefers-reduced-motion:reduce' in R.BASE_CSS and 'Reduced motion respected' in BODY
    sys.path.insert(0, os.path.join(ROOT, 'lib', 'studio')); import scenes
    assert scenes.TYPE and all(t.get('gf') for t in scenes.TYPE.values()) and 'Open-licence typefaces' in BODY   # every type system is set in faces served by Google Fonts, which carries open licences only
