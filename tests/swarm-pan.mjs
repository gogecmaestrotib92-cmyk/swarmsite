import assert from 'node:assert/strict';
import fs from 'node:fs';
import {chromium} from 'playwright';
const browser = await chromium.launch({executablePath:process.env.CHROME_PATH || undefined});
try {
 const page=await browser.newPage({viewport:{width:1100,height:700}});
 await page.setContent('<style>#frame{position:relative;width:1100px;height:619px;overflow:hidden;background:black}#frame img{display:block;width:100%;height:auto}</style><div id="frame"><img id="image"></div>');
 await page.addScriptTag({content:fs.readFileSync('web/js/swarm2.js','utf8')});
 for(const width of [390,1100]) for(const h of [900,3257]) {
  await page.locator('#frame').evaluate((frame,w)=>{frame.style.width=`${w}px`;frame.style.height=`${w*9/16}px`},width);
  const result=await page.evaluate(async height=>{
   const image=document.querySelector('#image');image.style.transform='';image.src='data:image/svg+xml,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="${height}"><rect width="100%" height="100%" fill="white"/></svg>`);
   await image.decode();const frame=document.querySelector('#frame');const swarm=window.Swarm2.mount(frame,{count:1});swarm.setPage(image,3257);swarm.panTo({x:10,y:2500,w:100,h:100});
   // Geometry after the transition has completed.
   await new Promise(resolve=>setTimeout(resolve,1300));const f=frame.getBoundingClientRect(),r=image.getBoundingClientRect();const data={pan:swarm.pan,pageH:swarm.pageH,imageBottom:r.bottom,frameBottom:f.bottom};swarm.stop();return data;
  },h);
  assert.ok(result.imageBottom>=result.frameBottom-1,`image ${h} leaves empty space at ${width}px`);
  assert.equal(result.pageH,h);if(h===900)assert.ok(result.pan<70);else assert.ok(result.pan>250);
 }
 console.log('Preview panning stays within the actual short or full capture');
}finally{await browser.close()}
