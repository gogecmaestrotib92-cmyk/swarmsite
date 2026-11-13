# AGENTS.md — rules for anyone (human or model) landing code in this repo

## The step before you land code
Every significant change goes through, in this order, before `git commit`:

1. **Live test** — not "it compiles". Run `scripts/livetest.sh`. It renders the sample direction through every blueprint, runs the contract (`lib/qa/contract.mjs`) on each render at 1440 and 390, and fails if any render errors or any contract scores below 75. When the change touches the server, capture or the swarm, also run a real job through `https://swarmsite.si/app` (or `POST /jobs`) in the browser and read `critic.json`, `contract.json` and `swarm.json` for that job — the trace, not the vibe.
2. **Autoreview** — read the full diff (`git diff --staged`) as a reviewer who did not write it: what breaks on a site with no photos, on a phone, on a dark band, with a 9-word h1? Fix before committing, never after.
3. **Commit** — one change per commit, message says what the page does differently, not what the code does.
4. **Track** — append one line to `REFACTOR.md` under today's date: what changed, the live-test result, the next bottleneck.

## Broken layout never ships (added 2026-11-10)
`lib/qa/layout.mjs <page.html>` measures every heading and paragraph at 390, 768, 1100, 1440 and 1920 and names what is broken as typesetting: a heading stacked a word to a line, a split word, a line of punctuation alone, a paragraph in a sliver of a column, text clipped or lying over other text. It is not a matter of taste and it is not weighed against the critic. `scripts/livetest.sh` fails on any break in any blueprint. In the loop (`lib/swarm/run.py mend_layout`) a composed section with a break goes back to what it was before composition, and a composed page whose first screen is broken is refused. A new kind of breakage seen on a real page becomes a check in `layout.mjs` with a fixture in `tests/layout-breaks.mjs` — never a patch for that one page. Check widths between and beyond the two the contract uses: the column that started this was fine at 1440 and 186 px wide at 1800.

## The landing is the engine's first client (added 2026-11-11, rebuilt 2026-11-12)
`web/index.html` is held to what a client's page is held to, and is built the way a client's page now is: on a template of the library — its measured build (sizes, spacing, type scale, radii, buttons, motion) with our words swapped in (owner, 2026-11-12). The shared layer of every page is `web/css/site.css` (tokens, type, buttons, nav box, fields); the landing's sections are `web/css/landing.css`; its movement is the template's own script, `web/js/landing.js` — no second motion library beside it. The product's header (`web/header.css`) is the same nav box. There is one way into a job from every entry: `POST /jobs` with `options.engine='templates'` (an address; an address with `options.screens`, the visitor's screenshots sent to `POST /uploads`; or the `/start` form with `options.source='form'`) — the old brief form is gone. In the chooser the line above each card says where that design stands; nothing says "ready" for all three while one is not. Never name the reference a template was rebuilt from anywhere in `web/`. `tests/test_landing.py` fails when a fact the page states is no longer what the code does, when the three ways in or the address field move from the opening, or when a page names a reference; `tests/landing-layout.mjs` is its gate (layout at five widths, headline by 1.5 s, nothing hidden, no spill, links/field/menu answering, readable words); before a change to it lands, serve `web/` and run `node lib/qa/template_gate.mjs <its address> --no-more`, which judges it on pixels at 1440 and 390 (no test runs this for you). What it shows of our work is our own interface photographed with a made-up client of `tests/fixtures/templates/` (`web/visuals/ui-*.webp`: the working screen, the chooser, the editor, one finished design) — never a real client's page until the owner calls one worth showing (2026-11-11, 2026-11-13). Scripts and stylesheets of `web/` are never cached for days (`web/vercel.json`, `tests/test_web_cache.py`).

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
