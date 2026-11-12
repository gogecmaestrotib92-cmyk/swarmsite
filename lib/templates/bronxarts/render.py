"""bronxarts/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type scale, spacing, motion, phone layout) was measured on the reference's home
page and, for the parts a home page does not carry (numbers, people, lists with values, contact), on its sub-pages, at
1440 and 390 on 2026-11-12 (see NOTES.md). Nothing of the reference's code, words, pictures, illustrations, icons, logos
or typefaces is here. The client's data fills it; a section whose data is missing is left out whole. No model call.
"""
import html
import re

FONTS = 'https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,600;9..40,700&display=swap'
MENU = {'en': 'Menu', 'de': 'Menü', 'es': 'Menú', 'fr': 'Menu', 'it': 'Menu', 'pt': 'Menu', 'nl': 'Menu', 'sr': 'Meni'}


# ───────────────────────── colour: the reference's relations (one dark block colour, one bright button colour, two
# light block colours, one deep block colour, white ground, black ink) applied to the client's palette
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
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _chroma(h):
    c = _rgb(h)
    return (max(c) - min(c)) / 255


def _on(bg, ink):
    """the ink for text on bg: the client's ink when it reads 7:1, else black or white, whichever reads better"""
    if _con(ink, bg) >= 7:
        return ink
    return '#000000' if _con('#000000', bg) >= _con('#ffffff', bg) else '#ffffff'


def _toward(c, pole, bg, need):
    """c moved toward pole until it reads `need` against bg"""
    out = c
    for i in range(1, 21):
        if _con(out, bg) >= need:
            break
        out = _mix(pole, c, i / 20)
    return out


def _roles(pal):
    g = pal.get('ground') or '#ffffff'
    ink = pal.get('ink') or '#000000'
    if _con(ink, g) < 7:
        ink = _on(g, ink)
    cands = []
    for c in [pal.get('accent')] + list(pal.get('extra') or []):
        if c and re.fullmatch(r'#?[0-9a-fA-F]{3}([0-9a-fA-F]{3})?', c.strip()):
            c = _hex(_rgb(c))
            if c not in cands and _con(c, g) > 1.12:
                cands.append(c)
    light_page = _lum(g) > .4
    # dark: the block that carries white type (the reference's navy)
    darks = [c for c in cands + [ink] if _con(c, '#ffffff') >= 9]
    if darks:
        dark = max(darks, key=_chroma)
    elif cands:
        dark = _toward(cands[0], '#000000', '#ffffff', 9)
    else:
        dark = '#111111'
    if not light_page:  # a dark page: the dark block must still part from the ground
        dark = _mix(dark, '#ffffff', .9) if _con(dark, g) < 1.25 else dark
    rest = [c for c in cands if c != dark]
    # bright: the button and block colour that carries dark type (the reference's lime)
    brights = [c for c in rest if _lum(c) >= .3 and _chroma(c) >= .3]
    bright = max(brights, key=_chroma) if brights else None
    rest = [c for c in rest if c != bright]
    # deep: a second block colour that carries white type (the reference's blue)
    deeps = [c for c in rest if _con(c, '#ffffff') >= 4.5 and _chroma(c) >= .2]
    deep = max(deeps, key=_chroma) if deeps else None
    if deep:
        # a mid-tone blue reads 4.6:1 with black and with white, so its rows fall under 4.5:1 as soon as anything
        # shades them (the stuck menu's shadow passing over): the block that carries white type is deepened in its own
        # hue until white reads 5.5:1, the same floor as the made-up deep below
        deep = _toward(deep, '#000000', '#ffffff', 5.5)
    rest = [c for c in rest if c != deep]
    lights = [c for c in rest if _lum(c) >= .45]
    if bright is None:
        base = deep or (cands[0] if cands else dark)
        bright = lights.pop(0) if lights else _mix(base, '#ffffff', .28)
    if deep is None:
        deep = _toward(_mix(dark, bright, .68), '#000000', '#ffffff', 5.5)
        if _con(deep, dark) < 1.25:
            deep = _toward(_mix(bright, dark, .45), '#000000', '#ffffff', 4.6)
    c2 = lights.pop(0) if lights else _mix(bright, '#ffffff', .42)
    c3 = lights.pop(0) if lights else _mix(bright, '#ffffff', .7)
    if _con(c3, bright) < 1.08:
        c3 = _mix(bright, '#ffffff', .22)
    link = deep if _con(deep, g) >= 4.5 else (dark if _con(dark, g) >= 4.5 else ink)
    r = {'g': g, 'i': ink, 'dark': dark, 'bright': bright, 'deep': deep, 'c2': c2, 'c3': c3, 'link': link}
    for k in ('dark', 'bright', 'deep', 'c2', 'c3'):
        r[k + 'i'] = _on(r[k], ink)
    return r


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def u(p):
    p = str(p or '')
    return p if re.match(r'^(https?:|data:|/|\.\./)', p) else '../../' + p


def href(h):
    return e(h or '#')


def arrow():
    return '<span class="ar" aria-hidden="true"><i></i></span>'


def btn(c, cls='b-bright', extra=''):
    if not c or not c.get('t'):
        return ''
    return f'<a class="btn {cls}{extra}" href="{href(c.get("h"))}"><span>{e(c["t"])}</span>{arrow()}</a>'


def words(s):
    return {w[:-1] if w.endswith('s') and len(w) > 4 else w for w in re.findall(r'[^\W\d_]{4,}', (s or '').casefold())}


def mw(s):
    """style hook: the length of the longest word, so a heading is set no larger than that word allows"""
    n = max([len(w) for w in re.split(r'[\s/–—-]+', str(s or ''))] + [1])
    return f' style="--mw:{n}"' if n >= 8 else ''


def paras(s):
    return ''.join(f'<p>{e(x.strip())}</p>' for x in re.split(r'\n\s*\n', s or '') if x.strip())


# ───────────────────────── photographs: chosen by size, proportion and role; each shown once
class Photos:
    def __init__(self, d):
        self.all = [p for p in ((d.get('media') or {}).get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
        self.by = {p['src']: p for p in self.all}
        self.used = set()
        self.held = set()  # pictures that belong to a named thing (a step, a room, a person, a list) stay with it

    def hold(self, src):
        if src:
            self.held.add(src)

    def take(self, p):
        if p:
            self.used.add(p['src'])
        return p

    def own(self, src, w, h):
        """a thing's own picture, if it fills w×h without being enlarged more than a tenth (a small one: not at all)"""
        p = self.by.get(src)
        if not p or p['src'] in self.used:
            return None
        k = max(w / p['w'], h / p['h'])
        return self.take(p) if k <= (1.0 if p.get('small') else 1.1) else None

    def free(self, w, h, match='', roles=None, small_first=False, slack=1.1):
        """an unused picture that fills w×h; the one whose description shares most words with `match`, else by role"""
        order = roles or ['people', 'room', 'exterior', 'action', 'work', 'workshop', 'landscape', 'bar', 'dish', 'product', 'detail', 'other']
        ok = []
        for i, p in enumerate(self.all):
            if p['src'] in self.used or p['src'] in self.held or p.get('role') == 'portrait':
                continue
            if max(w / p['w'], h / p['h']) > (1.0 if p.get('small') else slack):
                continue
            role = p.get('role') or 'other'
            score = len(words(match) & words(p.get('alt'))) if match else 0
            ok.append((-score, (0 if p.get('small') else 1) if small_first else 0,
                       order.index(role) if role in order else len(order), i, p))
        if not ok:
            return None
        return self.take(sorted(ok, key=lambda t: t[:4])[0][4])


def img(p, cls='', eager=False, sizes=''):
    if not p:
        return ''
    return (f'<img class="{cls}" src="{e(u(p["src"]))}" width="{int(p["w"])}" height="{int(p["h"])}" alt="{e(p.get("alt") or "")}"'
            f'{"" if eager else " loading=lazy"} decoding="async">')


# ───────────────────────── sections
def s_header(d, R, hero_dark):
    b = d.get('brand') or {}
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    cta = d.get('cta') or (d.get('hero') or {}).get('primary') or {}
    pl = d.get('place') or {}
    ct = d.get('contact') or {}
    hero = d.get('hero') or {}
    top = []
    if (hero.get('secondary') or {}).get('t'):
        top.append((hero['secondary']['t'], hero['secondary'].get('h')))
    ph = pl.get('phone') or ct.get('phone') or {}
    if ph.get('t'):
        top.append((ph['t'], ph.get('h') or 'tel:' + re.sub(r'[^\d+]', '', ph['t'])))
    mail = pl.get('email') or ct.get('email')
    if mail:
        top.append((mail, 'mailto:' + mail))
    if (d.get('signin') or {}).get('t'):
        top.append((d['signin']['t'], d['signin'].get('h')))
    name = b.get('name') or ''
    logo = f'<span class="lgw"><img class="lg" src="{e(u(b["logo"]))}" alt="{e(name)}"></span>' if b.get('logo') else ''
    brand = f'<a class="brand{" has-lg" if logo else ""}" href="{href(b.get("home"))}">{logo}<span class="bnm">{e(name)}</span></a>'
    tb = ''
    if top or cta.get('t'):
        tb = ('<div class="tb"><div class="w">' + ''.join(f'<a href="{href(h)}">{e(t)}</a>' for t, h in top)
              + (f'<a class="tcta" href="{href(cta.get("h"))}"><span>{e(cta["t"])}</span></a>' if cta.get('t') else '') + '</div></div>')
    pn = '<nav class="pn" aria-label="Primary">' + ''.join(f'<a href="{href(n.get("h"))}">{e(n["t"])}</a>' for n in nav) + '</nav>' if nav else ''
    mcta = f'<a class="mcta{" long" if len(cta["t"]) > 12 else ""}" href="{href(cta.get("h"))}"><span>{e(cta["t"])}</span></a>' if cta.get('t') else ''
    panel = ''
    if nav or top:
        word = MENU.get((d.get('lang') or 'en')[:2], 'Menu')
        panel = (f'<details class="mm"><summary aria-label="{e(word)}"><span class="bars" aria-hidden="true"><i></i><i></i><i></i></span></summary>'
                 '<div class="panel"><nav aria-label="' + e(word) + '">' + ''.join(f'<a href="{href(n.get("h"))}">{e(n["t"])}</a>' for n in nav) + '</nav>'
                 + ('<div class="sec">' + ''.join(f'<a href="{href(h)}">{e(t)}</a>' for t, h in top) + '</div>' if top else '')
                 + (btn(cta, 'b-bright') if cta.get('t') else '') + '</div></details>')
    return tb, f'<div class="mnw"><div class="mn{"" if hero_dark else " on-light"}" id="mn"><div class="w">{brand}{pn}<div class="mr">{mcta}{panel}</div></div></div></div>'


def s_hero(d, R, P):
    h = d.get('hero') or {}
    title = h.get('title') or (d.get('brand') or {}).get('name') or ''
    v = (d.get('media') or {}).get('video')
    back = ''
    if v and v.get('src'):
        back = (f'<video class="bk" autoplay muted loop playsinline preload="metadata"{" poster=" + chr(34) + e(u(v["poster"])) + chr(34) if v.get("poster") else ""}'
                f' aria-label="{e(v.get("alt") or "")}"><source src="{e(u(v["src"]))}"></video>')
    else:
        p = P.free(1440 * .97, 820 * .97, roles=['people', 'exterior', 'room', 'landscape', 'action', 'work', 'workshop', 'bar', 'other', 'dish', 'product', 'detail'], slack=1.2)
        back = img(p, 'bk', eager=True)
    body = f'<h1{mw(title)}>{e(title)}</h1>' + ''.join(f'<p>{e(x)}</p>' for x in [h.get('text')] if x) + btn(h.get('primary'), 'b-bright')
    return back, f'<section class="hero{"" if (h.get("primary") or {}).get("t") else " nob"}"><div class="w">{body}</div></section>'


def s_cards(d, R, P):
    links = [l for l in (d.get('links') or []) if l.get('t')][:3]
    if not links:
        return ''
    cols = [('bright', R['bright']), ('c2', R['c2']), ('c3', R['c3'])]
    pics = [P.free(480, 350, match=l['t'] + ' ' + (l.get('d') or ''), roles=['room', 'people', 'exterior', 'action', 'work', 'workshop', 'detail', 'other'], small_first=True, slack=1.0) for l in links]
    mode = 'full' if all(pics) else ''
    if not mode:
        for p in pics:
            if p:
                P.used.discard(p['src'])
        pics = [P.free(403, 320, match=l['t'] + ' ' + (l.get('d') or ''), roles=['room', 'people', 'exterior', 'action', 'work', 'workshop', 'detail', 'other'], small_first=True, slack=1.0) for l in links]
        mode = 'inset' if all(pics) else 'none'
        if mode == 'none':
            for p in pics:
                if p:
                    P.used.discard(p['src'])
            pics = [None] * len(links)
    out = []
    for i, l in enumerate(links):
        k, col = cols[i % 3]
        tcol = col if _con(col, R['dark']) >= 3 else R['darki']
        out.append(f'<a class="fc" href="{href(l.get("h"))}"><span class="fct" style="background:{col}">{img(pics[i])}</span>'
                   f'<span class="fcd"><span class="t" style="color:{tcol};--mw:{max(len(x) for x in l["t"].split())}">{e(l["t"])}</span>'
                   f'<span class="r">{"<span>" + e(l["d"]) + "</span>" if l.get("d") else ""}{arrow()}</span></span></a>')
    return f'<section class="fcs n{len(links)} {mode}">{"".join(out)}</section>'


def s_steps(d, R, P):
    items = [dict(s) for s in ((d.get('steps') or {}).get('items') or []) if s.get('title') or s.get('text')]
    for sp in ((d.get('place') or {}).get('spaces') or []):
        if sp.get('title') or sp.get('text'):
            items.append({'title': sp.get('title'), 'text': sp.get('text'), 'img': sp.get('img'), 'cta': sp.get('cta')})
    if not items:
        return ''
    grounds = [('c3', R['c3'], R['c3i']), ('bright', R['bright'], R['brighti']), ('c2', R['c2'], R['c2i'])]
    banners, cards = [], []
    for s in items:
        own = P.by.get(s.get('img')) if s.get('img') else None
        bh = max(500, min(739, int(own['h'] * (1.0 if own.get('small') else 1.1)))) if own else 739
        big = P.own(s.get('img'), 738, bh) if own else None
        if big:
            banners.append((s, big, bh))
        elif s.get('img') and P.by.get(s['img']):
            cards.append((s, P.own(s['img'], 291, 288)))
        else:
            p = P.free(738, 739, match=(s.get('title') or '') + ' ' + (s.get('text') or '')) if len(banners) < 2 else None
            if p:
                banners.append((s, p, 739))
            else:
                cards.append((s, p))
    out = []
    for i, (s, p, bh) in enumerate(banners):
        k, bg, ink = grounds[i % 3]
        out.append(f'<section class="bn {"l" if i % 2 == 0 else "r"}" style="--bg:{bg};--ink:{ink};--h:{bh}px"><div class="bp">{img(p)}</div>'
                   f'<div class="bc"><h2{mw(s.get("title"))}>{e(s.get("title") or "")}</h2>{paras(s.get("text"))}{btn(s.get("cta"), "b-ground")}</div></section>')
    if cards:
        n = len(cards)
        per = n if n <= 3 else (2 if n == 4 else 3)
        cs = []
        for i, (s, p) in enumerate(cards):
            k, bg, ink = grounds[(i + len(banners)) % 3]
            c = s.get('cta') or {}
            inner = (f'{img(p)}<h3{mw(s.get("title"))}>{e(s.get("title") or "")}</h3>{paras(s.get("text"))}'
                     + (f'<span class="r"><span>{e(c["t"])}</span>{arrow()}</span>' if c.get('t') else ''))
            tag = f'a href="{href(c.get("h"))}"' if c.get('h') else 'div'
            cs.append(f'<{tag} class="lc{"" if p else " nop"}{" has-r" if c.get("t") else ""}" style="background:{bg};color:{ink}">{inner}</{tag.split()[0]}>')
        out.append(f'<section class="lcs p{per}">{"".join(cs)}</section>')
    return ''.join(out)


def s_statement(d, R, P):
    st = d.get('statement') or {}
    if not (st.get('title') or st.get('text')):
        return ''
    p = P.free(1382, 520, match=(st.get('title') or '') + ' ' + (st.get('text') or ''), slack=1.0)
    pic = f'<div class="sm" style="--ar:{p["w"]}/{p["h"]}">{img(p)}</div>' if p else ''
    return (f'<section class="st{"" if p else " nop"}">{pic}<div class="w">'
            + (f'<h2{mw(st["title"])}>{e(st["title"])}</h2>' if st.get('title') else '<span></span>') + f'<div class="x">{paras(st.get("text"))}</div></div></section>')


def blocks():
    return '<div class="ptc" aria-hidden="true"><i></i><i></i></div>'


def s_pattern(d, R):
    h = d.get('hero') or {}
    if not h.get('text2'):
        return ''
    lines = [x for x in [h.get('text2'), h.get('note')] if x]
    return '<section class="pt"><div class="ptx">' + ''.join(f'<p>{e(x)}</p>' for x in lines) + '</div>' + blocks() + '</section>'


def s_quotes(d, R):
    out = []
    for q in (d.get('quotes') or [])[:2]:
        if not q.get('q'):
            continue
        by = ', '.join(x for x in [q.get('name'), q.get('role')] if x)
        out.append(f'<section class="pt qt"><div class="ptx"><blockquote><p>{e(q["q"])}</p>' + (f'<footer>{e(by)}</footer>' if by else '')
                   + '</blockquote></div>' + blocks() + '</section>')
    return ''.join(out)


def s_figures(d, R):
    fs = [f for f in (d.get('figures') or []) if f.get('v')]
    if not fs:
        return ''
    rows = ''.join(f'<div class="fi"><span class="l">{e(f.get("l") or "")}</span><span class="v">{e(f["v"])}</span></div>' for f in fs)
    return f'<section class="blk" style="--bg:{R["deep"]};--ink:{R["deepi"]}"><div class="in"><div class="fis">{rows}</div></div></section>'


def s_credentials(d, R):
    cr = [c for c in (d.get('credentials') or []) if c.get('t')]
    if not cr:
        cr = [{'t': t} for t in (d.get('trust') or []) if t]
    if not cr:
        return ''
    out = []
    for c in cr:
        t = e(c['t'])
        if c.get('h'):
            t = f'<a href="{href(c["h"])}">{t}</a>'
        out.append(f'<div class="cq"><h3{mw(c["t"])}>{t}</h3>' + (f'<p class="y">{e(c["year"])}</p>' if c.get('year') else '')
                   + (f'<p class="x">{e(c["text"])}</p>' if c.get('text') else '') + '</div>')
    return f'<section class="crs"><div class="w"><div class="cqs">{"".join(out)}</div></div></section>'


def _cat_names(d):
    return {(i.get('name') or '').casefold() for g in ((d.get('catalogue') or {}).get('groups') or []) for i in (g.get('items') or [])}


def s_features(d, R):
    f = d.get('features') or {}
    items = [i for i in (f.get('items') or []) if i.get('t')]
    if not items:
        return ''
    names = _cat_names(d)
    if names and all(i['t'].casefold() in names for i in items):
        return ''  # the same list stands in the catalogue, with its groups
    rows = ''.join(f'<div class="li"><h3{mw(i["t"])}>{e(i["t"])}</h3>{paras(i.get("d"))}</div>' for i in items)
    head = (f'<h2{mw(f["title"])}>{e(f["title"])}</h2>' if f.get('title') else '') + (f'<div class="lead">{paras(f["text"])}</div>' if f.get('text') else '')
    return f'<section class="ls"><div class="w">{head}<div class="lis">{rows}</div></div></section>'


FOLD = 12  # CONTRACT "A long list is folded": more items or people than this → groups that open in place


def _amount(price):
    """(currency, value) read from a client's price string, or None; '1.800 €' and '1,800 €' are both 1800"""
    m = re.search(r'([€$£])?\s*(\d{1,3}(?:[.,\s]\d{3})+|\d+)(?:[.,](\d{1,2}))?\s*([€$£]|EUR|CHF|GBP|USD)?', str(price or ''))
    if not m or not (m.group(1) or m.group(4)):
        return None
    whole = re.sub(r'[.,\s]', '', m.group(2))
    return (m.group(1) or m.group(4), float(whole + '.' + (m.group(3) or '0')))


def _range(items):
    """the lowest and highest price of a group, in the client's own words, when every priced item reads in one currency"""
    pr = [(it.get('price'), _amount(it.get('price'))) for it in items if it.get('price')]
    if len(pr) < len(items):  # a range only when every item states a price; else the group shows its count
        return ''
    if len(pr) < 2 or any(a is None for _, a in pr) or len({a[0] for _, a in pr}) != 1:
        return pr[0][0] if len(pr) == 1 else ''
    lo, hi = min(pr, key=lambda x: x[1][1]), max(pr, key=lambda x: x[1][1])
    return lo[0] if lo[1][1] == hi[1][1] else f'{lo[0]} – {hi[0]}'


def fold(name, first, value, body, opened=False):
    """one group as the reference's facts row (name left, value right, a rule under) that opens in place"""
    return (f'<details class="fg"{" open" if opened else ""}><summary><span class="fn"><span class="gn"{mw(name)}>{e(name)}</span>'
            + (f'<span class="gf">{e(first)}</span>' if first else '') + '</span>'
            + (f'<span class="gv">{e(value)}</span>' if value else '') + '<span class="pm" aria-hidden="true"><i></i><i></i></span></summary>'
            + f'<div class="fb">{body}</div></details>')


def cat_row(it):
    name = e(it.get('name') or '')
    if it.get('h'):
        name = f'<a href="{href(it["h"])}">{name}</a>'
    price = it.get('price') or ''
    sub = ''.join(f'<p class="n">{e(x)}</p>' for x in [it.get('note'), it.get('state')] if x)
    sub += ''.join(f'<p class="pr"><span>{e(p.get("label") or "")}</span><b>{e(p.get("price") or "")}</b></p>' for p in (it.get('prices') or []))
    sub += f'<p class="x">{e(it["text"])}</p>' if it.get('text') else ''
    sub += '<ul>' + ''.join(f'<li>{e(r)}</li>' for r in it['rows']) + '</ul>' if it.get('rows') else ''
    return f'<div class="ci"><div class="ch"><h4>{name}</h4>' + (f'<span class="v">{e(price)}</span>' if price else '') + f'</div>{sub}</div>'


def s_catalogue_folded(c, groups, R, P):
    """the schools page's facts block: one colour block, the catalogue's title, then one row per group — its name, its
    first items, its price range (or count) at the right — each opening in place to its full rows"""
    head = (f'<h2{mw(c.get("title"))}>{e(c["title"])}</h2>' if c.get('title') else '') + (f'<div class="lead">{paras(c["text"])}</div>' if c.get('text') else '')
    rows = []
    for g in groups:
        its = g.get('items') or []
        first = ' · '.join(it.get('name') or '' for it in its[:3] if it.get('name')) + (' …' if len(its) > 3 else '')
        value = _range(its) or (str(len(its)) if its else '')
        body = (f'<div class="lead">{paras(g.get("text"))}</div>' if g.get('text') else '') + f'<div class="cis">{"".join(cat_row(it) for it in its)}</div>'
        if g.get('h'):
            body += f'<p class="gl"><a href="{href(g["h"])}"><span>{e(g.get("t") or "")}</span>{arrow()}</a></p>'
        gp = P.own(g.get('img'), 1184, 400) if g.get('img') else None
        if gp:
            body = f'<div class="band in-f" style="--ar:{gp["w"]}/{gp["h"]}">{img(gp)}</div>' + body
        rows.append(fold(g.get('t') or c.get('title') or '', first, value, body))
    out = f'<section class="blk cat fold" style="--bg:{R["deep"]};--ink:{R["deepi"]}"><div class="in">{head}<div class="fgs">{"".join(rows)}</div></div></section>'
    if c.get('note'):
        out += f'<section class="ls nt"><div class="w"><p>{e(c["note"])}</p></div></section>'
    return out


def s_catalogue(d, R, P):
    c = d.get('catalogue') or {}
    groups = [g for g in (c.get('groups') or []) if g.get('items') or g.get('t')]
    if not groups:
        return ''
    cyc = [(R['deep'], R['deepi']), (R['bright'], R['brighti']), (R['g'], R['i']), (R['c2'], R['c2i'])]
    if sum(len(g.get('items') or []) for g in groups) > FOLD:
        return s_catalogue_folded(c, groups, R, P)
    out, weight = [], 0
    for gi, g in enumerate(groups):
        bg, ink = cyc[gi % len(cyc)]
        rows = []
        for it in (g.get('items') or []):
            name = e(it.get('name') or '')
            if it.get('h'):
                name = f'<a href="{href(it["h"])}">{name}</a>'
            price = it.get('price') or ''
            sub = ''.join(f'<p class="n">{e(x)}</p>' for x in [it.get('note'), it.get('state')] if x)
            sub += ''.join(f'<p class="pr"><span>{e(p.get("label") or "")}</span><b>{e(p.get("price") or "")}</b></p>' for p in (it.get('prices') or []))
            sub += f'<p class="x">{e(it["text"])}</p>' if it.get('text') else ''
            sub += '<ul>' + ''.join(f'<li>{e(r)}</li>' for r in it['rows']) + '</ul>' if it.get('rows') else ''
            rows.append(cat_row(it))
            weight += 1 + len(it.get('text') or '') / 260
        head = (f'<p class="eb">{e(c["title"])}</p>' if c.get('title') and c.get('title') != g.get('t') else '')
        gt = e(g.get('t') or c.get('title') or '')
        if g.get('h') and gt:
            gt = f'<a href="{href(g["h"])}">{gt}</a>'
        head += f'<h2{mw(g.get("t") or c.get("title"))}>{gt}</h2>' if gt else ''
        txt = [x for x in [c.get('text') if gi == 0 else None, g.get('text')] if x]
        head += '<div class="lead">' + ''.join(f'<p>{e(x)}</p>' for x in txt) + '</div>' if txt else ''
        gp = P.own(g.get('img'), 1440, 420) if g.get('img') else None
        if gp:
            out.append(f'<div class="band" style="--ar:{gp["w"]}/{gp["h"]}">{img(gp)}</div>')
            weight = 0
        if len(rows) > 8:
            out.append(f'<section class="blk cat hd" style="--bg:{bg};--ink:{ink}"><div class="in">{head}</div></section>'
                       f'<section class="blk cat rw" style="--bg:{R["g"]};--ink:{R["i"]}"><div class="in"><div class="cis">{"".join(rows)}</div></div></section>')
        else:
            out.append(f'<section class="blk cat" style="--bg:{bg};--ink:{ink}"><div class="in">{head}<div class="cis">{"".join(rows)}</div></div></section>')
        if weight >= 16 and gi < len(groups) - 1:  # about two screens of rows: a picture band of the client's breaks the list
            bp = P.free(1440, 420, slack=1.0)
            if bp:
                out.append(f'<div class="band" style="--ar:{bp["w"]}/{bp["h"]}">{img(bp)}</div>')
                weight = 0
    if c.get('note'):
        out.append(f'<section class="ls nt"><div class="w"><p>{e(c["note"])}</p></div></section>')
    return ''.join(out)


def team_picture(d, P):
    """the reference's 'Our Teachers' banner: a team with no portraits of its own takes an unused people photograph that
    fills the half (738 wide, at least 500 high) for its title and text"""
    t = d.get('team') or {}
    ms = (t.get('items') or []) + [m for g in (t.get('groups') or []) for m in (g.get('items') or [])]
    if not ms or not (t.get('title') or t.get('text')) or any(m.get('img') for m in ms):
        return None
    for h in (739, 640, 560, 500):
        p = P.free(738, h, match='team teacher staff people ' + (t.get('title') or '') + ' ' + (t.get('text') or ''), roles=['people'], slack=1.1)
        if p and (p.get('role') == 'people'):
            return p, h
        if p:
            P.used.discard(p['src'])
    return None


def s_team(d, R, P, tp=None):
    t = d.get('team') or {}
    groups = [g for g in (t.get('groups') or []) if g.get('items')] or ([{'t': '', 'items': t.get('items')}] if t.get('items') else [])
    if not groups:
        return ''

    def person(m):
        p = P.by.get(m.get('img')) if m.get('img') else None
        pic = ''
        if p:
            P.used.add(p['src'])
            side = min(291, int(p['w']), int(p['h']))
            pic = f'<span class="po" style="width:{side}px">{img(p)}</span>'
        nm = e(m.get('name') or '')
        if m.get('h'):
            nm = f'<a href="{href(m["h"])}">{nm}</a>'
        more = ''.join(f'<p class="ro">{e(x)}</p>' for x in [m.get('role')] if x) + paras(m.get('text'))
        if m.get('phone'):
            more += f'<p><a href="tel:{e(re.sub(r"[^0-9+]", "", str(m["phone"])))}">{e(m["phone"])}</a></p>'
        if m.get('email'):
            more += f'<p><a href="mailto:{e(m["email"])}">{e(m["email"])}</a></p>'
        return f'<div class="li pe">{pic}<h3{mw(m.get("name"))}>{nm}</h3>{more}</div>'

    out = []
    folded = sum(len(g['items']) for g in groups) > FOLD
    for gi, g in enumerate(groups):
        head = ''
        if gi == 0 and tp:
            p, bh = tp
            out.append(f'<section class="bn r" style="--bg:{R["bright"]};--ink:{R["brighti"]};--h:{bh}px"><div class="bp">{img(p)}</div>'
                       f'<div class="bc"><h2{mw(t.get("title"))}>{e(t.get("title") or "")}</h2>{paras(t.get("text"))}</div></section>')
        elif gi == 0:
            head += (f'<h2{mw(t["title"])}>{e(t["title"])}</h2>' if t.get('title') else '') + (f'<div class="lead">{paras(t["text"])}</div>' if t.get('text') else '')
        if g.get('t'):
            head += f'<h2 class="g"{mw(g["t"])}>{e(g["t"])}</h2>'
        people = [m for m in g['items'] if m.get('name')]
        lis = f'<div class="lis">{"".join(person(m) for m in people)}</div>'
        if folded:
            first = ' · '.join(m['name'] for m in people[:3]) + (' …' if len(people) > 3 else '')
            if g.get('t'):
                head = head.replace(f'<h2 class="g"{mw(g["t"])}>{e(g["t"])}</h2>', '')
            lis = '<div class="fgs">' + fold(g.get('t') or t.get('title') or '', first, str(len(people)), lis) + '</div>'
        out.append(f'<section class="ls tm"><div class="w">{head}{lis}</div></section>')
    return ''.join(out)


def s_plans(d, R):
    pl = d.get('plans') or {}
    items = [p for p in (pl.get('items') or []) if p.get('name') or p.get('price')]
    if not items:
        return ''
    out = []
    if pl.get('title') or pl.get('text'):
        out.append('<section class="ls"><div class="w">' + (f'<h2>{e(pl["title"])}</h2>' if pl.get('title') else '')
                   + (f'<div class="lead">{paras(pl["text"])}</div>' if pl.get('text') else '') + '</div></section>')
    cyc = [(R['c2'], R['c2i']), (R['c3'], R['c3i'])]
    k = 0
    for p in items:
        if p.get('marked'):
            bg, ink = R['bright'], R['brighti']
        else:
            bg, ink = cyc[k % 2]
            k += 1
        rows = ''.join(f'<div class="si"><span>{e(r)}</span></div>' for r in (p.get('rows') or []))
        left = (f'<p class="eb">{e(p["line"])}</p>' if p.get('line') else '') + f'<h2{mw(p.get("name"))}>{e(p.get("name") or "")}</h2>'
        if p.get('price'):
            left += f'<p class="pp"><b>{e(p["price"])}</b>' + (f' <span>{e(p["per"])}</span>' if p.get('per') else '') + '</p>'
        left += btn(p.get('cta'), 'b-ground')
        out.append(f'<section class="blk plan" style="--bg:{bg};--ink:{ink}"><div class="in two"><div>{left}</div><div class="sis">{rows}</div></div></section>')
    if pl.get('note'):
        out.append(f'<section class="ls nt"><div class="w"><p>{e(pl["note"])}</p></div></section>')
    return ''.join(out)


def s_faq(d, R):
    f = d.get('faq') or {}
    items = [i for i in (f.get('items') or []) if i.get('q')]
    if not items:
        return ''
    rows = ''.join(f'<div class="li"><h3{mw(i["q"])}>{e(i["q"])}</h3>{paras(i.get("a"))}</div>' for i in items)
    return f'<section class="ls fq"><div class="w">' + (f'<h2>{e(f["title"])}</h2>' if f.get('title') else '') + f'<div class="lis one">{rows}</div></div></section>'


def s_more(d, R, P):
    links = [l for l in (d.get('links') or []) if l.get('t')][3:]
    if not links:
        return ''
    out = []
    for l in links:
        p = P.free(504, 257, match=l['t'] + ' ' + (l.get('d') or ''), slack=1.0) if l.get('d') else None
        out.append(f'<a class="xc{"" if p else " nop"}" href="{href(l.get("h"))}">{img(p)}<span class="xd"><span class="t"{mw(l["t"])}>{e(l["t"])}</span>'
                   + (f'<span class="x">{e(l["d"])}</span>' if l.get('d') else '') + f'{arrow()}</span></a>')
    return f'<section class="xcs{" odd" if len(out) % 2 else ""}">{"".join(out)}</section>'


def _fit(s, top=36):
    n = max(8, len(s))
    return f'font-size:min({top}px,calc((100vw - 64px) / {n * .56:.1f}))'


def _addr(a):
    if not a:
        return ''
    l2 = ' '.join(x for x in [a.get('postcode'), a.get('city')] if x)
    return ''.join(f'<p>{e(x)}</p>' for x in [a.get('street'), l2, ', '.join(x for x in [a.get('region'), a.get('country')] if x)] if x)


def _hours(hs):
    return ''.join(f'<div class="si"><span class="k">{e(h.get("days") or "")}</span><span class="v">{e(" – ".join(x for x in [h.get("open"), h.get("close")] if x))}</span></div>'
                   for h in (hs or []) if h.get('days') or h.get('open'))


def s_contact(d, R):
    pl, ct, cl, b = d.get('place') or {}, d.get('contact') or {}, d.get('close') or {}, d.get('brand') or {}
    ph = pl.get('phone') or ct.get('phone') or {}
    mail = pl.get('email') or ct.get('email')
    addr = _addr(pl.get('address'))
    hours = _hours(pl.get('hours'))
    locs = d.get('locations') or []
    routes = [r for r in (ct.get('routes') or []) if r.get('t')]
    if not (ph.get('t') or mail or addr or hours or locs or routes):
        return ''
    left = f'<h2{mw(b.get("name"))}>{e(b.get("name") or "")}</h2>' + (f'<div class="lead">{paras(cl["text"])}</div>' if cl.get('text') else '')
    if mail:
        left += f'<p class="big"><a href="mailto:{e(mail)}" style="{_fit(mail)}">{e(mail)}</a></p>'
    if ph.get('t'):
        left += f'<p class="big"><a href="{href(ph.get("h") or "tel:" + re.sub(r"[^0-9+]", "", ph["t"]))}" style="{_fit(ph["t"])}">{e(ph["t"])}</a></p>'
    if addr:
        left += f'<div class="ad"><p class="nm">{e(b.get("name") or "")}</p>{addr}</div>'
    for lo in locs:
        lp = lo.get('phone')
        lp = lp.get('t') if isinstance(lp, dict) else lp
        left += (f'<div class="ad"><p class="nm">{e(lo.get("name") or "")}</p>{_addr(lo.get("address"))}'
                 + (f'<p>{e(lp)}</p>' if lp else '') + (f'<p><a href="mailto:{e(lo["email"])}">{e(lo["email"])}</a></p>' if lo.get('email') else '')
                 + (f'<p>{e(lo["note"])}</p>' if lo.get('note') else '') + (f'<div class="sis sm2">{_hours(lo.get("hours"))}</div>' if lo.get('hours') else '') + '</div>')
    right = hours
    if ph.get('note'):
        right += f'<p class="hn">{e(ph["note"])}</p>'
    for r in routes:
        v = e(r.get('note') or r.get('t'))
        right += f'<div class="si rt"><span class="k">{e(r["t"])}</span><span class="v2">' + (f'<a href="{href(r["h"])}">{v}</a>' if r.get('h') else v) + '</span></div>'
    form = ct.get('form') or {}
    bk = pl.get('booking') or ({'t': form.get('t'), 'h': form.get('h')} if form.get('t') else None)
    right += btn(bk, 'b-bright')
    soc = [s for s in (pl.get('social') or []) if s.get('t')]
    if soc:
        right += '<p class="so">' + ''.join(f'<a href="{href(s.get("h"))}">{e(s["t"])}</a>' for s in soc) + '</p>'
    return f'<section class="ct"><div class="w"><div class="cl">{left}</div>' + (f'<div class="cr sis">{right}</div>' if right else '') + '</div></section>'


def s_close(d, R, P):
    cl = d.get('close') or {}
    if not cl.get('title'):
        return ''
    p = P.free(847, 540, roles=['people', 'exterior', 'room', 'action', 'landscape', 'work', 'workshop', 'detail', 'other'], slack=1.0)
    side = f'<div class="cp">{img(p)}</div>' if p else blocks()
    return (f'<section class="cz{" pic" if p else ""}"><div class="cb"><h2{mw(cl["title"])}>{e(cl["title"])}</h2>{btn(cl.get("cta"), "b-ground")}</div>{side}</section>')


def s_foot(d, R):
    b, f, pl = d.get('brand') or {}, d.get('foot') or {}, d.get('place') or {}
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    cta = d.get('cta') or {}
    logo = f'<span class="flw"><img class="fl" src="{e(u(b["logo"]))}" alt="{e(b.get("name") or "")}" loading="lazy"></span>' if b.get('logo') else f'<p class="fn">{e(b.get("name") or "")}</p>'
    half = (len(nav) + 1) // 2
    cols = ''.join('<div class="fcol">' + ''.join(f'<a href="{href(n.get("h"))}">{e(n["t"])}</a>' for n in part) + '</div>' for part in (nav[:half], nav[half:]) if part)
    soc = [s for s in (pl.get('social') or []) if s.get('t')]
    if soc:
        cols += '<div class="fcol">' + ''.join(f'<a href="{href(s.get("h"))}">{e(s["t"])}</a>' for s in soc) + '</div>'
    low = ''.join(f'<a href="{href(l.get("h"))}">{e(l["t"])}</a>' for l in (f.get('links') or []) if l.get('t'))
    small = ''.join(f'<p>{e(x)}</p>' for x in [f.get('text'), f.get('legal')] if x)
    notices = ''
    for n in (pl.get('notices') or []):
        notices += '<div class="no">' + (f'<img src="{e(u(n["img"]))}" width="{int(n.get("w") or 0) or ""}" height="{int(n.get("h") or 0) or ""}" alt="" loading="lazy" style="max-width:min(100%,{int(n.get("w") or 271)}px)">' if n.get('img') else '') + ''.join(f'<p>{e(x)}</p>' for x in (n.get('text') or [])) + '</div>'
    return (f'<footer class="ft"><div class="w"><div class="f1"><div class="fm">{logo}</div><div class="fcs2">{cols}</div>{btn(cta, "b-bright")}</div>'
            + (f'<div class="f2">{low}</div>' if low else '') + (f'<div class="f3">{small}</div>' if small else '') + notices + '</div></footer>')


CSS = r"""
*,*::before,*::after{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--i);font:400 18px/28px "DM Sans",system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased;overflow-wrap:break-word}
img,video{display:block;max-width:100%}h1,h2,h3,h4,p,blockquote,ul{margin:0}a{color:inherit;text-decoration:none}
:focus-visible{outline:3px solid currentColor;outline-offset:3px}
.w{max-width:1320px;margin:0 auto;padding:0 64px}
h1,h2,h3,h4,.t{overflow-wrap:break-word}
/* arrow: a 44×2 line with a 7px head; grows to twice its length in .3s ease */
.ar{position:relative;display:inline-block;flex:none;width:44px;height:2px;background:currentColor;transition:width .3s ease;vertical-align:middle}
.ar i{position:absolute;right:-1px;top:-2.5px;width:7px;height:7px;border:solid currentColor;border-width:0 2px 2px 0;border-radius:0 0 2px 0;transform:rotate(-45deg)}
a:hover>.ar,a:hover .r .ar,a:hover .xd .ar,a:focus-visible .ar{width:88px}
/* buttons: 180×70, square, bold 16; a half-transparent sheet rises from the foot in .09s ease-in */
.btn,.tcta,.mcta{position:relative;z-index:0;display:inline-flex;align-items:center;justify-content:center;overflow:hidden;font-weight:700;font-size:16px;line-height:28px;text-align:center}
.btn{min-width:180px;min-height:70px;padding:12px 37px;max-width:100%}.btn .ar{display:none}
.btn::before,.tcta::before,.mcta::before{content:"";position:absolute;z-index:-1;left:0;right:0;bottom:0;height:0;opacity:.5;background:var(--g);transition:height .09s ease-in}
.btn:hover::before,.tcta:hover::before,.mcta:hover::before,.btn:focus-visible::before{height:100%}
.b-bright,.tcta{background:var(--bright);color:var(--brighti)}.b-ground{background:var(--g);color:var(--i)}.b-ground::before{background:var(--bright)}
/* top line */
.tb{background:var(--g)}.tb .w{display:flex;justify-content:flex-end;align-items:center;gap:8px 32px;min-height:48px;padding-top:8px;padding-bottom:8px;flex-wrap:wrap;font-weight:600;font-size:14px;line-height:16px}
.tb a:not(.tcta):hover{color:var(--link)}.tcta{font-weight:600;font-size:14px;line-height:20px;padding:6px 12px;margin-left:16px}
/* first screen: navigation and opening share one backdrop */
.top{position:relative;z-index:5;isolation:isolate;background:var(--dark);color:#fff}
.top>.bk{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:-2}
.top.has-bk::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,rgba(0,0,0,.48) 0,rgba(0,0,0,.48) 131px,rgba(0,0,0,0) 250px),linear-gradient(90deg,rgba(0,0,0,.62) 0,rgba(0,0,0,.62) 46%,rgba(0,0,0,.4) 100%)}
.mnw{height:127px}.mn{height:131px;display:flex;align-items:center}.mn .w{display:flex;align-items:center;justify-content:space-between;gap:32px;width:100%}
.brand{display:flex;align-items:center;gap:14px;min-width:0}.lgw{display:none;align-items:center;width:219px;height:78px}.lg{max-width:100%;max-height:100%;object-fit:contain;object-position:left center}
.bnm{font-weight:700;font-size:18px;line-height:21px;max-width:230px;display:block}
.pn{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px 32px;font-weight:600;font-size:16px;line-height:19px}.pn a{padding:12px 0}.pn a:hover{color:var(--bright)}
.mr{display:none;align-items:center;gap:15px;flex:none}
.mn.stuck{position:fixed;top:0;left:0;right:0;z-index:999;background:var(--g);color:var(--i);box-shadow:0 0 5px 5px rgba(0,0,0,.2)}
.mn.stuck .pn a:hover{color:var(--link)}.mn.stuck .has-lg .lgw{display:flex}.mn.stuck .has-lg .bnm{display:none}
.mn.on-light{color:#fff}
.mcta{background:#fff;color:#000;padding:10px 24px;min-height:48px;max-width:46vw}.mcta span{white-space:nowrap}
.mn.stuck .mcta{background:var(--dark);color:var(--darki)}
.mm summary{list-style:none;cursor:pointer;width:68px;height:68px;display:flex;align-items:center;justify-content:center;border-radius:6px}.mm summary::-webkit-details-marker{display:none}
.bars{position:relative;width:32px;height:24px;display:block}.bars i{position:absolute;left:0;right:0;height:2px;background:currentColor;transition:transform .3s ease,opacity .15s linear}
.bars i:nth-child(1){top:1px}.bars i:nth-child(2){top:11px}.bars i:nth-child(3){top:21px}
.mm[open] .bars i:nth-child(1){transform:translateY(10px) rotate(45deg)}.mm[open] .bars i:nth-child(2){opacity:0}.mm[open] .bars i:nth-child(3){transform:translateY(-10px) rotate(-45deg)}
.panel{position:absolute;left:0;right:0;top:95px;z-index:998;background:var(--dark);color:var(--darki);padding:24px 40px 48px}
.js .panel{position:fixed;bottom:0;overflow:auto}
.panel nav a{display:block;font-weight:600;font-size:20px;line-height:32px;padding:16px 0}.panel .sec{border-top:1px solid currentColor;margin-top:24px;padding-top:24px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px 24px;font-size:18px;line-height:28px}.panel .sec a{overflow-wrap:anywhere}.panel .sec a[href^="tel:"]{white-space:nowrap;overflow-wrap:normal}
.mn.open{position:fixed;top:0;left:0;right:0;z-index:999;background:var(--dark);color:var(--darki);box-shadow:none}.mn.open .mcta{background:#fff;color:#000}.mn.open .lgw{display:none!important}.mn.open .bnm{display:block!important}
.hero .w{display:flex;flex-direction:column;align-items:flex-start;justify-content:flex-end;min-height:498px}
.hero.nob .w{padding-bottom:72px}
h1{font-weight:700;font-size:min(80px,calc(69vw / var(--mw,1) / .6));line-height:1.125;max-width:993px;margin-bottom:16px}
.hero p{font-weight:600;font-size:18px;line-height:27px;max-width:497px;margin-bottom:43px}
/* three colour cards */
.fcs{display:grid;grid-template-columns:repeat(3,1fr)}.fcs.n1{grid-template-columns:1fr}.fcs.n2{grid-template-columns:1fr 1fr}
.fc{display:flex;flex-direction:column;min-width:0}.fct{display:flex;align-items:flex-end;justify-content:center;height:350px;padding-top:30px}
.fct img{width:403px;max-width:calc(100% - 76px);height:320px;object-fit:cover}.full .fct{padding:0}.full .fct img{width:100%;max-width:none;height:100%}.none .fct{height:30px;padding:0}
.fcd{flex:1;display:block;background:var(--dark);color:var(--darki);padding:16px 32px 32px;min-height:175px}
.fcd .t{display:block;font-weight:700;font-size:37px;line-height:54px}.fcd .r,.lc .r{display:flex;align-items:center;gap:16px}.fcd .r>span:first-child{max-width:calc(100% - 110px)}
/* banners: a photograph from the window's edge, as tall as the block, beside the copy on a colour */
.bn{display:grid;grid-template-columns:1fr 1fr;min-height:var(--h,739px);background:var(--bg);color:var(--ink)}
.bp{position:relative;min-height:374px}.bp img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.bc{align-self:center;padding:64px 80px 64px 128px;max-width:702px}.bn.r .bp{order:2}.bn.r .bc{justify-self:end;width:100%}
.bn h2,.lc h3{font-weight:700;font-size:50px;line-height:1.16;margin-bottom:16px}.lc h3{font-size:min(50px,calc(26vw / var(--mw,1) / .6))}.p2 .lc h3{font-size:min(50px,calc(40vw / var(--mw,1) / .6))}.bn h2{font-size:min(50px,calc(34vw / var(--mw,1) / .6))}.bc p{margin-bottom:27px}.bc p+p{margin-top:-11px}
/* colour cards with a small picture above the words */
.lcs{display:grid;grid-template-columns:repeat(3,1fr);margin:48px}.lcs.p1{grid-template-columns:1fr}.lcs.p2{grid-template-columns:1fr 1fr}
.lc{position:relative;display:block;padding:24px 24px 48px;min-width:0}.lc.has-r{padding-bottom:96px}.lc img{width:291px;height:288px;object-fit:cover;margin:48px 48px 48px;max-width:calc(100% - 96px)}
.lc.nop{padding-top:72px}.lc p{margin-bottom:16px}.lc .r{position:absolute;left:24px;bottom:40px;font-weight:700;font-size:16px;line-height:28px}
/* statement on the dark block, under a wide picture */
.st{background:var(--dark);color:var(--darki);padding-bottom:64px}.st.nop{padding-top:96px}
.sm{padding:48px 29px}.sm img{width:100%;aspect-ratio:var(--ar);max-height:763px;object-fit:cover}
.st .w{display:grid;grid-template-columns:5fr 7fr;gap:32px 40px}.st h2{font-weight:600;font-size:50px;line-height:58px}.st .x p+p{margin-top:16px}
/* large sentences on the dark block, colour blocks at the edge */
.pt{display:flex;background:var(--dark);color:var(--darki)}.ptx{flex:1;display:flex;flex-direction:column;justify-content:center;min-height:672px;padding:48px 128px}
.ptx p{font-weight:600;font-size:42px;line-height:52px;max-width:848px}.ptx p+p{margin-top:32px}
.ptc{flex:none;width:336px;display:flex;flex-direction:column}.ptc i{flex:1;min-height:200px;background:var(--c2)}.ptc i+i{background:linear-gradient(135deg,var(--c3) 50%,var(--bright) 50%)}
.qt{background:var(--deep);color:var(--deepi)}.qt .ptx{min-height:336px}.qt footer{margin-top:24px;font-weight:700;font-size:16px;line-height:20px;text-transform:uppercase}
/* colour blocks with rows: a label on the left, the value large on the right, a rule under */
.blk{background:var(--bg);color:var(--ink);padding:128px}.blk .in{max-width:1184px;margin:0 auto}
.eb{font-weight:700;font-size:16px;line-height:20px;text-transform:uppercase;margin-bottom:16px}
.blk h2{font-weight:700;font-size:min(80px,calc(62vw / var(--mw,1) / .6));line-height:1.125;max-width:900px;margin-bottom:32px}.blk .lead{max-width:685px;margin-bottom:32px}.blk h2 a:hover,.ci h4 a:hover,.cq a:hover,.li a:hover{text-decoration:underline}
.fis,.cis{display:grid;grid-template-columns:1fr 1fr;column-gap:13%;align-items:start}.cat .cis{margin-top:64px}.cat.hd{padding-bottom:64px}.cat.hd h2,.cat.hd .lead{margin-bottom:0}.cat.hd .lead{margin-top:32px}.cat.rw{padding-top:32px;padding-bottom:48px}
.fi{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;border-bottom:1px solid currentColor;padding-bottom:32px;margin-bottom:80px}
.fi .l{font-weight:700;font-size:18px;line-height:28px;text-transform:uppercase;max-width:60%}.fi .v{font-weight:600;font-size:60px;line-height:60px;white-space:nowrap}
.fis .fi:last-child,.fis .fi:nth-last-child(2):nth-child(odd){margin-bottom:0}
.ci{border-bottom:1px solid currentColor;padding-bottom:24px;margin-bottom:48px;min-width:0}.ch{display:flex;justify-content:space-between;align-items:baseline;gap:8px 24px;flex-wrap:wrap}
.ci h4{font-weight:700;font-size:18px;line-height:28px;text-transform:uppercase;flex:1 1 50%;min-width:0}.ci .v{font-weight:600;font-size:36px;line-height:48px;white-space:nowrap;margin-left:auto}
.ci .n,.ci .x,.ci li,.ci .pr{font-weight:600;font-size:15px;line-height:28px}.ci .x{font-weight:400}.ci .pr{display:flex;justify-content:space-between;gap:16px}.ci ul{padding-left:18px}
.band img{width:100%;aspect-ratio:var(--ar);max-height:735px;object-fit:cover}
.two{display:grid;grid-template-columns:1fr 1fr;column-gap:96px;align-items:start}.pp{margin-bottom:32px}.pp b{font-weight:600;font-size:36px;line-height:48px}
.si{display:flex;justify-content:space-between;align-items:baseline;gap:8px 24px;flex-wrap:wrap;margin-bottom:48px}.plan .si{margin-bottom:0;padding:14px 0;border-bottom:1px solid currentColor}
.si .k{font-weight:700;font-size:16px;line-height:20px;text-transform:uppercase}.si .v{font-weight:600;font-size:36px;line-height:48px;margin-left:auto;text-align:right}.si .v2{margin-left:auto;text-align:right;font-weight:600}
/* folded groups: the schools page's facts row as the summary of a native <details> */
.fgs{margin-top:48px;border-top:1px solid currentColor}.fg{border-bottom:1px solid currentColor}
.fg summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:8px 32px;padding:28px 0}.fg summary::-webkit-details-marker{display:none}
.fn{flex:1;min-width:0;display:block}.gn{display:block;font-weight:600;font-size:36px;line-height:48px}.gf{display:block;font-weight:600;font-size:15px;line-height:28px;margin-top:4px}
.gv{font-weight:600;font-size:36px;line-height:48px;text-align:right;white-space:nowrap}
.pm{position:relative;flex:none;width:24px;height:24px}.pm i{position:absolute;left:0;right:0;top:11px;height:2px;background:currentColor;transition:transform .3s ease}.pm i+i{transform:rotate(90deg)}
.fg[open] .pm i+i{transform:rotate(0)}.fg summary:hover .gn{text-decoration:underline;text-underline-offset:6px;text-decoration-thickness:2px}
.fb{padding:8px 0 32px}.fb .cis{margin-top:32px}.fb>.lead{margin:0}.gl{margin-top:-16px;font-weight:700;font-size:16px}.gl a{display:inline-flex;align-items:center;gap:16px}
.band.in-f img{max-height:400px}.tm .fgs{margin-top:16px}.tm .fb .lis{margin-top:24px}
/* credentials: rules above, a heavy name, small capitals, a short text */
.crs{padding:96px 0 64px}.cqs{display:grid;grid-template-columns:1fr 1fr;column-gap:16px;padding:0 8px}
.cq{border-top:2px solid currentColor;padding:32px 0;min-width:0}.cq h3{font-weight:700;font-size:42px;line-height:52px;margin-bottom:16px}
.cq .y{font-weight:700;font-size:16px;line-height:20px;text-transform:uppercase;margin-bottom:8px}.cq .x{font-weight:600;font-size:15px;line-height:28px}
/* lists set as the reference sets its people: a heading, then names in two columns with a line under each */
.ls{padding-top:64px}.ls+.ls.tm{padding-top:0}.ls h2{font-weight:700;font-size:60px;line-height:72px;margin-bottom:32px;max-width:1000px}.ls .lead{max-width:685px;margin-bottom:48px}.ls .lead p+p{margin-top:16px}
.lis{display:grid;grid-template-columns:1fr 1fr;column-gap:24px;align-items:start}.lis.one{grid-template-columns:minmax(0,808px)}
.li{margin-bottom:48px;min-width:0}.li h3{font-weight:600;font-size:36px;line-height:48px;margin-bottom:8px}.li p{max-width:584px}.li p+p{margin-top:12px}.li p a{text-decoration:underline}
.pe h3{font-size:50px;line-height:58px;margin-bottom:0}.pe .ro{font-weight:600}.pe .ro+p{margin-top:8px}.po{display:block;max-width:100%;margin-bottom:16px}.po img{width:100%;aspect-ratio:1;object-fit:cover}
.ls.nt{padding:32px 0}.ls.nt p{font-weight:600;font-size:15px;line-height:28px}
/* more ways in: two cards a row, picture above a colour block */
.xcs{display:grid;grid-template-columns:repeat(2,504px);justify-content:center;gap:48px 64px;padding:96px 24px 48px}
.xc{display:flex;flex-direction:column;min-width:0}.xc img{width:100%;height:257px;object-fit:cover}.xd{flex:1;display:block;background:var(--c2);color:var(--c2i);padding:32px 48px}
.xd .t{display:block;font-weight:700;font-size:36px;line-height:48px;margin-bottom:8px}.xd .x{display:block;margin-bottom:27px}
/* contact */
.ct{padding:96px 0}.ct .w{display:grid;grid-template-columns:634fr 558fr;column-gap:64px;align-items:start}
.ct h2{font-weight:700;font-size:60px;line-height:72px;margin-bottom:32px}.ct .lead{max-width:610px;margin-bottom:27px}
.big{line-height:48px;font-weight:600;margin-bottom:8px}.big a{text-decoration:underline;text-underline-offset:5px;text-decoration-thickness:2px;white-space:nowrap}
.ad{margin-top:32px}.ad .nm{font-weight:700;font-size:20px;line-height:31px;margin-bottom:8px}.sm2{margin-top:16px}.sm2 .si{margin-bottom:8px}.sm2 .v{font-size:18px;line-height:28px}
.cr{padding-top:12px}.hn{font-weight:600;margin:-24px 0 48px}.so{display:flex;flex-wrap:wrap;gap:8px 24px;margin-top:32px;font-weight:600}.so a,.rt a{text-decoration:underline}.rt{margin-bottom:20px}.cr .btn{margin-top:28px}
/* closing: a colour block with a round end over a photograph that runs to the window's edge */
.cz{position:relative;display:flex;min-height:540px;background:var(--c3);color:var(--c3i);overflow:hidden}
.cb{position:relative;z-index:1;flex:1;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;padding:64px 128px}
.cz h2{font-weight:700;font-size:60px;line-height:72px;max-width:651px;margin-bottom:32px}
.cz.pic .cb{flex:none;width:58.3%;background:var(--c3);border-radius:0 270px 270px 0}.cp{position:absolute;top:0;bottom:0;right:0;width:58.8%}.cp img{width:100%;height:100%;object-fit:cover}
.cz .ptc{flex-direction:row;width:44%}.cz .ptc i{background:var(--bright)}.cz .ptc i+i{background:linear-gradient(135deg,var(--bright) 50%,var(--c2) 50%)}
/* foot */
.ft{padding:48px 0 32px}.f1{display:flex;gap:32px;align-items:flex-start}.fm{flex:0 0 202px}.flw{display:flex;align-items:flex-start;width:205px;height:146px}.fl{max-width:100%;max-height:100%;object-fit:contain;object-position:left top}.fn{font-weight:700;font-size:20px;line-height:24px}
.fcs2{flex:1;display:flex;justify-content:flex-end;gap:24px 128px;flex-wrap:wrap;padding-right:64px}.fcol{display:flex;flex-direction:column;font-weight:600;font-size:16px;line-height:24px}.fcol a{padding:12px 0}.fcol a:first-child{padding-top:0}
.fcol a:hover,.f2 a:hover{color:var(--link)}.f2{display:flex;flex-wrap:wrap;gap:8px 48px;margin-top:48px;font-weight:600;font-size:14px;line-height:21px}
.f3{margin-top:12px;font-size:13px;line-height:28px;color:color-mix(in srgb,var(--i) 80%,var(--g))}.no{margin-top:24px;font-size:13px;line-height:22px}
@media (max-width:1399px){.pn{display:none}.mr{display:flex}.mnw{height:95px}.mn{height:95px}.w{padding:0 48px}.bn h2{font-size:min(42px,calc(34vw / var(--mw,1) / .6))}.lc h3{font-size:min(42px,calc(24vw / var(--mw,1) / .6))}
 .bc{padding:64px 48px 64px 64px}.blk{padding:96px 64px}.ptx,.cb{padding-left:64px;padding-right:64px}.lcs{margin:32px}.lc img{margin:24px}.xcs{grid-template-columns:repeat(2,minmax(0,504px))}}
@media (min-width:1400px){.mm{display:none}.mr{display:none}}
@media (max-width:991px){
 .tb{display:none}.w{padding:0 32px}h1,h2,h3,h4,.t{overflow-wrap:anywhere}
 .mn .w{padding:0 12px 0 23px;gap:12px}.brand{flex:1 1 auto}.bnm{font-size:14px;line-height:17px;max-width:none}.mcta{max-width:38vw;padding:10px 16px}.mcta.long{display:none}.panel .btn{margin-top:32px}.mr{gap:4px}.lgw{width:123px;height:79px}
 .top.has-bk::after{background:rgba(0,0,0,.6)}
 .hero .w{min-height:666px;padding-top:32px;justify-content:flex-start}.hero .btn{margin-top:auto;background:#fff;color:#000}.hero .btn::before{background:var(--bright)}
 h1,.fcd .t,.bn h2,.lc h3,.p2 .lc h3,.blk h2,.xd .t{font-size:min(50px,calc((100vw - 64px) / var(--mw,1) / .6));line-height:1.2}.st h2,.ls h2,.ct h2,.cz h2{font-size:min(42px,calc((100vw - 64px) / var(--mw,1) / .6))!important;line-height:1.2!important}.li h3,.pe h3{font-size:min(36px,calc((100vw - 64px) / var(--mw,1) / .6))!important;line-height:1.33!important}.hero p{margin-bottom:43px}
 .fcs,.fcs.n2{grid-template-columns:1fr}.fct img{width:100%;max-width:403px}.full .fct img{max-width:none}.fcd{padding:32px;min-height:0}.fcd .t{margin-bottom:16px}
 .bn{display:flex;flex-direction:column;min-height:0;background:var(--g);color:var(--i)}.bn .bc{order:1;align-self:stretch;max-width:none;padding:48px 32px 16px}.bn .bp{order:2;height:374px}
 .bc .btn{min-width:0;min-height:0;padding:0;background:none;color:var(--link);font-weight:600;font-size:18px;gap:16px;justify-content:flex-start;margin-bottom:16px;overflow:visible;text-align:left}.bc .btn::before{display:none}.bc .btn .ar{display:inline-block;width:27px}
 .lcs,.lcs.p2{grid-template-columns:1fr;margin:0}.lc{padding:32px 32px 48px}.lc.has-r{padding-bottom:96px}.lc img{margin:0 0 32px;max-width:100%}.lc .r{left:32px}
 .sm{padding:48px 19px}.st .w{grid-template-columns:1fr;padding:0 52px}
 .ptx{min-height:0;padding:48px 32px}.pt:not(.qt) .ptx{min-height:620px}.ptx p{font-size:32px;line-height:46px}.ptc{display:none}
 .blk{padding:64px 32px}.eb{font-size:18px}.fis,.cis,.two,.cqs,.lis{grid-template-columns:minmax(0,1fr)}.cqs{padding:0}
 .fi{margin-bottom:48px}.fi .v{font-size:42px;line-height:48px}.fi .l{max-width:none}.ci .v,.si .v,.pp b{font-size:32px;line-height:42px}.two>div+div{margin-top:48px}
 .cq h3{font-size:32px;line-height:42px}.fg summary{flex-wrap:wrap;padding:24px 0}.fn{flex-basis:calc(100% - 56px)}.gn{font-size:min(32px,calc((100vw - 120px) / var(--mw,1) / .6));line-height:42px}.gv{order:3;flex-basis:100%;text-align:left;font-size:28px;line-height:36px;white-space:normal}.pm{order:2}.crs{padding:64px 0 32px}
 .ls{padding-top:64px}
 .xcs{grid-template-columns:minmax(0,1fr);padding:48px 0 0;gap:48px}.xc{flex-direction:column-reverse}.xc img{width:calc(100% - 64px);margin:0 32px;height:auto;aspect-ratio:504/257}.xd{background:none;color:var(--i);padding:0 32px 32px}.xd .t{margin-bottom:16px}.xd .x{margin-bottom:16px}.xd .ar{width:31px}
 .ct{padding:64px 0}.ct .w{grid-template-columns:minmax(0,1fr)}.cr{margin-top:48px}.si .k{flex-basis:100%}.si .v{margin-left:0;text-align:left}.si .v2{margin-left:0;text-align:left}.si{margin-bottom:32px}.hn{margin-top:-8px}
 .cz{min-height:376px}.cz .cb,.cz.pic .cb{width:auto;flex:1;border-radius:0;padding:48px 32px}.cp,.cz .ptc{display:none}
 .f1{flex-direction:column;gap:32px}.fm{flex:none}.flw{width:123px;height:106px}.fcs2{flex-direction:column;justify-content:flex-start;gap:0;padding:0}.fcol a,.fcol a:first-child{padding:12px 0}.ft .btn{min-height:50px}.f2{flex-direction:column;gap:15px}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}}
"""

JS = r"""(function(){var h=document.documentElement;h.classList.add('js');var mn=document.getElementById('mn');if(!mn)return;var wrap=mn.parentNode,mm=mn.querySelector('.mm');
function st(){var on=window.scrollY>wrap.offsetTop+(window.innerWidth>=992?0:0)&&window.scrollY>0;mn.classList.toggle('stuck',on)}
addEventListener('scroll',st,{passive:true});addEventListener('resize',st);st();
if(mm){mm.addEventListener('toggle',function(){mn.classList.toggle('open',mm.open);document.body.style.overflow=mm.open?'hidden':''});
addEventListener('keydown',function(e){if(e.key==='Escape'&&mm.open){mm.open=false;mm.querySelector('summary').focus()}});
mm.querySelectorAll('.panel a').forEach(function(a){a.addEventListener('click',function(){mm.open=false})});
addEventListener('resize',function(){if(innerWidth>=1400&&mm.open)mm.open=false})}
var v=document.querySelector('video.bk');if(v&&matchMedia('(prefers-reduced-motion:reduce)').matches){v.removeAttribute('autoplay');v.pause()}})();"""


def render(d: dict) -> str:
    R = _roles(d.get('palette') or {})
    P = Photos(d)
    # pictures that belong to a thing are kept for it
    for s in ((d.get('steps') or {}).get('items') or []) + ((d.get('place') or {}).get('spaces') or []):
        P.hold(s.get('img'))
    t = d.get('team') or {}
    for m in (t.get('items') or []) + [m for g in (t.get('groups') or []) for m in (g.get('items') or [])]:
        P.hold(m.get('img'))
    for g in ((d.get('catalogue') or {}).get('groups') or []):
        P.hold(g.get('img'))
        for it in (g.get('items') or []):
            P.hold(it.get('img'))
    for c in (d.get('credentials') or []):
        P.hold(c.get('img'))
    for pr in (d.get('projects') or []):
        for src in (pr.get('photos') or []):
            P.hold(src if isinstance(src, str) else (src or {}).get('src'))

    back, hero = s_hero(d, R, P)
    tb, mn = s_header(d, R, True)
    # the order pictures are given out in: opening, the wide picture over the statement, the banners, the closing
    # block, the three cards, the further cards, the bands that break long lists
    tp = team_picture(d, P)
    statement = s_statement(d, R, P)
    steps = s_steps(d, R, P)
    cards = s_cards(d, R, P)
    close = s_close(d, R, P)
    more = s_more(d, R, P)
    cat = s_catalogue(d, R, P)
    team = s_team(d, R, P, tp)
    body = (tb + f'<div class="top{" has-bk" if back else ""}">{back}{mn}{hero}</div>' + '<main>' + cards + steps + statement + s_pattern(d, R)
            + s_figures(d, R) + s_quotes(d, R) + s_credentials(d, R) + s_features(d, R) + cat + s_plans(d, R) + team + s_faq(d, R) + more
            + s_contact(d, R) + close + '</main>' + s_foot(d, R))
    b = d.get('brand') or {}
    title = ' — '.join(x for x in [b.get('name'), (d.get('hero') or {}).get('title')] if x)
    var = ';'.join(f'--{k}:{v}' for k, v in R.items())
    return (f'<!doctype html><html lang="{e(d.get("lang") or "en")}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)}</title><meta name="description" content="{e((d.get("hero") or {}).get("text") or "")}">'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="{FONTS}">'
            f'<style>:root{{{var}}}{CSS}</style></head><body>{body}<script>{JS}</script></body></html>')
