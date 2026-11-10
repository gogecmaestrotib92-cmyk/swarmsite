# Swarmsite — visual failure root cause (Automateed)

Diagnostic case: production job `a00bf117-6dc7-46a9-9f1e-37d50712de93` (automateed.com, 2026-11-10, after PR #14).
Written 2026-11-10. Every claim below is marked **[A]** read from that job's artefacts, **[C]** read from code,
**[M]** measured by me in a browser on the served page, or **[H]** hypothesis, not verified.

Artefacts read: `brief.json`, `direction.json`, `inventory.json`, `composition.json`, `critic.json`, `contract.json`,
`swarm.json`, `scores.json`, `coverage.json`, `findings.json`, and the served page. Not available: the critic's own
screenshots for this job (they are not uploaded), so what the critic *saw* is inferred from what it wrote.

## 1. What the job recorded

- Mode `seo-safe`; no goal, kind or keep text given **[A brief.json]**.
- Three rounds: template rounds 1–2 at taste 56 / contract 95; round 3 is the composed page, taste 62 / contract 100,
  kept by gates against the template read again at 52 **[A swarm.json, composition.json]**.
- Scorecard: technical **pass**, hard failures none; creative **fail** (62 < 70), page level 2.5 **[A scores.json]**.
- Contract SEO block: 98.1% of the source's words on the page, 29/29 internal links kept **[A contract.json]**.

## 2. The failures, traced

### B — heading stacked a word to a line ("What could your book earn?")

- **[M]** `#earn h2`: 64 px in a column 264 px wide at 1440 and **186 px at 1800** — the column narrows as the screen widens.
- **[A]** The pictures composer chose `{"form": "stage", "side": "right", "cols": 8, "title": "lg"}`.
- **[C]** `lib/compose/pictures.py`: the picture takes `cols/12` of the *screen*; the words get what is left minus the
  page margin and padding. `_heading_fits` checked only that the heading's **longest word** fits, at 1440 only.
- **[A]** The critic did not report it (its finding on this section, IMG-01, is about the screenshot). The contract
  checks at 1440 and 390 and has no check for this.
- **Class:** composition failure (type B), made possible by a QA gap: nothing measured rendered line boxes, and
  nothing looked between or beyond the two contract widths.

### C — raw link runs and the long accordion

Two separate mechanisms, both deterministic renderer code, neither an agent's choice:

1. **"Original links" under a section** — **[C]** `render_bp.py captured_source_actions`: every link the source section
   offered (up to 20) is appended under the beat that owns that section, as underlined text links. A card on the
   source that is one `<a>` becomes one link whose name is its whole text. **[M]** `#toolkit`: 11 such links, the
   longest 164 characters.
2. **"More about us"** — **[C]** `render_bp.py seo_archive`: in `seo-safe` mode every source section less than 85%
   covered by the page's words is added as an accordion row (up to 6000 characters each), plus every internal link
   the page lost. **[M]** `#more`: 2493 px tall at 1440, 29,419 characters, 22 links.

- **Why they exist:** **[C]** `lib/qa/contract.mjs` — `seo-text-kept` needs ≥ 95% of the source's words **on this
  page** (weight 3) and `seo-links-kept` needs every internal link (weight 2). `seo-safe` is the default mode
  (`lib/seo.py mode`). The system equates "preserved" with "present on the homepage". This is the confirmed root cause.
- **The critic saw it and said so, twice** — **[A]** `critic.json`, finding USE-03: *"After the plate come ten
  accordion rows that repeat the section titles…"*, correction `{"op": "drop_beat", …}`. Nothing happened because
  (a) **[C]** the archive is not a beat, so `drop_beat` has nothing to remove, (b) removing it would break the SEO
  promises the contract enforces, and (c) **[C]** the composed page is the last step of `main()` — no repair round
  runs after it, so its findings are written down and never acted on.
- **Class:** content-architecture failure (type A) by design, plus a repair-authority failure.

### D / E — page coherence, generic feature grid

- **[A]** The plan named the device ("stepped headline with one italic word"), two carriers (`earn`, `includes`) and
  the closing as the event; `toolkit` was planned **plain**. The device pass carried it to three headings.
- **[A]** Critic: *"picture work is thin… the toolkit is a plain 3x2 text grid… the page repeats one tidy column
  logic"* (ART-02, ART-01, CMP-05, HIE-01). Corrections all `{"op": "layout", …}` in prose.
- **[C]** A `layout` op is free text handed to an agent in the *next template round*; no round follows composition.
- **[A]** `images.json` holds book covers and one product screenshot (the calculator); the critic notes a cover
  "was assigned" and unused in the toolkit **[not verified which image]**.
- **Class:** creative-direction + execution (types C, F): a heading treatment alone does not make a section carry
  a device, and no form exists for "feature list with the product's pictures".

### F — why none of this blocked delivery

- **[A]** technical pass, creative fail (62 against a bar of 70) — and the page was delivered. **[C]** `composed_candidate`
  refuses a composed page only when it is worse than the template it replaces; I found no step that withholds or
  retries a page for being under the creative bar **[not exhaustively verified in `server/`]**.
- Typography geometry was not measured at all (above).

## 3. Confirmed root causes

| # | Cause | Evidence |
|---|---|---|
| 1 | Preservation is defined as presence on the homepage (95% of words, all links) and paid for with an appended archive and link runs | contract.mjs seo checks; render_bp `seo_archive`, `captured_source_actions` |
| 2 | Rendered text geometry was never measured; checks ran at two widths only | pictures `_heading_fits`; contract viewports |
| 3 | Words beside a picture had no minimum column; it shrank on wide screens | pictures CSS grid, `geometry()` |
| 4 | The critic's findings on the final (composed) page have no repair path | `main()` order; `drop_beat` on a non-beat |
| 5 | The creative bar does not gate delivery | scores.json vs. shipped page |
| 6 | No section form takes the product's pictures into a feature list | forms in `lib/compose/lists.py`, critic ART-02 |

## 4. Unverified hypotheses

- **[H]** A repair round after composition would raise taste rather than churn it (one reading moves ±4).
- **[H]** Supporting pages would let the homepage drop the archive without losing search standing — needs a real
  crawl comparison, which we cannot run in a preview.
- **[H]** The hero reads "conventional editorial SaaS" because the composer's concepts converge on stepped serif
  headlines; three recent jobs chose the same device. Three jobs are not a distribution.

## 5. Fixes — smallest effective, in order

Done on branches `round5`–`round7` (not deployed at the time of writing):

1. **Geometry is measured** — `lib/qa/layout.mjs`: every heading and paragraph at 390/768/1100/1440/1920 from the
   browser's line boxes: `stacked-words`, `split-word`, `lone-mark`, `thin-column`, `clipped`, `overlap`,
   `empty-frame`, `distorted-picture`, `link-dump`. No universal "three lines" rule: a heading is flagged when it
   runs about one word to a line over four or more lines (five or more words), which a deliberate four-word poster
   does not trip.
2. **A break cannot ship** — `run.py mend_layout` / `guard_layout`: a composed section with a break goes back to its
   pre-composition form; a heading that still does not fit is set smaller at the widths where it broke; what is
   left fails the technical track; `scripts/livetest.sh` fails on any break in any blueprint.
3. **Cause 3 at source** — words beside a `stage`/`bleed` picture keep ≥ 22.5rem; the picture gives way.
4. **Cause 1, presentation** — more than three source links, or a link whose name is a card of text, become one
   quiet row a reader opens ("More in this section · 11"); the SEO archive is one row ("More about us"). Words and
   links stay in the page; the SEO promises still hold. On Automateed rendered locally: `#more` 2493 px → 113 px,
   detector breaks 3 → 0.

Proposed, **not done — these are product decisions or larger than a patch**:

5. **Cause 1, properly — a content destination per source item** (`homepage`, `directory`, `supporting page`,
   `footer`). Today the product generates one page, so the only honest destinations are the page itself, a
   collapsed directory on it, and a link to the client's original page. Generating supporting pages is the real
   answer and is new product scope.
6. **Cause 4 — one repair pass after composition**, limited to operations the renderer can execute
   deterministically (re-choose a section's form, revert a section, resize a heading), then re-measure.
7. **Cause 5 — decide what happens under the creative bar**: ship with the score shown (today), or retry once with
   a different concept. Costs a second composition (~$0.7, ~4 min) on jobs that fall under it.
8. **Cause 6 — a list form that takes pictures** (feature rows beside the product's own screenshots), offered only
   when `images.json` has them.

## 6. Risks

- Collapsing preserved content behind a row changes what is visible without scrolling into it; search engines read
  `<details>` content, but its weight against always-visible text is not something we can measure here **[H]**.
- Auto-shrinking a heading cures the symptom; the form that left it no room is still wrong. Each shrink is recorded
  in `layout.json` so the forms that cause them can be counted and fixed.
- The detector reads text and whether a picture loaded. It does not judge a crop, an empty-looking section, or
  whether sections belong together.

## 7. Regression strategy

`npm test` + `scripts/livetest.sh 80 --all` (now including the layout gate) on every commit; composed runs on three
bench sites of different kinds with full-page screenshots at four widths read by a second agent; then production
jobs with `layout.json` read back. Results go in `SWARMSITE_VISUAL_QUALITY_VALIDATION.md`.
