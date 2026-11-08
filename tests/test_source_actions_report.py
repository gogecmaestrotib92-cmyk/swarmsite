"""Source-link provenance must not fabricate content coverage."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('source_actions_coverage', ROOT / 'lib/swarm/coverage_report.py')
coverage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coverage)


class SourceActionsCoverage(unittest.TestCase):
    def test_incomplete_and_legacy_capture_and_provenance_text(self):
        section = {'id': 's', 'title': 'Original section', 'sourceActionsVersion': 1,
                   'sourceActions': [{'label': 'Go', 'url': 'https://example.com/path'}],
                   'sourceActionsExcluded': 1, 'sourceActionsTruncated': True}
        inv = {'sourceCoverage': {'sections': [section], 'routes': []}}
        page = ('<section><h2>Rewritten</h2><aside class="source-actions">'
                '<p class="source-actions-label">Original links · Original section</p>'
                '<a href="https://example.com/path">Go</a></aside></section>')
        report = coverage.build_coverage(inv, page)
        result = report['sections'][0]
        self.assertEqual(result['status'], 'needs_review')
        self.assertEqual(result['source_actions'][0]['status'], 'url_detected')
        self.assertTrue(result['source_actions_truncated'])
        self.assertEqual(result['source_actions_excluded'], 1)
        self.assertTrue(report['source_actions_needing_review'])
        del section['sourceActionsVersion']
        self.assertTrue(coverage.build_coverage(inv, page)['source_actions_needing_review'])

if __name__ == '__main__':
    unittest.main()
