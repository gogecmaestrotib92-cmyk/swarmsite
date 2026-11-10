"""validate.py — is this hero composition one the renderer may draw?

A composition is a small document that says where the hero's own content sits on a 12-column grid. It is written by a
person or a model and it is not trusted: everything is checked here before a pixel is drawn, and a composition that
fails is refused whole — the page keeps its production hero. Nothing is repaired silently.

What a composition can do: place each piece of content on the grid, size the headline, set a measure, let a picture
bleed or sit under the headline, choose the height, order the pieces for a phone. Since 0.2 also: set the page in a
typeface from the registry (lib/type), break the headline into lines by word count, indent or scale a line, mark a
word (accent, italic, outline, underline, box), tone and shape a photograph, tilt it, layer two or three pictures, and
say how a picture arrives and moves.
What it cannot do: contain text, link anywhere, leave content out, stack text on text, put text on a picture without
a plate or a scrim, stretch a picture past its pixels, treat a screenshot as anything but the product shown whole, or
use a field this file does not list.

  validate(ir, content) → [{'code', 'at', 'message'}]      ([] = may be drawn)
Codes are stable; tests seed one defect per code. Deterministic, no network, no model."""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'type'))
import faces as FACES

VERSION = '0.2'
ACCEPTED = ('0.1', '0.2')   # 0.2 only adds fields: a 0.1 composition means the same thing
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
SCALES = (0.6, 0.8, 1, 1.3, 1.6)          # a line of the headline relative to the others
MARKS = ('accent', 'italic', 'outline', 'underline', 'box')
CASES = ('none', 'upper')
STACKS = ('offset', 'fan')
TONES = ('none', 'mono', 'duotone', 'tint')
SHAPES = ('rect', 'soft', 'arch', 'circle', 'pill')
SHADOWS = ('none', 'soft', 'hard')
MEDIA_ENTER = ('none', 'rise', 'clip', 'settle')
MEDIA_SCROLL = ('none', 'parallax')
MIN_H1_PX = 48   # the page contract's floor for a headline at 1440
FIRST_SCREEN_PX = {'auto': 720, 'screen': 720, 'tall': 900}   # the room a 1440×900 first screen has under the navigation: a picture taller than this pushes the rest under the fold
MAX_LINES = 3    # and its ceiling on lines
UPSCALE = 1.35   # a photograph may be shown up to this much past its pixels (the renderer's own limit); a screenshot not at all

KEYS = {
    'text': {'id', 't', 'src', 'as', 'size', 'measure', 'align', 'plate', 'at', 'lines', 'indent', 'scale', 'mark', 'mark_words', 'fit'},
    'actions': {'id', 't', 'src', 'align', 'at'},
    'media': {'id', 't', 'src', 'fit', 'ratio', 'focal', 'bleed', 'frame', 'scrim', 'at', 'stack', 'tone', 'shape', 'tilt', 'shadow', 'grain', 'enter', 'scroll'},
    'shape': {'id', 't', 'kind', 'at'},
}
HERO_KEYS = {'surface', 'height', 'rows', 'gap', 'nodes', 'sm', 'enter', 'face'}


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


def stack_layout(kind, n, ratio):
    """Where the layers of a stack of n pictures sit inside the node's box. The first picture named is the one in front.
    Returns (box width / box height, [{'left', 'top', 'width', 'height' as fractions of the box, 'rotate' in degrees, 'z'}], layer width as a fraction of the box).
    Every layer, rotated, stays inside the box: what the validator knows about the node's cells stays true of the pixels."""
    import math
    num, den = (int(v) for v in ratio.split('/')); r = num / den
    if kind == 'fan':   # the front picture upright in the middle (or leaning, for two), the others turned away behind it
        f, angles, side = (0.64, (4, -5), (1, -1)) if n == 2 else (0.6, (0, -7, 7), (0, -1, 1))
        layer_h = f / r
        turned = [(f * math.cos(math.radians(abs(t))) + layer_h * math.sin(math.radians(abs(t))), layer_h * math.cos(math.radians(abs(t))) + f * math.sin(math.radians(abs(t)))) for t in angles]   # each layer's bounding box once rotated
        drop = [0 if k == 0 else 0.03 * layer_h for k in range(n)]
        box_h = max(h + d for (_, h), d in zip(turned, drop))
        spread = min(0.14 if n == 2 else 0.19, min(0.5 - w / 2 for w, _ in turned))
        layers = [{'left': 0.5 + side[k] * spread - f / 2, 'top': ((turned[k][1] - layer_h) / 2 + drop[k]) / box_h, 'width': f, 'height': layer_h / box_h, 'rotate': angles[k], 'z': n - k} for k in range(n)]
    else:   # offset: a diagonal step, the front picture lowest and furthest right
        f = 0.74 if n == 2 else 0.62
        layer_h = f / r; step_x = (1 - f) / (n - 1); step_y = 0.14 * layer_h; box_h = layer_h + (n - 1) * step_y
        layers = [{'left': (n - 1 - k) * step_x, 'top': (n - 1 - k) * step_y / box_h, 'width': f, 'height': layer_h / box_h, 'rotate': 0, 'z': n - k} for k in range(n)]
    return 1 / box_h, layers, f


def face_of(hero, content):
    """(face or None, set in capitals?) for the headline of this composition: the registry face it chooses, else what is
    known about the page's own (its measured widths, when it is a family the registry has measured)."""
    chosen = hero.get('face') if isinstance(hero.get('face'), dict) else None
    page = content.get('page', {})
    face = FACES.get(chosen.get('id')) if chosen else FACES.known(page.get('display'))
    if chosen and chosen.get('case') in CASES: upper = chosen['case'] == 'upper'
    elif chosen and face: upper = bool(face.get('upper'))
    else: upper = bool(page.get('upper'))
    return face, upper


def headline_em(node, content, face, upper):
    """The widest thing the headline must fit on one line, in em of its own size: its longest line when it is broken by
    hand (scale and indent counted), its longest word when it wraps freely. Measured in a browser when the composition
    carries the measurement (`fit`); otherwise estimated from the face's average advance."""
    measured = node.get('fit')
    if isinstance(measured, dict) and isinstance(measured.get('line'), (int, float)) and not isinstance(measured.get('line'), bool) and measured['line'] > 0: return measured['line']
    words = [''.join(t for t, _ in w) for w in content_words(content['text'].get(node.get('src')) or [])]
    adv = FACES.advance(face, upper)
    lines = node.get('lines')
    if not (isinstance(lines, list) and lines and all(isinstance(n, int) and not isinstance(n, bool) and n > 0 for n in lines) and sum(lines) == len(words)):
        return max((len(w) for w in words), default=6) * adv
    widest, at = 0, 0
    for i, count in enumerate(lines):
        chars = len(' '.join(words[at:at + count])); at += count
        scale = node['scale'][i] if isinstance(node.get('scale'), list) and len(node['scale']) == len(lines) and node['scale'][i] in SCALES else 1
        indent = node['indent'][i] if isinstance(node.get('indent'), list) and len(node['indent']) == len(lines) and isinstance(node['indent'][i], int) else 0
        widest = max(widest, chars * adv * scale + indent * 0.5)
    return widest


def content_words(segments):
    import content as CONTENT
    return CONTENT.words(segments)


def validate(ir, content):
    errors = []
    def err(code, at, message): errors.append({'code': code, 'at': at, 'message': message})
    if not isinstance(ir, dict) or ir.get('ir') not in ACCEPTED or not isinstance(ir.get('hero'), dict):
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
    chosen = hero.get('face'); known = None
    if chosen is not None:   # the typeface is a decision for the whole page: it comes from the registry of faces that are free to ship, or it stays the page's own
        known = FACES.get(chosen.get('id')) if isinstance(chosen, dict) else None
        if not isinstance(chosen, dict) or set(chosen) - {'id', 'weight', 'case'}: err('IR050', 'hero.face', 'face is {"id", optional "weight", optional "case"}')
        elif not known: err('IR050', 'hero.face', f'no typeface "{chosen.get("id")}" in the registry; available: {[f["id"] for f in FACES.all()]}')
        else:
            weight = chosen.get('weight')
            if weight is not None and not (isinstance(weight, int) and not isinstance(weight, bool) and known['weights'][0] <= weight <= known['weights'][1]):
                err('IR050', 'hero.face', f'{known["family"]} has weights {known["weights"][0]}–{known["weights"][1]}')
            if chosen.get('case') is not None and chosen['case'] not in CASES: err('IR050', 'hero.face', f'case is one of {CASES}')
            if content.get('page', {}).get('face_locked'): err('IR051', 'hero.face', f'this page is set in the brand\'s own typeface ({content["page"].get("display")}): it is kept')
    face, upper = face_of(hero, content)
    rows = hero.get('rows')
    if not (isinstance(rows, list) and 1 <= len(rows) <= 6 and all(r in ROW_SIZES for r in rows)):
        err('IR001', 'hero.rows', f'rows is a list of 1–6 sizes from {ROW_SIZES}'); return errors
    nodes = hero.get('nodes')
    if not (isinstance(nodes, list) and 1 <= len(nodes) <= 12 and all(isinstance(n, dict) for n in nodes)):
        err('IR001', 'hero.nodes', 'nodes is a list of 1–12 objects'); return errors

    ids, areas, placed_text, placed_actions, placed_media, widths = [], {}, [], [], [], {}
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
            treated = [k for k in ('lines', 'indent', 'scale', 'mark', 'mark_words', 'fit') if k in node]
            if treated and role != 'h1': err('IR042', where, f'{treated} belong to the headline only')
            elif role == 'h1' and src in content['text']:
                words = content_words(content['text'][src]); lines = node.get('lines'); ok_lines = False
                if lines is not None:
                    if not (isinstance(lines, list) and 1 <= len(lines) <= MAX_LINES and all(isinstance(n, int) and not isinstance(n, bool) and n > 0 for n in lines)):
                        err('IR042', where, f'lines is 1–{MAX_LINES} word counts, one per line, each at least 1')
                    elif sum(lines) != len(words): err('IR042', where, f'lines {lines} adds up to {sum(lines)} words; the headline has {len(words)}: {" / ".join("".join(t for t, _ in w) for w in words)}')
                    else: ok_lines = True
                    if node.get('measure') is not None: err('IR042', where, 'a headline broken by hand has no measure: the lines are the measure')
                for field, allowed, what in (('indent', None, 'whole steps 0–6 (half an em each)'), ('scale', SCALES, f'one of {SCALES}')):
                    value = node.get(field)
                    if value is None: continue
                    fits = lambda v: (v in allowed) if allowed else (isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 6)
                    if not ok_lines: err('IR042', where, f'{field} is given per line: it needs "lines"')
                    elif not (isinstance(value, list) and len(value) == len(lines) and all(not isinstance(v, bool) and fits(v) for v in value)): err('IR042', where, f'{field} has one value per line, {what}')
                    elif field == 'scale' and sum(value) > MAX_LINES + 0.4: err('IR042', where, f'lines scaled {value} stand as tall as {sum(value):g} lines; the headline may stand as tall as {MAX_LINES}')
                mark, marked = node.get('mark'), node.get('mark_words')
                if mark is not None and mark not in MARKS: err('IR043', where, f'mark is one of {MARKS}')
                if marked is not None:
                    if mark is None: err('IR043', where, 'mark_words says which words; "mark" says how they are drawn')
                    if not (isinstance(marked, list) and marked and all(isinstance(i, int) and not isinstance(i, bool) and 0 <= i < len(words) for i in marked) and len(set(marked)) == len(marked)):
                        err('IR043', where, f'mark_words lists word positions 0–{len(words) - 1}, each once')
                    elif len(marked) > max(1, len(words) // 2): err('IR043', where, f'{len(marked)} of {len(words)} words marked: a mark is the exception, at most {max(1, len(words) // 2)} here')
                elif mark is not None and not any(em for w in words for _, em in w): err('IR043', where, 'this headline has no emphasised word of its own: say which with mark_words')
                if mark == 'italic' and known and not known.get('italic'): err('IR043', where, f'{known["family"]} has no italic: mark with accent, outline, underline or box')
                # can it be set at all? the widest line (or word) at the contract's smallest headline has to fit the columns it was given
                estimate = headline_em({k: v for k, v in node.items() if k != 'fit'}, content, face, upper); fit = node.get('fit')
                if fit is not None:   # what a browser measured for these words in this face (lib/compose/measure.mjs): it replaces the estimate, it does not contradict it
                    good = isinstance(fit, dict) and set(fit) == {'line', 'word'} and all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0.3 <= v <= 80 for v in fit.values())
                    if not good: err('IR045', where, 'fit is {"line", "word"}: the measured width in em of the widest line and of the widest word')
                    elif not 0.6 <= fit['line'] / estimate <= 1.6: err('IR045', where, f'fit says the widest line is {fit["line"]:.2f} em; these words in this face are about {estimate:.2f} em: the measurement belongs to another headline, face or break — measure again')
                widest = headline_em(node, content, face, upper)
                gap_px = {'sm': 16, 'md': 24, 'lg': 40}.get(hero.get('gap', 'md'), 24); room = span_px(a, content.get('page', {}), 'none', gap_px)
                if widest > 0 and room / widest < MIN_H1_PX * 0.9:
                    what_ = 'its longest line' if ok_lines else 'its longest word'
                    err('IR044', where, f'{what_} is about {widest:.1f} em wide and these columns are {round(room)} px at 1440: the headline would be set near {round(room / widest)} px, under the {MIN_H1_PX} px a headline needs. Give it more columns' + (', break it into more or shorter lines' if ok_lines else '') + ' or a narrower face')
        elif kind == 'actions':
            src = node.get('src')
            if not (isinstance(src, list) and 1 <= len(src) <= 2 and all(isinstance(s, str) for s in src)): err('IR001', where, 'actions.src is a list of one or two action addresses'); continue
            for s in src:
                if s not in content['actions']: err('IR010', where, f'no action at address "{s}"; available: {sorted(content["actions"])}')
                else: placed_actions.append(s)
            if node.get('align', 'start') not in ALIGN: err('IR001', where, f'align is one of {ALIGN}')
        elif kind == 'media':
            src = node.get('src'); stacked = isinstance(src, list)
            sources = src if stacked else [src]
            if stacked and not (2 <= len(src) <= 3 and all(isinstance(x, str) for x in src) and len(set(src)) == len(src)): err('IR001', where, 'a stack names two or three different pictures, the front one first'); continue
            missing = [x for x in sources if not isinstance(x, str) or x not in content['media']]
            if missing: err('IR010', where, f'no picture at address {missing}; available: {sorted(content["media"])}'); continue
            fit, ratio, bleed, frame = node.get('fit', 'cover'), node.get('ratio'), node.get('bleed', 'none'), node.get('frame', 'none')
            tone, shape, tilt, shadow = node.get('tone', 'none'), node.get('shape', 'rect'), node.get('tilt', 0), node.get('shadow', 'none')
            enter, scroll, stack = node.get('enter', 'none'), node.get('scroll', 'none'), node.get('stack')
            if fit not in FITS: err('IR001', where, f'fit is one of {FITS}')
            if ratio not in RATIOS: err('IR064', where, f'a picture states its ratio, one of {RATIOS}: the height it takes is then known before it is drawn')
            if bleed not in BLEEDS: err('IR001', where, f'bleed is one of {BLEEDS}')
            if frame not in FRAMES: err('IR001', where, f'frame is one of {FRAMES}')
            if tone not in TONES: err('IR001', where, f'tone is one of {TONES}')
            if shape not in SHAPES: err('IR001', where, f'shape is one of {SHAPES}')
            if shadow not in SHADOWS: err('IR001', where, f'shadow is one of {SHADOWS}')
            if not (isinstance(tilt, int) and not isinstance(tilt, bool) and -4 <= tilt <= 4): err('IR001', where, 'tilt is a whole number of degrees, -4 to 4: more than that leaves the cells the picture was given'); tilt = 0
            if not isinstance(node.get('scrim', False), bool): err('IR001', where, 'scrim is true or false')
            if not isinstance(node.get('grain', False), bool): err('IR001', where, 'grain is true or false')
            if enter not in MEDIA_ENTER: err('IR070', where, f'a picture arrives as one of {MEDIA_ENTER}')
            if scroll not in MEDIA_SCROLL: err('IR070', where, f'a picture moves with the scroll as one of {MEDIA_SCROLL}')
            if stacked and stack not in STACKS: err('IR001', where, f'pictures named together are a stack: "stack" is one of {STACKS}')
            if not stacked and stack is not None: err('IR001', where, '"stack" needs two or three pictures in "src"')
            focal = node.get('focal', [0.5, 0.5])
            if not (isinstance(focal, list) and len(focal) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1 for v in focal)): err('IR001', where, 'focal is [x, y], each 0..1')
            if bleed == 'left' and a[0] != 1: err('IR030', where, 'a picture bleeds left only from the first column')
            if bleed == 'right' and a[1] != COLS + 1: err('IR030', where, 'a picture bleeds right only from the last column')
            # treatments that do not go together
            if shape == 'circle' and ratio != '1/1': err('IR067', where, 'a circle is a picture at ratio 1/1')
            if bleed in ('left', 'right') and (tilt or shape not in ('rect',) or shadow != 'none' or stacked): err('IR067', where, 'a picture that bleeds to the screen edge is a plain rectangle: no tilt, shape, shadow or stack')
            if frame != 'none' and shape not in ('rect', 'soft'): err('IR067', where, 'a framed picture keeps a rectangular shape')
            if stacked and (node.get('scrim') or shape not in ('rect', 'soft') or tilt or scroll != 'none'): err('IR067', where, 'a stack is rectangles laid on each other: no scrim, shape, tilt of its own or parallax')
            if scroll == 'parallax' and (fit != 'cover' or tilt or shape not in ('rect', 'soft') or frame != 'none'): err('IR067', where, 'parallax moves a photograph inside its own frame: fit "cover", no tilt, no frame, a rectangular shape')
            shots = [x for x in sources if content['media'][x].get('shot')]
            if shots:   # a screenshot is evidence of the product: shown whole, in its own colours
                if fit != 'contain' or frame == 'none' or bleed != 'none' or node.get('scrim'): err('IR062', where, 'a screenshot is shown whole in a frame: fit "contain", a frame, no bleed, no scrim')
                if tone != 'none' or shape not in ('rect', 'soft') or scroll != 'none': err('IR062', where, 'a screenshot keeps its own colours and its rectangle: no tone, no shape, no parallax')
            gap = {'sm': 16, 'md': 24, 'lg': 40}.get(hero.get('gap', 'md'), 24)
            share = stack_layout(stack, len(sources), ratio)[2] if stacked and stack in STACKS and ratio in RATIOS else 1
            for x in sources:
                m = content['media'][x]
                if m.get('gen'): err('IR065', where, f'"{x}" is a generated picture: it is never the picture of a real place or product')
                if x in content.get('used_elsewhere', []): err('IR061', where, f'"{x}" is already shown in another section of this page; a picture appears once')
                if x in placed_media: err('IR061', where, f'"{x}" is placed twice in this first screen; a picture appears once')
                placed_media.append(x)
                w, h = m.get('w'), m.get('h')
                if not (isinstance(w, (int, float)) and isinstance(h, (int, float)) and w > 0 and h > 0): err('IR063', where, f'the pixel size of "{x}" is unknown, so it cannot be checked against the space it would fill'); continue
                if ratio not in RATIOS or bleed not in BLEEDS: continue
                width = span_px(a, content.get('page', {}), bleed, gap) * share; num, den = (int(v) for v in ratio.split('/')); height = width * den / num
                limit = 1.0 if m.get('shot') else UPSCALE
                needed = min(width / w, height / h) if fit == 'contain' else max(width / w, height / h)
                if needed > limit + 1e-6: err('IR060', where, f'"{x}" is {int(w)}×{int(h)} px and would fill {round(width)}×{round(height)} px at a 1440 viewport ({needed:.2f}× its pixels, limit {limit}×): give it fewer columns or a different ratio')
                if stacked and m.get('shot') and abs((num / den) / (w / h) - 1) > 0.12:
                    nearest = min(RATIOS, key=lambda q: abs(int(q.split('/')[0]) / int(q.split('/')[1]) - w / h))
                    err('IR068', where, f'"{x}" is a {int(w)}×{int(h)} screenshot and the stack\'s ratio {ratio} would letterbox it: the nearest ratio to its own is {nearest}')
            # what registers as the first screen's picture: one picture by its own width, a stack by the room its pictures take together
            # (the page contract counts a figure of several pictures as one visual) as long as each is a picture and not an icon
            layer = span_px(a, content.get('page', {}), bleed if bleed in BLEEDS else 'none', gap) * share
            widths[nid] = (layer / share if layer >= 0.15 * 1440 else 0) if stacked else layer
            if ratio in RATIOS and bleed in BLEEDS:   # the first screen is 900 px tall: a picture that stands taller pushes what is under it out of it
                num, den = (int(v) for v in ratio.split('/')); full = span_px(a, content.get('page', {}), bleed, gap)
                first = content['media'][sources[0]]
                if stacked and stack in STACKS: tall = full / stack_layout(stack, len(sources), ratio)[0]
                elif fit == 'contain' and isinstance(first.get('w'), (int, float)) and isinstance(first.get('h'), (int, float)) and first['w'] > 0: tall = full * first['h'] / first['w']
                else: tall = full * den / num
                room = FIRST_SCREEN_PX.get(hero.get('height', 'auto'), 720)
                if tall > room: err('IR069', where, f'{"this stack" if stacked else "this picture"} would stand about {round(tall)} px tall at 1440 ({round(full)} px wide) and the first screen has room for about {room}: give it fewer columns or a wider ratio')
        elif kind == 'shape':
            if node.get('kind') != 'rule': err('IR001', where, 'the only shape is "rule"')

    # a picture that is placed has to register: the contract asks for a first-screen visual at least 30% of the screen wide
    pictures = [n for n in nodes if n.get('t') == 'media' and n.get('id') in areas]
    if pictures and not any(widths.get(n['id'], span_px(areas[n['id']], content.get('page', {}), 'none')) >= 0.3 * 1440 for n in pictures):
        err('IR066', 'hero.nodes', 'the pictures placed are all under 30% of the screen width (a stack counts by its whole width when each of its pictures is at least 15% of the screen): give one more columns, or compose with type alone')
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
