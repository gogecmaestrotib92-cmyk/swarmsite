"""iip/render.py — one pure function: render(d) -> a complete page.

The build (section anatomy, grid, measures, type scale, spacing, slants, motion, phone layout) was measured on the
reference's pages at 1440 and 390 on 2026-11-12 (see NOTES.md): the home page gives the bar, header, opening panel,
picture rows and foot; its inner pages give the parts a non-profit's own page needs and the home page keeps elsewhere
(slanted colour bands, story rows, cards, people grid, questions, the dark address band).
Nothing of the reference's code, words, pictures, icons, logos or colours is here. The client's data fills it; a section
whose data is missing is left out whole. No model call, no client logic, no file reads.
"""
import html
import json
import re

# TASA Orbiter is the reference's own face and is open-licence (SIL OFL, served by Google Fonts) — no stand-in needed.
FONTS = 'https://fonts.googleapis.com/css2?family=TASA+Orbiter:wght@400..800&display=swap'
MENU = {'en': 'Menu', 'de': 'Menü', 'fr': 'Menu', 'es': 'Menú', 'it': 'Menu', 'pt': 'Menu', 'nl': 'Menu', 'sr': 'Meni',
        'hr': 'Izbornik', 'sl': 'Meni', 'pl': 'Menu', 'sv': 'Meny', 'da': 'Menu', 'nb': 'Meny'}


# ───────────────────────── colour: the reference's relations (ground / deep ink / one accent / a pale tint of it)
def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 0, 0)


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
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _pick(bg, cands, need):
    """first candidate that reaches `need` on bg, else the strongest"""
    for c in cands:
        if _con(c, bg) >= need:
            return c
    return max(cands + ['#ffffff', '#000000'], key=lambda c: _con(c, bg))


def colours(p):
    g, ink, acc = p.get('ground') or '#ffffff', p.get('ink') or '#111111', p.get('accent') or p.get('ink') or '#111111'
    if _con(ink, g) < 4.5:
        ink = _pick(g, ['#111111', '#ffffff'], 4.5)
    on = _pick(acc, ['#ffffff', ink, g], 4.5)
    dk, ond = ink, _pick(ink, [g, '#ffffff'], 4.5)
    t = .16
    tint = _mix(acc, g, t)
    while _con(ink, tint) < 7 and t > .04:
        t -= .03
        tint = _mix(acc, g, t)
    # the hairlines lie on the ground at .3, multiplied; small type that a line crosses must still read on the line
    ln = _mix(acc, '#ffffff', .8)

    def under(line):
        return _hex(tuple(gc * .7 + .3 * gc * lc / 255 for gc, lc in zip(_rgb(g), _rgb(line))))
    for _ in range(6):
        if _con(ink, under(ln)) >= 5:
            break
        ln = _mix(ln, '#ffffff', .6)
    lg = under(ln)
    ey = next((c for c in [acc, _mix(acc, ink, .85), _mix(acc, ink, .7), _mix(acc, ink, .5), _mix(acc, ink, .3), ink]
               if _con(c, lg) >= 4.6 and _con(c, g) >= 4.6), ink)
    return {
        'g': g, 'ink': ink, 'acc': acc, 'on': on, 'dk': dk, 'ond': ond, 'tint': tint,
        'ey': ey,                                                          # small capitals on the ground
        'hl': _pick(dk, [_mix(acc, ond, .45), _mix(acc, ond, .25), ond], 4.5),  # headings on the dark band
        'ft': _pick(acc, [ink], 3.2) if _con(ink, acc) >= 3.2 else on,     # the big line in the foot
        'ln': ln,
        'inv': _pick(g, [acc, ey, ink], 4.5),                                  # text of the ground-coloured button
    }


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def m(src):
    return src if (not src or src.startswith(('http:', 'https:', 'data:', '/'))) else '../../' + src


def paras(text, cls=''):
    parts = [t.strip() for t in str(text or '').replace('\r', '').split('\n') if t.strip()]
    c = ' class="%s"' % cls if cls else ''
    return ''.join('<p%s>%s</p>' % (c, e(t)) for t in parts)


TRI = '<svg class="tri" viewBox="0 0 32 52" preserveAspectRatio="none" aria-hidden="true"><path d="M0 0 32 26 0 52z" fill="currentColor"/></svg>'


def btn(c, kind=''):
    """the reference's button: label, a triangle flush at the right end; on hover a second triangle slides in from the left"""
    if not c or not c.get('t'):
        return ''
    inner = '<span class="b2" aria-hidden="true">%s</span><span class="bi"><span class="bt">%s</span>%s</span>' % (TRI, e(c['t']), TRI)
    if c.get('h'):
        return '<a class="b %s" href="%s">%s</a>' % (kind, e(c['h']), inner)
    return ''


def link(t, h, cls=''):
    c = ' class="%s"' % cls if cls else ''
    return '<a%s href="%s">%s</a>' % (c, e(h), e(t)) if h else '<span%s>%s</span>' % (c, e(t))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# words or signs inside a photograph: such a picture is never cropped (a crop cuts the words mid-word). Capture should set
# `lettering: true` on the photo; until it does, the alt is read for the usual ways a describer names lettering.
LETTERING = re.compile(r"\b(words?|letter(?:s|ing)?|lettered|sign(?:s|post|board)?|text|written|writing|caption(?:ed)?|"
                       r"inscri\w*|banner|placard|poster|logo|label(?:led)?|reads|says|slogan|headline|watermark)\b", re.I)


def lettered(p):
    if p.get('lettering') is not None:
        return bool(p['lettering'])
    return bool(LETTERING.search(p.get('alt') or ''))


class Pool:
    """the client's photographs, each used once; chosen by proportion and size, never looped"""

    def __init__(self, d):
        media = d.get('media') or {}
        self.all = [p for p in (media.get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
        self.by = {p['src']: p for p in self.all}
        taken = set()
        for it in ((d.get('steps') or {}).get('items') or []):
            taken.add(it.get('img'))
        cat = d.get('catalogue') or {}
        for g in cat.get('groups') or []:
            taken.add(g.get('img'))
            for it in g.get('items') or []:
                taken.add(it.get('img'))
        team = d.get('team') or {}
        for it in (team.get('items') or []) + [i for g in (team.get('groups') or []) for i in (g.get('items') or [])]:
            taken.add(it.get('img'))
        for c in d.get('credentials') or []:
            taken.add(c.get('img'))
        for s in ((d.get('place') or {}).get('spaces') or []):
            taken.add(s.get('img'))
        self.free = [p for p in self.all if p['src'] not in taken and p.get('role') not in ('portrait', 'product')]

    def take(self, kind, minw, minh=0, whole=False):
        """kind: wide (1.2–2.6) · tall (<0.95) · any (≤2.6). A picture is never asked to stand wider than its own pixels.
        A lettered picture is given only to a slot that shows it whole (`whole=True`: the slot keeps its proportion)."""
        def ok(p):
            a = p['w'] / p['h']
            if p['w'] < minw or p['h'] < minh or a > 2.6:
                return False
            if lettered(p) and not whole:
                return False
            return (1.2 <= a) if kind == 'wide' else (a < .95) if kind == 'tall' else True
        for p in self.free:
            if ok(p):
                self.free.remove(p)
                return p
        return None


def pic(p, slot, cls='', eager=False, lo=None, hi=None):
    """a photograph in its slot; `lo`/`hi` clamp the slot's proportion around the picture's own"""
    if not p:
        return ''
    a = p['w'] / p['h']
    if lo is not None and not lettered(p):  # a lettered picture keeps its own proportion: nothing is cut off
        a = clamp(a, lo, hi)
    return ('<div class="pv %s" data-slot="%s" style="--a:%.4f;--nw:%dpx"><img src="%s" alt="%s" width="%d" height="%d"%s decoding="async"></div>'
            % (cls, slot, a, p['w'], e(m(p['src'])), e(p.get('alt') or ''), p['w'], p['h'], '' if eager else ' loading="lazy"'))


# ───────────────────────── sections
def s_head(d, c):
    brand = d.get('brand') or {}
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    contact = d.get('contact') or {}
    phone = contact.get('phone') or (d.get('place') or {}).get('phone') or {}
    if isinstance(phone, str):
        phone = {'t': phone, 'h': 'tel:' + ''.join(ch for ch in phone if ch.isdigit() or ch == '+')}
    bar = ''
    if phone.get('t'):
        bar += link(phone['t'], phone.get('h'), 'ul')
    si = d.get('signin') or {}
    if si.get('t') and si.get('h'):
        bar += link(si['t'], si['h'], 'ul')
    cta = d.get('cta') or {}
    if cta.get('t') and cta.get('h'):
        bar += '<a class="ub" href="%s"><span class="b2" aria-hidden="true">%s</span><span class="bi"><span class="bt">%s</span>%s</span></a>' % (e(cta['h']), TRI, e(cta['t']), TRI)
    name = e(brand.get('name') or '')
    logo = brand.get('logo')
    mark = ('<img src="%s" alt="%s">' % (e(m(logo)), name)) if logo else name
    links = ''.join('<a href="%s">%s</a>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav)
    menu = ''
    if nav:
        word = MENU.get(str(d.get('lang') or 'en')[:2].lower(), 'Menu')
        menu = ('<details class="mn"><summary><span class="ms">%s</span><span class="mt">%s</span></summary>'
                '<nav class="mp" aria-label="%s">%s%s</nav></details>') % (TRI, e(word), e(word), links, btn(cta, 'inv') if cta.get('h') else '')
    return ('<div class="ubar">%s</div><header class="hd"><a class="lg%s" href="%s">%s</a>'
            '<nav class="nv" aria-label="%s">%s</nav>%s</header>') % (bar, ' im' if logo else '', e(brand.get('home') or '#'), mark, name, links, menu)


def s_hero(d, pool):
    h = d.get('hero') or {}
    title = h.get('title') or (d.get('brand') or {}).get('name') or ''
    n = len(title)
    size, msize = ((86.4, 40) if n <= 26 else (72, 36) if n <= 40 else (60, 32) if n <= 64 else (48, 28) if n <= 110 else (40, 25))
    p = pool.take('wide', 900, 750) or pool.take('any', 900, 750) or pool.take('any', 640, 750)
    if not p:  # type alone carries the panel: one step larger, the panel a little lower
        size = 86.4 if n <= 40 else 64 if n <= 110 else 48
    # the reference's type column is 444 of 1392 with the imagery over the other two thirds; a long title needs more room
    out = '<section class="hero"><div class="hp%s%s" style="--h1:%spx;--h1m:%spx"><div class="ht">' % (' hpc' if p else '', ' sh1' if n <= 40 else '', size, msize)
    if h.get('kicker'):
        out += '<p class="ey">%s</p>' % e(h['kicker'])
    out += '<h1>%s</h1>' % e(title)
    if h.get('text'):
        out += paras(h['text'], 'sub')
    out += '</div><div class="hb">'
    if h.get('note'):
        out += '<p class="sm">%s</p>' % e(h['note'])
    out += '<div class="bs">%s%s</div></div>' % (btn(h.get('primary'), 'inv'), btn(h.get('secondary'), 'dkb'))
    out += pic(p, 'hero', 'hpic', eager=True)
    return out + '</div></section>'


def s_trust(d):
    t = [x for x in (d.get('trust') or []) if x]
    return '<ul class="tr">%s</ul>' % ''.join('<li>%s</li>' % e(x) for x in t) if t else ''


def people(items):
    out = ''
    for it in items:
        out += '<li><b>%s</b>' % link(it.get('name'), it.get('h'))
        if it.get('role'):
            out += '<span>%s</span>' % e(it['role'])
        if it.get('text'):
            out += '<p>%s</p>' % e(it['text'])
        if it.get('phone'):
            out += link(it['phone'], 'tel:' + ''.join(ch for ch in str(it['phone']) if ch.isdigit() or ch == '+'), 'tl')
        if it.get('email'):
            out += link(it['email'], 'mailto:' + it['email'], 'tl')
        out += '</li>'
    return out


def s_rows(d, pool):
    """the home page's alternating picture rows: the statement, then the people when they are one or two"""
    rows = []
    st = d.get('statement') or {}
    t2 = (d.get('hero') or {}).get('text2')
    if st.get('title') or st.get('text') or t2:
        p = pool.take('tall', 760) or pool.take('any', 760) or pool.take('any', 760, whole=True)
        tx = '<div class="tx">'
        if st.get('title'):
            tx += '<h2 class="h3">%s</h2>' % e(st['title'])
        tx += paras(st.get('text'), 'sub ind') + paras(t2, 'bd') + '</div>'
        rows.append(('r50' + ('' if p else ' np'), tx, pic(p, 'statement', 'bleed', lo=.667, hi=1.4)))
    team = d.get('team') or {}
    items = team.get('items') or []
    if not team.get('groups') and items and len(items) <= 2 and sum(1 for i in items if i.get('img')) <= 1 and (len(items) == 1 or not any(i.get('img') for i in items)):
        one = items[0] if len(items) == 1 else None
        p = pool.by.get(one.get('img')) if one and one.get('img') else None
        tx = '<div class="tx">'
        if one:
            if one.get('role'):
                tx += '<p class="ey">%s</p>' % e(one['role'])
            tx += '<h2 class="h3">%s</h2>' % link(team.get('title') or one.get('name'), one.get('h'))
            tx += paras(team.get('text') or one.get('text'), 'sub ind')
            if team.get('text') and one.get('text'):
                tx += paras(one['text'], 'bd')
            cl = ''
            if one.get('phone'):
                cl += link(one['phone'], 'tel:' + ''.join(ch for ch in str(one['phone']) if ch.isdigit() or ch == '+'), 'tl')
            if one.get('email'):
                cl += link(one['email'], 'mailto:' + one['email'], 'tl')
            tx += '<p class="cl">%s</p>' % cl if cl else ''
        else:
            if team.get('title'):
                tx += '<h2 class="h3">%s</h2>' % e(team['title'])
            tx += paras(team.get('text'), 'sub ind') + '<ul class="ppl">%s</ul>' % people(items)
        tx += '</div>'
        rows.append(('r60' + ('' if p else ' np'), tx, pic(p, 'team', 'bleed', lo=.9, hi=1.6)))
    if not rows:
        return ''
    out = '<section class="rows">'
    for cls, tx, pv in rows:
        out += '<div class="row %s">%s%s</div>' % (cls, tx, pv)
    return out + '</section>'


def s_team_grid(d, pool):
    team = d.get('team') or {}
    groups = team.get('groups') or ([{'t': '', 'items': team.get('items')}] if team.get('items') else [])
    items = [i for g in groups for i in (g.get('items') or [])]
    if not items:
        return ''
    if not team.get('groups') and len(items) <= 2 and sum(1 for i in items if i.get('img')) <= 1 and (len(items) == 1 or not any(i.get('img') for i in items)):
        return ''  # shown as a row
    out = '<section class="sec team"><header class="sh">'
    if team.get('title'):
        out += '<h2>%s</h2>' % e(team['title'])
    out += paras(team.get('text'), 'sub') + '</header>'
    for g in groups:
        if not g.get('items'):
            continue
        if g.get('t'):
            out += '<h3 class="ey gt">%s</h3>' % e(g['t'])
        out += '<ul class="tg">'
        for it in g['items']:
            p = pool.by.get(it.get('img')) if it.get('img') else None
            out += '<li>'
            if p:
                out += '<div class="tp" data-slot="portrait" style="--nw:%dpx"><img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></div>' % (p['w'], e(m(p['src'])), e(p.get('alt') or it.get('name') or ''), p['w'], p['h'])
            out += people([it])[4:-5] + '</li>'
        out += '</ul>'
    return out + '</section>'


def s_figures(d, pool):
    f = [x for x in (d.get('figures') or []) if x.get('v')]
    if not f:
        return ''
    p = pool.take('wide', 900) or pool.take('any', 900)
    out = '<section class="band tint figs%s"><div class="bw"><ul class="fg">' % (' bpc' if p else '')
    for x in f:
        out += '<li><b>%s</b><span>%s</span></li>' % (e(x['v']), e(x.get('l') or ''))
    return out + '</ul>%s</div></section>' % pic(p, 'figures', 'bp')


def cat_body(it, with_button):
    out = ''
    if it.get('price'):
        out += '<p class="pr">%s</p>' % e(it['price'])
    if it.get('state'):
        out += '<p class="stt">%s</p>' % e(it['state'])
    if it.get('note'):
        out += '<p class="nt">%s</p>' % e(it['note'])
    out += paras(it.get('text'), 'bd')
    if it.get('prices'):
        out += '<dl class="pl">%s</dl>' % ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(x.get('label') or ''), e(x.get('price') or '')) for x in it['prices'])
    if it.get('rows'):
        out += '<ul class="bl">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in it['rows'] if r)
    if with_button and it.get('h') and it.get('name'):
        out += btn({'t': it['name'], 'h': it['h']})
    return out


ROWS = 3  # pictured catalogue items set as full story rows; the rest go into the card part


def first_sentence(t):
    t = str(t or '').strip()
    m_ = re.match(r'(.+?[.!?])(?:\s+|$)(.*)', t, re.S)
    return (m_.group(1), m_.group(2).strip()) if m_ else (t, '')


def cat_card(it, H, pool):
    """the reference's card (take-action "Get involved"): picture, name, price, the first sentence; the rest opens in place"""
    p = pool.by[it['img']]
    out = '<article class="cc">'
    out += ('<div class="cp" data-slot="catalogue-card" style="--nw:%dpx"><img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></div>'
            % (p['w'], e(m(p['src'])), e(p.get('alt') or ''), p['w'], p['h']))
    out += '<%s class="h4">%s</%s>' % (H, e(it['name']), H)
    if it.get('price'):
        out += '<p class="pr">%s</p>' % e(it['price'])
    if it.get('state'):
        out += '<p class="stt">%s</p>' % e(it['state'])
    if it.get('note'):
        out += '<p class="nt">%s</p>' % e(it['note'])
    head, rest = first_sentence(it.get('text'))
    more = paras(rest, 'bd')
    if it.get('prices'):
        more += '<dl class="pl">%s</dl>' % ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(x.get('label') or ''), e(x.get('price') or '')) for x in it['prices'])
    if it.get('rows'):
        more += '<ul class="bl">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in it['rows'] if r)
    if more:
        out += ('<details class="more"><summary><span class="plus" aria-hidden="true"></span><span class="bd">%s</span></summary>'
                '<div class="mo">%s</div></details>') % (e(head), more)
    elif head:
        out += '<p class="bd">%s</p>' % e(head)
    if it.get('h'):
        out += btn({'t': it['name'], 'h': it['h']})
    return out + '</article>'


def s_catalogue(d, pool):
    cat = d.get('catalogue') or {}
    groups = [g for g in (cat.get('groups') or []) if g.get('items') or g.get('t')]
    if not groups:
        return ''
    out = '<section class="sec cat">'
    titled = bool(cat.get('title'))
    if titled or cat.get('text'):
        out += '<header class="sh">%s%s</header>' % ('<h2>%s</h2>' % e(cat['title']) if titled else '', paras(cat.get('text'), 'sub'))
    rows_left = ROWS
    n_pic = sum(1 for g in groups for i in (g.get('items') or []) if i.get('img') and pool.by.get(i['img']))
    for gi, g in enumerate(groups):
        # the reference's strip of pictures between the lead and the rows — only for a catalogue that would otherwise run long
        # in type: when its items carry pictures enough to fill cards, the cards already break the page every screen
        if gi == 1 and n_pic <= ROWS:
            strip = [pool.take('wide', 700) for _ in range(3)] if len([p for p in pool.free if 1.2 <= p['w'] / p['h'] <= 2.6 and p['w'] >= 700 and not lettered(p)]) >= 3 else []
            if strip:
                out += '<div class="strip">%s</div>' % ''.join(pic(p, 'strip') for p in strip)
        out += '<div class="cg">'
        if g.get('t') or g.get('text'):
            out += '<header class="%s">' % ('gh' if titled else 'sh')
            if g.get('t'):
                out += ('<h3 class="ey">%s</h3>' if titled else '<h2>%s</h2>') % link(g['t'], g.get('h'))
            out += paras(g.get('text'), 'sub') + '</header>'
        H = 'h4' if titled else 'h3'
        withp = [i for i in (g.get('items') or []) if i.get('img') and pool.by.get(i['img'])]
        plain = [i for i in (g.get('items') or []) if i not in withp and i.get('name')]
        rows, cards = withp[:rows_left], withp[rows_left:]
        rows_left -= len(rows)
        if rows:
            out += '<div class="srs">'
            for it in rows:
                out += '<article class="sr"><div class="tx"><%s class="h3">%s</%s>%s</div>%s</article>' % (
                    H, e(it.get('name') or ''), H, cat_body(it, True), pic(pool.by[it['img']], 'catalogue', 'bleed', lo=.8, hi=1.5))
            out += '</div>'
        if cards:
            n = len(cards)
            out += '<div class="cards ccs c%d">%s</div>' % (2 if n in (2, 4) else 3 if n in (3, 5, 6, 9) else 4, ''.join(cat_card(it, H, pool) for it in cards))
        if plain:
            out += '<div class="cl2%s">' % (' few' if len(plain) == 1 else '')
            for it in plain:
                out += '<article><%s class="h4">%s</%s>%s</article>' % (H, link(it['name'], it.get('h'), 'tl2' if it.get('h') else ''), H, cat_body(it, False))
            out += '</div>'
        out += '</div>'
    if cat.get('note'):
        out += '<p class="sub cn">%s</p>' % e(cat['note'])
    return out + '</section>'


def s_plans(d):
    """a client's tiers, built from the reference's card part (small capitals, title, text, list, button)"""
    pl = d.get('plans') or {}
    items = [i for i in (pl.get('items') or []) if i.get('name')]
    if not items:
        return ''
    n = len(items)
    cols = n if n <= 2 else 4 if n == 4 else 3
    out = '<section class="sec inv"><header class="sh">%s%s</header><div class="cards c%d">' % ('<h2>%s</h2>' % e(pl['title']) if pl.get('title') else '', paras(pl.get('text'), 'sub'), cols)
    for it in items:
        out += '<article%s><p class="ey">%s</p>' % (' class="mk"' if it.get('marked') else '', e(it['name']))
        if it.get('price'):
            out += '<h3 class="h4">%s%s</h3>' % (e(it['price']), ' <small>%s</small>' % e(it['per']) if it.get('per') else '')
        out += paras(it.get('line'), 'bd')
        if it.get('rows'):
            out += '<ul class="bl">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in it['rows'] if r)
        c = it.get('cta')
        out += btn(c if isinstance(c, dict) else None) + '</article>'
    out += '</div>'
    if pl.get('note'):
        out += '<p class="sub cn">%s</p>' % e(pl['note'])
    return out + '</section>'


def s_features(d, pool):
    f = d.get('features') or {}
    items = [i for i in (f.get('items') or []) if i.get('t') or i.get('d')]
    if not (items or f.get('title')):
        return ''
    want = 3 if sum(len(i.get('d') or '') for i in items) + len(f.get('text') or '') > 1900 else 2
    stack = [p for p in [pool.take('any', 700) for _ in range(want)] if p]
    out = '<section class="band dark feat%s"><div class="fw"><div class="fl">' % (' fpc' if stack else '')
    if f.get('title'):
        out += '<h2 class="h3">%s</h2>' % e(f['title'])
    out += paras(f.get('text'), 'bd')
    if items:
        out += '<ul class="vl">'
        for i in items:
            out += '<li>%s%s%s</li>' % ('<b>%s</b>' % e(i['t']) if i.get('t') else '', ' – ' if i.get('t') and i.get('d') else '', e(i.get('d') or ''))
        out += '</ul>'
    out += '</div>'
    if stack:
        out += '<div class="fs">%s</div>' % ''.join(pic(p, 'features', lo=.75, hi=1.45) for p in stack)
    return out + '</div></section>'


def s_steps(d, pool):
    s = d.get('steps') or {}
    items = [i for i in (s.get('items') or []) if i.get('title') or i.get('text')]
    if not items:
        return ''
    n = len(items)
    cols = n if n <= 2 else 4 if (n == 4 or n == 7 or n == 8) else 3
    out = '<section class="sec inv"><header class="sh">%s%s</header><div class="cards c%d">' % ('<h2>%s</h2>' % e(s['title']) if s.get('title') else '', paras(s.get('text'), 'sub'), cols)
    allpic = all(i.get('img') and pool.by.get(i['img']) for i in items)
    for it in items:
        out += '<article>'
        if it.get('k'):
            out += '<p class="ey">%s</p>' % e(it['k'])
        if allpic:
            p = pool.by[it['img']]
            out += '<div class="cp" data-slot="step" style="--nw:%dpx"><img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></div>' % (p['w'], e(m(p['src'])), e(p.get('alt') or ''), p['w'], p['h'])
        if it.get('title'):
            out += '<h3 class="h4">%s</h3>' % e(it['title'])
        out += paras(it.get('text'), 'bd')
        c = it.get('cta')
        out += btn(c if isinstance(c, dict) else None) + '</article>'
    return out + '</div></section>'


def s_quotes(d, pool):
    q = [x for x in (d.get('quotes') or []) if x.get('q')]
    if not q:
        return ''
    p = pool.take('any', 760)
    out = '<section class="band dark quo%s"><div class="qw">%s<div class="ql">' % (' qpc' if p else '', pic(p, 'quotes', 'qp'))
    for x in q:
        out += '<blockquote><p>%s</p>' % e(x['q'])
        if x.get('name'):
            out += '<footer><b>%s</b>%s</footer>' % (e(x['name']), ' <span>%s</span>' % e(x['role']) if x.get('role') else '')
        out += '</blockquote>'
    return out + '</div></div></section>'


def s_contact_faq(d):
    c = d.get('contact') or {}
    faq = d.get('faq') or {}
    qs = [i for i in (faq.get('items') or []) if i.get('q')]
    left = ''
    ph = c.get('phone') or {}
    if isinstance(ph, str):
        ph = {'t': ph}
    if ph.get('t'):
        left += '<p class="big">%s</p>' % link(ph['t'], ph.get('h') or 'tel:' + ''.join(ch for ch in ph['t'] if ch.isdigit() or ch == '+'))
        if ph.get('note'):
            left += '<p class="bd">%s</p>' % e(ph['note'])
    if c.get('email'):
        left += '<p class="mid">%s</p>' % link(c['email'], 'mailto:' + c['email'])
    form = c.get('form') or {}
    if form.get('h') and form.get('t'):
        left += btn(form)
    routes = [r for r in (c.get('routes') or []) if r.get('t')]
    rl = ''
    if routes:
        rl = '<ul class="rt">%s</ul>' % ''.join('<li><b>%s</b>%s</li>' % (link(r['t'], r.get('h')), '<span>%s</span>' % e(r['note']) if r.get('note') else '') for r in routes)
    right = ''
    if qs:
        if faq.get('title'):
            right += '<h2 class="h3">%s</h2>' % e(faq['title'])
        right += '<div class="qs">'
        for i in qs:
            right += ('<details class="q"><summary><span class="plus" aria-hidden="true"></span><span class="qt">%s</span></summary>'
                      '<div class="an">%s</div></details>') % (e(i['q']), paras(i.get('a')))
        right += '</div>'
    if not (left or rl or right):
        return ''
    if right and (left or rl):
        return '<section class="sec cf"><div class="cfw"><div class="ct">%s%s</div><div class="fq">%s</div></div></section>' % (left, rl, right)
    if right:
        return '<section class="sec cf"><div class="cfw one"><div class="fq">%s</div></div></section>' % right
    return '<section class="sec cf"><div class="cfw"><div class="ct">%s</div><div class="ct">%s</div></div></section>' % (left, rl)


def addr_lines(a):
    if not a:
        return ''
    if isinstance(a, str):
        return '<span>%s</span>' % e(a)
    l1 = a.get('street')
    l2 = ' '.join(x for x in [a.get('postcode'), a.get('city')] if x)
    l3 = ', '.join(x for x in [a.get('region'), a.get('country')] if x)
    return ''.join('<span>%s</span>' % e(x) for x in [l1, l2, l3] if x)


def s_places(d, pool):
    """the dark band above the foot: every door, then the credentials"""
    locs = []
    pl = d.get('place') or {}
    if pl.get('address') or pl.get('hours'):
        locs.append({'name': (d.get('brand') or {}).get('name'), 'address': pl.get('address'), 'phone': (pl.get('phone') or {}).get('t') if isinstance(pl.get('phone'), dict) else pl.get('phone'),
                     'email': pl.get('email'), 'hours': pl.get('hours'), 'booking': pl.get('booking')})
    locs += [l for l in (d.get('locations') or []) if l.get('name') or l.get('address')]
    creds = [c for c in (d.get('credentials') or []) if c.get('t') or c.get('text')]
    if not (locs or creds):
        return ''
    out = '<section class="apply">'
    if locs:
        out += '<div class="ag c%d">' % min(len(locs), 3)
        for l in locs:
            out += '<article>'
            if l.get('name'):
                out += '<h2 class="ah">%s</h2>' % link(l['name'], l.get('h'))
            ad = addr_lines(l.get('address'))
            if ad:
                out += '<address>%s</address>' % ad
            cl = ''
            if l.get('phone'):
                cl += link(l['phone'], 'tel:' + ''.join(ch for ch in str(l['phone']) if ch.isdigit() or ch == '+'), 'tl')
            if l.get('email'):
                cl += link(l['email'], 'mailto:' + l['email'], 'tl')
            if cl:
                out += '<p class="cl">%s</p>' % cl
            hrs = [x for x in (l.get('hours') or []) if x.get('days')]
            if hrs:
                out += '<dl class="pl">%s</dl>' % ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(x['days']), e(' – '.join(y for y in [x.get('open'), x.get('close')] if y))) for x in hrs)
            out += paras(l.get('note'), 'bd')
            bk = l.get('booking')
            out += btn(bk if isinstance(bk, dict) else None)
            out += '</article>'
        out += '</div>'
    if creds:
        out += '<ul class="ag cr c%d">' % min(len(creds), 3)
        for c in creds:
            out += '<li>'
            p = pool.by.get(c.get('img')) if c.get('img') else None
            if c.get('img') and not p:
                p = {'src': c['img'], 'w': 0, 'h': 0}
            if p:
                out += '<img class="badge" data-slot="credential" src="%s" alt=""%s loading="lazy">' % (e(m(p['src'])), ' width="%d" height="%d" style="max-width:min(%dpx,100%%)"' % (p['w'], p['h'], p['w']) if p['w'] else '')
            if c.get('t'):
                out += '<b>%s</b>' % link(c['t'], c.get('h'))
            if c.get('year'):
                out += '<span>%s</span>' % e(c['year'])
            out += paras(c.get('text'), 'bd') + '</li>'
        out += '</ul>'
    return out + '</section>'


def s_foot(d):
    brand, cl, f = d.get('brand') or {}, d.get('close') or {}, d.get('foot') or {}
    links = [l for l in (d.get('links') or []) if l.get('t')] or [{'t': n['t'], 'h': n.get('h')} for n in (d.get('nav') or []) if n.get('t')]
    title = cl.get('title') or ''
    n = len(title)
    size, msize = (86.4, 40) if n <= 16 else (64, 32) if n <= 34 else (48, 28)
    out = '<footer class="ft" id="foot"><a class="top" href="#top" aria-label="↑ %s">↑</a><div class="fgd"><div class="fa"><p class="lg fl2">%s</p>' % (e(brand.get('name') or ''), e(brand.get('name') or ''))
    if f.get('text'):
        out += '<p class="fad">%s</p>' % e(f['text'])
    out += '</div><div class="fb">'
    if title:
        out += '<h2 class="fh" style="--fh:%spx;--fhm:%spx">%s</h2>' % (size, msize, ''.join('<span class="w">%s</span> ' % e(w) for w in title.split()))
    out += paras(cl.get('text'), 'sub')
    c = cl.get('cta')
    out += btn(c if isinstance(c, dict) else None, 'gr')
    if links:
        out += '<ul class="fl">%s</ul>' % ''.join('<li>%s%s</li>' % (link(l['t'], l.get('h'), 'ft1'), '<span>%s</span>' % e(l['d']) if l.get('d') else '') for l in links)
    lg = ''.join(link(l['t'], l.get('h')) for l in (f.get('links') or []) if l.get('t'))
    if f.get('legal'):
        lg += '<span>%s</span>' % e(f['legal'])
    if lg:
        out += '<p class="lgl">%s</p>' % lg
    return out + '</div></div></footer>'


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--g);color:var(--ink);font:400 16px/1.4 "TASA Orbiter",system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased;overflow-x:clip}
img{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
p,h1,h2,h3,h4,ul,dl,dd,blockquote,address{margin:0;padding:0;font-style:normal}
ul{list-style:none}
:focus-visible{outline:3px solid var(--ink);outline-offset:2px;box-shadow:0 0 0 7px var(--g)}
/* hairlines held to the window while the page moves under them */
.lw{position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:0;opacity:.3;mix-blend-mode:multiply}
.lw.f{z-index:3;opacity:.2;mix-blend-mode:color-dodge}
.lw i{position:absolute;background:var(--ln);width:1px;height:120vh;top:-10vh}
.lw i:nth-child(1){left:24%;transform:rotate(-20deg)}
.lw i:nth-child(2){left:48%;transform:rotate(20deg)}
.lw i:nth-child(3){left:65.9%}
.lw i:nth-child(4){width:120vw;height:1px;left:-10vw;top:6vh;transform:rotate(20deg)}
.pg{position:relative}
/* the front lines brighten a streak through white type on the accent (4.0:1 measured), so accent grounds and buttons stand above them */
.ubar,.hp,.ft,.b{z-index:4}
.ubar{position:relative}
/* type */
h1{font-weight:700;font-size:var(--h1,86.4px);line-height:.9;letter-spacing:-.03em;overflow-wrap:break-word}
h2{font-weight:600;font-size:60px;line-height:1;overflow-wrap:break-word}
.h3{font-weight:700;font-size:43.2px;line-height:1;letter-spacing:0;overflow-wrap:break-word}
.h4{font-weight:700;font-size:30.67px;line-height:1.2;overflow-wrap:break-word}
.ey{font-weight:700;font-size:19.2px;line-height:1.2;text-transform:uppercase;color:var(--ey)}
.sub{font-size:20px;line-height:28px}
.sub.ind{text-indent:40px}
.bd{font-size:16px;line-height:22.4px}
.sm{font-size:14px;line-height:19.6px}
.tl{display:inline-block;margin-right:24px;text-decoration:underline;text-underline-offset:3px;overflow-wrap:anywhere}
a:not(.b):not(.ub):hover{text-decoration:underline;text-underline-offset:3px}
/* the button */
.b,.ub{position:relative;display:inline-flex;align-items:stretch;min-height:52px;padding-left:16px;overflow:clip;background:var(--acc);color:var(--on);font-weight:700;font-size:18.4px;line-height:1.4;max-width:100%}
.b .bi,.ub .bi{display:flex;align-items:stretch;gap:16px;transition:transform .3s cubic-bezier(.2,.8,.2,1);min-width:0}
.bt{align-self:center;padding:8px 0}
.tri{width:32px;height:auto;min-height:100%;flex:none;display:block}
.b2{position:absolute;left:0;top:0;bottom:0;width:40px;display:flex;transform:translateX(-48px);transition:transform .3s cubic-bezier(.2,.8,.2,1)}
.b2 .tri{width:40px}
.b.inv{background:var(--g);color:var(--inv)}
.b.dkb{background:var(--dk);color:var(--ond)}
.b.gr{background:var(--g);color:var(--ink)}
@media(hover:hover){.b:hover .b2,.ub:hover .b2{transform:none}.b:hover .bi,.ub:hover .bi{transform:translateX(48px)}
 .b.inv:hover{background:var(--dk);color:var(--ond)}}
.b:active,.ub:active{filter:brightness(.92)}
/* bar and header */
.ubar{min-height:32px;flex-wrap:wrap;background:var(--acc);color:var(--on);display:flex;justify-content:flex-end;align-items:stretch;font-weight:700;font-size:14px;line-height:1}
.ubar .ul{display:flex;align-items:center;padding:0 16px}
.ub{min-height:32px;font-size:14px;background:var(--dk);color:var(--ond);align-items:stretch}
.ub .tri{width:24px}.ub .b2{width:24px;transform:translateX(-32px)}
@media(hover:hover){.ub:hover .bi{transform:translateX(32px)}}
.hd{position:relative;min-height:88px;display:flex;justify-content:space-between;align-items:center;gap:32px;padding:8px 24px 8px 56px}
.lg{font-weight:800;font-size:23px;line-height:.92;letter-spacing:-.01em;text-transform:uppercase;max-width:9.5em;color:var(--ink)}
.lg.im img{max-height:64px;width:auto}
.nv{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:0 24px}
.nv a{font-weight:500;font-size:19.2px;line-height:1.1;padding:8px 0}
.nv a:hover{color:var(--ey);text-decoration:none}
.mn{display:none}
/* opening panel */
.hero{padding:12px 24px 0}
.hp{position:relative;background:var(--acc);color:var(--on);min-height:750px;padding:32px 24px 56px 43.2px;display:flex;flex-direction:column;justify-content:space-between;gap:48px;overflow:hidden}
.ht{display:flex;flex-direction:column;gap:23px;max-width:1040px;position:relative;z-index:1}
.hpc .ht{max-width:43%}
.hpc.sh1 .ht,.hpc.sh1 .hb{max-width:33%}
.hp .ey{color:var(--on)}
.ht .sub{max-width:660px}
.hb{position:relative;z-index:1;display:flex;flex-direction:column;gap:16px;max-width:44%}
.hp:not(.hpc) .hb{max-width:none}
.hp:not(.hpc){min-height:600px}
.bs{display:flex;flex-wrap:wrap;gap:12px}
.pv{position:relative;overflow:hidden}
.pv img{width:100%;height:100%;object-fit:cover}
.hpic{position:absolute;top:0;right:0;bottom:0;width:min(54%,var(--nw));clip-path:polygon(9% 0,100% 0,100% 100%,0 100%)}
.sh1 .hpic{width:min(64%,var(--nw))}
h1{animation:up .6s cubic-bezier(.2,.7,.2,1) both}
@keyframes up{from{opacity:0;transform:translateY(9px)}}
/* the line of standing facts */
.tr{display:flex;flex-wrap:wrap;gap:10px 40px;padding:32px 24px 0}
.tr li{font-weight:700;font-size:19.2px;line-height:1.2;text-transform:uppercase;color:var(--ey)}
/* picture rows */
.rows{padding:64px 0 32px;display:flex;flex-direction:column;gap:64px}
.row,.sr{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:32px;align-items:center}
.row .tx,.sr .tx{display:flex;flex-direction:column;align-items:flex-start;gap:24px;padding:47px 0 47px 24px}
.pv.bleed{aspect-ratio:var(--a);width:100%;max-width:var(--nw);justify-self:end}
.row.r60{grid-template-columns:minmax(0,60fr) minmax(0,40fr)}
.row.r60 .pv{order:-1;justify-self:start}
.row.r60 .tx{padding:47px 24px 47px 0}
.row.np,.row.r60.np{grid-template-columns:minmax(0,1fr)}
.row.np .tx,.row.r60.np .tx{padding:0 24px;max-width:960px}
.ppl{display:grid;gap:14px}
.ppl li,.tg li{display:flex;flex-direction:column;gap:2px;font-size:16px;line-height:22.4px}
.ppl b,.tg b{font-weight:700}
/* sections on the ground */
.sec{padding:96px 0}
.sh{padding:0 24px;display:flex;flex-direction:column;gap:16px;margin-bottom:60px}
.sh .sub{max-width:900px}
.gt{padding:0 24px;margin:48px 0 20px}
.tg{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:48px 8px;padding:0 24px}
.tp{aspect-ratio:1;max-width:var(--nw);margin-bottom:10px;overflow:hidden}
.tp img{width:100%;height:100%;object-fit:cover}
/* slanted colour bands */
.band{position:relative;padding:116px 0 96px}
.band::before{content:"";position:absolute;inset:0;background:var(--tint);clip-path:polygon(0 0,100% 44px,100% 100%,0 calc(100% - 50px))}
.band.dark{color:var(--ond)}
.band.dark::before{background:var(--dk);clip-path:polygon(0 40px,100% 0,100% calc(100% - 44px),0 100%)}
.band>*{position:relative}
.bw{display:grid;grid-template-columns:minmax(0,1fr);align-items:center}
.bpc .bw{grid-template-columns:minmax(0,617fr) minmax(0,823fr)}
.fg{display:grid;gap:36px;padding:0 32px 0 60px}
.figs:not(.bpc) .fg{grid-template-columns:repeat(2,minmax(0,1fr));gap:56px 48px;padding:0 60px}
.fg li{display:flex;flex-direction:column;gap:10px}
.fg b{font-weight:700;font-size:64px;line-height:1;letter-spacing:-.01em;overflow-wrap:anywhere}
.fg span{font-size:20px;line-height:28px;max-width:520px}
.bp{aspect-ratio:823/673;min-height:100%;max-width:var(--nw);width:100%;justify-self:end;clip-path:polygon(10% 0,100% 4%,100% 100%,0 95%)}
/* the catalogue */
.cg+.cg,.strip+.cg{margin-top:96px}
.gh{padding:0 24px;margin-bottom:28px;display:flex;flex-direction:column;gap:12px}
.srs{display:flex;flex-direction:column;gap:32px}
.sr .tx{gap:16px;padding:16px 24px 16px 24px}
.sr .tx .h3{margin-bottom:8px}
.sr .b{margin-top:16px}
.pr{font-weight:700;font-size:19.2px;line-height:1.2;color:var(--ey)}
.nt,.stt{font-size:14px;line-height:19.6px}
.stt{font-weight:700;text-transform:uppercase}
.bl{display:grid;gap:10px;padding-left:24px;list-style:disc;font-size:16px;line-height:22.4px}
.pl{display:grid;gap:6px;font-size:16px;line-height:22.4px;width:100%;max-width:440px}
.pl div{display:flex;justify-content:space-between;gap:24px}
.pl dd{font-weight:700;text-align:right}
.ccs{gap:56px 32px}
.srs+.ccs{margin-top:72px}
.ccs+.cl2{margin-top:72px}
.cc .cp{aspect-ratio:3/2}
.cc .h4{margin-bottom:-4px}
.more{width:100%}
.more summary{display:flex;gap:14px;align-items:flex-start;cursor:pointer;list-style:none}
.more summary::-webkit-details-marker{display:none}
.more .plus{width:18px;height:18px;margin-top:2px}.more .plus::before,.more .plus::after{width:18px;top:8px}
.more[open] .plus{transform:rotate(45deg)}
.more summary:hover .bd{color:var(--ey)}
.mo{display:grid;gap:10px;padding:12px 0 0 32px}
.cl2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:56px 80px;padding:0 24px}
.srs+.cl2{margin-top:72px}
.cl2 article{display:flex;flex-direction:column;align-items:flex-start;gap:12px}
.tl2::after{content:"";display:inline-block;width:.42em;height:.68em;margin-left:.3em;background:var(--acc);clip-path:polygon(0 0,100% 50%,0 100%)}
.cn{padding:0 24px;margin-top:56px;font-weight:700;max-width:900px}
.strip{display:flex;gap:8px;margin-top:96px}
.strip .pv{flex:1 1 0;height:400px;max-width:var(--nw)}
/* cards */
.cards{display:grid;gap:64px 48px;padding:0 24px}
.cards.c1{grid-template-columns:minmax(0,680px)}.cards.c2{grid-template-columns:repeat(2,minmax(0,1fr))}
.cards.c3{grid-template-columns:repeat(3,minmax(0,1fr))}.cards.c4{grid-template-columns:repeat(4,minmax(0,1fr));gap:64px 32px}
.cards article{display:flex;flex-direction:column;align-items:flex-start;gap:14px}
.cards .ey{font-size:16px}
.cards .b{margin-top:10px}
.cards .h4 small{font-size:16px;font-weight:400}
.cp{aspect-ratio:3/2;width:100%;max-width:var(--nw);overflow:hidden;margin-bottom:16px}
.cp img{width:100%;height:100%;object-fit:cover}
/* the dark panel: text left, a stack of photographs off the right edge */
.fw{display:grid;grid-template-columns:minmax(0,1fr);align-items:start}
.fpc .fw{grid-template-columns:minmax(0,786fr) minmax(0,654fr)}
.fl{display:flex;flex-direction:column;gap:20px;padding:48px 48px 32px;max-width:1100px}
.fpc .fl{max-width:656px}
.vl{display:grid;gap:14px;padding-left:24px;list-style:disc;font-size:16px;line-height:22.4px;margin-top:8px}
.feat:not(.fpc) .vl{grid-template-columns:repeat(2,minmax(0,1fr));gap:20px 64px}
.fs{display:flex;flex-direction:column;gap:2px;margin:-131px 0 -111px}
.fs .pv{aspect-ratio:var(--a);width:100%;max-width:var(--nw);align-self:flex-end}
.fs .pv:first-child{clip-path:polygon(0 0,100% 34px,100% 100%,0 100%)}
.fs .pv:last-child{clip-path:polygon(0 0,100% 0,100% calc(100% - 36px),0 100%)}
.fs .pv:only-child{clip-path:polygon(0 0,100% 34px,100% calc(100% - 36px),0 100%)}
/* voices */
.qw{display:grid;grid-template-columns:minmax(0,1fr);align-items:center}
.qpc .qw{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
.qp{aspect-ratio:1;width:100%;max-width:var(--nw);clip-path:polygon(0 3%,93% 0,100% 100%,0 100%);margin:-60px 0 -40px}
.ql{display:grid;gap:40px;padding:24px 48px}
.quo:not(.qpc) .ql{grid-template-columns:repeat(2,minmax(0,1fr));gap:48px 64px}
.ql p{font-size:19.2px;line-height:26.9px}
.ql footer{margin-top:14px;font-size:16px}
/* reach us · questions */
.cfw{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:80px;padding:0 24px;align-items:start}
.cfw.one{grid-template-columns:minmax(0,900px)}
.ct{display:flex;flex-direction:column;align-items:flex-start;gap:16px}
.big{font-weight:600;font-size:60px;line-height:1}
.mid{font-weight:700;font-size:30.67px;line-height:1.2;overflow-wrap:anywhere}
.rt{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px 32px;margin-top:24px;width:100%;font-size:16px;line-height:22.4px}
.rt li{display:flex;flex-direction:column;overflow-wrap:anywhere}
.rt a{text-decoration:underline;text-underline-offset:3px}
.fq .h3{margin-bottom:36px}
.qs{display:grid;gap:32px}
.q summary{display:flex;gap:32px;align-items:flex-start;cursor:pointer;list-style:none}
.q summary::-webkit-details-marker{display:none}
.plus{position:relative;flex:none;width:32px;height:32px;transition:transform .4s cubic-bezier(.2,.7,.2,1)}
.plus::before,.plus::after{content:"";position:absolute;left:0;top:15px;width:32px;height:2px;background:var(--ey)}
.plus::after{transform:rotate(90deg)}
.q[open] .plus{transform:rotate(45deg)}
.qt{font-size:24px;line-height:31.2px;transition:color .2s}
.q summary:hover .qt{color:var(--ey)}
.an{padding:20px 0 0 64px;display:grid;gap:12px;font-size:16px;line-height:22.4px;overflow:hidden}
/* the dark band above the foot */
.apply{position:relative;background:var(--dk);color:var(--ond);padding:80px 48px 110px;display:grid;gap:72px}
.ag{display:grid;gap:56px 80px}
.ag.c2{grid-template-columns:repeat(2,minmax(0,1fr))}.ag.c3{grid-template-columns:repeat(3,minmax(0,1fr))}
.ag article,.ag li{display:flex;flex-direction:column;align-items:flex-start;gap:14px}
.ah{color:var(--hl);font-weight:600;font-size:43.2px;line-height:1}
.apply address{display:flex;flex-direction:column;font-weight:700;font-size:16px;line-height:22.4px}
.apply .pl dd{font-weight:400}
.cr b{font-size:20px;line-height:28px;font-weight:700}
.badge{width:auto;height:auto;max-height:112px}
.apply :focus-visible,.band.dark :focus-visible{outline-color:var(--ond);box-shadow:0 0 0 7px var(--dk)}
/* foot */
.ft{position:relative;background:var(--acc);color:var(--on);margin-top:-30px;padding:102px 16px 14px;clip-path:polygon(0 30px,100% 4px,100% 100%,0 100%)}
.ft .top{position:absolute;right:16px;top:44px;font-size:19.2px;line-height:1.4;padding:0 8px}
.fgd{display:grid;grid-template-columns:minmax(0,536fr) minmax(0,872fr);gap:0;min-height:520px}
.fa{display:flex;flex-direction:column;justify-content:space-between;gap:40px;padding:20px 32px 46px 0}
.fl2{color:var(--on);font-size:27px}
.fad{font-size:16px;line-height:22.4px;max-width:300px}
.fb{display:flex;flex-direction:column;align-items:flex-start}
.fh{font-weight:700;font-size:var(--fh);line-height:1;letter-spacing:-.03em;color:var(--ftc);margin:20px 0 40px;overflow-wrap:break-word}
.fh .w{display:inline-block}
.js .fh .w{opacity:0;transform:scale(.8);transition:opacity 1s cubic-bezier(.3,.6,.3,1),transform 1s cubic-bezier(.3,.6,.3,1);transition-delay:calc(var(--i)*120ms)}
.js .fh.in .w{opacity:1;transform:none}
.fb .sub{max-width:872px}
.fb .b{margin-top:80px}
.fb .sub+.sub{margin-top:14px}
.fl{list-style:none}
ul.fl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px 40px;margin-top:48px;width:100%;padding:0}
ul.fl li{display:flex;flex-direction:column;gap:2px}
.ft1{font-weight:500;font-size:20px;line-height:28px}
ul.fl span{font-size:14px;line-height:19.6px}
.lgl{display:flex;flex-wrap:wrap;gap:6px 24px;margin-top:44px;font-size:14px;line-height:19.6px}
.ft :focus-visible{outline-color:var(--on);box-shadow:0 0 0 7px var(--acc)}
.hp :focus-visible,.ubar :focus-visible{outline-color:var(--on);box-shadow:0 0 0 7px var(--acc)}

@media(max-width:1100px){
 .nv{display:none}
 .mn{display:block}
 .mn summary{position:relative;z-index:3001;display:inline-flex;align-items:stretch;min-height:44px;background:var(--acc);color:var(--on);font-weight:500;font-size:19.2px;cursor:pointer;list-style:none}
 .mn summary::-webkit-details-marker{display:none}
 .mn .ms{display:flex;width:27px}.mn .ms .tri{width:27px}
 .mn .mt{align-self:center;padding:0 14px 0 12px}
 .mn[open] summary{background:var(--g);color:var(--inv)}
 .mp{position:absolute;z-index:3000;left:0;right:0;top:0;min-height:100vh;background:var(--acc);color:var(--on);padding:96px 16px 40px;display:flex;flex-direction:column;align-items:flex-start;gap:14px;animation:slide .4s cubic-bezier(.2,.7,.2,1)}
 .mp a:not(.b){font-weight:500;font-size:28px;line-height:1.15}
 .mp .b{margin-top:20px}
 @keyframes slide{from{transform:translateX(100%)}}
 .cards.c4,.cards.c3{grid-template-columns:repeat(2,minmax(0,1fr))}
 .tg{grid-template-columns:repeat(3,minmax(0,1fr))}
}
@media(max-width:760px){
 h1{font-size:var(--h1m,40px)}
 h2{font-size:34px}
 .h3{font-size:28px}
 .h4{font-size:22px}
 .ey,.tr li{font-size:13.6px}
 .sub{font-size:16px;line-height:22.4px}
 .sub.ind{text-indent:24px}
 .b{font-size:16px;min-height:44px}
 .ubar{min-height:28px;font-size:12.8px}
 .ubar .ul{padding:0 10px}
 .ub{min-height:28px;font-size:12.8px;padding-left:10px}
 .hd{min-height:76px;padding:8px 8px 8px 16px}
 .lg{font-size:17px}
 .hero{padding:2px 8px 0}
 .hp{min-height:0;padding:28px 17.6px 28px;gap:28px}
 .hpc{padding-bottom:0}
 .hpc .ht,.hb,.hpc.sh1 .ht,.hpc.sh1 .hb{max-width:none}
 .ht{gap:18px}
 .hpic,.sh1 .hpic{position:relative;width:auto;max-width:none;margin:8px -17.6px 0;height:320px;clip-path:polygon(0 9%,100% 0,100% 100%,0 100%)}
 .tr{padding:24px 8px 0;gap:8px 24px}
 .rows{padding:40px 0 20px;gap:40px}
 .row,.sr,.row.r60{grid-template-columns:minmax(0,1fr);gap:16px}
 .row .pv,.sr .pv{order:-1;max-height:150vw}
 .row .tx,.sr .tx,.row.r60 .tx{padding:0 8px;gap:16px}
 .row.np .tx,.row.r60.np .tx{padding:0 8px}
 .sec{padding:56px 0}
 .sh,.gh,.gt,.cn{padding:0 8px}
 .sh{margin-bottom:32px}
 .tg{grid-template-columns:repeat(2,minmax(0,1fr));padding:0 8px;gap:32px 8px}
 .band{padding:72px 0 64px}
 .band::before{clip-path:polygon(0 0,100% 24px,100% 100%,0 calc(100% - 26px))}
 .band.dark::before{clip-path:polygon(0 22px,100% 0,100% calc(100% - 24px),0 100%)}
 .bpc .bw,.fpc .fw,.qpc .qw{grid-template-columns:minmax(0,1fr)}
 .fg,.figs:not(.bpc) .fg{grid-template-columns:minmax(0,1fr);padding:0 18px;gap:28px}
 .fg b{font-size:34px}
 .fg span{font-size:16px;line-height:22.4px}
 .bp{margin-top:36px;aspect-ratio:4/3;clip-path:polygon(4% 0,100% 5%,100% 100%,0 96%)}
 .cg+.cg,.strip+.cg{margin-top:56px}
 .srs{gap:44px}
 .sr .tx .h3{margin-bottom:0}
 .cl2{grid-template-columns:minmax(0,1fr);gap:36px;padding:0 8px}
 .srs+.cl2,.srs+.ccs,.ccs+.cl2{margin-top:48px}
 .cards.ccs,.cards.ccs.c3,.cards.ccs.c4{grid-template-columns:repeat(2,minmax(0,1fr));gap:36px 12px}
 .cards.ccs.c2:has(> :only-child){grid-template-columns:minmax(0,1fr)}
 .cc{gap:8px}
 .cc .cp{margin-bottom:6px}
 .cc .h4{font-size:19.2px;margin-bottom:0}
 .cc .pr{font-size:16px}
 .cc .bd,.cc .bl,.cc .pl{font-size:14px;line-height:19.6px}
 .more summary{gap:8px}
 .more .plus{width:14px;height:14px}.more .plus::before,.more .plus::after{width:14px;top:6px}
 .mo{padding-left:0}
 .cc .b{font-size:14px;min-height:40px;padding-left:10px}.cc .b .tri{width:24px}.cc .b .bi{gap:10px}
 .strip{gap:4px;margin-top:56px}
 .strip .pv{height:150px}
 .cards,.cards.c2,.cards.c3,.cards.c4{grid-template-columns:minmax(0,1fr);gap:40px;padding:0 8px}
 .fl{padding:8px 18px 8px}
 .feat:not(.fpc) .vl{grid-template-columns:minmax(0,1fr)}
 .fs{margin:36px 12px -40px}
 .fs .pv:first-child,.fs .pv:last-child,.fs .pv:only-child{clip-path:none}
 .qp{margin:-30px 0 28px;clip-path:polygon(0 3%,100% 0,100% 100%,0 97%)}
 .ql,.quo:not(.qpc) .ql{grid-template-columns:minmax(0,1fr);padding:0 18px;gap:32px}
 .ql p{font-size:16px;line-height:22.4px}
 .cfw{grid-template-columns:minmax(0,1fr);gap:56px;padding:0 8px}
 .big{font-size:34px}.mid{font-size:20px}
 .rt{grid-template-columns:minmax(0,1fr)}
 .q summary{gap:16px}
 .plus{width:24px;height:24px}.plus::before,.plus::after{width:24px;top:11px}
 .qt{font-size:19.2px;line-height:25px}
 .an{padding-left:40px}
 .apply{padding:56px 18px 84px;gap:48px}
 .ag,.ag.c2,.ag.c3{grid-template-columns:minmax(0,1fr);gap:40px}
 .ah{font-size:30px}
 .ft{padding:84px 11px 14px}
 .ft .top{top:40px;right:8px;font-size:16px}
 .fgd{grid-template-columns:minmax(0,1fr);min-height:0}
 .fa{padding:0 0 28px;gap:16px}
 .fh{font-size:var(--fhm);margin:8px 0 20px}
 .fb .b{margin-top:32px}
 ul.fl{grid-template-columns:repeat(2,minmax(0,1fr));gap:18px 16px;margin-top:36px}
 .ft1{font-size:16px;line-height:22.4px}
 .lgl{margin-top:36px}
}
@media(prefers-reduced-motion:reduce){
 html{scroll-behavior:auto}
 *,*::before,*::after{animation:none!important;transition:none!important}
 .js .fh .w{opacity:1;transform:none}
}
"""

JS = r"""
(function(){var R=matchMedia('(prefers-reduced-motion: reduce)').matches,D=document;
D.documentElement.classList.add('js');
var fh=D.querySelector('.fh');
if(fh){[].forEach.call(fh.querySelectorAll('.w'),function(w,i){w.style.setProperty('--i',i)});
 if(R||!('IntersectionObserver' in window))fh.classList.add('in');
 else new IntersectionObserver(function(en,o){en.forEach(function(x){if(x.isIntersecting){fh.classList.add('in');o.disconnect()}})},{threshold:.2}).observe(fh);}
[].forEach.call(D.querySelectorAll('details.q'),function(q){var s=q.querySelector('summary'),a=q.querySelector('.an');
 if(R||!a.animate)return;
 s.addEventListener('click',function(ev){ev.preventDefault();
  if(q.open){var h=a.offsetHeight;q.classList.add('cl');a.animate([{height:h+'px'},{height:'0px',paddingTop:'0px'}],{duration:400,easing:'cubic-bezier(.2,.7,.2,1)'}).onfinish=function(){q.open=false;q.classList.remove('cl')};}
  else{q.open=true;var h2=a.offsetHeight;a.animate([{height:'0px',paddingTop:'0px'},{height:h2+'px'}],{duration:400,easing:'cubic-bezier(.2,.7,.2,1)'});}
 });});
var mn=D.querySelector('details.mn');
if(mn){mn.addEventListener('click',function(ev){if(ev.target.closest&&ev.target.closest('.mp a'))mn.open=false});
 D.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&mn.open){mn.open=false;mn.querySelector('summary').focus()}});}
})();
"""


def render(d: dict) -> str:
    c = colours(d.get('palette') or {})
    pool = Pool(d)
    brand = d.get('brand') or {}
    hero = d.get('hero') or {}
    # the order the pool is drawn in is the order of the slots' weight, not of the page
    head = s_head(d, c)
    s1 = s_hero(d, pool)
    s3 = s_rows(d, pool)
    s4 = s_figures(d, pool)
    s6 = s_features(d, pool)
    s8 = s_quotes(d, pool)
    s5 = s_catalogue(d, pool)
    body = (head + '<main>' + s1 + s_trust(d) + s3 + s_team_grid(d, pool) + s4 + s5 + s_plans(d) + s6 + s_steps(d, pool) + s8
            + s_contact_faq(d) + s_places(d, pool) + '</main>' + s_foot(d))
    var = ('--g:%(g)s;--ink:%(ink)s;--acc:%(acc)s;--on:%(on)s;--dk:%(dk)s;--ond:%(ond)s;--tint:%(tint)s;--ey:%(ey)s;'
           '--hl:%(hl)s;--ftc:%(ft)s;--ln:%(ln)s;--inv:%(inv)s') % c
    title = ' — '.join(x for x in [brand.get('name'), hero.get('kicker') or hero.get('title')] if x)
    desc = hero.get('text') or (d.get('statement') or {}).get('text') or ''
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="%s"><style>:root{%s}%s</style></head>'
            '<body id="top"><div class="lw" aria-hidden="true"><i></i><i></i><i></i><i></i></div>'
            '<div class="pg">%s</div><div class="lw f" aria-hidden="true"><i></i><i></i><i></i><i></i></div>'
            '<script>%s</script></body></html>') % (e(d.get('lang') or 'en'), e(title), e(desc[:300]), FONTS, var, CSS, body, JS)
