# Swarmsite — Design Reference Research

Research phase of 2026-11-10, done before any further change to the creative architecture. It answers three questions:
how do recognised studios and designers decide, what do our 12 design references actually do when a browser measures
them, and what follows for the engine. The companion document `SWARMSITE_STUDIO_QUALITY_STANDARD.md` turns the
findings into criteria. Nothing in the production path was changed by this research.

## How to read this document

Every statement carries one of four marks. They are never mixed in one sentence.

| Mark | Meaning |
|---|---|
| **[S n]** | Stated by source *n* in the list at the end, opened during this research. Paraphrased, never quoted at length. `partly` = a secondary source or an incomplete page. |
| **[M]** | Measured by us: in a browser on 2026-11-10 with `design_dna/inspect.mjs` (references), or in our own pipeline (`bench/`, production jobs, `REFACTOR.md`). The file that holds the number is named. |
| **[I]** | Our interpretation. A judgement that the evidence supports but does not prove. |
| **not found** | Looked for and not published by the source. Absence of a published statement is not evidence of absence of the practice. |

Limits that apply throughout:

- Most studio pages were read through a fetch tool that returns a summary, so the wording here is paraphrase; where
  a page refused the tool (Medium, Codrops, one interview) it was read as full text in a browser. Three pages could not
  be opened at all and are listed as such.
- The classic texts are print-era. Their numbers (points, millimetres, words per line) transfer to screens by analogy
  only; where we use one as a threshold the Standard says so and marks the threshold as ours.
- A reference website is a moving target. Every measurement is of the page as served on 2026-11-10 to headless
  Chrome 1440×900 and 390×844, one run. Lab timings are indicative, not field data.
- Screenshots and raw readings of third-party sites are study material. They live in `bench/runs/_research/`, which
  git ignores, and are never shipped or copied into a generated page.

---

## Part A — How four studios say they work

Scope: published process, principles, case studies and stated quality bars of Active Theory, Locomotive, Resn and
Instrument. 31 pages opened; three more could not be opened. Active Theory and Locomotive document technique well;
Resn and Instrument publish almost nothing about the path from brief to launch.

### A.1 Active Theory

**Process, as stated**

- They learn "top-down": do the client task with existing tools, find the tools' limits, then build their own [S 1].
- Design and development overlap; prototyping joins them; a project's technology shapes how it looks; they iterate
  in small steps [S 5, a talk summary, no transcript].
- No hand-off from design to development: their Hydra GUI lets artists assemble 3D scenes without code; developers
  add behaviour and hand parameters back to artists [S 1].
- The Fiomet project began with content strategy and a messaging hierarchy, before any visuals [S 2].
- Rapid prototypes win work, and lab work is kept apart from client work [S 6, a third-party feature].

**Principles**

- An experience must deliver the product's functional points, not only engage [S 2].
- Own the stack as far down as possible: three.js and Electron were replaced once they capped performance [S 1].
- Text went into WebGL only where it was very large; small text blurs when render quality is lowered [S 3].
- Take the cheaper technique when it looks sufficient (an occlusion texture instead of physically based rendering,
  a faked depth of field) [S 2].

**Case studies**

- Pottermore Patronus (2016): an endless forest from repeatable tiles (one tile proved enough), six short audio
  loops remixed per question, geometry merged off the main thread [S 3].
- Fiomet (2020): a dark and a light art direction for two products, joined by a lateral transition; fullscreen 3D
  sections that can be navigated by scroll, keys, bullets, scrollbar and drag, and interrupted mid-way; CAD models
  reduced from 300k+ to 15–20k polygons [S 2].
- Their own site, version 5: the concept did not change from prototype to launch; environments grew from three to
  eight [S 4].

**Stated quality bars** — the only numeric ones found in any of the four studios: a 60 fps target; a test at load
that assigns each device a performance tier; dozens of per-feature settings that scale by tier; only visible scenes
render; a hidden HTML view runs in parallel for keyboard and screen-reader users [S 2][S 3].

### A.2 Locomotive

**Process, as stated** — thin. The agency page names operations, design and development as three equal parts but
gives no stages [S 15]. Developers judge feasibility during design because they know their own boilerplate [S 8].
Each project is built from scratch; reusable parts go into shared packages [S 9][S 10]. The creative director's
interview could not be opened.

**Principles**

- Smooth scrolling is decided early and per project: an experiential site may favour spectacle; a shop favours
  conversion, performance and native behaviour; strict accessibility needs mean native scroll. They list its costs
  themselves: in-page search stops scrolling to results, performance, conflicts with other plugins [S 7].
- No front-end framework by default; React or Vue only for application-like work [S 8][S 13].
- Fewer first-level menu choices; one distinct element to direct attention; the first screen sets the impression
  [S 16].
- Their own rebrand: fewer animations, two typefaces in four styles [S 12].

**Case studies**

- itsnotviolent.com (2020): a light, playful treatment chosen to sharpen a grave subject; candy colours on dark; one
  bold and one naive typeface; genderless illustrations; the delay before each chat message scaled to its length,
  capped, and tuned by repeated tests; static HTML behind a CDN [S 13].
- Baillat Studio (2022): black-on-white and white-on-black halves organise the studio's two disciplines; a custom
  stencil typeface with ligatures; a flexible editorial grid; scroll tied to an animation timeline [S 11].
- Locomotive rebrand (2023): a glyph-rich typeface as the identity tool; restrained motion [S 12].

**Stated quality bars** — no budgets or test method published. The documentation of their scroll library claims a
native scrollbar, keyboard navigation and ARIA, parallax switched off on touch, animation only while visible;
reduced-motion handling is not mentioned [S 14]. Their own-site case studies omit type, grid, testing and
accessibility [S 15].

### A.3 Resn

**Process, as stated** — almost none. A 2026 studio feature is a round-up of projects without method [S 17]. The
founders' interview is mostly humour; its substantive points: with a small budget they compress the idea to its
essence rather than cheapen it; dependable delivery on short timelines is what they sell; the staff is roughly 40%
developers and 35% designers [S 22]. Two further profiles could not be read.

**Principles, read from case studies**

- Two creative directions are proposed; the client picks one [S 18].
- The motion system — easings, reactions, principles — is fixed before the site is designed [S 18].
- Rendering is chosen by content: no WebGL on a site that is mostly DOM [S 18]; elsewhere CSS first, then Rive, then
  WebGL, until the result stayed sharp and fast [S 19].
- Motion designers author the animation; developers handle its synchronisation with scroll [S 19].

**Case studies**

- Zentry (2024): a typography-led direction; a display face adapted into distorted custom glyphs; a soundtrack that
  shifts as the visitor explores [S 18].
- Savor (2025): macro photography; diagrams driven by scroll; one shared WebGL context [S 19].
- KPR (2022): grid, white space and one variable typeface; click-and-hold opens a second layer [S 20].
- Noiz!: fast prototyping to cull weak options; touch latency as the governing constraint [S 21].

**Stated quality bars** — text rendering in a new tool was prototyped before the tool was adopted [S 19]. Nothing on
accessibility, testing or budgets in any Resn source: not found.

### A.4 Instrument

**Process, as stated**

- "Anti-process" (their term): team, process and deliverables are set per engagement; design and development are
  equal in size and mixed inside client teams [S 23, 2016].
- Components start in code after one round of content strategy; designers review pull requests; builds are shared
  with the client; projects end with a post-mortem [S 24].
- Prototype during design, not after it: cheap, disposable, one question each — can we build it, does it feel right
  [S 25].
- Flow, pacing and hierarchy are decided before any file or code exists [S 26].
- Oura: existing research reused, qualitative and quantitative consumer testing, iteration [S 29].

**Principles** — outcomes over process; data informs but targets do not drive; a rough experimental prototype beats a
safe interface [S 27]. Deliver a system with a guidebook, not a one-off site [S 24]. Accessibility through co-design,
beyond contrast ratios and tap targets [S 28].

**Case studies** — Oura.com (progressive disclosure, reusable components, a reported sales uplift) [S 29]; Electronic
Arts (a display typeface extended into serif, mono and text cuts; a motion toolkit) [S 30]; ServiceNow (an evolution
anchored on the existing colour and logo; a custom typeface family) [S 31]. None explains grid, type rationale,
accessibility or performance method.

**Stated quality bars** — none published as numbers: not found.

### A.5 What the four have in common [I]

Each line is our reading; the sources behind it are named so it can be checked.

1. **A prototype answers one question before anything is committed** — Active Theory [S 5][S 6], Instrument [S 25],
   Resn [S 19][S 21].
2. **Design and build overlap; there is no hand-off** — Active Theory [S 1][S 5], Instrument [S 23][S 24][S 26],
   Locomotive [S 8].
3. **A narrow toolset the studio owns makes feasibility knowable early** — Active Theory [S 1], Locomotive [S 8][S 9],
   Resn [S 18].
4. **Technique is chosen by content and cost, not by ambition** — Active Theory [S 2][S 3], Resn [S 18][S 19],
   Locomotive [S 7][S 8].
5. **The message hierarchy comes before the visuals** — Active Theory [S 2], Instrument [S 24][S 26].
6. **A custom or adapted typeface carries the identity** — Resn [S 18][S 20], Locomotive [S 11][S 12], Instrument
   [S 30][S 31].
7. **Motion is a defined system, or deliberately restrained** — Resn [S 18], Instrument [S 30], Locomotive [S 12].
8. **A two-sided contrast (dark/light) organises the page** — Active Theory [S 2], Locomotive [S 11][S 13].
9. **Spectacle is weighed against access explicitly** — Locomotive [S 7], Active Theory [S 3].
10. **Proposals come as more than one direction** — Resn proposes two and the client picks [S 18]; Active Theory
    built a dark and a light direction for Fiomet [S 2].

What none of them publishes: a reduced-motion policy; a performance budget (only Active Theory states a frame-rate
target); a grid or type rationale for a specific site; a test protocol. Whoever claims to know those from the outside
is guessing. For geometry, type and motion the only honest source is the shipped work itself, which is why Part C
measures it.

---

## Part B — Foundations, juries and testable standards

### B.1 Josef Müller-Brockmann — the grid as an attitude

- The grid is an ordering system that expresses a mental attitude: constructive and future-oriented. Work should have
  the intelligible, objective, functional and aesthetic quality of mathematical thinking. Using a grid implies the
  will to systematise, to reduce to essentials, to prefer objectivity to subjectivity, to rationalise production, to
  integrate colour, form and material, and to command surface and space [S 32][S 33] (the "Grid and Design
  Philosophy" text of 1981, read in an anthology reprint).
- From an OCR scan of *Grid Systems in Graphic Design*, read through a summarising tool — so the items stand, the
  wording and page numbers do not [S 34]:
  - fields let text and pictures be placed by objective, functional criteria; fewer picture formats give order and
    credibility; the grid is an aid, not a guarantee;
  - line length: two figures appear — about 7 words per line as a rule of thumb for longer text, and a column that
    reads well at an average of about 10 words. Web sources repeat only the second [S 35, partly]. No character count
    was seen;
  - type size and column width depend on each other;
  - leading: too tight and the eye takes in the neighbouring lines, too open and lines disconnect;
  - field heights derive from line counts; fields are separated by at least one empty line; pictures, captions and
    titles are sized to land on text lines;
  - margins are deliberately proportioned, not equal all round; too small crowds, too large looks wasteful;
  - one column gives little freedom; three and six force small type; four suits dense material;
  - hierarchy: sizes and weights clearly distinguishable, one family, captions subordinate.
- In a 1995 interview: the grid makes order cheaper, quicker and more legible; objectivity means legibility without
  emotional appeal [S 36].

### B.2 Massimo Vignelli — the Canon

Read directly in the PDF published by the Vignelli Center at RIT [S 37].

- **Semantics**: search for the meaning of the subject; nothing arbitrary. **Syntactics**: consistent relations
  between grid, type, images and the whole. **Pragmatics**: if it is not understood, the effort is wasted.
- **Discipline**: self-imposed rules; every detail counts equally. **Appropriateness**: the solution specific to the
  problem, beyond style. **Ambiguity**: a plurality of meanings, to be used with great caution. **Timelessness**:
  against fashion and obsolescence.
- Typefaces: he can manage with about half a dozen, perhaps a dozen. No type as decoration, no deformation.
- Type size follows column width (he gives pairs of size/leading for columns up to 70 mm, up to 140 mm, beyond).
- At most two sizes on a page; display roughly twice the text size; headings at text size in bold, separated by line
  spaces.
- Flush left by default; centred for lapidary text; justified is contrived.
- The grid exists to prevent arbitrary placement. Too fine a module equals no grid; too coarse restricts. Small outer
  margins give tension. Gutters are ideally one line of type.
- Rules have a weight hierarchy; type hangs from the rule.
- Large headings against small text need white space between them; scale may be broken only knowingly.

### B.3 Don Norman — signifiers, feedback and three levels of response

- An affordance is a possible action and exists whether or not it is perceived; what a designer controls on a screen
  is the *perceived* affordance. A signifier is any perceivable cue to what can be done; designers should supply
  signifiers. Follow conventions, use words, build a coherent conceptual model [S 38][S 39].
- The revised *Design of Everyday Things* adds signifiers as its one new concept; its chapters cover affordances,
  signifiers, mapping, feedback, constraints (physical, cultural, semantic, logical), discoverability and conceptual
  models [S 40][S 41].
- A numbered list of "seven principles" exists only in secondary summaries, and they disagree with each other
  [S 42, partly]. We do not use the list.
- Three levels of response: **visceral** (initial impact, appearance), **behavioural** (use, performance, feeling in
  control), **reflective** (self-image, meaning, brand). The levels can conflict and their weight depends on what the
  product is for [S 43].
- Positive affect broadens thinking and tolerance of minor faults; stressful contexts need the most usable design. He
  does not license neglecting usability [S 44].

### B.4 Awwwards

- Four criteria with published weights: **Design 40%, Usability 30%, Creativity 20%, Content 10%** [S 45].
- At least 18 jurors; the three scores furthest from the average are dropped; five days of voting [S 45].
- Honorable Mention at a jury score of 6.5 or more. No numeric threshold is published for Site of the Day [S 45].
- The Developer Award is judged separately, by a developer jury, on Site of the Day winners. Its weights: **web
  performance 0.20, responsive/mobile 0.20, semantics/SEO 0.20, markup/metadata 0.15, animations/transitions 0.15,
  accessibility 0.10** [S 46][S 47].

Two things matter for us beyond the numbers [I]: the jury scores *design* and *technical execution* in two separate
awards with two separate juries — the separation the brief asks for is how the best-known jury already works; and
the design jury is plural and trimmed (18 scores, 3 dropped), because one person's score is noise.

### B.5 CSS Design Awards

- Three criteria: **UI** (aesthetics, effects), **UX** (experience, functionality), **Innovation** (new development
  and design ideas). No weights or scale are published [S 48].
- Website of the Day needs an average judge score above 8.00 (stated as variable); Special Kudos above 6 [S 48].
- On one award page each judge's total equals the plain mean of the three scores [S 49] — an inference from one page,
  not a stated rule.

### B.6 The Webby Awards (Websites and Mobile Sites)

- Seven criteria, no weights: **Content; Structure and Navigation; Visual Design; Functionality; Interactivity;
  Innovation; Overall Experience** [S 50].
- The definitions place accessibility under Visual Design and under Functionality, and speed, working links and
  cross-browser operation under Functionality [S 50].
- Associate members of the Academy rate entries into shortlists; Executive members ballot; five nominees per
  category [S 51]. The People's Voice is a separate public vote [S 52].

FWA: its judging page returned 404; a search snippet gives a 0–100 average of judges' votes with site-of-the-day at
70 or more [S 53, partly]. Not used.

### B.7 WCAG 2.2 — the success criteria a generated landing page meets or fails

From the Recommendation itself [S 54]; what is new in 2.2 from [S 55].

| Criterion | Level | Requirement |
|---|---|---|
| 1.1.1 Non-text Content | A | Text alternative; decorative content can be ignored by assistive technology |
| 1.3.4 Orientation | AA | Not locked to one orientation |
| 1.4.3 Contrast (Minimum) | AA | 4.5:1; large text 3:1 (18 pt, or 14 pt bold) |
| 1.4.4 Resize Text | AA | 200% without loss of content or function |
| 1.4.10 Reflow | AA | No two-dimensional scrolling at 320 CSS px wide |
| 1.4.11 Non-text Contrast | AA | 3:1 for interface components and meaningful graphics |
| 1.4.12 Text Spacing | AA | Survives line height 1.5, paragraph spacing 2, letter spacing 0.12, word spacing 0.16 |
| 2.2.2 Pause, Stop, Hide | A | Motion that starts by itself, lasts over 5 s and sits beside other content can be paused |
| 2.3.1 Three Flashes | A | No more than three flashes per second |
| 2.3.3 Animation from Interactions | AAA | Motion triggered by interaction can be disabled |
| 2.4.6 Headings and Labels | AA | Describe topic or purpose |
| 2.4.7 Focus Visible | AA | Keyboard focus indicator is visible |
| 2.4.11 Focus Not Obscured (Minimum) | AA | The focused element is not entirely hidden (new in 2.2) |
| 2.5.7 Dragging Movements | AA | A single-pointer alternative exists (new in 2.2) |
| 2.5.8 Target Size (Minimum) | AA | 24×24 CSS px, or the spacing exception (new in 2.2) |
| 1.4.6 / 2.5.5 / 2.4.13 | AAA | 7:1 contrast; 44×44 px targets; focus indicator of 2 px perimeter and 3:1 change |

### B.8 Core Web Vitals

From Google's own documentation [S 56]–[S 63].

- Good: **LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1**. Poor: above 4.0 s, 500 ms, 0.25. Assessed at the 75th percentile of
  real visits, phone and desktop separately [S 56]. INP replaced FID on 12 March 2024 [S 63].
- Supporting, not core: TTFB good at ≤ 0.8 s; FCP good at ≤ 1.8 s [S 61][S 62].
- LCP excludes elements at opacity 0 and full-viewport background-like elements; a web font's block period delays
  text candidates; reporting stops at the first interaction [S 57].
- CLS counts unexpected shifts in the worst session window; shifts within 500 ms of a discrete input are excluded;
  composited `transform` animations do not count, animating `top`/`left` or `width`/`height` does [S 59].
- Fonts shift layout under both swap and invisible-text behaviour; give pictures their dimensions or an aspect ratio
  [S 60].

Consequence for an engine that animates [I, from S 57 and S 59]: an intro that holds the headline at opacity 0 delays
LCP by exactly the length of the intro, and a reveal that animates layout properties is counted as layout shift. Both
are measurable in a lab run of our own page; neither is a matter of taste.

### B.9 Three kinds of authority — and what each can be used for

| | What it is | Strength | Limit | Used in the Standard as |
|---|---|---|---|---|
| Müller-Brockmann, Vignelli, Norman | The reasoned position of a master | Coherent, explains *why* | Self-declared; print-era numbers; not testable | Vocabulary, direction, the reasons attached to defects |
| Awwwards, CSSDA, Webby | A jury's weighted score | Names the criteria and (Awwwards) their weights; plural | Each score is a human judgement; thresholds relative or unpublished; not reproducible | The structure of the creative score and the rule that it is plural and separate from the technical one |
| WCAG 2.2, Core Web Vitals | A testable requirement | A number, a method, pass or fail | Certifies a floor, never quality | Hard gates, graded on their own track |

---

## Part C — The twelve references, measured

### C.0 Method

**Instrument.** `design_dna/inspect.mjs`, written for this research. It is a measuring tool, not part of the
production path, and it calls no model. For one page it writes `evidence.json` and screenshots:

| Reading | How it is taken |
|---|---|
| Type | Every style text is actually set in (computed family, size, weight, case, tracking, leading), with the characters it carries and where; line length of the longest paragraphs from the browser's own line boxes |
| Geometry | The first screen (headline box, largest picture, text extent, filled buttons, the bar); the left edges at least three blocks share; declared grids; the sections in order with their height, ground, space around content, columns, density |
| Pictures and surfaces | Each picture's size, ratio, own ratio, bleed, corner, shadow, filter, blend, whether words stand on it; counts of filled or framed boxes, shadows, hairlines, gradients; button styles |
| Motion on load | Every animation frame for about 5.5 s from DOMContentLoaded: position, width and opacity of each heading, paragraph, list item, picture, button and every element inside a heading that is on screen |
| Motion on scroll | The page scrolled in steps of 0.6 screen with a 1.2 s pause after each (wheel at 1440, a touch gesture at 390), sampled every frame; at most 20 steps at 1440 and 16 at 390 |
| Pointer | Computed style of up to four actions on the first screen before and after the pointer rests on them |
| Reduced motion | The first 6 s again with `prefers-reduced-motion: reduce` |
| Lab | Largest Contentful Paint and layout shift before any input, requests and transferred bytes — one run |
| Rules, on a second short visit | Rules on elements, rules drawn by pseudo-elements and `hr`, at 1440; added to the evidence file under `supplement` after the first reading turned out to miss the last two |

**Thresholds of the motion readings** (written into every evidence file under `method`): a *fade* is opacity from
≤ 0.2 to ≥ 0.9; a *travel* is 6–240 px of movement relative to the document while the page stands still, lasting
50 ms–3 s; *held* is an unchanged position on screen while the page scrolls at least 0.4 screen (held through 75% of
all scrolling counts as fixed chrome); *parallax* is a position that changes relative to the document in at least 60%
of ten or more scrolling frames; *sideways* is at least a quarter of the screen width of horizontal movement while
scrolling; *scroll lag* is the time between the last input of a step and the last frame in which the scroll position
changed, read against the same on an empty page (0 ms in ten of twelve runs, at most 84 ms).

**Run.** 2026-11-10, headless Chrome, 1440×900 and 390×844 (phone user agent, touch), one run per view. Evidence and
screenshots: `bench/runs/_research/references/<id>/` — untracked, research only.

**Limits — they apply to every number below**

- One run of a live page. Sites change: one of the twelve is today a different page from the one our recipe was
  captured from (C.3).
- Headless Chrome: WebGL and canvas may render differently, video may not play, and lab timings say nothing about
  visitors.
- Consent banners were recognised and hidden; none was answered.
- Motion readings cover the first 12 screens at 1440 and about 10 at 390; later parts of very long pages were walked
  for layout but not sampled for motion. At most 500 elements near the viewport are followed.
- "Pictures" are `img` and `video` elements of at least 160×100 px, at most 44 per page. CSS background pictures are
  counted separately and not analysed.
- Sections are found structurally (the tall blocks of the page). A reading can belong to a wrapper rather than to
  what a designer would call a section; where that shows, the analysis says so.
- A full-page capture shows a held section as it stands at the top of the page, so long holds appear blank in the
  contact sheets. They were read from the viewport captures and the `held` readings.
- Face names are the computed `font-family` as loaded by the page, nothing more.

**The twelve**

| Id | Source | Kind (our record) | Measured | Note |
|---|---|---|---|---|
| butter | butter.video | software | both views | |
| cerebrium | cerebrium.ai | software | both views | |
| deepbook | deepbook.tech | software | both views | redirects to another domain; today's page differs substantially from our capture |
| tengile | tengilemalamala.com | place | both views | |
| belgrade-arbor | belgradearbor.rs/en | place | both views | the page shows a ribbon reading "Site of the Day" in every viewport capture [M-seen]; not verified independently |
| white-desert | white-desert.com | place | both views | |
| crav | cravburgers.shop | product | both views | |
| halfdays | halfdays.com | product | both views | redirected to a regional storefront |
| units | units.gr/en/homepage | place | both views | |
| aino | aino.agency | service | both views | ignored wheel and touch input and was moved by script; every viewport capture shows a character-drawn field over the page |
| lpas | lpas.com | service | both views | |
| atelier | none — our own authored recipe | service | both views, as rendered by our renderer with sample content | not a third-party reference; excluded from every range in Part D |

How the per-reference analyses were made: each was written from that reference's `evidence.json` and screenshots
alone, under written rules of evidence — a number must be in the evidence; a statement is marked measured **[M]**,
seen in a named screenshot **[M-seen]**, or interpretation **[I]**; nothing may come from prior knowledge of the
site, its makers or its typefaces. The recipes in `lib/blueprints/` and the records in `design_dna/references/` were
read for comparison and were not changed.

### C.0.1 The twelve at a glance

One line each; every line is **[I]**, condensed from the analysis that follows, which gives the evidence.

| Reference | The idea the page is built on |
|---|---|
| butter | A neutral editing surface: one near-white ground, one face in one weight; colour and movement belong to looping product media, and statements arrive a word at a time |
| cerebrium | A dark moving backdrop as stage, content on light sheets that slide over it; three voices — light display, plain text, mono capitals for anything that is interface |
| deepbook | The opening argument is a film that carries the headline; below it a plain squared document in one bold face, with one picture language (halftone cut-outs on flat blue) |
| tengile | One paper ground on which scale does the work: a single very large, very light heading over full-screen video, then statements as large paragraphs and pictures whose size changes every section |
| belgrade-arbor | A run of full-screen chapters, each opened by one enormous word on a full-bleed picture, with a long pinned stage where the text is released word by word |
| white-desert | Three typefaces kept far apart in scale on white over visible column lines, and one stage in the middle where the page stops going down and goes sideways |
| crav | A poster, not a layout: the words are the frame, the product is pasted over the letters, and the ground changes colour instead of drawing a box |
| halfdays | A shop front where photographs persuade and type is shelf labelling: one small sans, labels set on the pictures, a strict proportion per row, almost no movement |
| units | A card system: one paper ground on which photographs, text and navigation are all flat-coloured tiles with one large radius, and a single pinned rail |
| aino | An index, not a pitch: unframed tiles on a four-column grid, every label at one small size, one sentence as the only large type; the first screen is a character-drawn field |
| lpas | The first screen does not leave: it holds while scrolling pushes five cards across it sideways; everything after is a plain white document in one face at one weight |
| atelier | Not a studio's page: our own recipe, written to mirror lpas. What our renderer draws from it under the sample direction is a different page (C.12) |

### C.1 butter — https://www.butter.video/

**Measured**: [M] status 200 in both views; 16.53 screens at 1440×900, 15.33 at 390×844; `failed` empty, no input ignored (wheel and touch moved the page natively); the scroll run ended at its step limit in both views (20 steps desktop, 16 phone), so the last part of the page has no motion reading.

**Creative thesis [I]** — The page is built as a neutral editing surface: one near-white ground, one face in one weight, and all colour and movement handed to looping product media, with statements given a screen each and delivered a word at a time. What carries it: 13 of 14 sections share the ground 250,250,250 (desktop, sections); every type style is weight 400 (desktop, type); the page holds 49 video elements (desktop, built_with); 76 of the 98 scroll reveals are word spans inside headings, fading for about 667 ms at 50 ms intervals (desktop, scroll.reveals); one section is pinned and moves sideways (desktop, scroll.held, scroll.sideways).

**Typography system**

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Largest display = h1 | DieGrotesk | 107.6 (7.47) | 400 | +0.003 | 0.99 | none | 56.7 |
| Section heading (h2) | DieGrotesk | 60.4 (4.19) | 400 | +0.006 | 0.97 | none | 32.4 |
| Sub-heading (h3) | DieGrotesk | 45.5 (3.16) | 400 | +0.008 | 0.96 | none | 32.2 |
| Name list (buttons) | DieGrotesk | 41.7 (2.89) | 400 | +0.008 | 0.96 | none | 26.0 |
| Lede, card heading (p, small h3) | DieGrotesk | 24.5 (1.70) | 400 | +0.030 | 1.15 | none | 20.1 |
| Body, large | DieGrotesk | 20.7 (1.44) | 400 | +0.033 | 1.16 | none | 20.0 |
| Body, small; navigation | DieGrotesk | 16.0 (1.11) | 400 | +0.044 | 1.31 (nav 1.25) | none | 16.0 |
| Label | ABCDiatype | 13.5 (0.94) | 400 | +0.036 | 1.78 | none | 12.0 |

- [M] Two families (desktop, families_loaded); the phone also lists "DieGrotesk Fallback" and "ABCDiatype Fallback". ABCDiatype sets 273 characters of labels (p ×12, footer p ×6, header p ×4); everything else is DieGrotesk.
- [M] h1 ÷ body = 107.6 ÷ 20.7 ≈ 5.2, and ÷ 16 ≈ 6.7. The 16 px style carries the most characters (901), then 20.7 px (840), then h2 (411). Ten sizes in the desktop reading; nine carry content (18 px holds only a 15-character skip link).
- [M] Line length: 16 px paragraphs run 45 characters per line at 29.7 em (475 px); a 20.7 px paragraph 30 per line at 24.8 em (514 px) (desktop, paragraphs).
- [M] Tracking rises as size falls (+0.003 em at 107.6 px to +0.044 em at 16 px); leading is 0.96–0.99 on headings and 1.15–1.31 on text. Headings are split into word spans (the h2 style counts 125 elements). No italic, no uppercase transform.
- [M] `headings.h1.lines` reads 2 at 1440 and 3 at 390. [M-seen] The h1 is on one line in desktop-scroll-0.jpg and on two in mobile-scroll-0.jpg. [M] The h1 height (0.119 and 0.146 of the screen) agrees with the screenshots, so the line count is an artefact of the split words.
- [M-seen] Small pictograms sit inside the running text of one heading ("Make blocks your own…", sheet-desktop.jpg).

**Layout geometry**
- [M] Shared left edge at 0.05 of the width (37 blocks); section text runs 0.046–0.954. Other edges: 0.59 (16 blocks), 0.08 (13), 0.20 (12), 0.51 (12), 0.66 (9), 0.82 (7) (desktop, alignment.edges). Declared grids: 12 columns ×8, 24 columns ×1 (both views).
- [M] First screen: h1 centred at x 0.124, y 0.397, width 0.751; a canvas covers the whole screen (share 1.0); text spans y 0.031–0.669; fixed bar 88 px high, transparent ground, 18 links.
- [M] `first_screen.filled_buttons` reads 0. [M-seen] Two dark filled buttons are visible on the first screen (desktop-scroll-0.jpg); the reading disagrees with the screenshot.
- [M] Centred text: 0.19 of text blocks; four sections are centred (hero, logo strip, statement, template-rail heading), the rest left-aligned. Median one text column per section.
- [M] In the six "heading opposite media" sections (at 3.24, 4.74, 6.29, 9.70, 12.11, 14.25 screens) the text starts at 0.046, 0.586, 0.046, 0.586, 0.046, 0.586 — it alternates sides.

**Section rhythm**
- [M] 14 sections, in screens: 1, 0.24, 1, 1, 1.5, 1.29, 2, 1.1, 1.1, 1.32, 1.02, 1.11, 1.1, 1.25 (desktop).
- [M] The long ones: 1.5 and 1.29 (heading opposite product media) and 2.0 at 6.29 screens (a heading, a 1308×736 video starting at x 0.546, 1064 px below the content — the pinned section).
- [M] Grounds: 250,250,250 for thirteen sections, 237,237,237 for the footer — one change; area shares 0.92 / 0.08.
- [M] Space above / below content: median 140 / 190 px; the statement has 357 px above and below a three-line heading; -72 and -83 are artefacts of pictures overhanging their wrapper.
- [M] Characters per screen, in order: 86, 213, 102, 0, 168, 82, 56, 348, 98, 579, 173, 306, 82, 240 — a picture-only screen follows the statement; the dense screens are the four cards, the template rail and the two-card row.
- [I] One idea per screen with long quiet gaps, broken three times by a denser inventory screen.

**Image treatment**
- [M] The picture list stops at its limit of 44 (desktop, pictures); the per-section counts add up to 59. Of the 44: 34 video, 2 bleed, 9 rounded (all 32px), 0 shadow, 0 filter, blend or mask, 2 with words on them.
- [M] No listed video was playing (`playing` false on all) — headless caveat; what the videos do in motion is not in the evidence.
- [M] Ratios and width shares: 0.56 (rail items 216×384, share 0.15), 0.77 (four cards 308×401, share 0.21), 0.91–0.93 (half-width media 641×706 and 641×687, share 0.45), 1.0 (tiles of 241 and 194 px), 1.78 (1308×736, share 0.91), 2.01 (the bleeding panel 1504×747, share 1.04), 2.67 (641×240, cut from own 1.43).
- [M] The hero still's box is 1872×360 (ratio 5.2, share 1.3) with fit contain and own ratio 1.89; "cropped" there is an artefact — a contained picture is not cut.
- [M-seen] Pictures show the product's interface in dark panels, square effect tiles in saturated colour, phone-shaped template clips, one object photograph on a white card, a 3D key ring in the hero and a wordmark with a blurred multi-colour extrusion in the footer (sheet-desktop.jpg, desktop-scroll-25.jpg, -75, -100).
- [M-seen] Half-width media sit in rounded dark panels or rounded cards opposite a text column; the rail and the two-card row sit inside pale rounded panels (sheet-desktop.jpg).

**Motion behaviour**
- [M] Load, desktop (times after the sampler began, 222 ms after navigation): an intro sentence fades in at 148 ms (144 ms); the canvas fades at 682 ms (399 ms); the three h1 words start at 2920, 2947, 2997 ms and fade for 644–667 ms; the h1 settles at 3664 ms, the last reveal. No travel on load. LCP 244 ms on a span (lab, one run).
- [M-seen] desktop-load-1.25s.jpg shows only the intro sentence, centred, its words darker to lighter left to right; in desktop-load-3.5s.jpg the h1 is soft-edged and lighter toward its last word and the key ring is partly above the top edge; in desktop-scroll-0.jpg it hangs lower and the h1 is solid.
- [M] Scroll reveals, desktop: 98, all fades (quartiles 534 / 666 / 667 ms); 3 also travel 7–12 px upward in 317–383 ms; kinds: h2 › span 55, h3 › span 21, video 11, img 10, p 1; 14 staggered groups, gap 50 ms. Logos in the strip fade for about 533 ms, 100 ms apart.
- [M] Held, desktop: 19 elements, 12 for about 1.0 screen and 7 for about 0.5. The named examples (a video, the label and the heading of "Customize and save…") also move sideways with the scroll: -0.28 px per px scrolled for the video, -0.38 for the label, -0.47 for the heading, about half a screen-width in total; 19 elements move this way. `sticky_inside` reads 0 for that section. [I] The pin is probably scripted or set on an ancestor the section reading does not see.
- [M] Scale with scroll: 5 elements; the tile img goes 70 → 140 px and tile videos 69 → 110–116 px while scrolling, then on to 171–200 px while the page stands; the tiles are 241 px in the static reading.
- [M] 27 elements drift sideways by themselves on desktop, 10 on the phone (marquee-type). Parallax: none.
- [M] Smoothing: median scroll lag 1007 ms against a baseline of 0 (desktop); `lenis` detected; lag 0 on the phone.
- [M] Pointer: one text link drops to opacity 0.4 over 0.5 s; a second probed link changes nothing; cursor reads `auto`. [M-seen] A small black pill with two words sits at the top-left corner in desktop-scroll-25.jpg only; what places it there was not measured.
- [M] Reduced motion: 9 load reveals with the preference set, 6 without — the load sequence is not reduced; 0 reduced-motion rules found, with 3 of 10 stylesheets unreadable.
- [M] Declared: transitions of 0.8 s (111 elements), 1 s (52), 0.5 s (47), 0.4 s (8); easings cubic-bezier(0, 0, 0, 1) (105), cubic-bezier(0.2, 0.715, 0.205, 0.99) (95), cubic-bezier(0.835, 0.12, 0.225, 0.77) (15); 55 elements with keyframes.

**Responsive transformations**
- [M] Type: h1 56.7 px (×0.53), h2 32.4 (×0.54), h3 32.2 (×0.71) — h2 and h3 become one size; 24.5 → 20.1; body 20.7 → 20.0 and 16 → 16; label 13.5 → 12.
- [M] h1 at x 0.066, y 0.369, width 0.867. No canvas (canvases 0): the largest first-screen picture is a still, 507×338, 1.3 of the width from x -0.15, 0.4 of the screen.
- [M] One left edge at 0.07 carries 94 blocks; paragraphs run 24–27 characters per line (16.9–17.4 em). Median space above / below content 101 / 181 px.
- [M] 14 sections again: 1, 0.29, 1.11, 1.35, 0.97, 0.48, 1.13, 1.18, 1.34, 0.99, 1.85, 1.31, 1.23, 0.18 (the last is a link wrapping the footer picture — an artefact). The 2.0-screen pinned section becomes 0.48 screen; held 0, sideways-with-scroll 0, scale-with-scroll 0.
- [M] The four cards go from four columns (share 0.21) to a row of 0.78-wide cards at x 0.066, 0.914, 1.762, 2.61 running off the right edge; rail items go from share 0.15 to 0.55. Radii: 32px kept on cards, other product media read 14.3px.
- [M] Bar 88 → 76 px, links 18 → 11, a menu button in both views. [M-seen] The phone bar is one pale pill with the wordmark and a two-dot menu (mobile-scroll-0.jpg); on desktop the pill carries six links at the top and collapses to wordmark and dots once scrolled (desktop-scroll-0.jpg, desktop-scroll-25.jpg).
- [M] Motion kept: 93 scroll reveals, all fades (663 / 666 / 667 ms), 18 groups at 50 ms; more travel than desktop (19 elements, 10–19 px, upward). On load five bar parts rise 48 px in 330 ms and the hero still travels 66 px; the h1 settles at 3673 ms.
- [M-seen] mobile-load-1.25s.jpg shows the text of a consent panel faintly through the intro screen; the banner was hidden by the tool, not answered.

**Surfaces**
- [M] 9 filled or framed boxes (radius 11px ×4, 32px ×3, 0 ×2), 0 shadows, 0 hairlines, 1 gradient, no CSS background pictures; one filled-button style: ground 30,30,30, ink 250,250,250, radius 8px, 47 px high; no outlined buttons (desktop, surfaces).
- [M-seen] The hero ground is a vertical grey-to-near-white gradient (desktop-load-0.35s.jpg); a soft shadow lies under the dark timeline panel (sheet-desktop.jpg, foot of the first column). [I] As `shadows` reads 0, it is probably painted in the picture or by a property the reading does not cover.

**Reusable principles [I, each with its evidence]**
1. Hold weight constant and let size, tracking and ink strength make the hierarchy. Evidence: weight 400 on every style at ten sizes (desktop, type); tracking +0.003 em at 107.6 px rising to +0.044 em at 16 px; leading 0.96–0.99 on headings, 1.15–1.31 on text; ink 15,15,15 at 0.4 alpha sets 0.36 of all characters (desktop, colour.inks).
2. Keep one ground and let the media carry all the colour. Evidence: 13 of 14 sections on 250,250,250, one change at the footer, area share 0.92; saturated media seen in sheet-desktop.jpg.
3. Reveal headings by the word, in place: fade only, one duration, one short gap. Evidence: 76 of 98 scroll reveals are spans in h2/h3; fade median 666 ms; gap 50 ms; only 3 travels, of at most 12 px; the h1 on load does the same (644–667 ms).
4. Alternate sparse statement screens with dense inventory screens. Evidence: characters per screen 86, 213, 102, 0, 168, 82, 56, 348, 98, 579, 173, 306, 82, 240; a 1.00-screen statement with 357 px above and below, followed by a picture-only screen.
5. Keep one pattern and one media width, and switch the side. Evidence: text starts at 0.046 / 0.586 alternately in six sections; half-width media at share 0.45; edges 0.05 (37 blocks) and 0.59 (16 blocks).
6. One scroll-coupled set-piece on wide screens, removed on phones while the reveals stay. Evidence: one 2.00-screen section with 19 held elements moving sideways and 5 elements scaling with scroll on desktop; on the phone 0 held, 0 sideways with scroll, that section 0.48 screen, 93 reveals kept.

**Against our existing record**
- [M] Sizes differ slightly: record display 103 px, h2 58, h3 44, body 21 at a 1440×756 viewport; today 107.6, 60.4, 45.5, 20.7 at 1440×900. Tracking and leading agree (0.0032 / 0.99 against +0.003 / 0.99). [I] The page may size type by viewport height as well as width; two captures cannot settle it.
- [M] The record lists three families (Times, DieGrotesk, ABCDiatype) and no label level; today two families load on desktop and the label is ABCDiatype 13.5 px, +0.036 em, leading 1.78. The blueprint's button radius is 999 at 48 px high; today the filled button reads radius 8px at 47 px.
- [M] Record: 13 sections over 17.8 screens of 756 px; today 14 sections over 16.53 screens of 900 px (the record's 2.0-screen statement is now two 1.00-screen blocks). The record's `custom_cursor` is true; today's cursor reads `auto`.
- [M] The record marks one section as pinned by a hand-written role ("story-sticky", 1.21 screens, scroll "not measured"). Today's held and sideways readings name the section the record calls "story-wide" (2.0 screens). [I] The desktop scroll run ended as the record's pinned section entered the view, so today neither confirms nor refutes it.
- [M] Not in the record: the phone view, the intro and h1 timing, word-by-word reveals, the sideways pinned section, scale with scroll, the smoothing lag, the reduced-motion result, the two ink strengths.

**Not measurable here** — What the videos and the 3D canvas do in motion (no video played; WebGL in a headless browser); motion in the last sections on both views (step limit); pictures beyond the 44-item limit; which elements are the seven held for half a screen; pointer effects beyond two probed links, the menu when open, card hover; reduced-motion rules in the 3 unreadable stylesheets; the layout with the consent banner present; widths between 390 and 1440; field timings (one lab run).

### C.2 cerebrium — https://cerebrium.ai/

**Measured**: [M] status 200 in both views; 12.08 screens at 1440×900, 12.13 at 390×844; `failed` empty, no input ignored; the desktop scroll run took 19 steps, the phone run ended at its 16-step limit, so the end of the phone page has no motion reading.

**Creative thesis [I]** — A dark, moving backdrop is the stage and the content arrives on light sheets that slide over it; the voice is split in three: large light-weight statements with one accented phrase, a plain text face for explanation, and small mono capitals for everything that behaves like interface. What carries it: a canvas fills the first screen (desktop, first_screen); grounds alternate dark / white / dark / pale / dark with area shares 0.42 / 0.36 / 0.22 (desktop, sections, colour); display type is weight 300 with tracking -0.025 to -0.05 em (desktop, type); labels, navigation and buttons are 13 px mono, uppercase (desktop, type); the feature run holds its index for about three screens (desktop, scroll.held).

**Typography system**

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Largest reading (20 single-letter spans, not seen) | ABC Favorit Trial | 144.0 (10.00) | 500 | 0 | 1.0 | none | 72.0 |
| h1 | ABC Favorit Trial | 86.1 (5.98) | 300 | -0.025 | 1.0 | none | 45.0 |
| Section statement (p) | ABC Favorit Trial | 72.6 (5.04) | 300 | -0.025 | 1.05 | none | 40.0 |
| Second statement (p) | ABC Favorit Trial | 57.4 (3.99) | 300 | -0.05 | 1.05 | none | 40.0 |
| Index titles (a), one h2 | ABC Favorit Trial | 43.9 (3.05) | 300 | -0.05 | 1.15 | none | 25.0 (h2 only) |
| Block heading (h3, footer p) | Suisse Intl | 36.1 (2.51) | 300 | -0.025 | 1.15 | none | 25.0 |
| Sub-heading, card title (h3, a, p) | Suisse Intl | 26.5 (1.84) | 400 | -0.025 | 1.35 | none | 20.0 |
| Body | Suisse Intl | 18.0 (1.25) | 400 | +0.01 | 1.5 | none | 17.0 |
| Lede, small body | Suisse Intl | 17.0 (1.18) | 400 | +0.01 | 1.35 | none | 16.0 |
| Label, navigation, buttons | Suisse Intl Mono | 13.0 (0.90) | 400 | -0.025 | 1.07 | uppercase | 13.0 |

- [M] Three families (families_loaded): ABC Favorit Trial for the h1, statements and index titles; Suisse Intl for sub-headings and text; Suisse Intl Mono for labels, navigation and buttons in capitals (518 + 87 characters) and for a terminal mock-up in mixed case at weight 500 (547 characters).
- [M] h1 ÷ body = 86.1 ÷ 18 ≈ 4.8 (÷ 17 ≈ 5.1). Fourteen sizes in the desktop reading; most characters sit at 26.5 px (1187), 18 px (773), 16 px (599) and 17 px (423).
- [M] Line length: 18 px paragraphs run 49–59 characters per line at 31.6 em (570 px); the 17 px lede 32 per line at 19.1 em (325 px).
- [M] The large statements are `p` elements (72.6 px in 10 elements, 57.4 px in 4), while four of the `h2` are one-line labels in the 13 px mono capitals. The h1 is split into seven blocks (load reveals 'h1 › div' 7). `text-wrap: balance` is set on the 26.5 px and 17 px styles. No italic.
- [M] The 144 px reading cannot be found in any screenshot; it is text present in the page but not shown in these captures.
- [M-seen] One phrase per statement is filled with a pink-to-violet gradient (desktop-scroll-0.jpg, -50, -75). [M] Pink 255,72,139 is the ink of 0.03 of all characters.

**Layout geometry**
- [M] Left margin edge at 0.03 (13 blocks; section text 0.028–0.972). The most-shared edge is the half line, 0.51 (24 blocks); then 0.67 (10), 0.75 (9), 0.35 (8) (desktop, alignment.edges). Declared grids: 2 columns ×7, 3 ×2, 12 ×2, 20 ×2. Centred text share 0.
- [M] First screen: h1 left-aligned and low, at x 0.028, y 0.622, width 0.465, three lines; content starts 560 px down; the canvas takes the whole screen; four filled buttons; text reaches y 0.909; fixed bar 82 px, transparent ground.
- [M] `bar.links` reads 0. [M-seen] The bar shows five links and two buttons (desktop-scroll-0.jpg) — a miss of the reading.
- [M-seen] The lede and two buttons form a second narrow column to the right of the h1 (desktop-scroll-0.jpg). [M] Median two text columns per section.
- [M] In the feature run the label and index titles sit at the left margin and the picture starts at x 0.507 (width share 0.47).

**Section rhythm**
- [M] The reading returns 13 blocks: 1, 0.15, 0.4, 0.16, 3.52, 0.66, 0.4, 0.64, 0.17, 0.79, 0.59, 0.73, 0.99 screens (desktop). Several are rows or wrappers, not sections (the 0.15–0.17 rows; two text-less 0.40 blocks with no spacing reading) — an artefact of the section finder; the heights add up to less than the page.
- [M-seen] The page reads as five bands: dark hero with a logo row and a dotted strip; a white sheet (statement, feature run); a dark band (security, dotted strip, examples); a pale sheet (industries, case cards, feature list, blog); a dark footer (sheet-desktop.jpg).
- [M] The long block is the feature run: 3.52 screens from 2.05, 1787 characters, one sticky element inside.
- [M] Grounds in order: 16,20,33 ×3, 255,255,255 ×2, 16,20,33 ×3, 238,242,245 ×4, 16,20,33 — four changes.
- [M] Space: the hero has 560 px above and 82 px below its content; elsewhere the blocks hug their content (median 0 / 16 px), which says little; -7, -6 and -90 are artefacts.
- [M] Characters per screen: hero 233, feature run 507, security 1076, examples 612, case cards 897, feature list 504, blog 400, footer 294.
- [I] A sparse opening, one long held passage, then short dense bands that change ground every one to three screens.

**Image treatment**
- [M] 11 pictures listed (desktop): none bleed, none rounded, none shadowed, none video, no filter, blend or mask; 2 with words on them.
- [M] `cropped` reads true on 10, but six of those are case-card logos drawn with fit contain in boxes of ratio 1.21 (own ratios 1 to 7.84) — letterboxed, an artefact. Cut by cover: the 670×775 feature picture (ratio 0.86 from own 1.0, share 0.47) and three 440×564 blog pictures (ratio 0.78 from own 1.18, share 0.31 at x 0.028, 0.347, 0.667).
- [M] The case-card logos sit at x 0.112, 0.43, 0.748, 1.067 … 2.025, a row continuing past the right edge; `swiper` detected.
- [M] The largest picture of the first screen is a canvas over the whole screen (canvases 1); 1 CSS background picture, 7 gradients.
- [M-seen] The canvas shows broad magenta ribbon arcs on a near-black ground with grain and small dots (desktop-scroll-0.jpg); a bright streak on one arc is present in desktop-scroll-0.jpg and absent in desktop-load-3.5s.jpg; the arcs return behind the footer (desktop-scroll-100.jpg) and a ringed sphere sits behind the security text (desktop-scroll-50.jpg, mobile-scroll-50.jpg). [I] With one canvas counted, the dark bands are probably openings onto a single backdrop that the light sheets cover. WebGL may render differently in a headless browser.
- [M-seen] Feature pictures are interface mock-ups (comparison bars, a dotted world map, a terminal, a line chart) in pale cards with mono-capital tags; blog pictures reuse the arcs with a white line icon (desktop-scroll-25.jpg, sheet-desktop.jpg).

**Motion behaviour**
- [M] Load, desktop (times after the sampler began, 296 ms after navigation): the first reveal is at 2679 ms; list items without text travel 82 px in 275 ms inside a clipped parent (15 `li` in all), the canvas fades in at 2687 ms (267 ms), and the seven h1 blocks fade for 100 ms each with a 34 ms gap; the h1 settles at 3054 ms, the last reveal at 3320 ms. LCP 3000 ms on the h1 (lab, one run).
- [M-seen] desktop-load-0.35s.jpg and desktop-load-1.25s.jpg show a small pink mark centred on the dark ground; at 1.25 s one h1 word is faintly visible in its final place; desktop-load-3.5s.jpg shows the finished first screen. [I] The 82 px travel equals the bar height, which fits the navigation items dropping in from above.
- [M] Load, phone: the same parts start at 276–392 ms (travel 72 px in 269 ms; bar height 72 px); the lede and a button fade from 0.02 over 550 ms while rising 38 px; the h1 settles at 908 ms; LCP 688 ms. [I] The long desktop hold is a loader waiting on something the phone run did not wait for; one run each, so the gap is indicative only.
- [M] Scroll reveals, desktop: 24 — 21 fades (267 / 350 / 350 ms) and 3 travels of 9–12 px upward in 183–217 ms inside a clipped parent; kinds: li 17, h2 › span 4, p 3; one staggered group, gap 67–101 ms. Labels fade for 267–358 ms; tag items on the case cards rise 9–12 px; feature-list rows fade for about 350 ms.
- [M] The three statement paragraphs read as fades of 15–18 ms: a one-frame switch, an artefact; what moves inside them was not captured.
- [M] Held: 6 elements for about 3 screens (3.2 in the examples) — the label and the index titles of the feature run; 10 elements fixed throughout. [M-seen] The active title is in dark ink and the other three pale (desktop-scroll-25.jpg).
- [M] Parallax, sideways movement and scale: none on desktop.
- [M] Smoothing: median lag 1016 ms against a baseline of 0 (desktop); `lenis` detected; lag 0 on the phone.
- [M] Pointer: on a filled button an inner element changes transform and opacity; on the logo link an inner element changes width; a navigation link changes nothing readable; cursor `auto`. [M-seen] The bar is absent from desktop-scroll-25.jpg, -50, -75 and -100 although it is position fixed. [I] It leaves the view while the page scrolls down.
- [M] Reduced motion: 25 load reveals with the preference set, 24 without; 4 animations running in both — not reduced on load. One reduced-motion rule found (3 stylesheets, all readable).
- [M] Declared: transitions of 0.2 s (260 elements), 0.4 s (35), 0.3 s (26), 0.25 s (7), 0.6 s (5), 0.8 s (4); easings cubic-bezier(0.645, 0.045, 0.355, 1) (181) and cubic-bezier(0.4, 0, 0.2, 1) (158); 5 elements with keyframes.

**Responsive transformations**
- [M] Type: h1 86.1 → 45 (×0.52); statements 72.6 and 57.4 → both 40; h2 43.9 → 25; block heading 36.1 → 25; sub-heading 26.5 → 20; body 18 → 17; lede 17 → 16; mono labels stay 13.
- [M] h1 at x 0.038, y 0.567, width 0.923, three lines; text reaches y 0.953; the canvas still fills the screen. [M-seen] The lede and buttons move under the h1 and a square play button appears above it (mobile-scroll-0.jpg).
- [M] One left edge at 0.04 carries 50 blocks; declared grids 2 columns ×4, 6 ×2; paragraphs run 33–45 characters per line at 21.2 em (360 px).
- [M] 14 blocks: 1.58, 0.21, 0.9, 0.68, 0.87, 0.71, 1.42, 0.32, 0.87, 0.15, 0.59, 0.97, 0.65, 1.06. The feature run is four stacked blocks (0.9, 0.68, 0.87, 0.71) with 25 px sub-headings; the four 43.9 px index titles are not in the phone type reading; held elements 0.
- [M] Pictures listed 11 → 4: the feature picture is 360×496 (share 0.92, ratio 0.73); blog pictures are 298×251 (ratio 1.18, uncut, share 0.76) at x 0.038, 0.84, 1.66 — a sideways row.
- [M] Navigation: menu button false → true; bar 82 → 72 px; buttons 54 → 42 px high. [M-seen] The bar shows the logo and a menu control (mobile-scroll-0.jpg).
- [M] Motion: 35 scroll reveals (21 fades of 267–350 ms; 14 travels of 11–25 px upward; kinds li 14, img 7, p 6, h2 › span 4, h3 4); 2 images move sideways with the scroll at -0.16 px per px, 3 drift; six text widths settle from 219 to 228–230 px. [I] That last reading is a layout settling, not a designed scale. [M] Ground shares 0.48 / 0.31 / 0.21.

**Surfaces**
- [M] 27 filled or framed boxes: radius 10px ×13, 0 ×10, 15px ×4; 0 shadows; 2 hairlines. Buttons: radius 7px, 54 px high, three fills — pink 255,72,139 with ink 16,20,33 (×4), a dark fill at 0.35 alpha with white ink (×3), pale 207,215,231 with ink 23,43,118 (×1); no outlined buttons (desktop, surfaces).
- [M-seen] The light sheets end in large rounded corners against the dark bands (desktop-scroll-50.jpg, desktop-scroll-100.jpg); that radius is not among the readings. A hairline separates the footer's legal row (desktop-scroll-100.jpg).

**Reusable principles [I, each with its evidence]**
1. Give each ground a job and change ground with the kind of content, not with every section. Evidence: three grounds, four changes over 12.08 screens; dark for hero, security and footer, white for the feature run, pale for cases, list and blog (desktop, sections; sheet-desktop.jpg).
2. Separate voice from interface by face: a light display for statements, mono capitals for anything that labels or is clicked. Evidence: weight 300, tracking -0.025 to -0.05 em at 43.9–86.1 px; 13 px mono uppercase on navigation, buttons, h2 labels and tags; body in a third face at +0.01 em.
3. Set the headline low and to one side of a full-screen backdrop, with the supporting text as a small second column. Evidence: h1 at y 0.622, width 0.465; 560 px above the content; canvas share 1.0; lede 19.1 em wide.
4. For a run of parallel features, hold a short index and scroll the proofs past it; on a phone, stack them. Evidence: 6 elements held about 3 screens in a 3.52-screen block; picture column from 0.507; phone: 0 held, four blocks of 0.68–0.9 screen.
5. Keep reveals short and nearly still. Evidence: scroll fades 267–350 ms; travels 9–12 px on desktop, 11–25 px on the phone; declared transitions mostly 0.2 s (260 elements).
6. Spend the accent on actions and on one phrase per statement. Evidence: pink fill on 4 buttons; pink ink on 0.03 of characters; a gradient phrase seen in three statements.

**Against our existing record**
- [M] Sizes agree: record display 86 px, weight 300, -0.025; h2 44; h3 36; label 13 uppercase; today 86.1, 43.9, 36.1, 13. The record names the display face "ABC Favorit"; the page loads it as "ABC Favorit Trial". The record's body is 17 px; today 18 px carries more paragraph text (773 characters against 423).
- [M] The record has no level for the statements (72.6 and 57.4 px, set as paragraphs) nor for the 26.5 px sub-heading that carries the most characters.
- [M] Record: 9 sections over 14.2 screens of 756 px (pacing 1.85, 4.18, 0.79, 0.47, 0.76, 0.93, 0.7, 0.87, 1.18); today 13 blocks over 12.08 screens of 900 px. The pinned run is 4.18 screens in the record, flagged but "not measured"; today 3.52 screens with 6 elements held about 3 screens.
- [M] The record's surface is "dark" (#101421) and its blueprint lists every band as "paper"; today that ground covers 0.42 of the page and the two light grounds 0.58 together, in four changes. [I] "dark-page" holds only as "largest single ground".
- [M] Not in the record: the phone view, the load sequence and loader hold, the smoothing lag, reveal timings, the reduced-motion result.

**Not measurable here** — What the canvas does under the pointer or a press (a ring with a short hint is visible near the top-left of sheet-desktop.jpg only); whether labels scramble (the type reading lists four `c-scramble-text` elements, no such motion was captured); the carousel and the segmented tabs in use; the rule by which the bar hides; where the 144 px letters appear; the radius of the sheet corners; whether the desktop logo row moves; reduced motion while scrolling; the phone menu when open; motion at the end of the phone page (step limit); the page with the consent banner answered; field timings.

### C.3 deepbook — https://deepbook.tech/

**Measured**: [M] status 200 in both views after a redirect (`final_url` https://deepbook.xyz/); 8.97 screens at 1440×900, 9.32 at 390×844; `failed` empty, `input_ignored` null; both scroll runs took 14 steps, under the step limit.

**Creative thesis [I]** — The opening argument is a film: the first screen carries no page text under the bar and the headline lives inside the video. Below it the page is a plain squared document in one bold grotesque, where character comes from a single picture language — black-and-white halftone cut-outs on flat blue — and from grounds that change with the job of the section. What carries it: a playing video takes 0.9 of the first screen and there is no h1 (desktop, first_screen, headings); one family in two weights with tracking 0 (desktop, type); 12 of 13 boxes have radius 0, with 13 hairlines, no shadows and no rounded pictures (desktop, surfaces, pictures); blue 30,110,243 is the ground of 0.24 of the page and of every button (desktop, colour, surfaces).

**Typography system**

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| h1 | none on the page | — | — | — | — | — | — |
| Largest display (h2) | PP Mori | 71.2 (4.94) | 700 | 0 | 1.05 | none | 40.0 |
| Section heading (h2) | PP Mori | 52.8 (3.67) | 700 | 0 | 1.08 | none | 32.0 |
| Figures (span) | PP Mori | 41.8 (2.90) | 700 | 0 | 1.0 | none | 32.0 |
| Product name (h2) | PP Mori | 36.0 (2.50) | 700 | 0 | 1.15 | none | 24.0 |
| Sub-heading (h3) | PP Mori | 26.6 (1.85) | 700 | 0 | 1.3 | none | 18.0 |
| Question (h3) / lede (p) | PP Mori | 22.0 (1.53) | 700 / 400 | 0 | 1.4 / 1.5 | none | 18.0 |
| Body | PP Mori | 18.0 (1.25) | 400 | 0 | 1.6 | none | 16.1 |
| Body, small | PP Mori | 16.0 (1.11) | 400 | 0 | 1.6 | none | 16.0 |
| Navigation (header links) | PP Mori | 16.0 (1.11) | 400 | 0 | 1.5 | none | absent |
| Label, footer | PP Mori | 14.0 (0.97) | 400 | 0 | 1.5 | none | 14.0 |

- [M] One family (families_loaded), two weights (700 and 400), tracking 0 and no uppercase transform at every size; no italic in page text.
- [M] No h1 (headings.h1 null); ten h2. Largest page text ÷ body = 71.2 ÷ 16 ≈ 4.5 (the 16 px style carries the most characters, 1907) and ÷ 18 ≈ 4.0. Nine sizes carry text.
- [M] Line length: 49–79 characters per line — 16 px at 69 (41.3 em, 661 px), 18 px at 79 (47.7 em, 859 px), the 22 px lede at 59 (37.8 em), 14 px at 79 (49.6 em) (desktop, paragraphs).
- [M] Two heading styles are split into single characters: the 52.8 px style counts 48 elements for 48 characters, the 71.2 px style 32 elements for 35 characters; scroll reveals list 71 'h2 › div'.
- [M] Grey 106,118,129 sets 0.57 of all characters, black 0.17, white 0.16 (desktop, colour.inks). [M-seen] Headings and bold labels are black, running text grey (desktop-scroll-25.jpg, desktop-scroll-50.jpg).
- [M-seen] The headline is drawn inside the video frames, two bold lines and a lighter third (desktop-load-3.5s.jpg), with an italic word in a later frame (desktop-scroll-0.jpg); the tool cannot read its size or face.

**Layout geometry**
- [M] Left edge at 0.06 (17 blocks; section text 0.056–0.944); then 0.39 (11 blocks, the FAQ column), 0 (6, bleeding pictures), 0.51 (6), 0.80 (5), 0.31 (4) (desktop, alignment.edges). Declared grids: 2 columns ×9, 6 ×6, 4 ×3, 3 ×2.
- [M] First screen: a sticky black bar 89 px high with 5 links and one filled button; below it a picture box from y 0.099 covering 0.9 of the screen; page text spans only y 0.024–0.073.
- [M] Centred text share 0.02 — only the closing call is centred (text 0.227–0.773).
- [M] Text columns per section: 0, 0, 4, 4, 1, 1, 2, 1, 5 (the 4s are two cards side by side; 5 is the footer). The custody section narrows its column to 0.144–0.741.

**Section rhythm**
- [M] 9 sections: 0.9, 0.52, 1.22, 1.01, 0.36, 1.61, 1.12, 1.21, 0.93 screens (desktop).
- [M] The longest, 1.61 at 4.10 screens, holds a paragraph, a six-row table and a 1024×484 picture; the shortest, 0.36, is a black band with a bleeding picture and a heading on it.
- [M] Grounds in order: black (video), white ×3, black (picture band), a pale grey (color(srgb 0.956 0.964 0.969)), white, blue 30,110,243 ×2 — five changes; area shares white 0.44, blue 0.24, pale 0.18, black 0.14.
- [M] Space above / below content: median 126 / 71 px; 126 px above recurs on three sections; 250 px below the product cards; -1 and -35 are artefacts.
- [M] Characters per screen: 0, 199, 532, 504, 146, 230, 602, 31, 325 — the film and the closing call are nearly wordless; the product cards, the API section and the FAQ are the dense ones.
- [I] Film, figures, then a steady alternation of explanation and picture-statement at about one screen each, ending on a quiet full-colour call.

**Image treatment**
- [M] 12 pictures listed (desktop), fewer distinct ones: the hero is an img and a video in the same 1440×810 box and the footer picture is three stacked 1440×496 layers. 6 bleed, 4 cropped, 0 rounded, 0 shadow, no filter, blend or mask, 4 with words on them, 1 video — playing.
- [M] Ratios and shares: 1.78 (hero, share 1), 1.59 (two product pictures 624×393, share 0.43 at x 0.056 and 0.511, cut from own 1.79), 4.0 (the 1440×360 band, cut from own 2.36), 2.11 (1024×484, share 0.71 at x 0.144), 0.82 (a 320×392 cut-out), 1.03 (544×529, share 0.38, centred), 2.9 (footer, share 1).
- [M-seen] Every still is a black-and-white photograph with a visible halftone screen, either cut out and set on flat blue (a suited figure with a labelled box for a head, hands snapping a labelled bar, an open book with a figure inside, a crowd seen from behind along the footer) or used as a monochrome band (a safe dial, a row of keys) (sheet-desktop.jpg, desktop-scroll-75.jpg, desktop-scroll-100.jpg).
- [M-seen] The film changes subject: a photographic interior with a person at a laptop (desktop-load-0.35s.jpg, -1.25s, -3.5s), a blue wireframe scene with a chapter counter and a progress line at the lower right (desktop-scroll-0.jpg), a white line-drawn mark on blue (sheet-desktop.jpg).
- [M] The action in the closing section is a 230×119 image. [M-seen] It pictures a physical key-cap button (sheet-desktop.jpg).

**Motion behaviour**
- [M] Load: no reveals in either view (0 elements); 0 animations running; the only movement on the first screen is the playing video. LCP 252 ms on an img (desktop), 352 ms (phone); 28 requests and 10,168,738 bytes transferred (desktop, lab, one run).
- [M] Scroll, desktop: 129 reveals — 119 fades (quartiles 17 / 17 / 184 ms), 31 travels of 10–16 px upward in 200–350 ms, 8 inside a clipped parent; kinds: h2 › div 71, h3 › div 25, li 16, h3 5, p 5, h2 › span 3, h2 2, img 2; 21 staggered groups, gap 50 ms (50 / 50 / 66).
- [M] The 17 ms fades are one-frame switches, not fades: the split characters turn on one after another about 50 ms apart. [I] A type-on effect.
- [M] Whole blocks fade and rise together: product names 383 ms with 10 px in 250 ms; list rows 431–483 ms with 14–16 px in 350 ms, the rows of a card starting about 150–170 ms apart (examples at 3133, 3280, 3447 ms).
- [M] One sub-heading reads a 38 px travel over 2799 ms inside a clipped parent, far longer than the rest. [I] Probably tied to the scroll rather than timed.
- [M] Scale: one picture settles from 1060 to 1024 px wide (desktop), another from 362 to 351 px (phone). Parallax: none on desktop, one image at rate -0.06 on the phone. 3 elements drift sideways by themselves in both views; which ones is not recorded.
- [M] Held: none; `sticky_inside` 0 in every section; `fixed_throughout` 0. [M-seen] The bar is at the top of all five scroll screenshots; the sampler does not follow its parts.
- [M] No smoothing: lag 0 against a baseline of 0; no animation or scroll library detected.
- [M] Pointer: the filled button darkens from 30,110,243 to 20,93,217 and gains a hard shadow (0 5px 0, black at 0.24 alpha) over 0.2–0.22 s; a bar link goes from 218,224,229 to white together with its top border.
- [M] Reduced motion: 0 load reveals with or without the preference, so the test shows nothing; 6 reduced-motion rules in 4 readable stylesheets.
- [M] Declared: transitions of 0.18 s (10 elements), 0.24 s (6), 0.22 s (4), all `ease-out`; no keyframes.

**Responsive transformations**
- [M] Type: 71.2 → 40 (×0.56), 52.8 → 32 (×0.61), figures 41.8 → 32, 36 → 24, 26.6 → 18, 22 → 18, body 18 → 16.1; 16 and 14 unchanged.
- [M] The film keeps its ratio (390×219, 1.78) and takes 0.26 of the first screen instead of 0.9. [M-seen] The four figures, in a 2×2 grid, share the first screen (mobile-scroll-0.jpg).
- [M] 10 sections: 0.26, 0.62, 0.86, 0.78, 1.28, 0.45, 1.27, 1.39, 0.87, 1.17; the two product cards become two stacked blocks (0.86 and 0.78).
- [M] One left edge at 0.05 carries 45 blocks; paragraphs are 350 px wide, 35–53 characters per line (19.4–25 em); declared grids 2 columns ×9, 3 ×6, 5 ×3.
- [M] Pictures are re-cut, not shrunk: the band goes from ratio 4.0 to 0.94 (390×414), the footer from 2.9 to 1.02 (390×384); product pictures go to share 0.9.
- [M] Bar 89 → 77 px, links 5 → 2, no menu button in either view. [M-seen] The phone bar shows only the logo and the button; the three text links are gone (mobile-scroll-0.jpg).
- [M] Motion kept: 109 reveals (h2 › div 78, li 16), 21 travels of 10–13 px, 21 groups at 50 ms, lag 0.

**Surfaces**
- [M] 13 filled or framed boxes: radius 0 ×12, 8px ×1; 0 shadows; 13 hairlines (15 on the phone); 2 gradients. Buttons are blue 30,110,243 with white ink: radius 4px at 52 px high (×2) and at 44 px (×1), and one square one, radius 0, 48 px; no outlined buttons.
- [M-seen] List rows and table rows are white boxes with a thin pale border and square corners; the table sits in a white panel on the pale ground; FAQ rows are divided by hairlines with a square toggle at the right, filled blue on the open row (desktop-scroll-25.jpg, -50, -75; sheet-desktop.jpg).

**Reusable principles [I, each with its evidence]**
1. If the opening is a film, let it carry the headline alone and follow it at once with facts. Evidence: video over 0.9 of the first screen with no page text below the bar; the next section is four figures at 41.8 px in 0.52 screen; on the phone the film takes 0.26, so the figures share the first screen. A page built this way has no h1 in its markup (headings.h1 null), which ours would have to supply.
2. One family, two weights, no tracking: hierarchy from weight and size, with grey for running text. Evidence: PP Mori only; 700 on every heading, figure and bold label, 400 on text; tracking 0 at all nine sizes; grey ink on 0.57 of characters.
3. Commit to one picture treatment and one accent ground, so every picture belongs to one set. Evidence: all stills monochrome halftone, on blue or as mono bands (sheet-desktop.jpg); 0 rounded, 0 shadowed, no filter or blend recorded — the treatment is in the files; blue is the ground of 0.24 of the page and of every button.
4. Square, hairline-framed rows as the only container. Evidence: radius 0 on 12 of 13 boxes; 13 hairlines; 0 shadows; buttons at radius 4px.
5. Change ground with the job of the section. Evidence: five changes in nine sections — white for explanation, a 0.36-screen black picture band, pale for the table, blue for the call and footer.
6. Keep motion native and small. Evidence: lag 0; rises of 10–16 px in 200–350 ms; block fades 383–483 ms; characters 50 ms apart; transitions 0.18–0.24 s ease-out; 6 reduced-motion rules; nothing held.

**Against our existing record**
- [M] The record describes a different page. It holds one family "TWKEverett" at 102 / 81 / 48 px, weight 500, tracking -0.02 to -0.03; today one family "PP Mori" at 71.2 / 52.8 / 36 px, weight 700, tracking 0.
- [M] Record: dark surface #000000, 8 sections over 13.3 screens of 756 px, a 5-screen "pinned-features" section, a canvas hero, GSAP, ScrollTrigger, Lenis and WebGL present, a relative bar 53 px high. Today: white is the largest ground (0.44) and black 0.14; 9 sections over 8.97 screens of 900 px; nothing held; a video hero; none of those libraries detected; a sticky bar 89 px high.
- [I] The record's principles "tight-tracking", "type-led" (0 of 8 sections with a large still), "pinned-sections" and "dark-page" do not hold for the page served now. What persists: the blue #1e6ef3 (30,110,243), a 4 px button radius, a single family.
- [M] The record already carried a caveat that its profile came from another address than its blueprint; today the blueprint's address redirects to a third.
- [M] Not in the record: anything about the present page, including the phone view and the picture language.

**Not measurable here** — The film's length, chapter timing, loop and whether it autoplays on real phones; the size and face of the headline inside it; the accordion and the three tabbed panels in use; which three elements drift and which image has the phone parallax; reduced motion during scrolling (the test covers the first 6 s, where nothing reveals); what the original address served before the redirect; the page with a consent banner answered; field timings (one lab run).

### C.4 tengile — https://tengilemalamala.com/

**Measured**: status 200 in both views; 12.83 screens at 1440×900 and 14.98 screens at 390×844; `failed` is empty and no input was ignored (wheel and touch both moved the page); the phone scroll run stopped after 8178 px, so roughly the last third of the phone page was not sampled in motion.

**Creative thesis [I]** — One paper-coloured ground from top to bottom on which scale does the work: a single very large, very light uppercase heading over a full-screen video, then statements set as large paragraphs, then pictures whose width and ratio change from section to section, with almost no interface drawn. Carried by: 12 of 13 sections share one ground (desktop, sections); the h1 is 120 px at weight 220 and the next size in the same face is 48 px (desktop, type); all eight h2 are 14 px labels (desktop, headings); every box and picture has radius 0 and there are no shadows, hairlines or gradients (desktop, surfaces).

**Typography system**

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Largest display = h1 | PP Fragment | 120 (8.33) | 220 | −0.02 | 0.9 | upper | 48.8 |
| Statement (p) | PP Fragment | 48 (3.33) | 220 | 0 | 1.1 | none | 24 (statement), 32 (quote) |
| Sub-statement (p, one h2) | PP Fragment | 32 (2.22) | 310 | 0 | 1.15 | none | 28 |
| Card title (h3) | PP Fragment | 20 (1.39) | 310 | 0 | 1.2 | none | 18 |
| Hero lede (p) | PP Fragment | 18 (1.25) | 310 | 0 | 1.1 | none | 18 |
| Body, menu and footer links | Inter | 16 (1.11) | 400 | −0.01 | 1.25 | none | 16 |
| Section label (the h2s), menu button | Inter | 14 (0.97) | 500 | −0.01 | 1 | upper | 14 |
| Button and link label | Inter | 14 (0.97) | 500 | −0.02 | 1 | none | 14 |

- [M] Two families loaded: PP Fragment and Inter (both views, families_loaded). [M-seen] The first is a light serif, the second a plain sans (desktop-scroll-0.jpg, desktop-scroll-25.jpg).
- [M] Display ÷ body = 120 ÷ 16 = 7.5 at 1440 and 48.8 ÷ 16 ≈ 3.05 at 390 (type).
- [M] Seven sizes carry text at 1440 (120, 48, 32, 20, 18, 16, 14) and seven at 390 (48.8, 32, 28, 24, 18, 16, 14) (type).
- [M] Line length at 1440: the 48 px statement 60 characters per line at 29.3 em; the 32 px paragraphs 40–42 at 21.8 em; the 16 px body 56–57 at 28.7 em (desktop, paragraphs). At 390: 30 characters at 14.9 em (24 px), 22–24 at 12.8 em (28 px), 42–44 at 22.4 em (16 px) (mobile, paragraphs).
- [M] The h1 is 18 text nodes for 18 letters, two words on two lines, `nowrap`; all 8 h2 are one-line 14 px labels of about two words; the long text is `p` at 48 and 32 px; no italic style appears in the readings (desktop, type.where, headings).

**Layout geometry**
- [M] Most blocks start at 0.01 of the width (20 blocks); other shared edges at 0.51 (11), 0.34 (10), 0.18 (6), 0.67 (3), 0.75 (3) (desktop, alignment.edges). At 390: 0.04 (41 blocks), 0.07 (6), 0.52 (5).
- [M] Declared grids: 12 columns ×13 and 6 columns ×1 at 1440; 4 columns ×11 and 2 columns ×3 at 390 (alignment.grids_declared).
- [M] h1 on the first screen: x 0.011, y 0.264, width 0.978, height 0.268, 2 lines, start-aligned (desktop, first_screen.h1). [M-seen] Its first line is indented and its second line steps further right, so the two words form a diagonal (desktop-scroll-0.jpg).
- [M] The largest picture on the first screen is the video, covering 1.0 of the screen; text spans y 0.004–0.781 (desktop, first_screen).
- [M] Centred text share is 0 in both views. [M-seen] One 32 px heading stands in the middle of the page between small pictures (desktop-scroll-75.jpg); it is centred by placement (text x 0.374–0.626), not by alignment.
- [M] Text columns per section in order: 2, 2, 1, 1, 3, 3, 1, 0, 3, 2, 1, 1, 4, median 2 (desktop, sections); median 1 at 390.

**Section rhythm**
- [M] 13 sections at 1440; heights in screens: 1, 0.33, 1.28, 0.46, 0.94, 0.92, 0.57, 0.92, 1.01, 0.98, 1.24, 1.41, 0.56 (desktop, sections). There is no long section; the tallest (1.41) is the closing picture with text on it.
- [M] Grounds: rgb(245,238,233) for the first 12 sections and rgb(92,110,33) for the footer, one change, shares 0.95 and 0.05 (desktop, colour.grounds). Three of the 12 have a picture as ground (hero, slider, closing picture).
- [M] Space above/below content: median 16/16 px; the quote 80/158; the story section 96/32; the closing picture 702/136, its text sitting low on the picture. The −101 and −2 px readings are pictures overlapping the top of their section box: artefacts.
- [M] Characters per screen in order: 151, 1085, 158, 936, 543, 462, 388, 16, 360, 63, 204, 262, 1013 (desktop, sections).
- [I] Short text-only strips of a third to half a screen alternate with picture sections of about one screen: read one statement, look, repeat; nothing holds the reader in place.

**Image treatment**
- [M] 32 pictures at 1440: 1 video (playing), 3 flagged as bleeding, 3 cropped, 0 rounded (all radii 0px), 0 shadows, 0 filters, 0 blends, 0 masks, 2 with words on them (desktop, pictures).
- [M] Frames in use: six cards 514×625 (ratio 0.82, width share 0.36); a pair at 0.79 (share 0.45) and 0.83 (share 0.54); a pair at 0.68 and 1.0 (share 0.26 each); four at 0.9 (share 0.14); 15 pictures 520 px wide at ratios 0.72–1.21 laid in a row from x −1.418 to 3.248; a slider picture at 1.78 (share 1.1); the closing picture at 1.13 (share 1.12); the hero video at 1.6, cover-cropped from an own ratio of 1.78.
- [M] Picture elements are larger than their frames: the cards are 514 px wide while the text column under them is 459 px wide (pictures, paragraphs), and the slider and closing pictures have width shares above 1. [M-seen] In desktop-scroll-50.jpg the slider picture keeps the page's side margin, so its "bleeds" flag reflects an oversized element in a clipped frame; the closing picture does run edge to edge (desktop-scroll-100.jpg).
- [M] 31 CSS background pictures are also counted (desktop, surfaces); the reading does not say where they sit.
- [M-seen] Subjects are landscape, animals, lodge exteriors and staff portraits; placements are a pair of unequal pictures with offset tops, rows of three equal upright pictures with the title under each, four small pictures scattered around a heading, and a row of upright pictures cut by the right edge (sheet-desktop.jpg).

**Motion behaviour**
- [M-seen] On load the screen is a flat olive ground with a small white mark in the centre at 0.35 s and 1.25 s; at 3.5 s the hero is complete (desktop-load-*.jpg).
- [M] Load reveals start at about 1906 ms: the lede fades in 484 ms; the video travels 40 px in 600 ms and settles from 1584 to 1440 px wide; the 18 h1 letters each rise 104 px inside a clip without fading, 715–717 ms each, 50 ms apart, in two groups that start together; the h1 settles at 3022 ms, about 3.2 s after navigation with `began_ms` 141 (desktop, load).
- [M] An "h1 › span" width change from 1408 to 1169 px is logged as settling. [I] That is the heading being re-laid as split letters, an artefact and not a scale effect.
- [M] Smoothing: scroll lag median 990 ms against a baseline of 0, Lenis present (desktop); lag 0 on the phone.
- [M] Hero on scroll: the video is held for 1.0 screen and the h1 with its parts (25 elements) moves at rate 0.53 (desktop); at 390 the same at rate 0.5 (35 elements, quartiles 0.04/0.5/0.5).
- [M] Scroll reveals: no fades in either view. At 1440 there are 36 travels: 5 pictures moving 24–174 px over 617–2116 ms inside clipped frames at 18.9–20.4 s of the run, and 31 footer items (21 li, 6 p, 3 buttons, 1 h3) all moving 12 px over 1836 ms together at 27.9 s. [I] Both read as scroll-tied offsets that keep easing after the wheel stops, not timed entrance reveals; by their timing the 5 pictures belong to the story and scatter sections.
- [M] Sideways: one picture moved 0.31 screen widths at 0.42 px per px scrolled and three elements drifted sideways on their own (desktop, scroll.sideways); one element drifted during load. Scale with scroll: 0.
- [M] Pointer: the two top links change colour from rgb(245,238,233) to rgb(227,225,212), with a pseudo-element border, over 0.3 s; cursor `auto`. [M-seen] A small label ("Play Video" on the hero, "Next" on the slider) sits where the pointer was parked in the middle of the viewport (desktop-scroll-0.jpg, desktop-scroll-50.jpg).
- [M] Reduced motion: 21 reveals on load against 20 normally, 1 animation running in both, 0 reduced-motion rules in 11 readable stylesheets; the load sequence is unchanged.
- [M] Declared transitions: 0.3 s ×95, 0.4 s ×26, 1.6 s ×18, 0.6 s ×4, 0.5 s and 0.8 s ×2 each, 1 s and 2 s ×1 each; easings `ease` ×93, cubic-bezier(0.19, 1, 0.22, 1) ×45, three other curves ×9 together; 2 elements with keyframes, 1 running.

**Responsive transformations**
- [M] Page 12.83 → 14.98 screens; sections 13 → 19, because each card row becomes a header plus three stacked blocks of 0.56 screens.
- [M] Type: h1 120 → 48.8 px (×0.41; 8.33 → 12.5 vw); the 48 px tier splits into 24 px (statement) and 32 px (quote); 32 → 28; 20 → 18; 18, 16 and 14 px unchanged.
- [M] Columns: grids 12 → 4; median text columns 2 → 1; main left edge 0.01 → 0.04.
- [M] Navigation: a menu button in both views; the bar is 34 px high at 1440 and 48 px at 390, `absolute` in both, and nothing is fixed throughout.
- [M] Pictures: cards keep ratio 0.82 one per row; the hero video is 0.46, cover-cropped from an own ratio of 0.56 (1.78 at 1440); the slider picture is 0.8 from an own 0.83 (1.78 at 1440); the closing picture is cropped to 0.46 from 1.14; 6 pictures carry words against 2. [M-seen] Small white tags sit on the card pictures (sheet-mobile.jpg).
- [M] 11 pictures are flagged as bleeding at 390; nine of them are 401 px wide at x −0.014. [M-seen] Those nine keep side margins on screen (mobile-scroll-50.jpg), so the flag is the oversized-element artefact again.
- [M] Motion kept: the load sequence (letters rise 40 px in 517–533 ms, 50 ms apart, h1 settles at 2795 ms), the held video, the h1 rate. Dropped: smoothing. Not observed: any picture travel, the picture row and the footer, which lie beyond the 8178 px the run covered.

**Surfaces**
- [M] 29 filled or framed boxes at 1440, all radius 0px; 0 shadows, 0 hairlines, 0 gradients, 0 outlined buttons, no filled buttons (desktop, surfaces). At 390 two filled buttons appear: ground rgb(120,136,67), ink rgb(251,248,246), radius 4px, 40 px high, 14 px uppercase. [M-seen] They are the two collapsed link groups of the footer (mobile-scroll-100.jpg).
- [M-seen] Small white square-cornered label-and-arrow buttons are visible on the hero and the closing picture (desktop-scroll-0.jpg, desktop-scroll-100.jpg). [M] The readings count 0 filled buttons on the first screen, so reading and screenshot disagree here.

**Reusable principles [I, each with its evidence]**
1. Let one heading own the scale and keep everything else at reading size. Evidence: 120 px h1 against a next size of 48 px; display ÷ body 7.5; eight h2 at 14 px.
2. Use the heading element as a small label and set the statements as large paragraphs with a measured line. Evidence: h2 = 14 px uppercase weight 500; statements in `p` at 48 and 32 px running 60 and 40–42 characters per line.
3. Hold the ground constant and make rhythm from text density and picture size. Evidence: one ground for 12 of 13 sections; characters per screen 1085, 158, 936, 543 in succession; no radius, shadow, hairline or gradient.
4. Change picture width and ratio from section to section instead of repeating one frame. Evidence: width shares 0.14, 0.26, 0.36, 0.45, 0.54, 1.1; ratios 0.68 to 1.78; two pairs of unequal size.
5. Animate the heading once, by letters inside a mask, and give the rest of the page no entrance effects. Evidence: 18 letters, 104 px masked rise, 50 ms apart, settled at 3022 ms; 0 fades on scroll in both views.
6. On a phone, shrink the display far more than the text. Evidence: h1 ×0.41 while 32 → 28 px and 16, 14 px stay.

**Against our existing record**
- The record and today agree on 13 sections, the display style (120 px, weight 220, −0.02 em, leading 0.9, uppercase), the 48/32/16/14 px steps, Lenis and a marquee keyframe; the record's 15.1 screens were taken at a 756 px high capture against 12.83 at 900, so its section heights are not comparable one to one.
- The record has no 20 px card-title or 18 px lede role, no tracking for Inter (−0.01, −0.02), no line lengths and no phone values (`mobile` is "missing").
- The record lists scroll, pinning, sequence, interaction and reduced motion as not measured; today adds the loader screen, the letter sequence, the held video, the h1 rate 0.53, the 990 ms lag, the pointer colours and the unchanged reduced-motion run. Its note of a "blur+scale" picture reveal is not confirmed: no fade or width settling was read on scroll, and the sampler does not read blur.
- The record's hero medium is `bleed: false`, width 0.99, ratio 1.88; today the video covers the screen (share 1, ratio 1.6, cover-cropped from 1.78). The recipe's button (48 px high, radius 999) matches nothing read or seen today.

**Not measurable here**: blur, clip-path or filter changes (the sampler reads position, width and opacity); motion on the phone past 8178 px; which picture moves sideways with scroll and where the 31 background pictures are; the opened menu, the slider's change and hover on pictures (not triggered); the video beyond single frames; timings are one lab run.

### C.5 belgrade-arbor — https://belgradearbor.rs/en

**Measured**: status 200 in both views; 26.31 screens at 1440×900 and 30.27 at 390×844; `failed` is empty and no input was ignored; the scroll runs covered 10794 px (desktop) and 8185 px (phone), so nothing after about screen 13 (desktop) or 10.7 (phone) was sampled in motion, and the full-page captures and the −50/−75/−100 viewport shots are unreliable for this page.

**Creative thesis [I]** — The page is a run of full-screen chapters, each sized to the viewport and opened by one very large uppercase word laid over a full-bleed picture, with a long pinned stage near the top where the text is released word by word and a second long stage near the end for a view from above. Carried by: 10 of 14 sections are 1.00–1.01 screens (desktop, sections); chapter headings are 159.8 px, 11.1 vw (desktop, type); 57 elements stay in place for 8.0 screens inside a 9-screen section (desktop, scroll.held); 96 heading words fade in 633 ms each, 50 ms apart (desktop, scroll.reveals).

**Typography system**

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Largest display (one h2) | editorialOld | 239.8 (16.65) | 300 | 0 | 1 | upper | 95.9 |
| Chapter heading (h2) | editorialOld | 159.8 (11.10) | 400 | 0 | 1 | upper | 48 |
| h1 | editorialOld | 151.2 (10.50) | 400 | 0 | 1 | upper | 66.3 |
| Other headings (h2) | editorialOld | 127.9 (8.88), 119.9 (8.32) | 400 | 0 | 1 | upper | 48, 52 |
| Statement and lists (h2 words, p) | editorialOld | 55.9 (3.89) | 300 | +0.02 | 1.1 (lists 1) | none | 36 (statement), 40 (lists) |
| Menu links | editorialOld | 32 (2.22) | 300 | 0 | 1.25 | none | 32 |
| Label (p) | Work Sans | 20 (1.39) | 400 | +0.02 | 1.5 | upper | 20 |
| Body | Work Sans | 16 (1.11) | 400 | 0 | 1.2 | none | 16 |
| Button label | Work Sans | 14 (0.97) | 400 | +0.02 | 1.5 | upper | 14 |

- [M] Families loaded: editorialOld, Work Sans and the page's "Work Sans Fallback"; 39 footer text nodes compute to `ui-sans-serif` at 16 px (both views, type). [M-seen] The first is a serif, the second a sans (desktop-scroll-0.jpg, desktop-scroll-50.jpg).
- [M] Largest ÷ body = 239.8 ÷ 16 ≈ 15 and h1 ÷ body = 151.2 ÷ 16 ≈ 9.5 at 1440; 95.9 ÷ 16 ≈ 6 and 66.3 ÷ 16 ≈ 4.1 at 390.
- [M] 14 sizes carry text at 1440 (239.8, 159.8, 151.2, 127.9, 119.9, 99.9, 55.9, 51.9, 48, 32, 20, 18, 16, 14) and 11 at 390 (95.9, 66.3, 52, 48, 40, 36, 32, 20, 18, 16, 14); the type reading keeps the 7 largest styles and the 17 with most characters (tool, inspect.mjs), so rare small styles can be absent.
- [M] Every uppercase display size has tracking 0 and leading 1; only the 55.9 px mixed-case tier and the small uppercase sans carry +0.02; one 16 px uppercase link style carries +0.1; no negative tracking.
- [M] Line length: 16 px body 58–66 characters at 34.2 em (547 px) and 14 px text 30 characters at 20.2 em at 1440; 35–38 characters at 20.7 em (331 px) at 390 (paragraphs).
- [M] Uppercase headings are one text node per letter (13 for the h1, 40 for the three 159.8 px headings, 9 each at 239.8 and 127.9 px, 43 at 119.9 px) and the 55.9 px statement is split by word; the same face in italic at 55.9 px carries 235 characters (type.where). [M-seen] The italic marks the selected item of a list (sheet-desktop.jpg).
- [M] The 9 menu links exist twice, upright and italic, and button labels read doubled. [I] Two stacked copies for a swap on hover; the doubled words are an artefact of reading both.

**Layout geometry**
- [M] Main left edge at 0.04 (51 blocks); others at 0.53 (12), 0.55 (11), 0.46 (10), 0 (9), 0.63 (8); no declared grids in either view (desktop, alignment). At 390: 0.06 (28 blocks), 0.08 (20), 0 (11), 0.19 (10).
- [M] h1: one line, centre-aligned, x 0.039, y 0.743, width 0.922, height 0.168, so it ends at about 0.91 of the screen height; the video covers the whole first screen (desktop, first_screen).
- [M] The first-screen bar reading (431 px high, `static`, 9 links) is the menu panel, not the visible bar: artefact. [M-seen] The visible bar is a centred, dark, fully rounded strip that does not span the width, with a menu control left, a mark in the middle and an outlined button right, present in every viewport shot (desktop-scroll-0.jpg to -100.jpg). [M] 3 elements are fixed throughout the desktop run.
- [M] Centred text share 0.1 at 1440 and 0.05 at 390.
- [M] Text columns per section: 1, 3, 2, 6, 2, 1, 1, 1, 2, 2, 1, 1, 2, 2, median 2 (desktop, sections).
- [M-seen] The chapter word sits in a different place each time — bottom right, left middle, top left on two lines, bottom right — with a small rounded inset video and a 16 px text block in other corners (sheet-desktop.jpg). [M] The heading text starts at x 0.396 in the first opener and at 0.044 in the next two.

**Section rhythm**
- [M] 14 sections at 1440; heights in screens: 1, 9, 1, 1.19, 1, 1, 1.01, 1, 1, 1, 1, 4.96, 1, 1.16; ten are 1.00–1.01 (desktop, sections).
- [M] The long ones: the second (9 screens from 1.00; 636 characters, 71 per screen; 1 picture; a sticky element inside) and the twelfth (4.96 screens from 19.20; 19 characters; 4 pictures; 2661 px empty below its content).
- [M] Grounds by the reading: rgb(253,251,239) ×13 and rgb(49,71,89) ×1, two changes, shares 0.96 and 0.04; six sections have a picture as ground. [M-seen] The screenshots show more grounds than that: the pinned stage is dark green (desktop-scroll-25.jpg), one list sits on dark green and one opener on pale sand (sheet-desktop.jpg). [I] Those grounds are drawn by picture or canvas layers the ground reading does not see, so the ground sequence for this page is unreliable.
- [M] Space above/below content: median −20/60 px. The negative values (−117, −80, −180, −320, −799, −397) are overlap, not spacing: the four chapter pictures are 1440×1220 in sections 1.00 screen tall and start about a third of a screen above them (tops 9.66, 11.85, 13.85, 16.85 against 10.00, 12.19, 14.19, 17.20).
- [M] Characters per screen in order: 14, 71, 266, 1288, 284, 246, 248, 899, 176, 9, 1037, 4, 31, 670.
- [I] A title card, then a working screen (list, map, cards), repeated at one screen each; the two long stages slow the visit at the start, to read, and near the end, to look.

**Image treatment**
- [M] 38 pictures at 1440: 6 videos (4 playing when read; the hero video not flagged as playing), 8 bleed, 14 cropped, 4 rounded (radius 19.98px, the inset videos), 0 shadows, 0 filters, 1 blend (`multiply`, on the 1797×1195 background of the pinned stage), 3 masked, 12 with words on them (desktop, pictures).
- [M] Frames: four chapter pictures 1440×1220 (ratio 1.18) cropped from own ratios 1.5, 1.34, 1.0, 1.61; twelve cards 864×1080 (ratio 0.8, width share 0.6) at x 0.45, 1.05 … 7.05; four more 864×1080 stacked at x 0.45–0.7; a half-width picture 720×1220 (0.59); an image 3220×900 (ratio 3.58, width share 2.24) with three square images 1399–1798 px wide in the long late section; inset videos at ratio 1.78, 656–875 px wide when read. One inset reads 787×150 (ratio 5.25). [I] That one was caught mid-change: artefact.
- [M] 2 canvases at 1440, none listed at 390 (built_with). [M-seen] In the pinned stage two photographs sit in tilted four-sided frames with rounded corners (desktop-scroll-25.jpg); on the navy section three pictures in similar irregular rounded shapes overlap each other and cover part of the 239.8 px word (desktop-scroll-75.jpg). [I] The tilted frames of the pinned stage are probably canvas-drawn, since the readings list one picture in that section; canvas may render differently in a headless browser.
- [M-seen] Subjects are architectural renderings (facade, interiors, lobby), close fabric and curtain textures used as chapter grounds, and two lifestyle portraits (sheet-desktop.jpg). A small yellow vertical tab is fixed at the right edge of every viewport shot; it is ignored here.

**Motion behaviour**
- [M-seen] Load: a paper screen with a mark, a thin progress line and a percentage at 0.35 s and 1.25 s; at 3.5 s the bar over a thin line drawing on paper; the video and the h1 are present only in desktop-scroll-0.jpg, taken later.
- [M] Load readings: 0 reveals and no h1 settle time; a "100%" paragraph widening 40 → 67 px is the counter's text changing (artefact); a background image grows 1728 → 1788 px; 1 element drifts sideways (desktop, load). The LCP of 424 ms is a `p`. [I] That is the loader, so how the video and h1 arrive was not captured.
- [M] Smoothing: lag median 1189 ms against a baseline of 0, Lenis present (desktop); lag 0 on the phone.
- [M] Pinned stage: 93 elements held — 57 for 8.0 screens, 35 for 7.5, 1 for 4.0 (desktop, scroll.held); at 390 the section is 6 screens and 81 elements hold 5.0 screens, 11 hold 4.5.
- [M] Reveals inside it: 96 heading words fade in 633–634 ms each, 50 ms apart, in 8 groups; 14 elements also shift 8–12 px in 250–350 ms, 11 of them upward; 2 buttons fade with them (desktop). At 390: 97 words, fades 627–634 ms, 50 ms gaps, 45 travels of 13–30 px over 450–1133 ms.
- [M-seen] Words not yet released are blurred and dim, and a step number with a progress line sits bottom left (desktop-scroll-25.jpg). [I] The stage steps through several statements (three h2 are held), each released word by word.
- [M] Scale with scroll: a chapter picture goes 1584 → 1458–1469 px and an inset video 722 → 656 and 770 → 701 px (desktop, 4 elements); at 390 the same pictures go 429 → 390 px as "settling" and 4 elements show parallax at rates 0.14–0.25. No parallax or sideways movement was read at 1440 within the sampled part.
- [M-seen] The long late section appears in one frame only: a view from above filling the screen, its heading's last letters sharp and its first letters blurred out, a letter label over one wing (desktop-scroll-100.jpg, mobile-scroll-100.jpg).
- [M] Pointer: the menu control shows no change; the bar's button gains a translucent fill over 0.65 s; cursor `auto`.
- [M] Reduced motion: 0 reveals on load and 0 animations in both modes, 0 reduced-motion rules in 5 readable stylesheets. [I] No evidence either way, because nothing was detected on load normally.
- [M] Declared transitions: 0.65 s ×148, 0.5 s ×49, 0.6 s ×22, 0.3 s ×15, 0.22 s ×6, 0.7 s ×6; one easing, cubic-bezier(0.4, 0, 0.2, 1) ×246; no keyframes.

**Responsive transformations**
- [M] Page 26.31 → 30.27 screens; sections 14 → 19 by the reading, of which six are footer fragments and one (2.22 screens, no content) is a wrapper: artefact.
- [M] The stages change length: pinned stage 9 → 6 screens; the late long section 4.96 → 7.23; the navy section 1 → 4 screens with a sticky element inside (not reached by the phone run).
- [M] Type: largest 239.8 → 95.9 px (×0.40); h1 151.2 → 66.3 (×0.44), one line → two; chapter headings 159.8 → 48 (×0.30); statement 55.9 → 36 and lists 55.9 → 40; 32, 20, 16 and 14 px unchanged.
- [M] Body column 547 → 331 px; main edge 0.04 → 0.06 and 0.08.
- [M] Pictures: chapter pictures become 390×1164 (ratio 0.34) crops of the same landscape sources; cards 390×544 (0.72) at x 0, 1 … 11; a row of six rounded cards 331×160 (radius 17.99px) appears in the surroundings section; rounded pictures 4 → 10 and bleeds 8 → 15.
- [M-seen] Lists that show every item at 1440 show one item with a round chevron control at 390 (sheet-mobile.jpg); the bar keeps the mark and a two-line menu icon (mobile-scroll-0.jpg).
- [M] Kept: the pin and the word-by-word fades at the same 50 ms gap. Dropped: smoothing.

**Surfaces**
- [M] 0 filled or framed boxes, 0 shadows, 10 hairlines, 4 gradients at 1440; 25 hairlines and 6 gradients at 390 (surfaces).
- [M] Buttons are pills (computed radius 3.36e+07 px): 6 outlined; 1 filled sand rgb(204,191,153) with ink rgb(46,58,38), 56 px high, 14 px uppercase; 2 at 64 px high with a 40 % alpha dark fill. At 390: 8 outlined, 1 filled (48 px high). [M-seen] Two round translucent arrow controls sit on the card picture (desktop-full.jpg, residences screen). [I] These are the two 64 px readings.

**Reusable principles [I, each with its evidence]**
1. Size sections and cards to the viewport so that every stop is a composed screen. Evidence: 10 of 14 sections at 1.00–1.01 screens; cards 864×1080 at a 900 px high viewport and 864×907 in the record's 756 px high capture, the same share of the screen both times.
2. Open each chapter with one word at display size on a full-bleed picture and move the word to a different corner each time. Evidence: 159.8 px headings; four 1440×1220 pictures; positions seen in sheet-desktop.jpg; text start 0.396 against 0.044.
3. When text must be read slowly, hold the frame and release the words on a fixed beat. Evidence: 57 elements held 8.0 screens; 96 words at 633 ms with 50 ms gaps; 71 characters per screen.
4. Leave display type untracked at leading 1 and give slight positive tracking only to the mid tier and the small caps. Evidence: 0 em and 1 at 119.9–239.8 px; +0.02 at 55.9, 20 and 14 px.
5. Mark the selected state with the italic of the same face at the same size, not with a box. Evidence: 235 italic characters at 55.9 px; 0 filled or framed boxes; lists seen in sheet-desktop.jpg.
6. On a phone, cut the display sizes hard and lengthen the stages rather than shrinking everything evenly. Evidence: 159.8 → 48 px (×0.30) while 16 px stays; long late section 4.96 → 7.23 screens; navy section 1 → 4.

**Against our existing record**
- Agreement: 14 sections; the pinned intro at 9.0 screens; 240/160/151 px headings and 16 px body; Lenis; transitions 0.65, 0.5 and 0.22 s on cubic-bezier(0.4, 0, 0.2, 1); one filled sand pill.
- Differences: 23.4 screens at a 756 px high capture against 26.31 at 900; the late long section 4.35 against 4.96 screens; cards 864×907 (0.95) against 864×1080 (0.8); keyframes "spin, enter, exit" and `animated: 12` against 0 elements with keyframes today; the recipe's display leading 1.1 against 1; `label` "not-in-capture" against today's 20 px uppercase +0.02 label and 14 px uppercase button label.
- The record's navigation (`static`, 432 px, 9 links) is the same artefact as today's 431 px reading: the menu panel, not the rounded bar.
- Still missing from the record: hold lengths (8.0 and 7.5 screens; 5.0 and 4.5 on the phone), word timing, the 1189 ms lag, scale with scroll on chapter pictures, all phone values. Its notes that the card rails "scrub with scroll" and that the late section is a "pinned zoom" remain unverified: today's runs did not reach them.

**Not measurable here**: any motion after about screen 13 (desktop) or 10.7 (phone) — card rail, navy collage, late long section, footer; how the h1 and video enter after the loader; blur (seen, not read); canvas content and grounds drawn by pictures; the footer's appearance (no viewport shot shows it and the full-page capture is blank or repeats the hero there); the −50, −75 and −100 shots show the sections the readings place at 10.00, 16.20 and 19.20, not the nominal fractions of the page; the opened menu and hover on list items; timings are one lab run.

### C.6 white-desert — https://white-desert.com/

**Measured**: status 200 in both views; 23.1 screens at 1440×900 and 22.83 at 390×844; `failed` is empty and no input was ignored; the scroll runs covered 10800 px (desktop) and 9243 px (phone) and both ended inside the long pinned section, so its hold is a lower bound and nothing after it was sampled in motion.

**Creative thesis [I]** — Three voices kept far apart in scale — a condensed sans for single words as wide as the screen, a serif in uppercase and in italic for statements, a small sans for facts — set on white over visible column lines, with one stage in the middle where the page stops going down and goes sideways. Carried by: 320 px and 256 px words against a 14 px text size (desktop, type); the 42 px tier set three ways (desktop, type); a 10.5-screen section whose backgrounds hold while 8 elements travel sideways at 0.56 px per px scrolled (desktop, scroll); text edges at 0.18, 0.34–0.35, 0.51 and 0.67 (desktop, alignment.edges).

**Typography system**

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Largest display (h2, route code) | Oswald | 320 (22.22) | 400 | 0 | 0.9 | upper | 200 |
| h1 | Oswald | 256 (17.78) | 400 | 0 | 1 | upper | 80 |
| Stage heading (h2) | Cardinal Classic Long | 140 (9.72) | 500 | 0 | not read | upper | 60 |
| Section title (h3) | Cardinal Classic Long | 60 (4.17) | 400 | 0 | 1 | upper | 32 |
| Statement (h3) | Cardinal Classic Long | 42 (2.92) | 400 | 0 | 1 | upper | 26 |
| Card title (h3, italic) | Cardinal Classic Long | 42 (2.92) | 500 | 0 | 1 | none | 42 |
| Figures (h3) | Inter Tight | 42 (2.92) | 400 | 0 | 1.5 | upper | 32 |
| Quote, paragraph, lede (italic) | Cardinal Classic Long | 32, 22, 18 | 500 | 0 | 1.2 | none | 24, 22, 20 |
| Body and interface | Inter Tight | 16 (1.11), 14 (0.97) | 500 | 0 | 1.4, 1.5 | none | 16, 14 |
| Small label | Oswald | 18, 16, 14 | 500, 400 | 0 | 1.2–1.4 | upper | 18, 10, 14 |
| Attribution | Inter Tight | 10 (0.69) | 600 | +0.1 | 1.2 | upper | not in the phone list |

- [M] Three families loaded: Inter Tight, Cardinal Classic Long, Oswald (both views). [M-seen] Oswald is a condensed sans, the second a serif (desktop-scroll-0.jpg, desktop-scroll-25.jpg).
- [M] Largest ÷ most-used text size = 320 ÷ 14 ≈ 22.9 (3360 characters sit at 14 px, 742 at 16 px) and h1 ÷ 14 ≈ 18.3 at 1440; 200 ÷ 14 ≈ 14.3 and 80 ÷ 14 ≈ 5.7 at 390.
- [M] 13 sizes carry text at 1440 (320, 256, 140, 60, 42, 32, 22, 20, 18, 16, 14, 12, 10) and 14 at 390 (200, 80, 60, 42, 32, 26, 24, 22, 20, 18, 16, 14, 12, 10); the type reading is a selection (tool, inspect.mjs), so rare styles can be absent.
- [M] The 42 px tier is set three ways: uppercase upright serif at weight 400 (206 characters), italic serif at weight 500 in mixed case with `text-wrap: balance` (105 characters), uppercase Inter Tight at leading 1.5 (40 characters).
- [M] Italic is a working style: five italic serif sizes (42, 32, 22, 20, 18 px), all weight 500 at leading 1–1.2; the 32 px quote uses `text-wrap: pretty`. Tracking is 0 everywhere except the 10 px attribution.
- [M] Line length: 14 px paragraphs 58–63 characters at 29.3 em (410 px) and 32–36 characters at 16.9 em (236 px) at 1440; 39–41 characters at 19.4 em at 390, where the 22 px italic paragraph runs 33 characters at 12.3 em (paragraphs).
- [M-seen] The first line of the uppercase statement and of the italic paragraph is indented (sheet-desktop.jpg, desktop-scroll-25.jpg).

**Layout geometry**
- [M] Edges: 0.51 (16 blocks), 0.35 (13), 0.18 (12), 0.04 (9), 0 (9), 0.34 (7), 0.01 (4), 0.1 (3), 0.67 (3); declared grids 12 columns ×16 and 13 ×1 (desktop, alignment). At 390: 0.15 (52 blocks), 0.08 (17), 0 (9), 0.03 (8); grids 8 columns ×5, 9 ×2, 10 ×1, 2 ×1.
- [M-seen] Thin vertical lines run the full height of every viewport shot at fixed positions and text blocks start on them (desktop-scroll-25.jpg, desktop-scroll-100.jpg, mobile-scroll-0.jpg). [M] The hairline count is 1, so the reading does not see these lines: reading and screenshot disagree.
- [M] h1: one word on one line, centre-aligned, x 0.096, y 0.689, width 0.809, height 0.284, so its bottom is at about 0.97 of the screen; the video covers the first screen; text spans x 0.014–0.986 (desktop, first_screen).
- [M] Bar: 80 px high, `fixed`, 3 links, with 5 filled buttons on the first screen (desktop, first_screen). [M-seen] Three buttons left, the name in the centre, two right (desktop-scroll-0.jpg).
- [M] Centred text share 0.29 in both views.
- [M] Text columns per section: 0, 2, 1, 1, 1, 4, 1, 0, 2, 1, 0, 3, 4, 1, 1, 6, median 1; the narrow columns are the statement at x 0.336–0.828, the season text at 0.172–0.336 and the italic paragraph at 0.336–0.664 (desktop, sections).

**Section rhythm**
- [M] 16 sections by the reading at 1440, but four are wrappers or layers that share a top with another block (2.00 screens at 0, 1.00 at 6.88, an empty 1.00 at 17.86, and two overlapping dark blocks of 1.91 at 19.04 and 19.13): artefacts, leaving about 12 distinct stretches.
- [M] Heights of the distinct stretches in order: 2.00 (the video screen inside it is 1.00), 0.87, 1.50, 0.60, 0.85, 1.06, 10.50, 0.48, 1.00 (the empty wrapper), 0.27, 1.91, 1.00, 1.05 (desktop, sections).
- [M] The long one starts at 6.88 and is 10.5 screens: 976 characters (93 per screen), 5 pictures, a sticky element inside, 8285 px empty below its content.
- [M] Grounds by the reading: white ×12, rgb(9,11,16) ×3, rgb(233,231,225) for the footer; two changes; shares 0.78, 0.18, 0.04 (desktop). At 390 the dark share reads 0.04 and the itinerary block reads white with white ink. [M-seen] That block is dark on the phone too (sheet-mobile.jpg), so the phone ground reading is an artefact.
- [M] Space above/below content: median 320/160 px; 320 px above the statement, the season text and the section title; 332/320 around the italic paragraph (desktop). Median 115/30 at 390.
- [M] Characters per screen for the distinct stretches: 76, 174, 245, 15, 1135, 313, 93, 19, 966, 53, 42, 754.
- [I] Very large rests of white around single sentences, then one stretch that takes nearly half the page length: slow, then one long held look.

**Image treatment**
- [M] 20 pictures at 1440: 1 video (playing), 9 bleed, 16 cropped, 1 rounded (4.4px, a 188×212 preview), 0 shadows, 0 filters, 0 blends, 0 masks, 15 with words on them (desktop, pictures).
- [M] Frames: seven at 1440×900 (ratio 1.6) — the hero video, two overlays in the hero stage, three stacked backgrounds of the pinned stage, the closing picture; one 1440×1350 (1.07); five trip pictures 720×765 (0.94, width share 0.5) at x 0.008, 0.131, 0.623, 0.746, 0.869; three camp cards 680×500 (1.36, share 0.47) at x 1.014, 1.653, 2.292; one 1440×1721 (0.84, `fill`) in the dark block; a 311×175 (1.78) and a 454×110 strip (4.13, own ratio 0.8). The two hero-stage overlays are drawn at 1.33 times their pixel width.
- [M-seen] In the trips row one panel is open and sharp with a title, a price and text on it, and the other four are narrow blurred strips (desktop-scroll-25.jpg). [I] A horizontal accordion; the x positions give the open panel about half the width.
- [M-seen] Subjects are ice, rock peaks, penguins and camp buildings; pictures are either full-screen grounds with centred words on them or cards that carry their own title and text; a white cloud texture follows the hero (sheet-desktop.jpg); the camp cards have a lighter translucent border over an ice-texture ground (desktop-scroll-50.jpg).

**Motion behaviour**
- [M] Load: the lede, the film control and the h1 fade together over 835–852 ms starting 12–29 ms into sampling (h1 from opacity 0.01); the h1 settles at 864 ms, about 1.2 s after navigation with `began_ms` 336; 4 moves longer than 240 px, unnamed; 3 animations running (desktop, load). [M-seen] At 0.35 s a grey veil with the bar, a pale h1 and the lede lower than its final place; at 1.25 s video and text are in place (desktop-load-*.jpg).
- [M] Smoothing: lag median 1024 ms against a baseline of 0, Lenis present (desktop); on the phone 0 on 15 of 16 steps and 928 ms on one.
- [M] Hero stage: 4 unnamed elements held 2.0 screens and 12 elements, the examples being the bar's items, moving at rate 0.7 (desktop); on the phone the video is held 2 screens, the lede, film control, preview and h1 move at 0.7 and a "Clouds overlay" image at 0.1. [M-seen] The bar is absent from the −25 to −100 shots and an orange vertical tab is fixed at the right edge instead. [I] The bar leaves with the hero rather than staying on screen, despite its `fixed` position.
- [M] Pinned stage: three background images held 5.1 screens and the h2 5.0 when the run ended; a card picture held 3.8; 8 elements travel sideways at −0.56 px per px scrolled, up to −1.35 screen widths within the run; the h2 narrows 755 → 381 px with scroll (desktop, scroll). On the phone the hold reads 1.2 screens when the run ended, the h2 narrows 273 → 152 px, and no sideways movement was read.
- [M-seen] The background changes in tall vertical strips, the second picture entering across the first with the heading still in place (mobile-scroll-50.jpg); the last background carries a logo, a centred 32 px italic quote and a tracked attribution (desktop-scroll-75.jpg).
- [M] Scroll reveals: 1 at 1440 (a trip title fading in 615 ms) and 0 at 390. [I] That single fade is probably the parked pointer opening an accordion panel, not a scroll effect.
- [M-seen] The uppercase statement is nearly invisible in both sheets. [M] Its ink reads rgb(31,42,68). [I] Its opacity is probably tied to scroll position, which the reveal rule (change while the page stands still) does not catch.
- [M] Pointer: a bar button's fill goes rgba(31,42,68,0.2) → rgb(255,126,21), border to the same, over 0.3 s; on the film control the border fades and something inside changes opacity, clip-path and width; cursor `auto`. [M-seen] A small orange square sits where the pointer was parked in every desktop shot.
- [M] Reduced motion: 3 reveals and 3 running animations in both modes; 0 reduced-motion rules in 15 readable stylesheets.
- [M] Declared transitions: 0.3 s ×133, 0.6 s ×5, 0.45 s ×4, 0.4 s and 1 s ×1 each; easings cubic-bezier(0.5, 1, 0.89, 1) ×127, `ease` ×6, cubic-bezier(0.4, 0, 0.2, 1) ×5, cubic-bezier(0.76, 0, 0.24, 1) ×4; keyframes on 5 elements.
- [M-seen] A blurred rectangle sits at the bottom right of every desktop shot from 3.5 s on, and as a bottom band on the phone, smearing the lower right of the h1 and the footer's small print. [I] It is fixed to the viewport and is treated as a capture artefact (a hidden consent layer or headless rendering), not as design.

**Responsive transformations**
- [M] Page 23.1 → 22.83 screens; sections 16 → 21 by the reading (five trip cards become five blocks of about 0.85 screens; the footer reads as three).
- [M] The pinned stage is 10.5 → 6.27 screens; the hero stage (2.00), the season picture (1.50) and the closing picture (1.00) are the same in both views.
- [M] Type: 320 → 200 px (×0.63, 22.2 → 51.3 vw, on two lines); h1 256 → 80 (×0.31), y 0.689 → 0.877; 140 → 60; 60 → 32; statement 42 → 26; italic card titles 42 → 42; figures 42 → 32; quote 32 → 24; 22, 16 and 14 px unchanged; the lede 18 → 20; Oswald place names 16 → 10.
- [M] Grid 12 → 8 columns; main edge at 0.15; paragraph width 410 → 272 px.
- [M] Navigation: a menu button appears (none at 1440) and the five translucent buttons become one filled button, rgb(255,126,21) with white ink, radius 2px, 40 px high (mobile, surfaces).
- [M] Pictures: trip pictures 366×717 (ratio 0.51, share 0.94) one per row; camp cards 310×398 (0.78, share 0.79) at x 1.103, 2.103, 3.103; full-screen pictures 390×844 (0.46) cropped from sources of 1.5–1.6; 19 of 20 cropped. [M-seen] Every trip card is sharp and open on the phone (sheet-mobile.jpg).
- [M] Motion: the load gains measurable travel (h1 rises 98 px in 667 ms, the film control 151 px in 744 ms); smoothing is dropped; held hero, rate 0.7 and the narrowing h2 are kept.

**Surfaces**
- [M] 27 filled or framed boxes at 1440 with radii 0px ×13, 5px ×6, 2px ×5, 6px ×3; 5 shadows; 1 hairline; 0 gradients; 5 filled buttons with a translucent ground rgba(31,42,68,0.2 or 0.15), white ink, radius 2px, 40 px high; 1 outlined button (desktop, surfaces). At 390: 10 boxes, 5 shadows, 2 hairlines.
- [M-seen] The footer has off-white tiles with slightly rounded corners on the rgb(233,231,225) ground, link columns on the vertical lines and the name set across the full width in the condensed face (desktop-scroll-100.jpg). [M] That wide name is not in the type list. [I] It is drawn as a picture or vector.

**Reusable principles [I, each with its evidence]**
1. Give each typeface one job and keep the jobs far apart in size. Evidence: Oswald at 256–320 px and again at 14–18 px for labels; the serif at 18–140 px; Inter Tight at 10–16 px plus the 42 px figures.
2. Let a single word span the screen and sit it on the bottom edge of the first screen. Evidence: h1 one word at 17.78 vw, width 0.809, bottom at about 0.97; the 320 px code at x 0.008–0.992 in a 0.48-screen section.
3. Show the grid and hang the text on it. Evidence: vertical lines seen in every shot; edges at 0.18, 0.34–0.35, 0.51, 0.67; 12-column grid declared 16 times.
4. Spend whole screens of white on one sentence. Evidence: 320 px above three sections and 332/320 around the paragraph; 15–313 characters per screen in those sections.
5. Put the collection in one pinned stage that moves sideways and change the ground behind it rather than the page. Evidence: 10.5 screens; backgrounds held at least 5.1 screens; −0.56 px per px; three stacked 1440×900 backgrounds.
6. Reserve the one saturated colour for action. Evidence: rgb(255,126,21) appears only as a hover fill, as the phone's single filled button and on the side tab; its ink share at 1440 is 0.

**Against our existing record**
- Agreement: the three families; 320, 256 and 140 px with leading 0.9 and 1.0; a 10 px label at +0.1; Lenis; 0.3 s on cubic-bezier(0.5, 1, 0.89, 1); hero stage 2.0, season picture 1.5, trips 0.85 and closing picture 1.0 screens; a `fixed` 80 px bar.
- Differences: 25.6 screens at a 756 px high capture against 23.1 at 900; 11 sections against 16 by the reading (about 12 distinct); the pinned sequence 11.83 against 10.5 screens; body recorded as the 22 px serif (ratio 14.55), whereas most characters today are at 14 px Inter Tight (ratio about 22.9) and the 22 px italic is one paragraph of 296 characters; trips recorded as two half-width cards 720×643 in a carousel against five pictures 720×765 with one open; `custom_cursor: true` against a cursor reading of `auto` with a pointer-following square seen.
- The record lacks the orange (the recipe's accent is null), the italic system and the three-way 42 px tier, the vertical lines, every motion value (hold of at least 5.1 screens, −0.56 px per px, h2 755 → 381 px, rate 0.7, load fades of 835–852 ms, 1024 ms lag) and all phone values.
- The recipe's button (44 px high, radius 0, not filled) differs from today's 40 px, radius 2px, translucent fill.

**Not measurable here**: the full hold and sideways distance of the pinned stage, since both runs ended inside it; any motion after it (route code, itinerary block, closing picture), which also appear in no viewport shot, the full-page capture repeating the hero there; opacity or strips tied to scroll position and their timing; what the film control, the bar's menus and the trips row do when used; whether the blurred patch exists for a real visitor; the video beyond single frames; timings are one lab run.

### C.7 crav — https://www.cravburgers.shop/

**Measured**: status 200 on both views, no redirect; 11.59 screens at 1440×900, 9.25 at 390×844; `failed` is empty; no input ignored (wheel and touch both moved the page natively). Lab, one run: LCP 4872 ms on desktop, 62 requests.

**Creative thesis [I]** — The page is a poster, not a layout: the words are the frame and the product is pasted on top of them. To act on it: set one or two words as wide as the screen, lay a cut-out object over the letters, and change the flat ground colour instead of drawing a box. Carried by: a one-line h1 at 30vw spanning 0.95 of the width with the product picture's box overlapping it (desktop, first_screen); three flat grounds and no filled box, shadow or hairline (desktop, surfaces, colour); every type size a round vw value (both views, type); never more than 313 characters per screen (desktop, sections).

**Typography system** — [M] (desktop and mobile, type)

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Largest display (footer h2, one word) | Modak | 504 (35) | 400 | 0 | 0.5 | none | 136.5 (35vw) |
| h1 | Mouse Memoirs | 432 (30) | 400 | 0 | 0.8 | none | 101.4 (26vw), leading 0.85 |
| Section heading (h2) | Mouse Memoirs | 216 (15) | 400 | 0 | 0.75 (one h2 0.85) | uppercase (one h2 none) | 93.6 (24vw) |
| Display word in a p | Modak | 216 (15) | 400 | 0 | 1.5 | uppercase | 78 (20vw) |
| Sub-heading / sticker label (p) | Modak | 40.3 (2.8) | 400 | 0 | 0.9 | none ×7, uppercase ×3 | 31.2, 27.3, 23.4 |
| Menu link (nav a ×5) | Modak | 34.6 (2.4) | 400 | 0 | 1.1 | uppercase | 31.2 (8vw) |
| Body (p) | Mouse Memoirs | 25.9 (1.8) | 400 | 0 | 1.1 (1.0 in six p) | none | 19.5 (5vw) |
| Button text (a) | Mouse Memoirs | 25.9 (1.8) | 700 | 0 | 1.5 | uppercase | 19.5 |
| Navigation label | Mouse Memoirs | 18.7 (1.3) | 400 | 0.025 | 1.5 | uppercase | 15.6 (4vw) |
| Smallest label (nav p) | Mouse Memoirs | 13 (0.9) | 400 | 0.2 | 1.5 | uppercase | 13.7 (3.5vw) |

- [M] Two families on both views, Modak and Mouse Memoirs, plus "Modak Fallback" (families_loaded).
- [M] Display ÷ body, computed from (desktop, type): 504 ÷ 25.9 ≈ 19.5, h1 432 ÷ 25.9 ≈ 16.7, h2 216 ÷ 25.9 ≈ 8.3. On the phone (mobile, type): 136.5 ÷ 19.5 = 7.0, 101.4 ÷ 19.5 ≈ 5.2, 93.6 ÷ 19.5 = 4.8.
- [M] Ten sizes on desktop (504, 432, 216, 129.6, 57.6, 40.3, 34.6, 25.9, 18.7, 13 px), each a round vw value. Three carry nearly all characters: 25.9 px (rows of 416, 203, 121, 69 chars), 216 px (89, 29), 40.3 px (55, 28).
- [M] The one paragraph measured: 71 characters per line in 23.7 em (616 px) at 25.9 px; phone 47 characters in 16.6 em (paragraphs, both views).
- [M] Headings are split into spans: `h1 › span` ×2 reveal on load, `h2 › span` ×16 on scroll (desktop, load and scroll reveals.by_kind). No italic row; tracking 0 except the two smallest label sizes.
- [I] 71 characters in 23.7 em means a very condensed text face; that is what lets a 15vw heading hold two words per line.

**Layout geometry**
- [M] Left edge 0.03 shared by 20 blocks; other edges 0.04 (3), 0.18 (3), 0.2 (5), 0.75 (3) (desktop, alignment.edges). Text runs about 0.025–0.975 in seven section readings (desktop, sections.text_from_x/to_x).
- [M] One declared grid, 3 columns (desktop, alignment.grids_declared); none on the phone.
- [M] h1: one line, two words, centred, x 0.025, y 0.128, width 0.95, height 0.384 of the screen (desktop, first_screen.h1).
- [M] Largest first-screen picture: x 0.3, y 0.211, w 0.4, h 0.64, 0.26 of the screen, `words_on_it` true; its box overlaps the h1 box (desktop, first_screen.largest_picture, pictures).
- [M] Bar: fixed, 86 px, transparent, 7 links, one filled button, menu button present (desktop, first_screen.bar, navigation).
- [M] Centred text share 0.44 desktop, 0.79 phone (alignment.text_centred_share). Text columns per section reading: 5, 3, 0, 4, 0, 2, 0, 0, 2, 1, 2 (desktop, sections.text_columns).
- [M-seen] `desktop-scroll-0.jpg`: two short paragraphs sit in the bottom-left and bottom-right corners; the cut-out covers the middle letters of the headline; two tilted labels sit on the letters.

**Section rhythm**
- [M] 11 section readings: 1, 1.45, 0.33, 1.43, 1.6, 0.89, 0.33, 2.61, 0.61, 1.29, 0.89 screens (desktop, sections).
- [M] Artefacts: the two 0.33-screen readings hold no text and no picture (dividers); the 2.61-screen reading starts at the same top (6.68) as one of them and contains the 0.61 block at 7.12, so it is a wrapper. Negative space readings (−59, −54, −169, −549, −115 px) are content overlapping a section edge, not spacing.
- [M] Long bands: 1.6 screens at 4.14 = one bleeding picture, no text; 2.61 screens at 6.68 = yellow ground with a heading block and five small rounded pictures between 7.53 and 8.81 screens (desktop, sections, pictures).
- [M] Grounds in order: 245,227,205 ×2 → 249,24,20 ×2 → 245,227,205 ×2 → 255,215,80 ×3 → 245,227,205 ×2, four changes; shares 0.57 / 0.29 / 0.14 (desktop, sections.ground, colour.grounds).
- [M] Median space above/below content 41/0 px; first section 115/29. Characters per screen: 250, 131, 0, 83, 0, 60, 0, 0, 313, 127, 154 (desktop, sections).
- [M-seen] `sheet-desktop.jpg`: bands meet along wavy edges, not straight lines.
- [I] Pacing: one statement per screen, text bands alternating with bands that are only a picture or only a colour.

**Image treatment**
- [M] 29 `img` readings on desktop, no video, no canvas (desktop, pictures, built_with). Four carry the filter `url("#expandAndFill")`; three of those sit on the exact position and size of an unfiltered twin, so the count includes doubled layers (artefact).
- [M] 1 bleeds (1440×1440, cover, own ratio 1.4, at 4.14 screens). 9 rounded: 4% ×3, 14.4 px ×5, 28.8 px ×1. 0 shadows on desktop, 5 on the phone. 3 with words on them. 0 blends, 0 masks.
- [M] `cropped` is true on 20; 11 of those have fit `fill` or `contain`. [I] For those 11 the reading is most likely the bounding box of a tilted element, not a crop.
- [M] Ratios 0.71 to 2.07. Width shares: 0.12–0.24 (small cut-outs, stickers, cards), 0.4–0.44 (hero cut-out, collage pieces), 0.78 (a 1125×750 cut-out), 1 (bleed) (desktop, pictures).
- [M-seen] `desktop-scroll-0.jpg`, `-25`, `-50`: product photographs with the background removed, drawn stickers with a white outline, ingredient cut-outs overlapping headline letters, all tilted. `desktop-scroll-75.jpg`: small tilted rounded photographs of people eating, set along a dashed curved line with a drawn plane. `sheet-desktop.jpg`: one full-width photograph with wavy top and bottom edges.

**Motion behaviour**
- [M-seen] Load: `desktop-load-0.35s.jpg` and `-1.25s.jpg` show a full-screen red intro with a drawn burger being stacked, a caption and a progress bar along the bottom; `desktop-load-3.5s.jpg` shows a dark curved shape leaving at the top of an otherwise empty cream screen.
- [M] Load: 3 reveals of 16 followed. Two h1 spans at 4085 and 4134 ms (one 16 ms, a one-frame switch and an artefact; one 234 ms fade); then the picture at 4584 ms fading 600 ms, rising 14 px over 1650 ms, its width going 576 → 594 px. `h1_settles_ms` 4368; add `began_ms` 278 for time since navigation (desktop, load). Phone: h1 settles 4438, picture travel 9 px.
- [M] `last_settles_ms` 6234 is later than the 5724 ms sampled; it is an over-estimate (the reading adds travel time to the fade start).
- [M] Scroll: 39 reveals of 103 followed: img 17, h2 › span 16, p 6. 22 fades, quartiles 149 / 151 / 183 ms. 17 travels, 12 / 21 / 29 px in 200 / 283 / 400 ms; 5 upward; 10 masked. Stagger: 2 groups, gap quartiles 49 / 50 / 450 ms; 6 revealed together (desktop, scroll.reveals).
- [M] One h2: three words start together at 923 ms and travel 10, 16, 23 px in 166, 215, 283 ms, masked (desktop, scroll.reveals.examples). The 16 ms fades of whole h2 wrappers are one-frame switches (artefact).
- [M] Width changes: 22 elements with scroll, 16 settling; h2 words e.g. 424 → 397, 344 → 365, 387 → 489, 89 → 336 px (desktop, scroll.scale). [I] Heading words are stretched or squeezed as they arrive; the px values depend on the frame sampled, and the phone reading 191 → 0 is that mechanism caught mid-change.
- [M] Held: nothing pinned; 4 elements fixed throughout on desktop, 0 on the phone (scroll.held). [M-seen] The bar is visible in `desktop-scroll-0.jpg` and `-25`, not in `-50`, `-75`, `-100`.
- [M] Parallax: 8 elements, rate quartiles −0.21 / 0.07 / 0.24; examples −0.72, −0.09, 0.51 (desktop, scroll.parallax).
- [M] Sideways with scroll: 2 elements. The img named "Plane" crosses 0.8 screen widths at 0.4 px per px scrolled; an unnamed img −0.62 screen widths at −1.54. Drifting by themselves: 3 during load, 5 during scroll (desktop, sideways).
- [M] Smoothing: lag between 858 and 992 ms on 18 of 19 steps, median 990, baseline 0; `lenis` true, gsap not detected (desktop, scroll.lag_ms, built_with). Phone: lag 0 at all 14 steps.
- [M] Pointer: filled button ground 249,24,20 → 27,27,27 in 0.3 s; menu link border from 0.2 alpha to solid in 0.4 s; logo link no change (desktop, pointer).
- [M] Reduced motion: 2 load reveals against 3 normally; 0 reduced-motion rules in 2 stylesheets, none unreadable.
- [M] Declared: transitions 0.3 s ×24, 0.2 ×4, 0.15 ×4, 0.4 ×1; one easing, cubic-bezier(0.4, 0, 0.2, 1), on 33 elements; 0 elements with keyframes, 0 animations running. [I] Load and scroll movement is therefore script-driven; the CSS transitions serve hover states.

**Responsive transformations**
- [M] Type: h1 432 → 101.4 px (÷4.26; 30vw → 26vw); h2 216 → 93.6 (÷2.31; 15vw → 24vw); body 25.9 → 19.5 (÷1.33; 1.8vw → 5vw); footer word 504 → 136.5 (35vw on both). Display ÷ body falls from about 19.5 to 7.0.
- [M] h1 box: width 0.95 → 0.823, y 0.128 → 0.185, height 0.384 → 0.102 of the screen. Hero picture width 0.4 → 0.8, starting at y 0.313, below the h1 box (mobile, first_screen).
- [M] Section readings 11 → 13: 0.92, 0.87, 0.88, 0.7, 0.59, 0.26, 0.51, 0.5, 0.52, 0.5, 0.51, 1.02, 0.48. The yellow band becomes five blocks of 0.5–0.52 screens, one picture each (0.65–0.67 of the width, radius 19.5 px, shadow). Centred share 0.44 → 0.79.
- [M] Pictures 29 → 15. The bleeding photograph goes from ratio 1 (1440×1440) to 0.66 (390×591); the 0.78-wide cut-out becomes full width (390×260, bleeds).
- [M] Motion kept: 47 reveals (h2 › span 18, img 17, p 12), 13 masked, 4 stagger groups (gaps 38 / 100 / 266 ms), 6 parallax elements (−0.6 / −0.07 / −0.06). Changed: travels grow to 17 / 39 / 83 px in 400 / 582 / 683 ms, 29 of 38 upward. Dropped: smoothing (lag 0), sideways-with-scroll (0), fixed elements (0).
- [M-seen] `mobile-scroll-50.jpg`: the plane points down along a vertical dashed line. `mobile-scroll-0.jpg`: the two hero paragraphs are stacked and centred under the picture.
- [M] Bar 86 → 71 px, still fixed and transparent; menu button on both views.

**Surfaces**
- [M] Desktop: 0 filled or framed boxes, 0 shadows, 0 hairlines, 0 gradients; one filled button (ground 249,24,20, ink 245,227,205, radius reading 3.35544e+07 px = fully rounded, 42 px high, 18.72 px, uppercase) and one outlined. Phone: 5 boxes at radius 19.5 px, 6 shadows; button 37 px high, 15.6 px.
- [M-seen] `desktop-scroll-100.jpg` shows a thin rule under the footer links; the hairline reading of 0 missed it.

**Reusable principles [I, each with its evidence]**
1. Size type as a share of the viewport width and raise the share on a phone for the levels that must still fill the line. Evidence: all sizes are round vw; h2 15vw → 24vw, body 1.8vw → 5vw, h1 30vw → 26vw (both views, type).
2. Let the headline span the page and place the object over the letters, not beside them. Evidence: h1 width 0.95 on one line; picture at x 0.3, w 0.4 overlapping the h1 box, `words_on_it` true; 0 boxes on desktop.
3. Separate sections by ground colour and a shaped edge instead of boxes or rules. Evidence: 3 grounds, 4 changes, two empty 0.33-screen divider readings, 0 boxes / shadows / hairlines on desktop; wavy edges in `sheet-desktop.jpg`.
4. Keep copy sparse when display type is extreme. Evidence: display ÷ body about 19.5; at most 313 characters per screen; one paragraph of 71 characters per line.
5. Reveal headings word by word with short, small, masked moves; let pictures fade. Evidence: 16 h2 spans, 10 masked, travel 12–29 px in 200–400 ms, fades 149–183 ms; same-start words with growing distance (10, 16, 23 px).
6. Give a few props their own scroll rate rather than pinning the layout. Evidence: 0 held elements; 8 parallax elements from −0.72 to 0.51; one prop crossing 0.8 screen widths with scroll.
7. On a phone, turn a scattered band into a stack of half-screen cards. Evidence: sections 11 → 13, five 0.5-screen blocks, centred share 0.79, pictures gain radius 19.5 px and a shadow.

**Against our existing record**
- The record's body is Modak 40 px (leading 0.9), giving display ÷ body 12.6; today the running text is Mouse Memoirs 25.9 px and the 40.3 px Modak rows are labels (the record's `label` is null). The record files the 432 px h1 under `h2` and the 216 px h2 under `h3`.
- The record has 9 sections ([1.0, 1.73, 2.28, 1.6, 1.06, 2.59, 0.72, 1.34, 1.06]) and 13.6 screens against a 756 px high viewport; today 11 readings (three of them dividers or a wrapper) and 11.59 screens at 900 px.
- The record's media radius is 0 and its full-width photograph is flagged not bleeding (wf 0.99); today 9 pictures are rounded (4%, 14.4 px, 28.8 px) and that photograph bleeds. Blueprint button 48 px high at 15 px; today 42 px at 18.72 px.
- The record's motion holds only `lenis`, two 0.3 s transitions and a prose note; it lacks the intro and load order, the scroll reveals, parallax rates, the sideways prop, the width changes, the 990 ms lag, the unanswered reduced-motion request, and every phone reading (`mobile` is "missing").

**Not measurable here** — The intro's own duration (three still frames only). How heading words are stretched (transform or font setting). Tilt angles of stickers. Which 4 elements are fixed, and whether the bar hides by scroll direction. The opened menu (its 34.6 px links are in the type reading; the menu was not opened). What the `#expandAndFill` filter draws. The easing of script-driven motion. A small round badge sits at the exact centre of every desktop scroll shot; whether it follows the pointer was not tested.

### C.8 halfdays — https://www.halfdays.com/

**Measured**: status 200 on both views, but `final_url` is https://www.halfdays.com/en-eu: the page redirected to a regional storefront, so everything below describes that storefront, not the URL in the record. 4.15 screens at 1440×900, 6.25 at 390×844; `failed` empty; no input ignored. Lab, one run: LCP 1152 ms desktop, 316 requests. The cookie dialog was not hidden on the phone view (see Responsive).

**Creative thesis [I]** — A shop front where photographs do the persuading and type works as shelf labelling. To act on it: one small sans in a narrow size range, labels set in white directly on the pictures, a strict proportion per row of pictures, and almost no movement. Carried by: largest text 26 px against 16 px body (desktop, type); the first picture takes 0.9 of the first screen (desktop, first_screen); 18 pictures, all radius 0 and without shadow (desktop, pictures); 0 load reveals and native scrolling with lag 0 (desktop, load, scroll).

**Typography system** — [M] (desktop and mobile, type)

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Hero word | not text: the hero h2 reads 44 px with 0 words | — | — | — | — | — | h2 box 32 px, 0 words |
| Section heading (h2 ×1) | SuisseIntl | 26 (1.81) | 500 | −0.01 | 1.0 | uppercase | 26 |
| Row heading / category link (a ×6, a ×1, h2 ×1) | SuisseIntl | 24 (1.67) | 500 | −0.02 | 1.1–1.2 | uppercase | 16 (category links), 18 (h2), 24 (one link) |
| Tile name (a ×6) | SuisseIntl | 20 (1.39) | 500 | −0.03 | 1.3 | none | 18 |
| Body (p ×1) | SuisseIntl | 16 (1.11) | 400 | −0.026 | 1.35 | none | 16 |
| Footer link (a ×16) | SuisseIntl | 16 (1.11) | 500 | −0.022 | 1.2 | uppercase | 16 |
| Product name (h3 ×6) | SuisseIntl | 14 (0.97) | 500 | −0.017 | not read | none | 14, tracking 0 |
| Label (p ×1) | SuisseIntl | 13 (0.9) | 600 | +0.08 | 1.5 | uppercase | 13 |
| Small print, price | SuisseIntl | 12 (0.83) | 400 | −0.035 | 1.5 / not read | none | 12 |
| Smallest caps (footer) | SuisseIntl | 12, 10.4, 10 | 400 (600 on one link) | +0.06 to +0.1 | 1.2–1.5 | uppercase | same |

- [M] One family loaded on desktop (SuisseIntl). A computed family "Metropolis" appears on 3 buttons but is not in `families_loaded`. The phone view also lists Inter.
- [M] Largest text ÷ body: 26 ÷ 16 ≈ 1.6 (computed; desktop, type).
- [M] Nine sizes, all between 10 and 26 px (26, 24, 20, 16, 14, 13, 12, 10.4, 10). 16 px carries the most characters (226 + 162), then 14 px (173 + 38).
- [M] The single paragraph: 57 characters per line in 28.7 em (459 px), 4 lines; phone 45 characters in 22.5 em (paragraphs).
- [M] Tracking changes sign with role: −0.01 to −0.035 em on every row of 14 px and above and on 12 px mixed-case text; +0.06 to +0.1 em on uppercase labels of 10–13 px. Weights 400, 500, 600 only; no italic row.
- [M-seen] `desktop-scroll-0.jpg`: the hero word is very large, pale yellow, top-left on the picture. [I] It is drawn (image or vector), which is why the h2 reads 0 words.

**Layout geometry**
- [M] Left edge 0.01 (8 blocks; text starts at 0.014); other edges 0.5 (14), 0.7 (12), 0.31 (8), and 0.18, 0.42, 0.67 (4 each) (desktop, alignment.edges). Three 2-column grids declared. Centred text share 0.13.
- [M] First screen: no h1; `bar` is null; largest picture x 0, y 0.102, w 1, h 0.9 = 0.9 of the screen; hero text column 0.014–0.334 (desktop, first_screen, sections[0]).
- [M-seen] `desktop-scroll-0.jpg`: a pale strip and a white header (one text link left, logo centre, three icons right) fill the 0.10 screen above the picture.
- [M] Text columns per section: 1, 0, 0, 1, 6, 3 (desktop, sections).
- [M] Tile row: six pictures of 0.16 width at x 0.014, 0.177, 0.34, 0.503, 0.667, 0.83. Tall row: three of 0.41 width at x 0, 0.42, 0.84, the third running past the right edge. Product row: heading at x 0.014, pictures of 0.15 width from x 0.177 to 0.948, the sixth cut by the edge (desktop, pictures).
- [M] Story section: pictures at x 0.014 (0.38 wide) and 0.415 (0.24 wide); text from 0.668 to 0.986 (desktop, pictures, sections[3]).

**Section rhythm**
- [M] 6 sections: 0.9, 0.37, 1.14, 0.64, 0.52, 0.48 screens (desktop, sections).
- [M] The long ones: the hero (0.9, one picture) and the three-picture row (1.14; pictures 593×880).
- [M] Grounds: all six read 255,255,255, share 1, 0 changes (desktop, sections, colour). [M-seen] `desktop-scroll-100.jpg` shows the last section near-black with white text, so the ground reading is wrong for the footer. [M] White is the largest ink share, 0.38 (desktop, colour.inks).
- [M] Space above/below content: 60/559, 24/0, 80/69, 30/30, 30/58, 30/90; median 30/69 (desktop, sections).
- [M] Characters per screen: 14, 131, 59, 465, 83, 1032 (desktop, sections).
- [I] Pacing: a short page of picture rows separated by 24–80 px, with one paragraph in the whole page and the densest text in the footer.

**Image treatment**
- [M] 18 pictures, all `img`, 0 video (desktop, pictures). 1 bleeds (1440×810, ratio 1.78, cover, not cropped, words on it). 2 cropped (the story pair: box ratios 1.07 and 0.66 against own 0.85 and 0.73). 0 rounded, 0 shadows on pictures, 0 filters, blends or masks.
- [M] One ratio per row: 1.78 (hero), 0.73 ×6 (tiles 225×307), 0.67 ×3 (593×880), 1.07 and 0.66 (story), 0.67 ×6 (products 210×315). Width shares 1, 0.41, 0.38, 0.24, 0.16, 0.15.
- [M-seen] `desktop-scroll-0.jpg`: one figure on a flat blue backdrop. `desktop-scroll-25.jpg`: six full-figure pictures in snow, each with a name and an arrow in white at its lower left. `desktop-scroll-50.jpg`: close crops with a category name left and a link right, both white, at mid-height on the picture. `desktop-scroll-100.jpg`: products on a pale studio ground with name and price underneath.

**Motion behaviour**
- [M] Load: 0 reveals of 17 followed; the sampler began 1264 ms after navigation, later than the LCP at 1152 ms, so anything earlier was not sampled; CLS 0 (desktop, load, lab). [M-seen] The three `desktop-load-*.jpg` frames show the same finished first screen.
- [M] Scroll: lag 0 on all 8 steps, baseline 0; `lenis` false (desktop, scroll). 6 reveals of 90 followed: four travels at 78 ms (the logo img −30 px in 98 ms, three `li` −26 px in 65 ms) and two picture fades from opacity 0 of 284 and 289 ms; no stagger group.
- [I] The four travels are the header leaving as scrolling starts; the two fades are pictures appearing when reached.
- [M] Held: nothing pinned; 2 elements fixed throughout on both views. [M-seen] `desktop-scroll-25.jpg` to `-100`: a round widget bottom-left and a chat button bottom-right; no header visible.
- [M] Parallax 0, sideways with scroll 0, drifting 0, scale 0 (both views). `swiper` is true in built_with; the rows were not dragged in the test.
- [M] Pointer: three links hovered, no computed change; transition 0.3 s.
- [M] Reduced motion: 1 reduced-motion rule found, with 15 of 177 stylesheets unreadable, so the count may be low. With reduce asked, 1 load reveal against 0 normally. [I] That is a difference between two runs, not a sign that the setting adds motion.
- [M] Declared: 0.3 s on 484 elements, 0.4 ×4, 0.25 ×4, 0.1 ×4, 0.2 ×3, 0.15 ×1; easings linear 400, ease 60, ease-in-out 33, cubic-bezier(0.29, 0.63, 0.44, 1) ×2, ease-in ×2; keyframes on 3 elements, none running.

**Responsive transformations**
- [M] Type barely changes: h2 26 → 26, body 16 → 16, labels 13 → 13 (ratio 1.0). Only tile names 20 → 18, the product-row heading 24 → 18 and category links 24 → 16 shrink (both views, type).
- [M] Page 4.15 → 6.25 screens; still 6 sections: 0.82, 0.34, 0.74, 1.06, 1.67, 1.49.
- [M] Hero picture: ratio 1.78 → 0.56 (390×693) with own ratio 0.56, i.e. a different, portrait file; 0.82 of the screen.
- [M] Tile row: 0.16 → 0.41 width at x 0.038, 0.474, 0.91, 1.346, 1.782, 2.218. Tall row: 0.41 → 0.83 width at x 0, 0.859, 1.718. Both run off to the right.
- [M] Story: 2 pictures → 1 (360×345, 0.92 wide), text below at 0.038–0.962. Products: one row → a 2-column grid (0.45 wide at x 0.038 and 0.513), section 0.52 → 1.67 screens.
- [M] Edges collapse to 0.04 (47 blocks) and 0.51 (6); centred share 0.04; paragraph 45 characters per line.
- [M] Motion: 0 reveals of 86 followed on scroll, lag 0, 2 fixed. Menu button present on both views.
- [M-seen] `mobile-scroll-0.jpg`, `-50`, `-100` and the first column of `sheet-mobile.jpg`: a cookie dialog covers the lower half of the screen; phone first-screen readings were taken with it present.

**Surfaces**
- [M] 0 filled or framed boxes, 0 hairlines, 0 gradients; 3 shadows on desktop, 0 on the phone (surfaces).
- [M] Filled buttons read on desktop: 3, white ground, black ink, radius 8 px, 63 px high, 13.33 px; none on the phone. [M-seen] The only button in `desktop-scroll-100.jpg` is a white square-cornered one on the dark footer. [I] The three readings, like the "Metropolis" rows, probably belong to an embedded widget, not to the page's design.

**Reusable principles [I, each with its evidence]**
1. Give the page to pictures and keep words to labels. Evidence: one paragraph on the page; 14, 131, 59 and 83 characters per screen in the picture sections; hero picture 0.9 of the first screen.
2. Use one family in a narrow range and separate levels by case, weight and tracking instead of size. Evidence: 10–26 px, largest ÷ body about 1.6, weights 400/500/600, tracking −0.035 to +0.1 em with the sign tied to role.
3. Put the label on the picture at a fixed spot per row rather than in a caption box. Evidence: 0 boxes and 0 hairlines; white ink share 0.38; white names on the tiles and tall pictures in `desktop-scroll-25.jpg` and `-50`.
4. Change the picture proportion from row to row and hold it strictly within a row. Evidence: 1.78 → 0.73 ×6 → 0.67 ×3 → 1.07 and 0.66 → 0.67 ×6; radius 0 and no shadow on all 18.
5. Let a row run off the right edge to show there is more. Evidence: x positions past the viewport on desktop (0.84 + 0.41 width; 0.948 + 0.15) and up to 2.218 on the phone.
6. On a phone keep the type and change the pictures. Evidence: type ratio 1.0 for heading and body; hero swapped for a 0.56 portrait; tiles 0.16 → 0.41 and 0.41 → 0.83 wide; product row becomes two columns.
7. Keep the motion budget near zero. Evidence: 0 load reveals, two fades of about 285 ms, lag 0, nothing pinned.

**Against our existing record**
- The record's URL is the root address; today's page is the `/en-eu` storefront, and the record's caveats list is empty.
- The record's display level is a 44 px text headline (weight 500, tracking −0.04, 461 wide per its note), giving display ÷ body 2.75. Today the hero h2 still computes 44 px but has 0 words and a drawn word, so the largest measurable text is 26 px and the ratio about 1.6. The record's h3 (26 px, −0.01, leading 1.0, uppercase) and label (13 px, +0.08) match today.
- Same six sections in the same order: record [1.06, 0.44, 1.36, 0.76, 0.61, 0.55] and 4.9 screens at a 756 px viewport; today [0.9, 0.37, 1.14, 0.64, 0.52, 0.48] and 4.15 at 900 px.
- The blueprint has a fixed 92 px bar with 6 links and a black 56 px button with radius 0; today `bar` is null, header parts travel up at scroll start, and no such button was read.
- The record's motion is a prose note plus two transitions (0.4 s cubic-bezier(0.29, 0.63, 0.44, 1); 0.3 s ease-in-out). It lacks the measured near-absence of reveals, the header leaving, the roughly 285 ms picture fades, `swiper`, and all phone behaviour (portrait hero, off-screen rows, two-column grid).

**Not measurable here** — The hero word's size and face (drawn, not text). The footer's ground (read as white, seen dark). Whether the header returns on scrolling up (the test only scrolled down). How the rows move when dragged. Hover on picture tiles (only three links were hovered). The strip above the header shows different words in `desktop-load-*.jpg` and `desktop-scroll-0.jpg`; its timing was not sampled. The phone first screen without the cookie dialog. Whether the address in the record serves the same design to another region.

### C.9 units — https://units.gr/en/homepage/

**Measured**: status 200 on both views, no redirect; 9.56 screens at 1440×900, 8.77 at 390×844; `failed` empty; no input ignored. `baseline_lag_ms` is [0, 75, 63], not all zero in this run. A promotional popup opened during load and stayed open through every viewport shot. Lab, one run: LCP 3040 ms desktop, 126 requests.

**Creative thesis [I]** — A card system: one paper ground, and everything on it (photographs, text, navigation, buttons) is a flat-coloured tile with the same large radius; the single piece of spectacle is one pinned rail that moves sideways. Carried by: one ground at share 1 with 40 filled or framed boxes, 14 of them at radius 37.4976 px, and 7 pictures at that radius (desktop, surfaces, pictures); a fixed side navigation 900 px high with 9 links (desktop, first_screen.bar); 21 elements held for up to 3.5 screens while moving −0.62 screen widths (desktop, scroll.held, sideways); 1 scroll reveal among 72 followed elements (desktop, scroll.reveals).

**Typography system** — [M] (desktop and mobile, type)

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Largest display (hero line, span ×1) | Bunch | 72 (5) | 850 | 0 | 1.0 | none | 38 (9.74vw) |
| h1 / h2 | none: `headings` reads null for both | — | — | — | — | — | — |
| Section heading (span ×9) | Bunch | 33 (2.29) | 850 | 0 | 1.0 | none | 28 (7.18vw) |
| Card title (span ×3, footer label) | Bunch | 25.5 (1.77) | 850 | 0 | 1.0 | none | 22 |
| Sub-heading (span ×4) | Bunch | 22 (1.53) | 850 | 0 | 1.1 | none | 22 |
| Hero sub-line (span ×1) | Aeonik Pro | 24 (1.67) | 700 | 0 | 1.1 | none | 18 |
| List item (li ×17) | Aeonik Pro | 16 (1.11) | 400 | 0 | 1.8 | none | 16 |
| Body (p ×3, spans) | Aeonik Pro | 15 (1.04) | 400 | 0 | 1.2 | none | 14 |
| Strip label (span ×18, nowrap) | Bunch | 15 (1.04) | 800 | 0 | 1.1 | none | 14 |
| Label / navigation | Aeonik Pro | 14 and 12 | 400, 700 | 0 | 1.2 | none | 14, 12, 10 |

- [M] Two families on both views: Aeonik Pro and Bunch (families_loaded).
- [M] Display ÷ body, computed: 72 ÷ 15 = 4.8 on desktop, 38 ÷ 14 ≈ 2.7 on the phone; section heading ÷ body 33 ÷ 15 = 2.2 and 28 ÷ 14 = 2.0.
- [M] Nine sizes on desktop (72, 33, 25.5, 24, 22, 16, 15, 14, 12 px). 15 px carries the most characters (1267 + 340), then 16 px (409 + 135).
- [M] Paragraphs at 15 px: 60 characters per line in 30.4 em (456 px), 51 in 29.8 em, 36 in 22.8 em. Phone at 14 px: 48, 51, 36 characters in 22.7–22.9 em (paragraphs).
- [M] No h1 or h2 element on the page: all headings are spans. Tracking is 0 on every row and no row is uppercase. Levels differ by face and weight (850 and 800 against 400 and 700), and lists by leading (1.8 against 1.2).

**Layout geometry**
- [M] Bar: fixed, 900 px high, transparent, 9 links, no menu button (desktop, first_screen.bar, navigation). [M-seen] `desktop-scroll-0.jpg`: a column of coloured tiles down the left edge under the logo.
- [M] Edges: 0.01 (4 blocks), 0.12 (3), 0.14 (3), 0.43 (3), 0.45 (3), 0.75 (4) (desktop, alignment.edges). Pictures start at x 0.116; text columns at 0.137–0.447, 0.137–0.454 and 0.432–0.67 (desktop, pictures, sections).
- [M] Grids declared: 2 columns ×5, 3 columns ×2, 30 columns ×1 (desktop, alignment.grids_declared).
- [M] First screen: no h1; largest picture x 0.116, y 0.033, w 0.87, h 0.944 = 0.82 of the screen, radius 37.4976 px, words on it; text spans x 0.014–0.614; 4 filled buttons (desktop, first_screen).
- [M-seen] `desktop-scroll-0.jpg` (dimmed behind the popup): the hero line runs in white across the middle of the picture. [M] Its position was not measured (no heading element).
- [M] Centred text share 0 on both views. [M-seen] `sheet-desktop.jpg`: the text in the three blue cards looks centred, so the reading and the sheet disagree.
- [M] Text columns per section: 0, 1, 0, 1, 1, 0, 0, 0 (desktop, sections).

**Section rhythm**
- [M] 8 sections: 0.94, 0.53, 4.34, 0.93, 0.67, 0.57, 0.46, 0.7 screens (desktop, sections).
- [M] The long one is the third, 4.34 screens from 1.55: 4 pictures, 1080 characters, and 3071 px of space below its content. That space is the pin's scroll length; the blank stretch in `sheet-desktop.jpg` is the capture, not the design.
- [M] Grounds: all eight 244,233,225, share 1, 0 changes (desktop, sections, colour). Inks: black 0.81, white 0.07, 255,178,0 0.06, 27,227,73 0.04.
- [M-seen] `sheet-desktop.jpg`: colour sits in the cards (yellow, orange-red, lilac, blue, red, purple, green), not in the page ground.
- [M] Space above/below content: 526/276, 10/133, 63/3071, 480/119, 0/0, 53/175, 88/0, 0/26; median 63/133. Characters per screen: 141, 550, 249, 463, 347, 662, 97, 213 (desktop, sections).
- [I] Pacing: sections of roughly half to one screen on either side of a single long hold; text density stays moderate throughout because each card carries a short block.

**Image treatment**
- [M] 19 `img` readings, 0 video, 2 canvases that are not in the picture list (desktop, pictures, built_with). 0 bleed. 6 cropped. 8 rounded: 37.4976 px ×7 (hero, four rail photographs, two portrait photographs) and 50 px ×1 (the popup's 520×520 picture). 0 shadows, filters, blends or masks. Words on 1 (hero).
- [M] Ratios: 1.47 (hero, 1253×850), 0.74 / 0.79 / 0.83 (rail photographs, each 405 px = 0.28 of the width, at x 0.428, 0.725, 1.022, 1.319), 0.67 ×2 (403×604), 1.18 ×3 (343×290, contain, radius 0), 0.81 ×8 (269×330, x from −0.264 to 1.09, a row wider than the screen).
- [M-seen] `sheet-desktop.jpg`: interior and people photographs in large-radius cards, mixed in one grid with flat-colour text cards of the same radius; pixel-grid drawings on blue cards; a map coloured in orange and yellow inside a rounded card; a perspective line drawing with coloured panels. [I] The map and the drawing are probably the two canvases; a headless browser may render them differently.

**Motion behaviour**
- [M-seen] Load: `desktop-load-0.35s.jpg` shows the paper ground with a house-shaped mark in blue at the centre and a cookie notice (hidden later); `-1.25s` the mark in ochre; `-3.5s` a dark scrim, the popup, and part of a black wordmark shape behind it.
- [M] Load: 5 reveals of 15 followed. Four start together at 2483 ms, each fading 317 ms and rising 39 px in 301 ms: button, picture, button, paragraph. A fifth, a picture inside a clipped parent, moves 82 px up in 100 ms at 5384 ms. No h1, so `h1_settles_ms` is null; `began_ms` 516 (desktop, load).
- [I] The four simultaneous reveals are the popup entering, not the hero; the hero's own entrance is hidden by the scrim and was not captured.
- [M] Scroll: 1 reveal of 72 followed (a button fading 784 ms and rising 14 px in 484 ms) (desktop, scroll.reveals).
- [M] Held: 21 elements: 10 for 3.5 screens, 5 for 3.0, 6 for 1.5; 16 fixed throughout (desktop, scroll.held).
- [M] Sideways with scroll: 21 elements, −0.62 screen widths in total, −0.2 to −0.22 px per px scrolled; drifting 0; parallax 0; scale 0 (desktop, scroll).
- [M-seen] `desktop-scroll-25.jpg` and `-50`: two rows of text cards and photograph cards shifted left between the shots, under a red strip of labels whose offset also differs. [M] Whether that strip is scroll-linked or drifting was not determined (drifting reads 0 on desktop, 4 on the phone).
- [M] Smoothing: lag 791–792 ms on 14 of 15 steps against a baseline of 0, 75, 63 ms; `lenis`, `gsap` and `scroll_trigger` true (desktop, scroll.lag_ms, built_with). Phone: lag 0 on all 13 steps.
- [M] Pointer: one filled button hovered, no change, transition 0.7 s. [I] The open popup may have covered it.
- [M] Reduced motion: 4 load reveals against 5; 2 reduced-motion rules in 11 readable stylesheets (1 in 10 on the phone).
- [M] Declared: 0.7 s ×32, 0.4 ×11, 0.2 ×10, 1 s ×5, 0.25 ×4, 0.6 ×4; easing cubic-bezier(0.19, 1, 0.22, 1) on 53 elements, ease 9, ease-in-out 4; keyframes on 2 elements.

**Responsive transformations**
- [M] Type: 72 → 38 px (÷1.89; 5vw → 9.74vw), 33 → 28 (÷1.18), 25.5 → 22, 24 → 18, body 15 → 14 (÷1.07), list 16 → 16. Display ÷ body 4.8 → about 2.7.
- [M] Navigation: the 900 px side bar with 9 links becomes a fixed 69 px top bar on the paper ground with 2 links and a menu button (mobile, first_screen.bar, navigation).
- [M] 8 sections on both; phone heights 0.89, 0.86, 1.24, 1.03, 1.09, 1.57, 0.7, 0.93; page 9.56 → 8.77 screens.
- [M] The pinned section shrinks from 4.34 to 1.24 screens: 0 elements held, 0 sideways with scroll; its four pictures are 370×215 at x 0.026, 1.026, 2.026, 3.026, one screen width apart; `swiper` true. [M-seen] `sheet-mobile.jpg`: text cards stacked, then one photograph with arrows at its left and right.
- [M] Hero picture 1253×850 (1.47) → 370×754 (0.49), 0.949 wide, 0.85 of the screen; radius 37.4976 → 30 px. Portrait photographs 403×604 (0.67) → 370×250 (1.48). The three 343×290 drawings stack at 330×279 (0.85 wide).
- [M] Edges 0.03 (7), 0.08 (3), 0.09 (6); text 0.09–0.91; chars per screen in the former pinned section 249 → 869.
- [M] Motion: the same four popup reveals (fade 300 ms, 39 px in 283 ms at 2498 ms); 0 scroll reveals of 43 followed; 4 fixed; 4 drifting (desktop 0); no smoothing.

**Surfaces**
- [M] Desktop: 40 filled or framed boxes with radii 0 px ×16, 37.4976 px ×14, 4 px ×8, 20 px ×1; 0 shadows; 1 hairline; 2 gradients. Phone: 16 boxes (0 px ×10, 4 px ×5, 20 px ×1), 18 hairlines. [M-seen] Rules under list rows are visible on desktop too (`desktop-scroll-25.jpg`), so the two hairline counts disagree and the desktop one is low.
- [M] Buttons, desktop: 3 black pills (radius 37.4976 px, 48 px high, 16 px), 1 on ground 171,84,247 (radius 10 px, 64 px high), 1 black (radius 10 px, 42 px high), 4 outlined. Ink reads black on black for the pills, a reading artefact: the label is white in `desktop-scroll-0.jpg`. Phone: pills at radius 30 px and 47 px high, plus one on 255,92,56 at 33 px high.

**Reusable principles [I, each with its evidence]**
1. Hold one ground and put all colour into cards, with text cards and photograph cards in the same grid. Evidence: ground share 1 and 0 changes; 40 boxes; 0 bleeding pictures; 0 shadows.
2. Use one large radius for every big surface and scale it with the viewport. Evidence: 37.4976 px on 14 boxes, 7 pictures and the pill buttons; 30 px for all of them on the phone.
3. Treat navigation as part of the composition, then collapse it. Evidence: a fixed 900 px side bar with 9 links and content inset to x 0.116 on desktop; a 69 px top bar with a menu button on the phone.
4. Spend the scroll effect on one section and leave the rest still. Evidence: 4.34 of 9.56 screens pinned, 21 elements held up to 3.5 screens and moved −0.62 screen widths; 1 scroll reveal of 72; on the phone the pin is replaced by a swipe row (1.24 screens, 0 held).
5. Distinguish headings by face and weight, not by size, case or tracking. Evidence: Bunch 850 against Aeonik Pro 400; section heading 2.2× body; tracking 0 and no uppercase on any row.
6. Keep text blocks narrow and short inside cards. Evidence: 36–60 characters per line in 22.8–30.4 em; list leading 1.8.

**Against our existing record**
- The record's display is Bunch 33 px (weight 850, leading 1.05) with display ÷ body 2.2 and a "scale-contrast-low" principle. Today a 72 px Bunch line sits on the first screen, giving 4.8; 33 px is the section heading, at leading 1.0. The record has no h3 or label level; today 25.5, 22 and 15 px Bunch rows exist.
- The record marks one 4.98-screen pinned section by a hand-written role name and says the scroll behaviour was not measured. Today it is measured: 4.34 screens at a 900 px viewport, 21 held elements, a sideways rate of about −0.2 px per px.
- The record's note and transition list hold a 1.8 s background colour crossfade per section. Today all eight sections read the same ground and no 1.8 s duration is declared (1, 0.7, 0.6, 0.4, 0.25, 0.2 s): not confirmed.
- The blueprint has media radius 0 and a fixed 60 px bar; today 7 pictures carry radius 37.4976 px and the bar is a 900 px side rail. The record has 11 screens and [0.93, 0.63, 4.98, 1.11, 0.8, 0.68, 0.55, 0.83] at a 756 px viewport against today's 9.56 and [0.94, 0.53, 4.34, 0.93, 0.67, 0.57, 0.46, 0.7]. It lacks the load sequence, the popup, the 791 ms lag and every phone reading.

**Not measurable here** — The hero's own entrance and the hero line's position (popup and scrim open from about 2.5 s; no heading element). Hover behaviour of the side tiles and cards under the open popup. The map and line drawing as real visitors see them (canvas in a headless browser). Whether the label strips and the picture row drift on desktop. Whether the ground changes colour once the popup is closed. The easing of the pinned rail. What the cookie notice covered before it was hidden.

### C.10 aino — https://aino.agency/

**Measured**: [M] status 200 on both views; 7.47 screens at 1440, 7.11 at 390; `failed` is empty. [M] The page ignored wheel input at 1440 and touch at 390 (`scroll.input_ignored`) and was moved by script, 11 steps per view. [M-seen] Every viewport shot — the three load shots and all five scroll positions — shows only a field of typed characters with the navigation over it (`desktop-load-*.jpg`, `desktop-scroll-0…100.jpg`, `mobile-scroll-*.jpg`); the content appears only in the full-page captures (`sheet-desktop.jpg`, `sheet-mobile.jpg`). Static readings (type, geometry, sections, pictures) therefore stand; what is on screen once the field is gone, and how the page answers a real wheel or finger, was not observed.

**Creative thesis [I]** — An index rather than a pitch: unframed tiles hung on a four-column grid over one pale ground, each named by a code-and-name label at one small size, with a single 18-word sentence as the only large type. The layout itself does not move; the one spectacle is a character-drawn field laid over the first screen. Carried by: three sizes for all text (desktop, type); block edges at 0.01 / 0.26 / 0.51 / 0.75 with one declared four-column grid (desktop, alignment); one ground, no ground change in nine sections (desktop, sections); no declared transitions, no keyframes, no scroll reveals (motion_declared, scroll.reveals).

**Typography system**

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Largest display = h1 | abcplus | 37.7 (2.62) | 720 | −0.03 | 1.03 | none | 27.8 |
| Body (the one paragraph) | abcplus | 22.6 (1.57) | 500 | −0.02 | 1.14 | none | 22.8 |
| Section heading / tile label (h3 ×11, h2 ×3) | abcplus | 12.6 (0.87) | 500 | +0.043 | 1.39 | upper | 12.6 |
| Link list (a ×11) | abcplus | 12.6 (0.87) | 500 | +0.002 | 1.39 | none | 12.6 |
| Navigation, footer links | abcplus | 12.6 (0.87) | 400 | +0.043 | 1.29 | upper | 12.6 |
| Character field (one div) | mono | 12.6 (0.87) | 400 | +0.043 | 1.29 | none, nowrap | 12.6 |

- [M] Three families are loaded (`mono`, `abc`, `abcplus`); the type rows use two, `abcplus` and `mono` (desktop, families_loaded, type).
- [M] Three sizes carry all text: 37.7, 22.6, 12.6 px. Display ÷ body = 1.67 (37.7 ÷ 22.6, derived); display ÷ label = 2.99 (derived).
- [M] The paragraph runs 72 characters per line, 46.4 em, 3 lines at 1440; 31 characters, 15.7 em, 7 lines at 390 (paragraphs). The h1 is 18 words: 3 lines at 1440, 5 at 390, with font feature `"ss05"` (headings, type).
- [M] At 12.6 px, roles differ only by case, weight and tracking (rows above). [M-seen] These small words are drawn in fixed-width letterforms like the character field (`desktop-scroll-0.jpg`, crop of `desktop-full.jpg`), while their reading names `abcplus`. [M] The instrument records only the first name of the computed family, so which loaded face draws them is not settled.

**Layout geometry**
- [M] Shared left edge at 0.01 of the width (16 blocks); further edges at 0.26 (14), 0.51 (6), 0.75 (4); one four-column grid declared (desktop, alignment).
- [M] Pictures start at x 0.011, 0.258, 0.506 or 0.753 and are 0.24, 0.48 or 0.98 of the width — one, two or four columns (desktop, pictures).
- [M] The h1 is not on the first screen: y 1.166 screens, x 0.011, width 0.607, 3 lines (desktop, headings); at 390: y 1.252, x 0.042, width 0.917, 5 lines.
- [M] By geometry the largest first-screen picture is an img 0.483 wide × 0.966 high, 0.46 of the screen (desktop, first_screen). [M-seen] It is hidden under the character field in every viewport shot.
- [M] Centred text share 0 on both views. Text columns per section: 2, 1, 2, 2, 1, 3, 1, 2, 1 (desktop, sections).
- [M] Columns are left empty: the third section has a two-column picture at x 0.011 and a one-column picture at x 0.753; the three-tile section's text ends at x 0.742 (desktop, pictures, sections). [M-seen] `sheet-desktop.jpg` shows those gaps as bare ground.

**Section rhythm**
- [M] 9 sections at 1440: 1.02, 0.22, 1.02, 0.98, 0.94, 0.53, 1.23, 0.23, 0.30 screens, starting at 0.05, 1.17, 1.48, 2.60, 3.69, 4.73, 5.37, 6.86, 7.17 (desktop, sections). The 22.6 px paragraph lies between the seventh and eighth and is not read as a section at 1440 (it is at 390).
- [M] The long ones (0.94–1.23) hold one or two pictures and a label of 2–3 words; the short ones hold the sentence (0.22) and the link lists (0.23).
- [M] One ground, rgb(245, 245, 240), share 1; ink rgb(24, 24, 24); 0 ground changes (colour, sections).
- [M] Median space above/below content 0 / 16 px; the h1 block has 0 above, 81 px below. The 808 and 1072 px "space above" readings belong to full-width pictures read as the section ground (`ground_is_picture`) with the label beneath — an artefact, not empty space.
- [M] Characters per screen: 30, 620, 27, 27, 19, 78, 7, 1136, 296 — picture sections under 80, text strips 296–1136.
- [I] Long, nearly wordless picture sections with two short dense text strips: a contact sheet with captions, one sentence near the top and the small print at the end.

**Image treatment**
- [M] 12 pictures at 1440: 0 bleed, 0 rounded (radius 0px), 0 shadows, 0 filters, 0 masks; all 12 carry blend mode `multiply`; 1 is a video (fit `contain`, reported playing) (desktop, pictures).
- [M] Ratios 0.8 (7 pictures), 0.84 (2), 1.78, 1.33, 6.75; width shares 0.48 (5), 0.24 (4), 0.98 (3). Only the 6.75 one reads as cropped (own ratio 6.82) — a rounding-level difference.
- [M] The 6.75 picture is 1408×208 in the footer with words on it. [M-seen] It is the site name as a wordmark picture, footer links overlapping its lower edge (crop of `desktop-full.jpg`).
- [M-seen] Tiles are photographs (clothing on a figure, a metal ring, a snow scene, a child's portrait); most carry a small screenshot of a web page floating in the middle of the photograph or on a blurred backdrop (`sheet-desktop.jpg`, crops of `desktop-full.jpg`). Each label sits directly under the tile's lower-left corner; no frame, no caption box.
- [I] `multiply` over a pale ground would let a picture's pale areas take the page colour; the screenshots cannot confirm how visible that is.

**Motion behaviour**
- [M] On load: no heading or picture reveal; `h1_settles_ms` null (the h1 is below the first screen). The only "reveals" are navigation buttons appearing in one frame (16 ms) at 2495 ms (1440) and 2443 ms (390) after the sampler began — a switch, not a fade (load.reveals).
- [M-seen] The character field differs in every shot: a row of `=` at 0.35 s, a sparse dotted column at 1.25 s, full hourglass shapes at 3.5 s, then dots, dashes or `N` at the scroll positions; the word CLICK sits at its centre at 1440 (`desktop-load-*.jpg`, `desktop-scroll-*.jpg`). [M] It is one `div` of 2989 characters in `mono`; 0 canvases; LCP is a `div` of 1,294,560 px at 336 ms (desktop, type, built_with, lab). [I] The field is animated by rewriting text, which the sampler (position and opacity) does not record, and it waits for a click the headless run never gave.
- [M] On scroll (script-driven): 0 reveals, 0 held elements beyond 1 fixed throughout (2 at 390), 0 parallax, 0 sideways, 0 scale changes among 23 followed elements (26 at 390) (scroll).
- [M] `lag_ms` 0 at every step, baseline [84, 0, 0]; with a script moving the page this says nothing about smoothing of real input. No library flag is set (gsap, lenis, locomotive, three all false).
- [M] Declared: no transition durations, no easings, 0 elements with keyframes, 0 running animations, 0 reduced-motion rules in 2 readable stylesheets (motion_declared).
- [M] Pointer: two text links probed, nothing changed, transition 0s. Reduced motion: 1 reveal on load, the same as normally; 0 animations either way.

**Responsive transformations**
- [M] h1 37.7 → 27.8 px (ratio 0.74, derived; 2.62 → 7.13 vw); paragraph 22.6 → 22.8 px; all 12.6 px text unchanged.
- [M] Edges 4 → 1 (0.04, 40 blocks); declared grid 4 columns → none; median text columns 2 → 1.
- [M] Sections 9 → 11: 1.18, 0.30, 1.18, 1.13, 0.30, 0.57, 0.57, 0.57, 0.38, 0.23, 0.39. The three-tile row becomes three stacked links of 0.57 screens each, counted as sections — a sectioning artefact.
- [M] Pictures 12 → 11, all 0.92 of the width, same ratios (0.8, 0.84, 1.78, 1.33); pairs stack (first pair tops 0.06 and 0.64 screens). The footer wordmark is absent from the 390 picture list; [M-seen] it is visible in `sheet-mobile.jpg`.
- [M] Navigation: 6 links, no menu button → 1 link and a menu button (first_screen.bar, navigation). Motion: the same absence; touch ignored instead of wheel.

**Surfaces**
- [M] 0 filled or framed boxes, 0 shadows, 0 hairlines, 0 gradients (surfaces).
- [M] 3 filled buttons, 32 px high, radius 4px, 12.6 px uppercase: two with ground rgba(24, 24, 24, 0.1) and dark ink, one with ground rgb(24, 24, 24) and pale ink; 0 outlined.

**Reusable principles [I, each with its evidence]**
1. Give everything that is not the statement one small size and separate roles by case, weight and tracking. Evidence: 12.6 px carries labels, links, navigation and buttons; three sizes in all (desktop, type).
2. Show the grid by leaving columns empty instead of filling every row. Evidence: edges 0.01 / 0.26 / 0.51 / 0.75; tile widths 0.24 / 0.48 / 0.98; a row with tiles at x 0.011 and 0.753 only; a three-tile row ending at 0.742.
3. A modest display size is enough when nothing competes with it; let weight and tight tracking do the work. Evidence: h1 37.7 px (2.62 vw), 1.67× body, weight 720, −0.03 em, and it is the largest text on the page.
4. Caption by position, not by box. Evidence: 0 framed boxes, 0 shadows, radius 0px on every picture; one label under each tile; 16 px below content.
5. Make rhythm from tile ratio and width on a constant ground rather than from colour or motion. Evidence: ratios 0.8 / 0.84 / 1.33 / 1.78; widths of 1, 2 and 4 columns; 1 ground, 0 changes; 0 scroll reveals.
6. A first screen that takes scroll input away hides the page from anyone, or anything, that does not click. Evidence: wheel and touch ignored; all viewport shots show only the field.

**Against our existing record**
- [M] The record's surface is dark (`paper` #181818, luminance 0.094, principle `dark-page`); today both views read ground rgb(245, 245, 240) at share 1 and ink rgb(24, 24, 24) — the record's paper value is today's ink.
- [M] Type agrees where the record has it: display 38 px / 720 / −0.0297 / 1.03 against 37.7 / 720 / −0.03 / 1.03. The record has no body level (`not-in-capture`); today there is a 22.6 px paragraph (500, −0.02 em, 1.14). The record's label is 13 px uppercase with weight, tracking and leading not recorded; today 12.6 px, weight 500 or 400, +0.043 em, leading 1.39 or 1.29.
- [M] Section count (9), media count (12) and aspects agree. The record's pacing (1.22, 0.26, 1.22 …; page 8.9 screens) was taken at a 756 px high viewport, today's (1.02, 0.22, 1.02 …; 7.47) at 900; they are not comparable screen for screen.
- [M] The record holds a 0.1 s `background-color, color` transition and keyframes `blinker`, `agent-pulse`; today: no declared transitions, 0 elements with keyframes, no change on the two links probed. The two disagree and today's evidence cannot say which is right.
- The record lacks: the 390 view; the character field over the first screen; that wheel and touch are ignored; `multiply` on every picture; the body paragraph.

**Not measurable here** — the page as seen after the field is clicked away, and whether anything reveals then; behaviour under a real wheel or finger (smoothing, lag); the field's animation timing; what the video shows (covered in every shot); hover on tiles (only two text links were probed); whether a dark state exists (a SETTINGS item is seen in the navigation, nothing more).

### C.11 lpas — https://lpas.com/

**Measured**: [M] status 200 on both views; 10.4 screens at 1440, 9.48 at 390; `failed` is empty; wheel and touch were accepted. [M] The first block is held for 4.8 screens at 1440; the contact sheet shows that stretch blank (a capture effect), so it is read from `desktop-scroll-*.jpg` and the `held` / `sideways` readings.

**Creative thesis [I]** — The first screen does not leave: it holds while vertical scrolling pushes five sector cards across it sideways, so the range of the practice is walked through before any body text is read. Everything after is a plain white document in one face at one weight, where size alone marks rank. Carried by: h1, video and a button held 4.8 screens (desktop, scroll.held); 19 elements moving sideways at 0.67–0.92 px per px scrolled (scroll.sideways); one family, weight 400 in every row but one (type); two grounds with one change (colour).

**Typography system**

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Largest display = h1 | Aeonik | 75 (5.21) | 400 | 0 | 1.0 | none | 46 |
| Section heading (h2 ×6: card titles, statement) | Aeonik | 56 (3.89) | 400 | 0 | 1.1 | none | 44 |
| Large link list on the closing photograph (footer a ×5) | Aeonik | 50 (3.47) | 400 | 0 | 1.1 | none | 32 |
| Sub-heading (header h2, one footer link) | Aeonik | 38 (2.64) | 400 | 0 | 1.1 | none | 28 |
| Small heading (h2 ×1) | Aeonik | 28 (1.94) | 400 | 0 | 1.3 | none | 24 |
| Body, titles (p, a, h3) | Aeonik | 16 (1.11) | 400 | 0 | 1.35 | none | 16 |
| Small body (p, nav a, spans) | Aeonik | 14 (0.97) | 400 | 0 | 1.35 | none | 14 |
| Label (menu button, spans, links) | Aeonik | 12 (0.83) | 400; one row 600 | 0 | 1.4 | none | 12 |

- [M] One family loaded and used; weight 400 in every row except a 12 px row at 600 (48 characters); tracking 0 and no case transform anywhere (type).
- [M] 8 sizes: 75, 56, 50, 38, 28, 16, 14, 12 px. Display ÷ body = 4.69 (75 ÷ 16); h1 ÷ h2 = 1.34 (derived). Leading loosens as size falls: 1.0, 1.1, 1.3, 1.35, 1.4.
- [M] Line length: the 16 px paragraph runs 103 characters per line, 50 em (800 px), 3 lines; two 14 px paragraphs run 62–66 characters, 33 em (463 px), 12–14 lines (desktop, paragraphs). At 390: 44–49 characters, 21.3–24.3 em. [M-seen] The 16 px paragraph is the statement's body (crop of `desktop-full.jpg`); the long 14 px paragraphs cannot be located in the screenshots.
- [M] 10 h2 on the page; the h1 is 9 words in 3 lines at 1440, 5 at 390 (headings).

**Layout geometry**
- [M] Left edge 0.03 (28 blocks), second edge 0.5 (8 blocks) (desktop, alignment). Declared grids: 22 columns ×19, 26 ×6, 24 ×3, 2 ×5, 3 ×1.
- [M] h1 at x 0.035, y 0.683, width 0.625, height 0.25, 3 lines, start-aligned: the lower left of the first screen (first_screen.h1).
- [M] The largest first-screen picture is the video at 1.0 × 1.0, share of screen 1. Text spans x 0.035–0.994, y 0.039–0.933. One filled button; no bar (height 0, static, 1 link). [M-seen] The first card already shows at the right edge (`desktop-scroll-0.jpg`).
- [M] Centred text share 0. Text columns per block: 1, 2, 1, 2, 0, 2 (sections).
- [M] Work grid: pictures 0.47 and 0.23 of the width at x 0.03 / 0.501 / 0.736 in the first row and 0.032 / 0.267 / 0.499 in the second — a 2:1:1 split, mirrored (pictures).

**Section rhythm**
- [M] 6 blocks at 1440: 5.80, 0.42, 1.25, 0.51, 1.00, 0.69 screens, starting at 0, 6.02, 6.55, 7.93, 8.71, 8.71 (sections).
- [M] The long one is first: 5.80 screens holding the h1, the video and the card rail; its content fills the first screen with 4320 px below it, the distance of the hold. Its −92 px "space above" is a negative-spacing artefact.
- [M] The last two blocks read at the same top (8.71): the bleed photograph (1.00) and the dark footer (0.69). [M-seen] `desktop-scroll-100.jpg` shows the photograph above and the footer below it, while `desktop-full.jpg` leaves the footer's stretch white. Overlap and white stretch are capture artefacts of a layered footer.
- [M] Grounds in order: white ×4, rgb(38, 38, 38) ×2 — 1 change; shares 0.83 / 0.17; most text ink is grey rgb(116, 116, 116), share 0.55 (colour). [M-seen] The card panels are flat brown, pale blue, grey-green and peach (`desktop-scroll-25.jpg`, `-50.jpg`); these are not in the ground readings.
- [M] In the three white sections: 0 px above content, 51–57 px below.
- [M] Characters per screen: 71, 997, 312, 4311, 83, 387 — the held block is the sparsest, the updates list the densest. [M-seen] The list's rows are cut to one line with an ellipsis (crop of `desktop-full.jpg`), so 4311 counts text that is not all visible.
- [I] Nearly five screens of one slow sideways scene, then four short white sections in about two and a half screens: one long breath, then brisk business.

**Image treatment**
- [M] 13 pictures at 1440: 2 bleed (video, closing photograph), 7 cropped, 0 rounded (all 0px), 0 shadows, 2 with words on them, all fit `cover`; 2 video elements on the page, 1 in the picture list (pictures, built_with).
- [M] Video: 1440×900, own ratio 1.78 shown at 1.6, filter brightness(0.5), words on it, playing.
- [M] Rail: 5 imgs about 1002×799 (ratio 1.25, own 1.47–1.61), 0.7 of the width at rest, at x 0.781, 1.315, 1.85, 2.384, 2.918 screens — off to the right; filter brightness(1). Their top of −0.1 screens is a reading inside the held block.
- [M] Grid: 6 imgs, all ratio 1.6, uncropped, 678×424 and 334×209. Closing photograph: 2016×1260, 1.4 of the width from x −0.2.
- [M] `masked` is 0 for every picture. [M-seen] The two large grid pictures have one corner cut diagonally, as has the small video frame of the intro (`desktop-scroll-75.jpg`, `desktop-load-3.5s.jpg`); the mask reading misses this.
- [M-seen] Subjects are buildings — exteriors at dusk and by day, furnished interiors. A rail card is a photograph above a flat colour panel carrying a 56 px title, a two-line descriptor and a counter (`desktop-scroll-25.jpg`); grid pictures have a name and a place beneath (`desktop-scroll-75.jpg`).

**Motion behaviour**
- [M-seen] Load: an empty dark screen at 0.35 s; letters stacking in a centred column at 1.25 s; at 3.5 s four words in two pairs either side of a small video frame (`desktop-load-*.jpg`; `mobile-load-3.5s.jpg` shows the same).
- [M] Load readings: the video settles from 245 to 1440 px wide and an img from 771 to 1003 px; 1 long move; 3 masked travels (button 20 px, h1 20 px, img 92 px) of 154 ms each, 505 ms after the sampler began (it began at 293 ms); `h1_settles_ms` 659 (desktop, load). LCP is the h1 at 6672 ms at 1440 and 280 ms at 390; CLS 0.178 / 0.232 (lab, one run). [I] The 154 ms travels happen under the intro and look like layout settling; the h1's visible entrance comes after the 3.5 s shot and is not timed by these readings.
- [M] Scroll reveals at 1440: 23 elements, all fades from opacity 0, fade 467 / 467 / 533 ms (quartiles); 2 also rise 6 px in 267–301 ms; kinds h2 6, p 6, img 6, li 4, h3 1; 2 stagger groups, gaps 100 / 101 / 499 ms. Example: a card title starts at 1786 ms, its descriptor and first list item at 2286, the next items at 2385, 2485, 2586.
- [M] Held: 34 elements — video, h1 and a button for 4.8 screens; 13 for about 2.0, 4 for 1.5, 13 for 1.0, 1 for 0.5; 2 fixed throughout. `sticky_inside` is 0 in the held block and 4 in the work section.
- [M] Sideways with scroll: 19 elements; the examples travel 1.18–1.51 screens leftward at 0.67–0.92 px per px scrolled. Scale with scroll: 5 imgs narrow from 1003 to 784–786 px. Parallax 0 at 1440.
- [M] Smoothing: lag 1024 ms median (890–1026) against baseline 0; `lenis` true, `gsap` false (desktop).
- [M] Declared: 0.3 s on 122 elements, 1.2 s on 6, 0.2 s on 3, 0.5 s and 0.1 s on 1 each; easings cubic-bezier(0, 0, 0.13, 0.99) ×71, ease ×56, cubic-bezier(0.14, 0.83, 0.4, 1) ×6; 0 elements with keyframes; 0 reduced-motion rules in 5 readable stylesheets.
- [M] Reduced motion: reveals on load 0 against 3 normally. Pointer: the menu button does not change (transition 0.3s); two list links change a transform inside them.

**Responsive transformations**
- [M] h1 75 → 46 px (0.61); h2 56 → 44 (0.79); 50 → 32; 38 → 28; 28 → 24; 16, 14, 12 unchanged. Display ÷ body 4.69 → 2.88 (derived). h1 width 0.625 → 0.846.
- [M] The hold is gone: held elements 0, sideways-with-scroll 0; the first block is 1.00 screen and the five cards become five stacked blocks of 0.33 screens (mobile, sections, scroll). 9 elements drift sideways by themselves during the run (sideways.drifting). [M-seen] In `sheet-mobile.jpg` the five panels stand shifted into the right half. [I] That is their state before entering; they slide in from the right as each comes into view.
- [M] Blocks 6 → 14: 1.00, 0.33 ×5, 0.24 (0 characters — an empty wrapper, an artefact), 0.68, 0.20, 1.13, 1.07, 0.85, 1.00, 1.12.
- [M] Pictures 13 → 8: video 390×844 shown at 0.46; six grid pictures 347×217 at 0.89 of the width, ratio 1.6 kept, stacked; closing photograph at 0.46 and 1.4 of the width. No card picture is in the 390 list, yet the scroll run records an img beside a card title fading in over 634 ms; the two readings disagree.
- [M] Kept: fades 467 / 528 / 599 ms on 26 elements, 9 rising 8 px in 266–300 ms, stagger gaps 100 / 100 / 500 ms. Changed: lag 0 and `lenis` false; 1 img with parallax rate −0.06.
- [M] Menu button on both views. Edges 0.06 (58 blocks), 0.16 (4), 0.51 (8). Dark ground share 0.17 → 0.24.

**Surfaces**
- [M] 6 filled or framed boxes, all radius 0px; 0 shadows; 10 hairlines (at 390: 0 boxes, 21 hairlines); 0 gradients.
- [M] 1 filled button: ground rgba(14, 14, 14, 0.6), white ink, radius 6px, 30 px high, 16 px text; 5 outlined buttons. [M-seen] The outlined ones are small circles with an arrow beside text links (crops of `desktop-full.jpg`).

**Reusable principles [I, each with its evidence]**
1. One face at one weight: rank by size and leading only. Evidence: Aeonik 400 in all rows but one; tracking 0; no uppercase; 8 sizes from 75 to 12 px; leading 1.0 → 1.4.
2. If a section is held, let the scroll move something at close to its own speed. Evidence: 0.67–0.92 px sideways per px scrolled; 5 cards over a 4.8-screen hold.
3. Text over a moving picture needs the picture dimmed by one fixed amount and nothing else. Evidence: brightness(0.5) on the video; white ink; 0 gradients, 0 shadows.
4. Reveal in reading order on a fixed step. Evidence: title first, support 500 ms later, list items 100 ms apart; fade 467 ms; travel 6–8 px.
5. Hold one picture ratio through a grid and vary only width. Evidence: 6 grid pictures at 1.6, uncropped, at 0.47 and 0.23 of the width; at 390 still 1.6 at 0.89.
6. Take the held scene apart on the phone instead of shrinking it. Evidence: held elements 0 at 390; five blocks of 0.33 screens; h1 ratio 0.61.

**Against our existing record**
- [M] Type agrees: 75 / 1.0 / 400, 56 / 1.1, 38 / 1.1, 16 / 1.35 and ratio 4.69 in both. The record has no label level; today there are 14 px and 12 px rows (12 px at 400 and 600), and sizes 50 and 28 px.
- [M] The record has 5 sections (6.71, 0.5, 1.47, 0.6, 1.99; page 12) from a 756 px high viewport; today 6 blocks (5.80, 0.42, 1.25, 0.51, 1.00, 0.69; page 10.4) at 900. Same order, the closing part read as two blocks; screen counts are not comparable across the two heights.
- [M] The record marks scroll, pinning, sequence, interaction and reduced motion as not measured and describes the rail in prose. Today's numbers: 4.8 screens held; 19 elements sideways at 0.67–0.92 px per px; rail pictures narrowing 1003 → 784–786 px; fades 467 ms with 100 / 500 ms gaps; lag 1024 ms; load reveals 3 → 0 under reduced motion with no reduced-motion rule in the stylesheets.
- [M] The record's rail media are 1.37–1.38 at 0.556–0.565 of the width; today they read 1.25 at 0.7 at rest and change width with scroll, so each figure is a snapshot.
- The record lacks: the 390 view (no hold, 14 blocks, h1 46 px); the intro sequence; the cut corners; the cards' colour panels.

**Not measurable here** — when the h1 becomes visible after the intro and how long the intro runs (the sampler covered about 5.7 s; the two LCP readings disagree); which elements the 2.0- and 1.0-screen holds are beyond the five examples; the card panel colours; hover on pictures; whether the video plays as intended (headless); any consent banner (hidden by the instrument, not answered); lag under a real trackpad.

### C.12 atelier — no URL: authored recipe `lib/blueprints/atelier.bp.json`, our own render measured from a local `file://` page

**Measured**: [M] This is our own render of an authored recipe with sample content, not a third-party site: status 200; 9.23 screens at 1440, 9.94 at 390; `failed` is empty; wheel and touch accepted. [M] Lab timings (LCP 400 ms, 18 requests) come from a local file and are not comparable with the network pages. [M] 1 of 4 stylesheets was unreadable, so declared-motion counts may be low; the 1440 load sampler recorded 71 frames in 5690 ms, so its durations are coarse. [M-seen] The sample text mixes two subjects and two languages (`sheet-desktop.jpg`), so line counts and text density describe the sample.

**Creative thesis [I]** — The thesis is the recipe's, not a studio's: the record states that atelier mirrors lpas and differs only in id, source and display family, so on paper it is the lpas idea — a held first screen with a sideways rail over dimmed video, then statement, 2:1:1 grid, dated list, photograph footer — with the h1 in a serif. The render measured here does not carry that idea: it is a nine-section paper-coloured page of split first screen, sticky feature list, numbered steps, one very large centred statement, a marquee, a priced list and a form on a dark band. Carried by: 0 videos and 0 bleeding pictures (pictures); nothing held longer than 0.6 screens and 0 sideways-with-scroll (scroll); three families (families_loaded); serif sizes from 28 to 316.8 px (type).

**Typography system**

| Role | Face (as loaded) | 1440: px (vw) | Weight | Tracking (em) | Leading | Case | 390: px |
|---|---|---|---|---|---|---|---|
| Largest display (footer wordmark) | Cormorant Garamond | 316.8 (22) | 400 | 0 | 0.85 | none | 85.8 |
| Statement h2 | Cormorant Garamond | 159.8 (11.1) | 400 | −0.02 | 1.08 | none | 43.3 |
| Step numerals (li) | Cormorant Garamond | 115.2 (8) | 400 | −0.04 | 0.85 | none | 46.8 |
| Form heading h2 | Cormorant Garamond | 86.4 (6) | 400 | 0 | 1.1 | none | 42 |
| h1 (one word italic) | Cormorant Garamond | 66 (4.58) | 400 | 0 | 1.0 | none | 29 |
| List heading h2 | Cormorant Garamond | 63.4 (4.4) | 400 | 0 | 1.3 | none | 36 |
| Sub-heading h3 (features; step text) | Cormorant Garamond | 44 (3.06); 34.6 (2.4) | 400 | −0.01 | 1.12 | none | 28; 24 |
| Section heading h2 | Cormorant Garamond | 28 (1.94) | 400 | 0 | 1.3 | none | 28 |
| Body (lead p; lists; small p) | Manrope | 19 (1.32); 18; 17; 16 | 400 (prices 500) | 0 | 1.4; 1.35 | none | same |
| Navigation, buttons | Manrope | 15 (1.04) | 500 | 0 | 1.35 | none | 15 |
| Label | JetBrains Mono | 12 (0.83); 14.4 (1) | 400 (footer h5 700) | +0.08 | 1.35; 1.5 | upper | 12; 13 |

- [M] 3 families loaded and used; 17 distinct sizes at 1440 (serif 10, sans 5, mono 2) (desktop, type).
- [M] h1 ÷ lead paragraph = 3.47 (66 ÷ 19, derived); largest text ÷ lead paragraph = 16.7 (derived). The h1 is the fifth-largest size at 1440 and the sixth at 390.
- [M] Section headings (h2, 28 px) are smaller than what they head: h3 at 44 px and 34.6 px.
- [M] Paragraph: 64 characters per line, 29.6 em (562 px), 2 lines at 1440; 32 characters, 17.9 em at 390 (paragraphs).
- [M] Headings wrap `balance`; display text is split into spans (`h1 › span`, `h2 › span` in the reveal readings); the 56 px marquee row is `nowrap`, −0.02 em.
- [M-seen] The caron of "š" is drawn detached and oversized above the letter in the serif at every display size — h1, form heading, footer wordmark — and correctly in the sans and the mono (`desktop-scroll-0.jpg`, crops of `desktop-full.jpg`). [I] The display face as loaded lacks that glyph and the accent comes from a fallback. (Checked afterwards and wrong: the face draws the letter itself, with its accent set apart — see E.1, G11.)

**Layout geometry**
- [M] Left edge 0.07 (27 blocks). Second-column starts scatter: 0.48 (8 blocks), 0.49 (4), 0.5 (3), 0.52 (3), 0.53 (3); also 0.29 (3), 0.3 (4), 0.74 (3). Declared grids: 2 columns ×14, 4 ×1 (desktop, alignment).
- [M] h1 at x 0.073, y 0.339, width 0.24, height 0.169, 2 lines of 4 words, left-aligned (first_screen.h1).
- [M] Largest first-screen picture: img at x 0.499, y 0.255, 0.428 × 0.456, 0.2 of the screen. Text ends at y 0.659, with 260 px below content: the lowest third of the first screen is empty.
- [M] Bar: fixed, 82 px, transparent, 4 links; 2 filled buttons on the first screen. [M-seen] The bar is absent from the shots at 25–100 % (`desktop-scroll-25…100.jpg`), and the logo at top left is a pale mark barely distinguishable from the ground (`desktop-scroll-0.jpg`, `mobile-scroll-0.jpg`).
- [M] Centred text share 0.13 (the statement section). Text columns per section: 1, 2, 2, 3, 1, 1, 1, 1, 0.

**Section rhythm**
- [M] 9 sections at 1440: 1.00, 1.84, 1.13, 1.50, 0.36, 0.85, 0.94, 0.90, 0.72 screens (sections).
- [M] The long ones: 1.84 (feature list, `sticky_inside` 1, three pictures at one position) and 1.50 (statement, `sticky_inside` 1, 329 px above and 737 px below its content).
- [M] Grounds: rgb(244, 239, 227) ×7, rgb(15, 42, 20), then a third pale ground — 2 changes; shares 0.82 / 0.10 / 0.08 (colour).
- [M] Space above / below content: 229/260, 165/280, 162/130, 329/737, 92/194, 131/131, 123/179, 130/130, 201/368 px.
- [M] Characters per screen: 229, 107, 165, 86, 792, 106, 411, 187, 381 — all but one under 420.
- [I] Even, airy pacing: sections near one screen, one idea each, no long scene and no dense passage; the two sticky sections lengthen the scroll without adding content.

**Image treatment**
- [M] 7 pictures: 0 bleed, 0 video, 0 filters, blends or masks; radius 12px on 3 and 0px on 4; 1 shadow (the first picture); width shares 0.37–0.44; shown ratios 1.5 (2), 0.9 (3), 1.15, 1.05; every source is 1.5 (`own_ratio`) (desktop, pictures).
- [M] The three 0.9 pictures share one position (x 0.49–0.50, top 1.31–1.32 screens) with fit `contain`; "cropped" with `contain` is a reading artefact. [M-seen] The photograph sits letterboxed in a taller pale framed panel with empty bands above and below, beside the feature text (`desktop-scroll-25.jpg`, crop of `desktop-full.jpg`).
- [M] Two pictures are `cover`, cropped to 1.15 and 1.05; two are shown at their own 1.5.
- [M-seen] Subjects are sample photographs: a restaurant garden, laid tables, a plate, a lectern at night; each stands beside a text column (`sheet-desktop.jpg`).

**Motion behaviour**
- [M] Load at 1440: two h1 line spans rise 72 px inside a mask over 914 and 1031 ms from 367 ms; the picture fades in 567 ms from 598 ms; the paragraph in 434 ms from 731 ms; the h1 settles at 1398 ms (sampler began at 301 ms; 71 frames). At 390 (340 frames): spans rise 30–31 px in 522–589 ms, starting at 337 and 404 ms; picture fade 500 ms; paragraph 433 ms; h1 settles at 926 ms.
- [M] While the page stands still the h1 narrows from 445 to 346 px (390: 196 → 152) and its italic word from 140 to 108 px (load.scale.settling); CLS 0.002. [I] A face swap after first paint.
- [M] Scroll at 1440: 9 reveals — 8 fades of 400 / 400 / 451 ms (quartiles); 2 travels of 7 and 11 px in 267–350 ms; 1 masked `h2 › span`; kinds figure 3, li 3, p 2; one stagger group at 67 ms. At 390: 15 reveals, fades 400 / 400 / 434 ms; 12 travels of 13 / 25 / 26 px in 250 / 350 / 383 ms; 4 masked `h2 › span`; stagger 66 / 72 / 84 ms.
- [M] Held at 1440: 12 elements for 0.5–0.6 screens (the five examples are figures and imgs); 0 fixed throughout. At 390: 6 elements for 0.5 screens — the statement's h2, its three word spans and its paragraph.
- [M-seen] In `desktop-scroll-50.jpg` the statement's first word is dark and the other two pale; in `desktop-scroll-25.jpg` the current feature is dark and an earlier one pale. [I] Colour steps through words and list items with the scroll while the block is held.
- [M] Parallax 0 at 1440, 1 img at −0.07 at 390; sideways 0, drifting 0; scale with scroll 0. [M-seen] A marquee line of 56 px serif crosses the fifth section (`sheet-desktop.jpg`). [M] Its 12 spans are not among the followed elements, so its drift is unmeasured; 1 element has keyframes and 3 animations run (motion_declared).
- [M] Smoothing: lag 1007 ms median (1006–1189) against baseline 0 at 1440; 0 at 390; `gsap`, `scroll_trigger`, `lenis` true on both views.
- [M] Declared: 0.5 s ×6, 0.35 ×5, 0.3 ×4, 0.25 ×3, 0.9 ×3, 1.2 ×3, 0.45 ×1; easings cubic-bezier(0, 0, 0.13, 0.99) ×16, cubic-bezier(0.2, 0.8, 0.2, 1) ×6, ease ×3; 7 reduced-motion rules.
- [M] Reduced motion: reveals on load 0 against 5; animations 0 against 1. Pointer: the button's own transform reads `none` → identity matrix (no visible change — a reading artefact) while something inside it transforms (0.35 s); text links change a pseudo-element's transform.

**Responsive transformations**
- [M] h1 66 → 29 px (0.44); statement 159.8 → 43.3 (0.27); numerals 115.2 → 46.8; form heading 86.4 → 42; wordmark 316.8 → 85.8 (22 vw on both, tracking 0 → −0.03); h3 44 → 28; the 28 px h2, all sans sizes and the 12 px mono unchanged. h1 ÷ lead paragraph 3.47 → 1.53 (derived).
- [M] Sections 9 → 9: 1.00, 1.51, 0.91, 1.50, 0.27, 0.85, 1.34, 1.49, 1.08. The statement stays 1.50 screens with 353 px above and 733 px below its content. [M-seen] `sheet-mobile.jpg` shows that as a long empty stretch.
- [M] Median columns 1; edges 0.06 (51 blocks), 0.05 (4), 0.07 (5).
- [M] Pictures: 7, 0.87–0.89 of the width; shown ratios 1.5, 0.77 (the framed three), 1.15, 1.5, 1.05. The feature section loses its sticky element (`sticky_inside` 1 → 0). [M-seen] The framed panel stacks above the list (`sheet-mobile.jpg`).
- [M] Bar 82 → 98 px, links 4 → 2, no menu button on either view. [M-seen] The two section links are gone at 390 with nothing in their place (`mobile-scroll-0.jpg`).
- [M] The h1 takes 0.39 of the 390 width in 2 lines. The 85.8 px wordmark is in the 390 type readings; [M-seen] it is not visible at the page end in `mobile-scroll-100.jpg`, and at 1440 it is cut by the page end (`desktop-scroll-100.jpg`).
- [M] Kept: masked line rise, 400 ms fades, stagger about 67–72 ms, the statement hold. Changed: travel 7–11 → 13–26 px; lag 1007 → 0 ms; the held feature panel dropped.

**Surfaces**
- [M] 4 filled or framed boxes (radius 12px ×3, 0px ×1); 1 shadow; 19 hairlines (16 at 390); 0 gradients (surfaces).
- [M] Filled buttons 46 px high, radius 0px, 15 px text: 2 with ground rgb(15, 42, 20) and pale ink, 1 pale; 0 outlined. Square buttons stand next to 12px-rounded pictures and boxes.

**Reusable principles [I, each with its evidence]**
1. Size must follow rank: a section heading may not be smaller than the items under it, nor the h1 smaller than incidental display text. Evidence: h2 28 px above h3 at 44 and 34.6 px; h1 fifth-largest at 1440, sixth at 390.
2. A second column needs one edge. Evidence: starts at 0.48, 0.49, 0.5, 0.52, 0.53 here; lpas has 0.03 and 0.5 only.
3. Check a display face against the content's alphabet before setting it large. Evidence: detached caron at 66–316.8 px, seen in three places.
4. Tie a masked line rise to the line's own height so it reads alike on both views. Evidence: 72 px rise at 66 px type, 30–31 px at 29 px; masked on both.
5. When type shrinks on the phone, the held section's length must shrink with it. Evidence: statement 159.8 → 43.3 px while the section stays 1.50 screens with 733 px empty below.
6. One corner rule per page. Evidence: pictures at 12px (3) and 0px (4), boxes at 12px and 0px, buttons at 0px.

**Against our existing record** (compared with today's `lpas` readings, since the record says atelier mirrors lpas)
- [M] Type sizes: record and recipe give display 75 px (leading 1.0, weight 400, Instrument Serif), h2 56, h3 38, body 16, ratio 4.69 — the lpas values, which lpas still measures today in one family. Our render: h1 66 px in Cormorant Garamond; no text at 75 or 38 px, and 56 px only as the marquee; body 19–16 px; 3 families and 17 sizes against 1 family and 8 sizes.
- [M] Held sections: lpas holds its first block 4.8 screens with 19 elements moving sideways and pictures narrowing 1003 → 784–786 px. Our render holds nothing longer than 0.6 screens, has 0 sideways-with-scroll and 0 scale-with-scroll, and a first section of 1.00 screen. The record's five sections (pinned-hero-rail 6.71, manifesto, work-grid-sticky, updates-list, footer-photo-offices) do not appear; 9 sections were measured.
- [M] Motion durations: scroll fades 400 ms (lpas 467); stagger 67 ms (lpas 100 and 500); travel 7–11 px at 1440 (lpas 6); lag 1007 ms (lpas 1024), Lenis flagged in both; the most-counted easing is the same string, cubic-bezier(0, 0, 0.13, 0.99). The render declares seven durations from 0.25 to 1.2 s where lpas concentrates on 0.3 s (122 elements) and 1.2 s (6). The render has 7 reduced-motion rules, lpas 0.
- [M] Pictures: lpas 13 — one full-screen video at brightness(0.5), 2 bleeding, all radius 0px, 0 shadows, a grid at one ratio 1.6, widths 0.23–1.4. Our render 7 — 0 video, 0 bleed, widths 0.37–0.44, radius 12px on 3, 1 shadow, shown ratios 0.9–1.5. The recipe says `radius` 0, `bleed` true, `video_hero` true.
- [M] Colour and buttons: recipe paper #ffffff, ink #262626, button height 45, radius 0, `filled` false; render ground rgb(244, 239, 227), ink rgb(15, 42, 20), buttons filled, 46 px, radius 0px.
- Context, from the render's input file beside the page (`direction.json`), not from `evidence.json`: the sample direction names its own face hint, paper, ink and its own sequence of beats. This evidence therefore cannot apportion the differences above between the recipe, the direction and the renderer.
- The record lacks any measurement of a render: its completeness fields read `authored`, with mobile `missing`.

**Not measurable here** — network timings (local file); how the recipe renders under a different direction or with a video and bleeding pictures (one direction was rendered); the marquee's speed; whether the 1440 hold includes the statement (the examples list only figures); precise load durations at 1440 (71 frames); hover on pictures and the form's behaviour; rules in the one unreadable stylesheet.

### C.13 Our existing records against today's measurements

Collected from the "Against our existing record" paragraphs above. All **[M]** unless marked.

- **Two records no longer describe the page that is served.** deepbook: the record holds another family, other sizes,
  a black surface, a five-screen pinned section and four libraries; today's page (reached after a redirect to another
  domain) is a white document in a different face with nothing held and none of those libraries. aino: the record's
  surface is dark (`#181818`); today the ground is pale and that value is the ink.
- **Every record was captured at one desktop viewport 756 px high.** Today's readings are at 900. Section heights and
  page lengths in screens are therefore not comparable one to one, and a page that sizes sections to the viewport
  (belgrade-arbor: ten of fourteen sections at exactly one screen) measures differently at each height.
- **Several records file a level under the wrong role**, because roles were hand annotations: crav's headline under
  `h2` and its running text as a 40 px label face; white-desert's body as the 22 px serif when most characters are at
  14 px; units' display as its 33 px section heading when a 72 px line now stands on the first screen; cerebrium's
  statements, which are large paragraphs, have no level at all.
- **Where the page has not changed, type agrees closely**: butter, cerebrium, lpas, tengile, belgrade-arbor and
  white-desert match the record's display size, weight, tracking and leading to within rounding or a few pixels.
- **No record holds any motion value.** All say scroll, pinning, sequence, interaction and reduced motion were not
  measured; they carry library flags, a few transition strings and a prose note. Today's readings add hold lengths,
  sideways rates, reveal durations and gaps, the scroll lag, load order, pointer changes and the reduced-motion run.
  Two prose notes could not be confirmed (a 1.8 s ground crossfade on units; a blur-and-scale picture reveal on
  tengile — the sampler does not read blur).
- **No record holds a phone value**, as each already says (`mobile: missing`).
- **Recipe details that match nothing on the live page**: button height and corner on butter, tengile, crav,
  halfdays and white-desert; media radius 0 on crav and units, where pictures are rounded today.

[I] The records are honest about what they lack, and what they hold is mostly still true of the type. What they
cannot do is describe how a reference moves, how it changes on a phone, or how its sections are paced on a viewport
other than the one captured — which is most of what distinguishes these pages. The recipes built from them remain
working assets; they should not be mistaken for a description of the references.

---

## Part D — Across the references

Eleven third-party references; `atelier` is our own recipe and is left out. Every table is generated from the
evidence files by script, not typed. All of Part D is **[M]** except the paragraphs marked [I]. A count such as
"6 of 11" always names the pages in the tables.

### D.1 Type

**Table D.1 — Type at 1440**

| Reference | Families carrying text | Largest type px (vw) | Weight | Case | Tracking em | Leading | Body px / leading | Largest ÷ body | Small label px | Characters per line (width in em) | h1: px · lines · words |
|---|---|---|---|---|---|---|---|---|---|---|---|
| aino | abcplus, mono | 37.7 (2.62) | 720 | none | -0.03 | 1.03 | 22.6 / 1.14 | 1.7 | 12.6 | 72 (46.4) | 37.7 · 3 · 18 |
| belgrade-arbor | Work Sans, editorialOld | 239.8 (16.65) | 300 | uppercase | 0 | 1 | 16 / 1.2 | 15 | 14 | 61 (34.2) | 151.2 · 1 · 2 |
| butter | ABCDiatype, DieGrotesk | 107.6 (7.47) | 400 | none | 0.003 | 0.99 | 16 / 1.31 | 6.7 | 13.5 | 45 (29.7) | 107.6 · 2 · 3 |
| cerebrium | ABC Favorit Trial, Suisse Intl, Suisse Intl Mono | 144 (10) | 500 | none | 0 | 1 | 18 / 1.5 | 8 | 13 | 49 (31.6) | 86.1 · 3 · 7 |
| crav | Modak, Mouse Memoirs | 504 (35) | 400 | none | 0 | 0.5 | 25.9 / 1.1 | 19.5 | 13 | 71 (23.7) | 432 · 1 · 2 |
| deepbook | PP Mori | 71.2 (4.94) | 700 | none | 0 | 1.05 | 16 / 1.6 | 4.5 | 14 | 69 (41.3) | no h1 element |
| halfdays | Metropolis, SuisseIntl | 26 (1.81) | 500 | uppercase | -0.01 | 1 | 16 / 1.35 | 1.6 | 14 | 57 (28.7) | no h1 element |
| lpas | Aeonik | 75 (5.21) | 400 | none | 0 | 1 | 14 / 1.35 | 5.4 | 14 | 66 (33) | 75 · 3 · 9 |
| tengile | Inter, PP Fragment | 120 (8.33) | 220 | uppercase | -0.02 | 0.9 | 16 / 1.25 | 7.5 | 14 | 56 (28.7) | 120 · 2 · 2 |
| units | Aeonik Pro, Bunch | 72 (5) | 850 | none | 0 | 1 | 16 / 1.8 | 4.5 | 12 | 51 (29.8) | no h1 element |
| white-desert | Cardinal Classic Long, Inter Tight, Oswald | 320 (22.22) | 400 | uppercase | 0 | 0.9 | 14 / 1.5 | 22.9 | 14 | 58 (29.3) | 256 · 1 · 1 |

**Table D.2 — Type at 390**

| Reference | Largest type px (vw) | Largest ÷ body | h1 px · lines | Body px | Characters per line | Largest type, 390 ÷ 1440 |
|---|---|---|---|---|---|---|
| aino | 27.8 (7.13) | 1.2 | 27.8 · 5 | 22.8 | 31 | 0.74 |
| belgrade-arbor | 95.9 (24.6) | 6 | 66.3 · 2 | 16 | 37 | 0.40 |
| butter | 56.7 (14.55) | 3.5 | 56.7 · 3 | 16 | 27 | 0.53 |
| cerebrium | 72 (18.46) | 4.2 | 45 · 3 | 17 | 40 | 0.50 |
| crav | 136.5 (35) | 7 | 101.4 · 1 | 19.5 | 47 | 0.27 |
| deepbook | 40 (10.26) | 2.5 | — | 16 | 38 | 0.56 |
| halfdays | 26 (6.67) | 1.6 | — | 16 | 45 | 1.00 |
| lpas | 46 (11.79) | 3.3 | 46 · 5 | 14 | 46 | 0.61 |
| tengile | 48.8 (12.5) | 2 | 48.8 · 2 | 24 | 30 | 0.41 |
| units | 38 (9.74) | 2.4 | — | 16 | 48 | 0.53 |
| white-desert | 200 (51.28) | 12.5 | 80 · 1 | 16 | 40 | 0.62 |

1. **Few families.** One or two families carry the text on 9 of 11 pages and three on the other two. None uses more.
2. **Scale comes in three regimes, with nothing between them.** Largest type ÷ body is 1.6–1.7 on two picture-led
   pages (aino, halfdays; largest type under 2.7 vw), 4.5–8.0 on six (deepbook, units, lpas, butter, tengile,
   cerebrium; 4.9–10 vw) and 15–23 on three (belgrade-arbor, crav, white-desert; 16.7–35 vw). No page sits between
   1.7 and 4.5 or between 8 and 15. (On one of the two quiet pages the largest word of the first screen is a drawn
   image, so the reading understates what a visitor sees there.)
   [I] Scale is decided, not drifted into: a page is quiet, classic or a poster. This is the measured form of
   Vignelli's rule that scale may be broken only knowingly [S 37] — and it is not his own figure of display at about
   twice the text, which nine of the eleven exceed.
3. **The largest type is set tight.** Leading 0.5–1.05 (median 1.0) on all eleven; tracking zero or negative on ten,
   +0.003 em on one.
4. **Text is ordinary in size.** Body 14–25.9 px, median 16, leading 1.1–1.8, median 1.35. Small labels 12–14 px.
   ("Body" is the style that carries the most running text in paragraphs and list items.)
5. **Lines are moderate.** 45–72 characters per line, median 58, in a block 24–46 em wide (median 30). At 390:
   27–48, median 40. [I] Müller-Brockmann's figure is in words — about ten per line, seven for long text [S 34] — so
   the two are not the same unit; they point the same way.
6. **Headlines are short.** Of the eight pages with an `h1`, it runs 1–3 lines at 1440 and 1–9 words on seven; the
   eighth is an 18-word statement set small. At 390 it runs 1–5 lines. (A heading split into word spans can read one
   line more than is seen: one page reads 2 and shows 1.)
7. **Three pages have no `h1` element at all** (deepbook, halfdays, units). That is a lapse of those pages, not a
   principle.
8. **On a phone contrast halves.** Largest ÷ body falls to 1.2–12.5, median 3.3; the largest type is 0.27–1.0 of
   its 1440 size in pixels while growing to 6.7–51 vw.

### D.2 Geometry and rhythm

**Table D.3 — Geometry and rhythm at 1440**

| Reference | Page, screens | Sections | Section height: median / longest (screens) | Grounds / changes | Dark share | Centred text | Edge most blocks share | Edges blocks align to (share of width) | Grids declared (columns) | Largest picture on first screen (share, kind) | Filled buttons on first screen | Characters per screen (median section) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aino | 7.47 | 9 | 0.94 / 1.23 | 1 / 0 | 0 | 0 | 0.01 | 0.01 0.26 0.51 0.75 | 4 | 0.46 img | 0 | 30 |
| belgrade-arbor | 26.31 | 14 | 1 / 9 | 2 / 2 | 0.04 | 0.1 | 0.04 | 0 0.04 0.46 0.53 0.55 0.63 | — | 1 video | 0 | 248 |
| butter | 16.53 | 14 | 1.1 / 2 | 2 / 1 | 0 | 0.19 | 0.05 | 0.03 0.05 0.08 0.2 0.28 0.51 0.59 0.66 0.74 0.82 | 12, 24 | 1 canvas | 0 | 168 |
| cerebrium | 12.08 | 13 | 0.64 / 3.52 | 3 / 4 | 0.42 | 0 | 0.51 | 0.03 0.21 0.35 0.51 0.53 0.57 0.62 0.67 0.75 0.87 | 2, 3, 12, 20 | 1 canvas | 4 | 400 |
| crav | 11.59 | 11 | 1 / 2.61 | 3 / 4 | 0.14 | 0.44 | 0.03 | 0.03 0.04 0.18 0.2 0.75 | 3 | 0.26 img | 1 | 83 |
| deepbook | 8.97 | 9 | 1.01 / 1.61 | 4 / 5 | 0 | 0.02 | 0.06 | 0 0.06 0.1 0.31 0.39 0.47 0.51 0.56 0.64 0.8 | 2, 3, 4, 6 | 0.9 img | 1 | 230 |
| halfdays | 4.15 | 6 | 0.64 / 1.14 | 1 / 0 | 0 | 0.13 | 0.5 | 0.01 0.18 0.31 0.42 0.5 0.67 0.7 | 2 | 0.9 img | 0 | 131 |
| lpas | 10.4 | 6 | 1 / 5.8 | 2 / 1 | 0.17 | 0 | 0.03 | 0.03 0.5 | 2, 3, 22, 24, 26 | 1 video | 1 | 387 |
| tengile | 12.83 | 13 | 0.94 / 1.41 | 2 / 1 | 0 | 0 | 0.01 | 0.01 0.18 0.34 0.51 0.67 0.75 | 6, 12 | 1 video | 0 | 360 |
| units | 9.56 | 8 | 0.7 / 4.34 | 1 / 0 | 0 | 0 | 0.01 | 0.01 0.12 0.14 0.43 0.45 0.75 | 2, 3, 30 | 0.82 img | 4 | 347 |
| white-desert | 23.1 | 16 | 1 / 10.5 | 3 / 2 | 0.18 | 0.29 | 0.51 | 0 0.01 0.04 0.1 0.18 0.34 0.35 0.51 0.67 | 12, 13 | 1 video | 5 | 76 |

1. **A section is about one screen.** The median section is 0.64–1.1 screens on all eleven, median 1.0.
2. **Most pages have one long section, and it is an event.** A section of 2.5 screens or more on 6 of 11 (2.6, 3.5,
   4.3, 5.8, 9 and 10.5 screens). On the five longest it is a held sequence (Table D.5).
3. **Text is flush left.** No centred text block on 6 of 11 (≤ 2%); ≤ 20% on 9. The two above that (29% and 44%) are
   poster pages. This agrees with flush left as the default and centred setting for lapidary text [S 37].
4. **Outer margins are small.** The first edge blocks align to is 1–6% of the width on all eleven — 14–86 px at 1440.
   Small outer margins give tension [S 37].
5. **Fine grids, few edges.** Declared grids run from 12 to 30 columns on eight pages, yet blocks share only 2–10
   left edges, and those fall on halves, thirds, quarters and sixths of the width (for example 1, 26, 51, 75% on one
   page; 1, 18, 34, 51, 67, 75% on another).
6. **The first screen is a picture.** The largest picture, video or canvas covers 82% of the first screen or more on
   9 of 11 (all of it on 7): video on four, canvas on two, a still on three. The two exceptions are a two-picture
   index and a type poster. [I] A first screen is led by an image or by type; none is a small picture beside a
   column of text.
7. **Few buttons on the first screen.** No filled button on 5 of 11, one on three, four or five on three (the bar's
   included). These are lower bounds: the reading counts an element with a filled ground of its own and missed two
   buttons that are visible on one page.
8. **The ground rarely changes.** One to four distinct grounds and 0–5 changes down the page, median 1; three pages
   never change ground. Only one page is substantially dark (42% of its length); seven have no dark section.
   (The reading is of each section's own ground. It missed one dark footer, so a count can be one low; and on one
   page all colour sits in cards on a single ground.)
9. **Density varies by an order of magnitude between pages** — a median of 30 to 400 characters per screen of a
   section — and each page keeps to its own end of that range.

### D.3 Pictures and surfaces

**Table D.4 — Pictures and surfaces at 1440**

| Reference | Pictures | Bleed | Cropped | Rounded | Shadowed | Words on them | Video | Portrait / landscape | Sections on a picture | Filled or framed boxes | Elements with a CSS shadow | Rules: on elements + by pseudo-elements + hr | Main button (height, corner) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aino | 12 | 0 | 1 | 0 | 0 | 1 | 1 | 9 / 3 | 2 | 0 | 0 | 0 + 0 + 0 = 0 | 32 px, 4px |
| belgrade-arbor | 38 | 8 | 14 | 4 | 0 | 12 | 6 | 20 / 14 | 6 | 0 | 0 | 10 + 0 + 0 = 10 | 64 px, pill |
| butter | 44 | 2 | 2 | 9 | 0 | 2 | 34 | 28 / 4 | 1 | 9 | 0 | 0 + 0 + 0 = 0 | 47 px, 8px |
| cerebrium | 11 | 0 | 10 | 0 | 0 | 2 | 0 | 4 / 7 | 0 | 27 | 0 | 2 + 14 + 0 = 16 | 54 px, 7px |
| crav | 29 | 1 | 20 | 9 | 0 | 3 | 0 | 14 / 8 | 1 | 0 | 0 | 0 + 0 + 0 = 0 | 42 px, pill |
| deepbook | 12 | 6 | 4 | 0 | 0 | 4 | 1 | 1 / 10 | 2 | 13 | 0 | 13 + 0 + 0 = 13 | 52 px, 4px |
| halfdays | 18 | 1 | 2 | 0 | 0 | 1 | 0 | 16 / 2 | 1 | 0 | 3 | 0 + 0 + 0 = 0 | 63 px, 8px |
| lpas | 13 | 2 | 7 | 0 | 0 | 2 | 1 | 0 / 13 | 1 | 6 | 0 | 10 + 0 + 0 = 10 | 30 px, 6px |
| tengile | 32 | 3 | 3 | 0 | 0 | 2 | 1 | 25 / 6 | 3 | 29 | 0 | 0 + 0 + 0 = 0 | — |
| units | 19 | 0 | 6 | 8 | 0 | 1 | 0 | 14 / 4 | 1 | 40 | 0 | 1 + 0 + 0 = 1 | 48 px, pill |
| white-desert | 20 | 9 | 16 | 1 | 0 | 15 | 1 | 7 / 13 | 5 | 27 | 5 | 1 + 2 + 0 = 3 | 40 px, 2px |

1. **No picture has a CSS shadow**: 0 of 248 pictures. Elements with any CSS shadow: none on 9 of 11 pages. (A shadow
   painted into a picture file is not read; one soft shadow under a product panel was seen.)
2. **Corners are a page decision.** No rounded picture on 6 of 11; 31 of 248 pictures in all, on five pages.
3. **Words stand on pictures on every page** — 45 pictures in all, from 1 to 15 per page.
4. **Pictures leave their column**: at least one runs edge to edge on 8 of 11 (32 in all). A third of all pictures
   (85 of 248) are drawn at a ratio other than their own. (Both flags over-count a little: an oversized picture in a
   clipped frame reads as edge to edge though it keeps its margin on screen, and a tilted or letterboxed picture
   reads as cropped; the per-reference analyses name the cases.)
5. **Portrait is common**: the majority of pictures on 7 of 11. Landscape leads on the architecture page and on
   software pages.
6. **Boxes divide the references.** No filled or framed box on four pages; 6–13 on three; 27–40 on four.
   [I] The page with the most (40) is built on tinted panels as its idea; two of the others owe the count to square
   picture holders. A grid of boxes is a decision some references make, never a default all of them share.
7. **Rules are rare**: ten or more on 4 of 11 (10, 10, 13, 16), three or fewer on the other seven — counting rules
   on elements, rules drawn by pseudo-elements and `hr`. Lines drawn as backgrounds or vectors are not read: one
   page's full-height column lines and row rules on two others were seen and not counted.
8. **One button style.** Height 30–64 px; corners of 2–8 px on seven pages, a full pill on three.

### D.4 Motion

**Table D.5 — Motion measured at 1440 (scrolled in steps of 0.6 screen)**

| Reference | h1 settled, ms after navigation | Elements followed | Reveals | Fade ms (median) | Travel px / ms (median) | Stagger gap ms | Reveals inside a split heading | Held: screens (elements) | Parallax: elements (rate) | Sideways with scroll | Size with scroll | Drifting | Scroll lag ms | Input |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aino | — | 23 | 0 | — | — / — | — | 0 | — | 0 | 0 | 0 | 0 | 0 | script (ignored wheel) |
| belgrade-arbor | — | 152 | 99 | 633 | 11 / 300 | 50 | 96 | 8.0 (57), 7.5 (35), 4.0 (1) | 0 | 0 | 4 | 0 | 1189 | wheel |
| butter | 3886 | 348 | 98 | 666 | 9 / 366 | 50 | 76 | 1.0 (12), 0.5 (7) | 0 | 19 | 5 | 27 | 1007 | wheel |
| cerebrium | 3350 | 170 | 24 | 350 | 12 / 217 | 68 | 4 | 3.0 (6) | 0 | 0 | 0 | 0 | 1016 | wheel |
| crav | 4646 | 103 | 39 | 151 | 21 / 283 | 50 | 16 | — | 8 (0.07) | 2 | 22 | 5 | 990 | wheel |
| deepbook | — | 234 | 129 | 17 | 12 / 250 | 50 | 99 | — | 0 | 0 | 0 | 3 | 0 | wheel |
| halfdays | — | 90 | 6 | 289 | 26 / 65 | — | 0 | — | 0 | 0 | 0 | 0 | 0 | wheel |
| lpas | 952 | 73 | 23 | 467 | 6 / 301 | 101 | 0 | 5.0 (3), 2.0 (13), 1.5 (4) | 0 | 19 | 5 | 0 | 1024 | wheel |
| tengile | 3163 | 111 | 36 | — | 12 / 1836 | — | 0 | 1.0 (1) | 25 (0.53) | 1 | 0 | 3 | 990 | wheel |
| units | — | 72 | 1 | 784 | 14 / 484 | — | 0 | 3.5 (10), 3.0 (5), 1.5 (6) | 0 | 21 | 0 | 0 | 791 | wheel |
| white-desert | 1200 | 56 | 1 | 615 | — / — | — | 0 | 5.0 (4), 4.0 (1), 3.5 (2) | 12 (0.7) | 8 | 1 | 0 | 1024 | wheel |

**Table D.6 — What a phone keeps (390)**

| Reference | Page, screens (1440 → 390) | Sections (1440 → 390) | Reveals | Fade ms | Travel px | Held: screens (elements) | Parallax (rate) | Sideways with scroll | Scroll lag ms | Menu button |
|---|---|---|---|---|---|---|---|---|---|---|
| aino | 7.47 → 7.11 | 9 → 11 | 0 | — | — | — | 0 | 0 | 0 | yes |
| belgrade-arbor | 26.31 → 30.27 | 14 → 19 | 102 | 633 | 17 | 5.0 (81), 4.5 (11) | 4 (0.21) | 0 | 0 | yes |
| butter | 16.53 → 15.33 | 14 → 14 | 93 | 666 | 15 | — | 0 | 0 | 0 | yes |
| cerebrium | 12.08 → 12.13 | 13 → 14 | 35 | 349 | 18 | — | 0 | 2 | 0 | yes |
| crav | 11.59 → 9.25 | 11 → 13 | 47 | 150 | 39 | — | 6 (-0.07) | 0 | 0 | yes |
| deepbook | 8.97 → 9.32 | 9 → 10 | 109 | 17 | 13 | — | 1 (-0.06) | 0 | 0 | no |
| halfdays | 4.15 → 6.25 | 6 → 6 | 0 | — | — | — | 0 | 0 | 0 | yes |
| lpas | 10.4 → 9.48 | 6 → 14 | 26 | 528 | 8 | — | 1 (-0.06) | 0 | 0 | yes |
| tengile | 12.83 → 14.98 | 13 → 19 | 0 | — | — | 1.0 (1) | 35 (0.5) | 0 | 0 | yes |
| units | 9.56 → 8.77 | 8 → 8 | 0 | — | — | — | 0 | 0 | 0 | yes |
| white-desert | 23.1 → 22.83 | 16 → 21 | 0 | — | — | 2.0 (1), 1.0 (4) | 6 (0.7) | 0 | 0 | yes |

**Table D.7 — Reduced motion, declared motion and one lab run**

| Reference | Reveals in the first 6 s: normally → with reduce-motion | Reduced-motion rules in readable CSS (unreadable sheets) | Commonest transition s | Commonest easing | Built with | LCP ms 1440 / 390 | CLS 1440 / 390 | Transferred MB 1440 |
|---|---|---|---|---|---|---|---|---|
| aino | 1 → 1 | 0 (0) | — | — | — | 336 / 276 | 0 / 0 | 1.4 |
| belgrade-arbor | 0 → 0 | 0 (0) | 0.65 | cubic-bezier(0.4, 0, 0.2, 1) | lenis, next | 424 / 440 | 0 / 0 | 8.9 |
| butter | 6 → 9 | 0 (3) | 0.8 | cubic-bezier(0, 0, 0, 1) | lenis, next | 244 / 244 | 0 / 0 | 5.6 |
| cerebrium | 24 → 25 | 1 (0) | 0.2 | cubic-bezier(0.645, 0.045, 0.355, 1) | lenis, swiper | 3000 / 688 | 0 / 0 | 2.6 |
| crav | 3 → 2 | 0 (0) | 0.3 | cubic-bezier(0.4, 0, 0.2, 1) | lenis, next | 4872 / 4836 | 0.005 / 0.02 | 6.1 |
| deepbook | 0 → 0 | 6 (0) | 0.18 | ease-out | — | 252 / 352 | 0 / 0 | 10.2 |
| halfdays | 0 → 1 | 1 (15) | 0.3 | linear | shopify, swiper | 1152 / 912 | 0 / 0.015 | 8.2 |
| lpas | 3 → 0 | 0 (0) | 0.3 | cubic-bezier(0, 0, 0.13, 0.99) | lenis, wordpress | 6672 / 280 | 0.178 / 0.232 | 5.7 |
| tengile | 20 → 21 | 0 (0) | 0.3 | ease | lenis, next | 272 / 192 | 0.042 / 0 | 6.7 |
| units | 5 → 4 | 2 (0) | 0.7 | cubic-bezier(0.19, 1, 0.22, 1) | gsap, lenis, scroll_trigger, swiper, wordpress | 3040 / 644 | 0.007 / 0 | 3.5 |
| white-desert | 3 → 3 | 0 (0) | 0.3 | cubic-bezier(0.5, 1, 0.89, 1) | lenis, next | 420 / 340 | 0 / 0 | 7.6 |

1. **Scrolling is smoothed on 8 of 11 at 1440** — a lag of 0.8–1.2 s against about 0 on an empty page — and on none
   at 390. The same eight load one smoothing library. The three that scroll natively are a shop, an index page whose
   body is locked against input, and the page that has changed since our capture. [I] This matches what a studio
   says of its own practice: smoothing for experience, native scroll for shops [S 7].
2. **Reveals are small and quick.** The median travel is 6–26 px (median of the medians 12 px); the median fade
   151–784 ms on eight pages (median 541), with a ninth switching in one frame; travel times 217–484 ms on seven of
   nine.
3. **Stagger is 50 ms** on four of the six pages where siblings reveal in sequence, 68 and 101 ms on the other two.
4. **Headings are revealed in parts** — word by word or line by line — on 5 of 11 (4 to 99 parts in the scrolled
   stretch).
5. **Not everything reveals.** The share of followed elements that reveal at all is 0–65%; under 15% on five pages.
6. **Holds are common, long and desktop-only.** Something is held for a screen or more on 7 of 11, for 3–8 screens
   on five. At 390 only three keep a hold, and shorter.
7. **Rails**: movement sideways tied to scroll on 4 of 11 (8–21 elements), on none of them at 390.
8. **Parallax** on 3 of 11 at 1440 (rates 0.07, 0.53, 0.7).
9. **Slow intros.** The headline animates in on 6 of 11 and is fully visible 0.95–4.65 s after navigation; on four
   of the six later than 3 s.
10. **Reduced motion is mostly ignored.** Of the seven pages with three or more reveals on load, six keep them when
    the visitor asks for less motion; one drops them. Reduced-motion rules were found in the readable CSS of 4 of 11.
11. **Performance is not their strength** in this one lab run: LCP above 2.5 s on 4 of 11 at 1440, layout shift
    above 0.1 on one, 1.4–10.2 MB transferred (median 6.1).

[I] Points 9–11 are why the Standard takes its motion-safety and performance thresholds from WCAG and Core Web
Vitals and not from the references: on those three counts the references are evidence of what studios trade away,
not of what to copy.

### D.5 Decisions that recur

[I] Each is a rule a different site could follow, named with the references whose measurements carry it (Part C).

1. **One ground, and colour delivered by something else** — by the media (butter), by cards (units), by the
   pictures (tengile, aino, halfdays). Where the ground does change, it changes with the job of the section, not with
   every section (cerebrium, deepbook, crav).
2. **One heading owns the scale and everything else stays at reading size** (tengile: 120 px, then 48; aino: one
   sentence at 37.7 px over a page of 12.6 px; white-desert and belgrade-arbor: one word across the screen).
3. **Rank by one means at a time.** One face at one weight, ranked by size alone (lpas, butter); or one small size,
   ranked by case, weight and tracking (aino, halfdays); or face against face (units, cerebrium, white-desert).
   No reference ranks by size, weight, case and colour all at once.
4. **Headings arrive in parts, in place**: words or letters fading or rising inside a mask on one duration and a
   50 ms beat (butter, belgrade-arbor, crav, deepbook; tengile for its one heading).
5. **One scroll-coupled set-piece per page, on wide screens only**: a held index (cerebrium), a held rail (lpas,
   units, white-desert, butter), a held stage of text (belgrade-arbor). On a phone it is replaced by a stack or a
   swipe row on four of them and kept on two.
6. **Picture size and ratio change from section to section and hold within a row** (tengile, halfdays, lpas, aino).
7. **A caption is placed, not boxed**: under the tile's corner (aino), on the picture at a fixed spot (halfdays).
8. **A screen can be spent on one sentence** (white-desert: 320 px above three sections; butter: 357 px above and
   below a statement; belgrade-arbor: 71 characters per screen in its held stage).
9. **The headline sits low or runs across**: in the lower 40% of the first screen on four of the eight pages with an
   `h1`; at 81% of the width or more on four.
10. **On a phone the display shrinks far more than the text, and pictures are re-cut rather than shrunk** (tengile
    × 0.41 against text unchanged; belgrade-arbor × 0.30; halfdays and deepbook swap to portrait crops).
11. **The saturated colour is for action** (white-desert, cerebrium, deepbook).
12. **Emphasis and state by the italic of the same face**, not by a box or a second colour (belgrade-arbor,
    white-desert).

### D.6 What the references do not agree on

[I] Just as useful as the agreements. Scale regime (three), ground (one page dark, most light), boxes (none to
forty), hairlines (none to thirteen), corners (square on six pages, round on five), density (thirteen-fold), holds
(none to eight screens), page length (4 to 26 screens). None of these can be a rule of quality. They are the
decisions an art direction makes — and a page that takes the middle value of each has made none.

---

## Part E — Where Swarmsite stands, and what each finding needs

### E.1 Our own pages on the same instrument

The eight bench sites, each as shipped (the template path) and as composed (the opt-in composition path, the pages
in `bench/runs/judged/`), measured as local files with the same tool on the same day. Evidence:
`bench/runs/_research/ours/`. Two cautions: lab timings of a local file are not comparable with a network page; and
our bench is six software sites and two restaurants while the references are three software, four places, two
products and two services, so some differences — picture counts above all — are of sector as well as of engine.

**Table E.1 — Our pages against the references, reading by reading (1440 unless marked 390)**

| Reading | References (11) | Our composed pages (8) | Our shipped pages (8) |
|---|---|---|---|
| Rules, however drawn (elements, pseudo-elements, hr) | 0–16 (median 1) | 17–50 (median 33) | 16–52 (median 36) |
| Families carrying text | 1–3 (median 2) | 2–3 (median 3) | 2–3 (median 3) |
| Largest type ÷ body | 1.6–22.9 (median 6.7) | 7–16.5 (median 12) | 6.3–16.5 (median 11.3) |
| Largest type, vw | 1.81–35 (median 7.47) | 9.2–20.6 (median 15.86) | 8.33–20.6 (median 15) |
| Largest type, leading | 0.5–1.05 (median 1) | 0.85–0.9 (median 0.85) | 0.85–0.9 (median 0.85) |
| h1 px | 37.7–432 (median 120) | 84.8–228.4 (median 138.5) | 71–176 (median 91) |
| h1 lines | 1–3 (median 2) | 2–3 (median 3) | 2–3 (median 3) |
| h1 width, share of screen | 0.47–0.98 (median 0.81) | 0.26–0.94 (median 0.42) | 0.24–0.87 (median 0.37) |
| Body px | 14–25.9 (median 16) | 18–21 (median 19) | 18–21 (median 19) |
| Body leading | 1.1–1.8 (median 1.35) | 1.16–1.4 (median 1.4) | 1.16–1.4 (median 1.4) |
| Small label px | 12–14 (median 14) | 12–14.4 (median 14) | 12–14.4 (median 14) |
| Characters per line | 45–72 (median 58) | 36–56 (median 48) | 38–56 (median 44) |
| Sizes carrying text | 3–13 (median 8) | 7–17 (median 13) | 6–16 (median 13) |
| Page, screens | 4.15–26.31 (median 11.59) | 6.3–21.16 (median 12.88) | 6.15–18.94 (median 12.15) |
| Sections | 6–16 (median 11) | 7–18 (median 13) | 7–17 (median 13) |
| Section height, median (screens) | 0.64–1.1 (median 1) | 0.71–1.15 (median 0.94) | 0.66–1.14 (median 0.89) |
| Longest section (screens) | 1.14–10.5 (median 2.61) | 1–3.09 (median 1.99) | 1–3.04 (median 1.41) |
| Grounds | 1–4 (median 2) | 2–4 (median 3) | 2–4 (median 3) |
| Ground changes | 0–5 (median 1) | 5–14 (median 10) | 5–14 (median 9) |
| Dark share | 0–0.42 (median 0) | 0.13–0.73 (median 0.39) | 0.2–0.7 (median 0.38) |
| Centred text share | 0–0.44 (median 0.02) | 0.01–0.36 (median 0.05) | 0.03–0.13 (median 0.07) |
| Edge most blocks share | 0.01–0.51 (median 0.04) | 0.03–0.09 (median 0.07) | 0.03–0.16 (median 0.07) |
| Outer margin (first edge) | 0.01–0.06 (median 0.03) | 0.03–0.09 (median 0.07) | 0.03–0.09 (median 0.07) |
| Edges listed | 2–10 (median 6) | 5–10 (median 10) | 5–10 (median 9) |
| Largest picture on first screen (share) | 0.26–1 (median 1) | 0.14–1 (median 0.23) | 0.12–1 (median 0.21) |
| Filled buttons on first screen | 0–5 (median 1) | 2–2 (median 2) | 2–2 (median 2) |
| Characters per screen (median section) | 30–400 (median 230) | 236–440 (median 382) | 244–473 (median 359) |
| Pictures | 11–44 (median 19) | 1–11 (median 5) | 1–8 (median 3) |
| Pictures that bleed | 0–9 (median 2) | 0–1 (median 1) | 0–1 (median 0) |
| Rounded pictures | 0–9 (median 0) | 0–2 (median 1) | 0–3 (median 2) |
| Shadowed pictures | 0–0 (median 0) | 0–3 (median 1) | 0–2 (median 1) |
| Pictures with words on them | 1–15 (median 2) | 0–1 (median 0) | 0–1 (median 0) |
| Filled or framed boxes | 0–40 (median 9) | 0–15 (median 7) | 0–11 (median 8) |
| Elements with a shadow | 0–5 (median 0) | 0–3 (median 2) | 0–2 (median 1) |
| Hairlines | 0–13 (median 1) | 17–50 (median 33) | 16–52 (median 36) |
| Gradients | 0–7 (median 0) | 0–1 (median 1) | 0–0 (median 0) |
| Headline settled, ms after navigation | 952–4646 (median 3350) | 601–1389 (median 1259) | 924–2017 (median 1608) |
| Reveals on load | 0–24 (median 3) | 2–7 (median 4) | 3–7 (median 5) |
| Elements followed while scrolling | 23–348 (median 103) | 81–225 (median 186) | 84–222 (median 210) |
| Reveals while scrolling | 0–129 (median 24) | 9–34 (median 19) | 2–41 (median 30) |
| Share of followed elements that reveal | 0–0.65 (median 0.28) | 0.06–0.21 (median 0.13) | 0.02–0.25 (median 0.17) |
| Fade ms (median) | 17–784 (median 467) | 398–416 (median 400) | 399–699 (median 459) |
| Travel px (median) | 6–26 (median 12) | 10–34 (median 18) | 9–24 (median 20) |
| Travel ms (median) | 65–1836 (median 300) | 301–580 (median 367) | 414–530 (median 447) |
| Stagger gap ms | 50–101 (median 50) | 67–68 (median 67) | 116–120 (median 118) |
| Reveals inside split headings | 0–99 (median 0) | 0–3 (median 0) | 0–2 (median 1) |
| Longest hold (screens) | 0–8 (median 1) | 0–2.5 (median 1.5) | 0–0.5 (median 0) |
| Parallax elements | 0–25 (median 0) | 0–0 (median 0) | 0–1 (median 0) |
| Sideways with scroll (elements) | 0–21 (median 1) | 0–0 (median 0) | 0–0 (median 0) |
| Size with scroll (elements) | 0–22 (median 0) | 0–1 (median 1) | 0–3 (median 1) |
| Drifting (elements) | 0–27 (median 0) | 0–0 (median 0) | 0–0 (median 0) |
| Scroll lag ms | 0–1189 (median 990) | 1007–1021 (median 1007) | 994–1072 (median 1023) |
| 390: largest ÷ body | 1.2–12.5 (median 3.3) | 2.4–4.5 (median 3.1) | 2.5–4.5 (median 3.1) |
| 390: h1 lines | 1–5 (median 3) | 2–3 (median 2) | 2–3 (median 3) |
| 390: characters per line | 27–48 (median 40) | 26–39 (median 34) | 26–39 (median 34) |
| 390: page, screens | 6.25–30.27 (median 9.48) | 5.82–25.77 (median 15.08) | 5.98–26.26 (median 15.35) |
| 390: longest hold (screens) | 0–5 (median 0) | 0–0.5 (median 0) | 0–0.5 (median 0) |
| 390: scroll lag ms | 0–0 (median 0) | 0–0 (median 0) | 0–0 (median 0) |
| 390: pictures that bleed | 0–15 (median 2) | 0–2 (median 1) | 0–1 (median 0) |
| LCP ms (local file for ours) | 244–6672 (median 424) | 156–504 (median 172) | 144–1036 (median 492) |
| CLS | 0–0.18 (median 0) | 0–0.08 (median 0) | 0–0.03 (median 0.01) |
| Reduced-motion rules in CSS | 0–6 (median 0) | 7–7 (median 7) | 7–7 (median 7) |

What the table says — all [M]:

- **G1 · The first screen is led by neither picture nor type.** The largest picture covers a median 23% of our
  composed first screens (under 40% on 7 of 8) against 100% on the references; the headline spans a median 42% of the
  width against 81%.
- **G2 · The page is striped.** The ground changes 5–14 times down our pages (median 10) against 0–5 (median 1).
  Dark sections make up a median 39% of the length against 0%.
- **G3 · Everything is ruled.** 17–50 rules per composed page (median 33) against 0–16 (median 1), counted the same
  way on both. Three references draw some lines in ways the count does not read (D.3-7), so their true figures are
  somewhat higher; the direction is not in doubt, the exact size of the gap is.
- **G4 · Few pictures, and some of them boxed.** A median of 5 pictures per composed page against 19. Words stand on
  a picture on at most one per page against at least one on every reference. Four of the eight composed pages put a
  shadow on a picture; none of the 248 reference pictures has one. (An earlier reading of the CSS of 17 other studio
  sites found product screens set with a hairline ring and one soft shadow [M: `REFACTOR.md`, 2026-11-10]. The two
  samples disagree; calibration settles it, not assertion.)
- **G5 · Dense, narrow, many sizes.** A median 382 characters per screen against 230; an outer margin of 7% against
  3%; 48 characters per line against 58; 13 sizes carrying text against 8.
- **G6 · Two filled buttons on every first screen** (8 of 8) against a median of one and none on five references.
- **G7 · Every page ends the same way.** On 7 of 8 composed pages the largest type on the page is the closing
  wordmark in the footer, at 9–21 vw.
- **G8 · Motion is within range where it exists and narrow in kind.** Fade 400 ms, travel 18 px, stagger 67 ms, the
  headline settled 0.6–1.4 s after navigation, where the six references that animate theirs take 0.95–4.65 s. But no
  composed page has parallax, a rail or a drifting band; headings are revealed in parts on almost none (0–3 parts
  against 4–99 on five references); the longest hold is 2.5 screens. All sixteen pages smooth scrolling, whatever
  the page is for.
- **G9 · Reduced motion is not fully honoured on composed pages.** With reduce-motion asked for, the shipped pages
  drop their load reveals on 7 of 8; three of the eight composed pages keep three or more (7 → 3, 5 → 4, 5 → 3).
  The cause has not been examined; the reading is a Track T finding on our own pages that no check of ours reports
  today.

Four more findings come from the analysis of our own recipe as rendered (C.12), not from the bench:

- **G10 · Size does not follow rank.** In that render the section headings are 28 px above items at 44 and 34.6 px,
  and the headline is the fifth-largest type on the page.
- **G11 · A display face whose accents come apart.** The caron of "š" stands high and detached over the letter in the
  serif at every display size, and sits correctly in the other two faces [M-seen:
  `references/atelier/desktop-scroll-0.jpg`]. Examined afterwards on a clean test page, same day: the letter is drawn
  by the face itself, not by a fallback — the instrument's letter reading confirms it — and the face as served draws
  its lowercase caron and acute that way, while its capitals hold together. So the defect is the choice of face for
  this alphabet, not its loading.
- **G12 · The second column has no single edge**: blocks start at 48, 49, 50, 52 and 53% of the width, where the
  reference it mirrors has two edges on the whole page.
- **G13 · A recipe is not what gets drawn.** The recipe says a held first screen with a rail over video, one family,
  square corners, bleeding pictures. The render under the sample direction holds nothing longer than 0.6 screen and
  has three families, 17 sizes, no video, no bleed, and rounded and shadowed pictures. This evidence cannot apportion
  the difference between recipe, direction and renderer; it does show that the reference's idea did not survive.

What is already inside the reference range and should be left alone: families (2–3), leading of display and text,
body size, headline lines, section height (about one screen), share of centred text, reveal timings, the phone page's
length against the desktop page (0.9–1.2 ×, references 0.8–1.5 ×).

[I] Read together, G1–G7 describe one thing: our pages apply *every* device at medium strength on *every* section —
a band here, a rule there, a modest picture, a second button — where each reference commits to a few decisions and
leaves the rest out. That is the measured meaning of the critic's recurring sentence that the page "thins" or
"becomes a template" below the first screen [M: `bench/runs/judged/*/judge.json`].

### E.2 What can be done with the components that exist

Rules, parameters and briefs. No new form, no new document.

| # | Change | Finding | Where in the engine |
|---|---|---|---|
| 1 | One ground carries the page; a change of ground is an event, at most three a page unless the direction says striped | G2; D.2-8 | grounds of the section forms (`words.py`, `pictures.py`), the renderer's bands, the composers' briefs; a validator over the whole page |
| 2 | Space instead of rules: a hairline budget per page; ruled rows only where the items are tabular | G3; D.3-7 | list form `ledger`, words form `columns`, the renderer's index rows |
| 3 | A first screen led by a picture or by type | G1; D.2-6 | the first-screen composition (`bleed: full`, `at.col`, headline `size`) and the choice among three concepts; a finding in its validator |
| 4 | One filled action | G6; D.2-7 | the first screen's `actions` node; the renderer's button styles |
| 5 | A wider frame, longer lines, a scale of fewer sizes | G5; D.1-5, D.2-4 | the renderer's frame, gutter and type-scale tokens |
| 6 | No shadow on a photograph; one corner decision per page | G4; D.3-1, D.3-2 | the picture forms' CSS; the renderer's photo styles |
| 7 | Words on a photograph more often where there is one | G4; D.3-3 | forms `backdrop` and `card` exist; the pictures brief |
| 8 | Reduced motion honoured inside composed sections | G9; [S 54] | the composed forms' `enter` motion |
| 9 | Headings revealed by line as one page decision | G8; D.4-4 | the renderer's choreography already has a masked line reveal for the template's headings; composed sections do not take it |
| 10 | Smoothed scrolling as a decision by kind of page, off for a shop or a form page | G8; D.4-1; [S 7] | the renderer's scroll set-up |
| 11 | The closing wordmark as one ending among several | G7 | the renderer's footer |
| 12 | Size follows rank: no heading smaller than what it heads; the headline the largest type on its screen | G10 | the renderer's type-scale tokens per beat |
| 13 | A face is set only in an alphabet it draws well | G11 | the type registry (`lib/type/faces.json`): record for each face whether its accented letters hold together in the languages we serve; the instrument reports letters a face does not draw itself (T-19) |
| 14 | One edge per column | G12 | the renderer's column starts |

### E.3 What needs a new composition capability

| # | Capability | Evidence | What exists today |
|---|---|---|---|
| 1 | **A page plan written before any section is composed**: the idea's device and the sections that carry it, the ground plan, a budget per form, where the one long section goes, which sections are dense and which sparse | ART-02 and CMP-05 in the Standard; D.2-2, D.2-8, D.2-9; the critics' verdicts on our composed pages | `page_direction`: one paragraph of text handed from the first-screen composer to the others; each family then composes its own sections without seeing the whole |
| 2 | **A held sequence and a rail as composed forms** | holds of 3–8 screens on 5 of 11, rails on 4 (D.4-6, D.4-7) | template moves only (`pinned-sequence`, `sticky-product`), not composable; composed pages hold at most 2.5 screens |
| 3 | **A motion system per page** — easing, two or three durations, stagger, what reveals and what does not — chosen with the concept and recorded | motion fixed before design [S 18]; the references' consistency (D.4-2, D.4-3, D.4-5) | one renderer-wide choreography, plus an `enter` name per composed form |
| 4 | **More material to compose with**: the client's own pictures from more than one page, details cut from product screens, short loops | a median of 5 pictures against 19 (G4); one reference shows 34 videos | one page captured; commissioned pictures as atmosphere only |
| 5 | **Content that crosses a boundary**: a picture or a headline that runs from one section into the next | CMP-07; seen on the place references (Part C) | `overlap` inside a section only |
| 6 | **Phone parameters for sections** | RSP-01; D.1-8, D.4-6 | the first screen has a phone block (`sm`); sections have one fixed phone arrangement per form |
| 7 | **A focal point per picture** that every crop respects | IMG-08; 85 of 248 reference pictures are cropped | crops are centred |
| 8 | **Type as image**: a headline at poster scale, cut by the edge of the screen | three references at 16.7–35 vw (D.1-2) | headline sizes up to `clamp(54px, 12.2vw, 200px)` [M: `lib/compose/render_ir.py`] |
| 9 | **A vocabulary of signature devices** a concept can name and the renderer can draw | ORG-03; G7 | the closing wordmark, on every page |
| 10 | **A text-measure parameter** on every form | TYP-05; G5 | `cols` on some forms |

### E.4 What needs better visual QA

| # | Change | Evidence | What exists today |
|---|---|---|---|
| 1 | **The instrument in the loop**: every candidate page measured, every reading outside the Standard's thresholds reported as a finding | G1–G9 were all invisible to our QA until this tool ran | the contract measures promises; the critic estimates everything else from screenshots |
| 2 | **Motion is looked at.** | G8, G9 | every QA tool forces motion off before it looks (`?nomotion=1`), so no check and no critic has ever seen our pages move |
| 3 | **The critic's output contract** (Standard §7): defect, evidence, reason, correction, expectation; corrections verified by re-measurement; capability gaps counted | P1, P2, P9 | a score, four axes, five reported sub-scores, a verdict and up to ten fixes; a fix is not checked for effect |
| 4 | **Area levels instead of one taste number**; the page level by rule | Standard §5 | `0.35 design + 0.20 originality + 0.25 craft + 0.20 function` |
| 5 | **The two gates enforced separately** | P1 | `scores.json` already holds taste and contract against separate bars — "reported, not enforced" [M: `lib/swarm/run.py`]; the loop decides on the blend |
| 6 | **Track T checks T-08 to T-17** | [S 54][S 56]–[S 60] | T-01 to T-07 |
| 7 | **Blind human calibration** | P9; Standard §6 | the comparison page exists; no round has been run; the bench holds 8 of the 30 sites planned |
| 8 | **Re-measurement of the references** on a cadence, with drift reported | one of twelve has changed (C.3) | records built once from a desktop capture; `mobile` and `screenshots` marked missing in every record |

---

## Part F — A prioritised plan

Nothing below is implemented. The order follows three rules: measure before changing; close measured gaps with the
parts that exist before building new ones; and start the one thing that needs people — calibration — early, because
it cannot be hurried.

### F.1 The order

| Step | What | Why first (evidence) | Done when |
|---|---|---|---|
| **1** | **The instrument and the critic's contract** (E.4-1, -2, -3, -5). Every job writes its measurements; readings outside the Standard become findings; the critic returns Standard §7 findings; technical and creative gates decide separately | Every later step is judged by it. The tool exists and has already measured sixteen of our pages. Without it, nine gaps stayed invisible (E.1) | each job has a measurement file and a findings list; the eight bench pages are re-read; no change to how a page looks |
| **2** | **The measured gaps, with existing parts** (E.2, in this order: grounds, hairlines, first screen, frame and scale, one action, picture surfaces, reduced motion, heading reveal, scrolling by kind, endings) | Each is a reading far outside the reference range today (G1–G9) and each has a lever that exists. One commit per change, with the readings before and after on the bench | each reading inside the Standard's threshold on at least 7 of 8 bench pages; two like-for-like critic readings not lower than before |
| **3** | **The page plan** (E.3-1) | The single thing the critics name on almost every composed page — the idea stops after the first screen — and the only place a ground plan, a form budget and a density curve can live. Studios decide flow, pacing and hierarchy before anything is drawn [S 26] | a page-level document validated like the others; sections composed against it; ART-02 and CMP-05 findings fall on the bench |
| **4** | **Material** (E.3-4, E.3-7) | A composer cannot place pictures it does not have: 5 against 19 | more of the client's own pictures reach the job; crops keep their subject |
| **5** | **The composed long section and the motion system** (E.3-2, E.3-3) | Present on about half the references (D.4-6, D.4-7); today outside the composable vocabulary | one hold or rail per page where the content has steps; one motion record per page; Track T motion checks pass |
| **6** | **Phone composition, type as image, signature devices, boundaries** (E.3-5, -6, -8, -9, -10) | Real, but each matters on fewer pages than steps 2–5 | by findings count after step 5 |
| **H** | **Human calibration**, alongside steps 1–3 (E.4-7; Standard §6) | A claim of level means nothing without it [P9]. The first round is worth running after step 2, when shipped and composed pages differ enough to compare | anchor set of 30 frozen; one blind round by at least five designers; agreement and correlation reported against the Standard's bars |

### F.2 What this plan deliberately leaves out

- **More agents or more templates.** Nothing measured points at either. The gaps are in what the page commits to
  (E.1) and in what our QA can see (E.4).
- **Tuning the critic until the scores rise.** A score that moves without a measurement moving is noise [P2].
- **Copying a reference.** Part D.5: the references disagree on every stylistic choice. What transfers is that
  each choice was made.
- **Treating the references as a model for accessibility or performance** (D.4-9 to -11).
- **Any claim of "studio quality" before a blind round** [P9].

### F.3 Decisions that are the owner's

1. Shadows on product screens: the eleven references have none; an earlier sample of studio sites had one (G4).
2. Smoothed scrolling: today on every page; the references and a studio's own rule say by kind of page (E.2-10).
3. The closing wordmark on every page (G7): keep as the house's signature, or make it one ending among several.
4. Who rates in the blind rounds, and the budget for them and for growing the bench from 8 to 30 sites.
5. Whether screenshots of the references may be shown to the critic's model as visual anchors. Today the critic is
   calibrated to three of them by description only; the screenshots are research-only material.

### F.4 What can honestly be expected

No score is promised. What is promised is that every step states in advance which readings it will move and by how
much, and is kept or dropped on that. Step 2 will make our pages measurably closer to how the references use
ground, rule, picture and margin; whether designers then prefer them is exactly what step H is for.

---

## Sources

Opened on 2026-11-10. "Summary" = read through a fetch tool that returns a summary, so wording was not checked word
for word; "full text" = read in a browser. An entry is identified by its address; the words before the address
describe the page and are not checked as its exact title. Numbers are shared with
`SWARMSITE_STUDIO_QUALITY_STANDARD.md`.

**Studios**

1. Active Theory, "The Story of Technology Built at Active Theory" — https://medium.com/active-theory/the-story-of-technology-built-at-active-theory-5d17ae0e3fb4 (full text)
2. Active Theory, "Fiomet Case Study" — https://medium.com/active-theory/fiomet-case-study-9a0180268423 (full text)
3. Active Theory, "Discover Your Patronus" — https://medium.com/active-theory/discover-your-patronus-348971420487 (full text)
4. The Webby Awards, "Crafted with Code: Active Theory" — https://www.webbyawards.com/crafted-with-code/active-theory (summary)
5. Awwwards, talk by Andy Thelander of Active Theory, "Designing with Code" — https://www.awwwards.com/andy-thelander-from-active-theory-designing-with-code.html (summary of a talk page; no transcript)
6. Communication Arts, feature on Active Theory — https://www.commarts.com/features/active-theory (summary; third-party)
7. Locomotive, "Should I use Locomotive Scroll on my project?" — https://medium.com/@LocomotiveMTL/should-i-use-locomotive-scroll-on-my-project-7fc8fa38bcc5 (full text)
8. Locomotive, "Why don't we use front-end frameworks at Locomotive?" — https://medium.com/@LocomotiveMTL/why-dont-we-use-front-end-frameworks-at-locomotive-4ccb20c05bc5 (full text)
9. Awwwards, "Case study: Locomotive presents the Kvell journey" — https://www.awwwards.com/case-study-locomotive-presents-the-kvell-journey.html (summary)
10. Awwwards, "Locomotive by Locomotive wins Site of the Month June: a case study" — https://www.awwwards.com/locomotive-by-locomotive-wins-site-of-the-month-june-a-case-study.html (summary)
11. Awwwards, "Case study: Baillat Studio by Locomotive" — https://www.awwwards.com/case-study-baillat-studio-by-locomotive.html (summary)
12. Awwwards, "Case study: Reinventing Locomotive" — https://www.awwwards.com/case-study-reinventing-locomotive-r.html (summary)
13. Codrops, "Case Study: itsnotviolent.com" — https://tympanus.net/codrops/2020/01/21/case-study-itsnotviolent-com/ (full text)
14. Locomotive Scroll documentation and repository — https://scroll.locomotive.ca/docs · https://github.com/locomotivemtl/locomotive-scroll (summary)
15. Locomotive, agency page and Scout Motors case study — https://locomotive.ca/en/agency · https://locomotive.ca/en/work/scout-motors (summary)
16. Locomotive, "A few things your UX designer can learn from your shrink" — https://medium.com/@LocomotiveMTL/a-few-things-your-ux-designer-can-learn-from-your-shrink-locomotive-style-8a8de62c841 (full text)
17. Codrops, "Inside Resn's digital experiences" — https://tympanus.net/codrops/2026/09/14/inside-resns-digital-experiences/ (full text)
18. Awwwards, "Zentry case study" — https://www.awwwards.com/zentry-case-study.html (summary)
19. Awwwards, "Savor: reimagining the future of fat" — https://www.awwwards.com/savor-reimagining-the-future-of-fat.html (summary)
20. Awwwards, "KPR by Resn wins Site of the Month" — https://www.awwwards.com/kpr-by-resn-wins-sotm.html (summary)
21. Communication Arts, Webpicks: Noiz! — https://www.commarts.com/webpicks/noiz (summary)
22. Designers Institute of New Zealand, Black Pin 2018, interview with Rik Campbell and Steve Le Marquand — https://designersinstitute.nz/initiatives/black-pin/2018-1/rik-campbell-and-steve-le-marquand/interview (full text)
23. Instrument, essay on working without a fixed process (2016) — https://medium.com/in-progress/488b7747d0ce (full text)
24. Instrument at designsystems.com, "Why we build design systems: an agency's perspective" — https://www.designsystems.com/why-we-build-design-systems-an-agencys-perspective/ (summary)
25. Instrument, "Why we prototype" — https://www.instrument.com/latest/why-we-prototype (summary)
26. Instrument, "Design to code" — https://www.instrument.com/latest/design-to-code (summary)
27. Instrument, "Making UX feel alive" — https://www.instrument.com/latest/making-ux-feel-alive (summary)
28. Instrument, "What sidewalks can teach us" — https://www.instrument.com/latest/what-sidewalks-can-teach-us (summary)
29. Instrument, Oura case study — https://www.instrument.com/work/oura-smart-ring (summary)
30. Instrument, Electronic Arts case study — https://www.instrument.com/work/electronic-arts (summary)
31. Instrument, ServiceNow rebrand case study — https://www.instrument.com/work/servicenow-rebrand (summary)

Not opened: https://spaces.is/loversmagazine/interviews/louis-paquet (HTTP 500);
https://lbbonline.com/news/radar-resn (body empty);
https://www.awwwards.com/awwwards-interviews-kris-hermansson-franc-cheetham-from-resn.html (introduction only).

**Foundations**

32. Josef Müller-Brockmann, "Grid and Design Philosophy" (1981), as reprinted in H. Armstrong (ed.), *Graphic Design Theory* — https://openlab.citytech.cuny.edu/langecomd3504fa2019/files/2018/10/MullerBrockmann_Grid_Des-Phil.pdf
33. The same text — https://neugraphic.com/muller-brockmann/muller-brockmann-text2.html
34. Josef Müller-Brockmann, *Grid Systems in Graphic Design*, OCR text at archive.org, read through a summarising tool; no page numbers established — https://archive.org/download/GridSystemsInGraphicDesignJosefMullerBrockmann/Grid%20systems%20in%20graphic%20design%20-%20Josef%20Muller-Brockmann_djvu.txt
35. V. van Gemert, "The Polder measure" (secondary; repeats the ten-words figure) — https://vasilis.nl/nerd/old/the-polder-measure/
36. *Eye* no. 19 (1995), "Reputations: Josef Müller-Brockmann" — https://www.eyemagazine.com/feature/article/reputations-josef-muller-brockmann
37. Massimo Vignelli, *The Vignelli Canon*, PDF published by the Vignelli Center for Design Studies, RIT; read directly — https://www.rit.edu/vignellicenter/sites/rit.edu.vignellicenter/files/documents/The%20Vignelli%20Canon.pdf
38. Don Norman, "Signifiers, not affordances" — https://jnd.org/signifiers-not-affordances/
39. Don Norman, "Affordances and design" — https://jnd.org/affordances-and-design/
40. Don Norman, on the revised and expanded *Design of Everyday Things* — https://jnd.org/the-design-of-everyday-things-revised-and-expanded-edition/
41. Publisher's page for the same book — https://www.hachettebookgroup.com/titles/don-norman/the-design-of-everyday-things/9780465050659/
42. UX Magazine, "Understanding Don Norman's principles of interaction" (secondary; not used for any claim) — https://uxmag.com/articles/understanding-don-normans-principles-of-interaction
43. Don Norman, "Emotional design" — https://jnd.org/emotional-design/
44. Don Norman, "Emotion and design: attractive things work better" — https://jnd.org/emotion-design-attractive-things-work-better/

**Juries**

45. Awwwards, "About evaluation" — https://www.awwwards.com/about-evaluation/
46. Awwwards, Developer Award — https://awwwards.com/developer-award
47. Awwwards, developer criteria document linked from the award page — https://docs.google.com/document/d/1Gvmg6Z60UQ-4BOM3XyUcBKvq2shd4J-l_MoXT26JFEg/
48. CSS Design Awards, "About" — https://www.cssdesignawards.com/about
49. CSS Design Awards, one award page (judges' scores) — https://www.cssdesignawards.com/sites/200/47007/
50. The Webby Awards, judging criteria — https://www.webbyawards.com/judging-criteria/
51. The Webby Awards, judging process — https://www.webbyawards.com/judging-process/
52. The Webby Awards, People's Voice — https://www.webbyawards.com/webby-peoples-voice-101/
53. FWA, live judging — https://thefwa.com/live-judging/ (404 when fetched; a search snippet only; not used for any claim)

**Standards**

54. W3C, Web Content Accessibility Guidelines (WCAG) 2.2 — https://www.w3.org/TR/WCAG22/
55. W3C WAI, "What's new in WCAG 2.2" — https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
56. web.dev, "Web Vitals" — https://web.dev/articles/vitals
57. web.dev, "Largest Contentful Paint" — https://web.dev/articles/lcp
58. web.dev, "Interaction to Next Paint" — https://web.dev/articles/inp
59. web.dev, "Cumulative Layout Shift" — https://web.dev/articles/cls
60. web.dev, "Optimize Cumulative Layout Shift" — https://web.dev/articles/optimize-cls
61. web.dev, "Time to First Byte" — https://web.dev/articles/ttfb
62. web.dev, "First Contentful Paint" — https://web.dev/articles/fcp
63. web.dev, "Interaction to Next Paint becomes a Core Web Vital on March 12" — https://web.dev/blog/inp-cwv-march-12

**Our own evidence**

- The references, measured: `bench/runs/_research/references/<id>/evidence.json` and screenshots (untracked), taken
  with `design_dna/inspect.mjs` on 2026-11-10.
- Our pages on the same instrument: `bench/runs/_research/ours/<variant>-<site>/evidence.json` (untracked).
- Critic readings of the bench pages: `bench/runs/judged/<site>/judge.json` (untracked), 2026-11-10.
- The engine's log of measurements and decisions: `REFACTOR.md`.
- The existing reference records and recipes: `design_dna/references/*.json`, `lib/blueprints/*.bp.json`.
