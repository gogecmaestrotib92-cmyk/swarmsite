# brecon — template for places, rebuilt from thebrecon.com (measured 2026-11-12, 1440 and 390)

Run: `python3 -I build.py brecon butarque|balamo`. Test clients (data re-read 2026-11-12, second pass): butarque 52 photographs
(4 large place pictures, 1 large dish, 45 small dish squares, 2 small space pictures), balamo 20 (5 not small, none 1600 wide).
The two client columns of the table below are from the first pass (5 and 0 photographs); what each slot takes now is under "Image slots".
Measurements: `ref/anatomy.json`, `probe/tree-d.txt`, `probe/tree-m.txt` (box, type, ground of every element),
`probe/motion.json` (load, scroll, sliders, hover, menu), `probe/css-motion.txt`. Reference screens: `ref/ref-d-*.jpg`,
`ref/ref-m-*.jpg`, `probe/ref-menu-*.jpg`. Ours: `out/*-d-*.jpg`, `out/*-m-*.jpg`, `probe/our-*`.

## Sections of the reference, in order, and the data each takes
| # | reference (measured at 1440) | data | butarque | balamo |
|---|---|---|---|---|
| 0 | bar 50 high, stays at the top; cells cut at 1/6, 1/2, 2/3, 5/6 of the width: empty · dates · guests · BOOK on the deep colour · one centred link; hairline under it | `brand.name` when there is no logo · `place.hours[0]` (else street, city) · `place.phone` · `cta` (else `place.booking`) · `hero.secondary` | name, hours, phone, Reservas, La carta | (logo) address, phone, Reservar, Entrar a Bálamo |
| 0b | round 52 px menu button fixed at 48/84 on the ground colour; 130 px logo fixed at the right, 100 from the top | menu button · `brand.logo` | no logo: the name sits in the bar's empty first cell | logo.png (192 px, opaque white square, shown as it is) |
| 0c | menu: deep colour at 90 % over the page under the bar, list at 48/226, rows 39 apart with hairlines, 22 px | `nav` + `links` not already in nav | 5 entries | 5 entries |
| 1 | first screen, 100vh − 50: pictures changing by a fade, h1 44/44 at left 48, centred on 60 % of the height, 16 px line 30 under, two arrows bottom left | `hero.title`, `hero.text2`; 1 large photograph (3 when there are 6 to spare) | barra.jpg | no picture: the deep colour, 75vh |
| 2 | text row: h2 + short text in column 1/6–1/2, running text + underlined link in column 1/2–5/6; under it a row of 471 px squares running off the right edge, round next button | `statement.title`, `statement.text` · `hero.text`, `hero.note`, `hero.secondary` · squares: free large photographs, ≥ 2 | text only | text only |
| 3 | picture band, full width, 100vh, no words | 1 free large landscape photograph, at its own proportion up to 100vh | left out | left out |
| 4 | text row: label, h2, link · paragraph | `hero.kicker`, `steps.title` · `steps.text` | yes | yes (no paragraph) |
| 5 | picture 945 wide (65.6 %), 16:10, flush left | 1 free large landscape photograph | left out | left out |
| 6 | deep section, 40/60 padding, own hairlines in white: row of cards 471 apart running off the edge — 27 px name (bottom of a 108 box), 456 square picture, 40 below it caps label, text, underlined link | `place.spaces` (title, own picture, text; label and link from the matching `steps.items`); with no spaces `steps.items` as word cards, three to the row | 3 cards with pictures | 3 word cards |
| 7 | picture band 100vh with words over it at 1/6 + 30, 350 wide: label, h2 60 under, text, link | `place.events[0]`: when · what · price, where · cta; 1 free large landscape photograph | left out (no event) | no picture: the same words in the text row |
| 8 | split: picture 705 wide left, label/h2/text/link right | **changed** (owner: no picture boxed beside text) → the menu: `features.title`, link to `place.menu.h` · `menu.sections` (names with their counts in brackets; a table name/price where there are dishes) and `menu.lists`; a dish photograph 945 wide flush right under it | 6 sections, Postres with prices, 8 lists; no picture | left out (no menu data) |
| 9 | low band 75vh with words over it | `close.title`, `close.text`, `close.cta` (else `place.booking`); 1 free large landscape photograph | salmon.jpg | no picture: text row |
| 10 | newsletter row: label, h2, text · form | — no data (a form needs an address to post to) | left out | left out |
| 11 | foot: hairline, name 43 high, columns at 48 · 1/3 (two lists) · 2/3 · 5/6, partner logos | `brand.name` · address, phone, email · `nav` + `foot.links` · `place.hours` · `place.social`, `foot.legal` · `place.notices` | address, phone, mail, links, hours, legal | address, phone, links, socials, FEDER notice |

Not placed (the reference has no slot): `trust`, `figures`, `place.cuisine`, `place.price_range`, `place.takeaway`, `links[].d`,
`features.items[].d`, `quotes`, `place.since` (see `needs.json` "drops"). Hours, booking and every menu entry are shown. No `alt` is ever set as visible text.

## Measures used (1440 → 390)
Two hairlines the length of the page at 16.667vw and 50vw, ink at 50 % (white at 50 % inside the deep section) → one line at 20 px.
Text columns 33.33vw each, padding 0 50 0 15, text 415 wide → one column, padding 0 50 0 35. Sections 85 apart → 45; page starts 50 under the first screen → 38.
h1/h2 44/44, −0.02em, 400 → h1 22/22, h2 34/34. h3 27/27 → 24/24. Text 16/19.2; paragraphs 27.2 apart; h2 30 above its text.
Bar 50 → 56 (menu mark left, name/logo 43 centre, booking as 22 px words right). Squares (66.667vw − 19)/2 = 470.5, gap 15 → 239, gap 20.
Card 471 with 15 right padding (picture 456) → 240 (225). Band 100vh, low band 75vh → height of the words, padding 60 50 60 35.
Menu rows 39.4 (22 px) → 44 (30 px), plus a 50 px ground-coloured button. Foot padding 25, name 50 down, columns 25 under it.
Colours are relations, not the reference's brand: ground = the client's ground; text and hairlines = the client's ink; the one deep
colour (button, deep section, menu, first screen without a picture) = the client's accent taken toward black until white reads 10:1
on it (reference: white on its burgundy ≈ 15:1; there the ink and the deep colour are the same colour — here they are two, because
the clients' inks are grey/black and their accent is the only colour they have).

## Typeface
Orbikular (commercial) → **Newsreader** (Google, OFL), 400 and italic, optical size on. Newsreader is a little lighter and
narrower; sizes, leading and tracking are the measured ones.

## Motion: measured → reproduced
- Bar: in the flow at the top, fixed from the first scroll → sticky at 0 (same result). Menu button and logo fixed → same.
- Logo turns white over pictures/deep sections and deep over the ground (a class set per section) → not reproduced: the client's logo is a picture file and cannot be recoloured; the name sits in the bar.
- Arrival: h1/h2/h3 from opacity 0 and 10 px lower, 1 s ease; pictures opacity 0 → 1, 1 s; per section as it enters → same (first screen by CSS alone, sections by an observer).
- First screen: pictures change by a 0.3 s fade about every 4.35 s; arrows step → same; stops while the pointer or focus is on it and under reduced motion.
- Square row and cards: one step (slide + gap = 485.5) in 0.3 s ease per press; next button at right 48, previous appears at left 48 after the first step → same (native sideways scroll with snap, so it also moves by touch/trackpad; measured step 486).
- Links: opacity 0.8 in 0.25 s; booking button darkens in 0.25 s → same.
- Menu: deep overlay fades to 0.9 in about 0.25 s; the mark becomes a cross → same; Escape closes and returns focus.
- No parallax, no pinning, no smooth-scroll script on the reference → none.
Reduced motion: nothing hidden, no fade, no automatic change, steps without easing. Without scripts: everything visible; arrows and round buttons are not shown; the menu button does nothing (the same links are in the foot).

## Where it leaves the reference, and why
- Booking widgets (dates, guests) need a booking engine: their cells carry opening hours and the phone instead.
- The split (picture beside text) is not built; see row 8. The no-words band is as high as the photograph's own proportion at full width, or its own pixel height if that is more (never over 100vh; on the phone always its own proportion), and has no 20 % black film (that film served the reference's white logo).
- Words over a picture get a black veil of 57 % under them (reference: 15–20 % over the whole picture), falling to 15–20 % away from the words, so the worst pixel still reads 4.5:1.
- First screen without a picture is the deep colour at 75vh (the reference's low-band height), not 100vh.
- Card pictures: a small photograph is never wider than its pixels, so when a space's picture is small the whole row takes its width and proportion (butarque 418×315 instead of 456×456). Card text is shown on the phone too (the reference hides it there).
- The reference's phone drops the no-words band (its box is 0 high); ours keeps the picture.
- Phone menu: the bar keeps the ground colour (the reference's bar turns deep with white marks).
- "Menu/Close/Previous/Next" are accessible names only, from a fixed list by `lang`; no visible word is added.
- Eyebrow labels exist where the reference has them (rows 4, 6, 7, 8) and only when the data has the words.
- Reference's partner logos, sister-hotel mark and language list: no data; hours take the language column.

## Image slots (photographs only; `media.made` is never read) — chosen, never looped
A backdrop is a picture of the place: not `small`, not a dish, enlarged at most 1.3× at 1440. Each photograph is used once.
Order of claims among photographs not owned by a space:
1. first screen 1440×850 — room/exterior before bar before people/other, then the one the crop cuts least;
2. clean band — the one that fits whole first (landscape ≥ 1150 wide), then by role;
3. event band 1440×900 (only with `place.events`) — least crop, then role;
4. closing band 1440×675 (only with `close.title`) — role, then least crop;
5. wide picture 945×591 — room/exterior/bar only;
6. menu picture — a dish, not small, ≥ 945 wide (only when the menu has sections or lists);
7. two more first-screen pictures if three backdrops are still free;
8. square row — short side ≥ 470 px, dishes first, at most 8; with more than 8 dishes, evenly through the client's own order; the row's squares never exceed the smallest chosen picture's short side.
Spaces keep their own pictures in the cards. A missing slot is left out or becomes a text row, never a gradient.

| slot | butarque | balamo |
|---|---|---|
| first screen | terraza-mesas-altas.jpg (exterior 1800×2400, crop) | gran-reserva-barrica.jpg (room 1242×720, 1.18×) |
| square row | postre-ferrero-rocher-gold, postre-tarta-de-queso, arroz-carabineros-2, hamburguesa-butarque-2, entrecot, surtido-de-ahumados, gamba-plancha, zamburinas-gratinadas (600×600 dishes) | pulpo, pulpo-perejil, zamburinas (dishes), maridaje-copa-2, sala-principal, salon-jardin-vertical, mostrador-marisco, bodega-botellero — capped at 480 px |
| clean band | gintonic.jpg (people 1900×800, 1440×800) | gran-reserva-reservado.jpg (room 1242×720, 1.16×) |
| wide picture | — (the fourth large place picture, salon-1900.jpg, belongs to a space) | — (no room left) |
| cards | terraza.jpg, salon-1900.jpg, chill-out.jpg at 418×315 | word cards (no spaces) |
| event band | — (no event) | maridaje-copa.jpg (other 1437×810) |
| menu picture | salmon.jpg (dish 1187×796) | — (menu is a link only) |
| closing band | barra-2400.jpg (bar 1800×2400, crop) | gran-reserva-pasillo.jpg (room 1242×1152, crop) |
Used: butarque 13 of 52, balamo 12 of 20. The wide-picture slot and the changing first screen are filled by neither client (run only by `probe/synthetic.py` in the first pass).
Seen and left: balamo's two octopus dishes stand side by side in the row (the data's order), and its logo is an opaque white square over the first picture.

## Picture share (`tools/coverage.mjs`, 1440)
reference 62 % overall, per screen 96 39 92 50 57 71 59 76 0, 5 screens with a wide picture.
butarque 57 % (96 53 84 28 20 81 30), 3 wide — 5 points under, at the limit; its screens 4–5 are the cards (small space pictures) and the menu text.
balamo 66 % (96 49 89 51 91 40 0), 5 wide.
Least photographs (`probe/subset.py`, balamo's data with fewer pictures): 6 (3 rooms 1242 wide, 1 other, 2 small dishes) → 64 %, every band filled;
4 (2 rooms, 2 dishes) → 46 %, event and closing bands fall back to text rows. None (first pass) → 2 %, a typographic page. `needs.json` states this.

## Checked (second pass)
`tools/shots.mjs` both clients, both widths: sideways 0, distorted 0, h1 1, errors []. `tools/legible.mjs`: ok — butarque 263 readings, balamo 178.
One-file copies 1.1 MB and 1.3 MB. Looked at both clients at 1440 and 390 (`out/*-full.jpg`, `out/*-00.jpg`).
From the first pass and not re-run on the new data: `probe/behave.mjs` (menu, focus, hover, row step, arrival, reduced motion, no script) —
the script and styles for these did not change. Stale files I could not remove (a removal was refused by the tool): `pairs/*-synthetic-test.jpg`,
`pairs/d-02-intro-butarque.jpg`, `pairs/d-06-event-without-picture-balamo.jpg`, `probe/syn-*.jpg`, `out/_synthetic.html`, `out/_min4.html`, `out/_min6.html` are test pages/old pairs, not client pages.
Not checked: Safari/Firefox, widths between 390 and 1440 and above 1440 (backdrops enlarge further there), a client with a dark ground, a long row of word cards.


## Engine import fixes (2026-11-12, stress: plans 1/3/5, features 2/9, steps 1/6, 12-word h1, 40-char button, no faq, no photographs; clients casaolmo and larchwick; 1440 and 390)
- A row of cards in which no card has a picture now takes the word-card build (three to the row), whether the cards come from `place.spaces` or `steps.items`. Before, the build was chosen by "has spaces", so spaces without photographs kept the half-width picture card and the round next button sat on the third card's title (1.12:1, larchwick with no photographs).
- In the word-card row the two round buttons stand in the section's lower margin, under the text, since there is no picture for them to stand on.
