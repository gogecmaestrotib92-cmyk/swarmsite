# Executable design-pattern experiment

This is a **prototype**, not part of the production pipeline. It does not call
an agent, change the supplied direction, deploy or approve a design. The
candidate is the tuple `(pattern ID, version, beat ID, blueprint ID)`. A future
consumer could ask an agent to propose that tuple, run this independent check,
and keep the original direction whenever the check fails. Applying an accepted
candidate and evaluating its design remain separate work.

`catalog.json` describes conservative subsets of existing renderer forms:
`story-assigned-product-ui@1`, `marquee-short-facts@1`, and `butter-editorial-product@1`. The Butter editorial entry allows up to six features and verifies that the renderer actually selected its specific editorial component. Each declares allowed
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
validator. The test invokes Chrome at widths 390 and 1440 with reduced and
normal motion on synthetic fixtures, checking text counts, links, overflow and
story-image geometry. Other tests cover accepted and rejected conditions,
asset ownership, unchanged source files and engine mismatch.

Run a dry-run against an existing local artifact directory containing
`direction.json` and `images.json` plus its associated input files:

```sh
python3 experiments/design-patterns/render_check.py ./my-artifact butter my-beat story-assigned-product-ui --version 1
python3 experiments/design-patterns/render_check.py ./my-artifact butter my-facts marquee-short-facts --version 1
```

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
hashes cover three key files but not all dependencies such as blueprint data,
fonts, browser and CSS: a production integration needs immutable dependency
versions, atomic validation/application and a broader regression suite.
