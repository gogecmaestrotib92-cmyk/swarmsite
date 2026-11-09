"""The one generated picture a page may carry is a backdrop behind a statement — never a picture in a slot."""
import base64, io, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def picture(colour='#223344'):
    im = Image.new('RGB', (1200, 800), colour); ImageDraw.Draw(im).ellipse((300, 200, 900, 600), fill='#556677')
    out = io.BytesIO(); im.save(out, 'JPEG'); return 'data:image/jpeg;base64,' + base64.b64encode(out.getvalue()).decode()


class AtmosphereTest(unittest.TestCase):
    def render(self, edit, images_only_gen=False):
        with tempfile.TemporaryDirectory() as temp:
            job = Path(temp)
            for name in ('direction', 'images', 'inventory', 'assets'):
                src = ROOT / 'tests' / f'{name}.sample.json'
                if src.is_file(): shutil.copy(src, job / f'{name}.json')
            d = json.loads((job / 'direction.json').read_text()); images = json.loads((job / 'images.json').read_text())
            if images_only_gen: images = []
            images.append({'id': 'gen-q', 'w': 1200, 'h': 800, 'gen': True, 'src': 'commissioned', 'data': picture()})
            edit(d)
            (job / 'direction.json').write_text(json.dumps(d)); (job / 'images.json').write_text(json.dumps(images))
            out = job / 'page.html'
            r = subprocess.run([sys.executable, str(ROOT / 'lib/render/render_bp.py'), str(job), 'butter', str(out)], capture_output=True, text=True, env={**os.environ, 'LIVETEST': '1'})
            self.assertEqual(r.returncode, 0, r.stderr)
            return out.read_text()

    def test_backdrop_sits_behind_the_statement_and_nowhere_else(self):
        def edit(d):
            for b in d['beats']:
                if b['type'] == 'quote': b['atmos'] = 'gen-q'
        html = self.render(edit)
        self.assertEqual(html.count('class="atmos-bg"'), 1)
        self.assertRegex(html, r'<section class="sec (statement|typewall) atmos band-[a-z]+" id="q"[^>]*>\s*<figure class="atmos-bg" data-move="parallax"')
        # the generated pixels appear once: behind the words, not again in a slot
        gen_data = picture()
        self.assertEqual(html.count(gen_data), 1)

    def test_generated_picture_assigned_to_a_slot_is_never_placed(self):
        def edit(d):
            for b in d['beats']:
                if b['type'] == 'features': b['image'] = 'gen-q'
        html = self.render(edit)
        self.assertNotIn(picture(), html)  # the slot stays typographic; a generated picture is not an illustration

    def test_generated_picture_never_becomes_the_hero_from_the_pool(self):
        def edit(d):
            d['hero']['media'] = ''
            for b in d['beats']: b.pop('image', None); b.pop('ui', None)
        html = self.render(edit, images_only_gen=True)
        self.assertNotIn(picture(), html)
        self.assertIn('class="sec ladder', html)  # picture-less steps become the ladder
        self.assertIn('class="sec indexlist', html)  # picture-less features become the index
        self.assertNotIn('<figure class="atmos-bg"', html)


if __name__ == '__main__':
    unittest.main()
