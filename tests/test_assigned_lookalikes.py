"""Regression: pdfbeautifier.com (2026-11-09) rendered with zero pictures although the source had three.

Three guards fired together: the hero reviewer said UNCERTAIN (and the gate emptied the hero), the 64-bit
look-alike hash merged two pages of the same document into one 'family' so the story slot was 'already used',
and a features pinned-sequence without per-feature pictures became a five-screen text ladder.
"""
import base64
import importlib.util
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('render_bp_lookalikes', ROOT / 'lib/render/render_bp.py')
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


def page(w, h, seed=0):
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (w, h), (255, 255, 255)); dr = ImageDraw.Draw(im)
    y = int(h * .08)
    while y < h * .95:
        dr.rectangle([int(w * .08), y, int(w * .08 + w * .84 * (.5 + ((y * 7 + seed) % 50) / 100)), y + max(2, h // 120)], fill=(40, 40, 48)); y += max(6, h // 40)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=60)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def direction(decision):
    return {
        'blueprint': 'cerebrium', 'kind': 'software', 'mode': 'dark', 'voice': 'sans',
        'brand': {'name': 'Doc Dresser', 'keep_font': False},
        'nav': {'links': [['#result', 'Result']], 'cta': 'Upload'},
        'hero': {'category': 'Document redesign', 'fact': 'Under 30 sec', 'h1': 'Your PDF, <em>redesigned.</em>', 'lede': 'Drop a document.',
                 'cta': 'Upload a PDF', 'cta_href': 'https://example.com/', 'media': 'img2', 'ui': {'move': 'split', 'size': 'L'},
                 'visual_verified': False, 'visual_review': {'id': 'img2', 'decision': decision}},
        'beats': [
            {'id': 'result', 'type': 'photo', 'label': 'The result', 'h2': 'Same words. Different presence.', 'lede': 'Preview it free.',
             'image': 'img3', 'cap': ['Page 2', '0 words changed'], 'ui': {'move': 'story', 'photo_layout': 'split'}, 'band': 'dark'},
            {'id': 'templates', 'type': 'features', 'label': 'Templates', 'h2': 'Five art directions', 'lede': 'Each a system.',
             'features': [{'title': f'Style {i}', 'body': f'Detail {i}'} for i in range(1, 6)], 'ui': {'move': 'pinned-sequence'}, 'band': 'dark'},
            {'id': 'faq', 'type': 'faq', 'label': 'FAQ', 'h2': 'Questions', 'items': [['Does it change my text?', 'Never.'], ['Formats?', 'PDF, DOCX, TXT.']], 'ui': {'move': 'cards'}},
        ],
        'ending': {'tag': 'Same words.', 'cols': [], 'next': 'Upload', 'legal': '© Doc Dresser'},
        'audit_notes': [], 'swarm': {},
    }


IMAGES = [
    {'id': 'img1', 'src': 'https://example.com/before.png', 'w': 1400, 'h': 1980, 'alt': 'Before', 'bg': False, 'lum': 228, 'data': page(1400, 1980, 0)},
    {'id': 'img2', 'src': 'https://example.com/after-1.png', 'w': 1400, 'h': 1978, 'alt': 'After page 1', 'bg': False, 'lum': 241, 'data': page(1400, 1978, 0)},
    {'id': 'img3', 'src': 'https://example.com/after-2.png', 'w': 1400, 'h': 1978, 'alt': 'After page 2', 'bg': False, 'lum': 242, 'data': page(1400, 1978, 3)},
]


def sections(html):
    return {m.group(2): (m.group(1), len(re.findall(r'<img', m.group(3)))) for m in re.finditer(r'<section class="sec ([^"]*)" id="([^"]*)"(.*?)</section>', html, re.S)}


class AssignedLookalikes(unittest.TestCase):
    def render(self, decision):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); (p / 'direction.json').write_text(json.dumps(direction(decision))); (p / 'images.json').write_text(json.dumps(IMAGES))
            (p / 'assets.json').write_text('{}'); (p / 'brief.json').write_text('{}')
            render.build(d, 'cerebrium', str(p / 'index.html'))
            self.last_html = (p / 'index.html').read_text(); return self.last_html

    def test_uncertain_review_keeps_the_directed_hero_and_the_lookalike_story_picture(self):
        secs = sections(self.render('UNCERTAIN'))
        self.assertGreaterEqual(secs['top'][1], 1, 'UNCERTAIN is not NOT_PRODUCT: the hero keeps the picture the director chose')
        self.assertEqual(secs['top'][1], 2, 'a document product is a stack of its own pages in the hero: the result on top, the original behind')
        self.assertIn('doc-stack', self.last_html)
        self.assertEqual(secs['result'][1], 1, 'page 2 is assigned to its own slot; the hero stack must not use it up')
        self.assertNotIn('pinned', secs['templates'][0], 'five text-only slides are cards, not a pinned ladder')

    def test_not_product_still_empties_the_hero(self):
        secs = sections(self.render('NOT_PRODUCT'))
        self.assertEqual(secs['top'][1], 0)
        self.assertEqual(secs['result'][1], 2, 'without a hero stack, the source\'s own Before page stands beside the result')
        self.assertIn('before-after', self.last_html)


if __name__ == '__main__':
    unittest.main()
