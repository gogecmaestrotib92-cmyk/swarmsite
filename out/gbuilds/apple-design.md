# /skill — Apple's design rules as a Claude skill (emilkowalski/skills · apple-design) + audit prompt
Install: npx skills add emilkowalski/skills --skill apple-design
## Audit prompt (verbatim)
Use the apple-design skill (and emil-design-eng if it's installed) to audit the UI of THIS app. Don't build anything new and don't change any code yet.
1. Map the app first: every screen/page and every interactive element (buttons, links, menus, modals, drawers, tabs, forms, sliders, toasts, anything that moves).
2. Check each against the skill's rules, in this order:
- Response: reacts on press (pointer-down), not after release? Artificial delays/debounces/long transitions on the input path?
- Motion: interruptible and spring-like, or fixed-duration CSS that jumps? Anything animating layout props (width/height/top/left) instead of transform/opacity?
- Spatial consistency: menus/popovers/sheets grow from the element that opened them? Panels leave the way they came?
- Materials & depth: sticky headers, overlays, modals — hard borders or proper blur/scrim? Translucent layers stacked?
- Typography: one letter-spacing for every size? Line-height not scaling with size? Hierarchy from size alone?
- Feedback & wayfinding: every action confirms itself? User always knows where they are and how back? Inline validation?
- Accessibility: prefers-reduced-motion, focus states, contrast, tap targets under 44px.
3. For every problem: file + line, what the user feels, which rule, exact fix. 4. Rank by how cheap/AI-generated it makes the app feel; 5-min / 30-min / bigger. 5. Top 5 fixes today; wait for OK.
