import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-source-action-paths-'));
const lib = path.join(tmp, 'lib');
// The copy lets us add a no-recipe blueprint without modifying repository files.
fs.cpSync('lib', lib, { recursive: true });
fs.copyFileSync(path.join(lib, 'blueprints/butter.bp.json'), path.join(lib, 'blueprints/nonrecipe.bp.json'));
const dir = path.join(tmp, 'fixture'); fs.mkdirSync(dir);
const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json'));
const section = { id: 's1', title: 'Original section', headingLevel: 'H2', kind: 'section',
  faq: [{ question: 'A', answer: 'B' }], testimonials: [{ text: 'Great', attribution: 'A' }],
  sourceActionsVersion: 1, sourceActions: [{ label: 'Read stories', url: 'https://source.example/stories' }],
  sourceActionsFound: 1, sourceActionsExcluded: 0, sourceActionsTruncated: false };
fs.writeFileSync(path.join(dir, 'inventory.json'), JSON.stringify({ sourceCoverage: { sections: [section] }, actions: [] }));
fs.writeFileSync(path.join(dir, 'images.json'), '[]');
const render = (beats, bp) => {
  direction.beats = beats;
  fs.writeFileSync(path.join(dir, 'direction.json'), JSON.stringify(direction));
  const result = spawnSync(process.env.PYTHON || 'python3', [path.join(lib, 'render/render_bp.py'), dir, bp, path.join(dir, 'page.html')], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  return fs.readFileSync(path.join(dir, 'page.html'), 'utf8');
};
const source = [section.id];
let browser;
try {
  let html = render([
    { id: 'empty-faq', type: 'faq', h2: 'Empty', items: [], source_sections: source },
    { id: 'valid', type: 'features', h2: 'Valid', features: [{ title: 'One', body: 'Body' }], source_sections: source },
  ], 'butter');
  assert.match(html, /<section[^>]+id="valid"[^>]*>[\s\S]*?Read stories/);
  assert.doesNotMatch(html, /<section[^>]+id="empty-faq"/);
  html = render([{ id: 'customer', type: 'testimonials', h2: 'Customers', testimonials: [{ text: 'Great', attribution: 'A' }], source_sections: source }], 'nonrecipe');
  assert.match(html, /<section[^>]+id="customer"[^>]*>[\s\S]*?Read stories/);
  html = render([{ id: 'form', type: 'form', h2: 'Contact', cta: 'Contact us', source_sections: source }], 'butter');
  assert.match(html, /<section[^>]+id="form"[^>]*>[\s\S]*?Read stories/);
  render([{ id: 'sticky-test', type: 'features', h2: 'Our steps', features: [
    { title: 'First', body: 'Hello' }, { title: 'Second', body: 'World' }, { title: 'Third', body: 'Yes' },
  ], source_sections: source, ui: { move: 'pinned-sequence' } }], 'butter');
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 390, height: 900 } });
  await page.goto(pathToFileURL(path.join(dir, 'page.html')).href);
  const link = page.getByRole('link', { name: 'Read stories' });
  await link.scrollIntoViewIfNeeded();
  await link.click({ trial: true });
  assert.notEqual(await page.locator('#sticky-test').getAttribute('data-sig'), 'pinned-sequence');
  console.log('Source actions survive owner filtering, all rendering paths and pinned-layout fallback');
} finally {
  if (browser) await browser.close();
  fs.rmSync(tmp, { recursive: true, force: true });
}
