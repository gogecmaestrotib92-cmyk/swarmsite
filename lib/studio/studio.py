"""studio.py — a page for one client, composed from authored scenes: a story, a type system, a palette, scenes in order.

  python3 lib/studio/studio.py <evidence dir> <out dir> [--variants 3] [--model claude-opus-5-5]

The art director (one model call per variant) decides what a designer decides — the story, which type system suits this
client's voice, which palette scheme, which scenes in which order, what goes in each slot — and draws nothing: every
composition is lib/studio/scenes.py, every motion is lib/devices. Variants are told to differ in story, type and scheme,
so an owner can choose; the choice is the data a judge can later be trained on.
Checks: every number against the evidence, every link the client's own, pictures real and used once, layout at five
widths (lib/qa/layout.mjs). A plan that fails is sent back once with the reasons. Nothing is deployed."""
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'lib'))
import _evidence as E, scenes as S

SYSTEM = """You are the art director of a studio, composing a client's new homepage from the studio's own SCENES. A scene is a finished composition — layout, motion and picture rules are already decided and measured; you choose scenes, order them as a story, and fill their slots with the client's own material. You draw nothing and you invent nothing.

THE STORY comes first. Before choosing a scene, decide: what does a visitor not know or not believe when they arrive; what one thing, once seen, changes that; what proves it; what they should do. The page is that argument in order: open → show → prove → breathe → decide → close. Never the stock order (hero, features, stats, pricing, FAQ) for its own sake: a scene earns its place by moving the argument, and a scene that only repeats an earlier one is cut.

HOW TO CHOOSE
- Type system: by the client's voice (read the names in TYPE). If the client's own headline face is one of them in spirit, keep that character.
- Scheme: "paper", "night" or "tint" — from the client's brand and from what its pictures need (dark screenshots sit badly on white unless framed; photographs want paper).
- A place (restaurant, hotel, shop) is shown with its photographs: "open-picture", "window", "gallery", its list as a "carte", and "visit" for where and when. Software is shown with "held-product", "stage", "figures". When there is no picture strong enough to open on, "open-atmosphere" or "open-statement".
- TWO SEPARATE DECISIONS. What kind of page it is decides WHAT is shown; the client's character decides HOW. Never let the trade choose the look: a sports-prediction product and a bank's API are both software and must not look alike.
- Character first. Read EVIDENCE.brand.character (measured on the client's page: how it sets its headline, its ground, its accent), its photographs and its words, then state "character" and "character_why". Type system, scheme and movement follow the character: energetic → "condensed-caps" or "tight-bold", the client's dark ground when it has one, its vivid accent, "kinetic-line" or "rail" welcome; calm → "light-grotesk" or "wide-geometric", few scenes, nothing that slides; warm → "soft-serif"; refined → "display-serif"; playful → "wide-geometric" or "tight-bold" with the accent used freely. Keep the client's own ground: a brand that lives on black is not moved to white paper, nor the reverse, unless a variant is told to differ in scheme.
- Software (an app, a SaaS product, a tool for developers) takes "scale": "product" and opens on "open-product" when there is a real screenshot of it: the product is the picture and the line is short. When the client has a wide photograph of its own world (a stadium, a kitchen, a workshop), name it as the "ground" of "open-product" so the product stands in that world. Its plans go in "plans" and, when the client publishes a feature comparison, "compare" — only what the client states, never a price, a limit or a plan of your own. A calm software page leaves out "kinetic-line", "rail" and the closing wordmark; an energetic one may use them.
- THE PARTS OF A SOFTWARE PAGE, top to bottom — use what the client has the material for, and do not repeat one form:
  · opening: "open-product" with "align": "beside" when the line is long and the screenshot wide; with "more" (two or three more screenshots or crops) when the product is best shown as pieces; "news" when the client announces one new thing.
  · "logos" directly after the opening whenever EVIDENCE.logos is present (label = said_with_them).
  · showing: "features" (cards; give it the client's photograph as "ground" when it has one), "lines" (ruled rows with links — for a product of named parts), "tabs" (two to four modes, one word each), "held-product" (claims read one at a time), "code" (only code the client itself publishes). Choose two of these at most, of different form.
  · "chips" for a long list of names (features, methods, integrations); "figures" for numbers.
  · proving: "quote" for one strong testimonial, "voices" for two or three, "cases" for customer stories with links.
  · deciding: "plans" (with "tag" and the "switch" when the client publishes both prices), "compare", "faq".
  · ending: "ways" (two to four next steps) before the close when the client has a demo, docs, a sandbox or pricing to send people to; "close" with "form": "centre" for software (or "card" on a photograph, or "split"), the "wordmark" ("faint" for a calm brand); "tone": "paper" when the page is light and calm. "reads" only for real articles.
- Movement the visitor makes happen: set "cover": true on one or two scenes where the argument turns (after the product has been shown, before the plans or the proof) — that scene slides up over the one before it. The product in "open-product" rises into place by itself. Cards arrive one at a time.
- "features" shows three to five things the product does, each in a card with its own real screenshot or crop — use it whenever a software client has three or more screenshots; it replaces icon lists. "held-product" is for claims that need to be read one at a time.
- The first screen always shows a picture when the client has one: a place opens on "open-picture", software on "open-product". "open-statement" is for a client with no usable picture at all.
- In SEO-safe jobs the h1 keeps at least half of the content words of the client's own h1 (EVIDENCE.h1). Write the stronger line around those words; do not move them to the label above.
- A place is its rooms. Every room, terrace or space the client names and has a photograph of is shown by that photograph, and the photographs of the place itself lead: a dish or a detail never takes the first or the largest place in a scene about the place. Put the largest, sharpest photograph of the place where it is seen widest.
- "statement" carries the thesis once, early. "steps" shows how something goes when the client describes a process. "rooms" holds words while two to four of the client's photographs pass. "voices" only with testimonials given to you, word for word. "faq" for six or more questions, "ledger" for fewer.
- "scatter" sets three to five of the client's pictures in rows that close — one large with two beside it, or two side by side — each cropped to its place (work, dishes, rooms, products). The sharpest takes the largest place; a picture marked soft is left out of it. "bento" sets four to six facts in tiles of different sizes when there is little to picture. "kinetic-line" is a statement in two or three huge rows that slide apart — use it or "rail", never both.
- "collage" lays exactly three sharp photographs over one another, each drifting at its own pace — only for a place or a maker with three strong photographs; use it or "scatter", never both.
- Scheme "tone" (three steps of one muted tone from the brand colour) suits brands whose colour is strong and whose pictures are few.
- 5–9 scenes including exactly one opening and one close. At most one "rail". Use "held-product" only with three or more claims that each have something to SHOW; give every panel the tightest, most readable real picture (prefer crops made for the purpose over whole pages of small text) or real figures. Use "stage" for the one whole screen worth seeing large. Use "figures" only for numbers that are an argument.
- Headings are written for their scene: display lines are short and break into rows with " / " (2–3 rows, 1–4 words a row); mark ONE phrase per line with *asterisks* at most. A heading over cards must agree with the number of cards.
- Secondary pages go in one "index" near the end (6–12 links, short names). Nothing is repeated, nothing is dumped.

RULES THAT ARE NOT YOURS TO BEND
- Every fact, number, price, name and claim comes from the evidence, in the client's meaning. Reword for length; never add. An empty slot is better than an invented one.
- Look at each picture before you use it. A picture that is a document, a notice, a poster of text, a certificate, a map, a logo or a screenshot of a website is NOT a photograph and is never shown, whatever its label says. A still from the client's own film is the client's own picture and may be shown.
- Every url is one of the links given. Every image id is one given; a generated picture is never shown as the product; a picture is used once.
- Write in the language of the client's site. Plain and specific. No exclamation marks, no marketing filler.
- brand.accent and brand.night are the client's OWN signature colour and darkest ground (hex)."""

TOOL = {'name': 'compose_page', 'description': 'The whole page as a plan.', 'input_schema': {'type': 'object', 'required': ['story', 'brand', 'character', 'character_why', 'type', 'scheme', 'action', 'scenes'], 'properties': {
    'story': {'type': 'object', 'required': ['doubt', 'turn', 'proof', 'ask'], 'properties': {'doubt': {'type': 'string', 'description': 'what the visitor does not know or believe on arrival'}, 'turn': {'type': 'string', 'description': 'the one thing that, once seen, changes that'}, 'proof': {'type': 'string'}, 'ask': {'type': 'string'}, 'idea': {'type': 'string', 'description': 'the one idea every scene expresses'}}},
    'title': {'type': 'string'}, 'description': {'type': 'string'},
    'brand': {'type': 'object', 'required': ['name', 'accent', 'night'], 'properties': {'name': {'type': 'string'}, 'accent': {'type': 'string'}, 'night': {'type': 'string'}, 'lang': {'type': 'string'}}},
    'type': {'type': 'string', 'enum': list(S.TYPE)}, 'scheme': {'type': 'string', 'enum': list(S.SCHEMES)}, 'character': {'type': 'string', 'enum': ['calm', 'energetic', 'warm', 'refined', 'playful'], 'description': 'the temperament of THIS client, whatever its trade: calm (exact, technical, quiet), energetic (sport, games, nightlife, loud launches), warm (hospitality, craft, family), refined (luxury, editorial, finance that wants to look old), playful (consumer apps, children, food with a wink)'},
    'character_why': {'type': 'string', 'description': 'what on the client\'s own page shows this character — its headline face and weight, its ground, its accent, its photographs, its words. One sentence, naming them'},
    'scale': {'type': 'string', 'enum': ['display', 'product'], 'description': '"display": headlines set very large, the page led by type and photographs (places, brands, studios). "product": software — headlines near 64 px, quick small reveals, the product screenshots are the pictures'}, 'eased': {'type': 'boolean', 'description': 'the page glides to a stop after the wheel (desk only)'},
    'why': {'type': 'string', 'description': 'why this type system and scheme for this client, in two sentences'},
    'nav': {'type': 'array', 'description': 'up to five; an item may hold "links" (2–6 of the client\'s own pages) instead of a url — it then opens a small panel', 'items': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'url': {'type': 'string'}, 'links': {'type': 'array', 'items': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'url': {'type': 'string'}}}}}}},
    'guides': {'type': 'boolean', 'description': 'true: hairline column guides run down the page behind everything — for exact, technical, financial brands; never with photographs as grounds'},
    'action': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'url': {'type': 'string'}}}, 'action2': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'url': {'type': 'string'}}},
    'scenes': {'type': 'array', 'minItems': 5, 'maxItems': 11, 'items': {'type': 'object', 'required': ['scene', 'moves', 'slots'], 'properties': {'scene': {'type': 'string', 'enum': list(S.SCENES)}, 'moves': {'type': 'string', 'description': 'how this scene moves the argument forward'}, 'cover': {'type': 'boolean', 'description': 'true: this scene slides up over the one before it, which stays in place — once or twice a page, where the argument turns; never the first scene, never two in a row'}, 'slots': {'type': 'object'}}}}}}}


known_quotes = []


def owed(ev, images):
    """What this client's material obliges a page to do, worked out once: the screenshots that can open a software page,
    the crisp wide photographs that can open a place, the photographs that can lie behind a product (these may be soft —
    they are grounds), and the words its own headline is found by. check() refuses a plan against these, and build()
    says them to the composer before its first try: a rule first heard as a refusal costs a second call."""
    wide = lambda i: int(i.get('w') or 0) >= 1000 and int(i.get('w') or 0) >= 1.2 * int(i.get('h') or 1)
    mine = [i for i in images.values() if not i.get('logo') and not i.get('gen')]
    shots = [i['id'] for i in mine if ev.get('kind') == 'software' and i.get('shot') and not i.get('soft') and int(i.get('w') or 0) >= 900]
    photos = [i['id'] for i in mine if not i.get('shot') and not i.get('soft') and not i.get('video') and wide(i)]
    grounds = [i['id'] for i in mine if not i.get('shot') and not i.get('video') and wide(i)]
    import seo as SEO_
    words = SEO_.keywords(ev['h1']) if ev.get('h1') and ev.get('seo_safe', True) else []
    return shots, photos, grounds, words


def briefing(ev, images):
    """The same obligations as sentences for the composer, for this client."""
    shots, photos, grounds, words = owed(ev, images); out = []
    if shots: out.append(f'This is software with real screenshots: with "scale": "product" the page OPENS on "open-product", its "image" one of {shots[:5]}.')
    if grounds and shots: out.append(f'The client has photographs of its own world {grounds[:4]}: name one as the "ground" of "open-product" (a ground may be soft or dark — it lies behind the product), unless you show the product as a cluster with "more".')
    if photos and not shots: out.append(f'The client has wide, crisp photographs {photos[:5]}: the first screen shows one — open on "open-picture", not on "open-statement".')
    if words: out.append(f'The h1 itself keeps at least {max(1, (len(words) + 1) // 2)} of these words the client\'s page is found by: {words}. Build the stronger line around them.')
    if (ev.get('logos') or {}).get('count'): out.append(f'{ev["logos"]["count"]} customer logos were captured: place "logos" directly after the opening, labelled "{ev["logos"].get("said_with_them") or ""}".')
    return ('CHECKED BEFORE THIS PAGE SHIPS — a plan that misses one is sent back, which costs a second try:\n- ' + '\n- '.join(out)) if out else ''


def check(plan, page, ev, allowed, images):
    bad = {'invented_numbers': E.invented_numbers(re.sub(r'src="data:[^"]+"', '', page), json.dumps(ev, ensure_ascii=False)), 'foreign_links': [], 'pictures': [], 'structure': []}
    for href in set(re.findall(r'<a\b[^>]*\bhref="([^"]+)"', page)):
        if not href.startswith('#') and href.rstrip('/') not in allowed: bad['foreign_links'].append(href[:90])
    used = re.findall(r'"image":\s*"([^"]+)"', json.dumps(plan))
    for pid in used:
        if pid not in images: bad['pictures'].append(f'{pid}: not a picture of this client')
        elif images[pid].get('gen'): bad['pictures'].append(f'{pid}: a generated picture shown as the product')
    if len(set(used)) != len(used): bad['pictures'].append('a picture is used more than once')
    for sc in plan.get('scenes') or []:   # a picture shown edge to edge has to be large enough to be sharp there
        pid = (sc.get('slots') or {}).get('image')
        if sc.get('scene') in ('open-picture', 'window', 'stage') and pid in images and images[pid].get('soft'):
            bad['pictures'].append(f'{pid}: out of focus (or a frame of a video) — not a picture to show across the screen in "{sc["scene"]}"')
        elif sc.get('scene') in ('open-picture', 'window', 'stage') and pid in images and (max(int(images[pid].get('w') or 0), int(images[pid].get('h') or 0)) < 900 or int(images[pid].get('sharp_w') or 900) < 900):
            bad['pictures'].append(f'{pid}: {images[pid].get("w")}×{images[pid].get("h")} px (crisp up to {images[pid].get("sharp_w") or images[pid].get("w")} px) is too small to be shown across the screen in "{sc["scene"]}" — use a larger picture or a scene that shows it small')
        if sc.get('scene') == 'open-product':   # the product on the first screen has to be read
            im = images.get(pid)
            if not im: bad['pictures'].append('"open-product" has no screenshot — use "open-statement"')
            else:
                phone = .42 <= int(im.get('w') or 1) / max(1, int(im.get('h') or 1)) <= .62
                if not im.get('shot') and not phone: bad['pictures'].append(f'{pid}: "open-product" shows the product itself — a screenshot of it, or a phone screen; this is a photograph or a cover')
                elif im.get('soft') or (not phone and int(im.get('w') or 0) < 900): bad['pictures'].append(f'{pid}: too small or too soft to stand as the product on the first screen — a wide screenshot needs 900 px')
            g = images.get((sc.get('slots') or {}).get('ground'))
            if (sc.get('slots') or {}).get('ground') and (not g or g.get('shot') or g.get('gen') or int(g.get('w') or 0) < 1000): bad['pictures'].append('"open-product": the ground behind the product is one of the client\'s own photographs at least 1000 px wide — not a screenshot (it may be soft: it lies behind the product)')
        if sc.get('scene') == 'compare':
            cols = (sc.get('slots') or {}).get('columns') or []
            if any(len(r.get('values') or []) != len(cols) for g in (sc.get('slots') or {}).get('groups') or [] for r in g.get('rows') or []): bad['structure'].append('"compare": every row needs one value for each column')
        if sc.get('scene') == 'collage':   # pictures laid over one another are each seen large: every one has to hold
            for p in (sc.get('slots') or {}).get('pictures') or []:
                im = images.get(p.get('image'))
                if im and (im.get('soft') or im.get('video') or im.get('shot') or int(im.get('w') or 0) < 900): bad['pictures'].append(f'{p.get("image")}: "collage" takes only sharp photographs at least 900 px wide — use "scatter", which shows pictures small')
    quotes = [q.get('text') for s in plan.get('scenes') or [] if s.get('scene') == 'voices' for q in (s.get('slots') or {}).get('quotes') or []] + [(s.get('slots') or {}).get('text') for s in plan.get('scenes') or [] if s.get('scene') == 'quote']
    source = ' '.join(json.dumps(ev, ensure_ascii=False).split())
    for q in quotes:
        if q and ' '.join(str(q).split())[:60] not in source and ' '.join(str(q).split())[:60] not in ' '.join(known_quotes): bad['pictures'].append('a quote that is not on the client\'s site, word for word')
    # What the page owes its first screen and the client's search standing is checked here, where a plan can still be sent
    # back — on SportBotAI (2026-11-11) all of it was advice, and the page that shipped opened on words alone, left the
    # stadium unused and dropped the words its headline ranked for.
    scenes_ = plan.get('scenes') or []; first = (scenes_[0] if scenes_ else {}); slots0 = first.get('slots') or {}
    wide = lambda i: int(i.get('w') or 0) >= 1000 and int(i.get('w') or 0) >= 1.2 * int(i.get('h') or 1)
    shots, photos, grounds, words = owed(ev, images)
    if plan.get('scale') == 'product' and shots and first.get('scene') != 'open-product':
        bad['structure'].append(f'software with a real screenshot opens on "open-product" (the product is the picture of the first screen): use one of {shots[:4]}')
    elif first.get('scene') == 'open-statement' and (photos or shots):
        bad['structure'].append(f'the first screen shows no picture although the client has one: open on "open-picture" with one of {photos[:4]}' + (f' or on "open-product" with one of {shots[:4]}' if shots else ''))
    if first.get('scene') == 'open-product' and grounds and not slots0.get('ground') and not slots0.get('more'):   # a cluster of pieces stands on the page itself
        bad['pictures'].append(f'the client has a wide photograph of its own world {grounds[:4]}: name one as the "ground" of "open-product" so the product stands in it')
    if ev.get('h1') and ev.get('seo_safe', True):
        import seo as SEO_
        said = re.sub(r'[*/]', ' ', str(slots0.get('h1') or '')); kept = SEO_.keyword_coverage(ev['h1'], said)
        if kept < .5: bad['structure'].append(f'the headline keeps {round(kept * 100)}% of the words the client\'s page is found by ("{str(ev["h1"])[:80]}" — {SEO_.keywords(ev["h1"])}): at least half of them stand in the h1 itself, not only in the label above it')
    for sc in scenes_:
        if sc.get('scene') == 'features':
            for it in (sc.get('slots') or {}).get('items') or []:
                im = images.get(it.get('image'))
                if im is None: bad['pictures'].append(f'"features": {it.get("image")} is not a picture of this client — every card holds a real screenshot')
                elif im.get('soft') or im.get('gen'): bad['pictures'].append(f'"features": {it.get("image")} is soft or generated — a card holds the real interface, crisp')
    for sc in scenes_:
        sl = sc.get('slots') or {}
        if sc.get('scene') == 'logos' and not (ev.get('logos') or {}).get('count'): bad['structure'].append('"logos" needs the customer logos captured from the client\'s page, and none were found: leave the scene out')
        if sc.get('scene') == 'code':
            def said(v): return ''.join(said(x) for x in (v.values() if isinstance(v, dict) else v)) if isinstance(v, (dict, list)) else str(v) if isinstance(v, str) else ''
            flat = lambda t: re.sub(r'\s+', '', str(t or ''))
            if flat(sl.get('code'))[:80] not in flat(said(ev)): bad['structure'].append('"code": the code must be the client\'s own, as its page publishes it — this block is not in the evidence')
        if sc.get('scene') == 'plans' and sl.get('switch') and not all(p.get('price_b') for p in sl.get('plans') or [] if re.search(r'[1-9]', str(p.get('price') or ''))): bad['structure'].append('"plans": the switch needs the second price on every paid plan, as the client publishes it — or no switch')
        if sc.get('scene') == 'close' and sl.get('form') == 'card':
            g = images.get(sl.get('ground'))
            if not g or g.get('shot') or int(g.get('w') or 0) < 1000: bad['pictures'].append('"close" as a card lies on one of the client\'s own photographs at least 1000 px wide: name it in "ground", or use form "centre"')
    shown = [sc.get('scene') for sc in scenes_ if sc.get('scene') in ('features', 'lines', 'tabs', 'held-product', 'code')]
    if len(shown) > 3: bad['structure'].append(f'the product is shown {len(shown)} times over ({shown}): two forms, three at most')
    covers = [k for k, sc in enumerate(scenes_) if sc.get('cover') in (True, 'true')]
    if len(covers) > 2 or 0 in covers or any(b - a == 1 for a, b in zip(covers, covers[1:])): bad['structure'].append('"cover" is for one or two scenes where the argument turns: not the first scene, not two in a row')
    roles = [S.SCENES[s['scene']]['role'] for s in plan.get('scenes') or [] if s.get('scene') in S.SCENES]
    if roles.count('open') != 1 or roles[:1] != ['open']: bad['structure'].append('exactly one opening scene, first')
    if roles.count('close') != 1 or roles[-1:] != ['close']: bad['structure'].append('exactly one close, last')
    body = re.sub(r'<(script|style)\b.*?</\1>', ' ', page, flags=re.S); h1 = re.search(r'<h1\b[^>]*>(.*?)</h1>', body, re.S)
    if not h1 or not re.sub(r'<[^>]+>|\s', '', h1.group(1)): bad['structure'].append('the opening has no headline')
    if len(re.sub(r'<[^>]+>', ' ', body).split()) < 60: bad['structure'].append('the page says almost nothing')
    for s in plan.get('scenes') or []:
        if s.get('scene') == 'stack':
            n = len((s.get('slots') or {}).get('cards') or []); words = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'dva': 2, 'tri': 3, 'dos': 2, 'tres': 3}
            said = [v for w, v in words.items() if re.search(rf'\b{w}\b', str((s.get('slots') or {}).get('h2') or ''), re.I)]
            if said and said[0] != n: bad['structure'].append(f'the stack\'s heading says {said[0]} and shows {n} cards')
    return bad


def one(material, ev, allowed, images, out, tag, hint, types=None):
    ask = material + [{'type': 'text', 'text': hint + '\nCompose the page. Call compose_page.'}]; plan = page = bad = None; tries = []
    for k in range(2):
        plan = E.call(SYSTEM, ask, f'{tag}-compose-{k}', tool=TOOL, max_tokens=14000)
        with open(os.path.join(out, f'plan-{tag}-{k}.json'), 'w', encoding='utf-8') as f: json.dump(plan, f, indent=1, ensure_ascii=False)
        if types and plan.get('type') not in types: plan['type_asked'] = plan.get('type'); plan['type'] = types[0]   # variants differ by construction: each of B and C has its own share of the type systems
        page = S.page(plan, images); bad = check(plan, page, ev, allowed, images); path = os.path.join(out, f'page-{tag}.html')
        with open(path, 'w', encoding='utf-8') as f: f.write(page)
        try:
            lay = subprocess.run(['node', os.path.join(ROOT, 'lib', 'qa', 'layout.mjs'), path], capture_output=True, text=True, timeout=240, cwd=ROOT); bad['layout'] = [{x: b.get(x) for x in ('kind', 'section', 'text', 'detail', 'widths')} for b in json.loads(lay.stdout.strip().splitlines()[-1])['breaks']]
        except Exception as err: bad['layout'] = [{'kind': 'unmeasured', 'detail': str(err)[:100]}]
        tries.append(bad)
        if not any(bad.values()): break
        ask = material + [{'type': 'text', 'text': hint + '\nYOUR PREVIOUS PLAN:\n' + json.dumps(plan, ensure_ascii=False) + '\n\nIT WAS RENDERED AND CHECKED, AND REFUSED FOR:\n' + json.dumps(bad, ensure_ascii=False) + '\n(A layout break names the scene and the text: shorten or re-break that heading, or choose another scene.)\nCorrect exactly these and call compose_page again with the whole page.'}]
    return {'tag': tag, 'type': plan.get('type'), 'scheme': plan.get('scheme'), 'story': plan.get('story'), 'why': plan.get('why'), 'scenes': [s.get('scene') for s in plan.get('scenes') or []], 'checks': tries, 'clean': not any(tries[-1].values())}


PICK_TOOL = {'name': 'pick', 'description': 'Which candidate, if any, may stand behind a headline.', 'input_schema': {'type': 'object', 'required': ['choice', 'why'], 'properties': {
    'choice': {'type': 'integer', 'description': 'the number of the one candidate that passes, or 0 to reject them all'}, 'why': {'type': 'string'},
    'faults': {'type': 'array', 'items': {'type': 'string'}, 'description': 'what disqualified the others: text or letters, a face or a hand, an interface, a recognisable object or logo, muddy or garish colour, the look of stock AI art'}}}}


def atmosphere(ev, plan_hint, out, n=3):
    """A commissioned ground for the opening: abstract, in the client's own colours, claiming nothing. Several are made
    and a strict second look keeps at most one — rejecting them all is a normal outcome and the page then opens on type.
    Returns an image record ({'id': 'atmos', 'gen': True, …}) or None, and what happened."""
    sys.path.insert(0, os.path.join(ROOT, 'lib', 'swarm'))
    import base64, io, gen as G
    from PIL import Image
    from concurrent.futures import ThreadPoolExecutor
    if not G.enabled(): return None, {'made': 0, 'why': 'no image key in this environment'}
    cols = [c.get('c') for c in ((ev.get('brand') or {}).get('colours') or {}).get('bg') or [] if isinstance(c, dict)][:3]
    prompt = (f'Abstract photographic study of light and material, no subject. Wide soft bands and folds of light crossing a deep dark field, one clear direction of movement, large calm empty areas for text. '
              f'Colour strictly from this palette: {", ".join(cols) or "near black"} with a single accent of {plan_hint}. Fine film grain, shallow depth, studio lighting, restrained, minimal, editorial. '
              'Absolutely no text, no letters, no numbers, no logos, no people, no faces, no hands, no screens, no interface, no devices, no objects, no buildings, no borders.')
    def one(k):
        try:
            im = Image.open(io.BytesIO(G.generate(prompt, '16:9'))).convert('RGB'); im.thumbnail((1920, 1920)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=86)
            return {'w': im.size[0], 'h': im.size[1], 'data': 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()}
        except Exception as err: return {'error': str(err)[:140]}
    with ThreadPoolExecutor(n) as ex: made = [m for m in ex.map(one, range(n))]
    good = [m for m in made if m.get('data')]
    for k, m in enumerate(good):
        with open(os.path.join(out, f'atmos-candidate-{k + 1}.jpg'), 'wb') as f: f.write(base64.b64decode(m['data'].split(',', 1)[1]))
    if not good: return None, {'made': 0, 'errors': [m.get('error') for m in made]}
    content = [{'type': 'text', 'text': f'{len(good)} candidates for the ground behind a homepage headline. The accent is {plan_hint}. Keep at most one. Reject any with text or letters, a face or hand, an interface or device, a recognisable object or logo, muddy or garish colour, or the plastic look of stock AI art. A ground must be calm enough to carry large white type.'}]
    for k, m in enumerate(good): content += [{'type': 'text', 'text': f'CANDIDATE {k + 1}'}, {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': E.thumb(m['data'], 1100)}}]
    verdict = E.call('You are a strict picture editor. Rejecting everything is a normal, respectable outcome.', content, 'atmosphere-pick', tool=PICK_TOOL, max_tokens=1500)
    k = verdict.get('choice') or 0; report = {'made': len(good), 'kept': k, 'why': verdict.get('why'), 'faults': verdict.get('faults')}
    return ({'id': 'atmos', 'gen': True, 'alt': '', **good[k - 1]} if 1 <= k <= len(good) else None), report


VARIANTS = [('a', 'VARIANT A — the page you believe is right for this client.'),
            ('b', 'VARIANT B — a different reading of the same client: a different type system and a different scheme from the obvious choice, a different opening scene if the material allows, and the story told in another order. It must still be true to the brand.'),
            ('c', 'VARIANT C — the boldest honest version: the fewest scenes that carry the argument, the largest type, one accent used once or twice. A different type system again.')]


def build(src, out, n=3, atmosphere_wanted=False):
    """Compose `n` variants of the page for the evidence in `src` into `out`; returns the report (also written to report.json)."""
    src, out = os.path.abspath(src), os.path.abspath(out); args = ['--atmosphere'] if atmosphere_wanted else []
    os.makedirs(out, exist_ok=True); t0 = time.time(); del E.USAGE[:]; del known_quotes[:]
    ev, imgs = E.evidence(src); images = {i['id']: i for i in imgs}; allowed = {l['url'].rstrip('/') for l in ev['links']} | {str(ev.get('url') or '').rstrip('/')}
    if len(re.findall(r'\w{3,}', json.dumps([ev['sections'], ev['factsheet']], ensure_ascii=False))) < 40:   # a restaurant's page can be 17 words and a full fact sheet: both count
        # Nothing to compose from: asking anyway buys an empty page that every check passes, because nothing in it is wrong.
        raise RuntimeError(f'the evidence in {src} holds no text of the client\'s site — nothing is composed from nothing')
    material = [{'type': 'text', 'text': 'THE STUDIO\'S SCENES, TYPE SYSTEMS AND SCHEMES:\n' + json.dumps(S.catalogue(), ensure_ascii=False, indent=1)}, {'type': 'text', 'text': 'THE EVIDENCE (the client\'s existing site):\n' + json.dumps(ev, ensure_ascii=False, indent=1)}]
    said = [{'text': ' '.join(str(t.get('text') or t.get('quote') or '').split())[:500], 'name': t.get('name') or t.get('author'), 'role': t.get('role')} for sec in ((E.J(src, 'inventory.json') or {}).get('sourceCoverage') or {}).get('sections') or [] for t in (sec.get('testimonials') or []) if isinstance(t, dict)]
    said = [t for t in said if t['text'] and t['name']][:8]; known_quotes.extend(t['text'] for t in said)
    material.append({'type': 'text', 'text': 'TESTIMONIALS FOUND ON THE CLIENT\'S SITE (the only words that may be shown as a quote): ' + (json.dumps(said, ensure_ascii=False) if said else 'none — the scene "voices" may not be used')})
    kind = (E.J(src, 'direction.json') or {}).get('kind') or (E.J(src, 'brief.json') or {}).get('kind') or 'software'
    ev['kind'] = kind; ev['seo_safe'] = str((E.J(src, 'brief.json') or {}).get('mode') or '').lower() not in ('free', 'studio', 'creative')   # read by check(): which pictures are the product, and whether the headline's keywords are owed
    shot_is = ' — screenshot of the real product' if kind == 'software' else ' — a SCREENSHOT OF THE CLIENT\'S OLD WEBSITE: not content, never shown'
    material.append({'type': 'text', 'text': f'KIND OF BUSINESS (as captured): {kind}'})
    told = briefing(ev, images)
    if told: material.append({'type': 'text', 'text': told})
    for i in [x for x in imgs if not x.get('logo')][:14]:
        try: material += [{'type': 'text', 'text': f'PICTURE {i["id"]} ({i.get("w")}×{i.get("h")})' + (' — GENERATED atmosphere, not the client\'s own' if i.get('gen') else (' — a crop of ' + i['crop_of'] if i.get('crop_of') else shot_is if i.get('shot') else (' — a still from the client\'s own film' if i.get('video') else ' — the client\'s own picture (look: is it a photograph?)')))}, {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': E.thumb(i['data'])}}]
        except Exception: pass
    made = None
    if '--atmosphere' in args:
        accent = next((c.get('c') for c in ((ev.get('brand') or {}).get('colours') or {}).get('buttons') or [] if isinstance(c, dict) and 'a0' not in str(c.get('c'))), None) or 'the brand\'s signature colour'
        pic, made = atmosphere(ev, accent, out)
        if pic: images['atmos'] = pic; material += [{'type': 'text', 'text': 'PICTURE atmos — a commissioned abstract ground in the client\'s colours, kept after a strict second look: the scene "open-atmosphere" stands on it (it is placed for you; do not name it in a slot)'}, {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': E.thumb(pic['data'])}}]
    from concurrent.futures import ThreadPoolExecutor
    first = one(material, ev, allowed, images, out, *VARIANTS[0]); results = [first]
    taken = f'\nVARIANT A ALREADY EXISTS: type system "{first["type"]}", scheme "{first["scheme"]}", opening "{(first["scenes"] or [""])[0]}", scenes {first["scenes"]}. You MUST choose a different type system'
    others = [t for t in S.TYPE if t != first['type']]; shares = [others[0::2], others[1::2]]   # B and C are composed at the same time: disjoint shares keep them from landing on one type system
    rest = [(VARIANTS[1][0], VARIANTS[1][1] + taken + f', one of {shares[0]}, and differ in the scheme or the opening scene as well.', shares[0]),
            (VARIANTS[2][0], VARIANTS[2][1] + taken + f', one of {shares[1]} — the third character this client could honestly have.', shares[1])][:max(0, n - 1)]
    with ThreadPoolExecutor(2) as ex: results += list(ex.map(lambda v: one(material, ev, allowed, images, out, v[0], v[1], v[2]), rest))
    priced = [u['usd'] for u in E.USAGE if u['usd'] is not None]
    report = {'atmosphere': made, 'variants': results, 'usage': E.USAGE, 'usd': round(sum(priced), 3), 'seconds': round(time.time() - t0)}
    with open(os.path.join(out, 'report.json'), 'w', encoding='utf-8') as f: json.dump(report, f, indent=1, ensure_ascii=False)
    return report


def main():
    args = sys.argv[1:]
    if '--model' in args: E.MODEL = args[args.index('--model') + 1]
    report = build(args[0], args[1], int(args[args.index('--variants') + 1]) if '--variants' in args else 3, '--atmosphere' in args)
    print(json.dumps({'variants': [(r['tag'], r['type'], r['scheme'], r['scenes'], r['clean']) for r in report['variants']], 'usd': report['usd'], 'seconds': report['seconds']}, ensure_ascii=False))


if __name__ == '__main__': main()
