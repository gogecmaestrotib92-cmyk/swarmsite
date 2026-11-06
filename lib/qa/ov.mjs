import { chromium } from 'playwright';
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox','--disable-gpu']});
const ctx=await b.newContext({viewport:{width:390,height:844}}); const p=await ctx.newPage(); await p.goto('file:///home/claude/swarm-demo/web/index.html'); await p.waitForTimeout(1500);
console.log(await p.evaluate(()=>[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.right>391&&r.width>0}).slice(0,12).map(e=>e.tagName+'.'+(e.className||'').toString().split(' ')[0]+' r='+Math.round(e.getBoundingClientRect().right)+' w='+Math.round(e.getBoundingClientRect().width)).join('\n')));
await b.close();
