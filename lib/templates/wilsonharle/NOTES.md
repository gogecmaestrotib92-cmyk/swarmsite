# wilsonharle — a law firm's page: one quiet face on a dark room, a slow slideshow, large ruled rows

Reference: https://wilsonharle.com — measured 2026-11-12 at 1440 and 390: the home page, and /people, /services,
/contact, /pages/about-us (also /resources, /pages/careers) for the parts the home page lacks. No cookie wall. The
measurements and the scripts that made them are in `ref/` (`anatomy.json`, `sub-*.json`, `probe2-4.mjs`, `probe3.txt`,
full and stepped shots). Test clients: `law1` (primary), `person1`. Niche: law (holds for one person).

The home page of the reference is three screens: slideshow, an index, the foot. Everything a client's visitor comes
for beyond that (people, fees, offices) the reference keeps on sub-pages, so those sub-pages' parts are used for it.

## Sections of the reference and what each takes
| # | reference | ours | data |
|---|---|---|---|
| 0 | header 142 high, sticks 38 above the window (104 stay); its ground stops 14 px short of both window edges with 5 px lower corners; drawn logo left; 7 words right, 14px | same; the name set in spaced capitals; `cta` is the last word | brand.name, nav, cta |
| 1 | first screen: a 1328×810 black room 56 in from both sides; 11 studio portraits fade through it; one 28/38 sentence (the h1) at the bottom left, 810 wide, 80 from the foot; at the right a 160 px hairline, then name and role, 16px | same room and slideshow; h1 = title, the text after it in the same size; the two buttons and the note as plain 16px words under it (the reference has no buttons anywhere); name and role only when the slide is that person's own portrait | hero, media.photos (≤3 wide), team (caption) |
| 2 | index: 454 \| 30 \| 844. Left: 16px label, a list of names 16/22 light, 39 apart. Right: label, rows of 28/38 titles (tracking −1px) with a hairline under each, "View All" | left: service names, each jumps to its tile; right: the steps as rows, title + its sentence in 16/22 under it | features (names), steps |
| 3 | /about-us: a ruled side list of sub-pages 156 wide; 40; a 546 column — 14px label, 36/38 heading, 16/23 paragraphs; 40; a photograph 546×900 from the header down | same; the photograph runs to the window's edge (see "Pictures and text"); numbers as one more ruled list under the text | hero.kicker, statement, links, figures, one photograph |
| 4 | /services: 16px label, 59, a 28/38 sentence 656 wide, 80, a four-column grid of 320×300 tiles (gap 16, radius 5), each a different muted colour at 60 %, 24/30 title in the page's dark; four dim photographs fixed behind (three at .1, the top right one at .45) | same grid; tile colours are one family (below); the tile also holds the service's sentence, 14/20, at its foot; one dim photograph at the top right, pinned while the section passes | features |
| — | (no fee list on the reference) | the index part again per group: label and text left, large ruled rows right with the price at the row's right end | catalogue, plans |
| 5 | /people: same head; a three-column grid of 432×300 black tiles, a studio portrait covering each, name and role 19px at the top left | four columns of square tiles so a square portrait is whole (see "could not be transferred"); name and role at the foot of the tile; phone and e-mail under it; people without a portrait in a ruled three-column type list. One or two people: part 3 instead, the portrait as the column | team |
| — | (no testimonials on the reference) | rows in the index's right column; the name after the slideshow's 160 px hairline | quotes |
| — | (no questions on the reference) | rows that open; answer in the 16/23 body face | faq |
| 6 | /contact: 150 below the header the address and the telephone, 28/38; then 16/22 and 18/22 lines in a 350 column; a photograph of the door fixed behind at .1 | same, opened by the client's closing words in the sub-page head (label + sentence); offices three across; credentials as a ruled list with the client's badges | close, hero.text2, place, contact, locations, credentials |
| 7 | foot: hairline, logo left, one 14px line right | name left; links, legal line right | brand, foot |

Not built: the publication pages, /resources, /careers, the second (boxed) text column on those pages.

## Measures used (1440 / 390)
- Side margin 56 / 14 (index and foot 28 on the phone). Header 142 / 126; name at y 60; nav 14px, gaps 48.
- Room: 90vh (810 at 900; 760 at 844), copy 56 / 20 in, 80 / 20 from the foot; h1 and sentence 28/38 / 20/27.
- Room → index 165. Label 16/16; label → list 57; list pitch 39; rows: 32 above and below the title, 1px hairline at 20 % of the ink.
  Phone: rows first, then the list (the reference reverses the two columns); titles 24/34.
- Sub-page head: label 80 below the section top; sentence 59 below, 28/38 / 27/35, 656 wide; grid 80 below. Tiles 320×300, gap 16, radius 5,
  title 20/24 in; one column 362×300 on the phone, title 22/27.
- Text beside a photograph: 156 \| 40 \| 546 \| 40 \| picture; side list starts 100 down, rows 57; label 14/20; heading 36/38 / 26/34, 50 under it;
  body 16/23, 20 between; picture min 900 high. Phone: picture first (360 high), text, then the side list.
- Contact: 150 below the section top; 28/38 lines 40 apart; small column 350 wide.
- Foot: hairline 107 below the section top; name and line 40 below it; 42 to the page end.
- Phone menu: full dark panel, words 26px centred, 46 apart; three 25 px hairlines 6 apart as the button.

## Font stand-ins (open licence, Google Fonts)
- Classico URW (an Optima) → **Tenor Sans** 400: the nearest open humanist sans with a slight flare and the same wide, calm
  set. It is a little wider (the statement is tracked −0.4px, rows −1px as measured) and its figures have more contrast
  than its letters (the 7 is crossed). Tried and set aside: Marcellus (old-style figures — a 0 reads as O in a price), Belleza (narrower, darker).
- DM Sans 300/400 — the reference's own second face, open licence, used as is.
- The reference's logo is drawn; the client's name is set in Tenor Sans capitals, tracked .42em.

## Colour
The reference is a dark room (#181717) with pale ink, black under its pictures, and red only where something is
pointed at. Kept as relations, with the client's palette: **the darker of the client's ground/ink is the room, the
lighter is the ink** (law1: navy #020030 with white; person1: #111 with white); a darker pit (62 % toward black) under
pictures; the accent on hover only, lightened toward the ink until 4.6:1 (law1's yellow as is; person1's blue → #2989b8).
This turns a client whose own site is white into a dark page — a decision, written down here because other templates keep the
client's ground. It is one place in `render()` (the lines that set `G` and `T`).
Tiles: the reference gives each service its own colour. Ours are one family — the accent stepped toward the ink in six
steps, at 60 % over the room, full when pointed at — each checked for 4.6:1 under the dark title.

## Pictures and text
- Photographs are shown without colour (`MONO = True`, a CSS filter): every picture on the reference is black-and-white
  and its page depends on that; the client's files are not changed. Badges keep their colour.
- First screen: the reference sets its sentence straight on dark studio portraits. A client's photograph may be white
  there, so the copy stands on a veil in the pit colour (.93 at the foot, gone 190 px above the first line). Departure for the owner's readability rule.
- The photograph beside the statement: the reference's column is 546×900 and stops at the 56 px margin, which leaves it
  standing as a panel. Ours runs from the header to the section's foot and off the right window edge (owner's rule: edge to edge, as tall as its section). Not boxed.
- One or two people: the portrait is the column, whole, at its own proportion and never wider than its pixels (person1: 944×814 shown 798×688), top and right edges flush.
- Dim pictures over services and people: the reference fixes four behind the whole page; ours is the top right one only
  (50vw × 450), pinned to the window while its section passes (sticky), fading out at its left and lower edge, at .45 or
  less (lowered from .45 until white ink keeps 4.7:1 on a white pixel of it: .42 on law1, .39 on person1).
- Contact: one photograph behind the block at .1, pinned likewise.
- No `media.made`. No picture is used twice; small ones never above their pixels; an `alt` is never set as copy.

## Image slots
| slot | takes | law1 | person1 |
|---|---|---|---|
| slideshow (≤3) | width ≥1300, ratio ≥1.2 | colleagues.jpg (one slide, so no fading) | bionassay.jpg, hero.jpg |
| beside the statement | upright ≥600 wide, else ≥760 high | — (plain) | ferrata.jpg |
| dim over people | ≥720×360, people/room first | firm-group.jpg | — (one person) |
| dim over services | ≥720×360 | — | aravis.jpg |
| behind contact, .1 | ≥1000×600 | — | powder.jpg |
| portraits | the person's own, ≥362 | 10 tiles; 25 people in type | portrait.jpg as the column |
| badges | the client's files | 3 | uiagm.png |
Still without a picture: law1's statement column, services and contact; nothing made stands in.

## Motion: measured → reproduced
| measured on the reference | ours |
|---|---|
| first screen fades in on load: opacity 0 → 1, about 2.5 s, starting ~1.2 s after load | CSS animation, 2.4 s linear after .3 s (measured 0 → 1 in ~2.8 s) |
| slideshow: Webflow "outin", delay 6000, duration 3000, ease-in-out — the picture fades to black in 1.5 s, the next comes up in 1.5 s, every 6 s; the sentence stays | same times and curve (measured: out ~1.5 s, in ~1.5 s, 6 s cycle). Stops when the tab is hidden or reduced motion is asked; without script the first picture stays |
| header sticky at top −38 px, z above everything | same (measured −38) |
| dim photographs fixed to the window | pinned per section (measured: top stays 0 over 500 px of scroll) |
| nav word → red in .525 s; list name .4 s; row title .6 s; "View All" .5 s | same durations, to the client's accent |
| service tile ground .6 → 1 in .2 s; people tile picture 1 → .65 in .2 s | same |
| phone menu: full panel | same, as a `<details>` so it opens without script; Escape and a tap on a word close it |
Not reproduced: Lenis smooth scrolling (script-driven scroll inertia; left to the browser); swipe on the slideshow;
the sticky side list and picture on /about-us (their column is shorter than the window, nothing moves).
Not measured: whether the phone header sticks (ours sticks 28 above, by analogy).

## What could not be transferred, and why
- The studio portraits on black: they are the reference's whole first screen and people grid. A client's portraits are
  what they are (law1: tight square head shots on white). So tiles are square (320) instead of 432×300 so no head is cut, the name
  stands at the foot on a veil instead of top left on black, and the grid is four across instead of three.
- Eleven slides: a client has one to three photographs wide enough.
- The four-picture backdrop grid; the per-service colours (see Colour).
- "Latest Publications": no client block holds dated articles; the rows carry the steps.

## Checks (2026-11-12)
shots.mjs — law1: d height 11364, sideways 0, distorted 0, h1 1, errors [] · m height 21019, sideways 0, distorted 0, h1 1, errors [].
person1: d height 8199 · m height 12735, the same zeros, errors [].
legible.mjs — law1 ok (863 readings), person1 ok (555). No FAIL was explained away.
coverage.mjs — reference 32 overall, per screen 80 / 6 / 0, one wide picture. law1 16 overall (80, 6, 0 … 42, 66 at the people), person1 22 (80, 6, 33, 37 …);
both pages are over 1.5 × the reference's height, so the shared screens are compared: 80 / 6 against 80 / 6. Pictures at .1 are not counted on either side.
Also checked by script: keyboard focus (2 px accent outline, offset 4), reduced motion (first slide shown, nothing fades), no script (page whole, menu opens).
Variants of law1 from scratch copies (1/3/5 plans, 2/9 features, 1/6 steps, 12-word h1, 40-character button, faq and none, no photographs,
42-letter name, slideshow caption, brand name only, sportbot's data): no sideways scroll or element outside the window at 1440, 1024 and 390;
legible ok on no-photographs, 5 plans, faq, 40-character button, caption, sportbot and a grey-ink palette.
One-file copies: `out/law1-one-file.html`, `out/person1-one-file.html`.
