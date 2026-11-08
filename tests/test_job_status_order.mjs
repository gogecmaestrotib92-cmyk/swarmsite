import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';
import { prepareAlternative, publishSelected, verifySelected, verifyAlternative } from '../server/variant_snapshot.mjs';

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-status-order-'));
try {
  const source = fs.readFileSync(new URL('../server/index.mjs', import.meta.url), 'utf8');
  const start = source.indexOf('async function process_(job) {');
  const end = source.indexOf('\nasync function loop()', start);
  assert.ok(start >= 0 && end > start);
  const slugOf = url => url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  const inputFiles = ['direction.json', 'images.json', 'assets.json', 'inventory.json', 'brief.json', 'hero.mp4'];
  const engineFiles = ['lib/render/render_bp.py', 'lib/templates/recipes.py', 'lib/visual_quality.py', 'lib/colour/palette.py', 'lib/colour_policy.py', 'lib/motion/moves.js', 'lib/motion/swarm.js'];
  const hash = file => fs.existsSync(file) && fs.statSync(file).isFile() ? crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex') : null;
  for (const scenario of ['success', 'artifact-failure', 'alternative-failure', 'primary-failure']) {
    const events = [];
    const base = path.join(tmp, scenario);
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
        const dir = args[1], bp = args[2], out = args[args.indexOf('--out') + 1];
        const manifest = {
          fingerprints: {
            inputs: Object.fromEntries(inputFiles.map(name => [name, hash(path.join(dir, name))])),
            engine: Object.fromEntries([...engineFiles, `lib/blueprints/${bp}.bp.json`].map(name => [name, hash(path.join(process.cwd(), name))])),
          },
          html: hash(out),
        };
        fs.writeFileSync(path.join(dir, 'critic.json'), '{"score":80}');
        fs.writeFileSync(path.join(dir, 'coverage.json'), JSON.stringify({ scope: 'single_page_preview', sections: [{ title: 'FAQ', status: 'needs_review' }], routes: [] }));
        return JSON.stringify({ done: { rounds: 1, best_blueprint: bp, render_manifest: manifest } });
      }
      if (args[0] === 'lib/qa/check.py') return 'QA score: 100';
      throw new Error('unexpected command: ' + args[0]);
    };
    const context = {
      fs, path, process, ROOT: process.cwd(), OUT: base, slugOf, run,
      BP: { software: ['butter', 'cerebrium'] }, SELF: 'https://example.test',
      prepareAlternative, publishSelected, verifySelected, verifyAlternative,
      setStep: async () => {}, emit: async () => {},
      // Simulate a final progress update that was still in flight when the
      // upload began; the published result must include it.
      drainEvents: async job => { job._result = { events: [{ text: 'last progress' }] }; },
      updateWithRetry: async (_job, data) => {
        if (data.status !== 'done') return;
        events.push('status-done');
        assert.equal(data.result.coverage.scope, 'single_page_preview');
        assert.equal(data.result.coverage.sections[0].status, 'needs_review');
        assert.equal(data.result.events[0].text, 'last progress');
        assert.equal(data.result.artifactsAvailable, scenario !== 'artifact-failure');
        assert.deepEqual(Array.from(data.result.blueprints), scenario === 'alternative-failure' ? ['butter'] : ['butter', 'cerebrium']);
      },
      eventsCapture: () => [], eventsDiagnose: () => [], eventsDirect: () => [], eventsRender: () => [], eventsQA: () => [],
      upload: async (local, remote) => {
        assert.ok(fs.existsSync(local));
        const alt = remote.endsWith('/bp-cerebrium.html');
        events.push(alt ? 'alternative-start' : 'primary-start');
        await Promise.resolve();
        if ((alt && scenario === 'alternative-failure') || (!alt && scenario === 'primary-failure')) {
          events.push(alt ? 'alternative-failed' : 'primary-failed');
          throw new Error('storage unavailable');
        }
        events.push(alt ? 'alternative-finished' : 'primary-finished');
        return 'https://example.test/preview';
      },
      uploadArtefacts: async (_job, dir) => {
        assert.ok(fs.existsSync(path.join(dir, 'index.html')), 'preview exists before artifact upload');
        events.push('artifacts-start');
        await Promise.resolve();
        events.push('artifacts-finished');
        return scenario !== 'artifact-failure';
      },
      J: f => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return null; } },
      console: { warn() {}, log() {}, error() {} },
    };
    const processJob = vm.runInNewContext(`(${source.slice(start, end)})`, context);
    const job = { id: '123', url: 'https://example.test', options: {}, steps: [] };
    if (scenario === 'primary-failure') {
      await assert.rejects(() => processJob(job), /storage unavailable/);
      assert.deepEqual(events, ['primary-start', 'primary-failed'], 'failed primary upload never reports done');
      continue;
    }
    await processJob(job);
    const alternativeEnd = scenario === 'alternative-failure' ? 'alternative-failed' : 'alternative-finished';
    assert.deepEqual(events, ['primary-start', 'primary-finished', 'alternative-start', alternativeEnd, 'artifacts-start', 'artifacts-finished', 'status-done'], 'done follows preview and artifact uploads');
    assert.equal(job._artifactsUploaded, scenario !== 'artifact-failure', 'failed artifact upload leaves the job done but retains local files');
  }
  console.log('Job done follows preview and artifact uploads; primary, alternative and artifact failures are handled');
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
