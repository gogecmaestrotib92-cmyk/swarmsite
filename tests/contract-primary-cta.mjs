import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'contract-primary-cta-'));
try {
  for (const mode of ['consistent', 'inconsistent-nav', 'inconsistent-closing']) {
    const navHref = mode === 'inconsistent-nav' ? 'https://example.test/sales' : '#contact';
    const closingHref = mode === 'inconsistent-closing' ? 'https://example.test/demo' : 'https://example.test/signup';
    const sections = ['Integrations', 'Events', 'Pricing', 'Documentation', 'Enterprise', 'Customers', 'Developers', 'Support']
      .map((name, i) => `<section><h2>${name}</h2><p>Read about ${name} and its features.</p><a class="btn" href="https://example.test/section-${i}">Explore ${name}</a></section>`).join('');
    const file = path.join(dir, 'page.html');
    fs.writeFileSync(file, `<!doctype html><style>section{padding:32px}a.btn{display:inline-block;padding:10px}</style>
      <nav class="nav"><a class="btn" href="${navHref}">Get started</a></nav>
      <section class="sec hero"><h1>Get started today</h1><a class="btn" href="https://example.test/signup">Start now</a></section>
      ${sections}<section class="sec cta" id="contact"><h2>Get started</h2><a class="btn" href="${closingHref}">Sign up</a></section>`);
    const run = spawnSync(process.execPath, ['lib/qa/contract.mjs', file, '--dir', dir], {encoding:'utf8', timeout:120000, env:{...process.env, LIVETEST:'1'}});
    assert.equal(run.status, 0, run.stderr || run.error?.message);
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'contract.json')));
    assert.equal(report.failed.some(x => x.id === 'one-cta'), mode !== 'consistent', mode);
  }
  console.log('Distinct section actions are preserved; inconsistent primary destinations are flagged');
} finally { fs.rmSync(dir, {recursive:true, force:true}); }
