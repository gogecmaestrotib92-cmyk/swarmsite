"""fill.py — a client's evidence set into a studio template's slots, held to the evidence, then drawn and measured.

  python3 lib/studio/fill.py <evidence dir> <out dir> [--template held_index] [--model claude-opus-5-5]

The template (lib/studio/<name>.py) is authored design: its markup, type, motion and composition are fixed. One model
call decides only what goes in its slots — which of the client's own words, numbers, links and pictures — and may not
write a fact, a number or a link the evidence does not hold. The page is rendered by the template, checked (every
number against the evidence, every link against the client's own), and measured by lib/qa/layout.mjs at five widths.
Writes <out>/content.json, page.html, checks.json. No production file is touched; nothing is deployed."""
import importlib, json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'lib'))
import _evidence as E

SYSTEM = """You are an editor and art director filling ONE fixed page design with a client's own material. The design is decided; you decide content. You are given the client's existing website as evidence (its words, facts, links, colours, pictures) and the design's slots.

The design, so you know what each slot is for:
- hero: a large light headline low on a full-bleed drawn backdrop (6–9 words, one phrase in *asterisks* takes the accent), a lede of two sentences at most, one main action and one quiet action.
- proof: a slow line of 4–8 short true facts in small capitals (numbers, limits, platforms) — each under 40 characters.
- statement: a small line on the left, a large line on the right (one *accent phrase*): the page's thesis, in the client's own terms.
- index: THE CENTRE OF THE PAGE. Three to five claims; their short titles (≤ 28 characters) stand as a held list on the left and light up one at a time while a panel for each scrolls past on the right. Every claim needs a panel that SHOWS it: kind "image" with one of the client's real screenshots (prefer whole screens of the product; give each picture to one claim only), or kind "bars" (2–5 real figures from the evidence, each with a share 0–1 for its bar length that is true to the numbers), or kind "rows" (3–6 real label/value pairs). A panel may carry a "chip" (a short mono caption, top) and a "foot" (a mono line, bottom). Then an h3 (one sentence) and a body (two sentences).
- ground: a dark section — what makes the client trustworthy: a heading with one *accent phrase* and 3–4 points (title + one sentence).
- cards: 3–4 ways in or plans, each a short title with a kicker (a price, a limit, an audience) and its link.
- directory: the secondary pages a visitor may want, 6–12 links with short names — a designed index, not everything the site has.
- closing: one line that asks for the action, and a short note (a caveat the client itself states, if any).
- footer: 2–4 columns of links, and the legal line as the client writes it.

Rules that are not yours to bend:
- Every fact, number, price, name and claim comes from the evidence, in the client's meaning. Reword for length and rhythm; never add. If the evidence does not say it, leave the slot empty.
- Every url is one of the links given. Every image id is one given, and a picture marked generated is never used as a panel.
- Write in the language of the client's site. Plain, specific, no marketing filler. No exclamation marks.
- brand.accent and brand.night are two of the client's OWN colours (hex): its signature colour, and its darkest ground."""

TOOL = {'name': 'fill_page', 'description': 'The content of every slot of the page.', 'input_schema': {'type': 'object', 'required': ['brand', 'hero', 'index', 'action'], 'properties': {
    'title': {'type': 'string'}, 'description': {'type': 'string'},
    'brand': {'type': 'object', 'required': ['name', 'accent', 'night'], 'properties': {'name': {'type': 'string'}, 'accent': {'type': 'string'}, 'night': {'type': 'string'}, 'lang': {'type': 'string'}}},
    'nav': {'type': 'array', 'items': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'url': {'type': 'string'}}}},
    'action': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'url': {'type': 'string'}}}, 'action2': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'url': {'type': 'string'}}},
    'hero': {'type': 'object', 'required': ['h1', 'lede'], 'properties': {'h1': {'type': 'string'}, 'lede': {'type': 'string'}, 'note': {'type': 'string'}}},
    'proof': {'type': 'array', 'items': {'type': 'string'}},
    'statement': {'type': 'object', 'properties': {'small': {'type': 'string'}, 'big': {'type': 'string'}}},
    'index': {'type': 'object', 'required': ['label', 'items'], 'properties': {'label': {'type': 'string'}, 'items': {'type': 'array', 'items': {'type': 'object', 'required': ['title', 'panel'], 'properties': {
        'title': {'type': 'string'}, 'h3': {'type': 'string'}, 'body': {'type': 'string'},
        'panel': {'type': 'object', 'required': ['kind'], 'properties': {'kind': {'type': 'string', 'enum': ['image', 'bars', 'rows']}, 'image': {'type': 'string'}, 'alt': {'type': 'string'}, 'chip': {'type': 'string'}, 'foot': {'type': 'string'},
                  'bars': {'type': 'array', 'items': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'value': {'type': 'string'}, 'share': {'type': 'number'}}}},
                  'rows': {'type': 'array', 'items': {'type': 'object', 'properties': {'k': {'type': 'string'}, 'v': {'type': 'string'}}}}}}}}}}},
    'ground': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'h2': {'type': 'string'}, 'points': {'type': 'array', 'items': {'type': 'object', 'properties': {'title': {'type': 'string'}, 'body': {'type': 'string'}}}}}},
    'cards': {'type': 'object', 'properties': {'h2': {'type': 'string'}, 'items': {'type': 'array', 'items': {'type': 'object', 'properties': {'kicker': {'type': 'string'}, 'title': {'type': 'string'}, 'url': {'type': 'string'}}}}}},
    'directory': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'links': {'type': 'array', 'items': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'url': {'type': 'string'}}}}}},
    'closing': {'type': 'object', 'properties': {'line': {'type': 'string'}, 'note': {'type': 'string'}}},
    'footer': {'type': 'object', 'properties': {'columns': {'type': 'array', 'items': {'type': 'object', 'properties': {'title': {'type': 'string'}, 'links': {'type': 'array', 'items': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'url': {'type': 'string'}}}}}}}, 'legal': {'type': 'string'}}}}}}


def check(content, page_html, ev, allowed, images):
    """What the filled page gets wrong against its evidence: numbers the evidence never says, links that are not the client's, pictures misused."""
    bad = {'invented_numbers': E.invented_numbers(re.sub(r'src="data:[^"]+"', '', page_html), json.dumps(ev, ensure_ascii=False)), 'foreign_links': [], 'pictures': []}
    for href in set(re.findall(r'<a\b[^>]*\bhref="([^"]+)"', page_html)):
        if not href.startswith('#') and href.rstrip('/') not in allowed: bad['foreign_links'].append(href[:90])
    used = [((i.get('panel') or {}).get('image')) for i in (content.get('index') or {}).get('items') or [] if (i.get('panel') or {}).get('kind') == 'image']
    for pid in used:
        if pid not in images: bad['pictures'].append(f'{pid}: not a picture of this client')
        elif images[pid].get('gen'): bad['pictures'].append(f'{pid}: a generated picture shown as the product')
    if len(set(used)) != len(used): bad['pictures'].append('one picture used for two claims')
    return bad


def main():
    args = sys.argv[1:]; src, out = os.path.abspath(args[0]), os.path.abspath(args[1]); name = args[args.index('--template') + 1] if '--template' in args else 'held_index'
    if '--model' in args: E.MODEL = args[args.index('--model') + 1]
    os.makedirs(out, exist_ok=True); t0 = time.time(); template = importlib.import_module(name)
    ev, imgs = E.evidence(src); images = {i['id']: i for i in imgs}; allowed = {l['url'].rstrip('/') for l in ev['links']} | {str(ev.get('url') or '').rstrip('/')}
    material = [{'type': 'text', 'text': 'THE EVIDENCE (the client\'s existing site):\n' + json.dumps(ev, ensure_ascii=False, indent=1)}]
    for i in imgs[:12]:
        try: material += [{'type': 'text', 'text': f'PICTURE {i["id"]} ({i.get("w")}×{i.get("h")})' + (' — GENERATED, not the product' if i.get('gen') else '')}, {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': E.thumb(i['data'])}}]
        except Exception: pass
    ask = material + [{'type': 'text', 'text': 'Fill the page. Call fill_page.'}]; content = None; rounds = []
    for k in range(3):
        content = E.call(SYSTEM, ask, f'fill-{k}', tool=TOOL, max_tokens=9000)
        with open(os.path.join(out, f'content-{k}.json'), 'w', encoding='utf-8') as f: json.dump(content, f, indent=1, ensure_ascii=False)   # what was paid for is kept before anything can fail
        page = template.render(content, images); bad = check(content, page, ev, allowed, images); rounds.append(bad)
        if not any(bad.values()): break
        ask = material + [{'type': 'text', 'text': 'YOUR PREVIOUS ANSWER:\n' + json.dumps(content, ensure_ascii=False) + '\n\nIT WAS CHECKED AGAINST THE EVIDENCE AND REFUSED:\n' + json.dumps(bad, ensure_ascii=False) + '\n\nCorrect exactly these and call fill_page again with the whole page.'}]
    with open(os.path.join(out, 'content.json'), 'w', encoding='utf-8') as f: json.dump(content, f, indent=1, ensure_ascii=False)
    path = os.path.join(out, 'page.html')
    with open(path, 'w', encoding='utf-8') as f: f.write(page)
    try:
        lay = subprocess.run(['node', os.path.join(ROOT, 'lib', 'qa', 'layout.mjs'), path], capture_output=True, text=True, timeout=240, cwd=ROOT); breaks = json.loads(lay.stdout.strip().splitlines()[-1])['breaks']
    except Exception as err: breaks = [{'kind': 'unmeasured', 'detail': str(err)[:120]}]
    priced = [u['usd'] for u in E.USAGE if u['usd'] is not None]
    report = {'template': name, 'checks': rounds, 'layout': breaks, 'usage': E.USAGE, 'usd': round(sum(priced), 3), 'seconds': round(time.time() - t0)}
    with open(os.path.join(out, 'checks.json'), 'w', encoding='utf-8') as f: json.dump(report, f, indent=1, ensure_ascii=False)
    print(json.dumps({'checks': rounds[-1], 'layout': [(b['kind'], b.get('section'), b.get('widths')) for b in breaks], 'usd': report['usd'], 'seconds': report['seconds']}, ensure_ascii=False))


if __name__ == '__main__': main()
