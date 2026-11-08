import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'footer-fallback-')); let browser;
try {
 const direction=JSON.parse(fs.readFileSync('tests/direction.sample.json'));
 direction.beats=[{id:'features',type:'features',h2:'Features',features:[{title:'Useful feature',body:'Helpful description'}],ui:{move:'cards'}}];
 direction.brand.name='Acme & Co';direction.hero.category='';
 direction.nav={links:[['#features','Features'],['#missing','Missing'],['https://example.com/contact','Contact'],['https://untrusted.example/','Unknown'],['javascript:alert(1)','Unsafe']]};
 const inventory={actions:[{text:'Contact',href:'https://example.com/contact'}]};
 fs.writeFileSync(path.join(dir,'images.json'),'[]');fs.writeFileSync(path.join(dir,'inventory.json'),JSON.stringify(inventory));
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox']});
 async function build(name,ending) {
  if(ending === undefined) delete direction.ending; else direction.ending=ending;
  fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(direction));
  const html=path.join(dir,name+'.html');const result=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,'butter',html],{encoding:'utf8'});assert.equal(result.status,0,result.stderr);return html;
 }
 for(const ending of [undefined,null,{}, {tag:'  ',cols:[['',[]],[' ',[' ']]],legal:' ',next:''}]) {
  const html=await build('fallback',ending);
  for(const width of [1440,390]) {
   const page=await browser.newPage({viewport:{width,height:844}});await page.route(/^https?:\/\//,r=>r.abort());await page.goto(`${pathToFileURL(html)}?nomotion=1`);
   const footer=page.locator('footer#end');assert.equal(await footer.count(),1);assert.equal(await footer.locator('.big-p').innerText(),'Acme & Co');
   assert.equal(await footer.getByRole('link',{name:'Features'}).getAttribute('href'),'#features');assert.equal(await footer.getByRole('link',{name:'Contact'}).getAttribute('href'),'https://example.com/contact');
   assert.equal(await footer.getByRole('link',{name:'Missing'}).count(),0);assert.equal(await footer.getByRole('link',{name:'Unknown'}).count(),0);assert.equal(await footer.getByRole('link',{name:'Unsafe'}).count(),0);
   assert.equal(await footer.locator('.fcols, .legal').count(),0);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);
   await footer.scrollIntoViewIfNeeded();await page.screenshot({path:`/tmp/swarm-footer-fallback-${width}.png`});await page.close();
  }
 }
 direction.beats.push({id:'contact',type:'form',h2:'Contact'});
 const html=await build('existing',{tag:'Existing tagline',cols:[['Resources',['One','Two']]],legal:'Source legal copy',next:''});const page=await browser.newPage();await page.route(/^https?:\/\//,r=>r.abort());await page.goto(`${pathToFileURL(html)}?nomotion=1`);
 let footer=page.locator('footer#end');assert.equal(await footer.locator('.big-p').innerText(),'Existing tagline');assert.match(await footer.locator('.fcols').innerText(),/Resources/i);assert.match(await footer.locator('.fcols').innerText(),/One/);assert.equal(await footer.locator('.legal').innerText(),'Source legal copy');assert.equal(await footer.locator('.footer-nav').count(),0);await page.close();
 direction.brand.name='';direction.nav={links:[]}; const empty=await build('no-footer',{});const p=await browser.newPage();await p.route(/^https?:\/\//,r=>r.abort());await p.goto(`${pathToFileURL(empty)}?nomotion=1`);assert.equal(await p.locator('footer#end').count(),0);await p.close();
 console.log('Empty footers use real identity and valid links or are omitted; existing content is preserved');
} finally {if(browser)await browser.close();fs.rmSync(dir,{recursive:true,force:true})}
