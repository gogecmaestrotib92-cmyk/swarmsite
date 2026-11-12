"""griffin/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type, spacing, motion, phone layout) was measured on the reference's home page
at 1440 and 390 on 2026-11-12 (see NOTES.md). Nothing of the reference's code, words, pictures, icons, logos or typefaces
is here. The client's data fills it; a section whose data is missing is left out whole. No model call, no client logic.
"""
import html
import json
import re

FONTS = ('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300'
         '&family=Hanken+Grotesk:wght@300;400;600&family=Geist+Mono:wght@400;600&display=swap')


# ───────────────────────── colour: the reference's light/dark/accent relations, applied to the client's palette
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


def _theme(bg, ink, accent, floor=4.6):
    """Reference relations on its own ground: muted text = ink at ~58 %, rules 18 %, dim marks 30 %, soft 80 %,
    the main pill 91 % (filling to full ink on hover). Muted text is raised until it reads at 4.6:1."""
    t = .58
    while _con(_mix(ink, bg, t), bg) < floor and t < 1:
        t += .02
    acc = accent if _con(accent, bg) >= 2.3 else ink
    v = {'bg': bg, 'ink': ink, 'mute': _mix(ink, bg, min(t, 1)), 'line': _mix(ink, bg, .18), 'dim': _mix(ink, bg, .30),
         'soft': _mix(ink, bg, .80), 'pill': _mix(ink, bg, .91), 'pillh': ink, 'pilltx': bg, 'ghost': _mix(ink, bg, .07),
         'cardh': _mix(ink, bg, .38), 'focus': _mix(ink, bg, .52), 'acc': acc,
         'bga': 'rgba(%d,%d,%d,.5)' % _rgb(bg), 'inka': '%d,%d,%d' % _rgb(ink), 'bgc': '%d,%d,%d' % _rgb(bg)}
    return ';'.join('--%s:%s' % kv for kv in v.items())


def _fields(ground, ink, extra):
    """Plain grounds that stand where the reference lays a photograph: the palette's other colours that read as a field
    against the page. Text over a field is whichever of ink/ground reads better, and the field is pushed away from it
    until body text reads at 7:1."""
    out = []
    for c in extra or []:
        try:
            if _con(c, ground) < 1.25:
                continue
            tx = ink if _con(ink, c) >= _con(ground, c) else ground
            far = '#000000' if _lum(tx) > .5 else '#ffffff'
            n = 0
            while _con(tx, c) < 7 and n < 12:
                c = _mix(far, c, .1)
                n += 1
            out.append((c, tx))
        except ValueError:
            continue
    return out


def _made(d, kind, i):
    """a made picture by kind and index (wraps round); None when the client has none of the kind"""
    xs = ((d.get('media') or {}).get('made') or {}).get(kind) or []
    xs = [x for x in (xs if isinstance(xs, list) else [xs]) if isinstance(x, dict) and x.get('src')]
    return xs[i % len(xs)] if xs else None


def _over(pic, ground, ink, accent):
    """The theme for text laid over a made picture: light ink on a dark picture, dark ink on a light one. The veil is
    whichever of the page's ground and ink lies on the picture's side; muted text is held at 7:1 against the veil so it
    keeps its margin where the picture shows through."""
    lo, hi = sorted((ground, ink), key=_lum)
    veil, tx = (lo, hi) if pic.get('tone') != 'light' else (hi, lo)
    return _theme(veil, tx, accent, 7)


def backdrop(pic, slot):
    wh = ' width="%s" height="%s"' % (e(pic['w']), e(pic['h'])) if pic.get('w') and pic.get('h') else ''
    return '<img class="bk" data-slot="%s" src="%s" alt=""%s loading="lazy" decoding="async">' % (slot, e(m(pic.get('src'))), wh)


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def m(p):
    """media paths in the data are relative to templates/; a page in <slug>/out/ reaches them two levels up"""
    p = str(p or '')
    return p if re.match(r'^(https?:)?//|^data:', p) else '../../' + p


def nb(s):
    """a heading never breaks inside a hyphenated word"""
    return re.sub(r'(\S+-\S+)', r'<span class="nb">\1</span>', e(s))


ARROW = ('<svg class="ar" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M2.5 8h10M8.5 4l4 4-4 4" '
         'fill="none" stroke="currentColor" stroke-width="1.1"/></svg>')


def pill(link, kind='', arrow=False, cls=''):
    if not link or not link.get('t'):
        return ''
    return '<a class="pill %s %s" href="%s"><span>%s</span>%s</a>' % (kind, cls, e(link.get('h') or '#'), e(link['t']), ARROW if arrow else '')


def img(o, cls='', lazy=True):
    wh = ' width="%s" height="%s"' % (e(o['w']), e(o['h'])) if o.get('w') and o.get('h') else ''
    return '<img class="%s" src="%s" alt="%s"%s%s decoding="async">' % (cls, e(m(o.get('src'))), e(o.get('alt', '')), wh, ' loading="lazy"' if lazy else '')


# ───────────────────────── sections (reference order)
def s_header(d):
    b = d.get('brand') or {}
    nav = [n for n in d.get('nav') or [] if n.get('t')]
    cta, signin = d.get('cta') or {}, d.get('signin') or {}
    logo = ''
    if b.get('logo'):
        logo = '<img src="%s" alt="%s"%s>' % (e(m(b['logo'])), e(b.get('name', '')) if b.get('logo_wordmark') else '', ' class="wm"' if b.get('logo_wordmark') else '')
    name = '' if b.get('logo_wordmark') and b.get('logo') else '<span>%s</span>' % e(b.get('name', ''))
    items = ''.join('<li><a class="ni" href="%s">%s</a></li>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav)
    navcta = '<li class="navcta"><span class="w">%s</span></li>' % pill(cta, 'sm') if cta.get('t') else ''
    navp = '<nav class="navp mono" aria-label="Primary"><ul><i class="hl" aria-hidden="true"></i>%s%s</ul></nav>' % (items, navcta) if items else ''
    right = '<div class="hd-r">%s%s</div>' % (pill(signin, 'sm bare') if signin.get('t') else '', pill(cta, 'sm'))
    mlinks = ''.join('<a href="%s">%s</a>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav + ([signin] if signin.get('t') else []))
    menu = ('<button class="menu" type="button" aria-expanded="false" aria-controls="mnav" aria-label="Menu"><i></i><i></i><i></i></button>'
            if mlinks or cta.get('t') else '')
    mnav = '<div class="mnav mono" id="mnav" hidden><div>%s%s</div></div>' % (mlinks, pill(cta, 'sm')) if menu else ''
    return '<header class="hd"><div class="in hd-in"><a class="logo" href="%s">%s%s</a>%s%s%s</div>%s</header>' % (
        e(b.get('home') or '#'), logo, name, navp, right, menu, mnav)


def s_open(d):
    h = d.get('hero') or {}
    if not h.get('title'):
        return ''
    lede = ''
    if h.get('text') or h.get('text2'):
        lede = '<p class="lede">%s%s</p>' % (e(h.get('text', '')), ' <span>%s</span>' % e(h['text2']) if h.get('text2') else '')
    acts = pill(h.get('primary'), '', True) + pill(h.get('secondary'), 'ghost')
    note = '<p class="note mono">%s</p>' % e(h['note']) if h.get('note') else ''
    row = '<div class="open-row">%s%s</div>' % ('<div class="acts">%s</div>' % acts if acts else '<span></span>', note) if acts or note else ''
    # the band (reference: a field of faint slashes with loose runs of two signs of its trade, one brighter than the
    # other). The slash is kept as the field; the two signs are the first two that stand in the client's own figures.
    # Without figures, or with fewer than two signs in them, the band is left out whole.
    chars = ''.join(str(f.get('v', '')) for f in d.get('figures') or [] if isinstance(f, dict))
    sym = [c for c in dict.fromkeys(chars) if not c.isalnum() and not c.isspace() and c not in '.,/']
    dig = [c for c in dict.fromkeys(chars) if c.isdigit()]
    g = (sym + dig)[:2]
    band = ''
    if len(g) == 2:
        band = '<div class="band" aria-hidden="true"><canvas id="band" data-g="%s"></canvas></div>' % e(json.dumps(['/', g[1], g[0]]))
    return '<section class="open"><div class="in"><div class="open-top"><h1>%s</h1>%s%s</div></div>%s</section>' % (nb(h['title']), lede, row, band)


def s_grid(d):
    logos = [x for x in d.get('logos') or [] if x]
    trust = [x for x in d.get('trust') or [] if x]
    if logos:
        cells = ''.join('<li>%s</li>' % (img(x, 'lg') if isinstance(x, dict) else '<img class="lg" src="%s" alt="" loading="lazy">' % e(m(x))) for x in logos)
    elif trust:
        cells = ''.join('<li>%s</li>' % e(x) for x in trust)
    else:
        return ''
    return '<section class="grid"><div class="in"><ul class="g6 mono">%s</ul></div></section>' % cells


def s_walk(d, colours):
    st = d.get('steps') or {}
    items = [x for x in st.get('items') or [] if x.get('title')]
    if not items:
        return ''
    md = d.get('media') or {}
    known = {x.get('src'): x for k in ('phones', 'photos', 'screens') for x in md.get(k) or []}
    intro = ''
    if st.get('title'):
        intro = '<div class="wintro"><h2 class="h2">%s</h2>%s</div>' % (e(st['title']), '<p class="t20">%s</p>' % e(st['text']) if st.get('text') else '')
    labels = ''.join('<li data-i="%d" style="--c:%s"><span class="no">%02d</span><span>%s</span></li>' % (i, colours[i % len(colours)], i + 1, e(x.get('k') or x['title']))
                     for i, x in enumerate(items))
    arts = ''
    for i, x in enumerate(items):
        fig = ''
        if x.get('img'):
            o = dict(known.get(x['img']) or {}, src=x['img'])
            # no annotation tag: the data has no copy for one, and a picture's alt is never display copy (CONTRACT)
            fig = '<figure class="wi %s" data-i="%d" style="--i:%d;--c:%s">%s</figure>' % (e(x.get('shape', '')), i, i, colours[i % len(colours)], img(o, '', i > 0))
        ey = '<p class="ey mono"><i class="mk"></i><span class="no">%02d</span><b>%s</b></p>' % (i + 1, e(x['k'])) if x.get('k') else '<p class="ey mono"><i class="mk"></i><span class="no">%02d</span></p>' % (i + 1)
        arts += '<article class="wp" data-i="%d" style="--c:%s"><div class="wp-t">%s<h3>%s</h3>%s%s</div>%s</article>' % (
            i, colours[i % len(colours)], ey, e(x['title']), '<p class="t20">%s</p>' % e(x['text']) if x.get('text') else '', pill(x.get('cta'), 'ghost'), fig)
    if not any(x.get('img') for x in items):
        # no step has a picture: the steps stand side by side under their heading — no held screen, no empty half beside them
        return ('<section class="walk rule nofig" style="--n:%d"><div class="in walk-l"><div class="wc">%s<div class="wrow">%s</div></div></div></section>') % (
            min(len(items), 4), intro, arts)
    return ('<section class="walk rule" id="walk" style="--n:%d"><div class="in walk-pin"><div class="walk-l"><div class="rail" aria-hidden="true"></div>'
            '<ol class="wl wl-top mono" aria-hidden="true">%s</ol><div class="wc">%s%s</div><ol class="wl wl-bot mono" aria-hidden="true">%s</ol></div>'
            '<div class="walk-r" aria-hidden="true"><div class="wtrack"></div></div></div></section>') % (len(items), labels, intro, arts, labels)


def _field(slot, field, pic, over, pane):
    """the opening of a two-column section's inner block: the made picture as the ground of the whole section with a
    veil under the text, else the plain palette field (only where a product stands on it), else the page ground"""
    if pic:
        return ' field pic" style="%s">%s' % (over, backdrop(pic, slot))
    if field and pane:
        return ' field" data-slot="%s" style="%s">' % (slot, field)
    return '" data-slot="%s">' % slot


def s_acc(d, field, pic=None, over=''):
    f = d.get('features') or {}
    items = [x for x in f.get('items') or [] if x.get('t')]
    if not items:
        return ''
    screens = [x for x in (d.get('media') or {}).get('screens') or [] if x.get('src')]
    lis = ''
    for i, x in enumerate(items):
        lis += ('<li class="ac%s"%s><h3><button type="button" aria-expanded="%s" aria-controls="ac%d">%s</button></h3>'
                '<div class="ac-b" id="ac%d"><div><p>%s</p></div></div></li>') % (
            ' on' if i == 0 else '', ' data-s="%d"' % (i % len(screens)) if screens else '', 'true' if i == 0 else 'false', i, e(x['t']), i, e(x.get('d', '')))
    pane = ''
    if screens:
        pane = '<div class="pane"><div class="scr">%s</div></div>' % ''.join(
            '<figure class="sc%s" data-s="%d">%s</figure>' % (' on' if i == 0 else '', i, img(x))
            for i, x in enumerate(screens))
    head = '<h2 class="h2">%s</h2>' % e(f['title']) if f.get('title') else ''
    return '<section class="accs rule"><div class="in two%s<div class="col">%s<ul class="acc">%s</ul></div>%s</div></section>' % (
        _field('accordion-backdrop', field, pic, over, pane), head, lis, pane)


def s_plans(d):
    p = d.get('plans') or {}
    items = [x for x in p.get('items') or [] if x.get('name')]
    if not items:
        return ''
    cols = ''
    for x in items:
        price = '<p class="pr">%s%s</p>' % ('<b>%s</b>' % e(x['price']) if x.get('price') else '', ' <span>%s</span>' % e(x['per']) if x.get('per') else '') if x.get('price') or x.get('per') else ''
        rows = ''.join('<li><i class="mono">%02d</i><span>%s</span></li>' % (i + 1, e(r)) for i, r in enumerate(x.get('rows') or []))
        cols += '<div class="pl"><h3>%s</h3>%s%s%s%s</div>' % (
            e(x['name']), price, '<p class="ln">%s</p>' % e(x['line']) if x.get('line') else '', '<ul class="rows">%s</ul>' % rows if rows else '',
            pill(x.get('cta'), '' if x.get('marked') else 'ghost', bool(x.get('marked'))))
    return '<section class="prod rule"><div class="in pad">%s%s<div class="cols" style="--k:%d">%s</div>%s</div></section>' % (
        '<h2 class="h2">%s</h2>' % e(p['title']) if p.get('title') else '', '<p class="sub">%s</p>' % e(p['text']) if p.get('text') else '',
        min(len(items), 3), cols, '<p class="pnote">%s</p>' % e(p['note']) if p.get('note') else '')


def s_shelf(d):
    """the reference's row of picture cards. Takes quotes when there are any; otherwise the client's own photographs
    that have not already stood in the walk — each whole, at its own proportion."""
    md = d.get('media') or {}
    used = {x.get('img') for x in (d.get('steps') or {}).get('items') or []}
    quotes = [q for q in d.get('quotes') or [] if q]
    cards = ''
    if quotes:
        for q in quotes:
            q = q if isinstance(q, dict) else {'text': q}
            text = q.get('text') or q.get('quote') or q.get('q') or ''
            if not text:
                continue
            ph = q.get('photo') or q.get('img')
            ph = ph if isinstance(ph, dict) else ({'src': ph} if ph else None)
            by = ' · '.join(e(v) for v in (q.get('name') or q.get('by'), q.get('role')) if v)
            cards += '<li>%s<p class="ct">%s</p>%s</li>' % (img(ph) if ph else '', e(text), '<p class="by mono">%s</p>' % by if by else '')
        k, n = 3, len(quotes)
    else:
        ph = [x for x in md.get('photos') or [] if x.get('src') and x['src'] not in used]
        if not ph:
            return ''
        tall = sum(1 for x in ph if (x.get('h') or 0) > (x.get('w') or 1)) * 2 >= len(ph)
        cards = ''.join('<li>%s</li>' % img(x) for x in ph)
        k, n = (4 if tall else 3), len(ph)
    if not cards:
        return ''
    return '<section class="shelf rule"><div class="in pad"><ul class="cards%s" style="--k:%d"%s>%s</ul></div></section>' % (
        ' run' if n > k else '', k, ' tabindex="0"' if n > k else '', cards)


def s_faq(d, field, pic=None, over=''):
    f = d.get('faq') or {}
    items = [x for x in f.get('items') or [] if x.get('q')]
    if not items:
        return ''
    md, h = d.get('media') or {}, d.get('hero') or {}
    v = md.get('video') or None
    pane = ''
    if v and v.get('src'):
        pane = ('<div class="pane"><video class="vid" src="%s"%s%s muted loop playsinline preload="metadata" aria-label="%s"></video></div>') % (
            e(m(v['src'])), ' poster="%s"' % e(m(v['poster'])) if v.get('poster') else '',
            ' width="%s" height="%s"' % (e(v['w']), e(v['h'])) if v.get('w') and v.get('h') else '', e(v.get('alt', '')))
    dl = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(x['q']), e(x.get('a', ''))) for x in items)
    acts = pill(h.get('primary'), '', True) + pill(h.get('secondary'), 'ghost')
    return '<section class="faq rule"><div class="in two%s<div class="col">%s<dl>%s</dl>%s</div>%s</div></section>' % (
        _field('pairs-backdrop', field, pic, over, pane),
        '<h2 class="h2">%s</h2>' % e(f['title']) if f.get('title') else '', dl, '<div class="acts">%s</div>' % acts if acts else '', pane)


def s_links(d):
    links = [x for x in d.get('links') or [] if x.get('t')]
    s = d.get('statement') or {}
    if not links and not s.get('title'):
        return ''
    head = ''
    if s.get('title'):
        head = '<div class="lhead"><h2 class="h2">%s</h2>%s</div>' % (e(s['title']), '<p class="sub">%s</p>' % e(s['text']) if s.get('text') else '')
    cards = ''.join('<li><a href="%s">%s</a>%s%s</li>' % (e(x.get('h') or '#'), e(x['t']), ARROW, '<p>%s</p>' % e(x['d']) if x.get('d') else '') for x in links)
    return '<section class="fast rule"><div class="in pad">%s%s</div></section>' % (head, '<ul class="four" style="--k:%d">%s</ul>' % (min(len(links), 4), cards) if cards else '')


def s_close(d):
    c = d.get('close') or {}
    if not c.get('title'):
        return ''
    return '<section class="end rule"><div class="in"><h2 class="h2">%s</h2>%s</div></section>' % (e(c['title']), pill(c.get('cta'), '', True))


def s_foot(d):
    b, f = d.get('brand') or {}, d.get('foot') or {}
    nav = [n for n in d.get('nav') or [] if n.get('t')]
    acct = [x for x in (d.get('signin'), d.get('cta')) if x and x.get('t')]
    logo = ''
    if b.get('logo'):
        logo = '<img src="%s" alt="%s"%s loading="lazy">' % (e(m(b['logo'])), e(b.get('name', '')) if b.get('logo_wordmark') else '', ' class="wm"' if b.get('logo_wordmark') else '')
    name = '' if b.get('logo_wordmark') and b.get('logo') else '<span>%s</span>' % e(b.get('name', ''))
    col = lambda xs: '<ul>%s</ul>' % ''.join('<li><a href="%s">%s</a></li>' % (e(x.get('h') or '#'), e(x['t'])) for x in xs) if xs else ''
    fl = ''.join('<a href="%s">%s</a>' % (e(x.get('h') or '#'), e(x['t'])) for x in f.get('links') or [] if x.get('t'))
    bar = '<div class="fbar">%s%s</div>' % ('<small>%s</small>' % e(f['legal']) if f.get('legal') else '<span></span>', '<p>%s</p>' % fl if fl else '') if f.get('legal') or fl else ''
    return '<footer class="ft rule"><div class="in"><div class="fgrid"><div class="fl"><a class="logo" href="%s">%s%s</a>%s</div>%s%s</div>%s</div></footer>' % (
        e(b.get('home') or '#'), logo, name, '<p>%s</p>' % e(f['text']) if f.get('text') else '', col(nav), col(acct), bar)


CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}html{background:var(--bg);-webkit-text-size-adjust:100%}
body{font:400 16px/1.5 var(--sans);color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased;overflow-x:clip}
a{color:inherit;text-decoration:none}img,video{display:block;max-width:100%;height:auto}ul,ol{list-style:none}button{font:inherit;color:inherit;background:none;border:0;cursor:pointer;text-align:left}
:focus-visible{outline:3px solid var(--focus);outline-offset:2px}
:root{--serif:'Newsreader',Georgia,'Times New Roman',serif;--sans:'Hanken Grotesk',system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'Geist Mono','IBM Plex Mono',ui-monospace,Menlo,monospace}
.in{margin:0 20px;position:relative}.pad{padding:80px 40px}.rule{border-top:1px solid var(--line)}
.mono{font:400 12px/1.33 var(--mono);letter-spacing:.06em;text-transform:uppercase}
.h2{font:300 40px/1.1 var(--serif);letter-spacing:-.04em;font-variation-settings:"opsz" 72;text-wrap:balance}
.t20{font:300 20px/1.4 var(--sans)}.sub{font:400 20px/1.4 var(--sans);color:var(--mute);max-width:32em;margin-top:16px}
/* pills: 40 high, 12x20, fully round; the fill wipes across in .3s */
.pill{position:relative;z-index:0;display:inline-flex;align-items:center;gap:6px;height:40px;padding:0 20px;border-radius:9999px;overflow:clip;background:var(--pill);color:var(--pilltx);font:400 12px/1.33 var(--mono);letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;max-width:100%}
.pill span{overflow:hidden;text-overflow:ellipsis}.pill::before{content:"";position:absolute;inset:0;z-index:-1;background:var(--pillh);transform:scaleX(0);transform-origin:0 50%;transition:transform .3s}.pill:hover::before{transform:scaleX(1)}
.pill.ghost{background:var(--bg);color:var(--ink);box-shadow:inset 0 0 0 1px var(--line)}.pill.ghost::before{background:var(--line)}
.pill.bare{background:none;color:var(--ink)}.pill.bare::before{background:var(--ghost)}
.pill.sm{height:32px;padding:0 14px;gap:4px}.pill .ar{margin-right:-4px;flex:none}
/* bar: 64 high, in the flow; the links ride in a fixed, blurred pill 12 from the top and the call joins them once the page moves */
.hd{position:relative;z-index:30}.hd-in{height:64px;padding:0 40px;display:flex;align-items:center;justify-content:space-between;gap:8px}
.logo{display:flex;align-items:center;gap:10px;font:400 24px/1 var(--serif);letter-spacing:-.02em;font-variation-settings:"opsz" 72}.logo img{height:28px;width:auto;border-radius:6px}.logo img.wm{height:24px;border-radius:0}
.navp{position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:40}.navp ul{position:relative;display:flex;align-items:center;padding:4px;border-radius:9999px;background:var(--bga);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
.ni{position:relative;z-index:1;display:flex;align-items:center;height:32px;padding:0 16px;border-radius:9999px;line-height:1;white-space:nowrap}
.hl{position:absolute;z-index:0;top:4px;left:0;height:32px;width:40px;border-radius:9999px;background:var(--dim);opacity:0;pointer-events:none;transition:transform .23s cubic-bezier(.3,.76,.27,1),width .23s cubic-bezier(.3,.76,.27,1),opacity .23s cubic-bezier(.3,.76,.27,1)}
.navcta{display:grid;grid-template-columns:0fr;opacity:0;visibility:hidden;transition:grid-template-columns .3s cubic-bezier(.4,0,.2,1),opacity .32s cubic-bezier(.4,0,.2,1),visibility 0s .32s}.navcta .w{min-width:0;overflow:hidden;display:block}
.moved .navcta{grid-template-columns:1fr;opacity:1;visibility:visible;transition-delay:0s}
.hd-r{display:flex;align-items:center;gap:12px}.menu{display:none;width:44px;height:44px;margin-right:-12px;place-content:center;gap:4px}.menu i{display:block;width:18px;height:1.5px;background:var(--ink)}
.mnav{border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--bg)}.mnav>div{display:grid;padding:8px 28px 24px}.mnav a:not(.pill){display:flex;align-items:center;height:52px;border-bottom:1px solid var(--line);font-size:14px}.mnav .pill{justify-self:start;margin-top:20px}
/* opening: display 72/1 light serif, text 20/1.4 light at 616, pills; everything 24 apart; then the band, 252 between two rules */
.open-top{min-height:454px;padding:80px 40px 40px;display:flex;flex-direction:column;justify-content:flex-end}
h1{font:300 72px/1 var(--serif);letter-spacing:-.02em;font-variation-settings:"opsz" 72;max-width:11.5em;text-wrap:balance}
.nb{white-space:nowrap}.lede{font:300 20px/1.4 var(--sans);max-width:616px;margin-top:24px}.lede span{color:var(--mute)}
.open-row{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;margin-top:24px}.acts{display:flex;gap:16px;flex-wrap:wrap}
.note{display:flex;align-items:center;gap:12px;font-size:14px;line-height:1}.note::before{content:"";flex:none;width:7px;height:7px;border-radius:50%;background:rgba(var(--inka),.8);animation:pulse 3s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(var(--inka),.5)}100%{box-shadow:0 0 0 .5em rgba(var(--inka),0)}}
.band{height:254px;border-block:1px solid var(--line);overflow:hidden}.band canvas{display:block;width:100%;height:100%}
/* ruled grid: six cells, 64 high, dashed inside, solid at the sides */
.g6{display:grid;grid-template-columns:repeat(6,1fr);border-inline:1px solid var(--line);color:var(--mute)}
.g6 li{min-height:64px;display:grid;place-items:center;text-align:center;padding:8px 14px;border-left:1px dashed var(--line);line-height:1.33}.g6 li:nth-child(6n+1){border-left:0}.g6 li:nth-child(n+7){border-top:1px dashed var(--line)}.g6 .lg{max-height:28px;width:auto}
/* THE WALK. Without script or with reduced motion it is a plain run of steps, text beside its picture on the dotted ground. */
.walk-l{padding:80px 40px}.wl,.rail{display:none}.wintro{max-width:620px;margin-bottom:24px}.wintro .t20{margin-top:16px;max-width:24em}
.wp{display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:40px;padding:56px 0}
.wp h3{font:300 40px/1.1 var(--serif);letter-spacing:-.04em;font-variation-settings:"opsz" 72;max-width:14em;text-wrap:balance}.wp .t20{margin-top:16px;max-width:24.6em}.wp .pill{margin-top:32px}
.ey{position:relative;display:flex;gap:12px;font-size:14px;line-height:1;margin-bottom:8px}.ey b{font-weight:600}.no{color:var(--mute)}
.mk{position:absolute;left:-44px;top:3px;width:8px;height:8px;border-radius:50%;background:var(--c);box-shadow:0 0 0 3px var(--bg),0 0 0 4px color-mix(in srgb,var(--c) 60%,transparent),0 0 0 7px var(--bg),0 0 0 8px color-mix(in srgb,var(--c) 30%,transparent),0 0 0 11px var(--bg),0 0 0 11.5px color-mix(in srgb,var(--c) 30%,transparent),0 0 0 14.5px var(--bg)}
.wi{position:relative;justify-self:center;line-height:0}.wi img{max-height:62vh;width:auto;max-width:min(34vw,100%);border-radius:8px;box-shadow:0 0 0 1px var(--line)}
.walk-r{display:none}
.nofig .wrow{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:40px;margin-top:40px}.nofig .wp{display:block;padding:0}.nofig .wp h3{font-size:32px}
@media (max-width:900px){.nofig .wrow{grid-template-columns:1fr;gap:32px;margin-top:24px}.nofig .wp h3{font-size:24px}}
/* pinned: the section is one screen held for 380 + 625 a step; labels wait below, pass, and collect above; the pictures ride the scroll */
.walk.pin{height:calc(100vh + 380px + var(--n)*625px)}.pin .walk-pin{position:sticky;top:0;height:100vh;display:grid;grid-template-columns:1fr 1fr}
.pin .walk-l{position:relative;height:100vh;padding:80px 40px 40px}.pin .rail{display:block;position:absolute;left:-1px;top:0;bottom:0;width:1px;background:linear-gradient(transparent 0,var(--rc,transparent) min(200px,var(--p,0px)),var(--rc,transparent) max(calc(var(--p,0px) - 200px),min(200px,var(--p,0px))),transparent var(--p,0px)),var(--line)}
.pin .wl{display:block;position:absolute;left:40px;right:40px;font-size:14px;line-height:1}.pin .wl-top{top:80px}.pin .wl-bot{bottom:40px}
.pin .wl li{position:relative;display:none;gap:12px;height:14px;margin-bottom:16px;color:var(--mute)}.pin .wl-bot li{margin:16px 0 0}.pin .wl li.on{display:flex;animation:lup .35s both}.pin .wl.dn li.on{animation-name:ldn}
.pin .wl li::before{content:"";position:absolute;left:-44px;top:3px;width:8px;height:8px;border-radius:50%;background:var(--dim);box-shadow:0 0 0 3px var(--bg),0 0 0 4px color-mix(in srgb,var(--dim) 60%,transparent),0 0 0 7px var(--bg)}
@keyframes lup{from{opacity:0;translate:0 8px}to{opacity:1;translate:0 0}}@keyframes ldn{from{opacity:0;translate:0 -8px}to{opacity:1;translate:0 0}}
.pin .wc{height:100%;display:grid;align-content:center}.pin .wintro,.pin .wp{grid-area:1/1;margin:0;padding:0;visibility:hidden;opacity:0}.pin .wp{display:block}
.pin .wintro.on,.pin .wp.on{visibility:visible;opacity:1}.pin .wp.on .ey b,.pin .wp.on .ey .no{animation:wipe .5s ease-out .05s both}.pin .wp.on h3,.pin .wp.on .t20,.pin .wp.on .pill{animation:fadein .5s ease-out .06s both}
@keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0)}}@keyframes fadein{from{opacity:0}to{opacity:1}}
.pin .walk-r{display:block;position:relative;height:100vh;overflow:hidden;background:radial-gradient(circle,var(--line) 1px,transparent 1px) 0 0/16px 16px;-webkit-mask-image:linear-gradient(90deg,transparent,#000 22%);mask-image:linear-gradient(90deg,transparent,#000 22%)}
.pin .wtrack{position:absolute;inset:0}.pin .wi{position:absolute;left:50%;top:50%;transform:translate(-50%,calc(-50% + (var(--i) - var(--f,-1))*var(--pitch,70vh)));opacity:.26;transition:opacity .5s ease}.pin .wi.on{opacity:1}
/* two columns: text on the left, the product whole on the right; where the reference lays a photograph the whole section takes one plain ground */
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}.two .col{padding:80px 40px;min-width:0}.field{background:var(--bg);color:var(--ink)}
/* with a made picture: it is the ground of the whole section, object-fit cover; a veil of the theme's ground lies under the text half and lets go toward the product side (on a phone: under the text block, letting go downward) */
.pic{isolation:isolate;overflow:hidden}.bk{position:absolute;inset:0;z-index:-2;width:100%;height:100%;max-width:none;object-fit:cover}
.pic::before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(90deg,rgba(var(--bgc),.92) 0,rgba(var(--bgc),.92) 49%,rgba(var(--bgc),.84) 52%,rgba(var(--bgc),.6) 56%,rgba(var(--bgc),.36) 60%,rgba(var(--bgc),.2) 65%)}
.pane{display:grid;place-items:center;padding:40px;min-width:0}.scr{display:grid;place-items:center;width:100%}
.sc{grid-area:1/1;opacity:0;visibility:hidden;transition:opacity .6s ease,visibility 0s .6s;width:100%}.sc.on{opacity:1;visibility:visible;transition-delay:0s}
.sc img,.vid{width:100%;border-radius:12px;box-shadow:0 0 0 1px var(--line)}
.accs .h2{margin-bottom:32px}.ac{position:relative}.ac+.ac{border-top:1px solid var(--line)}
.ac button{display:block;width:100%;padding:16px 0;font:300 24px/32px var(--serif);letter-spacing:-.04em;font-variation-settings:"opsz" 72;color:var(--mute);transition:color .3s ease,font-size .3s ease,line-height .3s ease}
.ac button:hover,.ac.on button{color:var(--ink)}.ac.on button{font-size:32px;line-height:40px}
.ac-b{display:grid;grid-template-rows:0fr;opacity:0;visibility:hidden;transition:grid-template-rows .4s ease,opacity .25s ease,visibility 0s .4s}.ac-b>div{overflow:hidden;min-height:0}.ac-b p{max-width:480px;padding-bottom:32px}
.ac.on .ac-b{grid-template-rows:1fr;opacity:1;visibility:visible;transition:grid-template-rows .4s ease,opacity .25s ease .1s,visibility 0s}
.acc.auto .ac.on::after{content:"";position:absolute;left:0;bottom:-1px;height:1px;width:100%;background:var(--soft);transform-origin:0 50%;animation:bar 8s linear both;z-index:1}.acc.auto.hold .ac.on::after{animation-play-state:paused}
@keyframes bar{from{transform:scaleX(0)}to{transform:scaleX(1)}}
/* products: 40 serif head, then columns of ruled rows — a 52 tile, 20/26 text, dashed between */
.prod .h2+.cols,.prod .sub+.cols{margin-top:32px}.cols{display:grid;grid-template-columns:repeat(var(--k),1fr);gap:0 40px}.pl{padding:24px 0;display:flex;flex-direction:column;align-items:flex-start}
.pl h3{font:300 28px/1.2 var(--sans);margin-bottom:12px}.pr{font:300 20px/1.4 var(--sans)}.pr b{font-weight:400}.pr span,.ln{color:var(--mute)}.ln{margin-top:4px}
.rows{width:100%;margin-top:12px}.rows li{position:relative;display:grid;grid-template-columns:52px 1fr;gap:24px;align-items:center;padding:16px 0;font:400 20px/26px var(--sans)}.rows li+li::before{content:"";position:absolute;top:0;left:76px;right:0;border-top:1px dashed var(--line)}
.rows i{width:52px;height:52px;display:grid;place-items:center;border:1px solid var(--dim);border-radius:4px;color:var(--soft);font-style:normal}.pl .pill{margin-top:24px}.pnote{margin-top:40px;max-width:44em;color:var(--mute)}
/* picture row: each picture whole at its own proportion, on the reference's card columns */
.cards{display:grid;grid-template-columns:repeat(var(--k),1fr);gap:40px;align-items:start}.cards[style*="--k:4"]{gap:16px}
.cards.run{display:flex;overflow-x:auto;scroll-snap-type:x proximity;scrollbar-width:thin;scrollbar-color:var(--dim) transparent;margin:0 -40px;padding:0 40px 16px}.cards.run li{flex:0 0 calc((100% - (var(--k) - 1)*16px)/var(--k));scroll-snap-align:start}
.cards li{min-width:0}.cards img{width:100%;border-radius:2px}.ct{font:300 24px/32px var(--sans);margin-top:16px}.by{margin-top:28px;color:var(--mute)}
/* pairs: 18/26, the answer muted */
.faq .h2{margin-bottom:64px}.faq dl{display:flex;flex-direction:column;gap:20px}.faq dl>div{position:relative;padding-left:38px;display:grid;gap:4px}.faq dl>div::before{content:"";position:absolute;left:6px;top:8px;width:10px;height:10px;border-radius:50%;background:var(--acc)}
.faq dt{font:400 18px/26px var(--sans)}.faq dd{font:400 18px/26px var(--sans);color:var(--mute);max-width:34em}.faq .acts{margin-top:40px}
/* link cards: four across, 16 apart, 16 inside, radius 8; the rule lightens under the pointer */
.lhead{margin-bottom:64px}.four{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.four li{position:relative;display:grid;grid-template-columns:1fr 20px;gap:36px 12px;padding:16px;border:1px solid var(--line);border-radius:8px;transition:border-color .2s ease}.four li:hover{border-color:var(--cardh)}
.four a{font:300 20px/28px var(--sans)}.four a::after{content:"";position:absolute;inset:0;border-radius:8px}.four .ar{width:20px;height:20px;margin-top:4px;color:var(--mute);transition:color .2s ease}.four li:hover .ar{color:var(--ink)}.four p{grid-column:1/-1;font:300 16px/24px var(--sans);color:var(--mute)}
/* the close: centred, 120 above and below */
.end .in{padding:120px 40px;display:flex;flex-direction:column;align-items:center;text-align:center}.end .h2{max-width:12em}.end .pill{margin-top:32px}
.fgrid{display:grid;grid-template-columns:360px repeat(4,1fr);gap:32px;padding:80px 0 40px}.fl{padding:0 40px;display:flex;flex-direction:column;gap:24px}.fl p{font:400 12px/16px var(--sans);color:var(--mute);max-width:280px}
.fgrid ul{display:grid;gap:4px;align-content:start}.fgrid ul a{display:block;padding:4px 0;font:400 14px/18px var(--sans);color:var(--mute);transition:color .2s ease}.fgrid ul a:hover,.fbar a:hover{color:var(--soft)}
.fbar{display:flex;justify-content:space-between;gap:4px 24px;flex-wrap:wrap;margin:0 -20px;padding:20px 60px;border-top:1px solid var(--line);font:400 12px/16px var(--sans);color:var(--mute)}.fbar small{font-size:12px}.fbar p{display:flex;gap:20px}.fbar a{transition:color .2s ease}
@media (max-width:1100px){.navp,.hd-r{display:none}.menu{display:grid}}
@media (min-width:1101px){.mnav{display:none}}
/* PHONE (measured at 390): 8 + 20 at the sides, display 32, text 18, pills 32 high, one column, the walk held with its text on top */
@media (max-width:900px){.in{margin:0 8px}.pad{padding:40px 20px}.hd-in{padding:0 20px}.logo{font-size:22px}.logo img{height:26px}.logo img.wm{height:22px}
.pill{height:32px;padding:0 14px;gap:4px}.h2{font-size:28px}.t20{font-size:16px;line-height:22px}.sub{font-size:16px;line-height:24px;margin-top:8px}
.open-top{min-height:472px;padding:40px 20px 20px}h1{font-size:32px}.lede{font-size:18px;margin-top:16px}.lede span{display:block}.open-row{flex-direction:column;align-items:flex-start;gap:20px;margin-top:16px}.acts{gap:12px 16px}.note{font-size:12px}.band{height:180px}
.g6{grid-template-columns:repeat(2,1fr)}.g6 li:nth-child(n){border-left:1px dashed var(--line);border-top:1px dashed var(--line)}.g6 li:nth-child(2n+1){border-left:0}.g6 li:nth-child(-n+2){border-top:0}
.walk-l{padding:40px 20px}.wp{grid-template-columns:1fr;gap:32px;padding:32px 0}.wp h3{font-size:28px}.wp .t20{margin-top:12px}.wp .pill{margin-top:24px}.ey{font-size:12px}.mk{left:-24px;top:2px}.wi img{max-height:56svh;max-width:min(78vw,100%)}
.walk.pin{height:calc(100svh + 340px + var(--n)*600px)}.pin .walk-pin{height:100svh;grid-template-columns:1fr;grid-template-rows:auto 1fr}.pin .walk-l{height:auto;min-height:280px;padding:40px 20px 20px}.pin .wl{display:none}.pin .wc{align-content:start}.pin .wintro .t20{margin-top:12px}
.pin .walk-r{height:auto;-webkit-mask-image:none;mask-image:none}.pin .wi img{max-height:46svh;max-width:78vw}
.two{grid-template-columns:1fr;gap:0}.two .col{padding:40px 20px}.pane{padding:0 20px 40px}.pic .pane{padding:32px 20px 40px}
.pic::before{background:rgba(var(--bgc),.2)}.pic .col{background:linear-gradient(0deg,rgba(var(--bgc),0) 0,rgba(var(--bgc),.16) 6px,rgba(var(--bgc),.5) 16px,rgba(var(--bgc),.8) 28px,rgba(var(--bgc),.9) 40px)}.sc img,.vid{border-radius:9px}
.ac button{font-size:20px;line-height:28px}.ac.on button{font-size:24px;line-height:32px}
.prod .h2+.cols,.prod .sub+.cols{margin-top:24px}.cols{grid-template-columns:1fr}.pl{padding:16px 0}.pl h3{font-size:20px;margin-bottom:8px}.pr{font-size:16px}.ln{font-size:14px}.rows li{grid-template-columns:36px 1fr;gap:12px;padding:12px 0;font-size:16px;line-height:20.8px}.rows i{width:36px;height:36px;font-size:10px}.rows li+li::before{left:48px}.pnote{font-size:14px;margin-top:24px}
.cards,.cards.run{display:flex;gap:20px;overflow-x:auto;scroll-snap-type:x proximity;margin:0 -20px;padding:0 20px 12px}.cards li,.cards.run li{flex:0 0 301px;scroll-snap-align:start}.cards[style*="--k:4"] li{flex-basis:220px}.ct{font-size:18px;line-height:22px}
.faq .two .col{padding:64px 20px}.faq .h2{margin-bottom:48px}.faq dl>div{padding-left:32px}.faq dl>div::before{left:4px;top:5px}.faq dt,.faq dd{font-size:16px;line-height:20px}.faq dd{line-height:22px}.faq .acts{flex-direction:column;align-items:center}
.lhead{margin-bottom:48px}.four{grid-template-columns:1fr}.four li{gap:24px 12px}.four a{font-size:16px;line-height:24px}.four p{font-size:14px;line-height:20px}.four .ar{margin-top:2px}
.end .in{padding:60px 20px}.fgrid{grid-template-columns:1fr 1fr;padding:40px 0}.fl{grid-column:1/-1;padding:0 20px}.fl p{max-width:none}.fgrid ul{padding:0 20px}.fbar{flex-direction:column;margin:0 -8px;padding:10px 28px}}
@media (min-width:901px) and (max-width:1100px){.four{grid-template-columns:repeat(2,1fr)}.fgrid{grid-template-columns:300px repeat(2,1fr)}h1{font-size:60px}}
@media (min-width:901px){.four[style*="--k:3"]{grid-template-columns:repeat(4,1fr)}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}html{scroll-behavior:auto}}
"""

JS = r"""
(() => { const D = document, calm = matchMedia('(prefers-reduced-motion:reduce)').matches, $ = (s, r) => (r || D).querySelector(s), $$ = (s, r) => [...(r || D).querySelectorAll(s)];
/* the bar: the call joins the fixed links once the page has moved about 105 px; a soft pill follows the pointer along the links */
const moved = () => D.documentElement.classList.toggle('moved', scrollY > 105); addEventListener('scroll', moved, { passive: true }); moved();
const ul = $('.navp ul'), hl = $('.navp .hl'); if (ul && hl) { $$('.ni', ul).forEach(a => { const on = () => { hl.style.width = a.offsetWidth + 'px'; hl.style.transform = 'translateX(' + a.offsetLeft + 'px)'; hl.style.opacity = 1; }; a.addEventListener('pointerenter', on); a.addEventListener('focus', on); }); ul.addEventListener('pointerleave', () => hl.style.opacity = 0); ul.addEventListener('focusout', () => hl.style.opacity = 0); }
const mb = $('.menu'), mn = $('#mnav'); if (mb && mn) mb.addEventListener('click', () => { const o = mb.getAttribute('aria-expanded') !== 'true'; mb.setAttribute('aria-expanded', o); mn.hidden = !o; });
/* the band: a 12 x 14 grid; a field of faint slashes, and two signs in loose runs of their own that drift and change */
(() => { const cv = $('#band'); if (!cv) return; const x = cv.getContext('2d'), G = JSON.parse(cv.dataset.g), cs = getComputedStyle(D.documentElement), ink = cs.getPropertyValue('--inka').trim(), A = [.16, .34, .62]; let W, H, R, live = true, last = 0;
  const h = (i, j, k) => { let n = Math.imul(i, 374761393) ^ Math.imul(j, 668265263) ^ Math.imul(k, 2147483647); n = Math.imul(n ^ (n >>> 13), 1274126177); return ((n ^ (n >>> 16)) >>> 0) / 4294967296; }, sm = t => t * t * (3 - 2 * t);
  const nz = (a, b, c) => { const i = Math.floor(a), j = Math.floor(b), k = Math.floor(c), u = sm(a - i), v = sm(b - j), w = sm(c - k), L = (p, q, t) => p + (q - p) * t; return L(L(L(h(i, j, k), h(i + 1, j, k), u), L(h(i, j + 1, k), h(i + 1, j + 1, k), u), v), L(L(h(i, j, k + 1), h(i + 1, j, k + 1), u), L(h(i, j + 1, k + 1), h(i + 1, j + 1, k + 1), u), v), w); };
  const lay = () => { R = Math.min(2, devicePixelRatio || 1); W = cv.clientWidth; H = cv.clientHeight; cv.width = W * R; cv.height = H * R; };
  const draw = now => { const t = now / 1000 * .22; x.setTransform(R, 0, 0, R, 0, 0); x.clearRect(0, 0, W, H); x.font = '400 12px ' + cs.getPropertyValue('--mono'); x.textAlign = 'center'; x.textBaseline = 'middle';
    for (let r = 0, y = 7; y < H + 7; r++, y += 14) for (let c = 0, X = 6; X < W + 6; c++, X += 12) { const a = nz(c * .11 + t * .5, r * .3, t) * .42 + nz(c * .85, r * 1.9 + 31, t * 1.6 + 9) * .58, b = nz(c * .11 - t * .4 + 57, r * .3 + 23, t + 5) * .42 + nz(c * .85 + 13, r * 1.9, t * 1.6 + 3) * .58; const q = b > .612 ? 2 : a > .607 ? 1 : 0; x.fillStyle = 'rgba(' + ink + ',' + A[q] + ')'; x.fillText(G[q], X, y); } };
  const loop = now => { if (live && now - last > 90) { last = now; draw(now); } requestAnimationFrame(loop); };
  addEventListener('resize', () => { lay(); draw(performance.now()); }); lay(); draw(0); if (D.fonts && D.fonts.ready) D.fonts.ready.then(() => draw(performance.now()));
  if (!calm) { new IntersectionObserver(es => live = es[0].isIntersecting).observe(cv); requestAnimationFrame(loop); } })();
/* the walk: held for one screen; the step follows the scroll (380 px of opening, then 625 a step; 340 and 600 on a phone) and the pictures are moved by the scroll itself, with no easing */
(() => { const sec = $('#walk'); if (!sec || calm) return; const steps = $$('.wp', sec), figs = $$('.wi', sec), track = $('.wtrack', sec), pane = $('.walk-r', sec), intro = $('.wintro', sec), top = $('.wl-top', sec), bot = $('.wl-bot', sec), rail = $('.rail', sec), n = steps.length; if (!n) return;
  figs.forEach(f => track.appendChild(f)); if (!figs.length) pane.style.visibility = 'hidden'; sec.classList.add('pin'); let cur = -2, lastY = 0, q = false;
  const upd = () => { q = false; const ph = innerWidth <= 900, I = ph ? 340 : 380, S = ph ? 600 : 625, y = -sec.getBoundingClientRect().top, a = y < I ? -1 : Math.min(n - 1, Math.floor((y - I) / S));
    const u = (y - I) / S, k = Math.floor(u), w = u - k, g = w < .22 ? -.5 * (1 - w / .22) : w > .78 ? .5 * (w - .78) / .22 : 0; track.style.setProperty('--f', (u < 0 ? Math.max(-1.2, u - .5) : u >= n ? n - 1 : k + g).toFixed(4)); track.style.setProperty('--pitch', Math.round(pane.clientHeight * (ph ? .96 : .7)) + 'px');
    const pr = Math.max(0, Math.min(1, y / (sec.offsetHeight - innerHeight))); if (rail) rail.style.setProperty('--p', Math.round(pr * innerHeight) + 'px');
    if (a === cur) return; const dn = y < lastY; lastY = y; cur = a; if (intro) intro.classList.toggle('on', a < 0); steps.forEach((s, i) => s.classList.toggle('on', i === a || (a < 0 && !intro && i === 0))); figs.forEach(f => f.classList.toggle('on', +f.dataset.i === a));
    [top, bot].forEach(l => l.classList.toggle('dn', dn)); $$('li', top).forEach((l, i) => l.classList.toggle('on', a >= 0 && i < a)); $$('li', bot).forEach((l, i) => l.classList.toggle('on', i > a)); if (rail) rail.style.setProperty('--rc', a < 0 ? 'transparent' : steps[a].style.getPropertyValue('--c')); };
  const ask = () => { if (!q) { q = true; requestAnimationFrame(upd); } }; addEventListener('scroll', ask, { passive: true }); addEventListener('resize', () => { cur = -2; ask(); }); upd(); })();
/* the list beside the screens: one open at a time; it moves on by itself every 8 s under a thin running line until someone chooses */
(() => { const acc = $('.acc'); if (!acc) return; const items = $$('.ac', acc), shots = $$('.sc'); let k = 0;
  const open = i => { k = i; items.forEach((it, j) => { it.classList.toggle('on', j === i); $('button', it).setAttribute('aria-expanded', j === i); }); const s = items[i].dataset.s; if (s != null) shots.forEach(f => f.classList.toggle('on', f.dataset.s === s)); };
  items.forEach((it, i) => $('button', it).addEventListener('click', () => { acc.classList.remove('auto'); open(i); }));
  if (calm || items.length < 2) return; acc.classList.add('auto', 'hold'); acc.addEventListener('animationend', ev => { if (ev.animationName === 'bar' && acc.classList.contains('auto')) open((k + 1) % items.length); });
  new IntersectionObserver(es => acc.classList.toggle('hold', !es[0].isIntersecting), { threshold: .25 }).observe(acc); })();
/* the film plays only while it is on screen, and not at all when motion is unwelcome */
(() => { const v = $('.vid'); if (!v) return; if (calm) { v.controls = true; return; } new IntersectionObserver(es => { es[0].isIntersecting ? v.play().catch(() => {}) : v.pause(); }, { threshold: .2 }).observe(v); })();
})();
"""


def render(d: dict) -> str:
    pal = d.get('palette') or {}
    ground, ink, accent = pal.get('ground') or '#0c0c0b', pal.get('ink') or '#f9f5ef', pal.get('accent') or pal.get('ink') or '#f9f5ef'
    root = _theme(ground, ink, accent)
    colours = [c for i, c in enumerate(dict.fromkeys([accent] + list(pal.get('extra') or []))) if _con(c, ground) >= (2.3 if i == 0 else 4)] or [ink]
    fields = [_theme(c, tx, accent) for c, tx in _fields(ground, ink, pal.get('extra'))]
    f1 = fields[0] if fields else ''
    f2 = fields[1] if len(fields) > 1 else f1
    b, h = d.get('brand') or {}, d.get('hero') or {}
    title = ' — '.join(x for x in (b.get('name'), h.get('kicker') or h.get('title')) if x)
    # where the reference lays a photograph: water behind the accordion, the wide empty landscape behind the pairs
    p1, p2 = _made(d, 'land', 2), _made(d, 'land', 5)
    o1, o2 = (_over(p, ground, ink, accent) if p else '' for p in (p1, p2))
    body = ''.join((s_open(d), s_grid(d), s_walk(d, colours), s_acc(d, f1, p1, o1), s_plans(d), s_shelf(d), s_faq(d, f2, p2, o2), s_links(d), s_close(d)))
    return ('<!DOCTYPE html>\n<html lang="%s">\n<head>\n<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n<title>%s</title>\n%s'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="%s" rel="stylesheet">\n'
            '<style>:root{%s}%s</style>\n</head>\n<body>\n%s\n<main id="main">%s</main>\n%s\n<script>%s</script>\n</body>\n</html>\n') % (
        e(d.get('lang') or 'en'), e(title), '<meta name="description" content="%s">\n' % e(h['text']) if h.get('text') else '', FONTS, root, CSS, s_header(d), body, s_foot(d), JS)
