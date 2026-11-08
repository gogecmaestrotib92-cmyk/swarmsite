import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-product-story-'));
let browser;
try {
  browser = await chromium.launch({executablePath: process.env.CHROME_PATH || undefined, args:['--no-sandbox']});
  const setup = await browser.newPage();
  const visuals = await setup.evaluate(() => {
    function make(id,w,h,shot,color) {
      const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
      x.fillStyle=color;x.fillRect(0,0,w,h);x.fillStyle='#fff';x.fillRect(12,12,w/3,h/3);x.fillStyle='#111';x.fillRect(w/2,h/2,w/3,h/3);
      return {id,w,h,shot,detail:true,src:shot?'visual-shot':`https://source.example/${id}.jpg`,data:c.toDataURL('image/png')};
    }
    return [make('hero',1100,700,false,'#903'),make('wide',1200,400,true,'#47c'),make('square',720,700,true,'#3b7'),make('small',400,200,true,'#951'),make('photo',1000,800,false,'#6ad')];
  });
  await setup.close();
  const original=JSON.parse(fs.readFileSync('tests/direction.sample.json','utf8'));
  const source={id:'s1',title:'Source',headingLevel:'H2',kind:'section',sourceActionsVersion:1,sourceActions:[{label:'Original details',url:'https://source.example/details'}]};
  fs.writeFileSync(path.join(dir,'inventory.json'),JSON.stringify({sourceCoverage:{sections:[source]},actions:[{text:'Explore',href:'https://source.example/explore'}]}));
  fs.writeFileSync(path.join(dir,'images.json'),JSON.stringify(visuals));
  const features=Array.from({length:7},(_,i)=>({title:`Capability ${i+1}`,body:`Exact useful detail ${i+1}.`}));
  function build(bp, image, mutate=()=>{}) {
    const d=structuredClone(original);d.kind='software';d.hero.media='hero';d.beats=[{id:'features',type:'features',h2:'One product for every team',lede:'All capabilities together.',source_sections:['s1'],cta:'Explore',cta_href:'https://source.example/explore',features:structuredClone(features),ui:{move:'cards',head:'left',lead:image}}];mutate(d);
    fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));
    const out=path.join(dir,'index.html');const r=spawnSync('python3',['lib/render/render_bp.py',dir,bp,out],{encoding:'utf8'});assert.equal(r.status,0,r.stderr);return out;
  }
  for(const bp of ['butter','cerebrium','deepbook','aino','atelier']) for(const image of ['wide','square']) {
    const out=build(bp,image);
    for(const [width,dpr] of [[390,1],[1440,1],[1440,2]]) {
      const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:dpr,reducedMotion:'reduce'});
      await page.route(/^https?:\/\//,r=>r.abort());await page.goto(`${pathToFileURL(out)}?nomotion=1`,{waitUntil:'domcontentloaded'});
      const section=page.locator('#features');assert.equal(await section.locator('.product-story-row').count(),7,`${bp}/${image}/${width}: all rows`);
      assert.equal(await section.locator('h2').innerText(),'One product for every team');
      for(const f of features){assert.equal(await section.getByText(f.title,{exact:true}).count(),1);assert.equal(await section.getByText(f.body,{exact:true}).count(),1)}
      assert.equal(await section.locator('a[href="https://source.example/details"]').count(),1,'source action');
      assert.equal(await section.locator('a[href="https://source.example/explore"]').count(),1,'CTA');
      const info=await section.locator('figure img').evaluate(i=>{let b=i.getBoundingClientRect();return {src:i.src,width:b.width,height:b.height,nw:i.naturalWidth,nh:i.naturalHeight,fit:getComputedStyle(i).objectFit,overflow:document.documentElement.scrollWidth>innerWidth}});
      assert.equal(info.src,visuals.find(v=>v.id===image).data,'assigned image only');assert.ok(info.width*dpr<=info.nw+1 && info.height*dpr<=info.nh+1,'no upscaling at device pixel ratio');assert.ok(Math.abs(info.width/info.height-info.nw/info.nh)<.02,'full image');assert.equal(info.fit,'contain');assert.equal(info.overflow,false);
      assert.equal(await section.locator('.product-story-wide').count(),0);assert.equal(await section.evaluate(e=>e.classList.contains('product-story-wide')),image==='wide');
      await page.close();
    }
  }
  // Exercise the real GSAP path in addition to reduced-motion / nomotion.
  {
    const out=build('butter','wide');
    const page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'no-preference'});
    await page.route(/^https?:\/\//,r=>r.abort());
    await page.route('**/gsap.min.js',r=>r.fulfill({path:'node_modules/gsap/dist/gsap.min.js',contentType:'application/javascript'}));
    await page.route('**/ScrollTrigger.min.js',r=>r.fulfill({path:'node_modules/gsap/dist/ScrollTrigger.min.js',contentType:'application/javascript'}));
    await page.goto(pathToFileURL(out).href,{waitUntil:'load'});
    const heading=page.locator('#features h2');await heading.scrollIntoViewIfNeeded();
    await page.waitForTimeout(1500);
    assert.ok(Number(await heading.evaluate(e=>getComputedStyle(e).opacity))>.95,'motion reveals heading');
    assert.equal(await page.locator('#features .product-story-row').count(),7);
    await page.close();
  }
  for(const [label,visual,change] of [
    ['missing','missing',()=>{}],['too-small','small',()=>{}],['not-shot','photo',()=>{}],
    ['short-list','wide',d=>d.beats[0].features.pop() && d.beats[0].features.pop() && d.beats[0].features.pop()],
    ['individual-image','wide',d=>d.beats[0].features[0].image='photo'],
    ['reserved-for-other-beat','wide',d=>d.beats.unshift({id:'owner',type:'photo',h2:'Image owner',image:'wide'})],
    ['pinned-intent','wide',d=>d.beats[0].ui.move='pinned-sequence'],
    ['nonsoftware','wide',d=>d.kind='place'],
  ]) {
    const out=build('butter',visual,change);const html=fs.readFileSync(out,'utf8');assert.doesNotMatch(html,/<section class="sec product-story/,label);
  }
  console.log('Long product story preserves source content, links and assigned screenshots across blueprints');
} finally {if(browser)await browser.close();fs.rmSync(dir,{recursive:true,force:true})}
