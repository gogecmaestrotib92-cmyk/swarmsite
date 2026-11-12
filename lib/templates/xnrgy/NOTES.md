# xnrgy — built from https://xnrgyclub.com (measured 2026-11-12 at 1440×900 and 390×844)

Niche: service (club, gym, studio, salon, workshop). Test clients: `local1` (primary), `hotel1`.
The reference is a normal scrolling page of text and photographs: 6356 px at 1440, 5201 px at 390, eight parts
(opening, two clubs, four ways, event band, reviews, partner marks, closing, foot). Checked first; screenshots in `ref/clean-*`.
A cookie dialog sits over the page for scripted pointers; it was passed with its "reject" button, never by accepting.

## Sections of the reference and what each takes

| Reference part (page) | Ours | Data |
|---|---|---|
| Fixed bar: wordmark, mono links, outline + filled button (home) | `.hd` | `brand.name` or `brand.logo`, `nav` (no "home", 7 at most), `hero.secondary` / `signin` (outline, only with ≤5 links), `cta` |
| Opening: full film 900 high under a 40 % veil, title in two halves (first from the left, second from the right), paragraph in column 4, two buttons under the first half, dark block in column 4 that runs 75 px below the picture (home) | `.hero` | `hero.title` split in two balanced halves, `hero.text` + `text2`, `hero.primary`, `hero.secondary`, `hero.note` (the phone as a link); `media.video`, else one photograph |
| Dark row of four facts, small label over a value in capitals (location page) | `.facts` | `figures` (label = `l`, value = `v`); without figures, `trust` as values |
| Two clubs: small label, 75 px heading, short lead, two picture cards 635×397 with name, one line, buttons (home) | `.cards` | `hero.kicker` (label), `steps.title`, `steps.text`, `trust` as the dotted line when `figures` took the facts row, `steps.items` (img, title, text, cta); `place.spaces` when there are no steps |
| Four ways: quarter-column cards on the grid lines, picture 233 high, label, name, text, underlined link (home) | `.quarters` | `projects` (first unused photograph, title, text, link); catalogue items that have a picture of their own and short text (label = price · state); `place.spaces` not already shown as steps |
| Event band: dark half 773 high with heading and text, photograph filling the other half from 75 px lower to the bottom edge (home, location page) | `.band` | `statement.title`, `statement.text`, one photograph |
| Question rows: centre two columns, 1 px rules, plus sign, group titles in bold mono (FAQ page) | `.rowsec` | `catalogue` (groups → group titles; items → rows with price, state, and — when there is text, `prices[]` or `rows[]` — an opening row), `catalogue.note`; `features.items` when they are not the catalogue's names; `place.events`; `place.menu`; `faq` |
| Trainers: dark ground, heading from column 2, cards with picture, label, name (trainers page) | `.people` | `team.title`, `team.text`, `team.items` / `team.groups[].items` (img, role, name, text, phone, email, link) |
| Membership cards: centred heading, cards 401 wide, the first dark, name, line, price in bold mono, list, full-width button, note (gym page) | `.plans` | `plans` (title, text, items: name, line, price, per, rows, cta, marked; note) |
| Reviews: moving headline 112.5 px, white chip with label and figure, white cards with a 3 px accent top, mark, text, name; a ruled line of small print under them (home) | `.reviews` | moving headline = `brand.name`; chips = `credentials` (t, year); cards = `quotes` (title, q, name, role); small print = `credentials[].text` (+ link) |
| Partner marks: ruled strip, grey marks 113×90 (home) | `.partners` | `logos[{src}]` (neither test client has any) |
| Closing: dark, small picture 200×278 at the top centre, moving headline across its lower part, centred line, two buttons, rule (home) | `.close` | `close.title` (moving headline), `close.text`, `close.cta`, phone as the outline button, one photograph |
| Foot: wordmark, paragraph, underlined phone and mail, two columns of 28.5 px links, an underlined "go" row with an arrow, 10.5 px bottom line (home) | `.ft` | `foot.text` (its phone / mail parts become links), `place.phone`, `email`, `contact.routes`, `nav` + `links` (large links), `place.address` (when not already in the foot line), `place.hours`, `place.social` (as words), `place.booking` / `contact.form` / `cta` (go rows), `locations[]`, `place.notices`, `foot.legal`, `foot.links` |

A part whose data is missing is left out whole. `plans` and `faq` are built from the reference's own membership cards and
question rows; neither test client has plans, so plans were exercised with borrowed data (see Variants).

## Measures used (1440 → 390)

- Page: ground 235,235,235 → `palette.ground`; band colour 15,19,32 → the client's ink mixed 14 % with its accent and taken
  down to near-black; accent 25,43,136 → `palette.accent`, darkened only until 10–12 px words reach 4.6:1 on the ground,
  on white cards and under button words. Side padding 70 (4.86 vw) → 21.
- Grid: three hairlines per section at 23.65 %, 50 %, 76.35 % of the 1300 measure (x = 377, 720, 1062), 0.75 px,
  6 % of the band colour on light, 9 % of the light on dark → one line at 50 % on phones.
- Display: 187.5/1, weight 300, −0.053 em, capitals (title); 75/1 and 52.5/1 weight 400 (headings); 36 (large card
  name); 25.5 (quarter card name, fact); 28.5 (foot links); 112.5/165 weight 300, +2 px (moving headline) → 95 (−0.042 em), 30, 19, 18, 20, 50.
- Mono: 16.5/24.25 body; 16/25.6 opening paragraph; 13.5 card line and band text; 12.75 quarter card text; 12 buttons,
  links (bold, underlined), bar; 10.5 labels and bottom line; 15/24 quotes; 12 bold +0.04 em names → 17, 15, 13, 12, 11.
- Buttons: 37.5 high, 0 15 padding, square, 12 px capitals, 11 px apart → 40 high, 15 px; in cards on phones 42 high, 11 px, full width.
- Opening: picture 900 (100svh), section 975; title top 510, halves 187.5 each; paragraph 308 wide at x 1063, ending
  35 px below the title's top; buttons at 745; block x 1063–1440, y 585–975 → picture 100svh − 150, title at 197,
  buttons 20 under it, paragraph 100 under those, no block.
- Clubs: padding 115 / 43; label to heading 31; lead 450 wide 14 under; cards 60 under, 30 apart, picture 635×397, name
  22 under, line 12 under, buttons 26 under → two-up 168 wide, 12 apart, picture 168×140.
- Four ways: padding 115; cards 59 under the heading; picture 233 high; label 26 under; name 12; text 14; link 16 →
  two-up, picture 120 high, no label.
- Band: dark half 720×773, heading 197 from the top, text 67 under it and 311 wide; picture 720×698 from 75 px down →
  dark block only, padding 50 18, no picture.
- Rows: 685 wide from x 377; row 52 high (9 + 4.5 padding), 1 px rules; plus sign 13 px.
- Reviews: padding 142 / 72; chip 53 under the headline, 54 high, 14 24 padding; cards 48 under, 423×283, 16 apart,
  28 26 padding, 3 px top; rule 28 under, small print 18 under → cards 285×372 in a snapping row, 12 apart.
- Closing: picture 200×278; headline 203 from the top; buttons 22 under the line; 142 to the rule → picture 195×271, headline at 231.
- Foot: padding 125; columns at x 70, 720, 1063; links 54.7 apart; go row 52 high with a bottom rule; bottom line 22.5 padding.

## Font stand-ins

- NeueHelvetica Pro 300/400 (commercial) → **Inter Tight** 300/400 (Google Fonts, OFL): a neo-grotesque of the same
  build, narrow enough in capitals to hold the reference's tight tracking. Its capitals run about 6 % narrower.
- Space Mono 400/700 is itself open (Google Fonts, OFL) and is used as it is.
- The quote mark is the system Georgia bold "“" (the reference draws a heavy double comma).

## Motion measured (`ref/motion.json`, `probe/motion.mjs`) and reproduced

| Measured | Ours (checked with `probe/behaviour.mjs`) |
|---|---|
| Title halves rise 100 px and fade in, the first from 0.7 s, the second 0.35 s later, about 0.6 s each; the paragraph's letters appear at 1.6–1.8 s | CSS keyframes: 100 px rise + fade, 0.6 s, delays 0.7 s and 1.05 s; the paragraph fades as a whole at 1.6 s (not letter by letter). Read: 0/0/0 at 0.3 s, 1/1/1 at 2.4 s |
| Bar: fixed, clear over the opening; after 60 px of scroll it takes the band colour and slides up out of view (0.25 s ease-in-out, 0.2 s delay); scrolling up brings it back 68 px high | Same: `.sc` after 40 px (top −75), `.up` on the way up (68 px, band colour) |
| Moving headlines: CSS animation, linear, 28–30 px/s, not tied to scroll | 28–30 px/s measured (copies and duration are worked out from the length of the words) |
| Event band heading: words rise 34 px and fade in as the band enters | The heading rises 34 px and fades, 0.7 s, once, on entering (as one block) |
| Buttons: a second colour layer behind the words, 0.3 s ease | The other colour wipes in from the left in 0.3 s; words change colour in 0.25 s |
| Bar links: 1 px underline scales in, 0.25 s; text links turn to the accent; foot links 0.3 s | Same |
| Partner marks drift 16 px/s; marks at 70 % and grey | Marks are grey at 70 % and stand still (no test client has marks; a drifting strip was not built) |
| Phone: reviews are a snapping row; the menu is a full dark sheet, 0.25 s fade/slide | Same (scroll-snap x mandatory; sheet with rows ruled 55 px apart; Escape closes; focus moves to the close button) |
| No parallax, nothing pinned besides the bar (sampled at 12 scroll positions) | None |

Reduced motion: no animation or transition; the moving headlines become one wrapped line of the words; the bar stays put.
Scripts off: everything is visible (the reveal is armed only by a class the script sets); the menu button does nothing,
the links are in the foot.

## What was not transferred, and why

- **The small button fixed at the lower left** (appears after 60 px). Built first, then removed: it lay over whatever
  text passed under it — `tools/legible.mjs` caught a quote's name (1.05:1), a plan's note (1.04:1) and a quote line
  (3.35:1) under it on three variants. The bar that returns on the way up carries the same button.
- The messaging bubble at the lower right (a third-party widget), the language switch, the bar's drop-down lists.
- The event poster (a designed graphic with a cut-out player): the half takes a photograph, as the reference's location page does.
- The trainer card's picture strip at the card's left edge (169 px wide beside the text, greyscale): under the owner's
  rule a picture is not boxed beside text, so people take the reference's own picture-above card (the "four ways"
  card) on the trainers' dark ground. This is the one boxed picture converted.
- Stars and scores in the chip and under the reviews: no client states a score; the chip holds a credential and its year.
- Letter-by-letter appearance of the opening paragraph; the drifting partner strip.
- The reference's 40 % black veil: ours is as strong as the client's brightest pixel needs for 4.5:1 under a 16 px
  paragraph (local1 0.77, hotel1 0.65 of the band colour; the headroom covers a grid hairline under a letter), so openings are darker than the reference's already dark film.
- The reference's title is two words; client titles run to twelve. The two halves are kept and the size steps down
  (187.5 → one line each ≥ 104 px → two lines each ≥ 78 px → three); the paragraph widens to columns 3–4 when the
  opening text is over 180 characters.

## Image slots (the client's own photographs; `media.made` is never read)

| Slot (`data-slot`) | Shown | Takes |
|---|---|---|
| `opening` | full width × 100svh, cover, under the veil | `media.video`, else a landscape ≥1600×800 (≥1200×700 accepted), role exterior / landscape / work / room / workshop first; never portrait, people, product, dish; not one a block names |
| `card` | 635×397 (two cards) or 413×258 (three), cover | `steps.items[].img` |
| `tile` | 274–650 × 233, cover | `projects[].photos` (first not yet shown), catalogue item `img` |
| `half` | 720×698, cover, bleeding off the right edge | an unused picture ≥720×698, role workshop / room / detail first; not on phones (as the reference) |
| `portrait` | card width, its own proportion held between 4:5 and 3:2 | `team…img`; a person without one is a card in type |
| `band` | full width × 620, cover | an unused landscape ≥1440×600 — only before a question list of eight or more, or between two long lists (CONTRACT picture share, rule 3) |
| `closing` | 200×278, cover, veiled in its lower third where the headline crosses | an unused picture ≥400×400, role detail / workshop / dish / product first; never portrait or people |

Each photograph is shown once. A `small` picture is never taken for the opening, half, band or closing and is capped at
its own width in cards. No `alt` is used as copy; a slot without copy is not made (hotel1's remaining room pictures have
no words of their own and stay unused).

- local1: 14 of 20 used — opening `staircase-curved`, cards ×3, tiles ×5 (Oake House takes `staircase-white` because
  `kitchen-island` is already a card), half `staircase-down`, portraits ×3, closing `chisel`. Unused: 6.
- hotel1: 7 of 13 used — opening `entrance`, cards ×3, half `room-2`, band `room-detail`, closing `breakfast`. Unused: 6.
- With no photographs: the opening is the band colour, cards and tiles become ruled type, the dark half becomes a full
  dark band with heading left and text right, the closing has no picture. Page of type on two grounds.

## Picture share (`tools/coverage.mjs`)

- Reference: 30 % (per 900 px screen 100, 41, 26, 40, 0, 5, 0, 0), 1 screen with a wide picture (the opening). Height 6356.
- local1: 28 % (100, 8, 43, 46, 18, 29, 2, 5, 0, 0), 1 wide screen. Height 8139 (1.28×) → overall compared: 2 points under.
- hotel1: 30 % (100, 14, 41, 13, 7, 64, 3, 2, 0), 2 wide screens. Height 7439 (1.17×) → overall compared: level.
  Without the band before its thirteen questions it read 23 %.
- The reference's wide pictures — the opening and the half-width photograph of the band — are both in ours, in order.
  Our second screen is lower than the reference's (8–14 against 41) because the facts row and the heading stand
  between the opening and the cards.

## Checks (final build)

- `tools/shots.mjs` — local1: d height 8139, sideways 0, distorted 0, h1 1, errors []; m height 9238, same. hotel1: d 7439, m 7724, same.
- `tools/legible.mjs` — local1 ok (429 readings), hotel1 ok (342).
- `probe/behaviour.mjs` — keyboard focus: 2 px outline in the ink of the ground it stands on, on every link and button
  of the bar and the opening; reduced motion: no animation, moving headlines become one wrapped line, no sideways scroll;
  bar, reveal, headline speed as in the motion table; phone menu opens, moves focus to its close button, closes on Escape.
- One-file copies: `out/local1-one-file.html` 1.1 MB, `out/hotel1-one-file.html` 1.3 MB, nothing left outside.

## Variants (`probe/variants.py` → `variants/`, scratch copies in memory; `probe/check.mjs` + `tools/legible.mjs`)

No sideways scroll, one h1, no script error, no distorted or enlarged picture, no overlapping text box at 1440 and 390 on all of:
1 / 3 / 5 plans (sportbot's two plans repeated, with hotel1's questions and figures added to local1) · 2 and 9 features
(catalogue removed) · 1 and 6 steps (both clients) · a 12-word and a 1-word title · a 40-character button label (both
clients) · no faq · seven people with one without a portrait, one quote · no photographs (both clients).
Legible ok on each. Three of them first FAILED under the fixed lower-left button (local1 1 plan, local1 1 step, hotel1
40-character label); ok after it was removed. After the last two small changes (dimmed labels a step lighter, menu
focus) legible was re-run on local1, hotel1, both no-picture variants and 5 plans only.

Also rendered, outside the assignment, with the other clients' data as they are: clinic1, law1, school1, shop1, person1,
butarque, balamo, automateed, sportbot (dark ground, film in the opening). Two faults found there and fixed in the
rules: a long mail address pushed law1's phone page 61 px sideways (words may now break anywhere), and dimmed labels on
a grid hairline read 3.99–4.46:1 on school1 and sportbot (dimming now leaves room for the hairline). After that: check
clean on all nine; legible ok on clinic1, law1, school1, shop1, person1, sportbot; butarque, balamo and automateed were
not put through legible.

## Not checked

- Real phones and Safari / Firefox (Chrome only, emulated 390×844).
- The drifting behaviour of the reference's partner strip was measured but nothing was built to compare.
- `logos`, `locations[]`, `place.notices`, `place.events`, `place.menu` are written from the contract and render on
  other clients' data without errors, but neither test client has them and they were not compared with a reference part.
- The opening with a film was seen only on sportbot's data.
- Print styles; right-to-left languages.
