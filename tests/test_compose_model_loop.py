"""The loop around the model that composes a hero: compose, correct once with the validator's reasons, look at the
render and revise once. The model here is a stand-in function — no network — so what is tested is what the loop does
with a good answer, a bad one, a malformed one and a worse revision."""
import io, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'compose'))
import compose as COMPOSE
import content as CONTENT
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


def answer(**changes):
    """A valid flat tool answer for the sample page."""
    nodes = []
    if 'hero.category' in BASE['text']: nodes.append({'id': 'cat', 't': 'text', 'src': 'hero.category', 'as': 'label', 'at': {'col': [1, 7], 'row': 1}})
    if 'hero.fact' in BASE['text']: nodes.append({'id': 'fact', 't': 'text', 'src': 'hero.fact', 'as': 'label', 'at': {'col': [8, 13], 'row': 1}})
    nodes.append({'id': 'h1', 't': 'text', 'src': 'hero.h1', 'as': 'h1', 'size': 'xxl', 'measure': 10, 'at': {'col': [1, 8], 'row': 2}})
    nodes.append({'id': 'pic', 't': 'media', 'src': 'hero.picture', 'fit': 'cover', 'ratio': '4/3', 'at': {'col': [8, 13], 'row': [2, 5], 'z': 0}})
    nodes.append({'id': 'lede', 't': 'text', 'src': 'hero.lede', 'as': 'lede', 'at': {'col': [1, 7], 'row': 3}})
    nodes.append({'id': 'go', 't': 'actions', 'src': sorted(BASE['actions']), 'at': {'col': [1, 7], 'row': 4}})
    doc = {'concept': 'The room on the right, the words on the left.', 'surface': 'paper', 'height': 'screen', 'rows': ['auto', '1fr', 'auto', 'auto'], 'gap': 'md',
           'nodes': nodes, 'phone_order': [n['id'] for n in nodes]}
    doc.update(changes); return doc


class Model:
    """Answers in order; remembers what it was shown."""
    def __init__(self, *answers): self.answers = list(answers); self.seen = []
    def __call__(self, system, content, tool, model=None, max_tokens=None):
        self.seen.append(content); return self.answers.pop(0) if self.answers else None
    def text(self, call): return '\n'.join(block['text'] for block in self.seen[call] if block.get('type') == 'text')


class Loop(unittest.TestCase):
    def test_a_good_first_answer_is_the_composition(self):
        model = Model(answer())
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=model)
        self.assertTrue(result['drawn']); self.assertEqual(result['attempts'], 1)
        self.assertEqual(V.validate(result['ir'], BASE), []); self.assertEqual(result['ir']['note'], 'The room on the right, the words on the left.')
        self.assertEqual(len(model.seen), 1)

    def test_a_refused_answer_goes_back_once_with_the_validators_reasons(self):
        bad = answer(); next(n for n in bad['nodes'] if n['id'] == 'lede')['text'] = 'The best table in town'
        model = Model(bad, answer(concept='Second try.'))
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=model)
        self.assertTrue(result['drawn']); self.assertEqual(result['attempts'], 2); self.assertEqual(result['ir']['note'], 'Second try.')
        self.assertIn('REFUSED', model.text(1)); self.assertIn('IR011', model.text(1))
        self.assertEqual([bool(step['errors']) for step in result['log']], [True, False]); self.assertIn('refused', result['log'][0])

    def test_two_refusals_mean_no_composition_and_no_third_call(self):
        bad = answer(); bad['nodes'] = [n for n in bad['nodes'] if n['id'] != 'go']
        model = Model(bad, json.loads(json.dumps(bad)), answer())
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=model)
        self.assertFalse(result['drawn']); self.assertIsNone(result['ir']); self.assertEqual(len(model.seen), 2)

    def test_no_answer_at_all_is_not_a_composition(self):
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=Model(None))
        self.assertFalse(result['drawn']); self.assertEqual(result['attempts'], 1)

    def test_lists_handed_back_as_json_text_are_read(self):
        doc = answer(); doc['rows'] = json.dumps(doc['rows']); doc['nodes'] = json.dumps(doc['nodes']); doc['phone_order'] = json.dumps(doc['phone_order'])
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=Model(doc))
        self.assertTrue(result['drawn'], result['log'])

    def test_broken_text_where_a_list_belongs_is_refused_not_guessed(self):
        doc = answer(); doc['nodes'] = '\n<parameter name="surface">paper'
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=Model(doc, None))
        self.assertFalse(result['drawn']); self.assertTrue(any('IR001' in e for e in result['log'][0]['errors']))

    def test_wishes_are_collected_and_never_drawn(self):
        doc = answer(wishes=[{'intent': 'the accent word in the brand green', 'missing': 'per-word colour'}, {'intent': '', 'missing': ''}])
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=Model(doc))
        self.assertEqual(result['wishes'], [{'intent': 'the accent word in the brand green', 'missing': 'per-word colour'}])
        self.assertNotIn('wishes', result['ir']); self.assertNotIn('unsupported', result['ir'])


class Review(unittest.TestCase):
    def setUp(self):
        from PIL import Image
        self.temp = tempfile.mkdtemp(); self.page = os.path.join(self.temp, 'page.html'); Path(self.page).write_text(PAGE)
        self.shot = os.path.join(self.temp, 'shot.png'); Image.new('RGB', (64, 40), '#ccc').save(self.shot)
        self.shots = patch.object(COMPOSE, 'hero_shots', lambda path: (self.shot, self.shot)); self.shots.start()
        self.readings = []   # what the contract "measures", call by call: the template's page first, then each drawn candidate
        self.contract = patch.object(COMPOSE, 'measured', lambda path: dict(self.readings.pop(0)) if self.readings else {}); self.contract.start()
    def tearDown(self): self.shots.stop(); self.contract.stop(); shutil.rmtree(self.temp, ignore_errors=True)

    def test_the_model_sees_its_render_and_a_valid_revision_replaces_the_first(self):
        model = Model(answer(), answer(concept='Revised: the picture taller.'))
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=model)
        self.assertEqual([s['stage'] for s in result['log']], ['compose', 'revise']); self.assertEqual(result['ir']['note'], 'Revised: the picture taller.')
        self.assertIn('AS DRAWN', model.text(1)); self.assertEqual(sum(1 for b in model.seen[1] if b.get('type') == 'image'), sum(1 for b in model.seen[0] if b.get('type') == 'image') + 2)
        self.assertEqual(sorted(os.listdir(self.temp)), ['page.html', 'shot.png'], 'the page drawn for the look is removed again')

    def test_a_revision_that_does_not_validate_is_dropped_and_the_valid_one_stands(self):
        worse = answer(concept='Worse.'); next(n for n in worse['nodes'] if n['id'] == 'h1')['at'] = {'col': [1, 12], 'row': 2}   # onto the picture, no plate
        model = Model(answer(concept='First.'), worse)
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=model)
        self.assertTrue(result['drawn']); self.assertEqual(result['ir']['note'], 'First.')
        self.assertTrue(result['log'][-1]['errors'])

    def test_a_failed_look_does_not_lose_the_composition(self):
        with patch.object(COMPOSE, 'hero_shots', side_effect=[(self.shot, self.shot), RuntimeError('no browser')]):
            result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=Model(answer(concept='Kept.')))
        self.assertTrue(result['drawn']); self.assertEqual(result['ir']['note'], 'Kept.'); self.assertIn('review skipped', result['log'][-1]['errors'][0])


    def test_what_the_render_measures_goes_back_to_the_model_and_a_fixed_revision_ships(self):
        self.readings = [{}, {'h1-lines': '4 lines'}, {}]
        model = Model(answer(concept='First.'), answer(concept='Shorter measure, three lines.'))
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=model)
        self.assertIn('MEASURED ON THIS RENDER', model.text(1)); self.assertIn('h1-lines: 4 lines', model.text(1))
        self.assertTrue(result['drawn']); self.assertEqual(result['ir']['note'], 'Shorter measure, three lines.'); self.assertEqual(result['measured'], {})

    def test_a_composition_that_still_breaks_the_page_is_not_shipped(self):
        self.readings = [{}, {'desktop-no-overflow': 'h1 runs past the screen'}, {'desktop-no-overflow': 'h1 runs past the screen'}]
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=Model(answer(), answer(concept='Still too wide.')))
        self.assertFalse(result['drawn']); self.assertIsNone(result['ir']); self.assertEqual(result['log'][-1]['stage'], 'refuse')
        self.assertIn('desktop-no-overflow', result['log'][-1]['errors'][0])

    def test_a_revision_that_measures_worse_is_dropped(self):
        self.readings = [{}, {}, {'h1-lines': '4 lines'}]
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=Model(answer(concept='Clean.'), answer(concept='Bigger, and now four lines.')))
        self.assertTrue(result['drawn']); self.assertEqual(result['ir']['note'], 'Clean.'); self.assertIn('measured worse', result['log'][-1]['errors'][0])

    def test_what_the_templates_own_page_already_breaks_is_not_blamed_on_the_composition(self):
        self.readings = [{'mobile-contrast': 'a footer link'}, {'mobile-contrast': 'a footer link'}, {'mobile-contrast': 'a footer link'}]
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=Model(answer(), answer()))
        self.assertTrue(result['drawn']); self.assertEqual(result['measured'], {})

    def test_without_a_look_the_render_is_still_measured(self):
        self.readings = [{}, {'h1-lines': '5 lines'}]
        model = Model(answer())
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, review=False, ask=model)
        self.assertEqual(len(model.seen), 1); self.assertFalse(result['drawn'], 'a headline measured at five lines is not shipped even when no revision was asked for')


class Brief(unittest.TestCase):
    def test_the_brief_names_what_may_be_placed_and_the_tool_has_no_field_for_words(self):
        text, pictures = COMPOSE.brief(BASE)
        for address in list(BASE['text']) + list(BASE['actions']): self.assertIn(address, text)
        self.assertIn(BASE['text']['hero.lede'], text)
        fields = json.dumps(COMPOSE.TOOL['input_schema'])
        for forbidden in ('"text":', '"href"', '"label":', '"html"', '"content"'): self.assertNotIn(forbidden, fields)

    def test_only_real_unused_pictures_of_a_useful_size_are_offered(self):
        content = json.loads(json.dumps(BASE))
        content['media'] = {'hero.picture': dict(BASE['media']['hero.picture']), 'img:tiny': {'src': 'data:a', 'w': 300, 'h': 200, 'shot': False},
                            'img:made': {'src': 'data:b', 'w': 1600, 'h': 1000, 'gen': True, 'shot': False}, 'img:taken': {'src': 'data:c', 'w': 1600, 'h': 1000, 'shot': False},
                            'img:free': {'src': 'data:d', 'w': 1500, 'h': 2000, 'shot': False}, 'img:nosize': {'src': 'data:e', 'w': None, 'h': None, 'shot': False}}
        content['used_elsewhere'] = ['img:taken']
        offered = [address for address, _ in COMPOSE.offered_pictures(content)]
        self.assertEqual(offered, ['hero.picture', 'img:free'])

    def test_reference_principles_come_from_the_design_dna_when_a_job_is_given(self):
        with tempfile.TemporaryDirectory() as job:
            Path(job, 'direction.json').write_text(json.dumps({'kind': 'place', 'mode': 'light'})); Path(job, 'images.json').write_text(json.dumps(IMAGES))
            text, _ = COMPOSE.brief(BASE, job)
        self.assertIn('REFERENCE PRINCIPLES', text); self.assertIn('Threshold', text)


if __name__ == '__main__':
    unittest.main()
