"""fluently/render.py — one pure function: render(d) -> a complete page.

The build (section order, anatomy, grid, measures, type, spacing, radii, motion, phone build) was measured on the
reference's home page at 1440 and 390 on 2026-11-12 (see NOTES.md, ref/, probe/). Nothing of the reference's code, words,
pictures, icons, logos or customers is here. The client's data fills it; a section whose data is missing is left out
whole. No file reads, no model call, no client logic.
"""
import html
import json
import re

# The reference's face is DM Sans, which is itself open-licence (SIL OFL) — used as it is.
FONTS = 'https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap'


# ───────────────────────── colour
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


def _tri(h):
    return '%d,%d,%d' % _rgb(h)


def _fit(c, bg, toward, floor=4.6):
    """c, pushed toward `toward` until it reads on bg"""
    n = 0
    while _con(c, bg) < floor and n < 20:
        c = _mix(toward, c, .12)
        n += 1
    return c


def _veil(mean, v, text, floor):
    """how much of the veil colour v a picture of this mean needs before `text` reads on it"""
    a = 0.0
    while a < .85 and _con(text, _mix(v, mean, a)) < floor:
        a += .05
    return round(a, 2)


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def m(p):
    """media paths in the data are relative to templates/; a page in <slug>/out/ reaches them two levels up"""
    p = str(p or '')
    return p if re.match(r'^(https?:)?//|^data:', p) else '../../' + p


def _wh(o):
    return ' width="%s" height="%s"' % (e(o['w']), e(o['h'])) if o.get('w') and o.get('h') else ''


def _img(o, cls='', lazy=True):
    return '<img%s src="%s" alt="%s"%s%s decoding="async">' % (
        ' class="%s"' % cls if cls else '', e(m(o.get('src'))), e(o.get('alt', '')), _wh(o), ' loading="lazy"' if lazy else '')


def _tall(o):
    return (o.get('h') or 0) > (o.get('w') or 1) * 1.15


class _Pool:
    """the client's own product pictures, handed out so that one picture is not shown twice while others wait"""

    def __init__(self, d):
        md = d.get('media') or {}
        self.items = []
        for kind in ('phones', 'screens', 'photos'):
            for x in md.get(kind) or []:
                if x.get('src'):
                    self.items.append(dict(x, kind=kind))
        self.used = {}
        for s in (d.get('steps') or {}).get('items') or []:
            if s.get('img'):
                self.used[s['img']] = 1

    def take(self, *prefs):
        """prefs: predicates in order of preference; an unused picture always wins over a used one"""
        for fresh in (True, False):
            for ok in prefs:
                for x in self.items:
                    if ok(x) and (not fresh or not self.used.get(x['src'])):
                        self.used[x['src']] = self.used.get(x['src'], 0) + 1
                        return x
        return None


def _land(made, page_dark, order, skip=()):
    """a wide made landscape whose tone agrees with the page, in the given order of preference"""
    land = made.get('land') or []
    cand = [land[i] for i in order if i < len(land) and land[i].get('src') and land[i]['src'] not in skip]
    for x in cand:
        if (x.get('tone') != 'light') == page_dark:
            return x
    return cand[0] if cand else None


def _series(made, page_dark, first):
    """the page's one motif as a series: the made landscapes whose tone agrees with the page, `first` leading"""
    land = [x for x in made.get('land') or [] if x.get('src')]
    same = [x for x in land if (x.get('tone') != 'light') == page_dark] or land
    if first and first in same:
        same = [first] + [x for x in same if x is not first]
    return same


def _over(pic, lo, hi, floor=7.0):
    """(veil colour, ink, alpha) for text laid over a made picture: a dark picture is veiled toward the darker of the
    page's two poles and takes the lighter as ink; a light one the reverse"""
    dark = pic.get('tone') != 'light'
    v, ink = (lo, hi) if dark else (hi, lo)
    mean = pic.get('mean') or ('#2a2a2a' if dark else '#dddddd')
    return v, ink, _veil(mean, v, ink, floor)


ARROW = ('<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M12 6v11M7.5 12.5 12 17l4.5-4.5" fill="none" '
         'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def _logo(b, cls='logo'):
    pic = ''
    if b.get('logo'):
        pic = '<img src="%s" alt="%s"%s>' % (e(m(b['logo'])), e(b.get('name', '')) if b.get('logo_wordmark') else '', ' class="wm"' if b.get('logo_wordmark') else '')
    name = '' if b.get('logo_wordmark') and b.get('logo') else '<span>%s</span>' % e(b.get('name', ''))
    return '<a class="%s" href="%s">%s%s</a>' % (cls, e(b.get('home') or '#'), pic, name)


def _glass(link):
    if not link or not link.get('t'):
        return ''
    return '<a class="glass" href="%s">%s</a>' % (e(link.get('h') or '#'), e(link['t']))


# ───────────────────────── sections (reference order)
def s_bar(d, ink):
    b = d.get('brand') or {}
    nav = [n for n in d.get('nav') or [] if n.get('t')]
    cta, signin = d.get('cta') or {}, d.get('signin') or {}
    seg = ''
    if nav:
        seg = '<nav class="seg wide" aria-label="Primary">%s</nav>' % ''.join('<a href="%s">%s</a>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav)
    call = ''
    if cta.get('t'):
        call = ('%s<a class="cta wide" href="%s"><span class="roll" data-t="%s"><span>%s</span></span></a>' % (
            '<span class="sep wide" aria-hidden="true"></span>' if seg else '', e(cta.get('h') or '#'), e(cta['t']), e(cta['t'])))
    small = ''.join('<a%s href="%s">%s</a>' % (' class="on"' if on else '', e(x.get('h') or '#'), e(x['t'])) for x, on in ((signin, False), (cta, True)) if x.get('t'))
    small = '<div class="seg small">%s</div>' % small if small else ''
    return '<header class="bar" id="bar" style="--nv:%s">%s<div class="bar-r">%s%s%s</div></header>' % (ink, _logo(b), seg, call, small)


def s_hero(d, pool, pic, lo, hi, ground):
    h = d.get('hero') or {}
    if not h.get('title'):
        return '', None
    if pic:
        v, ink, a = _over(pic, lo, hi)
        bg = '<img class="bg" src="%s" alt=""%s data-slot="hero-backdrop" data-kind="land" decoding="async">' % (e(m(pic['src'])), _wh(pic))
    else:
        v, ink, a, bg = ground, (hi if ground == lo else lo), 0, ''
    shot = pool.take(lambda x: x['kind'] == 'phones', lambda x: x['kind'] == 'screens', lambda x: True)
    fig = '<figure class="shot%s">%s</figure>' % (' tall' if _tall(shot) else '', _img(shot, '', False)) if shot else '<span class="shot"></span>'
    acts = _glass(h.get('primary')) + _glass(h.get('secondary'))
    hint = '<div class="hint">%s<span class="disc" aria-hidden="true"><span class="loop">%s%s</span></span></div>' % ('<p>%s</p>' % e(h['note']) if h.get('note') else '', ARROW, ARROW)
    return ('<section class="hero" data-ink="%s" style="--v:%s;--pi:%s;--pir:%s;--va:%s;--vb:%s">%s<div class="veil"></div><div class="veil2"></div>'
            '<div class="hero-in"><h1>%s</h1>%s%s%s</div>%s</section>') % (
        ink, _tri(v), ink, _tri(ink), max(.5, a), max(.16, round(a - .2, 2)), bg, e(h['title']),
        '<p class="sub">%s</p>' % e(h['text']) if h.get('text') else '', fig, hint + ('<div class="acts">%s</div>' % acts if acts else ''), ''), ink


def s_ticker(d, ink):
    logos = [x for x in d.get('logos') or [] if x]
    trust = [x for x in d.get('trust') or [] if x]
    if logos:
        cells = ''.join('<li>%s</li>' % (_img(x) if isinstance(x, dict) else '<img src="%s" alt="" loading="lazy">' % e(m(x))) for x in logos)
    elif trust:
        cells = ''.join('<li>%s</li>' % e(x) for x in trust)
    else:
        return ''
    return '<section class="lg" data-ink="%s"><div class="tkw fade"><ul class="tk" data-sp="60">%s</ul></div></section>' % (ink, cells)


def s_walk(d, ink, made, page_dark, first=None):
    st = d.get('steps') or {}
    items = [x for x in st.get('items') or [] if x.get('title')]
    if not items:
        return ''
    md = d.get('media') or {}
    known = {x.get('src'): x for k in ('phones', 'photos', 'screens') for x in md.get(k) or []}
    # the field behind a step's picture is the page's one motif again (the opening's landscape first, then its
    # neighbours of the same tone), held quiet — never a different saturated hue a step
    blur = _series(made, page_dark, first)
    arts = ''
    for i, x in enumerate(items):
        fig = ''
        if x.get('img'):
            o = dict(known.get(x['img']) or {}, src=x['img'])
            fld = ''
            if blur:
                bl = blur[i % len(blur)]
                fld = '<span class="fld" data-slot="walk-field-%d" data-kind="land" style="background-image:url(\'%s\')"></span>' % (i + 1, e(m(bl['src'])))
            fig = '<figure class="wk-f %s">%s%s</figure>' % (e(x.get('shape') or ''), fld, _img(o, '', i > 0))
        arts += '<article class="wk-s%s"><div class="wk-p">%s<h2>%s</h2>%s</div>%s</article>' % (
            ' on' if i == 0 else '', '<p class="ey">%s</p>' % e(x['k']) if x.get('k') else '', e(x['title']),
            '<p class="bd">%s</p>' % e(x['text']) if x.get('text') else '', fig)
    dots = '<ol class="dots" aria-hidden="true">%s</ol>' % ''.join('<li%s></li>' % (' class="on"' if i == 0 else '') for i in range(len(items))) if len(items) > 1 else ''
    return '<section class="wk" id="wk" data-ink="%s" style="--n:%d"><div class="wk-pin"><div class="wk-in">%s</div>%s</div></section>' % (ink, len(items), arts, dots)


def _pane(o, made, i, slot, page_dark=True, ground='#000000'):
    """a product picture standing whole on a made blurred field (the reference fills these panes with product film)"""
    blur = _series(made, page_dark, None)
    st = ''
    if blur:
        bl = blur[i % len(blur)]
        v = 'rgba(%s,.55)' % _tri(ground)
        st = ' data-slot="%s" data-kind="land" style="background-color:%s;background-image:linear-gradient(%s,%s),url(\'%s\')"' % (slot, e(ground), v, v, e(m(bl['src'])))
    if o.get('kind') == 'video':
        inner = '<video src="%s"%s%s muted loop playsinline preload="metadata" aria-label="%s"></video>' % (
            e(m(o['src'])), ' poster="%s"' % e(m(o['poster'])) if o.get('poster') else '', _wh(o), e(o.get('alt', '')))
    else:
        inner = _img(o)
    return '<div class="pane"%s>%s</div>' % (st, inner)


def s_bento(d, ink, pool, made, page_dark=True, ground='#000000'):
    f = d.get('features') or {}
    items = [x for x in f.get('items') or [] if x.get('t')][:3]
    if not items:
        return ''
    video = (d.get('media') or {}).get('video') or None
    cards = ''
    for i, x in enumerate(items):
        if i == 0:
            o = pool.take(_tall, lambda x: True)
        elif i == 2 and video and video.get('src'):
            o = dict(video, kind='video')
        else:
            o = pool.take(lambda x: not _tall(x), lambda x: True)
        cards += '<li class="bc bc%d"><article><div class="bc-t"><h3>%s</h3>%s</div>%s</article></li>' % (
            i + 1, e(x['t']), '<p>%s</p>' % e(x['d']) if x.get('d') else '', _pane(o, made, i + 1, 'tile-field-%d' % (i + 1), page_dark, ground) if o else '')
    head = '<div class="hd2 rv"><h2 class="h2">%s</h2></div>' % e(f['title']) if f.get('title') else ''
    return '<section class="bt" data-ink="%s">%s<div class="tkw bt-w"><ul class="bt-g k%d tk" data-ph="1" data-sp="70">%s</ul></div></section>' % (ink, head, len(items), cards)


def s_proof(d, band, on_band, acc):
    figs = [x for x in d.get('figures') or [] if x.get('v')]
    quotes = []
    for q in d.get('quotes') or []:
        q = q if isinstance(q, dict) else {'text': q}
        t = q.get('text') or q.get('quote') or q.get('q')
        if t:
            quotes.append((t, ' · '.join(str(v) for v in (q.get('name') or q.get('by'), q.get('role') or q.get('date')) if v)))
    if not figs and not quotes:
        return ''
    top = ''
    if figs:
        f0 = figs[0]
        rest = ''.join('<li><b>%s</b>%s</li>' % (e(x['v']), '<span>%s</span>' % e(x['l']) if x.get('l') else '') for x in figs[1:4])
        top = '<div class="pf-top">%s<p class="num" data-count>%s</p>%s</div>' % (
            '<div class="rv"><p class="ey">%s</p></div>' % e(f0['l']) if f0.get('l') else '', e(f0['v']), '<ul class="pf-r">%s</ul>' % rest if rest else '')
    rows = ''
    if quotes:
        n = 3 if len(quotes) >= 9 else (2 if len(quotes) >= 4 else 1)
        for r in range(n):
            part = quotes[r::n]
            rows += '<div class="tkw"><ul class="tk qr"%s data-sp="50">%s</ul></div>' % (
                ' data-rev="1"' if r % 2 else '', ''.join('<li><article class="qc"><p>%s</p>%s</article></li>' % (e(t), '<footer>%s</footer>' % e(by) if by else '') for t, by in part))
        rows = '<div class="pf-q">%s</div>' % rows
    return '<section class="pf%s" data-ink="%s" style="--bd:%s;--bdr:%s;--bi:%s;--bir:%s;--ba:%s">%s%s</section>' % (
        ' full' if quotes else '', on_band, band, _tri(band), on_band, _tri(on_band), acc, top, rows)


def s_results(d, ink, made, lo, hi, skip):
    f, s = d.get('features') or {}, d.get('statement') or {}
    items = [x for x in f.get('items') or [] if x.get('t')][3:]
    if not items:
        return ''
    land = [x for x in made.get('land') or [] if x.get('src') and x['src'] not in skip] or [x for x in made.get('land') or [] if x.get('src')]
    # squares first: the cards are near square
    land = [x for x in land if (x.get('tone') != 'light') == (_lum(lo) == _lum(ink) or _lum(ink) > .5)] or land
    land = sorted(land, key=lambda x: abs((x.get('w') or 1) / (x.get('h') or 1) - 1.1))
    cards = ''
    for i, x in enumerate(items):
        if land:
            p = land[i % len(land)]
            v, pin, a = _over(p, lo, hi, 5.5)
            st = ' style="--v:%s;--pi:%s;--pir:%s;--va:%s"' % (_tri(v), pin, _tri(pin), max(.2, a))
            bg = '<img class="bg" src="%s" alt=""%s loading="lazy" decoding="async" data-slot="result-card-%d" data-kind="land"><span class="veil"></span>' % (e(m(p['src'])), _wh(p), i + 1)
        else:
            st, bg = ' class="plain"', ''
        cards += '<li class="rc"%s>%s<h3>%s</h3>%s</li>' % (st, bg, e(x['t']), '<div class="chip"><p>%s</p></div>' % e(x['d']) if x.get('d') else '')
    head = '<div class="hd2"><h2 class="h2">%s</h2></div>' % e(s['title']) if s.get('title') else ''
    return '<section class="rs" id="rs" data-ink="%s"><div class="rs-pin">%s<div class="tkw rs-v"><ul class="rs-t tk" data-ph="1" data-sp="75">%s</ul></div></div></section>' % (ink, head, cards)


def s_plans(d, ink):
    """The reference has no pricing page (its /pricing answers 404). Built from its parts: the tiles (40 round, the
    marked one in the second colour, the other ink 8 %), the tile head, the band's figure for the price, the question
    rows (16 round, ink 6 %) for what a plan holds, the bar's call and tray for the buttons."""
    p = d.get('plans') or {}
    items = [x for x in p.get('items') or [] if x.get('name')]
    if not items:
        return ''
    cards = ''
    for x in items:
        price = ''
        if x.get('price') or x.get('per'):
            price = '<p class="pp">%s%s</p>' % ('<b>%s</b>' % e(x['price']) if x.get('price') else '', '<span>%s</span>' % e(x['per']) if x.get('per') else '')
        rows = ''.join('<li>%s</li>' % e(r) for r in x.get('rows') or [] if r)
        c = x.get('cta') or {}
        btn = ''
        if c.get('t'):
            btn = '<a class="%s" href="%s">%s</a>' % ('cta' if x.get('marked') else 'pbtn', e(c.get('h') or '#'), e(c['t']))
        cards += '<li class="pc%s"><h3>%s</h3>%s%s%s%s</li>' % (
            ' mk' if x.get('marked') else '', e(x['name']), price, '<p class="pln">%s</p>' % e(x['line']) if x.get('line') else '',
            '<ul class="prow">%s</ul>' % rows if rows else '', btn)
    head = ''
    if p.get('title') or p.get('text'):
        head = '<div class="hd2">%s%s</div>' % ('<h2 class="h2">%s</h2>' % e(p['title']) if p.get('title') else '', '<p class="lead">%s</p>' % e(p['text']) if p.get('text') else '')
    return '<section class="pl" data-ink="%s">%s<ul class="pl-g" style="--k:%d">%s</ul>%s</section>' % (
        ink, head, min(len(items), 3), cards, '<p class="pnote">%s</p>' % e(p['note']) if p.get('note') else '')


def s_faq(d, ink):
    """The reference keeps its questions in a dialog opened from the foot: a 40-round panel 720 wide, a 48 px head and
    native disclosure rows. Here the same column and rows stand in the page, before the close."""
    f = d.get('faq') or {}
    items = [x for x in f.get('items') or [] if x.get('q')]
    if not items:
        return ''
    rows = ''.join('<li><details%s><summary><span class="qn">%02d</span><span class="qq">%s</span><span class="qx" aria-hidden="true"></span></summary>%s</details></li>' % (
        ' open' if i == 0 else '', i + 1, e(x['q']), '<p>%s</p>' % e(x['a']) if x.get('a') else '') for i, x in enumerate(items))
    return '<section class="fq" data-ink="%s"><div class="fq-in">%s<ul>%s</ul></div></section>' % (ink, '<h2>%s</h2>' % e(f['title']) if f.get('title') else '', rows)


def s_close(d, pic, lo, hi, ground, ink0):
    c, h, b, f = d.get('close') or {}, d.get('hero') or {}, d.get('brand') or {}, d.get('foot') or {}
    if pic:
        v, ink, a = _over(pic, lo, hi)
        bg = '<img class="bg" src="%s" alt=""%s loading="lazy" decoding="async" data-slot="close-backdrop" data-kind="land"><div class="veil"></div>' % (e(m(pic['src'])), _wh(pic))
    else:
        v, ink, a, bg = ground, ink0, 0, ''
    top = ''
    if c.get('title'):
        acts = _glass(c.get('cta')) + (_glass(h.get('secondary')) if (h.get('secondary') or {}).get('h') != (c.get('cta') or {}).get('h') else '')
        top = '<div class="cl-top"><h2 class="h2">%s</h2>%s%s</div>' % (e(c['title']), '<p class="small">%s</p>' % e(c['text']) if c.get('text') else '', '<div class="acts">%s</div>' % acts if acts else '')
    nav = [n for n in d.get('nav') or [] if n.get('t')]
    seen = {n.get('h') for n in nav}
    links = []
    for x in d.get('links') or []:
        if x.get('t') and x.get('h') not in seen:
            seen.add(x.get('h'))
            links.append(x)
    acct = []
    for x in [d.get('signin'), d.get('cta')] + list(f.get('links') or []):
        if x and x.get('t') and x.get('h') not in seen:
            seen.add(x.get('h'))
            acct.append(x)
    col = lambda xs: '<ul>%s</ul>' % ''.join('<li><a href="%s">%s</a></li>' % (e(x.get('h') or '#'), e(x['t'])) for x in xs) if xs else ''
    cols = '<div class="ft-c"><div class="ft-b">%s</div>%s%s%s</div>' % (_logo(b), col(nav), col(links), col(acct))
    low = ''
    if f.get('legal') or f.get('text'):
        low = '<hr><div class="ft-l">%s%s</div>' % ('<small>%s</small>' % e(f['legal']) if f.get('legal') else '', '<p>%s</p>' % e(f['text']) if f.get('text') else '')
    return ('<section class="cl" data-ink="%s" style="--v:%s;--pi:%s;--pir:%s;--va:%s">%s<div class="cl-in">%s<div class="ft-w"><footer class="ft">%s%s</footer></div></div></section>') % (
        ink, _tri(v), ink, _tri(ink), min(.8, max(.3, round(a + .2, 2))), bg, top, cols, low)


CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}html{background:var(--g);-webkit-text-size-adjust:100%}
body{font:400 16px/1.5 'DM Sans',system-ui,-apple-system,'Segoe UI',sans-serif;color:var(--i);background:var(--g);-webkit-font-smoothing:antialiased;overflow-x:clip}
a{color:inherit;text-decoration:none}img,video{display:block;max-width:100%;height:auto}ul,ol{list-style:none}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
/* labels 12/700 +4px caps in the accent; section heads 56/1 600 -.06em centred, 440 wide */
.ey{font-weight:700;font-size:12px;line-height:1.2;letter-spacing:4px;text-transform:uppercase;color:var(--a)}
.h2{font-weight:600;font-size:56px;line-height:1;letter-spacing:-.06em;text-wrap:balance}
.hd2{display:flex;flex-direction:column;align-items:center;gap:16px;text-align:center;max-width:min(620px,100% - 32px);margin:0 auto}
html.js .rv{opacity:.001;transform:translateY(-20px);transition:opacity 1.5s cubic-bezier(.16,1,.3,1),transform 1.5s cubic-bezier(.16,1,.3,1)}html.js .rv.in{opacity:1;transform:none}
/* bar: fixed, clear, 16 all round; a 12-radius tray of links, a hairline, the call on a two-colour slope */
.bar{position:fixed;inset:0 0 auto;z-index:50;height:73px;padding:16px;display:flex;align-items:center;justify-content:space-between;gap:12px;color:var(--nv);transition:color .25s ease}
.logo{display:flex;align-items:center;gap:6px;font-weight:600;font-size:16px;line-height:1.2;min-width:0}.logo{flex:none}.logo img{flex:none;height:32px;width:auto;border-radius:7px}.logo img.wm{height:24px;border-radius:0}
.bar-r{display:flex;align-items:center;gap:0;min-width:0}
.seg{display:flex;align-items:center;border-radius:12px;background:color-mix(in srgb,currentColor 10%,transparent)}
.seg a{display:flex;align-items:center;height:41px;padding:0 16px;border-radius:12px;font-weight:500;font-size:14px;line-height:18px;letter-spacing:-.03em;white-space:nowrap}
.seg a.on{background:var(--nv);color:var(--nvt,var(--g));transition:background-color .25s ease,color .25s ease}.seg a.on:focus-visible{outline-color:var(--nv)}
.seg.small{display:none}
.logo,.seg{transition:background-color .25s ease}.moved .bar .logo{background:color-mix(in srgb,var(--nvt,var(--g)) 88%,transparent);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border-radius:12px;padding:4px 10px 4px 4px;margin:-4px -10px -4px -4px}.moved .seg{background:color-mix(in srgb,var(--nvt,var(--g)) 88%,transparent);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
.sep{width:1px;height:20px;margin:0 12px;background:color-mix(in srgb,currentColor 10%,transparent)}
.cta{display:flex;align-items:center;justify-content:center;height:40px;padding:0 18px;border-radius:12px;background:linear-gradient(100deg,var(--b1) 0%,var(--b2) 100%);color:var(--bt);font-weight:500;font-size:14px;line-height:18px;letter-spacing:-.03em;white-space:nowrap}
.cta:focus-visible{outline-color:var(--nv)}
.roll{display:block;height:18px;overflow:hidden}.roll span,.roll::after{display:block;transition:transform .3s cubic-bezier(.4,0,.2,1)}.roll::after{content:attr(data-t)}.cta:hover .roll span,.cta:hover .roll::after{transform:translateY(-100%)}
/* opening: one screen; the picture fills it under a veil that is half at the top, thin in the middle and whole at the foot */
.hero{position:relative;height:100vh;min-height:620px;overflow:hidden;color:var(--pi);background:rgb(var(--v))}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hero .veil{position:absolute;inset:0;background:linear-gradient(rgba(var(--v),var(--va)) 0%,rgba(var(--v),var(--vb)) 50%,rgb(var(--v)) 100%)}
.hero .veil2{position:absolute;inset:0 0 auto;height:380px;background:radial-gradient(60% 100% at 50% 0,rgba(var(--v),.55) 0%,rgba(var(--v),0) 100%)}
.hero-in{position:relative;height:100%;display:flex;flex-direction:column;align-items:center;padding:80px 24px 40px;text-align:center}
h1{font-weight:600;font-size:64px;line-height:1;letter-spacing:-.06em;max-width:18em;text-wrap:balance}
.sub{margin-top:16px;max-width:560px;font-weight:500;font-size:24px;line-height:1.2;letter-spacing:-.06em;text-wrap:balance}
.shot{flex:1 1 0;min-height:0;margin:28px 0 20px;display:flex;justify-content:center;align-items:center;max-width:100%}
.shot img{max-height:100%;max-width:100%;width:auto;height:auto;border-radius:10px;box-shadow:0 0 0 1px rgba(var(--pir),.14),0 30px 80px rgba(0,0,0,.35)}.shot.tall img{border-radius:22px}
.acts{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.glass{display:flex;align-items:center;justify-content:center;min-height:54px;padding:10px 24px;border-radius:100px;background:rgba(var(--pir),.24);box-shadow:inset 0 0 8px rgba(var(--pir),.25);-webkit-backdrop-filter:blur(5px);backdrop-filter:blur(5px);font-weight:500;font-size:16px;line-height:1.2;letter-spacing:-.05em;color:var(--pi);transition:background-color .15s cubic-bezier(.4,0,.2,1)}
.glass:hover{background:rgba(var(--pir),.36)}
.hint{display:flex;flex-direction:column;align-items:center;gap:12px;margin-bottom:22px;font-weight:500;font-size:16px;line-height:1.2}
.disc{position:relative;width:24px;height:24px;border-radius:99px;overflow:hidden;background:rgba(var(--pir),.12);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
.loop{position:absolute;left:0;top:0;display:flex;flex-direction:column;animation:arrow .64s cubic-bezier(.44,0,.56,1) infinite}.loop svg{display:block;width:24px;height:24px;padding:2px}
@keyframes arrow{from{transform:translateY(-24px)}to{transform:none}}
/* running line: 64 above and below, items at 70 %, the ends fading over a tenth of the width */
.lg{padding:64px 0}.tkw{overflow-x:auto;scrollbar-width:none}.tkw::-webkit-scrollbar{display:none}.tkw.run{overflow:hidden}
.fade{-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 10%,#000 90%,transparent 100%);mask-image:linear-gradient(90deg,transparent 0,#000 10%,#000 90%,transparent 100%)}
.tk{display:flex;align-items:center;width:max-content}
.lg .tk{gap:56px;padding-right:56px;font-weight:500;font-size:16px;line-height:23px;letter-spacing:-.02em;white-space:nowrap}.lg li{opacity:.7}.lg img{height:23px;width:auto}
/* THE WALK. Plain: each step is its words beside its picture, the picture whole on a soft field. */
.wk{overflow:clip}.wk-in{width:min(1200px,100% - 48px);margin:0 auto}
.wk-s{display:grid;grid-template-columns:51fr 49fr;align-items:center;min-height:760px}
.wk-p{padding-left:24px;display:flex;flex-direction:column;align-items:flex-start}
.wk-p .ey{margin-bottom:16px}.wk-p h2{font-weight:700;font-size:48px;line-height:1.1;letter-spacing:-.05em;max-width:420px;text-wrap:balance}
.bd{margin-top:24px;max-width:360px;font-weight:500;font-size:18px;line-height:22px;letter-spacing:-.06em}
.wk-f{position:relative;display:grid;place-items:center;min-width:0;height:100%}
.fld{position:absolute;top:0;bottom:0;left:-14%;right:calc(-1*max(24px,(100vw - 1200px)/2));background-size:cover;background-position:center;opacity:.5;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 48%),linear-gradient(transparent 0,#000 16%,#000 84%,transparent 100%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,transparent 0,#000 48%),linear-gradient(transparent 0,#000 16%,#000 84%,transparent 100%);mask-composite:intersect}
.wk-f img{position:relative;max-height:min(70vh,631px);max-width:100%;width:auto;border-radius:8px;box-shadow:0 0 0 1px color-mix(in srgb,var(--i) 14%,transparent)}.wk-f.phone img{border-radius:22px}
.dots{display:none}
/* held: the section is one screen pinned for 1350 a step (640 on a phone); words, picture and field change together in .48s */
.wk.pin{height:calc(100vh + (var(--n) + .47)*1350px)}.pin .wk-pin{position:sticky;top:0;height:100vh;overflow:clip}.pin .wk-in{position:relative;height:100%}
.pin .wk-s{position:absolute;inset:0;min-height:0;opacity:0;visibility:hidden;transition:opacity .48s cubic-bezier(.44,0,.56,1),visibility 0s .48s}.pin .wk-s.on{opacity:1;visibility:visible;transition-delay:0s}
@media (min-width:901px){.pin .wk-p{min-height:280px}}
.pin .dots{position:absolute;right:16px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:16px;padding:16px 14px;border-radius:16px;background:color-mix(in srgb,var(--i) 8%,transparent)}
.dots li{width:12px;height:12px;border-radius:99px;background:color-mix(in srgb,var(--i) 16%,transparent);transition:background-color .15s cubic-bezier(.4,0,.2,1)}.dots li.on{background:var(--a)}
/* tiles: head 80 from the top, then a tall tile (389) beside two wide ones (795), 16 apart, 40 round, 8 inside, panes 32 round */
.bt{padding:80px 0 160px;overflow:hidden}.bt .hd2{margin-bottom:80px}
.bt-g{display:grid;grid-template-columns:389fr 795fr;grid-template-rows:400px 400px;gap:16px;width:min(1200px,100% - 48px);margin:0 auto;align-items:stretch}
.bc{min-width:0;min-height:0}.bc1{grid-row:1/3}.bt-g.k1{grid-template-columns:1fr;grid-template-rows:auto}.bt-g.k1 .bc1{grid-row:auto;max-width:389px;justify-self:center}.bt-g.k2{grid-template-rows:816px}.bt-g.k2 .bc2{align-self:center}
.bc article{height:100%;display:flex;gap:10px;padding:8px;border-radius:40px;overflow:hidden}
.bc1 article{flex-direction:column;gap:16px;background:var(--i);color:var(--g)}.bc2 article{flex-direction:row-reverse;background:var(--c2);color:var(--c2t);min-height:400px}.bc3 article{background:color-mix(in srgb,var(--i) 8%,var(--g));color:var(--i)}
.bc-t{flex:1 1 0;min-width:0;padding:32px;display:flex;flex-direction:column;justify-content:flex-end;gap:16px}.bc1 .bc-t{flex:none;padding:32px 32px 8px;justify-content:flex-start}
.bc h3{font-weight:600;font-size:32px;line-height:1;letter-spacing:-.05em;text-wrap:balance}.bc-t p{font-weight:500;font-size:16px;line-height:20px;letter-spacing:-.03em;opacity:.9}
.pane{flex:1 1 0;min-width:0;min-height:0;display:grid;grid-template:minmax(0,1fr)/minmax(0,1fr);place-items:center;padding:24px;border-radius:32px;overflow:hidden;background-size:cover;background-position:center;background-color:color-mix(in srgb,currentColor 8%,transparent)}
.pane img,.pane video{max-width:100%;max-height:100%;width:auto;height:auto;border-radius:10px;box-shadow:0 10px 40px rgba(0,0,0,.28)}
/* the turned band: one screen in the other pole, a 100 px figure counting up, the smaller figures on a hairline row */
.pfw{position:relative}
.pf{position:sticky;top:0;z-index:0;background:var(--bd);color:var(--bi);padding:160px 0;overflow:hidden}.pf.full{height:100vh;min-height:760px;padding-bottom:0}
.pf-top{display:flex;flex-direction:column;align-items:center;gap:16px;padding:0 16px;text-align:center}.pf .ey{color:var(--ba);max-width:60ch}
.num{font-weight:600;font-size:100px;line-height:1;letter-spacing:-.04em;font-variant-numeric:tabular-nums}
.pf-r{display:flex;justify-content:center;gap:0;margin-top:24px;flex-wrap:wrap}.pf-r li{display:flex;flex-direction:column;align-items:center;gap:2px;padding:0 40px;max-width:300px}.pf-r li+li{border-left:1px solid rgba(var(--bir),.16)}
.pf-r b{font-weight:600;font-size:20px;line-height:1.2;letter-spacing:-.03em}.pf-r span{font-weight:500;font-size:12px;line-height:1.3;opacity:.78}
.pf-q{display:flex;flex-direction:column;gap:16px;margin-top:80px}.qr{gap:16px;padding-right:16px;align-items:stretch}
.qc{width:400px;height:240px;display:flex;flex-direction:column;justify-content:space-between;padding:30px 29px;border-radius:30px;box-shadow:inset 0 0 0 1px rgba(var(--bir),.1)}.qc p{font-weight:500;font-size:18px;line-height:22px;letter-spacing:-.06em;opacity:.85}.qc footer{font-size:16px;line-height:19px;opacity:.9}
.pf.full::after{content:"";position:absolute;inset:auto 0 0;height:320px;background:linear-gradient(rgba(var(--bdr),0),var(--bd));pointer-events:none}
.pf.full+.rs{margin-top:100vh}
/* outcomes: an 80-round slab that slides up over the band and holds while its cards run sideways with the scroll */
.rs{position:relative;z-index:1;background:var(--g);border-radius:80px 80px 0 0}
.rs-pin{display:flex;flex-direction:column;justify-content:center;gap:80px;padding:120px 0;border-radius:80px 80px 0 0;background:var(--g)}
.rs-t{gap:16px;padding:0 max(24px,(100% - 1200px)/2);align-items:stretch;margin:0 auto}
.rc{position:relative;flex:none;width:440px;height:400px;padding:40px;border-radius:40px;overflow:hidden;display:flex;flex-direction:column;justify-content:space-between;gap:16px;color:var(--pi);background:rgb(var(--v))}
.rc.plain{--v:0,0,0;background:color-mix(in srgb,var(--i) 8%,var(--g));color:var(--i);--pi:var(--i);--pir:var(--ir)}
.rc .veil{position:absolute;inset:0;background:linear-gradient(rgba(var(--v),.5) 0%,rgba(var(--v),0) 100%),rgba(var(--v),var(--va))}
.rc h3{position:relative;font-weight:600;font-size:32px;line-height:1;letter-spacing:-.05em;text-wrap:balance}
.chip{position:relative;padding:20px 24px;border-radius:24px;background:rgba(var(--v),.42);box-shadow:inset 0 0 0 2px rgba(var(--pir),.1);-webkit-backdrop-filter:blur(5px);backdrop-filter:blur(5px)}
.chip p{font-weight:500;font-size:16px;line-height:20px;letter-spacing:-.03em}
html.js .chip{opacity:0;transform:translateY(80px);transition:opacity .8s cubic-bezier(.2,.9,.3,1),transform .8s cubic-bezier(.2,.9,.3,1)}html.js .chip.in{opacity:1;transform:none}
.rs.pin .rs-pin{position:sticky;top:0;height:100vh;padding:80px 0 40px;overflow:clip}.rs.pin .rs-v{overflow:visible}.rs.pin .rs-t{margin:0;padding:0;will-change:transform}
/* plans: tiles again — 40 round, 40 inside, 16 apart; the marked plan in the second colour, the rest ink 8 %; price in the band's figure */
.pl{padding:160px 0 0}.pl .hd2{margin-bottom:80px}.lead{max-width:560px;font-weight:500;font-size:18px;line-height:22px;letter-spacing:-.06em;text-wrap:balance}
.pl-g{display:grid;grid-template-columns:repeat(var(--k),minmax(0,1fr));gap:16px;width:min(1200px,100% - 48px);margin:0 auto;align-items:stretch}.pl-g[style*="--k:1"]{max-width:592px}
.pc{display:flex;flex-direction:column;align-items:flex-start;gap:16px;padding:40px;border-radius:40px;background:color-mix(in srgb,var(--i) 8%,var(--g));color:var(--i)}.pc.mk{background:var(--c2);color:var(--c2t)}
.pc h3{font-weight:600;font-size:32px;line-height:1;letter-spacing:-.05em}.pp{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px}.pp b{font-weight:600;font-size:56px;line-height:1;letter-spacing:-.04em}.pp span{font-weight:500;font-size:14px;line-height:18px;letter-spacing:-.03em}
.pln{font-weight:500;font-size:18px;line-height:22px;letter-spacing:-.06em}.prow{align-self:stretch;display:flex;flex-direction:column;gap:8px;margin-top:8px}.prow li{padding:14px 20px;border-radius:16px;background:color-mix(in srgb,currentColor 6%,transparent);font-weight:500;font-size:16px;line-height:1.2}
.pc .cta,.pbtn{margin-top:auto}.pc .cta{margin-top:auto}.pc>:nth-last-child(2){margin-bottom:16px}.pbtn{display:flex;align-items:center;height:41px;padding:0 16px;border-radius:12px;background:color-mix(in srgb,currentColor 10%,transparent);font-weight:500;font-size:14px;line-height:18px;letter-spacing:-.03em;transition:background-color .15s cubic-bezier(.4,0,.2,1)}.pbtn:hover{background:color-mix(in srgb,currentColor 18%,transparent)}.pc .cta:focus-visible{outline-color:currentColor}
.pnote{width:min(720px,100% - 48px);margin:40px auto 0;text-align:center;font-weight:500;font-size:14px;line-height:18px;letter-spacing:-.03em;color:var(--mu2)}
/* questions: the reference's dialog column in the page — 656 wide, head 48/1.1 bold, rows 16 round on ink 6 %, 20x24 inside, 12 apart; the plus turns in .15s */
.fq{padding:160px 0 0}.fq-in{width:min(656px,100% - 48px);margin:0 auto;display:flex;flex-direction:column;gap:24px}.fq h2{font-weight:700;font-size:48px;line-height:1.1;letter-spacing:-.05em;text-align:center;text-wrap:balance;margin-bottom:8px}
.fq ul{display:flex;flex-direction:column;gap:12px}.fq details{padding:20px 24px;border-radius:16px;background:color-mix(in srgb,var(--i) 6%,transparent)}.fq summary{display:flex;align-items:flex-start;gap:16px;cursor:pointer;list-style:none;border-radius:8px}.fq summary::-webkit-details-marker{display:none}
.qn{flex:none;padding-top:3px;font-weight:500;font-size:14px;line-height:18px;letter-spacing:-.03em;color:var(--mu)}.qq{flex:1;font-weight:500;font-size:18px;line-height:22px;letter-spacing:-.06em}
.qx{flex:none;position:relative;width:13px;height:24px;transition:transform .15s cubic-bezier(.4,0,.2,1)}.qx::before,.qx::after{content:"";position:absolute;left:50%;top:50%;width:13px;height:1.5px;margin:-.75px 0 0 -6.5px;background:currentColor}.qx::after{transform:rotate(90deg)}details[open] .qx{transform:rotate(45deg)}
.fq details p{margin-top:16px;font-weight:500;font-size:16px;line-height:1.2;color:var(--mu2)}
.pl+.cl,.fq+.cl{margin-top:160px}
/* the close: 40-round top, a picture under a veil, head 160 from the top, the foot a frosted 32-round card 16 from the edges */
.cl{position:relative;z-index:1;border-radius:40px 40px 0 0;overflow:hidden;color:var(--pi);background:rgb(var(--v))}.cl .veil{position:absolute;inset:0;background:rgba(var(--v),var(--va))}
.cl-in{position:relative;display:flex;flex-direction:column;gap:40px;padding-top:160px}
.small{max-width:560px;font-weight:500;font-size:16px;line-height:1.2;margin-top:-28px}
.cl-top{display:flex;flex-direction:column;align-items:center;gap:44px;padding:0 16px;text-align:center}.cl-top .h2{max-width:620px}
.ft-w{padding:16px}.ft{display:flex;flex-direction:column;gap:24px;padding:40px;border-radius:32px;background:rgba(var(--pir),.12);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px)}
.ft-c{display:grid;grid-template-columns:repeat(4,minmax(0,304px));min-height:160px}.ft-c ul{display:flex;flex-direction:column}
.ft-c ul a{display:flex;align-items:center;min-height:32px;font-weight:500;font-size:16px;line-height:1.2;transition:opacity .2s cubic-bezier(.4,0,.2,1)}.ft-c ul a:hover{opacity:.5}
.ft hr{border:0;border-top:1px solid rgba(var(--pir),.16)}
.ft-l{display:flex;justify-content:space-between;gap:12px 40px;flex-wrap:wrap;font-weight:500;font-size:14px;line-height:18px;letter-spacing:-.03em}.ft-l small{font-size:14px;white-space:nowrap}.ft-l p{max-width:72ch}
@media (max-width:1100px){.seg.wide{display:none}.sep{display:none}}
/* PHONE (measured at 390): 16 at the sides, the first screen 760 high, display 48, heads 36, the walk with its picture above its words, tiles and cards as running rows */
@media (max-width:900px){
.bar .wide{display:none}.seg.small{display:flex;min-width:0}.seg.small a{flex:none}.seg.small a.on{flex:0 1 auto;min-width:0}.seg.small a{font-size:12px;line-height:18px;letter-spacing:-.035em;padding:0 10px;max-width:42vw;overflow:hidden;text-overflow:ellipsis;display:block;line-height:41px}.logo span{display:none}.logo img.wm{height:20px}
.h2{font-size:36px}.hero{height:min(100svh,760px);min-height:560px}.hero-in{padding:80px 16px 64px}h1{font-size:48px}.sub{max-width:302px;font-size:18px;line-height:1.1}
.shot{margin:24px 0 28px}.acts{width:100%;flex-wrap:nowrap}.glass{flex:1 1 0;min-width:0;min-height:49px;padding:10px 12px}.hint{margin-bottom:18px}
.lg{padding:40px 0}
.wk-in{width:auto;margin:0 16px}.wk-s{grid-template-columns:1fr;grid-template-rows:auto auto;min-height:0;padding:40px 0}.wk-f{order:-1;padding:24px 0 36px}.wk-p{padding:0}.wk-p .ey{margin-bottom:8px}.wk-p h2{font-size:36px;max-width:none}.bd{margin-top:12px;max-width:none;font-size:16px;line-height:20px}
.fld{left:-16px;right:-16px;top:-72px;-webkit-mask-image:linear-gradient(#000 0,#000 55%,transparent 100%);mask-image:linear-gradient(#000 0,#000 55%,transparent 100%);-webkit-mask-composite:source-over;mask-composite:add}.wk-f img{max-height:min(52svh,400px)}
.wk.pin{height:calc(min(100svh,760px) + (var(--n) + .47)*640px)}.pin .wk-pin{height:min(100svh,760px)}.pin .wk-s{grid-template-rows:minmax(0,1fr) auto;padding:72px 0 47px}.pin .wk-f{padding:0 0 28px}.pin .wk-f img{max-height:calc(min(100svh,760px) - 360px)}.pin .wk-p{min-height:174px}
.pin .dots{right:16px;top:44%}
.bt{padding:80px 0 160px}.bt .hd2{margin-bottom:56px}.bt-g,.bt-g.k1,.bt-g.k2{display:flex;width:max-content;gap:16px;padding:0 16px;margin:0;align-items:stretch}.run .bt-g{padding:0 16px 0 0}
.bc,.bt-g.k1 .bc1{width:358px;max-width:none}.bc article,.bc2 article{flex-direction:column;gap:16px;min-height:475px}.bc-t,.bc1 .bc-t{flex:none;padding:32px 32px 8px;justify-content:flex-start;gap:12px}.bc h3{font-size:24px}.bc-t p{font-size:14px;line-height:18px}.pane{flex:1 1 auto;height:325px;min-height:325px}
.pfw .pf{position:relative;border-radius:40px;padding:64px 0}.pf.full{height:auto;min-height:0;padding-bottom:0}.pf.full+.rs{margin-top:0}.num{font-size:48px}.pf-r{margin-top:12px;flex-direction:column;align-items:center;gap:14px}.pf-r li{padding:0 16px}.pf-r li+li{border-left:0}.pf-r b{font-size:16px}
.pf-q{margin-top:56px;padding-bottom:40px}.qc{width:320px;height:200px;padding:16px}.qc p{font-size:16px;line-height:1.2}
.rs,.rs-pin{border-radius:56px 56px 0 0}.rs-pin{padding:120px 0 80px;gap:40px}.rs .hd2{padding:0 8px}.rs-t{padding:0 16px;margin:0}.run .rs-t{padding:0 16px 0 0}.rc{width:320px;height:auto;min-height:320px;padding:24px;border-radius:24px}.rc h3{font-size:24px}.chip{padding:14px 16px;border-radius:16px}.chip p{font-size:14px;line-height:18px}
.pl,.fq{padding-top:120px}.pl .hd2{margin-bottom:40px}.lead{font-size:16px;line-height:20px}.pl-g{grid-template-columns:1fr;width:auto;margin:0 16px}.pc{padding:32px 24px;border-radius:32px}.pc h3{font-size:24px}.pp b{font-size:48px}.pln{font-size:16px;line-height:20px}.prow li{padding:12px 16px}
.fq-in{width:auto;margin:0 16px}.fq h2{font-size:28px;line-height:1.2}.qq{font-size:16px;line-height:1.2}.qn{font-size:12px;padding-top:1px}.pl+.cl,.fq+.cl{margin-top:120px}
.cl-in{padding-top:176px}.cl-top{gap:32px}.small{margin-top:-18px}.cl-top .h2{font-size:32px}.ft{padding:24px;gap:32px}.ft-c{grid-template-columns:1fr 1fr;gap:40px 40px;min-height:0}.ft-b{grid-column:1/-1}.ft-b .logo span{display:inline}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}html.js .rv,html.js .chip{opacity:1;transform:none}html{scroll-behavior:auto}}
"""

JS = r"""
(() => { try { const D = document, R = D.documentElement, calm = matchMedia('(prefers-reduced-motion:reduce)').matches, $ = (s, r) => (r || D).querySelector(s), $$ = (s, r) => [...(r || D).querySelectorAll(s)], phone = () => innerWidth <= 900, cl = (v, a, b) => Math.max(a, Math.min(b, v));
/* the bar takes the ink of whatever lies under it; the opening's arrow goes once the page has moved */
const bar = $('#bar'), inks = $$('[data-ink]'), G = getComputedStyle(R).getPropertyValue('--g').trim(), I = getComputedStyle(R).getPropertyValue('--i').trim();
const wm = bar && $('.logo img.wm', bar), lum = h => { const n = parseInt(h.replace('#', ''), 16); return (.2126 * (n >> 16 & 255) + .7152 * (n >> 8 & 255) + .0722 * (n & 255)) / 255; };
const barInk = () => { let c = null; for (const s of inks) { const r = s.getBoundingClientRect(); if (r.top <= 36 && r.bottom > 36) c = s.dataset.ink; } if (c && bar) { bar.style.setProperty('--nv', c); bar.style.setProperty('--nvt', c.toLowerCase() === G.toLowerCase() ? I : G); if (wm) wm.style.filter = c.toLowerCase() === I.toLowerCase() ? '' : (lum(c) > .4 ? 'brightness(0) invert(1)' : 'brightness(0)'); } R.classList.toggle('moved', scrollY > 40); };
/* heads drop in 20 px as they enter; the cards' lower panels rise 80 px when the card is in view */
if (!calm && 'IntersectionObserver' in window) { const io = new IntersectionObserver(es => es.forEach(x => { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } }), { rootMargin: '0px 0px -8% 0px' }); $$('.rv').forEach(x => io.observe(x)); const io2 = new IntersectionObserver(es => es.forEach(x => { if (x.isIntersecting) { x.target.querySelector('.chip').classList.add('in'); io2.unobserve(x.target); } }), { threshold: .55 }); $$('.rc').forEach(x => x.querySelector('.chip') && io2.observe(x)); } else $$('.rv,.chip').forEach(x => x.classList.add('in'));
/* the walk: one screen held; the step follows the scroll — 1350 px a step, 640 on a phone */
const wk = $('#wk'), steps = wk ? $$('.wk-s', wk) : [], dots = wk ? $$('.dots li', wk) : []; let cur = 0; const pinWalk = wk && !calm && steps.length > 1; if (pinWalk) wk.classList.add('pin');
const walk = () => { if (!pinWalk) return; const y = -wk.getBoundingClientRect().top, k = cl(Math.floor((y - 50) / (phone() ? 640 : 1350)), 0, steps.length - 1); if (k === cur) return; cur = k; steps.forEach((s, i) => s.classList.toggle('on', i === k)); dots.forEach((s, i) => s.classList.toggle('on', i === k)); };
/* the cards: while the slab is held the row runs from its first card at the column edge to its last 80 from the right, .82 px of scroll to the px; the band behind fades as it goes */
const rs = $('#rs'), tr = rs && $('.rs-t', rs), pf = $('.pf'); let travel = 0, x0 = 0;
const layCards = () => { if (!rs) return; rs.classList.remove('pin'); rs.style.height = ''; tr.style.transform = ''; travel = 0; if (calm || phone()) return; const vw = R.clientWidth, n = tr.children.length, w = n * 440 + (n - 1) * 16; x0 = Math.max(24, (vw - 1200) / 2); const t = x0 + w - (vw - 80); if (t < 8) return; travel = t; rs.classList.add('pin'); rs.style.height = Math.round(innerHeight + t * .82) + 'px'; };
const cards = () => { if (!rs) return; const top = rs.getBoundingClientRect().top; if (travel) { const p = cl(-top / (rs.offsetHeight - innerHeight), 0, 1); tr.style.transform = 'translate3d(' + (x0 - p * travel).toFixed(1) + 'px,0,0)'; if (pf) pf.style.opacity = (1 - p).toFixed(3); } else if (pf) pf.style.opacity = ''; };
/* the large figure counts up once, 1.6 s, fast then slow */
const num = $('[data-count]'); if (num && !calm && 'IntersectionObserver' in window) { const m = num.textContent.match(/^(\D*)(\d[\d,]*(?:\.\d+)?)(\D*)$/); if (m) { const dec = (m[2].split('.')[1] || '').length, comma = m[2].includes(','), end = parseFloat(m[2].replace(/,/g, '')), fmt = v => { let s = v.toFixed(dec); if (comma) { const a = s.split('.'); a[0] = a[0].replace(/\B(?=(\d{3})+$)/g, ','); s = a.join('.'); } return m[1] + s + m[3]; }; const full = num.textContent; num.setAttribute('aria-label', full);
  new IntersectionObserver((es, o) => { if (!es[0].isIntersecting) return; o.disconnect(); const t0 = performance.now(); const f = now => { const t = cl((now - t0) / 1600, 0, 1); num.textContent = t < 1 ? fmt(end * (1 - Math.pow(2, -10 * t))) : full; if (t < 1) requestAnimationFrame(f); }; requestAnimationFrame(f); }, { threshold: .6 }).observe(num); } }
/* running rows: the list is repeated and moved by its own width, steadily; a row marked for phones runs only there */
const runs = () => $$('.tk').forEach(ul => { const w = ul.parentElement; (ul._a && ul._a.cancel()); $$('.dup', ul).forEach(x => x.remove()); w.classList.remove('run'); if (calm || (ul.dataset.ph && !phone())) return; const one = ul.scrollWidth; if (!one) return; const kids = [...ul.children], k = Math.ceil(w.clientWidth / one) + 1; w.classList.add('run'); const one2 = ul.scrollWidth; for (let i = 0; i < k; i++) kids.forEach(c => { const n = c.cloneNode(true); n.classList.add('dup'); n.setAttribute('aria-hidden', 'true'); $$('a,video', n).forEach(a => a.tabIndex = -1); $$('.chip,.rv', n).forEach(a => a.classList.add('in')); ul.appendChild(n); }); const step = ul.children[kids.length].offsetLeft - ul.children[0].offsetLeft || one2; ul._a = ul.animate([{ transform: 'translateX(0)' }, { transform: 'translateX(' + -step + 'px)' }], { duration: step / (+ul.dataset.sp || 60) * 1000, iterations: Infinity, direction: ul.dataset.rev ? 'reverse' : 'normal' }); });
/* film in a tile plays only while it is on screen */
$$('.pane video').forEach(v => { if (calm) { v.controls = true; return; } new IntersectionObserver(es => { es[0].isIntersecting ? v.play().catch(() => {}) : v.pause(); }, { threshold: .2 }).observe(v); });
let q = false; const upd = () => { q = false; barInk(); walk(); cards(); }, ask = () => { if (!q) { q = true; requestAnimationFrame(upd); } };
let lw = innerWidth; addEventListener('scroll', ask, { passive: true }); addEventListener('resize', () => { layCards(); if (innerWidth !== lw) { lw = innerWidth; runs(); } ask(); });
layCards(); runs(); upd(); if (D.fonts && D.fonts.ready) D.fonts.ready.then(() => { runs(); layCards(); upd(); });
} catch (err) { document.documentElement.classList.remove('js'); throw err; } })();
"""


def render(d: dict) -> str:
    pal = d.get('palette') or {}
    G, I = pal.get('ground') or '#000000', pal.get('ink') or '#ffffff'
    A = pal.get('accent') or I
    page_dark = _lum(G) < _lum(I)
    lo, hi = (G, I) if page_dark else (I, G)
    acc = _fit(A, G, I)                     # the accent as label text on the page (reference: its green on black)
    acc_band = _fit(A, I, G)                # … and on the turned band (reference: its blue on white)
    # the second colour (reference: the blue tile and the call's slope): the first palette extra that stands off the page
    c2 = next((c for c in pal.get('extra') or [] if re.match(r'^#[0-9a-fA-F]{3,6}$', c or '') and _con(c, G) >= 1.35 and _con(c, I) >= 1.35), A)
    c2t = I if _con(I, c2) >= _con(G, c2) else G
    c2 = _fit(c2, c2t, '#000000' if _lum(c2t) > .5 else '#ffffff', 6.4)
    bt = I if _con(I, A) >= _con(G, A) else G
    b2 = _fit(A, bt, '#000000' if _lum(bt) > .5 else '#ffffff', 4.6)
    b1 = _fit(_mix(c2 if c2.lower() != b2.lower() else bt, b2, .3), bt, '#000000' if _lum(bt) > .5 else '#ffffff', 4.6)
    row = _mix(I, G, .08)
    mu, mu2 = _fit(_mix(I, G, .4), row, I, 4.7), _fit(_mix(I, G, .7), row, I, 4.7)
    root = ';'.join('--%s:%s' % kv for kv in dict(mu=mu, mu2=mu2, g=G, i=I, gr=_tri(G), ir=_tri(I), a=acc, c2=c2, c2t=c2t, b1=b1, b2=b2, bt=bt).items())

    made = (d.get('media') or {}).get('made') or {}
    pool = _Pool(d)
    hero_pic = _land(made, page_dark, (0, 5, 2, 1))
    close_pic = _land(made, page_dark, (2, 5, 1, 0, 3, 4), skip=(hero_pic or {}).get('src') and (hero_pic['src'],) or ())
    hero, hero_ink = s_hero(d, pool, hero_pic, lo, hi, G)
    skip = tuple(x['src'] for x in (hero_pic, close_pic) if x)
    proof, results = s_proof(d, I, G, acc_band), s_results(d, I, made, lo, hi, skip)
    mid = '<div class="pfw">%s%s</div>' % (proof, results) if proof or results else ''
    body = ''.join((hero, s_ticker(d, I), s_walk(d, I, made, page_dark, hero_pic), s_bento(d, I, pool, made, page_dark, G), mid, s_plans(d, I), s_faq(d, I), s_close(d, close_pic, lo, hi, G, I)))
    b, h = d.get('brand') or {}, d.get('hero') or {}
    title = ' — '.join(x for x in (b.get('name'), h.get('kicker') or h.get('title')) if x)
    return ('<!DOCTYPE html>\n<html lang="%s">\n<head>\n<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n<title>%s</title>\n%s'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="%s" rel="stylesheet">\n'
            '<style>:root{%s}%s</style>\n<script>document.documentElement.classList.add("js")</script>\n</head>\n<body>\n%s\n<main id="main">%s</main>\n<script>%s</script>\n</body>\n</html>\n') % (
        e(d.get('lang') or 'en'), e(title), '<meta name="description" content="%s">\n' % e(h['text']) if h.get('text') else '', FONTS, root, CSS,
        s_bar(d, hero_ink or I), body, JS)
