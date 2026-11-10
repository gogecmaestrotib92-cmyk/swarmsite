# Swarmsite Studio Quality Standard

Version 0.1 · 2026-11-10 · status: **proposed, not yet calibrated against human designers** (see §6).

This document defines what "studio quality" means for a page Swarmsite generates, in terms that can be measured by
a browser or reviewed by a person. It has three users: the Visual Critic, which grades a page and proposes
corrections; the designers who calibrate the critic; and the composers, which read it as constraints. It prescribes no
look. The references show ranges and decisions, not recipes.

The evidence behind it is in `SWARMSITE_DESIGN_REFERENCE_RESEARCH.md` ("the Research"). Marks used here:

| Mark | Meaning |
|---|---|
| **[S n]** | Stated by source *n* (same numbering as the Research; the sources cited here are repeated at the end). |
| **[M]** | Measured by us; the place that holds the number is named. "References" means the 12 design references measured in a browser on 2026-11-10 (Research, Part C and D). |
| **[I]** | Our decision or interpretation. Every threshold marked [I] is a working value that calibration may move. |

A threshold never appears without one of these marks. Where a number comes from a print-era source it is used as a
direction and the threshold itself is marked [I].

---

## 1. Nine principles the Standard rests on

| # | Principle | Evidence |
|---|---|---|
| P1 | **Two judgements, never blended.** Technical compliance is a gate; creative quality is a jury's score. | The best-known jury scores design and technical execution in two awards with two juries [S 45][S 46]. A testable requirement certifies a floor, not quality (Research B.9). Our own blended score shipped weak taste: production taste 56 before and after a change, 0 of 20 jobs at 70, all shipped [M: `REFACTOR.md`, 2026-11-09]. |
| P2 | **Creative quality is plural and noisy.** One reading is not a score. | At least 18 jurors, the three furthest scores dropped [S 45]. One reading of our critic moves about ±4 points [M: `REFACTOR.md`, 2026-11-10]. |
| P3 | **Nothing is arbitrary.** Every placement answers to a system — grid, scale, rhythm — and every departure from it is deliberate. | The grid exists to prevent arbitrary placement; scale may be broken only knowingly [S 37]. The grid as the will to systematise and reduce to essentials [S 32]. |
| P4 | **The message hierarchy comes before the visuals.** | Content strategy and messaging hierarchy before visuals [S 2]; flow, pacing and hierarchy decided before any file [S 26]; the first screen sets the impression [S 16]; if it is not understood the effort is wasted [S 37]. |
| P5 | **One idea, specific to the subject.** | Semantics and appropriateness: the solution specific to the problem, beyond style [S 37]. Studios propose whole directions, not parts [S 18][S 2]. |
| P6 | **Motion is a system decided before the page, or it is restrained.** | The motion system fixed before site design [S 18]; a motion toolkit [S 30]; fewer animations by choice [S 12]. |
| P7 | **Technique is chosen by content and cost.** An effect the content does not need is a defect. | [S 2][S 3][S 18][S 19]; smooth scrolling decided per project against its named costs [S 7]. |
| P8 | **Spectacle is weighed against access, explicitly.** | [S 7][S 3]; usability is not suspended by attractiveness [S 44]; the weight of each level of response depends on what the product is for [S 43]. |
| P9 | **A claimed level must survive a blind comparison by designers.** | Juries are human [S 45][S 48][S 50]; until §6 is done every score here is the critic's own. |

---

## 2. Two tracks

### Track T — technical compliance

Pass or fail, check by check, reported as a list. Never converted into points, never averaged with Track C.
The checks are in §4.10. A page that fails a hard check is not shipped whatever its creative level. A page that passes
every check has proved nothing about its quality.

### Track C — creative quality

A level from 1 to 4 for each of nine areas (§4.1–4.9), each with the evidence for it, and a page level decided by
rule (§5). Judged by the Visual Critic from screenshots *and* from measurements of the rendered page; confirmed by
designers in blind comparison (§6).

### What the two tracks decide together [I]

| Track T | Track C page level | Decision |
|---|---|---|
| any hard check fails | any | Not shippable. Repair the failure; the creative reading is kept for information. |
| passes | 1 | Not our work. Do not polish: change the direction and compose again. |
| passes | 2 | Shippable as competent; recorded as below target. |
| passes | 3 | Target. |
| passes | 4 | Only claimed after designers confirm it (§6). |

Today the loop decides on one number, `0.55 × taste + 0.45 × contract` [M: `lib/swarm/run.py`]. Under this Standard
that number stops being a decision variable: a composed page replaces the page it competes with when its Track C
reading is at least as high *and* it fails no Track T check the other passed. The second half of that rule already
exists in the loop; the first half is a change (Research, Part F).

---

## 3. Four levels

| Level | Name | What a designer says after ten seconds [I] | Score band on the critic's 0–100 scale |
|---|---|---|---|
| 1 | Generic, machine-made | "I have seen this page before with another logo." | below 55 |
| 2 | Competent professional | "Clear and tidy. Nothing is wrong and nothing stays with me." | 55–69 |
| 3 | Distinctive studio quality | "This could only be this company's page, and every screen was decided." | 70–89 |
| 4 | Exceptional, experimental | "I have not met this form before, and it serves the subject." | 90 and above |

The bands follow the anchors the critic already uses — tidy but anonymous at 45–55, 70 as "a good studio would ship
after a day of polish", 90 as reference level [M: `lib/qa/critic.py`, SYSTEM]. They are uncalibrated [I].

Where our pages stand on that scale [M: `bench/runs/judged/*/judge.json`, 2026-11-10, eight sites, two readings each,
same critic, same day]: the shipped (template) pages read 46–57, mean 54; the composed pages read 54–66, mean 62.
In the terms of this Standard the composed pages sit in the upper half of level 2 and none has reached level 3.

Three things about the levels:

- **Level 1 is not "ugly".** It is the absence of decisions: defaults everywhere, the same form repeated, decoration
  that means nothing. Its markers are listed per area in §4 and each is measurable or visible.
- **Level 3 is the target, consistently.** The work of the engine is to make level 3 the ordinary outcome.
- **Level 4 is a different kind, not a higher grade of the same.** It trades convention for a new form and is opt-in
  (the owner's "redesign freely" mode). The trade is explicit in the sources: an experiential site may favour
  spectacle while a shop favours conversion and native behaviour [S 7]; how much the first impression may outweigh
  ease of use depends on what the product is for [S 43]. A level-4 page still passes Track T.

---

## 4. The ten areas

Each area has four parts: what it is and on what authority; what a browser **measures** (the range found in the eleven
third-party references, and the threshold this Standard sets); what a reviewer **judges**, as descriptors for the four
levels; and the **defects** with their corrections. "References" figures are from the Research, Tables D.1–D.7, all
[M], measured 2026-11-10; the twelfth reference is our own recipe and is not counted in a range. A correction marked
*gap* names something the engine cannot do today (Research, Part E).

A range measured on eleven sites is a description, not a law. Every threshold derived from one is marked [I]; most
are set a little wider than the range, and where one is narrower the row says why.

### 4.1 Art direction

**What it is.** The one idea every other decision on the page answers to, and how consistently the page keeps it.
Authority: the solution specific to the subject, nothing arbitrary [S 37]; studios propose a whole direction and
build one [S 18][S 2]; meaning and brand are the reflective level of a visitor's response [S 43].

**Measured**

| Reading | References | Threshold |
|---|---|---|
| The page states its idea in a sentence before it is drawn (concept and direction recorded with the page) | not observable on a third-party page | required; the critic judges the page against it [I] |
| Distinct grounds on the page | 1–4 | ≤ 4 [I] |
| Scale regime (§4.2) is the same in every section | not measured per section | one regime per page [I] |
| A device of the first screen returns below it (a crop, a ground, a type gesture, a label system) | seen, not measured | at least twice below the first screen [I] |

**Judged**

| Level | Descriptor |
|---|---|
| 1 | No idea can be named. The page is a sequence of standard sections in a palette. |
| 2 | A consistent style (palette, faces, spacing) but no idea: the style would fit any company in the sector. |
| 3 | One idea, statable in a sentence, that comes from this subject; it is visible on the first screen and is still there on the last. |
| 4 | The idea and the form are inseparable: remove the idea and the layout no longer makes sense. |

**Defects and corrections**

| Id | Defect | Found by | Correction |
|---|---|---|---|
| ART-01 | The page does not do what its own direction says | critic, against the recorded direction | recompose the sections that depart; or rewrite the direction to what the page can carry |
| ART-02 | The idea lives on the first screen only; below it the page reverts to stock sections | critic; our critics name this on most composed pages [M: `bench/runs/judged/*/judge.json`] | *gap*: a page-level plan that assigns the idea's device to named sections before they are composed |
| ART-03 | Two regimes on one page (a poster headline over sections set like a quiet index) without intent | measured (§4.2) | one `title` scale for the page |
| ART-04 | Decoration that does not come from the subject (a gradient, a glow, a badge over the headline) | critic | remove; nothing replaces it |

### 4.2 Typography

**What it is.** The system of faces, sizes, weights and spacing the page is set in. Authority: few faces, no type as
decoration, size bound to column width, flush left by default, scale broken only knowingly [S 37]; line length,
leading and their interdependence [S 34]; a typeface as the carrier of identity [S 18][S 20][S 12][S 30].

**Measured**

| Reading | References | Threshold |
|---|---|---|
| Families carrying text | 1–3, median 2; never more | ≤ 3 [I] |
| Largest type ÷ body size | three regimes with nothing between them: 1.6–1.7 (two picture-led pages), 4.5–8.0 (six), 15–23 (three) | in a regime: ≤ 2 (only on a picture-led page), 4.5–9, or ≥ 12. Between 2 and 4.5 is a defect [I] |
| Largest type, leading | 0.5–1.05, median 1.0 | ≤ 1.1 [I] |
| Largest type, tracking | −0.03 to +0.003 em | ≤ 0 em; only small capital labels are tracked open [I] |
| Body size | 14–25.9 px, median 16 | ≥ 14 px at 1440 and at 390 [I] |
| Body leading | 1.1–1.8, median 1.35 | 1.2–1.7 [I] — the two references outside it set a condensed face and a list; text must also survive a forced 1.5 [S 54, 1.4.12] |
| Characters per line of running text | 45–72, median 58 at 1440; 27–48, median 40 at 390 | 40–75 at 1440, 25–50 at 390 [I]. Direction from [S 34]: about ten words a line, seven for long text |
| Headline lines | 1–3 at 1440; 1–5 at 390 | ≤ 3 at 1440, ≤ 5 at 390 [I] |
| Small label size | 12–14 px | ≥ 12 px [I] |
| Last line of a heading is one short word | not measured on the references | none [I] |

Vignelli's own figure — at most two sizes, display about twice the text [S 37] — is not adopted as a threshold: nine
of the eleven references set their largest type at 4.5 times the text size or more. What is adopted is his rule that scale is a decision.

**Judged**

| Level | Descriptor |
|---|---|
| 1 | A default face at default sizes; headings are the body face made bigger and bolder; no label system. |
| 2 | A sensible pairing, a consistent scale, readable text — and the same pairing and scale as a thousand other pages. |
| 3 | A display face with character, a quiet face for text and a label system; a scale in one regime; headings broken by sense; the type alone would identify the page. |
| 4 | Type is the image: cut by the edge of the screen, set at poster scale, built into the layout so that the words are the composition. |

**Defects and corrections**

| Id | Defect | Found by | Correction |
|---|---|---|---|
| TYP-01 | More than three families | measured | hero `type`: one pairing from the registry |
| TYP-02 | The display face is one seen everywhere | registry flag `common` [M: `lib/type/faces.json`] | another display face of the same role |
| TYP-03 | Scale between regimes (largest ÷ body between 2 and 4.5) | measured | the headline's `size` one step up and the section `title` with it; or the quiet regime, deliberately, on a picture-led page |
| TYP-04 | Display set loose (leading above 1.1 or positive tracking) | measured | renderer rule; not a model's choice |
| TYP-05 | Lines too long or too short | measured | narrower or wider text block: `cols` where the form has it; *gap*: a text-measure parameter on every form |
| TYP-06 | Headline in more than three lines, or ending on one short word | measured | break by sense (the headline's `lines`), one `size` step smaller, or fewer words (`hero_h1`) |
| TYP-07 | No label system: small text in several sizes and cases | measured: distinct styles under 15 px | hero `type.label`; one label style |
| TYP-08 | Emphasis by weight, colour and italic at once | critic | one means of emphasis per page |
| TYP-09 | Size does not follow rank: a heading smaller than the items under it, or a headline that is not the largest type on its screen | measured; found on our own render [M: Research C.12] | the renderer's scale per beat |
| TYP-10 | A letter drawn by a fallback face, or an accent detached from its letter | seen on our own render [M: Research C.12]; Track T-19 | a face that draws the content's alphabet; the registry records which alphabets each face covers |

### 4.3 Composition

**What it is.** Where things stand on the screen and against what. Authority: the grid exists to prevent arbitrary
placement; a module too fine is no grid, too coarse restricts; small outer margins give tension [S 37]; margins are
proportioned, not equal all round; fewer formats give order [S 34].

**Measured**

| Reading | References | Threshold |
|---|---|---|
| Outer margin (first edge blocks align to) | 1–6% of the width in 11 of 11 | 1–7% at 1440 [I] |
| Distinct left edges that at least three blocks share | 2–10 (the reading lists at most ten); they fall on halves, thirds, quarters and sixths of the width | every edge on the page grid; a block on an edge of its own is a finding [I] |
| Text set centred | none (≤ 2%) in 6 of 11; ≤ 20% in 9; 29% and 44% on two poster pages | ≤ 20% of text blocks, more only in the poster regime [I]; flush left is the default [S 37] |
| Largest picture on the first screen | ≥ 82% of the screen in 9 of 11; the two others are a two-picture index and a type poster | reviewed, not gated: a first screen that is neither picture-led nor type-led is a finding [I] |
| The same form on consecutive sections | not measured on the references | no form three times running [I] |
| Changes of ground down the page | 0–5, median 1; three pages never change | ≤ 3, more only when the direction says the page is striped [I]. Our pages: 5–14, median 10 [M: Research E.1] |
| Rules on the page (on elements, by pseudo-elements, `hr`) | 0–16, median 1; ten or more on 4 of 11 | above 16 is a finding [I]. Our pages: 17–50, median 33 [M: Research E.1] |
| Characters per screen of a section (page median) | 30–400, median 230 | reviewed: a page keeps to one end of the range; above 400 is a finding [I]. Our pages: median 382 |
| A picture as a rectangle beside a column of text | — | never [M: the owner's standard, 2026-11-10] |

**Judged**

| Level | Descriptor |
|---|---|
| 1 | Everything centred or everything in equal columns; every section the same container; each screen could be reordered without loss. |
| 2 | A clean grid, consistent gutters, alignment that holds — and symmetry everywhere; nothing is placed, everything is filled in. |
| 3 | Each screen is arranged on purpose: asymmetry with a reason, large empty areas that set something off, blocks that share few edges, elements that cross their column or their section. |
| 4 | The composition itself carries meaning; the grid is broken where the content breaks. |

**Defects and corrections**

| Id | Defect | Found by | Correction |
|---|---|---|---|
| CMP-01 | A box of content in the middle of the screen with wide empty margins | measured: outer margin above 7% (our pages: a median of 7%, references 3% [M: Research E.1]) | renderer frame; hero and section columns to the outer edge |
| CMP-02 | Ragged edges: blocks starting at many different x positions; a second column that starts at several | measured; found on our own render [M: Research C.12] | snap to the page grid (`at.col` in the first screen); one start per column in the renderer |
| CMP-03 | Centred by default | measured | flush left; centre only a statement |
| CMP-04 | A picture boxed beside text | section reader; critic | a picture form: `bleed`, `backdrop`, `panorama`, `stage`, `card`, `offset`, `inline`, `gallery` |
| CMP-05 | One form repeated down the page | measured from the page's own composition record | another form for the middle section; *gap*: the forms of a page chosen together, with a budget per form |
| CMP-06 | A first screen with a small picture and a narrow headline — neither image nor type leads | measured: picture share and headline width | first-screen composition: `bleed: full`, or the headline across the width |
| CMP-07 | Nothing ever crosses a boundary: every element inside its column, every section inside its band | critic | `overlap`, `bleed`; *gap*: content that crosses from one section into the next |
| CMP-08 | A striped page: the ground changes on most sections | measured | one ground carries the page; a change of ground marks a change of subject; *gap*: the grounds of a page chosen together |
| CMP-09 | Ruled everywhere: a hairline between every row of every section | measured | space instead of rules; ruled rows only where the items are tabular |

### 4.4 Visual hierarchy

**What it is.** The order in which the eye meets things, and whether that order is the order of importance.
Authority: a signifier tells what can be done; designers supply signifiers [S 38]; the message hierarchy is decided
before the visuals [S 2][S 26]; one distinct element directs attention and the first screen sets the impression
[S 16]; large headings against small text need white space between them [S 37].

**Measured**

| Reading | References | Threshold |
|---|---|---|
| Filled buttons on the first screen (navigation included) | 0 in 5, 1 in 3, 4–5 in 3 (lower bounds: the reading can miss a button) | one primary action style on the page; ≤ 2 filled buttons on the first screen [I]. Our pages: 2 on 8 of 8 |
| Words in the headline | 1–9 in 7 of the 8 that have an h1 | ≤ 12 [I]; the contract already grades `h1-words` |
| Sizes of text inside one section | not measured | ≤ 3 [I] |
| A heading is larger than the items it heads | not measured on the references; broken on our own render [M: Research C.12] | required [I] |
| The largest text on each screen is that screen's heading | not measured | required [I] |

**Judged**

| Level | Descriptor |
|---|---|
| 1 | Several things shout at once, or nothing does; buttons, links and labels look alike. |
| 2 | Heading, text and action are distinguishable on every screen; the order is correct and uniform. |
| 3 | Each screen has one thing seen first, and it is the right thing; secondary matter is clearly quieter; the page can be understood from its headings alone. |
| 4 | Hierarchy is used expressively — a deliberate inversion or silence that makes the main thing land harder. |

**Defects and corrections**

| Id | Defect | Found by | Correction |
|---|---|---|---|
| HIE-01 | Two elements compete for first place on a screen | critic | reduce one: `title` down, picture smaller, or drop it |
| HIE-02 | More than one primary action style, or several filled buttons side by side | measured | one filled action; the rest as text links |
| HIE-03 | The first screen does not say what this is within three seconds | critic; contract `h1-words`, `h1-lines` | `hero_h1`; fewer nodes in the first-screen composition |
| HIE-04 | Label, heading, text and caption are not distinguishable by size alone | measured | the label style; `title` |
| HIE-05 | An action that looks like text, or text that looks like an action | critic [S 38] | the page's one button style; underlined links |

### 4.5 Imagery

**What it is.** What the pictures are, how they are cut and where they stand. Authority: fewer picture formats give
order and credibility [S 34]; technique chosen by content [S 19]; and the owner's standard: a picture is never a box
beside text, it belongs to the look of its section [M: owner, 2026-11-10].

**Measured**

| Reading | References | Threshold |
|---|---|---|
| Pictures with a CSS shadow | 0 of 248 pictures on 11 pages | 0 on photographs [I]; on product screens the question is open (Research F.3) |
| Rounded pictures | none on 6 of 11 pages; 31 of 248 in all | one decision per page: all pictures square, or all at one radius [I] |
| Pictures with words standing on them | on 11 of 11 pages (45 pictures) | allowed; the words must measure 4.5:1 against what is really behind them [S 54, 1.4.3] |
| Pictures that run edge to edge | at least one on 8 of 11 pages | on a page with three or more photographs, at least one leaves its column [I] |
| Pictures drawn at a ratio other than their own | 85 of 248 | allowed for photographs; never for a screenshot [M: engine rule] |
| Picture ratios in use on one page | not counted | ≤ 4 [I], after [S 34] |
| A picture drawn larger than 1.35× its pixels | — | never [M: engine rule, measured in a browser] |
| The same picture twice | — | never [M: engine rule] |

**Judged**

| Level | Descriptor |
|---|---|
| 1 | Stock or generated pictures in equal boxes with rounded corners and a shadow; the pictures could be exchanged between sections. |
| 2 | Relevant pictures, cleanly cropped, consistently treated — each in its box. |
| 3 | Pictures are given a job and room: one fills the screen, one runs off the edge, one sits small in a large empty field; ratios and sizes vary on purpose; the product is shown as an object, not as a thumbnail. |
| 4 | The imagery is made for the page and cannot be told from the layout. |

**Defects and corrections**

| Id | Defect | Found by | Correction |
|---|---|---|---|
| IMG-01 | A picture boxed beside text | section reader | a picture form (CMP-04) |
| IMG-02 | A shadow, a frame or a card around a photograph | measured | none; a product screen keeps one hairline ring |
| IMG-03 | Mixed corner radii | measured | one radius for the page |
| IMG-04 | Every picture the same size and ratio | measured | `panorama` or `bleed` for one, `offset` small for another; `gallery` for neighbours |
| IMG-05 | A picture stretched beyond its pixels | measured (`picmeasure.mjs`) | a smaller form, or `stage` |
| IMG-06 | A picture that does not belong to its section | critic | `swap_image`; or a section of words |
| IMG-07 | A screenshot cropped, toned or written over | validator | `stage`, whole |
| IMG-08 | The crop cuts the subject | critic | *gap*: a focal point per picture that every crop respects |

### 4.6 Originality

**What it is.** Whether the page could be mistaken for another. Authority: creativity is a fifth of the best-known
jury's score [S 45]; innovation is a named criterion of two others [S 48][S 50]; a custom or adapted typeface is how
studios make an identity [S 18][S 20][S 12]; and appropriateness limits it — new for the subject's sake [S 37].

**Measured**

| Reading | Our pages | Threshold |
|---|---|---|
| Structural fingerprint equal to another page of ours | recorded per page [M: `scores.json`] | none [I] |
| Share of sections drawn in the three commonest forms | about 60% on the shipped pages [M: `REFACTOR.md`, 2026-11-09] | ≤ 40% [I] |
| Display face flagged `common` | registry | no [I] |

**Judged**

| Level | Descriptor |
|---|---|
| 1 | The page is a known template; its structure and look have been seen many times. |
| 2 | Conventional structure competently executed; nothing would be remembered tomorrow. |
| 3 | At least one device of its own — a way of setting the headline, of showing the product, of moving between sections — that follows from the subject. |
| 4 | A form or interaction new to the visitor, which also explains the subject better than a convention would. |

**Defects and corrections**

| Id | Defect | Found by | Correction |
|---|---|---|---|
| ORG-01 | Same structure as another of our pages | fingerprint | another concept for the first screen; other forms |
| ORG-02 | A trend imitated without relation to the subject | critic | remove (ART-04) |
| ORG-03 | No device of its own | critic | *gap*: a vocabulary of signature devices a concept can name and the renderer can draw |

### 4.7 Motion and interaction

**What it is.** What moves, when, and what answers the visitor. Authority: the motion system is fixed before the site
is designed, or motion is restrained [S 18][S 12][S 30]; smooth scrolling is a per-project decision with named costs
[S 7]; navigation can be interrupted [S 2]; feedback is a principle of interaction [S 38][S 40]; motion that starts by
itself must be pausable and motion from interaction should be switchable off [S 54, 2.2.2, 2.3.3]; hidden text delays
LCP and animated layout counts as shift [S 57][S 59].

**Measured** — with the same instrument as the references (`design_dna/inspect.mjs`)

| Reading | References | Threshold |
|---|---|---|
| Distance a revealed element travels (median) | 6–26 px, median of medians 12 | ≤ 32 px [I] |
| Fade duration (median per page) | 151–784 ms on 8 pages, median 541; a ninth page switches in one frame | 150–800 ms [I] |
| Gap between siblings revealed in sequence | 50 ms on 4 pages, 68 and 101 on two | 40–110 ms [I] |
| Share of followed elements that reveal at all | 0–65%; under 15% on 5 of 11 | ≤ 65%; a page where everything reveals is a finding [I] |
| Headings revealed word by word or line by line | 5 of 11 | a page decision, the same for every heading [I] |
| Headline fully visible after navigation | 0.95–4.65 s on the 6 that animate it; 5 do not animate it | ≤ 1.5 s [I]. Stricter than the references on purpose: text at opacity 0 is not an LCP candidate [S 57] and good LCP is ≤ 2.5 s [S 56] |
| A section held in place | on 7 of 11; for 3–8 screens on 5 | at most one long hold per page, ≤ 5 screens [I] — shorter than two of the references on purpose: a hold takes the scroll away from the visitor [S 7] |
| The same hold on a phone | kept on 3 of those 7 | released or ≤ 2 screens at 390 [I] |
| Sideways movement tied to scroll | 4 of 11 at 1440; none of those at 390 | never tied to scroll at 390 [I] |
| Smoothed scrolling | 8 of 11 at 1440 (lag 0.8–1.2 s against 0 on an empty page); 0 of 11 at 390 | optional at 1440, never at 390, never on a page whose job is a form or a shop [I], after [S 7] |
| With "reduce motion" asked for, reveals in the first 6 s | kept on 6 of the 7 pages that have three or more | none; content visible at once [I]. Here the Standard follows WCAG [S 54, 2.3.3], not the references |
| Motion that runs by itself for more than 5 s | drifting bands on 4 of 11 | pausable, or purely decorative and marked so [S 54, 2.2.2] |
| Every action answers a pointer | colour, ground or border change in 0.2–0.65 s | every button and link has a hover and a focus state; no hover moves the layout [I] |

**Judged**

| Level | Descriptor |
|---|---|
| 1 | Everything fades up the same way, or nothing moves and nothing answers; motion is a library's default. |
| 2 | Tidy entrances and hover states, consistently timed; the motion says nothing about the page. |
| 3 | A motion system: one easing family, two or three durations, a rule for what reveals and what does not; one composed moment (a hold, a rail, a sequence) where the content has steps to show. |
| 4 | Motion that explains: the interaction is how the subject is understood. |

**Defects and corrections**

| Id | Defect | Found by | Correction |
|---|---|---|---|
| MOT-01 | Every element enters the same way | measured: reveal share, kinds | reveal headings and pictures only; *gap*: a motion system chosen with the concept and recorded with the page |
| MOT-02 | Reveals travel far or last long | measured | renderer parameters to the thresholds above |
| MOT-03 | An intro keeps the headline hidden | measured | headline visible by 1.5 s; the intro animates something else |
| MOT-04 | A hold or a rail kept on a phone | measured at 390 | release at 390 (the renderer does this for its own moves) |
| MOT-05 | "Reduce motion" ignored | measured | Track T |
| MOT-06 | No system: many unrelated durations and easings | measured: declared transitions | one easing family and three durations for the page |
| MOT-07 | An action with no hover or focus answer | measured | the page's button and link states |
| MOT-08 | A long sequence that cannot be skipped or interrupted | critic [S 2] | shorten the hold; native scroll |

### 4.8 Content and usability

**What it is.** Whether the page says the right things in the right order and can be used without thought.
Authority: signifiers, feedback, conventions, a coherent conceptual model [S 38][S 40]; the behavioural level — use,
performance, feeling in control [S 43]; usability is not suspended by attractiveness [S 44]; content, structure and
navigation, functionality as jury criteria [S 50]; usability 30% and content 10% of a jury's score [S 45]; fewer
first-level menu choices [S 16]; if it is not understood the effort is wasted [S 37].

**Measured**

| Reading | Source of the threshold | Threshold |
|---|---|---|
| Every action leads somewhere real | contract `actionable-cta` | required (Track T) |
| The client's words and links kept, in SEO-safe mode | contract `seo-text-kept`, `seo-links-kept` | required (Track T) |
| First-level navigation items | [S 16]: fewer | ≤ 7 [I] |
| Characters on one screen of one section | references: median section 30–400 | a section above 900 per screen is a finding [I] |
| Headings describe their section | [S 54, 2.4.6] | reviewed |

**Judged**

| Level | Descriptor |
|---|---|
| 1 | Filler copy, sections that repeat each other, claims without proof, actions that lead nowhere in particular. |
| 2 | Complete and correct: what it is, for whom, proof, price, action — in the expected order. |
| 3 | The page has an argument: each section earns the next, proof stands beside the claim it proves, and the visitor always knows the next step. |
| 4 | The content is disclosed in a way that changes how the offer is understood. |

**Defects and corrections**

| Id | Defect | Found by | Correction |
|---|---|---|---|
| USE-01 | Two sections say the same thing | critic | `drop_beat` |
| USE-02 | A claim far from its proof; price before proof | critic | `reorder` |
| USE-03 | Too many words on a screen | measured | `shorten` (free mode); a `columns` or `ledger` form (SEO-safe mode) |
| USE-04 | A screen with no visible next step | critic | the page's action in the section's form |
| USE-05 | Navigation with more than seven first-level items | measured | group; the rest in the footer |
| USE-06 | A form where the visitor expects one that is only a link, or the reverse | contract; critic | the direction's form beat |

### 4.9 Responsive behaviour

**What it is.** Whether the phone page is composed or merely stacked. Authority: reflow without two-dimensional
scrolling, target size, orientation [S 54]; responsive and mobile as a fifth of a developer jury's score [S 47]; a
studio's scroll library switches parallax off on touch [S 14]; and both views of the references, measured.

**Measured**

| Reading | References at 390 | Threshold |
|---|---|---|
| No horizontal scrolling at 390 and at 320 | — | required (Track T) [S 54, 1.4.10] |
| Largest type ÷ body | 1.2–12.5, median 3.3 (about half the 1440 ratio) | ≥ 2.5, except in the quiet regime [I] |
| Headline lines | 1–5 | ≤ 5 [I] |
| Characters per line | 27–48, median 40 | 25–50 [I] |
| Page length against 1440, in screens | 0.8–1.5 × | ≤ 1.6 × [I]: a phone page much longer than that has been stacked |
| Holds, rails, smoothed scrolling | holds kept on 3 of 7, rails on 0 of 4, smoothing on 0 of 11 | §4.7 |
| Navigation collapses to a menu button | 10 of 11 | required when it has more than three items [I] |
| Pictures running edge to edge | as many as at 1440 or more on every page (15 against 8 and 11 against 3 on two picture-led pages) | pictures either bleed or keep the text's margin, one rule per page [I] |
| Targets | — | ≥ 24 × 24 px (Track T) [S 54, 2.5.8] |

**Judged**

| Level | Descriptor |
|---|---|
| 1 | The desktop page shrunk or stacked: tiny pictures, headings one word per line, pinned sections that trap the thumb. |
| 2 | Everything fits and reads; one column of the desktop content in the same order. |
| 3 | Recomposed: type rescaled to stay large, pictures given the full width, holds released, the first screen designed for a tall narrow frame. |
| 4 | The phone page has ideas of its own that the desktop page does not need. |

**Defects and corrections**

| Id | Defect | Found by | Correction |
|---|---|---|---|
| RSP-01 | A composition merely stacked | measured: page length; critic | the form's phone arrangement; the first screen has a phone block (`sm`); *gap*: the same for sections |
| RSP-02 | A headline in more than five lines or one word per line | measured (`measure.mjs`) | the first screen's phone block (`sm`); the headline's `lines` |
| RSP-03 | A picture reduced to a thumbnail | measured: width share | full width at 390 |
| RSP-04 | A hold or rail that survives on a phone | measured | release (MOT-04) |
| RSP-05 | Overflow, small targets | measured | Track T |

### 4.10 Technical execution — Track T

Pass or fail. "Exists" means a check of ours measures it today.

| Id | Requirement | Authority | Checked by | Exists |
|---|---|---|---|---|
| T-01 | No horizontal overflow, no clipped or overlapping text at 1440 and 390 | [S 54, 1.4.10] | contract `no-overflow`; composition measurement | yes |
| T-02 | No empty or near-empty screen | ours | contract `no-empty-screens` | yes |
| T-03 | Text contrast 4.5:1, large text 3:1, measured on the rendered pixels, including words on pictures | [S 54, 1.4.3] | contract `contrast`; `picmeasure.mjs` | yes |
| T-04 | Every action has a real destination | ours; functionality [S 50] | contract `actionable-cta` | yes |
| T-05 | SEO-safe: the source's words, links and meta kept; one h1 with its keywords | ours; semantics [S 47] | contract `seo-*` | yes |
| T-06 | No picture drawn above 1.35× its pixels; no screenshot cropped | ours | composition validators and measurement | yes |
| T-07 | No markup or script from a model's field reaches the page | ours | `tests/test_render_safety.py` | yes |
| T-08 | Reflow at 320 px wide | [S 54, 1.4.10] | — | no |
| T-09 | Text survives forced spacing (line 1.5, letter 0.12, word 0.16) | [S 54, 1.4.12] | — | no |
| T-10 | Targets ≥ 24 × 24 px or spaced | [S 54, 2.5.8] | — | no |
| T-11 | Keyboard focus visible and not hidden behind a fixed bar | [S 54, 2.4.7, 2.4.11] | — | no |
| T-12 | Pictures have a text alternative or are marked decorative | [S 54, 1.1.1] | — | partly |
| T-13 | With "reduce motion": no reveal hides content, nothing is held or smoothed | [S 54, 2.3.3], adopted [I] | `inspect.mjs` measures it; not yet a check | no |
| T-14 | Motion that runs by itself beyond 5 s can be paused | [S 54, 2.2.2] | — | no |
| T-15 | LCP ≤ 2.5 s in a stated lab profile; the headline visible by 1.5 s | [S 56][S 57]; [I] | `inspect.mjs` measures both; not yet a check | no |
| T-16 | CLS ≤ 0.1; reveals animate `transform` and `opacity` only | [S 56][S 59] | `inspect.mjs` measures CLS | no |
| T-17 | Pictures carry their dimensions; fonts have a metric-compatible fallback | [S 60] | — | no |
| T-18 | Responsiveness to input (INP ≤ 200 ms) | [S 56][S 58] | cannot be measured without visitors; reported as not measured | — |
| T-19 | Every character on the page is drawn by the face it is set in, with its accents attached | ours [I]; found on our own render [M: Research C.12] | — | no |

The references are no model for this track [M: Research D.7]: in one lab run four of eleven exceeded 2.5 s LCP, one
exceeded 0.1 CLS, six of the seven with load reveals kept them under "reduce motion", three have no h1, and they
transfer 1.4–10.2 MB. A page of ours can pass Track T where its reference would fail, and should.

---

## 5. Scoring

### 5.1 Weights [I, structured on S 45]

Awwwards weighs Design 40, Usability 30, Creativity 20, Content 10 [S 45]. The nine creative areas are mapped onto
those four weights; the mapping is ours.

| Awwwards criterion (weight) | Areas of this Standard | Weight |
|---|---|---|
| Design (40) | Art direction 10 · Typography 10 · Composition 8 · Visual hierarchy 6 · Imagery 6 | 40 |
| Creativity (20) | Originality 12 · Motion and interaction 8 | 20 |
| Usability (30) | Usability (the usability half of §4.8) 16 · Responsive behaviour 14 | 30 |
| Content (10) | Content (the content half of §4.8) | 10 |
| — | Technical execution | not weighed: Track T |

The critic's present four axes (design .35, originality .20, craft .25, function .20) [M: `lib/qa/critic.py`] do not
map one to one. "Craft" mixes two things this Standard separates: breakage (a clipped heading, an empty screen),
which is Track T, and finish, which belongs to each area.

### 5.2 From areas to a page level [I]

1. Each area gets a level 1–4 and the evidence for it (§7). A half level is allowed.
2. The page number is the weighted mean of the area levels mapped to the bands in §3.
3. A page is **never more than one level above its weakest creative area**. An average must not hide a failure.
4. Level 3 requires art direction and typography both at 3 or above. A page without an idea or without a type system
   is not studio work however well the rest is made (P5, §4.1, §4.2).
5. Track T is reported beside the level and never inside it.

### 5.3 Reading protocol

- Two independent readings of the same screenshots, averaged (already built: `critique_twice`). A third when the two
  differ by more than 8 points [I].
- A decision between two pages compares readings of the same kind: same critic version, same day, same screenshot
  protocol [M: comparing a fresh reading with a score from another day refused pages that were better —
  `REFACTOR.md`, 2026-11-10].
- The reader is given what the page set out to do (its concept and direction) and what the client's site looked like
  before; it judges whether the page does what it set out to do, and whether it is a step up.
- Measurements (§4, "measured") are taken before the reading and handed to the reader. The reader does not estimate
  what a browser has already measured.

---

## 6. Calibration against blind human evaluation

Not done yet. Until it is, every level in this Standard is the critic's opinion and must be labelled so.

**Anchor set** — at least 30 pages, frozen and versioned [I]: the 12 references (chosen by the owner as the bar; that
they are level 3–4 is the hypothesis calibration tests, not a fact); shipped and composed pages of the bench sites;
and pages chosen to anchor levels 1 and 2 (template and generator output for comparable businesses).

**Raters** — at least five working designers [I]. Juries we know of are larger and trim outliers (18, three dropped)
[S 45]; with five, the single furthest score per page is dropped [I]. Raters see no origin, no score, no name.

**Two tasks**

1. *Pairs*: two pages side by side at 1440 and 390, "which is the better piece of design work, and why in one
   sentence". The blind comparison page exists (`bench/compare.py`).
2. *Levels*: for a page alone, a level 1–4 for each of the nine areas using §4's descriptors.

**What is computed** [I]

| Quantity | Meaning | Required before the critic is trusted |
|---|---|---|
| Agreement among raters (ordinal α) | Is there a human consensus to calibrate to? | ≥ 0.6; below that the rubric is unclear and is rewritten first |
| Rank correlation, critic vs. mean human level | Does the critic order pages as designers do? | ≥ 0.7 |
| Pair agreement | On pairs where ≥ 80% of raters agree, how often does the critic pick the same page? | ≥ 75% |
| Critic repeatability | Median difference between two readings of one page | ≤ 4 points (today's measured noise) |
| Per-area bias | Mean (critic − human) per area | within ± half a level |

**When a requirement is missed** — the anchors or the descriptors of the area that disagrees are revised and the set
is read again. A disagreement is never resolved by tuning to one site (`AGENTS.md`: never special-case one site).

**Cadence** — after any change to the critic's prompt, model or inputs, the frozen set is read again; human rating is
repeated when the anchor set changes or the rank correlation of a new critic drops below the bar.

**What calibration cannot give** — a jury's score is not reproducible [Research B.9]. Calibration makes the critic
agree with *these* designers on *these* pages. The claim it supports is "designers preferred our page in N of M blind
pairs", never "this is a 92".

---

## 7. What the Visual Critic must return

A score is the least useful thing a critic produces. For every area below level 3 it returns findings, and each
finding has all six parts or it is not reported:

| Part | Content | Example |
|---|---|---|
| **Defect** | An id from the catalogue in §4, the area, the section id and the viewport | `TYP-03` · typography · `features` · 1440 |
| **Evidence** | Either a measurement (metric, value, the range it is outside of, where the range comes from) or a named region of a named screenshot | display÷body 2.9; references 4.5–15, median 6.7 [M] |
| **Reason** | Why a designer reads it as a defect: the principle (P1–P9 or the area's) with its source | P3: scale broken unknowingly [S 37] |
| **Correction** | One operation the engine implements, on one target, with parameters | `title: xl` on `features` |
| **Expectation** | Which measurement must move, and which way, if the correction worked | display÷body ≥ 4.5; heading ≤ 3 lines at 390 |
| **Confidence** | measured · seen · inferred | measured |

Rules:

- **The critic never edits the page** (`AGENTS.md`). A correction is a change to a document — the direction or a
  composition — which is validated, drawn and measured like any other.
- **A correction names an operation that exists.** A finding whose only remedy is something the engine cannot do is
  reported as a *capability gap* with the same evidence, and counted. The gaps, ranked by how often they are named,
  are the engine's backlog (Research, Part F).
- **A correction is verified.** After it is applied the expectation is measured. A correction that does not move its
  measurement is rolled back and recorded as ineffective for that defect. The record of which corrections work for
  which defects is the critic's memory, and it is evidence, not opinion.
- **Technical findings are reported on Track T**, by the checks that measured them, not by the critic's eye.
- **Words are the client's** in SEO-safe mode: the critic judges how they are set, not what they say.

---

## 8. Governance

- The Standard is versioned. A threshold changes only with the evidence that moved it: a calibration round, a new
  measurement of the references, or a source.
- Every [I] threshold is a candidate for calibration, and the calibration that confirms or moves it is recorded next
  to it.
- The references are re-measured before each calibration round. A reference that has changed is recorded as changed;
  one of the twelve already differs substantially from the capture our recipe was made from (Research, Part C).
  The recipes (`lib/blueprints/*.bp.json`) are functional assets and are not rewritten by a re-measurement.
- Third-party screenshots and readings stay in `bench/runs/_research/` (untracked) and are never shipped.
- No rule in this Standard may be satisfied by special-casing one site.

---

## Sources cited in this Standard

Numbering as in `SWARMSITE_DESIGN_REFERENCE_RESEARCH.md`, which lists all 63 with how each was read. An entry is
identified by its address.

- [S 2] Active Theory, Fiomet case study — https://medium.com/active-theory/fiomet-case-study-9a0180268423
- [S 3] Active Theory, Patronus case study — https://medium.com/active-theory/discover-your-patronus-348971420487
- [S 7] Locomotive, on when to use their scroll library — https://medium.com/@LocomotiveMTL/should-i-use-locomotive-scroll-on-my-project-7fc8fa38bcc5
- [S 12] Awwwards, case study of Locomotive's rebrand — https://www.awwwards.com/case-study-reinventing-locomotive-r.html
- [S 14] Locomotive Scroll documentation — https://scroll.locomotive.ca/docs
- [S 16] Locomotive, on UX — https://medium.com/@LocomotiveMTL/a-few-things-your-ux-designer-can-learn-from-your-shrink-locomotive-style-8a8de62c841
- [S 18] Awwwards, Zentry case study (Resn) — https://www.awwwards.com/zentry-case-study.html
- [S 19] Awwwards, Savor case study (Resn) — https://www.awwwards.com/savor-reimagining-the-future-of-fat.html
- [S 20] Awwwards, KPR case study (Resn) — https://www.awwwards.com/kpr-by-resn-wins-sotm.html
- [S 26] Instrument, on design and code — https://www.instrument.com/latest/design-to-code
- [S 30] Instrument, Electronic Arts case study — https://www.instrument.com/work/electronic-arts
- [S 32] Josef Müller-Brockmann, "Grid and Design Philosophy" (reprint) — https://openlab.citytech.cuny.edu/langecomd3504fa2019/files/2018/10/MullerBrockmann_Grid_Des-Phil.pdf
- [S 34] Josef Müller-Brockmann, *Grid Systems in Graphic Design* (OCR text, read through a summarising tool) — https://archive.org/download/GridSystemsInGraphicDesignJosefMullerBrockmann/Grid%20systems%20in%20graphic%20design%20-%20Josef%20Muller-Brockmann_djvu.txt
- [S 37] Massimo Vignelli, *The Vignelli Canon* — https://www.rit.edu/vignellicenter/sites/rit.edu.vignellicenter/files/documents/The%20Vignelli%20Canon.pdf
- [S 38] Don Norman, on signifiers — https://jnd.org/signifiers-not-affordances/
- [S 40] Don Norman, on the revised *Design of Everyday Things* — https://jnd.org/the-design-of-everyday-things-revised-and-expanded-edition/
- [S 43] Don Norman, on emotional design — https://jnd.org/emotional-design/
- [S 44] Don Norman, on attractive things — https://jnd.org/emotion-design-attractive-things-work-better/
- [S 45] Awwwards, evaluation — https://www.awwwards.com/about-evaluation/
- [S 46] Awwwards, Developer Award — https://awwwards.com/developer-award
- [S 47] Awwwards, developer criteria document — https://docs.google.com/document/d/1Gvmg6Z60UQ-4BOM3XyUcBKvq2shd4J-l_MoXT26JFEg/
- [S 48] CSS Design Awards, about — https://www.cssdesignawards.com/about
- [S 50] The Webby Awards, judging criteria — https://www.webbyawards.com/judging-criteria/
- [S 54] W3C, WCAG 2.2 — https://www.w3.org/TR/WCAG22/
- [S 56] web.dev, Web Vitals — https://web.dev/articles/vitals
- [S 57] web.dev, Largest Contentful Paint — https://web.dev/articles/lcp
- [S 58] web.dev, Interaction to Next Paint — https://web.dev/articles/inp
- [S 59] web.dev, Cumulative Layout Shift — https://web.dev/articles/cls
- [S 60] web.dev, Optimize Cumulative Layout Shift — https://web.dev/articles/optimize-cls
