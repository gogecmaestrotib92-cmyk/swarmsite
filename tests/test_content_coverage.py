import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'swarm'))
import agents
import coverage_report


class UXContentPreservationTests(unittest.TestCase):
    def test_reader_receives_homepage_section_evidence_before_subpages(self):
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'inventory.json', {'sourceCoverage': {'sections': [
                {'id': 'faq', 'title': 'Frequently asked questions', 'text': 'Helpful answers.', 'kind': 'faq'}]},
                'sourcePages': [{'url': 'https://example.test/pricing', 'copy': {'text': 'pricing'}}]})
            with patch.object(agents, 'ask', return_value={'what': 'Test', 'facts': [], 'offers': []}) as ask:
                agents.reader(directory)
            blocks = ask.call_args.args[1]
            self.assertIn('Frequently asked questions', blocks[0]['text'])
            self.assertTrue(any('SOURCE SUBPAGES' in block['text'] for block in blocks))
            self.assertIn('do not drop capabilities', agents.READER_TOOL['input_schema']['properties']['capabilities']['description'])

    def test_subpage_sections_are_reported_as_source_evidence(self):
        inventory = {'sourceCoverage': {'sections': [], 'routes': [
            {'url': 'https://example.test/pricing', 'status': 'visited'},
            {'url': 'https://example.test/missing', 'status': 'failed'}], 'complete': False},
            'sourcePages': [{'url': 'https://example.test/pricing', 'title': 'Pricing',
                             'sectionsFound': 2, 'sectionsTruncated': True,
                             'sections': [{'id': 'p1-1', 'title': 'Gold plan'}]}]}
        result = coverage_report.build_coverage(inventory, '<main><h1>Other</h1></main>')
        self.assertFalse(result['crawl']['complete'])
        self.assertEqual(result['crawl']['routes_failed'], 1)
        self.assertTrue(result['source_pages'][0]['sections_truncated'])
        self.assertEqual(result['source_pages'][0]['sections'][0]['status'], 'needs_review')
        self.assertEqual(result['scope'], 'single_page_preview')

    def test_ux_cannot_drop_any_existing_beat(self):
        with tempfile.TemporaryDirectory() as directory:
            doc = {'hero': {}, 'beats': [{'id': 'offer', 'type': 'features'},
                    {'id': 'faq', 'type': 'faq'}, {'id': 'contact', 'type': 'form'},
                    {'id': 'proof', 'type': 'quote'}]}
            agents.W(directory, 'direction.json', doc)
            agents.apply_ux(directory, {'order': ['offer', 'contact', 'proof']})
            self.assertEqual([b['id'] for b in agents.J(directory, 'direction.json')['beats']],
                             ['offer', 'faq', 'contact', 'proof'])

    def test_ux_can_reorder_all_beats(self):
        with tempfile.TemporaryDirectory() as directory:
            doc = {'hero': {}, 'beats': [{'id': 'a', 'type': 'features'},
                    {'id': 'b', 'type': 'faq'}, {'id': 'c', 'type': 'form'}]}
            agents.W(directory, 'direction.json', doc)
            agents.apply_ux(directory, {'order': ['b', 'a', 'c']})
            self.assertEqual([b['id'] for b in agents.J(directory, 'direction.json')['beats']], ['b', 'a', 'c'])

    def test_copy_preserves_faq_answers_and_questions_but_can_edit_other_items(self):
        with tempfile.TemporaryDirectory() as directory:
            faq = ['How does this work?', 'A complete source-grounded answer.']
            agents.W(directory, 'direction.json', {'hero': {}, 'beats': [
                {'id': 'faq', 'type': 'faq', 'items': [faq]},
                {'id': 'prices', 'type': 'ledger', 'items': [['Basic', 'Free']]}]})
            changes = agents.apply_copy(directory, {'edits': [
                {'path': 'faq.items[0][0]', 'value': 'Changed question'},
                {'path': 'faq.items[0][1]', 'value': 'Changed answer'},
                {'path': 'prices.items[0][0]', 'value': 'Starter'}]})
            beats = agents.J(directory, 'direction.json')['beats']
            self.assertEqual(changes, 1)
            self.assertEqual(beats[0]['items'][0], faq)
            self.assertEqual(beats[1]['items'][0][0], 'Starter')


class CoverageEvidenceTests(unittest.TestCase):
    def test_marks_only_evidence_and_never_claims_pages_generated(self):
        inventory = {'url': 'https://example.com/', 'sourceCoverage': {
            'sections': [{'id': 'a', 'title': 'Frequently Asked Questions', 'sourceUrl': 'https://example.com/'},
                         {'id': 'b', 'title': 'Voice agents', 'sourceUrl': 'https://example.com/'}],
            'routes': [{'url': 'https://example.com/pricing', 'label': 'Prices', 'status': 'visited'},
                       {'url': 'https://example.com/events', 'label': 'Events', 'status': 'limit', 'reason': 'not crawled'}]}}
        page = '''<html><head><title>Voice agents</title><style>.x::before {content:"Voice agents"}</style></head>
            <body><h2>Frequently Asked Questions</h2><a href="https://example.com/pricing/">Plans</a>
            <script>const hidden='Voice agents';</script><div aria-hidden="true">Voice agents</div></body></html>'''
        result = coverage_report.build_coverage(inventory, page)
        self.assertEqual([x['status'] for x in result['sections']], ['text_detected', 'needs_review'])
        self.assertEqual([x['status'] for x in result['routes']], ['linked_to_source', 'not_linked'])
        self.assertEqual(result['routes'][1]['capture_status'], 'limit')
        self.assertEqual(result['summary']['sections_needing_review'], 1)
        self.assertEqual(result['scope'], 'single_page_preview')
        self.assertTrue(any('not proof' in limitation for limitation in result['limitations']))
        self.assertFalse(result['source_catalog_fallback'])

    def test_missing_catalog_is_flagged_and_h2_only_fallback_is_not_full_sitemap(self):
        inventory = {'url': 'https://example.com/', 'copy': {'headings': [
            {'tag': 'H1', 'text': 'Home'}, {'tag': 'H2', 'text': 'Our events'}]},
            'sourcePages': [{'url': 'https://example.com/contact', 'navLabel': 'Contact'}]}
        result = coverage_report.build_coverage(inventory, '<h2>Our events</h2>')
        self.assertTrue(result['source_catalog_fallback'])
        self.assertEqual(result['summary']['sections_total'], 1)
        self.assertEqual(result['summary']['routes_not_linked'], 1)

    def test_similar_but_different_words_require_review(self):
        inventory = {'sourceCoverage': {'sections': [{'title': 'App integrations'}], 'routes': []}}
        result = coverage_report.build_coverage(inventory, '<h2>Apps</h2>')
        self.assertEqual(result['sections'][0]['status'], 'needs_review')

    def test_sections_with_identical_titles_remain_independent(self):
        inventory = {'sourceCoverage': {'sections': [{'id': 's1', 'title': 'Services'}, {'id': 's2', 'title': 'Services'}], 'routes': []}}
        result = coverage_report.build_coverage(inventory, '<h2>Services</h2>')
        self.assertEqual([s['id'] for s in result['sections']], ['s1', 's2'])

    def test_visited_canonical_destination_counts_as_source_link(self):
        inventory = {'sourceCoverage': {'sections': [], 'routes': [
            {'url': 'https://example.test/old', 'finalUrl': 'https://example.test/new/', 'status': 'visited'},
            {'url': 'https://example.test/unchecked', 'finalUrl': 'https://example.test/new', 'status': 'failed'}]}}
        result = coverage_report.build_coverage(inventory, '<a href="https://example.test/new">Learn more</a>')
        self.assertEqual([r['status'] for r in result['routes']], ['linked_to_source', 'not_linked'])

    def test_faq_question_and_answer_are_separately_verified(self):
        inventory = {'sourceCoverage': {'sections': [{'title': 'FAQ', 'faqTruncated': True, 'faq': [
            {'question': 'Does it cost?', 'answer': 'Free for individuals.', 'status': 'readable'},
            {'question': 'Are teams supported?', 'answer': 'Teams can schedule.', 'status': 'readable'},
            {'question': 'How does it work?', 'answer': '', 'status': 'unavailable'},
            {'question': 'What about contracts?', 'answer': 'A partial answer', 'status': 'readable', 'answerTruncated': True},
            {'question': 'A partial question', 'answer': 'A complete answer.', 'status': 'readable', 'questionTruncated': True},
        ]}], 'routes': []}}
        result = coverage_report.build_coverage(inventory, '''<h2>FAQ</h2>
            <h3>Does it cost?</h3><p>Free for individuals.</p>
            <h3>Are teams supported?</h3><p>Scheduling for teams.</p>
            <h3>How does it work?</h3><p>Unknown.</p><p>A partial answer</p>''')
        self.assertEqual([f['status'] for f in result['sections'][0]['faq']],
                         ['text_detected', 'needs_review', 'source_unavailable', 'source_incomplete', 'source_incomplete'])
        self.assertEqual(result['summary']['faq_total'], 5)
        self.assertEqual(result['summary']['faq_needing_review'], 1)
        self.assertEqual(result['summary']['faq_source_unavailable'], 1)
        self.assertEqual(result['summary']['faq_source_incomplete'], 2)
        self.assertTrue(result['faq_catalog_truncated'])

    def test_quotes_and_panels_require_complete_source_and_original_links(self):
        inventory = {'sourceCoverage': {'sections': [{'title': 'Reviews', 'testimonialsTruncated': True,
            'testimonials': [
                {'status': 'candidate', 'text': 'Very useful.', 'attribution': 'Ada', 'links': [{'url': 'https://reviews.test/a'}]},
                {'status': 'candidate', 'text': 'Wonderful.', 'attribution': 'Bea', 'links': [{'url': 'https://reviews.test/b'}]},
                {'status': 'candidate', 'text': 'Partial', 'attribution': 'C', 'textTruncated': True, 'links': []}],
            'panels': [{'status': 'candidate', 'trigger': 'Case study', 'text': 'A real customer story.', 'links': [{'url': 'https://example.test/customer'}]},
                       {'status': 'unavailable', 'trigger': 'Unavailable', 'text': '', 'links': []}]}], 'routes': []}}
        html = '''<h2>Reviews</h2><blockquote>Very useful.</blockquote><p>Ada</p>
            <a href="https://reviews.test/a">Review</a><p>Wonderful. Bea</p>
            <p>A real customer story.</p><a href="https://example.test/customer">Story</a>'''
        result = coverage_report.build_coverage(inventory, html)
        section = result['sections'][0]
        self.assertEqual([x['status'] for x in section['testimonials']], ['text_detected', 'needs_review', 'source_incomplete'])
        self.assertEqual([x['status'] for x in section['panels']], ['text_detected', 'source_incomplete'])
        self.assertEqual(result['summary']['testimonials_total'], 3)
        self.assertTrue(result['evidence_catalog_truncated'])

    def test_heading_match_is_independent_of_quote_and_panel_matches(self):
        quote = {'status': 'candidate', 'text': 'Real quote', 'attribution': 'Ada', 'links': []}
        panel = {'status': 'candidate', 'trigger': 'Customer', 'text': 'Real story', 'links': []}
        inventory = {'sourceCoverage': {'sections': [
            {'id': 'one', 'title': 'Heading present', 'testimonials': [quote], 'panels': [panel]},
            {'id': 'two', 'title': 'Heading missing', 'testimonials': [quote], 'panels': [panel]},
        ], 'routes': []}}
        result = coverage_report.build_coverage(inventory, '<h2>Heading present</h2>')
        self.assertEqual([s['status'] for s in result['sections']], ['text_detected', 'needs_review'])
        result = coverage_report.build_coverage(inventory, '<p>Real quote Ada Real story</p>')
        self.assertEqual([s['status'] for s in result['sections']], ['needs_review', 'needs_review'])
        self.assertEqual(result['sections'][0]['testimonials'][0]['status'], 'text_detected')
        self.assertEqual(result['sections'][0]['panels'][0]['status'], 'text_detected')

if __name__ == '__main__':
    unittest.main()
