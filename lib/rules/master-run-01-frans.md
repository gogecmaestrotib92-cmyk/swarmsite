# Master run 01 — frans.rs (place · restaurant) → rules extracted for the system

Input: a typical WordPress restaurant site. No H1, 58 nav links, 412 words, literary quote as the only copy, 7 garden photos, one 854×480 video, Cormorant Garamond, cream + deep green.
Output: 7 screens, 2.3 MB single file (5 photos @1344px, 5s hero loop 930 KB), QA clean at 1440 and 390.

## What made it premium (each line is a rule candidate)
1. **Keep the client's world, remove the noise.** Cream #F4EFE3 + green #0F2A14 are theirs; the nav went from 58 links to 4 + one action. Nothing new was invented: every price, hour, number and quote is from the site.
2. **Photography leads on a place.** Hero = the client's best photo turned into a 5 s loop (image-to-video from their own still, Kling 2.6, "subtle motion only"). Rule: generate motion from the client's photo, never a new scene. Every later section carries one full-bleed photo with a dark gradient and small caps on it.
3. **One type moment per page.** "Franš je izlazak." in 150px italic Cormorant, centered, with the quote under it. Nothing else on that screen.
4. **Serif as the whole voice.** Display, lede, ledger, labels (small caps, .22em tracking) are all Cormorant; the sans only for 16px UI. Mono labels are wrong for a place.
5. **The ledger is the artefact.** A restaurant's signature component is a dotted-leader price list in big serif — real dishes, real prices, tabular numbers. It replaces "features".
6. **Scale contrast.** Every screen has exactly one huge thing (H1 124px, italic quote 150px, facts 104px, the Franš wordmark 380px) and the rest is small.
7. **Facts as the band.** 1982 · 44 · 9–00 over a photo — numbers the client already had, set large.
8. **Reservation as a dark inverse screen.** The transaction gets its own world (ink background, hairline inputs, the real phone/WhatsApp numbers). The form is the client's own fields.
9. **Ending = wordmark.** Italic giant "Franš", 4 short columns, one legal row, "Sledeće: rezervišite sto →".
10. **Motion budget held.** hero-intro, clip-reveal on photos, masked lines on H2s, parallax on the band, giant-scrub. No pins, no scrubbed text. On mobile the same page just stacks.

## What the system still can't do alone
- Choosing the hero photo (the waiter walking away) and the pull-quote was taste, not a rule. Next: a "pick the frame" heuristic (a person seen from behind, depth, light) + an LLM pass for the quote.
- Logo had to be rebuilt from its alpha mask (PNG was white-on-transparent). capture.mjs must fetch logos as files, which Playwright does.
- Word budget per screen was obeyed by hand; the copy pass needs the LLM step in the pipeline.
