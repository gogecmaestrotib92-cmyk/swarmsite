"""quick.py pours a captured page into the house template with no model call, and the result renders."""
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


quick = load('quick_director', 'lib/direct/quick.py')
render = load('render_bp_quick', 'lib/render/render_bp.py')


class QuickDirector(unittest.TestCase):
    def setUp(self):
        self.inv = json.loads((ROOT / 'tests/inventory.seo.sample.json').read_text())
        self.inv.setdefault('copy', {})['h1'] = 'Restoran Franš'
        self.inv['sourceCoverage'] = {'sections': [
            {'id': 'home-1', 'title': 'Restoran Franš', 'text': 'Restoran Franš. Tradicija i elegancija pod starim stablima u Beogradu. Jelovnik koji se ne menja po modi.', 'faq': [], 'links': []},
            {'id': 'home-2', 'title': 'Kako rezervišete', 'text': 'Pozovite nas telefonom ili pošaljite poruku. Recite broj gostiju i vreme. Mi potvrdimo sto u roku od sat vremena.', 'faq': [], 'links': []},
            {'id': 'home-3', 'title': 'Česta pitanja', 'text': '', 'faq': [{'question': 'Da li imate baštu?', 'answer': 'Da, bašta radi od maja do oktobra.'}, {'question': 'Da li primate kartice?', 'answer': 'Da, sve kartice.'}], 'links': []},
            {'id': 'home-4', 'title': 'Jelovnik koji traje', 'text': 'Naš jelovnik nastaje iz sezone i tradicije. Svako jelo ima svoju priču i svog kuvara koji ga brani.', 'faq': [], 'links': []},
        ]}

    def build(self, audit):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'inventory.json').write_text(json.dumps(self.inv)); (p / 'audit.json').write_text(json.dumps(audit))
            (p / 'images.json').write_text('[]'); (p / 'brief.json').write_text('{}'); (p / 'assets.json').write_text('{}')
            direction = quick.quick(d)
            (p / 'direction.json').write_text(json.dumps(direction))
            render.build(d, direction['blueprint'], str(p / 'index.html'))
            return direction, (p / 'index.html').read_text()

    def test_restaurant_pours_into_the_place_template_in_source_order(self):
        direction, html = self.build({'industry': 'restaurant'})
        self.assertEqual(direction['kind'], 'place'); self.assertEqual(direction['blueprint'], 'white-desert')
        self.assertEqual(direction['hero']['h1'], 'Restoran Franš')
        types = [b['type'] for b in direction['beats']]
        self.assertEqual(types[0], 'steps', 'a "how" heading with three sentences is a steps beat')
        self.assertIn('faq', types)
        self.assertEqual(len(direction['beats'][types.index('faq')]['items']), 2)
        for needle in ('Restoran Franš', 'Kako rezervišete', 'Da li imate baštu?', 'Jelovnik koji traje'):
            self.assertIn(needle, html)
        self.assertNotIn('undefined', html)

    def test_software_goes_to_the_dark_house_template(self):
        direction, html = self.build({'industry': 'saas'})
        self.assertEqual(direction['blueprint'], 'cerebrium'); self.assertEqual(direction['voice'], 'sans')
        self.assertTrue(direction.get('quick'))
        self.assertTrue(re.search(r'<h1 class="h1"', html))

    def test_cta_is_never_a_price_line_or_a_skip_link(self):
        self.inv['copy']['buttons'] = ['Skip to content', 'Lifetime access · $299 one-time', 'Rezerviši sto']
        self.inv['actions'] = [{'text': 'Rezerviši sto', 'href': 'https://frans.rs/rezervacija', 'region': 'main'}]
        direction, _ = self.build({'industry': 'restaurant'})
        self.assertEqual(direction['hero']['cta'], 'Rezerviši sto')
        self.assertEqual(direction['hero']['cta_href'], 'https://frans.rs/rezervacija')


if __name__ == '__main__':
    unittest.main()
