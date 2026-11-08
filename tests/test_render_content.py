import importlib.util
import base64
import io
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('render_bp', ROOT / 'lib/render/render_bp.py')
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


class SectionText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = {}
        self.images = {}
        self.attributes = {}
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == 'section':
            self.current = dict(attrs).get('id')
            if self.current:
                self.sections[self.current] = []
                self.images[self.current] = []
                self.attributes[self.current] = dict(attrs)
        if tag == 'img' and self.current:
            self.images[self.current].append(dict(attrs).get('src'))

    def handle_endtag(self, tag):
        if tag == 'section': self.current = None

    def handle_data(self, data):
        if self.current: self.sections[self.current].append(data)


class RenderContentTests(unittest.TestCase):
    def test_cards_show_only_valid_images_associated_with_their_own_items(self):
        from PIL import Image, ImageDraw

        direction = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        beat = next(beat for beat in direction['beats'] if beat['type'] == 'features')
        beat['image'] = 'long-table'
        beat['ui'] = {'move': 'cards', 'lead': ''}
        images = json.loads((ROOT / 'tests/images.sample.json').read_text())
        for image in images: image['detail'] = True
        photo = next(image['data'] for image in images if image['id'] == 'long-table')

        def image_data(image):
            output = io.BytesIO()
            image.save(output, format='JPEG')
            return 'data:image/jpeg;base64,' + base64.b64encode(output.getvalue()).decode()

        texture = Image.new('RGB', (1000, 600), (15, 15, 15))
        dark_photo = Image.new('RGB', (1000, 600), (10, 10, 10))
        ImageDraw.Draw(dark_photo).rectangle((250, 150, 750, 450), fill=(70, 70, 70))
        dark_data = image_data(dark_photo)
        images.extend([
            {'id': 'texture', 'w': 1000, 'h': 600, 'bg': True, 'lum': None, 'detail': True, 'data': image_data(texture)},
            {'id': 'dark-photo', 'w': 1000, 'h': 600, 'bg': True, 'lum': 25, 'detail': True, 'data': dark_data},
        ])
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'images.json').write_text(json.dumps(images))
            output = folder / 'page.html'
            (folder / 'direction.json').write_text(json.dumps(direction))
            render.build(directory, 'white-desert', str(output))
            sections = SectionText()
            sections.feed(output.read_text())
            self.assertEqual(sections.images[beat['id']], [])

            for feature, image_id in zip(beat['features'], ('long-table', 'texture', 'dark-photo')):
                feature['image'] = image_id
            (folder / 'direction.json').write_text(json.dumps(direction))
            render.build(directory, 'white-desert', str(output))
            sections = SectionText()
            sections.feed(output.read_text())
            self.assertEqual(sections.images[beat['id']], [photo, dark_data])

    def test_numeric_ticker_does_not_show_its_saved_photo_but_story_can(self):
        direction = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        beat = next(beat for beat in direction['beats'] if beat['type'] == 'cells')
        beat['image'] = 'long-table'
        images = json.loads((ROOT / 'tests/images.sample.json').read_text())
        for image in images: image['detail'] = True
        photo = next(image['data'] for image in images if image['id'] == 'long-table')
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'images.json').write_text(json.dumps(images))
            for move in ('marquee', 'story'):
                beat['ui']['move'] = move
                (folder / 'direction.json').write_text(json.dumps(direction))
                output = folder / 'page.html'
                render.build(directory, 'white-desert', str(output))
                sections = SectionText()
                sections.feed(output.read_text())
                if move == 'marquee':
                    self.assertEqual(sections.images[beat['id']], [])
                else:
                    self.assertIn(photo, sections.images[beat['id']])
                self.assertEqual(json.loads((folder / 'direction.json').read_text())['beats'][direction['beats'].index(beat)]['image'], 'long-table')

    def test_photo_story_keeps_its_image_and_captions(self):
        direction = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        photo = {'id': 'room', 'type': 'photo', 'h2': 'The room',
                 'lede': 'A place for gatherings.', 'image': 'long-table',
                 'cap': ['Thirty guests', 'Call to book'], 'band': 'dark',
                 'ui': {'move': 'story'}}
        direction['beats'].insert(0, photo)
        images = json.loads((ROOT / 'tests/images.sample.json').read_text())
        for image in images:
            image['detail'] = True
            if image['id'] == 'long-table':
                from PIL import Image
                original = base64.b64decode(image['data'].split(',', 1)[1])
                with Image.open(io.BytesIO(original)) as source:
                    scaled = source.convert('RGB').resize((800, 600))
                data = io.BytesIO()
                scaled.save(data, format='JPEG')
                image['data'] = 'data:image/jpeg;base64,' + base64.b64encode(data.getvalue()).decode()
                image['w'] = 1200  # legacy metadata can describe the image before downsampling
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'direction.json').write_text(json.dumps(direction))
            (folder / 'images.json').write_text(json.dumps(images))
            output = folder / 'page.html'
            render.build(directory, 'white-desert', str(output))
            sections = SectionText()
            html = output.read_text()
            sections.feed(html)
        self.assertIn('story', sections.attributes['room']['class'].split())
        self.assertIn('band-dark', sections.attributes['room']['class'].split())
        self.assertIn(next(i['data'] for i in images if i['id'] == 'long-table'), sections.images['room'])
        self.assertIn('Thirty guests', sections.sections['room'])
        self.assertIn('Call to book', sections.sections['room'])
        self.assertIn('--story-image-max:1080px', html)

    def test_explicit_beat_band_is_not_replaced_by_recipe_band(self):
        direction = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        cells = next(beat for beat in direction['beats'] if beat['type'] == 'cells')
        cells['band'] = 'paper'
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'direction.json').write_text(json.dumps(direction))
            (folder / 'images.json').write_bytes((ROOT / 'tests/images.sample.json').read_bytes())
            output = folder / 'page.html'
            render.build(directory, 'cerebrium', str(output))
            sections = SectionText()
            sections.feed(output.read_text())
        self.assertIn('band-paper', sections.attributes[cells['id']]['class'].split())
        self.assertNotIn('band-dark', sections.attributes[cells['id']]['class'].split())

    def test_low_resolution_sticky_facts_and_compact_contact_are_readable(self):
        direction = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        facts = next(beat for beat in direction['beats'] if beat['type'] == 'facts')
        facts.update({'image': 'long-table', 'ui': {'move': 'sticky-product'}})
        form = next(beat for beat in direction['beats'] if beat['type'] == 'form')
        form['image'] = ''
        form['h2'] = 'Reserve a table'
        images = json.loads((ROOT / 'tests/images.sample.json').read_text())
        for image in images:
            image['detail'] = True
            if image['id'] == 'long-table': image['w'] = 500
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'direction.json').write_text(json.dumps(direction))
            (folder / 'images.json').write_text(json.dumps(images))
            (folder / 'inventory.json').write_bytes((ROOT / 'tests/inventory.sample.json').read_bytes())
            output = folder / 'page.html'
            render.build(directory, 'white-desert', str(output))
            html = output.read_text()
            sections = SectionText()
            sections.feed(html)
        self.assertIn('numbers', sections.attributes[facts['id']]['class'].split())
        for number, caption in facts['facts']:
            self.assertIn(number, sections.sections[facts['id']])
            self.assertIn(caption, sections.sections[facts['id']])
        self.assertIn('font-size:clamp(42px,6vw,88px)', html)
        self.assertIn('https://example.test/reservation', html)

    def test_recipe_honours_explicit_moves_for_matched_and_fallback_beats(self):
        direction = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        quote = next(beat for beat in direction['beats'] if beat['type'] == 'quote')
        quote.update({'big': 'A clear idea', 'body': 'An explanatory caption stays visible.', 'ui': {'move': 'type-wall'}})
        facts = next(beat for beat in direction['beats'] if beat['type'] == 'facts')
        facts.update({'image': 'long-table', 'ui': {'move': 'sticky-product'}})
        direction['beats'].append({'id': 'ticker-proof', 'type': 'facts',
                                   'facts': [['One', 'first detail'], ['Two', 'second detail']],
                                   'ui': {'move': 'marquee'}})
        images = json.loads((ROOT / 'tests/images.sample.json').read_text())
        for image in images: image['detail'] = True
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'direction.json').write_text(json.dumps(direction))
            (folder / 'images.json').write_text(json.dumps(images))
            output = folder / 'page.html'
            render.build(directory, 'white-desert', str(output))
            sections = SectionText()
            html = output.read_text()
            sections.feed(html)
        self.assertEqual(sections.attributes[quote['id']].get('data-sig'), 'typewall')
        self.assertIn('class="wrap tw-prominent"', html)
        self.assertIn('An explanatory caption stays visible.', ' '.join(sections.sections[quote['id']]))
        self.assertEqual(sections.attributes[facts['id']].get('data-sig'), 'sticky')
        self.assertEqual(sections.attributes['ticker-proof'].get('data-sig'), 'marquee')

    def test_long_type_wall_title_uses_restrained_scale(self):
        direction = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        quote = next(beat for beat in direction['beats'] if beat['type'] == 'quote')
        quote.update({'big': 'An extraordinarily long title which should wrap safely',
                      'body': 'The complete supporting caption.', 'ui': {'move': 'type-wall'}})
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'direction.json').write_text(json.dumps(direction))
            (folder / 'images.json').write_bytes((ROOT / 'tests/images.sample.json').read_bytes())
            output = folder / 'page.html'
            render.build(directory, 'white-desert', str(output))
            html = output.read_text()
        self.assertNotIn('class="wrap tw-prominent"', html)
        self.assertIn('The complete supporting caption.', html)

    def test_all_ledger_rows_facts_and_photo_captions_survive(self):
        direction = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        original = {beat['id']: beat for beat in direction['beats']}
        ledgers = []
        for prefix in ('menu', 'specials'):
            ledgers.append({'id': prefix, 'type': 'ledger', 'h2': prefix,
                            'items': [[f'{prefix} item {i}', f'{i} EUR'] for i in range(8)]})
        ledgers[0]['image'] = 'octopus'
        photo = {'id': 'photo-menu', 'type': 'photo', 'h2': 'Meal choices',
                 'lede': 'Choose your menu.', 'image': 'long-table',
                 'cap': ['Lunch menu', 'Weekend menu']}
        facts = {'id': 'late-facts', 'type': 'facts',
                 'facts': [['12', 'years serving'], ['24', 'places available']]}
        direction['beats'] = [original['q'], original['feat'], original['how'],
                              ledgers[0], ledgers[1], photo, facts, original['rezervacija']]
        images = json.loads((ROOT / 'tests/images.sample.json').read_text())
        for image in images: image['detail'] = True
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'direction.json').write_text(json.dumps(direction))
            (folder / 'images.json').write_text(json.dumps(images))
            output = folder / 'page.html'
            render.build(directory, 'white-desert', str(output))
            sections = SectionText()
            html = output.read_text()
            sections.feed(html)
        self.assertNotIn('<section class="sec giant', html)
        self.assertNotRegex(html, r'<section[^>]+id="ph\d+"')
        assigned = next(image['data'] for image in images if image['id'] == 'octopus')
        self.assertTrue(assigned in sections.images['menu'])
        for ledger in ledgers:
            text = ' '.join(sections.sections[ledger['id']])
            for name, price in ledger['items']:
                self.assertIn(name, text)
                self.assertIn(price, text)
        self.assertIn('years serving', ' '.join(sections.sections['late-facts']))
        caption = ' '.join(sections.sections['photo-menu'])
        for text in ('Meal choices', 'Lunch menu', 'Weekend menu'):
            self.assertIn(text, caption)


if __name__ == '__main__':
    unittest.main()
