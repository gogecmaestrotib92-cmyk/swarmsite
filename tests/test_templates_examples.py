"""lib/templates/examples.py: a thin site's design is shown complete — the sections its page lacks are filled with
examples; a site with content of its own is never touched, and neither is a section the client has (owner, 2026-11-25)."""
import copy
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / 'tests' / 'fixtures' / 'templates'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E = _load('swarmsite_templates_examples', ROOT / 'lib' / 'templates' / 'examples.py')
A = _load('swarmsite_templates_adapt_examples', ROOT / 'lib' / 'templates' / 'adapt.py')
THIN = {'brand': {'name': 'Zasox'}, 'lang': 'en', 'kind': 'software', 'niche': 'a personal film library', 'palette': {'ground': '#ffffff', 'ink': '#111111'},
        'hero': {'title': 'Please sign in'}, 'faq': {'items': [{'q': 'Is it free?', 'a': 'Yes.'}, {'q': 'Where?', 'a': 'Online.'}]}, 'media': {}}
RAW = {'lede': 'Your films and series in one place, ready on any screen.',
       'trust': ['No ads', 'Any device', 'Cancel any time'],
       'statement': {'title': 'A library that stays yours', 'text': 'Keep everything you watch in one tidy place. Pick up where you stopped, on the phone or the sofa.'},
       'features': {'title': 'What you get', 'items': [{'t': 'One library', 'd': 'Every film and series in a single list.'}, {'t': 'Any screen', 'd': 'Phone, tablet or television.'},
                                                         {'t': 'Seamless sync', 'd': 'A word a reader knows a machine by.'}, {'t': 'Offline', 'd': 'Download and watch on the train.'}]},
       'steps': {'title': 'Three steps', 'items': [{'title': 'Sign in', 'text': 'Use your email.'}, {'title': 'Add films', 'text': 'Pick from the list.'}, {'title': 'Watch', 'text': 'On any screen.'}]},
       'figures': [{'v': '4K', 'l': 'picture quality'}, {'v': '12 min', 'l': 'to set up'}, {'v': 'far too long a figure', 'l': 'dropped'}],
       'faq': {'items': [{'q': 'New?', 'a': 'This must not replace the client\'s own questions.'}] * 4},
       'quotes': [{'q': 'I finally stopped hunting for where I left off.', 'role': 'Subscriber, film club'}, {'q': 'The best app ever!', 'role': 'Somebody'}],
       'close': {'title': 'Start watching tonight', 'text': 'Sign in and add your first film.'}}


def test_a_site_with_content_of_its_own_is_never_thin():
    for f in sorted(FIX.glob('*.json')):
        assert E.thin(json.loads(f.read_text(encoding='utf-8')))[0] is False, f.name


def test_a_page_of_a_headline_is_thin_and_one_that_says_enough_is_not():
    assert E.thin(THIN)[0] is True
    wordy = copy.deepcopy(THIN)
    wordy['hero']['text'] = ' '.join(['word'] * E.WORDS_ENOUGH)
    assert E.thin(wordy) == (False, 'the page says %d words of its own' % E.words(wordy)) and E.words(wordy) > E.WORDS_ENOUGH
    assert 'faq' not in E.empty(THIN) and set(E.empty(THIN)) == set(E.SECTIONS) - {'faq'}


def test_a_page_nothing_is_known_of_gets_no_examples():
    # an address that answered with an error page: a headline of the browser's and nothing else. Nine sections written
    # for it would be a business invented from nothing (tried 2026-11-25) — it is not thin, it is unknown
    lost = {'brand': {'name': 'Zasox'}, 'hero': {'title': 'This page cannot be found'}, 'media': {}}
    assert E.known(lost) is False and E.thin(lost)[0] is False and 'too little is known' in E.thin(lost)[1]
    assert E.known({'hero': {'title': ' '.join(['word'] * 40)}}) is False, 'no name, no examples'
    assert E.known(THIN) is True


def test_examples_fill_only_what_is_empty_and_only_what_may_stand():
    d, filled = E.merge(THIN, RAW)
    assert filled == ['hero.text', 'statement', 'close', 'features', 'steps', 'figures', 'quotes', 'trust']
    assert d['faq'] == THIN['faq'] and d['brand'] == THIN['brand'] and d['hero']['title'] == 'Please sign in', "the client's own is never touched"
    assert [x['t'] for x in d['features']['items']] == ['One library', 'Any screen', 'Offline'], 'an item with a filler word is left out'
    assert [f['v'] for f in d['figures']] == ['4K', '12 min']
    assert d['quotes'] == [{'q': RAW['quotes'][0]['q'], 'quote': RAW['quotes'][0]['q'], 'role': 'Subscriber, film club', 'by': 'Subscriber, film club'}], 'a claim of rank, an exclamation: left out'
    assert A.validate(d) == [], 'the filled data is still the templates\' data'
    assert THIN.get('statement') is None, 'pure: the data given is not changed'
    again, more = E.merge(d, RAW)
    assert more == [] and again == d, 'a section that is there is not an empty one'


def test_nothing_usable_fills_nothing():
    for raw in (None, {}, {'statement': {'title': 'Only a title'}}, {'features': {'items': [{'t': 'One', 'd': 'Two.'}]}}, {'figures': 'no'}):
        assert E.merge(THIN, raw) == (THIN, [])


def test_the_job_takes_examples_only_through_the_switches():
    server = (ROOT / 'server' / 'templates.mjs').read_text(encoding='utf-8')
    assert re.search(r"SWARM_EXAMPLES !== '0' && !job\.options\?\.keep_text && job\.options\?\.mode !== 'seo-safe'", server)
    assert "extra.keep_text=true" in (ROOT / 'web' / 'app.html').read_text(encoding='utf-8')
    assert 'id="own"' in (ROOT / 'web' / 'index.html').read_text(encoding='utf-8') and "&own=1" in (ROOT / 'web' / 'js' / 'landing.js').read_text(encoding='utf-8')
