"""The house owns the architecture: order and moves per kind; the director and the agents fill the slots."""
import importlib.util, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('house', ROOT / 'lib/house.py'); house = importlib.util.module_from_spec(spec); spec.loader.exec_module(house)


class House(unittest.TestCase):
    def test_every_kind_has_a_structure_the_director_can_read(self):
        for kind in ('software', 'place', 'service', 'product'):
            text = house.describe(kind)
            self.assertIn('HOUSE STRUCTURE', text); self.assertIn('hero', text); self.assertIn('CTA band', text)  # product landings never render a FAQ block (0/8)

    def test_lock_orders_beats_by_the_house_and_sets_moves(self):
        d = {'kind': 'software', 'beats': [
            {'id': 'faq', 'type': 'faq', 'ui': {'move': 'pinned-sequence'}},
            {'id': 'steps', 'type': 'steps', 'ui': {'move': 'pinned-sequence'}},
            {'id': 'result', 'type': 'photo'},
            {'id': 'nums', 'type': 'cells', 'ui': {'move': 'cards'}},
            {'id': 'odd', 'type': 'facts'}]}
        out = house.lock(d)
        # software: proof → features → trust → figures → faq; a steps beat has no slot and follows the known ones
        self.assertEqual([b['id'] for b in out['beats']], ['result', 'nums', 'faq', 'steps', 'odd'])
        self.assertEqual(out['beats'][0]['ui']['move'], 'story')
        self.assertEqual(out['beats'][1]['ui']['move'], 'marquee')
        self.assertEqual(out['beats'][2]['ui']['move'], 'cards')
        self.assertEqual(out['beats'][3]['ui']['move'], 'pinned-sequence', 'a type without a house slot keeps the agents\' move')
        self.assertEqual(out['house'], 'software')

    def test_service_without_work_photos_leads_with_services(self):
        d = {'kind': 'service', 'beats': [{'id': 'svc', 'type': 'features'}, {'id': 'work', 'type': 'photo'}]}
        self.assertEqual([b['id'] for b in house.lock(d)['beats']], ['svc', 'work'])
        d = {'kind': 'service', 'beats': [{'id': 'svc', 'type': 'features'}, {'id': 'work', 'type': 'photo', 'image': 'img1'}]}
        self.assertEqual([b['id'] for b in house.lock(d)['beats']], ['work', 'svc'])

    def test_place_second_photo_becomes_the_gallery(self):
        d = {'kind': 'place', 'beats': [{'id': 'a', 'type': 'photo'}, {'id': 'b', 'type': 'photo'}, {'id': 'm', 'type': 'ledger', 'ui': {'move': 'marquee'}}]}
        out = house.lock(d)
        self.assertEqual([b['id'] for b in out['beats']], ['a', 'm', 'b'])
        self.assertEqual(out['beats'][0]['ui']['move'], 'story')
        self.assertEqual(out['beats'][2]['ui'].get('photo_layout'), 'gallery')
        self.assertEqual(out['beats'][1]['ui']['move'], 'marquee', 'a ledger has no house move; the agents keep theirs')

    def test_every_slot_type_is_one_the_renderer_knows(self):
        known = {'photo', 'cells', 'steps', 'features', 'ledger', 'quote', 'testimonials', 'faq', 'form', 'facts'}
        for kind, slots in house.HOUSE.items():
            for _, t, _, _, _ in slots: self.assertIn(t, known, f'{kind}: {t}')


if __name__ == '__main__':
    unittest.main()
