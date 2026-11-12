# omp — rebuilt from https://omp.dentist (One Manor Place, a dental practice). Niche: clinic / small professional practice

Measured 2026-11-12 at 1440×900 and 390×844 (`ref/anatomy.json`, `probe/tree-d.txt`, `probe/tree-m.txt`,
`probe/probe2.txt` = its stylesheet rules, `probe/probe3.txt` = motion and open states). Test clients: `clinic1`
(primary, German), `law1`. Nothing of the reference's words, pictures, drawing, logotype or faces is in the template.

## Halves and bands (owner's ruling, 2026-11-12)
The reference is built in **halves**: on five of its nine screens one half of the page is a photograph 720×900,
edge to edge and as tall as its section, beside type or a colour field. The owner ruled that this is allowed and
wanted (only a boxed picture floating beside text is forbidden), so the half build is reproduced as measured —
**for a photograph that can fill an upright half**: not `small`, not a portrait or product picture, at least 720×900
(not enlarged at 1440×900) and no wider than 4:3, so that the 4:5 half still shows 60 % or more of its width
(`HALF_MAX_RATIO`, `HALF_MIN_W/H` at the top of render.py; `object-position: 50% 35%`).
Where no photograph qualifies the slot keeps a **band**: the picture across the whole page at its own proportion
(never taller than the window; the opening band at most 62 % of it). No boxed picture was converted: the reference has none.
What that means for the two test clients, looked at:
- **clinic1** — no halves. Its eleven photographs are 2000×690 / 1680×580 banners: a half would show 28 % of each,
  enlarged 1.3×. Its only squarer pictures are the 400 px portraits, which belong to their people. All four slots are bands.
- **law1** — no halves. `colleagues.jpg` is 2000×1334 (3:2): forced into the opening half (`probe/law1-forced-half`,
  looked at) the man fills the picture and the woman is cut through at the right edge — it loses its subject, so it
  stays a band. `firm-group.jpg` is 1128×376: a row of thirty people, 376 px high; a half would enlarge it 2.4× and
  show a quarter of the row. It stays a band 1128 wide.
- **scratch clients with upright photographs** (butarque's two 1800×2400 put into copies of the data;
  `probe/clinic1-upright`, `probe/law1-upright`, looked at 1440 and 390): opening = type half with the name at its
  foot | photograph half, one window high; photograph half | headed paragraphs; ink field with the quote | photograph;
  photograph | pale field with the quote — the reference's four picture screens. On the phone the halves stack as the
  reference's do (type screen, then the picture 390×520; later pictures 390×390, picture before its text).

## Sections (reference → ours → data)
| # | Reference (1440) | Ours | Data |
|---|---|---|---|
| 1 | Opening 900: left half, 16 padding: sentence 56/56 serif (482 measure for the text below), mono text 15.33/23, pill button; the name as a logotype 720 wide × 240 at the bottom of the half. Right half: photograph | **With an upright photograph: the same.** Otherwise: type zone in halves — left as measured (h1 56/56, text 482 wide, buttons 40 below), right the name set large, 720 wide, bottom-aligned — and under it the picture band across the page; zone + band = one window | `hero.title` (h1), `text`, `text2`, `primary`, `secondary` (outlined pill), `note`; `brand.name`; band A |
| 2 | Header 60 high, enters after the opening and stays (sticky, −60 margin), white at 60 % + blur 10/saturate 180 %; name 30px serif left, links 15.33 mono spread over the right half | same; ground at 72 % (see contrast) | `brand.name`, `nav` (as many as fit; all in the phone menu) |
| 3 | Pale field, min. one window, 192 padding: underlined mono label, one paragraph 56/56 serif centred (1280 measure, 80 side padding), pill "MORE +" that opens a second paragraph | same | `statement.title` (label), `statement.text`: sentences up to ~300 characters stand, the rest opens under the button (clinic1 and law1 are shorter: no button) |
| 4 | Photograph half · text half: underlined mono labels over mono paragraphs, 619 measure (90 %) | **With an upright photograph: photograph half · text half (h2 56, text, then the labelled paragraphs).** Otherwise band B across; under it halves: h2 56 + text left, labelled paragraphs right, each with its link as an outlined pill | `steps.title`, `steps.text`, `steps.items[].k|title`, `.text`, `.cta` |
| 5 | Cream section, 160/80 padding, block 1216: h2 56 centred, 80 below; tiles 292 (25 % − 12), 16 apart, picture with 10 radius on top, white box 16 padding: name 30 serif, role mono, outlined pill "MORE" → sheet over the page (white 73 % + blur): role label, name 56, text; portrait 360 bottom right; cross top right | same; portraits at their own proportion (square); the pill only when the person has text, phone or e-mail; people without a portrait are ruled rows in two columns under the tiles (name 30 serif, role, text, phone, e-mail) — never a silhouette | `team.title`, `team.text`, `team.items` / `team.groups` |
| 6 | White, 60 top: left h2 56, text, pill; right ruled rows 57 high (1px rule, 30 serif, 16px plus) that open: text, then lines "name … price" | same. Rows by group when every item is priced (law1: four fee groups, each opening to its text and price lines); otherwise one such section per group with a row per item (clinic1: adults 11 rows, children 4). `features` is a section of its own unless it repeats the catalogue (clinic1's does). Plans = the same rows standing open with the price at the right; questions = rows that open | `features`, `catalogue`, `plans`, `faq`, `cta` |
| — | (the reference's headed paragraphs, part of 4) | Credentials as headed paragraphs in both halves | `credentials[].t`, `.text`, `.h` |
| 7 | Cream: h2 + pill left; right its drawn figure (640×550, animated) | The drawing is not taken and nothing stands in for it. Band C, then h2 + text + pill left; right ruled rows that say how to reach them: each location (name, address, phone, e-mail, hours, note) or the one address with hours, then phone, e-mail, other routes | `close`, `locations` or `place`, `contact` |
| 8 | Two screens: ink field with a centred quote 46.67/56 (528 measure, 96 padding) · photograph; photograph · pale field with a quote | **With upright photographs: the same two screens (field half one window high, quote centred, 96 padding).** Otherwise fields across the page, 160 padding: ink, band D, pale, cream — one quote each, name and role in mono under it. No quotes (clinic1): band D stands alone before the foot | `quotes[0..2]` |
| 9 | Foot in the ink colour, 60/16 padding: four mono columns (e-mail, phone, social · name, address · hours · copyright right-aligned); 240 below, the name 1408 wide | same; the fourth column carries the legal links; `foot.text` and `foot.legal` in a line under the columns | `place`, `contact`, `foot`, `brand.name` |

## Measures used
Type steps as the reference's rules give them: large serif `calc(8px + 3.3333vw)` (56 at 1440, 32 under 720, 68 from
1800); quote `calc(17.33px + 2.037vw)`; row/name/header serif `calc(18px + .8333vw)` (30; 24 on the phone); mono 15.33
at 1440, 14 on the phone, line 1.5; buttons 13.33 (12), padding 12.8/19.2/11.2, radius 22; outlined pill 3.2/16/1.6.
Halves 50 % with 16 padding; text measure 90 % of the column; ruled rows 58 high (reference 57); tiles 16 apart, 10
radius on the picture's top corners; breakpoint 720.
Colour relations: page = `ground`; every text, rule, button and the foot = `ink`; the reference's pale yellow field =
`accent` at 30 % in the ground (stepped down until ink on it reads 7:1); its cream = accent at 6 %; text on the ink =
accent at 4 % in the ground.
The name: broken into 1–3 lines so the block comes nearest the reference's 3:1 (clinic1: three lines, law1: two); the
longest line fills the measure (a script sets the size; without scripts an estimate from the letter count is used and
the name stands a little narrower).

## Faces
Reference: "Hue" (a light serif, commercial) and "Mono" (a grotesque monospace). Here **Newsreader 300** (display
optical size) and **DM Mono 400**, both Google Fonts, OFL. Newsreader is sharper and of higher contrast than Hue, whose
terminals are softer — seen in the pairs.

## Motion — measured → reproduced
| Reference | Ours |
|---|---|
| On load the three words of the logotype fly in from above and below (.7 s `cubic-bezier(.83,0,.17,1)`, delays 0 / .1 / .05 s), gather mid-screen, then sit at the foot of the left half | the name's lines come in over the same .7 s, curve and delays, from 60 % of their height above / below with opacity — the gathering mid-screen is not reproduced |
| Headings, buttons, each row, each quote: `.out` (opacity 0, 20px low) → `.in` over .6 s `cubic-bezier(.42,0,.58,1)` when they enter the window; once, not undone on the way up | same (IntersectionObserver, once) |
| Row opens: height .25 s `cubic-bezier(.4,0,.2,1)`; the plus's upright bar turns 90° → 180° over .3 s `cubic-bezier(.645,.045,.355,1)`; several rows may be open | same (measured on ours: 58 → 159 px in ~250 ms) |
| "MORE +" → "LESS -": second paragraph's height over .7 s | same (0 → 440 px, label changes; tested on a scratch client with a long statement) |
| Person's sheet: .3 s `cubic-bezier(.645,.045,.355,1)`, page blurred behind | opacity .3 s same curve; Escape closes; page behind does not scroll |
| Header: sticky, no change on scroll. Nothing pinned, no parallax (positions sampled at ten scroll offsets: all static) | same |
| Phone: people in a swiped row (286 tiles) with dots, active dot ×2 hollow; header is a bar with a three-line sign that opens name and links | scroll-snap row with dots; `<details>` menu, lines turn into a cross over .3 s; the bar does not grow in height over time, it opens at once |
| Button hover: none found in its rules | pill inverts over .3 s (ours; a press moves it 1px) |
| The drawn figure brushes its teeth (keyframes) | not taken |
Reduced motion: no animation or transition, everything shown (checked: 0 hidden). Without scripts: all text and
pictures visible, rows are native `<details>`, the long statement stands whole, the menu opens (by construction; a no-script render was made but not looked at).

## Checks
shots.mjs — clinic1 d `{"height":8395,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []`,
m `{"height":8226,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []`;
law1 d `{"height":12447,…,"distorted":0,"h1":1} errors: []`, m `{"height":14377,…,"h1":1} errors: []`.
legible.mjs — clinic1 `ok — 0 unreadable of 342`, law1 `ok — 0 unreadable of 756`; scratch with uprights 335 / 784;
variants 797 / 917 / 1026; clinic1 without pictures 352 — all ok.
coverage.mjs — reference 32 % `[50,0,50,26,0,8,51,43,60]`; clinic1 32 % `[56,0,56,31,46,0,56,49,9,0]` (page 1.04× the
reference: overall compared; its four pictures all present, as bands); **law1 12 %** `[58,4,36,38,36,0,…]` on a page
1.55× the reference, with only the first two of the reference's four pictures — the rule is not met, for want of
photographs; scratch law1 with four uprights 24 % `[50,0,50,29,46,…,76,27,24,51,27,0,0]`, all four halves in order;
scratch clinic1 with two uprights 32 %.
Contrast: the header's ground was raised from the reference's 60 % to 72 % so that ink on it holds over a dark picture
passing under it (worst case black behind: 6:1 for #363636). Focus: 2px outline in the text colour, 3px off (computed style read on one
focused summary). One-file pages (re-made after the disk was freed): clinic1 0.6 MB, law1 1.2 MB, `not inlined: []`.

## What could not be transferred
- For clients whose photographs are wide (both test clients) the first screen is type over a band, not type beside a picture.
- The drawn figure of section 7 and its animation.
- The logotype: a drawn wordmark in the reference, set type here; ours has descenders and three lines for a long name.
- The logo's mid-screen gathering on load; the phone header's growth in height.
- law1's second band is a 1128 px picture standing 1128 wide on the page ground, not edge to edge.

## Picture slots (`data-slot="photo-half"` / `"photo"`; the client's own photographs only, each once; no made pictures)
Halves are given out first (opening, after the statement, beside quote 1, beside quote 2), then bands to the slots left.
| Slot | Takes | clinic1 | law1 | scratch with uprights |
|---|---|---|---|---|
| A opening | half, else band: room, people, exterior … | band: behandlungszimmer | band: colleagues (cut to 62 % of the window, upper part kept) | half |
| B after the statement | half, else band: room, workshop, people | band: wartebereich | band: firm-group (1128 wide) | half |
| C before the contact rows | band only (the reference has its drawing here): exterior, landscape, room | eingang | — | band |
| D beside quote 1 / before the foot | half beside the quote, else band: detail, work, room | band: blumen | — | half (law1 copy) |
| beside quote 2 | half only | — (no quotes) | — | half (law1 copy) |
| tiles | each person's own portrait | 10 | 10 of 35 | |
Not shown: clinic1's other seven banners, the street sign (small), law1's three award badges.
Contract rule "long type sections are broken every two screens by a band" is **not built**: clinic1's type runs stay
under two screens; law1's people list (2 600 px of rows) has no unused photograph to break it.

## A button label is never cut
The first-screen label read "Termin buchen …": that is the client's own string (`cta.t` / `hero.primary.t` end in an
ellipsis — on its site the button opens a booking overlay), not a cut. Because it reads as cut, a trailing ellipsis is
now taken off every button label; nothing else of a label is shortened and no button has a fixed width or clips
(a 40-character label was tried: it stands on one line at 1440 and at 390).

## Variants (CONTRACT "A template holds for clients it has not seen") — scratch copies, `probe/variants.py`
Combined into three renders of law1 with sportbot's plans/questions borrowed: v1 = 1 plan · 2 features · 1 step ·
12-word h1 · 40-character button label · no faq; v2 = 3 plans · 9 features · 6 steps · faq; v3 = 5 plans · no
photographs at all. Each at 1440 and 390: no sideways scroll (docW = window), no element past the right edge, no
clipped button or heading, one h1, no script errors; legible ok on each (figures in needs.json). Looked at: v1's first
screen at both widths, the plans rows of v3 at both widths; the rest by the measures only.
