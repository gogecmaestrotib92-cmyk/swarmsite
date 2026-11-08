import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

// In an isolated tree, SWARM_RENDER_ROOT points to the candidate and cwd is
// the unchanged repository. CAL_ARTIFACT_DIR optionally uses a real job.
const root = process.cwd();
const { chromium } = createRequire(path.join(root,'package.json'))('playwright');
const candidateRoot = process.env.SWARM_RENDER_ROOT || root;
const fixture = process.env.CAL_ARTIFACT_DIR || path.join(root, 'tests');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-blueprint-colour-'));
const python = process.env.PYTHON || 'python3';
for (const key of ['direction','inventory','assets','images']) {
  const name = process.env.CAL_ARTIFACT_DIR ? `${key}.json` : `${key}.sample.json`;
  const file = path.join(fixture, name);
  if (fs.existsSync(file)) fs.copyFileSync(file, path.join(dir, `${key}.json`));
}
const render = (rendererRoot, blueprint, name) => {
  const file = path.join(dir, name);
  const r = spawnSync(python, [path.join(rendererRoot, 'lib/render/render_bp.py'), dir, blueprint, file], {encoding:'utf8', env:{...process.env,PYTHONHASHSEED:'0'}});
  assert.equal(r.status, 0, r.stderr); return file;
};
const bps = fs.readdirSync(path.join(root,'lib/blueprints')).filter(n=>n.endsWith('.bp.json')).sort();
assert.ok(bps.length > 0, 'blueprint catalog must not be empty');
const contrast = pair => {
  const lum = pair.map(s=>{ const m=s.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/); if (!m) return null;
    const v=m.slice(1).map(x=>{x=+x/255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4});return .2126*v[0]+.7152*v[1]+.0722*v[2]; });
  return lum.some(v=>v===null) ? null : (Math.max(...lum)+.05)/(Math.min(...lum)+.05);
};
let browser;
try {
  browser=await chromium.launch({executablePath:process.env.CHROME_PATH || undefined,args:['--no-sandbox']});
  for (const name of bps) {
    const blueprint=name.replace('.bp.json','');
    for (const keep of [true,false]) {
      fs.writeFileSync(path.join(dir,'brief.json'),JSON.stringify({keepColours:keep}));
      const base=render(root,blueprint,`${blueprint}-base.html`);
      const actual=render(candidateRoot,blueprint,`${blueprint}-candidate.html`);
      if (keep && root !== candidateRoot) assert.deepEqual(fs.readFileSync(actual),fs.readFileSync(base),`${blueprint}: source-color HTML byte identity`);
      for (const width of [390,1440]) {
        const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
        await page.route(/^https?:/, route=>route.abort());
        const read=async file=>{
          await page.goto(pathToFileURL(file).href+'?nomotion=1',{waitUntil:'load'});
          return page.evaluate(()=>({text:document.body.innerText,links:[...document.querySelectorAll('a')].map(e=>[e.textContent,e.getAttribute('href')]),sections:[...document.querySelectorAll('section[id]')].map(e=>e.id),
            pairs:[document.body,...document.querySelectorAll('.band-alt,.band-dark,.band-accent,.btn:not(.ghost):not(.light)')].filter(e=>e.getBoundingClientRect().width>0).map(e=>[getComputedStyle(e).backgroundColor,getComputedStyle(e).color])}));
        };
        const before=await read(base),after=await read(actual);
        assert.deepEqual(after.text,before.text,`${blueprint}: text`);assert.deepEqual(after.links,before.links,`${blueprint}: links`);assert.deepEqual(after.sections,before.sections,`${blueprint}: section order`);
        if(!keep) for (const pair of after.pairs) {const ratio=contrast(pair);if(ratio!==null)assert.ok(ratio>=4.5,`${blueprint} ${width}: ${pair} contrast ${ratio}`)}
        if (!keep) {
          const ghostPairs=await page.evaluate(()=>['band-alt','band-accent'].map(cls=>{
            const sec=document.createElement('div');sec.className=cls;
            const button=document.createElement('a');button.className='btn ghost';button.textContent='Test';sec.append(button);document.body.append(sec);
            const result=[getComputedStyle(sec).backgroundColor,getComputedStyle(button).color];sec.remove();return result;
          }));
          for(const pair of ghostPairs) assert.ok(contrast(pair)>=4.5,`${blueprint} ${width}: ghost ${pair}`);
        }
        if (process.env.EVIDENCE_DIR && ['butter','cerebrium'].includes(blueprint)) await page.screenshot({path:path.join(process.env.EVIDENCE_DIR,`${blueprint}-${keep?'source':'blueprint'}-${width}.png`)});
        await page.close();
      }
    }
  }
  console.log(`${bps.length} blueprints × source/blueprint palettes × 390/1440: source byte identity, content, links, and opaque component contrast pass`);
} finally {if(browser) await browser.close();fs.rmSync(dir,{recursive:true,force:true});}
