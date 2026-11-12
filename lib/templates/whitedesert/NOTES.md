# whitedesert — notes

Reference: https://white-desert.com (home page), measured 2026-11-12 at 1440×900 and 390×844 with `tools/anatomy.mjs`,
`tools/shots.mjs` and own Playwright probes in `probe/` (`steps.mjs` stepped screenshots every half screen over the whole
20 787 px page; `motion.mjs` load sampling every 200 ms, declared transitions, scroll sampling every 150 px; `hs.mjs`,
`hs2.mjs`, `more.mjs` box/style trees, the pinned section's timeline, hover states, phone build). Raw: `ref/`, `probe/`.
This is a template for **places**; test clients are `butarque` (five photographs, two small) and `balamo` (none).
Statements are kept apart as **measured** (read off the live page), **chosen** (my decision where the reference has no
answer for this data or an owner's rule overrides it) and **not verified**.

## Sections of the reference, in order, and the data each takes

| # | Reference (measured) | Data | Left out when |
|---|---|---|---|
| 0 | Fixed bar 80 high: three glass tiles left, mark centre, two tiles right (the last is "Enquire"). Leaves on scroll down, returns on scroll up. Phone: one glass bar, mark, accent "Enquire" | `nav[0:3]` left, `brand.logo`+`brand.name` centre, `nav[3:5]` + `place.booking` (else `cta`) right. Phone: brand + booking | never |
| 1 | Opening, one screen held for two: film backdrop, small italic line left and an outlined button right at 47.5 % height, one giant condensed word at the bottom (256 px) | backdrop `media.photos` (see slots); italic line `hero.text`; button `hero.secondary` (else `primary`); giant line = `hero.title` (h1) | never (no photo → dark ground) |
| 2 | White, 320/160: small italic label, 42 px capital serif statement with a first-line indent, inked line by line as it rises | `hero.kicker`, `statement.title` | no `statement.title` |
| 3 | Tall full-bleed picture 1440×1350 fading in from the page ground, a 236-wide block (condensed label + 14 px text) on its pale top | picture slot `tall`; label `hero.text2`; text `statement.text` | no picture and no text |
| 4 | Centred 60 px capital serif head, 320/160 | `features.title` (only when the menu has sections) | no title |
| 5 | Strip of five cards 765 high: four closed at 1/8 width (blurred picture), one open at 4/8 with italic 42 px title top-left, price · season and text bottom-left, "learn more" | `place.events[]` (what / price · when / where / cta) then `place.menu.sections[]` (title; its `items` as name–price rows; the title is the link). Below: the menu link, labelled from `links`/`nav` whose address is `place.menu.h` | no events and no sections |
| 6 | Quote: 472-wide column, italic 22 px, name + role | `quotes[0]` | no quotes (both test clients) |
| 7 | Held screen, 8 550 px of scroll: full picture with a 90→60 px head and a 236-wide note; three bars wipe a second picture in; cards 720×540 (glass frame 20, picture 680×500, capital title + text on the picture, a condensed line at the bottom) pass sideways at a 920 pitch; last panel a press quote | head `steps.title`, note `steps.text`, cards `place.spaces[]` (else `steps.items[]`): `title`, `text`, `img`; bottom line = the item's `cta.t`; last panel `quotes[1]` | no spaces/steps |
| 8 | Giant 320 px condensed route code, half-transparent, drifting | `place.since` | no `since` |
| 9 | "Journey": rule, corner lines left/right, centred 42 px head + 14 px text; then a dark band with a glass card of three facts (italic label, 42 px value) and map labels | corners: postcode+city / region+country — phone / email; head `place.address.street`; text `hero.note`; facts `place.hours[]` (days → open – close) then `place.phone`; side list `place.takeaway`, `place.social[]` | no address, phone or hours |
| 10 | Closing banner 900 high: picture, 42 px capital head, outlined button 160×50 | picture slot `close`; `close.title`, `close.cta` | no `close.title` |
| 11 | Foot on a warmer ground: mark, link columns with italic heads, a 2×3 block of tiles, the name across the full width, a bottom bar | `brand.logo`, `foot.text`; columns `nav`, `place.menu.lists[]` (head = the menu link's own label), `foot.links`; tiles booking / menu / phone / email or takeaway; `brand.name`; `foot.legal`; `place.notices[]` above the name | never |

Not shown (the reference has no place for them): `trust[]`, `figures[]`, `features.items` (the same sections come from
`place.menu`), `links[].d`, `close.text`, `place.price_range`, `place.cuisine` (same words as `hero.kicker` for balamo),
`place.phone.note` (for balamo it is a note about the capture, not the client's word, and the data gives no way to tell),
menu `count`s (a bare "5" on a card read as filler; the client's own label for it is the shop theme's English "products").
Every label on the page is a string from the data; the template adds no word of its own.

## Picture slots — what each takes, and what the page does without

Full-bleed slots take only pictures that are **not** `small`. Order of choice is by `role`: exterior, room, bar, people,
other, dish; wide before upright (**chosen**).

| Slot | Reference | Rule | butarque | balamo |
|---|---|---|---|---|
| `hero` | film, 1440×900 | best non-small picture by role, even if a space card shows it again | `salon.jpg` 1400×589 (cover, enlarged ×1.53 at 1440×900 — soft; see report) | none → dark ground, type only |
| `tall` | 1440×1350 | an upright picture not used elsewhere, else any unused; the section takes the picture's own ratio up to 15:16 | `barra.jpg` 1400×1867 | none → the text block alone on the page ground |
| `close` | 1440×900 | next unused, wide first | `salmon.jpg` 1187×796 (enlarged ×1.21) | none → a quiet band on the page's tinted ground, ink text |
| `open` (spaces, first picture) | 1440×900 | next unused | none left → dark ground | none |
| spaces backdrop (second picture) | 1440×900 | — never filled: plain tinted ground (ground + 7 % ink) | plain | plain |
| space cards | 680×500 each | the space's own `img`. Card width = the narrowest picture's own pixel width, capped at 680, so **no small picture is enlarged**; under 560 the card takes the reference's phone measures (26 px title) | 418×307 (terraza and chill-out are 418×315) | no pictures → cards on deep tones of the palette |
| strip cards | one picture each | **never filled**: the data does not say which dish belongs to which section, so no photograph is put under a section name. Deep tones of the client's palette (each colour mixed toward the dark until white text reaches 5.2:1) | 7 tones | 1 tone |
| foot film tile | 454×110 | not a picture: the booking tile in the accent | — | — |

`media.made` is not read (places get no generated pictures). A `small` picture appears only in a space card at or under
its own pixels; never as a backdrop.

## Measures used (measured unless marked)

- Grid: 12 px page margin, 12 columns without gutter (118 px at 1440); inner margin 60. Nine fixed 1 px hairlines at
  12 / 60 / 248 / 484 / 720 / 956 / 1192 / 1380 / 1428, white, 10 %, `mix-blend-mode:difference`.
- Bar: 80 high, 20 padding; tiles 120×40 (min-width here, the client's labels are longer), radius 2, 6 gap, 16 px;
  ink 20 %/15 % glass → here 42 % dark glass so white 16 px text holds on bright photographs (**chosen**); hover = accent
  fill. Phone: 350×50 bar, 5 padding, radius 2, tiles 80×40, 14 px.
- Opening: 100 vh; overlay 20 % black on the reference → 46–52 % here, 60 % on the phone (**chosen**, for 4.5:1 on a bright dining room);
  italic line 18/21.6, 294 wide, x 60, y 47.5 %; button 188×44, 1 px white 20 % (45 % here), 14/21; h1 Oswald 400
  capitals, line-height 1, 256 px = 17.78 vw for ten letters across 80.9 vw. Phone: italic 20/24 centred with 50 px side
  padding, button 266 wide, 169 below the line, h1 80 px = 20.5 vw.
  **Chosen**: the client's title is a sentence, not one word. `_fit()` sets it in at most two lines (five on the phone)
  at the size that fills the same measure (0.47 em per letter, measured from the reference's word), capped at the
  reference's 17.78 vw and at 24 vw of total height (64 vw on the phone).
- Statement: padding 320/160 (phone 200/100); column 5–10 of 12 (x 484, 708 wide; phone 47 px margins); label italic
  18; statement 42/42 capitals weight 400 (phone 26), first-line indent one column (16.6 % of the column).
- Tall banner: 1440×1350; block in columns 3–4 (x 248, 236 wide), 139 from the top; label Oswald 500 18/21.6 capitals;
  text 14/21 weight 500; 20 between. Phone: text first (126 above), the picture under it.
- Head: 320/160, 60/60 capitals centred (phone 200/48, 32 px).
- Strip: 12 px margins, 765 high (85 vh here, 520–765), closed 1 unit / open 4 units; content padding 44; title italic
  500 42/42; meta 16 px with a 1 px divider; text 16/22.4, 344 wide. Phone: stacked cards, radius 4, 10 gap, 20 padding.
- Quote: 320/320, columns 5–8, mark 36, italic 22/26.4 with indent, name 14/21, role muted.
- Spaces: head 90 px at pin start (131 px one screen earlier, 60 px one screen later) → scaled here; note 14/21 in the
  right columns; card frame 20 padding, radius 6, ink 5 % glass (7 % here, no blur); picture radius 2; title 42/42
  capitals centred, text 14/19.6 at most 480 wide, bottom line Oswald 500 14 capitals; pitch = card + 240 (920 for 680).
  Phone: panels one screen wide, card 310×398, title 26.
- Giant mark: Oswald 400, 320 px, line-height .9, white at 50 % over the picture → ink at 62 % on the tinted ground
  (**chosen**: there is no picture under it).
- Where: 1 px rule at 50 %; corners Oswald (13 px here; the reference's size was **not read**) in the muted tone;
  head 42/42 capitals, text 14/21 muted, 464 wide; band height 246. Dark band: card 445 wide at x 40, radius 6,
  padding 32/20, ink 20 % glass (white 9 % here); label italic 18; value Inter Tight 400 42/63 capitals (phone 32/48);
  dashed 1 px dividers with 24 above and below; map labels Oswald 400 16/19.2 capitals.
  **Chosen**: when nothing stands beside the facts (no takeaway, no social links) they run as one row across the band
  instead of a 445 card with an empty band beside it — the reference fills that space with its globe.
- Closing: 900 high, 20 % black overlay (50 % here), head 42 capitals at most 714 wide, button 30 below, 160×50,
  1 px white 20 %, radius 2; hover fills white.
- Foot: ground 233/231/225 beside a white page → page ground stepped 10 % toward ink/accent; tiles 110 high, radius 2,
  10 gap, 14/21; link heads italic 18; links 14/21 at 50 % → raised to 4.6:1; name Oswald across the width (187 px
  high on the reference); bottom bar 86 high between two 1 px side rules.
- Colour relations: page ground / ink / accent come from `palette`. Muted = ink at 50 % raised until 4.6:1. Dark band =
  ink 72 % toward black (reference 9,11,16 beside ink 31,42,68). Text on the accent is white or near-black, whichever
  has more contrast (butarque's and balamo's green carry near-black).
- Focus: 2 px accent outline, 3 px offset, with a 5 px ground ring behind it so it shows on photographs and dark bands.

## Typeface stand-ins (Google Fonts, SIL OFL)

| Reference | Here | Why |
|---|---|---|
| Oswald | **Oswald** 400/500 | already open-licence; used as is |
| Inter Tight | **Inter Tight** 400/500 | already open-licence; used as is |
| Cardinal Classic Long (commercial) | **Cormorant Garamond** 400/500 + 500 italic | a display Garamond with the same long extenders, sharp serifs and a calligraphic italic; lighter in colour than Cardinal at 14–18 px |

## Motion — measured, and what was reproduced

| What | Measured on the reference | Here |
|---|---|---|
| Load | the opening's content rises about 180 px and fades in: `reveal-transform` 1.4 s cubic-bezier(.16,1,.3,1), `reveal-opacity` 1.4 s ease; in place by ≈1.25 s | same keyframes |
| Bar | translateY −80 on scroll down, back to 0 within ≈240 ms of scrolling up | same, .25 s ease-out; also flips to ink-on-light tiles over light sections (**chosen**; the reference's own change over white was not measured) |
| Opening | pinned for 1 800 px (two screens). Title moves up at 0.3 px per px and blurs linearly 0 → 10 px. Two cloud pictures rise from below at 0.9 px per px; the white section slides over from 900 | same numbers; the clouds are the reference's pictures, so a plain veil of the page ground rises instead (transparent → ground over its top 46 %) |
| Statement | text goes from pale to ink top-down as it rises (mechanism not in the DOM as spans; **not measured** beyond the screenshots) | a ground-to-ink gradient clipped to the text, driven by the block's position (ink reaches the bottom when the block's top is at 72 % of the screen less its own height) |
| Tall banner | the text block moves 13 % faster than the picture | same (translate up to 175 px) |
| Strip | pointer over a card opens it: widths 177 ↔ 708 settle in ≈0.6 s; picture scale 1.05 with `transform .6s cubic-bezier(.4,0,.2,1)`; closed cards carry a 7.5 px backdrop blur | flex-grow 1 ↔ 4 over .6 s with that curve; content fades in .5 s after .25 s. Opens on pointer, focus and press. No blur (no pictures) |
| Spaces | pinned 8 550 px. Head: 131.7 px one screen before the pin, 90 at pin, 60 one screen in. Note travels up 1.07 px per px. Track starts at 1 100 px and moves 0.565 px per px (4 200 px in all). Three bars wipe the second picture in between ≈1 100 and ≈2 400 px (bar geometry read from screenshots only) | same thresholds and rates; pin length = 1 100 + travel / 0.565, so it depends on the number of cards (butarque ≈ 4 100 px). Bars: three thirds growing from their right edge (**approximation**) |
| Giant mark | moves at 0.31 px per px against the page | same |
| Tiles, buttons | `all .3s cubic-bezier(.5,1,.89,1)`; tile → accent fill, label shifts −8 px for an icon; outlined button → white fill, accent text | same curve and fills; no icon, so no shift |
| Side tab | accent tab 60×200 on the right edge after the opening, `all .45s cubic-bezier(.76,0,.24,1)`; opens a "how it works" drawer | same tab and curve, carrying `place.booking` as a plain link (**chosen**: the drawer's content has no data). Hidden on the phone and from the tab order (the bar already has the same link) |
| Custom pointer | 4 px accent dot with cross-hair lines following the pointer | not reproduced (pointer-only decoration) |
| Film hover preview, globe flight path, liquid-glass specular highlights | present | not reproduced: the reference's own imagery and product |
| Reduced motion | not measured | no animation or transition; the opening is one screen, not held; the spaces are not pinned: opening block, then the cards in a row that wraps; text fully inked |
| No script | — | same plain build as reduced motion except the opening stays held (CSS sticky); the strip's cards all stand open in a wrapped row (`<noscript>` style); nothing is hidden |

## What could not be transferred, and why

- **One word as the title.** The reference's first screen is a single place name at 256 px. A restaurant's title is a
  sentence; it is fitted to the same measure in two lines (butarque ≈ 7 vw, balamo ≈ 12 vw). The h1 could instead be the
  town (`place.address.city`) — nearer the reference's look, further from the client's own first line; not done.
- **Film.** No client film; the opening is a still. The "watch film" button carries `hero.secondary`.
- **Cloud and mist pictures, hand-drawn scribbles and the signature** are the reference's own imagery / drawn strokes
  (owner's rule: no drawn strokes): the first became a plain rising veil, the others are dropped.
- **Pictures on the strip cards and behind the spaces** — see slots. With seven menu sections and no pictures or
  descriptions the strip is seven tones with one title each; only "Postres" has rows.
- **Camp coordinates** have no data; the line takes the item's `cta.t` when there is one, else nothing.
- **Globe section.** The map, flight path and film tile are the reference's own; the band keeps its head, facts card
  and labels.
- **Press logo and partner badges** in the quote panel and foot: no data, left out.
- **Phone menu button.** The reference's phone bar has "Menu" (a drawer). No such word in the data and no drawer here;
  the nav links are in the foot.

## With no photographs (balamo) — what the page is

Every picture slot falls back to a plain ground: a black first screen with the title in white capitals, the statement,
the text block, one deep-grey card for the Thursday dinner, a black held screen with the head and three tone cards, the
address band, a quiet closing band, the foot with the legal notice. Nothing breaks, overlaps or scrolls sideways, and all
checks pass — but it is a type page in black, white and green; the reference's whole character (photographs lead) is
absent. It should not be offered in this state.

**Minimum to offer this template (chosen, from the slots above):** three photographs that are not small —
(1) one wide picture of the place itself (exterior or room), at least 1920 px wide and 3:2 or squarer, for the first
screen; (2) one upright or 4:3 picture at least 1440 px wide for the tall banner; (3) one wide picture at least 1440 px
wide for the closing banner — plus one picture per space at least 720 px wide (1360 for sharp 2× screens). Better: two
more wide pictures (spaces opening and backdrop) and one picture per menu section or event; without those the strip
stays tones. butarque meets (2) and, softly, (1) and (3); its space pictures are 418 px, so its cards are 418 wide on
a 1440 screen where the reference's are 680.

## Checks run (2026-11-12, final build)

`tools/shots.mjs`:
- butarque d `{"height":14069,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []`
- butarque m `{"height":11794,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []`
- balamo d `{"height":12719,"sideways":0,"docW":1440,"vw":1440,"distorted":0,"h1":1} errors: []`
- balamo m `{"height":9427,"sideways":0,"docW":390,"vw":390,"distorted":0,"h1":1} errors: []`

`probe/check.mjs` (own; output of the run before the last veil change in `probe/check.txt`): every visible text node is
compared with the rendered pixels under it (screenshot taken with the text made transparent, 60 samples per node, the
worst tenth decides; 4.5:1, or 3:1 from 24 px). balamo: 0 fails of 81 (1440) and 56 (390). butarque: 1 of 103 at 1440 —
the e-mail in the right corner of the address band while the fixed booking tab passes over it (the tab covers the last
48 px of that line for part of the scroll; the reference's tab does the same to its corner line); 1 of 92 at 390 — the
italic line on the first screen at 4.14:1, after which the phone veil was raised from 50 % to 60 % (**not re-measured**).
The statement's gradient-inked text is skipped by this check (it ends at full ink).
Focus: six Tab presses at both widths land on links with a solid 2–3 px outline. Reduced motion: no sideways scroll,
opening 900 high, spaces not pinned, no animation; the closed strip cards keep their titles hidden until opened (as the
reference's closed cards do). No script: nothing invisible.
Not checked: Safari and Firefox; widths between 390 and 1440 other than by reading the CSS; screens wider than 1440
(the first-screen photograph is enlarged further); touch behaviour of the held sections on a real phone; the one-file
copies beyond their being written.

## Pass of 2026-11-12 — one picture family, picture share, readability, real photographs
This section supersedes "Picture slots", "With no photographs", "Minimum to offer" and "Checks run" above (written when
butarque had five photographs and balamo none). The clients now carry their sites' photographs: butarque 52, balamo 20.

**Motif.** The reference repeats photographs of the place itself (ice, camps) in every slot. Here: the client's own
photographs of the place — opening, tall banner, close, room cards; dishes only inside the strip's cards. The strip's
picture-less cards and the room cards without pictures are one dark tone in three quiet steps (before: seven different
palette hues, one per card — the thing the owner rejected). No `media.made`.

**How photographs are chosen** (each once; most of a large set is never shown):
1. opening: not small, not a dish, exterior/room/bar first, the one that fills most of 1440×900 at its own size.
2. room cards: `place.spaces[].img`; else each `steps.items[]` takes the photograph whose `photos[].page` is its link (all or none).
3. strip cards: a menu section takes a dish photograph whose `page` is the section's link; a section listed dish by dish
   takes the photograph whose description begins with its first dish's name (used to choose, never printed).
4. tall banner (upright first), closing band (w ≥ 1.2 h): what is left of the large pictures, never a dish while another is left.
   The rooms' opening backdrop takes a further wide one if any is left (none was, for either client).

| slot | butarque (11 of 52 shown) | balamo (6 of 20) |
|---|---|---|
| opening | terraza-mesas-altas 1800×2400 | gran-reserva-pasillo 1242×1152 (1242 wide in the dark screen) |
| tall banner | barra-2400 1800×2400 | maridaje-copa-2 1344×1334 |
| strip cards | risotto-de-boletus, hamburguesa-butarque, surtido-de-ahumados, calamar-de-potera (by page), postre-ferrero-rocher-gold (Postres, by first dish); De la huerta / De la tierra: plain tone | none (the event's link has no photograph) |
| room cards | terraza 418, salon-1900, chill-out 418 → cards 418×307 | by page: gran-reserva-barrica, mostrador-marisco 570×740, gran-reserva-reservado → cards 570×419 |
| closing band | gintonic 1900×800 | maridaje-copa 1437×810 |
| rooms' opening | none left → dark ground | none left |

**No picture above its own pixels.** Opening, banner and close are capped at `--pw/--ph`; room cards at the narrowest
picture's width and the lowest picture's height; the strip is as high as its lowest picture (600 for butarque's dish
squares instead of 765) and a card's picture is at most its own width, anchored right under a veil of the card tone.
Before: salon.jpg ×1.53 on the first screen, salmon.jpg ×1.21 on the close, room pictures ×1.26 on the phone. Now every
picture measures ≤ ×1.00 at 1440 and 390 for both clients (own probe).

**Picture share** (`tools/coverage.mjs`, 1440): reference 36 % `[100,100,13,100,42,84,13,89,0×11,98,96,96,7,0]`, 8 wide
screens. butarque 27 % `[100,0,33,100,38,38,18,0×6,27,64,0]`, 3 wide. balamo 23 % `[89,0,31,94,8,27,0×7,84,12,0]`, 3 wide.
Held (sticky) screens read 0 in this tool on both pages: our second screen is in fact the opening picture (seen in
`out/*-d-01.jpg`), and the reference's held rooms section is full-bleed pictures where ours is cards on a plain ground.
**Ours is 9 and 13 points under the reference — outside the 5-point rule.** What is missing is a wide place photograph
for the rooms' opening (and a second for its backdrop); neither client has one left after opening, banner and close.

**Readability** (`tools/legible.mjs`): butarque ok — 0 of 198; balamo ok — 0 of 188; arriving from below (bar returned):
0 of 334 / 0 of 303. What was failing and how it was fixed: the statement's gradient-clipped glyphs (a measuring artefact —
now real ink under a veil of the ground, same look); muted small print on the fixed 10 % hairlines (3.7:1 on a hairline
pixel → muted tones raised to 5.8:1 on the ground); the banner's words on the picture (a soft pad of the ground behind
the column, any length); the room cards' foot line on a bright picture (dark foot veil); the first-screen italic on a
bright picture (veil .58–.60); the phone italic that measured 4.14 before is in these readings.
**Bar:** tiles and the name stand on 72 % dark glass (white holds over anything) or, over light sections, on an opaque
tint; the name had no ground of its own before. **Booking tab:** the right corner line keeps 60 px clear of it and the
tab leaves when the foot arrives (it used to pass over the e-mail line and would cover the name across the foot).
**Focus:** the ring was the accent on a white halo (2.4:1 for both clients' greens) → ink on the halo; a room card reached
with the keyboard is brought to the middle of the held screen (it was focused off-screen); every stop at both widths
now shows a ring ≥ 3:1 (own probe).

**shots.mjs:** butarque d `{"height":13804,"sideways":0,"distorted":0,"h1":1} errors: []`, m `{"height":11750,…} errors: []`;
balamo d `{"height":13572,…} errors: []`, m `{"height":10692,…} errors: []`. One-file copies 0.97 and 0.95 MB.

**Still not right / not checked.** balamo's two banners are two views of one wine glass, and its opening is 1242 wide in
a 1440 screen. butarque's room cards are 418 wide on a 1440 screen. The strip mixes picture cards and two plain ones.
The legibility gate was run before the last two script-only edits (focused-card scroll, `overflow:clip` on the held
screen); shots and the focus probe were run after. No FAQ part is built (both clients' `faq` is empty). Not checked:
Safari/Firefox (the pad uses `filter:blur`, the tints `color-mix`), widths between 390 and 1440, screens wider than 1440.
