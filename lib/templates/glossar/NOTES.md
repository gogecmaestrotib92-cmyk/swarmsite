# glossar — notes

Reference: https://glossar.app (home page), measured 2026-11-12 at 1440×900 and 390×844 with `tools/anatomy.mjs`,
`tools/shots.mjs` and own Playwright probes in `probe/` (`tree.mjs` box/style tree, `scroll.mjs` sampling every 60–100 px,
`time.mjs` and `press.mjs` for load, arrivals, hover, press, menu, questions). Raw captures: `ref/`, `probe/`.
Three kinds of statement are kept apart: **measured** (read off the live page), **chosen** (my decision where the
reference gives no answer, the data has another shape, or the owner's rules override it), **not verified**.

## Sections of the reference, in order, and the data each takes

| # | Reference section (measured) | Data | Left out when |
|---|---|---|---|
| 0 | Fixed bar, 480 wide, centred: a full-ink strip with the name in the middle and a two-line menu button; under it an accent strip with a label and an arrow tile. The strip opens into a list of links | `brand.name/home`; list: `nav[]` + `signin`; accent strip: `cta` | menu button and list without links; accent strip without `cta` |
| 1 | Opening, centred: app mark 86, display line, two lines of muted text, one pill with an accent chip inside it | `brand.logo`, `hero.title` (h1), `hero.text` + `hero.text2`, `hero.primary`; chip = `hero.secondary` | no `hero.title` |
| 2 | The stage: one panel held on screen; a statement at the left behind a thin rule that fills, the phone in the middle, a short muted remark at the right; four steps | `steps.items[]`: statement = `text`, remark = `k` / `title`, screen = `img` | no step items |
| 3 | Statement in two tones (first sentence ink, rest muted) and a row of coloured pills, in the middle of an 860 square | `statement.title` / `statement.text`, pills = `trust[]` | neither |
| 4 | Showcase: head; a rounded picture panel 816×621 with a device on it and a second screen 340 wide to the right; under it a small head beside a muted text | `features.title`; `media.screens[0]` on `media.made.land[1]`; second = first upright picture in `media.phones`/`photos` not used by a step, else `screens[1]`; pairs = `features.items[t,d]` | no feature items and no screens |
| 5 | Panel: two-tone centred head, three dark square cards that close like a fan | head = `hero.kicker` / `hero.note`; cards = `figures[v,l]` | no figures |
| — | (no pricing section in the reference) | `plans` — built from the reference's own parts, see below | no plan items |
| 6 | Panel: centred head, questions in two columns of tiles | `faq.title/items[q,a]` | no faq items |
| 7 | Close, centred: mark 90, two-line head, the pill | `brand.logo`, `close.title`, `close.text`, `close.cta` | no `close.title` |
| 8 | Foot: a panel with a small picture-link home, two rows of small tags, one line of small print; it stands on the top of a wide landscape | `brand`; tags = `links[].t` then `foot.links`; `foot.legal`, `foot.text`; backdrop `media.made.land[5]` | never |

Not shown (the reference has no place for them): `steps.title`, `steps.text`, each step's `cta`, `features.text`,
`links[].d`, `logos`, `quotes`, `media.video`, screens beyond the two used, the theme switch.
sportbot gets all sections; automateed gets all but 6 (no faq).

## Measures used (measured at 1440 unless marked; phone values at 390 in brackets)

- Grounds: page on its ground; panels = 4 % ink (reference #f5f5f7 on #fff); muted text = 57 % ink (#6e6e75), raised
  here until 4.6:1 on page and panel (**chosen**); bar and word cards in full ink with ground-coloured text; accent on
  the buy strip and the chip.
- Bar: 480 wide, 14 from the top [full width less 12, 12 from top]; strip 58 high radius 12 [52]; name 22/1 weight 500
  [19]; menu lines 28 wide; accent strip 54 high radius 12, 6 below, label 15 weight 500 at 22 from the left, tile 40
  radius 7 at 18 % [50 high radius 10, tile 36]. Open: radius 18, inner list panel radius 12, rows 62 high, 22 weight
  460, hairlines between, page dimmed at 32 % black. 132 px reserved above the page [124].
- Opening: 116 under the reserve [96]; mark 86 radius 20 [~76] — the client's logo is drawn inside that box at its own proportion and with its own corners (see the pass below); 28 between blocks [26]; display 40/48 weight 510
  [31/37]; 17 to the text [14]; text 17/25.5 weight 480 muted; pill 48 high, 6 inside, label 15 weight 510 −.01em at 22
  from the left [18], chip 36 high with 14 at the sides. 136 to the stage.
- Stage: section = 100vh + 90vh per step (reference 4140 = 900 + 4 × 810); panel 23/24 from the edges, radius 40;
  statement 24/28.8 weight 510 in a 344 column at x 113, rule 2 × 86 at x 82; phone 760 high at 900 (84.4 % of the
  height); remark column 317 at the right. [Phone: one panel a step, radius 28, 52×26 inside, 20 apart; statement
  21/27.3 centred; 48; the screen ≤ 655 high; 48; remark 20/26 muted.]
- Statement + pills: block 680 wide in the middle of 860 [660]; 32/38.4 weight 510 [26/31.2]; pills 54 high, 12 apart,
  radius 999 [two columns, 46 high, 10 apart]. Pill text is 22 px here against 26 measured — the reference's pills hold
  two characters, ours a phrase (**chosen**) [17 against 20].
- Showcase: 80 at the sides [16]; head 32; 41; panel 816×621 radius 24 beside a 432 column, 32 gap; second screen 340
  wide, right-aligned; 32; pairs on 244 | 540 with 32 gap: 22/33 weight 510 beside 20/30 weight 510 muted [one column,
  panel 358×503 radius 32, 44 gap, centred, text 17/25.5]. 250 to the next panel.
- Panels: edge to edge, radius 40, 210 above the head, 230–250 below [88×24–32, radius 32–40]; 80 between panels.
- Word cards: 248 square, radius 36, 24 inside, gradient from 20 % lighter to full ink, 1 px edge; overlap 12; 96 under
  the head; value 30/1.08 weight 590; soft shadow 0 4 95 at 35 % under the middle card [stacked, 4 apart].
- Questions: two columns of 620, 40 between, 16 between rows, filled column by column; tile radius 12; button 20×28,
  17/20.4 weight 510; round 28 with a 2×12 plus; answer 16/24 muted, padding 12 72 24 28 [one column, 18, 16/19.2,
  15/22.5].
- Close: block centred in 740 [560]; mark 90; head 34/40.8 [26]; 120 above, 180 to the foot.
- Foot: panel 40 from the sides, radius 24, 56/48/48 inside; tags 30 high, radius 6, padding 3 56 4 8, 14/21, 6 apart,
  rows 8 apart; small print 14/21; picture starts 178 below the panel's top and shows 633 under it [570].
- Focus ring: the reference leaves the browser's default; here 2 px solid ink, 3 px offset (**chosen**, for visibility).

## Typeface stand-in

| Reference | Stand-in | Why |
|---|---|---|
| SF Pro (system face, Apple licence), weights 400–590 incl. 460/480/510 | **Inter** variable 400–700 (SIL OFL, Google Fonts) | the open neo-grotesque drawn for the same screen use; its weight axis allows the same in-between weights (480, 510, 590) |

## Motion — measured, and what was reproduced

| What | Measured on the reference | Here |
|---|---|---|
| Load | mark: opacity + 22 px + scale .7→1, .75s cubic-bezier(.19,1,.22,1); head words rise 110 % out of a mask one after another (≈ 60–70 ms apart), .7s same curve; text lines the same, .72s; the pill opens from a 48 px circle in .64s cubic-bezier(.2,.9,.28,1), its label fades up after. First movement ≈ .85 s after navigation | same order, curves and durations; the pill opens by a clip from 48 px. Starts at once (the reference's ≈ .85 s is its hydration, not a designed delay — **interpretation**) |
| Bar | leaves (−148 px, opacity 0) once the page moves down past ≈ 80 px; returns on the first move up; transform .42s, opacity .18s, cubic-bezier(.16,1,.3,1) | same; it also returns when keyboard focus enters it (**chosen**) |
| Menu | strip grows in .58s cubic-bezier(.16,1,.3,1), radius 12→18, the list fades in .28s and rises 8 px; the two lines of the button close to one; the accent strip is pushed down; page dimmed in .38s | same. The reference marks the current page with a small accent square — not reproduced, the client's links all lead elsewhere |
| Buttons | hover: an inset wash (13 % white on the ink pill, 8 % black on the accent strip), .2s; the strip's arrow leaves to the right while a second enters from the left, .3s cubic-bezier(.5,.5,.3,1) after .1s. Press: no state beyond hover | same; no press state added |
| Stage | pinned for 4 × 810 px. Nothing is eased — every value follows the scroll. Statement words stand at 18 % and go to 100 % one by one, one per ≈ 15 px, from the step's start; remark words the same from ≈ 66 % of the step; the statement leaves over the last ≈ 10 % (36 px up, fading) and the next arrives over the first ≈ 7 % (36 px from below); the rule fills linearly over the whole pin; the screen cross-fades at the step boundary over the same span | same numbers (checked: opacity .87 at +740 px and .25 at +790 px of an 810 px step; reference .87 at +740, .13 at +800). Every step has its own screen, so every boundary cross-fades (the reference keeps one wallpaper for three steps and changes a widget inside it — its own product, not rebuilt) |
| Stage on the phone | not pinned; each panel arrives once: opacity, 22 px, scale .96 | same; duration .68s **not measured** (taken from the desktop panel's transition) |
| Statement + pills | lines rise out of masks ≈ 100 ms apart, ≈ .7s; pills follow ≈ .4 s later, 18 px + opacity, ≈ 40 ms apart | same |
| Showcase | panel picture scaled 1.12 and drifting −60→+60 px with the scroll; the second screen −58→+58 px; head words rise | same, tied to each element's passage through the window |
| Word cards | scroll-linked over ≈ 490 px, done when the row reaches mid-window: outer cards from ±236 px, scale .92, opacity .84, 8 px low; the middle one from scale 1.2 | same; with an even count there is no middle card and none is enlarged. Phone: cards arrive once, scale .88 + 12 px, opacity .55s / transform .7s cubic-bezier(.16,1,.3,1) |
| Questions | one open at a time; height .38s cubic-bezier(.16,1,.3,1), opacity .24s; the plus turns to a minus in .3s; tile darkens on hover .32s | same |
| Close | mark, words (≈ 40 ms apart), then the pill, once on arrival | same |
| Foot picture | opacity 0→1 over ≈ 300 px as the foot arrives; scale 1.15→1 over the last ≈ 830 px of the page | same |
| Theme switch | light / dark / system button top right | not reproduced: the client's palette is the page |
| Reduced motion | not measured | all animation and transitions off; the stage is not pinned (the phone build at every width); every arrival is shown at rest; no drift |
| No script | not measured | everything visible; the stage is the phone build; questions show their answers; the bar is not fixed and its list opens on hover/focus |

## What could not be transferred, and why

- **The price in the buttons.** The reference's chip and the right end of its accent strip carry the price. In the
  opening the chip takes `hero.secondary` as a link of its own (a price there would misstate a free sign-up); in the
  plans the chip carries each plan's `price`, exactly as the reference does; the accent strip has only label and arrow.
- **Plans.** The reference sells one thing at one price and has no pricing section. **Chosen**: a panel of the
  reference's kind with its tiles (radius 12 on the panel ground), name 22, line and rows 16 muted with hairlines, and
  the reference's pill with the price in the chip; `per` beside it; `note` under the grid. The unmarked plan's chip is
  neutral, the marked one's is the accent. This section has no pair.
- **Level pills.** Six two-letter level names in six hues there; `trust[]` phrases here, in the client's accent and
  palette extras (text is whichever of ground/ink reads at 4.5:1; colours within 1.35:1 of the page are skipped), so
  the row wraps to several lines.
- **Word cards.** Level badge, word, gloss and phonetics there; `figures` here: value at the top, label at the bottom
  in the phonetics size (17). No badge — there is no datum for it. The head over them is `hero.kicker` with `hero.note`.
- **Showcase device.** The reference crops a phone at the panel's lower edge. Owner's rule: the screen stands whole,
  at its own ratio, inside the panel (56/48 clear), on a made landscape in place of the reference's painted one.
  The reference has one pair of small head + text; all `features.items` are set as such pairs.
- **Stage screens** are shown whole at their own ratio: phone shapes with the reference's rounded corners, other shapes
  (book covers) with a 12 px radius so nothing of the picture is cut.
- **Foot.** The stamp picture, pretzel and author line are the reference's own; the brand mark stands where the stamp
  links home, `links` and `foot.links` are the tags, `foot.legal` the small line. The reference's paper texture is not taken.
- **Icons**: only a plain arrow in the accent strip's tile (drawn here) and a CSS plus/minus.

## Image slots

| Slot (`data-slot`) | Where | Takes | Without it |
|---|---|---|---|
| `showcase-backdrop` | `<img class="bk">` filling the 816×621 panel (358×503 on the phone), cover, scaled 1.12 | `media.made.land[1]` (valley) — both clients have it | the panel's plain 4 % ground; `data-slot` then sits on the panel |
| `foot-backdrop` | `<img>` under the foot, full width, ≈ 633 high visible (570 on the phone), cover, fading out of the page ground at its top | `media.made.land[5]` (wide, quiet upper third) — both clients have it | no picture and no extra height under the foot panel |

No text lies on either picture (the foot's text is on its opaque panel), so no veil is needed. Other made kinds
(`blur`, `sheet`, `sky`) are not used: the reference shows landscapes only. Still without a picture: nothing — the
reference's remaining images are its own product screens, whose places the client's screens take.

## Checks

`tools/shots.mjs` on both outputs at both widths: no sideways scroll, no script errors, no distorted media, one h1
(lines in the hand-back report). `probe/audit.mjs` (own): every text against the rendered pixels behind it (text made
transparent, each text box cut from a screenshot, worst pixel) — reduced-motion and no-script renders at 1440 and 390,
plus the pinned stage at 1440: lowest 5.41 (sportbot) and 4.12 (automateed, a 32 px gradient head; floor 3:1 for large
text, 4.5:1 otherwise), nothing under its floor, nothing hidden but the closed menu; every tab stop shows a ring; zero
running animations under reduced motion. The words of the pinned stage that have not yet lit stand at 18 % by the
reference's design and are below 4.5:1 until the scroll reaches them — a passing state, not audited as text at rest.

Not done: no browser other than Chrome; widths between 390 and 1440 not captured (the stage pins from 900 px; 900–1200
not looked at); pin length at viewport heights other than 900 **not verified** against the reference; hover states were
read as computed styles, not screenshotted; the one-file copies were built but not opened.

## Added after the contract's newer sections (2026-11-12)

- **One picture family.** Motif: `land` — the reference repeats one painted landscape series (phone wallpaper, showcase
  panel, foot). Both slots here take `land` (index 1 and 5); no `blur`, `sheet` or `sky`. Panels and cards are plain
  grounds of the page's own ink/ground, not pictures. The row of pills is multi-coloured because the reference's row
  is (six hues, one per level); they are small pills in the palette's own colours, not card or panel grounds.
- **Picture share** (`tools/coverage.mjs`, 1440): reference 17 % overall, per screen [4,18,0,0,0,0,24,40,0,0,0,99,100],
  2 screens with a wide picture (the foot). sportbot 14 %, [4,19,0,0,0,46,21,0,0,0,0,0,100], 2 wide. automateed 16 %,
  [6,27,0,0,0,47,20,0,0,0,69,100], 2 wide. Both within 5 points of the reference; the foot's wide picture is there in
  both. The reference's stage reads 0 on screens 3–6 for the same reason ours does: the tool samples the page at rest.
- **Readability gate** (`tools/legible.mjs`): sportbot `ok — 0 unreadable of 455 line readings`; automateed
  `ok — 0 unreadable of 307 line readings`.
- **needs.json** written from renders of the two clients and three stripped variants (`probe/v/`): the template needs
  steps with an upright picture each; without any pictures it renders but the stage's middle is empty, so
  `holds_without_pictures` is false.

## Pass of 2026-11-12 (engine stress: logo of any shape)
The engine's stress run found the logo drawn out of shape: the opening and closing marks were a fixed 86 / 90 square
(76 on the phone), so a wide logo (tallyfern's 5:1) was squeezed into it. Rule now: the reference's mark size is a
**bound, not a box** — `width:auto; height:auto; max-height:86px` (90 at the close, 76 on the phone, 34 for a wordmark,
44 / 30 in the foot) and `max-width:min(300px,80%)`, so any logo keeps its proportion and is never drawn larger than its
own file. The CSS corner radius is gone: a square app mark keeps the corners drawn in its own file (sportbot's has
them), a wordmark is never clipped. A wordmark is now drawn at its file's own height when that is under 34 (automateed
28) instead of being enlarged.
