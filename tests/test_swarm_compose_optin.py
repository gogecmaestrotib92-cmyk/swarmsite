"""The composed first screen in the production loop: off unless a job or the deployment asks, one more candidate when on.
It replaces the winning page only if it scores at least as high and breaks nothing the winner kept; otherwise every
file of the winner is put back exactly. No model, no browser: the composer, the contract and the critic are stand-ins."""
import json, os, shutil, sys, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'swarm')); sys.path.insert(0, str(ROOT / 'lib' / 'compose'))
import run
import compose as COMPOSE
import compose_lists as COMPOSE_LISTS
import compose_pictures as COMPOSE_PICTURES
import compose_words as COMPOSE_WORDS
import render_ir as IR

PAGE = ('<html><head><style>:root{--paper:#ffffff;--display:\'Geist\',sans-serif;--container:1300px;--frame:40px}</style></head><body>'
        '<section class="sec hero" id="top"><div class="cat"><span class="lab">A label</span></div><h1 class="h1">Four words <em>right</em> here</h1>'
        '<p class="lede">One sentence of lede.</p><div class="ctas"><a class="btn" href="https://example.test/go">Go <span class="ar">→</span></a></div></section>'
        '<section class="sec cards"><h2 class="h2">Below</h2></section>'
        '<section class="sec indexlist band-alt" id="what"><div class="wrap"><div class="gh"><span class="lab">What</span><h2 class="h2">Four things</h2></div><ol class="index-list">'
        + ''.join(f'<li class="index-row"><span class="idx">0{n}</span><h3 class="h3">Thing {n}</h3><p>Body of thing {n}.</p></li>' for n in range(1, 5))
        + '</ol></div></section>'
        '<section class="sec story band-paper" id="room"><div class="wrap st"><div class="photo-caption"><span class="lab">The room</span><h2 class="h2">Where it happens</h2><p class="cap">One line about the room.</p></div>'
        '<figure class="st-v"><img src="data:image/png;base64,AAAA" alt="The room"></figure></div></section>'
        '<section class="sec ledger band-paper" id="prices"><div class="wrap two"><div class="ledger-intro"><span class="lab">Prices</span><h2 class="h2">What it costs</h2></div><div><ul class="rows">'
        + ''.join(f'<li><span class="ledger-item">Plan {n}</span><i></i><b>{n}0 €</b></li>' for n in range(1, 5)) + '</ul></div></div></section></body></html>')
WORDS_OK = {'ir': '0.2', 'note': 'A printed price list.', 'words': [{'section': 'prices', 'form': 'columns', 'title': 'xl'}]}
ROOM = [{'id': 'room', 'data': 'data:image/png;base64,AAAA', 'w': 1600, 'h': 1067}]   # images.json describes the picture of the "room" section
PICTURES_OK = {'ir': '0.2', 'note': 'The room runs off the edge.', 'pictures': [{'section': 'room', 'form': 'bleed', 'side': 'right', 'cols': 6}]}
LISTS_OK = {'ir': '0.2', 'note': 'Hollow numerals.', 'lists': [{'section': 'what', 'form': 'ledger', 'numerals': 'outline', 'head': 'sticky'}]}
IR_OK = {'ir': '0.2', 'note': 'Type alone, stepped.', 'hero': {'rows': ['auto', 'auto', 'auto', 'auto'], 'face': {'id': 'fraunces'}, 'nodes': [
    {'id': 'cat', 't': 'text', 'src': 'hero.category', 'as': 'label', 'at': {'col': [1, 7], 'row': 1}},
    {'id': 'h1', 't': 'text', 'src': 'hero.h1', 'as': 'h1', 'lines': [2, 2], 'indent': [0, 2], 'at': {'col': [1, 10], 'row': 2}},
    {'id': 'lede', 't': 'text', 'src': 'hero.lede', 'as': 'lede', 'at': {'col': [1, 7], 'row': 3}},
    {'id': 'go', 't': 'actions', 'src': ['hero.cta'], 'at': {'col': [1, 7], 'row': 4}}]}}


class Job(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.dir, True)
        self.out = os.path.join(self.dir, 'bp-x.html'); Path(self.out).write_text(PAGE, encoding='utf-8')
        Path(self.dir, 'images.json').write_text(json.dumps(ROOM)); Path(self.dir, 'direction.json').write_text(json.dumps({'kind': 'software'}))
        self.result = {'ir': json.loads(json.dumps(IR_OK)), 'drawn': True, 'attempts': 2, 'log': [{'stage': 'compose', 'errors': []}], 'wishes': [], 'measured': {}}
        self.asked = []
        def composed(*a, **k): self.asked.append(k); return self.result
        patcher = patch.object(COMPOSE, 'compose', composed); patcher.start(); self.addCleanup(patcher.stop)
        self.lists = {'doc': None, 'drawn': False, 'attempts': 0, 'log': [], 'measured': None}   # by default the lists composer returns nothing
        patcher = patch.object(COMPOSE_LISTS, 'compose', lambda *a, **k: self.lists); patcher.start(); self.addCleanup(patcher.stop)
        self.pictures = {'doc': None, 'drawn': False, 'attempts': 0, 'log': [], 'measured': None}   # and so does the pictures composer
        patcher = patch.object(COMPOSE_PICTURES, 'compose', lambda *a, **k: self.pictures); patcher.start(); self.addCleanup(patcher.stop)
        self.words = {'doc': None, 'drawn': False, 'attempts': 0, 'log': [], 'measured': None}   # and the composer of the sections that are words only
        patcher = patch.object(COMPOSE_WORDS, 'compose', lambda *a, **k: self.words); patcher.start(); self.addCleanup(patcher.stop)
    def brief(self, **fields): Path(self.dir, 'brief.json').write_text(json.dumps(fields))
    def record(self): return json.loads(Path(self.dir, 'composition.json').read_text())


class OptIn(Job):
    def test_a_page_is_recomposed_unless_the_job_or_the_deployment_says_no(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('SWARM_COMPOSE', None); os.environ.pop('LIVETEST', None)
            self.assertTrue(run.compose_wanted(self.dir), 'no brief at all: the ordinary path')
            for value in (None, 'true', 1, 'yes', 'false', 0):
                self.brief(compose=value, url='https://example.test/'); self.assertTrue(run.compose_wanted(self.dir), f'{value!r} is not a no')
            self.brief(compose=False); self.assertFalse(run.compose_wanted(self.dir), 'the job says no')
            with patch.dict(os.environ, {'SWARM_COMPOSE': '1'}): self.assertFalse(run.compose_wanted(self.dir), 'the job comes before the deployment')
            self.brief()
            with patch.dict(os.environ, {'SWARM_COMPOSE': '0'}):
                self.assertFalse(run.compose_wanted(self.dir), 'the deployment says no'); self.brief(compose=True); self.assertTrue(run.compose_wanted(self.dir), 'and a job can still ask')
            self.brief()
            with patch.dict(os.environ, {'LIVETEST': '1'}):
                self.assertFalse(run.compose_wanted(self.dir), 'under tests nothing calls a model unasked')
                with patch.dict(os.environ, {'SWARM_COMPOSE': '1'}): self.assertTrue(run.compose_wanted(self.dir))

    def test_the_loop_does_not_reach_the_composer_by_default(self):
        source = (ROOT / 'lib' / 'swarm' / 'run.py').read_text()
        call = source.index('= recompose(slug_dir, out, log,'); guard = source.rindex('if compose_wanted(slug_dir) and', 0, call)
        self.assertEqual(source.count('= recompose(slug_dir, out, log,'), 1); self.assertLess(call - guard, 200, 'the only call sits right under the opt-in check')
        self.assertNotIn('import compose', source.split('def compose_first_screen')[0], 'lib/compose is imported only inside the opt-in step')


class FirstScreen(Job):
    def test_a_drawn_composition_replaces_the_page_and_is_recorded(self):
        record = run.compose_first_screen(self.dir, self.out)
        page = Path(self.out).read_text(encoding='utf-8')
        self.assertTrue(record['drawn']); self.assertIn('class="sec hero ir"', page); self.assertIn("--display:'Fraunces'", page)
        self.assertIn('<section class="sec cards"><h2 class="h2">Below</h2></section>', page, 'the rest of the page is untouched')
        self.assertIn('<ol class="index-list">', page, 'a list nobody recomposed stays as the template drew it'); self.assertEqual(record['lists']['drawn'], False)
        self.assertEqual(self.record()['concept'], 'Type alone, stepped.'); self.assertEqual(self.record()['face'], {'id': 'fraunces'})
        self.assertEqual(self.asked[0]['concepts'], 3, 'in the loop three first screens are drawn and one is chosen'); self.assertEqual(self.asked[0]['page_path'], self.out)
        self.assertFalse(os.path.exists(self.out + '.composed'))

    def test_no_composition_leaves_the_page_byte_for_byte(self):
        self.result = {'ir': None, 'drawn': False, 'attempts': 2, 'log': [{'stage': 'refuse', 'errors': ['breaks the page']}], 'wishes': [], 'measured': None}
        record = run.compose_first_screen(self.dir, self.out)
        self.assertFalse(record['drawn']); self.assertEqual(Path(self.out).read_text(encoding='utf-8'), PAGE); self.assertFalse(self.record()['drawn'])

    def test_the_lists_are_composed_on_the_page_as_it_stands_after_the_first_screen(self):
        seen = []
        def lists(page, path, **kw): seen.append(page); return {'doc': json.loads(json.dumps(LISTS_OK)), 'drawn': True, 'attempts': 1, 'log': [], 'measured': {}}
        with patch.object(COMPOSE_LISTS, 'compose', lists): record = run.compose_first_screen(self.dir, self.out)
        page = Path(self.out).read_text(encoding='utf-8')
        self.assertIn('class="sec hero ir"', seen[0], 'the lists composer is shown the page with its composed first screen')
        self.assertTrue(record['drawn']); self.assertTrue(record['lists']['drawn']); self.assertEqual(record['lists']['forms'], {'what': 'ledger'})
        self.assertIn('lc lc-ledger', page); self.assertIn('class="sec hero ir"', page); self.assertEqual(page.count('<h3 class="h3 lc-title">Thing '), 4)
        self.assertEqual(self.record()['lists']['concept'], 'Hollow numerals.')

    def test_the_pictures_are_composed_last_on_the_page_as_it_then_stands(self):
        seen = []; self.lists = {'doc': json.loads(json.dumps(LISTS_OK)), 'drawn': True, 'attempts': 1, 'log': [], 'measured': {}}
        def pictures(page, path, images=None, **kw): seen.append((page, images)); return {'doc': json.loads(json.dumps(PICTURES_OK)), 'drawn': True, 'attempts': 2, 'log': [], 'measured': {}}
        with patch.object(COMPOSE_PICTURES, 'compose', pictures): record = run.compose_first_screen(self.dir, self.out)
        page = Path(self.out).read_text(encoding='utf-8')
        self.assertIn('class="sec hero ir"', seen[0][0]); self.assertIn('lc lc-ledger', seen[0][0], 'the pictures composer is shown the page with its first screen and lists composed')
        self.assertEqual(seen[0][1], ROOM, 'and the job\'s images, which say what each picture is')
        self.assertTrue(record['pictures']['drawn']); self.assertEqual(record['pictures']['forms'], {'room': 'bleed'}); self.assertEqual(self.record()['pictures']['concept'], 'The room runs off the edge.')
        self.assertIn('pc pc-f-bleed', page); self.assertIn('lc lc-ledger', page); self.assertIn('class="sec hero ir"', page); self.assertEqual(page.count('data:image/png;base64,AAAA'), 1)

    def test_pictures_alone_are_a_candidate_and_a_failing_or_refused_composer_leaves_the_rest(self):
        self.result = {'ir': None, 'drawn': False, 'attempts': 2, 'log': [], 'wishes': [], 'measured': None}
        self.pictures = {'doc': json.loads(json.dumps(PICTURES_OK)), 'drawn': True, 'attempts': 1, 'log': [], 'measured': {}}
        record = run.compose_first_screen(self.dir, self.out); self.assertTrue(record['drawn']); self.assertIn('pc pc-f-bleed', Path(self.out).read_text(encoding='utf-8'))
        Path(self.out).write_text(PAGE, encoding='utf-8')
        with patch.object(COMPOSE_PICTURES, 'compose', side_effect=RuntimeError('no browser')): record = run.compose_first_screen(self.dir, self.out)
        self.assertFalse(record['drawn']); self.assertIn('no browser', record['pictures']['error']); self.assertEqual(Path(self.out).read_text(encoding='utf-8'), PAGE)
        self.pictures = {'doc': {'ir': '0.2', 'pictures': [{'section': 'room', 'form': 'bleed', 'cols': 11}]}, 'drawn': True, 'attempts': 1, 'log': [], 'measured': {}}
        record = run.compose_first_screen(self.dir, self.out)
        self.assertFalse(record['pictures']['drawn'], 'a document the validator refuses is never drawn, whoever returned it'); self.assertEqual(Path(self.out).read_text(encoding='utf-8'), PAGE)

    def test_the_sections_of_words_are_composed_too_and_alone_are_a_candidate(self):
        self.result = {'ir': None, 'drawn': False, 'attempts': 2, 'log': [], 'wishes': [], 'measured': None}; seen = []
        def words(page, path, **kw): seen.append(page); return {'doc': json.loads(json.dumps(WORDS_OK)), 'drawn': True, 'attempts': 1, 'log': [], 'measured': {}}
        with patch.object(COMPOSE_WORDS, 'compose', words): record = run.compose_first_screen(self.dir, self.out)
        page = Path(self.out).read_text(encoding='utf-8'); self.assertTrue(record['drawn']); self.assertEqual(record['words']['forms'], {'prices': 'columns'}); self.assertIn('wc wc-f-columns wc-t-xl', page)
        self.assertEqual(page.count('<span class="ledger-item">Plan '), 4); self.assertEqual(self.record()['words']['concept'], 'A printed price list.')
        Path(self.out).write_text(PAGE, encoding='utf-8')
        with patch.object(COMPOSE_WORDS, 'compose', side_effect=RuntimeError('no browser')): record = run.compose_first_screen(self.dir, self.out)
        self.assertIn('no browser', record['words']['error']); self.assertEqual(Path(self.out).read_text(encoding='utf-8'), PAGE)
        with patch.object(COMPOSE_WORDS, 'compose', side_effect=AssertionError('not asked')): self.assertIn('no time left', run.compose_first_screen(self.dir, self.out, deadline=time.time() - 1)['words']['error'])

    def test_one_direction_runs_down_the_page(self):
        self.result = dict(self.result, direction='Hollow numerals; one dark pause.'); got = {}
        def lists(page, path, direction=None, **kw): got['lists'] = direction; return {'doc': json.loads(json.dumps(LISTS_OK)), 'drawn': True, 'attempts': 1, 'log': [], 'measured': {}}
        def pictures(page, path, images=None, direction=None, **kw): got['pictures'] = direction; return {'doc': json.loads(json.dumps(PICTURES_OK)), 'drawn': True, 'attempts': 1, 'log': [], 'measured': {}}
        def words(page, path, direction=None, **kw): got['words'] = direction; return self.words
        with patch.object(COMPOSE_LISTS, 'compose', lists), patch.object(COMPOSE_PICTURES, 'compose', pictures), patch.object(COMPOSE_WORDS, 'compose', words): record = run.compose_first_screen(self.dir, self.out)
        self.assertEqual(record['direction'], 'Hollow numerals; one dark pause.'); self.assertIn('Hollow numerals; one dark pause.', got['lists']); self.assertIn('typeface "fraunces"', got['lists'])
        self.assertIn('Already composed — lists: "what" as ledger', got['pictures'], 'each composer is told what the ones before it chose'); self.assertIn('Their idea: Hollow numerals.', got['pictures'])
        self.assertIn('Already composed — pictures: "room" as bleed', got['words']); self.assertNotIn('pictures:', got['lists'])
        Path(self.out).write_text(PAGE, encoding='utf-8'); self.result = {'ir': None, 'drawn': False, 'attempts': 2, 'log': [], 'wishes': [], 'measured': None, 'direction': 'never used'}
        with patch.object(COMPOSE_LISTS, 'compose', lists): record = run.compose_first_screen(self.dir, self.out)
        self.assertIsNone(got['lists'], 'a first screen that was not drawn directs nothing'); self.assertIsNone(record['direction'])

    def test_the_pictures_are_left_alone_when_the_job_has_no_time_left(self):
        with patch.object(COMPOSE_PICTURES, 'compose', side_effect=AssertionError('not asked')): record = run.compose_first_screen(self.dir, self.out, deadline=time.time() - 1)
        self.assertTrue(record['drawn'], 'the first screen is still composed'); self.assertIn('no time left', record['pictures']['error'])
        self.pictures = {'doc': json.loads(json.dumps(PICTURES_OK)), 'drawn': True, 'attempts': 1, 'log': [], 'measured': {}}
        self.assertTrue(run.compose_first_screen(self.dir, self.out, deadline=time.time() + 60)['pictures']['drawn'])

    def test_lists_alone_are_a_candidate_when_the_first_screen_is_refused(self):
        self.result = {'ir': None, 'drawn': False, 'attempts': 2, 'log': [], 'wishes': [], 'measured': None}
        self.lists = {'doc': json.loads(json.dumps(LISTS_OK)), 'drawn': True, 'attempts': 1, 'log': [], 'measured': {}}
        record = run.compose_first_screen(self.dir, self.out); page = Path(self.out).read_text(encoding='utf-8')
        self.assertTrue(record['drawn']); self.assertIn('lc lc-ledger', page); self.assertIn('<section class="sec hero" id="top">', page, 'the template\'s first screen stays')

    def test_a_lists_composer_that_fails_or_is_refused_leaves_the_first_screen_standing(self):
        with patch.object(COMPOSE_LISTS, 'compose', side_effect=RuntimeError('no browser')): record = run.compose_first_screen(self.dir, self.out)
        self.assertTrue(record['drawn']); self.assertIn('no browser', record['lists']['error']); self.assertNotIn(' lc ', Path(self.out).read_text(encoding='utf-8'))
        Path(self.out).write_text(PAGE, encoding='utf-8')
        self.lists = {'doc': {'ir': '0.2', 'lists': [{'section': 'what', 'form': 'bento', 'head': 'left'}]}, 'drawn': True, 'attempts': 1, 'log': [], 'measured': {}}
        record = run.compose_first_screen(self.dir, self.out)
        self.assertFalse(record['lists']['drawn'], 'a document the validator refuses is never drawn, whoever returned it'); self.assertNotIn('lc-bento', Path(self.out).read_text(encoding='utf-8'))

    def test_a_composition_the_validator_refuses_is_never_written(self):
        self.result['ir']['hero']['nodes'][2]['text'] = 'We are the best'
        record = run.compose_first_screen(self.dir, self.out)
        self.assertFalse(record['drawn']); self.assertEqual(Path(self.out).read_text(encoding='utf-8'), PAGE)


class Candidate(Job):
    def grade(self, taste, contract, failed=()):
        return lambda: ({'score': contract, 'failed': [{'id': i, 'detail': '', 'weight': 1} for i in failed]}, {'score': taste, 'verdict': 'seen', 'axes': {'design': taste}, 'fixes': []})

    def test_kept_when_it_scores_at_least_as_high(self):
        d = run.composed_candidate(self.dir, self.out, 70, [], self.grade(64, 96))   # .55×64 + .45×96 = 78
        self.assertTrue(d['kept']); self.assertEqual((d['score'], d['taste'], d['contract'], d['before']), (78, 64, 96, 70))
        d = run.composed_candidate(self.dir, self.out, 78, [], self.grade(64, 96)); self.assertTrue(d['kept'], 'a tie goes to the composed page')

    def test_not_kept_when_it_scores_lower(self):
        d = run.composed_candidate(self.dir, self.out, 80, [], self.grade(64, 96))
        self.assertFalse(d['kept']); self.assertIn('78', d['why']); self.assertIn('80', d['why'])

    def test_not_kept_when_it_breaks_a_hard_promise_the_winner_kept(self):
        d = run.composed_candidate(self.dir, self.out, 60, [], self.grade(90, 90, failed=['desktop-no-overflow']))
        self.assertFalse(d['kept']); self.assertIn('desktop-no-overflow', d['why'])
        d = run.composed_candidate(self.dir, self.out, 60, [{'id': 'desktop-no-overflow'}], self.grade(90, 90, failed=['desktop-no-overflow', 'h2-short']))
        self.assertTrue(d['kept'], 'what the winner already broke, and what is not a hard promise, is not held against the composition')

    def test_not_kept_when_nothing_was_drawn_or_it_cannot_be_graded(self):
        self.result = {'ir': None, 'drawn': False, 'attempts': 1, 'log': [], 'wishes': [], 'measured': None}
        called = []
        d = run.composed_candidate(self.dir, self.out, 60, [], lambda: called.append(1))
        self.assertFalse(d['kept']); self.assertEqual(called, [], 'a page that was not recomposed is not graded again: no model call')
        self.result = {'ir': json.loads(json.dumps(IR_OK)), 'drawn': True, 'attempts': 1, 'log': [], 'wishes': [], 'measured': {}}
        d = run.composed_candidate(self.dir, self.out, 60, [], lambda: ({'score': 95, 'failed': []}, {'verdict': 'no score'}))
        self.assertFalse(d['kept']); self.assertIn('could not be graded', d['why'])


class Recompose(Job):
    def setUp(self):
        super().setUp()
        self.snapshot = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.snapshot, True); os.makedirs(os.path.join(self.snapshot, 'critic-shots'))
        Path(self.dir, 'critic.json').write_text(json.dumps({'score': 70, 'round': 1})); Path(self.dir, 'contract.json').write_text(json.dumps({'score': 92, 'failed': []}))
        self.files = {p: open(p, 'rb').read() for p in (self.out, os.path.join(self.dir, 'critic.json'), os.path.join(self.dir, 'contract.json'))}
        self.log = {'rounds': [{'k': 1, 'score': 70, 'taste': 52, 'contract': 92, 'broken': []}]}
        self.manifest = {'fingerprints': {'inputs': {}, 'engine': {}}, 'html': run.digest(self.out)}
        quiet = patch.object(run, 'ev', lambda *a: None); quiet.start(); self.addCleanup(quiet.stop)
        self.reread = 52   # the taste the winner gets when it is read again: by default what its round recorded
    def go(self, taste, contract, failed=()):
        report = {'score': contract, 'failed': [{'id': i, 'detail': '', 'weight': 1} for i in failed]}
        def graded(slug_dir, html): Path(slug_dir, 'contract.json').write_text(json.dumps(report)); return report
        def read(slug_dir, page, *a, **k):   # the winner read again scores as its round did unless the test says otherwise; the composed page scores `taste`
            if str(page).endswith('.ref.html'):
                if self.reread is None: raise RuntimeError('no critic')
                return {'score': self.reread, 'verdict': 'the page as it stood', 'axes': {'design': self.reread}, 'fixes': []}
            return {'score': taste, 'verdict': 'composed page', 'axes': {'design': taste}, 'fixes': [{'op': 'note'}]}
        with patch.object(run, 'contract', graded), patch.object(run.C, 'critique', read), patch.object(run.C, 'critique_twice', read):
            return run.recompose(self.dir, self.out, self.log, 70, 1, self.manifest, self.files, self.snapshot)

    def test_the_composed_page_is_compared_with_the_winner_as_the_critic_reads_it_now(self):
        self.reread = 44   # read again, the winner is .55×44 + .45×92 = 65.6 → 66, not the 70 its round recorded
        score, best_round, _ = self.go(taste=50, contract=92)   # composed: .55×50 + .45×92 = 68.9 → 69
        self.assertEqual((score, best_round), (69, 2), 'under the recorded 70, over the 66 the same critic gives the winner now: kept')
        self.assertEqual(self.log['composition']['before'], 70); self.assertEqual(self.log['composition']['reference'], 66); self.assertEqual(self.record()['reference'], 66)
        self.assertFalse(os.path.exists(self.out + '.ref.html')); self.assertFalse(os.path.exists(os.path.join(self.dir, 'critic-shots-ref')))

    def test_without_a_second_reading_of_the_winner_its_recorded_score_stands(self):
        self.reread = None; score, best_round, _ = self.go(taste=50, contract=92)   # 69 against the recorded 70
        self.assertEqual((score, best_round), (70, 1)); self.assertFalse(self.log['composition']['kept']); self.assertNotIn('reference', self.log['composition'])

    def test_a_better_composed_page_becomes_the_page_with_its_own_reports(self):
        score, best_round, manifest = self.go(taste=66, contract=96)   # .55×66 + .45×96 = 79.5 → 80
        self.assertEqual((score, best_round), (80, 2)); self.assertEqual(manifest['html'], run.digest(self.out)); self.assertNotEqual(manifest['html'], self.manifest['html'])
        self.assertEqual(manifest['fingerprints'], self.manifest['fingerprints'], 'the inputs the page was made from are the same inputs')
        self.assertIn('class="sec hero ir"', Path(self.out).read_text(encoding='utf-8'))
        self.assertEqual(self.log['rounds'][-1]['composed'], True); self.assertEqual(self.log['composition']['kept'], True)
        critic = json.loads(Path(self.dir, 'critic.json').read_text()); self.assertEqual((critic['taste'], critic['round'], critic['composed']), (66, 2, True))
        card = run.scorecard(self.log, best_round); self.assertEqual((card['taste'], card['contract']), (66, 96))
        self.assertEqual(self.record()['kept'], True); self.assertEqual(self.record()['before'], 70)

    def test_a_weaker_composed_page_is_undone_to_the_byte(self):
        score, best_round, manifest = self.go(taste=40, contract=90)
        self.assertEqual((score, best_round, manifest), (70, 1, self.manifest))
        for path, data in self.files.items(): self.assertEqual(open(path, 'rb').read(), data, os.path.basename(path))
        self.assertEqual(len(self.log['rounds']), 1); self.assertFalse(self.log['composition']['kept']); self.assertFalse(self.record()['kept'])
        self.assertEqual(self.record()['verdict'], 'composed page', 'what the critic said of the page that was refused is kept: that is where there is most to learn'); self.assertEqual(self.record()['axes'], {'design': 40})

    def test_a_composer_that_fails_changes_nothing(self):
        with patch.object(COMPOSE, 'compose', side_effect=RuntimeError('credit exhausted')):
            score, best_round, manifest = self.go(taste=99, contract=99)
        self.assertEqual((score, best_round, manifest), (70, 1, self.manifest)); self.assertEqual(Path(self.out).read_text(encoding='utf-8'), PAGE)
        self.assertIn('credit exhausted', self.log['composition']['why'])


if __name__ == '__main__':
    unittest.main()
