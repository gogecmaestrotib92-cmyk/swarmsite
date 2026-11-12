# butter — notes

Reference: https://butter.video (home page), measured 2026-11-12 at 1440×900 and 390×844 with `tools/anatomy.mjs`,
`tools/shots.mjs` and own Playwright probes (`probe/tree.mjs`, `deep.mjs` — box/style tree; `motion.mjs` — load sampled
every ~150 ms, scroll sampled every 60 px by wheel; `hover.mjs` — hover, click and timed states). Raw captures: `ref/`,
`probe/`. The site was reachable; a cookie banner was dismissed with its "Reject all" button.
Three kinds of statement are kept apart: **measured** (read off the live page), **chosen** (my decision where the
reference gives no answer, the data does not fit, or the owner's rules override it), **not verified**.

## Sections of the reference, in order, and the data each takes

| # | Reference section (measured) | Data | Left out when |
|---|---|---|---|
| 0 | Fixed bar, two soft pills: logo + links + a two-dot toggle that opens a panel of rows; sign-in + dark button | `brand`, `nav`, `signin`, `cta`; panel rows = `links[t,d]` (on the phone also `nav`, `signin`, `cta`) | never; toggle only when there are rows |
| 1 | Opening, one screen: ground shaded from the top, an object hanging at the top centre, one-line display head, one line of text, one dark button | `hero.title/text/primary`; picture `media.made.sky` | no `hero.title` |
| 2 | One muted centred line, then a row of marks that runs by itself | `hero.note`; `logos[]`, else `trust[]` set as words | no logos and no trust |
| 3 | A centred display sentence with small square tiles standing between its words; below it a dark slab into which the tiles fly as the page moves | `hero.text2`; tiles `media.made.blur[0..4]` | no `hero.text2` |
| 4 | Story one: sentence left, tall dark product panel right | words: the next `features.items[]` (`t` as the sentence, `d` under it); picture: first upright `media.phones` not used by a step (a general product view; never a photograph) | no such phone, or no feature left for it |
| 5 | Story two: product film left, sentence right | words: next feature; picture `media.screens[0]` | no screen, or no feature left |
| 6 | Story three, held: the sentence slides out to the left while a wide film slides in | words: next feature; picture `media.screens[1]` | fewer than two screens, or no feature left |
| 7 | Head left + button right, a row of four picture cards (picture, name, muted text) | `features.title/text` and the features the stories did not take (stories always leave at least three), button `cta`; pictures: `made.sky` in eight crops, held quiet | no feature items |
| 8 | Product left, at the right a mono label and a list of three large words; one is open with its text | `steps.title` (label), `steps.items[k,title,text,cta,img]` | no step items |
| 9 | Soft rounded field with upright films running by, each with a name | the upright phones/photos not used by a step or story one (needs 3); no names — an `alt` is not a caption | fewer than 3 |
| 10b | (built from the reference's picture-left / large-name list, #12) | `figures[v,l]`: value at h2 size, label in body under it, over the sky field | no figures |
| 10 | Label, head, text left; one square film right | `statement.title/text`; `media.video`, else the next screen | no statement |
| 11 | Two soft cards: head + arrow button, a picture, small muted text | `plans.items[name,price,per,line,rows,cta]`, `plans.title/text/note` | no plan items |
| 12 | Film left; at the right a label and a list of large names, one open | `faq.title` (label), `faq.items[q,a]`; backdrop `made.sky` | no faq items |
| 12b | (built from the reference's centred head with one dark button, as above its gallery) | `close.title/text/cta` | no `close.title` |
| 13 | Soft foot: link columns, the wordmark across the whole width, a muted legal line | `nav`, `links`, `signin`, `cta`, `foot.links/legal/text`, `brand` | never |

sportbot gets everything except the gallery (one upright phone is left after the steps, and story one takes it); its
stories tell features 1–3 and the cards carry 4–7. automateed has no story one (no phone), no faq; its stories tell
features 1–2 and the cards carry 3–5; its gallery runs four upright book pages/covers.

Not shown by this template (listed as "drops" in `needs.json`): `hero.kicker` (only in `<title>`), `hero.secondary`,
`steps.text`, `plans.items[].marked`, `quotes`, `media.screens` beyond the third, upright photographs when fewer than
three are free, every `alt` as visible words, the first-screen label lines ("eyebrows") of the reference — the data has
no words for them, so none were written.

## Measures used (measured at 1440 unless marked; the reference scales its large sizes with the width, kept as vw)

- Gutter 66.1 (4.59vw; phone 25.6). 12 columns, 25 gap. Text/picture halves: columns 1–6 (641) and 8–12 (530).
- Colour relations: ground 250, soft fields 237 (= ink 5.5 % into ground), ink 15, button fill 30, dark panels 10,
  muted text = ink 40 %, inactive list words = ink 30 %. Applied to the client's palette in `_theme()`. **Chosen**:
  muted is raised until 4.6:1 on the soft field, inactive words until 3:1 (they are 60 px), because the reference's
  own values are about 2.6:1 and 2:1.
- Type: h1 107.6/0.99; h2 60.4/0.97; h3 45.5/0.96; h4 24.5/1.15; body 20.75/24; small 16/21; mono label 13.5/24
  +.036em muted. Phone: h1 56.7/1.09, h2 32.4/0.9, h3 32.2/1.0, h4 and body 20/24, label 12.
- Buttons 50 high, 8×30, radius 16, 16/21; small one in the bar 39 high, radius 10; arrow buttons 50×50.
- Bar: 88 high (phone 76), pills 64 high radius 16, links 16/20 with 25 gap; panel under the pill, radius 16.
- Opening: 100vh, padding 200/140, 30 between head, text and button; ground gradient 214 → 250.
- Marks: section padding 50; 60 between line and row; marks 36 high, 100 apart.
- Statement: two blocks of 100vh, each centred (phone: padding 185/150); inline tiles 69 = 1.142em; slab tiles 241
  with 19.6 padding (phone 62, 5); tile corner about a quarter of its side (read off the screenshot, **not measured**).
- Stories: padding 238 (16.5vw); picture heights 870 / 687 / 736; media radius 32 (phone 14–24).
- Held story: 736 high, pinned at the middle of the screen (top 82 at 900) for 983 px while the row moves 720 px.
- Sections after that: padding 140 (phone 100). Cards 308 wide, picture 308×401 radius 32, 20 / 20 below.
- Opening list: label, 25 below; words h2 size with 25 under each; open text 20.75/24 with 20 under.
- Gallery: soft field radius 32, padding 50; items 308 wide, radius 20, padding 50, picture box 216×384, 30 to the name.
- Two cards: 641×719, radius 32, padding 50 (phone 30), 25 gap. List over picture: names 41.7/40.
- Foot: padding 160/60 (phone 160/70), columns two of twelve wide, links 20.75/24 with 5 gap.

## Typeface stand-ins (SIL OFL, Google Fonts)

| Reference (commercial) | Stand-in | Why |
|---|---|---|
| Die Grotesk, regular, everywhere | **Inter Tight** 400 (500 for the foot name) | tight neo-grotesque of the same build; tracking was set per size so that the reference's own lines come out at the reference's widths (test strings measured in the stand-in: 1082/1082, 223/223, 585/586, 468/468, 515/514, 308/308 px) |
| ABC Diatype Mono (labels) | **Geist Mono** 400 | plain grotesque monospace |

## Motion — measured, and what was reproduced

| What | Measured on the reference | Here |
|---|---|---|
| Load | once the page is ready the head's words fade in (~0.7 s), the line rises 17 px and fades, the button rises 30 px (transform .8s cubic-bezier(0,0,0,1), opacity .528s linear) | same, as CSS animations (they run without scripts). Start time on the reference depends on its 3D scene loading (3.7 s in my run); here 0.25 s |
| Arrival on scroll | blocks rise 30 px (.8s cubic-bezier(0,0,0,1) + opacity .528s linear), text lines rise 14.4 px, head words fade/rise one after another; triggered when the top edge is ~9 % into the screen; second card ~0.1 s after the first | same; only under `html.js`, so nothing is hidden when scripts fail. Paragraphs arrive as one block, not line by line |
| Bar | past 100 px the links fade and the toggle slides left (458 px) so the pill closes to logo + toggle (708 → 250 wide) | same, .5s cubic-bezier(.2,.715,.205,.99). How the reference shrinks the pill ground was **not read** (computed style still said 708); width taken from the screenshots |
| Bar panel | opacity .8s, scale .98 → 1 and clip-path .5s, same curve; page shaded rgba(53,53,53,.2) .5s; links hide while it is open | same; the reference's "Close" word is not used (no such word in the data); Escape closes |
| Marks row | runs left at ~150 px/s | same speed whatever the length; paused off-screen (**chosen**) |
| Statement tiles | scroll-led: five tiles go from their places in the sentence (69 px) to the slab (241 px), one after another, over ~320 px of scroll, turning a few degrees on the way (sampled scale .29 → 1 between scroll 1400 and 1720) | same model: starts when the sentence's top is 5 % from the screen top, each tile takes .267 screen heights, the next starts .023 later, ease in-out, ±8° at mid-flight (angle by eye from the sampled matrices). The reference smooths the wheel (Lenis); here the native scroll is used |
| Story one | hovering a tile in the product panel switches a type effect on the sentence | not reproduced — it is the reference's product demo |
| Held story | pinned 983 px, row translates 0 → −720 px linearly | same (sticky + one variable); measured on ours: pinned at top 82, row 0 → −720. Not held under 1000 px width (the reference's phone build does not hold it either) |
| Opening list | click opens; height changes in ~0.2 s; word colour .5s cubic-bezier(.835,.12,.225,.77); the pictures change by a soft sideways wipe (gradient mask 400 % wide, position 0 → 100 %, .6s same curve). No self-advance in 9 s | same |
| Gallery | runs left at ~100 px/s, does not stop on hover; hovered item's ground darkens over 1 s | same |
| Buttons | a many-coloured soft light swells behind (opacity 0 → 1, scaleY .9 → 1, .4s) | same; its three colours are the client's accent and palette extras |
| Links | bar link dims on hover (.5s); foot link moves 6 px right (.5s) | same |
| Foot wordmark | its colours turn with the scroll (hue-rotate) | not reproduced: the client's mark is not a colour piece |
| Pointer label | a small dark label follows the pointer over the opening | not taken (the reference's own words and gimmick) |
| Reduced motion | not measured | all animation and transitions off; tiles rest in the slab and the sentence reads plain; the story is not held; rows of marks wrap instead of running; film does not play and shows controls |

## What could not be transferred, and why

- **The hanging 3D object** in the opening is the reference's illustration. Its place (top centre, text under it) is
  taken by `made.sky`, masked out toward the ground, with a veil of the page's own ground under the head.
- **Product panels** (the timeline with ruler and transport, the library panel with four labelled tiles, the editor
  recordings) are the reference's product. The slab is a plain panel in the ink colour without drawn controls (so it
  is 280 high, not 389); story one shows the client's upright screen in the panel's place.
- **Owner's rule on boxed pictures.** Stories and the opening list show the client's screens whole, at their own ratio,
  standing on the page ground (the reference crops films into 641×687/706 rounded boxes). The last list (reference:
  film box left, list right) has no screen of its own, so the made photograph is the ground of the whole field and the
  list lies over a veil at the right; on the phone the picture is bare at the top and the veil closes downward.
- **Sentences for the stories**: the reference writes a sentence per story. Here each story tells one feature in the
  client's own words (`t`, with `d` under it in the body style) beside a general view of the product; the picture keeps
  its own `alt` as alt text only. (The first pass set the `alt` as the sentence — wrong, and gone; the gallery's
  captions, which were alts too, are gone with it.) The label lines above the sentences are left out.
- **Card pictures**: features have no pictures of their own; the cards take the page's one motif (below).
- **The slab on a dark page** (**chosen**): the reference's slab is the darkest thing on a light page. Turned over literally it was a white slab on sportbot's dark page; on a ground darker than luminance .2 it is a panel 10 % toward the ink instead.
- **Two cards → plans**: the reference's cards hold a product picture between head and text; here that band is the
  sky motif and the plan's price is set on it in display size. A card without `rows` drops the 719 minimum height (automateed).
- **Texts the reference has no place for** but the data has, added in the reference's own body style (**chosen**):
  `features.text` and `plans.text` under their heads, the step's `title` and `cta` inside the open list item.
- **Logos**: both clients have none; `trust[]` runs as words at h4 size. An entry equal to `hero.note` is skipped.
- **Foot**: column labels, social links and "all rights reserved" have no data. The wordmark across the width is the
  client's own logo when it is a wordmark (automateed), else the brand name set in type (sportbot).
- The toggle's `aria-label="Menu"` is the only string not from the data.

## Image slots

| Slot (`data-slot`) | Where | Takes | Without it |
|---|---|---|---|
| `opening-sky` | behind the opening, the whole first screen, cover from the top, masked to nothing at its foot, veil of the page ground under the type | `made.sky` (sportbot dark, automateed light); ink follows `tone` | the shaded ground alone; slot name on the section |
| `tile-blur` ×≤5 | square tiles, 69 px in the sentence → 241 px in the slab (62 on the phone), cover | `made.blur[0..4]` (sportbot 5, automateed 4) | plain squares in the accent and palette extras |
| `slab-sky` | ground of the slab (1308×280), cover from the foot, at 50 % | `made.sky` | plain panel |
| `card-sky` | card pictures 308×401, radius 32, cover, eight different crops, 38 % veil of the page ground | `made.sky` | card without picture |
| `plan-sky` | band across each plan card between head and text (641 × ≥230), 66 % veil of the card ground; the price stands on it | `made.sky`, left and right foot crops | plain card |
| `questions-backdrop` | whole field of the last list (1308 × ≥706), cover; veil 0 → 95 % between 18 % and 46 % of the width | `made.sky` (sportbot dark) | plain soft field, list at the left |
| `foot-sky` | lower 78 % of the foot, full width, turned over so the glow sits under the name; veil 62–93 % of the foot ground | `made.sky` | plain soft foot |

Pictures of the client's own: story one (upright, ≤870 high), story two (≤687 high), held story (≤736 high), the list's
pictures (≤706 high), the gallery (in 216×384), the film or screen beside the statement (≤641 high).
Still without a picture: logo marks (needs real `logos`); per-feature pictures (needs screens tied to each feature).

## One picture family, and picture share

Motif: **sky**. The reference repeats one kind of made image (its many-coloured "blocks") through the opening, the
slab, the cards and the foot. Here every large slot is `made.sky` — the opening, the slab ground, the card pictures,
the figures field (mirrored), the plan bands, the questions field, the foot — each in another crop and held toward the page ground. `made.blur` is
used only for the five small tiles, where the reference itself is many-coloured. `land` and `sheet` are not used
(the first pass used four kinds; that is gone).

`tools/coverage.mjs` at 1440: reference 35 % picture, 4 screens with a wide picture, per screen
[100,0,51,47,16,36,32,7,8,42,30,28,34,47,28,35,72]. sportbot 35 %, 4 wide,
[100,0,31,16,15,31,18,0,44,19,34,67,34,43,31,78]. automateed 33 %, 3 wide, [100,0,39,19,29,0,32,20,30,13,73,26,20,100].
Both are within 5 points. Wide pictures of the reference: opening, slab, held story, foot; ours have the opening, the
figures field and the foot on both clients, the questions field on sportbot; the slab (1308 wide) straddles two screens and is not
counted as wide; the held story's screen stands whole at its own ratio (944 of 1440 on sportbot).

## Checks

`tools/shots.mjs` on both outputs at both widths: no sideways scroll, no script errors, no distorted media, one h1.
`tools/legible.mjs`: `ok — 0 unreadable of 433 line readings` (sportbot), `ok — 0 unreadable of 233 line readings`
(automateed), final build. Two real findings on the way: the mono label over the questions picture read 4.13:1 (veil made
stronger and started earlier), and closed list items were still laid out under their neighbours (now hidden and out
of the tab order). Own audit before the picture changes (`probe/audit.mjs` + `probe/contrast.py`): every visible text box cut from a full-page capture with the text
made transparent, worst pixel against the text's colour — no text under 4.5:1 (3:1 from 24 px) on either client at
either width; lowest values: muted small text 4.6–4.7, marks line 5.2, inactive 60 px list words 3.5, opening head
14.2 (sportbot) / 10.6 (automateed). Keyboard focus shows a 2 px ring on links, buttons, the toggle, list buttons and
the card rail. Reduced motion: zero running animations. Scripts off: no text or picture left invisible.
Not done: no browser other than Chrome; widths between 390 and 1440 were not captured (the layout changes at 1000);
hover states were read from computed styles, not screenshotted; the bar's header texts were not in the pixel audit
(they stand on an opaque soft pill); the faq field with a `light`-tone picture is not exercised by either client; the own pixel audit and the
reference/ours pairs were not looked at again one by one after the last picture changes (legible, shots and coverage were re-run).

## Pass of 2026-11-12 (engine stress: a 40-character button)
The engine's stress run gave the buttons a 40-character label; at 390 they ran 21–42 px past the screen because every
`.btn` was `white-space:nowrap`. Rule now: a button is never wider than its column (`max-width:100%`), a long label
wraps onto a second line, centred and balanced (`text-wrap:balance`), at the measured 21 px leading inside the 50 px
minimum height — words are never cut. A label that fits on one line looks exactly as before.
