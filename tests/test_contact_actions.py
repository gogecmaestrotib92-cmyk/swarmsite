import importlib.util
import html
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib/swarm'))
import agents
spec = importlib.util.spec_from_file_location('render_bp', ROOT / 'lib/render/render_bp.py')
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


class ContactActionsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.direction = json.loads((ROOT / 'tests/direction.sample.json').read_text())
        self.direction['hero']['cta2'] = 'Menu'
        self.direction['hero']['cta2_href'] = 'https://example.test/menu'
        for beat in self.direction['beats']:
            if beat['type'] == 'form':
                beat['cta_href'] = 'https://example.test/#reservation'
        (self.directory / 'images.json').write_text((ROOT / 'tests/images.sample.json').read_text())

    def build(self, inventory):
        (self.directory / 'direction.json').write_text(json.dumps(self.direction))
        (self.directory / 'inventory.json').write_text(json.dumps(inventory))
        output = self.directory / 'index.html'
        render.build(str(self.directory), 'tengile', str(output))
        return output.read_text()

    def test_source_page_actions_and_form_are_used(self):
        html = self.build({'sourcePages': [{
            'actions': [{'text': 'Menu', 'href': 'https://example.test/menu'}],
            'forms': [{'source_url': 'https://example.test/#reservation', 'text': 'Reserve'}],
        }]})
        self.assertTrue('href="https://example.test/#reservation"' in html or 'action="https://example.test/#reservation"' in html, 'the reservation form posts to the source form page')
        self.assertIn('href="https://example.test/menu"', html)
        self.assertIn('<form class="form" action="https://example.test/#reservation"', html)  # a source form page behind it makes the rendered form real

    def test_uncaptured_destinations_and_fake_forms_are_omitted(self):
        self.direction['hero']['cta2_href'] = 'javascript:alert(1)'
        html = self.build({'url': 'https://example.test/', 'actions': [], 'forms': []})
        self.assertNotIn('href="javascript:', html)
        self.assertNotIn('href="#rezervacija"', html)
        self.assertNotIn('<form ', html)

    def test_main_action_does_not_redirect_to_an_unrelated_contact_form(self):
        self.direction['hero'].update({'cta':'Check a bet', 'cta_href':'https://example.test/bet-check'})
        form = next(b for b in self.direction['beats'] if b['type'] == 'form')
        form.update({'cta':'Send message', 'cta_href':'https://example.test/contact'})
        rendered = self.build({'actions':[{'text':'Check a bet','href':'https://example.test/bet-check'},
                                           {'text':'Send message','href':'https://example.test/contact'}]})
        self.assertTrue('href="https://example.test/bet-check">Check a bet' in rendered, 'main action should use captured destination')
        self.assertFalse('href="#'+form['id']+'">Check a bet' in rendered, 'contact form must not replace unrelated main action')

    def test_ux_keeps_existing_action_labels_with_their_destinations(self):
        ledger = next(beat for beat in self.direction['beats'] if beat['type'] == 'ledger')
        ledger['cta'] = 'View menu'
        ledger['cta_href'] = 'https://example.test/menu'
        (self.directory / 'direction.json').write_text(json.dumps(self.direction))
        agents.apply_ux(str(self.directory), {'goal_cta': 'Reserve a table'})
        self.direction = agents.J(str(self.directory), 'direction.json')
        html = self.build({'actions': [{'text': 'View menu', 'href': 'https://example.test/menu'}]})
        self.assertIn('href="https://example.test/menu">View menu', html)
        self.assertNotIn('href="https://example.test/menu">Reserve a table', html)

    def test_fragment_actions_require_a_visible_captured_target(self):
        self.direction['hero']['cta2'] = 'Open menu'
        self.direction['hero']['cta2_href'] = 'https://example.test/#menu'
        action = {'text': 'Open menu', 'href': 'https://example.test/#menu'}
        for navigable in (False, None):
            candidate = dict(action)
            if navigable is not None:
                candidate['fragment_navigable'] = navigable
            html = self.build({'actions': [candidate]})
            self.assertNotIn('href="https://example.test/#menu"', html)
        action['fragment_navigable'] = True
        html = self.build({'actions': [action]})
        self.assertIn('href="https://example.test/#menu"', html)

    def ledger_links(self, rendered, ledger_id):
        section = re.search(r'<section\b[^>]*\bid="' + re.escape(ledger_id) + r'"[^>]*>(.*?)</section>', rendered, re.S)
        self.assertIsNotNone(section, 'ledger section exists')
        return [(html.unescape(href), html.unescape(re.sub(r'<[^>]*>', '', text)).strip().removesuffix(' →'))
                for href, text in re.findall(r'<a\b[^>]*\bhref="([^"]*)"[^>]*>(.*?)</a>', section.group(1), re.S)]

    def test_ledger_preserves_both_actions_from_forms_and_source_pages(self):
        ledger = next(beat for beat in self.direction['beats'] if beat['type'] == 'ledger')
        ledger.update({'cta': 'Reserve & dine', 'cta_href': 'https://example.test/reserve?day=1&party=2',
                       'cta2': 'Wine & drinks', 'cta2_href': 'https://example.test/wine?red=1&white=2'})
        primary = {'source_url': ledger['cta_href'], 'text': ledger['cta']}
        secondary = {'href': ledger['cta2_href'], 'text': ledger['cta2']}
        # A captured form is an authorized action even when it isn't an <a>.
        for move in ('story', 'sticky-product', 'cards', 'marquee'):
            with self.subTest(move=move):
                ledger['ui'] = {'move': move}
                rendered = self.build({'forms': [primary], 'sourcePages': [{'actions': [secondary]}]})
                self.assertEqual(self.ledger_links(rendered, ledger['id']), [
                    (ledger['cta_href'], ledger['cta']), (ledger['cta2_href'], ledger['cta2'])])
        # The secondary can also be a form captured on a source subpage.
        rendered = self.build({'actions': [{'href': ledger['cta_href'], 'text': ledger['cta']}],
                               'sourcePages': [{'forms': [{'source_url': ledger['cta2_href'], 'text': ledger['cta2']}]}]})
        self.assertEqual(self.ledger_links(rendered, ledger['id']), [
            (ledger['cta_href'], ledger['cta']), (ledger['cta2_href'], ledger['cta2'])])

    def test_ledger_rejects_unverified_or_unsafe_secondary_actions(self):
        ledger = next(beat for beat in self.direction['beats'] if beat['type'] == 'ledger')
        ledger.update({'cta': 'Reserve', 'cta_href': 'https://example.test/reserve', 'cta2': 'Wine'})
        primary = {'href': ledger['cta_href'], 'text': ledger['cta']}
        for secondary, captured in [
            ('https://elsewhere.test/wine', []),
            ('javascript:alert(1)', [{'href': 'javascript:alert(1)', 'text': 'Wine'}]),
            ('https://example.test/#wine', [{'href': 'https://example.test/#wine', 'text': 'Wine'}]),
        ]:
            with self.subTest(secondary=secondary):
                ledger['cta2_href'] = secondary
                rendered = self.build({'actions': [primary, *captured]})
                self.assertEqual(self.ledger_links(rendered, ledger['id']), [(ledger['cta_href'], ledger['cta'])])
        ledger['cta2_href'] = 'https://example.test/#wine'
        rendered = self.build({'actions': [primary, {'href': ledger['cta2_href'], 'text': 'Wine', 'fragment_navigable': True}]})
        self.assertEqual(self.ledger_links(rendered, ledger['id']), [(ledger['cta_href'], ledger['cta']), (ledger['cta2_href'], 'Wine')])


if __name__ == '__main__':
    unittest.main()
