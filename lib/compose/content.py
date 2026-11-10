"""content.py — what a composition may place: the hero's own words, actions and pictures, each under an address.

A composition never contains a sentence. It names an address (`hero.h1`, `hero.cta`, `hero.picture`, `img:<id>`) and
the renderer fetches what is there. The addresses are read off the page the production renderer already built, so a
composed hero shows exactly the words and links the production hero shows: the same headline, the same lede, the same
buttons going to the same captured destinations. A composition can place them differently; it cannot change them,
add to them, or leave them out (lib/compose/validate.py checks that).

  from_page(page_html, images)  → {'text', 'actions', 'media', 'page', 'span'}
  words(headline segments)      → the headline word by word, for line breaks and marked words
Deterministic, no network, no model."""
import base64, io, re
from html.parser import HTMLParser

SAFE_URL = re.compile(r'^(https?://|mailto:|tel:|#)', re.I)


def hero_span(html):
    """(start, end) of the hero <section> in a rendered page, nested sections counted."""
    m = re.search(r'<section class="sec hero[^"]*"[^>]*>', html)
    if not m: raise ValueError('the page has no hero section')
    depth, i = 1, m.end()
    for tag in re.finditer(r'<section\b|</section>', html[m.end():]):
        depth += 1 if tag.group(0) != '</section>' else -1
        if depth == 0: return m.start(), m.end() + tag.end()
    raise ValueError('the hero section is not closed')


class _Hero(HTMLParser):
    """Reads the production hero: labels, the headline with its emphasised words, the lede, the buttons, the picture."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.labels = []; self.h1 = []; self.lede = ''; self.buttons = []; self.picture = None
        self.in_label = self.in_h1 = self.in_lede = self.in_em = False; self.button = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs); classes = (a.get('class') or '').split(); self.stack.append((tag, classes))
        if tag == 'span' and 'lab' in classes and not self.button: self.in_label = True; self.labels.append('')
        elif tag == 'h1': self.in_h1 = True
        elif tag == 'em' and self.in_h1: self.in_em = True
        elif tag == 'p' and 'lede' in classes: self.in_lede = True
        elif tag == 'a' and 'btn' in classes: self.button = {'label': '', 'href': a.get('href') or '', 'ghost': 'ghost' in classes, 'skip': 0}
        elif tag == 'span' and 'ar' in classes and self.button: self.button['skip'] += 1   # the arrow glyph is decoration, not the label
        elif tag in ('img', 'video') and self.picture is None and tag == 'img': self.picture = {'src': a.get('src') or '', 'alt': a.get('alt') or ''}
        if tag in ('img', 'br', 'source'): self.stack.pop()

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag: _, classes = self.stack.pop()
        else: classes = []
        if tag == 'span' and self.button and self.button['skip'] and 'ar' in classes: self.button['skip'] -= 1
        elif tag == 'span' and self.in_label: self.in_label = False
        elif tag == 'em': self.in_em = False
        elif tag == 'h1': self.in_h1 = False
        elif tag == 'p' and self.in_lede: self.in_lede = False
        elif tag == 'a' and self.button:
            self.button['label'] = ' '.join(self.button['label'].split()); self.button.pop('skip')
            if self.button['label'] and SAFE_URL.match(self.button['href']): self.buttons.append(self.button)
            self.button = None

    def handle_data(self, data):
        if self.button is not None:
            if not self.button['skip']: self.button['label'] += data
        elif self.in_label: self.labels[-1] += data
        elif self.in_h1:
            if self.h1 and self.h1[-1][1] == self.in_em: self.h1[-1] = (self.h1[-1][0] + data, self.in_em)
            else: self.h1.append((data, self.in_em))
        elif self.in_lede: self.lede += data


def _size(data):
    """Pixel size of a data-URI image, or (None, None) when it cannot be read here."""
    try:
        from PIL import Image
        with Image.open(io.BytesIO(base64.b64decode(data.split(',', 1)[1]))) as im: return im.size
    except Exception: return (None, None)


def from_page(page_html, images=None):
    """The addresses a hero composition may use, read off a rendered page and its images.json."""
    start, end = hero_span(page_html); parser = _Hero(); parser.feed(page_html[start:end])
    clean = lambda s: ' '.join(str(s or '').split())
    text = {}
    labels = [clean(l) for l in parser.labels if clean(l)]
    if labels: text['hero.category'] = labels[0]
    if len(labels) > 1: text['hero.fact'] = labels[1]
    h1 = [(seg, em) for seg, em in parser.h1 if seg.strip()]
    if h1: text['hero.h1'] = [(re.sub(r'\s+', ' ', seg), em) for seg, em in h1]
    if clean(parser.lede): text['hero.lede'] = clean(parser.lede)
    actions = {}
    for key, button in zip(('hero.cta', 'hero.cta2'), parser.buttons[:2]): actions[key] = {'label': button['label'], 'href': button['href'], 'ghost': button['ghost']}
    by_data = {i.get('data'): i for i in (images or []) if isinstance(i, dict) and i.get('data')}
    media = {}
    for i in (images or []):
        if not isinstance(i, dict) or not i.get('data') or not i.get('id') or i.get('gen'): continue   # a generated picture is never a hero picture
        media['img:' + str(i['id'])] = {'src': i['data'], 'alt': clean(i.get('alt'))[:200], 'w': i.get('w'), 'h': i.get('h'), 'shot': bool(i.get('shot')), 'id': str(i['id'])}
    if parser.picture and parser.picture['src'].startswith('data:image/'):
        known = by_data.get(parser.picture['src'])
        w, h = (known.get('w'), known.get('h')) if known else _size(parser.picture['src'])
        media['hero.picture'] = {'src': parser.picture['src'], 'alt': parser.picture['alt'], 'w': w, 'h': h, 'shot': bool(known and known.get('shot')), 'gen': bool(known and known.get('gen')), 'id': str(known['id']) if known and known.get('id') else None}
    root = re.search(r':root\{([^}]*)\}', page_html); tokens = root.group(1) if root else ''
    px = lambda name, default: int(float((re.search(r'--' + name + r':\s*([\d.]+)px', tokens) or [None, default])[1]))
    token = lambda name: (re.search(r'--' + name + r':\s*([^;}]+)', tokens) or [None, ''])[1].strip()
    family = re.match(r"\s*'([^']+)'", token('display'))
    used_elsewhere = {key for key, m in media.items() if m['src'] in page_html[:start] + page_html[end:]}
    return {'text': text, 'actions': actions, 'media': media, 'span': (start, end),
            'page': {'container': px('container', 1300), 'frame': px('frame', 40), 'dark': _dark(token('paper')), 'display': family.group(1) if family else None,
                     'h3_weight': int(token('h3-w')) if token('h3-w').isdigit() else None, 'upper': token('h1-tt') == 'uppercase'},
            'used_elsewhere': sorted(used_elsewhere)}


def _dark(colour):
    """Is this #RRGGBB page background a dark one? Unknown reads as light."""
    m = re.fullmatch(r'#([0-9a-fA-F]{6})', colour or '')
    if not m: return False
    r, g, b = (int(m.group(1)[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.4


def words(segments):
    """The headline as words, each a list of (text, emphasised) runs: 'Your PDF, <em>redesigned</em>.' is three words and
    the last one is [('redesigned', True), ('.', False)]. A composition refers to words by their index in this list."""
    out, current = [], []
    for text, em in segments:
        for part in re.split(r'(\s+)', text):
            if not part: continue
            if part.isspace():
                if current: out.append(current); current = []
            elif current and current[-1][1] == em: current[-1] = (current[-1][0] + part, em)
            else: current.append((part, em))
    if current: out.append(current)
    return out
