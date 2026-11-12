# chambres — template for places, rebuilt from chambresdamis.be (measured 2026-11-12, 1440 and 390)

Run: `python3 -I build.py chambres butarque|balamo`. The live page is a full home page (7112 px at 1440, eight sections), not a
pre-opening page. Measurements: `ref/anatomy.json`, `probe/tree-d.txt`, `probe/tree-m.txt` (every box), `probe/motion.json`
(rules, scroll samples, hover, panel), `probe/more.json` (section rules; the reference's menu, private-dining and practical pages),
`probe/glyphs.json` (cap widths of the wordmark face). Reference screens: `ref/ref-*.jpg`, `probe/s-d-*.jpg`, `probe/s-m-*.jpg`
(notice closed), `probe/menu-d.jpg`, `probe/page-*.jpg`.

## Sections of the reference, in order, and the data each takes
| # | reference (measured at 1440) | data | butarque | balamo |
|---|---|---|---|---|
| 0 | fixed layer one screen high, pointer-events none: first word of the name top left across the left column (824×128 drawing), three caps links 14 px + three-line toggle right-aligned under it, last word bottom right across the right column (472×128). It never moves or hides; ink only | `brand.name` split in two, set in type · `nav[0:2]` + booking · toggle | RESTAURANTE / BUTARQUE top, IN&OUT bottom, 7.66 vw | BÁLAMO top, RESTAURANTE bottom, 4.39 vw |
| 0b | panel: the right column (62.2 %→100 %), ground at 50 % + 20 px blur, 0.6 s; list 30 px serif caps, 59 px rows; socials at the foot; languages | `nav` + `links` not in nav + booking · `place.social` | 6 links | 6 links + 4 socials |
| 0c | notice over the first screen: 672 wide, ground at 70 % + blur, shadow, radius 3, h3 28 px caps with 80 px under it, text ≤ 400, links right | `place.events[0]`: what · when, price, where · cta | none | Thursday pairing dinner |
| 1 | opening: grid 62.2 % / 37.8 %; left picture 3:4, at least one screen and at most 1.5 screens high; right picture one screen minus the block of the last word (13.7 vw), so that word stands on the ground | two photographs | barra-2400, salmon | gran-reserva-pasillo, gran-reserva-reservado |
| 2 | line: block ≥ 80 % of the screen, content on its floor; h1 34 px serif caps in two lines, the second italic; one underlined serif link 20 px with » | `hero.title` + `hero.kicker` (italic line) · `hero.primary` / booking | yes | yes |
| 3 | pair: left 3:4 (896×1194), right 3:4 (544×726) standing on the left one's foot | two photographs | terraza-mesas-altas, gintonic | maridaje-copa-2, sala-principal |
| 4 | text: 20 % of a screen above; one column 347 wide starting at half the left column (x 448); h2 34 px caps, 14/21 sans paragraphs, two links | `statement.title` · `hero.text`, `hero.text2`, `statement.text`, `hero.note` · `hero.secondary`, `place.takeaway` | yes | yes |
| 5 | right picture 3:4 pulled up by 30 % of its column, beside the text | one photograph | postre-ferrero-rocher-gold | salon-jardin-vertical |
| 6 | left picture 3:4 pulled up by 20 % of its column | one large photograph (a room from `place.spaces` first) | salon-1900 | gran-reserva-barrica |
| + | menu (the reference's own menu page): h1 34 px, section names italic serif 28 px 90 px apart, one line per dish 14/21 with the price in italics | `place.menu`: lists and sections without dishes as linked lines, sections with dishes as name + price; heading = the nav/link label that leads to the menu; 1–2 dishes in the right column beside it | 14 lines + Postres (5 dishes, "Iva incluido" once), 2 desserts beside | left out (no menu data; the link stands in block 4's nav) |
| 7 | right picture 4:3 (544×408) | one photograph | postre-el-aguacate | pulpo |
| 8 | text across the left column, pulled up 7 %: h2 across, paragraphs in two columns (5 % gap), names in medium weight, two links | `steps.title`, `steps.text`, each item: **title** *k / cta* + text · two `links` not shown elsewhere (else `close.cta`) | three rooms + Grupos, Eventos | three entries + Bálamo eventos |
| + | plans, questions (reference: practical page — rows with an italic serif 24 px question, answer ≤ 600) | `plans` as block 8's two-column text · `faq` as `<details>` rows | none in data | none in data |
| + | legal notices | `place.notices`: picture ≤ 270 px + text, two columns, above the foot | none | FEDER |
| 9 | foot: one screen high, three small columns on its floor in the left column (caps address with the street in italics · underlined caps links · hours, 10 px grey credit); the fixed name stands over it | name, `place.address`, `phone`, `email` · `place.social`, `foot.links` · `place.hours`, booking, `foot.legal` | yes | yes (no hours in data) |

Not placed: see `needs.json` "drops".

## Measures used (1440 → 390; nearly everything is a share of the width, as in the reference)
Columns 62.2 % / 37.8 %, page inset 2.5 vw (36 → 10). Ground and ink only; no accent, no rules, no radii except the notice (3 px).
h1/h2 34/1.3, −0.05 em, caps → 24. Body 14/1.5, medium 500 for names. Link-buttons 20 px serif, 1 px underline 0.8 rem below, list rows 250 %
line-height 20 px apart. Nav 14 px caps, 30 px apart; toggle 33×13, three 1 px lines. Panel list 30/1.3 caps −0.05 em, 20 px under each.
Line block min 80 dvh (phone 60 vh), padding 2.5 % / 5 % (phone 10 %). Text block 20 dvh above; `.single` 50 % of the left column with 22.5 % right
padding; `.double` 4 % padding, 12.5 % right padding, 2 columns. Pull-ups −30 %, −20 %, −7 %. Foot 2.5 % padding, 100 dvh, 3 columns 2.5 % apart
(phone: stacked, 100 px under them for the last word). ≤ 1300: text block full column, ≤ 500 wide; ≤ 1000: one text column, foot stacked;
≤ 800: one column, every picture full width (3:4 = 390×520, last 4:3), nav links hidden, toggle top right, panel full screen.
Wordmark: one size for both parts — the largest at which every line fits its column less the insets (cap widths measured, ×0.97), at most 12 vw;
the first part may take two lines.

## Typefaces
Wordmark: a custom drawing (Didone capitals) → **Bodoni Moda** 500, optical size 36 (OFL). Headings, links: `old-standard` on Typekit = **Old Standard TT**
(OFL), the same design. Text: Helvetica Neue LT Pro (commercial) → **Arimo** (Apache 2.0, Helvetica's metrics). Bodoni Moda's hairlines are thinner and its
capitals wider than the reference's drawing; the reference's italic "d'" and slanted "A" are its logo and were not imitated.

## Motion: measured → reproduced
- Arrival (`.reveal`): opacity 0, blur 5 px, 28 px down → in place, 1 s (opacity, filter, transform; default ease), once, when it enters → same, on pictures, text blocks and links. The opening pictures are not animated (a transform would unpin their veil).
- Fixed name and nav: sampled every 150 px down the whole page at both widths — same box, opacity 1, no class change, no blend mode; scrolling up changes nothing → fixed, same.
- Links: nav underline from 0/transparent to 1 px ink, offset 0.1 → 0.3 rem, 0.6 s; link-buttons offset 0.8 → 0.6 rem in 0.3 s; panel links offset → 0.5 rem → same.
- Toggle: outer lines turn ±25° to the middle, middle line fades, 0.6 s → same. Panel: opacity + ground 0 → 50 % + blur 0 → 20 px, 0.6 s → same (ground held stronger, see below).
- Notice: closes by opacity → 0 with a 20 px blur, 0.6 s, then is remembered → same (sessionStorage; Escape and a click outside also close it).
- Nothing is pinned, nothing moves at a different speed from the page, no smooth-scroll library → none.
- Not reproduced: view-transition names between the reference's pages (one page here); its lazy-load fade of each image (0.5 s).
Reduced motion: no transitions, everything in place. Without scripts: everything visible; the notice stays closed; the toggle does nothing (the nav row and the foot carry the links).

## Where it leaves the reference, and why
- **The fixed name is not left over everything.** In the reference the black name and nav lie over every photograph; over its dark ones they cannot be read
  (`probe/s-d-02.jpg`: the nav row is invisible). Owner's rule: every letter readable. Here (a) on the opening pictures a veil of the ground colour stays with the
  name (a fixed-attachment gradient: full strength down to the nav row, gone 9 vw below; on a phone also behind the last word at the bottom), strength computed
  from the client's ink for 5.2:1 on the worst pixel (butarque 66 %, balamo 50 %); (b) after the opening, a photograph or text block passing under a part of
  the name makes that part step back (opacity, 0.6 s — the reference's own time) and it returns on bare ground; pictures and text blocks are also stacked above
  it, so without scripts they simply cover it. The toggle stays throughout, its hairlines ringed with the ground so it shows on any picture.
  On iOS Safari a fixed-attachment background scrolls with its box: the veil then covers only the top of the opening picture (not tested on a device).
- Panel and notice grounds are 12 points stronger than the veil (reference 50 % / 70 %) so 14 px text reads over a dark picture.
- A frame keeps the slot's proportion unless the photograph is too low for it: then the frame is as high as the picture allows (salon-1900 is 896×800,
  not 896×1194; balamo's small pictures are near-square). A `small` photograph is never wider than its pixels (max-width), and is not used in the left column.
- Menu, plans, questions and notices are not on the reference's home page; they are built from its menu and practical pages (parts above). The dishes
  beside the menu list repeat the reference's step of a right-column picture beside a text column; they were added after the picture share fell to 40 %.
- The reference's 10 px credit is #aaa (2.3:1); `foot.legal` is set in a grey held at 4.6:1.
- Language switch, newsletter link: no data. Visible words "nav"/"close" do not exist; aria-labels come from a small list by `lang`.
- `brand.logo` is not used: the template's opening is the name in type.
- Text beside a picture: blocks 4/5 and the menu stand in the left column with a photograph in the right one, as measured. The pictures are whole columns
  bleeding to the page edge, not boxes; say if that still falls under "no picture beside text".

## Image slots (no `media.made`; the client's photographs only)
Left column, large only (not `small`, short side ≥ 700), tallest first: opening (room/bar/exterior preferred) · pair · step (a large picture from `place.spaces` first).
Right column: opening (a large dish, else any large picture, else a dish ≥ 560 wide) · pair (people/other/bar) · step (room/exterior) · last, 4:3 (dish) · 1–2 dishes beside
the menu. One subject is not shown twice (`copa` / `copa-2`, `pulpo` / `pulpo-perejil` count as one) unless nothing else is left. A missing picture leaves its
column empty; a section with neither picture is left out. No gradient or colour stands in for a photograph.
Minimum to offer: 7 photographs — 3 large for the left column (one upright or near square), 4 at least 560 wide for the right. With none the page is type on a bare ground (`probe/syn-nophoto-*.jpg`): readable, not this reference.

## Picture share (`tools/coverage.mjs`, 1440)
reference 46 % · per screen 93 21 69 47 51 63 21 0 · 4 screens with a wide picture
butarque 45 % · 93 21 69 52 63 38 38 10 0 · 4      balamo 44 % · 95 18 67 47 65 27 3 0 · 4

## Checked
`tools/shots.mjs` both clients, both widths: sideways 0, distorted 0, h1 1, errors []. `tools/legible.mjs`: ok for both (184 and 117 line readings).
`probe/check.mjs`: focus ring 2 px solid on every stop (name, nav, toggle, links), Escape closes notice and panel, panel 544 wide (390 on a phone),
reduced motion leaves nothing hidden, 12 of 12 arrivals complete, where the name shows and steps back down the page (`probe/check-*.json`).
Not checked: a real phone or Safari (fixed-attachment veil, backdrop blur); widths between 390 and 1440 other than by the rules; a dark palette
(the veil and ink logic handle it in code, no dark client was rendered); printing.
