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
