# runningcharity — template from therunningcharity.org (niche: nonprofit)

Measured 2026-11-12 at 1440 and 390: home page (`ref/anatomy*`, `ref/ref-*`, `ref/probe-*.json`, `ref/probe2-*.txt`),
and, because the home page keeps prices, questions, people and places on sub-pages, also: FAQ page (accordion),
choose-a-run page (priced shop cards, two-up), how-it-works page (numbered list), who-we-are page (team grid),
locations / our-services / get-involved / mission pages (image-text rows) — `ref/sub-*-d-full.jpg`.
Motion and states: `ref/motion.txt`. Picture share: `ref/coverage.txt`. No cookie wall, nothing accepted.

Test clients: `charity1` (animal rescue, 29 photographs) and `school1` (language school, 4 large + 14 small photographs).

## Sections of the reference → data

| # | reference part (where measured) | ours takes |
|---|---|---|
| 1 | fixed white header 85 px, shadow .16 0 1 4; logo 158×46 at x 62; nav 18/25 pad 0 15; Donate pill (home) | brand.logo (mark + name in type unless `logo_wordmark`) or brand.name in type; nav; signin; cta as the pill |
| 2 | opening: pad 120, text column 468 at x 139 (sub-title 18 accent, title 66/55 uppercase, text 18/25, pill), 567² picture at x 734 (home) | hero.kicker, title (the only h1), text, primary (pill), secondary (text link), note (15 px) ; picture = **right half, edge to edge, full section height** |
| 3 | impact row: white, pad 43/50; left 340 (eyebrow 13 bold, heading 57.6/50.7, text 16/24, link); four figures 54.7 px number + 34 px suffix in accent, 14 px label; count-up (home) | statement (title, text) on the left; figures (v split into number + suffix, l) — 4 across, 3 when 5+ |
| 4 | image-text: #f7f7f7 ground, pad 120, picture 567×378 at x 139, text 468 at x 833: title 44/39, text 18/25, pill (home) | steps.title + text; picture = **left half, edge to edge** |
| 5 | numbered list: 567 column at x 437, headings 36/39 "1. …", text 18/25, accent link (how-it-works page) | steps.items (4 or fewer): k (accent sub-title when it changes), title numbered, text, cta; more than 4 stand in the two-up part (9) |
| 6 | photo band 1440×702, pad 255, moving line 79 px oblique uppercase white, 18 px line, pill (home) | catalogue.title as the moving line (or statement.title when there is no catalogue), catalogue.note as the line; no pill (the data has no label for it) |
| 7 | shop cards: 369 wide, shadow .16 0 3 12 → .26 0 3 15 on hover, square picture, title 66/55 centred, price 18 accent, text 18/25 centred, "View" pill (choose-a-run page) | catalogue groups with pictures (≥ half of a group's items): every item as a card: img, name (66 px when ≤ 10 characters, else the reference's 36 px card-title size), price with `from`, state, note, prices[] as ruled pairs, text, rows[] as ruled lines; the title links to item.h. Also plans as the same cards. |
| 7b | ruled rows: 1px rgba(0,0,0,.15) rules, 22/25 lines, 567 column (FAQ page accordion rows) | catalogue groups without pictures: name + price on one ruled line, note/prices/text/rows below (school1's 46 courses) |
| 8 | image-text, picture right (home, second one) | features.title + text; picture = right half |
| 9 | two-up: two 369 columns centred at x 238 / 833, title 36/39 centred, text 18/25, accent link (choose-a-run page) | features.items; quotes; and (section 13) locations / place, contact, credentials |
| 10 | accordion: 567 column, group title 44/39, rows ruled, questions 22/25 pad 15 0, round 36 px accent toggle with a white plus, answer 18/25 pad 20 0 5, first open (FAQ page) | faq.title, items (q, a) — `<details>`, the first open |
| 11 | team grid: 5 across, 219 wide, square portrait, name 22/24 condensed, role 15/21 (who-we-are page) | team (items and groups): name, role, text, email, phone; portrait only when the person has one — otherwise type only |
| 12 | news cards: 3 across, shadow, content pad 32, title 36/39 (home) | links (t, d, h) as type-only cards |
| 13 | two-up (as 9) | locations (name, address, phone, email, hours, note, h) or place; contact (phone as title, note, email, form, routes except social); credentials |
| 14 | newsletter block: centred, title 52/59, text 18/25 in 567, form + pill (home) | close (title, text, cta) — the pill instead of the e-mail form |
| 15 | supporters strip: logos, centred (home) | logos; when none, trust as a centred line of words |
| 16 | foot: #111, pad 60; moving line 34 px oblique; columns 198 apart, 15/21, heads white, links 60 % white → accent on hover; bottom rule .15, legal left, links right (home) | brand.name as the moving line; nav / links / phone, email and social routes as three columns; foot.text; foot.legal and foot.links |

Order on the page: 1, 2, 3, 4+5, 6+7, (plans), 8+9, quotes, 10, 11, 12, 13, 14, 15, 16. The reference's home order is
1, 2, 3, 4, 6, 4, 12, 14, 15, 16; the parts from sub-pages (5, 7, 9, 10, 11) are inserted where the data they carry
belongs (steps after their intro, the catalogue after its band, questions before the people and the doors).

## Measures used
Container 1190 (+14 gutters), text column 468, narrow column 567, two-up columns 369. Section pads 120 (100 for
two-up, links, close-to-foot). Pills: 50 radius, 13/30/12 padding, 18/25. Phone (390): header 70, side margin 22,
title 38/33, h2 32/28, h3 26/24, text 15/21, figures 2 across, cards and two-up one column, team 2 across, band 420
tall, moving line 49 px, foot 13/19.

## Font stand-ins (open licence, Google Fonts)
- Knockout (H&FJ, commercial; condensed gothic, uppercase titles) → **League Gothic** (OFL), same Alternate-Gothic family
  of forms. The oblique of the moving lines is synthesised (League Gothic has no italic).
- Simplon (commercial grotesk) → **Work Sans** 400 (OFL).

## Colour
The reference's relations: white page, #f7f7f7 sections, #111 headings and foot, one hot accent for pills, prices,
links and the sub-title. Ours: page = palette.ground; sections = ground mixed 4.5 % toward ink; headings = the darkest
palette colour that reads 7:1 on the ground; foot = the darkest palette colour when it is near black (charity1 #1a202c), else the heading colour taken 45 % toward
black (school1, from #353451); accent deepened only as far as needed for 4.7:1 on every light ground and on the pill's white words.
The reference's own orange pill with white words is about 2.9:1; ours is never below 4.6:1. Hover on pills: the
reference fades the pill to 70 %; ours mixes 18 % toward white (a 70 % fade would drop the words under 4.5:1).
Foot links on hover take a lightened accent that reads 4.5:1 on the foot.

## Motion — measured and reproduced
| measured | reproduced |
|---|---|
| header fixed, no change on scroll (0, 300, 1200 px sampled) | same |
| desktop nav dropdowns slide down: transform .4 s cubic-bezier(.455,.03,.515,.955) | the data has no sub-menus; the phone drawer uses the same curve |
| band line: CSS marquee, linear, 128 px/s (18.9 s per 2408 px); foot line 133 px/s | same speeds; duration set from the measured width by script (CSS fallback estimate without script) |
| figures count up once in view: 0→final in ≈ 1.8 s, easing out (samples every 200 ms: 0 22 43 58 71 81 88 93 94 95) | same, ease-out cubic, 1.8 s; years (1986) are not counted; the final value is in the HTML |
| images fade in on load: opacity .5 s, delay .15 s | same; only when script runs (`html.js`) |
| pill hover: background .3 s; card hover: shadow .16→.26, .3 s; nav/foot links colour .3 s; impact link arrow moves 5 px | same (no arrow: no such link in the data) |
| accordion: answer slides open ≈ .3 s, toggle plus → minus | `<details>` with a .3 s height animation by script; works without script |
| no parallax (band picture fixed in its box while scrolling: 0 px at 1500/1800/2100) | none |
`prefers-reduced-motion`: no animation, moving lines become one centred static line (the foot line is hidden), no
count-up, no fades. Without script: every picture visible, figures show final values, accordion works, phone menu
(button) does nothing — the nav is repeated in the foot.

## What is not transferred, and why
- **Boxed pictures → edge-to-edge halves** (owner's rule): the reference's 567² opening picture and its 567×378
  image-text pictures float in the page beside text. Ours run edge to edge as the full-height half of their section.
  On the phone they are full-width (opening square, image-text 4:3) instead of 346 wide with margins.
- The orange stripe drawings beside the opening picture and the SVG stripe background (brand drawing) — not taken
  (no drawn decoration; the reference's own artwork).
- Icons above the figures, social icons, cart and account icons, the e-mail sign-up form (the data has no newsletter;
  close.cta takes its place), "View all" and "View" labels (no words for them in the data — titles link instead),
  the "Thanks to our supporters" heading (their words; the strip stands without a heading).
- The news cards carry pictures in the reference; our `links` cards are type only: the photographs have no relation
  to "Our Policies" or "Charity Finances", and an unrelated photograph behind a small element is forbidden.
- hero.text2 is not shown (the reference's opening has one paragraph).

## Folding (added after the first build, CONTRACT.md "A long list is folded")
The first build set every item and every sentence out in full: charity1 14 659 px and school1 17 775 px at 1440
(2.8× and 3.3× the reference's 5 317). Now:
- **Long copy** (over 200 characters: adoption texts, step and feature texts, location notes, credentials, a person's
  lines) shows its first sentence; the rest — with a card's `rows[]` — opens in place under the accordion's round
  toggle (the reference's FAQ toggle, 28 px). Native `<details>`; nothing dropped; works without script.
- **A catalogue with more than 12 items** shows its groups as accordion rows: the group name (44 px, the accordion's
  group-title size), its count, and the client's own lowest and highest price only when every item has a price in one
  currency — otherwise the first three names. Each group opens in place to its cards or ruled rows; the group's page
  link sits at the foot of the open group. school1: 8 groups, 46 courses. charity1 has 12 adoption items, so its
  cards stay open with folded texts (the pictures carry the page).
- **A team of more than 12 people** folds the same way, one row per group (tested on a stress copy with 16 people).
- **More than 4 steps** stand in the two-up part (two centred columns, as the choose-a-run page) instead of one long
  numbered list; 4 or fewer keep the how-it-works list.
- On the phone the card picture is 346×260 (the reference's phone card picture), not square.
- Without a long list there is no picture strip inside it; school1's fourth large photograph now goes to the features
  half, which had none before.

Heights now: charity1 13 828 px at 1440 (2.6×), 17 215 at 390; school1 11 139 at 1440 (2.1×), 12 585 at 390.
charity1 stays above 2× because its twelve adoption cards keep their pictures open (about 3 800 px) and its
contact column, two doors and two credentials fill a long two-up; folding the adoption cards too would hide the
ten animal photographs that are why a visitor comes.

## Image slots (client photographs only; no made pictures)
| slot | chosen | charity1 | school1 |
|---|---|---|---|
| opening half (`hero`) | first photo ≥1200 wide, 1:1–2.6:1, not people (else people) | highland-calf | door-group (people fallback) |
| steps half (`steps`) | next ≥1000, 1.2–2.7 | sheep-portrait | team |
| band (`band`) | next ≥1500, 1.25–2.7, not people (else people) | hens-stable-door | teacher |
| catalogue cards (`item`) | the item's own img (≥369 wide) | 10 adoption pictures | none (rows) |
| price-list break (`list-break`) | after 14 ruled rows of an unfolded list, next ≥1500, 1.4–3.2 | — | — (school1's list is folded) |
| features half (`features`) | next ≥1000, 1.2–2.7 | rabbits-apple | students-outdoors |
Every picture once; `small` pictures never used in a slot; portraits only on the person they belong to.

## Checks (all on the final build)
- shots.mjs: charity1 1440 13 828 px / 390 17 215 px, school1 1440 11 139 / 390 12 585: sideways 0, distorted 0,
  one h1, errors [] — both widths, both clients.
- legible.mjs: charity1 ok (850 readings), school1 ok (791 readings; closed groups and folded texts are skipped by the tool, as they are not on screen).
- keyboard focus: 2 px accent outline, offset 3 (white on the band and foot) — checked by tabbing.
- reduced motion and no-script: checked (above).
- picture share: see needs.json `picture_share` (compared over shared sections because our page is 2.1–2.6× longer): charity1 34 %, school1 35 % against the reference's 31 % photographs only / 49 % with its drawn SVG.
- variants (scratch copies of both clients' data, rendered with this template): 1/3/5 plans, 2/9 features, 1/6 steps,
  12-word h1, 40-character button label in header, opening and close, no faq, no photographs (and no logo), and a
  combined stress copy (5 plans + 9 features + 6 steps + 12-word h1 + 40-character labels + no faq + a team over 12 people, folded): sideways 0,
  no element past the viewport edge, one h1, no distortion, no errors at 1440 and 390 for all 24 pages; legible ok on
  charity1 stress (973), charity1 without pictures (749), school1 stress (821), school1 without pictures (789).
  Heights of the variants at 1440: charity1 12 298–15 021, school1 10 282–12 332.

## Pairs (`pairs/`)
Reference above, ours below (charity1 unless named), scaled to 1080: 00 first screen at 390 (and a three-across with
school1), 01 header + opening, 02 figures, 03 image-text left, 04 numbered list (how-it-works page), 05 band,
06 priced cards (choose-a-run page), 06b school1's folded price groups against the FAQ accordion, 04 is now the roles in the two-up, 04b school1's numbered list, 07 image-text right,
08 two-up, 09 accordion, 10/10b team (type only), 11 cards, 12 doors/contact two-up, 13 close, 14 supporters + foot.
Seen differences: League Gothic sets a little narrower and lighter than Knockout; our opening and image-text
pictures fill their half where the reference's sit boxed; our catalogue cards are much longer (the client's
adoption texts run 250–350 characters where the reference's card has two lines); the stats row is shorter (no eyebrow
or link in the data); the reference's foot has social icons where ours lists the social routes as words.
