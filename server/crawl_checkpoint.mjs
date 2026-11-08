/* Immutable private checkpoint. Upload must finish before publishing its key in
   the leased job row. A failed upload can never advance the durable pointer. */
import fs from 'node:fs'; import path from 'node:path'; import crypto from 'node:crypto'; import zlib from 'node:zlib';
const FILES=['inventory.json','site-analysis.json','assets.json','images.json','geometry.json','mobile.json','before-desktop.png','before-mobile.png','before-hero.jpg','before-full.jpg'];
const MAX_UNCOMPRESSED=80*1024*1024;
export async function saveCrawlCheckpoint(storage, jobId, dir) {
 const files={}; let total=0;
 for (const name of FILES) {const fp=path.join(dir,name); if(!fs.existsSync(fp)) continue; const data=fs.readFileSync(fp); total+=data.length;if(total>MAX_UNCOMPRESSED) throw new Error('Crawl checkpoint too large');files[name]=data.toString('base64');}
 if(!files['inventory.json'] || !files['assets.json'] || !files['images.json']) throw new Error('Crawl checkpoint is incomplete');
 const bytes=zlib.gzipSync(Buffer.from(JSON.stringify({version:1,files})),{level:5}); const hash=crypto.createHash('sha256').update(bytes).digest('hex');
 const key=`${jobId}/${crypto.randomUUID()}.json.gz`; const {error}=await storage.upload(key,bytes,{contentType:'application/gzip',upsert:false}); if(error)throw new Error('Crawl checkpoint upload failed: '+error.message);
 return {key,sha256:hash};
}
export async function restoreCrawlCheckpoint(storage, jobId, checkpoint, dir) {
 if(!checkpoint || typeof checkpoint.key!=='string' || !checkpoint.key.startsWith(jobId+'/') || !/^[a-f0-9]{64}$/.test(checkpoint.sha256||'')) throw new Error('Invalid crawl checkpoint reference');
 const {data,error}=await storage.download(checkpoint.key);if(error||!data)throw new Error('Crawl checkpoint unavailable');const bytes=Buffer.from(await data.arrayBuffer());
 if(crypto.createHash('sha256').update(bytes).digest('hex')!==checkpoint.sha256)throw new Error('Crawl checkpoint checksum mismatch');
 const payload=JSON.parse(zlib.gunzipSync(bytes,{maxOutputLength:MAX_UNCOMPRESSED*2}).toString('utf8'));
 if(payload.version!==1||!payload.files||!payload.files['inventory.json']||!payload.files['assets.json']||!payload.files['images.json']) throw new Error('Crawl checkpoint is incomplete');
 const decoded={};let total=0;for(const [name,encoded] of Object.entries(payload.files)){if(!FILES.includes(name)||typeof encoded!=='string')throw new Error('Invalid crawl checkpoint file');const b=Buffer.from(encoded,'base64');total+=b.length;if(total>MAX_UNCOMPRESSED)throw new Error('Crawl checkpoint too large');decoded[name]=b;}
 JSON.parse(decoded['inventory.json'].toString('utf8'));JSON.parse(decoded['assets.json'].toString('utf8'));JSON.parse(decoded['images.json'].toString('utf8'));
 fs.mkdirSync(dir,{recursive:true});for(const [name,bytes] of Object.entries(decoded)){const tmp=path.join(dir,`${name}.restore`);fs.writeFileSync(tmp,bytes);fs.renameSync(tmp,path.join(dir,name));}
}
