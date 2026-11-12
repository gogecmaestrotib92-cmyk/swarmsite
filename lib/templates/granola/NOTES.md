# granola — template notes

Reference: https://www.granola.ai/ (home), measured 2026-11-12 at 1440×900 and 390×844 with `tools/anatomy.mjs`,
`tools/shots.mjs` and own Playwright scripts (element tree, sticky/fixed list, stylesheet keyframe values, scroll trace
every 90px, load frames, hover state). Raw: `ref.json`, `ref-d-*.jpg`, `ref-m-*.jpg`.
Kept apart below: **measured** (read from the live page), **built** (what render.py does), **judgement** (my decision).

## Sections of the reference, in order, and the data each takes

| # | Reference (measured, 1440) | In the template | Data |
|---|---|---|---|
| 0 | Header, fixed 8px from top, 56 high; logo left, 14px links centred, outlined + soft button right. After scroll: white pill, 0.5px stroke, shadow | same | `brand`, `nav`, `signin`, `cta` |
| 1 | Opening, 100vh: headline column left (720), product window right standing on three printed sheets | same; sheets are `made.sheet` pictures | `hero.title/text/text2/primary/note`, `media.screens[0]` (else `media.video`) |
| 2 | Second screen, 100vh, same window stays pinned at right: h2 48px, three 80px rows on a ruled sheet, dashed container edges | same, rows without icons | `hero.kicker` (h2), `trust[]` (rows) |
| 3 | One phrase at 160px, centred, that slides under a dark band; band: one 20px serif line + 6×2 logo grid with plus marks | phrase + inverse band carrying the statement text and the figures in the grid cells | `statement.title`, `statement.text`, `figures[]` |
| 4 | h2 48px set in the right half (160px above/below); then 600/600 grid: sticky label list left (top 96) with progress underline, three steps right (h3 24, p 16/24 max 448, square 600 picture r16), 96 apart | same | `steps.title/text`, `steps.items[]` (`k` → label, `img` → picture) |
| 5 | Lime band, 112 pad: small serif label, h2 108px/0.97 left (584), white card r28 right running off the page edge | accent band; h2 left (sticky), plan cards r28 right | `plans` |
| 6 | Dark band: h2 60 centred, rating line, sideways-scrolling quote cards 700×440 with 1px border | written only when present | `quotes[]` — both clients empty → left out |
| 7 | White, 128 pad: label, h2 108 (max 15ch), dark button; then groups 124 apart: hairline, h3 32 (820) \| p 22/29.7 (448), one picture 1280×527 r4 | same; rows run in groups, each group closed by one picture | `features`, `media.screens[1:]`, left-over `phones`/`photos`, `media.video` |
| 8 | Off-white band, 128 pad: label, h2 108, button, one h3 \| p row under a hairline, strip of logo tiles | band with h2 and h3 \| p rows | `faq` (automateed has none → left out). Logo strip needs `logos` → left out |
| 9 | Close, 749 high: full-width printed sheets; centred window-card 768 wide, r28, shadow 0 4px 50px, three dots, h2 88, p 24/32, filled + outlined button, card runs off the foot | same on `made.sheet` pictures | `close`, second button `hero.secondary` |
| 10 | Foot: four link columns (serif 24 heads, 14px links), socials, legal, wordmark 1200 wide | link rows (name serif 24 \| description 14), two plain link columns, small print, brand name fitted to 1200 | `links[]`, `nav`, `signin`, `foot`, `brand.name` |

Not fed by any data and left out whole: the announcement pill above the h1, the features dropdown, icons in the ruled rows,
the dark logo grid, the rating line, quotes, the logo-tile strip, social icons, foot column headings.

## Measures used (measured → built)

- Container 1280 with 40 gutters (text from x=120); features section container is 1280 edge to edge at x=80. Phone gutter 16.
- h1 86.4px / 0.93 / −0.02em, 4 lines, column max 562 (built 590). Phone 48px.
- Opening text 20/28; button 56 high, pad 0 24, full radius, 16px ~weight 430 (built 500 of Geist); note 13px grey with a 16px mark. Phone button 48, dark buttons full width.
- h2 48/1.0 (second screen, steps intro); very large h2 108/0.97/−0.02em (phone 60); statement 160/1.0/−0.015em (phone 46.8); close h2 88/0.98 (phone 36); h3 24/1.05 (steps), 32/1.05 (rows; phone 24); row paragraph 22/1.35 (phone 16); body 16/24; small 14 +0.01em.
- Judgement: client headings are longer than the reference's, so very large headings step 108 → 88 → 72 by length (≤24, ≤38, more characters); the statement is sized so a line fits 1320px (`--per` characters per line, two lines over 28 characters); FAQ answers are 17/1.55 instead of 22 because they run to 300 characters.
- Window: radius 12, shadow 0 20px 25px −5px /10% + 0 8px 10px −6px /10%, title bar with three dots (reference bar 44 high, 12px dots, 6.5 gap; built 36/10 on the smaller windows). Reference window is 384×576 (4:6), drawn 1.2× in the opening.
- Sheets behind the opening window (measured at rest, before the 1.2 scale): 441×552, 315×572, 384×682, all centred on the window, shifted (24%,−6%), (−35%,10%), (23%,21%) of their own size. Built with those sizes and shifts. Phone: 286×358, 215×390, 215×382, shifts (45%,8%), (−45%,8%), (40%,10%).
- Ruled sheet: 1px lines every 80px across the container. Built 80 (64 when more than four rows, so six rows fit one screen).
- Inverse band: 16 pad, lead line 48 below top, cells 200 high, plus marks 15px between cells.
- Step picture: square, r16, 24 below the paragraph. Coloured band 112 pad, card r28, shadow 0 8px 12px −4px /5%.
- Feature groups 124 apart (phone 80); picture r4, 527 high; split picture 439 | 833 with 8 gap.
- Close and foot as in the table.

## Typefaces (stand-ins, both OFL, from Google Fonts)

- Headings: reference uses a commercial light Clarendon-kind slab (`quadrant`) → **Besley 400**.
- Text: reference uses a commercial grotesque (`melange`) → **Geist 400/500** (700 for the foot wordmark).
Judgement: Besley is a little wider and darker than the reference face; sizes were kept, not shrunk.

## Colour relations kept (the client's palette goes in)

Reference: white ground, near-black ink, off-white surface, olive button, lime band, ink-coloured dark band with white type.
Built: ground = `palette.ground`; ink = `palette.ink`; surface = ground + 4.5% ink; card = ground lifted towards white
(light pages) or + 9% ink (dark pages); stroke = ground + 17% ink; primary button and coloured band = `palette.accent`
with ink or ground on it, whichever contrasts more; "dark band" = ink ground with ground-coloured type (on SportBot's dark
page this is a light band — the relation, not the darkness, is kept); picture grounds = `palette.extra` colours that differ
from the ground. Secondary text is mixed until it reaches 4.6:1.

## Motion — measured, and what is reproduced

Measured from the stylesheet's scroll-timeline keyframes and confirmed in the scroll trace:

1. **Opening window** — container two screens tall; window in a sticky layer (top 48). Over scroll 0 → 100vh, linear:
   `translate(25%, −6vh) scale(1.2)` → none. Phone: `scale(1)` → `scale(0.8)`, sticky top 96, ~530px of travel.
   Reproduced (rAF scroll handler writing transforms). Judgement: sideways start is 12% not 25%, and the window is 460 wide
   not 384, because the clients' screens are landscape and must be shown whole.
2. **Sheets behind it** — each runs over 50vh with `cubic-bezier(.7,0,.84,0)`, starting at 0, 6vh and 12vh: from its shift
   to centred at `scale(.75)` (phone `.2`); all fade 1 → 0 linearly between 60vh and 80vh. Reproduced with the same curve,
   offsets and fade. Judgement: end scale .55 on desktop so the sheets vanish behind a landscape window.
3. **Large phrase** — as the dark band passes the second half of its way through the viewport the phrase moves
   `translateY(0 → 130%)`, linear, and is clipped under the band. Reproduced. Unsure: which element the reference uses as
   the trigger; I used the band, which matches its screenshots.
4. **Steps list** — each label's underline fills `scaleX(0 → 1)` from the left while its step crosses the middle of the
   viewport; when passed it wipes out to the right in 0.5s ease; label colour changes over 0.5s `cubic-bezier(.4,0,.2,1)`.
   Reproduced; clicking a label scrolls to its step (reference labels are buttons; scroll behaviour not measured).
5. **Step pictures** — content inside drifts `translateY(10vh → −10vh)` while the picture crosses the viewport.
   Reproduced at ±2.5% of the square: the reference lets its window run off the picture, ours must stay whole.
6. **Header** — background, border and shadow 0.3s ease-out once the page has scrolled; header button turns to the accent.
   Reproduced.
7. **Hover** — primary button colour only (olive → darker olive), no movement, no press state measured. Reproduced as a
   colour change over 0.3s `cubic-bezier(0,0,.2,1)`.
8. **Load** — frames at 150–3000ms show no entrance sequence for layout; only the reference's window types its own
   content. Nothing reproduced (no load animation exists to copy).

Not reproduced: the typing/"enhancing" animation inside the reference's windows and its chat card, the small video-call
tile's parallax (12% → −45%), the logo-strip marquee, the foot's fixed reveal panel with cross-fading pictures, the foot
legal-line swap (0.7s `cubic-bezier(.87,0,.13,1)`) — each belongs to content the clients do not have.
`prefers-reduced-motion`: no scroll-linked transforms, the window is not pinned, transitions off, video does not autoplay
and gets controls.

## What could not be transferred, and why

- **Pictures.** The reference stands every window on a photograph or printed sheet; each such slot now takes a made
  picture of that kind (see Image slots), or a plain palette ground when the kind is absent.
- **Portrait window.** The reference's 4:6 note window cannot be made from landscape screens without cropping; windows
  take each screen's own ratio (owner's rule: screens whole). For the same reason nothing runs off a picture's edge and the
  plan cards do not run off the page edge.
- **Icons** in the ruled rows, **logos**, **quotes**, **rating**, **announcement pill**: no data; left out.
- **Coloured band content.** The reference shows a chat demo there; the band's anatomy is used for `plans` (judgement).
- **Inverse band content.** The reference shows a logo grid; the grid's cells carry `figures` (judgement). With a single
  row of cells the plus marks sit between cells, not at row crossings.
- **Inactive step labels** are grey at about 2.7:1 in the reference; built at 4.6:1.
- **Phone menu.** The reference's open menu was not measured; a plain disclosure panel is built.
- Owner's rule on pictures boxed beside text: the reference never does this on the home page (pictures sit under their
  text, full column width), so nothing had to be changed for it.

## Image slots (made pictures since 2026-11-12; plain palette ground when `media.made` lacks the kind)

Every slot is an element with `data-slot`, its background set to the picture's `mean` colour (or the palette fallback),
and inside it one `<img class="bgi" alt="" width height>` laid `object-fit: cover`. Opening pictures load eagerly, all
others `loading=lazy`. No glow, gradient or tint stands in for a picture anywhere. No text is laid over any picture in
this template (windows, phones and covers stand on them; the close's words stand on the opaque card), so no veil is used.

| Slot (`data-slot`) | Reference shows | Takes | Fallback |
|---|---|---|---|
| `open-back` 441×552, behind/right of the window | halftone burst print | `made.sheet[0]` | `extra[0]` |
| `open-left` 315×572, peeks left and below | accent paper, ruled scale, charcoal lower third | `made.sheet[1]`, anchored top-left so the scale shows | accent |
| `open-low` 384×682, shows below | pale paper, faint glyphs | `made.sheet[2]` | ground + 14% ink |
| `step-N` square 600 (phone 358), r16 | soft landscape photographs | `made.land[3]`, `[4]`, `[2]`, wrapping | `extra[N]` |
| `feat-N` 1280 wide, ≥527 high, r4 | wide landscape photographs | `made.land[5]`, `[1]`, `[0]`, wrapping | `extra[N+1]` |
| `split-left` 439×527 (carries the spare phone) | close crop of a surface | `made.blur[0]`, else `made.land[3]` | `extra[0]` |
| `split-right` 833×527 (carries the video) | alpine landscape | `made.land[1]`; when a feature picture of the same section already shows it, the first of `land[4]`, `[2]`, `[3]` the section has not used (judgement: not the same picture twice in one section) | ground + 14% ink |
| `shelf` 1280 wide (spare covers/phones) | no counterpart; nearest is a feature picture | next in the feature order after the last `feat-N` | last `extra` |
| `close-left` 38% | accent sheet with ruled scale | `made.sheet[1]`, anchored top-left | accent |
| `close-right` 62% | the burst, large | `made.sheet[0]`, drawn 1.08× so its paper margin does not show as a strip at the page edge | `extra[0]` |

Sizes, offsets and scroll behaviour of the opening sheets are unchanged (the sheet elements are the same boxes; the
picture is clipped inside them). Sheets are 3:4 and the slots are narrower (0.80, 0.55, 0.56), so cover crops their sides.

Still without a picture: the foot's fixed reveal panel (not built). `made.sky` and `made.blur[1:]` are not used here —
the reference has no such slot. The reference's hand lettering, numerals and thin ellipse on its sheets are not in the
made sheets. Sources are 1024–1344 wide: `land[1]` (1024) is drawn at 1280 CSS px in a feature picture and is soft,
more so on a 2× screen.

## Checks (tools/shots.mjs, run after the made pictures went in, 2026-11-12)

```
sportbot   d {"height":14179,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
sportbot   m {"height":13431,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
automateed d {"height":10845,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
automateed m {"height":9766,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
```
Heights are the same as before the pictures (no layout change). A DOM walk at 1440 found no text node inside any picture
slot. The earlier own audit (contrast of text on flat grounds 5.02 / 4.63 lowest, focus outline, reduced motion) was not
re-run in this pass; the grounds it measured did not change. With `made = {}` the page renders 0 pictures and every slot
keeps its palette ground. Between 1024 and 1439 the opening column is held to 36vw and the h1 to 5.4vw so the headline does not run under the
left sheet (it did at 1024 before; looked at 1024 on both clients and 1300 on automateed).

Render: 0.3–0.4 ms per client (build.py).

## Unsure

- Besley/Geist were chosen by eye against screenshots; not checked against the repo's type registry.
- Reference weights 430 (buttons) are approximated with 500.
- The phrase's trigger element (motion 3) and the reference's phone menu were inferred, not measured.
- Chunking feature rows around the screens is a rule of mine: a picture closes a run of rows, it does not illustrate a
  particular row. If screens should be tied to rows the data needs a field for it.
- `hero.kicker` is used as the second screen's heading and `hero.secondary` as the close's second button; the reference
  has no eyebrow above its h1 and one button in the opening.
- Only Chromium was run; Firefox/Safari not tested (the motion is plain JS transforms, no scroll-timeline CSS).

## Pass of 2026-11-12 (plans / questions kept, `alt` never copy, needs.json)

- **Nothing of the client's data is dropped**: every string of both data files is in the rendered text (checked by
  script; `plans` in the coloured band, `faq` in the surface band, `figures` in the inverse band). automateed has no
  questions, so that band is absent.
- **No `alt` is printed as copy.** The only crossing goes the other way: a step picture without an `alt` takes the
  step's title as its `alt`.
- **One fix**: with no screen and no film the second screen was still drawn up by one screen height and its heading and
  rows printed across the h1 (seen when sportbot was rendered with all media removed). The pull now applies only when
  the pinned window exists (`.pile.has-pin + .s2`). Output for the two test clients is unchanged apart from that class.
- **needs.json**: `holds_without_pictures` false — with all media removed the opening and the second screen are half
  empty; with only the made pictures removed every slot is a different saturated palette colour (brown, red, green
  squares under the steps), which is what the owner rejected. The template must be offered with made pictures.
- **Motif, said plainly**: two kinds are on the page — sheets behind the opening window and the closing card,
  landscapes under the steps and feature screens — plus one blur beside the film. Recorded in needs.json, not changed.
- Gates on the final build: `legible.mjs` ok (sportbot 569 line readings, automateed 285); `shots.mjs` clean, heights
  as before (14179 / 13431, 10845 / 9766); `coverage.mjs` sportbot 30 %, automateed 32 %, reference 31 %; one-file
  1.4 MB and 1.3 MB.
