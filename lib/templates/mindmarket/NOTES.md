# mindmarket — notes

Reference: https://mindmarket.com (home) and https://mindmarket.com/pricing (plan cards, numbered tiles, questions only),
read live 2026-11-12 at 1440×900 and 390×844. No cookie wall or loader stood in the way; nothing was accepted.
Measurements: `ref/anatomy.json`, `ref/ref-*.jpg`, `ref/sec-*.jpg`, `ref/pricing-*.jpg`. Probe scripts are in `probe/`
(`tools/run.sh node mindmarket/probe/<name>.mjs`): `tree` / `parts` (boxes, type, radii, transitions), `motion` (positions
and transforms sampled every 150px of scroll), `hover` (hover/press states, stylesheet rules), `par` (inner parallax, phone),
`css` (load rules), `pricing2/3` (pricing page parts), `pairs` (section shots), `audit` (our pages).

The reference's page is one long illustrated story: almost every picture on it is a character illustration (Rive
animations and SVG). None of that is taken. What is kept is the build around it.

## Sections of the reference, and the data each takes

| # | Reference (measured at 1440) | Ours | Data |
|---|---|---|---|
| 0 | Fixed bar 17px from the top, x109–1332: white bar r10, 68 high (mark + name, links 18/500 in 47px pills r50, round green menu button) and, 20px to its right, a separate white button r10 with a round animated face | same; the menu button is gone on desktop (no second menu in the data), the face is a plain accent disc with a chevron | `brand`, `nav` + `signin`, `cta` |
| 1 | Opening: green field, one viewport, pinned (the box is 900 high, its inner is 1800 with a sticky child); h1 139.68/500/0.95/−0.06em centred in a 968 box; 29.75 line 51px under it | same | `hero.title` (h1), `hero.kicker` (the line under it) |
| 1b | An illustration 748×547 stands at the foot of the opening (top at y635), stays pinned for 770px while the next panel slides up over the green, then leaves with it | the client's first screen, whole, in that place and with that behaviour (max 748 wide / 547 high) | `media.screens[0]` — without it the slot and its space are left out |
| 2 | Beige panel with 50px top corners slides over the opening. 29.75/1.2 paragraph 611 wide at x109, 109 below the panel's top; white button 38 under it | same | `hero.text` + `hero.text2`, `hero.primary` |
| 3 | A 4,600px illustrated path with four white tiles 513 wide (6 of 14 columns), r10, pad 53: h3 40.4/1.2, text 20.2/1.25, coloured button. Tiles sit right (x819), left (x109), centre (x464), right; figures fill the other side | tiles in the same columns, cycling right / left / centre; the step's own picture stands free and whole on the other side (centre tile: to the right, 12rem lower, as the reference's small figure does); one landscape is pinned behind the whole story as its backdrop | `steps.items[title,text,cta,img,shape]`, `media.made.land[1]` |
| 4 | Green band with 50px bottom corners, pad 170: line 139.68 centred; 29.75 paragraph 595 wide 85 below; white button; 255 lower three centred 18px lines in three columns; a figure rises at the left | same, without the figure | `close.title/text/cta`, `trust[0..2]` (the three lines only when there are three) |
| 5 | Full-bleed photograph, ratio 2268:1350, r50, moving inside its frame; a yellow ribbon with words runs across it | photograph in the same frame with the same movement; no ribbon (owner's rule) | `media.made.land[0]` — left out when absent |
| 6 | Beige block r50, pad 136/170. Left, sticky at 158: heading 80.75/0.95 over 690, text 18/1.25 355 wide (block 450 high, space-between). Right (x908, 424 wide), starting 340 lower: cards 424×550 r50 pad 34, round icon top right, figure 144/400/0.95, text 20.2 at the foot; white card with blue figure, then green, then red; they stick at 115 and stack 59.5 apart | same, no icons; figure steps down by length (144 → 112 → 84 → 58) | `statement.title/text` (left), `figures[v,l]` (cards) |
| 7 | Darker beige block r50: four pictures — 601×863, 601×515, two 291×249, r20, tags on top, title under (29.75 for the tall one, 20.2 for the rest) | same grid and sizes; each tile is the series' water surface held quiet, with one of the client's pictures whole on it; its `alt` is the title; no tags | `media.phones/photos` (first not used above → tall tile), `media.video`, `media.screens[1..]`; ground `media.made.land[4]` |
| 7b | Same block: centred 53 heading, three rails of pills (106 high, r64, white disc 64 + name 20.2) drifting ~22px/s, alternate rows opposite | built, shown only with `logos` | `logos` (both clients: empty → left out) |
| 8 | Pricing page: 53/1.15 heading; numbered tiles 3 across, gap 17, r20, pad 25.5; 34px square r10 with the number, h3 20.2, text 18 at 80% | same, on the page ground with card-coloured tiles | `features.title/text/items[t,d]` |
| 9 | Pricing page: 53 heading; cards r20 pad 30 gap 21: name 29.75, line 14.9 at 75%, price 29.75/700, unit 14.9, rows 18 with a coloured dot, coloured button at the foot; the marked card has a 2px coloured border and stands 42.5 higher | same, in a deeper block r50; 2 plans → two columns | `plans.title/text/items/note` |
| 10 | Pricing page: 53 heading; rows 800 wide, r10 on the darker beige, 5px apart, question 25.5/1.2, round 43px sign; answer 17/1.5 | same (`<details>`) | `faq` |
| 11 | Yellow foot r50, pad 136/38: 20.2 text 335 wide + white button; two link columns from x908; 85 lower two huge words 139.68 with a wave under the second, addresses at x908 in 18px at 60%; last row copyright, badge, one link | same; the huge words are the brand's name (no wave), the 60% text is the legal note | `hero.note` + `cta`; `nav`, `links`, `signin`; `brand.name`; `foot.text/legal/links` |

Phone (390): bar 16px inset, 60 high, round 40px menu button opening a card-coloured panel of 27px links; opening not
pinned, h1 66.9 (54 / 45 for longer titles), picture at the foot full width; panel corners 35; intro 27px; tiles full
width (pad 25/20, h3 35.4, text 18.6) with the picture between them; call 66.9 line, no three lines (hidden in the
reference too); number cards 350×400 r35, sticky at 60, 41.4 apart; pictures in a sideways strip, tiles 304×260 r15;
foot in one column with a rule over the big name.

## Measures used
Grid: 16 columns, 20px gutters, 20px page padding, content in columns 2–15 (x108.75–1331.25 at 1440). Root 17px at 1440
and fluid (1.18056vw; held between 14 and 20px here), 16.08px on the phone; all desktop sizes are that rem.
Type (desktop → phone): 139.68 → 66.9 · 80.75 → 46.6 · 53.1 → 35.4 · 40.4 → 35.4 · 29.75 → 27 / 24.4 · 25.5 → 20 ·
20.2 → 18.6 · 18.06 → 16.15 · 17 → 16.08 · 14.9. Everything is weight 500 (figures 400, prices and numbers 700),
tracking −0.06em on display sizes, −0.04em on text, line height 0.95 / 1.15–1.2 / 1.25 / 1.5.
Radii: 50 (blocks, number cards; 35 on the phone), 20 (picture tiles, plan cards, numbered tiles), 10 (bar, buttons, story
tiles, question rows). Buttons: 66 high, pad 10.6, label pad 10.6, disc 43.
Long titles step down (≤20 characters 139.68, ≤34 → 108.8, longer → 90) so the block stays the reference's height; a
hyphenated word is never broken at its hyphen.

## Font stand-in
The reference's face reports as **Inter** (its own build, weight 500). Ours: **Inter** 400/500/700 from Google Fonts
(SIL OFL) — the same family, so no tracking correction was needed.

## Colour
Client palette in, relations kept: accent field for the opening and the call (text = whichever of ink/ground reads
better); page ground; cards one step lighter (white on a light ground, 10% ink on a dark one); a deeper block (9% / 4.5%
ink); a second strong field for the foot (the palette's second extra colour); buttons on tiles cycle the extra colours
with a card-coloured disc; the first number card is card-coloured with its figure in the first palette colour that
reads on it at 4.5:1, then accent, then the extras. Any field is pushed away from its text until 4.6:1.

## Motion — measured, and what is reproduced
| Measured on the reference | Reproduced |
|---|---|
| Load: bar starts above the screen and comes down, `transform .4s cubic-bezier(.5,0,0,1)` after .2s; title and line rise 80px, `.8s` same curve, delays .2s / .1s | yes |
| Opening pinned for one viewport while the panel covers it; its text scales 1 → 0.8 linearly over that viewport (0.951 at 221px, 0.884 at 520, 0.8 from 900) | yes (desktop only, as in the reference — phone: none) |
| Foot picture scales 0.913 → 1 over the first ~750px, pinned for 770px | yes |
| Story tiles drift +90 → −90px while crossing the viewport; figures ±18px (one ±135) | yes, tiles ±90, pictures ±18 (desktop; the reference has none on the phone) |
| Tile arrives: coloured ground scales 0 → 1 `.6s cubic-bezier(.17,.67,.3,1.33)`, white ground the same .2s later, then title / text / button fade in `.4s cubic-bezier(.455,.03,.515,.955)` at .3 / .35 / .45s, text and button from −10px | yes |
| Button hover: a second disc grows at the left (scale 0 → 1), the label moves 51px right, the right disc shrinks to 0, all `.4s cubic-bezier(.17,.67,.3,1.33)` | yes; also on keyboard focus; a press scales the button to .97 (no press state on the reference — added for the owner's "the page answers a press") |
| Bar links: a ground-coloured pill grows behind the word (scale .8 → 1, opacity `.1s`), .9 on press | yes |
| Photograph inside its frame: translateY = −0.1 × the frame's distance from the top of the viewport (−90 … +85px); the ribbon at half of that | photograph yes; no ribbon |
| Number cards: sticky, each starts turned ±10° (alternating, first to the left) and 110px low, straightening linearly over ~536px and upright ~146px before it sticks | yes on desktop; not measured on the phone, so the phone only stacks |
| Picture tile hover: picture scales 1.05 and turns ~2°, `.6s cubic-bezier(.38,.005,.215,1)` | yes, on the tile's ground picture (the client's picture on top stays still) |
| Rails: ~22px/s, alternate rows opposite, slightly faster while scrolling | constant 22px/s, no scroll boost (built; not shown for these clients) |
| Smooth scrolling (Lenis), page-change wipe, Rive figures reacting, dropdown menus | not reproduced |
| Reduced motion | all transitions and animations off, no scroll transforms, tiles shown, video stays on its poster, rails wrap |
| Scripts off | nothing is hidden: the hidden states exist only under `html.js`; pins and stacking are CSS |

## Owner's rules that override the reference
- **No drawn strokes**: the wave under a word (numbers heading, foot), the yellow ribbon with words across the photograph
  and the green drawn path through the story are not built.
- **Screens whole**: the picture tiles are `object-fit: cover` crops of photographs in the reference; ours hold the
  client's picture whole (contain) on the series' water surface held quiet. The opening's foot picture is whole; while pinned its lower
  part is below the fold, as the reference's illustration is — nothing frames or crops it.
- **No picture boxed beside text**: story pictures stand free on the page ground at their own proportion, offset from
  the tile like the reference's figures; they are not in a panel.
- No invented words: no tags on picture tiles, no kicker labels (the pricing page has them), no list headings inside plan
  cards, no heading over the rails; `steps.title/text` have no place in this build and are not shown.

## What could not be transferred, and why
- All illustration: the opening group, the story's figures and path, the hills that turn the story into the green band
  (ours meets it with a straight edge), the figure rising in the call, the small looping figures on plan cards, the face
  in the bar button, the icons on number cards.
- The ribbon's two phrases and the three programme illustrations have no data.
- Dropdown menus, the desktop menu button, addresses, badge and social link in the foot — no data.
- `steps.title`, `steps.text`, `hero.secondary`, `links[].d` are in the data and not on the page.
- 1000–1440 uses the desktop build with the fluid root; below 1000 the phone build (the reference's 700–1000 tablet
  build was not measured).

## Image slots — one picture family: `land` (pass of 2026-11-12)
The reference's photographs (the band, the four article tiles) are one warm photographic series; its illustrations are
not taken. Ours names ONE motif, the landscape series `made.land`, and every made picture on the page is of it.
`_land()` picks by index and by tone: a large ground takes a picture of the page's own tone (dark page → `tone: dark`,
light page → `tone: light`); a dark page never takes a light one; a light page falls back to any when none is light.
1. **Opening foot** (`data-slot="opening-picture"`, 748×547 max, centred, pinned). Reference: a group of illustrated
   people. Ours: `media.screens[0]` whole. No made picture (the reference has none on that screen: coverage 0); empty → left out.
2. **Story backdrop** (`data-slot="story-backdrop"`, new). Reference: an illustrated path fills the 4,600px story
   (37–90 % picture per screen). Ours: `made.land[1]` (then 5, 2 by tone) pinned one viewport high behind the whole story
   (`position: sticky`), under a veil of the page ground (45 % dark page / 50 % light page) and a 60vh fade from the
   ground at its top; it runs to the edge of the call. Words stay on the card-coloured tiles; nothing is set on the
   picture. Without `land`: plain ground, as before.
3. **Story pictures** (`data-slot="step-picture"`, up to 432×640, beside each tile). Reference: illustrated figures.
   Ours: `steps.items[].img` (phone screens / book pages), free on the backdrop. A step without `img` shows the tile alone.
4. **Band** (`data-slot="band-picture"`, full-bleed 2268:1350). Reference: a warm photograph of two people reading.
   Ours: `made.land[0]` (ridge at dusk). Wanted from the client: one landscape photograph ≥ 2400×1430 of its own setting.
5. **Picture tiles** (`data-slot="tile-ground"`): ONE picture under all four tiles — `made.land[4]` (the soft square
   water surface; then 3), a different crop per tile, under a veil of the block's ground (50 % dark page / 45 % light).
   Before this pass each tile stood on a different saturated `made.blur` hue (green, mint, red, rust) — removed.
   Without `land`: the tile is the card colour. Wanted: four real photographs with titles (the reference's are article covers).
6. **Plan card heads** (214–251px square at the top of each plan card): looping illustrations in the reference — nothing
   stands there; the card starts with the plan's name.
7. **Number card icons**, **rail logos**: nothing.
`made.blur`, `made.sky`, `made.sheet`, `made.field` are not used by this build.

## Picture share (`tools/coverage.mjs`, 1440)
```
reference  {"height":13732,"screens":16,"picture_share":39,"per_screen":[0,37,58,74,64,46,90,34,93,11,0,0,75,8,0,0],"screens_with_wide_picture":2}
sportbot   before {"picture_share":18,"per_screen":[14,10,18,17,16,0,84,36,0,0,32,50,0,0,0,0],"screens_with_wide_picture":2}
sportbot   now    {"height":14091,"screens":16,"picture_share":23,"per_screen":[14,34,80,17,16,0,84,36,0,0,32,50,0,0,0,0],"screens_with_wide_picture":3}
automateed now    {"height":12586,"screens":14,"picture_share":26,"per_screen":[13,36,79,21,14,13,100,7,0,0,55,25,0,0],"screens_with_wide_picture":2}
```
The tool reads the pinned story backdrop only where it stands at scroll 0 (one 900px box). Measured in the page: the
story block is 2,449px (sportbot) / 2,442px (automateed) high at 1440 and the picture fills the viewport for all of it,
so about 1,550px more of the page is picture than the tool counts: **≈34 % (sportbot) and ≈38 % (automateed)** by
viewport, against the reference's 39. The first 60vh of the backdrop is a fade from the ground. The reference's two wide
pictures are the hills that end the story and the band; ours are the story backdrop and the band.

## Readability (`tools/legible.mjs`)
```
sportbot    ok — 0 unreadable of 515 line readings
automateed  ok — 0 unreadable of 285 line readings
```
The bar is fixed, opaque (card colour, ink type) at both widths, so it reads the same over the accent field, the
backdrop, the band and the foot; the tool judges it at every screen.

## Checks
`tools/shots.mjs` (final run, after the 2026-11-12 pass — unchanged heights; the audit lines below are from before that pass and were not re-run):
```
sportbot   d {"height":14091,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
sportbot   m {"height":12552,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
automateed d {"height":12586,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
automateed m {"height":10519,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
```
`probe/audit.mjs` (computed text colour against the rendered pixels beside each visible, unoccluded text while scrolling;
4.5:1, or 3:1 from 24px; ≥2px outline on every Tab stop; state under reduced motion; a scripts-off screenshot):
```
sportbot   d motion low-contrast: [] distorted: [] tabstops: 29 no-ring: [] {"nav":"none","rise":"none","anim":[],"tilesHidden":0,"sw":1440} errors: []
sportbot   d reduced low-contrast: [] distorted: [] tabstops: 29 no-ring: [] {"nav":"none","rise":"none","anim":[],"tilesHidden":0,"sw":1440} errors: []
sportbot   m motion low-contrast: [["bet again","2.12 @54"]] distorted: [] tabstops: 24 no-ring: [] {"nav":"none","rise":"none","anim":[],"tilesHidden":0,"sw":390} errors: []
sportbot   m reduced low-contrast: [["bet again","2.12 @54"]] distorted: [] tabstops: 24 no-ring: [] {"nav":"none","rise":"none","anim":[],"tilesHidden":0,"sw":390} errors: []
automateed d motion low-contrast: [] distorted: [] tabstops: 16 no-ring: [] {"nav":"none","rise":"none","anim":[],"tilesHidden":0,"sw":1440} errors: []
automateed d reduced low-contrast: [] distorted: [] tabstops: 16 no-ring: [] {"nav":"none","rise":"none","anim":[],"tilesHidden":0,"sw":1440} errors: []
automateed m motion low-contrast: [] distorted: [] tabstops: 14 no-ring: [] {"nav":"none","rise":"none","anim":[],"tilesHidden":0,"sw":390} errors: []
automateed m reduced low-contrast: [] distorted: [] tabstops: 14 no-ring: [] {"nav":"none","rise":"none","anim":[],"tilesHidden":0,"sw":390} errors: []
```
The one flag (sportbot, phone, "bet again" 2.12) is a sampling artefact: that text node's first box is the space at the
end of the line above, so the sample fell on the glyphs of the preceding word; the h1 is ground-on-accent (≈14:1) and the
same line passes at 1440. In the scripts-off screenshot all text and tiles show; lazily loaded pictures below the fold
are blank in that shot because it was taken without scrolling.
Limits: the audit skips text in the fixed bar and text covered by another element (stacked number cards cover each
other's lower text, as in the reference); the ground is sampled 6px left of the first line only; hover states and the
phone menu's open state were looked at, not measured.

## Unsure
- Whether free-standing story pictures beside tiles pass "never boxed beside text" to the owner's eye.
- `hero.kicker` under the h1 and `hero.note` beside the foot button are pairings the data does not state.
- sportbot: dark screens on the near-black ground have almost no edge; the marked plan's border and row dots (deep
  green on the dark card) are faint.
- With four figures the fourth stacked card ends a few pixels under a 900px viewport; card height shrinks on shorter
  windows (min 22rem) and was not checked below 800px high.
