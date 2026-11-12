# iip — notes

Reference: https://illinoisinnocenceproject.org (a non-profit, type-led). Measured 2026-11-12 at 1440×900 and 390×844 with
`tools/anatomy.mjs`, `tools/shots.mjs` and the Playwright probes in `probe/` (`probe.mjs`, `probe2.mjs`, `probe3.mjs`; their
printed readings are in `probe/probe3.txt`, screenshots in `ref/`). Test clients: `charity1` (primary), `person1`.

Three kinds of statement are kept apart below: **measured** (read off the live page), **reproduced** (what the template does),
**chosen** (where the reference gave no answer for a non-profit's data and something had to be decided).

## What the reference is, and which page each part comes from
The home page is short (4 631 px at 1440): a thin bar, a header, one accent panel with the title, four alternating
picture rows, the foot. Its opening was a dated anniversary graphic on the day of measuring (a "25" and a ribbon over a
texture picture); as instructed the *build* of the panel is taken and the graphic is not. Prices, people, questions and
addresses live on its inner pages, so the parts a client's one page needs were measured there:

| # | Our section | Reference part (page) | Client data |
|---|---|---|---|
| 1 | bar | bar: 32 px, right-aligned 14/700 links, one darker button with the triangle (home) | `contact.phone` (or `place.phone`), `signin`, `cta` |
| 2 | header | 88 px, mark left at 56, links 19.2/500 right (home) | `brand` (name in type when there is no logo), `nav` |
| 3 | opening panel | accent panel inset 24, 750 tall, title 86.4/0.9/−0.03em in a 444 px column, lead 20/28, button at the bottom-left 56 above the edge, imagery over the other two thirds (home) | `hero.kicker,title,text,primary,secondary,note`; one landscape photograph |
| 4 | line of standing facts | the small-capital label type 19.2/700 (home rows) | `trust[]` |
| 5 | picture rows | `block_text-img60` 680/680 gap 32 picture right; `-reverse` 835/525 picture left; rows 64 apart; h3 43.2/1, lead 20/28 indented 40, text blocks 24 apart (home) | row 1: `statement` + `hero.text2` + an upright photograph; row 2: `team` when it is one or two people (portrait only when it is that person's) |
| 6 | people grid | 4 × 342 squares, gap 8/48, name 700 + role (about) | `team` with three or more people, or `team.groups` |
| 7 | tinted slanted band | `section-color r1`: slanted ground, 617/823, 64 px display type, picture 823×673 clipped `polygon(10% 0,100% 4%,100% 100%,0 95%)` and running off the right edge (advocate) | `figures[]`; one landscape photograph |
| 8 | catalogue | lead: h2 60/600; story rows 680/680 gap 32, name 43.2, text 16/22.4, bulleted list, button, picture as tall as the row (advocate "cases"); then the card part of 12 (take-action) | `catalogue` — the first three items with their own picture are story rows (full text); every further pictured item is a card with its own picture (3:2, as the reference's card), name, price, note and the first sentence of its text — the rest of the text, the price table and the list open in place under a plus (native `<details>`); items without a picture are a two-column list in the card type (30.67/700). Cards stand 4 across at 1440 for 7 or 8 items (3 for 3, 5, 6, 9; 2 for 2 or 4), 2 across at 390 |
| 9 | picture strip | three pictures 400 tall across the page (advocate gallery, take-action "alumni") | three free landscapes between the first and second catalogue group — only when the catalogue has no cards (three pictured items or fewer); with cards the catalogue already carries a picture every screen |
| 10 | plans | card part (see 12) | `plans` (neither test client has any; tried with 1, 3 and 5) |
| 11 | dark slanted panel | `about-us`: dark slanted ground, text column 560 at 48, h3 43.2 white, 16/22.4 list with bold lead-ins, a stack of photographs 654 wide off the right edge, 2 px apart, reaching past the band top and bottom (about) | `features`; two or three free photographs |
| 12 | cards | "Get involved": h2 60, 3 × 432 gap 48, label 16/700 caps, picture 3:2, h4 30.67/1.2, text 16, button (take-action) | `steps` (k → label, img → picture only when every step has one) |
| 13 | dark band with a picture half | `section-color r2`: dark slanted ground, picture 720×720 from the left edge clipped `polygon(0 3%,93% 0,100% 100%,0 100%)`, text right (advocate) | `quotes[]`; one free photograph |
| 14 | reach us · questions | 656/656 gap 80; rows of a 32 px plus and a 24/31.2 question, 32 apart (about) | `contact` left (phone 60/600, email 30.67/700, routes), `faq` right |
| 15 | dark band above the foot | "Apply": dark ground, padding 64/48/80, heading in a pale tint of the accent, two columns gap 80, address in 16/700 (advocate) | `place` + `locations[]`, then `credentials[]` |
| 16 | foot | accent ground, top edge slanted (30 px at the left, 4 at the right), mark and address left (536), right 872: 86.4 px line, lead 20/28, button, link columns 20/28, small print 14 (home) | `brand`, `foot.text`, `close.title,text,cta`, `links[]` with their descriptions (or `nav`), `foot.links`, `foot.legal` |

Order on our page: 1 2 3 4 5 6 7 8(9) 10 11 12 13 14 15 16. A section whose data is missing is left out whole.

Page height after the change of 2026-11-12 (story rows for three items, cards for the rest, no strip beside cards):
charity1 11 092 px at 1440 (was 14 926) and 14 987 at 390 (was 17 629); person1 8 134 at 1440 and 11 225 at 390.

## Measures used (1440 → 390)
Type: h1 86.4/0.9/−0.03em/700 → 40 · h2 60/1/600 → 34 (chosen; the reference's phone h2 was not read) · h3 43.2/1/700 → 28 ·
band display 64/1/700 → 34 · h4 30.67/1.2/700 → 22 · label 19.2/1.2/700 caps → 13.6 · lead 20/28 → 16/22.4, first-line indent
40 → 24 · text 16/22.4 · nav 19.2/500 · bar 14/700 · small 14/19.6 · button 18.4/700, 52 tall, 16 left padding, triangle 32×52
flush right. Page gutter 24 → 8. Panel inset 24 → 8, padding 32/43.2 → 28/17.6. Radii: 0 everywhere (measured 0).
Title size steps down with its length (chosen; the reference's title is 26 characters): ≤26 → 86.4, ≤40 → 72, ≤64 → 60,
≤110 → 48, longer → 40 (phone 40/36/32/28/25). A title of 40 characters or fewer keeps the reference's proportion (type column
a third, picture 64 % of the panel); a longer one gets 43 % and the picture 54 %. Without a photograph the title is one step
larger and the panel 600 tall.

## Colour
The reference's relations, applied to the client's palette: page = `ground`; type and the dark bands = `ink`; panel, buttons,
foot = `accent` with white (or ink) on it, whichever reaches 4.5:1; the bar's button is the dark colour, as in the reference;
the pale band is the accent at 16 % on the ground (the reference has a lilac and a lime band; a client palette has no second
or third hue, so both roles take the tint — chosen); the heading on the dark band is a pale tint of the accent; the foot's
big line is ink when ink reaches 3.2:1 on the accent (person1) and the on-accent colour when not (charity1: 2.2:1).
Small accent-coloured type on the ground (labels, prices, the plus) is darkened toward ink until it holds 4.6:1 on the
ground *with a hairline under it* (charity1 #2b6cb0 → #2c5c91, person1 #0073aa → #05567c).

## Font
TASA Orbiter — the reference's own face. It is open-licence (SIL OFL) and served by Google Fonts, so it is used itself;
there is no stand-in. Weights 400–800 through the variable file.

## Motion
| Measured | Reproduced |
|---|---|
| Four hairlines (1 px, a lighter accent, rotate ±20°, one vertical at 65.9 %, one long diagonal) in two `position:fixed` layers — behind the page at .3 `multiply`, in front at .2 `color-dodge` — so they hold still while the page moves | yes, same positions and blends. Departure: the accent grounds (bar, panel, foot) and every button stand **above** the front layer, because a front line through white type on the accent read 4.0:1 on the gate |
| Nothing is pinned; the header scrolls away (`position: relative`); no parallax — picture and heading positions sampled at six scroll offsets did not move, opacity 1 before entering | yes: nothing pinned, no reveal on scroll for sections |
| Title: each line rises 9 px and fades in; at 200 ms it stood at 9.3 px / .54, done by 600 ms | whole title, 9 px, .6 s, CSS only (no line splitting) |
| Button hover: a second triangle (40 wide) slides in from −48 px at the left, the label block shifts +48 px so the right triangle leaves through the clipped edge, colours swap; ≈ 97 % done at 150 ms, settled by 300 | yes, .3 s `cubic-bezier(.2,.8,.2,1)`, only where a pointer hovers. Colour swap reproduced on the panel's light button; the accent button keeps its colours (its hover colours were not read) |
| Foot line: every letter from opacity 0 / scale .8, about 1 s each, about 40 ms apart, when it enters | by **word**, 1 s, 120 ms apart, behind an `IntersectionObserver`; words stay whole so nothing is cut into fragments. Without script the line is simply there |
| Questions: plus turns 45°, answer opens over ≈ 400 ms, question takes a second colour on hover | yes (`<details>`, height animated .4 s by script; opens instantly without it) |
| (no reference part) | a catalogue card's further text opens with the native `<details>` toggle, no animation; the plus turns 45° as on the questions |
| Phone menu: a full-height accent panel off the right edge (`translateX(390)`), opened by a "Menu" button with the triangle | `<details>`: accent panel slides in from the right .4 s; Escape and a link close it. The reference's opening timing was not read (the probe's click did not open it) |
| Page-transition overlay on load, gallery ticker (pictures drifting sideways) | not reproduced: one page has no page change; a ticker needs each picture twice |
| Tilt: in the colour bands the text block and pictures are rotated 2–8° | not reproduced: the band's edges and the picture's cut keep the slant, the type stands level (chosen — rotated body text reads worse and nothing in the client data asks for it) |
`prefers-reduced-motion`: all animation and transition off, the foot line shown (checked: animation-name none, opacity 1, 0 s).

## Owner's rules against the reference
- **Pictures beside text.** The reference's own colour bands already run their pictures off the page edge at full section
  height (kept as measured: 7, 11, 13). Its home rows and story rows stop 24 px short of the edge; ours run to the edge and are
  as tall as the row (converted: 5, 8). The opening picture fills its side of the panel top to bottom and to the panel's
  edge; the panel itself is inset 24 px as in the reference. Card pictures stand above their text as in the reference.
- A picture is never shown wider than its own pixels (`max-width` = natural width on every slot).
- No `alt` is used as copy. No word is invented: where the reference has a word the data lacks ("Read more", "Contact",
  "Return to top") the row's button carries the item's own name, the contact block starts with the number itself, and the
  top link is an arrow. One word is supplied by the template: the phone menu's "Menu", by language.
- No form. Donate / adopt / volunteer are links to the client's own pages.

## Photographs with lettering in them
A photograph with words in it (a sign, a caption, a marker burnt in) is never cropped: a crop cuts the words mid-word, as it
did with person1's hero.jpg ("YOU ARE HERE") in the first build. A picture counts as lettered when the data says
`lettering: true` (and not when it says `false`); when the data says nothing, when its alt names lettering (words, letters,
sign, text, writing, caption, inscription, banner, placard, poster, logo, label, "reads", "says", slogan, headline,
watermark). A lettered picture is given only to a slot that keeps the picture's own proportion — today the first picture
row (statement), where it stands whole; every cropping slot (opening panel, figures band, dark-panel stack, quotations,
strip) passes it over. Checked over all eleven test clients: it flags person1/hero.jpg only (an earlier pattern with "read"
also flagged corp1's "read a drawing"; narrowed to "reads").
**Capture should flag:** `media.photos[].lettering: true` for any photograph with legible words, numbers or a logo in it,
from looking at the picture, not the alt (an alt is written for a reader and may leave the words out); optionally
`lettering_box: [x, y, w, h]` in the picture's pixels so a template could crop around it instead of refusing the crop.

## Image slots (the client's own photographs; no made pictures)
Drawn in this order, each photograph once: `hero` (landscape ≥ 900 and ≥ 750 tall; else any ≥ 640 wide and ≥ 750 tall —
the slot is never wider than the picture's own pixels) → `statement` (upright ≥ 760, else any) → `figures`
(landscape ≥ 900) → `features` ×2, ×3 when the text is long (≥ 700) → `quotes` (≥ 760) → `strip` ×3 (landscapes ≥ 700, only
when three are left and the catalogue has two groups). Catalogue items, steps, people and credentials keep the pictures the
data gives them. Roles `portrait` and `product` are never drawn for a general slot; nothing wider than 2.6:1 is drawn.
charity1: 6 of 19 free photographs placed (calf → panel, lamb → row 1, sheep → band, hens and rabbits → dark panel) + all 10
catalogue pictures (3 rows, 7 cards). person1: toprope.jpg (770×769, black and white) → panel at its own 770 px width,
hero.jpg (lettered) → row 1 whole at 1.74:1, portrait → row 2, four step pictures; nothing left for the figures band, dark
panel or quotations (they are type).
With no photographs at all: every picture slot closes and the page is type on the same grounds (see needs.json).

## Checks
- `tools/shots.mjs`, both clients, 1440 and 390: no sideways scroll, distorted 0, one h1, errors [] (lines in the report).
- `tools/legible.mjs`: see `probe/legible-all.txt` for both clients and every variant.
- Keyboard focus: 3 px outline + a 7 px ring in the ground behind it (two-tone, visible on ground, accent and dark) — read on
  the first twelve tab stops. No script: page complete, questions and menu work (`<details>`), foot line visible.
- Picture share: reference home 46 % (75, 49, 54, 45, 16, 0); charity1 27 % (46, 42, 27, 36, 47, 44, 44, 19, 28, 0, 0, 0, 0);
  person1 16 % (47, 40, 35, 0, 0, 2, 23, 0, 0, 0). Our pages are 2.4× and 1.8× the reference's height, so the revised rule
  applies: over the shared sections (panel + rows) ours reads 46/42 and 47/40/35 against 75/49/54/45. (Before the change
  charity1 read 34 %: the strip and seven full-width story rows were picture; the cards keep every animal's photograph but
  smaller.) The first
  screen is short of the reference by 21–29 points: the reference lays a texture picture under the whole panel and a graphic
  over two thirds of it; ours has one photograph over 54–64 % of the panel and flat accent under the type. Not closed — laying
  the photograph under the type as well would only move the same picture behind the accent field.
- Variants (scratch copies, `probe/variants.py`, checked by `probe/vcheck.mjs`): 1/3/5 plans, 2/9 features, 1/6 steps, 12-word
  h1, 40-character buttons, no faq, no photographs (both clients), three photographs, a dark palette — no sideways scroll, no
  text past the window, no overlap of sibling text blocks, one h1, no errors at both widths.

## What could not be transferred, or was not
- The opening graphic (a campaign piece) and the texture under it.
- The mark: neither client has a logo file, so the name is set in type in the header and foot.
- Social icons in the bar and foot (the reference's icons are not taken; routes are text links in the contact block).
- Two- and three-colour bands (lilac, lime): one tint.
- Rotated text, ticker, page transition (above).
- Sub-menus in the header: `nav` is flat.
- The contact form: the contract has `contact.form{h,t}` only as a link.

## Known weak points
- person1's opening panel now carries a 770 px square picture (no larger unlettered landscape is free); it stands at its own
  width, so the panel shows 770 of its 890 px of picture room as photograph and the rest as the picture's edge.
- charity1 is still 2.4× the reference's height (11 092 / 14 987). The rest is content the reference keeps on sub-pages: seven
  volunteering roles, five injured-animal steps, seven questions, two sites, nine links with descriptions in the foot.
- A card's first sentence is its summary; a text with no sentence end shows whole in the summary.
- Under 1100 px the header's links fold into the menu (chosen; the reference folds at its own breakpoint, not read).
- Widths between 760 and 1100 and above 1440 were not looked at.
