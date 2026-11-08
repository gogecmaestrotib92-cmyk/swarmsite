"""agents.py — the studio as a swarm. Each agent has ONE job, ONE tool, and may touch ONLY its own part of direction.json.
Reader → (Designer = lib/direct/direct.py) → UX → Copy → UI → Visual, then Critic routes defects back to the owner of each defect.
Every agent returns a small JSON patch; `apply_*` functions are the only code that writes direction.json, so a bad agent cannot wreck the document."""
import json, os, re, base64, io
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODEL = os.environ.get('DIRECT_MODEL', 'claude-sonnet-5-5')

def ask(system, content, tool, model=None, max_tokens=4000):
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(model=model or MODEL, max_tokens=max_tokens, system=system, messages=[{"role": "user", "content": content}], tools=[tool], tool_choice={"type": "auto"})
    call = next((b for b in msg.content if getattr(b, 'type', '') == 'tool_use'), None)
    if call is None:  # one nudge
        msg2 = client.messages.create(model=model or MODEL, max_tokens=max_tokens, system=system, messages=[{"role": "user", "content": content}, {"role": "assistant", "content": msg.content}, {"role": "user", "content": f"Call {tool['name']} now."}], tools=[tool], tool_choice={"type": "auto"})
        call = next((b for b in msg2.content if getattr(b, 'type', '') == 'tool_use'), None)
    return call.input if call else None

def img_block(path, media='image/jpeg'):
    return {"type": "image", "source": {"type": "base64", "media_type": media, "data": base64.b64encode(open(path, 'rb').read()).decode()}}

def J(slug_dir, n):
    p = os.path.join(slug_dir, n); return json.load(open(p)) if os.path.exists(p) else None
def W(slug_dir, n, obj): json.dump(obj, open(os.path.join(slug_dir, n), 'w'), indent=1, ensure_ascii=False)
def words(s): return len(re.sub(r'<[^>]+>', '', str(s or '')).split())
def by_id(d): return {b['id']: b for b in d.get('beats', [])}

# ───────────────────────────── READER ─────────────────────────────
READER_TOOL = {"name": "write_factsheet", "description": "The verified fact sheet of this website.", "input_schema": {"type": "object", "required": ["what", "language", "facts", "offers"], "properties": {
    "what": {"type": "string", "description": "one sentence: what this business/product is and for whom"},
    "language": {"type": "string"}, "tone": {"type": "string", "description": "3 adjectives for the site's own voice"},
    "facts": {"type": "array", "items": {"type": "string"}, "description": "hard facts with numbers/dates/places, verbatim from the site, max 12"},
    "offers": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "price": {"type": "string"}, "note": {"type": "string"}}}, "description": "every plan/item/service with its price if stated"},
    "quotes": {"type": "array", "items": {"type": "object", "properties": {"text": {"type": "string"}, "who": {"type": "string"}}}, "description": "real quoted sentences with an author, verbatim"},
    "capabilities": {"type": "array", "items": {"type": "string"}, "description": "what it does / offers, one line each, from the site's words, max 10"},
    "people": {"type": "array", "items": {"type": "string"}}, "contact": {"type": "array", "items": {"type": "string"}},
    "best_sentence": {"type": "string", "description": "the single sentence on the site that best says why someone should care"},
    "missing": {"type": "array", "items": {"type": "string"}, "description": "what a premium page would need that the site does not state"}}}}
READER_SYSTEM = "You are the studio's reader. You read a client's website and write the fact sheet the rest of the team works from. Only what the site SAYS, verbatim where it matters. No invention, no marketing gloss. If a number or claim is not on the site, it is not on the sheet."

def reader(slug_dir):
    inv = J(slug_dir, 'inventory.json') or {}
    content = [{"type": "text", "text": "INVENTORY\n" + json.dumps(inv, ensure_ascii=False)[:70000]}]
    for s in ('before-hero.jpg', 'before-full.jpg'):
        p = os.path.join(slug_dir, s)
        if os.path.exists(p) and os.path.getsize(p) < 4_500_000: content += [{"type": "text", "text": "SCREENSHOT " + s}, img_block(p)]
    content.append({"type": "text", "text": "Call write_factsheet."})
    fs_ = ask(READER_SYSTEM, content, READER_TOOL)
    if fs_: W(slug_dir, 'factsheet.json', fs_)
    return fs_

# ───────────────────────────── CONCEPT ─────────────────────────────
MOVES = {
    'sticky-product': 'text blocks scroll on the left while the product stays pinned on the right and swaps per block — for features/steps/cells with 2–6 items and at least one product visual',
    'pinned-sequence': 'the section pins and each step takes over the screen (giant number, one sentence, a visual) — for steps with 2–5 items',
    'type-wall': 'one statement in giant type whose words light up as you scroll — for a quote or a lede worth a whole screen',
    'marquee': 'a slow ticker of the section\'s own words (titles / figures / prices) — a breath between heavy screens; for cells/facts/features/ledger',
    'story': 'text beside one visual, sides alternating — for features/facts with a good picture',
    'cards': 'a plain grid — when nothing above fits',
}
CONCEPT_TOOL = {"name": "set_concept", "description": "The one idea of the page and the signature moves that carry it.", "input_schema": {"type": "object", "required": ["idea", "beats"], "properties": {
    "idea": {"type": "string", "description": "one sentence: the single idea the whole page performs (e.g. 'the page is one court; every section is a play drawn on it')"},
    "hero_move": {"type": "string", "enum": ["default", "split"], "description": "split = words left, product right full height (software with a product shot)"},
    "beats": {"type": "array", "items": {"type": "object", "required": ["id", "move"], "properties": {"id": {"type": "string"}, "move": {"type": "string", "enum": ["sticky-product", "pinned-sequence", "type-wall", "marquee", "story", "cards", "auto"]}, "why": {"type": "string"}}}},
    "rhythm": {"type": "string", "description": "how the page breathes: which screens are loud, which are quiet"}}}}
CONCEPT_SYSTEM = """You are the creative director choosing the ONE idea of the page and the moves that perform it. You know the signature moves of award-winning sites:
""" + "\n".join(f"- {k}: {v}" for k, v in MOVES.items()) + """
Rules: at most ONE pinned move (sticky-product or pinned-sequence) and at most ONE type-wall per page; never two loud moves back to back — put a marquee or a quiet cards grid between them; a move needs the content it asks for (sticky needs ≥2 items and a visual; type-wall needs a sentence worth it). The first beat after the hero should be the strongest proof of the product. Write the idea in the client's language, in one sentence a designer could pin on the wall."""

def concept(slug_dir, notes=''):
    d = J(slug_dir, 'direction.json'); fs_ = J(slug_dir, 'factsheet.json') or {}
    imgs = [{k: v for k, v in i.items() if k != 'data'} for i in (J(slug_dir, 'images.json') or [])]
    distinct = len([i for i in imgs if not i.get('crop_of')])
    beats = [{'id': b['id'], 'type': b['type'], 'h2': b.get('h2'), 'n_items': len(b.get('features') or b.get('cells') or b.get('steps') or b.get('facts') or b.get('items') or []), 'has_image': bool(b.get('image'))} for b in d['beats']]
    content = [{"type": "text", "text": f"LANGUAGE OF THE SITE (write the idea in it): {fs_.get('language') or d.get('lang') or 'en'}\nKIND: {d.get('kind')} · BLUEPRINT: {d.get('blueprint')} · MODE: {d.get('mode')}\nWHAT: {fs_.get('what', '')}\nBEST SENTENCE: {fs_.get('best_sentence', '')}\nHERO: {json.dumps({k: d['hero'].get(k) for k in ('h1', 'lede', 'media')}, ensure_ascii=False)}\nBEATS: {json.dumps(beats, ensure_ascii=False)}\nDISTINCT VISUALS: {distinct} (ids: {[i['id'] for i in imgs][:16]})\nCRITIC NOTES: {notes or 'none'}\nCall set_concept."}]
    r = ask(CONCEPT_SYSTEM, content, CONCEPT_TOOL)
    return apply_concept(slug_dir, r) if r else 0

def apply_concept(slug_dir, r):
    d = J(slug_dir, 'direction.json'); ids = by_id(d); n = 0; pinned = 0; wall = 0
    if r.get('idea'): d.setdefault('swarm', {})['idea'] = r['idea'][:200]; n += 1
    if r.get('hero_move') == 'split' and d['hero'].get('media'): d['hero'].setdefault('ui', {})['move'] = 'split'; n += 1
    elif r.get('hero_move') == 'default': d['hero'].setdefault('ui', {}).pop('move', None)
    for u in r.get('beats', []):
        b = ids.get(u.get('id')); mv = u.get('move')
        if not b or mv not in MOVES and mv != 'auto': continue
        if mv in ('sticky-product', 'pinned-sequence'):
            if pinned: mv = 'cards'
            pinned += 1
        if mv == 'type-wall':
            txt = b.get('body') if b['type'] == 'quote' else (b.get('lede') or '')
            if wall or b['type'] in ('photo', 'form', 'ledger') or words(txt) < 8: mv = 'auto'
            else: wall += 1
        b.setdefault('ui', {})['move'] = mv; n += 1
    d.setdefault('swarm', {})['rhythm'] = (r.get('rhythm') or '')[:200]
    W(slug_dir, 'direction.json', d); return n

# ───────────────────────────── UX ─────────────────────────────
UX_TOOL = {"name": "set_flow", "description": "Set the page flow: beat order, goal action, nav.", "input_schema": {"type": "object", "required": ["order", "goal_cta"], "properties": {
    "order": {"type": "array", "items": {"type": "string"}, "description": "beat ids in the order the reader should meet them (every existing id exactly once; you may omit at most one weak beat to drop it)"},
    "goal_cta": {"type": "string", "description": "verb + what you get, ≤4 words; used in hero, nav and ending"},
    "cta2": {"type": "string", "description": "secondary action or ''"},
    "nav": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}, "description": "≤4 [#beat-id, Label]"},
    "reasons": {"type": "array", "items": {"type": "string"}}}}}
UX_SYSTEM = """You are the UX lead. One page, one goal. Order the beats so the story is: what it is (hero) → proof it works / what you get → how it works → what it costs → objections (faq) → act (form/cta).
A place or restaurant: photo → quote/proof → ledger (menu/prices) → facts → form. Software: features → steps → pricing ledger → faq → cta. Never put the form before the proof. Drop a beat only if it repeats another one.
Every CTA on the page must say the same verb+object. Nav has ≤4 links to beats that exist."""

def ux(slug_dir, notes=''):
    d = J(slug_dir, 'direction.json'); fs_ = J(slug_dir, 'factsheet.json') or {}
    beats = [{k: v for k, v in b.items() if k in ('id', 'type', 'h2', 'label')} for b in d['beats']]
    content = [{"type": "text", "text": f"KIND: {d.get('kind')}\nFACT SHEET: {json.dumps(fs_, ensure_ascii=False)[:4000]}\nHERO: {json.dumps(d['hero'], ensure_ascii=False)}\nBEATS: {json.dumps(beats, ensure_ascii=False)}\nOWNER GOAL: {(J(slug_dir, 'brief.json') or {}).get('goal', '')}\nCRITIC NOTES FOR UX: {notes or 'none'}\nCall set_flow."}]
    r = ask(UX_SYSTEM, content, UX_TOOL)
    return apply_ux(slug_dir, r) if r else 0

def apply_ux(slug_dir, r):
    d = J(slug_dir, 'direction.json'); ids = by_id(d); changed = 0
    order = [i for i in r.get('order', []) if i in ids]
    if order and len(set(order)) >= max(3, len(ids) - 1) and len(set(order)) == len(order):
        d['beats'] = [ids[i] for i in order]; changed += 1
    g = r.get('goal_cta')
    if g and 1 <= words(g) <= 5:
        d['hero']['cta'] = g; d.setdefault('nav', {})['cta'] = g
        for b in d['beats']:
            if b['type'] in ('form', 'ledger'): b['cta'] = g
        changed += 1
    if r.get('cta2') is not None and words(r.get('cta2')) <= 5: d['hero']['cta2'] = r['cta2']
    nav = [x for x in r.get('nav', []) if isinstance(x, list) and len(x) == 2 and x[0].lstrip('#') in ids][:4]
    if nav: d.setdefault('nav', {})['links'] = nav; changed += 1
    d.setdefault('swarm', {})['ux'] = r.get('reasons', [])[:3]
    W(slug_dir, 'direction.json', d); return changed

# ───────────────────────────── COPY ─────────────────────────────
COPY_TOOL = {"name": "rewrite", "description": "Rewrite text fields. Only fields listed; only words from the fact sheet/site.", "input_schema": {"type": "object", "required": ["edits"], "properties": {
    "edits": {"type": "array", "maxItems": 24, "items": {"type": "object", "required": ["path", "value"], "properties": {
        "path": {"type": "string", "description": "hero.h1 | hero.lede | hero.category | hero.fact | <beat-id>.h2 | <beat-id>.lede | <beat-id>.label | <beat-id>.steps[i] | <beat-id>.features[i].title | <beat-id>.features[i].body | <beat-id>.items[i][0] | <beat-id>.items[i][1] | ending.tag"},
        "value": {"type": "string"}, "why": {"type": "string"}}}}}}}
LIMITS = {'h1': 6, 'lede': 30, 'category': 8, 'fact': 8, 'h2': 5, 'label': 4, 'step': 12, 'ftitle': 4, 'fbody': 18, 'tag': 12, 'item': 6}
COPY_SYSTEM = f"""You are the copywriter. Limits are hard: h1 ≤ {LIMITS['h1']} words with a stance (one word may be in <em>), lede ≤ {LIMITS['lede']}, h2 ≤ {LIMITS['h2']} words and a NOUN phrase, step ≤ {LIMITS['step']}, feature title ≤ {LIMITS['ftitle']}, feature body ≤ {LIMITS['fbody']}, label ≤ {LIMITS['label']}.
Write in the site's language and voice. Every fact, number and name must be on the fact sheet. Cut adjectives, keep nouns and verbs. Buttons = verb + object. Never repeat the h2 inside the lede. Never two sections saying the same idea.
Fix exactly what is asked (critic notes) plus any field over its limit. Leave good text alone."""

def copy(slug_dir, notes=''):
    d = J(slug_dir, 'direction.json'); fs_ = J(slug_dir, 'factsheet.json') or {}
    over = []
    if words(d['hero'].get('h1')) > LIMITS['h1']: over.append('hero.h1')
    if words(d['hero'].get('lede')) > LIMITS['lede']: over.append('hero.lede')
    for b in d['beats']:
        if words(b.get('h2')) > LIMITS['h2']: over.append(f"{b['id']}.h2")
        for i, s in enumerate(b.get('steps', []) or []):
            if words(s) > LIMITS['step']: over.append(f"{b['id']}.steps[{i}]")
        for i, f in enumerate(b.get('features', []) or []):
            if words(f.get('body')) > LIMITS['fbody']: over.append(f"{b['id']}.features[{i}].body")
            if words(f.get('title')) > LIMITS['ftitle']: over.append(f"{b['id']}.features[{i}].title")
    if not over and not notes: return 0
    doc = {'hero': d['hero'], 'beats': d['beats'], 'ending': {'tag': d.get('ending', {}).get('tag')}}
    content = [{"type": "text", "text": f"FACT SHEET\n{json.dumps(fs_, ensure_ascii=False)[:6000]}\n\nCURRENT COPY\n{json.dumps(doc, ensure_ascii=False)[:14000]}\n\nOVER LIMIT: {over or 'none'}\nCRITIC NOTES FOR COPY: {notes or 'none'}\nCall rewrite."}]
    r = ask(COPY_SYSTEM, content, COPY_TOOL)
    return apply_copy(slug_dir, r) if r else 0

def apply_copy(slug_dir, r):
    d = J(slug_dir, 'direction.json'); ids = by_id(d); n = 0
    for ed in r.get('edits', []):
        p, v = ed.get('path', ''), ed.get('value')
        if not isinstance(v, str) or not v.strip(): continue
        m = re.match(r'^(hero|ending|[\w-]+)\.(\w+)(?:\[(\d+)\])?(?:\.(\w+)|\[(\d+)\])?$', p)
        if not m: continue
        root, f, i, sub, j = m.groups(); i = int(i) if i else None; j = int(j) if j else None
        tgt = d['hero'] if root == 'hero' else d.setdefault('ending', {}) if root == 'ending' else ids.get(root)
        if tgt is None: continue
        lim = LIMITS.get(f, LIMITS['lede']) if f not in ('steps', 'features', 'items') else None
        try:
            if f == 'steps' and i is not None and words(v) <= LIMITS['step']: tgt['steps'][i] = v; n += 1
            elif f == 'features' and i is not None and sub in ('title', 'body') and words(v) <= LIMITS['ftitle' if sub == 'title' else 'fbody']: tgt['features'][i][sub] = v; n += 1
            elif f == 'items' and i is not None and j in (0, 1) and words(v) <= LIMITS['item']: tgt['items'][i][j] = v; n += 1
            elif lim and f in ('h1', 'lede', 'category', 'fact', 'h2', 'label', 'tag', 'big', 'body', 'cta', 'cta2') and words(v) <= (lim if f != 'body' else 60):
                if f in ('cta', 'cta2') and words(v) > 5: continue
                tgt[f] = v; n += 1
        except (IndexError, KeyError, TypeError): pass
    W(slug_dir, 'direction.json', d); return n

# ───────────────────────────── UI ─────────────────────────────
UI_TOOL = {"name": "set_layout", "description": "Per-beat layout decisions the renderer honours.", "input_schema": {"type": "object", "required": ["beats"], "properties": {
    "hero": {"type": "object", "properties": {"size": {"type": "string", "enum": ["S", "M", "L"]}, "align": {"type": "string", "enum": ["start", "center"]}}},
    "beats": {"type": "array", "items": {"type": "object", "required": ["id"], "properties": {
        "id": {"type": "string"}, "cols": {"type": "integer", "minimum": 1, "maximum": 4}, "band": {"type": "string", "enum": ["paper", "dark", "alt"]},
        "lead": {"type": "string", "description": "image id to show as a full-width visual above the grid, or '' for none"},
        "compact": {"type": "boolean", "description": "tighter padding, no min-height"}, "h2_px": {"type": "integer", "minimum": 28, "maximum": 96},
        "head": {"type": "string", "enum": ["left", "center", "split"], "description": "split = eyebrow+h2 left, lede right"}}}},
    "reasons": {"type": "array", "items": {"type": "string"}}}}}
UI_SYSTEM = """You are the UI designer. The concept has already assigned each section a MOVE (ui.move) — do not fight it: a sticky-product or story section needs no lead visual (set lead ''), a marquee needs no columns. The renderer is fixed; you decide per section: number of columns (match the item count: 3 or 6 items → 3 cols, 4 → 4, 2 → 2, 5 → 3), band (alternate paper/dark so no two dark bands touch and the page is not all cream), a lead visual (a section screenshot id for a software how-it-works, a photo for people/places; '' when the grid has its own images), compact when a section has little content, h2 size when a heading wraps to 3+ lines (smaller) or a statement needs presence (bigger), head alignment.
Hero size: L for ≤4 words, M for 5–6, S for 7+. Think in screens: no screen should be more than 40% empty, none should hold two ideas."""

def ui(slug_dir, notes=''):
    d = J(slug_dir, 'direction.json'); imgs = [{k: v for k, v in i.items() if k != 'data'} for i in (J(slug_dir, 'images.json') or [])]
    beats = [{k: v for k, v in b.items() if k != 'image' or True} for b in d['beats']]
    summary = [{'id': b['id'], 'type': b['type'], 'h2': b.get('h2'), 'n_items': len(b.get('features') or b.get('cells') or b.get('steps') or b.get('facts') or b.get('items') or []), 'image': b.get('image', ''), 'band': b.get('band', ''), 'ui': b.get('ui', {})} for b in beats]
    content = [{"type": "text", "text": f"KIND: {d.get('kind')} · MODE: {d.get('mode')} · BLUEPRINT: {d.get('blueprint')}\nHERO h1: {d['hero'].get('h1')} ({words(d['hero'].get('h1'))} words)\nBEATS: {json.dumps(summary, ensure_ascii=False)}\nIMAGES: {json.dumps(imgs, ensure_ascii=False)[:3000]}\nCRITIC NOTES FOR UI: {notes or 'none'}\nCall set_layout."}]
    r = ask(UI_SYSTEM, content, UI_TOOL)
    return apply_ui(slug_dir, r) if r else 0

def apply_ui(slug_dir, r):
    d = J(slug_dir, 'direction.json'); ids = by_id(d); n = 0; img_ids = {i.get('id') for i in (J(slug_dir, 'images.json') or [])}
    if r.get('hero'): d['hero']['ui'] = {k: v for k, v in r['hero'].items() if k in ('size', 'align')}; n += 1
    for u in r.get('beats', []):
        b = ids.get(u.get('id'))
        if not b: continue
        uu = b.setdefault('ui', {})
        for k in ('cols', 'compact', 'h2_px', 'head'):
            if k in u and u[k] is not None: uu[k] = u[k]; n += 1
        if u.get('band') in ('paper', 'dark', 'alt'): b['band'] = u['band']; n += 1
        if 'lead' in u: uu['lead'] = u['lead'] if u['lead'] in img_ids else ''; n += 1
    d.setdefault('swarm', {})['ui'] = r.get('reasons', [])[:3]
    W(slug_dir, 'direction.json', d); return n

# ───────────────────────────── VISUAL ─────────────────────────────
VISUAL_TOOL = {"name": "set_visuals", "description": "Assign images to slots and crop section screenshots to their subject.", "input_schema": {"type": "object", "required": ["hero"], "properties": {
    "hero": {"type": "string", "description": "image id for the hero (software: the fullest product screenshot; place/service: the best landscape photo of the thing itself)"},
    "slots": {"type": "array", "items": {"type": "object", "required": ["beat", "image"], "properties": {"beat": {"type": "string"}, "image": {"type": "string"}}}},
    "crops": {"type": "array", "maxItems": 6, "items": {"type": "object", "required": ["image", "box"], "properties": {"image": {"type": "string"}, "box": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4, "description": "[x,y,w,h] as fractions 0–1 of the source; the subject only, no page chrome, no nav, no text columns"}, "as": {"type": "string", "description": "new id, e.g. shot3-play"}}}},
    "need": {"type": "array", "items": {"type": "string"}, "description": "visuals the page needs but the site does not have (one line each) — e.g. 'founders portrait', 'the play diagram at 1600px'"},
    "generate": {"type": "array", "maxItems": 3, "items": {"type": "object", "required": ["beat", "prompt", "ar"], "properties": {"beat": {"type": "string", "description": "beat id, or 'hero'"}, "prompt": {"type": "string", "description": "art-director prompt for an ORIGINAL visual: subject (an object, material, scene or abstract form that stands for the section's idea), medium (3D render / illustration / macro photo / paper-cut / ink), light, palette with hex codes, composition, 'no text, no letters, no logos, no user interface, no faces'"}, "ar": {"type": "string", "enum": ["16:9", "4:3", "1:1", "3:4", "3:2"]}, "as": {"type": "string"}}}, "description": "ONLY when GENERATION is enabled and fewer than 3 distinct real visuals exist: commission up to 3 originals"},
    "reasons": {"type": "array", "items": {"type": "string"}}}}}
VISUAL_SYSTEM = """You are the visual editor. When the site has fewer than 3 distinct visuals, do what a studio does with one product screenshot: cut it into DETAIL crops (each ≤ 40% of the source, one feature per crop — the court diagram, the sidebar library, the details panel, a toolbar) and give each features/steps slot its own detail. Details may come from the same screenshot; whole-image repeats may not. You look at every image the site has (thumbnails attached, with ids) and decide what goes where. Rules: never a logo, icon or text block as a photo; never the same image twice; a UI screenshot is shown FRAMED (hero of a software product, or a lead above a grid) never stretched as a background; crop screenshots to the actual product surface (drop the browser chrome, sidebars, headers, surrounding whitespace). People sections get people. If nothing fits a slot, leave it empty and list it under need.
When the prompt says GENERATION: enabled, you may also COMMISSION up to 3 original visuals like a studio commissions illustration: a 3D object, a material study, an abstract composition or a macro photo in the brand's palette that stands for a section's idea (a basketball court as clean line-art in brand orange on dark; a stack of printed sheets; a whistle on a bench). Never a fake product interface, never screenshots, never text or logos, never recognisable faces. Give each a beat (or 'hero' only if the site has no product image at all)."""

def _photo(i):  # a real visual is a photograph-like raster: not a page screenshot, not a banner strip or logo, not a crop, not vector art
    if i.get('crop_of') or i.get('gen') or i.get('shot') or i.get('w', 0) < 600: return False
    if 'svg' in str(i.get('data', ''))[:30]: return False
    ar = i.get('w', 1) / max(1, i.get('h', 1)); return .5 <= ar <= 2.2

def visual(slug_dir, notes=''):
    from PIL import Image
    d = J(slug_dir, 'direction.json'); imgs = J(slug_dir, 'images.json') or []
    import gen as G
    distinct = len([i for i in imgs if _photo(i)]); have_gen = len([i for i in imgs if i.get('gen')])
    gen_rule = 'disabled' if not G.enabled() else (f'enabled — the site has only {distinct} distinct real visual(s) and {have_gen} commissioned so far: you MUST commission {max(0, 3 - have_gen)} originals now, one per section that lacks its own picture (never the hero)' if distinct < 3 and have_gen < 3 else 'enabled (optional, the site has enough visuals)')
    content = [{"type": "text", "text": f"GENERATION: {gen_rule}\nBRAND: {json.dumps({k: d.get('brand', {}).get(k) for k in ('name', 'accent', 'paper', 'ink')})} mode={d.get('mode')}\nKIND: {d.get('kind')}\nHERO: {json.dumps({k: d['hero'].get(k) for k in ('h1', 'media')}, ensure_ascii=False)}\nBEATS: {json.dumps([{'id': b['id'], 'type': b['type'], 'h2': b.get('h2'), 'image': b.get('image', ''), 'lead': (b.get('ui') or {}).get('lead', '')} for b in d['beats']], ensure_ascii=False)}\nCRITIC NOTES FOR VISUAL: {notes or 'none'}\nIMAGES (thumbnails follow, in this order):"}]
    for it in imgs[:18]:
        if not it.get('data'): continue
        try:
            raw = base64.b64decode(it['data'].split(',', 1)[1]); im = Image.open(io.BytesIO(raw)).convert('RGB'); im.thumbnail((640, 640)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=70)
            content += [{"type": "text", "text": f"id={it.get('id')} {it.get('w')}×{it.get('h')}{' section-shot' if it.get('shot') else ''}{' hero-grade' if it.get('heroGrade') else ''}"}, {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}]
        except Exception: continue
    content.append({"type": "text", "text": "Call set_visuals."})
    r = ask(VISUAL_SYSTEM, content, VISUAL_TOOL, max_tokens=2500)
    return apply_visual(slug_dir, r) if r else 0

def apply_visual(slug_dir, r):
    from PIL import Image
    d = J(slug_dir, 'direction.json'); imgs = J(slug_dir, 'images.json') or []; by = {i.get('id'): i for i in imgs}; n = 0
    for c in r.get('crops', []) or []:
        src = by.get(c.get('image')); box = c.get('box') or []
        if not src or len(box) != 4: continue
        x, y, w, h = [max(0, min(1, float(v))) for v in box]
        if w < .18 or h < .15: continue
        try:
            raw = base64.b64decode(src['data'].split(',', 1)[1]); im = Image.open(io.BytesIO(raw)).convert('RGB'); W_, H_ = im.size
            cr = im.crop((int(x * W_), int(y * H_), int(min(W_, (x + w) * W_)), int(min(H_, (y + h) * H_))))
            if cr.size[0] < 360: continue
            buf = io.BytesIO(); cr.save(buf, 'JPEG', quality=84); nid = re.sub(r'[^\w-]', '', c.get('as') or (src['id'] + '-crop'))
            new = {**{k: v for k, v in src.items() if k not in ('data',)}, 'id': nid, 'w': cr.size[0], 'h': cr.size[1], 'data': 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode(), 'crop_of': src['id'], 'crop_area': round(w * h, 2), 'detail': (w * h) <= .42}
            if nid in by: imgs[[i.get('id') for i in imgs].index(nid)] = new
            else: imgs.append(new)
            by[nid] = new; n += 1
        except Exception: continue
    if r.get('hero') in by: d['hero']['media'] = r['hero']; n += 1
    ids = by_id(d); seen = {d['hero'].get('media')}
    for s in r.get('slots', []) or []:
        b = ids.get(s.get('beat')); im = s.get('image')
        if b and im in by and im not in seen: b['image'] = im; seen.add(im); n += 1
    # commissioned originals
    import gen as G
    gens = []
    if G.enabled():
        from concurrent.futures import ThreadPoolExecutor
        have_gen = len([i for i in imgs if i.get('gen')])
        asks = [g for g in (r.get('generate') or [])[:max(0, 3 - have_gen)] if g.get('prompt') and g.get('beat')]
        distinct = len([i for i in imgs if _photo(i)])
        if distinct < 3 and have_gen < 3 and not asks:  # the rule is mandatory: when the model only lists needs, the needs become the commissions
            holes = [b for b in d.get('beats', []) if b.get('type') not in ('form', 'faq', 'ledger') and not b.get('image')][:3 - have_gen]
            for b, need in zip(holes, (r.get('need') or []) + [f"{d.get('brand', {}).get('name', '')} — {b.get('h2') or b.get('big') or ''}" for b in holes]):
                asks.append({'beat': b['id'], 'prompt': f"Editorial photograph for a {d.get('kind')} website: {need}. Natural light, real place, restrained palette, no people.", 'ar': '16:9', 'as': f"gen-{b['id']}"})
        def one(g):
            try:
                pr = g['prompt'] + ' No text, no letters, no logos, no user interface, no watermark, no faces.'
                data = G.generate(pr, g.get('ar', '16:9')); im = Image.open(io.BytesIO(data)).convert('RGB'); im.thumbnail((1600, 1600)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=86)
                return {'id': re.sub(r'[^\w-]', '', g.get('as') or f"gen-{g['beat']}"), 'src': 'commissioned', 'w': im.size[0], 'h': im.size[1], 'alt': g['prompt'][:80], 'ratio': round(im.size[0] / im.size[1], 2), 'heroGrade': im.size[0] >= 1200, 'gen': True, 'data': 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()}, g['beat']
            except Exception as e: return {'error': str(e)[:120]}, g['beat']
        if asks:
            with ThreadPoolExecutor(max_workers=3) as ex: gens = list(ex.map(one, asks))
        for it, beat in gens:
            if it.get('error'): continue
            if it['id'] in by: imgs[[i.get('id') for i in imgs].index(it['id'])] = it
            else: imgs.append(it)
            by[it['id']] = it
            if beat == 'hero': d['hero']['media'] = it['id']
            elif beat in ids: ids[beat]['image'] = it['id']; ids[beat].setdefault('ui', {})['lead'] = it['id']
            n += 1
    d.setdefault('swarm', {})['visual'] = {'need': r.get('need', [])[:4], 'reasons': r.get('reasons', [])[:3], 'generated': [it['id'] for it, _ in gens if not it.get('error')], 'gen_errors': [it['error'] for it, _ in gens if it.get('error')]}
    W(slug_dir, 'images.json', imgs); W(slug_dir, 'direction.json', d); return n
