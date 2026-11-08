import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'/'swarm'))
import agents

class LedgerLeadReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.dir=self.temp.name
        d=json.loads((ROOT/'tests/direction.sample.json').read_text());d['kind']='place';d['hero']['media']='waiter'
        d['beats']=[{'id':'menu','type':'ledger','h2':'Grilled meat','lede':'Beef and pork','items':[['Steak','20 €']], 'image':'screen', 'ui':{'lead':'long-table'}}]
        images=json.loads((ROOT/'tests/images.sample.json').read_text())[:2]
        screen=copy.deepcopy(images[1]);screen['id']='screen';screen['shot']=True;images.append(screen)
        agents.W(self.dir,'direction.json',d);agents.W(self.dir,'images.json',images)
    def tearDown(self):self.temp.cleanup()
    def render_has_lead(self):
        out=Path(self.dir)/'out.html';r=subprocess.run([sys.executable,str(ROOT/'lib/render/render_bp.py'),self.dir,'white-desert',str(out)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
        html=out.read_text();section=html.split('id="menu"',1)[1].split('</section>',1)[0];return 'ledger-visual' in section
    def test_fail_closed_and_content_binding(self):
        self.assertFalse(self.render_has_lead())
        with patch.object(agents,'ask',return_value={'decision':'MATCH','observed':'A plate of steak'}):self.assertEqual(agents.review_ledger_leads(self.dir),1)
        self.assertTrue(self.render_has_lead())
        d=agents.J(self.dir,'direction.json');d['beats'][0]['h2']='Seafood';agents.W(self.dir,'direction.json',d)
        self.assertFalse(self.render_has_lead(),'content changes invalidate approval')
        with patch.object(agents,'ask',return_value={'decision':'MISMATCH','observed':'A plate of steak'}):agents.review_ledger_leads(self.dir)
        self.assertFalse(self.render_has_lead())
    def test_empty_observation_cannot_approve(self):
        with patch.object(agents,'ask',return_value={'decision':'MATCH','observed':''}):agents.review_ledger_leads(self.dir)
        self.assertFalse(self.render_has_lead())
        self.assertEqual(agents.J(self.dir,'direction.json')['swarm']['ledger_lead_checks']['menu']['decision'],'UNCERTAIN')
    def test_oversized_context_is_not_partially_reviewed(self):
        d=agents.J(self.dir,'direction.json');d['beats'][0]['items']=[['item','1'] for _ in range(21)];agents.W(self.dir,'direction.json',d)
        with patch.object(agents,'ask') as call:agents.review_ledger_leads(self.dir)
        call.assert_not_called()
        self.assertFalse(self.render_has_lead())
    def test_photo_change_and_review_error_fail_closed(self):
        with patch.object(agents,'ask',return_value={'decision':'MATCH','observed':'match'}):agents.review_ledger_leads(self.dir)
        imgs=agents.J(self.dir,'images.json');imgs[1]['data']=imgs[0]['data'];agents.W(self.dir,'images.json',imgs)
        self.assertFalse(self.render_has_lead(),'image bytes changed')
        with patch.object(agents,'ask',side_effect=RuntimeError('unavailable')):agents.review_ledger_leads(self.dir)
        self.assertFalse(self.render_has_lead())

if __name__=='__main__':unittest.main()
