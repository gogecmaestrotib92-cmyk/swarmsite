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
    def test_the_composer_of_the_first_screen_sets_a_direction_for_the_rest_of_the_page(self):
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=Model(answer(page_direction='  Hollow numerals;\n dark pauses. ')))
        self.assertEqual(result['direction'], 'Hollow numerals; dark pauses.', 'words for the other composers: kept beside the composition, never in it')
        self.assertNotIn('direction', result['ir']); self.assertNotIn('page_direction', json.dumps(result['ir'])); self.assertEqual(V.validate(result['ir'], BASE), [])
        self.assertIsNone(COMPOSE.compose(PAGE, IMAGES, review=False, ask=Model(answer()))['direction']); self.assertIsNone(COMPOSE.compose(PAGE, IMAGES, review=False, ask=Model(answer(rows=['bad'], page_direction='x')))['direction'])
        self.assertEqual(COMPOSE._directed(None), []); self.assertIn("THE PAGE'S DIRECTION", COMPOSE._directed('Loud type.')[0]['text'])

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
        self.seen = []   # what the browser "measures" of the first screen, call by call; nothing by default
        self.browser = patch.object(COMPOSE, 'measure_hero', lambda path: dict(self.seen.pop(0)) if self.seen else {}); self.browser.start()
    def tearDown(self): self.shots.stop(); self.contract.stop(); self.browser.stop(); shutil.rmtree(self.temp, ignore_errors=True)

    def test_the_headline_is_measured_in_a_browser_and_sized_from_that(self):
        h1 = lambda ir: next(n for n in ir['hero']['nodes'] if n.get('as') == 'h1')
        estimate = V.headline_em(h1(COMPOSE._to_ir(answer())), BASE, *V.face_of({}, BASE))
        self.seen = [{}, {'fit': {'line': round(estimate * 1.08, 3), 'word': round(estimate * 1.08, 3)}}]   # the template's page, then the candidate
        told = answer(); next(n for n in told['nodes'] if n['id'] == 'h1')['fit'] = {'line': 1, 'word': 1}   # a model does not get to state a measurement
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, review=False, ask=Model(told))
        self.assertTrue(result['drawn'], result['log']); self.assertEqual(h1(result['ir'])['fit'], {'line': round(estimate * 1.08, 3), 'word': round(estimate * 1.08, 3)})
        page, _ = IR.transplant(PAGE, result['ir'], IMAGES)
        self.assertIn(f'--fit:{round(estimate * 1.08, 3) * IR.MEASURED_SLACK:.3f}', page)

    def test_a_measurement_that_cannot_be_of_this_headline_is_not_used(self):
        self.seen = [{}, {'fit': {'line': 90, 'word': 90}}]
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, review=False, ask=Model(answer()))
        self.assertTrue(result['drawn']); self.assertNotIn('fit', next(n for n in result['ir']['hero']['nodes'] if n.get('as') == 'h1'))

    def test_a_line_that_does_not_stay_on_one_line_goes_back_and_is_not_shipped_if_it_stays_broken(self):
        wrapped = {'desktop': {'wrapped': [{'line': 2, 'text': 'Beograd slavi', 'rows': 2, 'over': 0}], 'actions_bottom': 700, 'fold': 900}}
        self.seen = [{}, {}, dict(wrapped), {}, dict(wrapped)]   # template · fit · look · fit of the revision · look at the revision
        model = Model(answer(concept='First.'), answer(concept='Second.'))
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=model)
        self.assertIn('desktop-hero-line-wrap', model.text(1)); self.assertIn('Beograd slavi', model.text(1))
        self.assertFalse(result['drawn']); self.assertIn('desktop-hero-line-wrap', result['log'][-1]['errors'][0])

    def test_a_picture_the_fold_cuts_through_is_reported_with_its_numbers(self):
        found = COMPOSE.hero_findings({'desktop': {'wrapped': [], 'fold': 900, 'actions_bottom': 700, 'pictures': [{'id': 'report', 'top': 760, 'bottom': 1100}, {'id': 'whole', 'top': 200, 'bottom': 880}]}})
        self.assertEqual(list(found), ['hero-picture-cut-by-fold']); self.assertIn('"report" runs from 760 to 1100 px', found['hero-picture-cut-by-fold']); self.assertIn('59%', found['hero-picture-cut-by-fold'])
        self.assertEqual(COMPOSE.hero_findings({'desktop': {'fold': 900, 'pictures': [{'id': 'a', 'top': 300, 'bottom': 960}]}}), {}, 'a tenth under the fold is a picture that invites the scroll')
        self.assertEqual(COMPOSE.hero_findings({'desktop': {'fold': 900, 'pictures': [{'id': 'a', 'top': 980, 'bottom': 1500}]}}), {}, 'a picture that starts under the fold is simply the next thing down the page')
        self.assertEqual(COMPOSE.hero_findings({'desktop': {'fold': 900, 'pictures': [{'id': 'a'}, 'junk']}}), {})
        cut = {'desktop': {'wrapped': [], 'fold': 900, 'actions_bottom': 700, 'pictures': [{'id': 'pic', 'top': 700, 'bottom': 1200}]}}
        self.seen = [{}, {}, dict(cut), {}, {}]   # template · fit · look (cut) · fit of the revision · look (clean)
        model = Model(answer(concept='Picture under the words.'), answer(concept='Picture beside the words.'))
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=model)
        self.assertIn('hero-picture-cut-by-fold', model.text(1)); self.assertIn('ALSO MEASURED', model.text(1)); self.assertEqual(result['ir']['note'], 'Picture beside the words.')
        self.seen = [{}, {}, {}, {}, dict(cut)]   # a revision that pushes the picture through the fold is worse than the one it would replace
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=Model(answer(concept='Clean.'), answer(concept='Now cut.')))
        self.assertEqual(result['ir']['note'], 'Clean.'); self.assertTrue(result['drawn'])

    def test_buttons_under_the_fold_are_reported_but_do_not_refuse_the_composition(self):
        low = {'desktop': {'wrapped': [], 'actions_bottom': 960, 'fold': 900}}
        self.seen = [{}, {}, dict(low), {}, {}]
        model = Model(answer(concept='First.'), answer(concept='Buttons up.'))
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=model)
        self.assertIn('hero-actions-under-fold', model.text(1)); self.assertIn('960 px', model.text(1)); self.assertEqual(result['ir']['note'], 'Buttons up.')
        self.seen = [dict(low), {}, dict(low)]   # the template's own buttons are under the fold too: not blamed on the composition
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, review=False, ask=Model(answer()))
        self.assertEqual(result['measured'], {})

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

    def test_what_must_be_fixed_is_told_apart_from_what_is_the_art_directors_to_weigh(self):
        self.readings = [{}, {'h1-lines': '4 lines', 'desktop-first-screen-visual': 'no visual in the first screen'}, {}]
        model = Model(answer(), answer())
        COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=model)
        blocks = [b['text'] for b in model.seen[1] if b.get('type') == 'text']
        must = next(t for t in blocks if t.startswith('MEASURED ON THIS RENDER')); also = next(t for t in blocks if t.startswith('ALSO MEASURED'))
        self.assertIn('h1-lines', must); self.assertNotIn('first-screen-visual', must); self.assertIn('not shipped', must)
        self.assertIn('first-screen-visual', also); self.assertIn('never place a document', also)

    def test_leaving_the_picture_out_is_a_choice_not_a_defect(self):
        typed = answer(concept='Type alone.'); typed['nodes'] = [n for n in typed['nodes'] if n['id'] != 'pic']; typed['phone_order'] = [n['id'] for n in typed['nodes']]
        self.readings = [{}, {}, {'desktop-first-screen-visual': 'no visual in the first screen', 'mobile-first-screen-visual': 'no visual in the first screen'}]
        result = COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=Model(answer(concept='With the picture.'), typed))
        self.assertTrue(result['drawn']); self.assertEqual(result['ir']['note'], 'Type alone.', 'a revision that drops a weak picture is not "measured worse"')

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


class Typeface(unittest.TestCase):
    def job(self, **brand):
        folder = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, folder, True)
        Path(folder, 'direction.json').write_text(json.dumps({'kind': 'place', 'mode': 'light', 'brand': brand})); Path(folder, 'images.json').write_text(json.dumps(IMAGES))
        return folder

    def test_a_chosen_face_becomes_the_pages_face_and_page_means_the_pages_own(self):
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=Model(answer(typeface='fraunces', weight=300, case='none')))
        self.assertTrue(result['drawn'], result['log']); self.assertEqual(result['ir']['hero']['face'], {'id': 'fraunces', 'weight': 300, 'case': 'none'})
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=Model(answer(typeface='page', weight=300)))
        self.assertTrue(result['drawn']); self.assertNotIn('face', result['ir']['hero'])

    def test_a_face_outside_the_registry_is_refused_with_the_list(self):
        model = Model(answer(typeface='Suisse Intl'), answer())
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=model)
        self.assertIn('IR050', model.text(1)); self.assertIn('fraunces', model.text(1)); self.assertTrue(result['drawn'])

    def test_the_brands_own_face_is_named_in_the_brief_and_kept(self):
        job = self.job(font_hint=BASE['page']['display'].upper(), keep_font=True)
        model = Model(answer(typeface='anton'), answer())
        result = COMPOSE.compose(PAGE, IMAGES, job_dir=job, review=False, ask=model)
        self.assertIn("the brand's own face", model.text(0)); self.assertNotIn('- fraunces:', model.text(0))
        self.assertIn('IR051', model.text(1)); self.assertTrue(result['drawn']); self.assertNotIn('face', result['ir']['hero'])

    def test_a_font_the_page_does_not_actually_use_locks_nothing(self):
        for brand in ({'font_hint': 'Inter', 'keep_font': True}, {'font_hint': BASE['page']['display'], 'keep_font': False}, {}):
            model = Model(answer(typeface='fraunces'))
            result = COMPOSE.compose(PAGE, IMAGES, job_dir=self.job(**brand), review=False, ask=model)
            self.assertTrue(result['drawn'], brand); self.assertEqual(result['ir']['hero']['face'], {'id': 'fraunces'}); self.assertIn('- fraunces: Fraunces', model.text(0))

    def test_the_registry_is_offered_with_each_faces_voice_and_measured_width(self):
        text, _ = COMPOSE.brief(BASE)
        for f in V.FACES.of_role('display'): self.assertIn(f'- {f["id"]}: {f["family"]}', text); self.assertIn(f['voice'], text)
        for f in V.FACES.of_role('body') + V.FACES.of_role('label'): self.assertIn(f'{f["id"]} ({f["family"]}', text)
        self.assertIn('PAIRINGS', text); self.assertIn('SEEN EVERYWHERE', text); self.assertNotIn('- inter: Inter', text, 'a text face is not offered for headings')
        self.assertIn(f'the page is set in {BASE["page"]["display"]} now', text)
        offered = COMPOSE.TOOL['input_schema']['properties']['typeface']['enum']
        self.assertEqual(offered, ['page'] + [f['id'] for f in V.FACES.of_role('display')], 'the tool offers the registry\'s display faces and nothing else')

    def test_a_face_that_breaks_a_section_further_down_is_measured_on_the_whole_page(self):
        from PIL import Image
        temp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, temp, True); page = os.path.join(temp, 'page.html'); Path(page).write_text(PAGE)
        shot = os.path.join(temp, 'shot.png'); Image.new('RGB', (64, 40), '#ccc').save(shot)
        readings = [{}, {'mobile-no-overflow': 'a card heading runs past the screen'}, {}]
        with patch.object(COMPOSE, 'hero_shots', lambda path: (shot, shot)), patch.object(COMPOSE, 'measured', lambda path: dict(readings.pop(0))), patch.object(COMPOSE, 'measure_hero', lambda path: {}):
            model = Model(answer(typeface='unbounded', concept='Wide and loud.'), answer(typeface='fraunces', concept='Quieter.'))
            result = COMPOSE.compose(PAGE, IMAGES, page_path=page, ask=model)
        self.assertIn('mobile-no-overflow: a card heading runs past the screen', model.text(1)); self.assertEqual(result['ir']['note'], 'Quieter.')


class Studio:
    """A stand-in for the model when three concepts are asked for at once: it answers by the lead it was given (the three
    calls run side by side, in no fixed order), chooses as the creative director, and revises."""
    LEADS = {'A': 'CONCEPT — type leads. The headline', 'B': ('CONCEPT — the picture leads', 'CONCEPT — type leads again'), 'C': 'CONCEPT — the one neither'}
    def __init__(self, drafts, verdict=None, revision=None, corrections=None):
        self.drafts, self.verdict, self.revision, self.corrections = drafts, verdict, revision, corrections or {}; self.calls = []
    def __call__(self, system, content, tool, model=None, max_tokens=None):
        text = '\n'.join(block['text'] for block in content if block.get('type') == 'text')
        label = next((l for l, marks in self.LEADS.items() if any(m in text for m in ([marks] if isinstance(marks, str) else marks))), None)
        kind = 'jury' if tool['name'] == 'choose_concept' else 'revise' if 'YOUR COMPOSITION, AS DRAWN' in text else 'correct' if 'WAS REFUSED' in text else 'compose'
        self.calls.append({'kind': kind, 'label': label, 'text': text, 'tool': tool, 'images': sum(1 for b in content if b.get('type') == 'image')})
        if kind == 'jury': return self.verdict
        if kind == 'revise': return self.revision
        return (self.corrections if kind == 'correct' else self.drafts).get(label)
    def of(self, kind): return [c for c in self.calls if c['kind'] == kind]


def concept(label, **changes):
    """A valid answer that can be told apart on the drawn page: A is set mega, B xxl, C xl."""
    doc = answer(**{'concept': f'Concept {label}.', **changes}); next(n for n in doc['nodes'] if n['id'] == 'h1')['size'] = {'A': 'mega', 'B': 'xxl', 'C': 'xl'}[label]
    return doc
MARK = {'A': IR.SIZE['mega'], 'B': IR.SIZE['xxl'], 'C': IR.SIZE['xl']}   # what each concept leaves in the page it is drawn into


class ThreeConcepts(unittest.TestCase):
    def setUp(self):
        from PIL import Image
        self.temp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.temp, True); self.page = os.path.join(self.temp, 'page.html'); Path(self.page).write_text(PAGE)
        shot = os.path.join(self.temp, 'shot.png'); Image.new('RGB', (64, 40), '#ccc').save(shot)
        self.breaks = {}   # label → what the contract finds on the page that concept is drawn into
        def graded(path):
            html = Path(path).read_text()
            return dict(next((found for label, found in self.breaks.items() if f'--ir-size:{MARK[label]}' in html), {}))
        for target, stand_in in (('hero_shots', lambda path: (shot, shot)), ('measured', graded), ('measure_hero', lambda path: {})):
            patcher = patch.object(COMPOSE, target, stand_in); patcher.start(); self.addCleanup(patcher.stop)
        self.drafts = {label: concept(label) for label in 'ABC'}
    def run_studio(self, studio, **kw): return COMPOSE.compose(PAGE, IMAGES, page_path=self.page, ask=studio, concepts=3, **kw)

    def test_three_leads_are_drawn_and_the_creative_director_chooses_among_the_renders(self):
        studio = Studio(self.drafts, verdict={'choice': 'B', 'reason': 'The room is what people come for.', 'improve': 'Give the headline one more column.'}, revision=concept('B', concept='Concept B, wider headline.'))
        result = self.run_studio(studio)
        self.assertEqual(sorted(c['label'] for c in studio.of('compose')), ['A', 'B', 'C'], 'each concept is asked for with its own lead')
        jury = studio.of('jury'); self.assertEqual(len(jury), 1)
        for label in 'ABC': self.assertIn(f'CONCEPT {label} — Concept {label}.', jury[0]['text'])
        self.assertEqual(jury[0]['tool']['input_schema']['properties']['choice']['enum'], ['A', 'B', 'C']); self.assertEqual(jury[0]['images'], 6, 'every concept is shown as drawn, at 1440 and on a phone')
        self.assertEqual(result['chosen'], 'B'); self.assertEqual(result['verdict']['reason'], 'The room is what people come for.')
        revise = studio.of('revise'); self.assertEqual(len(revise), 1)
        self.assertIn('The studio chose this one of its concepts: The room is what people come for. Before it ships: Give the headline one more column.', revise[0]['text'])
        self.assertTrue(result['drawn']); self.assertEqual(result['ir']['note'], 'Concept B, wider headline.')
        self.assertEqual([c['label'] for c in result['concepts']], ['A', 'B', 'C']); self.assertEqual(result['attempts'], 5)
        self.assertEqual(sorted(os.listdir(self.temp)), ['page.html', 'shot.png'], 'every page drawn for the look is removed again')

    def test_a_concept_that_breaks_the_page_is_not_put_before_the_creative_director(self):
        self.breaks = {'A': {'desktop-no-overflow': 'the headline runs past the screen'}}
        studio = Studio(self.drafts, verdict={'choice': 'C', 'reason': 'Unexpected and clean.'}, revision=concept('C'))
        result = self.run_studio(studio)
        jury = studio.of('jury')[0]
        self.assertEqual(jury['tool']['input_schema']['properties']['choice']['enum'], ['B', 'C']); self.assertNotIn('CONCEPT A', jury['text'])
        self.assertEqual(result['chosen'], 'C'); self.assertEqual(next(c for c in result['concepts'] if c['label'] == 'A')['measured'], {'desktop-no-overflow': 'the headline runs past the screen'})

    def test_when_nobody_chooses_the_least_broken_stands_and_a_is_before_b(self):
        self.breaks = {'A': {'h2-short': 'a long heading further down'}}
        for verdict in (None, {'choice': 'D', 'reason': 'x'}, {'reason': 'no choice'}):
            studio = Studio(self.drafts, verdict=verdict, revision=None)
            result = self.run_studio(studio)
            self.assertEqual(result['chosen'], 'B', 'B and C are clean, A has a finding: B is first of the clean ones'); self.assertTrue(result['drawn'])
            self.assertIn('no valid choice', next(s for s in result['log'] if s['stage'] == 'jury')['errors'][0])

    def test_when_every_concept_breaks_the_page_the_least_broken_gets_one_revision_or_nothing_ships(self):
        self.breaks = {label: {'desktop-no-overflow': 'too wide'} for label in 'ABC'}; self.breaks['C']['h1-lines'] = '4 lines'
        studio = Studio(self.drafts, verdict={'choice': 'A', 'reason': 'Fixable.'}, revision=concept('A'))
        result = self.run_studio(studio)
        self.assertEqual(studio.of('jury')[0]['tool']['input_schema']['properties']['choice']['enum'], ['A', 'B', 'C'], 'with nothing sound, all are shown and the break is named')
        self.assertIn('fix them, or it is not shipped', studio.of('jury')[0]['text'])
        self.assertFalse(result['drawn']); self.assertEqual(result['log'][-1]['stage'], 'refuse')

    def test_one_valid_draft_needs_no_choice(self):
        broken = concept('A'); broken['nodes'] = [n for n in broken['nodes'] if n['id'] != 'go']
        studio = Studio({'A': broken, 'B': concept('B'), 'C': None}, corrections={'A': json.loads(json.dumps(broken))}, revision=concept('B'))
        result = self.run_studio(studio)
        self.assertEqual(studio.of('jury'), []); self.assertEqual(result['chosen'], 'B'); self.assertTrue(result['drawn'])
        self.assertEqual(sorted(c['label'] for c in studio.of('correct')), ['A'], 'a refused draft is corrected once, under its own lead')
        self.assertIn(Studio.LEADS['A'], studio.of('correct')[0]['text'])

    def test_without_a_picture_worth_placing_the_second_concept_is_a_second_voice(self):
        with patch.object(COMPOSE, 'offered_pictures', lambda content, limit=7: []):
            typed = {}
            for label in 'ABC':
                doc = concept(label); doc['nodes'] = [n for n in doc['nodes'] if n['id'] != 'pic']; doc['phone_order'] = [n['id'] for n in doc['nodes']]; typed[label] = doc
            studio = Studio(typed, verdict={'choice': 'A', 'reason': 'Quiet and sure.'}, revision=None)
            self.run_studio(studio)
        texts = ' '.join(c['text'] for c in studio.of('compose'))
        self.assertIn('type leads again, in another voice', texts); self.assertNotIn('the picture leads', texts)

    def test_without_a_page_to_draw_on_there_is_one_concept(self):
        model = Model(answer())
        result = COMPOSE.compose(PAGE, IMAGES, review=False, ask=model, concepts=3)
        self.assertEqual(len(model.seen), 1); self.assertTrue(result['drawn']); self.assertNotIn('concepts', result)


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
