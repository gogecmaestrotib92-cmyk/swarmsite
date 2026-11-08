import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';

const dir=fs.mkdtempSync(path.join(os.tmpdir(),'story-provenance-'));
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,headless:true});
try {
  const generator=await browser.newPage();
  const assets=await generator.evaluate(()=>{
    const paint=(id,w,h,mode)=>{const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,w,h);x.fillStyle='#111';
      if(mode==='diagonal')for(let i=0;i<20;i++){x.fillRect(i*80,i*25,40,18)}
      if(mode==='stripes')for(let i=0;i<10;i++){x.fillRect(i*130,0,65,h)}
      if(mode==='circle'){x.beginPath();x.arc(w/2,h/2,200,0,Math.PI*2);x.fill()}
      if(mode==='checks')for(let i=0;i<15;i++)for(let j=0;j<10;j++)if((i+j)%2)x.fillRect(i*80,j*70,80,70);
      return {id,w,h,data:c.toDataURL('image/jpeg')};};
    return [
      {...paint('hero',1300,700,'circle'),src:'https://source.example/photos/hero.jpg'},
      {...paint('small-ui',600,595,'diagonal'),src:'visual-shot',shot:true},
      {...paint('unrelated-ui',1000,800,'circle'),src:'visual-shot',shot:true},
      {...paint('rasterized-logo',1400,1400,'stripes'),src:'https://source.example/apps/provider.svg?build=1',alt:'Provider'},
      {...paint('raster-icon',900,900,'diagonal'),src:'https://source.example/assets/icon-mark.png',alt:'Provider icon'},
      {...paint('real-photo',1200,700,'checks'),src:'https://source.example/photos/team.jpg',alt:'Team at work'},
    ];
  });
  await generator.close();
  const base=JSON.parse(fs.readFileSync('tests/direction.sample.json','utf8'));
  const features=[{title:'First feature',body:'A complete description.'},{title:'Second feature',body:'Another complete description.'}];
  for(const [includePhoto,reserveLogo] of [[true,false],[false,false],[true,true]]) {
    const d=structuredClone(base); d.kind='software';d.hero.media='hero';
    d.beats=[
      {id:'assigned-small',type:'features',h2:'Assigned screenshot',image:'small-ui',features,cta:'Read the guide',cta_href:'https://source.example/guide',ui:{move:'story'}},
      {id:'no-assignment',type:'features',h2:'Fallback visual',features,ui:{move:'story',lead:''}},
    ];
    if(!includePhoto) d.beats.push({id:'unassigned-steps',type:'steps',h2:'No visual steps',steps:['First step','Second step'],ui:{move:'story'}});
    if(reserveLogo) {
      d.beats.push({id:'assigned-logo',type:'features',h2:'Assigned logo',image:'rasterized-logo',features,ui:{move:'story'}});
      d.beats.push({id:'wide-logo',type:'features',h2:'Long list with logo',features:[...features,...features,features[0]],ui:{move:'story',lead:'rasterized-logo'}});
    }
    fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));
    fs.writeFileSync(path.join(dir,'images.json'),JSON.stringify(assets.filter(a=>includePhoto||a.id!=='real-photo')));
    fs.writeFileSync(path.join(dir,'inventory.json'),JSON.stringify({actions:[{text:'Read the guide',href:'https://source.example/guide'}]}));
    const html=path.join(dir,'result.html');const rendered=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,'butter',html],{encoding:'utf8'});assert.equal(rendered.status,0,rendered.stderr);
    for(const width of [1440,390]) {
      const page=await browser.newPage({viewport:{width,height:900}});await page.route(/^https?:\/\//,r=>r.abort());await page.goto(`${pathToFileURL(html)}?nomotion=1`,{waitUntil:'load'});
      for(const id of ['assigned-small',...(!includePhoto?['unassigned-steps']:[]),...(reserveLogo?['assigned-logo','wide-logo']:[])]) {
        const section=page.locator(`#${id}`);assert.equal(await section.locator('img').count(),0,`${id}: no unrelated logo or substitute image`);
        assert.equal(await section.locator('.card').count(),id==='wide-logo'?5:2,`${id}: all items retained`);
        assert.match(await section.innerText(),id==='unassigned-steps'?/First step/:/A complete description/);
      }
      const fallback=page.locator('#no-assignment');
      assert.equal(await fallback.locator('img').count(),includePhoto?1:0,'only a source photo may be used implicitly');
      if(includePhoto) assert.equal(await fallback.locator('img').getAttribute('src'),assets.find(x=>x.id==='real-photo').data,'the true photo is retained');
      assert.equal(await page.locator('#assigned-small a').getAttribute('href'),'https://source.example/guide');
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width,'no horizontal overflow');await page.close();
    }
  }
  for(const includePhoto of [false,true]) {
    const d=structuredClone(base); d.kind='place'; d.hero.media='hero';
    d.beats=[{id:'facts',type:'facts',h2:'Facts',facts:[['12','Years'],['4','Locations']],ui:{move:'cards'}}];
    fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));
    fs.writeFileSync(path.join(dir,'images.json'),JSON.stringify(assets.filter(a=>['hero','rasterized-logo','raster-icon',...(includePhoto?['real-photo']:[])].includes(a.id))));
    const html=path.join(dir,'facts.html');const rendered=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,'butter',html],{encoding:'utf8'});assert.equal(rendered.status,0,rendered.stderr);
    for(const width of [1440,390]) {
      const page=await browser.newPage({viewport:{width,height:900}});await page.route(/^https?:\/\//,r=>r.abort());await page.goto(`${pathToFileURL(html)}?nomotion=1`,{waitUntil:'load'});
      const section=page.locator('#facts');assert.equal(await section.locator('img').count(),includePhoto?1:0,'facts pool excludes SVG logos and icons');
      if(includePhoto) assert.equal(await section.locator('img').getAttribute('src'),assets.find(x=>x.id==='real-photo').data,'facts retains real source photo');
      assert.match(await section.innerText(),/Years/);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);await page.close();
    }
  }
  console.log('Story images avoid rasterized SVG logos and retain real photos, content and actions');
} finally {await browser.close();fs.rmSync(dir,{recursive:true,force:true});}
