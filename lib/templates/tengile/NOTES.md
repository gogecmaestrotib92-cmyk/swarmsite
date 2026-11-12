# tengile — template for places, rebuilt from tengilemalamala.com (measured 2026-11-12, 1440 and 390)

Run: `python3 -I build.py tengile butarque|balamo`. Test clients: butarque (5 photographs, 2 of them small), balamo (none).
Measurements: `ref/anatomy.json`, `probe/tree-d.txt`, `probe/tree-m.txt` (boxes of every element), `probe/motion.json`,
`probe/struct.json`, `probe/more.json`. Reference screens: `ref/ref-d-*.jpg`, `ref/ref-m-*.jpg`, `ref/menu-*.jpg`.

## Sections of the reference, in order, and the data each takes
| # | reference (measured) | data | butarque | balamo |
|---|---|---|---|---|
| 0 | header over the hero: MENU left, wordmark centre, ENQUIRE right, 14 px caps; leaves on scroll down, returns as a solid 38 px bar on scroll up | menu toggle · `brand.logo` or `brand.name` · `cta` (else `place.booking`) | name set as wordmark | logo.png (opaque white square, shown as it is) |
| 0b | menu: panel 8 px from the edges, 467 wide (+372 with cards); large list 40 px serif, small list 16 px, lodges as cards in a second scrolling column | `nav` · `links` not already in nav · `place.spaces` with pictures | all three | nav only (467 panel) |
| 1 | hero 100 vh: film pinned behind; h1 120 px caps in two lines (first from the left inset, second to the right inset); 18 px serif text + pill at column 7, 100 px under the title | `hero.title`, `hero.text`, `hero.primary`; backdrop = one photograph | barra.jpg | no picture: the deep accent slab |
| 2 | heading row: 14 px label col 1–2, 32 px serif paragraph col 7–12 | `hero.kicker` · `statement.title` (+ `statement.text` under it when there is no pair of pictures) | yes | yes |
| 3 | pair of pictures: caption top left (346 wide), picture 577×735 lower left (320 below the caption), picture 696×840 upper right | `statement.text` + two free photographs; with one photograph it stands alone in the right half at its own proportion | one (salmon.jpg) | left out |
| 4 | 48 px accent paragraph, full width | `steps.title` | yes | yes |
| 5 | group "Lodges": 16 px text col 1–4, three cards 459 wide: picture 460:560, 20 px serif name 12 below | `steps.text` · `place.spaces` (title, text, img); if there are no spaces, `steps.items` as word cards with their pill | 3 picture cards | 3 word cards |
| 6 | group "Camps" (same build) | `features.title` · `place.menu.sections` + `lists` as word cards (name → link; a section's dishes as a table name/price); `hero.secondary` as pill when it leads to the menu | 15 entries, Postres with prices | left out (no menu data) |
| 7 | quote: 48 px accent, col 2–11, name + source 14 px caps | `quotes[0]` | left out | left out |
| 8 | large gallery 16:9 (4:5 on a phone), halves are prev/next, counter | free large landscape photographs, ≥ 2 | left out | left out |
| 9 | "Our story": label col 1–2, 32 px paragraph col 7–12; pictures 340×500 and 340×340 at col 7–9 / 10–12; text + pill under the square one | `place.events[0]`: when · what · price, where · cta; two free photographs | left out (no event) | words only |
| 10 | centred block (label, 32 px title, pill) with six small pictures circling it, 882 high | `hero.text2` · `hero.secondary` (unless already used in 6) · 4–6 free photographs | words only | words + pill |
| 11 | "Community": label, 32 px paragraph, then a moving strip of pictures 464 wide | strip only: ≥ 4 free large photographs | left out | left out |
| 12 | closing cover 1440×1270: picture, text column at col 7–10 on the bottom (32 px title, 16 px text, pill) | `close.title`, `close.text`, `hero.note`, `close.cta` (else `place.booking`); one free large landscape photograph of a room/exterior, ≥ 800 px high | no picture: deep slab | no picture: deep slab |
| 13 | footer on the accent: link columns, addresses, socials, a pill; small print | `nav` · `place.social` · address + phone + email · `place.hours` · `place.booking` · `place.notices` · `foot.legal`, `foot.links` | address, phone, mail, hours | address, phone, socials, FEDER notice |

Not placed (the reference has no slot): `trust`, `figures`, `place.cuisine`, `place.price_range`, `place.takeaway`, the `d` of `links`,
menu `count`s, `features.items[].d` ("5 products" is the shop theme's label).

## Measures used (1440 → 390)
Grid 12 columns, 16 gap, 16 page margin → 4 columns. Sections 100 apart → 80; groups, gallery, story carry 16 of their own.
h1 120/0.9, −0.02 em, weight 220, caps (8.33 vw) → 48.75 px (12.5 vw). 48/1.1 w220 accent → 24/1.1 w310 (quote 32).
32/1.15 w310 → 28. Card name 20/1.2 → 18. Hero text 18/1.1 serif. Body Inter 16/1.25 −0.01 em. Labels Inter 500 14/1 caps.
Pill: label 24 high, 4×8 padding, radius 2, arrow box 30×24, 4 apart. Hero inset 120 each side (8.33 vw); description at column 7, 340 wide
(phone: column 2, 265). Cards 460:560, gap 16 (phone: one column, 32 apart). Cover 1440:1270 → 390:840, text 80 from the bottom.
Footer padding 80/25. Menu list rows 40 + 8, small rows 28.
Colours are relations, not the reference's brand: ground; ink; accent as text held at 4.6:1 on the ground (`--acct`); accent as slab carrying
the light ink at 5.5:1 (`--deep`; reference 5.6:1); quiet pill = 10 % ink on ground; pill on pictures = near-white.

## Typefaces
PP Fragment (commercial) → **Fraunces** (Google, OFL), variable, weights 220/310 as measured. Inter is the reference's own sans and is OFL → Inter.
Fraunces is softer and has more contrast in the hairlines than Fragment; its capitals are wider, so the h1 size is computed from the longest line.

## Motion: measured → reproduced
- Hero letters: each rises from 100 % below inside its word's clip, 1.6 s cubic-bezier(.19,1,.22,1), 0.05 s apart (0–0.4 s), with a blur clearing → same (CSS only).
- Hero text: opacity + blur, 1 s cubic-bezier(.165,.84,.44,1) → same. Cover: transform 2 s cubic-bezier(.19,1,.22,1) → same, from scale 1.2 (start value assumed; only the curve was read).
- Hero picture pinned (sticky inside a 200 % box, clipped by the hero) while the hero leaves; hero text moves down at half the scroll (y=300 → +150) → same.
- Every picture: 12 % larger than its frame, drifting from about −5.4 % to +5.4 % of its height while the frame crosses the screen → same.
- Header: fixed after the top, translateY(−100 %) on scroll down, back on scroll up with the ground colour; .3 s cubic-bezier(.25,.46,.45,.94), colour .15 s → same.
- Pills: label and arrow fill with the accent, text turns light, .3 s → same.
- Cards: label pill and round arrow slide up 24 px in .4 s cubic-bezier(.19,1,.22,1) and follow the pointer down the picture; on a phone they are simply there → same, only on cards that have a link.
- Gallery: the next slide scales 1.2 → 1 in about 0.75 s; a label follows the pointer → wipe + scale 1.2 s, arrow box follows the pointer (the reference's label says Next/Prev; a word the data does not have).
- Cloud: six pictures turn clockwise round the centre, about 37° over the pass (rx ≈ 372, ry ≈ 300; phone 200/262) → 56° over the whole pass, same radii.
- Marquee: 120 s linear, endless → same; pauses on hover.
- Footer (desktop only): content slides out from under the page at 0.8 of what is hidden → same. Phone: none → none.
- Menu: the reference's drawer panel moves in .8 s cubic-bezier(.77,0,.175,1), backdrop .6 s cubic-bezier(.25,.46,.45,.94); the menu panel's own curve was not sampled, the drawer's was used.
- Not reproduced: Lenis smooth scrolling (native scroll here); the 2 s page-load curtain; "Play video" pointer label and film overlay (places have no film).
Reduced motion: no animation, no drift, no half-speed text; marquee becomes a strip scrolled by hand. Without scripts: everything is visible, header stays at the top, menu button does nothing (nav is in the footer).

## Where it leaves the reference, and why
- Visible words "Menu", "Close", "Next/Prev", the footer column titles ("Explore", "Company", "Connect") and the card label ("9 Suites") are not in the data: the menu is a two-line mark, close is a cross, the gallery pointer shows an arrow, the footer columns have no titles, cards have no label. Accessible names (aria-label) come from a small fixed word list by `lang`.
- The 12 px patterned band under the hero is the reference's own ornament: left out.
- A small photograph is never wider than its pixels: when a space's picture is small the whole row takes that picture's proportion and width (butarque: 418×315 instead of 459×558; the row stops short of the right edge).
- Card text (`spaces[].text`) is set under the name; the reference's cards have a name only.
- One picture instead of the pair: it stands alone in the right half, the caption moves up under the 32 px paragraph (owner's rule: no picture boxed beside text). The pair itself (two pictures, caption above the left one) is kept as measured — the caption does stand beside the right picture; say if that must go.
- No picture is shown twice: a photograph used by a space is not used again, except that the hero may take one when every large picture belongs to a space.
- Text over a picture gets a veil (hero 63–68 %, cover up to 66 %) so the worst pixel reads ≥ 4.5:1; the reference's film is much lighter.
- Footer on a phone: lists are open (the reference folds two of them under titled buttons; there are no titles).
- Community section: only the strip of pictures; its label and paragraph have no data.

## Image slots
hero (1 large, room/bar/exterior preferred, a dish only if nothing else) · cover (1 large landscape room/exterior ≥ 800 px high) · pair (2 large) ·
gallery (2–6 large landscape) · story (2, ≥ 340 wide) · marquee (≥ 4 large) · cloud (4–6, small ones welcome) · cards (each space's own picture).
Order of claims as listed. No `media.made` is read. A missing slot is left out or becomes the plain deep/ground colour — never a gradient.
butarque: hero barra.jpg, single picture salmon.jpg, cards terraza/salon/chill-out. No cover picture, gallery, cloud, strip.
balamo: no photograph anywhere; the page is type on white with a deep-green first screen, closing block and footer. It holds, but it is not this reference any more — the reference is led by photographs.
To offer this template honestly: at least ~9 photographs — 1 large backdrop (≥ 1600 wide, room/exterior), 1 large landscape for the close, 2 large for the pair,
3 for the spaces (≥ 920 wide to fill the 460:560 cards), 2+ large landscapes for the gallery. The full reference (story pair, cloud, strip) needs about 23.

## Checked
`tools/shots.mjs` both clients, both widths: sideways 0, distorted 0, h1 1, errors []. Contrast against rendered pixels (`probe/check.mjs`): hero title worst
pixel 5.09 (d) / 5.14 (m), hero text 5.42 / 5.28, wordmark 6.03, 48 px accent text 4.85 (butarque) / 4.63 (balamo), slab text 5.62 / 5.79, small print 4.59–4.71.
Behaviour (`probe/behave.mjs`): pin, half-speed text, drift, header, footer slide, menu open/Escape/focus return, focus ring, reduced motion, no script.
`probe/synthetic.py` repeats butarque's three large photographs and adds a dummy quote/event so the pair, quote, gallery, story, cloud, strip and cover
paths run (`probe/syn-*.jpg`, pairs named `*-synthetic-test`): mechanical test only, not a client page.

## Pass of 2026-11-12 — one picture family, picture share, readability, real photographs
This section supersedes "Image slots", the "butarque / balamo" lines and "Checked" above (written when butarque had five
photographs and balamo none). The clients now carry their sites' photographs: butarque 52, balamo 20.

**Motif.** The reference repeats one thing: photographs of the place (lodges, river, rooms) with a few details. Here the
family is the client's own photographs — the place in backdrops and cards, dishes in the strip and small tiles. No
`media.made`, no tinted or coloured grounds behind pictures; a missing slot is left out or is the plain deep/ground colour.

**How photographs are chosen** (`_allocate`, `_by_page`; each picture once, a second view `-2` of a subject only when
nothing else is left, most of a large set is never shown):
1. opening: not small, not a dish, exterior/room/bar first, the one that fills most of 1440×900 at its own size.
2. room cards: `place.spaces[].img`; with no spaces, each `steps.items[]` takes the photograph whose `photos[].page`
   equals its link (all cards or none). Menu sections whose link equals a photograph's `page` become picture cards
   (460:560 as the reference's second group; four across when there are four); the rest stay word entries.
3. closing cover: wide, not a dish, ≥ 700 high, place/people first. 4. pair: the two large pictures that best fill
   696×840 / 577×735. 5. gallery: ≥ 2 wide large non-dish pictures left. 6. event pictures (only with `place.events`).
7. strip: 4–8 pictures ≥ 464 wide, dishes first, spread evenly through the set. 8. the six round the centred block.

| slot | butarque (25 of 52 shown) | balamo (20 of 20) |
|---|---|---|
| opening | terraza-mesas-altas 1800×2400 | gran-reserva-pasillo 1242×1152 (stops at 1242 wide: 99 px dark each side at 1440) |
| pair | barra-2400, salmon | maridaje-copa alone (right half) |
| room cards | terraza (418, small → row 418×315), salon-1900, chill-out | by page: gran-reserva-barrica, mostrador-marisco (570×740, small → row takes its proportion), gran-reserva-reservado |
| menu picture cards | by page: risotto-de-boletus (Arroces), hamburguesa-butarque (Carnes a la brasa), surtido-de-ahumados (Del mar), calamar-de-potera (Pescados) | — (no menu sections) |
| event | — | sala-principal, salon-jardin-vertical |
| round the block | 6 dishes | reservado-magallanes, sala-de-fiestas, sala-de-fiestas-mesas, bodega-botellero |
| strip | 8 dishes | pulpo, pulpo-perejil, zamburinas, terraza, alta-mar, arrecife, arrecife-copas, reservado-magallanes-mesa |
| closing cover | gintonic 1900×800 (the cover takes the picture's own proportion: 1440×606, grows with its text) | maridaje-copa-2 1344×1334 |
| gallery, quote | left out (no two wide large pictures left; no quote) | left out |

**No picture above its own pixels.** Every frame carries `max-width` = the picture's pixels for that frame's proportion;
the opening `.pin` and the cover stop at the picture's width/height; the 12 % drift is applied only where the picture
still covers the larger frame (`fits()` in the script). Measured (own probe, object-fit and transforms included): every
picture ≤ ×1.00 at 1440 and 390, both clients.

**Picture share** (`tools/coverage.mjs`, 1440): reference 56 % `[100,34,63,31,69,44,82,36,23,25,88,100,34]`, 3 wide
screens. butarque 57 % `[100,56,54,66,10,35,93,31]`, 2 wide (opening, cover). balamo 53 % `[89,27,78,29,14,85,76,8]`, 3 wide.
The reference's third wide band (gallery) has no counterpart for either client.

**Readability** (`tools/legible.mjs`): butarque ok — 0 of 182; balamo ok — 0 of 136. Arriving at each position from below
(header returned, solid): 0 of 190 / 0 of 126 (own variant of the gate).
**Header:** over the opening it is light type on the veiled picture; after 40 px it is a solid ground bar that only shows
on the way up. Both states are in the readings above.
**Focus:** every Tab stop at both widths shows a ring ≥ 3:1 against what it is drawn on (own probe: ring pixels compared
with the same pixels without the ring). Fixed: the skip link's ring (dark on the dark picture → now inside its own light
chip); in a short foot the focused link was still under the page (the foot now stops sliding when focus enters it).
The hero pill's changed focus ring measures as visible.
**Also changed:** the phone note beside the number is printed only when the client's own text says the same words
(balamo's `place.phone.note` is a capture remark and is not printed); card label pills no longer show a 2 px sliver at rest.

**shots.mjs:** butarque d `{"height":6811,"sideways":0,"distorted":0,"h1":1} errors: []`, m `{"height":9289,…} errors: []`;
balamo d `{"height":6814,…} errors: []`, m `{"height":7341,…} errors: []`. One-file copies 1.40 MB and 1.19 MB.

**Still not right / not checked.** balamo has nothing ≥ 1600 wide: its opening is a 1242-wide picture in a dark screen and
the title starts on the dark bar. balamo's pair and cover are two views of the same wine glass. The quote and gallery
paths are not exercised by either client (pairs `d-06`, `d-07` are from the earlier synthetic run and are stale).
No FAQ part is built (both clients' `faq` is empty). Not checked: Safari/Firefox, widths between 390 and 1440, screens
wider than 1440 (frames stop at the pictures' pixels there), behaviour.mjs was not re-run after the allocation change.


## Engine import fixes (2026-11-12, stress: plans 1/3/5, features 2/9, steps 1/6, 12-word h1, 40-char button, no faq, no photographs; clients casaolmo and larchwick; 1440 and 390)
- The slab's second text tone (`sub`: the light ink 15 % toward the slab) is now moved back toward the light ink until it reads 4.6:1 on the slab. The 15 % mix alone gave 4.48:1 on casaolmo's orange slab ("desde las 13:00h", the foot line).
- `plans` added to needs.json drops (the reference has no tiers).
