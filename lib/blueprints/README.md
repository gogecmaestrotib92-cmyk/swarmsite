# Blueprints — reverse-engineered winners, realised with the client's content

A blueprint is an exact, measured description of one award-winning site: section order and heights, grid
(frame, gutter, column width, container), type scale per role (family, size, weight, tracking, leading),
spacing rhythm, image treatment (aspect, fit, radius, bleed), buttons, nav, motion (libs, easings, durations,
what moves on scroll). Nothing creative is stored — no copy, no images, no code. The renderer builds the
client's content INTO the blueprint. Result: structurally identical to the winner, legally and brand-wise the client's.

## Pipeline
1. `lib/blueprint/extract.js` — runs in Chrome on the live site (via `fetch('https://swarmsite.si/js/extract.js')`
   + eval, or pasted inline when CSP blocks fetch). Writes JSON into `<article id="bpout">`; read with page text.
2. `raw/<slug>.json` — the measurement, lightly annotated (`role`, `note` per section, `class`, `archetype`).
3. `shots/<slug>-N-*.jpg` — 3 reference screenshots (hero, signature section, band/footer).
4. (next) `normalize.py` → `<slug>.bp.json`: the clean schema below.
5. (next) `render_bp.py` — builds a page from `direction.json` (content) + a blueprint (form).

## Schema (target)
```
{ id, class: place|service|software|product, archetype, source,
  grid: { frame, gutter, col, container, maxw },
  type: { display:{fam,px,w,ls,lh}, h2:{…}, h3:{…}, body:{…}, label:{…,tt,ls} },
  colour: { paper, ink, accent, bands: [light|dark per section] },
  media: { radius, fit, aspects:[…], bleed: bool },
  buttons: { h, pad, radius, tt, px },
  nav: { pos, h, links, blur },
  motion: { smooth: lenis|none, ease, dur:{fast,slow}, cursor, ideas:[…] },
  sections: [ { role, screens, cols, lefts, pad:[t,b], slots: { label, h2, lede, media[], items[] } } ] }
```

## Collected
- butter (software, editorial product story; 60/1300 grid, DieGrotesk 103/58/44/21 + mono 13, radius 32, Lenis, cursor)
- cerebrium (software, dark/light bands, ABC Favorit 144/86/57 light, Suisse 27 body, mono 13 labels, 54px pink buttons; sticky dimming list)
- aino (service, index-grid; 16px frame, 4×340 cols, 4:5 tiles, 13px uppercase labels, one 38px sentence, no motion)

## Skipped (WebGL/preloader-driven, not reproducible generically)
- obys.agency, heron.ai (domain for sale)

## Next
3 per class: place (restaurant/hotel/clinic), service, software, product. Candidates (2026 SOTD list):
software — Happly, Dirac.com, Elva (Lazarev), Fourmula AI, Resend Launch Week, Sidewave;
service — Studio Namma, Good Fella, KVS Studio, Ario Law Firm, ARCHIDOMO;
place — Utopia Tokyo, Tout Bien Pils, Loft 31, Hildén & Kaira, Detroit Paris, Lasala Plaza Hotel;
product — Halfdays, ANDERSSON BELL, Olive, Joby, Longbow, Enerblock, Pomelo.
