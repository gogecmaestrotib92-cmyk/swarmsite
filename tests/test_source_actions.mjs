import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'swarm-source-actions-'));
const base=process.cwd();
const d=JSON.parse(fs.readFileSync('tests/direction.sample.json'));
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH || undefined, args:['--no-sandbox']});
try{
 const p=await browser.newPage({viewport:{width:1440,height:900}});
 const extra=Array.from({length:22},(_,i)=>`<a href="/long-${i}">Item ${i}</a>`).join('');
 await p.route('https://source.example/',r=>r.fulfill({contentType:'text/html',body:`<!doctype html><style>section{min-height:200px}a{display:block}</style><header><a href="/global">Global header</a><section><h2>Never global</h2><a href="/bad-global">No</a></section></header><main><h1>Home</h1>
 <section><header><h2>Useful section</h2><a href="/stories">Read stories</a></header>
 <a href="/apps">Explore apps</a><a href="/apps">Explore apps</a><a href="/apps">Find apps</a>
 <a href="https://user:pass@source.example/private">Credentials</a><a href="javascript:alert(1)">JS</a><a href="http://127.0.0.1/">Private IP</a><a href="http://localhost./">Localhost dotted</a><a href="#fake">Anchor</a>
 <nav><a href="/nav">Navigation</a></nav><footer><a href="/footer">Footer</a></footer><form><a href="/form">Form</a></form><div role="application"><a href="/demo">Demo</a></div><div data-demo><a href="/demo2">Demo 2</a></div><div aria-hidden="true"><a href="/hidden">Hidden</a></div><figure><blockquote>A real quote</blockquote><figcaption>Person <a href="/review">Review</a></figcaption></figure>
 </section><section><h2>Long actions</h2>${extra}</section><section><h2>Third section</h2><p>Enough copy to count as content</p></section></main><script>window.clicked=0;document.addEventListener('click',()=>window.clicked++);</script>`}));
 await p.goto('https://source.example/');
 const inv=await p.evaluate(fs.readFileSync(base+'/lib/audit/inventory.js','utf8'));
 const sec=inv.sourceCoverage.sections.find(s=>s.title==='Useful section'),long=inv.sourceCoverage.sections.find(s=>s.title==='Long actions');
 assert.ok(sec&&long);assert.equal(await p.evaluate(()=>window.clicked),0);
 assert.equal(inv.sourceCoverage.sections.flatMap(s => s.sourceActions || []).some(a => /\/(global|bad-global)$/.test(a.url)), false, 'site-wide header must never become section evidence');
 assert.deepEqual(sec.sourceActions.map(a=>a.label),['Read stories','Explore apps','Find apps']);
 assert.equal(sec.sourceActionsVersion,1);assert.ok(sec.sourceActionsExcluded>=4);assert.equal(long.sourceActions.length,20);assert.equal(long.sourceActionsFound,22);assert.equal(long.sourceActionsTruncated,true);
 d.beats=[{id:'first',type:'features',h2:'Feature one',features:[{title:'Name',body:'Description'}],source_sections:[sec.id],cta:'Explore apps',cta_href:'https://source.example/apps'}, {id:'second',type:'features',h2:'Feature two',features:[{title:'Name',body:'Description'}],source_sections:[sec.id]}, {id:'third',type:'features',h2:'Feature three',features:[{title:'Name',body:'Description'}],source_sections:[long.id]}];
 fs.writeFileSync(dir+'/direction.json',JSON.stringify(d));fs.writeFileSync(dir+'/inventory.json',JSON.stringify(inv));fs.writeFileSync(dir+'/images.json','[]');
 for(const blueprint of ['aino','atelier','belgrade-arbor','butter','cerebrium','crav','deepbook','halfdays','lpas','tengile','units','white-desert']){
 const rendered=spawnSync(process.env.PYTHON || 'python3',[base+'/lib/render/render_bp.py',dir,blueprint,dir+'/out.html'],{encoding:'utf8'});assert.equal(rendered.status,0,rendered.stderr);
 for(const width of [390,1440]){
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await page.route(/^https?:\/\//,r=>r.abort());await page.goto(pathToFileURL(dir+'/out.html').href+'?nomotion=1');
  assert.equal(await page.locator('.source-actions').filter({hasText:'Useful section'}).count(),1);
  assert.equal(await page.locator('.source-actions-label').first().evaluate(el=>getComputedStyle(el).clip),'rect(0px, 0px, 0px, 0px)','provenance stays available to assistive technology without appearing as page copy');
  assert.ok(await page.getByRole('link',{name:'Read stories'}).isVisible());
  assert.equal(await page.getByRole('link',{name:'Explore apps'}).count(),1,'existing CTA exact pair not duplicated');
  assert.equal(await page.getByRole('link',{name:'Find apps'}).count(),1,'different label, same destination retained');
  assert.equal(await page.getByRole('link',{name:'Read stories'}).getAttribute('href'),'https://source.example/stories');
  for(const text of ['Credentials','JS','Private IP','Localhost dotted','Anchor','Navigation','Footer','Form','Demo','Hidden']) assert.equal(await page.getByRole('link',{name:text,exact:true}).count(),0,text);
  assert.equal(await page.locator('.source-actions').filter({hasText:'Long actions'}).locator('a').count(),20);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);
  await page.close();
 }
 }
 console.log('12 blueprints: captured and rendered provenanced section links, safely and once per section at both widths');
}finally{await browser.close();fs.rmSync(dir,{recursive:true,force:true})}
