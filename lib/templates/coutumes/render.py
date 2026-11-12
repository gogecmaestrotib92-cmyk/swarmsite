"""coutumes — a template for small shops, rebuilt from coutumes.com/fr (measured 2026-11-12 at 1440 and 390).

render(d) -> one self-contained page. Pure: no file reads, no clock, no model. See NOTES.md for the measures.
The build: a fixed 72 px bar that is clear over the opening and turns to the page ground after it; an opening of two
photographs side by side, one screen high, with the title in very large condensed capitals standing on its lower edge;
a centred 28 px serif paragraph with one italic underlined link; a rail of 4:5 product cards (picture, name and note
left, price right) with a 1 px progress line; a full-bleed picture band with a centred 48 px title; a rail of 4:5
picture tiles each carrying its name in the same condensed capitals; a row of small wide capitals; a foot on the
display colour with a ruled line, three columns of small links and the name set very large.
"""
from html import escape as _e

_FONTS = ('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,500..700'
          '&family=Literata:ital,opsz,wght@0,7..72,400..800;1,7..72,400&family=Saira+Extra+Condensed:wght@800&display=swap')
_W = {  # words the build itself needs (controls and column heads); never client copy
    'en': ('Menu', 'Close', 'View all', 'Opening hours', 'Contact', 'Skip to content'),
    'fr': ('Menu', 'Fermer', 'Tout voir', 'Horaires', 'Contact', 'Aller au contenu'),
    'de': ('Menü', 'Schließen', 'Alle ansehen', 'Öffnungszeiten', 'Kontakt', 'Zum Inhalt'),
    'es': ('Menú', 'Cerrar', 'Ver todo', 'Horario', 'Contacto', 'Ir al contenido'),
    'it': ('Menu', 'Chiudi', 'Vedi tutto', 'Orari', 'Contatti', 'Vai al contenuto'),
    'pt': ('Menu', 'Fechar', 'Ver tudo', 'Horário', 'Contacto', 'Ir para o conteúdo'),
    'nl': ('Menu', 'Sluiten', 'Alles bekijken', 'Openingstijden', 'Contact', 'Naar inhoud'),
    'sr': ('Meni', 'Zatvori', 'Pogledaj sve', 'Radno vreme', 'Kontakt', 'Na sadržaj'),
}
_GENERIC = ('room', 'exterior', 'workshop', 'work', 'landscape', 'bar', 'dish', 'action', 'product', 'detail', 'other', '')


# ---------- colour ----------
def _rgb(h):
    h = (h or '').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def _con(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _sat(c):
    mx, mn = max(c), min(c)
    return 0 if mx == 0 else (mx - mn) / mx


def _colours(p):
    g = _rgb(p.get('ground')) or (255, 255, 255)
    ink = _rgb(p.get('ink')) or ((20, 20, 20) if _lum(g) > .4 else (245, 245, 245))
    if _con(g, ink) < 7:
        ink = (16, 16, 16) if _lum(g) > .4 else (248, 248, 248)
    acc = _rgb(p.get('accent')) or ink
    # the display colour: the reference sets its largest type and its foot in one light saturated colour.
    # The client's lightest saturated palette colour takes that part; a dark accent is lightened along its own hue.
    cands = [c for c in [acc] + [_rgb(x) for x in (p.get('extra') or [])] if c and _sat(c) > .1]
    disp = max(cands, key=_lum) if cands else None
    if disp is None:
        disp = (255, 255, 255)
    t = 0
    while _lum(disp) < .55 and t < 30:
        disp = _mix(disp, (255, 255, 255), .08)
        t += 1
    dark = ink if _lum(ink) < _lum(g) else g
    veil = _mix(dark, (0, 0, 0), .5)
    t = 0
    while _lum(veil) > .02 and t < 20:
        veil = _mix(veil, (0, 0, 0), .3)
        t += 1
    foot_ink = max([ink, g, (0, 0, 0), (255, 255, 255)][:2], key=lambda c: _con(c, disp))
    if _con(foot_ink, disp) < 4.6:
        foot_ink = max([(0, 0, 0), (255, 255, 255)], key=lambda c: _con(c, disp))
    mute, t = _mix(ink, g, .45), .45
    while _con(mute, g) < 4.8 and t > 0:
        t -= .05
        mute = _mix(ink, g, t)
    return {'g': _hex(g), 'i': _hex(ink), 'd': _hex(disp), 'v': '%d,%d,%d' % tuple(round(x) for x in veil),
            'h': _hex(_mix(g, ink, .12)), 'q': _hex(_mix(g, ink, .06)), 'm': _hex(mute), 'fi': _hex(foot_ink),
            'dark': _lum(g) < .4}


# ---------- type fitting (Saira Extra Condensed 800 capitals, advance in em, measured: 13 letters = 4.94 em) ----------
def _em(s):
    w = 0
    for ch in s.upper():
        if ch in 'MW':
            w += .56
        elif ch in 'IJ1':
            w += .24
        elif ch == ' ':
            w += .19
        elif ch in ".,:;'’!·-–|":
            w += .19
        elif ch in '&@%':
            w += .5
        else:
            w += .41
    return w - .021 * len(s)


def _lines(s, width_em):
    n, cur = 1, 0
    for wd in s.split():
        w = _em(wd)
        if cur and cur + .19 + w > width_em:
            n, cur = n + 1, w
        else:
            cur = cur + (.19 if cur else 0) + w
    return n


def _fit(s, top, low, maxlines, width_vw):
    """largest size in vw, from `top` down, at which s sets in maxlines lines of width_vw (estimate kept 8 % safe)"""
    s = s.strip()
    longest = max((_em(w) for w in s.split()), default=1)
    size = top
    while size > low:
        if longest * size * 1.08 <= width_vw and _lines(s, width_vw / (size * 1.08)) <= maxlines:
            break
        size -= .25
    return round(size, 2)


# ---------- small helpers ----------
def _src(p):
    return p if (p or '').startswith(('http://', 'https://', 'data:', '../')) else '../../' + p


def _a(o):
    return isinstance(o, dict) and o.get('t') and o.get('h')


def _tokens(*texts):
    out = set()
    for t in texts:
        for w in ''.join(ch.lower() if ch.isalnum() else ' ' for ch in (t or '')).split():
            if len(w) >= 4:
                out.add(w[:-1] if w.endswith('s') else w)
    return out - {'with', 'from', 'that', 'this', 'your', 'ours', 'bespoke', 'about', 'home', 'welcome'}


class _Photos:
    """Each photograph is placed once. Slots named by the data come first; the rest are chosen by role and size."""

    def __init__(self, d):
        self.meta, self.used, self.order = {}, set(), []
        for p in ((d.get('media') or {}).get('photos') or []):
            if isinstance(p, dict) and p.get('src'):
                self.meta[p['src']] = p
                self.order.append(p['src'])

    def take(self, src):
        if not src or src in self.used:
            return None
        self.used.add(src)
        return dict(self.meta.get(src) or {}, src=src)

    def by_words(self, *texts, minw=0):
        want = _tokens(*texts)
        if not want:
            return None
        for s in self.order:
            p = self.meta[s]
            if s in self.used or p.get('role') in ('portrait', 'people') or (p.get('w') or 0) < minw:
                continue
            if want & _tokens(s.rsplit('/', 1)[-1].rsplit('.', 1)[0]):   # the file's name, not the alt: fewer chance matches
                return self.take(s)
        return None

    def like(self, src, minw=700):
        """a free photograph of the same role as `src` (which went to a priced product), upright or square first"""
        role = (self.meta.get(src) or {}).get('role')
        if not role or role in ('portrait', 'people'):
            return None
        return self.pick(minw, minw, .6, 1.3, roles=(role,)) or self.pick(minw, 500, 1.3, 2.4, roles=(role,))

    def pick(self, minw, minh, lo, hi, roles=_GENERIC, avoid_role=None):
        best = None
        for s in self.order:
            p = self.meta[s]
            w, h, role = p.get('w') or 0, p.get('h') or 0, p.get('role') or ''
            if s in self.used or p.get('small') or role in ('portrait', 'people') or role not in roles:
                continue
            if w < minw or h < minh or not h or not (lo <= w / h <= hi):
                continue
            rank = (role == avoid_role, roles.index(role))
            if best is None or rank < best[0]:
                best = (rank, s)
        return self.take(best[1]) if best else None


def _img(p, cls='', eager=False, alt=None):
    if not p:
        return ''
    wh = f' width="{int(p["w"])}" height="{int(p["h"])}"' if p.get('w') and p.get('h') else ''
    return (f'<img class="{cls}" src="{_e(_src(p["src"]))}" alt="{_e(alt if alt is not None else (p.get("alt") or ""))}"{wh}'
            f'{"" if eager else " loading=lazy"} decoding="async">')


def _price(it):
    out = []
    if it.get('price'):
        out.append(_e(str(it['price'])))
    for pr in it.get('prices') or []:
        if isinstance(pr, dict) and pr.get('price'):
            out.append((_e(pr.get('label', '')) + ' ' if pr.get('label') else '') + _e(str(pr['price'])))
    return '<br>'.join(out)


# ---------- parts ----------
def _rail(cards, cls=''):
    return (f'<div class="rail {cls}"><div class="rail-s" tabindex="-1">{"".join(cards)}</div>'
            '<div class="bar" aria-hidden="true"><i></i></div></div>')


def _head(title, link=None, tag='h2'):
    if not title and not link:
        return ''
    l = f'<a class="lab" href="{_e(link[1])}">{_e(link[0])}</a>' if link else ''
    return f'<header class="hd">{f"<{tag}>{_e(title)}</{tag}>" if title else "<span></span>"}{l}</header>'


def _cap(name, sub, price, text='', tag='h3'):
    s = f'<p class="sub">{sub}</p>' if sub else ''
    t = f'<p class="txt">{_e(text)}</p>' if text else ''
    pr = f'<p class="pr">{price}</p>' if price else ''
    return f'<div class="cap"><div><{tag}>{_e(name)}</{tag}>{s}{t}</div>{pr}</div>'


def _card(it, photo, href):
    sub = ' · '.join(_e(x) for x in [it.get('note'), None if photo else it.get('state')] if x)
    badge = f'<span class="chip">{_e(it["state"])}</span>' if photo and it.get('state') else ''
    rows = ''.join(f'<li>{_e(r)}</li>' for r in (it.get('rows') or []) if r)
    body = _cap(it.get('name', ''), sub, _price(it), it.get('text', '') if not photo else '')
    if rows:
        body += f'<ul class="rows">{rows}</ul>'
    pic = f'<div class="ph">{badge}{_img(photo, alt=it.get("name", ""))}</div>' if photo else ''
    inner = pic + body
    cls = 'card' if photo else 'card bare'
    return f'<a class="{cls}" href="{_e(href)}">{inner}</a>' if href else f'<div class="{cls}">{inner}</div>'


def _tile(title, photo, href, cap_title='', cap_text='', cols=4):
    t = (title or '').strip()
    wd = {4: 23.4, 3: 31.4, 2: 47.6, 1: 96}[cols]
    fs = _fit(t, 5.59, 2.4, 2, wd) if t else 0
    fm = _fit(t, 16.28, 7, 2, 67) if t else 0
    name = f'<span class="tn" style="--fs:{fs}vw;--fm:{fm}vw">{_e(t)}</span>' if t else ''
    pic = (f'<span class="tp">{_img(photo)}<span class="tv"></span>{name}</span>' if photo
           else f'<span class="tp none">{name}</span>')
    cap = _cap(cap_title, '', '', cap_text) if (cap_title or cap_text) else ''
    inner = pic + cap
    return f'<a class="tile" href="{_e(href)}">{inner}</a>' if href else f'<div class="tile">{inner}</div>'


def _inter(text, link=None, by=''):
    if not text:
        return ''
    l = f'<a class="il" href="{_e(link["h"])}">{_e(link["t"])}</a>' if _a(link) else ''
    b = f'<p class="lab by">{_e(by)}</p>' if by else ''
    return f'<section class="inter"><p class="big">{_e(text)}</p>{b}{l}</section>'


def render(d: dict) -> str:
    c = _colours(d.get('palette') or {})
    lang = (d.get('lang') or 'en')[:2]
    W = _W.get(lang, _W['en'])
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    hero = d.get('hero') or {}
    place = d.get('place') or {}
    contact = d.get('contact') or {}
    cat = d.get('catalogue') or {}
    ph = _Photos(d)
    title = (hero.get('title') or name).strip()

    # ---- pictures named by the data: a priced product keeps its own picture; then stories, projects, the rest ----
    groups = [g for g in (cat.get('groups') or []) if isinstance(g, dict) and g.get('items')]
    card_ph = {}
    for gi, g in enumerate(groups):
        for ii, it in enumerate(g['items']):
            if it.get('img') and (it.get('price') or it.get('prices')):
                card_ph[(gi, ii)] = ph.take(it['img'])
    steps = d.get('steps') or {}
    s_items = [s for s in (steps.get('items') or []) if isinstance(s, dict) and (s.get('k') or s.get('title'))]
    s_ph = [ph.take(s.get('img')) for s in s_items]
    projects = [p for p in (d.get('projects') or []) if isinstance(p, dict) and p.get('title')]
    p_ph = []
    for p in projects:
        got = None
        for s in p.get('photos') or []:
            got = ph.take(s if isinstance(s, str) else (s or {}).get('src'))
            if got:
                break
        p_ph.append(got)
    for gi, g in enumerate(groups):
        for ii, it in enumerate(g['items']):
            if it.get('img') and (gi, ii) not in card_ph:
                card_ph[(gi, ii)] = ph.take(it['img'])
    team = d.get('team') or {}
    people = list(team.get('items') or [])
    for tg in team.get('groups') or []:
        people += tg.get('items') or []
    people = [p for p in people if isinstance(p, dict) and p.get('name')]
    t_ph = [ph.take(p.get('img')) for p in people]
    # a story or project whose own picture went to a product: a free photograph that shares a word with it, else none
    g_ph = {}
    for gi, g in enumerate(groups):   # a group none of whose items has a picture may have one of its own
        if not any((gi, ii) in card_ph and card_ph[(gi, ii)] for ii in range(len(g['items']))):
            g_ph[gi] = ph.take(g.get('img')) or ph.by_words(g.get('t'), minw=1600)
            if not g_ph[gi]:
                del g_ph[gi]
    for i, p in enumerate(projects):
        if not p_ph[i]:
            p_ph[i] = ph.by_words(p.get('title'), minw=700)
    # ---- pictures chosen by role and size ----
    video = (d.get('media') or {}).get('video') or None
    h1p = ph.pick(1400, 1200, .6, 1.62)
    h2p = ph.pick(1400, 1200, .6, 1.62, roles=('product', 'work', 'dish', 'detail', 'room', 'workshop', 'bar', 'exterior', 'landscape', 'action', 'other', ''),
                  avoid_role=(h1p or {}).get('role')) if h1p else None
    if not h1p:
        h1p = ph.pick(1600, 900, 1.2, 2.2)
    statement = d.get('statement') or {}
    band_p = None
    if statement.get('title') and not (isinstance(video, dict) and video.get('src')):
        calm = ('room', 'workshop', 'work', 'landscape', 'bar', 'dish', 'action', 'product', 'detail', 'other', '', 'exterior')  # a front with its sign last
        band_p = ph.pick(1600, 900, 1.25, 2.4, roles=calm) or ph.pick(1600, 1200, .9, 1.25, roles=calm)
    for i, s in enumerate(s_items):   # after the opening and the band have theirs
        if not s_ph[i]:
            s_ph[i] = ph.by_words(s.get('k'), s.get('title'), minw=700) or ph.like(s.get('img'))
    for gi, g in enumerate(groups):   # an unpriced item (a kind of work) without a picture: a free photograph named for it
        for ii, it in enumerate(g['items']):
            if isinstance(it, dict) and not card_ph.get((gi, ii)) and gi not in g_ph and not (it.get('price') or it.get('prices')):
                card_ph[(gi, ii)] = ph.by_words(it.get('name'), minw=350)
    quotes = [q for q in (d.get('quotes') or []) if isinstance(q, dict) and q.get('q')][:3]
    quote_p = ph.pick(1600, 900, 1.25, 2.4) if quotes else None

    # ---- header ----
    nav = [n for n in (d.get('nav') or []) if _a(n)]
    right = [x for x in (d.get('signin'), d.get('cta')) if _a(x)]

    def bar_px(r):  # Literata 16 px sets about 8.4 px a letter; 280 px brand column, 40 px gaps, 24 px insets
        return 280 + 72 + sum(len(n['t']) * 8.4 + 40 for n in nav + r)
    if bar_px(right) > 1400 and len(right) and _a(hero.get('primary')) and right[-1]['h'] == hero['primary']['h']:
        right = right[:-1]      # the same link stands under the opening paragraph
    bp = max(1179, int(bar_px(right)) + 8)
    logo = (f'<img src="{_e(_src(brand["logo"]))}" alt="{_e(name)}">' if brand.get('logo') else _e(name))
    home = _e(brand.get('home') or '#top')
    navl = ''.join(f'<a href="{_e(n["h"])}">{_e(n["t"])}</a>' for n in nav)
    rl = ''.join(f'<a href="{_e(n["h"])}">{_e(n["t"])}</a>' for n in right)
    burger = ''
    if nav or right:
        rows = ''.join(f'<a href="{_e(n["h"])}">{_e(n["t"])}</a>' for n in nav)
        low = ''.join(f'<a href="{_e(n["h"])}">{_e(n["t"])}</a>' for n in right)
        burger = (f'<details class="mm"><summary aria-label="{_e(W[0])}"><span class="bg"><i></i><i></i><i></i></span>'
                  f'<span class="x">{_e(W[1])}</span></summary><div class="mp"><nav class="mr">{rows}</nav>'
                  f'<nav class="ml">{low}</nav></div></details>')
    header = (f'<header class="top" id="top"><a class="skip" href="#main">{_e(W[5])}</a>{burger}'
              f'<a class="brand" href="{home}">{logo}</a><nav class="n1">{navl}</nav><nav class="n2">{rl}</nav></header>')

    # ---- opening ----
    fs_d, fs_m = _fit(title, 12, 5, 3, 94), _fit(title, 23, 9, 6, 94)
    hl = (f'<a class="hl" href="{_e(hero["primary"]["h"])}" aria-label="{_e(hero["primary"]["t"])}"></a>'
          if _a(hero.get('primary')) else '')
    if h1p:
        halves = f'<span class="hh">{_img(h1p, eager=True)}</span>' + (f'<span class="hh two">{_img(h2p, eager=True)}</span>' if h2p else '')
        opening = (f'<section class="hero{" duo" if h2p else ""}" data-slot="hero">{halves}<span class="hv"></span>'
                   f'<h1 style="--fs:{fs_d}vw;--fm:{fs_m}vw">{_e(title)}</h1>{hl}</section>')
    else:
        opening = f'<section class="hero plain"><h1 style="--fs:{fs_d}vw;--fm:{fs_m}vw">{_e(title)}</h1>{hl}</section>'

    parts = [opening]
    lead = ' '.join(x for x in (hero.get('text'), hero.get('text2')) if x)
    parts.append(_inter(lead, hero.get('primary')))

    # ---- catalogue rails ----
    def group_html(gi, g, first):
        pics, bare = [], []
        for ii, it in enumerate(g['items']):
            if not isinstance(it, dict) or not it.get('name'):
                continue
            p = card_ph.get((gi, ii))
            (pics if p else bare).append(_card(it, p, it.get('h') or ''))
        gt = g.get('t') or (cat.get('title') if first else '') or ''
        link = (g.get('text') if g.get('text') and len(g['text']) <= 28 else W[2], g['h']) if g.get('h') else None
        intro = cat.get('text') if first and cat.get('text') else ''
        if g.get('text') and len(g['text']) > 28:
            intro = (intro + ' ' if intro else '') + g['text']
        gp = g_ph.get(gi)
        if gp and gt:
            ar = max(2.5, gp['w'] / gp['h']) if gp.get('w') and gp.get('h') else 2.5
            bl = f'<span class="bl">{_e(link[0])}</span>' if link else ''
            inner = f'{_img(gp)}<span class="bv"></span><span class="bt"><h2 class="h2">{_e(gt)}</h2>{bl}</span>'
            out = (f'<a class="band gb" style="--ar:{ar:.3f}" href="{_e(g["h"])}">{inner}</a>' if g.get('h')
                   else f'<div class="band gb" style="--ar:{ar:.3f}">{inner}</div>')
        else:
            out = _head(gt, link)
        if intro:
            out += f'<p class="intro">{_e(intro)}</p>'
        if pics:
            out += _rail(pics)
        if bare:
            out += f'<div class="grid">{"".join(bare)}</div>'
        return f'<section class="sec" data-slot="catalogue">{out}</section>'

    if groups:
        parts.append(group_html(0, groups[0], True))
    elif (d.get('features') or {}).get('items'):
        f = d['features']
        cells = ''.join(_card({'name': x.get('t', ''), 'text': x.get('d', '')}, None, '') for x in f['items'] if isinstance(x, dict) and x.get('t'))
        intro = f'<p class="intro">{_e(f["text"])}</p>' if f.get('text') else ''
        parts.append(f'<section class="sec">{_head(f.get("title"))}{intro}<div class="grid">{cells}</div></section>')

    # ---- the picture band and the paragraph it leads ----
    if statement.get('title'):
        sec = hero.get('secondary')
        bl = f'<span class="bl">{_e(sec["t"])}</span>' if _a(sec) else ''
        if isinstance(video, dict) and video.get('src'):
            post = f' poster="{_e(_src(video["poster"]))}"' if video.get('poster') else ''
            med = (f'<video src="{_e(_src(video["src"]))}"{post} autoplay muted loop playsinline preload="metadata" '
                   f'aria-label="{_e(video.get("alt") or "")}"></video>')
        else:
            med = _img(band_p)
        inner = f'{med}<span class="bv"></span><span class="bt"><span class="h2">{_e(statement["title"])}</span>{bl}</span>'
        cls = 'band' if med else 'band none'
        tag = (f'<a class="{cls}" href="{_e(sec["h"])}" data-slot="band">{inner}</a>' if _a(sec)
               else f'<div class="{cls}" data-slot="band">{inner}</div>')
        parts.append(f'<section aria-label="{_e(statement["title"])}">{tag}</section>')
    parts.append(_inter(statement.get('text')))

    for gi, g in enumerate(groups[1:], 1):
        parts.append(group_html(gi, g, False))

    # ---- tiles: stories, then named pieces of work ----
    def tiles_html(items, heading, text=''):
        n = len(items)
        if not n:
            return ''
        wide_ok = all((p or {}).get('w', 9999) >= {1: 1424, 2: 708, 3: 469}.get(n, 350) for _, p, _, _, _ in items)
        cols = n if (n < 4 and wide_ok) else 4
        cells = [_tile(t, p, h, ct, cx, cols) for t, p, h, ct, cx in items]
        intro = f'<p class="intro">{_e(text)}</p>' if text else ''
        return f'<section class="sec tiles c{cols}" data-slot="tiles">{_head(heading)}{intro}{_rail(cells, "tr")}</section>'

    parts.append(tiles_html([(s.get('k') or s.get('title'), s_ph[i], (s.get('cta') or {}).get('h') or '',
                              s.get('title') if s.get('k') else '', s.get('text') or '') for i, s in enumerate(s_items)],
                            steps.get('title'), steps.get('text')))
    parts.append(tiles_html([(p['title'], p_ph[i], p.get('h') or '', '', p.get('text') or '') for i, p in enumerate(projects)], ''))

    # ---- people ----
    if people:
        cards = []
        for i, p in enumerate(people):
            sub = ' · '.join(_e(x) for x in (p.get('role'),) if x)
            links = ''.join(f'<a href="{_e(h)}">{_e(t)}</a>' for t, h in (
                (p.get('phone'), 'tel:' + ''.join(ch for ch in str(p.get('phone') or '') if ch.isdigit() or ch == '+')),
                (p.get('email'), 'mailto:' + str(p.get('email') or ''))) if t)
            pic = f'<div class="ph">{_img(t_ph[i], alt=p["name"])}</div>' if t_ph[i] else ''
            body = _cap(p['name'], sub, '', p.get('text') or '')
            cards.append(f'<div class="card person{"" if pic else " bare"}">{pic}{body}{f"<p class=pl>{links}</p>" if links else ""}</div>')
        with_pic = [x for i, x in enumerate(cards) if t_ph[i]]
        without = [x for i, x in enumerate(cards) if not t_ph[i]]
        body = (_rail(with_pic) if with_pic else '') + (f'<div class="grid">{"".join(without)}</div>' if without else '')
        lead_t = _inter(team.get('text')) if team.get('text') else ''
        parts.append(f'{lead_t}<section class="sec" data-slot="team">{_head(team.get("title"))}{body}</section>')

    # ---- what customers said ----
    for qi, q in enumerate(quotes):
        by = ' · '.join(x for x in (q.get('name'), q.get('role')) if x)
        if qi == 0 and quote_p:
            byl = f'<span class="lab by">{_e(by)}</span>' if by else ''
            parts.append(f'<section><div class="band qb" data-slot="quote">{_img(quote_p)}<span class="bv"></span>'
                         f'<span class="bt"><span class="big">{_e(q["q"])}</span>{byl}</span></div></section>')
        else:
            parts.append(_inter(q['q'], None, by))

    # ---- plans and questions (the reference's home page has neither; built from its caption and its menu rows) ----
    plans = d.get('plans') or {}
    if plans.get('items'):
        cells = []
        for p in plans['items']:
            if not isinstance(p, dict) or not p.get('name'):
                continue
            price = _e(str(p.get('price') or '')) + (f' <small>{_e(p["per"])}</small>' if p.get('per') else '')
            rows = ''.join(f'<li>{_e(r)}</li>' for r in (p.get('rows') or []) if r)
            cta = f'<a class="lab u" href="{_e(p["cta"]["h"])}">{_e(p["cta"]["t"])}</a>' if _a(p.get('cta')) else ''
            mark = ' marked' if p.get('marked') else ''
            pp = f'<p class="pp">{price}</p>' if price else ''
            ln = f'<p class="txt">{_e(p["line"])}</p>' if p.get('line') else ''
            rw = f'<ul class="rows">{rows}</ul>' if rows else ''
            cells.append(f'<div class="plan{mark}"><h3>{_e(p["name"])}</h3>{pp}{ln}{rw}{cta}</div>')
        note = f'<p class="intro">{_e(plans["note"])}</p>' if plans.get('note') else ''
        intro = f'<p class="intro">{_e(plans["text"])}</p>' if plans.get('text') else ''
        parts.append(f'<section class="sec" data-slot="plans">{_head(plans.get("title"))}{intro}<div class="grid plans">{"".join(cells)}</div>{note}</section>')
    faq = d.get('faq') or {}
    if faq.get('items'):
        rows = ''.join(f'<details class="qa"><summary>{_e(x["q"])}</summary><p>{_e(x.get("a", ""))}</p></details>'
                       for x in faq['items'] if isinstance(x, dict) and x.get('q'))
        parts.append(f'<section class="sec" data-slot="faq">{_head(faq.get("title"))}<div class="qas">{rows}</div></section>')

    # ---- the rows of small capitals ----
    creds = [x for x in (d.get('credentials') or []) if isinstance(x, dict) and x.get('t')]
    if creds:
        cells = ''.join((f'<a href="{_e(x["h"])}">' if x.get('h') else '<span>') + _e(x['t'])
                        + (f'<br>{_e(str(x["year"]))}' if x.get('year') else '')
                        + (f'<em>{_e(x["text"])}</em>' if x.get('text') else '') + ('</a>' if x.get('h') else '</span>') for x in creds)
        parts.append(f'<section class="re" data-slot="credentials" style="--n:{min(len(creds), 5)}">{cells}</section>')
    trust = [t for t in (d.get('trust') or []) if isinstance(t, str) and t.strip()]
    if trust:
        parts.append(f'<section class="re" style="--n:{min(len(trust), 5)}">{"".join(f"<span>{_e(t)}</span>" for t in trust)}</section>')

    # ---- foot ----
    close = d.get('close') or {}
    ad = place.get('address') or {}
    addr = ', '.join(str(ad[k]) for k in ('street', 'city', 'region', 'postcode', 'country') if ad.get(k))
    phone = place.get('phone') or contact.get('phone') or {}
    email = place.get('email') or contact.get('email') or ''
    line = addr or (phone.get('t') if isinstance(phone, dict) else '') or email
    fl = ''
    if close.get('title') or line or close.get('text'):
        ctal = f'<a class="lab" href="{_e(close["cta"]["h"])}">{_e(close["cta"]["t"])}</a>' if _a(close.get('cta')) else ''
        fl = ((f'<h2 class="lab">{_e(close["title"])}</h2>' if close.get('title') else '')
              + (f'<p class="rule"><span>{_e(line)}</span>{ctal}</p>' if (line or ctal) else '')
              + (f'<p class="sm">{_e(close["text"])}</p>' if close.get('text') else ''))
    cols = []
    hours = [h for h in (place.get('hours') or []) if isinstance(h, dict) and h.get('days')]
    if hours:
        rows = ''.join(f'<li>{_e(h["days"])}<br>{_e(" – ".join(x for x in (h.get("open"), h.get("close")) if x))}</li>' for h in hours)
        cols.append(f'<div><h2 class="lab">{_e(W[3])}</h2><ul>{rows}</ul></div>')
    crow = []
    if isinstance(phone, dict) and phone.get('t'):
        crow.append(f'<li><a href="{_e(phone.get("h") or "tel:" + phone["t"])}">{_e(phone["t"])}</a>'
                    + (f'<br>{_e(phone["note"])}' if phone.get('note') else '') + '</li>')
    if email:
        crow.append(f'<li><a href="mailto:{_e(email)}">{_e(email)}</a></li>')
    for r in [place.get('booking'), place.get('takeaway'), contact.get('form')] + list(contact.get('routes') or []) + list(place.get('social') or []):
        if isinstance(r, dict) and r.get('t') and r.get('h') and not (close.get('cta') or {}).get('h') == r['h']:
            crow.append(f'<li><a href="{_e(r["h"])}">{_e(r["t"])}</a></li>')
    if crow:
        cols.append(f'<div><h2 class="lab">{_e(W[4])}</h2><ul>{"".join(crow)}</ul></div>')
    for loc in (d.get('locations') or [])[:2]:
        if isinstance(loc, dict) and loc.get('name'):
            la = loc.get('address') or {}
            rows = [', '.join(str(la[k]) for k in ('street', 'city', 'postcode') if la.get(k)), loc.get('phone') if isinstance(loc.get('phone'), str) else (loc.get('phone') or {}).get('t'), loc.get('note')]
            rows += [f'{h.get("days")} {h.get("open", "")}–{h.get("close", "")}' for h in (loc.get('hours') or []) if isinstance(h, dict) and h.get('days')]
            cols.append(f'<div><h2 class="lab">{_e(loc["name"])}</h2><ul>{"".join(f"<li>{_e(r)}</li>" for r in rows if r)}</ul></div>')
    links = [l for l in (d.get('links') or []) if _a(l)][:8]
    if links and len(cols) < 3:
        cols.append(f'<div><h2 class="lab">{_e(name)}</h2><ul>{"".join(f"""<li><a href="{_e(l["h"])}">{_e(l["t"])}</a></li>""" for l in links)}</ul></div>')
    foot = d.get('foot') or {}
    legal = [f'<a href="{_e(l["h"])}">{_e(l["t"])}</a>' for l in (foot.get('links') or []) if _a(l)]
    if foot.get('legal'):
        legal.append(f'<span>{_e(foot["legal"])}</span>')
    ftext = f'<p class="sm">{_e(foot["text"])}</p>' if foot.get('text') and not (addr or crow) else ''
    wm_d = round(min(6.94, 42.8 / max(1, sum(.5 if ch == ' ' else (.95 if ch in 'MW' else .74) for ch in name.upper()))), 2)
    wm_m = round(min(16, 87 / max(1, sum(.5 if ch == ' ' else (.95 if ch in 'MW' else .74) for ch in name.upper()))), 2)
    footer = (f'<footer class="ft"><div class="fr">{fl}{ftext}{f"""<div class="fc">{"".join(cols)}</div>""" if cols else ""}</div>'
              f'<p class="wm" style="--fs:{wm_d}vw;--fm:{wm_m}vw">{_e(name)}</p>'
              f'{f"""<p class="lg">{"<b>•</b>".join(legal)}</p>""" if legal else ""}</footer>')

    body = header + '<main id="main">' + ''.join(p for p in parts if p) + '</main>' + footer
    desc = _e((hero.get('text') or '')[:200])
    solid = '' if h1p else ' solid'
    return (f'<!doctype html><html lang="{_e(lang)}" class="{("dk" if c["dark"] else "lt") + solid}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{_e(name)}</title>'
            f'<meta name="description" content="{desc}"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link href="{_FONTS}" rel="stylesheet"><style>:root{{--g:{c["g"]};--i:{c["i"]};--d:{c["d"]};--v:{c["v"]};--h:{c["h"]};'
            f'--q:{c["q"]};--m:{c["m"]};--fi:{c["fi"]}}}{_CSS.replace("1179px", str(bp) + "px")}</style></head><body>{body}<script>{_JS}</script></body></html>')


_CSS = r"""
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;background:var(--g);color:var(--i);font:400 16px/24px Literata,Georgia,'Times New Roman',serif;font-optical-sizing:auto;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,video{display:block;max-width:100%}a{color:inherit;text-decoration:none}h1,h2,h3,p,ul{margin:0;padding:0;font-weight:400}ul{list-style:none}
:focus-visible{outline:2px solid currentColor;outline-offset:2px}
.lab{font:600 11px/14px Archivo,Arial,sans-serif;font-stretch:112%;text-transform:uppercase;letter-spacing:.02em}
.skip{position:absolute;left:8px;top:-60px;background:var(--g);color:var(--i);padding:8px 12px;z-index:9}.skip:focus{top:8px}
/* bar: 72 px, fixed; clear with light type over the opening, page ground after it (0.25 s) */
.top{position:fixed;inset:0 0 auto 0;height:72px;z-index:50;display:flex;align-items:center;padding:0 24px;background:var(--g);color:var(--i);border-bottom:1px solid var(--h);transition:background-color .25s,color .25s,border-color .25s}
.top.over:not(:hover):not(:focus-within){background:transparent;color:#fff;border-color:transparent}
.brand{font-weight:700;font-size:17px;letter-spacing:-.01em;text-transform:uppercase;white-space:nowrap;width:280px;flex:none}.brand img{height:22px;width:auto}
.n1,.n2{display:flex;gap:clamp(18px,2.78vw,40px);white-space:nowrap}.n2{margin-left:auto;padding-left:24px}.top nav a{padding:22px 0}.top nav a:hover{text-decoration:underline;text-underline-offset:4px;text-decoration-thickness:1px}
.mm{display:none}
/* opening: one screen, two photographs, the title on the lower edge */
.hero{position:relative;height:100vh;height:100svh;min-height:560px;overflow:hidden;display:flex;background:var(--q)}
.hh{flex:1 1 0;min-width:0;height:100%}.hh img{width:100%;height:100%;object-fit:cover}
.hv{position:absolute;inset:0;pointer-events:none;background:linear-gradient(to bottom,rgba(var(--v),.64) 0,rgba(var(--v),.6) 72px,rgba(var(--v),0) 190px),linear-gradient(to top,rgba(var(--v),.7) 0,rgba(var(--v),.68) var(--th,40%),rgba(var(--v),0) calc(var(--th,40%) + 22%))}
.hero h1{position:absolute;left:0;right:0;bottom:-.05em;margin:0 auto;padding:0 2vw;font:800 var(--fs)/.8 'Saira Extra Condensed','Arial Narrow',sans-serif;letter-spacing:-.021em;text-transform:uppercase;text-align:center;color:var(--d);text-wrap:balance;pointer-events:none;z-index:2}
.hl{position:absolute;inset:0;z-index:1}.hl:focus-visible{outline-offset:-6px;outline-color:#fff}
.hero.plain{height:auto;min-height:0;display:block;padding:calc(72px + 12vw) 0 0;background:var(--d)}.hero.plain h1{position:relative;color:var(--fi);bottom:-.06em}
/* the centred paragraph */
.inter{padding:104px 24px;text-align:center}.inter .big{font-size:28px;line-height:32px;letter-spacing:-.04em;max-width:720px;margin:0 auto;text-wrap:balance}
.il{display:inline-block;margin-top:19px;font-size:14px;line-height:17px;font-style:italic;text-decoration:underline;text-underline-offset:2px;text-decoration-thickness:1px}.il:hover{text-decoration-thickness:2px}
.by{margin-top:22px}.inter+.inter{padding-top:0}
/* section heads and rails */
.sec{padding:0 0 80px}.hd{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;padding:0 24px;min-height:56px;padding-bottom:24px}
.hd h2,.hd h1{font-size:28px;line-height:32px;letter-spacing:-.04em}.hd .lab{padding:6px 0;white-space:nowrap}.hd .lab:hover,.lab.u{text-decoration:underline;text-underline-offset:3px}
.intro{padding:0 24px 24px;max-width:760px;font-size:14px;line-height:20px;color:var(--m)}
.rail-s{display:flex;gap:8px;padding:0 8px;overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none;cursor:default;outline:0}.rail-s::-webkit-scrollbar{display:none}.rail-s.drag{cursor:grabbing;user-select:none}
.rail-s>*{flex:0 0 calc((100vw - 40px)/4);min-width:0}
.bar{display:none;height:1px;background:var(--h);margin:19px 16px 0;position:relative}.bar i{position:absolute;left:0;top:0;height:1px;background:var(--i);width:40%}.rail.sc .bar{display:block}
.card{display:block}.ph{position:relative;aspect-ratio:350/441;background:var(--q);overflow:hidden}.ph img{width:100%;height:100%;object-fit:cover}
.chip{position:absolute;left:0;top:0;z-index:2;background:var(--g);color:var(--i);padding:4px 6px;font:600 11px/14px Archivo,Arial,sans-serif;font-stretch:112%;text-transform:uppercase;letter-spacing:.02em}
.cap{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:8px 8px 0;text-align:left}.cap h3{font-size:12px;line-height:16px}.cap .sub{font-size:11px;line-height:14.3px;color:var(--m);margin-top:2px}
.cap .txt,.plan .txt{font-size:12px;line-height:16px;color:var(--m);margin-top:6px;max-width:44em}.cap .pr{font:500 12px/16px Archivo,Arial,sans-serif;font-stretch:108%;white-space:nowrap;text-align:right;flex:none}
a.card:hover h3,a.tile:hover .cap h3{text-decoration:underline;text-underline-offset:2px}
.rows{padding:8px 8px 0;font-size:12px;line-height:16px;color:var(--m)}.rows li{padding:2px 0}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0 8px;padding:0 8px}.rail+.grid{margin-top:32px}
.grid .card.bare{border-top:1px solid var(--h);padding:4px 0 20px}.grid .bare .cap h3{font-size:14px;line-height:18px}.person .cap h3{font-size:14px;line-height:18px}
.pl{padding:6px 8px 0;font-size:12px;line-height:16px;display:flex;gap:12px;flex-wrap:wrap}.pl a{text-decoration:underline;text-underline-offset:2px}
/* the picture band: 57.5vw high, title centred */
.band{position:relative;display:block;height:57.5vw;max-height:100vh;overflow:hidden;background:var(--i);color:#fff}.band img,.band video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.bv{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(var(--v),.22) 0,rgba(var(--v),.62) 38%,rgba(var(--v),.62) 62%,rgba(var(--v),.22) 100%)}
.bt{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 24px}.bt .h2{font-size:48px;line-height:55px;max-width:16em;text-wrap:balance}
.bl{margin-top:8px;font:800 14px/21px 'Saira Extra Condensed','Arial Narrow',sans-serif;letter-spacing:.04em;text-transform:uppercase}.band:hover .bl{text-decoration:underline;text-underline-offset:3px}
.gb{height:calc(100vw/var(--ar));max-height:40vw}.gb+.grid,.gb+.intro{margin-top:24px}.gb .bt h2{color:#fff}.qb{height:auto;min-height:57.5vw;display:flex}.qb .bt{position:relative;padding:120px 24px}.qb .big{font-size:28px;line-height:32px;letter-spacing:-.04em;max-width:720px;text-wrap:balance}.qb .bv{background:rgba(var(--v),.66)}.band.none{height:auto;padding:120px 0}.band.none .bt{position:relative}.band.none .bv{display:none}.band:focus-visible{outline-offset:-6px;outline-color:#fff}
section+.sec,.inter+.sec{padding-top:0}section:has(>.band)+.sec,section:has(>.band)+.inter+.sec{padding-top:40px}section:has(>.band)+.inter{padding:72px 24px 64px}
/* tiles */
.tile{display:block}.tp{position:relative;display:block;aspect-ratio:350/438;overflow:hidden;background:var(--q)}.tp img{width:100%;height:100%;object-fit:cover}
.tv{position:absolute;inset:0;background:linear-gradient(to top,rgba(var(--v),.7) 0,rgba(var(--v),.68) 40%,rgba(var(--v),.12) 66%)}
.tn{position:absolute;left:5px;right:5px;bottom:0;font:800 var(--fs)/.8 'Saira Extra Condensed','Arial Narrow',sans-serif;letter-spacing:-.021em;text-transform:uppercase;text-align:center;color:var(--d);text-wrap:balance}
.tp.none{background:var(--d)}.tp.none .tn{color:var(--fi)}
.tiles.c3 .rail-s>*{flex-basis:calc((100vw - 32px)/3)}.tiles.c2 .rail-s>*{flex-basis:calc((100vw - 24px)/2)}.tiles.c1 .rail-s>*{flex-basis:calc(100vw - 16px)}
.tiles.c2 .tp{aspect-ratio:8/5}.tiles.c1 .tp{aspect-ratio:16/5}.tile .cap{padding-top:10px}.tile .cap h3{font-size:14px;line-height:18px}
/* plans, questions */
.plans{gap:32px 8px}.plans+.intro{margin-top:28px;padding-bottom:0}.plan{border-top:1px solid var(--h);padding:16px 8px 0}.plan.marked{border-top:2px solid var(--i)}.plan h3{font-size:28px;line-height:32px;letter-spacing:-.04em}.pp{font:500 16px/24px Archivo,Arial,sans-serif;margin-top:8px}.pp small{font-size:12px;color:var(--m)}
.plan .rows{padding:12px 0 0}.plan .lab{display:inline-block;margin-top:16px}
.qas{border-top:1px solid var(--h);margin:0}.qa{border-bottom:1px solid var(--h)}.qa summary{list-style:none;cursor:pointer;padding:15px 24px;font-size:18px;line-height:24px;display:flex;justify-content:space-between;gap:24px}
.qa summary::-webkit-details-marker{display:none}.qa summary::after{content:'+';font:500 16px/24px Archivo,Arial,sans-serif}.qa[open] summary::after{content:'–'}.qa p{padding:0 24px 20px;max-width:760px;font-size:14px;line-height:20px;color:var(--m)}
/* the row of small capitals */
.re{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:24px 8px;padding:40px 8px;text-align:center;font:600 11px/14px Archivo,Arial,sans-serif;font-stretch:112%;text-transform:uppercase;letter-spacing:.02em}
.re>*{max-width:170px;margin:0 auto;text-wrap:balance}.re em{display:block;font-style:normal;font-weight:500;text-transform:none;margin-top:4px}.re+.re{padding-top:0}
/* foot */
.ft{position:relative;background:var(--d);color:var(--fi);padding:48px 24px 24px;display:grid;grid-template-columns:minmax(0,1fr) 47.5vw;gap:0 24px;overflow:hidden;min-height:41vw}
.ft{background-blend-mode:multiply;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/%3E%3CfeColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .11 0'/%3E%3C/filter%3E%3Crect width='240' height='240' filter='url(%23n)'/%3E%3C/svg%3E")}
.fr{grid-column:2}.rule{display:flex;justify-content:space-between;align-items:baseline;gap:24px;border-bottom:1px solid currentColor;padding:14px 0 10px;margin-top:10px;font-size:18px;line-height:24px}.rule .lab{white-space:nowrap;padding:4px 0}.rule .lab:hover,.ft li a:hover,.lg a:hover{text-decoration:underline;text-underline-offset:2px}
.sm{font-size:12px;line-height:16px;margin-top:13px;max-width:62em}.fc{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px 12px;margin-top:76px}.fc ul{margin-top:25px;font-size:12px;line-height:16px}.fc li{padding:0 0 8px}
.wm{grid-column:1;grid-row:2;align-self:end;font-weight:800;font-size:var(--fs);line-height:.86;letter-spacing:-.03em;text-transform:uppercase;white-space:nowrap;margin-top:80px}
.lg{grid-column:2;grid-row:2;align-self:end;font-size:12px;line-height:16px;display:flex;flex-wrap:wrap;gap:4px 12px;padding-bottom:6px}.lg b{font-weight:400}
img.fade{opacity:0;transition:opacity .25s}img.fade.in{opacity:1}
@media (max-width:1179px){
.top{height:56px;padding:0 8px;justify-content:center}.n1,.n2{display:none}.brand{width:auto;font-size:18px}
.mm{display:block;position:absolute;left:0;top:0}.mm summary{list-style:none;width:56px;height:56px;display:flex;align-items:center;justify-content:center;cursor:pointer}.mm summary::-webkit-details-marker{display:none}
.bg{display:block;width:16px}.bg i{display:block;height:1.5px;background:currentColor;margin:3.5px 0}.mm .x{display:none}
.mm[open] summary{position:fixed;z-index:3;color:var(--i)}.mm[open] .bg i:nth-child(2){opacity:0}.mm[open] .bg i:first-child{transform:translateY(5px) rotate(45deg)}.mm[open] .bg i:last-child{transform:translateY(-5px) rotate(-45deg)}
.mp{position:fixed;inset:0;background:var(--g);color:var(--i);padding-top:56px;display:flex;flex-direction:column;overflow:auto;z-index:2}.mr{border-top:1px solid var(--h)}.top .mr a{display:block;padding:15px 12px 16px;font-size:18px;line-height:24px;border-bottom:1px solid var(--h)}
.ml{margin-top:auto;padding:24px 12px 16px}.top .ml a{display:block;padding:5px 0;font-size:16px;line-height:24px}
.top:has(.mm[open]){background:var(--g)!important;color:var(--i)!important}.top:has(.mm[open]) .brand{position:relative;z-index:3}
}
@media (max-width:767px){
.hero h1{font-size:var(--fm)}.hero.duo .two{display:none}.hero.plain{padding-top:calc(56px + 22vw)}
.inter{padding:40px 8px;text-align:left}.inter .big{font-size:18px;line-height:22px;letter-spacing:0;margin:0}.il{margin-top:14px}
.hd{padding:0 8px 16px;min-height:0}.hd h2{font-size:18px;line-height:24px;letter-spacing:0}.sec{padding-bottom:64px}.intro{padding:0 8px 16px}
.rail-s>*,.tiles .rail-s>*{flex-basis:70.8vw!important}.tiles.c1 .rail-s>*{flex-basis:calc(100vw - 16px)!important}.tiles .tp{aspect-ratio:276/345!important}.tn{font-size:var(--fm)}
.bar{margin:23px 8px 0}.grid{grid-template-columns:1fr}
.band{height:125vw}.gb{height:80vw;max-height:none}.qb{height:auto;min-height:125vw}.qb .big{font-size:20px;line-height:25px;letter-spacing:-.01em}.bt .h2{font-size:32px;line-height:37px}.bl{font-size:11px;line-height:16.5px}section:has(>.band)+.sec{padding-top:24px}
.qa summary,.qa p{padding-left:8px;padding-right:8px}
.re{grid-template-columns:1fr;gap:24px;padding:40px 8px}
.ft{display:block;padding:48px 24px 24px}.fc{grid-template-columns:repeat(2,minmax(0,1fr));margin-top:56px}.wm{font-size:var(--fm);margin-top:72px;white-space:normal}.lg{margin-top:20px}
.rule{flex-wrap:wrap}
}
@media (min-width:768px){.tn{font-size:var(--fs)}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;scroll-behavior:auto!important}img.fade{opacity:1}}
"""

_JS = r"""
(function(){var D=document,top=D.querySelector('.top'),hero=D.querySelector('.hero:not(.plain)'),rm=matchMedia('(prefers-reduced-motion:reduce)').matches;
function hd(){if(!hero){return}top.classList.toggle('over',scrollY<hero.offsetHeight-top.offsetHeight)}
if(hero){hd();addEventListener('scroll',hd,{passive:true});addEventListener('resize',hd)}
var h1=D.querySelector('.hero:not(.plain) h1'),hv=D.querySelector('.hv');function th(){if(h1&&hv){hv.style.setProperty('--th',Math.round(h1.offsetHeight*.9)+'px')}}th();addEventListener('resize',th);if(D.fonts&&D.fonts.ready){D.fonts.ready.then(th)}
D.querySelectorAll('.rail').forEach(function(r){var s=r.querySelector('.rail-s'),b=r.querySelector('.bar'),i=b.firstChild;
function up(){var sc=s.scrollWidth>s.clientWidth+4;r.classList.toggle('sc',sc);if(!sc){return}var f=s.clientWidth/s.scrollWidth,w=b.clientWidth;i.style.width=(f*100)+'%';i.style.transform='translateX('+(s.scrollLeft/(s.scrollWidth-s.clientWidth))*(w-w*f)+'px)'}
up();s.addEventListener('scroll',up,{passive:true});addEventListener('resize',up);
var x0=null,l0=0,moved=0;s.addEventListener('pointerdown',function(e){if(e.pointerType!=='mouse'||s.scrollWidth<=s.clientWidth){return}x0=e.clientX;l0=s.scrollLeft;moved=0});
addEventListener('pointermove',function(e){if(x0===null){return}moved=Math.abs(e.clientX-x0);if(moved>4){s.classList.add('drag');s.scrollLeft=l0-(e.clientX-x0)}});
addEventListener('pointerup',function(){x0=null;setTimeout(function(){s.classList.remove('drag')},0)});
s.addEventListener('click',function(e){if(moved>4){e.preventDefault()}},true);s.addEventListener('dragstart',function(e){e.preventDefault()})});
if(!rm){D.querySelectorAll('img[loading=lazy]').forEach(function(m){if(m.complete){return}m.classList.add('fade');function on(){m.classList.add('in')}m.addEventListener('load',on);m.addEventListener('error',on)})}
else{D.querySelectorAll('video[autoplay]').forEach(function(v){v.removeAttribute('autoplay');v.pause();v.controls=true})}
D.addEventListener('keydown',function(e){if(e.key==='Escape'){var m=D.querySelector('.mm[open]');if(m){m.open=false;m.querySelector('summary').focus()}}});
})();
"""
