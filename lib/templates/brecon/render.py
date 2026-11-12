"""brecon/render.py — one pure function: render(d) -> a complete page. A template for PLACES.

The build (section order, the two page-long hairlines at 1/6 and 1/2 of the width, the booking bar, measures, type scale,
spacing, motion, phone build) was measured on the reference's home page at 1440 and 390 on 2026-11-12 (see NOTES.md).
Nothing of the reference's code, words, pictures, logo or typefaces is here. The client's data fills it; a section whose
data is missing is left out whole. No model call, no file reads, no client logic.
"""
import html

FONTS = 'https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400&display=swap'
ROOMY = ('room', 'bar', 'exterior', 'people', 'other')
WORDS = {  # accessible names only (never visible): the data has no words for these controls
    'es': ('Menú', 'Cerrar', 'Anterior', 'Siguiente'), 'en': ('Menu', 'Close', 'Previous', 'Next'),
    'fr': ('Menu', 'Fermer', 'Précédent', 'Suivant'), 'de': ('Menü', 'Schließen', 'Zurück', 'Weiter'),
    'it': ('Menu', 'Chiudi', 'Precedente', 'Successivo'), 'pt': ('Menu', 'Fechar', 'Anterior', 'Seguinte'),
    'sr': ('Meni', 'Zatvori', 'Prethodno', 'Sledeće'),
}


# ───────────────────────── colour: the reference's relations (tinted ground / one deep colour as ink, slab and button)
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


def _toward(col, pole, against, want):
    t = 0.0
    while t < 1 and _con(_mix(pole, col, t), against) < want:
        t += .02
    return _mix(pole, col, min(t, 1))


def _theme(p):
    g = p.get('ground') or '#ffffff'
    ink = p.get('ink') or '#111111'
    acc = p.get('accent') or ink
    pole = '#000000' if _lum(g) >= _lum(ink) else '#ffffff'
    if _con(ink, g) < 7:  # body text must read on the ground
        ink = _toward(ink, pole, g, 7)
    # the slab / button / menu colour: the client's accent taken deep enough to carry white as the reference's does
    deep = _toward(acc, '#000000', '#ffffff', 10)
    r, gg, b = _rgb(ink)
    return {'g': g, 'ink': ink, 'deep': deep, 'deeper': _mix('#000000', deep, .25),
            'line': 'rgba(%d,%d,%d,.5)' % (r, gg, b)}


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s or ''), quote=True)


def src(p):
    return '../../' + p if p and not p.startswith(('http:', 'https:', 'data:', '/')) else (p or '')


def a(link, cls='', inner=None):
    """a link when the data has an address, plain words when it has none"""
    if not link or not link.get('t'):
        return ''
    t = inner if inner is not None else e(link['t'])
    c = f' class="{cls}"' if cls else ''
    return f'<a{c} href="{e(link["h"])}">{t}</a>' if link.get('h') else f'<span{c}>{t}</span>'


def img(p, cls='', lazy=True, sizes=''):
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="{e(src(p["src"]))}" width="{p.get("w") or ""}" height="{p.get("h") or ""}" alt="{e(p.get("alt"))}"'
            + (' loading="lazy"' if lazy else '') + ' decoding="async">')


def _up(p, w, h):
    """how much a picture must be enlarged to cover a w×h box"""
    return max(w / max(p.get('w') or 1, 1), h / max(p.get('h') or 1, 1))


CHEV = '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M9 4l8 8-8 8" fill="none" stroke="currentColor" stroke-width="{w}"/></svg>'


# ───────────────────────── pictures: who gets which (chosen by role, size and proportion; each once; a fixed number)
RANK = {'room': 0, 'exterior': 0, 'bar': 1, 'people': 2, 'other': 2}
SQ_MAX = 8      # the square row never takes more than this, however many the client has
SQ_SIDE = 470   # a square is 470 px at 1440: a picture shorter than that on its short side is not enlarged into it


def _loss(p, w, h):
    """share of the picture that a w×h cover crop cuts away"""
    pw, ph = max(p.get('w') or 1, 1), max(p.get('h') or 1, 1)
    s = max(w / pw, h / ph)
    return 1 - (w / s) * (h / s) / (pw * ph)


def _slots(d):
    place = d.get('place') or {}
    photos, seen = [], set()
    for p in ((d.get('media') or {}).get('photos') or []):
        if p.get('src') and p['src'] not in seen:
            seen.add(p['src'])
            photos.append(p)
    by = {p['src']: p for p in photos}
    owned = {s.get('img') for s in (place.get('spaces') or []) if s.get('img')}
    free = [p for p in photos if p['src'] not in owned]
    S = {'hero': [], 'close': None, 'band': None, 'event': None, 'wide': None, 'menu': None, 'car': [], 'by': by}
    rank = lambda p: RANK.get(p.get('role'), 2)
    # a backdrop is a large picture of the place itself — never a small one, never a dish — enlarged at most 1.3× at 1440
    drop = lambda p, w, h: not p.get('small') and p.get('role') != 'dish' and _up(p, w, h) <= 1.3

    def take(ok, key):
        c = [p for p in free if ok(p)]
        if not c:
            return None
        p = min(c, key=key)
        free.remove(p)
        return p
    # first screen: a room or the outside before anything else, then the one the crop cuts least
    h = take(lambda p: drop(p, 1440, 850), lambda p: (rank(p), round(_loss(p, 1440, 850), 1), _up(p, 1440, 850)))
    if h:
        S['hero'].append(h)
    # the band without words shows its picture clean: the one that fits whole comes first
    S['band'] = take(lambda p: drop(p, 1440, 1) and (p.get('w') or 0) >= 1150,
                     lambda p: (round(_loss(p, 1440, min(900, 1440 * (p.get('h') or 1) / (p.get('w') or 1))), 1), rank(p), _up(p, 1440, 1)))
    if place.get('events'):
        S['event'] = take(lambda p: drop(p, 1440, 900), lambda p: (round(_loss(p, 1440, 900), 1), rank(p)))
    if (d.get('close') or {}).get('title'):
        S['close'] = take(lambda p: drop(p, 1440, 675), lambda p: (rank(p), round(_loss(p, 1440, 675), 1)))
    S['wide'] = take(lambda p: drop(p, 945, 591) and rank(p) <= 1, lambda p: (rank(p), round(_loss(p, 945, 591), 1)))
    menu = place.get('menu') or {}
    if menu.get('sections') or menu.get('lists'):
        S['menu'] = take(lambda p: p.get('role') == 'dish' and not p.get('small') and _up(p, 945, 591) <= 1.0,
                         lambda p: _loss(p, 945, 591))
    spare = [p for p in free if drop(p, 1440, 850)]
    if S['hero'] and len(spare) >= 3:  # the reference's first screen changes pictures; only when there are large ones to spare
        for p in sorted(spare, key=lambda p: (rank(p), _loss(p, 1440, 850)))[:2]:
            free.remove(p)
            S['hero'].append(p)
    # the square row: dishes first, then what else is left; only pictures that fill a square without enlarging
    sq = [p for p in free if min(p.get('w') or 0, p.get('h') or 0) >= SQ_SIDE]
    sq = sorted(sq, key=lambda p: p.get('role') != 'dish')
    dishes = [p for p in sq if p.get('role') == 'dish']
    if len(dishes) > SQ_MAX:  # many dishes: evenly through the client's own order, so the row is not eight of one course
        sq = [dishes[i * len(dishes) // SQ_MAX] for i in range(SQ_MAX)]
    sq = sq[:SQ_MAX]
    if len(sq) >= 2:
        S['car'] = sq
        S['sqmax'] = min(min(p.get('w') or 0, p.get('h') or 0) for p in sq)
    return S


# ───────────────────────── sections
def _bar(d, place, words):
    b = d.get('brand') or {}
    cta = d.get('cta') or place.get('booking')
    hours = place.get('hours') or []
    ad = place.get('address') or {}
    if hours:
        h0 = hours[0]
        cell_a = e(h0.get('days')) + (f' <span class="sm">·</span> {e(h0.get("open"))} – {e(h0.get("close"))}' if h0.get('open') else '')
    else:
        cell_a = e(', '.join(x for x in (ad.get('street'), ad.get('city')) if x))
    ph = place.get('phone') or {}
    cell_b = a(ph) if ph.get('t') else ''
    sec = (d.get('hero') or {}).get('secondary')
    name = '' if b.get('logo') else f'<a class="bname" href="{e(b.get("home") or "#")}">{e(b.get("name"))}</a>'
    return f'''<header class="bar">
<div class="bcell bn">{name}</div>
<div class="bcell ba">{cell_a}</div>
<div class="bcell bb">{cell_b}</div>
{a(cta, "bbook") if cta else '<span class="bbook none"></span>'}
<div class="bcell bd">{a(sec) if sec else ''}</div>
</header>'''


def _menu(d, place, words):
    seen, items = set(), []
    for it in (d.get('nav') or []) + [{'t': x.get('t'), 'h': x.get('h')} for x in (d.get('links') or [])]:
        if it.get('t') and it.get('h') and it['h'] not in seen:
            seen.add(it['h'])
            items.append(it)
    if not items:
        return '', ''
    b = d.get('brand') or {}
    sec = (d.get('hero') or {}).get('secondary')
    lis = ''.join(f'<li>{a(it)}</li>' for it in items)
    btn = (f'<button class="hamb" type="button" aria-expanded="false" aria-controls="nav" aria-label="{e(words[0])}" '
           f'data-open="{e(words[0])}" data-close="{e(words[1])}"><span></span></button>')
    nav = (f'<nav class="menu" id="nav" aria-label="{e(words[0])}"><ul>{lis}</ul>'
           + (a(sec, 'mbtn') if sec and sec.get('h') and sec['h'] not in seen else '') + '</nav>')
    return btn, nav


def _hero(d, S, words):
    h = d.get('hero') or {}
    if not h.get('title'):
        return ''
    sl = ''.join(f'<div class="sl{" on" if i == 0 else ""}">{img(p, lazy=i > 0)}</div>' for i, p in enumerate(S['hero']))
    arrows = ''
    if len(S['hero']) > 1:
        ch = CHEV.format(w=2.6)
        arrows = (f'<div class="harr"><button type="button" class="hprev" aria-label="{e(words[2])}">{ch}</button>'
                  f'<button type="button" class="hnext" aria-label="{e(words[3])}">{ch}</button></div>')
    sub = f'<p>{e(h.get("text2"))}</p>' if h.get('text2') else ''
    return f'''<div class="hero{' pic' if sl else ''}" data-slot="hero">{sl}{'<div class="hveil"></div>' if sl else ''}
<div class="cap"><h1>{e(h["title"])}</h1>{sub}</div>{arrows}</div>'''


def _two(label, title, link, paras, extra_cls='', right_html=''):
    """the reference's text row: label / heading / link in the first column, running text in the second"""
    left = ((f'<p class="lab">{e(label)}</p>' if label else '') + (f'<h2>{e(title)}</h2>' if title else '') + (link or ''))
    right = ''.join(f'<p>{x}</p>' for x in paras if x) + right_html
    if not left and not right:
        return ''
    return f'<div class="row {extra_cls}"><div class="col">{left}</div><div class="col">{right}</div></div>'


def _lnk(link):
    x = a(link, 'u')
    return f'<p class="lk">{x}</p>' if x else ''


def _intro(d, S, words):
    st, h = d.get('statement') or {}, d.get('hero') or {}
    if not st.get('title') and not h.get('text'):
        return ''
    left = (f'<h2>{e(st.get("title"))}</h2>' if st.get('title') else '') + (f'<p>{e(st.get("text"))}</p>' if st.get('text') else '')
    right = ''.join(f'<p>{e(x)}</p>' for x in (h.get('text'), h.get('note')) if x) + _lnk(h.get('secondary'))
    car = ''
    if S['car']:
        ch = CHEV.format(w=1.2)
        car = (f'<div class="car" data-slot="carousel" style="--sqmax:{S["sqmax"]}px"><div class="track" tabindex="0">'
               + ''.join(f'<div class="sq">{img(p)}</div>' for p in S['car']) + '<div class="end"></div></div>'
               f'<button type="button" class="cbtn cprev" aria-label="{e(words[2])}" hidden>{ch}</button>'
               f'<button type="button" class="cbtn cnext" aria-label="{e(words[3])}" hidden>{ch}</button></div>')
    return (f'<section class="s1{" hascar" if car else ""}"><div class="row"><div class="col">{left}</div>'
            f'<div class="col">{right}</div></div>{car}</section>')


def _band(S):
    p = S['band']
    if not p:
        return ''
    return (f'<section class="band" data-slot="band" style="--r:{(p.get("h") or 9) / (p.get("w") or 16):.4f};--nh:{p.get("h") or 0}px">'
            f'{img(p)}</section>')


def _rooms(d, S):
    st, h = d.get('steps') or {}, d.get('hero') or {}
    if not st.get('title'):
        return ''
    out = '<section class="s4">' + _two(h.get('kicker'), st.get('title'), '', [e(st.get('text'))]) + '</section>'
    if S['wide']:
        out += f'<section class="s5" data-slot="wide"><div class="wide">{img(S["wide"])}</div></section>'
    return out


def _cards(d, place, S, words, gap_after):
    spaces = place.get('spaces') or []
    steps = (d.get('steps') or {}).get('items') or []
    cards = []
    if spaces:
        pics = [S['by'].get(s.get('img')) for s in spaces]
        small = [p for p in pics if p and p.get('small')]
        if small:  # a small picture is never wider than its pixels: the whole row takes its width and proportion
            m = min(small, key=lambda p: p.get('w') or 0)
            fw, fr = min(456, m.get('w') or 456), (m.get('h') or 1) / (m.get('w') or 1)
        else:
            fw, fr = 456, 1
        for s, p in zip(spaces, pics):
            st = next((x for x in steps if (x.get('img') and x.get('img') == s.get('img')) or x.get('title') == s.get('title')), {})
            pic = f'<div class="cpic" data-slot="space">{img(p)}</div>' if p else ''
            cards.append((s.get('title'), pic, st.get('k'), s.get('text'), st.get('cta')))
        style = f' style="--fw:{fw}px;--fr:{fr:.4f}"'
    else:
        for x in steps:
            cards.append((x.get('title'), '', x.get('k'), x.get('text'), None if not x.get('cta') else x['cta']))
        style = ''
    cards = [c for c in cards if c[0]]
    if not cards:
        return ''
    ch = CHEV.format(w=1.2)
    body = ''
    for t, pic, k, text, cta in cards:
        lab = k if k and k != t else ''
        link = ''
        if cta and cta.get('h') and cta.get('t') and cta.get('t') != lab:
            link = f'<p class="cta">{a(cta, "u")}</p>'
        elif cta and cta.get('h') and lab:  # the label is the link's own words: it carries the link
            lab, link = '', f'<p class="cta">{a(cta, "u")}</p>'
        body += (f'<article class="card"><div class="chead"><h3>{e(t)}</h3></div>{pic}<div class="cbody">'
                 + (f'<p class="lab">{e(lab)}</p>' if lab else '') + (f'<p>{e(text)}</p>' if text else '') + link + '</div></article>')
    # a row in which no card has a picture is the word-card build (three to the row), whether the cards come from
    # spaces or from steps: a space without a photograph must not keep the empty half-width picture card
    words_row = not any(c[1] for c in cards)
    return (f'<section class="s3{" gap" if gap_after else ""}{" words" if words_row else ""}"{style}><div class="car"><div class="track" tabindex="0">{body}<div class="end"></div></div>'
            f'<button type="button" class="cbtn cprev" aria-label="{e(words[2])}" hidden>{ch}</button>'
            f'<button type="button" class="cbtn cnext" aria-label="{e(words[3])}" hidden>{ch}</button></div></section>')


def _over(p, label, title, paras, link, cls, slot):
    """the reference's picture band with words over it; with no picture the same words in the plain text row"""
    if not title:
        return ''
    if not p:
        return f'<section class="s4" data-slot="{slot}">' + _two(label, title, _lnk(link), [e(x) for x in paras]) + '</section>'
    inner = ((f'<p class="lab">{e(label)}</p>' if label else '') + f'<h2>{e(title)}</h2>'
             + ''.join(f'<p>{e(x)}</p>' for x in paras if x) + _lnk(link))
    return (f'<section class="over {cls}" data-slot="{slot}">{img(p)}<div class="oveil"></div>'
            f'<div class="otext">{inner}</div></section>')


def _event(place, S):
    ev = (place.get('events') or [None])[0]
    if not ev or not ev.get('what'):
        return ''
    line = ' · '.join(x for x in (ev.get('price'), ev.get('where')) if x)
    return _over(S['event'], ev.get('when'), ev.get('what'), [line], ev.get('cta'), '', 'event')


def _carta(d, place, S):
    menu = place.get('menu') or {}
    secs, lists = menu.get('sections') or [], menu.get('lists') or []
    if not secs and not lists:
        return ''
    title = next((x.get('t') for x in (d.get('links') or []) + (d.get('nav') or []) if x.get('h') and x.get('h') == menu.get('h')), None)
    plain = [s for s in secs if not s.get('items')]
    priced = [s for s in secs if s.get('items')]
    li = lambda x: f'<li>{a({"t": x.get("t"), "h": x.get("h")})}' + (f' <span class="n">({e(x["count"])})</span>' if x.get('count') else '') + '</li>'
    right = ''
    if plain:
        right += '<ul class="ml">' + ''.join(li(x) for x in plain) + '</ul>'
    for s in priced:
        rows = ''.join(f'<tr><th scope="row">{a({"t": i.get("name"), "h": i.get("h")})}</th><td>{e(i.get("price"))}</td></tr>' for i in s['items'] if i.get('name'))
        notes = {i.get('note') for i in s['items'] if i.get('note')}
        right += (f'<table class="mt"><caption>{e(s.get("t"))}</caption>{rows}</table>'
                  + (f'<p class="mn">{e(notes.pop())}</p>' if len(notes) == 1 else ''))
    if lists:
        right += '<ul class="ml">' + ''.join(li(x) for x in lists) + '</ul>'
    link = _lnk({'t': title, 'h': menu.get('h')}) if title and menu.get('h') else ''
    out = ('<section class="s4 carta">' + _two((d.get('features') or {}).get('title'), None if link else title, link, [], right_html=right) + '</section>')
    if S['menu']:
        out += f'<section class="s5 rev" data-slot="menu"><div class="wide">{img(S["menu"])}</div></section>'
    return out


def _close(d, place, S):
    c = d.get('close') or {}
    return _over(S['close'], None, c.get('title'), [c.get('text')], c.get('cta') or place.get('booking'), 'low', 'close')


def _foot(d, place):
    b, f = d.get('brand') or {}, d.get('foot') or {}
    ad, ph = place.get('address') or {}, place.get('phone') or {}
    lines = [ad.get('street'), ' '.join(x for x in (ad.get('postcode'), ad.get('city')) if x),
             ', '.join(x for x in (ad.get('region'), ad.get('country')) if x)]
    lines = [e(x) for x in lines if x]
    c1 = '<br>'.join(lines) if lines else e(f.get('text'))
    contact = ''
    if ph.get('t'):
        contact += f'<li>{a(ph)}' + (f' <span class="note">{e(ph.get("note"))}</span>' if ph.get('note') and ph.get('h') else '') + '</li>'
    if place.get('email'):
        contact += f'<li><a href="mailto:{e(place["email"])}">{e(place["email"])}</a></li>'
    col1 = f'<div class="fc f1"><p>{c1}</p>' + (f'<ul>{contact}</ul>' if contact else '') + '</div>'
    links = [x for x in (d.get('nav') or []) + (f.get('links') or []) if x.get('t') and x.get('h')]
    soc = place.get('social') or []
    sh = {x.get('h') for x in soc}
    seen, uniq = set(sh), []
    for x in links:
        if x['h'] not in seen:
            seen.add(x['h'])
            uniq.append(x)
    links = uniq
    half = max(5, (len(links) + 1) // 2)
    col2 = ('<div class="fc f2">' + ''.join('<ul>' + ''.join(f'<li>{a(x)}</li>' for x in part) + '</ul>'
                                            for part in (links[:half], links[half:]) if part) + '</div>') if links else '<div class="fc f2"></div>'
    hrs = ''.join(f'<li>{e(x.get("days"))}<br>{e(x.get("open"))} – {e(x.get("close"))}</li>' for x in (place.get('hours') or []))
    col3 = f'<div class="fc f3">{"<ul>" + hrs + "</ul>" if hrs else ""}</div>'
    col4 = ('<div class="fc f4"><ul>' + ''.join(f'<li>{a(x)}</li>' for x in soc)
            + (f'<li class="legal">{e(f.get("legal"))}</li>' if f.get('legal') else '') + '</ul></div>')
    notices = ''
    for n in place.get('notices') or []:
        pic = (f'<img src="{e(src(n["img"]))}" width="{n.get("w") or ""}" height="{n.get("h") or ""}" alt="" loading="lazy" '
               f'style="max-width:min(100%,{min(n.get("w") or 220, 220)}px)">') if n.get('img') else ''
        notices += f'<div class="notice">{pic}' + ''.join(f'<p>{e(t)}</p>' for t in n.get('text') or []) + '</div>'
    return f'''<footer class="foot"><p class="fname">{e(b.get("name"))}</p>
<div class="frow">{col1}{col2}{col3}{col4}</div>{f'<div class="fnot">{notices}</div>' if notices else ''}</footer>'''


CSS = '''
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--i);font:400 16px/1.2 Newsreader,"Iowan Old Style",Georgia,serif;font-optical-sizing:auto;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img{display:block;max-width:100%;height:auto}
p,h1,h2,h3,ul{margin:0;padding:0}ul{list-style:none}
a{color:inherit;text-decoration:none;transition:opacity .25s ease}
a:hover{opacity:.8}
a.u{text-decoration:underline;text-underline-offset:2px;text-decoration-thickness:1px}
h1,h2{font-weight:400;font-size:44px;line-height:1;letter-spacing:-.02em;text-wrap:balance}
h3{font-weight:400;font-size:27px;line-height:1;letter-spacing:-.02em}
.lab{text-transform:uppercase}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}

/* the bar: 50 high, cells at 1/6, 1/2, 2/3, 5/6 of the width, a hairline under it; stays at the top */
.bar{position:sticky;top:0;z-index:30;display:flex;height:50px;background:var(--g);line-height:50px;white-space:nowrap}
.bar::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--line)}
.bcell{overflow:hidden;text-overflow:ellipsis}
.bn{width:16.6667vw;padding:0 10px 0 48px;display:flex;align-items:center;white-space:normal}
.bname{line-height:1.05;text-wrap:balance}
.ba{width:33.3333vw;border-left:1px solid var(--line);padding-left:15px}
.bb{width:16.6667vw;border-left:1px solid var(--line);padding-left:15px}
.bbook{width:16.6667vw;background:var(--d);color:#fff;text-align:center;text-transform:uppercase;transition:background-color .25s ease}
a.bbook:hover{opacity:1;background:var(--dd)}
.bbook:focus-visible{outline-offset:-5px}
.bbook.none{background:none}
.bd{flex:1;text-align:center;padding:0 15px}
.sm{font-size:14px}

/* the round menu button stays put; the logo stays put at the right */
.hamb{position:fixed;z-index:40;left:48px;top:84px;width:52px;height:52px;border-radius:50%;background:var(--g);color:var(--i)}
.hamb span,.hamb span::before,.hamb span::after{position:absolute;left:11px;width:30px;height:1px;background:currentColor;content:""}
.hamb span{top:25px}.hamb span::before{left:0;top:-7px}.hamb span::after{left:0;top:7px}
.hamb[aria-expanded=true]{background:none;color:#fff}
.hamb[aria-expanded=true] span{background:none}
.hamb[aria-expanded=true] span::before{top:0;transform:rotate(45deg);left:2px;width:26px}
.hamb[aria-expanded=true] span::after{top:0;transform:rotate(-45deg);left:2px;width:26px}
.mark{position:fixed;z-index:38;right:25px;top:100px;width:min(9vw,130px)}
.mark img{width:100%}
.menu{position:fixed;z-index:35;inset:50px 0 0 0;background:var(--dm);color:#fff;overflow:auto;padding:176px 48px 48px;opacity:0;visibility:hidden;transition:opacity .25s ease,visibility 0s .25s}
.menu.open{opacity:1;visibility:visible;transition:opacity .25s ease}
.menu ul{display:inline-block;min-width:186px;border-top:1px solid rgba(255,255,255,.5)}
.menu li{border-bottom:1px solid rgba(255,255,255,.5)}
.menu li a{display:block;font-size:22px;line-height:1.2;padding:6px 0;letter-spacing:-.01em}
.mbtn{display:none}

/* first screen */
.hero{position:relative;height:calc(100vh - 50px);min-height:520px;overflow:hidden;background:var(--d);color:#fff}
.sl{position:absolute;inset:0;opacity:0;transition:opacity .3s ease}
.sl.on{opacity:1}
.sl img{width:100%;height:100%;object-fit:cover}
.hveil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.15) 0,rgba(0,0,0,.15) 20%,rgba(0,0,0,.57) 44%,rgba(0,0,0,.57) 100%)}
.hero:not(.pic){height:75vh}
.cap{position:absolute;left:48px;width:75vw;top:60%;transform:translateY(-50%)}
.cap h1{margin-bottom:30px;max-width:22em}
.harr{position:absolute;left:37px;bottom:36px;display:flex;gap:19px}
.harr button{width:35px;height:35px;color:#fff;display:none}
.js .harr button{display:block}
.harr svg{width:35px;height:35px}
.hprev svg{transform:scaleX(-1)}

/* the page under it: two hairlines run its whole length at 1/6 and 1/2 */
main{position:relative;padding-top:50px}
main::before,main::after,.s3::before,.s3::after{content:"";position:absolute;top:0;bottom:0;width:1px;background:var(--line);left:16.6667vw;pointer-events:none}
main::after,.s3::after{left:50vw}
section{position:relative;margin-bottom:85px}
.row{display:flex;padding-left:16.6667vw}
.col{width:33.3333vw;padding:0 50px 0 15px}
.col p{max-width:415px}
.col h2{margin-bottom:30px;max-width:415px}
.col p+p,.col .lab+h2{margin-top:27.2px}
.col h2+p{margin-top:0}
.col .lab{margin-bottom:27.2px}
.col .lab+h2{margin-top:0}
.s1.hascar .row{padding-bottom:60px}
.car{position:relative}
.track{display:flex;gap:15px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding-left:calc(16.6667vw + 4px);scroll-padding-left:calc(16.6667vw + 4px)}
.track::-webkit-scrollbar{display:none}
.track:focus-visible{outline-offset:-3px}
.sq{flex:0 0 min(calc((66.6667vw - 19px)/2),var(--sqmax,600px));aspect-ratio:1;scroll-snap-align:start}
.sq img{width:100%;height:100%;object-fit:cover}
.end{flex:0 0 calc(16.6667vw - 15px)}
.cbtn{position:absolute;top:50%;margin-top:-26px;width:52px;height:52px;border-radius:50%;background:var(--g);color:var(--i);display:grid;place-items:center}
.cbtn[hidden]{display:none}
.cnext{right:48px}.cprev{left:48px}.cprev svg{transform:scaleX(-1)}
.band{z-index:1}
.band img{width:100%;height:min(100vh,max(calc(100vw*var(--r)),var(--nh,0px)));object-fit:cover}
.s5{z-index:1}
.wide{width:65.625vw;padding-right:15px;background:var(--g)}
.wide img{width:100%;aspect-ratio:945/591;object-fit:cover}
.s5.rev .wide{margin-left:auto;padding:0 0 0 15px}

/* the deep section: a row of cards that runs off the right edge */
.s3{background:var(--d);color:#fff;padding:40px 0 60px;margin-bottom:0;z-index:1}
.s3.gap{margin-bottom:85px}
.s3::before,.s3::after{background:rgba(255,255,255,.5)}
.card{flex:0 0 calc((66.6667vw - 19px)/2);padding-right:15px;scroll-snap-align:start;display:flex;flex-direction:column}
.chead{min-height:108px;display:flex;align-items:flex-end;padding-left:15px;margin-bottom:15px}
.s3.words .chead{min-height:54px}
.s3.words .card{flex-basis:calc((66.6667vw - 34px)/3)}
.s3.words .cbody{padding-right:20px}
.s3.words .cbtn{top:auto;bottom:-56px;margin-top:0}  /* no picture to stand on: the arrows stand in the lower margin, under the text */
.cpic{width:min(100%,var(--fw,456px));aspect-ratio:1/var(--fr,1);overflow:hidden}
.cpic img{width:100%;height:100%;object-fit:cover}
.cbody{margin-top:40px;padding:0 50px 0 15px}
.s3.words .cbody{margin-top:25px}
.cbody .lab+p{margin-top:14px}
.cbody .cta{margin-top:15px}

/* a picture band with words over it */
.over{z-index:1;min-height:100vh;display:flex;align-items:center;color:#fff;overflow:hidden;background:var(--d)}
.over.low{min-height:75vh}
.over>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.oveil{position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.57) 0,rgba(0,0,0,.57) 46%,rgba(0,0,0,.2) 78%)}
.otext{position:relative;margin:80px 0 80px calc(16.6667vw + 30px);width:350px}
.otext .lab{margin-bottom:60px}
.otext h2{margin-bottom:30px}
.otext p+p{margin-top:27.2px}
.lk{margin-top:27.2px}
.col .lk:first-child{margin-top:0}

/* the menu, in the text row: lines of names, a table where there are prices */
.ml+.ml,.ml+.mt,.mt+.ml,.mn+.ml,.mn+.mt,.mt+.mt{margin-top:27.2px}
.ml li{max-width:415px}
.mt{border-collapse:collapse;width:100%;max-width:415px}
.mt caption{text-align:left;text-transform:uppercase;padding-bottom:8px}
.mt th{font-weight:400;text-align:left;padding:5px 12px 5px 0;border-top:1px solid var(--line)}
.mt td{text-align:right;white-space:nowrap;padding:5px 0;border-top:1px solid var(--line);font-variant-numeric:lining-nums tabular-nums}
.mt tr:last-child th,.mt tr:last-child td{border-bottom:1px solid var(--line)}
.mn{margin-top:8px;font-size:14px}

/* foot */
.foot{position:relative;padding:25px 0 12px}
.foot::before{content:"";position:absolute;left:0;right:0;top:0;height:1px;background:var(--line)}
.fname{font-size:44px;line-height:1;letter-spacing:-.02em;margin:50px 48px 0}
.frow{display:flex;margin-top:25px}
.fc{padding:0 15px}
.f1{width:33.3333vw;padding-left:48px}.f1 ul{margin-top:38px}
.f2{width:33.3333vw;display:flex}.f2 ul{width:240px;max-width:50%}
.f3{width:16.6667vw}.f3 li+li{margin-top:19px}
.f4{width:16.6667vw;padding-right:48px;display:flex;justify-content:flex-end}
.f4 .legal:not(:first-child){margin-top:38px}
.note{opacity:.9}
.fnot{margin:25px 48px 0}
.notice p{max-width:60ch;font-size:14px;margin-top:8px}
.foot{padding-bottom:62px}

/* arrival: headings rise 10px and clear in a second, pictures clear in a second */
@media (prefers-reduced-motion:no-preference){
.cap h1,.cap p{animation:in 1s ease .2s both}
.hero.pic .sl img{animation:fade 1s ease both}
.js section h2,.js section h3{opacity:0;transform:translateY(10px);transition:opacity 1s ease,transform 1s ease}
.js section img{opacity:0;transition:opacity 1s ease}
.js section.vis h2,.js section.vis h3{opacity:1;transform:none}
.js section.vis img{opacity:1}
}
@keyframes in{from{opacity:0;transform:translateY(10px)}}
@keyframes fade{from{opacity:0}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;scroll-behavior:auto!important}}

/* phone */
@media (max-width:899px){
h1{font-size:22px}h2{font-size:34px}h3{font-size:24px}
.bar{height:56px;line-height:56px;justify-content:flex-end;padding:0 20px}
.ba,.bb,.bd{display:none}
.bn{position:absolute;left:50%;top:0;height:56px;transform:translateX(-50%);width:auto;max-width:calc(100% - 250px);padding:0;text-align:center;font-size:15px}
.bbook{width:auto;background:none;color:var(--i);text-transform:none;font-size:22px}
a.bbook:hover{background:none;opacity:.8}
.bbook:focus-visible{outline-offset:3px}
.hamb{left:12px;top:2px;background:none;border-radius:0}
.hamb span{left:8px;width:36px}.hamb span::before,.hamb span::after{width:36px}
.hamb span::before{top:-8px}.hamb span::after{top:8px}
.hamb[aria-expanded=true]{color:var(--i)}
.hamb[aria-expanded=true] span::before,.hamb[aria-expanded=true] span::after{left:5px}
.mark{right:auto;left:50%;top:6px;width:43px;margin-left:-21.5px}
.menu{inset:56px 0 0 0;background:var(--d);padding:38px 20px 40px}
.menu ul{display:block}
.menu li a{font-size:30px;padding:3px 0 4px}
.mbtn{display:block;margin-top:15px;height:50px;line-height:50px;font-size:30px;text-align:center;background:var(--g);color:var(--i)}
.hero{height:100vh;height:100svh;margin-top:-56px;min-height:480px}
.hero:not(.pic){height:75vh}
.s3.words .card{flex-basis:61.5vw}
.hveil{background:linear-gradient(180deg,rgba(0,0,0,.57) 0,rgba(0,0,0,.57) 46%,rgba(0,0,0,.15) 68%)}
.cap{left:20px;right:20px;width:auto;top:122px;transform:none}
.harr{left:auto;right:21px;bottom:34px;gap:15px}
.harr button,.harr svg{width:30px;height:30px}
main{padding-top:38px}
main::before{left:20px}main::after,.s3::before,.s3::after{display:none}
section{margin-bottom:45px}
.row{display:block;padding-left:0}
.col{width:auto;padding:0 50px 0 35px}
.col+.col:not(:empty){margin-top:30px}
.col p,.col h2{max-width:none}
.track{gap:20px;padding-left:21px;scroll-padding-left:21px}
.sq{flex-basis:min(61.3vw,var(--sqmax,600px))}
.end{flex-basis:1px}
.cbtn{display:none}
.band img{height:calc(100vw*var(--r))}
.wide,.s5.rev .wide{width:100%;padding:0}
.wide img{aspect-ratio:390/244}
.s3{padding:40px 0 60px}.s3.gap{margin-bottom:45px}
.card{flex-basis:61.5vw}
.chead{min-height:48px;padding-left:0}
.s3.words .chead{min-height:48px}
.cpic{width:min(100%,var(--fw,456px))}
.cbody{margin-top:20px;padding:0}
.s3.words .cbody{margin-top:10px}
.cbody .cta{margin-top:10px}
.over,.over.low{min-height:0;display:block}
.oveil{background:rgba(0,0,0,.57)}
.otext{margin:0;width:auto;padding:60px 50px 60px 35px}
.s4.carta+.s5{display:flex;flex-direction:column}
.foot{padding:0 20px 40px}
.fname{font-size:34px;margin:45px 0 0}
.frow{display:block;margin-top:20px}
.fc{width:auto;padding:0;margin-top:25px}
.f1 ul{margin-top:19px}
.f2 ul{width:50%}
.f4{justify-content:flex-start}
.fnot{margin:25px 0 0}
}
'''

JS = r'''
(function(){var D=document,H=D.documentElement;H.classList.add('js');
var rm=matchMedia('(prefers-reduced-motion:reduce)').matches;
/* sections arrive once */
var ss=[].slice.call(D.querySelectorAll('main section'));
if('IntersectionObserver' in window&&!rm){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('vis');io.unobserve(x.target)}})},{rootMargin:'0px 0px -8% 0px'});ss.forEach(function(s){io.observe(s)})}
else ss.forEach(function(s){s.classList.add('vis')});
/* menu */
var hb=D.querySelector('.hamb'),nav=D.getElementById('nav');
if(hb&&nav){var set=function(o){nav.classList.toggle('open',o);hb.setAttribute('aria-expanded',o);hb.setAttribute('aria-label',o?hb.dataset.close:hb.dataset.open);if(o){var f=nav.querySelector('a');f&&f.focus({preventScroll:true})}};
hb.addEventListener('click',function(){set(hb.getAttribute('aria-expanded')!=='true')});
D.addEventListener('keydown',function(e){if(e.key==='Escape'&&nav.classList.contains('open')){set(false);hb.focus()}});
nav.addEventListener('click',function(e){if(e.target.closest('a'))set(false)})}
/* first screen: pictures change by a .3s fade about every 4.3s; arrows step */
var sl=[].slice.call(D.querySelectorAll('.hero .sl'));
if(sl.length>1){var i=0,t,go=function(n){sl[i].classList.remove('on');i=(n+sl.length)%sl.length;sl[i].classList.add('on')},
run=function(){clearInterval(t);if(!rm)t=setInterval(function(){go(i+1)},4350)};
D.querySelector('.hnext').addEventListener('click',function(){go(i+1);run()});
D.querySelector('.hprev').addEventListener('click',function(){go(i-1);run()});
var he=D.querySelector('.hero');he.addEventListener('mouseenter',function(){clearInterval(t)});he.addEventListener('mouseleave',run);he.addEventListener('focusin',function(){clearInterval(t)});
D.addEventListener('visibilitychange',function(){D.hidden?clearInterval(t):run()});run()}
/* rows that run off the edge: one step per press, .3s */
[].forEach.call(D.querySelectorAll('.car'),function(c){var tr=c.querySelector('.track'),p=c.querySelector('.cprev'),n=c.querySelector('.cnext');if(!tr||!p||!n)return;
var step=function(){var f=tr.children[0];return f?f.getBoundingClientRect().width+parseFloat(getComputedStyle(tr).columnGap||0):300},
upd=function(){var max=tr.scrollWidth-tr.clientWidth;p.hidden=tr.scrollLeft<8;n.hidden=max<8||tr.scrollLeft>max-8};
p.addEventListener('click',function(){tr.scrollBy({left:-step(),behavior:rm?'auto':'smooth'})});
n.addEventListener('click',function(){tr.scrollBy({left:step(),behavior:rm?'auto':'smooth'})});
tr.addEventListener('scroll',upd,{passive:true});addEventListener('resize',upd);upd()});
})();
'''


def render(d: dict) -> str:
    place = d.get('place') or {}
    b = d.get('brand') or {}
    th = _theme(d.get('palette') or {})
    lang = (d.get('lang') or 'en')[:2]
    words = WORDS.get(lang, WORDS['en'])
    S = _slots(d)
    r, g, bl = _rgb(th['deep'])
    hamb, nav = _menu(d, place, words)
    mark = (f'<a class="mark" href="{e(b.get("home") or "#")}"><img src="{e(src(b["logo"]))}" alt="{e(b.get("name"))}"></a>'
            if b.get('logo') else '')
    event = _event(place, S)
    close = _close(d, place, S)
    carta = _carta(d, place, S)
    # the deep section runs straight into a picture band, as measured; into anything else it keeps the section gap
    cards = _cards(d, place, S, words, gap_after=not (event and S['event']))
    main = _intro(d, S, words) + _band(S) + _rooms(d, S) + cards + event + carta + close
    hero = d.get('hero') or {}
    desc = hero.get('text') or (d.get('statement') or {}).get('text') or ''
    return f'''<!doctype html>
<html lang="{e(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(b.get("name"))}</title>
<meta name="description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>:root{{--g:{th['g']};--i:{th['ink']};--d:{th['deep']};--dd:{th['deeper']};--dm:rgba({r},{g},{bl},.9);--line:{th['line']}}}{CSS}</style>
</head>
<body>
{_bar(d, place, words)}
{hamb}{mark}{nav}
{_hero(d, S, words)}
<main>
{main}
</main>
{_foot(d, place)}
<script>{JS}</script>
</body>
</html>'''
