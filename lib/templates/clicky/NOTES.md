# clicky — notes

Reference: https://heyclicky.com (an app a person downloads), measured 2026-11-12 at 1440×900 and 390×844.
No cookie wall, no loader. Measurements are in `ref/` (`anatomy.json`, `tree-d.json`, `tree-m.json` — every box with its
type, ground, radius, shadow, transition; `rules.json` — keyframes, hover/active rules, breakpoints) and the probe scripts
in `probe/` (run with `tools/run.sh node clicky/probe/<name>.mjs`; `show.py d <y0> <y1>` prints a slice of the box tree).

The page is a desktop: everything is a window. That idiom is the build and is kept; the reference's stickers, memes,
emoticons, folder icons and name tags scattered over it are its illustrations and are not taken.

## Sections of the reference, and the data each takes

| # | Reference (measured at 1440) | Ours | Data |
|---|---|---|---|
| 0 | Menu bar 53 high, sticky, page ground, 1px line under it. Left: name 14/500 + links 14/400 at 55% ink, gap 16. Centre: the mark 54×35, squashes twice every 7s. Right: status icons, a clock, one link in the accent 14/500 | same; right side holds sign-in (grey) and the call to action (accent as a link colour). A wordmark logo stands in the centre and the name is then not repeated on the left | `brand`, `nav`, `signin`, `cta` |
| 1 | Opening, 966 high, ground dotted (1px dots every 34px, 13% ink). Centred h1 88/500/1.1/−0.03em, 20/30 line under it, two glossy pill buttons 40 high (18/27/500) each with a 12px note, block centred at y 352. Five small windows round it (r8 chrome, 12px traffic dots, 4px-radius screen, 12px caption) at x527 y25 · x996 y62 · x125 y75 · x1262 y378 · x38 y405; they can be dragged. One frame 800×440, r16, 1px ink line, from y 526 with a film in it and a caption | same positions and sizes (in 1/1440ths of the width, so the cluster shrinks with the window down to 1024); each window keeps the reference's width and its picture's own proportion, with a cap on height per slot. h1 is the client's title: 88 up to 12 letters, 72 up to 24, else 56. The large frame is `min(800, 520 × ratio)` wide and as tall as its picture | `hero.title/text/text2/primary/secondary` · first `trust[]` that is not `hero.note` under the first button · `media.video` (else first screen) in the frame · `screens`, `phones`, `photos` in the windows (those the feature rows do not show come first) · `alt` as caption |
| 2 | Three feature rows 1090×474, gap 48, alternating. Text column 320 (pad 16): a row of 12 voice bars (8 wide, 8–28 high, gap 10), a request bubble (24/28.8, r25.5, accent tints, tail) typed letter by letter, an answer bubble, then h2 20/30/500 and 16/24 text at 60% ink. Beside it a "desktop" 706×474, r16, 1px ink line, a landscape wallpaper, and on it a window 688×456 (title 12px centred in the bar) playing a film | same parts; **the wallpaper box runs under the whole row** (see "Owner's rules"). Request bubble = the step's short name, answer bubble = the step's link, window = the step's picture whole (portrait pictures give a narrow window, 422 high), window title = the brand name. A centred 56/500 heading with 20/30 text is added above the rows for `steps.title/text` — the reference has no heading there; its own section-heading anatomy (plans, questions) is used | `steps.title/text` · `steps.items[k,title,text,cta,img]` · `media.made.land[1]` |
| 3 | "Notes" window 480 wide centred, r8, 30px bar tinted 20% yellow, white sheet pad 20/24, paragraphs 20/30 at 50% ink, one phrase in ink on a 35% yellow marker, blinking caret at the end, signature row. Behind it a 1440×511 film of folder arches, faded 150px at both sides. A dotted rule 1090 wide closes the section | same; bar tint and marker in the accent; `statement.title` is the marked phrase, `statement.text` the grey paragraph; the brand's logo signs it; window title = brand name | `statement` · `brand` · `media.made.land[1]` held quiet for the band |
| 4 | Wall: a 56/500 line that runs sideways with the scroll (copies at 40%, the middle one in ink, edges masked 14%), then three columns of 353 (gap 16) of small windows r8 — 32px bar tinted 20% in six hues, sheet pad 16: name 14, handle, text 16/24/300, date, counts. The wall fades out at the bottom under a glass bar 1090×72 (20/30/500 line + accent link) | same wall and bar; the windows hold the features (title 14, text 16/24/300) and then the figures (value 28/500, label 16/24/300); bar tints from the accent and `palette.extra`; **the wall is not faded out** (it would hide the client's own features) so the bar sits under it instead of over it. `features.text` is set under the running line (20/30) — the reference has no text there | `features.title/text/items[t,d]` · `figures[v,l]` · `hero.note` + `cta` in the bar |
| 5 | Plans on a full-width animated sky, r16: white 56/500 heading, 20/30 line, monthly/yearly switch, three glass windows 350 wide (gap 16) — name 28/500, tagline 20, 12px note, dotted rule, price 56/500, 14px note, pill button, dotted rule, "includes" + three rows 16/500 with a round tick. Middle plan: accent wash over the top 40% and a "popular" badge | same; the sky is the made landscape `land[5]` with its open upper part, still; no switch (one price per plan in the data), no badge and no "includes" label (words not in the data) — the marked plan keeps the accent wash and gets the accent button | `plans.title/text/items/note` · `media.made.land[5]` |
| 6 | Dark terminal window 1082×176 straddling the sky's lower edge: mono 20/30/500 title, mono 16/24 text at 50%, grey pill button in mono; a 12px line under it | same, with a blinking block after the title | `close.title/text/cta` · `plans.note` as the 12px line |
| 7 | Questions: dotted rule, 56/500 heading (+20/30 line), list 834 wide, items white r8 pad 20 gap 8, question 20/500, answer 16/24 at 50% ink in a 480 measure, a plus that turns 45°; one open at a time, the first open | same | `faq` — left out whole when empty (automateed) |
| 8 | Foot: four columns of 249 (gap 31) with a heading each, links 16/24 at 60% ink; the name 1139×297 built from blue folder icons, scaling in from .82; 12px centred copyright | columns without headings (no words for them in the data): nav, links, sign-in + call to action, `foot.text`; the name set in a block face in the accent; legal line | `nav`, `links`, `signin`, `cta`, `foot`, `brand.name` |

Type: everything Inter, −0.03em, sizes 88 / 56 / 28 / 24 / 20 / 18 / 16 / 14 / 12, weight 500 for headings and buttons,
400 for text, 300 for the wall's text. Radii 999 (buttons, bubbles), 16 (large frame, desktops, sky), 8 (windows, cards),
4 (screens inside windows). Shadows `0 10px 24px rgba(0,0,0,.12)` (buttons, windows), `0 4px 12px rgba(0,0,0,.08)` (wall).

Phone (390, measured): bar keeps the mark, the accent link and a 32px toggle; h1 56 (ours 36 for a long title, 56 up to
12 letters) at y 84 under the bar, 18/27 line, buttons stacked with their notes, the frame 350 wide; no small windows.
Feature rows stack: text (h 24/31.2), desktop 350 wide r12 with the window on it, bars centred, request bubble right,
answer left, dotted rule between rows. Notes text 17/24.65. Running line 36. Wall one column. Plans stacked, price 44.
Terminal stacked. Questions 18 / 15. Foot two columns. Breakpoint 1023, as on the reference.

## Font stand-ins
- Inter and Geist Mono are the reference's own faces and both are SIL OFL on Google Fonts — used as they are.
- The name at the foot is drawn from folder icons on the reference (an illustration). Stand-in: the brand name set in
  **Pixelify Sans 700** (SIL OFL), a block face, in the accent.

## Colour
Client palette in, relations kept: one quiet ground for the whole page, windows' sheets one step lighter (light page) or
one step up (dark page), window chrome a left-right-left grey sheen derived from ground and ink, first button and request
bubble in tints of the accent with a dark-accent line, second button in window grey, links in the accent (mixed toward
ink until it reads at 4.6:1), one dark terminal. The three traffic-light dots are the usual red / amber / green.
The reference's greys at 60 / 50 / 40 / 30 % ink are below 4.5:1; ours are solved per palette to hold 5.0 (text) and
5.8 (captions over the dotted ground).

## Motion — measured, and what is reproduced
| Measured on the reference | Reproduced |
|---|---|
| Opening: every item fades in rising 8px, `.45s ease-out`, 16ms apart from .11s | yes |
| Small windows: grab by the bar, `scale(.97)` in `.12s ease` while held, raised above the others, stay where dropped | yes (pointer events; the whole window is the handle) |
| Mark in the bar: two quick squashes (`scaleY(.95)`) at 61% and 66% of a 7s loop | yes |
| Buttons and links: hover `opacity .8` (.15s), press `scale(.97)` (.12s) | yes |
| Feature rows: the row nearest the middle of the window is live; the others go to `opacity .3; scale(.8)` (`.35s` / `.4s cubic-bezier(.22,1,.36,1)`); nothing is dimmed before the first row is ~62% up the window or after the last has left | yes |
| Live row: bars change height about every 110ms while the request is typed (~30 letters a second, caret blinking 1s); ~.5s after the last letter the bars turn grey and stop; ~.45s later the answer bubble fades in rising 6px (`.3s` / `.35s cubic-bezier(.22,1,.36,1)`); its film plays | yes, except the film (ours are stills) |
| Arrival of sections: from `opacity 0; translate 0 22px; scale .965` to rest, `.55s ease` / `.7s cubic-bezier(.2,.7,.25,1)`, later parts .12s and .24s behind | yes, without the two delays |
| Running line: moves with the scroll, ≈0.16px per pixel scrolled (109 → −48px over 1000px), not on a clock | yes |
| Questions: one open at a time, height in ≈.16s, plus turns 45° | yes (`.2s ease`) |
| Foot name: `scale(.82)` → 1 in `.62s cubic-bezier(.2,.9,.25,1)` with opacity `.5s` | yes |
| Caret in the notes window and block in the terminal blink (1s, stepped) | yes |
| Sky: clouds drift on a canvas | no — a still photograph |
| Plan prices roll digit by digit when the switch is used | no — no switch |
| Phone: rows not in focus at `opacity .15; scale(.75)`; whole later sections held at 15% until reached | no — on the phone nothing is dimmed (readability); sections arrive with the 22px rise only |
| Reduced motion (reference keeps the dimming, drops the scale) | no load fade, no typing (requests and answers stand complete, bars still and grey), dimming without scale, running line still, film paused until pressed, no arrival fade |

## Owner's rules that override the reference
- **No picture boxed beside text.** The reference's rows put a bordered wallpaper box (706×474) with a window on it
  beside the text. Ours: the wallpaper box is the ground of the whole row (1090×474, same radius and line) and the text
  column lies over it on a veil of the page ground (96% for 400px, gone by 560px); the window stands on the open part.
  On the phone the reference already stacks the box under its text at full column width, and that is kept.
- **Screens whole.** Every window takes its picture's own proportion: the reference's fixed 688×456 window becomes
  `min(678, 422 × ratio)` wide; the opening's frame and small windows likewise. Nothing is cropped (`object-fit` is
  not used on product pictures).
- **No invented words.** Left out: the pills over sections ("the dream", "feedback", "pricing", "faq"), "play video",
  "popular", "includes", the foot column headings, the monthly/yearly switch, the clock and status icons.
- **Nothing hidden.** The wall's bottom fade is not applied (it would cover real features).
- **Contrast.** Greys darkened (see Colour); the sky gets a veil behind the heading (below).

## What could not be transferred, and why
- Stickers, memes, emoticons, folder and bin icons, name tags, the rainbow badge, the cap — the reference's illustrations.
- The folder-arch film behind the notes window and the name built from folders — illustrations; a made photograph and
  a block typeface stand in.
- Films inside the small windows and the row windows (the clients have one film; stills otherwise), the full-screen
  player that a window's zoom dot opens, the sound buttons.
- Lower-case setting of all text (the reference writes and transforms everything to lower case): treated as its voice,
  not its build — the clients' names, acronyms and prices stay as written.
- The liquid-glass SVG filter on cards and the switch: a plain `backdrop-filter: blur(12px)` instead.
- The phone's control-centre menu (glass tiles with now-playing): a plain two-column panel of the nav links in tiles.
- The 1024–1439 build was not measured separately; ours scales the opening's cluster by the window width.

## Image slots
**One picture family: `land`** (pass of 2026-11-12, CONTRACT.md "One picture family per page"). What the reference repeats
is a single landscape wallpaper — the same one behind every feature row — and then its sky behind the plans. Before this
pass the rows took four different landscapes and the plans took `made.sky` (two families).
1. **Row wallpaper** (`.desk img`, `data-slot="wallpaper"`, 1090×474 at 1440, 350 wide on the phone): `made.land[1]` in
   every row, seen through a different part each time (`object-position` 62 % / 38 % / 82 %), `cover`, lazy, `alt=""`.
   Without `made.land`: the plain sheet colour.
2. **Notes band** (`.band img`, `data-slot="band"`, full width × 511): the same wallpaper at 42 % toward the ground,
   faded to the ground on all four sides (it was the dense water photograph `land[2]` at full strength; the reference
   has light objects there). No text lies on it. Without it: no band.
3. **Plans backdrop** (`.sky img`, `data-slot="backdrop"`, full width, its own proportion, fading out downward from 40 %):
   `made.land[5]` (wide, empty upper third), else `land[0]`. Heading and line lie on its open upper part under a veil of
   the page's own tone over the top 380px (fading to 640px), solved from the picture's mean. Without it: plain ground.
4. A dark page never takes a `tone: light` land picture for any of the three (`family()` in render.py).
5. **Small windows and the frame of the opening**: client screens, phone screens, book pages. No made picture.
6. No picture: the wall's avatars (no people), the plan cards, the terminal, the foot.

Picture share (`tools/coverage.mjs`, 1440): reference 38 % `[23,45,46,61,2,76,47,0,44]`, 3 screens with a wide picture ·
sportbot 37 % `[23,37,73,67,24,44,47,0,0]`, 4 wide · automateed 46 % `[23,44,73,69,16,71,19]`, 4 wide. The reference's
last screen is its name built from folder pictures; ours is type. At 390: reference 35 %, sportbot 26 %, automateed 32 %
— the reference's phone shows its sky at 67–100 % over three screens; ours fades the backdrop out behind the cards.

Readability (`tools/legible.mjs`): sportbot `ok — 0 unreadable of 465`, automateed `ok — 0 unreadable of 283`.
One real failure was found and fixed: the name at the foot in the accent was 2.36:1 on automateed's cream; it is now
the accent mixed toward the ink until it holds 3.1:1 (`--mk`).

Dimmed rows: at 1024 and wider the rows not in focus still stand at 30 % (the reference's device) — a row is 474 high,
fits the window whole, and is at full strength whenever it is the one nearest the middle. On the phone a row is taller
than the window, so its heading would stand at 15 % in the lower half of the screen before the row became the live
one: **no row is dimmed below 1024** any more. Without scripts no row is dimmed at all (the rule needs `.js`).

## Checks
`tools/shots.mjs`, final run:
```
(heights unchanged after the 2026-11-12 pass)
sportbot   d {"height":7604,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
sportbot   m {"height":9583,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
automateed d {"height":6139,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
automateed m {"height":7359,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
```
`probe/audit.mjs` (reduced motion on; every visible text against the lightest and darkest rendered pixel behind it,
4.5:1 or 3:1 from 24px; a ≥2px outline on every Tab stop; reduced-motion state; a no-script screenshot):
sportbot worst 4.51 at 1440 (the 56px plans heading on the sky; all body text ≥ 4.5) and 4.50 at 390, 0 below the
line, 35 / 29 Tab stops all ringed; automateed worst 5.12 / 5.13, 0 below, 21 / 19 stops all ringed; nothing hidden,
no animation running, no film playing under reduced motion; without scripts every section stands complete
(`out/<client>-nojs.jpg`). Dimmed feature rows (6 / 4 texts at 30% opacity) are skipped by that audit — see Unsure.
`probe/widths.mjs`: no sideways scroll and no small window over the opening's text at 320, 360, 414, 768, 1023, 1024,
1180, 1280, 1680, 1920. `probe/ours.mjs`: dimming, typing, answer, drag, running line and questions sampled on our page.
Render: 1–4 ms per client.

A full-page screenshot taken straight after load (headless) shows the small windows and late sections not yet arrived —
the load fade and the arrival transitions have not been ticked; the stepped shots show them.

## Unsure
- Feature rows out of focus stand at 30% opacity at 1024 and wider (not on the phone any more). `legible.mjs` does not
  judge text under 40 % opacity, so the dimmed neighbours are outside the gate; each is full when it is the live row.
- One wallpaper three times (as on the reference) may read as "the same picture again"; the crops differ, the picture does not.
- Whether the wallpaper under the whole row satisfies "never boxed beside text": the window with the product screen
  still stands beside the text, on the same ground.
- Features as wall windows carry a 14px title — small for a feature name; it is the reference's size for a name there.
- Figures share the wall with the features (the reference has no figures section); they fall in the last column.
- `trust[]` is used once (one string under the first button); the other strings are not shown. `links[].d` and
  `hero.kicker` are not shown.
- The heading above the rows and the text under the running line have no counterpart in the reference.
- Captions under the small windows are the pictures' `alt` texts; the reference's are file names.

## Soft sections absent (2026-11-12, branch never-zero)
A floating window of the opening keeps its caption to one line, cut with an ellipsis at the window's width (the whole
alt stays in `title`). A client without product screens fills the windows with photographs, whose alt texts run longer
("A Year of Small Gardens — cover" under a 70 px upright window): wrapped to three lines it lay over the h1 at 1440
(stress `minimal` on quillmoor). With steps, close or features absent the page drops those sections whole and holds
(`python3 lib/templates/stress.py --sweep clicky`).
