import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';
const log = process.env.SWARM_CAPTURE_LOG;
const imagePath = process.env.SWARM_CAPTURE_IMAGE;
if (!log || !imagePath) throw new Error('Provide real capture log and before-full image');
const events = fs.readFileSync(log, 'utf8').split('\n').flatMap(line => { try { const v=JSON.parse(line); return v.event ? [v.event] : []; } catch { return []; } });
assert.ok(events.some(e => e.role === 'Reader' && e.text.startsWith('Reading page')), 'capture emitted real Reader progress');
const html=fs.readFileSync('web/app.html','utf8'), swarm=fs.readFileSync('web/js/swarm2.js','utf8'), image=fs.readFileSync(imagePath);
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH || undefined,args:['--no-sandbox']});
try { for(const width of [390,1440]) { const page=await browser.newPage({viewport:{width,height:900}});
 await page.route('**/*',async route=>{const u=new URL(route.request().url());
  if(u.hostname==='app.test'&&u.pathname==='/app') return route.fulfill({contentType:'text/html',body:html});
  if(u.hostname==='app.test'&&u.pathname==='/config.js') return route.fulfill({contentType:'application/javascript',body:"window.SWARMSITE_API='https://api.test'"});
  if(u.hostname==='app.test'&&u.pathname==='/js/swarm2.js') return route.fulfill({contentType:'application/javascript',body:swarm});
  if(u.hostname==='api.test'&&u.pathname==='/before.jpg') return route.fulfill({contentType:'image/jpeg',body:image});
  if(u.hostname==='api.test'&&u.pathname.startsWith('/jobs/')) return route.fulfill({contentType:'application/json',body:JSON.stringify({id:'job',status:'running',steps:[{id:'capture',label:'Reading',status:'running'}],result:{beforeFullUrl:'https://api.test/before.jpg',pageHeight:7000,events}})});
  return route.abort(); });
 await page.goto('http://app.test/app?url=example.com&job=job');
 await page.waitForFunction(()=>document.querySelector('#before').naturalWidth>0);
 await page.waitForFunction(()=>[...document.querySelectorAll('.s2-cur.in:not(.off)')].some(e=>getComputedStyle(e).opacity!=='0'),null,{timeout:12000});
 assert.equal(await page.locator('#stage').isVisible(),true);
 assert.ok((await page.locator('#log').textContent()).includes('Reader'));
 await page.close(); }
 console.log('Real capture progress and source image keep Reader visible in the loading view on phone and desktop');
} finally {await browser.close();}
