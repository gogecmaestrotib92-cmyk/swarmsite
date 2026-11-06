# Swarmsite — paste a URL, get your site rebuilt at studio level

Pipeline: `lib/pipeline/capture.mjs` (Playwright: inventory, assets, images, screenshots) → `lib/audit/diagnose.py` → concept (`lib/concepts`) + typography (`lib/typography`) + colour worlds (`lib/colour/palette.py`) → `lib/render` (content JSON → HTML) → `lib/motion/moves.js` + `lib/artefacts` → `lib/qa` (check.py, shots.mjs) → `swarm.js` (the live rebuild show).

- `web/` — the landing (static; Vercel root = `web`)
- `lib/rules/` — copy, rhythm, master-run notes (the taste, written down)
- `out/frans.rs/` — master run 01 (restaurant) with build script
- `v3/`, `lib/motion/kitchen-sink.html` — concept demos and the motion catalogue
- `out/gbuilds/` — prompts collected from gbuilds.si (design, security, legal, pre-launch, SEO, promise)
