# bokman — template for places, rebuilt from bokman.co.uk

Measured 2026-11-12 at 1440×900 and 390×844 on `https://www.bokman.co.uk` (the bare domain did not resolve from this
machine; `www.` did). Files: `ref/anatomy.json`, `ref/ref-*.jpg`, `probe/tree.txt` (box tree with positions, grids,
transitions), `probe/motion.txt` and `probe/motion2.txt` (load sequence, scroll, strip, hover, phone menu),
`probe/pages.txt` (about / contact / journal pages: text modules without a picture, label-and-content rows, the
full-width picture). Test clients: `butarque` (52 photographs, 47 of them `small`) and `balamo` (20, 15 `small`); the
cases of five and of no photographs were built from scratch copies of the data (`probe/five-*.html`, `probe/nopics-*.html`).
*Measured* = a reading from those files. *Choice* = mine, and said so.

## What the reference is
A four-screen home page in ONE colour on white: every letter is the red, one band is the red with white type. Type-led
and compact: a wordmark as wide as half the page, one sentence at 40px, headed paragraphs at 36/18px, a foot of 12px
capitals. Its home page currently carries a closure notice in the text column; the notice's *build* (a 36px heading
over 18px paragraphs with links) is what was taken, not the notice.

## Sections (reference → data)
| # | reference (1440) | what it takes here |
|---|---|---|
| 1 opening, pinned, 100vh | 12 columns, side 24, gutter 24, 20 above/below. Left six: wordmark 684×111 over a picture 684×729. Right six: picture 684×729 over a second wordmark (the name in Korean) with a seal at its right end | left: **h1 = `brand.name`**, set in capitals and broken into the lines that fill the column at the largest size (see "Fitting"), over a photograph. Right: a photograph over the second line = `hero.title` when it does not repeat the name, else `hero.kicker`; `brand.logo` in the seal's place. With fewer than two photographs large enough, the opening is the two lines side by side and nothing is pinned (this is the reference's own state at the end of its scroll) |
| 2 header, sticky | 72 high, wordmark 32 high left, links 14px capitals 42 apart, outlined pill (26 high, radius 24, tracking .143em) | `brand.name`, `nav`, pill = `place.booking` (else `cta`) |
| 3 band in the one colour | sentence 40/42 in the ground colour, padding 90 / 24 / 32; a strip of photographs 480 high (3:4 = 360 wide, 4:3 = 640 wide), 24 apart, drifting left; 120 below | sentence = `hero.text`; strip = up to eight photographs chosen by size, role and shape |
| 4 picture + text | picture 684×912 in the left six columns (24 from the page edge), text in the right six, centred against it: headed blocks (h 36px, p 18/22, 22 between paragraphs) | **kept as the reference has it, with the picture run to the page edge** (owner's ruling 2026-11-12: a photograph from the edge and as tall as its section beside a column of text is right; only a boxed picture is not). The photograph is the left half, from x = 0 to the middle gutter (708 wide at 1440), as tall as the module (at least 912 at 1440, i.e. 63.33vw; never taller than its own pixels). Right six columns, in this order: `statement` · each `place.events` · contact block (`place.hours`, `phone`, `email`, `address`, links to booking and takeaway, and to the menu when it has no sections) · rooms (`steps.title` + `place.spaces` or `steps.items` as label / text rows) · menu (`place.menu.sections` and `lists` as label / line rows, count or price at the right, link to `place.menu.h`) · `plans` · `faq` as the same rows. On the phone the text comes first and the picture after it at 3:4, as measured. **Fallback when no photograph fills the half at its own pixels** (not `small`, ≥ 950 wide, ≥ 912 high, and two large ones still left for the opening): the rows take the left six columns, the text the right six, and a full-width picture (the reference's about-page module, 1392×783) stands above them if the client has a landscape ≥ 1200 wide |
| 4b closing picture | — (home page has none; the about page closes modules with full-width pictures) | one landscape ≥ 1200 wide, when the client has one, closes the page before the foot (a second one in the fallback case). *Choice*, kept only because the share of picture needs it — see "Picture share" |
| 5 foot | one row on the 12 columns: three links (2 columns each), a 20px seal in column 7, two links, © at the right; 12/16 capitals | `foot.links` + `place.social` (same address once), `brand.logo`, `foot.legal`; then `place.notices` (image at no more than 330px, then its text) |

Labels the template adds are all from the data: the contact block's heading is the label of the nav/link entry whose
address contains "contact", else `place.address.name`, else the name; the menu's heading and link are the labels of the
entries that point at `place.menu.h`; the row label of counted menu sections is `features.title`.
Not used: see `needs.json` → `drops`. No `alt` is ever set as copy.

## Measures used (px at 1440 / at 390)
side 24 / 16 · gutter 24 / 16 · opening padding 20, gap 20 · header 72 / 100 (name on a line, a 90×16 three-rule
trigger centred under it) · band text 40/42 / 25/30, padding 90 24 32 / 16 16 32, 120 / 20 below the strip · strip 480 /
320 high, 24 / 16 apart · between modules 96 / 48, same below the last · headings 36 / 32, text 18/22 / 16/18 · rows:
label 2 of 6 columns, content 4 (*the reference's label is 1 of 6; its labels are one word, the clients' are three*) ·
foot 12/16 capitals, row 32 high / a 3-column grid of 33px cells ruled at 1px · phone menu rows 24/24 capitals with 16
padding and a 2px rule, small rows 16/18.
The phone build starts at 767 as in the reference. The *header* alone turns to its phone form (name line, trigger,
full-screen list) as soon as its row no longer fits: the width is computed from the name and the nav labels (butarque
below 1440, balamo below 1096). The reference never needs this with four one-word links.

**Fitting (choice, needed because the names are longer than six letters).** Advance widths of Arimo Bold capitals are in
`render.py`. A line is broken into at most three lines; the fewest lines that reach 60% of the reference's size (its
capitals are 111px high ≈ 155px type) are taken, else the break that gives the largest size; the block is never taller
than 236px at 1440. butarque: three lines at 90px; balamo: two lines at 92px. The picture under or over it takes the
rest of the column, so it is 603–734px high instead of 729.

## Typeface
Reference: Neue Haas Grotesk Text (commercial) for everything, and a drawn wordmark. Here: **Arimo** 400/700 (Google
Fonts, Apache 2.0) — the open face of the same kind and the same widths; the wordmark slots are Arimo Bold capitals at
−.01em. The Korean wordmark and the toad seal have no counterpart: the second line of type and the client's own logo
stand in those places, nothing was drawn.

## Colour
The reference's relation is kept exactly: one colour for all type and for the band, the ground for the type on the
band. The colour is `palette.accent` moved along its own hue until it reads at 4.9:1 on the ground (butarque `#83b735`
→ about `#577923`; balamo `#61a229` → about `#4b7d20`) — the true accent fails on white as text and under white text.
The hover colour of text links (reference: a blue) is the first chromatic `palette.extra` made readable the same way,
else the ink.

## Motion
Measured on the reference:
- load: a full-screen curtain of the one colour leaves to the left in about .9s (ease in-out) while the two wordmarks
  slide in from above and below; then the two pictures come in whole, the left from below and the right from above, in
  about .6s (ease out), done at about 1.8s;
- the opening is pinned and the page rides over it; over one screen of scroll, eased cubic-out (229px of 769 after
  100px, 673 after 450): the left picture leaves downward, the right upward, the second wordmark rises to the top row
  beside the first. On the phone the two half-screen pictures close toward the line between them instead;
- the header sticks at the top once reached;
- the strip drifts left at about 33px/s, wraps, and can be dragged (cursor grab);
- hover: links to .8 opacity in .3s; nav labels roll up 24px in .3s to a second label (the Korean word); text links
  turn to the second colour;
- phone menu: a panel of the one colour drops from the top in .5s `cubic-bezier(.65,0,.35,1)`; its rows rise 30px
  from behind their rule, 1s each, .2s apart.

Reproduced: all of the above. The nav label rolls to a second copy of itself (there is no second-language label in
the data). The strip loops only when one round of pictures is wider than the screen plus its widest picture, so that
no picture is ever on screen twice; otherwise it is a still row that can be pushed sideways. A press state (opacity
.6) is added. The load sequence runs once and only with scripts (`html.js`); without scripts everything is in place
and the phone menu is a plain list under the header. With reduced motion: no load sequence, no scroll-linked moves,
no drift (the strip scrolls by hand), no transitions.
Not reproduced: the word "Loading..." in the curtain; smoothed scrolling (none measured).

## Image slots — all `media.photos`, each photograph once, chosen by role, size and shape (never looped)
- opening left: the first photograph that is not `small` and at least 680×700 with role `dish` (else `other`, else the
  first large one) — the reference shows dishes there. Opening right: the most upright large photograph of another role.
  butarque: salmon.jpg · barra-2400.jpg. balamo: maridaje-copa.jpg · gran-reserva-barrica.jpg.
- the half beside the text: a photograph that is not `small`, ≥ 950 wide and ≥ 912 high; the building, then a room, then
  the bar first, the most upright of them. butarque: terraza-mesas-altas.jpg (1800×2400). balamo:
  gran-reserva-pasillo.jpg (1242×1152). It is chosen before the opening pair, but only when two large photographs
  are then still left for the opening.
- closing band (one; two bands in the fallback case): landscapes ≥ 1200 wide, rooms/exterior/bar first, cropped to no
  wider than 16:9 and no squarer than 3:2, shown at no more than their own pixels (balamo's is 1242 wide in a 1392
  slot); 3:4 on the phone. butarque: salon-1900.jpg. balamo: gran-reserva-reservado.jpg.
- strip (up to eight): photographs at least 480 high, a second shot of the same thing left out (same file stem), taken
  in turn from each role and spread evenly through a role's list; shapes held to the reference's 3:4…4:3. A `small`
  picture is 480 high at most 640 wide here, always within its own pixels. When fewer than four are tall enough, all
  that is left is shown at its own shape and at the height of the lowest (five-photograph case: 315px).
- foot: `brand.logo` at 20px; notices' images.
No made pictures. No picture stands in a box beside text: the one beside text is a full half from the page edge. `place.spaces[].img` is not tied to its row.

## Picture share (`tools/coverage.mjs`)
reference 57 at 1440 (per screen 81 55 44 20) and 58 at 390; it has no full-width picture on its home page, and its
half beside the text is in place in ours. Our pages are 4.3–4.5k px against the reference's 2.9k (under 1.5×), so the
overall share is compared: butarque 62 and 55; balamo 55 and 57.
Without the closing band the restored half alone gave butarque 55 / 49 and balamo 49 / 52 — three of four readings more
than 5 below the reference, because our page carries the menu and the notices under the same pictures. That is why one
closing band was kept; with it removed the template would fail the gate at 390 for butarque and at both widths for balamo.

## What could not be transferred
- The picture beside the text is 24px wider than the reference's (it runs to the page edge) and grows with the text
  beside it; with a long menu the text is longer than 912 and the picture follows it up to its own pixel height.
- The second-script wordmark and the seal (the client has neither).
- The nav roll to a translation.
- The menu: the reference shows no menu at present (closed); the rows are its about-page "label + lines" build.

## With few or no photographs
- none: holds as a type-led page (two lines of large type, header, band with the sentence, two text columns, foot);
  every gate passes; the name stands twice at the top (large, then in the header) — plain, honest, not rich.
- five (the first five of butarque: three large, two small): the upright bar photograph takes the half, the dish and the
  wide room the opening, the two small ones a still strip at 315px that does not fill the row.
- to be offered as a picture page: see `needs.json`.

## Variants tried (CONTRACT "A template holds for clients it has not seen")
Scratch copies of butarque in `probe/var-*.html`: 1, 3 and 5 plans (with four questions); 2 and 9 menu categories /
features; 1 and 6 rooms; a 12-word name with a 12-word title; a 44-character booking label; no faq; no photographs
(with plans and faq); and `sportbot` as it is (a dark software client with two real plans and four questions).
`probe/var.mjs` checks each at 1440, 1024 and 390 for sideways scroll, text boxes running out of the page and text
boxes overlapping; `tools/legible.mjs` was run on each. One defect was found and fixed: a long price string
("$18.99 a month · $0.63 a day") was kept on one line and pushed the page 49px wide at 390 — prices now wrap.
Results are in `probe/final.txt`.


## Engine import fixes (2026-11-12, stress: plans 1/3/5, features 2/9, steps 1/6, 12-word h1, 40-char button, no faq, no photographs; clients casaolmo and larchwick; 1440 and 390)
- The second text column was built with `%` formatting applied to an f-string that already held client text: any `%` in the client's words raised TypeError. It is now plain concatenation; client text is never %-formatted. (Searched every research template for an f-string or client text under `%` or `.format`: no other case.)
