"""validate.py — is this hero composition one the renderer may draw?

A composition is a small document that says where the hero's own content sits on a 12-column grid. It is written by a
person or a model and it is not trusted: everything is checked here before a pixel is drawn, and a composition that
fails is refused whole — the page keeps its production hero. Nothing is repaired silently.

What a composition can do: place each piece of content on the grid, size the headline, set a measure, let a picture
bleed or sit under the headline, choose the surface and the height, order the pieces for a phone.
What it cannot do: contain text, link anywhere, leave content out, stack text on text, put text on a picture without
a plate or a scrim, stretch a picture past its pixels, or use a field this file does not list.

  validate(ir, content) → [{'code', 'at', 'message'}]      ([] = may be drawn)
Codes are stable; tests seed one defect per code. Deterministic, no network, no model."""

VERSION = '0.1'
COLS = 12
SURFACES = ('paper', 'dark', 'alt', 'accent')
HEIGHTS = ('auto', 'screen', 'tall')
ROW_SIZES = ('auto', '1fr', '2fr', 'min')
GAPS = ('sm', 'md', 'lg')
H1_SIZES = ('xl', 'xxl', 'mega')
LEDE_SIZES = ('md', 'lg')
ROLES = ('label', 'h1', 'lede')
FITS = ('cover', 'contain')
RATIOS = ('1/1', '4/5', '3/4', '2/3', '4/3', '3/2', '16/9', '16/10', '21/9')
BLEEDS = ('none', 'left', 'right')
FRAMES = ('none', 'browser', 'paper')
PLATES = ('paper', 'ink')
SELF = ('start', 'center', 'end', 'stretch')
ALIGN = ('start', 'center', 'end')
ENTER = ('none', 'rise')
UPSCALE = 1.35   # a photograph may be shown up to this much past its pixels (the renderer's own limit); a screenshot not at all

KEYS = {
    'text': {'id', 't', 'src', 'as', 'size', 'measure', 'align', 'plate', 'at'},
    'actions': {'id', 't', 'src', 'align', 'at'},
    'media': {'id', 't', 'src', 'fit', 'ratio', 'focal', 'bleed', 'frame', 'scrim', 'at'},
    'shape': {'id', 't', 'kind', 'at'},
}
HERO_KEYS = {'surface', 'height', 'rows', 'gap', 'nodes', 'sm', 'enter'}


def area(node, rows):
    """(col0, col1, row0, row1) as half-open grid lines, or None when the placement is not well formed."""
    at = node.get('at')
    if not isinstance(at, dict): return None
    col, row = at.get('col'), at.get('row')
    if not (isinstance(col, list) and len(col) == 2 and all(isinstance(v, int) and not isinstance(v, bool) for v in col)): return None
    if isinstance(row, int) and not isinstance(row, bool): row = [row, row + 1]
    if not (isinstance(row, list) and len(row) == 2 and all(isinstance(v, int) and not isinstance(v, bool) for v in row)): return None
    c0, c1, r0, r1 = col[0], col[1], row[0], row[1]
    if not (1 <= c0 < c1 <= COLS + 1 and 1 <= r0 < r1 <= rows + 1): return None
    return c0, c1, r0, r1


def overlap(a, b):
    return a[0] < b[1] and b[0] < a[1] and a[2] < b[3] and b[2] < a[3]


def span_px(node_area, page, bleed='none', gap=24, viewport=1440):
    """Width in CSS pixels a node spans at a 1440 viewport, bleed included."""
    container, frame = page.get('container', 1300), page.get('frame', 40)
    inner = min(viewport, container) - 2 * frame
    col = (inner - (COLS - 1) * gap) / COLS
    n = node_area[1] - node_area[0]
    width = n * col + (n - 1) * gap
    if bleed in ('left', 'right'): width += frame + max(0, (viewport - container) / 2)
    return width


def validate(ir, content):
    errors = []
    def err(code, at, message): errors.append({'code': code, 'at': at, 'message': message})
    if not isinstance(ir, dict) or ir.get('ir') != VERSION or not isinstance(ir.get('hero'), dict):
        err('IR001', 'ir', f'a composition is {{"ir": "{VERSION}", "hero": {{…}}}}'); return errors
    extra = set(ir) - {'ir', 'hero', 'note', 'unsupported'}
    if extra: err('IR001', 'ir', f'unknown top-level fields: {sorted(extra)}')
    if ir.get('unsupported'): err('IR100', 'unsupported', 'the composition says it needs something the renderer does not have: ' + '; '.join(str(u.get('missing') if isinstance(u, dict) else u) for u in ir['unsupported'][:4]))
    hero = ir['hero']
    extra = set(hero) - HERO_KEYS
    if extra: err('IR001', 'hero', f'unknown hero fields: {sorted(extra)}')
    if hero.get('surface', 'paper') != 'paper':  # the nav belongs to the page and cannot follow another surface yet: white links on a white hero
        err('IR001', 'hero.surface', 'in this version the first screen sits on the page\'s own surface ("paper"): the navigation above it cannot follow another one yet')
    if hero.get('height', 'auto') not in HEIGHTS: err('IR001', 'hero.height', f'height is one of {HEIGHTS}')
    if hero.get('gap', 'md') not in GAPS: err('IR001', 'hero.gap', f'gap is one of {GAPS}')
    if hero.get('enter', 'none') not in ENTER: err('IR070', 'hero.enter', f'enter is one of {ENTER}')
    rows = hero.get('rows')
    if not (isinstance(rows, list) and 1 <= len(rows) <= 6 and all(r in ROW_SIZES for r in rows)):
        err('IR001', 'hero.rows', f'rows is a list of 1–6 sizes from {ROW_SIZES}'); return errors
    nodes = hero.get('nodes')
    if not (isinstance(nodes, list) and 1 <= len(nodes) <= 12 and all(isinstance(n, dict) for n in nodes)):
        err('IR001', 'hero.nodes', 'nodes is a list of 1–12 objects'); return errors

    ids, areas, placed_text, placed_actions = [], {}, [], []
    for i, node in enumerate(nodes):
        where = f'hero.nodes[{i}]'; kind = node.get('t'); nid = node.get('id')
        if not (isinstance(nid, str) and nid and nid.replace('-', '').replace('_', '').isalnum() and len(nid) <= 24): err('IR001', where, 'every node has a short alphanumeric id'); continue
        if nid in ids: err('IR001', where, f'node id "{nid}" is used twice')
        ids.append(nid); where = f'hero.nodes[{nid}]'
        if kind not in KEYS: err('IR001', where, f't is one of {sorted(KEYS)}'); continue
        extra = set(node) - KEYS[kind]
        if extra:  # the only way to say something is by address: a field that could carry words or markup does not exist
            err('IR011' if extra & {'text', 'content', 'html', 'label', 'href', 'value', 'title'} else 'IR001', where, f'unknown fields {sorted(extra)}: a composition places content by address, it does not contain it')
        a = area(node, len(rows))
        if a is None: err('IR030', where, f'"at" needs col [start, end] within 1..{COLS + 1} and row within 1..{len(rows) + 1}, start before end'); continue
        areas[nid] = a
        z = node['at'].get('z', 1)
        if not (isinstance(z, int) and not isinstance(z, bool) and 0 <= z <= 4): err('IR030', where, 'z is 0..4')
        if node['at'].get('self', 'start') not in SELF: err('IR030', where, f'self is one of {SELF}')
        if set(node['at']) - {'col', 'row', 'z', 'self'}: err('IR001', where, 'unknown placement fields')

        if kind == 'text':
            src, role = node.get('src'), node.get('as')
            if role not in ROLES: err('IR001', where, f'"as" is one of {ROLES}')
            if src not in content['text']: err('IR010', where, f'no text at address "{src}"; available: {sorted(content["text"])}')
            else: placed_text.append(src)
            expected = {'hero.h1': 'h1', 'hero.lede': 'lede', 'hero.category': 'label', 'hero.fact': 'label'}.get(src)
            if expected and role in ROLES and role != expected: err('IR080', where, f'"{src}" is placed as "{expected}", not "{role}": the headline is the h1 and nothing else is')
            if role == 'h1' and node.get('size', 'xxl') not in H1_SIZES: err('IR041', where, f'a headline size is one of {H1_SIZES}')
            if role == 'lede' and node.get('size', 'md') not in LEDE_SIZES: err('IR041', where, f'a lede size is one of {LEDE_SIZES}')
            if role == 'label' and 'size' in node: err('IR041', where, 'a label has one size')
            measure = node.get('measure'); lo, hi = (6, 40) if role == 'h1' else (20, 70)
            if measure is not None and not (isinstance(measure, int) and not isinstance(measure, bool) and lo <= measure <= hi): err('IR041', where, f'measure for a {role} is {lo}–{hi} characters')
            if role == 'label' and measure is not None: err('IR041', where, 'a label has no measure')
            if node.get('align', 'start') not in ALIGN: err('IR001', where, f'align is one of {ALIGN}')
            if node.get('plate') is not None and node.get('plate') not in PLATES: err('IR001', where, f'plate is one of {PLATES}')
        elif kind == 'actions':
            src = node.get('src')
            if not (isinstance(src, list) and 1 <= len(src) <= 2 and all(isinstance(s, str) for s in src)): err('IR001', where, 'actions.src is a list of one or two action addresses'); continue
            for s in src:
                if s not in content['actions']: err('IR010', where, f'no action at address "{s}"; available: {sorted(content["actions"])}')
                else: placed_actions.append(s)
            if node.get('align', 'start') not in ALIGN: err('IR001', where, f'align is one of {ALIGN}')
        elif kind == 'media':
            src = node.get('src'); m = content['media'].get(src)
            if m is None: err('IR010', where, f'no picture at address "{src}"; available: {sorted(content["media"])}'); continue
            fit, ratio, bleed, frame = node.get('fit', 'cover'), node.get('ratio'), node.get('bleed', 'none'), node.get('frame', 'none')
            if fit not in FITS: err('IR001', where, f'fit is one of {FITS}')
            if ratio not in RATIOS: err('IR064', where, f'a picture states its ratio, one of {RATIOS}: the height it takes is then known before it is drawn')
            if bleed not in BLEEDS: err('IR001', where, f'bleed is one of {BLEEDS}')
            if frame not in FRAMES: err('IR001', where, f'frame is one of {FRAMES}')
            if not isinstance(node.get('scrim', False), bool): err('IR001', where, 'scrim is true or false')
            focal = node.get('focal', [0.5, 0.5])
            if not (isinstance(focal, list) and len(focal) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1 for v in focal)): err('IR001', where, 'focal is [x, y], each 0..1')
            if bleed == 'left' and a[0] != 1: err('IR030', where, 'a picture bleeds left only from the first column')
            if bleed == 'right' and a[1] != COLS + 1: err('IR030', where, 'a picture bleeds right only from the last column')
            if m.get('shot'):
                if fit != 'contain' or frame == 'none' or bleed != 'none' or node.get('scrim'): err('IR062', where, 'a screenshot is shown whole in a frame: fit "contain", a frame, no bleed, no scrim')
            if m.get('gen'): err('IR065', where, f'"{src}" is a generated picture: it is never the picture of a real place or product')
            if src in content.get('used_elsewhere', []): err('IR061', where, f'"{src}" is already shown in another section of this page; a picture appears once')
            w, h = m.get('w'), m.get('h')
            if not (isinstance(w, (int, float)) and isinstance(h, (int, float)) and w > 0 and h > 0): err('IR063', where, f'the pixel size of "{src}" is unknown, so it cannot be checked against the space it would fill')
            elif ratio in RATIOS and bleed in BLEEDS:
                gap = {'sm': 16, 'md': 24, 'lg': 40}.get(hero.get('gap', 'md'), 24)
                width = span_px(a, content.get('page', {}), bleed, gap); num, den = (int(v) for v in ratio.split('/')); height = width * den / num
                limit = 1.0 if m.get('shot') else UPSCALE
                if fit == 'contain': needed = min(width / w, height / h)
                else: needed = max(width / w, height / h)
                if needed > limit + 1e-6: err('IR060', where, f'"{src}" is {int(w)}×{int(h)} px and would fill {round(width)}×{round(height)} px at a 1440 viewport ({needed:.2f}× its pixels, limit {limit}×): give it fewer columns or a different ratio')
        elif kind == 'shape':
            if node.get('kind') != 'rule': err('IR001', where, 'the only shape is "rule"')

    # a picture that is placed has to register: the contract asks for a first-screen visual at least 30% of the screen wide
    pictures = [n for n in nodes if n.get('t') == 'media' and n.get('id') in areas]
    if pictures and not any(span_px(areas[n['id']], content.get('page', {}), n.get('bleed', 'none')) >= 0.3 * 1440 for n in pictures):
        err('IR066', 'hero.nodes', 'the pictures placed are all under 30% of the screen width: give one of them at least five columns, or compose with type alone')
    # content is constrained: everything the production hero says is placed, once
    for address in content['text']:
        n = placed_text.count(address)
        if n != 1: err('IR020', 'hero.nodes', f'"{address}" is placed {n} times; every piece of the hero\'s text is placed exactly once')
    for address in content['actions']:
        n = placed_actions.count(address)
        if n != 1: err('IR021', 'hero.nodes', f'action "{address}" is placed {n} times; every action is placed exactly once')

    by_id = {n.get('id'): n for n in nodes if isinstance(n.get('id'), str)}
    wordy = [i for i in areas if by_id[i].get('t') in ('text', 'actions')]
    for x, a in enumerate(wordy):
        for b in wordy[x + 1:]:
            if overlap(areas[a], areas[b]): err('IR031', f'hero.nodes[{a}]', f'"{a}" and "{b}" occupy the same cells: text never sits on text')
    for t in wordy:
        for m in (i for i in areas if by_id[i].get('t') == 'media'):
            if overlap(areas[t], areas[m]) and not by_id[t].get('plate') and not by_id[m].get('scrim'):
                if by_id[t].get('t') == 'actions': err('IR032', f'hero.nodes[{t}]', f'buttons "{t}" sit on picture "{m}": give the picture a scrim or move the buttons off it')
                else: err('IR032', f'hero.nodes[{t}]', f'"{t}" sits on picture "{m}" with nothing between them: give the text a plate or the picture a scrim')

    # reading order is document order: the headline comes before the lede and the actions
    order = [n.get('id') for n in nodes]
    h1 = next((n['id'] for n in nodes if n.get('t') == 'text' and n.get('as') == 'h1'), None)
    if h1:
        for n in nodes:
            later = n.get('t') == 'actions' or (n.get('t') == 'text' and n.get('as') == 'lede')
            if later and order.index(n['id']) < order.index(h1): err('IR080', f'hero.nodes[{n["id"]}]', 'in the list of nodes the headline comes before the lede and the actions: that order is what a screen reader hears')
    sm = hero.get('sm')
    if sm is not None:
        phone = sm.get('order') if isinstance(sm, dict) else None
        if not (isinstance(phone, list) and sorted(phone) == sorted(ids) and set(sm) <= {'order'}): err('IR090', 'hero.sm', 'sm.order lists every node id exactly once: on a phone the pieces stack in that order')
    return errors


if __name__ == '__main__':
    import json, os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import content as CONTENT
    if len(sys.argv) != 4: raise SystemExit('usage: validate.py <composition.json> <page.html> <images.json>')
    with open(sys.argv[1]) as f: ir = json.load(f)
    with open(sys.argv[2], encoding='utf-8') as f: page = f.read()
    with open(sys.argv[3]) as f: images = json.load(f)
    found = validate(ir, CONTENT.from_page(page, images))
    for e in found: print(f"{e['code']} {e['at']}: {e['message']}")
    print('composition may be drawn' if not found else f'{len(found)} problem(s): refused')
    raise SystemExit(1 if found else 0)
