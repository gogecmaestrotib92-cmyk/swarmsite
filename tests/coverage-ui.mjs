import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';

const html = fs.readFileSync(process.env.SWARM_VARIANT_UI || 'web/app.html', 'utf8');
const report = {
  scope: 'single_page_preview',
  source_catalog_truncated: true,
  source_actions_needing_review: true,
  crawl: { complete: false, routes_visited: 1, routes_failed: 1, routes_limited: 2, routes_excluded: 1 },
  source_analysis: {complete:false,batches_completed:2,batches_total:2,missing_pages:1,missing_sections:3,context_truncated:true},
  source_pages: [{title: 'Pricing details', sections_truncated: true, sections: [{title:'Enterprise plan',status:'needs_review'}]}],
  sections: [
    { title: 'Frequently asked questions', status: 'needs_review', faq: [
      { question: 'What is included?', status: 'text_detected' },
      { question: 'Can I cancel?', status: 'source_unavailable' },
      { question: 'Where is the rest?', status: 'source_incomplete' },
      { question: 'Is support included?', status: 'needs_review' },
    ] },
    { title: 'Booking tools', status: 'text_detected', source_text_truncated: true, source_actions_version: 1, source_actions_truncated: true, source_actions_excluded: 2,
      source_actions: [{label:'Explore apps',url:'https://example.com/apps',status:'url_detected'},{label:'Missing <img src=x>',url:'https://example.com/missing',status:'needs_review'},{label:'Unsafe action',url:'javascript:alert(1)',status:'needs_review'},{label:'Local action',url:'http://localhost.:8080/',status:'needs_review'}],
      testimonials: [{attribution:'Ada',status:'text_detected'},{attribution:'<img src=x onerror=alert(1)>',status:'needs_review'}],
      panels: [{trigger:'Case study',status:'needs_review',source_excerpt:'Captured <img src=x> details.',source_links:[{label:'Original story',url:'https://example.com/customer'},{label:'Unsafe panel link',url:'javascript:alert(1)'}]},{trigger:'Hidden panel',status:'source_incomplete'}] },
    { title: '<img src=x onerror=alert(1)>', status: 'needs_review', source_actions_version: null, source_actions: [] },
  ],
  routes: [
    { label: 'Pricing', url: 'https://example.com/pricing', status: 'linked_to_source', capture_status:'visited' },
    { label: 'Unsafe', url: 'javascript:alert(1)', status: 'not_linked' },
  ],
};
const job = { id: '11111111-1111-4111-8111-111111111111', status: 'done', steps: [], result: { blueprints: ['butter', 'cerebrium'], direction: { kind: 'software', concept: 'C3', beats: [], audit_notes: ['An unverified quote was omitted for review.', '<svg onload=alert(1)>'] }, coverage: report } };
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
 for (const width of [390, 1440]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  let responseJob = {...job, status:'running', steps:[{id:'capture',label:'Reading',status:'running'}], result:{}};
  await page.route('**/*', async route => {
   const u = new URL(route.request().url());
   if (u.hostname === 'app.test' && u.pathname === '/app') return route.fulfill({ status: 200, contentType: 'text/html', body: html });
   if (u.hostname === 'app.test' && u.pathname === '/config.js') return route.fulfill({ status: 200, contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test';" });
   if (u.hostname === 'app.test' && u.pathname === '/js/swarm2.js') return route.fulfill({ status: 200, contentType: 'application/javascript', body: "window.__swarmEvents=[];window.Swarm2={ROLES:[],mount:()=>({phase(){},stop(){},push(e){window.__swarmEvents.push(...e)},setPage(){}})};" });
   if (u.hostname === 'api.test' && u.pathname.startsWith('/jobs/')) return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(responseJob) });
   if (u.hostname === 'api.test' && u.pathname.startsWith('/p/')) return route.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><title>Preview</title><h1>Preview</h1>' });
   return route.abort();
  });
  await page.goto('http://app.test/app?url=example.com&job=11111111-1111-4111-8111-111111111111', { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => document.querySelector('#hudL').textContent === 'reading');
  const eventsSeen=await page.evaluate(()=>{const steps=[{id:'capture',label:'Reading',status:'running'}];renderSteps({status:'running',steps,result:{eventsOffset:0,events:[{role:'Reader',text:'a'},{role:'Reader',text:'b'}]}});renderSteps({status:'running',steps,result:{eventsOffset:2,events:[{role:'Reader',text:'c'},{role:'Reader',text:'d'}]}});return window.__swarmEvents.map(e=>e.text)});
  assert.deepEqual(eventsSeen,['a','b','c','d'],'agents keep receiving events after the log rolls over');
  assert.equal(await page.locator('#stage').isVisible(), true, 'loading screen stays visible before completion');
  assert.equal(await page.locator('#result').isHidden(), true, 'preview remains hidden while loading');
  const loadingHud=await page.locator('#frame .hud').boundingBox();
  assert.ok(loadingHud, 'loading HUD has a visible position');
  assert.equal(await page.evaluate(({x,y}) => !!document.elementFromPoint(x,y)?.closest('#frame .hud'), {x:loadingHud.x+loadingHud.width/2,y:loadingHud.y+loadingHud.height/2}), true, 'loading HUD is on top during the run');
  responseJob = job;
  await page.locator('#result.on').waitFor({timeout:10000});
  assert.equal(await page.locator('#stage').isHidden(), true, 'loading screen and its HUD are removed after completion');
  const header=await page.locator('.top').boundingBox(), preview=await page.locator('#preview').boundingBox();
  assert.ok(header && preview && preview.y >= header.y+header.height-1, 'preview starts below the fixed application header');
  assert.equal(await page.evaluate(({x,y}) => document.elementFromPoint(x,y)?.id === 'preview', {x:preview.x+preview.width/2,y:preview.y+Math.min(20,preview.height/2)}), true, 'header and loading UI cannot cover the top of the preview');
  await page.locator('#coverage > summary').click();
  assert.match(await page.locator('#coveragePanel').textContent(), /1 pages read · 1 unavailable · 2 not read within limits/);
  assert.match(await page.locator('#coveragePanel').textContent(), /1 pages and 3 section IDs need review/);
  assert.match(await page.locator('#coveragePanel').textContent(), /Some observations were shortened for the design agents/);
  assert.equal(await page.getByText('Read · Linked to original page').count(), 1);
  await page.getByText('Pricing details', {exact:true}).click();
  assert.equal(await page.getByText('Enterprise plan · Needs review').count(), 1);
  assert.equal(await page.getByText('Frequently asked questions', { exact: true }).count(), 1);
  assert.equal(await page.getByText('This source inventory is incomplete; more sections or pages may need review.').count(), 1);
  assert.equal(await page.getByText('Some original links need review: they may be missing, excluded from capture, or truncated.').count(), 1);
  assert.equal(await page.getByText('Links open original destinations. A URL found in the preview does not confirm its label, placement, visibility or functionality.').count(), 1);
  assert.equal(await page.getByText('Link capture truncated · 2 excluded from link capture').count(), 1);
  assert.equal(await page.getByText('Link capture unavailable').count(), 1);
  assert.equal(await page.getByText('Explore apps', {exact:true}).getAttribute('href'), 'https://example.com/apps');
  assert.equal(await page.getByText('Explore apps', {exact:true}).getAttribute('rel'), 'noopener noreferrer');
  assert.equal(await page.getByText('URL found in preview — check link').count(), 1);
  assert.equal(await page.getByText('Needs review — URL not found in preview').count(), 3);
  assert.equal(await page.getByText('Missing <img src=x>', {exact:true}).count(), 1);
  assert.equal(await page.getByText('Unsafe action', {exact:true}).evaluate(el=>el.tagName), 'SPAN');
  assert.equal(await page.getByText('Local action', {exact:true}).evaluate(el=>el.tagName), 'SPAN');
  assert.equal(await page.getByText('Matching title found — check details · Source section text was truncated').count(), 1);
  assert.equal(await page.getByText('Needs review — title not matched').count(), 2);
  assert.equal(await page.getByText('Linked to original page').count(), 1);
  assert.equal(await page.getByText('Question and answer found — check meaning').count(), 1);
  assert.equal(await page.getByText('Original answer unavailable').count(), 1);
  assert.equal(await page.getByText('Original answer is incomplete').count(), 1);
  assert.equal(await page.getByText('Needs review — question or answer not matched').count(), 1);
  assert.equal(await page.getByText('Text, attribution and source links found — check association').count(), 1);
  assert.equal(await page.getByText('Needs review — quote, attribution or source link not matched').count(), 1);
  assert.equal(await page.getByText('Needs review — panel text or links not matched').count(), 1);
  assert.equal(await page.getByText('Original panel evidence incomplete or unavailable').count(), 1);
  assert.equal(await page.getByText('Captured <img src=x> details.').count(), 1);
  assert.equal(await page.getByText('Original story').getAttribute('href'), 'https://example.com/customer');
  assert.equal(await page.getByText('Unsafe panel link').count(), 0);
  assert.equal(await page.getByText('An unverified quote was omitted for review.').count(), 1);
  assert.equal(await page.locator('#coveragePanel svg').count(), 0, 'audit notes must remain text');
  assert.equal(await page.locator('#coveragePanel img').count(), 0, 'untrusted titles must not inject HTML');
  assert.equal(await page.getByText('Unsafe', { exact: true }).evaluate(el => el.tagName), 'SPAN', 'unsafe source URLs must not become links');
  await page.evaluate(r=>renderCoverage({...r,crawl:{...r.crawl,scope:'landing_page_only'},routes:[{url:'https://example.com/pricing',label:'Pricing',capture_status:'not_scanned',status:'linked_to_source'}]},[]),report);
  assert.match(await page.locator('#coveragePanel').textContent(),/Analysis covers the submitted landing page. Linked pages were not scanned/);
  assert.match(await page.locator('#coveragePanel').textContent(),/Outside landing page scope/);
  await page.locator('#coverage > summary').click();
  const rect = await page.locator('#coveragePanel').boundingBox();
  assert.ok(rect && rect.x >= -1 && rect.x + rect.width <= width + 1, `${width}px panel fits viewport`);
  const bar=await page.locator('.result .bar').boundingBox();
  assert.ok(bar && rect.y >= header.y+header.height-1 && rect.y+rect.height <= bar.y-5, 'coverage panel fits between the header and result bar');
  assert.equal(await page.evaluate(({x,y}) => !!document.elementFromPoint(x,y)?.closest('#coveragePanel'), {x:rect.x+rect.width/2,y:rect.y+rect.height/2}), true, 'coverage panel is not obscured by loading HUD');
  await page.setViewportSize({width:width===390?1440:390,height:900});
  await page.waitForTimeout(100);
  const resized=await page.evaluate(()=>{const h=document.querySelector('.top').getBoundingClientRect(), p=document.querySelector('#preview').getBoundingClientRect(), c=document.querySelector('#coveragePanel').getBoundingClientRect(), b=document.querySelector('.result .bar').getBoundingClientRect();return {headerBottom:h.bottom,previewTop:p.top,panelTop:c.top,panelBottom:c.bottom,barTop:b.top};});
  assert.ok(resized.previewTop >= resized.headerBottom-1 && resized.panelTop >= resized.headerBottom-1 && resized.panelBottom <= resized.barTop-5, 'resizing recalculates header and panel positions');
  await page.setViewportSize({width,height:900});
  await page.locator('#variants button').nth(1).click();
  assert.equal(await page.locator('#coverage').isHidden(), false);
  assert.match(await page.locator('#coveragePanel').textContent(), /not available for this alternative/);
  assert.match(await page.locator('#preview').getAttribute('src'), /bp=cerebrium/);
  await page.locator('#variants button').first().click();
  assert.equal(await page.locator('#coverage').isVisible(), true, 'primary report returns with selected variant');
  await page.locator('[data-v="mobile"]').click();
  // measured, not read off the style attribute: the frame is a flex item, and a width merely written on it was ignored — the old assertion passed while the phone view did nothing
  const frameWidth = async () => Math.round(await page.locator('#preview').evaluate(f => f.getBoundingClientRect().width));
  if ((await page.viewportSize()).width > 500) assert.equal(await frameWidth(), 390, 'the phone view narrows the preview to a phone');
  assert.ok(await page.locator('.preview-stage').evaluate(s => s.classList.contains('is-phone')));
  await page.close();
 }
 console.log('Coverage UI explains limits, handles variants and treats source content as text');
} finally { await browser.close(); }
