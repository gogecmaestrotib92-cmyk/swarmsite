import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-status-order-'));
try {
  const source = fs.readFileSync(new URL('../server/index.mjs', import.meta.url), 'utf8');
  const start = source.indexOf('async function process_(job) {');
  const end = source.indexOf('\nasync function loop()', start);
  assert.ok(start >= 0 && end > start);
  const slugOf = url => url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  for (const result of [true, false]) {
    const events = [];
    const base = path.join(tmp, String(result));
    fs.mkdirSync(base);
    const direction = { kind: 'software', blueprint: 'butter', beats: [], brand: {} };
    const run = async (_cmd, args) => {
      if (args[0] === 'lib/pipeline/capture.mjs') {
        const dir = path.join(args[args.indexOf('--out') + 1], slugOf(args[1]));
        fs.mkdirSync(dir, { recursive: true });
        fs.writeFileSync(path.join(dir, 'inventory.json'), '{}');
        return '';
      }
      if (args[0] === '-I') return '{}';
      if (args[0] === '-c') return '{"what":"test","n":0}';
      if (args[0] === 'lib/direct/direct.py') {
        fs.writeFileSync(path.join(args[1], 'direction.json'), JSON.stringify(direction));
        return '';
      }
      if (args[0] === 'lib/render/render_bp.py') {
        fs.writeFileSync(args[3], '<html>preview</html>');
        return '';
      }
      if (args[0] === 'lib/swarm/run.py') {
        fs.writeFileSync(path.join(args[1], 'critic.json'), '{"score":80}');
        return '{"done":{"rounds":1}}';
      }
      if (args[0] === 'lib/qa/check.py') return 'QA score: 100';
      throw new Error('unexpected command: ' + args[0]);
    };
    const context = {
      fs, path, process, ROOT: process.cwd(), OUT: base, slugOf, run,
      BP: { software: ['butter', 'cerebrium'] }, SELF: 'https://example.test',
      setStep: async () => {}, emit: async () => {},
      eventsCapture: () => [], eventsDiagnose: () => [], eventsDirect: () => [], eventsRender: () => [], eventsQA: () => [],
      upload: async local => { assert.ok(fs.existsSync(local)); return 'https://example.test/preview'; },
      uploadArtefacts: async (_job, dir) => {
        assert.ok(fs.existsSync(path.join(dir, 'index.html')), 'preview exists before artifacts upload');
        events.push('artifacts-start');
        await Promise.resolve();
        events.push('artifacts-finished');
        return result;
      },
      J: f => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return null; } },
      sb: { from: () => ({ update: data => ({ eq: async () => { if (data.status === 'done') events.push('status-done'); } }) }) },
      console: { warn() {}, log() {}, error() {} },
    };
    const processJob = vm.runInNewContext(`(${source.slice(start, end)})`, context);
    const job = { id: '123', url: 'https://example.test', options: {}, steps: [] };
    await processJob(job);
    assert.deepEqual(events, ['artifacts-start', 'artifacts-finished', 'status-done'], 'done is reported only after artifact uploads finish');
    assert.equal(job._artifactsUploaded, result, 'failed artifact upload still leaves job done but retains local files');
  }
  console.log('Job done status follows artifact upload, including best-effort upload failure');
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
