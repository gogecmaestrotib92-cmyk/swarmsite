/* measure.mjs — check every face in faces.json (the ones a page may choose and the ones pages are already set in) against Google Fonts and measure how wide it sets.
   node lib/type/measure.mjs [--write]
   For each face: the css2 spec must answer 200 and the face must actually load in a browser; then the mean advance of
   one character of a headline is measured at the display weight, in sentence case and in capitals (`avg`, `avg_upper`,
   in em). The composer sizes a headline from these numbers, so they are measured, never guessed.
   Without --write it only reports and exits 1 when a face fails or a stored number is more than 6% off. Needs network. */
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url)); const file = path.join(here, 'faces.json');
const registry = JSON.parse(fs.readFileSync(file, 'utf8')); const write = process.argv.includes('--write');
const SAMPLE = 'Stop betting on a hunch. Your team, your game plan. Know what your launch exposed. El lugar para todos';
const mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chromePath = process.env.CHROME_PATH || (fs.existsSync(mac) ? mac : '/usr/bin/google-chrome');
const browser = await chromium.launch({ executablePath: fs.existsSync(chromePath) ? chromePath : undefined, args: ['--no-sandbox', '--disable-gpu'] });
let failed = 0;
for (const face of [...registry.faces, ...(registry.known || [])]) {
  const url = `https://fonts.googleapis.com/css2?family=${face.gf}&display=block`;
  const page = await browser.newPage();
  try {
    const status = (await page.request.get(url)).status();
    if (status !== 200) throw new Error(`css2 answered ${status} for "${face.gf}"`);
    await page.setContent(`<link href="${url}" rel="stylesheet"><span id="s" style="font:${face.display} 100px '${face.family}';white-space:nowrap"></span>`, { waitUntil: 'load' });
    const loaded = await page.evaluate(async ({ family, weight }) => { await document.fonts.load(`${weight} 100px '${family}'`); await document.fonts.ready; return document.fonts.check(`${weight} 100px '${family}'`) && [...document.fonts].some(f => f.family.replace(/['"]/g, '') === family && f.status === 'loaded'); }, { family: face.family, weight: face.display });
    if (!loaded) throw new Error('the face did not load in the browser');
    const measure = text => page.evaluate(t => { const s = document.getElementById('s'); s.textContent = t; return s.getBoundingClientRect().width / (t.length * 100); }, text);
    const avg = +(await measure(SAMPLE)).toFixed(3), upper = +(await measure(SAMPLE.toUpperCase())).toFixed(3);
    const off = Math.max(Math.abs(avg - (face.avg || 0)) / avg, Math.abs(upper - (face.avg_upper || 0)) / upper);
    console.log(`${off > .06 ? (write ? '~' : '✗') : '✓'} ${(face.id || face.family).padEnd(18)} avg ${avg} (stored ${face.avg})  upper ${upper} (stored ${face.avg_upper})`);
    if (off > .06 && !write) failed++;
    face.avg = avg; face.avg_upper = upper;
  } catch (err) { failed++; console.log(`✗ ${(face.id || face.family).padEnd(18)} ${String(err.message).slice(0, 140)}`); }
  await page.close();
}
await browser.close();
if (write) fs.writeFileSync(file, '{\n "about": ' + JSON.stringify(registry.about) + ',\n "faces": [\n' + registry.faces.map(f => '  ' + JSON.stringify(f)).join(',\n') + '\n ],\n "known": [\n' + (registry.known || []).map(f => '  ' + JSON.stringify(f)).join(',\n') + '\n ]\n}\n');   // one face per line: a change to one face is one line in a diff
process.exit(failed ? 1 : 0);
