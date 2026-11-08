import assert from 'node:assert/strict';import {createRequire} from 'node:module';import {pathToFileURL} from 'node:url';
const {chromium}=createRequire(new URL('../../package.json',import.meta.url))('playwright');const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {})});
for(const [kind,file] of [['story',process.argv[2]],['marquee',process.argv[3]]])for(const width of [390,1440])for(const mode of ['reduce','no-preference']){
 const p=await browser.newPage({viewport:{width,height:900},reducedMotion:mode});await p.goto(pathToFileURL(file).href+(mode==='reduce'?'?nomotion=1':''),{waitUntil:'domcontentloaded'});
 const sec=p.locator('#target');await sec.scrollIntoViewIfNeeded();
 if(kind==='story'){
  assert.equal(await sec.locator('.st-l li').count(),2);assert.equal(await sec.locator('img').count(),1);
  const info=await sec.locator('img').evaluate(e=>{let r=e.getBoundingClientRect();return {w:r.width,h:r.height,nw:e.naturalWidth,nh:e.naturalHeight,fit:getComputedStyle(e).objectFit}});assert.equal(info.fit,'contain');assert(info.w<=info.nw+1&&info.h<=info.nh+1);assert(Math.abs(info.w/info.h-info.nw/info.nh)<.02);
 }else{
  assert.equal(await sec.locator('.marquee-static li').count(),2);
  if(mode==='reduce')assert.equal(await sec.locator('.marquee-static').evaluate(e=>getComputedStyle(e).position),'static');
 }
 assert.equal(await sec.locator('a[href="https://source.example/docs"]').count(),1);
 assert.equal(await sec.locator('a[href="https://source.example/original"]').count(),1);
 assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth),width);await p.close();
}
await browser.close();console.log('Chrome: 390/1440, reduced/normal motion, image geometry, text, links and overflow pass');
