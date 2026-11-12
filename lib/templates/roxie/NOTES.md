# roxie — a person's own site, led by photographs

Reference: https://roxienafousi.com (home page), measured 2026-11-12 at 1440×900 and 390×844 with `tools/anatomy.mjs`,
`tools/shots.mjs`, `tools/coverage.mjs` and the probes in `probe/` (`probe.mjs` boxes/type/pictures, `labels.mjs` small
labels, `motion.mjs` scroll, list, row of cards, hover). Raw readings: `ref/anatomy.json`, `probe/probe.json`,
`probe/motion.log`, `probe/motion-m.log`. The cookie bar was passed with "Reject All" or left alone; nothing accepted.
Test clients: `person1` (primary), `local1`. Kind: sourced = read from the live page; chosen = my decision, marked.

## Sections of the reference and what each takes

| # | Reference (1440) | Ours | Data |
|---|---|---|---|
| 1 | First screen, 100vh: one photograph edge to edge; one bold capital line at the centre; the name as a wordmark across the whole measure at the foot. No header at rest. | same | first-screen photograph (see slots) · `hero.title` (the h1) · `brand.name` set in type |
| 2 | Accent band (orange, black ink): small label at column 4, a ruled list of three lines (31 px medium), each opens to date / place / bold link | same list, one block per group | `catalogue.groups[]` (label = `t`, paragraph = `text`, lines = items: name + price; opened: note, text, prices, rows, state, link) · then `plans` · `catalogue.note` |
| 3 | Centred sentence on white: small label, 50.6 px light italic serif over 9 columns, bold underlined capital link | same | `statement.title` (label) · `statement.text` · link = `hero.secondary` only when the hero has no text of its own |
| 4 | Half-and-half row, 714 high: left half pale with a ruled label at the top and heading / paragraph / underlined link at the foot; right half one picture | same anatomy, repeated; picture treated differently (below) | (a) opening words: `hero.kicker`, `hero.text`, `text2`, `primary`, `secondary`, `note` + a free photograph · (b) a single person: `team.items[0]` role / name / text / e-mail + portrait · (c) every `steps.items[]`: `k`, `title`, `text`, `cta`, `img` |
| 5 | "Products": full-width ruled label, centred 40 px serif heading + paragraph, a row of cards in two alternating sizes (2 and 3 columns; pictures 218×241 and 335×417), title and bold link under each, arrows at the page edges | heading part before the step rows; the cards for projects | heading: `steps.title` / `steps.text` · cards: `projects[]` (first free photograph, title, text, link) |
| 6 | "Mission": pale ground, small label, 45 px capital display serif over 9 columns, bold link | twice | `quotes[]` (label = name, role) on the pale ground · `close` (title, text, cta) on the page ground |
| 7 | "Latest": ruled label, cards of 3 and 4 columns: bold capital title above, 16:9 picture below, the smaller pictures centred on the larger | same | `team` with two or more people: name above, portrait, then role / text / phone / e-mail · `team.title`, `team.text` as the heading |
| 8 | "As seen in": pale ground, a row of marks 21 px high, link at the right | row of lines | `logos[]` (files) or else `trust[]` as lines of type |
| 9 | Foot, deeper ground, 285 px empty above four columns (cols 1–3 text · 5–7 policies and copyright · 8–9 links · 10–12 newsletter field) | same columns | `foot.text` · `foot.links` + `foot.legal` · social + `links[]` · `cta.t` as label, then phone, e-mail, reply note, form, booking, address, hours, locations |
| — | (not on the reference's home page) | ruled lists on the page ground, built from part 2 | `features` (title, t → d) · `credentials` (t → text, year, badge, link) · `faq` (q → a) |
| — | Phone only: "The Books" row of cards | not built | — |

Order on our page: 1 · 2 · 3 · 4a · 4b · 5-heading · 4c… · 5-cards · features · 7 · 6 quotes · credentials · faq · 8 · 6 close · 9.
Chosen: the reference has one half-and-half row; we repeat it once per step because a card (title + link) has no room
for a step's paragraph, and the paragraph is what the visitor reads. person1 has six such rows, local1 four.

## Measures used (1440; 1rem = 14.6834 px = 1.01968vw, as the reference scales everything with the window)

- Grid 12 columns, gutters 1rem (14.7), margins 2rem (29). Column 4 starts at 378.
- Header 59 high (padding 31.6 / 11), fixed; links 10.87 px capitals, tracking .05em, 37 px apart; wordmark 113×13 at left.
- First screen: line 23.18 px bold capitals, leading .969, 73 px margins, at 50 % (translated −35 %); name 1381 wide, 30 px above the foot.
- Band: padding 69.7 / 55; label 11.87 px capitals tracking .05em; 29 px to the list; lines 54 high, 30.97 px medium, leading 1.14, tracking .021em; plus 16 px, 161 px in from the right; opened: 14.68 px lines from 34 px below the title, bold link, 51 px below.
- Centred sentence: padding 80.8; label → sentence 38; 50.63 px, leading 1.07, tracking .015em, 1031 wide; link 14.68 bold capitals, 1 px rule, 40 below.
- Half-and-half: 714 high (49.6vw); label row 29 above, 13.5 below, 1 px rule 661 wide; heading 40.28 px light serif, leading 1.02, tracking .02em; paragraph 14.68/17.6, 396 wide; 18 px steps; 29 to the foot.
- Cards heading: label row 56 high; 107 above and below the centred heading; cards 218 / 335 wide, 14.7 apart; 17.6 to the title; section foot 74.8.
- Mission: padding 80.8; 45.33 px capitals, leading .92, tracking .009em.
- Latest: 125 from the rule to the titles; titles 14.68 bold capitals; 52 to the larger picture; cards 335 / 451.
- Marks: 66 above, 62 below. Foot: padding 285 / 29.
- Colours as relations: page ground · pale = ground + 2.2 % ink (#faf9f7 on white) · foot = + 6 % (#f2efeb) · one accent band. Radii: none anywhere.
- 390 (1rem = 10.066 px = 2.581vw): margins 14; header 46 with three-line opener left and the name centred; line 11.07 px; name 362 wide 14 above the foot; band padding 121 / 92, lines 44 high at 20.13 px, plus at the right edge; sentence and capitals 23.15 px leading 1.26; half-and-half stacks words then a square picture edge to edge; cards 201 wide one at a time, centred, 40 apart; people cards 281 wide, title centred; foot: contact first, then text, then two columns.
- Chosen: below 1024 px the phone build (the reference's breakpoint was not measured); root size floored at 11.5 px on desktop and capped at 13.5 px on the phone build.

## Fonts (open licence, Google Fonts)

| Reference | Stand-in | Where |
|---|---|---|
| Helvetica Neue LT Pro roman / medium / bold | Arimo 400 / 500 / 700 (the metric-compatible grotesque) | text, labels, list lines, bold links |
| Lyon Display light, light italic | Newsreader (72pt optical size) 360, 360 italic | headings, the centred sentence |
| Louize Display; the wordmark | Cormorant 500 | capital display lines, the name |

Arimo runs a little wider than Helvetica Neue at the list size; Cormorant's capitals are lighter and wider-set than the
reference's wordmark. The name is fitted to the measure by script (CSS estimate from the letter count without script).

## Motion — measured, and what was reproduced

| Measured on the reference | Ours |
|---|---|
| The name follows the scroll one to one: at 1440 its top goes 709 → 32 (viewport) and its height 161 → 18 between scroll 0 and ≈ 823, linearly (sampled at 13 positions); at ≈ 850 it is swapped for the header wordmark. On the phone it shrinks toward the centre (42 → 18 high by scroll ≈ 803). | reproduced: same linear scrub, ends where hero height − header − wordmark height is reached, swap to the header name; origin left on desktop, centre on the phone |
| Header at scroll 0: transparent, links at opacity 0; from the first pixels: ground colour (background .15s cubic-bezier(.25,.1,.25,1)) and links (opacity .15s) | reproduced; also shown whenever something in it has keyboard focus |
| List line opens: height over ≈ .3s on the phone (44 → 138 sampled every 60 ms); plus turns to a minus | reproduced with `<details>` + a .3s height animation; the plus → minus as a .25s turn of one bar (the turn itself was not measured, only the two states) |
| Row of cards (Flickity): wraps round endlessly, arrows 29 px at the page edges, a press moves ≈ 438 px and settles in ≈ .45–.6s; dragged on the phone | native sideways scroll with snap; arrows only when the cards do not fit (person1: no cards; local1: five cards fit at 1440, so no arrows there); no endless wrap |
| "Latest" thumbnails: filter none → grayscale(1) over .3s on hover | reproduced on the people cards |
| Phone menu: full-screen sheet in the ground colour slides down, transform .6s cubic-bezier(.23,1,.32,1) after .1s; links 20 px medium between rules, at the foot of the sheet; opener bars .25s | reproduced; opens by `:target` without script |
| Page fades in: opacity .5s | reproduced as a CSS animation (no script needed) |
| Link rules: nav links carry a transparent 1 px rule; text links a visible one | hover states chosen (nav rule appears, text-link rule goes): the reference's hover could not be read under its newsletter sheet |
| Not reproduced: the newsletter sheet that covers the page after a few seconds, the cart drawer, the orange loading squares over pictures, the cookie bar, video embeds. |

Reduced motion: no scrub (the name stays in the first screen, the header name is always shown), no fade-in, no list
animation, transitions off. Without script: everything is visible, the header is solid, lists open natively, the phone
menu opens by its link.

## What could not be transferred, and why

- **Picture beside text (part 4).** The reference stands a hard-edged picture in the right half beside the words. Owner's
  rule: never. Here the photograph is the ground of the right 62.5 % of the row, bleeds off three edges and sinks into
  the pale ground toward the words (a veil in the page's own ground over its left 30 %); it is never wider than its
  own pixels (person1's 770 px picture stands 770 wide). On the phone it is a full-width square under the words, as the reference.
- **Black type straight on the picture (part 1).** The reference's portrait is pale enough for black ink. A client's
  picture may be anything, and the data carries no tone, so the first screen gets a veil in the page's ground: 10 % over
  the top fifth, rising to the strength at which the darkest possible pixel still gives 4.7:1 (50 % on white, 54 % on
  local1's grey) from 40 % down, where the line and the name stand. A dark picture therefore reads paler than it is.
- **Accent band ink.** Black on the reference's orange; ours takes whichever of ink and its opposite reads better on
  the client's accent (white on person1's blue, black on local1's green) and deepens the accent if neither reaches 4.7:1.
- **The wordmark** is the reference's drawn logo; ours is the name in type, so its height depends on its length
  (person1 156 px, local1 87 px at 1440; the reference 161).
- **The card's bottom rule** (the reference's "buy now" link draws a rule across the card) is not built; our project
  cards have a title and, when the data has an address, a link.
- **Endless carousels, "The Books" phone row, press logos as pictures, newsletter field** — no data of that kind.

## Image slots (`data-slot`) — the client's own photographs only; `media.made` is never read

| Slot | Takes | person1 | local1 |
|---|---|---|---|
| `hero` | not small, ≥ 1400 wide, wider than tall, not product/detail; one no section names comes first | hero.jpg 1568×900 | staircase-curved.jpg |
| `intro` | a photograph no section names, ≥ 600 wide, not portrait/people/product/detail; not small first | toprope.jpg (770, small → 770 wide) | staircase-down.jpg |
| `person` | the single person's portrait | portrait.jpg (944 → 900 wide) | — (three people → cards) |
| `step` ×n | each `steps.items[].img`, ≥ 600 wide | aravis, powder, ferrata, bionassay | staircase-spiral, kitchen-island, workshop |
| `projects` cards | first unused photograph of each project | — | staircase-white, door-painted, kitchen-timber, bar, oak-frame |
| `team` cards | each person's portrait | — | adam, jake, workshop-machine |
| credentials badge | `credentials[].img`, 95 px, inside its opened line | uiagm.png | — |

Not used: person1 salbit.jpg (376 px), book.jpg (300 px product roundel); local1 seven work/workshop pictures.
With no photographs: every section stands on plain grounds, the rows shrink to their words; checks and the readability
gate pass, coverage 0 % — a typographic page, not this reference (`holds_without_pictures: false`).

## Readings

- Coverage (`tools/coverage.mjs`, 1440): reference 36 % (100, 8, 33, 36, 26, 0; 1 wide screen) · person1 37 %
  (100, 0, 24, 60, 36, 63, 63, 49, 0, 0, 0; 6 wide) · local1 36 % (100, 0, 47, 39, 63, 57, 41, 12, 0, 0; 5 wide).
- `tools/legible.mjs` on the final pages: person1 ok, 0 unreadable of 439 line readings; local1 ok, 0 of 394.
- Also run: person1 on an invented dark palette with invented plans and questions (`probe/synthetic-dark.html`, test
  only) — checks pass, legible ok; `render({})` returns a page.

## Known differences when the pairs are looked at

- 01: our first-screen picture is veiled; person1's own hero photograph has the words "YOU ARE HERE" in the picture itself.
- 02: our band is two to three times as tall (person1: three groups, each with a paragraph; local1: ten lines); person1's ink is white.
- 03: Newsreader italic is lighter and wider than Lyon; four lines where the reference has three (longer sentence, smaller size above 170 characters — chosen).
- 04: the picture's left edge is soft and it reaches 62.5 % instead of a hard half.
- 05: no ruled label and no heading above the project cards (no words for them in the data); landscape photographs are
  cropped hard in the tall 335×417 cells (local1 "The Old Rectory" shows the door's edge, not the door).
- 06: long quotations (over 300 characters, both of person1's) are set at 23 px sentence case, not in 45 px capitals.
- 07: role and biography stand under each portrait (the reference has only a title and a picture); three cards leave the row's right quarter empty.
- 08: lines of type instead of marks. 09: a long links column.
