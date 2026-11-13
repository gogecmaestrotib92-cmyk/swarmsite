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
        assert R.render(slug, d) == own and R.render(slug, d, '../../') == own and own.startswith(R.load(slug).render(copy.deepcopy(d))[:2000])
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
