// A photographed part of a page that drew nothing is not a picture of the product: an embed that failed to load was
// photographed as a grey box with the browser's sad page in it and stood in three designs as the product (a visitor's
// job, 2026-11-22). flatShot reads the share of the commonest tone; at FLAT_SHOT or above the capture leaves it out.
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { flatShot, FLAT_SHOT } from '../lib/pipeline/flat.mjs';

const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
try {
  const p = await b.newPage();
  const svg = body => 'data:image/svg+xml;utf8,' + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650">${body}</svg>`);
  const failed = svg('<rect width="900" height="650" fill="#dcdcdc"/><rect x="415" y="283" width="32" height="40" fill="none" stroke="#555" stroke-width="3"/>');
  const product = svg('<rect width="900" height="650" fill="#0b1020"/>' + Array.from({ length: 12 }, (_, i) => `<rect x="${40 + (i % 4) * 210}" y="${60 + Math.floor(i / 4) * 190}" width="180" height="150" rx="12" fill="hsl(${i * 30},60%,${30 + i * 3}%)"/>`).join(''));
  assert.ok(await flatShot(p, failed) >= FLAT_SHOT, 'a grey box with an icon is flat');
  assert.ok(await flatShot(p, product) < .6, 'a product panel with many parts is not');
  assert.equal(await flatShot(p, 'data:image/png;base64,not-a-picture'), 0, 'a picture that cannot be read is not called flat');
  console.log('A photographed part that drew nothing (a failed embed, an empty box) is read as flat and left out; a product panel is kept');
} finally { await b.close(); }
