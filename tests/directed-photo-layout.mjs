import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'directed-photo-'));
const python = process.env.PYTHON || 'python3';
const fixture = String.raw`
import base64, io, json, os, sys
from PIL import Image
root=sys.argv[1]
d=json.load(open('tests/direction.sample.json')); d['kind']='place'; d['hero']['media']='hero'
d['beats']=[{'id':id,'type':'photo','h2':'A meaningful section heading','lede':'A caption about this particular image.','image':id,'ui':{'photo_layout':layout}} for id,layout in [('small','wide'),('stack','stacked'),('wide','wide'),('gallery1','gallery'),('gallery2','gallery'),('gallery3','gallery')]]
def image(id,w,h,metadata):
 im=Image.new('RGB',(w,h)); seed=sum(map(ord,id)); im.putdata([((x*7+y*3+seed)%240, (x*3+seed)%220, (y*5+seed)%220) for y in range(h) for x in range(w)])
 buf=io.BytesIO(); im.save(buf,'JPEG'); return {'id':id,'w':metadata,'h':h,'detail':True,'data':'data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()}
imgs=[image('hero',1400,750,1400), image('small',418,315,1400), image('stack',700,500,700), image('wide',1200,750,1200), image('gallery1',418,315,418), image('gallery2',418,315,418), image('gallery3',418,315,418)]
for name,obj in [('direction.json',d),('images.json',imgs)]:
 with open(os.path.join(root,name),'w') as f: json.dump(obj,f)
`;
let browser;
try {
  let r=spawnSync(python,['-c',fixture,dir],{encoding:'utf8'}); assert.equal(r.status,0,r.stderr);
  const html=path.join(dir,'page.html'); r=spawnSync(python,['lib/render/render_bp.py',dir,'tengile',html],{encoding:'utf8'}); assert.equal(r.status,0,r.stderr);
  browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox']});
  for (const width of [320,390,1440]) {
    const page=await browser.newPage({viewport:{width,height:900}}); await page.route(/^https?:\/\//,route=>route.abort());
    await page.goto(`${pathToFileURL(html)}?nomotion=1`);
    for (const [id,cls,native] of [['small','art-photo-split',418],['stack','art-photo-stacked',700],['wide','art-photo-wide',1200]]) {
      const metrics=await page.locator(`#${id}`).evaluate(el=>{const img=el.querySelector('img'); if(!img) throw new Error('Missing image in '+el.id+' '+el.className); const rect=img.getBoundingClientRect(); return {cls:el.className,natural:img.naturalWidth,width:rect.width,height:rect.height,ratio:img.naturalWidth/img.naturalHeight,heading:el.querySelector('h2')?.textContent,overflow:document.documentElement.scrollWidth>innerWidth};});
      assert.ok(metrics.cls.includes(cls),`${id} should use ${cls}`); assert.equal(metrics.natural,native); assert.ok(metrics.width<=native+1,`${id} is upscaled`); assert.ok(Math.abs(metrics.width/metrics.height-metrics.ratio)<.02,`${id} is cropped`); assert.match(metrics.heading,/meaningful section/); assert.equal(metrics.overflow,false);
    }
    assert.equal(await page.locator('.photo-gallery > section').count(),3, await page.locator('#gallery1,#gallery2,#gallery3').evaluateAll(els=>els.map(e=>e.outerHTML.slice(0,120)).join(' | ')));
    for (const id of ['gallery1','gallery2','gallery3']) {const box=await page.locator(`#${id} img`).boundingBox(); assert.ok(box.width <= 418 && box.x >= 0 && box.x+box.width <= width+1);}
    if(width === 1440) {const positions = await page.locator('.photo-gallery > section img').evaluateAll(els=>els.map(el=>el.getBoundingClientRect().top)); assert.ok(Math.max(...positions)-Math.min(...positions)<2, 'three related photos must fit in one row');}
    await page.close();
  }
  console.log('Directed photos preserve pixel size, aspect ratio, content, and mobile bounds');
} finally {if(browser) await browser.close(); fs.rmSync(dir,{recursive:true,force:true});}
