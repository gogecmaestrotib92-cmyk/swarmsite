# sunbeam — template for places, rebuilt from sunbeambagels.com

Measured 2026-11-12 at 1440×900 and 390×844: `ref/anatomy.json`, `ref/tree-1440.txt`, `ref/tree-390.txt` (boxes and
computed styles of every visible element), `ref/motion.txt` (sampled over scroll, over time, on hover; made by
`ref/motion.mjs`), `ref/coverage.txt`, screenshots `ref/ref-*.jpg`, the coffee sub-page `ref/sub-coffee.jpg`.
Test clients: `butarque` (52 photographs: four large, 45 dish squares of 600px) and `balamo` (20, none 1600 wide, 15
small) — first built on 2026-11-12 with five and none; the readings for that state are kept under "With few or no
photographs". *Measured* = a reading from those files;
*choice* = mine, and said so.

## What the reference is
The home page of a bagel shop and café: cream ground, black text, one red, an orange→red gradient for its two big
bands, a pale lilac as third colour. A fat soft serif for display, a mono for everything else, a narrow bold sans for
card headings, one script line. It is dense and practical: hours and town in the top bar, one button to the ordering
page, address and hours in two dashed cards at the foot, a pill of links fixed at the foot of the window.
Its pictures are of three kinds:
1. **ordinary photographs** — the room film behind the opening, three category pictures, a moving strip of six, a
   loose pile of nineteen from its Instagram;
2. **cut-outs** — a wheel of four cut-out products under the changing heading, a cut-out cup set into a letter;
3. **3D objects on a canvas** — bagels that fall through the page when asked to ("drop a bagel"), a sticker that
   starts them, a sound switch.
This template is the build that kind 1 can fill. Kinds 2 and 3 are not carried over and nothing stands in for them as a
fake (see "Depends on cut-outs").

## Sections (reference → data)
| # | reference (1440) | what it takes here |
|---|---|---|
| 1 opening, 100vh | room film full-bleed under a black veil at .67 · top bar at 50px, sides 90px: hours left (14px), wordmark 250×58 between two 173px dashed rules, a line naming the town right · h1 8vw/1 on the third grid column (131px) · a button with a 4px gradient ring (radius 14, pad 25×40, 18px) beside the last line · an underlined text link bottom-left (30px, 55px from the foot) · a sound switch bottom-right | backdrop = chosen (see "How photographs are chosen") · left = first `place.hours` line, else `place.phone.t` · wordmark = `brand.name` (with `brand.logo` only when there is no photograph: a mark of unknown tone is not laid on a picture) · right = `hero.text2` when short, else `place.address` city, region · h1 = `hero.title` · button = the menu (`place.menu.h`, labelled with the shortest label in the data that points at it), else the booking · text link = `place.booking` (else `place.takeaway`) · no sound switch |
| 2 what is served, 1000px | script line 60px tilted −2° in the red · h2 8vw/1 centred, four ingredient lists that change every 2 s · below, a 1251px wheel of four cut-outs turning a quarter with each change (587px of it showing) | script = `statement.title` (else `hero.kicker`) · h2 = names of `place.menu.sections` set as short sentences in groups of about 36 letters (else `place.cuisine`, else `trust`), changing every 2 s · a centred paragraph = `hero.text` (taken from the reference's coffee page, which has one in this place) · **the wheel becomes a full-width band, 40.8vw high, of one landscape photograph at least as wide as the page** |
| 3a band: three columns | gradient band, 15vw of air top and foot · h2 8vw (820px wide) · a faint round stamp of arched text top right · three columns (gap 20): photograph 379×400 radius 15 over a dashed card (1px, radius 15, pad 80×55, third colour multiplied at .25) with h3 26/30 narrow bold upper case + 15/27 text | h2 = `steps.title`, line = `steps.text` · columns = `place.spaces` (title, text, own picture), else `steps.items` (title, `k` as text, title linked to its `cta`, and a picture from the page it links to) · stamp = `brand.name` / `place.since` / city, region on three arcs, at .14 |
| 3b moving strip | 200px below; twelve frames in a row (six pictures twice), 350×300 and tilted 245×312, radius 10, gap 40, one run of 1960px in 34.8 s | four to eight photographs, dishes first, no dish twice; upright ones take the narrow tilted frame |
| 3c — (the reference orders on another site; its three columns ARE its menu categories, each a photograph over a dashed card) | — | **the menu**, in that same column: h2 = the menu's label · a section whose own page carries a dish picture (`photo.page` = `section.h`) is a column: picture over a card with the name and the `count` · sections without a picture are short dashed cards (name + count) · a section with priced `items`: its name as a heading, then one column per dish that has a picture (name, price · note), the rest as name ⋯ price rows on dashed leaders · `place.menu.lists` as one card of name ⋯ count rows · a button to `place.menu.h` · `faq`, when a client has one, follows as one dashed card per question |
| 3d rows | 200px below, on a narrower measure (196–1243): three rows, each h2 6vw/1, 51px, text 15/27 up to 700px left and a button right (radius 10, pad 15×30, 16px + arrow), 31px, a 2px dashed rule · hand-drawn icons at the row ends · a picture that follows the pointer | **three rows, as the reference**: the first `place.events` (what / when · price · where / its `cta`), `links` (title / `d` / an arrow-only button, because the data has no label for it), and `close` last (title / text / its `cta`) · no icons, no pointer picture |
| 4 the pile, 900px | cream; nineteen pictures laid loose (radius 20, ±5°), each draggable; a link to the Instagram in the middle | six to fifteen of the photographs still unused, the largest in the largest frames; the link is `place.social[0]`; **its ground is the page ground tinted 14 % toward the band** (the reference's is cream; on a pure white ground white-backed dish pictures lost their edges) |
| 5 foot | gradient band · the name at 21vw, one line · two dashed cards 320×288 (2px, radius 15, pad 50) at the right: "directions" (address, phone) and "hours" + round social buttons · 185px · a last line: © left, two links and a round to-top button right | name = `brand.name`, broken into the lines that give the largest size (not above 21vw, block not above 24vw) · card 1: city as heading, street, postcode region, phone, e-mail · card 2: each `place.hours` entry (days as heading, open – close), `place.social` as text links · last line = `foot.legal` (else `foot.text`), `foot.links`, to-top · then `place.notices` |
| pill | fixed at the foot of the window, centred: 737×66, radius 10, pad 20×60, gradient 102° red → orange → lilac, links 18px gap 20 with a 3px underline on hover | `nav` (+ `cta` when not already in it) |

Not used: `figures`, `quotes`, `logos`, `features.items`, `hero.note`, `statement.text`, `hero.kicker` when the
statement gives the script line, `place.price_range` — the reference has no place for them.
The card headings "Directions / Hours / Follow us" are the reference's words and are not in the data, so the cards
carry the city and the days as their headings instead.

## Measures used
grid 22 columns, content from 9.09vw to 90.9vw (phone 20px) · rows on 13.61vw · h1 and band h2 8vw (phone 16.67vw and
11.54vw) · changing h2 8vw (phone 13vw) · row h2 6vw (phone 10.26vw) · name at the foot 21vw (phone 18vw) · all display
line-height 1 · text 15/27 mono 500 · top bar 14/21 · pill links 18 · card h3 26/30, foot card h3 22 · radii 15 (cards,
pictures), 10 (buttons, pill, strip), 14 (opening button), 20 (pile) · dashed 1px on band cards, 2px on foot cards and
row rules · band padding 15vw · 200px between the band's blocks (phone 80 / 50) · phone: picture 350×275, card pad
50×35, foot cards pad 30, stacked.
**Sizing from the words (choice, needed because Spanish names are longer than "Coffee. Breakfast. Lunch.").** Caprasimo's
advance widths were measured once and are in `render.py`. A display line never exceeds the reference's size; it is
reduced until its longest word fits the measure, and a title longer than the reference's steps down by the square root
of the excess so that it keeps about the reference's number of lines (butarque h1: 6.2vw instead of 8vw).
**Columns (choice).** No picture is enlarged: the picture boxes of one row of columns take the reference's 400px, or the
height of the lowest picture among them (butarque's rooms: 315px, because two of its room pictures are 418×315). Columns
go three to a row; a last row of two shares the width and four go two and two, so no row ends in a hole.

## How photographs are chosen (each picture once; `render.py`, "photographs")
1. A room keeps the picture the data gives it (`place.spaces[].img`).
2. **Opening**: among pictures that are not small, `room`/`exterior` first (then `bar`, then `people`/`other`), the one
   that covers 1440×900 with the least enlarging, the largest of those; never enlarged more than a quarter.
3. **Band** (1440×587): a landscape picture at least 1398px wide, a `dish` first, then `people`, `other`, `bar`; a dish
   down to 1100px only when nothing wider exists.
4. **Rooms without a picture, menu sections**: a picture whose `page` is the address the item links to.
5. **Priced dishes**: a picture whose file name matches the dish's own address (one contains the other, six letters at
   least). This is a match on names, not a link in the data; the data has no `img` on menu items.
6. **Strip**: up to eight, dishes first, short side 300px or more, never two views of one dish (`arroz.jpg`,
   `arroz-2.jpg`).
7. **Pile**: up to fifteen of the rest, a second view of a dish only after every dish has been seen once, the largest
   picture in the largest frame.
A small picture is never a backdrop and its box never exceeds its own pixels. An `alt` is only ever an `alt`.

## Typefaces (all Google Fonts, open licence)
| reference | here | why |
|---|---|---|
| Belgard (commercial; fat soft serif with flared strokes) | **Caprasimo** | the same kind: one heavy weight, soft bracketed serifs, tight fit. It is rounder and less flared than Belgard |
| Forma DJR Mono 500 (commercial) | **DM Mono 500** | geometric mono of the same weight and width |
| Archivo Narrow 700 | **Archivo Narrow 700** | the reference's own, open licence |
| Tilda Petite (commercial script) | **Yesteryear** | upright-leaning brush script with flourished capitals; heavier than Tilda |

## Colour
Relations kept: ground · ink · one accent · a band that runs from a lighter neighbour hue at the top to the accent at
the foot (reference: hsl 28° → 3°, 7 points lighter at the top; here the accent is the foot and the top is the accent
25° further round and 7 points lighter) · a third colour (first chromatic `palette.extra`, else the band's top mixed
half-way to the ground) used in the pill's and the button ring's gradient and, multiplied at .25, as the cards' ground.
Departures, all forced by the 4.5:1 rule (the reference's own white 15px text on its orange measures about 2:1):
- text, rules and dashed borders on the bands are white only when white reads on every band colour; for both test
  clients (two light greens) they are the ink, darkened until it reads on the tinted cards too;
- the same for the pill; the script line and the solid buttons take the accent darkened along its own hue
  (butarque `#83b735` → about `#597c24`);
- with no photograph the opening is the band gradient (as on the reference's sub-pages) with band-coloured text.
Seen on the outputs: butarque's third colour is its orange, which multiplied over green makes the cards an olive; that
is the measured relation applied to this palette, not a chosen colour.

## Motion
Measured (`ref/motion.txt`):
- the changing heading: a timer, every 2.0 s; headings cross-fade in .2 s; the wheel turns 90° in .5 s ease-in-out; one
  cut-out spins continuously (3 s linear);
- the pill: `bottom` 0 at the top of the page, 30px (phone 60px) once scrolled, 0 again when the foot arrives; .2 s ease;
- entrances, once, as each thing comes into view: band h2 rises its own height (115px) and fades in; each column rises
  half its height; row headings half theirs; the name at the foot and the foot cards their whole height; the stamp
  slides up 164px; the cut-out cup shrinks into its letter (width, 1 s);
- the strip: 1960px in 34.8 s linear at 1440 (the same run in 69.2 s on the phone);
- hover: buttons swap their ground for a 45° six-stop gradient with a light border (.3 s), the opening button's ring
  fades (.2 s); pill links get a 3px underline; address and phone a 2px underline; a category picture swaps to a short
  film (.2 s); a picture follows the pointer over the rows; pile pictures can be dragged;
- phone: the pill is one button; it opens a full-screen gradient sheet with the links at 36px (.4 s);
- bagels fall through a fixed canvas on request (physics), with sound.
Reproduced: the 2 s change with the .2 s cross-fade; the pill's lift and return; all the entrances with their measured distances (about .7 s, eased out — the
duration is read off samples 260 ms apart, not from the source); the strip at the measured speed at both widths; the
hover states of buttons, pill links and address lines; dragging in the pile; the phone sheet (.4 s); a press state
(scale .97) on both buttons, which the reference lacks.
Not reproduced: the wheel and the spinning cut-out, the cup, the film on hover, the pointer picture, the falling
bagels and their sound — each needs a cut-out, a film or a 3D object the clients do not have.
Without scripts everything is visible and the first heading group stands (hidden states exist only under `html.js`);
with `prefers-reduced-motion` the script stops before setting it and all transitions and the strip are off. The phone
menu is a `<details>`, so it opens without scripts.

## Phone build (390), measured and kept
top bar stacked: name between two short rules, hours under it, the town line moved under the h1 · h1 16.67vw · no
button in the opening (the reference hides it; the text link stays bottom-left) · script 40px, heading 13vw, dish band
57.7vw high · band h2 11.54vw, stamp 210px, columns stacked (picture 275 high over its card) · rows stacked with the
button under the text · foot name 18vw, cards full width, last line reversed and centred · pill = one button, lifts
60px. Changed: the reference prints the word "Menu" beside the three bars; the word is not in the data, so the button
shows the bars only and carries the word as its spoken label (the one string the template adds, by language).
The row of links in the pill is also replaced by the button at any width where the client's links would not fit
(butarque: under 1125px).

## Depends on cut-outs or 3D — not transferred, nothing faked
- **the wheel of cut-out products** (section 2): replaced by an ordinary dish photograph as a full-width band. With a
  client's cut-outs the wheel could be built; with ordinary photographs it cannot — a rectangle turning by quarters is
  not the same thing.
- **the cut-out cup inside a letter** of the band heading.
- **the falling bagels** (canvas, physics, sound), the sticker that starts them and the sound switch. With them goes
  the reference's 500px of empty foot on the phone, which exists for the bagels to land in.
Also not transferred:
- hand-drawn icons at the row ends and beside the bottom-left link (drawn strokes; owner's rule) and the sun mark
  beside the hours (its own mark);
- social icons (brand marks) — the networks are text links;
- the films (opening film, hover films): the clients have none; the opening takes a photograph;
- the pictures that follow the pointer over the rows (they would need three more pictures a client rarely has);
- the cookie notice.

## Image slots — what each took (2026-11-12, `python3 -I ref/slots.py <client>`)
| slot | butarque (37 of 52 placed) | balamo (20 of 20 placed) |
|---|---|---|
| opening | terraza-mesas-altas 1800×2400 (exterior) | gran-reserva-pasillo 1242×1152 (room; shown 1.16× under the veil) |
| band | gintonic 1900×800 (people) | maridaje-copa 1437×810 (other) |
| rooms | terraza (418×315), salon-1900, chill-out (418×315) — from the data | gran-reserva-barrica, mostrador-marisco, gran-reserva-reservado — by the page each room links to |
| menu sections | risotto-de-boletus, hamburguesa-butarque, surtido-de-ahumados, calamar-de-potera (Arroces, Carnes a la brasa, Del mar, Pescados); De la huerta and De la tierra have no picture | no menu block |
| priced dishes | postre-ferrero-rocher-gold, postre-el-aguacate, postre-el-huevo, postre-brownie, postre-tarta-de-queso | — |
| strip (8) | salmon, arroz-bogavante, arroz-carabineros-2, arroz-senorito-2, chuletitas-de-lechal, presa-iberica, secreto-iberico, entrecot | pulpo, pulpo-perejil, zamburinas, sala-principal, salon-jardin-vertical, bodega-botellero, alta-mar, arrecife-copas |
| pile | 15: barra-2400, solomillo-de-ternera, tbone, sardina-ahumada, anchoas-del-cantabrico, gamba-plancha, pata-de-pulpo-2, zamburinas-plancha, zamburinas-gratinadas, tartar-de-salmon, then second views: postre-el-aguacate-2, postre-tarta-de-queso-2, risotto-de-boletus-2, arroz-bogavante-2, arroz-carabineros | 7: maridaje-copa-2, terraza, reservado-magallanes-mesa, sala-de-fiestas, arrecife, reservado-magallanes, sala-de-fiestas-mesas |
No photograph is used twice. `media.made` is not read. Seen in the pairs: butarque's strip is all squares, so it has
none of the reference's narrow tilted frames; its pile is white-backed dish pictures, which read flatter than the
reference's snapshots; balamo's pile of seven leaves the middle of the screen open.

## Picture share (1440)
| | `tools/coverage.mjs` | per screen |
|---|---|---|
| reference | 49 % | 100 / 53 / 85 / 28 / 21 / 35 / 53 / 7 |
| reference, cut-outs counted only where seen (`ref/coverage-clipped.mjs`) | 42 % | 100 / 46 / 46 / 27 / 20 / 36 / 49 / 7 |
| butarque | 39 % | 100 / 44 / 26 / 40 / 49 / 48 / 39 / 39 / 0 / 28 / 48 / 0 |
| balamo | 36 % | 100 / 42 / 32 / 44 / 23 / 20 / 34 / 2 / 17 |
**By the tool as it stands neither client is within 5 points of the reference (10 and 13 under).** Seven of the
reference's 49 points are the bounding boxes of its rotated cut-outs reaching out of their section, where nothing is
seen; `ref/coverage-clipped.mjs` is the same tool with boxes clipped to ancestors that hide overflow, and by it butarque
is 3 under and balamo 6 under. Where the reference still has picture and ours has ground:
- its third screen (85 → 46 clipped): the wheel and the category pictures stand close together; ours has the band's
  15vw of air and a three-line heading there (26–32);
- the screens of the menu lists and the three rows (butarque's ninth: 0) — type the reference does not carry;
- the foot (ours 0–17, the reference 7).
What was closed in the build after the photographs arrived: menu sections and priced dishes became picture columns
(two screens that were plain green), the strip and the pile appear, rows were cut from five to the reference's three,
a last row of columns no longer ends in a hole. 25 % → 39 % for butarque, 1 % → 36 % for balamo.

## With few or no photographs (the first data, 2026-11-12, rendered and looked at)
- butarque with five: opening, band, three room pictures; no strip, no pile, no menu pictures; 25 %; it held, but was a
  green page below the third screen.
- balamo with none: nothing broke and every line was legible, but it was gradient and type from top to bottom (1 %),
  with no menu block. Not a page to offer.
**Minimum to offer this template (`needs.json`): fifteen ordinary photographs** — one of the room or outside, not small,
at least 1152×720, for the opening; one landscape at least 1400px wide for the band; one per room shown (three); four
for the strip; six for the pile. Dish squares of 600px are enough for every card, strip and pile frame. Under fifteen
the pile goes first, then the strip. Cut-outs are not required and would not be used.

## Data remarks met while building
- `balamo.place.phone.h` is null, so the phone is text, not a link; its `note` ("no tel: link in the capture") is a
  remark about the capture and is never shown (the template shows no phone note at all).
- `balamo.brand.logo` is a black mark on an opaque white square. It is shown only when the opening has no photograph
  (multiplied onto the gradient); now that balamo has photographs the opening shows the name alone.
- menu `count` is a bare number in the data ("5"); the template shows it bare, right of the name, with no word added.


## Engine import fixes (2026-11-12, stress: plans 1/3/5, features 2/9, steps 1/6, 12-word h1, 40-char button, no faq, no photographs; clients casaolmo and larchwick; 1440 and 390)
- A gradient that carries text has one ink for all of it. When neither white nor the dark ink reads on every stop (casaolmo: a mid-tone orange whose lighter neighbour is too light for white and whose foot is too dark for the ink; larchwick: the pill runs from a dark green to a light sand third colour), the stops are now moved together along their own hues, toward black under white text or toward white under the dark ink, whichever is the shorter way, until one ink reads 4.6:1 on all of them. Bands, foot and the plain opening use the held band stops; the pill and the buttons' hover grounds use the held pill stops; the decorative ring keeps the true colours. Before, the template fell back to plain black or white and printed 2.3:1.
- The card ground was modelled as a multiply, but the card is an isolated group, so the .25 layer draws as a plain mix. The contrast is now computed against what is drawn: the stop mixed a quarter toward the third colour (larchwick read 4.43:1 before).
- `plans` added to needs.json drops (the reference has no tiers).
