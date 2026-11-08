import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';

const html = fs.readFileSync('web/app.html', 'utf8');
const report = {
  scope: 'single_page_preview',
  source_catalog_truncated: true,
  sections: [
    { title: 'Frequently asked questions', status: 'needs_review', faq: [
      { question: 'What is included?', status: 'text_detected' },
      { question: 'Can I cancel?', status: 'source_unavailable' },
      { question: 'Where is the rest?', status: 'source_incomplete' },
      { question: 'Is support included?', status: 'needs_review' },
    ] },
    { title: 'Booking tools', status: 'text_detected', source_text_truncated: true,
      testimonials: [{attribution:'Ada',status:'text_detected'},{attribution:'<img src=x onerror=alert(1)>',status:'needs_review'}],
      panels: [{trigger:'Case study',status:'needs_review',source_excerpt:'Captured <img src=x> details.',source_links:[{label:'Original story',url:'https://example.com/customer'},{label:'Unsafe panel link',url:'javascript:alert(1)'}]},{trigger:'Hidden panel',status:'source_incomplete'}] },
    { title: '<img src=x onerror=alert(1)>', status: 'needs_review' },
  ],
  routes: [
    { label: 'Pricing', url: 'https://example.com/pricing', status: 'linked_to_source' },
    { label: 'Unsafe', url: 'javascript:alert(1)', status: 'not_linked' },
  ],
};
const job = { id: '11111111-1111-4111-8111-111111111111', status: 'done', steps: [], result: { blueprints: ['butter', 'cerebrium'], direction: { kind: 'software', concept: 'C3', beats: [], audit_notes: ['An unverified quote was omitted for review.', '<svg onload=alert(1)>'] }, coverage: report } };
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
 for (const width of [390, 1440]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.route('**/*', async route => {
   const u = new URL(route.request().url());
   if (u.hostname === 'app.test' && u.pathname === '/app') return route.fulfill({ status: 200, contentType: 'text/html', body: html });
   if (u.hostname === 'app.test' && u.pathname === '/config.js') return route.fulfill({ status: 200, contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test';" });
   if (u.hostname === 'app.test' && u.pathname === '/js/swarm2.js') return route.fulfill({ status: 200, contentType: 'application/javascript', body: "window.Swarm2={ROLES:[],mount:()=>({phase(){},stop(){},push(){},setPage(){}})};" });
   if (u.hostname === 'api.test' && u.pathname.startsWith('/jobs/')) return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(job) });
   if (u.hostname === 'api.test' && u.pathname.startsWith('/p/')) return route.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><title>Preview</title><h1>Preview</h1>' });
   return route.abort();
  });
  await page.goto('http://app.test/app?url=example.com&job=11111111-1111-4111-8111-111111111111', { waitUntil: 'domcontentloaded' });
  await page.locator('#coverage > summary').click();
  assert.equal(await page.getByText('Frequently asked questions', { exact: true }).count(), 1);
  assert.equal(await page.getByText('This source inventory is incomplete; more sections or pages may need review.').count(), 1);
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
  const rect = await page.locator('#coveragePanel').boundingBox();
  assert.ok(rect && rect.x >= -1 && rect.x + rect.width <= width + 1, `${width}px panel fits viewport`);
  await page.locator('#variants button').nth(1).click();
  assert.equal(await page.locator('#coverage').isHidden(), true, 'primary report must not describe the alternative');
  assert.match(await page.locator('#preview').getAttribute('src'), /bp=cerebrium/);
  await page.locator('#variants button').first().click();
  assert.equal(await page.locator('#coverage').isVisible(), true, 'primary report returns with selected variant');
  await page.locator('[data-v="mobile"]').click();
  assert.match(await page.locator('#preview').getAttribute('style'), /width:\s*390px/);
  await page.close();
 }
 console.log('Coverage UI explains limits, handles variants and treats source content as text');
} finally { await browser.close(); }
