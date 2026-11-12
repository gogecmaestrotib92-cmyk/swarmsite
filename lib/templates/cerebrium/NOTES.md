# cerebrium — notes

Reference: https://www.cerebrium.ai (home), read 2026-11-12 at 1440×900 and 390×844. No cookie wall; a 1s loader covers
the page first. Measurements: `ref/anatomy.json`, `ref/ref-*.jpg`, and the probes in `probe/` (run with
`tools/run.sh node cerebrium/probe/<name>.mjs`): `dump.mjs` (every box, type and ground → `dump-1440.txt`,
`dump-390.txt`), `motion.mjs`, `detail.mjs` (reference motion), `audit.mjs`, `behave.mjs` (our pages), `pairs.mjs` +
`pairs.sh` (the pairs), `go.sh` (build + shots for both clients).

## Sections of the reference, and the data each takes

| # | Reference (measured) | Ours | Data |
|---|---|---|---|
| 0 | Header fixed, 82 high, pad 14/40: logo left (26px name); nav box starting at the page's centre line (x724), 54 high, r7, translucent dark + blur 17.5, mono 13 uppercase; light button + accent button, 54 high, gap 12. Phone: logo + a 42px "menu" button. It has no bar of its own: back on a light panel its white name is invisible (`ref/header-up.jpg`) | same at the top of the page; **once scrolled it carries its own ground** (owner, see "Header" below); phone menu is a `<details>` sheet | `brand`, `nav`, `signin`, `cta` |
| 1 | Opening, one viewport high over a fixed full-screen canvas: h1 86/300/1.0 (−0.025em) in columns 1–6, bottom at 818; at column 9 a 17/1.35 paragraph 325 wide and two 54px buttons, bottom-aligned to the h1. One word of the h1 in an accent gradient | same; the accent word is chosen mechanically (see Unsure) | `hero.title`, `hero.text`, `hero.text2`, `hero.primary`, `hero.secondary` · backdrop `media.made.land[0]` |
| 2 | Row of customer marks 52 high, 83 under the opening, moving with the scroll | the same row, moving the same way, set in type when the client has no marks | `logos` if present, else `trust[]` |
| 3 | Dot field 360 high: 72px cells, a 2px dot in each; a 34px accent square r7 where the pointer is | same (6 columns × 4 rows on the phone, as measured) | — |
| 4 | White panel r32, laid 60px over the dark above and below, pad 82. Two columns 670/670 gap 20: left a 26.5/1.35 line 480 wide, right a 72.6/300/1.05 heading with an accent phrase | same; a text longer than 110 characters is set at the reference's body size (18/1.5) instead of 26.5 | `statement.text` (left), `statement.title` (right) |
| 5 | Same panel: left column sticky at top 98 — mono label with a 6px dot, then a list of titles 43.9/300/1.15, the one whose card is in view dark, the others pale; right column, cards 82 apart: a visual box r15 (583/569/434 high), h3 26.5, paragraph 18/1.5 570 wide | same; visual box = made picture as the ground with the client's screen whole on it (see Owner's rules); a mono underlined link under the paragraph | `steps.title` (label), `steps.items[k,title,text,cta,img,shape]` · grounds `media.made.land[0]`, a different crop per card, veiled 52% |
| 6 | Dark section over the canvas: left mono label, h2 57.4/300/1.05 with an accent word, two buttons; right, at the centre line, four points 50 apart: icon + 26.5 title, 16/500/1.5 text at 75% white, 460 wide | same without label and icons; `features.text` added under the h2 in the points' text style; one button | `features.title`, `features.text`, `features.items[t,d]`, `cta` · backdrop `media.made.land[0]` again, enlarged 1.7× from its lower right |
| 7 | Dot field again, then centred h2 43.9, a segmented tab control, and a 2×2 grid of light cards 570×167 r10 pad 16: 135px icon tile, 21.3 title, 17 grey text, mono underlined "try now", arrow | dot field and the 2×2 cards with title, text and arrow; no heading, tabs, tile or label (no data for them) | `links[t,d,h]` |
| 8 | Second light panel (slate), r32, pad 82: 72.6 heading with accent phrase; 129 below, two 54px arrow buttons; a carousel of cards 443×596 r10 on a darker slate: mono tags, a customer mark, 26.5 title, 15px grey "read" line + arrow | heading, the text under it at 26.5, then the cards as plan cards: mono line (`per`), price at 72.6 where the mark stood, name at 26.5, line at 18 grey, rows at 15 on hairlines, button. Two plans take the page's two 670 columns; three take the reference's three | `plans.title`, `plans.text`, `plans.items[...]`, `plans.note` |
| 9 | Mono label left; from x500 two columns of link rows 442 wide: 26.5 text, arrow, 76 high, hairline under each | same rows; each opens its answer (the arrow turns down) | `faq.title` (label), `faq.items[q,a]` |
| 10 | "Latest…" h3 36 + small button, then three cards 440×565 r10: picture 440×372 with a white icon centred, white body pad 20/20/28 with mono date + tags and a 26.5 title. Phone: the cards scroll sideways, 298 wide | cards with a crop of the page's one motif on top, the figure set large and centred on it, the label in the body at 20/1.35; four figures make four columns; no heading row. Phone: sideways scroll, 298 wide | `figures[v,l]` · pictures `media.made.land[0]`, four crops, veiled 52% |
| 11 | Foot over the canvas: social icons left; at the centre line two link columns 325 wide with small grey labels; 200 lower a 36/300/1.15 line and two buttons; hairline; legal left at 17, mono links right | logo in place of the social icons; columns without labels; close line + its text + buttons; `foot.text` small above the hairline; legal row | `brand`, `nav`, `links`, `signin`, `cta`, `close`, `foot` |

Left out because the reference has no place for them: `hero.kicker`, `hero.note`, `steps.text`, `quotes`,
`media.video`, and `media.screens` except as the stand-in for a step with no picture of its own.

Type scale (1440 → 390): 86 → 45 (72.6 when the h1 is longer than 48 characters) · 72.6 → 40 · 57.4 → 40 · 43.9 (list,
hidden on the phone as in the reference) · 36.1 → 25 · 26.5 → 25/300 (card headings) or 20 · 21.3 → 18 · 18 → 17 · 17 →
16 · 16/500 · 15 · mono 13/1.07 uppercase −0.025em. Margins 40 → 15; gaps 20 → 15; panel pad 82 → 40; panel overlap
60 → 30; radii 32 (panels) · 15 (visual boxes) · 10 (cards) · 7 (buttons, nav, squares). Buttons 54 → 42 high, pad 20 → 14.
The phone build is used up to 1100px; the reference's tablet build was not measured.

## Font stand-ins
- ABC Favorit (commercial; h1, large headings, list) → **Hanken Grotesk** 300 (OFL). Tracking −0.03em/−0.04em in place of
  −0.025/−0.05em because Hanken sets a little wider.
- Suisse Int'l (commercial; text, h3) → **Inter** 400/500 (OFL).
- Suisse Int'l Mono (commercial; labels, buttons, nav) → **IBM Plex Mono** 400 (OFL).

## Colour
The reference: near-black canvas, white type on it; a white panel and a slate panel with navy type; pink accent with
dark type on it, pink→magenta gradient for the accent word. Ours: `dark` = the darker of ground/ink, `lite` = the other.
Panel 1 = `lite` mixed 60% to white; panel 2 = `lite`; cards = `lite` + 7% dark; grey text = dark at 68%, pushed until
it reads 4.6:1 on the card. Accent as type: on dark pushed to 4.6:1, on the light panels to 3.1:1 (it is only used
from 40px up); the gradient runs from that to a 25–30% mix with the text colour. The button text on the accent is
whichever of dark/lite contrasts more.

## Motion — measured, and what is reproduced
| Measured on the reference | Reproduced |
|---|---|
| One WebGL canvas, `position: fixed`, behind the whole page; dark sections are windows onto it, light panels (z above, r32) slide over it. The scene differs between the opening/foot (ribbons) and the middle section (a sphere) | yes, as one fixed picture: each dark section clips a fixed copy of land[0] (`clip-path: inset(0)`), enlarged in the middle section as the reference shows another view of its one scene there. The canvas's own animation and its "click and hold" pointer interaction are not reproduced |
| Loader 1s (three bars of the logo), then the h1 words flicker in: opacity 0 → .34 → 1 → .27 → 1 within about 0.5s | flicker yes, per word, `.45s steps`, 45ms apart, CSS only (text is visible without scripts). No loader |
| Header: `transform .2s cubic-bezier(.645,.045,.355,1)`; away when scrolling down, back on the first scroll up | yes; also returns when anything in it has keyboard focus; the open phone menu closes when it leaves. Without scripts the header is not fixed at all (it stays at the top of the page) |
| Mark row: no clock; x moves −0.29px per scrolled px and keeps easing for about 1.5s after the scroll stops | yes (lerp .12 per frame) |
| Dot field: square `transform: scale(0→1) .2s cubic-bezier(.645,.045,.355,1)`, opacity .85, under the pointer; a few cells are lit with no pointer near | hover yes; one random cell lights every 0.7s for 1.8s while the field is in view — that timing is a guess, the reference's rule was not measured |
| Buttons: an inner darker fill from `scale3d(.9,.7,1)`, opacity 0 to full in .2s, same curve; the label scrambles to random capitals and resolves left to right, about one letter per 30ms | yes, both; a press scales the button to .97 (the reference has no press state — added per the owner's "page answers a press") |
| Sticky list: colour `.2s cubic-bezier(.4,0,.2,1)`; the item whose card intersects turns dark; click scrolls to the card | yes |
| Segmented tabs: indicator slides, `left/width .2s cubic-bezier(0,0,.2,1)` | not reproduced — no tabbed data (see below) |
| Feature link rows: the text span has `transform .2s cubic-bezier(.4,0,.2,1)`; the hover value was not captured | text shifts 6px on hover — the distance is a guess |
| Carousel with two arrow buttons | not reproduced; plan cards are a grid |
| Custom 150px pointer ring with a mono caption over the canvas | not reproduced (it belongs to the canvas interaction) |
| Reduced motion | no flicker, header stays, row does not move, no scramble, no self-lighting cells, transitions off |

## Owner's rules that override the reference
- **No picture boxed beside text.** The reference's link cards (7) carry a 135px icon tile beside the text and its case
  cards (8) a mark in a box: both dropped. The visual boxes in (5) stay as the reference builds them — a picture ground
  with an interface standing on it, above its own heading and paragraph — but see Unsure.
- **Screens whole.** Step pictures stand on the ground at their own ratio (`max-height 487`, phone 448), never cropped.
  Made pictures (grounds, backdrops, card tops) are cropped `cover`; they are grounds, not product screens.
- **No invented words or icons.** No "why/security/features" labels where the data has no title for them, no icons on
  the points, no "try now"/"read" captions, no column labels in the foot, no heading over the link cards and the figure
  cards. The only word the template brings is "Menu" on the phone button.
- **Text over pictures is veiled** toward the dark ground: 52→70% over all three dark sections, 52% over the figure
  cards and the step grounds.
- **Header (owner, 2026-11-12, after a white wordmark sat on a plan card on his phone).** The reference's header has no
  ground and its white name vanishes over light panels. Ours: at the top it is as the reference; once scrolled it has a
  ground — the dark ground at 88% with blur over dark sections, the panel's paper with a hairline over a light panel,
  where the logo is its own dark version (no filter), nav box, menu and light button take card grounds and dark type.
  `probe/hdsweep.mjs` forces the header on at every 90px of scroll.
- **One picture family (CONTRACT, 2026-11-12).** Motif: `land`, picture `land[0]`. Backdrops, step grounds and figure
  cards are all that one picture in other crops. `blur`, `field`, `sky`, `sheet` and `land[1–5]` are not used. First
  build used a different blur hue per step and four different landscapes behind the figures; both rejected.

## What could not be transferred, and why
- The 3D ribbons/sphere and their animation — imagery of theirs; made landscapes stand in.
- The four different visuals inside the list cards (benchmark bars, hex map, terminal, line chart) — invented product
  imagery if rebuilt; each card shows the client's own picture instead.
- Segmented tabs, carousel arrows, mega-menu, social icons, loader — no data, or theirs.
- The pale idle colour of the sticky list (about 1.5:1 on the reference) — ours is the grey at 72%, ≥ 3:1, so the
  dark/pale difference is smaller.
- On the phone the reference hides the intro's left line; ours keeps `statement.text` under the heading.

## Image slots
| Slot | Reference shows | Takes | Still without a picture |
|---|---|---|---|
| Backdrop, opening + middle + foot (`.bd`, fixed, full screen) | its one ribbon scene, two views | `made.land[0]` (middle: enlarged) | — (plain dark ground if absent) |
| Ground of each step visual (`.vis`, 670×583 r15) | the ribbon motif, dark | `made.land[0]`, crop per card | — (plain dark if absent) |
| Step visual itself | product UI drawn in HTML | `steps.items[].img`, else `media.screens[i]` | a step with neither shows no box |
| Figure card tops (`.pic`, 440×372) | crops of the ribbon motif + white icon | `made.land[0]`, crop per card | — |
| Link-card tile (135×135) | line icon on slate | nothing — dropped (boxed beside text; no icons) | yes |
| Case-card mark (202×167) | customer logo | nothing — the price stands there | — |

## Picture share (`tools/coverage.mjs`, 1440)
```
reference  {"height":10870,"screens":13,"picture_share":17,"per_screen":[100,0,42,0,0,0,0,0,5,1,59,0,0],"screens_with_wide_picture":1}
sportbot   {"height":9854,"screens":11,"picture_share":42,"per_screen":[100,27,75,70,91,31,0,0,0,64,0],"screens_with_wide_picture":4}
automateed {"height":8898,"screens":10,"picture_share":46,"per_screen":[100,22,73,74,83,39,0,0,65,0],"screens_with_wide_picture":5}
```
Ours is above the reference overall and has the wide picture on the first screen where the reference has its one.
The tool skips `position: fixed` elements and reads a fixed scene only where it sits at scroll 0, for the reference
(a canvas inside a fixed wrapper) and for ours (an img inside a fixed wrapper, built that way so both read alike): the
backdrop seen through the middle section and the foot is counted for neither.

## Checks (final run, after the header and one-motif changes)
`tools/shots.mjs`:
```
sportbot   d {"height":9854,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
sportbot   m {"height":9897,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
automateed d {"height":8898,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
automateed m {"height":8163,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
```
`tools/legible.mjs` (the gate): sportbot `ok — 0 unreadable of 406 line readings`, automateed `ok — 0 unreadable of
250 line readings`.
`probe/hdsweep.mjs` — header forced visible at every 90px of scroll: sportbot 100 positions at 1440 (58 over a light
panel) and 96 at 390 (55), automateed 89 (52) and 77 (42). At every one: the header has a ground once scrolled, the
wordmark is unfiltered exactly when over light, every header text ≥ 4.5:1 against the rendered pixels (800/192 and
356/77 readings, 0 bad), and the header was away at every step while scrolling down.
`probe/audit.mjs`: sportbot 192/135 texts, 0 low; 39/31 Tab stops all ringed and on screen; reduced motion respected;
nothing hidden with scripts off. automateed 132/104 texts: 0 low at 1440; at 390 one low reading
("85%", 1.51) which is the audit's own artefact — that figure was sampled at a step where it sat half above the
viewport, under the header the audit forces on; `legible.mjs` reads the same page ok. 18/20 Tab stops ringed.
`probe/nopic.py`: sportbot with every picture removed renders, passes legible and shots (see `needs.json`).
Limits: the ring's own colour against its ground, hover states and the open phone menu were not measured for
contrast; Safari/Firefox not opened (`clip-path` + fixed child, `color-mix`, `:has`, `text-wrap: balance` are the parts
to look at there — in particular whether iOS Safari keeps the clipped fixed backdrop while scrolling); the header's
hide-on-scroll was driven by wheel and `scrollTo`, not by touch momentum on a real phone. Render 0.3 ms per client.

## Unsure
- The accent word in headings is the longest word of the title. The reference picks by meaning; the data does not say.
- `trust[]` set in type in the customer-mark row: the reference shows marks, not words.
- Step visuals: unframed screen on a made ground, in a column next to the sticky list — whether that satisfies "never
  boxed beside text" to the owner's eye.
- Plans in the case-card slot, FAQ in the link-row slot, figures in the article-card slot: the anatomy is the
  reference's, the content kind is not.
- With one dark dusk picture everywhere, sportbot's step grounds and figure cards are close to plain black; the motif
  shows mainly in the opening and foot.
- The header's ground once scrolled is the owner's rule, not the reference's build.
- Wordmark logos are shown white on the dark header and foot by a CSS filter (automateed's is dark navy on transparent).
- The link cards keep the reference's 167px height without its tile and caption, so they sit rather empty.
