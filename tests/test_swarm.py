import json
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'swarm'))
import agents
import run


class AgentUpdateTests(unittest.TestCase):
    def test_unchanged_layout_is_not_reported_as_a_change(self):
        with tempfile.TemporaryDirectory() as directory:
            direction = {'hero': {'h1': 'Headline', 'ui': {'size': 'M'}},
                         'beats': [{'id': 'menu', 'type': 'features', 'band': 'paper', 'ui': {'cols': 3}}]}
            agents.W(directory, 'direction.json', direction)
            changed = agents.apply_ui(directory, {'hero': {'size': 'M'},
                'beats': [{'id': 'menu', 'cols': 3, 'band': 'paper'}]})
            self.assertEqual(changed, 0)

    def test_visual_metadata_alone_is_not_a_render_change(self):
        with tempfile.TemporaryDirectory() as directory:
            direction = {'hero': {'h1': 'Headline'}, 'beats': []}
            agents.W(directory, 'direction.json', direction)
            agents.W(directory, 'images.json', [])
            with patch.dict('os.environ', {'HIGGSFIELD_KEY': ''}):
                changed = agents.apply_visual(directory, {'hero': '', 'need': ['A photograph']})
            self.assertEqual(changed, 0)
            self.assertEqual(agents.J(directory, 'direction.json')['swarm']['visual']['need'], ['A photograph'])

    def test_critic_ui_fix_does_not_rewrite_unrelated_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            direction = {'hero': {'h1': 'Headline', 'ui': {'size': 'M'}}, 'beats': [
                {'id': 'menu', 'type': 'features', 'band': 'paper', 'ui': {'cols': 3}},
                {'id': 'contact', 'type': 'form', 'band': 'dark', 'ui': {'cols': 1}},
            ]}
            agents.W(directory, 'direction.json', direction)
            reply = {'hero': {'size': 'L'}, 'beats': [
                {'id': 'menu', 'cols': 2}, {'id': 'contact', 'band': 'paper'},
            ]}
            with patch.object(agents, 'ask', return_value=reply):
                changed = agents.ui(directory, '[layout] beat=menu  — Reduce the columns')
            result = agents.J(directory, 'direction.json')
            self.assertGreater(changed, 0)
            self.assertEqual(result['hero']['ui']['size'], 'M')
            self.assertEqual(result['beats'][0]['ui']['cols'], 2)
            self.assertEqual(result['beats'][1]['band'], 'dark')

    def test_global_contract_feedback_can_change_any_section(self):
        with tempfile.TemporaryDirectory() as directory:
            direction = {'hero': {'h1': 'Headline'}, 'beats': [
                {'id': 'menu', 'type': 'features', 'ui': {'cols': 3}},
                {'id': 'contact', 'type': 'form', 'band': 'dark'},
            ]}
            agents.W(directory, 'direction.json', direction)
            reply = {'beats': [{'id': 'menu', 'cols': 2}, {'id': 'contact', 'band': 'paper'}]}
            with patch.object(agents, 'ask', return_value=reply):
                agents.ui(directory, '[note] beat=  — CONTRACT BROKEN: overflow')
            result = agents.J(directory, 'direction.json')
            self.assertEqual(result['beats'][0]['ui']['cols'], 2)
            self.assertEqual(result['beats'][1]['band'], 'paper')

    def test_hero_layout_preserves_concept_move(self):
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'direction.json', {'hero': {'media': 'shot'}, 'beats': []})
            agents.apply_concept(directory, {'hero_move': 'split'})
            agents.apply_ui(directory, {'hero': {'size': 'L', 'align': 'start'}})
            self.assertEqual(agents.J(directory, 'direction.json')['hero']['ui'],
                             {'move': 'split', 'size': 'L', 'align': 'start'})

    def test_billboard_requires_assigned_photo_and_survives_ui(self):
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'direction.json', {'hero': {'media': 'hero'}, 'beats': []})
            agents.W(directory, 'images.json', [{'id': 'hero', 'data': 'photo', 'shot': True}])
            agents.apply_concept(directory, {'hero_move': 'billboard'})
            self.assertNotEqual((agents.J(directory, 'direction.json')['hero'].get('ui') or {}).get('move'), 'billboard')
            agents.W(directory, 'images.json', [{'id': 'hero', 'data': 'photo', 'shot': False}])
            agents.apply_concept(directory, {'hero_move': 'billboard'})
            agents.apply_ui(directory, {'hero': {'size': 'L'}})
            self.assertEqual(agents.J(directory, 'direction.json')['hero']['ui']['move'], 'billboard')

    def test_editorial_type_requires_service_kind(self):
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'direction.json', {'kind': 'software', 'hero': {}, 'beats': []})
            agents.apply_concept(directory, {'hero_move': 'editorial-type'})
            self.assertFalse((agents.J(directory, 'direction.json')['hero'].get('ui') or {}).get('move'))
            agents.W(directory, 'direction.json', {'kind': 'service', 'hero': {'media': 'hero'}, 'beats': []})
            agents.W(directory, 'images.json', [{'id': 'hero', 'data': 'photo'}])
            agents.apply_concept(directory, {'hero_move': 'editorial-type'})
            self.assertEqual(agents.J(directory, 'direction.json')['hero']['ui']['move'], 'editorial-type')

    def test_concept_repair_changes_only_targeted_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            direction = {'hero': {'h1': 'Headline', 'media': 'shot', 'ui': {'move': 'split'}}, 'beats': [
                {'id': 'menu', 'type': 'features', 'ui': {'move': 'cards'}},
                {'id': 'quote', 'type': 'quote', 'body': 'A memorable sentence with at least eight words here', 'ui': {'move': 'type-wall'}},
            ]}
            agents.W(directory, 'direction.json', direction)
            reply = {'idea': 'New idea', 'hero_move': 'default', 'beats': [
                {'id': 'menu', 'move': 'story'}, {'id': 'quote', 'move': 'auto'},
            ]}
            with patch.object(agents, 'ask', return_value=reply) as ask:
                changed = agents.concept(directory, '[layout] beat=menu — Add a large image beside the copy')
            result = agents.J(directory, 'direction.json')
            self.assertGreater(changed, 0)
            self.assertEqual(result['hero']['ui']['move'], 'split')
            self.assertEqual(result['beats'][0]['ui']['move'], 'story')
            self.assertEqual(result['beats'][1]['ui']['move'], 'type-wall')
            self.assertIn('"current_move": "cards"', ask.call_args.args[1][0]['text'])

    def test_concept_repair_counts_existing_pinned_and_type_wall_moves(self):
        with tempfile.TemporaryDirectory() as directory:
            direction = {'hero': {}, 'beats': [
                {'id': 'existing-pin', 'type': 'features', 'ui': {'move': 'sticky-product'}},
                {'id': 'existing-wall', 'type': 'quote', 'ui': {'move': 'type-wall'}},
                {'id': 'menu', 'type': 'features', 'ui': {'move': 'story'}},
                {'id': 'quote', 'type': 'quote', 'body': 'A memorable sentence with at least eight words here', 'ui': {'move': 'auto'}},
            ]}
            agents.W(directory, 'direction.json', direction)
            reply = {'idea': 'Idea', 'beats': [
                {'id': 'menu', 'move': 'pinned-sequence'}, {'id': 'quote', 'move': 'type-wall'},
            ]}
            with patch.object(agents, 'ask', return_value=reply):
                agents.concept(directory, '[layout] beat=menu — Rearrange\n[layout] beat=quote — Emphasize')
            moves = [(b.get('ui') or {}).get('move') for b in agents.J(directory, 'direction.json')['beats']]
            self.assertEqual(moves[:2], ['sticky-product', 'type-wall'])
            self.assertNotIn(moves[2], ('sticky-product', 'pinned-sequence'))
            self.assertNotEqual(moves[3], 'type-wall')

    def test_concurrent_agent_changes_survive(self):
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'direction.json', {'hero': {'h1': 'Old headline'}, 'beats': []})
            barrier = threading.Barrier(2)
            original_read = agents.J

            def delayed_read(*args):
                result = original_read(*args)
                if args[1] == 'direction.json':
                    time.sleep(.02)
                return result

            def ask(system, content, tool, **kwargs):
                barrier.wait(timeout=5)
                if tool['name'] == 'rewrite':
                    return {'edits': [{'path': 'hero.h1', 'value': 'New headline'}]}
                return {'hero': {'size': 'L'}, 'beats': []}

            with patch.object(agents, 'ask', ask), patch.object(agents, 'J', delayed_read):
                with ThreadPoolExecutor(2) as pool:
                    copy = pool.submit(agents.copy, directory, 'Change the headline')
                    ui = pool.submit(agents.ui, directory, 'Change the hero size')
                    self.assertEqual(copy.result(), 1)
                    self.assertEqual(ui.result(), 1)

            hero = agents.J(directory, 'direction.json')['hero']
            self.assertEqual(hero['h1'], 'New headline')
            self.assertEqual(hero['ui']['size'], 'L')


class FeedbackRoutingTests(unittest.TestCase):
    def test_layout_feedback_also_reaches_concept_for_a_section(self):
        direction = {'beats': [{'id': 'menu', 'type': 'features'}, {'id': 'contact', 'type': 'form'}]}
        fixes = [
            {'op': 'layout', 'agent': 'ui', 'beat': 'menu', 'reason': 'Make the visual larger'},
            {'op': 'layout', 'agent': 'ui', 'beat': 'contact', 'reason': 'Increase the title'},
            {'op': 'layout', 'agent': 'ui', 'beat': 'hero', 'reason': 'Increase the title'},
            {'op': 'note', 'agent': 'ui', 'beat': '', 'reason': 'CONTRACT BROKEN'},
            {'op': 'swap_image', 'agent': 'visual', 'beat': 'menu', 'reason': 'Sharper photograph'},
        ]
        notes = run.route_fixes(fixes, direction)
        self.assertEqual(len(notes['ui']), 4)
        self.assertEqual(len(notes['concept']), 1)
        self.assertIn('beat=menu', notes['concept'][0])
        self.assertIn('Make the visual larger', notes['concept'][0])
        self.assertEqual(len(notes['visual']), 1)

    def test_explicit_concept_operation_routes_to_concept_by_default(self):
        notes = run.route_fixes([{'op': 'concept', 'beat': 'menu', 'reason': 'Change the rhythm'}],
                                {'beats': [{'id': 'menu', 'type': 'features'}]})
        self.assertEqual(len(notes['concept']), 1)
        self.assertEqual(notes['ui'], [])


class ContractTests(unittest.TestCase):
    def setUp(self):
        stage = patch.object(run.Patterns, 'apply_verified_patterns', return_value={'choices': [], 'reason': 'stubbed'})
        stage.start()
        self.addCleanup(stage.stop)
    def test_no_gain_on_second_round_still_tries_the_remaining_round(self):
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'direction.json', {'hero': {'h1': 'Headline'}, 'beats': []})
            agents.W(directory, 'factsheet.json', {})
            agents.W(directory, 'images.json', [])
            output = Path(directory) / 'page.html'
            rendered = []

            def render(folder, blueprint, path):
                rendered.append(len(rendered) + 1)
                Path(path).write_text(f'page {len(rendered)}')

            def contract(folder, path):
                result = {'score': 100, 'failed': []}
                agents.W(folder, 'contract.json', result)
                return result

            def critique(*args):
                score = 70 if len(rendered) < 3 else 80
                return {'score': score, 'fixes': [{'op': 'note', 'agent': 'ui', 'reason': 'Improve'}]}

            def ui(folder, notes='', blueprint_id=None):
                return int(bool(notes))

            with patch.object(run.sys, 'argv', ['run.py', directory, 'butter', '--out', str(output), '--rounds', '3']), \
                    patch.object(run, 'render', render), patch.object(run, 'contract', contract), \
                    patch.object(run.C, 'critique', critique), patch.object(agents, 'ui', ui), \
                    patch.object(agents, 'concept', return_value=0), patch.object(agents, 'ux', return_value=0), \
                    patch.object(agents, 'visual', return_value=0), patch.object(agents, 'copy', return_value=0):
                run.main()

            self.assertEqual(rendered, [1, 2, 3])
            self.assertEqual(output.read_text(), 'page 3')
            self.assertEqual(agents.J(directory, 'swarm.json')['best_round'], 3)

    def test_target_score_does_not_hide_critic_defects(self):
        for first_taste in (64, 90):
            with self.subTest(taste=first_taste), tempfile.TemporaryDirectory() as directory:
                agents.W(directory, 'direction.json', {'hero': {'h1': 'Headline'}, 'beats': []})
                agents.W(directory, 'factsheet.json', {})
                agents.W(directory, 'images.json', [])
                output = Path(directory) / 'page.html'
                rendered = []
                routed = []

                def render(folder, blueprint, path):
                    rendered.append(len(rendered) + 1)
                    Path(path).write_text(f'page {len(rendered)}')

                def contract(folder, path):
                    result = {'score': 100, 'failed': []}
                    agents.W(folder, 'contract.json', result)
                    return result

                def critique(*args):
                    if len(rendered) == 1:
                        return {'score': first_taste, 'fixes': [{'op': 'note', 'agent': 'ui', 'reason': 'Visible defect'}]}
                    return {'score': 90, 'fixes': []}

                def ui(folder, notes='', blueprint_id=None):
                    if notes: routed.append(notes)
                    return int(bool(notes))

                with patch.object(run.sys, 'argv', ['run.py', directory, 'butter', '--out', str(output), '--rounds', '2']), \
                        patch.object(run, 'render', render), patch.object(run, 'contract', contract), \
                        patch.object(run.C, 'critique', critique), patch.object(agents, 'ui', ui), \
                        patch.object(agents, 'concept', return_value=0), patch.object(agents, 'ux', return_value=0), \
                        patch.object(agents, 'visual', return_value=0), patch.object(agents, 'copy', return_value=0):
                    run.main()

                self.assertEqual(len(rendered), 2)
                self.assertTrue(any('Visible defect' in notes for notes in routed))
                self.assertEqual(output.read_text(), 'page 2')

    def test_failed_contract_does_not_reuse_existing_report(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / 'contract.json'
            report.write_text(json.dumps({'score': 100, 'failed': []}))
            failed = SimpleNamespace(returncode=1, stderr='browser failed', stdout='')
            with patch.object(run.subprocess, 'run', return_value=failed):
                with self.assertRaisesRegex(RuntimeError, 'browser failed'):
                    run.contract(directory, 'page.html')
            self.assertFalse(report.exists())

    def test_missing_contract_report_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = SimpleNamespace(returncode=0, stderr='', stdout='')
            with patch.object(run.subprocess, 'run', return_value=completed):
                with self.assertRaisesRegex(RuntimeError, 'invalid report'):
                    run.contract(directory, 'page.html')

    def test_clean_round_wins_and_restores_matching_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory, 'direction.json', {'hero': {'h1': 'Headline'}, 'beats': []})
            agents.W(directory, 'factsheet.json', {})
            agents.W(directory, 'inventory.json', {'url': 'https://example.test', 'sourceCoverage': {
                'sections': [{'id': 's1', 'title': 'page 2'}], 'routes': []}})
            output = Path(directory) / 'page.html'
            round_number = 0

            def render(folder, blueprint, path):
                nonlocal round_number
                round_number += 1
                Path(path).write_text(f'page {round_number}')
                agents.W(folder, 'images.json', [{'id': f'image-{round_number}'}])
                direction = agents.J(folder, 'direction.json')
                direction['hero']['h1'] = f'Headline {round_number}'
                agents.W(folder, 'direction.json', direction)

            def contract(folder, path):
                broken = [] if round_number == 2 else [
                    {'id': 'mobile-no-overflow', 'detail': 'overflow', 'weight': 2}]
                result = {'score': 100, 'failed': broken}
                agents.W(folder, 'contract.json', result)
                return result

            def critique(*args):
                shots = Path(directory) / 'critic-shots'
                shots.mkdir(exist_ok=True)
                for old in shots.glob('*.png'): old.unlink()
                (shots / f'desktop-{round_number}.png').write_bytes(f'screenshot {round_number}'.encode())
                (shots / 'notes.txt').write_text('keep this unrelated file')
                return {'score': {1: 90, 2: 25, 3: 100}[round_number],
                        'verdict': f'round {round_number}',
                        'fixes': [{'op': 'note', 'agent': 'ui', 'reason': 'Improve'}]}

            def ui(folder, notes='', blueprint_id=None):
                return int(bool(notes))

            with patch.object(run.sys, 'argv', ['run.py', directory, 'butter', '--out', str(output), '--rounds', '3']), \
                    patch.object(run, 'render', render), patch.object(run, 'contract', contract), \
                    patch.object(run.C, 'critique', critique), patch.object(agents, 'ui', ui), \
                    patch.object(agents, 'concept', return_value=0), patch.object(agents, 'ux', return_value=0), \
                    patch.object(agents, 'visual', return_value=0), patch.object(agents, 'copy', return_value=0):
                run.main()

            self.assertEqual(round_number, 3)
            self.assertEqual(output.read_text(), 'page 2')
            self.assertEqual(agents.J(directory, 'direction.json')['hero']['h1'], 'Headline 2')
            self.assertEqual(agents.J(directory, 'images.json')[0]['id'], 'image-2')
            self.assertEqual(agents.J(directory, 'contract.json')['failed'], [])
            self.assertEqual(agents.J(directory, 'critic.json')['round'], 2)
            self.assertEqual(agents.J(directory, 'swarm.json')['best_round'], 2)
            shots = Path(directory) / 'critic-shots'
            self.assertEqual((shots / 'desktop-2.png').read_bytes(), b'screenshot 2')
            self.assertFalse((shots / 'desktop-3.png').exists())
            self.assertEqual((shots / 'notes.txt').read_text(), 'keep this unrelated file')
            # Coverage must refer to the selected, restored HTML, not the last attempted round.
            self.assertEqual(agents.J(directory, 'coverage.json')['sections'][0]['status'], 'text_detected')

    def test_missing_best_shots_remove_later_shots_without_touching_other_files(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as snapshot:
            run.snapshot_shots(directory, snapshot)
            shots = Path(directory) / 'critic-shots'
            shots.mkdir()
            (shots / 'later.png').write_bytes(b'other round')
            (shots / 'notes.txt').write_text('keep')
            run.restore_shots(directory, snapshot)
            self.assertFalse((shots / 'later.png').exists())
            self.assertEqual((shots / 'notes.txt').read_text(), 'keep')

    def test_failed_snapshot_cleans_temporary_directory(self):
        actual_tempdir = tempfile.TemporaryDirectory
        created = []
        def tempdir(*args, **kwargs):
            result = actual_tempdir(*args, **kwargs)
            created.append(Path(result.name))
            return result
        with patch.object(run.tempfile, 'TemporaryDirectory', side_effect=tempdir), \
                patch.object(run, '_main', side_effect=OSError('snapshot failed')):
            with self.assertRaisesRegex(OSError, 'snapshot failed'):
                run.main()
        self.assertEqual(len(created), 1)
        self.assertFalse(created[0].exists())

    def test_snapshot_copy_failure_is_reported_without_deleting_original(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as snapshot:
            shots = Path(directory) / 'critic-shots'
            shots.mkdir()
            source = shots / 'desktop.png'
            source.write_bytes(b'original')
            with patch.object(run.shutil, 'copy2', side_effect=OSError('disk full')):
                with self.assertRaisesRegex(OSError, 'disk full'):
                    run.snapshot_shots(directory, snapshot)
            self.assertEqual(source.read_bytes(), b'original')


if __name__ == '__main__':
    unittest.main()
