# supaste — notes

Reference: https://supaste.com (home), read 2026-11-12 at 1440×900 and 390×844 with `tools/anatomy.mjs`, `tools/shots.mjs`
and own Playwright probes in `probe/` (run with `tools/run.sh node supaste/probe/<name>.mjs`): `tree.mjs` (box/style tree
of a y-range), `motion.mjs` and `motion2.mjs` (load sampled every 100 ms, scroll sampled at nine positions, reveal sampled
per frame, hover/open states), `shots2.mjs`, `refsecs.mjs`. Raw captures in `ref/`, raw numbers in `probe/*.txt`.
No cookie wall or loader was met. Three kinds of statement are kept apart: **measured**, **chosen**, **not verified**.

## Sections of the reference, in order, and the data each takes

| # | Reference (measured) | Ours | Data | Left out when |
|---|---|---|---|---|
| 0 | Bar fixed at the top edge, centred, 710×53, ink ground, bottom corners rounded, a 20 px "ear" turning out into the edge on each side; 30 px app tile r8 + name 16/600, links 14/500 at 60 %, small white button r8 12/600. Phone: 350×50 with a three-line button | same; the bar is the ink colour with ground-coloured type | `brand`, `nav`, `signin` (as the last link), `cta` | never |
| 1 | Opening, 1383 high: sky (deep → bright → pale accent, a CSS gradient) with a landscape photograph across the last 600 px that fades into the page; 600-wide centred column, 20 gaps: small line 20/600, two-line h1 80/1.0/−.05em (line 1 sans 700, line 2 serif italic), text 20/1.4, two buttons 52 high r20 (ink and ground), 12 px notes; 60 below, a 1120×562 product panel with a 260×563 phone laid over its right end | same column on the page's own ground; the landscape at the foot is the page's lead picture; product screen whole with a second picture standing beside it | `hero.kicker/title/text/text2/primary/secondary/note` · `media.screens[0]` · first of `phones`/`photos` not used by a step · lead `made.land` | no `hero.title`; panel when no screen |
| 2 | Row of seven 90 px award discs | built, but takes only `logos[{src}]` | `logos` | empty (both clients) |
| 3 | Centred head 740 wide: h2 60/1.0/−.05em, text 20/1.4 at 60 %, two rows of small pills (12/500, r30, 5×10, ground + 3 % ink) | same | `statement.title/text`, `trust[]` | all three missing |
| 4 | Stack of cards 1120 wide, 20 apart: ground + 3 % ink, r30, 40 inside, 40 between parts; centred h3 50/1.0/−.05em, text 16/1.4 at 60 %; one 1040-wide film r20 (the app on a landscape photograph) | same card; the stage is the lead landscape again, in another crop, with the client's film or screen standing on it whole | `media.video` (first card), `media.screens[1:]` (one card each); the heading is that picture's own `alt` | no video and fewer than two screens |
| 5 | Second card of the stack: h3, text, button, four 253×547 tiles r30 (heading + small text + phone, alternating text-above / text-below) | same; all tiles stand on one quiet `made.field` in the page's tone | `steps.title/text`, `cta`, `steps.items[title,text,cta,img,shape]` | no step items |
| 6 | 500-wide quote between cards (after the third and fourth): stars, 16 px text, portrait, name, role | text, name, role only (no stars, no portrait) | `quotes` | empty (both clients) |
| 7 | End of the stack: two cards side by side (550 each), h4 30 centred, text 16 at 60 %, a small interface drawing | two-column cards: figure at 50/700, label 16 | `figures[v,l]` | empty |
| 8 | Head 600 wide (h2 60, text 20) + grid of 3 × 360, 20 gaps; cards r30, 40 inside, 20 between parts: 64 px white icon disc, h4 30/1.0/−.05em, text 16/1.4 at 60 %, left-aligned | same without the icon disc | `features.title/text/items[t,d]` | no items and no title |
| 9 | Price: head (h2 60, text 20, a 12 px line), one card 400 wide r40 (80/40/40 inside) with a 240×50 ink tab hanging from its top edge (app tile + name), a 320×40 segment switch (white r14, ink thumb r13, 14/600), the price, a white r10 box, check rows 14/1.6 with 24 px rings at 20 %, a 52 px button; 14 px note 400 wide below. Behind the card's lower part: the opening's sky turned upside down | same; the switch chooses between the plans (the marked plan first shown) | `plans.title/text/items[name,price,per,line,rows,cta,marked]/note`, `brand`, lead `made.land` (not turned over) | no plan items |
| 10 | Questions: head, two columns of 490 with 20 gaps; rows r20 on ground + 3 % ink, 20 inside, a 16 px plus at the left that turns 45°, question 14/1.6, answer 16 at 60 % | same | `faq.title/items[q,a]` | no items (automateed) |
| 11 | Three cards 1120 wide, 60 apart: left 510 (app tile + name 20/600, h3 50 left, 16/600 line, text 20 at 60 %, 240×52 button), right a 510×358 picture | text in the left 510; the picture is the card's own backdrop (owner's rule) | `links[t,d,h]`: `d` is the heading, `t` the button · `made.land` | no links |
| 12 | "Featured on" badge rows | not built | — | reference's own marks; no data of that kind |
| 13 | Foot on ink: the page ends in a rounded lip 1120×40 hanging into it; left 400: app tile + name, two-tone 30 px line (sans 700 + serif italic), 14 px text at 60 %, small white button, 12 px lines at 40 %; three 200-wide link columns under small headings; the name set 320 px high in ink + 7 % | same; no column headings (they are the reference's words) | `brand`, `close.title/text/cta`, `foot.legal/text/links`, `nav`, `links`, `signin` (a link is listed once) | never |

Has no place in this build: `plans.items[].marked` as a visual mark (only decides which plan shows first), `media.photos`
beyond the opening and the tiles, `features` icons. sportbot renders 0, 1, 3, 4 (four cards), 5, 7–11, 13; automateed
renders 0, 1, 3, 4 (two cards), 5, 7, 8, 9, 11, 13.

## Measures used (measured unless marked)

- Column 1120 (1200 container, 40 inside); sections 100 above and below, 60 between head and body; phone 20 gutters, 60.
- Type: Inter Display at 80 / 60 / 50 / 30, all 700, line-height 1.0, tracking −.05em; text 20/1.4 and 16/1.4, −.01em;
  small 14 and 12. Phone: 50 / 38 / 32 / 19, text 16 / 14.
- **Chosen:** the reference's h1 lines hold 10–14 letters. The clients' titles are split in two at a sentence end, else at
  the most even word break, and the size is 80 (phone 50) reduced only until the wider line fits 1040 (phone 340): both
  clients get 80 at 1440; at 390 sportbot 44, automateed 32. Card headings step 50 → 42 → 34 by length (the reference's
  never pass one line of 1040).
- Colours: card = ground + 3.1 % ink (#f7f7f7 on white), chip = ground + 11 % ink (#e3e3e3), secondary text = ink at 60 %
  — **chosen:** raised until 4.6:1 on the card. The reference sets its notes at 40 % (2.6:1); ours use the 60 % colour.
  Bar and foot = ink with ground-coloured type (on sportbot, a dark page, they are therefore light). The accent has no
  flat surface in the reference outside its sky; here it arrives only through the made pictures and the text selection.
  The bar is opaque at both widths, so it reads the same over everything that passes under it.
- Buttons 52 high, 15×30, r20, 16/600; small 33 high, 8×16, r8, 12/600. Pills 29 high.
- Stage (**chosen**, the reference's film is 1040×582 cover-cropped): the screen is at most 80 % of the stage wide and 560
  high (phone 320), 52 above and below, r12 on the screen, r20 on the stage.
- Tiles: 10 gaps, 547 high, r30; heading 28/700, text 15. Phone: **chosen** one tile a row — the reference keeps 2 × 2 at
  140 wide because its tile text is part of the picture; live text at that width would be about 9 px.

## Typefaces

The reference uses Inter Display and Instrument Serif (italic). Both are SIL OFL and on Google Fonts, so no stand-in was
needed: `Inter` with its optical-size axis (14–32, which yields the Display cut at these sizes) and `Instrument Serif`
italic. The reference's phone-panel labels in plain Inter are not rebuilt.

## Motion — measured, and what was reproduced

| What | Measured | Here |
|---|---|---|
| Load, headline | every letter its own span: opacity 0, 10 px low, blur 10 px → clear; first letter starts ≈0.3 s after first paint, each next ≈45–50 ms later, each takes ≈0.6 s, decelerating | same values (45 ms steps, .65 s, starts .15 s); words kept whole; the sentence is given to screen readers once |
| Load, text and buttons | block at opacity 0, 30 px low; starts ≈0.75 s after the first letter, ≈0.9 s | same (.9 s after .9 s; buttons, note and panel 50–200 ms later) |
| Scroll, opening landscape | scales 1 + 0.01447 per 100 px and sinks 7.24 px per 100 px, linear with the scroll (1.17 and 87 px at 1200) | same |
| Scroll, phone on the panel | 50 px low at rest; reaches 0 between scroll 300 and 600 (19.8 at 450) | same, eased quadratic to match 450 |
| Bar | fixed, does not hide or change on scroll | same |
| Cards, questions, grid cards | wait at opacity 0, 30 px low; start when about half a screen of the card shows (card top at 320–440 of 900); exponential settle, ≈40 % left every 66 ms, done in ≈0.7 s; stay once shown | start when the top passes half the window; .9 s `cubic-bezier(.2,.75,.25,1)`; anything already passed, or reached at the page end, is shown |
| Films | play muted in a loop | same (`media.video`) |
| Hover | ink button → 80 % ink; small white button → 80 %; bar links 60 % → 80 % | same |
| Press | no press state found | none |
| Question row | opens over ≈0.5 s with a spring; plus turns 45° | height + opacity .5 s `cubic-bezier(.2,.8,.2,1)`, plus 45° |
| Price switch | ink thumb slides to the chosen segment; price rises 12 px while fading in | thumb .45 s, panel 12 px + fade |
| Reduced motion | not measured on the reference | nothing animates, nothing waits hidden, landscape and second picture stay put, film shows controls and does not start |

Not reproduced: the reference's opening panel is a live HTML mock-up of the app whose rows slide in (it is the reference's
own product); the cursor that moves inside its films; the counting price digits; the fixed "Honors" tab at the right edge.

## What could not be transferred, and why

- **Opening panel.** The reference draws its app in HTML with glass side panels and lays a phone over the right end.
  Ours: the client's screen whole, and the second picture *beside* it (840 + 260 of the 1120, 20 between, dropped 57 px
  as in the reference) rather than over it — owner's rule, screens whole.
- **Films in the cards.** The reference's films crop the app inside a 1040×582 frame. Ours stand whole on the made
  landscape. Screen cards have no paragraph: the only words the data ties to a screen are its `alt`.
- **Tiles.** The reference's phones run off the tile's lower edge; ours are whole, so the tile shows a smaller phone.
- **Link cards.** The reference boxes a 510×358 picture beside the text. Owner's rule applied: the made landscape is the
  whole card's backdrop and fades into the card's ground under the text. The reference's product-name line and 16/600
  line have no data; heading and button only, so the cards carry less than the reference's.
- **Icon discs** in the grid, **stars and portraits** in quotes, **award discs**, **"Featured on" badges**, the
  **progress bar "spots left"**, the **struck-through old price**: never taken / never invented.
- **Foot column headings**: the reference's words; columns stand without them.
- **Figures** have no section in the reference; they take the two-column small cards (**chosen**), without the drawings.
- **Hero secondary button** (**chosen**): the reference's is the page's other extreme (white on blue). The opening's
  words now stand on the page ground, so it is the ground mixed 10 % toward the ink.
- **The sky.** The reference's opening is a smooth CSS sky in its brand colour. `made.sky` stood there under a veil
  until the 2026-11-12 pass (sportbot's is a nebula and read heavy; it was also a second picture family). Now the
  opening's upper part is the page's own ground and the only sky is the one in the landscape photograph.

## Image slots — one picture family: `land` (pass of 2026-11-12)

The reference shows ONE picture throughout: the same sunlit hills at the foot of the opening, behind the app in every
film, behind the screenshot in every link card. So the motif is `land`, and the page has a **lead picture** that comes
back: `lead_land()` takes the first of `made.land[0, 5, 1]` whose `tone` is the page's own (sportbot, dark page →
`land[0]` ridge at dusk; automateed, light page → `land[5]`, the pale dune). A dark page never takes a light one.

| Slot | Where | Reference shows | Takes |
|---|---|---|---|
| `land-lead` | foot of the opening, 1440×820 (phone 420), fading in from the page ground above and out into the page below | sunlit grass hills under a CSS sky | the lead picture; the words above it stand on the plain ground |
| `land-lead` (stages) | 1040 × (screen + 104) in each film/screen card | the same hills behind the app, every time | the lead picture again, one of four crops in turn (`object-position`) |
| `land-lead` (price) | band behind the price card's lower part | the opening's sky upside down | the lead picture, upright, masked out at both ends |
| `field` | each tile, ~340×547 | one blue gradient under all four tiles | ONE `made.field` of the page's tone under every tile (another crop each), text veiled toward the ground; plain chip colour when no field of that tone exists. Before: a different saturated `made.blur` hue per tile — removed |
| `land` (link cards) | whole card 1120×444, text on a veil of the card colour over the left half | product screenshot on the hills | the lead's neighbours in the series, each once: `land[1, 2, 5, 3, 4, 0]` without the lead, own tone first (a dark page takes only dark ones). sportbot 4 cards → valley, water, rock, pines; automateed 3 → valley, pines, lake. **No picture repeats** unless a client has more link cards than pictures |

Not used: `made.sky`, `made.blur`, `made.sheet`. Still without a picture: the grid cards' icon discs, the award discs,
the quotes' portraits (all left out). Without `made` every slot is a plain palette ground (`out/sportbot-nomade.html`).

## Picture share (`tools/coverage.mjs`, 1440)
```
reference  {"height":19969,"screens":23,"picture_share":31,"per_screen":[13,65,43,48,51,21,48,48,53,55,53,53,53,55,21,0,0,0,0,14,0,0,0],"screens_with_wide_picture":11}
sportbot   {"height":12392,"screens":14,"picture_share":44,"per_screen":[36,58,56,51,55,51,51,0,7,84,21,71,69,0],"screens_with_wide_picture":9}
automateed {"height":8423,"screens":10,"picture_share":41,"per_screen":[51,42,53,53,22,0,42,74,45,0],"screens_with_wide_picture":6}
```
The reference's sky is a CSS gradient and reads as zero; the full-page capture in `ref/` shows the opening a second time lower down (whether that is the page or the capture was not determined). Ours is
above the reference overall because the link cards are whole-card backdrops (owner's rule) where the reference boxes a
510×358 picture, and the price band is a photograph where the reference's is a gradient. Nothing here is pinned.

## Readability (`tools/legible.mjs`)
```
sportbot    ok — 0 unreadable of 503 line readings
automateed  ok — 0 unreadable of 268 line readings
```

## Checks

`tools/shots.mjs` on both outputs: see the report lines. `probe/audit.mjs` (not covered by shots.mjs): every text node's
colour against the rendered pixels behind it (text hidden, full-page PNG sampled at 12 points per line), eight Tab stops
for a 2 px outline, a `reducedMotion` page for hidden or running things, and a script-disabled page for anything hidden.
Results are in `probe/audit.txt`.

`tools/shots.mjs` after the 2026-11-12 pass:
```
sportbot   d {"height":12392,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
sportbot   m {"height":11457,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
automateed d {"height":8423,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
automateed m {"height":8428,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
```
`probe/audit.mjs` was not re-run after that pass.

## Engine stress fixes (2026-11-12)
- Logo (non-wordmark) is 30 high at its own width (was forced 30×30).
- Price switch: one row while every plan name fits its share of the narrowest card (phone, 286 px inside); otherwise
  the segments stand one under another and the thumb moves down. With five plans names spilled onto the thumb (1:1)
  and the page ran 1 px sideways at 390.
- With the switch shown, the plan name inside each pane is no longer kept as clipped hidden text (it lay across the
  price for the gate); the pane is labelled by its tab. Without scripts the names show as before.
