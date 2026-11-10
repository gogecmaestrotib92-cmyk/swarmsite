"""A section whose typesetting is broken after composition goes back to what it was; what cannot go back refuses the page."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'swarm'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'compose'))
import run as RUN

HERO = '<section class="sec hero" id="top"><h1>H</h1></section>'
BEFORE = f'<html><head></head><body>{HERO}<section class="sec photo" id="earn"><h2 class="h2">What could your book earn?</h2></section><section class="sec cards" id="kit"><h2 class="h2">Kit</h2></section></body></html>'
AFTER = BEFORE.replace('<section class="sec photo" id="earn">', '<section class="sec photo pc pc-f-stage" id="earn">').replace('<section class="sec cards" id="kit">', '<section class="sec cards lc" id="kit">')


def run(tmp_path, monkeypatch, readings):
    out = tmp_path / 'page.html'; out.write_text(AFTER, encoding='utf-8'); calls = iter(readings)
    monkeypatch.setattr(RUN, 'layout_breaks', lambda path: next(calls))
    record = RUN.mend_layout(str(out), BEFORE, lambda page: out.write_text(page, encoding='utf-8'))
    return record, out.read_text(encoding='utf-8')


def test_a_broken_section_goes_back_and_the_others_stay(tmp_path, monkeypatch):
    record, page = run(tmp_path, monkeypatch, [[{'kind': 'stacked-words', 'section': 'earn', 'widths': [1440], 'detail': 'x'}], []])
    assert record['reverted'] == ['earn'] and record['left'] == [] and record['own'] == []
    assert 'pc-f-stage' not in page and 'class="sec cards lc"' in page


def test_a_clean_page_is_left_alone(tmp_path, monkeypatch):
    record, page = run(tmp_path, monkeypatch, [[]])
    assert record == {'breaks': [], 'reverted': [], 'left': []} and page == AFTER


def test_a_break_in_the_first_screen_is_the_compositions_own(tmp_path, monkeypatch):
    broken = [{'kind': 'split-word', 'section': 'top', 'widths': [390], 'detail': 'x'}]
    record, page = run(tmp_path, monkeypatch, [broken])
    assert record['reverted'] == [] and record['own'] == broken


def test_a_break_that_was_there_before_is_not_held_against_the_composition(tmp_path, monkeypatch):
    out = tmp_path / 'page.html'; out.write_text(BEFORE, encoding='utf-8')
    monkeypatch.setattr(RUN, 'layout_breaks', lambda path: [{'kind': 'thin-column', 'section': 'kit', 'widths': [390], 'detail': 'x'}])
    record = RUN.mend_layout(str(out), BEFORE, lambda page: None)
    assert record['reverted'] == [] and record['own'] == []
