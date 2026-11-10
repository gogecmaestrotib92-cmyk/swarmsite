"""Sections that show a picture, as compositions: read off the page whole, validated against the picture's own pixels and
kind, drawn in another form with the same words, picture and tail, and chosen by a model that is held to what the
render measures. No network, no model: the model is a stand-in function and the browser tools are patched."""
import base64, copy, io, json, os, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'compose'))
import compose_pictures as COMPOSE
import content as CONTENT
import pictures as PICTURES
import sections as SECTIONS


def production_page():
    """A real page from the production renderer: "mk" is a story section — its words and one 1344×896 photograph."""
    with tempfile.TemporaryDirectory() as temp:
        job = Path(temp)
        for name in ('direction', 'images', 'inventory', 'assets'):
            src = ROOT / 'tests' / f'{name}.sample.json'
            if src.is_file(): shutil.copy(src, job / f'{name}.json')
        d = json.loads((job / 'direction.json').read_text()); d['kind'] = 'software'; d.pop('house', None); (job / 'direction.json').write_text(json.dumps(d))
        out = job / 'page.html'
        r = subprocess.run([sys.executable, str(ROOT / 'lib/render/render_bp.py'), str(job), 'butter', str(out)], capture_output=True, text=True, env={**os.environ, 'LIVETEST': '1'})
        assert r.returncode == 0, r.stderr
        return out.read_text(), json.loads((job / 'images.json').read_text())


def picture(width, height, colour=(120, 110, 100)):
    """A data-URI JPEG of this size: the reader measures the file itself."""
    from PIL import Image
    buf = io.BytesIO(); Image.new('RGB', (width, height), colour).save(buf, 'JPEG', quality=40)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


PAGE, IMAGES = production_page()
span = lambda sid, page=PAGE: {s['id']: s for s in SECTIONS.sections(page)}[sid]['span']
section = lambda sid, page=PAGE: page[span(sid, page)[0]:span(sid, page)[1]]
MK = SECTIONS.from_picture(section('mk'))
SRC = MK['picture']['src']
SMALL = PAGE.replace(SRC, picture(418, 315))           # the same page with a small photograph in that section
SHOT = [dict(i, shot=True) if i.get('data') == SRC else i for i in IMAGES]   # … and with that picture marked as a screenshot
def doc(*entries): return {'ir': '0.2', 'pictures': [dict(e) for e in entries]}
def codes(document, page=PAGE, images=IMAGES): return sorted({e['code'] for e in PICTURES.validate(document, page, images)})
FORMS = {
    'backdrop': {'section': 'mk', 'form': 'backdrop', 'place': 'bottom-left', 'height': 'lg', 'scrim': 'mid', 'title': 'xl'},
    'bleed': {'section': 'mk', 'form': 'bleed', 'side': 'right', 'cols': 6, 'align': 'center'},
    'panorama': {'section': 'mk', 'form': 'panorama', 'ratio': '21/9', 'words': 'above'},
    'card': {'section': 'mk', 'form': 'card', 'side': 'right', 'cols': 8, 'ratio': '3/2', 'anchor': 'bottom', 'bleed': True},
    'offset': {'section': 'mk', 'form': 'offset', 'side': 'left', 'cols': 5, 'ratio': '3/4', 'shape': 'arch', 'tone': 'duotone'},
    'stage': {'section': 'mk', 'form': 'stage', 'side': 'left', 'cols': 6, 'ground': 'accent', 'tilt': -2},
}


class Reading(unittest.TestCase):
    def test_a_picture_section_is_its_words_its_picture_and_what_follows(self):
        self.assertEqual(MK['kind'], 'picture'); self.assertIn('story', MK['classes']); self.assertEqual(MK['band'], 'paper')
        self.assertTrue(MK['picture']['src'].startswith('data:image/')); self.assertIn(MK['words']['html'], section('mk'))
        self.assertTrue(MK['words']['heading']); self.assertIn(MK['words']['heading'].split()[0], MK['words']['html'])
        self.assertGreater(MK['words']['chars'], 20); self.assertIn(MK['first'], ('words', 'picture'))
        whole = section('mk'); self.assertTrue(whole.endswith(MK['tail'] + '</section>'), 'what follows the picture is kept to the byte')

    def test_the_hero_a_list_the_closing_call_and_a_composed_section_are_not_picture_sections(self):
        with self.assertRaises(ValueError): SECTIONS.from_picture(section('top'))
        with self.assertRaises(ValueError): SECTIONS.from_picture(section('rezervacija'))   # a call to action with a picture: its own job
        with self.assertRaises(ValueError): SECTIONS.from_picture('<section class="sec indexlist" id="x"><div class="wrap"><div class="a">w</div><figure><img src="data:image/png;base64,AA"></figure></div></section>')
        drawn, report = PICTURES.transplant(PAGE, doc(FORMS['offset']), IMAGES); self.assertTrue(report['drawn'])
        with self.assertRaisesRegex(ValueError, 'already composed'): SECTIONS.from_picture(section('mk', drawn))
        self.assertNotIn('mk', {k for k, v in PICTURES.readable(drawn, IMAGES).items() if not isinstance(v[1], str)})

    def test_a_section_that_is_not_read_whole_is_refused(self):
        whole = section('mk'); words = MK['words']['html']
        for broken, why in ((whole.replace(words, words, 1).replace('<figure', '<div class="extra">more</div><figure', 1), 'blocks'),
                            (whole.replace('<figure', 'loose words<figure', 1), 'outside its blocks'),
                            (re.sub(r'<img [^>]*>', lambda m: m.group(0) + m.group(0), whole, 1), 'one picture')):
            with self.assertRaisesRegex(ValueError, why): SECTIONS.from_picture(broken)

    def test_the_picture_is_measured_and_its_kind_known(self):
        _, content = PICTURES.readable(PAGE, IMAGES)['mk']; self.assertEqual((content['picture']['w'], content['picture']['h'], content['picture']['shot']), (1344, 896, False))
        _, content = PICTURES.readable(SMALL, [])['mk']; self.assertEqual((content['picture']['w'], content['picture']['h']), (418, 315), 'without images.json the file itself is measured')
        _, content = PICTURES.readable(PAGE, SHOT)['mk']; self.assertTrue(content['picture']['shot'])
        self.assertIn('rezervacija', PICTURES.readable(PAGE, IMAGES)); self.assertIsInstance(PICTURES.readable(PAGE, IMAGES)['rezervacija'][1], str)


class OpenForms(unittest.TestCase):
    def forms(self, page, images): return [f['form'] for f in PICTURES.open_forms(PICTURES.readable(page, images)['mk'][1], CONTENT.page_of(page))]
    def test_the_picture_decides_which_forms_are_open(self):
        self.assertEqual(self.forms(PAGE, IMAGES), list(PICTURES.FORMS), 'a large photograph can do anything')
        self.assertEqual(self.forms(SMALL, []), ['offset', 'stage'], 'a small photograph cannot be made large: a print or an object')
        self.assertEqual(self.forms(PAGE, SHOT), ['offset', 'stage'], 'a screenshot is shown whole')

    def test_each_open_form_says_what_it_would_draw(self):
        opened = {f['form']: f for f in PICTURES.open_forms(PICTURES.readable(PAGE, IMAGES)['mk'][1], CONTENT.page_of(PAGE))}
        self.assertEqual(opened['backdrop']['box'], (1440, 702)); self.assertAlmostEqual(opened['backdrop']['scale'], 1440 / 1344, places=2)
        self.assertEqual(opened['panorama']['box'][0], 1440); self.assertLessEqual(max(f['scale'] for f in opened.values()), 1.35)


class Validation(unittest.TestCase):
    def test_every_form_validates_on_a_photograph_that_can_carry_it(self):
        for name, entry in FORMS.items(): self.assertEqual(PICTURES.validate(doc(entry), PAGE, IMAGES), [], name)

    def test_IP001_the_document_and_its_fields(self):
        for bad in ({}, {'ir': '9', 'pictures': [FORMS['bleed']]}, {'ir': '0.2', 'pictures': []}, {'ir': '0.2', 'pictures': [FORMS['bleed']], 'extra': 1}, {'ir': '0.2', 'pictures': ['x']}, doc({**FORMS['bleed'], 'place': 'center'}), doc({**FORMS['stage'], 'tone': 'mono'})):
            self.assertEqual(codes(bad), ['IP001'], bad)

    def test_IP011_a_composition_carries_no_words_and_no_picture(self):
        for field in ('heading', 'caption', 'text', 'html', 'alt', 'src', 'href'): self.assertEqual(codes(doc({**FORMS['bleed'], field: 'New words'})), ['IP011'], field)

    def test_IP010_a_section_that_is_not_there_twice_or_unreadable(self):
        self.assertEqual(codes(doc({**FORMS['bleed'], 'section': 'nope'})), ['IP010']); self.assertEqual(codes(doc(FORMS['bleed'], FORMS['card'])), ['IP010'])
        self.assertEqual(codes(doc({**FORMS['bleed'], 'section': 'rezervacija'})), ['IP010']); self.assertEqual(codes(doc({**FORMS['bleed'], 'section': 'feat'})), ['IP010'])

    def test_IP020_every_field_has_its_values(self):
        wrong = [('bleed', {'side': 'top'}), ('bleed', {'cols': 4}), ('bleed', {'cols': 8}), ('bleed', {'height': 'screen'}), ('bleed', {'align': 'middle'}), ('bleed', {'tone': 'sepia'}), ('bleed', {'grain': 'yes'}),
                 ('bleed', {'focal': [0.5]}), ('bleed', {'focal': [2, 0]}), ('bleed', {'title': 'huge'}), ('bleed', {'enter': 'spin'}), ('bleed', {'scroll': 'zoom'}),
                 ('backdrop', {'place': 'middle'}), ('backdrop', {'scrim': 'none'}), ('backdrop', {'height': 'auto'}), ('panorama', {'ratio': '16/9'}), ('panorama', {'words': 'beside'}),
                 ('card', {'ratio': '21/9'}), ('card', {'anchor': 'left'}), ('card', {'bleed': 'yes'}), ('card', {'cols': 6}), ('offset', {'ratio': '5/7'}), ('offset', {'shape': 'star'}), ('offset', {'tilt': 9}),
                 ('offset', {'tilt': 1.5}), ('offset', {'shadow': 'glow'}), ('offset', {'frame': 'gold'}), ('offset', {'drop': 'left'}), ('offset', {'cols': 2}), ('stage', {'ground': 'pink'}), ('stage', {'tilt': 4}), ('stage', {'height': 'screen'}), ('stage', {'cols': 9})]
        for form, change in wrong: self.assertEqual(codes(doc({**FORMS[form], **change})), ['IP020'], (form, change))
        self.assertEqual(codes(doc({'section': 'mk', 'form': 'mosaic'})), ['IP020'])

    def test_IP021_many_words_do_not_stand_on_a_photograph(self):
        words = MK['words']['html']; long = PAGE.replace(words, words + '<p class="cap">' + 'More to read here. ' * 30 + '</p>', 1)
        self.assertEqual(codes(doc(FORMS['backdrop']), long), ['IP021']); self.assertEqual(codes(doc(FORMS['bleed']), long), [], 'beside the picture they are fine')
        rows = PAGE.replace(words, words + '<ul>' + '<li>row</li>' * 5 + '</ul>', 1); self.assertEqual(codes(doc(FORMS['backdrop']), rows), ['IP021'])

    def test_IP060_a_picture_is_never_shown_past_its_pixels(self):
        for name in ('backdrop', 'bleed', 'panorama', 'card'):
            found = PICTURES.validate(doc(FORMS[name]), SMALL, []); self.assertEqual([e['code'] for e in found], ['IP060'], name); self.assertIn('418×315', found[0]['message'])
        self.assertEqual(codes(doc({**FORMS['offset'], 'ratio': '3/4', 'shape': 'rect', 'cols': 4}), SMALL, []), [], 'cut upright it is drawn narrower, never larger')
        tall = PAGE.replace(SRC, picture(1100, 500)); self.assertEqual(codes(doc({**FORMS['backdrop'], 'height': 'screen'}), tall, []), ['IP060'], 'the height counts, not only the width')
        self.assertEqual(codes(doc({**FORMS['backdrop'], 'height': 'md'}), tall, []), [])

    def test_IP062_a_screenshot_is_shown_whole_in_its_own_colours(self):
        for name in ('backdrop', 'bleed', 'panorama', 'card'): self.assertEqual(codes(doc(FORMS[name]), PAGE, SHOT), ['IP062'], name)
        self.assertEqual(codes(doc(FORMS['offset']), PAGE, SHOT), ['IP062'], 'no crop, no tone, no arch')
        self.assertEqual(codes(doc({'section': 'mk', 'form': 'offset', 'cols': 6, 'frame': 'browser', 'shape': 'soft', 'tilt': 2}), PAGE, SHOT), [])
        self.assertEqual(codes(doc(FORMS['stage']), PAGE, SHOT), [])

    def test_IP063_a_picture_of_unknown_size_is_not_placed(self):
        blind = PAGE.replace(SRC, 'data:image/jpeg;base64,AAAA'); self.assertEqual(codes(doc(FORMS['stage']), blind, []), ['IP063'])

    def test_IP066_a_picture_drawn_too_small_is_no_picture(self):
        tiny = PAGE.replace(SRC, picture(150, 110)); self.assertEqual(codes(doc({'section': 'mk', 'form': 'offset', 'cols': 5}), tiny, []), ['IP066'])

    def test_IP067_treatments_that_do_not_go_together(self):
        for change in ({'shape': 'circle', 'ratio': '4/5'}, {'frame': 'paper', 'shape': 'arch'}, {'frame': 'browser', 'shape': 'rect', 'tone': 'none'}, {'ratio': 'own', 'shape': 'arch'}):
            self.assertEqual(codes(doc({**FORMS['offset'], **change})), ['IP067'], change)
        self.assertEqual(codes(doc({**FORMS['offset'], 'shape': 'circle', 'ratio': '1/1'})), [])

    def test_IP044_a_heading_too_large_for_the_room_its_form_leaves(self):
        heading = MK['words']['heading']; long = PAGE.replace('>' + heading + '<', '>Internationalisation Unprecedented<', 1)
        self.assertIn('Internationalisation', SECTIONS.from_picture(section('mk', long))['words']['heading'])
        found = PICTURES.validate(doc({**FORMS['stage'], 'cols': 8, 'title': 'xl'}), long, IMAGES); self.assertEqual([e['code'] for e in found], ['IP044']); self.assertIn('Internationalisation', found[0]['message'])
        self.assertEqual(codes(doc({**FORMS['panorama'], 'title': 'md'}), long), [])


class Drawing(unittest.TestCase):
    def draw(self, entry, page=PAGE, images=IMAGES):
        out, report = PICTURES.transplant(page, doc(entry), images); self.assertTrue(report['drawn'], report['errors']); return out

    def test_every_form_keeps_the_words_the_picture_the_tail_the_id_and_the_band(self):
        text = lambda html: ' '.join(re.sub(r'<[^>]+>', ' ', re.sub(r'<style.*?</style>', '', html, flags=re.S)).split())
        for name, entry in FORMS.items():
            out = self.draw(entry); drawn = section('mk', out)
            self.assertIn(MK['words']['html'] if name != 'panorama' else MK['words']['html'][:MK['words']['html'].find('</h2>') + 5], drawn, name)
            self.assertEqual(drawn.count(SRC), 1, name); self.assertTrue(drawn.endswith(MK['tail'] + '</section>') or MK['tail'] in drawn, name)
            self.assertRegex(drawn, r'^<section class="sec story band-paper pc pc-f-%s [^"]*" id="mk" data-pc="0.2" data-form="%s"' % (name, name))
            self.assertEqual(text(out), text(PAGE), f'{name}: the page says exactly what it said')
            self.assertEqual(sorted(re.findall(r'href="([^"]+)"', out)), sorted(re.findall(r'href="([^"]+)"', PAGE)), name)
            self.assertEqual(out[:span('mk', out)[0]].replace(f'<style id="pc-css">{PICTURES.CSS}</style>', ''), PAGE[:span('mk')[0]], f'{name}: nothing above the section changes but the stylesheet')

    def test_a_refused_document_leaves_the_page_untouched(self):
        out, report = PICTURES.transplant(PAGE, doc({**FORMS['bleed'], 'cols': 11}), IMAGES)
        self.assertIs(out, PAGE); self.assertFalse(report['drawn']); self.assertEqual(report['sections'], [])

    def test_the_same_document_gives_the_same_bytes_and_one_stylesheet(self):
        once = self.draw(FORMS['card']); self.assertEqual(once, self.draw(FORMS['card'])); self.assertEqual(once.count('id="pc-css"'), 1)
        again, report = PICTURES.transplant(once, doc(FORMS['card']), IMAGES)
        self.assertFalse(report['drawn'], 'a composed section is not composed again')

    def test_the_look_at_rest_uses_nothing_the_measuring_tools_switch_off(self):
        for banned in ('transform:', 'filter:', 'clip-path:', 'opacity:'): self.assertNotIn(banned, PICTURES.CSS.replace('backdrop-filter:', ''), banned)
        out = self.draw({**FORMS['offset'], 'tilt': 3, 'shape': 'rect', 'ratio': 'own', 'tone': 'none'}); self.assertIn('rotate:3deg', section('mk', out)); self.assertNotIn('transform', section('mk', out))

    def test_a_backdrop_stands_the_words_on_the_picture_under_a_veil(self):
        drawn = section('mk', self.draw({**FORMS['backdrop'], 'place': 'right', 'scrim': 'deep', 'focal': [0.2, 0.8], 'scroll': 'parallax', 'enter': 'settle'}))
        self.assertLess(drawn.index('class="pc-fig"'), drawn.index('class="pc-scrim"')); self.assertLess(drawn.index('class="pc-scrim"'), drawn.index('pc-words'))
        self.assertIn('--pc-h:78svh', drawn); self.assertIn('--focal:20% 80%', drawn); self.assertIn('data-move="scale-settle parallax"', drawn); self.assertIn('linear-gradient(270deg', drawn)
        soft = section('mk', self.draw({**FORMS['backdrop'], 'scrim': 'soft'})); alpha = lambda html: max(float(a) for a in re.findall(r'rgba\(16,14,12,([\d.]+)\)', html))
        self.assertLess(alpha(soft), alpha(drawn), 'a deeper veil is a darker one')

    def test_a_cropped_or_staged_picture_is_never_wider_than_its_pixels_allow_on_any_screen(self):
        upright = section('mk', self.draw({'section': 'mk', 'form': 'offset', 'cols': 4, 'ratio': '3/4'}, SMALL, []))
        self.assertIn(f'--pc-max:{int(1.35 * min(418, 315 * 0.75))}px', upright); self.assertIn('data-limit="1.35"', upright)
        own = section('mk', self.draw({'section': 'mk', 'form': 'offset', 'cols': 5, 'frame': 'paper', 'tilt': -2}, SMALL, [])); self.assertIn(f'--pc-max:{int(1.35 * 418)}px', own)
        shot = section('mk', self.draw(FORMS['stage'], PAGE, SHOT)); self.assertIn('--pc-max:1344px', shot); self.assertIn('data-limit="1"', shot)

    def test_a_panorama_sets_the_heading_left_and_what_it_introduces_right(self):
        drawn = section('mk', self.draw(FORMS['panorama'])); cut = MK['words']['html'].find('</h2>') + 5
        self.assertIn(f'<div class="pc-wh">{MK["words"]["html"][:cut]}</div><div class="pc-wr">{MK["words"]["html"][cut:]}</div>', drawn)
        self.assertLess(drawn.index('<div class="pc-words'), drawn.index('<figure class="pc-fig')); below = section('mk', self.draw({**FORMS['panorama'], 'words': 'below'}))
        self.assertLess(below.index('<figure class="pc-fig'), below.index('<div class="pc-words'))

    def test_a_card_lies_over_the_inner_columns_of_its_picture(self):
        right = section('mk', self.draw(FORMS['card'])); self.assertIn('--c0:5;--c1:13', right); self.assertIn('--w0:1;--w1:7', right); self.assertIn('pc-bleeds', right)
        left = section('mk', self.draw({**FORMS['card'], 'side': 'left', 'cols': 9, 'bleed': False})); self.assertIn('--c0:1;--c1:10', left); self.assertIn('--w0:8;--w1:13', left)


def answer(*entries, concept='Each picture gets a job.'): return {'concept': concept, 'pictures': [dict(e) for e in entries]}
CLEAN = {'desktop': [{'id': 'mk', 'form': 'x', 'scale': 1.0, 'limit': 1.35, 'contrast': None, 'heading_out': 0, 'overlap': 0}], 'mobile': []}
def seen(**change): return {'desktop': [{**CLEAN['desktop'][0], **change}], 'mobile': []}


class Loop(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.dir, True); self.path = os.path.join(self.dir, 'page.html'); Path(self.path).write_text(PAGE, encoding='utf-8')
        self.asked = []; self.measured = lambda path: CLEAN; self.contract = lambda path: {}
        for target, name, stand_in in ((COMPOSE, 'measure', lambda path: self.measured(path)), (COMPOSE.HERO, 'measured', lambda path: self.contract(path)), (COMPOSE.LISTED, 'section_shots', lambda path, ids: {})):
            p = patch.object(target, name, stand_in); p.start(); self.addCleanup(p.stop)
    def ask(self, *answers):
        queue = list(answers)
        def stand_in(system, content, tool, **kw): self.asked.append(content); return queue.pop(0) if queue else None
        return stand_in
    def run_(self, *answers, review=False): return COMPOSE.compose(PAGE, self.path, images=IMAGES, ask=self.ask(*answers), review=review)
    said = lambda self, n: '\n'.join(b.get('text', '') for b in self.asked[n] if b.get('type') == 'text')

    def test_the_model_is_told_what_each_picture_is_and_which_forms_are_open(self):
        text, ids = COMPOSE.brief(PAGE, IMAGES); self.assertEqual(ids, ['mk']); self.assertIn('▸ "mk"', text); self.assertIn('1344×896 px, a photograph', text)
        self.assertIn('Forms open to it: backdrop (would draw it 1440×702 px', text); self.assertIn('"rezervacija" — cta (holds a picture but cannot be recomposed', text)
        text, _ = COMPOSE.brief(PAGE, SHOT); self.assertIn('a SCREENSHOT', text); self.assertNotIn('backdrop (would', text)

    def test_a_valid_answer_is_the_document(self):
        result = self.run_(answer(FORMS['bleed'])); self.assertTrue(result['drawn']); self.assertEqual(result['attempts'], 1)
        self.assertEqual(result['doc']['pictures'], [FORMS['bleed']]); self.assertEqual(result['doc']['note'], 'Each picture gets a job.')

    def test_fields_of_another_form_are_not_part_of_the_answer(self):
        result = self.run_(answer({**FORMS['backdrop'], 'side': 'left', 'cols': 6, 'ground': 'ink', 'ratio': None}))
        self.assertTrue(result['drawn']); self.assertEqual(result['doc']['pictures'], [FORMS['backdrop']])
        refused = self.run_(answer({**FORMS['backdrop'], 'caption': 'New words'})); self.assertFalse(refused['drawn'], 'a field that carries words is still refused')

    def test_the_validators_reasons_go_back_once(self):
        result = self.run_(answer({**FORMS['bleed'], 'cols': 11}), answer(FORMS['bleed'])); self.assertTrue(result['drawn']); self.assertEqual([s['stage'] for s in result['log']], ['compose', 'correct'])
        self.assertIn('IP020', self.said(1)); self.assertIn('WAS REFUSED', self.said(1))
        self.asked.clear(); twice = self.run_(answer({**FORMS['bleed'], 'cols': 11}), answer({**FORMS['bleed'], 'cols': 12})); self.assertFalse(twice['drawn']); self.assertEqual(len(self.asked), 2)

    def test_a_veil_that_leaves_the_words_unreadable_is_thickened_by_rule(self):
        def measured(path):
            html = Path(path).read_text(encoding='utf-8'); deep = 'rgba(16,14,12,0.82)' in html
            return CLEAN if deep else seen(contrast={'ratio': 2.1, 'need': 4.5, 'text': 'the words'})
        self.measured = measured
        result = self.run_(answer({**FORMS['backdrop'], 'scrim': 'soft'})); self.assertTrue(result['drawn']); self.assertEqual(result['doc']['pictures'][0]['scrim'], 'deep')
        settled = next(s for s in result['log'] if s['stage'] == 'settle'); self.assertEqual(len(settled['changes']), 2); self.assertIn('scrim soft→mid', settled['changes'][0]); self.assertEqual(len(self.asked), 1, 'no model call for a rule')

    def test_a_heading_out_of_its_block_is_set_smaller_and_a_picture_past_its_pixels_given_less_room(self):
        self.measured = lambda path: seen(heading_out=14) if re.search(r'<section class="[^"]*pc-t-lg', Path(path).read_text(encoding='utf-8')) else CLEAN
        self.assertEqual(self.run_(answer({**FORMS['stage'], 'title': 'lg'}))['doc']['pictures'][0]['title'], 'md')
        self.measured = lambda path: seen(scale=1.5) if '--pc-h:78svh' in Path(path).read_text(encoding='utf-8') else CLEAN
        self.assertEqual(self.run_(answer(FORMS['bleed']))['doc']['pictures'][0]['height'], 'md')

    def test_a_section_that_cannot_be_eased_goes_back_to_the_templates_form(self):
        self.measured = lambda path: seen(contrast={'ratio': 1.4, 'need': 4.5, 'text': 'the words'})
        result = self.run_(answer({**FORMS['backdrop'], 'scrim': 'deep'})); self.assertFalse(result['drawn']); self.assertIsNone(result['doc'])
        self.assertIn("back to the template's form", next(s for s in result['log'] if s['stage'] == 'settle')['changes'][0])

    def test_what_was_measured_goes_back_with_the_render_and_a_worse_revision_is_not_kept(self):
        self.contract = lambda path: {'desktop-first-screen-visual': 'small'} if 'data-form="card"' in Path(path).read_text(encoding='utf-8') else {}
        result = self.run_(answer(FORMS['bleed']), answer(FORMS['card']), review=True)
        self.assertEqual(result['doc']['pictures'][0]['form'], 'bleed'); self.assertIn('AS DRAWN', self.said(1)); self.assertIn('measured worse', result['log'][-1]['errors'][0])
        self.asked.clear(); better = self.run_(answer(FORMS['card']), answer(FORMS['bleed']), review=True); self.assertEqual(better['doc']['pictures'][0]['form'], 'bleed')
        self.assertIn('ALSO MEASURED', self.said(1))

    def test_a_refused_revision_gets_its_reasons_once(self):
        result = self.run_(answer(FORMS['bleed']), answer({**FORMS['card'], 'cols': 3}), answer(FORMS['card']), review=True)
        self.assertEqual([s['stage'] for s in result['log']], ['compose', 'revise', 'correct']); self.assertEqual(result['doc']['pictures'][0]['form'], 'card'); self.assertIn('YOUR REVISION WAS REFUSED', self.said(2))

    def test_pictures_that_break_the_page_are_not_shipped(self):
        self.contract = lambda path: {'desktop-no-overflow': '40 px'} if 'data-pc="' in Path(path).read_text(encoding='utf-8') else {}
        result = self.run_(answer(FORMS['bleed'])); self.assertFalse(result['drawn']); self.assertEqual(result['log'][-1]['stage'], 'refuse')

    def test_pictures_that_cannot_be_measured_are_not_shipped(self):
        def broken(path): raise RuntimeError('no browser')
        self.measured = broken; result = self.run_(answer(FORMS['bleed'])); self.assertFalse(result['drawn']); self.assertIn('not measured', result['log'][-1]['errors'][0])

    def test_a_page_without_a_picture_section_asks_nobody(self):
        bare = PAGE[:span('mk')[0]] + PAGE[span('mk')[1]:]; path = os.path.join(self.dir, 'bare.html'); Path(path).write_text(bare, encoding='utf-8')
        result = COMPOSE.compose(bare, path, images=IMAGES, ask=self.ask(answer(FORMS['bleed'])), review=False); self.assertFalse(result['drawn']); self.assertEqual(self.asked, [])

    def test_measurements_become_findings_by_kind(self):
        found = COMPOSE.findings_of({'desktop': [{'id': 'a', 'scale': 1.6, 'limit': 1.35, 'contrast': {'ratio': 2, 'need': 4.5, 'text': 't'}, 'heading_out': 9, 'overlap': 900}, {'id': 'b', 'scale': 1.02, 'limit': 1, 'contrast': None, 'heading_out': 0, 'overlap': 0}],
                                    'mobile': [{'id': 'a', 'scale': 1.0, 'limit': 1.35, 'contrast': {'ratio': 5, 'need': 4.5, 'text': 't'}, 'heading_out': 30, 'overlap': 0}]})
        self.assertEqual(sorted(found), ['desktop-heading-out', 'desktop-picture-over-pixels', 'desktop-words-on-picture', 'desktop-words-over-picture'])
        self.assertIn('section "a"', found['desktop-picture-over-pixels']); self.assertNotIn('"b"', found['desktop-picture-over-pixels'], 'two hundredths is rounding, not a finding')
        self.assertEqual(sorted(COMPOSE._broken(found)), sorted(found))


if __name__ == '__main__': unittest.main()
