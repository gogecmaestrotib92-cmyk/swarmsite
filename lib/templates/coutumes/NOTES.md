# coutumes — a shop template rebuilt from coutumes.com/fr

Measured 2026-11-12 at 1440×900 and 390×844 (`ref/anatomy.json`, `ref/structure.json`, `ref/clean-*.jpg`; the cookie
panel was closed with "Refuser"). Test clients: shop1 (primary), local1.

## Cut-outs — said plainly
The reference does **not** depend on cut-outs. Its product shots (`packshot-*.jpg`) are ordinary photographs of the
piece lying on a pale textured ground, set 4:5 edge to edge with `object-fit: cover`; there is no transparency, no
blend mode, no shared background behind them. Any ordinary product photograph fills the card. What the reference has
and a small shop may not: a *uniform* packshot series (same ground, same light) — with mixed photographs the rail is
less even (see shop1: one dark-green, one cream, one aubergine picture); a film for the band; lifestyle pictures of
people wearing the product for the opening and the tiles.

## Sections of the reference and the data each takes
| reference (1440) | measures | ours |
|---|---|---|
| bar, fixed, 72 high (56 phone); clear with white type over the opening, white with black type after it, 0.25 s; brand left, links from x=304 with 40 gaps, right group | 16/24 serif | `brand`, `nav`, right group `signin` + `cta` (the cta is left out of the bar when the row would not fit and it equals `hero.primary`, which stands under the opening paragraph). Below the width at which the row fits (never under 1180): three-line button left, brand centred, full-screen panel of 18 px rows with hairlines, as the reference's phone menu |
| opening 0–900: two photographs 720×900 side by side (one on the phone), title in condensed capitals 172.8 px (12vw; phone 89.7 px = 23vw), line-height .8, tracking −.021em, centred, standing on the lower edge with the letter feet just cut, in the display colour; whole opening is one link | | two photographs chosen by role and size; `hero.title` as the h1 (the reference hides its h1 and shows an h2; ours shows the h1), size fitted so the title sets in at most 3 lines (phone 6): shop1 10.25vw; link `hero.primary` |
| paragraph 900–1304: 28/32 serif, −.04em, centred in 720, one italic underlined 14 px link, 104 above and below | | `hero.text` (+`text2`), link `hero.primary`. The reference hides this paragraph on the phone; ours keeps it (18/22, left) because it is the client's opening sentence |
| rail 1304–1969: head 56 high (h2 28/32 left at 24, 11 px wide capitals link right), cards 350×441 (4:5, cover) with 8 gaps and 8 inset, white chip top-left, caption name 12/16 + grey 11/14.3 note left and 12 px sans price right, 1 px progress line 19 below; free horizontal drag | phone: card 276×348, h2 18/24 | first `catalogue` group: h2 = group name, right link = the group's own count text ("7 PRODUCTS") to the group page, a card per item that has a picture (chip = `state`, price = the client's string, link = the item's own page `h`). Items without a picture follow as the caption alone on a hairline, in the same four columns. No cart |
| band 1969–2797: full-bleed film 1440×828 (57.5vw; phone 390×488 = 125vw), darkened .22, title 48/55 white centred, 14 px condensed capitals link under it | | `statement.title` over one landscape photograph (or `media.video` when the client has one), link `hero.secondary`. `statement.text` follows as a second centred paragraph (the reference's paragraph part, used twice) |
| — | | further `catalogue` groups: as the rail; a group none of whose items has a picture and that has a photograph named for it (`group.img`, or a free photograph whose file name shares a word with the group's name) gets the band part as its head (shop1: Hand Lotion) |
| tiles 2797–3395: h2 + four 350×438 pictures, each with its name in the condensed capitals 80.5 px (5.59vw; phone 63.5 px) on the lower edge, darkened .12 | | `steps` (name = `k`, link = `cta.h`), then `projects`. Under each tile the step's `title` and `text` in the caption style (the reference has no words under its tiles; ours keeps the client's copy). Three or fewer tiles share the full width (3 → 469×587) |
| — | | `team`: `team.text` as a centred paragraph, people as cards (portrait 4:5, name, role, text); a person without a portrait in type only. `quotes` (3 at most): the first over a free landscape photograph if one is left, the rest as centred paragraphs with the name in small capitals |
| — | | `plans` and `faq` (the reference's home page has neither): plans as hairline cells in the four columns (name 28 px, price, rows, link), questions as the phone menu's 18 px hairline rows that open |
| row 3395–3509: four statements in 11/14 wide capitals, centred, 40 above and below | | `credentials`, then `trust` (up to five columns) |
| foot 3509–4101 on the display colour with a paper grain: right half (from x=732) a small-capitals line, an 18 px ruled line with a capitals action at its right end, a 12 px note, three columns of 12 px links under 11 px capitals heads; the name very large bottom left (616 wide); legal links with bullets bottom right | | capitals line = `close.title`; ruled line = the address (else phone, else e-mail) with `close.cta` at its end — the reference's e-mail field becomes the address, no form; note = `close.text`; columns = opening hours (`place.hours`), contact (phone with its note, e-mail, booking/form/routes, social), then `locations` or the first eight `links`; `brand.name` large; `foot.links` + `foot.legal` |

Words the build itself needs (menu, close, view all, opening hours, contact, skip) come from a small table per
language; everything else is the client's copy. `alt` is only ever an `alt`.

## Colour
The reference: white page, black type, one light saturated colour (amber #f9af26) for the largest type and the foot.
Ours: `palette.ground`, `palette.ink`; the display colour is the lightest saturated colour among accent and extra,
lightened along its own hue until its luminance is .55 (shop1 #bddbd3 as given; local1 #647e65 → #bcc7bc).

## Fonts (open licence, Google Fonts)
- Plaak 3 (condensed display) → **Saira Extra Condensed 800** — "DEUXIÈME DROP" at 172.8 px sets 806 wide against the reference's 764.
- Exposure (text serif) → **Literata** (optical sizes) — the first paragraph line sets 549 wide against 560.
- Plaak 6 (wide small capitals) → **Archivo** at 112 % width, 600.

## Motion — measured and reproduced
- Bar: `position: fixed`; transparent/white type until the opening has passed under it (measured: clear at y=200, white at y=700 with a 900 px opening), `transition: background-color .25s, color .25s`; goes white when a link in it is hovered. Reproduced: switches at opening height − bar height (shop1: 828), .25 s, white on hover and on keyboard focus. Without scripts the bar is simply solid.
- Opening title and pictures do not move with scroll (sampled at 0/300/600: same document position). Nothing is pinned, nothing reveals on scroll. Reproduced as still.
- Rails: Swiper in free mode, a 1 px scrollbar whose thumb is the visible fraction (565 of 1408). Reproduced with native horizontal scroll, mouse drag, and a 1 px line updated from the scroll position; the line is absent when everything fits.
- Pictures fade in over .25 s on load (`pc-fade`). Reproduced for lazy pictures only when scripts run.
- Film in the band: autoplay, muted, loop. Reproduced only when the client has `media.video`; under reduced motion it does not start and gets controls.
- Cards and tiles: no hover change measured (opacity, transform, filter unchanged). Ours: the caption name underlines.
- Reduced motion: all transitions off (measured on ours: bar transition 0 s, no fading pictures).

## Not transferred, and why
- The per-letter variable axis ("EXPO") on the reference's paragraph: belongs to its commercial face.
- The emblem top-left of the foot and the drawn wordmark: its marks. The name is set in Literata 800 instead.
- The newsletter field, search, language/currency, cart: no backend in a template; the ruled line carries the address.
- The mega-menu under the bar: the contract's `nav` has one level.
- The reference lays its type straight on the photographs (opening darkened 0, tiles .12, band .22). The readability
  gate requires 3:1 / 4.5:1 on the brightest pixel, so ours darkens more: about .7 toward the dark ink under the
  opening title and under the bar, .62 across the middle of the band, .7 under a tile's name. This is the visible
  difference in the pairs: our pictures are darker where type lies on them.
- Tile names stand on the edge uncut (the gate reads a cut line as overflowing on to the page ground).

## Pictures (the client's own photographs; no made pictures; each placed once)
Order of placing: a priced product keeps its own picture → stories (`steps[].img`) → projects → unpriced catalogue
items → people → the opening (2: at least 1400×1200, not small, not people) → a group's own band → the band
(landscape ≥1600 wide; shopfronts last) → a story or project whose picture went to a product takes a free photograph
whose file name shares a word with it, else a free one of the same role (shop1: "Sustainability" lost the plant-pot
candle to its product card and stands on the cotton stems — a stand-in, the one place where a label and a picture
are paired by the template and not by the data) → an unpriced item without a picture takes a free photograph named
for it (local1: Kitchens, Doors, Windows) → the first quote.
shop1: 11 of 17 placed (band: the dried bunches); unused: the two 2400×678 panoramas (too flat for any slot), the three
exteriors (two small; the black-and-white front has its sign where the band title lies), the small people picture.
local1: 17 of 20 placed.
With no photographs: see needs.json (`holds_without_pictures: false`).

## Picture share (tools/coverage.mjs)
reference 80 % [100,49,84,73,100] · shop1 74 % [100,51,84,69,73,67,100] · local1 54 % [100,23,59,53,80,52,22,22,100].
The last screen reads 100 in all three because the foot carries a grain texture as a background picture (the
reference a PNG, ours an inline SVG noise); without the foot: 76.5 / 74 / 51. shop1 is 6 points under the reference
with the foot, 2.5 without; local1 is far under: it is a service with long texts, shown in the reference's text parts.

## Checks (final build)
shots.mjs — shop1 d: height 5455, sideways 0, distorted 0, h1 1, errors [] · m: 5054, 0, 0, 1, [] ·
local1 d: 7648, 0, 0, 1, [] · m: 6837, 0, 0, 1, []. legible.mjs — shop1 ok (268 lines), local1 ok (387 lines).
Keyboard focus: 2 px outline in the current colour on every link (tabbed through twelve stops). Scripts off: bar solid,
all text and pictures present. Also rendered without error on the other nine data files in data/ (not looked at, except
sportbot: its plans and questions show; its screens would be cropped in tiles — not a template for software).
