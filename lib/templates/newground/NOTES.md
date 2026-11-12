# newground — a shop template (reference: newgroundcoffee.com, home page; listing page /coffee for the grid)

Measured 2026-11-12 at 1440×900 and 390×844: `ref/anatomy.json` (tools/anatomy.mjs), `ref/ref-detail.json`,
`ref/ref-detail2.json` (probe/ref.mjs, ref2.mjs: computed styles, containers, hover sampling), probe/ref3.mjs (phone
carousel, menu, foot), probe/ref4.mjs (listing grid). Clean screenshots `ref/clean-*.jpg`. The cookie notice was
declined and the sign-up pop-up closed with its own close button; nothing was accepted or submitted.
Test clients: `shop1` (primary), `butarque`.

## Sections of the reference and what each takes

| # | reference (1440) | measures | data |
|---|---|---|---|
| 0 | announcement bar, accent ground, one centred line, close cross | 44 high, pad 12/30, Inter 14/1.4 | `hero.kicker`, else `trust[0]`; ink on the accent is white or black, whichever reads |
| 1 | header, sticky | 70 high, 1px ink rule under; three columns: nav left (display capitals 16, 15 between), name centre (258×30), call right (ink pill 40 high, 12px) | `nav` (as many as fit the left third at 1440; the rest hidden), "More" opens the drop panel; `brand.name` set in the display face; `signin` as a capital link; `cta` as the pill |
| 1b | drop panel under the header | full width, links Inter 500 40/48, small links 17 in 60% ink; opacity .15s linear, inner moves .5s cubic-bezier(.165,.84,.44,1) | all of `nav` large, `links` small |
| 2 | two half panels, each a photograph edge to edge | 720×786 = the screen under the header; words bottom-left, 40 in; title Inter 500 40/48 −.03em, line 20/500, white pill 55 high (pad 0/40, radius 30, display capitals 16) 30 under | left: `hero.title` (the h1), `hero.text`, `hero.text2`, `hero.primary`; right: `statement` with the link of the step that repeats its title, else `hero.secondary` |
| 3 | product row | header pad 60/30, h2 display capitals 80/72 −.03em left, pill on the 4.5%-ink ground right; three cards 440 with 30 between; square picture, 30, title display 30/27, line 20/26 at 60%, price display capitals 16 at the foot; 80 under | a `catalogue` group (or a `place.menu` section that lists items): h2 = group name, pill = the group's own count line → the group's page; a card per item that has a picture; more than three cards run on in one row, 3.3 to the screen, as the reference's row does on a phone; items without a picture are rows in type under the cards |
| 4 | second pair of half panels | as 2 | `steps.items` two at a time (title, text, link) |
| 5 | second product row | as 3 | the next group. A group none of whose items has a picture opens with the group's own photograph as a full-width band (title, count pill), then its rows |
| 6, 7 | full-width picture bands | 1440×786, words centred at the foot, 80 up: title 40/48, line 24/30, pill; 40 between | a step left over after the pairs; then `close` (title, text, link) |
| 8 | foot, ink ground | pad 30; a line in display capitals 90/81 −.04em; 250 lower a second very large line with a white pill at its right end on a 2px rule; a 20px line under; then columns at 105: titles display capitals 16, lists Inter 19/26.6 at 60% white; site map in two columns, contact, "visit" with a 235×223 picture and the address; a last strip 14px over a 1px rule | very large line: `place.phone` (else e-mail) as a link, pill = `place.booking`; under it the phone note and e-mail; site map = `links` (else `nav`) under the name; contact = e-mail, phone, `place.social`; door = city as the title, a small photograph of the front, address, `place.hours`; `foot.links`; `foot.legal` |

Also built from the reference's parts because a visitor comes for them (not on its home page): `plans` (card without a
picture, price in the 80px display size), `faq` (rows that open), `team` (cards when a person has a portrait, rows in
type when not), `credentials`, `locations`, the menu's index (`place.menu.sections` without items and `lists`, as rows
with the count at the right, under the label of the link that points at the menu), `features` as rows. Checked on a
scratch copy with test words (probe/extra-shop1.html): shots and legible pass.

Words the template adds: none of copy. Column titles in the foot come from the data (the name; the label of the link
whose address contains "contact"; the city). The only interface words are "More" on the header's drop panel and the
aria-label "Close", from a ten-language table by `lang`.

## Phone build (390)
Bar 13px on two lines; header 60 with the name left and a two-line burger right; the menu is a sheet that slides in
from the right (.75s, the same curve) with links at 26px, the call as a full-width pill at the foot. The opening pair
is a carousel: one panel to the screen (390×724), two dots bottom right (10px, .6/1 opacity), moving on by itself.
The second pair stacks at 500 high each. Product header stacks (h2 40/36, pill under); cards 276 wide with 20 between
slide sideways; bands 390×724 with title 26, line 18; foot line 50px; columns stack.

## Type
Body: Inter (the reference's own body face, open licence) 400/500, −.03em. Display: the reference's `fontdisplay` is a
commercial tight grotesque set in capitals → **Inter Tight 600**, capitals, same sizes and tracking. Ours runs a
little narrower per letter than the reference's.

## Colour
The reference's relations with the client's palette: ground = `palette.ground`; ink = `palette.ink` (replaced by
near-black/white only if it does not read on the ground); bar = `palette.accent`; foot and picture-less panels = the
ink; card ground and quiet pill = the ground with 4.5% ink (the reference's #f4f4f4 on white), 8% on hover; second
lines = the ink at 60%, strengthened until it reads 4.7:1 (shop1's teal at 60% read 3.9:1).

## Motion measured → reproduced
- Header `position: sticky; top: 0`, unchanged down the page (sampled at 9 scroll positions) → same.
- Pills: `.15s linear`; white → #f4f4f4 with ink → #2d2d2d; quiet pill #f4f4f4 → #ebebeb (sampled at 60/120/200/400/900 ms) → same.
- Product card picture: scale 1 → 1.05, `transform .75s cubic-bezier(.165,.84,.44,1)`, clipped by its square → same.
- Foot links: 60% → 100% white, `color .2s linear` → same. Header name: `opacity .25s linear` → same.
- Drop panel: `opacity .15s linear`, inner `transform .5s` on that curve → same (as keyframes, on opening only).
- Phone menu: `transform .75s` on that curve from the right → same (opening only; it closes at once).
- Phone opening carousel: moves on every ~4.5 s (positions sampled each 500 ms for 15 s), dots `opacity .3s linear`
  → same interval, a native smooth scroll with snap; it stops for good at the first touch, key or focus and never
  starts under reduced motion.
- No scroll reveals, no parallax, no pinned sections on the reference (panel pictures do not move on hover) → none.
- Reduced motion: all transitions and the carousel off. Without scripts: everything is visible, the menu still opens
  (it is a `details`), the carousel can be swiped, the bar cannot be closed.

## Where ours departs, and why
- **Veil under words on pictures.** The reference sets white words straight on dark photographs. The client's are
  not chosen for that, so each block of words carries a black veil (74% → 66% → 0 over the top 150 px of the block);
  the second lines are full white (reference: 60% white in the bands). legible.mjs: ok for both clients.
- **Longer words on the panels.** The reference has one short line per panel; the clients' paragraphs run 2–7 lines at
  the same 20px, so the dark part of a panel is taller.
- **No newsletter, cart, account icons, payment marks, certification mark.** No form without somewhere to send it; no
  cart in the template. The foot's two very large lines are the phone number and the booking pill instead.
- **Icons**: the reference's account and bag drawings are not taken; `signin` is a word. The burger and the cross are
  two plain lines.
- **Rows in type** for products without a picture are not a part the reference has; they are its card title and price
  on one line between 1px rules.
- "More" opens on a press (the reference's panel opens on hover).

## Pictures (the client's own photographs; each used once; no made pictures)
Picture family: the client's photography throughout. A slot whose picture is missing falls back to the ink ground.

| slot | size at 1440 | chosen by | shop1 | butarque |
|---|---|---|---|---|
| card | 440² (388² when more than three) | the item's `img`; else a product/dish photograph whose description starts with the item's name (a join; the description is never shown) | 4 candles | 3 desserts |
| opening left | 720×786 | not small, short side ≥ 780, proportion .55–1.9; role product/dish/work first, then nearest to the slot's proportion | no2-range | salmon |
| opening right | 720×786 | the picture of the step that repeats the statement's title; else role room/bar first | diffuser | barra-2400 |
| pair panels | 720×786 | the step's own `img`; if that is small, the larger picture of the room with the same title; if still none, an unused photograph of the same role; else plain | dried-bunches (the step's own is on a product card), store-plants | terraza-mesas-altas (same role as the small one), salon-1900 |
| group band | 1440×786 | group `img`, else the photograph whose description equals the group's name; ≥ 1600×780 | hand-lotion | — |
| step band | 1440×786 | as pair panels | — | Chill Out: its picture is 418 px and no other room is left → plain ground |
| closing band | 1440×786 | ≥ 1600 wide, ≥ 780 high; role exterior, then room/bar, people | shopfront-bw | gintonic |
| foot | 235×223 | an unused exterior/room picture, small allowed | shopfront | terraza |

No picture stands in a box beside text: every large picture is the whole ground of its panel or band with the words
laid over it; a card's picture stands above its words, as in the reference.

## Picture share (tools/coverage.mjs)
| | 1440 overall | per screen | 390 overall |
|---|---|---|---|
| reference | 65 | 89 56 87 70 100 56 5 0 | 60 |
| shop1 | 62 | 89 46 78 100 62 30 3 | 61 |
| butarque | 49 | 89 48 73 18 58 34 4 | 49 |
| no photographs | 0 | | 0 |

butarque is 16 points under: it has five photographs that are not small, the reference's page uses six large ones
plus product pictures; its 45 small dish pictures can only be cards, and only three of them can be joined to a
priced item (the menu data lists items for one section only).

## Checks
shots.mjs — shop1: d height 5849, sideways 0, distorted 0, h1 1, errors []; m height 5987, same.
butarque: d 5883, m 5956, same. legible.mjs: ok both (292 and 222 line readings). Keyboard focus: 2px outline in
the current colour, 3px inside panels and cards (probe/own-shop1-d-focus.jpg). Scratch copies without pictures and
with plans/faq/team/credentials/locations: shots and legible pass (probe/).

## Not transferred
The reference's newsletter form, cart count, account, payment marks, B-Corp mark and its drawn wordmark; hover-opened
submenu with a product thumbnail; star ratings on cards. `figures`, `quotes`, `logos`, `hero.note` have no part on
this page (needs.json "drops").

## Not checked
Press (:active) states of the reference; its tablet widths (ours switches to the phone build at 900px — the
reference's own breakpoint was not measured); Safari and Firefox; widths above 1440; right-to-left text; a dark
client palette (the colour rules allow for one, no test client has it).
