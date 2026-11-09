# Swarmsite — product strategy and 30-day validation

Written 2026-11-09 against commit `9200ead`. Companion to [SWARMSITE_CREATIVE_ENGINE_V2_PLAN.md](SWARMSITE_CREATIVE_ENGINE_V2_PLAN.md), which holds the code audit and the engineering plan. Nothing here is implemented; pricing, hosting and unrelated features are deliberately not built.

How to read the claims:

| Tag | Meaning |
|---|---|
| **[V]** | Verified fact from the repository (`file:line` in the engine plan where not given here) |
| **[P]** | Measured on production: the 20 most recent finished jobs, read 2026-11-09 |
| **[M]** | External market evidence, researched 2026-11-09. *(primary)* = the vendor's own page was read; *(third-party)* = another site's page was read; *(search)* = seen only in a search summary — low confidence. Sources are numbered at the end. |
| **[H]** | Architectural or product hypothesis — to be tested |
| **[A]** | Business assumption — no evidence yet |
| **[R]** | Recommendation |

---

## 0. Summary

| Question | Answer |
|---|---|
| What are we proving first? | That people prefer Swarmsite's redesign to the output of other URL-to-site tools, on the same site, blind. Nothing else is worth building until that is shown. **[R]** |
| Is URL → redesign a differentiator? | No. At least nine products take an existing URL today. **[M]** |
| Where do we stand on quality today? | Technically sound, creatively generic: contract median 97, taste median 56, originality median 45, and no page of the last 20 reached the engine's own "ship after a day of polish" mark. **[P]** |
| Initial category | Software-product landing pages built by their founders. Moderate confidence; the switch criteria are in §3. **[R]** |
| Hosting or export | Export first. Keep the hosted preview that already exists. Do not build a hosting platform. **[R]** |
| Pricing | One-time, tested between $149 and $299 for a single page. A hypothesis. **[A]** |
| Cost of one generation today | About $0.6 in model fees at list price (range about $0.3–$1.1), about 4 minutes. **[P]** |
| First engineering step | Measurement: a fixed benchmark, separate technical and creative scores, a blind comparison page. Then the cheapest test of the main cause (one day). **[R]** |

---

## 1. Positioning

**What Swarmsite is.** An autonomous design studio: it reads an existing site, understands the business, develops a creative concept, and returns a working page that looks art-directed rather than generated.

**What it is not.** A template marketplace, a general site builder, or the fastest way to get a page.

**Positioning lines to test — not to claim yet [A]:**
- "Your website. Reimagined by an AI creative studio."
- "Agency-level design. Without the agency."
- For the recommended first audience: "It no longer looks AI-generated."

**Why none of these can be claimed today.** On the last 20 production jobs the critic's originality axis ran from 32 to 55, and its own summary of several pages was that they "fall apart into a template" below the hero **[P]**. The engine plan explains why and what would change it. Until the benchmark in §4 shows a preference, these lines are hypotheses for a landing-page test, not statements about the product.

**The promise the engine can already keep [V]:** nothing is invented. FAQ answers and testimonials are taken only from captured source pairs, links go only to captured destinations, and a coverage report says what was not carried over. This is a real difference from tools whose own documentation tells users to check that pages, images and links survived the import [1]. It should be part of the pitch from the start.

**And the user decides how much may change [V]:** "keep my SEO" (default) keeps the words, the headings' keywords, every internal link and the meta, and reports the kept share on the result; "redesign freely" lets headings and copy change while facts stay true. What can be promised is what is measured — words, headings, links, meta carried over. Rankings themselves cannot be promised by anyone.

**Checked 2026-11-09 [P]:** the engine's own contract reported three of the four production jobs made in "keep my SEO" mode as having lost internal links, and one restaurant as keeping 51% of the source's words. On inspection every reported loss was a measurement error: anchors within the source page itself counted as links, one link compared without decoding `&amp;`, and a cookie banner counted as page copy. No real loss was found in the four. The measurement is being corrected. Until the corrected check has run on more sites, the honest wording is "measured and reported", not "guaranteed".

---

## 2. Competitive landscape and differentiation

### 2.1 URL intake is common **[M]**

| Product | What it does with a URL | Output | Price | Confidence |
|---|---|---|---|---|
| Wix Harmony "Create from URL" | Brings over pages, text, images, links, colours | Hosted Wix site | Wix plans | primary [1] |
| Framer agents | Recreates pages, structure and CMS content | Hosted Framer site | Basic $10, Pro $30 per month | primary [4][5] |
| Lovable "import website" | Reads text, images, fonts, colours, layout; up to 10 pages | Editable project | Credit-based | primary [6] |
| Replit Design "Import URL" | Recreates look and feel; its guide suggests generating three directions | Design frame, then app | Core $20, Pro $100 per month | primary [7][36] |
| Hostinger AI Builder | URL, image or PDF → site | Hosted; code export stated | $1.99–7.99 promo, renews $10.99–25.99 | primary [8][9] |
| 10Web | Recreates a page from a URL; migrations | WordPress | $10–22.5 per month, annual | primary [10][11] |
| Repaint | Reads the live site; recreate or fully redo, optionally with a style-reference site | Hosted | $25 / $100 / $200 per month | primary [13][14] |
| Shuffle "Redesign Mode" | URL plus a brief | Export to Next.js, React, Vue, Laravel, HTML | not stated | primary [17] |
| Readdy | URL, screenshot or prompt | Hosted; code export on paid plans | $25 / $40 per month | search + primary [15][16] |

Not found to take a URL: Squarespace Blueprint, Webflow's AI site builder, Durable, B12, Unicorn Platform (search or pricing pages only) [23][24][25][26][27]. No official documentation of URL cloning was found for v0 or Bolt.

Two details matter for us:
- Replit's own guide already suggests three directions [7]. "Three concepts" is not a differentiator in itself; what is in them is.
- Repaint already offers "recreate or fully redo" with a style reference [13]. It is the closest in shape to Swarmsite.

### 2.2 What nobody has published **[M]**

- No independent, hands-on comparison of design quality between URL-redesign tools was found.
- One single-run test of general AI builders called Framer's layout the "most polished" and also the slowest, at over 8 minutes [28] (third-party).
- The "all AI sites look the same" complaint is public and specific: Anthropic's own write-up names "Inter fonts, purple gradients on white backgrounds" [68] (primary, 12 months old); a studio lists twelve tells and calls sameness "the most expensive" one [69] (third-party, commercially interested).

### 2.3 Where Swarmsite can differ

| Dimension | Others, as documented | Swarmsite today | Swarmsite if the engine plan works |
|---|---|---|---|
| Content fidelity | "Check that pages, images and links came over" [1]; "small differences are expected" [6] | Source-grounded, with a coverage report **[V]** | Same, enforced structurally by the composition format **[H]** |
| Originality | Not measured publicly | Originality median 45; 4 distinct section sequences across 12 recipes **[P][V]** | The test of the plan **[H]** |
| Typography | — | 9 display faces across 12 references; 12 of 20 pages shipped in one face **[V][P]** | Font registry, per-concept type decisions **[H]** |
| Evidence of quality | None published | None | A blind benchmark against named tools — itself a marketing asset if we win **[R]** |
| Business model | Monthly subscription, mostly hosted | Free hosted preview, nothing sold **[V]** | One-time purchase with export **[A]** |

**The differentiator must be the result.** The agent count, the six layers and the three concepts are how; a buyer sees one page. Every engineering decision is judged by one question: does this make the page more original, more professional, or more fitting for the brand? If not, it needs a separate justification (measurement, safety and cost control are the legitimate ones).

---

## 3. Target customer and the initial category

### 3.1 What the repository constrains **[V]**

- The engine redesigns **one page**. Site-wide capture exists in code but is never switched on by the server, and sub-pages are "read, not rebuilt".
- The output is **one self-contained HTML file** and a hosted preview. There is no export, account or payment.
- A place (restaurant, hotel) is shown **only in its own photographs**; generated imagery is forbidden there. Sites without photographs do badly (Bálamo's early runs).
- Of the last 20 production jobs, **17 were software sites**, 3 were restaurants, none were service or product sites **[P]**.

So today a complete deliverable exists only where one page is the whole site, and only a technical buyer can use it without us doing something by hand.

### 3.2 The four candidates

Scores are 1 (bad for us) to 5 (good for us). **E** = supported by evidence cited in this document; **J** = judgment.

| Criterion | Restaurants | Boutique hotels | Premium services (architecture, interiors, agencies) | Software-product landing pages |
|---|---|---|---|---|
| Willingness to pay | 3 **E** — they pay $179–$499 per month for site + ordering platforms [45][47], but for ordering and marketing, not design | 4 **E/J** — builds quoted at $4k–$40k [58] (search, aggregator) | 4 **J** — no spend data found | 3 **E** — templates $49–$149, human landing pages $2k–$10k [62][64]; a gap in between |
| Suitable visual assets | 3 **E/J** — own photographs or nothing | 5 **J** | 4 **J** | 2 **E** — screenshots are the weak point throughout REFACTOR.md |
| Site complexity (5 = simple) | 4 **J** — usually one page | 2 **E** — rooms, booking engine; OTAs take 63% of independent-hotel bookings [54] | 2 **J** — the work lives in sub-pages; one page is a partial redesign | 5 **V** — one page is the site |
| Technical difficulty (5 = easy) | 3 **E** — menus, hours, reservation embeds are pasted widget code [50] | 2 **E** — booking-engine widgets [55][57] | 3 **J** | 3 **V** — hardest visuals, but most of the engine work already went here |
| Design differentiation potential | 5 **J** | 5 **J** | 5 **J** | 4 **E** — the sameness complaint is loudest here [68][69], and the hardest to beat |
| Customer acquisition (5 = cheap) | 2 **J** — owners are not searching for a redesign | 1 **J** | 2 **J** | 5 **J** — reachable in builder communities; self-serve |
| Competition (5 = light) | 2 **E** — vertical platforms bundle ordering and POS [45][46] | 3 **J** | 3 **E** — Squarespace, Cargo, Readymag at $14–$58 per month [59][60][61] | 1 **E** — every tool in §2.1 |
| Repeat purchase | 1 **J** | 1 **J** | 2 **J** | 3 **J** — relaunches, next products |
| Fits export, no hosting | 1 **J** — needs someone to host it | 1 **J** | 3 **J** | 5 **J** |
| **Sum** | **24** | **24** | **28** | **31** |

The table is a way to lay out the reasoning, not a calculation. Most cells are judgment.

### 3.3 Recommendation **[R]**

**Start with software-product landing pages built by their founders** — often with an AI builder, which is exactly why they look the way they do.

Why:
1. **It is the only category where today's engine delivers a complete product.** One page is the site; the buyer can take an HTML export; no hosting, booking engine or menu platform stands in the way. **[V]**
2. **It is where the engine's evidence is.** 17 of the last 20 jobs; the most renderer work. **[P]**
3. **The pain matches the positioning.** "My site looks AI-generated" is a sentence these founders already say. **[M][A]**
4. **It is the cheapest audience to reach and the fastest to answer,** which is what a 30-day test needs. **[A]**

What this choice costs:
- It is the hardest category to win visually: weak assets and the most competition.
- It tempts the engine toward the SaaS conventions the brief wants to escape.

**Confidence: moderate.** The honest alternative is that photo-rich businesses (restaurants, studios) are where the visible quality gap is largest, and that agencies who build for them could take an export. The benchmark is designed to find out.

**Switch criteria, fixed now [R]:** move the focus to hospitality or premium services in month 2 if both hold —
- in the week-3 blind test, the preference uplift over the original on photo-rich sites exceeds the uplift on software sites by 15 points or more; and
- at least 3 of 10 contacted owners or agencies in that category say they would pay, with us deploying the page for them by hand.

**The architecture stays general.** Kinds, content requirements and references are data, not code paths. Nothing in the engine plan is specific to software.

### 3.4 What happened to the earlier plan

`PLAN-SWARMSITE.md` (2026-11-08) described a paid developer kit for people using Claude Code or Codex. It is not contradicted by this strategy: for a technical buyer, a kit is one possible form of the export in §8. Its hard part — proving that an agent can carry a design into someone else's codebase faithfully — is a second validation problem and should wait until the first (do people prefer the design at all?) is answered.

---

## 4. Design quality benchmark

### 4.1 The set

30 sites, fixed before any run and not changed afterwards. 20 for development, 10 held out and never used for tuning.

| Group | Sites | Why |
|---|---|---|
| Software-product landing pages | 14 | The initial category. Half with usable product screenshots, half without. |
| Restaurants | 6 | Photo-led; menu, hours and reservation must survive exactly. |
| Premium services (architecture, interiors, agencies) | 4 | Strong photography, weak presentation. |
| Product / small e-commerce | 3 | Price and buy action must survive. |
| Boutique hotels / other places | 3 | To learn how far the engine is from that category. |

**Mode.** Users choose between "keep my SEO" (default) and "redesign freely" **[V]** (`web/app.html:84-85`). The benchmark runs in the default mode first — it is what most users will get, and it is the harder case, because the headline's words are largely fixed. A subset of 10 is also run in free mode. Engines are only ever compared within the same mode.

Across the set, deliberately include: badly structured, visually outdated, weak imagery, strong imagery, content-heavy, minimal, and clearly different brand temperaments. Exclude from the hold-out any site already used to tune the engine — pdfbeautifier.com alone accounts for 8 of the last 20 jobs **[P]**.

### 4.2 What is kept for every site and engine variant

1. Original desktop and mobile screenshots *(captured today; the mobile one is not yet used)* **[V]**
2. Original content and assets, frozen: `inventory.json`, `assets.json`, `images.json`, `factsheet.json`
3. Current-engine output
4. Experimental-engine output, per variant
5. Desktop screenshots of each
6. Mobile screenshots of each
7. Technical QA results (contract, hard failures)
8. Creative evaluation (critic axes, kept separate from 7)
9. Generation time, per stage
10. Generation cost, per attempt
11. Structural fingerprint and its similarity to other outputs

Items 1–3, 5–7 and 9 are already produced by the pipeline. Items 8 (as a separate score), 10 (in dollars) and 11 are small additions described in the engine plan.

### 4.3 The questions, asked blind

Two screenshots side by side, sides randomised, source hidden:

1. Which looks more professional?
2. Which has stronger typography?
3. Which has a more distinctive visual identity?
4. Which better represents this business? *(original shown for reference)*
5. Which feels less template-driven?
6. Which would you expect from a professional design studio?

Desktop and phone are judged separately. Raters: the owner, at least three working designers, at least five people from the target market **[R]**. Model scores are recorded and never shown to raters.

### 4.4 Targets — proposals, not standards **[H]**

| Comparison | Target |
|---|---|
| Redesign vs. the original site | At least 24 of 30 judged meaningfully better |
| Experimental engine vs. current engine | Preferred in ≥ 65% of blind pairs |
| Swarmsite vs. two or three tools from §2.1 on the same URLs | Preferred in ≥ 60% of blind pairs |
| Technical success rate | ≥ 90% of jobs pass the technical gate with no hard failure |
| Creative success rate | Reported separately; no target until the scale is calibrated against people |

**Technical and creative success are two numbers.** A correct but generic page is not a success. A beautiful page with a broken phone layout is not a success. They are never averaged.

### 4.5 Comparing against other tools

- Candidates: Framer (rated most polished in the one test found [28]), Lovable, and Repaint (closest in shape) **[R]**.
- Run each on the same 10–30 URLs, with its defaults, and screenshot at the same two sizes.
- Read each tool's terms before publishing any comparison. Until then the results are for internal decisions only.
- If we do not win, that is the most valuable thing the 30 days can tell us.

---

## 5. Pricing hypotheses

### 5.1 Anchors **[M]**

| Reference point | Price | Confidence |
|---|---|---|
| Landing-page templates (Framer, Webflow) | mostly $49–$149, one-time | search [64][65] |
| AI site builders | roughly $10–$40 per month; Repaint $25 / $100 / $200 | primary [5][9][14][15][25] |
| Small-business site built by people | $500–$5,000+; freelance design $500–$10,000+ | primary, vendor survey with undescribed method [39] |
| One landing page from an agency or designer | $2,000–$10,000 | search [62][63] |
| Award-level studio site | $20,000–$200,000 | third-party, one studio's own ranges [43] |

A one-time price of $149–$299 sits above a template and an order of magnitude below a person. Almost every competitor sells a subscription bundled with hosting; a one-time purchase with export is a different shape, and whether buyers want that shape is itself unknown **[A]**.

### 5.2 What to test — nothing is hard-coded

| Offer | Price to test | Contents | Status |
|---|---|---|---|
| Free preview | $0 | Analysis and a redesign preview, watermarked or time-limited | Exists as a free hosted preview **[V]**; needs a cost cap (§7) |
| Studio Redesign | $149–$299 one-time | One page, responsive, content preserved, export, a limited number of revisions | Export and payment do not exist **[V]** |
| Studio Pro | $399–$799 one-time | Multi-page, more concepts, more revisions | Multi-page redesign does not exist **[V]** — do not offer yet |

For the first five customers, payment can be a payment link and delivery can be by hand. Building checkout before anyone has tried to pay is the wrong order **[R]**.

---

## 6. The agency opportunity

**Evidence [M]:** white-label and agency plans exist and are priced per seat or per site — 10Web $42.50–$160 per month for 10–20 sites [11], Duda $52–$199 per month [38], Readdy $72–$199 per month [15] (all primary). Agencies already pay for tools that produce first drafts.

**Hypothesis [A]:** small agencies and freelance designers would use Swarmsite for audits, concept development, first drafts and client presentations, and would take a code export for any business category — which also opens restaurants, hotels and studios without Swarmsite hosting anything.

**What to do in the 30 days [R]:** five conversations in week 4 with agencies or freelancers, each shown a before/after of one of *their own clients'* sites. Record: would they pay, per project or per month, and what the export must contain. Build nothing — no multi-client projects, white-labelling, teams or credits — until those conversations say so.

---

## 7. Generation cost model

### 7.1 What is measured today

| Quantity | Value | Source |
|---|---|---|
| Wall time per job | 153–447 s, median 256 s | **[P]** n=20 |
| Model calls per job | 12–22, median 19.5 | **[P]** n=14 |
| Input tokens per job | 87k–344k, median 175k | **[P]** n=14 |
| Output tokens per job | 14k–41k, median 26k | **[P]** n=14 |
| Model | `claude-sonnet-5-5` unless `DIRECT_MODEL` is set | **[V]** `lib/swarm/agents.py:16` |
| List price | $2 per million input tokens, $10 per million output tokens | Anthropic price table, as of 2026-11-03 |
| **Model cost per job** | **≈ $0.61 median; about $0.3–$1.1** | computed from the rows above |
| Per-job cap | 60 calls, 3M tokens — a single runaway job is bounded at single-digit dollars | **[V]** `lib/budget.py:15` |
| Per-IP limit | 3 jobs per hour | **[V]** `server/index.mjs:31` |
| Daily ceiling | 5,000 jobs — about $3,000 a day in model fees at the median if it were ever reached | **[V]** same line; computed |

### 7.2 What is not measured **[V]**

- **Dollars.** `budget.json` records calls and tokens; nothing converts them or stores a cost.
- **Image generation.** `lib/swarm/gen.py` (Higgsfield) has no budget or charge call.
- **Infrastructure.** Railway compute and browser minutes, Supabase storage and egress.
- **Failures and retries.** Failed jobs are not included in any cost figure.
- **Revisions and support.** Neither exists yet.

### 7.3 The number that matters

```
cost per accepted redesign =
    ( model cost of every attempt, including failed ones
    + image generation
    + infrastructure for those attempts
    + revisions
    + support time )
    ÷ number of redesigns a customer accepted
```

Worked example with stated assumptions **[A]**: if the experimental engine costs 2.5× today's job ($1.50), 15% of attempts fail technically, a free preview converts to a purchase 1 time in 30, and each buyer uses one revision, the model cost behind one sale is about 30 × $1.50 ÷ 0.85 + $1.50 ≈ **$54** — significant against a $149 price, and dominated by free previews, not by the paid job. Change the conversion to 1 in 10 and it is about $19. **The free tier's conversion rate, not the price of a generation, decides the economics.** None of these rates is known yet.

### 7.4 Recommendations **[R]**

1. Record dollars per job at write time (tokens × a price table in config), and image-generation spend.
2. Lower the daily ceiling for free previews to a number chosen from a monthly budget, not 5,000.
3. Measure the free-preview → paid conversion before deciding anything else about pricing.
4. Keep the instant v0 and progressive drafts **[V]**: they make a longer generation tolerable at no model cost.

---

## 8. Hosting versus export

| | Model A — full platform | Model B — design studio with export |
|---|---|---|
| What exists today **[V]** | A hosted, `noindex` preview in a storage bucket. No domains, accounts, CMS, forms backend or payment. | The page is already one self-contained HTML file. No download endpoint. |
| To make it sellable | Custom domains, TLS, accounts, editing, uptime, support — months | A download, a sensible bundle (assets as files, a README, a note on fonts), a payment link — days |
| Revenue shape | Recurring | One-time |
| Who it suits | Non-technical owners | Founders, developers, agencies |
| Risk | Operations and security obligations before the design is proven | Hand-off friction for non-technical buyers; lower retention |

**Recommendation [R]: Model B first, plus the hosted preview that already exists.**

- The first 30 days must prove a design preference. Model B gets a paid deliverable into a customer's hands in days; Model A does not.
- It matches the recommended first audience and the agency hypothesis.
- For a non-technical early customer, deploy the exported page for them by hand to a static host. That is a service, not a platform, and it is a cheap way to learn whether hosting is what they are really buying.
- Revisit Model A when there is evidence: a meaningful share of people who wanted to pay did not, because they could not host.

**Do not build a hosting platform without an explicit decision.**

One technical note for the export **[V]**: pages are 0.1–1.8 MB because every image is inlined as base64. That is fine for a preview and poor for a production site. The export should write images as files.

---

## 9. Showing the creative process honestly

**Today [V]:** six steps, each driven by a real state change in the job (`server/index.mjs:17-24`), and an event log of real agent events. Three log lines are fixed strings rather than measurements (`server/index.mjs:250`) and should be removed.

**Proposed stages, each tied to work that actually happens:**

| Stage shown | Real work behind it | Exists today? |
|---|---|---|
| Analysing your brand | Capture, screenshot, asset extraction | Yes |
| Understanding your business | Fact sheet; content requirements with what is missing | Partly — fact sheet yes, content contract no |
| Exploring creative directions | Three concepts, three rendered heroes | **No** — do not show this stage until it exists |
| Designing your new experience | Composing the selected concept | No (today: one concept, fixed structure) |
| Building your website | Deterministic render | Yes |
| Reviewing the result | Technical and creative checks, shown as two results | Partly — exists, shown as one number |
| Refining your design | Targeted revision, with what was changed and why | Partly |

Rules **[R]:**
- A stage appears only when its work is running. No timers, no invented progress.
- When the system is waiting on a model, say so.
- Show artefacts, not adjectives: the three heroes, the list of preserved facts, what was missing on the source site.
- Keep the instant first version and the improving drafts.

**On waiting [M]:** other tools take 2 to more than 8 minutes [28]; a site import at Wix is documented at 15–60 minutes [3]; research on short delays is mixed and nothing was found on multi-minute waits [66][67]. Swarmsite's median is about 4 minutes today **[P]**, and the experimental engine is expected to take 8–12 **[H]**. Whether buyers accept that is to be measured in week 4, not assumed. Generation is never slowed on purpose.

---

## 10. The 30 days

Day 1 is Monday 2026-11-09.

### Week 1 (Nov 9–15) — foundation and measurement

- [x] Architectural audit; main creative bottlenecks identified *(engine plan §1–2)*
- [ ] Owner decisions from the engine plan §14
- [ ] Fix the benchmark set of 30; freeze captured artefacts; record the current engine's output on all 30
- [ ] Separate technical and creative scores in stored results; structural fingerprint; blind comparison page
- [ ] The one-day ablation: house structure as requirements only, behind a flag
- [ ] Design DNA records for the 12 references with honest gaps; recapture at least 5 with desktop and mobile screenshots
- [ ] Record dollars per job

*Done when:* any engine variant can be re-run on the frozen set and compared blind; the first comparison (ablation vs. current) has human judgments.

### Week 2 (Nov 16–22) — quality experiments

- [ ] Content contract; three concepts with a distinctness check
- [ ] Composition format for the hero; validator; hero rendered into the existing page; three-hero comparison
- [ ] About 10 redesigns per variant, same sites
- [ ] First blind round: owner plus two or three designers
- [ ] List the recurring visual failures, ranked by how often raters name them

*Done when:* there is a ranked list of failures and a first answer to "does the experimental hero beat the current one".

### Week 3 (Nov 23–29) — quality improvement

- [ ] Fix the top three recurring failures at the level of the rule, not the site
- [ ] Phone layouts judged as carefully as desktop
- [ ] Full 30-site run of the best variant; hold-out judged for the first time
- [ ] Second blind round with the full rater pool
- [ ] Run two or three other tools on the same URLs
- [ ] Decide, by the fixed rule, whether the experimental engine replaces the current one for demonstrations

*Done when:* the targets in §4.4 are answered with numbers, in either direction.

### Week 4 (Nov 30 – Dec 8) — commercial validation

- [ ] Ten strong before/after pairs from the benchmark, as a page
- [ ] Export as a downloadable bundle; a payment link
- [ ] Show the pairs to at least 30 potential customers in the initial category, each with a redesign of their own site
- [ ] Five agency or freelancer conversations
- [ ] Try to close five paying customers at a price in the test range
- [ ] Record every objection in their words

*Done when:* we know how many of those shown tried to pay, at what price, and why the others did not.

**If week 3 says the design is not preferred,** week 4 is not spent selling. It is spent on the failure list.

---

## 11. Engineering priorities

In order. Each states how it helps the page become more original, professional or fitting — or why it is needed anyway.

| # | Priority | Helps the page? |
|---|---|---|
| 1 | Benchmark, separate scores, blind comparison | Not directly. Without it no later change can be shown to help. |
| 2 | House structure as requirements, not layout (flag) | Yes — restores the variety the 12 references already contain. One day. |
| 3 | Close the two injection gaps; remove the prompt contradiction and the canned progress lines | Not directly. Safety and honesty; half a day. |
| 4 | Design DNA with real evidence; retrieval | Yes — the director and the critic work from grounded principles instead of one line of text. |
| 5 | Three concepts chosen on rendered heroes | Yes — a weak idea is caught before the page is built. |
| 6 | Composition format and renderer for the hero | Yes — the first place a composition can be original rather than selected. |
| 7 | QA with two gates and three failure types | Yes — repairs can address the idea or the execution, not only defects; weak pages stop shipping as "done". |
| 8 | Dollars per job; free-tier ceiling | Not directly. Needed before anyone is invited in. |
| 9 | Export bundle and a payment link | Not directly. Needed for week 4. |
| 10 | Full-page composition | Yes — only if 6 earns it. |

**Not now:** hosting, a CMS, accounts and teams, integrations, pricing tiers, a marketplace, more templates, more agents, multi-page redesign, the agency product.

---

## 12. Assumptions, and how each gets tested

| Assumption | Test | When |
|---|---|---|
| People prefer the redesign to the original | Blind benchmark, 24 of 30 | Week 3 |
| People prefer it to other tools' output | Blind benchmark on the same URLs | Week 3 |
| The house lock, not the references, is the main limiter | Ablation | Week 1 |
| Freer composition can stay technically sound | Technical gate on every variant | Weeks 2–3 |
| The critic's judgment tracks human judgment | Agreement rate on benchmark pairs | Weeks 2–3 |
| Founders of software products are the right first buyers | Reply and purchase rate in outreach; the switch criteria in §3.3 | Week 4 |
| A one-time $149–$299 is acceptable | Attempts to pay | Week 4 |
| An 8–12 minute wait is acceptable | Completion rate of people who start a generation | Week 4 |
| Export, not hosting, is enough | Share of interested people who could not use an export | Week 4 |
| Agencies would pay | Five conversations | Week 4 |
| Free previews convert often enough to carry their cost | Preview → payment rate | Week 4 onward |

---

## Sources

External evidence was gathered on 2026-11-09. Numbers match the references above.

- [1] https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-from-a-url
- [3] https://dev.wix.com/docs/api-reference/account-level/sites/skills/site-import
- [4] https://www.framer.com/agents
- [5] https://www.framer.com/pricing
- [6] https://docs.lovable.dev/features/projects/import-website
- [7] https://docs.replit.com/use-cases/redesign-your-website
- [8] https://www.hostinger.com/ai-builder
- [9] https://www.hostinger.com/pricing/ai-builder
- [10] https://10web.io/pricing-platform/
- [11] https://10web.io/ai-website-builder/for-agencies/
- [13] https://repaint.com/website-redesign
- [14] https://repaint.com/pricing
- [15] https://readdy.ai/pricing
- [16] https://readdy.ai/blog/how-to-redesign-your-website-with-ai
- [17] https://shuffle.dev/blog/2026/01/how-to-redesign-an-existing-website-using-ai/
- [23] https://www.hostinger.com/tutorials/how-to-migrate-from-squarespace-to-wordpress/
- [24] https://help.webflow.com/hc/en-us/articles/38840145286035
- [25] https://durable.com/pricing
- [26] https://www.b12.io/pricing/
- [27] https://unicornplatform.com/pricing/
- [28] https://www.stork.ai/blog/ai-website-builder-test-2026
- [36] https://replit.com/pricing
- [38] https://www.duda.co/pricing
- [39] https://www.webfx.com/web-design/pricing/website-costs/
- [43] https://www.utsubo.com/blog/premium-website-cost-budget-guide
- [45] https://www.owner.com/pricing
- [46] https://www.getbento.com/pricing/
- [47] https://www.getsauce.com/post/popmenu-pricing-fees
- [50] https://helpdesk.resy.com/en_us/booking-button-installation-Skx_7ueNo
- [54] https://hotelbusiness.com/cloudbeds-report-otas-dominate-independent-hotel-bookings/
- [55] https://www.mews.com/en/pricing
- [57] https://hoteltechreport.com/news/cloudbeds-launches-websites
- [58] https://projectcostestimator.com/cost/industry/hotel
- [59] https://archinect.com/forum/thread/146182249/best-website-builders-for-architects
- [60] https://toolradar.com/tools/cargo-site/pricing
- [61] https://pricingsaas.com/companies/readymag
- [62] https://www.wavespace.agency/blog/landing-page-design-cost
- [63] https://projectcostestimator.com/blog/landing-page-pricing-guide-2026
- [64] https://brixtemplates.com/blog/how-much-does-a-framer-website-cost
- [65] https://www.thecssagency.com/blog/guide-to-webflow-templates
- [66] https://arxiv.org/abs/2604.06183
- [67] https://scholarx.skku.edu/item/fa505c37-51c2-43a5-beec-d59852f83e2b
- [68] https://www.claude.com/blog/improving-frontend-design-through-skills
- [69] https://www.utsubo.com/blog/built-with-ai-trust-signals-2026

**Could not be verified, and therefore not relied on:** official prices for Popmenu, Toast websites, Clover/BentoBox, Cloudbeds, SiteMinder, Cargo and Readymag (third-party figures only); marketplace rates on Upwork and Fiverr; any survey of which platforms architecture firms use or what they spend; URL intake in v0 and Bolt; Squarespace prices in dollars; any independent comparison of design quality between redesign tools.
