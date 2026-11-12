# bellagrande — template for places, rebuilt from hotelbellagrande.com (measured 2026-11-12, 1440 and 390)

Run: `python3 -I build.py bellagrande butarque|balamo`. Test clients as they were at the last build (11:25): butarque 52
photographs (5 large, 47 flagged small; 4 are ≥1600 wide), balamo 20 (5 large, 15 small; none ≥1600 wide).
Measurements: `ref/anatomy.json`, `probe/tree-d.txt`, `probe/tree-m.txt` (every element's box, type, padding, transition),
`probe/tree-rooms-*.txt`, `probe/tree-food-and-drinks-*.txt` (two sub-pages), `probe/motion.json`. Reference screens:
`ref/ref-d-*.jpg`, `ref/ref-m-*.jpg`, `ref/rooms-*-full.jpg`, `ref/food-and-drinks-*-full.jpg`, `ref/menu-*.jpg`, `ref/hdr-*.jpg`,
`ref/cta-hover-*.jpg`. The cookie panel was closed with its "Decline all" button (`probe/probe.mjs`); `ref/anatomy-*.jpg`
still show it because `tools/anatomy.mjs` looks for a role=button and the panel's control is not one.

## Sections of the reference, in order, and the data each takes
The home page is ten modules; rooms and the restaurant are each one photograph-teaser that leads to a sub-page. A client's
page is one page, so the two sub-pages' own parts are brought in under their teasers: the **room card** of `/en/rooms` for
spaces, and the **ruled rows** of the menu panel for the carta.

| # | reference (measured) | data | butarque | balamo |
|---|---|---|---|---|
| 0 | header 72 high (62), fixed: MENU left, mark centre (1.42× while at the top), BOOK right; clear over the hero, page ground + 1 px rule once moved; slides away at the footer | menu button · `brand.logo`, else `brand.name` · `cta` (else `place.booking`) | name (hidden while the hero's own name is on screen) | logo.png (opaque white square, shown as it is) |
| 0b | menu panel: full screen on the accent; left half ruled rows 80 high, 23.4 px display; contact lines at the foot; right half one photograph 656×796 | `nav` + `links` not in nav · `place.email`, address, `place.phone` · the hero's photograph | 5 rows | 5 rows |
| 1 | hero 100 vh: film behind, the name as a 1376-wide two-line wordmark at the foot, chevron (blinks, 2 s) | h1 = `brand.name` in two balanced lines · one large photograph | terraza-mesas-altas | gran-reserva-pasillo |
| 2 | headline module: h2 63 px centred (907 wide), paragraph 640 wide, button, one more line with a link | `hero.title` · `hero.text`, `hero.text2` · `hero.primary` · `hero.note` (phone linked) | yes | yes (no note) |
| 3 | gallery: four upright tiles 320×427, gap 32 | 4 photographs (places first) | 4 dishes (it has no other tiles) | sala, salón, mostrador, bodega |
| 4 | content module: film 672×896 left, right a 27 px sub-head, paragraph, lines starting "- ", button; the text pins at 88 px | `statement.title` · `statement.text` · `trust[]` as the dashed lines · `hero.secondary` (unless it is the menu link) · picture: see "leaves the reference" | words only | band photograph + words |
| 5 | image teaser 100 vh: photograph, 12 px tag, h2 63, light button at the foot | `steps.title` · `steps.text` · a large room/exterior photograph; without one → a headline module | barra-2400 | gran-reserva-barrica |
| 5b | (rooms page) cards 672 wide in two columns, gap 40/32: double frame, tag, name 45 px, text 576 wide at 55 % ink, picture 600×400, rule, call | `place.spaces` {title,text,img} — else `steps.items` {k→tag,title,text,img,cta}; foot call = the item's `cta`, else `place.booking` | 3 cards with their pictures (two are 418 px and stay 418) | 3 word cards |
| 6 | image teaser (the restaurant) | the `links`/`nav` entry that points at `place.menu.h` (t → h2, d → tag) · button `hero.secondary` when it is that link · a dish photograph | salmon | maridaje-copa-2 |
| 6b | (menu panel) ruled rows; (rooms page) cards | `menu.sections` without dishes + `menu.lists` → rows in two columns, name left, `count` right · a section with dishes → a card with name / note / price rows | 14 rows + Postres card | left out (no sections) |
| 7 | gallery: two uprights 672×896 | two photographs that cover 672×896 unenlarged; if there are not two, a third row of four tiles (dishes first) | row of four | left out (3 tiles left) |
| 8 | — (reference has none on this page) | `catalogue` → cards with priced rows · `plans` → cards · `place.events` → content module (what / when / "- price", "- where" / button) · `faq` → ruled rows that open | none | the Thursday dinner |
| 9 | headline module "Our other restaurants" + paragraph + button | `close.title` · `close.text` · `close.cta` (else booking) · `place.hours` as the lines under the button | with hours | title + button |
| 10 | gallery of four | 4 more tiles (dishes first) | 4 dishes | left out |
| 11 | full-width photograph 1440×960 | one large photograph (exterior/room first) | gintonic | left out (the only one left is a second view of the menu teaser's glass) |
| 12 | footer on the accent, 748 high with a halftone picture; a 400×400 card of the page ground: wordmark, then mail / address / phone 16 px caps; below, a link row and a social icon | card: logo + name · mail, address, phone, `place.hours` · row: `place.takeaway` (the newsletter link's place), `nav` + `foot.links`, `place.social` as words · `foot.legal` · `place.notices` | card + 6 links | card + takeaway + 10 links + FEDER notice |

Not placed: see `needs.json` "drops".

## Measures used (1440 → 390)
Page margin 32 → 16. Modules 40 above/below → 24. Headline module padding 120/32/40 → 80/16/24, gap 40. h2 63/1.2, +0.05 em → 36.
Sub-head 27/1.3 → 18. Rows 23.4/1.31, 24.3 padding (80 high) → 18, 63 high. Card name 45/1.25, 24 padding → 26, 16. Body 16/1.45.
Button label 700 14/1.4, +0.04 em, caps → 12. Tag 12/1.4 +0.04 em caps → 11 (the reference goes to 10; kept one pixel larger).
Button: 203 wide minimum, padding 12/48, two 1 px frames at 15 % ink (inset 0/4 and 4/0) → full width on a phone. Light button: frames at 45 % white.
Gallery tiles 3:4, gap 32 → two columns, gap 16. Pair 3:4 → one column, 74 % wide, first left, second right, 40 apart.
Teaser 100 vh, padding 40/32/64 → 24/16/40; tag 24 above the h2 → 16; button 48 below → 32. Cards: top padding 48 → 32; picture 36 in
from the card → 24; foot 32 in, rule, padding 24/24/32 → 16/20/20. Grid padding 80 → 56, gap 40/32 → 24. Full photograph 3:2.
Footer card 400² padding 32, top left → 286² padding 16, centred. Footer row padding 16/32 → 24/16, links in two columns.
Colours are relations: page ground; ink; rules = ink at 15 %; quiet text = ink toward the ground as far as 4.6:1 allows (reference 55 %);
the accent only as a field (menu panel, footer, and the hero when there is no photograph) carrying whichever of ink/ground reads at ≥4.6:1;
text on photographs = the page ground.

## Typefaces
Inbox (commercial, an art-deco display sans with small capitals) → **Josefin Sans** 400/700 (OFL), set in capitals, same tracking.
Neutraface (commercial) → **Jost** 400 (OFL). Josefin's capitals are wider than Inbox's, so a headline runs about a fifth longer and
wraps a word earlier; the name in the hero is sized from its longest line, not from the reference's 112 px capitals.

## Motion: measured → reproduced
- Header enters from above, 0.8 s → same. At the top it is clear with light text and the mark is 1.42× and 8 px lower; after the first
  pixels of scroll (class change seen at y=60) it takes the page ground and dark text, mark back to 1× in 0.6 s cubic-bezier(.45,0,.55,1) → same.
  When the footer reaches the top it slides out (translateY −72) → same.
- Every module fades in once when it enters, opacity 1 s ease → same (only when scripts run).
- Button hover: the two frames move to inset 5 and 4 and turn solid, 0.2 s → same.
- Menu panel: opens with opacity and −45 px → 0, 0.8 s cubic-bezier(.25,1,.5,1); closes 0.3 s cubic-bezier(.32,0,.67,0) → same (−5 vh).
  The reference's 0.5 s delay on opening and the cross-fade of the right-hand picture per hovered row (0.6 s) are not reproduced: one picture.
- Chevron blinks, 2 s → same. Links: colour 0.2 s → opacity 0.2 s.
- Content module: text column `sticky; top: 88px` beside the tall film → the sub-head is sticky at 88 beside the text column (only visible when the text is long).
- Nothing on the reference moves with scroll (hero, tiles, teaser pictures and footer were sampled at 17 scroll positions: all move 1:1) → none.
- Not reproduced: the films (places have no film); the room card's three-slide carousel (one picture per space); the card's hover shadow (value not read).
Reduced motion: no animation or transition, modules visible from the start (checked: 0 animated, 0 hidden). Without scripts: everything
visible, header on the page ground, menu button absent, the nav links stand in the footer row (checked: `probe/checks.mjs`).

## Where it leaves the reference, and why
- **Picture beside text** (module 4) is against the owner's rule: the picture becomes a band across the full measure (8:3, 3:2 on a phone)
  above the text, and the text keeps the reference's two columns (sub-head left, lines right). Without a spare large photograph: words only.
- The reference shows "Menu", "Close" and "Scroll"; the data has no such words: a two-line mark, a cross, a chevron; accessible names from a fixed list by language.
- No "View details" link, persons/size line or ornament in the cards: no data for them (the ornament is the reference's own drawing).
- Sections of the menu are not on the reference's home page at all; they are built from its menu-panel rows and its room card. Rows keep the name
  left and the count right on a phone, where the reference centres its rows.
- Footer: the reference's halftone picture is its own artwork. Ours takes a spare large photograph if one is left (neither client has one), otherwise
  the plain accent, and then the field is only as high as the card — 748 px of empty colour would be filler.
- Veils: the reference darkens only the foot of its pictures; ours also darkens the top 14 % (header labels) and holds 0.52–0.84 black behind the
  words so the readability gate passes on a white plate and a bright corridor.
- Two views of one subject (`x.jpg`, `x-2.jpg`) are treated as one picture, so a page never shows the same dish or glass twice.
- A photograph flagged small is never a backdrop or band, and a tile or card only takes a photograph it does not enlarge. Backdrops are enlarged at most 1.25.

## Image slots (in the order they are filled)
hero 1440×900 · spaces teaser · menu teaser (dish first) · full 1440×960 · content band 1376×516 · tiles ×4 · pair ×2 (or tiles ×4) · tiles ×4 · footer 1440×748 ·
cards: each space's own `img`. No made pictures. butarque uses 19 of 52, balamo 8 of 20 (+ the notice image).

## Checks at the last build
`tools/shots.mjs` — butarque d: height 10285, sideways 0, distorted 0, h1 1, errors [] · m: 9358, 0, 0, 1, [] ·
balamo d: 7034, 0, 0, 1, [] · m: 6704, 0, 0, 1, [].
`tools/legible.mjs` — butarque `ok — 0 unreadable of 279 line readings` · balamo `ok — 0 unreadable of 160` · balamo with no photographs `ok — 0 of 167`.
(On the way: two 12 px tags on teasers at 3.67 and 3.82, and balamo's name on the bright corridor at 2.95 — real failures, fixed with the veil.)
`tools/coverage.mjs` at 1440 — reference **77 %** (per screen 100,31,53,81,98,96,49,91,100,69; 7 wide) · butarque **52 %**
(100,27,57,68,30,62,47,6,40,82,73,0; 7 wide) · balamo **53 %** (100,36,69,84,18,93,9,4; 4 wide) · balamo without photographs 1 %.
**Ours is 24–25 points under the reference; the 5-point rule is not met.** Every wide picture of the reference has its slot here (hero, two
teasers, full photograph, footer); what lowers the share is (a) the cards, rows and priced lists that the reference keeps on sub-pages,
(b) no pair of 672×896 uprights and no footer picture for either client, (c) for balamo no full photograph and one tile row.
`probe/checks.mjs` — scripts off: nothing hidden, footer carries the nav · reduced motion: 0 animations, 0 transitions, 0 hidden · focus: 2 px
solid outline on the first six stops at both widths · pictures enlarged: only backdrops, at most 1.25 (salmon 1.21, gintonic 1.20, barrica 1.25,
pasillo 1.16, reservado 1.11, copa-2 1.07) · no text under 11 px.
One-file: `out/butarque-one-file.html` 1.1 MB, `out/balamo-one-file.html` 1.3 MB, nothing left outside.
No photographs (`probe/nophotos.py`, data untouched): `out/balamo-nophotos.html`, `out/butarque-nophotos.html`, and butarque with its first five.

## Not checked
Other browsers than Chrome; widths between 390 and 1440 other than by eye at those two; 1920 and wider; the open menu with a screen reader;
the one-file pages were not re-shot; `plans`, `faq` and `catalogue` render paths have no test client here and were not looked at.


## Engine import fixes (2026-11-12, stress: plans 1/3/5, features 2/9, steps 1/6, 12-word h1, 40-char button, no faq, no photographs; clients casaolmo and larchwick; 1440 and 390)
- Over an opening with no photograph (the deep colour), the header at the top takes the deep colour's ink (`on-deep`), as it takes the light ink over a photograph. Before, it kept the dark ink on the dark opening (2.06:1 and 2.83:1 with no photographs).
- The header's booking label stands on one line. Where it would wrap (a long label on a phone: four lines spilled below the 62px header onto the pictures, 1.02:1), the script measures it and moves it into the menu, which carries it as its last row; with no other menu rows the menu button appears only for that case.
