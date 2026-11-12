# serus — notes

Reference: https://serus.ai (home), read 2026-11-12 at 1440×900 and 390×844. Niche: software sold to companies.
The cookie card was answered with "Reject all" (never accepted). Measurements are in `ref/` (`anatomy.json`,
`dom-d.txt`, `dom-m.txt` = every visible box with its type, radius, spacing, transitions; `hero-d.jpg`, `hero-m.jpg`,
`menu-m.jpg`, `popup.jpg`). Probe scripts are in `probe/` (run with `tools/run.sh node serus/probe/<name>.mjs` from the
templates folder): `probe1` boxes, `probe2` motion and states, `probe3` corner card and phone menu, `audit` our checks,
`pairshot` our section pictures.

The reference is a short page: bar, opening, trust row, two picture cards each with a row of four points, a
three-tile news grid, foot, and a small dark card that rises in the corner. It has no plans, no questions, no figures
band and no closing section. What the clients have beyond that is set in the reference's own parts (below, marked
"built from parts") rather than dropped.

## Sections of the reference, and the data each takes

| # | Reference (measured at 1440) | Ours | Data |
|---|---|---|---|
| 0 | Sticky bar 52 high (56 on phone), ground colour, no rule or shadow at any scroll. Logo 24 high at x16; links 13/500, gap 24, with dropdown panels; right: text link, dark pill, accent pill (36 high, pad 10 16, 13/500), gap 8 | same; links are plain (no dropdowns — no data); the dark pill appears only when `close.cta` differs from `cta` in both label and target (neither client) | `brand`, `nav`, `signin`, `cta`, `close.cta` |
| 1 | Opening: section top margin 56, pad 96 24, 632 high. 672 column: a 36px mark of pulsing dots, 16 gap, one serif line 40/1.15/-0.017em centred that is replaced every ~3.45s; ask-box 672×148, r32, 1px line, pad 10 16 16: a typed grey line 17/24 w450, 24 gap, a row of 36px r12 chips and a 48px round send button at the right; 24 below, a 12px grey note | same measures. The mark is the client's own mark at 36px (left out when its logo is a wordmark). The line cycles `hero.title` → `hero.kicker` → `hero.text` (each ≤ 64 characters); the h1 is always named by `hero.title`. The box is a **display, not a field** (owner, 2026-11-12: the typed grey line with a caret looked like an input one cannot type in): it shows one step at a time — the step's short name `k` at 13/500 grey over its `title` at 17/24 in the page's ink — replaced by a .28s fade every 3.45s; nothing is typed, there is no caret, the box has the default cursor and is not a click target; only its two links take focus. With the label the line block is 56 high and the gap to the row 16, so the box stays 148. One grey chip = `hero.secondary`; the pill carries `hero.primary` with a link arrow (not the reference's send arrow). With no steps and no features the box holds the row alone | `hero.title/kicker/text/primary/secondary/note`, `steps.items[].k/title` (else `features.items[].t`) |
| 2 | Trust row: 13/500 pale label, then a 896-wide row of grey marks 24 high, gap 80, opacity .5, edges masked 14%, sliding 36s linear; pad 48 above, 48 below | same row, no label (no words for it in the data). With no marks, the client's `trust[]` lines run as 15/500 text in the quiet grey (held at 4.5:1 — the reference's own row is far paler) | `logos` if any, else `trust[]` |
| 3 | Two picture cards 1392×870 (16:10), r32, pad 28, 64 apart: a photograph of the product on a device fills the card; top-left a 56px pill (17/500, pad 0 10 0 28) ending in a 36px round arrow; bottom-left h2 36/500/1.15/-0.02em and one line 20/1.4 w450 at 90%. 40 below each card a centred 896 row of four 212 columns (gap 16): 36px r8 icon tile, 15/500 name, 13 grey line | one card per step, same measures. Backdrop = a made landscape (cover); the step's own picture stands whole in the middle at its own proportion; pill = the step's link; h = `title`, line = `text` (max 600 wide, may run to three lines). The points are `features.items` shared out over the cards in order (7 → 3,2,2; 5 → 2,2,1), 212 columns centred, no icon tile (no icons in the data; the reference's are not taken). A 28/500 heading with a 15px line (the news heading's anatomy) stands before the first card — built from parts | `steps.title/text`, `steps.items[title,text,cta,img,shape]`, `features.items[t,d]`, `media.made.land` |
| 4 | News: pad 96 24 112; h2 28/500/1.3 left, small grey pill right; 3 columns gap 32: 16:9 picture r16, 20 below a 20/1.4 w450 title, 8 below a 13px grey date. The middle tile is not a photograph but a figure set large in grey on a grey tile | every tile is that figure tile: `figures[].v` large (700, sized to the tile by its length), `figures[].l` as the title. Heading = `statement.title` with `statement.text` as a 15px line. Four figures stand four across (3 otherwise). No pill, no dates | `figures`, `statement` |
| – | (no plans on the reference) | built from parts: the same tile grid — price in the tile, name as title, `per` as the grey line, `line` at 15, rows as 13px lines on hairlines, a 40px pill (dark when `marked`, grey otherwise — the two buttons of the reference's cookie card), `note` in small grey | `plans` — left out whole when empty |
| – | (no questions on the reference) | built from parts: the reference's opened phone menu — rows on 1px lines, 52 high, a 12px chevron at 50% that turns in .15s — as native `details`, 896 wide | `faq` — left out whole when empty |
| 5 | Corner card: fixed right 24 bottom 24, 320 wide, r24, near-black whatever the page, pad 16 16 24, an animated dither canvas behind the top with a gradient to the card colour from 123px down; logo in a 112 zone, 20/500 heading, 15/1.6 text at 70%, white 40px pill, 32px close button. Hidden below 1024. Opens once the page is scrolled past the opening (closed at 500, open at 800) | same card and behaviour (opens past 640). Picture = a dark landscape of the page's own series at 60%. Below 1024 and without scripts it stands in the page before the foot instead of being absent, so the client's closing words are never lost | `close.title/text/cta`, `brand.logo`, `media.made` |
| 6 | Foot: pad 64 24 24; grid 416 + 896, gap 80: logo 28 high, a 15/1.63 paragraph at 70% (384 wide), 12px address, store badges; link columns right-aligned, gap 128, 13/500 labels over 13/400 links at a 34 pitch; bottom row 13px pale: rights left, three links right | same grid; columns without labels (none in the data): `nav` · `links` not already in `nav` · `signin`/`cta` not already listed; bottom row `foot.legal` and `foot.links` | `brand`, `foot`, `nav`, `links`, `signin`, `cta` |

Phone build (measured at 390): bar 56 with logo, accent pill and a 40px round menu button; the panel drops under the bar
with link rows on hairlines, then a dark full-width pill and an outlined one (ours: `hero.secondary`, `signin`). Opening
pad 96 16, serif line 30.4. Cards go 3:4, full-bleed, no radius, pad 20, pill 40 high with a 28 round, heading 28.27,
line 16.155. Points in two columns of 171. Tiles one per row, full-bleed, no radius; titles 16.155; heading 22.125.
Foot columns two across; bottom row centred. Switches at 768 (card shape, bar) and 640 (bleed, two-column points), as
the reference's class names state.

## Font stand-ins
- Sans: the reference uses **Geist** — open-licence (SIL OFL) and on Google Fonts, so it is used as is (400/450/500/700).
- Serif line: the reference uses **Reckless** (commercial). Stand-in: **Newsreader** 400 (SIL OFL, Google Fonts,
  optical size axis) — a soft, low-contrast text serif of the same kind; same size, leading and tracking.

## Colour
Client palette in, relations kept: ground; ask-box one step lighter (light pages) or one step up (dark); chip, grey
pill and hairline at 5 / 8 / 9% of ink (7 / 12 / 14% on dark pages); secondary text = the reference's 70% ink; the
pale 45% ink is taken only as far as 4.6:1 holds on ground, box, chip and pill. Dark pill = ink on ground; accent pill =
accent with whichever of the two reads best. The corner card stays near-black with white text on both clients, as on
the reference. Card text is white with a dark veil on a dark picture, the page's dark ink with a light veil on a light one.

## Motion — measured, and what is reproduced
| Measured on the reference | Reproduced |
|---|---|
| Serif line: each letter `hero-letter-in .28s ease-out` (opacity 0→1, 2px rise), one after another (a 18-letter line is in after ≈0.75s); stands ≈2s; letters leave the same way first to last (`hero-letter-out`, 2px up); next line. Lines changed at 3.56 / 6.95 / 10.5 / 14.1s — a ≈3.45s cycle | yes — 28ms between letters in, 20ms out, 3.45s cycle (longer lines stand at least 1.8s). Words are kept whole when the line wraps; room for the longest line is reserved so the box below does not move |
| Ask-box: placeholder typed at ≈70ms a letter with a caret, stands ≈1.4s, cleared at ≈45ms a letter, 0.3s wait, next | **not reproduced** — typing with a caret says "type here"; ours is a display whose line changes by a .28s fade every 3.45s |
| Mark: 17 dots, `smp-pulse 2s ease-in-out infinite` (opacity .5→1, scale 1→1.5), out of phase | no — the mark is the reference's own logo; the client's mark stands still |
| Trust row: `trusted-scroll 36s linear infinite`, −50% | yes |
| Picture card: picture `all .3s cubic-bezier(0,0,.2,1)` to scale 1.03 and opacity .9 on hover; nothing moves with scroll (sampled at six scroll positions: no transform, no reveal; nothing starts hidden) | yes; no scroll-linked motion added |
| Bar: sticky, unchanged by scroll. Text links to opacity .6 in .15s `cubic-bezier(.4,0,.2,1)`; dark pill 23→102 grey; accent pill to a lighter accent | yes (dark pill mixes 38% toward the ground; accent 30% toward white) |
| News tile: picture to opacity .9, title to .7 on hover | not applicable — our tiles are not links |
| Corner card: `opacity` + 16px rise, .3s `cubic-bezier(.4,0,.2,1)`; after the first scroll past the opening; close button | yes |
| Dropdown panels: opacity .15s; rows take a 5% ground | no dropdowns (no data) |
| Phone menu: panel under the bar, chevrons turn .15s | panel yes (native `details`, closes on Escape or on a link); the two bars of the button cross in .15s |
| Press: none measured on the reference (its pill class lists `transform .15s`, no change seen while pressed) | pills and buttons scale to .97 while pressed — added, per the owner's "the page answers a press" |
| Focus: browser default 1px ring | 2px ink ring, 2px off, on every stop (white inside the corner card) |
| Reduced motion | the line stands as `hero.title`, the box shows its first step and does not change, the trust row stands still and wraps, no hover scale, no transitions |
| No scripts | title, first ask line, every section and the corner card (in the page) are present; nothing starts hidden |

## Owner's rules against the reference
- **No picture boxed beside text**: the reference never does it — its pictures are full card backdrops with the text laid
  over. Kept so.
- **Screens whole**: the reference shows its product inside a photographed device, cropped by the photograph. Ours: the
  client's picture stands whole on the made landscape, at its own proportion (≤ 62% of the card's width, the height
  between pill and text; 86% / 70% on phone), with a soft shadow. It is therefore a flat screen on a landscape, not a
  device in a still life.
- No words invented: no "used by" label, no column labels in the foot, no "all articles" pill, no dates.

## What could not be transferred, and why
- The pulsing dot mark and the dither canvas in the corner card — the reference's own identity and imagery.
- The still-life photographs (tray, keys, glasses; laptop on a stool) — pictures of theirs; see Image slots.
- The icon tiles over each point, and the icons inside the ask-box chips — icons are not taken and the data has none.
- Dropdown menus, model selector chip, attach button, store badges, address line, news dates — no data.
- The second (dark) pill in the bar — both clients' `close.cta` repeats their `cta`.
- `hero.text2`, `features.title/text`, `links[].d`, `media.video`, and screens not named by a step
  have no place in this build and are not shown.
- Widths between 768 and 1439 use the desktop build fluidly; the reference's tablet build was not measured (ours was
  only checked at 800 for sideways scroll).

## Image slots
1. **Card backdrops** (`data-slot="card-backdrop"`, 1392×870 at 1440, 390×520 on phone, cover). Reference: a pale,
   evenly lit still life with the product on a device at the centre. Ours: `media.made.land` in the order 3, 4, 1, 5,
   2, 0 (the two square, soft ones first — "a device stands on them"), wrapping; plain chip ground when there is none.
   Still missing: a photograph of the client's own setting with the device in it.
2. **Corner card** (`data-slot="corner-card"`, 320×~250 at the top of the card, at 60% over near-black). Ours: the
   first dark `media.made.land` not already behind a card (both clients: land 0, the ridge at dusk), else the first dark
   one; no dark landscape → plain near-black. (Before 2026-11-12 this took `sky` or a `blur` — another family.)
3. **Tiles**: the reference's other two news tiles are photographs (a team portrait, a hand holding a phone). Ours
   are all figure tiles, so no picture is needed; a client with news and pictures would need a different mapping.

## Checks (final run)
```
sportbot   d {"height":6602,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
sportbot   m {"height":8108,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
automateed d {"height":5875,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
automateed m {"height":6619,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
```
`probe/audit.mjs` (both clients, 1440 and 390, with and without reduced motion): text colour against the pixels behind
each text (text hidden, full-page picture sampled at 40 points per text; 4.5:1, or 3:1 from 24px): 0 low; 0 distorted;
0 script errors; Tab walk at 1440: 31 / 18 stops, 0 without a ≥2px ring; no-script: title, first ask line and corner
card present, 0 hidden texts. Limits: the letters of the changing line are judged only in the reduced-motion pass
(standing title); the corner card is judged where it stands in the page (390 and no-script), not while fixed over
moving content at 1440; closed FAQ answers and the closed phone menu are not sampled.
Measured against the reference at 1440: h1 block at y220, 672 wide; ask-box 672×148; trust row from y788; card
1392×870; corner card 320 wide at right 24 / bottom 24.

Render time 0.3 ms per client.

## Where ours still differs when the pairs are looked at
- Opening: with a title or line longer than ~38 characters the serif runs to two lines, so the ask-box stands 46px
  lower than the reference's (both clients). The reference's box holds three chips and a grey round button; ours one
  chip and a dark labelled pill — heavier at the right.
- Trust row: words in readable grey instead of pale marks — stronger than the reference's.
- Cards: a landscape with a flat screen instead of a still life; the text under the heading runs to two or three
  lines where the reference has one; on phone the screen is small (≈280 high) because that text takes room.
- Points: text only, and the descriptions run 3–5 lines in the 212 columns where the reference has one short line.
- Tiles: four across for four figures (reference: three); plans leave the third column empty with two plans.
- Foot: two or three short unlabelled columns against the reference's seven labelled ones — much lighter.

## Unsure
- Whether a flat screen standing on a landscape reads as intended to the owner's eye, or as a picture "in a box".
- `hero.kicker` and `hero.text` taking turns with the title in the h1 is a pairing the data does not state.
- Plans and questions have no counterpart on the reference; they are assembled from its parts.

## Pass of 2026-11-12 (one picture family, picture share, readability)
- **Motif: `land`.** The reference repeats one kind of picture — a pale photograph filling each large card. Ours: every
  picture on the page is from the landscape series (cards 3, 4, 1 …; corner card 0). No `sky`, `blur`, `sheet` or `field`
  is used. Figure and plan tiles stay plain chip ground (the reference's figure tile is plain grey).
- **Picture share** (`tools/coverage.mjs`, share of page / per 900px screen):
  reference 1440: 43% [10,95,80,43,0,0] · 390: 32% [7,64,56,73,0,0,0]
  sportbot 1440: 40% [7,84,78,80,45,0,0,0] · 390: 23% [0,60,67,53,0,0,0,19,8,0]
  automateed 1440: 45% [6,84,78,80,48,0,0] · 390: 28% [0,69,80,31,0,0,23,0]
  At 1440 both hold within 5 points. At 390 sportbot is 9 points under and automateed 4: the screens where the
  reference has pictures have them in ours (three card screens); what lowers the share is the length added by
  sections the reference does not have (plans, questions) and by all tiles being figure tiles where two of the
  reference's three are photographs. No picture was added there: four landscapes behind four figures is what the owner
  rejected.
- **Readability** (`tools/legible.mjs`): sportbot `ok — 0 unreadable of 443 line readings`; automateed
  `ok — 0 unreadable of 248 line readings` in the last run, and in an earlier run of the same page one FAIL
  (`m 2.54:1 "100+"`): the large tile figure half under the sticky bar, its box overlapping the bar's orange pill.
  Judged a measuring artefact (the bar is opaque; what is under it is not shown); nothing was changed for it.
- **Sticky bar**: opaque page ground at every scroll position, so nothing shows through it; judged by legible.mjs at
  every screen at both widths.


## Fixes for the engine's gate (2026-11-12)

The mark above the h1 keeps its own proportion for any shape: max-height 36, max-width 180, width and height auto (was a fixed 36x36 box that stretched a wide logo).
