
import { chromium } from 'playwright'; 
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox','--disable-gpu']});
for (const w of ['brand','red','blue','amber']) { const ctx=await b.newContext({viewport:{width:1440,height:900}}); const p=await ctx.newPage();
  await p.goto('file:///home/claude/swarm-demo/v3/c1.html'); await p.waitForTimeout(800);
  await p.evaluate(w=>{const r=document.querySelector(`input[name=world][value=${w}]`); if(r) r.checked=true;},w);
  await p.click('#sw-skip'); await p.waitForTimeout(1500); await p.screenshot({path:`/tmp/world-${w}-hero.png`});
  await p.evaluate(()=>document.querySelector('#price').scrollIntoView()); await p.waitForTimeout(1500); await p.screenshot({path:`/tmp/world-${w}-price.png`});
  await ctx.close(); }
await b.close();
