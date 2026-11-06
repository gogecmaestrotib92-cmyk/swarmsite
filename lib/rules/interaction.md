# Interaction rules (from Apple's WWDC design talks via emilkowalski/apple-design + emil-design-eng + ui-cheatsheet)

These are the "logic" under the look. Every page the swarm ships, and our own app, must pass them.

## Response
1. Feedback on pointer-down, never on release: `.btn:active{transform:scale(.97);transition:transform 100ms ease-out}`.
2. Nothing on the input path waits: no debounce on clicks, no transition the user must wait out, no `ease-in` on things that open (use `ease-out` under 300ms).
3. Drags, sliders, sheets track 1:1 with the pointer (Pointer Events + setPointerCapture; respect the grab offset).

## Motion
4. Animate only `transform` and `opacity` (and `clip-path`); never width/height/top/left.
5. Anything a user can touch uses springs, critically damped by default (bounce only after a flick). Scroll-driven reveals may be eased (expo.out) because the user doesn't interrupt them with a gesture — but they must be `once` and short (≤1.4 s).
6. Interruptible: a closing panel the user grabs again follows the finger. Never lock input during a transition.
7. Spatial consistency: a thing leaves the way it came; menus/popovers grow from their trigger (`transform-origin` at the trigger; modals stay centred).
8. Reduced motion is a cross-fade, not nothing: `prefers-reduced-motion` → opacity only, no parallax, no pins, no marquee. `prefers-reduced-transparency` → solid chrome.

## Materials & depth
9. Sticky chrome is a translucent material (`backdrop-filter: blur(14–20px) saturate(180%)` + 60–80% background), content scrolls under it. Never stack two light translucent layers.
10. Scroll-edge effect instead of a hard 1px line under a sticky header where it overlaps content.
11. Modal task = scrim + background pushed back; parallel panel = no scrim.

## Typography
12. Tracking is size-specific: display −0.02…−0.04em, body ≈ 0, small caps labels +0.1…+0.22em. Never one letter-spacing for all sizes.
13. Leading inverse to size: 0.95–1.05 on display, 1.45–1.6 on body. Hierarchy = size + weight + leading as a set.
14. `font-variant-numeric: tabular-nums` on any number that changes; body line length ≤ 65ch; optical sizing on when the face has it (Fraunces, Instrument Serif).

## Wayfinding & feedback
15. Every screen answers: where am I, where can I go, what's there, how do I get out. Nav items named for contents, not "Home".
16. Four kinds of feedback: status, completion, warning, error. Inline validation, not on submit. Confirmation dialogs only for the irreversible.
17. One main action per screen, same label everywhere it appears.

## Craft checks (ui-cheatsheet)
avatar `flex-shrink:0`; eased gradients (extra stops), not linear fades; `blur(2px)` during a hard transition; "1 members" → Intl.PluralRules; timestamps absolute after a week; tap targets ≥ 44px.

## Where this lives in the system
- moves.js: hover layer (press scale, underline draw), nav hide/show, reduced-motion guard — ✔
- components.css: tabular-nums on .num, tracking per role — ✔ ; translucent nav + scroll-edge effect — TODO
- QA (check.py): add `press-feedback`, `layout-animation` (width/height/top/left in transitions), `tap-target`, `tracking-per-size`, `reduced-motion` ids — TODO
- Audit prompt (gbuilds /skill) runs on our own app before launch.
