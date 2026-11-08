import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';

const app = fs.readFileSync('web/app.html', 'utf8');
const swarm = fs.readFileSync('web/js/swarm2.js', 'utf8');
const payload = '<img src=x onerror=window.eventXss=1>';
const stepPayload = '<svg onload=window.stepXss=1>';
const job = { id: '11111111-1111-4111-8111-111111111111', status: 'running',
  steps: [{ id: 'audit', label: stepPayload, status: 'done', note: stepPayload },
    { id: 'direct', label: 'Direct', status: 'running' },
    { id: 'other', label: 'Other', status: stepPayload }],
  result: { events: [{ role: 'Copy', text: payload }, { role: stepPayload, text: payload }] } };
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.route('**/*', route => {
    const url = new URL(route.request().url());
    if (url.hostname === 'app.test' && url.pathname === '/app') return route.fulfill({ contentType: 'text/html', body: app });
    if (url.hostname === 'app.test' && url.pathname === '/config.js') return route.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test';" });
    if (url.hostname === 'app.test' && url.pathname === '/js/swarm2.js') return route.fulfill({ contentType: 'application/javascript', body: swarm });
    if (url.hostname === 'api.test' && url.pathname.startsWith('/jobs/')) return route.fulfill({ contentType: 'application/json', body: JSON.stringify(job) });
    return route.abort();
  });
  await page.goto('https://app.test/app?url=example.test&job=11111111-1111-4111-8111-111111111111', { waitUntil: 'domcontentloaded' });
  await page.locator('#log').getByText(`Copy · ${payload}`, { exact: true }).waitFor();
  assert.equal(await page.locator('#log img, #log svg').count(), 0, 'event text and role must stay text');
  assert.equal(await page.locator('#steps svg, #steps img').count(), 0, 'step fields must stay text');
  assert.equal(await page.locator('#steps .step.done').innerText(), `${stepPayload}\n${stepPayload}`);
  assert.equal(await page.locator('#steps .step.running .note').innerText(), 'working…');
  assert.equal(await page.locator('#steps .step').nth(2).getAttribute('class'), 'step');
  await page.locator('.s2-cur .tag s').filter({ hasText: payload }).first().waitFor({ timeout: 10000 });
  assert.equal(await page.locator('.s2-cur .tag s img').count(), 0, 'Swarm2 must display event text as text');
  assert.equal(await page.evaluate(() => !!(window.eventXss || window.stepXss)), false, 'no payload executes');
  await page.close();
  console.log('Live event log, steps, and Swarm2 display untrusted payloads safely');
} finally { await browser.close(); }
