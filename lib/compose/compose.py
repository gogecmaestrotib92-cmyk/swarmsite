"""compose.py — a model writes the hero composition; this file keeps it honest.

The model is an art director with fixed material: the production hero's words, buttons and pictures (content.py). It
sees the pictures, the hero the template made, and the measured principles of the references that fit this business
(design_dna). It answers with a composition and nothing else. The loop around it:

  1. compose        — one call; the answer is validated (validate.py)
  2. correct        — a refused composition goes back once with the validator's reasons
  3. look and revise — the valid composition is rendered and screenshotted at 1440 and 390; the model sees its own
                       page and may revise once. A revision that does not validate is dropped; the valid one stands.

The model never writes text, links or markup: the format has no field for them. What it wishes the format could do is
collected in `wishes` — the backlog for new primitives — and never drawn.

  compose(page_html, images, job_dir=None, page_path=None, model=None) → {'ir', 'drawn', 'attempts', 'log', 'wishes'}
  python3 lib/compose/compose.py <page.html> <images.json> --out composition.json [--job <job dir>] [--no-review]
Needs ANTHROPIC_API_KEY. Every call is charged to the job budget when SWARM_JOB_DIR is set."""
import base64, io, json, os, subprocess, sys, tempfile

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
- A screenshot of a product is shown whole, in a frame. It is never cropped, bled or written over.
- The actions sit where the eye lands after the headline and the lede.
- Leave real empty space. A first screen that fills every cell is a template.
- On a phone the pieces stack. Order them so the headline is first or second and the first action comes before a long scroll.

REFERENCE PRINCIPLES, when given, are measurements from reference sites that fit this business. Use them as principles — how large, how far off-centre, how much of the screen a picture takes — never as a layout to reproduce.

THE FORMAT
The hero is a grid of 12 columns and the rows you declare. A node sits at "at": {"col": [start, end], "row": n or [start, end]} using grid lines: columns 1..13, rows 1..(number of rows + 1); the end line is not included, so "col": [1, 7] is the left half.
- the hero: "height": auto|screen|tall, "rows": 1–6 of auto|1fr|2fr|min, "gap": sm|md|lg, "nodes": [...], "phone_order": [every node id, in the order they stack on a phone]. It sits on the page's own background and uses the page's own typeface and colours (you see them in the template's first screen).
- text node: {"id", "t": "text", "src": a text address, "as": label|h1|lede, "at"}. hero.h1 is always "as": "h1"; hero.lede is "lede"; hero.category and hero.fact are "label".
  h1 takes "size": xl|xxl|mega (mega is about 12% of the viewport width: for short headlines) and "measure" 6–40 (characters per line). lede takes "size": md|lg and "measure" 20–70. A label takes neither.
  Optional "align": start|center|end, and "plate": paper|ink when the text crosses a picture.
- actions node: {"id", "t": "actions", "src": [one or two action addresses], "at", optional "align"}.
- media node: {"id", "t": "media", "src": a picture address, "fit": cover|contain, "ratio": one of 1/1 4/5 3/4 2/3 4/3 3/2 16/9 16/10 21/9, "focal": [x, y] each 0–1, "bleed": none|left|right, "frame": none|browser|paper, "scrim": true|false, "at"}.
  "bleed" runs the picture to the screen edge and is allowed only from column 1 (left) or to column line 13 (right). A screenshot must be "fit": "contain" with a "frame" and no bleed or scrim.
- shape node: {"id", "t": "shape", "kind": "rule", "at"} — a hairline.
- "at" may add "z": 0–4 (higher is in front) and "self": start|center|end|stretch (where the node sits inside its rows).
Rules the renderer enforces — a composition that breaks one is refused whole:
- Every text address and every action address is placed exactly once. Pictures are optional.
- A composition contains no words and no links: there is no field for them.
- Text never shares a cell with other text or with the buttons. Text or buttons over a picture need a plate on the text or a scrim on the picture.
- A photograph is never shown wider or taller than 1.35 times its pixels; a screenshot never larger than its pixels. Column widths are given below.
- In the list of nodes the h1 comes before the lede and the actions.
- A picture you place should register: at least one spans five columns or more (the page is graded on showing a picture or the product at 30% of the screen width in the first screen when it has one).
- The headline takes at most three lines at 1440 px. You cannot see line breaks in advance: choose size and measure for the words you have, and you will be told what was measured on the render.
Answer by calling write_composition. In "concept", say in one sentence what the first screen does and why it suits this business. In "wishes", list anything you wanted that the format cannot do — it is not drawn, it is how the format grows."""

AT = {"type": "object", "required": ["col", "row"], "properties": {
    "col": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
    "row": {"anyOf": [{"type": "integer"}, {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2}]},
    "z": {"type": "integer"}, "self": {"type": "string", "enum": list(V.SELF)}}}
NODE = {"type": "object", "required": ["id", "t", "at"], "properties": {
    "id": {"type": "string"}, "t": {"type": "string", "enum": ["text", "actions", "media", "shape"]},
    "src": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2}]},
    "as": {"type": "string", "enum": list(V.ROLES)}, "size": {"type": "string", "enum": ["md", "lg", "xl", "xxl", "mega"]}, "measure": {"type": "integer"},
    "align": {"type": "string", "enum": list(V.ALIGN)}, "plate": {"type": "string", "enum": list(V.PLATES)},
    "fit": {"type": "string", "enum": list(V.FITS)}, "ratio": {"type": "string", "enum": list(V.RATIOS)},
    "focal": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}, "bleed": {"type": "string", "enum": list(V.BLEEDS)},
    "frame": {"type": "string", "enum": list(V.FRAMES)}, "scrim": {"type": "boolean"}, "kind": {"type": "string", "enum": ["rule"]}, "at": AT}}
# Flat on purpose: with the hero as one nested object the first answer came back as broken text; its fields are top-level here.
TOOL = {"name": "write_composition", "description": "The composition of the first screen. The hero's fields are given directly: height, rows, gap, nodes, phone_order.", "input_schema": {"type": "object", "required": ["concept", "rows", "nodes", "phone_order"], "properties": {
    "concept": {"type": "string", "description": "one sentence: what this first screen does and why it suits this business"},
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
        if m.get('gen') or address in content.get('used_elsewhere', []): continue
        if not isinstance(m.get('w'), (int, float)) or m['w'] < 480: continue
        if address != 'hero.picture' and any(m['src'] == content['media'][o]['src'] for o in ('hero.picture',) if o in content['media']): continue
        out.append((address, m))
    out.sort(key=lambda x: (x[0] != 'hero.picture', -(x[1]['w'] * (x[1].get('h') or 1))))
    return out[:limit]


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
        lines.append(f'- {address}: {int(m["w"])}×{int(m["h"])} px {kind}' + (' — the picture the template used in its hero' if address == 'hero.picture' else ''))
    lines.append(f'WIDTHS at a 1440 px viewport: one column is about {round(col)} px and gaps are 24 px, so n columns span n×{round(col)} + (n−1)×24 px; '
                 f'a bleed adds about {round(page["frame"] + max(0, (1440 - page["container"]) / 2))} px.')
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
HERO_PROMISES = ('h1-', 'first-screen-visual', 'no-overflow', 'contrast', 'no-upscaled-images', 'no-empty-screens', 'no-duplicate-images')
BREAKING = ('h1-lines', 'no-overflow', 'contrast', 'no-empty-screens')   # a composition that newly breaks one of these is not shipped


def measured(page_path):
    """What the page contract finds on this page at 1440 and 390, limited to what a first screen can break: {id: detail}."""
    out = tempfile.mkdtemp(prefix='compose-contract-')
    r = subprocess.run(['node', os.path.join(ROOT, 'lib/qa/contract.mjs'), page_path, '--dir', out], cwd=ROOT, capture_output=True, text=True, timeout=300)
    try:
        with open(os.path.join(out, 'contract.json')) as f: report = json.load(f)
    except (OSError, ValueError): raise RuntimeError('the contract could not grade the page: ' + (r.stderr or r.stdout)[-200:])
    return {f['id']: f['detail'] for f in report.get('failed', []) if any(k in f['id'] for k in HERO_PROMISES)}


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
    order = read(answer.get('phone_order'))
    if order is not None: hero['sm'] = {'order': order}
    return {'ir': V.VERSION, 'note': str(answer.get('concept') or '')[:300], 'hero': hero}

def compose(page_html, images, job_dir=None, page_path=None, model=None, review=True, ask=None):
    """Compose, correct once, look and revise once. Returns the last composition that validates, or none.
    `ask(system, content, tool, model=..., max_tokens=...)` is the model call; it defaults to the swarm's and is injectable for tests."""
    if ask is None:
        import agents; ask = agents.ask
    content = CONTENT.from_page(page_html, images or []); text, pictures = brief(content, job_dir)
    material = [{"type": "text", "text": text}]
    for address, m in pictures:
        data = _thumb(m['src'])
        if data: material += [{"type": "text", "text": f'PICTURE {address}'}, {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": data}}]
    shots = None
    if page_path:
        try:
            shots = hero_shots(page_path)
            if shots[0]: material += [{"type": "text", "text": "THE TEMPLATE'S FIRST SCREEN (same material; this is the page's typeface and colours — yours will use them too):"}, _image_block(shots[0])]
        except Exception as e: material.append({"type": "text", "text": f'(the template\'s first screen could not be pictured: {str(e)[:80]})'})
    log, wishes, best = [], [], None

    def attempt(stage, extra):
        answer = ask(SYSTEM, material + extra + [{"type": "text", "text": "Call write_composition."}], TOOL, model=model, max_tokens=6000)
        if not isinstance(answer, dict): log.append({'stage': stage, 'errors': ['no composition returned']}); return None, [{'code': 'IR000', 'at': 'answer', 'message': 'no composition returned'}]
        ir = _to_ir(answer); errors = V.validate(ir, content)
        for w in answer.get('wishes') or []:
            if isinstance(w, dict) and (w.get('missing') or w.get('intent')): wishes.append({'intent': str(w.get('intent') or '')[:200], 'missing': str(w.get('missing') or '')[:120]})
        log.append({'stage': stage, 'concept': ir['note'], 'errors': [f"{e['code']} {e['at']}: {e['message']}" for e in errors], **({'refused': ir['hero']} if errors else {})})
        return ir, errors

    ir, errors = attempt('compose', [])
    if errors and ir is not None:
        problems = '\n'.join(f"- {e['code']} at {e['at']}: {e['message']}" for e in errors[:12])
        ir, errors = attempt('correct', [{"type": "text", "text": "YOUR PREVIOUS COMPOSITION WAS REFUSED:\n" + json.dumps(ir['hero'], ensure_ascii=False) + "\nReasons:\n" + problems + "\nKeep the idea; fix exactly these."}])
    if ir is not None and not errors: best = ir
    findings = None
    if best and page_path:
        folder = os.path.dirname(os.path.abspath(page_path))
        def look_at(candidate):
            """Draw the candidate next to the page, picture it and grade it; what it newly breaks against the template's own page."""
            page, _ = IR.transplant(page_html, candidate, images)
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=folder) as f: f.write(page); drawn = f.name
            try:
                shots_ = hero_shots(drawn) if review else (None, None)
                found = measured(drawn)
            finally: os.unlink(drawn)
            return shots_, {k: v for k, v in found.items() if k not in baseline}
        try:
            baseline = measured(page_path)
            (desktop, mobile), findings = look_at(best)
            log[-1]['measured'] = findings
            if review:
                look = [{"type": "text", "text": "YOUR COMPOSITION, AS DRAWN. First at 1440 px, then on a phone:\n" + json.dumps(best['hero'], ensure_ascii=False)}]
                if desktop: look.append(_image_block(desktop))
                if mobile: look += [{"type": "text", "text": "On a phone:"}, _image_block(mobile, 700)]
                if findings: look.append({"type": "text", "text": "MEASURED ON THIS RENDER — your composition newly breaks these promises of the page; fix them:\n" + '\n'.join(f'- {k}: {v}' for k, v in findings.items())})
                look.append({"type": "text", "text": "Look at it as the art director. Does one thing dominate? Is anything cramped, drifting, awkwardly empty, clipped, or is the picture cropped off its subject? Is the headline the right size for its words? "
                                                        "Return the composition you would ship: revised where the picture or the measurements show a problem, unchanged if you would ship this."})
                revised, revised_errors = attempt('revise', look)
                if revised is not None and not revised_errors:
                    _, revised_findings = look_at(revised)
                    log[-1]['measured'] = revised_findings
                    worse = len([k for k in revised_findings if any(b in k for b in BREAKING)]) > len([k for k in findings if any(b in k for b in BREAKING)]) or (len(revised_findings) > len(findings))
                    if worse: log[-1]['errors'] = ['revision measured worse than the first composition: kept the first']
                    else: best, findings = revised, revised_findings
        except Exception as e: log.append({'stage': 'look', 'errors': ['review skipped: ' + str(e)[:160]]})
        broken = [k for k in (findings or {}) if any(b in k for b in BREAKING)]
        if broken:  # correct and generic beats striking and broken: the page keeps the template's hero
            log.append({'stage': 'refuse', 'errors': [f'the composition breaks the page on the render ({", ".join(broken)}): not shipped']}); best = None
    return {'ir': best, 'drawn': best is not None, 'attempts': sum(1 for step in log if step['stage'] in ('compose', 'correct', 'revise')), 'log': log, 'wishes': wishes, 'measured': findings}


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2 or '--out' not in args: raise SystemExit(__doc__)
    page_path, images_path = args[0], args[1]; out = args[args.index('--out') + 1]
    job = args[args.index('--job') + 1] if '--job' in args else None
    with open(page_path, encoding='utf-8') as f: html = f.read()
    with open(images_path) as f: pictures_json = json.load(f)
    result = compose(html, pictures_json, job_dir=job, page_path=page_path, model=os.environ.get('COMPOSE_MODEL') or None, review='--no-review' not in args)
    if result['ir']:
        with open(out, 'w', encoding='utf-8') as f: json.dump(result['ir'], f, indent=1, ensure_ascii=False)
    with open(os.path.splitext(out)[0] + '.log.json', 'w', encoding='utf-8') as f: json.dump({k: result[k] for k in ('drawn', 'attempts', 'log', 'wishes')}, f, indent=1, ensure_ascii=False)
    print(json.dumps({'drawn': result['drawn'], 'attempts': result['attempts'], 'concept': (result['ir'] or {}).get('note'), 'wishes': len(result['wishes'])}, ensure_ascii=False))
    raise SystemExit(0 if result['drawn'] else 1)
