import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'poster-hero-'));
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox']});
try {
 const base=JSON.parse(fs.readFileSync('tests/direction.sample.json'));
 const images=JSON.parse(fs.readFileSync('tests/images.sample.json'));
 for(const name of ['assets']) fs.copyFileSync(`tests/${name}.sample.json`,path.join(dir,`${name}.json`));
 fs.writeFileSync(path.join(dir,'inventory.json'),JSON.stringify({actions:[{text:'Book your table',href:'https://example.com/book'}]}));
 fs.writeFileSync(path.join(dir,'brief.json'),JSON.stringify({keepColours:false}));
 for(const withImage of [true,false]) for(const headline of ['Big flavors for every gathering','One exceptionally long headline with nine words and extraordinary supercalifragilisticexpialidocious']) {
  const d=structuredClone(base);d.beats=d.beats.filter(b=>b.type!=='form');d.kind='product';d.hero.ui={};d.hero.h1=headline;d.hero.cta='Book your table';d.hero.cta_href='https://example.com/book';if(!withImage)d.hero.media='';
  fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));fs.writeFileSync(path.join(dir,'images.json'),JSON.stringify(withImage?images:[]));
  const output=path.join(dir,'index.html');const run=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,'crav',output],{encoding:'utf8'});assert.equal(run.status,0,run.stderr);
  for(const width of [320,390,1440]) {
   const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await page.route(/^https?:/,r=>r.abort());await page.goto(pathToFileURL(output).href+'?nomotion=1');
   const hero=page.locator('#top');const cls=await hero.getAttribute('class');assert.match(cls,/poster-composition|has-media poster/); /* a picture wide enough carries the type: the real poster; otherwise the composition */assert.equal(await hero.locator('h1').innerText(),headline);
   const realPoster=/has-media poster/.test(cls);assert.equal(realPoster,withImage,'a wide picture gives the real poster, no picture gives the composition');if(realPoster){assert.equal(await hero.locator('.media img').count(),1);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);const h=await hero.locator('h1').boundingBox();assert.ok(h&&h.x>=0&&h.x+h.width<=width+1);await page.close();continue;}
   assert.equal(await hero.locator('.poster-visual img').count(),0);assert.equal(await hero.locator('.ctas a').first().getAttribute('href'),'https://example.com/book');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);const h=await hero.locator('h1').boundingBox();const c=await hero.locator('.ctas a').first().boundingBox();assert.ok(h&&c&&h.x>=0&&h.x+h.width<=width+1&&c.y>=h.y+h.height);if(withImage){const im=await hero.locator('.poster-visual img').boundingBox();assert.ok(im&&im.y>=c.y+c.height-1)}
   await page.close();
  }
 }
 console.log('Poster hero: image/no image, long headings, CTA and three viewport widths passed');
} finally {await browser.close();fs.rmSync(dir,{recursive:true,force:true})}
