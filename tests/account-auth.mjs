/* Who is asking, and what an account may still start: the server side of accounts, without a network.
   - a token is taken only from a well-formed Authorization: Bearer header, and is verified by Supabase, never trusted;
   - a verified answer is remembered for a minute, a refused one too (a bad token must not hammer the auth service);
   - the dashboard gets a job's address, state and preview — never the whole result. */
import assert from 'node:assert/strict';
import { bearer, makeUserOf, allowance, mine } from '../server/auth.mjs';

assert.equal(bearer({ headers: { authorization: 'Bearer ' + 'a'.repeat(40) } }), 'a'.repeat(40));
for (const bad of ['', 'Basic abc', 'Bearer short', 'Bearer ' + 'a'.repeat(30) + ' extra', 'bearer\n' + 'a'.repeat(40)]) assert.equal(bearer({ headers: { authorization: bad } }), '', JSON.stringify(bad));
assert.equal(bearer({}), '');

let calls = 0, clock = 0;
const sb = { auth: { getUser: async token => { calls++; return token.startsWith('good') ? { data: { user: { id: 'u1', email: 'Person@Example.com' } }, error: null } : { data: { user: null }, error: { message: 'invalid' } }; } } };
const userOf = makeUserOf(sb, 60000, () => clock);
const req = t => ({ headers: { authorization: 'Bearer ' + t } });
assert.equal(await userOf({ headers: {} }), null); assert.equal(calls, 0, 'no token, no question asked');
assert.deepEqual(await userOf(req('good' + 'x'.repeat(30))), { id: 'u1', email: 'person@example.com' });
assert.deepEqual(await userOf(req('good' + 'x'.repeat(30))), { id: 'u1', email: 'person@example.com' }); assert.equal(calls, 1, 'verified once within the minute');
assert.equal(await userOf(req('bad' + 'x'.repeat(30))), null); assert.equal(await userOf(req('bad' + 'x'.repeat(30))), null); assert.equal(calls, 2, 'a refused token is remembered as refused');
clock = 61000; await userOf(req('good' + 'x'.repeat(30))); assert.equal(calls, 3, 'and asked again after the minute');
const failing = makeUserOf({ auth: { getUser: async () => { throw new Error('down'); } } });
assert.equal(await failing(req('good' + 'x'.repeat(30))), null, 'an auth service that is down signs nobody in');

assert.deepEqual(allowance({ used: 0, free: 3 }), { used: 0, free: 3, left: 3, allowed: true });
assert.deepEqual(allowance({ used: 3, free: 3 }), { used: 3, free: 3, left: 0, allowed: false });
assert.equal(allowance({ used: 9, free: 3, paid: true }).allowed, true);
assert.deepEqual(allowance(), { used: 0, free: 0, left: 0, allowed: false });

const row = { id: 'j1', url: 'https://x.test/', status: 'done', step: 'upload', created_at: '2026-11-11T10:00:00Z', result: { seconds: 300, previewUrl: 'https://api.test/p/j1?v=1', beforeUrl: 'https://cdn.test/before.jpg', critic: { verdict: 'private' }, budget: { usd: 2.5 },
  studio: { kept: 'a', variants: [{ tag: 'a', clean: true }, { tag: 'b', clean: true }, { tag: 'c', clean: false }] } } };
assert.deepEqual(mine(row), { id: 'j1', url: 'https://x.test/', status: 'done', step: 'upload', created_at: '2026-11-11T10:00:00Z', seconds: 300, preview: 'https://api.test/p/j1?v=1', before: 'https://cdn.test/before.jpg', designs: 2 });
assert.ok(!JSON.stringify(mine(row)).includes('private') && !JSON.stringify(mine(row)).includes('2.5'), 'what a job cost and what the critic said stay on the server');
assert.deepEqual(mine({ id: 'j2', url: 'u', status: 'queued', created_at: 't' }), { id: 'j2', url: 'u', status: 'queued', step: null, created_at: 't', seconds: null, preview: null, before: null, designs: 0 });
console.log('Accounts: a token is verified, an allowance is counted, a dashboard sees only its own summary');
