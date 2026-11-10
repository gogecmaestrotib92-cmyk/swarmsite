"""The first screen's treatment of its headline is repeated on the sections the plan names, without writing a word."""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'compose'))
import device as DEVICE

IR = {'hero': {'nodes': [{'id': 'h1', 't': 'text', 'as': 'h1', 'lines': [2, 3], 'indent': [0, 2], 'mark': 'italic'}]}}
PAGE = ('<html><head></head><body><section class="sec hero" id="top"><h1>x</h1></section>'
        '<section class="sec photo band-paper" id="tour"><div class="wrap"><h2 class="h2" style="--fs:40px;--lw:7">Draw. Film. Prepare.</h2><p>Words.</p></div></section>'
        '<section class="sec ledger band-paper" id="faq"><div class="wrap"><h2 class="h2">Questions coaches ask</h2></div></section>'
        '<section class="sec indexlist band-paper" id="mid"><div class="wrap"><h2 class="h2" style="text-align:center;--lw:6">Centred heading of four</h2></div></section>'
        '<section class="sec cta band-dark" id="contact"><div class="wrap center"><h2 class="h2" style="--lw:10">A tool made by players</h2><div class="ctas"><a class="btn" href="https://x.test/">Start</a></div></div></section>'
        '</body></html>')
PLAN = {'device': 'stepped', 'carriers': [{'section': 'tour', 'how': 'stepped', 'word': 'Film'}, {'section': 'mid', 'how': 'stepped'}], 'event': {'section': 'contact', 'what': 'plate'}, 'plain': ['faq']}
text = lambda html: ' '.join(re.sub(r'<[^>]+>', ' ', re.sub(r'</?em\b[^>]*>', '', html)).split())   # as a reader gets it: an <em> does not part a word from its full stop


def test_the_treatment_is_read_off_the_drawn_headline():
    assert DEVICE.treatment(IR) == {'mark': 'italic', 'step': 2}
    assert DEVICE.treatment({'hero': {'nodes': [{'as': 'h1'}]}}) == {'mark': None, 'step': 0}


def test_a_carrier_heading_is_stepped_and_its_named_word_marked():
    page, report = DEVICE.carry(PAGE, PLAN, IR)
    assert report['drawn'] and report['sections']['tour'] == {'mark': 'italic', 'word': 'Film', 'step': 2}
    assert '<em class="dv-mk dv-mk-italic">Film</em>.' in page and page.count('class="dv-l"') >= 2 and '--dv-step:2' in page


def test_no_word_is_written_or_lost():
    page, _ = DEVICE.carry(PAGE, PLAN, IR)
    assert text(page.split('</style>')[-1]) == text(PAGE)


def test_a_plain_section_and_a_centred_heading_are_not_stepped():
    page, report = DEVICE.carry(PAGE, PLAN, IR)
    assert 'faq' not in report['sections'] and 'step' not in report['sections']['mid'] and report['sections']['mid']['mark'] == 'italic'


def test_the_closing_named_as_the_event_becomes_the_plate():
    page, report = DEVICE.carry(PAGE, PLAN, IR)
    assert report['event'] == 'contact' and 'class="sec cta band-dark dv-event"' in page


def test_a_closing_with_a_form_is_left_as_it_is():
    page, report = DEVICE.carry(PAGE.replace('<div class="ctas">', '<form class="form"></form><div class="ctas">'), PLAN, IR)
    assert report['event'] is None and 'dv-event"' not in page


def test_nothing_to_carry_changes_nothing():
    assert DEVICE.carry(PAGE, PLAN, {'hero': {'nodes': [{'as': 'h1'}]}})[0] == PAGE and DEVICE.carry(PAGE, None, IR)[0] == PAGE
