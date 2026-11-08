import base64
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))
from visual_quality import empty_visual

spec = importlib.util.spec_from_file_location('swarm_empty_visual_agents', ROOT / 'lib/swarm/agents.py')
agents = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agents)


def image_data(color, *, mark=False):
    image = Image.new('RGBA', (1000, 600), color)
    if mark:
        # A tiny but real mark on an otherwise white minimalist image.
        ImageDraw.Draw(image).rectangle((300, 280, 302, 282), fill=(249, 249, 249, 255))
    output = io.BytesIO()
    image.save(output, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(output.getvalue()).decode()


class EmptyVisualsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.white = image_data((255, 255, 255, 255))
        cls.black = image_data((0, 0, 0, 255))
        cls.transparent = image_data((255, 255, 255, 0))
        cls.minimal = image_data((255, 255, 255, 255), mark=True)
        cls.offwhite = image_data((254, 254, 254, 255))
        cls.partial = image_data((255, 255, 255, 128))

    def test_only_definitely_empty_pixels_are_rejected(self):
        for data in (self.white, self.black, self.transparent):
            self.assertTrue(empty_visual({'data': data}))
        for data in (self.minimal, self.offwhite, self.partial, 'data:image/svg+xml,<svg/>'):
            self.assertFalse(empty_visual({'data': data}))

    def test_empty_proposals_cannot_replace_owned_images(self):
        imgs = {name: {'id': name, 'data': data} for name, data in [('good', self.minimal), ('white', self.white), ('transparent', self.transparent)]}
        d = {'hero': {'media': 'good'}, 'beats': [{'id': 'product', 'type': 'features', 'image': 'good'}]}
        # Separate hero and beat ownership to avoid the legacy duplicate rule.
        d['beats'][0]['image'] = ''
        agents.apply_visual_assignments(d, imgs, hero='white', slots=[{'beat': 'product', 'image': 'transparent'}])
        self.assertEqual(d['hero']['media'], 'good')
        self.assertEqual(d['beats'][0]['image'], '')

    def test_renderer_does_not_steal_another_sections_image_for_empty_hero(self):
        d = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        d['kind'] = 'software'
        d['hero']['media'] = 'blank'
        d['hero']['ui'] = {'move': 'split'}
        d['beats'] = [
            {'id': 'empty-shot', 'type': 'features', 'h2': 'First', 'features': [{'title': 'A', 'body': 'B'}], 'image': 'blank', 'ui': {'move': 'cards', 'lead': 'blank'}},
            {'id': 'valid-shot', 'type': 'features', 'h2': 'Second', 'features': [{'title': 'C', 'body': 'D'}], 'image': 'minimal', 'ui': {'move': 'cards', 'lead': 'minimal'}},
        ]
        imgs = [{'id': 'blank', 'w': 1000, 'h': 600, 'shot': True, 'data': self.white},
                {'id': 'minimal', 'w': 1000, 'h': 600, 'shot': True, 'data': self.minimal}]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, data in [('direction.json', d), ('images.json', imgs), ('inventory.json', {})]:
                (root / name).write_text(json.dumps(data))
            out = root / 'page.html'
            result = subprocess.run([sys.executable, str(ROOT / 'lib/render/render_bp.py'), directory, 'butter', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text()
            self.assertFalse(self.white in html, 'blank screenshot should not render')
            self.assertTrue(self.minimal in html, 'valid minimalist visual should remain')
            hero = html.split('<section', 1)[1].split('</section>', 1)[0]
            self.assertNotIn('<img', hero)

    def test_blank_poster_does_not_remove_independent_hero_video(self):
        d = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        d['hero']['media'] = 'blank'
        d['hero']['ui'] = {'move': 'photo'}
        d['beats'] = []
        images = [{'id': 'blank', 'w': 1000, 'h': 600, 'data': self.white}]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, data in [('direction.json', d), ('images.json', images), ('inventory.json', {})]:
                (root / name).write_text(json.dumps(data))
            # Tag preservation is checked here; real playback is separately
            # verified in Chrome with a valid MP4.
            (root / 'hero.mp4').write_bytes(b'video-fixture')
            out = root / 'page.html'
            result = subprocess.run([sys.executable, str(ROOT / 'lib/render/render_bp.py'), directory, 'tengile', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            hero = out.read_text().split('<section', 1)[1].split('</section>', 1)[0]
            self.assertIn('<video ', hero)
            self.assertIn(base64.b64encode(b'video-fixture').decode(), hero)
            self.assertNotIn('poster=', hero)
            self.assertFalse(self.white in hero)


if __name__ == '__main__':
    unittest.main()
