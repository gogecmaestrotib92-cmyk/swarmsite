"""The house can speak in two voices. 'lock' (the default, production): it fixes the order and the move of every
section. 'requirements' (SWARM_HOUSE=requirements): it says what a page of this kind must carry and recommends an
order; the director, the Concept and the recipe decide the forms. Nothing here may change the default."""
import importlib.util, json, os, sys, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('house_modes', ROOT / 'lib/house.py'); house = importlib.util.module_from_spec(spec); spec.loader.exec_module(house)


def software():
    return {'kind': 'software', 'beats': [
        {'id': 'faq', 'type': 'faq', 'ui': {'move': 'cards'}},
        {'id': 'how', 'type': 'steps', 'ui': {'move': 'pinned-sequence'}},
        {'id': 'what', 'type': 'features', 'ui': {'move': 'sticky-product'}},
        {'id': 'plans', 'type': 'ledger'},
        {'id': 'nums', 'type': 'cells', 'ui': {'move': 'cards'}}]}


class Modes(unittest.TestCase):
    def test_default_is_lock_and_unknown_values_fall_back_to_it(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('SWARM_HOUSE', None)
            self.assertEqual(house.mode(), 'lock')
        for value in ('', 'lock', 'LOCK', 'nonsense', '1'):
            with mock.patch.dict(os.environ, {'SWARM_HOUSE': value}): self.assertEqual(house.mode(), 'lock', value)
        for value in ('requirements', 'Requirements ', 'req'):
            with mock.patch.dict(os.environ, {'SWARM_HOUSE': value}): self.assertEqual(house.mode(), 'requirements', value)

    def test_lock_mode_still_sorts_and_sets_moves(self):
        out = house.lock(software(), mode='lock')
        self.assertEqual([b['id'] for b in out['beats']], ['what', 'nums', 'faq', 'how', 'plans'])
        self.assertEqual(out['beats'][0]['ui']['move'], 'pinned-sequence'); self.assertEqual(out['beats'][1]['ui']['move'], 'marquee')
        self.assertEqual(out['house'], 'software'); self.assertNotIn('house_requirements', out)

    def test_requirements_mode_keeps_the_order_and_the_moves_it_was_given(self):
        before = software(); out = house.lock(json.loads(json.dumps(before)), mode='requirements')
        self.assertEqual([b['id'] for b in out['beats']], [b['id'] for b in before['beats']])
        self.assertEqual([b.get('ui') for b in out['beats']], [b.get('ui') for b in before['beats']])
        self.assertNotIn('house', out, 'agents read `house` as "order and moves are not yours"')
        self.assertEqual(out['house_requirements'], 'software')

    def test_requirements_mode_unlocks_a_document_that_was_locked_before(self):
        locked = house.lock(software(), mode='lock'); self.assertEqual(locked['house'], 'software')
        out = house.lock(locked, mode='requirements')
        self.assertNotIn('house', out)

    def test_the_environment_selects_the_mode_when_none_is_passed(self):
        with mock.patch.dict(os.environ, {'SWARM_HOUSE': 'requirements'}):
            self.assertNotIn('house', house.lock(software()))
            self.assertEqual(house.violations(software()), [])
        with mock.patch.dict(os.environ, {'SWARM_HOUSE': 'lock'}):
            self.assertEqual(house.lock(software())['house'], 'software')
            self.assertTrue(house.violations(software()))

    def test_requirements_mode_rejects_no_beat_type(self):
        doc = {'kind': 'software', 'beats': [{'type': 'steps'}, {'type': 'quote'}, {'type': 'ledger'}, {'type': 'ledger'}, {'type': 'facts'}]}
        self.assertTrue(house.violations(doc, mode='lock'))
        self.assertEqual(house.violations(doc, mode='requirements'), [])

    def test_requirements_text_states_content_and_does_not_order_or_forbid(self):
        for kind in ('software', 'place', 'service', 'product'):
            text = house.describe(kind, mode='requirements')
            self.assertIn('CONTENT REQUIREMENTS', text); self.assertIn('recommend', text.lower())
            self.assertNotIn('do not reorder', text); self.assertNotIn('do not add other beats', text)
            self.assertIn('REQUIRED', text)
            locked = house.describe(kind, mode='lock')
            self.assertIn('HOUSE STRUCTURE', locked); self.assertIn('do not reorder', locked)

    def test_requirements_carry_no_layout(self):
        for kind in house.HOUSE:
            reqs = house.requirements(kind)
            self.assertEqual([r['id'] for r in reqs], [s[0] for s in house.HOUSE[kind]])
            for r in reqs:
                self.assertEqual(set(r), {'id', 'type', 'need', 'what', 'compose', 'position'})
                self.assertIn(r['need'], ('required', 'recommended', 'optional'))
            self.assertTrue(any(r['need'] == 'required' for r in reqs), kind)

    def test_every_slot_has_a_need_level(self):
        for kind, slots in house.HOUSE.items():
            self.assertEqual(set(house.NEED[kind]), {s[0] for s in slots}, kind)


class DirectorAndAgents(unittest.TestCase):
    """What the rest of the pipeline does with a document that carries no `house`."""
    def setUp(self):
        sys.path.insert(0, str(ROOT / 'lib' / 'direct')); sys.path.insert(0, str(ROOT / 'lib' / 'swarm')); sys.path.insert(0, str(ROOT / 'lib'))

    def document(self):
        return {'kind': 'software', 'blueprint': 'butter', 'hero': {'h1': 'Plans drawn in seconds'},
                'beats': [{'id': 'what', 'type': 'features', 'h2': 'What it does', 'features': [{'title': 'a', 'body': 'b'}, {'title': 'c', 'body': 'd'}]},
                          {'id': 'how', 'type': 'steps', 'h2': 'How it works', 'steps': ['one', 'two', 'three']},
                          {'id': 'plans', 'type': 'ledger', 'h2': 'Plans', 'items': [['Free', '0'], ['Pro', '9']]}]}

    def test_director_validation_accepts_free_beat_types_only_in_requirements_mode(self):
        import direct
        with mock.patch.dict(os.environ, {'SWARM_HOUSE': 'lock'}):
            self.assertTrue(any('house has no' in e for e in direct.validate(self.document())))
        with mock.patch.dict(os.environ, {'SWARM_HOUSE': 'requirements'}):
            self.assertEqual(direct.validate(self.document()), [])

    def test_ux_order_is_honoured_once_the_house_does_not_own_it(self):
        import tempfile
        import agents
        for mode_name, expected in (('requirements', ['plans', 'how', 'what']), ('lock', None)):
            with tempfile.TemporaryDirectory() as temp, mock.patch.dict(os.environ, {'SWARM_HOUSE': mode_name}):
                doc = house.lock(self.document()); original = [b['id'] for b in doc['beats']]
                agents.W(temp, 'direction.json', doc)
                agents.apply_ux(temp, {'order': ['plans', 'how', 'what'], 'goal_cta': 'Start free'})
                after = [b['id'] for b in agents.J(temp, 'direction.json')['beats']]
                self.assertEqual(after, expected or original, mode_name)


if __name__ == '__main__':
    unittest.main()
