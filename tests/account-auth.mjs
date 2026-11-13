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
// a template job: its designs by id, a cover for each, the one paid for, and whether the editor can open it — never a template's name
const tj = { id: 'j3', url: 'form:casa-fern-1a2b3c4d', status: 'done', created_at: 't', options: { engine: 'templates', source: 'form', form: { name: 'Casa Fern', photos: [{ file: 'secret.jpg' }] } },
  result: { beforeUrl: 'https://cdn.test/before.jpg', paid: { maze: { at: 't2', user: 'u1', session: 'cs_live_private' } },
    templates: { store: { data: 'j3/data.json' }, variants: [{ slug: 'griffin', id: 'v1', cover: 'https://cdn.test/j3/t/v1-cover.jpg' }, { slug: 'maze', id: 'v2', cover: 'javascript:alert(1)' }, { slug: 'cerebrium', id: 'v3' }] } } };
const m = mine(tj);
assert.equal(m.designs, 3); assert.deepEqual(m.covers, [{ id: 'v1', cover: 'https://cdn.test/j3/t/v1-cover.jpg' }, { id: 'v2', cover: null }, { id: 'v3', cover: null }], 'a cover is an https cover file or nothing');
assert.deepEqual(m.paid, ['v2']); assert.equal(m.editable, true); assert.equal(m.name, 'Casa Fern');
assert.ok(!/griffin|maze|cerebrium|cs_live|secret\.jpg|data\.json/.test(JSON.stringify(m)), 'no template name, no payment session, no private file reaches the dashboard: ' + JSON.stringify(m));
assert.equal(mine({ ...tj, status: 'running' }).editable, false);
console.log('Accounts: a token is verified, an allowance is counted, a dashboard sees only its own summary');
