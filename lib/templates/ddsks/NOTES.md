# ddsks — Den Danske Scenekunstskole (ddsks.dk), niche: school

Measured 2026-11-12 at 1440×900 and 390×844 with `tools/anatomy.mjs` and the probes in `probe/` (`dom.mjs` computed
styles and boxes, `motion.mjs` positions over scroll, `css.mjs` the rules behind them, `menu.mjs`, `steps.mjs`).
Test clients: `school1` (primary), `person1`. Everything below is either **measured** (a number read from the live
page), **ours** (what the template does) or marked as a choice.

The home page has four real sections (opening, staggered teasers, three event cards, picture band) and a foot. It has
no prices, people, questions or contact details, so four inner pages were measured for the parts those need:
`/da/uddannelser` (two-column title list, dark band of links, "see also" list), `/da/oftest-stillede-spoergsmaal`
(drawers), `/da/ansatte` (people list), `/da/kontakt` (type-only opening, address block).

`tools/shots.mjs` on the reference reports height 4604 and an opening 1280 px tall: that is an artefact of its
full-page capture resizing the window. Scrolled for real the page is 4124 px and the opening is 800 px (`ref/home-real-*`).

## Sections of the reference and the data each takes

| # | Reference (measured at 1440) | Ours takes |
|---|---|---|
| 0 | Header: links fixed at y 30, 20 px condensed caps (language switch at x 827, search and menu at the right, each with a 32 px ring). A 65 px paper bar is fixed behind them; the opening picture lies over the bar, so the links are white on the picture and black on the bar once the opening has gone. Logo fixed at 144/70, fades after the opening. | `brand.name` in type at the left (as the reference's phone build sets its name: 20 px, tracking .1em); `place.phone` at x 827; `cta` and the menu button at the right. |
| 0b | Menu: whole screen, black, numbered items 40/40 in two columns at x 535 and 926, 150 px apart, from y 280; the word "Menu" turns red and the ring becomes a filled disc with a cross. | `nav` (+ `signin`). |
| 1 | Opening: full-bleed photograph, 800 px. Text block 100 px from the bottom: h1 80/70 caps, 74.6 % wide; text 24/30 light from x 535, 66.1 % wide; link 20 px with a 24 px arrow, 30 px below. | `hero.title`, `hero.text`, `hero.primary`; picture = widest free landscape photograph. Without one: the reference's type-only opening (`/da/kontakt`: h1 130/111 at x 437, 150 px from the top). |
| 1b | (inner pages) text block at x 437, 566 wide, 18/24. | `hero.text2`, `hero.note` (14/20 grey), `hero.secondary`. |
| 2 | Label 20 px caps 80 px under the opening; four teasers, staggered: 1 picture 469×317 at the right, text from x 535; 2 picture 371×469 upright at the left, text from x 534, 160 px of air under it; 3 pulled up 130 px over the second, picture 469×317 at x 437, text right-aligned at the right edge; 4 as 1. h2 60/55, text 18/24, link 20 px. | `steps.title` (label), `steps.text` (24/30), `steps.items[]`: title, text, `cta`, `img`. A fifth step starts the cycle again. |
| 3 | Picture band, 750 px, padding 90/300: label, sentence 80/70 white, two links 40/40 with rings. Joined to the foot. | Two bands of this build: `statement` + `figures` (values 80/70, labels 18/24, three columns) mid-page; `close` (+ `close.cta`, phone, e-mail as the 40 px links) as the last band, joined to the foot. |
| 4 | Drawers (FAQ page): ring with chevron at x 339, title 40/40 at x 391, 566 wide. | `catalogue.groups[]` — one drawer a group, closed as the reference's are (a single group is open); inside, rows in the reference's small type: name 20 px condensed, price 20 px condensed at the right, note 14/20 grey under the price, `prices[]`, `text`, `rows[]`, `state`. `faq` uses the same drawers. |
| 5 | Three cards (home, "Det sker"): columns 371 wide at x 144/534/925, title 40/40 (274 wide), 14/20 grey line, picture 371×195, 20 px date; row gap 40. | `features.items[]` as type cards (title 40/40, text 18/24); `plans` in the same columns (name 40/40, price 80/70); `place.spaces[]` as cards with their pictures, then up to four further room photographs without words. |
| 6 | People (staff page): two columns at x 339 and 827, portrait 176×220, name 40/40, 14/20 grey line, role 20 px condensed. | `team` (items or groups): name, role, text, e-mail/phone; portrait only if the person has one. `credentials` in the same two columns (title 40/40, year, 14/20 grey text, badge 88 px). |
| 7 | Dark band of links (inner pages): padding 80/70, faint picture, links 40/40 with rings in two columns at x 339/827; "see also" entries carry a 14/20 line. | `links[]` with `d`. |
| 8 | (FAQ page) lead paragraph 24/30 at x 437, 761 wide. | `quotes[]` (the words 24/30 light, name 20 px condensed) and every section's lead text. |
| 9 | Foot: grey block (rgb 241), padding 40/45, columns at x 339/632/827, heads 20 px caps, entries 20 px condensed 30 px apart; under it a white row with e-mail, grey registration lines, grey links, three social rings; a "back to top" bar slides up from the bottom edge. | Column 1 `brand` (logo file, name), address, phone, e-mail, hours; column 2 `nav`; column 3 `contact.form`/booking as head, `contact.routes`, `place.social`. Row: `foot.text`, `foot.legal`, `foot.links`. |

Not in either test client and built from the same parts: `plans`, `faq` (checked with sportbot's data: renders, legible ok).

## Measures used
Wrapper 80vw (10vw margins; 90vw from 800 px down). Twelve columns of 78.1 px with 19.5 px gutters at 1440; the
reference's stops 144 · 339 · 437 · 535 · 632 · 827 · 925 · 1120 are column edges and are written as percentages
(16.95 %, 25.42 %, 33.90 %, 59.32 %, 67.80 % …). Type: 130/111, 80/70, 60/55, 40/40, 20/20 condensed caps; 24/30
light, 18/24, 14/20 text. Phone: bar 50 px, opening one screen high with the text 100 px from the top, h1 40/40,
text 22/27, teaser heads 30/30 with **no pictures** (the reference hides them at 500 px and below), cards one column
with 50 px between, band padding 60/120 with 40/40 heading, foot in two columns. No radii anywhere except the 32 px rings.

Colours: the reference is white, black, one grey block (241), grey 74 for small lines, red on hover and for text links.
Ours: `palette.ground`, `palette.ink`, grey block = ground with 6 % ink, small lines = ink lightened until 4.6:1 on that
grey, links and hover = `palette.accent` (moved toward ink if under 4.5:1); menu and bands stand on one dark derived from
the ink; on the dark the hover colour is the accent lightened to 4.6:1.

## Fonts
- Akzidenz-Grotesk Condensed (commercial) → **League Gothic** (OFL). Same kind — a tight condensed grotesque — and the
  same set width: the reference's 80 px heading runs 25.8 px a letter, ours 26.
- Akzidenz-Grotesk Light/Regular (commercial) → **Hanken Grotesk** 300/400 (OFL), a plain grotesque with a light cut.

## Motion — measured, and what ours does
| Measured on the reference | Ours |
|---|---|
| Header links fixed; white until the opening's bottom edge reaches the 65 px bar (colour flips between scroll 700 and 800 of an 800 px opening), then black on the paper bar; colour transition 100 ms cubic-bezier(.25,.46,.45,.94). | Same: the flip is at opening height − 65 (measured on ours: white at 700, ink at 760; phone white at 744, ink at 804). |
| Logo fades (opacity, 100 ms, 100 ms delay) once past the opening. | Not reproduced: the name stays in the bar — choice, it is the way home on a long page. |
| Teasers, cards, link row, band, foot blocks start at opacity 0, 50 px low, and rise into place when they enter; the three cards one after another (at one sample: 0.4 / 10.8 / 50 px left to travel). Sampled every 350 ms a block had 1–4 px left, i.e. roughly 400 ms with an ease-out. Duration and curve are **read from samples, not from a rule** (the page sets them from script). | 50 px rise + fade, 400 ms, the reference's own curve, 150 ms between neighbours in a row. Only when scripts run; nothing is hidden without them. |
| Teaser hover: picture scale 1.05 (100 ms ease-in), heading to red (100 ms), arrow 10 px to the right (200 ms). Card hover: a second copy of the picture fades to .3. | Scale, heading colour and arrow as measured. The second-picture fade is not reproduced (needs a second file per picture). |
| Rings (search, menu, top): fill slides in, 200 ms cubic-bezier(.77,0,.175,1). | Ring fills on hover over 200 ms with that curve (a fade, not a slide). |
| Menu: opacity 0 → 1 (0.99 at 150 ms). | 200 ms fade; focus moves into it, Escape closes it. |
| "Back to top" bar: translateY(100 %) → 0 over 500 ms cubic-bezier(.25,.46,.45,.94) when the foot comes into view (first seen at scroll 2800, foot top 3709 − 900). | Same, on the foot entering the window. |
| No parallax: the opening picture scrolls with the page (transform stays identity). Nothing is pinned but the header. | Same. |
`prefers-reduced-motion`: no rise, no transitions (checked: 0 of 48 blocks hidden at load).

## Where ours departs, and why
- **Text does not run over the teaser pictures.** In the reference the heading and the black text overlap the picture's
  left edge by 177 px. Black text over a photograph fails the readability gate, so the text column of teasers 1 and 4
  starts at x 339 instead of 535 and stops at the picture; teaser 3's text is 4 columns instead of 6.5. The stagger,
  the picture sizes and the third teaser riding 130 px up over the second are kept.
- **Veils.** The reference sets white type on bare photographs. Ours puts a veil of the dark behind every text block on
  a picture (60–78 % in the opening, 74–76 % in bands, 80 % in the band of links, 70 % behind the header links),
  fading out below the text, because the gate reads the third-worst pixel and a client's photograph can be white there.
  The pictures are therefore dimmer than the reference's where text stands.
- **The upright teaser picture** is only cut upright (371×469) when the photograph is 600 px high or more; a small
  picture keeps its own proportion and is never shown wider than its pixels (school1: all four at 450×338).
- **Logo.** The reference's turned wordmark is its logo and not taken; the client's name is set in type in the bar and
  the logo file stands in the foot.
- Interface words that are not client facts ("Menu", "Close", "Back to top") come from a ten-language table in render.py.
- Icons are drawn here (ring with arrow, chevron, three dots, cross); the reference's own glyphs are not used.

## Image slots
`data-slot` on each: `hero`, `close`, `statement`, `links` (bands — widest free landscape photographs, in that order),
`step`, `space`, `room`, `portrait`, `badge`, `logo`. No made pictures. A band without a photograph stands on the dark
ground; a step, space or person without one is type only.
- school1: hero door-group 2400, close teacher 1900, statement students-outdoors 1900, links team 1200 (**enlarged to
  1440**, 1.2×, under the 80 % veil); steps teacher-2, aula-5, flamenco, students-view at 450×338; spaces patio, aula-4;
  rooms aula-1, aula-2, aula-6, oficina. Left over: sala-profesores, students-2017, school-group, tango.
- person1: hero hero.jpg 1568 (the photograph itself carries the words "You are here"); steps aravis, powder (cut
  upright), ferrata, bionassay; portrait; badge. Statement, links and close have no picture. Left over: toprope, salbit, book.

## Picture share (`tools/coverage.mjs`, 1440)
- Reference home: **53 %**, per screen 89 · 34 · 27 · 82 · 22, two screens with a wide picture.
- school1: **36 %**, per screen 89 · 16 · 31 · 87 · 11 · 0 · 48 · 5 · 0 · 2 · 89 · 64 · 0, four screens with a wide picture.
- person1: **17 %**, per screen 89 · 17 · 35 · 11 · 0 · 0 · 0 · 0 · 0, one.
Both are more than 5 points under the reference. The reference's two wide pictures are both there (opening, closing
band) on school1, plus two more; what pulls the share down is length — the reference's home page is 4124 px and sends
prices, people and questions to other pages; a one-page site for school1 is 11 111 px, and 46 courses, 11 people without
portraits and 6 credentials are type. person1 has a single photograph free for a band.

## Checks
- `shots.mjs`: school1 d 11111 / m 15050, person1 d 7956 / m 9427 — sideways 0, distorted 0, one h1, errors [].
- `legible.mjs`: school1 `ok — 0 unreadable of 723 line readings`, person1 `ok — 0 unreadable of 462 line readings`.
- `probe/ours.mjs`: without scripts nothing is hidden, the header is not fixed, drawers are native `<details>`;
  focus ring 2 px solid in the text colour on every stop tried; menu opens, takes focus, closes on Escape.
- With `media.photos` emptied: both render clean; school1 legible ok and looked at (see needs.json).

## Not transferred
The search link (no search on a one-page site; the `cta` stands there), the language switch (the phone number stands
there), the event calendar with dates and sign-up state (no client block; `place.events` is not built), the second
hover picture, the staff filter and pager, the breadcrumb.

## Not checked
Widths between 501 and 1000 px were not looked at (the rules for them are the reference's breakpoints at 800 and 500,
written from its style rules, not from screenshots). Hover states on ours were not photographed. The reference's inner
pages were measured at 1440 only. The one-file copies were written, not opened. The machine's disk was full during the
work (about 120 MB free); several captures failed with ENOSPC and were run again — the files listed here were checked after.

## Soft sections absent (2026-11-12, branch never-zero)
The header turns from white to ink when the opening picture has gone past the middle of its line (40 px from the top),
not when it is 65 px from the top. A short page (the minimal stress client: the opening, three photographs, the contact
lines) can end its scroll with the bottom 35-65 px of the opening picture still under the header; the ink line stood on
the dark picture there (1.47:1 at 1440). With steps, close or features absent the page drops those sections whole and
holds: `python3 lib/templates/stress.py --sweep ddsks` on svetlinka passes base, no-features, no-close, no-steps,
no-step-pictures and minimal.
