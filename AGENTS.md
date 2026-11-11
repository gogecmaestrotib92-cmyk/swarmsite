# AGENTS.md — rules for anyone (human or model) landing code in this repo

## The step before you land code
Every significant change goes through, in this order, before `git commit`:

1. **Live test** — not "it compiles". Run `scripts/livetest.sh`. It renders the sample direction through every blueprint, runs the contract (`lib/qa/contract.mjs`) on each render at 1440 and 390, and fails if any render errors or any contract scores below 75. When the change touches the server, capture or the swarm, also run a real job through `https://swarmsite.si/app` (or `POST /jobs`) in the browser and read `critic.json`, `contract.json` and `swarm.json` for that job — the trace, not the vibe.
2. **Autoreview** — read the full diff (`git diff --staged`) as a reviewer who did not write it: what breaks on a site with no photos, on a phone, on a dark band, with a 9-word h1? Fix before committing, never after.
3. **Commit** — one change per commit, message says what the page does differently, not what the code does.
4. **Track** — append one line to `REFACTOR.md` under today's date: what changed, the live-test result, the next bottleneck.

## Broken layout never ships (added 2026-11-10)
`lib/qa/layout.mjs <page.html>` measures every heading and paragraph at 390, 768, 1100, 1440 and 1920 and names what is broken as typesetting: a heading stacked a word to a line, a split word, a line of punctuation alone, a paragraph in a sliver of a column, text clipped or lying over other text. It is not a matter of taste and it is not weighed against the critic. `scripts/livetest.sh` fails on any break in any blueprint. In the loop (`lib/swarm/run.py mend_layout`) a composed section with a break goes back to what it was before composition, and a composed page whose first screen is broken is refused. A new kind of breakage seen on a real page becomes a check in `layout.mjs` with a fixture in `tests/layout-breaks.mjs` — never a patch for that one page. Check widths between and beyond the two the contract uses: the column that started this was fine at 1440 and 186 px wide at 1800.

## The landing is the engine's first client (added 2026-11-11)
`web/index.html` is held to what a client's page is held to. Its movement is the library's devices (`lib/devices/registry.py`), written into the page by `python3 scripts/landing_devices.py` from the list in `<style id="dv-css" data-devices="…">` — never edited there by hand, never a second motion library beside them. `tests/test_landing_devices.py` fails when the page's copy differs from the library, when it breaks a device's own rule (how often, how long), or when a fact it states is no longer what the code does. `tests/landing-layout.mjs` is its gate: the layout check at five widths, the headline standing by 1.5 s, nothing left hidden, no ground of one section over the next, links, the field and the phone menu answering. Change a device in the library and the landing changes with every client page: run the script, look at the page. It shows no example of the engine's work until the owner calls one worth showing (2026-11-11).

## Effort
Use high effort for anything in `lib/render`, `lib/swarm`, `lib/qa`, `server/`. A cheap pass that "looks fine" has cost us a day more than once (sticky that never stuck, text invisible on dark bands, the same picture four times).

## What the loop is (see LOOPS.md)
Deterministic renderer + blueprints = the engine. Agents only write `direction.json`. The critic grades taste; the contract grades promises. Neither is allowed to edit the page directly.

## Deploys kill runs
Railway restarts the worker on every push; a job that was running is lost (the worker now marks it failed on boot). Before `git push`, check nothing is running: `GET https://swarmsite-production.up.railway.app/jobs?status=running` — or accept that you are killing it and say so.

## Never
- Never paste secrets into code, logs or chat. Keys live in Railway variables; the owner sets them.
- Never add a model call inside the renderer.
- Never fix a critic finding by special-casing one site; fix the rule that let it through.

## Working in parallel (added 2026-11-08)
`main` is the deployed branch. Any agent other than the owner's active session works on a branch and opens a PR. Before every commit: `npm test` (pytest + every `tests/*.mjs`) and `scripts/livetest.sh 80` must both pass. A test that a change breaks is fixed or consciously updated in the same commit — never left red.
