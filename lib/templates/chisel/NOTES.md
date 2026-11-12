# chisel — notes

Reference: https://chiselindustries.com (home), and its /team, /capital, /about and /contact pages for the parts the
home page does not have. Measured 2026-11-12 at 1440×900 and 390×844 with `tools/anatomy.mjs`, `tools/shots.mjs`,
`tools/coverage.mjs` and own Playwright probes kept in `ref/` (`measure.mjs` box/style tree → `tree*.json`;
`motion.mjs` load sampling, scroll, hover/press/focus; `menu.mjs` the phone menu). It is a normal scrolling page of
type and photographs, an investor-and-software firm for the building trades; no canvas, no 3D, no cut-outs.
Three kinds of statement are kept apart: **measured** (read off the live page), **chosen** (my decision where the
reference gives no answer or the owner's rules override it), **not verified**.
Test clients: `corp1` (primary) and `law1`. Niche: corporate.

## Sections, in page order, and the data each takes

| # | Reference part (measured) | Data | Left out when |
|---|---|---|---|
| 0 | Bar over the opening, `position:absolute` (leaves with the page): mark left, six links right, 20/500, 50 apart. Phone: 32 px accent square, panel in the accent under the bar | `brand`, first five `nav` + `cta`; phone menu: all `nav` + `cta` | never |
| 1 | Opening, 100svh, dark ground, photograph under three veils, type at the foot: mono eyebrow, h1 79, text 20, a 920-wide box of three linked cells | `hero.kicker/title/text`; photograph: first free landscape ≥ 1600 wide; cells: first three `catalogue.groups` (title, first sentence of text, link to its section), else first three `features` | no title and no brand; cells when neither catalogue nor features; then `hero.primary/secondary` stand under the text as on the reference's sub-pages |
| 2… | Home "01 / 02 / 03": the three numbered sections, cycled in the reference's order of grounds — light: head left, numbered rows with a turned square right · dark: head and rows left, the visual right · second light: picture left, head and ruled rows right | one section per `catalogue.groups[]`: eyebrow `NN · catalogue.title`, h2 `t`, `text`, items (name, text, note, price, prices[], rows[], state, link); `catalogue.text` leads the first, `catalogue.note` closes the last; `group.img` as the half in the 2nd and 3rd of every three | no groups |
| — | /capital "three ways": three dark panels, radius 12 | `plans` (not in either test client; tried in variants) | no plans |
| — | /capital band: photograph 460 high, veil left to right, a line at 34/500 and a mono line | `statement.text` + `statement.title` (as the section's h2), when a free landscape ≥ 1600 exists | no such photograph (then head and text stand in the next section) |
| — | Home "02": text, figure rows (value 30 in the accent, 114 column), outlined button + arrow link; right a panel, radius 14, header with a dot, ruled rows with a mono label | `hero.text2`, `figures[]`, `hero.primary/secondary`; panel: `brand.name`, `place.since`, `credentials[]` (year or running number, title, text, link, badge image when the file is not one of the photographs); `trust[]` only when there are no credentials | no statement title, figures or credentials |
| — | /capital "what you get": ruled cells, 3 across, 40×4 accent bar | `features.title/text/items[t,d]` | no items |
| — | band again | `steps.text` + brand name over the first step picture, when it is ≥ 2.2 times as wide as tall | no such picture |
| — | Home "03" rows (history) or home "01" numbered rows | `steps.title/items`: with a `k` that is not the title or a number → ruled rows `k` \| title + text; otherwise numbered rows | no items |
| — | band again | one of `quotes[]` (first of ≤ 200 characters) over a free landscape ≥ 1600 | no such photograph |
| — | /team "what partners say": ruled cells, mark 48, quote 20 in the display face, name, mono role | up to six more `quotes[]` | none left |
| — | /team "leadership": dark, 3 across, portrait 433×542 with a foot veil and 15 % grey, name 24, mono role | `team.title/text/items` or `groups`; text, phone, email added under the role (**chosen**); people without a portrait as a ruled list in two columns | no people |
| — | Home "03" (one project) or /capital "two films" (several) | `projects[]` (title, text, first photograph) | none |
| — | Home "01" rows without the square | `faq` | no items |
| — | /contact: eyebrow, head 65, a ruled block of details; right column; /capital "guides": 4-across small cells | `contact.form.t` or `cta.t` as head; `contact/place` phone (its note as mono label), email, address, hours, social, booking; right: `contact.routes[]`; below: `locations[]` in ruled cells, `links[]` in small cells | nothing of these |
| — | Home close: centred, eyebrow, h2 ≤ 18ch, button + arrow link | `hero.kicker`, `close.title/text/cta`, phone | no `close.title` |
| — | Foot: mark, line in the display face, mail underlined, columns under mono heads, a ruled bottom bar in mono | `brand`, `hero.title`, `foot.text`, email, `place.social`; columns: all nav (head: brand name), catalogue groups (head: catalogue title), routes and locations with a link (head: contact head); bar: `foot.legal`, `foot.links`, `hero.kicker` | never |

corp1 gets 17 blocks (opening, four groups, three bands, statement, features, history, quotes, people, project,
contact, close, foot); law1 gets 13 (no bands, no halves, no project).
Two neighbours on the same ground are parted by a hairline (**chosen**; the reference never has that case).
Eyebrows are the running number alone outside the catalogue sections: the reference writes a short label there
("Track record", "Leadership"), the data has none and none is invented.

## Measures used (measured unless marked)

- Grid: 12 columns, 24 gutter, 50 page padding (phone 4 columns, 20). Head column 1–5 (544), second column 7–12 (658).
  Sections 50 + 50 above and below; close 100 + 50; foot 100 + 50 above, 50 below.
- Grounds and their relations, taken as relations to the client's palette: light page, second light, dark = text
  colour, panel = dark lifted 7 %; accent bright on dark, deepened on light. Muted text at 85/75/65/60/50 % of the ink
  over its ground, each raised until 4.6:1 (**chosen**; the reference's own 60 % passes on its cream, not on white with navy).
- h1 5.5vw (79.2 at 1440; 38.4 phone), 1.05, max 8.9em. h2 80/1.1 (64 from 1024, 48 from 768, 34.4 phone).
  Lede 24/1.6 (21.3; 20/1.4 phone). Eyebrow mono 11.2, +.18em, caps. Card title 20/28, card text 14/19.25.
- Opening cells: 920 box, 1 px gaps and border at 15 % of the light, cell 28 padding (24), fill dark 70 % + blur 12, 8 px turned square.
- Numbered rows: 28 above and below, 1 px rule, square 36 with 2 px line, turned 45°, number 14/700, title 24/32, text 18/29.25 (20/28 and 16/26 phone).
- Ruled rows: 16 above and below, title 20/28 in a 16ch column, text 16/22; stacked on the phone.
- Figure rows: 14 above and below, value 30/36 (24/32), text 18/28 (16/24).
- Panel: radius 14, padding 32 (24), 1 px line at 10 %, shadow 0 25 50 −12 at 25 %; rows 16 above and below; mono label 10.4, +.15em.
- Cells: 1 px gaps, padding 32 (28), bar 40×4, title 24/32, text 18/29.25. Quote cells: padding 36 (32), mark 48, quote 20/27.5 (18/24.75).
- People: 3 across, 20 × 40 gaps (2 across on the phone; one across when the texts are long — **chosen**), picture 433:542.
- Band: 460 high, text 34 with −.02em over 8 columns (24/1.2 phone), mono line 14 with +.25em.
- Buttons: 12 × 32, 2 px line, no radius, 16/24 weight 500; arrow link 12 × 8 with the arrow in the accent.
- Small cells: 4 across (2 on the phone), padding 20, title 18.
- Foot: mark, line 24/33 at 22ch, links 15.2/22.8 on 12 gaps, bar 11.2 mono with +.18em, rule at 12 %.

## Typeface stand-ins (Google Fonts, SIL OFL)

| Reference | Stand-in | Why |
|---|---|---|
| PP Editorial Sans (commercial), 500 | **Alegreya Sans** 500 (400 in quotes) | a humanist sans with flared, calligraphic strokes and narrow proportions; nearest in kind. It is lighter in colour and has a smaller x-height than the reference at the same size (seen in the pairs) |
| Aeonik (commercial) | **Albert Sans** 400/500/700 | geometric grotesque of the same plain build |
| JetBrains Mono | **JetBrains Mono** 400/500 | the reference's own mono is open-licence (OFL) |

Heading tracking is −.03em (h2) and −.02em (h1), not the −.04em / −.025em measured: Alegreya Sans is set tighter (**chosen**).

## Motion — measured, and what is reproduced

| What | Measured | Here |
|---|---|---|
| Opening picture | `scale(1.08)` → 1 in 2 s, cubic-bezier(.16,1,.3,1), once | same |
| Opening eyebrow and cells | opacity 0 → 1 and 18 px rise in .7 s, same curve; cells .15 s later; h1 and text do not move | same (CSS only, `both` fill: nothing stays hidden without scripts) |
| Scroll | nothing: no element below the fold has opacity or transform before it is reached; the bar is `absolute` and scrolls away; nothing is pinned | none; **chosen addition**: a picture half taller than the window holds at the top of the window while its text passes (`position:sticky`), so the photograph is never stretched beyond the window's height |
| Links in the bar | opacity .7 in .3 s cubic-bezier(.4,0,.2,1) | same |
| Opening cells | fill 70 % → 90 % in .3 s; arrow moves 4 px in .3 s | same |
| Buttons | fill and ink change places with no transition; the same on press | same |
| Arrow links | arrow moves 4 px in .3 s | same |
| Foot links | colour to full in .3 s | same |
| Phone menu | panel fades in .3 s, bar takes the accent | same, built on `<details>` so it opens without scripts |
| Focus | no visible ring on the reference's button under a programmatic focus | **chosen**: 2 px ring in the accent, 3 px away |
| Reduced motion | the two opening animations are switched off | all animation and transitions off |

No script on the page.

## Where it departs from the reference, and why

- **Boxed picture → edge-to-edge half.** The reference's home "03" stands a 544×680 picture in the page beside the text.
  Here it is a half that bleeds off the page edge and runs the full height of its section (same right edge, column 5),
  as CONTRACT allows; on the phone it is a full-width picture above (or below) the text at the photograph's own
  proportion held between 4:5 and 3:2. The same build takes the dark section's right side, where the reference has a
  drawn interface the client cannot supply. /team's boxed picture beside "We honor what you built" is not used.
- **Veils.** The reference's photographs are dark; these clients' are bright workshop pictures. The opening's veils are
  stronger (bottom-up 100/70/25 % at 1440 and 100/90/84 % on the phone, left-to-right 92/80/45/0, top 88 %), and the band's
  right end is 40 % instead of 30 % (flat 88 % on the phone), so that every line reads at 4.5:1 on a white pixel. The
  opening eyebrow takes the accent pushed to 8:1 against the dark. Result: the phone opening shows its picture only faintly.
- **Opening cells** have no "Explore …" words (none in the data): an arrow alone.
- **Phone menu** links are 16 px (measured 12 px) and take whichever of dark/light reads on the client's accent.
- **Skip link** of the reference is not reproduced (its words are not in the data).
- **Panel** has no pair of buttons at its foot (the reference's belong to its drawn interface).
- **Mark**: the brand name set in Albert Sans 700 (the reference's logo is never taken); `brand.logo` when present.
- Long values in figure and price rows: the value column grows to its content (≤ 46 %) and rows stack on the phone
  when a value is longer than nine characters (**chosen**; the reference's values are short).
- Plans: 1–4 across in one row; five as 3 + 2; more wrap in threes (**chosen**).

## Picture slots (the client's own photographs; `media.made` is not used)

| Slot | Takes | corp1 | law1 |
|---|---|---|---|
| opening | first free landscape ≥ 1600 wide, workshop/exterior/room/work/action/people first | workshop-5axis-operator | colleagues |
| halves | `group.img` ≥ 800×800 of the 2nd and 3rd group in every three; the one project's photograph | parts-on-drawing (right), inspection-projector (left), team-hare-car (left) | — |
| statement band | free landscape ≥ 1600, detail/product first | parts-flanges | — (statement stands as head and text) |
| history band | first step picture when ≥ 2.2:1 and ≥ 1600 wide | history-first-workshop (2400×709) | — |
| quotation band | next free landscape ≥ 1600 | parts-passivated | — (all three quotes in cells) |
| people | each person's own portrait | 4 of 5 | 10 of 35 |
| credential badge | `credentials[].img` when it is not one of the photographs | — (the award picture is a photograph: not shown small) | three award badges |

Each photograph is used once; `small` pictures and pictures under the size of their slot are passed over; portraits
stand only with their person. Unused: corp1 12 of 24 (among them the item pictures of the catalogue, which this build
has no slot for); law1 `firm-group.jpg` (1128×376, too small to run edge to edge at 1440).
Without any photograph: the opening is the dark ground with type and cells, sections keep their two columns, people
become a ruled list — rendered for both clients, shots clean, corp1 looked at.

## Picture share (`tools/coverage.mjs`, 1440)

| Page | Height | Share | Per 900 px screen | Wide pictures |
|---|---|---|---|---|
| reference home | 4 728 | 25 % | 100, 0, 0, 30, 0, 0 | 1 |
| corp1 | 17 248 | 25 % | 100, 4, 11, 44, 39, 0, 29, 24, 0, 0, 53, 53, 0, 57, 22, 17, 20, 0, 0, 0 | 3 |
| law1 | 14 774 | 18 % | 100, 0, 0, 0, 0, 0, 0, 34, 76, 69, 20, 0, 0, 0, 0, 0, 0 | 1 |

Both pages are more than 1.5 times the reference's height, so the overall share is not the comparison (revised rule);
the reference's one wide picture — the opening — is in place in both. law1 is 7 points under the reference overall and
has six screens of prices without a picture: it has no second photograph wide enough for a band.

## Checks

- `tools/shots.mjs`, both clients, 1440 and 390: no sideways scroll, no distorted media, one h1, errors [].
- `tools/legible.mjs`: ok for both (corp1 1245 line readings, law1 1203). An earlier build printed four FAILs on the
  corp1 opening and phone band (3.58–4.08:1); they were real and were answered with the veils above, not by changing the text.
- Variants (scratch copies, `ref/variants.py` → `out/look/var/`): see the report; shots clean on all five.
- Pairs: `pairs/<client>-1440-NN-<section>.jpg` (reference part above, ours below) and `pairs/<client>-390-01-hero.jpg`.
  In the pairs a picture half is shown at the full height of its section (the sticky hold is switched off for the
  screenshot), so tall halves look more enlarged there than on the page.

## Could not be transferred / not verified

- The reference's drawn "morning briefing" interface, its play buttons over films, its contact form: no data for them.
- The reference's commercial faces; its logo.
- Not verified: Safari and Firefox (only Chromium was run); the page between 391 and 1439 px wide other than by the
  CSS written for 640/768/1024/1280; the one-file copies were written but not opened; hover states were written from
  the measurements and not re-measured on our page; `prefers-reduced-motion` was not run in a browser.
