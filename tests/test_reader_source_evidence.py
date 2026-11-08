import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'swarm'))
import agents


class ReaderSourceEvidenceTests(unittest.TestCase):
    def test_reader_does_not_send_unbounded_panel_or_review_candidates(self):
        faq = [{'question': 'Question?', 'answer': 'Actual answer', 'status': 'readable'}]
        inventory = {'sourcePages': [{'url': 'https://example.test/about', 'sections': [
            {'id': 'p1', 'title': 'Proof', 'faq': faq, 'panels': [{'text': 'panel evidence' * 10000}],
             'testimonials': [{'text': 'review evidence' * 10000}]}]}]}
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'inventory.json', inventory)
            with patch.object(agents, 'ask', return_value=None) as ask:
                agents.reader(directory)
            prompt = '\n'.join(p.get('text', '') for p in ask.call_args.args[1] if p.get('type') == 'text')
            self.assertIn('Actual answer', prompt)
            self.assertNotIn('panel evidence', prompt)
            self.assertNotIn('review evidence', prompt)
            self.assertIn('testimonials', agents.J(directory, 'inventory.json')['sourcePages'][0]['sections'][0])


if __name__ == '__main__':
    unittest.main()
