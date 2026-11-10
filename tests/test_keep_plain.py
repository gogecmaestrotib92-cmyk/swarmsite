"""The page plan names sections that stay quiet; a later composer's proposal for one of them is not drawn."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'swarm'))
import run as RUN


def test_a_plain_section_is_taken_out_and_recorded():
    record = {'plan': {'plain': ['faq', 'team']}}
    doc, dropped = RUN.keep_plain({'ir': 1, 'note': 'n', 'lists': [{'section': 'faq', 'form': 'index'}, {'section': 'features', 'form': 'ledger'}]}, record)
    assert [l['section'] for l in doc['lists']] == ['features'] and dropped == ['faq'] and record['kept_plain'] == ['faq']


def test_nothing_left_means_nothing_is_drawn():
    record = {'plan': {'plain': ['faq']}}
    doc, dropped = RUN.keep_plain({'ir': 1, 'words': [{'section': 'faq', 'form': 'columns'}]}, record)
    assert doc is None and dropped == ['faq']


def test_a_gallery_that_takes_in_a_plain_section_goes_and_the_pictures_stay():
    record = {'plan': {'plain': ['team']}}
    doc, dropped = RUN.keep_plain({'ir': 1, 'pictures': [{'section': 'story', 'form': 'bleed'}], 'galleries': [{'sections': ['work', 'team']}]}, record)
    assert doc['pictures'] and 'galleries' not in doc and dropped == ['work']


def test_no_plan_changes_nothing():
    doc = {'ir': 1, 'lists': [{'section': 'faq', 'form': 'index'}]}
    assert RUN.keep_plain(doc, {}) == (doc, []) and RUN.keep_plain(None, {'plan': {'plain': ['faq']}}) == (None, [])
