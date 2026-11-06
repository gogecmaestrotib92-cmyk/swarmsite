"""critic.py — the visual loop. Looks at the rendered page screen by screen (1440 and 390) and returns BOUNDED fixes,
applies them to direction.json, and says whether a re-render is needed.
Usage: python3 lib/qa/critic.py out/<slug> <html-file> [model]
Fixes it may ask for (nothing else): drop a beat, shorten a text field, swap a beat's image, swap the hero image,
change hero h1 (≤6 words, from the site's own words), set a beat's band (dark/paper). Each fix carries the reason."""
import json, os, sys, subprocess, base64, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

TOOL = {"name": "report_fixes", "description": "Report concrete visual defects and the bounded fixes for them.",
        "input_schema": {"type": "object", "required": ["score", "fixes"], "properties": {
            "score": {"type": "integer", "minimum": 0, "maximum": 100},
            "verdict": {"type": "string"},
            "fixes": {"type": "array", "maxItems": 10, "items": {"type": "object", "required": ["op", "reason"], "properties": {
                "op": {"type": "string", "enum": ["drop_beat", "shorten", "swap_image", "hero_image", "hero_h1", "band", "layout", "reorder", "note"]},
                "agent": {"type": "string", "enum": ["copy", "ui", "visual", "ux"], "description": "who owns the fix: copy = words; ui = columns/bands/sizes/spacing/empty screens; visual = which image, crops, missing visuals; ux = order of sections, CTAs, nav"},
                "beat": {"type": "string"}, "field": {"type": "string"}, "max_words": {"type": "integer"}, "image": {"type": "string"}, "value": {"type": "string"}, "reason": {"type": "string"}}}}}}}

SYSTEM = """You are the creative director reviewing screenshots of a page your studio just built. Be hard but concrete.
Look for: text clipped or overlapping, invisible text (same colour as background), empty or near-empty screens, images that are wrong for their slot (a UI screenshot stretched as a photo, a logo as a hero, a text-heavy crop), a hero that does not read in 3 seconds, sections that repeat the same idea, too many words on one screen, broken grids on the phone.
Report only what you can SEE. Every fix must name the beat id (from the direction), the agent who owns it, and the reason — written so that agent can act without seeing the screenshot (say which element, where, how big, what it should become).
Ops: shorten/hero_h1 → copy; swap_image/hero_image → visual (name the image id); band/layout → ui (columns, lead visual, compact, h2 size, head alignment); drop_beat/reorder → ux; note → anything else, to the right agent. Prefer dropping a weak section over padding it. Score 0–100 against award-level work (90+ = ship)."""

def shots(html, outdir):
    os.makedirs(outdir, exist_ok=True)
    subprocess.run(['node', os.path.join(ROOT, 'lib/qa/shots.mjs'), html, '--out', outdir], cwd=ROOT, capture_output=True, text=True, timeout=180)
    files = sorted(f for f in os.listdir(outdir) if f.endswith(('.png', '.jpg')))
    return [os.path.join(outdir, f) for f in files]

def critique(slug_dir, html, model='claude-sonnet-5-5'):
    import anthropic
    d = json.load(open(os.path.join(slug_dir, 'direction.json')))
    imgs_meta = [{k: v for k, v in i.items() if k != 'data'} for i in (json.load(open(os.path.join(slug_dir, 'images.json'))) if os.path.exists(os.path.join(slug_dir, 'images.json')) else [])]
    files = shots(html, os.path.join(slug_dir, 'critic-shots'))
    if not files: return {'score': -1, 'fixes': [], 'verdict': 'no screenshots'}
    content = [{"type": "text", "text": "DIRECTION (beat ids + copy)\n" + json.dumps({k: d[k] for k in ('hero', 'beats') if k in d}, ensure_ascii=False)[:14000] + "\n\nIMAGES available (ids)\n" + json.dumps(imgs_meta, ensure_ascii=False)[:3000]}]
    from PIL import Image; import io
    for f in files[:16]:
        try:
            im = Image.open(f).convert('RGB'); im.thumbnail((1100, 1100)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=72)
        except Exception: continue
        content.append({"type": "text", "text": "SCREEN: " + os.path.basename(f)})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}})
    content.append({"type": "text", "text": "Call report_fixes."})
    client = anthropic.Anthropic()
    msg = client.messages.create(model=model, max_tokens=3000, system=SYSTEM, messages=[{"role": "user", "content": content}], tools=[TOOL], tool_choice={"type": "auto"})
    call = next((b for b in msg.content if getattr(b, 'type', '') == 'tool_use'), None)
    return call.input if call else {'score': -1, 'fixes': [], 'verdict': 'no report'}

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
