# fluently — notes

Reference: https://getfluently.app (home page, "For Individuals"), measured 2026-11-12 at 1440×900 and 390×844 with
`tools/anatomy.mjs`, `tools/shots.mjs` and own Playwright probes kept in `probe/` (`tree.mjs` box/style tree of the whole
page at both widths, `motion.mjs` + `motion2.mjs` load frames and scroll sampling, `res.mjs` the card row under real wheel
events, `snap.mjs` section screenshots). Raw captures: `ref/` (anatomy, full-page, stepped, `x-*` section shots),
`probe/tree-d.txt`, `probe/tree-m.txt`, `probe/motion-d.json`.
Three kinds of statement are kept apart: **measured** (read off the live page), **chosen** (my decision where the
reference gives no answer, the data does not fit, or the owner's rules override it), **not verified**.

## Sections of the reference, in order, and the data each takes

| # | Reference section (measured) | Data | Left out when |
|---|---|---|---|
| 0 | Bar, fixed, clear, 16 all round: mark + name left; right a 12-radius tray of two links (the current one filled), a hairline, the call on a two-colour slope. Its ink turns over on the white band | `brand`, `nav` (tray), `cta` (call); phone tray: `signin` + `cta` (filled) | never |
| 1 | Opening, one screen: a filmed photograph (hands holding the phone with the product) covers it under a veil; centred h1 and two lines of text at the top; two frosted pills at the foot; a small looping arrow above them | `hero.title`, `hero.text`, `hero.note` (the small 16/19.2 line above the arrow, where the reference says "scroll"), `hero.primary`, `hero.secondary`; backdrop `media.made.land`; the product in the middle = one of the client's own screens | no `hero.title` |
| 2 | Running line of press marks, 151 high | `logos[]`, else `trust[]` as words | both empty |
| 3 | The walk: one screen held for 7380 px, five steps; label, head and text left, the phone right on a soft coloured field, a tray of dots at the right edge | `steps.items[k,title,text,img]`; field `media.made.land` | no step items |
| 4 | Tiles: centred head, then a tall tile (389) beside two wide ones (795) — each a label, a head and a pane of product film | `features.title`, `features.items[0..2]` (`t` head, `d` text), panes: client screens / `media.video` on `media.made.land` held quiet | no feature items |
| 5 | Turned band (white on a black page), one screen, sticky: label, a 100 px figure counting up, two rating badges, three running rows of review cards | `figures[0]` (v = the figure, l = the label), `figures[1..3]` (the small row), `quotes[]` (rows) | no figures and no quotes; rows alone when no quotes |
| 6 | Outcome cards: an 80-round slab slides up over the band and is held while six 440×400 picture cards run sideways with the scroll; each card a head on a photograph and a frosted panel at its foot | `statement.title` (head), `features.items[3..]` (`t` head, `d` in the frosted panel), pictures `media.made.land` | fewer than four feature items |
| 6a | — (no pricing on the reference: `/pricing`, `/faq`, `/teams`, `/business` all answer 404). Built from its parts: tiles of radius 40 (marked plan in the second colour, others ink 8 %), tile head 32/1, the band's figure style for the price (56/1 −.04em), the question rows (16 round, ink 6 %) for what a plan holds, the bar's call (marked) and tray (others) as buttons | `plans.title/text/items[name,price,per,line,rows,cta,marked]/note` | no plan items |
| 6b | Questions: on the reference a dialog opened from the foot — a 40-round panel 720 wide, 32 inside, head 48/1.1 weight 700 −.05em, native disclosure rows 16 round on ink 6 %, 20×24 inside, 12 apart: number 14/18 at 40 %, question 18/22 weight 500 −.06em, a 24 px plus, answer 16/19.2 at 70 % 16 below (phone: head 28, question 16) | `faq.title`, `faq.items[q,a]` — the same column and rows standing in the page before the close, first row open | no faq items |
| 7 | Close, 40-round top, film backdrop: centred head, QR, two frosted pills; then the foot as a frosted 32-round card: mark, three link columns, social marks, language row, legal row, two labelled link rows | `close.title`, `close.text` (small line, the dialog's 16/19.2), `close.cta`, `hero.secondary`; backdrop `media.made.land`; foot: `brand`, `nav`, `links` (not already in nav), `signin`/`cta`/`foot.links` (not already shown), `foot.legal`, `foot.text` | head when no `close.title`; the foot always stands |

Not shown by this template (no place on the reference; listed under `drops` in `needs.json`): `hero.kicker` (only in
`<title>`), `hero.text2`, `steps.title`, `steps.text`, `steps.items[].cta`, `features.text`, `statement.text`,
`figures[4..]`. Plans and questions were added on 2026-11-12 after the contract's rule that they are never dropped.
sportbot renders every section; automateed renders all but the questions (it has none), its card row has two cards
and is therefore not held, and its plan tiles are short (no rows in the data).

## Measures used (measured unless marked)

- Page: one ground, one ink; column 1200 centred. Labels 12/1.2 weight 700, +4 px tracking, caps, in the accent.
  Section heads 56/1 weight 600 −.06em centred, at most 440–620 wide (phone 36).
- Bar: 73 high, 16 padding. Mark 32, name 16/600. Tray radius 12, ink at 10 %; items 41 high, 0×16, 14/18 weight 500
  −.03em (phone 12, 0×10). Hairline 1×20, 12 either side. Call 40 high, 0×18, radius 12, slope at 100deg.
- Opening: 100vh (phone 760 of 844 → `min(100svh,760px)`), padding 80/24/40 (phone 80/16/64). h1 64/1 weight 600 −.06em
  (phone 48). Text 24/1.2 weight 500 −.06em, 560 wide, 16 below the h1 (phone 18/1.1, 302). Veil: linear 50 % → 16 % at
  the middle → 100 % at the foot, plus a radial 55 % at the top over 380. Pills 54 high, 10×24, radius 100, ink 24 %,
  blur 5, inner glow 8 px at 25 %, 12 apart (phone 49 high, each half the width). Arrow disc 24, ink 12 %, blur 8.
- Running line: 64 above and below (phone 40); items 23 high at 70 % opacity; ends masked over 10 % of the width.
- Walk: section 100vh + 7380 for five steps; halves 612 | 588; text starts 24 in (x 144); label 16 above the head; head
  48/1.1 weight 700 −.05em, 400 wide; text 18/22 weight 500 −.06em, 360 wide, 24 below; screen 298×631, radius 22, centred
  in its half; dots 12 px, 16 apart, in a 16-radius tray of ink 8 %, 16 from the right edge. Phone: held block 760; picture
  above (reference screen 164×347), words from y 539: head 36/1.1, text 16/20; section 760 + 3680.
- Tiles: 80 above the head, 160 below the grid, 80 between head and grid; grid 389 | 795, rows 400, gap 16; tile radius
  40, padding 8; pane radius 32 (373×618 in the tall tile, 390×384 in the wide ones); text padding 32; tile head 32/1
  weight 600 −.05em. Tall tile in the other pole (white there), first wide tile in the second colour (blue there), second
  wide tile ink 8 %; the wide tiles mirror each other. Phone: every tile 358×475 with a 342×325 pane, head 24/1, in a row.
- Turned band: 160 above; label, 16, figure 100/1 weight 600 −.04em; 40 to the small row (40 apart, a 1×24 hairline at
  16 %); cards 400×240, radius 30, padding 30×29, 1 px inner line, text 18/22, three rows 16 apart, 320 fade at the foot.
  Phone: 40-round card, 64 above, figure 48, cards 320×200.
- Outcome cards: slab radius 80 (phone 56); held block padding 80/80/40 with 80 between head and row; cards 440×400,
  radius 40, padding 40, 16 apart, head 32/1; first card at the column edge, last one ends 80 from the right. Phone: cards
  320×320, radius 24, padding 24, head 24/1, section padding 120/24/80.
- Close: radius 40 at the top; 160 above the head; head 56/1 at most 620 wide (phone 32); 44 to the pills. Foot card: 16
  from the edges, radius 32, padding 40 (phone 24), ink 12 %, blur 10; four columns of 304; links 16/1.2 weight 500 in
  32-high rows; hairline at 16 %; small rows 14/18.

## Typeface

The reference is set in **DM Sans** throughout, which is itself an open-licence face (SIL OFL, Google Fonts) — used as it
is, weights 400/500/600/700 with its optical-size axis. No stand-in was needed.

## Colour relations (reference → client palette)

Measured: page black, ink white, labels and the active dot in one accent (green), a second colour (blue) for one tile,
the call's slope (violet → blue) and the label on the white band; one band turned to the other pole.
Here: `palette.ground` / `palette.ink`; labels take `palette.accent`, pushed toward the ink until it reads at 4.6:1
(**chosen** — automateed's orange on cream did not); the band is ink with ground-coloured text; the second colour is the
first `palette.extra` that stands off both poles (sportbot deep green, automateed blue); the call's slope runs from a
mix of that colour into the accent.

## Motion — measured, and what was reproduced

| What | Measured on the reference | Here |
|---|---|---|
| Load | nothing moves: at the first sampled frame (355 ms) h1, text, pills and bar are at opacity 1 in place; the whole page fades in .26 s ease-out | no load sequence (the page fade is not reproduced) |
| Opening film | plays once (6 s), not looped | a still made photograph — no film of this kind exists for the clients |
| Arrow | two arrows in a 24 px disc, translateY −24 → 0, .64 s cubic-bezier(.44,0,.56,1), infinite; the hint leaves by opacity + transform .48 s once the page moves | same; leaves after 40 px of scroll (threshold **chosen**) |
| Bar | never hides (sampled scrolling down and up); its text is white, and black exactly while the white band is under it; colour .25 s; it is clear all the way down, so its words cross tiles of the other pole unreadable for a moment | same, generalised: the bar takes the ink of the section under it; a word-mark logo is turned to one flat tone over the other pole. **Departure for the readability gate**: once the page has moved 40 px the mark and the tray stand on a frosted plate (88 %) of the ground under them; at the top of the page the bar is clear as on the reference |
| Call button | label is two stacked copies in an 18 px clip, transform .3 s cubic-bezier(.4,0,.2,1) | the copies roll up by one line on hover. The hover end state was **not captured** — inferred from the structure |
| Frosted pills | ink 24 % → 48 % on hover, .15 s cubic-bezier(.4,0,.2,1) | 24 % → 36 % (**chosen**: 48 % drops the label under 4.5:1) |
| Running line | translateX 0 → −50 %, linear, infinite; 38 s for 2280 px (60 px/s) | same speed; the list is repeated by script and moved by its own width |
| Walk | block sticky for 7380 px (phone 3680); steps change at 1360–1440 / 2700–2780 / 4060–4140 / 5400–5480 px after the block arrives (≈ 1350 a step; phone ≈ 640), the last step holds for the rest; words, screen and field cross-fade together, opacity .48 s cubic-bezier(.44,0,.56,1); each step's film plays once in real time (not tied to the scroll); two blurred discs behind the phone turn over 5 s and change colour by step; dots .15 s | same thresholds (step = floor((y − 50) / 1350), 640 on a phone) and the same cross-fade. The screens are stills, so nothing plays during a step. The turning discs are **not reproduced** (see below) |
| Tiles head, band label | start at opacity .001, translateY −20; arrive over 1.51 s on a spring curve when they enter the view | same distance and duration with cubic-bezier(.16,1,.3,1) standing for the spring |
| Tile film | looped, plays in view | sportbot's film plays while its tile is on screen |
| Figure | counts up in about 1.6 s, fast then slow (519 k at .2 s, 950 k at 1 s, done at 1.6 s) | same curve (1 − 2^(−10t)) over 1.6 s, once, when the figure is in view; only when the value is a single number with a prefix/suffix (`+3.1%`, `85%`) |
| Review rows | 116.48 s for 5824 px (50 px/s), middle row reversed | written, same speed and reversal — **not exercised**: neither client has quotes |
| Band and slab | band sticky; after one screen of holding, the slab (radius 80) slides up over it; the band's opacity falls linearly 1 → 0 while the slab is held | same; without quotes the band is only as high as its content and the extra screen of holding is dropped (**chosen**: an empty white screen held for 900 px) |
| Card row | slab held for 1215 px while the row moves 1480 px (linear, .82 px of scroll to the px), from first card at the column edge to last card 80 from the right; each card's lower panel rises 80 px and fades in (.8 s spring; .4 s on one) when the card is in view | same geometry from the number of cards; panels rise over .8 s with cubic-bezier(.2,.9,.3,1). With too few cards to overflow, nothing is held |
| Phone rows | tiles 16 s for 1122 px (70 px/s); outcome cards 26.88 s for 2016 px (75 px/s); both run by themselves | same speeds |
| Questions | native disclosure, no height animation declared; the plus carries transform .15 s cubic-bezier(.4,0,.2,1); the dialog itself was at opacity 1 in every frame sampled after the click | native `<details>`, the plus turns 45° in .15 s on the same curve. The reference's open state was **not captured** (my probe did not find its rows to click), so the 45° is an assumption |
| Foot links | opacity 1 → .5, .2 s cubic-bezier(.4,0,.2,1) | same |
| Fixed QR card | bottom right, leaves (opacity .4 s) when the close arrives | not reproduced — the clients have no QR |
| Reduced motion | not measured | no animation or transition; the walk is not held and becomes a plain run of steps; rows do not run and can be scrolled by hand; the card row is a hand-scrolled row; the figure does not count |

## What could not be transferred, and why

- **The filmed backdrops** (opening and close) show the reference's product in someone's hands. The slots take a made
  landscape whose tone agrees with the page (sportbot: ridge, then water; automateed: rock, then valley). The product
  that the reference shows in the middle of its opening film stands there as one of the client's own screens, whole.
- **The hand holding the phone** in the walk is the reference's photograph. The step's own picture stands alone.
- **The glowing discs behind the phone.** Owner's rules: no coloured glow, one picture family a page. In their place the
  page's own landscape series (the opening's picture first, then its neighbours of the same tone) fills the picture's
  side of the screen at half strength and fades toward the words, one per step, cross-fading with it. A first pass used
  the `blur` hues there (a different saturated colour a step) and was taken out. This is the largest visible departure
  in the walk.
- **Product film in the tiles** is cropped to its pane on the reference. Owner's rule: screens whole. Each pane is the
  page's landscape motif veiled 55 % toward the page ground, with the client's screen standing on it uncropped.
- **Tile and section labels** ("GAMES", "NEVER STOP GROWING" and the like): the data has no label for a feature, a
  feature list or the statement, so those lines are absent; the walk's labels are `steps.items[].k`.
- **Tile text**: the reference's tiles carry a head only. `features.items[].d` is set under the head (16/20) so the
  feature is not reduced to its name (**chosen**).
- **Rating badges with laurels**: drawn marks, not taken. The small figures stand as number over label.
- **The interface fragments on the outcome cards** (a phrase chip, a streak row) are the reference's product. The
  frosted panel carries the feature's own sentence instead. The photographs of people are replaced by made landscapes.
- **QR code, store badges with marks, language menu, social marks, the two labelled link rows of the foot**: no data.
  The pills carry the client's own two calls as plain words.
- **"Scroll to Explore"** words are not in the data; the line takes `hero.note` and sits in the flow between the product
  and the pills (the reference lays it over the phone's foot, where it would not be readable on a client screen), and
  it stays when the page moves (the reference fades it out).
- **Plan tiles** have no counterpart on the reference; they are assembled from its tile, figure, row and button parts
  and stand two (or three) across in the 1200 column, one column on a phone.
- **The questions' dialog** (blurred page behind, close button, contact line with an e-mail) is not reproduced: the rows
  stand in the page so they are read without a click; no contact line because the data has none.
- **Phone bar**: the reference shows its two audience links there; the data has no such pair, so the phone tray carries
  `signin` and `cta`, the call filled like the reference's current item (**chosen**). On the desktop tray no item is
  filled because none of the links is the current page.
- **Phone close**: the reference repeats its mark above the head; not reproduced.

## Image slots

| Slot (`data-slot`) | Where | Reference shows | Takes | Now |
|---|---|---|---|---|
| `hero-backdrop` | whole first screen | filmed desk scene, product in hands | `made.land` 0, else 5, 2, 1 — first whose tone agrees with the page | sportbot ridge · automateed rock |
| `walk-field-N` | the picture's half of the held screen, one a step | coloured glow | `made.land` of the page's tone, the opening's first | filled |
| `tile-field-1..3` | the three panes | product film | `made.land` of the page's tone, veiled 55 % toward the ground | filled |
| `result-card-N` | 440×400 cards | photographs of people at work | `made.land`, squarest first, not the two backdrops | filled |
| `close-backdrop` | whole closing section and foot | filmed desk scene | `made.land` 2, else 5, 1, 0, 3, 4 — tone agreeing, not the opening's | sportbot water · automateed valley |

Without `media.made` every slot falls back to the plain ground (the opening and close stand on the page colour, the cards
on ink 8 %). Still without a picture of the right kind: the opening and close would want a photograph or film of the
client's product in use; the outcome cards would want photographs of the client's users. None was invented.
The client's own pictures are handed out once each where there are enough (`_Pool`): steps keep their own; the opening
takes an unused phone screen, else a desktop screen; the tall tile an unused upright picture, the wide tiles screens.

## One picture family

Motif: **land**. The reference repeats one photographed scene (its desk film opens and closes the page; its cards are
photographs), so every slot here takes the made landscapes and no other kind; `blur`, `sky`, `sheet` and `field` are not
used. On the dark page no large ground takes a light picture (the series is filtered by tone).

## Picture share (`tools/coverage.mjs`, 1440, 2026-11-12)

| Page | Share | Per 900 px screen | Screens with a wide picture |
|---|---|---|---|
| reference | 22 % (20 % on an earlier run) | 100, 53, 15, 0, 0, 0, 0, 0, 0, 0, 11, 35, 0, 0, 40, 0, 87, 100 | 3 |
| sportbot | 24 % | 100, 47, 10, 0, 0, 0, 0, 17, 28, 33, 10, 0, 7, 100 | 2 |
| automateed | 26 % | 100, 47, 10, 0, 0, 0, 0, 14, 31, 14, 16, 69, 100 | 2 |

(Read with plans and questions in place; they are plain grounds, which is why sportbot fell from 28 %.)
The reference's wide pictures are its opening and its close (the close spans two of its screens); ours has both. The
zeros in the middle of both pages are the held walk: the tool reads the sticky block once, where it first stands.

## Checks

`tools/shots.mjs` on both outputs at both widths: lines in the hand-back report. `tools/legible.mjs`: ok for both clients. Own audit (`probe/audit.mjs`): text
contrast against rendered pixels at stops down the page, focus ring on every focusable, running animations and hidden
text under reduced motion, hidden content with the page's script removed — results in the hand-back report.
