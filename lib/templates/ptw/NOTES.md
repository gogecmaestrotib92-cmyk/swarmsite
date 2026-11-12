# ptw — a law firm's page: dense, practical, a name across the window

Reference: https://ptwlaw.com.au — measured 2026-11-12 at 1440 and 390 (home, and the people and contact pages for the
parts the home page lacks). Optional cookies declined, never accepted. Measuring scripts and their output are in `ref/`
(`anatomy.json`, `measure.json`, `motion.json`, `motion2.json`, `inner.json`, `clean-*` shots, `hover-*` shots).
Test clients: `law1` (primary), `clinic1`. Niche: law (also holds for a clinic).

The reference's pictures are pen drawings (a film of the building being drawn, a drawn stair hall, drawn certificates).
None was taken or imitated. Where it has a drawing the client's own photograph stands, or the slot stays plain.

## Sections of the reference and what each takes
| # | reference (home, top to bottom) | ours | data |
|---|---|---|---|
| 0 | header, 88 high, held at the top: 5 links left, 3 right, 20px light sans; a search sign | same; the last two `nav` items and `cta` go right; no search | nav, cta |
| 1 | first screen: the drawing alone (1354×728, contained), no heading; the firm's name as a wordmark across the foot of the window | the client's photograph alone in the same box; the name set in capitals across the width | media.photos (one, by role), brand.name |
| 2 | wordmark bar, 84 high, sticks under the header for the whole main part | same | brand.name |
| 3 | "services overview": 30px tracked capitals label; two columns of 52px serif names, some with a bulleted sub-list (30px); a sentence under a name comes up on hover | same | features (name + sentence), or an unpriced catalogue (group = name, items = sub-list) |
| 4 | text block A: 52px heading and 15.2px text in the left five columns, a drawing in the right six, a 26px line under it | the page's h1, text, the two buttons, the telephone in the 26px line. Right half plain | hero |
| — | (no price part on the reference) | fee list: block-B head, then per group a title at the left and ruled rows at the right (name 26px, note in 10px capitals, price 26px) | catalogue with prices; `plans` in the same part |
| 5 | text block A again (it repeats on the people page) | the firm's own words, under a photograph band when one is left | statement |
| 6 | text block B: heading across, a long text column with bold sub-heads, right half empty | values as sub-heads; or one block-A per step when the steps carry pictures (each under its band); an unpriced catalogue's item texts in two columns by group; `faq` in the same part | steps, catalogue item texts, faq |
| — | people page: heading, three-column grid of small upright portraits (89×118) with name/role/contacts in 12px tracked capitals | same grid under a people band; people without a portrait in a four-column type-only grid | team |
| 7 | call block: heading, two lines, one button | same | close |
| 8 | quotations on a brighter ground: typewriter face, centred, one at a time, a button for the next | same (no label: the client gives none) | quotes |
| 9 | floating button at the foot of the window from the second screen to the end of the main part | same | cta |
| 10 | tinted band: a 52px line and a link in the accent with an arrow | the client's call line and the telephone | hero.text2 or booking/cta, phone |
| — | contact page: details at the left; a tinted panel running to the right edge with the contact list | name (or the client's logo as a letterhead), telephone 52px, mail, routes, the form/booking button; panel with every office (address, phone, mail, hours, note) | contact, place, locations |
| 11 | row of article cards (picture 4:3, 26px title, 10px meta), round arrows | what the client can prove, badge pictures first | credentials |
| 12 | dark band: wordmark, newsletter sign-up, contact lines, link columns, all 10px tracked capitals | wordmark, contact lines, the firm's formal name, three link columns, legal text. No sign-up | brand, place/contact, hero.kicker, links, foot |

Not built: the cookie bar, the newsletter pop-up, the search drawer, the mega-menu that opens under a nav word (it shows
sub-pages and articles the data does not hold), the newsletter field in the foot.

## Measures used (1440 / 390)
- Margins 3vw (43px) / 12px. Twelve columns, gap 2vw (28.8px). Text column = 5 columns (547px); the right part starts at column 7 (x 734).
- Section padding 116.48 / 64. Tinted band and card row 49.92 / 48.
- Header 88 / 64. Wordmark bar 84 (mark 51 high) / 34 (18). First-screen box = window − header − bar.
- Label 30/33, tracking 3px, capitals (same on the phone). Service names 52/52, row pitch 90 / 30px, pitch 50. Sub-list 30 / 20, indent 25.
- Headings 52/52 / 30/30. Body 15.2/18.24 / 14/16.8. Heading → text 33. 26px line 67 below the text / 22px.
- Buttons 49 high, 1px line, side padding 16.64, 16px light sans, square.
- Quotation 18/23.4 / 14/18.2, at most 880 wide; name 49 below; button 54 below.
- People: portrait 89×118 / 103×135, text 45 / 25 to its right, 12/13.2 tracked 1.2px capitals.
- Cards 263.5 wide, gap 48 / 282, gap 50; title 26 / 22; meta 10px, tracking 1px; arrows 33px circles.
- Foot: 10/11 tracked 1px capitals; wordmark 88 from the band's top.
- Phone menu: full dark panel, links 14px tracked 1.4px capitals, 47 apart from y 104; telephone and mail below.

## Font stand-ins (all open licence, Google Fonts)
- Kepler Std Condensed Display 500 → **Instrument Serif** 400 (a condensed display serif; one weight only, so ours is a little lighter and a little wider).
- Nimbus Roman (body) → **Tinos**. Nimbus Sans 300 (nav, labels, buttons) → **Inter** 200/300/400.
- Typewriter BasiX (quotations) → **Courier Prime**.
- The reference's wordmark is its drawn logo in inscriptional capitals; the client's name is set in **Cinzel**.

## Colour
The client's palette goes in. Kept from the reference: one quiet ground; a second ground under the quotations; a pale
tint of the accent for the band and the contact panel; the dark band and phone menu in the ink; the accent as large
type only. Two forced departures: a white client ground cannot go brighter under the quotations, so that zone goes 5 %
toward the ink; a pale accent is deepened in its own hue to 3.2:1 before it is used as type (law1's yellow → dark gold;
on the dark band the accent itself is used).

## Motion: measured → reproduced
| measured on the reference | ours |
|---|---|
| wordmark bar: `position: sticky; top: 88px` (64 on the phone) from the first screen to the end of the main part | same |
| page ground changes under the quotations (grey → white at scroll 4600, back at 5800), `0.35s cubic-bezier(.19,1,.22,1)`; header and bar change with it | same curve and time; switch when the zone's top passes 80 % of the window |
| nav words turn white when the dark band is under the header | same (our dark band is shorter than a window, so on the test pages it does not reach the header at the page's end) |
| service rows enter once, each on its own: opacity 0→1, translateX −40→0, about 0.5 s | same, IntersectionObserver |
| service row hover: name to the accent in 0.35 s; sentence opacity 0→1 and translateY −30→−7 in 0.35 s, same curve | same; on touch devices the sentence is always shown (the reference hides it there — a client's sentence would never be seen) |
| button words typed in when the button enters: first letter after ~250 ms, then ~60 ms a letter (10 letters complete at ~760 ms) | same |
| quotation: words come up one after another, each `1.2s` on the same curve; "next" swaps the quotation | same, 45 ms between words (the gap between words was read from one sample, not timed precisely) |
| floating call: absent on the first screen, then held 33px above the window's foot, its ground following the page ground; leaves with the main part | same; shown after 0.6 of a window |
| card row: one card (311.5px) a step, `transform 0.3s ease` | native scroll-snap row, smooth step of one card; arrows only when the row overflows |
| tinted band link: underline on hover | same |
| first screen: a 12.6 s film of the drawing being made, played once | not reproduced — a still photograph |
| drawing in block A: the coloured drawing fades in over the line drawing on hover | not reproduced (no drawing) |
| mega-menu panel sliding under a nav word, `0.8s` same curve; newsletter pop-up `0.8s` | not built |
Button hover and press: no change of computed style was measured on the reference's buttons; ours have none either.
Reduced motion: every transition off, rows and letters shown at once. Without scripts: everything is visible, all
quotations stand one under another, the phone menu still opens (`details`).

## What could not be transferred, and why
- The drawing film and drawings: the reference's own pictures; a small firm has photographs. The first screen keeps the
  build (picture alone, name under it) with a photograph.
- Picture beside text (block A): the owner's rule forbids a boxed picture beside text. The photograph becomes a band
  across all columns above its heading (ratio held between 2.2:1 and 3.4:1; 1.3–2:1 on the phone); where no photograph
  is left the right half is plain, as in the reference's block B.
- Logo: the reference's name bar is its logo. A client's logo image cannot be stretched across the window, so the name
  is typeset there and the logo stands as a letterhead over the contact details (clinic1). On the dark band a dark logo
  would not read, so the foot uses the typeset name.
- The footer's full-window height and its sign-up: no data for a newsletter; our dark band is as tall as its content.
- Labels the client gives no words for ("Client testimonials", "Recent articles", "Contact details") are left out.
  Interface words that had to exist — "Next" for the quotation button, "Menu", "Skip to content" — come from a small
  table in `en` and `de`; any other language gets signs only.
- The people grid is three columns across twelve (the reference: three across nine, the right quarter kept for its
  pop-up), and each person also shows the sentence, telephone and mail the client gives.
- Tablet widths were not measured on the reference; ours switches to the phone build below 1000px and to the menu
  button below 1100px.

## Picture slots
| slot | takes | law1 | clinic1 |
|---|---|---|---|
| hero | first usable photograph by role (people, room, work, workshop, action, exterior, …), not small, ≥1000 wide; cover in the 1354×728 box, or its own ratio if wider than the box | colleagues.jpg | wartebereich.jpg (2.9:1, stands at its own ratio with ground above and below) |
| team band | role `people` | firm-group.jpg (1128 wide, shown at most 1.2× its pixels) | — |
| door band (contact) | role `exterior` | — | eingang.jpg |
| about band (statement) | any left that is not a detail, else a detail | — (plain) | behandlungszimmer-2.jpg |
| step bands | the step's own `img` | — | behandlungszimmer, behandlungseinheit, stofftiere |
| portraits | each person's own | 10 of 35 (25 in type) | 10 of 10 |
| card pictures | the credential's own badge file | 3 | — |
| letterhead | brand.logo | — | logo.png |
Each photograph once; never looped; five of clinic1's banners and its small street-sign picture are not used.
No `media.made` picture is used anywhere.

## Picture share (tools/coverage.mjs)
Reference 16 (per screen 86,0,5,22,0,0,10,12,0; one screen with a wide picture). law1 12 (76,0,0,0,0,50,0,0,0,0,10,0;
two wide). clinic1 25 (50,0,40,50,29,44,38,0,0,0,46,6,0; five wide). law1 is 4 points under the reference: it has two
photographs that are not portraits.

## Checks
shots.mjs, both clients, 1440 and 390: no sideways scroll, no distorted media, one h1, errors []. legible.mjs: ok for
both (law1 912 line readings, clinic1 497) and for both with pictures removed. Keyboard focus: 2px outline on every
link and button. See needs.json for the renders without pictures.

## Ink checked against the size it is set at (2026-11-12, engine stress)
The accent is deepened only to 3.2:1, which holds for type from 24 px. The wordmark is sized to the width, so a long
name sets under 24 px (on the phone "Fernhollow Physiotherapy" is 19 px and read 3.2:1). `_wordmark` now works out the
smallest size the name takes in each build (desktop from 1000 px, phone from 320 px) and, where that is under 24 px,
gives the wordmark the 4.6:1 accent (`--accs`, or `--accds` on the dark foot). The phone's hover colours on 22 px and
20 px lines (`.h6`, `.sub`) take `--accs` too. Stress (engine, fernhollow / pellbrook / wendholm): every variant passes.
