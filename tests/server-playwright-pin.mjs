// The server image carries the browsers of ONE Playwright version (server/Dockerfile: FROM mcr.microsoft.com/playwright:vX.Y.Z).
// The image installs server/package.json without a lockfile, so a range there (^1.65.0) took 1.65.1 the day it was
// released and no capture could start ("Executable doesn't exist", production, 2026-11-14). The two must be the same
// exact version: raise them together.
import assert from 'node:assert/strict';
import fs from 'node:fs';
const image = (fs.readFileSync('server/Dockerfile', 'utf8').match(/^FROM mcr\.microsoft\.com\/playwright:v(\d+\.\d+\.\d+)/m) || [])[1];
const dep = JSON.parse(fs.readFileSync('server/package.json', 'utf8')).dependencies.playwright;
assert.ok(image, 'the server image is a Playwright image with an exact version');
assert.equal(dep, image, `server/package.json asks for playwright "${dep}"; the image carries the browsers of ${image}`);
console.log(`The server installs exactly the Playwright its image carries the browsers of (${image})`);
