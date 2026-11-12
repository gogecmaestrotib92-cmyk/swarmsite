"""fryreglet/render.py — one pure function: render(d) -> a complete page.
A template for WORKS, MANUFACTURERS and FIRMS led by their own photographs (kind: corporate | service | ...).

The build was measured on the reference on 2026-11-12 at 1440 and 390 — its home page (full-height tinted opening,
the rotating half of words beside an edge-to-edge half of picture, the film band, the featured half, the two link
tiles, the foot) and, because the home page is short, its about page (short opening, words beside a pale panel, the
alternating halves), its product page (the four-column grid of pale tiles, the link-list tile) and its contact page
(the two halves of labelled paragraphs). See NOTES.md. Nothing of the reference's code, words, pictures, logo or
typefaces is here. The client's data fills it; a section whose data is missing is left out whole. No model call, no
file reads, no client logic.
"""
import html
import re

FONTS = ('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@700&'
         'family=Nunito+Sans:opsz,wght@6..12,300;6..12,400;6..12,800&display=swap')
WORDS = {  # accessible names only (never visible): the data has no words for these controls
    'en': ('Menu', 'Close', 'Previous', 'Next'), 'de': ('Menü', 'Schließen', 'Zurück', 'Weiter'),
    'fr': ('Menu', 'Fermer', 'Précédent', 'Suivant'), 'es': ('Menú', 'Cerrar', 'Anterior', 'Siguiente'),
    'it': ('Menu', 'Chiudi', 'Precedente', 'Successivo'), 'pt': ('Menu', 'Fechar', 'Anterior', 'Seguinte'),
    'sr': ('Meni', 'Zatvori', 'Prethodno', 'Sledeće'), 'nl': ('Menu', 'Sluiten', 'Vorige', 'Volgende'),
}
FOOT = '#323233'    # the reference's foot is a neutral charcoal whatever stands above it
ARROW = ('<svg class="ar" width="24" height="8" viewBox="0 0 24 8" aria-hidden="true">'
         '<path d="M23.4 3.8 17.2.2v3.1H.3v1h16.9v3.1z"/></svg>')


# ───────────────────────── colour: the reference's relations
def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _mix(a, b, t):
    a, b = _rgb(a), _rgb(b)
    return _hex(tuple(a[i] * t + b[i] * (1 - t) for i in range(3)))


def _lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def _con(a, b):
    x, y = sorted((_lum(a), _lum(b)), reverse=True)
    return (x + .05) / (y + .05)


def _theme(p):
    """Reference: a near-white ground; ONE strong colour that is both the ink on the pale grounds and the ground of
    the strong halves (white ink); a panel 4 % of it; link tiles 30 % of it; a charcoal foot."""
    g = p.get('ground') or '#fafcfe'
    if _lum(g) < .6:            # the build is a light page; a dark client ground becomes the strong colour's partner
        g = _mix('#ffffff', g, .94)
    ink = p.get('ink') or '#10233f'
    acc = p.get('accent') or ink
    # the strong colour: the accent when it can carry white words and stand on the ground, else the ink
    strong = acc if _con(acc, g) >= 3 else ink
    t = 0.0
    while t < 1 and (_con(_mix('#000000', strong, t), g) < 5.6 or _con(_mix('#000000', strong, t), '#ffffff') < 5.6):
        t += .03
    strong = _mix('#000000', strong, min(t, 1))
    panel = _mix(strong, g, .045)
    tint_src, t = (acc if _con(acc, g) < 3 else strong), .30 if _con(acc, g) >= 3 else .5
    while t > .04 and _con(strong, _mix(tint_src, g, t)) < 4.7:
        t -= .02
    tint = _mix(tint_src, g, t)
    return dict(g=g, strong=strong, panel=panel, tint=tint, line=_mix(strong, g, .2), lineS=_mix('#ffffff', strong, .28),
                soft=_mix('#ffffff', strong, .82))


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def m(src):
    return src if not src or src.startswith(('http:', 'https:', 'data:', '/')) else '../../' + src


def _href(link):
    return e((link or {}).get('h') or '#')


def _go(link, cls=''):
    """The reference's call: 12 px capitals and a long arrow that moves 5 px on hover. '' when there are no words."""
    if not link or not link.get('t'):
        return ''
    return '<a class="go %s" href="%s"><span>%s</span>%s</a>' % (cls, _href(link), e(link['t']), ARROW)


def _paras(*texts):
    return ''.join('<p>%s</p>' % e(t) for t in texts if t)


class Photos:
    """The client's photographs, each used once. A slot asks by role and least size; nothing is enlarged past 1.3×."""

    def __init__(self, d):
        self.all = [p for p in ((d.get('media') or {}).get('photos') or []) if p.get('src')]
        self.by = {p['src']: p for p in self.all}
        self.used = set()

    def own(self, src):
        """A picture a block names itself (a person's portrait, a step's picture). None when taken or unknown."""
        if not src or src in self.used:
            return None
        self.used.add(src)
        return self.by.get(src) or {'src': src, 'w': 0, 'h': 0, 'alt': ''}

    def reserve(self, src):
        if src:
            self.used.add(src)

    def pick(self, roles, minw, minh, wide=False, skip=()):
        best = None
        for p in self.all:
            if p['src'] in self.used or p['src'] in skip or p.get('role') not in roles:
                continue
            w, h = p.get('w') or 0, p.get('h') or 0
            if w * 1.3 < minw or h * 1.3 < minh or (wide and w < h * 1.2):
                continue
            key = (roles.index(p['role']) if w >= minw and h >= minh else 99, -(w * h))
            if best is None or key < best[0]:
                best = (key, p)
        if best:
            self.used.add(best[1]['src'])
            return best[1]
        return None


SCENE = ['workshop', 'machine', 'work', 'product', 'detail', 'exterior', 'room', 'landscape', 'action', 'bar', 'dish']
FIT = ['workshop', 'machine', 'work', 'product', 'detail', 'room', 'exterior']   # beside a step's or group's words
THING = ['product', 'detail', 'work', 'machine', 'workshop', 'exterior', 'room', 'landscape']


def _img(p, cls='', eager=False, sizes='(max-width:1022px) 100vw, 50vw'):
    if not p:
        return ''
    wh = ' width="%d" height="%d"' % (p['w'], p['h']) if p.get('w') and p.get('h') else ''
    return '<img class="%s" src="%s" alt="%s"%s %s decoding="async" sizes="%s">' % (
        cls, e(m(p['src'])), e(p.get('alt') or ''), wh,
        'fetchpriority="high"' if eager else 'loading="lazy"', sizes)


# ───────────────────────── parts of the reference
def _half(text_html, pic, strong, flip, kicker='', cta='', tag='section', extra=''):
    """Words in one half, an edge-to-edge photograph as tall as the section in the other (reference: 720 + 720 × 900).
    A panorama (twice as wide as high or more) would lose most of itself in an upright half: it runs edge to edge in
    its own proportion above the words instead. Without a photograph the words stand in the right half alone."""
    k = '<p class="kick">%s</p>' % e(kicker) if kicker else '<span></span>'
    c = '<div class="h-c">%s</div>' % cta if cta else '<span></span>'
    wide = bool(pic and pic.get('w') and pic.get('h') and pic['w'] >= 1.9 * pic['h'])
    if wide:
        p = '<div class="h-p" style="aspect-ratio:%d/%d">%s</div>' % (pic['w'], pic['h'], _img(pic, sizes='100vw'))
    else:
        p = '<div class="h-p par">%s</div>' % _img(pic) if pic else ''
    return '<%s class="half %s %s %s"%s><div class="h-t">%s<div class="h-m">%s</div>%s</div>%s</%s>' % (
        tag, 'S' if strong else 'P', 'flip' if flip else '', 'wide' if wide else ('' if pic else 'nopic'), extra, k, text_html, c, p, tag)


def _rot(slides, strong, flip, W, shared=None):
    """The reference's rotating half: the words change, the picture slides. slides = [(text_html, pic|None)].
    shared = one picture for every slide (quotes). One slide → a still half."""
    texts = ''.join('<article class="sl-t%s">%s</article>' % (' on' if i == 0 else '', t) for i, (t, _) in enumerate(slides))
    if shared:
        pics = '<div class="sl-p on still par">%s</div>' % _img(shared)
    else:
        pics = ''.join('<div class="sl-p%s">%s</div>' % (' on' if i == 0 else '', _img(p)) for i, (_, p) in enumerate(slides) if p)
    has = bool(pics)
    btn = ('<button class="sb prev" type="button" aria-label="%s">%s</button>'
           '<button class="sb next" type="button" aria-label="%s">%s</button>') % (e(W[2]), ARROW, e(W[3]), ARROW)
    return ('<section class="rot %s %s %s" data-n="%d"><div class="rot-t">%s</div>%s%s</section>' % (
        'S' if strong else 'P', 'flip' if flip else '', '' if has else 'nopic', len(slides), texts,
        '<div class="rot-p">%s</div>' % pics if has else '', btn if len(slides) > 1 else ''))


def _slide_text(kicker, title, body, cta, htag='h3'):
    return '%s<div class="h-m">%s%s</div>%s' % (
        '<p class="kick">%s</p>' % e(kicker) if kicker else '<span></span>',
        '<%s class="ser">%s</%s>' % (htag, e(title), htag) if title else '', body,
        '<div class="h-c">%s</div>' % cta if cta else '<span></span>')


def _band(p):
    if not p:
        return ''
    if p.get('w') and p.get('h') and p['w'] >= 1.9 * p['h']:   # a panorama runs in its own proportion, not cropped to a screen
        return '<section class="band pano" style="aspect-ratio:%d/%d">%s</section>' % (p['w'], p['h'], _img(p, sizes='100vw'))
    return '<section class="band par">%s</section>' % _img(p, sizes='100vw')


def _tiles(items, cls=''):
    return '<div class="grid %s">%s</div>' % (cls, ''.join(items))


def _fold(summary, inner, opened=False, cls=''):
    """A long list is folded (CONTRACT): a native <details>, everything one press away."""
    return '<details class="fold %s"%s><summary><span>%s</span><i aria-hidden="true"></i></summary>%s</details>' % (
        cls, ' open' if opened else '', summary, inner)


def _price(it):
    out = ''
    if it.get('price'):
        out += '<p class="pr">%s</p>' % e(it['price'])
    for p in it.get('prices') or []:
        if p.get('price'):
            out += '<p class="pr2"><span>%s</span><b>%s</b></p>' % (e(p.get('label')), e(p['price']))
    return out


def _sentence(text):
    """Split at the end of the first sentence; ('', text) when there is no clean break."""
    m = re.search(r'[.!?…](?=\s+[A-Z0-9“"‘(\u00C0-\u024F])', text or '')
    return (text[:m.end()], text[m.end():].strip()) if m and m.end() < len(text) - 20 else ('', text)


def _ptext(text, cls='', limit=140):
    """Words on a tile: when long, the first sentence stands and the rest opens in place (native <details>)."""
    if not text:
        return ''
    first, rest = _sentence(text) if len(text) > limit else ('', text)
    if not first:
        return '<p class="%s">%s</p>' % (cls, e(text))
    return ('<details class="more %s"><summary><span>%s</span><i aria-hidden="true"></i></summary><p>%s</p></details>'
            % (cls, e(first), e(rest)))


def _rows(rows, show=3):
    """A plant list: the first three rows stand; the rest open in place under '+ n'."""
    rows = [r for r in (rows or []) if r]
    if not rows:
        return ''
    head = '<ul class="rows">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in rows[:show])
    if len(rows) <= show + 1:
        return '<ul class="rows">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in rows)
    return head + ('<details class="more rows-more"><summary><span>+ %d</span><i aria-hidden="true"></i></summary>'
                   '<ul class="rows">%s</ul></details>' % (len(rows) - show, ''.join('<li>%s</li>' % e(r) for r in rows[show:])))


def _tile(name, body, h):
    """A tile. Its name is the link (a <details> may not sit inside a link); the hover of the reference is kept with :has()."""
    if h:
        return ('<div class="tile ln"><h3 class="nm"><a href="%s">%s</a></h3>%s<a class="t-ar" href="%s" tabindex="-1" aria-hidden="true">%s</a></div>'
                % (e(h), e(name), body, e(h), ARROW))
    return '<div class="tile"><h3 class="nm">%s</h3>%s</div>' % (e(name), body)


def _cat_tile(it):
    body = _price(it)
    if it.get('state'):
        body += '<p class="st">%s</p>' % e(it['state'])
    body += _ptext(it.get('text'))
    if it.get('note'):
        body += '<p class="nt">%s</p>' % e(it['note'])
    body += _rows(it.get('rows'))
    return _tile(it.get('name'), body, it.get('h'))


# ───────────────────────── the page
def render(d: dict) -> str:
    T = _theme(d.get('palette') or {})
    lang = (d.get('lang') or 'en')[:2]
    W = WORDS.get(lang, WORDS['en'])
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    hero = d.get('hero') or {}
    ph = Photos(d)

    team = d.get('team') or {}
    people = list(team.get('items') or [])
    for g in team.get('groups') or []:
        people += g.get('items') or []
    steps = d.get('steps') or {}
    step_items = [s for s in (steps.get('items') or []) if s.get('title') or s.get('text')]
    cat = d.get('catalogue') or {}
    groups = cat.get('groups') or []
    projects = [p for p in (d.get('projects') or []) if p.get('title')]

    # pictures that belong to something are kept for it, in this order: a person, a told step, a group, a project
    person_pic = [ph.own(p.get('img')) for p in people]
    step_pic = [ph.own(s.get('img')) for s in step_items]
    spot = [g for g in groups if g.get('t') and (g.get('text') or g.get('img'))]
    spot_pic = [ph.own(g.get('img')) for g in spot]
    proj_pic = []
    for p in projects:
        got = None
        for src in p.get('photos') or []:
            got = ph.own(src)
            if got:
                break
        proj_pic.append(got)
    for c in d.get('credentials') or []:
        ph.reserve(c.get('img'))
    for it in people:
        ph.reserve(it.get('img'))
    # free slots, in the order of their weight on the page
    top = ph.pick(SCENE, 1440, 900, wide=True)
    video = (d.get('media') or {}).get('video')
    pano = lambda q: bool(q and q.get('w') and q.get('h') and q['w'] >= 1.9 * q['h'])
    band1 = None
    # the band is a full screen, as the reference's film (its wide pictures are kept strictly); a step's panorama would
    # be cropped to a sliver in the rotating half, so with three or more steps the step takes another picture
    band1 = None if video else ph.pick(SCENE, 1600, 760, wide=True)
    if len(step_items) >= 3:
        step_pic = [None if pano(q) else q for q in step_pic]
    # a picture a catalogue item names is not set beside the words of another group or step (seen: a measuring cone
    # beside the tool room); it may stand in a slot without words, or beside its own group
    named = {it.get('img') for g in groups for it in (g.get('items') or []) if it.get('img')}
    # second choice for a step: a workshop scene even if an item names it (a scene fits a story; a part does not)
    step_pic = [p or ph.pick(FIT, 720, 900, skip=named) or ph.pick(['workshop', 'machine'], 720, 900) for p in step_pic]
    for i, g in enumerate(spot):
        for it in (g.get('items') or []):
            spot_pic[i] = spot_pic[i] or ph.own(it.get('img'))
        spot_pic[i] = spot_pic[i] or ph.pick(FIT, 720, 900, skip=named)
    spot = [(g, p) for g, p in zip(spot, spot_pic) if p or len(spot) == 1]
    shown = {id(g) for g, _ in spot}

    out = []
    # ── header: 140 high, name at 60, links spread from 474; clear over the opening, white after it; leaves on the way
    # down and returns on the way up
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    cta = d.get('cta') or hero.get('primary') or {}
    head_links = nav[:4]
    rest = nav[4:]
    li = ''.join('<li><a href="%s">%s</a></li>' % (_href(n), e(n['t'])) for n in head_links)
    if cta.get('t'):
        li += '<li class="last"><a href="%s">%s</a></li>' % (_href(cta), e(cta['t']))
    logo = ('<img src="%s" alt="%s">' % (e(m(brand['logo'])), e(name))) if brand.get('logo') else e(name)
    menu_li = ''.join('<li><a href="%s">%s</a></li>' % (_href(n), e(n['t'])) for n in nav)
    if cta.get('t'):
        menu_li += '<li><a href="%s">%s</a></li>' % (_href(cta), e(cta['t']))
    if (d.get('signin') or {}).get('t'):
        menu_li += '<li><a href="%s">%s</a></li>' % (_href(d['signin']), e(d['signin']['t']))
    out.append(
        '<header class="hd" id="hd"><div class="hd-bg"></div><a class="logo" href="%s">%s</a>'
        '<nav class="hd-nav"><ul>%s</ul></nav>'
        '%s</header>' % (
            e(brand.get('home') or '#'), logo, li,
            ('<button class="burger" type="button" aria-label="%s" aria-expanded="false" aria-controls="menu">'
             '<i></i><i></i></button>' % e(W[0])) if menu_li else ''))
    if menu_li:
        out.append('<div class="menu" id="menu" hidden><button class="x" type="button" aria-label="%s"><i></i><i></i></button>'
                   '<ul>%s</ul></div>' % (e(W[1]), menu_li))

    out.append('<main>')
    # ── 1 opening: the photograph in one colour, full height, the h1 in the right half
    out.append('<section class="mq %s"><div class="mq-i">%s</div><div class="mq-in"><h1 class="ser">%s</h1></div>'
               '%s</section>' % ('' if top else 'nopic', _img(top, eager=True, sizes='100vw'), e(hero.get('title') or name),
                                 '<span class="cue" aria-hidden="true"><i></i></span>'))

    # ── 2 the told half beside a pale panel (reference: about page). The panel holds the figures, else the trust lines.
    figures = [f for f in (d.get('figures') or []) if f.get('v')]
    trust = [t for t in (d.get('trust') or []) if t]
    intro_links = ''.join(x for x in (_go(hero.get('primary')), _go(hero.get('secondary'))) if x)
    note = hero.get('note')
    if hero.get('text') or hero.get('kicker'):
        if figures:
            panel = '<dl class="figs">%s</dl>' % ''.join(
                '<div><dt class="ser">%s</dt><dd>%s</dd></div>' % (e(f['v']), e(f.get('l'))) for f in figures[:4])
        elif trust:
            panel = '<ul class="trust">%s</ul>' % ''.join('<li>%s</li>' % e(t) for t in trust[:5])
        else:
            panel = ''
        out.append(
            '<section class="intro"><div class="in-p">%s</div><div class="in-t">%s<div class="copy">%s</div>%s%s</div></section>' % (
                panel, '<h2 class="ser">%s</h2>' % e(hero['kicker']) if hero.get('kicker') else '',
                _paras(hero.get('text'), hero.get('text2')),
                '<div class="gos">%s</div>' % intro_links if intro_links else '',
                '<p class="note">%s</p>' % e(note) if note else ''))

    # ── 3 the rotating half on the strong colour (reference: products spotlight) — the catalogue's groups
    if spot:
        slides = [(_slide_text(cat.get('title'), g.get('t'), _paras(g.get('text')),
                               _go({'t': g.get('t'), 'h': g.get('h')}) if g.get('h') else '', 'h2' if i == 0 else 'h3'), p)
                  for i, (g, p) in enumerate(spot)]
        out.append(_rot(slides, True, False, W))

    # ── 4 the band without words (reference: a film, edge to edge, one screen high)
    if video and video.get('src'):
        out.append('<section class="band"><video src="%s"%s muted loop playsinline autoplay preload="metadata" aria-label="%s"></video></section>' % (
            e(m(video['src'])), ' poster="%s"' % e(m(video['poster'])) if video.get('poster') else '', e(video.get('alt') or '')))
    else:
        out.append(_band(band1))

    # ── 5 alternating halves (reference: featured project on the home page, the four halves of the about page) — steps
    if len(step_items) >= 3 and all(step_pic):
        out.append(_rot([(_slide_text(s.get('k') or steps.get('title') or '', s.get('title'), _paras(s.get('text')), _go(s.get('cta')), 'h2'), p)
                         for s, p in zip(step_items, step_pic)], False, True, W))
        step_items = []
    for i, (s, p) in enumerate(zip(step_items, step_pic)):
        body = ('<h2 class="ser">%s</h2>' % e(s['title']) if s.get('title') else '') + '<div class="copy">%s</div>' % _paras(s.get('text'))
        out.append(_half(body, p, strong=(i % 2 == 1), flip=(i % 2 == 0), kicker=s.get('k') or steps.get('title') or '',
                         cta=_go(s.get('cta'))))

    # ── 6 the grid of pale tiles (reference: product page, four columns of 315 × 435) — every catalogue item, its
    # rows (plant lists, what is included) ruled as a table
    items = [it for g in groups for it in (g.get('items') or []) if it.get('name')]
    if items:
        full = [it for it in items if it.get('rows') or it.get('text') or it.get('price') or it.get('prices')]
        rich = len(full) * 2 >= len(items)
        if rich:
            # folded by group: past twelve items (CONTRACT), and here already past six when there are two or more titled
            # groups — a works' plant lists set open made a page of 18,876 px (coordinator, 2026-11-12); the first stands open
            titled = [g for g in groups if g.get('t') and any(it.get('name') for it in (g.get('items') or []))]
            long = len(items) > 12 or (len(items) > 6 and len(titled) >= 2)
            tiles, folds = [], []
            for g in groups:   # a group that found no place in the rotating half keeps its words, as a row above its tiles
                its = [it for it in (g.get('items') or []) if it.get('name')]
                if not its:
                    continue
                row = ''
                if id(g) not in shown and g.get('t') and g.get('text'):
                    row = '<div class="g-row">%s%s</div>' % ('' if long else '<h3 class="nm">%s</h3>' % e(g['t']), _ptext(g['text'], 'gr'))
                if long and g.get('t'):   # more than twelve items: each group opens in place, the first stands open
                    folds.append(_fold('%s <b>%d</b>' % (e(g['t']), len(its)), _tiles([row] + [_cat_tile(it) for it in its]), not folds))
                else:
                    tiles += [row] + [_cat_tile(it) for it in its]
            if long and not folds:
                body = _tiles(tiles[:12]) + _fold('<b>+ %d</b>' % (len(tiles) - 12), _tiles(tiles[12:]))
            else:
                body = ''.join(folds) + (_tiles(tiles) if tiles else '')
        else:   # mostly bare names: the reference's link list (12 px capitals in columns), not a wall of empty tiles
            body = '<ul class="names">%s</ul>' % ''.join(
                '<li>%s</li>' % ('<a class="go" href="%s"><span>%s</span>%s</a>' % (e(it['h']), e(it['name']), ARROW) if it.get('h')
                                 else '<span class="go">%s</span>' % e(it['name'])) for it in items)
        out.append('<section class="gs" id="catalogue">%s%s%s%s</section>' % (
            '<h2 class="ser">%s</h2>' % e(cat['title']) if cat.get('title') else '',
            '<p class="lead">%s</p>' % e(cat['text']) if cat.get('text') else '', body,
            '<p class="lead nt">%s</p>' % e(cat['note']) if cat.get('note') else ''))
        if len(items) > 4 and not any(q.get('q') for q in (d.get('quotes') or [])):
            out.append(_band(ph.pick(SCENE, 1600, 760, wide=True)))

    # ── 9 what customers say: the rotating half again, the words turning beside one still photograph of the work
    quotes = [q for q in (d.get('quotes') or []) if q.get('q')]
    if quotes:
        qp = ph.pick(THING, 720, 900)
        slides = []
        for q in quotes:
            who = ' · '.join(x for x in (q.get('name'), q.get('role')) if x)
            slides.append(('<span></span><blockquote class="h-m"><p>%s</p>%s</blockquote><span></span>' % (
                e(q['q']), '<footer class="kick">%s</footer>' % e(who) if who else ''), None))
        out.append(_rot(slides, True, False, W, shared=qp))


    # ── 7 two halves of labelled paragraphs (reference: contact page) — features with their words
    feats = d.get('features') or {}
    f_items = [f for f in (feats.get('items') or []) if f.get('t')]
    if f_items and (any(f.get('d') for f in f_items) or not items):
        out.append('<section class="split"><div class="sp-h S"><div class="stick">%s%s</div></div><div class="sp-l"><ol>%s</ol></div></section>' % (
            '<h2 class="ser">%s</h2>' % e(feats['title']) if feats.get('title') else '',
            '<p class="big">%s</p>' % e(feats['text']) if feats.get('text') else '',
            ''.join('<li>%s</li>' % (_fold(e(f['t']), '<p>%s</p>' % e(f['d']), i == 0, 'q') if (len(f_items) > 6 and f.get('d')) else
                                     '<h3 class="lab">%s</h3>%s' % (e(f['t']), '<p>%s</p>' % e(f['d']) if f.get('d') else ''))
                    for i, f in enumerate(f_items))))

    # ── 8 people: the tile grid, each person's own portrait filling the top of the tile; no portrait → type only
    if people:
        tiles = []
        for it, p in zip(people, person_pic):
            pic = '<div class="t-pic">%s</div>' % _img(p, sizes='(max-width:1022px) 100vw, 25vw') if p else ''
            more = ''
            if it.get('phone'):
                more += '<p class="nt">%s</p>' % e(it['phone'])
            if it.get('email'):
                more += '<p class="nt"><a href="mailto:%s">%s</a></p>' % (e(it['email']), e(it['email']))
            tiles.append('<div class="tile person%s">%s<h3 class="nm">%s</h3>%s%s%s</div>' % (
                '' if p else ' type', pic, e(it.get('name')),
                '<p class="role">%s</p>' % e(it['role']) if it.get('role') else '',
                _ptext(it.get('text')), more))
        out.append('<section class="gs" id="team">%s%s%s</section>' % (
            '<h2 class="ser">%s</h2>' % e(team['title']) if team.get('title') else '',
            '<p class="lead">%s</p>' % e(team['text']) if team.get('text') else '',
            _tiles(tiles) if len(tiles) <= 12 else _tiles(tiles[:12]) + _fold('<b>+ %d</b>' % (len(tiles) - 12), _tiles(tiles[12:]))))

    # ── 10 credentials: tiles, as the client states them
    creds = [c for c in (d.get('credentials') or []) if c.get('t')]
    if creds:
        tiles = []
        for c in creds:
            inner = ('<p class="pr">%s</p>' % e(c['year']) if c.get('year') else '') + _ptext(c.get('text'))
            tiles.append(_tile(c['t'], inner, c.get('h')))
        out.append('<section class="gs tight" id="credentials">%s</section>' % _tiles(tiles, 'mid'))

    # ── 11 projects: the featured half (reference: home page) — one stands still, several rotate
    if projects:
        slides = []
        for p, pic in zip(projects, proj_pic):
            if not (pic or p.get('text')):
                continue
            slides.append((_slide_text('', p['title'], _paras(p.get('text')),
                                       _go({'t': p['title'], 'h': p['h']}) if p.get('h') else '', 'h2'), pic))
        if slides and all(pic for _, pic in slides) or len(slides) == 1:
            out.append(_rot(slides, False, True, W))
        elif slides:
            out.append(_rot([s for s in slides if s[1]], False, True, W))

    # ── 12 plans and questions are never dropped: plans in the tiles, questions in the two halves
    plans = d.get('plans') or {}
    p_items = [p for p in (plans.get('items') or []) if p.get('name')]
    if p_items:
        tiles = []
        for p in p_items:
            rows = ''.join('<li>%s</li>' % e(r) for r in (p.get('rows') or []) if r)
            tiles.append('<div class="tile plan">%s<p class="pr">%s%s</p>%s%s%s</div>' % (
                '<h3 class="nm">%s</h3>' % e(p['name']), e(p.get('price')),
                ' <small>%s</small>' % e(p['per']) if p.get('per') else '',
                '<p>%s</p>' % e(p['line']) if p.get('line') else '',
                '<ul class="rows">%s</ul>' % rows if rows else '', _go(p.get('cta'))))
        out.append('<section class="gs" id="plans">%s%s%s%s</section>' % (
            '<h2 class="ser">%s</h2>' % e(plans['title']) if plans.get('title') else '',
            '<p class="lead">%s</p>' % e(plans['text']) if plans.get('text') else '', _tiles(tiles),
            '<p class="lead nt">%s</p>' % e(plans['note']) if plans.get('note') else ''))
    faq = d.get('faq') or {}
    q_items = [q for q in (faq.get('items') or []) if q.get('q')]
    if q_items:
        out.append('<section class="split" id="faq"><div class="sp-h S"><div class="stick">%s</div></div><div class="sp-l"><ol>%s</ol></div></section>' % (
            '<h2 class="ser">%s</h2>' % e(faq['title']) if faq.get('title') else '',
            ''.join('<li>%s</li>' % _fold(e(q['q']), '<p>%s</p>' % e(q.get('a')), i == 0, 'q') for i, q in enumerate(q_items))))

    # ── 13 reaching them (reference: contact page — a strong half of labelled paragraphs beside a pale half)
    place = d.get('place') or {}
    contact = d.get('contact') or {}
    close = d.get('close') or {}
    rows = []
    ad = place.get('address') or {}
    adr = ', '.join(x for x in (ad.get('street'), ' '.join(y for y in (ad.get('postcode'), ad.get('city')) if y),
                                ad.get('region'), ad.get('country')) if x)
    if adr:
        rows.append('<p>%s</p>' % e(adr))
    phone = place.get('phone') or contact.get('phone') or {}
    if phone.get('t'):
        rows.append('<p><a href="%s">%s</a>%s</p>' % (_href(phone), e(phone['t']), ' <span>%s</span>' % e(phone['note']) if phone.get('note') else ''))
    email = place.get('email') or contact.get('email')
    if email:
        rows.append('<p><a href="mailto:%s">%s</a></p>' % (e(email), e(email)))
    hours = [h for h in (place.get('hours') or []) if h.get('days')]
    if hours:
        rows.append('<p class="hrs">%s</p>' % '<br>'.join('%s <span>%s</span>' % (
            e(h['days']), e('–'.join(x for x in (h.get('open'), h.get('close')) if x))) for h in hours))
    for r in contact.get('routes') or []:
        if r.get('t'):
            rows.append('<p><b class="lab">%s</b>%s <a class="go" href="%s"><span>%s</span>%s</a></p>' % (
                e(r['t']), e(r.get('note')), _href(r),
                e((r.get('h') or '').replace('mailto:', '').replace('tel:', '') if (r.get('h') or '').startswith(('mailto:', 'tel:')) else r['t']), ARROW))
    for loc in d.get('locations') or []:
        la = loc.get('address') or {}
        ltxt = ', '.join(x for x in (la.get('street'), ' '.join(y for y in (la.get('postcode'), la.get('city')) if y)) if x)
        bits = [x for x in (ltxt, loc.get('phone') if isinstance(loc.get('phone'), str) else (loc.get('phone') or {}).get('t'),
                            loc.get('email'), loc.get('note')) if x]
        if loc.get('name') or bits:
            rows.append('<p><b class="lab">%s</b>%s</p>' % (e(loc.get('name')), e(' · '.join(bits))))
    right = ''
    if close.get('title') or close.get('text'):
        right += ('<h2 class="ser">%s</h2>' % e(close['title']) if close.get('title') else '') + '<div class="copy">%s</div>' % _paras(close.get('text'))
    r_links = ''.join(x for x in (_go(close.get('cta')), _go(place.get('booking')),
                                  _go(contact.get('form')) if (contact.get('form') or {}).get('h') != (close.get('cta') or {}).get('h') else '') if x)
    if r_links:
        right += '<div class="gos">%s</div>' % r_links
    if rows or right:
        out.append('<section class="split reach" id="contact"><div class="sp-h S">%s<div class="copy">%s</div></div>'
                   '<div class="sp-l">%s</div></section>' % ('<h2 class="ser">%s</h2>' % e(name) if rows else '', ''.join(rows), right))

    # ── 14 the two link tiles (reference: 650 × 350 each, 30 % of the strong colour): the site's pages as a link list
    # under the name, and the call
    links = [l for l in (d.get('links') or []) if l.get('t') and l.get('h')]
    t1 = ''
    if links:
        t1 = '<div class="bl multi"><h2 class="ser">%s</h2><ul>%s</ul></div>' % (
            e(name), ''.join('<li><a href="%s">%s</a></li>' % (_href(l), e(l['t'])) for l in links[:12]))
    t2 = ''
    if cta.get('t'):
        t2 = '<a class="bl single" href="%s"><h2 class="ser">%s</h2>%s</a>' % (
            _href(cta), e(cta['t']), '<span class="go"><span>%s</span>%s</span>' % (e(phone.get('t') or email or ''), ARROW))
    if t1 or t2:
        out.append('<section class="bls">%s%s</section>' % (t1, t2))
    out.append('</main>')

    # ── foot: charcoal, three columns at 60 / 720 / 1050, 12 px capitals 42 apart
    foot = d.get('foot') or {}
    social = [s for s in (place.get('social') or []) if s.get('t') and s.get('h')]
    c2 = ''.join('<li><a href="%s">%s</a></li>' % (_href(n), e(n['t'])) for n in (rest or nav))
    c3 = ''.join('<li><a href="%s">%s</a></li>' % (_href(n), e(n['t'])) for n in (social + [l for l in (foot.get('links') or []) if l.get('t')]))
    notices = ''.join('<div class="notice">%s%s</div>' % (
        '<img src="%s" alt="" loading="lazy" width="%s" height="%s">' % (e(m(n['img'])), n.get('w') or '', n.get('h') or '') if n.get('img') else '',
        ''.join('<p>%s</p>' % e(t) for t in (n.get('text') or []))) for n in (place.get('notices') or []))
    out.append('<footer class="ft"><div class="ft-c"><div class="ft-a"><p class="ft-n">%s</p>%s</div><ul>%s</ul><ul>%s</ul></div>%s%s</footer>' % (
        e(name), '<p>%s</p>' % e(foot['text']) if foot.get('text') else '', c2, c3, notices,
        '<p class="legal">%s</p>' % e(foot['legal']) if foot.get('legal') else ''))

    body = ''.join(x for x in out if x)
    desc = hero.get('text') or ''
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="%s"><style>%s</style></head><body>%s<script>%s</script></body></html>') % (
        e(lang), e(name), e(desc[:160]), FONTS, CSS % T, body, JS)


CSS = r"""
:root{--g:%(g)s;--s:%(strong)s;--panel:%(panel)s;--tint:%(tint)s;--line:%(line)s;--lineS:%(lineS)s;--soft:%(soft)s;--m:60px;
--sans:"Nunito Sans","Avenir Next",Avenir,"Helvetica Neue",Arial,sans-serif;--ser:"Libre Baskerville",Baskerville,"Times New Roman",serif;
--ez:cubic-bezier(.645,.045,.355,1)}
*,*:before,*:after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%%}
body{margin:0;background:var(--g);color:var(--s);font:300 16px/1.31 var(--sans);-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,video{display:block;max-width:100%%}
a{color:inherit;text-decoration:none}
h1,h2,h3,p,ul,ol,dl,dd,blockquote,figure{margin:0;padding:0}
ul,ol{list-style:none}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}
:focus-visible{outline:2px solid currentColor;outline-offset:4px}
.ser{font:700 48px/46px var(--ser);letter-spacing:-1px;overflow-wrap:break-word}
.kick,.lab,.nm,.go,.role{font:800 12px/1.4 var(--sans);letter-spacing:1.2px;text-transform:uppercase}
.copy p,.big,.lead{font:300 24px/36px var(--sans);letter-spacing:-.2px}
.copy p+p{margin-top:24px}
.go{display:inline-flex;align-items:center;gap:10px;padding:6px 0;max-width:100%%}
.go span{overflow-wrap:anywhere}
.ar{flex:none;fill:currentColor;transition:transform .3s var(--ez)}
a:hover .ar,button:hover .ar{transform:translateX(5px)}
.gos{display:flex;flex-wrap:wrap;gap:14px 44px;margin-top:48px}
.S{background:var(--s);color:#fff}
.P{background:var(--g);color:var(--s)}

/* header */
.hd{position:absolute;z-index:50;top:0;left:0;right:0;height:140px;display:flex;align-items:center;padding:0 var(--m);color:#fff;
transition:transform .3s cubic-bezier(.315,.44,.18,1),color .15s linear}
.hd-bg{position:absolute;inset:0;background:#fff;opacity:0;transition:opacity .15s linear;z-index:-1}
.js .hd{position:fixed}
.hd.solid{color:var(--s)}.hd.solid .hd-bg{opacity:1}
.hd.away{transform:translateY(-141px)}
.logo{flex:0 0 414px;font:300 20px/1 var(--sans);letter-spacing:1px;text-transform:uppercase;padding-right:30px}
.logo img{max-height:44px;width:auto}
.hd-nav{flex:1;min-width:0}
.hd-nav ul{display:flex}
.hd-nav li{flex:1 1 0;min-width:0}
.hd-nav li.last{flex:0 0 auto;text-align:right}
.hd-nav a{font:800 12px/1.2 var(--sans);letter-spacing:1.2px;text-transform:uppercase;display:inline-block;padding:8px 0}
.hd-nav a:hover{opacity:.7}
.burger,.menu{display:none}

/* 1 opening */
.mq{position:relative;height:100vh;min-height:560px;background:var(--s);overflow:hidden;color:#fff}
.mq-i{position:absolute;inset:0}
.mq-i img{width:100%%;height:100%%;object-fit:cover;filter:grayscale(1) contrast(1.15) brightness(1.25);mix-blend-mode:multiply}
.mq-in{position:relative;height:100%%;display:flex;align-items:center;justify-content:flex-end}
.mq h1{width:50%%;padding:0 110px 0 var(--m);animation:rise .9s cubic-bezier(.315,.44,.18,1) both}
@keyframes rise{from{transform:translateY(-50px);opacity:0}to{transform:none;opacity:1}}
.cue{position:absolute;left:50%%;bottom:30px;width:1px;height:60px;overflow:hidden}
.cue i{display:block;width:1px;height:60px;background:#fff;animation:cue 2.4s var(--ez) infinite}
@keyframes cue{0%%{transform:translateY(-60px)}50%%,60%%{transform:none}100%%{transform:translateY(60px)}}

/* 2 intro */
.intro{display:grid;grid-template-columns:1fr 1fr;padding:100px 0;background:var(--g)}
.in-p{background:var(--panel);display:flex;align-items:center;padding:60px 100px 60px var(--m);min-height:560px}
.in-t{padding:60px 160px 60px var(--m);align-self:center}
.in-t h2{margin-bottom:55px}
.note{font:800 12px/1.4 var(--sans);letter-spacing:1.2px;margin-top:28px}
.figs{display:grid;gap:44px;width:100%%}
.figs dt{margin-bottom:12px}
.figs dd{font:800 12px/1.5 var(--sans);letter-spacing:1.2px;text-transform:uppercase;max-width:420px}
.trust{width:100%%}
.trust li{font:300 24px/36px var(--sans);letter-spacing:-.2px;padding:22px 0;border-top:1px solid var(--line)}
.trust li:last-child{border-bottom:1px solid var(--line)}

/* halves */
.half{display:grid;grid-template-columns:1fr 1fr;min-height:900px}
.h-t,.sl-t{display:flex;flex-direction:column;justify-content:space-between;padding:60px 160px 60px var(--m);min-width:0}
.h-m{padding:40px 0}
.h-m .ser+.copy,.h-m .ser+p{margin-top:55px}
.sl-t .h-m>p{font:300 24px/36px var(--sans);letter-spacing:-.2px}
.h-p{position:relative;overflow:hidden;min-height:0}
.h-p img,.sl-p img,.band img,.band video{position:absolute;left:0;top:0;width:100%%;height:100%%;object-fit:cover}
.par img{top:-50px;height:calc(100%% + 100px);will-change:transform}
.half.flip .h-p{order:-1}
.half.wide,.half.nopic{grid-template-columns:1fr;min-height:0}
.half.wide .h-p{order:-1;width:100%%;max-height:900px}
.half.wide .h-t,.half.nopic .h-t{margin-left:50%%;padding-top:100px;padding-bottom:100px;gap:20px}
.h-c{min-height:27px}

/* rotating */
.rot{position:relative;display:grid;grid-template-columns:1fr 1fr;overflow:hidden}
.rot.nopic{grid-template-columns:1fr}
.rot.flip .rot-p{order:-1}
.rot-t,.rot-p{display:flex;flex-direction:column;min-width:0}
.rot-t .sl-t,.rot-p .sl-p{flex:1 1 0;min-height:640px}
.sl-p{position:relative;overflow:hidden}
blockquote.h-m p{font:300 24px/36px var(--sans);letter-spacing:-.2px}
blockquote .kick{display:block;margin-top:40px}
.sb{display:none}
.js .rot{height:100vh;min-height:640px}
.js .rot-t{display:grid}
.js .rot-t .sl-t{grid-area:1/1;opacity:0;visibility:hidden;transition:opacity .3s linear,visibility 0s .3s}
.js .rot-t .sl-t.on{opacity:1;visibility:visible;transition:opacity .45s linear .25s,visibility 0s}
.js .rot-p{display:block;position:relative;overflow:hidden}
.js .rot-p .sl-p{position:absolute;inset:0;transform:translateX(100%%);transition:transform .9s cubic-bezier(.2,.75,.2,1)}
.js .rot-p .sl-p.on{transform:none}
.js .rot-p .sl-p.was{transform:translateX(-100%%)}
.js .rot-p .sl-p.jump{transition:none}
.js .sb{display:grid;place-items:center;position:absolute;top:50%%;margin-top:-30px;width:60px;height:60px;border-radius:50%%;background:#fff;color:var(--s);
z-index:3;transition:opacity .15s linear}
.sb:focus-visible{outline:2px solid #fff;outline-offset:2px;box-shadow:0 0 0 6px var(--s)}
.sb.next{right:var(--m)}
.sb.prev{right:calc(50%% - 120px)}
.sb.prev .ar{transform:scaleX(-1)}
.sb.prev:hover .ar{transform:scaleX(-1) translateX(5px)}
.rot.flip .sb.next{right:calc(50%% + 60px)}
.rot.flip .sb.prev{right:auto;left:var(--m)}
.rot.nopic .sb{top:auto;bottom:60px;margin:0}
.rot.nopic .sb.prev{right:calc(var(--m) + 76px)}
.rot.nopic .sl-t{padding-right:max(160px,40%%)}
.sb[disabled]{opacity:0;pointer-events:none}

/* band */
.gs+.band{margin-top:120px}
.band.pano{height:auto;min-height:0;max-height:none}
.band{position:relative;height:100vh;min-height:520px;max-height:900px;overflow:hidden;background:var(--panel)}

/* tiles */
.gs{padding:200px var(--m) 0}
.gs.tight{padding-top:120px}
.gs>.ser{margin-bottom:40px}
.lead{max-width:720px;margin-bottom:20px}
.lead.nt{font-size:16px;line-height:24px;margin-top:40px}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;margin-top:60px}
.gs>.grid:first-child{margin-top:0}
.tile{position:relative;display:block;background:var(--panel);padding:30px 30px 56px;min-height:435px;transition:background-color .2s linear,box-shadow .2s linear;min-width:0}
.names{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0 20px;margin-top:60px}
.names li{border-top:1px solid var(--line);padding:16px 0}
.names .go{display:flex;justify-content:space-between}
.grid.mid .tile{min-height:300px}
a.tile:hover,.tile.ln:has(.nm a:hover){background:#fff;box-shadow:inset 0 0 0 1px var(--s)}
.tile .nm a{display:block}
.tile .nm a:after{content:"";position:absolute;inset:0;z-index:0}
.tile.ln details,.tile.ln a:not(.t-ar),.tile.ln summary{position:relative;z-index:1}
.t-ar{position:absolute;right:30px;bottom:30px;opacity:0;transition:opacity .2s linear}
a.tile:hover .t-ar,a.tile:focus-visible .t-ar,.tile.ln:has(.nm a:hover) .t-ar,.tile.ln:has(.nm a:focus-visible) .t-ar{opacity:1}
.tile .nm a:focus-visible{outline:none}
.tile.ln:has(.nm a:focus-visible){outline:2px solid var(--s);outline-offset:3px}
.tile .nm{margin-bottom:22px;overflow-wrap:break-word}
.tile p{font:400 16px/24px var(--sans);margin-top:14px;overflow-wrap:break-word}
.tile .pr{font:700 30px/36px var(--ser);letter-spacing:-.5px;margin:0 0 6px}
.tile .pr small{font:400 14px/1 var(--sans);letter-spacing:0}
.tile .pr2{display:flex;justify-content:space-between;gap:16px;border-top:1px solid var(--line);padding-top:10px}
.tile .role{margin:-12px 0 0;font-weight:400}
.tile .nt,.tile .st{font-size:14px;line-height:21px}
.tile .nt a{font-size:12px;letter-spacing:-.1px;border-bottom:1px solid var(--line)}
.rows{margin-top:22px;border-bottom:1px solid var(--line)}
.rows li{font:400 14px/21px var(--sans);padding:9px 0;border-top:1px solid var(--line);overflow-wrap:break-word}
.g-row{grid-column:1/-1;padding:50px 0 10px;max-width:720px}
.g-row p,.g-row .more>summary{font:300 24px/36px var(--sans);letter-spacing:-.2px}
.g-row>p,.g-row>.more{margin-top:18px}
.g-row .more>summary i{margin-top:12px}
.tile.person{padding-top:0}
.tile.person.type{padding-top:30px;min-height:0}
.t-pic{position:relative;margin:0 -30px 30px;aspect-ratio:4/3;overflow:hidden}
.t-pic img{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;object-position:50%% 28%%}
.tile.plan .go{margin-top:26px}

/* words and rows that open in place on a tile */
.more{margin-top:14px}
.more>summary{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;cursor:pointer;list-style:none;font:400 16px/24px var(--sans)}
.more>summary::-webkit-details-marker{display:none}
.more>summary i{flex:none;position:relative;width:11px;height:11px;margin:7px 2px 0;transition:transform .3s var(--ez)}
.more>summary i:before,.more>summary i:after{content:"";position:absolute;left:0;top:5px;width:11px;height:1px;background:currentColor}
.more>summary i:after{transform:rotate(90deg)}
.more[open]>summary i{transform:rotate(45deg)}
.more>p{margin-top:8px}
.rows-more{margin-top:0;border-bottom:1px solid var(--line)}
.rows-more>summary{font:800 12px/1.4 var(--sans);letter-spacing:1.2px;padding:10px 0}
.rows-more .rows{margin-top:0;border-bottom:0}
.rows+.rows-more{margin-top:-1px}
.rows:has(+.rows-more){border-bottom:0}
/* folded lists */
.fold{border-top:1px solid var(--line)}
.fold:last-of-type{border-bottom:1px solid var(--line)}
.fold>summary{display:flex;justify-content:space-between;align-items:center;gap:20px;cursor:pointer;list-style:none;padding:24px 0;
font:800 12px/1.4 var(--sans);letter-spacing:1.2px;text-transform:uppercase}
.fold>summary::-webkit-details-marker{display:none}
.fold>summary b{font-weight:400;margin-left:10px}
.fold>summary i{flex:none;position:relative;width:13px;height:13px;margin:0 4px;transition:transform .3s var(--ez)}
.fold>summary i:before,.fold>summary i:after{content:"";position:absolute;left:0;top:6px;width:13px;height:1px;background:currentColor}
.fold>summary i:after{transform:rotate(90deg)}
.fold[open]>summary i{transform:rotate(45deg)}
.fold>.grid{margin:10px 0 50px}
.gs>.fold:first-of-type{margin-top:60px}
.grid+.fold{margin-top:20px}
.sp-l li .fold{border:0}
.sp-l li .fold>summary{padding:0}
.sp-l li .fold>p{margin-top:12px}
.sp-l li:has(.fold){padding:24px 0}
/* two halves of labelled paragraphs */
.split{display:grid;grid-template-columns:1fr 1fr;margin-top:200px}
.rot+.split,.band+.split,.half+.split{margin-top:0}
.sp-h,.sp-l{padding:170px var(--m) 100px;min-width:0}
.sp-h .ser{margin-bottom:55px}
.stick{position:sticky;top:170px}
.sp-l{background:var(--g)}
.sp-l li{padding:30px 0;border-top:1px solid var(--line)}
.sp-l li:first-child{border-top:0;padding-top:0}
.sp-l li p{font:300 18px/28px var(--sans);margin-top:12px;max-width:600px}
.sp-l .ser{margin-bottom:55px}
.reach .copy p{overflow-wrap:anywhere}
.reach .copy a{border-bottom:1px solid var(--lineS)}
.reach .copy a.go{border:0;display:flex;font-weight:800;text-transform:none;letter-spacing:.4px;font-size:14px}
.reach .copy span{opacity:.86}
.reach .lab{display:block;margin-bottom:6px}
.reach .sp-l{background:var(--panel)}
.reach .sp-l .copy a{border-color:var(--line)}

/* link tiles */
.bls{display:flex;gap:10px;padding:180px 70px}
.bl{flex:1 1 0;min-width:0;min-height:350px;background:var(--tint);color:var(--s);padding:60px;display:flex;flex-direction:column;justify-content:space-between;gap:40px}
.bl.multi{justify-content:flex-start}
.bl.multi ul{display:grid;grid-template-columns:1fr 1fr;gap:0 20px}
.bl.multi a{display:inline-block;font:800 12px/21px var(--sans);letter-spacing:1.2px;text-transform:uppercase;padding:7px 0 8px}
.bl.multi a:hover{opacity:.7}

/* foot */
.ft{background:%(foot)s;color:#fff;padding:120px var(--m) 25px;font:400 12px/1.5 var(--sans);letter-spacing:1.2px;text-transform:uppercase}
.ft-c{display:grid;grid-template-columns:660px 330px 1fr;padding-bottom:120px}
.ft-a{padding-right:120px}
.ft-n{font-weight:800;color:rgba(255,255,255,.82);margin-bottom:30px}
.ft-a p+p{line-height:2;text-transform:none;letter-spacing:.4px;font-size:14px;max-width:420px}
.ft li{margin-bottom:14px}
.ft li a{display:inline-block;padding:7px 0}
.ft li a:hover{opacity:.7}
.legal{color:#b4b4b6}
.notice{padding-bottom:40px;text-transform:none;max-width:720px}
.notice img{max-width:260px;height:auto;margin-bottom:12px}

@media (max-width:1180px){.names{grid-template-columns:repeat(3,minmax(0,1fr))}.h-t,.sl-t,.in-t{padding-right:80px}.grid{grid-template-columns:repeat(3,minmax(0,1fr))}.ft-c{grid-template-columns:1.6fr 1fr 1fr}
.logo{flex-basis:300px}}
@media (max-width:1022px){
:root{--m:35px}
.ser{font-size:30px;line-height:36px}
.copy p,.big,.lead,.trust li,.sl-t .h-m>p,blockquote.h-m p,.g-row p,.g-row .more>summary{font-size:18px;line-height:24px}
.g-row .more>summary i{margin-top:6px}
.copy p+p{margin-top:18px}
.hd{height:80px}.hd.away{transform:translateY(-81px)}
.logo{flex:1;font-size:17px}
.hd-nav{display:none}
.burger{display:block;width:44px;height:44px;margin-right:-12px;position:relative}
.burger i,.menu .x i{position:absolute;left:12px;right:12px;height:1px;background:currentColor}
.burger i:first-child{top:18px}.burger i:last-child{top:25px}
.menu{position:fixed;inset:0;z-index:60;background:var(--s);color:#fff;padding:110px var(--m) 40px;overflow:auto}
.menu:not([hidden]){display:block}
.menu .x{position:absolute;top:18px;right:23px;width:44px;height:44px}
.menu .x i{top:22px;transform:rotate(45deg)}.menu .x i:last-child{transform:rotate(-45deg)}
.menu a{display:block;font:700 30px/36px var(--ser);padding:12px 0}
.mq h1{width:100%%;padding:0 var(--m)}
.intro{grid-template-columns:1fr;padding:0}
.in-p{min-height:0;padding:60px var(--m)}
.in-p:empty{display:none}
.in-t{padding:60px var(--m)}
.in-t h2{margin-bottom:15px}
.half,.rot{grid-template-columns:1fr;min-height:0}
.h-t,.sl-t{padding:35px;min-height:420px;gap:28px}
.h-p,.half.flip .h-p{order:-1;height:min(173vw,675px)}
.half.wide .h-t,.half.nopic .h-t{margin-left:0;padding:35px;min-height:0}
.half.wide .h-p{height:auto}
.h-m .ser+.copy,.h-m .ser+p{margin-top:15px}
.rot .rot-p,.rot.flip .rot-p{order:-1}
.rot-p .sl-p{flex:none;min-height:0;height:min(154vw,600px)}
.rot-t .sl-t{min-height:0;padding-top:35px;padding-bottom:35px;gap:28px}
.js .rot-t{min-height:420px}
.js .rot{height:auto}
.js .rot-p{height:min(154vw,600px)}
.sb.next,.rot.flip .sb.next{right:var(--m);top:calc(min(154vw,600px)/2)}
.sb.prev,.rot.flip .sb.prev{left:var(--m);right:auto;top:calc(min(154vw,600px)/2)}
.rot.nopic .sb{top:auto;bottom:35px}.rot.nopic .sb.prev{left:auto;right:calc(var(--m) + 70px)}
.rot.nopic .sl-t{padding-right:35px;padding-bottom:120px}
.band{height:min(120vw,600px);min-height:0}
.gs{padding-top:80px}.gs.tight{padding-top:60px}
.grid{grid-template-columns:1fr;margin-top:40px}
.tile,.grid.mid .tile{min-height:0;padding-bottom:30px}
.t-ar{display:none}
.names{grid-template-columns:1fr;margin-top:40px}
.split{grid-template-columns:1fr;margin-top:80px}
.sp-h,.sp-l{padding:60px var(--m)}
.sp-h .ser,.sp-l .ser{margin-bottom:20px}
.stick{position:static}
.bls{flex-direction:column;gap:35px;padding:60px var(--m)}
.bl{flex:none;min-height:197px;padding:30px}
.bl.single .go span{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%%)}
.bl.multi ul{grid-template-columns:1fr}
.ft{padding:35px var(--m);font-size:11px}
.ft-c{grid-template-columns:1fr;gap:40px;padding-bottom:50px}
.ft-a{padding-right:0}
}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}.par img{transform:none!important}}
"""

JS = r"""
(function(){var D=document,R=D.documentElement;R.classList.add('js');
var still=matchMedia('(prefers-reduced-motion: reduce)').matches;
/* header: clear over the opening, white after it; leaves on the way down, returns on the way up */
var hd=D.getElementById('hd'),mq=D.querySelector('.mq'),last=0;
function head(){var y=scrollY,lim=(mq?mq.offsetHeight:0)-hd.offsetHeight;
hd.classList.toggle('solid',y>Math.max(lim,40));
if(y>last+2&&y>hd.offsetHeight)hd.classList.add('away');else if(y<last-2||y<=hd.offsetHeight)hd.classList.remove('away');last=y}
/* pictures in the halves drift 5 px per 100 px of travel, as measured (−50 … +45) */
var pars=[].slice.call(D.querySelectorAll('.par img')),tick=0;
function drift(){tick=0;if(still)return;var vh=innerHeight;pars.forEach(function(im){var r=im.parentNode.getBoundingClientRect();
if(r.bottom<-80||r.top>vh+80)return;var t=Math.max(-50,Math.min(45,-r.top*.05));im.style.transform='translate3d(0,'+t.toFixed(1)+'px,0)'})}
addEventListener('scroll',function(){head();if(!tick)tick=requestAnimationFrame(drift)},{passive:true});
addEventListener('resize',drift);head();drift();
D.addEventListener('focusin',function(ev){if(hd.contains(ev.target))hd.classList.remove('away')});
/* phone menu */
var bg=D.querySelector('.burger'),mn=D.getElementById('menu');
if(bg&&mn){var x=mn.querySelector('.x');function set(o){mn.hidden=!o;bg.setAttribute('aria-expanded',o);R.style.overflow=o?'hidden':'';(o?x:bg).focus()}
bg.addEventListener('click',function(){set(true)});x.addEventListener('click',function(){set(false)});
mn.addEventListener('click',function(ev){if(ev.target.closest('a'))set(false)});
D.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&!mn.hidden)set(false)})}
/* rotating halves: 5 s a slide, the picture slides in .9 s, the words cross-fade */
[].forEach.call(D.querySelectorAll('.rot'),function(rot){
var ts=[].slice.call(rot.querySelectorAll('.sl-t')),ps=[].slice.call(rot.querySelectorAll('.sl-p:not(.still)')),n=ts.length,i=0,tm=0;
var prev=rot.querySelector('.prev'),next=rot.querySelector('.next');if(n<2)return;
function show(j,dir){j=(j+n)%%n;if(j===i)return;
if(ps.length===n){var a=ps[i],b=ps[j];b.classList.add('jump');b.classList.toggle('was',dir<0);b.classList.remove('on');b.offsetWidth;b.classList.remove('jump');
a.classList.remove('on');a.classList.toggle('was',dir>0);b.classList.remove('was');b.classList.add('on')}
ts[i].classList.remove('on');ts[j].classList.add('on');i=j;if(prev)prev.disabled=i===0}
function auto(){clearInterval(tm);if(!still)tm=setInterval(function(){if(!D.hidden&&!rot.matches(':hover')&&!rot.contains(D.activeElement))show(i+1,1)},5000)}
if(prev){prev.disabled=true;prev.addEventListener('click',function(){show(i-1,-1);auto()})}
if(next)next.addEventListener('click',function(){show(i+1,1);auto()});
rot.addEventListener('keydown',function(ev){if(ev.key==='ArrowRight'){show(i+1,1);auto()}if(ev.key==='ArrowLeft'){show(i-1,-1);auto()}});
auto()});
})();
"""
CSS = CSS.replace('%(foot)s', FOOT)
JS = JS.replace('%%', '%')
