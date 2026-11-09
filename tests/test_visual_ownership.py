import base64
import io
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'swarm'))
import agents
import gen


class VisualOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = self.tmp.name
        image = Image.new('RGB', (800, 600), (170, 90, 40))
        buffer = io.BytesIO()
        image.save(buffer, 'PNG')
        self.raw = buffer.getvalue()
        data = 'data:image/png;base64,' + base64.b64encode(self.raw).decode()
        self.images = [{'id': name, 'w': 800, 'h': 600, 'data': data}
                       for name in ('hero', 'a', 'b', 'c', 'source')]
        direction = {'hero': {'h1': 'Old headline', 'media': 'hero'}, 'beats': [
            {'id': 'first', 'type': 'ledger', 'image': 'a', 'ui': {'lead': 'a'}},
            {'id': 'second', 'type': 'facts', 'image': 'b'},
            {'id': 'third', 'type': 'photo', 'image': 'c'},
        ]}
        agents.W(self.directory, 'direction.json', direction)
        agents.W(self.directory, 'images.json', self.images)

    def apply(self, reply):
        with patch.object(gen, 'enabled', return_value=False):
            return agents.apply_visual(self.directory, reply)

    def direction(self):
        return agents.J(self.directory, 'direction.json')

    def test_partial_update_cannot_steal_untouched_image_or_hero(self):
        self.apply({'hero': 'b', 'slots': [{'beat': 'first', 'image': 'b'}]})
        direction = self.direction()
        self.assertEqual(direction['hero']['media'], 'hero')
        self.assertEqual([b['image'] for b in direction['beats']], ['a', 'b', 'c'])
        self.assertEqual(direction['beats'][0]['ui']['lead'], 'a')

    def test_explicit_image_swap_preserves_both_owners(self):
        self.apply({'hero': 'hero', 'slots': [
            {'beat': 'first', 'image': 'b'}, {'beat': 'second', 'image': 'a'}]})
        direction = self.direction()
        self.assertEqual([b['image'] for b in direction['beats']], ['b', 'a', 'c'])
        self.assertEqual(direction['beats'][0]['ui']['lead'], 'b')

    def test_hero_can_swap_with_a_beat_in_the_same_reply(self):
        self.apply({'hero': 'a', 'slots': [{'beat': 'first', 'image': 'hero'}]})
        direction = self.direction()
        self.assertEqual(direction['hero']['media'], 'a')
        self.assertEqual(direction['beats'][0]['image'], 'hero')
        self.assertEqual(direction['beats'][0]['ui']['lead'], 'hero')

    def test_feature_image_is_reserved_by_its_beat(self):
        direction = self.direction()
        direction['beats'][2]['features'] = [{'title': 'Detail', 'image': 'source'}]
        agents.W(self.directory, 'direction.json', direction)
        self.apply({'hero': 'hero', 'slots': [{'beat': 'first', 'image': 'source'}]})
        direction = self.direction()
        self.assertEqual(direction['beats'][0]['image'], 'a')
        self.assertEqual(direction['beats'][2]['features'][0]['image'], 'source')

    def test_missing_legacy_reference_and_invalid_image_metadata_are_preserved(self):
        direction = self.direction()
        direction['beats'][0]['image'] = 'old-missing-image'
        direction['beats'][0].pop('ui')
        agents.W(self.directory, 'direction.json', direction)
        images = self.images + [{'data': ''}]
        agents.W(self.directory, 'images.json', images)
        self.apply({'hero': 'hero'})
        self.assertEqual(self.direction()['beats'][0]['image'], 'old-missing-image')
        self.apply({'slots': [{'beat': 'first', 'image': 'does-not-exist'}]})
        self.assertEqual(self.direction()['beats'][0]['image'], 'old-missing-image')
        self.assertEqual(agents.J(self.directory, 'images.json'), images)

    def test_existing_crop_can_be_updated_without_creating_another_id(self):
        crop = {**self.images[-1], 'id': 'existing-crop', 'crop_of': 'source', 'detail': True}
        agents.W(self.directory, 'images.json', self.images + [crop])
        direction = self.direction()
        direction['beats'][1]['image'] = 'existing-crop'
        agents.W(self.directory, 'direction.json', direction)
        self.apply({'crops': [{'image': 'source', 'box': [0, 0, .6, .6], 'as': 'existing-crop'}],
                    'slots': [{'beat': 'second', 'image': 'existing-crop'}]})
        images = agents.J(self.directory, 'images.json')
        self.assertEqual(len(images), len(self.images) + 1)
        self.assertEqual(next(i for i in images if i['id'] == 'existing-crop')['w'], 480)
        self.assertEqual(self.direction()['beats'][1]['image'], 'existing-crop')

    def test_dependent_conflicts_restore_old_assignments(self):
        self.apply({'hero': 'hero', 'slots': [
            {'beat': 'first', 'image': 'b'}, {'beat': 'second', 'image': 'c'}]})
        self.assertEqual([b['image'] for b in self.direction()['beats']], ['a', 'b', 'c'])

    def test_legacy_duplicate_is_resolved_without_removing_inventory(self):
        direction = self.direction()
        direction['beats'][1]['image'] = 'a'
        direction['beats'][1]['ui'] = {'lead': 'a'}
        agents.W(self.directory, 'direction.json', direction)
        self.apply({'hero': 'hero'})
        direction = self.direction()
        self.assertEqual(direction['beats'][0]['image'], 'a')
        self.assertEqual(direction['beats'][0]['ui']['lead'], 'a')
        self.assertEqual(direction['beats'][1]['image'], '')
        self.assertEqual(direction['beats'][1]['ui']['lead'], '')
        self.assertEqual(agents.J(self.directory, 'images.json'), self.images)

    def test_large_crop_shares_source_owner_but_detail_crop_is_distinct(self):
        images = self.images + [
            {**self.images[1], 'id': 'large-crop', 'crop_of': 'a', 'detail': False},
            {**self.images[1], 'id': 'detail-crop', 'crop_of': 'a', 'detail': True},
        ]
        agents.W(self.directory, 'images.json', images)
        self.apply({'hero': 'hero', 'slots': [{'beat': 'second', 'image': 'large-crop'}]})
        self.assertEqual(self.direction()['beats'][1]['image'], 'b')
        self.apply({'hero': 'hero', 'slots': [{'beat': 'second', 'image': 'detail-crop'}]})
        self.assertEqual(self.direction()['beats'][1]['image'], 'detail-crop')

    def test_crop_id_collision_preserves_original_and_reuses_alias_on_retry(self):
        reply = {'hero': 'hero', 'crops': [{'image': 'source', 'box': [0, 0, .6, .6], 'as': 'a'}],
                 'slots': [{'beat': 'second', 'image': 'a'}]}
        self.apply(reply)
        images = agents.J(self.directory, 'images.json')
        self.assertEqual(next(i for i in images if i['id'] == 'a'), self.images[1])
        self.assertEqual(self.direction()['beats'][1]['image'], 'a-crop-2')
        self.assertEqual(len(images), len(self.images) + 1)
        self.apply(reply)
        self.assertEqual(len(agents.J(self.directory, 'images.json')), len(self.images) + 1)
        self.assertEqual(self.direction()['beats'][1]['image'], 'a-crop-2')

    def test_generation_is_one_atmosphere_behind_a_statement_never_a_slot_picture(self):
        direction = self.direction(); direction['beats'].append({'id': 'why', 'type': 'quote', 'big': 'Why we exist'})
        agents.W(self.directory, 'direction.json', direction)
        reply = {'hero': 'hero', 'generate': [{'beat': 'second', 'prompt': 'A plate', 'ar': '16:9', 'as': 'a'}]}
        with patch.object(gen, 'enabled', return_value=True), patch.object(gen, 'generate', return_value=self.raw) as generate:
            agents.apply_visual(self.directory, reply)
            agents.apply_visual(self.directory, reply)
        images = agents.J(self.directory, 'images.json'); direction = self.direction()
        self.assertEqual(generate.call_count, 1, 'one backdrop per page; the editor\'s object commission is not honoured')
        self.assertEqual(next(i for i in images if i['id'] == 'a'), self.images[1])
        self.assertEqual(direction['beats'][1]['image'], 'b')
        self.assertEqual(direction['beats'][3]['atmos'], 'gen-why')
        self.assertFalse(direction['beats'][3].get('image'))
        self.assertEqual(len(images), len(self.images) + 1)

    def test_visual_update_and_copy_update_both_survive(self):
        barrier = threading.Barrier(2)
        def visual():
            barrier.wait(timeout=5)
            return self.apply({'hero': 'hero', 'slots': [{'beat': 'first', 'image': 'source'}]})
        def copy():
            barrier.wait(timeout=5)
            return agents.apply_copy(self.directory, {'edits': [{'path': 'hero.h1', 'value': 'New headline'}]})
        with ThreadPoolExecutor(2) as pool:
            results = [pool.submit(visual), pool.submit(copy)]
            for result in results: result.result(timeout=10)
        direction = self.direction()
        self.assertEqual(direction['hero']['h1'], 'New headline')
        self.assertEqual(direction['beats'][0]['image'], 'source')


if __name__ == '__main__':
    unittest.main()
