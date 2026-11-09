"""Taste and contract are reported side by side, each against its own bar. A high contract never stands in for taste,
and a page with a broken screen is not technically sound however it is scored. Reported, not enforced."""
import io, json, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'swarm'))
import agents
import run


def log(*rounds): return {'rounds': [dict(r) for r in rounds]}


class Scorecard(unittest.TestCase):
    def test_a_sound_but_generic_page_passes_one_gate_only(self):
        card = run.scorecard(log({'k': 1, 'taste': 52, 'contract': 97, 'score': 72, 'broken': [], 'axes': {'design': 55, 'originality': 42, 'craft': 50, 'function': 62}}), 1)
        self.assertTrue(card['technical']['pass']); self.assertFalse(card['creative']['pass'])
        self.assertEqual((card['taste'], card['contract'], card['blended']), (52, 97, 72))
        self.assertEqual(card['axes']['originality'], 42); self.assertFalse(card['enforced'])

    def test_a_broken_screen_fails_the_technical_gate_whatever_the_score(self):
        card = run.scorecard(log({'k': 1, 'taste': 90, 'contract': 96, 'score': 93, 'broken': [{'id': 'mobile-no-overflow', 'detail': 'x', 'weight': 2}, {'id': 'h2-short', 'detail': 'y', 'weight': 1}]}), 1)
        self.assertFalse(card['technical']['pass']); self.assertEqual(card['technical']['hard_failures'], ['mobile-no-overflow'])
        self.assertTrue(card['creative']['pass'])

    def test_a_style_promise_alone_does_not_fail_the_technical_gate(self):
        card = run.scorecard(log({'k': 2, 'taste': 60, 'contract': 94, 'score': 75, 'broken': [{'id': 'h2-short', 'detail': 'y', 'weight': 1}]}), 2)
        self.assertTrue(card['technical']['pass']); self.assertEqual(card['technical']['hard_failures'], [])

    def test_the_card_describes_the_round_that_ships_not_the_last_one(self):
        card = run.scorecard(log({'k': 1, 'taste': 58, 'contract': 100, 'score': 77, 'broken': []}, {'k': 2, 'taste': 52, 'contract': 96, 'score': 72, 'broken': []}), 1)
        self.assertEqual((card['round'], card['taste']), (1, 58))
        self.assertIsNone(run.scorecard(log(), 1))

    def test_bars_come_from_the_environment_and_bad_values_fall_back(self):
        rounds = log({'k': 1, 'taste': 60, 'contract': 88, 'score': 73, 'broken': []})
        with patch.dict(os.environ, {'GATE_CREATIVE': '55', 'GATE_TECHNICAL': '85'}):
            card = run.scorecard(rounds, 1); self.assertTrue(card['creative']['pass']); self.assertTrue(card['technical']['pass'])
        with patch.dict(os.environ, {'GATE_CREATIVE': 'high', 'GATE_TECHNICAL': ''}):
            card = run.scorecard(rounds, 1); self.assertEqual((card['creative']['min'], card['technical']['min']), (70, 90))
            self.assertFalse(card['creative']['pass']); self.assertFalse(card['technical']['pass'])

    def test_a_missing_score_never_passes(self):
        card = run.scorecard(log({'k': 1, 'taste': None, 'contract': True, 'score': None, 'broken': None}), 1)
        self.assertFalse(card['technical']['pass']); self.assertFalse(card['creative']['pass'])


class LoopWritesTheCard(unittest.TestCase):
    def test_scores_and_fingerprint_are_written_for_the_page_that_ships(self):
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'direction.json', {'hero': {'h1': 'Headline'}, 'beats': []})
            agents.W(directory, 'factsheet.json', {})
            agents.W(directory, 'inventory.json', {'url': 'https://example.test', 'sourceCoverage': {'sections': [{'id': 's1', 'title': 'page 1'}], 'routes': []}})
            output = Path(directory) / 'page.html'; state = {'round': 0}

            def render(folder, blueprint, path):
                state['round'] += 1
                Path(path).write_text(f'<section class="sec hero split" id="top"></section><section class="sec cards band-dark" id="r{state["round"]}"></section><section class="sec cta"></section>')

            def contract(folder, path):
                result = {'score': 97, 'failed': [{'id': 'desktop-no-empty-screens', 'detail': 'one empty screen', 'weight': 2}] if state['round'] == 1 else []}
                agents.W(folder, 'contract.json', result); return result

            def critique(*args):
                return {'score': {1: 58, 2: 40}[state['round']], 'axes': {'design': 60, 'originality': 44, 'craft': 55, 'function': 62}, 'verdict': 'tidy but anonymous',
                        'fixes': [{'op': 'note', 'agent': 'ui', 'reason': 'Improve'}]}

            printed = io.StringIO()
            with patch.object(run.sys, 'argv', ['run.py', directory, 'butter', '--out', str(output), '--rounds', '3']), \
                    patch.object(run, 'render', render), patch.object(run, 'contract', contract), patch.object(run.C, 'critique', critique), \
                    patch.object(agents, 'ui', lambda folder, notes='', blueprint_id=None: int(bool(notes))), \
                    patch.object(agents, 'concept', return_value=0), patch.object(agents, 'ux', return_value=0), \
                    patch.object(agents, 'visual', return_value=0), patch.object(agents, 'copy', return_value=0), redirect_stdout(printed):
                run.main()

            card = agents.J(directory, 'scores.json')
            self.assertEqual((card['round'], card['taste'], card['contract']), (1, 58, 97))
            self.assertFalse(card['creative']['pass'])
            self.assertFalse(card['technical']['pass'], 'contract 97 with an empty screen is not technically sound')
            self.assertEqual(card['technical']['hard_failures'], ['desktop-no-empty-screens'])
            self.assertEqual(card['axes']['originality'], 44)
            fp = agents.J(directory, 'fingerprint.json')
            self.assertEqual(fp['signature'], ['hero.split', 'cards', 'cta']); self.assertEqual(fp['body'], ['cards'])
            trace = agents.J(directory, 'swarm.json')
            self.assertEqual(trace['scores'], card); self.assertEqual(trace['fingerprint']['digest'], fp['digest'])
            self.assertEqual(trace['rounds'][0]['axes']['design'], 60)
            lines = [json.loads(l) for l in printed.getvalue().splitlines() if l.startswith('{')]
            done = next(l['done'] for l in lines if 'done' in l)
            self.assertEqual(done['scores']['taste'], 58); self.assertEqual(done['score'], trace['best'])
            said = [l['event']['text'] for l in lines if 'event' in l and l['event']['role'] == 'Critic']
            self.assertTrue(any('design 58/100 (below 70)' in t and 'technical 97/100 (broken: desktop-no-empty-screens)' in t for t in said), said)


if __name__ == '__main__':
    unittest.main()
