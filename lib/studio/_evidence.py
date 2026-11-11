"""freedom.py — an experiment, not a product path: can a page be better when no recipe or section form decides it?

  python3 experiments/freedom/freedom.py <evidence dir> <out dir> [--model claude-opus-5-5] [--rounds 2]

Version B of a controlled comparison. It reads the SAME source evidence the production loop reads (inventory.json,
factsheet.json, images.json — what capture and the reader already wrote) and nothing of the production renderer:
no blueprint, no section form, no composer. A model first writes a creative direction, then writes the page as one
self-contained HTML document, then looks at it in a browser and revises it.

What "isolated" means here, and why there is no React build:
  * the output is static HTML + CSS + inline vanilla JS. Nothing the model writes is ever executed by Node or Python —
    there is no build step, no dependency install, no generated code on our side of the fence;
  * the page is opened only in headless Chrome, whose network is cut to the page's own file and Google's font hosts;
  * before it is opened it is scanned: no external scripts, no fetch/XHR/WebSocket/eval/import(), no iframes, no forms
    that post anywhere, and every link must be one the client's own site offered (or an anchor on the page);
  * nothing is deployed. The preview is a file.
Facts are held, not trusted: every number on the page must occur in the source evidence, or the page is sent back.

Writes into <out dir>: direction.json, page.html (the best round), round-<n>.html, shots/, report.json (calls, tokens,
cost at list price, seconds, checks, the critic's reading of every round). No production file is touched."""
import base64, io, json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'lib'))
import seo as SEO, budget as BUDGET

MODEL = 'claude-opus-5-5'
USAGE = []


def J(d, name):
    try:
        with open(os.path.join(d, name), encoding='utf-8') as f: return json.load(f)
    except Exception: return None


def call(system, content, who, tool=None, max_tokens=8000, model=None):
    """One model call, streamed; its usage is kept for the report. With a tool, returns the tool's input; else the text."""
    import anthropic
    client = anthropic.Anthropic(); model = model or MODEL; t0 = time.time()
    kwargs = dict(model=model, max_tokens=max_tokens, system=system, messages=[{'role': 'user', 'content': content}], thinking={'type': 'adaptive'})
    if tool: kwargs.update(tools=[tool], tool_choice={'type': 'auto'})
    def ask(kw, attempt):
        with client.messages.stream(**kw) as stream: msg = stream.get_final_message()
        u = msg.usage; tin = (u.input_tokens or 0) + (getattr(u, 'cache_creation_input_tokens', 0) or 0); tout = u.output_tokens or 0
        try: BUDGET.charge(u, 'studio_' + re.sub(r'[^a-z]+', '_', who.lower()).strip('_'), model)   # a job's ledger counts these calls like any other
        except Exception: pass
        USAGE.append({'who': who + attempt, 'model': model, 'in': tin, 'out': tout, 'seconds': round(time.time() - t0, 1), 'usd': BUDGET.cost(model, tin, tout, getattr(u, 'cache_read_input_tokens', 0) or 0), 'stop': msg.stop_reason})
        return msg
    msg = ask(kwargs, '')
    if tool:
        used = lambda m: next((b.input for b in m.content if b.type == 'tool_use'), None)
        got = used(msg)
        if got is None and msg.stop_reason != 'refusal':
            # The tool is offered, not forced (a forced tool cannot be thought about first), so an answer can come back as prose
            # or run out of room while thinking. Once more: with more room if it ran out, with the tool named if it wrote prose.
            again = dict(kwargs)
            if msg.stop_reason == 'max_tokens': again['max_tokens'] = int(max_tokens * 1.6)
            else: again['messages'] = kwargs['messages'] + [{'role': 'assistant', 'content': msg.content}, {'role': 'user', 'content': f'Answer by calling the tool `{tool["name"]}` — nothing else is read.'}]
            first = msg.stop_reason; msg = ask(again, ' (again)'); got = used(msg)
            if got is None: raise RuntimeError(f'{who}: the model did not answer with the tool (stopped on {first}, then {msg.stop_reason})')
        if got is None: raise RuntimeError(f'{who}: the model did not answer with the tool (stopped on {msg.stop_reason})')
        return got
    return ''.join(b.text for b in msg.content if b.type == 'text')


def thumb(data_uri, side=900):
    from PIL import Image
    raw = base64.b64decode(data_uri.split(',', 1)[1]); im = Image.open(io.BytesIO(raw)).convert('RGB'); im.thumbnail((side, side)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=72)
    return base64.b64encode(buf.getvalue()).decode()


def sharp_width(data_uri, floor=200):
    """The widest a picture may be drawn before it reads as blurred, in px; None when the picture cannot be read. Measured,
    not judged: the variance of an edge filter, taken at the picture's own size (no more than 1400 px) and then at smaller
    and smaller sizes until the edges are crisp. A picture that is blurred at its own size and crisp at half of it has
    detail for half its width. Calibrated 2026-11-11 on the captures of one site at their own size: two frames of films read
    42 and 79, a soft photograph 72 (it read 257 once reduced to 640 px, which is how it passed the earlier rule and was
    drawn half a screen wide), a plate photographed with a shallow focus 481, ten photographs of rooms 2076-5849."""
    try:
        import base64, io
        from PIL import Image, ImageFilter, ImageStat
        im = Image.open(io.BytesIO(base64.b64decode(data_uri.split(',', 1)[1]))).convert('L'); w, h = im.size
        if max(w, h) > 1400: k = 1400 / max(w, h); im = im.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
        for scale in (1, .8, .64, .5, .4, .32, .25):
            at = im if scale == 1 else im.resize((max(8, int(im.size[0] * scale)), max(8, int(im.size[1] * scale))), Image.LANCZOS)
            edges = at.filter(ImageFilter.FIND_EDGES); edges = edges.crop((3, 3, edges.size[0] - 3, edges.size[1] - 3))   # the filter draws its own edge along the border
            if ImageStat.Stat(edges).var[0] >= floor: return int(w * scale)
        return int(w * .2)
    except Exception: return None


def soft(data_uri, floor=200):
    """Whether a picture is blurred at its own size (see sharp_width). A picture that cannot be read is not called soft."""
    try:
        import base64, io
        from PIL import Image
        got = sharp_width(data_uri, floor)
        return got is not None and got < Image.open(io.BytesIO(base64.b64decode(data_uri.split(',', 1)[1]))).size[0]
    except Exception: return False


def _look(data_uri):
    """A 9x8 difference hash of a picture: two crops or two sizes of one photograph differ in a few of its 64 bits."""
    import base64, io
    from PIL import Image
    im = Image.open(io.BytesIO(base64.b64decode(data_uri.split(',', 1)[1]))).convert('L').resize((9, 8), Image.LANCZOS); px = list(im.tobytes())
    return [px[r * 9 + c] > px[r * 9 + c + 1] for r in range(8) for c in range(8)]


def distinct(images, near=9):
    """The pictures without the ones that are not photographs (a notice, a diagram: `plain` from the capture) and without
    a second file of a photograph already held — the larger of two that look alike stays, in the place of the first."""
    kept = []
    for i in images:
        if i.get('plain') and not i.get('shot') and not i.get('gen'): continue
        try: i['_look'] = _look(i['data'])
        except Exception: kept.append(i); continue
        twin = next((k for k in kept if k.get('_look') and sum(a != b for a, b in zip(k['_look'], i['_look'])) <= near and not (k.get('shot') or i.get('shot'))), None)
        if twin is None: kept.append(i)
        elif (i.get('w') or 0) * (i.get('h') or 0) > (twin.get('w') or 0) * (twin.get('h') or 0) and not i.get('video'): kept[kept.index(twin)] = i
    for i in kept: i.pop('_look', None)
    return kept


def evidence(d):
    """The source evidence as the model gets it: what the business is, every source section's words, the links the
    client's site offered, the brand's own colours and type, and the pictures by id."""
    inv = J(d, 'inventory.json') or {}; fact = J(d, 'factsheet.json') or {}; images = distinct([i for i in (J(d, 'images.json') or []) if i.get('data')])
    sections = [{'title': s.get('title'), 'text': ' '.join(str(s.get('text') or '').split())[:3000], 'faq': [{'q': q.get('question'), 'a': q.get('answer')} for q in (s.get('faq') or []) if isinstance(q, dict)][:14]}
                for s in SEO.source_sections(inv)]
    links, seen = [], set()
    for a in inv.get('actions') or []:
        href, text = str(a.get('href') or ''), ' '.join(str(a.get('text') or '').split())
        if not href.startswith('http') or not text or len(text) > 120 or (href, text.casefold()) in seen or re.match(r'skip to\b|saltar al?\b|ir al contenido|preskoči', text, re.I): continue   # a skip link is a control of the old page, never an action to offer
        seen.add((href, text.casefold())); links.append({'label': text, 'url': href})
    for i in images:
        if 'sharp_w' not in i:
            got = sharp_width(i['data']); i['sharp_w'] = got if got is not None else int(i.get('w') or 0)
            if 'soft' not in i: i['soft'] = bool(i.get('video')) or (got is not None and got < int(i.get('w') or 0))   # a frame of a film is never the picture to show large
    # The composer is shown fourteen pictures: the client's own photographs first, the ones with most detail before the
    # rest, soft ones and frames of films after them, screenshots of the old site last. What it is not shown it is not offered.
    images = sorted(images, key=lambda i: (bool(i.get('shot')), bool(i.get('soft')), -int(i.get('sharp_w') or 0)))[:14]
    pictures = [{'id': i['id'], 'w': i.get('w'), 'h': i.get('h'), 'kind': 'generated atmosphere (not the product, never evidence)' if i.get('gen') else 'screenshot of the real product' if i.get('shot') else 'the client\'s own picture',
                 'note': ' '.join(str(i.get('alt') or '').split())[:140], **({'page': str(i['page'])[:60]} if i.get('page') else {}), **({'soft': f"out of focus or a frame of a video — crisp only up to about {i.get('sharp_w')} px wide: show it small, never across the screen"} if i.get('soft') else {})} for i in images]
    found = J(d, 'logos.json') or {}; marks = [m for m in (found.get('items') or []) if isinstance(m, dict) and str(m.get('data') or '').startswith('data:image/')][:12]
    logos = [{'id': f'logo{k + 1}', 'logo': True, 'data': m['data'], 'w': m.get('w'), 'h': m.get('h'), 'alt': m.get('alt') or ''} for k, m in enumerate(marks)] if len(marks) >= 4 else []
    images = images + logos   # placed by the scene "logos", never offered as pictures
    return {'url': inv.get('url'), 'title': inv.get('title'), 'lang': inv.get('lang'), 'logos': {'count': len(logos), 'said_with_them': str(found.get('label') or '')[:90]} if logos else None, 'h1': (inv.get('copy') or {}).get('h1') or None, 'factsheet': fact, 'sections': sections, 'links': links[:120],
            'brand': {'colours': inv.get('colors'), 'type': inv.get('typography'), 'name': (inv.get('brand') or {}).get('name'), 'character': character(inv)}, 'pictures': pictures}, images


SERIF = re.compile(r'serif|garamond|playfair|didot|bodoni|cormorant|fraunces|canela|times|georgia|caslon|baskerville|tiempos|domaine|reckless|editorial', re.I)


def character(inv):
    """What the client's own page shows of its character, read off its measured type and colours — never off the name of
    its trade. Returns the readings and what they suggest; the composer states the character itself and says why. A sports
    product set in heavy condensed capitals on black and a ledger set in a light grotesque on white are both software."""
    typ = (inv or {}).get('typography') or {}; h1 = typ.get('h1') or {}; col = (inv or {}).get('colors') or {}
    def hexes(key): return [str(c.get('c')) for c in col.get(key) or [] if isinstance(c, dict) and re.fullmatch(r'#[0-9a-fA-F]{6}', str(c.get('c') or ''))]
    def lum(h): r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)); return .2126 * r + .7152 * g + .0722 * b
    def sat(h): r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)); return (max(r, g, b) - min(r, g, b)) / max(r, g, b) if max(r, g, b) else 0
    font = str(h1.get('font') or '').strip('_ ').replace('_', ' ')
    try: weight = int(float(h1.get('weight') or 400))
    except (TypeError, ValueError): weight = 400
    grounds = hexes('bg'); accents = [h for h in hexes('buttons') + hexes('text') if sat(h) >= .35 and .08 < lum(h) < .95]
    dark = bool(grounds) and lum(grounds[0]) < .2; loud = str(h1.get('tt') or '').lower() == 'uppercase' or weight >= 800 or 'condensed' in font.lower() or 'impact' in font.lower()   # a bold 700 sans is ordinary; capitals, a condensed face or a black weight are a voice
    serif = bool(SERIF.search(font)); vivid = bool(accents) and sat(accents[0]) >= .6
    suggests = None if not h1 else 'energetic' if loud and (dark or vivid) else 'refined' if serif else 'calm' if weight <= 500 and not loud else None   # nothing measured, nothing suggested
    return {'headline_as_the_client_sets_it': {'face': font[:60] or None, 'weight': weight, 'case': h1.get('tt') or 'none', 'px': h1.get('size')} if h1 else None,
            'ground': {'colour': grounds[0], 'dark': dark} if grounds else None, 'accent': {'colour': accents[0], 'vivid': vivid} if accents else None,
            'suggests': suggests, 'note': 'measured on the client\'s page; "suggests" is a reading of these three, not a rule — its photographs and its words count too'}


DIRECTION_TOOL = {'name': 'write_direction', 'description': 'The creative direction of this one page, decided before any code.', 'input_schema': {'type': 'object', 'required': ['distinctive', 'idea', 'feeling', 'metaphor', 'type', 'palette', 'composition', 'product', 'narrative', 'interactions', 'content', 'not_this'], 'properties': {
    'distinctive': {'type': 'string', 'description': 'what is true of this business and of no competitor — from the evidence'},
    'idea': {'type': 'string', 'description': 'the one creative idea the whole page is an expression of; drawable, not a mood'},
    'feeling': {'type': 'string'}, 'metaphor': {'type': 'string', 'description': 'the visual metaphor and where on the page it is literally seen'},
    'type': {'type': 'object', 'properties': {'display': {'type': 'string'}, 'text': {'type': 'string'}, 'detail': {'type': 'string'}, 'why': {'type': 'string'}}, 'description': 'families from Google Fonts only (open licences); display, running text, small detail'},
    'palette': {'type': 'object', 'description': 'named roles → hex, and why; start from the brand\'s own colours'},
    'composition': {'type': 'string', 'description': 'the geometry of the page: grid, asymmetry, what bleeds, how sections differ in scale and pace'},
    'product': {'type': 'string', 'description': 'how the real product is demonstrated with the real screenshots and real numbers given — which picture, where, how large, annotated how'},
    'narrative': {'type': 'array', 'items': {'type': 'object', 'required': ['id', 'purpose', 'form'], 'properties': {'id': {'type': 'string'}, 'purpose': {'type': 'string', 'description': 'the visitor\'s question this answers'}, 'form': {'type': 'string', 'description': 'what it looks like — specific enough to build'}, 'source': {'type': 'string', 'description': 'which source sections it draws on'}}}},
    'interactions': {'type': 'array', 'items': {'type': 'string'}, 'description': 'only those that help a visitor understand or decide'},
    'content': {'type': 'object', 'properties': {'homepage': {'type': 'array', 'items': {'type': 'string'}}, 'secondary': {'type': 'array', 'items': {'type': 'object', 'properties': {'what': {'type': 'string'}, 'where': {'type': 'string', 'description': 'navigation | footer | a designed directory | a link to the client\'s existing page'}}}}}, 'description': 'what belongs on this page and where everything else goes — nothing important is dropped, nothing is dumped'},
    'not_this': {'type': 'string', 'description': 'the stock sequence this page refuses (big type hero → feature grid → stats → FAQ accordion → big type closing) and what it does instead at each of those points'}}}}

STUDIO = """You are the creative director and lead front-end designer of a small studio that wins awards for web design. A client's existing website is in front of you as evidence: its words, its facts, its links, its colours and type, its pictures. You are redesigning its homepage from nothing. No template, no component library, no section pattern is given to you and none is wanted.

What makes a page read as studio work rather than as a generated page: ONE idea that every section is an expression of; typography with a real hierarchy and a face chosen for this client; composition that changes scale and pace on purpose; the product shown, not described; restraint — most of the page is quiet so that two or three moments can be loud; and nothing on it that is there only because the source had it.

The rules that are not yours to bend:
- Every fact, number, name, price and claim on the page comes from the evidence. You invent nothing: no testimonials, no customers, no statistics, no features. If the evidence does not say it, the page does not say it.
- Screenshots are evidence of the real product: shown whole or as an honest crop, in their own colours, never redrawn, never faked. A picture marked "generated atmosphere" may only be background mood, never presented as the product.
- Every link on the page is one of the links given, or an anchor to a section of this page.
- Curate. The homepage carries what a visitor needs to understand and decide. Secondary material gets a deliberate place — navigation, footer, a designed directory, a link to the client's own page. Never a run of raw links, never an appended dump.
- It must work at 390, 768, 1100, 1440 and 1920 px wide, with no horizontal scroll, no clipped or overlapping text, no word broken across lines, no heading stacked one word to a line. Text meets WCAG AA contrast. Honour prefers-reduced-motion."""

BUILD = """Write the page: ONE complete HTML document, nothing else — no commentary, no markdown fence.

Technical contract:
- Self-contained: all CSS in one <style>, any JavaScript inline in one <script> at the end, vanilla only. No frameworks, no external scripts, no fetch/XHR/WebSocket, no eval, no dynamic import, no iframes, no forms that submit anywhere.
- Fonts: Google Fonts <link> tags only, with font-display swap, the families of your direction.
- Pictures: use <img src="img:ID" alt="…"> with the ids given (or url(img:ID) in CSS); they are replaced by the real files. Give every img explicit width and height attributes from the sizes given so nothing shifts. Do not reference any other image URL.
- Semantic HTML: one <h1>, <header>/<nav>, <main>, <section id> for every part of your narrative, <footer>. A skip link. Visible focus. Buttons and links at least 44 px tall on a phone.
- Motion: CSS and IntersectionObserver only; nothing hides content when JavaScript is off; everything is still and visible under prefers-reduced-motion.
- Fluid type with clamp(); a real grid; test your own layout mentally at 390 and at 1920 before you write each section — long words, long headings, the widest picture.
- <title> and <meta name="description"> from the source's own.
Write real, finished CSS. This is the deliverable, not a sketch."""

CRITIC_TOOL = {'name': 'read_page', 'description': 'What a demanding art director sees in these screenshots.', 'input_schema': {'type': 'object', 'required': ['scores', 'verdict', 'defects'], 'properties': {
    'scores': {'type': 'object', 'description': '0–100 each: 50 = a competent generated page, 70 = professional studio work, 85+ = award level', 'required': ['typography', 'composition', 'originality', 'brand_coherence', 'product_storytelling', 'rhythm', 'imagery', 'responsive', 'content_organisation'],
               'properties': {k: {'type': 'integer', 'minimum': 0, 'maximum': 100} for k in ('typography', 'composition', 'originality', 'brand_coherence', 'product_storytelling', 'rhythm', 'imagery', 'responsive', 'content_organisation')}},
    'verdict': {'type': 'string', 'description': 'four sentences at most: what this page is, where it is strong, where it fails, whether it reads as one idea'},
    'template_likeness': {'type': 'string', 'description': 'does it follow the stock sequence (big type hero, feature grid, stats, FAQ accordion, big type closing)? say exactly where'},
    'defects': {'type': 'array', 'items': {'type': 'object', 'required': ['kind', 'where', 'what', 'fix'], 'properties': {'kind': {'type': 'string', 'enum': ['concept', 'implementation', 'technical']}, 'where': {'type': 'string'}, 'what': {'type': 'string'}, 'fix': {'type': 'string'}}}}}}}

CRITIC = """You are a demanding art director reviewing a homepage from screenshots (desktop in slices from top to bottom, then phone). You do not know how it was made and it does not matter. Judge what is in front of you against professional studio work, not against other generated pages. Be specific and unsentimental: name the section, say what is wrong, say what would fix it. Classify every defect: "concept" (the idea or the structure is weak — no amount of CSS fixes it), "implementation" (a good intention badly executed), "technical" (broken: clipped, overlapping, unreadable, misaligned, empty)."""


def scan(html, allowed):
    """Why this document may not be opened, or [] — the fence around generated code."""
    bad = []
    low = html.lower()
    if re.search(r'<script[^>]+\bsrc\s*=', low): bad.append('an external script')
    for word in ('fetch(', 'xmlhttprequest', 'websocket(', 'eval(', 'import(', 'new function(', 'navigator.sendbeacon', 'document.cookie', 'localstorage', 'sessionstorage', '<iframe', '<object', '<embed'):
        if word in low: bad.append(f'"{word}" in the page')
    if re.search(r'<form\b[^>]*\baction\s*=\s*["\']?https?:', low): bad.append('a form that posts to another host')
    for href in set(re.findall(r'<a\b[^>]*\bhref\s*=\s*["\']([^"\']+)', html)):
        if href.startswith(('#', 'mailto:', 'tel:')): continue
        if href.rstrip('/') not in allowed: bad.append(f'a link the client\'s site did not offer: {href[:80]}')
    for src in set(re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', html)):
        if not re.match(r'https://fonts\.(googleapis|gstatic)\.com(/|$)', src) and src.rstrip('/') not in allowed: bad.append(f'a foreign resource: {src[:80]}')
    return bad[:12]


def invented_numbers(html, source_text):
    """Numbers on the page that the evidence never says — a page may not make up a statistic, a price or a count."""
    text = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S); text = re.sub(r'<[^>]+>', ' ', text)
    norm = lambda s: re.sub(r'[,\s]', '', s)
    known = set(norm(n) for n in re.findall(r'\d[\d.,]*\d|\d', source_text))
    out = []
    for n in re.findall(r'\d[\d.,]*\d', text):
        v = norm(n).rstrip('.')
        if len(re.sub(r'\D', '', v)) < 2 or v in known or v.rstrip('0').rstrip('.') in known: continue
        if re.fullmatch(r'(19|20)\d\d', v) or re.fullmatch(r'0?[1-9]|1\d|2\d', v): continue   # a year, a small ordinal used as a label
        if v not in out: out.append(v)
    return out[:20]


def place_pictures(html, images):
    by = {i['id']: i['data'] for i in images}
    return re.sub(r'img:([A-Za-z0-9_-]+)', lambda m: by.get(m.group(1), 'data:image/gif;base64,R0lGODlhAQABAAAAACw='), html)


SHOT = r"""
import { chromium } from 'playwright'; import fs from 'node:fs';
const [,, file, dir] = process.argv; fs.mkdirSync(dir, { recursive: true });
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox', '--disable-gpu'] }); const out = { errors: [], shots: [], blocked: 0 };
for (const [name, w, h, cap] of [['desktop', 1440, 900, 5], ['phone', 390, 844, 4]]) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1, reducedMotion: 'reduce' }); const p = await ctx.newPage();
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:') || u.startsWith('data:') || /^https:\/\/fonts\.(googleapis|gstatic)\.com\//.test(u)) return r.continue(); out.blocked++; return r.abort(); });
  p.on('pageerror', e => out.errors.push(name + ': ' + String(e).slice(0, 160))); p.on('console', m => { if (m.type() === 'error') out.errors.push(name + ' console: ' + m.text().slice(0, 160)); });
  await p.goto('file://' + file, { waitUntil: 'load' }); await p.evaluate(() => document.fonts && document.fonts.ready).catch(() => {}); await p.waitForTimeout(900);
  // a page is photographed as a visitor who scrolled through it would have it: pictures loaded, things that arrive on scroll arrived
  await p.evaluate(() => document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager'));
  for (let y = 0, h = await p.evaluate(() => document.documentElement.scrollHeight); y < h; y += 700) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(70); }
  await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(500);
  const H = await p.evaluate(() => document.documentElement.scrollHeight); out[name] = { height: H, overflow: await p.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1) };
  const step = name === 'desktop' ? 1800 : 1900; let n = 0;
  for (let y = 0; y < H && n < cap * 2; y += step, n++) { const f = `${dir}/${name}-${String(n).padStart(2, '0')}.jpg`; await p.screenshot({ path: f, clip: { x: 0, y, width: w, height: Math.min(step, H - y) }, fullPage: true, type: 'jpeg', quality: 70 }); out.shots.push(f); }
  await ctx.close(); }
await b.close(); console.log(JSON.stringify(out));
"""


def look(page_path, shots_dir):
    """Open the page in the fenced browser: screenshots for the critic, runtime errors, and the measured layout."""
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_shot.mjs')
    with open(script, 'w') as f: f.write(SHOT)
    r = subprocess.run(['node', script, page_path, shots_dir], capture_output=True, text=True, timeout=240, cwd=ROOT)
    seen = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 and r.stdout.strip() else {'errors': ['the page could not be opened: ' + r.stderr[-300:]], 'shots': []}
    try:
        lay = subprocess.run(['node', os.path.join(ROOT, 'lib', 'qa', 'layout.mjs'), page_path], capture_output=True, text=True, timeout=240, cwd=ROOT)
        seen['layout'] = json.loads(lay.stdout.strip().splitlines()[-1])['breaks']
    except Exception as e: seen['layout'] = None; seen['errors'].append('layout not measured: ' + str(e)[:100])
    return seen


def critique(shots, who):
    content = [{'type': 'text', 'text': 'The screenshots, desktop first (top to bottom), then phone.'}]
    for f in shots[:14]:
        with open(f, 'rb') as fh: data = base64.b64encode(fh.read()).decode()
        content += [{'type': 'text', 'text': os.path.basename(f)}, {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': data}}]
    return call(CRITIC, content, who, tool=CRITIC_TOOL, max_tokens=5000)


def total(scores): return round(sum(scores.values()) / max(1, len(scores)), 1) if isinstance(scores, dict) and scores else 0


def main():
    global MODEL
    args = sys.argv[1:]; src, out = os.path.abspath(args[0]), os.path.abspath(args[1]); rounds = int(args[args.index('--rounds') + 1]) if '--rounds' in args else 2
    if '--model' in args: MODEL = args[args.index('--model') + 1]
    os.makedirs(out, exist_ok=True); started = time.time()
    ev, images = evidence(src)
    source_text = json.dumps(ev, ensure_ascii=False)
    allowed = {l['url'].rstrip('/') for l in ev['links']} | {str(ev.get('url') or '').rstrip('/')}
    material = [{'type': 'text', 'text': 'THE EVIDENCE (the client\'s existing site):\n' + json.dumps(ev, ensure_ascii=False, indent=1)}]
    for i in images[:12]:
        try: material += [{'type': 'text', 'text': f'PICTURE {i["id"]} ({i.get("w")}×{i.get("h")})'}, {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': thumb(i['data'])}}]
        except Exception: pass
    kept = J(out, 'direction.json'); first = os.path.join(out, 'round-0.raw.html')   # a run that was stopped is taken up where it stood: what was paid for is not paid for twice
    prior = (J(out, 'report.json') or {}).get('usage') or []
    if kept and os.path.exists(first): USAGE.extend(u for u in prior if u.get('who') in ('direction', 'build'))
    direction = kept or call(STUDIO, material + [{'type': 'text', 'text': 'Decide the creative direction of the new homepage. Call write_direction.'}], 'direction', tool=DIRECTION_TOOL, max_tokens=14000)
    with open(os.path.join(out, 'direction.json'), 'w', encoding='utf-8') as f: json.dump(direction, f, indent=1, ensure_ascii=False)
    brief = material + [{'type': 'text', 'text': 'YOUR DIRECTION (decided, now build exactly this):\n' + json.dumps(direction, ensure_ascii=False, indent=1) + '\n\n' + BUILD}]
    html = open(first, encoding='utf-8').read() if kept and os.path.exists(first) else call(STUDIO, brief, 'build', max_tokens=48000)
    report = {'model': MODEL, 'source': src, 'rounds': []}; best = None
    for k in range(rounds + 1):
        html = html[html.find('<!'):] if '<!' in html else html; html = re.sub(r'```\s*$', '', html.strip())
        raw = os.path.join(out, f'round-{k}.raw.html'); page = os.path.join(out, f'round-{k}.html')
        with open(raw, 'w', encoding='utf-8') as f: f.write(html)
        fence = scan(html, allowed); numbers = invented_numbers(html, source_text)
        entry = {'k': k, 'fence': fence, 'invented_numbers': numbers, 'bytes': len(html), 'truncated': '</html>' not in html.lower()}
        if fence: entry['opened'] = False; seen = {'errors': ['not opened: ' + '; '.join(fence)], 'shots': [], 'layout': None}
        else:
            with open(page, 'w', encoding='utf-8') as f: f.write(place_pictures(html, images))
            seen = look(page, os.path.join(out, 'shots', f'round-{k}')); entry['opened'] = True
        entry.update(runtime_errors=seen.get('errors'), blocked_requests=seen.get('blocked'), layout=seen.get('layout'), overflow={v: (seen.get(v) or {}).get('overflow') for v in ('desktop', 'phone')},
                     text_kept=round(SEO.text_coverage(' '.join(s['text'] for s in ev['sections']), re.sub(r'<[^>]+>', ' ', html)), 3),
                     links_used=len(set(re.findall(r'href\s*=\s*["\'](https?://[^"\']+)', html))), links_offered=len(allowed))
        reading = critique(seen['shots'], f'critic-{k}') if seen.get('shots') else None
        entry['critic'] = reading; entry['score'] = total((reading or {}).get('scores'))
        technical = not fence and not numbers and not (seen.get('errors') or []) and not (seen.get('layout') or []) and not any(entry['overflow'].values()) and not entry['truncated']
        entry['technical_pass'] = technical
        report['rounds'].append(entry)
        if entry['opened'] and (best is None or (technical, entry['score']) > (best['technical_pass'], best['score'])): best = entry
        with open(os.path.join(out, 'report.json'), 'w', encoding='utf-8') as f: json.dump({**report, 'usage': USAGE, 'seconds': round(time.time() - started)}, f, indent=1, ensure_ascii=False)
        if k == rounds or (technical and entry['score'] >= 80 and not [d for d in (reading or {}).get('defects', []) if d['kind'] != 'implementation']): break
        problems = []
        if fence: problems.append('THE PAGE WAS NOT OPENED — it breaks the technical contract: ' + '; '.join(fence))
        if entry['truncated']: problems.append('Your document was cut off before </html>: it is too long. Write tighter CSS and finish the document.')
        if numbers: problems.append('NUMBERS ON THE PAGE THAT THE EVIDENCE NEVER SAYS (remove or replace with what the evidence says): ' + ', '.join(numbers))
        if seen.get('errors'): problems.append('RUNTIME ERRORS: ' + ' | '.join(seen['errors'][:6]))
        if seen.get('layout'): problems.append('MEASURED LAYOUT BREAKS (browser line boxes, at the widths named): ' + json.dumps([{x: b[x] for x in ('kind', 'section', 'text', 'detail', 'widths')} for b in seen['layout'][:14]], ensure_ascii=False))
        if any(entry['overflow'].values()): problems.append('The page scrolls sideways at: ' + ', '.join(v for v, o in entry['overflow'].items() if o))
        if reading: problems.append('AN ART DIRECTOR READ THE RENDERED PAGE:\n' + json.dumps({k2: reading.get(k2) for k2 in ('scores', 'verdict', 'template_likeness', 'defects')}, ensure_ascii=False, indent=1))
        revise = material + [{'type': 'text', 'text': 'YOUR DIRECTION:\n' + json.dumps(direction, ensure_ascii=False) + '\n\nTHE PAGE YOU WROTE:\n' + html + '\n\nWHAT WAS FOUND WHEN IT WAS RENDERED IN A BROWSER:\n' + '\n\n'.join(problems) +
                              '\n\nRevise. A "concept" defect is answered by changing the structure of that part, not its CSS. Fix every technical item. Keep what is strong.\n\n' + BUILD}]
        html = call(STUDIO, revise, f'revise-{k + 1}', max_tokens=48000)
    if best:
        import shutil
        shutil.copyfile(os.path.join(out, f'round-{best["k"]}.html'), os.path.join(out, 'page.html')); report['best'] = best['k']
    priced = [u['usd'] for u in USAGE if u['usd'] is not None]
    report.update(usage=USAGE, seconds=round(time.time() - started), calls=len(USAGE), tokens_in=sum(u['in'] for u in USAGE), tokens_out=sum(u['out'] for u in USAGE), usd=round(sum(priced), 3) if len(priced) == len(USAGE) else None)
    with open(os.path.join(out, 'report.json'), 'w', encoding='utf-8') as f: json.dump(report, f, indent=1, ensure_ascii=False)
    print(json.dumps({'best': report.get('best'), 'rounds': [(r['k'], r['score'], r['technical_pass']) for r in report['rounds']], 'seconds': report['seconds'], 'usd': report['usd'], 'calls': report['calls']}))


if __name__ == '__main__': main()
