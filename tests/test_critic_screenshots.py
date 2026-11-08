import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('swarm_critic', ROOT / 'lib/qa/critic.py')
critic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(critic)


class CriticScreenshotsTest(unittest.TestCase):
    def test_balanced_screens_reach_model_including_first_and_last(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'direction.json').write_text(json.dumps({'hero': {}, 'beats': []}))
            (root / 'page.html').write_text('<!doctype html><html></html>')
            files = []
            for viewport in ('desktop', 'mobile'):
                for section in range(15):
                    name = root / f'{viewport}-{section:02}-section.png'
                    Image.new('RGB', (8, 8), 'white').save(name)
                    files.append(str(name))
            sent = {}

            def create(**kwargs):
                sent.update(kwargs)
                return types.SimpleNamespace(content=[types.SimpleNamespace(type='tool_use', input={'score': 80, 'fixes': []})])

            fake_client = types.SimpleNamespace(Anthropic=lambda: types.SimpleNamespace(messages=types.SimpleNamespace(create=create)))
            with patch.dict(sys.modules, {'anthropic': fake_client}), patch.object(critic, 'shots', return_value=files):
                report = critic.critique(directory, str(root / 'page.html'))

            self.assertEqual(report['score'], 80)
            content = sent['messages'][0]['content']
            names = [item['text'].removeprefix('SCREEN: ') for item in content if item['type'] == 'text' and item['text'].startswith('SCREEN: ')]
            self.assertEqual(len(names), 28)
            for viewport in ('desktop', 'mobile'):
                selected = [name for name in names if name.startswith(viewport + '-')]
                self.assertEqual(len(selected), 14)
                self.assertIn(f'{viewport}-00-section.png', selected)
                self.assertIn(f'{viewport}-14-section.png', selected)

    def test_twenty_screens_include_every_section_for_both_viewports(self):
        files = [f'{viewport}-{section:02}-{name}.png' for viewport in ('desktop', 'mobile')
                 for section, name in enumerate(('top', 'quote', 'ph2', 'sec', 'bacalao', 'brasa', 'salon', 'facts', 'reserva', 'end'))]
        self.assertEqual(critic.select_screenshots(files), files)

    def test_rendered_external_booking_is_described_as_a_link(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            direction = {'hero': {}, 'beats': [
                {'id': 'booking', 'type': 'form', 'fields': ['Name', 'Date']},
                {'id': 'missing', 'type': 'form', 'fields': ['Email']},
                {'id': 'onsite', 'type': 'form', 'fields': ['Phone']},
            ]}
            (root / 'direction.json').write_text(json.dumps(direction))
            page = root / 'page.html'
            page.write_text('<section id="booking"><a class="btn" href="https://example.test/book">Reserve<span>→</span></a></section>'
                            '<section id="missing"></section><section id="onsite"><form><input></form></section>')
            image = root / 'desktop-00-top.png'
            Image.new('RGB', (8, 8), 'white').save(image)
            sent = {}

            def create(**kwargs):
                sent.update(kwargs)
                return types.SimpleNamespace(content=[types.SimpleNamespace(type='tool_use', input={'score': 80, 'fixes': []})])

            fake_client = types.SimpleNamespace(Anthropic=lambda: types.SimpleNamespace(messages=types.SimpleNamespace(create=create)))
            with patch.dict(sys.modules, {'anthropic': fake_client}), patch.object(critic, 'shots', return_value=[str(image)]):
                critic.critique(directory, str(page))

            prompt = sent['messages'][0]['content'][0]['text']
            self.assertIn('https://example.test/book', prompt)
            self.assertIn('Sections ["booking"] use a link', prompt)
            self.assertNotIn('"fields": ["Name", "Date"]', prompt)
            self.assertIn('"fields": ["Email"]', prompt)
            self.assertIn('"fields": ["Phone"]', prompt)

    def test_fast_capture_requests_both_viewports(self):
        with tempfile.TemporaryDirectory() as directory:
            def run(args, **kwargs):
                self.assertIn('--fast', args)
                self.assertNotIn('--desktop-only', args)
                for name in ('desktop-00-top.png', 'mobile-00-top.png'):
                    Path(directory, name).touch()
                return types.SimpleNamespace(returncode=0, stderr='', stdout='')

            with patch.object(critic.subprocess, 'run', side_effect=run):
                files = critic.shots('page.html', directory, fast=True)
            self.assertEqual([os.path.basename(f) for f in files], ['desktop-00-top.png', 'mobile-00-top.png'])

    def test_failed_capture_does_not_use_partial_screenshots(self):
        with tempfile.TemporaryDirectory() as directory:
            def run(args, **kwargs):
                Path(directory, 'desktop-00-top.png').touch()
                return types.SimpleNamespace(returncode=1, stderr='mobile capture failed', stdout='')

            with patch.object(critic.subprocess, 'run', side_effect=run):
                with self.assertRaisesRegex(RuntimeError, 'screenshot capture failed: mobile capture failed'):
                    critic.shots('page.html', directory)

    def test_single_viewport_keeps_first_and_last(self):
        files = [f'desktop-{section:02}-section.png' for section in range(35)]
        selected = critic.select_screenshots(files)
        self.assertEqual(len(selected), 28)
        self.assertEqual((selected[0], selected[-1]), (files[0], files[-1]))

    def test_section_overviews_are_prioritized_and_budget_is_balanced(self):
        primary = [f'{viewport}-{section:02}-section.png' for viewport in ('desktop', 'mobile')
                   for section in range(13)]
        slides = [f'{viewport}-04-tour-slide-{slide:02}-of-03.png' for viewport in ('desktop', 'mobile')
                  for slide in (1, 2, 3)]
        selected = critic.select_screenshots(primary + slides)
        self.assertEqual(len(selected), 28)
        self.assertTrue(set(primary).issubset(selected))
        for viewport in ('desktop', 'mobile'):
            self.assertIn(f'{viewport}-04-tour-slide-03-of-03.png', selected)

    def test_first_and_last_pinned_slides_are_kept_when_budget_allows(self):
        primary = [f'{viewport}-{section:02}-section.png' for viewport in ('desktop', 'mobile')
                   for section in range(10)]
        slides = [f'{viewport}-04-tour-slide-{slide:02}-of-03.png' for viewport in ('desktop', 'mobile')
                  for slide in (1, 2, 3)]
        selected = critic.select_screenshots(primary + slides)
        for viewport in ('desktop', 'mobile'):
            self.assertIn(f'{viewport}-04-tour-slide-01-of-03.png', selected)
            self.assertIn(f'{viewport}-04-tour-slide-03-of-03.png', selected)


if __name__ == '__main__':
    unittest.main()
