// The inside of an app is not redesigned (2026-11-22: a school ERP's dashboard became three designs headed "Dashboard"):
// a captured page with no menu, no footer, no link and no form stops the job before the paid reading, with a message the
// app shows as an explanation, not as a fault.
import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path';
import { appScreen, APP_SCREEN, runTemplateJob } from '../server/templates.mjs';

const app = { brand: { navCount: 0, hasFooter: false }, actions: [], forms: [], copy: { h1: 'Dashboard' } };
assert.equal(appScreen(app), true);
assert.equal(appScreen({ ...app, brand: { navCount: 5, hasFooter: false } }), false, 'a menu: a page that presents');
assert.equal(appScreen({ ...app, brand: { navCount: 0, hasFooter: true } }), false, 'a footer: a page that presents');
assert.equal(appScreen({ ...app, actions: [{ t: 'Start', h: '/signup' }] }), false, 'a link: a page that presents');
assert.equal(appScreen({ ...app, forms: [{ fields: 1 }] }), false, 'a "coming soon" with a sign-up form is not an app');
assert.equal(appScreen({ brand: {} }), false, 'what the capture did not measure is not read as an app');
assert.equal(appScreen(null), false);

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'appscreen-'));
try {
  const jobRoot = path.join(tmp, 'job'), dir = path.join(jobRoot, 'site'), ran = [];
  fs.mkdirSync(dir, { recursive: true });
  const run = async (cmd, args) => { ran.push(args[0]);
    if (args[0] === 'lib/pipeline/capture.mjs') { fs.writeFileSync(path.join(dir, 'inventory.json'), JSON.stringify({ url: 'https://erp.example/', ...app })); return ''; }
    throw new Error('nothing after the capture may run: ' + args.join(' ')); };
  const job = { id: '33333333-3333-4333-8333-333333333333', url: 'https://erp.example/', options: { engine: 'templates' }, result: {} };
  const steps = [];
  const deps = { job, dir, jobRoot, run, self: 'https://api.example', chrome: '', upload: async () => '', uploadPrivate: async () => {}, fetchUpload: async () => {},
    publicBase: k => k, setStep: async (id, status) => { steps.push(`${id}:${status}`); }, emit: async () => {}, save: async () => {} };
  await assert.rejects(runTemplateJob(deps), e => e.message === APP_SCREEN);
  assert.deepEqual(ran, ['lib/pipeline/capture.mjs'], 'no reading, no build: nothing is paid for');
  // the app's working screen reads it as an explanation, not "Something broke"
  const html = fs.readFileSync(new URL('../web/app.html', import.meta.url), 'utf8');
  assert.ok(new RegExp(html.match(/const appInside=\/(.+?)\/\.test/)[1]).test(APP_SCREEN), 'web/app.html recognises the message');
  console.log('App screen: the inside of an app stops after the capture, before any paid call, and is explained to the visitor');
} finally { fs.rmSync(tmp, { recursive: true, force: true }); }
