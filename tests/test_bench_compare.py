"""The blind comparison must hide which engine made which page, and the tally must credit the right one."""
import json, os, shutil, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bench'))
import compare as C


class BlindComparisonTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.mkdtemp(); self.old = (C.HERE, C.RUNS)
        C.HERE = self.temp; C.RUNS = os.path.join(self.temp, 'runs')
        sites = [{'id': f's{i}', 'url': f'https://example{i}.test/', 'blueprint': 'butter'} for i in range(4)]
        Path(self.temp, 'sites.json').write_text(json.dumps({'sites': sites}))
        for variant in ('alpha', 'beta'):
            for s in sites:
                d = Path(C.RUNS, variant, s['id']); d.mkdir(parents=True)
                for viewport in ('desktop', 'mobile'): (d / f'{viewport}.jpg').write_bytes(f'{variant}-{s["id"]}-{viewport}'.encode())
        # one site renders identically in both variants: nothing to judge
        for viewport in ('desktop', 'mobile'): Path(C.RUNS, 'beta', 's3', f'{viewport}.jpg').write_bytes(f'alpha-s3-{viewport}'.encode())

    def tearDown(self):
        C.HERE, C.RUNS = self.old; shutil.rmtree(self.temp, ignore_errors=True)

    def test_page_names_no_variant_and_the_key_matches_the_pictures(self):
        out, n, skipped = C.build('alpha', 'beta', seed=3)
        self.assertEqual(n, 6); self.assertEqual(len(skipped), 2)
        page = Path(out, 'index.html').read_text()
        self.assertNotIn('alpha', page); self.assertNotIn('beta', page)
        key = json.loads(Path(out, 'key.json').read_text())
        sides = set()
        for pid, pair in key['pairs'].items():
            left = Path(out, f'{pid}-l.jpg').read_bytes().decode(); right = Path(out, f'{pid}-r.jpg').read_bytes().decode()
            self.assertTrue(left.startswith(pair['left'] + '-' + pair['site'])); self.assertTrue(right.startswith(pair['right'] + '-' + pair['site']))
            sides.add(pair['left'])
        self.assertEqual(sides, {'alpha', 'beta'})  # with this seed both variants appear on the left: the side tells nothing

    def test_same_seed_same_page_and_score_credits_the_variant_not_the_side(self):
        out, _, _ = C.build('alpha', 'beta', seed=3); first = Path(out, 'index.html').read_text(); key = json.loads(Path(out, 'key.json').read_text())
        out, _, _ = C.build('alpha', 'beta', seed=3); self.assertEqual(first, Path(out, 'index.html').read_text())
        answers = {pid: {'typography': 'left' if pair['left'] == 'beta' else 'right', 'professional': 'same'} for pid, pair in key['pairs'].items()}
        path = Path(self.temp, 'answers.json'); path.write_text(json.dumps({'comparison': key['comparison'], 'answers': answers}))
        report = C.score(out, str(path))
        self.assertEqual(report['questions']['typography']['beta'], 6); self.assertEqual(report['questions']['typography']['alpha'], 0)
        self.assertEqual(report['questions']['typography']['share_beta'], 1.0)
        self.assertEqual(report['questions']['professional']['no_difference'], 6); self.assertIsNone(report['questions']['professional']['share_beta'])
        low, high = report['questions']['typography']['interval_95']
        self.assertTrue(0.5 < low < 1.0 and high == 1.0)  # six of six is not certainty: the interval says so

    def test_answers_from_another_comparison_are_refused(self):
        out, _, _ = C.build('alpha', 'beta', seed=3)
        path = Path(self.temp, 'answers.json'); path.write_text(json.dumps({'comparison': 'someone-else', 'answers': {}}))
        with self.assertRaises(SystemExit): C.score(out, str(path))

    def test_interval_is_honest_at_small_n(self):
        self.assertEqual(C.interval(0, 0), (0.0, 0.0))
        low, high = C.interval(13, 20)
        self.assertTrue(low < 0.5 < high)  # 65% of 20 does not yet clear 50%
        low, high = C.interval(98, 150)
        self.assertTrue(low > 0.5)  # 65% of 150 does


if __name__ == '__main__':
    unittest.main()
