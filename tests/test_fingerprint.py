"""The structural fingerprint says whether two pages share a skeleton, and nothing else."""
import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'qa'))
import fingerprint as F


def page(*sections):
    return '<html><body><nav></nav>' + ''.join(sections) + '<footer></footer></body></html>'


class FingerprintTest(unittest.TestCase):
    def test_signature_reads_forms_in_order_and_ignores_colour(self):
        html = page('<section class="sec hero split" id="top"><h1>One</h1></section>',
                    '<section class="sec sticky band-dark" data-sig="sticky"><p>a</p></section>',
                    '<section class="sec cards compact band-alt"><p>b</p></section>',
                    '<section class="sec cta cta-pic band-dark"></section>')
        self.assertEqual(F.signature(html), ['hero.split', 'sticky[sticky]', 'cards', 'cta.cta-pic'])
        self.assertEqual(F.body(F.signature(html)), ['sticky[sticky]', 'cards'])

    def test_words_pictures_and_bands_do_not_change_the_fingerprint(self):
        a = page('<section class="sec hero" id="top"><h1>First site</h1></section>', '<section class="sec cards band-paper"><img src="a.jpg"></section>')
        b = page('<section class="sec hero" id="top"><h1>Another business entirely</h1></section>', '<section class="sec cards band-dark"><img src="b.jpg"><p>more words</p></section>')
        self.assertEqual(F.fingerprint(a)['digest'], F.fingerprint(b)['digest'])
        self.assertEqual(F.similarity(F.signature(a), F.signature(b)), 1.0)

    def test_a_different_skeleton_is_less_similar(self):
        a = ['sticky[sticky]', 'story', 'statement', 'cards']
        b = ['indexlist', 'twocol', 'typewall[typewall]', 'numbers']
        c = ['sticky[sticky]', 'story', 'cards', 'statement']
        self.assertEqual(F.similarity(a, a), 1.0)
        self.assertEqual(F.similarity(a, b), 0.0)
        self.assertTrue(0 < F.similarity(a, c) < 1)
        self.assertEqual(F.similarity([], []), 1.0)

    def test_section_like_text_inside_scripts_is_not_a_section(self):
        html = page('<section class="sec hero"></section>', '<script>const s = \'<section class="sec fake">\';</script>', '<section class="sec faq"></section>')
        self.assertEqual(F.signature(html), ['hero', 'faq'])

    def test_closing_sections_are_not_part_of_the_body(self):
        sig = ['hero.has-media.photo', 'ledger', 'overlay.cta-ov[parallax]', 'archive']
        self.assertEqual(F.body(sig), ['ledger'])

    def test_compare_counts_distinct_skeletons(self):
        same = page('<section class="sec hero"></section>', '<section class="sec cards"></section>')
        other = page('<section class="sec hero"></section>', '<section class="sec ledger"></section>')
        report = F.compare({'a': same, 'b': same, 'c': other})
        self.assertEqual(report['distinct_bodies'], 2)
        self.assertEqual(report['max_body_similarity'], 1.0)
        self.assertEqual(len(report['pairs']), 3)

    def test_real_render_has_a_hero_first_and_a_stable_fingerprint(self):
        with tempfile.TemporaryDirectory() as temp:
            job = Path(temp)
            for name in ('direction', 'images', 'inventory', 'assets'):
                src = ROOT / 'tests' / f'{name}.sample.json'
                if src.is_file(): shutil.copy(src, job / f'{name}.json')
            prints = []
            for attempt in ('one', 'two'):
                out = job / f'{attempt}.html'
                r = subprocess.run([sys.executable, str(ROOT / 'lib/render/render_bp.py'), str(job), 'butter', str(out)], capture_output=True, text=True, env={**os.environ, 'LIVETEST': '1'})
                self.assertEqual(r.returncode, 0, r.stderr)
                prints.append(F.fingerprint(out.read_text()))
            self.assertTrue(prints[0]['hero'].startswith('hero'))
            self.assertGreaterEqual(len(prints[0]['body']), 3)
            self.assertEqual(prints[0]['digest'], prints[1]['digest'])
            cli = subprocess.run([sys.executable, str(ROOT / 'lib/qa/fingerprint.py'), str(job / 'one.html'), '--write', str(job / 'fingerprint.json')], capture_output=True, text=True)
            self.assertEqual(cli.returncode, 0, cli.stderr)
            self.assertEqual(json.loads((job / 'fingerprint.json').read_text())['digest'], prints[0]['digest'])


if __name__ == '__main__':
    unittest.main()
