"""newground/render.py — one pure function: render(d) -> a complete page. A template for SHOPS (and other small
businesses that sell priced things from a door: it is also built with a restaurant's menu).

The build — announcement bar, sticky header with its drop panel, two half-screen picture panels that become a
self-advancing carousel on a phone, product rows under an 80px capital heading, a second pair of panels, full-width
picture bands with centred words, the dark foot with one very large line — was measured on the reference's home page
and on its listing page at 1440 and 390 on 2026-11-12 (see NOTES.md, ref/). Nothing of the reference's code, words,
pictures, marks or display typeface is here. The client's data fills it; a part whose data is missing is left out whole.
No model call, no file reads, no client logic. Pictures are the client's own photographs, chosen by role, size and
proportion, each used once.
"""
import html
import math
import re
import unicodedata

FONTS = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Inter+Tight:wght@600&display=swap'
MEDIA = '../../'
MORE = {'en': 'More', 'es': 'Más', 'de': 'Mehr', 'fr': 'Plus', 'it': 'Altro', 'pt': 'Mais', 'nl': 'Meer', 'sr': 'Još',
        'sl': 'Več', 'hr': 'Više'}
CLOSE = {'en': 'Close', 'es': 'Cerrar', 'de': 'Schließen', 'fr': 'Fermer', 'it': 'Chiudi', 'pt': 'Fechar',
         'nl': 'Sluiten', 'sr': 'Zatvori', 'sl': 'Zapri', 'hr': 'Zatvori'}


def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


# ───────────────────────── colour: the reference is ink on a white ground, one accent bar, a foot in the ink
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


def _lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def _con(a, b):
    x, y = _lum(a), _lum(b)
    return (max(x, y) + .05) / (min(x, y) + .05)


def _mix(a, b, t):
    """a moved toward b by t (0 = a, 1 = b)"""
    x, y = _rgb(a), _rgb(b)
    return _hex([x[i] + (y[i] - x[i]) * t for i in range(3)])


def _muted(ink, ground, t=.4, want=4.7):
    """the reference's 60% ink for second lines — held at a strength that still reads on this ground"""
    while t > 0 and _con(_mix(ink, ground, t), ground) < want:
        t -= .04
    return _mix(ink, ground, max(t, 0))


def _on(ground, a='#ffffff', b='#000000'):
    return a if _con(a, ground) >= _con(b, ground) else b


# ───────────────────────── small helpers
def _norm(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def _lnk(o):
    return (o or {}).get('h') or ''


def _a(href, inner, cls='', extra=''):
    """a link when there is an address, the same box without one"""
    c = f' class="{cls}"' if cls else ''
    if href:
        return f'<a{c} href="{e(href)}"{extra}>{inner}</a>'
    return f'<div{c}{extra}>{inner}</div>'


def _img(p, cls='', lazy=True, sizes=''):
    return (f'<img{" class=" + chr(34) + cls + chr(34) if cls else ""} src="{MEDIA}{e(p["src"])}" alt="{e(p.get("alt") or "")}" '
            f'width="{int(p.get("w") or 0)}" height="{int(p.get("h") or 0)}"{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""} decoding="async">')


def render(d: dict) -> str:
    lang = (d.get('lang') or 'en')[:2]
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    pal = d.get('palette') or {}
    ground = pal.get('ground') or '#ffffff'
    ink = pal.get('ink') or '#000000'
    accent = pal.get('accent') or ink
    if _con(ink, ground) < 7:                       # the reference's ink is black on white; keep that relation
        ink = _on(ground, '#ffffff', '#0a0a0a') if _con(ink, ground) < 4.5 else ink
    light = _lum(ground) > .4
    dark = ink if light else _mix(ground, '#000000', .45)      # the foot and a panel without a picture
    on_dark = '#ffffff'
    if _con(on_dark, dark) < 7:
        dark = _mix(dark, '#000000', .5)
    tile = _mix(ground, ink, .045)                  # the reference's #f4f4f4 on white: the ground with 4.5% ink
    tile2 = _mix(ground, ink, .08)                  # its hover, #ebebeb
    muted = _muted(ink, ground)
    foot_muted = _muted(on_dark, dark)
    acc_ink = _on(accent)
    line_dark = _mix(dark, on_dark, .18)

    hero = d.get('hero') or {}
    place = d.get('place') or {}
    contact = d.get('contact') or {}
    media = d.get('media') or {}
    photos = [p for p in (media.get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
    by_src = {p['src']: p for p in photos}
    used = set()

    # ───────────────────────── what is sold: catalogue groups, and a menu's sections that list their items
    cat = d.get('catalogue') or {}
    groups = [dict(g) for g in (cat.get('groups') or []) if g.get('items')]   # copies: render never writes into the data
    menu = place.get('menu') or {}
    groups += [dict(g, text=g.get('text') or '') for g in (menu.get('sections') or []) if g.get('items')]
    index_rows = [s for s in (menu.get('sections') or []) if not s.get('items') and s.get('t')] + \
                 [s for s in (menu.get('lists') or []) if s.get('t')]

    def own_picture(it, roles=('product', 'dish', 'work', 'detail')):
        """an item's picture: the one the data names, else a product photograph whose description starts with the
        item's name (a join on the data — the description itself is never set as copy)"""
        p = by_src.get(it.get('img') or '')
        if p and p['src'] not in used:
            return p
        n = _norm(it.get('name'))
        if len(n) < 4:
            return None
        for p in photos:
            if p['src'] in used or p.get('role') not in roles:
                continue
            a = _norm(p.get('alt'))
            if a == n or a.startswith(n + ' '):
                return p
        return None

    for g in groups:                                 # products first: a card keeps its own picture
        g['_cards'], g['_rows'] = [], []
        for it in g['items']:
            p = own_picture(it)
            if p:
                used.add(p['src'])
                g['_cards'].append((it, p))
            else:
                g['_rows'].append(it)

    def pick(kind, ranks, role=None):
        """a photograph for a half panel (720×786 at 1440, upright on a phone) or a full band (1440×786): never a
        small one, never a portrait of a person, the nearest in proportion among the best-ranked roles"""
        best = None
        for i, p in enumerate(photos):
            if p['src'] in used or p.get('small') or p.get('role') == 'portrait':
                continue
            if role and p.get('role') != role:
                continue
            w, h = p['w'], p['h']
            r = w / h
            if kind == 'half':
                ok, target = min(w, h) >= 780 and .55 <= r <= 1.9, .92
            else:
                ok, target = w >= 1600 and h >= 780 and .9 <= r <= 2.6, 1.83
            if not ok:
                continue
            key = (ranks.get(p.get('role'), 6), abs(math.log(r / target)), i)
            if best is None or key < best[0]:
                best = (key, p)
        if best:
            used.add(best[1]['src'])
            return best[1]
        return None

    R_LEAD = dict(product=0, dish=0, work=0, detail=1, room=2, bar=2, workshop=2, exterior=3, landscape=3, people=4, action=4)
    R_ROOM = dict(room=0, bar=0, workshop=0, people=1, action=1, exterior=2, landscape=2, detail=3, product=4, dish=4, work=4)
    R_DOOR = dict(exterior=0, room=1, bar=1, workshop=1, people=2, landscape=2, action=3, detail=4, product=5, dish=5, work=5)

    def block_picture(src, title, kind):
        """the picture a block names; when that one is small, the larger one a room of the same title has; when there
        is none, an unused photograph of the same role"""
        p = by_src.get(src or '')
        if p and not p.get('small') and p['src'] not in used:
            used.add(p['src'])
            return p
        for sp in place.get('spaces') or []:
            q = by_src.get(sp.get('img') or '')
            if q and not q.get('small') and q['src'] not in used and _norm(sp.get('title')) == _norm(title):
                used.add(q['src'])
                return q
        if p and p.get('role'):
            return pick(kind, {}, role=p['role'])
        return None

    # ───────────────────────── the blocks that become picture panels and bands
    st = d.get('statement') or {}
    steps = [s for s in ((d.get('steps') or {}).get('items') or []) if s.get('title') or s.get('text')]
    close = d.get('close') or {}
    twin = next((s for s in steps if st.get('title') and _norm(s.get('title')) == _norm(st.get('title'))), None)
    if twin:
        steps = [s for s in steps if s is not twin]

    # opening pair: the hero, and the statement beside it
    hero_a = dict(t=hero.get('title') or name, x=[hero.get('text'), hero.get('text2')], cta=hero.get('primary') or d.get('cta'))
    hero_a['p'] = pick('half', R_LEAD)
    hero_b = None
    if st.get('title') or st.get('text'):
        b_cta = (twin or {}).get('cta') or hero.get('secondary')
        hero_b = dict(t=st.get('title'), x=[st.get('text')], cta=b_cta)
        hero_b['p'] = (block_picture(twin.get('img'), twin.get('title'), 'half') if twin else None) or pick('half', R_ROOM)
    elif hero.get('secondary'):
        hero_a['cta2'] = hero.get('secondary')

    def step_block(s, kind):
        return dict(k=s.get('k'), t=s.get('title'), x=[s.get('text')], cta=s.get('cta'),
                    p=block_picture(s.get('img'), s.get('title'), kind) or (pick(kind, R_ROOM) if not s.get('img') else None))

    pairs, bands = [], []
    i = 0
    while len(steps) - i >= 2 and len(pairs) < 2:
        pairs.append([step_block(steps[i], 'half'), step_block(steps[i + 1], 'half')])
        i += 2
        if len(steps) - i == 1:
            break
    for s in steps[i:]:
        bands.append(step_block(s, 'band'))
    if close.get('title') or close.get('text'):
        bands.append(dict(t=close.get('title'), x=[close.get('text')], cta=close.get('cta'), p=pick('band', R_DOOR)))

    # a group none of whose items has a picture opens with the group's own picture as a band, when it has one
    for g in groups:
        g['_band'] = None
        if not g['_cards']:
            p = by_src.get(g.get('img') or '')
            if not p:
                p = next((q for q in photos if _norm(q.get('alt')) == _norm(g.get('t')) and q['src'] not in used), None)
            if p and not p.get('small') and p['src'] not in used and p['w'] >= 1600 and p['h'] >= 780:
                used.add(p['src'])
                g['_band'] = p

    # ───────────────────────── parts
    NOHEAD = '<p class="ft-h">&nbsp;</p>'

    def wrap(tag, cls, inner):
        return f'<{tag} class="{cls}">{inner}</{tag}>' if inner else ''

    def opt(cls, text, tag='p'):
        return f'<{tag}{" class=" + chr(34) + cls + chr(34) if cls else ""}>{e(text)}</{tag}>' if text else ''

    def btn(label, cls='btn-w', tag='span', href=''):
        if not label:
            return ''
        if tag == 'a':
            return f'<a class="btn {cls}" href="{e(href)}"><span>{e(label)}</span></a>'
        return f'<span class="btn {cls}"><span>{e(label)}</span></span>'

    def panel(b, htag='h2', first=False):
        pic = b.get('p')
        txt = ''.join(f'<p class="pan-x">{e(x)}</p>' for x in b.get('x') or [] if x)
        cta = b.get('cta') or {}
        inner = (f'<span class="pan-m">{_img(pic, lazy=not first)}</span>' if pic else '') + \
                f'<span class="pan-c"><{htag} class="pan-t">{e(b.get("t") or "")}</{htag}>{txt}{btn(cta.get("t"))}</span>'
        return _a(_lnk(cta), inner, 'pan' + ('' if pic else ' pan-plain'))

    def band(b):
        pic = b.get('p')
        txt = ''.join(f'<p class="band-x">{e(x)}</p>' for x in b.get('x') or [] if x)
        cta = b.get('cta') or {}
        inner = (f'<span class="band-m">{_img(pic)}</span>' if pic else '') + \
                f'<span class="band-o"><span class="band-c"><h2 class="band-t">{e(b.get("t") or "")}</h2>{txt}{btn(cta.get("t"))}</span></span>'
        return f'<section class="blk">{_a(_lnk(cta), inner, "band" + ("" if pic else " band-plain"))}</section>'

    def duo(a, b, cls='', htag='h2'):
        if not b:
            return f'<section class="blk duo duo-1 {cls}">{panel(a, htag, first=bool(cls))}</section>'
        dots = '<span class="dots" aria-hidden="true"><i class="on"></i><i></i></span>' if cls else ''
        return (f'<section class="blk duo {cls}"><div class="duo-w">{panel(a, htag, first=bool(cls))}{panel(b, "h2", first=bool(cls))}</div>{dots}</section>')

    def price_of(it):
        out = []
        if it.get('price'):
            out.append(f'<span>{e(it["price"])}</span>')
        for pr in it.get('prices') or []:
            out.append(f'<span>{e(pr.get("label") or "")} {e(pr.get("price") or "")}</span>')
        return ''.join(out)

    def sub_of(it):
        return ' · '.join(x for x in [it.get('text'), it.get('note')] if x)

    def card(it, p):
        cap = f' style="max-width:{int(p["w"])}px"' if p.get('small') else ''
        state = f'<span class="state">{e(it["state"])}</span>' if it.get('state') else ''
        desc = f'<p class="card-x">{e(sub_of(it))}</p>' if sub_of(it) else ''
        rows = ''.join(f'<p class="card-x">{e(r)}</p>' for r in it.get('rows') or [])
        inner = (f'<span class="card-im">{_img(p)}</span><span class="card-d"><h3 class="card-t">{e(it.get("name") or "")}</h3>'
                 f'{desc}{rows}<span class="card-p">{price_of(it)}{state}</span></span>')
        return f'<li class="card-li"{cap}>{_a(it.get("h"), inner, "card")}</li>'

    def row(a, b='', sub='', href='', state=''):
        st_ = f'<span class="state">{e(state)}</span>' if state else ''
        sub_ = f'<span class="row-x">{e(sub)}</span>' if sub else ''
        inner = f'<span class="row-l"><span class="row-t">{e(a)}</span>{sub_}</span><span class="row-p">{b}{st_}</span>'
        return f'<li>{_a(href, inner, "row")}</li>'

    def rows_list(items, two=False):
        return f'<ul class="rows{" rows-2" if two else ""}">{"".join(items)}</ul>' if items else ''

    def head(title, pill=None, href=''):
        if not title and not pill:
            return ''
        t = e(title or '')
        if href and not pill:
            t = f'<a href="{e(href)}">{t}</a>'
        return f'<div class="sec-h"><h2 class="sec-t">{t}</h2>{btn(pill, "btn-g", "a", href) if pill and href else opt("sec-n", pill, "span")}</div>'

    def group_section(g):
        out = []
        cards, rws = g['_cards'], g['_rows']
        pill = g.get('text') or (str(g['count']) if g.get('count') else None)
        if g['_band']:
            inner = (f'<span class="band-m">{_img(g["_band"])}</span><span class="band-o"><span class="band-c">'
                     f'<h2 class="band-t">{e(g.get("t") or "")}</h2>{btn(pill)}</span></span>')
            out.append(_a(g.get('h'), inner, 'band'))
        else:
            out.append(head(g.get('t'), pill, g.get('h')))
        if cards:
            out.append(f'<ul class="cards{" cards-run" if len(cards) > 3 else ""}">{"".join(card(it, p) for it, p in cards)}</ul>')
        if rws:
            out.append(rows_list([row(it.get('name'), price_of(it), sub_of(it), it.get('h'), it.get('state')) for it in rws], two=len(rws) > 6))
        return f'<section class="blk sec{" sec-b" if g["_band"] else ""}">{"".join(out)}</section>'

    # ───────────────────────── header
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    links = [l for l in (d.get('links') or []) if l.get('t')]
    cta = d.get('cta') or {}
    signin = d.get('signin') or {}
    n = max(len(name), 1)
    logo_d = 34 if n <= 12 else max(18, round(34 * 12 / n))
    logo_m = 22 if n <= 12 else max(13, round(22 * 12 / n))
    budget = (1440 - n * logo_d * .62) / 2 - 60 - 62          # the left third at 1440, less its padding and "More"
    shown, wsum = 0, 0
    for it in nav:
        wsum += len(it['t']) * 10.3 + 15
        if wsum > budget:
            break
        shown += 1
    more_w = MORE.get(lang, MORE['en'])
    kicker = hero.get('kicker') or ((d.get('trust') or [None])[0])
    bar = (f'<div class="bar" id="bar"><p>{e(kicker)}</p><button class="bar-x" type="button" aria-label="{e(CLOSE.get(lang, "Close"))}"></button></div>'
           if kicker else '')
    menu_big = ''.join(f'<li><a href="{e(i_["h"])}">{e(i_["t"])}</a></li>' for i_ in nav if i_.get('h'))
    nav_h = {i_.get('h') for i_ in nav}
    menu_small = ''.join(f'<li><a href="{e(l["h"])}">{e(l["t"])}</a></li>' for l in links if l.get('h') and l['h'] not in nav_h)
    menu_cta = (btn(cta.get('t'), 'btn-k', 'a', cta.get('h')) if cta.get('t') and cta.get('h') else '') + \
               (f'<a class="menu-s" href="{e(signin["h"])}">{e(signin["t"])}</a>' if signin.get('t') and signin.get('h') else '')
    header = f'''<header class="hd">{bar}
<div class="hd-in">
<nav class="hd-l" aria-label="{e(name)}"><ul class="hd-nav">{"".join(f'<li{"" if k < shown else " class=over"}><a href="{e(i_.get("h") or "#")}">{e(i_["t"])}</a></li>' for k, i_ in enumerate(nav))}</ul>
<details class="more"><summary><span class="more-w">{e(more_w)}</span><span class="more-b" aria-hidden="true"></span></summary>
<div class="menu"><div class="menu-in"><ul class="menu-big">{menu_big}</ul>{f'<ul class="menu-small">{menu_small}</ul>' if menu_small else ''}<div class="menu-f">{menu_cta}</div></div></div></details></nav>
<a class="logo" href="{e(brand.get("home") or "#")}" style="--ld:{logo_d}px;--lm:{logo_m}px">{e(name)}</a>
<div class="hd-r">{f'<a class="hd-s" href="{e(signin["h"])}">{e(signin["t"])}</a>' if signin.get('t') and signin.get('h') else ''}{btn(cta.get('t'), 'btn-k btn-s', 'a', cta.get('h')) if cta.get('t') and cta.get('h') else ''}</div>
</div></header>'''

    # ───────────────────────── main: the reference's order — pair, products, pair, products, bands
    main = [duo(hero_a, hero_b, 'hero', 'h1')]
    gs = [group_section(g) for g in groups]
    ps = [duo(a, b) for a, b in pairs]
    k = 0
    while gs or ps:
        if gs:
            main.append(gs.pop(0))
        if ps:
            main.append(ps.pop(0))
        k += 1

    # the menu's index (sections that only say how many, further lists) — or, when there is no menu, the features list
    feats = d.get('features') or {}
    f_items = [f for f in (feats.get('items') or []) if f.get('t')]
    idx_names = {_norm(s['t']) for s in index_rows}
    if index_rows:
        lab = next((x['t'] for x in links + nav if menu.get('h') and x.get('h') == menu['h']), None)
        main.append(f'<section class="blk sec">{head(lab, None, menu.get("h"))}'
                    f'{rows_list([row(s["t"], e(s["count"]) if s.get("count") else "", "", s.get("h")) for s in index_rows], two=len(index_rows) > 6)}</section>')
    if f_items and not all(_norm(f['t']) in idx_names for f in f_items):
        main.append(f'<section class="blk sec">{head(feats.get("title"))}'
                    f'{rows_list([row(f["t"], "", f.get("d")) for f in f_items], two=len(f_items) > 6)}</section>')

    # plans: the product card without a picture, the price in the heading size
    plans = d.get('plans') or {}
    p_items = [p for p in (plans.get('items') or []) if p.get('name')]
    if p_items:
        cards_ = []
        for p in p_items:
            rws = ''.join(f'<li>{e(r)}</li>' for r in p.get('rows') or [])
            c = p.get('cta') or {}
            cards_.append(f'<li class="plan"><h3 class="card-t">{e(p["name"])}</h3>{opt("card-x", p.get("line"))}'
                          f'<p class="plan-p"><span>{e(p.get("price") or "")}</span>{opt("", p.get("per"), "small")}</p>'
                          f'{wrap("ul", "plan-r", rws)}'
                          f'{btn(c.get("t"), "btn-k" if p.get("marked") else "btn-g", "a", c.get("h")) if c.get("t") and c.get("h") else ""}</li>')
        main.append(f'<section class="blk sec">{head(plans.get("title"))}{opt("sec-x", plans.get("text"))}'
                    f'<ul class="plans">{"".join(cards_)}</ul>{opt("sec-x", plans.get("note"))}</section>')

    # people: a card when the person has a portrait of their own, a row in type when not
    team = d.get('team') or {}
    people = list(team.get('items') or []) + [p for g in (team.get('groups') or []) for p in (g.get('items') or [])]
    people = [p for p in people if p.get('name')]
    if people:
        withp, without = [], []
        for p in people:
            ph = by_src.get(p.get('img') or '')
            if ph and ph['src'] not in used:
                used.add(ph['src'])
                withp.append((dict(name=p['name'], text=p.get('role'), note=p.get('text'), h=p.get('h')), ph))
            else:
                without.append(p)
        body = (f'<ul class="cards{" cards-run" if len(withp) > 3 else ""}">{"".join(card(it, ph) for it, ph in withp)}</ul>' if withp else '') + \
            rows_list([row(p['name'], e(p.get('role') or ''), p.get('text'), p.get('h')) for p in without])
        main.append(f'<section class="blk sec">{head(team.get("title"))}{opt("sec-x", team.get("text"))}{body}</section>')

    creds = [c for c in (d.get('credentials') or []) if c.get('t')]
    if creds:
        main.append(f'<section class="blk sec">{rows_list([row(c["t"], e(c.get("year") or ""), c.get("text"), c.get("h")) for c in creds])}</section>')

    locs = [l for l in (d.get('locations') or []) if l.get('name')]

    def addr_line(a):
        a = a or {}
        return ', '.join(x for x in [a.get('street'), ' '.join(y for y in [a.get('postcode'), a.get('city')] if y), a.get('region')] if x)

    def hours_line(hs):
        return ' · '.join(f'{h_.get("days")} {h_.get("open")}–{h_.get("close")}' if h_.get('open') else str(h_.get('days'))
                          for h_ in hs or [] if h_.get('days'))

    if locs:
        main.append(f'<section class="blk sec">{rows_list([row(l["name"], e((l.get("phone") or {}).get("t") if isinstance(l.get("phone"), dict) else (l.get("phone") or "")), " · ".join(x for x in [addr_line(l.get("address")), hours_line(l.get("hours")), l.get("note")] if x), l.get("h")) for l in locs])}</section>')

    faq = d.get('faq') or {}
    q_items = [q for q in (faq.get('items') or []) if q.get('q')]
    if q_items:
        main.append(f'<section class="blk sec">{head(faq.get("title"))}<div class="faq">'
                    + ''.join(f'<details><summary><span>{e(q["q"])}</span><i aria-hidden="true"></i></summary><p>{e(q.get("a") or "")}</p></details>' for q in q_items)
                    + '</div></section>')

    main += [band(b) for b in bands]

    # ───────────────────────── foot: the very large line is how to reach the shop; then the map of the site, contact, the door
    phone = place.get('phone') or contact.get('phone') or {}
    email = place.get('email') or contact.get('email') or ''
    booking = place.get('booking') or contact.get('form') or {}
    big = phone.get('t') or email
    big_h = phone.get('h') if phone.get('t') else (f'mailto:{email}' if email else '')
    reach = ''
    if big:
        under = ' · '.join(x for x in [phone.get('note'), email if phone.get('t') else ''] if x)
        reach = (f'<div class="reach"><div class="reach-r"><a class="reach-b" href="{e(big_h)}" style="--n:{max(len(big), 6)}">{e(big)}</a>'
                 f'{btn(booking.get("t"), "btn-w", "a", booking.get("h")) if booking.get("t") and booking.get("h") else ""}</div>'
                 f'{opt("reach-x", under)}</div>')
    site_links = links or nav
    half = (len(site_links) + 1) // 2
    cols = [site_links[:half], site_links[half:]] if len(site_links) > 5 else [site_links]
    sitemap = ''
    if site_links:
        sitemap = (f'<div class="ft-col ft-map"><p class="ft-h">{e(name)}</p><div class="ft-2">'
                   + ''.join('<ul>' + ''.join(f'<li><a href="{e(l.get("h") or "#")}">{e(l["t"])}</a></li>' for l in c) + '</ul>' for c in cols if c)
                   + '</div></div>')
    all_links = nav + links + ((d.get('foot') or {}).get('links') or [])
    contact_lab = next((x['t'] for x in all_links if re.search(r'contact|kontakt', (x.get('h') or '').lower())), None)
    social = place.get('social') or []
    routes = contact.get('routes') or []
    c_lines = ''
    if email:
        c_lines += f'<li><a href="mailto:{e(email)}">{e(email)}</a></li>'
    if phone.get('t'):
        c_lines += f'<li><a href="{e(phone.get("h") or "#")}">{e(phone["t"])}</a></li>'
    for r_ in routes:
        if r_.get('t'):
            c_lines += f'<li>{_a(r_.get("h"), e(r_["t"]))}</li>'
    soc = ''.join(f'<a href="{e(s.get("h") or "#")}">{e(s.get("t"))}</a>' for s in social if s.get('t'))
    contact_col = ''
    if c_lines or soc:
        contact_col = (f'<div class="ft-col">{opt("ft-h", contact_lab) or NOHEAD}'
                       f'<ul>{c_lines}</ul>{wrap("p", "ft-soc", soc)}</div>')
    addr = place.get('address') or {}
    hours = place.get('hours') or []
    door = ''
    if addr or hours:
        thumb = None
        for p in photos:                               # the reference's small picture of the shop: 235 px wide, so a small one serves
            if p['src'] not in used and p.get('role') in ('exterior', 'room', 'bar', 'workshop') and p['w'] >= 235 and .7 <= p['w'] / p['h'] <= 1.6:
                if thumb is None or (p.get('role') == 'exterior') > (thumb.get('role') == 'exterior'):
                    thumb = p
        if thumb:
            used.add(thumb['src'])
        a_lines = ''.join(f'<span>{e(x)}</span>' for x in [addr.get('street'), ' '.join(y for y in [addr.get('city'), addr.get('postcode')] if y), addr.get('region'), addr.get('country')] if x)
        h_lines = ''.join(f'<span>{e(h_.get("days"))}{" " + e(h_.get("open")) + "–" + e(h_.get("close")) if h_.get("open") else ""}</span>' for h_ in hours if h_.get('days'))
        door = (f'<div class="ft-col ft-door">{opt("ft-h", addr.get("city")) or NOHEAD}'
                f'{wrap("span", "ft-im", _img(thumb) if thumb else "")}'
                f'{wrap("p", "ft-a", a_lines)}{wrap("p", "ft-a", h_lines)}</div>')
    foot = d.get('foot') or {}
    f_links = [l for l in (foot.get('links') or []) if l.get('t')]
    legal_li = ''.join('<li><a href="%s">%s</a></li>' % (e(l.get('h') or '#'), e(l['t'])) for l in f_links)
    legal_col = f'<div class="ft-col ft-legal"><ul>{legal_li}</ul></div>' if f_links else ''
    f_text = f'<p class="ft-t">{e(foot.get("text"))}</p>' if foot.get('text') and not (addr or email or phone.get('t')) else ''
    notices = ''.join(f'<figure class="ft-n">{_img(dict(src=n_["img"], w=n_.get("w"), h=n_.get("h"), alt=" ".join(n_.get("text") or [])))}</figure>'
                      for n_ in (place.get('notices') or []) if n_.get('img'))
    footer = f'''<footer class="ft"><div class="ft-main">{reach}
<div class="ft-row">{sitemap}<div class="ft-pair">{contact_col}{door}</div></div>
{f'<div class="ft-row ft-row3">{legal_col}{f_text}{notices}</div>' if legal_col or f_text or notices else ''}
</div>{f'<div class="ft-end"><span>{e(foot.get("legal"))}</span></div>' if foot.get('legal') else ''}</footer>'''

    css = CSS % dict(g=ground, ink=ink, acc=accent, acc_ink=acc_ink, dark=dark, tile=tile, tile2=tile2, muted=muted,
                     fmuted=foot_muted, ldark=line_dark)
    title = name + (' — ' + hero['title'] if hero.get('title') and _norm(hero['title']) != _norm(name) else '')
    return f'''<!doctype html>
<html lang="{e(d.get('lang') or 'en')}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>{f'<meta name="description" content="{e(hero.get("text"))}">' if hero.get('text') else ''}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>{css}</style></head>
<body>
{header}
<main>{"".join(main)}</main>
{footer}
<script>{JS}</script>
</body></html>'''


CSS = '''
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%%}
body{margin:0;background:%(g)s;color:%(ink)s;font:400 20px/1.3 Inter,Helvetica,Arial,sans-serif;letter-spacing:-.03em;-webkit-font-smoothing:antialiased}
img{display:block;max-width:100%%;height:auto}
a{color:inherit;text-decoration:none}
ul{list-style:none;margin:0;padding:0}
h1,h2,h3,p{margin:0}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
.pan:focus-visible,.band:focus-visible,.card:focus-visible{outline:3px solid %(ink)s;outline-offset:-6px;box-shadow:inset 0 0 0 3px #fff}
.dsp,.btn,.hd-nav,.more-w,.logo,.sec-t,.card-t,.card-p,.row-t,.row-p,.ft-h,.reach-b,.hd-s,.sec-n,.plan-p{font-family:"Inter Tight",Inter,Helvetica,Arial,sans-serif;font-weight:600;text-transform:uppercase}

/* buttons: 55 high, 40 either side, 30 radius, 16px capitals; .15s linear on colour */
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:55px;padding:6px 40px;border-radius:30px;font-size:16px;line-height:1;letter-spacing:.01em;text-align:center;transition:background-color .15s linear,color .15s linear;cursor:pointer}
.btn-w{background:#fff;color:#000}
a:hover>.pan-c .btn-w,a:hover .band-c .btn-w,a.btn-w:hover{background:#f4f4f4;color:#2d2d2d}
.btn-g{background:%(tile)s;color:%(ink)s}
a.btn-g:hover{background:%(tile2)s}
.btn-k{background:%(ink)s;color:%(g)s}
a.btn-k:hover{opacity:.86}
.btn-s{min-height:40px;padding:4px 20px;font-size:12px}

/* header: sticky; bar 44; row 70 with a 1px rule under it; nav left, name centre, call right */
.hd{position:sticky;top:0;z-index:50;background:%(g)s}
.bar{position:relative;background:%(acc)s;color:%(acc_ink)s;padding:12px 50px;text-align:center;font-size:14px;line-height:1.4;letter-spacing:-.01em}
.bar-x{display:none;position:absolute;right:22px;top:50%%;width:32px;height:32px;margin-top:-16px;border:0;background:none;color:inherit;cursor:pointer}
.js .bar-x{display:block}
.bar-x::before,.bar-x::after{content:"";position:absolute;left:7px;right:7px;top:50%%;border-top:1px solid currentColor;transform:rotate(45deg)}
.bar-x::after{transform:rotate(-45deg)}
.hd-in{position:relative;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;height:70px;border-bottom:1px solid %(ink)s;background:%(g)s}
.hd-l{display:flex;align-items:center;gap:15px;padding:0 30px;min-width:0;height:100%%}
.hd-nav{display:flex;flex-wrap:wrap;gap:0 15px;height:16px;overflow:hidden;min-width:0;font-size:16px;line-height:1;letter-spacing:.01em}
.hd-nav li{white-space:nowrap}
.hd-nav li.over{display:none}
.hd-nav a,.hd-s,.more summary{transition:opacity .25s linear}
.hd-nav a:hover,.hd-s:hover,.more summary:hover{opacity:.6}
.logo{font-size:var(--ld);line-height:1;letter-spacing:-.04em;white-space:nowrap;transition:opacity .25s linear;padding:0 10px}
.logo:hover{opacity:.7}
.hd-r{display:flex;justify-content:flex-end;align-items:center;gap:20px;padding:0 30px}
.hd-s{font-size:16px;line-height:1;letter-spacing:.01em;white-space:nowrap}
.more summary{list-style:none;cursor:pointer;font-size:16px;line-height:1;letter-spacing:.01em;white-space:nowrap}
.more summary::-webkit-details-marker{display:none}
.more-b{display:none}
.menu{position:absolute;left:0;right:0;top:100%%;background:%(g)s;border-bottom:1px solid %(ink)s;overflow:hidden;animation:mfade .15s linear}
.menu-in{display:grid;grid-template-columns:360px 1fr;gap:30px;padding:10px 30px 30px;animation:mdrop .5s cubic-bezier(.165,.84,.44,1)}
.menu-big{font:500 40px/1.2 Inter,Helvetica,Arial,sans-serif;letter-spacing:-.03em;grid-column:1/-1}
.menu-big a,.menu-small a{transition:color .25s linear}
.menu-big:hover a{color:%(muted)s}
.menu-big a:hover{color:%(ink)s}
.menu-small{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:8px 24px;font:500 17px/1 Inter,Helvetica,Arial,sans-serif;color:%(muted)s;padding-top:14px}
.menu-small a:hover{color:%(ink)s}
.menu-f{display:none}
@keyframes mfade{from{opacity:0}}
@keyframes mdrop{from{transform:translateY(-20px)}}
@keyframes mslide{from{transform:translateX(100%%)}}

/* picture panels: two halves, each the height of the screen under the header; words at the foot, 40 in */
.duo-w{display:grid;grid-template-columns:1fr 1fr}
.duo{position:relative;background:%(dark)s}
.pan{position:relative;display:flex;flex-direction:column;justify-content:flex-end;height:calc(100vh - 114px);min-height:560px;max-height:980px;color:#fff;overflow:hidden;background:%(dark)s}
.pan-m,.band-m{position:absolute;inset:0}
.pan-m img,.band-m img{width:100%%;height:100%%;object-fit:cover}
.pan-c{position:relative;display:flex;flex-direction:column;align-items:flex-start;gap:10px;padding:150px 40px 40px;background:linear-gradient(to top,rgba(0,0,0,.74) 0,rgba(0,0,0,.66) calc(100%% - 150px),rgba(0,0,0,0) 100%%)}
.pan-plain{height:auto;min-height:420px}
.pan-plain .pan-c{background:none;padding-top:40px}
.duo-w>.pan+.pan.pan-plain,.duo-w>.pan-plain:first-child{border-left:0}
.duo-w>.pan-plain+.pan-plain{border-left:1px solid %(ldark)s}
.pan-t{font:500 40px/1.2 Inter,Helvetica,Arial,sans-serif;letter-spacing:-.03em;max-width:16em;text-wrap:balance}
.pan-x{font-weight:500;font-size:20px;line-height:1.3;max-width:31em;text-wrap:pretty}
.pan .btn{margin-top:20px}
.dots{display:none}
.duo-1 .pan{height:calc(100vh - 114px)}

/* product rows: header 60/30, heading 80/72 capitals; cards 440 with 30 between; 80 under */
.sec{padding-bottom:80px}
.sec-h{display:flex;justify-content:space-between;align-items:center;gap:40px 20px;padding:60px 30px}
.sec-t{font-size:80px;line-height:.9;letter-spacing:-.03em;text-wrap:balance;overflow-wrap:anywhere}
.sec-n{font-size:16px;letter-spacing:.01em}
.sec-x{padding:0 30px 40px;max-width:46em;color:%(muted)s}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:60px 30px;padding:0 30px}
.cards-run{display:flex;gap:30px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-padding:0 30px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.cards-run::-webkit-scrollbar{display:none}
.cards-run>.card-li{flex:0 0 calc((100%% - 90px)/3.3);scroll-snap-align:start}
.card-li{display:flex;min-width:0}
.card{display:flex;flex-direction:column;gap:30px;width:100%%}
.card-im{display:block;aspect-ratio:1;overflow:hidden;background:%(tile)s}
.card-im img{width:100%%;height:100%%;object-fit:cover;transition:transform .75s cubic-bezier(.165,.84,.44,1)}
a.card:hover .card-im img{transform:scale(1.05)}
.card-d{display:flex;flex-direction:column;flex:1;min-height:136px}
.card-t{font-size:30px;line-height:.9;letter-spacing:-.02em;overflow-wrap:anywhere}
.card-x{padding-top:10px;color:%(muted)s;font-size:20px;line-height:1.3}
.card-p{display:flex;justify-content:space-between;align-items:baseline;gap:6px 20px;flex-wrap:wrap;margin-top:auto;padding-top:30px;font-size:16px;line-height:1;letter-spacing:.01em}
.state{color:%(muted)s}
.cards+.rows{margin-top:60px}
.sec>.rows:first-child,.sec>.faq:first-child,.sec>.plans:first-child{margin-top:60px}

/* rows in type: the card's heading and price on one line, a 1px rule between */
.rows{margin:0 30px;border-bottom:1px solid %(ink)s}
.rows-2{columns:2;column-gap:30px;border-bottom:0}
.rows-2 li{break-inside:avoid;border-bottom:1px solid %(ink)s;margin-bottom:-1px}
.row{display:flex;justify-content:space-between;align-items:baseline;gap:10px 30px;padding:24px 0 22px;border-top:1px solid %(ink)s}
.row-l{display:flex;flex-direction:column;gap:8px;min-width:0}
.row-t{font-size:30px;line-height:.9;letter-spacing:-.02em;overflow-wrap:anywhere;transition:opacity .25s linear}
a.row:hover .row-t{opacity:.6}
.row-x{color:%(muted)s;font-size:20px;line-height:1.3;max-width:40em}
.row-p{display:flex;gap:6px 20px;flex-wrap:wrap;justify-content:flex-end;font-size:16px;line-height:1;letter-spacing:.01em;text-align:right;flex:none;max-width:50%%}
.plans{display:grid;grid-template-columns:repeat(3,1fr);gap:60px 30px;padding:0 30px}
.plan{display:flex;flex-direction:column;align-items:flex-start;border-top:1px solid %(ink)s;padding-top:30px}
.plan-p{font-size:80px;line-height:.9;letter-spacing:-.03em;padding:40px 0 30px;overflow-wrap:anywhere}
.plan-p small{font-size:16px;letter-spacing:.01em;margin-left:10px}
.plan-r{color:%(muted)s;padding-bottom:30px}
.plan .btn{margin-top:auto}
.faq{margin:0 30px;border-bottom:1px solid %(ink)s}
.faq details{border-top:1px solid %(ink)s}
.faq summary{display:flex;justify-content:space-between;gap:30px;align-items:baseline;padding:24px 0;cursor:pointer;list-style:none;font:500 24px/1.25 Inter,Helvetica,Arial,sans-serif}
.faq summary::-webkit-details-marker{display:none}
.faq summary i{position:relative;flex:none;width:16px;height:16px}
.faq summary i::before,.faq summary i::after{content:"";position:absolute;left:0;right:0;top:50%%;border-top:2px solid currentColor;transition:transform .15s linear}
.faq summary i::after{transform:rotate(90deg)}
.faq details[open] summary i::after{transform:rotate(0)}
.faq p{color:%(muted)s;max-width:40em;padding:0 0 30px}

/* full-width band: the screen under the header, words centred at the foot, 80 up */
.band{position:relative;display:flex;height:calc(100vh - 114px);min-height:560px;max-height:980px;color:#fff;background:%(dark)s;overflow:hidden}
.band-o{position:absolute;left:0;right:0;bottom:0;display:flex;flex-direction:column;align-items:center;padding:170px 30px 80px;background:linear-gradient(to top,rgba(0,0,0,.74) 0,rgba(0,0,0,.66) calc(100%% - 170px),rgba(0,0,0,0) 100%%)}
.band-c{display:flex;flex-direction:column;align-items:center;gap:40px;text-align:center}
.band-t{font:500 40px/1.2 Inter,Helvetica,Arial,sans-serif;letter-spacing:-.03em;max-width:20em;text-wrap:balance}
.band-x{font-weight:500;font-size:24px;line-height:1.25;max-width:30em;text-wrap:pretty;margin-top:-10px}
.band-plain{height:auto;min-height:0;border-top:1px solid %(ldark)s}
.band-plain .band-o{position:relative;background:none;padding:120px 30px;width:100%%}
.sec-b{padding-bottom:80px}
.sec-b .band+.rows{margin-top:60px}

/* foot: the ink as ground; one very large line; columns in 19px at 60%% */
.ft{background:%(dark)s;color:#fff;overflow:hidden}
.ft-main{padding:30px}
.reach{padding-bottom:0}
.reach-r{display:flex;justify-content:space-between;align-items:flex-end;gap:30px;padding:170px 0 26px;border-bottom:2px solid %(ldark)s}
.reach-b{font-size:min(90px,calc((100vw - 60px)/(var(--n)*.6)));line-height:.9;letter-spacing:-.04em;white-space:nowrap;transition:opacity .2s linear}
.reach-b:hover{opacity:.7}
.reach-x{padding-top:30px;font-size:20px;line-height:1.3}
.ft-row{display:grid;grid-template-columns:1fr 1fr;gap:30px;padding-top:105px}
.ft-pair{display:grid;grid-template-columns:1fr 1fr;gap:30px}
.ft-h{font-size:16px;line-height:.9;padding-bottom:30px}
.ft-2{display:grid;grid-template-columns:1fr 1fr;gap:30px}
.ft-col li,.ft-a,.ft-soc,.ft-t{font-size:19px;line-height:1.4;letter-spacing:-.02em;color:%(fmuted)s}
.ft-col a,.ft-end a{transition:color .2s linear}
.ft-col a:hover{color:#fff}
.ft-soc{padding-top:26px}
.ft-soc a+a{margin-left:12px;padding-left:12px;border-left:1px solid %(fmuted)s}
.ft-im{display:block;width:235px;max-width:100%%;aspect-ratio:235/223;overflow:hidden;margin-bottom:30px}
.ft-im img{width:100%%;height:100%%;object-fit:cover}
.ft-a span{display:block}
.ft-a+.ft-a{padding-top:14px}
.ft-row3{padding-top:105px;align-items:end}
.ft-legal ul{display:flex;flex-wrap:wrap;gap:4px 24px}
.ft-t{max-width:34em}
.ft-n img{max-width:min(100%%,420px)}
.ft-end{display:flex;justify-content:space-between;gap:10px;padding:10px 30px;border-top:1px solid %(ldark)s;font-size:14px;line-height:1.4;letter-spacing:-.01em;color:%(fmuted)s}

/* phone build (reference at 390): header 60, burger; the opening pair is a carousel; pairs stack at 500; rows slide */
@media (max-width:900px){
body{font-size:16px;line-height:1.25}
.bar{font-size:13px;padding:12px 50px}
.bar-x{right:12px}
.hd-in{display:flex;justify-content:space-between;height:60px;padding:0 20px}
.hd-l{order:2;padding:0;gap:0}
.hd-nav,.hd-r,.more-w{display:none}
.logo{font-size:var(--lm);padding:0;letter-spacing:-.03em}
.more summary{display:flex;align-items:center;justify-content:flex-end;width:44px;height:44px}
.more-b{display:block;position:relative;width:30px;height:9px;border-top:2px solid currentColor;border-bottom:2px solid currentColor;transition:height .2s linear}
.more[open] .more-b{height:0;border-bottom:0}
.menu{height:calc(100dvh - var(--hb,120px));border-bottom:0;overflow-y:auto;animation:mslide .75s cubic-bezier(.165,.84,.44,1)}
.menu-in{display:flex;flex-direction:column;min-height:100%%;gap:0;padding:30px 20px 20px;animation:none}
.menu-big{font-size:26px;display:flex;flex-direction:column;gap:20px}
.menu-small{flex-direction:column;gap:16px;padding-top:36px;font-size:17px}
.menu-f{display:flex;flex-direction:column;gap:18px;align-items:stretch;margin-top:auto;padding-top:40px;text-align:center}
.menu-f .btn{min-height:50px;font-size:14px}
.menu-s{font:600 14px/1 "Inter Tight",Inter,sans-serif;text-transform:uppercase;letter-spacing:.01em;padding:8px}
html:has(.more[open]){overflow:hidden}
.btn{min-height:42px;padding:5px 20px;font-size:14px}
.pan{height:500px;min-height:0}
.pan-c{padding:120px 30px 40px;background:linear-gradient(to top,rgba(0,0,0,.74) 0,rgba(0,0,0,.66) calc(100%% - 120px),rgba(0,0,0,0) 100%%)}
.pan-t{font-size:26px}
.pan-x{font-size:16px}
.pan-plain{height:auto;min-height:300px}
.duo-w{grid-template-columns:1fr}
.duo-w>.pan-plain+.pan-plain{border-left:0;border-top:1px solid %(ldark)s}
.hero .duo-w{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}
.hero .duo-w::-webkit-scrollbar{display:none}
.hero .pan{flex:0 0 100%%;scroll-snap-align:start;height:calc(100svh - 120px);min-height:480px}
.hero .pan-plain{height:auto;min-height:300px}
.hero .pan-c{padding-bottom:40px}
.js .hero .dots{display:flex;gap:7px;position:absolute;right:0;bottom:0;padding:40px 30px;pointer-events:none}
.dots i{width:10px;height:10px;border-radius:50%%;background:#fff;opacity:.6;transition:opacity .3s linear}
.dots i.on{opacity:1}
.duo-1 .pan{height:calc(100svh - 120px)}
.sec-h{flex-direction:column;align-items:flex-start;padding:40px 20px}
.sec-t{font-size:40px;letter-spacing:-.02em}
.sec-x{padding:0 20px 30px}
.cards{display:flex;gap:20px;padding:0 20px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-padding:0 20px;scrollbar-width:none}
.cards::-webkit-scrollbar{display:none}
.cards>.card-li,.cards-run>.card-li{flex:0 0 276px;scroll-snap-align:start}
.card{gap:20px}
.card-d{min-height:100px}
.card-t{font-size:22px}
.card-x{font-size:16px}
.card-p{font-size:14px;padding-top:24px}
.cards+.rows,.sec-b .band+.rows{margin-top:40px}
.rows,.faq{margin:0 20px}
.rows-2{columns:1}
.row{padding:18px 0 16px;gap:8px 20px}
.row-t{font-size:22px}
.row-x{font-size:16px}
.row-p{font-size:14px;flex-direction:column;align-items:flex-end;gap:8px;flex-wrap:nowrap}
.plans{grid-template-columns:1fr;padding:0 20px;gap:40px}
.plan-p{font-size:50px;padding:30px 0 20px}
.faq summary{font-size:18px;padding:18px 0}
.band{height:calc(100svh - 120px);min-height:480px}
.band-o{padding:140px 20px 80px;background:linear-gradient(to top,rgba(0,0,0,.74) 0,rgba(0,0,0,.66) calc(100%% - 140px),rgba(0,0,0,0) 100%%)}
.band-c{gap:16px}
.band-t{font-size:26px}
.band-x{font-size:18px;margin-top:0}
.band .btn{margin-top:10px}
.band-plain{height:auto;min-height:0}
.band-plain .band-o{padding:80px 20px}
.ft-main{padding:40px 20px 30px}
.reach-r{flex-direction:column;align-items:flex-start;gap:20px;padding:100px 0 20px}
.reach-b{font-size:min(50px,calc((100vw - 40px)/(var(--n)*.6)))}
.reach-x{font-size:16px;padding-top:20px}
.ft-row,.ft-pair{grid-template-columns:1fr;gap:0}
.ft-row{padding-top:40px}
.ft-col{padding-top:50px}
.ft-h{font-size:15px;padding-bottom:20px}
.ft-2{gap:20px}
.ft-col li,.ft-a,.ft-soc,.ft-t{font-size:14px;line-height:1.25}
.ft-col li a,.ft-soc a{display:inline-block;padding:5px 0}
.ft-soc{padding-top:14px}
.ft-end{padding:10px 20px;font-size:13px;flex-direction:column}
}
@media (prefers-reduced-motion:reduce){
*,*::before,*::after{transition:none!important;animation:none!important;scroll-behavior:auto!important}
a.card:hover .card-im img{transform:none}
}
'''

JS = r'''(function(){var D=document,H=D.documentElement;H.classList.add('js');
var bar=D.getElementById('bar');if(bar){var x=bar.querySelector('.bar-x');x&&x.addEventListener('click',function(){bar.hidden=true;bar.style.display='none'})}
var more=D.querySelector('.more');if(more){more.addEventListener('toggle',function(){H.style.setProperty('--hb',Math.round(D.querySelector('.hd').getBoundingClientRect().bottom)+'px')});D.addEventListener('keydown',function(e){if(e.key==='Escape'&&more.open){more.open=false;more.querySelector('summary').focus()}});
D.addEventListener('click',function(e){if(more.open&&!more.contains(e.target))more.open=false});
more.querySelectorAll('.menu a').forEach(function(a){a.addEventListener('click',function(){more.open=false})})}
/* the opening pair on a phone: a carousel that moves on by itself every 4.5s, as measured; it stops for good at the first touch, key or focus, and never starts when motion is to be reduced */
var w=D.querySelector('.hero .duo-w'),dots=D.querySelectorAll('.hero .dots i');
if(w&&dots.length){var mq=matchMedia('(max-width:900px)'),rm=matchMedia('(prefers-reduced-motion:reduce)'),t=null,
mark=function(){var i=Math.round(w.scrollLeft/Math.max(1,w.clientWidth));dots.forEach(function(d,k){d.classList.toggle('on',k===i)})},
stop=function(){if(t){clearInterval(t);t=null}},
go=function(){stop();if(!mq.matches||rm.matches||w.scrollWidth<=w.clientWidth+4)return;t=setInterval(function(){if(D.hidden)return;var n=w.scrollLeft+w.clientWidth>=w.scrollWidth-4?0:w.scrollLeft+w.clientWidth;w.scrollTo({left:n,behavior:'smooth'})},4500)};
w.addEventListener('scroll',mark,{passive:true});['touchstart','pointerdown','keydown','focusin','wheel'].forEach(function(ev){w.addEventListener(ev,function(){stop();go=function(){}},{passive:true})});
mq.addEventListener&&mq.addEventListener('change',function(){go()});go()}
})();'''
