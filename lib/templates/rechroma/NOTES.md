# rechroma — notes

Reference: https://rechroma.com (home), measured 2026-11-12 at 1440×900 and 390×844. No cookie wall, nothing accepted.
Probe scripts are in `probe/` (run with `tools/run.sh node rechroma/probe/<name>.mjs` from the templates folder); raw
readings: `probe/dom-d.txt`, `dom-m.txt`, `styles-d-end.txt`, `styles-d-story.txt`, `pseudo.txt`, `sweep-d.json/.txt`,
`chars-d.txt`, `chars-d-p1.txt`, `intro-d.txt`. Reference frames: `ref/steps/d-<scrollY>.jpg` every 300px, contact
sheets `ref/sheet-*.jpg`, the opening over time `ref/sheet-intro.jpg`, the open phone menu `ref/menu-m.jpg`.

## Sections of the reference, and the data each takes

| # | Reference (measured) | Ours | Data |
|---|---|---|---|
| 0 | Nav: fixed, 8px from the edges, two floating plates 72 high r12 (logo 248 wide; right panel pad 24 with a group of three equal toggles 121×34 — mono 14/500 +1.25 upper, a 12px lamp each, the current section's lamp lit — and a dark button). Absent on the first screen, drops in after ~150px of scroll. Phone: logo plate 184 + a 68 plate with a 44×36 menu button; menu panel 159 wide r8 pad 4, items 32 high, a divider, the door link | same; toggles are the client's nav links (up to 5), lamps light on hover/focus (the links leave the page, there is no "current section"); dark button = sign-in | `brand`, `nav`, `signin` (else `cta`) |
| 1 | Opening, section 1620 (stage pinned 720 = .8 screen). Full-stage canvas: the name in square blocks 1072×98 at y280–378 (phone 312×32); h1 50/60 right-aligned in a 640 box whose top is the middle of the screen, inset 10%; one button 36 high under it, gap 16; an arrow of 4px squares 90 from the bottom. Phone: h1 37/1.15, block top at 35% | same anatomy; the name is set in a plain 5-row block alphabet of our own (the reference's 3-row letterforms are its logo and are not taken), width min(80vw−80, 33px per cell) | `brand.name` · `hero.title` · `hero.text` (the lead, 24/31.2 right-aligned between h1 and button — the reference has no lead; its secondary text size is used) · `hero.primary` (else `cta`) |
| 2 | Story, pinned for 14400px (16 screens): left column 573 (copy centred on the screen's height), gap 43, right column 776 holding one plate (r16, 4px ring, face inset 4, pad 28, 464–690 high) in which a live product demo builds itself. Panel 0: a 50/60 sentence, then a 34/44.2 paragraph in its place. Panels 1–3: h2 50/60 + p 34/44.2 (544 wide), a new plate each. Phone: not pinned — copy (39/.98, 26.5/1.04) then plate, 48 apart, panels ~70 apart | same; the plate holds the client's product picture whole at its own proportion (max 634 high) | `statement.title` (sentence) + `statement.text` (paragraph) + `media.video` else first screen · `steps.items[title,text,img]` |
| 2a | — (the reference's home page has no figures) | Figures: one plate, the figures side by side in it; each is the reference's price pairing — the number in the pixel face at 50/50, a mono 14 upper label under it. Phone: stacked, number 40 | `figures[v,l]` |
| 2b | — (no feature list on the reference) | Features: the pricing head (h2 40/52 + p 24/31.2), then one plate holding checked rows in three columns — the plan rows' 18px check, a name at 24/31.2 pixel, the description mono 16/20.8. One plate, not a row of cards. Phone: one column | `features.title/text/items[t,d]` |
| 3 | Pricing: h2 40/52 left, a monthly/yearly switch right; two plates 684 wide gap 24, pad 28+14.4: name 40 (the paid plan's in a second colour, with an icon and a tag), price 50 with "/ month" mono 14 upper under it, rows mono 16/20.8 with an 18px check, a 12.24 mono note, a wide button 88 high (label top-left, mark bottom-right) | same without the switch, icon and tag (no data); `plans.text` under the head in the reference's own h2+p pairing (24/31.2, from its last section); `plan.line` in the note slot; `plans.note` as one more note under the plates | `plans.title/text/items[name,price,per,rows,line,cta,marked]/note` |
| 3a | — (no questions on the reference) | Questions: the last section's grid (head 573 left, plate 776 right); in the plate each question is a toggle row — pixel 24/31.2 with the nav toggle's 12px lamp at the right, lit while the row is open — the answer mono 16/20.8, rows parted by a 1px rule. `<details>`; the first is open | `faq.title/items[q,a]` |
| 4 | Last section, one screen high: h2 40/52 + p 24/31.2 left (573), plate right (776) with an e-mail field and a button | same grid; the plate holds the wide button — the client has no mailing-list form and none is invented | `close.title/text/cta` |
| 5 | Foot: one row pad 24 — 40px mark left, mono 14 upper links centre, © right | same; `foot.text` as a 12.24 mono note under the row | `brand`, `foot.links/legal/text` |

Data with no place, left out (also listed under "drops" in `needs.json`): `hero.kicker/text2/secondary/note`, `trust`,
`steps.title/text`, each step's `k` and `cta`, `links`, `quotes`, `logos`, `media.photos`/screens that no step names.
An `alt` is only ever an `alt` (a step picture without one takes the step's title as its alt, never as display copy).

## Length (pass of 2026-11-12: "a software site must be functional, not constant scroll")
| at 1440×900 | before | now |
|---|---|---|
| sportbot, whole page | 18046 | 8663 (with three sections it did not have before: figures 297, features 827, questions 588) |
| automateed, whole page | 17870 | 7455 |
| opening | 1620 (pinned .8 screen) | 1260 (pinned .4 screen) |
| story | ≈14600 (4080 + 3600 + 3600 + 2420 of held scroll) | 4150 (one screen + 3250 held: 1220 / 880 / 880 / 510, 80 overlapping) |
| pricing, close | each at least one screen high | their own height (1006 / 376 on sportbot) |
At 390 the page is 10348 (sportbot; was 8211 — the three new sections add 2894, the opening pin lost 338) and 7611
(automateed; was 6766). The story is not pinned on a phone.
Each hold is the least that shows its content once: a plate lands in 300px of scroll (the same damped overshoot,
compressed from 580), its head types over 180 and its paragraph over 280–310 while it lands, the picture grows over 260,
the finished panel stands about 150, then drifts 46px and leaves in 290. The statement keeps its two beats (sentence,
then the paragraph in its place).

## Measures used
Ground one flat colour for the whole page. Margins 24 (phone 16). Section padding 96 24 24 (phone 104 16 64).
Columns 573fr / 776fr, gap 43. Radii: plate 16 (face 12), nav plates 12, buttons 7, toggles/menu items 8→6 inside a
1px ring, picture 6. Type: h1 50/60 (phone 37/1.15) · story 50/60 and 34/44.2 (phone 39/.98, 26.5/1.04) · h2/h3
40/52 (phone 32) · close text 24/31.2 (phone 20) · price 50/50 · mono 14/500 +1.25px upper (buttons, toggles),
mono 14/400 +.75px upper (labels, foot), mono 16/20.8 (rows), mono 12.24/1.3 (notes).

Colour relations (reference → ours): ground L.8 → `palette.ground`; ink L.3 → `palette.ink`; small text L.4 → ink
raised to ≥4.6:1 on ground and face; raised face L.9 → half-way from ground to white (dark ground: 13% ink);
ring L.1, darker than the ink → half-way from ink to black (dark ground: drawn in the ink's direction, 62% ink —
a ring darker than a near-black ground cannot be seen); inverse button L.4 with L.95 text → 82% ink with a light
text (dark ground: 88% ink, ground-coloured text); pressed L.5 → 62% / 50% ink; the one yellow of lamp and hover →
`palette.accent` (hover face = accent mixed into the face, held where the label keeps 4.6:1); the paid plan's violet
name → `palette.extra[0]` if it reads 3:1 on the plate, else the accent, else ink. Shadows as measured (light from
the top left: white −3/−3/10 and black 8/8/16 on raised things, inset when pressed); on a dark ground the white
shadows are held at 14% so they do not read as a glow.

## Font stand-ins
None needed: the reference's faces are open-licence and on Google Fonts — Geist Pixel (all display text), Geist Mono
(buttons, labels, rows), Geist (body default). Geist Pixel exists there in one weight (400); the reference asks for
500/600 of the same file, ours asks for 400 with synthesis off.

## Motion — measured, and what is reproduced

| Measured on the reference | Ours |
|---|---|
| Opening on load: black cover over the stage; block outlines appear one by one, fill, the cover fades to the ground over ~2.8s; then the h1's letters come in left to right (each from 14px right, fading), the button fades in, the arrow's 14 squares appear one after another and redraw about every 4.3s. On the reference this starts ~4s after navigation and ends at ~10s | yes, same order, shortened: outlines 0–.7s, fill .3–1s, cover fade .9–2.5s, letters from 2.3s (20ms apart, .34s each; they fade in place — the 14px slide per letter is not kept, see "Typed copy"), lead and button +.25s, arrow squares 65ms apart on a 4.3s loop |
| Opening on scroll: stage pinned 720px; h1+button opacity falls linearly to 0 over the pin; the blocks take colours, then fade (coloured by 300, mostly gone by 600) | yes, at half the length — pinned 360px (.4 screen); blocks take the client's palette colours over the first .12 screen, fade between .16 and .38 |
| Nav: opacity .18s ease-out, transform from −88px .72s cubic-bezier(.34,1.56,.64,1); out at scroll 100, in by 200 | yes (threshold 150) |
| Story is pure scrub (held 3s at one position: nothing moves). Letters: each letter its own span, opacity 0→1 in sequence; a 50px sentence types over ~320px of scroll, a paragraph over ~530–650px; a block fades out whole over ~150px | yes in kind, shorter: a head types over 180px, a paragraph over 280–310 (each letter fades over 70px); a block fades out whole over 100 |
| Plate: holds, drifts down 46–55px over 500px, leaves upward past the top with opacity falling to 0 over ~600px; the next rises from below the screen over ~580px, overshoots by ~50px and settles (readings 623 / 60 / −51 / −32 / +5 / 0 px at 14 / 31 / 48 / 65 / 83 / 100% of the entrance) | yes in kind — the same damped-cosine fit, run over 300px instead of 580; drift 46px over 90, exit on a cubic over 200 |
| Inside the plate the demo builds itself after the plate lands (in panel 1 a picture grows from ~40% to full over ~600px) | the picture grows .4→1 and fades in over 260px as the plate lands |
| Panel lengths 4080 / 3600 / 4300 / 2420px at 900 high | 1220 for the statement (two beats), 880 per step, 510 for the last; scaled by screen height/900 — see "Length" |
| Phone: opening pinned (675px); story not pinned, letters type as a block crosses the middle of the screen | yes |
| Buttons: face and shadow .15s ease; hover = face tinted with the accent; press = mid-grey face, light label, inset shadow. Toggle hover the same tint. Foot links underline on hover | yes |
| Plan head and action fade in when the plates come into view | yes (.6s) |

Not reproduced: the live demos themselves (3D colour space, draggable handles, colour wheel, scale editor — the
reference's product); the monthly/yearly switch and the price roll; the foot's flipping theme tile; the hero blocks'
exact per-cell colour order. Whether the 14400px is tied to screen height was not tested (one height measured).

## Typed copy (how the letter reveal is built, and why)
The h1 and the story copy are real text in the page's ink: one `<span class="w">` per word, nothing duplicated, nothing
`aria-hidden`. The letters are let through one after another by a CSS mask on the word — one hard-edged gradient stop
per letter, at that letter's measured edges (`Range` rects), alpha 0→1 in steps of .05. Before this pass every letter
was its own span beside a clipped copy for readers, and `tools/legible.mjs` (which ignores text nodes under 2
characters) never judged the h1 or the story. Now it does: with the copy's ink forced to #2a2a2e on sportbot the gate
printed 86 FAILs (50 at 1440, 36 at 390) naming the h1's and the story's words; with the real ink it prints ok.
Not judged even so: one-letter words ("a", "—"), and at 1440 the statement's paragraph, because the gate's fixed stops
(every 820px) fall where that beat is not up — it is judged at 390, same ink, same ground.

With reduced motion: no cover, no typing (no word spans, no masks), no pin (the stacked build), arrow still, nav
without transition. Without scripts: the same stacked build, the name as an inline SVG of the same blocks, nav always
present; closed answers stay closed (`<details>` needs no script).

## Owner's rules against the reference
- **Picture in a box beside text.** The story's plate is exactly that, and it is the reference's whole idea, so it is
  kept — with the client's screen whole and uncropped inside it, plate height following the picture. See "Unsure".
- No made pictures are used: the reference has no photograph, backdrop or band anywhere — one flat ground and plates.
  `media.made` is not read. The motif is "none" (`needs.json`): product screens only, no made pictures.
- No eyebrows, pills or reveals beyond the reference's own. The square arrows are the reference's device (drawn here
  from our own squares); the check mark is our own.

## Image slots
1. Opening: full-stage `<canvas>` with the name in blocks (as the reference). No picture.
2. Statement plate: `media.video` (sportbot: the simulator film, muted loop) → else first of screens/phones/photos
   (automateed: the ebook maker screen). No picture at all → the panel is copy only.
3. Step plates: `steps.items[n].img` (sportbot: three phone screens 780×1616, shown 306×634; automateed: three book
   pages 800×1193). A tall narrow picture leaves the plate's face empty to its left and right.
4. Close plate: no picture (a button). Plans, figures, features, questions: no picture.

## Picture share (`tools/coverage.mjs`, 2026-11-12 after the pass)
| | 1440 overall | per screen | wide | 390 overall |
|---|---|---|---|---|
| reference | 6 (18832 px) | 100, 0, 16, 0 … | 1 | 13 |
| sportbot | 10 (8663 px) | 100, 0 … | 1 | 26 |
| automateed | 12 (7455 px) | 100, 0 … | 1 | 30 |

The first screen's 100 is the stage canvas in all three. At 1440 the tool reads the page at scroll 0, where the pinned
plates' pictures are still at opacity 0 / off screen, so they are not counted on either side (the reference's 16 on
screen 3 is its first demo canvas). Ours rose only because the page is shorter. The reference has no backdrop or band,
and ours has none.

## Checks (final run, 2026-11-12)
```
sportbot   d {"height":8663,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
sportbot   m {"height":10348,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
automateed d {"height":7455,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
automateed m {"height":7611,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
legible.mjs  sportbot: ok — 0 unreadable of 429 line readings · automateed: ok — 0 unreadable of 250 line readings
onefile.py   sportbot 0.9 MB · automateed 0.3 MB, nothing left un-inlined
```
`probe/audit.mjs <client>`: every Tab stop has a ≥2px outline (18/13 stops sportbot, 9/7 automateed, 1440/390 — the
question rows are stops); it lists the plan buttons as "faded when focused" (their .6s fade-in is still running at the
moment of focus; `:focus-within` sets them to 1). Reduced motion → stacked build, no animation. Scripts off → nothing
invisible but the three closed answers, no sideways scroll.
Closed answers are native closed `<details>`, nothing added: an earlier `opacity:0` hold (put in because the gate read a
closed answer at 3.86:1) was removed — `tools/legible.mjs` itself now skips text inside a closed `<details>`.
The fixed nav's two plates are opaque (`--plate`), so their labels are read on the plate whatever passes under; content
does pass under them and is cut by them, as on the reference.
`probe/tops.mjs <client> [width]` prints each section's offset and height.

## Unsure
- Whether a product screen inside the plate beside the copy passes "never boxed beside text".
- The ring on a dark ground is light (62% ink): a judgement, the reference only shows the light case.
- The story is now 3.6 screens of held scroll for four panels; whether ~150px of standing time per panel is enough to read a long paragraph on a fast wheel was judged from frames, not from use.
- Figures, features and questions are built from the reference's parts but have no counterpart on its page; trust, links, hero kicker/note still have no place.
- On a phone the page is longer than before (three more sections); the step pictures at 70vh each are most of it.
- `plan.line` in the 12px note slot and `plans.text` under the pricing head are pairings the reference does not state.
- The nav's lamps never stay lit (no current-section state for outbound links).
- Tablet widths (600–899) take the phone build; the reference's tablet build was not measured.

## Pass of 2026-11-12 (engine stress: five plans)
With five plans the plates fall into columns of 330 at 1440 (the measured `minmax(320px,1fr)`), leaving 245 inside a
plate; a plan name at 40 beside a 50 px price could not fit and the price ran 20 px past the screen. Rule now: the plan
head wraps — when the name and the price do not fit side by side, the price moves under the name and stays at the
right edge (12 px between the lines). Two plans (684 wide each) keep the reference's name-left / price-right line.
