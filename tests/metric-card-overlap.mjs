import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'metric-cards-'));
const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
direction.kind = 'place';
direction.beats = [{id:'hours',type:'cells',h2:'Opening hours',ui:{move:'cards',cols:3,lead:''},cells:[
  ['Weekdays','08:00 – 0:00','Hours'],['Weekend','09:30 – 02:00','Hours'],['Telephone','910 51 45 04','Reservations'],
]}];
fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(direction));
fs.writeFileSync(path.join(dir,'images.json'),'[]');
let browser;
try {
  const out=path.join(dir,'page.html');
  const r=spawnSync(process.env.PYTHON || 'python3',['lib/render/render_bp.py',dir,'white-desert',out],{encoding:'utf8'});
  assert.equal(r.status,0,r.stderr);
  browser=await chromium.launch({executablePath:process.env.CHROME_PATH || undefined,args:['--no-sandbox']});
  for(const width of [320,390,1024,1440]) {
    const p=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
    await p.route(/^https?:/,route=>route.abort());
    await p.goto(pathToFileURL(out).href+'?nomotion=1');
    const cards=p.locator('#hours .card'); assert.equal(await cards.count(),3);
    const rects=await cards.evaluateAll(els=>els.map(el=>{
      const box=el.getBoundingClientRect(),num=el.querySelector('.num'),range=document.createRange();
      range.selectNodeContents(num);return {box:box.toJSON(),text:[...range.getClientRects()].map(r=>r.toJSON()),value:num.textContent};
    }));
    assert.deepEqual(rects.map(x=>x.value),['08:00 – 0:00','09:30 – 02:00','910 51 45 04']);
    for(const x of rects) assert.ok(x.text.every(r=>r.left>=x.box.left-1&&r.right<=x.box.right+1),`${width}: ${x.value} escaped its card`);
    assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth),width);
    await p.close();
  }
  console.log('Metric cards retain hours and phone without crossing columns at four widths');
} finally { if(browser) await browser.close(); fs.rmSync(dir,{recursive:true,force:true}); }
