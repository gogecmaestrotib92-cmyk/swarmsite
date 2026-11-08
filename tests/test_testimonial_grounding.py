import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('director', ROOT / 'lib/direct/direct.py')
director = importlib.util.module_from_spec(spec)
spec.loader.exec_module(director)
sys.path.insert(0, str(ROOT / 'lib/swarm'))
import agents


class TestimonialGrounding(unittest.TestCase):
    def setUp(self):
        self.good = lambda text, name, link: {'status': 'candidate', 'text': text, 'attribution': name, 'links': [{'label':'Read original', 'url':link}]}
        self.inv = {'sourceCoverage': {'sections': [
            {'id':'home-11', 'title':'Customer reviews', 'testimonials':[
                self.good('First original review.', 'Pat', 'https://reviews.example/first'),
                self.good('Second original review.', 'Pat', 'https://reviews.example/second'),
                {'status':'candidate', 'text':'Unknown author', 'attribution':'', 'links':[]},
                {'status':'candidate', 'text':'Truncated...', 'attribution':'Lin', 'links':[], 'textTruncated':True},
                {'status':'candidate', 'text':'Ambiguous', 'attribution':'Q', 'links':[{'url':'https://one.test/','label':'One'}, {'url':'https://two.test/','label':'Two'}]},
                self.good('Attack.', 'Bad', 'javascript:alert(1)'),
            ]},
        ]}}
        self.doc = {'beats':[{'id':'reviews', 'type':'quote', 'source_sections':['home-11'], 'body':'First original review.', 'who':'Pat'}]}

    def test_only_complete_pairs_in_source_order_and_no_author_dedup(self):
        director.ground_testimonials(self.doc,self.inv)
        b=self.doc['beats'][0]
        self.assertEqual(b['type'],'testimonials')
        self.assertEqual([q['text'] for q in b['testimonials']],['First original review.','Second original review.'])
        self.assertEqual([q['attribution'] for q in b['testimonials']],['Pat','Pat'])
        self.assertEqual([q['links'][0]['url'] for q in b['testimonials']],['https://reviews.example/first','https://reviews.example/second'])
        self.assertNotIn('body',b)
        self.assertTrue(self.doc['audit_notes'])

    def test_verified_quote_with_other_source_is_preserved_and_homepage_recovered(self):
        self.doc['beats'][0]['source_sections']=['home-other']
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(self.doc['beats'][0]['type'],'quote')
        self.assertEqual(self.doc['beats'][1]['source_sections'],['home-11'])

    def test_incomplete_source_review_and_unverified_model_quote_are_omitted(self):
        self.inv['sourceCoverage']['sections'][0]['testimonials']=[{'status':'candidate','text':'Truncated','attribution':'Pat','links':[],'textTruncated':True}]
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(len(self.doc['beats']),0)
        self.assertIn('omitted',self.doc['audit_notes'][0])

    def test_unmatched_model_quote_is_omitted_then_source_quotes_added(self):
        self.doc['beats'][0]['body']='A different original quote.'
        self.doc['beats'][0]['who']='Other person'
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['testimonials'])
        self.assertEqual(len(self.doc['beats'][0]['testimonials']),2)
        self.assertTrue(any('omitted' in note and 'review' in note for note in self.doc['audit_notes']))

    def test_same_quote_from_different_author_does_not_replace_existing(self):
        self.doc['beats'][0]['who']='Another Pat'
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['testimonials'])

    def test_different_punctuation_is_not_treated_as_the_same_quote(self):
        self.doc['beats'][0]['body']='First original review?'
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['testimonials'])

    def test_unverified_quote_headline_is_removed_but_visual_is_retained(self):
        self.doc['beats'][0].update({'big':'A distinct claim', 'image':'source-photo'})
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['quote','testimonials'])
        self.assertNotIn('big', self.doc['beats'][0])
        self.assertEqual(self.doc['beats'][0]['image'],'source-photo')

    def test_first_quote_with_action_is_not_replaced_by_grid(self):
        self.doc['beats'][0].update({'cta':'Read story','cta_href':'https://example.test/story'})
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['quote','testimonials'])
        self.assertEqual(self.doc['beats'][0]['cta_href'],'https://example.test/story')

    def test_unidentified_fabricated_quote_is_omitted_and_audited(self):
        self.doc['beats'][0].update({'source_sections':[], 'body':'Fabricated quote.', 'who':'Imagined person'})
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['testimonials'])
        self.assertNotIn('Fabricated quote.', repr(self.doc['beats']))
        self.assertEqual(len(self.doc['beats'][0]['testimonials']), 2)
        self.assertIn('omitted',self.doc['audit_notes'][0])

    def test_recovers_homepage_sections_even_when_director_did_not_select_quotes(self):
        self.inv['sourceCoverage']['sections'].append({'id':'home-12', 'title':'More voices', 'testimonials':[
            self.good('A distinct source quotation.', 'Jordan', 'https://reviews.example/third')]})
        self.inv['sourcePages'] = [{'sections':[{'id':'sub-1','title':'Unselected subpage','testimonials':[
            self.good('Only on a subpage.', 'Other', 'https://reviews.example/subpage')]}]}]
        self.doc = {'beats':[{'id':'features','type':'features'}, {'id':'questions','type':'faq'}]}
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['id'] for b in self.doc['beats']],['features','source-reviews-home-11','source-reviews-home-12','questions'])
        self.assertEqual([b['source_sections'] for b in self.doc['beats'][1:3]],[['home-11'],['home-12']])
        self.assertEqual([q['text'] for q in self.doc['beats'][1]['testimonials']],['First original review.','Second original review.'])
        self.assertNotIn('Only on a subpage.',repr(self.doc['beats']))
        snapshot=repr(self.doc); director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(repr(self.doc),snapshot)

    def test_incomplete_hidden_and_unsafe_homepage_candidates_are_audited(self):
        self.inv['sourceCoverage']['sections'][0]['testimonials'] = [
            {'status':'candidate','text':'Hidden','attribution':'Author','links':[],'hidden':True},
            {'status':'candidate','text':'Not visible','attribution':'Author','links':[],'visible':False},
            {'status':'candidate','text':'Hidden for accessibility','attribution':'Author','links':[],'ariaHidden':True},
            {'status':'candidate','text':'Truncated','attribution':'Author','links':[],'textTruncated':True},
            self.good('Unsafe','Author','javascript:alert(1)')]
        self.doc = {'beats':[{'id':'features','type':'features'}]}
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['id'] for b in self.doc['beats']],['features'])
        self.assertTrue(any('incomplete' in n for n in self.doc['audit_notes']))

    def test_multiple_homepage_sections_share_one_remaining_slot_without_losing_pairs(self):
        self.inv['sourceCoverage']['sections'].append({'id':'home-12','title':'More voices','testimonials':[
            self.good('A distinct source quotation.','Jordan','https://reviews.example/third')]})
        self.doc={'beats':[{'id':f'feature-{i}','type':'features'} for i in range(47)]}
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(len(self.doc['beats']),48)
        b=self.doc['beats'][-1]
        self.assertEqual(b['source_sections'],['home-11','home-12'])
        self.assertEqual([q['text'] for q in b['testimonials']],['First original review.','Second original review.','A distinct source quotation.'])
        snapshot=repr(self.doc); director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(repr(self.doc),snapshot)

    def test_no_room_does_not_drop_existing_sections_and_is_explicit(self):
        self.doc={'beats':[{'id':f'feature-{i}','type':'features'} for i in range(48)]}
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(len(self.doc['beats']),48)
        self.assertEqual([b['id'] for b in self.doc['beats']],[f'feature-{i}' for i in range(48)])
        self.assertTrue(any('no room' in n for n in self.doc['audit_notes']))
        snapshot=repr(self.doc); director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(repr(self.doc),snapshot)

    def test_group_with_missing_source_keeps_available_quotes_and_flags_gap(self):
        self.doc={'beats':[{'id':'group','type':'testimonials','source_sections':['home-11','gone'],'testimonials':[]}]}
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(self.doc['beats'][0]['source_sections'],['home-11'])
        self.assertEqual(len(self.doc['beats'][0]['testimonials']),2)
        self.assertTrue(any('incomplete or unavailable' in n for n in self.doc['audit_notes']))
        snapshot=repr(self.doc);director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(repr(self.doc),snapshot)

    def test_real_quote_is_preserved_even_without_section_reference(self):
        self.doc['beats'][0]['source_sections']=[]
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['testimonials'])
        self.assertEqual(self.doc['beats'][0]['testimonials'][0]['text'],'First original review.')
        self.assertEqual(self.doc['beats'][0]['testimonials'][0]['attribution'],'Pat')

    def test_quote_without_section_is_preserved_when_it_has_independent_content(self):
        self.doc['beats'][0].update({'source_sections':[],'h2':'A distinct headline', 'cta':'Read story'})
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['quote','testimonials'])
        self.assertEqual(self.doc['beats'][0]['h2'],'A distinct headline')

    def test_repeated_guard_is_idempotent_and_repairs_tampered_grid(self):
        director.ground_testimonials(self.doc,self.inv)
        self.doc['beats'][0]['testimonials'][0]['text']='Fabricated overwrite'
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(len(self.doc['beats']),1)
        self.assertEqual(self.doc['beats'][0]['testimonials'][0]['text'],'First original review.')
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(len(self.doc['beats']),1)

    def test_old_direction_with_unverified_quote_and_existing_grid_is_cleaned_once(self):
        self.doc['beats'] = [
            {'id':'old','type':'quote','source_sections':['home-11'],'body':'Fabricated text.','who':'Imaginary author'},
            {'id':'source-reviews-home-11','type':'testimonials','source_sections':['home-11'],'testimonials':[self.good('Fabricated','Writer','https://example.test/')]},
        ]
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['testimonials'])
        self.assertEqual(len(self.doc['beats'][0]['testimonials']),2)
        cleaned = repr(self.doc)
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(repr(self.doc),cleaned)

    def test_duplicate_exact_verified_quote_is_removed_beside_source_grid(self):
        self.doc['beats'].append({'id':'reviews-duplicate','type':'quote','source_sections':['home-11'],
                                  'body':'First original review.','who':'Pat'})
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['testimonials'])
        self.assertEqual(len(self.doc['beats'][0]['testimonials']),2)
        snapshot = repr(self.doc)
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(repr(self.doc),snapshot)

    def test_duplicate_with_extra_content_or_a_linked_anchor_is_preserved(self):
        for name, value in [('h2','More about Pat'), ('lede','A distinct explanation.'),
                            ('image','source-image'), ('cta','Read their story'),
                            ('label','A separate label'), ('big','First original')]:
            with self.subTest(field=name):
                doc = {'beats':[self.doc['beats'][0].copy(),
                        {'id':'reviews-duplicate','type':'quote','source_sections':['home-11'],
                         'body':'First original review.','who':'Pat',name:value}]}
                director.ground_testimonials(doc,self.inv)
                self.assertEqual([b['type'] for b in doc['beats']],['testimonials','quote'])
                self.assertEqual(doc['beats'][1][name],value)
        doc = {'nav':{'links':[['#reviews-duplicate','Customer']]},
               'beats':[self.doc['beats'][0].copy(),
                        {'id':'reviews-duplicate','type':'quote','source_sections':['home-11'],
                         'body':'First original review.','who':'Pat'}]}
        director.ground_testimonials(doc,self.inv)
        self.assertEqual([b['type'] for b in doc['beats']],['testimonials','quote'])

    def test_quote_anchor_references_from_any_content_are_not_deleted(self):
        for location in ('hero-primary', 'hero-secondary', 'section', 'nav', 'ending', 'relative', 'absolute'):
            with self.subTest(location=location):
                doc = {'hero':{}, 'nav':{'links':[]}, 'ending':{}, 'beats':[
                    self.doc['beats'][0].copy(),
                    {'id':'reviews-duplicate','type':'quote','source_sections':['home-11'],
                     'body':'First original review.','who':'Pat'},
                    {'id':'feature', 'type':'features'}]}
                if location == 'hero-primary': doc['hero']['cta_href'] = '#reviews-duplicate'
                if location == 'hero-secondary': doc['hero']['cta2_href'] = '#reviews-duplicate'
                if location == 'section': doc['beats'][-1]['cta_href'] = '#reviews-duplicate'
                if location == 'nav': doc['nav']['links'] = [['#reviews-duplicate','Customer']]
                if location == 'ending': doc['ending']['cols'] = [['Read', [['#reviews-duplicate','Customer']]]]
                if location == 'relative': doc['hero']['cta_href'] = './#reviews-duplicate'
                if location == 'absolute': doc['hero']['cta_href'] = 'https://example.test/path#reviews-duplicate'
                director.ground_testimonials(doc,self.inv)
                self.assertEqual([b['id'] for b in doc['beats']],['reviews','reviews-duplicate','feature'])
                self.assertEqual(doc['beats'][1]['type'],'quote')
                snapshot=repr(doc);director.ground_testimonials(doc,self.inv)
                self.assertEqual(repr(doc),snapshot)

    def test_bare_verified_quote_without_source_keeps_referenced_anchor(self):
        self.doc['hero']={'cta_href':'#reviews'}
        self.doc['beats'][0]['source_sections']=[]
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['quote','testimonials'])
        self.assertEqual(self.doc['beats'][0]['id'],'reviews')

    def test_percent_encoded_fragment_protects_target(self):
        self.doc['nav']={'links':[['#reviews%2Dduplicate','Customer']]}
        self.doc['beats'].append({'id':'reviews-duplicate','type':'quote','source_sections':['home-11'],
                                  'body':'First original review.','who':'Pat'})
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['id'] for b in self.doc['beats']],['reviews','reviews-duplicate'])

    def test_duplicate_identification_includes_author_and_source_section(self):
        # Same quote by another source-attributed author is a distinct pair.
        self.inv['sourceCoverage']['sections'][0]['testimonials'].append(
            self.good('First original review.','Another Pat','https://reviews.example/another'))
        self.doc['beats'].append({'id':'another','type':'quote','source_sections':['home-11'],
                                  'body':'First original review.','who':'Another Pat'})
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual([b['type'] for b in self.doc['beats']],['testimonials'])
        self.assertEqual([v['attribution'] for v in self.doc['beats'][0]['testimonials']],['Pat','Pat','Another Pat'])

    def test_verified_quote_copy_cannot_be_rewritten(self):
        self.doc['beats'][0].update({'source_sections':[], 'big':'First original'})
        director.ground_testimonials(self.doc,self.inv)
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory,'direction.json', {'hero':{}, **self.doc})
            before=agents.J(directory,'direction.json')
            agents.apply_copy(directory, {'edits':[{'path':'reviews.big','value':'Fabricated'}, {'path':'reviews.body','value':'Fake claim'}]})
            self.assertEqual(agents.J(directory,'direction.json'),before)

    def test_forty_eight_beat_limit_is_preserved(self):
        self.doc['beats'] += [{'id':f'f{i}', 'type':'features'} for i in range(47)]
        self.doc['beats'][0]['image']='source-photo'
        director.ground_testimonials(self.doc,self.inv)
        self.assertEqual(len(self.doc['beats']),48)
        self.assertTrue(any('no room' in note for note in self.doc['audit_notes']))

    def test_copy_agent_cannot_modify_grounded_testimonials(self):
        director.ground_testimonials(self.doc,self.inv)
        with tempfile.TemporaryDirectory() as directory:
            agents.W(directory,'direction.json', {'hero':{}, **self.doc})
            before=agents.J(directory,'direction.json')
            agents.apply_copy(directory, {'edits':[{'path':'reviews.h2','value':'Changed'}, {'path':'reviews.body','value':'Invented'}]})
            self.assertEqual(agents.J(directory,'direction.json'),before)

if __name__ == '__main__': unittest.main()
