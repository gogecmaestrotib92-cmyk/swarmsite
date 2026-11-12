# dock — notes

Reference: https://dock.cool (redirects to https://cooldock.app/), read 2026-11-12 at 1440×900 and 390×844.
Everything measured is in `ref/` (`anatomy.json`, `dump.json` = every text box, box, picture; `motion.json` = positions
sampled over the scroll; `css-d.txt` = the rules read for transitions; `sec/` = one shot per section). Probe scripts are
in `probe/` (run with `tools/run.sh node dock/probe/<name>.mjs`).

**The site changed while it was being measured.** 09:22 it served the page (15 300 px). 09:23–09:24 it answered 503 with
a "website upgrade in progress" page. From 09:24 it served the page again with a 900 px **Black Friday** screen in front
of the opening and every button turned into a lime "BUY 50% OFF" button (16 200 px). `ref/ref-d-*.jpg` are from before
the campaign, `ref/sec/*`, `dump.json` and `motion.json` from after (their y values are 900 px lower). The campaign
screen is a dated promotion, not part of the build, and is left out; everything else was identical in both states.
No cookie wall was met.

## Sections of the reference, and the data each takes

| # | Reference (measured at 1440) | Ours | Data |
|---|---|---|---|
| 0 | Header: a pill 610×53, fixed 20 px from the top, r18, white 80 % + blur 10, pad 10; app icon 30 r8 + name 16/600; links 14/500 at 60 % ink, gap 20; small button r8, 12/700, pad 8 16 | same; the pill grows with the number of links | `brand`, `nav` + `signin` as the last link, `cta` |
| 1 | Opening, 1326 high, all centred in a 680 column from y142: line 20/600 whose letters come in one by one, then "by …" at 400; h1 80/80 −4 px 700; grey 20/28; one button 52 high r20 pad 15 30 16/600; a row of 12 px grey facts gap 20. Behind: a landscape film 800 high from y150, fading into the page over 454 px at the top and 350 at the bottom. At y592 a glass "desktop" 948×533 r30 (white 20 %, blur 10, white hairline) with a notch, a menu bar and the product's dock bar; two cut-out rocks 500×726 at the sides | same column and sizes; the landscape is a made picture; **the glass frame holds the product's first screen, whole** (pad 10, inner r20); no notch, menu bar or rocks | `hero.kicker` (letters) + `hero.note` ("by …" place) · `hero.title` · `hero.text` + `text2` · `hero.primary` · `trust[0:4]` · `media.made.land` · `media.screens[0]` |
| – | Four award badges 90 px in a row | left out | (none) |
| 2 | h2 60/60 −3 px in 700; 20/28 text; two rows of chips (12/500, r30, pad 5 10, surface colour, gap 10); 60 below, a film 1120×730 r30 with controls | same | `features.title/text` · chips = `features.items[].t` · `media.video`, else the next unused screen |
| – | One centred quote 16/22.4 in 500 with face and name | built, left out without quotes | `quotes[0]` |
| 3 | h2 + text in 600; two columns of cards 550×488, gap 20, r30, pad 40, surface colour: h3 30/30 −1.5, 16/22.4 text, "Includes: …", then rows of small product pieces 62 high, r13 | same cards; text, an underlined 16/600 link, then the step's picture whole (r13), 220 wide when upright. With an odd number the last card spans both columns and carries a row of the client's other upright pictures, as the reference's cards carry rows | `steps.title/text/items[title,text,cta,img]` (+ unused `phones`/`photos` in the last card) |
| 4 | Small badge link; h2 + text in 700; 60 below, a film 1120×730 r30 of the product on a landscape wallpaper | h2 + text; a made landscape 1120×730 r30 with the next unused screen standing on it, whole | `statement.title/text` · `media.made.land[1]` · next unused `screens` |
| – | "Loved by…" wall: two columns of quote cards 550 wide r30 pad 40 | built, left out with fewer than two quotes | `quotes` |
| 5 | Black section 3886 high. A wall of ~75 product tiles (124 high, gap 20) is pinned for 2740 px: it comes from 2× and transparent to 1× and opaque, then shrinks to 0.1× and fades into the app icon (120 px), under which stand h2 60 white, 20/28 at 60 % white and the button | same mechanism; the wall is the client's pictures **once each**, sized so the wall fills the frame; section in the ink colour | `close.title/text/cta` · `brand.logo` · all of `media.screens/phones/photos` |
| 6 | Strip 700 high (pad 200 / 100): three screenshots 400 high, r20, gap 20, running left, 40 s for 2001 px | same; pictures not yet shown large (topped up to three with screens) at their own proportion | `media.*` |
| 7 | h2 "Pricing" + grey 20; three cards 387 wide gap 20, r32, pad 32 28 28, hairline white border, soft shadow; the middle one 80 taller, lifted 40, white, with a lime pill on its top edge; name 25/30 650; price 60/60 −3.3; 12 grey note; rows 14/21 with a 20 px ring-tick; full-width button 52 r20 (black; lime on the lifted card); behind the cards a band that darkens to 76 % of its height and returns; two rocks; 14/22.4 grey note 750 wide | same; as many cards as there are plans; the `marked` plan is the lifted one; no pill (no words for it), no device switch, no rocks | `plans.title/text/items[name,price,per,line,rows,cta,marked]/note` |
| 8 | h2 + grey 20; two columns 490 wide gap 20 of rows r20 on the surface colour, plus sign 16 px at the left, question 14/22.4, answer 16/25.6 at 60 % | same | `faq.title/items[q,a]` |
| 9 | A strip of "featured on" badges 48 high, then the dock bar alone: 869×100, r30, black 90 %, pad 10, cells r20 80 high with a 30/600 figure and a 12 px line at 60 % | badges only with `logos`; **the dock bar carries the figures** (figure 30/600, label 12) | `logos` · `figures[v,l]` (first four) |
| 10 | Foot, pad 100: brand column 274 (icon + name, 20/700 line, 14/19.6 text, small button, 12 px legal) and five link columns 137 wide gap 32 with 16/700 headings; below, a landscape film with the name set 320 px/600 across 1200 px in the page colour | same; link columns without headings (the data has none); the name is fitted to the width by letter-spacing, never stretched | `brand` · `hero.kicker` · `foot.text` (else `hero.text`) · `cta` · `foot.legal` · `nav`, `links`, `foot.links` + `signin` · `media.made.land` |

Not placed anywhere: `hero.secondary` (the reference's opening has one button), `steps.items[].k`, `features.items[].d`,
`links[].d`. Nothing was invented to fill a slot.

## Measures used (1440 → 390)
Column 1120 inside 40 px margins → 350 inside 20. h1 80/80 −4 → 51/51 −2.55 (68 and 56 for titles over 44 and 64
letters, the same tracking of −0.05 em). h2 60/60 −3 → 38/38 −1.9. Lead 20/28 −0.2 → 16/22.4. Card h3 30/30 −1.5 →
19/19 −0.95; card text 16/22.4 → 14/19.6. Chips, facts and legal 12/19.2. Radii: 30 cards and media, 32 plans, 20
buttons, FAQ rows and strip pictures, 18 header, 13 pictures inside cards, 8 small buttons. Card padding 40 → 30.
Gaps: 20 between cards, 10 between chips, 60 from a section head to its content, 100 between sections (200 after the
cards). Plans stack at 390 with 32 between them, pad 32 24 28. FAQ becomes one column. Foot columns stack.

## Font stand-in
The reference sets **Inter Display / Inter** — Inter is SIL OFL and on Google Fonts, so it is the same family, loaded
with its optical-size axis (`opsz 14..32, wght 400..700`); the display cut comes from the axis at large sizes. No
stand-in was needed. The 650 weight of the plan names is taken from the variable axis.

## Colour
Client palette in, relations kept: quiet ground; cards one step lighter than the ground (light pages: 60 % toward
white; dark pages: 6 % toward the ink); the lifted plan and the header one step further; grey text derived from the
ink and held at ≥ 5.3:1 on every ground it stands on; buttons in the accent with the reference's soft drop of the same
colour (0 10 28 at 35 %), the plain plan's button in the ink. The reference's black section and black dock bar are
"the ink on the page" on the light client (navy). On the dark client the straight inversion made the pinned wall a
near-white stretch about four screens long in a dark site and a white dock bar; since the pass of 2026-11-12 both are a
raised dark ground there (ink 8 % on the ground, text in the page's ink), so the dark page stays dark. Kept from the
reference's rhythm: the wall section still changes ground against the page and is the page's longest single stretch;
given up on the dark client: the strong inversion.

## Motion — measured, and what is reproduced
| Reference (measured) | Ours |
|---|---|
| Header drops in from −53 px with a fade, 1 s, spring `linear()` curve, after 1.5 s | same curve, time and delay |
| Opening: letters of the first line blur(10)→0, +10 px, 1 s each, 0.05 s apart from 1.5 s; h1 rises 30 px in 1 s at 0.3 s; text at 1 s; button and facts at 1.5 s; glass frame at 1 s; landscape scales 1.04→1 in 1 s `cubic-bezier(.16,1,.3,1)` | same |
| Cards (and quote cards) rise 30 px and fade in, 0.76 s `cubic-bezier(.16,1,.3,1)`, when they enter | same, also on plan cards (a scroll check instead of an observer, so nothing passed in a jump stays hidden) |
| Wall: frame `position: sticky; top: 0`, travel 2740 px (≈3 viewports). From the moment the section's top reaches the bottom edge to 79 % of the travel: scale 2→1, translateY 490→0, opacity 0→1, linear with scroll. Over the next 895 px (≈ one viewport, ending after the frame lets go): scale 1→0.1, opacity 1→0. Icon: scale 1.5→1, translateY 300→0, opacity 0→1 over the whole stretch, arriving at the frame's centre. At 390 the same, section 3561 | same fractions on a travel of 300 vh, frame 100 vh (at least 880 px); sampled with `probe/mine.mjs`: 2×/0 at entry, 1×/1 at 79 % of the 300 vh travel, 0.1×/0 at the end with the icon on the frame's centre |
| Strip runs left at 50 px/s (2001 px in 40.02 s), linear, endless | same speed; duration follows the strip's length |
| Buttons lift 2 px on hover in 0.18 s `cubic-bezier(.2,.7,.2,1)`, glow grows; pressed, corners go to 40 px. Nav links 60 %→80 % ink in 0.15 s | same |
| FAQ row opens over ≈450 ms (height read every 50 ms: 62→96→129→147→151→154); plus turns 45° at once | height animated 450 ms `cubic-bezier(.16,1,.3,1)`; plus turns at once |
| 390: menu is a `<details>`; the panel (352×447, r18) replaces the pill at once, links 24/400 54 px apart, button across the foot | same |
| Nothing is pinned or moves with the scroll apart from the wall (rocks, frame, dock, pictures all scroll with the page — sampled every 90 px) | same |
| `prefers-reduced-motion`: all durations 0, wall and reveals static | no animation, no pin: the wall is a plain collage above the closing text; the strip can be scrolled by hand |

Not reproduced: the films (opening, wallpaper, foot) are still pictures; the progress ring and device switch belong to
the reference's own product and have no data.

## What could not be transferred, and why
- **The cut-out rocks** (opening and plans): `media.made` has no cut-out objects; the slots are empty, not replaced.
- **The drawn dock, menu bar and notch** in the glass frame, and the 75 widget tiles: they are the reference's product.
  The frame holds the client's screen; the dock bar's cells hold the client's figures; the wall holds the client's
  pictures once each (8–10 tiles instead of 75, so the tiles are larger — 300 px high at most).
- **Award badges, "featured on" strip, quotes, plan pill, device switch, column headings in the foot**: no data.
- **Dock bar at 390**: the reference scales the whole bar to 40 % (figures 12 px high). Ours becomes a 2×2 grid so the
  figures stay readable.
- **Foot landscape** starts under the link columns instead of behind them (the reference lets 14 px links run over
  the picture; with a picture of unknown tone that fails 4.5:1).
- **Opening veil**: the reference lets the facts row stand on the almost bare film. Ours keeps at least 70 % of the
  ground over the picture down to the facts row and anchors the picture to the frame, so longer copy never slides
  onto it.
- **Owner's rule on boxed pictures**: no slot of the reference puts a picture in a box beside text, so nothing had to
  be re-laid for it; in cards the picture stands under the text as in the reference.

## Image slots
| Slot | Takes | sportbot | automateed |
|---|---|---|---|
| Opening landscape | `made.land`, first of [0, 5, 1] whose tone is the page's | ridge (dark) | rock coast (light) |
| Glass frame | first of `screens`, `phones`, `photos` | sim-screen | img1 |
| Film under the chips | `video`, else next screen | sim.mp4 | shot3 |
| Cards | each step's `img` (+ unused upright pictures in an odd last card) | 3 phones + 1 | 3 covers + 3 |
| Statement | `made.land` [1, 3, 4] + next unused screen | valley + record-screen | valley + shot2 |
| Wall | every screen, phone and photo once | 8 | 10 |
| Strip | pictures not yet shown large, topped up to 3 | picks, matches, sim-phone | 4 book pages/covers |
| Foot landscape | `made.land` [5, 2, 0] not yet used | rock | water |
| Rocks, award badges, quote faces | — | no picture | no picture |
**One picture family: `land`** — the reference shows landscapes only (opening film, wallpaper film, foot film), and so
does ours; `made.blur`, `made.sheet`, `made.sky` and `made.field` are not used. Nothing had to change for this rule.
The foot name over the landscape is set in the palette end that reads on that picture (light on a `tone: dark`
landscape, dark on a light one); before the pass it was always the page colour, which on sportbot was near-black on a
dark rock landscape. The strip's pictures are drawn as grounds from one custom property per picture (whole, at their
own proportion, `role="img"` with the picture's alt on the first run), so the endless repeats do not multiply files:
one-file copies went from 1.7 / 2.1 MB to 1.3 / 1.3 MB. Without `media.made` the
landscape slots render the plain ground (`data-slot` stays).

## Checks run
Pass of 2026-11-12: `tools/legible.mjs` ok for both clients (sportbot 0 of 453 line readings, automateed 0 of 260).
Picture share (`tools/coverage.mjs`, 1440): reference 34 % (4 screens with a wide picture, measured with its campaign
screen in front); ours sportbot 32 % (3), automateed 37 % (5). The pinned wall reads as zeros on both.
`tools/shots.mjs` on both outputs: no sideways scroll, 0 distorted, one h1, errors [] at 1440 and 390.
`probe/check.mjs` + `probe/contrast.py` (text hidden, page photographed, every text box compared with the pixels under
it): worst 5.46 / 5.33 (sportbot 1440 / 390), 5.36 / 5.33 (automateed). 60 Tab stops, each with a ring. Reduced
motion: 0 running animations, nothing hidden, wall not pinned. Script unable to animate: nothing hidden.
Not checked: Safari and Firefox; real touch scrolling of the pinned wall; widths between 390 and 1440 other than by
eye in the rules; the quote and logo sections (neither client has the data); a client without `media.made`, with no media, or with only a title (each renders without error and with one h1, but was not looked at).

## Engine stress fixes (2026-11-12)
- Logos keep their own proportion: the header/foot mark is 30 high at its own width (was forced 30×30); the closing app
  tile fits the logo inside 120×120 at its own proportion (was forced 120×120); a wordmark is never narrowed.
- The very large name in the foot on a plain ground (no made landscape) was the card colour, ~1.1:1. It is now ink let
  down toward the ground only as far as 3:1 (large type), so it stays quiet but reads.
- Header link grey: the pill is the raised colour at 80 % with a blur, so a fifth of whatever passes under it shows
  through; the grey is now chosen to hold 5.3:1 over the pill mixed with any page colour, white or black (was 4.4:1
  when the accent button passed under it).
- The kicker's screen-reader copy now sits over its own animated letters instead of across the middle of the line.
- The large name over the foot landscape took its ink from the picture's tone label; on automateed at 390 the cream
  name stood on a lightened part of the water (2.78:1). Its ink is now chosen by measured contrast over the picture's
  mean colour through the foot's lower fade; when neither end reaches 3:1, the end farthest from the ground is laid on
  a full-width veil of the ground made just strong enough (automateed: navy name, 40 % veil). sportbot unchanged.
