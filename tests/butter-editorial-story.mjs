import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

// SWARM_RENDER_ROOT permits testing an isolated renderer tree; default is this repo.
const root = process.cwd();
const rendererRoot = process.env.SWARM_RENDER_ROOT || root;
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'butter-editorial-story-'));
const base = JSON.parse(fs.readFileSync(path.join(root, 'tests/direction.sample.json'), 'utf8'));
const features = n => Array.from({length: n}, (_, i) => ({title: `Feature ${i + 1}`, body: `Verified detail ${i + 1}`}));
const lede = n => ('A real product story carries its useful details clearly and carefully across every screen. '.repeat(3)).slice(0, n - 1).trimEnd().padEnd(n - 1, '.') + '!';
const cases = [
  {name: 'short', editorial: true, length: 35, count: 2},
  {name: 'middle', editorial: true, length: 67, count: 3},
  {name: 'long', editorial: true, length: 120, count: 6},
  {name: 'too-short', editorial: false, length: 34, count: 3},
  {name: 'too-long', editorial: false, length: 121, count: 3},
  {name: 'one-item', editorial: false, length: 67, count: 1},
  {name: 'seven-items', editorial: false, length: 67, count: 7},
  {name: 'long-heading', editorial: false, length: 67, count: 3, heading: 'A deliberately long heading that exceeds the editorial limit'},
  {name: 'photo', editorial: false, length: 67, count: 3, photo: true},
  {name: 'cards', editorial: false, length: 67, count: 3, move: 'cards'},
  {name: 'individual-images', editorial: false, length: 67, count: 3, individual: true},
  {name: 'other-blueprint', editorial: false, length: 67, count: 3, blueprint: 'cerebrium'},
  {name: 'other-kind', editorial: false, length: 67, count: 3, kind: 'place'},
  {name: 'unbroken-ascii', editorial: true, length: 40, count: 3, heading: 'W'.repeat(40), rawLede: 'W'.repeat(40), bounds: true},
  {name: 'unbroken-unicode', editorial: true, length: 40, count: 3, heading: '🧭'.repeat(40), rawLede: 'Ж'.repeat(40), bounds: true},
];
let browser;
try {
  browser = await chromium.launch({executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox']});
  const setup = await browser.newPage();
  const pixels = await setup.evaluate(() => {
    const canvas = document.createElement('canvas'); canvas.width = 600; canvas.height = 500;
    const ctx = canvas.getContext('2d'); ctx.fillStyle = '#f4f4f4'; ctx.fillRect(0, 0, 600, 500);
    ctx.fillStyle = '#1265a4'; ctx.fillRect(20, 30, 250, 400); ctx.fillStyle = '#e28b31'; ctx.fillRect(310, 80, 240, 300);
    return canvas.toDataURL('image/png');
  });
  await setup.close();
  const inventory = {actions: [{text: 'Read docs', href: 'https://source.example/docs'}], sourceCoverage: {sections: [{id:'s1', title:'Original section', headingLevel:'H2', kind:'section', sourceActionsVersion:1, sourceActions:[{label:'Read original', url:'https://source.example/original'}]}]}};
  for (const c of cases) {
    const d = structuredClone(base); d.kind = c.kind || 'software'; d.hero.media = 'hero'; d.hero.ui = {move:'split'};
    const items = features(c.count);
    if (c.individual) items[0].image = 'item-visual';
    const beat = {id:'target', type:'features', label:'Verified source', h2:c.heading || 'Product story', lede:c.rawLede || lede(c.length), features:items, image:'assigned', ui:{move:c.move || 'story', lead:''}, source_sections:['s1'], cta:'Read docs', cta_href:'https://source.example/docs'};
    d.beats = [beat, {id:'after', type:'faq', h2:'Questions', items:[['Question?', 'Verified answer.']]}];
    const images = [{id:'hero', w:1200, h:800, shot:true, detail:true, src:'visual-hero', data:pixels}, {id:'assigned', w:600, h:500, shot:!c.photo, detail:true, src:c.photo ? 'https://source.example/photo.jpg' : 'visual-shot', data:pixels}];
    if (c.individual) images.push({id:'item-visual', w:600, h:500, shot:false, detail:true, src:'https://source.example/item.jpg', data:pixels});
    for (const [name, value] of [['direction.json',d],['images.json',images],['inventory.json',inventory]]) fs.writeFileSync(path.join(dir,name), JSON.stringify(value));
    const out = path.join(dir, `${c.name}.html`);
    const run = spawnSync(process.env.PYTHON || 'python3', [path.join(rendererRoot,'lib/render/render_bp.py'), dir, c.blueprint || 'butter', out], {encoding:'utf8'});
    assert.equal(run.status, 0, `${c.name}: ${run.stderr}`);
    for (const width of c.bounds ? [390,920] : [390,1440]) for (const motion of ['reduce','no-preference']) for (const dpr of c.name === 'middle' ? [1,2,3] : [1]) {
      const page = await browser.newPage({viewport:{width,height:900}, deviceScaleFactor:dpr, reducedMotion:motion});
      await page.route(/^https?:/, route => route.abort());
      await page.goto(pathToFileURL(out).href + (motion === 'reduce' ? '?nomotion=1' : ''), {waitUntil:'load'});
      const section = page.locator('#target');
      assert.equal(await section.count(), 1, `${c.name}: target exists once`);
      const cls = await section.getAttribute('class');
      assert.equal(cls.split(/\s+/).includes('product-editorial'), c.editorial, `${c.name}: conditional editorial eligibility`);
      assert.equal(await section.locator('h2').textContent(), beat.h2);
      assert.equal((await section.locator('.lede').first().textContent()).trim(), beat.lede);
      for (const item of items) {
        assert.equal(await section.getByText(item.title, {exact:true}).count(), 1, `${c.name}: title preserved`);
        assert.equal(await section.getByText(item.body, {exact:true}).count(), 1, `${c.name}: body preserved`);
      }
      assert.equal(await section.locator('a[href="https://source.example/docs"]').count(), 1, `${c.name}: CTA`);
      assert.equal(await section.locator('a[href="https://source.example/original"]').count(), 1, `${c.name}: source link`);
      await section.locator('a[href="https://source.example/docs"]').click({trial:true});
      await section.locator('a[href="https://source.example/original"]').click({trial:true});
      assert.equal(await page.locator('#after details').count(), 1, `${c.name}: other section retained`);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width, `${c.name}: no horizontal overflow`);
      if (c.bounds) {
        for (const selector of ['.st-t h2', '.st-t .lede']) {
          const clipped = await section.locator(selector).evaluate(el => {
            const parent = el.closest('.st-t').getBoundingClientRect();
            const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
            const failures = [];
            while (walker.nextNode()) {
              const node = walker.currentNode;
              for (let i = 0; i < node.length;) {
                const codepoint = node.data.codePointAt(i), count = codepoint > 0xffff ? 2 : 1;
                const range = document.createRange(); range.setStart(node, i); range.setEnd(node, i + count);
                if (!/\s/u.test(String.fromCodePoint(codepoint))) for (const r of range.getClientRects()) {
                  if (r.left < Math.max(0, parent.left) - 0.75 || r.right > Math.min(innerWidth, parent.right) + 0.75) failures.push({character:String.fromCodePoint(codepoint), left:r.left, right:r.right, parentLeft:parent.left, parentRight:parent.right});
                }
                i += count;
              }
            }
            return failures;
          });
          assert.deepEqual(clipped, [], `${c.name}: every character of ${selector} stays within its column and viewport`);
        }
      }
      if (c.editorial) {
        const img = section.locator('img'); assert.equal(await img.count(), 1); assert.equal(await img.getAttribute('src'), pixels);
        const sizes = await img.evaluate(el => {const r=el.getBoundingClientRect(); return {w:r.width,h:r.height,nw:el.naturalWidth,nh:el.naturalHeight,fit:getComputedStyle(el).objectFit};});
        assert.equal(sizes.fit, 'contain'); assert.ok(sizes.w * dpr <= sizes.nw + 1 && sizes.h * dpr <= sizes.nh + 1, `${c.name}: no pixel upscale`);
        assert.ok(Math.abs(sizes.w/sizes.h-sizes.nw/sizes.nh)<.02, `${c.name}: no screenshot cropping`);
        assert.equal(await section.locator('.st-l li').count(), c.count);
        assert.equal(await section.locator('.st-l').evaluate(el => getComputedStyle(el).gridTemplateColumns.split(' ').length), width === 390 ? 1 : 3);
      }
      await page.close();
    }
  }
  console.log(`Butter editorial: ${cases.length} positive/negative cases; 390/1440, normal/reduced motion, content, actions and screenshots verified`);
} finally {
  if (browser) await browser.close();
  fs.rmSync(dir, {recursive:true, force:true});
}
