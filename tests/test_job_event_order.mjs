import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import http from 'node:http';
import { createRequire } from 'node:module';

const { createClient } = createRequire(new URL('../server/package.json', import.meta.url))('@supabase/supabase-js');

const source = fs.readFileSync(new URL('../server/index.mjs', import.meta.url), 'utf8');
const writeSource = source.slice(source.indexOf('async function updateRunning('), source.indexOf('\nasync function upload(', source.indexOf('async function updateRunning(')));
const eventsSource = source.slice(source.indexOf('function emit('), source.indexOf('\nfunction eventsCapture(', source.indexOf('function emit(')));
const handlerSource = source.slice(source.indexOf('async function runClaimed('), source.indexOf('\nasync function process_(', source.indexOf('async function runClaimed(')));
assert.ok(writeSource.includes('async function setStep') && eventsSource.includes('async function drainEvents'));

function deferred() { let resolve; const promise = new Promise(r => { resolve = r; }); return { promise, resolve }; }
function makeDb(state, gateFirst = false) {
  const calls = []; const first = deferred();
  const sb = { from(table) {
    assert.equal(table, 'jobs');
    return { update(patch) {
      // PostgREST serializes the body when the request is sent.
      const call = { patch: JSON.parse(JSON.stringify(patch)), filters: {} }; calls.push(call);
      const query = { eq(key, value) { call.filters[key] = value; return query; }, select(fields) { assert.equal(fields, 'id'); return query; }, async maybeSingle() {
        if (gateFirst && calls.indexOf(call) === 0) await first.promise;
        if (state.errors?.length) return { data: null, error: state.errors.shift() };
        if (state.error) return { data: null, error: { message: state.error } };
        if (call.filters.id !== state.id || call.filters.status !== state.status) return { data: null, error: null };
        Object.assign(state, call.patch); return { data: { id: state.id }, error: null };
      }};
      return query;
    }};
  }};
  return { sb, calls, release: first.resolve };
}
function load(db) {
  const ctx = vm.createContext({ sb: db.sb, console, Date, Promise, setTimeout });
  vm.runInContext(`${writeSource}\n${eventsSource}`, ctx);
  return ctx;
}

// The first HTTP update is delayed while a second progress event arrives.
// Completion must wait for both, preserving their order and the final preview.
{
  const state = { id: 'job', status: 'running', result: null };
  const db = makeDb(state, true); const { emit, drainEvents, updateWithRetry } = load(db);
  const job = { id: 'job' };
  const first = emit(job, [{ role: 'Audit', text: 'first' }]);
  const second = emit(job, [{ role: 'QA', text: 'second' }]);
  const finish = (async () => { await drainEvents(job); await updateWithRetry(job, { status: 'done', result: { ...job._result, previewUrl: '/p/job' } }); })();
  await new Promise(r => setImmediate(r));
  assert.equal(db.calls.length, 1, 'the second event and completion wait behind the first write');
  db.release(); await Promise.all([first, second, finish]);
  assert.deepEqual(db.calls.map(c => c.patch.status || 'event'), ['event', 'event', 'done']);
  assert.equal(state.status, 'done'); assert.equal(state.result.previewUrl, '/p/job');
  assert.deepEqual(state.result.events.map(e => e.text), ['first', 'second']);
}

// A terminal state set by another worker cannot be resurrected or overwritten.
for (const terminal of ['failed', 'done']) {
  const state = { id: 'job', status: terminal, result: { preserved: true } };
  const db = makeDb(state); const { setStep, emit, updateWithRetry } = load(db);
  const job = { id: 'job', steps: [{ id: 'capture', status: 'pending' }] };
  await assert.rejects(setStep(job, 'capture', 'running'), /no longer running/);
  await assert.rejects(emit(job, [{ text: 'late' }]), /no longer running/);
  await assert.rejects(updateWithRetry(job, { status: 'failed', error: 'late' }), /no longer running/);
  assert.equal(state.status, terminal); assert.deepEqual(state.result, { preserved: true });
}

// A failure while progress is in flight is fenced at commit time.
{
  const state = { id: 'job', status: 'running', result: { preserved: true } };
  const db = makeDb(state, true); const { emit, drainEvents } = load(db);
  const job = { id: 'job' }; const pending = emit(job, [{ text: 'late' }]);
  await new Promise(r => setImmediate(r)); state.status = 'failed'; db.release();
  await assert.rejects(pending, /no longer running/); await assert.rejects(drainEvents(job), /no longer running/);
  assert.deepEqual(state.result, { preserved: true });
}

// A DB error must not be mistaken for a successful progress or terminal write.
{
  const state = { id: 'job', status: 'running', error: 'database offline' };
  const db = makeDb(state); const { setStep, emit, updateRunning } = load(db);
  const job = { id: 'job', steps: [{ id: 'capture', status: 'pending' }] };
  await assert.rejects(setStep(job, 'capture', 'running'), /job update failed: database offline/);
  await assert.rejects(emit(job, [{ text: 'event' }]), /job update failed: database offline/);
  await assert.rejects(updateRunning(job, { status: 'done' }), /job update failed: database offline/);
  assert.equal(state.status, 'running');
}

// Explicitly aborted PostgreSQL transactions may be retried without adding
// the same event twice. Unknown network outcomes must fail closed.
{
  const state = { id: 'job', status: 'running', errors: [{ code: '40001', message: 'serialization failure' }] };
  const db = makeDb(state); const { emit, drainEvents } = load(db); const job = { id: 'job' };
  const first = emit(job, [{ text: 'first' }]); const second = emit(job, [{ text: 'second' }]);
  await Promise.all([first, second, drainEvents(job)]);
  assert.equal(db.calls.length, 3, 'the first rejected transaction is retried once');
  assert.deepEqual(db.calls.map(c => c.patch.result.events.map(e => e.text)), [['first'], ['first'], ['first', 'second']]);
  assert.deepEqual(state.result.events.map(e => e.text), ['first', 'second']);
}
{
  const state = { id: 'job', status: 'running', errors: Array.from({ length: 3 }, () => ({ code: '40P01', message: 'deadlock' })) };
  const db = makeDb(state); const { emit, drainEvents } = load(db); const job = { id: 'job' };
  await assert.rejects(emit(job, [{ text: 'only once' }]), /deadlock/);
  await assert.rejects(drainEvents(job), /deadlock/);
  assert.equal(db.calls.length, 3, 'retry count is bounded');
  assert.equal(job._result.events.length, 1, 'retry never duplicates an event');
}
{
  const state = { id: 'job', status: 'running', errors: [{ message: 'fetch failed: outcome unknown' }] };
  const db = makeDb(state); const { emit, updateWithRetry } = load(db); const job = { id: 'job' };
  await assert.rejects(emit(job, [{ text: 'unknown' }]), /outcome unknown/);
  assert.equal(db.calls.length, 1, 'network outcomes are not retried');
  state.errors = [{ message: 'terminal network outcome unknown' }];
  await assert.rejects(updateWithRetry(job, { status: 'done' }), /terminal network outcome unknown/);
  assert.equal(db.calls.length, 2, 'terminal writes with unknown outcomes are not retried');
}

// A PostgreSQL serialization rejection is safe to retry for either terminal
// state; the retry uses the same guarded patch and confirms the final state.
for (const terminal of ['done', 'failed']) {
  const state = { id: 'job', status: 'running', errors: [{ code: '40001', message: 'serialization failure' }] };
  const db = makeDb(state); const { updateWithRetry } = load(db);
  await updateWithRetry({ id: 'job' }, { status: terminal, result: { preview: '/p/job' } });
  assert.equal(db.calls.length, 2, `${terminal}: explicitly aborted transaction is retried`);
  assert.deepEqual(db.calls[0].patch, db.calls[1].patch, 'terminal retry sends identical data');
  assert.equal(state.status, terminal);
}

// A failure waits for queued writes before marking the job failed. If a
// different actor has already finalized it, stale artifacts are not uploaded.
for (const externallyFinalized of [false, true]) {
  const gate = deferred(); const order = [];
  const context = {
    process_: async () => { throw new Error('capture failed'); },
    drainEvents: async () => { order.push('drain-start'); await gate.promise; order.push('drain-end'); },
    updateWithRetry: async (_job, patch) => { order.push('terminal-update'); if (externallyFinalized) throw new Error('job is no longer running'); assert.equal(patch.status, 'failed'); },
    uploadArtefacts: async () => { order.push('artifact-upload'); return true; },
    fs: { rmSync() { order.push('cleanup'); } },
    console: { log() {}, error() {}, warn() {} },
  };
  const handler = vm.runInNewContext(`(${handlerSource})`, context);
  const handling = handler({ id: 'job', _dir: '/tmp/example', _jobRoot: '/tmp/example' });
  await new Promise(r => setImmediate(r));
  assert.deepEqual(order, ['drain-start'], 'failure must wait for in-flight progress');
  gate.resolve(); await handling;
  assert.deepEqual(order, externallyFinalized
    ? ['drain-start', 'drain-end', 'terminal-update']
    : ['drain-start', 'drain-end', 'terminal-update', 'artifact-upload', 'cleanup']);
}

// Exercise the actual Supabase client against a tiny PostgREST-compatible
// HTTP fixture; a zero-row conditional update must resolve as no data.
{
  const state = { id: 'job', status: 'running' }; const requests = [];
  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost'); let raw = '';
    for await (const chunk of req) raw += chunk;
    requests.push({ method: req.method, path: url.pathname, id: url.searchParams.get('id'), status: url.searchParams.get('status') });
    const matches = url.searchParams.get('id') === 'eq.job' && url.searchParams.get('status') === `eq.${state.status}`;
    if (matches) Object.assign(state, JSON.parse(raw));
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify(matches ? [{ id: state.id }] : []));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    const { port } = server.address();
    const sb = createClient(`http://127.0.0.1:${port}`, 'fixture-key', { auth: { persistSession: false } });
    const { updateRunning } = load({ sb });
    await updateRunning({ id: 'job' }, { status: 'done' });
    await assert.rejects(updateRunning({ id: 'job' }, { status: 'failed' }), /no longer running/);
    assert.equal(state.status, 'done');
    assert.ok(requests.every(r => r.method === 'PATCH' && r.path === '/rest/v1/jobs' && r.id === 'eq.job' && r.status === 'eq.running'));
  } finally { await new Promise(resolve => server.close(resolve)); }
}
console.log('Progress writes stay ordered and terminal job states cannot be overwritten');
