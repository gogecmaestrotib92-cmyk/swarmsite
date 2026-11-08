import assert from 'node:assert/strict';
import fs from 'node:fs';
import {chromium} from 'playwright';
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox']});
try {
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 const sections=Array.from({length:505},(_,i)=>`<section><h2>Meaningful topic ${i+1}</h2><p>Specific business evidence for topic ${i+1} is available.</p></section>`).join('');
 await page.setContent(`<html><body><main>${sections}</main></body></html>`);
 const inventory=await page.evaluate(fs.readFileSync('lib/audit/inventory.js','utf8'));
 assert.equal(inventory.sourceCoverage.sections.length,500); assert.equal(inventory.sourceCoverage.sectionsFound,505);
 assert.equal(inventory.sourceCoverage.sectionsTruncated,true); assert.equal(inventory.sourceCoverage.sections.at(-1).title,'Meaningful topic 500');
 await page.setContent('<main><div><h3>Menu and dishes</h3><p>Food made for local guests.</p></div><div><h3>Opening times</h3><p>See the hours before visiting.</p></div></main>');
 const h3Only=await page.evaluate(fs.readFileSync('lib/audit/inventory.js','utf8'));
 assert.deepEqual(h3Only.sourceCoverage.sections.map(s=>s.title),['Menu and dishes','Opening times']);
 assert.ok(h3Only.sourceCoverage.sections.every(s=>s.headingLevel==='H3' && s.kind==='heading'));
 assert.ok(h3Only.sourceCoverage.sections[0].text.includes('Food made for local guests'));
 console.log('Long homepages retain first 500 sections and report remaining sections');
} finally {await browser.close();}
