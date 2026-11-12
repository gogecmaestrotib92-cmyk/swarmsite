# fryreglet — a photograph-led template for works, manufacturers and firms

Reference: https://fryreglet.com (an architectural-metal manufacturer), measured 2026-11-12 at 1440×900 and 390×844 with
headless Chrome. Its home page has five parts (opening, rotating half, film band, featured half, two link tiles) and a
foot, so — as the assignment allows — three inner pages were measured too and their parts used:
`/about-us/` (short opening, words beside a pale panel, four alternating halves), `/drywall-trims-reveals-moldings/`
(the four-column grid of pale tiles, the link-list tile) and `/contact-us/` (two halves of labelled paragraphs).
`/portfolio/` did not render in the headless browser at 390 (height 844, no h1) and was not used.
Raw measurements: `ref/anatomy.json`, `ref/*-d-*.jpg`, `ref/*-m-*.jpg`; scripts in `probe/`.
The cookie bar was never accepted; it stays visible at the bottom of the reference half of each pair.

Test clients: `corp1` (CNC machining works, primary) and `local1` (joinery workshop). No `media.made` is read: the
picture family is the client's own photography.

## Sections of the reference and what each takes

| # | Reference part (page) | Measured | Client data |
|---|---|---|---|
| 0 | Header (all pages) | fixed, 140 high, name at x 60, links from x 474 every 227, 12 px bold capitals +1.2 px; clear with white words over the opening, white ground with strong-colour words after it; leaves on the way down, returns on the way up. 390: 80 high, name at 35, two-line menu button | `brand.name` (or `brand.logo`), first four `nav`, `cta` at the right; all of `nav` in the phone menu; the rest of `nav` in the foot |
| 1 | Opening (home) | 1440×900 (100vh), photograph in ONE colour (the strong colour, darks to black), h1 48/46 bold serif −1 px in the right half at x 780, a 1 px line cue at the bottom centre. 390: h1 30/36 at x 35 | `hero.title`; opening photograph by role and size |
| 2 | Words beside a pale panel (about) | 100 px above and below; left half a panel of 4 % strong colour (the reference shows a turning 3D wordmark there), right half padded 60/160/60/60: h 48/46, paragraphs 24/36 light, 60 apart | `hero.kicker` as heading, `hero.text`, `hero.text2`, `hero.primary`/`secondary` as arrow links, `hero.note`; the panel holds `figures` (48 serif + 12 px capitals) or, without figures, `trust` as ruled lines |
| 3 | Rotating half (home, "products spotlight") | 1440×900 on the strong colour: left half words (label 12 px capitals at the top, h 48 + paragraph 24/36 centred, arrow link at the bottom), right half an edge-to-edge photograph 720×900; 60 px white round buttons at the picture's edges; 5 s a slide | `catalogue.title` (label), each `catalogue.groups[]` with a title: `t`, `text`, `img`, `h` |
| 4 | Band (home) | a film, edge to edge, 1440×900 (the reference loads it from a video host; it stayed black in the headless browser) | `media.video`, else one large landscape photograph |
| 5 | Alternating halves (home "featured project"; about ×4) | 720 + 720 × 900, picture left/words right on the pale ground, then words left on the strong colour/picture right, and so on | `steps.items[]`: `k` (label), `title`, `text`, `img`, `cta` |
| 6 | Tile grid (product page) | 200 above, h 48, 100 to the grid; 4 columns of 315 × 435, gap 20, tile ground 4 % strong, padding 30, name 12 px bold capitals; on hover the tile turns white with a 1 px outline and an arrow at the bottom right | `catalogue.title`, `text`, every item: `name`, `price`/`prices`, `state`, `text`, `note`, `rows` (ruled as a table — the plant lists), `h`; `catalogue.note` |
| 7 | Two halves of labelled paragraphs (contact) | 720 + 720, padding 170/60/60; left on the strong colour: h 48, labelled paragraphs; right pale | `features` (title + text left, items right); again for `faq`; again for reaching them: left `brand.name`, `place.address`, phone, email, `place.hours`, `contact.routes`, `locations`; right `close.title`, `close.text`, `close.cta`, `place.booking`, `contact.form` |
| 8 | Tile grid again | as 6 | `team` (portrait 4:3 at the top of the tile, name, role, text, phone, email) · `credentials` (t, year, text, link) · `plans` |
| 9 | Rotating half again | as 3 | `quotes` — the words turn beside ONE still photograph of the work |
| 10 | Featured half / rotating on pale | as 5, picture left | `projects` (one → a still half, several → rotating) |
| 11 | Two link tiles (all pages) | section padded 180/60; two tiles 650 × 350, 10 apart, ground 30 % strong, padding 60, h 48, a list of 12 px capital links in two columns (product page) or one arrow link at the bottom. 390: 320 × 197, arrow only | tile 1: `brand.name` + `links[]` (t, h); tile 2: `cta` with the phone number as its arrow line |
| 12 | Foot | charcoal 50,50,51; padding 120/60/25; columns at 60 / 720 / 1050; 12 px capitals +1.2 px, 42 apart; legal line at the bottom | `brand.name`, `foot.text`; rest of `nav`; `place.social` + `foot.links`; `place.notices`; `foot.legal` |

Order on our page: 0 1 2 3 4 5 6 9 7 8-team 8-credentials 10 8-plans 7-faq 7-reach 11 12 (quotes follow the
catalogue so that its picture breaks the type; a second band follows the catalogue only when there are no quotes).
Three or more steps that all have a picture run as the rotating half (part 3's build, on the pale ground, picture left)
instead of three to six alternating halves — chosen to keep the page a working length (coordinator, 2026-11-12: corp1
was 18,876 px). One or two steps keep the alternating halves.
A section whose data is missing is left out whole.

## Measures used
Margin 60 (390: 35). Half text column 500 (padding 60/160/60/60). Serif 48/46 −1 px (390: 30/36). Body 24/36 light −0.2 px
(390: 18/24). Labels, links, names 12 px bold capitals +1.2 px. Half 900 high; rotating half and band 100vh. 390: picture
above (675 high; 600 in the rotating half), words below padded 35 with 600 least height. Tiles 4 × 315 × 435, gap 20,
padding 30. Link tiles 650 × 350, padding 60. Foot as in the table.
Choices I had to make, all toward the reference: long lists (features, faq) are set 18/28 instead of 24/36; tile body
copy 16/24 and rows 14/21 (the reference's tiles hold a drawing, not text); credentials tiles 300 least height.

## Colour — relations kept, the client's palette in
The reference is a near-white ground and ONE strong colour that is both ink on the pale grounds and the ground of the
strong halves with white words; panel and tiles 4 % of it; link tiles 30 % of it; a neutral charcoal foot.
Ours: ground = `palette.ground`; strong = `palette.accent` when it reaches 3:1 on the ground, else `palette.ink`, darkened
until it holds 5.6:1 both on the ground and under white. corp1 → #002a4c (its navy; the accent #929ebe is too pale to
carry words and becomes the link-tile ground instead); local1 → #4c604d (its green, darkened from #647e65).
Foot #323233 as measured (a neutral, not a brand colour); the reference's legal line (141 grey, 4.0:1) is lightened to pass.

## Font stand-ins (open licence, Google Fonts)
Baskerville Display PT Bold → **Libre Baskerville 700**. Avenir Next Thin / Regular / Bold → **Nunito Sans 300 / 400 / 800**.

## Motion measured → reproduced
| Measured on the reference | Ours |
|---|---|
| Header: clear at the top; past the opening it is white with strong-colour words; translateY(−141) while scrolling down, back at 0 on the first move up; .3 s cubic-bezier(.315,.44,.18,1), colour .15 s linear | same values (`.hd.solid`, `.hd.away`); also returns when a link in it takes keyboard focus |
| Halves' pictures drift with scroll: translateY −50 px when the section's top is one screen below, 0 when it reaches the top, +43 when it has left (≈ −0.05 × distance) | same factor, clamped −50…+45. The reference moves the whole picture box and lets a strip of ground show; ours moves an oversized picture inside its half, so no strip shows |
| Rotating half: next slide every ~5 s (changes seen at 2.8 s, 7.8 s), the picture track settles in ~0.9 s decelerating (44 % after 0.1 s, 93 % after 0.35 s); previous button invisible on the first slide; arrows | 5 s interval, picture slides in .9 s cubic-bezier(.2,.75,.2,1), words cross-fade (.3 s out, .45 s in); previous hidden on the first slide; ← → keys; stops while hovered or focused |
| Arrow of a link moves 5 px right on hover, .3 s cubic-bezier(.645,.045,.355,1) | same |
| Tile: ground to white in .2 s linear, outline and arrow appear | same |
| h1 comes down from −50 px on load | .9 s rise from −50 px |
| A 1 px line travels down at the bottom of the opening (keyframes −80 → 0 → +120 px) | 60 px line, 2.4 s loop (the reference's duration was not read) |
Reduced motion: no rotation, no drift, no line, no rise (checked). Without scripts: the header is not fixed, every slide
of a rotating half is laid out one under another with its picture beside it, nothing is hidden (checked).

## What could not be transferred, and why
- The turning 3D wordmark in the pale panel and the line drawings in the product tiles: illustration a small firm cannot
  supply. The panel carries the client's figures (or trust lines) in the reference's type; tiles carry words and rows.
- The film band: used when `media.video` exists; neither test client has one, so a photograph stands there.
- The email sign-up in the foot and the contact form: no form is built; the client's contact links stand there.
- The mega-menu behind "Products" and the search: not built (the header holds links only).
- The reference's section labels ("Featured project") and tile headings ("Connect") are its words; ours come from the
  data (`steps[].k`, `catalogue.title`, `brand.name`, `cta.t`). Credentials, quotes and people's sections have no
  heading when the data gives none.
- The strip of ground above a drifting picture (see motion).

## Owner's rules applied
- No boxed picture beside text: every picture beside words is an edge-to-edge half as tall as its section (kept as
  measured). A panorama (≥ 1.9:1) beside one or two steps runs edge to edge in its own proportion above its words — the
  one conversion. With three or more steps (the rotating half) a panorama would be cropped to a sliver, so the step
  takes another picture: corp1's 2400×709 first-workshop photograph is now unused.
- A step without a fitting picture takes, as second choice, a workshop scene that a catalogue item names (a scene fits
  a story; a machined part beside a story does not).
- Portraits only for their people; each photograph once; nothing wider than 1.3× its pixels; `alt` only as `alt`.
- A picture that a catalogue item names is never set beside another group's or step's words (first build put a
  measuring cone beside the tool room): such a group leaves the rotation and its words stand above its tiles.
- No made pictures, no glow in place of a picture: a missing picture leaves the plain ground.

## Image slots
| Slot | corp1 | local1 |
|---|---|---|
| opening (tinted) | workshop-5axis-operator 1800×1350 | staircase-curved 2400×1606 |
| rotating half (groups) | parts-flanges, parts-on-drawing, inspection-projector (group 4 has no picture → words above its tiles) | — (its one group has no title) |
| band | parts-passivated 1920×1080 | staircase-down 2400×1606 |
| steps (rotating) | workshop-mill-door (1982: its own panorama would be cropped), workshop-lathe-operator (1990: its own picture is Tom Brown's portrait, kept for him), award-2023 | staircase-spiral, kitchen-island, workshop |
| band after the catalogue | — (quotes follow) | — (quotes follow) |
| people | Tom Brown, Gavin, Rowland, Kris; Deneale type only | Adam, Jake, Anthony |
| beside the quotes | inspection-cone | kitchen-painted |
| projects | team-hare-car | staircase-white (Oake House's first picture is the kitchen step's), door-painted, kitchen-timber, bar, oak-frame |
| unused | 11 of 24 | 6 of 20 |
Still without a picture: the pale panel (by design), tiles (type), contact halves, link tiles, foot.

## Long lists are folded (CONTRACT "A long list is folded", and page length)
- On every tile: a plant list (`rows`) shows its first three rows; the rest open in place under "+ n" (native
  `<details>`; four rows or fewer stand whole). Words longer than 140 characters show their first sentence; the rest
  opens in place from it (people, catalogue items, credentials, a group's words). A linked tile is no longer one `<a>`
  (a `<details>` may not sit inside a link): its name is the link, stretched over the tile, and the reference's hover
  (white ground, outline, arrow) is kept with `:has()`.
- The catalogue folds by group — each titled group a `<details>` (title + count, the first open) — past twelve items
  (CONTRACT) and, in this template, already past six when there are two or more titled groups. corp1's 11 items in 4
  groups therefore show Precision Machining open and three ruled rows below it. An untitled catalogue past twelve shows
  twelve tiles and folds the rest under "+ n". `team` over twelve: the same.
- `faq`: every question folds (first open). `features` with more than six described items: the same.
- No script needed: all of it is native `<details>`. legible.mjs skips closed ones.

Heights (1440 / 390): corp1 18,876 / 24,929 → **13,219 / 17,035**; local1 12,218 / 14,791 → **8,910 / 10,590**.
corp1 at 1440: opening 900, told half 1,127, groups 900, band 900, steps 900, catalogue 1,209, quotes 900, ten reasons
999, people 1,311, credentials 776, project 900, contact 1,103, link tiles 828, foot 467. Every part left is a measured
reference part at its measured height; reaching 12,000 would mean dropping one of the full-screen parts (the band or a
rotating half), which the strict wide-picture rule keeps. The reference spreads the same parts over home, about,
product and contact pages (29,793 px together).

## Picture share (tools/coverage.mjs, 1440)
| Page | share | per 900 px screen | screens with a wide picture |
|---|---|---|---|
| reference home | 37 % as read | 100,50,0,49,0,0 | 1 — the third screen is the film band, which did not load in the headless browser (0); with it 56 % |
| reference about | 44 % | 78,50,50,50,49,33,0,0 | 1 |
| reference product page | 65 % | 78,50,50,49,49,49,34,88…92 (tiles of line drawings),65,3,0 | 1 |
| corp1 | 29 % | 100,0,38,88,63,13,21,30,0,26,0,49,2,0,0 | 2 |
| local1 | 38 % | 100,0,84,59,18,42,32,39,0,0 | 2 |
Case 2 of the revised rule applies (corp1 is 2.7× the home page's height, local1 1.8×). (1) Every wide picture of the
reference is in place and in order: opening, rotating half, band, the picture halves (steps as a rotating half, the
featured project as a half). (2) Over the home page's parts — opening, rotating half, band, one half, link tiles, foot —
both clients carry 2,700 px of picture height in about 4,840 (56 %; my sum from the section heights), as the reference
home does once its film band is counted (56 %; 37 % as read). (3) No stretch of type is longer than two screens on
either client: the quotes half follows the catalogue.
