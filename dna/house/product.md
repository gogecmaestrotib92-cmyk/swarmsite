# House structure research: product / D2C landing pages

Date: 2026-11-09. Method: WebSearch + WebFetch text extraction only (no browser). Visual types are inferred from alt text, file names, video embeds and section copy, so "product photo vs lifestyle photo" is a best reading of the markup, not a visual check. Headlines are quoted verbatim as served; capitalisation preserved.

## Site selection and substitutions

Candidates came from the Awwwards "E-commerce Honors" / SOTD list (2024–2025) plus the reference brands in the brief.

| Requested / candidate | Status | Used? |
|---|---|---|
| Halfdays (halfdays.com) | fetched OK | yes — multi-product apparel D2C |
| Nothing (nothing.tech) homepage | fetched OK | yes — small range |
| Nothing Headphone (1) Pro product landing | fetched OK | yes — single hero product landing |
| Teenage Engineering homepage | JS-rendered, body text empty; `/products/op-1-field` client error | replaced by `teenage.engineering/store/tp-7` product page (fetched OK) |
| Aesop (aesop.com) | homepage text fetched but no CTAs/visuals/footer captured; product page client error | partial — used as supporting evidence only |
| Crav (crav.com) | domain parked (302 to GoDaddy for-sale page) | replaced |
| Telepathic Instruments (Awwwards SOTD Mar 2025) | site in "Something is coming" teaser mode | replaced |
| SPYLT (Awwwards SOTD Mar 2025) | site in countdown/teaser mode (~75 words) | replaced |
| Bored Cow (Awwwards SOTD Apr 2024) | robots disallowed | replaced |
| Daylight Computer (Awwwards SOTD Jun 2024) | fetched OK | yes — single-product D2C (DC-1) |
| Oura Ring (Awwwards E-commerce Honors Apr 2025) | fetched OK | yes — one hero product |
| Polène (Awwwards E-commerce Honors Nov 2024) | fetched OK | yes — supplementary, small range |
| Onyx Coffee Lab | fetched OK | yes — specialty roaster |

Primary set (6): Halfdays, Nothing Headphone (1) Pro, Daylight, Oura, Onyx Coffee Lab, Teenage Engineering TP-7. Supplementary (2): Nothing homepage, Polène. Aesop homepage used only for the price/certification observations.

---

## 1. Halfdays — halfdays.com (homepage)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 0 | other (announcement bar) | "FREE SHIPPING ON US ORDERS $95+." | none | — | n |
| 1 | hero | "Ski season starts here." | lifestyle photo (background) | — | y "SHOP WINTER 2026" |
| 2 | range-or-variants (promo tiles) | "SKI SEASON STARTS HERE" / "POWERED BY GORE-TEX®" | 2 photo tiles | 2 | y "Shop Winter 2026", "Shop now" |
| 3 | product-story (hero product) | "Penny" (eyebrow "MEET", sub "Your one-piece wonder.") | lifestyle photo | 1 | y "SHOP NOW" |
| 4 | range-or-variants | "SHOP BY COLOR" | product/lifestyle tiles | 7 colours | n (tiles link) |
| 5 | range-or-variants (categories) | "BESTSELLING LAYERS" / "Accessories" / "Outerwear" | photo tiles | 3 | y "SHOP NOW" x3 |
| 6 | product-story (brand) | "bye-bye, boys club." | 2 lifestyle photos (skiers on mountain) | 2 badges ("Olympian-founded.", "Designed in Colorado.") | y "Learn more" |
| 7 | prices + range (product carousel) | "FOUNDER FAVES" | studio product photos on white | 10 cards with price ($145–$695) | n (cards link) |
| 8 | other (newsletter) | "LET'S MAKE IT OFFICIAL." | none | — | y "SIGN ME UP" |
| 9 | footer | none | none | 3 link columns + region + legal | n |

Totals: 10 sections (incl. bar and footer); ~600–700 words of unique copy (~2,400 incl. nav/country list); ~22 product photographs (7 colour tiles + 10 studio cards + 3 category tiles + 2 hero/Penny); buy action: hero CTA "SHOP WINTER 2026" first; prices only in the product carousel (section 7), none in hero.

## 2. Nothing — Headphone (1) Pro product landing (nothing.tech/products/headphone-1-pro)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 1 | hero | "Hear more details with three drivers" | video carousel + 7 thumbnails | 7 | y "Go to sound" (anchor) |
| 2 | product-story | "Studio-level precision for our most advanced headphone ever" | product photo | — | n |
| 3 | features-materials | "Active Noise Cancellation with 10 mics" | product photo | — | y "Go to noise control" |
| 4 | product-story | "Tuning with Metropolis Studios" | video | — | y "Go to tuning" |
| 5 | features-materials | "Machined metal and adaptive fit" | none | — | y "Go to design" |
| 6 | features-materials | "iOS + Android compatible" | none | — | y "Go to performance" |
| 7 | features-materials (tabs) | "Triple driver architecture" | image + 4 tabs | 4 tabs, 4 sub-blocks, 5 driver videos | n |
| 8 | features-materials | "All the details" | cert logo + video | — | n |
| 9 | figures | "Our best Active Noise Cancellation" (46 dB, 10 mics) | video | 3 sub-features | n |
| 10 | features-materials | "Like it's live" | video | 4 environments | n |
| 11 | product-story | "Tuning with Metropolis Studios" (2nd) | video | 5 sub-sections | y "Watch" |
| 12 | features-materials | "Ludicrously over-engineered" | video + image | 2 | n |
| 13 | features-materials | "Designed for comfort" | video | — | n |
| 14 | how-to-use | "Control everything" | 4 product photos | 4 (Roller, Paddle, Button, Switch) | n |
| 15 | figures | "50,000+ rounds of testing" | video | — | y "Watch" |
| 16 | features-materials | "Ready for anywhere" | product photo (case) | — | n |
| 17 | features-materials | "Performance" | 2 images | 5 | n |
| 18 | features-materials (specs) | "Technical specs" | in-the-box image + tables | 9 tables | n |
| 19 | other (disclaimers) | none | none | 17 notes | n |
| 20 | other (trust strip) | "Why buy on nothing.tech" | none | 5 | n |
| 21 | range-or-variants (cross-sell) | "You may also like" | 3 product thumbnails | 3 | y "Explore" x3 |
| 22 | prices + shop-cta (purchase block) | "Headphone (1) Pro" | none | 2 colours; price £349 | y "Add to bag" / "Sold Out" |
| 23 | footer | none | none | 4 link groups + social | n |

Totals: 23 sections; ~4,000–5,000 words (specs + disclaimers heavy); ~20+ product photographs/videos, all studio; buy action: price (£349), colour picker and "Add to bag" live in one purchase block that sits last in DOM order (rendered as a sticky bar in the live UI); hero carries only an anchor link.

## 3. Daylight Computer — daylightcomputer.com (single-product D2C, Awwwards SOTD Jun 2024)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 0 | other (header + stock notice) | "In stock · Ships in 3-5 business days" | none | — | y "Order now" (x2) |
| 1 | hero | "The computer, de-invented" | 3 lifestyle photos (tablet on grass, park bench) + animated video | 4 media | y "Order now" |
| 2 | product-story (mission) | "We refuse to accept a future where our devices are exhausting…" | none | — | n |
| 3 | features-materials | "The world's first full-speed paper-like display" | icons | 3 | n |
| 4 | how-to-use (use cases) | "A distraction-free space for learning & creativity" | UI screenshots | 3 cards | n |
| 5 | features-materials (compat) | "With all the apps you need" | 9 app icons + illustration | 9 | n |
| 6 | features-materials | "it's a computer you can use outside" | lifestyle photo + icons | 7 | n |
| 7 | other (deep links) | "Dive deeper into Daylight" | 4 thumbnails | 4 | y (links: Product, Specs, FAQ, Support) |
| 8 | reviews | "What people are saying" | 4 profile photos | 4 social quotes | n |
| 9 | reviews (press) | "know more about daylight on:" | 4 logos | 4 | n |
| 10 | sustainability-story (PBC letter) | "Daylight is a Public Benefit Co." | sun illustration | — | n |
| 11 | features-materials (recap) | "DC-1 at a glance" | icons | 5 | n |
| 12 | shop-cta | none | lifestyle photo (person holding device) | — | y "Order now" + "Ships within 3-5 business days" |
| 13 | footer | none | none | legal + nav + social + "Get updates" | n |

Totals: 14 sections; ~800–900 words; ~6 product photographs, all lifestyle (no studio packshot); buy action: "Order now" in header, stock bar, hero and pre-footer; no price shown on the page (price lives in cart).

## 4. Oura Ring — ouraring.com (Awwwards E-commerce Honors Apr 2025)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 0 | other (announcement) | "Use your FSA or HSA HSA/FSA funds on Oura" | image | — | n |
| 1 | hero | "Wear your best life" | campaign lifestyle photo | — | y "Shop Now" |
| 2 | product-story + features | "Understand your body. Own your health." | carousel of 6 lifestyle photos, each captioned | 6 | y "Why Oura", "How It Works" |
| 3 | figures | "86% of Oura Members see their health improve" | app UI collage | 5 screens | y "Explore Membership" |
| 4 | reviews | "Real members, real stories of impact" | 3 profile photos | 3 | n |
| 5 | features-materials (new feature) | "Meet Health Radar" | app UI on phone | — | y "Explore" |
| 6 | reviews (press) | "IN THE NEWS" / "FEATURED ARTICLE" | product photo (two hands wearing rings) | 1 article + 3 press quotes | y "Read More" |
| 7 | other (footnotes) | none | none | 2 | n |
| 8 | other (trust: payment) | "FSA or HSA" | 6 payment logos | 6 | n |
| 9 | other (newsletter) | "Receive articles, tips, and offers from Oura" | none | — | y (email field) |
| 10 | footer | none | none | legal links | n |

Totals: 11 sections; ~550–650 words; ~8 product photographs (6 captioned lifestyle carousel + hero + hands), plus app screenshots; buy action: "Shop Now" in hero; no price on the homepage; no variants/colour selector, no FAQ, no specs.

## 5. Onyx Coffee Lab — onyxcoffeelab.com (specialty roaster)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 0 | other (announcement + sign-up + promo strip) | "Join Our Pilgrimage" | 4 brand logos | 3 promo links | y "Pre-Order Now", "Shop Now", "Discover" |
| 1 | hero | none (mission paragraph) | looping video | — | y "Explore Advent 2026 →" |
| 2 | product-story (single coffee) | "Guatemala El Injerto Gesha" | product photo | 1 | y "Explore This Offering" |
| 3–8 | range-or-variants (6 collection panels) | "Barista Provisions", "BOX SETS", "TERROIR", "ONYX AT THE PRESERVE", "Classes", "Fall Menu" | video / GIF / lifestyle photo per panel | 6 | y one CTA each |
| 9 | product-story (brand) | "D o y e n n e" | background image | — | y "Order Now" |
| 10 | product-story (origin) | "Producer Spotlight" | image | 1 | y "Explore The Offering" |
| 11 | shop-cta | "Explore Our Coffee" | video | — | y "Shop Coffee" |
| 12 | other (B2B) | "Wholesale" | video | — | y "Learn More" |
| 13 | sustainability-story | "We Are A Certified B-Corp" | background image | — | y "See Our Certification" |
| 14 | range-or-variants | "Fall Offerings" | text cards | 3 | y "View Coffees →" x3 |
| 15–18 | product-story / collabs | "CIRCADIAN", James Beard, "(ONYX)RED", "USA CYCLING" | video / image | 4 | y one each |
| 19 | figures (awards) | "The most awarded coffee roaster" | none | 46 awards 2014–2026 | n |
| 20–23 | range (merch, matcha, subscription, cafés) | "CHECK OUT OUR MERCH", "SPECIALTY MATCHA", "SUBSCRIBE & SAVE", "Come Visit Us" | image / video | 4 | y one each |
| 24 | reviews (press) | none | 11 publication logos + excerpts | 11 | n |
| 25 | shop-cta (categories) | "Coffee" / "Tea" / "Chocolate" / "Merch" | 4 image tiles | 4 | y "Shop" x4 |
| 26 | footer | "Join Our Pilgrimage" (repeat) | none | 8 link columns, 8 locations | n |

Totals: ~30 sections; ~2,000–2,500 words; ~4 product photographs, ~15 video/lifestyle backgrounds; buy action: "Pre-Order Now" in the promo strip above the hero, then one "Explore/Shop" per panel; no product prices on the homepage (only "$40+" free-shipping threshold).

## 6. Teenage Engineering — TP-7 product page (teenage.engineering/store/tp-7)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 0 | other (nav) | none | none | 12 links | n |
| 1 | hero (gallery) | none | 9 studio product photos ("TP–7 aluminum, 1 of 9") | 9 | n |
| 2 | range-or-variants + shop-cta | "TP–7 aluminum" | none | 2 variants (aluminum, black) | y "buy", "add to cart" |
| 3 | product-story | none (one paragraph + in-the-box) | none | 1 paragraph | n |
| 4 | features-materials (specs) | "details" | none | 9 bullets | y "explore", "read the user guide" |
| 5 | range-or-variants (accessories) | "accessories" | product thumbnails | 8 | y "add to cart" x8 |
| 6 | range-or-variants (related) | "related" | product thumbnails | 8 | y "add to cart" x8 |
| 7 | footer | none | none | 2 link groups, shipping/returns note, address | y "join our newsletter" |

Totals: 8 sections; ~400 words; 9 studio product photographs + 16 thumbnails; buy action: "buy" / "add to cart" directly under the gallery; price not in extracted text (rendered client-side by region).

## Supplementary A. Nothing — homepage (nothing.tech)

Order: hero (video, "Studio-level precision for our most advanced headphone ever.", CTA "Discover") → "Shop by category" (4 text links) → campaign video ("On set with V…", CTA "Discover the campaign") → "Going pink?" (3 product links) → "Pack your sound" (2 product cards with photos, "Discover") → Charli xcx campaign video (CTA "Discover Headphone (a)") → "Why buy on nothing.tech" (5 trust items) → "Join the community" newsletter → footer. 10 sections; ~300–350 words; 3 videos + 2 product photos; no prices; first CTA in hero ("Discover", not "Buy").

## Supplementary B. Polène — polene-paris.com (Awwwards E-commerce Honors Nov 2024)

Order: header/mega-menu → hero = shoppable video + 4 product cards with prices ("Mokki 540 €", "Cyme Mini 390 €"…), CTA "Découvrir la sélection" → "Ormé" jewellery feature (banner + 14 priced products 140–250 €, CTA "Découvrir les nouveautés") → "Suivez-nous sur Instagram" → model search → newsletter → footer with 4 payment logos. 7 sections; ~300–400 words unique; prices on every product card from the hero down; the hero itself is a priced product grid.

## Supplementary C. Aesop — homepage (partial text)

Order observed: hero ("A striking show of hands", one new product) → "New and notable" → editorial repeat → "Potency in precision" (how-to-use: after cleansing, before hydration) → product card "New addition … $49.00" → "Certified B Corp" → "Leaping Bunny approved" → store feature "Aesop Upper West Side" → "The Hand & Body Care Finder" → Ada Lovelace quote. ~300–340 words; a single price appears, in the one product card; CTAs/footer not captured.

---

## Synthesis

### 1. Modal order of roles (present in ≥ 50 % of the 8 pages)

| Role | Present | Typical position |
|---|---|---|
| hero (one headline, one visual, one CTA) | 8/8 | 1 |
| product-story (brand/mission or hero-product beat; photo + 1–2 sentences) | 8/8 | 2–3, directly after hero |
| features-materials | 7/8 (Polène lacks) | 3–5 |
| range-or-variants (colours, categories, related/accessory grid) | 7/8 (Oura lacks) | 4–6, and again before footer as cross-sell |
| other: trust/service strip (shipping, returns, warranty, payment logos) | 6/8 | near the end, before newsletter |
| other: newsletter sign-up | 7/8 | penultimate |
| footer | 8/8 | last |
| reviews / press (social proof, any form) | 4/8 (Daylight, Oura, Onyx, Halfdays cart quote) | after features, before mission/sustainability |
| figures | 4/8 (Oura, Nothing, Onyx, Daylight "60fps") | folded into feature copy; only Oura uses a number as a section headline |
| prices on the landing | 4/9 incl. Aesop (Halfdays, Nothing product, Polène, Aesop) | always attached to a product card or purchase block, never in a standalone "price" section |

Modal order: **hero → product-story → features → range/variants (+ prices on cards) → social proof → trust strip → newsletter/CTA → footer**.

### 2. Optional roles and what sites do without them

- **reviews**: 4/8 skip entirely (Nothing x2, TE, Polène). Substitutes: press logos (Daylight, Onyx), a membership statistic (Oura), or nothing — hardware/luxury brands let specs and photography carry proof.
- **figures**: Skipped as a section by most. Substituted by numbers embedded in feature headlines ("Active Noise Cancellation with 10 mics", "50,000+ rounds of testing", "86% of Oura Members…"). Onyx substitutes an awards list (46 items).
- **how-to-use**: 3/9 (Daylight use cases, Nothing "Control everything", Aesop ritual sentence). Others skip.
- **sustainability-story**: 4/9 (Onyx B-Corp, Daylight PBC letter, Aesop B Corp + Leaping Bunny, Nothing sustainability spec row). Always placed late, after proof and before the final CTA; skipped silently when absent.
- **faq**: 0/8 inline. Daylight and Halfdays link to an FAQ page from a "dive deeper" tile or the footer; none renders Q&A on the landing.
- **prices**: 5/9 omit prices on the landing (Daylight, Oura, Onyx, Nothing home, TE in extracted text). They substitute an "Order now / Shop now" CTA and a shipping/stock micro-line ("In stock · Ships in 3-5 business days", "free shipping over $120").
- **variants**: Oura and Daylight (single-SKU) skip; Daylight substitutes a "Dive deeper" link tile row where a range grid would sit.

### 3. How the product is shown after the hero

- **Count**: single-product landings re-show the product 4–6 times (Daylight 5 lifestyle shots + screenshots; Oura 6-image captioned carousel + hands shot; Nothing product 20+ studio shots/videos, one per feature). Range sites re-show via grids: Halfdays 7 colour tiles + 10 studio cards; TE 9-shot gallery + 16 thumbnails; Polène 4 + 14 cards.
- **Lifestyle vs studio**: wellness/lifestyle positioning (Daylight, Oura, Halfdays hero, Onyx) leads with lifestyle photos and keeps studio shots for the price grid. Engineering/design positioning (Nothing, TE) is almost entirely studio product photography and video with no people.
- **Captions**: yes, nearly always. Oura's carousel pairs each photo with a benefit line ("Get the best sleep of your life"); Nothing gives each image a feature headline; Halfdays colour tiles are captioned with colour names; TE's gallery is uncaptioned (only "1 of 9").
- **Video**: 5/8 use video in or directly after the hero (Nothing x2, Onyx, Daylight, Polène).

### 4. Where price and buy action sit

- **Buy action first appears in the hero** on 6/8 pages (Halfdays "SHOP WINTER 2026", Nothing "Discover", Daylight "Order now" also in header and stock bar, Oura "Shop Now", Onyx "Pre-Order Now" strip above hero, Polène "Découvrir la sélection"). TE puts "buy / add to cart" immediately under the hero gallery. Nothing's product page places price + colours + "Add to bag" in a purchase block that is last in DOM but rendered as a sticky bar.
- **Price** is never a section of its own. It appears (a) on product cards inside a range grid (Halfdays, Polène, Aesop), or (b) in a compact purchase block next to the variant picker (Nothing, TE). Single-SKU D2C pages (Daylight, Oura) defer price to the cart and replace it with stock/shipping reassurance.
- **Repeat CTA**: 4/8 close with a dedicated pre-footer CTA block (Daylight lifestyle photo + "Order now" + ship time; Onyx 4 shop tiles; Nothing purchase block; Halfdays newsletter instead).

### 5. Recommended house structure (8 slots)

| # | Slot | Beat | Recommended visual | Rule |
|---|---|---|---|---|
| 1 | Hero | photo | one poster photo or looping video of the product in context; CTA + stock/shipping micro-line | ≤ 8-word headline, one CTA ("Shop now" / "Order now"), a one-line reassurance under it (Daylight, Halfdays bar). |
| 2 | Story | photo | one lifestyle photo + one sentence | The "why" in one line ("bye-bye, boys club.", "We refuse to accept a future…"); optional "Learn more" link, never a buy button. |
| 3 | Features | features | 3–6 items, each with its own product detail photo or icon, number in the headline where there is one | Fold figures into feature headlines ("…with 10 mics"); 3 for simple goods, up to 6–7 for hardware (Daylight 3/5/7, Nothing 5). |
| 4 | Gallery | gallery | 3–6 captioned product shots (lifestyle for wellness/apparel, studio for hardware/design) | Every image gets a one-line caption (Oura, Nothing); this is where the product is shown "in use". |
| 5 | Offer | ledger | product cards or variant row with price per card + "Add to bag"; single-SKU: variants + price + stock line | Prices live only here, on cards or beside the picker (Halfdays, Polène, Nothing, TE). If price is hidden by region, show "Ships in N days / Free shipping over X". |
| 6 | Voice | quote | 3 short quotes with avatar, or press logos if there are no customers yet | Modal is 3–4 testimonials (Daylight 4, Oura 3), not one. Substitute press logos (Daylight, Onyx) or a single stat (Oura "86%…") when absent. |
| 7 | Trust | cells | 4–5 cells: delivery, returns, warranty, payments, (optional) certification/B-Corp | 6/8 sites have this strip; also where sustainability credentials go (Onyx, Aesop, Daylight). |
| 8 | Close | cta | lifestyle photo + repeat CTA + ship-time line; newsletter field below; footer | Daylight pre-footer is the model; FAQ becomes a link here, not a block. |

### Comparison with the draft

Draft: hero(poster photo) → story (photo + one sentence) → features (3–6) → offer (ledger: variants with prices) → figures (cells) → voice (one review) → faq → cta.

**Keep**
- hero as poster photo with one CTA: 8/8 sites, 6/8 put the buy action here.
- story = photo + one sentence directly after hero: Halfdays, Daylight, Oura, Nothing all do exactly this.
- features 3–6: Daylight 3/5, Nothing 5, Oura 6, TE 9 bullets — 3–6 is the right band.
- offer as a ledger of variants with prices: Halfdays, Polène, TE, Nothing all show price only beside a card or variant picker.
- closing cta: Daylight, Onyx, Nothing end on a buy block.

**Change**
- **Add a gallery slot** between features and offer (or merge into features as one-photo-per-feature). Every site re-shows the product 4–20 times after the hero; the draft has only two photos (hero, story), which is far below the observed norm.
- **Demote figures from a standalone cells slot to numbers inside feature headlines.** Only Oura uses a statistic as a section; Nothing, Daylight and Onyx embed numbers in features or awards. Re-use the cells beat for a **trust strip** (delivery / returns / warranty / payments), which appears on 6/8 sites and is absent from the draft.
- **Voice: 3 quotes, not one.** Daylight 4, Oura 3, Onyx 11 press excerpts. One isolated review was not observed anywhere except Halfdays' cart drawer. Allow press logos as the fallback.
- **Drop FAQ as a page block; make it a link in the close/footer.** 0/8 landings render FAQ inline; Daylight and Halfdays link to it.
- **Offer should sit earlier for range brands** (Halfdays shows priced cards at section 7 of 10, Polène in the hero, TE right under the gallery) and **may omit price for single-SKU D2C** (Daylight, Oura show no price at all and substitute stock/shipping reassurance). The ledger therefore needs a "price hidden → show ship-time" fallback rule.
- **Sustainability/certification** is a recurring optional beat (4/9) with no slot in the draft; the trust strip is the natural home (B-Corp cell alongside shipping/returns).
- **Newsletter capture** (7/8) is missing from the draft; add it to the close slot above the footer.

---

## Sources

- Awwwards e-commerce winners list: https://www.awwwards.com/websites/winner_category_ecommerce/
- Halfdays homepage: https://halfdays.com/
- Nothing homepage: https://nothing.tech/
- Nothing Headphone (1) Pro: https://nothing.tech/products/headphone-1-pro
- Daylight Computer: https://daylightcomputer.com/
- Oura Ring: https://ouraring.com/
- Onyx Coffee Lab: https://onyxcoffeelab.com/
- Teenage Engineering TP-7: https://teenage.engineering/store/tp-7
- Teenage Engineering homepage (text empty, JS-rendered): https://teenage.engineering/
- Polène: https://www.polene-paris.com/
- Aesop homepage (partial): https://www.aesop.com/
- Failed/replaced: https://crav.com/ (parked), https://telepathicinstruments.com/ (teaser), https://spylt.com/ (teaser), https://boredcowmilk.com/ (robots disallowed), https://www.aesop.com/us/p/hand/hand-wash/resurrection-aromatique-hand-wash/ (client error), https://teenage.engineering/products/op-1-field (client error)
