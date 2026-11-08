# Blueprints — design references for the renderer

A blueprint is a normalized set of design parameters and section roles used to render a client's content. Some entries are derived from measurements of public websites; `atelier` is an original internal concept without a raw reference capture. The renderer interprets those parameters through its own components and fallbacks. A blueprint is not a promise of an exact measurement, a structurally identical reproduction, or a verified mobile implementation.

The [catalog audit](../../docs/blueprint-catalog-audit.md) lists all active entries, their provenance, known measurement limitations and the review process for new candidates.

## Files and provenance

- `<slug>.bp.json` is the normalized schema used by `render_bp.py`: grid, type roles, colours, media treatment, motion hints and section roles. It primarily describes form; it does not establish rights to the source's creative assets.
- `raw/<slug>.json` holds source measurements and annotations where available. These files can include short excerpts of source headings, button labels or other reference text; they are not a content-free data set. Not every entry has a raw file or a fully recorded viewport.
- `../../dna/` is a separate research collection with notes and reference screenshots. Some names overlap with blueprints, but the 16 DNA profiles are not 16 active blueprints. The screenshots and extracted source text are not assets authorized for customer delivery merely because they appear in this repository.
- Reference sites can change or become unavailable. Source URLs, award status, capture date and terms should be checked independently when a reference is reviewed again.

## Pipeline and limits

1. `lib/blueprint/extract.js` can measure a visible page in a browser and outputs a compact JSON record. It samples a limited number of sections and elements, is sensitive to the current viewport and loading/animation state, and does not capture every interaction or canvas/WebGL scene. The extractor change currently in progress records both viewport width and height and re-measures page height after the scroll pass; it does not retroactively update older raw files or guarantee that all late-loaded content was visited. Its `bpout` output element is inserted into the page and should be removed before taking reference screenshots.
2. Raw measurements are annotated and passed through `lib/blueprint/normalize.py`; missing and inferred values can receive defaults. A raw file is evidence of a capture, not proof that every normalized value was measured.
3. `lib/render/render_bp.py` combines the normalized form with the client's direction, content and authorized assets using recipe components. Components have their own eligibility checks and fallbacks, so the result may differ materially from the source's section geometry or motion.
4. A candidate is ready for the active catalog only after its source and representative generated outputs have been reviewed on desktop and mobile, including reduced motion, content preservation and working actions. The mechanical contract complements but does not replace visual review.

## Normalized schema

```text
{ id, class: place|service|software|product, archetype, source,
  grid: { frame, gutter, col, container, maxw },
  type: { display, h2, h3, body, label },
  colour: { paper, ink, accent, bands },
  media: { radius, aspects, bleed },
  button, nav, motion,
  sections: [ { role, screens, pad, band, head, body, media, cols } ] }
```

Fields vary with the source and the normalizer; missing data and fallbacks should not be interpreted as observed measurements. Reuse licensed or client-provided content and assets in generated output; do not treat third-party reference photographs, logos, text, fonts, video or code as freely reusable.
