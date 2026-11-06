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
   {"id":"...","type":"cells","label":"...","h2":"...","lede":"...","cells":[["label","big number","sub"],...3-6]},
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
- Pick 4–6 beats only. One screen each. Photographs lead for a place/service; the ledger (real items + prices) is the artefact for a restaurant/shop/clinic; cells/steps for software.
- Choose images by id from images.json: the hero gets the best 'heroGrade' landscape photo; never reuse the same image twice.
- Output ONLY the JSON document, no prose, matching the schema. Comments in the schema are for you, not for the output.
"""

def load(slug_dir):
    def j(n):
        p = os.path.join(slug_dir, n); return json.load(open(p)) if os.path.exists(p) else None
    inv, assets, images, audit = j('inventory.json'), j('assets.json'), j('images.json'), j('audit.json')
    imgs_meta = [{k: v for k, v in i.items() if k != 'data'} for i in (images or [])]
    return inv, assets, imgs_meta, audit

def direct(slug_dir, model='claude-sonnet-5-5'):
    import anthropic
    inv, assets, imgs, audit = load(slug_dir)
    rules = '\n\n'.join(f'### {r}\n' + open(os.path.join(ROOT, r)).read() for r in RULES)
    user = f"""RULES\n{rules}\n\nSCHEMA\n{SCHEMA}\n\nINVENTORY (what the site HAS)\n{json.dumps(inv, ensure_ascii=False)[:60000]}\n\nBRAND ASSETS\n{json.dumps({k: v for k, v in (assets or {}).items() if k != 'logo'}, ensure_ascii=False)[:6000]}\n\nIMAGES (ids you may use)\n{json.dumps(imgs, ensure_ascii=False)[:6000]}\n\nAUDIT\n{json.dumps(audit, ensure_ascii=False)[:8000] if audit else 'n/a'}\n\nWrite direction.json now."""
    client = anthropic.Anthropic()
    msg = client.messages.create(model=model, max_tokens=8000, system=SYSTEM, messages=[{"role": "user", "content": user}])
    text = ''.join(b.text for b in msg.content if getattr(b, 'type', '') == 'text')
    m = re.search(r'\{.*\}', text, re.S)
    doc = json.loads(m.group(0))
    out = os.path.join(slug_dir, 'direction.json'); json.dump(doc, open(out, 'w'), indent=1, ensure_ascii=False)
    return doc

if __name__ == '__main__':
    d = direct(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'claude-sonnet-5-5')
    print(json.dumps({k: d.get(k) for k in ('kind', 'concept', 'mode', 'voice')}), '· beats:', [b['type'] for b in d['beats']])
