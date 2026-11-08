"""Blueprint contrast/layout contract comparison (no production writes)."""
import concurrent.futures,json,os,shutil,subprocess,tempfile
from pathlib import Path
root=Path.cwd();candidate=Path(os.environ.get('SWARM_RENDER_ROOT',root));fixture=Path(os.environ.get('CAL_ARTIFACT_DIR',root/'tests'));real='CAL_ARTIFACT_DIR' in os.environ
with tempfile.TemporaryDirectory(prefix='swarm-blueprint-colour-contract-') as tmp:
 tmp=Path(tmp);bps=sorted(p.name[:-8] for p in (root/'lib/blueprints').glob('*.bp.json'))
 if not bps: raise RuntimeError('blueprint catalog must not be empty')
 jobs=[]
 for bp in bps:
  for label,renderer in [('base',root/'lib/render/render_bp.py'),('candidate',candidate/'lib/render/render_bp.py')]:
   folder=tmp/(bp+'-'+label);folder.mkdir();(folder/'brief.json').write_text('{"keepColours":false}')
   for n in ('direction','images','assets','inventory'):
    src=fixture/(f'{n}.json' if real else f'{n}.sample.json')
    if src.is_file():shutil.copy(src,folder/f'{n}.json')
   out=folder/'render.html';r=subprocess.run([os.environ.get('PYTHON','python3'),str(renderer),str(folder),bp,str(out)],cwd=root,capture_output=True,text=True)
   if r.returncode:raise RuntimeError(f'{bp} {label} render: {r.stderr[-300:]}')
   jobs.append((bp,label,folder,out))
 def check(job):
  bp,label,folder,out=job;env={**os.environ,'LIVETEST':'1'}
  r=subprocess.run(['node','lib/qa/contract.mjs',str(out),'--dir',str(folder)],cwd=root,capture_output=True,text=True,timeout=90,env=env)
  if r.returncode:raise RuntimeError(f'{bp} {label} contract: {r.stderr[-500:]}')
  rep=json.loads((folder/'contract.json').read_text());return bp,label,rep['score'],[x['id'] for x in rep['failed']]
 results={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for bp,label,score,fail in pool.map(check,jobs):results.setdefault(bp,{})[label]=(score,fail)
 any_new=False
 for bp in bps:
  before,after=results[bp]['base'],results[bp]['candidate'];added=sorted(set(after[1])-set(before[1]));print(bp,'before',before,'after',after,'new',added,flush=True);any_new|=bool(added)
 if any_new:raise SystemExit('New contract failures detected; see above')
 print(f'{len(bps)} blueprints: no new contract failure IDs versus baseline')
