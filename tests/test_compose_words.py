"""Sections that are words only — a price ledger, a menu, a paragraph under its heading — as compositions: read off the
page whole, drawn in a form of their own with the same words, and chosen by a model that is held to what the render
measures. No network, no model: the model is a stand-in function and the browser tools are patched."""
import json, os, re, shutil, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'compose'))
import compose_words as COMPOSE
import sections as SECTIONS
import words as WORDS

ROWS = ''.join(f'<li><span class="ledger-item">Dish {n}</span><i></i><b>{n},50 €</b></li>' for n in range(1, 6))
MENU = ('<section class="sec ledger band-paper" id="menu"><div class="wrap two no-visual"><div class="ledger-intro"><span class="lab">The menu</span><h2 class="h2" style="--lw:6">From the sea</h2><p class="lede">Cooked the way it was.</p></div>'
        f'<div><ul class="rows">{ROWS}</ul><div class="ctas"><a class="btn" href="https://example.test/menu">See the menu <span class="ar">→</span></a></div></div></div>'
        '<aside class="wrap source-actions"><div><ul><li><a href="https://example.test/pdf">The menu as a PDF ↗</a></li></ul></div></aside></section>')
NOTE = ('<section class="sec photo band-alt" id="note"><div class="wrap"><div class="photo-caption"><span class="lab">Take away</span><h2 class="h2">Take it home</h2><p class="cap">Everything on the menu, to go.</p>'
        '<div class="ctas"><a class="btn" href="https://example.test/go">Order</a></div></div></div></section>')
PAGE = ('<html><head><style>:root{--paper:#ffffff;--container:1300px;--frame:40px}</style></head><body><section class="sec hero" id="top"><h1>Hello</h1></section>' + MENU + NOTE
        + '<section class="sec cta band-dark" id="go"><div class="wrap"><div><h2 class="h2">Book</h2><p>Now.</p></div></div></section></body></html>')
def doc(*entries): return {'ir': '0.2', 'words': [dict(e) for e in entries]}
def codes(document, page=PAGE): return sorted({e['code'] for e in WORDS.validate(document, page)})
COLUMNS = {'section': 'menu', 'form': 'columns', 'title': 'xl'}
STATEMENT = {'section': 'note', 'form': 'statement', 'ground': 'accent'}
POSTER = {'section': 'menu', 'form': 'poster', 'side': 'left', 'ground': 'ink'}


class Reading(unittest.TestCase):
    def test_a_ledger_is_its_heading_block_and_what_the_heading_introduces(self):
        menu = SECTIONS.from_words(MENU); self.assertEqual((menu['kind'], menu['band'], menu['heading'], menu['rows'], menu['buttons']), ('words', 'paper', 'From the sea', 5, 1))
        self.assertTrue(menu['head'].startswith('<div class="ledger-intro">')); self.assertTrue(menu['body'].startswith('<div><ul class="rows">')); self.assertEqual(MENU.count(menu['head'] + menu['body']), 1)
        self.assertTrue(MENU.endswith(menu['tail'] + '</section>')); self.assertIn('The menu as a PDF', menu['tail'])

    def test_one_block_is_split_at_its_own_heading(self):
        note = SECTIONS.from_words(NOTE); self.assertEqual(note['holder'], ['photo-caption']); self.assertTrue(note['head'].endswith('</h2>')); self.assertTrue(note['body'].startswith('<p class="cap">'))

    def test_what_is_not_words_only_is_refused(self):
        for broken in (MENU.replace('sec ledger', 'sec cta'), MENU.replace('sec ledger', 'sec indexlist'), MENU.replace('sec ledger', 'sec hero'), MENU.replace('<ul class="rows">', '<img src="data:image/png;base64,AA"><ul class="rows">'),
                       MENU.replace('<ul class="rows">', '<ul class="rows" data-sig="pinned">'), MENU.replace('<div class="wrap two no-visual">', '<div class="wrap">loose words'), MENU.replace('<h2 class="h2" style="--lw:6">From the sea</h2>', ''),
                       NOTE.replace('<p class="cap">Everything on the menu, to go.</p><div class="ctas"><a class="btn" href="https://example.test/go">Order</a></div>', '')):
            with self.assertRaises(ValueError): SECTIONS.from_words(broken)
        drawn, report = WORDS.transplant(PAGE, doc(COLUMNS)); self.assertTrue(report['drawn'])
        self.assertIsInstance(WORDS.readable(drawn)['menu'][1], str, 'a composed section is not composed again'); self.assertIsInstance(WORDS.readable(PAGE)['go'][1], str)


class Validation(unittest.TestCase):
    def test_the_three_forms_validate(self):
        for entry in (COLUMNS, STATEMENT, POSTER): self.assertEqual(WORDS.validate(doc(entry), PAGE), [], entry)

    def test_one_defect_per_code(self):
        self.assertEqual(codes({'ir': '0.2', 'words': []}), ['IW001']); self.assertEqual(codes(doc({**COLUMNS, 'colour': 'red'})), ['IW001'])
        for field in ('heading', 'rows', 'text', 'href'): self.assertEqual(codes(doc({**COLUMNS, field: 'New'})), ['IW011'], field)
        self.assertEqual(codes(doc({**COLUMNS, 'section': 'nope'})), ['IW010']); self.assertEqual(codes(doc(COLUMNS, POSTER)), ['IW010']); self.assertEqual(codes(doc({**COLUMNS, 'section': 'go'})), ['IW010'])
        for change in ({'form': 'grid'}, {'title': 'huge'}, {'ground': 'pink'}, {'side': 'left'}): self.assertEqual(codes(doc({**COLUMNS, **change})), ['IW020'], change)
        self.assertEqual(codes(doc({**STATEMENT, 'form': 'columns'})), ['IW021'], 'two columns want rows'); self.assertEqual(codes(doc({**COLUMNS, 'form': 'statement'})), ['IW021'], 'a statement is short')
        self.assertEqual(codes(doc({**STATEMENT, 'ground': 'alt'})), ['IW021'], 'it already stands on that ground')
        long = PAGE.replace('From the sea', 'Extraordinarily Mediterranean'); self.assertEqual(codes(doc({**STATEMENT, 'section': 'menu', 'form': 'poster', 'title': 'xl'}), long.replace('--container:1300px', '--container:700px')), ['IW044'])


class Drawing(unittest.TestCase):
    text = staticmethod(lambda html: ' '.join(re.sub(r'<[^>]+>', ' ', re.sub(r'<style.*?</style>', '', html, flags=re.S)).split()))
    def test_the_section_says_what_it_said_and_keeps_its_id_its_links_and_what_followed(self):
        out, report = WORDS.transplant(PAGE, doc(POSTER, STATEMENT)); self.assertTrue(report['drawn'], report['errors']); self.assertEqual(report['sections'], ['menu', 'note'])
        self.assertEqual(self.text(out), self.text(PAGE)); self.assertEqual(sorted(re.findall(r'href="([^"]+)"', out)), sorted(re.findall(r'href="([^"]+)"', PAGE)))
        menu = SECTIONS.from_words(MENU); self.assertIn(f'<div class="wc-head">{menu["head"]}</div><div class="wc-body" data-move="fade-rise">{menu["body"]}</div></div>{menu["tail"]}</section>', out)
        self.assertIn('<section class="sec ledger wc wc-f-poster wc-t-lg wc-g-ink wc-grounded wc-side-left" id="menu" data-wc="0.2" data-form="poster">', out, 'a new ground replaces the band it stood on')
        self.assertIn('<section class="sec photo wc wc-f-statement wc-t-lg wc-g-accent wc-grounded" id="note"', out); self.assertIn('<div class="wc-head photo-caption">', out); self.assertEqual(out.count('id="wc-css"'), 1)
        self.assertEqual(out, WORDS.transplant(PAGE, doc(POSTER, STATEMENT))[0]); kept = WORDS.transplant(PAGE, doc(COLUMNS))[0]; self.assertIn('class="sec ledger band-paper wc wc-f-columns wc-t-xl"', kept)

    def test_a_refused_document_leaves_the_page_untouched(self):
        out, report = WORDS.transplant(PAGE, doc({**COLUMNS, 'form': 'statement'})); self.assertIs(out, PAGE); self.assertFalse(report['drawn'])

    def test_the_look_at_rest_uses_nothing_the_measuring_tools_switch_off(self):
        for banned in ('transform:', 'filter:', 'clip-path:', 'opacity:'): self.assertNotIn(banned, WORDS.CSS, banned)


def answer(*entries): return {'concept': 'A rhythm of quiet and loud.', 'words': [dict(e) for e in entries]}


class Loop(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.dir, True); self.path = os.path.join(self.dir, 'page.html'); Path(self.path).write_text(PAGE, encoding='utf-8')
        self.asked = []; self.contract = lambda path: {}
        for target, name, stand_in in ((COMPOSE.HERO, 'measured', lambda path: self.contract(path)), (COMPOSE.LISTED, 'section_shots', lambda path, ids: {})):
            p = patch.object(target, name, stand_in); p.start(); self.addCleanup(p.stop)
    def run_(self, *answers, review=False):
        queue = list(answers)
        def ask(system, content, tool, **kw): self.asked.append(content); return queue.pop(0) if queue else None
        return COMPOSE.compose(PAGE, self.path, ask=ask, review=review)
    said = lambda self, n: '\n'.join(b.get('text', '') for b in self.asked[n] if b.get('type') == 'text')

    def test_the_model_is_told_what_each_section_holds(self):
        text, ids = COMPOSE.brief(PAGE); self.assertEqual(ids, ['menu', 'note']); self.assertIn('▸ "menu" — ledger, on the paper band. Heading: "From the sea". ', text); self.assertIn('5 rows, 1 button(s)', text); self.assertIn('"go" — cta, on the dark ground', text); self.assertIn('Three or more neighbours on one ground', COMPOSE.SYSTEM)

    def test_a_valid_answer_is_the_document_and_a_side_on_another_form_is_not_part_of_it(self):
        result = self.run_(answer(COLUMNS, {**STATEMENT, 'side': 'left'})); self.assertTrue(result['drawn']); self.assertEqual(result['doc']['words'], [COLUMNS, STATEMENT]); self.assertEqual(result['attempts'], 1)

    def test_asking_for_the_ground_a_section_already_stands_on_is_asking_for_nothing(self):
        result = self.run_(answer({**STATEMENT, 'ground': 'alt'})); self.assertTrue(result['drawn']); self.assertNotIn('ground', result['doc']['words'][0]); self.assertEqual(len(self.asked), 1)

    def test_the_pages_direction_is_the_first_thing_the_model_reads(self):
        queue = [answer(COLUMNS)]
        def ask(system, content, tool, **kw): self.asked.append(content); return queue.pop(0)
        COMPOSE.compose(PAGE, self.path, ask=ask, review=False, direction='Loud type; one dark pause.')
        self.assertTrue(self.asked[0][0]['text'].startswith("THE PAGE'S DIRECTION")); self.assertIn('Loud type; one dark pause.', self.asked[0][0]['text']); self.assertIn('▸ "menu"', self.asked[0][1]['text'])

    def test_an_entry_still_refused_costs_its_own_section_not_the_others(self):
        wrong = {'section': 'note', 'form': 'columns'}   # two columns want rows; this section has none
        result = self.run_(answer(COLUMNS, wrong), answer(COLUMNS, wrong)); self.assertTrue(result['drawn']); self.assertEqual(result['doc']['words'], [COLUMNS]); self.assertEqual(result['log'][-1], {'stage': 'prune', 'errors': [], 'dropped': ['note']})

    def test_the_validators_reasons_go_back_once(self):
        result = self.run_(answer({**COLUMNS, 'form': 'statement'}), answer(COLUMNS)); self.assertTrue(result['drawn']); self.assertIn('IW021', self.said(1))
        self.asked.clear(); self.assertFalse(self.run_(answer({**COLUMNS, 'form': 'statement'}), answer({**COLUMNS, 'form': 'statement'}))['drawn']); self.assertEqual(len(self.asked), 2)

    def test_a_worse_revision_is_not_kept_and_a_broken_page_is_not_shipped(self):
        self.contract = lambda path: {'desktop-page-length': '17 screens'} if 'data-form="poster"' in Path(path).read_text(encoding='utf-8') else {}
        result = self.run_(answer(COLUMNS), answer(POSTER), review=True); self.assertEqual(result['doc']['words'], [COLUMNS]); self.assertIn('AS DRAWN', self.said(1))
        self.contract = lambda path: {'desktop-contrast': 'Dish 1'} if 'wc-g-ink' in Path(path).read_text(encoding='utf-8').split('</head>')[1] else {}
        refused = self.run_(answer(POSTER)); self.assertFalse(refused['drawn']); self.assertEqual(refused['log'][-1]['stage'], 'refuse')

    def test_sections_that_cannot_be_measured_are_not_shipped_and_a_page_without_any_asks_nobody(self):
        def broken(path): raise RuntimeError('no browser')
        self.contract = broken; self.assertFalse(self.run_(answer(COLUMNS))['drawn'])
        self.asked.clear(); bare = PAGE.replace(MENU, '').replace(NOTE, ''); self.assertFalse(COMPOSE.compose(bare, self.path, ask=lambda *a, **k: self.asked.append(1), review=False)['drawn']); self.assertEqual(self.asked, [])


if __name__ == '__main__': unittest.main()
