# bronxarts — a type-led school template in colour blocks

Reference: https://bronxarts.net (a charter school in the Bronx). Measured 2026-11-12 at 1440×900 and 390×844: the home
page, and for the parts it does not carry, eight sub-pages: /statistics/ (numbers), /leadership/ (people),
/contact-us/, /admissions/, /our-schools/ (rows of facts on a colour), /curriculum/ (cards with a small picture),
/teacher-spotlights/, /who-we-are/. Measurements: `ref/anatomy.json`, `probe/ref-tree-{d,m}.txt`,
`probe/sub-*-tree-{d,m}.txt`, `ref/motion.json`. Screens: `ref/ref-{d,m}-NN.jpg`, `ref/ref-{d,m}-full.jpg`, `ref/sub-*`.

**Pop-up.** On load a welcome panel (a photograph of a child, an enrolment line, "Apply Now") opens over a 40 % black
backdrop. It was closed every time with its own × (`#customModal .custom-close`, 94×86 at the panel's top right);
nothing was accepted. `ref/ref-{d,m}-popup.jpg` show it open; `ref/anatomy-*.jpg` (made by `tools/anatomy.mjs`, which
cannot close it) still show it; every other reference screen does not. There is no cookie banner.

**Children.** The reference's photographs are of its pupils. None was taken, copied or described here; only boxes.

## Sections of the reference and the data each takes
| # | Reference (where) | Ours takes | school1 | clinic1 |
|---|---|---|---|---|
| 0 | Top line 48 high, white: small links (14/16 medium) right, a lime button 98×32 (home) | `hero.secondary`, phone, email, `signin` → links; `cta` → button | 3 links + Booking | 3 links + Termin buchen |
| 1 | Navigation 131 high over the opening (white type on the picture), logo 219×78 left, 7 links (16/19 medium) right (home) | `brand.name` (logo only in the stuck bar: logo files are usually dark), `nav` | yes | yes |
| 2 | Opening: video 1440×820 behind, 40 % black veil, h1 80/90 bold max 993, paragraph 18/27 medium max 497, lime button 180×70 sitting on the opening's foot (home) | `hero.title` (h1), `hero.text`, `hero.primary`; backdrop = `media.video`, else the widest people/exterior/room photograph that fills 1440×820 | door-group.jpg | eingang.jpg |
| 3 | Three cards 480 wide: a colour field 350 high (lime/sky/teal) with a 403×320 picture standing on its foot, a navy panel 175 high with the name in the field's colour (37/54 bold) and "Learn More" + arrow (home) | `links[0..2]`: t, d, h; picture = an unused photograph whose description shares words with the link, else by role. If all three fill 480×350 they fill the field edge to edge (reference proportion kept); if they fill only 403×320 they stand inset as on the reference; else the field is a 30 px colour strip | inset (team, oficina, school-group) | full (strassenschild, wartebereich, behandlungszimmer-2) |
| 4 | Two banners 1440×739 ("Our Students", "Our Teachers"): a 738×739 picture from the window's edge, beside it the copy on a colour (h3 50/58 bold, 18/28 text, white button 180×70); left/right alternate (home) | `steps.items[]` and `place.spaces[]`, each with its own `img` when that picture fills the half (height held between 500 and 739 so a picture is not enlarged past a tenth). The teachers banner: a `team` with no portraits of its own takes an unused people photograph that fills the half for `team.title` + `team.text`, placed where the team stands (after the price lists), its names listed under it | 1: the team banner (team.jpg); every step's own picture is 450 px, too small for a half | 3 step banners (behandlungszimmer, behandlungseinheit, stofftiere) |
| 4b | Curriculum page: three colour cards 447 wide, a 291×288 picture, h3 50/58, text, an arrowed link at the foot | the steps/spaces whose own picture is too small for a banner — their own small picture, never enlarged | 6 cards (4 steps + 2 rooms) in 3+3 | none |
| 5 | Navy section: a video 1382×763 inside 48 px, then a 50/58 medium title left (with a drawn arrow) and an 18/28 paragraph right (home) | `statement.title`, `statement.text`; the video slot → an unused wide photograph at its own proportion (no drawn arrow: owner's rule) | teacher.jpg (1900×768) | a wide practice photograph |
| 6 | Navy block 1104×672 with two 42/52 medium sentences, a 336×672 column of colour shapes at the right edge (home) | `hero.text2` (+ `hero.note`); the colour column is two flat blocks of the palette (see below) | yes | left out (no text2) |
| 7 | Numbers page: a blue block, padding 128, rows of an uppercase 18/28 bold label left and a 60 px number right, 1 px rule under, two columns | `figures[]` (v, l) | 5 rows | left out |
| 8 | Numbers page head: 42/52 bold names over 2 px rules, an uppercase 16/20 line, 15/28 text, two columns | `credentials[]` (t, year, text, h), else `trust[]` | 6 | 5 (trust) |
| 9 | Schools page: colour blocks, uppercase eyebrow 16/20, 80/90 title, facts as label left / 36/48 value right with a rule under | `catalogue`. **Folded** (CONTRACT "A long list is folded") when it has more than 12 items: one deep-colour block with the catalogue's title and text, then one facts row per group — the group's name (36/48) with its first three items under it (15/28), at the right the group's price range in the client's own strings (lowest – highest, only when every item states a price in one currency; else the count), a plus that turns to a minus — each a native `<details>` that opens in place to the group's full rows (name uppercase, price at 36 px right, note/text/prices/rows under), the group's own picture and its link. Nothing is dropped. With 12 items or fewer: one colour block per group as before | folded: 8 groups (46 items) | folded: 2 groups (15 items) |
| 10 | Leadership page: a 60/72 section title, people in two columns as 50/58 medium names over an 18/28 role | `team` (title, text, items or groups); a portrait only when the person has one (at most its own pixels, ≤291). More than 12 people: each group (or the whole list) becomes the same facts row — name, first three people, count — opening in place | 11 people, type only, under the team banner | 10 people with portraits |
| 11 | (no part on the site) | `features` (title, text, items) as the leadership list with 36/48 names; left out when every item is also in the catalogue | 7 | left out (same 15 as catalogue) |
| 12 | Plans and questions: the site has neither | `plans` as numbers-page blocks (price at 36 px, rows ruled); `faq` as the leadership list in one column | none | none |
| 13 | Two cards 504 wide: a 504×257 picture above a sky-blue panel (36/48 title, 18/28 text, arrowed link) (home) | `links[3..]`; picture only where the link has a sentence and an unused photograph fills 504×257 | 6 cards | 2 cards |
| 14 | Contact page: 60/72 title, an 18/28 sentence, the e-mail at 36/48 underlined, per school a bold 20/31 name, address, telephone | `brand.name`, `close.text`, `place.email`, `place.phone`, `place.address`, `locations[]`; right: `place.hours` as label/value rows, `contact.routes`, booking button, `place.social` | yes | yes |
| 15 | Enrolment band 1440×540: a 60/72 title and a white button over a field of colour shapes (home); the admissions/schools pages put a colour panel with a round end over a photograph running to the right edge | `close.title`, `close.cta`; with an unused photograph → the round-ended panel over it, else the colour blocks | students-outdoors.jpg | hausnummer.jpg |
| 16 | Foot: logo 146 square, link columns (16/24), a lime button 180×70 right; small links 14/21; 13/28 line at half opacity (home) | `brand.logo` (else name), `nav` in two columns, `place.social`, `cta`; `foot.links`, `foot.text`, `foot.legal`, `place.notices` | yes | yes |

Not placed (needs.json `drops`): `quotes` only when there are more than two; `media.screens`, `media.phones`; `steps.title` and
`steps.text` (the banners carry the items, the reference has no section title there); `place.since`, `price_range`,
`events`; `projects`.

## Measures used (1440 → 390)
- Page: white ground, black ink; content inset 124 (container 1320, padding 64) → 32. Breakpoints: navigation collapses
  below 1400 (the reference's `d-xxl-none` menu button shows up to 1399), single column below 992.
- Type (reference Sailec): h1 80/90 → 50/60; section titles 60/72 → 42/54; block titles 50/58 → 50/60; card names
  37/54 → 50/60; large sentences 42/52 → 32/46; numbers 60/60 → 42/48, values 36/48 → 32/42; body 18/28; labels
  uppercase 16–18 bold; nav 16/19 and 14/16 medium; foot 16/24, 14/21, 13/28.
  A heading is set no larger than its longest word allows on that width (`--mw` = letters of the longest word), so
  "Accommodation" or "Zahnmedizin" never breaks inside the word; the reference's own words never needed it.
- Buttons: 180×70, square corners, bold 16/28, lime on the opening and in the foot, white on colour blocks. Phone top
  button 48 high. Header button at 1440: 98×32, 14/20.
- Blocks: banners 739 (720 + 720), padding of copy 0 80 0 128; colour blocks padding 128 → 64/32; card rows 1 px
  rules and 32 px under; numbers rows 80 apart.
- Colour, as relations: the reference has one deep navy that carries white type (opening veil, card panels, statement,
  sentences), one bright lime for buttons and blocks with black type, two light fields (sky, teal) behind pictures, and
  a saturated blue block (numbers, schools). From the client's palette: `dark` = the most saturated colour that carries
  white at 9:1 (else the ink); `bright` = the most saturated light colour (else accent lightened); `deep` = a second
  saturated colour that carries white at 4.5:1 (else dark and bright mixed and darkened); `c2`, `c3` = the remaining
  light colours or bright lightened. Ink on each block is the client's ink when it reads 7:1, else black or white.
  school1: dark #104567, bright #d8ae22, deep #9c0607, c2 #e0e9f5, c3 #e4c664. clinic1: dark #363636 (its ink: the
  palette has no dark colour), bright #abcb1e, deep #5b662e (mixed), c2 #dce9a0, c3 #c4db62.

## Typeface
Sailec (commercial geometric grotesque) → **DM Sans** (OFL, Google Fonts), 400/600/700. Same kind: geometric, round o,
large x-height. The reference uses three cuts: Sailec (400), Sailec-Medium (its 500) and Sailec-Bold (its 500/700). Sailec-Medium reads
as heavy as DM Sans 600 (seen in the pairs: at 500 our names and statements read light), so Medium → 600, Bold → 700.
DM Sans runs about 3 % narrower than Sailec at the same size.

## Motion: measured → reproduced
- **Header** (measured by sampling positions at 15 scroll offsets): the top line and the navigation scroll away; from
  60 px of scroll the navigation is fixed at the top, 131 high (95 on a phone, from 20 px), on white with a shadow
  `0 0 5px 5px rgba(0,0,0,.2)`, dark type and the dark logo. No transition (it switches). → same: fixed from the
  moment it would leave the window, white, same shadow and height; the logo (if any) appears only in the fixed bar.
  This header stands over content as on the reference; the legibility gate judges the text in it over everything that
  passes under it (white ground, so it holds).
- **Opening video**: autoplay, muted, loop, 72.8 s, no poster; it scrolls with the page (no parallax). → a client
  video plays the same way; otherwise a still photograph. With reduced motion the video does not play.
- Nothing else moves with scroll: no reveal, no parallax (11 elements sampled).
- **Buttons**: a half-transparent sheet (white on lime, lime on white, opacity .5) rises from the foot to full height,
  `top .09s ease-in`. → same with `height`.
- **Arrows** (44×2 line, 7 px head): on hover of the card the line doubles in length, `all .3s ease`. → same, also on
  keyboard focus. On sky cards the arrow also turns white; not reproduced (our card colour varies).
- **Links**: colour change to the link colour (top line, foot) or to lime (navigation over the opening), no transition.
- **Dropdowns** under the navigation (white, shadow `0 4px 20px rgba(0,0,0,.15)`, .1s): not reproduced — the data's
  `nav` has no second level.
- **Phone menu**: the button (68×68, three lines) opens a navy panel the full height under the header, links 20/32
  medium white with a chevron, a rule, two columns of secondary links. → a `<details>` element (works without script):
  navy panel, 20/32 links, a rule, the secondary links in two columns, the booking button; lines cross to an ×; Escape
  and choosing a link close it. No chevrons (decoration the data does not need).
- Reduced motion: every transition is off; the video does not play. Without scripts: everything is visible, the
  header is not fixed, the menu still opens.

## Where it leaves the reference, and why
- The pop-up is not reproduced (a veil over the page on arrival; the gates would judge the page behind it).
- The colour-shape illustrations (the column at the right of the navy sentences, the enrolment band's field) are the
  school's own drawn identity. Ours are two flat blocks of the client's colours — one plain, one split on the diagonal —
  in the same place and proportion; no drawn shapes, glows or gradients. Without them the navy block reads unfinished.
- The circle and the rounded-corner crop of the two banner pictures on the reference are its shape motif; ours are
  plain rectangles to the window's edge (the owner's edge-to-edge rule; a circle would read as a boxed picture).
- The statement's video becomes a photograph at its own proportion.
- On the reference the inset card picture stands on a colour field; with clinic1's wide pictures (2.9:1) the picture
  fills the field to the edges instead (it cannot fill 403×320 without enlarging).
- Long price lists: rows on the page ground under a coloured title (see 9).

## Photographs: how they are chosen (each once, never a loop)
1. A step's, a room's, a person's own picture stays with it and is never used elsewhere. Portraits only for their people.
2. Opening ← the widest people/exterior/room photograph that fills 1440×820 (enlarged at most a fifth); none → navy ground.
3. Statement ← the next unused photograph that fills 1382×520 at its own proportion.
4. Steps/spaces ← their own picture as a banner if it fills the half, else as a curriculum card, never enlarged; a step
   without a picture of its own takes an unused one that shares words with it (at most two banners).
5. Enrolment band ← an unused photograph filling 847×540.
6. Three cards ← an unused photograph sharing words with the link (small ones first).
7. Further cards ← the same, only for links with a sentence.
8. Price lists ← a picture band of the client's (1440×420, not enlarged) after about two screens of rows, when an unused
   photograph is large enough. school1 has none left (its large pictures are used above); the list stays type.
A `small` picture is never shown wider than its pixels (checked: no image enlarged beyond 1.1, small ones not at all).

## Page height (folded long lists)
Reference 6 021 px at 1440, 7 698 at 390; the target is under about 3× at 1440 (18 063).
| | 1440 folded | 1440 every group open | 390 folded | before folding (1440 / 390) |
|---|---|---|---|---|
| school1 | **14 147** (2.3×) | 19 273 | 26 491 | 20 812 / 35 366 |
| clinic1 | **10 745** (1.8×) | 13 149 | 17 046 | 14 000 / 23 292 |
At 390 school1 is still 3.4× the reference's phone page: its eleven people with long biographies (under the fold limit of 12)
and six curriculum cards are set in full. The legible gate skips closed groups (CONTRACT); the variant check was run once with
every group closed and once with every group open (`probe/variants.txt`, `probe/variants-open.txt`), both clean.

## Picture share (tools/coverage.mjs)
Reference: 45 % at 1440 (95, 54, 51, 0, 27, 63, 19 per screen; 2 screens with a wide picture: the opening video and the
enrolment band), 46 % at 390. coverage.mjs cannot close the pop-up, so its photograph is counted on screen 0 (already 95 %
from the video); the YouTube frame of the statement is not counted (an iframe), the drawn colour shapes are (images).
Our pages are longer than 1.5× the reference (folded: school1 14 147 px = 2.3×, clinic1 10 745 px = 1.8×), so by the revised rule
the share is compared on the sections that exist on both: `probe/v/<client>-core.html` = the same data without catalogue,
team list, faq, plans and features (school1's core keeps the team title and text, i.e. the teachers banner).
| | 1440 | 390 | wide-picture screens at 1440 |
|---|---|---|---|
| reference | 45 | 46 | 2 |
| clinic1 core | **45** (96, 50, 52, 66, 39, 22, 1, 38) | 38 | 3 |
| school1 core | **28** (91, 36, 21, 60, 24, 0, 0, 38, 4, 4, 35) | 25 | 2 |
| clinic1 whole page (folded) | 39 | 43 | 3 |
| school1 whole page (folded) | 20 | 17 | 2 |
- Strict part (every wide picture of the reference, in order): opening backdrop — both; banners (halves) — clinic1 three,
  school1 one (the teachers banner); statement picture (the video slot) — both; enrolment band — both, as a photograph
  running to the right edge behind a round-ended colour panel (847 wide: the tool counts it as a half, not as wide).
- clinic1 meets the share at 1440 and is 8 under at 390 (the reference stacks three full-width card portraits there).
- **school1 does not: 28 against 45.** It has 18 photographs, 14 of them 450×338 (`small`). Its four large ones are all
  used (opening, statement, teachers banner, enrolment band); every step and room carries its own small picture, which
  this template shows at its own size in the curriculum cards and never wider. The screens at 0 are the numbers, the
  credentials and the navy sentences (the reference's numbers sit on a sub-page; its sentences block counts its drawn
  column as picture, ours is two flat colour blocks). The price list is now folded into eight rows, so rule (3) (a picture band every two screens of a
  long list) no longer applies. Fixing this needs larger photographs of the school,
  not a template change.

## Checked (final build)
- shots.mjs (folded build): school1 d 14 147 / m 26 491, clinic1 d 10 745 / m 17 046; sideways 0, distorted 0, h1 1, errors [] at both widths.
- legible.mjs (the improved one: timers held, transitions finished): school1 `ok — 0 unreadable of 876`, clinic1 `ok — 0 unreadable of 367` (fewer lines than before because closed groups are not read). Earlier FAILs and what fixed them:
  the foot's small print at 4.49:1 (set at 68 % ink → 80 %), and clinic1's navigation over the bright entrance photograph
  (3.69–4.35:1 → a veil under the 131 px navigation band). Both were real, not artefacts.
- Own checks (`probe/checks.mjs`): no image enlarged more than a tenth (clinic1's 2000×690 banners at 1.07–1.10), none
  `small` enlarged; keyboard focus a 3 px outline in the ink; the header fixes at the measured point (131 / 95 high,
  white, the reference's shadow); the phone menu opens and closes on Escape; reduced motion: every transition 0 s;
  without scripts nothing is hidden and the menu still opens (the header then does not fix).
- Variants (`probe/variants.py`, `probe/vcheck.mjs`, 27 pages, run with groups closed and again with every group open): 1, 3, 5 plans; 2 and 9 features; 1 and 6 steps; a
  12-word h1; a 40-character button label; no faq; four questions; no photographs — for both clients, plus sportbot.
  No sideways scroll, no overlapping text boxes, one h1, no errors at 1440 and 390 on any. A label longer than 12
  characters leaves the phone header (it stays in the opening, the menu panel and the foot) instead of being cut.
- No photographs (`probe/v/*-nopics.html`, `probe/look/*-nopics-*`): the opening on the dark colour, the three cards as
  name strips, the steps as colour cards, lists, contact, the enrolment band as colour blocks. It reads as a deliberate
  type page in colour blocks, as the reference is type-led.
- onefile: school1 0.7 MB, clinic1 1.1 MB, nothing left out.
- Not checked: Safari, Firefox, real phones; widths between 992 and 1399 only by layout reading of the CSS (the menu
  button shows there, as on the reference); a dark page ground beyond sportbot rendering clean; right-to-left text.
- The pairs are cut from per-section captures of the live page (`probe/crops.mjs`): Chrome repeats the top of a full-page
  capture below ~16 000 px, which the unfolded school1 page exceeded. `pairs/*-catalogue.jpg` shows the folded block
  under the reference's schools-page facts block.

## Deep block deepened to 5.5:1 (2026-11-12, engine stress)
svetlinka's blue #3a7ca5 reads 4.6:1 with black and with white: its catalogue rows fell to 4.01:1 where the stuck menu's
shadow passed over them. A palette colour taken as `deep` is now moved toward black in its own hue until white reads
5.5:1 (the floor the made-up deep already had); its rows then take white. svetlinka #31698c, fernhollow #935635;
pellbrook and wendholm unchanged in effect. Stress (engine, svetlinka / fernhollow / wendholm): every variant passes.
