import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'/'swarm'))
import agents

class ReaderSourceContextTests(unittest.TestCase):
    def test_large_map_keeps_every_page_and_marks_shortened_evidence(self):
        pages = [{'url': f'https://example.test/{i}', 'copy': {'text': 'a' * 5000},
                  'sections': [{'id': f'p{i}', 'title': f'Topic {i}', 'text': 'b' * 2000}]} for i in range(60)]
        pages[-1]['sections'][0]['text'] = 'LAST PAGE EVIDENCE'
        result = agents.model_pages({'sourcePages': pages})
        self.assertEqual(len(result), 60)
        self.assertEqual(result[-1]['sections'][0]['text'], 'LAST PAGE EVIDENCE')
        self.assertTrue(result[0]['copy']['textTruncated'])
        self.assertTrue(result[0]['sections'][0]['textTruncated'])
        self.assertEqual(len(pages[0]['copy']['text']), 5000, 'source evidence remains intact')

    def test_analysis_context_is_bounded_and_reports_omitted_observations(self):
        entries=[{'source_url':f'https://example.test/{i}','section_ids':[f's{i}'],'facts':['x'*2000]} for i in range(500)]
        state={'complete':True,'ordered_keys':['k'],'batches':{'k':{'observations':entries}}}
        result=agents.model_analysis(state)
        self.assertTrue(result['context_truncated'])
        self.assertEqual(result['observations_total'],500)
        self.assertEqual(result['observations_in_context'],300)
        self.assertEqual(result['observations'][-1]['source_url'],'https://example.test/499')

    def test_landing_scope_never_feeds_old_subpage_text_to_reader(self):
        with tempfile.TemporaryDirectory() as folder:
            agents.W(folder,'inventory.json',{'url':'https://example.test/', 'copy':{'text':'Landing content'},
                'sourceCoverage':{'scope':'landing_page_only','sections':[]},
                'sourcePages':[{'url':'https://example.test/sub','copy':{'text':'STALE SUBPAGE MATERIAL'}}]})
            with patch.object(agents,'ask',return_value=None) as call: agents.reader(folder)
            text='\n'.join(block['text'] for block in call.call_args.args[1] if block['type']=='text')
            self.assertIn('Landing content',text)
            self.assertNotIn('STALE SUBPAGE MATERIAL',text)

    def test_late_sampled_page_is_not_lost_to_serialized_text_cutoff(self):
        with tempfile.TemporaryDirectory() as folder:
            pages=[{'url':f'https://example.test/{i}','sections':[{'id':f'p{i}','title':f'Topic {i}','text':('important '*1500)}]} for i in range(8)]
            pages[-1]['sections'][0]['text']='LAST PAGE EVIDENCE'
            agents.W(folder,'inventory.json',{'sourcePages':pages,'sourceCoverage':{'sections':[],'routes':[{'url':'https://example.test/missing','status':'limit'}], 'routeLimit':8}})
            with patch.object(agents,'ask',return_value=None) as call:
                agents.reader(folder)
            text='\n'.join(x['text'] for x in call.call_args.args[1] if x['type']=='text')
            self.assertIn('LAST PAGE EVIDENCE',text)
            self.assertIn('CAPTURE COVERAGE',text)
            self.assertIn('https://example.test/missing',text)

if __name__=='__main__': unittest.main()
