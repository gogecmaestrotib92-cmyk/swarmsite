"""critic.py — the visual loop. Looks at the rendered page screen by screen (1440 and 390) and returns BOUNDED fixes,
applies them to direction.json, and says whether a re-render is needed.
Usage: python3 lib/qa/critic.py out/<slug> <html-file> [model]
Fixes it may ask for (nothing else): drop a beat, shorten a text field, swap a beat's image, swap the hero image,
change hero h1 (≤6 words, from the site's own words), set a beat's band (dark/paper). Each fix carries the reason."""
import json, os, sys, subprocess, base64, re
from html.parser import HTMLParser
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

TOOL = {"name": "report_fixes", "description": "Report concrete visual defects and the bounded fixes for them.",
        "input_schema": {"type": "object", "required": ["score", "fixes"], "properties": {
            "axes": {"type": "object", "required": ["design", "originality", "craft", "function"], "properties": {
                "design": {"type": "integer", "minimum": 0, "maximum": 100, "description": "hierarchy, type, colour, rhythm of screens, imagery fit — weight 35"},
                "originality": {"type": "integer", "minimum": 0, "maximum": 100, "description": "one idea the page performs, signature moves, not a template — weight 20"},
                "craft": {"type": "integer", "minimum": 0, "maximum": 100, "description": "nothing broken, clipped, blurry, empty, repeated; phone holds — weight 25"},
                "function": {"type": "integer", "minimum": 0, "maximum": 100, "description": "reads in 3 seconds, one action, proof before price, real facts — weight 20"}}},
            "score": {"type": "integer", "minimum": 0, "maximum": 100, "description": "weighted: .35 design + .20 originality + .25 craft + .20 function"},
            "verdict": {"type": "string", "description": "one paragraph: the gap between this page and the reference it is closest to"},
            "fixes": {"type": "array", "maxItems": 10, "items": {"type": "object", "required": ["op", "reason"], "properties": {
                "op": {"type": "string", "enum": ["drop_beat", "shorten", "swap_image", "hero_image", "hero_h1", "band", "layout", "reorder", "note"]},
                "agent": {"type": "string", "enum": ["copy", "ui", "visual", "ux", "concept"], "description": "who owns the fix: copy = words; ui = columns/bands/sizes/spacing/empty screens; visual = which image, crops, missing visuals; ux = order of sections, CTAs, nav; concept = the section's MOVE is wrong (sticky/pinned/type-wall/marquee/story/cards) or the page lacks one idea"},
                "beat": {"type": "string"}, "field": {"type": "string"}, "max_words": {"type": "integer"}, "image": {"type": "string"}, "value": {"type": "string"}, "reason": {"type": "string"}}}}}}}

SYSTEM = """You are the creative director reviewing screenshots of a page your studio just built. Be hard but concrete.
CALIBRATION — score each axis against these references (Awwwards SOTD winners you know by their form):
- Butter (butter.us) = 90: cream paper, one serif voice, product framed in generous white space, sticky story sections, a ticker, every screen one idea; nothing decorative.
- Cerebrium (cerebrium.ai) = 88: dark, type-led, pinned feature tour, monospace labels, dense but never crowded; the product is the only picture and it is enough.
- Tengile (tengile.com) = 92: a place told in photographs; full-bleed photo screens, a quiet editorial serif, a ledger of real prices, every image sharp and sized to its frame.
A page that is tidy but anonymous (grid of cards, stock rhythm, no idea) sits at 45–55. A page with a broken screen, a blurry or repeated picture, or an empty half-screen cannot score above 60 on craft. 70 means "a good studio would ship after a day of polish"; 80 means "ship"; 90 means SOTD.
Look for: text clipped or overlapping, invisible text (same colour as background), empty or near-empty screens, images that are wrong for their slot (a UI screenshot stretched as a photo, a logo as a hero, a text-heavy crop), a hero that does not read in 3 seconds, sections that repeat the same idea, too many words on one screen, broken grids on the phone.
Report only what you can SEE. Every fix must name the beat id (from the direction), the agent who owns it, and the reason — written so that agent can act without seeing the screenshot (say which element, where, how big, what it should become).
Ops: shorten/hero_h1 → copy; swap_image/hero_image → visual (name the image id); band/layout → ui (columns, lead visual, compact, h2 size, head alignment); drop_beat/reorder → ux; note → anything else, to the right agent. Prefer dropping a weak section over padding it. Score 0–100 against award-level work (90+ = ship)."""

def shots(html, outdir, fast=False):
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir): os.remove(os.path.join(outdir, f))
    result = subprocess.run(['node', os.path.join(ROOT, 'lib/qa/shots.mjs'), html, '--out', outdir] + (['--fast'] if fast else []), cwd=ROOT, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError('screenshot capture failed: ' + (result.stderr or result.stdout)[-500:])
    files = sorted(f for f in os.listdir(outdir) if f.endswith(('.png', '.jpg')))
    return [os.path.join(outdir, f) for f in files]

def select_screenshots(files, limit=28):
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

def critique(slug_dir, html, model='claude-sonnet-5-5', fast=False):
    import anthropic
    d = json.load(open(os.path.join(slug_dir, 'direction.json')))
    imgs_meta = [{k: v for k, v in i.items() if k != 'data'} for i in (json.load(open(os.path.join(slug_dir, 'images.json'))) if os.path.exists(os.path.join(slug_dir, 'images.json')) else [])]
    files = shots(html, os.path.join(slug_dir, 'critic-shots'), fast)
    if not files: return {'score': -1, 'fixes': [], 'verdict': 'no screenshots'}
    actions, embedded_forms = rendered_actions(html)
    form_ids = {b.get('id') for b in d.get('beats', []) if b.get('type') == 'form'}
    linked_forms = {a['section'] for a in actions if a['section'] in form_ids and a['section'] not in embedded_forms
                    and re.match(r'^(?:https?://|mailto:|tel:)', a['href'], re.I)}
    beats = [{k: v for k, v in beat.items() if k != 'fields' or beat.get('id') not in linked_forms}
             for beat in d.get('beats', [])]
    moves = {b['id']: (b.get('ui') or {}).get('move') for b in d.get('beats', []) if (b.get('ui') or {}).get('move')}
    content = [{"type": "text", "text": "SIGNATURE MOVES on this page (all screenshots use the no-motion accessibility layout; slide-labeled images show positions within that static layout. Multiple steps visible together are expected in no-motion mode. The screenshots cannot establish whether animations or pinning work, so do not report them as broken or absent solely from these images): " + json.dumps(moves) + "\n- sticky-product: text blocks scroll on the left, the product stays pinned on the right and swaps per block\n- pinned-sequence: the section pins, each step takes the screen in turn\n- type-wall: one sentence in giant type lights up word by word as you scroll\n- marquee: a slow ticker of the section's words (one line IS the design)\n- story: text beside a visual\n\nRENDERED CTA LINKS (from the page HTML; destinations have not been tested)\n" + json.dumps(actions, ensure_ascii=False) + "\nSections " + json.dumps(sorted(linked_forms)) + " use a link to the source site or contact method in place of an embedded form. Do not report missing fields merely because these sections use a link. Evaluate their visible layout and whether the action is clear.\n\nDIRECTION (beat ids + copy)\n" + json.dumps({'hero': d.get('hero', {}), 'beats': beats}, ensure_ascii=False)[:14000] + "\n\nIMAGES available (ids)\n" + json.dumps(imgs_meta, ensure_ascii=False)[:3000]}]
    from PIL import Image; import io
    for f in select_screenshots(files):
        try:
            im = Image.open(f).convert('RGB'); im.thumbnail((1000, 1000)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=70)
        except Exception: continue
        content.append({"type": "text", "text": "SCREEN: " + os.path.basename(f)})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}})
    content.append({"type": "text", "text": "Score the four axes against the calibration, compute the weighted score, then call report_fixes."})
    client = anthropic.Anthropic()
    msg = client.messages.create(model=model, max_tokens=3000, system=SYSTEM, messages=[{"role": "user", "content": content}], tools=[TOOL], tool_choice={"type": "auto"})
    call = next((b for b in msg.content if getattr(b, 'type', '') == 'tool_use'), None)
    r = dict(call.input) if call else {'score': -1, 'fixes': [], 'verdict': 'no report'}
    if not isinstance(r.get('fixes'), list): r['fixes'] = []
    r['fixes'] = [f for f in r['fixes'] if isinstance(f, dict)]
    if isinstance(r.get('axes'), dict) and not isinstance(r.get('score'), (int, float)):
        ax = r['axes']; r['score'] = round(.35 * ax.get('design', 0) + .2 * ax.get('originality', 0) + .25 * ax.get('craft', 0) + .2 * ax.get('function', 0))
    return r

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
