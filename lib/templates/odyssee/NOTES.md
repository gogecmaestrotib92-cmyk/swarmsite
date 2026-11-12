# odyssee — template for clinics and other photograph-led small businesses, rebuilt from odysseeclinic.com.au

Measured 2026-11-12 at 1440×900 and 390×844. Run: `python3 -I build.py odyssee clinic1|hotel1`.
Measurements: `ref/anatomy.json`, `probe/tree-d.txt`, `probe/tree-m.txt` (box, type, ground, position, transition of every
element), `probe/motion.json` (positions sampled every 100 px of scroll, both widths), `probe/behave.mjs` (hover, menu),
`probe/reveal.mjs` (the word-by-word entrance). Reference screens: `ref/ref-d-*.jpg`, `ref/ref-m-*.jpg`,
`ref/page-treatments-full.jpg`, `ref/page-about-full.jpg`, `probe/ref-menu-*.jpg`, `probe/ref-tile-hover.jpg`.
Ours: `out/<client>-d-*.jpg`, `out/<client>-m-*.jpg`, `probe/our-*`, `probe/v-*` (scratch variants), `pairs/`.

The reference is photograph-led (studio photographs and short looping films of skin, faces, gel). Nothing in it needs
illustration, 3D or cut-outs except the closing band (a film of a pearl with the name on it); that band takes a photograph.

## Sections of the reference, in order, and the data each takes
| # | reference (measured at 1440) | data | clinic1 | hotel1 |
|---|---|---|---|---|
| 0 | header 46 high, sticky at 0, ground colour, lies *under* the first screens (they cover it until they have passed). 12 columns, gutter 20, gap 10. Wordmark left; right: MENU, one section link, the call — 14 px caps, tracking .028em, 60 apart; a 7 px dot comes in at the left on hover (.5 s) | `brand.logo` (else name in the serif) · `hero.secondary` · `cta` | logo.png, Menü, Kontakt + Sprechzeiten, Termin buchen … | name, Menu, Accommodation, Tariff and Booking |
| 0b | menu: panel 363 wide at the right edge, drops from the top in 1.2 s cubic-bezier(.16,1,.3,1); the page behind blurred and whitened; CLOSE; numbered list 28/30.8 serif; a 101×178 picture with a sentence; block on the ink colour with A. / C. / S. rows in white | `nav` + `cta` · `hero.kicker` (+ a small picture when one is left) · `place.address`, email, phone, social | 7 entries, address block; no sentence (kicker is the name) | 6 entries, "Bed and Breakfast", address block |
| 1 | two first screens, each 100vh: a film, then a photograph. One row sticky at 50 % of the height runs over both: wordmark (cols 1–2), h1 18/19.8 serif (cols 3–5), three links and the call 13 px caps, all white with a soft shadow. Each picture 110 % high, moving ±8 % against the scroll | `brand.name` · `hero.title` · three `nav` entries of 14 characters or fewer · `cta`; two largest backdrop photographs | wartebereich, behandlungszimmer-2 (897 high: banners 690 high, see "Not transferred") | entrance, room-2 (100vh, moving) |
| 2 | opening statement: picture 225 wide in cols 1–2; h2 48/48 serif in cols 4–12, first line indented 120; under it 15/19.5 text 312 wide and a 12 px caps link | `hero.text` (52 px to 170 characters, 35 px beyond) · `hero.text2`, `hero.note` · `hero.primary`; one small picture | strassenschild (225 wide, own proportion) | keys |
| 3 | pinned list: "n : 4" and a caps label, hairline with a progress line; four columns 350 wide — film 350×263, "(n)." + h3 18 serif + text. The block pins at mid-height; the active column is at full strength, the others at 10 %, their text hidden; .3 s cubic-bezier(.16,1,.3,1). At 390 the columns lie on top of each other and one shows | `steps.title` · `steps.items` (own picture, title, text, cta) | 3 columns 466 wide | 3 columns |
| 4 | two tiles edge to edge, 720×900, photographs in one colour (grey, differenced, screened with the ink); caps label centred, sticky at 50 %; on hover the picture comes back in colour, the other tile pales, a white dot stands before the label | `catalogue.groups` that have a link, else the first two `links`; two backdrops | Erwachsene / Kinder on hausnummer, treppenhaus | Accommodation / Tariff and Booking on room-3, room-red |
| 5 | caps label left; 32/33.6 serif statement in the right half, indented 120; caps link 36 under | `statement.title` · `statement.text` · `hero.secondary` | yes | yes |
| 5b | (treatments page) numbered list: number, name, the open one with its text; a picture at the right | `catalogue` (groups, items, prices) or `features.items`; the first row open; one backdrop when left | 15 services in 2 groups, bueste at the right | tariff, 2 rows with prices |
| 6 | tall film 700×1233 in cols 7–12, widening from 560 to 700 as it enters; small film 233×291 in cols 5–6 sticky at 30 % with a 15 px caption; h2 48 serif at the foot of cols 1–4 | `close.title` · `trust` as lines · one backdrop, one small picture | leuchter (897 high), 5 lines, no small picture | room-twin, 5 lines |
| 6b | (about page) heading 48 serif in cols 10–12; under a hairline a person: name 28 serif, portrait 225, role 12 px, text | `team` — people with text in that row, people without in four columns (portrait up to 342, name 21 serif, role 12) | 10 people with portraits | — |
| 7 | band 110vh, full width, moving ±8 %; three caps words left / centre / right over it | one backdrop · `steps.items[].k` (each ≤ 14 characters) | eingang; Praxis / Erwachsene / Kinder | grounds; Our Rooms / Breakfast / Location |
| 8 | 32 serif statement in the left half, 24 under the band | `steps.text` | yes | yes |
| 9 | caps label cols 1–2; text 225 wide cols 3–4; two tiles 348×429 in cols 7–12, same one-colour treatment | `hero.kicker` · `close.text`, `close.cta` · two further `links` with two backdrops (else the two links as caps links) | links Praxis, Wir (no photographs left) | Location, News on bathroom, room-detail |
| 9b | (no such part) | `plans` → row part; `faq` → list part, two columns from 8 rows; `quotes` → 35 serif statements side by side with name and title; `credentials`, `locations` → row part | — | 13 questions, 2 reviews, 2 awards |
| 10 | foot, 160 above: line 18 serif; A. address / C. e-mail, phone / S. links; hours table; © left, legal links right at 13 px | `hero.title` · `place` / `contact` · `place.hours`, `phone.note` · `foot.legal`, `foot.links` | 4 hour rows, "Freitag nach Vereinbarung" | no hours |
| 11 | closing band 75vh: sticky under the foot, uncovered as the foot leaves, shrinking from 1.5 to 1 | one photograph (a detail first) | blumen | breakfast |

## Measures used (1440 / 390)
Grid 12 columns, gutter 20, gap 10 / 6 columns, gutter 16, gap 8. Body 15/19.5 / 13/16.9. Caps 12 px, tracking .03em.
Serif 48/48, 32/33.6, 28/30.8, 18/19.8 / 32, 24, 18. Section distance 120 / 96; foot 160. Radii 0 everywhere. Hairlines
1 px ink at 20 %. Colours: the reference is two-colour (warm white ground, navy ink); ours are `palette.ground` and
`palette.ink`; `palette.accent` is used only for the 7 px dots.

## Font stand-ins
PS Times (commercial) → **Instrument Serif** (Google, OFL): narrow, light, Times-like at display size. It is narrower and
smaller on the body than PS Times, so the sizes are set a step up (52 / 35 / 31 / 21 / 19 for 48 / 32 / 28 / 18 / 18) —
chosen by eye against the reference's line lengths, not measured.
Basel Grotesk (commercial) → **Hanken Grotesk** 400 (Google, OFL).

## Motion — measured, and what is reproduced
| measured | reproduced |
|---|---|
| first-screen row sticky at 50 % over 1800 px; header under the screens | yes, same |
| pictures 110 % high, translate −8 % … +8 % over their pass (hero, tiles, band, tall film) at 1440; none at 390 | ±4 % with scale 1.085, only from 1024 wide and only on photographs that can afford it (see below); none at 390 |
| pinned list: fixed at mid-height for 1350 px; active column 1, others .1; text 0/1; .3 s; counter; progress line. The following tiles slide *over* the pinned block (no spacing is added to the page) | sticky for n × 20vh with spacing added, so every step is seen before the tiles arrive; same strengths, timing, counter, line |
| tiles: label sticky at 50 %; hover — colour back, layers to 0, other tile pale, .3 s cubic-bezier(.4,0,.2,1) | yes; on hover a 38 % veil stays and the label takes a shadow |
| tall film: outer scaleX .8 → 1 with inner 1.2 → 1 (560 → 700 wide) while entering; small film sticky at 30svh | clip from the right 20 % → 0 over the same stretch; sticky 30svh |
| headings set word by word: each word 10 px up and from 0 to 1, about .6 s, one after the other across about .45 s; text blocks and pictures follow | yes: .6 s cubic-bezier(.16,1,.3,1), 18 ms per word, blocks .35 s later |
| links: dot from the left (.5 s), underline drawn out (.4 s) | yes |
| menu: 1.2 s cubic-bezier(.16,1,.3,1); page blurred | yes; Escape, backdrop click and CLOSE close it; opens without scripts through `:target` |
| closing film: sticky, scale 1.5 → 1 as the foot leaves; a label follows the pointer | sticky and scale yes; no label |
| a loader (full-screen blurred picture, the line centred, fade 1 s) is in the DOM | not reproduced: it was already at opacity 0 in every sample, so its timing was not measured |
| live clock and "today" row at full strength in the hours | not reproduced (not client data; day names are free text) |
With reduced motion: no transitions, no pin, no movement, everything visible. Without scripts: everything visible, list
unpinned in columns.

## Not transferred, and why
- **White words on the pictures.** The reference sets white 13–18 px words on bright photographs with only a shadow; the
  gate does not pass that. First screens: 12 % over the whole picture plus a soft fall-off centred on the row (50 % at
  the row, 0 at top and bottom of the screen). Band: the three words stand in ink directly under the picture. Closing
  band: no words. Tiles: the one-colour treatment is multiplied with the ink lifted to luminance .155, so the lightest
  pixel still gives white 12 px words 4.5:1 — darker than the reference's pale blue.
- **Secondary words at 30 % opacity** (other weekdays, legal links): ours use the lightest ink that still gives 4.6:1.
- **100vh pictures from 690-high banners.** A photograph is enlarged at most 1.3× at 1440. clinic1's banners give
  897-high screens, tiles and band instead of 900 / 990, a 897-high tall picture instead of 1233, and do not move.
- **Films** → photographs (the clients have no film). `media.video` is not read.
- **Owner's rule "no picture boxed beside text"** — the reference places pictures in the grid beside type in three
  places (225 picture beside the opening statement; tall picture with small picture and heading; text with two tiles).
  These are kept as measured: unframed, square-cornered, on the grid, the picture the larger part in two of the three.
  This is a judgement; if the rule is read strictly, sections 2 and 9 are the ones to change.
- **Label on the statement** (5) sits at the left as in the reference; the reference's opening statement (2) has no label.
- **Phone first screen**: the reference hides its h1 there and shows only wordmark, BOOK, MENU. Ours shows name, menu,
  the h1 and the call, so the first screen has its heading.
- **Phone header**: the call stays in the header only when it is 10 characters or shorter; otherwise menu only.
- Inner-page parts (list, person row) are taken from full-page screenshots of /treatments and /about, not from the DOM.

## Image slots
All the client's own photographs, each used once. Backdrops = not small, ≥ 1200×560, place roles before details.
hero-1 = largest by area · hero-2 = second largest (only from 7 backdrops) · foot = first detail (from 5 left) ·
band · tile-1, tile-2 (a pair or none) · method · list · approach-1, approach-2 (a pair or none) · statement and
method-small from pictures under 1200 wide · step-n = `steps.items[n].img` · portraits with their people only.
clinic1: 22 of 22 used. hotel1: 13 of 13 used. No slot takes a made picture; a slot without a photograph is left out
(tiles fall back to a plain ground of the tile colour, 429 high).

## Picture share (`tools/coverage.mjs`)
reference 58 % (4 wide screens) · clinic1 53 % (4) · hotel1 51 % (5). hotel1 is 7 below, 2 beyond the allowance: its
tariff, 13 questions, 2 reviews and 2 awards are text the reference's home page does not have, and all 13 photographs are
placed. On the reference's own sections alone (scratch data without those blocks): clinic1 58 %, hotel1 59 %.

## Checks
shots.mjs, both clients, 1440 and 390: sideways 0, distorted 0, h1 1, errors []. legible.mjs: ok for both (445 and 447
readings), and ok for both no-picture variants. Focus ring 2 px solid in the text colour. Reduced motion and no-script
states checked in `probe/ours.mjs`.
