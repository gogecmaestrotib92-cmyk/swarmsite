import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-beat-order-'));
const direction = JSON.parse(fs.readFileSync('tests/direction.sample.json', 'utf8'));
const feature = (id) => ({ id, type: 'features', h2: id, features: [{ title: `${id} item`, body: `${id} description` }], ui: { move: 'cards', lead: '' } });
direction.beats = [
  { id: 'first-steps', type: 'steps', h2: 'First steps', steps: ['First step', 'Second step'], ui: { move: 'cards' } },
  { ...feature('matched-features'), ui: { move: 'cards', lead: '', cols: 3 }, cta: 'Read docs', cta_href: 'https://source.example/docs', source_sections: ['s1'] },
  { id: 'review', type: 'testimonials', h2: 'Review', testimonials: [{ text: 'A helpful product', attribution: 'Pat Name', links: [{ label: 'Original review', url: 'https://source.example/review' }] }] },
  feature('unmatched-features'),
  { id: 'numbers', type: 'facts', h2: 'Numbers', facts: [['10', 'Customers'], ['20', 'Projects']] },
  { id: 'pricing', type: 'ledger', h2: 'Pricing', items: [['Basic', '$10']] },
  feature('another-unmatched'),
  { id: 'questions', type: 'faq', h2: 'Questions', items: [['How does this work?', 'It works well.']] },
  { id: 'closing', type: 'form', h2: 'Contact', cta: 'Contact us' },
];
const inventory = { actions: [{ text: 'Read docs', href: 'https://source.example/docs' }], sourceCoverage: { sections: [{ id: 's1', title: 'Original section', headingLevel: 'H2', kind: 'section', sourceActionsVersion: 1, sourceActions: [{ label: 'Read stories', url: 'https://source.example/stories' }] }] } };
for (const [name, value] of [['direction.json', direction], ['inventory.json', inventory], ['images.json', []]]) fs.writeFileSync(path.join(dir, name), JSON.stringify(value));
let browser;
try {
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox'] });
  const blueprints = fs.readdirSync('lib/blueprints').filter(x => x.endsWith('.bp.json'));
  assert.equal(blueprints.length, 12);
  for (const name of blueprints) {
    const bp = name.replace('.bp.json', '');
    const html = path.join(dir, `${bp}.html`);
    const result = spawnSync(process.env.PYTHON || 'python3', ['lib/render/render_bp.py', dir, bp, html], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    for (const width of [390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
      await page.goto(pathToFileURL(html).href + '?nomotion=1');
      const expected = direction.beats.map(x => x.id);
      const actual = await page.locator('section.sec').evaluateAll((nodes, ids) => nodes.map(n => n.id).filter(id => ids.includes(id)), expected);
      assert.deepEqual(actual, expected, `${bp} ${width}: matched and unmatched beats keep direction order`);
      for (const [id, selector, expectedText] of [['matched-features', 'a[href="https://source.example/docs"]', 'Read docs'], ['matched-features', 'a[href="https://source.example/stories"]', 'Read stories'], ['review', 'a[href="https://source.example/review"]', 'Original review']]) {
        const link = page.locator(`#${id} ${selector}`);
        assert.equal(await link.count(), 1, `${bp} ${id} keeps ${expectedText}`);
        assert.match(await link.textContent(), new RegExp(expectedText));
      }
      for (const id of ['matched-features', 'unmatched-features', 'another-unmatched']) assert.equal(await page.getByText(`${id} description`, { exact: true }).count(), 1, `${bp}: ${id} content`);
      assert.equal(await page.locator('#questions details').count(), 1);
      if (bp === 'cerebrium') {
        assert.match(await page.locator('#numbers').getAttribute('class'), /\bnumbers\b/);
        assert.match(await page.locator('#numbers').getAttribute('class'), /\bband-dark\b/);
      }
      if (bp === 'white-desert') assert.equal(await page.locator('#matched-features .grid').evaluate(el => el.style.getPropertyValue('--n')), '2', 'recipe variant stays with its matched beat');
      await page.close();
    }
  }
  console.log(`Recipe order, content, links and slot band verified in ${blueprints.length} blueprints on desktop and mobile`);
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
