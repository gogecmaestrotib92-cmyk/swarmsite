import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../server/index.mjs', import.meta.url), 'utf8');
const start = source.indexOf('async function runClaimed(');
const end = source.indexOf('\nasync function process_(', start);
assert.ok(start >= 0 && end > start);

for (const scenario of ['provider-credit', 'unrelated']) {
  const errors = [], updates = [];
  const raw = scenario === 'provider-credit'
    ? "python3 lib/direct/direct.py exit 1: Traceback (most recent call last):\nanthropic.BadRequestError: Error code: 400 - {'message': 'Your credit balance is too low to access the Anthropic API.', 'request_id': 'private-sentinel'}"
    : 'capture failed because the source page timed out';
  const context = {
      WORKER_ID: 'test-worker', setInterval, clearInterval, setTimeout, CURRENT_JOB_DIR: '',
    process_: async () => { throw new Error(raw); },
    drainEvents: async () => {},
    updateWithRetry: async (_job, data) => { updates.push(data); },
    console: { log() {}, warn() {}, error(...args) { errors.push(args); } },
    sb: { from() { return { update(value) { updates.push(value); return { async eq() {} }; } }; } },
    uploadArtefacts: async () => true,
    fs: { rmSync() {} },
  };
  const runClaimed = vm.runInNewContext(`(${source.slice(start, end)})`, context);
  await runClaimed({ id: 'test-job' });
  assert.equal(updates[0].status, 'failed');
  if (scenario === 'provider-credit') {
    assert.equal(updates[0].error, 'The AI service is temporarily unavailable. Please try again later.');
    assert.match(errors[0].join(' '), /Anthropic API credit balance is too low; check provider billing/);
    assert.doesNotMatch(JSON.stringify([updates, errors]), /Traceback|private-sentinel|request_id/);
  } else {
    assert.equal(updates[0].error, raw, 'unrelated diagnostics remain unchanged');
    assert.equal(errors[0][2], raw);
  }
}
console.log('Provider credit failure is safe for customers and actionable in operator logs');
