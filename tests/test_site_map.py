import json, sys, tempfile, unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'/'swarm'))
import site_map

class SiteMapTests(unittest.TestCase):
    def test_homepage_and_late_sections_are_included_in_batches(self):
        inv={'url':'https://example.test/','copy':{'text':'Home'},'sourceCoverage':{'sections':[{'id':f'h{i}','text':f'Evidence {i}'} for i in range(100)]},'sourcePages':[]}
        sections=[s for batch in site_map.batches(inv) for page in batch for s in page['sections']]
        self.assertEqual(len(sections),100)
        self.assertEqual(sections[-1]['id'],'h99')

    def test_landing_scope_does_not_analyze_stale_subpages(self):
        inv={'url':'https://example.test/','copy':{'text':'Landing'},
             'sourceCoverage':{'scope':'landing_page_only','sections':[{'id':'home-1','text':'Our actual service'}]},
             'sourcePages':[{'url':'https://example.test/other','copy':{'text':'Unrelated subpage'}}]}
        pages=[page for batch in site_map.batches(inv) for page in batch]
        self.assertEqual([page['url'] for page in pages],['https://example.test/'])

    def test_large_section_splits_evidence_without_losing_quotes_or_panels(self):
        section={'id':'home-1','text':'intro','testimonials':[{'text':str(i)+'x'*1900} for i in range(25)],
                 'panels':[{'text':str(i)+'y'*1900} for i in range(15)]}
        inv={'url':'https://example.test/','sourceCoverage':{'sections':[section]}}
        parts=[s for batch in site_map.batches(inv) for page in batch for s in page['sections']]
        self.assertGreater(len(parts),1)
        self.assertEqual(sum(len(p['testimonials']) for p in parts),25)
        self.assertEqual(sum(len(p['panels']) for p in parts),15)
        self.assertTrue(all(p['id']=='home-1' for p in parts))

    def test_batches_resume_and_reject_unknown_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            pages=[]
            for i in range(20):
                pages.append({'url':f'https://example.test/{i}','copy':{'text':'Source evidence. '*1000},'sections':[{'id':f's{i}','title':f'Topic {i}','text':'Full section text.'}]})
            Path(d,'inventory.json').write_text(json.dumps({'sourcePages':pages}))
            groups=site_map.batches({'sourcePages':pages}); self.assertGreater(len(groups),1)
            def answer(system,content,tool,**kwargs):
                kwargs['usage_callback'](SimpleNamespace(input_tokens=100,output_tokens=20))
                batch=json.loads(content[0]['text'].split('\n',1)[1])
                return {'observations':[{'source_url':p['url'],'section_ids':[s['id'] for s in p['sections']]+['made-up'],'facts':['Observed fact'],'uncertainties':[]} for p in batch]+[{'source_url':'https://wrong.test/','section_ids':[],'facts':['fake'],'uncertainties':[]}]}
            with patch.object(site_map.agents,'ask',side_effect=answer) as ask:
                first=site_map.run_next(d,3);self.assertEqual(first['completed'],3)
                while not first['completed']==first['total']: first=site_map.run_next(d)
                self.assertTrue(first['complete']); self.assertEqual(ask.call_count,len(groups))
                site_map.run_next(d);self.assertEqual(ask.call_count,len(groups),'resume must not repay completed batches')
            state=json.loads(Path(d,'site-analysis.json').read_text()); observations=[o for b in state['batches'].values() for o in b['observations']]
            from source_context import model_analysis
            self.assertEqual(model_analysis(state)['token_usage']['input_tokens'],100*len(groups))
            self.assertFalse(any(o['source_url']=='https://wrong.test/' or 'made-up' in o['section_ids'] for o in observations))
            self.assertEqual(len(observations),20)
    def test_missing_evidence_is_explicit_and_failure_saves_no_progress(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'inventory.json').write_text(json.dumps({'sourcePages':[{'url':'https://example.test/a','sections':[{'id':'s1','title':'Topic'}]}]}))
            with patch.object(site_map.agents,'ask',return_value={'observations':[]}): result=site_map.run_next(d)
            self.assertFalse(result['complete']);self.assertEqual(result['missing_pages'],1);self.assertEqual(result['missing_sections'],1)
        with tempfile.TemporaryDirectory() as d:
            Path(d,'inventory.json').write_text(json.dumps({'sourcePages':[{'url':'https://example.test/a'}]}))
            with patch.object(site_map.agents,'ask',return_value=None):
                with self.assertRaises(RuntimeError):site_map.run_next(d)
            self.assertFalse(Path(d,'site-analysis.json').exists())
    def test_parallel_batch_failure_preserves_other_completed_results(self):
        with tempfile.TemporaryDirectory() as d:
            pages=[{'url':f'https://example.test/{i}','copy':{'text':'x'*30000},'sections':[]} for i in range(3)]
            Path(d,'inventory.json').write_text(json.dumps({'sourcePages':pages}))
            def answer(system,content,tool,**kwargs):
                batch=json.loads(content[0]['text'].split('\n',1)[1]);url=batch[0]['url']
                if url.endswith('/0'):raise RuntimeError('temporary provider failure')
                return {'observations':[{'source_url':url,'section_ids':[],'facts':['Fact'],'uncertainties':[]}]}
            with patch.object(site_map.agents,'ask',side_effect=answer):
                with self.assertRaises(RuntimeError):site_map.run_next(d,3)
            self.assertEqual(json.loads(Path(d,'site-analysis.json').read_text())['completed'],2)
if __name__=='__main__':unittest.main()
