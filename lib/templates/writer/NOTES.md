# writer — notes

Reference: https://writer.com/ (home page), measured 2026-11-12 at 1440×900 and 390×844. The two plan columns were
measured on https://writer.com/plans/ because the home page has no plans. Raw readings: `ref.json`, `probe/*.json`;
the scripts that took them: `probe/p1…p4.mjs`. Extra checks beyond `tools/shots.mjs`: `probe/check.mjs`
(contrast on every ground, focus ring on every tab stop, reduced motion, which media is distorted).

What was seen earlier, checked: the dark opening over an atmospheric picture with a centred sans headline, the
field-and-button row and the logo row are there. The "tilted glass cards over a coloured glow" is one flat picture
(1050×493, radius 16) in the "advantage" section, not live elements. The two soft-tinted columns and the comparison
table are on the plans page only. **The typeface is not commercial on the home page: it is Poppins (SIL OFL)**; only
the plans page's H1 uses a commercial serif (Canela Deck), which this template does not use.

## Sections of the reference → what feeds them here

| # | Reference (1440: top, height) | Build | Data here |
|---|---|---|---|
| 0 | Header, 83 high | lies on the page (absolute, transparent); past ~90px it is fixed on the ground colour | `brand`, `nav`, `signin`, `cta` |
| 1 | Opening, 0–555, pad 180/100 | centred column ≤700; picture 1321×258 at the top edge, soft lower edge; field+button pill 407×54 | `hero.title/text/text2`; `media.made.sky` as the picture; two 54px pills: `hero.primary` (accent) and `hero.secondary` (outlined) |
| 2 | Logo row, 555–681 | 16px line, then a 100px-high running row, faded at both ends | `hero.note` as the line; `logos[]` if any, else `trust[]` set as words |
| 3 | "Marketing", 681–1581, lighter band | left title block (eyebrow, h2, 20px text), one panel a view 1050×427 r32, 3 dots | `steps` (+ `hero.kicker` as the eyebrow) |
| 4 | "Customers", 1581–2313 | row of 488×332 r12 cards from x=56 running off the right edge, two 40px round buttons | `figures[]`, then `quotes[]` if any |
| 5 | "Team workflow", 2313–3770 | centred title, picture 954 wide, 2×2 cards 345 wide, gap 16, r16, pad 50/32, centred | `features` + film and the screens not used in 6, shown whole |
| 6 | "Advantage", 3770–4769 | left title, text, accent button, one picture 1050 wide r16 | `statement`, `cta`, `media.screens[0]` whole |
| 7 | "Governance", 4769–5651, lighter band | centred title, 3 left-set cards (h3 + paragraphs), gap 8, r16, pad 32 | `faq` (question = h3, answer = paragraph) |
| 7b | plans page: two columns 460 wide, gap 24, r16, pad 28/40/52 | name 24/600 tracked 3px caps, line 16/24, pill 266×44, ticked list 14/20 | `plans` (placed before 7, on the same lighter band) |
| 8 | "Transform", 5651–6546 | second slider, text left / picture right | not built — see "Not transferred" |
| 9 | "Resources", 6546–7531 | two columns, gap 28, a 1px rule between them that draws itself | `links[]` |
| 10 | Closing band, 7531–7928 | 44/55 centred, two 60px pills | `close`, `hero.secondary` |
| 11 | Foot, 7928–8742 | mark + link lists, ruled middle row, tracked legal row | `brand`, `nav`, `signin`, `cta`, `links`, `foot` |

Every section is left out whole when its data is missing (automateed has no faq → section 7 is absent; no video → the
features show starts with a screen). No field anywhere; the reference's two e-mail fields (opening, foot) are replaced
by the primary button and by `foot.text`. The opening used to keep the field's shape (a grey half holding the secondary
link beside the accent half) — it read as an input that does nothing, so it is now two separate pills, 12 apart, the
second one outlined like the reference's own outline buttons; on a phone they stack, 10 apart.

## Measures used (1440 / 390)

- Column 1080 with 15 side padding (content 1050). Bands: pad 90 / 50. Ground, lighter band (+3.5% ink), card (+10.5%),
  panel and closing band (+9.5%), panel border (+15.5%), idle dot (+29%). Text greys 90% / 80% / 63% of ink.
- h1 64/1.0/−0.02em/500 → 40/1.0/−0.015em. h2 40/1.15/−0.02em/500 → 36. Panel h3 32/1.15/−0.02em → 26. Card h3 24/1.25.
  Body 16/1.6. Section lead 20/1.6 → 16. Eyebrow 16/600, tracking 3px, caps → 14, 1.6px. Nav 14/600. Link-list
  title 24/1.2 with 12/16 text. Closing title 44/55. Legal 14/600 tracking 4.2px caps → 11.4.
- Buttons: header pill 45 high r82 (2px border); opening pill 54 high r50; section buttons 46–48 high r60, pad 10/24;
  plan pill 44 high r82, min 266; closing pills 60 high r60, pad 20/24, gap 12.
- Title block: eyebrow → h2 16, h2 → text 16; title → slider 60; slider → dots 20; dots 14px, 17 apart.
- Phone: header 76; opening pad 100/50, pill halves stack (219+ wide, gap 10); panel becomes a column (picture, then
  text pad 30/25); figure cards 360×240, gap 16, from x=20; cards one column (pad 32/24 and 24); foot lists two a row.
  Menu: full panel under the header in the inverse colours, slides in from the right in .3s, rows 51 high, 14/600.

## Font

Poppins 400/500/600 from Google Fonts (SIL Open Font License) — the reference's own face, open, so used as is.

## Motion — measured, and what is reproduced

| What | Measured on the reference | Here (read back with `probe/pairs.mjs`) |
|---|---|---|
| Load | nothing animates in; h1 at full opacity from the first frame | nothing animates in |
| Header | absolute at top; becomes fixed between 40 and 100px of scroll with keyframes `top:-100% → 0`, .4s ease; stays on scroll-up | fixed past 90px, same keyframes, .4s ease |
| Logo row | continuous, linear, 60.0 px/s leftwards, pauses under the pointer | 59.9 px/s, pauses under the pointer |
| Panel sliders | 600ms ease, next every 8000ms, loops, draggable, does not pause on hover | 600ms ease, advances at 8.05s, draggable; at the end it runs back to the first instead of looping seamlessly |
| Figure row | 600ms ease, no autoplay, no loop; prev/next 40px, idle opacity .5, disabled .35, hover fills white in .2s | same |
| Buttons | fill darkens ~16% in .2s; outline button fills on hover; nothing moves | same |
| Closing pills | .3s ease-in-out; the light one goes grey with light text | same |
| Link hover | colour shifts to a pale accent tint in .3s; foot links grey → white in .2s | same |
| Column rule | draws top to bottom: bright line `scaleY 0→1` to 84% of 1.4s, a grey one follows from 50% to 100% of 1.8s | same, started once when seen |
| Scroll | no reveals, no parallax, nothing pinned except the header | none |
| Picture scale | one picture in "Resources" scales 1 → 1.06 → 1 as it crosses the screen | not reproduced (no picture there; a screen must not be cropped) |
| Floating promo card | slides up 24px with scale .96→1 in .35s, cubic-bezier(.22,1,.36,1) | not built (their promotion, no data) |

Reduced motion: no animation or transition runs, sliders do not advance, the film does not play and shows its
controls, the running row becomes a wrapped still line.

## Departures made for the owner's standing rules

- **Panel (3):** the reference puts a 620-wide picture in the left of the card (its opening star field again, with a
  collage on it) beside a plain dark text half. Here the same build: the picture side (59.1% of the card, behind the
  screen) carries `made.sky` again, dim, and dissolves toward the text half; the text half is the plain panel ground.
  The product screen stands on the picture side whole, at its own ratio, uncropped. A portrait screen makes the card
  taller — 524 instead of 427 — rather than being cropped. This is still a screen next to text inside one card; if that
  reads as "boxed beside text" to the owner, the alternative is the phone layout (screen above, text under) at every width.
- **Features (5):** the reference lays its four cards over the lower half of a 954×950 picture (an astronaut on the
  opening's star field). A product screen may not be covered, so the film/screens stand whole above the cards, one at a
  time on the reference's slider, and the picture slot behind them takes `made.sky` (see Image slots, 4).
- **Statement (6):** the screen is shown whole at its own ratio (the reference's picture is 1050×493; a 16:10 screen is
  656 high here).

## Not transferred, and why

- "Transform" slider (8): it is the same panel as (3) mirrored, with three paragraphs and a button per slide. No
  second block in the data has that shape; feeding it would mean pairing unrelated text and screens.
- Section eyebrows and their small icons, the icons at the top of every card, the foot's column headings and social
  buttons: no data for them, and icons are not taken. Only the steps section keeps an eyebrow (`hero.kicker`).
- The features and statement buttons in the reference are "Learn more →"; features has no link in the data, so no
  button there; the statement uses the site `cta`.
- Thumbnails in the link list and the big picture at its left: no pictures of that kind; the list is text only, split
  in two columns around the rule.
- Portraits, names and company marks on the figure cards: none in the data.
- Seamless loop on the sliders (see motion table).
- Unused client media: sportbot's fourth phone screen and the performance screen that is not in `media.screens`;
  automateed's four book pages not referenced by a step.
- Plans: the reference has no price on its columns; price and period are set in the h2 measure between the line and
  the button. The comparison table of the plans page is not built (no data).

## Image slots (motif: `sky`)

**Motif: `sky`** (CONTRACT, "One picture family per page"). The reference repeats one picture family down its page:
the opening nebula, the same star field in the step card, behind its customer cards and behind the team section. So
every picture slot here is `made.sky` in another crop, or `made.field` — the quiet out-of-focus ground in the page's
own tone — where a ground has to carry text. No `blur` hue, no `land`, no `sheet` anywhere (2026-11-12: the vivid green
`blur` panel behind the phone was what the owner rejected). `GLOW` and every radial-gradient stand-in are gone (the
radial gradients left are masks). With `media.made = {}` every slot below is the plain palette ground and no made
file is referenced.

1. **Opening sky** ← `made.sky` (`data-slot="sky"`, eager, 1321×258 at 1440, `object-fit:cover` from the top). Masked,
   not veiled: a half-ellipse removes the sides and lower edge, intersected with a vertical ramp that holds the picture
   at 24% under the header's words (0–62px; it was 42%, which measured 3.26:1 under sportbot's first nav link) and
   lets it come up to full by 140px. On a phone the strip is 124px (32vw) high instead of the reference's 76.
2. **Step panel, picture side** ← `made.sky` again (`data-slot="panel-sky"`, lazy). Size and place as the reference's
   620×426: the left 59.1% of the card, full height (620×524 with a portrait screen); on a phone the top of the card
   behind the screen. The picture is set at 150% of that box and moved per card (`CROPS`: left/top −25/−50, 0/−22,
   −50/−22 %) so each card shows another, lower and quieter part; opacity .62 over the panel ground; the last 28% toward
   the text dissolves (mask). The text half is the plain panel with the page ink — no text on a picture. A dark page
   never takes a light sky here (`_fit_page`); a panel without a screen has no picture.
3. **Figure cards** ← `made.field[0]` in the page's tone (`data-slot="figure-field"`, lazy): one field runs behind the
   whole row — each 488×332 card shows the next slice (picture at 250% of the card, shifted by card index). The
   reference's cards are photographs of customers on its nebula; there are no portraits in the data and people are never
   generated, so the slot takes the quiet ground. sportbot: field-green; automateed: field-cream. A field whose tone is
   not the page's is not used (automateed's navy).
4. **Features backdrop** ← `made.sky` (`data-slot="features-sky"`, lazy), 954 wide and up to 950 high as measured,
   behind the film/screen and the upper cards, edges masked away (no box). When the first screen is as wide as the
   picture (ratio ≥ 1.4, automateed) the picture starts under the caption and dots instead of above the screen, so it is
   seen round the cards and no text lies on it. Phone: up to 420 high.
5. **Links section** — plain, no picture. The reference has a 543×311 article picture and thumbnails there; no picture
   of that kind exists. A field laid behind the columns with its edges masked was tried and taken out: on sportbot it
   read as a green glow behind the text, which is what the contract forbids.
6. **Statement picture** — the client's own first screen, whole (the reference: one 1050×493 made picture).
7. **Features picture** — the client's own film/screens, whole.

### Picture share (per 900px screen)

`tools/coverage.mjs` counts an `<img>`'s whole box even where an `overflow:hidden` parent cuts it; slots 2 and 3 are
oversized crops, so its numbers for ours are too high on those screens. "visible" is the same tool with each box cut to
its clipping ancestors (own copy, scratchpad).

| | 1440 | 390 |
|---|---|---|
| reference (tool = visible) | 25% [27,27,47,62,27,15,14,21,0,0] | 23% [0,44,28,40,8,13,0,27,30,63,25,0,0] |
| sportbot before (tool) | 18% [27,53,8,28,0,48,8,0,0,0] | — not taken |
| sportbot now, tool | 27% [36,64,52,56,0,48,8,0,0,0] | 16% [27,58,49,25,0,25,0,0,0,0,0,0] |
| sportbot now, visible | 23% [27,30,52,56,0,48,8,0,0,0] | 14% [16,44,47,25,0,25,0,0,0,0,0,0] |
| automateed now, tool | 37% [35,62,46,62,33,48,0,0] | 27% [27,56,40,55,23,0,0,0] |
| automateed now, visible | 31% [27,27,46,62,33,48,0,0] | 24% [16,44,39,55,23,0,0,0] |

(The brief's first reading of the reference was [27,28,47,62,27,20,14,21,0,0]; the live page differed slightly on the
day.) What still differs: the reference's "Transform" slider picture (screen 7) and resource pictures (screen 8) are not built;
sportbot's page is longer (seven feature cards, plans and questions), so its statement screen falls on screen 6 and
screen 5 is cards only; at 390 the reference's opening strip is under the tool's 120px floor and counts 0.

### Contrast, measured from rendered pixels (text hidden, lowest of ink against lightest/darkest pixel in the text's box)

| | sportbot 1440 / 390 | automateed 1440 / 390 |
|---|---|---|
| opening: h1, paragraphs, nav links, name | 4.91 (first nav link) / 9.94 | 8.03 / 12.62 |
| step panel text (on the plain half) | 6.07 / 6.07 (label) | 4.83 / 4.69 (label) |
| figure cards, value and label on the field | 9.83 / 11.55 | 7.91 / 8.60 |
| caption under the film/screen | 7.08 / 7.23 (on the sky's dark lower part) | 5.81 / 5.81 (plain ground) |

Only the first slide of each slider was measured (the others are off-screen until they come round; they use the same
build, the panel text half being plain in all). `probe/check.mjs` was not re-run.

Not used by this template: `made.blur`, `made.land`, `made.sheet`.

Seen and not fixed: screens in the features slider load lazily with `width:auto`, and the page below them moves by
about 500px when they arrive (found while measuring; it was there before this change).


## Fixes for the engine's gate (2026-11-12)

Header and foot marks keep their own proportion (limits, not square boxes). On a phone the step screen's shadow scales with the screen (0 11px 30px) so it ends before the label under it. Without a hero title the brand name is the h1. needs.json written 2026-11-12.
