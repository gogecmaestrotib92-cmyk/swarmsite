import importlib.util
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('render_bp_pinned_features', ROOT / 'lib/render/render_bp.py')
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


class Section(HTMLParser):
    def __init__(self, section_id):
        super().__init__()
        self.section_id = section_id
        self.inside = False
        self.attrs = None
        self.slides = 0
        self.images = 0
        self.sources = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section' and attrs.get('id') == self.section_id:
            self.inside = True
            self.attrs = attrs
        if self.inside:
            if tag == 'div' and 'ps-s' in attrs.get('class', '').split():
                self.slides += 1
            if tag == 'img':
                self.images += 1
                self.sources.append(attrs.get('src'))

    def handle_endtag(self, tag):
        if tag == 'section' and self.inside:
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.text.append(data)


class PinnedFeatureTests(unittest.TestCase):
    def render_section(self, count, blueprint='white-desert', item_images=False):
        direction = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        features = next(beat for beat in direction['beats'] if beat['type'] == 'features')
        features['features'] = [
            {'title': '24/7 support' if i == 0 else f'Offer {i + 1}', 'body': f'Description {i + 1}'}
            for i in range(count)
        ]
        features['ui'] = {'move': 'pinned-sequence'}
        features['image'] = 'long-table'
        if item_images:
            features['features'][0]['image'] = 'long-table'
            features['features'][1]['image'] = 'basta-table'
        images = json.loads((ROOT / 'tests/images.sample.json').read_text())
        for image in images:
            image['detail'] = True
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'direction.json').write_text(json.dumps(direction))
            (folder / 'images.json').write_text(json.dumps(images))
            output = folder / 'page.html'
            render.build(directory, blueprint, str(output))
            section = Section(features['id'])
            section.feed(output.read_text())
            return section

    def test_features_preserve_numeric_title_without_misattributed_photo(self):
        # no per-feature pictures: the section is not pinned (a text-only pinned ladder is what the critic
        # kept flagging) but every feature and its numeric title stay visible in the cards fallback
        section = self.render_section(4)
        self.assertNotEqual(section.attrs.get('data-sig'), 'pinned')
        self.assertEqual(section.slides, 0)
        self.assertLessEqual(section.images, 1)  # the cards fallback may keep the assigned section picture as its lead
        for text in ['24/7 support', 'Offer 2', 'Offer 3', 'Offer 4',
                     'Description 1', 'Description 2', 'Description 3', 'Description 4']:
            self.assertIn(text, section.text)

    def test_single_and_six_features_remain_visible_without_pinning(self):
        for count, blueprint in ((1, 'white-desert'), (6, 'white-desert'), (6, 'cerebrium')):
            with self.subTest(count=count, blueprint=blueprint):
                section = self.render_section(count, blueprint)
                self.assertNotEqual(section.attrs.get('data-sig'), 'pinned')
                self.assertEqual(section.slides, 0)
                self.assertIn('24/7 support', section.text)
                self.assertIn(f'Description {count}', section.text)

    def test_explicit_item_images_are_preserved_without_section_photo_repeats(self):
        section = self.render_section(4, item_images=True)
        images = json.loads((ROOT / 'tests/images.sample.json').read_text())
        expected = [image['data'] for image in images if image['id'] in ('long-table', 'basta-table')]
        self.assertEqual(section.slides, 4)
        self.assertEqual(section.images, 2)
        self.assertCountEqual(section.sources, expected)


if __name__ == '__main__':
    unittest.main()
