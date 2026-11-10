# Design DNA

The engine's 12 design references, each as one structured record: what was measured on the original, where each number comes from, what was never measured, and which design principles follow from the numbers. A model that picks or adapts a reference is given these records (as compact cards), not one line of text per reference.

This is a library of evidence. It does not render anything, it calls no model, and nothing in the production path reads it yet.

## The one rule

**A value in a record is copied or computed from a named field of the reference's own files and says where from, or it is `null`.** Nothing is written from knowledge of the original website.

The files are `lib/blueprints/<id>.bp.json` (the normalised blueprint) and `lib/blueprints/raw/<id>.json` (the capture it was normalised from). How the rule is kept:

- **Defaults are not measurements.** `lib/blueprint/normalize.py` fills gaps: weight 400, leading 1.05 or 1.1, align `start`, x 0, gutter 40, frame = gutter, a viewport 1440 wide, h2 = display. Where the raw capture has no field behind a blueprint value, the record holds `null` and names the attribute in `not_recorded`.
- **Roles and notes are annotations.** `lib/blueprint/extract.js` emits neither; someone wrote them into the raw file. A role is carried as a label. A note is carried only as `{"kind": "prose", "source": "<pointer>", "text": …}` and the validator checks that the text is what the pointer holds.
- **Fractions have a denominator.** `head.x`, `head.wf`, `media.wf`, `media.xf` are pixels over the viewport width. Only three captures record that width; for the rest the normaliser assumed 1440, and `composition.fraction_base.basis` says `assumed`.
- **Tracking is recomputed.** The blueprint rounds letter-spacing to whole pixels before dividing, so `-2.4px` at 120px becomes −0.017em. The record computes it from the raw value: −0.02em.
- **Absent is not zero.** `extract.js` drops `normal`, `none`, `0px` and `false`. A missing `ls` or `tt` may mean "normal" or may mean "not written down", and most raw files were condensed by hand. Those come out `null`. The one exception is `media.bleed`, a flag: absent reads as `false`.
- **Principles come from rules.** Each is produced by a function in `build.py` from values in the record, names its threshold in its statement, and points at the values it used. No rule speaks about motion feel, mobile or interaction, because none of that was measured.

## What is in here

| File | What it is |
|---|---|
| `build.py` | The generator. Reads blueprints, raw captures, `evidence.json`; writes `references/*.json` and the tables below. Same input, same bytes. |
| `evidence.json` | Hand-written: which folder holds screenshots of an original, which blueprint an authored one mirrors, and known caveats with the files that show them. |
| `references/<id>.json` | The records. Generated; do not edit. |
| `schema.json` | JSON Schema of a record, with the meaning of each field. The validator reads it. |
| `validate.py` | Checks every record against the schema and against the files it cites. Standard library only. |
| `retrieve.py` | `retrieve(brand, k)`: the references that fit a brand, with scores, reasons and a compact card. Standard library only. |
| `inspect.mjs` | A measuring instrument, separate from the records: `node design_dna/inspect.mjs <id> <url>` reads a live page in a browser at 1440 and 390 — type, geometry, sections, pictures, surfaces, what moves on load and on scroll, pointer, reduced motion, one lab run — and writes `evidence.json` and screenshots to `bench/runs/_research/` (untracked, research only). The records below are not built from it; `SWARMSITE_DESIGN_REFERENCE_RESEARCH.md` is. |

```bash
python3 design_dna/build.py            # rebuild the records and the tables in this file
python3 design_dna/build.py --check    # exit 1 if anything on disk differs from the build
python3 design_dna/validate.py         # exit 1 and a list of problems, or "12 records valid"
python3 design_dna/retrieve.py out/<job>   # the references for a job folder; --k N, --json
python3 -m pytest tests/test_design_dna.py -q -p no:cacheprovider
```

`build.py` and `validate.py` import `font_for` from `lib/render/render_bp.py`, so they need the Python the renderer needs (3.10 or newer). `retrieve.py` reads only the records.

## Reading a record

- `status`: `measured-desktop` (a raw capture exists; one viewport), `authored` (no capture; a recipe, never evidence), `incomplete`.
- `source`: url, viewport as recorded, `captured_at` and `dpr` (null for every reference: no file records them).
- `evidence`: the blueprint and raw file, screenshots by path, caveats. `built_from` holds the sha256 of each input; a changed input makes the record stale and the validator says so.
- `completeness`: one word per dimension. See the table below.
- `typography`: per level the source face, the face that ships (`delivery_face`, exactly what `font_for` returns; `delivery_fallback: true` when the renderer has no mapping and fell back to its generic face), px, weight, tracking, leading, case. `display` is the largest heading anywhere on the page, which is not always the hero headline. `ratios` are computed.
- `composition`: grid, page surface (light or dark), and per section the role, height in screens, first heading (`x`, `y`, `wf`, `px` …) and media (`ar`, `wf`, `xf`, `bleed`, `kind`). `summary` holds the computed figures; each has `how` (the formula), `evidence` (the values it ranged over) and `matched` (the ones that counted).
- `imagery`: aspect ratios, portrait and landscape shares, how many sections hold a large still, whether the first section holds a video.
- `motion`: library flags, CSS transition strings and keyframe names as captured, plus the prose note. Nothing here describes how the page moves.
- `experience`: pacing (measured) and the per-section prose notes.
- `principles`: `{id, statement, evidence, derived_by: "rule", confidence, rule}`. `confidence` is `measured`, or `observed` when the rule rests on a hand-written role name alone.
- `fits`: `kinds` (the blueprint's class), `needs` and `temper`, both derived by rule.
- `rights`, `implementation`: below.

Two pointer forms: a file pointer `lib/blueprints/raw/tengile.json#/sections/0/heads/0` (repo path + JSON pointer) and an internal pointer `composition.sections[2].media[0].ar` (into the record).

## What the 12 hold today

<!-- GENERATED by design_dna/build.py: do not edit between these markers -->
### Completeness

| Reference | Status | Viewport w × h | Typography | Composition | Imagery | Motion | Experience | Mobile | Screenshots | Principles |
|---|---|---|---|---|---|---|---|---|---|---|
| aino | measured-desktop | 1440 × 756 | partial (2 of 5 levels) | measured-desktop | measured-desktop | partial | prose-only | missing | missing | 6 |
| atelier | authored | not recorded × not recorded | authored (4 of 5 levels) | authored | authored | authored | authored | missing | missing | 0 |
| belgrade-arbor | measured-desktop | not recorded × 756 | measured (4 of 5 levels) | measured-desktop | measured-desktop | partial | prose-only | missing | missing | 9 |
| butter | measured-desktop | 1440 × 756 | measured (4 of 5 levels) | measured-desktop | measured-desktop | partial | missing | missing | unverified (16 files) | 3 |
| cerebrium | measured-desktop | 1440 × 756 | measured (5 of 5 levels) | measured-desktop | measured-desktop | partial | prose-only | missing | unverified (27 files) | 6 |
| crav | measured-desktop | not recorded × 756 | measured (4 of 5 levels) | measured-desktop | measured-desktop | partial | prose-only | missing | missing | 3 |
| deepbook | measured-desktop | not recorded × 756 | measured (4 of 5 levels) | measured-desktop | measured-desktop | partial | prose-only | missing | unverified (15 files) | 5 |
| halfdays | measured-desktop | not recorded × 756 | measured (4 of 5 levels) | measured-desktop | measured-desktop | partial | prose-only | missing | missing | 6 |
| lpas | measured-desktop | not recorded × 756 | measured (4 of 5 levels) | measured-desktop | measured-desktop | partial | prose-only | missing | missing | 6 |
| tengile | measured-desktop | not recorded × 756 | measured (5 of 5 levels) | measured-desktop | measured-desktop | partial | prose-only | missing | missing | 9 |
| units | measured-desktop | not recorded × 756 | measured (2 of 5 levels) | measured-desktop | measured-desktop | partial | prose-only | missing | missing | 3 |
| white-desert | measured-desktop | not recorded × 756 | measured (5 of 5 levels) | measured-desktop | measured-desktop | partial | prose-only | missing | missing | 8 |

Capture date and device pixel ratio: not recorded for any reference.

### Rules and where they fired

| Principle | Rule in build.py | Temper tag | Fired on | References |
|---|---|---|---|---|
| scale-contrast-high | `rule_scale_contrast_high` | high-contrast-type | 4 | belgrade-arbor, crav, tengile, white-desert |
| scale-contrast-low | `rule_scale_contrast_low` | even-type | 2 | halfdays, units |
| display-light-weight | `rule_display_light_weight` | light-weight | 3 | belgrade-arbor, cerebrium, tengile |
| display-heavy-weight | `rule_display_heavy_weight` | heavy-weight | 2 | aino, units |
| display-uppercase | `rule_display_uppercase` | uppercase | 3 | belgrade-arbor, tengile, white-desert |
| tight-tracking | `rule_tight_tracking` | tight-tracking | 5 | aino, cerebrium, deepbook, halfdays, tengile |
| tight-leading | `rule_tight_leading` | tight-leading | 4 | crav, halfdays, tengile, white-desert |
| single-family | `rule_single_family` | one-family | 3 | deepbook, halfdays, lpas |
| offset-headings | `rule_offset_headings` | asymmetric | 4 | belgrade-arbor, butter, cerebrium, tengile |
| full-bleed-media | `rule_full_bleed_media` | full-bleed | 3 | belgrade-arbor, lpas, white-desert |
| portrait-media | `rule_portrait_media` | portrait-imagery | 3 | aino, halfdays, tengile |
| landscape-media | `rule_landscape_media` | landscape-imagery | 2 | lpas, white-desert |
| image-led | `rule_image_led` | image-led | 4 | aino, belgrade-arbor, crav, lpas |
| type-led | `rule_type_led` | type-led | 2 | cerebrium, deepbook |
| video-first-section | `rule_video_first_section` | video-led | 5 | aino, belgrade-arbor, lpas, tengile, white-desert |
| pinned-sections | `rule_pinned_sections` | pinned | 7 | belgrade-arbor, butter, cerebrium, deepbook, lpas, units, white-desert |
| dark-page | `rule_dark_page` | dark | 3 | aino, cerebrium, deepbook |
| long-page | `rule_long_page` | long | 4 | belgrade-arbor, butter, tengile, white-desert |
| short-page | `rule_short_page` | compact | 1 | halfdays |

### What a brand has to bring

| Reference | Kind | Surface | Image-bearing sections (`needs.images_min`) | Video in first section | Caveats |
|---|---|---|---|---|---|
| aino | service | dark | 6 | yes | none |
| atelier | service | light | not derived (authored) | not derived (authored) | none |
| belgrade-arbor | place | light | 12 | yes | none |
| butter | software | light | 5 | no | profile-display-size-differs |
| cerebrium | software | dark | 2 | no | profile-page-height-differs, profile-display-size-differs |
| crav | product | light | 6 | no | none |
| deepbook | software | dark | 0 | no | profile-url-differs |
| halfdays | product | light | 3 | no | none |
| lpas | service | light | 3 | yes | none |
| tengile | place | light | 6 | yes | none |
| units | place | light | 4 | no | none |
| white-desert | place | light | 5 | yes | none |

### Faces: what was measured and what ships

| Source face | Ships as (`font_for`) | Class | Mapping in the renderer | Licence note, source face | Licence note, shipped face | References |
|---|---|---|---|---|---|---|
| ABC Favorit | Bricolage Grotesque | sans | mapped | Dinamo — paid | OFL | cerebrium |
| abcplus | Hanken Grotesk | sans | mapped | unknown | unknown | aino |
| Aeonik | Manrope | sans | mapped | unknown | OFL | atelier, lpas |
| Aeonik Pro | Manrope | sans | mapped | unknown | OFL | units |
| Bunch | Geist | sans | none: generic fallback | unknown | unknown | units |
| Cardinal Classic Long | Instrument Serif | serif | mapped | unknown | OFL | white-desert |
| DieGrotesk | Schibsted Grotesk | sans | mapped | unknown | OFL | butter |
| editorialOld | Instrument Serif | serif | mapped | unknown | OFL | belgrade-arbor |
| Instrument Serif | Instrument Serif | serif | mapped | OFL | OFL | atelier |
| Inter | Geist | sans | mapped | unknown | unknown | tengile |
| Inter Tight | Geist | sans | mapped | unknown | unknown | white-desert |
| Modak | Modak | sans | mapped | unknown | unknown | crav |
| Mouse Memoirs | Mouse Memoirs | sans | mapped | unknown | unknown | crav |
| Oswald | Oswald | sans | mapped | unknown | unknown | white-desert |
| PP Fragment | Cormorant Garamond | serif | mapped | unknown | unknown | tengile |
| Suisse Intl | Geist | sans | mapped | Swiss Typefaces — paid | unknown | cerebrium |
| Suisse Intl Mono | Geist | sans | mapped | Swiss Typefaces — paid | unknown | cerebrium |
| SuisseIntl | Geist | sans | none: generic fallback | unknown | unknown | halfdays |
| TWKEverett | Hanken Grotesk | sans | mapped | unknown | unknown | deepbook |
| Work Sans | Work Sans | sans | mapped | unknown | unknown | belgrade-arbor |
<!-- /GENERATED -->

How to read the completeness words:

- **Typography** `measured`: the largest heading and the body paragraph are both bound to an element of the capture. `partial`: some level is. Single attributes can still be null; each level lists them in `not_recorded`.
- **Composition, imagery** `measured-desktop`: one desktop capture, 756px high. The capture is a sample: the first 16 blocks, and a few headings and media per block (two and three in today's `extract.js`; the normaliser keeps at most four media). Counts are lower bounds.
- **Motion** `partial`: transition strings, keyframe names or library flags exist. Scroll, pinning, sequencing, interaction and reduced-motion behaviour were not measured for any reference.
- **Experience** `prose-only`: hand-written notes exist. `missing`: not even those (butter).
- **Mobile** `missing` for all 12: no raw file holds a second viewport.
- **Screenshots** `unverified`: files exist under `dna/<id>/`, but no file records the viewport or date of a screenshot, so none can be filed as desktop or mobile. Caveats for these three are listed in the last table and in each record.
- **authored** (atelier): no raw file. The blueprint is `lpas.bp.json` with three fields changed (`evidence.mirrors.differs_at`). The record carries the blueprint's values so the recipe can be described; it has no principles, no needs, and retrieval never returns it.

## Rights

- Screenshots of the originals are third-party material: **research only**. Records name them by path. They are never copied into this folder, into an export or onto a page.
- Source text is **excluded**. The raw files contain headings, button labels and page titles of the originals; `build.py` never reads those fields into a record, withholds a prose note that quotes one (12 characters or more), and `validate.py` fails a record that shares 60 characters with any of them or contains a whole one of 12 characters or more.
- Fonts: `rights.fonts` lists each source face and each delivery face with the licence note `lib/typography/fonts.json` holds for it, or `unknown` when the face is not listed there. Most are `unknown`; that is the state of the file, not a finding that a face is free.
- A principle is a statement about form with its numbers. It is not a licence to reproduce a reference.

## Retrieval

```python
retrieve({"kind": "place", "subtype": "restaurant", "photographs": 8, "screenshots": 0,
          "has_video": False, "mode": None, "temper": []}, k=4)
```

Returns the best `k` references, each with `score`, `components`, `reasons` (what matched), `gaps` (what did not), `applies` (which of its principles the brand asks for or owns the material for) and `card`. The scoring is written out in the docstring of `retrieve.py`: kind 40, imagery 30, temper 10, mode 10, video 5, subtype 5. A reference of another kind is returned only when the brand can meet its image need and one of its principles applies. An `authored` reference is never returned. Ties break by id, so the same brand always gets the same list.

`brand.temper` uses the temper tags in the rules table above. `brand_from_job(job_dir)` derives a brand from `direction.json`, `images.json` and `hero.mp4`. The folder has no `__init__.py`; load `retrieve.py` by path with `importlib`, as `tests/test_design_dna.py` does.

Two things retrieval cannot know from the records: whether a reference's stills are photographs or product screenshots (the capture does not say, so a brand's photographs and screenshots are counted together), and anything about taste beyond the measured tags.

## Adding a reference

1. Capture it: run `lib/blueprint/extract.js` on the live page and save the output as `lib/blueprints/raw/<id>.json`. Record what the 11 existing captures lack: viewport width and height, device pixel ratio, the date, and a second capture at a phone width. Add `class` and `archetype`; add roles and notes if you want them, knowing they will be treated as annotations.
2. Normalise it: `python3 lib/blueprint/normalize.py lib/blueprints/raw/<id>.json`, and add a recipe under the same id in `lib/templates/recipes.py`.
3. Register it in `evidence.json`: `{"screenshots": null, "caveats": []}`, or the screenshot folder and each known caveat with the pointers that show it.
4. `python3 design_dna/build.py`, then `python3 design_dna/validate.py`. The build stops if a blueprint value cannot be traced to the capture.
5. Read the new record. A principle you expected and did not get means the value behind it is null: fix the capture, not the record.

New kinds of evidence (a capture date, a mobile capture, classified screenshots) need a field in `schema.json`, a line in `build.py` that fills it from a file, and a check in `validate.py`. The validator already refuses a date, a pixel ratio, a mobile claim or a `present` screenshot status that has no file behind it.

To add a principle: write a `rule_…` function in `build.py` that reads the record and returns a statement with its threshold and the pointers it used, add it to `RULES` with a temper tag, add the tag to `TEMPER_TAGS` in `retrieve.py`, rebuild.
