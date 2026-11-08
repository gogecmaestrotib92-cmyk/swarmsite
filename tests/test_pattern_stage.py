import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import shutil
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'swarm'))
import pattern_stage
sys.path.insert(0, str(ROOT / 'experiments' / 'design-patterns'))
import validate_transition
import verify_selected
import run


def fingerprint(directory, blueprint):
    p = Path(directory) / 'direction.json'
    return {'direction': hashlib.sha256(p.read_bytes()).hexdigest(), 'blueprint': blueprint}


class PatternStageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.verify = patch.object(pattern_stage, 'verify_transition')
        self.verify_mock = self.verify.start()
        self.dir = Path(self.tmp.name)
        self.direction = {'kind': 'place', 'hero': {'h1': 'Test'}, 'beats': [
            {'id': 'menu', 'type': 'ledger', 'h2': 'Menu', 'items': [['Soup', '12']], 'ui': {'move': 'invented'}},
            {'id': 'other', 'type': 'steps', 'steps': ['One', 'Two'], 'ui': {'move': 'pinned-sequence'}},
        ]}
        (self.dir / 'direction.json').write_text(json.dumps(self.direction))
        (self.dir / 'images.json').write_text('[]')

    def tearDown(self):
        self.verify.stop()
        self.tmp.cleanup()

    def process(self, tamper=False, mutate=False):
        outer = self
        class FakeProcess:
            returncode = 0
            pid = 123
            def __init__(self, cmd, **kwargs):
                self.staged = Path(cmd[-3])
                self.root = Path(kwargs['env']['TMPDIR'])
            def communicate(self, timeout=None):
                candidate = json.loads((self.staged / 'direction.json').read_text())
                assert all('move' not in b.get('ui', {}) for b in candidate['beats'])
                candidate['beats'][0]['ui']['move'] = 'cards'
                if tamper: candidate['beats'][0]['items'][0][1] = '99'
                trial = self.root / 'preview'; trial.mkdir()
                (trial / 'direction.json').write_text(json.dumps(candidate))
                if mutate: (outer.dir / 'images.json').write_text('[1]')
                return json.dumps({'choices': [{'beat': 'menu', 'pattern': 'ledger-cards', 'version': 1}], 'trial_directory': str(trial)}), ''
        return FakeProcess

    def test_only_selected_verified_move_is_applied(self):
        with patch.object(pattern_stage.subprocess, 'Popen', self.process()):
            result = pattern_stage.apply_verified_patterns(self.dir, 'butter', fingerprint)
        actual = json.loads((self.dir / 'direction.json').read_text())
        self.assertEqual(actual['beats'][0]['ui']['move'], 'cards')
        self.assertNotIn('move', actual['beats'][1]['ui'])
        self.assertEqual(actual['beats'][0]['items'], [['Soup', '12']])
        self.assertEqual(len(result['choices']), 1)

    def test_unexpected_content_change_is_rejected(self):
        with patch.object(pattern_stage.subprocess, 'Popen', self.process(tamper=True)):
            result = pattern_stage.apply_verified_patterns(self.dir, 'butter', fingerprint)
        actual = json.loads((self.dir / 'direction.json').read_text())
        self.assertEqual(actual['beats'][0]['items'], [['Soup', '12']])
        self.assertTrue(all('move' not in b['ui'] for b in actual['beats']))
        self.assertEqual(result['choices'], [])

    def test_changed_inputs_are_not_overwritten(self):
        def all_inputs(directory, blueprint):
            return (fingerprint(directory, blueprint), (Path(directory) / 'images.json').read_text())
        with patch.object(pattern_stage.subprocess, 'Popen', self.process(mutate=True)):
            with self.assertRaisesRegex(RuntimeError, 'changed'):
                pattern_stage.apply_verified_patterns(self.dir, 'butter', all_inputs)
        self.assertEqual(json.loads((self.dir / 'direction.json').read_text()), self.direction)

    def test_failure_uses_default_layout(self):
        class Failed:
            returncode = 1
            def __init__(self, *args, **kwargs): pass
            def communicate(self, timeout=None): return '', 'failure'
        with patch.object(pattern_stage.subprocess, 'Popen', Failed):
            result = pattern_stage.apply_verified_patterns(self.dir, 'butter', fingerprint)
        actual = json.loads((self.dir / 'direction.json').read_text())
        self.assertTrue(all('move' not in b['ui'] for b in actual['beats']))
        self.assertEqual(result['choices'], [])

    def test_timeout_stops_selector_and_uses_checked_default(self):
        class TimedOut:
            pid = 123
            def __init__(self, *args, **kwargs): self.calls = 0
            def communicate(self, timeout=None):
                self.calls += 1
                if self.calls == 1: raise subprocess.TimeoutExpired('selector', timeout)
                return '', ''
        with patch.object(pattern_stage.subprocess, 'Popen', TimedOut), patch.object(pattern_stage.os, 'killpg') as kill:
            result = pattern_stage.apply_verified_patterns(self.dir, 'butter', fingerprint, timeout=1)
        kill.assert_called_once()
        self.assertEqual(result['reason'], 'selector timed out')
        self.assertEqual(result['choices'], [])
        self.verify_mock.assert_called_once()

    def test_transition_detects_lost_rendered_content(self):
        old, new = self.dir / 'old', self.dir / 'new'
        old.mkdir(); new.mkdir()
        direction = json.loads((ROOT / 'tests' / 'direction.sample.json').read_text())
        for folder in (old, new):
            shutil.copyfile(ROOT / 'tests' / 'images.sample.json', folder / 'images.json')
            (folder / 'direction.json').write_text(json.dumps(direction))
        self.assertTrue(validate_transition.validate(old, new, 'white-desert'))
        section = next(beat for beat in direction['beats'] if beat.get('h2'))
        section['h2'] = 'A replacement heading'
        (new / 'direction.json').write_text(json.dumps(direction))
        with self.assertRaisesRegex(ValueError, 'content was lost'):
            validate_transition.validate(old, new, 'white-desert')

    def test_alternative_rejects_unsupported_move(self):
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            verify_selected.verify(self.dir, 'butter')
        direction = json.loads((self.dir / 'direction.json').read_text())
        for beat in direction['beats']: beat['ui'].pop('move', None)
        (self.dir / 'direction.json').write_text(json.dumps(direction))
        self.assertTrue(verify_selected.verify(self.dir, 'butter'))

    def test_automatic_selection_is_opt_in_until_quality_gate(self):
        with patch.dict('os.environ', {'SWARM_VERIFIED_PATTERNS': ''}), \
             patch.object(run.A, 'review_ledger_leads', return_value=0), \
             patch.object(run.Patterns, 'apply_verified_patterns', return_value={'choices': [], 'reason': 'checked'}) as select, \
             patch.object(run, 'render', return_value='rendered'):
            self.assertEqual(run.checked_render(str(self.dir), 'butter', 'out'), 'rendered')
            select.assert_not_called()
            with patch.dict('os.environ', {'SWARM_VERIFIED_PATTERNS': '1'}):
                self.assertEqual(run.checked_render(str(self.dir), 'butter', 'out'), 'rendered')
                select.assert_called_once()

if __name__ == '__main__': unittest.main()
