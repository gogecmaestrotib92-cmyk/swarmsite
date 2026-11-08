import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';

const html = fs.readFileSync('web/app.html', 'utf8');
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
try {
  for (const [label, error] of [
    ['new', 'The AI service is temporarily unavailable. Please try again later.'],
    ['legacy', "Traceback: anthropic.BadRequestError: Your credit balance is too low to access the Anthropic API. request_id=private-sentinel"],
    ['unrelated', 'capture failed because the source page timed out'],
  ]) {
    const page = await browser.newPage({ viewport: { width: 390, height: 900 } });
    await page.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.hostname === 'app.test' && url.pathname === '/app') return route.fulfill({ contentType: 'text/html', body: html });
      if (url.hostname === 'app.test' && url.pathname === '/config.js') return route.fulfill({ contentType: 'application/javascript', body: "window.SWARMSITE_API='https://api.test';" });
      if (url.hostname === 'app.test' && url.pathname === '/js/swarm2.js') return route.fulfill({ contentType: 'application/javascript', body: "window.Swarm2={ROLES:[],mount:()=>({phase(){},stop(){window.__swarmStopped=true},push(){},setPage(){}})};" });
      if (url.hostname === 'api.test' && url.pathname.startsWith('/jobs/')) return route.fulfill({ contentType: 'application/json', body: JSON.stringify({status:'failed', steps:[], error}) });
      return route.abort();
    });
    await page.goto('http://app.test/app?url=example.test&job=11111111-1111-4111-8111-111111111111');
    await page.getByText('That one didn’t go through.').waitFor();
    const actual = await page.locator('#err').textContent();
    assert.equal(await page.evaluate(() => window.__swarmStopped), true, 'the failed job stops the progress animation');
    if (label === 'unrelated') assert.match(actual, /capture failed because the source page timed out/);
    else {
      assert.equal(actual, 'The AI service is temporarily unavailable. Please try again later.');
      assert.doesNotMatch(await page.locator('body').innerText(), /Traceback|request_id|private-sentinel/);
    }
    await page.close();
  }
  console.log('Credit failure and legacy tracebacks are shown safely in the real app');
} finally { await browser.close(); }
