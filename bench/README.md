# bench — the design-quality benchmark

Compares engine variants on **identical frozen input**, so a difference between two pages comes from how the page is
composed, not from a different capture or different words. Plan: `SWARMSITE_CREATIVE_ENGINE_V2_PLAN.md` §10;
what is asked of raters: `SWARMSITE_PRODUCT_STRATEGY.md` §4.

## Files

| File | What it is |
|---|---|
| `sites.json` | The fixed set. A site enters once, with the job its artefacts were frozen from. Target: 30 (20 dev, 10 hold-out). |
| `fetch.py` | Downloads each job's artefacts into `seed/<id>/`. Read-only, no credentials. |
| `run.py` | Renders one variant over the set and measures it: contract at 1440 and 390, structural fingerprint, full-page pictures. No model call. |
| `fullshot.mjs` | One top-to-bottom picture per viewport, motion off. |
| `compare.py` | Builds a blind side-by-side page from two variants, and tallies exported answers. |
| `seed/`, `runs/` | Frozen inputs and outputs. **Not committed**: they hold third-party text and images. |

## Use

```bash
python3 bench/fetch.py
python3 bench/run.py shipped
python3 bench/run.py recipe
python3 bench/compare.py build shipped recipe
open bench/runs/compare-shipped-vs-recipe/index.html
python3 bench/compare.py score bench/runs/compare-shipped-vs-recipe ~/Downloads/answers-<id>.json
```

Needs Python ≥ 3.12 (the renderer does not parse on older versions), node with `playwright`, and a Chrome
(`CHROME_PATH`; on macOS the installed Google Chrome is found automatically).

## Variants that need no model

| Variant | What changes |
|---|---|
| `shipped` | Nothing: the direction as the job left it, through today's renderer. |
| `house` | The house lock applied — order and move of every section fixed per kind. |
| `recipe` | No house, per-section moves cleared — the chosen recipe's own slots decide the forms. |

Variants that need the model (three concepts, composed heroes) are added as they are built; they must start from the
same `seed/` files.

## Rules

- The set is fixed before results exist. A site is never swapped out afterwards.
- A site the engine was tuned on (`tuned_on` in `sites.json`) may not be in the hold-out.
- Technical and creative results are reported separately and never averaged.
- `key.json` of a comparison is not opened until the answers are in.
- 65% preference means little below about 150 judgments; `compare.py score` prints the 95% interval so this is visible.

## Adding a site

Run a job for the URL (the app or `POST /jobs`), wait for it to finish, then add an entry to `sites.json` with the job
id, kind, subtype, the blueprint from the job's `swarm.json` (`best_blueprint`), the mode from its `brief.json`, and the
group. Then `python3 bench/fetch.py <id>`.
