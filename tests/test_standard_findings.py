"""The measurable half of the Studio Quality Standard as code (lib/qa/standard.py): a reading outside its threshold is a
finding with all its parts; a reading inside it is not; the page level follows the Standard's rule; and the loop decides
on two tracks that are never added up (lib/swarm/run.py standing / beats / composed_candidate)."""
import os, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'qa')); sys.path.insert(0, str(ROOT / 'lib' / 'swarm'))
import standard as ST
import critic as C
import run


def view(**over):
    """A page inside every threshold; `over` moves single readings out."""
    kinds = [{'family': 'Display', 'px': 96, 'vw': 6.7, 'weight': 400, 'tracking_em': -0.01, 'leading': 1.0, 'chars': 24, 'where': {'h1': 1}},
             {'family': 'Text', 'px': 16, 'vw': 1.1, 'weight': 400, 'tracking_em': 0, 'leading': 1.4, 'chars': 900, 'where': {'p': 12}}]
    sections = [{'ground': 'rgb(250, 250, 250)', 'chars_per_screen': 220} for _ in range(6)]
    v = {'page_screens': 9.0, 'type': kinds, 'sections': sections, 'paragraphs': [{'per_line': 58}], 'headings': {'h1': {'px': 96, 'lines': 2, 'w': 0.8}},
         'alignment': {'edges': [{'at': 0.03, 'blocks': 20}, {'at': 0.5, 'blocks': 8}], 'text_centred_share': 0.0}, 'first_screen': {'largest_picture': {'share_of_screen': 1.0}, 'filled_buttons': 1},
         'pictures': [{'bleeds': True, 'shadow': False, 'radius': '0px'}, {'bleeds': False, 'shadow': False, 'radius': '0px'}, {'bleeds': False, 'shadow': False, 'radius': '0px'}],
         'surfaces': {'rules': {'on_elements': 2, 'by_pseudo_elements': 0, 'hr': 0}}, 'letters': {'by_family': [], 'accents_as_separate_marks': []},
         'load': {'session': {'began_ms': 200}, 'reveals': {'h1_settles_ms': 700}}, 'lab': {'cls_on_load': 0.0, 'lcp': {'ms': 300}},
         'scroll': {'elements_followed': 100, 'reveals': {'elements': 20, 'fade_ms': [400, 450, 500], 'travel_px': [10, 12, 14]}, 'held': {'screens': {}}, 'lag_ms': [0, 0, 0]}}
    v.update(over); return v


def page(desktop=None, mobile=None, calm=None): return {'views': {'desktop': desktop or view(), 'mobile': mobile or view(paragraphs=[{'per_line': 40}])}, 'reduced_motion': calm or {'reveals_on_load': 0, 'reveals_on_load_normally': 4}}
ids = lambda evidence: [f"{f['id']}@{f['view']}" for f in ST.findings(evidence)]


class Findings(unittest.TestCase):
    def test_a_page_inside_every_threshold_has_no_finding_and_passes_the_measured_checks(self):
        self.assertEqual(ids(page()), []); self.assertTrue(all(c['pass'] for c in ST.technical(page()))); self.assertEqual({c['id'] for c in ST.technical(page())}, {'T-13', 'T-15', 'T-16', 'T-19'})

    def test_each_reading_outside_its_threshold_is_named(self):
        striped = [{'ground': g, 'chars_per_screen': 220} for g in ('a', 'b', 'a', 'b', 'a', 'b', 'a')]
        cases = {'CMP-08@1440': view(sections=striped), 'CMP-09@1440': view(surfaces={'rules': {'on_elements': 30, 'by_pseudo_elements': 3, 'hr': 0}}),
                 'CMP-06@1440': view(first_screen={'largest_picture': {'share_of_screen': 0.2}, 'filled_buttons': 1}, headings={'h1': {'px': 96, 'lines': 2, 'w': 0.3}}),
                 'CMP-01@1440': view(alignment={'edges': [{'at': 0.09, 'blocks': 20}], 'text_centred_share': 0.0}), 'CMP-03@1440': view(alignment={'edges': [{'at': 0.03, 'blocks': 20}], 'text_centred_share': 0.4}),
                 'IMG-02@1440': view(pictures=[{'bleeds': True, 'shadow': True, 'radius': '0px'}]), 'IMG-03@1440': view(pictures=[{'bleeds': True, 'shadow': False, 'radius': '8px'}, {'bleeds': False, 'shadow': False, 'radius': '24px'}]),
                 'IMG-04@1440': view(pictures=[{'bleeds': False, 'shadow': False, 'radius': '0px'}] * 3), 'TYP-06@1440': view(headings={'h1': {'px': 96, 'lines': 5, 'w': 0.8}}),
                 'TYP-05@1440': view(paragraphs=[{'per_line': 30}]), 'HIE-06@1440': view(headings={'h1': None}),
                 'MOT-03@1440': view(load={'session': {'began_ms': 300}, 'reveals': {'h1_settles_ms': 3000}}), 'TEC-16@1440': view(lab={'cls_on_load': 0.2, 'lcp': {'ms': 300}}),
                 'TYP-10@1440': view(letters={'by_family': [{'family': 'Display', 'asked': 2, 'not_drawn_by_it': ['š']}], 'accents_as_separate_marks': []})}
        for expected, desktop in cases.items():
            with self.subTest(expected): self.assertIn(expected, ids(page(desktop)))
        self.assertIn('MOT-04@390', ids(page(mobile=view(paragraphs=[{'per_line': 40}], scroll={'elements_followed': 50, 'reveals': {'elements': 5}, 'held': {'screens': {'4.0': 3}}, 'lag_ms': [0]}))))
        self.assertIn('MOT-09@390', ids(page(mobile=view(paragraphs=[{'per_line': 40}], scroll={'elements_followed': 50, 'reveals': {'elements': 5}, 'held': {'screens': {}}, 'lag_ms': [900, 1000, 1000]}))))

    def test_scale_between_regimes_is_a_finding_and_each_regime_is_not(self):
        with_h1 = lambda px: page(view(headings={'h1': {'px': px, 'lines': 2, 'w': 0.8}}))
        for px, found in ((30, False), (56, True), (96, False), (176, True), (240, False)):   # ÷16: 1.9 quiet · 3.5 between · 6 classic · 11 between · 15 poster
            with self.subTest(px): self.assertEqual('TYP-03@1440' in ids(with_h1(px)), found)

    def test_a_finding_has_every_part_the_standard_asks_for_and_track_t_comes_first(self):
        found = ST.findings(page(view(surfaces={'rules': {'on_elements': 40, 'by_pseudo_elements': 0, 'hr': 0}}), calm={'reveals_on_load': 3, 'reveals_on_load_normally': 5}))
        self.assertEqual([f['id'] for f in found], ['MOT-05', 'CMP-09']); rule = found[1]
        self.assertEqual((rule['area'], rule['track'], rule['confidence'], rule['evidence']['value']), ('composition', 'C', 'measured', 40))
        for part in ('reason', 'correction', 'expectation'): self.assertTrue(rule[part])
        self.assertIn('references', rule['evidence']['references']); self.assertFalse(next(c for c in ST.technical(page(calm={'reveals_on_load': 3, 'reveals_on_load_normally': 5})) if c['id'] == 'T-13')['pass'])

    def test_a_view_that_was_not_read_yields_nothing_rather_than_a_guess(self):
        self.assertEqual(ST.findings({'views': {'desktop': {'status': 200}, 'mobile': None}}), []); self.assertEqual(ST.technical({}), []); self.assertIsNone(ST.readings(None)['desktop'])


class FeelAndLead(unittest.TestCase):
    def test_small_targets_on_a_phone_fail_the_measured_check(self):
        check = lambda targets: next(c for c in ST.technical(page(mobile=view(paragraphs=[{'per_line': 40}], targets=targets))) if c['id'] == 'T-10')
        self.assertTrue(check({'counted': 12, 'under_24_px': 0, 'under_44_px': 5})['pass'], '24 px is the floor; 44 is reported, not required')
        self.assertFalse(check({'counted': 12, 'under_24_px': 2, 'under_44_px': 7})['pass'])
        self.assertNotIn('T-10', {c['id'] for c in ST.technical(page())}, 'not read, not guessed')

    def test_a_composed_first_screen_that_nothing_leads_is_sent_back(self):
        sys.path.insert(0, str(ROOT / 'lib' / 'compose')); import compose as COMPOSE
        seen = lambda picture, headline: {'desktop': {'lead': {'picture': picture, 'headline': headline}, 'wrapped': [], 'pictures': []}, 'mobile': {'lead': {'picture': 0.1, 'headline': 0.3}, 'wrapped': [], 'pictures': []}}
        found = COMPOSE.hero_findings(seen(0.2, 0.42)); self.assertIn('desktop-hero-nothing-leads', found); self.assertIn('20%', found['desktop-hero-nothing-leads']); self.assertIn('42%', found['desktop-hero-nothing-leads'])
        for picture, headline in ((0.9, 0.3), (0.1, 0.8), (0.4, 0.6)):
            with self.subTest(picture=picture, headline=headline): self.assertNotIn('desktop-hero-nothing-leads', COMPOSE.hero_findings(seen(picture, headline)))
        self.assertNotIn('desktop-hero-nothing-leads', COMPOSE.hero_findings({'desktop': {'lead': None, 'wrapped': [], 'pictures': []}}), 'a first screen that is not composed is not judged by this')
        self.assertNotIn('nothing-leads', ' '.join(COMPOSE.BREAKING), 'it is asked to be corrected, not a reason to throw the page away')

    def test_the_page_answers_a_press_and_respects_three_preferences(self):
        css = (ROOT / 'lib' / 'render' / 'render_bp.py').read_text()
        for rule in (':active', 'transform:scale(.97)', ':focus-visible', 'min-height:44px', 'prefers-reduced-transparency:reduce', 'prefers-contrast:more', 'prefers-reduced-motion'):
            with self.subTest(rule): self.assertIn(rule, css)


class Levels(unittest.TestCase):
    def test_bands_and_the_page_rule(self):
        self.assertEqual([ST.level_of(s) for s in (40, 55, 69, 70, 89, 90, -1, None)], [1, 2, 2, 3, 3, 4, None, None])
        even = {a: 3 for a in ST.AREAS}; self.assertEqual(ST.page_level(even), 3)
        self.assertEqual(ST.page_level(dict(even, imagery=1)), 2, 'never more than one level above the weakest area')
        self.assertEqual(ST.page_level(dict(even, typography=2.5)), 2.5, 'level 3 needs art direction and typography both at 3')
        self.assertIsNone(ST.page_level({})); self.assertEqual(sum(ST.WEIGHTS.values()), 100)

    def test_the_critics_final_report_is_made_safe(self):
        r = C.reviewed({'score': 61, 'levels': {'typography': 3, 'art_direction': 2, 'made_up': 4, 'imagery': 'high'}, 'findings': [
            {'defect': 'ART-02', 'area': 'art_direction', 'beat': 'features', 'evidence': 'the idea stops after the first screen', 'reason': 'no idea below', 'correction': {'op': 'gap', 'detail': 'a page plan'}},
            {'defect': 'X', 'area': 'typography', 'evidence': 'e', 'reason': 'r', 'correction': {'op': 'delete_everything'}}, {'defect': 'Y', 'area': 'typography', 'evidence': '', 'reason': 'r', 'correction': {'op': 'note'}}, 'nonsense']})
        self.assertEqual(r['levels'], {'typography': 3.0, 'art_direction': 2.0}); self.assertEqual(r['page_level'], 2.5)
        self.assertEqual([(f['id'], f['correction']['op'], f['confidence']) for f in r['findings']], [('ART-02', 'gap', 'seen')])
        self.assertEqual(C.reviewed({'score': 50, 'fixes': []}), {'score': 50, 'fixes': []}, 'an intermediate round has neither and is left as it is')
        tool = C.final_tool()['input_schema']['properties']; self.assertIn('gap', tool['findings']['items']['properties']['correction']['properties']['op']['enum'])
        self.assertNotIn('levels', C.TOOL['input_schema']['properties'], 'the short tool of the intermediate rounds is untouched')


class TwoTracks(unittest.TestCase):
    def test_which_page_stands(self):
        s = run.standing
        self.assertTrue(run.beats(s(40, 95, []), s(90, 99, [{'id': 'mobile-no-overflow'}])), 'a page that breaks no hard promise first')
        self.assertTrue(run.beats(s(50, 92, []), s(60, 85, [])), 'then the one that clears the technical bar')
        self.assertTrue(run.beats(s(60, 92, []), s(55, 100, [])), 'then the better-looking one, beyond a reading\'s noise')
        self.assertTrue(run.beats(s(58, 100, []), s(60, 92, [])), 'within the noise, the sounder one')
        self.assertFalse(run.beats(s(60, 92, [{'id': 'h2-short'}]), s(60, 92, [{'id': 'h2-short'}])), 'a tie is not a gain')
        self.assertEqual(s(60, 95, [{'id': 'h2-short'}, {'id': 'desktop-no-empty-screens'}])['hard'], ['desktop-no-empty-screens'])

    def decide(self, taste, contract, winner, rival_taste, failed=()):
        d = tempfile.mkdtemp(); out = os.path.join(d, 'page.html'); Path(out).write_text('<html></html>')
        grade = lambda: ({'score': contract, 'failed': [{'id': i, 'detail': ''} for i in failed]}, {'score': taste, 'verdict': 'v', 'fixes': []})
        with patch.object(run, 'compose_first_screen', lambda *a: {'drawn': True, 'ir': {}}):
            return run.composed_candidate(d, out, 76, winner.get('broken'), grade, None, lambda: {'taste': rival_taste, 'score': round(0.55 * rival_taste + 0.45 * winner['contract'])}, winner)

    def test_a_composed_page_stands_on_taste_and_never_on_a_higher_contract(self):
        winner = {'taste': 58, 'contract': 92, 'broken': []}
        kept = self.decide(62, 90, winner, rival_taste=60); self.assertTrue(kept['kept']); self.assertEqual((kept['decided_by'], kept['reference_taste']), ('gates', 60))
        refused = self.decide(56, 100, winner, rival_taste=60)   # blended it would be 76 against 74: the contract would have carried it
        self.assertFalse(refused['kept']); self.assertIn('56', refused['why']); self.assertIn('60', refused['why'])
        lost = self.decide(70, 84, winner, rival_taste=60); self.assertFalse(lost['kept']); self.assertIn('technical bar', lost['why'])
        broke = self.decide(80, 95, winner, rival_taste=60, failed=['mobile-no-overflow']); self.assertFalse(broke['kept']); self.assertIn('mobile-no-overflow', broke['why'])
        with patch.object(run, 'DECIDE', 'blend'): self.assertTrue(self.decide(56, 100, winner, rival_taste=60)['kept'], 'the old rule, kept behind SWARM_DECIDE=blend')

    def test_measurement_is_off_under_tests_and_never_stops_a_job(self):
        with patch.dict(os.environ, {'LIVETEST': '1'}, clear=False): os.environ.pop('SWARM_MEASURE', None); self.assertIsNone(run.measured('/nowhere', '/nowhere/page.html'))
        with patch.dict(os.environ, {'SWARM_MEASURE': '1'}), patch.object(run.MEASURE, 'measure', side_effect=RuntimeError('no browser')): self.assertIsNone(run.measured('/nowhere', __file__))
        card = run.scorecard({'rounds': [{'k': 1, 'taste': 60, 'contract': 95, 'score': 76, 'broken': [], 'levels': {'typography': 3}, 'page_level': 2.5}]}, 1,
                             {'findings': ST.findings(page(view(surfaces={'rules': {'on_elements': 40, 'by_pseudo_elements': 0, 'hr': 0}}))), 'technical': ST.technical(page())})
        self.assertEqual((card['measured']['findings'], card['measured']['ids'], card['measured']['checks_failed']), (1, ['CMP-09@1440'], []))
        self.assertEqual((card['creative']['level'], card['creative']['page_level']), (2, 2.5))


if __name__ == '__main__': unittest.main()
