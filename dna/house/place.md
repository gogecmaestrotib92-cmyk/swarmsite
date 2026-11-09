# House structure: PLACE landing pages (restaurants, hotels, bars, cafés, wellness)

Research date: 2026-11-09. Method: WebSearch to locate sites, WebFetch of each homepage's text (no browser). Counts of photographs and words are approximate, derived from the fetched markup; JS-rendered media may be under-counted (flagged per site).

## Corpus

| # | Site | Type | Why it is in the corpus | Fetch |
|---|------|------|-------------------------|-------|
| A | tastavents.com (Restaurante Tastavents, Badalona) | restaurant, Michelin-selected 2026 | Awwwards Honorable Mention (listed as "Tastavents Restaurant - Awwwards Honorable Mention") | ok |
| B | thewittmore.com (The Wittmore, Barcelona) | boutique hotel | Awwwards Honorable Mention, 19 May 2024 | ok, text only; images not exposed in markup |
| C | noma.dk | restaurant, reference | brief | ok |
| D | aman.com | hotel group, reference | brief | ok |
| E | sixsenses.com | hotel/wellness group, reference | brief | ok |
| F | geranium.dk (Geranium, Copenhagen) | 3-Michelin-star restaurant | brief: Michelin-starred site | ok |
| G | lilianewyork.com (Lilia, Brooklyn) | independent neighbourhood restaurant, Resy | brief | ok |
| H (supplementary) | pellicanohotels.com/en/hotels/hotel-il-pellicano | independent luxury hotel | reference | ok |
| I (supplementary) | earls.ca | casual restaurant chain | Awwwards Honorable Mention ("Earls Restaurants Website") | ok |

Replaced / failed: frantzen.com (robots disallowed) -> replaced by geranium.dk; pulsohotel.com.br (Awwwards HM Nov 2025, robots disallowed) and jaegerhof.it (Awwwards HM Dec 2025, robots disallowed) -> replaced by thewittmore.com; alchemist.dk returned only a JS shell (nav + footer) and was dropped. Awwwards pages themselves do not expose the live URL to a text fetch, so awarded sites were matched by name.

---

## A. Tastavents (tastavents.com) — Awwwards HM, restaurant

| # | role | headline | visual | items | CTA |
|---|------|----------|--------|-------|-----|
| 1 | hero | "Un Viaje Gastronómico Único" | full-bleed photo + 6-tile photo strip | — | y: "Reservas" (header), "Regala" (gift) |
| 2 | story-about | "Presentación" | 3 feature photos | 3 (Espacio singular / Propuesta de autor / Oasis íntimo) + 8-item ingredient ticker | n |
| 3 | menu-or-rooms (cuisine) | "Ingredientes Exquisitos, Platos memorables." | 1 photo + ticker | 8-item ticker | y: "Carta de vinos" (external wine list), "Menú degustación" (PDF) |
| 4 | other (the room/space) | "Panorámicas que extasían y deleitan los sentidos." | photo pair | — | y: "Menú degustación" (PDF) |
| 5 | story-about (chef) | "Dídac Alcoriza" | photo pair (portrait + duo) | — | y: "Descubrir legado" (press article) |
| 6 | menu-or-rooms | "Homenaje al Producto, Gustos Genuinos" | gallery (5 photos) | — | y: "Carta de vinos", "Menú degustación" |
| 7 | reservation-form + location-hours | "Reserva Tu Mesa en Tastavents" | none | hours: 2 entries | y: embedded TheFork widget; tel; mailto |
| 8 | gallery | none (4 sub-galleries: Experiencias, Espacio, Propuesta, Oasis) | gallery (≈15 thumbnails, 34-image lightbox) | 4 galleries | y: "Ver galería" x4 |
| 9 | footer | none | Michelin 2026 badge | legal, address/map, credits | y: "Dirección" (map), "Teléfono" |

Totals: 9 sections; ≈1,000 words (with repeated tickers); ≈65 unique photographs (very image-heavy); reservation action: nav/header link + dedicated section with embedded provider widget (TheFork). No prices on page (PDF menu), no review quotes (Google "Reseñas" link in header only), no FAQ.

## B. The Wittmore (thewittmore.com) — Awwwards HM, hotel

| # | role | headline | visual | items | CTA |
|---|------|----------|--------|-------|-----|
| 1 | hero / story-about | "You are welcome." | full-bleed (not detectable in markup) | — | n |
| 2 | other (sun deck / garden) | "Sun Deck" | photo (presumed) | — | n |
| 3 | menu-or-rooms (rooms, unlabelled) | none | photo (presumed) | — | y: "See Rooms", "Book a Room" |
| 4 | menu-or-rooms (dining, unlabelled) | none | photo (presumed) | — | n |
| 5 | other (concept + house rules) | "Sound Hall" | photo (presumed) | 3 rules (adults only / no pets / no photos) | n |
| 6 | other (members) | none | none | — | y: "Members Access" |
| 7 | footer | none | none | back-to-top only | n |

Totals: 7 sections; ≈200 words (shortest in corpus); photographs not countable from text (site is a full-screen scroll of imagery with one sentence per screen); reservation action: mid-page "Book a Room" link (booking engine) only; no nav captured, no hours, no prices, no reviews, no FAQ.

## C. Noma (noma.dk)

| # | role | headline | visual | items | CTA |
|---|------|----------|--------|-------|-----|
| 1 | hero | "Copenhagen 2026-2027" | looping video + row of ≈10 photos | — | y: "Book a table" |
| 2 | other (banner) | none | 1 photo (NomaLA26) | — | n |
| 3 | other (newsletter) | "Sign up for reservation updates & news from noma." | none | — | y: "Subscribe" |
| 4 | other (shop) | "Bring home the flavors of noma with our collection…" | 1 photo | — | y: "Shop Noma Projects" |
| 5 | other (shop) | "Introducing the restaurant's very own coffee subscription…" | 1 photo | — | y: "Shop Noma Kaffe" |
| 6 | story-about (letter) | "Copenhagen 2026: We're coming home" | photo pair (header + team) | — | n |
| 7 | other (book) | "The Noma Guide to Building Flavour" | 1 photo | — | y: "Order the book" |
| 8 | other (sister venue) | "Welcome to Barr – A place to gather" | 1 photo | — | y: "Book your table" |
| 9 | other (non-profit) | none | 1 photo | — | y: "Learn More" |
| 10 | other (film) | "Omnivore on Apple TV+" | 1 photo | — | y: "Watch Omnivore" |
| 11 | events | "Noma LA 2026" | 1 photo | — | n |
| 12 | location-hours | "Contact" | none | address, phone, phone hours | y: "See map", "Contact" |
| 13 | location-hours / reservation | "Booking + Hours" | none | hours (Wed–Sat 17–23) | y: "Reservations" |
| 14 | other (careers) | "Careers" | none | 1 | y: "Join our team" |
| 15 | footer | none | none | 4 + 4 links | n |

Totals: 15 sections; ≈1,000 words (≈390 of them the letter); ≈20 photographs (10 in hero strip, 1 per card after); reservation action: hero button + nav "Reservations" + "Booking + Hours" near footer (link to booking system). No menu, no prices, no reviews, no FAQ.

## D. Aman (aman.com)

| # | role | headline | visual | items | CTA |
|---|------|----------|--------|-------|-----|
| 1 | other (region shortcuts) | "Discover Aman in…" | none | 3 | y: 3 region links |
| 2 | hero (carousel "New & Noteworthy") | "Amanvari, Mexico" | full-bleed photo + video; 3 further cards | 4 slides | y: "Discover more", "Discover all destinations" |
| 3 | menu-or-rooms (experiences) | "Seasonal Experiences" | photo cards | 7 | y: "Discover more" x7 |
| 4 | other (residences) | none | photo cards | 2 | y: "Discover more" |
| 5 | other (shop / gift) | "The World of Aman" | photo cards | 3 | y: "Shop now", "Discover more" |
| 6 | other (newsletter) | "Get inspired" | none | — | y: "Sign Up" |
| 7 | footer (links) | "More information" | none | 16 | y: "Contact Us" |
| 8 | footer (directory) | "Destinations" | none | 50 | n |

Totals: 8 sections; ≈1,200 words; ≈16 photographs (1 per card); reservation action: nav only ("Reserve" button in top bar). No prices, no figures block (the "36 hotels in 21 countries" figure is a card caption), no reviews, no FAQ, no hours (group site).

## E. Six Senses (sixsenses.com)

| # | role | headline | visual | items | CTA |
|---|------|----------|--------|-------|-----|
| 1 | reservation-form (booking bar) | none | none | destination/hotel/dates/guests/promo | y: "Check availability", "Book now" |
| 2 | hero | "Some places you visit. Others, you feel…" | full-bleed video | — | y: "View properties on map", "Play full video" |
| 3 | menu-or-rooms (properties) | "In the spotlight: featured properties" | photo cards | 6 | y: "Where next: view all hotels and resorts" |
| 4 | story-about (wellness) | "Wellness & Spa" | photo (presumed) | — | y: "View all", "Come on in" |
| 5 | story-about (values) | "Personalized Wellness Retreats" | none | 3 (values / pioneering wellness / sustainability) | n |
| 6 | other (new openings) | "On the horizon: featured new openings" | photo cards | 7 | y: "Discover more" x7 |
| 7 | events / other | "What's on at Six Senses?" | tiles | 6 (offers, gift cards, experiences, news, meetings, journeys) | y: 3 labels |
| 8 | other (newsletter) | "Journey through Six Senses offers and updates" | none | — | y: "Subscribe now" |
| 9 | footer | none | none | 9 links, 4 social, address | y: email |

Totals: 9 sections; ≈1,000 unique words (≈3,000 with repeated dropdowns); ≈19 photographs (cards); reservation action: real booking form at very top (sticky bar) + nav "Book now". No prices, no reviews, no FAQ.

## F. Geranium (geranium.dk) — 3 Michelin stars

| # | role | headline | visual | items | CTA |
|---|------|----------|--------|-------|-----|
| 1 | hero / story-about | "Welcome to Geranium" (sub "Thoughtfulness can be tasted") | 1 photo (team) | — | y: "Visit Geranium on Facebook" |
| 2 | story-about (place) | "Dinner in the canopy" | 1 photo | 2 chef links | y: Instagram |
| 3 | other (notice) | "Dear Guests." | none | — | n |
| 4 | menu-or-rooms + prices | "Menu" | 1 photo | 6 (menu 4,500 DKK + 5 pairings) | y: "Download the wine list as PDF", Michelin link |
| 5 | reservation-form (link) | "Reservations for 2-6 guests in the restaurant" | 1 photo | prose terms: deposit, 3-month window, waitlist, phone hours | y: "Click here to book a table via SevenRooms." |
| 6 | reservation (groups) | "Reservations for 7+ guests" | none | — | y: "Book a table" |
| 7 | other (special table) | "Fireplace Table" | none | seats 4 | y: "contact our Booking Team" |
| 8 | events (private dining) | "Inspiration Kitchen" | photo pair | seats 16 | y: "Visit our photo and & video gallery", map link |
| 9 | other (press/careers) | "Press Inquiries & Careers" | none | 3 | y: 3 email links |
| 10 | other (hygiene) | "Smiley" | none | — | y: findsmiley.dk |
| 11 | location-hours | "Geranium" (address) | none | address, phone | n |
| 12 | location-hours | "Opening hours" | none | 2-row table | n |
| 13 | location-hours | "Parking" | none | — | n |
| 14 | footer | none | none | photo credit | y: "Gift card", "Book a table" |

Totals: 14 sections; ≈900 words; 6 photographs (1 per section, no captions); reservation action: dedicated section (link to SevenRooms) + footer button + nav. Only site in the corpus that prints prices on the homepage. Figures appear in prose (seats 4 / 16, 8th floor, 3 hours, 1,500 DKK deposit), never as cells. No reviews, no FAQ as such (but the reservation section is FAQ-shaped prose: deposit, groups, gift certificates, waitlist).

## G. Lilia (lilianewyork.com) — neighbourhood restaurant, Resy

| # | role | headline | visual | items | CTA |
|---|------|----------|--------|-------|-----|
| 1 | other (header address) | none (address line) | logo | — | y: map link |
| 2 | hero | "Home" (carousel) | 3 full-bleed food photos | 3 slides | n |
| 3 | story-about | "About" | none | — | y: "About Us" |
| 4 | menu-or-rooms | "Menu" | none | — | y: "View Menu" |
| 5 | reservation (link) | "Reservations" | none | — | y: Resy + mailto |
| 6 | location-hours | "Lilia Restaurant" | none | 2 hours lines | n |
| 7 | other (partner) | none | 1 photo (sign) | 1 | y: link |
| 8 | other (social) | none | none | 2 | y: Instagram, Email |
| 9 | other (newsletter) | "Email Signup" | none | 3 fields | y: "Submit" |
| 10 | reservation-form (popup) | "Reservations" | none | party size (8), date, time (33) | y: "Find A Table" |
| 11 | footer | none | logo | 5 links | n |

Totals: 11 sections; ≈500 words; 4 photographs (3 hero + 1); reservation action: nav + dedicated section (link) + popup form (BentoBox -> Resy). No prices, no gallery, no reviews, no FAQ.

## H/I. Supplementary (not in the ≥50 % count)

Hotel Il Pellicano: opening-dates banner with "Book" -> one-sentence intro statement -> 4 feature cards (Location, Rooms & Suites, Story, Dining) -> "Il Pellicano Experiences" (3) -> Instagram follow -> footer with newsletter and partner logos. ≈600 words, ≈12 images; booking in banner + nav.
Earls (chain): sticky location bar with "Book a table" -> hero "Globally Inspired. Locally Adored. Made For Every Moment." -> "New + Notable" (3 dishes) -> events -> gift cards -> blog (2) -> footer newsletter; reservation panel is a real popup form.

---

## Synthesis

### 1. Modal order of roles (present in ≥ 50 % of the 7 main sites)

| role | present | typical position |
|------|---------|------------------|
| hero (full-bleed photo/video, one line, often a booking button) | 7/7 | 1 |
| story-about (one short paragraph: place, concept or chef) | 6/7 (all but Aman) | 2 |
| menu-or-rooms as cards/links (menu, rooms, properties, experiences) | 6/7 (all but Noma) | 3 |
| events / news / private dining / "what's on" | 4/7 (Noma, Six Senses, Geranium, + Earls, Aman festive) | 4–5 |
| commerce (gift card, shop, voucher) | 5/7 (Noma, Aman, Six Senses, Tastavents, Geranium) | 4–6 or footer |
| reservation action (form or provider link) | 7/7 | nav + a late dedicated block |
| location-hours (address, hours, phone, map) | 5/7 (Tastavents, Noma, Geranium, Lilia, Six Senses footer) | penultimate |
| newsletter | 4/7 (Noma, Aman, Six Senses, Lilia) | just before footer |
| footer | 7/7 | last |

Modal order: hero -> story -> offer cards -> secondary offer / events / shop -> reservation + location-hours -> newsletter -> footer.

Below 50 %: prices on page 1/7 (Geranium), dedicated gallery 1/7 (Tastavents; Noma and Lilia put the gallery in the hero), reviews/testimonials 0/7, figure cells 0/7, FAQ 0/7.

### 2. Optional roles and what sites do without content

- Prices: skipped, substituted by a PDF/external menu link (Tastavents, Lilia "View Menu") or by "Discover more" cards (hotels). Only Geranium prints a price list, and it is 6 lines.
- Reviews: never a quote. Substituted by credential badges and links: Michelin badge in footer (Tastavents), Michelin / 50 Best / Bocuse d'Or links in nav (Geranium), Google "Reseñas" link in header (Tastavents), partner logos in footer (Il Pellicano). Lilia and Wittmore simply skip.
- Figures: never cells. Capacities and durations live inside prose (Geranium: seats 4 / 16, 3 hours; Noma: phone hours; Wittmore: 3 house rules as a mini-list). Hours and address are the one quantitative block that reliably appears, always near the booking action.
- FAQ: skipped everywhere. Geranium folds FAQ content (deposit, groups, gift certificates, waitlist, parking) into the reservation block as short paragraphs.
- Gallery: hotels fold photography into offer cards (1 photo per card, 3–7 cards); restaurants use a hero carousel/strip (Noma 10, Lilia 3, Tastavents 6-tile strip) and only Tastavents adds a thumbnail gallery with lightbox.
- Events: substituted by "news" or "what's on" tiles when there is no event calendar; skipped by small restaurants.

### 3. Photography after the hero

- Rhythm is one photo per section, not pairs or grids: Geranium 5 photos after hero (1 each), Noma 1 per card (≈9), Aman/Six Senses 1 per card in rows of 3–7.
- Size: card-width (1/3 to 1/2 viewport) in the hotel groups; full-width single image per screen in the boutique sites (Wittmore, Tastavents sections 3–5).
- Captions: none. Images carry a card title ("Seasonal Experiences" card names) or nothing; Geranium has a single photo credit in the footer.
- Volume: 4–6 photographs for independents (Lilia 4, Geranium 6), ≈16–20 for groups (Aman, Six Senses, Noma), 60+ only in the Awwwards restaurant site that leans on galleries (Tastavents).
- Photo pairs appear twice in the whole corpus (Noma letter, Geranium Inspiration Kitchen, Tastavents space/chef) and always attached to a story beat, not to a gallery.

### 4. Reservation / contact action

- Present in the navigation on every site that exposed a nav (Noma "Reservations", Aman "Reserve", Six Senses "Book now", Tastavents "Reservas", Lilia "Reservations", Geranium "Reservations", Earls "Book a Table").
- In the hero: Noma ("Book a table"), Earls, Il Pellicano banner; Six Senses places a full booking bar above the hero.
- Dedicated late section: Tastavents (embedded TheFork widget + tel/mail + hours), Geranium (prose + SevenRooms link + group email), Lilia (Resy link + mailto, plus popup form), Noma ("Booking + Hours").
- Real form vs link: real embedded form 3/7 (Six Senses booking bar, Tastavents TheFork widget, Lilia BentoBox popup); link to provider 4/7 (Noma, Geranium SevenRooms, Wittmore "Book a Room", Aman "Reserve"). No site uses a custom-built reservation form; all forms are provider widgets. Phone and email are listed alongside in every restaurant.
- Hours and address sit directly beside the booking action in 4/5 cases where they exist.

### 5. Recommended house structure for place landings

| slot | name | beat | visual | rule |
|------|------|------|--------|------|
| 1 | Hero | photo | full-bleed photo or looping video, one line ≤ 8 words, booking button | Booking CTA appears here and in the sticky nav; no body copy (7/7). |
| 2 | Story | photo | one photo (team, room or plate) + one sentence/paragraph ≤ 60 words | Place, concept or chef; never more than one paragraph (6/7). |
| 3 | Offer | ledger as cards | 3–6 cards, 1 photo each, title + one line, link or PDF | Menu / rooms / experiences; prices only when ≤ 6 lines (Geranium); otherwise link to PDF/menu page. |
| 4 | Proof | quote -> badge row | credential badges and links (Michelin, guide, Google reviews link), no portrait | Substitute for testimonials: 0/7 sites quote a guest; 3/7 show badges. Skip if no credential. |
| 5 | Gallery | gallery | 3–6 photos, uniform strip or 2-up, no captions | Optional; skip when fewer than 3 good photos (Lilia, Geranium skip). |
| 6 | What's on | ledger | 2–4 tiles: events, private dining, gift card, news | Optional; gift card / voucher is the most common commerce item (5/7). |
| 7 | Book | form + cells | provider widget embedded (TheFork/Resy/SevenRooms/booking engine) or deep link; beside it hours, address/map, phone, email as cells; 2–4 FAQ-style lines (deposit, groups, dress, parking) | Hours/address live here, not in a separate figures block (4/5). Form = provider embed, never custom. |
| 8 | Footer | cells | newsletter field, social, legal, credits | Newsletter sits just above or inside footer (4/7). |

Comparison with the draft (hero -> story -> offer ledger with prices -> figures cells -> gallery 2–3 -> voice -> faq -> book form):

- KEEP hero (full photo): 7/7. Add the booking button to the hero itself (Noma, Earls, Pellicano) and to the nav (every site with a nav).
- KEEP story (photo + one sentence): 6/7, and the sites that score on Awwwards (Wittmore, Tastavents) run exactly this cadence of one photo + one sentence per screen.
- CHANGE offer: keep as the third slot, but make it cards with photos and links, with prices optional. Only 1/7 sites prints prices; 3/7 link to a PDF or external menu. A priced ledger should be allowed only when the list is ≤ 6 lines.
- CHANGE figures: drop the stand-alone cells slot. 0/7 sites show stat cells; the only recurring figures are hours/address/phone, and they sit beside the booking action (Tastavents, Noma, Geranium, Lilia). Move them into the Book slot as cells.
- KEEP gallery but make it optional and later: dedicated gallery 1/7; hotels fold photos into the offer cards. When present, 3–6 photos, no captions.
- CHANGE voice: replace the single review quote with a badge/credential row (Michelin, guide listings, Google reviews link, partner logos). 0/7 quote a guest; 3/7 display badges. Keep the "quote" beat type available but default to badges.
- CHANGE faq: no site has a FAQ block. Fold 2–4 booking-terms lines (deposit, group size, parking, adults-only) into the Book slot as Geranium and Wittmore do.
- KEEP book as the closing action, but specify provider embed or link rather than a bespoke form (3/7 embed, 4/7 link, 0/7 custom), and add phone/email alongside (all restaurants).
- ADD a "What's on" / commerce slot (events, private dining, gift card): events/news 4/7, gift card or shop 5/7; this is where the draft under-counts what real place pages carry.
- ADD a newsletter field at the foot: 4/7.

Word budget: 200 (Wittmore) to 1,200 (Aman) words; the Awwwards boutique pattern is ≈200–1,000 words with 1 sentence per section. Photograph budget: 4–6 for an independent, 15–20 for a brand; one photo per section after the hero.

---

## Sources

- https://www.tastavents.com/
- https://www.awwwards.com/sites/tastavents-restaurant
- https://www.thewittmore.com/
- https://www.awwwards.com/sites/wittmore-hotel
- https://noma.dk/
- https://www.aman.com/
- https://www.sixsenses.com/
- https://www.geranium.dk/
- https://www.lilianewyork.com/
- https://www.pellicanohotels.com/en/hotels/hotel-il-pellicano
- https://earls.ca/
- https://www.awwwards.com/sites/pulso-hotel (HM, 7 Nov 2025; live site robots-disallowed)
- https://www.awwwards.com/sites/hotel-jagerhof (HM, 26 Dec 2025; live site robots-disallowed)
- https://www.awwwards.com/sites/flavori-restaurant (HM, 4 Jul 2024; live URL not exposed)
- Failed fetches: https://www.frantzen.com/, https://pulsohotel.com.br/, https://www.jaegerhof.it/, https://alchemist.dk/ (JS shell only)
