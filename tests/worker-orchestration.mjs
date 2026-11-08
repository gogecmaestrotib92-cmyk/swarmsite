import assert from 'node:assert/strict';import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import crypto from 'node:crypto';import vm from 'node:vm';import {prepareAlternative,publishSelected,verifySelected,verifyAlternative} from '../server/variant_snapshot.mjs';
const root=process.env.SWARM_VARIANT_ROOT||process.cwd(),source=fs.readFileSync(path.join(root,'server/index.mjs'),'utf8'),a=source.indexOf('async function process_(job)'),z=source.indexOf('\nasync function loop()',a);assert.ok(a>=0&&z>a);
const inputs=['direction.json','images.json','assets.json','inventory.json','brief.json','hero.mp4'],engine=['lib/render/render_bp.py','lib/templates/recipes.py','lib/visual_quality.py','lib/visual_semantics.py','lib/colour/palette.py','lib/colour_policy.py','lib/motion/moves.js','lib/motion/swarm.js'];const sha=f=>fs.existsSync(f)?crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'):null;
async function scenario({best='cerebrium',failFirst=false,failAltUpload=false,stale=false}){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'variant-worker-')),objects=new Map(),published=[];let result,jobDir;
 const upload=async(file,key)=>{if(failAltUpload&&key.includes('/bp-'))throw Error('access denied');objects.set(key,fs.readFileSync(file));published.push(key)};
 const makeManifest=(dir,bp,out)=>({fingerprints:{inputs:Object.fromEntries(inputs.map(n=>[n,sha(path.join(dir,n))])),engine:Object.fromEntries([...engine,`lib/blueprints/${bp}.bp.json`].map(n=>[n,sha(path.join(root,n))]))},html:sha(out)});
 const run=async(_bin,args)=>{
  if(args[0]==='lib/pipeline/capture.mjs'){const jobRoot=args[args.indexOf('--out')+1];jobDir=path.join(jobRoot,'site');fs.mkdirSync(jobDir,{recursive:true});fs.writeFileSync(path.join(jobDir,'inventory.json'),'{}');fs.writeFileSync(path.join(jobDir,'images.json'),'[]');return ''}
  if(args[0]==='-I')return '{}';
  if(args[0]==='lib/swarm/site_map.py')return JSON.stringify({analysis:{total:1,completed:1,complete:true}});
  if(args[0]==='-c')return '{"what":"test","n":0}';
  if(args[0]==='lib/direct/direct.py'){fs.writeFileSync(path.join(jobDir,'direction.json'),JSON.stringify({kind:'software',blueprint:'butter',hero:{h1:'old'},beats:[]}));return ''}
  if(args[0]==='experiments/design-patterns/verify_selected.py')return '';
  if(args[0]==='lib/render/render_bp.py'){const folder=args[1],bp=args[2],out=args[3];if(failFirst&&folder===jobDir&&bp==='butter')throw Error('render failed');const d=JSON.parse(fs.readFileSync(path.join(folder,'direction.json')));fs.writeFileSync(out,`<html><body>${bp}:${d.hero.h1}</body></html>`);if(stale&&folder!==jobDir)fs.appendFileSync(path.join(jobDir,'images.json'),' ');return ''}
  if(args[0]==='lib/swarm/run.py'){const out=args[args.indexOf('--out')+1];const d=JSON.parse(fs.readFileSync(path.join(jobDir,'direction.json')));d.hero.h1='FINAL';d.blueprint=best;fs.writeFileSync(path.join(jobDir,'direction.json'),JSON.stringify(d));fs.writeFileSync(out,`<html><body>${best}:FINAL</body></html>`);fs.writeFileSync(path.join(jobDir,'coverage.json'),JSON.stringify({scope:'single_page_preview',sections:[],routes:[]}));return JSON.stringify({done:{best_blueprint:best,render_manifest:makeManifest(jobDir,best,out),rounds:1}})}
  if(args[0]==='lib/qa/check.py')return 'QA score 100';throw Error('unexpected run '+args[0])
 };
 const appCtx={fs,path,OUT:temp,ROOT:root,process,console,slugOf:()=> 'site',setStep:async()=>{},run,emit:async()=>{},eventsCapture:()=>[],eventsDiagnose:()=>[],eventsDirect:()=>[],eventsRender:()=>[],eventsQA:()=>[],upload,J:f=>{try{return JSON.parse(fs.readFileSync(f,'utf8'))}catch{return null}},BP:{software:['butter','cerebrium','deepbook'],service:['lpas']},prepareAlternative,publishSelected,verifySelected,verifyAlternative,SELF:'https://api.test',uploadArtefacts:async()=>true,drainEvents:async()=>{},checkpointCrawl:async()=>{},updateWithRetry:async(_j,patch)=>{if(patch.status==='done')result=patch.result}};
 vm.runInNewContext(source.slice(a,z)+'\nglobalThis.work=process_',appCtx);const job={id:'11111111-1111-4111-8111-111111111111',url:'https://example.com',options:{},steps:[]};
 try{await appCtx.work(job);return {result,objects,published}}finally{fs.rmSync(temp,{recursive:true,force:true})}
}
let x=await scenario({});assert.deepEqual([...x.result.blueprints],['cerebrium','butter']);let v=new URL(x.result.previewUrl).searchParams.get('v'),base=`11111111-1111-4111-8111-111111111111/v-${v}`;assert.equal(x.objects.get(`${base}/index.html`).toString(),'<html><body>cerebrium:FINAL</body></html>');assert.equal(x.objects.get(`${base}/bp-butter.html`).toString(),'<html><body>butter:FINAL</body></html>');
x=await scenario({failAltUpload:true});assert.deepEqual([...x.result.blueprints],['cerebrium']);assert.equal(x.published.filter(k=>k.includes('/bp-')).length,0);
x=await scenario({failFirst:true});assert.deepEqual([...x.result.blueprints],['cerebrium']);assert.equal(x.published.filter(k=>k.includes('/bp-')).length,0);
await assert.rejects(()=>scenario({stale:true}),/changed/);
console.log('Worker orchestration: winner identity, final snapshot alternative, upload failure, initial render failure and stale assets pass');
