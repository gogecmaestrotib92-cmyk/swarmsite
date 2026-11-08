import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-content-length-'));
try {
  for (const mode of ['valid', 'empty', 'duplicate']) {
    const content = i => `<h2>Meaningful section ${i + 1}</h2><p>Important content about feature ${i + 1} remains on the page.</p>`;
    const sections = Array.from({length: 16}, (_, i) => `<section id="section-${i}">${mode === 'empty' && i === 3 ? '' : content(mode === 'duplicate' && i === 3 ? 2 : i)}</section>`).join('');
    const file = path.join(dir, 'page.html');
    fs.writeFileSync(file, `<!doctype html><style>html,body{margin:0}section{min-height:100vh;padding:2rem;box-sizing:border-box}</style>${sections}`);
    const run = spawnSync(process.execPath, ['lib/qa/contract.mjs', file, '--dir', dir], {encoding:'utf8', timeout: 120000, env:{...process.env, LIVETEST:'1'}});
    assert.equal(run.status, 0, run.stderr || run.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    assert.equal(report.failed.some(x => x.id === 'page-length'), false, 'length alone must not penalize real content');
    assert.equal(report.failed.some(x => x.id === 'sections'), mode !== 'valid', 'empty or identical repeated sections must still fail');
  }
  // Closed accordion answers are invisible but still distinguish sections;
  // their visible summaries must count when judging a long FAQ's density.
  for (const duplicate of [false, true]) {
    const faq = answer => `<section class="sec faq"><h2>Frequently asked questions about your account</h2>${Array.from({length: 18}, (_, i) => `<details><summary>How does feature ${i + 1} work for my company?</summary><p>${answer} for feature ${i + 1}</p></details>`).join('')}</section>`;
    const file = path.join(dir, 'faq.html');
    fs.writeFileSync(file, `<!doctype html><style>body{margin:0}section{padding:50px}summary{padding:20px}details{border-bottom:1px solid}</style>${faq('First answer')}${faq(duplicate ? 'First answer' : 'Different answer')}`);
    const run = spawnSync(process.execPath, ['lib/qa/contract.mjs', file, '--dir', dir], {encoding:'utf8', timeout: 120000, env:{...process.env, LIVETEST:'1'}});
    assert.equal(run.status, 0, run.stderr || run.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    assert.equal(report.failed.some(x => x.id.endsWith('-no-empty-screens')), false, 'visible closed FAQ questions count as content');
    assert.equal(report.failed.some(x => x.id === 'sections'), duplicate, 'different closed answers make FAQs distinct');
  }
  // Long real-style review lists use blockquote/figcaption instead of p/li.
  // Only actual nonempty, visible quote text should fill the measured screens.
  for (const populated of [true, false]) {
    const reviews = Array.from({length: 14}, (_, i) => `<figure><blockquote>${populated ? `Review ${i + 1}: ${'Customers rely on this service for their scheduling. '.repeat(8)}` : ''}</blockquote><figcaption>${populated ? `Customer ${i + 1}` : ''}</figcaption></figure>`).join('');
    const file = path.join(dir, 'reviews.html');
    fs.writeFileSync(file, `<!doctype html><style>body{margin:0}section{padding:32px}figure{margin:0;padding:24px}blockquote{margin:0;min-height:160px;font:24px/1.5 sans-serif}</style><section class="sec reviews">${reviews}</section>`);
    const run = spawnSync(process.execPath, ['lib/qa/contract.mjs', file, '--dir', dir], {encoding:'utf8', timeout: 120000, env:{...process.env, LIVETEST:'1'}});
    assert.equal(run.status, 0, run.stderr || run.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    assert.equal(report.failed.some(x => x.id === 'desktop-no-empty-screens'), !populated, 'visible testimonial text must be counted on desktop');
    assert.equal(report.failed.some(x => x.id === 'mobile-no-empty-screens'), !populated, 'visible testimonial text must be counted on mobile');
  }
  console.log('Contract accepts long content without accepting empty sections');
} finally { fs.rmSync(dir, {recursive:true, force:true}); }
