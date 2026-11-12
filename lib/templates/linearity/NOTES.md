# linearity — notes

Reference: https://www.linearity.io (home), read 2026-11-12 at 1440×900 and 390×844. No cookie wall appeared; nothing
was accepted. Measurements are in `ref/` (`anatomy.json`, `outline-d.txt`, `outline-m.txt`, `motion-d.json`, walk and
`at/` screenshots); the scripts that made them are in `probe/` (run with `tools/run.sh node linearity/probe/<name>.mjs`).

The reference sets every measure in rem and scales the root with the viewport: 13.714px at 1440 (= 100vw/105), 16.64px at
390 (= 100vw/23.4375). The template does the same, so its rem values are the reference's own.

The reference is 28 650px high at 1440 because four stretches are held while the scroll drives them. **Ours is 13 936
(sportbot) / 11 603 (automateed)** since the pass of 2026-11-12 — see "Holds". `tools/shots.mjs`
stops after 14 screens, so the whole page was walked with `probe/walk.mjs` (reference) and `probe/walkours.mjs` (ours).

## Sections of the reference, and the data each takes

| # | Reference (measured at 1440) | Ours | Data |
|---|---|---|---|
| 0 | Header, fixed, clear, 98px: logo x34, links 13.7px, text link + glass pill right. Leaves going down, returns going up | same; a veil of the ground behind it once the page has moved (the reference has a blur layer there) | `brand`, `nav`, `signin`, `cta` |
| 1 | Opening, held. h1 in two rows: a grey sentence 34.3/500 (white 42 %) with three glass pills whose words change, then the claim 45.3/700. Glass panel 489×141 r20.6 in which a prompt types itself, round hot button 31px (**not built**: with a client's sentence in it the panel looked like an input that is not one — `hero.text` now stands as a plain centred line, 20.6px, and there is no panel and no round button). Note 10.3px, 243–404 wide. Glass pill + hot pill (41 high, 12px/500). Bouncing arrow with three words. Bottom bar on a hairline: play tile 58×41 + shimmering label · logo marquee 583 wide · award line right | same anatomy without the panel. Grey row = kicker + **one** pill; bar = film button · trust words as the marquee · the note | `hero.kicker/title/text/text2/primary/secondary/note` · `steps.items[].k` (pill) · `media.video` · `trust[]` |
| 2 | Same hold, second scene: small label, 44.6px three-line heading whose first word changes three times (with a drawn underline), three dots, a 13.7px grey paragraph 531 wide; 22 tiles of made work rise past in four lanes | one heading and one paragraph (no three states in the data, so no dots); the client's pictures rise past in the same lanes | `statement.title/text` · every picture in `media` once |
| 3 | Held 6 vh. App window 677×480 (glass, r17) starts centred, moves 260px left while the text arrives: label, 44.6 heading, two pills, three rows (41px icon tile, 13.7/500 title, 12px text) of which one is open; the open row advances every 1200px and a line runs round its icon tile | same; the tile carries the step's number; the step's own link is a plain underlined line in the open row (not on the reference) | `steps.title`, `steps.items[k,title,text,cta,img]` · `hero.secondary/primary` for the two pills |
| – | "The difference": centred heading, two framed pictures 366×530 with captions | **left out** — the data has no second headed block for it (see below) | – |
| 4 | (no figures anywhere on the reference) | a row of the reference's plan cards (333 wide, r20.6, corner light) carrying number 44.6 + label 12 | `figures[v,l]` |
| 5 | Held ~13.6 vh. A row 7 100px long moves sideways at 0.891px per px scrolled, starting 607px before it sticks: three panels, each a label, 44.6 heading, grey text, two pills, then (247 on) a diagram 405 high; panels 617 apart. A thick green ribbon is drawn through it | same run; each panel = the link's sentence as the heading, the link's name as its one glass pill, and one screen 405 high. No ribbon (owner: no drawn strokes) | `links[t,d,h]` · `media.screens[i]` |
| 6 | End of the same row, 1013 on: a wheel (ring 662, hub 322 with the mark, eight tiles on a 591px radius, 251–386 high) turning 45° per 900px; right column 504 wide: label, 44.6 heading with a changing word, two pills, five rows as in 3, advancing every 900px; fades out over the last 600px | same; no changing word (none in the data); hub = the client's logo | `features.title/items[t,d]` · pictures from `media` · `brand.logo` |
| 7 | Plans: 44.6 heading, 13.7 grey text 504 wide, monthly/yearly switch, four cards 333×720 r20.6 pad 34/38: name 20.6/500, line, price 44.6, "per month" 12, pill, bullets 12px with 5px accent dot; then a wide glass bar r20.6 with a line and a pill | same; no switch (one price per plan in the data); cards centred; the bar carries `plans.note` | `plans.title/text/items/note` · `cta` |
| 8 | Questions: left 434 wide at x121 (label, 44.6 heading, text), right 677 at x642: rows 60 high on hairlines, 15.4px, 26px round plus; first open | same, no label; left out whole when there are none | `faq` |
| 9 | Close: 75.4px two-line heading, 15.4 grey line, then the typing panel again | heading, line, then the hot pill (the panel would type the same sentence twice) | `close` |
| 10 | Foot: download tiles, eight link columns 243 wide with headings, language + socials row, the wordmark 1371 wide whose letters can be dragged, legal row 12px at 40 %, logo marquee | three columns without headings, the name set across the page, the small print, legal row | `nav`, `links`, `signin`, `cta`, `brand.name`, `foot` |

Type (1440 → 390): claim 45.3/700 → 29.5 · grey row 34.3/500 → 25 · headings 44.6/400/1.0 → 29.1 · close 75.4 → 37.4 ·
card name 20.6/500 · question 15.4 · body 13.7/1.5 → 14.6 · small 12 → 14.6 · note 10.3 → 12.5. Margins 34 → 21.
Pills 41 high, 12/20.6 padding, a 5px halo ring. Section padding 86–123 → 67.

## Font stand-ins
- Headings: the reference uses **Acid Grotesk** (commercial). Stand-in: **Bricolage Grotesque** 400/500/700 (SIL OFL,
  Google Fonts) — a grotesque with the same slightly eccentric, tight drawing. Its lower-case is a little narrower.
- Text: the reference uses **Inter**, which is open (SIL OFL) and is used as is.

## Colour
Client palette in, relations kept: one ground for the whole page; ink; grey text = ink at 55 % raised until it reads
4.7:1 on the ground and on glass; the opening's grey row = ink at 42 % raised to 3.1:1 (large type); glass = ink at
5–10 % with an inner light and a hairline whose highlight goes round in 4s; one hot colour (the accent) on the main pill,
the round button, bullets and the caret, with a lighter inner light. The accent is pushed away from its label until
the label reads 4.6:1.

## Motion — measured, and what is reproduced
| Measured on the reference | Reproduced |
|---|---|
| Header: `transform .3s`; away after ~220px going down, back going up | yes |
| Pills in the opening row: one changes every ~3.3s; out = opacity 0, blur 5.5px, 5.5px down; in from 5.5px above; `opacity .26s, transform .36s cubic-bezier(.32,.72,0,1), filter .3s` | yes, on the one pill |
| Panel: ~25ms a letter, retyped whenever a pill changes | no — the panel is not built |
| Glass hairline highlight: conic gradient, `4s linear infinite`, paused on hover | yes |
| Pill labels: two copies, roll up 100 % on hover, `.65s cubic-bezier(.785,.135,.15,.86)` | yes; a press scales to .97 (the reference has no press state — the owner's "page answers a press") |
| Arrow: `bounce 1s infinite`; label shimmer `6s linear infinite`; marquee `19s linear infinite` | yes; the shimmer is the label's colour going to the ink and back once in 6s, not a light sweeping across clipped letters (the sweep painted the letters as a background, which the readability gate reads as a failure) |
| Opening hold (scroll in px at 900 high): content opacity 1 → 0 over 500–1100, block scale 1 → .6 over 450–1200; second scene in over 1200–1500; tiles rise from 900 on at 1.07–1.37× the scroll (edge lanes slower, inner lanes faster); scene out over the last 700; the next section slides up over the last 900 | same order, shortened (see "Holds"): content out over 250–600, statement in over 520–720 and out over the last 560–260, tiles rise from 350 on and fade with the statement; hold 1800 |
| Steps hold: window x 260 → 0 over 90–1140 (ease in-out), text opacity over 390–1290 with a 40px slide; rows at 1300 + 1200·i; open row `grid .5s linear`; line round the tile follows the scroll | shortened (see "Holds"): picture and text arrive while the section rises into the window and are complete when it sticks; rows at 250 + 420·i; pictures cross-fade .5s |
| Sideways run: 0.891px per px, begins 607px before sticking; wheel 45° per 900px; rows every 900px; section fades over 600px while the plans rise over it (−60dvh) | shortened (see "Holds"): 1.6px per px, panels 14rem apart (were 45), wheel 45° and one row per 330px, fade over the last 200px, overlap −30vh |
| Questions: height by `grid-template-rows`; plus turns 45° | yes (.3s; the reference's duration was not read) |
| Phone: opening still held with tiles; steps, panels and wheel rows become swipe rows with dots | yes (scroll-snap rows; dots follow) |
| Reduced motion | no holds, no sideways run (panels stack, every row open), no drift, marquee wraps and stands still, panel shows its line, pill stays on its first word; header still leaves and returns, without the slide |
| Scripts off | everything stands in plain flow and is visible; swipe rows still swipe |

## Owner's rules that override the reference
- **No drawn strokes**: the green ribbon through the sideways run and the brushed underline under the changing words are not built.
- **No coloured glow in place of a picture**: the reference has a moving WebGL aurora behind the page and a glowing line
  round the viewport. Ours: the client's made `sky`, the one picture family of the page, in five places (see "Image slots"). No edge line.
- **No picture boxed beside text**: the steps window is a glass box on the reference; ours is the step's picture standing
  free, whole, at its own proportion (at most 677×480). Panel pictures and wheel tiles likewise stand free and whole.
- **Screens whole**: every picture is `auto × auto` inside a maximum box; nothing is cropped.
- No words invented: no small labels above headings, no "scroll" words by the arrow, no "popular" tag, no column
  headings in the foot, no monthly/yearly switch.

## What could not be transferred, and why
- The aurora's movement: it is WebGL and rendered only in some headless runs, so its path could not be sampled.
- "The difference" section: it needs its own heading, text and two captioned pictures; every heading in the data
  already has a place. Its frame survives only as the plan card.
- The three changing states of the second scene and the changing word in the wheel heading: one statement, one title.
- Lottie product animation in the steps window, the diagrams in the panels: theirs; ours are the client's stills.
- Logo marquees, award badge, avatars in pills, icons in the rows (numbers instead), download tiles, socials, language switch: no data.
- Dragging tiles and wordmark letters with the pointer, hover caption on tiles: not built.
- Tablet (768–1023) uses the phone build with capped type; the reference's tablet build was not measured.

## Holds (pass of 2026-11-12 — the owner: software sites must be functional, not constant scroll)
All in px of scroll at a 900-high window (scaled by height/900), 1024 and wider only; the phone has no holds but the opening.
| Hold | Reference | Before | Now | What sets the least |
|---|---|---|---|---|
| Opening + statement | 4410 | 2300–2900 | **1800** | two scenes: the opening leaves by 600, the statement stands whole from 720 to 1240, out by 1540 |
| Steps | 1300 + 1200 a step + 300 (5200 for three) | the same | **250 + 420 a step + 120** (1630 for three) | the entrance no longer costs scroll (it happens while the section rises); each step is open for 420px |
| Sideways run | 0.891px sideways per px; panels 45rem apart | the same | **1.6px per px; panels 14rem apart, 6rem inside, 22rem before the wheel** | every panel still crosses the whole window |
| Wheel | 900 a feature + 700 | the same | **330 a feature + 260** | each row is open for 330px |
Page at 1440: sportbot 29 233 → 13 936, automateed 25 228 → 11 603. What is left of the length is the sideways run
(four panels and seven features for sportbot ≈ 5 400px of hold).

## Image slots
**One picture family: `sky`** (CONTRACT.md "One picture family per page"). The reference repeats one thing: a moving field
of coloured light behind the whole page, showing at the window's edges in every section. Ours is the client's made sky
in each open space of the page, another crop each time, every one an ellipse that ends inside its own box (no edge):
| `data-slot="sky"` | Where | Crop | Text near it |
|---|---|---|---|
| `.sk-hero` | behind the opening, strongest upper right, veiled to the ground, drifting; fades with the statement | centre top | header and headline in the ink; veil .3 at the corner (.55 on the phone, where the header pill sits on it) |
| `.sk-how` | rises from the lower edge under the steps' picture (held section only, 1024+) | left 70 % | none — it ends left of the text column |
| `.sk-caps` | lower left corner of the sideways run (held section only, 1024+) | right 40 % | none — panels and rows stand above and right of it |
| `.sk-plans` | behind and round the plan cards and the note bar | centre 30 % | the cards and the bar are **solid** when the sky is there (ground + 5 % ink, no blur): small grey text cannot stand on a sky |
| `.sk-close` | between the closing button and the foot's links | centre 60 % | the button (solid); the line above and the links below are outside the ellipse |
No sky → none of these is rendered and the page stands on its plain ground; a dark page skips a `tone: light` sky.
| Slot | Reference shows | Takes | Still without a picture |
|---|---|---|---|
| tiles of the second scene | 22 pieces of made design work, 171–248 wide | client's phones, photos, screens, each once | a client with no media gets the statement alone |
| steps window | product animation | `steps.items[i].img` | step without `img`: empty place |
| panel visual | UI diagrams 405 high | `media.screens[i]`, else any picture | none in media → text-only panel |
| wheel tiles (8) | made design work, 251–386 high | the same pool of pictures, wrapping round — with fewer than 8 pictures the same one can be on the wheel twice (opposite sides) | – |
| hub | the reference's mark | `brand.logo` | – |
`land`, `blur`, `sheet`, `field` are not used.

Picture share (`tools/coverage.mjs`, 1440): reference 6 % `[0,5,30,31,13,0,…,78,24,0,…]`, 1 screen with a wide picture
(its field of light is a fixed canvas, which the tool leaves out, so this counts only its tiles and wheel) · sportbot
24 %, 5 wide · automateed 28 %, 4 wide (before the pass: 5 %). Held sections read as zeros in that tool; they were
looked at viewport by viewport instead (`out/walk/`, every 450px).

Readability (`tools/legible.mjs`): sportbot `ok — 0 unreadable of 344`, automateed `ok — 0 unreadable of 236`. On the
way there: a first try with the sky fixed behind the whole page failed on small grey text wherever it passed the clear
part (3.3–3.9:1) — hence the placed ellipses and the solid plan cards; the rolling label's hidden second copy was read
as a second text under the button (now `visibility:hidden` until hover).

## Checks
`tools/shots.mjs`, run of 2026-11-12 after the pass:
```
sportbot   d {"height":13936,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
sportbot   m {"height":8190,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
automateed d {"height":11603,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []
automateed m {"height":6739,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []
```
`probe/audit.mjs`, final run (`out/audit.txt`): both clients, both widths, with and without reduced motion — 0 texts
under the contrast floor, 0 Tab stops without a ring or off screen, 0 script errors, no sideways scroll. `audit.mjs` hides the
text, screenshots, and measures each visible text's colour against the pixels behind it (21 points per text, 4.5:1, or
3:1 from 24px) every 0.62 screen down the page, with and without reduced motion; walks 60 Tab stops for a ≥2px outline
that is on screen; saves a scripts-off full page to `out/walk/`. Limits: texts mid-fade (opacity < .97) and the moving
marquee are skipped; scripts-off was looked at, not measured, and its lazy pictures do not load in a full-page capture.

## Unsure
- The opening pill cycles the step names beside the kicker — a pairing of mine, not stated by the data.
- On sportbot the sky is a dark nebula and its ellipses under the steps and in the run are faint; on automateed they are plain to see.
- 420px a step and 330px a feature are judged by eye from stepped screenshots, not by a person scrolling.
- Panels use a link's sentence as a 44px heading; that is large for a line like "Open your workspace."
- Figures have no counterpart on the reference.
- Glass on a light ground (automateed) reads grey rather than luminous.
- Whether free-standing pictures beside the text in steps and panels satisfy "never boxed beside text" to the owner's eye.


## Fixes for the engine's gate (2026-11-12)

The h1 is the client's hero title whole. The kicker and its changing pill words stand in a line above it (a <p>), outside the heading; the look is unchanged. Without a title the brand name is the h1. On a phone a pill never runs past the box it stands in: a label longer than the box takes a second line, and the hover roll's second copy is not drawn there (no hover on a phone).
