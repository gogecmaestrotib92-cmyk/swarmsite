import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'section-actions-'));
let browser;
try {
 const d=JSON.parse(fs.readFileSync('tests/direction.sample.json'));
 delete d.lang;
 d.beats=[
  {id:'features-section',type:'features',h2:'Features',features:[{title:'Feature one',body:'A feature'},{title:'Feature two',body:'Another feature'}],cta:'Explore apps',cta_href:'https://example.com/apps',cta2:'API docs',cta2_href:'https://example.com/docs',ui:{move:'sticky-product'}},
  {id:'steps-section',type:'steps',h2:'Steps',steps:['Step one','Step two'],note:'No credit card required.',cta:'Host an event',cta_href:'https://example.com/event',ui:{move:'pinned-sequence'}},
  {id:'photo-section',type:'photo',h2:'A photo story',lede:'Photo introduction',cta:'Read story',cta_href:'https://example.com/story'},
  {id:'cells-section',type:'cells',h2:'Facts',cells:[['Numbers','25%','Growth'],['Info','Free','Unlimited']],cta:'Unknown action',cta_href:'https://unsafe.example/path'},
  {id:'facts-section',type:'facts',h2:'Facts two',facts:[['Customers','100']],cta:'Dangerous link',cta_href:'javascript:alert(1)'},
  {id:'ledger-section',type:'ledger',h2:'Prices',items:[['Basic','Free']],cta:'Get started',cta_href:'https://example.com/start'}
 ];
 const actions=[['Explore apps','apps'],['API docs','docs'],['Host an event','event'],['Read story','story'],['Get started','start']].map(([text,url])=>({text,href:`https://example.com/${url}`}));
 const inventory={lang:'es-ES',actions};
 fs.writeFileSync(path.join(tmp,'direction.json'),JSON.stringify(d));fs.writeFileSync(path.join(tmp,'inventory.json'),JSON.stringify(inventory));fs.writeFileSync(path.join(tmp,'images.json'),'[]');
 const ids=['aino','atelier','belgrade-arbor','butter','cerebrium','crav','deepbook','halfdays','lpas','tengile','units','white-desert'];
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH,args:['--no-sandbox']});
 for(const id of ids){
  const html=path.join(tmp,`${id}.html`);const result=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',tmp,id,html],{encoding:'utf8'});assert.equal(result.status,0,result.stderr);
  for(const [width,mode] of [[390,'reduce'],[1440,'no-preference']]){
   const page=await browser.newPage({viewport:{width,height:844},reducedMotion:mode});await page.route(/^https?:\/\//,r=>r.abort());await page.route('**/gsap.min.js', route => route.fulfill({path:'node_modules/gsap/dist/gsap.min.js',contentType:'application/javascript'}));await page.route('**/ScrollTrigger.min.js', route => route.fulfill({path:'node_modules/gsap/dist/ScrollTrigger.min.js',contentType:'application/javascript'}));await page.goto(`${pathToFileURL(html)}${mode === 'reduce' ? '?nomotion=1' : ''}`,{waitUntil:'load'});
   assert.equal(await page.locator('html').getAttribute('lang'),'es-ES',id);
   for(const [section,text,target] of [['features-section','Explore apps','apps'],['features-section','API docs','docs'],['steps-section','Host an event','event'],['photo-section','Read story','story'],['ledger-section','Get started','start']]){
    const link=page.locator(`#${section}`).getByRole('link',{name:text});assert.equal(await link.count(),1,`${id} ${section} ${text}`);assert.equal(await link.getAttribute('href'),`https://example.com/${target}`);assert.ok(await link.isVisible());await link.click({trial:true,timeout:3000});const box=await link.boundingBox();assert.ok(box&&box.x>=-1&&box.x+box.width<=width+1,`${id} ${width} ${text} clipped`);
   }
   assert.equal(await page.locator('#steps-section .section-note').innerText(),'No credit card required.');
   assert.equal(await page.getByRole('link',{name:'Unknown action'}).count(),0);assert.equal(await page.getByRole('link',{name:'Dangerous link'}).count(),0);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);await page.close();
  }
 }
 d.lang='sr-Latn';fs.writeFileSync(path.join(tmp,'direction.json'),JSON.stringify(d));let render=spawnSync('python3',['lib/render/render_bp.py',tmp,'aino',path.join(tmp,'lang.html')]);assert.equal(render.status,0);let output=fs.readFileSync(path.join(tmp,'lang.html'),'utf8');assert.match(output,/<html lang="sr-Latn">/);
 delete d.lang;inventory.lang='bad\" lang=\"x';fs.writeFileSync(path.join(tmp,'direction.json'),JSON.stringify(d));fs.writeFileSync(path.join(tmp,'inventory.json'),JSON.stringify(inventory));render=spawnSync('python3',['lib/render/render_bp.py',tmp,'aino',path.join(tmp,'lang.html')]);assert.equal(render.status,0);output=fs.readFileSync(path.join(tmp,'lang.html'),'utf8');assert.match(output,/<html><head>/);
 console.log('Verified source-backed section actions, notes, safe URLs and language across blueprints');
} finally {if(browser)await browser.close();fs.rmSync(tmp,{recursive:true,force:true})}
