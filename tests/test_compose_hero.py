"""A hero composition places the page's own content; it cannot change it, add to it or drop it, and a composition the
validator refuses is never drawn. One seeded defect per validator code; the renderer is deterministic and escapes."""
import copy, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'compose'))
import content as CONTENT
import render_ir as IR
import validate as V


def production_page(edit=None):
    """A real page from the production renderer: a place with photographs, on the tengile blueprint."""
    with tempfile.TemporaryDirectory() as temp:
        job = Path(temp)
        for name in ('direction', 'images', 'inventory', 'assets'):
            src = ROOT / 'tests' / f'{name}.sample.json'
            if src.is_file(): shutil.copy(src, job / f'{name}.json')
        d = json.loads((job / 'direction.json').read_text()); d['kind'] = 'place'
        if edit: edit(d)
        (job / 'direction.json').write_text(json.dumps(d))
        out = job / 'page.html'
        r = subprocess.run([sys.executable, str(ROOT / 'lib/render/render_bp.py'), str(job), 'tengile', str(out)], capture_output=True, text=True, env={**os.environ, 'LIVETEST': '1'})
        assert r.returncode == 0, r.stderr
        return out.read_text(), json.loads((job / 'images.json').read_text())


PAGE, IMAGES = production_page()
BASE = CONTENT.from_page(PAGE, IMAGES)


def composition(content=BASE):
    """A valid composition for whatever the hero offers: labels on top, headline left, picture right, lede and actions below."""
    nodes = []
    if 'hero.category' in content['text']: nodes.append({'id': 'cat', 't': 'text', 'src': 'hero.category', 'as': 'label', 'at': {'col': [1, 7], 'row': 1}})
    if 'hero.fact' in content['text']: nodes.append({'id': 'fact', 't': 'text', 'src': 'hero.fact', 'as': 'label', 'align': 'end', 'at': {'col': [8, 13], 'row': 1}})
    nodes.append({'id': 'h1', 't': 'text', 'src': 'hero.h1', 'as': 'h1', 'size': 'xxl', 'measure': 10, 'at': {'col': [1, 8], 'row': 2}})
    if 'hero.picture' in content['media']: nodes.append({'id': 'pic', 't': 'media', 'src': 'hero.picture', 'fit': 'cover', 'ratio': '4/3', 'at': {'col': [8, 13], 'row': [2, 5], 'z': 0}})
    if 'hero.lede' in content['text']: nodes.append({'id': 'lede', 't': 'text', 'src': 'hero.lede', 'as': 'lede', 'measure': 40, 'at': {'col': [1, 7], 'row': 3}})
    if content['actions']: nodes.append({'id': 'go', 't': 'actions', 'src': sorted(content['actions']), 'at': {'col': [1, 7], 'row': 4}})
    return {'ir': '0.1', 'hero': {'surface': 'paper', 'height': 'screen', 'rows': ['auto', '1fr', 'auto', 'auto'], 'gap': 'md', 'nodes': nodes}}


def codes(ir, content=BASE): return sorted({e['code'] for e in V.validate(ir, content)})

def node(ir, nid): return next(n for n in ir['hero']['nodes'] if n['id'] == nid)


class Content(unittest.TestCase):
    def test_addresses_are_the_production_heros_own_words_links_and_picture(self):
        d = json.loads((ROOT / 'tests' / 'direction.sample.json').read_text())
        self.assertEqual(''.join(t for t, _ in BASE['text']['hero.h1']).strip(), d['hero']['h1'].replace('<em>', '').replace('</em>', ''))
        self.assertEqual(BASE['text']['hero.lede'], ' '.join(d['hero']['lede'].split()))
        start, end = BASE['span']; hero = PAGE[start:end]
        self.assertTrue(BASE['actions'], 'the production hero has at least one button')
        for action in BASE['actions'].values():
            self.assertIn(f'href="{IR.e(action["href"])}"', hero); self.assertNotIn('→', action['label'])
        picture = BASE['media']['hero.picture']
        self.assertEqual((picture['w'], picture['h']), (1344, 896)); self.assertIn(picture['src'], hero)
        self.assertEqual(BASE['page'], {'container': BASE['page']['container'], 'frame': BASE['page']['frame']})

    def test_emphasis_in_the_headline_survives_as_structure_not_markup(self):
        page, images = production_page(lambda d: d['hero'].update(h1='Stari grad, <em>nova</em> kuhinja'))
        segments = CONTENT.from_page(page, images)['text']['hero.h1']
        self.assertEqual([(t.strip(), em) for t, em in segments], [('Stari grad,', False), ('nova', True), ('kuhinja', False)])

    def test_a_page_without_a_hero_is_refused(self):
        with self.assertRaises(ValueError): CONTENT.from_page('<html><body><section class="sec cards"></section></body></html>', [])


class Validator(unittest.TestCase):
    def test_the_base_composition_may_be_drawn(self):
        self.assertEqual(V.validate(composition(), BASE), [])

    def test_structure(self):
        self.assertEqual(codes({'ir': '9.9', 'hero': {}}), ['IR001'])
        ir = composition(); ir['hero']['surface'] = 'neon'; self.assertEqual(codes(ir), ['IR001'])
        for surface in ('dark', 'alt', 'accent'):   # the nav above cannot follow another surface yet
            ir = composition(); ir['hero']['surface'] = surface; self.assertEqual(codes(ir), ['IR001'], surface)
        ir = composition(); ir['hero']['rows'] = ['auto', '3fr']; self.assertEqual(codes(ir), ['IR001'])
        ir = composition(); ir['hero']['nodes'].append(dict(node(ir, 'h1'))); self.assertIn('IR001', codes(ir))   # duplicate id
        ir = composition(); node(ir, 'h1')['colour'] = '#f00'; self.assertEqual(codes(ir), ['IR001'])

    def test_a_composition_cannot_contain_words_or_links(self):
        for field, value in (('text', 'Best restaurant in town'), ('html', '<b>hi</b>'), ('href', 'https://evil.test')):
            ir = composition(); node(ir, 'lede')[field] = value
            self.assertEqual(codes(ir), ['IR011'], field)

    def test_unknown_addresses(self):
        ir = composition(); node(ir, 'lede')['src'] = 'hero.slogan'; self.assertEqual(codes(ir), ['IR010', 'IR020'])
        ir = composition(); node(ir, 'pic')['src'] = 'img:nope'; self.assertEqual(codes(ir), ['IR010'])
        ir = composition(); node(ir, 'go')['src'] = ['hero.buy']; self.assertIn('IR010', codes(ir))

    def test_every_piece_of_text_and_every_action_is_placed_exactly_once(self):
        ir = composition(); ir['hero']['nodes'] = [n for n in ir['hero']['nodes'] if n['id'] != 'lede']; self.assertEqual(codes(ir), ['IR020'])
        ir = composition(); twin = dict(node(ir, 'lede'), id='lede2', at={'col': [8, 13], 'row': 1}); ir['hero']['nodes'] = [n for n in ir['hero']['nodes'] if n['id'] != 'fact'] + [twin]
        self.assertIn('IR020', codes(ir))
        ir = composition(); ir['hero']['nodes'] = [n for n in ir['hero']['nodes'] if n['id'] != 'go']; self.assertEqual(codes(ir), ['IR021'])

    def test_placement_stays_on_the_grid(self):
        for at in ({'col': [0, 5], 'row': 2}, {'col': [5, 5], 'row': 2}, {'col': [1, 14], 'row': 2}, {'col': [1, 8], 'row': 9}, {'col': [1, 8]}, {'col': [1, 8], 'row': 2, 'z': 9}, {'col': [1.5, 8], 'row': 2}):
            ir = composition(); node(ir, 'h1')['at'] = at
            self.assertIn('IR030', codes(ir), at)

    def test_text_never_sits_on_text(self):
        ir = composition(); node(ir, 'lede')['at'] = {'col': [3, 8], 'row': 2}   # onto the headline, clear of the picture
        self.assertEqual(codes(ir), ['IR031'])

    def test_text_on_a_picture_needs_a_plate_or_a_scrim(self):
        ir = composition(); node(ir, 'h1')['at'] = {'col': [1, 10], 'row': 2, 'z': 2}
        self.assertEqual(codes(ir), ['IR032'])
        with_plate = copy.deepcopy(ir); node(with_plate, 'h1')['plate'] = 'paper'; self.assertEqual(codes(with_plate), [])
        with_scrim = copy.deepcopy(ir); node(with_scrim, 'pic')['scrim'] = True; self.assertEqual(codes(with_scrim), [])
        ir = composition(); node(ir, 'go')['at'] = {'col': [8, 12], 'row': 4}; self.assertEqual(codes(ir), ['IR032'])

    def test_sizes_and_measures_come_from_the_scale(self):
        ir = composition(); node(ir, 'h1')['size'] = '300px'; self.assertEqual(codes(ir), ['IR041'])
        ir = composition(); node(ir, 'h1')['measure'] = 90; self.assertEqual(codes(ir), ['IR041'])
        ir = composition(); node(ir, 'cat')['size'] = 'mega'; self.assertEqual(codes(ir), ['IR041'])

    def test_a_picture_is_not_stretched_past_its_pixels(self):
        small = copy.deepcopy(BASE); small['media']['hero.picture'] = dict(small['media']['hero.picture'], w=320, h=213)   # five columns at 4/3 is about 490×370 px: more than 1.35× this picture
        self.assertEqual(codes(composition(small), small), ['IR060'])
        narrow = composition(small); node(narrow, 'pic')['at'] = {'col': [10, 13], 'row': [2, 5], 'z': 0}; node(narrow, 'pic')['ratio'] = '3/2'
        self.assertEqual(codes(narrow, small), ['IR066'], 'small enough to be sharp is too small to register: such a picture cannot be the first screen\'s picture')
        medium = copy.deepcopy(BASE); medium['media']['hero.picture'] = dict(medium['media']['hero.picture'], w=700, h=467)
        self.assertEqual(codes(composition(medium), medium), [], 'five columns at 4/3 is within 1.35× of a 700 px picture')
        unknown = copy.deepcopy(BASE); unknown['media']['hero.picture'] = dict(unknown['media']['hero.picture'], w=None, h=None)
        self.assertEqual(codes(composition(unknown), unknown), ['IR063'])
        ir = composition(); node(ir, 'pic').pop('ratio'); self.assertEqual(codes(ir), ['IR064'])

    def test_a_placed_picture_is_large_enough_to_register(self):
        ir = composition(); node(ir, 'pic')['at'] = {'col': [11, 13], 'row': [2, 5], 'z': 0}
        self.assertEqual(codes(ir), ['IR066'])
        ir = composition(); ir['hero']['nodes'] = [n for n in ir['hero']['nodes'] if n['id'] != 'pic']
        self.assertEqual(codes(ir), [], 'no picture at all is a choice: type alone can carry a first screen')

    def test_a_picture_appears_once_and_is_real(self):
        elsewhere = copy.deepcopy(BASE); elsewhere['used_elsewhere'] = ['hero.picture']
        self.assertEqual(codes(composition(elsewhere), elsewhere), ['IR061'])
        generated = copy.deepcopy(BASE); generated['media']['hero.picture'] = dict(generated['media']['hero.picture'], gen=True)
        self.assertEqual(codes(composition(generated), generated), ['IR065'])

    def test_a_screenshot_is_framed_never_cropped_or_bled(self):
        shot = copy.deepcopy(BASE); shot['media']['hero.picture'] = dict(shot['media']['hero.picture'], shot=True)
        self.assertEqual(codes(composition(shot), shot), ['IR062'])
        ok = composition(shot); node(ok, 'pic').update(fit='contain', frame='browser')
        self.assertEqual(codes(ok, shot), [])

    def test_bleed_only_from_the_edge_column(self):
        ir = composition(); node(ir, 'pic')['bleed'] = 'left'; self.assertEqual(codes(ir), ['IR030'])
        ir = composition(); node(ir, 'pic')['bleed'] = 'right'; self.assertEqual(codes(ir), [])

    def test_reading_order_and_roles(self):
        ir = composition(); nodes = ir['hero']['nodes']; lede = node(ir, 'lede'); nodes.remove(lede); nodes.insert(0, lede)
        self.assertEqual(codes(ir), ['IR080'])
        ir = composition(); node(ir, 'h1')['as'] = 'label'; node(ir, 'h1').pop('size'); node(ir, 'h1').pop('measure')
        self.assertEqual(codes(ir), ['IR080'])

    def test_phone_order_names_every_node(self):
        ir = composition(); ids = [n['id'] for n in ir['hero']['nodes']]
        ir['hero']['sm'] = {'order': ids[:-1]}; self.assertEqual(codes(ir), ['IR090'])
        ir['hero']['sm'] = {'order': list(reversed(ids))}; self.assertEqual(codes(ir), [])

    def test_a_composition_that_says_it_needs_more_is_not_drawn(self):
        ir = composition(); ir['unsupported'] = [{'intent': 'the picture cut on a diagonal', 'missing': 'mask: polygon'}]
        self.assertEqual(codes(ir), ['IR100'])

    def test_motion_comes_from_the_vocabulary(self):
        ir = composition(); ir['hero']['enter'] = 'spin'; self.assertEqual(codes(ir), ['IR070'])


class Renderer(unittest.TestCase):
    def test_same_composition_same_bytes_and_the_content_is_the_pages_own(self):
        ir = composition()
        first, report = IR.transplant(PAGE, ir, IMAGES); second, _ = IR.transplant(PAGE, ir, IMAGES)
        self.assertTrue(report['drawn']); self.assertEqual(first, second)
        start, end = CONTENT.hero_span(first); hero = first[start:end]
        self.assertIn('class="sec hero ir"', hero); self.assertIn('data-ir="0.1"', hero)
        self.assertEqual(hero.count('<h1'), 1)
        self.assertIn(IR.e(BASE['text']['hero.lede']), hero)
        for action in BASE['actions'].values(): self.assertIn(f'href="{IR.e(action["href"])}"', hero)
        self.assertEqual(hero.count('<a '), len(BASE['actions']), 'no link the production hero did not have')
        self.assertEqual(first.count('id="ir-css"'), 1)
        # the rest of the page is byte-for-byte what production built
        old_start, old_end = BASE['span']
        self.assertEqual(first[:start].replace(f'<style id="ir-css">{IR.CSS}</style>', ''), PAGE[:old_start]); self.assertEqual(first[end:], PAGE[old_end:])

    def test_recomposing_a_composed_page_keeps_one_stylesheet_and_the_same_content(self):
        once, _ = IR.transplant(PAGE, composition(), IMAGES)
        again_content = CONTENT.from_page(once, IMAGES)
        self.assertEqual(again_content['text'], BASE['text']); self.assertEqual(again_content['actions'], BASE['actions'])
        twice, report = IR.transplant(once, composition(again_content), IMAGES)
        self.assertTrue(report['drawn'], report['errors']); self.assertEqual(twice.count('id="ir-css"'), 1)

    def test_a_refused_composition_leaves_the_page_untouched_and_says_why(self):
        ir = composition(); node(ir, 'lede')['text'] = 'We are the best'
        page, report = IR.transplant(PAGE, ir, IMAGES)
        self.assertEqual(page, PAGE); self.assertFalse(report['drawn'])
        self.assertEqual([e['code'] for e in report['errors']], ['IR011'])

    def test_everything_drawn_is_escaped(self):
        hostile = copy.deepcopy(BASE)
        hostile['text']['hero.lede'] = '<script>alert(1)</script> & "quoted"'
        hostile['text']['hero.h1'] = [('<img src=x onerror=1> ', False), ('<b>bold</b>', True)]
        for action in hostile['actions'].values(): action['label'] = '"><script>x</script>'
        html = IR.render_hero(composition(hostile), hostile)
        self.assertNotIn('<script>', html); self.assertNotIn('<img src=x', html); self.assertNotIn('<b>', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt; &amp; &quot;quoted&quot;', html)
        self.assertIn('<em>&lt;b&gt;bold&lt;/b&gt;</em>', html)

    def test_phone_order_and_long_words_are_carried_into_the_markup(self):
        ir = composition(); ids = [n['id'] for n in ir['hero']['nodes']]; ir['hero']['sm'] = {'order': list(reversed(ids))}
        html = IR.render_hero(ir, BASE)
        self.assertIn(f'data-node="{ids[0]}"', html); self.assertRegex(html, rf'data-node="{ids[0]}" style="[^"]*--sm:{len(ids) - 1}"')
        longest = max(len(w) for w in ''.join(t for t, _ in BASE['text']['hero.h1']).split())
        self.assertIn(f'--lw:{longest}', html)

    def test_shipped_compositions_are_well_formed(self):
        """The hand-written compositions in bench/ against stand-in content that has every address they name."""
        for path in sorted((ROOT / 'bench' / 'compositions').glob('*.json')):
            ir = json.loads(path.read_text()); stand_in = {'text': {}, 'actions': {}, 'media': {}, 'page': {'container': 1300, 'frame': 40}, 'used_elsewhere': []}
            for n in ir['hero']['nodes']:
                if n['t'] == 'text': stand_in['text'][n['src']] = [('Headline here', False)] if n['as'] == 'h1' else 'Some words'
                if n['t'] == 'actions':
                    for s in n['src']: stand_in['actions'][s] = {'label': 'Go', 'href': 'https://example.test/', 'ghost': False}
                if n['t'] == 'media': stand_in['media'][n['src']] = {'src': 'data:image/png;base64,AAAA', 'alt': '', 'w': 2400, 'h': 2400, 'shot': n.get('fit') == 'contain', 'gen': False}
            self.assertEqual(V.validate(ir, stand_in), [], path.name)
            self.assertIn('data-ir="0.1"', IR.render_hero(ir, stand_in))


if __name__ == '__main__':
    unittest.main()
