"""adapt.py — what capture and the reader already produce → the data every reference template takes (schema.json).

    adapt(seed) -> dict          seed = {'inventory', 'assets', 'images', 'factsheet', 'geometry', 'source', 'logos', 'product'}
    adapt_dir(folder) -> dict    the same, read from a job folder / bench/seed/<id>/
    validate(d) -> [problems]    against schema.json

Deterministic, no model call, no network, no clock. THE RULE: nothing about a client is invented. A value goes in only
when it stands in the capture (the page's own words, links, colours, pictures), or when the reader's fact sheet states
it AND the capture confirms it letter for letter (an address, opening hours, a price). Everything else is left out and
named in `_adapter.gaps`, so a missing section is a known gap and never a guess. What is decided by rule and not read
off the page (which section is the "steps", which colour is the accent) is named in `_adapter.rules`.

Not used at all: direction.json, swarm.json, critic.json (the old pipeline's director, swarm and critic), commissioned
pictures (`gen`), and crops an agent cut (`crop_of`).

Media: a picture is written as `media/<id>.<ext>`; `_media` maps each such path to where its bytes are in the capture
({'from': 'images', 'id': …} or {'from': 'assets.logo'}), so the caller can write the files next to the page.
"""
import colorsys
import functools
import json
import re
from pathlib import Path
from urllib.parse import urlparse

VERSION = 1
HERE = Path(__file__).resolve().parent

# ───────────────────────── words the rules look for (labels a site puts on the same thing in several languages)
SIGNIN_RX = re.compile(r'^(?:log ?in|sign ?in|login|iniciar sesi[oó]n|acceder|entrar|anmelden|connexion|se connecter|accedi|prijava|prijavi se|my account|mi cuenta)$', re.I)
SIGNUP_RX = re.compile(r'(?:^|[/.?=_-])(?:register|sign[-_]?up|signup|join|get[-_]?started|start|trial|create[-_]?account)(?:$|[/.?=&_-])', re.I)
FEATURES_RX = re.compile(r'\b(?:features?|includes?|included|everything|what you get|toolkit|capabilit\w+|funciones|caracter[ií]sticas|incluye|funktionen|fonctionnalit\w+)\b', re.I)
PERIOD_RX =re.compile(r'month|year|week|/\s?(?:mo|yr|wk)\b|mes\b|año|monat|jahr|mois|\ban\b|mjesec|mesec|godi', re.I)
READY_RX =re.compile(r'^(?:ready to|start|get started|begin|try|create your|join)\b', re.I)
CTA_RX = re.compile(r'\b(?:start|get|try|sign ?up|register|create|book|reserv\w*|run|demo|buy|download|join|subscribe|order|empez\w*|prueba|crear|comenzar|pedir|see tonight|scan)\b', re.I)
LEGAL_RX = re.compile(r'\b(?:terms|privacy|legal|cookies?|imprint|impressum|datenschutz|aviso legal|pol[ií]tica|condiciones|mentions l[ée]gales|uslovi|privatnost)\b', re.I)
SKIP_RX = re.compile(r'^(?:skip to|ir al contenido|saltar al|zum inhalt|aller au contenu)', re.I)
BOOK_RX = re.compile(r'\b(?:reserv\w*|book(?:ing| a table| now| online)?|r[ée]server|prenota\w*|tisch\w*|buchen)\b', re.I)
MENU_RX = re.compile(r'\b(?:la carta|carta|men[uú]s?|speisekarte|la carte|dishes|food)\b', re.I)
TAKEAWAY_RX = re.compile(r'\b(?:take ?away|para llevar|to go|delivery|a domicilio|[àa] emporter|zum mitnehmen)\b', re.I)
STEPS_RX = re.compile(r'\b(?:how|steps?|ways|works?|process|c[oó]mo|pasos|funciona|so funktioniert|comment)\b', re.I)
PRICING_RX = re.compile(r'\b(?:pric\w+|plans?|precios?|tarif\w*|preise|membership|cennik|cene)\b', re.I)
HOURS_RX = re.compile(r'^(?:opening )?(?:hours|horarios?|[öo]ffnungszeiten|horaires|orari|radno vreme)\s*:\s*', re.I)
SINCE_RX = re.compile(r'\b(?:desde|since|est\.?|established|seit|depuis|dal|od)\s+((?:1[6-9]|20)\d{2})\b', re.I)
SOCIAL = (('instagram.com', 'Instagram'), ('facebook.com', 'Facebook'), ('linkedin.com', 'LinkedIn'), ('youtube.com', 'YouTube'), ('youtu.be', 'YouTube'),
          ('tiktok.com', 'TikTok'), ('twitter.com', 'X'), ('x.com', 'X'), ('pinterest.', 'Pinterest'), ('tripadvisor.', 'Tripadvisor'), ('threads.net', 'Threads'))
# the first of these to stand in the reader's one-sentence account of the client decides what the client is
KINDS = (
    ('software', r'software|\bapps?\b|platform|\btools?\b|saas|\bapi\b|simulator|scanner|workspace|browser-based|web app|plugin|extension|dashboard|generator'),
    ('restaurant', r'restaurant\w*|ristorante|bistro|brasserie|trattoria|pizzer[ií]a|taberna|marisquer[ií]a|steakhouse|gastrobar|restoran|tavern|eatery|asador'),
    ('cafe', r'caf[eé]\b|coffee ?shop|cafeter[ií]a|bakery|panader[ií]a|patisserie|tea ?room'),
    ('bar', r'\bbar\b|\bpub\b|cocktail|winery|bodega|brewery'),
    ('hotel', r'hotel|hostel|lodge|guest ?house|b&b|bed and breakfast|resort|\bvilla\b|apartments?\b|hostal|posada|pension'),
    ('venue', r'venue|event space|club\b|gallery|museum|theatre|theater|studio space'),
    ('shop', r'\bshop\b|\bstore\b|boutique|florist|butcher|market\b|tienda'),
)
PLACE_KINDS = {'restaurant', 'cafe', 'bar', 'hotel', 'venue', 'shop'}
ARROWS = '→›↗➜➝⟶'
PRICE_RX = re.compile(r'(?:[$€£]\s?\d[\d.,]*\d|[$€£]\s?\d|\d[\d.,]*\s?(?:€|£|\$|USD|EUR|GBP|RSD)\b|\d[\d.,]*\s?€)')
FREE_RX = re.compile(r'^(?:free|gratis|gratuit|kostenlos|besplatno)\b', re.I)


# ───────────────────────── text
def norm(s):
    return re.sub(r'\s+', ' ', str(s or '').replace(' ', ' ').replace('​', '')).strip()


_PLAIN = str.maketrans({'’': "'", '‘': "'", '“': '"', '”': '"', '´': "'", '`': "'", '–': '-', '—': '-', ' ': ' '})


def _low(s):
    """lower-case and plain quotes, one character for one character (indices stay true)"""
    s = s.translate(_PLAIN)
    lo = s.lower()
    return lo if len(lo) == len(s) else ''.join(c.lower() if len(c.lower()) == 1 else c for c in s)


def has_lower(s):
    return any(c.islower() for c in s)


BADGE_RX = re.compile(r"(?<!what's)(?<!whats)(?<!what is)(?<!\bbrand)(?<!\ball)\s+(?:new|beta|hot|soon|neu|nuevo|novo|novi|nouveau)!?$", re.I)


def strip_label(s):
    return norm(re.sub(r'(?:\s*[%s]+|\s+[»>]+)+\s*$' % ARROWS, '', str(s or '')))        # 'Start →', 'More >>' — but «a quoted name» keeps its mark


class Corpus:
    """Every word the capture read, as written. `find` looks a phrase up without regard to case or to how the white
    space fell, and gives back the page's own spelling of it."""

    def __init__(self, texts, hints=()):
        self.texts = [norm(t) for t in texts if norm(t)]
        self.hints = [norm(t) for t in hints if norm(t)]          # the reader's transcriptions: casing hints only
        self._ix = {}

    def _index(self, which):
        if which not in self._ix:
            raw = ' ␞ '.join(self.texts if which == 'texts' else self.hints)
            keep = [i for i, c in enumerate(raw) if not c.isspace()]
            self._ix[which] = (raw, _low(''.join(raw[i] for i in keep)), keep)
        return self._ix[which]

    def spans(self, phrase, which='texts'):
        raw, squeezed, keep = self._index(which)
        key = _key(phrase)
        if len(key) < 2:
            return
        at = squeezed.find(key)
        while at != -1:
            yield raw[keep[at]:keep[at + len(key) - 1] + 1]
            at = squeezed.find(key, at + 1)

    def says(self, phrase, whole=False):
        """does the capture hold this phrase (whole=True: not as a part of a longer word or number)"""
        raw, squeezed, keep = self._index('texts')
        key = _key(phrase)
        if len(key) < 2:
            return False
        at = squeezed.find(key)
        while at != -1:
            if not whole:
                return True
            a, b = keep[at], keep[at + len(key) - 1]
            before, after = raw[a - 1] if a else ' ', raw[b + 1:b + 3]
            if not (before.isalnum() and raw[a].isalnum()) and not (raw[b].isalnum() and after[:1].isalnum()) \
                    and not (raw[b].isdigit() and re.match(r'[.,]\d', after)):
                return True
            at = squeezed.find(key, at + 1)
        return False

    def _words(self):
        """each word → how the page's running text (a stretch with small letters in it) spells it, commonest first"""
        if 'words' not in self._ix:
            seen = {}
            for t in self.texts + self.hints:
                ws = re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)*", t)
                for i, w in enumerate(ws):
                    near = ws[max(0, i - 1):i] + ws[i + 1:i + 2]
                    # a word in capitals is the page's spelling only where it stands among small letters ("the NBA and"), not in a run of capitals
                    if has_lower(w) or (near and not any(len(x) > 1 and x.isupper() for x in near) and any(has_lower(x) for x in near)):
                        seen.setdefault(_low(w), {}).setdefault(w, 0)
                        seen[_low(w)][w] += 1
            best = {}
            for k, v in seen.items():
                small = sorted(((n, w) for w, n in v.items() if has_lower(w)), key=lambda x: (-x[0], x[1]))
                if small:
                    best[k] = small[0][1]
                elif len(k) <= 4:                                # only ever in capitals and short: an acronym (AI, NBA, PDF, DOCX)
                    best[k] = sorted(v)[0]
            self._ix['words'] = best
        return self._ix['words']

    def recase(self, s):
        """A label the page shows in capitals by style, set as the page's own running text spells it: the whole phrase
        where the capture has it in small letters, else word by word (so 'AI' stays 'AI' where the page writes it so),
        and a word the running text never uses is set small. The first letter of a label is a capital. Letters are
        never added or changed, only their case."""
        s = norm(s)
        if has_lower(s) or sum(c.isalpha() for c in s) < 2:
            return s
        up = lambda x: next((x[:i] + c.upper() + x[i + 1:] for i, c in enumerate(x) if c.isalpha()), x)
        spaced = None
        for which in ('texts', 'hints'):
            hits = [norm(h) for h in self.spans(s, which) if has_lower(h) and '␞' not in h]
            exact = [h for h in hits if _low(h) == _low(s)]
            if exact:
                return up(exact[0]) if not any(c.isupper() for c in exact[0]) else exact[0]
            spaced = spaced or next(iter(hits), None)             # the same letters with the page's own spaces ("RESEARCHEDPREMIUM" is two words there)
        words = self._words()
        small = lambda m: m.group(0) if has_lower(m.group(0)) else words.get(_low(m.group(0)), m.group(0).lower())
        out = re.sub(r"[^\W\d_]+(?:['’][^\W\d_]+)*", small, spaced or s)
        return up(out) if out[:1].islower() or not out[:1].isalpha() else out


def sentences(text):
    """split after a full stop, question or exclamation mark that a capital letter (of any script), a digit or an
    opening mark follows"""
    t, out, start = norm(text), [], 0
    for m in re.finditer(r'[.!?…]["”’)]?\s+', t):
        nxt = t[m.end():m.end() + 1]
        if nxt and (nxt.isupper() or nxt.isdigit() or nxt in '¿¡"“(«'):
            out.append(t[start:m.end()].strip())
            start = m.end()
    out.append(t[start:].strip())
    return [p for p in out if p]


def lead(text, cap=320, bounded=False):
    """The opening whole sentences of a run of page text, within `cap` characters. The capture gives a section's text
    without its element borders, so what follows the last full stop may belong to the next element: it is dropped,
    unless the run was cut at a known border (`bounded`) and is short."""
    parts = sentences(text)
    out = []
    for i, p in enumerate(parts):
        done = bool(re.search(r'[.!?…]["”’)]?$', p))
        if not done and not (bounded and i == 0 and len(parts) == 1 and len(p) <= 160 and not re.search(r'[·|•]', p)):
            break
        if not running(p) or len(' '.join(out + [p])) > cap:
            break
        out.append(p)
    return ' '.join(out)


def running(sentence):
    """Is this a sentence of running text — or labels, names and badges that the flattened capture ran together
    ("Léo CO-FOUNDER · POINT GUARD · 170+ EUROLEAGUE GAMES …", "Plays Practice Scouting Video Teams")? Three long
    words in capitals (not PDF, DOCX, TXT), or capitalised words in a row with nothing between them — four anywhere,
    three at the start — is not running text. A list of names with commas ("Cursor, Claude, Codex or Lovable") is."""
    words = re.findall(r"[^\W\d_]+(?:-[^\W\d_]+)*", sentence)                 # letters of any script: a Cyrillic or Greek page is read the same way
    if sum(1 for w in words if w.isupper() and '-' not in w and len(w) >= 5) >= 3:
        return False
    if any(w.isupper() and '-' in w and all(len(p) >= 2 for p in w.split('-')) for w in words):
        return False
    run = longest = 0
    opening = None                                                  # the run of capitalised words the sentence opens with
    for tok in sentence.split():
        if tok.strip('"“”\'’(«»')[:1].isupper():
            run += 1
            longest = max(longest, run)
        else:
            opening, run = (run if opening is None else opening), 0
        if re.search(r'[,;:.!?…)]$', tok):                           # a comma between names: a list, not labels run together
            opening, run = (run if opening is None else opening), 0
    opening = run if opening is None else opening
    return not (longest >= 4 or opening >= 3)


def caps_head(label):
    """('PICKS, WITH THE WHY', 'Rule-based picks against …') for a link whose text is a label in capitals followed by
    its sentence; None for anything else (and for a script without capitals)"""
    toks = norm(label).split()
    i = 0
    while i < len(toks) and not has_lower(toks[i]):
        i += 1
    head, rest = ' '.join(toks[:i]), ' '.join(toks[i:])
    return (head, rest) if 2 <= i <= 10 and sum(c.isupper() for c in head) >= 4 and len(rest) >= 12 else None


@functools.lru_cache(maxsize=4096)
def _squeeze(text):
    """(text, its letters without white space in lower case, where each of those stands in the text)"""
    t = norm(text)
    keep = [i for i, c in enumerate(t) if not c.isspace()]
    return t, _low(''.join(t[i] for i in keep)), keep


def _key(phrase):
    return _squeeze(phrase)[1]


def after(text, phrase):
    """the text that follows the first standing of `phrase` (any case, any spacing); None when it is not there"""
    (t, sq, keep), key = _squeeze(text), _key(phrase)
    at = sq.find(key) if key else -1
    return None if at == -1 else t[keep[at + len(key) - 1] + 1:].strip()


def before(text, phrase):
    (t, sq, keep), key = _squeeze(text), _key(phrase)
    at = sq.find(key) if key else -1
    return None if at == -1 else t[:keep[at]].strip()


def cut_at(text, stops, buttons=()):
    """text up to the earliest of the stop phrases; (text, cut_by_a_button). A stop of one short word is no border
    (a plan called "Pro" also stands inside sentences)."""
    best, by = None, False
    for s, is_button in [(x, False) for x in stops] + [(x, True) for x in buttons]:
        if len(norm(s)) < 8 and len(norm(s).split()) < 2 and not re.search(r'\d', s):
            continue
        b = before(text, s)
        if b is not None and (best is None or len(b) < len(best)):
            best, by = b, is_button
    return (best, by) if best is not None else (norm(text), False)


def slug(s):
    s = _low(norm(s))
    for a, b in (('áàäâã', 'a'), ('éèëê', 'e'), ('íìïî', 'i'), ('óòöôõ', 'o'), ('úùüû', 'u'), ('ñ', 'n'), ('ç', 'c'), ('ß', 'ss')):
        for c in a:
            s = s.replace(c, b)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


# ───────────────────────── colour
def _hex(c):
    m = re.match(r'^#([0-9a-fA-F]{6})$', str(c or '').strip())           # '#rrggbb a0' (a see-through fill) is not a colour of the page
    return '#' + m.group(1).lower() if m else None


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a, b):
    x, y = sorted((_lum(a), _lum(b)), reverse=True)
    return (x + .05) / (y + .05)


def _chromatic(h):
    """a colour, not a grey: a slate text colour (#374151) has a hue but no one would call it the brand's colour"""
    r, g, b = (v / 255 for v in _rgb(h))
    _, s, v = colorsys.rgb_to_hsv(r, g, b)
    return s >= .3 and max(r, g, b) - min(r, g, b) >= .25


def _far(a, b, d=48):
    return sum(abs(x - y) for x, y in zip(_rgb(a), _rgb(b))) > d


def palette(inv, assets, gaps, rules):
    cols = inv.get('colors') or {}
    tally = lambda k: [(h, _px(x.get('n'))) for x in cols.get(k) or [] if isinstance(x, dict) for h in [_hex(x.get('c'))] if h]
    bg, tx, bt = tally('bg'), tally('text'), tally('buttons')
    if not bg:
        gaps.append('palette: the capture measured no page ground; the templates fall back to their own')
        return None
    ground = bg[0][0]
    readable = [(h, n) for h, n in tx if contrast(h, ground) >= 4.5]
    if readable:
        top = max(n for _, n in readable)
        ink = max((h for h, n in readable if n >= top / 2), key=lambda h: contrast(h, ground))
        rules.append('palette.ink: of the text colours that read on the ground and are used at least half as often as the commonest, the one with most contrast')
    else:
        ink = '#000000' if _lum(ground) > .4 else '#ffffff'
        gaps.append('palette.ink: no measured text colour reads on the ground at 4.5:1; black or white stands in')
    ap = assets.get('palette') or {}
    score = {}
    for src, w, cap in ((bt, 3, None), (tx, 1, None), (bg, 1, 10)):
        for h, n in src:
            if _chromatic(h):
                score[h] = score.get(h, 0) + w * (min(n, cap) if cap else n)
    ba = _hex(ap.get('brandAccent'))
    if ba and _chromatic(ba):
        score[ba] = score.get(ba, 0) + 2
    ranked = [h for h, _ in sorted(score.items(), key=lambda kv: (-kv[1], kv[0])) if _far(h, ground)]
    out = {'ground': ground, 'ink': ink}
    if ranked:
        out['accent'] = ranked[0]
        rules.append('palette.accent: the saturated colour most used on buttons (×3), text and fills')
    else:
        gaps.append('palette.accent: the page has no saturated colour; left out (the templates use the ink)')
    extra = []
    for h in ranked[1:] + [x for x in (_hex(c.get('c')) for c in ap.get('fromLogo') or []) if x and _chromatic(x)]:
        if all(_far(h, o) for o in [ground, ink, out.get('accent', ground)] + extra):
            extra.append(h)
    out['extra'] = extra[:5]
    return out


# ───────────────────────── the adapter
def _host(u):
    try:
        return (urlparse(u).hostname or '').lower().removeprefix('www.')
    except ValueError:
        return ''


def _same(a, b):
    k = lambda u: re.sub(r'/+$', '', re.sub(r'#.*$', '', str(u or ''))).lower().replace('://www.', '://')
    return bool(a) and k(a) == k(b)


def _ext(data_uri, fallback='jpg'):
    m = re.match(r'^data:image/([a-z0-9.+-]+)', str(data_uri or ''))
    return {'jpeg': 'jpg', 'svg+xml': 'svg', 'x-icon': 'ico', 'vnd.microsoft.icon': 'ico'}.get(m.group(1), m.group(1)) if m else fallback


def kind_of(fs, inv):
    """(kind, where it was read) — the earliest telling word in the reader's sentence, else in the page's own title and description"""
    for where, text in (('reader: what', fs.get('what')), ('capture: title and description', ' '.join(filter(None, [inv.get('title'), (inv.get('seo') or {}).get('description')])))):
        t = _low(norm(text))
        m = re.search(r'\bis (?:an?|the)\b', t)
        t = t[m.end():] if m else t
        hits = [(mm.start(), k) for k, rx in KINDS for mm in [re.search(rx, t)] if mm]
        if hits:
            return min(hits)[1], where
    return '', ''


def brand_name(fs, inv, corpus):
    title = norm(inv.get('title'))
    m = re.match(r'^(.{2,60}?)\s+(?:is|are)\s+(?:an?|the)\b', norm(fs.get('what')))
    if m and corpus.says(m.group(1)):
        return next(corpus.spans(m.group(1))), 'reader: what, confirmed in the capture'
    host = _host(inv.get('url')).split('.')[0]
    parts = [p for p in re.split(r'\s+[|—–-]\s+|\.\s+', title) if p]
    for p in parts:
        if host and slug(p).replace('-', '') == host.replace('-', ''):
            return p, 'capture: title'
    if parts:
        return min(parts, key=len), 'capture: shortest part of the title'
    return host or 'Home', 'capture: host name'


def safe_href(h):
    """An address a page of ours may link to: the web, a phone number, a mail address. A captured `javascript:` or
    `data:` link would run in the preview of whoever opens it — it is not carried over."""
    h = str(h or '').strip()
    return h if re.match(r'^(?:https?://[^\s<>"\']+|mailto:[^\s<>"\']+|tel:[+\d][\d ().-]*)$', h, re.I) else None


def _actions(inv):
    out = []
    for a in inv.get('actions') or []:
        t, h = strip_label(a.get('text')), safe_href(a.get('href'))
        if not t or not h or SKIP_RX.match(t):
            continue
        out.append({'t': t, 'h': h})
    return out


def _header(inv, geo, actions, name, corpus, d, is_place, rules, gaps):
    labels = [strip_label(x) for x in (inv.get('brand') or {}).get('nav') or []]
    n = _px((geo.get('nav') or {}).get('links'))
    if n:
        labels = labels[:n]
        rules.append('nav: the first %d links the capture read from the page\'s bars — the count it measured in the top bar' % n)
    else:
        cut = next((i for i, x in enumerate(labels) if x in labels[:i]), len(labels))
        labels = labels[:max(cut, 1)] if cut else labels
        gaps.append('nav: the capture did not measure which links stand in the top bar; taken up to the first repeated label')
    home = inv.get('url')
    href = {}
    for a in actions:
        href.setdefault(_low(a['t']), a['h'])
    items, seen, dropped = [], set(), []
    for lab in labels:
        h = href.get(_low(lab))
        if h and '#' in h and _same(h, home) and slug(lab) != slug(name) and not SKIP_RX.match(lab):
            dropped.append(corpus.recase(lab))
        if not h or h.startswith(('tel:', 'mailto:', 'javascript:')) or _same(h, home) or re.fullmatch(r'[\d\W]*|[A-Z]{2}', lab) or slug(lab) == slug(name):
            continue
        key = re.sub(r'/+$', '', h.lower())
        if key in seen:
            continue
        seen.add(key)
        # a badge set beside a link ('Sim NEW', 'Props Beta') is read into its label; the link is named without it
        shown = BADGE_RX.sub('', lab) if len(lab.split()) >= 2 else lab
        items.append({'t': corpus.recase(shown or lab), 'h': h})
    nav = []
    for it in items:
        if SIGNIN_RX.match(it['t']) and 'signin' not in d and not is_place:
            d['signin'] = it
        elif LEGAL_RX.search(it['t']):
            continue
        else:
            nav.append(it)
    if dropped:
        gaps.append('nav: %d link(s) of the old top bar lead to parts of the old page (%s) and are left out — the new page is not cut the same way' % (len(dropped), ', '.join(dropped)[:120]))
    bar = (geo.get('nav') or {}).get('rect') or {}
    low = (bar.get('y') or 0) + (bar.get('h') or 0)
    buttons = {_key(strip_label(c.get('text'))) for c in geo.get('ctas') or [] if low and ((c.get('rect') or {}).get('y') or 0) < low}
    cta = next((it for it in reversed(nav) if _key(it['t']) in buttons and not re.fullmatch(r'[A-Za-z]{2}', it['t'])), None)
    if cta:
        rules.append('cta: the link of the top bar that the capture measured as a button')
    elif is_place:
        cta = next((it for it in nav if BOOK_RX.search(it['t'])), None)
    elif nav and CTA_RX.search(nav[-1]['t']):
        cta = nav[-1]
    if cta:
        nav = [it for it in nav if it is not cta]
        d['cta'] = cta
    d['nav'] = nav[:8]


def _sections(inv):
    """The home page as the capture cut it: [{title, level, text, actions, faq, quotes, kids:[h3 titles]}] in page order."""
    cov = [s for s in ((inv.get('sourceCoverage') or {}).get('sections') or []) if norm(s.get('title'))]
    heads = [(h.get('tag'), norm(h.get('text'))) for h in ((inv.get('copy') or {}).get('headings') or []) if norm(h.get('text'))]
    kids, cur = {}, None
    for tag, text in heads:
        if tag in ('H1', 'H2'):
            cur = _low(text)
            kids.setdefault(cur, [])
        elif cur is not None and tag in ('H3', 'H4') and _low(text) not in [_low(k) for k in kids[cur]]:
            kids[cur].append(text)
    out = []
    for s in cov:
        acts = [{'t': strip_label(a.get('label')), 'h': safe_href(a.get('url'))} for a in s.get('sourceActions') or [] if strip_label(a.get('label')) and safe_href(a.get('url'))]
        out.append({'title': norm(s['title']), 'level': s.get('headingLevel') or '', 'kind': s.get('kind') or '', 'text': norm(s.get('text')), 'actions': acts,
                    'faq': [f for f in s.get('faq') or [] if norm(f.get('question')) and norm(f.get('answer')) and not f.get('answerTruncated') and not f.get('questionTruncated')],
                    'quotes': [q for q in s.get('testimonials') or [] if norm(q.get('text')) and not q.get('textTruncated')],
                    'kids': list(kids.get(_low(norm(s['title'])), [])), 'used': ''})
    for s in out:                                                    # any other heading of the page ends a section's own paragraph
        s['borders'] = [t for _, t in heads if _low(t) != _low(s['title']) and len(t.split()) >= 2]
    return out


def _body(sec, extra_stops=(), cap=320):
    """the section's own opening sentences: what follows its heading, up to its first button, sub-heading or other stop"""
    rest = after(sec['text'], sec['title'])
    if rest is None:
        rest = sec['text']
    text, button = cut_at(rest, list(sec['kids']) + list(sec.get('borders') or []) + list(extra_stops), [a['t'] for a in sec['actions']])
    return lead(text, cap, bounded=button)


def _items(sec, corpus, cap=260):
    """a section's sub-headings with the text that stands between each and the next: [{title, text, k, cta}]"""
    out, rest = [], after(sec['text'], sec['title']) or sec['text']
    labels = [a['t'] for a in sec['actions']]
    for i, kid in enumerate(sec['kids']):
        head = before(rest, kid)
        tail = after(rest, kid)
        if tail is None:
            continue
        nxt = sec['kids'][i + 1] if i + 1 < len(sec['kids']) else None
        span = before(tail, nxt) if nxt and before(tail, nxt) is not None else tail
        cta = next((a for a in sec['actions'] if before(span, a['t']) is not None), None)
        text = span
        for lab in labels:                                           # a button's label inside the span is not the paragraph
            b, a = before(text, lab), after(text, lab)
            if b is not None:
                text = norm(b + ' ' + (a or '').lstrip(ARROWS + ' ')) if len(b) < 40 else b
        item = {'title': corpus.recase(kid), 'text': lead(text, cap, bounded=nxt is None and bool(cta))}
        frag = re.split(r'(?<=[.!?…])\s+', norm(head or ''))[-1] if head else ''
        for lab in labels:
            a = after(frag, lab)
            frag = a if a is not None else frag
        if frag and not re.search(r'[.!?…]$', frag) and len(frag) <= 32 and len(frag.split()) <= 4:
            item['k'] = frag
        if cta:
            item['cta'] = {'t': corpus.recase(cta['t']), 'h': cta['h']}
        out.append(item)
        rest = tail
    return out


def _split_price(price, corpus):
    """('$18.99', '/month') from the reader's '$18.99/month ($0.63/day)': the amount as the page prints it, and as much
    of what follows as the page prints right after it. (None, '') when the page does not print the amount."""
    p = norm(price)
    m = PRICE_RX.search(p)
    if not m:
        return (p.split()[0], '') if FREE_RX.match(p) and corpus.says(p.split()[0], whole=True) else (None, '')
    amount = m.group(0)
    if not corpus.says(amount, whole=True):
        return None, ''
    per, words = '', p[m.end():].split()
    for i in range(1, len(words) + 1):
        if corpus.says(amount + ' '.join(words[:i])):
            per = ' '.join(words[:i])
        else:
            break
    return amount, per.strip(' ,;')


def _stem(src):
    """What two sizes of one file have in common: the address without `-800x600`, `-scaled`, and the size and quality
    an image service is asked for (`/_next/image?url=…&w=1080&q=75` keeps its `url`, or every picture of such a site
    would count as one)."""
    path, _, query = str(src or '').partition('?')
    keep = [q for q in query.split('&') if q and q.split('=')[0].lower() not in ('w', 'h', 'q', 'width', 'height', 'quality', 'dpl', 'dpr', 'fit', 'auto', 'format', 'fm', 'v', 'ver', 'id')]
    return re.sub(r'(?:-scaled)?(?:-\d{2,4}x\d{2,4})?(\.\w+)?$', '', path) + ('?' + '&'.join(keep) if keep else '')


def _px(v):
    return int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0 else 0


def _path(u):
    try:
        return re.sub(r'/+$', '', urlparse(str(u or '')).path) or '/'
    except ValueError:
        return ''


def _pictures(images, d, media, gaps, is_place, product=None, rules=None):
    rules = rules if rules is not None else []
    photos, shots, seen = [], [], {}
    for im in images or []:
        if not isinstance(im, dict) or not im.get('data') or im.get('gen') or im.get('crop_of'):
            continue
        w, h = _px(im.get('w')), _px(im.get('h'))
        if im.get('shot'):
            if w >= 480 and h >= 200:
                shots.append({'id': im.get('id'), 'w': w, 'h': h, 'alt': norm(im.get('alt')).split('  ')[0][:120], 'page': im.get('page') or ''})
            continue
        if w < 200 or h < 200:
            continue
        if im.get('plain'):                                          # the capture's own reading: a notice, a diagram, a blank page — not a photograph
            continue
        if max(w, h) <= 600 and abs(w - h) <= .08 * max(w, h) and isinstance(im.get('flat'), (int, float)) and im['flat'] >= .7:
            continue                                                 # small, square and mostly two flat tones: a crest, a badge, an app icon — a mark, not a photograph
        stem = _stem(im.get('src') or im.get('id'))
        pic = {'src': 'media/%s.%s' % (slug(im.get('id')) or 'img', _ext(im['data'])), 'w': w, 'h': h, 'alt': norm(im.get('alt'))[:200]}
        if max(w, h) < 1000:
            pic['small'] = True
        if stem in seen:                                             # the same file served at two sizes: the larger stays
            old = seen[stem]
            if w * h > old['w'] * old['h']:
                media.pop(old['src'], None)
                old.clear()
                old.update(pic)
                media[pic['src']] = {'from': 'images', 'id': im.get('id')}
            continue
        seen[stem] = pic
        photos.append(pic)
        media[pic['src']] = {'from': 'images', 'id': im.get('id')}
    d['media'] = {'screens': [], 'phones': [], 'video': None, 'photos': photos}
    if photos:
        gaps.append('media.photos: every picture the page shows as an image is here with its own size and alt; the capture does not say what a picture shows, so `role` '
                    '(dish, room, bar, exterior, people) is not set' + ('' if is_place else ', and a product screen that the site serves as an image file is among them, not in `screens`'))
    if is_place:
        return shots
    # a product's own screens: the pages behind its top bar photographed at desk and phone width (capture product.json),
    # then — when those are fewer than three — the framed parts of its home page that are not a whole band of it
    prod = product if isinstance(product, dict) else {}
    for kind in ('screens', 'phones'):
        for i, x in enumerate(prod.get(kind) or []):
            if not isinstance(x, dict) or not x.get('data') or not _px(x.get('w')) or not _px(x.get('h')):
                continue
            src = 'media/%s-%d.%s' % (kind[:-1], i + 1, _ext(x['data']))
            d['media'][kind].append({'src': src, 'w': _px(x['w']), 'h': _px(x['h']), 'alt': norm(x.get('alt'))[:120], 'page': _path(x.get('url'))})
            media[src] = {'from': 'product', 'kind': kind, 'index': i}
    if d['media']['screens'] or d['media']['phones']:
        rules.append('media.screens, media.phones: the first screen of each page behind the top bar that shows a working product (controls, figures, data — not prose), '
                     'photographed at 1440 and at 390 wide; alt is the page\'s own heading')
    framed = [x for x in shots if 560 <= x['w'] <= 1300 and x['h'] >= 240 and 1.2 <= x['w'] / x['h'] <= 3.0 and not x['page']]
    for x in sorted(framed, key=lambda x: -x['w'] * x['h'])[:max(0, 3 - len(d['media']['screens']))]:
        im = next((i for i in images if isinstance(i, dict) and i.get('id') == x['id']), None)
        if not im or not im.get('data'):
            continue
        src = 'media/%s.%s' % (slug(x['id']), _ext(im['data']))
        first = norm(str(im.get('alt') or '').split('\n')[0])                 # the first line the framed part sets: its own heading
        d['media']['screens'].append({'src': src, 'w': x['w'], 'h': x['h'], 'alt': first[:120]})
        media[src] = {'from': 'images', 'id': x['id']}
        x['placed'] = True
    if any(x.get('placed') for x in shots):
        rules.append('media.screens: framed parts of the home page (a box with a shadow or a rounded border round a picture or controls), narrower than the page and '
                     'between 1.2 and 3 times as wide as tall, the largest first, while the product\'s own pages gave fewer than three')
    if not d['media']['screens'] and not d['media']['phones']:
        gaps.append('media.screens, media.phones: empty. No page behind the top bar showed a working product, and no framed part of the home page had the build of a screen; '
                    'the %d shot(s) of the old page are listed in `_adapter.candidates.shots` and not placed' % len(shots))
    gaps.append('media.video: none. The capture counts videos on the page and may save one film, but keeps no size or poster for it')
    return shots


def _plan_cards(plans, cards, corpus):
    """each plan gets the rows, the line and the mark of the page's price card with its name (else its price); -> how many got a card"""
    n = 0
    for it in plans:
        c = next((c for c in cards if norm(c.get('name')) and _low(norm(c['name'])) == _low(it['name'])), None) \
            or next((c for c in cards if norm(c.get('price')) and norm(c['price']) == norm(it.get('price'))), None)
        if not c:
            continue
        rows = [corpus.recase(norm(r)) for r in c.get('rows') or [] if norm(r) and corpus.says(norm(r))]
        if len(rows) < 2:
            continue
        it['rows'] = rows[:10]
        line = norm(c.get('line'))
        if line and 'line' not in it and corpus.says(line):
            it['line'] = corpus.recase(line)
        if c.get('marked'):
            it['marked'] = True
        n += 1
    return n


def _step_pictures(d, rules, gaps):
    """each step whose call leads to a page of the product gets that page's phone screen (else its desk screen); the
    rest, in order, the product's page screens not yet given. Only screens of the product's own pages (not framed parts
    of the home page), and all steps or none: a run of steps where one stands without its picture reads as a hole."""
    st = d.get('steps') or {}
    items = st.get('items') or []
    md = d.get('media') or {}
    phones, screens = [x for x in md.get('phones') or [] if x.get('page')], [x for x in md.get('screens') or [] if x.get('page')]
    pool = [(x, 'phone') for x in phones] if len(phones) >= len(items) else [(x, 'screen') for x in screens]
    if items and len(pool) < len(items):
        # no page of the product to show beside each step: the client's own pictures stand there, in the page's order —
        # what the product makes (a cover, a page) as a book, an upright picture as a portrait
        own = [x for x in md.get('photos') or [] if x.get('src') and not x.get('small')] or [x for x in md.get('photos') or [] if x.get('src')]
        if len(own) >= len(items):
            shape = lambda x: ('book' if re.search(r'\b(?:cover|e?book|libro|buch|livre)\b', x.get('alt') or '', re.I) else 'portrait') if (x.get('h') or 0) > (x.get('w') or 0) else 'photo'
            for it, x in zip(items, own):
                it['img'], it['shape'] = x['src'], shape(x)
            rules.append('steps.items[].img: the product\'s own pages gave no screen for each step; the client\'s own pictures stand beside the steps in the page\'s order')
            return
    if not items or len(pool) < len(items):
        if items:
            gaps.append('steps.items[].img: not set — the product\'s own pages gave %d screen(s) and the page %d picture(s) for %d step(s); a step is shown with a picture or not at all' % (len(pool), len(md.get('photos') or []), len(items)))
        return
    used, by_link = set(), 0
    for it in items:
        p = _path((it.get('cta') or {}).get('h'))
        hit = next(((x, k) for x, k in pool if x.get('page') and x['page'] == p and x['src'] not in used), None)
        if hit:
            it['img'], it['shape'] = hit[0]['src'], hit[1]
            used.add(hit[0]['src'])
            by_link += 1
    for it in items:
        if it.get('img'):
            continue
        hit = next(((x, k) for x, k in pool if x['src'] not in used), None)
        if not hit:
            break
        it['img'], it['shape'] = hit[0]['src'], hit[1]
        used.add(hit[0]['src'])
    if any(it.get('img') for it in items):
        rules.append('steps.items[].img: %d step(s) show the screen of the page their own call leads to; the others the product\'s remaining screens in order' % by_link)


def capture_texts(seed):
    """every text the capture read off the client's pages (the reader's fact sheet is not among them)"""
    inv, assets, geo = seed.get('inventory') or {}, seed.get('assets') or {}, seed.get('geometry') or {}
    copy = inv.get('copy') or {}
    cov = (inv.get('sourceCoverage') or {}).get('sections') or []
    texts = [inv.get('title'), copy.get('text'), (inv.get('seo') or {}).get('description'), (assets.get('social') or {}).get('description')]
    texts += [h.get('text') for h in copy.get('headings') or []] + [a.get('text') for a in inv.get('actions') or []]
    texts += [c.get('text') for c in geo.get('ctas') or []]
    texts += [s.get('text') for s in cov] + [s.get('title') for s in cov]
    for s in cov:
        texts += [f.get('question') for f in s.get('faq') or []] + [f.get('answer') for f in s.get('faq') or []] + [a.get('label') for a in s.get('sourceActions') or []]
        texts += [q.get('text') for q in s.get('testimonials') or []] + [q.get('attribution') for q in s.get('testimonials') or []]
    for p in inv.get('sourcePages') or []:
        texts += [p.get('title'), p.get('navLabel'), (p.get('copy') or {}).get('text'), ((p.get('seo') or {}).get('description'))] + [s.get('text') for s in p.get('sections') or []]
        texts += [a.get('text') for a in p.get('actions') or []]
    texts += [im.get('alt') for im in seed.get('images') or [] if isinstance(im, dict) and not im.get('gen')]
    texts += [m.get('alt') for m in (seed.get('logos') or {}).get('items') or []]
    texts += [x.get('alt') for k in ('screens', 'phones') for x in (seed.get('product') or {}).get(k) or [] if isinstance(x, dict)]   # the headings of the product's own pages
    return [t for t in texts if isinstance(t, str) and t.strip()]


def adapt(seed):
    inv = seed.get('inventory') or {}
    assets = seed.get('assets') or {}
    fs = seed.get('factsheet') or {}
    geo = seed.get('geometry') or {}
    images = seed.get('images') or []
    gaps, rules, media = [], [], {}
    pages = inv.get('sourcePages') or []
    copy = inv.get('copy') or {}
    hints = [fs.get('what'), fs.get('best_sentence')] + [x for k in ('facts', 'capabilities', 'contact') for x in (fs.get(k) or []) if isinstance(x, str)]
    corpus = Corpus(capture_texts(seed), hints)
    actions = _actions(inv)
    heads_all = sorted({norm(h.get('text')) for h in copy.get('headings') or [] if len(norm(h.get('text')).split()) >= 2}, key=len, reverse=True)
    for a in actions:
        for h in heads_all:
            if _low(a['t']).startswith(_low(h) + ' '):
                a['head'], a['t'] = h, norm(a['t'][len(h):])
                break
    for p in pages:
        actions += [a for a in _actions(p) if not any(_same(a['h'], b['h']) and a['t'] == b['t'] for b in actions)]
    home = inv.get('url') or (seed.get('source') or {}).get('url') or ''

    kind, kind_from = kind_of(fs, inv)
    is_place = kind in PLACE_KINDS
    if not kind:
        gaps.append('kind: neither the reader\'s sentence nor the page\'s title says what the client is; left empty, so no niche can be matched')
    else:
        rules.append('kind: %r — the earliest telling word in %s' % (kind, kind_from))
    name, name_from = brand_name(fs, inv, corpus)
    d = {'brand': {'name': name, 'logo': None, 'home': safe_href(home)}}
    lang = re.match(r'^[a-z]{2,3}(?![a-z])', _low(norm(inv.get('lang'))))
    if not lang:
        lang = re.search(r'(?<![a-z])[a-z]{2}(?![a-z])', _low(norm(fs.get('language'))))
        gaps.append('lang: the page states none' + ('; taken from the reader' if lang else '; "en" stands in'))
    d['lang'] = lang.group(0) if lang else 'en'
    d['kind'] = kind
    # what kind of business, in the reader's words: chooses the family of made pictures (lib/templates/pictures.py); never shown on a page
    sub = norm(fs.get('subtype') or (fs.get('business_understanding') or {}).get('offer') or fs.get('what'))[:200]
    if sub:
        d['niche'] = sub
        (rules if fs.get('subtype') else gaps).append('niche: the reader\'s ' + ('subtype' if fs.get('subtype') else 'account of what the business offers (it gave no subtype)') + '; used only to choose made pictures, never shown')
    gaps.append('character: not derivable (a judgement of the page\'s temper; the reader\'s `tone` is another vocabulary)')

    # logo: only a file the page itself marks as the brand's
    lg = assets.get('logo') or {}
    src = str(lg.get('src') or '')
    marked = (norm(lg.get('alt')) and (slug(lg.get('alt')) in slug(name) or slug(name) in slug(lg.get('alt')))) or re.search(r'logo|brand|wordmark|[-_/]mark\b', src, re.I)
    if lg.get('data') and _px(lg.get('nw')) and _px(lg.get('nh')) and marked and not re.search(r'lazy|placeholder|blank|spacer', src, re.I):
        path = 'media/logo.' + _ext(lg['data'], 'svg')
        d['brand']['logo'] = path
        media[path] = {'from': 'assets.logo'}
        if _px(lg['nw']) / _px(lg['nh']) >= 2.5:
            d['brand']['logo_wordmark'] = True
    else:
        gaps.append('brand.logo: none. The file the capture took for the logo (%s) is not marked as the brand\'s (alt %r); the name is set in type'
                    % (src.rsplit('/', 1)[-1][:50] or 'nothing', norm(lg.get('alt'))[:40]))

    pal = palette(inv, assets, gaps, rules)
    if pal:
        d['palette'] = pal
        gaps.append('palette: the page\'s measured colours only; nothing is sampled from the client\'s pictures (the hand-made files do that for `extra`)')
    _header(inv, geo, actions, name, corpus, d, is_place, rules, gaps)

    secs = _sections(inv)
    hero_sec = next((s for s in secs if s['level'] == 'H1'), None)
    if hero_sec:
        hero_sec['used'] = 'hero'

    # ── hero
    hero = {}
    h1 = norm(copy.get('h1'))
    best = [p for p in re.split(r'\s+[—–]\s+', norm(fs.get('best_sentence'))) if p]
    if h1:
        hero['title'] = corpus.recase(h1)
    elif best and len(best[0].split()) <= 12 and corpus.says(best[0]):
        hero['title'] = next(corpus.spans(best[0]))
        rules.append('hero.title: the page has no h1; the sentence the reader singled out, which stands on the page word for word')
        if len(best) > 1 and corpus.says(best[1]):
            hero['text'] = next(corpus.spans(best[1]))
    else:
        first = next((norm(h.get('text')) for h in copy.get('headings') or [] if norm(h.get('text')) and len(norm(h.get('text')).split()) <= 12), '')
        hero['title'] = corpus.recase(first) if first else name
        (rules if first else gaps).append('hero.title: the page has no h1; ' + ('its first heading stands in' if first else 'the brand name stands in'))
    if hero_sec:
        pre = before(hero_sec['text'], hero_sec['title']) or ''
        if pre and len(pre) <= 48 and len(pre.split()) <= 6:
            hero['kicker'] = corpus.recase(pre)
        rest = after(hero_sec['text'], hero_sec['title']) or ''
        chunk, cut = cut_at(rest, hero_sec['borders'], [a['t'] for a in hero_sec['actions']])
        ss = sentences(lead(chunk, 420, bounded=cut))
        if ss:
            hero['text'] = ss[0]
            if len(ss) > 1:
                hero['text2'] = lead(' '.join(ss[1:]), 240)
        own = '.'.join(_host(home).split('.')[-2:])
        acts = [a for a in hero_sec['actions'] if not re.fullmatch(r'ios|android|app store|google play', a['t'], re.I) and (not own or _host(a['h']).endswith(own))]
        measured = {_key(strip_label(c.get('text'))) for c in geo.get('ctas') or []}
        if measured:
            links_only = [a['t'] for a in acts if _key(a['t']) not in measured]
            acts = [a for a in acts if _key(a['t']) in measured]
            if links_only and not acts:
                gaps.append('hero.primary: the opening\'s links (%s) are not among the buttons the capture measured; its call is a form or a script, which has no address to carry over' % ', '.join(links_only)[:140])
        if acts:
            hero['primary'] = {'t': corpus.recase(acts[0]['t']), 'h': acts[0]['h']}
        if len(acts) > 1 and not _same(acts[1]['h'], acts[0]['h']):
            hero['secondary'] = {'t': corpus.recase(acts[1]['t']), 'h': acts[1]['h']}
        marks = [norm(x) for x in re.split(r'[✓✔]', rest)[1:]]
        trust = [m for m in marks[:-1] if 0 < len(m) <= 60]          # the last one has no border after it
        if trust:
            d['trust'] = trust
            rules.append('trust: the ticked phrases of the opening, each bounded by the next tick; the last tick has no border in the capture and is left out')
    if 'text' not in hero:
        desc = norm((inv.get('seo') or {}).get('description'))
        if desc:
            hero['text'] = desc
            rules.append('hero.text: the page\'s own meta description (the capture has no bordered text for the opening)')
    gaps.append('hero.note: not derivable (which short line the page sets beside its opening is not marked in the capture)')
    if 'trust' not in d:
        d['trust'] = []
        gaps.append('trust: empty — the opening has no ticked list the capture could bound')
    d['hero'] = hero

    # ── figures: only a number the reader lists AND the page prints, with the words that follow it
    figs = []
    for f in fs.get('facts') or []:
        m = re.match(r'^([+−-]?[$€£]?\d[\d.,]*\s?(?:%|\+|k|K|M|×|x)?)\s+(.{3,60})$', norm(f)) if isinstance(f, str) else None
        if m and len(m.group(2).split()) <= 8 and corpus.says(norm(f)) and not re.search(r'[.:;]', m.group(2)):
            figs.append({'v': m.group(1).strip(), 'l': corpus.recase(next(corpus.spans(m.group(2))))})
    # and the numbers the page sets large with their own label beside them (capture cards.json), when the reader gave fewer than three
    if len(figs) < 3:
        had = len(figs)
        for st in (seed.get('cards') or {}).get('stats') or []:
            v, l = norm(st.get('v')), norm(st.get('l'))
            if v and l and corpus.says(v) and corpus.says(l) and not any(f['v'] == v for f in figs) and len(l.split()) <= 12:
                figs.append({'v': v, 'l': corpus.recase(next(corpus.spans(l)))})
        if len(figs) > had:
            rules.append('figures: besides the reader\'s, each number the page sets at least 1.6 times its body size with the words beside it (capture cards.json)')
    d['figures'] = figs[:6]
    gaps.append('figures: %d. A fact the reader gives as "number + a few words" and the page prints in the same words, and the numbers the page sets large with their label' % len(figs))

    # ── faq, quotes: the capture reads these as pairs
    faq_sec = next((s for s in secs if s['faq']), None)
    if faq_sec:
        faq_sec['used'] = 'faq'
        d['faq'] = {'title': corpus.recase(faq_sec['title']), 'items': [{'q': corpus.recase(norm(f['question'])), 'a': norm(f['answer'])} for f in faq_sec['faq']]}
    else:
        d['faq'] = {'title': '', 'items': []}
    # both spellings the templates read: {q, name} (the newer data files) and {quote, by} (the older templates)
    d['quotes'] = [{'q': norm(q['text']), 'name': norm(q.get('attribution')), 'quote': norm(q['text']), 'by': norm(q.get('attribution'))} for s in secs for q in s['quotes']]
    if not d['quotes']:
        gaps.append('quotes: none (the capture pairs a quote with its author only where the page marks both; reviews drawn as cards are not read)')
    d['logos'] = []
    marks = (seed.get('logos') or {}).get('items') or []
    for i, m in enumerate(marks):
        if m.get('data'):
            path = 'media/mark-%d.%s' % (i + 1, _ext(m['data'], 'svg'))
            d['logos'].append({'src': path, 'w': _px(m.get('w')) or 1, 'h': _px(m.get('h')) or 1, 'alt': norm(m.get('alt'))})
            media[path] = {'from': 'logos', 'index': i}
    if not marks:
        gaps.append('logos: none in this capture')

    # ── plans (a product) : the reader's offers, each kept only when the page prints its name and its amount
    offers = [o for o in fs.get('offers') or [] if isinstance(o, dict) and norm(o.get('name'))]
    if not is_place:
        plans, amounts = [], []
        for o in offers:
            nm = norm(re.sub(r'\s*\([^)]*\)\s*$', '', o['name']))
            amount, per = _split_price(o.get('price'), corpus)
            if amount is None or not corpus.says(nm, whole=True):
                continue
            item = {'name': corpus.recase(nm), 'price': amount}
            if per:
                item['per'] = per
            if norm(o.get('note')) and corpus.says(o['note']):
                item['line'] = next(corpus.spans(o['note']))
            item['rows'] = []
            plans.append(item)
            amounts.append(amount)
        psec = None
        if not any(re.search(r'\d', a) for a in amounts):            # "Free" alone is a claim, not a price list
            plans = []
        if plans:
            priced = [a for a in amounts if re.search(r'\d', a)]
            cands = [s for s in secs if not s['used'] and sum(1 for a in priced if before(s['text'], a) is not None) >= min(2, len(priced))]
            psec = next((s for s in cands if PRICING_RX.search(s['title'])), cands[0] if cands else None)
        if plans and psec:
            psec['used'] = 'plans'
            for it in plans:
                c = next((a for a in psec['actions'] if re.search(r'\b%s\b' % re.escape(_low(it['name'])), _low(a['t']))), None)
                if c:
                    it['cta'] = {'t': corpus.recase(c['t']), 'h': c['h']}
            carded = _plan_cards(plans, (seed.get('cards') or {}).get('plans') or [], corpus)
            if carded >= 2 and carded < len(plans):
                left = [it['name'] for it in plans if not it.get('rows')]
                plans = [it for it in plans if it.get('rows')]
                rules.append('plans.items: the plans the page sets as cards (%d); offers it only names in passing (%s) are not cards and are left out' % (carded, ', '.join(left)[:120]))
            # a row of price cards holds three: with more, the plans paid by the period stand as cards when there are two or
            # three of them (else the first three in the page's order), and every other offer is named with its price in the note
            aside = []
            if len(plans) > 3:
                timed = [it for it in plans if PERIOD_RX.search(it.get('per') or '')]
                keep = timed if 2 <= len(timed) <= 3 else plans[:3]
                aside = [it for it in plans if not any(it is k for k in keep)]
                plans = keep
                rules.append('plans.items: the page prints %d offers; %s stand as cards, the others (%s) are named with their price in plans.note' % (
                    len(keep) + len(aside), 'those paid by the period' if keep is timed else 'the first three in its order', ', '.join(it['name'] for it in aside)[:120]))
            d['plans'] = {'title': corpus.recase(psec['title']), 'text': _body(psec, amounts), 'items': plans}
            if aside:
                d['plans']['note'] = ' · '.join('%s %s' % (it['name'], it['price']) for it in aside)
            if carded:
                rules.append('plans.items[].rows, .line, .marked: read from the page\'s own price cards (capture cards.json): each card\'s list, its first short paragraph, and the one card set on a ground of its own')
            else:
                gaps.append('plans.items[].rows, .line, .marked: empty — no price card of the page holds a list the capture could read; every offer the page prints with a price is listed')
        elif plans:
            d['plans'] = {'title': '', 'text': '', 'items': plans}
            gaps.append('plans.title: the plans are printed on the page but no section of the capture holds them together; no heading')
        else:
            gaps.append('plans: none — no offer of the reader\'s is printed on the page with a price')

    # ── sections by their build: link cards, steps, features; then a statement and the closing call
    free = lambda: [s for s in secs if not s['used'] and s['level'] in ('H2', 'H3')]
    for s in free():                                                 # sub-headings that are each the start of a link: cards that lead somewhere
        cards = []
        for kid in s['kids']:
            a = next((a for a in s['actions'] if _low(a['t']).startswith(_low(kid)) and len(a['t']) > len(kid) + 8), None)
            if a:
                cards.append({'t': corpus.recase(kid), 'd': norm(a['t'][len(kid):]), 'h': a['h']})
        if len(cards) >= 2 and len(cards) == len(s['kids']) and 'links' not in d:
            d['links'] = cards
            s['used'] = 'links'
    if 'links' not in d:
        cards = [{'t': corpus.recase(a['head']), 'd': corpus.recase(a['t']), 'h': a['h']} for a in actions if a.get('head')]
        if len(cards) >= 3:
            d['links'] = cards
            rules.append('links: headings of the page that are links themselves, each with the link\'s own label')
    if len(d.get("links") or []) > 6:                                # a row of link cards holds six; a longer run is the page's index, and the first six stand for it
        rules.append("links: the page has %d such cards; the first six in its order are kept" % len(d["links"]))
        d["links"] = d["links"][:6]
    if 'links' not in d:
        d['links'] = []
        gaps.append('links: none — no section of the page is a row of headed cards that each lead to a page')
    groups = [s for s in free() if 2 <= len(s['kids']) <= 5]
    worded = lambda s: all(i['text'] for i in _items(s, corpus))
    st = next((s for s in groups if STEPS_RX.search(s['title']) and worded(s)), None) or next((s for s in groups if len(s['kids']) in (3, 4) and worded(s)), None)
    if st:
        items = [i for i in _items(st, corpus) if i['title']]
        if len(items) >= 2 and all(i['text'] for i in items):
            st['used'] = 'steps'
            d['steps'] = {'title': corpus.recase(st['title']), 'text': _body(st), 'items': items}
            rules.append('steps: the first section with two to five sub-headings, each over its own sentence, whose heading speaks of how / steps / ways, else the first with three or four')
    if 'steps' not in d:
        # the page numbers its steps itself (1, 2, 3 beside a heading and a sentence each — capture cards.json): taken as numbered
        for run in (seed.get('cards') or {}).get('steps') or []:
            items = [{'k': norm(x.get('k')), 'title': norm(x.get('title')), 'text': lead(norm(x.get('text')), 260)} for x in run.get('items') or []]
            if 3 <= len(items) <= 6 and all(i['title'] and i['text'] and corpus.says(i['title']) and corpus.says(i['text'].rstrip('.…')) for i in items):
                for i in items:
                    i['title'] = corpus.recase(i['title'])
                title = norm(run.get('title'))
                d['steps'] = {'title': corpus.recase(title) if title and corpus.says(title) else '', 'text': '', 'items': items}
                rules.append('steps: a run the page numbers itself (%s … %s), each number beside its own heading and sentence, under the last heading before it' % (items[0]['k'], items[-1]['k']))
                break
    if 'steps' not in d:
        gaps.append('steps: none — no section of the page is a short run of sub-headed parts, and it numbers no run of steps')
    # features: a section that says it lists what the product holds comes before the one that merely has the most parts
    for f in sorted([s for s in free() if len(s['kids']) >= 3], key=lambda s: (0 if FEATURES_RX.search(s['title']) else 1, -len(s['kids']))):
        items = [{'t': i['title'], 'd': i['text']} for i in _items(f, corpus, 220)]
        if len(items) >= 3 and sum(1 for i in items if i['d']) * 3 >= len(items) * 2:
            f['used'] = 'features'
            d['features'] = {'title': corpus.recase(f['title']), 'text': _body(f), 'items': items}
            rules.append('features: the unused section with the most sub-headings (three or more) of which at least two in three stand over a sentence of their own')
            break
    if 'features' not in d:
        for s in free():                                             # cards that are links: a label in capitals followed by its sentence
            items = []
            for a in s['actions']:
                m = caps_head(a['t'])
                if m:
                    items.append({'t': corpus.recase(m[0]), 'd': m[1]})
            if len(items) >= 3:
                s['used'] = 'features'
                d['features'] = {'title': corpus.recase(s['title']), 'text': _body(s, [i['t'] for i in items]), 'items': items}
                rules.append('features: a section whose links are each a capitalised label followed by its sentence')
                break
    if 'features' not in d:
        gaps.append('features: none read off the page. The reader\'s `capabilities` are its own summaries (and in English whatever the site\'s language), not the client\'s words; they are not used')
    primary = (hero.get('primary') or {}).get('h')
    closers = [s for s in free() if s['level'] == 'H2' and s['actions'] and not s['kids']]
    late = [s for s in secs if s['level'] in ('H1', 'H2')][-3:]
    half = [s for s in secs[len(secs) // 2:]]
    cl = next((s for s in reversed(closers) if primary and _same(s['actions'][0]['h'], primary) and any(s is x for x in half)), None) \
        or next((s for s in reversed(closers) if len(s['actions']) == 1 and any(s is x for x in late) and CTA_RX.search(s['actions'][0]['t'])), None)
    if cl:
        cl['used'] = 'close'
        d['close'] = {'title': corpus.recase(cl['title']), 'text': _body(cl), 'cta': {'t': corpus.recase(cl['actions'][0]['t']), 'h': cl['actions'][0]['h']}}
        rules.append('close: the last section in the page\'s second half whose call repeats the opening\'s, else one of its last three sections with a single call to act')
    else:
        gaps.append('close: none — no late section of the page ends on a single call')
    for s in free():
        if s['level'] == 'H2' and s['kind'] != 'heading' and not s['kids']:
            body = _body(s)
            if len(body) >= 60:
                s['used'] = 'statement'
                d['statement'] = {'title': corpus.recase(s['title']), 'text': body}
                rules.append('statement: the first section left that is a heading over a paragraph')
                break
    if 'statement' not in d:
        gaps.append('statement: none — no section left is a heading over a paragraph')
    left = [corpus.recase(s['title']) for s in secs if not s['used']]
    if left:
        gaps.append('not placed (%d of %d sections of the page have no block in the schema, or their build was not recognised): %s' % (len(left), len(secs), ' · '.join(left)[:600]))
    if not secs:
        gaps.append('sections: the capture cut the home page into no headed sections (no h1/h2 on it); statement, steps, features, close cannot be read')

    # ── foot
    legal = re.search(r'(?:©|\(c\)|copyright)\s?[^|·•\n]{2,70}?(?=\s{2}|\s[|·•]|\.\s|$)', norm(copy.get('text')), re.I)
    flinks, seen = [], set()
    for a in actions:
        if LEGAL_RX.search(a['t']) and len(a['t']) <= 60 and a['h'].lower() not in seen and _low(a['t']) not in seen \
                and not a['h'].startswith(('tel:', 'mailto:')) and not a['h'].endswith('#'):
            seen.update((a['h'].lower(), _low(a['t'])))
            flinks.append({'t': corpus.recase(a['t']), 'h': a['h']})
    legal = norm(LEGAL_RX.split(legal.group(0))[0]) if legal else ''                 # the © line ends where the foot's links begin
    d['foot'] = {'text': '', 'legal': legal if len(legal) > 3 else '', 'links': flinks[:6]}
    if not flinks:
        gaps.append('foot.links: none — no terms / privacy link among the links the capture kept (it keeps the first hundred of a page)')
    gaps.append('foot.text: empty — the small print of the foot is not bordered in the capture' + ('' if legal else '; foot.legal: the page prints no © line the capture read'))

    shots = _pictures(images, d, media, gaps, is_place, seed.get('product'), rules)
    if not is_place:
        _step_pictures(d, rules, gaps)
    if is_place:
        _place(d, fs, inv, pages, actions, corpus, offers, gaps, rules)
        if 'cta' not in d and d['place'].get('booking'):
            d['cta'] = dict(d['place']['booking'])
        hero.setdefault('primary', d.get('cta') or None)
        menu_h = (d['place'].get('menu') or {}).get('h')
        if menu_h and 'secondary' not in hero:
            lab = next((a['t'] for a in actions if _same(a['h'], menu_h) and len(a['t']) <= 40), None)
            if lab:
                hero['secondary'] = {'t': corpus.recase(lab), 'h': menu_h}
        if hero.get('primary') is None:
            hero.pop('primary', None)
    else:
        if 'cta' not in d and hero.get('primary'):
            d['cta'] = dict(hero['primary'])
            rules.append('cta: the top bar ends on no call; the opening\'s first button stands in')
        if 'cta' not in d:
            # the page's own way in: the first of its links that leads to signing up on the client's own domain and says so
            own = '.'.join(_host(home).split('.')[-2:])
            way = next((a for a in actions if own and _host(a['h']).endswith(own) and SIGNUP_RX.search(a['h']) and CTA_RX.search(a['t']) and len(a['t']) <= 40), None)
            if way:
                d['cta'] = {'t': corpus.recase(way['t']), 'h': way['h']}
                hero.setdefault('primary', dict(d['cta']))
                rules.append('cta: neither the top bar nor the opening has a call; the page\'s first link to signing up on the client\'s own domain stands in, and opens the page too')
        if 'close' not in d and d.get('cta'):
            # a late section that asks the reader to begin ("Ready to …?", "Start …") and has no call of its own takes the page's call
            late = [s for s in secs[-4:] if s['level'] == 'H2' and not s['used'] and not s['actions'] and READY_RX.search(s['title'])]
            if late:
                s = late[-1]
                s['used'] = 'close'
                d['close'] = {'title': corpus.recase(s['title']), 'text': _body(s, [k for k in s['kids']]), 'cta': dict(d['cta'])}
                gaps[:] = [g for g in gaps if not g.startswith('close: none')]
                rules.append('close: one of the page\'s last four sections asks the reader to begin and has no call of its own; the page\'s call is set under it')
    if 'cta' not in d:
        gaps.append('cta: none — neither the top bar nor the opening has a call the capture read')

    d['_media'] = media
    d['_adapter'] = {'version': VERSION, 'name_from': name_from, 'gaps': gaps, 'rules': rules, 'candidates': {'shots': shots},
                     'reader_missing': [m for m in fs.get('missing') or [] if isinstance(m, str)]}
    return d


def _place(d, fs, inv, pages, actions, corpus, offers, gaps, rules):
    """the `place` block: address, phone, hours, booking, menu — each from a link the capture read, or from the
    reader's line confirmed letter for letter in the capture"""
    p = {}
    stated = [x for k in ('contact', 'facts') for x in (fs.get(k) or []) if isinstance(x, str)]
    for line in stated:                                              # address: a line with a postcode whose parts all stand on the page
        body = re.sub(r'^(?:address|direcci[oó]n|adresse|adresa)\s*:\s*', '', norm(line), flags=re.I)
        m = re.match(r'^(?:(.{2,40}?),\s+)?([^,]{4,60}?),?\s+(\d{4,5})\s+([^.;]{2,60}?)\.?$', body)
        if not m or re.search(r'https?:|@', body):
            continue
        street, code, town = norm(m.group(2)), m.group(3), norm(m.group(4))
        if not (corpus.says(street) and corpus.says(code, whole=True)):
            continue
        addr = {'street': next(corpus.spans(street)), 'postcode': code}
        parts = [x for x in re.split(r'\s+-\s+|,\s*', town) if x]
        if parts and corpus.says(parts[0]):
            addr['city'] = parts[0]
            if len(parts) > 1 and corpus.says(parts[1]):
                addr['region'] = parts[1]
        p['address'] = addr
        if len(parts) == 1 and ' ' in town:
            gaps.append('place.address.city: %r — the page prints town and region with nothing between them; not split' % town)
        break
    if 'address' not in p:
        gaps.append('place.address: none — no line of the reader\'s with a postcode is confirmed by the capture')
    else:
        gaps.append('place.address.country: not stated on the page')
    tel = next((a for a in actions if a['h'].startswith('tel:')), None)
    if tel:
        m = re.search(r'\+?\d[\d ().-]{5,}\d', tel['t'])
        p['phone'] = {'t': norm(m.group(0)) if m else tel['h'][4:], 'h': tel['h']}
        note = norm(tel['t'][m.end():]) if m else ''
        if note:
            p['phone']['note'] = note
    else:
        for line in stated:
            m = re.search(r'(?<![\d/])\+?\d[\d ]{7,}\d(?![\d/])', line)
            if m and not re.search(r'https?:', line) and corpus.says(m.group(0), whole=True):
                p['phone'] = {'t': norm(m.group(0)), 'h': 'tel:' + re.sub(r'[^\d+]', '', m.group(0))}
                rules.append('place.phone.h: the page prints the number without a tel: link; the link is built from its digits')
                break
    if 'phone' not in p:
        gaps.append('place.phone: none on the page')
    mail = next((a['h'][7:].split('?')[0] for a in actions if a['h'].startswith('mailto:')), None)
    if not mail:
        m = next((mm.group(0) for line in stated for mm in [re.search(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+', line)] if mm and corpus.says(mm.group(0))), None)
        mail = m
    if mail and re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', mail):
        p['email'] = mail
    else:
        gaps.append('place.email: none on the page')
    hours = []
    for line in stated:
        if not HOURS_RX.match(norm(line)):
            continue
        for part in re.split(r'\s*;\s*', HOURS_RX.sub('', norm(line))):
            m = re.match(r'^(.{2,60}?)\s+(\d{1,2}[:.]\d{2}\s?h?)\s*(?:a|-|–|—|to|bis|à|al|do)\s*(\d{1,2}[:.]\d{2}\s?h?)\.?$', part)
            if m and corpus.says(part):
                hours.append({'days': m.group(1), 'open': m.group(2), 'close': m.group(3)})
        break
    p['hours'] = hours
    if not hours:
        gaps.append('place.hours: empty — not stated on the pages the capture read in a form that could be confirmed (never guessed, and structured data the visitor does not see is not used)')
    book = next((a for a in actions if BOOK_RX.search(a['t']) and len(a['t']) <= 30 and not a['h'].startswith(('tel:', 'mailto:'))), None)
    if book:
        p['booking'] = {'t': corpus.recase(book['t']), 'h': book['h']}
    else:
        gaps.append('place.booking: no booking link on the page')
    since = SINCE_RX.search(' '.join(corpus.texts))
    if since:
        p['since'] = since.group(1)
    take = next((a for a in actions if TAKEAWAY_RX.search(a['t']) and not a['h'].startswith(('tel:', 'mailto:'))), None)
    if take:
        p['takeaway'] = {'t': corpus.recase(take['t']), 'h': take['h']}
    social, seen = [], set()
    for a in actions:
        net = next((n for dom, n in SOCIAL if dom in _host(a['h'])), None)
        if net and net not in seen and 'share' not in a['h'].lower() and urlparse(a['h']).path.strip('/'):
            seen.add(net)
            social.append({'t': net, 'h': a['h']})
    if social:
        p['social'] = social
    for line in stated:                                              # the reader quoting the page's structured data
        if re.search(r'structured data', line, re.I):
            m = re.search(r'priceRange\W+([^";]{1,20})"?', line)
            if m:
                p['price_range'] = norm(m.group(1))
            m = re.search(r'servesCuisine:?\s*([^;]+)$', line)
            if m:
                p['cuisine'] = [norm(x) for x in m.group(1).split(',') if norm(x)]
            if 'price_range' in p or 'cuisine' in p:
                rules.append('place.price_range, place.cuisine: from the page\'s structured data as the reader quotes it — not text a visitor sees, and not confirmed by the capture (which keeps only a count of structured data)')
    if 'cuisine' not in p:
        gaps.append('place.cuisine, place.price_range: not stated')
    # menu: the link to it; categories the page lists with a count; dishes the page prices
    menu = {'h': None, 'sections': [], 'lists': []}
    ml = next((a for a in actions if MENU_RX.search(a['t']) and not BOOK_RX.search(a['t']) and not re.match(r'^\d+ ', a['t'])), None)
    if ml:
        menu['h'] = ml['h']

    def counted(heads, acts):
        out, seen = [], set()
        for a in acts:
            m = re.match(r'^(\d+)\s+\w+$', norm(a.get('text') or a.get('t')))
            h = safe_href(a.get('href') or a.get('h'))
            if not m or not h:
                continue
            last = [x for x in urlparse(h).path.split('/') if x][-1:] or ['']
            head = next((x for x in heads if slug(x) == last[0]), None)
            if head and h not in seen:
                seen.add(h)
                out.append({'t': corpus.recase(head), 'count': int(m.group(1)), 'h': h})
        return out
    heads = lambda c: [norm(h.get('text')) for h in (c or {}).get('headings') or [] if norm(h.get('text'))]
    menu['sections'] = counted(heads(inv.get('copy')), inv.get('actions') or [])
    mp = next((pg for pg in pages if menu['h'] and _same(pg.get('url'), menu['h'])), None)
    if mp:
        menu['lists'] = counted(heads(mp.get('copy')), mp.get('actions') or [])
    if menu['sections'] or menu['lists']:
        rules.append('place.menu: a category is a heading the page pairs with a counted link ("5 products") whose address ends in the heading\'s own words; on the home page → sections, on the menu page → lists')
    dishes = {}
    for o in offers:
        nm = norm(re.sub(r'\s*\([^)]*\)\s*$', '', o['name']))
        m = PRICE_RX.search(norm(o.get('price')))
        if not m or not corpus.says(nm) or not corpus.says(m.group(0), whole=True):
            continue
        link = next((a['h'] for a in actions if _low(a['t']) == _low(nm)), None)
        item = {'name': next(corpus.spans(nm)), 'price': m.group(0)}
        tail = norm(norm(o['price'])[m.end():]).strip(' ,;')
        if tail and not re.search(r'\d', tail) and corpus.says(tail):
            item['note'] = tail
        if link:
            item['h'] = link
        segs = [x for x in urlparse(link or '').path.split('/') if x]
        dishes.setdefault(segs[-2] if len(segs) >= 2 else '', []).append(item)
    loose = 0
    for seg, items in dishes.items():
        if seg and len(items) >= 2:
            menu['sections'].append({'t': seg.replace('-', ' ').capitalize(), 'items': items})
            rules.append('place.menu.sections: %d priced dishes share the address part %r; it names their section' % (len(items), seg))
        else:
            loose += len(items)
    if loose:
        gaps.append('place.menu: %d priced item(s) the pages print belong to no section the capture can name; left out' % loose)
    if menu['h'] or menu['sections'] or menu['lists']:
        p['menu'] = menu
    else:
        gaps.append('place.menu: no link to a menu and no listed categories on the page')
    p['spaces'] = []
    p['events'] = []
    gaps.append('place.spaces: empty — rooms and terraces are shown as pictures with captions that the capture does not pair; place.events, place.notices: not read (a pop-up or a funding notice is not bordered in the capture)')
    d['place'] = p


def load_seed(folder):
    folder, out = Path(folder), {}
    for k in ('inventory', 'assets', 'images', 'factsheet', 'geometry', 'source', 'logos', 'product', 'cards'):
        f = folder / (k + '.json')
        try:
            out[k] = json.loads(f.read_text(encoding='utf-8')) if f.is_file() else ([] if k == 'images' else {})
        except ValueError:
            out[k] = [] if k == 'images' else {}
    return out


def adapt_dir(folder):
    return adapt(load_seed(folder))


# ───────────────────────── schema
_SCHEMA = None


def schema():
    global _SCHEMA
    if _SCHEMA is None:
        _SCHEMA = json.loads((HERE / 'schema.json').read_text(encoding='utf-8'))
    return _SCHEMA


def validate(d, sch=None, root=None, at='$'):
    """problems of `d` against schema.json (the part of JSON Schema that file uses); [] = valid"""
    root = root or schema()
    sch = root if sch is None else sch
    if '$ref' in sch:
        sch = root['definitions'][sch['$ref'].rsplit('/', 1)[-1]]
    bad = []
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'null': type(None)}
    t = sch.get('type')
    if t:
        ok = False
        for one in (t if isinstance(t, list) else [t]):
            if one == 'integer':
                ok |= isinstance(d, int) and not isinstance(d, bool)
            elif one == 'number':
                ok |= isinstance(d, (int, float)) and not isinstance(d, bool)
            else:
                ok |= isinstance(d, types[one])
        if not ok:
            return ['%s: %s, not %s' % (at, type(d).__name__, t)]
    if 'enum' in sch and d not in sch['enum']:
        bad.append('%s: %r is not one of %s' % (at, d, sch['enum']))
    if isinstance(d, str):
        if len(d) < sch.get('minLength', 0):
            bad.append('%s: empty' % at)
        if 'pattern' in sch and not re.search(sch['pattern'], d):
            bad.append('%s: %r does not match %s' % (at, d[:40], sch['pattern']))
    if isinstance(d, int) and not isinstance(d, bool) and 'minimum' in sch and d < sch['minimum']:
        bad.append('%s: %d under %d' % (at, d, sch['minimum']))
    if isinstance(d, dict):
        for k in sch.get('required', []):
            if k not in d:
                bad.append('%s: no %r' % (at, k))
        for k, sub in (sch.get('properties') or {}).items():
            if k in d:
                bad += validate(d[k], sub, root, at + '.' + k)
    if isinstance(d, list) and 'items' in sch:
        for i, x in enumerate(d):
            bad += validate(x, sch['items'], root, '%s[%d]' % (at, i))
    return bad


if __name__ == '__main__':                                          # python3 lib/templates/adapt.py <job folder>  → the data as JSON
    import sys
    out = adapt_dir(sys.argv[1])
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write('\n')
    for b in validate(out):
        sys.stderr.write('schema: ' + b + '\n')
