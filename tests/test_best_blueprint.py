import contextlib,importlib.util,io,json,sys,tempfile,unittest,shutil
from pathlib import Path
from unittest.mock import patch
root=Path.cwd();module=Path(__file__).resolve().parents[1]/'lib/swarm/run.py';sys.path.insert(0,str(root/'lib/swarm'));spec=importlib.util.spec_from_file_location('variant_run',module);run=importlib.util.module_from_spec(spec);spec.loader.exec_module(run);agents=run.A
class BestBlueprintTest(unittest.TestCase):
 def setUp(self):
  stage=patch.object(run.Patterns,'apply_verified_patterns',return_value={'choices':[],'reason':'stubbed'});stage.start();self.addCleanup(stage.stop)
 def execute(self,initial,alternative,scores):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);d=json.loads((root/'tests/direction.sample.json').read_text());d['blueprint']='butter';agents.W(t,'direction.json',d);agents.W(t,'factsheet.json',{});out=p/'render.html'; calls=[]
   def render(_folder,bp,file):calls.append(bp);Path(file).write_text('render:'+bp)
   def contract(folder,_file):result={'score':0,'failed':[]};agents.W(folder,'contract.json',result);return result
   it=iter(scores)
   def critique(*_a):return {'score':next(it),'fixes':[]}
   argv=['run.py',t,initial,'--alt',alternative,'--out',str(out),'--rounds',str(len(scores))];buff=io.StringIO()
   with patch.object(run.sys,'argv',argv),patch.object(run,'render',render),patch.object(run,'contract',contract),patch.object(run.C,'critique',critique),patch.object(run.Coverage,'write_coverage',side_effect=RuntimeError('unavailable')),patch.object(agents,'concept',return_value=0),patch.object(agents,'ux',return_value=0),patch.object(agents,'visual',return_value=0),patch.object(agents,'copy',return_value=0),patch.object(agents,'ui',return_value=0),contextlib.redirect_stdout(buff):run.main()
   messages=[json.loads(line) for line in buff.getvalue().splitlines()];done=next(m['done'] for m in messages if 'done'in m)
   return done,json.loads((p/'direction.json').read_text()),out.read_text(),calls
 def test_restart_wins(self):
  done,d,html,calls=self.execute('butter','cerebrium',[0,70]);self.assertEqual(calls,['butter','cerebrium']);self.assertEqual(done['best_blueprint'],'cerebrium');self.assertEqual(html,'render:cerebrium');self.assertEqual(d['blueprint'],'cerebrium')
 def test_rollback_to_original(self):
  done,d,html,calls=self.execute('butter','cerebrium',[0,0]);self.assertEqual(calls,['butter','cerebrium']);self.assertEqual(done['best_blueprint'],'butter');self.assertEqual(html,'render:butter');self.assertEqual(d['blueprint'],'butter')
 def test_real_render_manifest_survives_rollback(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);d=json.loads((root/'tests/direction.sample.json').read_text());d['blueprint']='butter';agents.W(t,'direction.json',d);agents.W(t,'factsheet.json',{});shutil.copy(root/'tests/images.sample.json',p/'images.json');out=p/'render.html';scores=iter([0,0]);buff=io.StringIO()
   def contract(folder,_file):result={'score':0,'failed':[]};agents.W(folder,'contract.json',result);return result
   def critique(*_a):return {'score':next(scores),'fixes':[]}
   argv=['run.py',t,'butter','--alt','cerebrium','--out',str(out),'--rounds','2']
   with patch.object(run.sys,'argv',argv),patch.object(run,'contract',contract),patch.object(run.C,'critique',critique),patch.object(run.Coverage,'write_coverage',side_effect=RuntimeError('unavailable')),patch.object(agents,'concept',return_value=0),patch.object(agents,'ux',return_value=0),patch.object(agents,'visual',return_value=0),patch.object(agents,'copy',return_value=0),patch.object(agents,'ui',return_value=0),contextlib.redirect_stdout(buff):run.main()
   done=next(m['done'] for m in map(json.loads,buff.getvalue().splitlines()) if 'done'in m)
   self.assertEqual(done['best_blueprint'],'butter');self.assertEqual(done['render_manifest']['html'],run.digest(str(out)));self.assertEqual(done['render_manifest']['fingerprints'],run.fingerprints(t,'butter'))
 def test_initial_fallback_identity_not_direction(self):
  done,d,html,calls=self.execute('cerebrium','butter',[80]);self.assertEqual(done['best_blueprint'],'cerebrium');self.assertEqual(d['blueprint'],'butter');self.assertEqual(html,'render:cerebrium')
if __name__=='__main__':unittest.main()
