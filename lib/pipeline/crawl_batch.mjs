#!/usr/bin/env node
/* Continue a previously captured site map. Each completed page and the queue
   are atomically checkpointed, so an interrupted batch can be resumed. */
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const dir = process.argv[2];
if (!dir) throw new Error('capture directory required');
const options = Object.fromEntries(process.argv.slice(3).map(x => x.split('=')));
const batchSize = Math.max(1, Math.min(200, Number(options['--batch']) || 25));
const duration = Math.max(1000, Math.min(480000, Number(options['--time']) || 180000));
const concurrency = Math.max(1, Math.min(4, Number(options['--workers']) || 3));
const limit = Math.max(1, Math.min(20000, Number(options['--max-routes']) || 5000));
const file = path.join(dir, 'inventory.json');
const inv = JSON.parse(fs.readFileSync(file, 'utf8'));
const coverage = inv.sourceCoverage;
if (!coverage || !Array.isArray(coverage.routes) || !Array.isArray(inv.sourcePages) || !inv.url) throw new Error('invalid source inventory');
const home = new URL(inv.url); const sourceOrigin = home.origin;
const invSrc = fs.readFileSync(path.join(ROOT, 'lib/audit/inventory.js'), 'utf8');
const start = Date.now();
const canonical = value => { try { const u = new URL(value, home); if (u.origin !== sourceOrigin || !/^https?:$/.test(u.protocol)) return '';
 u.hash=''; for (const k of [...u.searchParams.keys()]) if (/^(utm_.+|gclid|fbclid)$/i.test(k)) u.searchParams.delete(k); u.searchParams.sort(); u.pathname=u.pathname.replace(/\/+$/,'') || '/'; return u.href; } catch { return ''; } };
const homeKey = canonical(home.href);
const excluded = value => { const u=new URL(value), p=u.pathname;
 if (/(?:^|\/)(?:log[-_]?in|sign[-_]?(?:in|up)|register|registration|logout|checkout|cart|account|admin|delete|remove|unsubscribe|cancel|reset)(?:[\/._-]|$)/i.test(p) || [...u.searchParams.keys()].some(k => /^(?:add[-_]to[-_]cart|remove[-_]item|delete|unsubscribe|logout|action)$/i.test(k))) return 'Account or transactional route is not opened';
 if (/\.(?:pdf|zip|jpg|jpeg|png|webp|gif|svg|mp4|mp3|xml|json)$/i.test(p)) return 'Non-HTML asset is not opened'; return ''; };
const seen = new Map();
for (const r of coverage.routes) { const key=canonical(r.url); if (key && !seen.has(key)) seen.set(key,r); }
const progress = text => console.log(JSON.stringify({event:{role:'Reader', text}}));
const write = () => { const tmp=file+'.tmp'; fs.writeFileSync(tmp, JSON.stringify(inv)); fs.renameSync(tmp,file); };
function addRoutes(routes, from, truncated) {
 if (truncated) coverage.routesTruncated = true;
 for (const r of routes || []) { const key=canonical(r.url); if (!key || key===homeKey || seen.has(key)) continue;
  if (seen.size >= limit) { coverage.routesTruncated=true; continue; }
  const reason=excluded(key); const route={url:key,label:String(r.label||'').slice(0,100),discoveredFrom:from,status:reason?'excluded':'pending',reason:reason || 'Discovered and awaiting capture'};
  coverage.routes.push(route); seen.set(key,route);
 }
 coverage.routesFound=seen.size;
}
for (const r of coverage.routes) if (r.status==='limit' || r.status==='pending' || r.status==='reading') {
 const key=canonical(r.url), reason=key ? excluded(key) : 'Route is outside the source site';
 r.status=reason?'excluded':'pending'; r.reason=reason || 'Waiting for the next crawl batch';
}
coverage.complete=false; coverage.phase='crawling';
write();
const exe = process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH) ? process.env.CHROME_PATH : undefined;
const browser=await chromium.launch({executablePath:exe,args:['--no-sandbox','--disable-gpu']});
let started=0; const assigned=new Set();
// Continue sitemap indexes saved by the initial capture in bounded batches.
coverage.sitemapQueue = Array.isArray(coverage.sitemapQueue) ? coverage.sitemapQueue : [];
coverage.sitemapSeen = Array.isArray(coverage.sitemapSeen) ? coverage.sitemapSeen : [];
coverage.sitemapErrors = Array.isArray(coverage.sitemapErrors) ? coverage.sitemapErrors : [];
let sitemapProcessed=0;
if (coverage.sitemapQueue.length) {
 const ctx=await browser.newContext();const p=await ctx.newPage();
 try {while(coverage.sitemapQueue.length && sitemapProcessed<5 && Date.now()-start<duration){
   const candidate=canonical(coverage.sitemapQueue[0]);
   if(!candidate || coverage.sitemapSeen.includes(candidate) || !/\.xml$/i.test(new URL(candidate).pathname)){coverage.sitemapQueue.shift();write();continue;}
   sitemapProcessed++;progress(`Reading sitemap · ${new URL(candidate).pathname}`.slice(0,110));
   try {const response=await p.request.get(candidate,{timeout:5000,maxRedirects:0});if(!response.ok())throw new Error(`HTTP ${response.status()}`);
     const xml=await response.text();if(xml.length>2000000)throw new Error('Sitemap exceeds capture limit');
     const parsed=await p.evaluate(xml=>{const d=new DOMParser().parseFromString(xml,'application/xml');if(d.querySelector('parsererror'))return null;const root=d.documentElement.localName;if(root!=='urlset'&&root!=='sitemapindex')return null;return {index:root==='sitemapindex',urls:[...d.getElementsByTagNameNS('*','loc')].slice(0,5001).map(x=>x.textContent.trim())};},xml);
     if(!parsed)throw new Error('Invalid sitemap');if(parsed.urls.length>5000)coverage.routesTruncated=true;
     if(parsed.index){for(const item of parsed.urls.slice(0,5000)){const u=canonical(item);if(u&&/\.xml$/i.test(new URL(u).pathname)&&!coverage.sitemapSeen.includes(u))coverage.sitemapQueue.push(u);}}
     else addRoutes(parsed.urls.slice(0,5000).map(url=>({url,label:''})),candidate,false);
   }catch(e){coverage.sitemapErrors.push({url:candidate,reason:String(e.message||'Sitemap unavailable').slice(0,120)});}
   coverage.sitemapSeen.push(candidate);coverage.sitemapQueue.shift();write();
  }} finally {await ctx.close();}
}
const NOT_A_SITE=/checking the site connection security|checking your browser|just a moment|verify you are (a )?human|enable cookies|requires cookies|attention required|access denied|captcha|please wait while we verify|404 not found|this site can.t be reached|domain (is )?for sale|parked domain/i;
const priority = r => /menu|pricing|price|services|service|product|features|contact|about|cijene|usluge|kontakt|ponuda|carta|precios/i.test(r.url+' '+r.label) ? 0 : 1;
async function worker() {
 const context=await browser.newContext({viewport:{width:1440,height:900}});const page=await context.newPage();
 try { while (started < batchSize && Date.now()-start < duration) {
  const route=coverage.routes.filter(r=>r.status==='pending'&&!assigned.has(r)).sort((a,b)=>priority(a)-priority(b))[0]; if(!route) break;
  assigned.add(route); started++; route.status='reading'; route.reason='Capture in progress'; route.attempts=(route.attempts||0)+1; write();
  progress(`Reading page · ${route.label || new URL(route.url).pathname}`.slice(0,110));
  try {
   const response=await page.goto(route.url,{waitUntil:'domcontentloaded',timeout:12000});
   if(!response || !response.ok() || new URL(page.url()).origin!==sourceOrigin) throw new Error(response&&!response.ok()?`HTTP ${response.status()}`:'Redirected outside source site');
   await page.waitForLoadState('networkidle',{timeout:1200}).catch(()=>{});
   await page.evaluate(async()=>{for(let y=0;y<Math.min(document.body.scrollHeight,30000);y+=innerHeight){scrollTo(0,y);await new Promise(r=>setTimeout(r,40));}scrollTo(0,0)});
   const text=await page.evaluate(()=> (document.title+' '+document.body.innerText).replace(/\s+/g,' ').slice(0,1200));
   if (NOT_A_SITE.test(text)&&text.split(' ').length<140) throw new Error('Page returned a bot check or error');
   if (text.trim().split(/\s+/).filter(Boolean).length<12) throw new Error('Page contained too little readable text');
   const captured=await page.evaluate(invSrc); const id=crypto.createHash('sha256').update(route.url).digest('hex').slice(0,12);
   const previous=inv.sourcePages.findIndex(p=>canonical(p.requestedUrl || p.url)===canonical(route.url));
   const data={url:page.url(),requestedUrl:route.url,title:captured.title,navLabel:route.label,
    copy:{...captured.copy,text:captured.copy.text.slice(0,40000),textTruncated:captured.copy.text.length>40000||captured.copy.totalWords>captured.copy.text.split(/\s+/).filter(Boolean).length},
    actions:captured.actions||[],forms:captured.forms||[],seo:captured.seo,sectionsFound:captured.sourceCoverage?.sectionsFound||0,sectionsTruncated:!!captured.sourceCoverage?.sectionsTruncated,
    sections:(captured.sourceCoverage?.sections||[]).map(s=>({...s,id:`p${id}-${s.id}`}))};
   if(previous<0) inv.sourcePages.push(data); else inv.sourcePages[previous]=data;
   route.status='visited';route.reason='Source content captured; not a generated page';route.finalUrl=page.url();
   addRoutes(captured.sourceCoverage?.routes,page.url(),captured.sourceCoverage?.routesTruncated);
  } catch(e) {
   const reason=String(e.message||'Page could not be captured').slice(0,160);
   const retryable=/timeout|net::|HTTP (429|5\d\d)/i.test(reason);
   route.status=retryable&&route.attempts<2?'pending':'failed';route.reason=route.status==='pending'?'Temporary error; retry queued':reason;
   if (route.status==='pending') await new Promise(resolve=>setTimeout(resolve,1500));
  }
  assigned.delete(route); write();
 } } finally {await context.close();}
}
try {await Promise.all(Array.from({length:concurrency},worker));} finally {await browser.close();}
for(const r of coverage.routes) if(r.status==='reading'){r.status='pending';r.reason='Capture interrupted';}
const pending=coverage.routes.filter(r=>r.status==='pending').length + coverage.sitemapQueue.length;
coverage.attempted=coverage.routes.filter(r=>r.status==='visited'||r.status==='failed').length;
coverage.contentTruncated=!!inv.copy?.textTruncated || (coverage.sections||[]).some(s=>s.textTruncated||s.faqTruncated||s.panelsTruncated||s.testimonialsTruncated) || inv.sourcePages.some(p=>p.copy?.textTruncated||p.sectionsTruncated||(p.sections||[]).some(s=>s.textTruncated||s.faqTruncated||s.panelsTruncated||s.testimonialsTruncated));
coverage.complete=!pending&&!coverage.sitemapErrors.length&&!coverage.contentTruncated&&!coverage.routesTruncated&&!coverage.sectionsTruncated&&coverage.routes.every(r=>r.status==='visited'||r.status==='excluded');
coverage.phase=pending?'crawling':'finished';coverage.routeLimit=limit;write();
progress(`Site map · ${coverage.routes.filter(r=>r.status==='visited').length} read · ${pending} waiting`);
console.log(JSON.stringify({batch:{started,sitemaps:sitemapProcessed,pending,visited:coverage.routes.filter(r=>r.status==='visited').length,failed:coverage.routes.filter(r=>r.status==='failed').length}}));
