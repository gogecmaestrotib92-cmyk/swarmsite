"""direct.py — the art-direction + copy step (the part a studio's creative director does).
Input: out/<slug>/{inventory.json, assets.json, images.json, audit.json}
Output: out/<slug>/direction.json — a beats document the renderer can draw (schema below), written under our rules.
Usage: python3 lib/direct/direct.py out/frans.rs   (needs ANTHROPIC_API_KEY)
"""
import json, os, sys, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RULES = ['lib/rules/copy.md', 'lib/rules/rhythm.md', 'lib/rules/master-run-01-frans.md', 'lib/rules/interaction.md']

SCHEMA = r'''
{
 "blueprint": "id from the BLUEPRINTS list — the winner whose FORM fits this business best (class, mood, amount of imagery)",
 "change": "rebuild|restructure|polish",             // rebuild = weak site, new structure; restructure = keep their sections, re-set type/rhythm; polish = already good, keep structure and copy, fix only what the audit found
 "kind": "place|service|product|software",          // taste-skill kinds: place = people come to it; service = people hire them; product = thing sold; software = app/SaaS
 "concept": "C1..C8", "mode": "light|dark",
 "voice": "serif|sans",                              // serif for place/luxury/editorial; sans for software/product
 "brand": {"name": "...", "badge": "" , "keep_font": true, "font_hint": "display font to keep or ''", "accent": "#hex or ''", "paper": "#hex or ''", "ink": "#hex or ''"},
 "nav": {"links": [["#id","Label"],...max 4], "cta": "verb + object"},
 "hero": {"category": "category + buyer/place, 3-8 words", "fact": "one hard fact (number/price/date/place)", "h1": "claim ≤ 6 words, ONE word may be wrapped in <em>",
          "lede": "15-30 words", "cta": "verb + what you get", "cta2": "second action", "media": "image id from images.json, or '' "},
 "beats": [                                           // 4-6 beats, each ONE screen, in this order of types where they apply
   {"id":"quote","type":"quote","label":"...","big":"≤4 words italic statement","body":"≤60 words from the site's own words","who":"author or ''"},
   {"id":"...","type":"photo","label":"...","h2":"noun heading 1-6 words","lede":"10-40 words","image":"image id","cap":["left caption","right caption"]},
   {"id":"...","type":"ledger","label":"...","h2":"...","lede":"...","image":"image id or ''","items":[["name","price"],...6-10],"cta":"...","cta_href":"https://...","cta2":"","cta2_href":""},
   {"id":"...","type":"facts","image":"image id","facts":[["1982","label"],["44","label"],["9–00","label"]]},
   {"id":"...","type":"cells","label":"...","h2":"...","lede":"...","cells":[["label","REAL number from the site e.g. 39 / €69 / 14 days","sub"],...3-6]},   // ONLY real figures. Never 01/02/03 ordinals, never invented counts.
   {"id":"...","type":"features","label":"...","h2":"noun heading ≤5 words","lede":"...","features":[{"title":"2-4 words","body":"one sentence ≤18 words from the site"},...3-6]},   // software/product capabilities as text, not numbers
   {"id":"...","type":"steps","label":"...","h2":"...","steps":["...","...","..."],"note":"..."},
   {"id":"...","type":"form","label":"Rezervacija","h2":"≤4 words","fields":["Ime i prezime","Telefon","Broj gostiju","Datum","Vreme","Napomena"],"cta":"...","alt":["phone line","email line"],"image":"image id or ''"},
   {"id":"...","type":"faq","label":"...","items":[["Q","A ≤40 words"],...3-5]}
 ],
 "ending": {"tag":"one line","cols":[["Heading",["line","line"]],...3-4],"next":"Sledeće: … →","legal":"© 2026 …"},
 "audit_notes": ["things the owner must confirm: conflicting prices, missing photos, claims without proof"]
}'''

SYSTEM = """You are the creative director of a small, very good web studio. You turn an existing website into a premium one WITHOUT inventing anything.
Hard rules:
- Every number, price, hour, address, name, quote and claim must come from the inventory. If it isn't there, leave it out. Never invent reviews, counts, logos, customers.
- Write in the site's own language (the inventory shows it). Keep the owner's voice; cut the noise.
- Follow the copy and rhythm rules below exactly (H1 ≤ 6 words with a stance; category + fact label; 60–80 words per screen; nouns in headings; buttons = verb + object; one main action everywhere).
- Pick 4–6 beats only. One screen each. Photographs lead for a place/service; the ledger (real items + prices) is the artefact for a restaurant/shop/clinic.
- SOFTWARE / PRODUCT: voice "sans" unless the brand's own display font is a serif. hero.media = the product screenshot (the largest UI image), shown framed, not as a photo background. Beats: features (capabilities as text) → steps (≤3, each ≤12 words) → cells ONLY if the site states real figures (prices, counts, days) → ledger for pricing (plan, price) → faq/form. No "quote" beat unless the site has a real quoted sentence with an author.
- Headings: h2 ≤ 5 words (nouns). Steps ≤ 12 words each. Feature bodies ≤ 18 words. Never pad a grid with ordinals or placeholders; fewer, true items beat more.
- Choose images by id from images.json: the hero gets the best 'heroGrade' landscape photo; never reuse the same image twice.
- You SEE the site (screenshots attached). Judge it as a creative director: if it is already well designed (clear hierarchy, custom type, real photography, restraint), choose change="polish" and keep its structure, order and wording — only fix the audit findings. Average template sites get "restructure"; broken or generic sites get "rebuild". Never flatten a good site into a generic one.
- Choose ONE blueprint from BLUEPRINTS whose class EQUALS the site's kind (a restaurant never gets a software blueprint, a SaaS never a place one); among those, the mood (dark/light, serif/sans, photo-led vs type-led) and how much imagery the site actually has. Say why in audit_notes[0].
- IMAGERY BUDGET: count the DISTINCT visuals in IMAGES (a screenshot of the same screen counts once). With fewer than 3 distinct visuals choose a TYPE-LED blueprint (imagery=light) and plan beats that need no pictures: features as text, a ledger, facts as big figures, a quote. Never plan a photo beat or a 'makers' section without a real photo for it. Do not invent what a section 'would' show.
- Output ONLY the JSON document, no prose, matching the schema. Comments in the schema are for you, not for the output.
"""

def load(slug_dir):
    def j(n):
        p = os.path.join(slug_dir, n); return json.load(open(p)) if os.path.exists(p) else None
    inv, assets, images, audit = j('inventory.json'), j('assets.json'), j('images.json'), j('audit.json')
    imgs_meta = [{k: v for k, v in i.items() if k != 'data'} for i in (images or [])]
    return inv, assets, imgs_meta, audit

TOOL = {
    "name": "write_direction",
    "description": "Write the direction.json beats document for the renderer. Follow the SCHEMA in the prompt exactly.",
    "input_schema": {
        "type": "object",
        "required": ["kind", "concept", "mode", "voice", "brand", "nav", "hero", "beats", "ending", "audit_notes", "blueprint", "change"],
        "properties": {
            "kind": {"type": "string", "enum": ["place", "service", "product", "software"]}, "blueprint": {"type": "string"}, "change": {"type": "string", "enum": ["rebuild", "restructure", "polish"]},
            "concept": {"type": "string"}, "mode": {"type": "string", "enum": ["light", "dark"]}, "voice": {"type": "string", "enum": ["serif", "sans"]},
            "brand": {"type": "object", "properties": {"name": {"type": "string"}, "badge": {"type": "string"}, "keep_font": {"type": "boolean"}, "font_hint": {"type": "string"}, "accent": {"type": "string"}, "paper": {"type": "string"}, "ink": {"type": "string"}}, "required": ["name"]},
            "nav": {"type": "object", "properties": {"links": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}, "cta": {"type": "string"}}},
            "hero": {"type": "object", "required": ["category", "fact", "h1", "lede", "cta"], "properties": {"category": {"type": "string"}, "fact": {"type": "string"}, "h1": {"type": "string"}, "lede": {"type": "string"}, "cta": {"type": "string"}, "cta2": {"type": "string"}, "media": {"type": "string"}}},
            "beats": {"type": "array", "minItems": 3, "maxItems": 7, "items": {"type": "object", "required": ["id", "type"], "properties": {"id": {"type": "string"}, "type": {"type": "string", "enum": ["quote", "photo", "ledger", "facts", "cells", "features", "steps", "form", "faq"]}}, "additionalProperties": True}},
            "ending": {"type": "object", "additionalProperties": True},
            "audit_notes": {"type": "array", "items": {"type": "string"}}
        }
    }
}

def validate(doc):
    errs = []
    if not 3 <= len(doc.get('beats', [])) <= 7: errs.append('beats must be 4-6')
    h1 = re.sub(r'<[^>]+>', '', str(doc.get('hero', {}).get('h1', '')))
    if len(h1.split()) > 8: errs.append(f'h1 too long ({len(h1.split())} words): "{h1}"')
    try:
        import glob as _g; cls = {json.load(open(f))['id']: json.load(open(f)).get('class') for f in _g.glob(os.path.join(ROOT, 'lib/blueprints', '*.bp.json'))}
        if doc.get('blueprint') in cls and cls[doc['blueprint']] != doc.get('kind'): errs.append(f"blueprint {doc['blueprint']} is class {cls[doc['blueprint']]}, the site is kind {doc.get('kind')} — choose a {doc.get('kind')} blueprint")
    except Exception: pass
    for b in doc.get('beats', []):
        if b.get('type') == 'cells':
            nums = [str(c[1]).strip() for c in b.get('cells', []) if len(c) > 1]
            if nums and all(re.fullmatch(r'0?\d', n) for n in nums): errs.append('cells hold ordinals (01,02…) — use type "features" with text, or real figures')
        if b.get('type') == 'steps' and any(len(str(x).split()) > 14 for x in b.get('steps', [])): errs.append('a step is longer than 12 words')
        if b.get('h2') and len(re.sub(r'<[^>]+>', '', b['h2']).split()) > 6: errs.append(f'h2 too long: "{b["h2"]}"')
    ids = [b.get('id') for b in doc.get('beats', [])]
    if len(set(ids)) != len(ids): errs.append('beat ids must be unique')
    return errs

def brief_text(b):
    if not b: return 'none'
    lines = []
    lines.append('Keep their display font: ' + ('YES — brand.keep_font=true, font_hint = their font' if b.get('keepFont', True) else 'NO — choose a better one for this kind'))
    lines.append('Keep their colours: ' + ('YES — brand.accent/paper/ink must come from their palette' if b.get('keepColours', True) else 'NO — propose a palette that fits the kind'))
    lines.append('Keep their logo: ' + ('YES' if b.get('keepLogo', True) else 'NO — set the wordmark'))
    if b.get('keep'): lines.append('Owner says this is already good, do not change its meaning or wording: ' + str(b['keep'])[:400])
    if b.get('goal'): lines.append('The one action every screen should lead to: ' + str(b['goal'])[:120] + ' (hero.cta, nav.cta, ending.next)')
    if b.get('tone'): lines.append('Tone: ' + str(b['tone'])[:60])
    if b.get('kind'): lines.append('Kind of site (owner-stated): ' + str(b['kind']))
    return '\n'.join('- ' + l for l in lines)

def direct(slug_dir, model='claude-sonnet-5-5'):
    import anthropic
    inv, assets, imgs, audit = load(slug_dir)
    bp = os.path.join(slug_dir, 'brief.json'); brief = json.load(open(bp)) if os.path.exists(bp) else {}
    rules = '\n\n'.join(f'### {r}\n' + open(os.path.join(ROOT, r)).read() for r in RULES)
    fsp = os.path.join(slug_dir, 'factsheet.json'); factsheet = open(fsp).read()[:8000] if os.path.exists(fsp) else 'n/a'
    user = f"""RULES\n{rules}\n\nSCHEMA\n{SCHEMA}\n\nFACT SHEET (verified by the reader — prefer these words and figures)\n{factsheet}\n\nINVENTORY (what the site HAS)\n{json.dumps(inv, ensure_ascii=False)[:60000]}\n\nBRAND ASSETS\n{json.dumps({k: v for k, v in (assets or {}).items() if k != 'logo'}, ensure_ascii=False)[:6000]}\n\nIMAGES (ids you may use)\n{json.dumps(imgs, ensure_ascii=False)[:6000]}\n\nAUDIT\n{json.dumps(audit, ensure_ascii=False)[:8000] if audit else 'n/a'}\n\nOWNER'S BRIEF (hard constraints, override everything above)\n{brief_text(brief)}\n\nCall write_direction with the complete document."""
    client = anthropic.Anthropic()
    import base64, glob
    bps = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'lib/blueprints', '*.bp.json'))):
        bpj = json.load(open(f)); t = bpj.get('type', {}); dsp = t.get('display') or {}
        bps.append(f"- {bpj['id']}: class={bpj.get('class')} archetype={bpj.get('archetype')} mode={bpj.get('colour', {}).get('mode')} display={dsp.get('fam')} {dsp.get('px')}px w{dsp.get('w')} sections={len(bpj.get('sections', []))} imagery={'heavy' if bpj.get('media', {}).get('aspects') and len(bpj['media']['aspects']) > 3 else 'light'} note={bpj.get('motion', {}).get('idea', '')[:90]}")
    content = [{"type": "text", "text": user + "\n\nBLUEPRINTS (choose one id)\n" + "\n".join(bps)}]
    for shot in ('before-hero.jpg', 'before-full.jpg'):
        fp = os.path.join(slug_dir, shot)
        if os.path.exists(fp) and os.path.getsize(fp) < 4_500_000:
            content.append({"type": "text", "text": f"SCREENSHOT: {shot} ({'the first screen' if 'hero' in shot else 'the whole page, top to bottom'})"})
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(open(fp, 'rb').read()).decode()}})
    messages = [{"role": "user", "content": content}]
    doc, last = None, None
    for attempt in range(3):
        msg = client.messages.create(model=model, max_tokens=8000, system=SYSTEM, messages=messages, tools=[TOOL], tool_choice={"type": "auto"})
        call = next((b for b in msg.content if getattr(b, 'type', '') == 'tool_use'), None)
        if call is None:
            last = "no tool call"; messages += [{"role": "assistant", "content": msg.content}, {"role": "user", "content": "You must call write_direction with the document. Do it now."}]; continue
        doc = call.input; errs = validate(doc)
        if not errs: break
        last = '; '.join(errs)
        messages += [{"role": "assistant", "content": msg.content}, {"role": "user", "content": [{"type": "tool_result", "tool_use_id": call.id, "content": f"Rejected: {last}. Call write_direction again with a corrected document."}]}]
    if doc is None: raise SystemExit(f'direct: no document ({last})')
    out = os.path.join(slug_dir, 'direction.json'); json.dump(doc, open(out, 'w'), indent=1, ensure_ascii=False)
    return doc

if __name__ == '__main__':
    d = direct(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'claude-sonnet-5-5')
    print(json.dumps({k: d.get(k) for k in ('kind', 'concept', 'mode', 'voice')}), '· beats:', [b['type'] for b in d['beats']])
