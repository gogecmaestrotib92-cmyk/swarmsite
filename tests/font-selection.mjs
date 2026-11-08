import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-font-selection-'));
const sample = JSON.parse(fs.readFileSync('tests/direction.sample.json', 'utf8'));
const python = process.env.PYTHON || 'python3';
const render = (hint, keep = true) => {
  const d = structuredClone(sample);
  d.brand.keep_font = true;
  d.brand.font_hint = hint;
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(d));
  fs.writeFileSync(path.join(dir, 'brief.json'), JSON.stringify({ keepFont: keep }));
  const result = spawnSync(python, ['lib/render/render_bp.py', dir, 'butter', path.join(dir, 'render.html')], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  return fs.readFileSync(path.join(dir, 'render.html'), 'utf8');
};
let browser;
try {
  for (const file of ['images', 'assets', 'inventory']) fs.copyFileSync(`tests/${file}.sample.json`, path.join(dir, `${file}.json`));
  const html = render(' cal sans ');
  assert.match(html, /--display:'Cal Sans','Instrument Sans',system-ui,sans-serif/);
  assert.match(html, /family=Cal\+Sans/);
  // A rejected family cannot inject into the style element, a font URL, or HTML.
  const hostile = `x';}</style><script>window.fontInjected=1</script><style>/*`;
  const rejected = render(hostile);
  assert.ok(!rejected.includes(hostile));
  assert.match(rejected, /--display:'Instrument Sans',system-ui,sans-serif/);
  assert.doesNotMatch(rejected, /family=Cal\+Sans/);
  fs.writeFileSync(path.join(dir, 'hostile.html'), rejected);
  assert.match(render('No Such Family'), /--display:'Instrument Sans',system-ui,sans-serif/);
  assert.match(render('Cal Sans', false), /--display:'Instrument Sans',system-ui,sans-serif/);
  render('Cal Sans');
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  const hostilePage = await browser.newPage();
  await hostilePage.goto(pathToFileURL(path.join(dir, 'hostile.html')).href + '?nomotion=1');
  assert.equal(await hostilePage.evaluate(() => window.fontInjected), undefined);
  const fontUrls = await hostilePage.locator('link[rel="stylesheet"]').evaluateAll(links => links.map(link => link.href));
  assert.ok(fontUrls.every(url => new URL(url).hostname === 'fonts.googleapis.com' && !url.includes('No+Such+Family')));
  await hostilePage.close();
  const actualFont = async (page, selector) => {
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
    const doc = await cdp.send('DOM.getDocument');
    const node = await cdp.send('DOM.querySelector', { nodeId: doc.root.nodeId, selector });
    assert.ok(node.nodeId, `missing ${selector}`);
    const { fonts } = await cdp.send('CSS.getPlatformFontsForNode', { nodeId: node.nodeId });
    await cdp.detach();
    return fonts.map(font => font.familyName);
  };
  for (const width of [390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
    const googleStyles = [];
    page.on('response', response => { if (response.url().startsWith('https://fonts.googleapis.com/css2') && response.url().includes('Cal+Sans')) googleStyles.push(response.status()); });
    await page.goto(pathToFileURL(path.join(dir, 'render.html')).href + '?nomotion=1', { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    assert.ok(googleStyles.includes(200), `real Cal Sans Google stylesheet loaded at ${width}`);
    assert.ok((await actualFont(page, 'h2')).includes('Cal Sans'), `Chrome actually renders Cal Sans at ${width}`);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width);
    assert.equal(await page.evaluate(() => window.fontInjected), undefined);
    await page.close();
  }
  // A failed Cal font file should use the already allowed blueprint font.
  const fallback = await browser.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  await fallback.route('https://fonts.gstatic.com/**', route => /\/calsans\//i.test(route.request().url()) ? route.abort() : route.continue());
  await fallback.goto(pathToFileURL(path.join(dir, 'render.html')).href + '?nomotion=1', { waitUntil: 'load' });
  await fallback.evaluate(() => document.fonts.ready);
  const fallbackFonts = await actualFont(fallback, 'h2');
  assert.ok(fallbackFonts.includes('Instrument Sans'), `expected blueprint fallback, got ${fallbackFonts}`);
  assert.ok(!fallbackFonts.includes('Cal Sans'));
  await fallback.close();
  const offline = await browser.newPage({ viewport: { width: 390, height: 900 }, reducedMotion: 'reduce' });
  await offline.route(/^https?:\/\//, route => route.abort());
  await offline.goto(pathToFileURL(path.join(dir, 'render.html')).href + '?nomotion=1', { waitUntil: 'load' });
  await offline.evaluate(() => document.fonts.ready);
  assert.ok((await actualFont(offline, 'h2')).length, 'a system fallback renders when the network is unavailable');
  assert.equal(await offline.evaluate(() => document.documentElement.scrollWidth), 390);
  await offline.close();
  console.log('Whitelisted Cal Sans really renders at 390/1440; blocked font uses blueprint fallback; unknown and injected families rejected');
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
