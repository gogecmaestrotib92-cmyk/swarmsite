# What capture and the reader must learn so that a real capture fills the templates' contract

A plan, not code. Written 2026-11-12 on branch `template-engine-7-capture-plan`.

Three kinds of statement are kept apart: **measured** (a number read off a run, with where it came from), **read in
the code** (file and line on this branch), **proposed** (not built, not measured — every time and cost under
"proposed" is an estimate and says so).

## Where things stand — measured

**What the adapter (`lib/templates/adapt.py`) gets out of the eight frozen captures** (`bench/seed/`, captured
2026-11-08/09; PR #30): against the hand-made data files, leaf by leaf — butarque 113 the same / 25 differ / 90
missed, sportbot 68 / 41 / 80, automateed 25 / 66 / 78. `media.screens` and `media.phones` are empty for all eight.

**What selection (`lib/templates/select.py`) then offers** (PR #31, 25 `needs.json` of the research folder at 11:27):

| client | hand-made data | data from the frozen capture |
|---|---|---|
| sportbot | bevel, butter, fluently | griffin, terminal, cerebrium (all type-led) |
| automateed | griffin, bevel, butter | terminal |
| courtsensei | — | cerebrium |
| scanmysaas | — | griffin, terminal, cerebrium |
| pdfbeautifier, simscore | — | none |
| butarque | brecon, schulhaus, bokman | none |
| balamo | brecon, bokman | none |

**Where two restaurants' photographs really are** (`CAPTURE-NOTES.md` in the research folder, measured on the live
sites): Butarque 52 photographs kept, 40 of them on pages other than home; Bálamo 20, all 20 on other pages. A capture
that reads `<img src>` of the home page from the raw HTML gets 0 of 52 and 0 of 20; from the rendered, scrolled home
page 11 of 52 and 0 of 20. The frozen captures had 5 and 0. 62 of the 72 kept photographs are under 1000 px wide;
Bálamo has none at 1600. 17 of 71 files opened on Butarque and 7 of 46 on Bálamo were not photographs of the place
(stock tiles with lettering, brand shots, flyers, drawings): "a size floor is not enough … someone has to look".

**What today's capture already does that the frozen captures did not** (read in the code, `lib/pipeline/capture.mjs`
on this branch — the seeds are older than this code, so its effect on the eight sites is **not measured**):
- `imagesSrc` (lines 20–62) reads the rendered page after a scroll: `currentSrc`, the widest `srcset` entry,
  `data-src` / `data-lazy-src` / `data-original` / `data-srcset`, `<picture><source>`, the WordPress original behind
  `-300x200`, `video[poster]`, computed `background-image` on every element (≥ 280×180 box), one still of each
  playing `<video>`. It keeps **at most 20 pictures a page** and **stores each at most 1400 px wide** (line 45).
- "Linked pictures" (lines ~190–215): up to **6** same-site pages linked from home are opened for their pictures,
  **4 pictures a page, 12 in all**, inside a **40 s** box (`SWARM_PICTURE_PAGES_MS`). A sub-page picture carries
  `page: <the link's label>` — the label, not the address.
- `visualShots` (line 93): up to 10 shots of framed elements of the page.
- `lib/audit/inventory.js`: text by `innerText` (line 7, so CSS capitals arrive as capitals); `a[href]` kept to the
  first **100** (line 94); sections with flattened text, FAQ pairs, quote/caption pairs (lines 222–242); structured
  data kept as a count of types only (lines 320–321).
- The reader (`lib/swarm/agents.py` 137–178): one model call (`claude-sonnet-5-5`, up to 7000 output tokens) writing
  `what, language, tone, facts[], offers[{name, price, note}], quotes[], capabilities[], people[], contact[],
  best_sentence, business_understanding, missing[]` — free strings.

## The gaps, ranked by how many templates each unlocks

"Unlocks" is counted on the 39 `needs.json` of the research folder as normalised at 13:09 (PR #33). It is the number
of templates that **state** the need — not a promise that they will then be offered: most templates state several.
Nine of the 39 also need made pictures, which is the picture library's work (`lib/templates/pictures.py`, planned), not capture's.

| # | gap | templates that state it (of 39) | deterministic? |
|---|---|---|---|
| 1 | which shots are product screens; phone screens | 16 need `screens_min ≥ 1` (16 of the 20 software/app templates) | deterministic capture + one yes/no per picture from the reader |
| 2 | photographs: all of them, at their own size, with page and role | 16 need photographs, 15 of them four or more; 11 need large ones; 13 say which roles they want (`photos_by_role`); three read `page` (CONTRACT.md) | deterministic, role needs the reader |
| 3 | which picture belongs to which step / room / person | 15 need a picture to each step, room or person | deterministic |
| 4 | sections with their borders: figures, plan rows, kickers, foot | 26 need `steps`, 19 `features`, 17 a `statement`, 12 `figures`, 7 a `close`, 6 `plans` | deterministic |
| 5 | kinds that are not software or a restaurant, and their blocks (team, catalogue, locations, credentials, contact, projects) | 15 templates are for clinic, law, service, shop, school or person; 7 need one of the new blocks | reader (extraction into fixed fields), confirmed deterministically |
| 6 | a film: its file, size and poster | 1 needs `video`, 9 say they do not show one; Bálamo's first screens are films | deterministic |
| 7 | place facts the capture misses: country, split town/region, hours from structured data, menus on another host | 11 restaurant/hotel/venue templates, 9 of which need menu, rooms, hours, address or phone | deterministic |
| 8 | label casing; the 100-link cap; in-page nav | all | deterministic |

### 1. Product screens and phone screens
- **Gap.** `media.screens` and `media.phones` are always empty (adapter gap 1). The capture has shots, but nothing
  says which shows the product; none is taken at phone width.
- **Where.** `visualShots` in `lib/pipeline/capture.mjs` (line 93) already knows *what kind of element* each shot is
  (framed UI, video, canvas, big image, card with shadow) and throws that away: keep it as `shot.kind`, with the
  element's own size and whether it holds an `<img>` whose file is the whole of it. Run the same pass in the mobile
  context (the loop at line ~150 already opens one at 390) and keep phone-proportioned framed elements as
  `shot.phone = true`. Then the adapter can place `kind: 'ui'` shots in `screens` and upright ones in `phones`.
- **Deterministic or model.** Recording the kind is deterministic. Whether a framed element is *the product* or a
  marketing card ("Now on iOS & Android") is not: add one field to the reader's tool (`agents.py` 138) —
  `screens: [shot ids that show the product's own interface]` — and send it the shots it already receives. No extra
  call. The adapter uses a shot as a screen only when the reader names it **and** capture's kind is `ui`.
- **Test on fixtures.** The eight seeds: sportbot must yield 0 screens from its section shots (the hand file used
  none of them), automateed `shot2` and `shot3` (the hand file used both). A unit fixture page with a framed UI
  mock, a marketing card and a photograph: only the first becomes a screen. Selection table re-run: the software
  rows must gain templates with `screens_min ≥ 1`.
- **Cost per job (proposed, estimate).** Capture: the mobile shot pass, about +3–6 s. Reader: no new call; a few
  hundred output tokens more.
- **Also** the product's real screens often are not on the marketing page at all (sportbot's were captured from the
  app by hand). That is the flow "URL + screens" (a developer uploads them) — outside capture; the form is in the
  owner's list of flows.

### 2. Photographs: all of them, own size, page, role
- **Gap.** Too few, too small, no role. Measured above: 5 of 52 and 0 of 20 in the frozen captures.
- **Where.** `imagesSrc` and the linked-pictures loop in `capture.mjs`:
  1. **Caps** — 20 a page, 6 pages, 4 a page, 12 in all, 40 s. Butarque needs 12 page loads for its 52; the caps
     give at most 32 and in practice far fewer. For the template path: all same-site pages one link from home (up to
     ~12), no per-page cut of 4, a total around 60, the time box raised to match.
  2. **Size** — line 45 stores at most 1400 px. Large is ≥ 1400 (decided today), so a 1900 px file stored at 1400
     still counts; but the package should carry the file as the site serves it. Keep the original bytes (the
     response body) beside the 1400 px working copy and record the original's `w`/`h`.
  3. **What it misses** — slider attributes (`data-lazyload`, Revolution Slider: both of Butarque's 1900×800
     pictures), pictures seen only as network responses (listen to `response` events for images as a net), and the
     file names the `/logo|icon|avatar|sprite/` filter drops by accident.
  4. **`page`** — store the page's address (now: the link label), as CONTRACT.md asks; three templates read it.
  5. **`small`**, `w`, `h` are already there once (2) is done.
  6. **Role** (dish | room | bar | exterior | people | work | workshop | portrait | product | detail | landscape |
     action | other) and **"is this a photograph of the business at all"** — the notes measured 24 of 117 files that
     are not. Deterministic signals go some way (lettering: OCR-free proxy — the flat-tone test at lines 47–50
     already drops notices; the file sits in a `product-category` grid; alt text). The rest needs eyes: the reader.
- **Deterministic or model.** 1–5 deterministic. 6: one reader field `photos: [{id, role, of_the_business: bool}]`
  over thumbnails. That is the costly part: 60 thumbnails at ~250 px are on the order of 60 × 100–200 input tokens
  each — **an estimate, to be measured on butarque before it is switched on**.
- **Test on fixtures.** A local fixture site (the repo already serves fixture pages in `tests/capture-linked-pictures.mjs`
  and `tests/test_capture_images.mjs`): lazy `data-src`, `data-lazyload`, a CSS background, a sub-page, a 1920 px
  file, a lettered tile. Assert: every photograph found once, at its own size, with its page; the tile marked.
  Then the two restaurants live, against the counts in CAPTURE-NOTES.md (52 and 20) — a job run, with the owner's
  go-ahead, since it is a paid run.
- **Cost per job (proposed, estimate).** Capture +20–60 s (6 more page loads and the downloads). Reader: the
  thumbnails; unmeasured.

### 3. Which picture belongs to which step, room, person
- **Gap.** `steps.items[].img`, `place.spaces[].img`, `team.items[].img` are never set: the capture has pictures
  and headings but not which picture stands in which block.
- **Where.** `lib/audit/inventory.js`, where sections are cut (`sourceCoverage.sections`): for each heading (h2/h3)
  record the pictures inside its own block — nearest common ancestor that holds exactly that heading — as
  `pictures: [image ids]`. `imagesSrc` must then give each picture an id that inventory can refer to (today the two
  run separately; give both the element's source address as the key). Geometry (`geometrySrc`, line 133) already
  has rects for headings and images and can confirm by position.
- **Deterministic.** Yes — DOM containment, then position. No model.
- **Test on fixtures.** A fixture page with three cards (picture + h3 + text) and one picture that belongs to none:
  three pairings, one left free. Butarque's three rooms (the hand file pairs terraza/salon/chill-out by eye).
- **Cost per job (proposed, estimate).** Under a second.

### 4. Sections with their borders
- **Gap.** A section's text arrives flattened (`text` of a coverage section), so the adapter can only take whole
  sentences and must drop what follows the last full stop. Lost: `figures` (a number and its label), `plans.items[].rows`
  / `line` / `marked`, `steps.items[].k`, `hero.note`, `trust` (the last tick), `foot.text`, `place.events`,
  `place.notices`, and any home page without h1/h2 (butarque: no headed section at all).
- **Where.** `lib/audit/inventory.js`: beside `text`, keep `blocks: [{tag, role, text, href?}]` — one entry per
  block-level text element in order (p, li, h3, h4, a/button, a number set large). `role` from the element: `kicker`
  (small text right above a heading), `figure` (a text node that is mostly digits at ≥ 28 px with a sibling label),
  `row` (li), `price`, `action`. Sections without a heading: cut by the page's own top-level blocks (the `sections`
  list already has 16 entries for sportbot by tag) instead of by headings only.
- **Deterministic.** Yes.
- **Test on fixtures.** A fixture pricing section (two cards, five rows each, one marked), a figures band, a hero
  with a note: the adapter's output must equal the hand-written data for that fixture, field by field. The seeds:
  sportbot's 4 figures and 2 × 5 plan rows (the hand file has them; the adapter has 1 and 0).
- **Cost per job (proposed, estimate).** Negligible in time; inventory.json grows by roughly a third.

### 5. Businesses that are not software or a restaurant
- **Gap.** `kind` knows software and places. CONTRACT.md now has clinic, law, service, shop, school, person (seven
  real test clients) and the blocks `team`, `catalogue`, `locations`, `credentials`, `contact`, `projects`. Nothing
  in capture or the reader produces them; 15 of the 39 templates are for these kinds.
- **Where.** The reader (`agents.py` 138–149). Its fields are free strings that the adapter has to parse back
  ("Address: …", "Hours: …"). Replace the parsing with fields: `kind` (from the fixed list of
  `needs.schema.json`), `team[{name, role, text, picture id}]`, `catalogue[{group, name, price, note}]`,
  `locations[…]`, `credentials[…]`, `contact{phone, email, form}`, `projects[{title, text, picture ids}]`, and for a
  place `address{street, postcode, city, region, country}`, `hours[{days, open, close}]`. **The adapter's rule does
  not change:** a value goes in only when the capture confirms it letter for letter (the test that finds every
  output string in the capture stays as it is). So the reader says *where things are*; it cannot add a word.
- **Model.** Yes, the one reader call that already runs; more output (a long catalogue). Capture side, deterministic:
  the sub-pages these facts live on (team, prices, contact) must be among the pages read for text — today only
  the landing page's text is read unless the job is site-wide (`siteWide`, line ~180).
- **Test on fixtures.** The seven hand-made files (clinic1 … person1, research folder) are the answer sheet once
  those sites are captured: leaf-by-leaf comparison as in PR #30, per kind. Before that, unit fixtures: a reader
  reply with one invented team member → the adapter drops it and says so.
- **Cost per job (proposed, estimate).** Reader output grows — unmeasured; from the price table ($2 / M in, $10 / M
  out) each 1000 more output tokens are $0.01. Reading 3–5 more pages for text: +10–20 s of capture.

### 6. A film
- **Gap.** `media.video` is always null. Capture counts videos and may save one clip (`hero.mp4`) without size or
  poster. Bálamo's first screens are films and it has no still picture on its home page.
- **Where.** `imagesSrc` lines 53–60 already reads each `<video>`'s frame: also record `{src, w, h, duration}` and
  keep the frame as the poster. Download the file only when it is the page's first-screen film and under a size
  limit (Bálamo's are 0.9–5.8 MB).
- **Deterministic.** Yes.
- **Test.** Fixture page with a muted looping film: `video{src, poster, w, h}` filled; a 40 MB film: poster only.
- **Cost per job (proposed, estimate).** The download: seconds; +1–6 MB of job storage.

### 7. Place facts
- `country`: never on the page; take it from the structured data (`addressCountry`) — capture must keep the
  structured data itself, not only its types (`inventory.js` 320–321). The same gives `openingHours`, `priceRange`,
  `servesCuisine` first-hand instead of through the reader's quotation; conflicting entries (Bálamo has two) → left
  empty, as now.
- Town and region printed with nothing between them ("Alcorcón Madrid"): split with the structured address when it
  is there; otherwise leave as it is.
- A menu on another host (Bálamo's `carta.` site): follow one same-registrable-domain link named menu/carta.
- Deterministic; tests are fixture pages with JSON-LD; cost: one more page load at most.

### 8. Small things with wide effect
- **Label casing.** `inventory.js` line 7 reads `innerText` (CSS capitals as capitals); the adapter then puts the
  casing back word by word. Record `textContent` beside it for labels (nav, buttons, headings): exact, and the
  recasing rule becomes a fallback.
- **The 100-link cap** (line 94) cuts the foot's legal links on long pages (sportbot has none): keep all links of
  `<footer>` apart from the cap.
- **In-page nav** (`#features`): keep the target section's id with each coverage section, so that the adapter can
  point a nav link at the block that section became.
- All deterministic; unit fixtures; no time.

## Order of work (proposed)
1. **3 and 4 first** (inventory.js only, deterministic, cheap): they turn data the capture already holds into
   steps with pictures, figures, plan rows — and they need no paid run to test.
2. **2** (photographs) — the restaurants' rows are empty without it; needs one paid run per restaurant to confirm
   against CAPTURE-NOTES.md.
3. **1** (screens) — the software rows; needs the reader field.
4. **5** (other kinds) with the capture of the seven test sites; **6, 7, 8** alongside.

## What each visitor costs (the owner's decision: three previews before sign-up)
The template path has **one** paid call, the reader. Its cost is **not measured** in the frozen jobs (their
`swarm.json` holds no usage). From the price table (`lib/prices.json`: `claude-sonnet-5-5` $2 / M input, $10 / M
output) and the reader's limit of 7000 output tokens: at most $0.07 of output a visitor, plus the input (the page
text and a handful of pictures) — to be read off the ledger of the first template job and written here. Gaps 2 and 5
raise it; that is why their reader fields are to be measured on one site before they are switched on for anonymous
visitors.

## Beside capture: made pictures from the prepared library (planned — `lib/templates/pictures.py`)
The owner's decision of today: a preview takes its made pictures from a library prepared in advance, never from a
generation at preview time. Nine of the 39 templates need made pictures and cannot be offered without them.

**Read in the research folder (13:15):** `media/library/library.json` lists 150 pictures:
`{family, palette, slot, kind, src, w, h, tone, mean, scene}` — six families (nature 50, space, ribbon, aurora, tech,
material 20 each), six palettes (navy, warm-cream, forest-green, teal, indigo-violet, oxblood), slots wide-lead,
texture, mid, soft, wide-quiet, glow, field, tile; `mean` is the picture's mean colour, `tone` dark or light.
`build.py` there does not read it yet.

**Proposed** `pictures.made_for(d, motif, library) -> media.made`:
1. The client's palette → the nearest library palette: distance in a perceptual colour space (the repo has OKLCH in
   `lib/colour/palette.py`) between the client's `palette.accent` (hue) and `palette.ground` (tone) and each
   library palette's own colours, read from the `mean` of its pictures. Ties by palette name. Deterministic.
2. The template's `motif` (land, sky, sheet, blur, field) → the family and slots that carry it; the contract's fixed
   order of `made.land` (0 ridge … 5 wide, empty) → the library's slots (wide-lead, mid, texture, soft, soft,
   wide-quiet). This mapping has to be written down by whoever made the library; it is not in `library.json`.
3. The dark-page rule of the contract (a dark page never takes a `tone: light` picture for a large ground) is applied
   when choosing between a palette's dark and light variants.
4. Output: `media.made` in the contract's shape with `src` under `media/library/…`; the files are shared by all
   clients, served once, and copied into a package only when the page uses them (`registry.media_used` already
   answers that).
- **Tests:** a made-up library of four palettes: the nearest is chosen for six client palettes, the same every time;
  a dark page never gets a light ground; a motif the library lacks → `made` without that kind (the template's plain
  ground). Then `select(d, promised=('made',))` becomes `select(d)` on data that has them.
- **Cost:** no model, no network; milliseconds. The 150 files must be in the deploy (their total size is not
  measured here).
- **Open:** the library is still being made (two palettes cover 110 of the 150); whether it ships in the repo, in
  the image, or in storage.
