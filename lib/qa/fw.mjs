import { chromium } from 'playwright';
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox','--disable-gpu']});
for (const [w,f] of [['navy','fraunces'],['ink','instrument'],['terracotta','brand']]) { const ctx=await b.newContext({viewport:{width:1440,height:900}}); const p=await ctx.newPage();
  await p.goto('file:///tmp/f.html'); await p.waitForTimeout(1500); await p.evaluate(([w,f])=>{const h=document.documentElement; if(w!=='brand')h.dataset.world=w; if(f!=='brand')h.dataset.font=f;},[w,f]); await p.waitForTimeout(800);
  await p.screenshot({path:`/tmp/fw-${w}-hero.png`}); await p.evaluate(()=>document.querySelector('#jelovnik').scrollIntoView()); await p.waitForTimeout(1500); await p.screenshot({path:`/tmp/fw-${w}-menu.png`}); await ctx.close(); }
await b.close();