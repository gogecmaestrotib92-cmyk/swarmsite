# altufanulu — a law office's page: dark photographs, a serif line, ruled columns

Reference: https://altufanulu.com/en — measured 2026-11-12 at 1440 and 390 (home; and the about, practice-areas,
one practice-area and contact pages for the parts the home page lacks). No cookie wall. Measuring scripts are in
`probe/`, their output and the reference shots in `ref/` (`anatomy.json`, `dom-d.txt`, `dom-m.txt`, `dom-inner-*.txt`,
`ref-*` shots, `hover-*` shots, `inner-*` shots, `coverage-ref.txt`).
Test clients: `law1` (primary), `clinic1`. Niche: law.

**The reference's pictures are plainly stock**: a looped city film at dusk behind the first screen, towers seen from
below, a blurred lobby with walking figures, a glass facade, a night skyline. None was taken or imitated. Only the
build is taken; every picture slot takes the client's own photograph or stays a plain ground. What is kept of the
pictures is their *relation* to the page: black-and-white, low-key, text standing on a dark veil.

## Sections of the reference and what each takes
| # | reference (home, top to bottom) | ours | data |
|---|---|---|---|
| 0 | header 130 high (80 on a phone), fixed, clear over the first screen; logo left, six capital 18px links right, a bordered language box. Navy once the page has moved 1 px; slides away going down, returns going up | same. The name is set in the serif (the reference's mark is a logo; a client logo of unknown tone cannot stand on the dark picture, so it is shown in the foot instead). The bordered box holds `cta` | brand.name, nav (7), cta |
| 1 | first screen 1440×900: film filling it; h1 70/77 serif at the foot left (20 from the edge, 80 from the foot, 100 under it); from x=820 a bordered button 60 high and an 18px text | same; the client's widest photograph of a room or of people, black-and-white under a near-black veil. Both hero buttons, text, and the telephone note | hero, one photograph (≥1400 wide, ratio ≥1.2) |
| 2 | "why": 24px capital serif label left, 40/48 serif statement from x=420; three picture cards 453×635, 20 apart: number top right (60px bold, half-white), 30px capital serif title, 16px text on a black foot gradient | same when every step has a photograph: the step's own `img`, else one from the pool. Texts longer than 220 characters stand under the card (the reference's item is a column with a 20 gap). With no photographs: the reference's **values grid** from its about page (ruled cells 700×264, 20px bold name, 18px sentence) | steps |
| 3 | navy band: 38px serif line from x=350; left three numbers under hairlines (60px, 16px label right); right a picture 946×578 **boxed** in the band | the statement and figures. With a photograph: text half and a picture half, **edge to edge and as tall as the band** (the boxed picture converted). Without: the reference's about-page band (label at left, 40px line, 18px text, numbers in columns behind a hairline) | statement, figures, one photograph (≥1000×600) |
| 4 | carousel: 499 panel (label, 50px tight serif line, 50px capital sans line), then ruled columns 336×706 (2.8 in view): 40/40 sans name at the top, 18px text and an arrow at the foot; hover tints the column 10 % navy. 60px bar: two arrow buttons, a link at the right | same. Panel: the block's title as the 50px line and its text as a paragraph (or label + line when the text is ≤60 characters). No link at the right of the bar (no data) | features |
| — | (practice-areas page: nothing at the left, two columns of ruled rows 81 high, 20px names) | **list** on the grey ground: label left, per group a 30px capital serif name and ruled rows — name and note left, price right. Unpriced groups with texts use the practice-area page's barred 20px sub-head and paragraph. A photograph band breaks a long list between groups | catalogue |
| — | (no pricing on the reference) | **plans** as the carousel's ruled columns with the numbers' 60px figure; a marked plan takes the hover tint and the filled button | plans |
| — | (no questions on the reference) | **faq** in the list part: barred 20px question, 18px answer, hairline between | faq |
| — | (about page: "our team" split and picture cards) | **team**: section head, a people photograph as a band, then the picture cards (four across; name in capitals, role; sentence and contacts under the card), then everyone without a portrait in the two-column ruled rows | team |
| — | — | **quotes** as ruled columns (26px serif) | quotes |
| 5 | "sectors": grey ground; label, 50px tight serif line, capital sans line, bordered button; picture 620×780 as tall as the section at the right (20 from the edge) | **reach**: grey ground; the telephone as the 50px serif line, mail, booking/form buttons, social links; bold-name blocks of 20px lines per office (the contact page's part). With a photograph of the door: a full half at the left, edge to edge (the about page mirrors the split the same way) | place, locations, contact, one exterior photograph |
| 6 | closing band 1440×720: night picture; 50px serif line at the foot left, 18px text at the top right, a filled white button at the foot right | same over the client's photograph under a 70 % veil; without one a plain band in the deep colour, 520 high. The button is the one place the client's accent is used | close, one photograph (≥1400 wide) |
| 7 | foot on #f6f6f6: logo 280×119, the h1 again at 50/60, 14px address; right: arrow to the top, two link columns 18px, a badge 100 wide; hairline; legal links | same: the client's logo (or the name), hero.title again, foot.text; links in two columns; credential badge pictures 100 wide; credentials without a picture as 14px lines; foot.links and legal | brand, hero.title, foot, links, credentials |

## Measures used (1440 / 390)
- Side margin 20. Sections 100 top and bottom (60). Grey zone #f4f4f5 on white = ground 4.5 % toward the ink. Hairlines
  #b3b3b3 = 30 % ink. No radius anywhere (2px on the header box). No shadows.
- h1 70/77 (40/44), weight 400. Labels 24px (20) weight 500, capitals, −0.02em. Statement 40/48 (28/33.6) weight 500.
  Panel line 50/55 −0.08em (28/30.8). Column names 40/40 sans 500 (24/24). Card titles 30/40 capitals (20/26).
  Numbers 60px (40). Body 18/25.2, card text 16/22.4. Buttons 60 high, 0 40 padding, 20px/500 (50 high, 16px).
- Cards 453×635 with a 20 gap (phone: a swiped row, card 302×423, 16 gap, the next one showing).
- Carousel: panel 34.65 %, column 35.71 % of the rest (336), 100/60/60 padding, 706 high (phone: 83 % wide, 349 high).
- Closing band 720 high, caption inset 100 (phone 422, inset 20). Foot 100 padding; tagline 97 under the mark.
- A first screen is never taller than 1.1× the photograph's own height (clinic1's banners are 690 high → 759).

## Fonts
- Victor Serif (commercial) → **Newsreader** (Google Fonts, OFL), weights 400/500 with optical size: the nearest open
  text serif with the same light, wide, low-contrast drawing at display sizes.
- Inter is open (OFL) and is used as on the reference.

## Motion — measured and reproduced
| measured on the reference | ours |
|---|---|
| header: `transition: all .4s ease`; transparent at 0; gets class `scrolled` (navy ground) from the first pixels; `translateY(-130px)` while scrolling down, back at 0 on scrolling up | same (navy from 60 px, leaves from 130 px) |
| numbers: each row starts at opacity 0 / 30px lower and comes in as it enters the window; the figures count up (the full-page shot caught 19+/24/11 on the way to 20+/25/12) | same: .7s ease, IntersectionObserver at 88 % of the window; count over 1.4s for plain numbers of up to three digits (a year or a price is not counted) |
| carousel: Swiper, 2.8 columns (1.2 on a phone), 300ms, no loop, no autoplay; column hover `background .3s ease-in-out` to navy 10 % | native scroll-snap row with the same widths; arrows move one column (smooth scroll); same hover |
| buttons `all .4s ease`: bordered → navy fill, cream text; filled white → navy fill, white text and border; foot links → opacity .5 | same |
| phone menu: navy sheet from the top (~0.9s), 26px capital links rising one after another | same: .8s cubic-bezier(.7,0,.2,1), links .6s with 80ms steps; Escape closes |
| first-screen film: 8.1s loop, muted | not reproduced — the client has a photograph, not a film |
| Lenis smooth scrolling (a 300px wheel step eases over ~1s) and its own 4px scrollbar | not reproduced: scrolling is left to the browser |
| headings and pictures: no reveal (all at opacity 1 before scrolling) | none added |
Reduced motion: transitions off, numbers shown at once, no smooth scroll. Without scripts: everything visible, the
carousel is a native scrolling row, the menu button jumps to the foot links.

## What could not be transferred, and why
- The film behind the first screen, and every picture (stock). The clients' own photographs stand instead.
- The logo in the header (a client logo's tone is not known to the template; shown in the foot on the light ground).
- The second and third lines of the carousel panel and of the "sectors" block (a serif phrase and a capital sans
  phrase): the client has one title and one text per block, so there is one 50px line.
- The link at the right of the carousel bar ("All Areas") and the "Sectors" button: no such link in the data.
- The value icons of the about page (its own drawings): cells are type only.
- The map on the contact page: an embedded third-party map; the door photograph takes the half instead.
- The boxed picture in the numbers band → a full half (owner's rule). The "sectors" picture stood 20 from the page edge
  → ours bleeds off it.
- Card veils are heavier than the reference's (it can rely on dark stock pictures; ours hold on a white room): a dark
  corner behind the number and a 90 % foot. Photographs carrying text are also taken down to 80 % brightness.
- Card titles and column names shrink for long words (clinic1: 26px column names against 40) and hyphenate.

## Image slots — the client's own photographs only (no `media.made`)
Picture family: the client's photography, all shown black-and-white (the reference's pages are black-and-white with a
blue cast); credential badges and the logo keep their colours.
| slot | takes | size wanted | law1 | clinic1 |
|---|---|---|---|---|
| first screen | role room, people, work, workshop, action, exterior, landscape…; ≥1400 wide, ≥600 high, ratio ≥1.2 | 1920×1200 | colleagues.jpg (2000×1334) | wartebereich.jpg (2000×690; screen held to 759 high) |
| cards | each step's own `img`, else any non-portrait ≥450×560; all or none | 906×1270 | none → values grid | the three steps' own (2000×690, 1680×580: the middle third of each is shown) |
| people band | role people, ≥1100 wide, ratio ≥1.6 | 2000 wide | firm-group.jpg (1128×376, shown 1440 wide = 1.28× its pixels) | none |
| door half | role exterior or landscape, ≥1000×600 | 1440×1500 | none → type in two columns | eingang.jpg |
| statement half | role room, work, people, detail…, ≥1000×600 | 1440×1200 | none → about-page band | behandlungszimmer-2.jpg |
| closing band | exterior, landscape, room, detail…, ≥1400 wide, ratio ≥1.3 | 1920×1080 | none → plain deep band | hausnummer.jpg |
| band in the list | detail, product, work, room…, ≥1400 wide, ratio ≥1.8; only when the list has ≥2 groups and ≥8 items | 2000×700 | none | blumen.jpg |
| portraits | the person's own, any size ≥300; upright card when ≥640 high, square otherwise | 906×1270 | 10 of 35 (1024²) | 10 of 10 (400², shown 335 square) |
| badges | credentials' own files, 100 wide | — | 3 | none |
A `small` photograph is never used. Photographs left over are not shown (clinic1: treppenhaus, leuchter, bueste,
strassenschild).

## Picture share (tools/coverage.mjs, 1440)
See needs.json `measured` for the readings and which case of the rule applies.

## Checks
See the report / needs.json. Variants tried are in `variants/` (built by `probe/variants.py`).
