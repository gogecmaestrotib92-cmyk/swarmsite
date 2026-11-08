import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';
import {spawnSync} from 'node:child_process';import {pathToFileURL} from 'node:url';import {createRequire} from 'node:module';
const root=process.cwd(), candidate=process.env.SWARM_RENDER_ROOT||root;
const {chromium}=createRequire(path.join(root,'package.json'))('playwright');
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'swarm-context-contrast-'));
const d=JSON.parse(fs.readFileSync(path.join(root,'tests/direction.sample.json')));
const inventory={actions:[{text:'Read docs',href:'https://source.example/docs'}],sourceCoverage:{sections:[{id:'s1',title:'Source section',headingLevel:'H2',kind:'section',sourceActionsVersion:1,sourceActions:[{label:'Read original',url:'https://source.example/original'}]}]}};
const baseBeat={id:'target',type:'features',label:'Proof',h2:'A product story',lede:'Real source detail for this feature.',features:[{title:'One',body:'Original detail one'},{title:'Two',body:'Original detail two'}],source_sections:['s1'],cta:'Read docs',cta_href:'https://source.example/docs'};
const render=(tree,bp,name)=>{let out=path.join(dir,name),r=spawnSync(process.env.PYTHON||'python3',[path.join(tree,'lib/render/render_bp.py'),dir,bp,out],{encoding:'utf8',env:{...process.env,PYTHONHASHSEED:'0'}});assert.equal(r.status,0,r.stderr);return out};
let browser;
try{
  for(const name of ['images','assets'])fs.copyFileSync(path.join(root,`tests/${name}.sample.json`),path.join(dir,`${name}.json`));
  fs.writeFileSync(path.join(dir,'inventory.json'),JSON.stringify(inventory));
  browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox']});
  for(const bp of ['atelier','lpas','crav','tengile']) {
    d.kind=bp==='tengile'?'place':bp==='crav'?'product':'service';
    d.beats=[{...baseBeat,features:bp==='crav'?[{title:'One'},{title:'Two'}]:baseBeat.features,band:bp==='crav'?'accent':'alt',ui:bp==='crav'?{}:{move:'cards',lead:''}}];
    fs.writeFileSync(path.join(dir,'direction.json'),JSON.stringify(d));
    for(const keep of [true,false]){
      fs.writeFileSync(path.join(dir,'brief.json'),JSON.stringify({keepColours:keep}));
      const before=render(root,bp,`${bp}-${keep}-base.html`),after=render(candidate,bp,`${bp}-${keep}-candidate.html`);
      if(keep&&root!==candidate)assert.deepEqual(fs.readFileSync(after),fs.readFileSync(before),`${bp}: source colours unchanged`);
      if(keep)continue;
      for(const width of [390,1440]){
        const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await page.route(/^https?:/,r=>r.abort());
        await page.goto(pathToFileURL(after).href+'?nomotion=1',{waitUntil:'load'});
        const section=page.locator('#target');const cta=section.locator('.section-actions .btn');assert.equal(await cta.count(),1,`${bp}: source CTA`);
        assert.equal(await section.locator('a[href="https://source.example/original"]').count(),1,`${bp}: source link`);
        const ratio=async (selector,context)=>page.locator(selector).evaluate((el,context)=>{
          const bg=getComputedStyle(el.closest(context)).backgroundColor;
          const cs=getComputedStyle(el), cv=document.createElement('canvas');cv.width=cv.height=1;const c=cv.getContext('2d');
          function paint(color,base,alpha=1){c.clearRect(0,0,1,1);c.fillStyle=base;c.fillRect(0,0,1,1);c.globalAlpha=alpha;c.fillStyle=color;c.fillRect(0,0,1,1);c.globalAlpha=1;return [...c.getImageData(0,0,1,1).data].slice(0,3)}
          const backdrop=paint(bg,'rgb(255,255,255)');const back=`rgb(${backdrop.join(',')})`;let a=1;for(let node=el;node&&node!==el.closest(context);node=node.parentElement)a*=parseFloat(getComputedStyle(node).opacity);
          const color=paint(cs.color,back,a), button=paint(cs.backgroundColor,back,a);
          const lum=x=>x.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
          const cr=(x,y)=>{let p=lum(x),q=lum(y);return (Math.max(p,q)+.05)/(Math.min(p,q)+.05)};
          return {textBackground:cr(color,button),buttonSurround:cr(button,backdrop),textSurround:cr(color,backdrop),opacity:a,bg,color:cs.color};
        },context);
        const b=await ratio('#target .section-actions .btn','#target');assert.ok(b.textBackground>=4.5,`${bp} ${width}: button text ${JSON.stringify(b)}`);assert.ok(b.buttonSurround>=3,`${bp} ${width}: visible button ${JSON.stringify(b)}`);
        const label=await ratio('#target .source-actions a','#target');assert.ok(label.textSurround>=4.5,`${bp} ${width}: source link ${JSON.stringify(label)}`);
        if(bp==='crav'){
          assert.equal(await section.locator('.stickers').count(),0);assert.match(await section.getAttribute('class'),/stickers/);
          const lede=await ratio('#target .lede','#target');assert.ok(lede.textSurround>=4.5,`${bp} ${width}: sticker lede ${JSON.stringify(lede)}`);
        }
        console.log(`${bp} ${width} button ${b.buttonSurround.toFixed(2)}/${b.textBackground.toFixed(2)} source ${label.textSurround.toFixed(2)}`);await page.close();
      }
    }
  }
  console.log('Actual alt/accent CTAs, Crav lede, and source labels pass computed/composited contrast; source colours unchanged');
}finally{if(browser)await browser.close();fs.rmSync(dir,{recursive:true,force:true})}
