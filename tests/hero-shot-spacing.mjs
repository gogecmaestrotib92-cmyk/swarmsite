import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {spawnSync} from 'node:child_process';
import {fileURLToPath, pathToFileURL} from 'node:url';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'swarm-hero-shot-gap-'));
const b=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||undefined});
const blueprintFiles=fs.readdirSync(path.join(root,'lib/blueprints')).filter(x=>x.endsWith('.bp.json'));
let covered=new Set(),cases=0;
try{
 for(const variant of ['default','centre']){
  const dir=path.join(tmp,variant);fs.mkdirSync(dir);
  for(const name of ['direction','images','inventory','assets']) fs.copyFileSync(path.join(root,'tests',`${name}.sample.json`),path.join(dir,`${name}.json`));
  const direction=JSON.parse(fs.readFileSync(path.join(dir,'direction.json')));
  direction.kind='software';direction.hero.ui={...direction.hero.ui};
  if(variant==='centre')direction.hero.ui.move='centre';else delete direction.hero.ui.move;
  fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(direction));
  for(const file of blueprintFiles){
   const bp=file.replace('.bp.json',''),html=path.join(dir,bp+'.html');
   const render=spawnSync(process.env.PYTHON||'python3',[path.join(root,'lib/render/render_bp.py'),dir,bp,html],{cwd:root,encoding:'utf8'});
   assert.equal(render.status,0,`${bp}: ${render.stderr}`);
   for(const width of [320,390,900,1440]){
    const p=await b.newPage({viewport:{width,height:900}});await p.goto(pathToFileURL(html).href+'?nomotion=1',{waitUntil:'load'});
    const result=await p.locator('#top').evaluate(el=>{let c=el.querySelector('.ctas'),i=el.querySelector('.shotwrap img');if(!c||!i)return null;const a=c.getBoundingClientRect(),z=i.getBoundingClientRect();return {gap:z.top-a.bottom,loaded:i.complete&&i.naturalWidth>0,overflow:document.documentElement.scrollWidth>innerWidth};});
    if(result){cases++;covered.add(bp);assert.ok(result.loaded,`${bp}/${variant}/${width} image missing`);assert.equal(result.overflow,false,`${bp}/${variant}/${width} overflow`);assert.ok(result.gap>=22,`${bp}/${variant}/${width} CTA-image gap ${result.gap}`);if(width===1440)assert.ok(Math.abs(result.gap-37)<1,`${bp}/${variant} desktop spacing changed: ${result.gap}`)}
    await p.close();
   }
  }
 }
 assert.equal(covered.size,blueprintFiles.length,'at least one actual shot hero per blueprint');
 console.log(`CTA-to-shot spacing verified in ${cases} real browser cases across ${covered.size} blueprints`);
}finally{await b.close();fs.rmSync(tmp,{recursive:true,force:true})}
