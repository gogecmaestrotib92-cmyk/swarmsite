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


if __name__ == '__main__':
    unittest.main()
