# griffin — notes

Reference: https://griffin.com/ (home page), measured 2026-11-12 at 1440×900 and 390×844 with `tools/anatomy.mjs`,
`tools/shots.mjs` and own Playwright probes (box/style tree, load sampling per frame, scroll sampling every 20–150 px,
hover/focus computed styles, canvas pixel sampling, accordion sampled each second). Raw captures: `ref/`.
Three kinds of statement are kept apart below: **measured** (read off the live page), **chosen** (my decision where the
reference gives no answer or the owner's rules override it), **not verified**.

## Sections of the reference, in order, and the data each takes

| # | Reference section (measured) | Data | Left out when |
|---|---|---|---|
| 0 | Bar 64 high, in the flow: logo left, account links right. Links ride in a separate fixed pill | `brand`, `nav`, `signin`, `cta` | never |
| 1 | Opening: two-line display, text with a muted second sentence, two pills, a mono note at the right with a pulsing dot; then a 252 px band of flickering signs between two rules | `hero.title/text/text2/primary/secondary/note`; band: a field of `/` with two signs out of `figures[].v` | no `hero.title`; the band alone, whole, when there are no `figures` or they give fewer than two signs |
| 2 | Ruled grid, six cells a row, 64 high | `logos[]`, else `trust[]` | both empty |
| 3 | The walk: one held screen, intro then numbered steps, picture on a dotted ground | `steps.title/text/items[k,title,text,cta,img]` | no step items |
| 4 | Accordion beside a picture | `features.title/items[t,d]`, `media.screens[]`, backdrop `media.made.land[2]` | no feature items |
| 5 | "Products": serif head, two columns of ruled rows with a 52 px tile | `plans.title/text/items[name,price,per,line,rows,cta,marked]/note` | no plan items |
| 6 | Row of three picture cards | `quotes[]`, else `media.photos[]` not already used in the walk | neither |
| 7 | Check list of pairs beside a picture, two pills | `faq.title/items[q,a]`, `media.video`, `hero.primary/secondary`, backdrop `media.made.land[5]` | no faq items |
| 8 | Head + muted text, four link cards | `statement.title/text`, `links[t,d,h]` | neither |
| 9 | Centred closing statement, one pill | `close.title/cta` | no `close.title` |
| 10 | Foot: brand + small print, link columns, bottom bar | `brand`, `foot.text/legal/links`, `nav`, `signin`, `cta` | never |

Not shown by this template (the reference has no place for them): `hero.kicker` (only in `<title>`), `figures[].l`,
`features.text`, `close.text`, `media.phones` (except as walk pictures). sportbot gets 0–5, 7–10; automateed gets 0–6, 8–10.

## Measures used (all measured unless marked)

- Frame: 20 px gutter each side (8 on phone), content padded a further 40 (20) → text starts at x 60 (28). Every section opens with a 1 px rule. Section padding 80/40 (40/20).
- Colour relations on the reference's ground: muted text ≈ ink 58 %, rules 18 %, dim marks 30 %, soft 80 %, main pill 91 % with ground-coloured text. Applied to the client palette in `_theme()`; muted is raised until 4.6:1 (**chosen**).
- h1 72/1.0 weight 300 −.02em (phone 32). h2 40/1.1 weight 300 (phone 28). Lede 20/1.4 weight 300, 616 wide (phone 18). Labels mono 12 caps +.06em; step labels and the note mono 14.
- Opening block 454 min-height, content bottom-aligned, 24 between h1/text/pills (phone 472, 16). Band 252 + 2 rules (phone 178 + 2); sign grid 12 × 14 px, three brightness tiers (field .16, dimmer sign .34, brighter sign .62 of ink).
- Pills 40 high, 12×20, radius 9999, gap 6; small 32 high, 8×14 (all pills are the small size on phone). Secondary: ground fill, 1 px inset ring.
- Bar pill: fixed, 12 from top, centred, 4 px padding, items 32 high with 0×16, blur 12 px.
- Walk: section = 100vh + 380 + 625 per step (reference 900 + 2880 for four steps); two halves of 700; text padding 80/40/40; labels 30 px pitch, markers 8 px at x 16 with ring shadows at 3/4/7 (active also 8/11/11.5/14.5); step head 40/1.1, text 20/1.4, pill 32 below; dotted ground 1 px dots on a 16 px grid. Phone: 100svh + 340 + 600 per step, text on top (padding 40/20/20), picture below, only the active label.
- Accordion: head 32 below h2; rows ruled; button 16 px padding, serif 24/32 muted → 32/40 ink when open (phone 20/28 → 24/32); body 16/24, 480 wide, 32 below.
- Products: columns 640, gap 40; group head 28/1.2 weight 300; rows 16 px padding, 52 tile radius 4, 24 gap, text 20/26, dashed rule starting at the text (phone 36 tile, 16/20.8).
- Picture cards: three columns of 413 with 40 gap; phone a sideways strip of 301-wide cards, 20 gap.
- Pairs: 64 under the head, 20 between pairs, 18/26 with the answer muted, pills 40 below (phone 16/20, pills stacked centred).
- Link cards: four columns, 16 gap, 16 padding, radius 8, title 20/28 weight 300, text 16/24 weight 300 muted, 36 between; head block 64 above (phone one column, 16/24 and 14/20).
- Close: 120 above and below, h2 at most 480 wide, pill 32 below (phone 60).
- Foot: 360 + four columns, 32 gap, 80/40 padding; small print 12/16 at 280; links 14/18 on a 30 px pitch; bottom bar 20×60, 12/16.
- Focus ring: 3 px solid, 2 px offset (reference colour #7c7771 → ink 52 % here).

## Typeface stand-ins (all SIL OFL, Google Fonts)

| Reference (commercial) | Stand-in | Why |
|---|---|---|
| Cambon, light | **Newsreader** 300, optical size 72 | light, high-contrast text serif with a similar narrow, bookish display cut |
| Söhne | **Hanken Grotesk** 300/400/600 | plain grotesque with the same quiet light weight |
| Söhne Mono | **Geist Mono** 400/600 (falls back to IBM Plex Mono) | grotesque monospace, slashed zero, even caps |

Heading tracking is −.04em, not the −.05em measured for Cambon: Newsreader is set tighter by default and collided at −.05em (**chosen**).

## Motion — measured, and what was reproduced

| What | Measured on the reference | Here |
|---|---|---|
| Load | nothing: at the first sampled frame (157 ms) h1, text, pills, bar and band are at full opacity in their final place | no load sequence |
| Scroll reveals | none: off-screen heads and cards already at opacity 1 | none |
| Bar | links pill is `fixed` at top 12; the call button is 0 wide/opacity 0 at scroll ≤ 100 and full at ≥ 110; width .3s, opacity .32s, cubic-bezier(.4,0,.2,1). A soft pill slides to the hovered link: .23s cubic-bezier(.3,.76,.27,1) | same; threshold 105 |
| Pills | a fill wipes across by scaleX 0→1 in .3s (lighter fill on the main pill, rule colour on the secondary, 7 % ink on the bare one) | same. Origin of the wipe **not verified**; left edge chosen |
| Note dot | 7 px dot, box-shadow pulse to .5em, 3 s, infinite | same |
| Band | canvas; a field of faint `/` in every cell; two heavier signs (one dimmer, one brighter) replace it in loose horizontal runs of one to about eight cells, each sign in runs of its own, changing continuously (about 4 % of sampled pixels per 100 ms); pointer has no visible effect | same anatomy: `/` field, two signs, each from its own value-noise field (slow drift + a fine component that breaks the runs), redrawn every 90 ms, paused off-screen. Share of cells per sign is by eye against the capture, **not counted** |
| Walk | sticky for 2880 px; intro until 380, steps switch at 380 / 1000 / 1640 / 2260 (≈ 625 each); drawing layers translate linearly with the scroll, no easing; passed labels collect at the top, coming ones wait at the bottom; label arrives by opacity + 8 px in .35s; eyebrow wipes in by clip-path .5s ease-out .05s; head, text and pill fade .5s ease-out .06s; a 1 px rail at x 19 carries a coloured run, fading over 200 px at both ends, to the scroll position; each step has its own marker colour | same thresholds and timings; the pictures are moved by the scroll itself. **Chosen**: each picture rests centred for the middle 56 % of its step (the reference's layers never rest) so a product screen stands whole while its text is read; marker colours are the client's accent then palette extras that reach 4:1 |
| Walk annotations | dot fades, leader line draws, text fades (keyframes seen; durations **not measured**) | not reproduced since 2026-11-12: the tag was the picture's `alt`, and an `alt` is never display copy; the data has no words for an annotation |
| Accordion | advances by itself every ≈ 7.8–8 s while a 1 px line runs along the bottom of the open row; a click opens that row and stops the run; body height .4s ease, opacity .25s ease after .1s; button size/colour .3s ease; pictures cross-fade .6s ease (a clip-path transition, cubic-bezier(.65,0,.35,1) .6s, is declared but stayed `inset(0)` in every sample) | same, 8 s; cross-fade only. **Chosen**: the run is held while the list is off-screen (reference behaviour off-screen not measured) |
| Product rows | tile fills with the dim tone and an arrow slides in 8 px, .2s / .23s — the rows are links there | not reproduced: plan rows are not links, so nothing answers the pointer |
| Link cards | border lightens (18 % → 38 % ink) and the arrow goes from muted to ink, .2s ease | same |
| Foot links | muted → soft | same |
| Reduced motion | not measured | all animation and transitions off; the walk is not pinned and becomes a plain run of steps, each beside its picture; the accordion does not advance; the band is one still frame; the film does not play and shows controls |

## What could not be transferred, and why

- **The band's signs.** The reference's two signs are currency signs — its own imagery; its field sign `/` is plain punctuation and is kept. The two signs here are the first two non-letter characters that stand in the client's `figures` (digits only if there are no others): sportbot `+` (brighter) and `%`, automateed `%` (brighter) and `+`. The first pass also made the field out of a third figure character and drew the signs as nested blobs with an empty rim — that was an invention and is gone (pairs/01). No figures, or fewer than two signs in them: no band at all (checked with `figures: []` and with one figure `8`).
- **Logo grid.** Both clients have no `logos`; `trust[]` stands in the cells as mono labels. The reference's "trusted by" head cell has no data and is not there.
- **The isometric drawing in the walk** is the reference's own illustration. The step's picture (phone screen, book cover) stands in its place, whole. Owner's rule: the reference's dividing rule between text and drawing is dropped and the dotted ground fades in from the middle, so the picture is not in a box.
- **Photographs behind the accordion and the pairs.** The reference boxes a photograph in the right half with a product card on it, the text on the page ground at the left. Owner's rule applied: the made photograph is the ground of the whole section (`object-fit: cover`), a veil of the section's ground lies under the text half at 92 % and lets go between 49 % and 65 % of the width, so the left reads as the reference's plain half and the right as its photograph, with no edge between them; the product screen/film stands on it whole at its own ratio. On the phone the reference puts the photograph under the product only, below the text; here the veil (20 % + 90 %) lies under the text block and lets go over its last 40 px. The screen has no caption (the reference has none there); its `alt` stays an `alt`, on the photograph and on the plain-ground fallback alike. The reference's interactive cards (UI/API switch, code request/response) are its own product and are not rebuilt.
- **Accordion sub-lists and "learn more" pills**: `features.items` has only `t` and `d`.
- **Product icons**: not taken; row numbers stand in the tiles. Prices and the plan's line are added under the group head because the reference has no place for a price.
- **Customer stories** (photo, headline, logo): no `quotes` for either client. The row takes `media.photos` instead, uncropped, four across when they are upright, with no caption (the `alt` was printed there until 2026-11-12); it has no heading because the data has none for it. The `quotes` path is written but **not exercised by either client** (the schema gives no fields for a quote).
- **Check-list section**: fed with `faq` (question / muted answer) — the nearest pair-shaped data; the reference's green ticks became a plain accent dot because a tick beside a question would mislead.
- **Foot column heads, social icons, certification badge, address**: no data. Columns carry `nav` and the account links without heads.
- **Phone menu**: the reference opens a dialog I did not measure. Here the button opens a plain ruled list (`aria-label="Menu"` is the only string not from the data).
- `hero.note` stays visible on the phone (the reference hides its note there) so no client content is lost by width.

## Image slots

| Slot (`data-slot`) | Where | Takes | Without it |
|---|---|---|---|
| `accordion-backdrop` | `<img class="bk">` in `.accs .field`, whole section (1400 × ~650–780 at 1440; 374 × ~850–1010 at 390), cover, lazy, `alt=""`, width/height set | `media.made.land[2]` (water with reflections; index wraps) — sportbot `land-water` (dark), automateed `land-water` (dark) | plain `palette.extra[0]` field when a screen stands on it, else the page ground; `data-slot` then sits on the section's inner block |
| `pairs-backdrop` | `<img class="bk">` in `.faq .field`, whole section (1400 × ~945; 374 × ~1420) | `media.made.land[5]` (wide, empty upper third) — sportbot `land-rock` (dark). automateed has no `faq`, so the section and the slot are not rendered | plain `palette.extra[1]` field, as above |

Ink over a picture follows its `tone`: `dark` → the lighter of the page's ground/ink as text and the darker as veil; `light` → the reverse (`_over()`). Both clients' pictures in these slots are `dark`, so the `light` branch is **not exercised**. Muted text over a picture is raised to 7:1 against the veil colour. A section with a picture but no product screen (no `media.screens` / no `media.video`) keeps the two columns and shows the picture bare at the right (checked once on sportbot, 1440 and 390).

Contrast measured on rendered pixels (text made transparent, each text box cut from a full-page screenshot, worst pixel against the text's colour; reduced-motion render, first accordion row open):

| | 1440 | 390 |
|---|---|---|
| sportbot accordion: head / open row / body 16 px | 17.1 / 17.8 / 17.0 | 17.2 / 17.1 / 16.9 |
| sportbot accordion: closed rows (muted, 24 / 20 px serif) | 7.05 | 6.72 |
| sportbot pairs: head / question / answer (muted 18 / 16 px) | 17.2 / 17.4 / 6.92 | 17.2 / 17.3 / 6.87 |
| automateed accordion: head / open row / body | 14.1 / 14.8 / 14.4 | 13.7 / 14.4 / 13.7 |
| automateed accordion: closed rows (muted) | 7.11 | 6.71 |

Body text is at 7:1 or more everywhere; the muted closed rows on the phone are 6.7 (large text). Only the first row's body was measured open; the other bodies sit in the same veiled area.

Still without a picture:
- **Story cards** — three 16:9 photographs (413 × 232; square 301 on phone) of the client's customers at work; needs real `quotes` with photographs. Left out; the row shows `media.photos` when there are any.
- **Logo cells** — monochrome customer logos at most 28 high in the ruled grid; needs real `logos`. `trust[]` stands there as mono labels.

No other made kind (`blur`, `sheet`, `sky`) is used: the reference shows none of those. The dotted ground of the walk is the reference's own 1 px dot grid, not a stand-in for a picture.

## Checks

`tools/shots.mjs` on both outputs: no sideways scroll, no script errors, no distorted media, one h1, at both widths (lines in the hand-back report). Own audit (not part of the tools): every text node ≥ 4.5:1 (≥ 3:1 from 24 px) on its ground at both widths, every focusable shows a ring, zero running animations under reduced motion.
Not done: no browser other than Chrome; the picture sections were not looked at between 390 and 1440 (the veil switches from sideways to downward at 900); hover and the phone menu were not screenshotted; widths between 390 and 1440 were not captured.

## Pass of 2026-11-12 (plans / questions kept, `alt` never copy, needs.json)

- **Plans and questions** were already on the page (sections 5 and 7); checked string by string against both data files:
  every `plans` and `faq` string is in the rendered text.
- **`alt` as copy — three places removed**: the mono annotation tag beside each walk picture, the caption under the
  product screen on the plain-ground fallback of the feature section, and the caption under each picture of the
  picture row. None had copy of the client's to take instead, so the elements are gone; every `alt` stays on its `<img>`.
- **Not shown** (listed under "drops" in `needs.json`): `figures` (values and labels — only two signs of the values are
  drawn in the band), `features.text`, `close.text`, `hero.kicker`.
- **needs.json** written from two scratch renders of sportbot (data/ untouched): with all media removed the page is a
  ruled page of type with no empty frame — it holds, the held walk being its weak part (right half blank for three
  steps); with only the made pictures removed the two backdrops are flat palette fields (green, brown).
- Gates on the final build: `legible.mjs` ok for both (sportbot 426 line readings, automateed 230); `shots.mjs` clean
  at both widths (sportbot 8050 / 9202, automateed 6994 / 6900); `coverage.mjs` sportbot 29 %, automateed 26 %, reference
  15 %; one-file 1.1 MB and 0.9 MB.
- Not done: pairs 02 (walk) and 05 (picture row) still show the tag and the captions — not re-made; the two
  no-picture renders were not looked at at 390.
