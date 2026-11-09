"""What the director writes is model output built from a stranger's website. Three fields used to reach the page
without a check: nav link targets, the brand's paper/ink colours, and a beat's band. None may carry markup or script."""
import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render(edit, blueprint='butter'):
    with tempfile.TemporaryDirectory() as temp:
        job = Path(temp)
        for name in ('direction', 'images', 'inventory', 'assets'):
            src = ROOT / 'tests' / f'{name}.sample.json'
            if src.is_file(): shutil.copy(src, job / f'{name}.json')
        d = json.loads((job / 'direction.json').read_text()); edit(d)
        (job / 'direction.json').write_text(json.dumps(d))
        out = job / 'page.html'
        r = subprocess.run([sys.executable, str(ROOT / 'lib/render/render_bp.py'), str(job), blueprint, str(out)], capture_output=True, text=True, env={**os.environ, 'LIVETEST': '1'})
        return r, (out.read_text() if out.exists() else '')


def nav_of(html):
    start = html.index('<nav'); return html[start:html.index('</nav>', start)]


class NavLinks(unittest.TestCase):
    def test_script_and_data_urls_never_become_links(self):
        def edit(d): d['nav'] = {'cta': 'Go', 'links': [['javascript:alert(1)', 'Bad'], ['data:text/html,<script>1</script>', 'Worse'], ['#feat', 'Features'], ['https://example.com/menu', 'Menu']]}
        r, html = render(edit); self.assertEqual(r.returncode, 0, r.stderr)
        nav = nav_of(html)
        self.assertNotIn('javascript:', nav); self.assertNotIn('data:text', nav)
        self.assertNotIn('>Bad<', nav); self.assertNotIn('>Worse<', nav)
        self.assertIn('<a href="#feat">Features</a>', nav); self.assertIn('<a href="https://example.com/menu">Menu</a>', nav)

    def test_malformed_entries_are_skipped_not_fatal(self):
        def edit(d): d['nav'] = {'cta': 'Go', 'links': ['#feat', ['#how'], ['#q', 'Quote', 'extra'], None, ['#nums', 'Numbers'], ['#x y', 'Spaced']]}
        r, html = render(edit); self.assertEqual(r.returncode, 0, r.stderr)
        nav = nav_of(html)
        self.assertIn('<a href="#nums">Numbers</a>', nav); self.assertNotIn('Spaced', nav); self.assertNotIn('Quote', nav)


class BrandColours(unittest.TestCase):
    def test_a_colour_that_is_not_a_hex_never_reaches_the_stylesheet(self):
        payload = '#F4EFE3;}body{display:none}.x{color:red'
        def edit(d): d['brand'] = {**d.get('brand', {}), 'accent': '#0F2A14', 'ink': '#101010', 'paper': payload}
        r, html = render(edit); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('body{display:none}', html); self.assertNotIn(payload, html)

    def test_a_script_in_the_ink_does_not_break_out_of_the_style_block(self):
        def edit(d): d['brand'] = {**d.get('brand', {}), 'accent': '#0F2A14', 'ink': '#101010</style><script>alert(1)</script>', 'paper': '#F4EFE3'}
        r, html = render(edit); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('<script>alert(1)</script>', html)

    def test_valid_brand_colours_are_still_the_page_colours(self):
        def edit(d): d['brand'] = {**d.get('brand', {}), 'accent': '#0F2A14', 'ink': '#101010', 'paper': '#F4EFE3'}
        r, html = render(edit); self.assertEqual(r.returncode, 0, r.stderr)
        root = html[html.index(':root{'):html.index('}', html.index(':root{'))]
        self.assertIn('--paper:#F4EFE3', root); self.assertIn('--ink:#101010', root)

    def test_short_hex_is_accepted_and_non_colours_fall_back_to_the_blueprint(self):
        def short(d): d['brand'] = {**d.get('brand', {}), 'accent': '#0a3', 'ink': '#111', 'paper': '#fff'}
        r, html = render(short); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('--paper:#FFFFFF', html)
        def words(d): d['brand'] = {**d.get('brand', {}), 'accent': 'forest green', 'ink': 'rgb(0,0,0)', 'paper': 'cream'}
        r, html = render(words); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('forest green', html); self.assertNotIn('--paper:cream', html)


class Bands(unittest.TestCase):
    def test_a_band_cannot_carry_an_attribute(self):
        def edit(d):
            for b in d['beats']: b['band'] = 'dark" onmouseover="alert(1)'
        r, html = render(edit); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('onmouseover', html)

    def test_known_bands_still_apply(self):
        def edit(d):
            for b in d['beats']:
                if b['type'] == 'steps': b['band'] = 'dark'
        r, html = render(edit); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(html, r'<section class="sec [^"]*band-dark[^"]*" id="how"')


class LayoutChoices(unittest.TestCase):
    """Column counts, heading sizes and hero alignment are written into attributes: numbers and known words only."""
    def test_columns_that_are_not_a_number_are_ignored(self):
        def edit(d):
            for b in d['beats']: b.setdefault('ui', {})['cols'] = '3" onclick="alert(1)'
        r, html = render(edit, 'cerebrium'); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('alert(1)', html)  # the page's own scripts use .onclick; the injected handler is what must be absent
        self.assertNotIn('--n:3"', html.replace('style="--n:3"', ''))

    def test_a_chosen_column_count_is_still_honoured(self):
        def edit(d):
            for b in d['beats']:
                if b['type'] == 'steps': b['ui'] = {'move': 'cards', 'cols': 2, 'lead': ''}; b['steps'] = ['First step', 'Second step', 'Third step', 'Fourth step', 'Fifth step', 'Sixth step', 'Seventh step']
        r, html = render(edit, 'cerebrium'); self.assertEqual(r.returncode, 0, r.stderr)
        section = html[html.index('id="how"'):]; section = section[:section.index('</section>')]
        self.assertIn('style="--n:2"', section)

    def test_hero_alignment_is_one_of_two_words(self):
        def edit(d): d['hero'].setdefault('ui', {})['align'] = 'center" data-x="1'; d['hero']['ui'].pop('move', None); d['hero']['media'] = ''
        for blueprint in ('butter', 'tengile'):
            r, html = render(edit, blueprint); self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn('data-x="1"', html)

    def test_a_heading_size_that_is_not_a_number_does_not_stop_the_render(self):
        def edit(d):
            for b in d['beats']: b.setdefault('ui', {})['h2_px'] = 'huge'
        r, html = render(edit); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('id="how"', html)


if __name__ == '__main__':
    unittest.main()
