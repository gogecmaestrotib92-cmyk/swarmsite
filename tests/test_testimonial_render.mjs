import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';
const dir = fs.mkdtempSync(path.join(os.tmpdir(),'testimonials-render-'));
let browser;
try {
  const d = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  const reviews = Array.from({length:12},(_,i)=>({text:`Original quote ${i+1}.`,attribution:`Person ${i+1}`,links:[{label:`Source ${i+1}`,url:`https://review.example/${i+1}`}]}));
  d.beats = [{id:'existing-quote',type:'quote',big:'Better working days',body:'This existing quote is still part of the page.',who:'Original Person'},
             {id:'reviews',type:'testimonials',h2:'Customer reviews',testimonials:reviews}];
  fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));
  fs.writeFileSync(path.join(dir,'images.json'),'[]');
  browser = await chromium.launch({executablePath:process.env.CHROME_PATH||undefined});
  for (const id of ['aino','atelier','belgrade-arbor','butter','cerebrium','crav','deepbook','halfdays','lpas','tengile','units','white-desert']) {
    const html = path.join(dir,`${id}.html`);
    const run = spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,id,html],{encoding:'utf8'});
    assert.equal(run.status,0,`${id}: ${run.stderr}`);
    for (const width of [390,1440]) {
      const page = await browser.newPage({viewport:{width,height:844},reducedMotion:'reduce'});
      await page.route(/^https?:\/\//,route=>route.abort());
      await page.goto(`${pathToFileURL(html)}?nomotion=1`,{waitUntil:'domcontentloaded'});
      const original=page.locator('#existing-quote'); assert.equal(await original.count(),1,`${id}: unmatched original quote remains`);
      assert.match((await original.innerText()).toLowerCase(),/this existing quote is still part of the page/);
      assert.match((await original.innerText()).toLowerCase(),/original person/);
      const section=page.locator('#reviews'); assert.equal(await section.count(),1,`${id} ${width}: one section`);
      const figures=section.locator('figure.review-card'); assert.equal(await figures.count(),12,`${id}: all quotes`);
      for (let i=0;i<reviews.length;i++) {
        const card=figures.nth(i); assert.equal(await card.locator('blockquote').innerText(),reviews[i].text);
        assert.equal(await card.locator('figcaption span').innerText(),reviews[i].attribution);
        assert.equal(await card.locator('a').getAttribute('href'),reviews[i].links[0].url);
        assert.ok(await card.isVisible()); const box=await card.boundingBox(); assert.ok(box.x>=-1 && box.x+box.width<=width+1,`${id} ${width}: card fits`);
      }
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);
      await page.close();
    }
  }
  console.log('All twelve quotes and source links render in one section on twelve blueprints at phone and desktop widths');
} finally { if(browser) await browser.close(); fs.rmSync(dir,{recursive:true,force:true}); }
