"""critic.py — the visual loop. Looks at the rendered page screen by screen (1440 and 390) and returns BOUNDED fixes,
applies them to direction.json, and says whether a re-render is needed.
Usage: python3 lib/qa/critic.py out/<slug> <html-file> [model]
Fixes it may ask for (nothing else): drop a beat, shorten a text field, swap a beat's image, swap the hero image,
change hero h1 (≤6 words, from the site's own words), set a beat's band (dark/paper). Each fix carries the reason."""
import json, os, sys, subprocess, base64, re
from html.parser import HTMLParser
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import budget as B
import standard as STANDARD
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

TOOL = {"name": "report_fixes", "description": "Report concrete visual defects and the bounded fixes for them.",
        "input_schema": {"type": "object", "required": ["score", "fixes"], "properties": {
            "axes": {"type": "object", "required": ["design", "originality", "craft", "function"], "properties": {
                "design": {"type": "integer", "minimum": 0, "maximum": 100, "description": "hierarchy, type, colour, rhythm of screens, imagery fit — weight 35"},
                "originality": {"type": "integer", "minimum": 0, "maximum": 100, "description": "one idea the page performs, signature moves, not a template — weight 20"},
                "craft": {"type": "integer", "minimum": 0, "maximum": 100, "description": "nothing broken, clipped, blurry, empty, repeated; phone holds — weight 25"},
                "function": {"type": "integer", "minimum": 0, "maximum": 100, "description": "reads in 3 seconds, one action, proof before price, real facts — weight 20"}}},
            "score": {"type": "integer", "minimum": 0, "maximum": 100, "description": "weighted: .35 design + .20 originality + .25 craft + .20 function"},
            "studio": {"type": "object", "description": "five closer readings, reported beside the score and not part of it", "properties": {
                "typography": {"type": "integer", "minimum": 0, "maximum": 100, "description": "a system of faces with contrast of scale, set with care"},
                "composition": {"type": "integer", "minimum": 0, "maximum": 100, "description": "each screen arranged on purpose: asymmetry, space, alignment"},
                "imagery": {"type": "integer", "minimum": 0, "maximum": 100, "description": "pictures that belong to their section and are given room"},
                "rhythm": {"type": "integer", "minimum": 0, "maximum": 100, "description": "the page changes pace and ground from screen to screen"},
                "concept": {"type": "integer", "minimum": 0, "maximum": 100, "description": "one idea, stated by the page's own direction when there is one, and kept down the page"}}},
            "verdict": {"type": "string", "description": "one paragraph: the gap between this page and the reference it is closest to"},
            "fixes": {"type": "array", "maxItems": 10, "items": {"type": "object", "required": ["op", "reason"], "properties": {
                "op": {"type": "string", "enum": ["drop_beat", "shorten", "swap_image", "hero_image", "hero_h1", "band", "layout", "reorder", "note"]},
                "agent": {"type": "string", "enum": ["copy", "ui", "visual", "ux", "concept"], "description": "who owns the fix: copy = words; ui = columns/bands/sizes/spacing/empty screens; visual = which image, crops, missing visuals; ux = order of sections, CTAs, nav; concept = the section's MOVE is wrong (sticky/pinned/type-wall/marquee/story/cards) or the page lacks one idea"},
                "beat": {"type": "string"}, "field": {"type": "string"}, "max_words": {"type": "integer"}, "image": {"type": "string"}, "value": {"type": "string"}, "reason": {"type": "string"}}}}}}}

AREAS = {'art_direction': 'one idea, specific to this subject, visible on the first screen and still there on the last',
         'typography': 'a system of faces and sizes with one scale regime; headings broken by sense',
         'composition': 'each screen arranged on purpose: few shared edges, room given, something crossing its column',
         'hierarchy': 'one thing seen first on each screen, and it is the right thing',
         'imagery': 'pictures given a job and room, never a box beside text',
         'originality': 'a device of its own that follows from the subject',
         'motion': 'what the direction says moves, as one system — judged from the frozen frames and from what the browser measured',
         'content': 'an argument: what it is, for whom, proof beside the claim, the next step always visible',
         'responsive': 'the 390 screens recomposed, not stacked'}
OPS = ["drop_beat", "shorten", "swap_image", "hero_image", "hero_h1", "band", "layout", "reorder", "note"]


def final_tool():
    """The tool of the final look: the same report, plus a level for each area of the Standard and findings with all their
    parts. Intermediate rounds keep the short tool: they steer the agents and do not decide what ships."""
    tool = json.loads(json.dumps(TOOL)); props = tool['input_schema']['properties']
    props['levels'] = {"type": "object", "description": "the level of each area: 1 machine-made, 2 competent, 3 distinctive studio quality, 4 experimental; halves allowed",
                       "properties": {a: {"type": "number", "minimum": 1, "maximum": 4, "description": d} for a, d in AREAS.items()}}
    props['findings'] = {"type": "array", "maxItems": 8, "description": "for the areas below level 3: what is wrong, where, why, and the one correction", "items": {
        "type": "object", "required": ["defect", "area", "evidence", "reason", "correction"], "properties": {
            "defect": {"type": "string", "description": "an id from DEFECTS, or NEW"}, "area": {"type": "string", "enum": list(AREAS)}, "beat": {"type": "string", "description": "the section id"},
            "viewport": {"type": "string", "enum": ["1440", "390", "both"]}, "evidence": {"type": "string", "description": "what is seen, on which screen, where on it"},
            "reason": {"type": "string", "description": "why a designer reads it as a defect"},
            "correction": {"type": "object", "required": ["op"], "properties": {"op": {"type": "string", "enum": OPS + ["gap"], "description": "an operation that exists, or gap when nothing the engine can do today would fix it"},
                                                                                   "detail": {"type": "string", "description": "the parameters, or for a gap what would have to exist"}}},
            "expectation": {"type": "string", "description": "what will be different, visibly or measurably, if the correction worked"}, "confidence": {"type": "string", "enum": ["seen", "inferred"]}}}}
    return tool


STANDARD_BRIEF = """
THE FINAL LOOK — besides the report above, give a level to each area and findings for the areas below level 3.
LEVELS: 1 = machine-made, a known template with another logo; 2 = competent: clear and tidy, nothing wrong and nothing remembered; 3 = distinctive studio quality: this could only be this company's page and every screen was decided; 4 = experimental: a form not met before that serves the subject. Level 3 needs an idea and a type system; a tidy page without them is level 2 whatever else it does.
A FINDING has every part or is not reported: the defect (an id from DEFECTS, or NEW), the area, the section and viewport, the evidence (what is seen, on which screen, where), the reason, ONE correction, and what will change if it worked. The correction is an operation that exists (the ops of report_fixes). When nothing the engine can do today would fix it, the op is "gap" and the detail says what would have to exist: gaps are counted and become the engine's backlog, so name them precisely.
MEASURED BY A BROWSER, when listed below, is fact: the page was measured while it loaded, scrolled and moved. Do not re-estimate what is measured. Weigh those findings in your levels, refer to them by id, and spend your own findings on what a browser cannot measure.
DEFECTS a reviewer judges:
""" + '\n'.join(f'- {fid} ({area}): {what}' for fid, (area, what) in STANDARD.REVIEWED.items()) + """
DEFECTS a browser measures (listed for you when present): """ + ', '.join(sorted(STANDARD.CATALOGUE))

SYSTEM = """You are the creative director reviewing screenshots of a page your studio just built. Be hard but concrete.
CALIBRATION — score each axis against these measured references; the numbers are an internal comparison scale:
- Butter (butter.video) = 90: near-white paper, regular-weight grotesk type, product framed in generous white space, story sections and a logo ticker; every screen one idea.
- Cerebrium (cerebrium.ai) = 88: dark and light bands, light-weight type, pinned feature tour, monospace labels, product widgets, a 3D hero and case studies.
- Tengile (tengilemalamala.com) = 92: a place told in photographs; a full-bleed video hero, offset photo pairs and portrait cards, a quiet editorial serif, photo marquee and collage.
A page that is tidy but anonymous (grid of cards, stock rhythm, no idea) sits at 45–55. A page with a broken screen, a blurry or repeated picture, or an empty half-screen cannot score above 60 on craft. 70 means "a good studio would ship after a day of polish"; 80 means "ship"; 90 means reference-level craft on this internal scale.
WHAT SEPARATES STUDIO WORK — use it to place a page between 55 and 90: a system of type (a display face with character, a quiet face for text, small labels) with real contrast of scale; lists held as ruled rows with space and a hairline between them rather than as grids of boxes; pictures that belong to their section — running off the screen, dissolved into the ground, cut by the type, the ground of the words — rather than rectangles beside text; almost no shadows; grounds that change the pace; one idea that returns down the page. Tiles on every section, identical icon cards, a badge above the headline, gradients and glows read as machine-made.
Look for: text clipped or overlapping, invisible text (same colour as background), empty or near-empty screens, images that are wrong for their slot (a UI screenshot stretched as a photo, a logo as a hero, a text-heavy crop), a hero that does not read in 3 seconds, sections that repeat the same idea, too many words on one screen, broken grids on the phone.
Report only what you can SEE. Every fix must name the beat id (from the direction), the agent who owns it, and the reason — written so that agent can act without seeing the screenshot (say which element, where, how big, what it should become).
Ops: shorten/hero_h1 → copy; swap_image/hero_image → visual (name the image id); band/layout → ui (columns, lead visual, compact, h2 size, head alignment); drop_beat/reorder → ux; note → anything else, to the right agent. Prefer dropping a weak section over padding it. Score 0–100 against award-level work (90+ = ship)."""

LIST_FORMS = {'ledger': 'ruled rows across the width, each with its numeral or tag, its title and its body', 'stagger': 'two or three columns whose items step down against each other', 'bento': 'tiles on a grid, one of them large on the accent colour'}
PICTURE_FORMS = {'backdrop': 'the picture fills the section and the words stand on it', 'bleed': 'the picture runs off one edge of the screen, dissolving into the section or cut clean, the words beside it',
                 'panorama': 'the picture crosses the whole screen as a strip, the words above or below it', 'card': 'a large picture with the words in a notch cut from its corner',
                 'offset': 'the picture cut to a proportion and hung beside the words', 'stage': 'the picture shown whole on a ground of colour, which may be the picture\'s own colour', 'inline': 'the picture set into the heading like a word',
                 'gallery': 'neighbouring pictures in one row, each over its own heading and words'}
WORD_FORMS = {'poster': 'the heading very large across the width, what it introduces set under it to one side', 'columns': 'the heading on top and the rows in two columns, like a printed menu', 'statement': 'a short section centred, the heading large'}


def recomposed(page):
    """{section id: what it now is} for the sections of this page that were redrawn as compositions after the direction was
    written. The move the direction names for such a section no longer applies, and the critic is told what it is instead."""
    out = {}
    for tag in re.finditer(r'<section class="([^"]*)"([^>]*)>', page):
        classes, rest = tag.group(1).split(), tag.group(2); sid = (re.search(r'\bid="([^"]*)"', rest) or [None, ''])[1]; form = (re.search(r'data-form="([^"]*)"', rest) or [None, ''])[1]
        if 'data-ir=' in rest: out[sid or 'top'] = 'the first screen, composed on a twelve-column grid in the page\'s own type system'
        elif 'data-lc=' in rest: kind = next((c[3:] for c in classes if c.startswith('lc-') and c[3:] in LIST_FORMS), ''); out[sid] = 'a list drawn as ' + LIST_FORMS.get(kind, 'a composed list')
        elif 'data-pc=' in rest:
            out[sid] = PICTURE_FORMS.get(form, 'a composed picture section')
            if form == 'gallery':   # the sections that were run together keep their ids on the columns of the row
                end = page.find('</section>', tag.end())
                for member in re.findall(r'<article class="pc-gi" id="([^"]+)"', page[tag.end():end if end > 0 else len(page)]): out[member] = f'one picture of the row that begins at "{sid}"'
        elif 'data-wc=' in rest: out[sid] = 'words only: ' + WORD_FORMS.get(form, 'a composed section of words')
    return out


def shots(html, outdir, fast=False):  # fast = intermediate rounds: desktop only, short waits; the final look sees both viewports
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir): os.remove(os.path.join(outdir, f))
    result = subprocess.run(['node', os.path.join(ROOT, 'lib/qa/shots.mjs'), html, '--out', outdir] + (['--fast', '--desktop-only'] if fast else []), cwd=ROOT, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError('screenshot capture failed: ' + (result.stderr or result.stdout)[-500:])
    files = sorted(f for f in os.listdir(outdir) if f.endswith(('.png', '.jpg')))
    return [os.path.join(outdir, f) for f in files]

def select_screenshots(files, limit=20):  # final look: both viewports, every section of a 10-section page; fast rounds are desktop only
    if len(files) <= limit: return files
    # Preserve the section overview before spending the remaining budget on
    # individual pinned slides, with both viewport sizes represented.
    primary = [f for f in files if not re.search(r'-slide-\d+-of-\d+\.png$', os.path.basename(f))]
    extra = [f for f in files if f not in primary]
    def balanced(group, count, prefer_end=False):
        if count <= 0: return []
        def evenly(items, n):
            if not n: return []
            if n == 1: return [items[-1] if prefer_end else items[0]]
            return [items[round(i * (len(items) - 1) / (n - 1))] for i in range(n)]
        desktop = [f for f in group if os.path.basename(f).startswith('desktop-')]
        mobile = [f for f in group if os.path.basename(f).startswith('mobile-')]
        if not desktop or not mobile: return evenly(group, min(count, len(group)))
        nd = min(len(desktop), count // 2)
        nm = min(len(mobile), count - nd)
        nd = min(len(desktop), count - nm)
        return evenly(desktop, nd) + evenly(mobile, nm)
    selected = balanced(primary, min(limit, len(primary)))
    return selected + balanced(extra, limit - len(selected), prefer_end=True)

class RenderedActions(HTMLParser):
    """Read actual rendered CTA destinations and embedded forms by section."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections, self.actions, self.forms = [], [], set()
        self.link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section': self.sections.append(attrs.get('id', ''))
        if tag == 'form' and self.sections: self.forms.add(self.sections[-1])
        if tag == 'a' and 'btn' in attrs.get('class', '').split() and attrs.get('href'):
            self.link = {'section': self.sections[-1] if self.sections else '',
                         'href': attrs['href'], 'text': ''}

    def handle_data(self, text):
        if self.link is not None: self.link['text'] += text

    def handle_endtag(self, tag):
        if tag == 'a' and self.link is not None:
            self.link['text'] = ' '.join(self.link['text'].split())
            self.actions.append(self.link)
            self.link = None
        if tag == 'section' and self.sections: self.sections.pop()

def rendered_actions(html):
    parser = RenderedActions()
    with open(html, encoding='utf-8') as f: parser.feed(f.read())
    return parser.actions, parser.forms

def critique(slug_dir, html, model='claude-sonnet-5-5', fast=False, files=None, measured=None, own=None):
    """One reading of the page. `files`: screenshots already taken (critique_twice takes them once for both readings).
    `measured`: the findings a browser measured on this page (lib/qa/standard.py), handed to the final look as fact.
    `own`: the page's own plan, when the page was not rendered from direction.json (the studio's page): the critic is
    then told what this page set out to be and is not shown a direction, beats or moves that describe another page."""
    import anthropic
    d = json.load(open(os.path.join(slug_dir, 'direction.json')))
    imgs_meta = [{k: v for k, v in i.items() if k != 'data'} for i in (json.load(open(os.path.join(slug_dir, 'images.json'))) if os.path.exists(os.path.join(slug_dir, 'images.json')) else [])]
    files = files or shots(html, os.path.join(slug_dir, 'critic-shots'), fast)
    if not files: return {'score': -1, 'fixes': [], 'verdict': 'no screenshots'}
    with open(html, encoding='utf-8') as f: redrawn = recomposed(f.read())
    def J(name):
        try:
            with open(os.path.join(slug_dir, name), encoding='utf-8') as f: return json.load(f)
        except (OSError, ValueError): return {}
    composition, brief = J('composition.json') if redrawn else {}, J('brief.json')
    actions, embedded_forms = rendered_actions(html)
    form_ids = {b.get('id') for b in d.get('beats', []) if b.get('type') == 'form'}
    linked_forms = {a['section'] for a in actions if a['section'] in form_ids and a['section'] not in embedded_forms
                    and re.match(r'^(?:https?://|mailto:|tel:)', a['href'], re.I)}
    beats = [{k: v for k, v in beat.items() if k != 'fields' or beat.get('id') not in linked_forms}
             for beat in d.get('beats', [])]
    moves = {b['id']: (b.get('ui') or {}).get('move') for b in d.get('beats', []) if (b.get('ui') or {}).get('move') and b['id'] not in redrawn}
    context = ''
    if redrawn:   # the page was recomposed after the direction was written: what it set out to do, and what each redrawn section now is
        said = ' '.join(str(x) for x in (composition.get('concept'), composition.get('direction')) if x)
        context += ("RECOMPOSED ON PURPOSE — these sections were redrawn after the direction below was written. The move the direction names for them no longer applies and is not listed under SIGNATURE MOVES: judge each as what it now is, "
                    "and whether that is done well.\n" + '\n'.join(f'- {k}: {v}' for k, v in redrawn.items()) + (f"\nTHE PAGE'S OWN DIRECTION (what it set out to do; judge whether it does it): {said[:1200]}" if said else '') + "\n\n")
    if brief.get('mode') == 'seo-safe':
        context += "THE WORDS ARE THE CLIENT'S OWN, kept as they are for search: a claim, a count or a phrase of the copy is not a defect of this page (report it once as a note for copy at most); how the words are set is.\n\n"
    if own:
        moves = {}; redrawn = {}
        context += ("THIS PAGE WAS COMPOSED FROM AUTHORED SCENES, not rendered from a direction: there are no beat ids and none of the signature moves listed below is promised. Judge the page in the screenshots as what it is. "
                    "ITS OWN PLAN (what it set out to do; judge whether it does it): " + json.dumps(own, ensure_ascii=False)[:3000] + "\n\n")
    content = [{"type": "text", "text": context + "SIGNATURE MOVES on this page (screenshots are the real layout with animation frozen: a pinned or sticky section is shown mid-scroll with its first frame on; slide-labeled images show later frames. Judge whether each move reads as designed — a pinned panel that is not on screen, a ticker that is one static line, a type-wall that is plain unlit text are defects): " + json.dumps(moves) + "\n- sticky-product: text blocks scroll on the left, the product stays pinned on the right and swaps per block\n- pinned-sequence: the section pins, each step takes the screen in turn\n- type-wall: one sentence in giant type lights up word by word as you scroll\n- marquee: a slow ticker of the section's words (one line IS the design)\n- story: text beside a visual\n\nRENDERED CTA LINKS (from the page HTML; destinations have not been tested)\n" + json.dumps(actions, ensure_ascii=False) + "\nSections " + json.dumps(sorted(linked_forms)) + " use a link to the source site or to a contact method in place of an embedded form: a preview cannot take a booking or a message, so that is by design and not a defect. Any other form beat must show real input fields; a bare link in its place is a defect.\n\n" + ("" if own else "DIRECTION (beat ids + copy)\n" + json.dumps({'hero': d.get('hero', {}), 'beats': beats}, ensure_ascii=False)[:14000]) + "\n\nIMAGES available (ids)\n" + json.dumps(imgs_meta, ensure_ascii=False)[:3000]}]
    from PIL import Image; import io
    before = os.path.join(slug_dir, 'before-hero.jpg')
    if os.path.exists(before) and not fast:   # what the client has now: the new page is judged as a redesign of it
        try:
            im = Image.open(before).convert('RGB'); im.thumbnail((900, 900)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=68)
            content += [{"type": "text", "text": "THE CLIENT'S CURRENT SITE, first screen — for comparison only: the new page should be a clear step up from it, in its own right."},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}]
        except Exception: pass
    for f in select_screenshots(files, 8 if fast else 20):  # a fast round looks at the shape (8 desktop frames), the final look at everything
        try:
            im = Image.open(f).convert('RGB'); im.thumbnail((1000, 1000)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=70)
        except Exception: continue
        content.append({"type": "text", "text": "SCREEN: " + os.path.basename(f)})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}})
    if not fast and measured:
        content.append({"type": "text", "text": "MEASURED BY A BROWSER on this page (fact, not opinion):\n" + '\n'.join(
            f"- {m.get('id')} at {m.get('view')}: {(m.get('evidence') or {}).get('reading')} = {json.dumps((m.get('evidence') or {}).get('value'), ensure_ascii=False)}; expected {(m.get('evidence') or {}).get('expected')}; {(m.get('evidence') or {}).get('references')}"
            for m in measured[:16] if isinstance(m, dict))})
    content.append({"type": "text", "text": "Score the four axes against the calibration, compute the weighted score, then call report_fixes." + ('' if fast else " Give the level of each area and the findings.")})
    client = anthropic.Anthropic()
    B.check('critic'); msg = client.messages.create(model=model, max_tokens=3000 if fast else 4500, system=SYSTEM if fast else SYSTEM + STANDARD_BRIEF, messages=[{"role": "user", "content": content}], tools=[TOOL if fast else final_tool()], tool_choice={"type": "auto"})
    B.charge(getattr(msg, 'usage', None), 'critic', model)
    call = next((b for b in msg.content if getattr(b, 'type', '') == 'tool_use'), None)
    r = dict(call.input) if call else {'score': -1, 'fixes': [], 'verdict': 'no report'}
    if not isinstance(r.get('fixes'), list): r['fixes'] = []
    r['fixes'] = [f for f in r['fixes'] if isinstance(f, dict)]
    if isinstance(r.get('axes'), dict) and not isinstance(r.get('score'), (int, float)):
        ax = r['axes']; r['score'] = round(.35 * ax.get('design', 0) + .2 * ax.get('originality', 0) + .25 * ax.get('craft', 0) + .2 * ax.get('function', 0))
    return reviewed(r)


def reviewed(r):
    """The Standard's part of a report, made safe: levels as numbers 1–4 for known areas, findings that have their parts,
    the page level by the Standard's rule. A report without them (an intermediate round) is returned as it is."""
    if isinstance(r.get('levels'), dict):
        r['levels'] = {a: float(v) for a, v in r['levels'].items() if a in AREAS and isinstance(v, (int, float)) and not isinstance(v, bool) and 1 <= v <= 4}
        r['page_level'] = STANDARD.page_level(r['levels'])
    elif 'levels' in r: del r['levels']
    if 'findings' in r:
        kept = []
        for f in r['findings'] if isinstance(r['findings'], list) else []:
            if not isinstance(f, dict) or not all(isinstance(f.get(k), str) and f[k].strip() for k in ('defect', 'area', 'evidence', 'reason')): continue
            fix = f.get('correction') if isinstance(f.get('correction'), dict) else {}
            if fix.get('op') not in OPS + ['gap'] or f['area'] not in AREAS: continue
            kept.append({'id': f['defect'].strip()[:12], 'area': f['area'], 'track': 'C', 'beat': str(f.get('beat') or '')[:60], 'view': str(f.get('viewport') or 'both'), 'evidence': f['evidence'].strip()[:400], 'reason': f['reason'].strip()[:300],
                         'correction': {'op': fix['op'], 'detail': str(fix.get('detail') or '')[:300]}, 'expectation': str(f.get('expectation') or '')[:300], 'confidence': f.get('confidence') if f.get('confidence') in ('seen', 'inferred') else 'seen'})
        r['findings'] = kept
    return r

def critique_twice(slug_dir, html, model='claude-sonnet-5-5', shots_dir='critic-shots', measured=None):
    """Two readings of the same screenshots, averaged. One reading of a page moves about four points either way; where a
    decision hangs on the score — is the composed page at least as good as the one it would replace — two are taken.
    The verdict and the fixes are the harder reading's; `readings` keeps both scores."""
    from concurrent.futures import ThreadPoolExecutor
    files = shots(html, os.path.join(slug_dir, shots_dir), False)
    if not files: return {'score': -1, 'fixes': [], 'verdict': 'no screenshots'}
    with ThreadPoolExecutor(2) as pool: both = list(pool.map(lambda _: critique(slug_dir, html, model, False, files, **({'measured': measured} if measured else {})), range(2)))
    read = [r for r in both if isinstance(r, dict) and isinstance(r.get('score'), (int, float)) and r['score'] >= 0]
    if not read: return both[0]
    hard = min(read, key=lambda r: r['score']); mean = lambda values: round(sum(values) / len(values))
    merged = dict(hard, score=mean([r['score'] for r in read]), readings=[r['score'] for r in read])
    for group in ('axes', 'studio'):
        parts = [r[group] for r in read if isinstance(r.get(group), dict)]
        if parts: merged[group] = {k: mean([p[k] for p in parts if isinstance(p.get(k), (int, float))]) for k in parts[0] if any(isinstance(p.get(k), (int, float)) for p in parts)}
    levels = [r['levels'] for r in read if isinstance(r.get('levels'), dict) and r['levels']]
    if levels:   # the level of an area is the mean of the readings that gave one, to the half
        merged['levels'] = {a: round(sum(l[a] for l in levels if a in l) / sum(1 for l in levels if a in l) * 2) / 2 for a in AREAS if any(a in l for l in levels)}
        merged['page_level'] = STANDARD.page_level(merged['levels'])
    seen, findings = set(), []
    for r in [hard] + [x for x in read if x is not hard]:   # the harder reading's findings first; the other's where they name something else
        for f in r.get('findings') or []:
            key = (f.get('id'), f.get('beat'))
            if key not in seen: seen.add(key); findings.append(f)
    if findings or any('findings' in r for r in read): merged['findings'] = findings[:10]
    return merged


def apply(slug_dir, rep):
    p = os.path.join(slug_dir, 'direction.json'); d = json.load(open(p)); changed = 0
    by_id = {b['id']: b for b in d.get('beats', [])}
    for fx in rep.get('fixes', []):
        op = fx.get('op'); b = by_id.get(fx.get('beat', ''))
        if op == 'drop_beat' and b and len(d['beats']) > 3: d['beats'] = [x for x in d['beats'] if x['id'] != b['id']]; changed += 1
        elif op == 'shorten' and fx.get('field'):
            tgt = b if b else d.get('hero', {}); f = fx['field']; mw = max(6, int(fx.get('max_words') or 20))
            if isinstance(tgt.get(f), str): w = tgt[f].split(); tgt[f] = ' '.join(w[:mw]) + ('.' if len(w) > mw and not tgt[f].rstrip().endswith('.') else ''); changed += 1
        elif op == 'swap_image' and b and fx.get('image'): b['image'] = fx['image']; changed += 1
        elif op == 'hero_image' and fx.get('image'): d.setdefault('hero', {})['media'] = fx['image']; changed += 1
        elif op == 'hero_h1' and fx.get('value') and len(re.sub(r'<[^>]+>', '', fx['value']).split()) <= 8: d['hero']['h1'] = fx['value']; changed += 1
        elif op == 'band' and b and fx.get('value') in ('dark', 'paper'): b['band'] = fx['value']; changed += 1
    if changed: json.dump(d, open(p, 'w'), indent=1, ensure_ascii=False)
    return changed

if __name__ == '__main__':
    slug_dir, html = sys.argv[1], sys.argv[2]; model = sys.argv[3] if len(sys.argv) > 3 else 'claude-sonnet-5-5'
    rep = critique(slug_dir, html, model); n = apply(slug_dir, rep)
    json.dump({**rep, 'applied': n}, open(os.path.join(slug_dir, 'critic.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({'score': rep.get('score'), 'fixes': len(rep.get('fixes', [])), 'applied': n, 'verdict': rep.get('verdict', '')[:160]}))
