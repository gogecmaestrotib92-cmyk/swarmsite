# Performance rules — "fast is a feeling" (the 23 lines; Deloitte/Google: 0.1 s faster → +8.4% retail conversions, web.dev "Milliseconds Make Millions", 2020)

Applies to (a) swarmsite.si itself, (b) every site the swarm ships, (c) the worker/API.

## What the user sees in the first second
1. Skeleton screen while it loads, never a blank page. → /app: swarm intro is the skeleton; the "before" screenshot shows within 300 ms.
2. Show the result before the server answers (optimistic UI). → /app: URL accepted instantly, job state streamed.
3. Stream AI answers word by word. → chat editor streams; swarm HUD streams agent labels.
4. Images as WebP, only as big as the screen. → `srcset` 480/960/1440; shipped sites: assets split out of the single file at publish time (base64 only for preview).
5. Lazy-load images below the fold (`loading="lazy" decoding="async"`), always `width`/`height`.
6. Don't search on every keystroke; debounce until typing stops (chat editor, URL field validation).
7. Paginate: 20 at a time, never all (projects list, versions).
8. Chat widgets and trackers after the page (`defer`, or after `load`). No tracker before consent.
9. Self-host fonts, two weights max, `font-display: swap`, preload the hero face, subset by unicode-range.
10. Split code by page; `defer` every script; no render-blocking CSS beyond the inline critical block.

## The hidden half: database and server
11. Index every column you filter or sort by (projects.user_id, versions.project_id, payments.stripe_id).
12. No N+1: one query, not a hundred (versions with project in one select).
13. Select only the columns you need (never `select *` on versions with content JSON for lists).
14. Cache what everyone asks for (concept library, fonts/palettes JSON, public previews with Cache-Control).
15. Slow jobs to a background queue: capture, render, QA, video generation, emails, exports. Nothing slow inside an HTTP request.
16. Run independent steps in parallel (capture desktop + mobile; image downsizing; QA at 1440 and 390).
17. Never call the same API twice for the same input (memoize Higgsfield/Replicate by prompt hash; cache captures by URL+day).
18. Timeout on every outside API (capture 60 s, image gen 180 s, video 10 min) with a fallback path.
19. Server in the same region as the database (worker + Supabase in one region; eu-central for EU users).
20. Compression and a CDN (Vercel/Cloudflare default; immutable cache headers on fonts/js/webp).

## Did it work
21. Measure on real users (Vercel Speed Insights / web-vitals), not on the laptop.
22. Test on a cheap phone on slow internet (QA: throttled mobile profile in Playwright, 390×844).
23. Every week: the slowest page, reported.

## Done on the landing (2026-11-06)
self-hosted Instrument Sans 400/500 + JetBrains Mono 400 (84 KB total, unicode-range subsets), hero font preloaded; before/after as WebP 480/960 with srcset, lazy, dimensions; GSAP/ScrollTrigger/Lenis/moves self-hosted and deferred; zero external requests; cache headers in vercel.json.
## TODO when /app and the worker exist
skeleton + optimistic job state (1–3), queue + timeouts + memoization (15–18), indexes (11), Speed Insights (21), weekly slowest-page report (23).
