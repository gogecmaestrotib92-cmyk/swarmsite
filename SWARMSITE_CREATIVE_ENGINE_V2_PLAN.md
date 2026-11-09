# Swarmsite — Creative Intelligence Engine V2: audit and plan

Audit of commit `9200ead` (main), 2026-11-09. No production code was changed to produce this document.
Companion: [SWARMSITE_PRODUCT_STRATEGY.md](SWARMSITE_PRODUCT_STRATEGY.md).

How to read the claims:

| Tag | Meaning |
|---|---|
| **[V]** | Verified by reading the code; `file:line` given |
| **[P]** | Measured on production: the 20 most recent finished jobs, read from `GET /jobs?status=done` and each job's artefacts on 2026-11-09 |
| **[X]** | Measured by a local, read-only experiment (Appendix A) |
| **[H]** | Hypothesis — not yet tested |
| **[R]** | Recommendation |

**Status on branch `engine-v2` (2026-11-09, after the owner said go):** measurement (separate scorecard, fingerprint, cost in dollars), the house-as-requirements flag, the benchmark tooling with 8 of 30 sites, five input checks in the renderer, and measured progress lines are built and committed. The first benchmark run changed the ranking of causes — read §1.6 before §2.

---

## 0. Summary

**The diagnosis in the brief is half right, and the larger cause is somewhere else.**

1. **Three decisions are merged in one model call — true.** The director chooses the business kind, the blueprint, the concept id and every beat in a single tool call (`lib/direct/direct.py:67-84`), and is told the blueprint's class must equal the kind (`direct.py:55`, enforced at `direct.py:96`). **[V]**
2. **But the recipes are no longer what constrains the page.** Since the house structures landed (2026-11-09), `lib/house.py` fixes the order of sections *and the visual move of each* per kind and is re-applied after the director and after the Concept agent (`house.py:79-109`, `direct.py:497`, `run.py:144,210`). The Concept agent is told its moves are ignored (`agents.py:207`). With the lock on, the 12 blueprints produce **4 distinct section sequences — one per kind**; with it off, the same 12 produce **12**. **[X]**
3. **Under that sits a closed vocabulary.** The renderer is one 1,800-line function with about 25 section templates and 10 hero templates. A model can pick a named variant and a few scalars (columns 1–4, band, heading size, photo layout). It cannot address position, overlap, asymmetry, crop, spacing or motion. The stylesheet is the same for every blueprint (≥ 99.97% similar) apart from the `:root` token block. **[V][X]**
4. **The creative concept never reaches the page.** The Concept agent's `idea` and `rhythm` are passed to three other prompts as 200-character guidance and are never read by the renderer (`agents.py:68-77`; `render_bp.py` reads `swarm` only at `:1325`). **[V]**
5. **Quality control cannot tell a weak idea from a weak execution, and does not stop a weak page.** The score is `0.55·taste + 0.45·contract` (`run.py:179`). On production the contract median is 97 and the taste median is 56; **0 of 20 jobs reached taste 70, and all 20 were delivered.** In 11 of 20 jobs the first round already had the best taste; the median gain from the repair rounds is 0. **[P]**

**What this means for the plan.** The business-structure layer and the reference layer are both worth keeping, but both currently do a job they were not meant to do: the house decides composition, and the references are reduced to token sets. The smallest change that tests the main cause costs about a day (make the house state requirements only, behind a flag, and measure). The Composition IR is the answer to cause 3, and should be built only as far as measurement justifies — hero first.

**Recommended order [R]:** measure first (benchmark, separate scores) → unlock the house (ablation) → reference-grounded direction with three concepts → Composition IR for the hero → full-page IR only if the hero result earns it. Each step is compared blind against the one before, on the same captured content.

---

## 1. Verified current architecture

### 1.1 Production execution path

One job, in order. All from `server/index.mjs` `process_` (`:317-446`) unless noted. **[V]**

| # | Stage | What runs | Writes |
|---|---|---|---|
| 1 | Capture | `node lib/pipeline/capture.mjs <url>` (`:332`) — desktop 1440×900 and mobile 390×844 passes | `inventory.json`, `assets.json`, `images.json` (≤28), `geometry.json`, `mobile.json`, `before-hero.jpg`, `before-full.jpg`, `before-mobile.png` |
| 2 | Diagnose | `python3 lib/audit/diagnose.py` (`:371`) — keyword heuristics, no model | `audit.json` (industry, 16 design findings, keep list) |
| – | Instant v0 | `lib/direct/quick.py` → `render_bp.py` (`:375-382`) — no model; kind → one fixed blueprint (`quick.py:15`) | `direction.json` (overwritten later), draft round 0 |
| 3a | Reader | `agents.reader` (`:395`, `agents.py:151`) — 1 model call | `factsheet.json` |
| 3b | Director | `lib/direct/direct.py` (`:396`) — 1–3 model calls | `direction.json` |
| 4a | First render | `render_bp.py` for up to two blueprints: the director's pick plus the next in `BP[kind]` (`:256, 399-403`) | `bp-<id>.html` |
| 4b | Swarm loop | `lib/swarm/run.py` (`:407`): Concept → UX, Visual, Copy, UI in parallel → render → up to 3 rounds of contract + critic → owners repair | `contract.json`, `critic.json`, `swarm.json`, `coverage.json` |
| 4c | Finalise | copy best round to `index.html`, re-render the alternative blueprint (`:417-421`) | `variant-<alt>.html` |
| 5 | QA | `lib/qa/check.py` (`:424`) — text only, stored in `result.qa` | – |
| 6 | Upload | Supabase bucket `previews`, served at `/p/:id` with `noindex` (`:127-143, 427-433`) | hosted preview |

Measured on production **[P]**: wall time 153–447 s (median 256 s); 12–22 model calls (median 19.5); 87k–344k input tokens (median 175k) and 14k–41k output tokens (median 26k) per job (n=14 jobs that recorded a budget).

### 1.2 The ten stages, one by one

**1. How the site is captured** — `lib/pipeline/capture.mjs`, `lib/audit/inventory.js`, `lib/audit/assets.js` **[V]**
- Works: text by section with ids, actions with real hrefs, forms, FAQ pairs, testimonials with attribution, SEO head, element-level visual shots, full-page desktop screenshot, refusal of bot-check pages.
- Reusable as is: all of it. This is the Brand Intelligence raw material.
- Limits: landing page only by default — `--site-wide` exists (`capture.mjs:140-230`) but the server never passes it. The mobile screenshot of the original is captured but shown to no model.
- Change: nothing in capture for V2. Pass `before-mobile.png` to the creative director.
- Leave untouched: section ids, action capture, FAQ/testimonial evidence records.

**2. How the business category is determined** — two places **[V]**
- `diagnose.py:11-19, 49-54`: keyword counts over 8 industries; used only for the instant v0 (`quick.py:16-17`).
- The real decision is the director's `kind` field, an enum of four: `place | service | product | software` (`direct.py:74`). The owner can state it in the brief (`direct.py:120`).
- Limits: four kinds. A restaurant and a hotel are both `place`; an architecture studio and a law firm are both `service`. There is no subtype.
- Change: keep the four kinds as the requirement tables; add a free `subtype` for retrieval and benchmarking.

**3. How structural rules are applied** — `lib/house.py` **[V]**
- `HOUSE` (`:12-55`): per kind, an ordered list of slots — id, beat type, **move**, what fills it, whether it may be composed from facts.
- `violations()` (`:112-130`): rejects any beat type the kind has no slot for, and more beats of a type than slots. A software page cannot have a `steps`, `quote`, `facts` or `ledger` beat.
- `lock()` (`:79-109`): sorts beats into the house order and writes each slot's move into `ui.move`.
- Called after the director (`direct.py:497`), after Concept in round 0 (`run.py:144`), after a restart (`run.py:210`) and on the instant v0 (`quick.py:140`).
- The stated intent, in the module docstring: "two runs of one site differ in copy and pictures, never in architecture" (`house.py:6-7`).
- Works: the *content* knowledge is good and evidence-based (what a restaurant page must carry, that a booking is the provider's link and never a custom form, that software pricing is not a homepage section).
- Limits: it also decides order and visual form. This is the line the brief asks not to cross.
- Change: split it. Requirements stay; order becomes a recommendation; moves leave the file.

**4. How recipes are selected** **[V]**
- The director sees one line per blueprint: id, class, archetype, mode, display font/size/weight, section count, "imagery heavy/light", 90 characters of a motion note (`direct.py:461-463`). No screenshot, no measured geometry.
- It must pick one whose class equals the kind (`direct.py:55, 96`).
- In production **[P]**: 4 of the 12 were used in the last 20 jobs — deepbook 13, butter 3, tengile 3, cerebrium 1.

**5. How creative direction is generated** **[V]**
- Director (`direct.py:41-58`): the system prompt is mostly content rules. Creative fields it writes: `concept` (C1–C8), `mode`, `voice`, brand hexes.
- Concept agent (`agents.py:181-250`): writes one `idea` sentence, a `hero_move` from four values, per-beat moves from seven values, and a `rhythm` sentence. Under the house it is told "beat moves you return are ignored" (`:207`).
- What reaches the page: `hero_move` (gated — `editorial-type` only for services, `billboard` only with a photo, `agents.py:226-237`), and the concept id as a decoration class (`render_bp.py:1899-1902`; C3 and C5 have no rules at all).
- One concept is produced, not three. Nothing evaluates it before it is built.

**6. How components are selected** — `render_bp.py:1522-1542` `component_for` **[V]**
- Order of authority: `ui.move` if the content qualifies → the recipe slot's component → `FALLBACK` by beat type (`recipes.py:135`).
- Because the house writes `ui.move` on most beats, the recipe slot is usually overridden.
- Then content guards re-select: 28 separate reroutes were counted, e.g. pinned-sequence → cards unless at least half the features have their own picture (`:710-712`), cards → index list when there are no pictures (`:1254-1256`), `wide` photo → `split` under 1100 px (`:779`).

**7. How the renderer works** — `lib/render/render_bp.py` **[V]**
- `build()` is one function from `:119` to `:1941`; every section renderer is a nested closure sharing image-allocation state.
- Each section is one f-string that emits a whole `<section>`.
- One shared stylesheet (`:1664-1870`), main breakpoints at 900 and 600 px (a few rules at 820, 800, 700 and 320); blueprints differ only in `:root` values and a few inline measures.
- Blueprint sections are not laid out as measured: they are bucketed into four pools by role prefix and handed out round-robin (`:1477-1493`). Fields never read: `archetype`, `grid.col`, `media.aspects`, section `pad/cols/note`, `media.xf`.
- Motion is assigned by CSS selector, never by the direction (`:1912-1929`); 11 of the 22 moves in `lib/motion/moves.js` are never used.
- Works, and is valuable: deterministic, escapes all text (`:15`), only links to captured URLs (`:333-352`), refuses upscaled and duplicate images, fits headlines to their longest word (`:106-117`), 134 test files.
- `lib/render/render.py`, `render_beats.py`, `build.py`, `lib/css/components.css`, `lib/css/tokens.py`, `lib/typography/typeselect.py` have no production callers.

**8. How visual QA operates** **[V]**
- Contract (`lib/qa/contract.mjs`): 20 promise ids at 1440 and 390 — h1 words/lines/size, first-screen visual, no upscaled or duplicate images, no empty screens, no overflow, actionable CTA, one CTA, short h2, page length, section count, sticky/pinned frames, contrast, and four SEO-safe checks.
- Critic (`lib/qa/critic.py`): one model call on screenshots of the generated page — 8 desktop frames in intermediate rounds, up to 20 across both viewports in the last (`:112`). Four axes: design 35, originality 20, craft 25, function 20.
- Calibration is three sentences of prose about Butter, Cerebrium and Tengile (`critic.py:27-31`). No reference image, no screenshot of the original site, and no statement of the concept are given to the critic.
- Screenshots are taken with motion frozen (`shots.mjs`: `?nomotion=1`, transforms forced off), so motion is never seen.
- Not checked anywhere: accessibility beyond contrast, page weight or load performance, runtime errors, whether links resolve.

**9. How repair instructions are applied** — `run.py:160-231` **[V]**
- The critic emits up to 10 fixes from nine bounded ops (`critic.py:22`); each is routed to an owner (`run.py:65-79`), and contract failures are added as notes (`:181`).
- Owners can only change what their tool allows (§1.4).
- A restart happens once, only if round 1 scores under 45 (`:199`).
- The loop stops when score ≥ target and taste ≥ 70 and nothing is broken, or rounds run out, or a round brought no gain (`:197, 214-217`). The best round by blended score is delivered whatever its taste.

**10. How the final site is delivered** **[V]**
- One self-contained HTML file with images inlined as base64; 0.1–1.8 MB in production **[P]**.
- Hosted preview at `/p/:id`, an alternative blueprint variant, a draft while running, an optional email.
- There is no export or download endpoint, no accounts, no payment.

### 1.3 How the 12 recipes are used today

`lib/templates/recipes.py` defines, per blueprint id: a hero move, a closing, and 6–9 slots (`accepts` beat types → component, optional variant and band). **[V]**

What still reaches the page:

| From the recipe / blueprint | Reaches the page? |
|---|---|
| Type scale, grid frame/gutter/container, radius, button metrics, easing (`*.bp.json`) | Yes — as `:root` tokens |
| Display/body/label font family | Mapped to a free face (`render_bp.py:18-44`); 12 blueprints → 9 display faces |
| Default hero move (`recipes.py` `hero`) | Yes, unless a verified software screenshot forces `split` (`render_bp.py:525-526`) |
| Closing (`cta` / `cta-photo`) | Yes |
| Slot component | Only for beats the house gives no move — in practice rarely |
| Slot variant / band | Partly: card variants `photos` and `contained` are never read; `giant` slots never fill |
| `photo-pair`, `collage`, `overlay`, photo `marquee` | **Never** — every photo beat returns `photo` or `story` at `render_bp.py:1527` |
| Measured section geometry (heading x/y/width, media aspect/width/offset) | Heading size and line-height only; the statement x-offset when `x > 0.3` |

So today the 12 recipes act as **12 token sets and a default hero**, laid over 4 house structures. Much of what made each recipe a distinct composition — Tengile's offset photo pairs and collage, White Desert's overlay itinerary, Belgrade Arbor's chapter photos — is defined in `recipes.py` and cannot be reached.

Evidence **[X]** (same sample content through every blueprint; Appendix A):

| Kind | Blueprints | Section sequences with the house lock | Section sequences with the recipe alone |
|---|---|---|---|
| software | 3 | 1 | 3 |
| place | 4 | 1 | 4 |
| service | 3 | 1 | 3 |
| product | 2 | 1 | 2 |
| **total** | **12** | **4** | **12** |

Stylesheet outside the `:root` block: 54.78 KB in every blueprint, pairwise similarity ≥ 0.9997.

On production, after the lock landed, two different software sites came out with the same skeleton **[P]**:
- pdfbeautifier.com: `hero.split | art-photo-split | cards | numbers | faq | cta`
- simscore.ai: `hero.centre | art-photo-wide | cards | cards.compact | faq | cta`

### 1.4 Everything a model can decide about composition today

The complete list. **[V]**

| Who | Field | Values |
|---|---|---|
| Director | `kind`, `blueprint`, `concept`, `mode`, `voice` | 4 · 12 (class-locked) · 8 · 2 · 2 |
| Director | beat types | 9, limited per kind by the house |
| Concept | `hero_move` | default, split, billboard, editorial-type (gated) |
| Concept | per-beat `move` | 6 named + auto — overwritten by the house in round 0 |
| UX | beat order | ignored under the house (`agents.py:274`) |
| UI | `cols` | 1–4, cards and ledger cards only, overridden by count rules |
| UI | `band` | paper, dark, alt |
| UI | `h2_px` | 28–96 |
| UI | `head` | left, center, split |
| UI | `photo_layout` | split, stacked, wide, gallery |
| UI | `compact`, `lead` | boolean; an image id |
| UI | hero `size`, `align` | S/M/L; start/center (ignored by four hero variants) |
| Visual | which image where, up to 6 crops | image ids; crop boxes |

Not addressable by any model: element position, overlap, asymmetry, grid tracks, spacing, per-section type, image aspect or focal point, layering, motion.

### 1.5 What production output looks like

The 20 most recent finished jobs, 2026-11-08 16:55 to 2026-11-09 19:03. **[P]**

| Measure | Min | Median | Max |
|---|---|---|---|
| Taste (critic) | 38 | 56 | 62 |
| — design | 40 | 58 | 66 |
| — **originality** | 32 | **45** | 55 |
| — craft | 40 | 54.5 | 58 |
| — function | 42 | 62 | 72 |
| Contract | 77 | 97 | 100 |
| Blended score shown to the loop | 56 | 73.5 | 77 |

- Taste ≥ 70 (the loop's own "a good studio would ship after a day of polish"): **0 of 20**.
- All 20 were delivered.
- Round 1 already had the best taste in 11 of 20; the last round tasted worse than the first in 8 of 20; median gain 0, best gain 8.
- 26% of all sections are a cards grid; 7 of 20 pages contain any pinned, sticky, type-wall or marquee move.
- The critic's own recurring sentence: "below the hero it falls apart into a template" (pdfbeautifier, Bálamo).
- The sample is narrow: 8 distinct sites — 6 software, 2 restaurants, no service or product site. All 20 predate commit `9200ead`, so the newest renderer changes have no production evidence yet.

The critic's scale is uncalibrated against people, so the absolute numbers mean little. The pattern — high contract, low originality, repairs that do not move taste — is the finding.

### 1.6 First benchmark run: the lock on real content

Added after the plan was accepted. Three variants of the same eight frozen production directions, through today's renderer, no model call (`bench/run.py`). **[X]**

| Variant | Contract median | Sections | Ledger + index list + cards | Distinct forms | Mean similarity between pages |
|---|---|---|---|---|---|
| `shipped` — the direction as the job left it | 92 | 62 | 61% | 11 | 0.25 |
| `house` — the lock applied | 92 | 62 | 60% | 10 | 0.27 |
| `recipe` — lock off, moves cleared, the recipe's slots decide | 92 | 62 | 63% | 11 | 0.31 |

- **With the lock on or off, real pages are built from the same few forms in nearly the same share.** Three forms are six sections in ten in every variant.
- The 12 → 4 collapse in §1.3 is real, but it was measured on identical sample content. Across real sites the content differs, and that difference — not the lock — is what separates one page from the next. Taking the lock off adds almost no variety.
- Together with the production before/after in §2, this moves the weight: **the closed vocabulary (cause 2) is the first cause, for sameness and for the taste ceiling. The lock (cause 1) matters for variation between blueprints on the same content, and little else.**
- Limits: the variants only re-render. A real run with `SWARM_HOUSE=requirements` would also let the director use other beat types and the Concept choose moves; that needs model calls and has not been run. Eight sites.

A second finding from the same run — **the contract reports the SEO-safe promise as broken on three of four jobs, and the report is wrong.** The four jobs made in SEO-safe mode: **[P]**

| Site | Reported by the contract | What it is |
|---|---|---|
| automateed.com | 97% of words, 29 / 29 links | Correct |
| pdfbeautifier.com | 22 / 24 links | The two "lost" links are anchors on the source page itself (`/#templates`, `/#faq`). Nothing lost. |
| courtsensei.com | 17 / 24 links | Six are same-page anchors (`/#features`, `/#how`, …). The seventh is on the new page six times, written `&amp;` in the HTML, which the contract compares without decoding. Nothing lost. |
| balamorestaurante.es | 7 / 8 links, **51% of words** | The link is the skip link `#content`. The 34 "lost" words are the cookie banner's (`aceptar`, `configurar`, `ajustes`, …): capture stores the whole body text, banner included, as the page's copy. Nothing lost. |

- No real loss of links or words was found in any of the four.
- The renderer and the contract disagree on what an internal link is: the renderer's list (`lib/seo.py:44-69`) leaves same-page anchors out, the contract (`lib/qa/contract.mjs:243-245`) counts them and does not decode entities.
- The capture (`lib/audit/inventory.js:60`) takes `document.body.innerText` as the copy, so consent banners count as source words everywhere that text is used — the contract, the director's prompt, the audit's word counts.
- What stands from the first reading: one blended score absorbed these failures without anyone looking, true or false. The scorecard now names them, which is how these were found.
- Fixes: decode and drop same-page anchors in the contract; keep consent text apart in the capture. Until the corrected contract has run on more sites, "keep my SEO" is measured and reported, not guaranteed.

---

## 2. Root-cause analysis

Ranked by how much of the observed sameness each was expected to explain when the plan was written. **Revised by §1.6: for real sites read cause 2 first and cause 1 second.**

### Cause 1 — Composition is decided by a table, before and after any creative thinking

- `kind` → house → fixed order and fixed move per slot (`house.py:12-55, 79-109`). **[V]**
- The lock runs after the two agents that could have chosen otherwise, and the prompts tell them so (`agents.py:207, 274`). **[V]**
- Effect: 12 → 4 distinct section sequences. **[X]**
- This is recent (REFACTOR.md, 2026-11-09, "House structures"). It was introduced to cut run-to-run variance, and it did — by removing the variation.

**This confirms the brief's concern, with a correction:** the collapse is not "SaaS → SaaS recipe → fill its slots". It is "SaaS → the software house → the same five moves, whichever recipe was chosen".

**What the lock does not explain: the taste score.** The 20 production jobs straddle the day the lock landed, which gives a rough before/after. **[P]**

| | Jobs | Sites | Taste median (min–max) | Originality median | Contract median | Sections per page |
|---|---|---|---|---|---|---|
| Before the lock | 13 | 7 | 56 (38–62) | 45 | 100 | 11.2 |
| After the lock | 7 | 4 | 56 (52–58) | 45 | 95 | 8.0 |

Same site before → after: Bálamo 58 → 58; courtsensei 62 → 58; pdfbeautifier 38–52 → 52–58.

The critic rated the freer, pre-lock pages no higher. The comparison is confounded — moods, the world layer and other changes landed in the same days, the critic is uncalibrated, and the sample is small — but it sets the expectation: **removing the lock restores variety between pages; on its own it is unlikely to make any one page better.** That points at cause 2 as the ceiling on quality, and it is why the house flag (S2) is kept cheap and the hero composition (S4) is not made to wait for it.

### Cause 2 — The composition vocabulary is closed

- About 25 section templates and 10 hero templates, each a fixed internal geometry (`render_bp.py:475-1473`). **[V]**
- No model-written field reaches position, overlap, spacing, crop or motion (§1.4). **[V]**
- One stylesheet for every page. **[X]**
- Even with cause 1 removed, the ceiling is "one of N templates per beat type". Removing the lock restores variety between recipes; it does not make an original composition possible.

### Cause 3 — The concept is text that nothing renders

- `swarm.idea` and `swarm.rhythm` are never read by the renderer. **[V]**
- One concept per job, not compared with any alternative, not checked against the result.
- The critic is not told what the concept was, so it cannot say whether the page fulfils it.

### Cause 4 — Reference knowledge is thin at the moment of decision

- The director sees one text line per blueprint (`direct.py:463`). **[V]**
- The critic's calibration is three prose sentences. **[V]**
- The underlying evidence is thinner than the catalogue suggests (§5.3): no mobile measurements for any of the 12, screenshots of the originals for only 3, motion recorded only as CSS strings, one of the 12 (`atelier`) authored as a copy of `lpas` with no measurement at all. **[V]**

### Cause 5 — QA cannot route by failure type and has no creative gate

- One blended number (`run.py:179`); the best round ships regardless of taste (`run.py:184-197`). **[V]**
- The only response to a weak idea is the single restart under 45 (`run.py:199`). On production it almost never fires: first-round blended scores were 56–77. **[P]**
- Repairs are bounded to the same vocabulary as cause 2, so they cannot fix "falls apart into a template". Median taste gain: 0. **[P]**

### Not the cause

- **Capture and content grounding.** FAQ and testimonial grounding (`direct.py:147-438`), link preservation and the coverage report are careful and work. Contract median 97.
- **The contract.** It measures what it promises. The problem is what is done with its score.
- **Prompt wording alone.** Better prompts cannot widen an enum.

### Inconsistencies found on the way

Small, verified, worth fixing regardless of V2.

| # | Finding | Where |
|---|---|---|
| 1 | The director's system prompt prescribes for software "features → steps → cells → ledger for pricing", but the house rejects `steps` and `ledger` for software. The model is given two contradictory structures and up to three retries to reconcile them. | `direct.py:50` vs `house.py:15-21, 123` |
| 2 | REFACTOR.md says the lock is re-applied "after every agent pass". It is called twice: after Concept in round 0 and after a restart. Concept's moves in repair rounds do stick, while its prompt says they are ignored. | `run.py:144, 210`; `agents.py:207, 238-248` |
| 3 | `nav.links` hrefs are escaped but not scheme-filtered, so a `javascript:` URL written by the director would be emitted. The UX agent's replacement is validated; the director's original is not. | `render_bp.py:1649`; `agents.py:286` |
| 4 | `brand.paper` / `brand.ink` from the director are interpolated into `<style>` with no hex validation. | `render_bp.py:298 → 1665` |
| 5 | Body font falls back to Inter Tight on 3 blueprints (aino, deepbook, halfdays), against the stated "no Inter-likes". | `render_bp.py:263` |
| 6 | The renderer needs Python ≥ 3.12 (backslash in an f-string expression). The system `python3` on this machine is 3.9.6, so `scripts/livetest.sh` fails locally unless 3.12 is first on the path. Production (Ubuntu noble) is fine. | `render_bp.py:1390` |
| 7 | `scripts/livetest.sh` renders 6 blueprints unless a second argument `--all` is given; AGENTS.md describes it as every blueprint. | `scripts/livetest.sh:8` |
| 8 | Three progress events are canned strings, not measurements ("type scale set · h1 clamp(52px, 7.4vw, 124px)", "ending + contact written", "lenis on"). | `server/index.mjs:250` |
| 9 | `moods.LIBRARY` holds 41 moods; the log says 42. | `lib/moods.py` |
| 10 | The world-layer default concept is C5, the palette default is C1, and `quick.py` hardcodes C2. | `render_bp.py:297, 1899`; `quick.py:135` |

Items 3 and 4 matter because source text is untrusted input to the director. Both are a few lines to close.

---

## 3. Proposed architecture

### 3.1 Principle

**Content is constrained. Composition is creative. Quality is verified.** In engineering terms:

- Content enters the composition **by reference only**. A composition can place a content unit; it cannot contain a sentence.
- Composition is a document the model writes and a validator accepts or rejects. It is not code.
- Nothing is called good until it has been rendered in a browser, measured, and looked at — by the critic for routing, by people for the verdict.

### 3.2 The six layers, mapped onto what exists

```
URL
 │
 ▼  capture.mjs · diagnose.py · agents.reader            (exists)
┌─────────────────────────────────────────────────────────────────────┐
│ 1 BRAND INTELLIGENCE      brand_intelligence.json                   │
│   assemble + add evidence refs to facts            new: assembler   │
└─────────────────────────────────────────────────────────────────────┘
 ▼  house.py requirements · direct.py content plan · seo.py   (exists, split)
┌─────────────────────────────────────────────────────────────────────┐
│ 2 STRUCTURAL INTELLIGENCE content_contract.json                     │
│   what must exist, with sources; no order lock, no moves            │
└─────────────────────────────────────────────────────────────────────┘
 ▼  lib/blueprints · raw · dna · docs                         (exists, restructured)
┌─────────────────────────────────────────────────────────────────────┐
│ 3 DESIGN DNA              design_dna/references/{id}.json           │
│   measured principles + evidence + what is missing; retrieval       │
└─────────────────────────────────────────────────────────────────────┘
 ▼  replaces: blueprint pick in direct.py, agents.concept
┌─────────────────────────────────────────────────────────────────────┐
│ 4 CREATIVE DIRECTION      creative_direction.json                   │
│   three concepts → hero bake-off → one selected                     │
└─────────────────────────────────────────────────────────────────────┘
 ▼  replaces: agents.ux order, agents.ui layout, house moves
┌─────────────────────────────────────────────────────────────────────┐
│ 5 COMPOSITION             composition.json  (Composition IR)        │
│   validate → render (new IR renderer + existing section components) │
└─────────────────────────────────────────────────────────────────────┘
 ▼  contract.mjs · critic.py · shots.mjs                      (exists, split)
┌─────────────────────────────────────────────────────────────────────┐
│ 6 QA                      qa_report.json                            │
│   technical gate ∥ creative gate · failure type A/B/C · routing     │
└─────────────────────────────────────────────────────────────────────┘
 ▼
 release experimental page — or fall back to the production page, which always exists
```

Layers are responsibilities, not agents. Model calls in the experimental path: reader (exists), content plan (the director, relieved of form), three concepts (1 call), hero compositions (1–3 calls), concept jury (1 call, on screenshots), page composition (1 call), critic (exists), revisions (0–2 calls). Concept, UX-order and UI-layout calls disappear from this path because the composition document subsumes them.

### 3.3 The smallest changes, in order of cost

| # | Change | Size | Tests which cause |
|---|---|---|---|
| S1 | Store taste and contract separately in the job result; add the structural fingerprint; build the blind pairwise comparison page — **built** | small, no engine change | — (measurement) |
| S2 | `SWARM_HOUSE=requirements` flag: the house states requirements and rejects no beat type, `lock()` no longer writes moves or order; Concept's moves are honoured; recipe slots live again — **built; render-only comparison in §1.6; a run with model calls is still to do** | small, flag default off | Cause 1 |
| S3 | Reference-grounded direction: Design DNA records + retrieval; three concepts; critic receives the concept, the original screenshot and separate scores with a failure type | medium | Causes 3, 4, 5 |
| S4 | Composition IR for the hero only, transplanted into the production page | medium | Cause 2, cheaply |
| S5 | Full-page IR; section components called as IR nodes | large; requires hoisting the renderer's closures | Cause 2, fully |

Each step is measured against the previous one on the same captured artefacts. **Stop climbing when a step does not earn its cost.** If S2 alone moves blind preference a lot, S5 becomes less urgent. If S2 moves nothing, the vocabulary is the ceiling and S4 is the next test.

### 3.4 What must not change

- The production path, until the comparison in §10 says otherwise. Every new behaviour is behind a flag that defaults off, as `SWARM_VERIFIED_PATTERNS` already is (`run.py:91`).
- The 12 recipes and their components. In V2 they become (a) the fallback engine, (b) the source of the Design DNA records, (c) callable components inside the IR.
- The house's content knowledge.
- Deterministic rendering, content grounding, the contract, the coverage report, the SEO-safe mode.

---

## 4. Reuse, modify, add

### 4.1 Reuse as is

| Component | Role in V2 |
|---|---|
| `lib/pipeline/capture.mjs`, `lib/audit/*` | Layer 1 raw material |
| `agents.reader` + `factsheet.json` | Layer 1 interpretation (schema extended, §4.2) |
| `direct.ground_faq`, `direct.ground_testimonials` | Layer 2 evidence rules — the model for every other fact |
| `lib/seo.py`, `lib/swarm/coverage_report.py` | Preservation mode and the coverage audit |
| `lib/qa/contract.mjs`, `lib/qa/shots.mjs` | Technical QA and screenshots |
| `lib/budget.py` | Per-job caps and the token record |
| `lib/moods.py`, `lib/colour_policy.py`, `lib/colour/palette.py` | Colour tokens and contrast repair for the IR |
| `lib/motion/moves.js` | The motion vocabulary the IR may name (22 moves, 11 currently unused) |
| `render_bp.py` section components | Called as IR `component` nodes (ledger, FAQ, testimonials, form, footer, SEO archive, nav) |
| `render_bp.py` helpers: `e`, `safe_url`, `action_url`, `fit_headings`, `source_alt`, image guards | Safety layer of the IR renderer |
| `lib/swarm/pattern_stage.py` + `experiments/design-patterns` | The pattern for an isolated, verified, opt-in stage |
| `server/index.mjs` job, lease, draft and variant machinery | Unchanged; the variant slot can carry the experimental page next to the production one |
| 134 test files, `scripts/livetest.sh` | Regression net for any renderer refactor |

### 4.2 Modify (behind flags; production default unchanged)

| Component | Modification |
|---|---|
| `lib/house.py` | Add `need` (required / recommended / optional) per slot. Add `requirements(kind)` returning slots without order or move. `lock()` gains a mode that neither sorts nor writes moves. |
| `lib/direct/direct.py` | Experimental mode: no blueprint choice, no house order; output is the content plan only. Remove the contradiction in §2 item 1 in both modes. |
| `agents.READER_TOOL` | Facts become `{text, source_section}`; a deterministic check marks each fact verbatim / normalised / unverified against captured text. |
| `lib/qa/critic.py` | Separate creative axes; receives the original screenshot, the selected concept and reference thumbnails; returns `failure_type` and per-section concept fidelity. |
| `lib/swarm/run.py` | No blended score in the experimental path; two gates; routing by failure type. |
| `server/index.mjs` | Persist taste and contract separately; honest progress events (remove the canned strings); record wall time per stage and cost per job. |
| `render_bp.py` | Later, and only after S4 shows value: hoist section closures out of `build()` so the IR renderer can call them. Behaviour-preserving, guarded by the existing tests. Independently: close items 3 and 4 of §2. |

### 4.3 New modules

| Module | Purpose | Model calls |
|---|---|---|
| `lib/intel/brand.py` | Assemble `brand_intelligence.json` from capture, audit and factsheet; verify fact evidence | 0 |
| `lib/structure/contract.py` | Build and validate `content_contract.json` | 0 |
| `design_dna/` — `references/*.json`, `schema.json`, `fonts.json`, `seeds/*.json`, `retrieve.py` | The reference library, its validator, and retrieval | 0 at run time |
| `lib/creative/director.py` | Three concepts; distinctness check; jury | 2 |
| `lib/compose/` — `schema.json`, `validate.py`, `render_ir.py`, `ir.css`, `compose.py` | Composition IR: schema, static validator, deterministic renderer, the composing call | 1–3 |
| `lib/qa/fingerprint.py` | Structural fingerprint and template-similarity score | 0 |
| `bench/` — site list, frozen artefacts, runner, blind pairwise page, results | The benchmark | 0 |

---

## 5. Data contracts between stages

Every file carries `schema_version` and the sha256 of each input it was built from, the way `run.py:30-38` already fingerprints render inputs. A stage refuses to run on a stale input.

### 5.1 `brand_intelligence.json` — written by `lib/intel/brand.py`

```jsonc
{
  "source": {"url": "…", "captured_at": "…", "scope": "landing_page_only", "pages": 1},
  "business": {"what": "…", "audience": "…", "value": "…", "kind": "place", "subtype": "restaurant",
               "kind_source": "director|owner|heuristic"},
  "brand": {"name": "…", "voice": ["…"], "palette": {"accent": "#…", "from": "buttons|logo"},
            "fonts": {"display": "…", "body": "…"}, "logo": "assets:logo"},
  "goals": [{"action": "a1", "label": "…", "href": "…", "kind": "booking"}],
  "facts": [{"id": "f7", "text": "…", "source": {"section": "home-3", "url": "…"},
             "verified": "verbatim|normalised|unverified"}],
  "assets": {"photos": 9, "screenshots": 2, "video": false, "hero_grade": ["img-3", "img-7"],
             "quality_note": "…"},
  "weaknesses": [{"code": "small_h1", "severity": "med", "evidence": "…"}],   // from audit.json
  "missing": ["opening hours not stated on the captured page"],
  "evidence": {"screenshots": {"desktop": "before-full.jpg", "mobile": "before-mobile.png"}}
}
```

Invariants: every fact has a source or is marked `unverified`; `unverified` facts may not be placed on the page; `missing` is never filled by a model.

### 5.2 `content_contract.json` — written by `lib/structure/contract.py`

```jsonc
{
  "category": {"kind": "place", "subtype": "restaurant"},
  "units": [
    {"id": "unit:offer", "what": "the menu", "need": "required", "status": "present",
     "sources": ["home-4"], "items": 14, "preserve": "verbatim", "payload_ref": "direction:beats[1]"},
    {"id": "unit:hours", "what": "opening hours", "need": "required", "status": "missing", "sources": []}
  ],
  "actions": [{"id": "a1", "label": "Reserve", "href": "https://…", "kind": "booking",
               "source": "home-nav", "must_keep": true}],
  "journeys": [{"goal": "book a table", "uses": ["a1"], "must_work": true}],
  "hierarchy": {"recommended_order": ["unit:story", "unit:offer", "unit:whats-on"],
                "status": "recommendation"},
  "preservation": {"mode": "seo-safe", "text_share_min": 0.95, "h1_keywords_min": 0.5, "links": "all"},
  "missing": [{"unit": "unit:hours", "note": "not found; shown to the owner, not invented"}]
}
```

Invariants: no `move`, no layout field, no order lock. `need` comes from the house tables. `status: missing` on a required unit is reported to the owner and never composed.

**Preservation is the user's choice (owner decision, 2026-11-09).** The choice already exists: the brief asks "keep my SEO" (default) or "redesign freely" (`web/app.html:84-85`), stored as `brief.mode` and read by `lib/seo.py:11-13`. **[V]** V2 honours it in every layer:

| | SEO-safe — "keep my SEO" (default) | Free — "redesign freely" |
|---|---|---|
| Body text | Kept: ≥ 95% of the source's words on the page; facts never paraphrased; whatever is not placed goes to the archive section | May be rewritten; facts stay true |
| h1 | Keeps the source h1's keywords; a stance may be added | May change |
| Section headings | Keep their keywords; verbatim when ≤ 7 words | May change |
| Internal links, title, description, canonical, hreflang, Open Graph, structured data | All kept | Not promised |
| Order and grouping of sections | Free | Free |
| Visual composition, type, colour, motion | Free | Free |
| Inventing content | Never | Never |
| Measured by | `seo-text-kept`, `seo-h1-keywords`, `seo-links-kept`, `seo-meta` in the contract (`lib/qa/contract.mjs:224-251`) | Coverage report only |

Two consequences for V2:
- **Section order is not preserved in either mode today** — the house reorders in both (`house.lock` takes no mode). V2 keeps it that way: "keep my SEO" protects words, headings, links and meta, not the source's order.
- **SEO-safe is the harder creative case.** The headline's words are largely fixed, so a long source h1 cannot be cut to four words. The composition has to carry a long headline well. The benchmark is run in SEO-safe first, because it is what users get by default, and each engine comparison stays within one mode.

In the Composition IR this needs no special machinery: text enters only by reference, as real text in the page, so a composition cannot reword it. Free mode differs upstream — in what the content plan is allowed to write — not in the composition.

### 5.3 `design_dna/references/{id}.json`

```jsonc
{
  "id": "tengile", "status": "measured-desktop",          // measured-desktop | authored | incomplete
  "source": {"url": "…", "captured_at": null, "viewport": {"w": null, "h": 756}, "dpr": null},
  "evidence": {"blueprint": "lib/blueprints/tengile.bp.json", "raw": "lib/blueprints/raw/tengile.json",
               "screenshots": {"desktop": [], "mobile": []}, "scroll_capture": null},
  "completeness": {"typography": "measured", "composition": "measured-desktop", "imagery": "measured-desktop",
                   "motion": "prose-only", "experience": "prose-only", "mobile": "missing", "screenshots": "missing"},
  "typography": {"display": {"source_face": "PP Fragment", "licence": "commercial", "delivery_face": "Cormorant Garamond",
                             "px": 120, "weight": 220, "leading": null, "tracking": null}, "scale_ratio": 2.5},
  "composition": {"grid": {"frame": 0, "gutter": 0, "container": 0},
                  "sections": [{"role": "photo-pair", "screens": 1.2, "head": {"x": 0.52, "y": 0.4, "wf": 0.38},
                                "media": [{"ar": 0.8, "wf": 0.34, "xf": 0.08}, {"ar": 1.3, "wf": 0.42, "xf": 0.5}]}]},
  "imagery": {"aspects": [], "bleed_share": null, "video_hero": true},
  "motion": {"libs": [], "transitions": [], "note": {"text": "…", "kind": "prose"}},
  "experience": {"pacing_screens": [], "narrative": {"text": "…", "kind": "prose"}},
  "principles": [{"id": "offset-photo-pair", "statement": "…",
                  "evidence": ["composition.sections[2].media"], "derived_by": "human|model",
                  "confidence": "measured|observed|inferred"}],
  "fits": {"kinds": ["place"], "also": ["service"], "needs": {"photos_min": 6}, "temper": ["quiet", "editorial"]},
  "rights": {"screenshots": "research-only", "source_text": "excluded", "fonts": "commercial, mapped"},
  "implementation": {"recipe": "lib/templates/recipes.py#tengile", "ir_seeds": ["design_dna/seeds/tengile-hero.json"]}
}
```

(Numeric values above are illustrative of the shape, not copied from the file.)

What the 12 records can honestly contain today **[V]**:

| Dimension | State |
|---|---|
| Typography | Measured for 11: family, px, weight, tracking, leading per heading level. Source faces are mostly commercial; a mapped free face is what ships. |
| Composition | Measured for 11, desktop only: grid frame/gutter/container, section heights in screens, heading position and width as fractions, media aspect/width/offset. |
| Imagery | Measured for 11, desktop only. |
| Motion | CSS transition strings, keyframe names, library flags. Everything about scroll and pinning is hand-written prose. |
| Experience / narrative | Prose only. |
| Mobile | **Missing for all 12.** |
| Screenshots of the original | Only butter, cerebrium, deepbook (in `dna/`), with caveats: the deepbook DNA profile was captured from a different URL; cerebrium's DNA numbers disagree with its raw file. |
| Capture date, DPR | **Missing for all.** Viewport width recorded for 3 of 11. |
| `atelier` | No raw file. Identical to `lpas` except id, source and display family. Marked `authored`; kept as a recipe; not used as evidence. |

The separate `dna/` folder (16 profiles, 211 screenshots, a different set of sites) and `dna/house/*.md` (text-only evidence from web fetches) are further inputs. Rights to the third-party screenshots and source text are not established (`lib/blueprints/README.md`, `docs/blueprint-catalog-audit.md`); they are for internal analysis and must not ship in a product or an export.

Retrieval is deterministic: score `fits` against `brand_intelligence` (kind and subtype, photo count and quality, temper, light/dark preference), return the top 3–5 references, including from other kinds when a principle fits. With 12–100 references no embedding search is needed. The creative director receives their DNA cards, not the library.

### 5.4 `creative_direction.json` — written by `lib/creative/director.py`

```jsonc
{
  "concepts": [
    {"id": "A", "thesis": "…", "brand_reading": "…", "metaphor": "…",
     "typography": {"philosophy": "…", "display_class": "high-contrast serif", "scale": "extreme"},
     "composition": {"philosophy": "…", "grid": "asymmetric 5/7", "density": "sparse"},
     "imagery": {"strategy": "…", "treatment": "full-bleed, uncropped"},
     "motion": {"strategy": "…", "intensity": "quiet"},
     "narrative": [{"carries": ["unit:story"], "intent": "…", "loudness": "loud"}],
     "relevance": "…", "dna": [{"ref": "tengile", "principles": ["offset-photo-pair"]}], "risks": "…"}
    // B, C
  ],
  "distinctness": {"dimensions_differing": {"A-B": 4, "A-C": 5, "B-C": 3}, "hero_fingerprint_distance": {"A-B": 0.62}},
  "evaluation": {"method": "hero-bakeoff", "by": "model:<id>|human",
                 "scores": {"A": {"brand_fit": 0, "originality": 0, "visual_potential": 0,
                                  "content_fit": 0, "feasibility": 0, "usability": 0}},
                 "selected": "B", "why": "…"}
}
```

Rules:
- Three concepts must differ in at least 3 of 5 structured dimensions (type class, grid, imagery strategy, motion, narrative order). Checked in code, not by the author of the concepts.
- **Selection is made on rendered evidence.** Each concept gets a hero composition; the three heroes are rendered and screenshotted; a separate call (or the user) picks. A concept that cannot be composed fails here, cheaply.
- `narrative` assigns every required content unit to a section. A concept that drops one is rejected before anything is rendered.

### 5.5 `composition.json` — see §6

### 5.6 `qa_report.json` — see §7

---

## 6. Composition IR

### 6.1 Goals

1. The model describes geometry and behaviour; it never writes HTML, CSS or copy.
2. Same IR → same bytes.
3. Content cannot be invented or lost, by construction.
4. Responsive, accessible and safe by construction; whatever cannot be guaranteed statically is checked on the render.
5. Everything the current engine can do is expressible, so the IR is a superset and the 12 recipes compile into it.
6. When an idea cannot be expressed, the system says which primitive is missing. It does not quietly substitute.

### 6.2 Shape

```jsonc
{
  "ir": "0.1",
  "inputs": {"content_contract": "sha256:…", "creative_direction": "sha256:…", "concept": "B"},
  "tokens": { /* §6.3 */ },
  "page": {
    "nav":    {"t": "component", "name": "nav"},
    "sections": [ /* §6.4 */ ],
    "footer": {"t": "component", "name": "footer"}
  },
  "unsupported": [{"section": "s3", "intent": "photograph cut by a diagonal that follows the headline",
                   "missing": "mask: polygon"}]
}
```

### 6.3 Tokens

```jsonc
"tokens": {
  "type": {
    "display": {"family": "Fraunces", "weight": 300, "tracking": -0.035, "leading": 0.9, "case": "none"},
    "text":    {"family": "Geist", "weight": 400, "leading": 1.45},
    "label":   {"family": "Geist Mono", "case": "upper", "tracking": 0.08},
    "scale":   {"xs": 13, "sm": 15, "md": 17, "lg": 24, "xl": 40, "xxl": 72,
                "mega": {"vw": 17, "min": 56, "max": 260}}
  },
  "colour": {"paper": "#F3EEE4", "ink": "#15130F", "accent": "#C4411E", "alt": "#E4DCCB", "from": "brand|mood:<id>"},
  "space":  {"xs": 8, "sm": 16, "md": 32, "lg": 64, "xl": 120, "xxl": 200},
  "grid":   {"cols": 12, "gutter": 24, "margin": 40, "max": 1440},
  "shape":  {"radius": 0, "rule": 1},
  "motion": {"ease": "cubic-bezier(.2,.7,.1,1)", "tempo": "slow", "intensity": "still|quiet|expressive"}
}
```

- Families come from a registry (`design_dna/fonts.json`: family, source, licence, axes, fallback metrics), extending `lib/typography/fonts.json`. A family outside the registry is a validation error.
- Colours pass through `colour_policy.resolve`; a failing pair is an error, not a silent repair.

### 6.4 Sections and nodes

```jsonc
{
  "id": "s1", "role": "hero",                       // a label for people and QA, never a template key
  "carries": ["unit:hero"],                         // content units this section is accountable for
  "surface": "paper",                               // paper | ink | alt | accent | media
  "height": {"screens": 1},                         // "auto" | {"screens": n} | {"pin": n}
  "pad": ["lg", "md"],
  "frame": {"cols": 12, "rows": ["auto", "1fr", "auto"], "gap": "md", "bleed": "right"},
  "nodes": [
    {"t": "text", "id": "n1", "src": "hero.category", "as": "label", "at": {"col": [1, 5], "row": 1}},
    {"t": "media", "id": "n2", "src": "img:hero", "fit": "cover", "ratio": "4/5", "focal": [0.5, 0.35],
     "mask": "none", "treat": "none", "at": {"col": [7, 13], "row": [1, 4], "z": 1},
     "motion": {"type": "parallax", "amount": 0.1}},
    {"t": "text", "id": "n3", "src": "hero.h1", "as": "h1", "size": "mega", "measure": "9ch",
     "at": {"col": [1, 9], "row": 2, "z": 2}, "over": {"node": "n2", "plate": "paper"}},
    {"t": "text", "id": "n4", "src": "hero.lede", "as": "p", "size": "md", "measure": "38ch",
     "at": {"col": [1, 5], "row": 3}},
    {"t": "action", "id": "n5", "src": "hero.cta", "style": "solid", "at": {"col": [1, 4], "row": 3, "self": "end"}},
    {"t": "shape", "id": "n6", "kind": "rule", "tone": "line", "at": {"col": [1, 13], "row": 3, "self": "start"}}
  ],
  "sm": {"order": ["n1", "n3", "n2", "n4", "n5"], "overlap": false},
  "motion": {"enter": "mask-lines", "scroll": "none"},
  "join": "none"                                    // none | overlap-next | rule | colour-step
}
```

Node types:

| `t` | Purpose | Key fields |
|---|---|---|
| `text` | One content field | `src` (content path — required; no literal text), `as` (h1 / h2 / h3 / p / label / quote / figure), `size`, `measure`, `align`, `case`, `em` |
| `media` | Image or video | `src`, `fit`, `ratio`, `focal`, `mask` (none / round / arch / circle / inset), `treat` (none / mono / duotone / grain), `frame` (none / browser / device / paper) |
| `action` | A captured action | `src` → an action id in the content contract; `style` |
| `list` | Repeat over items of a unit | `src`, `layout` (rows / grid / rail / index / ladder), `cols` per breakpoint, `item`: node templates with `@.title`, `@.body`, `@.image` |
| `group` | Stack, row or overlay of nodes | `layout`, `gap`, `sticky` |
| `shape` | Decoration | `kind` (rule / block / disc / grid-lines), `tone`; always `aria-hidden` |
| `ordinal`, `wordmark` | The only generated text: a section or item number; the brand name | `size` |
| `component` | An existing section renderer | `name` (ledger / faq / testimonials / form / pinned-sequence / sticky-product / type-wall / marquee / story / cards / numbers / …), `unit`, `variant` |

Placement `at`: `col` and `row` as grid lines, `z` 0–4, `self`, `nudge` up to ±2 grid units. Overlap is two nodes whose areas intersect.

### 6.5 Responsive rules

- Three ranges, matching the existing stylesheet's main breakpoints: phone < 600, tablet 600–899, desktop ≥ 900.
- Desktop is authored. Tablet is derived (12 → 8 columns, placements scaled, overlaps kept only if they pass validation at that width).
- Phone is linear in `sm.order` (default: `nodes` order); every node is full width; overlap only where `sm` declares it for a named pair.
- `mega` and `xxl` sizes are always fitted to the longest word, reusing `fit_headings` (`render_bp.py:106-117`).

### 6.6 Accessibility and safety, by construction

- DOM order is `nodes` order, independent of visual placement.
- Exactly one `h1`; heading levels never skip.
- Images take their alt text from the source (`source_alt`, `render_bp.py:249`); decorative nodes are hidden from assistive technology.
- Actions render only as links to URLs in the content contract, through `safe_url` / `action_url`.
- All text through `html.escape`. No raw HTML, CSS or script can appear in an IR document; there is no field for it.
- `prefers-reduced-motion` removes all motion; the existing `?nomotion` path is reused for QA.

### 6.7 Validation

Static, before any render. Each failure has a code and is returned to the composing model once; a second failure falls back.

| Code | Check |
|---|---|
| IR001 | Schema |
| IR010 | Every `src` resolves in the content contract, images or assets |
| IR011 | No literal text outside `ordinal` and `wordmark` |
| IR020 | Coverage: every `required` unit that is `present` is carried by exactly one section; no unit twice |
| IR021 | Every `must_keep` action is placed at least once |
| IR030 | Placement inside the grid |
| IR031 | No two text nodes overlap |
| IR032 | Text over media has a `plate` or `scrim` |
| IR040 | Font family in the registry |
| IR041 | Size in the scale |
| IR050 | Contrast of every surface/ink pair in use |
| IR060 | Rendered image width at 1440 ≤ native width × 1.35 for photographs, ≤ native for screenshots (the renderer's existing limits) |
| IR070 | Motion from the vocabulary; at most one pinned section; pin length ≤ 4 screens |
| IR080 | Heading order |
| IR090 | Every overlay group has a phone rule |
| IR100 | `unsupported` non-empty → handled by policy below |

Rendered, in a browser at 1440 and 390: the existing contract (`lib/qa/contract.mjs`) plus new checks — text clipped or overlapping by measurement, tap targets, all `carries` units present in the rendered text, console errors, failed image loads, page weight.

### 6.8 When an idea cannot be expressed

- The composing call must list it in `unsupported`, with the intent and the primitive it would need.
- The engine never substitutes a different composition on its own. It either (a) asks once for the nearest expressible form and lets the critic judge whether the concept survives, or (b) falls back to the production page for the whole job.
- Every entry is appended to `design_dna/missing_primitives.jsonl`. That file is the engineering backlog for the vocabulary: primitives are added because real concepts asked for them, most-requested first.

### 6.9 How the model gets geometry right

Language models place things poorly when they cannot see the result. Three supports:

1. **Seeds from measured references.** The blueprints already hold heading position and width and media aspect, width and offset as fractions of the viewport (`agents.py:122-125` whitelists them). On a 12-column grid these translate directly into `at` placements. Each reference's hero and two or three signature sections are compiled once into IR seeds (`design_dna/seeds/`). The composing call sees the seeds of the retrieved references as worked examples — principles in the IR's own units, not layouts to copy.
2. **Render in the loop.** Compose → validate → render → screenshot → the model sees its own page and revises. Two iterations at most.
3. **The bake-off.** Three hero compositions are compared as pictures before a full page is composed.

### 6.10 Renderer

- `lib/compose/render_ir.py`: pure function, IR + content + images → HTML. CSS Grid with custom properties per node (`--c0`, `--c1`, `--r0`, `--z`), one small fixed stylesheet (`ir.css`) implementing the primitives, motion through the existing `data-sig` hooks in `moves.js`.
- **S4, hero only:** the production renderer builds the page as today; the experiment replaces the `<section class="sec hero …" id="top">…</section>` element with the IR hero and appends `ir.css`. No production file changes. Everything below the hero, the nav, the footer and the SEO archive are untouched.
- **S5, full page:** requires the section renderers to be callable from outside `build()`. They are nested closures today, so this is a behaviour-preserving refactor of `render_bp.py`, done only if S4 shows value, guarded by the existing tests and a byte-for-byte comparison of all 12 livetest renders before and after.
- **The recipes as IR.** Each recipe is expressible as an IR document made only of `component` nodes. That gives the fallback, and a regression test: recipe → IR → render must equal the current render.

---

## 7. Visual and technical QA

### 7.1 Two scores, two gates, never blended

| | Technical | Creative |
|---|---|---|
| Source | `contract.mjs` + new rendered checks; deterministic | Critic on screenshots; calibrated against people |
| Inputs | The rendered page at 1440 and 390 | Original site (desktop + mobile), the selected concept, thumbnails of the references the concept cites, the rendered page at both widths |
| Axes | Content preserved, links and actions, overflow, contrast, empty screens, images, accessibility, weight, runtime errors | Typography, composition, originality, brand fit, imagery treatment, rhythm, concept fidelity, template similarity |
| Hard failures | Missing required unit, broken `must_keep` action, overflow, text contrast, runtime error | — |
| Gate (initial proposal, to calibrate) **[H]** | score ≥ 90 and no hard failure | creative ≥ 70, originality ≥ 60, template similarity under threshold |

A page is released from the experimental path only if both gates pass. Otherwise the production page is delivered and the reason is recorded. A high technical score never offsets a weak creative one.

### 7.2 Three failure types, three responses

| Type | The critic's finding | Response | Budget |
|---|---|---|---|
| **A — weak concept** | The idea is generic or wrong for the brand; the render fulfils it and is still dull | Take the runner-up concept from the bake-off, or regenerate concepts with the verdict as a negative example | once |
| **B — good concept, weak execution** | Sections do not realise their stated intent (fidelity "partly" / "no") | Revise `composition.json` for the named sections only, with the screenshot | twice |
| **C — technical defect** | The contract or a rendered check failed | Deterministic fixers first (fit, clamp, contrast repair); then a bounded IR patch on the offending node | twice |

Concept fidelity is asked per section: given the section's `intent` from the creative direction and its screenshot — realised, partly, or not. That is what separates A from B, and it is only possible because the concept is now a document the critic is given.

### 7.3 Template similarity, measured without a model

`lib/qa/fingerprint.py`: for each rendered page, the ordered list of section signatures (the method of Appendix A) plus, for IR sections, a hash of the grid placements. Compared against (a) the 12 recipe renders of the same content and (b) every previous output. Reported as a similarity score. This is the direct measure of "does it look like the same template again", and it costs nothing per job.

### 7.4 Motion

Stills cannot judge motion, and the screenshots are deliberately frozen. For sections with a `scroll` behaviour, capture a filmstrip of 3–5 frames at fixed scroll positions with motion on, and give the strip to the critic. Until that exists, motion coherence is reported as "not evaluated", not scored.

### 7.5 Calibrating the critic against people

- Every benchmark comparison is also judged blind by people (§10).
- Agreement = share of pairs where the critic's preference matches the human majority, among pairs where people agree with each other.
- The critic may gate on its own only once agreement is ≥ 75% **[H]**. Until then it routes repairs, and people give the verdict on benchmark runs.
- No page is described as studio-quality on the strength of a model's score.

---

## 8. Migration strategy

| Phase | Deliverable | Production impact | Exit |
|---|---|---|---|
| 1 Audit | This document | none | accepted by the owner |
| 1b Measurement | Benchmark set frozen; baseline E0 recorded; separate scores stored; fingerprint; blind comparison page | additive fields in `jobs.result` | 30 sites with artefacts and E0 output |
| 1c Ablation | `SWARM_HOUSE=requirements`, default off | none | E1 vs E0 measured |
| 2 Design DNA | 12 records with honest completeness; 5+ references recaptured at 1440 and 390 with screenshots; validator; retrieval | none | all records validate; no field without evidence or `missing` |
| 3 Content contract | `content_contract.json` from existing artefacts | none | 10 sites: every required unit present-with-sources or missing; zero invented |
| 4 Creative Director V2 | Three concepts, distinctness check | none | 10 sites: concepts pass the check; people can tell them apart |
| 5 Composition IR, hero | Schema, validator, IR renderer, hero transplant, bake-off | none | §13 criteria for S4 |
| 6 QA V2 | Two gates, failure types, fidelity | none (experimental path) | routing exercised on seeded defects of each type |
| 7 Comparison | E0–E3 on the benchmark, blind | none | decision per §10 |
| 8 Rollout, only if 7 says so | Experimental page offered as the second variant next to the production page; then swapped | flag per job; rollback is the flag | two weeks of live jobs without a technical-rate regression |

The existing "alternative blueprint" slot (`server/variant_snapshot.mjs`) is the natural carrier for step 8: the user already sees two variants. The experimental engine can be one of them before it is the default, and which variant people choose is live preference data.

Deploy rule from AGENTS.md stands: check `GET /jobs?status=running` before any push.

---

## 9. Test strategy

- **Existing net:** `npm test` (pytest + `tests/*.mjs`) and `scripts/livetest.sh 80 --all` before every commit. Pin the interpreter: the renderer needs Python ≥ 3.12 (§2 item 6).
- **Renderer refactor (S5 only):** golden renders of all 12 blueprints on the sample and on five frozen real jobs; byte-equal before and after.
- **IR validator:** one fixture per error code — a seeded defect the validator must catch — and a set of valid documents it must pass. No change lands that reduces the seeded-defect catch rate below 100%.
- **IR renderer:** determinism (same input, same bytes, twice); the existing contract at 1440 and 390 on every fixture; reduced-motion parity; long-word, long-headline, no-image, one-image and 40-item fixtures.
- **Content preservation:** property test — for any valid IR, every `present` required unit's text appears in the rendered DOM and every `must_keep` href appears as a link.
- **Design DNA:** schema validation; every `evidence` path exists; every `principles[].evidence` pointer resolves.
- **Content contract:** every fact marked `verbatim` is a normalised substring of captured text.
- **Critic:** recorded-response tests as today (`tests/` already mock the model request), plus a small labelled set of pages with a known failure type.
- **Security:** fixtures for the two gaps in §2 (scheme-filtered nav links, validated hexes) and for hostile source text in every `src` path.
- **End to end:** the benchmark runner re-runs any engine variant on frozen artefacts, so a change is compared on identical input.

---

## 10. Controlled experiment

**Question:** on the same source site, content and assets, do people prefer the page from the experimental engine?

**Arms**

| Arm | Engine |
|---|---|
| E0 | Production at `9200ead` (house lock on) |
| E1 | E0 with `SWARM_HOUSE=requirements` |
| E2 | E1 + Design DNA retrieval + three concepts + QA V2 |
| E3 | E2 + IR hero (bake-off) |
| E4 | Full-page IR (only if E3 earns it) |
| C | Competitor tools that take a URL, where terms allow — see the strategy document |

**Control of inputs.** Capture once per site and freeze `inventory.json`, `assets.json`, `images.json`, `factsheet.json` and the content plan. Every arm starts from the same frozen files, so differences come from composition, not from a different crawl or different copy.

**Sites.** 10 in week 2, 30 by week 3, chosen before any arm is run and not changed afterwards. Composition of the set is in the strategy document.

**Measures per site and arm**

| Measure | How |
|---|---|
| Brand fidelity | Human rating 1–5 with the original beside it |
| Content preservation | `coverage.json` + SEO-safe contract checks; count of dropped required units |
| Technical correctness | Contract score, hard failures, rendered checks, at 1440 and 390 |
| Visual originality | Blind pairwise preference; fingerprint similarity |
| Typography, composition | Blind pairwise, asked separately |
| Responsive quality | Phone screenshots judged separately from desktop |
| Generation time | Wall time per stage |
| Model cost | Tokens × list price, per attempt and per accepted page |

**Blind protocol.** A static page shows two screenshots of the same site from two arms, side by side, left/right randomised, arm names hidden, desktop and phone each. Questions are the six in the strategy document. Raters: the owner, at least three working designers, at least five people from the target market. Critic scores are recorded alongside and never shown to raters.

**Decision rule, fixed in advance.** An arm replaces its predecessor if all hold:
- preferred in ≥ 65% of pairs over ≥ 150 judgments, with the lower bound of the 95% interval above 50%;
- technical pass rate no more than 5 points below the predecessor;
- no increase in dropped required content;
- p90 wall time ≤ 15 minutes and cost per attempt ≤ 3× E0 **[H — thresholds are proposals]**.

If an arm does not clear the rule, the cause it was built to test is not the bottleneck, or the build is not good enough yet. Say which, with the evidence; do not move the threshold.

---

## 11. Risks

| Risk | Why it is real | Mitigation |
|---|---|---|
| The model composes badly in the IR | Spatial layout without sight is a known weakness | Seeds from measured references; render in the loop; hero first; the bake-off |
| More freedom, more breakage | Every guard in the current renderer exists because something broke (REFACTOR.md) | Static validator + rendered contract; fall back to the production page for the whole job, never silently per section |
| Cost and time grow | Three concepts, three heroes, revisions | Measure per stage; bake-off heroes are small; stop at the cheapest arm that wins |
| The critic rewards the wrong thing | Uncalibrated; 0 of 20 at 70 today may be the scale, not the pages | Human verdict on the benchmark; critic gates alone only after agreement ≥ 75% |
| Reference evidence is too thin for honest DNA | No mobile, 3 of 12 with screenshots, motion as prose | Recapture; mark `missing`; do not let a model fill in measurements |
| Rights in reference material | Third-party screenshots and text in `dna/` and `raw/`; commercial font names | Internal analysis only; never in an export or a public page; principles, not copies; the fingerprint also guards against cloning a reference |
| SEO-safe mode versus reorganising | Default mode keeps 95% of words and all links | The content contract carries the mode; in SEO-safe the composition may move and restyle, not rewrite |
| The house lock was added for a reason | It cut run-to-run variance and "AI slop" | E1 measures what removing it costs in broken or weak pages before anything changes in production |
| Vocabulary sprawl | Every missing primitive is tempting | Add from `missing_primitives.jsonl` by frequency; each new primitive ships with validator rules and fixtures |
| Refactoring `render_bp.py` | 1,800 lines of closures with shared state | Only after S4 proves value; golden renders; one move per commit |
| The benchmark overfits | 6 of 8 recent sites are software, and one site was run 8 times | Fix the 30-site set first; hold out 10 that are never used for tuning |

---

## 12. Estimated complexity

Estimates for one engineer working with an AI coding agent, in working days. They are judgments, not measurements. **[H]**

| Work | Size | Days | Notes |
|---|---|---|---|
| S1 Measurement: benchmark runner, frozen artefacts, separate scores, fingerprint, blind page | S | 2–3 | No engine change |
| S2 House as requirements, behind a flag | S | 1 | ~30 lines + tests |
| Hardening: nav scheme filter, hex validation, prompt contradiction, canned events | S | 0.5 | Independent of V2 |
| Design DNA: schema, 12 records, validator, retrieval | M | 3–4 | Plus 1–2 days to recapture 5+ references properly |
| Content contract: house split, builder, validator, fact evidence | M | 2–3 | Mostly deterministic |
| Creative Director V2: three concepts, distinctness, jury | M | 2–3 | Prompt and schema work; the jury needs S4's hero render |
| Composition IR v0.1: schema, validator, fixtures | M | 3–4 | The validator is most of it |
| IR renderer, hero + transplant | M | 3–4 | CSS Grid primitives, responsive rules |
| Hero seeds from the 12 references | S | 1–2 | |
| QA V2: split gates, fidelity, failure types, routing | M | 2–3 | |
| Comparison runs and analysis (10, then 30 sites) | M | 3–4 | Mostly waiting and rating |
| **Subtotal to an E3 decision** | | **~23–32** | Fits the 30-day plan only with S1–S2 in week 1 and strict scope |
| S5 Full-page IR: hoist closures, `component` nodes, section primitives | L | 8–12 | Only if E3 earns it |
| Rollout as a variant, then default | M | 2–3 | |

Running cost **[P][H]**: a production job today uses a median of 175k input and 26k output tokens; at the list price of the model in use that is roughly $0.6 per job (range about $0.3–$1.1). An E3 job is expected to cost 2–3× that. The 30-site, four-arm benchmark is on the order of a few hundred dollars. The strategy document has the cost model.

---

## 13. Acceptance criteria

**Phase 1b — measurement**
- 30 sites frozen with full artefacts; E0 output, both scores, fingerprint and wall time stored for each.
- The blind page works on a phone and records judgments to a file.

**Phase 1c — ablation**
- E1 produces ≥ 8 distinct section sequences across the 12 blueprints on the sample (today: 4), with a contract score ≥ 90 on every one.

**Phase 2 — Design DNA**
- 12 records validate. Every value is either tied to an evidence path or marked `missing`. `atelier` is `authored`.
- At least 5 references have desktop and mobile screenshots and a recorded capture date and viewport.
- Retrieval returns the same references for the same input.

**Phase 3 — content contract**
- On 10 benchmark sites: every required unit is `present` with source ids or `missing`; no fact without a source is placeable; the contract contains no layout field.

**Phase 4 — Creative Director V2**
- Three concepts differ in ≥ 3 of 5 structured dimensions on 10 of 10 sites.
- Shown the three hero renders, a person who has not seen the concepts matches concept to render on ≥ 8 of 10 sites.

**Phase 5 — Composition IR, hero**
- The validator catches 100% of seeded defects; passes 100% of valid fixtures.
- Same input renders to the same bytes.
- On 10 sites: contract ≥ 95 at 1440 and 390 with the IR hero in place; no dropped hero content; no action lost.
- Zero silent substitutions: every fallback has a recorded reason.
- Hero fingerprints of the 10 sites are pairwise distinct.

**Phase 6 — QA V2**
- Pages seeded with a type A, a type B and a type C problem are routed to the right response.
- No blended score exists in the experimental path.

**Phase 7 — comparison**
- The decision rule in §10 is applied as written, and the result is reported with the judgments, whichever way it goes.

**Overall**
- Three sites of different kinds (software, restaurant, studio), same engine, produce pages a blind rater does not assign to the same template.
- All three pass the technical gate.
- The strategy document's benchmark target: at least 24 of 30 redesigns judged meaningfully better than the original, by people.

---

## 14. Decisions the owner needs to make

1. ~~Reorganising versus "visual only".~~ **Decided 2026-11-09: it is the user's choice.** Those who want to keep their SEO and ranking choose SEO-safe; the others choose a free redesign. Both modes already exist; the table in §5.2 states what each one fixes. The sentence in REFACTOR.md ("we never change or add their words") describes the SEO-safe default, not a rule for every job.
2. **The house lock.** It was added on 2026-11-09 to make runs repeatable. E1 will show what it costs. If E1 wins, are you willing to give up "two runs never differ in architecture"?
3. **Reference material.** May third-party screenshots be sent to the model for analysis (they already are in `dna/`), given that rights are not established? The plan keeps them out of anything delivered.
4. **Who are the human raters,** and how many designers can be asked.
5. **How far up the ladder to go** if E1 or E2 already clears the bar.
6. **Concept selection:** model jury, or show the user three heroes and let them choose. The second is slower, and is itself a product feature.

---

## Appendix A — the local experiment

Read-only; writes only to a scratch directory. Python 3.12 (the system 3.9 cannot parse the renderer). Pillow was not installed in that interpreter, so image-pixel checks inside the renderer took their fallback paths.

Method: take `tests/direction.sample.json` with the sample images, assets and inventory. For each kind and each blueprint of that kind, clear per-beat `ui.move` and render twice — (A) beats limited to the types the kind's house has slots for, then `HOUSE.lock`; (B) all beats, no house. Extract the ordered list of `<section>` class tokens (without `sec` and `band-*`) and `data-sig`.

```python
def sig(html):
    out = []
    for m in re.finditer(r'<section class="([^"]*)"([^>]*)>', html):
        cls = [c for c in m.group(1).split() if c != 'sec' and not c.startswith('band-')]
        ds = re.search(r'data-sig="([^"]+)"', m.group(2))
        out.append('.'.join(cls) + (f'[{ds.group(1)}]' if ds else ''))
    return out
```

Result, sections between the hero and the closing call to action:

```
software · house    butter / cerebrium / deepbook            indexlist | marquee
software · recipe   butter      sticky | story | statement | marquee | cards.facts-cards | ledger
                    cerebrium   indexlist | twocol | typewall | numbers | numbers | ledger
                    deepbook    indexlist | twocol | typewall | cards | numbers | ledger
place    · house    tengile / white-desert / belgrade-arbor / units   ledger | indexlist | marquee
place    · recipe   tengile         indexlist | story | statement | cards | numbers | ledger
                    white-desert    indexlist | pinned | statement | cards | numbers | ledger
                    belgrade-arbor  railsec | story | typewall | cards | numbers | ledger
                    units           sticky | twocol | statement | cards | numbers | ledger
service  · house    aino / lpas / atelier                    indexlist | marquee
service  · recipe   aino     indexlist | numbers | statement | cards | numbers | ledger
                    lpas     sticky | ladder | typewall | cards | numbers | ledger
                    atelier  story | pinned | statement | cards | numbers | ledger
product  · house    crav / halfdays                          indexlist | ledger | marquee
product  · recipe   crav      indexlist | ladder | qband | cards | numbers | ledger
                    halfdays  story | twocol | qband | products | numbers | ledger

distinct sequences / blueprints:   house 4/12   ·   recipe 12/12
CSS outside :root: 54,781–54,796 bytes per blueprint; pairwise similarity ≥ 0.9997
```

Limits of this experiment: one content sample; the house arm has fewer beats than the recipe arm because the house rejects several beat types; it measures which components are chosen, not how the pages look.

## Appendix B — production sample

Source: `GET https://swarmsite-production.up.railway.app/jobs?status=done` (20 rows) and, per job, `/jobs/:id`, `/jobs/:id/art/critic.json`, `/art/direction.json`, `/art/swarm.json`, `/p/:id`. Read 2026-11-09.

| Site | Jobs | Kind | Blueprints | Taste (min–max) | Contract (min–max) |
|---|---|---|---|---|---|
| pdfbeautifier.com | 8 | software | deepbook 7, cerebrium 1 | 38–58 | 77–97 |
| sportbotai.com | 4 | software | deepbook | 52–58 | 100 |
| courtsensei.com | 2 | software | butter | 58–62 | 91–96 |
| balamorestaurante.es | 2 | place | tengile | 58 | 89–100 |
| simscore.ai | 1 | software | deepbook | 52 | 98 |
| automateed.com | 1 | software | butter | 52 | 95 |
| scanmysaas.com | 1 | software | deepbook | 58 | 100 |
| restaurantebutarque.es | 1 | place | tengile | 56 | 100 |

Display font on the delivered page: Instrument Sans on 12 of 20.
