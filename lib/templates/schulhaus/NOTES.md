# schulhaus — a type-led template for places

Reference: https://schulhaus.tirol (a restaurant with rooms). Measured 2026-11-12 at 1440×900 and 390×844: the home page,
and for the parts the home page does not have, its rooms page (/schlafen/), food page (/essen-trinken/) and contact page
(/kontakt/). Measurements: `ref/anatomy.json`, `ref/measure.json`, `probe/sub-*.txt`, `probe/rules.txt`.

**Cookie panel.** It has no decline button ("Ausgewählte akzeptieren", "Alle akzeptieren", "Individuelle
Datenschutzeinstellungen"). Nothing was accepted: for every screenshot and measurement the panel's elements
(`#BorlabsCookieBox`, `#BorlabsCookieWidget`) were set to `display:none` in the page. `ref/anatomy-*.jpg` (made by
`tools/anatomy.mjs`, which cannot hide it) still show the panel; all `ref/ref-*`, `ref/sub-*` and the pairs do not.
The opening-hours pop-up was closed with its own "Schließen" (`ref/ref-*-popup.jpg` show it open).

**The test data changed while this was built.** The brief said butarque has five photographs and balamo none; at 11:01 both
were recaptured (butarque 52, balamo 20). The delivered pages use the new data. The no-photograph case and the
five-photograph case are kept as scratch builds in `probe/v/` (`balamo-nopics`, `butarque-nopics`, `butarque-five`).

## Sections of the reference and the data each takes
| # | Reference (where measured) | Ours takes | butarque | balamo |
|---|---|---|---|---|
| 1 | First screen (home): five-column grid, 12 gap, 30 margin. Two short lines top left, the house name as a wide mark at the foot of columns 1–2, a 3:4 picture tile with a typewriter caption in column 3, a paragraph in column 4, a tile in column 5; second row five tiles | lines = `hero.kicker`, `hero.title`; mark = `brand.name` (the h1); paragraph = `hero.text`, `hero.text2`; tiles = `links[]` (first two in row 1, the rest in row 2) | 3 picture tiles, 2 text tiles | 5 picture tiles |
| 2 | Two paragraphs at 26 px across the full width (home) | `statement.title`, `statement.text` | yes | yes |
| 3 | Left: a short line at the top, a small 3:4 picture (325×434) at 30 % of the column, a line and the round house stamp at the foot, stamp on the page's centre; right: a picture 596×900 to the window's edge (home) | lines = `steps.title`, `steps.text`; small = a dish; tall = an upright photograph of the place; stamp = `brand.logo`, else name + `place.since` + city | bar tall, dessert small, typeset stamp | wine glass tall, octopus small, logo |
| 4 | Left: picture 596×900 from the window's edge; touching it a small picture 271×362, a 20 px sentence beside its foot, an arrowed link under it (home). Lists set as the reference sets "what a guest should know" on its rooms page: 12 px typewriter label, 14 px lines each led by an arrow | sentence = `place.cuisine` joined; links = `place.menu.h` (label from `nav`/`links` with that address), `place.takeaway`; lists = `place.menu.sections` (name, count; a part with `items` becomes its own list with prices; a note shared by all items is set once under the list), `place.menu.lists` | salmon tall (3:4), dessert small, 3 lists | corridor tall, scallops small, sentence + 2 links |
| 4b | The food page's grid of five 266-wide picture cards with a label | one card per menu part that has a dish photographed on its own page (`page` on the photograph = the part's address); caption = the part's name | 4 cards | none (no menu parts) |
| 5 | The rooms page's three columns (414 wide, indented 114): 12 px paragraph, arrowed name under it on one line for all three, picture 414×552 | `place.spaces[]` text, title, img | 3 rooms, frame 4:3 because two pictures are small | left out (no spaces) |
| 6 | Left a 26 px paragraph (403), a picture 549×900 in the middle, right two small pictures 242×323 with an arrowed link between (home) | `close.title`, `close.text`, `close.cta`; pictures from what is left | square dish in the middle, two desserts | room 3:4, two rooms |
| 7 | Questions and prices — the reference has neither; built from its parts (list label + short paragraphs; the rooms columns with the price at 41 px) | `faq`, `plans` | none | none |
| 8 | The contact page: 20 px sentences left; right-aligned at 41 px the hours, telephone and mail (underlined), the address at 20 px, an arrowed link; the booking where the form stands | left = `place.events[]` (when / what / price / where, its link), `hero.note`; right = `place.hours`, `place.phone`, `place.email`, `place.address`, `place.social`; booking = `place.booking` | hours, phone, mail, address, booking | event, phone, address, socials, booking |
| 9 | (none in the reference) legal notices and small print at the foot | `place.notices[]` (picture at most 271 wide, paragraphs at 14 px), `foot.text`, `foot.legal` | small print | FEDER notice |
| nav | One line fixed to the foot of the window, 49 high, on the page's ground: secondary links left, primary right, divided by commas. Phone: an 80 px ground strip at the top, a bordered button top right, a full-height panel | left = `foot.links` + `place.social`; right = `nav` + `cta`; panel = the same, the stamp, the secondary row | yes | yes |

Not placed (listed under `drops` in needs.json): `trust`, `figures`, `features`, `hero.primary/secondary`, `quotes`, `logos`,
screens/phones/video, `place.price_range`, `steps.items`.

## Measures used (1440 → 390)
- Grid: 5 columns, 12 gap, 30 margin → 2 columns of 137 with 68 between, 24 margin. Tile 266×355 (3:4), caption 18 under it → 137×182, caption 10 under.
- Vertical: page starts at 26; row 1 → row 2: 48; tiles → statement: 121; statement → block 3: 56; between the blocks: 64; foot padding 48 + bar 49. Phone: 80 top strip, blocks 32 apart.
- Type: sentences 20/25, +0.32 px (phone 20/28.4, +0.48); large paragraphs 26/31.2 (phone 26/32.5); contact 41/50 (phone 41/49.2); captions typewriter 14/19.9 +0.48 (phone 12/17); links, labels, bar typewriter 12/17 +0.48 (bar 10/17 between 1024 and 1279); lists 14/19.9; room paragraphs 12/17.
- The mark: 534 wide × 82 high at 1440 for a 15-letter name, i.e. the two columns → 236 wide on a phone. Ours: size = min(6.97 vw, 37.08 vw ÷ the longest line's width in em) → min(11.37 vw, 87.7 vw ÷ …) on a phone; a name wider than the two columns at four fifths of that size is set in two balanced lines. Line widths are estimated per letter in Python and were checked in the browser (Restaurante 3.94 em, Butarque In&Out 5.72 em, Bálamo 2.55 em; the estimate runs 2–5 % over, so a line does not overflow; `white-space:nowrap` holds the two lines).
- Tall frames 596×900 (41.39 vw, held as a proportion), small 325×434 and 271×362, rooms 414×552, closing 549×900 and 242×323. Phone: 298×397 flush to one edge, 205×274 centred, 342×456, two of 137×182.
- Stamp 167×101 on the page's centre → 137×78 centred.
- Bordered things: 1 px ink, no radius (the phone button 55×30; the booking link takes the form field's 36 px height).
- Colour is a relation, not the reference's orange: its page is the brand colour edge to edge with black type (8.3:1). Ours: ground = `palette.accent`, ink = `palette.ink` if it reads 7:1 on it, else black or white; an accent on which neither reaches 7:1 is moved toward the far pole until it does. butarque #83b735 with black 8.8:1; balamo #61a229 → #67a632 with black 7.1:1.

## Typefaces (all open licence, Google Fonts)
- Office Times Sharp (commercial, a sharpened Times) → **Tinos** (Apache 2.0, Times metrics).
- Office Times Sharp Mono (commercial, a typewriter cut of it) → **Courier Prime** (OFL).
- The house mark (a drawn logotype: narrow, high-contrast display serif) → the client's name in **Instrument Serif** (OFL). It is lighter and wider than the reference's mark: at the same width the capitals are 72 px high where the reference's are 82.
- A script face on the sub-pages' vertical titles ("elva Script") — not used; those titles are not rebuilt.

## Motion: measured → reproduced
- The page itself does not move: no reveal, no parallax (60 elements sampled at 6 scroll positions kept their place). → none.
- The bar is fixed to the foot of the window on its own ground; an entry gets a 1 px underline, opacity 0 → 1 in .3 s. → same (also on keyboard focus).
- Arrowed links: the arrow moves 4 px right, .3 s ease-out. → same.
- Food-page cards: the picture swings open like a door (rotateY −90° about its left edge, .7 s, perspective 2800) and shows the card's text face — label at the top, sentence at the foot, on the page ground. → same, on a first-screen tile that has both a picture and a sentence; pointer devices from 1024 only. On a phone the reference opens the card on tap; ours does not, because our tiles are links.
- Phone panel: height 0 → 100 vh and padding 0 → 80/40 in .7 s cubic-bezier(.4,0,.2,1). → same; Escape and choosing a link close it.
- **Measured, not reproduced — the pinned mark.** From 275 px of scroll the mark stays fixed 30 px from the top for the rest of the page, above text and pictures alike, so paragraphs and photographs pass under black letters. The owner's readability rule overrides it (a header standing over content was already recorded as a defect on another template): our mark stays in the first screen.
- **Measured, not reproduced — the pop-up.** A notice opens on load (fade-in .5 s ease-in-out over a 50 % black backdrop, closes with the same fade). A veil over the whole page on arrival would also hide the page from the gates; the event stands in the contact block instead.
- Reduced motion: every transition is off; the door does not open (the tile's caption still names it). Without scripts: everything is visible; on a phone the navigation stands open at the top of the page instead of behind the button.

## Where it leaves the reference, and why
- No booking form: the data has an address for booking, not an endpoint, and the field labels would be invented words. The booking is an arrowed link in a 1 px box of the field's height.
- "Menu" / "Menu schliessen" on the phone button are words the data does not have: the button shows two lines that cross when open. Its accessible name comes from a fixed word list by `lang`.
- The stamp is the client's logo when it has one (blended into the ground so a white logo field does not show as a box; on balamo a very faint edge is still visible in the phone panel), else name, year and town set in the page's faces — not an arched drawing.
- Tile without a picture → the reference's own text face of a card (food page), not an empty frame. A tile with neither picture nor sentence takes an unused picture of the place, else it is left out and stays in the bar.
- Menu rows carry a count or a price at the right of the line; the reference has no priced list anywhere (its menu is a download).
- The reference changes ground per page (orange, pale blue, pale grey). One page → one ground.
- Text never stands on a picture here (the reference's card labels do); captions are under the picture.

## Photographs: how they are chosen (each once, never a loop)
1. A room's own picture (`place.spaces[].img`) stays with its room. If one of them is `small` or cannot fill 414×552, the whole row takes that picture's own proportion and no picture is drawn wider than its pixels.
2. The two tall frames at the window's edge: house ← the most upright photograph that fills 596×900 (place roles first); menu ← a dish at 596×900, else a dish at 596×795 (3:4), else any.
3. Each first-screen tile ← a photograph from the page it leads to (`page` on the photograph), the menu's tile ← a dish; small pictures first.
4. Each menu part ← a dish from its own page.
5. Tiles with neither picture nor sentence ← an unused place picture.
6. Closing frame ← keeps its width and gives up height (549×900, 3:4, square, 3:2) until an unused picture fills it; the two small food frames ← dishes only; the closing block's two small frames ← what is left.
A second shot of the same thing (same file name but for a trailing number, or the same opening words of the description) is
treated as spent. A picture fills a frame only if it need not be enlarged more than 10 % (a `small` one: not at all).
`page` is not in CONTRACT.md; without it steps 3–4 fall back to text tiles and no dish grid.

## Picture share (tools/coverage.mjs)
Reference 44 at 1440 (57, 37, 50, 45, 29 per screen), 35 at 390. butarque 39 (25, 46, 48, 55, 55, 1), 36 at 390.
balamo 39 (41, 45, 47, 48, 17, 0), 39 at 390. Both sit exactly on the 5-point limit. The gap is the first screen (the
reference shows seven pictures there; ours shows as many as have a picture of their own) and the last screen (contact
and legal notices, which the reference's home page does not carry). No screen of the reference has a wide band, and
ours has none.

## With no photographs (probe/v/balamo-nopics, probe/v/butarque-nopics)
Renders clean and readable. What is left is type on the accent ground: the name, the two lines, the paragraph, the tiles
as text faces, the two large paragraphs, the logo or stamp, the links, the menu lists, the rooms as text columns, the
contact block at 41 px. With balamo's thin copy (no menu parts, no rooms, no hours) the page is 2364 px tall and the
tiles' second row is mostly empty ground — a deliberate-looking but thin page. With butarque's copy (menu, rooms, hours)
it is fuller. Minimum to offer it with pride: two upright photographs of the place about 1200 px high, three dishes, and
one picture per room; with none, only to a client with real copy.

## Checked
shots.mjs at 1440 and 390 for both clients and the scratch builds: no sideways scroll, no distortion, one h1, errors [].
legible.mjs `ok` for both clients and the three scratch builds. Keyboard focus: 2 px ink outline on every link and the button.
Reduced motion and no-script builds looked at. Widths 768, 1100, 1920: no sideways scroll.
Not checked: Safari and Firefox; real phones; a right-to-left language; a dark accent beyond one look at hotel1 (light ink on a dark ground rendered and passed legible.mjs there);
the faq and plans blocks beyond rendering sportbot once.
