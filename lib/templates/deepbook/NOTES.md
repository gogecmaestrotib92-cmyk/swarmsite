# deepbook — notes

Reference: https://deepbook.tech (home page; it serves its scripts from deepbook.xyz), measured 2026-11-12 at 1440×900 and
390×844 with `tools/anatomy.mjs`, `tools/shots.mjs` and own Playwright probes in `probe/` (box/style tree of every element,
load sampled at ten moments, a per-frame log of opacity/transform/text of 300 elements over a wheel scroll of the whole
page, hover computed styles, the accordion sampled per frame, film frames every 140 ms). Raw captures: `ref/`, `cap/ref-*`,
`probe/`. Three kinds of statement are kept apart: **measured** (read off the live page), **chosen** (my decision where the
reference gives no answer or the owner's rules override it), **not verified**.

## Sections of the reference, in order, and the data each takes

| # | Reference section (measured) | Data | Left out when |
|---|---|---|---|
| 0 | Bar, sticky, the page's dark colour, 88 + 1 px rule (76 + 1 on phone): brand left, links centred, one small button right. On phone the links are not shown at all (no menu) | `brand`, `nav` + `signin` as links, `cta` | never |
| 1 | Opening: nothing but a 16:9 film, edge to edge. Its title and one line under it are part of the film (the page's h1 is hidden for readers only) | `hero.title`, `hero.text`; picture `made.land[0]` | no `hero.title` |
| 2 | Four figures in a row (2 × 2 on phone): the number in the accent colour, a bold label under it | `figures[v,l]` | no figures |
| 3 | Two panels side by side: a 624 × 349 picture, a name in large grey bold, a grey paragraph, three ruled rows of bold one-liners; one grey button centred under both | `plans.items[name, price, per, line, rows, cta]`, `plans.note`; pictures: `made.land[3]` (one ground for every panel, a different crop each, held quiet) with `media.screens[i]` standing whole on it | no plan items |
| 4 | Small accent label, typed heading, grey lede, a button and an underlined link; then a stack of folder tabs, numbered, alternating left and right, each a step lighter or darker than the last | `steps.title`, `steps.text`, `hero.primary` (button), `hero.secondary` (link), `steps.items[title, text]` as the folders | no `steps.title` and no items |
| 5 | Picture banner, 320 high, a typed heading at its lower left | `statement.title` (else `features.title`); picture `made.land[5]` | neither title |
| 6 | Tinted section, 1024 wide: a grey paragraph, a white card of ruled label / value rows, a wide picture, a button | `statement.text` (else `features.text`), `features.items[t,d]`, picture `made.land[2]`, `cta` | no text and no feature items |
| 7 | Accordion: large heading left, questions right, one open | `faq.title`, `faq.items[q,a]` | no faq items |
| 8 | Accent-coloured close: typed heading centred, one picture, a key-shaped button | `close.title`, `close.cta`; picture `media.video`, else `media.photos[0]`, `media.phones[0]`, last of `media.screens` | no `close.title` |
| 9 | Foot on the same accent: brand and a small line, link columns, then a picture band with the small print on it | `brand`, `foot.legal`, `nav` / `links` / `signin` + `cta` as columns, `foot.text`, `foot.links`; picture `made.land[1]` | never |

sportbot renders 0–9. automateed renders 0–6, 8, 9 (no faq), and its panels have no rows (its plans carry none).

Not shown by this template, because the reference has no place for them: `hero.kicker` (only in `<title>`), `hero.text2`
(only in the meta description), `hero.note`, `trust[]`, `plans.title`, `plans.text`, a plan's `marked`, `features.title` and
`features.text` when a statement exists, step `k`, `img` and `cta`, `close.text`, `quotes`, `logos`, link descriptions `d`.
`media.phones` and all but the first two `media.screens` appear only if the close needs them.

## Measures used (measured at 1440 / 390 unless marked)

- Frame: content `min(100% − 2 × gutter, 1280)`; gutter 80 / 20. Section padding 126.4 / 64, the short one 71.2 / 40.
  Between the two widths every size runs in a straight line (**chosen**: the reference uses its own curves, which I did not copy).
- Type: display 71.2 / 40 at 1.05; section heading 52.8 / 32 at 1.08; panel name 36 / 24 at 1.15; lede 22 / 18 at 1.5;
  body 18 / 16.14 at 1.6; small 14 at 1.5; base 16 at 1.5. Two weights only, 400 and 700. No tracking anywhere.
- Colour relations: canvas, ink, one accent, and the page's dark for the bar. Grey text reads 4.6:1 on the canvas; rules and the
  grey button are one colour (ink 14 % into the canvas here); the tinted section is 30 % of that into the canvas. The accent
  carries the buttons, the figures, the open accordion row, the folders, the close and the foot.
- Bar: grid 1fr / auto / 1fr, links 16/24 with 32 between, button 44 high, 0 × 20, 14 px bold, radius 4.
- Opening: `aspect-ratio 16/9`, so 810 high at 1440 and 219 at 390. Title in the film ≈ 95 px bold on a 104 px pitch at 1440
  (6.6 vw), second line ≈ 56 px regular (3.9 vw), block centred a little below the middle (≈ 57 %); the same proportions at 390
  because it is a film.
- Figures: cell 296 wide, 32 between (163 and 24 on phone, rows 48 apart); number box 144 / 128 high, number 41.76 / 32 bold,
  tabular; label 16 / 14 bold, 20 / 16 under the box.
- Panels: two columns of 624 with 32 between (one column, 64 apart, on phone); picture 624 × 349; 32 / 24 between picture,
  text and rows; rows 12 apart, equal height, min 80, padding 20, 1 px rule, 16/24 bold; button 52 high, 0 × 28, 71.2 above.
- Typed-heading block: heading margin 24, lede max 832, actions 24 under it, 48 to the folders.
- Folders: curve 96 wide (56 on phone), tab 72 high (64), 16 above it, label 26.64 / 18 bold with the number 10 before it;
  text 18/28.8 starting under the label (x = 184 at 1440); on desktop each folder starts 88 px after the previous one, so its
  tab stands beside the previous folder's text; right-hand tabs start at the page's centre; 1 px lighter edge along tab and
  top. On phone folders follow one another, all tabs at the left edge, text padded 28 / 44.
- Banner: min-height 320 (384 on phone), content padded 48 / 32, heading at the section size.
- Fact list: paragraph max 75ch, 32 under it; card radius 8, padding 8, rows 8 apart, min 72, padding 16 × 24 (16 on phone),
  two equal columns; picture 1584:672, 71.2 above; button 32 under it.
- Accordion: columns 1fr / 2fr with 72 between (one column on phone); rows ruled, min 104, padding 24; question 22 / 18 at 1.4
  bold; toggle 44 × 44, radius 4; answer 16/25.6, max 65ch, 68 clear at the right, 28 under.
- Close: heading max 1024 centred; picture at most 544 wide, 71.2 above and 24 under; button 230 / 192 wide.
- Foot: 304 + rest with 64 between; links 18/28.8 bold in 44-high rows, four columns (two on phone); band min-height
  496 / 384; small print 14/21, max 78ch, links 24 apart, 32 padding.
- Focus ring: 2 px solid, 4 px offset, radius 4 (5 px offset on the key) — the reference's.

## Typeface stand-in (SIL OFL, Google Fonts)

| Reference (commercial) | Stand-in | Why |
|---|---|---|
| PP Mori 400 / 700 | **Wix Madefor Display** 400 / 700 | a plain round grotesque with the same straight-tailed y and two-storey a; eleven strings measured on the reference set 2.0 % wider or narrower on average in this face (Inter 1.9 %, Onest 1.9 %, Instrument Sans 2.5 %; table in `probe/font.mjs`). Onest was tried first and dropped for its curled y |

## Motion — measured, and what was reproduced

| What | Measured on the reference | Here |
|---|---|---|
| Bar on load | slides down from above: −69 px at 0.9 s, −15 at 1.5 s, in place by 2.2 s (desktop); in place by 0.9 s on phone. Never hides again | slides down .9 s, cubic-bezier(.23,1,.32,1), .15 s delay. The exact curve is **not verified** (six samples) |
| Opening | a 30 s looping film; in it each title line rises from behind its own baseline (line 1 ≈ .35–.6 s, line 2 ≈ .5–.9 s), the second sentence fades at ≈ 1.4 s; after ≈ 4 s the film leaves the title for product scenes | still picture; title lines rise .5 s, .17 s apart, from .3 s; second line fades at 1.2 s. The film itself is not reproduced (see below) |
| Figures | number: opacity 0→1 in ≈ .65 s, later columns ≈ .3 s later, digits run while it fades; moves 14 → −14 px with the scroll while it crosses the screen; label words fade in turn | same. How the digits settle is **not measured**; here they settle from the left over .9 s |
| Pictures in frames | layer 12 % taller than its frame, moves +6 % → −6 % of the frame with the scroll (20.94 px on 349, 19.2 on 320, 24 on 434), trailing the scroll slightly; picture scales 1.035 → 1 in ≈ 1 s when it comes in | same; the trailing is a per-frame ease of 14 % toward the target (**chosen**, the reference's lag was not timed) |
| Lines of text | each line rises 12 px and fades over ≈ .85 s, lines ≈ .117 s apart, ease-out | same (words are grouped by the line they stand on) |
| Panel name, rows, button | name 12 px / .5 s; rows 18 px / .6 s, ≈ .17 s apart, their words fading .18 s each, ≈ .065 s apart; button 8 px / .45 s | same |
| Row hover | hovered row scale 1.025, the others opacity .45 and scale .975, .24 s ease-out | same |
| Typed headings | a block cursor (≈ .52 × .86 em) appears, ≈ .23 s later the characters appear one each ≈ 60 ms with the cursor after the last one, the cursor blinks in .7 s steps and goes ≈ .38 s after the end | same |
| Folders | at first each folder hangs 48 px (24 on phone) lower than the one before; they close up to 0 with the scroll between the stack entering and its end reaching mid-screen | same |
| Fact rows | from scale 1.04, −12 px, opacity 0, ≈ .62 s, ≈ .18 s apart | same |
| Accordion | rows rise 18 px / .38 s, .066 s apart. Click: the open row closes while the clicked one opens, height and opacity together in ≈ .47 s, ease-in-out; toggle colours .18 s; question and toggle border take the accent on hover | same |
| Buttons | hover: up 3 px, scale 1.035, hard shadow 0 5px 0 at 24 % black, darker fill, .22 s cubic-bezier(.23,1,.32,1) (fill .2 s ease-out); press: down 2 px, scale .97, .1 s | same |
| Links | bar links go from 86 % to full; a 1 px line grows from the left under bar and foot links, .24 s cubic-bezier(.23,1,.32,1) | same |
| Closing button | two drawings swapped on press, no easing | a cap that sinks 9 px on press, no easing |
| Foot | link rows rise 14 px / .28 s, .117 s apart; the crowd picture is three layers that settle 7 / 20 / 35 px with the scroll | rows the same; one picture settling 20 px |
| Smooth scrolling | `scroll-behavior: smooth` | same, off under reduced motion |
| Reduced motion | film hidden (its still stays), buttons and link lines without transition, cursor off; the rest **not measured** | every animation and transition off, everything visible, no typing, no scroll movement; the close film does not play by itself and shows its controls |

Every hidden start state sits behind a `js` class that the script sets as its last step, so a page whose script fails or is
off shows everything; the accordion then works as plain `details`.

## What could not be transferred, and why

- **The film.** The reference's opening is a film with its words inside it. A client's film here is a product recording at
  its own ratio, which may not be cropped to 16:9, so the opening takes a made landscape and the title is real text laid
  over it at the film's scale, with a flat veil toward the page's dark (or light) for 4.5:1. Nothing moves in the picture.
- **No button in the opening.** The reference has none; the client's `hero.primary` / `secondary` stand in section 4, where
  the reference has its button and link. `hero.text2` and `hero.note` have no place. Unsure whether the owner accepts an
  opening without a call other than the bar's.
- **Line drawings behind the figures** (they draw themselves in ≈ .85 s each) are the reference's own drawings and fall under
  "no drawn strokes"; the number box keeps its measured height and stays empty behind the number.
- **Row icons** in the panels are the reference's icons; rows start at the padding instead.
- **Panel pictures** are the reference's collages, both on the one flat accent. Here: one ground for every panel too —
  the soft square landscape of the page's own series (`land[3]`), upper crop in the first panel, lower in the second,
  under a veil of the page ground (38 %; 72 % if the picture is light and the page dark) — and the client's screen whole
  on it (78 % × 70 % of the frame at most); with no landscape, the plain rule colour; with no screen, the ground alone.
  (Until 2026-11-12 each panel took a different `blur` hue — a vivid green and a bright mint panel on the dark page.) A plan and the screen above it are not related by the data — the pairing is by order only.
- **Panels are fed with plans**, the only data shaped name / paragraph / short rows / one button. The price stands as the
  first line of the paragraph in ink bold (**chosen**; the reference's paragraph is all grey). `plans.note` is set small under
  the button (the reference has nothing there). `plans.title` and `.text` are lost.
- **Small accent label** over the typed heading, and the label over the banner heading: no data of that kind; left out.
- **Folder texture** (a paper grain drawn in the reference) is not rebuilt; folders are flat. They step lighter when the
  accent carries dark text and darker when it carries light text, so the text gains contrast as in the reference.
- **Fact rows with long values.** The reference's values are one or two words, bold, right-aligned beside a grey label. A
  feature's description is a sentence, so when any value is longer than 40 characters the name is bold ink and the sentence
  grey, left-aligned, and on phone it stands under the name (**chosen**). Short values keep the reference's setting; that
  path is **not exercised** by either client.
- **Portrait beside the accordion heading** is an illustration of a person; no picture of that kind may be made. Left out.
  The "view all" link has no data.
- **Book illustration in the close** → the client's own film or picture, whole, at its own ratio.
- **Key-shaped button**: the reference's two drawings are not taken; a plain cap in a dark rim is drawn in CSS.
- **Crowd picture in the foot** shows people on the accent colour; a made landscape takes the band and fades into the
  accent at its top so there is no hard edge (the reference's picture has the accent as its own ground).
- **Foot column heads** have no data; columns are `nav`, then `links` not already listed, then sign-in and the call.
- **Bar colour**: the reference's bar is its darkest colour, not its ink. Here it is the darker of ground and ink, so on a
  dark client the bar is the page's own ground with a faint rule. A wordmark logo is turned to one flat light (or dark)
  colour by a filter where it stands on the bar or the foot, as the reference's mark is.
- **Phone bar**: the reference shows no links and no menu on a phone; the links are in the foot. Kept. A call longer than
  16 characters gets 12 px side padding and a smaller mark under 480 px so both fit.
- **Skip link**: the reference has one; its words are not in the data, so it is not rendered.
- `sign in` is added to the bar's links (the reference has no such link in its bar).

## Image slots (nothing generated)

| Slot (`data-slot`) | Reference shows | Takes | Without it |
|---|---|---|---|
| `hero-backdrop:land` | film still: a room at night | `made.land[0]`, cover | flat dark |
| `panel-N:land` + `panel-N:screen` | collage on flat accent (the same ground in both) | `made.land[3]`, crop by N, veiled toward the page ground + `media.screens[N−1]` whole | plain rule colour / ground alone |
| `banner:land` | halftone close-up photograph | `made.land[5]`, cover, veil from the left and bottom | flat dark |
| `facts-picture:land` | wide halftone photograph, 1584:672 | `made.land[2]`, cover | frame left out |
| `close:film` / `close:book|phone|screen` | illustration, about square | client film, else first photo / phone / last screen, whole | left out |
| `foot:land` | crowd from behind | `made.land[1]`, cover from the top, faded in | band without picture |

Still without a picture of its kind: the portrait beside the accordion heading; the line drawings behind the figures.

## Checks

`tools/shots.mjs` on both outputs at both widths: no sideways scroll, no script errors, no distorted media, one h1 (lines
in the hand-back report). Own audit (`probe/audit.mjs`): every text node against the rendered pixels behind it (5th
percentile of the pixels in its box; ≥ 4.5:1, ≥ 3:1 from 24 px or 18.66 px bold), every focusable reached by Tab shows a
2 px ring that reads ≥ 3:1 on the ground around it, zero running animations and nothing hidden under reduced motion,
nothing hidden with scripts off or with the script failing half-way.
Not done: no browser other than Chrome; widths between 390 and 1440 were not captured; hover and press states were set from
the measured values and not screenshotted; the long folder stack (more than three steps) and a short-value fact list were
not rendered by either client.

## Pass of 2026-11-12 (one picture family, picture share, readability)
- **Motif: `land`.** The reference repeats one kind: halftone photographs (film still, banner, wide picture, crowd in the
  foot, and the panel collages on one flat ground). Ours: opening land 0, panels land 3 (quiet), banner land 5, wide
  picture land 2, foot land 1. No `blur`, `sky`, `sheet` or `field` is used any more.
- **Picture share** (`tools/coverage.mjs`, share of page / per 900px screen):
  reference 1440: 34% [91,41,0,27,17,40,9,24,57] · 390: 26% [37,34,4,11,38,25,0,36,59]
  sportbot 1440: 32% [91,40,0,18,24,40,0,20,56] · 390: 23% [35,24,16,0,38,13,18,0,30,86]
  automateed 1440: 39% [91,40,0,42,39,12,38,100] · 390: 32% [29,46,0,51,16,28,57]
  Within 5 points at both widths; the wide pictures (opening, banner, wide picture, foot band) stand where the
  reference's do.
- **Readability** (`tools/legible.mjs`): sportbot `ok — 0 unreadable of 792 line readings`, automateed
  `ok — 0 unreadable of 334 line readings`.
- **Sticky bar**: opaque (the page's dark) with a rule, at every scroll position and both widths; nothing shows through.
- `shots.mjs`: sportbot d 8094 / m 8535, automateed d 6492 / m 6081 — sideways 0, distorted 0, one h1, errors [].
- Seen and left: the wide picture (land 2, water) carries strong orange reflections on both clients — livelier than
  the reference's grey halftone; it is of the family and carries no text. The close and foot on sportbot are a large
  mint (accent) field on a dark page — the reference's own accent close, a colour, not a picture.


## Fixes for the engine's gate (2026-11-12)

The header mark never shrinks (flex none, 26 high, width from its own ratio). On a phone the bar's columns are the brand at its own width and the call in the rest; a long call wraps beside the mark instead of squeezing it. Without a hero title the brand name is the h1.
