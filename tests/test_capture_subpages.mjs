import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-subpages-'));
const links = [
  ['/politica-privacidad', 'Política de privacidad'],
  ['/politica-de-cookies', 'Política de cookies'],
  ['/politica-privacidade', 'Política de privacidade'],
  ['/datenschutzerklaerung', 'Datenschutzerklärung'],
  ['/confidentialite', 'Politique de confidentialité'],
  ['/cookie_policy', 'Cookie policy'],
  ['/cookie-settings', 'Cookie settings'],
  ['/sign-in', 'Sign in'],
  ['/signup', 'Create account'],
  ['/register', 'Register'],
  ['/menu', 'Menu'],
  ['/contacto', 'Contacto'],
  ['/design', 'Design'],
  ['/store/cookies', 'Our cookies'],
  ['/historia', 'Nuestra historia'],
];
const server = http.createServer((req, res) => {
  const navigation = req.url === '/' ? `<nav>${links.map(([href, label]) => `<a href="${href}">${label}</a>`).join(' ')}</nav>` : '';
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><html><head><title>Local cafe</title></head><body>${navigation}<main><h1>Our local cafe</h1><p>Visit our friendly neighbourhood cafe for fresh food and drinks. Our team serves breakfast and lunch each day with locally sourced ingredients and offers seasonal specials for everyone to enjoy.</p></main></body></html>`);
});

try {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const url = `http://127.0.0.1:${server.address().port}/`;
  const child = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--out', dir], { stdio: ['ignore', 'ignore', 'pipe'] });
  let error = '';
  child.stderr.on('data', chunk => { error += chunk; });
  const code = await new Promise((resolve, reject) => {
    child.on('error', reject);
    child.on('close', resolve);
  });
  assert.equal(code, 0, error);
  const slug = url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  const inventory = JSON.parse(fs.readFileSync(path.join(dir, slug, 'inventory.json'), 'utf8'));
  const paths = inventory.sourcePages.map(page => new URL(page.url).pathname).sort();
  assert.deepEqual(paths, ['/contacto', '/design', '/menu', '/store/cookies']);
  console.log('Capture excludes privacy and account pages while keeping relevant content');

  // The supplied URL can redirect to a canonical origin. Only that landed
  // origin may contribute subpages, even when another page redirects back to
  // the originally supplied origin.
  let landedOrigin = '';
  let entryOrigin = '';
  const entry = http.createServer((req, res) => {
    if (req.url === '/') { res.writeHead(302, { location: landedOrigin + '/' }); res.end(); return; }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end('<html><title>External pricing</title><body><h1>External pricing</h1><p>This page is outside the landed website and must not become a source page.</p></body></html>');
  });
  const landed = http.createServer((req, res) => {
    if (req.url === '/pricing') { res.writeHead(302, { location: entryOrigin + '/external' }); res.end(); return; }
    const nav = req.url === '/' ? '<nav><a href="/menu">Menu</a><a href="/contacto">Contacto</a><a href="/pricing">Pricing</a></nav>' : '';
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html><head><title>Canonical cafe</title></head><body>${nav}<main><h1>Our local cafe</h1><p>Visit our friendly neighbourhood cafe for fresh food and drinks. Our team serves breakfast and lunch each day with locally sourced ingredients and offers seasonal specials for everyone to enjoy. We welcome our guests every day and help them discover the menu.</p></main></body></html>`);
  });
  try {
    await new Promise(resolve => landed.listen(0, '127.0.0.1', resolve));
    landedOrigin = `http://127.0.0.1:${landed.address().port}`;
    await new Promise(resolve => entry.listen(0, '127.0.0.1', resolve));
    entryOrigin = `http://127.0.0.1:${entry.address().port}`;
    const redirectUrl = `${entryOrigin}/`;
    const redirected = spawn(process.execPath, ['lib/pipeline/capture.mjs', redirectUrl, '--out', dir], { stdio: ['ignore', 'ignore', 'pipe'] });
    let redirectError = '';
    redirected.stderr.on('data', chunk => { redirectError += chunk; });
    const redirectCode = await new Promise((resolve, reject) => {
      redirected.on('error', reject);
      redirected.on('close', resolve);
    });
    assert.equal(redirectCode, 0, redirectError);
    const redirectSlug = redirectUrl.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
    const redirectedInventory = JSON.parse(fs.readFileSync(path.join(dir, redirectSlug, 'inventory.json'), 'utf8'));
    assert.deepEqual(redirectedInventory.sourcePages.map(page => new URL(page.url).pathname).sort(), ['/contacto', '/menu']);
    assert.ok(redirectedInventory.sourcePages.every(page => new URL(page.url).origin === landedOrigin));
    console.log('Capture follows the landed origin and rejects cross-origin subpage redirects');
  } finally {
    await new Promise(resolve => entry.close(resolve));
    await new Promise(resolve => landed.close(resolve));
  }
} finally {
  await new Promise(resolve => server.close(resolve));
  fs.rmSync(dir, { recursive: true, force: true });
}
