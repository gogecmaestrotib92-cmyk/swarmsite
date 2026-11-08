import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';

const dir=fs.mkdtempSync(path.join(os.tmpdir(),'swarm-logo-contrast-'));
const direction=JSON.parse(fs.readFileSync('tests/direction.sample.json','utf8'));
const svg=body=>'data:image/svg+xml;base64,'+Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="101" height="22" viewBox="0 0 101 22">${body}</svg>`).toString('base64');
const dark=svg('<path fill="#292929" d="M0 0h101v22H0z"/>');
const light=svg('<path fill="#ffffff" d="M0 0h101v22H0z"/>');
const mixed=svg('<path fill="#292929" d="M0 0h50v22H0z"/><path fill="#ffffff" d="M50 0h51v22H50z"/>');
const inherited=svg('<g fill="white"><rect stroke="black" width="50" height="22"/><rect fill="black" x="50" width="51" height="22"/></g>');
const gradient=svg('<defs><linearGradient id="g"><stop stop-color="#000"/></linearGradient></defs><path fill="url(#g)" d="M0 0h101v22H0z"/>');
let browser;
try{
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox']});
 const setup=await browser.newPage();
 const raster=await setup.evaluate(()=>{function logo(color){const c=document.createElement('canvas');c.width=101;c.height=22;const x=c.getContext('2d');x.fillStyle=color;x.fillRect(10,2,80,18);return c.toDataURL('image/png')};function large(withLight,overLimit=false){const c=document.createElement('canvas');c.width=c.height=overLimit?2001:1000;const x=c.getContext('2d');x.fillStyle='#141414';x.fillRect(0,0,c.width,c.height);if(withLight){x.fillStyle='#fff';x.fillRect(501,501,1,1)}return c.toDataURL('image/png')};const c=document.createElement('canvas');c.width=101;c.height=22;const x=c.getContext('2d');x.fillStyle='#292929';x.fillRect(0,0,50,22);x.globalAlpha=191/255;x.fillStyle='#fff';x.fillRect(51,0,50,22);return {dark:logo('#292929'),light:logo('#fff'),partlyLight:c.toDataURL('image/png'),largeDark:large(false),tinyLight:large(true),overLimit:large(false,true)}});await setup.close();
 const cases=[
  {name:'dark-svg',bp:'cerebrium',logo:dark,plate:true},
  {name:'light-svg',bp:'cerebrium',logo:light,plate:false},
  {name:'mixed-svg',bp:'cerebrium',logo:mixed,plate:false},
  {name:'inherited-white-svg',bp:'cerebrium',logo:inherited,plate:false},
  {name:'gradient-svg',bp:'cerebrium',logo:gradient,plate:false},
  {name:'dark-png',bp:'cerebrium',logo:raster.dark,plate:true},
  {name:'light-png',bp:'cerebrium',logo:raster.light,plate:false},
  {name:'partly-light-png',bp:'cerebrium',logo:raster.partlyLight,plate:false},
  {name:'large-dark-png',bp:'cerebrium',logo:raster.largeDark,plate:true},
  {name:'tiny-light-detail-png',bp:'cerebrium',logo:raster.tinyLight,plate:false},
  {name:'oversized-png',bp:'cerebrium',logo:raster.overLimit,plate:false},
  {name:'light-page',bp:'butter',logo:dark,plate:false},
  {name:'translucent-nav-worst-case',bp:'cerebrium',logo:dark,plate:true,mediumPaper:true},
  {name:'dark-blueprint-colours',bp:'cerebrium',logo:dark,plate:true,keepColours:false},
  {name:'wordmark',bp:'cerebrium',logo:dark,plate:false,keepLogo:false},
 ];
 direction.kind='software';direction.brand={...direction.brand,name:'Test company',accent:'#242424',paper:'#fbfaf7',ink:'#111111'};
 direction.hero={...direction.hero,media:'',cta:'Start free',cta_href:'https://source.example/start',ui:{move:'split'}};
 direction.nav={...direction.nav,cta:'Start free'};
 const inventory={actions:[{text:'Start free',href:'https://source.example/start'}]};
 for(const c of cases){
  const d=structuredClone(direction);if(c.mediumPaper){d.brand.paper='#7c7c7c';d.brand.ink='#ffffff'}
  for(const [name,value] of [['direction',d],['assets',{logo:{data:c.logo}}],['inventory',inventory],['images',[]],['brief',{keepLogo:c.keepLogo!==false,keepColours:c.keepColours!==false}]])fs.writeFileSync(path.join(dir,`${name}.json`),JSON.stringify(value));
  const out=path.join(dir,`${c.name}.html`),r=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,c.bp,out],{encoding:'utf8'});assert.equal(r.status,0,r.stderr);
  const before=Object.fromEntries(['direction','assets','inventory','images','brief'].map(n=>[n,crypto.createHash('sha256').update(fs.readFileSync(path.join(dir,`${n}.json`))).digest('hex')]));
  for(const width of [320,390,1440]){
   const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await page.route(/^https?:/,route=>route.abort());await page.goto(pathToFileURL(out).href+'?nomotion=1',{waitUntil:'load'});
   const logo=page.locator('nav .logo');
   if(c.keepLogo===false){assert.equal(await logo.count(),0);assert.equal(await page.locator('nav .wordmark').count(),1)}else{
    assert.equal(await logo.count(),1);assert.equal(await logo.getAttribute('src'),c.logo,`${c.name}: original image unchanged`);
    const info=await page.locator('nav .logo-surface').evaluate(e=>({bg:getComputedStyle(e).backgroundColor,rect:e.getBoundingClientRect().toJSON()}));
    assert.equal(info.bg,c.plate?'rgb(255, 255, 255)':'rgba(0, 0, 0, 0)',`${c.name} ${width}: appropriate surface`);
    const button=await page.locator('nav .btn').boundingBox();assert.ok(button&&info.rect.right<=button.x+1,`${c.name} ${width}: logo and CTA do not overlap`);
    assert.ok(info.rect.left>=0&&info.rect.right<=width,`${c.name} ${width}: logo stays visible`);
   }
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width,`${c.name} ${width}: no overflow`);
   if(c.name==='dark-svg'){
    const btn=page.locator('.hero .btn:not(.ghost)').first();assert.equal(await btn.count(),1);
    const styles=await btn.evaluate(e=>({bg:getComputedStyle(e).backgroundColor,fg:getComputedStyle(e).color}));
    const luminance=c=>{const a=c.match(/\d+/g).slice(0,3).map(x=>{x=+x/255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4});return .2126*a[0]+.7152*a[1]+.0722*a[2]};const x=luminance(styles.bg),y=luminance(styles.fg);assert.ok((Math.max(x,y)+.05)/(Math.min(x,y)+.05)>=4.5,`${width}: CTA text contrast`);
    await page.evaluate(()=>scrollTo(0,500));await page.waitForTimeout(100);assert.match(await page.locator('nav').getAttribute('class'),/\bsolid\b/);assert.equal(await page.locator('nav .logo-surface').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(255, 255, 255)',`${width}: dark solid nav after scroll`);
   }
   if(c.mediumPaper){
    await page.evaluate(()=>{const e=document.createElement('div');e.style.cssText='position:fixed;inset:0 0 auto;height:120px;background:#000;z-index:49';document.body.append(e);scrollTo(0,500)});await page.waitForTimeout(100);
    assert.match(await page.locator('nav').getAttribute('class'),/\bsolid\b/);
    const worst=await page.locator('nav').evaluate(e=>{const c=document.createElement('canvas');c.width=c.height=1;const x=c.getContext('2d');x.fillStyle='#000';x.fillRect(0,0,1,1);x.fillStyle=getComputedStyle(e).backgroundColor;x.fillRect(0,0,1,1);return [...x.getImageData(0,0,1,1).data].slice(0,3)});
    const lum=v=>{let x=v/255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4};const bg=.2126*lum(worst[0])+.7152*lum(worst[1])+.0722*lum(worst[2]),fg=lum(41);
    assert.ok((Math.max(bg,fg)+.05)/(Math.min(bg,fg)+.05)<3,`${width}: fixture needs the surface over black`);
    assert.equal(await page.locator('nav .logo-surface').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(255, 255, 255)');
   }
   await page.close();
  }
  for(const [name,hash] of Object.entries(before))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(dir,`${name}.json`))).digest('hex'),hash);
 }
 // On a photo hero the dark logo needs a surface even if the page's normal
 // paper is light; after scrolling to the light solid nav it no longer does.
 for(const [logo,needsPlate] of [[dark,true],[light,false]]){
  const d=structuredClone(direction);d.kind='place';d.hero.media='waiter';d.hero.ui={};
  const images=JSON.parse(fs.readFileSync('tests/images.sample.json','utf8'));
  for(const [name,value] of [['direction',d],['assets',{logo:{data:logo}}],['inventory',inventory],['images',images],['brief',{keepLogo:true,keepColours:true}]])fs.writeFileSync(path.join(dir,`${name}.json`),JSON.stringify(value));
  const out=path.join(dir,'photo-nav.html'),r=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,'tengile',out],{encoding:'utf8'});assert.equal(r.status,0,r.stderr);
  for(const width of [390,1440]){
   const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await page.route(/^https?:/,route=>route.abort());await page.goto(pathToFileURL(out).href+'?nomotion=1',{waitUntil:'load'});
   assert.equal(await page.locator('.hero.has-media').count(),1);assert.match(await page.locator('nav').getAttribute('class'),/\bon-photo\b/);
   assert.equal(await page.locator('nav .logo-surface').evaluate(e=>getComputedStyle(e).backgroundColor),needsPlate?'rgb(255, 255, 255)':'rgba(0, 0, 0, 0)');
   await page.evaluate(()=>scrollTo(0,900));await page.waitForTimeout(100);assert.match(await page.locator('nav').getAttribute('class'),/\bsolid\b/);
   assert.equal(await page.locator('nav .logo-surface').evaluate(e=>getComputedStyle(e).backgroundColor),'rgba(0, 0, 0, 0)');await page.close();
  }
 }
 // Use a saved real job when supplied; otherwise exercise the same paths with
 // a source-backed fixture. Include transparent secondary actions by computing
 // their foreground over their actual opaque ancestor backgrounds.
 const captured=process.env.CAL_ARTIFACT_DIR;
 if(captured){for(const name of ['direction','assets','inventory','images'])fs.copyFileSync(path.join(captured,`${name}.json`),path.join(dir,`${name}.json`));}
 else {
  const d=structuredClone(direction);d.beats=[{id:'pricing',type:'ledger',h2:'Plans',items:[['Basic','$10']],cta:'Start free',cta_href:'https://source.example/start'}];
  for(const [name,value] of [['direction',d],['assets',{logo:{data:dark}}],['inventory',inventory],['images',[]]])fs.writeFileSync(path.join(dir,`${name}.json`),JSON.stringify(value));
 }
 const ratio=async el=>el.evaluate(e=>{
  const c=document.createElement('canvas');c.width=c.height=1;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,1,1);
  const nodes=[];for(let n=e;n&&n.nodeType===1;n=n.parentElement)nodes.push(n);nodes.reverse();
  for(const n of nodes){x.fillStyle=getComputedStyle(n).backgroundColor;x.fillRect(0,0,1,1)}
  const bg=[...x.getImageData(0,0,1,1).data].slice(0,3);let alpha=1;for(const n of nodes)alpha*=parseFloat(getComputedStyle(n).opacity);x.globalAlpha=alpha;x.fillStyle=getComputedStyle(e).color;x.fillRect(0,0,1,1);const fg=[...x.getImageData(0,0,1,1).data].slice(0,3);
  const lum=a=>a.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);const a=lum(bg),b=lum(fg);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
 });
 for(const bp of ['butter','cerebrium'])for(const keepColours of [false,true]){
  fs.writeFileSync(path.join(dir,'brief.json'),JSON.stringify({keepLogo:true,keepColours}));const out=path.join(dir,`${bp}-${keepColours}.html`),r=spawnSync(process.env.PYTHON||'python3',['lib/render/render_bp.py',dir,bp,out],{encoding:'utf8'});assert.equal(r.status,0,r.stderr);
  for(const width of [390,1440]){
   const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await page.route(/^https?:/,route=>route.abort());await page.goto(pathToFileURL(out).href+'?nomotion=1',{waitUntil:'load'});
   assert.ok(await page.locator('nav .btn').count(),`${bp}/${keepColours}/${width}: nav CTA exists`);
   assert.ok(await page.locator('.hero .btn').count(),`${bp}/${keepColours}/${width}: hero CTA exists`);
   if(captured)assert.ok(await page.locator('#pricing .btn').count(),`${bp}/${keepColours}/${width}: captured pricing CTA exists`);
   for(const selector of ['nav .btn','.hero .btn','#pricing .btn'])for(const el of await page.locator(selector).all())assert.ok(await ratio(el)>=4.5,`${bp}/${keepColours}/${width} ${selector}: actual text contrast`);
   await page.evaluate(()=>scrollTo(0,500));await page.waitForTimeout(100);assert.match(await page.locator('nav').getAttribute('class'),/\bsolid\b/);
   for(const el of await page.locator('nav .btn').all())assert.ok(await ratio(el)>=4.5,`${bp}/${keepColours}/${width}: nav CTA after scroll`);
   await page.close();
  }
 }
 console.log(`${cases.length} logo cases at 320/390/1440: source pixels, surfaces, CTA contrast and layout pass`);
}finally{if(browser)await browser.close();fs.rmSync(dir,{recursive:true,force:true})}
