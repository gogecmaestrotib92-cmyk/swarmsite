import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-job-test-'));
try {
  const source = fs.readFileSync(new URL('../server/index.mjs', import.meta.url), 'utf8');
  const start = source.indexOf('async function process_(job) {');
  const end = source.indexOf('\nasync function loop()', start);
  assert.ok(start >= 0 && end > start, 'worker entry point is available');

  const observedFacts = [];
  let attempt = 0;
  const slugOf = url => url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  const run = async (command, args) => {
    if (args[0] === 'lib/pipeline/capture.mjs') {
      attempt++;
      const outputRoot = args[args.indexOf('--out') + 1];
      const dir = path.join(outputRoot, slugOf(args[1]));
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, 'inventory.json'), '{}');
      return '';
    }
    if (args[0] === '-I') return '{}';
    if (args[0] === '-c') {
      if (attempt === 1) {
        fs.writeFileSync(path.join(args[2], 'factsheet.json'), '{"what":"first attempt"}');
        return '{"what":"first attempt","n":1}';
      }
      throw new Error('reader failed');
    }
    if (args[0] === 'lib/direct/direct.py') {
      const facts = path.join(args[1], 'factsheet.json');
      observedFacts.push(fs.existsSync(facts) ? JSON.parse(fs.readFileSync(facts, 'utf8')).what : null);
      throw new Error('stop after inspecting director input');
    }
    throw new Error('unexpected command');
  };
  const context = {
    fs, path, process, OUT: root, slugOf, run,
    setStep: async () => {}, emit: async () => {}, eventsCapture: () => [], eventsDiagnose: () => [],
    console: { warn: () => {} },
  };
  const processJob = vm.runInNewContext(`(${source.slice(start, end)})`, context);
  const jobs = Array.from({ length: 2 }, () => ({ id: 'same-id', url: 'https://example.test', steps: [], options: {} }));
  for (const job of jobs) {
    await assert.rejects(processJob(job), /stop after inspecting director input/);
  }

  assert.notEqual(jobs[0]._dir, jobs[1]._dir);
  assert.deepEqual(observedFacts, ['first attempt', null]);
  assert.equal(fs.existsSync(path.join(jobs[1]._dir, 'factsheet.json')), false);
  console.log('Job attempts use fresh capture and director inputs');
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
