import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-ui-photo-'));
let browser;
try {
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  const builder = await browser.newPage();
  const images = await builder.evaluate(() => {
    function make(id, w, h, shot) {
      const c=document.createElement('canvas'); c.width=w; c.height=h; const x=c.getContext('2d');
      x.fillStyle='#fff'; x.fillRect(0,0,w,h); x.fillStyle='#f00';x.fillRect(0,0,20,20); x.fillStyle='#00f';x.fillRect(w-20,h-20,20,20);
      return {id,w,h,shot,detail:true,src:shot?'visual-shot':`https://example.test/${id}.jpg`,data:c.toDataURL('image/png')};
    }
    const mismatch=make('mismatch',600,450,true); mismatch.w=1200; // metadata may describe the pre-downsampled original
    return [make('hero',1200,700,false),make('wide',1200,300,true),make('portrait',450,1200,true),mismatch];
  });
  await builder.close();
  const sample=JSON.parse(fs.readFileSync('tests/direction.sample.json','utf8'));
  const blueprints=fs.readdirSync('lib/blueprints').filter(f=>f.endsWith('.bp.json')).map(f=>f.replace('.bp.json',''));
  for(const kind of ['software','product']) for(const bp of blueprints){
    const d=structuredClone(sample);d.kind=kind;d.hero.media='hero';d.beats=[
      {id:'ui-wide',type:'photo',image:'wide',h2:'Wide UI heading',label:'Real product',lede:'Complete source explanation.',cap:['Source detail'],cta:'Explore tools',cta_href:'https://example.test/tools',band:'paper',ui:{move:'story'}},
      {id:'ui-portrait',type:'photo',image:'portrait',h2:'Portrait UI heading',label:'Another label',lede:'More verified source content.',cap:['Additional detail'],band:'dark',ui:{move:'story'}},
      {id:'ui-mismatch',type:'photo',image:'mismatch',h2:'Downsampled UI heading',label:'Source detail',lede:'Content is still readable.',cap:['Original detail'],band:'paper',ui:{move:'story'}}
    ];
    fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));fs.writeFileSync(path.join(dir,'images.json'),JSON.stringify(images));
    fs.writeFileSync(path.join(dir,'inventory.json'),JSON.stringify({actions:[{text:'Explore tools',href:'https://example.test/tools'}]}));
    const html=path.join(dir,'page.html');const result=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,bp,html],{encoding:'utf8'});
    assert.equal(result.status,0,`${kind}/${bp}: ${result.stderr}`);
    for(const width of [390,1440]){
      const page=await browser.newPage({viewport:{width,height:900}});await page.route(/^https?:\/\//,r=>r.abort());await page.goto(`${pathToFileURL(html)}?nomotion=1`,{waitUntil:'domcontentloaded'});
      for(const id of ['ui-wide','ui-portrait','ui-mismatch']){
        const section=page.locator(`#${id}`);const h=section.locator('h2');const figure=section.locator('figure.ui-shot');const img=figure.locator('img');
        assert.equal(await h.count(),1,`${kind}/${bp}/${id}: one heading`);assert.equal(await figure.count(),1,`${kind}/${bp}/${id}: UI image shown`);
        const info=await section.evaluate(s=>{const h=s.querySelector('h2'), f=s.querySelector('figure'),i=f.querySelector('img'), a=h.getBoundingClientRect(), b=f.getBoundingClientRect(),c=i.getBoundingClientRect();return {overlay:!!h.closest('figure'),headingBelow:a.bottom> b.top+1,light:h.classList.contains('light'),color:getComputedStyle(h).color,fit:getComputedStyle(i).objectFit,w:c.width,h:c.height,nw:i.naturalWidth,nh:i.naturalHeight,overflow:document.documentElement.scrollWidth>innerWidth};});
        assert.equal(info.overlay,false,`${kind}/${bp}/${id}: heading must not overlay UI`);assert.equal(info.headingBelow,false,`${kind}/${bp}/${id}: heading precedes image`);assert.equal(info.light,false,`${kind}/${bp}/${id}: do not apply photo-overlay text`);
        assert.equal(info.fit,'contain');assert.ok(info.w<=info.nw+1 && info.h<=info.nh+1,`${kind}/${bp}/${id}: no upscaling`);assert.ok(Math.abs(info.w/info.h-info.nw/info.nh)<.02,`${kind}/${bp}/${id}: full image aspect`);assert.equal(info.overflow,false);
        const text=await section.innerText();assert.ok(text.includes(id==='ui-wide'?'Complete source explanation.':id==='ui-portrait'?'More verified source content.':'Content is still readable.'));assert.ok(text.includes(id==='ui-wide'?'Source detail':id==='ui-portrait'?'Additional detail':'Original detail'));
      }
      assert.equal(await page.locator('#ui-wide a[href="https://example.test/tools"]').count(),1,`${kind}/${bp}: source CTA retained`);
      await page.close();
    }
  }
  console.log('Software and product screenshots keep readable headings and full UI across all blueprints');
} finally { if(browser)await browser.close();fs.rmSync(dir,{recursive:true,force:true}); }
