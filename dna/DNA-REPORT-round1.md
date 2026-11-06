# DNA Report — Round 1 (Top-10 Awwwards SOTD, deep pass)

Date: 2026-11-06 · Method: opened each site in Chrome, 5–10 screenshots per site incl. scroll bursts, computed-style extraction (fonts, sizes, colors, libs, animation counts). Raw data + screenshots in `dna/<site>/`.

## 0. The honest headline

The top-10 by score is **dominated by custom WebGL one-offs** (Santioni, Pacôme, Jesper, Why Zero, Lidar, Shader hero). Those win awards because a studio spent weeks on a bespoke 3D/illustration idea. That is **not systematizable** and not what a restaurant or a SaaS needs.

What IS systematizable — and what every one of the ten does, WebGL or not — is a set of **decisions**. Below are the decisions, with evidence, and what each means for the transformation engine.

## 1. The 9 decisions behind "wow" (evidence from the 10 sites)

### D1. One big idea per site, and the whole site obeys it
- Shader: "retro 80s computing" → serif type, film grain, CRT 3D, film-strip carousel, vintage team photo, page-curl transition, copy voice ("closed deals").
- Heron AI: "architect's blueprint" → paper texture, ruler ticks, crosshair marks, mono labels, floor plan drawn on scroll, outlined wordmark.
- Maxima: "kindergarten flat shapes" → blobs, arches, kites, mascots, rounded everything.
- Why Zero: "draw a zero to enter" → the brand name IS the interaction.
→ Engine: step 1 of any redesign is **choosing a concept** for the client (from a library of 20–30 concepts matched to industry + brand). Not a "style", a world.

### D2. Extreme type contrast, one or two faces, line-height < 1 on display
- Maxima: Robuck Rounded 56px **/0.80** uppercase vs Diatype 17px/1.2 vs 12px uppercase labels.
- Pacôme: one family (Indivisible), one weight (500): 80px ls −0.05em vs 18px.
- Heron: BT Grotesk 48px/1.0 −0.02em uppercase vs 14px/1.3; Geist Mono 9–12px uppercase ×83 instances.
→ Rule: display 3–5× body size; display line-height 0.8–1.0; negative tracking −0.02…−0.05em; labels 9–12px uppercase mono/grotesk. Never Inter.

### D3. Few words. Very few.
- Pacôme: 81 words on the whole site. Gil Huybrecht: project names only. Heron: 831 words for a full product story. Jesper: zero marketing copy.
- SportBot current landing: ~3,000+ words.
→ Rule: a landing ≤ 600 words; hero ≤ 12 words; every section has one sentence of ≤ 25 words.

### D4. The work / the product is the hero, not a headline about it
- Gil, Jesper, Huy Phan: open directly on the work. Heron: the product drawing floor plans is the hero. Shader: 3D artefact is the hero.
→ Rule: hero must contain a **real artefact** (screenshot, data, object), rendered beautifully, not a device mockup.

### D5. Motion is choreography tied to scroll, not decoration
- Heron: 375 transitions, 59 animations, 126 will-change, GSAP + ScrollTrigger + Lenis + Barba; floor plan draws itself; pinned Observe/Advise/Act.
- Maxima: Lenis smooth scroll; card deck peels on scroll; angled dividers.
- Santioni: headline splits apart to reveal YES/NO.
→ Engine needs a **motion vocabulary** (≈15 named moves) implemented once in GSAP: masked line reveal, split headline, card-deck peel, pinned step story, counter, draw-on-scroll SVG, marquee, page-curl/colour-world switch, cursor tooltip, hover scramble.

### D6. Texture and material beat flat default
- Heron (paper grain + ruler ticks), Shader (film grain), Why Zero (ice/water), Maxima (flat but rounded "paper cut").
→ Rule: pick one material per concept (grain, paper, ice, felt, screen). A 4% noise overlay + one texture move removes "default web" instantly.

### D7. Section rhythm alternates registers
- Maxima: illustration → full-bleed photo → typographic statement → illustration → "Next stop".
- Shader: dark 3D world → page-curl → cream paper world → logos → dark again.
→ Rule: no two adjacent sections with the same register (text/image/data/illustration). Plan the page as beats.

### D8. UI chrome is minimal and corner-anchored
- Jesper: 4 corners only. Gil: name | Profile, Email me. Pacôme: logo | spiral·list | menu pill. Huy: hamburger | wordmark | angled photo.
→ Rule: nav ≤ 4 items + 1 pill; everything else in a menu. Corner anchoring (TL/TR/BL/BR) as a layout system.

### D9. Endings are designed
- Maxima: "Next stop → ADAPTIVE SKILLS TRAINING" + giant wordmark with mascots. Heron: outlined giant "HERON AI" with construction marks. Shader: retro computer + "For companies serious about…".
→ Rule: footer = brand moment (giant wordmark or illustration) + one forward pointer. Never a link dump.

## 2. What is transferable vs. one-off

| Site | Transferable to a client site | One-off (do not try to systematize) |
|---|---|---|
| Heron AI | blueprint concept, mono labels, pinned 3-step story, outlined wordmark footer, grid-lined footer | floor plan that draws itself (custom SVG + canvas) |
| Maxima | ALL of it: flat colour worlds, card-deck peel, angled dividers, Next-stop ending, mascot wordmark | custom illustration set (needs an illustrator or a generated set) |
| Shader | theme-commitment method, grain, serif+retro, page-curl world switch, film-strip carousel | 3D CRT model |
| Gil / Jesper / Huy | corner-anchored UI, work-as-hero, counter pagination, per-project swatches | curved WebGL carousel, 3D floor |
| Pacôme | sound gate, pill UI, cursor tooltip | 3D spiral |
| Santioni / Why Zero / Lidar | gesture/age gates as brand moments | everything else |

## 3. What this means for the engine (replaces "style skills")

A redesign is **not** "apply palette + fonts". It is a pipeline of decisions:

1. **Read** the client: industry, brand assets, real content, real numbers, real screenshots.
2. **Choose a concept** (D1) from a curated concept library (each concept = world + material + type pair + motion subset + copy voice). The user can pick 1 of 3 proposed concepts — this is also the "wow" moment in the product.
3. **Cut** content to beats (D3, D7): ≤ 6–7 sections, each with one register and one sentence.
4. **Build the hero around a real artefact** (D4).
5. **Apply type system** (D2) and **UI chrome** (D8).
6. **Choreograph** motion from the vocabulary (D5), texture (D6).
7. **Design the ending** (D9).
8. **QA against the slop list** (banned words, banned visuals, contrast, mobile).

The swarm then builds that result live — and the agents' labels can now be honest: "Concept", "Beats", "Hero artefact", "Type", "Motion", "Ending", "QA".

## 4. Next extraction round (recommended)

Top-by-score was the wrong sample for a system. Next 10 should be the **product/SaaS subset** (closer to real customers): Heron (done), Cerebrium, Aspen Search, DeepBook, Butter, Illoca, Wembi, ICOMAT, Sharplink, Moto Finance, Seasats — plus 5 non-tech services (Odyssée clinic, White Desert, Tengile, Marvell Tile, Odd Ritual). From those we extract the concept library.

## 5. Numbers captured (for reference)

- Heron AI: BT Grotesk + Geist Mono; ink #282828, paper #F2F1EC, muted #B3B3AF, accent #FA3600; 831 words; GSAP/ScrollTrigger/Lenis/Barba; 375 transitions.
- Maxima: Robuck Rounded + ABC Diatype Rounded; cream #F3EFE0, yellow #FDCB40, orange #FD4401, pale #FFF2B7, green #10B14B, blue #1D5CFF; 24px radii; Lenis.
- Pacôme: Indivisible Variable 500 only; 18px / 80px; #0A0A0A; 81 words; Three.js + Lenis + Nuxt.
