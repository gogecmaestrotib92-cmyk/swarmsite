"""woodwrights/render.py — one pure function: render(d) -> a complete page.
A template for MAKERS and small SHOPS led by their own photographs (kind: service | shop | ...).

The build (section order, the 40 px margin and the columns at 40 / 612 / 955 and 720 / 728, type scale, spacing, the
header that leaves on the way down and returns on the way up, the sticky caption and sticky picture, the numbered list
that swaps its text and widens its picture, the phone build) was measured on the reference's home page at 1440 and 390
on 2026-11-12 (see NOTES.md). Nothing of the reference's code, words, pictures, logo or typefaces is here. The client's
data fills it; a section whose data is missing is left out whole. No model call, no file reads, no client logic.
"""
import html

FONTS = ('https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@300;400&'
         'family=Newsreader:opsz,wght@6..72,500&display=swap')
WORDS = {  # accessible names only (never visible): the data has no words for these controls
    'en': ('Menu', 'Close'), 'de': ('Menü', 'Schließen'), 'fr': ('Menu', 'Fermer'), 'es': ('Menú', 'Cerrar'),
    'it': ('Menu', 'Chiudi'), 'pt': ('Menu', 'Fechar'), 'sr': ('Meni', 'Zatvori'), 'nl': ('Menu', 'Sluiten'),
}
LIGHT = '#fbfbf9'   # ink over a veiled photograph


# ───────────────────────── colour: the reference's relations (near-white ground, a warm tint band, a deeper tint bar)
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
    g = p.get('ground') or '#fbfbf9'
    ink = p.get('ink') or '#262525'
    acc = p.get('accent') or ink
    pole = '#000000' if _lum(g) > .3 else '#ffffff'
    band = _mix(acc, g, .14)      # reference: ground 251,251,249 → band 232,223,208
    bar = _mix(acc, g, .28)       # reference: announcement bar 210,197,183
    head = _mix(acc, g, .05)      # reference: header on the way up 244,242,236
    t = 0.0
    while t < 1 and min(_con(_mix(pole, ink, t), x) for x in (g, band, bar, head)) < 7:
        t += .04
    ink = _mix(pole, ink, min(t, 1))
    soft, t = _mix(ink, g, .62), 0.0   # reference: copyright line at half strength
    while t < 1 and min(_con(_mix(ink, soft, t), x) for x in (g, band)) < 4.6:
        t += .04
    soft = _mix(ink, soft, min(t, 1))
    return dict(g=g, ink=ink, band=band, bar=bar, head=head, soft=soft, line=_mix(ink, g, .22))


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def m(src):
    return src if not src or src.startswith(('http:', 'https:', 'data:', '/')) else '../../' + src


def _a(link, cls='', inner=None, extra=''):
    """A link from {t,h}; returns '' when there is nothing to say."""
    if not link or not (inner or link.get('t')):
        return ''
    c = f' class="{cls}"' if cls else ''
    body = inner or e(link.get('t'))
    if not link.get('h'):
        return f'<span{c}{extra}>{body}</span>'
    return f'<a{c} href="{e(link["h"])}"{extra}>{body}</a>'


def _img(ph, cls='', sizes='100vw', eager=False, slot=''):
    if not ph:
        return ''
    wh = f' width="{ph["w"]}" height="{ph["h"]}"' if ph.get('w') and ph.get('h') else ''
    ld = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ''
    s = f' data-slot="{slot}"' if slot else ''
    return f'<img{c}{s} src="{e(m(ph["src"]))}" alt="{e(ph.get("alt") or "")}"{wh}{ld}>'


def _paras(text, cls=''):
    c = f' class="{cls}"' if cls else ''
    return ''.join(f'<p{c}>{e(t.strip())}</p>' for t in str(text or '').split('\n') if t.strip())


class _Pictures:
    """The client's photographs, chosen for a slot by role, size and proportion; each is used once."""

    def __init__(self, d):
        self.all = [p for p in ((d.get('media') or {}).get('photos') or []) if p.get('src')]
        self.by = {p['src']: p for p in self.all}
        self.used = set()
        own = []   # pictures that belong to a named thing are kept for it
        for it in ((d.get('steps') or {}).get('items') or []):
            own.append(it.get('img'))
        for grp in ((d.get('catalogue') or {}).get('groups') or []):
            own.append(grp.get('img'))
            own += [it.get('img') for it in (grp.get('items') or [])]
        for it in _people(d):
            own.append(it.get('img'))
        for pr in (d.get('projects') or []):
            own += [x if isinstance(x, str) else (x or {}).get('src') for x in (pr.get('photos') or [])]
        for sp in ((d.get('place') or {}).get('spaces') or []):
            own.append(sp.get('img'))
        self.own = {x for x in own if x}

    @staticmethod
    def fits(p, w, h, limit=1.3):
        """Can p fill a w×h slot (cover) without being enlarged past its pixels (1.3× for a picture that is not small)?"""
        if not p.get('w') or not p.get('h'):
            return False
        return max(w / p['w'], h / p['h']) <= (1.0 if p.get('small') else limit)

    def named(self, src, w=0, h=0):
        """A picture the data names for a thing (a step, a product, a person): taken once, whatever its role."""
        if not src or src in self.used:
            return None
        self.used.add(src)
        return self.by.get(src) or {'src': src, 'alt': ''}

    def take(self, w, h, roles=None, never=('portrait',), prefer=None):
        pool = [p for p in self.all if p['src'] not in self.used and p['src'] not in self.own
                and p.get('role') not in never and self.fits(p, w, h)]
        if roles:
            first = [p for p in pool if p.get('role') in roles]
            pool = first + [p for p in pool if p not in first] if roles[-1] != '!' else first
        if prefer and pool:
            pool = sorted(pool, key=lambda p: (0 if roles and p.get('role') in roles else 1, prefer(p)))   # stable: the client's own order decides ties
        if not pool:
            return None
        self.used.add(pool[0]['src'])
        return pool[0]


def _people(d):
    t = d.get('team') or {}
    out = list(t.get('items') or [])
    for g in (t.get('groups') or []):
        out += list(g.get('items') or [])
    return [p for p in out if p.get('name')]


def _addr(a):
    a = a or {}
    l1 = a.get('street') or ''
    l2 = ' '.join(x for x in (a.get('postcode'), a.get('city')) if x)
    if a.get('city') and a.get('postcode') and (a.get('country') or '').lower() in ('', 'uk', 'gb', 'united kingdom'):
        l2 = ', '.join(x for x in (a.get('city'), a.get('region')) if x) + ' ' + a['postcode']
    elif a.get('region'):
        l2 = ', '.join(x for x in (l2, a['region']) if x)
    return [x for x in (l1, l2.strip(), a.get('country')) if x]


def _hours(hs):
    out = []
    for h in hs or []:
        span = '–'.join(x for x in (h.get('open'), h.get('close')) if x)
        if h.get('days') or span:
            out.append(f'<li><span>{e(h.get("days") or "")}</span><span>{e(span)}</span></li>')
    return out


# ───────────────────────── the page
def render(d: dict) -> str:
    th = _theme(d.get('palette') or {})
    lang = (d.get('lang') or 'en')[:2]
    w_menu, w_close = WORDS.get(lang, WORDS['en'])
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    hero = d.get('hero') or {}
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    cta = d.get('cta') or hero.get('primary') or {}
    place = d.get('place') or {}
    contact = d.get('contact') or {}
    foot = d.get('foot') or {}
    pics = _Pictures(d)
    steps = d.get('steps') or {}
    step_items = [s for s in (steps.get('items') or []) if s.get('title') or s.get('k') or s.get('text')]
    cat = d.get('catalogue') or {}
    groups = [g for g in (cat.get('groups') or []) if g.get('items') or g.get('t')]
    priced = any(it.get('price') or it.get('prices') for g in groups for it in (g.get('items') or []))
    projects = [p for p in (d.get('projects') or []) if p.get('title')]

    # ── pictures for the slots that take a free photograph (order = importance)
    wide = lambda p: (0 if p['w'] >= 1600 and p['w'] > p['h'] else 1)
    p_hero = pics.take(1440, 1121, never=('portrait', 'people'), prefer=wide)
    upright = lambda p: (0 if p['h'] > p['w'] else 1, -min(p['h'], 1400))
    p_tall = pics.take(672, 908, never=('portrait', 'people'), prefer=upright)
    big = lambda p: 0 if p['w'] >= 1440 and p['w'] > p['h'] else 1
    statement = d.get('statement') or {}
    has_statement = bool(statement.get('title') or statement.get('text'))
    p_state = p_state_print = None
    if has_statement:
        p_state = pics.take(1440, 773, roles=('workshop', 'room', 'exterior', 'detail', 'landscape', 'bar'),
                            never=('portrait', 'people'), prefer=big)
        if not p_state:
            p_state_print = pics.take(792, 566, roles=('workshop', 'room', 'exterior', 'detail'), never=('portrait',))
    video = (d.get('media') or {}).get('video')
    p_film = None if video else pics.take(1440, 600, never=('portrait', 'people'),
                                          prefer=big)

    out = []

    # ── header (reference: bar 32 + row 60, fixed; clear over the first picture, leaves going down, returns going up)
    solid = not p_hero or bool(brand.get('logo'))
    size = min(24.0, 310 / (.64 * max(len(name), 1)))
    mark = (f'<img src="{e(m(brand["logo"]))}" alt="{e(name)}">' if brand.get('logo') else e(name))
    navh = ''.join(_a(n) for n in nav)
    side = _a(d.get('signin')) + _a(cta)
    bar = f'<p class="bar">{e(hero["kicker"])}</p>' if hero.get('kicker') else ''
    out.append(
        f'<header class="hd{" solid" if solid else ""}{"" if bar else " nobar"}" id="hd">{bar}'
        f'<div class="row"><a class="mark" style="--ms:{size:.1f}px" href="{e(brand.get("home") or "#top")}">{mark}</a>'
        f'<nav class="nav">{navh}</nav><div class="side">{side}</div>'
        + (f'<button class="burger" type="button" aria-label="{e(w_menu)}" aria-expanded="false" aria-controls="menu">'
           f'<i></i><i></i><i></i></button>' if nav else '') + '</div></header>')
    if nav:
        out.append(f'<div class="menu" id="menu" hidden><button class="x" type="button" aria-label="{e(w_close)}"></button>'
                   f'<nav>{navh}{side}</nav></div>')

    # ── 1 first screen (reference: picture 100vh + 221, name 331 wide at 40 / 450, one serif line riding the bottom)
    out.append('<main id="top">')
    h1 = hero.get('title') or name
    if p_hero:
        out.append(
            f'<section class="hero">{_img(p_hero, "bg", eager=True, slot="hero")}<i class="veil"></i>'
            f'<p class="big" aria-hidden="true">{e(name)}</p>'
            f'<div class="track"><h1 class="cap">{e(h1)}</h1></div></section>')
    else:
        out.append(f'<section class="hero plain"><p class="big" aria-hidden="true">{e(name)}</p>'
                   f'<div class="track"><h1 class="cap">{e(h1)}</h1></div></section>')

    # ── 2 opening words · numbered list · upright picture (reference: 454 wide at 40; picture 672×908 at 728)
    lead = hero.get('text') or ''
    links = _a(hero.get('primary'), 'ul') + _a(hero.get('secondary'), 'ul')
    if len(groups) == 1 and not priced:
        rows = [(it.get('name'), it.get('h')) for it in (groups[0].get('items') or []) if it.get('name')]
    else:
        rows = [(g.get('t'), g.get('h')) for g in groups if g.get('t')]
    if not rows:
        rows = [(f.get('t'), None) for f in ((d.get('features') or {}).get('items') or []) if f.get('t')]
    feat = d.get('features') or {}
    l_title = cat.get('title') or (feat.get('title') if rows else '')
    l_text = cat.get('text') or (feat.get('text') if rows else '')
    if lead or rows or links:
        s = '<section class="open"><div class="txt">'
        if lead or links:
            s += '<div class="top">' + _paras(lead, 'lead') + _paras(hero.get('text2'), 'small')
            if links:
                s += f'<p class="links">{links}</p>'
            if hero.get('note'):
                s += f'<p class="small note">{e(hero["note"])}</p>'
            s += '</div>'
        if rows:
            s += '<div class="browse">'
            if l_title:
                s += f'<h2 class="label">{e(l_title)}</h2>'
            if l_text:
                s += _paras(l_text, 'small')
            s += '<ol class="nl">'
            for i, (t, h) in enumerate(rows):
                inner = f'<span>{i + 1:02d}</span><span class="t">{e(t)}</span>'
                s += '<li>' + (f'<a href="{e(h)}">{inner}</a>' if h else f'<div>{inner}</div>') + '</li>'
            s += '</ol></div>'
        s += '</div>'
        if p_tall:
            s += f'<figure class="tall">{_img(p_tall, sizes="47vw", slot="tall")}</figure>'
        out.append(s + '</section>')

    # ── 3 tint band: title · numbered points · the active point's text · a picture per point (reference: "approach")
    if step_items:
        n = len(step_items)
        gap = max(1.2, min(8.26, (94.44 - 25.7 - 12.08 * (n - 1)) / max(n - 1, 1)))
        free = max(0.0, 94.44 - 25.7 - 12.08 * (n - 1) - gap * (n - 1))
        s = f'<section class="band steps" data-tabs style="--gap:{gap:.2f}vw;--free:{free:.2f}vw"><div class="topw">'
        s += '<div class="ttl">' + (f'<h2 class="h22">{e(steps["title"])}</h2>' if steps.get('title') else '')
        s += _paras(steps.get('text'), 'small') + '</div>'
        s += '<ol class="pts">'
        for i, it in enumerate(step_items):
            s += (f'<li><button type="button" class="pt{" on" if i == 0 else ""}" data-i="{i}" aria-pressed="{"true" if i == 0 else "false"}">'
                  f'<span class="no">{i + 1:02d}</span><span class="t">{e(it.get("title") or it.get("k"))}</span></button></li>')
        s += '</ol><div class="descs">'
        for i, it in enumerate(step_items):
            s += (f'<div class="desc{" on" if i == 0 else ""}"><h3 class="label">{e(it.get("title") or it.get("k"))}</h3>'
                  + _paras(it.get('text'), 'serif') + _a(it.get('cta'), 'ul') + '</div>')
        s += '</div></div>'
        shots = [pics.named(it.get('img')) for it in step_items]
        if all(shots):
            s += '<div class="gal">'
            for i, ph in enumerate(shots):
                s += (f'<figure class="gi{" on" if i == 0 else ""}{" end" if i == n - 1 else ""}" data-i="{i}">'
                      f'{_img(ph, sizes="26vw", slot="step")}</figure>')
            s += '</div>'
        out.append(s + '</section>')

    # ── 4 one thing told (reference: picture 792×566 beside a 330 column; owner's rule: the picture carries the section)
    if has_statement:
        body = ((f'<h2 class="h28">{e(statement["title"])}</h2>' if statement.get('title') else '')
                + _paras(statement.get('text'), 'small') + _a(cta, 'ul'))
        if p_state:
            out.append(f'<section class="told over">{_img(p_state, "bg", slot="told")}<i class="veil"></i>'
                       f'<div class="col">{body}</div></section>')
        elif p_state_print:
            wpx = min(792, p_state_print['w']) if p_state_print.get('small') else 792
            out.append(f'<section class="told print"><figure style="--w:{wpx}px;--ar:{p_state_print["w"]}/{p_state_print["h"]}">'
                       f'{_img(p_state_print, slot="told")}</figure><div class="col">{body}</div></section>')
        else:
            out.append(f'<section class="told bare"><div class="col">{body}</div></section>')

    # ── 5 the listed things: head · cards one under another · a sticky upright picture (reference: "featured")
    blocks = []
    if priced:
        for g in groups:
            head = ''
            if cat.get('title'):
                head += f'<p class="label">{e(cat["title"])}</p>'
            if g.get('t'):
                head += '<h2 class="h28">' + (f'<a href="{e(g["h"])}">{e(g["t"])}</a>' if g.get('h') else e(g['t'])) + '</h2>'
            head += _paras(g.get('text'), 'small')
            cards, lines = '', ''
            for it in (g.get('items') or []):
                if not it.get('name'):
                    continue
                price = e(it.get('price') or '')
                if it.get('prices'):
                    price = ' · '.join(f'{e(x.get("label") or "")} {e(x.get("price") or "")}'.strip() for x in it['prices'])
                state = f'<span class="st">{e(it["state"])}</span>' if it.get('state') else ''
                meta = f'<span class="pr">{price}{state}</span>' if price or state else ''
                extra = _paras(it.get('text') or it.get('note'), 'small') + (
                    '<ul class="inc">' + ''.join(f'<li>{e(r)}</li>' for r in it['rows']) + '</ul>' if it.get('rows') else '')
                ph = pics.named(it.get('img'))
                if ph:
                    inner = (f'<figure>{_img(ph, sizes="31vw", slot="item")}</figure>'
                             f'<h3 class="cap12"><span>{e(it["name"])}</span>{meta}</h3>')
                    cards += ('<article class="card">' + (f'<a href="{e(it["h"])}">{inner}</a>' if it.get('h') else inner)
                              + extra + '</article>')
                else:
                    inner = f'<span class="t">{e(it["name"])}</span>{meta}'
                    lines += '<li>' + (f'<a href="{e(it["h"])}">{inner}</a>' if it.get('h') else f'<div>{inner}</div>') + extra + '</li>'
            blocks.append(f'<div class="grp"><div class="head">{head}</div>{cards}'
                          + (f'<ul class="nl priced">{lines}</ul>' if lines else '') + '</div>')
        if cat.get('note'):
            blocks.append(f'<p class="small fine">{e(cat["note"])}</p>')
    if projects:
        cards = ''
        for pr in projects:
            ph = None
            for x in (pr.get('photos') or []):
                ph = pics.named(x if isinstance(x, str) else (x or {}).get('src'))
                if ph:
                    break
            inner = ((f'<figure>{_img(ph, sizes="31vw", slot="project")}</figure>' if ph else '')
                     + f'<h3 class="cap12"><span>{e(pr["title"])}</span></h3>')
            cards += (f'<article class="card{"" if ph else " bare"}">' + (f'<a href="{e(pr["h"])}">{inner}</a>' if pr.get('h') else inner)
                      + _paras(pr.get('text'), 'small') + '</article>')
        blocks.append(f'<div class="grp">{cards}</div>')
    if blocks:
        p_stick = pics.take(680, 820, roles=('product', 'work', 'detail'), never=('portrait', 'people'),
                            prefer=lambda p: abs(p['w'] / p['h'] - .83))
        out.append('<section class="feat' + ('' if p_stick else ' nopic') + '"><div class="left">' + ''.join(blocks) + '</div>'
                   + (f'<figure class="stick">{_img(p_stick, sizes="47vw", slot="stick")}</figure>' if p_stick else '')
                   + '</section>')

    # ── 6 a picture with no words (reference: a film, full width, 1440×1080)
    if video and video.get('src'):
        out.append(f'<section class="film"><video src="{e(m(video["src"]))}"'
                   + (f' poster="{e(m(video["poster"]))}"' if video.get('poster') else '')
                   + (f' width="{video["w"]}" height="{video["h"]}"' if video.get('w') and video.get('h') else '')
                   + f' muted loop playsinline autoplay preload="metadata" aria-label="{e(video.get("alt") or "")}"></video></section>')
    elif p_film:
        out.append(f'<section class="film" style="--ar:{p_film["w"]}/{p_film["h"]}">{_img(p_film, slot="film")}</section>')

    # ── what clients say (not on the reference's home page: its tint band and its three columns at 40 / 497 / 955)
    quotes = [q for q in (d.get('quotes') or []) if q.get('q')]
    if quotes:
        s = '<section class="band says"><div class="cols3">'
        for q in quotes:
            who = ''.join(f'<span>{e(x)}</span>' for x in (q.get('name'), q.get('role')) if x)
            s += f'<figure><blockquote class="serif">{e(q["q"])}</blockquote>' + (f'<figcaption class="label">{who}</figcaption>' if who else '') + '</figure>'
        out.append(s + '</div></section>')

    # ── the people (the reference's "visit" part: label and serif words at 40, upright pictures from 613)
    people = _people(d)
    team = d.get('team') or {}
    if people:
        n = len(people)
        s = '<section class="visit team"><div class="say">'
        if team.get('title'):
            s += f'<h2 class="label">{e(team["title"])}</h2>'
        s += _paras(team.get('text'), 'serif20') + f'</div><div class="who n{min(n, 3)}">'
        for p in people:
            ph = pics.named(p.get('img'))
            ar = ''
            if ph and ph.get('w') and ph.get('h'):
                ar = f' style="--ar:{max(389 / 540, min(1.5, ph["w"] / ph["h"])):.3f}"'
            reach = ''.join(x for x in (
                _a(p.get('phone') if isinstance(p.get('phone'), dict) else ({'t': p['phone'], 'h': 'tel:' + str(p['phone']).replace(' ', '')} if p.get('phone') else None)),
                (f'<a href="mailto:{e(p["email"])}">{e(p["email"])}</a>' if p.get('email') else '')))
            s += ('<article>' + (f'<figure{ar}>{_img(ph, sizes="27vw", slot="person")}</figure>' if ph else '')
                  + f'<h3 class="label">{e(p["name"])}</h3>' + (f'<p class="role">{e(p["role"])}</p>' if p.get('role') else '')
                  + _paras(p.get('text'), 'small') + (f'<p class="small reach">{reach}</p>' if reach else '') + '</article>')
        out.append(s + '</div></section>')

    # ── plans (never dropped: the reference's head and its outlined button, in its three columns)
    plans = d.get('plans') or {}
    pl = [p for p in (plans.get('items') or []) if p.get('name')]
    if pl:
        s = '<section class="plans"><div class="head">' + (f'<h2 class="h28">{e(plans["title"])}</h2>' if plans.get('title') else '')
        s += _paras(plans.get('text'), 'small') + '</div><div class="cols3">'
        for p in pl:
            s += ('<article' + (' class="marked"' if p.get('marked') else '') + f'><h3 class="label">{e(p["name"])}</h3>'
                  + (f'<p class="price"><span class="h28">{e(p["price"])}</span>' + (f' <span class="small">{e(p["per"])}</span>' if p.get('per') else '') + '</p>' if p.get('price') else '')
                  + _paras(p.get('line'), 'small')
                  + ('<ul class="inc">' + ''.join(f'<li>{e(r)}</li>' for r in p['rows']) + '</ul>' if p.get('rows') else '')
                  + _a(p.get('cta'), 'btn') + '</article>')
        s += '</div>' + (f'<p class="small fine">{e(plans["note"])}</p>' if plans.get('note') else '')
        out.append(s + '</section>')

    # ── questions (never dropped: the tint band's title column and numbered rows; each row opens)
    faq = d.get('faq') or {}
    qs = [q for q in (faq.get('items') or []) if q.get('q')]
    if qs:
        s = '<section class="band faq"><div class="ttl">' + (f'<h2 class="h22">{e(faq["title"])}</h2>' if faq.get('title') else '') + '</div><div class="qs">'
        for i, q in enumerate(qs):
            s += (f'<details{" open" if i == 0 else ""}><summary><span class="no">{i + 1:02d}</span><span class="t">{e(q["q"])}</span></summary>'
                  f'<div class="ans">{_paras(q.get("a"), "serif")}</div></details>')
        out.append(s + '</div></section>')

    # ── credentials, as the client states them (three columns; a badge only when the client's own file is given)
    creds = [c for c in (d.get('credentials') or []) if c.get('t') or c.get('text')]
    if creds:
        s = '<section class="creds"><div class="cols3">'
        for c in creds:
            t = ' · '.join(str(x) for x in (c.get('t'), c.get('year')) if x)
            inner = ((f'<img class="badge" src="{e(m(c["img"]))}" alt="" loading="lazy">' if c.get('img') else '')
                     + (f'<h3 class="label">{e(t)}</h3>' if t else '') + _paras(c.get('text'), 'small'))
            s += '<article>' + (f'<a href="{e(c["h"])}">{inner}</a>' if c.get('h') else inner) + '</article>'
        out.append(s + '</div></section>')

    # ── 7 come and find us (reference: label, serif words 253 wide at 40; two upright pictures 389×540 from 613)
    close = d.get('close') or {}
    phone = place.get('phone') or contact.get('phone') or {}
    email = place.get('email') or contact.get('email')
    reach = []
    addr = _addr(place.get('address'))
    if addr:
        reach.append('<address>' + '<br>'.join(e(x) for x in addr) + '</address>')
    if phone.get('t'):
        reach.append('<p>' + _a(phone) + (f'<br><span class="soft">{e(phone["note"])}</span>' if phone.get('note') else '') + '</p>')
    if email:
        reach.append(f'<p><a href="mailto:{e(email)}">{e(email)}</a></p>')
    hrs = _hours(place.get('hours'))
    if hrs:
        reach.append('<ul class="hrs">' + ''.join(hrs) + '</ul>')
    for r in (contact.get('routes') or []):
        if r.get('t'):
            reach.append('<p>' + _a(r) + (f'<br><span class="soft">{e(r["note"])}</span>' if r.get('note') else '') + '</p>')
    for loc in (d.get('locations') or []):
        bits = [f'<h3 class="label">{e(loc["name"])}</h3>'] if loc.get('name') else []
        la = _addr(loc.get('address'))
        if la:
            bits.append('<address>' + '<br>'.join(e(x) for x in la) + '</address>')
        lp = loc.get('phone')
        if lp:
            bits.append('<p>' + (_a(lp) if isinstance(lp, dict) else e(lp)) + '</p>')
        if loc.get('email'):
            bits.append(f'<p><a href="mailto:{e(loc["email"])}">{e(loc["email"])}</a></p>')
        lh = _hours(loc.get('hours'))
        if lh:
            bits.append('<ul class="hrs">' + ''.join(lh) + '</ul>')
        if loc.get('note'):
            bits.append(f'<p class="soft">{e(loc["note"])}</p>')
        reach.append('<div class="loc">' + ''.join(bits) + '</div>')
    book = place.get('booking') or close.get('cta') or contact.get('form') or {}
    if close.get('title') or close.get('text') or reach:
        v1 = pics.take(389, 540, roles=('exterior', 'room', 'workshop', 'bar', 'detail', 'landscape', '!'), never=('portrait', 'people'))
        v2 = pics.take(389, 540, roles=('exterior', 'room', 'workshop', 'bar', 'detail', 'landscape', '!'), never=('portrait', 'people')) if v1 else None
        s = '<section class="visit"><div class="say">'
        if close.get('title'):
            s += f'<h2 class="label">{e(close["title"])}</h2>'
        s += _paras(close.get('text'), 'serif20') + (f'<p class="links">{_a(book, "ul")}</p>' if _a(book) else '')
        if reach:
            s += '<div class="reach small">' + ''.join(reach) + '</div>'
        s += '</div>'
        if v1:
            where = ', '.join(x for x in ((place.get('address') or {}).get('city'), (place.get('address') or {}).get('region')) if x)
            s += '<div class="who n2">'
            for i, ph in enumerate([v1, v2]):
                if ph:
                    s += (f'<article><figure class="zoom">{_img(ph, sizes="27vw", slot="visit")}</figure>'
                          + (f'<p class="label">{e(where)}</p>' if i == 0 and where else '') + '</article>')
            s += '</div>'
        out.append(s + '</section>')
    out.append('</main>')

    # ── foot (reference: three link columns at 40 / 270 / 497, a 445 block at 955 with an outlined button, a last line)
    seen = set()
    def col(items):
        r = ''
        for x in items:
            if x.get('t') and (x.get('t'), x.get('h')) not in seen:
                seen.add((x.get('t'), x.get('h')))
                r += '<li>' + _a(x) + '</li>'
        return f'<ul>{r}</ul>' if r else ''
    c1 = col(nav)
    more = [x for x in (d.get('links') or []) if x.get('t')]
    c2 = col(more[:8])
    c3 = col(more[8:16] + list(place.get('social') or []))
    block = ''
    if name:
        block += f'<p class="label">{e(name)}</p>'
    block += _paras(foot.get('text'), 'small')
    block += _a(cta, 'btn')
    legal = (f'<p class="copy">{e(foot["legal"])}</p>' if foot.get('legal') else '<p class="copy"></p>')
    fl = ''.join(_a(x) for x in (foot.get('links') or []))
    notices = ''
    for nt in (place.get('notices') or []):
        notices += ('<div class="notice">' + (f'<img src="{e(m(nt["img"]))}" alt="" loading="lazy"' + (f' width="{nt["w"]}" height="{nt["h"]}"' if nt.get('w') and nt.get('h') else '') + '>' if nt.get('img') else '')
                    + ''.join(f'<p>{e(t)}</p>' for t in (nt.get('text') or [])) + '</div>')
    out.append(f'<footer class="ft"><div class="cols"><div class="lk">{c1}{c2}{c3}</div><div class="blk">{block}</div></div>'
               f'{notices}<div class="last">{legal}<p class="fl">{fl}</p></div></footer>')

    title = name + (' — ' + hero['title'] if hero.get('title') and hero['title'] != name else '')
    desc = hero.get('text') or (d.get('statement') or {}).get('text') or ''
    return (f'<!doctype html><html lang="{e(lang)}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title>'
            f'<meta name="description" content="{e(desc[:300])}">'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="{FONTS}"><style>{_css(th)}</style></head><body>'
            + ''.join(out) + f'<script>{JS}</script></body></html>')


def _css(t):
    return (':root{--g:%(g)s;--ink:%(ink)s;--band:%(band)s;--bar:%(bar)s;--head:%(head)s;--soft:%(soft)s;--line:%(line)s;--light:' % t
            + LIGHT + '}' + CSS)


CSS = r'''
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--ink);font:400 13px/1.35 "Hanken Grotesk",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;letter-spacing:.02em;-webkit-font-smoothing:antialiased;overflow-x:clip}
img,video{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
p,h1,h2,h3,figure,ul,ol,blockquote,address{margin:0;padding:0;font-style:normal}
ul,ol{list-style:none}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer;letter-spacing:inherit;text-align:left}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
.label,.cap12{font:400 12px/1.5 "Hanken Grotesk",system-ui,sans-serif;letter-spacing:.04em;text-transform:uppercase}
.serif,.lead,.h22,.h28,.serif20,.cap{font-family:"Newsreader",Georgia,"Times New Roman",serif;font-weight:500;letter-spacing:0}
.serif{font-size:16px;line-height:1.35}
.lead,.h22{font-size:22px;line-height:1.2}
.h28{font-size:28px;line-height:1.2}
.serif20{font-size:20px;line-height:1.2}
.small{font-size:13px;line-height:1.35}
.soft{color:var(--soft)}
p+p{margin-top:.8em}
/* the underlined link: its line leaves to the right and comes back from the left, .3s ease-in-out (measured) */
.ul{position:relative;display:inline-block;font-size:13px;line-height:17.55px;padding-bottom:5px}
.ul::before,.ul::after{content:"";position:absolute;left:0;bottom:0;height:1px;width:100%;background:currentColor;transition:transform .3s ease-in-out}
.ul::after{transform-origin:100% 50%}.ul::before{transform:scaleX(0);transform-origin:0 50%}
a.ul:hover::after{transform:scaleX(0)}a.ul:hover::before{transform:scaleX(1);transition-delay:.3s}
.links{display:flex;flex-wrap:wrap;gap:14px 28px}
.btn{display:block;border:1px solid var(--ink);padding:12px 16px;text-align:center;font-size:13px;line-height:17.55px;transition:background-color .3s ease,color .3s ease}
a.btn:hover,.marked .btn{background:var(--ink);color:var(--g)}
.marked a.btn:hover{background:transparent;color:var(--ink)}
/* numbered list (reference: number column 80, rows 28 apart, the row moves 10px and underlines its name under the pointer) */
.nl li>a,.nl li>div{display:flex;padding:5px 0;font-size:12px;line-height:18px;letter-spacing:.04em;text-transform:uppercase;transition:transform .3s ease}
.nl li>*>span:first-child{flex:0 0 80px}
.nl a:hover{transform:translateX(10px)}.nl a:hover .t{text-decoration:underline;text-underline-offset:3px}
.nl.priced li>*>span:first-child{flex:1 1 auto;padding-right:16px}
.pr{white-space:nowrap;margin-left:auto}.st{margin-left:12px;color:var(--soft)}
.inc{margin-top:10px}.inc li{padding:7px 0;border-top:1px solid var(--line)}

/* header */
.hd{position:absolute;z-index:50;left:0;top:0;width:100%;color:var(--light);transition:transform .3s ease}
.js .hd{position:fixed}
.hd .bar{background:var(--bar);color:var(--ink);font-size:11px;line-height:16.5px;letter-spacing:.02em;text-align:center;padding:8px 40px 7.5px;margin:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hd .row{display:flex;align-items:center;height:60px;padding:0 40px}
.mark{flex:0 0 auto;min-width:342px;padding-right:32px;font-weight:300;font-size:var(--ms);line-height:1;text-transform:uppercase;letter-spacing:.005em;white-space:nowrap}
.mark img{height:26px;width:auto}
.nav{display:flex;gap:20px;flex:1 1 auto;min-width:0}
.nav a,.side a,.side span{font-size:12px;line-height:18px;letter-spacing:.04em;text-transform:uppercase;white-space:nowrap}
.side{display:flex;gap:20px;margin-left:20px}
.nav a,.side a{background:linear-gradient(currentColor,currentColor) 0 100%/0 1px no-repeat;transition:background-size .3s ease}
.nav a:hover,.side a:hover{background-size:100% 1px}
.hd.solid,.hd.up{color:var(--ink)}
.hd.solid .row,.hd.up .row{background:var(--head)}
.hd.gone{transform:translateY(-100%)}
.hd.up{transform:translateY(-32px)}.hd.up.nobar{transform:none}
.burger{display:none;width:44px;height:44px;margin-right:-11px;position:relative}
.burger i{position:absolute;left:11px;width:22px;height:1px;background:currentColor}
.burger i:nth-child(1){top:17px}.burger i:nth-child(2){top:22px}.burger i:nth-child(3){top:27px}
.menu{position:fixed;z-index:60;inset:0;background:var(--head);color:var(--ink);overflow:auto}
.menu[hidden]{display:none}
.menu nav{display:flex;flex-direction:column;padding:43vh 36px 60px}
.menu nav a,.menu nav span{font-size:13px;line-height:20px;letter-spacing:.04em;text-transform:uppercase;padding:8px 0}
.menu .x{position:absolute;right:13px;top:40px;width:44px;height:44px}
.menu .x::before,.menu .x::after{content:"";position:absolute;left:12px;top:22px;width:20px;height:1px;background:currentColor;transform:rotate(45deg)}
.menu .x::after{transform:rotate(-45deg)}

/* 1 first screen */
.hero{position:relative;height:calc(100vh + 221px);min-height:700px;color:var(--light);overflow:clip}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hero .veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.76),rgba(0,0,0,.72) 100px,rgba(0,0,0,0) 250px),linear-gradient(90deg,rgba(0,0,0,.62),rgba(0,0,0,.5) 30%,rgba(0,0,0,0) 62%),linear-gradient(0deg,rgba(0,0,0,.72),rgba(0,0,0,.66) 300px,rgba(0,0,0,0) 620px)}
.big{position:absolute;z-index:2;left:40px;top:450px;margin-top:-9px;font-weight:300;font-size:46px;line-height:1;text-transform:uppercase;letter-spacing:.005em;white-space:nowrap}
.track{position:sticky;z-index:2;top:0;height:100vh;min-height:479px;display:flex;align-items:flex-end;padding:0 40px 40px}
.hero .track{margin-top:0}
.cap{font-size:16px;line-height:1.35;max-width:560px;text-wrap:balance;margin-left:39.85%}
.hero.plain{background:var(--band);color:var(--ink);height:75vh;min-height:520px}
.hero.plain .track{height:75vh;min-height:520px}
.hero.plain .big{top:calc(37.5vh - 23px)}

/* 2 opening */
.open{display:flex;justify-content:space-between;align-items:flex-start;padding:40px 40px 120px}
.open .txt{flex:0 1 454px;padding-top:80px}
.open .top .lead+.small,.open .top .lead+.links{margin-top:32px}
.open .top .small+.links{margin-top:24px}
.open .note{margin-top:18px}
.open .top+.browse{margin-top:197px}
.browse .label+.small{margin-top:14px;max-width:330px}
.browse .nl{margin-top:45px}
.tall{flex:0 0 46.67vw;aspect-ratio:672/908;overflow:hidden}
.tall img,.stick img,.who figure img,.card figure img,.gi img,.film img,.film video,.told.print img{width:100%;height:100%;object-fit:cover}

/* 3 tint band with points */
.band{background:var(--band)}
.steps{padding:174px 40px 201px}
.topw{display:grid;grid-template-columns:42.06% 25.22% 1fr;align-items:start}
.ttl{padding-top:10px;max-width:447px;padding-right:40px}
.ttl .small{margin-top:20px;max-width:330px}
.pts li+li{margin-top:10px}
.pt{display:flex;font-size:12px;line-height:18px;letter-spacing:.04em;text-transform:uppercase;width:100%;padding:0}
.pt .no{flex:0 0 79px}.pt .no::after{content:"";display:block;width:15px;height:1px;background:currentColor;transform:scaleX(0);transform-origin:0 50%;transition:transform .3s ease}
.pt.on .no::after{transform:scaleX(1)}
.pt .t{max-width:171px}
.pt:hover .t{text-decoration:underline;text-underline-offset:3px}
.descs{max-width:331px;padding-top:4px}
.desc .label{display:none}
.desc .ul{margin-top:20px}
.desc+.desc{margin-top:32px}
.js .descs{display:grid}.js .desc{grid-area:1/1;opacity:0;visibility:hidden;transition:opacity .3s ease,visibility 0s .3s;margin:0}
.js .desc.on{opacity:1;visibility:visible;transition:opacity .3s ease .15s,visibility 0s}
.gal{display:flex;gap:var(--gap);margin-top:138px}
.gi{flex:0 1 12.08vw;min-width:0;height:16.53vw;overflow:hidden;cursor:pointer;transition:flex-basis .6s ease,margin .6s ease,filter .6s ease}
.gi img{width:25.7vw;max-width:none}
.js .gi:not(.on){filter:grayscale(1) brightness(.91) contrast(.8) opacity(.5)}
.gi.on,html:not(.js) .gi:first-child{flex:0 0 25.7vw;margin-right:var(--free)}
.gi.on.end{margin-right:0;margin-left:var(--free)}

/* 4 one thing told */
.told{position:relative;border-bottom:1px solid var(--ink)}
.told.over{min-height:773px;display:flex;align-items:center;justify-content:flex-end;color:var(--light);padding:120px 40px;border:0;overflow:hidden}
.told.over .veil{position:absolute;inset:0;background:linear-gradient(270deg,rgba(0,0,0,.78),rgba(0,0,0,.72) 30%,rgba(0,0,0,0) 64%)}
.told .col{position:relative;z-index:1;width:330px}
.told .h28+.small{margin-top:24px}.told .ul{margin-top:30px}
.told.print{display:flex;align-items:center;justify-content:space-between;padding:120px 40px 76px}
.told.print figure{width:min(var(--w),55vw);aspect-ratio:var(--ar);overflow:hidden}
.told.bare{padding:120px 40px}.told.bare .col{width:454px}

/* 5 listed things */
.feat{display:flex;justify-content:space-between;align-items:flex-start;padding:40px 40px 120px}
.feat .left{flex:0 1 445px;min-width:0}
.grp+.grp,.grp+.fine{margin-top:120px}.fine{margin-top:40px;color:var(--soft)}
.head{max-width:304px;margin-bottom:82px}
.head .label+.h28{margin-top:10px}.head .h28+.small{margin-top:33px}
.card+.card{margin-top:95px}.card.bare+.card.bare{margin-top:6px}
.card figure{aspect-ratio:445/288;overflow:hidden;background:var(--band)}
.card .cap12{display:flex;gap:16px;padding:7px 24px 0}
.card>.small,.card>.inc{padding:8px 24px 0}
.card+.nl{margin-top:95px}
.nl.priced li>a,.nl.priced li>div{padding:5px 24px}
.stick{flex:0 0 47.22vw;aspect-ratio:680/820;position:sticky;top:40px;overflow:hidden}

/* 6 picture without words */
.film{aspect-ratio:var(--ar,4/3);max-height:1080px;overflow:hidden;width:100%}
.film video{aspect-ratio:auto}

/* said by clients · plans · credentials: three columns at 40 / 497 / 955 */
.cols3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));column-gap:9.3%;row-gap:80px}
.cols3>*{max-width:331px}
.says{padding:120px 40px}
.says figcaption{margin-top:20px;display:flex;flex-direction:column}
.plans{padding:120px 40px}.plans .head{margin-bottom:60px}
.plans article{display:flex;flex-direction:column;gap:14px}.plans .btn{margin-top:14px}
.creds{padding:80px 40px;border-top:1px solid var(--line)}.creds .label+.small{margin-top:10px}.badge{max-height:64px;width:auto;margin-bottom:16px}
/* questions */
.faq{padding:120px 40px;display:grid;grid-template-columns:42.06% 1fr}
.faq .ttl{padding-top:0}
.qs{max-width:560px}
.qs details{border-top:1px solid var(--line)}.qs details:last-child{border-bottom:1px solid var(--line)}
.qs summary{display:flex;padding:14px 0;font-size:12px;line-height:18px;letter-spacing:.04em;text-transform:uppercase;cursor:pointer;list-style:none}
.qs summary::-webkit-details-marker{display:none}
.qs .no{flex:0 0 79px}.qs .ans{padding:4px 0 24px 79px}

/* 7 visit · the people */
.visit{display:flex;justify-content:space-between;align-items:flex-start;padding:40px 40px 160px}
.visit.team{padding-bottom:120px}
.say{flex:0 1 330px;min-width:0}
.say .serif20{max-width:253px}.say .label+.serif20{margin-top:42px}
.say .links{margin-top:28px}
.reach{margin-top:44px;display:grid;gap:14px;max-width:330px}
.reach a:hover{text-decoration:underline;text-underline-offset:3px}
.hrs li{display:flex;justify-content:space-between;gap:16px;max-width:253px}
.loc{display:grid;gap:8px;padding-top:14px}
.who{flex:0 0 54.65vw;display:grid;gap:40px 9px}
.who.n1,.who.n2{grid-template-columns:repeat(2,minmax(0,1fr))}.who.n3{grid-template-columns:repeat(3,minmax(0,1fr))}
.who figure{aspect-ratio:var(--ar,389/540);overflow:hidden}
.who .label{margin-top:4px}
.team .who .label{margin-top:10px}
.role{font-size:12px;line-height:1.5;color:var(--soft)}
.who .small{margin-top:14px}.who .reach{display:flex;flex-direction:column;gap:2px;margin-top:10px}
.zoom img{transition:transform .9s ease}.zoom:hover img{transform:scale(1.1)}

/* foot */
.ft{padding:34px 40px 24px;border-top:1px solid var(--line)}
.ft .cols{display:flex;justify-content:space-between;align-items:flex-start}
.lk{display:grid;grid-template-columns:230px 227px 227px}
.lk li a,.lk li span{display:inline-block;padding:6px 0;font-size:13px;line-height:17.55px}
.lk a:hover,.fl a:hover{text-decoration:underline;text-underline-offset:3px}
.blk{flex:0 0 445px;display:grid;gap:18px}
.notice{margin-top:40px;display:flex;gap:20px;align-items:center;font-size:12px}.notice img{max-height:60px;width:auto}
.last{display:flex;justify-content:space-between;margin-top:64px;font-size:12px;line-height:18px;letter-spacing:.02em}
.copy{color:var(--soft)}
.fl{display:flex;gap:32px;flex:0 0 445px;flex-wrap:wrap}

@media (max-width:1100px){
 .mark{min-width:0}
 .nav{gap:14px}
}
@media (max-width:900px){
 .nav,.side{display:none}.burger{display:block;margin-left:auto}
 .hd .bar{font-size:12px;line-height:15px;padding:8px 44px}
 .hd .row{padding:0 20px;height:60px}
 .mark{font-size:min(var(--ms),22px)}
 .big{display:none}
 .hero{height:calc(100vh + 221px)}
 .track{align-items:flex-start;padding:max(56.75vh,330px) 20px 0}
 .cap{margin-left:0;max-width:350px}
 .hero .veil{background:linear-gradient(180deg,rgba(0,0,0,.76),rgba(0,0,0,.72) 100px,rgba(0,0,0,0) 250px),linear-gradient(0deg,rgba(0,0,0,0),rgba(0,0,0,.7) 26%,rgba(0,0,0,.7) 58%,rgba(0,0,0,0) 86%)}
 .hero.plain,.hero.plain .track{height:auto;min-height:0}.hero.plain .track{padding:150px 20px 60px}
 .open{display:block;padding:40px 24px 80px}
 .open .txt{padding:0 12px}.lead{font-size:20px}
 .tall{margin-top:44px;width:100%}
 .steps{padding:80px 0 81px}
 .topw{display:block;padding:0 40px}
 .ttl{padding:0}
 .pts{display:flex;gap:26px;margin-top:42px}.pts li+li{margin:0}
 .pt{padding:6px 0;min-width:17px}.pt .t{display:none}.pt .no{flex:0 0 auto}
 .descs{margin-top:44px;padding-left:40px;max-width:none}
 .desc .label{display:block;margin-bottom:20px}
 .gal{margin-top:150px;gap:40px;padding:0 6px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}
 .gal::-webkit-scrollbar{display:none}
 .gi,.gi.on,html:not(.js) .gi:first-child,.gi.on.end{flex:0 0 80.5vw;height:57.4vw;margin:0;scroll-snap-align:center}
 .gi img{width:100%}
 .told.over{min-height:560px;align-items:flex-end;justify-content:flex-start;padding:200px 40px 56px}
 .told.over .veil{background:linear-gradient(0deg,rgba(0,0,0,.8),rgba(0,0,0,.74) 55%,rgba(0,0,0,0) 92%)}
 .told .col{width:290px}.told .h28{font-size:24px}
 .told.print{display:block;padding:20px 20px 80px}.told.print figure{width:min(var(--w),100%)}.told.print .col{margin:97px 20px 0}
 .told.bare{padding:80px 40px}.told.bare .col{width:auto}
 .feat{display:flex;flex-direction:column-reverse;padding:40px 6px 64px}
 .stick{position:static;flex:none;width:calc(100% - 28px);margin:0 14px 34px}
 .feat .left{flex:none;width:100%}
 .head{margin:0 14px 82px;max-width:350px}
 .feat.nopic .left{padding-top:0}
 .card+.card{margin-top:25px}
 .grp+.grp{margin-top:80px}
 .cols3{grid-template-columns:1fr;row-gap:48px}
 .says,.plans{padding:80px 40px}
 .faq{display:block;padding:80px 40px}.faq .ttl{margin-bottom:40px}.qs .no{flex-basis:40px}.qs .ans{padding-left:40px}
 .visit{display:block;padding:40px 40px 58px}
 .who{margin-top:56px}
 .who.n1,.who.n2,.who.n3{grid-template-columns:1fr}
 .ft{padding:36px 20px 24px}
 .ft .cols{flex-direction:column-reverse;gap:48px}
 .blk{flex:none;width:100%}
 .lk{grid-template-columns:1fr 1fr;gap:24px 20px;width:100%}
 .last{flex-direction:column;gap:14px;margin-top:56px}.fl{flex:none;gap:10px 24px}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
'''

JS = r'''(function(){var D=document,R=D.documentElement;R.classList.add('js');
var hd=D.getElementById('hd'),last=scrollY,tick=0;
function head(){tick=0;var y=scrollY;if(y<100){hd.classList.remove('gone','up')}else if(y>last+2){hd.classList.add('gone');hd.classList.remove('up')}else if(y<last-2){hd.classList.remove('gone');hd.classList.add('up')}last=y}
if(hd){addEventListener('scroll',function(){if(!tick)tick=requestAnimationFrame(head)},{passive:true});head()}
var menu=D.getElementById('menu'),bg=D.querySelector('.burger');
if(menu&&bg){var shut=function(){menu.hidden=true;bg.setAttribute('aria-expanded','false');bg.focus()};
bg.addEventListener('click',function(){menu.hidden=false;bg.setAttribute('aria-expanded','true');menu.querySelector('.x').focus()});
menu.querySelector('.x').addEventListener('click',shut);menu.addEventListener('keydown',function(e){if(e.key==='Escape')shut()});
menu.addEventListener('click',function(e){if(e.target.closest('a'))menu.hidden=true})}
D.querySelectorAll('[data-tabs]').forEach(function(s){var pts=s.querySelectorAll('.pt'),ds=s.querySelectorAll('.desc'),gs=s.querySelectorAll('.gi'),gal=s.querySelector('.gal');
function go(i,move){pts.forEach(function(p,k){p.classList.toggle('on',k===i);p.setAttribute('aria-pressed',k===i?'true':'false')});ds.forEach(function(x,k){x.classList.toggle('on',k===i)});gs.forEach(function(g,k){g.classList.toggle('on',k===i)});
if(move&&gal&&gal.scrollWidth>gal.clientWidth+4&&gs[i]){gal.scrollTo({left:gs[i].offsetLeft-gal.offsetLeft-6,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'})}}
pts.forEach(function(p,i){p.addEventListener('click',function(){go(i,true)})});gs.forEach(function(g,i){g.addEventListener('click',function(){go(i,false)})});
if(gal){var t=0;gal.addEventListener('scroll',function(){clearTimeout(t);t=setTimeout(function(){if(gal.scrollWidth<=gal.clientWidth+4)return;var c=gal.scrollLeft+gal.clientWidth/2,b=0,bd=1e9;gs.forEach(function(g,k){var m=g.offsetLeft-gal.offsetLeft+g.offsetWidth/2,dd=Math.abs(m-c);if(dd<bd){bd=dd;b=k}});go(b,false)},120)},{passive:true})}});
})();'''
