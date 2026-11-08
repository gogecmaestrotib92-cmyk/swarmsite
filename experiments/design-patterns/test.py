import base64, copy, hashlib, importlib.util, io, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from PIL import Image, ImageDraw
P=Path(__file__).parent; ROOT=Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('catalog_check',P/'render_check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sys.path.insert(0, str(P)); import explore, choose_patterns

def image(id,shot=False,blank=False):
 im=Image.new('RGB',(1000,700),'white');
 if not blank: ImageDraw.Draw(im).rectangle((20 if shot else 450,30,400 if shot else 800,300),fill='#345c98')
 b=io.BytesIO();im.save(b,'PNG');return {'id':id,'w':1000,'h':700,'shot':shot,'detail':True,'src':'visual-shot' if shot else 'https://example.test/photo.jpg','data':'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()}
class CatalogTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.dir=Path(self.tmp.name)
  self.d=json.loads((ROOT/'tests/direction.sample.json').read_text());self.d['kind']='software';self.d['hero']['media']='hero';self.d['hero']['ui']={'move':'split'}
  self.d['beats']=[{'id':'target','type':'features','h2':'Product story','image':'shot','source_sections':['s1'],'cta':'Explore','cta_href':'https://source.example/docs','features':[{'title':'Feature one','body':'Useful detail one'},{'title':'Feature two','body':'Useful detail two'}],'ui':{'move':'cards','lead':''}},{'id':'other','type':'faq','h2':'Questions','items':[['Question?','Verified answer.']]}]
  self.imgs=[image('hero'),image('shot',True),image('blank',True,True)]
  self.inv={'actions':[{'text':'Explore','href':'https://source.example/docs'}],'sourceCoverage':{'sections':[{'id':'s1','title':'Original','headingLevel':'H2','kind':'section','sourceActionsVersion':1,'sourceActions':[{'label':'Original link','url':'https://source.example/original'}]}]}}
  self.save()
 def tearDown(self):self.tmp.cleanup()
 def save(self):
  for name,obj in [('direction',self.d),('images',self.imgs),('inventory',self.inv)]: (self.dir/f'{name}.json').write_text(json.dumps(obj))
 def call(self,kind='story-assigned-product-ui',version=1):return m.check(self.dir,'butter','target',kind,version)
 def test_story_and_source_not_modified(self):
  before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.dir.iterdir()};result=self.call();self.assertTrue(result['accepted'],result);self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.dir.iterdir()})
 def test_explore_lists_verified_options_and_preserves_inputs(self):
  before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.dir.iterdir()}; result=explore.explore(self.dir,'butter'); self.assertTrue(any(c['beat']=='target' and c['pattern']=='story-assigned-product-ui' and c['accepted'] for c in result['candidates'])); self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.dir.iterdir()})
  self.d['beats'].append(copy.deepcopy(self.d['beats'][0]));self.save()
  with self.assertRaises(ValueError):explore.explore(self.dir,'butter')
 def test_agent_can_only_choose_verified_options_and_stale_input_is_rejected(self):
  response={'choices':[{'beat':'target','pattern':'made-up','version':1},{'beat':'target','pattern':'story-assigned-product-ui','version':1}]}
  result=choose_patterns.select(self.dir,'butter',ask=lambda *a,**k:response)
  self.assertEqual(result['choices'],[{'beat':'target','pattern':'story-assigned-product-ui','version':1}])
  def mutate(*a,**k):
   (self.dir/'brief.json').write_text('{}');return response
  result=choose_patterns.select(self.dir,'butter',ask=mutate)
  self.assertEqual(result['choices'],[]);self.assertIn('changed',result['reason'])
 def test_multiple_choices_are_checked_against_the_updated_snapshot(self):
  self.d['beats'].insert(1,{'id':'proof','type':'facts','h2':'Proof','facts':[['10','Customers'],['20','Projects']],'ui':{'move':'cards'}});self.save()
  response={'choices':[{'beat':'target','pattern':'story-assigned-product-ui','version':1},{'beat':'proof','pattern':'marquee-short-facts','version':1}]}
  before=(self.dir/'direction.json').read_bytes();result=choose_patterns.select(self.dir,'butter',ask=lambda *a,**k:response)
  self.assertEqual(result['choices'],response['choices']);self.assertEqual((self.dir/'direction.json').read_bytes(),before)
 def test_preview_is_a_private_render_and_source_is_unchanged(self):
  response={'choices':[{'beat':'target','pattern':'story-assigned-product-ui','version':1}]}
  before=(self.dir/'direction.json').read_bytes();result=choose_patterns.select(self.dir,'butter',ask=lambda *a,**k:response,make_trial=True);trial=Path(result['trial_directory'])
  try:
   self.assertTrue((trial/'page.html').is_file()); self.assertEqual(json.loads((trial/'direction.json').read_text())['beats'][0]['ui']['move'],'story'); self.assertEqual((self.dir/'direction.json').read_bytes(),before)
  finally:shutil.rmtree(trial)
 def test_butter_editorial_five_items_and_wrong_blueprint(self):
  self.d['beats'][0]['features']=[{'title':f'Feature {i}','body':f'Detail {i}'} for i in range(5)];self.d['beats'][0]['lede']='A distinctive product story that explains the product clearly';self.save();r=self.call('butter-editorial-product');self.assertTrue(r['accepted'],r);self.assertFalse(m.check(self.dir,'cerebrium','target','butter-editorial-product',1)['accepted']);self.d['beats'][0]['features'] += [{'title':'Six','body':'Details'},{'title':'Seven','body':'Details'}];self.save();self.assertFalse(self.call('butter-editorial-product')['accepted'])
 def test_marquee_and_negative_conditions(self):
  self.d['beats'][0]={'id':'target','type':'facts','h2':'Proof','source_sections':['s1'],'facts':[['10','Customers'],['20','Projects']],'ui':{'move':'cards'}};self.save();self.assertTrue(self.call('marquee-short-facts')['accepted']);self.d['beats'][0]['facts']=[['a b c d e f','detail']];self.save();self.assertFalse(self.call('marquee-short-facts')['accepted']);self.d['beats'][0]['facts']=[[str(i),'x'] for i in range(11)];self.save();self.assertFalse(self.call('marquee-short-facts')['accepted'])
 def test_pinned_text_steps_reject_extra_actions_and_media(self):
  self.d['beats'][0]={'id':'target','type':'steps','h2':'How it works','steps':['Choose a time','Share the link','Meet your guests'],'ui':{'move':'cards','lead':''}};self.save();r=self.call('pinned-text-steps');self.assertTrue(r['accepted'],r)
  self.d['beats'][0]['cta']='Book';self.save();self.assertFalse(self.call('pinned-text-steps')['accepted']);del self.d['beats'][0]['cta'];self.d['beats'][0]['image']='shot';self.save();self.assertFalse(self.call('pinned-text-steps')['accepted']);del self.d['beats'][0]['image'];self.d['beats'][0]['source_sections']=['s1'];self.save();self.assertFalse(self.call('pinned-text-steps')['accepted'])
 def test_type_wall_preserves_quote_and_attribution(self):
  self.d['beats'][0]={'id':'target','type':'quote','body':'A thoughtful product gives people more time to do what matters most','who':'A real customer','ui':{'move':'auto'}};self.save();r=self.call('type-wall-quote');self.assertTrue(r['accepted'],r)
  self.d['beats'][0]['source_sections']=['s1'];self.save();self.assertFalse(self.call('type-wall-quote')['accepted']);del self.d['beats'][0]['source_sections'];self.d['beats'][0]['body']='Too short';self.save();self.assertFalse(self.call('type-wall-quote')['accepted'])
 def test_ledger_patterns_keep_extra_fields_and_source_actions(self):
  self.d['beats'][0]={'id':'target','type':'ledger','h2':'Menu','items':[['Soup','12','Fresh herbs'],['Fish','20','Grilled','Lemon']],'source_sections':['s1'],'ui':{'move':'auto'}};self.save();r=self.call('ledger-cards');self.assertTrue(r['accepted'],r)
  self.assertFalse(self.call('ledger-story')['accepted']);self.assertFalse(self.call('ledger-sticky')['accepted'])
  self.d['beats'][0]['items'][0]={'name':'Soup','price':'12'};self.save();self.assertFalse(self.call('ledger-cards')['accepted'])
 def test_sticky_requires_and_preserves_assigned_visual(self):
  r=self.call('sticky-assigned-visual');self.assertTrue(r['accepted'],r)
  self.d['hero']['media']='shot';self.save();self.assertFalse(self.call('sticky-assigned-visual')['accepted']);self.d['hero']['media']='hero';self.d['beats'][0]['image']='blank';self.save();self.assertFalse(self.call('sticky-assigned-visual')['accepted'])
 def test_unknown_wrong_kind_missing_blank_and_item_images(self):
  self.assertFalse(self.call(version=2)['accepted']);self.assertFalse(self.call('no-such-pattern')['accepted']);self.d['kind']='place';self.save();self.assertFalse(self.call()['accepted']);self.d['kind']='software';self.d['beats'][0]['image']='missing';self.save();self.assertFalse(self.call()['accepted']);self.d['beats'][0]['image']='blank';self.save();self.assertFalse(self.call()['accepted']);self.d['beats'][0]['image']='shot';self.d['beats'][0]['features'][0]['image']='hero';self.save();self.assertFalse(self.call()['accepted'])
 def test_ownership_conflict_fails_closed(self):
  self.d['hero']['media']='shot';self.save();r=self.call();self.assertFalse(r['accepted'],r)
 def test_rejects_marquee_with_assigned_image(self):
  self.d['beats'][0]={'id':'target','type':'facts','h2':'Proof','image':'shot','facts':[['10','Customers']],'ui':{'move':'cards'}};self.save();r=self.call('marquee-short-facts');self.assertFalse(r['accepted'],r)
 def test_rejects_mismatched_engine(self):
  checks=m.CATALOG['engine_file_sha256'];key=next(iter(checks));before=checks[key]
  try:
   checks[key]='bad';result=self.call();self.assertEqual(result['reason'],'engine revision mismatch; revalidate catalog')
  finally:checks[key]=before
 def test_runtime(self):
  stories=[]
  for move in ['story','marquee','pinned-sequence','type-wall','sticky-product']:
   d=copy.deepcopy(self.d)
   if move=='marquee':d['beats'][0]={'id':'target','type':'facts','h2':'Proof','source_sections':['s1'],'cta':'Explore','cta_href':'https://source.example/docs','facts':[['10','Customers'],['X'*100,'Projects']],'ui':{'move':'marquee'}}
   elif move=='pinned-sequence':d['beats'][0]={'id':'target','type':'steps','h2':'How it works','steps':['Choose a time','Share the link','Meet your guests'],'ui':{'move':move}}
   elif move=='type-wall':d['beats'][0]={'id':'target','type':'quote','body':'A thoughtful product gives people more time to do what matters most','who':'A real customer','ui':{'move':move}}
   else:d['beats'][0]['ui']['move']=move
   (self.dir/'direction.json').write_text(json.dumps(d));out=self.dir/f'{move}.html';r=subprocess.run([os.environ.get('PYTHON',sys.executable),str(ROOT/'lib/render/render_bp.py'),str(self.dir),'butter',str(out)],cwd=ROOT,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr);stories.append(out)
  r=subprocess.run(['node',str(P/'runtime.mjs'),*map(str,stories)],cwd=ROOT,capture_output=True,text=True,timeout=90);self.assertEqual(r.returncode,0,r.stderr)
if __name__=='__main__':unittest.main()
