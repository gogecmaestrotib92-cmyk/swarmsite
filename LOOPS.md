# LOOPS.md — how this project lets the swarm drive

Rules we hold ourselves to (after Karpathy's field notes), and where each lives.

1. **Write the loop, not the prompt** — `lib/swarm/run.py`: gather → reason → act → verify → repeat, up to 3 rounds or score ≥ 80.
2. **Separate the roles** — `lib/swarm/agents.py`: Reader, Concept, UX, Copy, UI, Visual each own one part of `direction.json`; the Critic (`lib/qa/critic.py`) never grades its own work; the renderer (`lib/render/render_bp.py`) is deterministic and never asks a model.
3. **Negotiate the contract first** — `lib/qa/contract.mjs`: ~25 mechanical promises (no empty screens, no upscaled or repeated pictures, h1 ≤ 8 words, one CTA, sticky frames well formed, contrast, no overflow) graded on the real render at 1440 and 390. Broken promises are routed to their owner as notes. Which page stands is decided on two tracks that are never added up (`lib/swarm/run.py` `beats`): fewer broken hard promises, then clearing the technical bar, then the critic's reading — the blended `.55 taste + .45 contract` is still shown as the page's score but no longer decides (`SWARM_DECIDE=blend` brings it back). The page that ships is measured in a browser while it loads, scrolls and moves (`lib/qa/measure.py`) and the Standard's findings are written beside it (`findings.json`).
4. **Write to disk, not context** — `factsheet.json`, `direction.json`, `images.json`, `contract.json`, `critic.json`, `swarm.json` in `out/<slug>/`. A run can die and be re-read from these.
5. **Let the loop restart** — first round < 45 → throw the idea away: new concept, alternative blueprint, moves cleared; the best render is always kept.
6. **Score the subjective** — four axes (design 35, originality 20, craft 25, function 20) calibrated on Butter 90, Cerebrium 88, Tengile 92.
7. **Read the traces** — `swarm.json` holds every round: scores, broken promises, every fix and who got it.
8. **Delete the harness** — legacy renderer removed; the critic only routes, it no longer edits.
9. **The bottleneck always moves** — it was motion (fixed: sticky/pinned), then visuals (commissioned originals), now the contract. Find the next one.
