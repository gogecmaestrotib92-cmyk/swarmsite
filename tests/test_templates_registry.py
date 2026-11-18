"""The template library: every registered template renders every fixture client (a dark product with phone
screens and a film, a light product with book covers, a restaurant with five photographs, and one made-up client each
for a works, a charity, a person and a shop, plus whatever other niches add) to one whole page with one
h1, nothing reading None/undefined, in under 50 ms, as a pure function — and the media prefix is a parameter whose
default is the template's own output.

The fixture clients are made up: invented names and words, in the shapes of the real test clients. The real ones
(third parties' own text) stay out of git, like bench/seed; where the research folder is on the machine they are
rendered too, and the test is skipped elsewhere."""
import copy
import html
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / 'tests' / 'fixtures' / 'templates'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load('swarmsite_templates_registry', ROOT / 'lib' / 'templates' / 'registry.py')
CLIENTS = {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in sorted(FIX.glob('*.json'))}
SLUGS = R.slugs()


def test_the_library_holds_the_first_two_templates_and_the_fixture_clients():
    assert {'griffin', 'maze'} <= set(SLUGS)
    assert {'tallyfern', 'quillmoor', 'casaolmo', 'larchwick', 'fernhollow', 'pellbrook', 'wendholm', 'svetlinka', 'pellworth', 'lindenrow', 'marenoakhurst', 'hartwell'} <= set(CLIENTS), 'each niche the library serves has a fixture client'
    assert all('made-up client' in d['_note'] for d in CLIENTS.values())
    for t in R.list_templates():
        assert (ROOT / 'lib' / 'templates' / t['slug'] / 'NOTES.md').is_file(), t['slug']
        assert t['selectable'] == t['has_needs'] and (t['selectable'] or 'needs.json' in t['why'])


@pytest.mark.parametrize('slug', SLUGS)
def test_every_template_holds_what_the_library_asks(slug):
    assert R.audit(slug, CLIENTS) == []


@pytest.mark.parametrize('slug', SLUGS)
@pytest.mark.parametrize('client', sorted(CLIENTS))
def test_one_h1_no_none_and_the_clients_own_words(slug, client):
    d = CLIENTS[client]
    page = R.render(slug, d)
    assert len(re.findall(r'<h1[\s>]', page)) == 1
    seen = re.sub(r'<(script|style)\b.*?</\1>', ' ', page, flags=re.S)
    assert not re.search(r'(?<![\w-])(None|undefined|NaN)(?![\w-])', seen)
    assert page.lstrip().lower().startswith('<!doctype html') and '</html>' in page
    assert f'lang="{d["lang"]}"' in page
    tag = re.search(r'<h1.*?</h1>', page, re.S).group(0)
    label = re.match(r'<h1\b[^>]*\baria-label="([^"]*)"', tag)          # a heading set letter by letter is read by its label
    h1 = html.unescape(label.group(1) if label else re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', tag))).strip()
    words = lambda s: re.findall(r'\w+', s.lower())
    title, name, kicker = (words(x or '') for x in (d['hero']['title'], d['brand']['name'], d['hero'].get('kicker')))
    # the first heading is one of the client's own lines, whole: the headline, or — on a page led by its name, as
    # places are — the name; either may carry the kicker after it. Never a cut or a rewording.
    assert words(h1) in (title, title + kicker, name, name + kicker), 'the first heading is the client\'s own, whole'
    if words(h1)[:len(name)] == name and words(h1)[:len(title)] != title:   # led by the name: the headline is still shown, or declared dropped
        seen_text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', seen)))
        assert d['hero']['title'] in seen_text or 'hero.title' in ((R.needs(slug) or {}).get('drops') or []), 'the headline is neither shown nor declared dropped'


@pytest.mark.parametrize('slug', SLUGS)
def test_the_media_prefix_is_a_parameter_and_the_default_is_the_templates_own_page(slug):
    for name, d in CLIENTS.items():
        own = R._page(slug, copy.deepcopy(d))                      # the template's page with what it has no place for under its sections (more.py)
        assert R.render(slug, d) == own and R.render(slug, d, '../../') == own and re.sub(r'<style data-sw-(?:wrap|art)>[^<]*</style>', '', own).startswith(R.load(slug).render(copy.deepcopy(d))[:2000]) and own.count('data-sw-wrap') == 1   # the one line the registry sets first in <head>: a headline's lines of a like length
        paths = R.media_paths(d)
        used = R.media_used(slug, d)
        assert set(used) <= set(paths)
        for base in ('', 'media-root/', 'https://preview.example/jobs/1/'):
            page = R.render(slug, d, base)
            for p in used:
                assert '../../' + p not in page and base + p in page, (name, base, p)
            assert '../../' not in re.sub(r'<(script|style)\b.*?</\1>', ' ', page, flags=re.S), (name, base)
            assert len(page) == len(own) + len(re.findall('|'.join(re.escape('../../' + p) + r'(?![\w./-])' for p in used) or r'(?!)', own)) * (len(base) - 6) if used else page == own


def test_media_paths_are_only_the_local_files_the_data_names():
    d = CLIENTS['tallyfern']
    paths = R.media_paths(d)
    assert 'media/tallyfern/logo.svg' in paths and 'media/tallyfern/tour.mp4' in paths and 'media/tallyfern/tour-poster.jpg' in paths
    assert not [p for p in paths if p.startswith('http')] and len(paths) == len(set(paths))
    assert R.media_paths({'brand': {'logo': None, 'home': 'https://x.example/a.png'}, 'media': {'photos': [{'src': 'data:image/png;base64,AAAA'}, {'src': '//cdn.example/p.jpg'}]}}) == []
    # a file name with a space is still a file; a sentence that ends in '.jpg' is not
    assert R.media_paths({'steps': {'items': [{'img': 'media/a/my photo.jpg', 'text': 'We send it as a file called cover.jpg'}]}}) == ['media/a/my photo.jpg']
    assert R.rebase('<img src="../../media/a/my photo.jpg">', {'media': {'photos': [{'src': 'media/a/my photo.jpg'}]}}, '')[0] == '<img src="media/a/my photo.jpg">'
    # a path that is the beginning of another is not confused with it
    page, used = R.rebase('<img src="../../media/a/img1.jpg"><img src="../../media/a/img1.jpg.webp"><img src="../../media/a/img10.jpg">',
                          {'media': {'photos': [{'src': 'media/a/img1.jpg'}, {'src': 'media/a/img10.jpg'}]}}, 'm/')
    assert page == '<img src="m/media/a/img1.jpg"><img src="../../media/a/img1.jpg.webp"><img src="m/media/a/img10.jpg">' and used == ['media/a/img1.jpg', 'media/a/img10.jpg']


def test_a_section_without_data_is_left_out_and_a_bare_client_still_renders():
    bare = {'brand': {'name': 'Acme'}, 'lang': 'en', 'hero': {'title': 'One plain sentence'}}
    for slug in SLUGS:
        assert R.audit(slug, {'bare': bare, 'empty-lists': {**bare, 'figures': [], 'faq': {'title': '', 'items': []}, 'plans': {'items': []},
                                                             'media': {'screens': [], 'phones': [], 'photos': [], 'video': None}}}) == []
        full, thin = R.render(slug, CLIENTS['tallyfern']), R.render(slug, {k: v for k, v in CLIENTS['tallyfern'].items() if k not in ('plans', 'faq')})
        drops = (R.needs(slug) or {}).get('drops') or []
        for block, said in (('plans', 'Go Row'), ('faq', 'Is Tallyfern an accounting package?')):
            assert said not in thin, (slug, said)
            assert (said in full) == (block not in drops), (slug, block, 'shown although its needs.json drops it' if said in full else 'not shown and not declared in drops')


def test_slugs_cannot_leave_the_library(tmp_path):
    for bad in ('../render', 'griffin/../maze', '', 'Griffin', 'a b', None, '.hidden'):
        with pytest.raises(R.TemplateError):
            R.render(bad, CLIENTS['tallyfern'])
    with pytest.raises(R.TemplateError):
        R.render('nosuchtemplate', CLIENTS['tallyfern'])
    with pytest.raises(R.TemplateError):
        R.render('griffin', ['not', 'a', 'dict'])


def test_audit_refuses_a_template_that_reaches_outside_or_breaks_a_promise(tmp_path):
    def make(slug, body):
        (tmp_path / slug).mkdir()
        (tmp_path / slug / 'render.py').write_text(body, encoding='utf-8')
    page = "'<!doctype html><html><body><h1>' + d['hero']['title'] + '</h1>%s</body></html>'"
    make('good', 'def render(d):\n    return ' + page % '')
    make('calls', 'import urllib.request\ndef render(d):\n    return ' + page % '')
    make('twoh1', 'def render(d):\n    return ' + page % '<h1>again</h1>')
    make('none', 'def render(d):\n    return ' + (page % "<p>' + str(d.get('nothing')) + '</p>"))
    make('chance', 'import random\ndef render(d):\n    return ' + (page % "<i>' + str(random.random()) + '</i>"))
    make('writes', 'def render(d):\n    d["x"] = 1\n    return ' + page % '')
    make('stuck', 'def render(d):\n    return ' + (page % '<img src="../../elsewhere/pic.jpg">'))
    make('broken', 'def render(d:\n')
    c = {'c': {'hero': {'title': 'T'}}}
    assert R.slugs(tmp_path) == sorted(['good', 'calls', 'twoh1', 'none', 'chance', 'writes', 'stuck', 'broken'])
    assert R.audit('good', c, root=tmp_path) == []
    assert any('urllib' in b for b in R.audit('calls', c, root=tmp_path))
    assert any('2 h1' in b for b in R.audit('twoh1', c, root=tmp_path))
    assert any("'None'" in b for b in R.audit('none', c, root=tmp_path))
    assert any('random' in b for b in R.audit('chance', c, root=tmp_path)) and any('differ' in b for b in R.audit('chance', c, root=tmp_path))
    assert any('changed the data' in b for b in R.audit('writes', c, root=tmp_path))
    assert any('outside the data' in b for b in R.audit('stuck', c, root=tmp_path))
    assert len(R.audit('broken', c, root=tmp_path)) == 1 and 'cannot be read' in R.audit('broken', c, root=tmp_path)[0]


def test_the_import_script_copies_a_template_unchanged_and_refuses_a_bad_one(tmp_path):
    imp = _load('swarmsite_import_template', ROOT / 'scripts' / 'import_template.py')
    src = tmp_path / 'research'
    for slug, extra in (('fine', ''), ('bad', '<h1>two</h1>')):
        (src / slug / 'out').mkdir(parents=True)
        (src / slug / 'render.py').write_text("def render(d):\n    return '<!doctype html><html><body><h1>' + d['hero']['title'] + '</h1>%s</body></html>'\n" % extra, encoding='utf-8')
        (src / slug / 'NOTES.md').write_text('# notes\n', encoding='utf-8')
        (src / slug / 'out' / 'client.html').write_text('reference imagery lives here', encoding='utf-8')
    (src / 'fine' / 'needs.json').write_text('{"niche": ["saas"]}', encoding='utf-8')
    lib = tmp_path / 'lib'
    lib.mkdir()
    imp.LIB = lib
    real_audit = R.audit
    R.audit = lambda slug, clients, root=None, limit_ms=50.0: real_audit(slug, clients, root=lib, limit_ms=limit_ms)
    real_needs = R.needs
    R.needs = lambda slug, root=None: real_needs(slug, root=lib)
    try:
        ok, lines = imp.bring('fine', src, R)
        assert ok, lines
        assert sorted(p.name for p in (lib / 'fine').iterdir()) == ['NOTES.md', 'needs.json', 'render.py']
        assert (lib / 'fine' / 'render.py').read_bytes() == (src / 'fine' / 'render.py').read_bytes()
        ok, lines = imp.bring('bad', src, R)
        assert not ok and any('h1' in ln for ln in lines) and not (lib / 'bad').exists()
        (src / 'bad' / 'render.py').write_text('def render(d:\n', encoding='utf-8')
        ok, lines = imp.bring('bad', src, R)
        assert not ok and any('cannot be read' in ln for ln in lines) and not (lib / 'bad').exists(), 'a file that does not parse is refused, and nothing of it stays'
        ok, lines = imp.bring('fine', src, R)
        assert not ok and '--force' in lines[0]
        ok, lines = imp.bring('../fine', src, R)
        assert not ok
    finally:
        R.audit, R.needs = real_audit, real_needs


def test_the_real_test_clients_render_where_the_research_folder_is_here():
    """The hand-made data of the real test clients is not in git. On a machine that has it, every template holds
    with each of them as it does with the made-up ones."""
    imp = _load('swarmsite_import_template', ROOT / 'scripts' / 'import_template.py')
    try:
        src = imp.source()
    except SystemExit:
        pytest.skip('research folder not on this machine')
    real = {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in sorted((src / 'data').glob('*.json'))}
    if not real:
        pytest.skip('no client data in the research folder')
    for slug in SLUGS:
        assert R.audit(slug, real) == [], slug


def test_the_two_templates_are_the_measured_ones_unchanged_when_the_research_folder_is_here():
    """Where the research folder is present (the owner's machine), the library's copy is byte-identical to it or the
    difference is known: this test names a template that drifted. Skipped elsewhere."""
    imp = _load('swarmsite_import_template', ROOT / 'scripts' / 'import_template.py')
    try:
        src = imp.source()
    except SystemExit:
        pytest.skip('research folder not on this machine')
    drift = [s for s in ('griffin', 'maze') if (src / s / 'render.py').is_file() and (src / s / 'render.py').read_bytes() != (ROOT / 'lib' / 'templates' / s / 'render.py').read_bytes()]
    if drift:
        pytest.skip('the research copy has moved on since import: ' + ', '.join(drift) + ' — re-import with scripts/import_template.py --force')


def test_a_library_picture_is_set_in_the_clients_own_accent_and_left_alone_when_it_already_is():
    """pictures.tint: the prepared picture is turned toward the client's accent (at most 30° of hue) and its saturation
    raised to the accent's; nothing for a grey or missing accent, another colour family, or a palette of that colour"""
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location('pics_tint', Path(__file__).resolve().parents[1] / 'lib' / 'templates' / 'pictures.py')
    P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
    pals = {'oxblood': {'name': 'oxblood', 'ground': '#1c0a0c', 'accent': '#d05a56'}, 'sand-peach': {'name': 'sand-peach', 'ground': '#f8ebdd', 'accent': '#e8734a'}}
    assert P.tint('#ff4a1f', 'oxblood', pals) == 'saturate(1.72) hue-rotate(10deg) brightness(1.08)'
    for accent, pal in (('#2f6fe4', 'oxblood'), ('#888888', 'oxblood'), (None, 'oxblood'), ('#ff4a1f', 'none-such'), ('#e8734a', 'sand-peach'), ('#d05a56', 'oxblood')):
        assert P.tint(accent, pal, pals) == '', (accent, pal)
    assert 'brightness' not in P.tint('#ff3b00', 'sand-peach', pals) and P.tint('#ff3b00', 'sand-peach', pals).startswith('saturate(')


def test_a_device_frame_is_drawn_round_a_picture_never_by_changing_its_box():
    """a border on a picture changes the box the gate measures against the picture's own proportions: fluently's framed
    phone was read as distorted and the design held back on production (2026-11-15). The frame is rings of shadow."""
    from pathlib import Path
    src = (Path(__file__).resolve().parents[1] / 'lib' / 'templates' / 'fluently' / 'render.py').read_text(encoding='utf-8')
    rule = re.search(r'\.wk-f\.phone img\{([^}]*)\}', src).group(1)
    assert 'border:' not in rule and 'padding' not in rule and 'box-shadow:0 0 0 10px' in rule, rule



def test_the_openings_picture_is_never_what_one_screen_has_left_after_the_words():
    """The owner's test on a real client, on his phone (2026-11-18): the opening is one screen high and its picture took
    what was left after a four-line headline — 80 px on a browser 600 px high, a phone drawn 40 px wide. The picture
    has a least height, never more than it stands at the full width (its own proportion, --r), and the opening grows
    past one screen to keep it; the gate reads product screens on a short phone screen too (`tiny`)."""
    src = (Path(__file__).resolve().parents[1] / 'lib' / 'templates' / 'fluently' / 'render.py').read_text(encoding='utf-8')
    assert re.search(r'figure\.shot\{flex:1 0 min\(var\(--sh,340px\),calc\(\(100vw - 48px\)/var\(--r,1\.6\)\)\)', src)
    assert re.search(r'\.hero\{position:relative;min-height:max\(620px,100vh\)', src) and not re.search(r'\.hero\{[^}]*[;{]height:', src)
    d = copy.deepcopy(CLIENTS['tallyfern'])
    d.setdefault('media', {})['phones'] = [{'src': 'media/phone-1.jpg', 'w': 780, 'h': 1616, 'alt': 'app'}]
    assert re.search(r'<figure class="shot tall" style="--r:0\.483">', R.render('fluently', d))
    gate = (ROOT / 'lib' / 'qa' / 'template_gate.mjs').read_text()
    assert 'tiny: []' in gate and "n + '-short'" in gate and 'SHORT = 600' in gate


def test_on_a_phone_a_desk_screen_gives_way_to_the_phone_capture_of_the_same_page():
    """Measured on the seventeen software designs (2026-11-18): at 390 every desk screen stood at 9–25 % of its size,
    whatever its frame — letters 3 px high. Where the data has the phone capture of the same page (`page`), the desk
    screen's <img> stands in a <picture> whose source up to NARROW px is that capture (no script), drawn whole and
    upright; a screen with no such capture is left as it is; a design can say `fit` or `no` on the <img>; the phone
    file is among the media the page asks for, at any media base; the same data gives the same bytes."""
    d = copy.deepcopy(CLIENTS['tallyfern'])
    md = d.setdefault('media', {})
    scr = md.get('screens') or []
    assert len(scr) >= 2
    scr[0] = {**scr[0], 'w': 1800, 'h': 1125, 'page': '/picks'}
    scr[1] = {**scr[1], 'w': 1800, 'h': 1125, 'page': '/models'}
    md['phones'] = [{'src': 'media/phone-9.jpg', 'w': 780, 'h': 1616, 'alt': 'app', 'page': '/picks'}]
    first, second = scr[0]['src'], scr[1]['src']
    ran = 0
    for slug in SLUGS:
        page = R.render(slug, copy.deepcopy(d))
        assert page == R.render(slug, copy.deepcopy(d))
        for m in re.finditer(r'<picture class="sw-ph( fit)?" style="--ph:780/1616"><source media="\(max-width:720px\)" srcset="([^"]+)" width="780" height="1616">(<img[^>]*>)</picture>', page):
            assert m.group(2).endswith('media/phone-9.jpg') and first in m.group(3) and second not in m.group(3) and 'data-sw-ph="no"' not in m.group(3)
            ran += 1
        assert '<picture class="sw-ph' not in page or ('<style data-sw-ph>' in page and 'media/phone-9.jpg' in R.media_used(slug, d))
        assert not re.search(r'<picture class="sw-ph[^>]*>(?:(?!</picture>).)*<picture', page, re.S), 'never a picture inside a picture'
        based = R.render(slug, copy.deepcopy(d), media_base='https://cdn.example/x/')
        assert '<picture class="sw-ph' not in based or 'srcset="https://cdn.example/x/media/phone-9.jpg"' in based
    assert ran >= 5, ran
    md['phones'][0].pop('page')
    assert all('<picture class="sw-ph' not in R.render(slug, copy.deepcopy(d)) for slug in SLUGS), 'no capture of the same page: nothing changes'
    assert R.NARROW == 720 and 'display:contents' in R.PHONE_CSS and 'picture.sw-ph.fit>img{max-height:100%!important}' in R.PHONE_CSS


def _clicky():
    spec = importlib.util.spec_from_file_location('clicky_render', ROOT / 'lib' / 'templates' / 'clicky' / 'render.py')
    R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
    return R


def test_wide_screens_alone_leave_the_upright_windows_of_the_opening_empty():
    """Courtsensei on production, beside the reference (2026-11-15): six wide screens of one interface stood in five
    wide windows and read as five thumbnails of the same thing; an upright window on a wide screen (the remedy then)
    cut the screen in half, which the owner called ugly on a real client (2026-11-18). An upright slot with only wide
    screens left now stays empty: three wide windows, each showing its screen whole. A title of 26 letters stands at 72."""
    R = _clicky()
    scr = [{'src': 'media/screen-%d.jpg' % i, 'w': 1800, 'h': 1125, 'alt': 'S%d' % i} for i in range(1, 7)]
    big, wins = R.hero_media({'media': {'screens': scr, 'phones': [], 'photos': []}})
    assert big and len(wins) == 3 and all(w[1] >= 160 for w in wins), [w[1] for w in wins]
    assert all(w[4] and w[4][1] == 'width:100%;left:0;top:0' for w in wins), 'each window shows its screen whole'
    mixed = R.hero_media({'media': {'screens': scr, 'phones': [{'src': 'media/phone-%d.jpg' % i, 'w': 780, 'h': 1616} for i in (1, 2)], 'photos': []}})[1]
    assert len(mixed) == 5 and sum(1 for w in mixed if w[1] < 160) == 2, 'phones take the upright windows'
    page = R.s_hero({'hero': {'title': 'Your team. Your game plan.'}, 'media': {'screens': scr, 'phones': [], 'photos': []}}, {})
    assert page.count('class="scr dt"') == 3 and '--fs:72' in page
    ph = [{'src': 'media/photo-%d.jpg' % i, 'w': 1800, 'h': 1125, 'alt': ''} for i in range(1, 7)]
    assert not any(w[4] for w in R.hero_media({'media': {'screens': [], 'phones': [], 'photos': ph}})[1])


def test_a_screen_in_a_small_window_stands_whole_in_a_window_of_its_own_shape():
    """A product's screen in a window was shown enlarged and cut to its busiest part (2026-11-15); the owner, on a real
    client, called the cut screens ugly (2026-11-18). A window now takes the screen's own proportion and shows it
    whole: its width is the window's, nothing is moved, nothing is cut."""
    R = _clicky()
    m = {'src': 'media/tab1.jpg', 'w': 767, 'h': 533, 'alt': 'S', 'detail': [[1] * 32 for _ in range(22)]}
    box, img = R.detail(m, 172, 110, 767)
    assert box == 'aspect-ratio:172/120' and img == 'width:100%;left:0;top:0'
    box, img = R.detail({'src': 'media/phone-1.jpg', 'w': 780, 'h': 1616}, 137, 300, 390)
    assert box == 'aspect-ratio:137/284' and 'width:100%' in img
    assert R.busiest(None, .3, .3, [.156, .156])[0] == .5                 # no map: the middle past the flat margin
    css = (ROOT / 'lib' / 'templates' / 'clicky' / 'render.py').read_text()
    assert re.search(r'\.scr\.dt img\{[^}]*position:absolute[^}]*height:auto', css)


def test_every_page_lists_its_product_screens_and_never_crops_one_by_script():
    """A product's screen stands whole in its frame. From 2026-11-15 to 2026-11-18 the registry added lines that drew a
    screen larger inside a small box and cropped it (object-fit: none) so its letters would read; on a real client every
    such frame held half a headline (the owner, on his phone, 2026-11-18). The page now only lists its screens with the
    width each was drawn in, for the gate's `sliced`; a page without a screen is unchanged; the same data gives the
    same bytes."""
    ran = 0
    for slug in SLUGS:
        d = copy.deepcopy(CLIENTS['tallyfern'])
        md = d.setdefault('media', {})
        scr = md.get('screens') or []
        if not scr:
            continue
        scr[0] = {**scr[0], 'w': 1800}
        md['phones'] = [{'src': 'media/phone-1.jpg', 'w': 780, 'h': 1616, 'alt': 'app'}]
        page = R.render(slug, d)
        assert page == R.render(slug, copy.deepcopy(d))
        blob = re.search(r'<script type="application/json" id="sw-detail">(.*?)</script>', page, re.S)
        assert blob, slug
        maps = json.loads(blob.group(1))
        assert maps[scr[0]['src'].rsplit('/', 1)[-1]] == {'c': 1440} and maps['phone-1.jpg'] == {'c': 390}
        assert 'objectFit' not in page and 'data-sw-detail' not in page and page.index('id="sw-detail"') < page.rindex('</body>'), slug
        ran += 1
    assert ran == len(SLUGS)
    bare = copy.deepcopy(CLIENTS['tallyfern'])
    bare['media'] = {k: v for k, v in (bare.get('media') or {}).items() if k not in ('screens', 'phones')}
    assert 'id="sw-detail"' not in R.render(SLUGS[0], bare)
    gate = (ROOT / 'lib' / 'qa' / 'template_gate.mjs').read_text()
    assert 'sliced: []' in gate and re.search(r'const SIDES = \.97', gate) and re.search(r'SMALL = \.4\b', gate) and not hasattr(R, 'READABLE')


def test_a_small_window_shows_the_product_not_the_apps_own_menu_or_a_bar_of_controls():
    """The owner's review of a court-sports app (2026-11-16): the part with most detail was the app's side menu with
    one loud button, or a bar of filters. Where three screens or more of one product share a frame (the same columns
    and rows at their edges), the frame is taken out of each screen's map before any template reads it; the part
    chosen is the one most evenly full whose edge cuts least; the caller's data is not changed, and one or two
    screens are left as they are, and of screens that are all alike no more than the edges are taken."""
    def screen(k):
        g = [[0] * 32 for _ in range(22)]
        for r in range(22):
            for c in range(6):
                g[r][c] = 30 if r % 2 else 12                         # the side menu: the same on every screen
        for c in range(6, 32):
            g[0][c] = 25                                              # the top bar
        g[19][2] = 99                                                 # its one loud button
        for r in range(4 + k, 12 + k):
            for c in range(10 + k, 24 + k):
                g[r][c] = 18 + (r + c + k) % 9                        # the screen's own content, different on each
        return g
    grids = [screen(k) for k in range(4)]
    boxes = R._frame(grids)
    assert all(b and b[0] == 6 and b[1] >= 1 for b in boxes), boxes
    d = {'media': {'screens': [{'src': 'media/tab%d.jpg' % i, 'w': 767, 'h': 533, 'detail': g} for i, g in enumerate(grids)]}}
    before = copy.deepcopy(d)
    out = R._subject(d)
    assert d == before and out is not d
    g0 = out['media']['screens'][0]['detail']
    assert all(g0[r][c] == 0 for r in range(22) for c in range(6)) and g0[0][20] == 0 and g0[6][14] == grids[0][6][14]
    C = _clicky()
    fx, fy = C.busiest(g0, .3, .3)
    assert .3 < fx < .8 and .15 < fy < .6, (fx, fy)                   # with the frame out: the content
    two = {'media': {'screens': d['media']['screens'][:2]}}
    assert R._subject(two) is two
    alike = {'media': {'screens': [{'src': 'a%d.jpg' % i, 'w': 767, 'h': 533, 'detail': grids[0]} for i in range(3)]}}
    ga = R._subject(alike)['media']['screens'][0]['detail']          # screens all alike: never more than the edges go
    assert ga[10][16] == grids[0][10][16] and sum(1 for r in ga if any(r)) * 2 >= 8
    # a list beside a louder bar of controls: the evenly full part wins, and its edge does not run through the bar
    g = [[0] * 32 for _ in range(22)]
    for c in range(8, 20):
        g[3][c] = 95
    for r in range(8, 15):
        for c in range(8, 18):
            g[r][c] = 22
    assert C.busiest(g, .32, .3)[1] > .4
    loud = [[0] * 32 for _ in range(22)]
    loud[10][20] = loud[10][21] = 99
    assert abs(C.busiest(loud, .05, .05)[0] - 20.5 / 32) < .04            # a part one cell high: never an empty one for a loud one
    assert R.CAP == C.CAP and R.RING == C.RING


def test_the_windows_opening_keeps_the_clients_own_small_things_between_its_windows():
    """Beside the reference (2026-11-16): its desktop has small things between the windows, ours had none. Ours are
    the client's own in the reference's places — a folder for each of the first two links of the menu (the link
    itself), the mark as an app's icon, a tag for a figure and for a plan's price — and one with nothing of the
    client's for it is not drawn; none lies on the headline's column, none is more than a fifth under a window."""
    R = _clicky()
    scr = [{'src': 'media/screen-%d.jpg' % i, 'w': 1800, 'h': 1125, 'alt': 'S%d' % i} for i in range(1, 7)]
    base = {'hero': {'title': 'Your team. Your game plan.'}, 'media': {'screens': scr, 'phones': [], 'photos': []}}
    c = R.colours({'ground': '#14120f', 'ink': '#f7dbba', 'accent': '#ff4a1f'})
    assert 'class="ob ' not in R.s_hero(base, c)                      # nothing of the client's: nothing drawn
    full = dict(base, brand={'name': 'N', 'logo': 'media/logo.svg'},
                nav=[{'t': 'Blog', 'h': '/blog'}, {'t': 'A name far too long for a folder', 'h': '/x'}, {'t': 'Pricing', 'h': '/pricing'}, {'t': 'Docs', 'h': '/docs'}],
                figures=[{'v': '42%', 'l': 'Hit rate'}, {'v': 'many', 'l': 'teams'}, {'v': '1.80', 'l': 'Avg odds'}],
                plans={'items': [{'name': 'Pro', 'price': '€69'}, {'name': 'Free', 'price': 'Free'}]})
    page = R.s_hero(full, c)
    assert re.findall(r'class="ob od"[^>]*href="([^"]+)"', page) == ['/blog', '/pricing']
    assert page.count('class="ob oi"') == 1 and 'media/logo.svg' in page
    assert re.findall(r'<b>([^<]+)</b><span>([^<]+)</span>', page) == [('Hit rate', '42%'), ('Pro', '€69')]   # one of each; no tag without a number
    assert 'class="ob oi"' not in R.s_hero(dict(full, brand={'name': 'N', 'logo': 'media/logo.svg', 'logo_wordmark': True}), c)
    # places: clear of the headline's column; a thing a window would cover is left out
    _, wins = R.hero_media(full)
    boxes = [w[5] for w in wins]
    for kind, anchor, off, top, w, h, turn in R.THINGS:
        x = {'c': 720 + off, 'l': off, 'r': 1440 - off - w}[anchor]
        assert not R._over((x, top, w, h), R.HEAD), kind
    wide = [(dict(scr[0]), 300, '', 200, None, (250, 200, 300, 200))]   # a window lying where the left folder stands
    left = R.things(full, c, wide)                                      # … leaves one folder's place: the first link takes it
    assert left.count('class="ob od"') == 1 and 'right:calc' in left.split('class="ob od"')[1][:40] and 'href="/blog"' in left
    assert all(max(R._over((1230, 141, 104, 77), b) for b in boxes) <= .2 for _ in [0])
    src = (ROOT / 'lib' / 'templates' / 'clicky' / 'render.py').read_text()
    assert "$$('.win,.oi,.ot')" in src and '.wins{display:none}' in src      # carried like the windows; none on a phone
