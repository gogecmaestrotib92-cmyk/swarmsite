# STYLE SKILL — Clean Minimal Light (v0.1)

Derived from 28 Awwwards SOTD winners (Apr–Nov 2026) tagged Clean / Minimal / Typography with a light base and no WebGL/3D.
Reference set (score): Aspen Search 7.48, Odd Ritual 7.55, Kononenko 7.27, Signal-A 7.22, Oimachi 7.31, Off Menu 7.37,
Marvell Tile & Stone 7.26, Odyssée 7.38, Tresmares Capital 7.25, Brunello Cucinelli AI 7.19, Studio X 7.38, twks 7.35.

## 1. Palette (hard rules)
- Base: warm off-white, never pure #FFFFFF for large surfaces. Observed: #F6F4F2, #F2F0E6, #F1EDE7, #EDE7DE, #E8E5DF, #FFFBF7.
- Ink: near-black, never pure #000 for body. Observed: #232323, #282828, #12110D, #131410, #35311F, #1A1A1A.
- ONE accent only, saturated, used on ≤5% of the page (primary CTA, one highlight, one underline). Observed: #050fff, #FF4101, #D81413, #1E305E.
- Brand accent is kept if the client has one (SportBot: #10B981 → keep hue, use as the single accent).
- Dividers: 1px lines at ink/12%. No drop shadows on cards. No gradients. No glassmorphism.

## 2. Typography
- Two families max. Display: a condensed or grotesk with character (client already uses Barlow Condensed → keep it as display, it is the brand). Body: a neutral grotesk (Inter is BANNED; use Geist, Satoshi, Instrument Sans, or system-ui).
- Display sizes are big: hero h1 between 72–120px desktop, tracking -0.02 to -0.04em, line-height 0.9–1.0, uppercase allowed for display only.
- Body 16–18px, line-height 1.5–1.6, max line length 60–70ch.
- Small labels: 11–12px, uppercase, letter-spacing 0.12–0.18em, ink/55%. Used for section numbers ("01", "02"), eyebrows and table headers.
- Numbers (prices, stats) are set in the display face, large, tabular.

## 3. Layout & spacing
- 12-col grid, max-width 1280–1440, outer gutter 24px mobile / 48–64px desktop.
- Section vertical padding 96–160px desktop. Air is the main design element.
- Asymmetry over symmetry: hero text left 7 cols / visual right 5 cols; feature lists as 2-col "label | text" rows, not 3 identical cards.
- Section numbering ("01 — Before you stake it") used as navigation rhythm (seen in Odd Ritual, Kononenko, client's own site).
- Tables and ledgers are a feature, not a chore: hairline rows, right-aligned numbers, monospace or tabular figures.
- Sticky slim nav, 56–64px, transparent → base colour on scroll; wordmark left, 4–6 links, one outlined CTA.

## 4. Section patterns allowed (from the Elements library)
- Hero: big headline + one-line sub + one primary CTA + one text link + a single real product screenshot (no device frame mockups with fake shadows).
- Big-number stats row (Revelatio "Big Numbers"): 3–4 numbers, display face, label beneath, hairline between.
- Ledger / public record table (client content): the strongest trust element, give it a full section.
- Price comparison list (client "Same bet, better price"): vertical list, best row highlighted with accent bar on the left.
- Three ways in: 3 rows, not cards — number, title, one sentence, arrow link.
- Pricing: two columns side by side, hairline separated, accent only on the recommended CTA; lifetime as a separate quiet band.
- FAQ: accordion with "+" (twks "Accordion", Signal-A "Minimal Grid Accordeon"), questions in display face.
- Footer: large wordmark bottom-left, links in small caps, responsible-gambling note in a bordered box.
- Marquee allowed once (logos or league names), slow (≥40s loop).

## 5. Motion (restraint)
- Entrance: fade + 12px rise, 500–700ms, ease-out, staggered 60ms. Nothing bounces.
- Hover: underline draw or colour shift only. Scale ≤1.02.
- No parallax, no 3D, no cursor followers, no particle effects.

## 6. Copy rules
- Headline ≤ 8 words. Concrete beats abstract. Keep the client's own claims and numbers verbatim; never invent testimonials, logos, or stats.
- Banned words: unlock, seamless, elevate, revolutionize, supercharge, next-level, cutting-edge, game-changer, effortless, empower. No emoji.
- Labels are nouns, buttons are verbs ("Check my next bet", not "Get started").

## 7. Banned visual clichés
- Purple/blue gradients, glass cards, icon-in-circle feature grids, 3 identical cards in a row, stock illustrations of people, floating blobs, neon glow, "trusted by" rows with fake logos, device frames with heavy shadows.

## 8. Checklist before shipping
[ ] ≤1 accent colour, ≤5% coverage   [ ] ≤2 font families, none is Inter   [ ] no gradients/shadows/glass
[ ] all client numbers preserved        [ ] every section has one message     [ ] contrast AA on body text
[ ] mobile: single column, hero ≥48px   [ ] no banned words                   [ ] real screenshot or none
