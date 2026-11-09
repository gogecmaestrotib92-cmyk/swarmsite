# House structure: software / SaaS / dev-tool / data landings

Research date: 2026-11-09. Method: homepage text of each site fetched via WebFetch (no browser), sections recorded top to bottom as they appear in the DOM order. Visual types are inferred from image/video markup and alt text, so a "video" in a hero may be an abstract loop rather than the product; that is flagged where known. Headlines are verbatim, truncated to 12 words.

Sites analysed (8):

| Site | Why it is here | Award status |
|---|---|---|
| cerebrium.ai | requested | Awwwards SOTD 10 Sep 2026 (per juncastudio.com round-up) |
| linear.app | requested | widely cited reference SaaS landing |
| vercel.com | requested | widely cited reference dev-platform landing |
| resend.com | requested | widely cited reference dev-tool landing |
| cal.com | requested | widely cited reference SaaS landing |
| butter.us | requested | Awwwards SOTD winner; homepage is JS-rendered, only partial text extracted (see note) |
| heronai.com | added, Awwwards SOTD 12 Oct 2026 (Awwwards SOTD feed) | AI / data decision product |
| deepbook.xyz | added, Awwwards SOTD 3 Nov 2026 (Awwwards SOTD feed) | trading platform / data product with API-SDK |

Awwwards itself blocks fetching (robots), so award dates come from the public Awwwards SOTD RSS feed and a third-party round-up. A third candidate, Oryzo AI (Lusion), was rejected because it is a satirical fake product page.

---

## 1. Cerebrium (cerebrium.ai)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 1 | hero | "Real-time AI infrastructure that scales with you" | product video | – | y (Try it now / Book a demo) |
| 2 | logos-trust | (none) | logos | 12 | n |
| 3 | other (positioning) | "Production speed without the production complexity" | none | – | n |
| 4 | features (overview) | "Why Cerebrium" | illustration | 4 anchor cards | n |
| 5 | features + figures | "Low-latency from the first request." | image | 2 stats | n |
| 6 | features | "No reservations, no lock-ins." | product screenshot (terminal) | – | n |
| 7 | features | "Bring your own code. We'll run it." | none | – | n |
| 8 | features | "End-to-end Observability for every workload." | product screenshot (dashboard) | – | n |
| 9 | other (security/trust) | "Stable, secure and compliant" | none (badges in text) | 4 | links only |
| 10 | use-cases | "Built with Cerebrium" | none | 3 tabs | n |
| 11 | use-cases (case studies) | "Powering real-time AI across industries" | thumbnails | 7 | y (Read case study ×7) |
| 12 | features (list) | (capabilities list) | none | 14 | n |
| 13 | other (blog) | "Latest from our blog" | thumbnails | 3 | y (See all) |
| 14 | cta | "Start serving LLMs in production today or talk to us…" | none | – | y (Get started / Book a demo) |
| 15 | footer | – | none | ~20 links | n |

Total: 15 sections (13 content). ~1,000 words incl. nav/footer (~550 marketing copy). First product visual: hero video; first product screenshot: section 6.

## 2. Linear (linear.app)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 1 | hero | "The product development system for teams and agents" | product screenshot | – | y (announcement link; sign-up in nav) |
| 2 | features (trio) | "A new species of product tool." | illustrations ("Fig 0.1–0.3") | 3 | n |
| 3 | features (workflow 1) | "Intake and integrations" | product screenshot | 4 backlog items | y (Learn more) |
| 4 | features (workflow 2) | "Planning and monitoring" | product screenshot | – | y (Learn more) |
| 5 | features (workflow 3) | "AI and automations" | product screenshot | – | y (Learn more) |
| 6 | features (workflow 4) | "Build, review, and ship" | product screenshot + code | – | y (Learn more) |
| 7 | other (changelog) | "Changelog" | none | 4 | y (View all) |
| 8 | testimonials + figures | "Linear powers over 50,000 product teams." | none | 3 quotes | y (Customer stories) |
| 9 | cta | "Built for the future. Available today." | none | – | y (4 buttons) |
| 10 | footer | – | none | ~39 links | n |

Total: 10 sections (8 content). ~1,000 words. First product visual: hero. Note: sections 3–6 are features ordered as the product workflow (intake → plan → automate → ship), i.e. an implicit how-it-works.

## 3. Vercel (vercel.com)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 1 | hero | "Agentic Infrastructure" | illustration (abstract glow) | 3 lines | y (Deploy now / Talk to sales) |
| 2 | use-cases + proof + figures | "Build agents on infrastructure that thinks like them" | product screenshot (Notion, customer site) + customer stat | 4 features | n |
| 3 | use-cases + proof + figures | "Ship apps that scale from zero to millions instantly" | product screenshot (Zapier) + stat | 4 | n |
| 4 | use-cases + proof + figures | "Host platforms that serve every customer" | product screenshot (Mintlify) + stat | 4 | n |
| 5 | other (recently shipped) | "Recently shipped" | none | 3 cards | n |
| 6 | logos + cta | "Built by you, or your agents" | logos (Claude, OpenAI, Cursor) | 3 | y (3 buttons) |
| 7 | footer | – | none | ~80 links | n |

Total: 7 sections (5 content, excluding nav). ~700 words (~230 body). First product visual: section 2 (a customer's product on Vercel, not Vercel's own UI). The shortest page in the set; each use-case block fuses features (4 bullets), proof (screenshot) and a figure ("100 million monthly visits").

## 4. Resend (resend.com)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 1 | hero | "Email for developers" | video (abstract light/cube) | – | y (Get started / Documentation) |
| 2 | logos-trust | "Companies of all sizes trust Resend to deliver their most important emails." | logos (text strip) | – | y (Explore Enterprise) |
| 3 | features (integrate) | "Integrate" | code snippet | 13 SDKs + 8 frameworks | y (View on GitHub) |
| 4 | features (DX) | "First-class developer experience" | product screenshot (interactive demo) | 7 responses | y (Send) |
| 5 | features | "Test mode" | product screenshot | 5 | y (Learn more) |
| 6 | features | "Modular webhooks" | none | – | y |
| 7 | features | "Write using a delightful editor" | product screenshot | – | n |
| 8 | features | "Go beyond editing" | product screenshot | – | n |
| 9 | features | "Contact management" | product screenshot | – | y |
| 10 | features | "Broadcast analytics" | none | – | y |
| 11 | features (code) | "Develop emails using React" | code + rendered preview | 4 | y (Get started / Check the docs) |
| 12 | features (grid) | "Reach humans, not spam folders" | none | 9 | n |
| 13 | testimonials (single) | (quote, Guillermo Rauch, Vercel) | logo | 1 | y (Send with Next.js) |
| 14 | features | "Everything in your control" | product screenshot (dashboard) | 3 | n |
| 15 | testimonials (wall) | "Beyond expectations" | none | 10 | n |
| 16 | cta | "Email reimagined. Available today." | none | – | y (Get started) |
| 17 | footer | – | none | 5 link groups | n |

Total: 17 sections (15 content). ~1,800 words (~1,200 without nav/footer). First product visual: section 3 (code) / section 4 (screenshot). Heavy feature run (10 feature blocks) broken by a single hero-quote.

## 5. Cal.com (cal.com)

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 1 | other (segmenter) | "How big is your team?" | avatars | 6 | y (Talk to sales) |
| 2 | hero | "Where people find the time to meet" | product screenshot (booking UI mockups) | – | y (Google / Microsoft / email sign-up) |
| 3 | logos-trust | "The fastest-growing companies use Cal.com for scheduling" | logos | 12 | partial (4 case-study links) |
| 4 | how-it-works + figures | "Finding a time took a week of emails. Now it's one link." | product screenshot (inbox mockup) + Deel stat | 3 steps | n |
| 5 | features (tour) | "One calendar for every way people meet." | product screenshots + code | 6 | n |
| 6 | logos (integrations) | "All your key tools in sync with your meetings." | logos (app icons) | 12 | y (Get started / Explore apps) |
| 7 | features (AI) | "Give your agents a calendar." | code + product screenshot | – | y (3) |
| 8 | use-cases (stories) | "Trusted by teams that meet at scale." | photos + logos | 4 stories, 5 quotes | y (Read stories) |
| 9 | testimonials | "See why our users love Cal.com." | avatars | 12 | y (Show more) |
| 10 | features (product line) | "Hosting more than a meeting? Events takes the whole room." | product screenshot | – | y (2) |
| 11 | other (enterprise/trust) + figures | "Scheduling the whole company actually adopts." | compliance badges | 4 features, 5 badges, 3 metrics | y (2) |
| 12 | faq | "Frequently asked questions." | none | 5 | y (3) |
| 13 | cta + figures | "Scheduling for absolutely everyone." | logo + 3 ratings | 3 | y (Get started for free) |
| 14 | footer | – | logos, badges | many | links |

Total: 14 sections (12 content). ~2,000 words. First product visual: hero. The only requested site with an explicit 3-step how-it-works and a FAQ.

## 6. Butter (butter.us) — partial

The homepage is rendered client-side; WebFetch returned only ~220 words of body copy with no headings, buttons or image markup. An archive summary (saas-pages.pages.dev, 2024 snapshot) adds that the page uses app screenshots, four feature themes, facilitator testimonials and a FAQ. Recorded order from the extracted text:

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 1 | hero / proof-product | (lead: "Create engaging workshops that combine the best of presentation…") | product screenshot (per archive) | – | ? |
| 2 | features (overview) | (toolbox copy, no heading extracted) | ? | – | ? |
| 3 | testimonials + figures | "How can I get Butter?" (quote, 500 % engagement claim) | ? | 1 | ? |
| 4 | features | (pin-on-image, polls, reactions, canvases, kanbans) | ? | 5 named | ? |
| 5 | testimonials | (Meet/Zoom integration quote) | ? | 1 | ? |
| 6 | other (onboarding) | (one link, no downloads) | ? | – | ? |
| – | faq, footer | present per archive | none | ? | ? |

Total: ≥6 content sections, word count not measurable. Pattern that is visible: features interleaved with single testimonials. Treated as supporting evidence only; excluded from the ≥50 % counts below.

## 7. Heron AI (heronai.com) — Awwwards SOTD 12 Oct 2026

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 1 | hero + logos | "Radically different business decision-making." | video background + logo strip | 5 logos | y |
| 2 | proof-product | "Refuse Ordinary" | 2 product videos | – | n |
| 3 | features | "See Beyond the Numbers" | none | 3 | n |
| 4 | features | "Focus on Moving the Business Forward" | 2 product videos (dashboard, revenue at risk) | 3 | n |
| 5 | features | "Unlock New Possibilities" | none | 3 | n |
| 6 | use-cases (dashboards) | "Dashboards built for decisions" | product screenshots | 6 | y (links) |
| 7 | testimonials (rating) | "Community" | star rating | – | n |
| 8 | use-cases (case studies) | "Client Case Studies" | none | 3 | y (Show more) |
| 9 | other (press) | "Featured Media" | none | 6 | y |
| 10 | other (blog) | "Blog" | none | 5 | y |
| 11 | proof-product (tour) | "Want to see it in action? Explore the virtual tour." | illustration | – | y |
| 12 | cta | "Results that Lead to Action in Minutes" | none | – | y (Schedule Time With Us) |
| 13 | other (trust) | (closing statement) | SOC badge | – | n |
| 14 | footer + form | "Beta test with us!" | none | 8 links | y (Book a Demo + email form) |

Total: 14 sections (12 content). ~700 words. First product visual: section 2 (product video), first screenshot section 6.

## 8. DeepBook (deepbook.xyz) — Awwwards SOTD 3 Nov 2026

| # | Role | Headline | Visual | Items | CTA |
|---|---|---|---|---|---|
| 1 | hero + figures | "The Home of DeFi. Built on Sui." | video (poster) | 4 stats | n (Launch App in nav) |
| 2 | features (product line) | "SPOT" | illustration (collage) | 3 | n |
| 3 | features (product line) | "PREDICT" | illustration | 3 | y (Learn More) |
| 4 | how-it-works (dev) | "API and SDK access, from day one." | none | 3 numbered cards | y (Explore Docs / GitHub) |
| 5 | other (trust/security) | "Your keys. Your capital." | illustration | 6 table rows | y (Read the Audit) |
| 6 | faq | "FAQs" | illustration | 5 | y (View all FAQs) |
| 7 | cta | "Start trading on the book behind Sui." | illustration showing interface | – | y (Start Trading) |
| 8 | footer | – | illustration | ~14 links | y |

Total: 8 sections (7 content). ~1,000 words. First product visual: hero video poster (content unknown); the only explicit interface image is in the closing CTA. Illustration-led, not screenshot-led.

---

## Synthesis

Counts below use the 7 fully captured sites (Cerebrium, Linear, Vercel, Resend, Cal.com, Heron AI, DeepBook). Butter supports but is not counted.

### 1. Modal order of roles (present in ≥ 50 % of sites)

| Order | Role | Sites | Typical position |
|---|---|---|---|
| 1 | hero | 7/7 | first (Cal.com puts a segmenter above it) |
| 2 | logos-trust | 5/7 (Cerebrium, Resend, Cal, Heron-in-hero, Vercel-at-bottom) | directly under hero in 4/5 |
| 3 | features (product blocks, each with its own headline, 3–10 blocks) | 7/7 | the body of the page, immediately after logos |
| 4 | use-cases / customer stories | 4/7 (Cerebrium, Vercel, Cal, Heron) | after or fused into features |
| 5 | security / enterprise trust block | 4/7 (Cerebrium, Cal, Heron, DeepBook) | late, before FAQ/CTA |
| 6 | social proof (quotes, ratings or customer stats) | 6/7 (all but DeepBook) | after features, before CTA |
| 7 | "freshness" block (changelog / recently shipped / blog) | 4/7 (Linear, Vercel, Cerebrium, Heron) | just before the testimonials or CTA |
| 8 | cta (closing) | 7/7 | last before footer |
| 9 | footer | 7/7 | last |

Modal sequence: **hero → logos → features (3–6 screenshot blocks, often ordered as a workflow) → use-cases/customer proof → trust (security/figures) → testimonials → [freshness] → [faq] → cta → footer**.

Page length: 7–17 sections, median 14 (incl. footer). Words: 700–2,000, median ~1,000. The two shortest pages (Vercel ~700, Heron ~700) are also the ones that fuse roles (feature + proof + figure in one block).

### 2. Optional roles and what sites do without them

| Role | Frequency | Behaviour when absent |
|---|---|---|
| pricing | 0/7 on homepage | always a separate page; never substituted on the landing |
| faq | 2/7 (Cal.com 5 q, DeepBook 5 q; Butter has one per archive) | simply skipped; no substitute |
| how-it-works (explicit numbered steps) | 2/7 (Cal.com 3 steps, DeepBook 3 numbered API cards) | substituted by features ordered as a workflow (Linear: intake → plan → automate → ship; Resend: integrate → send → test → write → analyse). Not skipped so much as dissolved into features. |
| figures as a standalone cells section | 1/7 (DeepBook hero stats; Cal.com enterprise metrics are close) | figures are embedded: one stat under a feature (Cerebrium), a customer stat under each use-case (Vercel), a single line above testimonials (Linear "over 50,000 product teams"), ratings in the final CTA (Cal.com). |
| testimonial quotes | 3/7 (Linear 3, Resend 1+10, Cal 5+12) | substituted by case-study cards (Cerebrium, Heron), customer stat sentences (Vercel) or a star rating (Heron). DeepBook substitutes an audit link. |
| logos | 5/7 | Linear substitutes a figure line; DeepBook substitutes hero stats. |
| before/after | 0/7 | not used. The closest is Cal.com's "problem" narrative (inbox mockup of email chaos next to "Now it's one link"). |
| video/illustration hero | 4/7 heroes are video/illustration rather than a static screenshot (Cerebrium, Resend, Vercel, Heron, DeepBook); 2/7 static screenshot (Linear, Cal) | when the hero visual is abstract, the first real product visual appears in section 2–4 |

### 3. How the product is shown after the hero

- Number of distinct product visuals after the hero: Linear 4, Resend ~7, Cal.com ~5, Cerebrium 2–3, Vercel 3 (customer products built on Vercel), Heron 4 videos + 6 screenshots, DeepBook 0–1. Median ≈ 4.
- Form: one cropped screenshot (or short loop video) per feature headline, alternating or stacked; code snippets count as "product" for dev tools (Resend, Cal.com, Linear, DeepBook all show code). No site shows a full-page screenshot more than once; the hero carries the wide shot, the body carries crops.
- Dev-tool rule: the first thing after logos is "Integrate"/code (Resend, DeepBook API section, Cal.com API). Infrastructure products that cannot screenshot easily (Vercel, Cerebrium) show customer outcomes or a terminal.
- Award-winning SOTD pages (Heron, DeepBook, Cerebrium) lean on video and illustration in the hero and hold the real UI until mid-page; the mainstream SaaS references (Linear, Cal.com) put the UI in the hero.

### 4. FAQ position and length

Present on 2 of 7 (plus Butter). In both cases it is the **penultimate content section, immediately before the closing CTA**, with **exactly 5 questions** and a "view all / ask anything else" link out. Cal.com attaches two CTAs to the FAQ itself. No site puts a FAQ above the features.

### 5. Recommended house structure (7 slots)

| # | Slot | Beat | Visual | Rule |
|---|---|---|---|---|
| 1 | Hero | photo (product) | wide product screenshot or short loop; split layout | ≤ 8-word headline, one line of sub-copy, 2 CTAs (primary + docs/demo); if no screenshot exists, use abstract loop and move the real UI into slot 3. |
| 2 | Logos | logos | 6–12 logos, one caption line | Directly under hero (4/5 sites that have logos). If no logos: replace with a one-line figure ("powers over N teams") or drop the slot; never pad. |
| 3 | Proof | photo + cells | one product-in-use screenshot/video with one customer result sentence or 1–3 figures | This is the "first real UI" slot. For dev tools make it a code snippet + response. Before/after only when the source actually has a before. |
| 4 | Features | features (3–6 blocks) | one cropped screenshot or code block per block | Order blocks as the user's workflow (intake → … → ship) so the run doubles as how-it-works; collapse to an explicit 3-step `steps` beat only if the source names steps. Break a run of > 5 blocks with a single quote (Resend pattern). |
| 5 | Trust | quote + cells | 1–3 testimonials with avatar/logo, plus compliance badges / uptime / ratings as small cells | Substitutes allowed in this order: quotes → case-study cards → customer stat sentences → rating. Figures live here (or in slot 3), not in their own section. |
| 6 | FAQ (optional) | faq | none | Exactly 5 questions, sits right before the CTA; skip entirely if fewer than 3 real questions. Pricing is never on the landing; link to it from FAQ or nav. |
| 7 | CTA | form | none or logo mark | Closing headline that echoes the hero ("X reimagined. Available today."), 1–2 buttons or an email form; footer follows. Optional "freshness" strip (changelog / recently shipped, 3–4 items) may sit between slot 5 and 6 for products that ship often. |

### Comparison with the draft

DRAFT: hero(split, product) → proof (photo/story: result or main screen; before/after if the source has an original) → figures (cells) → how it works (steps) → features → faq → cta.

**Keep**
- Hero with product visual, split layout: 7/7 start with a hero; 5/7 heroes carry product video/screenshot, the rest put UI in section 2–4.
- A proof slot right after the hero showing the main screen / a result: Heron (product videos in section 2), Vercel (customer screenshot + stat in section 2), Cal.com (inbox mockup + Deel stat in section 4) all do this.
- Features as the body of the page: 7/7, 3–10 blocks.
- FAQ just before CTA: both sites that have a FAQ place it exactly there, 5 questions.
- Closing CTA as the last content section: 7/7.

**Change**
1. **Insert a logos slot between hero and proof.** 5/7 sites show logos, 4 of them directly under the hero. The draft has no logos beat; it is the most common second section in the set.
2. **Demote figures from a standalone slot to cells embedded in proof or trust.** Only DeepBook has a pure figures section; Linear, Vercel, Cerebrium, Cal.com all embed one stat next to a screenshot or a quote. A dedicated "figures" section after proof is not modal and will often be empty for a new product.
3. **Make "how it works (steps)" optional and merge it into features.** Explicit steps appear on 2/7; the modal substitute is features ordered as a workflow (Linear, Resend). The draft's hard "steps → features" sequence should become "features ordered as workflow, with a steps variant when the source names steps".
4. **Add a testimonials / trust slot between features and FAQ.** The draft has no quote beat at all, yet 6/7 sites show social proof after the features and 4/7 add a security/compliance block. This is the second biggest gap.
5. **Drop before/after as a default expectation for proof.** 0/7 sites use before/after; proof is a product-in-use shot plus a customer result line. Keep it as a conditional only.
6. **Keep the FAQ optional, not fixed.** 2/7 presence; skip when the source has fewer than ~3 real questions rather than padding.
7. **Add "freshness" (changelog / recently shipped) as an optional strip** for products that ship often (4/7 have one). Not a slot, but the builder should allow it between trust and FAQ.

Resulting house order: **hero → logos → proof → features (workflow-ordered, steps optional) → trust (quotes + cells) → [freshness] → [faq] → cta → footer.**

---

## Sources

Fetched:
- https://www.cerebrium.ai
- https://linear.app
- https://vercel.com
- https://resend.com
- https://cal.com
- https://butter.us and https://www.butter.us/ (partial, client-rendered)
- https://saas-pages.pages.dev/landing-pages/butter/2024 (archive summary of Butter homepage)
- https://www.heronai.com/ (via redirect from heron-ai.com)
- https://deepbook.xyz/ (via redirect from deepbook.tech)
- https://feeds.feedburner.com/awwwards-sites-of-the-day (Awwwards SOTD feed: Heron AI 12 Oct 2026, DeepBook 3 Nov 2026)
- https://juncastudio.com/news/the-12-best-deeptech-websites-in-2026 (Cerebrium SOTD 10 Sep 2026)
- https://videinfra.com/blog/best-startup-websites-award-winning-examples
- https://www.landing.love/sites/oryzo/ (used to reject Oryzo AI as satire)

Blocked (robots): https://www.awwwards.com/sites/heron-ai, https://www.awwwards.com/sites/sidewave, https://www.awwwards.com/inspiration_search/startups/, https://www.butter.us/scenes.
