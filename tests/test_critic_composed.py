"""The critic and a recomposed page: it is told what each redrawn section now is instead of the move the direction named,
and where a decision hangs on its score it reads twice. No network: the model call is a stand-in."""
import os, sys, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'qa')); sys.path.insert(0, str(ROOT / 'lib'))
import critic as C

PAGE = ('<section class="sec hero ir" id="top" data-ir="0.2"></section><section class="sec indexlist band-alt lc lc-ledger" id="features" data-lc="0.2"></section>'
        '<section class="sec photo pc pc-f-bleed" id="room" data-pc="0.2" data-form="bleed" data-over="1" style="x"></section><section class="sec ledger wc wc-f-columns" id="menu" data-wc="0.2" data-form="columns"></section>'
        '<section class="sec story band-paper" id="story"></section><section class="sec cards pc" id="odd" data-pc="0.2" data-form="new-form"></section>')


class Recomposed(unittest.TestCase):
    def test_every_redrawn_section_is_named_for_what_it_now_is(self):
        said = C.recomposed(PAGE); self.assertEqual(list(said), ['top', 'features', 'room', 'menu', 'odd'], 'a section the template drew is not in the list')
        self.assertIn('ruled rows', said['features']); self.assertIn('runs off one edge', said['room']); self.assertIn('two columns', said['menu']); self.assertIn('first screen', said['top'])
        self.assertEqual(said['odd'], 'a composed picture section', 'a form this file does not know yet is still said to be composed'); self.assertEqual(C.recomposed('<section class="sec hero" id="top"></section>'), {})

    def test_the_sections_run_together_as_a_gallery_are_all_named(self):
        row = ('<section class="sec photo pc pc-f-gallery" id="terrace" data-pc="0.2" data-form="gallery"><div class="wrap pc-gal"><article class="pc-gi"><h2>Terrace</h2></article>'
               '<article class="pc-gi" id="hall"><h2>Hall</h2></article><article class="pc-gi" id="lounge"><h2>Lounge</h2></article></div></section><section class="sec story" id="after"><article class="pc-gi" id="not-in-a-row"></article></section>')
        said = C.recomposed(row); self.assertEqual(list(said), ['terrace', 'hall', 'lounge']); self.assertIn('one row', said['terrace']); self.assertEqual(said['hall'], 'one picture of the row that begins at "terrace"')

    def test_every_form_the_composers_draw_has_its_words(self):
        sys.path.insert(0, str(ROOT / 'lib' / 'compose'))
        import lists, pictures, words
        self.assertEqual(set(lists.FORMS), set(C.LIST_FORMS)); self.assertTrue(set(pictures.FORMS) <= set(C.PICTURE_FORMS)); self.assertEqual(set(words.FORMS), set(C.WORD_FORMS))

    def test_the_prompt_says_what_studio_work_is_and_what_a_linked_form_is(self):
        self.assertIn('WHAT SEPARATES STUDIO WORK', C.SYSTEM); self.assertIn('ruled rows', C.SYSTEM); self.assertEqual(set(C.TOOL['input_schema']['properties']['studio']['properties']), {'typography', 'composition', 'imagery', 'rhythm', 'concept'})
        source = (ROOT / 'lib/qa/critic.py').read_text(); self.assertIn('that is by design and not a defect', source); self.assertNotIn('in place of an A form beat', source, 'the sentence that told the critic the opposite of what was meant')


class TwoReadings(unittest.TestCase):
    def read(self, *scores):
        queue = list(scores)
        def one(slug_dir, html, model, fast, files):
            score = queue.pop(0)
            if score is None: return {'score': -1, 'fixes': [], 'verdict': 'no report'}
            return {'score': score, 'axes': {'design': score, 'craft': score + 2}, 'studio': {'typography': score - 4}, 'verdict': f'read at {score}', 'fixes': [{'op': 'note', 'reason': str(score)}]}
        with patch.object(C, 'shots', lambda html, outdir, fast=False: ['a.png']), patch.object(C, 'critique', one): return C.critique_twice('job', 'page.html')

    def test_the_score_is_the_mean_and_the_words_are_the_harder_readings(self):
        r = self.read(60, 52); self.assertEqual((r['score'], sorted(r['readings'])), (56, [52, 60])); self.assertEqual(r['axes'], {'design': 56, 'craft': 58}); self.assertEqual(r['studio'], {'typography': 52})
        self.assertEqual(r['verdict'], 'read at 52'); self.assertEqual(r['fixes'][0]['reason'], '52')

    def test_one_reading_that_fails_leaves_the_other_and_none_leaves_none(self):
        r = self.read(None, 64); self.assertEqual((r['score'], r['readings']), (64, [64])); self.assertEqual(self.read(None, None)['score'], -1)
        with patch.object(C, 'shots', lambda html, outdir, fast=False: []): self.assertEqual(C.critique_twice('job', 'page.html')['verdict'], 'no screenshots')


if __name__ == '__main__': unittest.main()
