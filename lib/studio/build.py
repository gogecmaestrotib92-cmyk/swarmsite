"""build.py — a page designed for one client and built from the device library, not from a template and not from a model's habits.

  python3 lib/studio/build.py <evidence dir> <out dir> [--model claude-opus-5-5] [--rounds 1]

What decides the page is not in the model: the DEVICES (lib/devices/registry.py — what award-level pages do, measured,
written once as our code) and the RULES those pages share as whole pages (display size, text size, grounds, length).
The model is the art director who chooses and composes: it reads the client's evidence, writes a direction that names
the devices each section uses and why, then writes the page's own markup and layout CSS. It does not write motion: a
device's stylesheet and script are injected from the library, byte for byte; a class it invents that looks like a
device (dv-…) is refused.

Held to the same fence as every experiment here: static HTML, opened only in a browser cut off from the network, every
number checked against the evidence, every link the client's own, layout measured at five widths, then looked at and
revised. Nothing is deployed. Writes direction.json, round-<n>.html, page.html, report.json."""
import json, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'lib')); sys.path.insert(0, os.path.join(ROOT, 'lib', 'devices'))
import _evidence as E, registry as LIB

HOUSE = """You are the art director of a studio. A client's existing website is in front of you as evidence — its words, facts, links, colours, pictures. You design and write its new homepage.

You do not work from your own habits. You work from the studio's LIBRARY and RULES below. The library is what award-level pages actually do — each device was measured on real award-winning sites and written once as tested code. The rules are what sixteen measured Sites of the Month share as whole pages. A page that could have been produced without this library is a failure of the brief.

HOW A PAGE IS MADE HERE
1. One idea. Say what is true of this client and of no competitor, and the one drawable idea the whole page expresses.
2. The page is a sequence of SCENES, not a stack of blocks. A scene is one thing shown at full attention: a held list with the product passing beside it, one picture growing to the edges, a row that moves sideways, cards that pile up. Between scenes, quiet. Most of a page is quiet so that three or four scenes can be loud.
3. Type carries the page: ONE display size that is very large, running text that is small, and almost nothing in between (see RULES for the measured numbers). Few grounds — one or two colours of ground for the whole page, the accent used sparingly.
4. The product is shown, not described: the client's real screenshots, whole and large, or their real numbers drawn (figure-bars). Never a fake interface, never an invented figure.
5. Curate. The homepage carries what a visitor needs to understand and decide; secondary pages get one designed index near the end. No runs of links, nothing repeated.

THE HOUSE TASTE (the owner's, read from the one page he made by hand and is satisfied with — an interpretation, to be corrected by him)
Calm and exact. Light, quiet grounds unless the client's own brand is dark; a great deal of empty space; one large, tight headline per scene; black or one deep ink with a single accent used a few times a page. No neon, no glow, no decorative gradients, no dashboard look, no invented charts or gauges, no glass cards, no emoji, no badges and pills scattered as decoration. If a choice looks like "AI-generated SaaS page", it is the wrong choice.

RULES THAT ARE NOT YOURS TO BEND
- Every fact, number, price, name and claim comes from the evidence. Invent nothing.
- Every link is one of the links given, or an anchor on this page. Screenshots are shown whole in their own colours; a picture marked generated is atmosphere only.
- Use the devices by their exact markup contract (class names as given). Do NOT write CSS or JavaScript for any dv- class or data-rise: the library's code is added for you. You write the page's own layout and type CSS, and no JavaScript at all.
- It must hold at 390, 768, 1100, 1440 and 1920 px: no sideways scroll, no clipped or overlapping text, no word broken, no heading stacked a word to a line. WCAG AA contrast. Everything visible without JavaScript."""

DIRECTION_TOOL = {'name': 'write_direction', 'description': 'The direction of this page, decided before any code.', 'input_schema': {'type': 'object', 'required': ['distinctive', 'idea', 'type', 'palette', 'scenes', 'quiet', 'index'], 'properties': {
    'distinctive': {'type': 'string'}, 'idea': {'type': 'string', 'description': 'the one drawable idea'},
    'type': {'type': 'object', 'required': ['display', 'text', 'display_px', 'text_px'], 'properties': {'display': {'type': 'string', 'description': 'a Google Fonts family (open licence) chosen for THIS client, and its weight'}, 'text': {'type': 'string'}, 'detail': {'type': 'string'},
             'display_px': {'type': 'integer', 'description': 'the largest size at a 1440 screen, inside the measured range'}, 'text_px': {'type': 'integer'}, 'why': {'type': 'string'}}},
    'palette': {'type': 'object', 'required': ['paper', 'ink', 'accent'], 'properties': {'paper': {'type': 'string'}, 'ink': {'type': 'string'}, 'accent': {'type': 'string'}, 'second_ground': {'type': 'string', 'description': 'optional: the one other ground, hex'}, 'why': {'type': 'string', 'description': 'start from the client\'s own colours'}}},
    'scenes': {'type': 'array', 'minItems': 3, 'maxItems': 5, 'items': {'type': 'object', 'required': ['id', 'shows', 'devices', 'material'], 'properties': {'id': {'type': 'string'}, 'shows': {'type': 'string', 'description': 'what the visitor sees happen'}, 'devices': {'type': 'array', 'items': {'type': 'string'}, 'description': 'device ids from the library'}, 'material': {'type': 'string', 'description': 'which of the client\'s pictures (by id) or figures it uses'}}}},
    'quiet': {'type': 'array', 'items': {'type': 'object', 'properties': {'id': {'type': 'string'}, 'what': {'type': 'string'}}}, 'description': 'the plain passages between scenes'},
    'index': {'type': 'string', 'description': 'where the secondary pages go and which ones'},
    'refused': {'type': 'string', 'description': 'what a stock generated page would have done here, and what this page does instead'}}}}

BUILD = """Write the page: ONE complete HTML document and nothing else — no commentary, no markdown fence.

- <html lang> … with the attribute data-eased-scroll on <html> only if your direction uses the eased-scroll device.
- One <style> with YOUR CSS only (layout, type, colour — set --ink, --paper and --accent on :root). No CSS for .dv-* or [data-rise]. No <script> at all. Put the exact comment <!--LIBRARY--> once inside <head> after your <style>, and <!--LIBRARY-JS--> once just before </body>: the library's stylesheet and script are placed there.
- Fonts: Google Fonts <link> tags only, the families of your direction, display=swap.
- Pictures: <img src="img:ID" alt="…" width height> with the ids and sizes given. No other image URL.
- One <h1>. <header>/<nav>, <main>, a <section id> for every scene and quiet passage, <footer>. A skip link. Visible focus. Actions at least 44 px tall on a phone.
- Use each device with its exact markup. Fluid type with clamp(); set the display size to your direction's display_px at 1440 and let it fall on a phone so that the longest word still fits the screen.
- Leave room: a scene needs height. Do not shrink the page to fit a laptop screen; these pages are long."""


def assemble(html, images):
    """The model's page with the library's code put where it asked, and the client's pictures in."""
    used = [i for i in LIB.DEVICES if re.search(r'\b' + re.escape({'rise-stagger': 'data-rise', 'eased-scroll': 'data-eased-scroll'}.get(i, 'dv-' + {'line-rise': 'lines', 'held-index': 'held', 'fact-ticker': 'tick', 'side-rail': 'rail', 'stack-cards': 'stack', 'grow-to-bleed': 'grow', 'magnet': 'magnet', 'scramble': 'scramble', 'figure-bars': 'bars', 'end-mark': 'endmark', 'peek': 'peek', 'depth': 'depth'}.get(i, i))) + r'\b', html)]
    css, js = LIB.bundle(used)
    out = html.replace('<!--LIBRARY-->', f'<style id="library">{css}</style>', 1) if '<!--LIBRARY-->' in html else html.replace('</head>', f'<style id="library">{css}</style></head>', 1)
    out = out.replace('<!--LIBRARY-JS-->', f'<script>{js}</script>', 1) if '<!--LIBRARY-JS-->' in out else out.replace('</body>', f'<script>{js}</script></body>', 1)
    return E.place_pictures(out, images), used


def house_rules(html):
    """What the page does against the studio's own rules: its own script, its own motion code for library classes, a device class the library does not have."""
    bad = []
    if re.search(r'<script\b', html, re.I): bad.append('the page carries its own <script>: motion comes from the library only')
    own = re.search(r'<style[^>]*>(.*?)</style>', html, re.S); css = own.group(1) if own else ''
    known = {'dv', 'dv-lines', 'dv-ln', 'dv-held', 'dv-held-side', 'dv-held-names', 'dv-held-items', 'dv-held-item', 'dv-held-m', 'dv-tick', 'dv-rail', 'dv-rail-row', 'dv-stack', 'dv-card', 'dv-grow', 'dv-magnet', 'dv-scramble', 'dv-bars', 'dv-endmark', 'dv-peek', 'dv-depth'}
    invented = sorted({c for c in re.findall(r'class="([^"]*)"', html) for c in c.split() if c.startswith('dv-') and c not in known})
    if invented: bad.append('device classes the library does not have: ' + ', '.join(invented[:8]))
    if re.search(r'\[data-rise\]\s*\{|@keyframes|\banimation\s*:', css): bad.append('the page writes its own motion (keyframes, animation or data-rise rules): use the devices')
    if len(re.findall(r'<h1\b', html)) != 1: bad.append('exactly one <h1>')
    return bad


def main():
    args = sys.argv[1:]; src, out = os.path.abspath(args[0]), os.path.abspath(args[1]); rounds = int(args[args.index('--rounds') + 1]) if '--rounds' in args else 1
    if '--model' in args: E.MODEL = args[args.index('--model') + 1]
    os.makedirs(out, exist_ok=True); started = time.time()
    ev, imgs = E.evidence(src); source_text = json.dumps(ev, ensure_ascii=False); allowed = {l['url'].rstrip('/') for l in ev['links']} | {str(ev.get('url') or '').rstrip('/')}
    library = 'THE LIBRARY — devices (use by id; markup is the contract):\n' + json.dumps(LIB.catalogue(), ensure_ascii=False, indent=1) + '\n\nTHE RULES — what sixteen measured Sites of the Month share as whole pages:\n' + json.dumps(LIB.RULES, ensure_ascii=False, indent=1)
    material = [{'type': 'text', 'text': library}, {'type': 'text', 'text': 'THE EVIDENCE (the client\'s existing site):\n' + json.dumps(ev, ensure_ascii=False, indent=1)}]
    for i in imgs[:12]:
        try: material += [{'type': 'text', 'text': f'PICTURE {i["id"]} ({i.get("w")}×{i.get("h")})' + (' — GENERATED atmosphere, not the product' if i.get('gen') else ' — screenshot of the real product' if i.get('shot') else '')}, {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': E.thumb(i['data'])}}]
        except Exception: pass
    kept = E.J(out, 'direction.json')
    direction = kept or E.call(HOUSE, material + [{'type': 'text', 'text': 'Decide the direction. Call write_direction.'}], 'direction', tool=DIRECTION_TOOL, max_tokens=12000)
    with open(os.path.join(out, 'direction.json'), 'w', encoding='utf-8') as f: json.dump(direction, f, indent=1, ensure_ascii=False)
    unknown = sorted({d for s in direction.get('scenes') or [] for d in s.get('devices') or [] if d not in LIB.DEVICES})
    brief = material + [{'type': 'text', 'text': 'YOUR DIRECTION (decided; build exactly this' + (f'; these are not in the library and may not be used: {unknown}' if unknown else '') + '):\n' + json.dumps(direction, ensure_ascii=False, indent=1) + '\n\n' + BUILD}]
    first = os.path.join(out, 'round-0.raw.html')
    html = open(first, encoding='utf-8').read() if kept and os.path.exists(first) else E.call(HOUSE, brief, 'build', max_tokens=48000)
    report = {'model': E.MODEL, 'rounds': [], 'devices_planned': sorted({d for s in direction.get('scenes') or [] for d in s.get('devices') or []})}; best = None
    for k in range(rounds + 1):
        html = html[html.find('<!'):] if '<!' in html else html; html = re.sub(r'```\s*$', '', html.strip())
        with open(os.path.join(out, f'round-{k}.raw.html'), 'w', encoding='utf-8') as f: f.write(html)
        house = house_rules(html); page, used = assemble(html, imgs)
        fence = [x for x in E.scan(re.sub(r'<script>.*?</script>', '', page, flags=re.S), allowed) if 'script' not in x]; numbers = E.invented_numbers(html, source_text)
        path = os.path.join(out, f'round-{k}.html')
        with open(path, 'w', encoding='utf-8') as f: f.write(page)
        seen = E.look(path, os.path.join(out, 'shots', f'round-{k}')) if not fence else {'errors': ['not opened: ' + '; '.join(fence)], 'shots': [], 'layout': None}
        reading = E.critique(seen['shots'], f'critic-{k}') if seen.get('shots') else None
        entry = {'k': k, 'devices_used': used, 'house': house, 'fence': fence, 'invented_numbers': numbers, 'runtime_errors': seen.get('errors'), 'layout': seen.get('layout'), 'overflow': {v: (seen.get(v) or {}).get('overflow') for v in ('desktop', 'phone')},
                 'height': {v: (seen.get(v) or {}).get('height') for v in ('desktop', 'phone')}, 'truncated': '</html>' not in html.lower(), 'critic': reading, 'score': E.total((reading or {}).get('scores'))}
        entry['technical_pass'] = not (house or fence or numbers or seen.get('errors') or seen.get('layout') or any(entry['overflow'].values()) or entry['truncated'])
        report['rounds'].append(entry)
        if not fence and (best is None or (entry['technical_pass'], entry['score']) > (best['technical_pass'], best['score'])): best = entry
        with open(os.path.join(out, 'report.json'), 'w', encoding='utf-8') as f: json.dump({**report, 'usage': E.USAGE, 'seconds': round(time.time() - started)}, f, indent=1, ensure_ascii=False)
        if k == rounds: break
        problems = []
        if house: problems.append('AGAINST THE STUDIO\'S RULES: ' + '; '.join(house))
        if fence: problems.append('NOT OPENED: ' + '; '.join(fence))
        if entry['truncated']: problems.append('The document was cut off before </html>: write tighter CSS and finish it.')
        if numbers: problems.append('NUMBERS THE EVIDENCE NEVER SAYS: ' + ', '.join(numbers))
        if seen.get('errors'): problems.append('RUNTIME ERRORS: ' + ' | '.join(seen['errors'][:6]))
        if seen.get('layout'): problems.append('MEASURED LAYOUT BREAKS: ' + json.dumps([{x: b[x] for x in ('kind', 'section', 'text', 'detail', 'widths')} for b in seen['layout'][:14]], ensure_ascii=False))
        if any(entry['overflow'].values()): problems.append('Scrolls sideways at: ' + ', '.join(v for v, o in entry['overflow'].items() if o))
        if reading: problems.append('AN ART DIRECTOR READ THE RENDERED PAGE:\n' + json.dumps({x: reading.get(x) for x in ('scores', 'verdict', 'template_likeness', 'defects')}, ensure_ascii=False, indent=1))
        html = E.call(HOUSE, material + [{'type': 'text', 'text': 'YOUR DIRECTION:\n' + json.dumps(direction, ensure_ascii=False) + '\n\nTHE PAGE YOU WROTE:\n' + html + '\n\nWHAT WAS FOUND WHEN IT WAS RENDERED:\n' + '\n\n'.join(problems) + '\n\nRevise. A "concept" defect is answered by changing the scene, not its CSS. Keep what is strong.\n\n' + BUILD}], f'revise-{k + 1}', max_tokens=48000)
    if best:
        import shutil; shutil.copyfile(os.path.join(out, f'round-{best["k"]}.html'), os.path.join(out, 'page.html')); report['best'] = best['k']
    priced = [u['usd'] for u in E.USAGE if u['usd'] is not None]
    report.update(usage=E.USAGE, seconds=round(time.time() - started), usd=round(sum(priced), 3))
    with open(os.path.join(out, 'report.json'), 'w', encoding='utf-8') as f: json.dump(report, f, indent=1, ensure_ascii=False)
    print(json.dumps({'best': report.get('best'), 'rounds': [(r['k'], r['score'], r['technical_pass'], r['devices_used']) for r in report['rounds']], 'usd': report['usd'], 'seconds': report['seconds']}))


if __name__ == '__main__': main()
