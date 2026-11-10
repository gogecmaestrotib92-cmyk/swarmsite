"""compose.py — a model writes the hero composition; this file keeps it honest.

The model is an art director with fixed material: the production hero's words, buttons and pictures (content.py). It
sees the pictures, the hero the template made, and the measured principles of the references that fit this business
(design_dna). It answers with a composition and nothing else. The loop around it:

  1. compose        — one call; the answer is validated (validate.py)
  2. correct        — a refused composition goes back once with the validator's reasons
  3. look and revise — the valid composition is rendered and screenshotted at 1440 and 390 and graded by the page
                       contract; the model sees its own page and what it newly breaks, and may revise once. A revision
                       that does not validate, or measures worse, is dropped; the valid one stands.
  4. refuse         — a composition that still breaks the page on the render is not shipped at all.
Before it is looked at, the composition's headline is measured in a browser (measure.mjs) and sized from that
measurement (`fit` on the headline node): how wide words set in a face is measured, never estimated.

Besides placement the model may choose the page's typeface from the registry of free faces (lib/type), break and mark
the headline, tone, shape, tilt and layer pictures, and name how a picture arrives — all fields of the composition,
all checked by the validator. A page set in the brand's own typeface keeps it.

The model never writes text, links or markup: the format has no field for them. What it wishes the format could do is
collected in `wishes` — the backlog for new primitives — and never drawn.

With concepts=3 the studio works the way a studio does: three compositions from three different leads (type leads, the
picture leads, the unexpected one), each drawn and measured, and a creative director chooses among the renders — never
among descriptions. A concept that breaks the page is not put before the director while a sound one exists.

  compose(page_html, images, job_dir=None, page_path=None, model=None, concepts=1) → {'ir', 'drawn', 'attempts', 'log', 'wishes'[, 'concepts', 'chosen', 'verdict']}
  python3 lib/compose/compose.py <page.html> <images.json> --out composition.json [--job <job dir>] [--no-review] [--concepts 3]
Needs ANTHROPIC_API_KEY. Every call is charged to the job budget when SWARM_JOB_DIR is set."""
import base64, io, json, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'lib', 'swarm')); sys.path.insert(0, os.path.join(ROOT, 'lib')); sys.path.insert(0, os.path.join(ROOT, 'design_dna'))
import content as CONTENT
import render_ir as IR
import validate as V

SYSTEM = """You are the art director of a small studio. You compose the first screen of a website for a real business.
The words, the buttons and the pictures are fixed: you do not write, you place. A page-building template has already made a competent, forgettable first screen from the same material. Yours has to be the one a person remembers, and it has to be true to this business.

How a first screen reads as designed rather than assembled:
- One thing dominates: the headline at a size that feels slightly too big, or one picture given real room. Never two equals.
- Asymmetry with a reason. Push the headline or the picture off the centre line and let the empty side be a shape, not leftover.
- Few edges. The pieces share two or three vertical edges; small text hangs from the same edge as something large.
- Scale contrast. Labels small and quiet, the headline loud, the lede narrow (36–48 characters) and close to the headline's edge.
- A picture is chosen for its subject and given the ratio that suits the subject: a tall room gets a tall ratio, a wide terrace a wide one. Put the focal point on the subject. A weak or irrelevant picture is left out — type alone can carry a first screen.
- Crossing. A headline that runs onto the picture ties the two into one object; it then needs a plate (a block of the page's own colour under the words). At most once, and only when it earns it.
- A screenshot of a product is shown whole, in a frame, in its own colours. It is never cropped, bled, toned or written over.
- The actions sit where the eye lands after the headline and the lede.
- Leave real empty space. A first screen that fills every cell is a template.
- On a phone the pieces stack. Order them so the headline is first or second and the first action comes before a long scroll.
- Type is most of it. The typeface carries the voice of the business before a word is read; where a headline breaks, which word is marked and how, decide whether it reads as written by someone. Break by sense and by shape: a short line against a long one, the stressed word alone on its line.
- Treatments are seasoning. One typographic move and one picture move per screen, each because of what this business is. If everything is treated, nothing is.

REFERENCE PRINCIPLES, when given, are measurements from reference sites that fit this business. Use them as principles — how large, how far off-centre, how much of the screen a picture takes — never as a layout to reproduce.

THE FORMAT
The hero is a grid of 12 columns and the rows you declare. A node sits at "at": {"col": [start, end], "row": n or [start, end]} using grid lines: columns 1..13, rows 1..(number of rows + 1); the end line is not included, so "col": [1, 7] is the left half.
- the hero: "height": auto|screen|tall, "rows": 1–6 of auto|1fr|2fr|min, "gap": sm|md|lg, "nodes": [...], "phone_order": [every node id, in the order they stack on a phone]. It sits on the page's own background and uses the page's own colours (you see them in the template's first screen).
- the typeface: the page is set in one display face and every heading of the page follows it. Keep the page's own ("typeface": "page") or set the page in one from TYPEFACES, chosen by its voice — what this business sounds like, never what is fashionable. Optional "weight" inside the face's range (light for a large quiet serif, heavy for a condensed or grotesque face) and "case": none|upper. When the brief says the face is the brand's own, it stays.
- the type system: a studio sets a page in a system, not a font — a display face with character, a quiet face for running text, and a third for the small print (labels, numerals, captions), very often a monospace. "body_face" and "label_face" choose the other two from TEXT FACES and LABEL FACES ("page" keeps the page's own). PAIRINGS lists systems that are known to sit well together: start from the one whose voice is this business, and change a member only for a reason. Contrast is the point: a serif display over a plain grotesk text, a grotesk display over the same grotesk for text, never two display faces. Faces marked "seen everywhere" are on most machine-made pages this year: take one only when nothing else has the voice.
- text node: {"id", "t": "text", "src": a text address, "as": label|h1|lede, "at"}. hero.h1 is always "as": "h1"; hero.lede is "lede"; hero.category and hero.fact are "label".
  h1 takes "size": xl|xxl|mega (mega is about 12% of the viewport width: for short headlines). lede takes "size": md|lg and "measure" 20–70. A label takes neither.
  Optional "align": start|center|end, and "plate": paper|ink when the text crosses a picture.
  The headline, and only it, can be set by hand:
  · "lines": word counts per line, e.g. [2, 3] for a five-word headline; one to three lines. A line never wraps and the headline is sized so that its longest line fits its columns: short lines get large type, a long line makes all of it small. Without "lines" the headline wraps by itself inside "measure" (6–40 characters); with "lines" there is no measure.
  · "indent": one value per line, steps of half an em, 0–6: [0, 2, 4] is a stepped headline. Needs "lines".
  · "scale": one value per line from 0.6 0.8 1 1.3 1.6: one line larger or smaller than the rest. Needs "lines"; the values may add up to 3.4 at most.
  · "mark": accent|italic|outline|underline|box — how the emphasised words are drawn (outline: hollow letters; box: on a block of the accent colour). It applies to the words the headline already emphasises (shown between * in the brief) unless "mark_words" names others by position, 0 being the first word. At most half the words.
- actions node: {"id", "t": "actions", "src": [one or two action addresses], "at", optional "align"}.
- media node: {"id", "t": "media", "src": a picture address, "fit": cover|contain, "ratio": one of 1/1 4/5 3/4 2/3 4/3 3/2 16/9 16/10 21/9, "focal": [x, y] each 0–1, "bleed": none|left|right|full, "frame": none|browser|paper, "scrim": true|false, "at"}.
  "bleed" runs the picture to the screen edge and is allowed only from column 1 (left) or to column line 13 (right).
  "bleed": "full" makes a photograph the BACKDROP of the whole first screen — edge to edge, under the navigation, the words standing on it in the on-photo colour. It covers "col": [1, 13] and every row, has "scrim": true and no "ratio", and takes only "tone", "grain", "focal", "enter" and "scroll". It needs a large photograph (the brief says which can carry it). Then the layout of the words answers the picture: put them where the picture is quiet, set "focal" on its subject so the crop keeps it, and keep the headline off the subject. A studio does this when the photograph is the strongest thing the business has; a picture boxed beside the text is the weaker choice whenever a photograph can carry the screen. A screenshot is always "fit": "contain" (that is its default) and needs a "frame": browser or paper; no bleed, no scrim.
  A photograph can be treated:
  · "tone": none|mono|duotone|tint — mono is black and white; duotone prints the photograph in the page's own two colours, so it belongs to the page; tint prints it in the accent colour. A snapshot that looks out of place in full colour often holds in one tone.
  · "shape": rect|soft|arch|circle|pill (a circle needs ratio 1/1). "tilt": whole degrees −4 to 4. "shadow": none|soft|hard (hard is an offset block of the accent colour). "grain": true|false.
  · a stack: "src": [the picture in front, the one behind, optionally a third] with "stack": offset|fan — two or three pictures laid on each other inside the node's own box: pages of a document, covers, two views of one thing. "ratio" is each picture's ratio; each is about two thirds of the node's width, so a stack needs six columns or more.
  · "enter": none|rise|clip|settle — how the picture arrives when the page loads (clip: it opens from the bottom; settle: it eases in from slightly large). "scroll": none|parallax — a photograph drifts inside its frame as the page scrolls. Only media nodes choose "enter" and "scroll": the words and buttons always arrive rising, the headline line by line.
  None of the treatments applies to a screenshot except "tilt", "shadow", "enter" and a stack; a picture that bleeds takes none but "tone", "grain", "enter" and "scroll".
- shape node: {"id", "t": "shape", "kind": "rule", "at"} — a hairline.
- "at" may add "z": 0–4 (higher is in front) and "self": start|center|end|stretch (where the node sits inside its rows).
Rules the renderer enforces — a composition that breaks one is refused whole:
- Every text address and every action address is placed exactly once. Pictures are optional.
- A composition contains no words and no links: there is no field for them.
- Text never shares a cell with other text or with the buttons. Text or buttons over a picture need a plate on the text or a scrim on the picture.
- A photograph is never shown wider or taller than 1.35 times its pixels; a screenshot never larger than its pixels. Column widths are given below.
- In the list of nodes the h1 comes before the lede and the actions.
- A picture you place should register: at least one spans five columns or more (the page is graded on showing a picture or the product at 30% of the screen width in the first screen when it has one).
- A picture stands no taller than about 720 px at 1440 (its width divided by its ratio; 900 px with "height": "tall"): taller, and the buttons fall under the fold.
- The headline takes at most three lines at 1440 px and is never set under 48 px. Break it yourself with "lines" when the break matters; otherwise choose size and measure for the words you have. You will be told what was measured on the render.
Answer by calling write_composition. In "concept", say in one sentence what the first screen does and why it suits this business. In "wishes", list anything you wanted that the format cannot do — it is not drawn, it is how the format grows."""

AT = {"type": "object", "required": ["col", "row"], "properties": {
    "col": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
    "row": {"anyOf": [{"type": "integer"}, {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2}]},
    "z": {"type": "integer"}, "self": {"type": "string", "enum": list(V.SELF)}}}
NODE = {"type": "object", "required": ["id", "t", "at"], "properties": {
    "id": {"type": "string"}, "t": {"type": "string", "enum": ["text", "actions", "media", "shape"]},
    "src": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 3}]},
    "as": {"type": "string", "enum": list(V.ROLES)}, "size": {"type": "string", "enum": ["md", "lg", "xl", "xxl", "mega"]}, "measure": {"type": "integer"},
    "lines": {"type": "array", "items": {"type": "integer"}, "minItems": 1, "maxItems": 3}, "indent": {"type": "array", "items": {"type": "integer"}, "maxItems": 3},
    "scale": {"type": "array", "items": {"type": "number", "enum": list(V.SCALES)}, "maxItems": 3}, "mark": {"type": "string", "enum": list(V.MARKS)}, "mark_words": {"type": "array", "items": {"type": "integer"}, "maxItems": 4},
    "stack": {"type": "string", "enum": list(V.STACKS)}, "tone": {"type": "string", "enum": list(V.TONES)}, "shape": {"type": "string", "enum": list(V.SHAPES)}, "tilt": {"type": "integer"},
    "shadow": {"type": "string", "enum": list(V.SHADOWS)}, "grain": {"type": "boolean"}, "enter": {"type": "string", "enum": list(V.MEDIA_ENTER)}, "scroll": {"type": "string", "enum": list(V.MEDIA_SCROLL)},
    "align": {"type": "string", "enum": list(V.ALIGN)}, "plate": {"type": "string", "enum": list(V.PLATES)},
    "fit": {"type": "string", "enum": list(V.FITS)}, "ratio": {"type": "string", "enum": list(V.RATIOS)},
    "focal": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}, "bleed": {"type": "string", "enum": list(V.BLEEDS)},
    "frame": {"type": "string", "enum": list(V.FRAMES)}, "scrim": {"type": "boolean"}, "kind": {"type": "string", "enum": ["rule"]}, "at": AT}}
# Flat on purpose: with the hero as one nested object the first answer came back as broken text; its fields are top-level here.
TOOL = {"name": "write_composition", "description": "The composition of the first screen. The hero's fields are given directly: typeface, height, rows, gap, nodes, phone_order.", "input_schema": {"type": "object", "required": ["concept", "rows", "nodes", "phone_order"], "properties": {
    "concept": {"type": "string", "description": "one sentence: what this first screen does and why it suits this business"},
    "page_direction": {"type": "string", "description": "two or three sentences for the art directors who compose the rest of this page after you: the attitude of the type (quiet/loud, large/small, numerals hollow or solid), where colour and dark grounds belong, what pictures should do, and the one motif that should return down the page. Instructions for colleagues, never shown to a visitor."},
    "typeface": {"type": "string", "enum": ["page"] + [f["id"] for f in V.FACES.of_role('display')], "description": "the display face the whole page is set in; \"page\" keeps the page's own"},
    "body_face": {"type": "string", "enum": ["page"] + [f["id"] for f in V.FACES.of_role('body')], "description": "the face of the page's running text; \"page\" keeps the page's own"},
    "label_face": {"type": "string", "enum": ["page"] + [f["id"] for f in V.FACES.of_role('label')], "description": "the face of the small print: labels, numerals, captions; \"page\" keeps the page's own"},
    "weight": {"type": "integer", "description": "the display weight, inside the chosen face's range"}, "case": {"type": "string", "enum": list(V.CASES)},
    "height": {"type": "string", "enum": list(V.HEIGHTS)},
    "rows": {"type": "array", "items": {"type": "string", "enum": list(V.ROW_SIZES)}, "minItems": 1, "maxItems": 6},
    "gap": {"type": "string", "enum": list(V.GAPS)},
    "nodes": {"type": "array", "minItems": 1, "maxItems": 12, "items": NODE},
    "phone_order": {"type": "array", "items": {"type": "string"}, "description": "every node id, in the order the pieces stack on a phone"},
    "wishes": {"type": "array", "maxItems": 5, "items": {"type": "object", "properties": {"intent": {"type": "string"}, "missing": {"type": "string"}}}}}}}

def _thumb(src, size=560):
    """A bounded JPEG of a data-URI image for the model to look at, or None."""
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1]))).convert('RGB'); im.thumbnail((size, size))
        buf = io.BytesIO(); im.save(buf, 'JPEG', quality=72); return base64.b64encode(buf.getvalue()).decode()
    except Exception: return None


def offered_pictures(content, limit=7):
    """Pictures a composition may reasonably use: real, not already on the page, wide enough to matter; the hero's own first."""
    out = []
    for address, m in content['media'].items():
        if address in content.get('used_elsewhere', []) or (m.get('gen') and address != 'hero.picture'): continue   # a generated picture is offered only where the template itself put it: the first screen
        if not isinstance(m.get('w'), (int, float)) or m['w'] < 480: continue
        if address != 'hero.picture' and any(m['src'] == content['media'][o]['src'] for o in ('hero.picture',) if o in content['media']): continue
        out.append((address, m))
    out.sort(key=lambda x: (x[0] != 'hero.picture', -(x[1]['w'] * (x[1].get('h') or 1))))
    return out[:limit]


def face_locked(job_dir, content):
    """Is the page set in the brand's own typeface? Then it is part of the brand and a composition keeps it. The
    direction says so: the owner kept the font and the page's display face is the one the brand's site named."""
    try:
        with open(os.path.join(job_dir, 'direction.json'), encoding='utf-8') as f: brand = json.load(f).get('brand') or {}
    except (OSError, ValueError, TypeError): return False
    named = str(brand.get('font_hint') or '').strip().casefold()
    return bool(brand.get('keep_font') and named and named == str(content['page'].get('display') or '').casefold())


def brief(content, job_dir=None):
    """The material, as text: what may be placed, how wide a column is, and the reference principles that fit."""
    page = content['page']; inner = min(1440, page['container']) - 2 * page['frame']; col = (inner - 11 * 24) / 12
    lines = ['TEXT — place each exactly once:']
    for address, value in content['text'].items():
        if address == 'hero.h1':
            words = ''.join(t for t, _ in value).split(); shown = ''.join(f'*{t}*' if em else t for t, em in value).strip()
            lines.append(f'- hero.h1 (as h1): "{shown}" — {len(words)} words, longest word {max(len(w) for w in words)} letters')
        else: lines.append(f'- {address} (as {"lede" if address == "hero.lede" else "label"}): "{value}" — {len(value.split())} words')
    lines.append('ACTIONS — place each exactly once:')
    for address, a in content['actions'].items(): lines.append(f'- {address}: "{a["label"]}" ({"outlined" if a["ghost"] else "solid"} button)')
    pictures = offered_pictures(content)
    lines.append('PICTURES — optional (thumbnails follow in this order):' if pictures else 'PICTURES — none that can carry a first screen: compose with type.')
    for address, m in pictures:
        kind = 'screenshot' if m.get('shot') else 'photograph'
        carries = not m.get('shot') and max(1440 / m['w'], V.BACKDROP_PX['auto'] / m['h']) <= V.UPSCALE
        if m.get('gen'):
            lines.append(f'- {address}: {int(m["w"])}×{int(m["h"])} px — an atmosphere picture commissioned for this page, not a photograph of the business. It may ONLY be the BACKDROP of the first screen ("bleed": "full"), which is how the template uses it; '
                         + ('it is large enough for that.' if carries else 'it is too small for that, so it is not placed.')); continue
        lines.append(f'- {address}: {int(m["w"])}×{int(m["h"])} px {kind}' + (' — the picture the template used in its hero' if address == 'hero.picture' else '') + (' — large enough to be the BACKDROP of the first screen ("bleed": "full")' if carries else ''))
    lines.append(f'WIDTHS at a 1440 px viewport: one column is about {round(col)} px and gaps are 24 px, so n columns span n×{round(col)} + (n−1)×24 px; '
                 f'a bleed adds about {round(page["frame"] + max(0, (1440 - page["container"]) / 2))} px.')
    own = page.get('display') or 'unknown'
    if page.get('face_locked'): lines.append(f'TYPEFACE — the page is set in {own}, the brand\'s own face: it stays ("typeface": "page").')
    else:
        lines.append(f'TYPEFACES — the page is set in {own} now' + (' (headlines in capitals)' if page.get('upper') else '') + '. Keep it ("page") or set the page in one of these; an average character is about `width` em wide, so a line of n characters at s px runs about n × width × s px:')
        for f in V.FACES.of_role('display'):
            lo, hi = f['weights']
            lines.append(f'- {f["id"]}: {f["family"]}, {f["kind"]}, ' + (f'weights {lo}–{hi}' if lo != hi else f'one weight ({lo})') + (', has an italic' if f.get('italic') else ', no italic')
                         + (', set in capitals' if f.get('upper') else '') + f', width {f["avg_upper" if f.get("upper") else "avg"]} — {f["voice"]}. Suits: {", ".join(f["suits"])}.' + (' SEEN EVERYWHERE this year.' if f.get('common') else ''))
        lines.append('TEXT FACES ("body_face") — the page\'s running text: ' + '; '.join(f'{f["id"]} ({f["family"]}, {f["kind"]}: {f["voice"]})' for f in V.FACES.of_role('body')) + '.')
        lines.append('LABEL FACES ("label_face") — the small print: ' + '; '.join(f'{f["id"]} ({f["family"]}: {f["voice"]})' for f in V.FACES.of_role('label')) + '.')
        lines.append('PAIRINGS — systems that sit well together (display / text / label): ' + '; '.join(f'{p["voice"]}: {p["display"]} / {p["body"]} / {p["label"]}' for p in V.FACES.pairings()) + '.')
    if job_dir:
        try:
            import retrieve as DNA
            found = DNA.retrieve(DNA.brand_from_job(job_dir), k=3)
            if found:
                lines.append('REFERENCE PRINCIPLES (measured on reference sites that fit this business; principles, not layouts):')
                for r in found:
                    statements = [p.get('statement') for p in (r.get('card') or {}).get('principles', []) if p.get('statement')][:6]
                    lines.append(f'- {r["id"]} ({(r.get("card") or {}).get("archetype", "")}): ' + ' '.join(statements))
        except Exception as e: lines.append(f'(reference principles unavailable: {str(e)[:80]})')
    return '\n'.join(lines), pictures


def hero_shots(page_path):
    """First-screen pictures of a page at 1440 and 390 (the first section, as lib/qa/shots.mjs takes it)."""
    out = tempfile.mkdtemp(prefix='compose-shots-')
    r = subprocess.run(['node', os.path.join(ROOT, 'lib/qa/shots.mjs'), page_path, '--out', out, '--fast'], cwd=ROOT, capture_output=True, text=True, timeout=240)
    if r.returncode: raise RuntimeError('screenshots failed: ' + (r.stderr or r.stdout)[-300:])
    files = sorted(os.listdir(out)); pick = lambda prefix: next((os.path.join(out, f) for f in files if f.startswith(prefix + '-00')), None)
    return pick('desktop'), pick('mobile')


# Promises of the page contract that a first screen can break. Measured on the render, never estimated.
# A composition that newly breaks one of these is not shipped: the page is broken for a visitor, or it lost words or links the source had.
BREAKING = ('h1-lines', 'h1-size', 'no-overflow', 'contrast', 'no-empty-screens', 'hero-line-wrap', 'seo-text-kept', 'seo-links-kept', 'picture-over-pixels')


def measured(page_path):
    """What the page contract finds failing on this page at 1440 and 390: {id: detail}. The whole page, not the first
    screen alone: a composition may set the page in another typeface, and every heading below follows it."""
    out = tempfile.mkdtemp(prefix='compose-contract-')
    for name in ('brief.json', 'inventory.json'):   # what the contract needs to grade the kept-words and kept-links promises, when the page sits in its job's folder
        source = os.path.join(os.path.dirname(os.path.abspath(page_path)), name)
        if os.path.isfile(source): shutil.copyfile(source, os.path.join(out, name))
    r = subprocess.run(['node', os.path.join(ROOT, 'lib/qa/contract.mjs'), page_path, '--dir', out], cwd=ROOT, capture_output=True, text=True, timeout=300)
    try:
        with open(os.path.join(out, 'contract.json')) as f: report = json.load(f)
    except (OSError, ValueError): raise RuntimeError('the contract could not grade the page: ' + (r.stderr or r.stdout)[-200:])
    return {f['id']: f['detail'] for f in report.get('failed', [])}


def measure_hero(page_path):
    """What only a browser knows about this page's first screen (lib/compose/measure.mjs): the real width of the headline's
    lines and words in the face the page loads, hand-broken lines that did not stay on one line, where the first button ends."""
    r = subprocess.run(['node', os.path.join(HERE, 'measure.mjs'), page_path], cwd=ROOT, capture_output=True, text=True, timeout=180)
    try: return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError): raise RuntimeError('the first screen could not be measured: ' + (r.stderr or r.stdout)[-200:])


def backdrop_findings(page_path):
    """Promises of a first screen whose picture is its ground, measured on the render (lib/compose/picmeasure.mjs): the
    picture is within its pixels, and the words read against what is really behind them."""
    r = subprocess.run(['node', os.path.join(HERE, 'picmeasure.mjs'), page_path], cwd=ROOT, capture_output=True, text=True, timeout=240)
    try: seen = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError): raise RuntimeError('the backdrop could not be measured: ' + (r.stderr or r.stdout)[-200:])
    found = {}
    for view in ('desktop', 'mobile'):
        for s in seen.get(view) or []:
            if s.get('form') != 'hero-backdrop': continue
            if isinstance(s.get('scale'), (int, float)) and s['scale'] > s.get('limit', 1.35) + 0.02: found[f'{view}-hero-picture-over-pixels'] = f'the backdrop is drawn at {s["scale"]:.2f}× its pixels (limit {s.get("limit", 1.35):g}×): this photograph cannot carry the whole screen'
            c = s.get('contrast')
            if c and c['ratio'] < c['need']: found[f'{view}-hero-words-on-picture-contrast'] = f'"{c["text"]}" reads at {c["ratio"]:.1f}:1 against the picture behind it and needs {c["need"]:g}:1: move the words to a quieter part of the picture, change "focal", tone the picture ("mono"), or give the text a "plate"'
    return found


CUT_BY_FOLD = 0.2   # the share of a first-screen picture that may hang under the fold before it reads as cut off


def hero_findings(seen):
    """Promises of a first screen that the page contract does not grade, from measure_hero()."""
    found = {}
    for view in ('desktop', 'mobile'):
        v = (seen or {}).get(view) or {}
        for w in v.get('wrapped') or []:
            found[f'{view}-hero-line-wrap'] = f'line {w.get("line")} of the headline ("{str(w.get("text"))[:40]}") does not stay on one line in its columns' + (f' ({w["over"]} px too wide)' if w.get('over') else '')
    d = (seen or {}).get('desktop') or {}
    if isinstance(d.get('actions_bottom'), (int, float)) and isinstance(d.get('fold'), (int, float)) and d['actions_bottom'] > d['fold']:
        found['hero-actions-under-fold'] = f'at 1440×900 the first button ends at {round(d["actions_bottom"])} px: under the fold'
    for p in d.get('pictures') or []:   # a picture the fold cuts through reads as an accident: either it is in the first screen or it is plainly below it
        try: top, bottom, fold = float(p['top']), float(p['bottom']), float(d['fold'])
        except (KeyError, TypeError, ValueError): continue
        under = (bottom - fold) / (bottom - top) if bottom > top else 0
        if top < fold - 40 and under > CUT_BY_FOLD:
            found['hero-picture-cut-by-fold'] = (f'at 1440×900 the picture "{p.get("id")}" runs from {round(top)} to {round(bottom)} px down the page: {round(under * 100)}% of it is under the fold. '
                                                 'Put it beside the headline instead of under it, give it fewer rows or a wider ratio, or shorten what stands above it')
    return found


def fit(page_html, ir, images, folder):
    """The composition with its headline measured: drawn into the page, measured in a browser, the widths written on the
    headline node as `fit`. The renderer then sizes the headline from the measurement instead of an estimate. Returns the
    composition unchanged when there is nothing to measure or the measurement does not validate."""
    content = CONTENT.from_page(page_html, images or []); page, report = IR.transplant(page_html, ir, images)
    if not report['drawn']: return ir
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=folder) as f: f.write(page); drawn = f.name
    try: seen = measure_hero(drawn)
    finally: os.unlink(drawn)
    measured_fit = (seen or {}).get('fit')
    if not isinstance(measured_fit, dict): return ir
    fitted = json.loads(json.dumps(ir))
    for node in fitted['hero']['nodes']:
        if node.get('t') == 'text' and node.get('as') == 'h1': node['fit'] = {'line': measured_fit.get('line'), 'word': measured_fit.get('word')}
    return fitted if not V.validate(fitted, content) else ir


def veil(page_html, ir, images, folder):
    """A composition whose first screen stands on a backdrop, with the veil the render asks for: drawn, measured, and when
    the words do not read against what is really behind them the scrim is made deep — by rule, without asking again."""
    ground = [n for n in ir['hero']['nodes'] if isinstance(n, dict) and n.get('bleed') == 'full' and n.get('scrim') is True]
    if not ground: return ir
    page, report = IR.transplant(page_html, ir, images)
    if not report['drawn']: return ir
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=folder) as f: f.write(page); drawn = f.name
    try: found = backdrop_findings(drawn)
    finally: os.unlink(drawn)
    if not any('words-on-picture' in k for k in found): return ir
    deeper = json.loads(json.dumps(ir))
    for node in deeper['hero']['nodes']:
        if node.get('bleed') == 'full': node['scrim'] = 'deep'
    return deeper


def _directed(direction):
    """What the page has already decided, as the first thing a composer reads: the direction set with the first screen and
    what the composers before this one chose. Words for a model only — nothing of it reaches the page."""
    return [{"type": "text", "text": "THE PAGE'S DIRECTION — decided with its first screen; what you compose continues it, it does not start again:\n" + str(direction)[:1400]}] if direction else []


def _pruned(doc, key, errors, check):
    """A document for the sections below the first screen, without the entries the validator still refuses after its
    reasons went back once: (document or None, [section ids left as the template drew them]). One wrong entry costs its
    own section, not the others — but what is left is validated whole again, and a fault of the document itself costs all."""
    named = {e['at'][len(key) + 1:-1] for e in errors if e['at'].startswith(key + '[') and e['at'].endswith(']')}
    entries = doc.get(key) if isinstance(doc, dict) else None
    if not named or len(named) != len({e['at'] for e in errors}) or not isinstance(entries, list): return None, []
    kept = [x for x in entries if isinstance(x, dict) and x.get('section') not in named]
    if not kept or len(kept) == len(entries): return None, []
    smaller = dict(doc, **{key: kept})
    return (smaller, sorted(named)) if not check(smaller) else (None, [])


def _image_block(path, size=1100):
    from PIL import Image
    im = Image.open(path).convert('RGB'); im.thumbnail((size, size)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=74)
    return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}


def _to_ir(answer):
    """The composition document from the tool answer. A model sometimes hands a list or object back as its JSON text:
    that is read, never guessed at; anything else wrong is left for the validator to name."""
    def read(value):
        if isinstance(value, str) and value.strip()[:1] in '[{':
            try: return json.loads(value)
            except ValueError: return value
        return value
    hero = {}
    for key in ('height', 'rows', 'gap', 'nodes'):
        if answer.get(key) is not None: hero[key] = read(answer[key])
    if isinstance(hero.get('nodes'), list):   # `fit` is a measurement the loop takes, never something a model states
        hero['nodes'] = [{k: v for k, v in n.items() if k != 'fit'} if isinstance(n, dict) else n for n in hero['nodes']]
    order = read(answer.get('phone_order'))
    if order is not None: hero['sm'] = {'order': order}
    if answer.get('typeface') not in (None, '', 'page'):   # "page" is the page's own face: nothing to set
        hero['face'] = {'id': answer['typeface'], **({'weight': answer['weight']} if answer.get('weight') is not None else {}), **({'case': answer['case']} if answer.get('case') else {})}
    system = {role: answer[field] for role, field in (('body', 'body_face'), ('label', 'label_face')) if answer.get(field) not in (None, '', 'page')}
    if system: hero['type'] = system   # the faces of the running text and the small print: with the display face, the page's type system
    return {'ir': V.VERSION, 'note': str(answer.get('concept') or '')[:300], 'hero': hero}

LEADS = (
    ('A', "THIS CONCEPT — type leads. The headline is the picture: its face, its breaks, its size. A picture is in support — smaller, lower, held to one side. When the product's own screen or a photograph worth showing is on offer it stays on the screen in that supporting role; only when nothing offered deserves the place is there none."),
    ('B', "THIS CONCEPT — the picture leads. One photograph, a stack, or the product's own screen is given real room, and the headline answers it rather than competing with it."),
    ('C', "THIS CONCEPT — the one neither obvious arrangement would reach: an unusual split of the screen, a crossing, a jump in scale, the pieces hung from one unexpected edge. It still has to be true to this business."),
)
# With no picture worth placing, the second concept is a second voice rather than a second arrangement of nothing.
LEAD_WITHOUT_PICTURES = "THIS CONCEPT — type leads again, in another voice: a different face and a different structure from the one you would reach for first. If that was a serif set quietly, this is a grotesque set loud, or the reverse."

JURY = """You are the creative director of a small studio. Up to three first screens were composed for the same business from the same words, buttons and pictures. You see each as it renders, at 1440 px and on a phone, with what was measured on it. One ships.
Choose the one a visitor would remember and that is true to this business — not the safest. A screen that only rearranges a template is the wrong choice even when nothing is wrong with it. A screen that breaks something measured can still be chosen when the break is small and can be fixed: say what to fix.
The page is graded on showing a picture or the product in its first screen. A screen that shows none is the right choice only when nothing on offer is worth showing; if you choose one, say why nothing was.
Answer by calling choose_concept."""
JURY_TOOL = {"name": "choose_concept", "description": "Which first screen ships.", "input_schema": {"type": "object", "required": ["choice", "reason"], "properties": {
    "choice": {"type": "string", "enum": ["A", "B", "C"]},
    "reason": {"type": "string", "description": "one sentence: why this one, for this business"},
    "improve": {"type": "string", "description": "the one thing the chosen screen should change before it ships; empty when nothing"}}}}


def _broken(found): return [k for k in (found or {}) if any(b in k for b in BREAKING)]
def _standing(found):
    """How a measured composition stands, for comparison: (broken promises, other findings) — leaving a picture out is a choice, not a finding."""
    return (len(_broken(found)), len([k for k in (found or {}) if not any(b in k for b in BREAKING) and 'first-screen-visual' not in k]))


def compose(page_html, images, job_dir=None, page_path=None, model=None, review=True, ask=None, concepts=1):
    """Compose, correct once, look and revise once. Returns the last composition that validates, or none.
    With concepts=3 (and a page to draw on) three compositions are written from three different leads, each drawn and
    measured, and a creative director chooses among the renders; the chosen one is then revised once like any other.
    `ask(system, content, tool, model=..., max_tokens=...)` is the model call; it defaults to the swarm's and is injectable for tests."""
    if ask is None:
        import agents; ask = agents.ask
    content = CONTENT.from_page(page_html, images or [])
    if face_locked(job_dir, content): content['page']['face_locked'] = True
    text, pictures = brief(content, job_dir)
    material = [{"type": "text", "text": text}]
    for address, m in pictures:
        data = _thumb(m['src'])
        if data: material += [{"type": "text", "text": f'PICTURE {address}'}, {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": data}}]
    if page_path:
        try:
            shots = hero_shots(page_path)
            if shots[0]: material += [{"type": "text", "text": "THE TEMPLATE'S FIRST SCREEN (same material; this is the page's typeface and colours — yours will use them too):"}, _image_block(shots[0])]
        except Exception as e: material.append({"type": "text", "text": f'(the template\'s first screen could not be pictured: {str(e)[:80]})'})
    log, wishes, findings, best = [], [], None, None
    several = concepts >= 3 and bool(page_path)

    def attempt(stage, extra):
        """One model call → (composition or None, the validator's errors, this call's entry in the log)."""
        answer = ask(SYSTEM, material + extra + [{"type": "text", "text": "Call write_composition."}], TOOL, model=model, max_tokens=6000)
        if not isinstance(answer, dict):
            entry = {'stage': stage, 'errors': ['no composition returned']}; log.append(entry)
            return None, [{'code': 'IR000', 'at': 'answer', 'message': 'no composition returned'}], entry
        ir = _to_ir(answer); errors = V.validate(ir, content)
        for w in answer.get('wishes') or []:
            if isinstance(w, dict) and (w.get('missing') or w.get('intent')): wishes.append({'intent': str(w.get('intent') or '')[:200], 'missing': str(w.get('missing') or '')[:120]})
        entry = {'stage': stage, 'concept': ir['note'], 'errors': [f"{e['code']} {e['at']}: {e['message']}" for e in errors], **({'refused': ir['hero']} if errors else {})}; log.append(entry)
        if isinstance(answer.get('page_direction'), str) and answer['page_direction'].strip(): entry['direction'] = ' '.join(answer['page_direction'].split())[:900]
        return ir, errors, entry

    def draft(label='', lead=None):
        """Compose and, when the validator refuses it, correct once. → (composition or None, its log entry)."""
        tag = f':{label}' if label else ''; extra = [{"type": "text", "text": lead}] if lead else []
        ir, errors, entry = attempt('compose' + tag, extra)
        if errors and ir is not None:
            problems = '\n'.join(f"- {e['code']} at {e['at']}: {e['message']}" for e in errors[:12])
            ir, errors, entry = attempt('correct' + tag, extra + [{"type": "text", "text": "YOUR PREVIOUS COMPOSITION WAS REFUSED:\n" + json.dumps(ir['hero'], ensure_ascii=False) + "\nReasons:\n" + problems + "\nKeep the idea; fix exactly these."}])
        return (ir if ir is not None and not errors else None), entry

    if several:
        leads = [(label, LEAD_WITHOUT_PICTURES if label == 'B' and not pictures else lead) for label, lead in LEADS]
        with ThreadPoolExecutor(len(leads)) as pool: drafts = list(pool.map(lambda l: (l[0],) + draft(l[0], l[1]), leads))
        candidates = [{'label': label, 'ir': ir, 'entry': entry} for label, ir, entry in drafts if ir is not None]
    else:
        ir, entry = draft()
        candidates = [{'label': '', 'ir': ir, 'entry': entry}] if ir is not None else []
    chosen = candidates[0] if candidates else None; best = chosen['ir'] if chosen else None; verdict = None

    if best and page_path:
        folder = os.path.dirname(os.path.abspath(page_path))
        def look_at(candidate):
            """Draw the candidate next to the page, picture it and grade it; what it newly breaks against the template's own page."""
            page, _ = IR.transplant(page_html, candidate, images)
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=folder) as f: f.write(page); drawn = f.name
            try:
                shots_ = hero_shots(drawn) if review else (None, None)
                found = {**measured(drawn), **hero_findings(measure_hero(drawn))}
                if any(isinstance(n, dict) and n.get('bleed') == 'full' for n in candidate['hero']['nodes']): found.update(backdrop_findings(drawn))
            finally: os.unlink(drawn)
            return shots_, {k: v for k, v in found.items() if k not in baseline}
        def seen(candidate):
            """Measure the candidate's headline, draw it, picture it, grade it — in place, on the candidate's own record."""
            try:
                candidate['ir'] = veil(page_html, fit(page_html, candidate['ir'], images, folder), images, folder)
                candidate['shots'], candidate['findings'] = look_at(candidate['ir']); candidate['entry']['measured'] = candidate['findings']
            except Exception as e: candidate['failed'] = str(e)[:160]
            return candidate
        def shown(candidate, title):
            """What the model is shown of a drawn composition: the document, the two pictures, what was measured."""
            blocks = [{"type": "text", "text": title + "\n" + json.dumps(candidate['ir']['hero'], ensure_ascii=False)}]
            desktop, mobile = candidate.get('shots') or (None, None)
            if desktop: blocks.append(_image_block(desktop))
            if mobile: blocks += [{"type": "text", "text": "On a phone:"}, _image_block(mobile, 700)]
            found = candidate.get('findings') or {}
            must = {k: v for k, v in found.items() if any(b in k for b in BREAKING)}; other = {k: v for k, v in found.items() if k not in must}
            if must: blocks.append({"type": "text", "text": "MEASURED ON THIS RENDER — your composition breaks these; fix them, or it is not shipped:\n" + '\n'.join(f'- {k}: {v}' for k, v in must.items())})
            if other: blocks.append({"type": "text", "text": "ALSO MEASURED — the page is graded on these too. They are yours to weigh: change the composition only where it gets better for it. "
                                                              "A first screen without a picture is right when no picture offered is good enough; never place a document, a notice or a logo sheet to have one.\n" + '\n'.join(f'- {k}: {v}' for k, v in other.items())})
            return blocks
        try:
            baseline = {**measured(page_path), **hero_findings(measure_hero(page_path))}
            if several and len(candidates) > 1:
                with ThreadPoolExecutor(len(candidates)) as pool: list(pool.map(seen, candidates))
                drawn = [c for c in candidates if 'failed' not in c]
                if not drawn: raise RuntimeError(candidates[0]['failed'])
                sound = [c for c in drawn if not _broken(c['findings'])] or drawn
                chosen = min(sound, key=lambda c: (_standing(c['findings']), c['label']))   # the fallback when nobody chooses: the least broken, then A before B before C
                if review and len(sound) > 1:
                    table = [{"type": "text", "text": text}]
                    for c in sound: table += shown(c, f"CONCEPT {c['label']} — {c['ir']['note']}\nAS DRAWN, at 1440 px:")
                    tool = json.loads(json.dumps(JURY_TOOL)); tool['input_schema']['properties']['choice']['enum'] = [c['label'] for c in sound]
                    answer = ask(JURY, table + [{"type": "text", "text": "Call choose_concept."}], tool, model=model, max_tokens=800)
                    picked = next((c for c in sound if isinstance(answer, dict) and c['label'] == answer.get('choice')), None)
                    verdict = {'choice': (picked or chosen)['label'], 'reason': str((answer or {}).get('reason') or '')[:300] if picked else 'no valid choice was returned: the least broken stands', 'improve': str((answer or {}).get('improve') or '')[:300] if picked else ''}
                    if picked: chosen = picked
                    log.append({'stage': 'jury', 'errors': [] if picked else ['no valid choice returned'], **verdict})
            else:
                seen(chosen)
                if 'failed' in chosen: raise RuntimeError(chosen['failed'])
            best, findings = chosen['ir'], chosen['findings']
            if review:
                look = shown(chosen, "YOUR COMPOSITION, AS DRAWN. First at 1440 px, then on a phone:")
                if verdict and verdict.get('reason'): look.append({"type": "text", "text": "The studio chose this one of its concepts: " + verdict['reason'] + (" Before it ships: " + verdict['improve'] if verdict.get('improve') else '')})
                look.append({"type": "text", "text": "Look at it as the art director. Does one thing dominate? Is anything cramped, drifting, awkwardly empty, clipped, or is the picture cropped off its subject? Is the headline the right size for its words? "
                                                        "Return the composition you would ship: revised where the picture or the measurements show a problem, unchanged if you would ship this."})
                revised, revised_errors, entry = attempt('revise', look)
                if revised is not None and not revised_errors:
                    second = seen({'label': chosen['label'], 'ir': revised, 'entry': entry})
                    if 'failed' in second: entry['errors'] = ['the revision could not be drawn and measured: kept the first']
                    elif _standing(second['findings']) > _standing(findings): entry['errors'] = ['revision measured worse than the first composition: kept the first']   # worse is: more broken, or as broken and more of the rest
                    else: best, findings = second['ir'], second['findings']
        except Exception as e: log.append({'stage': 'look', 'errors': ['review skipped: ' + str(e)[:160]]})
        if _broken(findings):  # correct and generic beats striking and broken: the page keeps the template's hero
            log.append({'stage': 'refuse', 'errors': [f'the composition breaks the page on the render ({", ".join(_broken(findings))}): not shipped']}); best = None
    said = [step for step in log if step.get('direction') and step.get('concept') == (best or {}).get('note')] or [step for step in log if step.get('direction')]
    direction = said[-1]['direction'] if best and said else None   # what the composer of the chosen first screen asked of the rest of the page
    result = {'ir': best, 'direction': direction, 'drawn': best is not None, 'attempts': sum(1 for step in log if step['stage'].split(':')[0] in ('compose', 'correct', 'revise', 'jury')), 'log': log, 'wishes': wishes, 'measured': findings}
    if several: result.update(concepts=[{'label': c['label'], 'concept': c['ir']['note'], 'measured': c.get('findings'), **({'failed': c['failed']} if 'failed' in c else {})} for c in candidates], chosen=chosen['label'] if chosen else None, verdict=verdict)
    return result


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2 or '--out' not in args: raise SystemExit(__doc__)
    page_path, images_path = args[0], args[1]; out = args[args.index('--out') + 1]
    job = args[args.index('--job') + 1] if '--job' in args else None
    with open(page_path, encoding='utf-8') as f: html = f.read()
    with open(images_path) as f: pictures_json = json.load(f)
    result = compose(html, pictures_json, job_dir=job, page_path=page_path, model=os.environ.get('COMPOSE_MODEL') or None, review='--no-review' not in args,
                     concepts=int(args[args.index('--concepts') + 1]) if '--concepts' in args else 1)
    if result['ir']:
        with open(out, 'w', encoding='utf-8') as f: json.dump(result['ir'], f, indent=1, ensure_ascii=False)
    with open(os.path.splitext(out)[0] + '.log.json', 'w', encoding='utf-8') as f: json.dump({k: result[k] for k in ('drawn', 'attempts', 'log', 'wishes')}, f, indent=1, ensure_ascii=False)
    print(json.dumps({'drawn': result['drawn'], 'attempts': result['attempts'], 'concept': (result['ir'] or {}).get('note'), 'wishes': len(result['wishes'])}, ensure_ascii=False))
    raise SystemExit(0 if result['drawn'] else 1)
