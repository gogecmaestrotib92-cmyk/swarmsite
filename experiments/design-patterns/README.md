# Executable design-pattern experiment

The optional `choose_patterns.py` calls a model, but does not change the supplied
direction, deploy or approve a design. The candidate is the tuple `(pattern ID,
version, beat ID, blueprint ID)`. The swarm's `pattern_stage.py` can use this
selector before rendering section moves when `SWARM_VERIFIED_PATTERNS=1` is set.
It checks the transition against the previous render and applies validated
changes. It is opt-in because it can produce a worse-looking page; there is no
visual quality gate yet. Hero moves are not covered by this catalog.

`catalog.json` describes conservative subsets of existing renderer forms:
`story-assigned-product-ui@1`, `marquee-short-facts@1`, `butter-editorial-product@1`, `pinned-text-steps@1`, `type-wall-quote@1`, `sticky-assigned-visual@1`, and three ledger layouts (`ledger-cards`, `ledger-story`, `ledger-sticky`). The Butter editorial entry allows up to six features and verifies that the renderer actually selected its specific editorial component. The pinned and quote patterns are limited to text-only sections without extra actions; ledger checks retain each item's name, price, extra fields, links and existing visuals. The actual render still has to pass. Each declares allowed
beat types and site classes, item limits, asset requirements, fallback, renderer
and reference. The reference identifies where a role was observed; it does not
claim the generated result is identical or copy any original assets.

## Run

From the repository root, install the repository's Node dependencies and make
Pillow available to the Python interpreter. Runtime tests use Playwright and a
Chromium-compatible browser. If Playwright's Chromium is installed, run:

```sh
python3 experiments/design-patterns/test.py
```

To use a locally installed browser and select a Python interpreter:

```sh
CHROME_PATH="/path/to/chrome" PYTHON=python3 python3 experiments/design-patterns/test.py
```

`CHROME_PATH` is optional; without it Playwright uses its installed Chromium.
`PYTHON` is optional and defaults to the interpreter running the test or
validator. The test invokes Chrome at widths 320, 390 and 1440 with reduced and
normal motion on synthetic fixtures, checking text counts, links, overflow and
story-image geometry. Other tests cover accepted and rejected conditions,
asset ownership, unchanged source files and engine mismatch.

Run a dry-run against an existing local artifact directory containing
`direction.json` and `images.json` plus its associated input files:

```sh
python3 experiments/design-patterns/render_check.py ./my-artifact butter my-beat story-assigned-product-ui --version 1
python3 experiments/design-patterns/render_check.py ./my-artifact butter my-facts marquee-short-facts --version 1
python3 experiments/design-patterns/explore.py ./my-artifact butter
```

`explore.py` lists accepted and rejected candidates for every compatible beat.
`choose_patterns.py ./my-artifact butter` makes a real model request using the
API key in the environment and filters its choices against that list. It then
rechecks choices sequentially in a private copy and rejects the result if its
recorded inputs changed during selection. It never modifies the job. This is
still a bounded subset: the selection can be visually worse than the baseline
and the cost and runtime grow with the number of candidates.
Pass `--preview` to render the selected choices in a new temporary directory;
the returned path is local to this machine and is not a published preview.

The script prints JSON with `accepted` and its reason or pattern details. It
renders baseline and candidate in separate temporary directories. It checks the
expected rendered form, target items, heading, lede, label, assigned image,
page link labels and destinations, section order and other sections' text and
media. The declared engine file hashes deliberately reject revision drift;
regenerate them only as part of revalidating the catalog against a new engine.

## Limits

Checks compare with the existing rendered baseline. They cannot detect source
material already omitted there, or establish that all source links survived
before this step. Accepted patterns can still be semantically inappropriate or
visually weak; no source semantic classification, design quality, complete
accessibility or production acceptance is asserted. Current tests use synthetic
Chrome fixtures; they do not constitute a production deployment test. Engine
hashes cover four key files but not all dependencies such as blueprint data,
fonts and browser. The production stage snapshots relevant files and applies a
validated direction atomically, but cannot guarantee that source material was
complete or that the selected design is visually good.
