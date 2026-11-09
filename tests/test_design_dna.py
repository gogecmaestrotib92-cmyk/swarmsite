"""The Design DNA library: every value in a record is bound to a file or is null, the validator catches a record
that claims more than its evidence, and retrieval gives the same references for the same brand."""
import copy, importlib.util, json, os, random, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location('design_dna_test_' + name, ROOT / 'design_dna' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


validate = load('validate'); build = validate.build; retrieve = load('retrieve')
CTX = validate.Context()
RECORDS = validate.load_records()
IDS = build.blueprint_ids()
RESTAURANT = {'kind': 'place', 'subtype': 'restaurant', 'photographs': 8, 'screenshots': 0, 'has_video': False, 'mode': None}
SAAS = {'kind': 'software', 'subtype': 'saas', 'photographs': 0, 'screenshots': 4, 'has_video': False, 'mode': None}
STUDIO = {'kind': 'service', 'subtype': 'architecture studio', 'photographs': 12, 'screenshots': 0, 'has_video': False, 'mode': None}


def raw_of(rid):
    path = ROOT / 'lib/blueprints/raw' / (rid + '.json')
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def held(pointer):
    return build.resolve_file_pointer(pointer)


class Build(unittest.TestCase):
    def test_files_on_disk_are_what_the_build_writes(self):
        self.assertEqual(build.stale(), [], 'run: python3 design_dna/build.py')

    def test_same_input_gives_the_same_bytes(self):
        first = build.generate(); second = build.generate()
        self.assertEqual(first, second)
        self.assertEqual(sorted(first), sorted(['design_dna/README.md'] + ['design_dna/references/%s.json' % i for i in IDS]))
        for seed in ('0', '4242'):          # set and dict order must not leak into a file
            run = subprocess.run([sys.executable, str(ROOT / 'design_dna/build.py'), '--check'], capture_output=True, text=True,
                                 env={**os.environ, 'PYTHONHASHSEED': seed})
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_one_record_per_blueprint(self):
        self.assertEqual(sorted(RECORDS), IDS)
        self.assertEqual(len(IDS), 12)

    def test_the_readme_table_is_generated_from_the_records(self):
        text = (ROOT / 'design_dna/README.md').read_text(encoding='utf-8')
        self.assertIn(build.tables([RECORDS[i] for i in IDS]), text)
        for rid in IDS: self.assertIn('| %s | %s |' % (rid, RECORDS[rid]['status']), text)


class Honesty(unittest.TestCase):
    """What the records may and may not say, checked against the blueprint and raw files rather than against the build."""

    def test_no_reference_has_mobile_measurements(self):
        for rid, rec in RECORDS.items():
            self.assertEqual(rec['completeness']['mobile'], 'missing', rid)
            raw = raw_of(rid) or {}
            self.assertFalse({'mobile', 'viewports'} & set(raw), rid)
            if raw.get('vw'): self.assertGreaterEqual(raw['vw'], 1000, rid)          # the one viewport there is, is a desktop one

    def test_no_reference_has_a_capture_date_or_pixel_ratio(self):
        for rid, rec in RECORDS.items():
            self.assertIsNone(rec['source']['captured_at'], rid); self.assertIsNone(rec['source']['dpr'], rid)
            raw = raw_of(rid) or {}
            self.assertFalse(set(build.UNREAD_CAPTURE_FIELDS) & set(raw), rid)

    def test_viewport_width_is_stated_only_where_the_capture_records_it(self):
        for rid, rec in RECORDS.items():
            raw = raw_of(rid)
            self.assertEqual(rec['source']['viewport']['w'], (raw or {}).get('vw'), rid)
            if raw: self.assertEqual(rec['composition']['fraction_base']['basis'], 'recorded' if raw.get('vw') else 'assumed', rid)

    def test_atelier_is_authored_and_mirrors_lpas(self):
        rec = RECORDS['atelier']
        self.assertEqual(rec['status'], 'authored'); self.assertIsNone(rec['evidence']['raw'])
        self.assertFalse((ROOT / 'lib/blueprints/raw/atelier.json').exists())
        self.assertEqual(rec['principles'], []); self.assertIsNone(rec['fits']['needs']); self.assertEqual(rec['fits']['temper'], [])
        self.assertFalse([v for v in rec['completeness'].values() if v in validate.MEASURED_CLAIMS])
        self.assertEqual(rec['evidence']['mirrors']['id'], 'lpas')
        self.assertEqual(rec['evidence']['mirrors']['differs_at'], ['/id', '/source', '/type/display/fam'])

    def test_every_other_reference_has_a_raw_capture(self):
        for rid, rec in RECORDS.items():
            if rid != 'atelier': self.assertEqual(rec['status'], 'measured-desktop', rid); self.assertTrue(raw_of(rid), rid)

    def test_screenshots_are_listed_only_where_the_folder_exists_and_never_copied(self):
        for rid, rec in RECORDS.items():
            folder = ROOT / 'dna' / rid; shots = rec['evidence']['screenshots']
            self.assertEqual(rec['completeness']['screenshots'] != 'missing', folder.is_dir(), rid)
            self.assertEqual(shots['desktop'], []); self.assertEqual(shots['mobile'], [])        # no file records its viewport
            for f in shots['unclassified']: self.assertTrue((ROOT / f).is_file(), f)
        self.assertEqual(sorted(r for r in RECORDS if RECORDS[r]['evidence']['screenshots']['unclassified']), ['butter', 'cerebrium', 'deepbook'])
        self.assertFalse([p for p in (ROOT / 'design_dna').rglob('*') if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.mp4')])

    def test_caveats_point_at_files_that_show_them(self):
        deep = RECORDS['deepbook']['evidence']['caveats'][0]
        self.assertEqual(deep['code'], 'profile-url-differs'); self.assertNotEqual(held(deep['shown_by'][0]), held(deep['shown_by'][1]))
        cer = {c['code']: c for c in RECORDS['cerebrium']['evidence']['caveats']}
        self.assertNotEqual(held(cer['profile-page-height-differs']['shown_by'][0]), held(cer['profile-page-height-differs']['shown_by'][1]))
        for rec in RECORDS.values():
            for c in rec['evidence']['caveats']:
                for p in c['shown_by']: held(p)                                               # raises when it does not resolve

    def test_measured_values_are_what_the_pointers_hold(self):
        for rid, rec in RECORDS.items():
            if rec['status'] == 'authored': continue
            for level in build.LEVELS:
                lv = rec['typography'][level]
                if not lv: continue
                el = held(lv['source']['raw']); bp = held(lv['source']['blueprint'])
                self.assertEqual(lv['px'], el['px'], (rid, level)); self.assertEqual(lv['px'], bp['px'], (rid, level))
                self.assertEqual(lv['source_face'], el.get('fam'), (rid, level))
            for i, sec in enumerate(rec['composition']['sections']):
                raw_sec = held(sec['source']['raw']); bp_sec = held(sec['source']['blueprint'])
                self.assertEqual(sec['role'], raw_sec.get('role'), (rid, i))
                if sec['screens'] is not None: self.assertEqual(sec['screens'], bp_sec['screens'], (rid, i))
                if sec['head']:
                    self.assertEqual(sec['head']['px'], held(sec['head']['source']).get('px'), (rid, i))
                for m in sec['media']:
                    im = held(m['source'])
                    self.assertEqual(m['ar'], round(im['w'] / im['h'], 2), (rid, i)); self.assertEqual(m['bleed'], im.get('bleed') is True, (rid, i))

    def test_a_default_of_the_normaliser_is_never_passed_off_as_a_measurement(self):
        seen = 0
        for rid, rec in RECORDS.items():
            raw = raw_of(rid)
            if not raw: continue
            for key in ('frame', 'gutter', 'col'):
                self.assertEqual(rec['composition']['grid'][key], raw.get(key), (rid, key))       # the blueprint invents frame and gutter
            for i, sec in enumerate(rec['composition']['sections']):
                h = sec['head']
                if not h: continue
                el = held(h['source']); rect = el.get('rect') or {}
                self.assertEqual(h['weight'] is None, not str(el.get('w', '')).split()[:1] or not str(el['w']).split()[0].isdigit(), (rid, i))
                self.assertEqual(h['leading'] is None, 'lh' not in el, (rid, i))
                self.assertEqual(h['tracking'] is None, 'ls' not in el, (rid, i))
                self.assertEqual(h['align'], el.get('al'), (rid, i)); self.assertEqual(h['case'], el.get('tt'), (rid, i))
                self.assertEqual(h['x'] is None, 'x' not in rect, (rid, i)); self.assertEqual(h['wf'] is None, 'w' not in rect, (rid, i))
                seen += sum(1 for k in ('weight', 'leading', 'align', 'x') if h[k] is None)
                bp_head = held(sec['source']['blueprint'])['head']
                if h['weight'] is None: self.assertEqual(bp_head['w'], 400, (rid, i))             # what the blueprint says instead
                if h['align'] is None: self.assertEqual(bp_head['al'], 'start', (rid, i))
        self.assertGreater(seen, 20, 'the fixtures no longer contain a defaulted value; this test checks nothing')

    def test_h2_is_null_where_the_blueprint_only_repeats_display(self):
        for rid in ('aino', 'halfdays', 'units'):
            bp = json.loads((ROOT / 'lib/blueprints' / (rid + '.bp.json')).read_text(encoding='utf-8'))
            self.assertEqual(bp['type']['h2'], bp['type']['display'])
            self.assertIsNone(RECORDS[rid]['typography']['h2']); self.assertEqual(RECORDS[rid]['typography']['levels_missing']['h2'], 'blueprint-copies-display')

    def test_tracking_comes_from_the_raw_letter_spacing(self):
        d = RECORDS['tengile']['typography']['display']; el = held(d['source']['raw'])
        self.assertEqual(el['ls'], '-2.4px'); self.assertEqual(d['tracking'], round(-2.4 / 120, 4))
        self.assertEqual(build.tracking_em('-2%', 81), -0.02); self.assertEqual(build.tracking_em('normal', 16), 0.0)
        self.assertIsNone(build.tracking_em(None, 16)); self.assertIsNone(build.tracking_em('tight', 16))

    def test_no_source_text_is_in_any_record(self):
        texts = [t for t in build.all_source_texts() if len(t) >= build.NOTE_QUOTE_MIN]
        self.assertGreater(len(texts), 50)
        for rid in IDS:
            body = (ROOT / 'design_dna/references' / (rid + '.json')).read_text(encoding='utf-8')
            for t in texts: self.assertNotIn(json.dumps(t, ensure_ascii=False)[1:-1], body, rid)

    def test_prose_is_carried_with_its_pointer_or_withheld(self):
        n = 0
        for rid, rec in RECORDS.items():
            for path, node in validate.walk(rec):
                if isinstance(node, dict) and node.get('kind') == 'prose':
                    n += 1
                    if node['text'] is None: self.assertEqual(node['withheld'], 'quotes-source-text', (rid, path))
                    else: self.assertEqual(node['text'], held(node['source']), (rid, path))
        self.assertGreater(n, 60)
        withheld = [n for n in RECORDS['cerebrium']['experience']['section_notes'] if n['withheld']]
        self.assertTrue(withheld, 'cerebrium notes quote two labels of the page')

    def test_principles_are_rule_made_and_point_at_values(self):
        fired = 0
        for rid, rec in RECORDS.items():
            for p in rec['principles']:
                fired += 1
                self.assertEqual(p['derived_by'], 'rule'); self.assertIn(p['rule'], build.RULE_NAMES); self.assertIn(p['confidence'], ('measured', 'observed'))
                for e in p['evidence']: self.assertIsNotNone(build.resolve_internal(rec, e), (rid, p['id'], e))
                self.assertIn('Threshold', p['statement'], (rid, p['id']))
            self.assertEqual([t['principle'] for t in rec['fits']['temper']], [p['id'] for p in rec['principles']], rid)
        self.assertGreater(fired, 40)

    def test_a_rule_fires_at_its_threshold_and_not_beside_it(self):
        def rec(weight=None, display=100, body=None, tracking=None):
            typ = {'display': {'px': display, 'weight': weight, 'tracking': tracking, 'leading': None, 'case': None}, 'body': {'px': body} if body else None, 'families': None,
                   'ratios': {'display_to_body': {'value': round(display / body, 2)} if body else None, 'display_to_h2': None}}
            return {'typography': typ}
        self.assertTrue(build.rule_display_light_weight(rec(weight=300))); self.assertIsNone(build.rule_display_light_weight(rec(weight=310)))
        self.assertIsNone(build.rule_display_light_weight(rec(weight=None)), 'an unrecorded weight is not a light weight')
        self.assertTrue(build.rule_display_heavy_weight(rec(weight=700))); self.assertIsNone(build.rule_display_heavy_weight(rec(weight=690)))
        self.assertTrue(build.rule_scale_contrast_high(rec(display=112, body=16))); self.assertIsNone(build.rule_scale_contrast_high(rec(display=111, body=16)))
        self.assertIsNone(build.rule_scale_contrast_high(rec(display=320)), 'no body size, no ratio, no principle')
        self.assertTrue(build.rule_tight_tracking(rec(tracking=-0.02))); self.assertIsNone(build.rule_tight_tracking(rec(tracking=-0.019)))
        self.assertIsNone(build.rule_tight_tracking(rec(tracking=None)))

    def test_pinned_is_only_observed_when_it_rests_on_a_role_name(self):
        for rid, rec in RECORDS.items():
            for p in rec['principles']:
                if p['id'] != 'pinned-sections': self.assertEqual(p['confidence'], 'measured', (rid, p['id'])); continue
                flagged = any(s['sticky'] for s in rec['composition']['sections'])
                self.assertEqual(p['confidence'], 'measured' if flagged else 'observed', rid)

    def test_rights(self):
        fonts = json.loads((ROOT / 'lib/typography/fonts.json').read_text(encoding='utf-8'))
        listed = {f['name'].lower() for f in fonts['fonts']}
        for rid, rec in RECORDS.items():
            self.assertEqual(rec['rights']['screenshots'], 'research-only'); self.assertEqual(rec['rights']['source_text'], 'excluded')
            for f in rec['rights']['fonts']:
                if f['source'] is None:
                    self.assertEqual(f['licence'], 'unknown', (rid, f['face'])); self.assertNotIn(f['face'].lower(), listed, (rid, f['face']))
                else: self.assertEqual(f['licence'], held(f['source']), (rid, f['face']))
        self.assertIn({'face': 'ABC Favorit', 'role': 'source', 'licence': 'Dinamo — paid',
                       'source': 'lib/typography/fonts.json#/_meta/seen_on_winners_licensed/ABC Favorit (Cerebrium)'}, RECORDS['cerebrium']['rights']['fonts'])

    def test_delivery_face_is_what_the_renderer_returns(self):
        spec = importlib.util.spec_from_file_location('render_bp_for_dna_test', ROOT / 'lib/render/render_bp.py')
        render_bp = importlib.util.module_from_spec(spec); spec.loader.exec_module(render_bp)
        for rid, rec in RECORDS.items():
            for level in build.LEVELS:
                lv = rec['typography'][level]
                if lv: self.assertEqual((lv['delivery_face'], lv['delivery_class']), tuple(render_bp.font_for(lv['source_face'])), (rid, level))
        self.assertEqual(RECORDS['tengile']['typography']['display']['delivery_face'], 'Cormorant Garamond')
        self.assertTrue(RECORDS['units']['typography']['display']['delivery_fallback'], 'the renderer has no mapping for this face')

    def test_recipe_pointer_names_a_recipe(self):
        for rid, rec in RECORDS.items(): self.assertEqual(rec['implementation'], {'recipe': 'lib/templates/recipes.py#' + rid, 'ir_seeds': []})


class Validator(unittest.TestCase):
    def problems(self, rid, change):
        rec = copy.deepcopy(RECORDS[rid]); change(rec)
        return validate.validate_record(rec, CTX)

    def assertCaught(self, problems, *words):
        self.assertTrue(problems, 'the validator let a seeded defect through')
        self.assertTrue(any(all(w in p for w in words) for p in problems), '\n'.join(problems))

    def test_all_twelve_validate(self):
        self.assertEqual(validate.validate_all(), {})
        for rid in IDS: self.assertEqual(validate.validate_record(RECORDS[rid], CTX), [], rid)

    def test_command_line_exits_zero_on_a_valid_library(self):
        run = subprocess.run([sys.executable, str(ROOT / 'design_dna/validate.py')], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr); self.assertIn('12 records valid', run.stdout)

    def test_a_missing_evidence_path_is_caught(self):
        def change(r): r['evidence']['raw'] = 'lib/blueprints/raw/tengile-recapture.json'
        self.assertCaught(self.problems('tengile', change), 'evidence.raw', 'no such file')
        def shot(r): r['evidence']['screenshots']['unclassified'].append('dna/butter/not-there.jpg')
        self.assertCaught(self.problems('butter', shot), 'no such file', 'dna/butter/not-there.jpg')
        def pointer(r): r['typography']['display']['source']['raw'] = 'lib/blueprints/raw/tengile.json#/sections/0/heads/7'
        self.assertCaught(self.problems('tengile', pointer), 'typography.display.source.raw', 'does not resolve')
        def recipe(r): r['implementation']['recipe'] = 'lib/templates/recipes.py#nope'
        self.assertCaught(self.problems('tengile', recipe), 'no recipe')

    def test_a_dangling_pointer_is_caught(self):
        def change(r): r['principles'][0]['evidence'] = ['typography.display.optical_size']
        self.assertCaught(self.problems('tengile', change), 'principles[0].evidence', 'does not resolve')
        def summary(r): r['composition']['summary']['offset_heading_share']['matched'].append('composition.sections[99].head.x')
        self.assertCaught(self.problems('tengile', summary), 'offset_heading_share', 'does not resolve')
        def null(r): r['principles'][0]['evidence'] = ['composition.sections[0].head.y']        # tengile: the hero has no section rect, so y is null
        self.assertCaught(self.problems('tengile', null), 'null', 'not evidence')

    def test_a_measured_claim_on_the_authored_record_is_caught(self):
        def change(r): r['completeness']['typography'] = 'measured'
        self.assertCaught(self.problems('atelier', change), 'completeness.typography', 'authored')
        def principle(r): r['principles'] = copy.deepcopy(RECORDS['lpas']['principles'][:1])
        self.assertCaught(self.problems('atelier', principle), 'authored record cannot carry principles')
        def basis(r): r['typography']['basis'] = 'measured'
        self.assertCaught(self.problems('atelier', basis), 'typography.basis')
        def status(r): r['status'] = 'measured-desktop'
        self.assertCaught(self.problems('atelier', status), 'needs a raw capture')

    def test_a_wrong_delivery_face_is_caught(self):
        def change(r): r['typography']['display']['delivery_face'] = 'PP Fragment'
        self.assertCaught(self.problems('tengile', change), 'typography.display.delivery_face', 'font_for')

    def test_copied_source_text_is_caught(self):
        long_text = max(build.raw_source_texts(raw_of('butter')), key=len)
        self.assertGreater(len(long_text), 80)
        def note(r): r['motion']['transitions'].append('note: ' + long_text[5:75].upper())
        self.assertCaught(self.problems('butter', note), 'characters of a source heading')
        def whole(r): r['fits']['archetype'] = held('lib/blueprints/raw/cerebrium.json#/sections/0/heads/0/text')
        self.assertCaught(self.problems('cerebrium', whole), 'fits.archetype', 'quotes a source heading')

    def test_invented_prose_is_caught(self):
        def change(r): r['motion']['note']['text'] = 'Slow, cinematic reveals that feel expensive.'
        self.assertCaught(self.problems('tengile', change), 'motion.note', 'is not what')
        def bare(r): r['experience']['section_notes'][0]['text'] = None
        self.assertCaught(self.problems('tengile', bare), 'withheld')

    def test_a_claim_without_a_file_is_caught(self):
        def mobile(r): r['completeness']['mobile'] = 'measured'
        self.assertCaught(self.problems('tengile', mobile), 'completeness.mobile')
        def date(r): r['source']['captured_at'] = '2026-11-06'
        self.assertCaught(self.problems('tengile', date), 'captured_at', 'needs')
        def shots(r): r['completeness']['screenshots'] = 'unverified'
        self.assertCaught(self.problems('tengile', shots), 'completeness.screenshots')
        def width(r): r['source']['viewport']['w'] = 1440
        self.assertCaught(self.problems('tengile', width), 'source.viewport.w')

    def test_an_unknown_or_mislabelled_principle_is_caught(self):
        def unknown(r): r['principles'].append({'id': 'feels-premium', 'statement': 'Feels premium.', 'evidence': ['typography.display.px'], 'derived_by': 'rule', 'confidence': 'measured', 'rule': 'rule_feels_premium'})
        self.assertCaught(self.problems('tengile', unknown), 'feels-premium', 'not produced by any rule')
        def human(r): r['principles'][0]['derived_by'] = 'human'
        self.assertCaught(self.problems('tengile', human), 'derived_by')
        def empty(r): r['principles'][0]['evidence'] = []
        self.assertCaught(self.problems('tengile', empty), 'at least 1 item')

    def test_a_stale_record_is_caught(self):
        def change(r): r['built_from']['lib/blueprints/tengile.bp.json'] = 'sha256:' + '0' * 64
        self.assertCaught(self.problems('tengile', change), 'has changed since the record was built')

    def test_shape_errors_are_caught(self):
        def status(r): r['status'] = 'measured'
        self.assertCaught(self.problems('tengile', status), 'status', 'not one of')
        def missing(r): del r['rights']
        self.assertCaught(self.problems('tengile', missing), 'required field "rights"')
        def extra(r): r['vibe'] = 'quiet luxury'
        self.assertCaught(self.problems('tengile', extra), 'vibe', 'not in the schema')

    def test_the_schema_cannot_promise_what_the_validator_does_not_check(self):
        with self.assertRaises(validate.SchemaError): validate.check_schema({}, {'oneOf': [{'type': 'object'}]}, {})
        used = set()
        def keys(node):
            if isinstance(node, dict):
                if any(k in node for k in ('type', 'enum', 'const', '$ref', 'properties')): used.update(node)
                for k, v in node.items(): keys(list(v.values()) if k in ('properties', '$defs') else v)
            elif isinstance(node, list):
                for v in node: keys(v)
        keys(CTX.schema)
        self.assertLessEqual(used, validate.KEYWORDS | validate.ANNOTATIONS)


class Inputs(unittest.TestCase):
    """The build and the validator against inputs that changed, in a throwaway copy of the files they read."""

    def sandbox(self):
        import shutil
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup); root = Path(tmp.name)
        shutil.copytree(ROOT / 'lib/blueprints', root / 'lib/blueprints')
        shutil.copytree(ROOT / 'design_dna', root / 'design_dna', ignore=shutil.ignore_patterns('__pycache__'))
        for f in ('lib/blueprint/normalize.py', 'lib/templates/recipes.py', 'lib/typography/fonts.json'):
            (root / f).parent.mkdir(parents=True, exist_ok=True); shutil.copy(ROOT / f, root / f)
        os.symlink(ROOT / 'dna', root / 'dna')
        return root

    def edit(self, path, change):
        data = json.loads(path.read_text(encoding='utf-8')); change(data); path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding='utf-8')

    def write(self, root):
        for path, text in build.generate(str(root)).items(): (root / path).write_text(text, encoding='utf-8')

    def test_the_copy_builds_to_the_same_bytes(self):
        root = self.sandbox()
        self.assertEqual(build.generate(str(root)), build.generate())
        self.assertEqual(validate.validate_all(str(root)), {})

    def test_a_blueprint_value_the_capture_does_not_hold_stops_the_build(self):
        root = self.sandbox()
        self.edit(root / 'lib/blueprints/tengile.bp.json', lambda bp: bp['type']['display'].update(px=132))
        with self.assertRaises(build.BuildError) as err: build.generate(str(root))
        self.assertIn('tengile', str(err.exception)); self.assertIn('type/display', str(err.exception))
        report = validate.validate_all(str(root))
        self.assertTrue(any('cannot build' in p for p in report['(library)']), report)
        self.assertTrue(any('has changed since the record was built' in p for p in report['tengile']), report)

    def test_a_capture_that_gains_a_date_or_a_second_viewport_stops_the_build(self):
        for field, value in (('captured_at', '2026-11-09'), ('dpr', 2), ('mobile', {'vw': 390})):
            root = self.sandbox()
            self.edit(root / 'lib/blueprints/raw/tengile.json', lambda raw: raw.update({field: value}))
            with self.assertRaises(build.BuildError) as err: build.generate(str(root))
            self.assertIn(field, str(err.exception))

    def test_a_change_the_records_do_not_use_still_marks_them_stale(self):
        root = self.sandbox()
        self.edit(root / 'lib/blueprints/crav.bp.json', lambda bp: bp['button'].update(h=52))
        report = validate.validate_all(str(root))
        self.assertEqual(sorted(report), ['(library)', 'crav'])
        self.assertTrue(any('has changed since the record was built' in p for p in report['crav']))
        self.write(root)
        self.assertEqual(validate.validate_all(str(root)), {})

    def test_a_reference_without_a_capture_becomes_authored(self):
        root = self.sandbox()
        (root / 'lib/blueprints/raw/units.json').unlink()
        self.write(root)
        rec = json.loads((root / 'design_dna/references/units.json').read_text(encoding='utf-8'))
        self.assertEqual(rec['status'], 'authored'); self.assertEqual(rec['principles'], []); self.assertIsNone(rec['fits']['needs'])
        self.assertEqual(rec['completeness']['typography'], 'authored'); self.assertIsNone(rec['source']['viewport']['h'])
        self.assertEqual(validate.validate_all(str(root)), {})
        ids = [r['id'] for r in retrieve.retrieve(RESTAURANT, k=12, records=retrieve.load_records(str(root / 'design_dna/references')))]
        self.assertNotIn('units', ids); self.assertIn('tengile', ids)

    def test_evidence_json_must_list_every_blueprint_and_only_true_caveats(self):
        root = self.sandbox(); ev = root / 'design_dna/evidence.json'
        self.edit(ev, lambda e: e['references'].pop('crav'))
        with self.assertRaises(build.BuildError): build.generate(str(root))
        root = self.sandbox(); ev = root / 'design_dna/evidence.json'
        same = 'lib/blueprints/deepbook.bp.json#/source'
        self.edit(ev, lambda e: e['references']['deepbook']['caveats'][0].update(shown_by=[same, same]))
        with self.assertRaises(build.BuildError) as err: build.generate(str(root))
        self.assertIn('profile-url-differs', str(err.exception))
        root = self.sandbox(); ev = root / 'design_dna/evidence.json'
        self.edit(ev, lambda e: e['references']['cerebrium']['caveats'][1].update(shown_by=['dna/cerebrium/data.json#/fonts/body', 'lib/blueprints/raw/cerebrium.json#/sections/0/paras/0/px']))
        with self.assertRaises(build.BuildError): build.generate(str(root))             # that profile text does mention the measured 17px

    def test_a_screenshot_folder_that_is_not_registered_is_caught(self):
        root = self.sandbox()
        self.edit(root / 'design_dna/evidence.json', lambda e: e['references']['butter'].update(screenshots=None, caveats=[]))
        self.write(root)
        report = validate.validate_all(str(root))
        self.assertTrue(any('dna/butter exists and is not registered' in p for p in report.get('butter', [])), report)


class Retrieval(unittest.TestCase):
    def test_weights_add_up_and_the_temper_vocabulary_is_the_rules(self):
        self.assertEqual(sum(retrieve.WEIGHTS.values()), 100)
        self.assertEqual(list(retrieve.TEMPER_TAGS), build.TEMPER_TAGS)

    def test_same_brand_same_references(self):
        records = retrieve.load_records()
        for brand in (RESTAURANT, SAAS, STUDIO, {'kind': 'product', 'photographs': 3, 'mode': 'light', 'temper': ['image-led', 'compact']}):
            first = retrieve.retrieve(brand); again = retrieve.retrieve(dict(brand))
            self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(again, sort_keys=True))
            shuffled = records[:]; random.Random(7).shuffle(shuffled)
            self.assertEqual([r['id'] for r in retrieve.retrieve(brand, records=shuffled)], [r['id'] for r in first])
            for r in first:
                self.assertEqual(r['score'], round(sum(r['components'].values()), 2)); self.assertLessEqual(r['score'], 100)
                self.assertEqual(set(r['components']), set(retrieve.WEIGHTS))
            self.assertEqual([r['score'] for r in first], sorted((r['score'] for r in first), reverse=True))

    def test_a_place_with_eight_photographs_gets_place_references_first(self):
        got = retrieve.retrieve(RESTAURANT, k=4)
        self.assertEqual(len(got), 4)
        for r in got: self.assertIn('place', r['card']['kinds'], r['id'])
        ranked = retrieve.retrieve(RESTAURANT, k=12); kinds = ['place' in r['card']['kinds'] for r in ranked]
        self.assertEqual(kinds, sorted(kinds, reverse=True), 'a reference of another kind is ranked above a place reference')

    def test_software_without_photographs_is_not_led_by_references_that_need_many(self):
        for brand in ({'kind': 'software', 'photographs': 0, 'screenshots': 0}, SAAS):
            supply = brand['photographs'] + brand['screenshots']
            got = retrieve.retrieve(brand, k=12); soft = [r for r in got if 'software' in r['card']['kinds']]
            self.assertEqual(len(soft), 3)
            self.assertLessEqual(got[0]['card']['needs']['images_min'], supply, 'the first reference needs more stills than the brand has')
            for r in got:
                if 'software' not in r['card']['kinds']: self.assertLessEqual(r['card']['needs']['images_min'], supply, r['id'])
        none = [r for r in retrieve.retrieve({'kind': 'software', 'photographs': 0, 'screenshots': 0}, k=12)]
        needs = [r['card']['needs']['images_min'] for r in none]
        self.assertEqual(needs, sorted(needs), 'with no stills at all, the reference that needs fewest comes first')
        self.assertEqual(none[0]['id'], 'deepbook')
        met = [r['card']['needs']['images_min'] <= 0 for r in none]
        self.assertEqual(met, sorted(met, reverse=True), 'a reference the brand cannot fill is ranked above one it can')

    def test_another_kind_is_returned_only_when_its_need_fits_and_a_principle_applies(self):
        seen = 0
        for brand in (RESTAURANT, SAAS, STUDIO, {'kind': 'product', 'photographs': 1}, {'kind': 'service', 'photographs': 0, 'mode': 'dark'}):
            for r in retrieve.retrieve(brand, k=12):
                if brand['kind'] in r['card']['kinds']: continue
                seen += 1
                self.assertLessEqual(r['card']['needs']['images_min'], brand.get('photographs', 0) + brand.get('screenshots', 0), r['id'])
                self.assertTrue(r['applies'], r['id'])
                self.assertTrue(set(r['applies']) <= {p['id'] for p in r['card']['principles']})
        self.assertGreater(seen, 5)
        self.assertIn('lpas', [r['id'] for r in retrieve.retrieve(SAAS, k=12)], 'fit, not class: a service reference the brand can fill')

    def test_authored_is_never_returned(self):
        for kind in retrieve.KINDS:
            for photos in (0, 3, 30):
                for mode in (None, 'light', 'dark'):
                    ids = [r['id'] for r in retrieve.retrieve({'kind': kind, 'photographs': photos, 'mode': mode, 'has_video': True, 'subtype': 'editorial studio'}, k=50)]
                    self.assertNotIn('atelier', ids)
                    for i in ids: self.assertNotEqual(RECORDS[i]['status'], 'authored')

    def test_mode_temper_video_and_subtype_move_the_order(self):
        dark = retrieve.retrieve({'kind': 'software', 'screenshots': 4, 'mode': 'dark'}, k=3)
        self.assertEqual(dark[-1]['id'], 'butter', 'the one light software reference comes last for a brand that wants dark')
        self.assertEqual(dark[0]['components']['mode'], 10)
        tempered = retrieve.retrieve({'kind': 'place', 'photographs': 8, 'temper': ['uppercase', 'light-weight']}, k=4)
        self.assertEqual(tempered[0]['components']['temper'], 10); self.assertIn(tempered[0]['id'], ('tengile', 'belgrade-arbor'))
        self.assertEqual(retrieve.retrieve({'kind': 'place', 'photographs': 8, 'temper': ['not-a-tag']}, k=1)[0]['components']['temper'], 0)
        video = {r['id']: r for r in retrieve.retrieve({'kind': 'place', 'photographs': 8, 'has_video': True}, k=4)}
        self.assertEqual(video['tengile']['components']['video'], 5); self.assertEqual(video['units']['components']['video'], 0)
        studio = {r['id']: r for r in retrieve.retrieve(STUDIO, k=4)}
        self.assertEqual(studio['lpas']['components']['subtype'], 5); self.assertEqual(studio['aino']['components']['subtype'], 0)

    def test_the_card_is_compact_and_says_what_is_missing(self):
        r = retrieve.retrieve(RESTAURANT, k=1)[0]; c = r['card']
        self.assertEqual(set(c), {'id', 'status', 'kinds', 'archetype', 'completeness', 'missing', 'typography', 'composition', 'imagery', 'needs', 'temper', 'principles', 'caveats'})
        self.assertIn('mobile', c['missing']); self.assertEqual(c['completeness'], RECORDS[c['id']]['completeness'])
        self.assertEqual([p['id'] for p in c['principles']], [p['id'] for p in RECORDS[c['id']]['principles']])
        self.assertLess(len(json.dumps(c)), 4000)
        self.assertTrue(r['reasons']); self.assertIn('kind', r['reasons'][0])
        self.assertIn(c['id'], retrieve.card_text(r))

    def test_bad_brands_are_refused(self):
        with self.assertRaises(TypeError): retrieve.retrieve('place')
        with self.assertRaises(ValueError): retrieve.retrieve({'kind': 'place', 'photographs': -1})
        with self.assertRaises(ValueError): retrieve.retrieve({'kind': 'place', 'photographs': '8'})
        self.assertEqual(retrieve.retrieve(RESTAURANT, k=0), [])

    def test_brand_from_a_job_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            images = [{'id': 'a', 'w': 1344, 'data': 'data:image/jpeg;base64,AAAA'}, {'id': 'b', 'w': 900, 'data': 'data:image/jpeg;base64,AAAA'},
                      {'id': 'small', 'w': 420, 'data': 'data:image/jpeg;base64,AAAA'}, {'id': 'crop', 'w': 800, 'data': 'data:image/jpeg;base64,AAAA', 'crop_of': 'a'},
                      {'id': 'gen', 'w': 1200, 'data': 'data:image/jpeg;base64,AAAA', 'gen': True}, {'id': 'shot', 'w': 1440, 'data': 'data:image/png;base64,AAAA', 'shot': True},
                      {'id': 'shot-crop', 'w': 700, 'data': 'data:image/png;base64,AAAA', 'shot': True, 'crop_of': 'shot'}, {'id': 'nodata', 'w': 1600}]
            Path(tmp, 'images.json').write_text(json.dumps(images)); Path(tmp, 'direction.json').write_text(json.dumps({'kind': 'place', 'mode': 'light'}))
            self.assertEqual(retrieve.brand_from_job(tmp), {'kind': 'place', 'subtype': None, 'photographs': 2, 'screenshots': 1, 'has_video': False, 'mode': 'light', 'temper': []})
            Path(tmp, 'hero.mp4').write_bytes(b'\x00'); Path(tmp, 'direction.json').write_text(json.dumps({'kind': 'software', 'mode': 'auto'}))
            brand = retrieve.brand_from_job(tmp)
            self.assertTrue(brand['has_video']); self.assertIsNone(brand['mode']); self.assertEqual(brand['kind'], 'software')
            run = subprocess.run([sys.executable, str(ROOT / 'design_dna/retrieve.py'), tmp, '--k', '2', '--json'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            out = json.loads(run.stdout)
            self.assertEqual(out['brand'], brand); self.assertEqual([r['id'] for r in out['results']], [r['id'] for r in retrieve.retrieve(brand, k=2)])
            text = subprocess.run([sys.executable, str(ROOT / 'design_dna/retrieve.py'), tmp], capture_output=True, text=True)
            self.assertEqual(text.returncode, 0, text.stderr); self.assertIn('score', text.stdout)
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(retrieve.brand_from_job(empty), {'kind': None, 'subtype': None, 'photographs': 0, 'screenshots': 0, 'has_video': False, 'mode': None, 'temper': []})
        with tempfile.TemporaryDirectory() as real:                       # the repo's own sample job: five photographs, no screenshot
            Path(real, 'images.json').write_bytes((ROOT / 'tests/images.sample.json').read_bytes())
            Path(real, 'direction.json').write_bytes((ROOT / 'tests/direction.sample.json').read_bytes())
            sample = retrieve.brand_from_job(real)
            self.assertEqual((sample['kind'], sample['mode'], sample['photographs'], sample['screenshots'], sample['has_video']), ('software', 'light', 5, 0, False))


if __name__ == '__main__':
    unittest.main()
