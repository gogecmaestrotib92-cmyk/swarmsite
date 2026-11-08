# Rhythm & layout rules (from taste-skill layout-v4, measured on 327 sites; adapted)

1. **Give sections breathing room.** Aim for one or two screens where content permits; let long lists or FAQs grow naturally, or split them into clear subsections. Never remove real content merely to enforce a screen count.
2. **The hero fills the first screen alone.** At 1440×900 and 390×844 nothing of section 2 shows at load. Main button inside the first screen.
3. **Equal left and right edges.** One `.wrap` per section; every block sits on the wrap lines or the grid columns. No sideways scroll at any width (html,body overflow-x hidden is a safety net, not the fix).
4. Content window at 1440×900: 495–708px → 1 screen; 1,320–1,608px → 2 screens. Shorten redundant wording or split dense content, but retain distinct offerings, proof, FAQs and actions. Merge related content only when no important meaning is lost.
5. At 390: one column, buttons full width, section 1 screen = 464–700px content; split stacks text first.
6. Sticky nav only; no modals, chat bubbles, badges, cookie pills in the demo.
7. **Motion budget:** one move per section (the hero may have two: line reveal + number scramble). One "moment" per page (pinned steps or a mask switch). Everything rests under prefers-reduced-motion.
8. One system: one button pair (primary / outline), one card family, one radius, one link look, one heading scale. Two boxes deep at most.
9. Every visual renders at 1440, 1024, 768, 390. No empty ground where an image is meant to be; no caption under a visual.
10. Hover answers the pointer: buttons step, linked cards lift 2px, underlines draw. No tilt, no carousels.

QA ids (our lib/qa/check.py): hero-fill, section-height, section-count, spill, off-viewport, words-per-screen, h1-length, banned-words, fact-agree, button-labels, contrast, motion-budget, link-count, font-load.
