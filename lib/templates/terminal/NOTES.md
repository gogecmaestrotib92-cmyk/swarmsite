# terminal — notes

Reference: https://terminal-industries.com (home), read 2026-11-12 at 1440×900 and 390×844. No cookie wall appeared; nothing
was accepted. Measurements: `ref/anatomy.json`, `ref/dump-*.txt` (boxes, type, spacing, radii, transitions per section),
`ref/ref-*.jpg`, `ref/hero-*.jpg`, `ref/pair-*.jpg`. Probe scripts are in `probe/` (run with `tools/run.sh node terminal/probe/<name>.mjs`):
`hero.mjs`, `hero2.mjs` (the pinned opening), `dump.mjs` (any section's tree with computed styles), `clip.mjs` (the notch
shapes' measures), `motion.mjs` (walk, headings, hovers, accordion, card row), `mob.mjs` (phone build), `pairs.mjs`,
`audit.mjs`, `look.mjs`.

## Sections of the reference, and the data each takes

| # | Reference (measured at 1440) | Ours | Data |
|---|---|---|---|
| 0 | Glass bar, fixed 46 from the top, centred, 939×78: black 30 % + blur 30, r8, pad 18, gap 24; logo 112; links 14/450 +0.03em, gap 18; three buttons 99×42, mono 11/600 +0.136em, r8 (accent / white / grey). Phone: 350×64 at top 25, pad 20×26, logo + two-line burger | same build; two buttons (accent, paper). Bar ground is the palette's dark at 70 % (see "Differences") | `brand`, `nav`, `cta`, `signin` |
| 1 | Pinned opening, section 2700 (3 × viewport): a full-bleed film scrubbed by the scroll; three statements 82.5/0.95 (−0.018em), white, centred in a 900 box whose bottom edge stands 134 above the viewport's bottom; each is set letter by letter, the newest letter in the accent, then taken away from its start. No heading is visible at scroll 0. A 48-high strip in the page ground with a notch (x 222→1218, 40 deep) closes the section | same, with made landscape stills in place of the film (one per statement, cross-faded, slowly enlarged by the scroll) | `hero.title` (the h1), `hero.text`, `hero.text2` · `media.made.land` |
| 2 | Centred 70/1.0 heading over a grid of 111-px logo cells with hairlines and corner marks | built plainly (cells, no heading — there is no data for one); **left out for both clients** | `logos` (empty) |
| 3 | Pad 120/70/90; h2 70/1.0 −0.051em in a 900 box, 72 below; three cards gap 24, ground 6 % ink, r24, pad 40, gap 32: mono 13 uppercase +0.18em label "01 …", h3 22.5/1.46, text 18/1.4 +0.02em at 70 % ink, picture 334×208 r12 with 1-px border (cropped), button full width 59 high, ink 5 %, r8, 11/600 +0.18em | same card; the picture tile is taller and the client's picture stands whole on the page's landscape held quiet (see "Owner's rules") | `steps.title`, `steps.items[k,title,text,img,shape,cta]` · `media.made.land` |
| 4 | Centred block pad 180/70 (grey 20-px label + h2 70), then a row pad 56/70, two columns of 630, gap 40. Left: label, h2 38, ruled fields (label 15, value 16, 1-px line at 20 % ink, row gap 24, column gap 37). Right: deep card r8, 722 high, notch in its top edge (x 297→585 of 630, 30 deep) and in its left edge (y 310→556), pad 44/36/36/44: 34-px line, amount 44, 20-px label, a list of rows (label 16 left, value 22 right, 40 high), an inner box with a field and a button | h2 70 = the statement's title; left: its text at 23/1.26 and the trust lines as ruled rows; right: the same notched deep card with the first figure at 44 and its label at 20, the other figures as rows, the call-to-action as a full-width button | `statement.title/text` · `trust[]` · `figures[v,l]` · `cta` |
| 5 | Centred block (label, h2 70, text 18/1.4 in 880, 54 below the heading), then a walk: section 3101 for four entries; left column at x 165, 435 wide, entries 34.5/1.2 weight 450 (bold title, blank line, text), 344 apart, starting 240 down; a two-digit mono counter at x 134 pinned at mid-height; right: a pinned 695×830 panel (top 35, r10, notch in its left edge) with one film per entry, cross-faded 0.5 s | heading block the same; **the panel becomes the backdrop of the whole walk** (see "Owner's rules"): one pinned picture across the section (margins 17, top 35, viewport − 70 high, r10), the entries walk over it at the reference's x, size and spacing; counter the same | `features.title/text/items[t,d]` · `media.made.land` |
| 6 | Centred block (label, h3 46/1.2, text), tabs row pad 0/52: tabs 58 high, pad 12/18, mono 13/600 +0.18em, r8 (active: ink 5 %; others: 1-px border), two arrow buttons 58×58 r8; a row of cards gap 20, r20, 725 high: the open one 890 wide with a blurred picture + 30 % black, pad 80/82/28/60, mono label, title 46, text 23/1.46, button 210×60 bottom right; closed ones 580 wide, flat grey, label + title, the picture appearing on hover | tabs, arrows and cards the same; the card's title is the link's sentence, its screen stands whole under the title, the button carries the link's name. No heading block (no data for one) | `links[t,d,h]` · `media.screens[i]` · `media.made.land` (blurred in CSS) |
| 7 | Centred heading 70 over a second logo grid | left out (same data as 2) | `logos` (empty) |
| 8 | Full-bleed photograph 900 high with a notch in its bottom edge; quotation 34.5/0.96 centred in 852, name/role 17.25/450 | built from the same measures on a made landscape; **left out for both clients** | `quotes` (empty) |
| 9 | Contact block pad 80/70, gap 56: two-line heading 48/1.05; grid 630 + 630 gap 40; left 23/1.26 text with a short list; right a deep card 540 wide, r17, pad 48, fields on 1-px rules, button 60 high | **plans, on this block's build** (the reference has no prices): heading 48, text 18 centred, deep cards r17 pad 48 in the two columns — mono name, price 44 with its period at 20, line 23, the rows on 1-px rules, button 60 high (accent on the marked plan, paper on the others); the note below. One plan only: the reference's own layout (text left, one 540 card right) | `plans.title/text/items/note` |
| 10 | Pad 90/0; grid 523 + 653, gap 124, pad 0/70; h2 34.5/1.2 left; right: tabs, then rows — summary pad 32/0, 22.5/1.46, 24-px plus turning 45°, answer 18/1.4 pad 0/32, a 1-px accent line fading at both ends under each row | same, without the tabs (the data has no groups) | `faq.title/items[q,a]` — left out whole when empty (automateed) |
| 11 | Deep panel with a notch in its top edge (x 204→1236, 30 deep), pad 230/70/20: line 70/0.95 centred in 825 (the page's only h1 on the reference), glass button 59 high 67 below; 225 lower: logo 37 high with a 13/1.5 note at left, two link columns from x 618 (20/1.46) with mono 11 labels, a third column at x 1056; 12-px copyright row 95 lower | same; the line is an h2 (the h1 is the opening); `close.text` added at 18/1.4 between line and button; columns without labels (no words for them) | `close` · `brand` · `foot.text/legal/links` · `nav`, `links`, `signin`, `cta` (each link once) |

Not placed anywhere: `hero.kicker`, `hero.note`, `hero.primary`, `hero.secondary`, `media.phones`, `media.video`,
`media.photos` (other than the pictures `steps.items` point at) — the reference has no slot of their kind (its opening has
no buttons and no small label, and it shows its product only as film).

## Measures used (desktop → 390)
- Type: 82.5/0.95 → 58 (68 → 44 when a statement is longer than 70 characters) · 70/1.0 −0.05em → 40 −0.03em · 48/1.05 → 40 ·
  46/1.2 → 24/1.46 · 44 → 40 (amounts) · 34.5/1.2 → 20/1.2 (walk) · 23/1.26 → 20 · 22.5/1.46 → 24 · 18/1.4 +0.02em ·
  16/1.35 · mono 13 and 11, uppercase, +0.18em (bar buttons +0.136em).
- Margins 70 → 20 (grid wrappers 52 → 20); card gaps 24 → 20; card pad 40 → 32; radii 8 (buttons, bar, tabs), 10 (pinned
  panel), 12 (tile), 17 (plan card), 20 (row cards), 24 (three cards).
- Phone build as measured: bar 25 from the top; statements 58 px, bottom edge 60 above the viewport's bottom; one card
  per row; figures card full-bleed with the notch at the top right; the walk becomes a sideways-swiped row (298-wide
  entries at 20 px, a 2-px progress line below); row cards 350 wide, min 438 high, pad 24, all open, arrows below right;
  foot one column, links in two.
- Notches are drawn by this template as clip polygons from the measured positions, depths and shoulder runs (smooth
  shoulders); the reference's SVG paths were read for their numbers only.

## Font stand-ins
- Reference text face: **Suisse Int'l** (commercial). Stand-in: **Geist** 400–600 (SIL OFL, Google Fonts) — a Swiss
  neo-grotesque of the same kind, close in width and x-height. Tracking kept as measured (−0.05em at 70).
- Reference label face: **Geist Mono** — itself open-licence (SIL OFL), so it is used as is.

## Colour
Client palette in, relations kept: page = ground; text = ink; cards = 6 % ink; quiet text = 70 % ink raised until it reads
4.6:1 on the card ground; the deep panels (figures card, plan cards, close and foot) take the ink colour on a light page
(automateed: navy) and, on a dark page, the first dark `palette.extra` colour that separates from the ground (sportbot:
deep green `#0e4b33`), with whichever of ink/ground reads better as text; buttons: accent / paper / 5 % ink; the hover
fill is the palette's dark with the accent as text.

## Motion — measured, and what is reproduced
| Measured on the reference | Reproduced |
|---|---|
| Opening pinned for 1800 px (2 × viewport); each statement owns 600 px (0.667 viewport): letters appear in order from 17 % to ~72 % of its span (`opacity .1s`), the newest in the accent, hold, then disappear from the start between ~76 % and 100 %; the film is scrubbed by the scroll; after the pin the picture leaves at half speed | yes — same spans; stills cross-fade (0.7 s) at each statement and grow 1 → 1.1 over the pin; half-speed exit |
| Headings (`animated-strong`): words go from pale grey to ink one after another as the heading enters | yes — `color .45s cubic-bezier(.39,.575,.565,1)`, 45 ms apart (the reference's own stagger was too fast to time exactly; a pass through the accent tint mid-way was seen and is not reproduced) |
| Buttons: a dark panel rises from below (`translateY 100% → 0`, `.3s cubic-bezier(.39,.575,.565,1)`), the label takes the accent | yes; plus a press state (scale .97) — the reference has none; added per the owner's "the page answers a press" |
| Bar links: colour to the accent `.3s cubic-bezier(0,0,.58,1)`, a 5-px accent dot scales in at the left | yes |
| Walk: an entry's letters go from grey to ink (`color .4s`) as it rises from ~56 % to ~10 % of the viewport height; the panel's film changes with the entry (`opacity .5s cubic-bezier(0,0,.58,1)`); the counter's digit column rolls 28 px per entry; panel pinned at top 35 | yes — letters from 50 % to full strength of the text colour (see "Differences"), backdrop cross-fade 0.5 s, rolling counter |
| Card row: a tab or arrow opens a card — widths 580 ↔ 890 over `.6s cubic-bezier(.19,1,.22,1)`, the row scrolls it to the left edge; a closed card shows its picture on hover (`opacity .9s`, `scale 1.2 → 1` over 1.2 s, same curve) | yes; arrow keys move between tabs; a press on a closed card opens it |
| Questions: plus turns 45° `.3s`; height opens over `.35s cubic-bezier(.19,1,.22,1)`; answer fades and rises 4 px | yes — native `<details>` (works without script); the height animates where `::details-content` is supported, otherwise it opens at once |
| Logo cells flicker at their corners and light under the pointer; close button's label is set through accent blocks; faint ruled paths drift behind the foot and the figures card | not reproduced (logo wall has no data; the other two are ornaments of theirs) |
| Reduced motion | no pin (one screen per statement, all text set), no word or letter effects, cross-fades instant, row scroll instant |
| Without script | statements one screen each, every text visible, cards scroll sideways with the first open, questions open natively |

## Owner's rules that override the reference
- **No picture boxed beside text.** The reference's walk (5) has a 695×830 picture panel pinned beside the text column.
  Ours: the picture is the backdrop of the whole walk, pinned across the section, with a veil toward the text side and the
  entries laid over it. On the phone the reference puts the picture above the text; ours keeps it as the backdrop, clear
  at the top 250 px and veiled under the text.
- **Screens whole.** The three cards (3) crop their pictures to 334×208; ours gives the tile the proportion 334×300 and
  stands the client's picture whole on one landscape of the series, veiled 50 % toward the card. The row cards (6) show a blurred photograph under a paragraph; ours
  stands the client's screen whole and sharp on a landscape of the series blurred 18 px (as the reference blurs its photographs), under the title (height-limited to the card, never cropped).
- **No coloured glow.** The reference's figures card has a soft accent glow in its upper right; ours is a plain panel.
- No words invented: no section labels ("Calculator", "Platform" …), no foot column labels, no heading over the card row
  or the logo wall, no "More" on buttons (the link's own name).

## Differences that remain (seen in `pairs/`)
- The opening is a sequence of stills, not a film; nothing moves inside the picture.
- The bar is darker than the reference's (70 % of the palette's dark instead of 30 % black): the reference's white labels
  on its grey bar measure about 2:1 over a white page; ours are held at 4.5:1 on every ground.
- Walk: unread letters stand at 50 % strength (70 % on a light picture), not the reference's pale grey (which measures about 1.4:1); the notch in
  the panel's edge is gone with the panel; the walk is as long as the client's list (sportbot: seven entries, 4 800 px).
- Three cards are about 100 px taller than the reference's (taller tile).
- Figures card: no inner box with a field; shorter when there are few figures (min 600 high; the reference is 722).
- Row cards: a screen where the reference has a paragraph; the closed cards carry a sentence at 46 px, the reference a
  three-to-five-word title.
- Plans have no counterpart on the reference; the cards use its contact block's parts.
- Between 901 and 1180 px the desktop build is used with the bar's links hidden and tighter margins (the reference's
  tablet build was not measured).

## Image slots — one family: `land`
Motif named for this template: **land**. The reference is one series of dusk and aerial photographs of a yard (opening
film, card pictures, the blurred pictures in the row cards, the quotation backdrop); every slot here takes the
landscape series. `made.blur`, `made.sheet` and `made.sky` (as a kind of its own) are not used.
`series(d)` = land 1, 3, 4, 5, 2, 0 in the page's own tone (ground luminance under .45 → dark pictures only; a light
page takes the light ones, any when it has no light one).

| Slot (`data-slot`) | Reference shows | Takes (sportbot · automateed) | When absent |
|---|---|---|---|
| `opening-backdrop` (full-bleed, one per statement) | a dusk-to-night film of a yard | `made.land` 0, 2, 5, 1, 3, 4 then `made.sky`, the dark-toned ones only (text is light): ridge, water, rock · ridge, water, ridge | the palette's dark, plain |
| `card-ground` in the three cards | cropped aerial photographs | the first picture of the series for all three cards, cut left / centre / right, under a 50 % veil of the card colour; the client's picture stands whole on it: valley · valley | the page ground |
| `steps-backdrop` (pinned, the walk) | product films in a panel | the series, one per entry, wrapping: valley, pines, lake, rock, water, ridge · valley, pines, lake, rock. Phone: the picture stands in the top 340 px, clear for 150 px, and ends in the page's tone under the text | the deep panel colour, plain |
| `card-ground` in the row cards | blurred photographs | the series in reverse order, blurred 18 px, veiled 50 % dark / 62 % light | the deep panel colour |
| `quote-backdrop` | a dusk photograph of a road | `made.land` 5, 0, 2 — first dark one | the palette's dark |
Still without a picture: the logo cells (2, 7) and a quotation (8) — no data.

## Pass of 2026-11-12 (one family, picture share, readability gate)
- **Was:** three cards on three `made.blur` hues (green, mint, red on sportbot), row cards on `blur` hues. **Is:** the table above.
- **First screen.** At scroll 0 with script no statement is set (the reference does the same). The h1 is in the DOM
  as the first statement (`aria-label` carries its text while the letters are set); without script the first screen
  shows the h1 set whole over the picture — checked, `probe/v/*-nojs-d.jpg`, `*-nojs-m.jpg` (h1 top at 609 px of 900 at 1440; 619 and 564 px of 844 at 390).
- **Phone walk on a light page.** The pale pictures lay under an 88–92 % veil across a tall cropped section and could
  not be seen. The picture now stands in the top 340 px only (so nearly the whole frame shows), clear for the first
  150 px, and the veil ends in the page's own light under the text.
- **Picture share** (`tools/coverage.mjs`, 1440): reference 21 % (100,0,0,0,19,0,0,44,3,0,0,94,0,78,24,0,0,0; 3 screens with a wide picture) · ours sportbot 21 % (100,0,0,27,0,9,84,0,0,0,0,79,21,0,0,0; 3 wide) · automateed 26 % (100,0,0,25,2,0,96,0,0,33,66,0,0; 3 wide).
  The zeros after the first screen of the opening and inside the walk are the pinned sections on both pages (the tool reads a pinned picture once); seen screen by screen in `out/*-d-0N.jpg` the opening and the walk carry a picture at every step. The reference's quotation backdrop (78) has no counterpart: no quotation in either client's data.
- **Readability gate:** `tools/legible.mjs` — sportbot `ok — 0 unreadable of 437 line readings`, automateed `ok — 0 unreadable of 262 line readings`. Nothing set aside as an artefact. The gate does not judge a line while the bar covers it.
- **One-file copies:** sportbot 1.2 MB, automateed 1.1 MB, nothing left un-inlined.
- **shots.mjs:** sportbot d 13779 / m 12001, automateed d 11293 / m 9905 — sideways 0, distorted 0, h1 1, errors [] in all four. `probe/audit.mjs` was not re-run.

## What could not be transferred, and why
- The scroll-scrubbed film and the product films — theirs; clients have stills (sportbot's one video is a product
  recording 924×758, which must stay whole and cannot be a full-bleed backdrop).
- Mega-menu drop-downs, the calculator's inputs and slider, the contact form, the FAQ's tabs, social links — no data.
- Logo wall, second logo grid, quotation — both clients have none.

## Checks
See the report in the hand-over for the `tools/shots.mjs` lines and `probe/audit.mjs` results (contrast against rendered
pixels with the text made transparent, a ≥ 2-px focus ring on every Tab stop, reduced motion, no script).

### Results (final run, 2026-11-12)
```
tools/shots.mjs
sportbot   d {"height":13779,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
sportbot   m {"height":12001,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
automateed d {"height":11293,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
automateed m {"height":9905,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []

probe/audit.mjs (lowest contrast of any text against the pixels behind it · failures · Tab stops without a ring)
sportbot   1440: 4.27 (motion) / 4.66 (reduced motion) · 0 · 0 of 36      390: 4.66 / 4.66 · 0 · 0 of 34
automateed 1440: 5.24 / 5.23 · 0 · 0 of 22                                390: 4.88 / 4.88 · 0 · 0 of 22
```
The one reading under 4.5 (sportbot, 4.27, a 70-px heading) is a heading caught while its words were still coming up
from pale to ink; settled it is the ink colour. Without script (`probe/noscript.mjs`): no hidden text at 1440; at 390
the bar's links are behind the menu button, which needs the script (the same links stand in the foot); every card in
the row stands open. Render time 0.5–6 ms per client (`build.py`).

Limits of these checks: the audit walks the page in steps of 0.7 screen, so not every scroll position of the pinned
opening and the walk is sampled; it reads 24 points per text box; it skips text under the fixed bar; hover states were
checked for the button and the bar only by computed style; Safari and Firefox were not opened (the `::details-content`
height animation and `interpolate-size` are Chromium-only — elsewhere the answer opens at once).
