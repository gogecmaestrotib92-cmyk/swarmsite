import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-coverage-'));
const topics = ['Booking', 'How it works', 'Features', 'Integrations', 'Automation', 'Customer proof', 'Testimonials', 'Events', 'Enterprise', 'FAQ', 'Final contact'];
const links = [['/pricing','Pricing'], ['/features','Features'], ['/menu','Menu'], ['/contact','Contact'], ['/about','About'], ['/privacy','Privacy'], ['/login','Login']];
let unexpectedActions = 0;
const server = http.createServer((req, res) => {
  if (req.url === '/unexpected-action') { unexpectedActions++; res.writeHead(204); res.end(); return; }
  res.writeHead(200, {'content-type': 'text/html; charset=utf-8'});
  const isHome = req.url === '/';
  const nav = isHome ? `<nav>${links.map(([href, label]) => `<a href="${href}">${label}</a>`).join(' ')} <a href="https://outside.example/x">Other site</a></nav>` : '';
  const filler = 'Readable, useful, specific content about this business and its services for real customers. '.repeat(20);
  const sections = topics.map((topic, n) => `<section id="part-${n}"><h2>${topic}</h2><p>Distinct evidence ${n + 1}. ${filler}</p>${n === 0 ? '<section><h3>Nested capability</h3><p>This child presents a separate capability and its details.</p></section>' : ''}${topic === 'Customer proof' ? '<button aria-expanded="false" aria-controls="case-study">A customer story</button><div id="case-study" hidden>Real customer evidence</div>' : ''}${topic === 'FAQ' ? `<details><summary>Can I book a room?</summary><p>Yes, reserve a room by telephone.</p><script>doNotExposeSecret()</script></details><button aria-expanded="false" aria-controls="answer-2" onclick="fetch('/unexpected-action')">Are pets welcome?</button><div id="answer-2" hidden>Yes, on the terrace.</div><button aria-expanded="false" aria-controls="not-loaded" onclick="fetch('/unexpected-action')">How do I order?</button><button id="q4" aria-expanded="false" onclick="fetch('/unexpected-action')">Can I cancel?</button><div role="region" aria-labelledby="q4" hidden>Cancel by phone.</div><h3>Is parking free?</h3><p>Parking is free.</p>` : ''}</section>`).join('');
  const meta = `<meta name="description" content="A real local description"><meta name="robots" content="index,follow"><link rel="canonical" href="/canonical"><link rel="alternate" hreflang="es" href="/es"><script type="application/ld+json">{"@type":"Organization","name":"A cafe"}</script><script type="application/ld+json">not-json</script>`;
  res.end(`<!doctype html><html lang="en"><head><title>Coverage fixture</title>${meta}<style>section{min-height:130px}</style></head><body>${nav}<main><h1>Original content</h1><p>${filler}</p>${sections}<div><h2>Bare service</h2><p>This useful service is in a div rather than a section.</p></div></main><footer>Footer is not an independent content section.</footer></body></html>`);
});
try {
 await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
 const url = `http://127.0.0.1:${server.address().port}/`;
 const child = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--out', dir], {stdio:['ignore','ignore','pipe']});
 let stderr = ''; child.stderr.on('data', c => {stderr += c});
 const code = await new Promise((resolve,reject) => {child.on('error',reject);child.on('close',resolve)});
 assert.equal(code, 0, stderr);
 const slug = url.replace(/^https?:\/\//,'').replace(/[^a-z0-9.-]+/gi,'_').replace(/_+$/,'').toLowerCase();
 const inv = JSON.parse(fs.readFileSync(path.join(dir,slug,'inventory.json')));
 assert.equal(inv.copy.text.length, 12000, 'fixture makes the legacy full-page text reach its cap');
 assert.deepEqual(inv.sourceCoverage.sections.map(x=>x.title), [topics[0], 'Nested capability', ...topics.slice(1), 'Bare service'], 'all meaningful homepage sections remain in the catalog');
 assert.ok(!inv.sourceCoverage.sections[0].text.includes('Nested capability'), 'nested section content is not duplicated');
 assert.ok(inv.sourceCoverage.sections.find(x=>x.title==='Final contact').text.includes('Distinct evidence 11'), 'content after the legacy body cutoff remains available');
 const faq = inv.sourceCoverage.sections.find(x=>x.title === 'FAQ').faq;
 assert.deepEqual(faq.map(x=>[x.question,x.answer,x.status]), [['Can I book a room?', 'Yes, reserve a room by telephone.', 'readable'], ['Are pets welcome?', 'Yes, on the terrace.', 'readable'], ['How do I order?', '', 'unavailable'], ['Can I cancel?', 'Cancel by phone.', 'readable'], ['Is parking free?', 'Parking is free.', 'readable']]);
 assert.equal(inv.sourceCoverage.sections.find(x=>x.title === 'Customer proof').faq.length,0, 'a customer story accordion is not an FAQ');
 assert.equal(unexpectedActions,0, 'capture must not click disclosure controls');
 assert.ok(!inv.sourceCoverage.sectionsTruncated);
 const byPath = new Map(inv.sourceCoverage.routes.map(x=>[new URL(x.url).pathname,x]));
 assert.equal(inv.sourceCoverage.routeLimit,4);
 for (const p of ['/pricing','/features','/menu','/contact']) assert.equal(byPath.get(p).status,'visited');
 assert.equal(byPath.get('/about').status,'limit');
 assert.equal(byPath.get('/privacy').status,'excluded');
 assert.equal(byPath.get('/login').status,'excluded');
 assert.equal(inv.sourceCoverage.routes.length,7, 'external route is not included');
 assert.equal(inv.seo.description,'A real local description');
 assert.equal(inv.seo.canonical,new URL('/canonical',url).href);
 assert.equal(inv.seo.robots,'index,follow');
 assert.deepEqual(inv.seo.hreflang,[{lang:'es',href:new URL('/es',url).href}]);
 assert.deepEqual(inv.seo.structuredData,{jsonLdCount:2,invalidJsonLd:1,types:['Organization']});
 assert.equal(inv.sourcePages[0].seo.description,'A real local description', 'subpage metadata is preserved');
 console.log('Source sections, route coverage and source SEO metadata preserved');
} finally { await new Promise(resolve => server.close(resolve));fs.rmSync(dir,{recursive:true,force:true}); }
