# REFACTOR.md — running log of the engine refactor

Goal: refactor until the architecture is simple enough to explain in five lines, and every landed change is live-tested, reviewed and committed (see AGENTS.md). One line per step: what changed · live test · next bottleneck.

## Architecture in five lines (keep this true)
1. `capture` reads the client's site: facts, visuals (element-level shots, sub-pages), geometry.
2. Agents (`lib/swarm/agents.py`) write ONE document, `direction.json`: Reader → Designer → Concept → UX → Visual → Copy → UI. Each owns one part.
3. The engine (`lib/render/render_bp.py` + `lib/blueprints/*.bp.json`) renders it deterministically: a winner's measured form + signature moves + the client's content. No model inside.
4. Two graders: the Contract (`lib/qa/contract.mjs`, mechanical promises) and the Critic (`lib/qa/critic.py`, calibrated taste). Score = .55 taste + .45 contract. Defects route back to their owners; weak first round → restart.
5. `server/index.mjs` runs it as a job and streams every agent's real events to `/app`.

## Log
- 2026-11-07 · swarm team (Reader/UX/Copy/UI/Visual) + critic routing loop · live: courtsensei 38→58 · next: visuals
- 2026-11-07 · element-level visual shots, sub-page crawl, perceptual dedupe, commissioned originals (Higgsfield) · live: courtsensei 58, Bálamo 34 · next: moves
- 2026-11-07 · signature moves (split hero, sticky-product, pinned-sequence, type-wall, marquee, story) + Concept agent + one renderer · live: sticky did not stick (body overflow-x:hidden) → fixed with overflow-x:clip, headless-verified · next: contract
- 2026-11-07 · LOOPS: contract.mjs (25 promises at 1440/390), 4-axis calibrated rubric, restart rule · live: scripts/livetest.sh 4 blueprints 75–81 in 66 s · next: run Bálamo + courtsensei through it once API credit is back; then cut Designer's copy duties (Reader+Copy own words, Designer owns form)

## Known debt
- Designer (direct.py) still writes all copy; Copy agent only trims. Split: Designer = blueprint/mode/beats skeleton, Copy = every sentence from the fact sheet.
- `cells` beat type overlaps `facts`; merge.
- Blueprint `sections` roles and renderer families are mapped by prefix lists; make the mapping a table in the blueprint file.
- Critic screenshots cost ~50 s per round; cache shots per section hash.
- 2026-11-07 · images assigned to a beat are reserved for it (sticky frames stole the form's photo), CTA never a logo/banner graphic, 6 form fields · live: 4 bp 75–81; Bálamo 34→65, courtsensei 64 (round 1) · next: critic round time (114 s even in fast mode)
- 2026-11-07 · leads/story never from sources < 900px; orphaned jobs marked failed on worker boot; GET /jobs?status=running; rule: don't push during a run · live: 4 bp pass · next: critic round time
