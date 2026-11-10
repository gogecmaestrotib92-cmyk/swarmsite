"""Composition 0.2: the typeface, the headline set by hand, pictures toned, shaped, tilted and layered, and motion by name.
Every rule has one seeded defect and its code; everything drawn is checked in the markup. No network, no model."""
import copy, json, os, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'compose'))
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
BASE = CONTENT.from_page(PAGE, IMAGES)   # headline: "Bašta gde Beograd *slavi*" — four words, the last emphasised; one 1344×896 photograph
WORDS = [''.join(t for t, _ in w) for w in CONTENT.words(BASE['text']['hero.h1'])]


def composition(content=BASE, **hero):
    nodes = []
    if 'hero.category' in content['text']: nodes.append({'id': 'cat', 't': 'text', 'src': 'hero.category', 'as': 'label', 'at': {'col': [1, 7], 'row': 1}})
    if 'hero.fact' in content['text']: nodes.append({'id': 'fact', 't': 'text', 'src': 'hero.fact', 'as': 'label', 'align': 'end', 'at': {'col': [8, 13], 'row': 1}})
    nodes.append({'id': 'h1', 't': 'text', 'src': 'hero.h1', 'as': 'h1', 'size': 'xxl', 'at': {'col': [1, 8], 'row': 2}})
    if 'hero.picture' in content['media']: nodes.append({'id': 'pic', 't': 'media', 'src': 'hero.picture', 'fit': 'cover', 'ratio': '4/3', 'at': {'col': [8, 13], 'row': [2, 5], 'z': 0}})
    if 'hero.lede' in content['text']: nodes.append({'id': 'lede', 't': 'text', 'src': 'hero.lede', 'as': 'lede', 'measure': 40, 'at': {'col': [1, 7], 'row': 3}})
    if content['actions']: nodes.append({'id': 'go', 't': 'actions', 'src': sorted(content['actions']), 'at': {'col': [1, 7], 'row': 4}})
    return {'ir': V.VERSION, 'hero': dict({'height': 'screen', 'rows': ['auto', '1fr', 'auto', 'auto'], 'gap': 'md', 'nodes': nodes}, **hero)}


def codes(ir, content=BASE): return sorted({e['code'] for e in V.validate(ir, content)})
def node(ir, nid): return next(n for n in ir['hero']['nodes'] if n['id'] == nid)
def with_node(nid, content=BASE, **fields):
    ir = composition(content); node(ir, nid).update(fields); return ir
def draw(ir, content=BASE):
    assert V.validate(ir, content) == [], V.validate(ir, content)
    return IR.render_hero(ir, content)
def stacked(content, start=6, **fields):
    """The composition with its words left of column line `start` and the picture node, changed by `fields`, from there to the right edge."""
    ir = composition(content)
    for n in ir['hero']['nodes']:
        if n['t'] != 'media': n['at'] = dict(n['at'], col=[1, start] if n['id'] != 'fact' else [start, 13])
    node(ir, 'pic').update({'at': {'col': [start, 13], 'row': [2, 5], 'z': 0}, **fields}); return ir
STACK = dict(src=['hero.picture', 'img:a'], stack='offset')
def more_pictures(**extra):
    content = copy.deepcopy(BASE)
    for name, (w, h, shot) in {'img:a': (1400, 1050, False), 'img:b': (1400, 1050, False), **extra}.items():
        content['media'][name] = {'src': f'data:image/png;base64,{name[-1] * 8}', 'alt': name, 'w': w, 'h': h, 'shot': shot, 'id': name[4:]}
    return content


class Typeface(unittest.TestCase):
    def test_a_registry_face_may_be_chosen_and_nothing_else(self):
        self.assertEqual(codes(composition(face={'id': 'fraunces', 'weight': 300, 'case': 'none'})), [])
        self.assertEqual(codes(composition(face={'id': 'gt-america'})), ['IR050'], 'a face that is not in the registry cannot be asked for')
        self.assertEqual(codes(composition(face='fraunces')), ['IR050'])
        self.assertEqual(codes(composition(face={'id': 'instrument-serif', 'weight': 700})), ['IR050'], 'one weight means one weight: no faux bold')
        self.assertEqual(codes(composition(face={'id': 'fraunces', 'case': 'small'})), ['IR050'])
        self.assertEqual(codes(composition(face={'id': 'fraunces', 'family': "x';}body{display:none"})), ['IR050'])

    def test_the_brands_own_face_is_kept(self):
        locked = copy.deepcopy(BASE); locked['page']['face_locked'] = True
        self.assertEqual(codes(composition(locked, face={'id': 'fraunces'}), locked), ['IR051'])
        self.assertEqual(codes(composition(locked), locked), [])

    def test_the_face_is_set_for_the_whole_page_and_loaded_once(self):
        page, report = IR.transplant(PAGE, composition(face={'id': 'fraunces', 'weight': 300}), IMAGES)
        self.assertTrue(report['drawn'], report['errors']); face = V.FACES.get('fraunces')
        self.assertEqual(page.count('id="ir-face"'), 1); self.assertIn(IR.e(V.FACES.link(face)), page)
        tokens = re.search(r'<style id="ir-face-css">:root\{([^}]*)\}</style>', page).group(1)
        self.assertIn("--display:'Fraunces',Georgia,serif", tokens); self.assertIn('--h1-w:300', tokens); self.assertIn('--h2-w:300', tokens)
        self.assertLess(page.index('id="ir-face-css"'), page.index('</head>')); self.assertGreater(page.index('id="ir-face-css"'), page.index('--display:'), 'it comes after the page\'s own tokens, so it wins')
        plain, _ = IR.transplant(PAGE, composition(), IMAGES)
        self.assertNotIn('ir-face', plain, 'a composition that names no face leaves the page in its own')

    def test_weights_and_case_follow_the_face(self):
        head = IR.face_head(composition(face={'id': 'instrument-serif'})['hero'], BASE)
        self.assertIn('--h1-w:400', head); self.assertIn('--h3-w:400', head, 'a small heading is never asked for a weight the face does not have')
        self.assertIn('--h1-tt:uppercase', IR.face_head(composition(face={'id': 'anton'})['hero'], BASE), 'a face drawn for capitals is set in capitals')
        self.assertIn('--h1-tt:none', IR.face_head(composition(face={'id': 'anton', 'case': 'none'})['hero'], BASE))
        self.assertIn('--h1-tt:uppercase', IR.face_head(composition(face={'id': 'geist', 'case': 'upper'})['hero'], BASE))

    def test_the_headline_is_sized_from_the_chosen_faces_measured_width(self):
        longest = max(len(w) for w in WORDS)
        narrow = draw(composition(face={'id': 'big-shoulders'})); wide = draw(composition(face={'id': 'unbounded'}))
        self.assertIn(f'--fit:{longest * V.FACES.get("big-shoulders")["avg_upper"] * IR.ESTIMATE_SLACK:.3f}', narrow)
        self.assertIn(f'--fit:{longest * V.FACES.get("unbounded")["avg"] * IR.ESTIMATE_SLACK:.3f}', wide)

    def test_a_measured_headline_is_sized_from_the_measurement(self):
        estimate = V.headline_em(node(composition(), 'h1'), BASE, *V.face_of({}, BASE))
        ir = with_node('h1', fit={'line': round(estimate * 0.9, 3), 'word': round(estimate * 0.8, 3)})
        html = draw(ir)
        self.assertIn(f'--fit:{round(estimate * 0.9, 3) * IR.MEASURED_SLACK:.3f};--fit-sm:{round(estimate * 0.8, 3) * IR.MEASURED_SLACK:.3f}', html)
        self.assertLess(IR.MEASURED_SLACK, IR.ESTIMATE_SLACK, 'a measurement needs less room than an average')
        self.assertEqual(codes(with_node('h1', fit={'line': estimate * 3, 'word': 1})), ['IR045'], 'a measurement three times the estimate belongs to another headline')
        self.assertEqual(codes(with_node('h1', fit=6.2)), ['IR045']); self.assertEqual(codes(with_node('h1', fit={'line': 5})), ['IR045'])
        self.assertEqual(codes(with_node('lede', fit={'line': 5, 'word': 2})), ['IR042'], 'only a headline is measured')

    def test_a_line_that_does_not_fit_wraps_and_is_never_cut(self):
        self.assertNotIn('nowrap', IR.CSS, 'a hand-broken line that turns out too wide takes a second line, which the loop measures; clipped letters are never the fallback')


class Headline(unittest.TestCase):
    def test_lines_are_word_counts_that_add_up(self):
        self.assertEqual(codes(with_node('h1', lines=[2, 2])), [])
        self.assertEqual(codes(with_node('h1', lines=[2, 3])), ['IR042'])
        self.assertEqual(codes(with_node('h1', lines=[1, 1, 1, 1])), ['IR042'], 'the page promises a headline of at most three lines')
        self.assertEqual(codes(with_node('h1', lines=[4, 0])), ['IR042'])
        self.assertEqual(codes(with_node('h1', lines=[2, 2], measure=12)), ['IR042'], 'lines are the measure')
        self.assertEqual(codes(with_node('lede', lines=[3])), ['IR042'], 'only the headline is set by hand')

    def test_indent_and_scale_are_given_per_line(self):
        self.assertEqual(codes(with_node('h1', lines=[2, 2], indent=[0, 3], scale=[1, 1.3])), [])
        self.assertEqual(codes(with_node('h1', indent=[0, 2])), ['IR042'])
        self.assertEqual(codes(with_node('h1', lines=[2, 2], indent=[1])), ['IR042'])
        self.assertEqual(codes(with_node('h1', lines=[2, 2], indent=[0, 7])), ['IR042'])
        self.assertEqual(codes(with_node('h1', lines=[2, 2], scale=[1, 1.5])), ['IR042'])
        self.assertEqual(codes(with_node('h1', lines=[1, 2, 1], scale=[1.6, 1.3, 1])), ['IR042'], 'three lines scaled up stand taller than three lines')

    def test_a_mark_is_one_style_on_few_words(self):
        self.assertEqual(codes(with_node('h1', mark='outline')), [], 'the headline\'s own emphasised word is the one marked')
        self.assertEqual(codes(with_node('h1', mark='outline', mark_words=[0])), [])
        self.assertEqual(codes(with_node('h1', mark='neon')), ['IR043'])
        self.assertEqual(codes(with_node('h1', mark_words=[0])), ['IR043'])
        self.assertEqual(codes(with_node('h1', mark='box', mark_words=[4])), ['IR043'])
        self.assertEqual(codes(with_node('h1', mark='box', mark_words=[0, 0])), ['IR043'])
        self.assertEqual(codes(with_node('h1', mark='box', mark_words=[0, 1, 2])), ['IR043'], 'a mark is the exception')
        plain = copy.deepcopy(BASE); plain['text']['hero.h1'] = [('Bašta gde Beograd slavi', False)]
        self.assertEqual(codes(with_node('h1', plain, mark='accent'), plain), ['IR043'], 'nothing is emphasised: the composition has to say which word')
        ir = with_node('h1', mark='italic'); ir['hero']['face'] = {'id': 'gloock'}
        self.assertEqual(codes(ir), ['IR043'], 'a face without an italic is never slanted by the browser')

    def test_a_headline_that_cannot_be_set_at_a_headlines_size_is_refused(self):
        ir = with_node('h1', lines=[4]); node(ir, 'h1')['at'] = {'col': [1, 4], 'row': 2}
        self.assertEqual(codes(ir), ['IR044'], 'one line of 23 characters does not fit three columns at 48 px')
        long_word = copy.deepcopy(BASE); long_word['text']['hero.h1'] = [('Donaudampfschifffahrtsgesellschaft', False)]
        ir = composition(long_word); node(ir, 'h1')['at'] = {'col': [1, 5], 'row': 2}
        self.assertEqual(codes(ir, long_word), ['IR044'])
        self.assertEqual(codes(with_node('h1', lines=[2, 2])), [], 'the same words in two lines over seven columns fit')

    def test_lines_indent_scale_and_marks_are_drawn_and_the_words_stay_the_words(self):
        html = draw(with_node('h1', lines=[2, 2], indent=[0, 2], scale=[1, 1.3], mark='outline'))
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S).group(0)
        self.assertEqual(h1.count('class="ir-l mv-line"'), 2); self.assertEqual(h1.count('class="mv-line-in"'), 2)
        self.assertIn('data-split="l"', h1, 'the page\'s motion library animates these lines as they are and does not split them again')
        self.assertIn('--ls:1.3;--ind:0.769em', h1, 'an indent is in ems of the headline, whatever the line\'s own scale')
        self.assertIn('<em class="ir-mk ir-mk-outline">slavi</em>', h1)
        self.assertEqual(re.sub(r'<[^>]+>', '', h1).split(), WORDS)
        self.assertEqual(CONTENT.from_page(PAGE[:BASE['span'][0]] + html + PAGE[BASE['span'][1]:], IMAGES)['text']['hero.h1'], [('Bašta gde Beograd ', False), ('slavi', True)], 'read back, it is the same headline with the same emphasis')

    def test_marked_words_replace_the_headlines_own_emphasis(self):
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', draw(with_node('h1', mark='box', mark_words=[0])), re.S).group(1)
        self.assertEqual(h1, '<em class="ir-mk ir-mk-box">Bašta</em> gde Beograd slavi')
        own = re.search(r'<h1[^>]*>(.*?)</h1>', draw(composition()), re.S).group(1)
        self.assertEqual(own, 'Bašta gde Beograd <em>slavi</em>', 'with no mark the page draws its emphasis its own way')

    def test_short_lines_are_kept_on_a_phone_and_long_ones_are_let_go(self):
        short = copy.deepcopy(BASE); short['text']['hero.h1'] = [('Stop betting on a ', False), ('hunch', True)]
        self.assertIn('ir-keep-sm', draw(with_node('h1', short, lines=[2, 3]), short))
        self.assertNotIn('ir-keep-sm"', draw(with_node('h1', lines=[2, 2])), '"Beograd slavi" is 13 characters: on a phone the headline wraps by itself')
        self.assertNotIn('ir-keep-sm"', draw(with_node('h1', short, lines=[2, 3], indent=[0, 2]), short))

    def test_a_marked_or_broken_headline_is_still_escaped(self):
        hostile = copy.deepcopy(BASE); hostile['text']['hero.h1'] = [('<img src=x onerror=1> two ', False), ('<b>three</b>', True)]
        ir = composition(hostile); node(ir, 'h1').update(lines=[4, 1], mark='underline', size='xl')   # five "words": <img / src=x / onerror=1> / two / <b>three</b>
        html = draw(ir, hostile)
        self.assertNotIn('<img src=x', html); self.assertNotIn('<b>', html); self.assertIn('<em class="ir-mk ir-mk-underline">&lt;b&gt;three&lt;/b&gt;</em>', html)


class Pictures(unittest.TestCase):
    def test_treatments_come_from_the_vocabulary(self):
        self.assertEqual(codes(with_node('pic', tone='duotone', grain=True, shape='soft', tilt=-3, shadow='hard', enter='clip')), [])
        for field, value in (('tone', 'sepia'), ('shape', 'star'), ('shadow', 'neon'), ('tilt', 9), ('tilt', 1.5), ('grain', 'yes')):
            self.assertEqual(codes(with_node('pic', **{field: value})), ['IR001'], f'{field}={value}')
        self.assertEqual(codes(with_node('pic', enter='spin')), ['IR070']); self.assertEqual(codes(with_node('pic', scroll='zoom')), ['IR070'])

    def test_treatments_that_do_not_go_together(self):
        self.assertEqual(codes(with_node('pic', shape='circle')), ['IR067']); self.assertEqual(codes(with_node('pic', shape='circle', ratio='1/1')), [])
        self.assertEqual(codes(with_node('pic', bleed='right', tilt=2)), ['IR067']); self.assertEqual(codes(with_node('pic', bleed='right', tone='mono', scroll='parallax')), [])
        self.assertEqual(codes(with_node('pic', frame='paper', shape='arch')), ['IR067'])
        self.assertEqual(codes(with_node('pic', scroll='parallax', tilt=2)), ['IR067']); self.assertEqual(codes(with_node('pic', scroll='parallax', fit='contain')), ['IR067'])

    def test_a_screenshot_keeps_its_colours_and_its_rectangle(self):
        shot = copy.deepcopy(BASE); shot['media']['hero.picture']['shot'] = True
        framed = dict(fit='contain', frame='browser', ratio='3/2')
        self.assertEqual(codes(with_node('pic', shot, **framed, tilt=2, shadow='soft', enter='settle'), shot), [])
        for field, value in (('tone', 'mono'), ('shape', 'arch'), ('scroll', 'parallax')):
            self.assertIn('IR062', codes(with_node('pic', shot, **framed, **{field: value}), shot), field)

    def test_a_stack_is_two_or_three_different_pictures_in_one_box(self):
        content = more_pictures()
        self.assertEqual(codes(stacked(content, **STACK), content), [])
        self.assertEqual(codes(stacked(content, start=5, src=['hero.picture', 'img:a', 'img:b'], stack='fan'), content), [])
        self.assertEqual(codes(stacked(content, start=10, src=['hero.picture', 'img:a', 'img:b'], stack='fan'), content), ['IR066'], 'three fanned pictures in three columns are each under 15% of the screen: icons, not pictures')
        self.assertEqual(codes(stacked(content, src=['hero.picture', 'img:a']), content), ['IR001'], 'pictures named together say how they are laid')
        self.assertEqual(codes(stacked(content, stack='fan'), content), ['IR001'], 'one picture is not a stack')
        self.assertEqual(codes(stacked(content, src=['hero.picture', 'hero.picture'], stack='offset'), content), ['IR001'])
        self.assertEqual(codes(stacked(content, src=['hero.picture', 'img:nowhere'], stack='offset'), content), ['IR010'])
        self.assertEqual(codes(stacked(content, **STACK, scrim=True), content), ['IR067'])
        self.assertEqual(codes(stacked(content, start=8, **STACK), content), [], 'a stack registers by the room its pictures take together')
        narrow = stacked(content, **STACK); node(narrow, 'pic')['at'] = {'col': [11, 13], 'row': [2, 5], 'z': 0}
        self.assertEqual(codes(narrow, content), ['IR066'], 'two columns hold thumbnails, not pictures')

    def test_every_picture_of_a_stack_is_checked_like_a_picture(self):
        small = more_pictures(**{'img:a': (300, 225, False)})
        self.assertEqual(codes(stacked(small, **STACK), small), ['IR060'])
        elsewhere = more_pictures(); elsewhere['used_elsewhere'] = ['img:a']
        self.assertEqual(codes(stacked(elsewhere, **STACK), elsewhere), ['IR061'])
        shots = more_pictures(**{'img:a': (1400, 700, True)})
        self.assertEqual(codes(stacked(shots, **STACK, fit='contain', frame='browser'), shots), ['IR068'], 'a 2:1 screenshot in a 4/3 stack would be letterboxed')
        self.assertEqual(codes(stacked(shots, **STACK), shots), ['IR062', 'IR068'])

    def test_a_picture_is_placed_once_in_the_first_screen(self):
        ir = composition(); twin = dict(node(ir, 'pic'), id='pic2', at={'col': [8, 13], 'row': 1, 'z': 0}); ir['hero']['nodes'].append(twin)
        ir['hero']['nodes'] = [n for n in ir['hero']['nodes'] if n['id'] != 'fact'] + [dict(n, at={'col': [1, 7], 'row': 4}, id='fact') for n in ir['hero']['nodes'] if n['id'] == 'fact']
        ir['hero']['nodes'] = [n for n in ir['hero']['nodes'] if n['id'] != 'go'] + [dict(n, at={'col': [1, 7], 'row': 3, 'self': 'end'}) for n in ir['hero']['nodes'] if n['id'] == 'go']
        self.assertIn('IR061', codes(ir))

    def test_a_picture_stands_inside_the_first_screen(self):
        tall = with_node('pic', ratio='2/3', at={'col': [8, 13], 'row': [2, 5], 'z': 0})
        width = V.span_px(V.area(node(tall, 'pic'), 4), BASE['page']); self.assertGreater(width * 3 / 2, 720)
        self.assertEqual(codes(tall), ['IR069'])
        self.assertEqual(codes(with_node('pic', ratio='4/5', at={'col': [9, 13], 'row': [2, 5], 'z': 0})), [])
        if width * 3 / 2 <= 900:
            roomy = with_node('pic', ratio='2/3', at={'col': [8, 13], 'row': [2, 5], 'z': 0}); roomy['hero']['height'] = 'tall'
            self.assertEqual(codes(roomy), [], 'a hero declared taller than the screen has the room')

    def test_every_layer_of_a_stack_stays_inside_its_box(self):
        import math
        for kind in V.STACKS:
            for n in (2, 3):
                for ratio in V.RATIOS:
                    box, layers, share = V.stack_layout(kind, n, ratio); self.assertEqual(len(layers), n); self.assertEqual(max(l['z'] for l in layers), layers[0]['z'], 'the first picture named is in front')
                    for l in layers:
                        w, h = l['width'], l['height'] / box; t = math.radians(abs(l['rotate']))   # in units of the box's width
                        bw, bh = w * math.cos(t) + h * math.sin(t), h * math.cos(t) + w * math.sin(t)
                        cx, cy = l['left'] + w / 2, (l['top'] / box) + h / 2
                        self.assertGreaterEqual(cx - bw / 2, -1e-9, (kind, n, ratio)); self.assertLessEqual(cx + bw / 2, 1 + 1e-9, (kind, n, ratio))
                        self.assertGreaterEqual(cy - bh / 2, -1e-9, (kind, n, ratio)); self.assertLessEqual(cy + bh / 2, 1 / box + 1e-9, (kind, n, ratio))

    def test_treatments_are_drawn(self):
        html = draw(with_node('pic', tone='duotone', grain=True, shape='soft', tilt=-3, shadow='hard', enter='clip'))
        figure = re.search(r'<figure[^>]*data-node="pic"[^>]*>.*?</figure>', html, re.S).group(0)
        for token in ('ir-tone', 'ir-shape-soft', 'ir-shadow-hard', 'rotate:-3deg', 'data-move="clip-reveal"', '<i class="ir-t-light"></i><i class="ir-t-dark"></i>', '<i class="ir-grain"></i>'): self.assertIn(token, figure)
        self.assertIn('--ir-dark:var(--ink);--ir-light:var(--paper)', html, 'on a light page the photograph\'s darks take the ink and its lights the paper')
        dark = copy.deepcopy(BASE); dark['page']['dark'] = True
        self.assertIn('--ir-dark:var(--paper);--ir-light:var(--ink)', draw(with_node('pic', dark, tone='duotone'), dark))
        moving = draw(with_node('pic', enter='settle', scroll='parallax'))
        self.assertIn('data-move="scale-settle parallax" data-parallax="7"', moving)
        self.assertNotIn('data-move', draw(composition()), 'a composition that asks for no motion draws none of its own')

    def test_a_stack_is_drawn_as_layers_in_the_order_named(self):
        content = more_pictures()
        html = draw(stacked(content, start=5, src=['hero.picture', 'img:a', 'img:b'], stack='fan', tone='mono', enter='rise'), content)
        figure = re.search(r'<figure[^>]*data-node="pic"[^>]*>.*?</figure>', html, re.S).group(0)
        self.assertIn('class="ir-n ir-stack ir-stack-fan"', figure); self.assertEqual(figure.count('class="ir-layer ir-tone"'), 3); self.assertIn('data-move="stagger-in"', figure); self.assertRegex(figure, r'--box:\d\.\d+')
        sources = re.findall(r'<img src="([^"]+)"', figure)
        self.assertEqual(sources, [content['media'][a]['src'] for a in ('hero.picture', 'img:a', 'img:b')])
        self.assertRegex(figure, r'rotate:-7deg'); self.assertRegex(figure, r'rotate:7deg')

    def test_names_of_moves_exist_in_the_pages_motion_library(self):
        library = (ROOT / 'lib' / 'motion' / 'moves.js').read_text()
        for name in list(IR.MOVES.values()) + ['parallax', 'stagger-in']: self.assertIn(f"'{name}'(el)", library, name)

    def test_nothing_is_drawn_with_a_property_the_measuring_tools_switch_off(self):
        """lib/qa/contract.mjs and the screenshot tools force transform, filter, clip-path and opacity off inside .sec:
        a treatment drawn with one of them would be measured and pictured without it."""
        declarations = re.sub(r'url\("[^"]*"\)', '', IR.CSS)
        self.assertEqual(re.findall(r'(?<![\w-])(transform|filter|clip-path|opacity)\s*:', declarations), [])
        html = draw(with_node('pic', tone='duotone', grain=True, tilt=3, shadow='soft'))
        self.assertEqual(re.findall(r'(?<![\w-])(transform|filter|clip-path|opacity)\s*:', html), [])


if __name__ == '__main__':
    unittest.main()
