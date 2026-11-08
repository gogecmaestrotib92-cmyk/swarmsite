# AGENTS.md — rules for anyone (human or model) landing code in this repo

## The step before you land code
Every significant change goes through, in this order, before `git commit`:

1. **Live test** — not "it compiles". Run `scripts/livetest.sh`. It renders the sample direction through every blueprint, runs the contract (`lib/qa/contract.mjs`) on each render at 1440 and 390, and fails if any render errors or any contract scores below 75. When the change touches the server, capture or the swarm, also run a real job through `https://swarmsite.si/app` (or `POST /jobs`) in the browser and read `critic.json`, `contract.json` and `swarm.json` for that job — the trace, not the vibe.
2. **Autoreview** — read the full diff (`git diff --staged`) as a reviewer who did not write it: what breaks on a site with no photos, on a phone, on a dark band, with a 9-word h1? Fix before committing, never after.
3. **Commit** — one change per commit, message says what the page does differently, not what the code does.
4. **Track** — append one line to `REFACTOR.md` under today's date: what changed, the live-test result, the next bottleneck.

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
