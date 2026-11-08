import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'render-complete-items-'));
let browser;
try {
  const d = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
  d.kind = 'software';
  const features = Array.from({length:12}, (_,i)=>({title:`Capability ${i+1}`,body:`Capability description ${i+1}`}));
  const steps = Array.from({length:11},(_,i)=>`Distinct step ${i+1} continues here`);
  const cells = Array.from({length:10},(_,i)=>[`Cell label ${i+1}`, i===0 ? 0 : i===1 ? 'Free' : `${i+10}%`, `Cell description ${i+1}`]);
  const facts = Array.from({length:11},(_,i)=>[`Fact value ${i+1}`,`Fact detail ${i+1}`]);
  const faq = Array.from({length:10},(_,i)=>[`Question number ${i+1}?`,`Answer number ${i+1}.`]);
  d.beats = [
    {id:'full-features',type:'features',h2:'Capabilities',lede:'Every capability matters.',features,ui:{move:'sticky-product'}},
    {id:'full-steps',type:'steps',h2:'Steps',steps,ui:{move:'pinned-sequence'}},
    {id:'full-cells',type:'cells',h2:'Cells',cells,ui:{move:'marquee'}},
    {id:'full-facts',type:'facts',h2:'Facts',facts,ui:{move:'story'}},
    {id:'full-faq',type:'faq',h2:'Questions',items:faq},
  ];
  fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));
  fs.writeFileSync(path.join(dir,'images.json'),'[]');
  const ids = ['aino','atelier','belgrade-arbor','butter','cerebrium','crav','deepbook','halfdays','lpas','tengile','units','white-desert'];
  browser = await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox']});
  for (const id of ids) {
    const html=path.join(dir,`${id}.html`);
    const out=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,id,html],{encoding:'utf8'});
    assert.equal(out.status,0,`${id}: ${out.stderr}`);
    for (const width of [390,1440]) {
      const page=await browser.newPage({viewport:{width,height:844},reducedMotion:'reduce'});
      await page.route(/^https?:\/\//, route=>route.abort());
      await page.goto(`${pathToFileURL(html)}?nomotion=1`,{waitUntil:'domcontentloaded'});
      for (const [selector, texts] of [
        ['#full-features',features.flatMap(f=>[f.title,f.body])],
        ['#full-steps',steps],
        ['#full-facts',facts.flat()],
      ]) {
        const section=page.locator(selector);
        assert.equal(await section.count(),1,`${id} ${width}: ${selector} section exists`);
        for (const text of texts) {
          const locator=section.getByText(text,{exact:true});
          assert.equal(await locator.count(),1,`${id} ${width}: ${selector} includes ${text} once; section=${await section.innerText()}`);
          assert.ok(await locator.isVisible(),`${id} ${width}: ${text} is not hidden in inactive motion`);
          const rect=await locator.boundingBox();
          assert.ok(rect && rect.x>=-1 && rect.x+rect.width<=width+1,`${id} ${width}: ${text} outside viewport`);
        }
      }
      const cellSection = page.locator('#full-cells');
      const cellRows = cellSection.locator('.card, .marquee-static li, .nums > div, .cols > div, .rc');
      assert.equal(await cellRows.count(),cells.length,`${id} ${width}: every cell is present once`);
      for (let i=0; i<cells.length; i++) {
        const row = cellRows.nth(i), body = await row.innerText();
        for (const value of cells[i]) assert.ok(body.includes(String(value)),`${id} ${width}: cell ${i+1} retains ${value}`);
        assert.ok(await row.isVisible(),`${id} ${width}: cell ${i+1} visible in reduced motion`);
        const rect = await row.boundingBox();
        assert.ok(rect && rect.x >= -1 && rect.x + rect.width <= width + 1,`${id} ${width}: cell ${i+1} fits viewport`);
      }
      const details=page.locator('#full-faq details');
      assert.equal(await details.count(),faq.length,`${id} ${width}: every FAQ exists`);
      await details.last().locator('summary').click();
      assert.equal(await details.last().locator('p').innerText(),faq.at(-1)[1],`${id} ${width}: last FAQ opens`);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width,`${id} ${width}: no horizontal overflow`);
      await page.close();
    }
  }
  // Shorter recipe rails still need every item on screen on a phone; the
  // long-list fallback above alone would not exercise the rail itself.
  d.beats[0].features = features.slice(0,6);
  d.beats[0].ui = {move:'auto'};
  fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));
  const railHtml = path.join(dir,'rail.html');
  const railRender = spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,'belgrade-arbor',railHtml],{encoding:'utf8'});
  assert.equal(railRender.status,0,railRender.stderr);
  for (const reducedMotion of ['reduce','no-preference']) {
    const page = await browser.newPage({viewport:{width:390,height:844},reducedMotion});
    await page.route(/^https?:\/\//, route=>route.abort());
    await page.goto(`${pathToFileURL(railHtml)}${reducedMotion === 'reduce' ? '?nomotion=1' : ''}`,{waitUntil:'domcontentloaded'});
    const rows = page.locator('#full-features .rc');
    assert.equal(await rows.count(),6,'recipe rail exists and keeps every row');
    for (let i=0;i<6;i++) {
      const rect=await rows.nth(i).boundingBox();
      assert.ok(rect && rect.x>=-1 && rect.x+rect.width<=391,`mobile rail item ${i+1} is not clipped`);
    }
    await page.close();
  }
  console.log('All list content is preserved across 12 blueprints, desktop and reduced-motion mobile');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir,{recursive:true,force:true});
}
