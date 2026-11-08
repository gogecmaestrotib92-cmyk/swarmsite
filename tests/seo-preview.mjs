import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'seo-preview-'));
const fixture = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
const sourceImages = JSON.parse(fs.readFileSync('tests/images.sample.json'));
const hero = sourceImages.find(image => image.id === fixture.hero.media);
hero.alt = 'A plate of fish & potatoes "fresh"';
const feature = fixture.beats.find(beat => beat.id === 'feat');
feature.h2 = ''; feature.lede = 'The original feature introduction must stay visible.';
const inventory = {
  url: 'https://source.example/', title: 'Restaurant & café | Original',
  seo: { description: 'Portuguese food & wine "locally"', canonical: 'https://source.example/canonical', robots: 'noindex, nofollow' },
};
for (const [name, object] of [['direction.json',fixture],['images.json',sourceImages],['inventory.json',inventory]]) fs.writeFileSync(path.join(dir,name), JSON.stringify(object));
const render = (name) => {
  const html = path.join(dir,name);
  const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py',dir,'butter',html], {encoding:'utf8'});
  assert.equal(result.status, 0, result.stderr); return html;
};
let browser, app, mock;
try {
  const withMetadata = render('metadata.html');
  browser = await chromium.launch({executablePath:process.env.CHROME_PATH || undefined,args:['--no-sandbox']});
  const page = await browser.newPage({viewport:{width:1440,height:900}});
  await page.route(/^https?:\/\//, route => route.abort());
  await page.goto(`${pathToFileURL(withMetadata)}?nomotion=1`, {waitUntil:'domcontentloaded'});
  assert.equal(await page.title(), inventory.title, 'the original title is preserved');
  assert.equal(await page.locator('meta[name="description"]').getAttribute('content'), inventory.seo.description, 'the original description is preserved');
  assert.equal(await page.locator('link[rel="canonical"]').count(),0,'source canonical is not copied to preview or export');
  assert.equal(await page.locator('meta[name="robots"]').count(),0,'source robots is not copied into downloadable HTML');
  assert.equal(await page.locator('#top img').first().getAttribute('alt'), hero.alt, 'real source image keeps its author-provided alt text');
  assert.equal(await page.locator('#top h1').count(), 1, 'visible page keeps a single main heading');
  assert.equal(await page.locator('#feat .lede').innerText(), feature.lede, 'a section lede is retained even without an H2');
  assert.equal(await page.locator('#feat h2').count(), 0, 'do not invent an empty section heading');
  const metaTags = await page.locator('head meta[name="description"]').count();
  assert.equal(metaTags, 1);

  inventory.title = ''; inventory.seo.description = '';
  hero.gen = true; hero.alt = 'unverified AI description';
  fs.writeFileSync(path.join(dir,'inventory.json'), JSON.stringify(inventory));
  fs.writeFileSync(path.join(dir,'images.json'), JSON.stringify(sourceImages));
  const fallbackHtml = render('fallback.html');
  await page.goto(`${pathToFileURL(fallbackHtml)}?nomotion=1`, {waitUntil:'domcontentloaded'});
  assert.equal(await page.title(),fixture.brand.name,'brand is the fallback title');
  assert.equal(await page.locator('meta[name="description"]').getAttribute('content'),fixture.hero.lede,'visible page lede is the fallback description');
  assert.equal(await page.locator('#top img').first().getAttribute('alt'),'', 'generated visuals are not assigned unverified source alt text');
  await page.close();

  // Exercise the real Express server with a local Supabase Storage/API stand-in.
  // No production credentials or production job are used.
  const servedHtml = fs.readFileSync(withMetadata);
  mock = http.createServer((req,res) => {
    if (req.url.startsWith('/storage/v1/object/')) { res.writeHead(200,{'content-type':'text/html'});res.end(servedHtml);return; }
    res.writeHead(200,{'content-type':'application/json'}); res.end('[]');
  });
  await new Promise(resolve => mock.listen(0,'127.0.0.1',resolve));
  const reservation = http.createServer();
  await new Promise(resolve => reservation.listen(0,'127.0.0.1',resolve));
  const port = reservation.address().port;
  await new Promise(resolve => reservation.close(resolve));
  app = spawn(process.execPath,['server/index.mjs'], {cwd:process.cwd(),env:{...process.env,PORT:String(port),SUPABASE_URL:`http://127.0.0.1:${mock.address().port}`,SUPABASE_SERVICE_KEY:'local-test-not-a-secret'},stdio:['ignore','pipe','pipe']});
  let output=''; app.stdout.on('data',d => output += d); app.stderr.on('data',d => output += d);
  const started = Date.now();
  while (!output.includes('api on') && Date.now()-started<10000) {
    if (app.exitCode!==null) throw new Error(`server stopped: ${output}`);
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  assert.ok(output.includes('api on'), `server startup: ${output}`);
  const id='12345678-1234-1234-1234-123456789abc';
  const previewPage = await browser.newPage({viewport:{width:390,height:844}});
  for (const suffix of [`/p/${id}`, `/p/${id}?bp=butter`, `/jobs/${id}/art/index.html`]) {
    const response = await previewPage.goto(`http://127.0.0.1:${port}${suffix}`, {waitUntil:'domcontentloaded'});
    assert.equal(response.status(),200,`${suffix} responds`);
    assert.equal(response.headers()['x-robots-tag'],'noindex',`${suffix} must not be indexed`);
  }
  await previewPage.close();
  console.log('SEO metadata, source alt and noindex preview headers pass in Chrome');
} finally {
  if (app && app.exitCode === null && app.signalCode === null) {
    const stopped = new Promise(resolve => app.once('exit', resolve));
    app.kill('SIGTERM'); await stopped;
  }
  if (mock) await new Promise(resolve => mock.close(resolve));
  if (browser) await browser.close();
  fs.rmSync(dir,{recursive:true,force:true});
}
