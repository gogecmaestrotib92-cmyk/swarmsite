"""The page is planned with its first screen (lib/compose/compose.py): the composer of the first screen names the one
device that returns down the page, the sections that carry it, at most one event and the sections that stay plain. The
plan names only sections that exist, travels with the direction to every composer after it, and without a device or a
carrier there is no plan."""
import sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'compose')); sys.path.insert(0, str(ROOT / 'lib'))
import compose as COMPOSE

PAGE = ('<section class="sec hero" id="top"><h1>Head</h1></section>'
        '<section class="sec photo band-paper" id="tour"><h2>Tour</h2><p>Twenty words of text here.</p><img src="a.jpg"></section>'
        '<section class="sec indexlist band-paper" id="features"><h2>Features</h2><ul><li>One</li><li>Two</li></ul></section>'
        '<section class="sec ledger band-paper" id="pricing"><h2>Pricing</h2><ul><li>Plan</li></ul></section>'
        '<section class="sec archive band-paper" id="more"><p>links</p></section>')


class Plan(unittest.TestCase):
    def test_the_outline_is_the_sections_under_the_first_screen(self):
        below = COMPOSE.outline(PAGE); self.assertEqual([s['id'] for s in below], ['tour', 'features', 'pricing'])
        self.assertEqual(below[0]['kind'], 'photo with a picture'); self.assertEqual(below[1]['kind'], 'indexlist'); self.assertGreater(below[0]['chars'], 10)

    def test_a_plan_names_only_sections_that_exist(self):
        below = COMPOSE.outline(PAGE)
        plan = COMPOSE.page_plan({'device': 'pictures  cut on a diagonal', 'carriers': [{'section': 'tour', 'how': 'the diagonal cut'}, {'section': 'invented', 'how': 'x'}, {'section': 'features', 'how': ''}],
                                  'event': {'section': 'pricing', 'what': 'the only dark ground'}, 'plain': ['features', 'tour', 'nowhere']}, below)
        self.assertEqual(plan['device'], 'pictures cut on a diagonal'); self.assertEqual([c['section'] for c in plan['carriers']], ['tour'])
        self.assertEqual(plan['event'], {'section': 'pricing', 'what': 'the only dark ground'}); self.assertEqual(plan['plain'], ['features'], 'a carrier is not also plain')
        words = COMPOSE.plan_words(plan)
        for part in ('PAGE PLAN', 'pictures cut on a diagonal', '"tour" — the diagonal cut', '"pricing" — the only dark ground', '"features"'): self.assertIn(part, words)

    def test_without_a_device_or_a_carrier_there_is_no_plan(self):
        below = COMPOSE.outline(PAGE)
        for answer in (None, 'a plan', {}, {'device': ' ', 'carriers': [{'section': 'tour', 'how': 'x'}]}, {'device': 'd', 'carriers': []}, {'device': 'd', 'carriers': [{'section': 'invented', 'how': 'x'}]}):
            with self.subTest(answer=answer): self.assertIsNone(COMPOSE.page_plan(answer, below))
        self.assertIsNone(COMPOSE.page_plan({'device': 'd', 'carriers': [{'section': 'tour', 'how': 'x'}], 'event': {'section': 'invented', 'what': 'y'}}, below)['event'])

    def test_the_composer_is_asked_for_the_plan_and_the_others_read_it(self):
        self.assertIn('page_plan', COMPOSE.TOOL['input_schema']['properties']); self.assertIn('THE PAGE PLAN', COMPOSE.SYSTEM)
        handed = COMPOSE._directed('Quiet type. ' + COMPOSE.plan_words({'device': 'd', 'carriers': [{'section': 'tour', 'how': 'h'}], 'event': None, 'plain': []}))
        self.assertIn('PAGE PLAN', handed[0]['text']); self.assertIn('stays quiet', handed[0]['text'])


if __name__ == '__main__': unittest.main()
