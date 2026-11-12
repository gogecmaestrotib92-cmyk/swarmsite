# recycle — rebuilt from re-cycle.org (a charity), niche: nonprofit

Measured 2026-11-12 at 1440 and 390 with tools/anatomy.mjs, tools/shots.mjs and the probes in `probe/`
(`measure.mjs` type/boxes/backgrounds, `motion.mjs` hover/menu/carousel/reveals, `sub.mjs` parts of four sub-pages).
Raw readings: `ref/measure.json`, `ref/motion.json`, `ref/sub.json`, `ref/anatomy.json`; screenshots `ref/ref-*.jpg`, `ref/sub-*-full.jpg`.
Test clients: `charity1` (primary), `local1`. No `media.made` is read: the picture family is the client's own photography.

## The reference's sections and what each takes
Home page (5893 px at 1440, 8023 px at 390), in order:

| # | reference | measures (1440 / 390) | data |
|---|---|---|---|
| 0 | bar on the accent, phone + e-mail left, social right | 59 high, 15.75/22.5 · 44 high, 14/20, social hidden | `contact.phone`/`place.phone`, e-mail; social = `contact.routes` without a note + `place.social`, as words (the reference's icons are not taken) |
| 1 | header lying over the picture, absolute — it leaves with the page, it is not pinned | pad 36/27/18, nav 15.75/600, two 54-high buttons · logo + three-line button | `brand`, `nav`, `signin` (pale button) + `cta` (accent button). No logo file → the name set in the display face |
| 2 | opening: full-bleed photograph 855 high, veil from the left and from the top, h1 in two colours (white, then accent), lead, button + arrowed link, ragged lower edge 75 px into the next ground | h1 Rubik 81/67.5 upper · 36/32; lead 22.5/31.5 600 · 18/28; text column = half the container | `hero.title` (split in two colours at the first clause break), `hero.text`, `hero.primary`, `hero.secondary`, `hero.note`; one landscape photograph ≥1600 wide |
| 3 | deep ground: four figures with a 2 px accent rule on the left; then kicker, h2, intro, body, one bold line, pale button — beside pictures | pad 135/67.5; figure 54/54, label 13.5 upper; h2 54/54 upper; intro 22.5/36.56; body 18/27 · figures 2×2, 30/36 | `figures`; `hero.kicker` (the reference has its eyebrow here, not in the opening), `statement.title/text`, `hero.text2`, `trust` joined as the bold line, the nav item named "About…" as the button; one photograph |
| 4 | band on the pale tint, a photograph at 10 % behind, centred h2 (not upper), text, button | 414 high, h2 40.5/45, p 18/27 max 900 · 24/32, 14/20 | `close` (title, text, cta) — the appeal; one wide photograph ≥1600 |
| 5 | white: h2 left + button right; article cards on the deep ground — one large (picture above, 684×360) and two beside it (picture in the left third); chips; a row of outlined term links | gap 18; chip 13.5/600 on the accent; card title 33.75 / 22.5; hover: ground → darker .15 s, picture ×1.1 .3 s, chip → tint | `catalogue`: an item with picture, price or text is a card (group name = chip, `price` in the date's place, `note`, `text`, `prices[]` as a ruled table, `rows[]` as a dotted list, `state` as a second chip); a bare name is a term link; `catalogue.note` beside them; the nav item that leads to the catalogue's page is the button |
| 6 | pale tint → accent gradient: centred h2, white cards (icon, h3, text) | cards 432 wide, gap 45, pad 22.5, h3 22.5, p 15.75 | `features` (no icons: the reference's are its own). Left out when every feature is only a name already standing in the catalogue |
| 7 | same ground: quotation carousel, one at a time, 54 px square buttons at the edges | quote 27/40.5 max 909 · 20/32, buttons under | `quotes` |
| 8 | accent ground: kicker, h2, three photograph tiles 450×340 with a veil, title, arrow chip | title 33.75, veil .5 → .7 on hover .3 s, picture ×1.05 | `steps` when every step has a picture of its own; otherwise the deep numbered cards of the volunteering page (285 wide, pad 36, label 13.5 accent, h3 22.5, text 15.75, centred) with `k` as the label |
| 9 | foot on the deep gradient, ragged upper edge; three-line slogan in two colours, link column, contact column, a block with heading, text and a full-width button; social; ruled bottom bar | slogan 54/54, cols 200 / 350 / 495, pad 150 top | `brand.name` in two colours, `nav`, `foot.text`, phone as the block's heading + `contact.form` or the e-mail as the button, social, `foot.legal`, `foot.links` |

Parts taken from the reference's sub-pages for what a client has and the home page has no place for:
- **Questions** (`/faqs/`): h2 40.5 upper, rows 18/27, pad 9, 1 px rule, a plus that turns → `faq` (native `<details>`).
- **Numbered deep cards** (`/support-us/volunteering/`) → `steps` without pictures, and `plans` (name as the label, price in Rubik 40.5, rows, button; the marked plan on the darker ground with accent rules).
- **Deep band with a photograph behind** (`/contact-us/`) → `team` when the people have no portraits: text and names in type over a client photograph under an 80 % veil. With portraits: the picture-topped white cards of `/what-we-do/how-we-do-it/` (444 wide, picture 370 high, pad 27).
- **"Visit our warehouse"** (`/contact-us/`: a boxed map beside labelled lines) → `locations` (or `place`), `contact.routes` with notes, `credentials`, as bold label + text lines.
- **Two-column dotted list** (`/what-we-do/how-we-do-it/`) → `links` not already linked higher on the page.
- **Photograph tiles** again on the pale ground → `projects` (first unused photograph of each).

## Colour: the client's palette in the reference's relations
The reference is deep teal `#193838` / darker `#051a1a` (grounds), lime `#c8df0a` (accent ground with dark ink), pale teal `#96cdcf`
(second button, band, chips' hover), white page, ink `#343434`. In `_colours()`:
deep ground = the client's ink (pushed down until luminance ≤ .05); darker = half-way to black; accent = `palette.accent`, moved the least
needed for its own text (white or deep, whichever stands better) to hold 4.6:1; accent as ink on the deep ground = accent lightened to 5.2:1;
pale tint = accent at 42 % over white; page = `palette.ground`.
Where the accent is dark (charity1's blue, local1's sage) the text on it is white, and the tint→accent gradient is held to the cards'
block with the tint kept for its first 30 % so the heading stays on the pale part; the quotations then stand on the plain accent.
With a light accent (lime-like) the gradient and dark ink are as the reference has them.

## Fonts
The reference sets Rubik (display, heavy) and DM Sans (text) — both are open-licence Google Fonts, so they are used as they are:
Rubik 800 (the reference loads the 800 face and computes 700), DM Sans 400/500/600/700. No stand-in was needed.

## Motion — measured, and what is reproduced
Measured: nothing is pinned (header `position:absolute`, sampled at six scroll positions); no scroll-linked movement (wide pictures sampled
at six positions: transform none); no reveal-on-scroll (nothing below the fold starts at opacity 0 or transformed); figures do not count up
(sampled 8× over 2 s). Transitions: buttons `all .15s cubic-bezier(.4,0,.2,1)`; article card ground `.15s`, its picture scale 1.1 `.3s`,
its chip accent → tint, its title underlined; tiles: veil .5 → .7 and picture 1.05 over `.3s`; term links fill with the tint (no transition);
carousel: Swiper, slide, 300 ms, loop, no autoplay, one per view, 20 px between; phone menu: panel slides in from the right
`transform .3s cubic-bezier(.4,0,.2,1)`, overlay to opacity .8 over `.3s`; FAQ plus `.15s`, answer `.3s`.
Reproduced: all of the above as CSS, with the same durations and curve. The carousel is a scroll-snap row driven by two buttons
(smooth scroll, wraps round; swipes on touch; works as a plain scrolling row without script).
Not reproduced / differs: the FAQ answer opens at once (native `<details>`; the reference animates height over .3 s). The arrow after a text
link moves 4 px on hover — the reference has a .15 s transform transition on that icon but the probe did not capture the distance, so 4 px is
an assumption. A press state (1 px down) and the 2 px edge on hover of filled buttons are mine: the probe read no change on the reference's
filled buttons on hover.
`prefers-reduced-motion`: every transition off (checked: durations read 0 s).

## Owner's rules applied over the reference
- **Boxed pictures beside text converted.** Section 3 of the reference floats two overlapping, shadowed pictures beside the text. Here the
  statement stands beside ONE photograph that runs from the middle of the page to its right edge and from the top of the block to the foot
  of the section (edge to edge, as tall as its block). On the phone it is a full-width band above the text, as the reference stacks them.
  The contact page's boxed map beside the address is likewise an edge-to-edge half (left) with the address column beside it.
- The opening photograph, the band backdrop and the team band are full-bleed as measured. Pictures inside cards and tiles fill their card.
- No drawn strokes. The ragged edge under the opening and above the foot is the reference's own section edge (a 1596×75 mask); the shape
  here is generated from a fixed number sequence in `_torn()`, not the reference's texture file. If the owner reads it as decoration, it
  is one mask rule on `.hero` and one on `.ft`.
- No icons (the reference's are its own), no invented labels: the foot's "Navigation"/"Contact us" column headings and the cards'
  "Read more" are left out because the client's data holds no such words; a card keeps the arrow only (the whole card is the link, named
  by its title). Buttons are `text-transform:capitalize` as the reference's.
- `alt` is only ever an `alt`.

## Image slots (client photographs; chosen by role, size and proportion; each once)
| slot | rule | charity1 | local1 |
|---|---|---|---|
| opening | ≥1600 wide, landscape, not `people`/`portrait`, not `small` | highland-calf | staircase-curved |
| statement half (720 × block) | ≥1000×760; an upright first, then workshop/exterior/room/people/landscape | lamb-grass (upright) | workshop |
| band backdrop at 10 % | ≥1600 wide; landscape/exterior first, then a panorama | field-panorama | kitchen-painted (1900×944) |
| catalogue cards | the item's own `img` (large card ≥600 wide, row card ≥220) | 10 items | 2 items |
| step tiles | each step's own `img`, only if all have one and none is already a catalogue picture | — (numbered cards) | — (its step pictures are its catalogue pictures; numbered cards) |
| project tiles | first unused photograph of the project, ≥440 wide | — | 5 |
| people | the person's own `img`, ≥400 wide | — (type over the band) | 3 |
| team band backdrop | ≥1600 wide; `people` first | volunteers-dinner | — |
| where-and-how half | ≥1000×760; exterior/landscape/room/workshop first | sheep-portrait | staircase-down |
Pictures the data assigns to a named thing are held back from the free slots. A slot with no fitting photograph renders without one:
the opening becomes the deep ground with the ragged edge (the reference's own sub-page header), halves become full-width text, the band
a plain tint, tiles become numbered cards, cards lose their picture part.

## Picture share (tools/coverage.mjs)
reference 36 % — per screen [96,26,64,10,13,26,0], 2 screens with a wide picture (opening, band).
charity1 35 % — [100,40,73,46,28,13,0,20,34,44,0,0], 2 wide (opening, band, same order). The page is 1.74× the reference's height
(it carries the catalogue, questions, places and further pages), so the revised rule's case (2) applies; the overall figure is within one point anyway.
local1 46 % — [100,54,75,6,17,71,41,19,0], 2 wide.
Long type sections: between the volunteering cards and the questions stands the team band (photograph), after the questions the
where-and-how half (photograph); no run of type longer than two screens on either client.

## What could not be transferred
- The reference's logo, pictogram icons (cards, social, quote mark, bar), regulator badge: not taken; words or nothing in their place.
- Dropdown navigation: the contract's `nav` is flat.
- The newsletter block: no form in a template; its place takes the phone number and a button to the client's own contact page or e-mail.
- The quotation's portrait: `quotes` carry no picture.
- Article dates and "Read more": the catalogue has prices and no dates; the price stands where the date stood.

## Checks
See `needs.json` → `measured_on` for the shots / legible / coverage lines and the variants.
