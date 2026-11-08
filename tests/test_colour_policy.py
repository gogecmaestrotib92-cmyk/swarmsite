import importlib.util,json,random,unittest,os,subprocess,tempfile,shutil
from pathlib import Path
s=importlib.util.spec_from_file_location('policy',Path(__file__).resolve().parents[1]/'lib/colour_policy.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
import os
root=Path(os.environ.get('SWARM_TEST_ROOT',Path(__file__).resolve().parents[1]))
class PolicyTest(unittest.TestCase):
 def verify(self,x):
  for a,b in [('paper','ink'),('paper','muted'),('alt','alt_ink'),('alt','alt_muted'),('accent','accent_ink'),('accent','accent_muted'),('button','button_ink'),('alt_button','alt_button_ink'),('accent_button','accent_button_ink'),('ink','paper'),('ink','dark_muted')]:self.assertGreaterEqual(m.contrast(x[a],x[b]),4.5,(a,b,x))
  self.assertGreaterEqual(m.contrast(x['button'],x['paper']),3)
  self.assertGreaterEqual(m.contrast(x['alt_button'],x['alt']),3)
  self.assertGreaterEqual(m.contrast(x['accent_button'],x['accent']),3)
 def test_all_blueprints(self):
  for f in sorted((root/'lib/blueprints').glob('*.bp.json')):
   bp=json.loads(f.read_text())['colour'];x=m.resolve(bp);self.verify(x)
   if m.norm(bp.get('paper')):self.assertEqual(x['paper'],m.norm(bp['paper']))
   if m.norm(bp.get('ink')) and m.contrast(x['paper'],m.norm(bp['ink']))>=4.5:self.assertEqual(x['ink'],m.norm(bp['ink']))
   if m.norm(bp.get('accent')):self.assertEqual(x['accent'],m.norm(bp['accent']))
 def test_butter_reference(self):
  bp=json.loads((root/'lib/blueprints/butter.bp.json').read_text())['colour'];b=m.resolve(bp);self.verify(b)
  self.assertEqual((b['paper'],b['ink'],b['accent']),('#FAFAFA','#353535','#353535'))
 def test_invalid_bp_neutral_and_invalid_input(self):
  for id in ('cerebrium','aino','deepbook'):
   bp=json.loads((root/f'lib/blueprints/{id}.bp.json').read_text())['colour'];x=m.resolve(bp);self.assertEqual(x['ink'],'#FFFFFF');self.assertIn('ink_contrast',x['fallback']);self.verify(x)
  for s in ('#888', '#ccc', '#333333'):
   x=m.resolve({'paper':'#fff','ink':'#000','accent':s});self.assertEqual(x['accent'],m.norm(s));self.assertEqual(len(set(m.rgb(x['accent']))),1);self.verify(x)
  x=m.resolve({'mode':'light','paper':'</style>','ink':'bad','accent':'red'});self.verify(x);self.assertEqual(x['paper'],'#FFFFFF')
 def test_invalid_blueprint_survives_real_renderer(self):
  candidate=Path(os.environ.get('SWARM_RENDER_ROOT',root))
  with tempfile.TemporaryDirectory() as temp:
   scratch=Path(temp);lib=scratch/'lib';lib.mkdir()
   for src in (candidate/'lib').iterdir():
    if src.name!='blueprints':(lib/src.name).symlink_to(src,target_is_directory=src.is_dir())
   (lib/'blueprints').mkdir();bp=json.loads((root/'lib/blueprints/butter.bp.json').read_text())
   bp['colour'].update(paper='#zzzzzz',ink='bad',accent='x;}</style><script>bad()</script>')
   (lib/'blueprints/butter.bp.json').write_text(json.dumps(bp))
   job=scratch/'job';job.mkdir()
   for name in ('direction','images','inventory','assets'):
    src=root/'tests'/f'{name}.sample.json'
    if src.is_file():shutil.copy(src,job/f'{name}.json')
   (job/'brief.json').write_text('{"keepColours":false}')
   out=job/'render.html';r=subprocess.run([os.environ.get('PYTHON','python3'),str(lib/'render/render_bp.py'),str(job),'butter',str(out)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr);html=out.read_text();self.assertIn('--paper:#FFFFFF;--ink:#000000;',html);self.assertNotIn('bad()</script>',html)
 def test_random_components(self):
  rng=random.Random(1032)
  for _ in range(3000):
   color=lambda:'#'+''.join(rng.choices('0123456789abcdef',k=6))
   self.verify(m.resolve({'paper':color(),'ink':color(),'accent':color(),'alt':color(),'mode':'light'}))
if __name__=='__main__':unittest.main()
