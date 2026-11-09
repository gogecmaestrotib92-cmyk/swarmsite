"""Moods: curated palettes chosen from the brand's own accent, in the blueprint's mode."""
import importlib.util, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('moods', ROOT / 'lib/moods.py'); moods = importlib.util.module_from_spec(spec); spec.loader.exec_module(moods)
cp = importlib.util.spec_from_file_location('colour_policy', ROOT / 'lib/colour_policy.py'); policy = importlib.util.module_from_spec(cp); cp.loader.exec_module(policy)


class Moods(unittest.TestCase):
    def test_green_buttons_pick_the_green_world_of_the_same_mode(self):
        inv = {'colors': {'bg': [{'c': '#0b0b0d', 'n': 900}], 'buttons': [{'c': '#ffffff a0', 'n': 8}, {'c': '#10b981', 'n': 4}]}}
        m = moods.choose('software', inv, 'dark')
        self.assertEqual(m['id'], 'terminal'); self.assertEqual(m['mode'], 'dark'); self.assertIn('#10b981', m['why'])

    def test_no_brand_accent_gives_the_kind_default(self):
        self.assertEqual(moods.choose('place', {'colors': {'bg': [{'c': '#ffffff', 'n': 10}], 'buttons': [{'c': '#000000', 'n': 3}]}}, 'light')['id'], 'warm-paper')
        self.assertEqual(moods.choose('software', {}, 'light')['id'], 'quiet-light')

    def test_far_hue_falls_back_to_default_rather_than_a_wrong_world(self):
        # a pink brand on a place site: no place mood within 45° → default, not a random one
        inv = {'colors': {'buttons': [{'c': '#ff00aa', 'n': 5}]}}
        m = moods.choose('service', inv, 'light')
        self.assertIn(m['id'], ('editorial-ivory', 'swiss'))

    def test_unbranded_sites_get_different_worlds_and_keep_them(self):
        # black-and-white sites (most first versions) are coloured by us: the pick is seeded by the site, so it is stable
        # for one site and different between sites, in both modes
        picks = {moods.choose('software', {}, 'dark', seed=f'https://site{i}.com')['id'] for i in range(12)}
        self.assertGreaterEqual(len(picks), 4)
        self.assertEqual(moods.choose('software', {}, 'dark', seed='https://www.acme.io/')['id'], moods.choose('software', {}, 'dark', seed='acme.io')['id'])
        self.assertIn('house pick', moods.choose('service', {}, 'light', seed='x.com')['why'])
        light = {moods.choose('software', {}, 'light', seed=f'https://site{i}.com')['id'] for i in range(12)}
        self.assertGreaterEqual(len(light), 4)

    def test_every_mood_is_legible_and_has_a_usable_button(self):
        for kind, ms in moods.MOODS.items():
            for m in ms:
                p = policy.resolve({k: m[k] for k in ('paper', 'ink', 'accent', 'alt', 'mode')})
                self.assertGreaterEqual(policy.contrast(p['ink'], p['paper']), 4.5, f'{kind}/{m["id"]} text')
                self.assertGreaterEqual(policy.contrast(p['button_ink'], p['button']), 3, f'{kind}/{m["id"]} button')
                self.assertEqual((m['mode'] == 'dark'), policy.luminance(p['paper']) < .3, f'{kind}/{m["id"]} mode matches paper')


if __name__ == '__main__':
    unittest.main()
