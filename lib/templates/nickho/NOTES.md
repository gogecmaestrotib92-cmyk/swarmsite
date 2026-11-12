# nickho — from https://nickho-motorsports.nl (measured 2026-11-12)

A racing driver's own site (Webflow, Lenis smooth scroll). One `<canvas>` sits in the first screen: a depth-map
effect over the opening photograph (the picture moves in depth with the pointer). The rest is a scrolling page of type
and photographs, so the brief's "canvas-led" stop does not apply; the canvas is reproduced as a small pointer lean of
the photograph. Measures in `ref/anatomy.json`, `probe/dom.txt`, `probe/motion-d.txt`, `probe/motion2.txt`.

## Sections of the reference → data

| # | reference (y at 1440) | ours | data |
|---|---|---|---|
| 1 | hero 0–900: one photograph, grey (saturate 0), black gradient over the lower third; 7 hairlines (white 20 %); stats left (Anton 32 + Helvetica 14), facts right-aligned (14, bold heads), giant "98" (Anton 200) centred, name h1 (Anton 50/1.1) + 14 px text bottom left, "Next race / TBA" bottom right | same grid | `media.photos` (first wide, see slots), `figures[0..2]` (the first also as the giant figure when ≤ 4 characters), `hero.kicker` + `trust[0..2]` (facts), `hero.title` (h1), `hero.text`, `hero.note`, `hero.primary`, `hero.secondary` |
| 2 | statement 900–1800: white, one centred quotation in Anton 50/1.1 uppercase, phrases in the accent; two small boxed photographs at its corners | statement centred, the sentences after the first in the accent (or the title when it is a sentence); `hero.text2` under it in 14 px | `statement`, `hero.text2`. The two corner photographs are **boxed pictures beside text — left out** (owner's rule) |
| 3 | logo wall 1800–3200: 4 columns of sponsor marks 177×118, inner columns raised 86 px, a pinned helmet cut-out in the middle | `logos` as that wall (neither test client has logos); `credentials` as rows of the ruled list (name, text, badge on the right) — they are named things, not marks | `logos`, `credentials` |
| 4 | history 3200–5716: black, pinned; title (Anton 50) left, upright 302×362 photographs in a column at x 515 that scroll through, text (14) right at x 949, "▪ n/5" bottom right; the current picture in colour, the others grey | same: titles and texts pinned at mid-window and swapped as each picture passes the centre; pictures grey/dim except the current one; counter | `steps.title/text` (white intro screen before it), a single `team` person as first slide (name, role, text, e-mail, portrait), `steps.items` (title, text, cta, img) |
| 5 | media 5716–6616: ghost word (huge Anton, 4.5 % ink, faded down), "MEDIA & ARTICLES" h2 + two 76×46 grey arrows (radius 4), a row of 416×312 cards at 16 px gaps running off the right edge, 14 px caption at 50 % | same carousel, scroll-snap + arrows | `projects` (title, text, first free photograph, link); `team` of 2+ people as cards (portrait, name, role, text, phone/e-mail) with the team title as ghost word |
| 6 | calendar 6616–7844: black; centred h2; rows: Anton 26 title, 14 px line under it, value (date) right-aligned at the row's foot, 1 px white-20 % rule, 83 px pitch; a car cut-out pinned in the middle | the ruled list, alternating black/light ground per block: `catalogue` (group heads as centred h2s; item name / note / text / rows; price, `from`, `prices[]`, `state` on the right), `plans`, `features` (unless they only repeat catalogue names), `faq` | `catalogue`, `plans`, `features`, `faq` |
| — | (no quotes on the reference) | quotations set as the statement part, one per screen width, with the reference's arrows | `quotes` |
| 7 | sponsor guide 7844–8546: centred h2 Anton 50, 14 px line, accent button | same | `close` |
| 8 | video 8546–9446: a film that grows from 1008×630 (radius 10) to the full window 1440×900 (radius 0) over 900 px of scroll, then parallaxes | same growth (70 % → 100 %, radius 10 → 0) on scroll | `media.video` or the second wide photograph |
| 9 | gallery 9446–10396: ghost word, a ring of square photographs (185–260) on a large circle, centre one in colour, a dial of ticks with an accent square, two arrows | same ring (8 slots at 45°, 270 squares on a 560 radius), dial, arrows, touch swipe | leftover photographs (3–8; ghost word = brand name) |
| 10 | contact 10436–11161: black, ghost word, one white card 1063 wide, radius 8, padding 64: heading + line left (258), form fields right (grey 5 % fills, radius 4, 37 high) | same card; the fields become the client's ways to reach: phone, e-mail, routes/social, address, hours, locations, then the form/booking button | `cta.t` (heading), `contact`, `place`, `locations` |
| 11 | footer: white, mark left, columns Menu / Socials / Contact (14 px, 50 %), credits line | same | `nav`, `links` (not already in nav), `foot.links`, phone/e-mail, `foot.legal`, `foot.text` |

A section whose data is missing is left out whole (checked with `probe/var/only-name.html`: header, first screen with the
name only, foot).

## Measures used (1440 / 390)
- Side margin 80 / 29 (we use 30); max 1600. 12-column grid, 16 gap (history uses columns 1–4 / 5–7 / 9–12).
- Display: Anton 50/1.1 h1–h2 (37/1.1 at 390), 26/1 row titles (19 at 390), 32/1 stats, 200 giant figure (146 at 390), ghost words ~190 stretched to the page width (scaleX, as the reference's SVG words are). Statement 50 → 29 at 390.
- Body: Helvetica 14/1.4 (15/1.4 at 390); captions at the reference's 50 % ink, held at ≥ 5.3:1.
- Section padding 128 (regular), 192 (call); first screen padding 80 80 60; footer 128 / 32.
- Button: accent block, 40 high, padding 12×16, radius 4, Anton 16 uppercase + a double chevron. Arrows 76×46, radius 4, 5 % ink fill.
- Contact card radius 8, padding 64; fields radius 4.
- Hairlines: 7 columns, 1 px at white 20 % on dark, ink 12 % on light (the reference draws them on its light sections too).

## Fonts
- Anton (Google Fonts, OFL) — the reference's own display face is Anton, so this is not a stand-in.
- Body: the reference sets Helvetica; we ask for "Helvetica Neue", Helvetica, Arial (system faces, nothing downloaded).

## Colour
The reference's relations are kept: white sections, black sections, one loud accent (yellow #fed60a) on buttons, the
menu tile, the counter square and accent phrases. The client's palette goes in: the lighter of ground/ink is the white,
the darker one taken down to ≥ 12:1 against white is the black (person1 #111111, local1 #212121 → slightly deeper),
the accent is the button fill (deepened if it carries neither black nor white at 4.5:1) and, deepened to ≥ 3.1:1,
the accent phrases in the 50 px statement.

## Motion measured → reproduced
- Menu: full-screen accent tile slides in; links Anton 64 (93.6 in the box) rise one by one: `transform .75s cubic-bezier(.7,0,.3,1)` with 0.05 s steps; the burger's colour changes after .3 s. → reproduced exactly (Escape closes, focus returns).
- Buttons: label rolls up and a copy rolls in, `translate .6s cubic-bezier(.19,1,.22,1)`; press `scale .15s cubic-bezier(.4,0,.2,1)`. → reproduced (press scales to .96; the hidden copy is `visibility:hidden` until hover so it is never read as a second label).
- Hero: depth-map canvas moves the photograph with the pointer. → a small pointer lean (±8 / ±5 px, .8 s ease-out) on hover-capable pointers only.
- History: pinned 2516 px; the column of pictures scrolls at page speed with an inner parallax (−36 → +36 px over the passage); the current picture goes from saturate 0 to 1 (a 70 px crossfade); titles/texts swap; counter n/5. Measured: one wheel step settles in ~600 ms (Lenis). → titles and texts sticky at mid-window, current slide chosen by the picture nearest the window centre; picture parallax ±36 px; swap `opacity .45s cubic-bezier(.19,1,.22,1)`; inactive pictures grey at 32 % (the reference dims them the same way, measured visually). From 992 px down the slides stack (the reference does the same on the phone).
- Headings: words rise from a mask as they enter (`reveal-word`). → `clip-path` + 28 px rise, .9 s cubic-bezier(.19,1,.22,1), once.
- Video: grows 1008×630 → 1440×900 and radius 10 → 0 over the 900 px before it reaches the top, then moves at 0.4 × scroll. → width/height 70 → 100 %, radius 10 → 0 over 0.8 window heights. The trailing parallax is not reproduced.
- Gallery ring: rotates one step per arrow press; measured settle ~560 ms on an expo-out curve; pictures grow 187 → 260 toward the top. → `transform .64s cubic-bezier(.19,1,.22,1)`, the current picture in colour; sizes are kept equal (270).
- Media arrows: `transform .2s`. → same, plus disabled state at the ends.
- Lenis smooth scrolling and the custom cursor are not reproduced (they replace the reader's own scroll and pointer).
- Reduced motion: every transition .01 ms, no reveals, no parallax, no lean, the video/band shown full at once. Scripts off: everything is shown (the hidden/scripted states take hold only when the script has finished wiring, via `html.ready`); the menu then lives only in the foot.

## Image slots (client's own photographs; `media.made` is never read — the picture family is the client's photography)
- first screen: the first photograph in the data that is not small, ≥ 1400 wide, ≥ 1.3:1, not a portrait/people/product/detail, and not named by a person or project; a step's own picture only when its role is `landscape` (that step then stands in type). Shown grey, as the reference shows its own.
- band: the second picture by the same rule (or the video). Without one the band is left out.
- sequence: each step's own img, the single person's portrait; 302×362 crops (square on a phone, never wider than the column).
- project cards / people cards: 416×312.
- ring: what nothing else has taken, shorter side ≥ 270, not portraits/people; 3–8 or the ring is left out.
- person1: 9 of 9 used once each (bionassay first screen — its Consulting step then has no picture; hero.jpg in the band, with its own "YOU ARE HERE" lettering, which is the client's picture). local1: 19 of 20 (directors.jpg, the group of three, is not placed — the three are already shown as people cards).
- No alt is shown as text.

## Picture share (tools/coverage.mjs)
reference 19 % (per screen 100, 6, 0, 3, 17, 18, 28, 4, 0, 16, 44, 12, 0; 2 wide screens) ·
person1 17 % (2 wide) · local1 23 % (2 wide). Both pages are within 1.5 × the reference's height, so the overall share
is compared directly: person1 is 2 points below, local1 4 above. The reference's two wide pictures (first screen, video)
are in ours in the same order.

## What could not be transferred and why
- The pinned helmet and car cut-outs (logo wall, calendar): product cut-outs the client does not have.
- The statement's two small corner photographs: boxed pictures beside text (owner's rule).
- The contact form: the client's form lives on its own site; the card holds its real ways of contact and a link button.
- The countdown "Next race" — the client has no dated events; its place takes `hero.note` and the buttons.
- The loader with the counting number, Lenis, the custom cursor, the checkered-flag band under the calendar (a racing
  pictogram, not the client's).

## Variants (scratch copies in probe/var/, built by probe/variants.py) — shots.mjs at 1440 and 390
plans 1/3/5, features 2/9, steps 1/6, a 12-word h1, a 40-character button label, 4 questions, no photographs (person1 and
local1), only a name: every one renders with no sideways scroll, no script error, no distortion, one h1. legible.mjs
results are in the report.
- Without photographs the first screen is the black ground with the figures and the name; the sequence becomes type
  (title / text) and the ring and band are left out. It holds, but it is a type page, not this reference's page.
