"""A page is set in a system of faces — display, running text, small print — chosen from the registry of free faces.
The registry says what each face may be used for and which systems sit well together; a composition names the faces,
the validator holds it to the registry, the renderer loads them in one request and sets the page's tokens. No network."""
import copy, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'compose')); sys.path.insert(0, str(ROOT / 'lib' / 'type'))
import compose as COMPOSE
import content as CONTENT
import faces as FACES
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
BASE = CONTENT.from_page(PAGE, IMAGES)


def composition(content=BASE, **hero):
    nodes = [{'id': 'h1', 't': 'text', 'src': 'hero.h1', 'as': 'h1', 'at': {'col': [1, 10], 'row': 1}}]
    row = 2
    for address in sorted(content['text']):
        if address != 'hero.h1': nodes.append({'id': f'n{row}', 't': 'text', 'src': address, 'as': 'lede' if address == 'hero.lede' else 'label', 'at': {'col': [1, 8], 'row': row}}); row += 1
    if content['actions']: nodes.append({'id': 'go', 't': 'actions', 'src': sorted(content['actions']), 'at': {'col': [1, 8], 'row': row}}); row += 1
    return {'ir': V.VERSION, 'hero': dict({'rows': ['auto'] * (row - 1), 'nodes': nodes}, **hero)}
def codes(ir, content=BASE): return sorted({e['code'] for e in V.validate(ir, content)})


class Registry(unittest.TestCase):
    def test_every_face_says_what_it_may_be_used_for(self):
        display, body, label = (FACES.of_role(r) for r in ('display', 'body', 'label'))
        self.assertGreaterEqual(len(display), 28); self.assertGreaterEqual(len(body), 12); self.assertGreaterEqual(len(label), 5)
        self.assertTrue(all(f['kind'] == 'mono' for f in label), 'the small print is set in a monospace'); self.assertFalse({f['id'] for f in label} & {f['id'] for f in display})
        self.assertIn('fraunces', [f['id'] for f in display]); self.assertNotIn('inter', [f['id'] for f in display], 'a text face is not a face for headings')
        self.assertEqual({f['id'] for f in FACES.all() if f.get('common')}, {'geist', 'space-grotesk', 'instrument-serif'}, 'the faces of every machine-made page this year are marked')

    def test_a_pairing_is_three_faces_of_the_right_kind(self):
        self.assertGreaterEqual(len(FACES.pairings()), 12); self.assertEqual(len({p['id'] for p in FACES.pairings()}), len(FACES.pairings()))
        for p in FACES.pairings():
            with self.subTest(p['id']):
                for role in ('display', 'body', 'label'): self.assertIn(p[role], [f['id'] for f in FACES.of_role(role)], role)
                self.assertGreater(len(p['voice']), 10); self.assertNotIn(p['display'], ('geist', 'space-grotesk', 'instrument-serif'), 'no pairing leads with a face that is seen everywhere')

    def test_nothing_comes_from_a_foundry_that_forbids_generators(self):
        for f in FACES.all(): self.assertNotIn('css', f, 'every face is loaded from Google Fonts (SIL OFL)'); self.assertNotIn('fontshare', json.dumps(f).lower())
        self.assertIn('Fontshare', json.load(open(ROOT / 'lib/type/faces.json'))['about'], 'and the registry says why')

    def test_several_faces_load_in_one_request(self):
        get = FACES.get; urls = FACES.links([get('fraunces'), get('figtree'), get('dm-mono'), get('fraunces'), None])
        self.assertEqual(len(urls), 1); self.assertEqual(urls[0].count('family='), 3); self.assertIn('family=Fraunces:', urls[0]); self.assertIn('&family=Figtree:', urls[0]); self.assertTrue(urls[0].endswith('&display=swap'))
        self.assertEqual(FACES.links([get('fraunces')]), [FACES.link(get('fraunces'))]); self.assertEqual(FACES.links([]), [])


class System(unittest.TestCase):
    def test_a_composition_may_set_the_running_text_and_the_small_print(self):
        for system in ({'body': 'figtree', 'label': 'dm-mono'}, {'body': 'literata'}, {'label': 'space-mono'}): self.assertEqual(V.validate(composition(type=system), BASE), [], system)
        self.assertEqual(V.validate(composition(face={'id': 'young-serif'}, type={'body': 'figtree', 'label': 'dm-mono'}), BASE), [])

    def test_only_from_the_registry_and_only_in_its_role(self):
        for system in ({'body': 'comic-sans'}, {'label': 'figtree'}, {'body': 'dm-mono'}, {'body': 'bebas-neue'}, {'heading': 'fraunces'}, {}, 'figtree'): self.assertEqual(codes(composition(type=system)), ['IR050'], system)
        self.assertEqual(codes(composition(face={'id': 'inter'})), ['IR050'], 'a text face cannot be the display face'); self.assertEqual(codes(composition(face={'id': 'dm-mono'})), ['IR050'])

    def test_a_brands_own_faces_are_kept(self):
        locked = copy.deepcopy(BASE); locked['page']['face_locked'] = True; self.assertEqual(codes(composition(locked, type={'body': 'figtree'}), locked), ['IR051'])

    def test_the_page_loads_the_system_once_and_follows_it(self):
        page, report = IR.transplant(PAGE, composition(face={'id': 'young-serif'}, type={'body': 'figtree', 'label': 'dm-mono'}), IMAGES); self.assertTrue(report['drawn'], report['errors'])
        self.assertEqual(page.count('id="ir-face"'), 1); link = page[page.index('<link id="ir-face"'):]; link = link[:link.index('>')]
        for family in ('Young+Serif', 'Figtree', 'DM+Mono'): self.assertIn(family, link)
        css = page[page.index('<style id="ir-face-css">'):]; css = css[:css.index('</style>')]
        self.assertIn("--display:'Young Serif',Georgia,serif", css); self.assertIn("--body:'Figtree',system-ui,sans-serif", css); self.assertIn("--label:'DM Mono',ui-monospace,monospace", css)
        only, _ = IR.transplant(PAGE, composition(type={'label': 'space-mono'}), IMAGES); css = only[only.index('<style id="ir-face-css">'):]; self.assertIn("--label:'Space Mono'", css[:css.index('</style>')]); self.assertNotIn('--display:', css[:css.index('</style>')])
        self.assertNotIn('ir-face', IR.transplant(PAGE, composition(), IMAGES)[0].replace('id="ir-css"', ''), 'a composition that chooses no face loads none')

    def test_set_type_has_its_manners_on_the_whole_page(self):
        for rule in ('h1,h2,h3{text-wrap:balance}', 'p,li{text-wrap:pretty}', 'font-variant-numeric:tabular-nums'): self.assertIn(rule, IR.CSS)

    def test_the_composer_is_offered_the_system_and_its_answer_becomes_the_composition(self):
        text, _ = COMPOSE.brief(copy.deepcopy(BASE)); self.assertIn('TEXT FACES ("body_face")', text); self.assertIn('LABEL FACES ("label_face")', text); self.assertIn('quiet luxury restaurant', text)
        props = COMPOSE.TOOL['input_schema']['properties']; self.assertEqual(props['body_face']['enum'], ['page'] + [f['id'] for f in FACES.of_role('body')]); self.assertEqual(props['label_face']['enum'], ['page'] + [f['id'] for f in FACES.of_role('label')])
        ir = COMPOSE._to_ir({'concept': 'x', 'rows': ['auto'], 'nodes': [], 'typeface': 'young-serif', 'body_face': 'figtree', 'label_face': 'dm-mono'})
        self.assertEqual(ir['hero']['face'], {'id': 'young-serif'}); self.assertEqual(ir['hero']['type'], {'body': 'figtree', 'label': 'dm-mono'})
        self.assertNotIn('type', COMPOSE._to_ir({'concept': 'x', 'rows': ['auto'], 'nodes': [], 'body_face': 'page', 'label_face': ''})['hero'])


class Atmosphere(unittest.TestCase):
    """A picture commissioned for the page is not a photograph of the business: it may be the ground of the first screen,
    which is how the template uses it, and nothing else."""
    def commissioned(self):
        content = copy.deepcopy(BASE); content['media']['hero.picture']['gen'] = True; return content

    def test_it_may_be_the_backdrop_and_nothing_else(self):
        content = self.commissioned(); ir = composition(content, height='screen')
        ir['hero']['nodes'].insert(0, {'id': 'bg', 't': 'media', 'src': 'hero.picture', 'bleed': 'full', 'scrim': True, 'at': {'col': [1, 13], 'row': [1, len(ir['hero']['rows']) + 1], 'z': 0}})
        self.assertEqual(V.validate(ir, content), [])
        framed = composition(content); framed['hero']['nodes'].append({'id': 'pic', 't': 'media', 'src': 'hero.picture', 'ratio': '4/3', 'at': {'col': [9, 13], 'row': [1, len(framed['hero']['rows']) + 1], 'z': 0}})
        for n in framed['hero']['nodes'][:-1]: n['at'] = dict(n['at'], col=[1, 8])
        found = V.validate(framed, content); self.assertEqual([e['code'] for e in found], ['IR065']); self.assertIn('only be the backdrop', found[0]['message'])

    def test_the_composer_is_told_so(self):
        text, offered = COMPOSE.brief(self.commissioned()); self.assertIn('hero.picture', [a for a, _ in offered]); self.assertIn('ONLY be the BACKDROP', text); self.assertIn('not a photograph of the business', text)


if __name__ == '__main__': unittest.main()
