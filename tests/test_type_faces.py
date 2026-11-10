"""The registry of display typefaces: every face is one a page may ship, and every number a headline is sized from is there.
Whether Google Fonts still serves each spec and how wide each face really sets is checked over the network by
`node lib/type/measure.mjs` (not part of this suite)."""
import json, re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'type'))
import faces as FACES

# Faces sold under a commercial licence that the benchmark's reference sites use. None may be in the registry.
COMMERCIAL = ('suisse', 'gt america', 'gt walsheim', 'söhne', 'sohne', 'aeonik', 'abc favorit', 'abc diatype', 'neue haas', 'helvetica', 'graphik', 'canela', 'tiempos',
              'pp neue', 'pp editorial', 'pp fragment', 'twk', 'everett', 'lausanne', 'druk', 'apercu', 'circular', 'proxima', 'avenir', 'futura', 'gotham', 'akkurat')


class Registry(unittest.TestCase):
    def test_every_face_is_complete_and_named_once(self):
        faces = FACES.all(); self.assertGreaterEqual(len(faces), 12)
        self.assertEqual(len({f['id'] for f in faces}), len(faces)); self.assertEqual(len({f['family'] for f in faces}), len(faces))
        for f in faces:
            with self.subTest(face=f['id']):
                self.assertRegex(f['id'], r'^[a-z][a-z0-9-]{2,24}$'); self.assertIn(f['kind'], ('serif', 'sans'))
                lo, hi = f['weights']; self.assertTrue(100 <= lo <= f['display'] <= hi <= 900)
                self.assertIsInstance(f['italic'], bool); self.assertRegex(f['ls'], r'^-?0(\.\d+)?em$'); self.assertTrue(0.85 <= f['lh'] <= 1.2)
                self.assertTrue(0.3 <= f['avg'] <= 0.8 and f['avg'] <= f['avg_upper'] <= 0.9, 'widths are measured (lib/type/measure.mjs --write), in em')
                self.assertGreater(len(f['voice']), 30); self.assertGreaterEqual(len(f['suits']), 3)

    def test_the_stylesheet_spec_asks_for_what_the_face_says_it_has(self):
        for f in FACES.all():
            with self.subTest(face=f['id']):
                self.assertRegex(f['gf'], r'^[A-Za-z0-9+]+(:[a-z,]+@[0-9.;,]+)?$', 'a css2 family spec and nothing else: it goes into a URL')
                self.assertEqual(f['gf'].split(':')[0], f['family'].replace(' ', '+'))
                self.assertEqual('ital' in f['gf'], f['italic'], 'italic is claimed exactly when the stylesheet loads one')
                lo, hi = f['weights']
                if lo != hi: self.assertIn(f'{lo}..{hi}', f['gf'])
                self.assertEqual(FACES.link(f), f'https://fonts.googleapis.com/css2?family={f["gf"]}&display=swap')
                self.assertRegex(FACES.stack(f), r"^'[A-Za-z0-9 ]+',[A-Za-z, -]+$", 'the family goes into CSS: letters, digits and spaces only')

    def test_no_commercial_face_is_in_the_registry(self):
        for f in FACES.all():
            for name in COMMERCIAL: self.assertNotIn(name, f['family'].lower(), f'{f["family"]} is not free to ship')
        about = json.loads((ROOT / 'lib' / 'type' / 'faces.json').read_text())['about']
        self.assertIn('Open Font License', about)

    def test_lookup_and_the_width_of_a_face_nobody_measured(self):
        self.assertEqual(FACES.get('fraunces')['family'], 'Fraunces'); self.assertIsNone(FACES.get('nope')); self.assertIsNone(FACES.get(None))
        self.assertEqual(FACES.advance(None), FACES.DEFAULT_ADVANCE)
        self.assertGreaterEqual(FACES.DEFAULT_ADVANCE, max(f['avg'] for f in FACES.all() if f['id'] != 'unbounded'), 'an unknown face is assumed wide, so a headline sized for it never overflows')
        anton = FACES.get('anton'); self.assertEqual(FACES.advance(anton, upper=True), anton['avg_upper']); self.assertEqual(FACES.advance(anton), anton['avg'])


if __name__ == '__main__':
    unittest.main()
