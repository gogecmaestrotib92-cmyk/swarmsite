import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'product-hero-')); let browser;
try {
  for (const n of ['images','assets']) fs.copyFileSync(`tests/${n}.sample.json`,path.join(dir,`${n}.json`));
  const d=JSON.parse(fs.readFileSync('tests/direction.sample.json')); d.kind='software'; d.hero.visual_verified=false;
  fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));
  const html=path.join(dir,'page.html'); const r=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,'deepbook',html],{encoding:'utf8'}); assert.equal(r.status,0,r.stderr);
  browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox']});
  for(const width of [390,1440]) {const page=await browser.newPage({viewport:{width,height:900}}); await page.route(/^https?:\/\//,route=>route.abort()); await page.goto(`${pathToFileURL(html)}?nomotion=1`);
    assert.equal(await page.locator('#top img, #top video').count(),0,'rejected hero must not fall back to a decorative image');
    assert.ok(await page.locator('#top h1').isVisible()); assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false); await page.close();}
  const maker=await browser.newPage(); const image=await maker.evaluate(()=>{const c=document.createElement('canvas');c.width=893;c.height=304;const ctx=c.getContext('2d');ctx.fillStyle='#c4d7e9';ctx.fillRect(0,0,c.width,c.height);ctx.fillStyle='#202a35';ctx.fillRect(20,20,400,200);return c.toDataURL('image/png')});await maker.close();
  fs.writeFileSync(path.join(dir,'images.json'),JSON.stringify([{id:'wide-product',w:893,h:304,shot:true,data:image}]));
  d.hero.media='wide-product';d.hero.visual_verified=true;fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));
  const wide=path.join(dir,'wide.html'),render=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,'deepbook',wide],{encoding:'utf8'});assert.equal(render.status,0,render.stderr);
  for(const width of [390,1440]){const page=await browser.newPage({viewport:{width,height:900}});await page.route(/^https?:\/\//,route=>route.abort());await page.goto(`${pathToFileURL(wide)}?nomotion=1`);assert.equal(await page.locator('#top .product-shot img').count(),1,'verified wide product interface must remain in the hero');const metrics=await page.locator('#top .product-shot img').evaluate(el=>({fit:getComputedStyle(el).objectFit,ratio:el.getBoundingClientRect().width/el.getBoundingClientRect().height,natural:el.naturalWidth/el.naturalHeight}));assert.equal(metrics.fit,'contain');assert.ok(Math.abs(metrics.ratio-metrics.natural)<.03);await page.close();}
  console.log('Rejected visuals stay out; verified wide product screenshots remain visible without distortion');
} finally {if(browser) await browser.close(); fs.rmSync(dir,{recursive:true,force:true});}
