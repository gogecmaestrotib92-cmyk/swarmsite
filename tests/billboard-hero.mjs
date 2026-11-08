import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'billboard-hero-'));
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox']});
try {
 const base=JSON.parse(fs.readFileSync('tests/direction.sample.json'));const imgs=JSON.parse(fs.readFileSync('tests/images.sample.json'));
 fs.copyFileSync('tests/assets.sample.json',path.join(dir,'assets.json'));fs.writeFileSync(path.join(dir,'inventory.json'),JSON.stringify({actions:[{text:'Book your table',href:'https://example.com/book'}]}));
 for(const mode of ['photo','missing','screenshot']) for(const headline of ['A better place to meet','A very long headline with nine words and supercalifragilisticexpialidocious']) {
  const d=structuredClone(base);d.beats=d.beats.filter(b=>b.type!=='form');d.hero.ui={move:'billboard'};d.hero.h1=headline;d.hero.cta='Book your table';d.hero.cta_href='https://example.com/book';d.hero.media=mode==='missing'?'missing':'waiter';
  const shots=structuredClone(imgs);if(mode==='screenshot')shots.find(x=>x.id==='waiter').shot=true;
  fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));fs.writeFileSync(path.join(dir,'images.json'),JSON.stringify(shots));
  const out=path.join(dir,'index.html'),run=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,'tengile',out],{encoding:'utf8'});assert.equal(run.status,0,run.stderr);
  for(const [width,height] of [[320,900],[390,900],[1000,625],[1440,900]]) {const page=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});await page.route(/^https?:/,r=>r.abort());await page.goto(pathToFileURL(out).href+'?nomotion=1');const hero=page.locator('#top');assert.equal(await hero.locator('h1').textContent(),headline);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);if(mode==='photo'){assert.match(await hero.getAttribute('class'),/billboard/);assert.equal(await hero.locator('.billboard-media img').count(),1);assert.equal(await hero.locator('.ctas a').first().getAttribute('href'),'https://example.com/book');if(width===1000&&headline==='A better place to meet'){const cta=await hero.locator('.ctas a').first().boundingBox();assert.ok(cta&&cta.y+cta.height<=height,'CTA fits short desktop viewport')}const box=await hero.locator('h1').boundingBox();assert.ok(box&&box.x>=0&&box.x+box.width<=width+1);const bg=await hero.locator('.billboard-content').evaluate(e=>getComputedStyle(e).backgroundColor);assert.equal(bg,'rgba(0, 0, 0, 0.58)');const geometry=await hero.evaluate(e=>{const f=e.querySelector('.billboard-frame').getBoundingClientRect(),c=e.querySelector('.billboard-content').getBoundingClientRect();return {f:f.toJSON(),c:c.toJSON()}});assert.ok(Math.abs(geometry.f.left-geometry.c.left)<1&&Math.abs(geometry.f.right-geometry.c.right)<1&&Math.abs(geometry.f.top-geometry.c.top)<1&&Math.abs(geometry.f.bottom-geometry.c.bottom)<1,'scrim covers full image panel');const channel=1-.58;const linear=channel<=.04045?channel/12.92:((channel+.055)/1.055)**2.4;assert.ok(1.05/(linear+.05)>=4.5,'white text retains contrast over white photo');}else assert.doesNotMatch(await hero.getAttribute('class'),/billboard/);await page.close();}
 }
 console.log('Billboard: assigned photo, fallback, long headings and four viewports passed');
}finally{await browser.close();fs.rmSync(dir,{recursive:true,force:true})}
