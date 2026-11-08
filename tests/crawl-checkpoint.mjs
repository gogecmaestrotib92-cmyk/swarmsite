import assert from 'node:assert/strict';import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import {saveCrawlCheckpoint,restoreCrawlCheckpoint} from '../server/crawl_checkpoint.mjs';
const base=fs.mkdtempSync(path.join(os.tmpdir(),'crawl-checkpoint-')); const from=path.join(base,'a'),to=path.join(base,'b');fs.mkdirSync(from);const objects=new Map();
const store={async upload(k,b){objects.set(k,Buffer.from(b));return {error:null}},async download(k){const b=objects.get(k);return {data:b?new Blob([b]):null,error:b?null:{message:'missing'}}}};
try {for(const f of ['inventory.json','assets.json','images.json'])fs.writeFileSync(path.join(from,f),JSON.stringify({file:f}));fs.writeFileSync(path.join(from,'before-full.jpg'),'image');
 const c=await saveCrawlCheckpoint(store,'job-a',from);await restoreCrawlCheckpoint(store,'job-a',c,to);assert.deepEqual(JSON.parse(fs.readFileSync(path.join(to,'inventory.json'))),{file:'inventory.json'});assert.equal(fs.readFileSync(path.join(to,'before-full.jpg'),'utf8'),'image');
 await assert.rejects(()=>restoreCrawlCheckpoint(store,'job-b',c,to),/Invalid/);objects.set(c.key,Buffer.from('corrupt'));await assert.rejects(()=>restoreCrawlCheckpoint(store,'job-a',c,to),/checksum/);
 const fail={async upload(){return {error:{message:'offline'}}}};await assert.rejects(()=>saveCrawlCheckpoint(fail,'job-a',from),/upload failed/);
 console.log('Private checkpoint restores complete state and rejects missing, corrupt or cross-job data');
}finally{fs.rmSync(base,{recursive:true,force:true});}
