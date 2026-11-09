/* A cookie or consent banner is the visitor's chore, not the page's content. Its words must not become the copy the
   director writes from, the audit counts, or the SEO-safe contract expects back on the rebuilt page — and a section that
   merely has "cookie" in its class (a bakery's product) must not be mistaken for a banner. */
import assert from 'node:assert/strict'; import { spawn } from 'node:child_process'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import http from 'node:http';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarm-consent-'));
const PAGE = `<!doctype html><html lang="es"><head><title>Horno Bálamo — panadería artesanal</title><style>body{font:16px sans-serif;margin:0}section{padding:60px 40px}
  #cookie-notice{position:fixed;left:0;right:0;bottom:0;background:#111;color:#fff;padding:20px}</style></head><body>
  <nav><a href="/carta">Carta</a></nav>
  <main>
    <section><h1>Pan de masa madre horneado cada mañana</h1><p>Abrimos a las siete. Harina ecológica molida en piedra y fermentación lenta de veinticuatro horas.</p></section>
    <section class="cookie-box"><h2>Caja de galletas</h2><p>Doce galletas de mantequilla con chocolate negro, horneadas a diario para llevar.</p></section>
    <section><h2>Dónde estamos</h2><p>Calle del Almendro 14, Madrid. De martes a domingo.</p></section>
  </main>
  <div id="cookie-notice" role="dialog" aria-label="Aviso de cookies"><p>Utilizamos cookies propias y de terceros para analizar tus búsquedas e intereses y mostrarte publicidad ajustada a tus gustos. Puedes aceptar todas las cookies, rechazarlas o configurar tus preferencias en el apartado de ajustes.</p><button>Aceptar</button><button>Rechazar</button><button>Configurar</button></div>
  </body></html>`;
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); res.end(PAGE); });
try {
  await new Promise(r => server.listen(0, '127.0.0.1', r)); const url = `http://127.0.0.1:${server.address().port}/`;
  const proc = spawn(process.execPath, ['lib/pipeline/capture.mjs', url, '--out', dir], { stdio: ['ignore', 'pipe', 'pipe'] }); let stderr = ''; proc.stderr.on('data', c => stderr += c); proc.stdout.on('data', () => {});
  const code = await new Promise((r, j) => { proc.on('error', j); proc.on('close', r); }); assert.equal(code, 0, stderr);
  const slug = url.replace(/^https?:\/\//, '').replace(/[^a-z0-9.-]+/gi, '_').replace(/_+$/, '').toLowerCase();
  const inv = JSON.parse(fs.readFileSync(path.join(dir, slug, 'inventory.json')));
  const copy = inv.copy.text;
  for (const word of ['masa madre', 'fermentación lenta', 'Calle del Almendro']) assert.ok(copy.includes(word), `page content kept: ${word}`);
  assert.ok(copy.includes('Doce galletas de mantequilla'), 'a product section with "cookie" in its class is content, not a banner');
  for (const word of ['Utilizamos cookies', 'publicidad ajustada', 'Rechazar', 'configurar tus preferencias']) assert.ok(!copy.includes(word), `consent text is not page copy: ${word}`);
  assert.ok(inv.copy.consent && inv.copy.consent.includes('Utilizamos cookies'), 'the banner text is kept apart, not thrown away');
  assert.ok(inv.copy.totalWords < 70, `word count is the page's, not the banner's (${inv.copy.totalWords})`);
  assert.ok(!inv.copy.buttons.some(b => /aceptar|rechazar|configurar/i.test(b)), `the banner's buttons are not the page's actions: ${JSON.stringify(inv.copy.buttons)}`);
  console.log('Consent banner text is kept apart from the page copy; lookalike content is untouched');
} finally { await new Promise(r => server.close(r)); fs.rmSync(dir, { recursive: true, force: true }); }
