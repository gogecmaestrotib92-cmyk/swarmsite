# acme — a catalogue-first shop page, built on acmecups.nz

Reference: https://acmecups.nz (home page). Measured on 2026-11-12 at 1440×900 and 390×844 with the location and
newsletter pop-ups closed or hidden. Nothing was accepted.
Measurements: `ref/anatomy.json`, `probe/dom-d.txt` and `probe/dom-m.txt` (every box with its styles),
`probe/motion.txt` and `probe/thr.txt` (motion), and screenshots in `ref/` and `probe/` (`nopop-*` are clean).
Test clients: `shop1` (primary; 10 priced products in 2 groups) and `school1` (46 priced courses in 8 groups).
None of the reference's code, words, pictures, CAD drawings, logo or customers' names is used.

## Sections of the reference and what each takes

| # | reference at 1440 | data | shop1 | school1 |
|---|---|---|---|---|
| 0 | fixed bar 72 high: 15 px bold condensed caps links at 28 with a 17 px gap; a 231 px announcement running right to left (10 s, linear); search, account and cart at the right. Clear over the first picture, on the page ground after it | `nav` · run = `hero.kicker` + `trust[]` (each once) · `signin`, `cta` (the reference's search, account and cart have no data and are left out) | 6 links, log in, call | 6 links, call |
| 0b | the name `ACME`, fixed at 26/136: 148 px over the first picture, 48 px after it (0.3 s) | `brand.name` (as text; its size is held so a long name fits: 148 px, or 55 vw / its letters at the top, and 48 px or the 12.5 vw column after) | "Wild & Rust" 120→48 | "Escuela Montalbán" 78→25 (two lines) |
| 1 | one photograph at 100 vh; a 26 px/120 % sentence 325 wide at 888/387, its words rising one after another; one dark 31 px button | 1 free photograph (≥1100×690, product first) · **h1 = `hero.title`** · `hero.primary` | hand-lotion | team |
| 2 | ground; a 30/39 px sentence 624 wide at 181, a 14/20 note 357 wide at 902; 300 px of air under it | `hero.text` · `hero.text2`, `hero.note` | text, note | text, text2, note |
| 3 | "range": 48 px caps title at 178 with its count `[15]`; at the right a grey "shop collection" button and two 34×32 arrows; ruled cards 360 wide (25 vw): 20 px caps name, 12 px lines, square picture, a 29 px ruled price bar ("add to cart … $26"); one card per arrow press, 0.3 s | the first catalogue group with ≥2 items that have their own picture: `t`, count, `h` → "view all"; its items with `img`: `name`, `note`/`text`/`prices`/`rows`, `img`, `price`, `state`; the card links to the item's `h` (the client's own page; no cart) | Candles, 4 cards | — (no item has a picture) |
| 4 | three CAD drawings of the range (cup, plate, cutlery), 976 high | **not transferred**: line drawings of the product, which a small business does not have. Left out | — | — |
| 5 | "collection": a 48 px title over three ruled columns 443 / 443 / 553: words + grey button · one product card between black rules · **a film running to the page edge, as tall as the row (682)** | the next group with items: `t`, count, `text`, `h` · its first 5 items as name + price bar · a free upright photograph (≥425×525, product first) to the edge. With no photograph the third column is left out | Hand Lotion, 3 items, no2-range | Intensive courses, 5, door-group |
| 6 | a full-bleed photograph 1440×900; a 391 px accent panel (28/24/24) low at the right, 14 px words, a dark button | `statement.title/text` · `hero.secondary` · 1 free photograph (≥1100×690, room first); the panel takes `palette.accent`. With no photograph, a tinted band | dried-flowers | teacher |
| 7 | the shop: a 360 px column with the range names in 48 px caps (grey, pressed one black with its count), **sticky at 136**; beside it a 21 px title, 14 px words, a button and a 4-column grid of small ruled cards (171 wide: 15 px caps name, 12 px line, picture, price) | **the whole `catalogue`**: `title`, `text` as the head · each group a name in the column (marks the group in view; a press goes to it) · per group `t`, `text`, `h`, items in the small cards (four across; two across for items with long lines of prices). `note` under it. A group of more than ~1500 px is followed by a band of a free photograph when one ≥1100×400 is left | 2 groups, 10 items | 8 groups, 46 items, no band (no photograph left) |
| + | — | `plans`: the card row of part 3 again (name, `line`, `rows`, price + `per`, the bar carries the button words; `marked` fills the bar) | — | — (tested with 1/3/5) |
| 8 | "colours": a ruled strip of 177 px square cells (a tag top-left, a colour dot), sliding; under it the pressed cell's 21 px title, 14 px words, a button | `features`: `title`, count, `text`; each item a cell (its number as the tag, `t` in caps); a press shows its `d` below | — | 7 accreditations |
| 9 | a full-bleed film 1440×765 with a 30/39 px white sentence and a grey button at 180/142 | `close.title/text/cta` · `media.video`, else 1 free photograph (≥1100×590, exterior first) under a ground veil at the left | shopfront-bw | students-outdoors |
| 10 | "journal": a 48 px title, then ruled rows 547 high: a tag at 180 · a 21 px title and "keep reading" at 360 · a picture from 747 | `steps`: `title`, `text`; each item: `k` as the tag, `title`, `text`, `cta`, `img` — **changed**: the picture runs to the page edge and the row's height (owner's rule; the reference's 298×414 picture sits boxed in a 720 column). A picture under 720 wide is shown on the phone only, at its own pixels; on the desktop the row is words only | 3 rows, 3 pictures | 4 rows, words (pictures on the phone) |
| + | — | `team`: the small ruled cards of part 7 (portrait only when the person has one) · `credentials`, `faq`, `quotes`, `locations`: the ruled rows of part 10 without pictures | — | 11 people, 6 credentials |
| 11 | "trusted by": a ruled strip of square cells (city tag, small picture), sliding | `figures`: the same ruled cells: `v` 48 px caps, `l` 12 px | 3 | 5 |
| 12 | foot in halves (720/720): the left half again in halves — newsletter, social icons, fine print at the bottom; the right half three link columns (12 px caps head, 14/18 links) and a 14 px paragraph at the bottom with a drawn mascot | left: address, phone (+note), email, `contact.routes`, `place.hours`, `place.booking` or `contact.form` as a button, `place.social`, `foot.links` + `foot.legal` as 10 px fine print · right: `nav`, `links` (in two columns when there are more than six), `foot.text` at the bottom, `place.notices`. The newsletter form (no endpoint) and the mascot (the reference's drawing) are left out | ✓ | ✓ |

## Measures used
Gutter 26 (bar and foot 28); the reference's 180 column (12.5 vw) carries the titles; the grid is quarters: 360 / 1080 for
the shop, 443 / 443 / 553 for one group, 25 / 25 / 50 % for the rows, 720 / 720 for the foot.
Type: titles 48/48 bold condensed caps (36 on the phone); card names 20/20 (17 phone), small cards 15/15 +.225;
sentences 30/39 and 26/31.2 (22/27.5 phone); sub-titles 21/27.3; text 14/20, 16/22.4; small lines 12; fine print 10/13;
bar and buttons 13/13 +.26 bold caps. Buttons 31 high, radius 3, padding 9 10 7, arrow 18×9; price bar 29 high radius 2.
Rules 1 px: `--line` (24 % ink into the ground, the reference's 195-grey on white) and full ink where the reference has black.
Section paddings as measured: intro 33/300, collection 142 top, shop 135 + sticky 136, strip 138/160, close 142, rows 547.
Phone (the reference changes at 1024): bar 53, "Menu" opens a full panel of 36 px caps links; the name 85 px in the
first picture, which is then not fixed; the sentence at the bottom of the first picture; cards two across (two rows,
sliding); the range names become a sideways row of 36 px caps; small cards two across.

## Colour
The reference's relations, the client's palette: ground = `palette.ground`; ink = `palette.ink` (pushed to 7:1);
rules 24 % ink; grey buttons 11 % ink; the unpressed range names a grey held to 3:1 (they are 36–48 px; at smaller
sizes the grey is held to 4.5:1); tags 4.5:1. The reference's one strong colour is its orange panel — that place takes
`palette.accent`, with ground or ink on it, whichever reads.
Over photographs a veil toward the ground holds 4.5:1 (3:1 for the 30 px sentence) on the darkest pixel; the closing
picture's veil is at least 90 % under the words and falls off to the right.

## Fonts (open licence, Google Fonts)
- Helvetica Neue Condensed Bold (titles, bar, buttons, card names) → **Roboto Condensed 700**.
- Helvetica Neue 400/500 (sentences, text) → **Arimo 400/500/700** (metrically the Helvetica/Arial family).

## Motion — measured and reproduced
| measured on the reference | ours |
|---|---|
| bar `position:fixed`, clear with light links over the first picture; at scroll 800 of the 900 picture (`navbar--scrolled`) it takes the ground and dark links, `transition: .3s` | same threshold (picture height − 100), same 0.3 s (verified: clear at 790, ground at 810) |
| the name: `position:fixed; left:26px; top:136px; font-size:148px` → 48 px at the same threshold, `transition: .3s` | same (verified: 26/136, 120 → 48 px for a longer name); after the picture it stands on a ground patch so it does not collide with content passing under it |
| announcement: `animation: scroll 10s linear infinite`, 231 px wide | same, the duration grows with the text (0.3 s per letter, at least 10 s) |
| the opening sentence: each word in an `overflow:hidden` line rises from `translateY(30px)` to 0, one after another (first word done by about 1.5 s, last by about 3.8 s), easing out | each word from 34 px, 1.2 s `cubic-bezier(.16,1,.3,1)`, 0.12 s apart (verified) |
| card row: press → `swiper-wrapper` moves one card (360 px) with a slow-down curve, about 0.3 s | the row scrolls by one card width, smooth, snapping; arrows hidden when nothing overflows |
| card hover: a 1 px black frame (`::after`, inset −1) and the price bar filled black with light words, 0.3 s; product images at `scale(1.15)` all the time | same frame and bar (verified); our pictures are photographs, so they are not scaled up |
| grey buttons: hover fills black with light words, 0.3 s | same |
| range names: a press changes the shown range; colour 0.3 s; the count appears on the pressed one; column `position:sticky; top:136px` | same column, sticky at 136; the name of the group in view is marked as you scroll, a press goes to the group (the whole catalogue is on the page, so nothing is hidden behind a press) |
| colour cells: hover darkens the tag, the dot grows to 1.15 | a cell press shows its words below; hover darkens the tag and name |
| phone menu: "Menu"/"Close" text toggle, full panel, 0.3 s | same; Escape and a link close it |
Not reproduced: the location and newsletter pop-ups, the mega-menu with its pictures, search, cart drawer, the
colour/variant swatches inside a card, the auto-playing films (a client `media.video` goes into the closing picture).
Reduced motion: every transition and animation off; the announcement stands still, cut with an ellipsis.
Without scripts: the bar is solid from the start, the name stands at 48 px, every feature's words are shown, nothing is hidden.

## Departures from the reference, and why
- **Part 10's pictures** run to the edge and the row's full height instead of a 298 px box in a 720 column (owner's rule).
- **Part 4 (CAD drawings)** is left out: drawn product illustrations, not something a client supplies.
- **Part 7 shows every group open** under the sticky names instead of one range per press, because a visitor comes for the
  prices; the reference's own tab behaviour would hide all but one group.
- **Each photograph once** (niche addendum): the reference repeats product shots between its card row and its shop
  grid; ours shows the row's pictures once and the same products below by name and price only. A step's picture is
  kept for its row first.
- The name is the client's name in type, never a logo file at that size (the reference's is type too).

## Image slots
first screen 1 (≥1100×690; product → room → …) · collection 1 upright (≥425×525, product first) · photograph with the
panel 1 (≥1100×690, room first) · closing 1 (≥1100×590, exterior first) or `media.video` · card row: the group's own
item pictures · shop grid: item pictures not yet shown · rows: `steps.items[].img` (to the edge when ≥720 wide; phone
only and at own pixels when smaller) · bands in a long shop: free ≥1100×400 · people: own portraits only.
A `small` picture is never a backdrop or band. No `media.made` is read.

## Picture share (`tools/coverage.mjs`)
- reference: 45 %, per screen [100,63,71,33,86,32,8,29,61,18,0,0], 4 screens with a wide picture.
- shop1: 47 %, per screen [100,16,22,74,44,51,54,50,23,0], 5 wide (page 8,420 px, under 1.5× the reference) — passes.
- shop1 with its first five photographs only: 31 %, 3 wide. Without any photograph: 0 % (the page holds as type).
- school1: 21 % overall, per screen [100,1,39,80,36,0,0,0,0,0,29,58,0,0,0,0,0], 4 wide. Its page is 14,678 px, 1.45× the
  reference, so by the letter of the rule the overall share applies, and it is 24 points under. Over the screens that
  exist on both pages (leaving out the shop, people and credential screens) it is about 51 % against the reference's
  46 % without its shop screens. Every wide picture of the reference is there, in order (first screen, the photograph at
  the row edge, the panel photograph, the closing photograph). The 46 courses, 11 people and 6 credentials stay type:
  school1 has no further photograph of ≥1100×400 (its other 14 are 450×338), so rule (3) has nothing to place.

## Checks (final build)
`tools/shots.mjs` — shop1: 1440 height 8420, 390 height 8697; school1: 1440 height 14678, 390 height 19089; all four
with sideways 0, distorted 0, h1 1, errors []. `tools/legible.mjs` — ok for both (516 / 1554 line readings).
Also checked by hand: keyboard focus is a 2 px ink outline; reduced motion turns every animation and transition off;
without scripts nothing is hidden. The bar was measured at 1025, 1100 and 1280 with a 40-character call: no overlap.
Variants (scratch copies; generator kept in the session scratchpad): 1/3/5 plans, 2/9 features, 1/6 steps, a 12-word h1
with 40-character labels, faq added, no faq, no photographs, first five photographs only — 24 pages, all clean and legible ok.
