# maze — notes

Reference: https://maze.co/ (home) and https://maze.co/pricing/ (plan cards only), read 2026-11-12 at 1440×900 and 390×844.
Cookie banner was never accepted; it was hidden with a style rule for the measuring shots. Probe scripts are in `probe/`
(they import `probe/lib.mjs`; run with `tools/run.sh node maze/probe/<name>.mjs`).

The earlier description was partly out of date: there is no "panel with a centred statement and a button" on the home
page today, and the big chips sit on a band that fades in. What is below is what was measured.

## Sections of the reference, and the data each takes

| # | Reference (measured) | Ours | Data |
|---|---|---|---|
| 0 | Black announcement bar 49px + white header 80px, fixed; leaves on scroll down, returns on scroll up | same | `hero.note` (+ `hero.secondary` as its link) · `brand`, `nav`, `signin`, `cta` |
| 1 | Pinned opening, section 1800px (2 × viewport). h1 130/300/1.05 two lines in an 800 box at x40,y263; grey lead 28/300 400 wide; pill + dark button; five tiles right: top row 192×171 and 348×310 bottom-aligned to the h1's last line, bottom row 311×248 · 177×247 · 311×247 starting x560, gaps 20, r8 | same anatomy; tiles keep their own proportion; a portrait tile is never narrower than the reference's 177 (see "Opening tiles" below) | `hero.title/text/text2/primary/secondary` · `media.video`, `screens`, `phones`, `photos` |
| 2 | Same pin, second scene: pixel disc ≈620px in the accent, centred 90/300 headline 800 wide + grey 22 text 520 wide | same | `steps.title`, `steps.text` (it introduces the tabs, as in the reference) |
| 3 | White card r20 pad 40: three tab words at 90px in 400×106 buttons (active: beige r16, 1px line filling along the bottom); below, 400 text column (h3 46, p 17, arrow link) and an 800×550 coloured panel r16 with a product picture | card, tabs, text column the same; **the coloured panel is gone — see "Owner's rules"** | `steps.items[k,title,text,cta,img,shape]` |
| – | Centred 58px line + logo marquee | dropped | `logos` (empty) |
| 4 | White card r16 pad 40, 720 high: row of small uppercase chips (14px, r8) as tabs, 90px heading, grey 22 text, pill + arrow link; 640×640 dark illustration right | chips; the link's name `t` as the big line (a title, as in the reference), its description `d` as the grey 22 text under it, pill with `t`; one screen shown whole on the card's own ground. The reference's second (arrow) link has no data and is left out | `links[t,d,h]` · `media.screens[2]` (or last) |
| 5 | Band: ground fades to the accent; 58/300 paragraph 1080 wide inset 40; two rows of 46px word chips (white, r8, pad 12, gap 20) running opposite ways, edges masked | same | `statement.title` (58) + `statement.text` (22) · `trust[]` as chips |
| 6 | Box r16 pad 112 on the band's fading ground: centred 58 heading (960 box), 17px text 440 wide, dark button; 3-column grid gap 20 of white cards r12 pad 16: bordered uppercase tag with 8px square + 22/300 text | same | `features.title/text/items[t,d]` · `cta` |
| – | Quote carousel | dropped | `quotes` (empty) |
| 7 | Mint card r16: tag, 58 heading, grey 22 text, dark button, report cover at right. Pricing page: two cards 670 wide gap 20, r16 pad 20; 58 name, 22 line, dark button, 260×378 picture panel r8; rule; 15px rows with 16px check | soft-accent band with heading and text, then the plan cards; the picture panel (a made blur, one calm hue per plan) carries the price | `plans.title/text/items/note` · `media.made.blur[n]` |
| 8 | Full-bleed photograph 876 high; white 58 heading; three glass cards 387×341 r12 pad 20 (white 50%, blur 40) with tag, 46px line, logo | glass cards on the made water/ridge photograph, darkened (plain deep ground when there is none), figure at 90/72/46 by length, label 17 | `figures[v,l]` · `media.made.land[2|0]` |
| – | (no FAQ anywhere on the reference) | FAQ built from the reference's own parts: r16 box, centred 58 heading, 22/300 rows on 1px rules, chevron | `faq` — left out whole when empty |
| 9 | Close, pad 208: 130/300/1.0 centred, 80px-high buttons (28px text, dark r16 + pill); pictures trail the pointer | same; one button (only one in the data), `close.text` at 22 grey added under the line | `close` · `media` for the trail |
| 10 | Foot: 4 columns of 240 with small grey column labels, newsletter card, logo at ~250px height, small uppercase legal row | columns without labels, brand name set very large, legal row | `nav`, `links`, `signin`, `cta`, `foot` |

Type scale used (desktop → 390): 130→52 (stepped down to 104→44 and 84→38 for longer titles, so a 9-word h1 holds three
lines) · 90→44 · 58→32.77 · 46→24 · 28→20 · 22→18 · 17→15 · labels 12–14 uppercase +0.03em. Weight 300 for everything
set large, 400 for body. Margins 40 → 16; card gaps 20 → 12; section rhythm 80 → 32.

## Font stand-in
The reference sets everything in **Phonic** (commercial). Stand-in: **Inter Tight** 300/400/500 (SIL OFL, Google Fonts) —
a light, narrow-set grotesque of the same kind. Inter Tight is already set tighter, so the reference's tracking
(-0.09em at 130px, -0.07 at 90, -0.06 at 58) is reduced to -0.045 / -0.04 / -0.035em to give the same colour of line.

## Colour
Client palette in, relations kept: quiet ground, cards one step lighter (light schemes) or one step up (dark), grey text
derived from ink and held at ≥ 4.6:1 on ground, card and chip; dark button = ink on ground; one bright band in the
accent with the text colour that contrasts best. The disc uses the accent only if ink reads on it at ≥ 4.6:1, otherwise
the accent mixed towards the ground until it does (sportbot: deep green, because the headline crosses the disc's edge
onto the ground and must read on both).

## Motion — measured, and what is reproduced
| Measured on the reference | Reproduced |
|---|---|
| Load (0–1.3s after first paint): h1 lines rise ~110px with opacity, second line ~90ms behind, lead and buttons after; tiles arrive from above/below, staggered; long ease-out | yes — lines split in JS, `1.1s cubic-bezier(.16,1,.3,1)`, 90ms stagger; tiles ±360px, 90ms stagger |
| Pinned opening over 900px of scroll: y≈100–200 headline and copy lift ~55px and fade; tiles shrink towards the centre and become accent squares (gone by ≈350); pixel disc forms ≈300–500; second headline rises ~270px and fades in 550–750; holds; "scroll on" pill leaves at ≈1250; page continues | yes, scrubbed with a short lag (lerp .16); disc drawn on a 2D canvas from 10px cells (8px on phone) with a noisy edge. The reference uses WebGL with hollow squares inside the disc — ours is a plain filled disc with an outlined rim while forming |
| Header: `transform .5s cubic-bezier(.4,0,.2,1)`, away going down, back going up | yes |
| Tabs: auto-advance, 1px line fills in ≈12s linear; tab ground and picture cross-fade `.5s cubic-bezier(.4,0,.2,1)`; click selects | yes; clock runs only while the card is in view and stops on keyboard focus; arrow keys move between tabs |
| Chip-tab card: `fade-in-up` 40px on a view timeline (entry 0–25%); picture cross-fade 1s | yes (`animation-timeline: view()`, shown plainly where unsupported) |
| Band: accent ground opacity 0→1 as the section enters (≈ top 870→690 of 900); each line of the statement from opacity .5 + blur 8px to clear as it passes ≈82%→52% of the viewport, line after line | yes, per line |
| Word chips: `60s linear infinite`, second row reversed | yes |
| Glass cards: white 50%→80% on hover, .5s | yes (14%→22% of the text colour) |
| Buttons: `.15s cubic-bezier(.4,0,.2,1)`; dark → lighter; pill → solid card colour + ink border; nav and foot links get a chip ground | yes; a press scales the button to .97 (the reference has no press state — added per the owner's "page answers a press") |
| Close: five pictures follow the pointer, each later than the one before | yes, behind the text, whole pictures |
| Reduced motion | pin released (two plain scenes, disc drawn full), no load rise, marquee static and wrapped, tabs do not advance, video shows its poster, header stays |

## Owner's rules that override the reference
- **No picture boxed beside text.** Reference tabs (3) put a picture inside a coloured 800×550 panel beside the text.
  Ours: the whole card takes the tab's colour (from `palette.extra`, text colour by contrast) and the picture stands
  free on that ground at its own proportion, 550 high. Same in (4): no dark square; one screen stands on the card.
- **Screens whole.** Every tile, tab picture and screen is `width × auto` at its own ratio; the opening's tile rows are
  justified by ratio instead of cropped to the reference's fixed boxes. The video is a tile at its own 924×758.
- **Opening tiles (changed 2026-11-12, phones were unreadable at 87 and 129 wide).** Top row, 540 wide, bottom-aligned
  to the h1's last line as in the reference: one portrait (first phone, else first portrait photo) at 177 wide — the
  reference's portrait tile width — and whole, so a phone screen is 177×367 and a book cover 177×264; the first screen
  takes the remaining 343. Bottom row (840, capped at 280 high): film and screens justified by ratio; a portrait joins
  it only if it still comes out ≥ 177 wide there (a book cover does: 188×280; a phone would be 135 wide, so it does
  not). Result: sportbot shows one phone, not two (phone 177×367 · screen 343×214 / film 341×280 · screen 359×280);
  automateed book 177×264 · screen 343×192 / screen 524×280 · book 188×280. Four tiles, where the reference has five.
  At ≤1100 the top row is the one shown, under the buttons as in the reference: portrait 36% of the width
  (129×267 for a phone at 390), the screen beside it, bottom-aligned.
- No words invented: the reference's "Scroll to continue" pill is a chevron only; foot columns have no labels; glass
  cards have no tags; the figures section has no heading.

## What could not be transferred, and why
- The WebGL dither/pixel treatment of photographs and the hollow-square texture inside the disc — imagery of theirs; the disc is a flat fill.
- Logo marquee and quote carousel — clients have no logos or quotes; left out whole.
- Mega-menu dropdowns, newsletter card, social row — no data.
- Plan picture panels and the report cover — see Image slots; the panel carries the price instead.
- The tab pictures on the reference are short product videos (mux); ours are the client's stills.
- 1101–1440 uses the desktop build with fluid margins; ≤1100 uses the phone build (the reference's tablet build was not measured).

## Image slots (pictures of a kind the clients do not have) — filled from `media.made` since 2026-11-12
1. **Figures backdrop** (`section.figs`, `data-slot="backdrop"`, full-bleed, ~660px high at 1440). Reference: a close,
   warm, low-key photograph, even enough for glass cards. **Takes `made.land[2]` (water) or `made.land[0]` (ridge),
   whichever has the darker `mean`** — both clients: water. `object-fit: cover`, lazy, `alt=""`. It is always darkened,
   on a light client too: a flat veil of the page's dark colour (ground on a dark page, ink on a light one), its share
   solved from `mean` so the result is ≤ ~25% (sRGB) and gives the text 7:1, and never under 0.6 — 0.6 for both
   clients since 2026-11-12, with the picture itself at `saturate(.45)`, because the water's orange reflections made
   the backdrop livelier than the reference's calm photograph. Cards and text
   take the page's light colour. Measured on the rendered pixels: backdrop mean luminance 0.015–0.032, brightest
   pixel 0.14 (sportbot) / 0.36 (automateed, the orange reflections). Without `made.land`: the plain deep ground as before.
2. **Plan panels** (260×378 portrait, r8, top right of each plan card; 180 high full width on the phone). Reference: a
   single-colour picture per plan. **Takes the calm ones of `made.blur`, in order, wrapping round** — never a light picture on a dark page; of the
   rest, as many as there are plans, those with the least colour in their `mean` and nearest the accent's hue
   (`calm()` in render.py) — (sportbot: green, teal — mint is light, red and rust are loud; automateed: cream, navy —
   the vivid blue and the orange flowers are not taken), `cover`, lazy, `alt=""`, `data-slot="plan"`. The price sits at the foot on a veil that fades out
   upward (full to 30% of the height, gone at 62%; on the phone full to 60%), veil and ink chosen by the picture's
   `tone`: dark picture → dark veil, light ink; light picture → light veil, dark ink. Without `made.blur`: the plain
   palette ground as before (accent for the marked plan). The marked plan is no longer told apart by the accent panel.
3. **Plans band cover** (right half of the soft-accent band). Still no picture; the band holds text only (left as it is).
4. **Link card illustration** (640×640, right). Unchanged: the client's screen, whole; text-only card when there is none.
5. **Opening tiles**: the reference mixes two photographs of people with product tiles. Clients have none; only product
   pictures are used. No made picture is used here (a made picture is ground, never a tile).

Text over the made pictures, measured from screenshots (text made transparent, lightest/darkest pixel under each text
box against the ink; worst case per kind):

| | sportbot 1440 | sportbot 390 | automateed 1440 | automateed 390 |
|---|---|---|---|---|
| figure (glass card) | 7.57 | 8.67 | 5.84 | 8.52 |
| figure label 17/15px | 7.72 | 9.17 | 8.72 | 8.55 |
| price | 8.15 | 7.23 | 7.42 | 7.90 |
| price line 15px | 8.77 | 9.00 | 9.54 | 7.70 |

At 390 only the glass cards in view (the first, and part of the second) were measured; the row scrolls sideways.

## Checks (`tools/shots.mjs`, final run)
```
sportbot   d {"height":9571,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
sportbot   m {"height":9018,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
automateed d {"height":8167,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
automateed m {"height":6979,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
```
`shots.mjs` does not test contrast, focus or reduced motion; `probe/audit.mjs` does (computed text/ground contrast for
every visible text while scrolling, 4.5:1 or 3:1 from 24px; a ≥2px outline on every Tab stop; marquee/pin state under
`prefers-reduced-motion`). Both clients, both widths, with and without reduced motion: 0 low-contrast texts, 0 stops
without a ring, 0 script errors. Limits of that audit: text over the moving disc is judged against the ground behind
the canvas, not the canvas pixels (the disc colour is held at ≥ 4.6:1 against ink by construction); only the first 59
Tab stops are walked.

Render time: 0.2–0.3 ms per client (`build.py`).

## Unsure
- The link card says the link's name three times (chip, big line, pill) — the data has one name and one description per link.
- Whether the opening's tile cluster and the free-standing tab picture satisfy "never boxed beside text" to the owner's eye — they are unframed and whole, but they do stand beside text.
- `hero.note` + `hero.secondary` in the announcement bar is a pairing the data does not state.
- The FAQ has no counterpart in the reference.
- sportbot's tab grounds come from `palette.extra` (deep green, brown, dark red); the brown and red were not judged by eye beyond the first tab.

## Pass of 2026-11-12 (one picture family, picture share, readability)
- **Motif.** The reference has one full-bleed photograph (behind the glass cards) and one single-colour picture per
  plan. Ours: `land` for the one backdrop (water, held quiet: veil 0.6, saturation 45%); the plan panels keep the
  reference's own device of one hue per plan, limited to the calm blurs (above). Nothing else on the page is a made
  picture; tab grounds and the band are palette colours.
- **Tab labels.** `legible.mjs` printed 2.06:1 for the two resting tab labels. Not a real fault: their colour was
  written as `color-mix()`, which the browser reports as `color(srgb 0.73 0.79 0.76)` and the tool reads as near-black.
  Rendered it is #bacac2 on #0e4b33 = 5.9:1. The colour is now computed in render.py and written as a plain hex
  (`--dim`, `data-dim`), so the tool reads what is on screen: the two lines no longer fail.
- **Picture share** (`tools/coverage.mjs`, share of page / per 900px screen):
  reference 1440: 26% [100,0,0,10,23,0,14,25,100,7,5] · 390: 25% [100,0,0,25,8,0,32,35,53,0,26]
  sportbot 1440: 21% [100,0,12,21,0,0,17,62,15,1,0] · 390: 21% [100,0,14,21,0,0,32,23,27,0,0]
  automateed 1440: 24% [100,0,17,10,0,0,37,56,0,0] · 390: 26% [100,0,20,0,0,30,54,0]
  sportbot stands exactly 5 points under at 1440 (4 at 390). The reference's one wide backdrop has its counterpart
  (figures); what the reference has more of is its logo/quote sections and the report cover, for which there is no data.
- **Readability** (`tools/legible.mjs`): automateed `ok — 0 unreadable of 241 line readings`. sportbot printed
  `ok — 0 unreadable of 359 line readings` in one run and FAIL lines in two others, each time for different word chips
  of the moving rows ("Public performance record", "iOS & Android", "Picks · live since 29 Sept 2026" … at 1.3–2.4:1).
  Judged a measuring artefact: the chips move ~40px/s, the tool reads a line's box and screenshots some 0.2–0.5s later,
  by which time the box lies partly over the gap between chips (the accent band), so light chip text is compared with
  the band. The crops show light text on dark chips. The chips were not changed.
- **Fixed header**: opaque card colour (announcement bar opaque ink colour), leaves going down and returns going up; it
  was read by legible.mjs at every screen at both widths with no failing line, and looked at over the plans, the
  figures backdrop and the tab card at 390 and 1440.
- `shots.mjs`: sportbot d 9571 / m 9018, automateed d 8167 / m 6979 — sideways 0, distorted 0, one h1, errors [].

## Stress pass of 2026-11-12 (CONTRACT.md "A template holds for clients it has not seen")
What the engine's gate found, and what was changed:
- **Sideways scroll with 3 and 5 plans.** The plan grid was `repeat(n, 1fr)` with n capped at 3: a `1fr` track cannot go
  under its content's own width, and the card (name + button beside a fixed 260 px picture panel) needs ~560. Now the
  tracks are `minmax(0,1fr)` and the row is laid out by count: 1 plan → one card, 670 wide (the reference's card width);
  2 or 4 → two across, the reference's card (4 = two rows); 3, 5 and more → three across, wrapping, and the card
  stacks — picture panel with the price on top (220 high, full card width), 46 px name, line and button under it —
  because 433 px cannot hold name and panel side by side. Names and prices may break anywhere rather than push the card;
  a button never exceeds its card. At 390 always one per row. Panels take at most two calm hues, in turn.
- **Figure labels 3.9:1 on another palette.** The glass card adds 14% (22% under the pointer) of the text colour to the
  ground under it, and the ground had been solved for the text without the card. Now the ground is solved for the card:
  with no backdrop picture the plain ground is taken away from its text colour until text reads ≥ 4.6:1 on the card at
  rest and under the pointer; with a picture the veil is raised until the same holds at ≥ 5.5:1 on the picture's mean
  (and 7:1 without the card). Computed in render.py from the palette, no value is tied to a client.
- **Never at rest.** Three things ran whatever was on screen: the word rows (CSS `infinite`), the link card's rise
  (a scroll-timeline animation, which the browser reports as running from the top of the page until the card has
  passed), and the opening film (it kept playing through the second, pictureless scene of the pin and below). Now: the
  rows have no animation while the band is off screen (`.band.idle`, IntersectionObserver); the rise is set from the
  scroll handler and only while the card is near the viewport; every film pauses when off screen and the opening film
  also while its scene is hidden; the tab clock's line is removed when the tab card leaves the view. Measured per
  900 px screen on sportbot at 1440 (`document.getAnimations()` running / films playing, 1.2 s after arriving):
  before — `up` on screens 0–2, `mq`×4 only where the band is, film playing on screens 0 and 1; after — nothing on any
  screen except the tab line while the tab card is in view, the word rows while the band is in view, and the film on
  the first screen.
- **Found by the variants, not by the gate's report** (both on the scratch palettes only):
  (a) *band heading unreadable while the band's ground fades in* (phone, 1.9–2.4:1 on a warm light and a deep blue
  palette): the band's text is set for the accent, but the accent ground was still at ~23% when the first line came on
  screen. The ground is now whole before the first line is on screen (it fades over the band's own top padding, at most
  20% of the viewport, instead of always 20%).
  (b) *a mid-tone accent carries neither text colour* (#c8502b: 3.8:1 with ink and with ground — statement text on
  the band, price line on the marked plan's plain panel): `colours()` now takes such an accent away from its text
  colour until the text reads 4.6:1. Neither test client's accent is touched by this (mint 14:1, orange 6.5:1).
- **Variants run** (scratch copies of both clients' data, `tools/shots.mjs` + `tools/legible.mjs`, 1440 and 390):
  1, 3, 5 plans · 2, 9 features · 1, 6 steps · 12-word h1 · 40-character button label (bar, opening, plans, close) ·
  no faq · no pictures at all (media emptied, no made pictures) — for sportbot and automateed; plus sportbot's data
  with a warm light palette (#f4ead9 / #2b1d12 / #c8502b) and a deep blue one (#0a1633 / #e8eefc / #4f8cff), each with
  and without made pictures. 26 pages. Results are in the hand-back; every page: sideways 0, distorted 0, one h1,
  errors [], legible ok.
- Seen in the variants and left: a 40-character primary button no longer fits beside the secondary in the opening's
  400 px copy column at 1440, so it drops to a second row and the opening grows past one screen (the pin is then
  released and the two scenes follow one another — nothing is cut); at 390 it wraps to three lines inside its half of
  the row. Six steps set the tab words at 30 px on two lines each. The "scroll on" chevron pill sits over the lower
  left tile of the opening at 1440×900 (also on the real sportbot page; not changed).
