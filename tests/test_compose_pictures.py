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
    'bleed': {'section': 'mk', 'form': 'bleed', 'side': 'right', 'cols': 6, 'align': 'center', 'edge': 'hard'},   # the sample photograph is dark at its edges and the section light: it is cut clean
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
        for broken, why in ((whole.replace('<figure', '<div>a</div><div>b</div><div>c</div><figure', 1), 'blocks'),
                            (whole.replace('<figure', 'loose words<figure', 1), 'outside its blocks'),
                            (re.sub(r'<img [^>]*>', lambda m: m.group(0) + m.group(0), whole, 1), 'one picture')):
            with self.assertRaisesRegex(ValueError, why): SECTIONS.from_picture(broken)

    def test_the_templates_heading_over_a_photo_is_read_with_its_caption(self):
        over = ('<section class="sec photo" id="story"><figure style="aspect-ratio:1.1"><img src="%s" alt="The room"><div class="wrap over"><h2 class="h2 light" style="--lw:12">Home cooking</h2></div></figure>'
                '<div class="wrap"><div class="photo-caption"><span class="lab">Since 1996</span><p class="cap">One line about the house.</p><ul class="photo-details"><li>Leganés</li></ul></div></div></section>') % picture(1400, 600)
        read = SECTIONS.from_picture(over); self.assertEqual((read['first'], read['tail'], read['words']['heading'], read['picture']['alt']), ('picture', '', 'Home cooking', 'The room'))
        self.assertEqual(read['words']['html'], '<span class="lab">Since 1996</span><h2 class="h2 light" style="--lw:12">Home cooking</h2><p class="cap">One line about the house.</p><ul class="photo-details"><li>Leganés</li></ul>', 'the heading takes its place after the label; nothing else moves')
        page = '<html><head></head><body><section class="sec hero" id="top"><h1>Hi</h1></section>' + over + '</body></html>'
        out, report = PICTURES.transplant(page, doc({'section': 'story', 'form': 'bleed', 'side': 'left', 'cols': 7, 'overlap': 1}), []); self.assertTrue(report['drawn'], report['errors'])
        self.assertEqual(out.count('Home cooking'), 1); self.assertIn('.sec.pc .pc-words .h2.light{color:inherit}', out, 'a heading that was light on its photo takes the colour of the ground it now stands on')
        with self.assertRaises(ValueError): SECTIONS.from_picture(over.replace('<div class="wrap over">', '<div class="wrap over"><b>x</b>').replace('</h2></div>', '</h2></div><p>stray</p>'))

    def test_the_picture_is_measured_and_its_kind_known(self):
        _, content = PICTURES.readable(PAGE, IMAGES)['mk']; self.assertEqual((content['picture']['w'], content['picture']['h'], content['picture']['shot']), (1344, 896, False))
        _, content = PICTURES.readable(SMALL, [])['mk']; self.assertEqual((content['picture']['w'], content['picture']['h']), (418, 315), 'without images.json the file itself is measured')
        _, content = PICTURES.readable(PAGE, SHOT)['mk']; self.assertTrue(content['picture']['shot'])
        self.assertIn('rezervacija', PICTURES.readable(PAGE, IMAGES)); self.assertIsInstance(PICTURES.readable(PAGE, IMAGES)['rezervacija'][1], str)


class OpenForms(unittest.TestCase):
    def forms(self, page, images): return [f['form'] for f in PICTURES.open_forms(PICTURES.readable(page, images)['mk'][1], CONTENT.page_of(page))]
    def test_the_picture_decides_which_forms_are_open(self):
        self.assertEqual(self.forms(PAGE, IMAGES), [f for f in PICTURES.FORMS if f != 'inline'], 'a large photograph can do anything but hide in a heading over so few words')
        self.assertEqual(self.forms(SMALL, []), ['offset', 'stage'], 'a small photograph cannot be made large: a print or an object')
        self.assertEqual(self.forms(WORDIER, []), ['offset', 'stage', 'inline'], '… or, where the section has words to carry it, a word of the heading')
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


DARK = PAGE.replace(SRC, picture(1200, 900, (12, 14, 18)))     # the same page with a picture whose edges are one dark colour (a render on black)
LIGHT = PAGE.replace(SRC, picture(1200, 900, (244, 240, 232)))   # … and one light colour (a product on white)
WORDIER = SMALL.replace(MK['words']['html'], MK['words']['html'] + '<p class="cap">' + 'There is more to say about this room. ' * 4 + '</p>', 1)   # the small photograph in a section with words to carry it
def scene(width, height):
    """A picture whose edges are a scene, not a colour."""
    from PIL import Image
    im = Image.new('RGB', (width, height)); im.putdata([((x * 7) % 256, (y * 5) % 256, (x + y) % 256) for y in range(height) for x in range(width)])
    buf = io.BytesIO(); im.save(buf, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


class NoBox(unittest.TestCase):
    """A picture never stands in a box of its own: it dissolves into its section, the section takes its ground, the type
    cuts it, or it is set into the heading."""
    def draw(self, entry, page=PAGE, images=IMAGES):
        out, report = PICTURES.transplant(page, doc(entry), images); self.assertTrue(report['drawn'], report['errors']); return section('mk', out)

    def test_the_ground_of_a_picture_is_the_colour_its_edges_share(self):
        dark = PICTURES._ground(picture(400, 300, (12, 14, 18))); self.assertTrue(dark['dark']); self.assertTrue(all(abs(a - b) <= 6 for a, b in zip(dark['rgb'], (12, 14, 18))))
        self.assertFalse(PICTURES._ground(picture(400, 300, (244, 240, 232)))['dark']); self.assertIsNone(PICTURES._ground(scene(120, 90))); self.assertIsNone(PICTURES._ground('data:image/png;base64,AAAA'))
        self.assertIsNone(PICTURES.readable(PAGE, IMAGES)['mk'][1]['picture']['ground'], 'a photograph of a room has no ground of its own')

    def test_a_section_takes_the_pictures_own_ground_and_the_words_the_colour_that_reads_on_it(self):
        own = {'section': 'mk', 'form': 'stage', 'side': 'left', 'cols': 6, 'ground': 'own'}
        dark = self.draw(own, DARK, []); self.assertIn('pc-own', dark); self.assertRegex(dark, r'--pc-ground:rgb\(1\d,1\d,\d\d\)'); self.assertIn('pc-words', dark); self.assertRegex(dark, r'class="pc-words[^"]* pc-inv"')
        self.assertRegex(self.draw(own, LIGHT, []), r'class="pc-words[^"]* pc-dk"')
        found = PICTURES.validate(doc(own), PAGE, IMAGES); self.assertEqual([e['code'] for e in found], ['IP067']); self.assertIn('a scene, not one colour', found[0]['message'])
        self.assertIn('.sec.pc.pc-own .pc-fig{box-shadow:none;border-radius:0}', PICTURES.CSS, 'on its own ground the picture has no edge and no shadow')

    def test_a_picture_that_runs_off_the_screen_dissolves_into_its_section_and_the_words_may_reach_into_it(self):
        fade = {k: v for k, v in FORMS['bleed'].items() if k != 'edge'}   # on the light page the picture and the ground are of one lightness: it dissolves, and that is the default
        self.assertIn('<i class="pc-fade"></i></figure>', self.draw(fade, LIGHT, [])); self.assertIn('pc-edge-fade', self.draw(fade, LIGHT, []))
        hard = self.draw(FORMS['bleed']); self.assertNotIn('pc-fade', hard); self.assertNotIn('data-over', hard)
        reach = self.draw({**fade, 'overlap': 2}, LIGHT, []); self.assertIn('pc-over-2', reach); self.assertIn('data-over="2"', reach)
        mud = PICTURES.validate(doc(fade), PAGE, IMAGES); self.assertEqual([e['code'] for e in mud], ['IP067']); self.assertIn('turn to mud', mud[0]['message'])
        self.assertEqual(codes(doc(fade), DARK, []), ['IP067'], 'a dark picture does not dissolve into a light section'); self.assertEqual(codes(doc({**fade, 'side': 'left'}), LIGHT, []), [])
        self.assertEqual(codes(doc({**FORMS['bleed'], 'edge': 'hard', 'overlap': 1})), ['IP067']); self.assertEqual(codes(doc({**FORMS['bleed'], 'overlap': 3})), ['IP020']); self.assertEqual(codes(doc({**FORMS['bleed'], 'edge': 'soft'})), ['IP020'])
        self.assertEqual(codes(doc({**FORMS['card'], 'edge': 'fade'})), ['IP001'])

    def test_a_picture_is_set_into_the_heading_like_a_word(self):
        heading = MK['words']['heading']; inline = {'section': 'mk', 'form': 'inline'}
        end = self.draw(inline, WORDIER, []); self.assertRegex(end, r' <span class="pc-fig pc-pill pc-pill-pill" data-limit="1.35" style="--focal:50% 50%"><img [^>]*></span></h2>'); self.assertIn('pc-t-xl', end)
        start = self.draw({**inline, 'at': 'start', 'shape': 'circle', 'title': 'lg', 'tone': 'mono'}, WORDIER, []); self.assertRegex(start, r'<h2\b[^>]*><span class="pc-fig pc-pill pc-pill-circle pc-tone"'); self.assertIn('pc-t-lg', start)
        for drawn in (end, start): self.assertEqual(drawn.count('<img '), 1); self.assertNotIn('<figure', drawn); self.assertIn(heading.split()[0], drawn)
        out, _ = PICTURES.transplant(WORDIER, doc(inline), []); text = lambda html: ' '.join(re.sub(r'<[^>]+>', ' ', re.sub(r'<style.*?</style>', '', html, flags=re.S)).split())
        self.assertEqual(text(out), text(WORDIER), 'the heading says what it said')
        self.assertEqual(codes(doc(inline), WORDIER, [{'id': 'x', 'data': picture(418, 315), 'w': 418, 'h': 315, 'shot': True}]), ['IP062']); self.assertEqual(codes(doc({**inline, 'title': 'md'}), WORDIER, []), ['IP020']); self.assertEqual(codes(doc({**inline, 'shape': 'arch'}), WORDIER, []), ['IP020'])
        found = PICTURES.validate(doc(inline), SMALL, []); self.assertEqual([e['code'] for e in found], ['IP021']); self.assertIn('a thin band with a thumbnail', found[0]['message'])
        bare = WORDIER.replace(re.search(r'<h2\b[^>]*>.*?</h2>', MK['words']['html'], re.S).group(0), '', 1); self.assertEqual(codes(doc(inline), bare, []), ['IP021'])

    def test_a_stage_may_stand_across_the_top_with_the_words_under_it(self):
        top = self.draw({'section': 'mk', 'form': 'stage', 'side': 'top', 'ground': 'ink'}); self.assertIn('pc-side-top', top)
        self.assertLess(top.index('class="pc-panel"'), top.index('class="wrap pc-wrap"')); self.assertIn('pc-split', top); self.assertNotIn('pc-col', top)
        self.assertEqual(codes(doc({**FORMS['bleed'], 'side': 'top'})), ['IP020'], 'only a stage stands across the top')

    def test_a_picture_section_may_hold_several_blocks_of_words(self):
        rows = '<ol class="rows"><li>First row</li><li>Second row</li></ol>'; whole = section('mk'); close = len(whole) - len(MK['tail'] + '</section>') - len('</div>')
        page = PAGE.replace(whole, whole.replace('<figure', rows + '<figure', 1) if MK['first'] == 'words' else whole[:close] + rows + whole[close:], 1)   # the rows follow the words block
        read = SECTIONS.from_picture(section('mk', page)); self.assertEqual(len(read['words']['parts']), 2); self.assertIn(rows, read['words']['html']); self.assertEqual(read['words']['rows'], MK['words']['rows'] + 2)
        out, report = PICTURES.transplant(page, doc(FORMS['panorama']), IMAGES); self.assertTrue(report['drawn'], report['errors']); drawn = section('mk', out)
        self.assertIn(f'<div class="pc-wr">{rows}</div>', drawn, 'the heading block to the left, the rows to the right, each whole'); self.assertEqual(drawn.count('First row'), 1)

    def test_the_words_step_back_out_of_the_picture_when_they_do_not_read_there(self):
        eased = COMPOSE._eased({**FORMS['bleed'], 'overlap': 2}, 'words-on-picture'); self.assertEqual(eased['overlap'], 1)
        self.assertIsNone(COMPOSE._eased({**FORMS['bleed'], 'overlap': 0}, 'words-on-picture'))
        text, _ = COMPOSE.brief(PAGE, IMAGES); self.assertIn('its edges are a scene', text); text, _ = COMPOSE.brief(DARK, []); self.assertIn('its edges are one even dark colour', text)
        self.assertIn('a rectangle on one side and the words on the other', COMPOSE.SYSTEM)


LEDGER = ('<section class="sec ledger band-paper" id="menu"><div class="wrap two"><div class="ledger-intro"><span class="lab">The menu</span><h2 class="h2">From the sea</h2></div>'
          '<div><ul class="rows"><li><span class="ledger-item">Sole</span><i></i><b>24 €</b></li><li><span class="ledger-item">Prawns</span><i></i><b>18 €</b></li></ul></div></div></section>')
HOURS = '<section class="sec ledger band-alt" id="hours"><div class="wrap two"><div class="ledger-intro"><h2 class="h2">Opening hours</h2></div><div><p>Every day from noon.</p></div></div></section>'
USED = picture(900, 700, (90, 80, 70))
WORDY = ('<html><head><style>:root{--paper:#ffffff;--container:1300px;--frame:40px}</style></head><body><section class="sec hero" id="top"><h1>Hello</h1><img src="%s" alt=""></section>' % USED) + LEDGER + HOURS + '</body></html>'
JOB = [{'id': 'menu-fish', 'data': picture(1600, 1067, (40, 60, 80)), 'w': 1600, 'h': 1067, 'gen': True, 'alt': 'Fish on ice'},       # commissioned for the "menu" section
       {'id': 'menu-fish-detail', 'data': picture(800, 500, (41, 61, 81)), 'w': 800, 'h': 500, 'gen': True, 'crop_of': 'menu-fish'},  # a detail cut from it
       {'id': 'gen-terrace', 'data': picture(1500, 1000, (10, 90, 30)), 'w': 1500, 'h': 1000, 'gen': True},                           # commissioned for another section
       {'id': 'room', 'data': picture(1400, 900, (120, 100, 90)), 'w': 1400, 'h': 900, 'alt': 'The dining room'},                      # a photograph the page does not show
       {'id': 'shot1', 'data': picture(1440, 900, (20, 20, 20)), 'w': 1440, 'h': 900, 'shot': True},                                   # a screen of something else
       {'id': 'thumb', 'data': picture(400, 300, (1, 2, 3)), 'w': 400, 'h': 300},                                                      # too small to matter
       {'id': 'hero', 'data': USED, 'w': 900, 'h': 700}]                                                                               # already on the page


class Offers(unittest.TestCase):
    """A section of words may take one of the job's pictures that the page does not show yet."""
    def test_what_is_offered_to_a_section(self):
        menu = PICTURES.offered(WORDY, JOB, 'menu'); self.assertEqual(sorted(menu), ['img:menu-fish', 'img:room']); self.assertTrue(menu['img:menu-fish']['meant']); self.assertFalse(menu['img:room']['meant'])
        self.assertEqual(sorted(PICTURES.offered(WORDY, JOB, 'hours')), ['img:room'], 'atmosphere made for another section, a screen of something else, a detail, a thumbnail and a picture already shown are not offered')
        self.assertEqual(sorted(PICTURES.offered(WORDY, JOB, 'terrace')), ['img:gen-terrace', 'img:room'])
        read = PICTURES.readable(WORDY, JOB); self.assertIsNone(read['menu'][1]['picture']); self.assertEqual(sorted(read['menu'][1]['offers']), ['img:menu-fish', 'img:room']); self.assertEqual(len(read['menu'][1]['words']['parts']), 2)
        self.assertEqual(PICTURES.readable(WORDY, None), {}, 'without the job\'s pictures nothing is on offer')

    def test_a_section_of_words_takes_one_offered_picture_and_says_what_it_said(self):
        entry = {'section': 'menu', 'picture': 'img:menu-fish', 'form': 'bleed', 'side': 'right', 'cols': 6, 'edge': 'hard'}
        out, report = PICTURES.transplant(WORDY, doc(entry), JOB); self.assertTrue(report['drawn'], report['errors'])
        drawn = section('menu', out); self.assertEqual(out.count(JOB[0]['data']), 1); self.assertIn('alt="Fish on ice"', drawn); self.assertIn('class="sec ledger band-paper pc pc-f-bleed', drawn)
        self.assertIn('<span class="ledger-item">Sole</span><i></i><b>24 €</b>', drawn); text = lambda html: ' '.join(re.sub(r'<[^>]+>', ' ', re.sub(r'<style.*?</style>', '', html, flags=re.S)).split())
        self.assertEqual(text(out), text(WORDY)); self.assertNotIn('img:menu-fish', PICTURES.readable(out, JOB).get('hours', (None, {'offers': {}}))[1].get('offers', {}), 'a picture that is now on the page is no longer on offer')
        strip, report = PICTURES.transplant(WORDY, doc({'section': 'menu', 'picture': 'img:menu-fish', 'form': 'panorama'}), JOB); self.assertTrue(report['drawn'], report['errors']); self.assertIn('<div class="pc-wh"><div class="ledger-intro">', strip)

    def test_one_defect_per_rule(self):
        base = {'section': 'menu', 'picture': 'img:menu-fish', 'form': 'bleed', 'edge': 'hard'}
        self.assertEqual(codes(doc({'section': 'menu', 'form': 'bleed'}), WORDY, JOB), ['IP010'], 'a section of words needs a picture'); self.assertEqual(codes(doc({**base, 'picture': 'img:gen-terrace'}), WORDY, JOB), ['IP010'], 'only what is offered to it')
        self.assertEqual(codes(doc({**base, 'picture': 'img:room'}, {'section': 'hours', 'picture': 'img:room', 'form': 'bleed', 'edge': 'hard'}), WORDY, JOB), ['IP061'], 'a picture is shown once')
        for form in ('offset', 'stage', 'inline'): self.assertEqual(codes(doc({'section': 'menu', 'picture': 'img:menu-fish', 'form': form}), WORDY, JOB), ['IP065'], f'atmosphere is never an object: {form}')
        self.assertEqual(codes(doc({'section': 'menu', 'picture': 'img:room', 'form': 'stage', 'ground': 'ink'}), WORDY, JOB), [], 'a photograph may stand on a stage')
        self.assertEqual(codes(doc({**FORMS['bleed'], 'picture': 'img:room'})), ['IP001'], 'a section with its own picture takes no other')

    def test_the_composer_is_shown_what_is_on_offer(self):
        text, ids = COMPOSE.brief(WORDY, JOB); self.assertEqual(ids, ['menu', 'hours']); self.assertIn('▸ "menu" — ledger, WORDS ONLY', text); self.assertIn('img:menu-fish ★ made for this section — 1600×1067 px, a commissioned atmosphere picture, "Fish on ice"', text)
        self.assertIn('(forms: backdrop, bleed, panorama, card)', text, 'atmosphere is offered only the forms that crop it'); self.assertEqual([a for a, _ in COMPOSE.brief.offered], ['img:menu-fish', 'img:room', 'img:room'])
        self.assertIn('"picture": {"type": "string"', json.dumps(COMPOSE.ENTRY)); self.assertIn('a document, a notice', COMPOSE.SYSTEM)


class Screens(unittest.TestCase):
    """A product screen is set down with a hairline ring and one soft shadow; a tall one may show its top and fade."""
    TALL = [dict(i, shot=True, w=1200, h=1600) if i.get('data') == SRC else i for i in IMAGES]
    def test_a_tall_screen_shows_its_top_and_fades_into_the_stage(self):
        entry = {'section': 'mk', 'form': 'stage', 'side': 'right', 'cols': 7, 'ground': 'ink', 'crop': 'fade'}
        out, report = PICTURES.transplant(PAGE, doc(entry), self.TALL); self.assertTrue(report['drawn'], report['errors']); drawn = section('mk', out)
        self.assertIn('pc-screen pc-crop', drawn); self.assertIn('--crop:1.5', drawn); self.assertIn('<i class="pc-cropfade"></i></figure>', drawn); self.assertIn('pc-cropped', drawn); self.assertIn('data-limit="1"', drawn)
        self.assertEqual(codes(doc({**entry, 'tilt': 2}), PAGE, self.TALL), ['IP067']); self.assertEqual(codes(doc({**entry, 'crop': 'top'}), PAGE, self.TALL), ['IP020'])
        self.assertEqual(codes(doc(entry), PAGE, IMAGES), ['IP067'], 'a photograph is not shown this way'); self.assertEqual(codes(doc(entry), PAGE, SHOT), ['IP067'], 'a screen already wider than the crop is shown whole')

    def test_no_heavy_shadow_is_left(self):
        import render_ir as IR
        for css in (PICTURES.CSS, IR.CSS): self.assertNotIn('rgba(0,0,0,.6)', css); self.assertNotIn('rgba(0,0,0,.55)', css)
        for css in (PICTURES.CSS, IR.CSS): self.assertNotIn('0 24px 60px', css, 'no soft shadow either: none of 248 reference pictures carries one')
        self.assertIn('.pc-fig.pc-screen{border-radius:8px;box-shadow:0 0 0 1px color-mix(in srgb,currentColor 14%,transparent)}', PICTURES.CSS)
        whole = section('mk', PICTURES.transplant(PAGE, doc(FORMS['stage']), SHOT)[0]); self.assertIn('pc-contain pc-screen', whole); self.assertNotIn('pc-screen', section('mk', PICTURES.transplant(PAGE, doc(FORMS['stage']), IMAGES)[0]))


def room(sid, band, title, colour, extra=''):
    return (f'<section class="sec photo inset band-{band}" id="{sid}"><div class="wrap inset-wrap"><figure style="aspect-ratio:1.327"><img src="{picture(418, 315, colour)}" alt="{title}"></figure>'
            f'<div class="photo-caption"><span class="lab">Rooms</span><h2 class="h2">{title}</h2><p class="cap">One line about the {title.lower()}.</p>{extra}</div></div></section>')
ROOMS = ('<html><head><style>:root{--paper:#ffffff;--container:1300px;--frame:40px}</style></head><body><section class="sec hero" id="top"><h1>Hello</h1></section>'
         + room('terrace', 'paper', 'Terrace', (200, 180, 150)) + room('hall', 'alt', 'Hall', (150, 120, 100)) + room('lounge', 'dark', 'Lounge', (30, 60, 90)) + LEDGER + room('garden', 'paper', 'Garden', (60, 120, 60)) + '</body></html>')
ROW = {'sections': ['terrace', 'hall', 'lounge'], 'ratio': '4/3', 'title': 'lg'}
def gallery(*runs, pictures=()): return {'ir': '0.2', 'pictures': [dict(p) for p in pictures], 'galleries': [dict(r) for r in runs]}


class Galleries(unittest.TestCase):
    """Neighbouring sections that each show a small photograph are run as one row: together they are a spine."""
    def test_a_run_of_neighbours_becomes_one_row_and_every_section_keeps_its_words_and_its_anchor(self):
        self.assertEqual(PICTURES.validate(gallery(ROW), ROOMS, []), []); self.assertEqual(PICTURES.validate({'ir': '0.2', 'galleries': [ROW]}, ROOMS, []), [], 'a document may be galleries alone')
        out, report = PICTURES.transplant(ROOMS, gallery(ROW), []); self.assertTrue(report['drawn'], report['errors']); self.assertEqual(report['sections'], ['hall', 'lounge', 'terrace'])
        row = section('terrace', out); self.assertRegex(row, r'^<section class="sec photo inset band-paper pc pc-f-gallery pc-t-lg" id="terrace" data-pc="0.2" data-form="gallery"'); self.assertIn('style="--n:3;--ratio:4/3"', row)
        self.assertEqual(row.count('<article class="pc-gi"'), 3); self.assertIn('<article class="pc-gi" id="hall">', row); self.assertIn('<article class="pc-gi" id="lounge">', row); self.assertEqual(row.count('<img '), 3)
        for title in ('Terrace', 'Hall', 'Lounge'): self.assertIn(f'<h2 class="h2">{title}</h2><p class="cap">One line about the {title.lower()}.</p>', row)
        text = lambda html: ' '.join(re.sub(r'<[^>]+>', ' ', re.sub(r'<style.*?</style>', '', html, flags=re.S)).split()); self.assertEqual(text(out), text(ROOMS))
        self.assertEqual(len(SECTIONS.sections(out)), len(SECTIONS.sections(ROOMS)) - 2); self.assertIn('id="garden"', out); self.assertEqual(PICTURES.readable(out, [])['terrace'][1], 'this section is already composed', 'a composed row is not composed again')

    def test_one_defect_per_rule(self):
        for bad, code in (({'sections': ['terrace', 'lounge']}, 'IP010'), ({'sections': ['hall', 'terrace']}, 'IP010'), ({'sections': ['terrace']}, 'IP010'), ({'sections': ['terrace', 'hall', 'lounge', 'menu']}, 'IP010'),
                          ({'sections': ['lounge', 'garden']}, 'IP010'), ({**ROW, 'ratio': '21/9'}, 'IP020'), ({**ROW, 'title': 'xl'}, 'IP020'), ({**ROW, 'cols': 3}, 'IP001'), ({'sections': ['terrace', 'hall'], 'ratio': '3/4'}, 'IP060')):
            self.assertEqual(codes(gallery(bad), ROOMS, []), [code], bad)
        self.assertEqual(codes(gallery(ROW, pictures=[{'section': 'hall', 'form': 'stage', 'ground': 'ink'}]), ROOMS, []), ['IP010'], 'a section is in a gallery or has an entry of its own, not both')
        self.assertEqual(codes({'ir': '0.2', 'pictures': [], 'galleries': []}, ROOMS, []), ['IP001'])
        shot = [{'id': 'h', 'data': picture(418, 315, (150, 120, 100)), 'w': 418, 'h': 315, 'shot': True}]; self.assertEqual(codes(gallery(ROW), ROOMS, shot), ['IP062'])
        wordy = ROOMS.replace('One line about the hall.', 'A long account of the hall. ' * 14); self.assertEqual(codes(gallery(ROW), wordy, []), ['IP021'])

    def test_the_composer_is_shown_the_runs_and_a_refused_gallery_goes_back_to_its_sections(self):
        text, ids = COMPOSE.brief(ROOMS, []); self.assertIn('RUNS OF NEIGHBOURS that can be one gallery ("galleries"): ["terrace", "hall", "lounge"]', text); self.assertNotIn('"garden"]', text.split('RUNS OF NEIGHBOURS')[1])
        doc_ = COMPOSE._to_doc({'concept': 'A row of rooms.', 'galleries': [dict(ROW, tone=None)]}); self.assertEqual(doc_['pictures'], []); self.assertEqual(doc_['galleries'], [ROW])
        self.assertEqual(COMPOSE.settle.__doc__ is not None, True)
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, 'rooms.html'); Path(path).write_text(ROOMS, encoding='utf-8'); asked = []
            def ask(system, content, tool, **kw): asked.append(1); return {'concept': 'Rooms.', 'pictures': [{'section': 'garden', 'form': 'stage', 'ground': 'ink'}], 'galleries': [{'sections': ['terrace', 'lounge']}]}
            with patch.object(COMPOSE, 'measure', lambda p: {'desktop': [], 'mobile': []}), patch.object(COMPOSE.HERO, 'measured', lambda p: {}), patch.object(COMPOSE.LISTED, 'section_shots', lambda p, i: {}):
                result = COMPOSE.compose(ROOMS, path, images=[], ask=ask, review=False)
                self.assertTrue(result['drawn']); self.assertNotIn('galleries', result['doc']); self.assertEqual([p['section'] for p in result['doc']['pictures']], ['garden']); self.assertEqual(len(asked), 2)
                self.assertIn({'stage': 'prune', 'errors': [], 'dropped': ['galleries']}, result['log'])
                over = lambda p: {'desktop': [{'id': 'terrace', 'form': 'gallery', 'scale': 1.7, 'limit': 1.35, 'contrast': None, 'heading_out': 0, 'overlap': 0}], 'mobile': []}
                with patch.object(COMPOSE, 'measure', over): settled, changes, _ = COMPOSE.settle(ROOMS, gallery(ROW), [], temp)
                self.assertIsNone(settled); self.assertIn("goes back to the template's sections", changes[0])


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

    def test_an_entry_still_refused_costs_its_own_section_not_the_others(self):
        path = os.path.join(self.dir, 'wordy.html'); Path(path).write_text(WORDY, encoding='utf-8')
        good = {'section': 'menu', 'picture': 'img:menu-fish', 'form': 'panorama'}; bad = {'section': 'hours', 'form': 'bleed', 'edge': 'hard'}   # a section of words without its picture
        result = COMPOSE.compose(WORDY, path, images=JOB, ask=self.ask(answer(good, bad), answer(good, bad)), review=False)
        self.assertTrue(result['drawn']); self.assertEqual(result['doc']['pictures'], [good]); self.assertEqual([s['stage'] for s in result['log']], ['compose', 'correct', 'prune']); self.assertEqual(result['log'][-1]['dropped'], ['hours'])
        self.assertEqual(PICTURES.validate(result['doc'], WORDY, JOB), [], 'what is left is a document that validates whole')
        alone = COMPOSE.compose(WORDY, path, images=JOB, ask=self.ask(answer(bad), answer(bad)), review=False); self.assertFalse(alone['drawn'], 'nothing is left to draw')
        prune = COMPOSE.HERO._pruned; self.assertEqual(prune({'ir': '9', 'pictures': [good, bad]}, 'pictures', [{'at': 'ir', 'code': 'IP001', 'message': ''}], lambda d: []), (None, []), 'a fault of the document itself costs all of it')

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
