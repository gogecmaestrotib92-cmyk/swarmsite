import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';

const extractor = fs.readFileSync('lib/blueprint/extract.js', 'utf8');
// The first intro is 220px on desktop, below the 225px split threshold;
// it grows to 228px on mobile. A second heading has the same text inside
// a retained section, so text-based deduplication would lose evidence.
const fixture = `<!doctype html><style>body{margin:0}.intro{height:220px}.big{height:1500px}
  @media(max-width:600px){.intro{height:228px}}</style>
  <main><div><div class="intro"><h2>Repeated title</h2><p>Lead.</p><h2 style="display:none">Hidden</h2></div>
  <section class="big"><h2>Repeated title</h2><p>Retained section.</p></section>
  <section class="big"><h2>Another heading</h2></section></div></main><nav><h2>Nav heading</h2></nav>`;
let browser;
try {
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  for (const width of [1440, 390]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.setContent(fixture);
    await page.evaluate(extractor);
    const text = await page.locator('#bpout pre').textContent();
    const result = JSON.parse(text.replace(/^BPSTART/, '').replace(/BPEND$/, ''));
    assert.equal(result.sections.length, width === 1440 ? 2 : 3, 'diagnostic must not add a section');
    assert.equal(result.unassignedHeadingsFound, width === 1440 ? 1 : 0);
    assert.equal(result.unassignedHeadingsTruncated, false);
    assert.equal(result.sections.filter(s => s.heads?.some(h => h.text === 'Repeated title')).length,
      width === 1440 ? 1 : 2, 'retained headings are kept even when their text repeats');
    if (width === 1440) {
      assert.equal(result.unassignedHeadings[0].text, 'Repeated title');
      assert.equal(result.unassignedHeadings[0].parentRect.h, 220);
    }
    await page.close();
  }
  console.log('Unassigned heading diagnostics preserve sections and distinct repeated titles');
} finally {
  if (browser) await browser.close();
}
