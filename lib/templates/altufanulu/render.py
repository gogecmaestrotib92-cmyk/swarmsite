"""altufanulu/render.py — one pure function: render(d) -> a complete page.

The build (section order and anatomy, measures, type scale, spacing, grounds, the relation of text and picture, motion,
the phone build) was measured on https://altufanulu.com/en at 1440 and 390 on 2026-11-12, with its about, practice-areas,
practice-area and contact pages for the parts the home page lacks (see NOTES.md). Nothing of the reference's code, words,
pictures, icons, logo or typefaces is here. Its pictures are stock (a city film, towers, a blurred lobby); only the build
is taken — every picture slot takes the client's own photograph or stays a plain ground.
A section whose data is missing is left out whole. No model call, no file reads, no client logic.
"""
import html
import re

FONTS = ('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500'
         '&family=Inter:wght@300;400;500;600;700&display=swap')

# words of the interface itself (not client copy); a language not listed gets signs and values only
UI = {'en': {'menu': 'Menu', 'close': 'Close', 'next': 'Next', 'prev': 'Back', 'skip': 'Skip to content', 'top': 'Back to top',
             'hours': 'Opening hours', 'phone': 'Phone', 'email': 'Email', 'address': 'Address'},
      'de': {'menu': 'Menü', 'close': 'Schließen', 'next': 'Weiter', 'prev': 'Zurück', 'skip': 'Zum Inhalt', 'top': 'Nach oben',
             'hours': 'Sprechzeiten', 'phone': 'Telefon', 'email': 'E-Mail', 'address': 'Adresse'}}

M = '../../'          # a page in <slug>/out/ reaches media two folders up
SAY_MAX = 200         # a block's text is set as the 40px statement up to this length; longer text is a paragraph
CARD_TEXT_MAX = 220   # a card carries its text on the picture up to this length; longer texts stand under the cards
SLIDE_TEXT_MAX = 260  # a carousel column carries its text up to this length when a catalogue gives it in full below


# ───────────────────────── colour: the reference's relations — white ground, a 4 % grey zone, one deep band colour
def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _mix(a, b, t):
    """t of a over b"""
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


def _palette(p):
    g, k = p.get('ground') or '#ffffff', p.get('ink') or '#111111'
    a = p.get('accent') or k
    if _con(g, k) < 7:                                     # an ink that does not carry text on its ground is not used as given
        k = '#111111' if _lum(g) > .45 else '#f4f4f4'
    dark = _lum(g) < .45
    if dark:
        deep, on = _mix('#000000', g, .4), k
    else:
        deep = k
        while _lum(deep) > .035:                           # the band colour is the ink, taken down until white reads on it as on the reference's navy
            deep = _mix('#000000', deep, .12)
        on = '#ffffff'
    alt = _mix(k, g, .045)                                 # #f4f4f5 on white under a navy ink
    rule = _mix(k, g, .30)                                 # #b3b3b3
    muted = _mix(k, g, .72)
    while min(_con(muted, g), _con(muted, alt)) < 4.6:
        muted = _mix(k, muted, .12)
    on_a = k if _con(k, a) >= 4.5 else max((deep, '#ffffff', '#000000'), key=lambda c: _con(c, a))
    return dict(shade=_mix('#000000', deep, .72), g=g, k=k, a=a, deep=deep, on=on, alt=alt, rule=rule, muted=muted, on_a=on_a, dark=dark)


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def _t(x):
    return (x or '').strip() if isinstance(x, str) else ''


def _lst(x):
    return x if isinstance(x, list) else []


def _dic(x):
    return x if isinstance(x, dict) else {}


def _src(s):
    s = _t(s)
    return s if re.match(r'(https?:|data:|/)', s) else M + s


ARROW = ('<svg class="arw" viewBox="0 0 20 18" width="20" height="18" aria-hidden="true" focusable="false">'
         '<path d="M0 9h18.5M11 1.5 18.5 9 11 16.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>')
ARROW_BIG = ('<svg viewBox="0 0 30 21" width="30" height="21" aria-hidden="true" focusable="false">'
             '<path d="M0 10.5h28.5M19 1.5l9.5 9-9.5 9" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>')
ARROW_UP = ('<svg viewBox="0 0 21 24" width="21" height="24" aria-hidden="true" focusable="false">'
            '<path d="M10.5 24V1.5M1.5 10.5l9-9 9 9" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>')


def _btn(link, cls='', arrow=True):
    link = _dic(link)
    if not _t(link.get('t')):
        return ''
    return '<a class="btn %s" href="%s"><span>%s</span>%s</a>' % (cls, e(link.get('h') or '#'), e(link['t']), ARROW if arrow else '')


def _paras(text, cls=''):
    parts = [p.strip() for p in re.split(r'\n\s*\n|\n', _t(text)) if p.strip()]
    return ''.join('<p%s>%s</p>' % (' class="%s"' % cls if cls else '', e(p)) for p in parts)


def _head(title, text, tag='h2', extra=''):
    """the reference's section head: a 24px capital label at the left, a 40px statement from the fifth column.
    The label is the block's title; the statement is its text when that is a sentence or two, otherwise the text is a paragraph."""
    title, text = _t(title), _t(text)
    if not title and not text:
        return ''
    lab = '<%s class="lab">%s</%s>' % (tag, e(title), tag) if title else '<span class="lab"></span>'
    if text and len(text) <= SAY_MAX:
        right = '<p class="say">%s</p>' % e(text)
    elif text:
        right = '<div class="txt">%s</div>' % _paras(text)
    else:
        right = ''
    return '<div class="head">%s%s%s</div>' % (lab, ('<div class="head-r">%s%s</div>' % (right, extra)) if (right or extra) else '', '')


def _longest_word(strings):
    return max([len(w) for s in strings for w in re.split(r'[\s/–—-]+', s)] or [0])


# ───────────────────────── pictures: chosen by role, size and proportion; each once; never looped
class Pool:
    def __init__(self, d):
        media = _dic(d.get('media'))
        self.all = [p for p in _lst(media.get('photos')) if isinstance(p, dict) and _t(p.get('src'))]
        self.by_src = {p['src']: p for p in self.all}
        taken = set()
        for it in _lst(_dic(d.get('steps')).get('items')):
            taken.add(_t(_dic(it).get('img')))
        team = _dic(d.get('team'))
        for it in _lst(team.get('items')) + [x for g in _lst(team.get('groups')) for x in _lst(_dic(g).get('items'))]:
            taken.add(_t(_dic(it).get('img')))
        for it in _lst(d.get('credentials')):
            taken.add(_t(_dic(it).get('img')))
        for g in _lst(_dic(d.get('catalogue')).get('groups')):
            taken.add(_t(_dic(g).get('img')))
            for it in _lst(_dic(g).get('items')):
                taken.add(_t(_dic(it).get('img')))
        taken.add(_t(_dic(d.get('brand')).get('logo')))
        self.free = [p for p in self.all if p['src'] not in taken and p.get('role') != 'portrait' and not p.get('small')]

    def take(self, roles, minw, minh, rmin=0, rmax=99):
        best = None
        for p in self.free:
            w, h = p.get('w') or 0, p.get('h') or 0
            role = p.get('role') or 'other'
            if role not in roles or w < minw or h < minh or not h or not (rmin <= w / h <= rmax):
                continue
            key = (roles.index(role), -(w * h))
            if best is None or key < best[0]:
                best = (key, p)
        if best:
            self.free.remove(best[1])
            return best[1]
        return None

    def give_back(self, ps):
        self.free = [p for p in ps if p] + self.free

    def own(self, src):
        """a picture a block names itself: used when it is one of the client's photographs and not small"""
        src = _t(src)
        if not src:
            return None
        p = self.by_src.get(src)
        if p is None:                       # a product screen or anything that is not one of the client's photographs is not cropped into a card
            return None
        return None if p.get('small') or p.get('role') == 'portrait' else p


ANY = ['room', 'work', 'workshop', 'action', 'people', 'exterior', 'landscape', 'detail', 'product', 'dish', 'bar', 'other']


def _img(p, cls='', sizes='100vw', eager=False):
    wh = ' width="%d" height="%d"' % (p['w'], p['h']) if p.get('w') and p.get('h') else ''
    return '<img class="%s" src="%s" alt="%s"%s%s decoding="async">' % (
        cls, e(_src(p['src'])), e(p.get('alt') or ''), wh, '' if eager else ' loading="lazy"')


# ───────────────────────── sections
def _header(d, ui):
    brand = _dic(d.get('brand'))
    name = _t(brand.get('name'))
    nav = [n for n in _lst(d.get('nav')) if _t(_dic(n).get('t'))]
    cta = _dic(d.get('cta'))
    links = ''.join('<li><a href="%s">%s</a></li>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav[:7])
    cta_h = '<a class="hd-cta" href="%s">%s</a>' % (e(cta.get('h') or '#'), e(cta['t'])) if _t(cta.get('t')) else ''
    big = ''.join('<li><a href="%s">%s</a></li>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav)
    if _t(cta.get('t')) and not any(_t(n.get('t')).lower() == cta['t'].lower() for n in nav):
        big += '<li><a href="%s">%s</a></li>' % (e(cta.get('h') or '#'), e(cta['t']))
    burger = ('<a class="burger" href="#foot" aria-label="%s" aria-expanded="false" aria-controls="menu" role="button">'
              '<span></span><span></span></a>' % e(ui.get('menu', 'Menu'))) if big else ''
    long_cls = ' long' if len(name) > 22 else ''
    head = ('<header class="hd" id="hd"><a class="brand%s" href="%s">%s</a>'
            '<nav class="hd-nav" aria-label="%s"><ul>%s</ul>%s</nav>%s</header>') % (
        long_cls, e(brand.get('home') or '#top'), e(name), e(ui.get('menu', 'Menu')), links, cta_h, burger)
    menu = ('<div class="menu" id="menu" aria-hidden="true"><ul>%s</ul></div>' % big) if big else ''
    return head + menu


def _hero(d, pool):
    h = _dic(d.get('hero'))
    title = _t(h.get('title')) or _t(_dic(d.get('brand')).get('name'))
    pic = pool.take(['room', 'people', 'work', 'workshop', 'action', 'exterior', 'landscape', 'dish', 'bar', 'product', 'detail', 'other'],
                    1400, 600, 1.2)
    style = ''
    bg = ''
    if pic:
        # a shallow picture is not blown up to fill a tall window: the first screen is at most 1.1 times the picture's height
        style = ' style="--hmax:%dpx"' % max(600, round(pic['h'] * 1.1))
        bg = '<div class="hero-bg">%s</div><div class="hero-veil"></div>' % _img(pic, 'ph', eager=True)
    size = ' h1-s' if len(title) > 56 else ''
    btns = _btn(h.get('primary'), 'on-dark') + _btn(h.get('secondary'), 'on-dark')
    text = _t(h.get('text'))
    note = _t(h.get('note'))
    right = ''
    if btns:
        right += '<div class="btns">%s</div>' % btns
    if text:
        right += '<p>%s</p>' % e(text)
    if note:
        m = re.sub(r'[^\d+]', '', note)
        right += ('<p class="note"><a href="tel:%s">%s</a></p>' % (m, e(note))) if len(m) >= 7 and len(m) >= len(note) * .6 else '<p class="note">%s</p>' % e(note)
    return ('<section class="hero%s" id="top"%s>%s<div class="hero-cap"><div class="l"><h1 class="%s">%s</h1></div>'
            '%s</div></section>') % ('' if pic else ' plain', style, bg, size.strip(), e(title),
                                     '<div class="r">%s</div>' % right if right else '')


def _why(d, pool):
    s = _dic(d.get('steps'))
    items = [i for i in _lst(s.get('items')) if isinstance(i, dict) and (_t(i.get('title')) or _t(i.get('text')))]
    if not items and not _t(s.get('title')):
        return ''
    head = _head(s.get('title'), s.get('text'))
    if not items:
        return '<section class="pad why">%s</section>' % ('<div class="wrap">%s</div>' % head)
    pics, taken = [], []
    for it in items:
        p = pool.own(it.get('img'))
        if p is None:
            p = pool.take(ANY, 450, 560)
            taken.append(p)
        pics.append(p)
    if not all(pics):
        pool.give_back(taken)
        pics = None
    n = len(items)
    if pics:
        below = any(len(_t(i.get('text'))) > CARD_TEXT_MAX for i in items)
        cols = n if n <= 4 else 3
        longest = _longest_word([_t(i.get('title')) for i in items])
        small = ' t-s' if (cols == 4 or longest > 13) else ''
        out = []
        for k, (it, p) in enumerate(zip(items, pics)):
            cta = _dic(it.get('cta'))
            link = ('<a class="more" href="%s"><span>%s</span>%s</a>' % (e(cta.get('h') or '#'), e(cta['t']), ARROW)) if _t(cta.get('t')) else ''
            txt = _t(it.get('text'))
            cap_txt = '<p>%s</p>' % e(txt) if txt and not below else ''
            under = '<div class="under">%s%s</div>' % ('<p>%s</p>' % e(txt) if txt else '', link) if below and (txt or link) else ''
            out.append('<div class="card"><figure>%s<figcaption><span class="no" aria-hidden="true">%02d</span><div class="cap">'
                       '<h3>%s</h3>%s%s</div></figcaption></figure>%s</div>' % (
                           _img(p, 'ph', '(max-width:1024px) 80vw, 33vw'), k + 1, e(_t(it.get('title'))), cap_txt, '' if below else link, under))
        body = '<div class="cards c%d%s" data-row>%s</div>' % (cols, small, ''.join(out))
    else:
        # the reference's values grid (about page): ruled cells, a bold name and a sentence
        cells = ''.join('<div class="cell"><h3>%s</h3>%s%s</div>' % (
            e(_t(i.get('title'))), '<p>%s</p>' % e(_t(i.get('text'))) if _t(i.get('text')) else '',
            ('<a class="more" href="%s"><span>%s</span>%s</a>' % (e(_dic(i.get('cta')).get('h') or '#'), e(_dic(i.get('cta'))['t']), ARROW)) if _t(_dic(i.get('cta')).get('t')) else '')
            for i in items)
        body = '<div class="cells%s">%s</div>' % (' one' if n == 1 else '', cells)
    return '<section class="pad why"><div class="wrap">%s%s</div></section>' % (head, body)


def _numbers(d, pool):
    st = _dic(d.get('statement'))
    figs = [f for f in _lst(d.get('figures')) if isinstance(f, dict) and _t(str(f.get('v') or ''))]
    title, text = _t(st.get('title')), _t(st.get('text'))
    if not figs and not title and not text:
        return ''
    pic = pool.take(['room', 'work', 'workshop', 'action', 'people', 'detail', 'landscape', 'exterior', 'product', 'other'], 1000, 600)
    if text and len(text) <= SAY_MAX:
        say, para, lab = text, '', title
    else:
        say, para, lab = title, text, ''
    wide = any(len(_t(f.get('l'))) > 30 for f in figs)

    def fig(f, cls):
        v = _t(str(f.get('v')))
        cnt = ' data-n' if re.fullmatch(r'\d{1,3}[+%]?', v) else ''
        return '<div class="%s rv"><span class="v"%s>%s</span><small>%s</small></div>' % (cls, cnt, e(v), e(_t(f.get('l'))))
    if pic:
        # the reference boxes this picture beside the numbers; here it is a full half, edge to edge and as tall as the band
        nums = '<div class="nlist">%s</div>' % ''.join(fig(f, 'n') for f in figs) if figs else ''
        return ('<section class="nums half"><div class="half-t">%s%s%s%s</div><figure class="half-p">%s</figure></section>' % (
            '<h2 class="lab">%s</h2>' % e(lab) if lab else '',
            ('<p class="say">%s</p>' % e(say)) if lab else ('<h2 class="say">%s</h2>' % e(say) if say else ''),
            '<div class="txt">%s</div>' % _paras(para) if para else '', nums, _img(pic, 'ph-l', '(max-width:1024px) 100vw, 50vw')))
    nums = '<div class="ngrid g%d%s">%s</div>' % (min(len(figs), 4), ' wide' if wide else '', ''.join(fig(f, 'n') for f in figs)) if figs else ''
    return ('<section class="pad nums"><div class="wrap firm">%s<div class="firm-r">%s%s%s</div></div></section>' % (
        '<h2 class="lab">%s</h2>' % e(lab) if lab else '<span class="lab"></span>',
        ('<p class="say">%s</p>' % e(say)) if lab else ('<h2 class="say">%s</h2>' % e(say) if say else ''),
        '<div class="txt">%s</div>' % _paras(para) if para else '', nums))


def _slug(s, k):
    return 'i%d-%s' % (k, re.sub(r'[^a-z0-9]+', '-', _t(s).lower()).strip('-')[:40])


def _carousel(d, ui):
    f = _dic(d.get('features'))
    items = [i for i in _lst(f.get('items')) if isinstance(i, dict) and _t(i.get('t'))]
    cat = _dic(d.get('catalogue'))
    cat_names = {}
    k = 0
    for g in _lst(cat.get('groups')):
        for it in _lst(_dic(g).get('items')):
            k += 1
            if _t(_dic(it).get('text')):
                cat_names.setdefault(_t(it.get('name')).lower(), _slug(it.get('name'), k))
    title, text = _t(f.get('title')), _t(f.get('text'))
    if not items:
        return ''
    if text and len(text) <= 60:
        left = ('<h2 class="lab">%s</h2>' % e(title) if title else '') + '<p class="disp">%s</p>' % e(text)
    else:
        left = ('<h2 class="disp">%s</h2>' % e(title) if title else '') + ('<div class="txt">%s</div>' % _paras(text) if text else '')
    longest = _longest_word([i['t'] for i in items])
    fs = 40 if longest <= 10 else max(26, min(40, int(216 / (longest * .6))))
    slides, any_text = [], False
    for it in items:
        txt = _t(it.get('d'))
        href = _t(it.get('h'))
        anchor = cat_names.get(it['t'].lower())
        if anchor and len(txt) > SLIDE_TEXT_MAX:
            txt, href = '', '#' + anchor                      # the whole text stands in the list below; the column points at it
        elif anchor and not href:
            href = '#' + anchor
        any_text = any_text or bool(txt)
        inner = '<h3>%s</h3><div class="cap">%s%s</div>' % (e(it['t']), '<p>%s</p>' % e(txt) if txt else '', ARROW_BIG.replace('<svg', '<svg class="arw"') if href else '')
        slides.append('<a class="slide" href="%s">%s</a>' % (e(href), inner) if href else '<div class="slide">%s</div>' % inner)
    ctrl = ('<div class="ctrl"><button class="prev" type="button" aria-label="%s" disabled>%s</button>'
            '<button class="next" type="button" aria-label="%s">%s</button></div>') % (
        e(ui.get('prev', 'Back')), ARROW_BIG, e(ui.get('next', 'Next')), ARROW_BIG)
    return ('<section class="car%s" style="--h4:%dpx"><div class="car-top"><div class="car-l">%s</div>'
            '<div class="car-r" tabindex="0" role="group"%s>%s</div></div>%s</section>') % (
        '' if any_text else ' short', fs, left, ' aria-label="%s"' % e(title) if title else '', ''.join(slides), ctrl)


def _price_rows(items):
    out = []
    for it in items:
        name, price, note, text = _t(it.get('name')), _t(it.get('price')), _t(it.get('note')), _t(it.get('text'))
        state = _t(it.get('state'))
        left = '<span class="nm">%s%s</span>' % (e(name), ' <em>%s</em>' % e(state) if state else '') + ('<span class="nt">%s</span>' % e(note) if note else '')
        right = '<span class="pr">%s</span>' % e(price) if price else ''
        more = ''
        for pr in _lst(it.get('prices')):
            pr = _dic(pr)
            if _t(pr.get('price')):
                more += '<div class="sub"><span>%s</span><span class="pr">%s</span></div>' % (e(_t(pr.get('label'))), e(pr['price']))
        if text:
            more += '<p>%s</p>' % e(text)
        rows = [r for r in _lst(it.get('rows')) if _t(r)]
        if rows:
            more += '<ul class="inc">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in rows)
        href = _t(it.get('h'))
        nm = '<a class="row" href="%s">' % e(href) if href and not price else '<div class="row">'
        out.append('<li>%s<span class="lft">%s</span>%s%s%s</li>' % (nm, left, right or (ARROW if href else ''), '</a>' if href and not price else '</div>', more))
    return '<ul class="rows">%s</ul>' % ''.join(out)


def _catalogue(d, pool):
    c = _dic(d.get('catalogue'))
    groups = [g for g in _lst(c.get('groups')) if isinstance(g, dict) and _lst(g.get('items'))]
    if not groups:
        return ''
    n_items = sum(len(g['items']) for g in groups)
    band = pool.take(['detail', 'product', 'work', 'workshop', 'room', 'dish', 'landscape', 'other'], 1400, 400, 1.8) if (len(groups) > 1 and n_items >= 8) else None
    parts, k = [], 0
    mid = (len(groups) + 1) // 2
    for gi, g in enumerate(groups):
        items = [i for i in g['items'] if isinstance(i, dict) and _t(i.get('name'))]
        priced = any(_t(i.get('price')) or _lst(i.get('prices')) for i in items)
        texts = any(_t(i.get('text')) for i in items)
        gh = ('<h3>%s</h3>' % e(_t(g.get('t'))) if _t(g.get('t')) else '') + ('<p class="gt">%s</p>' % e(_t(g.get('text'))) if _t(g.get('text')) else '')
        if priced or not texts:
            k += len(items)
            body = _price_rows(items)
        else:
            # the reference's practice-area page: a barred sub-head and its paragraph
            blocks = []
            for it in items:
                k += 1
                href = _t(it.get('h'))
                blocks.append('<div class="blk" id="%s"><h4>%s</h4>%s%s</div>' % (
                    _slug(it.get('name'), k), e(it['name']), _paras(it.get('text')),
                    ''))
            body = '<div class="blks">%s</div>' % ''.join(blocks)
        gl = _t(g.get('h'))
        parts.append('<div class="grp">%s%s</div>' % (gh, body))
        if band and gi + 1 == mid:
            parts.append('</div></div><figure class="band">%s</figure><div class="wrap list"><span class="lab"></span><div class="list-r">' % _img(band, 'ph-l'))
    note = '<p class="cnote">%s</p>' % e(_t(c.get('note'))) if _t(c.get('note')) else ''
    left = ('<h2 class="lab">%s</h2>' % e(_t(c.get('title'))) if _t(c.get('title')) else '<span class="lab"></span>')
    intro = '<div class="txt intro">%s</div>' % _paras(c.get('text')) if _t(c.get('text')) else ''
    return '<section class="alt cat" id="catalogue"><div class="wrap list">%s<div class="list-r">%s%s%s</div></div></section>' % (left, intro, ''.join(parts), note)


def _plans(d):
    p = _dic(d.get('plans'))
    items = [i for i in _lst(p.get('items')) if isinstance(i, dict) and (_t(i.get('name')) or _t(i.get('price')))]
    if not items:
        return ''
    n = len(items)
    cols = n if n <= 4 else 3
    out = []
    for it in items:
        rows = [r for r in _lst(it.get('rows')) if _t(r)]
        cta = _dic(it.get('cta'))
        out.append('<div class="plan%s"><div><h3>%s</h3>%s%s%s</div>%s</div>' % (
            ' marked' if it.get('marked') else '', e(_t(it.get('name'))),
            '<p class="price"><span class="v">%s</span>%s</p>' % (e(_t(it.get('price'))), ' <small>%s</small>' % e(_t(it.get('per'))) if _t(it.get('per')) else '') if _t(it.get('price')) else '',
            '<p class="line">%s</p>' % e(_t(it.get('line'))) if _t(it.get('line')) else '',
            '<ul class="inc">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in rows) if rows else '',
            _btn(cta, 'solid' if it.get('marked') else '') ))
    note = '<p class="cnote wrap">%s</p>' % e(_t(p.get('note'))) if _t(p.get('note')) else ''
    head = _head(p.get('title'), p.get('text'))
    return '<section class="plans" id="plans">%s<div class="pgrid p%d">%s</div>%s</section>' % (
        '<div class="wrap pad-t">%s</div>' % head if head else '', cols, ''.join(out), note)


def _faq(d):
    f = _dic(d.get('faq'))
    items = [i for i in _lst(f.get('items')) if isinstance(i, dict) and _t(i.get('q'))]
    if not items:
        return ''
    left = '<h2 class="lab">%s</h2>' % e(_t(f.get('title'))) if _t(f.get('title')) else '<span class="lab"></span>'
    body = ''.join('<div class="qa"><h3>%s</h3>%s</div>' % (e(i['q']), _paras(i.get('a'))) for i in items)
    return '<section class="alt cat faq" id="faq"><div class="wrap list">%s<div class="list-r">%s</div></div></section>' % (left, body)


def _contact_bits(p, sep=' · '):
    out = []
    ph, em = p.get('phone'), _t(p.get('email'))
    if isinstance(ph, dict):
        ph = _t(ph.get('t'))
    ph = _t(ph)
    if ph:
        out.append('<a href="tel:%s">%s</a>' % (re.sub(r'[^\d+]', '', ph), e(ph)))
    if em:
        out.append('<a href="mailto:%s">%s</a>' % (e(em), e(em)))
    return sep.join(out)


def _team(d, pool):
    t = _dic(d.get('team'))
    groups = [(_t(_dic(g).get('t')), [i for i in _lst(_dic(g).get('items')) if isinstance(i, dict) and _t(i.get('name'))]) for g in _lst(t.get('groups'))]
    if _lst(t.get('items')):
        groups = [('', [i for i in t['items'] if isinstance(i, dict) and _t(i.get('name'))])] + groups
    groups = [g for g in groups if g[1]]
    if not groups:
        return ''
    head = _head(t.get('title'), t.get('text'))
    band = pool.take(['people'], 1100, 360, 1.6)
    body = '<figure class="band tb">%s</figure>' % _img(band, 'ph-l') if band else ''
    for gt, items in groups:
        with_p = [(i, pool.by_src.get(_t(i.get('img'))) or ({'src': i['img'], 'w': 0, 'h': 0} if _t(i.get('img')) else None)) for i in items]
        cards = [(i, p) for i, p in with_p if p]
        plain = [i for i, p in with_p if not p]
        if gt:
            body += '<div class="wrap"><h3 class="gt-h">%s</h3></div>' % e(gt)
        if cards:
            square = any((p.get('h') or 9999) < 640 for _, p in cards)
            n = len(cards)
            cols = 3 if n <= 3 else 4
            out = []
            for i, p in cards:
                pp = dict(p, alt=_t(i.get('name')))
                bits = _contact_bits(i, '<br>')
                under = ('<p>%s</p>' % e(_t(i.get('text'))) if _t(i.get('text')) else '') + ('<p class="ct">%s</p>' % bits if bits else '')
                out.append('<div class="card"><figure>%s<figcaption><div class="cap"><h4>%s</h4>%s</div></figcaption></figure>%s</div>' % (
                    _img(pp, 'ph-p', '(max-width:1024px) 80vw, 25vw'), e(i['name']),
                    '<p class="role">%s</p>' % e(_t(i.get('role'))) if _t(i.get('role')) else '',
                    '<div class="under">%s</div>' % under if under else ''))
            body += '<div class="wrap"><div class="cards people c%d%s%s" data-row>%s</div></div>' % (cols, ' sq' if square else '', ' t-s' if cols == 4 else '', ''.join(out))
        if plain:
            lis = []
            for i in plain:
                bits = _contact_bits(i)
                lis.append('<li><div class="row"><span class="lft"><span class="nm">%s</span>%s</span></div>%s%s</li>' % (
                    e(i['name']), '<span class="nt">%s</span>' % e(_t(i.get('role'))) if _t(i.get('role')) else '',
                    '<p>%s</p>' % e(_t(i.get('text'))) if _t(i.get('text')) else '', '<p class="ct">%s</p>' % bits if bits else ''))
            body += '<div class="wrap"><ul class="rows ppl">%s</ul></div>' % ''.join(lis)
    return '<section class="pad team" id="team">%s%s</section>' % ('<div class="wrap">%s</div>' % head if head else '', body)


def _quotes(d):
    qs = [q for q in _lst(d.get('quotes')) if isinstance(q, dict) and _t(q.get('q'))]
    if not qs:
        return ''
    out = ''.join('<figure class="q"><blockquote>%s<p>%s</p></blockquote>%s</figure>' % (
        '<strong>%s</strong>' % e(_t(q.get('title'))) if _t(q.get('title')) else '', e(q['q']),
        '<figcaption>%s%s</figcaption>' % ('<span class="nm">%s</span>' % e(_t(q.get('name'))) if _t(q.get('name')) else '',
                                           '<span class="nt">%s</span>' % e(_t(q.get('role'))) if _t(q.get('role')) else '') if (_t(q.get('name')) or _t(q.get('role'))) else '')
        for q in qs)
    return '<section class="quotes"><div class="qgrid q%d">%s</div></section>' % (min(len(qs), 3), out)


def _addr(a):
    a = _dic(a)
    l1 = _t(a.get('street'))
    l2 = ' '.join(x for x in [_t(a.get('postcode')), _t(a.get('city'))] if x)
    l3 = ', '.join(x for x in [_t(a.get('region')), _t(a.get('country'))] if x)
    return [x for x in [l1, l2, l3] if x]


def _hours(hs):
    out = []
    for h in _lst(hs):
        h = _dic(h)
        if _t(h.get('days')):
            span = ' – '.join(x for x in [_t(h.get('open')), _t(h.get('close'))] if x)
            out.append('<span>%s</span><span>%s</span>' % (e(h['days']), e(span)))
    return '<span class="hrs">%s</span>' % ''.join(out) if out else ''


def _reach(d, pool, ui):
    place, contact = _dic(d.get('place')), _dic(d.get('contact'))
    locs = [l for l in _lst(d.get('locations')) if isinstance(l, dict)]
    phone = _dic(contact.get('phone')) or _dic(place.get('phone'))
    email = _t(contact.get('email')) or _t(place.get('email'))
    items = []
    if locs:
        for l in locs:
            lines = ''.join('<span>%s</span>' % e(x) for x in _addr(l.get('address')))
            bits = _contact_bits(l, '</span><span>')
            hrs = _hours(l.get('hours'))
            nm = _t(l.get('name'))
            nm_h = ('<a href="%s">%s</a>' % (e(l['h']), e(nm)) if _t(l.get('h')) else e(nm)) if nm else ''
            items.append('<div class="it">%s%s%s%s%s</div>' % (
                '<strong>%s</strong>' % nm_h if nm_h else '', lines, '<span>%s</span>' % bits if bits else '', hrs,
                '<span class="nt">%s</span>' % e(_t(l.get('note'))) if _t(l.get('note')) else ''))
    else:
        lines = ''.join('<span>%s</span>' % e(x) for x in _addr(place.get('address')))
        if lines:
            items.append('<div class="it">%s%s</div>' % ('<strong>%s</strong>' % e(ui['address']) if ui.get('address') else '', lines))
        hrs = _hours(place.get('hours'))
        if hrs:
            items.append('<div class="it">%s%s</div>' % ('<strong>%s</strong>' % e(ui['hours']) if ui.get('hours') else '', hrs))
    for r in _lst(contact.get('routes')):
        r = _dic(r)
        if _t(r.get('t')):
            t = '<a href="%s">%s</a>' % (e(r['h']), e(r['t'])) if _t(r.get('h')) else e(r['t'])
            items.append('<div class="it"><strong>%s</strong>%s</div>' % (t, '<span>%s</span>' % e(_t(r.get('note'))) if _t(r.get('note')) else ''))
    social = [s for s in _lst(place.get('social')) if _t(_dic(s).get('t')) and _t(_dic(s).get('h'))]
    lead = ''
    if _t(phone.get('t')):
        lead += '<p class="tel"><a href="%s">%s</a></p>' % (e(phone.get('h') or 'tel:' + re.sub(r'[^\d+]', '', phone['t'])), e(phone['t']))
        if _t(phone.get('note')):
            lead += '<p class="tel-n">%s</p>' % e(phone['note'])
    if email:
        lead += '<p class="mail"><a href="mailto:%s">%s</a></p>' % (e(email), e(email))
    form, booking = _dic(contact.get('form')), _dic(place.get('booking'))
    btns = _btn(booking, '') + (_btn(form, '') if _t(form.get('h')) != _t(booking.get('h')) or not _t(booking.get('t')) else '')
    if btns:
        lead += '<div class="btns">%s</div>' % btns
    if social:
        lead += '<p class="soc">%s</p>' % ''.join('<a href="%s">%s</a>' % (e(s['h']), e(s['t'])) for s in social)
    if not lead and not items:
        return ''
    pic = pool.take(['exterior', 'landscape'], 1000, 600)
    its = '<div class="its n%d">%s</div>' % (min(len(items), 3), ''.join(items)) if items else ''
    if pic:
        return '<section class="alt reach half rev" id="contact"><figure class="half-p">%s</figure><div class="half-t"><div class="lead">%s</div>%s</div></section>' % (
            _img(pic, 'ph-l', '(max-width:1024px) 100vw, 50vw'), lead, its)
    return '<section class="alt reach pad" id="contact"><div class="wrap two"><div class="lead">%s</div>%s</div></section>' % (lead, its)


def _close(d, pool):
    c = _dic(d.get('close'))
    title, text, cta = _t(c.get('title')), _t(c.get('text')), _dic(c.get('cta'))
    if not title and not text:
        return ''
    pic = pool.take(['exterior', 'landscape', 'room', 'detail', 'work', 'workshop', 'action', 'people', 'other'], 1400, 600, 1.3)
    bg = '%s<div class="ban-veil"></div>' % _img(pic, 'ph') if pic else ''
    return ('<section class="ban%s">%s<div class="ban-cap">%s<div class="r">%s%s</div></div></section>' % (
        '' if pic else ' plain', bg, '<h2>%s</h2>' % e(title) if title else '<span></span>',
        '<div class="txt">%s</div>' % _paras(text) if text else '<span></span>', _btn(cta, 'solid')))


def _foot(d, ui):
    brand, foot, hero = _dic(d.get('brand')), _dic(d.get('foot')), _dic(d.get('hero'))
    name = _t(brand.get('name'))
    logo = _t(brand.get('logo'))
    mark = '<img class="logo" src="%s" alt="%s" loading="lazy">' % (e(_src(logo)), e(name)) if logo else '<span class="wm">%s</span>' % e(name)
    links = [l for l in _lst(d.get('links')) if _t(_dic(l).get('t'))] or [n for n in _lst(d.get('nav')) if _t(_dic(n).get('t'))]
    half = (len(links) + 1) // 2
    cols = ''.join('<ul>%s</ul>' % ''.join('<li><a href="%s">%s</a></li>' % (e(l.get('h') or '#'), e(l['t'])) for l in part)
                   for part in (links[:half], links[half:]) if part)
    creds = [c for c in _lst(d.get('credentials')) if isinstance(c, dict) and (_t(c.get('t')) or _t(c.get('img')))]
    badges = ''.join(('<a href="%s">%s</a>' if _t(c.get('h')) else '%.0s%s') % (e(_t(c.get('h'))), '<img src="%s" alt="%s" loading="lazy">' % (
        e(_src(c['img'])), e(' — '.join(x for x in [_t(c.get('t')), _t(c.get('text'))] if x)))) for c in creds if _t(c.get('img')))
    words = ''.join('<li><strong>%s</strong>%s</li>' % (
        ('<a href="%s">%s</a>' % (e(c['h']), e(_t(c.get('t')))) if _t(c.get('h')) else e(_t(c.get('t')))),
        ' %s' % e(_t(c.get('text'))) if _t(c.get('text')) else '') for c in creds if not _t(c.get('img')) and _t(c.get('t')))
    tag = _t(hero.get('title'))
    fl = ''.join('<li><a href="%s">%s</a></li>' % (e(l.get('h') or '#'), e(l['t'])) for l in _lst(foot.get('links')) if _t(_dic(l).get('t')))
    bottom = ''
    if fl or _t(foot.get('legal')):
        bottom = '<div class="wrap"><div class="bot">%s%s</div></div>' % ('<ul>%s</ul>' % fl if fl else '', '<p class="legal">%s</p>' % e(_t(foot.get('legal'))) if _t(foot.get('legal')) else '')
    return ('<footer class="ft" id="foot"><div class="wrap ft-m"><div class="l"><div class="mark">%s</div>%s%s</div>'
            '<div class="r"><a class="totop" href="#top" aria-label="%s">%s</a>%s%s</div></div>%s%s</footer>') % (
        mark, '<p class="tag">%s</p>' % e(tag) if tag else '', '<p class="nap">%s</p>' % e(_t(foot.get('text'))) if _t(foot.get('text')) else '',
        e(ui.get('top', '↑')), ARROW_UP, '<nav aria-label="%s">%s</nav>' % (e(name), cols) if cols else '',
        '<div class="badges">%s</div>' % badges if badges else '',
        '<div class="wrap"><ul class="creds">%s</ul></div>' % words if words else '', bottom)


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--g);color:var(--k);font:400 18px/1.4 Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
h1,h2,h3,h4,p,ul,figure,blockquote{margin:0;padding:0}
ul{list-style:none}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
.hd :focus-visible,.menu :focus-visible,.hero :focus-visible,.nums :focus-visible,.ban :focus-visible,.card figure :focus-visible{outline-color:var(--on)}
.skip{position:absolute;left:-999px;top:0;background:var(--g);color:var(--k);padding:12px 20px;z-index:99}
.skip:focus{left:0}
.wrap{padding:0 20px}
.pad{padding:100px 0}
.alt{background:var(--alt)}
.serif,.lab,.say,.disp,h1{font-family:Newsreader,Georgia,serif}
.lab{display:block;font-weight:500;font-size:24px;line-height:1.3;letter-spacing:-.02em;text-transform:uppercase}
.say{font-weight:500;font-size:40px;line-height:48px;text-wrap:pretty}
.txt p{font-size:18px;line-height:25.2px;letter-spacing:-.02em;max-width:760px}
.txt p+p{margin-top:14px}
.ph{filter:grayscale(1) contrast(1.06) brightness(.8)}
.ph-l{filter:grayscale(1)}
.ph-p{filter:grayscale(1) brightness(.92)}
.arw{flex:none;transition:transform .4s ease}
.btn{display:inline-flex;align-items:center;gap:10px;min-height:60px;padding:8px 40px;border:1px solid var(--rule);font-weight:500;font-size:20px;line-height:1.2;color:var(--k);transition:background-color .4s ease,color .4s ease,border-color .4s ease;max-width:100%}
.btn:hover{background:var(--deep);color:var(--on);border-color:var(--deep)}
.btn.on-dark{border-color:var(--on);color:var(--on)}
.btn.on-dark:hover{background:var(--deep);border-color:var(--deep)}
.btn.solid{background:var(--a);color:var(--on-a);border-color:var(--a)}
.btn.solid:hover{background:var(--deep);color:var(--on);border-color:var(--on)}
.btns{display:flex;flex-wrap:wrap;gap:12px}

/* header: 130 high, clear over the first screen, the band colour once the page has moved; leaves going down, returns going up */
.hd{position:fixed;z-index:30;left:0;right:0;top:0;height:130px;padding:20px;display:flex;align-items:center;justify-content:space-between;gap:30px;color:var(--on);transition:transform .4s ease,background-color .4s ease}
.hd.scrolled{background:var(--deep)}
.hd.away{transform:translateY(-100%)}
.brand{font:500 28px/1.1 Newsreader,Georgia,serif;letter-spacing:.01em;max-width:420px;text-wrap:balance}
.brand.long{font-size:22px;max-width:300px}
.hd-nav{display:flex;align-items:center;gap:30px;flex:none}
.hd-nav ul{display:flex;gap:30px}
.hd-nav ul a{display:flex;align-items:center;height:60px;font-size:18px;text-transform:uppercase;white-space:nowrap;transition:opacity .4s ease}
.hd-nav ul a:hover{opacity:.6}
.hd-cta{display:flex;align-items:center;min-height:40px;padding:5px 13px;border:1px solid var(--on);border-radius:2px;font-weight:600;font-size:16px;letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;transition:background-color .4s ease,color .4s ease}
.hd-cta:hover{background:var(--on);color:var(--deep)}
.burger{display:none;position:relative;width:40px;height:40px;flex:none}
.burger span{position:absolute;left:0;top:10px;width:40px;height:2px;background:currentColor;transition:transform .3s ease}
.burger span+span{top:30px}
.burger[aria-expanded=true] span{transform:translateY(10px) rotate(45deg)}
.burger[aria-expanded=true] span+span{transform:translateY(-10px) rotate(-45deg)}
.menu{position:fixed;z-index:25;inset:0;background:var(--deep);color:var(--on);padding:140px 80px 80px 100px;overflow:auto;transform:translateY(-100%);visibility:hidden;transition:transform .8s cubic-bezier(.7,0,.2,1),visibility 0s .8s}
.menu.open{transform:none;visibility:visible;transition:transform .8s cubic-bezier(.7,0,.2,1)}
.menu li{overflow:hidden;padding-top:2px}
.menu a{display:inline-block;font-size:50px;line-height:70px;text-transform:uppercase;transform:translateY(110%);opacity:0;transition:transform .6s ease,opacity .6s ease}
.menu.open a{transform:none;opacity:1}
.menu.open li:nth-child(2) a{transition-delay:.08s}.menu.open li:nth-child(3) a{transition-delay:.16s}.menu.open li:nth-child(4) a{transition-delay:.24s}
.menu.open li:nth-child(5) a{transition-delay:.32s}.menu.open li:nth-child(6) a{transition-delay:.4s}.menu.open li:nth-child(n+7) a{transition-delay:.48s}

/* first screen: the picture fills the window; 70px heading at the foot left, button and 18px text from x=820 */
.hero{position:relative;height:100vh;height:min(100svh,var(--hmax,2000px));min-height:600px;overflow:hidden;background:var(--deep);color:var(--on)}
.hero-bg,.hero-veil{position:absolute;inset:0}
.hero-bg img{width:100%;height:100%;object-fit:cover}
.hero-veil{background:linear-gradient(to bottom,color-mix(in srgb,var(--shade) 66%,transparent) 0,color-mix(in srgb,var(--shade) 40%,transparent) 28%,color-mix(in srgb,var(--shade) 46%,transparent) 42%,color-mix(in srgb,var(--shade) 80%,transparent) 68%,color-mix(in srgb,var(--shade) 88%,transparent) 100%)}
.hero-cap{position:absolute;left:20px;right:20px;bottom:80px;display:flex;justify-content:space-between;align-items:flex-end;gap:40px}
.hero .l{flex:0 1 700px;padding-bottom:100px;min-width:0}
h1{font-weight:400;font-size:70px;line-height:77px;text-wrap:balance;overflow-wrap:break-word}
h1.h1-s{font-size:54px;line-height:60px}
.hero .r{flex:0 0 600px;max-width:42%;display:flex;flex-direction:column;gap:40px}
.hero .r p{font-size:18px;line-height:25.2px;letter-spacing:-.02em}
.hero .r .note{font-size:20px;font-weight:500;margin-top:-20px}

/* head of a section: label at the left, statement from x=420 */
.head{display:flex;gap:40px;justify-content:space-between}
.head .lab{flex:1 1 0;min-width:0}
.head-r{flex:0 0 71.43%;min-width:0}

/* picture cards: three across, 453x635, number top right, capital serif title and 16px text on the dark foot */
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;padding-top:40px}
.cards.c1{grid-template-columns:minmax(0,1fr)}.cards.c2{grid-template-columns:repeat(2,minmax(0,1fr))}.cards.c4{grid-template-columns:repeat(4,minmax(0,1fr))}
.card{display:flex;flex-direction:column;gap:20px;min-width:0}
.card figure{position:relative;overflow:hidden;background:var(--deep);color:#fff;aspect-ratio:453/635;display:grid}
.cards.c1 .card figure{aspect-ratio:1400/635}.cards.c2 .card figure{aspect-ratio:690/635}
.card figure>img{grid-area:1/1;width:100%;height:100%;min-height:0;object-fit:cover;position:absolute;inset:0}
.card figcaption{grid-area:1/1;position:relative;display:flex;flex-direction:column;justify-content:space-between;min-width:0;background:radial-gradient(ellipse 300px 220px at 100% 0,color-mix(in srgb,var(--shade) 68%,transparent) 0,color-mix(in srgb,var(--shade) 66%,transparent) 72%,transparent 100%)}
.card .no{align-self:flex-end;padding:40px 40px 0;font-weight:700;font-size:60px;line-height:72px;color:rgba(255,255,255,.72)}
.card .cap{display:flex;flex-direction:column;gap:20px;padding:110px 40px 40px;background:linear-gradient(to top,color-mix(in srgb,var(--shade) 94%,transparent) 0,color-mix(in srgb,var(--shade) 90%,transparent) calc(100% - 110px),transparent 100%)}
.card h3,.card h4{font:400 30px/40px Newsreader,Georgia,serif;letter-spacing:-.007em;text-transform:uppercase;overflow-wrap:anywhere;hyphens:auto}
.cards.t-s h3,.cards.t-s h4{font-size:24px;line-height:31px}
.cards.t-s .no{padding:30px 30px 0}.cards.t-s .cap{padding:110px 30px 30px}
.card .cap p{font-size:16px;line-height:22.4px;letter-spacing:-.0125em}
.more{display:inline-flex;align-items:center;gap:10px;font-weight:500;font-size:16px}
.more:hover .arw,.btn:hover .arw,.slide:hover .arw{transform:translateX(4px)}
.card .under{display:flex;flex-direction:column;gap:16px;align-items:flex-start}
.card .under p{font-size:16px;line-height:22.4px;letter-spacing:-.0125em}
.people .card figure{aspect-ratio:453/635}
.people.sq .card figure{aspect-ratio:1/1}
.people figcaption{justify-content:flex-end;background:none}
.people .cap{gap:8px;padding-top:90px}
.people .under{gap:8px}
.people .under .ct{overflow-wrap:anywhere}
.people .under .ct a{text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}
.people .cap .role{font-weight:500}

/* values grid (the reference's about page): ruled cells, 20px bold name, 18px sentence */
.cells{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));margin-top:60px;border-top:1px solid var(--rule);border-left:1px solid var(--rule)}
.cells.one{grid-template-columns:minmax(0,1fr)}
.cell{display:flex;flex-direction:column;gap:40px;padding:60px 40px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);min-width:0}
.cell h3{font-weight:700;font-size:20px;line-height:1.2;color:var(--muted)}
.cell p{font-size:18px;line-height:1.35}

/* band of numbers on the deep colour */
.nums{background:var(--deep);color:var(--on)}
.firm{display:flex;gap:0}
.firm>.lab{flex:0 0 400px}
.firm-r{flex:1 1 0;min-width:0}
.firm-r .txt{margin-top:60px}.firm-r .txt p{max-width:1000px}
.ngrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));margin-top:44px;row-gap:44px}
.ngrid.g1{grid-template-columns:minmax(0,1fr)}.ngrid.g2{grid-template-columns:repeat(2,minmax(0,1fr))}.ngrid.g4{grid-template-columns:repeat(4,minmax(0,1fr))}
.ngrid .n{display:flex;flex-direction:column;border-left:1px solid var(--on);padding:0 20px;min-width:0}
.n .v{font-size:60px;line-height:72px;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.ngrid small{font-size:20px;line-height:1.2}
.half{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
.half.rev .half-t{padding:100px 20px 100px 80px}
.half-t{padding:100px 80px 100px 20px;min-width:0;display:flex;flex-direction:column;justify-content:center}
.half-t .lab{margin-bottom:40px}
.half-t .say{font-size:38px;line-height:45.6px}
.half-t .txt{margin-top:40px}
.half-p{position:relative;min-height:578px}
.half-p img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.nlist{margin-top:52px}
.nlist .n{display:flex;justify-content:space-between;gap:30px;border-top:1px solid color-mix(in srgb,var(--on) 50%,transparent);padding:20px 0 56px}
.nlist .n:last-child{padding-bottom:0}
.nlist .v{line-height:44px}
.nlist small{font-size:16px;line-height:1.3;text-align:right;max-width:55%;padding-top:10px}
.js .rv{opacity:0;transform:translateY(30px);transition:opacity .7s ease,transform .7s ease}
.js .rv.in{opacity:1;transform:none}

/* carousel: a 499 panel, then ruled columns 336 wide and 706 high; 60px control bar */
.car{border-bottom:1px solid var(--rule)}
.car-top{display:flex;border-bottom:1px solid var(--rule)}
.car-l{flex:0 0 34.65%;padding:80px 60px;border-right:1px solid var(--rule);min-width:0}
.car-l .lab{margin-bottom:80px}
.disp{font-weight:400;font-size:50px;line-height:55px;letter-spacing:-.08em;overflow-wrap:break-word;hyphens:auto}
.car-l .txt{margin-top:50px}
.car-r{flex:1 1 0;min-width:0;display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;overscroll-behavior-x:contain}
.car-r::-webkit-scrollbar{display:none}
.slide{flex:1 0 35.71%;min-height:706px;display:flex;flex-direction:column;justify-content:space-between;gap:60px;padding:100px 60px 60px;scroll-snap-align:start;transition:background-color .3s ease-in-out;min-width:0}
.car.short .slide{min-height:420px}
.slide+.slide{border-left:1px solid var(--rule)}
a.slide:hover{background:color-mix(in srgb,var(--k) 10%,transparent)}
.slide h3{font-weight:500;font-size:var(--h4,40px);line-height:1;hyphens:auto;overflow-wrap:anywhere}
.slide .cap{display:flex;flex-direction:column;gap:20px;align-items:flex-start}
.slide p{font-size:18px;line-height:21px}
.ctrl{display:none;height:60px}
.js .ctrl{display:flex;gap:10px}
.js .ctrl.none{display:none}
.ctrl button{width:60px;height:60px;display:flex;align-items:center;justify-content:center;background:none;border:0;color:inherit;cursor:pointer;padding:0;transition:opacity .3s ease}
.ctrl .prev{border-right:1px solid var(--rule)}
.ctrl .prev svg{transform:scaleX(-1)}
.ctrl button:disabled{opacity:.5;cursor:default}

/* lists (the reference's practice-areas page): nothing at the left but the label, 1000 at the right, ruled rows 81 high in two columns */
.cat{padding:100px 0}
.list{display:flex;gap:80px}
.list>.lab{flex:0 0 320px}
.list-r{flex:1 1 0;min-width:0}
.intro{margin-bottom:60px}
.grp+.grp{margin-top:80px}
.grp h3,.gt-h{font:400 30px/1.3 Newsreader,Georgia,serif;letter-spacing:-.007em;text-transform:uppercase}
.grp .gt{margin-top:14px;max-width:760px;font-size:18px;line-height:25.2px;color:var(--muted)}
.rows{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:60px;margin-top:20px}
.rows>li{border-bottom:1px solid var(--rule);padding:0 0 24px;min-width:0}
.rows .row{display:flex;justify-content:space-between;align-items:center;gap:24px;min-height:80px;padding:24px 0 0}
.rows .lft{display:flex;flex-direction:column;gap:4px;min-width:0}
.rows .nm{font-size:20px;line-height:1.25;letter-spacing:-.01em}
.rows .nm em{font-style:normal;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-left:8px}
.rows .nt,.q .nt{font-size:16px;line-height:1.35;color:var(--muted)}
.rows .pr{font-weight:500;font-size:20px;line-height:1.25;text-align:right;flex:0 1 auto;max-width:55%}
.rows li>p{font-size:16px;line-height:22.4px;margin-top:12px}
.rows .sub{display:flex;justify-content:space-between;gap:20px;font-size:16px;margin-top:8px}
.rows .ct a,.it a,.mail a,.soc a,.creds a,.bot a,.nap a{text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}
.inc{margin-top:14px}
.inc li{font-size:16px;line-height:22.4px;padding:10px 0;border-top:1px solid var(--rule)}
.blks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:50px 60px;margin-top:40px}
.blk{scroll-margin-top:150px;min-width:0}
.blk h4,.qa h3{font-weight:700;font-size:20px;line-height:1.25;border-left:2px solid var(--k);padding-left:12px;margin-bottom:14px;overflow-wrap:anywhere;hyphens:auto}
.blk p,.qa p{font-size:16px;line-height:22.4px}
.blk p+p,.qa p+p{margin-top:10px}
.qa{padding:36px 0;border-bottom:1px solid var(--rule);max-width:1000px}
.qa:first-child{padding-top:0}
.qa p{font-size:18px;line-height:25.2px}
.cnote{margin-top:50px;font-size:16px;color:var(--muted)}
.band{margin:80px 0;max-height:520px;overflow:hidden;display:flex}
.band img{width:100%;height:auto;max-height:520px;object-fit:cover}
.band.tb{margin:40px 0 0}

/* plans: the carousel's ruled columns, the numbers' 60px figure */
.pad-t{padding-top:100px;padding-bottom:60px}
.pgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.pgrid.p1{grid-template-columns:minmax(0,1fr)}.pgrid.p2{grid-template-columns:repeat(2,minmax(0,1fr))}.pgrid.p4{grid-template-columns:repeat(4,minmax(0,1fr))}
.plan{display:flex;flex-direction:column;justify-content:space-between;gap:50px;padding:80px 60px 60px;border-left:1px solid var(--rule);margin-left:-1px;min-width:0;box-shadow:0 1px 0 var(--rule)}
.pgrid.p4 .plan{padding:60px 30px 40px}
.plan.marked{background:color-mix(in srgb,var(--k) 10%,transparent)}
.plan h3{font-weight:500;font-size:40px;line-height:1;overflow-wrap:anywhere}
.plan .price{margin-top:40px}
.plan .price .v{font-size:60px;line-height:1;letter-spacing:-.02em}
.plan .price small{font-size:16px;display:block;margin-top:10px}
.plan .line{margin-top:24px;font-size:18px;line-height:1.3}
.plans .cnote{padding-bottom:60px}

.team .cards{padding-top:40px}
.gt-h{margin-top:60px}
.ppl{margin-top:40px}
.ppl .row{min-height:0}

/* quotations: ruled columns */
.qgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.qgrid.q1{grid-template-columns:minmax(0,1fr)}.qgrid.q2{grid-template-columns:repeat(2,minmax(0,1fr))}
.q{display:flex;flex-direction:column;justify-content:space-between;gap:60px;padding:80px 60px 60px;border-left:1px solid var(--rule);margin-left:-1px;min-width:0;box-shadow:0 1px 0 var(--rule)}
.q blockquote p{font:500 26px/1.3 Newsreader,Georgia,serif;text-wrap:pretty}
.q blockquote strong{display:block;font-weight:700;font-size:20px;margin-bottom:20px;color:var(--muted)}
.q figcaption{display:flex;flex-direction:column;gap:4px}
.q .nm{font-weight:500;font-size:18px}

/* reaching them (the reference's contact page): bold 20px name over 20px lines, 40 apart */
.two{display:flex;gap:100px}
.two .lead{flex:0 0 38%;min-width:0}
.two .its{flex:1 1 0}
.tel{font:400 50px/55px Newsreader,Georgia,serif;letter-spacing:-.03em;overflow-wrap:anywhere}
.tel-n{margin-top:8px;font-size:18px;color:var(--muted)}
.mail{margin-top:24px;font-size:20px;overflow-wrap:anywhere}
.lead .btns{margin-top:40px}
.soc{margin-top:40px;display:flex;flex-wrap:wrap;gap:8px 24px;font-weight:500;font-size:18px}
.its{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:40px 60px;align-content:start}
.its.n1{grid-template-columns:minmax(0,1fr)}
.half .its{margin-top:60px;grid-template-columns:minmax(0,1fr)}
.it .hrs span:nth-child(even){white-space:nowrap}
.it{display:flex;flex-direction:column;font-size:20px;line-height:1.3;min-width:0;overflow-wrap:anywhere}
.it strong{font-weight:700}
.it .hrs{display:grid;grid-template-columns:auto 1fr;column-gap:20px;overflow-wrap:normal}
.it .nt{font-size:16px;line-height:1.4;color:var(--muted);margin-top:10px}

/* closing band: the picture across, 720 high; 50px line at the foot left, text at the top right, the one filled button */
.ban{position:relative;min-height:720px;overflow:hidden;background:var(--deep);color:var(--on);display:flex}
.ban.plain{min-height:520px}
.ban>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ban-veil{position:absolute;inset:0;background:color-mix(in srgb,var(--shade) 70%,transparent)}
.ban-cap{position:relative;flex:1;margin:100px;display:flex;justify-content:space-between;gap:40px}
.ban h2{align-self:flex-end;flex:0 1 600px;font:400 50px/1.3 Newsreader,Georgia,serif;text-wrap:balance;min-width:0}
.ban .r{flex:0 0 600px;max-width:48%;display:flex;flex-direction:column;justify-content:space-between;align-items:flex-start;gap:40px}
.ban .txt p{font-size:18px;line-height:1.3;letter-spacing:0}

/* foot */
.ft{background:var(--alt);padding:100px 0}
.ft-m{display:flex;justify-content:space-between;gap:60px}
.ft .l{flex:0 1 840px;min-width:0}
.ft .mark{min-height:119px;display:flex;align-items:center}
.ft .logo{max-width:288px;max-height:119px;width:auto;height:auto}
.ft .wm{font:500 34px/1.1 Newsreader,Georgia,serif;letter-spacing:.01em;max-width:480px}
.ft .tag{margin-top:97px;max-width:620px;font:400 50px/60px Newsreader,Georgia,serif;text-wrap:balance}
.ft .nap{margin-top:21px;max-width:560px;font-size:14px;line-height:23.8px;color:var(--muted)}
.ft .r{flex:0 0 auto;min-width:293px;max-width:46%;display:flex;flex-direction:column}
.totop{align-self:flex-end;margin:66px 0 127px;transition:transform .4s ease}
.totop:hover{transform:translateY(-4px)}
.ft nav{display:flex;gap:100px;justify-content:flex-end}
.ft nav ul{display:flex;flex-direction:column;gap:10px}
.ft nav a{font-weight:500;font-size:18px;line-height:21px;transition:opacity .4s ease}
.ft nav a:hover,.bot a:hover{opacity:.5}
.badges{display:flex;flex-wrap:wrap;gap:16px;justify-content:flex-end;margin-top:40px}
.badges img{width:100px;height:auto}
.creds{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 60px;margin-top:60px;font-size:14px;line-height:1.5;color:var(--muted)}
.creds strong{font-weight:600;color:var(--k)}
.bot{margin-top:60px;padding-top:40px;border-top:1px solid color-mix(in srgb,var(--k) 20%,transparent);display:flex;flex-direction:column;gap:10px}
.bot ul{display:flex;flex-wrap:wrap;gap:6px 20px}
.bot a{font-size:16px;color:var(--muted);transition:opacity .4s ease}
.legal{font-weight:300;font-size:14px;line-height:1.5;color:var(--muted);max-width:1000px}

@media (max-width:1280px){
  .hd-nav{display:none}.burger{display:block}
}
.hd.compact .hd-nav{display:none}.hd.compact .burger{display:block}
@media (max-width:1024px){
  body{font-size:16px}
  .pad,.cat{padding:60px 0}
  .lab{font-size:20px}
  .say,.half-t .say{font-size:28px;line-height:33.6px}
  .btn{min-height:50px;font-size:16px;padding:8px 28px}
  .hd{height:80px;padding:10px 20px}
  .brand{font-size:22px;max-width:260px}.brand.long{font-size:17px;max-width:230px}
  .menu{padding:140px 14px 40px 34px}
  .menu a{font-size:26px;line-height:46px}
  .hero-cap{flex-direction:column;align-items:flex-start;justify-content:flex-end;bottom:40px;gap:0;top:90px}
  .hero .l{flex:0 0 auto;padding-bottom:40px;max-width:100%}
  h1,h1.h1-s{font-size:40px;line-height:44px}
  h1.h1-s{font-size:32px;line-height:36px}
  .hero .r{flex:0 0 auto;max-width:100%;width:100%}
  .head{flex-direction:column;gap:20px}
  .head .lab{flex:none}
  .head-r{flex:none}
  .cards,.cards.c2,.cards.c4{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;margin-right:-20px;padding-right:20px}
  .cards::-webkit-scrollbar{display:none}
  .cards .card{flex:0 0 78%;max-width:340px;scroll-snap-align:start}
  .cards.c1{display:grid;margin-right:0;padding-right:0}.cards.c1 .card{max-width:none}
  .cards.c1 .card figure,.cards.c2 .card figure{aspect-ratio:302/423}
  .card figure{aspect-ratio:302/423}
  .card .no,.cards.t-s .no{padding:20px 20px 0;font-size:40px;line-height:49px}
  .card figcaption{background:radial-gradient(ellipse 200px 150px at 100% 0,color-mix(in srgb,var(--shade) 68%,transparent) 0,color-mix(in srgb,var(--shade) 66%,transparent) 72%,transparent 100%)}
  .people figcaption{background:none}
  .card .cap,.cards.t-s .cap{padding:90px 20px 20px}
  .card h3,.card h4,.cards.t-s h3,.cards.t-s h4{font-size:20px;line-height:26px}
  .cells{grid-template-columns:minmax(0,1fr);margin-top:40px}
  .cell{padding:30px 20px;gap:16px}
  .cell p{font-size:16px}
  .firm{flex-direction:column;gap:20px}
  .firm>.lab{flex:none}
  .firm-r .txt{margin-top:30px}
  .ngrid,.ngrid.g2,.ngrid.g4{grid-template-columns:repeat(3,minmax(0,1fr));column-gap:20px;row-gap:30px;margin-top:60px}
  .ngrid.g4,.ngrid.wide,.ngrid.g2{grid-template-columns:repeat(2,minmax(0,1fr))}
  .ngrid .n{border-left:0;border-top:1px solid color-mix(in srgb,var(--on) 50%,transparent);padding:20px 0 0;gap:14px}
  .n .v,.nlist .v{font-size:40px;line-height:1.1}
  .ngrid small{font-size:16px}
  .half,.half.rev{display:flex;flex-direction:column}
  .half-t,.half.rev .half-t{padding:60px 20px}
  .half-p{min-height:0;aspect-ratio:350/214;order:2}
  .half.rev .half-p{order:0}
  .nlist{margin-top:40px}.nlist .n{padding-bottom:30px}
  .car-top{flex-direction:column}
  .car-l{flex:none;padding:40px 20px;border-right:0;border-bottom:1px solid var(--rule)}
  .car-l .lab{margin-bottom:20px}
  .disp{font-size:28px;line-height:30.8px}
  .car-l .txt{margin-top:20px}
  .slide,.car.short .slide{flex:0 0 83.3%;min-height:349px;padding:40px 20px;gap:40px}
  .car.short .slide{min-height:220px}
  .slide h3{font-size:24px;line-height:24px}
  .slide p{font-size:16px;line-height:1.3}
  .list{flex-direction:column;gap:30px}
  .list>.lab{flex:none}
  span.lab:empty{display:none}
  .rows,.blks,.creds{grid-template-columns:minmax(0,1fr)}
  .rows .nm,.rows .pr{font-size:18px}
  .grp h3,.gt-h{font-size:24px}
  .grp+.grp{margin-top:60px}
  .band{margin:50px 0}
  .pad-t{padding-top:60px;padding-bottom:40px}
  .pgrid,.pgrid.p2,.pgrid.p4,.qgrid,.qgrid.q2{grid-template-columns:minmax(0,1fr)}
  .plan,.pgrid.p4 .plan,.q{padding:40px 20px;gap:30px;border-left:0;margin-left:0}
  .plan h3{font-size:28px}.plan .price .v{font-size:44px}
  .q blockquote p{font-size:22px}
  .two{flex-direction:column;gap:50px}
  .two .lead{flex:none}
  .tel{font-size:34px;line-height:40px}
  .its{grid-template-columns:minmax(0,1fr);gap:30px}
  .it{font-size:18px}
  .ban,.ban.plain{min-height:422px}
  .ban-cap{margin:20px;flex-direction:column;justify-content:space-between}
  .ban h2{align-self:auto;flex:none;font-size:38px;line-height:45.6px}
  .ban .r{flex:1 1 auto;max-width:none}
  .ban .txt p{font-size:16px}
  .ft{padding:40px 0 40px}
  .ft-m{flex-direction:column;gap:40px}
  .ft .mark{min-height:68px}.ft .logo{max-width:200px;max-height:68px}
  .ft .wm{font-size:26px}
  .ft .tag{margin-top:38px;font-size:30px;line-height:36px}
  .ft .r{max-width:none;min-width:0}
  .totop{margin:0 0 20px}
  .ft nav{justify-content:flex-start;gap:60px}
  .ft nav a{font-size:16px}
  .badges{justify-content:flex-start}
  .bot a,.legal{font-size:14px}
}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{transition-duration:.01ms!important;transition-delay:0s!important;animation:none!important}
  .js .rv{opacity:1;transform:none}
}
"""

JS = r"""
(function(){
var R=document.documentElement;R.classList.add('js');
var calm=matchMedia('(prefers-reduced-motion: reduce)').matches;
var hd=document.getElementById('hd'),menu=document.getElementById('menu'),bg=document.querySelector('.burger'),last=0,open=false;
function onScroll(){var y=window.scrollY||0;if(!hd)return;hd.classList.toggle('scrolled',y>60);
  if(!open){if(y>last+2&&y>130)hd.classList.add('away');else if(y<last-2||y<=130)hd.classList.remove('away');}last=y;}
addEventListener('scroll',onScroll,{passive:true});onScroll();
/* a row of links that does not fit beside the name goes into the menu */
function fit(){if(!hd)return;hd.classList.remove('compact');var n=hd.querySelector('.hd-nav'),b=hd.querySelector('.brand');if(n&&b&&n.offsetWidth&&(hd.scrollWidth>hd.clientWidth+1||b.getBoundingClientRect().right+24>n.getBoundingClientRect().left))hd.classList.add('compact');}
fit();addEventListener('resize',fit);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fit);
if(hd)hd.addEventListener('focusin',function(){hd.classList.remove('away');});
function setMenu(v){open=v;if(!menu)return;menu.classList.toggle('open',v);menu.setAttribute('aria-hidden',v?'false':'true');bg.setAttribute('aria-expanded',v?'true':'false');
  hd.classList.remove('away');document.body.style.overflow=v?'hidden':'';}
if(bg&&menu){bg.addEventListener('click',function(ev){ev.preventDefault();setMenu(!open);});
  bg.addEventListener('keydown',function(ev){if(ev.key===' '||ev.key==='Enter'){ev.preventDefault();setMenu(!open);}});
  menu.addEventListener('click',function(ev){if(ev.target.closest('a'))setMenu(false);});
  addEventListener('keydown',function(ev){if(ev.key==='Escape'&&open){setMenu(false);bg.focus();}});}
/* numbers rise 30px and count as each row comes into the window */
function count(el){var m=/^(\d+)(.*)$/.exec(el.textContent.trim());if(!m||calm)return;var to=+m[1],suf=m[2],t0=null;
  function step(t){if(t0===null)t0=t;var p=Math.min(1,(t-t0)/1400);p=1-Math.pow(1-p,3);el.textContent=Math.round(to*p)+suf;if(p<1)requestAnimationFrame(step);}
  el.textContent='0'+suf;requestAnimationFrame(step);}
var rv=[].slice.call(document.querySelectorAll('.rv'));
if('IntersectionObserver' in window&&!calm){var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');
  var n=en.target.querySelector('[data-n]');if(n)count(n);io.unobserve(en.target);}});},{rootMargin:'0px 0px -12% 0px'});rv.forEach(function(x){io.observe(x);});}
else rv.forEach(function(x){x.classList.add('in');});
/* carousel: the two arrows move one column */
[].forEach.call(document.querySelectorAll('.car'),function(c){var r=c.querySelector('.car-r'),pv=c.querySelector('.prev'),nx=c.querySelector('.next'),ct=c.querySelector('.ctrl');if(!r||!ct)return;
  function upd(){var max=r.scrollWidth-r.clientWidth;ct.classList.toggle('none',max<4);pv.disabled=r.scrollLeft<4;nx.disabled=r.scrollLeft>max-4;}
  function go(dir){var s=r.querySelector('.slide');r.scrollBy({left:dir*(s?s.getBoundingClientRect().width:300),behavior:calm?'auto':'smooth'});}
  pv.addEventListener('click',function(){go(-1);});nx.addEventListener('click',function(){go(1);});r.addEventListener('scroll',upd,{passive:true});addEventListener('resize',upd);upd();});
})();
"""


def render(d: dict) -> str:
    d = d if isinstance(d, dict) else {}
    lang = _t(d.get('lang')) or 'en'
    ui = UI.get(lang[:2], {})
    pal = _palette(_dic(d.get('palette')))
    pool = Pool(d)
    brand = _dic(d.get('brand'))
    hero = _dic(d.get('hero'))
    # pictures are given out in this order: first screen, the steps' cards, the people band, the door, the statement half, the closing band, a band in the list
    s_hero = _hero(d, pool)
    s_why = _why(d, pool)
    s_team = _team(d, pool)
    s_reach = _reach(d, pool, ui)
    s_nums = _numbers(d, pool)
    s_close = _close(d, pool)
    s_cat = _catalogue(d, pool)
    body = ''.join([
        '<a class="skip" href="#main">%s</a>' % e(ui.get('skip', '↓')),
        _header(d, ui), '<main id="main">', s_hero, s_why, s_nums, _carousel(d, ui), s_cat, _plans(d), _faq(d),
        s_team, _quotes(d), s_reach, s_close, '</main>', _foot(d, ui)])
    title = ' — '.join(x for x in [_t(brand.get('name')), _t(hero.get('title'))] if x)
    root = ':root{--g:%(g)s;--k:%(k)s;--a:%(a)s;--on-a:%(on_a)s;--deep:%(deep)s;--shade:%(shade)s;--on:%(on)s;--alt:%(alt)s;--rule:%(rule)s;--muted:%(muted)s}' % pal
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title>%s<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="%s"><style>%s%s</style></head><body>%s<script>%s</script></body></html>') % (
        e(lang), e(title), '<meta name="description" content="%s">' % e(_t(hero.get('text'))[:300]) if _t(hero.get('text')) else '',
        FONTS, root, CSS, body, JS)
