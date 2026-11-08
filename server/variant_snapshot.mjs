import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import crypto from 'node:crypto';
const INPUTS=['direction.json','images.json','assets.json','inventory.json','brief.json','hero.mp4'];
const ENGINE=['lib/render/render_bp.py','lib/templates/recipes.py','lib/visual_quality.py','lib/visual_semantics.py','lib/colour/palette.py','lib/colour_policy.py','lib/motion/moves.js','lib/motion/swarm.js'];
const hash = f => fs.existsSync(f) && fs.statSync(f).isFile() ? crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex') : null;
const valid = s => typeof s === 'string' && /^[a-z0-9-]{2,24}$/.test(s);
const snapshot = (dir,root,bp) => ({inputs:Object.fromEntries(INPUTS.map(n=>[n,hash(path.join(dir,n))])),engine:Object.fromEntries([...ENGINE,`lib/blueprints/${bp}.bp.json`].map(n=>[n,hash(path.join(root,n))]))});
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function verifySelected({dir,root,bp,manifest,out}) {
 if(!valid(bp)||!manifest||!manifest.fingerprints||!manifest.html||!same(snapshot(dir,root,bp),manifest.fingerprints)||hash(out)!==manifest.html)throw new Error('selected render or inputs changed after review');
}
export async function prepareAlternative({dir,root,primary,alternate,manifest,out,run}) {
 verifySelected({dir,root,bp:primary,manifest,out});
 if(!valid(alternate)||alternate===primary)return null;
 const altPath=path.join(root,'lib/blueprints',`${alternate}.bp.json`);const altVersion=hash(altPath);if(!altVersion)return null;
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'swarm-variant-'));
 try {
  for(const name of INPUTS)if(manifest.fingerprints.inputs[name]!==null)fs.copyFileSync(path.join(dir,name),path.join(tmp,name));
  if(!same(snapshot(tmp,root,primary).inputs,manifest.fingerprints.inputs))throw new Error('variant snapshot differs from selected inputs');
  verifySelected({dir,root,bp:primary,manifest,out});
  const result=path.join(tmp,'alternative.html');
  if(process.env.SWARM_VERIFIED_PATTERNS==='1')await run('python3',['experiments/design-patterns/verify_selected.py',tmp,alternate],{timeoutMs:60000});
  await run('python3',['lib/render/render_bp.py',tmp,alternate,result],{timeoutMs:120000});
  if(hash(altPath)!==altVersion)throw new Error('alternative blueprint changed during render');
  verifySelected({dir,root,bp:primary,manifest,out});
  if(!same(snapshot(tmp,root,primary).inputs,manifest.fingerprints.inputs))throw new Error('variant snapshot changed during render');
  if(!hash(result))throw new Error('alternative render missing');
  const target=path.join(dir,`variant-${alternate}.html`);fs.copyFileSync(result,target);
  return {bp:alternate,path:target,html:hash(target),blueprint:altVersion};
 } finally {fs.rmSync(tmp,{recursive:true,force:true})}
}
export function verifyAlternative({root,alternate}) {
 if(!alternate||!valid(alternate.bp)||hash(alternate.path)!==alternate.html||hash(path.join(root,'lib/blueprints',`${alternate.bp}.bp.json`))!==alternate.blueprint)throw new Error('alternative changed after render');
}
export async function publishSelected({dir,root,primary,alternate,manifest,out,jobId,upload,makeVersion=()=>crypto.randomBytes(16).toString('hex')}) {
 verifySelected({dir,root,bp:primary,manifest,out});
 const version=makeVersion();if(!/^[0-9a-f]{32}$/.test(version))throw new Error('invalid version');
 const key=`${jobId}/v-${version}`;await upload(out,`${key}/index.html`,'text/html');
 const blueprints=[primary];
 if(alternate){
   verifyAlternative({root,alternate});
   verifySelected({dir,root,bp:primary,manifest,out});
   let uploaded=false;try{await upload(alternate.path,`${key}/bp-${alternate.bp}.html`,'text/html');uploaded=true}catch{}
   verifyAlternative({root,alternate});
   verifySelected({dir,root,bp:primary,manifest,out});if(uploaded)blueprints.push(alternate.bp);
 }

 verifySelected({dir,root,bp:primary,manifest,out});
 return {version,blueprints};
}
