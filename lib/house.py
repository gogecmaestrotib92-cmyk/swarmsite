"""house.py — the house structures: what a good landing page is, per kind of business.

The site supplies facts, words and pictures. We supply the architecture: a fixed order of slots with a fixed move
each, the way a studio has a way of building a page. The director fills the slots — from the source section that
matches, or, when the source has no such section, from the factsheet's verified facts. A slot is skipped only
when no facts can carry it. The renderer then locks order and moves, so two runs of one site differ in copy and
pictures, never in architecture. Everything here is deterministic.
"""

# slot: id prefix, beat type, the move the renderer gets, what fills it, whether the director may compose it from facts
# Evidence: dna/house/{software,place,service,product}.md — 6–8 awarded or reference landings per kind, section by section.
HOUSE = {
    # 7/7 hero with the product; proof right after the hero; features are the body, ordered as the workflow, one crop each;
    # social proof after features on 6/7; FAQ rare (2/7), exactly 5 questions, right before the CTA; figures never stand alone
    'software': [
        ('proof', 'photo', 'story', 'the product in use beside one result line (a before/after pair only when the source has an original and a result; a code snippet for a dev tool)', True),
        ('features', 'features', 'pinned-sequence', 'three to six capabilities in the order a user meets them (intake → plan → ship), title 2–4 words, one sentence, each with its own product crop when there is one; steps only when the source itself names steps', True),
        ('trust', 'testimonials', None, 'one to three real customer quotes with names; when the source has none, real figures or badges (customers, uptime, compliance) as cells', False),
        ('figures', 'cells', 'marquee', 'only when there are no quotes: three to six real figures (customers, speed, limits, price) — value, label, one-line detail', True),
        ('faq', 'faq', 'cards', 'up to five questions a buyer asks before signing up, in the site\'s own words; skip under three real questions', True),
    ],
    # 7/7 full-bleed photo hero with the booking action; one photo + one sentence per screen; the offer is cards with a photo
    # (prices only when short, 1/7 prints them); badges not quotes; events / private dining / gift card on 4–5 of 7; booking
    # is the provider's widget or link beside hours and address — never a custom form
    'place': [
        ('story', 'photo', 'story', 'the place itself: its best photograph beside the one sentence that says what it is and for whom', True),
        ('offer', 'ledger', None, 'the menu, rooms or treatments as three to six items, each with its photo when there is one; prices only when the list is six lines or fewer, otherwise the link to their menu', False),
        ('whats-on', 'features', 'cards', 'two to four tiles for events, private dining, gift cards, news — only what the source offers', False),
        ('proof', 'cells', 'marquee', 'credentials as short facts: guide mentions, awards, since when, seats, a reviews link — real only', True),
        ('gallery', 'photo', 'photo:gallery', 'three to six more photographs of the place, no captions needed', False),
        ('faq', 'faq', 'cards', 'two to four practical terms guests ask about (hours, children, parking, cards) from the site', True),
        ('book', 'form', None, 'the reservation action: their booking provider\'s link or widget with hours, address and phone beside it', True),
    ],
    # 5/8 typographic heroes; agencies show work before services, clinics and firms lead with services; 7/8 have a people/about
    # block; 0/8 show a stats row or a testimonial; logos/credentials on 4/8; contact is a CTA with channels, a form only when the source has one
    'service': [
        ('work', 'photo', 'story', 'proof of work: project or result photographs beside a one-line caption (agencies lead with this; a practice without work images skips it and leads with services)', False),
        ('services', 'features', 'cards', 'what they do: three to six services, title and one sentence; when the services are stages, order them as the process instead of a separate steps beat', True),
        ('people', 'photo', 'story', 'the people or the office: one real photograph beside a short paragraph about who they are', True),
        ('credentials', 'cells', 'marquee', 'clients, awards, certifications, memberships, years — short real facts; the only place for numbers', True),
        ('faq', 'faq', 'cards', 'the questions a prospect asks before calling, answered from the site; skip under three', True),
        ('contact', 'form', None, 'the contact action: their form when the source has one, otherwise the direct channels (email, phone, booking link)', True),
    ],
    # 8/8 hero with the buy action and a shipping micro-line; story right after; features carry the numbers; the product is
    # re-shown 4–20 times; price lives on cards, never in a section; 3 quotes or press, never one; a trust strip (delivery,
    # returns, warranty) on 6/8; FAQ never inline; newsletter on 7/8
    'product': [
        ('story', 'photo', 'story', 'the product in use: one lifestyle photograph beside one sentence of what it is', True),
        ('features', 'features', 'cards', 'what it does or what it is made of, three to six, the numbers inside the titles (40 h battery, 100 % wool), each with its detail photo when there is one', True),
        ('gallery', 'photo', 'photo:gallery', 'three to six product photographs with short captions (studio for hardware, lifestyle for apparel and wellness)', False),
        ('offer', 'ledger', None, 'variants or bundles as cards with their price and the buy action; a single product shows shipping time and returns instead of a price list', False),
        ('voice', 'testimonials', None, 'three real customer quotes with names, or press mentions; never a single quote', False),
        ('trust', 'cells', 'marquee', 'the trust strip: delivery time, returns, warranty, payments, certifications — real terms only', True),
    ],
}

HERO = {
    'software': 'their claim (h1 ≤ 6 words), one category line, one real fact, the primary action with its source URL, the product itself (the wide screenshot or the result it makes) framed beside the words',
    'place': 'one full-bleed photograph of the place, one line, the booking action with its real destination in the hero and in the nav',
    'service': 'a typographic hero: the claim in large type, one line of who they are for, the primary action; a single proof token (award, years) when real; a photograph only for a practice people visit',
    'product': 'the product photograph or video, the claim, the buy action with its real destination and a one-line shipping or stock note when the source states one',
}
TYPE_ORDER = {kind: [t for _, t, _, _, _ in slots] for kind, slots in HOUSE.items()}


def describe(kind):
    """The block the director reads: the architecture is given, the director fills it."""
    slots = HOUSE.get(kind) or HOUSE['service']
    lines = [f'HOUSE STRUCTURE for a {kind} site — this is the page. Fill these slots in this order; do not add other beats and do not reorder them:',
             '0. hero — ' + HERO.get(kind, HERO['service'])]
    for i, (sid, typ, move, what, compose) in enumerate(slots, 1):
        lines.append(f'{i}. {sid} (type "{typ}") — {what}.' + (' If the source has no such section, COMPOSE it from the factsheet facts only.' if compose else ' Only from the source; skip when the source has none.') )
    lines.append('The page always closes with the CTA band (headline echoing the hero, one or two actions) and the footer; those are not beats.')
    lines.append('A slot is skipped only when neither the source nor the factsheet can fill it truthfully. Never pad: three true items beat six thin ones. Pricing is never a homepage section for software.')
    lines.append('SEO-safe mode keeps the source headings, words and links inside these slots; free mode writes them in the house voice.')
    return '\n'.join(lines)


def lock(doc):
    """After the director: order the beats by the house order for the kind and set each slot's move.
    Beats of a type the house does not know keep their place after the known ones (a 'facts' beat, say)."""
    kind = doc.get('kind') or 'service'
    slots = HOUSE.get(kind) or HOUSE['service']
    positions = {}
    for i, (_, t, _, _, _) in enumerate(slots): positions.setdefault(t, []).append(i)
    beats = doc.get('beats') or []
    seen = {}
    def key(b):
        # the n-th beat of a type takes the n-th slot of that type (place: story, then gallery); extras follow the last
        t = b.get('type'); n = seen.get(t, 0); seen[t] = n + 1
        pos = positions.get(t)
        return (pos[min(n, len(pos) - 1)] if pos else len(slots), n)
    beats = sorted(beats, key=key)
    if kind == 'service' and len(beats) >= 2 and beats[0].get('type') == 'photo' and not beats[0].get('image') and beats[1].get('type') == 'features':
        beats[0], beats[1] = beats[1], beats[0]  # a practice without work photographs leads with its services
    seen2 = {}
    for b in beats:
        t = b.get('type'); n = seen2.get(t, 0); seen2[t] = n + 1
        # the n-th beat of a type takes the n-th slot of that type (place: story, then gallery)
        slot_moves = [m for _, tt, m, _, _ in slots if tt == t]
        m = slot_moves[n] if n < len(slot_moves) else (slot_moves[-1] if slot_moves else None)
        if m is None: continue
        ui = dict(b.get('ui') or {})
        if m.startswith('photo:'): ui['photo_layout'] = m.split(':', 1)[1]; ui['move'] = 'default'
        else: ui['move'] = m
        b['ui'] = ui
    doc['beats'] = beats
    doc['house'] = kind
    return doc


def violations(doc):
    """What the director must fix before the house accepts the document: beats of a type the house has no slot for,
    or more beats of a type than the house has slots (five menu ledgers in a row, three photo stories, a pricing
    ledger on a software page). The message tells the director where that content belongs instead."""
    kind = doc.get('kind') or 'service'
    slots = HOUSE.get(kind) or HOUSE['service']
    allowed = {}
    for sid, t, _, _, _ in slots: allowed.setdefault(t, []).append(sid)
    counts = {}
    for b in doc.get('beats') or []: counts[b.get('type')] = counts.get(b.get('type'), 0) + 1
    errs = []
    nearest = {'quote': 'testimonials', 'facts': 'cells', 'steps': 'features (order the features as the steps)', 'ledger': 'features (software has no pricing section; put plan names into features or drop)'}
    for t, n in counts.items():
        if t not in allowed:
            hint = nearest.get(t, 'the closest house slot')
            errs.append(f'{kind} house has no "{t}" slot — rewrite that content as {hint} or drop it')
        elif n > len(allowed[t]):
            errs.append(f'{kind} house has {len(allowed[t])} "{t}" slot(s) ({", ".join(allowed[t])}) but the document has {n}: merge them into one beat of 3–6 items (a menu is one offer beat with its best 6 lines and the link to the full menu)')
    return errs
