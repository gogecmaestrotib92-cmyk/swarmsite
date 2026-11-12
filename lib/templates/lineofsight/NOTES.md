# lineofsight — the build of lineofsight.co with a client's data

Reference: https://lineofsight.co (vision-care practice), measured 2026-11-12 at 1440 and 390 (`ref/anatomy.json`,
`ref/ref-*.jpg`), plus its `/services` and `/team` pages for the parts the home page does not have
(`ref/services-d-full.jpg`, `ref/team-d-full.jpg`). Niche: clinic; also service / studio with a door.
Test clients: clinic1 (German dental practice, primary), local1 (joinery workshop).

## What the reference is (measured)
One monospaced face in capitals on a two-tone page (cream rgb(255,251,235), near-black rgb(12,12,12)); colour comes only
from the photographs. Thin 1px rules and 5px "thick" marker bars stand left of every heading; a ruler of ticks closes the
first screen and the page. No accent colour anywhere — so the client's `palette.accent` is **not used** (ground and ink only).

| # | reference section (y at 1440) | what it is | our data |
|---|---|---|---|
| 0 | header, fixed | wordmark left (24,24); nav list 300 wide, 44px rows, right; collapses to a "Menu" bar after the first scroll, opens on hover/click | `brand.name`; `nav` + `signin` + `cta` (the reference's last nav row is its booking link) |
| 1 | hero 0–2700 (300vh, sticky 100vh) | full-bleed photograph, h1 at 50vh (25.2px/1.28, 600), 1px line from the h1 down to a ruler 24px from the bottom | `hero.title`; first photograph (see slots) |
| 2 | opening sentence 1824 | 25.2px/1.4, 880 wide, bold lead-in, thick bar | `hero.kicker` (bold) + `hero.text`; `hero.text2` under it at 13px |
| 3 | intro 2183 | one heading at column 2 with a 1px rule, 144px below it | `steps.title` (+ `steps.text` at 13px, 416 wide — the reference has no paragraph here) |
| 4 | three cards 2362–4678 | 3 columns of 416 with 48 gaps; card i stands in column 2, 1, 3 and one row lower each (788 pitch); roman numeral, 20.7px title, picture 416×521, 13px text, full-width button 44 high; rules between the columns | `steps.items[]` (title or k, img, text, cta) — cycles 2,1,3 for more than three |
| 5 | band 4774, 100vh | full-bleed photograph under a veil, three staggered columns (332/534/433 high, 300 wide, title top, text bottom), hover makes one active; full-width button | `statement` (title, text) — plus the first two `features` with a description only when the client has no `catalogue`; button = `cta` |
| 6 | film 5722 | 1344×760 picture in a 1px border, play mark | `media.video` (native controls), else one wide photograph in its own proportion (1.5–2.9:1) |
| 7 | ruled grid 6754 | 3 columns of 464×155 cells, top and right rule, press logos | `figures`, `trust`, `logos`, `credentials` — one grid each, as words (logos as files only when the data gives a file) |
| 8 | quotes 7362 | cards 856×414 on ink, 96 padding, centred 20.7px, arrows 72×46 | `quotes[]` |
| 9 | closing 8027 | 20.7px sentence at x=348 with the phone bold and underlined, 1px rule, then the ruler | `close.title`, phone (`place.phone` / `contact.phone`), `close.text` (13px), `close.cta`, `contact.form` |
| 10 | foot 8333, ink | dl: Addr. / Tele. / E. / IG. (label 184, value at 273, 20.7px; small lines 13px muted); nav list and legal list in column 3; large wordmark; small print | `place.address`, `locations[]`, `place.hours`, phone note, phone, email, `place.social`, `contact.routes`; `nav`; `foot.links`; `brand.name`; `foot.text` + `foot.legal` |
| — | /services: list that opens | right half 696 wide: group title with bar, rows 20.7px with a triangle, pad 12/12/48/24; open row = ink ground, 13px muted text | `catalogue` (groups, name, text, price, prices[], rows[], note, state, h) — or `features` when there is no catalogue; `faq` in the same part |
| — | /team: row of people | cards 348 wide (300 picture), name 20.7px bold, role 11px, rules between, arrows | `team.items` / `team.groups[].items` (own portraits only; no portrait → type only); `projects[]` in the same row with 464-wide cards |
| — | plans | (the reference has none) built from its ruled three columns: bar + name, price at 25.2px, line, rows, its button; the marked plan on ink | `plans` |

Order on our page: 1 2 3 4 5 6 7 · list · plans · people · projects · questions · credentials · quotes · closing · foot.

## Measures used
Margin 40 (21 on the phone); bars at −24 (−14); page rule at x=24 (14). Type: heading clamp(18px, 1.751vw, 28px),
large clamp(13px, 1.4384vw, 23px), body 13px (.8125rem), small 11px; root 16px, 14px under 700 (so body 11.4px on the
phone, as measured). Line height 1.4 (h1 1.28). Radii 0 everywhere. Buttons 44 high, pad 12/24, 1px border, ink fill,
10px triangle; hover swaps fill and ink at once (no transition measured on colour). Ruler: ticks every 39px (38.67
measured), every third 32 high, the others 16; 30px on the phone.

## Font stand-in
NB Akademie Pro Mono (commercial) → **Geist Mono** (SIL OFL, Google Fonts), 400/600/700. Akademie's advance is .744em
(measured: 15 capitals of 13px = 145px); Geist Mono's is .6em, so `letter-spacing:.144em` restores the measured line
lengths. Everything is `text-transform:uppercase` as in the reference.

## Motion — measured and reproduced
| measured on the reference | ours |
|---|---|
| hero wrapper 300vh, inner sticky 100vh; page starts at 200vh (margin −100vh) and slides over the held picture | same (only with scripts and without reduced motion; otherwise one 100vh screen) |
| 0→100vh: picture blur 15px→0 and scale 1.1→1, both 1−(1−t)³ (blur 4.44px at t=⅓, .556 at ⅔) | same formula; our readings at 300/600/900: 4.44 / .56 / 0 |
| 0→100vh: ruler slides left 348px (24.2 % of the width), same curve | same |
| 100→200vh: picture moves up 225px (25vh) linearly, ink overlay 0→1, the h1's rule retracts | same (the rule scales to 0 from its top instead of moving out) |
| card pictures: blur 10px→0, scale 1.1→1, linear from entering the screen to its middle | same |
| header: nav rows fold up behind "Menu" (transform .5s cubic-bezier(.215,.61,.355,1)) after the first scroll; hover or press opens | same; Escape and leaving close it |
| thick bars grow in .75s; buttons are uncovered left to right, clip-path .75s cubic-bezier(.38,.005,.215,1) | same, by IntersectionObserver |
| band: hovered column becomes active, others at opacity .25, .5s | active column full; the others' rules and bars at .3, their **text at .82** (text at .25 is unreadable on a photograph — the owner's readability rule wins) |
| quotes / team: transform slider, about 1.2s ease-out, arrows; previous at .25 when at the start | native scroll-snap row moved by the arrows (smooth scroll), previous disabled at .25 |
| bottom ruler moves left .249px per px of scroll once on screen | same |
Not reproduced: the loader (black screen with 38 lines), the page-transition fade, the film modal (our film plays in place
with native controls).

## Where ours departs, and why
- **Header chips.** The reference's wordmark and "Menu" are bare type that takes the colour of what is under it and
  runs over the page's text. Ours stand on an ink chip (the same fill as the reference's open nav rows) so they read
  over a bright photograph and over text — the readability gate judges a fixed header on every screen.
- **First screen veil.** The reference's picture is dark; a clinic's rooms are white. The picture gets the reference's
  20 % ink veil plus a scrim of ink at 66 % under the h1 (left half at 1440, lower part at 390), falling to nothing —
  enough for 4.5:1 on a pure white pixel. The band's veil is 80 % for the same reason (reference 25 %).
- **Boxed picture converted.** /services shows a 416×450 picture floating in the left half beside the list. Ours is an
  edge-to-edge half: from the page's left edge to the middle, as tall as the list, held while the list scrolls
  (a full-bleed band above the list on the phone). The section heading moves to the top of the right column.
  The /team "highlight" rows (portrait in a column beside a biography) are not used; every person stands in the team row.
- **Card pictures** are pictures above their text in a ruled column (not beside text) — kept as measured.
- The opening sentence starts 96px below the page's top edge (reference 24px) so the header does not cover its first line.
- The faint numerals (I. II. III.) are ink at 74 % instead of the reference's near-invisible grey.
- No section labels are invented: the grid has no "As seen in:" heading, the team row has a heading only when
  `team.title` exists. The only words the template supplies are Adr./Tel./E. (Addr. in English), FB./IG. for social rows,
  "Menü/Menu" and the arrows' aria-labels.
- Wordmark is the brand name set in the face (the reference's is a wordmark too); `brand.logo` is not drawn.

## Image slots (client's own photographs; `media.made` is never read)
Each photograph is used once; `small` pictures and portraits never fill a slot; a slot without a fitting picture is left out.
| slot | size at 1440 | takes | clinic1 | local1 |
|---|---|---|---|---|
| hero (cover, 100vh) | 1440×900 | ≥1108×690 (enlarged at most 1.3×), role room → exterior → work → landscape → workshop | wartebereich 2000×690 | staircase-curved 2400×1606 |
| step cards | 416×521 each | `steps.items[].img` | 3 | 3 |
| band backdrop | 1440×900 | ≥1108×690, role detail → workshop → room | blumen | staircase-down |
| wide | 1359 × own ratio (1.5–2.9:1) | ≥1040 wide, role exterior → work → room | eingang 2.9:1 | kitchen-painted 2:1 |
| list half | 672×900 held | ≥600×690, role detail → room → work | leuchter | kitchen-blue |
| people | 300 × own ratio (2:3–1:1) | each person's own `img` | 10 (400px squares shown at 300) | 3 |
| projects | 416 × own ratio (4:5–3:2) | first photo of each project not used elsewhere | — | 5 |
clinic1's banners are 690px high, so the three 900-high slots enlarge them 1.3× (soft on a large screen; stated in needs.json).
Without any photograph: hero is an ink screen with the h1 and ruler (no pin), the band is an ink band, the wide picture
and list half are absent, cards and people are type.

## Picture share (tools/coverage.mjs)
reference 33 % — per screen [100,0,10,21,22,72,92,21,0,0,0], 3 wide · clinic1 31 % [100,0,0,18,19,18,98,57,34,15,32,0,0], 3 wide ·
local1 31 % [100,0,0,19,18,18,76,92,19,36,24,31,0,0], 3 wide. Our pages are 1.24× and 1.36× the reference's height, so the
overall share is the one compared (case 2 of the rule, under 1.5×). The reference's three wide pictures (hero, band,
film) are all present in the same order.

## What could not be transferred
- The art-directed, colour-graded photography (blue eye, red face) — the page's colour. A client's daylight room
  photographs under an ink veil read grey-toned, not saturated. This is the largest visible difference.
- The loader, page transitions, film modal, the wordmark's strike-through glyph, the small logo mark at the page's top right.
- Hover-only dimming at .25.

## Checks (final render)
shots.mjs, both widths, no sideways scroll, no distortion, one h1, errors []:
clinic1 d 11414 / m 10017 · local1 d 12527 / m 10754. legible.mjs: clinic1 ok (413 readings), local1 ok (478).
Focus: 2px ring in currentColor (inset 5px on filled controls so it shows on the chip). Reduced motion: no hold, no blur,
bars and buttons shown at once (hero 900 high, filter none, measured). Without scripts: header is not fixed, nav shown
open, every bar/button visible, hero one screen (looked at, full page).

## Variants (scratch copies of the data, `out/var-*.html`)
All: no sideways scroll, errors [], one h1 at 1440 and 390. legible ok unless stated.
1 / 3 / 5 plans + sportbot's faq (ok, ok, ok — plans1 see below) · 2 and 9 features without a catalogue (ok, ok) ·
1 and 6 steps (ok, ok) · 12-word h1 (ok; wraps to 3 lines at 1440, 4 at 390) · 40-character button label (ok; wraps
inside the 300 nav row and the 44 button) · no photographs, clinic1 (ok) and local1 (see below) · first five large
photographs only (ok) · local1 with test credentials, a second location, figures and catalogue prices (ok).
Two variants print one FAIL each (nopic-local1 "Working closely…", plans1 "What sports does…"), both at 1440. Looked at
the crops: in both the line stands just below the fixed header chip at that one scroll step, and the chip's lower edge
cuts the top of the letters. The line's middle and both ends are free, so the gate judges it there. At the next step
the line is clear. I read this as the gate's "sliding under a header" exemption missing a partial overlap from above.
It is not a ground or contrast fault, so the page was not changed for it. Reported for the tool.
