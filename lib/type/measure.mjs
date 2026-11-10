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
    // how the face holds an accent to its letter: the empty rows between the caron and the "s" of "š", in em, at the display
    // weight; null when the face does not draw the letter itself. A page in Serbian, Croatian, Czech or Polish is set in these.
    face.accent_gap = await page.evaluate(async ({ family, weight }) => {
      await document.fonts.load(`${weight} 100px '${family}'`, 'šŠčćž');   // the subset that holds these letters is loaded only when asked for
      const pen = document.createElement('canvas').getContext('2d'), wide = fb => { pen.font = `${weight} 100px '${family}', ${fb}`; return pen.measureText('š').width; };
      if (wide('monospace') !== wide('serif')) return null;
      const c = document.createElement('canvas'); c.width = 500; c.height = 600; const x = c.getContext('2d'); x.font = `${weight} 300px '${family}'`; x.fillText('š', 80, 440);
      const d = x.getImageData(0, 0, 500, 600).data, rows = []; for (let y = 0; y < 600; y++) { let ink = false; for (let i = 0; i < 500; i++) if (d[(y * 500 + i) * 4 + 3] > 60) { ink = true; break; } rows.push(ink); }
      let i = 0; while (i < 600 && !rows[i]) i++; const top = i; while (i < 600 && rows[i]) i++; const from = i; while (i < 600 && !rows[i]) i++;
      if (i >= 600) return { gap: 0, shift: 0, width: 1 };
      const span = (y0, y1) => { let a = 500, b = 0; for (let y = y0; y < y1; y++) for (let k = 0; k < 500; k++) if (d[(y * 500 + k) * 4 + 3] > 60) { if (k < a) a = k; if (k > b) b = k; } return [a, b]; };
      const mark = span(top, from), letter = span(i, 600);
      return { gap: +((i - from) / 300).toFixed(3), shift: +(((mark[0] + mark[1]) / 2 - (letter[0] + letter[1]) / 2) / 300).toFixed(3), width: +((mark[1] - mark[0]) / Math.max(1, letter[1] - letter[0])).toFixed(2) };
    }, { family: face.family, weight: face.display });
  } catch (err) { failed++; console.log(`✗ ${(face.id || face.family).padEnd(18)} ${String(err.message).slice(0, 140)}`); }
  await page.close();
}
await browser.close();
const rows = list => list.map(f => '  ' + JSON.stringify(f)).join(',\n');   // one record per line: a change to one face is one line of diff
if (write) fs.writeFileSync(file, '{\n "about": ' + JSON.stringify(registry.about) + ',\n "faces": [\n' + rows(registry.faces) + '\n ],\n "pairings": [\n' + rows(registry.pairings || []) + '\n ],\n "known": [\n' + rows(registry.known || []) + '\n ]\n}\n');
process.exit(failed ? 1 : 0);
