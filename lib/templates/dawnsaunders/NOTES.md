# dawnsaunders — template from https://dawnsaunders.com (measured 2026-11-12, 1440 and 390)

An author's and speaker's own site: type-led, three grounds (accent yellow, black, white), Figtree light at giant sizes,
Forum for reading text, pill buttons, 32 px card radii, half discs and 2:1 arches as its only shapes.
Test clients: person1 (a mountain guide, primary), law1 (a 35-person solicitors' firm, for robustness).

## What depends on the cut-out, and what was built instead
The reference's first screen is a CUT-OUT portrait (hero-seated-cutout.webp, 2000×3000, transparent) standing through the
word "dawn" (489.6 px Figtree 300, white on yellow) and in front of a black half disc (833×417, radius 999 999 0 0).
The word is behind her and in front of the yellow; that interleaving only works with a cut-out.
A client with ordinary photographs gets: the same word, the same black half disc, and the photograph in an arch window
(641 wide at 1440 = the cut-out's own column; top radius 999 px, rising to the foot of the word, cropped to cover,
held to the photograph's own pixels). The word stays whole above the arch instead of being cut by the head.
A client with a cut-out could have the reference's build; the contract has no field for it (suggest `photos[].cutout`).
With no portrait the arch and its disc are left out: the first screen is the word and two columns of type.

## Sections (reference → ours → data)
1. Opening, yellow, 900 high: giant first name + dot, h1 left (41.8 px/300), Forum 20.9 px paragraph right, portrait centre
   → `brand.name` first word, `hero.title`, `hero.text` (whole sentences ≤340 chars) and `hero.text2` if ≤120 chars;
   portrait: team member whose name is the brand / the only team member / largest people photograph.
2. Statement in a yellow half disc hanging from the top of a black section (1066×533 at 1440), 51.8 px/300 centred with
   bold words → `statement.title` (bold) + `statement.text`; three size tiers by length. The rest of `hero.text` and
   `hero.text2` follow as a Forum lead below.
3. "My recent books" centred heading 63 px + Forum 26 px → `steps.title/text`.
4. Book cards: two per row, 690 wide, 20 gap, radius 32, alternately yellow and rgb(12) black; each opens with a 245 px
   word + coloured dot, then the cover, a Forum meta line, h3 40 px/300, Forum 22 px, two pill buttons
   → `steps.items`: word = the title's first word, the step's photograph edge to edge across the card (the cover's slot;
   a book cover is boxed in the reference, a photograph here runs to the card's edges), `k` as the meta line, call.
   An odd last card spans both columns with its photograph as the right half.
5. Photograph band 1400×1000, radius 32, brightness .72 + gradient veil, 86 px/300 white sentence with a yellow second half,
   white pill → the widest free photograph (not small, ≤1.6× upscaled), `statement.title` as the sentence, `hero.secondary`.
6. Readers' shelf, yellow, 140 px padding: title + "4.9 out of 5", then a row of 73 px spines (names set upright,
   alternately 8 % black and white) with one 732 px open black panel (Forum 30 px quote, yellow name); dots below;
   moves on by itself → `figures` as the row above (value 44 px/300 + Forum label; there is no rating in our data),
   `quotes` in the shelf (title / role at the panel's top corners). The same shelf on the white ground carries
   `team` (up to ten people with portraits: the portrait is the right 40 % of the open panel, edge to edge).
7. Letters, white, 100 px padding, two columns 621 + 86 gap, left column sticky at 110 px, a yellow featured card
   (radius 28, 36 padding) and ruled rows (52 px label column, Figtree 27 px title, Forum 17 px sub, date right)
   → the ledger for `catalogue` groups (group title + text + link left; first priced item with text as the yellow card,
   the rest as rows with prices right), `plans` (quiet cards, the marked one yellow), one-person `team` (name, role,
   trust lines left; bio card + credentials right), `credentials` (badge in the label column), other `trust`.
8. FAQ, black, 1200 wide, gradient rule on top, 403 px left heading / rows right, 27 px/300 questions, 42 px ring with +
   → `features` (first open: the visitor sees one answer) and `faq`.
9. Invite pair: yellow card (63 px/300 heading, Forum 26 px, pill) beside a whole photograph card 690×699
   → `close` + every way to reach (phone, email, address, hours, form, routes not already in the foot) + one more
   photograph; without one the call card runs full width.
   `locations` → three columns before the foot (the reference has none; built from its foot columns).
10. Foot, black: logo (first word in yellow), Forum blurb, two link columns, small print; then a 245 px "Begin again." on a
    yellow half disc → `foot.text`, `links`/`nav`, `foot.links` + `place.social`, `foot.legal`; the giant line is the
    client's whole name (the reference's line is its own words; ours must not invent a slogan).

## Measures used
Header fixed, 84 high (64 on phone), accent ground, logo 34 px (700 first word / 400 rest, −0.035 em), links 20 px/500 gap 34,
call 20 px/500 pill 14×24. Side padding 56 (20 on phone); card gutters 20 (12 on phone). Type scale in units of
min(1vw, 19.2 px) so 1440 reproduces the measured px: word 34u, statement 3.6u, section titles 4.4–5.4u, h3 2.8u.
Phone build as measured: logo 24 px + burger (three 24×2 bars); word 132.6 px; cards stacked; shelf as horizontal rows
64 high (star, name, dot) with the open one 460 high; headings 35.1 px; Forum 18.72 px.

## Fonts
Figtree (open licence, Google Fonts) is the reference's own face — used as is. Forum (Google Fonts) is also the
reference's own reading face. No stand-in was needed.

## Colour
The reference's relations are kept, the client's palette goes in: accent = page accent (header, opening, cards, shelf,
call card); dark = the darker of ground/ink; light = the lighter. The giant word takes the light/dark that is not the
accent's ink (white on yellow in the reference; dark on person1's blue, which white text needs). Every soft ink
(the reference's 60–75 % whites/blacks) is held back only as far as 4.6:1 on its own ground.

## Motion (measured with Playwright, reproduced)
- Reveal: sections rise 22 px and fade, opacity .8 s ease + transform .8 s cubic-bezier(.2,.8,.2,1), delays 0/.08/.16 s,
  fired on entering the view (statement at scroll ≈200). Reproduced with IntersectionObserver; the statement disc
  fades in place (.6 s, .08 s delay).
- Nothing is pinned but the header; nothing moves with scroll (no parallax: positions sampled at 19 scroll depths
  move 1:1). The letters column is sticky at top 110 px — reproduced on the ledger's left column.
- Shelf: auto-advances about every 5.3 s (changes at 5.1 s and 11.1 s; it did not pause on hover), open item flex 1→10
  over .7 s cubic-bezier(.2,.8,.2,1), colours .5 s; click a spine to open it; dots widen 8→28 px over .4 s.
  Reproduced with radio inputs (works without script and by keyboard); the timer only runs while the shelf is in view.
- Hover: buttons lift 2 px (.25 s); header call inverts; nav links get a glow in the reference — ours a 2 px underline
  (a glow on our accent would be a halo); letter rows indent 12 px (.3 s); FAQ ring fills (.3 s).
- FAQ open/close is instant in the reference (no transition on details) — ours the same; the + turns to −.
- Reduced motion: all transitions off, reveals shown, shelf timer off. Without script every section is visible.

## Picture slots
portrait (arch) · step pictures (from `steps.items[].img`) · band (widest free) · shelf portraits (team) · pair card.
Each photograph is used once; `small` photographs are never shown wider than their pixels and never in the band.
First screen: only a portrait/people photograph — never a landscape, so a picture with lettering baked in (person1
hero.jpg, "YOU ARE HERE") cannot open the page. Any photograph whose alt mentions words, a caption, a sign, a logo or
a quoted phrase is also ranked last in every slot. Data cannot see lettering; capture should run OCR and set
`photos[].lettered` (the template already reads it). person1's hero.jpg still reaches the band (the only free wide
photograph); its lettering sits top right, the band's sentence bottom left.

## Readings
- shots.mjs: person1 1440 h 10894 / 390 h 12902; law1 1440 h 12809 / 390 h 18570 — sideways 0, distorted 0, one h1, errors [].
- legible: person1 ok, law1 ok. Variants (scratch copies of the data): 3 and 5 plans, 1/3/6 steps, 2/9 features,
  12-word h1, 40-character button, with faq, no photographs, 30-character name — ok. Two runs (1 plan, law1 without
  photographs) printed FAILs on the phone shelf only: the crops show one item caught in its .5 s colour/fade change
  because the shelf's 5.3 s timer advanced while the gate was reading (a closing spine still yellow-on-yellow, an opening
  quote at a third of its opacity). The same lines pass on every other run. Measuring artefact of timed motion: the gate
  freezes requestAnimationFrame and CSS animations but not setInterval or CSS transitions.
- coverage: reference 24 % (2 wide screens); person1 22 %; law1 7 % (page 1.58× the reference: lists stay type, no
  unused large photograph to break them).

## Could not be transferred
- The cut-out interleave (above). The book covers' drop shadow on yellow (a boxed picture; ours runs to the card edges).
- The rating block ("4.9 out of 5") — no such data. The letters' dates — the ledger shows prices in that place.
- Nav link glow (see Motion).
