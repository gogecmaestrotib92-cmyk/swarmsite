# innerflow — notes

Reference: https://innerflow.es (home page; its /faqs/ and /buy-a-pack/ pages for the question and price parts), measured
2026-11-12 at 1440×900 and 390×844 with `tools/anatomy.mjs` and own Playwright probes (`probe/`: box/style tree, scroll
sampling at 21 positions, hover/press states, slideshow sampled every 90 ms, keyframes read from the stylesheets).
The cookie notice was refused ("Deny"); the chat bubble was hidden for the captures. Raw captures: `ref/`.
Test clients: `local1` (joinery) and `clinic1` (dental practice, German). Statements are **measured**, **chosen** or **not verified**.

## Sections of the reference, in order, and the data each takes

| # | Reference (measured) | Data | Left out when |
|---|---|---|---|
| 0 | Bar: fixed, 16 in from the edges, 60 high, radius 5, tinted ground at 50 % with a 15 px blur; logo, 4 links 14 px, 3 outline pills 25 high, a two-line menu sign. Menu = full-screen layer, list in the right half | `brand`, `nav` (without "Home"), `place.phone`, `signin`, `cta` | never |
| 1 | Opening: one screen, pinned while the next section slides over it; a photograph smeared into vertical streaks; h1 60/60 with a mono note at the right; two 30 px arrow links; 16 px text 648 wide; two 260×50 pills; "explore ↓" at the right | `hero.title`, note = `place.address.city` + `hero.note`, links = first two `nav` items, `hero.text` + `text2`, `hero.primary/secondary`; picture = a free large landscape photograph | never (plain dark band without a photograph) |
| 2 | Statement: mono label, 60 px head 680 wide, a rule that is faint in the left half and full in the right, a line drawing left, two 25/35 paragraphs and two pills right | `hero.kicker`, `statement.title`, `statement.text`, `cta` + `hero.secondary`; left half: `figures` or empty | no statement |
| 3 | Intro: 60 px head with an 11×46 accent bar, 30 px "more →" link under it; 40 px head and 16 px text right | `catalogue.title`, link = the catalogue's own address with the client's words for it, `steps.title`, `steps.text` | none of them |
| 4 | Nine outline cards (3 × 417×251, radius 10, 1 px white) on a full-width photograph under a 50 % veil; a card's list fades in on hover, the card blurs what is behind it, the photograph changes to that card's | `catalogue.groups` (two or more titled groups → a card per group with its item names) or items (a card per item: prices, note, rows, text ≤ 380 characters); backdrop = second free large photograph; hover picture = the item's own `img` | no catalogue and no `features.items` |
| 5 | "The location": head 40, text 16 at 414 wide, ← →, a 130 px count "01 /04", a 893×595 slideshow bleeding off the right edge | `steps.items[title,text,cta,img]` | no step items |
| 6 | (its /faqs/ page) numbered rows: mono number, 18 px question, plus sign, 25 px padding, 25 % rule, 40 px head in a left column | catalogue items the cards cannot hold (grouped catalogues; texts over 380 characters), then `faq` | nothing to list |
| 7 | Dark part: 60 px statement in pale accent; rule; bar head left, bullet list (18 px caps) and 18 px text right; four pale cards 309×357, radius 10, a drawing and a mono caption each | short `features.text`/`catalogue.text` (≤ 150 characters); `team.title`, `trust[]`, `team.text`; cards = `team` people (portrait, name, role, text) | each part alone |
| 8 | Mono label, rule, a diagram left, 25/35 text right | one block per `quotes[]` (label = name, text = quote, role under it) and per `credentials[]` | none |
| 9 | Film, 1280×720, container wide | `media.video`, else `projects[]` as a slideshow with the project title, else up to four unused landscape photographs | none of them |
| 10 | (its /buy-a-pack/ page) outlined price cards, radius 4, centred: name in caps, 40 px price, short rule, small lines, a mono tag | `plans` | no plans |
| 11 | Closing: dot + one 16 px line, 60 px head, two outline pills, centred | `close.text` (above the head when ≤ 90 characters, else under it), `close.title`, `close.cta`, `hero.secondary` or the phone | no `close.title` |
| 12 | Foot: the name set 1280 wide, tone on tone; a 40 px line; two columns of mono arrow links; a block of ruled 34 px rows (its newsletter form); bottom line 12 px | `brand.name`; `place.address`; `nav`; `place.social` + other `links`; rows = phone, e-mail, `place.hours`, booking, `contact.form/routes`, `locations[]`; `foot.text`, `foot.legal`, `foot.links` | never |

Both clients get 0–5, 7–9, 11, 12. clinic1 also gets 6 (two groups, fifteen services with their texts); local1's two long
service texts fit their cards. Neither has `plans` or `faq`; those parts were checked with sportbot's plans and questions
put into local1 (`probe/local1-plansfaq.html`, not an output).

## Measures used (measured unless marked)

- Container: 80 px each side (16 on the phone); two columns of 620 with a 40 gap, the right one starting at x 740.
- Type: h1 / big heads 60/60, −.14 px (phone 50 and 35); second heads 40/46.8 (phone 25/29.25); lead 25/35 (phone 16/22.4);
  text 16/23.2; large links 30/43.5 (phone 28, "more" 18); mono label 15/23.4 +.7 px caps (phone 12); small mono 12/18;
  pills 14 px, weight 500, caps; count 130/130 with a 12 px "/04".
  **Chosen:** the h1 steps down for long titles (≤ 34 characters 60/50, ≤ 60 → 52/40, longer → 44/32); the reference's is six words.
- Opening: bottom-aligned, 70 px under the pills (phone 40); 150 between h1 and links (scaled with the screen height), 50 to the text, 50 to the pills.
- Statement section: 70 above, head 25 under the label, rule 100 under the head (phone 40), 50 to the columns, pills 50 under the text; intro 150 lower (phone 70).
- Cards: section padding 70 (phone 40); gaps 15 across, 63 down (phone 40); padding 25, title 25/35, body 16/23.2 from 25 lower, lists in two columns; phone: two per row, 93 high, padding 10, title 16.
- Slideshow band: 150 above the head; text 414 wide; arrows 25 under the text; count at the bottom. Phone: text, arrows, then the picture 300 high inside the 16 px margins, no count.
- Rows: left column 290 + 40, number column 100, 25 px padding, 1 px rule at 25 %.
- Dark part: 100 above and below (phone 40); rule 100 under the statement; cards 100 lower, 15 apart, padding 40 (phone 30), caption 25 under the picture; label blocks 100 apart, rule 25 under the label, text 50 under the rule; film slot 150 above; closing 150 above, 25 between its lines.
- Price cards: 3 columns, 15 gap, radius 4, name 16 caps, price 40, rule 150 wide. **Chosen:** lines 14/20 instead of the reference's 12/18.
- Foot: name band 100 above and below; 40 px line; link columns 220 each, 12/17.4 mono caps; rows 34 high in a 400 column; bottom line 40 above and below.
- Radii: bar 5, cards 10, price cards 4, pills 500. Focus ring 2 px in the text colour, 3 px off (**chosen**; the reference shows none that I could measure).

## Colour relations

Reference: white ground, ink (42,53,55), dark part (30,39,43), foot (43,53,55), pale accent (213,225,194), bar (230,228,220) at 50 %.
Here: ground and ink are the client's; the dark part is the ink taken 27 % toward black, the foot is the ink; the pale accent
is the client's accent lifted toward white until 9:1 on the dark part; the bar is the ground at 78 % (**chosen**, see below);
the four pale card grounds are one hue (the accent at 14–44 % in the ground) instead of the reference's four hues (contract: one family).

## Typeface stand-ins (SIL OFL, Google Fonts)

| Reference (commercial, Dinamo) | Stand-in | Why |
|---|---|---|
| Favorit 400/500 | **Space Grotesk** 400/500 | geometric grotesque with the same idiosyncratic details (single-storey shapes, flat terminals), drawn as a companion to a monospace |
| Favorit Mono | **Space Mono** 400 | the monospace Space Grotesk derives from; same role of small caps labels |

Space Grotesk runs slightly wider than Favorit; no sizes were changed for it.

## Motion — measured, and what was reproduced

| What | Measured on the reference | Here |
|---|---|---|
| Opening | `position: fixed` from 0 to one screen of scroll, then released; the next section (opaque) slides over it | `position: sticky; top: 0` under the following sections; if the opening is taller than the screen it scrolls to its end first (set by script). Without script it simply scrolls |
| Opening links and text | drift up: 0 → −18 px over the first ~400 px of scroll (−6.8 at 100, −16 at 300, −17.9 from 600), linear | same |
| Reveals | on entering view: fade .5 s ease-out; heads drop 10 px, text and links rise 50 px; 200 ms between items of a section | same keyframes and delay; only with script and without reduced motion |
| Bar | stays; its text turns white over the card grid and the dark part while the bar keeps its light 50 % tint | bar stays; **not reproduced:** the text does not turn white — on a half-clear bar over a dark picture the ink comes to about 3.7:1 by calculation (not measured on the reference), and white on the light tint is no better, so the bar is 78 % ground with ink text everywhere (owner's readability rule) |
| Card grid | photograph travels 200 px down against the section while it crosses the screen, linear; hover: body opacity 0 → 1, card backdrop blur 0 → 15 px, both .3 s ease-in-out; an arrow appears top right; the section photograph is swapped at once | same travel and timings; the swap is a .3 s cross-fade (**chosen**); the hovered card also gets a 28 % dark tint so its text holds on any photograph (**chosen**). On touch screens the body is always shown |
| Pills | colour, ground and border .1 s ease-in-out: dark → pale accent with dark text; outline → filled | same; hover of the white pill **not measured**, set to the pale accent |
| Slideshow | arrows only, no autoplay (count unchanged after 9 s); new picture pushes the old one out sideways over ≈ 800 ms, decelerating (−137 px at 150 ms, −582 at 340, −817 at 530, −890 at 750); count changes at once | `transform .75s cubic-bezier(.165,.84,.44,1)`, both pictures; count at once; the text of a step cross-fades in .3 s (**chosen** — the reference's text does not change); swipe on touch |
| Menu | full-screen layer, opacity .3 s linear | same; focus moves to the close button, Escape closes |
| Question rows | not opened in the probe | `<details>`; the plus loses its upright when open. Opening animation **not measured**, none here |
| Foot | the large name is held at the bottom of the screen and uncovered by the dark part (UIkit sticky, `position: bottom`) | **not reproduced**: needs script-driven pinning; the foot scrolls in normally |
| Reduced motion | not measured | no reveals, no drift, no pinning, slides change at once |

## What could not be transferred, and why

- **The opening picture** is the reference's own photograph, already smeared. Here the client's photograph is smeared in the
  browser (SVG `feGaussianBlur` 3 × 110 px, brightness .74, a 50 % veil of the dark tone, darker at top and bottom as in the reference).
  The streaks are softer and less colourful than the reference's; they depend on the photograph (pairs/01, /12).
- **Line drawings** (the circles beside the statement, the four drawings on the pale cards, the two-circle diagram) are the
  reference's illustrations. Statement: the left half holds `figures` or stays empty. Pale cards: the people of `team`, each
  with their own portrait in the drawing's place — the cards grow with a person's text (local1) and wrap to rows of four
  on desktop instead of sliding (clinic1 has ten people; **chosen** so nobody is hidden); on the phone they are the reference's sideways strip.
  Diagram block: the left half stays empty beside each quote.
- **Owner's rule, picture beside text.** The reference sets the location slideshow as a 893×595 picture to the right of its text.
  Here the slideshow is the backdrop of the whole band (1440 × ≈800), the text on a veil that is 90 % at the left edge and
  lets go between 34 % and 60 % of the width. On the phone the reference stacks text above a 358×300 picture; kept.
- **Words of the reference's controls** ("Explore", "More", "Close"): "explore" is only an arrow with an aria-label; "more"
  is shown only when the client's data has its own words for that address (local1 "View our work", clinic1 "Erwachsene").
- **City + clock** in the opening: the data has no time zone; the note is the city and `hero.note` (the phone number).
- **Newsletter form** in the foot: no such data; its ruled rows carry phone, e-mail, opening hours and booking.
- **Three bar pills**: phone, sign-in, call to action — as many as the client has.
- **Phone**: as the reference, the opening has no buttons and the bar only the menu sign.

## Image slots

| Slot (`data-slot`) | Takes | Without |
|---|---|---|
| `opening` | first free landscape ≥ 1600 wide (else ≥ 1200), not small, not portrait/people/product/dish | plain dark band |
| `cards` | next free landscape ≥ 1600 (else ≥ 1400) | cards on the foot colour |
| `card` | a catalogue item's or group's own `img` (≥ 1200, not a slideshow picture), on hover | backdrop stays |
| `slide` | `steps.items[].img` | band becomes type on the light ground |
| `portrait` | `team` person's `img`, own proportion held within 4:5–4:3 | card in type |
| `project` / `film` | `media.video`; else project pictures; else up to four unused landscapes ≥ 1280 | slot left out |

"Free" = not pointed at by a step, catalogue entry, person or project. Each photograph appears once. local1 uses 13 of 20
(its two catalogue pictures are the slideshow's, so no card swaps the backdrop); clinic1 uses 19 of 22.
Enlargement at 1440: local1's third slide (1200 wide) 1.2×, three project pictures (1200 wide) 1.07×; clinic1's banners
(2000×690) are shown 800 high in the slideshow band, 1.16×. None of them is marked `small`.

## Checks (2026-11-12)

- `tools/shots.mjs`: local1 d height 8892, m 7820; clinic1 d 8375, m 7143 — sideways 0, distorted 0, h1 1, errors [] in all four.
- `tools/legible.mjs`: ok for both (405 line readings each); ok for both renders without pictures (395, 390).
- `tools/coverage.mjs`: reference 33 %, local1 45 %, clinic1 36 % (details in needs.json).
- Own probe (`probe/check.mjs`): pin, drift, card hover, slide transition, menu focus and Escape, focus ring, reduced
  motion, no-script render, touch phone (card bodies shown, strip scrolls, no sideways scroll).
- One-file copies: local1 1.4 MB, clinic1 1.0 MB, nothing left outside.
