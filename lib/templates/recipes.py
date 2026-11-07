"""recipes.py — the 12 templates. Each is an ORIGINAL composition inspired by one winner's measured form (the .bp.json still
supplies type scale, colour relationships, spacing and easing). A recipe is a rhythm of SLOTS; each slot says which beat types
it accepts and which component performs them. The renderer walks the slots in order and gives each the first unused beat it
accepts, so the page keeps the template's rhythm while the UX agent's order decides which beat of a type comes first.

Components (lib/render/render_bp.py): hero moves  split | shot | photo | centre | poster | inset
  sticky-product · pinned-sequence · type-wall · marquee · story · cards · two-col · ledger · faq · statement · quote-band
  photo · photo-pair · collage · overlay · rail · numbers · stickers · product-row · cta · cta-photo · giant · footer
accepts: beat types (features, steps, cells, facts, faq, ledger, quote, photo, form) · 'photo*' = a photo slot that may be filled
from the image pool even without a photo beat · 'any-list' = features|steps|cells|facts · optional:True = skip silently when nothing fits."""

L = ['features', 'steps', 'cells', 'facts']
RECIPES = {
    # ── software, light, editorial product ─────────────────────────────────────────────
    'butter': {'class': 'software', 'hero': 'shot', 'closing': 'cta', 'slots': [
        {'accepts': ['features'], 'comp': 'sticky-product'},
        {'accepts': ['cells', 'facts'], 'comp': 'marquee', 'optional': True},
        {'accepts': ['steps'], 'comp': 'story', 'optional': True},
        {'accepts': ['quote'], 'comp': 'statement', 'variant': 'wide', 'optional': True},
        {'accepts': ['cells', 'facts'], 'comp': 'cards', 'optional': True},
        {'accepts': ['ledger'], 'comp': 'ledger', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── software, dark, type-led, pinned tour ───────────────────────────────────────────
    'cerebrium': {'class': 'software', 'hero': 'centre', 'closing': 'cta', 'slots': [
        {'accepts': ['features'], 'comp': 'pinned-sequence'},
        {'accepts': ['quote'], 'comp': 'type-wall', 'optional': True},
        {'accepts': ['facts', 'cells'], 'comp': 'numbers', 'band': 'dark', 'optional': True},
        {'accepts': ['steps'], 'comp': 'two-col', 'optional': True},
        {'accepts': ['ledger'], 'comp': 'ledger', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── software, dark, giant statements, two audiences ─────────────────────────────────
    'deepbook': {'class': 'software', 'hero': 'centre', 'closing': 'cta', 'slots': [
        {'accepts': ['features'], 'comp': 'pinned-sequence'},
        {'accepts': ['steps', 'cells'], 'comp': 'two-col', 'optional': True},
        {'accepts': ['quote'], 'comp': 'type-wall', 'optional': True},
        {'accepts': ['facts'], 'comp': 'numbers', 'optional': True},
        {'accepts': ['ledger'], 'comp': 'ledger', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── place, light, photographs tell it ───────────────────────────────────────────────
    'tengile': {'class': 'place', 'hero': 'photo', 'closing': 'cta-photo', 'slots': [
        {'accepts': ['quote'], 'comp': 'statement', 'variant': 'right', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'photo-pair', 'optional': True},
        {'accepts': ['features', 'cells'], 'comp': 'cards', 'variant': 'photos'},
        {'accepts': ['quote'], 'comp': 'quote-band', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'photo', 'variant': 'bleed', 'optional': True},
        {'accepts': ['steps', 'facts'], 'comp': 'story', 'optional': True},
        {'accepts': ['ledger'], 'comp': 'ledger', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'collage', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── place, light, giant uppercase, pinned sequence ──────────────────────────────────
    'white-desert': {'class': 'place', 'hero': 'photo', 'closing': 'cta-photo', 'slots': [
        {'accepts': ['quote'], 'comp': 'statement', 'variant': 'upper', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'photo', 'variant': 'tall', 'optional': True},
        {'accepts': ['features', 'cells'], 'comp': 'cards', 'variant': 'wide2'},
        {'accepts': ['quote'], 'comp': 'quote-band', 'variant': 'centre', 'optional': True},
        {'accepts': ['steps'], 'comp': 'pinned-sequence', 'optional': True},
        {'accepts': ['giant'], 'comp': 'giant'},
        {'accepts': ['ledger', 'facts'], 'comp': 'overlay', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── place, light, chapters over photos, card rail ───────────────────────────────────
    'belgrade-arbor': {'class': 'place', 'hero': 'photo', 'closing': 'cta-photo', 'slots': [
        {'accepts': ['quote'], 'comp': 'type-wall', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'overlay', 'variant': 'chapter', 'optional': True},
        {'accepts': ['features', 'cells'], 'comp': 'rail'},
        {'accepts': ['photo*'], 'comp': 'overlay', 'variant': 'chapter', 'optional': True},
        {'accepts': ['steps', 'facts'], 'comp': 'story', 'optional': True},
        {'accepts': ['giant'], 'comp': 'giant'},
        {'accepts': ['ledger'], 'comp': 'ledger', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── place, light, inset hero, pinned cards, photo marquee ───────────────────────────
    'units': {'class': 'place', 'hero': 'inset', 'closing': 'cta', 'slots': [
        {'accepts': ['quote'], 'comp': 'statement', 'variant': 'wide', 'optional': True},
        {'accepts': ['features', 'cells'], 'comp': 'sticky-product'},
        {'accepts': ['steps', 'facts'], 'comp': 'two-col', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'photo-pair', 'optional': True},
        {'accepts': ['ledger'], 'comp': 'cards', 'variant': 'contained', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'marquee', 'variant': 'photos', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── service, dark, work grid ────────────────────────────────────────────────────────
    'aino': {'class': 'service', 'hero': 'centre', 'closing': 'cta', 'slots': [
        {'accepts': ['photo*'], 'comp': 'photo-pair', 'optional': True},
        {'accepts': ['quote'], 'comp': 'statement', 'variant': 'wide', 'optional': True},
        {'accepts': ['features', 'cells'], 'comp': 'cards', 'variant': 'photos'},
        {'accepts': ['photo*'], 'comp': 'photo', 'variant': 'bleed', 'optional': True},
        {'accepts': ['steps', 'facts'], 'comp': 'numbers', 'optional': True},
        {'accepts': ['ledger'], 'comp': 'ledger', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── service, light, manifesto + sticky work grid ────────────────────────────────────
    'lpas': {'class': 'service', 'hero': 'split', 'closing': 'cta-photo', 'slots': [
        {'accepts': ['quote'], 'comp': 'type-wall', 'optional': True},
        {'accepts': ['features', 'cells'], 'comp': 'sticky-product'},
        {'accepts': ['steps', 'facts'], 'comp': 'cards', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'photo', 'variant': 'bleed', 'optional': True},
        {'accepts': ['ledger'], 'comp': 'ledger', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── service, light, editorial studio (12th) ─────────────────────────────────────────
    'atelier': {'class': 'service', 'hero': 'split', 'closing': 'cta', 'slots': [
        {'accepts': ['quote'], 'comp': 'statement', 'variant': 'right', 'optional': True},
        {'accepts': ['features', 'cells'], 'comp': 'story'},
        {'accepts': ['steps'], 'comp': 'pinned-sequence', 'optional': True},
        {'accepts': ['facts'], 'comp': 'numbers', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'collage', 'optional': True},
        {'accepts': ['ledger'], 'comp': 'ledger', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── product, light, poster + stickers + red band ────────────────────────────────────
    'crav': {'class': 'product', 'hero': 'poster', 'closing': 'giant', 'slots': [
        {'accepts': ['features', 'cells'], 'comp': 'stickers'},
        {'accepts': ['quote'], 'comp': 'quote-band', 'variant': 'accent', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'photo', 'variant': 'bleed', 'optional': True},
        {'accepts': ['steps', 'facts'], 'comp': 'statement', 'variant': 'left', 'optional': True},
        {'accepts': ['ledger'], 'comp': 'product-row', 'optional': True},
        {'accepts': ['photo*'], 'comp': 'collage', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
    # ── product, light, photo-left hero, product rows ───────────────────────────────────
    'halfdays': {'class': 'product', 'hero': 'split', 'closing': 'cta', 'slots': [
        {'accepts': ['cells', 'ledger'], 'comp': 'product-row'},
        {'accepts': ['photo*'], 'comp': 'collage', 'optional': True},
        {'accepts': ['features', 'steps'], 'comp': 'story'},
        {'accepts': ['quote'], 'comp': 'quote-band', 'optional': True},
        {'accepts': ['facts'], 'comp': 'numbers', 'optional': True},
        {'accepts': ['faq'], 'comp': 'faq', 'optional': True},
    ]},
}
FALLBACK = {'features': 'cards', 'steps': 'two-col', 'cells': 'cards', 'facts': 'numbers', 'faq': 'faq', 'ledger': 'ledger', 'quote': 'statement', 'photo': 'photo', 'form': 'cta'}
BY_CLASS = {k: [i for i, r in RECIPES.items() if r['class'] == k] for k in ('software', 'place', 'service', 'product')}
