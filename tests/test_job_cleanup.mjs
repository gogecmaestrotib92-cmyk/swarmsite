import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-cleanup-'));
try {
  const source = fs.readFileSync(new URL('../server/index.mjs', import.meta.url), 'utf8');
  const artifactSource = source.slice(source.indexOf('async function uploadArtefacts('), source.indexOf('\nconst BP ='));
  const handlerSource = source.slice(source.indexOf('async function runClaimed('), source.indexOf('\nasync function process_('));
  assert.ok(artifactSource.includes('return uploaded') && handlerSource.includes('finally'), 'worker cleanup entry points exist');
  for (const scenario of ['success', 'job-failed', 'artifact-upload-failed', 'status-write-failed']) {
    const root = path.join(tmp, scenario);
    const dir = path.join(root, 'example.test');
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'direction.json'), '{"site":"example"}');
    fs.writeFileSync(path.join(dir, 'contract.json'), '{"score":100}');
    const events = [];
    const job = { id: scenario, _jobRoot: root, _dir: dir };
    const context = {
      fs, path, ARTS: ['direction.json', 'contract.json'],
      console: { log() {}, warn() {}, error() {} },
      drainEvents: async () => {},
      updateWithRetry: async (_job, data) => { if (data.status === 'failed') { events.push('failed-status'); if (scenario === 'status-write-failed') throw new Error('database unavailable'); } },
      sb: { from: () => ({ update: () => ({ eq: async () => { events.push('failed-status'); } }) }) },
      upload: async fp => {
        assert.ok(fs.existsSync(fp), 'artifacts must exist during upload');
        events.push('upload:' + path.basename(fp));
        if (scenario === 'artifact-upload-failed' && fp.endsWith('direction.json')) throw new Error('storage failure');
      },
      process_: async j => {
        if (scenario === 'job-failed') throw new Error('capture failed');
        j._artifactsUploaded = await context.uploadArtefacts(j, j._dir);
        if (scenario === 'status-write-failed') throw new Error('done status update failed');
        j._terminalPersisted = true;
      },
    };
    context.uploadArtefacts = vm.runInNewContext(`(${artifactSource})`, context);
    const handle = vm.runInNewContext(`(${handlerSource})`, context);
    await handle(job);
    assert.deepEqual(events.filter(e => e.startsWith('upload:')), ['upload:direction.json', 'upload:contract.json']);
    assert.equal(fs.existsSync(root), ['artifact-upload-failed', 'status-write-failed'].includes(scenario), `${scenario}: retain files if upload or terminal persistence failed`);
    if (scenario === 'job-failed') assert.equal(events[0], 'failed-status');
  }
  console.log('Job directories are cleaned after uploads and retained on artifact upload failure');
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
