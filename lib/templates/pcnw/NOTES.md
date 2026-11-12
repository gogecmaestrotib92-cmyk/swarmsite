# pcnw — the practical school template (reference: pcnw.org)

Measured 2026-11-12 at 1440 and 390: the home page, and two inner pages for parts the home page does not have — the
rates page (`/facilities/hours-rates`: the ruled price table) and the classes page (`/education/classes`: outlined
cards two across, the colour band of outlined links). Raw readings: `ref/measure.txt` (every element with computed
styles, both widths), `ref/anatomy.json`, `ref/sub/rates-measure.json`; scripts `ref/measure.mjs`, `ref/motion2.mjs`,
`ref/motion3.mjs`. The reference does not depend on illustration, 3D or cut-outs (one drawn picture, see "not transferred").
Test clients: `school1` (primary), `law1`. No made pictures; the picture family is the client's own photography.

## Sections of the reference and what each takes

| # | reference (measured at 1440) | ours takes | school1 | law1 |
|---|---|---|---|---|
| 0 | notice: black band 138 high, two bold centred lines 25px, slides in from the right | `hero.text2` if ≤ 60 characters + `hero.note`; band in the ink colour | one line | two lines, the number is a tel link |
| 1 | small row 44 high, right-aligned: three links 12.8px bold + social marks | `contact.phone`, `email`, `signin`, `place.social` as words (no marks taken) | phone, mail, 4 | phone, mail, 3 |
| 2 | header 117 high, ruled 1px above and below, **not fixed**: logo 130×85 at x=50, four capitals 16px bold spread evenly, black button 184×48 | `brand.logo` (85 high) or the name in bold capitals; `nav`; `cta` | sun mark, 6 links | wordmark, 7 links |
| 3 | opening: film across the page, 675 high (¾ of the screen), 21 % black film; kicker 19.2 condensed capitals, h1 67.2 bold with a second line at 96 in capitals; words at mid height, 72 from the left | first landscape photograph ≥ 1600 wide; `hero.kicker`, `hero.title` (at 96 in capitals when ≤ 22 characters, else 67.2), `hero.text` in the reference's 24/31 lead | door-group.jpg, 67.2 | colleagues.jpg, 96 capitals |
| 3b | one outlined button centred under the opening (2px, 12×24, 14.4 condensed capitals — its "pause" control) | `hero.primary`, `hero.secondary` as that outlined button | 2 | 2 |
| 4 | centred statement: 60.8/73 bold, then 24/31, both ≤ 1030 wide, 50 above | `statement`; `figures` under it when the client also has quotes | statement | statement + 4 figures |
| 5 | four outlined cards 332×270, 10 apart, 2px border each in one of the four colours, title 24 capitals, text 17.6, centred; under the pointer the card fades to its colour in 0.6s | `features`: section head + cards. Four across only for exactly four short items; else the classes-page build: two across (20 apart), an odd last one full width | 7 cards, two across | 6 cards, two across |
| 6 | (classes page) colour band ≈ 394 high, centred 44.8 heading, four outlined white links; (rates page) table 1230 wide: group title row in bold capitals, rows 55 high, cells 15 padding, 1px grey rules, every other row tinted 7 %, 15.84/23.76 | `catalogue`: band = title, text, one outlined link per group (jumps to the group); table = groups and items: name (link) · note · price; an item's `text` on a second line of the row in italic; `prices[]`, `rows[]`, `state` read too | 8 links, 46 rows | 4 links, 12 rows |
| 7 | section head (44.8 bold, the part before a colon in the lead colour, one line 17.6, hairline) + filled tiles 468 high, 20 apart: row of two at 60/40, row of three; date line 14.4 capitals, title 28.8, words at mid height 50 from the left; the tile's picture lies hidden under the colour and shows under the pointer in 0.3s | `steps` (k → small line, title, text, cta as a small capital line; the whole tile is the link); `place.events` the same way. A step's picture is used under the colour only if it is ≥ 900 wide | 4 tiles 2+2, no pictures (they are 450 wide) | 4 tiles, no pictures |
| 8 | colour band 547 high: photograph on the left 40 %, orange right with one italic quote 24/31, attribution 14.4 capitals right-aligned, a 240px quotation mark in a tint | all `quotes`; without quotes the `figures` (value 44.8 bold, label 17.6, two columns). Second landscape photograph ≥ 1600 on the left under the colour | figures over teacher.jpg | 3 quotes, flat band |
| 9 | three ruled rows 605 wide (title 24 capitals in the second colour, arrow at the far end, 17.6 text, 2px rule, 50 above and below) beside a drawing 720×622 | `links` (t, d, h) in two columns of such rows; no drawing | 9 rows | 8 rows |
| 10 | people: section head; four cards 313 wide 24.5 apart on a track (picture 313×500, hairline, name 25.6 regular); round arrows 48 in the lead colour below; moves one card every 8s in 0.5s, stops under the pointer | `team`: a landscape `people` photograph 1000–1599 wide across the section at its own size; people with a portrait on the track (role, text, phone, mail under the name); people without one four across in type only | group photo + 11 in type | panorama + 10 on the track + 25 in type |
| 11 | centred capital line 22.4 + six pictures edge to edge, 4px apart, 237 wide (three across on a phone) | `place.spaces[0]` title and text centred; up to six landscape photographs not used elsewhere, `room` first, each never wider than its pixels; other spaces as ruled rows | 6 rooms + 1 row | left out |
| 12 | (not on the home page) | `plans` in the two-across outlined cards (price at 44.8, rows, outlined button; a marked plan filled); `faq` as ruled rows that open | none in the data | none in the data |
| 13 | (the same ruled rows) | `credentials` (t, year, text, link, the client's own badge picture 302 wide above the title) in the lead colour | 6 | 5, three with pictures |
| 14 | closing band 600 high: green left 902 wide with 67.2 capitals, one capital line 17.6, the call in 19.2 condensed capitals on a pale disc 77 across; photograph right 537 wide | `close` (text in capitals only when ≤ 90 characters); third landscape photograph ≥ 1600 on the right under the colour | students-outdoors.jpg | flat band |
| 15 | foot, ruled above: wide column 326 + four of 237, headings 20.8 capitals, text 14.4/20; black bar 64 high with 12.8 text | column 1 `brand.name` + `trust`; one column per `locations` entry, or one for `place` (city as heading: address, phone, mail, hours); a column headed by `contact.form.t` with `routes` and the social links; bar: `foot.legal`, `foot.links`, notices | 3 columns | 5 columns |

No heading on the page is the template's own: every visible word is the client's. Words kept only as accessible names
(never shown): Menu, Previous, Next, by language.

## Measures used
Fluid between the two measured widths (390 → 1440): h1 49.6 → 67.2 (short title 59.2 → 96), statement 35.2 → 60.8,
section heads 33.6 → 44.8, card titles 20.8 → 24, tile titles 20.8 → 28.8, quote 19.2 → 24, closing heading 51.2 → 67.2,
notice 17 → 25; body 17.6/22.88 at both; table 15.84/23.76. Page margin 4vw (57.6 / 15.6), opening 5vw (72 / 19.5),
cards and foot 3vw. Section distance 100.8 (47 on the phone), people 129.6. Letter-spacing −0.2px on running text,
0.8px on capital lines, 0.3px on card titles. No radius anywhere except the round arrows and the disc; no shadows.
Phone: small row hidden, the navigation folds into a three-bar control (32×3 bars as measured) that opens a panel;
cards, tiles, rows, people one per row (cards 338 high, tiles 439 high with 10 padding); track shows one person;
strip three across; the table stays a three-column table as on the reference (which itself runs 48px sideways there —
ours does not: fixed layout, 43/30/27 %).

## Font stand-ins
Reference: DIN (commercial) for everything, Gravur Condensed (commercial) for the kicker and button labels.
Ours: **Barlow** 400/700/400 italic (open licence, drawn after the same road-sign letterforms) and **Barlow Condensed**
700. The reference asks for weight 900 in capital lines but its DIN has no such cut and draws bold; ours uses 700 there.

## Motion — measured, and what is reproduced
| measured on the reference | ours |
|---|---|
| header and everything else scroll away; nothing fixed or pinned (header top −400 at scroll 400) | same |
| each section fades in once when it enters: opacity 0 → 1 in 1.25s (keyframes read) | same, only when scripts run; 8 % before the lower edge |
| notice text comes in from the right, 1.25s; its slider turns every 5s (one slide) | the entrance only |
| card: back face fades over the front, 0.6s ease-in-out (sampled 0.08 at 100ms, 0.55 at 300ms, 1 at 600ms); back shows the title and an outlined "more" label | a card with a link has that back face (title, the item's own label if it has one); a card without a link fills with its colour over the same 0.6s ease-in-out (measured 0 → half at 300ms → full) |
| tile: colour overlay → black at 40 % in 0.3s, showing the picture | with a picture: black at 62 % (so the words still read); without: the colour darkens to 72 % in 0.3s, linked tiles only |
| header button black → green, 0.3s; navigation words → orange; row headings → their tint, 0.3s | button → the first palette colour that is not the ink (law1: its yellow, dark words); navigation → second colour; rows → tint; 0.3s |
| people track: one card every 8s, 0.5s, stops under the pointer, loops; arrows swap ground and sign in 0.5s | measured on ours: one card per press (337px, settled in about 0.35s — the browser's smooth scroll, not a 0.5s ease), one card per 8s when idle, back to the start after the last; stops under pointer and focus; arrows swap in 0.5s. Without scripts the track scrolls by hand |
| opening film: 26.7s loop, muted, with a pause button | no film: a still photograph (see below) |
| keyboard focus: 2px black outline with a 4px white halo | same, in ink and ground |
| reduced motion | measured on ours: 0 hidden sections, 0 running animations, longest transition 0; the track does not move by itself |

## Not transferred, and why
- **Three places where the reference puts a picture beside words** (owner's rule): the quote band (photograph 40 % |
  colour 60 %), the closing band (colour 63 % | photograph 37 %) and the link rows beside a drawing. In the two bands
  the photograph now lies under the band and the colour is laid over it: flat where the words stand, clearing over
  about 150px to the photograph, which reaches three edges of the band; no frame and no hard edge. The photograph is
  fitted to the part that shows, so its middle is seen (both of school1's are centred on faces). **Open to the owner's
  eye**: the words still do not stand on the picture — it reads as a band that is half photograph. A stricter reading
  would lay the photograph under the whole band with a veil; with the colour at reading strength the picture would then
  hardly show. The drawing beside the link rows is dropped and the rows take both columns.
- **The opening film** → a still photograph. With a veil of 66 % black under the words (21 % at the far right; 66 %
  everywhere on the phone) instead of the reference's 21 %: 21 % does not hold white words on school1's pale wall.
- **The second size in the h1** (one phrase at 67, one at 96 in capitals): a client's title is one phrase and is not
  split; short titles take the large size whole.
- **The first tile's pale tint** (white on light green, 2.6:1 on the reference): ours is the second colour at full
  strength.
- **"Photo coming soon" slabs** for people without portraits: not built; such people are set in type.
- **Mega menus** under the four navigation words: the data has flat `nav`; plain links.
- **Footer headings** ("Visit us", "Open hours", "Quick links", "Policies"): the data has no such words. Columns are
  headed by the brand, the city or office names and the contact form's own label; hours stand under the address; there
  is no column of quick links; legal links stand in the bar.
- **Social marks and the cart**: brand icons are not taken; names in words.
- **Portrait proportion** 313×500: ours takes the first portrait's own proportion (law1: square), cropped no further.
- The classes-page band stood after its content on the reference; here it stands before the table as its heading and index.

## Pictures
Chosen by size, proportion and role, each once, never all of them:
| slot | takes | school1 | law1 | with none |
|---|---|---|---|---|
| `hero` | 1st landscape ≥ 1600 wide, not a portrait | door-group 2400×968 | colleagues 2000×1334 | flat ink band |
| `band` | 2nd such | teacher 1900×768 | — | flat colour |
| `close` | 3rd such | students-outdoors 1900×768 | — | flat colour |
| `team` | landscape `people`, 1000–1599 wide | team 1200×800 at 1200 | firm-group 1128×376 at 1128 | no picture |
| portraits | each person's own | none (type) | 10 at 313×313 | type |
| `strip` | up to 6 other landscape pictures, `room` first, each ≤ its pixels (237 wide at 1440) | patio + 5 classrooms (450×338 at 237×178) | left out (none left) | left out |
| tile, under the colour | the step's own picture if ≥ 900 wide | none qualify | none | flat |
| credential | the client's own badge file | — | 3 award pictures at 302 wide | — |
Still without a slot: school1's 8 other small pictures (office, teachers' room, 4 of people, tango, flamenco).
A small picture is never shown wider than its pixels (`max-width` = its width on every picture element).

**Picture share** (`tools/coverage.mjs`, 1440): reference 44 % (per screen 67, 11, 64, 44, 38, 53, 43, 30 — the 64 and
44 are the event tiles, whose pictures lie under opaque colour and are not seen at rest). school1 **14 %**
(67, 11, 0 ×7, 14, 16, 24, 52, 11, 11, 23, 10), law1 **12 %** (67, 11, 0 ×6, 71, 0, 0, 10, 4, 0). **Both are more than
5 points under the reference — the rule is not met.** Wide pictures stand where the reference has them (opening,
colour band, closing band for school1; opening only for law1). The gap comes from the length: school1's page is
14 962 px against 6 822, of which the price list is 4 500 px and the people in type 1 100 px with no picture, and from
tiles that have no picture to hide. It cannot be closed with these clients' photographs inside the rules (14 of
school1's 18 are 450 px wide).

## Checks (final build)
`shots.mjs` school1: d height 14962, sideways 0, distorted 0, h1 1, errors [] · m height 21100, sideways 0, distorted 0, h1 1, errors [].
law1: d 12495, 0, 0, 1, [] · m 20675, 0, 0, 1, [].
`legible.mjs`: school1 ok (0 of 1115), law1 ok (0 of 998); with all pictures removed ok (1104, 1103).
Focus ring present on the first 14 tab stops; phone menu opens (9 / 10 links); without scripts nothing is hidden
(sections are hidden only under `html.js`, which a script sets).

## Where ours still differs when the pairs are looked at
- Barlow is rounder and a little wider than DIN; headings read heavier.
- The opening has a paragraph and a darker film; the reference's is a title alone on a brighter film.
- Cards are two across and taller (the clients' texts run to 250 characters), so that part reads as the reference's
  classes page, not its home page row of four.
- The bands' pictures melt into the colour instead of meeting it on a line; no quotation mark on school1's band (figures).
- school1's foot has three columns spread over the width where the reference has five.
- law1 is navy throughout (its palette has one deep colour) with yellow bands; the reference has four colours.
- The price table's rows with a second line: the vertical rules stop above that line.

## Not checked
- The 390 build was looked at for school1 only (twelve screens); law1's phone build went through the tools, not the eye,
  beyond its first screen in `pairs/`.
- Tablet widths (768–1100): rules exist (cards two across, people three across, folded navigation), not looked at.
- Hover states were measured on ours for the card and the track only; the others were not looked at.
- `plans` and `faq` rendered with sportbot's data without error and not looked at. `place.events`,
  `catalogue.items[].prices/rows/state`, team `groups`, a card with a link (its fading back face), a tile with a large
  picture under it: written, never rendered with data that has them.
- Safari and Firefox (`tr:has()`, `color-mix` is not used, `text-wrap: balance`).
- Screens wider than 1440.
- `ref/anatomy-*.jpg` and the stepped shots of the two inner pages were deleted again: the disk was full (118 MB free)
  during the build; `anatomy.json`, the full-page shots and all measurements are kept.

## Disc under the closing call (2026-11-12, engine stress)
The call's first letters stand on the pale disc. Taken as the slider arrows' tint (half way to the label colour), the
disc dropped the label to 2.96:1 on fernhollow's green. The disc is now its own colour (`--dp`): pale only as far as the
label still reads 4.5:1 on it at the hover opacity (.75); when that leaves no visible disc it goes the other way
(darker under light words), which only adds contrast. The round arrows' tint (`--tp`) is held at 3:1 against the button.
Stress (engine, fernhollow / pellbrook / wendholm / svetlinka): every variant passes.
