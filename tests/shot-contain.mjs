import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'shot-contain-')); let browser;
try{
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox']});
 const gen=await browser.newPage();const images=await gen.evaluate(()=>{
  function make(id,w,h,shot){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,w,h);x.fillStyle='#c00';x.fillRect(0,0,20,h);x.fillStyle='#00c';x.fillRect(w-20,0,20,h);x.fillStyle='#008000';x.fillRect(0,0,w,20);x.fillStyle='#ee0';x.fillRect(0,h-20,w,20);x.fillStyle='#333';x.font='40px sans-serif';x.fillText(id,40,70);return {id,w,h,shot,detail:true,data:c.toDataURL('image/png')}}
  return [make('wide',1200,300,true),make('portrait',1000,2200,true),make('photo',1200,300,false),make('hero',1200,800,false)];
 });await gen.close();
 const d=JSON.parse(fs.readFileSync('tests/direction.sample.json'));d.kind='software';d.hero.media='hero';d.beats=images.filter(it=>it.id!=='hero').map(it=>({id:`beat-${it.id}`,type:'features',h2:`${it.id} lead`,features:[{title:'One',body:'Description'},{title:'Two',body:'Another'}],image:it.id,ui:{move:'cards',lead:it.id}}));
 fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));fs.writeFileSync(path.join(dir,'images.json'),JSON.stringify(images));
 const html=path.join(dir,'page.html');const run=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,'butter',html],{encoding:'utf8'});assert.equal(run.status,0,run.stderr);
 for(const width of [1440,390]){const p=await browser.newPage({viewport:{width,height:844},reducedMotion:'reduce'});await p.route(/^https?:\/\//,r=>r.abort());await p.goto(`${pathToFileURL(html)}?nomotion=1`);
  for(const id of ['wide','portrait']){const f=p.locator(`#beat-${id} figure.lead-shot`);assert.equal(await f.count(),1,`${id} screenshot lead exists`);const v=await f.evaluate(f=>{const i=f.querySelector('img'),r=i.getBoundingClientRect(),fr=f.getBoundingClientRect(),s=getComputedStyle(i);return {natural:[i.naturalWidth,i.naturalHeight],size:[r.width,r.height],inside:r.left>=fr.left&&r.right<=fr.right&&r.top>=fr.top&&r.bottom<=fr.bottom,fit:s.objectFit,radius:getComputedStyle(f).borderRadius}});
   assert.ok(v.inside,`${id} image must be entirely within the frame`);assert.equal(v.fit,'contain');assert.equal(v.radius,'0px',`${id} corners are not clipped`);assert.ok(v.size[0]<=v.natural[0]+.01&&v.size[1]<=v.natural[1]+.01,`${id} is not upscaled`);assert.ok(Math.abs(v.size[0]/v.size[1]-v.natural[0]/v.natural[1])<.01,`${id} keeps intrinsic aspect ratio`);assert.ok(v.size[0]>0&&v.size[1]>0);}
  const photo=p.locator('#beat-photo figure.lead');assert.equal(await photo.count(),1,'photo lead exists');assert.equal(await photo.getAttribute('class'),'lead');assert.equal(await photo.locator('img').evaluate(el=>getComputedStyle(el).objectFit),'cover');const ratio=await photo.evaluate(el=>{const r=el.getBoundingClientRect();return r.width/r.height});assert.ok(Math.abs(ratio-2.4)<.02,'photo retains existing crop behavior');
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth),width);await p.close();
 }
 console.log('Wide and portrait UI screenshots are fully visible without upscaling; photographs keep their crop');
}finally{if(browser)await browser.close();fs.rmSync(dir,{recursive:true,force:true})}
