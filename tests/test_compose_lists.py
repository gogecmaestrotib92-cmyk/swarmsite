"""Lists below the first screen as compositions: read off the page whole, validated whole, drawn in another form with the
same items in the same order, and chosen by a model that is held to what the render measures. No network, no model:
the model is a stand-in function and the browser tools are patched."""
import copy, json, os, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'compose'))
import compose_lists as COMPOSE
import lists as LISTS
import sections as SECTIONS


def production_page():
    """A real page from the production renderer with an index list ("feat", numbered) and a row of cards ("nums", facts)."""
    with tempfile.TemporaryDirectory() as temp:
        job = Path(temp)
        for name in ('direction', 'images', 'inventory', 'assets'):
            src = ROOT / 'tests' / f'{name}.sample.json'
            if src.is_file(): shutil.copy(src, job / f'{name}.json')
        d = json.loads((job / 'direction.json').read_text()); d['kind'] = 'software'; d.pop('house', None)
        for beat in d['beats']:
            if beat['id'] in ('feat', 'nums'): beat['ui'] = dict(beat.get('ui') or {}, move='cards')
        (job / 'direction.json').write_text(json.dumps(d))
        out = job / 'page.html'
        r = subprocess.run([sys.executable, str(ROOT / 'lib/render/render_bp.py'), str(job), 'butter', str(out)], capture_output=True, text=True, env={**os.environ, 'LIVETEST': '1'})
        assert r.returncode == 0, r.stderr
        return out.read_text(), d


PAGE, DIRECTION = production_page()
BY_ID = {s['id']: s for s in SECTIONS.sections(PAGE)}
read = lambda sid, page=PAGE: SECTIONS.from_section(page[{s['id']: s for s in SECTIONS.sections(page)}[sid]['span'][0]:{s['id']: s for s in SECTIONS.sections(page)}[sid]['span'][1]])
FEAT, NUMS = read('feat'), read('nums')
def doc(*lists): return {'ir': '0.2', 'lists': [dict(l) for l in lists]}
def codes(document, page=PAGE): return sorted({e['code'] for e in LISTS.validate(document, page)})
LEDGER = {'section': 'feat', 'form': 'ledger', 'numerals': 'outline', 'head': 'left', 'title': 'lg'}
BENTO = {'section': 'nums', 'form': 'bento', 'feature': 1}


class Reader(unittest.TestCase):
    def test_the_page_has_the_lists_the_direction_wrote(self):
        self.assertEqual((BY_ID['feat']['kind'], BY_ID['nums']['kind']), ('indexlist', 'cards'))
        beat = next(b for b in DIRECTION['beats'] if b['id'] == 'feat')
        self.assertEqual([i['title'] for i in FEAT['items']], [f['title'] for f in beat['features']]); self.assertEqual([i['body'] for i in FEAT['items']], [' '.join(f['body'].split()) for f in beat['features']])
        cells = next(b for b in DIRECTION['beats'] if b['id'] == 'nums')['cells']
        self.assertEqual(len(NUMS['items']), len(cells)); self.assertTrue(all(i['tag'] for i in NUMS['items']), 'a card\'s figure is its tag')
        self.assertIn(beat['h2'].split()[0], re.sub(r'<[^>]+>', ' ', FEAT['head']))

    def test_sections_are_found_in_page_order_with_the_hero_first(self):
        found = SECTIONS.sections(PAGE)
        self.assertIn('hero', found[0]['classes']); self.assertEqual([s['span'][0] for s in found], sorted(s['span'][0] for s in found))
        for s in found: self.assertTrue(PAGE[s['span'][0]:s['span'][1]].startswith('<section') and PAGE[s['span'][0]:s['span'][1]].endswith('</section>'))

    def test_a_list_that_cannot_be_read_whole_is_refused(self):
        section = PAGE[BY_ID['feat']['span'][0]:BY_ID['feat']['span'][1]]
        with self.assertRaises(ValueError): SECTIONS.from_section(section.replace('<h3 class="h3">', '<table><tr><td>', 1))
        with self.assertRaises(ValueError): SECTIONS.from_section(PAGE[BY_ID['jelovnik']['span'][0]:BY_ID['jelovnik']['span'][1]])   # a price ledger is not a list this reader knows
        how = read('how'); self.assertEqual((how['kind'], len(how['items']), [i['tag'] for i in how['items']]), ('ladder', 3, ['01', '02', '03']), 'steps are a heading block and items too')
        self.assertTrue(all(i['title'] for i in how['items'])); self.assertTrue(LISTS.numbering(how['items']))
        one = re.sub(r'(<li class="index-row">.*?</li>)(<li class="index-row">.*</li>)(</ol>)', r'\1\3', section, flags=re.S)
        with self.assertRaises(ValueError): SECTIONS.from_section(one)


FAQ = ('<section class="sec faq band-paper" id="faq"><div class="wrap two"><div><span class="lab">FAQ</span><h2 class="h2">Questions</h2></div><div class="qa">'
       '<details><summary>Can I import?</summary><p>Yes.<br>Drag files in.</p></details><details><summary>Is there a trial?</summary><p>Fourteen days.</p><p>No card.</p></details></div></div></section>')
FIGURES = ('<section class="sec numbers band-alt" id="figs"><div class="wrap"><div class="gh one center"><h2 class="h2">In figures</h2></div><div class="nums">'
           '<div><b class="num">&lt;30s</b><p class="num-label">Average redesign</p><p>On most documents</p></div><div><b class="num">5</b><p class="num-label">Art directions</p><p>Each complete</p></div>'
           '<div><b class="num">0</b><p class="num-label">Words changed</p><p>Ever</p></div></div></div></section>')
SMALL_PAGE = '<html><head></head><body><section class="sec hero" id="top"><h1>Hello</h1></section>' + FAQ + FIGURES + '</body></html>'


class OtherKinds(unittest.TestCase):
    """Questions and figures are a heading block and items like any list: read whole, drawn in the same forms."""
    def test_questions_are_read_with_their_whole_answers(self):
        faq = SECTIONS.from_section(FAQ); self.assertEqual((faq['kind'], faq['band'], len(faq['items'])), ('faq', 'paper', 2))
        self.assertEqual([(i['tag'], i['title'], i['body']) for i in faq['items']], [('', 'Can I import?', 'Yes. Drag files in.'), ('', 'Is there a trial?', 'Fourteen days. No card.')])
        self.assertIn('<h2 class="h2">Questions</h2>', faq['head'])

    def test_figures_are_facts_with_a_name_and_a_line(self):
        figs = SECTIONS.from_section(FIGURES); self.assertEqual([(i['tag'], i['title'], i['body']) for i in figs['items']], [('<30s', 'Average redesign', 'On most documents'), ('5', 'Art directions', 'Each complete'), ('0', 'Words changed', 'Ever')])
        self.assertFalse(LISTS.numbering(figs['items'])); self.assertEqual({e['code'] for e in LISTS.validate({'ir': '0.2', 'lists': [{'section': 'figs', 'form': 'bento', 'numerals': 'none'}]}, SMALL_PAGE)}, {'IL022'})

    def test_they_are_drawn_in_the_forms_a_list_has_and_say_what_they_said(self):
        out, report = LISTS.transplant(SMALL_PAGE, {'ir': '0.2', 'lists': [{'section': 'faq', 'form': 'ledger', 'numerals': 'none', 'head': 'left'}, {'section': 'figs', 'form': 'bento', 'feature': 0}]})
        self.assertTrue(report['drawn'], report['errors']); self.assertEqual(report['sections'], ['faq', 'figs'])
        self.assertIn('<h3 class="h3 lc-title">Can I import?</h3><p>Yes. Drag files in.</p>', out); self.assertNotIn('<details', out, 'every answer is on the page, open')
        self.assertIn('<span class="lc-tag">&lt;30s</span><h3 class="h3 lc-title">Average redesign</h3>', out); self.assertIn('class="sec faq band-paper lc lc-ledger"', out); self.assertIn('class="sec numbers band-alt lc lc-bento"', out)
        words = lambda html: sorted(re.sub(r'<[^>]+>', ' ', re.sub(r'<style.*?</style>', '', html, flags=re.S)).split()); self.assertEqual(words(out), words(SMALL_PAGE.replace('<br>', ' ')))


class Validator(unittest.TestCase):
    def test_a_good_document_may_be_drawn(self):
        self.assertEqual(codes(doc(LEDGER, BENTO)), []); self.assertEqual(codes(doc({'section': 'feat', 'form': 'stagger', 'cols': 3})), [])

    def test_structure_and_no_field_for_words(self):
        for bad in ({}, {'ir': '0.2'}, {'ir': '0.2', 'lists': []}, {'ir': '9', 'lists': [LEDGER]}, {'ir': '0.2', 'lists': [LEDGER], 'extra': 1}): self.assertEqual(codes(bad), ['IL001'], bad)
        self.assertEqual(codes(doc(dict(LEDGER, items=[{'title': 'We are the best'}]))), ['IL011'])
        self.assertEqual(codes(doc(dict(LEDGER, heading='A better heading'))), ['IL011']); self.assertEqual(codes(doc(dict(LEDGER, colour='#f00'))), ['IL001'])

    def test_only_lists_of_this_page_once_each(self):
        self.assertEqual(codes(doc(dict(LEDGER, section='nowhere'))), ['IL010']); self.assertEqual(codes(doc(dict(LEDGER, section='jelovnik'))), ['IL010'], 'a price ledger is not a list')
        self.assertEqual(codes(doc(LEDGER, dict(LEDGER, form='stagger'))), ['IL010'])

    def test_forms_and_their_parameters_come_from_the_vocabulary(self):
        for field, value in (('form', 'carousel'), ('head', 'right'), ('numerals', 'roman'), ('title', 'xl')): self.assertEqual(codes(doc(dict(LEDGER, **{field: value}))), ['IL020'], field)
        self.assertEqual(codes(doc(dict(LEDGER, cols=3))), ['IL020'], 'cols belongs to the staggered form'); self.assertEqual(codes(doc({'section': 'feat', 'form': 'stagger', 'cols': 5})), ['IL020'])
        self.assertEqual(codes(doc(dict(BENTO, feature=len(NUMS['items'])))), ['IL020']); self.assertEqual(codes(doc(dict(LEDGER, feature=0))), ['IL020'])

    def test_forms_that_a_list_cannot_carry(self):
        self.assertEqual(codes(doc(dict(BENTO, head='left'))), ['IL021'])
        self.assertEqual(codes(doc({'section': 'feat', 'form': 'stagger', 'cols': 3, 'head': 'left'})), ['IL021'])
        short = re.sub(r'((?:<li class="index-row">.*?</li>){2})(?:<li class="index-row">.*?</li>)*(</ol>)', r'\1\2', PAGE, count=1, flags=re.S)
        self.assertEqual(len(read('feat', short)['items']), 2)
        self.assertEqual(codes(doc({'section': 'feat', 'form': 'bento'}), short), ['IL021']); self.assertEqual(codes(doc(dict(LEDGER, head='sticky')), short), ['IL021'])

    def test_tags_that_are_facts_are_never_hidden(self):
        self.assertEqual(codes(doc({'section': 'nums', 'form': 'ledger', 'numerals': 'none'})), ['IL022'])
        self.assertEqual(codes(doc(dict(LEDGER, numerals='none'))), [], '01, 02 … are numbering and may go')
        self.assertTrue(LISTS.numbering(FEAT['items'])); self.assertFalse(LISTS.numbering(NUMS['items']), 'a card that says 39 states a fact even though it is two digits')
        self.assertFalse(LISTS.numbering([{'tag': '02'}, {'tag': '03'}])); self.assertTrue(LISTS.numbering([{'tag': '1'}, {'tag': ''}, {'tag': '03'}]))


class Renderer(unittest.TestCase):
    def test_same_items_same_order_same_heading_and_the_rest_of_the_page_untouched(self):
        page, report = LISTS.transplant(PAGE, doc(LEDGER, BENTO)); again, _ = LISTS.transplant(PAGE, doc(LEDGER, BENTO))
        self.assertTrue(report['drawn'], report['errors']); self.assertEqual(page, again); self.assertEqual(report['sections'], ['feat', 'nums'])
        for sid, before in (('feat', FEAT), ('nums', NUMS)):
            section = page[{s['id']: s for s in SECTIONS.sections(page)}[sid]['span'][0]:{s['id']: s for s in SECTIONS.sections(page)}[sid]['span'][1]]
            self.assertIn(before['head'], section, 'the heading block is the page\'s own, byte for byte')
            titles = [re.sub(r'<[^>]+>', '', t) for t in re.findall(r'<h3 class="h3 lc-title">(.*?)</h3>', section)]
            self.assertEqual(titles, [LISTS.e(i['title']) for i in before['items']])
            for item in before['items']: self.assertIn(f'<p>{LISTS.e(item["body"])}</p>', section)
            self.assertIn(f'id="{sid}"', section); self.assertIn(f'band-{before["band"]}', section); self.assertIn(' lc lc-', section)
            self.assertTrue(section.endswith(before['tail'] + '</section>'), 'what the section holds after its list is kept, byte for byte')
            self.assertEqual(section.count('<div'), section.count('</div>'), 'the section is balanced')
        self.assertEqual(page.count('id="lc-css"'), 1)
        untouched = [s for s in SECTIONS.sections(PAGE) if s['id'] not in ('feat', 'nums')]
        for s in untouched: self.assertIn(PAGE[s['span'][0]:s['span'][1]], page, s['id'])

    def test_buttons_and_source_links_under_a_list_stay_in_its_section(self):
        extras = '<div class="wrap section-extras"><div class="section-actions"><a class="btn" href="https://example.test/register">Create account <span class="ar">→</span></a></div></div><aside class="source-actions"><ul><li><a href="https://example.test/help">Help ↗</a></li></ul></aside>'
        start, end = BY_ID['feat']['span']; page = PAGE[:end - len('</section>')] + extras + PAGE[end - len('</section>'):]
        self.assertTrue(read('feat', page)['tail'].endswith(extras))
        out, report = LISTS.transplant(page, doc(LEDGER)); self.assertTrue(report['drawn'], report['errors'])
        section = out[{s['id']: s for s in SECTIONS.sections(out)}['feat']['span'][0]:{s['id']: s for s in SECTIONS.sections(out)}['feat']['span'][1]]
        self.assertIn(extras, section); self.assertEqual(len(re.findall(r'<a ', out)), len(re.findall(r'<a ', page)), 'no link of the page is lost')
        stray = PAGE[:BY_ID['feat']['span'][0]] + PAGE[BY_ID['feat']['span'][0]:end].replace('<div class="gh', '<p>A sentence nobody expected.</p><div class="gh', 1) + PAGE[end:]
        self.assertEqual(codes(doc(LEDGER), stray), ['IL010'], 'a section with something this reader cannot place is not recomposed at all')

    def test_a_refused_document_leaves_the_page_untouched(self):
        page, report = LISTS.transplant(PAGE, doc(dict(LEDGER, items=[])))
        self.assertEqual(page, PAGE); self.assertFalse(report['drawn']); self.assertEqual(report['errors'][0]['code'], 'IL011')

    def test_the_bento_leaves_no_cell_empty(self):
        for count in range(3, 13):
            for feature in (0, count // 2, count - 1):
                spans = LISTS._spans(count, feature); self.assertEqual(spans[feature], (4, 2))
                self.assertEqual(sum(w * h for w, h in spans) % 6, 0, f'{count} items, feature {feature}: every row of the six-column grid is full')
        html, _ = LISTS.transplant(PAGE, doc(BENTO))
        self.assertEqual(html.count('class="lc-item lc-feature"'), 1); self.assertEqual(html.count('class="lc-item'), len(NUMS['items']))
        self.assertNotIn('lc-ordinal"', html, 'a list of facts features its fact')
        numbered, _ = LISTS.transplant(PAGE, doc({'section': 'feat', 'form': 'bento'}))
        self.assertIn(' lc-ordinal"', numbered, 'in a numbered list the featured tile is led by its title: a large "01" says nothing')

    def test_numerals_and_heads_are_drawn_as_asked(self):
        page, report = LISTS.transplant(PAGE, doc(dict(LEDGER, numerals='none', head='left')))
        self.assertTrue(report['drawn'], report['errors']); self.assertIn('lc-head-left', page); self.assertNotIn('class="lc-tag"', page)
        page, _ = LISTS.transplant(PAGE, doc({'section': 'nums', 'form': 'stagger', 'cols': 3, 'numerals': 'outline'}))
        self.assertIn('lc-n-outline', page); self.assertIn('style="--n:3"', page)
        for item in NUMS['items']: self.assertIn(f'<span class="lc-tag">{LISTS.e(item["tag"])}</span>', page)

    def test_everything_drawn_is_escaped(self):
        hostile = copy.deepcopy(FEAT); hostile['items'][0].update(title='<script>alert(1)</script>', body='"quoted" & <b>bold</b>', tag='<i>', link={'href': 'https://example.test/?a=1&b="2"', 'label': '<u>more</u>'})
        html = LISTS.render_section(BY_ID['feat'], hostile, LEDGER)
        self.assertNotIn('<script>', html); self.assertNotIn('<b>bold', html); self.assertNotIn('<u>', html); self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
        self.assertIn('href="https://example.test/?a=1&amp;b=&quot;2&quot;"', html)

    def test_nothing_is_drawn_with_a_property_the_measuring_tools_switch_off(self):
        self.assertEqual(re.findall(r'(?<![\w-])(transform|filter|clip-path|opacity)\s*:', LISTS.CSS), [])
        self.assertIn("'stagger-in'(el)", (ROOT / 'lib' / 'motion' / 'moves.js').read_text(), 'the one move a list asks for exists in the page\'s motion library')


class Model:
    def __init__(self, *answers): self.answers = list(answers); self.seen = []
    def __call__(self, system, content, tool, model=None, max_tokens=None):
        self.seen.append(content); return self.answers.pop(0) if self.answers else None
    def text(self, call): return '\n'.join(b['text'] for b in self.seen[call] if b.get('type') == 'text')


class Loop(unittest.TestCase):
    def setUp(self):
        from PIL import Image
        self.temp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.temp, True); self.page = os.path.join(self.temp, 'page.html'); Path(self.page).write_text(PAGE)
        shot = os.path.join(self.temp, 'shot.jpg'); Image.new('RGB', (64, 40), '#ccc').save(shot)
        self.readings = []
        for module, target, stand_in in ((COMPOSE, 'section_shots', lambda path, ids: {i: shot for i in ids}), (COMPOSE.HERO, 'measured', lambda path: dict(self.readings.pop(0)) if self.readings else {})):
            patcher = patch.object(module, target, stand_in); patcher.start(); self.addCleanup(patcher.stop)
    def go(self, *answers, **kw):
        model = Model(*answers); return COMPOSE.compose(PAGE, self.page, ask=model, **kw), model

    def test_the_brief_names_every_list_and_the_tool_has_no_field_for_words(self):
        text, ids = COMPOSE.brief(PAGE)
        self.assertEqual(ids, ['feat', 'how', 'nums']); self.assertIn('▸ "feat" — indexlist', text); self.assertIn('(facts: cannot be hidden)', text); self.assertIn('"how" — ladder', text)
        fields = json.dumps(COMPOSE.TOOL['input_schema'])
        for forbidden in ('"text"', '"href"', '"label"', '"html"', '"items": {"type": "string"', '"heading"'): self.assertNotIn(forbidden, fields)

    def test_a_good_answer_is_looked_at_and_a_valid_revision_replaces_it(self):
        result, model = self.go({'concept': 'Hollow numerals down the page.', 'lists': [LEDGER, BENTO]}, {'concept': 'The same, the ledger heading on top.', 'lists': [dict(LEDGER, head='top'), BENTO]})
        self.assertTrue(result['drawn']); self.assertEqual(result['doc']['note'], 'The same, the ledger heading on top.'); self.assertEqual(result['attempts'], 2)
        self.assertIn('YOUR LISTS, AS DRAWN', model.text(1)); self.assertEqual(sum(1 for b in model.seen[1] if b.get('type') == 'image'), sum(1 for b in model.seen[0] if b.get('type') == 'image') + 2)
        self.assertEqual(sorted(os.listdir(self.temp)), ['page.html', 'shot.jpg'])

    def test_a_refused_answer_goes_back_once_with_the_reasons(self):
        result, model = self.go({'concept': 'x', 'lists': [dict(BENTO, head='left')]}, {'concept': 'Fixed.', 'lists': [BENTO]}, review=False)
        self.assertIn('IL021', model.text(1)); self.assertTrue(result['drawn']); self.assertEqual(result['doc']['note'], 'Fixed.')
        result, model = self.go({'concept': 'x', 'lists': [dict(BENTO, head='left')]}, {'concept': 'x', 'lists': [dict(BENTO, head='left')]}, {'concept': 'never asked', 'lists': [BENTO]}, review=False)
        self.assertFalse(result['drawn']); self.assertEqual(len(model.seen), 2)

    def test_lists_that_break_the_page_are_not_shipped(self):
        self.readings = [{}, {'mobile-no-overflow': 'a tile runs past the screen'}, {'mobile-no-overflow': 'a tile runs past the screen'}]
        result, model = self.go({'concept': 'a', 'lists': [BENTO]}, {'concept': 'b', 'lists': [BENTO]})
        self.assertIn('mobile-no-overflow', model.text(1)); self.assertFalse(result['drawn']); self.assertEqual(result['log'][-1]['stage'], 'refuse')

    def test_what_the_template_already_breaks_is_not_blamed_on_the_lists(self):
        self.readings = [{'h2-short': 'a long heading'}, {'h2-short': 'a long heading'}]
        result, _ = self.go({'concept': 'a', 'lists': [LEDGER]}, review=False)
        self.assertTrue(result['drawn']); self.assertEqual(result['measured'], {})

    def test_a_page_without_lists_asks_nobody(self):
        bare = PAGE
        for sid in ('nums', 'how', 'feat'): bare = bare[:{s['id']: s for s in SECTIONS.sections(bare)}[sid]['span'][0]] + bare[{s['id']: s for s in SECTIONS.sections(bare)}[sid]['span'][1]:]
        model = Model({'concept': 'x', 'lists': [LEDGER]})
        result = COMPOSE.compose(bare, self.page, ask=model)
        self.assertFalse(result['drawn']); self.assertEqual(model.seen, [])


if __name__ == '__main__':
    unittest.main()
