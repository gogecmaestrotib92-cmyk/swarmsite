"""A photograph as the ground of the whole first screen: the composition says so with bleed "full", the validator holds
it to the picture's pixels and to a scrim, the renderer lays it under the grid and the navigation, and the loop measures
on the render whether the words read against it — deepening the veil by rule when they do not. No network, no model."""
import copy, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'compose'))
import compose as COMPOSE
import content as CONTENT
import render_ir as IR
import validate as V


def production_page():
    with tempfile.TemporaryDirectory() as temp:
        job = Path(temp)
        for name in ('direction', 'images', 'inventory', 'assets'):
            src = ROOT / 'tests' / f'{name}.sample.json'
            if src.is_file(): shutil.copy(src, job / f'{name}.json')
        d = json.loads((job / 'direction.json').read_text()); d['kind'] = 'place'; (job / 'direction.json').write_text(json.dumps(d))
        out = job / 'page.html'
        r = subprocess.run([sys.executable, str(ROOT / 'lib/render/render_bp.py'), str(job), 'tengile', str(out)], capture_output=True, text=True, env={**os.environ, 'LIVETEST': '1'})
        assert r.returncode == 0, r.stderr
        return out.read_text(), json.loads((job / 'images.json').read_text())


PAGE, IMAGES = production_page()
BASE = CONTENT.from_page(PAGE, IMAGES)   # one 1344×896 photograph as hero.picture


def backdrop(content=BASE, **hero):
    """The hero's words on its own photograph: the picture under everything, the words in four rows on it."""
    nodes = [{'id': 'bg', 't': 'media', 'src': 'hero.picture', 'bleed': 'full', 'scrim': True, 'at': {'col': [1, 13], 'row': [1, 5], 'z': 0}}]
    if 'hero.category' in content['text']: nodes.append({'id': 'cat', 't': 'text', 'src': 'hero.category', 'as': 'label', 'at': {'col': [1, 7], 'row': 1}})
    if 'hero.fact' in content['text']: nodes.append({'id': 'fact', 't': 'text', 'src': 'hero.fact', 'as': 'label', 'align': 'end', 'at': {'col': [8, 13], 'row': 1}})
    nodes.append({'id': 'h1', 't': 'text', 'src': 'hero.h1', 'as': 'h1', 'size': 'xxl', 'at': {'col': [1, 10], 'row': 2, 'self': 'end'}})
    if 'hero.lede' in content['text']: nodes.append({'id': 'lede', 't': 'text', 'src': 'hero.lede', 'as': 'lede', 'measure': 40, 'at': {'col': [1, 7], 'row': 3}})
    if content['actions']: nodes.append({'id': 'go', 't': 'actions', 'src': sorted(content['actions']), 'at': {'col': [1, 7], 'row': 4}})
    return {'ir': V.VERSION, 'hero': dict({'height': 'screen', 'rows': ['auto', '1fr', 'auto', 'auto'], 'gap': 'md', 'nodes': nodes}, **hero)}


def codes(ir, content=BASE): return sorted({e['code'] for e in V.validate(ir, content)})
def ground(ir): return ir['hero']['nodes'][0]
def changed(content=BASE, **fields):
    ir = backdrop(content); ground(ir).update(fields); return ir
def sized(w, h, shot=False):
    content = copy.deepcopy(BASE); content['media']['hero.picture'].update(w=w, h=h, shot=shot); return content


class Validation(unittest.TestCase):
    def test_a_photograph_may_be_the_ground_of_the_first_screen(self):
        for height in ('auto', 'screen', 'tall'): self.assertEqual(V.validate(backdrop(height=height), BASE), [], height)
        self.assertEqual(codes(changed(tone='mono', grain=True, focal=[0.3, 0.6], enter='settle', scroll='parallax')), [])

    def test_it_covers_the_whole_screen_or_it_is_not_a_backdrop(self):
        self.assertEqual(codes(changed(at={'col': [1, 12], 'row': [1, 5], 'z': 0})), ['IR030']); self.assertEqual(codes(changed(at={'col': [1, 13], 'row': [2, 5], 'z': 0})), ['IR030'])

    def test_it_carries_the_words_so_it_has_its_scrim(self):
        self.assertEqual(codes(changed(scrim=False)), ['IR032']); ir = backdrop(); ground(ir).pop('scrim'); self.assertEqual(codes(ir), ['IR032'])
        self.assertEqual(codes(changed(scrim='deep')), []); self.assertEqual(codes(changed(scrim='soft')), ['IR001', 'IR032'])

    def test_a_deep_scrim_belongs_to_a_backdrop_only(self):
        ir = backdrop(); ground(ir).update(bleed='none', ratio='4/3', scrim='deep'); self.assertIn('IR001', codes(ir))

    def test_it_has_the_screens_proportion_not_one_of_its_own(self):
        self.assertEqual(codes(changed(ratio='16/9')), ['IR064'])

    def test_it_is_held_to_its_pixels_in_both_directions(self):
        wide = sized(1400, 589); found = V.validate(backdrop(wide), wide)   # wide enough, not tall enough for a whole screen
        self.assertEqual([e['code'] for e in found], ['IR060']); self.assertIn('1440×900', found[0]['message']); self.assertIn('"height": "auto" it can carry it', found[0]['message'])
        self.assertEqual(V.validate(backdrop(wide, height='auto'), wide), [])
        small = sized(900, 700); found = V.validate(backdrop(small, height='auto'), small)
        self.assertEqual([e['code'] for e in found], ['IR060']); self.assertIn('place it in columns instead', found[0]['message'])

    def test_a_screenshot_is_never_a_backdrop(self):
        shot = sized(1600, 1200, shot=True); self.assertIn('IR062', codes(backdrop(shot), shot))

    def test_it_is_a_plain_rectangle(self):
        for change in ({'tilt': 2}, {'shape': 'arch'}, {'shadow': 'soft'}, {'frame': 'paper'}): self.assertEqual(codes(changed(**change)), ['IR067'], change)

    def test_it_is_the_first_screens_picture_and_is_not_too_tall_for_it(self):
        self.assertNotIn('IR066', codes(backdrop())); self.assertNotIn('IR069', codes(backdrop(height='tall')))


class Drawing(unittest.TestCase):
    def test_the_picture_lies_under_the_grid_and_the_words_read_in_the_on_photo_colour(self):
        html = IR.render_hero(backdrop(), BASE)
        self.assertRegex(html, r'^<section class="sec hero ir has-media ir-has-backdrop" id="top"'); self.assertLess(html.index('ir-backdrop'), html.index('ir-grid'))
        self.assertIn('<figure class="ir-media ir-backdrop ir-scrim" data-node="bg" style="--focal:50% 50%">', html); self.assertNotIn('--ratio', html)
        self.assertEqual(html.count('ir-on-scrim'), len(backdrop()['hero']['nodes']) - 1, 'every block of words stands on the picture'); self.assertEqual(html.count('<img '), 1)

    def test_a_deep_veil_and_the_treatments_are_drawn(self):
        html = IR.render_hero(changed(scrim='deep', tone='duotone', focal=[0.2, 0.7], enter='clip', scroll='parallax'), BASE)
        self.assertIn('ir-scrim ir-scrim-deep ir-tone', html); self.assertIn('--focal:20% 70%', html); self.assertIn('data-move="clip-reveal parallax" data-parallax="6"', html); self.assertIn('ir-t-light', html)

    def test_the_page_script_sets_the_navigation_on_the_photograph(self):
        page, report = IR.transplant(PAGE, backdrop(), IMAGES); self.assertTrue(report['drawn'], report['errors'])
        self.assertIn("document.querySelector('.hero.has-media')", page, 'the page\'s own script reads this class and puts the navigation in the on-photo colour')
        self.assertIn('.hero.ir .ir-backdrop{position:absolute;inset:0;width:100%;height:100%', page)

    def test_the_look_at_rest_uses_nothing_the_measuring_tools_switch_off(self):
        for banned in ('transform:', 'filter:', 'clip-path:', 'opacity:'): self.assertNotIn(banned, IR.CSS, banned)


class Measured(unittest.TestCase):
    def setUp(self): self.dir = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.dir, True)

    def test_a_veil_the_words_do_not_read_through_is_deepened_by_rule(self):
        with patch.object(COMPOSE, 'backdrop_findings', lambda path: {'desktop-hero-words-on-picture-contrast': '2.4:1'}) :
            deeper = COMPOSE.veil(PAGE, backdrop(), IMAGES, self.dir)
        self.assertEqual(ground(deeper)['scrim'], 'deep'); self.assertEqual(V.validate(deeper, BASE), []); self.assertEqual(os.listdir(self.dir), [], 'the drawing it measured is removed')

    def test_a_veil_that_reads_is_left_alone_and_other_compositions_are_not_measured(self):
        ir = backdrop()
        with patch.object(COMPOSE, 'backdrop_findings', lambda path: {}): self.assertIs(COMPOSE.veil(PAGE, ir, IMAGES, self.dir), ir)
        plain = backdrop(); ground(plain).update(bleed='none', ratio='4/3', at={'col': [8, 13], 'row': [2, 5], 'z': 0}, scrim=False)
        for n in plain['hero']['nodes'][1:]: n['at'] = dict(n['at'], col=[1, 7])
        with patch.object(COMPOSE, 'backdrop_findings', side_effect=AssertionError('not called')): self.assertIs(COMPOSE.veil(PAGE, plain, IMAGES, self.dir), plain)

    def test_the_render_says_whether_the_words_read_and_the_picture_is_within_its_pixels(self):
        seen = {'desktop': [{'id': 'top', 'form': 'hero-backdrop', 'scale': 1.5, 'limit': 1.35, 'contrast': {'ratio': 2.4, 'need': 4.5, 'text': 'Since 1996'}}, {'id': 'mk', 'form': 'bleed', 'scale': 2, 'limit': 1.35, 'contrast': None}],
                'mobile': [{'id': 'top', 'form': 'hero-backdrop', 'scale': 0.6, 'limit': 1.35, 'contrast': {'ratio': 6.1, 'need': 4.5, 'text': 'Since 1996'}}]}
        with patch.object(COMPOSE.subprocess, 'run', lambda *a, **k: SimpleNamespace(stdout='noise\n' + json.dumps(seen) + '\n', stderr='', returncode=0)):
            found = COMPOSE.backdrop_findings('page.html')
        self.assertEqual(sorted(found), ['desktop-hero-picture-over-pixels', 'desktop-hero-words-on-picture-contrast']); self.assertIn('"Since 1996" reads at 2.4:1', found['desktop-hero-words-on-picture-contrast'])
        self.assertEqual(sorted(COMPOSE._broken(found)), sorted(found), 'both are promises: a composition that breaks them is not shipped')
        with patch.object(COMPOSE.subprocess, 'run', lambda *a, **k: SimpleNamespace(stdout='', stderr='no chrome', returncode=1)):
            with self.assertRaisesRegex(RuntimeError, 'could not be measured'): COMPOSE.backdrop_findings('page.html')

    def test_the_composer_is_told_which_photograph_can_carry_the_screen(self):
        text, _ = COMPOSE.brief(copy.deepcopy(BASE)); self.assertIn('large enough to be the BACKDROP', text); self.assertIn('"bleed": "full"', COMPOSE.SYSTEM)
        small = sized(900, 700); text, _ = COMPOSE.brief(small); self.assertNotIn('BACKDROP of the first screen ("bleed"', text)


if __name__ == '__main__': unittest.main()
