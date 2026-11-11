"""The studio step of a job: the first clean variant stands as the page with what the client's search standing needs; nothing clean leaves the page alone."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'swarm'))
for sub in ('studio', 'devices'): sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', sub))
import run as RUN, studio as STUDIO, scenes as SCENES

INV = {'lang': 'en', 'url': 'https://x.test/', 'seo': {'canonical': 'https://x.test/'}, 'actions': [{'text': 'Pricing', 'href': 'https://x.test/pricing'}, {'text': 'Deep page', 'href': 'https://x.test/deep'}],
       'sourceCoverage': {'sections': [{'title': 'A long story', 'text': 'A paragraph of the source that the new page does not carry at all, word for word, kept for search.'}]}}
PAGE = '<html><head></head><body><main><section id="top"><h1>New</h1><a href="https://x.test/pricing">Pricing</a></section></main><footer></footer></body></html>'


def job(tmp_path, variants):
    (tmp_path / 'inventory.json').write_text(json.dumps(INV)); (tmp_path / 'brief.json').write_text(json.dumps({'mode': 'seo-safe'})); (tmp_path / 'page.html').write_text('ROUND PAGE')
    def build(src, out, n=3, atmosphere_wanted=False):
        os.makedirs(out, exist_ok=True)
        for v in variants: open(os.path.join(out, f'page-{v["tag"]}.html'), 'w').write(PAGE)
        return {'variants': variants, 'usd': .5, 'seconds': 60}
    return build


def test_the_first_clean_variant_stands_and_keeps_words_and_links(tmp_path, monkeypatch):
    monkeypatch.setattr(STUDIO, 'build', job(tmp_path, [{'tag': 'a', 'clean': False, 'type': 't', 'scheme': 's', 'scenes': []}, {'tag': 'b', 'clean': True, 'type': 't', 'scheme': 's', 'scenes': []}, {'tag': 'c', 'clean': True, 'type': 't', 'scheme': 's', 'scenes': []}]))
    info = RUN.studio_page(str(tmp_path), str(tmp_path / 'page.html')); page = (tmp_path / 'page.html').read_text()
    assert info['kept'] == 'b' and info['others'] == ['c']
    assert 'A paragraph of the source' in page and 'https://x.test/deep' in page and 'rel="canonical"' in page and page.count('id="more-about"') == 1
    assert 'A paragraph of the source' in (tmp_path / 'studio' / 'page-c.html').read_text()


def test_no_clean_variant_leaves_the_round_page(tmp_path, monkeypatch):
    monkeypatch.setattr(STUDIO, 'build', job(tmp_path, [{'tag': 'a', 'clean': False}]))
    info = RUN.studio_page(str(tmp_path), str(tmp_path / 'page.html'))
    assert info['kept'] is None and (tmp_path / 'page.html').read_text() == 'ROUND PAGE'


def test_a_free_job_is_not_given_the_archive(tmp_path, monkeypatch):
    monkeypatch.setattr(STUDIO, 'build', job(tmp_path, [{'tag': 'a', 'clean': True}])); (tmp_path / 'brief.json').write_text(json.dumps({'mode': 'free'}))
    RUN.studio_page(str(tmp_path), str(tmp_path / 'page.html'))
    assert 'more-about' not in (tmp_path / 'page.html').read_text()


def test_the_switch(tmp_path, monkeypatch):
    monkeypatch.setenv('LIVETEST', '1'); monkeypatch.delenv('SWARM_STUDIO', raising=False)
    assert RUN.studio_wanted(str(tmp_path)) is False
    (tmp_path / 'brief.json').write_text(json.dumps({'studio': True})); assert RUN.studio_wanted(str(tmp_path)) is True
    monkeypatch.delenv('LIVETEST'); (tmp_path / 'brief.json').write_text('{}'); assert RUN.studio_wanted(str(tmp_path)) is True
    monkeypatch.setenv('SWARM_STUDIO', '0'); assert RUN.studio_wanted(str(tmp_path)) is False


def graded(tmp_path, monkeypatch, con, crit):
    log = {'rounds': [{'k': 1, 'score': 64, 'taste': 42, 'contract': 92, 'broken': [{'id': 'seo-text-kept'}], 'fixes': []}], 'studio': {'kept': 'a'}}
    def contract(slug, page):
        if isinstance(con, Exception): raise con
        return con
    def critique(slug, page, model, fast, files=None, measured=None, own=None):
        assert own and own.get('scenes'), "the critic is told the page's own plan, not the template's direction"
        if isinstance(crit, Exception): raise crit
        return crit
    monkeypatch.setattr(RUN, 'contract', contract); monkeypatch.setattr(RUN.C, 'critique', critique)
    got = RUN.grade_studio(str(tmp_path), str(tmp_path / 'page.html'), log, __import__('time').time(), {'scenes': ['open-picture', 'close']})
    return got, log


def test_the_scores_of_a_job_are_of_the_studio_page(tmp_path, monkeypatch):
    got, log = graded(tmp_path, monkeypatch, {'score': 100, 'failed': []}, {'score': 70, 'verdict': 'Reads as designed.', 'axes': {'design': 70}, 'fixes': []})
    assert got == (round(.55 * 70 + .45 * 100), 2) and log['rounds'][-1]['studio'] is True
    card = RUN.scorecard(log, got[1]); critic = json.loads((tmp_path / 'critic.json').read_text())
    assert card['page'] == 'studio' and card['taste'] == 70 and card['contract'] == 100 and card['technical']['pass'] and card['technical']['hard_failures'] == []
    assert critic['studio'] is True and critic['verdict'] == 'Reads as designed.' and critic['taste'] == 70


def test_a_studio_page_the_critic_did_not_read_shows_no_taste_rather_than_another_pages(tmp_path, monkeypatch):
    got, log = graded(tmp_path, monkeypatch, {'score': 95, 'failed': [{'id': 'seo-text-kept', 'detail': '90%', 'weight': 3}]}, RuntimeError('overloaded'))
    card = RUN.scorecard(log, got[1])
    assert got == (95, 2) and card['page'] == 'studio' and card['taste'] is None and card['creative']['pass'] is False and card['contract'] == 95 and card['technical']['hard_failures'] == ['seo-text-kept']


def test_a_studio_page_nothing_could_grade_says_whose_scores_these_are(tmp_path, monkeypatch):
    got, log = graded(tmp_path, monkeypatch, RuntimeError('no browser'), {'score': 70})
    assert got is None and len(log['rounds']) == 1 and log['studio']['graded'] is False
    assert RUN.scorecard(log, 1)['page'] == 'replaced'


def test_what_no_section_holds_is_kept_and_the_structured_data_is_the_sources_own():
    import seo
    inv = dict(INV, title='X — home', copy={'text': 'Pricing Deep page Made with care in a small kitchen since 1996. Shopping cart Close. Every dish is cooked to order by two people.'},
               seo={'canonical': 'https://x.test/', 'structuredData': {'raw': ['{"@type":"Restaurant","name":"X"}', 'not json']}})
    rest = seo.leftover(inv, 'Every dish is cooked to order by two people.')
    assert rest == ['Made with care in a small kitchen since 1996.'], 'labels of links are cut out, short scraps are dropped, what the page already says is not repeated'
    page = SCENES.keep(PAGE, inv)
    assert 'Made with care in a small kitchen' in page and page.count('application/ld+json') == 1 and '"@type":"Restaurant"' in page and 'not json' not in page
