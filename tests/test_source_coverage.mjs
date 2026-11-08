import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-coverage-'));
const topics = ['Booking', 'How it works', 'Features', 'Integrations', 'Automation', 'Customer proof', 'Testimonials', 'Events', 'Enterprise', 'FAQ', 'Final contact'];
const links = [['/pricing','Pricing'], ['/features','Features'], ['/menu','Menu'], ['/contact','Contact'], ['/about','About'], ['/privacy','Privacy'], ['/login','Login'], ['/?add-to-cart=1','Add to cart']];
let unexpectedActions = 0;
const server = http.createServer((req, res) => {
  if (req.url === '/unexpected-action') { unexpectedActions++; res.writeHead(204); res.end(); return; }
  if (req.url === '/robots.txt') { res.writeHead(200, {'content-type':'text/plain'}); res.end('User-agent: *\nSitemap: http://127.0.0.1:' + server.address().port + '/sitemap.xml'); return; }
  if (req.url === '/sitemap.xml') { res.writeHead(200, {'content-type':'application/xml'}); res.end('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>http://127.0.0.1:' + server.address().port + '/sitemap-only</loc></url></urlset>'); return; }
  if (req.url === '/empty') { res.writeHead(200, {'content-type':'text/html'}); res.end('<title>Empty</title><p>Loading</p>'); return; }
  if (req.url === '/missing') { res.writeHead(404); res.end('Missing'); return; }
  res.writeHead(200, {'content-type': 'text/html; charset=utf-8'});
  const isHome = req.url === '/';
  const nav = isHome ? `<nav>${links.map(([href, label]) => `<a href="${href}">${label}</a>`).join(' ')} <a href="https://outside.example/x">Other site</a></nav>` : '';
  const nested = req.url === '/features' ? '<a href="/nested">Nested page</a><a href="/missing">Missing page</a><a href="/empty">Empty page</a>' : '';
  const filler = 'Readable, useful, specific content about this business and its services for real customers. '.repeat(40);
  const sections = topics.map((topic, n) => `<section id="part-${n}"><h2>${topic}</h2><p>Distinct evidence ${n + 1}. ${filler}</p>${n === 0 ? '<section><h3>Nested capability</h3><p>This child presents a separate capability and its details.</p></section>' : ''}${topic === 'Customer proof' ? '<button aria-expanded="false" aria-controls="case-study">A customer story</button><div id="case-study" hidden>Real customer evidence</div>' : ''}${topic === 'FAQ' ? `<details><summary>Can I book a room?</summary><p>Yes, reserve a room by telephone.</p><script>doNotExposeSecret()</script></details><button aria-expanded="false" aria-controls="answer-2" onclick="fetch('/unexpected-action')">Are pets welcome?</button><div id="answer-2" hidden>Yes, on the terrace.</div><button aria-expanded="false" aria-controls="not-loaded" onclick="fetch('/unexpected-action')">How do I order?</button><button id="q4" aria-expanded="false" onclick="fetch('/unexpected-action')">Can I cancel?</button><div role="region" aria-labelledby="q4" hidden>Cancel by phone.</div><h3>Is parking free?</h3><p>Parking is free.</p>` : ''}</section>`).join('');
  const meta = `<meta name="description" content="A real local description"><meta name="robots" content="index,follow"><link rel="canonical" href="/canonical"><link rel="alternate" hreflang="es" href="/es"><script type="application/ld+json">{"@type":"Organization","name":"A cafe"}</script><script type="application/ld+json">not-json</script>`;
  res.end(`<!doctype html><html lang="en"><head><title>Coverage fixture</title>${meta}<style>section{min-height:130px}</style></head><body>${nav}${nested}<main><h1>Original content</h1><p>${filler}</p>${sections}<div><h2>Bare service</h2><p>This useful service is in a div rather than a section.</p></div></main><footer>Footer is not an independent content section.</footer></body></html>`);
});
try {
 await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
 const url = `http://127.0.0.1:${server.address().port}/`;
 const child = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--site-wide', '--out', dir], {stdio:['ignore','ignore','pipe']});
 let stderr = ''; child.stderr.on('data', c => {stderr += c});
 const code = await new Promise((resolve,reject) => {child.on('error',reject);child.on('close',resolve)});
 assert.equal(code, 0, stderr);
 const slug = url.replace(/^https?:\/\//,'').replace(/[^a-z0-9.-]+/gi,'_').replace(/_+$/,'').toLowerCase();
 const inv = JSON.parse(fs.readFileSync(path.join(dir,slug,'inventory.json')));
 assert.ok(inv.copy.text.length > 12000, 'source copy continues beyond the old 12000-character cap');
 assert.deepEqual(inv.sourceCoverage.sections.map(x=>x.title), [topics[0], 'Nested capability', ...topics.slice(1), 'Bare service'], 'all meaningful homepage sections remain in the catalog');
 assert.ok(!inv.sourceCoverage.sections[0].text.includes('Nested capability'), 'nested section content is not duplicated');
 assert.ok(inv.sourceCoverage.sections.find(x=>x.title==='Final contact').text.includes('Distinct evidence 11'), 'content after the legacy body cutoff remains available');
 const faq = inv.sourceCoverage.sections.find(x=>x.title === 'FAQ').faq;
 assert.deepEqual(faq.map(x=>[x.question,x.answer,x.status]), [['Can I book a room?', 'Yes, reserve a room by telephone.', 'readable'], ['Are pets welcome?', 'Yes, on the terrace.', 'readable'], ['How do I order?', '', 'unavailable'], ['Can I cancel?', 'Cancel by phone.', 'readable'], ['Is parking free?', 'Parking is free.', 'readable']]);
 assert.equal(inv.sourceCoverage.sections.find(x=>x.title === 'Customer proof').faq.length,0, 'a customer story accordion is not an FAQ');
 assert.equal(unexpectedActions,0, 'capture must not click disclosure controls');
 assert.ok(!inv.sourceCoverage.sectionsTruncated);
 const byPath = new Map(inv.sourceCoverage.routes.map(x=>[new URL(x.url).pathname,x]));
 assert.equal(inv.sourceCoverage.routeLimit,50);
 for (const p of ['/pricing','/features','/menu','/contact']) assert.equal(byPath.get(p).status,'visited');
 assert.equal(byPath.get('/about').status,'visited');
 assert.equal(byPath.get('/privacy').status,'visited');
 assert.equal(byPath.get('/nested').status,'visited', 'links found on a subpage are followed');
 assert.equal(new URL(byPath.get('/nested').discoveredFrom).pathname,'/features');
 assert.equal(byPath.get('/missing').status,'failed');
 assert.equal(byPath.get('/empty').status,'failed', 'a blank page is not counted as read');
 assert.equal(byPath.get('/sitemap-only').status,'visited', 'sitemap-only routes are read');
 assert.equal(inv.sourceCoverage.contentTruncated,true, 'truncated page text is reported');
 assert.equal(inv.sourceCoverage.complete,false, 'failed routes are not reported as complete');
 assert.equal(byPath.get('/login').status,'excluded');
 assert.equal(inv.sourceCoverage.routes.find(r=>new URL(r.url).searchParams.has('add-to-cart')).status,'excluded');
 assert.equal(inv.sourceCoverage.routes.length,12, 'external route is not included');
 assert.equal(inv.seo.description,'A real local description');
 assert.equal(inv.seo.canonical,new URL('/canonical',url).href);
 assert.equal(inv.seo.robots,'index,follow');
 assert.deepEqual(inv.seo.hreflang,[{lang:'es',href:new URL('/es',url).href}]);
 const {raw,...sd}=inv.seo.structuredData; assert.deepEqual(sd,{jsonLdCount:2,invalidJsonLd:1,types:['Organization']}); assert.equal(raw.length,1,'only the valid JSON-LD block is carried verbatim'); assert.ok(raw[0].includes('Organization'));
 assert.equal(inv.sourcePages[0].seo.description,'A real local description', 'subpage metadata is preserved');
 const limited = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--site-wide', '--out', path.join(dir,'limited')], {env:{...process.env, SWARM_CRAWL_PAGE_LIMIT:'1'},stdio:['ignore','ignore','pipe']});
 let limitedError=''; limited.stderr.on('data', c => {limitedError += c});
 assert.equal(await new Promise((resolve,reject) => {limited.on('error',reject);limited.on('close',resolve)}), 0, limitedError);
 const partial = JSON.parse(fs.readFileSync(path.join(dir,'limited',slug,'inventory.json')));
 assert.equal(partial.sourceCoverage.attempted,1);
 assert.ok(partial.sourceCoverage.routes.some(r=>r.status==='limit' && r.reason==='Page limit reached'));
 assert.equal(partial.sourceCoverage.complete,false);
 console.log('Source sections, route coverage and source SEO metadata preserved');
} finally { await new Promise(resolve => server.close(resolve));fs.rmSync(dir,{recursive:true,force:true}); }
