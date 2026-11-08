import base64
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib' / 'swarm'))
import agents


def image_data(image):
    buffer = io.BytesIO()
    image.save(buffer, 'JPEG')
    return 'data:image/jpeg;base64,' + base64.b64encode(buffer.getvalue()).decode()


class VisualAssetTest(unittest.TestCase):
    def test_numeric_ticker_rejects_new_picture_without_deleting_existing(self):
        with tempfile.TemporaryDirectory() as directory:
            direction = {'hero': {}, 'beats': [
                {'id': 'facts', 'type': 'facts', 'image': 'saved', 'ui': {'move': 'marquee'}},
                {'id': 'menu', 'type': 'ledger', 'ui': {'move': 'story'}},
            ]}
            agents.W(directory, 'direction.json', direction)
            agents.W(directory, 'images.json', [{'id': 'saved'}, {'id': 'new'}])
            reply = {'slots': [{'beat': 'facts', 'image': 'new'}, {'beat': 'menu', 'image': 'new'}]}
            with patch('gen.enabled', return_value=False):
                agents.apply_visual(directory, reply)
                updated = agents.J(directory, 'direction.json')
                self.assertEqual(updated['beats'][0]['image'], 'saved')
                self.assertEqual(updated['beats'][1]['image'], 'new')
                updated['beats'][0]['ui']['move'] = 'story'
                agents.W(directory, 'direction.json', updated)
                agents.apply_visual(directory, {'slots': [{'beat': 'facts', 'image': 'new'}]})
                updated = agents.J(directory, 'direction.json')
                self.assertEqual(updated['beats'][0]['image'], 'saved')
                self.assertEqual(updated['beats'][1]['image'], 'new')

    def test_missing_data_and_flat_dark_background_are_not_photos(self):
        self.assertFalse(agents._photo({'w': 1200, 'h': 800}))
        flat = Image.new('RGB', (1200, 800), (15, 15, 15))
        self.assertFalse(agents._photo({'w': 1200, 'h': 800, 'bg': True, 'lum': 15, 'data': image_data(flat)}))
        self.assertFalse(agents._photo({'w': 1200, 'h': 800, 'bg': True, 'lum': None, 'data': image_data(flat)}))

    def test_dark_picture_with_detail_remains_available(self):
        image = Image.new('RGB', (1200, 800), (10, 10, 10))
        ImageDraw.Draw(image).rectangle((300, 200, 900, 600), fill=(70, 70, 70))
        self.assertTrue(agents._photo({'w': 1200, 'h': 800, 'bg': True, 'lum': 25, 'data': image_data(image)}))

    def test_visual_prompt_counts_only_valid_photo_and_generated_images(self):
        white = image_data(Image.new('RGB', (1200, 800), 'white'))
        useful = Image.new('RGB', (1200, 800), 'white')
        ImageDraw.Draw(useful).rectangle((400, 300, 600, 500), fill='#eeeeee')
        imgs = [{'id': f'blank-{i}', 'w': 1200, 'h': 800, 'data': white} for i in range(3)]
        imgs += [{'id': 'blank-gen', 'w': 1200, 'h': 800, 'gen': True, 'data': white},
                 {'id': 'useful', 'w': 1200, 'h': 800, 'data': image_data(useful)}]
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'direction.json', {'hero': {}, 'brand': {}, 'beats': [], 'kind': 'place'})
            agents.W(directory, 'images.json', imgs)
            with patch('gen.enabled', return_value=True), patch.object(agents, 'ask', return_value=None) as ask, patch.object(agents, 'empty_visual', wraps=agents.empty_visual) as check_empty, patch('PIL.Image.open', wraps=Image.open) as open_image:
                agents.visual(directory)
            content = ask.call_args.args[1]
            self.assertIn('only 1 distinct real visual(s) and 0 commissioned', content[0]['text'])
            self.assertIn('MUST commission 3 originals', content[0]['text'])
            labels = [item['text'] for item in content[1:] if item['type'] == 'text' and item['text'].startswith('id=')]
            self.assertEqual(len(labels), 1)
            self.assertIn('id=useful', labels[0])
            checked = [call.args[0]['id'] for call in check_empty.call_args_list]
            self.assertCountEqual(checked, [image['id'] for image in imgs], 'each image is decoded at most once for this prompt')
            self.assertEqual(open_image.call_count, len(imgs), 'counting and thumbnails share each sequential decode')

    def test_blank_assigned_and_blank_generation_do_not_block_replacement(self):
        white = image_data(Image.new('RGB', (1200, 800), 'white'))
        useful = Image.new('RGB', (1200, 800), 'white')
        ImageDraw.Draw(useful).rectangle((400, 300, 600, 500), fill='#eeeeee')
        generated = base64.b64decode(image_data(useful).split(',', 1)[1])
        with tempfile.TemporaryDirectory() as directory:
            direction = {'hero': {}, 'brand': {'name': 'Studio'}, 'kind': 'place', 'beats': [
                {'id': 'offer', 'type': 'features', 'h2': 'Offer', 'image': 'blank', 'features': []}]}
            agents.W(directory, 'direction.json', direction)
            agents.W(directory, 'images.json', [{'id': 'blank', 'w': 1200, 'h': 800, 'data': white},
                                                {'id': 'blank-gen', 'w': 1200, 'h': 800, 'gen': True, 'data': white}])
            with patch('gen.enabled', return_value=True), patch('gen.generate', return_value=generated) as generate:
                agents.apply_visual(directory, {'need': ['A real visual']})
            self.assertEqual(generate.call_count, 1)
            updated = agents.J(directory, 'direction.json')
            self.assertNotEqual(updated['beats'][0]['image'], 'blank')
            self.assertEqual(len(updated['swarm']['visual']['generated']), 1)

    def test_empty_generated_output_is_not_assigned(self):
        white = base64.b64decode(image_data(Image.new('RGB', (1200, 800), 'white')).split(',', 1)[1])
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'direction.json', {'hero': {}, 'brand': {'name': 'Studio'}, 'kind': 'place',
                                                    'beats': [{'id': 'offer', 'type': 'features'}]})
            agents.W(directory, 'images.json', [])
            with patch('gen.enabled', return_value=True), patch('gen.generate', return_value=white):
                agents.apply_visual(directory, {'generate': [{'beat': 'offer', 'prompt': 'Image'}]})
            d = agents.J(directory, 'direction.json')
            self.assertFalse(d['beats'][0].get('image'))
            self.assertEqual(d['swarm']['visual']['generated'], [])
            self.assertEqual(d['swarm']['visual']['gen_errors'], ['generated image is empty'])

    def test_fully_transparent_source_cannot_create_opaque_crop(self):
        output = io.BytesIO()
        Image.new('RGBA', (1200, 800), (255, 0, 0, 0)).save(output, 'PNG')
        transparent = 'data:image/png;base64,' + base64.b64encode(output.getvalue()).decode()
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'direction.json', {'hero': {}, 'beats': []})
            agents.W(directory, 'images.json', [{'id': 'transparent', 'w': 1200, 'h': 800, 'data': transparent}])
            reply = {'crops': [{'image': 'transparent', 'box': [0, 0, .8, .8], 'as': 'false-red'}], 'hero': 'false-red'}
            with patch('gen.enabled', return_value=False):
                agents.apply_visual(directory, reply)
            self.assertEqual([i['id'] for i in agents.J(directory, 'images.json')], ['transparent'])
            self.assertFalse(agents.J(directory, 'direction.json')['hero'].get('media'))


if __name__ == '__main__':
    unittest.main()
