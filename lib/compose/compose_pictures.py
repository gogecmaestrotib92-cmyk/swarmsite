"""compose_pictures.py — a model decides what each picture below the first screen does; this file keeps it honest.

The same loop as for the first screen (compose.py) and the lists (compose_lists.py): the model sees each picture
section as the template drew it, what the picture is (its pixels, photograph or screenshot) and which forms are open
to it, and answers with a picture composition (pictures.py) and nothing else. The validator's reasons go back once.
What validates is then settled against a real render (picmeasure.mjs) by rule, not by asking again: a veil that
leaves the words unreadable over the picture is thickened, a heading that runs out of its block is set smaller, a
picture drawn past its pixels is given less room, and a section that still fails goes back to the template's form.
The drawn sections are pictured and the whole page graded by the contract; what the composition newly breaks goes
back once with the pictures; one that still breaks the page is refused whole.

  settle(page_html, doc, images, folder)   → (doc or None, [what was changed and why], findings that remain)
  compose(page_html, page_path, images=None, model=None, review=True, ask=None) → {'doc', 'drawn', 'attempts', 'log', 'measured'}
Needs ANTHROPIC_API_KEY for the default model call. Every call is charged to the job budget when SWARM_JOB_DIR is set."""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'lib', 'swarm')); sys.path.insert(0, os.path.join(ROOT, 'lib'))
import compose as HERO
import compose_lists as LISTED
import content as CONTENT
import pictures as PICTURES
import validate as V

SYSTEM = """You are the art director of a small studio. The first screen of this page is composed. Below it, every section that shows a picture was drawn by a page-building template in the one way it has: the picture in a box and its words beside it. That is what makes a page look assembled rather than designed. You decide what each picture does instead. The words and the pictures are fixed: you choose a form, you do not write.

The one thing that must not be left on the page: a rectangle on one side and the words on the other. Decorating the rectangle — a frame, a tilt, a rounded corner, a coloured panel behind it — does not change what it is. On a designed page a picture never has a box of its own: it belongs to the look of its section.

How a picture belongs to its section:
- It has no visible edge. It fills the section (backdrop), or it runs off the screen and its inner edge dissolves into the section's ground while the heading reaches into it (bleed with "edge": "fade" and "overlap"), or the section takes the picture's own ground colour so that the picture simply stands in it (stage with "ground": "own" — offered when the picture's edges are one even colour: a product on white, a render on black, a screen on its own dark).
- Or it is cut by the type: the words sit in a notch cut out of its corner (card), or the picture is set into the heading itself, as tall as the capitals, like a word (inline) — the honest form for a small photograph, which cannot be made large.
- Or it is the whole width (panorama).
- offset — a picture cut and hung beside the words — and a stage on accent, ink or alt are the weakest forms: use them only when nothing above is open to the picture, and never twice on a page.

How a studio uses a picture:
- A picture is given a job. It is the ground the words stand on; or it runs off the edge of the screen from the top of the section to the bottom; or it crosses the page as a strip; or it carries the words on a card laid over its corner; or it is cut to a proportion that suits what it shows and hung off the line of the text; or it is set on a stage of colour like an object.
- The picture decides. A wide, atmospheric photograph with a quiet area wants to be a backdrop or a panorama. A photograph with one strong subject wants to bleed off an edge with the words beside it. A small photograph cannot be made large — it becomes a print: framed in paper, turned a few degrees, beside a very large heading. A screenshot, a document or a cover is an object: shown whole, on a stage.
- When the picture becomes the backdrop the words move to where the picture is quiet. Look at it: say where the words stand ("place") and set "focal" on its subject, so that the crop keeps the subject and the words do not sit on it.
- Sections that follow each other never take the same form on the same side. Alternate the side, vary the form, and let one idea run down the page.
- Many words (a list of rows, several paragraphs) do not stand in a narrow column beside a picture: put them under it (panorama, or stage with "side": "top").
- The heading grows when the picture is small or calm ("title": xl) and stays modest when the picture is loud or the words are many.
- A section you leave out stays as the template drew it. Leave one out only when the template's form is right for it.

THE FORMAT — call write_pictures with "concept" (one sentence: what the pictures do on this page) and "pictures": one object per section you recompose. Every object has "section" (its id, as given) and "form"; the other fields depend on the form. Each section lists the forms open to its picture — its pixels and its kind decide them; a form that is not listed for a section is refused.
- backdrop — the picture fills the section edge to edge and the words stand on it under a veil. "place": bottom-left | bottom-right | top-left | center | left | right (where the words stand). "height": md | lg | screen. "scrim": soft | mid | deep (the veil; it is thickened by rule if the words do not read).
- bleed — the picture runs off one edge of the screen, as tall as the section. "side": left | right (the picture's side). "cols": 5–7 of twelve. "height": md | lg. "align": start | center | end (the words, top to bottom). "edge": fade | hard — fade (the default) dissolves the picture's inner edge into the section; "overlap": 0 | 1 | 2 columns the words then reach into that dissolved edge, so heading and picture interlock (it is taken back by rule if the words do not read there).
- panorama — the picture crosses the whole screen as a strip. "ratio": 2/1 | 21/9 | 3/1. "words": above | below; the heading stands to the left and what it introduces to the right.
- card — a large picture with the words on a card laid over its inner corner. "side": the picture's side. "cols": 7–9. "ratio": 1/1 | 4/5 | 4/3 | 3/2 | 16/10 | 16/9. "anchor": top | middle | bottom (where the card lies). "bleed": true lets the picture run off its edge of the screen.
- offset — the picture cut to a proportion and hung beside the words. "side", "cols": 3–7, "ratio": own | 1/1 | 4/5 | 3/4 | 2/3 | 4/3 | 3/2 | 16/9 | 16/10 | 21/9, "shape": rect | soft | arch | circle | pill, "tilt": -4…4 degrees, "shadow": none | soft | hard, "frame": none | paper | browser, "drop": none | up | down (hung above or below the line of the words), "align".
- stage — the picture shown whole on a ground that runs off the screen edge. "side": left | right | top (top: the picture across the top of the section on its ground, the words under it in two columns — the form for a section with many words or rows), "cols": 5–8 (the picture's share), "ground": own | accent | ink | alt, "tilt": -3…3, "align", "height": auto | md | lg (auto: as tall as what it shows). With "ground": "own" the whole section takes the picture's own ground colour, the words turn to the colour that reads on it, and the picture has no panel and no edge.
- inline — the picture set into the section's heading like a word, as tall as its capitals. "at": start | end (of the heading), "shape": pill | soft | circle, "title": lg | xl. Photographs only; the heading becomes the picture's frame, so the heading is large.
On any form: "title": md | lg | xl (the heading's size), "enter": none | rise | clip | settle (how the picture arrives). On every form but stage: "tone": none | mono | duotone | tint, "grain": true, "focal": [x, y] each 0–1. On backdrop, bleed, panorama and card: "scroll": parallax.
A screenshot is evidence of the product: it is never cropped, toned or written over — stage or offset only. A composition that breaks a rule is refused whole and you are told why."""

FIELDS = ('side', 'cols', 'place', 'height', 'scrim', 'ratio', 'words', 'anchor', 'bleed', 'shape', 'tilt', 'shadow', 'frame', 'drop', 'align', 'ground', 'tone', 'grain', 'focal', 'title', 'enter', 'scroll', 'edge', 'overlap', 'at')
ENTRY = {"type": "object", "required": ["section", "form"], "properties": {
    "section": {"type": "string"}, "form": {"type": "string", "enum": list(PICTURES.FORMS)}, "side": {"type": "string", "enum": list(PICTURES.SIDES) + ["top"]}, "cols": {"type": "integer"},
    "place": {"type": "string", "enum": list(PICTURES.PLACES)}, "height": {"type": "string", "enum": ["auto"] + list(PICTURES.HEIGHTS)}, "scrim": {"type": "string", "enum": list(PICTURES.SCRIMS)},
    "ratio": {"type": "string"}, "words": {"type": "string", "enum": list(PICTURES.WORDS)}, "anchor": {"type": "string", "enum": list(PICTURES.ANCHORS)}, "bleed": {"type": "boolean"},
    "shape": {"type": "string", "enum": list(V.SHAPES)}, "tilt": {"type": "integer"}, "shadow": {"type": "string", "enum": list(V.SHADOWS)}, "frame": {"type": "string", "enum": list(PICTURES.FRAMES)},
    "drop": {"type": "string", "enum": list(PICTURES.DROPS)}, "align": {"type": "string", "enum": list(PICTURES.ALIGN)}, "ground": {"type": "string", "enum": list(PICTURES.GROUNDS)},
    "tone": {"type": "string", "enum": list(V.TONES)}, "grain": {"type": "boolean"}, "focal": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
    "edge": {"type": "string", "enum": list(PICTURES.EDGES)}, "overlap": {"type": "integer"}, "at": {"type": "string", "enum": ["start", "end"]},
    "title": {"type": "string", "enum": list(PICTURES.TITLES)}, "enter": {"type": "string", "enum": list(V.MEDIA_ENTER)}, "scroll": {"type": "string", "enum": list(V.MEDIA_SCROLL)}}}
TOOL = {"name": "write_pictures", "description": "What each picture below the first screen does.", "input_schema": {"type": "object", "required": ["concept", "pictures"], "properties": {
    "concept": {"type": "string", "description": "one sentence: what the pictures do on this page"},
    "pictures": {"type": "array", "minItems": 1, "maxItems": 12, "items": ENTRY}}}}
MAX_PICTURED = 6
BREAKING = HERO.BREAKING + ('picture-over-pixels', 'words-on-picture', 'heading-out', 'words-over-picture')
SMALLER = {'xl': 'lg', 'lg': 'md'}; THICKER = {'soft': 'mid', 'mid': 'deep'}; LOWER = {'screen': 'lg', 'lg': 'md'}; FLATTER = {'2/1': '21/9', '21/9': '3/1'}


def measure(page_path):
    """What only a browser knows about the composed picture sections of this page (lib/compose/picmeasure.mjs)."""
    r = subprocess.run(['node', os.path.join(HERE, 'picmeasure.mjs'), page_path], cwd=ROOT, capture_output=True, text=True, timeout=240)
    try: return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError): raise RuntimeError('the picture sections could not be measured: ' + (r.stderr or r.stdout)[-200:])


def problems(seen):
    """[(view, section id, kind, what was measured)] for the promises of a picture section that the page contract does not grade."""
    out = []
    for view in ('desktop', 'mobile'):
        for s in (seen or {}).get(view) or []:
            if s.get('missing'): continue
            if isinstance(s.get('scale'), (int, float)) and s['scale'] > s.get('limit', V.UPSCALE) + 0.02: out.append((view, s['id'], 'picture-over-pixels', f'the picture is drawn at {s["scale"]:.2f}× its pixels (limit {s.get("limit", V.UPSCALE):g}×)'))
            c = s.get('contrast')
            if c and c['ratio'] < c['need']: out.append((view, s['id'], 'words-on-picture', f'"{c["text"]}" reads at {c["ratio"]:.1f}:1 against the picture behind it and needs {c["need"]:g}:1'))
            if view == 'desktop' and s.get('heading_out', 0) > 2: out.append((view, s['id'], 'heading-out', f'the heading runs {s["heading_out"]} px out of its block of words'))
            if s.get('overlap', 0) > 400: out.append((view, s['id'], 'words-over-picture', 'the words lie on the picture in a form where they stand beside it'))
    return out


def findings_of(seen):
    """The same as {finding id: detail}, one per kind and view, naming the sections."""
    found = {}
    for view, sid, kind, detail in problems(seen):
        key = f'{view}-{kind}'; found[key] = (found[key] + '; ' if key in found else '') + f'section "{sid}": {detail}'
    return found


def _eased(entry, kind):
    """The entry changed by rule so that what was measured no longer holds, or None when the form has nothing left to give."""
    e = dict(entry); form = e['form']
    if kind == 'words-on-picture' and form == 'bleed':   # the words step back out of the picture's edge
        if not e.get('overlap'): return None
        e['overlap'] -= 1; return e
    if kind == 'words-on-picture':
        now = e.get('scrim', 'mid')
        if now not in THICKER: return None
        e['scrim'] = THICKER[now]; return e
    if kind == 'heading-out':
        now = e.get('title', 'md')
        if now not in SMALLER: return None
        e['title'] = SMALLER[now]; return e
    if kind == 'picture-over-pixels':
        if form in ('backdrop', 'bleed') and e.get('height', 'lg') in LOWER: e['height'] = LOWER[e.get('height', 'lg')]; return e
        if form == 'panorama' and e.get('ratio', '21/9') in FLATTER: e['ratio'] = FLATTER[e.get('ratio', '21/9')]; return e
        if form in ('card', 'offset', 'bleed') and e.get('cols', PICTURES.DEFAULT_COLS[form]) > PICTURES.COLS[form][0]: e['cols'] = e.get('cols', PICTURES.DEFAULT_COLS[form]) - 1; return e
    return None


def settle(page_html, doc, images, folder):
    """Draw the composition, measure it in a browser and ease by rule whatever the measurement shows, up to four times.
    → (the settled document, or None when no section is left; what was changed; the findings that remain)."""
    changes, seen = [], None
    for _ in range(4):
        if not doc or not doc.get('pictures'): return None, changes, {}
        page, report = PICTURES.transplant(page_html, doc, images)
        if not report['drawn']: return None, changes + ['refused after easing: ' + '; '.join(e['message'][:80] for e in report['errors'][:2])], {}
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=folder) as f: f.write(page); drawn = f.name
        try: seen = measure(drawn)
        finally: os.unlink(drawn)
        found = problems(seen)
        if not found: return doc, changes, {}
        entries = {e['section']: e for e in doc['pictures']}
        for view, sid, kind, detail in found:
            if sid not in entries: continue
            eased = _eased(entries[sid], kind)
            if eased is not None and not PICTURES.validate({'ir': V.VERSION, 'pictures': [eased]}, page_html, images):
                changes.append(f'{sid}: {kind} at {view} ({detail}) → {", ".join(f"{k} {entries[sid].get(k)}→{eased[k]}" for k in eased if eased[k] != entries[sid].get(k))}'); entries[sid] = eased
            else: changes.append(f'{sid}: {kind} at {view} ({detail}) → back to the template\'s form'); del entries[sid]
        doc = {**doc, 'pictures': [entries[e['section']] for e in doc['pictures'] if e['section'] in entries]}
    return (doc if doc.get('pictures') else None), changes, findings_of(seen)


def brief(page_html, images=None):
    """What may be recomposed, as text: every picture section with its picture, its words and the forms open to it, in the
    order of the page. → (text, [section ids])"""
    lines, ids = ['THE PAGE, top to bottom (sections whose picture you direct are marked ▸):'], []
    page = PICTURES.readable(page_html, images); tokens = CONTENT.page_of(page_html)
    for sec in PICTURES.SECTIONS.sections(page_html):
        known = page.get(sec['id']); kind = next((k for k in sec['classes'] if k not in ('sec', 'compact', 'pc', 'lc') and not k.startswith(('band-', 'pc-', 'lc-'))), 'section')
        if known and not isinstance(known[1], str):
            c = known[1]; pic = c['picture']; forms = PICTURES.open_forms(c, tokens)
            if not forms: lines.append(f'  "{sec["id"]}" — {kind} (its picture is too small for any other form)'); continue
            ids.append(sec['id'])
            opened = '; '.join(f'{f["form"]} (would draw it {f["box"][0]}×{f["box"][1]} px, {f["scale"]:.2f}× its pixels)' for f in forms)
            lines.append(f'▸ "{sec["id"]}" — on the {c["band"]} band. Picture: {pic["w"]}×{pic["h"]} px, {"a SCREENSHOT (evidence of the product)" if pic["shot"] else "a photograph or illustration"}'
                         + (f', described as "{pic["alt"][:90]}"' if pic['alt'] else '') + (f'; its edges are one even {"dark" if pic["ground"]["dark"] else "light"} colour (stage with "ground": "own" is open)' if pic.get('ground') else '; its edges are a scene (no ground of its own)') + f'. Heading: "{c["words"]["heading"][:90]}". Words: {c["words"]["chars"]} characters'
                         + (f', a list of {c["words"]["rows"]} rows' if c['words']['rows'] else '') + f'. The template put the {"picture first" if c["first"] == "picture" else "words first"}.\n    Forms open to it: {opened}.')
        else:
            lines.append(f'  "{sec["id"] or "-"}" — {kind}' + (f' (holds a picture but cannot be recomposed: {known[1][:70]})' if known else ''))
    return '\n'.join(lines), ids


def _to_doc(answer):
    """The document from the flat tool answer: per entry, the fields its form takes. A field of another form is not part
    of what was asked for; everything else wrong is left for the validator to name."""
    pictures = answer.get('pictures')
    if isinstance(pictures, str) and pictures.strip()[:1] == '[':
        try: pictures = json.loads(pictures)
        except ValueError: pass
    if isinstance(pictures, list):
        pictures = [{k: v for k, v in p.items() if v is not None and (p.get('form') not in PICTURES.KEYS or k not in FIELDS or k in PICTURES.KEYS[p['form']])} if isinstance(p, dict) else p for p in pictures]
    return {'ir': V.VERSION, 'note': str(answer.get('concept') or '')[:300], 'pictures': pictures}


def _broken(found): return [k for k in (found or {}) if any(b in k for b in BREAKING)]
def _standing(found): return (len(_broken(found)), len([k for k in (found or {}) if not any(b in k for b in BREAKING)]))


def compose(page_html, page_path, images=None, model=None, review=True, ask=None):
    """Compose the picture sections, correct once, settle against the render, look and revise once. Returns the last
    document that validates and breaks nothing, or none."""
    if ask is None:
        import agents; ask = agents.ask
    text, ids = brief(page_html, images); log, findings, best = [], None, None
    if not ids: return {'doc': None, 'drawn': False, 'attempts': 0, 'log': [{'stage': 'skip', 'errors': ['the page has no picture section that can be recomposed']}], 'measured': None}
    material = [{"type": "text", "text": text}]
    try:
        shots = LISTED.section_shots(page_path, ids[:MAX_PICTURED]) if review else {}
        for sid in ids[:MAX_PICTURED]:
            if sid in shots: material += [{"type": "text", "text": f'SECTION "{sid}" AS THE TEMPLATE DREW IT:'}, HERO._image_block(shots[sid], 900)]
    except Exception as e: material.append({"type": "text", "text": f'(the sections could not be pictured: {str(e)[:80]})'})
    folder = os.path.dirname(os.path.abspath(page_path))

    def attempt(stage, extra):
        answer = ask(SYSTEM, material + extra + [{"type": "text", "text": "Call write_pictures."}], TOOL, model=model, max_tokens=3000)
        if not isinstance(answer, dict):
            entry = {'stage': stage, 'errors': ['no composition returned']}; log.append(entry); return None, ['none'], entry
        doc = _to_doc(answer); errors = PICTURES.validate(doc, page_html, images)
        entry = {'stage': stage, 'concept': doc['note'], 'errors': [f"{e['code']} {e['at']}: {e['message']}" for e in errors], **({'refused': doc['pictures']} if errors else {})}; log.append(entry)
        return doc, errors, entry

    def look_at(candidate):
        """Settle the candidate against its render, then picture its sections and grade the whole page. → (settled, pictures, findings)"""
        settled, changes, left = settle(page_html, candidate, images, folder)
        if changes: log.append({'stage': 'settle', 'errors': [], 'changes': changes})
        if settled is None: return None, {}, {}
        page, _ = PICTURES.transplant(page_html, settled, images)
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=folder) as f: f.write(page); drawn = f.name
        try:
            pictures = LISTED.section_shots(drawn, [p['section'] for p in settled['pictures']][:MAX_PICTURED]) if review else {}
            found = {**HERO.measured(drawn), **left}
        finally: os.unlink(drawn)
        return settled, pictures, {k: v for k, v in found.items() if k not in baseline}

    doc, errors, entry = attempt('compose', [])
    if errors and doc is not None:
        doc, errors, entry = attempt('correct', [{"type": "text", "text": "YOUR PREVIOUS COMPOSITION WAS REFUSED:\n" + json.dumps(doc['pictures'], ensure_ascii=False) + "\nReasons:\n" + '\n'.join('- ' + e for e in entry['errors'][:12]) + "\nKeep the idea; fix exactly these."}])
    if doc is not None and not errors:
        try:
            baseline = HERO.measured(page_path)
            best, pictures, findings = look_at(doc); entry['measured'] = findings
            if best and review:
                look = [{"type": "text", "text": "YOUR PICTURES, AS DRAWN (settled against the render where a measurement asked for it):\n" + json.dumps(best['pictures'], ensure_ascii=False)}]
                for sid, path in pictures.items(): look += [{"type": "text", "text": f'SECTION "{sid}":'}, HERO._image_block(path, 900)]
                must = {k: v for k, v in findings.items() if any(b in k for b in BREAKING)}; other = {k: v for k, v in findings.items() if k not in must}
                if must: look.append({"type": "text", "text": "MEASURED ON THIS RENDER — your pictures break these; fix them, or none of it is shipped:\n" + '\n'.join(f'- {k}: {v}' for k, v in must.items())})
                if other: look.append({"type": "text", "text": "ALSO MEASURED — yours to weigh:\n" + '\n'.join(f'- {k}: {v}' for k, v in other.items())})
                look.append({"type": "text", "text": "Look at them as the art director. Is the subject of a picture cropped away, or under the words? Is a section half empty, or a small picture lost in a large space? Do two neighbours look the same? "
                                                        "Is any heading too large or too small for what stands next to it? Return the pictures you would ship: revised where the renders or the measurements show a problem, unchanged if you would ship this."})
                revised, revised_errors, second = attempt('revise', look)
                if revised is not None and revised_errors:   # a revision the validator refuses gets its reasons once, like a first composition
                    revised, revised_errors, second = attempt('correct', look + [{"type": "text", "text": "YOUR REVISION WAS REFUSED:\n" + json.dumps(revised['pictures'], ensure_ascii=False) + "\nReasons:\n" + '\n'.join('- ' + e for e in second['errors'][:12]) + "\nKeep the idea; fix exactly these."}])
                if revised is not None and not revised_errors:
                    settled, _, revised_findings = look_at(revised); second['measured'] = revised_findings
                    if settled is None or _standing(revised_findings) > _standing(findings): second['errors'] = ['revision measured worse than the first composition: kept the first']
                    else: best, findings = settled, revised_findings
        except Exception as e:
            log.append({'stage': 'look', 'errors': ['not measured: ' + str(e)[:160]]}); best = None   # a picture composition that could not be measured is not shipped
        if best and _broken(findings):
            log.append({'stage': 'refuse', 'errors': [f'the pictures break the page on the render ({", ".join(_broken(findings))}): not shipped']}); best = None
    return {'doc': best, 'drawn': best is not None, 'attempts': sum(1 for s in log if s['stage'] in ('compose', 'correct', 'revise')), 'log': log, 'measured': findings}


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 3 or args[1] != '--out': raise SystemExit('usage: compose_pictures.py <page.html> --out pictures.json [--images images.json] [--no-review]')
    with open(args[0], encoding='utf-8') as f: html = f.read()
    page_images = None
    if '--images' in args:
        with open(args[args.index('--images') + 1]) as f: page_images = json.load(f)
    result = compose(html, args[0], images=page_images, model=os.environ.get('COMPOSE_MODEL') or None, review='--no-review' not in args)
    if result['doc']:
        with open(args[2], 'w', encoding='utf-8') as f: json.dump(result['doc'], f, indent=1, ensure_ascii=False)
    with open(os.path.splitext(args[2])[0] + '.log.json', 'w', encoding='utf-8') as f: json.dump({k: result[k] for k in ('drawn', 'attempts', 'log')}, f, indent=1, ensure_ascii=False)
    print(json.dumps({'drawn': result['drawn'], 'attempts': result['attempts'], 'concept': (result['doc'] or {}).get('note')}, ensure_ascii=False))
    raise SystemExit(0 if result['drawn'] else 1)
