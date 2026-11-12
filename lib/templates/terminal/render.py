"""terminal/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type, spacing, radii, motion, phone layout) was measured on the reference's
home page at 1440 and 390 on 2026-11-12 (see NOTES.md, probe/). Nothing of the reference's code, words, pictures, icons,
logos or commercial typefaces is here. The client's data fills it; a section whose data is missing is left out whole.
No model call, no file read, no client logic.
"""
import html
import re

FONTS = 'https://fonts.googleapis.com/css2?family=Geist:wght@400..600&family=Geist+Mono:wght@400;600&display=swap'


# ───────────────────────── colour: the reference's relations (white page, deep panels, one bright accent) on the client's palette
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


def _best(on, a, b):
    return a if _con(a, on) >= _con(b, on) else b


def _raise(tx, on, t, floor=4.6):
    """tx at strength t over `on`, strengthened until it reads at `floor`"""
    while _con(_mix(tx, on, t), on) < floor and t < 1:
        t += .02
    return _mix(tx, on, min(t, 1))


def _theme(p):
    bg, ink, acc = p.get('ground') or '#ffffff', p.get('ink') or '#052424', p.get('accent') or p.get('ink') or '#052424'
    light, dark = (bg, ink) if _lum(bg) >= _lum(ink) else (ink, bg)
    is_dark = bg == dark
    card = _mix(ink, bg, .06)
    grey = _mix(ink, bg, .24)
    panel = ink
    if is_dark:
        panel = _mix(ink, bg, .10)
        for c in p.get('extra') or []:
            try:
                if _lum(c) < .12 and _con(c, bg) >= 1.25:
                    panel = c
                    break
            except ValueError:
                continue
    ptx = _best(panel, light, dark)
    v = {
        'bg': bg, 'ink': ink, 'light': light, 'dark': dark, 'card': card, 'grey': grey,
        'mute': _raise(ink, card, .70), 'faint': _raise(ink, bg, .45, 3.1), 'line': _mix(ink, bg, .20),
        'soft': 'rgba(%d,%d,%d,%s)' % (_rgb(ink) + ('.08' if is_dark else '.05',)),
        'acc': acc, 'acctx': _best(acc, ink, bg), 'accon': acc if _con(acc, bg) >= 3 else ink,
        'panel': panel, 'ptx': ptx, 'pmute': _raise(ptx, panel, .60), 'pline': 'rgba(%d,%d,%d,.2)' % _rgb(ptx),
        'psoft': 'rgba(%d,%d,%d,.15)' % _rgb(ptx), 'pacc': acc if _con(acc, panel) >= 3 else ptx,
        'fill': dark, 'filltx': acc if _con(acc, dark) >= 4.5 else light,
        'bar': 'rgba(%d,%d,%d,.7)' % _rgb(dark), 'darka': '%d,%d,%d' % _rgb(dark), 'lighta': '%d,%d,%d' % _rgb(light),
    }
    return ';'.join('--%s:%s' % kv for kv in v.items())


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def m(p):
    """media paths in the data are relative to templates/; a page in <slug>/out/ reaches them two levels up"""
    p = str(p or '')
    return p if re.match(r'^(https?:)?//|^data:', p) else '../../' + p


def img(o, cls='', lazy=True, alt=None, slot=''):
    wh = ' width="%s" height="%s"' % (e(o['w']), e(o['h'])) if o.get('w') and o.get('h') else ''
    return '<img class="%s" src="%s" alt="%s"%s%s%s decoding="async">' % (
        cls, e(m(o.get('src'))), e(o.get('alt', '') if alt is None else alt), wh, ' loading="lazy"' if lazy else '',
        ' data-slot="%s"' % slot if slot else '')


def btn(link, kind='', cls=''):
    if not link or not link.get('t'):
        return ''
    return '<a class="btn %s %s" href="%s"><span>%s</span></a>' % (kind, cls, e(link.get('h') or '#'), e(link['t']))


def _sh(n=8):
    return [(i / n, (i / n) ** 2 * (3 - 2 * i / n)) for i in range(n + 1)]


def notch(top=None, bottom=None, left=None):
    """a clip polygon with tab-shaped notches: each edge takes (from, to, depth px, shoulder run px); from/to are CSS lengths"""
    P = ['0 0']
    if top:
        a, b, dp, run = top
        P += ['calc(%s + %.1fpx) %.1fpx' % (a, run * t, dp * s) for t, s in _sh()]
        P += ['calc(%s - %.1fpx) %.1fpx' % (b, run * t, dp * s) for t, s in reversed(_sh())]
    P += ['100% 0', '100% 100%']
    if bottom:
        a, b, dp, run = bottom
        P += ['calc(%s - %.1fpx) calc(100%% - %.1fpx)' % (b, run * t, dp * s) for t, s in _sh()]
        P += ['calc(%s + %.1fpx) calc(100%% - %.1fpx)' % (a, run * t, dp * s) for t, s in reversed(_sh())]
    P += ['0 100%']
    if left:
        a, b, dp, run = left
        P += ['%.1fpx calc(%s - %.1fpx)' % (dp * s, b, run * t) for t, s in _sh()]
        P += ['%.1fpx calc(%s + %.1fpx)' % (dp * s, a, run * t) for t, s in reversed(_sh())]
    return 'polygon(%s)' % ','.join(P)


def made(d, kind):
    x = ((d.get('media') or {}).get('made') or {}).get(kind)
    if isinstance(x, dict):
        return [x]
    return [o for o in x or [] if o.get('src')]


def by_tone(pics, want=None):
    """pictures of one tone (the wanted one, else the commoner one), order kept"""
    if not pics:
        return [], want or 'dark'
    if want and any(o.get('tone') == want for o in pics):
        return [o for o in pics if o.get('tone') == want], want
    n = sum(1 for o in pics if o.get('tone') == 'dark')
    tone = 'dark' if n * 2 >= len(pics) else 'light'
    return [o for o in pics if o.get('tone', 'dark') == tone], tone


def series(d):
    """the page's one picture family: the landscape series in the page's own tone (never a light picture as a large
    ground on a dark page), in the walk's order"""
    land = made(d, 'land')
    p = d.get('palette') or {}
    page = 'dark' if _lum(p.get('ground') or '#ffffff') < .45 else 'light'
    pool = [land[i] for i in (1, 3, 4, 5, 2, 0) if i < len(land)]
    same = [o for o in pool if o.get('tone', 'dark') == page]
    return (same or ([] if page == 'dark' else pool)), page


def brand_mark(d, lazy=False):
    b = d.get('brand') or {}
    logo = ''
    if b.get('logo'):
        wm = bool(b.get('logo_wordmark'))
        logo = '<img src="%s" alt="%s"%s%s>' % (e(m(b['logo'])), e(b.get('name', '')) if wm else '', ' class="wm"' if wm else '', ' loading="lazy"' if lazy else '')
    name = '' if b.get('logo_wordmark') and b.get('logo') else '<span>%s</span>' % e(b.get('name', ''))
    return '<a class="logo" href="%s">%s%s</a>' % (e(b.get('home') or '#'), logo, name)


# ───────────────────────── sections, in the reference's order
def s_header(d):
    nav = [n for n in d.get('nav') or [] if n.get('t')]
    cta, signin = d.get('cta') or {}, d.get('signin') or {}
    items = ''.join('<li><a class="ni" href="%s">%s</a></li>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav)
    navp = '<nav class="nav" aria-label="Primary"><ul>%s</ul></nav>' % items if items else ''
    acts = btn(cta, 'acc sm') + btn(signin, 'paper sm')
    mlinks = ''.join('<a class="ni" href="%s">%s</a>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav)
    menu = mnav = ''
    if mlinks or acts:
        menu = '<button class="menu" type="button" aria-expanded="false" aria-controls="mnav" aria-label="Menu"><i></i><i></i></button>'
        mnav = '<div class="mnav" id="mnav" hidden>%s<div class="mb">%s</div></div>' % (mlinks, acts)
    return '<header class="hd"><div class="bar">%s%s<div class="acts">%s</div>%s%s</div></header>' % (brand_mark(d), navp, acts, menu, mnav)


def s_open(d):
    h = d.get('hero') or {}
    lines = [x for x in (h.get('title'), h.get('text'), h.get('text2')) if x]
    if not h.get('title'):
        return ''
    land = made(d, 'land')
    pool = [land[i] for i in (0, 2, 5, 1, 3, 4) if i < len(land)] + made(d, 'sky')
    pics, _ = by_tone(pool, 'dark')
    scenes = ''
    for i, t in enumerate(lines):
        pic = img(pics[i % len(pics)], 'bgp', lazy=i > 0, alt='', slot='opening-backdrop') if pics else ''
        tag = 'h1' if i == 0 else 'p'
        scenes += '<div class="scene%s">%s<div class="veil"></div><%s class="st%s">%s</%s></div>' % (
            ' on' if i == 0 else '', pic, tag, ' long' if len(t) > 70 else '', e(t), tag)
    return '<section class="open" data-n="%d" style="--n:%d"><div class="pin">%s</div><div class="sep" aria-hidden="true"></div></section>' % (len(lines), len(lines), scenes)


def s_logos(d):
    logos = [x for x in d.get('logos') or [] if x]
    if not logos:
        return ''
    cells = ''
    for x in logos:
        o = x if isinstance(x, dict) else {'src': x}
        cells += '<li>%s</li>' % img(o, 'lg', alt=o.get('alt', ''))
    return '<section class="lgs"><ul class="lgrid">%s</ul></section>' % cells


def s_cards(d):
    s = d.get('steps') or {}
    items = [x for x in s.get('items') or [] if x.get('title')]
    if not items:
        return ''
    ser, _ = series(d)
    cards = ''
    for i, x in enumerate(items):
        media = ''
        if x.get('img'):
            # one landscape, held quiet toward the card, in three crops — not a different picture behind each device
            g = ser[0] if ser else None
            ground = (img(g, 'tg', alt='', slot='card-ground').replace('<img ', '<img style="object-position:%d%% 60%%" ' % (0, 50, 100)[i % 3], 1)
                      + '<div class="tv"></div>') if g else ''
            media = '<div class="tile %s">%s<img class="ti" src="%s" alt="" loading="lazy" decoding="async"></div>' % (e(x.get('shape') or ''), ground, e(m(x['img'])))
        cards += '<article class="pc"><div class="pt"><p class="eb mono">%02d%s</p><h3>%s</h3>%s</div>%s%s</article>' % (
            i + 1, ' ' + e(x['k']) if x.get('k') else '', e(x['title']), '<p class="pd">%s</p>' % e(x['text']) if x.get('text') else '',
            media, btn(x.get('cta'), 'soft wide'))
    head = '<h2 class="t70 aw">%s</h2>' % e(s['title']) if s.get('title') else ''
    return '<section class="pg"><div class="pgi">%s</div><div class="pgg n%d">%s</div></section>' % (head, min(len(items), 3), cards)


def s_calc(d):
    st = d.get('statement') or {}
    figs = [f for f in d.get('figures') or [] if f.get('v')]
    trust = [t for t in d.get('trust') or [] if t]
    if not (st.get('title') or figs):
        return ''
    head = '<div class="intro"><h2 class="t70 aw">%s</h2></div>' % e(st['title']) if st.get('title') else ''
    left = ''
    if st.get('text'):
        left += '<p class="lead">%s</p>' % e(st['text'])
    if trust:
        left += '<ul class="rows">%s</ul>' % ''.join('<li>%s</li>' % e(t) for t in trust)
    right = ''
    if figs:
        f0, rest = figs[0], figs[1:]
        rows = ''.join('<div class="rr"><dt>%s</dt><dd>%s</dd></div>' % (e(f.get('l', '')), e(f['v'])) for f in rest)
        right = '<div class="res%s"><div class="resin"><p class="amt">%s</p>%s%s%s</div></div>' % ('' if rest else ' thin',
            e(f0['v']), '<p class="amtl">%s</p>' % e(f0['l']) if f0.get('l') else '', '<dl class="brk">%s</dl>' % rows if rows else '',
            btn(d.get('cta'), 'paper wide big'))
    if not (left or right):
        return '<section class="calc">%s</section>' % head
    return '<section class="calc">%s<div class="cg%s">%s%s</div></section>' % (
        head, '' if left and right else ' one', '<div class="cleft">%s</div>' % left if left else '', right)


def s_feats(d):
    f = d.get('features') or {}
    items = [x for x in f.get('items') or [] if x.get('t')]
    if not (f.get('title') or items):
        return ''
    head = ''
    if f.get('title') or f.get('text'):
        head = '<div class="intro">%s%s</div>' % ('<h2 class="t70 aw">%s</h2>' % e(f['title']) if f.get('title') else '',
                                                 '<p class="ip">%s</p>' % e(f['text']) if f.get('text') else '')
    if not items:
        return '<section class="fsec">%s</section>' % head
    pics, tone = series(d)
    bgs = ''.join(img(o, 'fb' + (' on' if i == 0 else ''), alt='', slot='steps-backdrop') for i, o in enumerate(pics))
    lis = ''.join('<li class="fi"><strong>%s</strong>%s</li>' % (e(x['t']), '<span class="fx">%s</span>' % e(x['d']) if x.get('d') else '') for x in items)
    odo = '<div class="odo mono" aria-hidden="true"><span>0</span><span class="ov"><span class="os">%s</span></span></div>' % ''.join('<b>%d</b>' % ((i + 1) % 10) for i in range(len(items)))
    return ('<section class="fsec">%s<div class="fst %s%s" data-slot="steps-backdrop"><div class="fbg">%s<div class="fveil"></div></div>'
            '<div class="fcol">%s<ol class="fl">%s</ol><div class="fprog" aria-hidden="true"><i></i></div></div></div></section>') % (
        head, tone if pics else 'plain', '' if pics else ' nopic', bgs, odo, lis)


def s_car(d):
    links = [x for x in d.get('links') or [] if x.get('t')]
    if not links:
        return ''
    md = d.get('media') or {}
    screens = [s for s in md.get('screens') or [] if s.get('src')]
    ser, page = series(d)
    blur = ser[::-1]
    tabs = cards = ''
    for i, x in enumerate(links):
        on = ' on' if i == 0 else ''
        tabs += '<button class="tab mono%s" type="button" role="tab" aria-selected="%s" data-i="%d">%s</button>' % (on, 'true' if i == 0 else 'false', i, e(x['t']))
        g = blur[i % len(blur)] if blur else None
        ground = '<div class="cgd">%s<div class="cv"></div></div>' % img(g, 'cgi', alt='', slot='card-ground') if g else '<div class="cgd flat"></div>'
        scr = '<div class="cs">%s</div>' % img(screens[i], 'csi') if i < len(screens) else ''
        cards += ('<li class="cd %s%s" data-i="%d">%s<div class="cc"><div class="ctop"><span class="cl mono">%s</span>%s</div>%s<div class="cb">%s</div></div></li>') % (
            (g or {}).get('tone', 'dark'), on, i, ground, e(x['t']), '<h3 class="ct">%s</h3>' % e(x['d']) if x.get('d') else '', scr,
            btn({'t': x['t'], 'h': x.get('h')}, 'paper big'))
    arrows = ''
    if len(links) > 1:
        ar = '<svg viewBox="0 0 14 14" width="14" height="14" aria-hidden="true"><path d="M5 2.5 9.5 7 5 11.5" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
        arrows = '<div class="arr"><button class="ab prev" type="button" aria-label="Previous" disabled>%s</button><button class="ab next" type="button" aria-label="Next">%s</button></div>' % (ar, ar)
    return '<section class="car"><div class="tw"><div class="tabs" role="tablist">%s</div>%s</div><ul class="cw">%s</ul></section>' % (tabs, arrows, cards)


def s_quote(d):
    qs = [q for q in d.get('quotes') or [] if q]
    if not qs:
        return ''
    q = qs[0]
    q = q if isinstance(q, dict) else {'text': q}
    text = q.get('text') or q.get('quote') or q.get('q')
    if not text:
        return ''
    land = made(d, 'land')
    pics, _ = by_tone([land[i] for i in (5, 0, 2) if i < len(land)], 'dark')
    who = ''.join('<p>%s</p>' % e(q[k]) for k in ('name', 'author', 'role', 'company') if q.get(k))
    return '<section class="qt">%s<div class="veil"></div><blockquote><p class="qq">%s</p>%s</blockquote></section>' % (
        img(pics[0], 'bgp', alt='', slot='quote-backdrop') if pics else '', e(text), '<footer>%s</footer>' % who if who else '')


def s_plans(d):
    p = d.get('plans') or {}
    items = [x for x in p.get('items') or [] if x.get('name')]
    if not items:
        return ''
    cards = ''
    for x in items:
        rows = ''.join('<li>%s</li>' % e(r) for r in x.get('rows') or [])
        price = ''
        if x.get('price'):
            price = '<p class="pp">%s%s</p>' % (e(x['price']), ' <span>%s</span>' % e(x['per']) if x.get('per') else '')
        cards += '<article class="pl"><p class="pn mono">%s</p>%s%s%s%s</article>' % (
            e(x['name']), price, '<p class="pline">%s</p>' % e(x['line']) if x.get('line') else '',
            '<ul class="prow">%s</ul>' % rows if rows else '', btn(x.get('cta'), ('acc' if x.get('marked') else 'paper') + ' wide big'))
    head = '<h2 class="t48 aw">%s</h2>' % e(p['title']) if p.get('title') else ''
    note = '<p class="pnote">%s</p>' % e(p['note']) if p.get('note') else ''
    if len(items) == 1:
        info = ('<p class="pi">%s</p>' % e(p['text']) if p.get('text') else '') + note
        body = '<div class="plg solo"><div class="pinfo">%s</div>%s</div>' % (info, cards)
        return '<section class="pls">%s%s</section>' % (head, body)
    lead = '<p class="ip">%s</p>' % e(p['text']) if p.get('text') else ''
    return '<section class="pls"><div class="plh">%s%s</div><div class="plg n%d">%s</div>%s</section>' % (head, lead, min(len(items), 3), cards, note)


def s_faq(d):
    f = d.get('faq') or {}
    items = [x for x in f.get('items') or [] if x.get('q') and x.get('a')]
    if not items:
        return ''
    plus = '<svg class="pls-i" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M12 0v24M0 12h24" fill="none" stroke="currentColor" stroke-width="2.2"/></svg>'
    rows = ''.join('<details class="qa"><summary><span>%s</span>%s</summary><div class="an"><p>%s</p></div></details>' % (e(x['q']), plus, e(x['a'])) for x in items)
    return '<section class="fq"><div class="fqg"><div class="fqh">%s</div><div class="fqa">%s</div></div></section>' % (
        '<h2 class="aw">%s</h2>' % e(f['title']) if f.get('title') else '', rows)


def s_foot(d):
    c, f = d.get('close') or {}, d.get('foot') or {}
    nav = [n for n in d.get('nav') or [] if n.get('t')]
    seen = set((n['t'], n.get('h')) for n in nav)
    links = [n for n in d.get('links') or [] if n.get('t') and (n['t'], n.get('h')) not in seen]
    seen |= set((n['t'], n.get('h')) for n in links)
    acct = [n for n in (d.get('signin'), d.get('cta')) if n and n.get('t') and (n['t'], n.get('h')) not in seen]

    def col(xs):
        return '<ul class="fc">%s</ul>' % ''.join('<li><a href="%s">%s</a></li>' % (e(n.get('h') or '#'), e(n['t'])) for n in xs) if xs else ''
    top = ''
    if c.get('title'):
        top = '<div class="fh"><h2 class="t70 aw">%s</h2>%s%s</div>' % (e(c['title']), '<p class="ftx">%s</p>' % e(c['text']) if c.get('text') else '', btn(c.get('cta'), 'glass big'))
    legal = ''.join('<a href="%s">%s</a>' % (e(n.get('h') or '#'), e(n['t'])) for n in f.get('links') or [] if n.get('t'))
    bar = ''
    if f.get('legal') or legal:
        bar = '<div class="fb2"><p>%s</p>%s</div>' % (e(f.get('legal', '')), '<p class="fll">%s</p>' % legal if legal else '')
    return ('<footer class="ft%s">%s<div class="fg"><div class="flg">%s%s</div><div class="fcs">%s%s</div><div class="fct">%s</div></div>%s</footer>') % (
        '' if top else ' notop', top, brand_mark(d, True), '<p class="fnote">%s</p>' % e(f['text']) if f.get('text') else '', col(nav), col(links), col(acct), bar)


CSS = r"""
*,*::before,*::after{box-sizing:border-box}html{-webkit-text-size-adjust:100%;interpolate-size:allow-keywords}
body{margin:0;background:var(--bg);color:var(--ink);font:400 16px/1.5 Geist,'Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:clip}
h1,h2,h3,p,ul,ol,dl,dd,blockquote{margin:0;padding:0}ul,ol{list-style:none}a{color:inherit;text-decoration:none}img{max-width:100%;height:auto;display:block}button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}
:focus-visible{outline:2px solid var(--accon);outline-offset:3px;border-radius:4px}.hd :focus-visible,.open :focus-visible,.ft :focus-visible,.res :focus-visible,.pl :focus-visible,.cd :focus-visible{outline-color:var(--lighta-c,#fff)}
.mono{font-family:'Geist Mono',ui-monospace,Menlo,monospace;text-transform:uppercase;letter-spacing:.18em;font-weight:600}
.t70{font-size:70px;line-height:1;letter-spacing:-.05em;font-weight:400;text-align:center;text-wrap:balance}
.t48{font-size:48px;line-height:1.05;letter-spacing:-.018em;font-weight:400;text-align:center;text-wrap:balance}
/* words of a heading come up from pale to ink, one after another, when it enters (set by script; plain without it) */
.aw .w{transition:color .45s cubic-bezier(.39,.575,.565,1);transition-delay:calc(var(--i)*45ms)}.aw.wait .w{color:var(--faint);transition:none}
/* buttons: r8, mono 11; on hover a dark panel rises from below and the label takes the accent */
.btn{position:relative;display:inline-flex;align-items:center;justify-content:center;overflow:hidden;border-radius:8px;padding:25px 50px;min-height:59px;font:600 11px/1.2 'Geist Mono',ui-monospace,monospace;letter-spacing:.18em;text-transform:uppercase;text-align:center;transition:color .3s cubic-bezier(.39,.575,.565,1),transform .15s}
.btn::before{content:"";position:absolute;inset:0;background:var(--fill);transform:translateY(101%);transition:transform .3s cubic-bezier(.39,.575,.565,1)}.btn span{position:relative}
.btn:hover,.btn:focus-visible{color:var(--filltx)}.btn:hover::before,.btn:focus-visible::before{transform:none}.btn:active{transform:scale(.97)}
.btn.acc{background:var(--acc);color:var(--acctx)}.btn.paper{background:var(--light);color:var(--dark)}.btn.soft{background:var(--soft);color:var(--ink)}
.btn.glass{background:var(--psoft);color:var(--ptx);backdrop-filter:blur(27px)}.btn.acc:hover,.btn.paper:hover,.btn.soft:hover,.btn.glass:hover,.btn:focus-visible{color:var(--filltx)}
.btn.sm{padding:8px 21px;min-height:42px;font-size:11px;letter-spacing:.136em;max-width:170px}.btn.wide{display:flex;width:100%}.btn.big{min-height:60px}
/* header: a glass bar, fixed 46 from the top, centred */
.hd{position:fixed;top:46px;left:0;right:0;z-index:60;display:flex;justify-content:center;pointer-events:none;padding:0 20px}
.bar{pointer-events:auto;position:relative;display:flex;align-items:center;gap:24px;padding:18px;border-radius:8px;background:var(--bar);-webkit-backdrop-filter:blur(30px);backdrop-filter:blur(30px);color:var(--light);max-width:100%}
.logo{display:inline-flex;align-items:center;gap:8px;font-size:22px;font-weight:500;letter-spacing:-.04em;line-height:1;white-space:nowrap}.logo img{height:26px;width:auto;border-radius:6px}.logo img.wm{height:22px;border-radius:0;filter:brightness(0) invert(1)}
.nav ul{display:flex;align-items:center;gap:18px}.ni{position:relative;display:block;padding:14px 0;font-size:14px;line-height:1;font-weight:450;letter-spacing:.03em;white-space:nowrap;transition:color .3s cubic-bezier(0,0,.58,1)}
.nav .ni::after{content:"";position:absolute;left:-10px;top:50%;width:5px;height:5px;margin-top:-2.5px;border-radius:50%;background:var(--filltx);transform:scale(0);opacity:0;transition:transform .3s,opacity .3s}
.ni:hover{color:var(--filltx)}.nav .ni:hover::after{transform:none;opacity:1}
.acts{display:flex;gap:6px}.menu{display:none;width:44px;height:44px;margin:-10px -12px -10px auto;position:relative}.menu i{position:absolute;left:12px;right:12px;height:2px;background:currentColor;top:17px;transition:transform .3s}.menu i+i{top:25px}
.menu[aria-expanded=true] i{transform:translateY(4px) rotate(45deg)}.menu[aria-expanded=true] i+i{transform:translateY(-4px) rotate(-45deg)}
.mnav{position:absolute;left:0;right:0;top:calc(100% + 8px);border-radius:8px;background:rgba(var(--darka),.92);-webkit-backdrop-filter:blur(30px);backdrop-filter:blur(30px);padding:14px 26px 26px;display:flex;flex-direction:column}.mnav[hidden]{display:none}
.mnav .ni{padding:16px 0;font-size:16px;font-weight:500;letter-spacing:-.02em;border-bottom:1px solid rgba(var(--lighta),.16)}.mb{display:flex;flex-direction:column;gap:8px;margin-top:20px}.mb .btn{max-width:none;width:100%}
/* opening: three statements over a full-bleed picture. Plain: one screen each. With script: pinned, the statements are set letter by letter by the scroll */
.open{position:relative;background:var(--dark);color:var(--light);overflow:clip}
.scene{position:relative;min-height:100vh;min-height:100svh;display:flex;align-items:flex-end;justify-content:center;padding:160px 20px 134px;overflow:hidden}
.bgp{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(var(--darka),.34),rgba(var(--darka),.5) 45%,rgba(var(--darka),.72))}
.st{position:relative;max-width:900px;font-size:82.5px;line-height:.95;letter-spacing:-.018em;font-weight:400;text-align:center}.st.long{font-size:68px}
.st .wd{display:inline-block;white-space:nowrap}.st .c{transition:opacity .1s}.st .c.h{color:var(--filltx)}
.scrub .open{height:calc(100vh + var(--n)*66.7vh)}.scrub .pin{position:sticky;top:0;height:100vh;overflow:hidden}
.scrub .scene{position:absolute;inset:0;min-height:0;opacity:0;transition:opacity .7s cubic-bezier(0,0,.58,1)}.scrub .scene.on{opacity:1}.scrub .scene .bgp{transform:scale(var(--z,1));will-change:transform}.scrub .st .c{opacity:0}.scrub .st .c.s{opacity:1}
.sep{position:absolute;left:0;right:0;bottom:-1px;height:48px;background:var(--bg);z-index:3;clip-path:__SEP__}
/* logo wall */
.lgs{padding:40px 52px}.lgrid{display:grid;grid-template-columns:repeat(auto-fill,111px);justify-content:center}.lgrid li{height:111px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 .5px var(--line)}.lg{max-width:80px;max-height:44px;width:auto}
/* three cards */
.pg{padding:120px 70px 90px}.pgi{max-width:900px;margin:0 auto 72px}.pgg{display:grid;gap:24px;grid-template-columns:repeat(3,1fr)}.pgg.n2{grid-template-columns:repeat(2,1fr)}.pgg.n1{grid-template-columns:minmax(0,640px);justify-content:center}
.pc{display:flex;flex-direction:column;gap:32px;background:var(--card);border-radius:24px;padding:40px}.pt{flex:1}.eb{font-size:13px;line-height:.81;font-weight:400;color:var(--mute);margin-bottom:20px}
.pc h3{font-size:22.5px;line-height:1.46;letter-spacing:-.018em;font-weight:400;margin-bottom:16px}.pd{font-size:18px;line-height:1.4;letter-spacing:.02em;color:var(--mute)}
.tile{position:relative;aspect-ratio:334/300;border-radius:12px;border:1px solid var(--line);overflow:hidden;display:flex;align-items:center;justify-content:center;padding:22px;background:var(--bg)}
.tg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.tv{position:absolute;inset:0;background:var(--card);opacity:.5}.ti{position:relative;max-width:100%;max-height:100%;width:auto;height:auto;border-radius:6px;box-shadow:0 10px 30px rgba(0,0,0,.28)}.tile.phone .ti{border-radius:10px}
/* a centred heading with its paragraph */
.intro{padding:180px 70px 120px;text-align:center}.intro .t70{max-width:934px;margin:0 auto}.ip{max-width:880px;margin:54px auto 0;font-size:18px;line-height:1.4;letter-spacing:.02em;text-align:center}
/* statement, ruled rows, and the deep notched card with the figures */
.calc .intro{padding-bottom:120px}.cg{display:grid;grid-template-columns:1fr 1fr;gap:40px;padding:56px 70px}.cg.one{grid-template-columns:minmax(0,630px);justify-content:center}
.lead{font-size:23px;line-height:1.26;letter-spacing:-.01em;margin-bottom:28px}.rows{display:grid;grid-template-columns:1fr 1fr;gap:24px 37px}.rows li{padding:4px 0 12px;border-bottom:1px solid var(--line);font-size:16px;line-height:1.35;letter-spacing:.02em;color:var(--mute);display:flex;align-items:flex-end;min-height:64px}
.res{background:var(--panel);color:var(--ptx);border-radius:8px;min-height:600px;clip-path:__RES__}.resin{display:flex;flex-direction:column;height:100%;padding:74px 36px 36px 44px}
.res.thin{min-height:340px}
.amt{font-size:44px;line-height:1.2;letter-spacing:-.014em}.amtl{font-size:20px;line-height:1.26;letter-spacing:-.015em;color:var(--pmute);margin-top:8px;max-width:440px}
.brk{margin-top:50px;display:flex;flex-direction:column}.rr{display:flex;justify-content:space-between;align-items:baseline;gap:24px;padding:9px 0}.rr dt{font-size:16px;line-height:1.35;letter-spacing:-.019em;color:var(--pmute)}.rr dd{font-size:22px;line-height:1.46;letter-spacing:-.018em;white-space:nowrap}
.res .btn{margin-top:auto}.resin .brk+.btn,.resin .amtl+.btn,.resin .amt+.btn{margin-top:auto}.resin>.btn{transform-origin:center}.brk{margin-bottom:36px}.amtl:last-child,.amt:last-child{margin-bottom:0}
/* features: a pinned picture across the section, the list walks over it and each entry lights as it is read */
.fsec .intro{padding-bottom:110px}.fst{position:relative;display:grid;margin:0 17px;padding-bottom:0}.fbg{grid-area:1/1;position:sticky;top:35px;height:calc(100vh - 70px);border-radius:10px;overflow:hidden;background:var(--panel)}
.fb{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .5s cubic-bezier(0,0,.58,1)}.fb.on{opacity:1}
.fveil{position:absolute;inset:0}.fst.dark .fveil{background:linear-gradient(90deg,rgba(var(--darka),.86),rgba(var(--darka),.8) 42%,rgba(var(--darka),.3) 78%,rgba(var(--darka),.18))}.fst.light .fveil{background:linear-gradient(90deg,rgba(var(--lighta),.9),rgba(var(--lighta),.84) 42%,rgba(var(--lighta),.3) 78%,rgba(var(--lighta),.14))}
.fst.dark,.fst.plain{color:var(--light)}.fst.light{color:var(--dark)}.fst.plain{color:var(--ptx)}
.fcol{grid-area:1/1;position:relative;z-index:1;padding:240px 0 calc(50vh - 120px) 148px;max-width:640px}.fl{display:flex;flex-direction:column;gap:344px}
.fi{font-size:34.5px;line-height:1.2;letter-spacing:-.018em;font-weight:450;max-width:435px}.fi strong{display:block;font-weight:600;margin-bottom:41px}.fx{display:block}.fi .wd{display:inline-block;white-space:nowrap}
.lit .fi .c{opacity:.5;transition:opacity .4s}.lit.light .fi .c{opacity:.7}.lit .fi .c.s{opacity:1}
.odo{position:sticky;top:50vh;float:left;margin-left:-31px;display:flex;font-size:9.75px;line-height:28px;height:28px;letter-spacing:0;opacity:.75}.odo span{display:block;width:8px;text-align:center}.ov{height:28px;overflow:hidden}.os{display:block!important;transition:transform .5s cubic-bezier(.19,1,.22,1);transform:translateY(calc(var(--k,0)*-28px))}.os b{display:block;height:28px;font-weight:600}
.fprog{display:none}
/* the row of cards: one open at 890, the others closed at 580; tabs and arrows open the next */
.car{padding:82px 0 94px;display:flex;flex-direction:column;gap:48px}.tw{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:0 52px}
.tabs{display:flex;gap:12px;overflow-x:auto;scrollbar-width:none;padding:3px}.tabs::-webkit-scrollbar,.cw::-webkit-scrollbar{display:none}
.tab{height:58px;padding:12px 18px;border-radius:8px;border:1px solid var(--line);font-size:13px;line-height:.81;color:var(--mute);white-space:nowrap;transition:background-color .3s cubic-bezier(.39,.575,.565,1),color .3s,border-color .3s}.tab.on{background:var(--soft);border-color:transparent;color:var(--ink)}.tab:hover{color:var(--ink)}.tab:active,.ab:active{transform:scale(.97)}
.arr{display:flex;gap:12px}.ab{width:58px;height:58px;border-radius:8px;background:var(--soft);display:flex;align-items:center;justify-content:center;transition:background-color .25s,color .25s}.ab.prev svg{transform:rotate(180deg)}.ab:hover:not(:disabled){background:var(--fill);color:var(--filltx)}.ab:disabled{background:var(--grey);cursor:default}
.cw{display:flex;gap:20px;padding:0 52px;overflow-x:auto;scrollbar-width:none;scroll-padding:0 52px}
.cd{position:relative;flex:none;width:890px;height:725px;border-radius:20px;overflow:hidden;background:var(--grey);transition:width .6s cubic-bezier(.19,1,.22,1),color .2s ease-in-out}.cd.dark{color:var(--light)}.cd.light{color:var(--dark)}
.cgd{position:absolute;inset:0;transition:opacity .9s cubic-bezier(.19,1,.22,1),transform 1.2s cubic-bezier(.19,1,.22,1)}.cgd.flat{background:var(--panel)}.cd:has(.cgd.flat){color:var(--ptx)}
.cgi{position:absolute;inset:-40px;width:calc(100% + 80px);max-width:none;height:calc(100% + 80px);object-fit:cover;filter:blur(18px)}.cv{position:absolute;inset:0}.cd.dark .cv{background:rgba(var(--darka),.5)}.cd.light .cv{background:rgba(var(--lighta),.62)}
.cc{position:relative;height:100%;display:flex;flex-direction:column;gap:24px;padding:80px 82px 28px 60px}.ctop{display:flex;flex-direction:column;gap:14px}.cl{font-size:13px;line-height:.81;opacity:.8}.ct{font-size:46px;line-height:1.2;letter-spacing:-.01em;font-weight:400;max-width:748px}
.cs{flex:1;min-height:0;width:748px;max-width:calc(100vw - 180px);transition:opacity .6s .25s}.csi{max-height:100%;max-width:100%;width:auto;height:auto;border-radius:8px;box-shadow:0 14px 40px rgba(0,0,0,.3)}
.cb{display:flex;justify-content:flex-end;margin-top:auto;transition:opacity .6s .25s}.cb .btn{min-width:210px}
/* closed cards exist only when the script runs; without it every card stands open and the row scrolls */
@media (min-width:901px){.js .cd:not(.on){width:580px;cursor:pointer;color:var(--ink)}.js .cd:not(.on) .cgd{opacity:0;transform:scale(1.2)}.js .cd:not(.on) .cs,.js .cd:not(.on) .cb{opacity:0;visibility:hidden;transition:opacity .2s}
.js .cd:not(.on):hover .cgd{opacity:1;transform:none}.js .cd.dark:not(.on):hover{color:var(--light)}.js .cd.light:not(.on):hover{color:var(--dark)}.js .cd:not(.on):has(.cgd.flat):hover{color:var(--ptx)}}
/* quotation over a picture */
.qt{position:relative;min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--dark);color:var(--light);padding:120px 20px;clip-path:__QT__}.qt blockquote{position:relative;max-width:852px;text-align:center}.qq{font-size:34.5px;line-height:.96;letter-spacing:-.018em;margin-bottom:64px}.qt footer{font-size:17.25px;line-height:1.26;font-weight:450}
/* plans, on the build of the reference's contact block: a two-line 48 heading, deep cards r17 with ruled rows */
.pls{padding:80px 70px;display:flex;flex-direction:column;gap:56px}.plh .ip{margin-top:28px}.plg{display:grid;gap:40px;grid-template-columns:repeat(2,1fr)}.plg.n3{grid-template-columns:repeat(3,1fr);gap:24px}.plg.solo{align-items:start}.plg.solo .pl{max-width:540px;justify-self:center;width:100%}
.pl{display:flex;flex-direction:column;background:var(--panel);color:var(--ptx);border-radius:17px;padding:48px;box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 30px 60px -30px rgba(0,0,0,.35)}
.pn{font-size:13px;line-height:.81;color:var(--pmute);margin-bottom:28px}.pp{font-size:44px;line-height:1.2;letter-spacing:-.014em}.pp span{font-size:20px;letter-spacing:-.015em;color:var(--pmute);margin-left:6px;white-space:nowrap}.pline{font-size:23px;line-height:1.26;letter-spacing:-.01em;margin-top:14px}
.prow{margin-top:26px}.prow li{padding:14px 0 14px;border-bottom:1px solid var(--pline);font-size:16px;line-height:1.35;letter-spacing:.02em}.pl .btn{margin-top:38px}.pl .pline+.btn,.pl .pp+.btn{margin-top:auto}.pl .pline{margin-bottom:38px}.pl .pline+.prow{margin-top:-12px}
.pinfo{padding:0 15px}.pi{font-size:23px;line-height:1.26;letter-spacing:-.01em;margin-bottom:24px}.pnote{font-size:18px;line-height:1.4;letter-spacing:.02em;color:var(--mute);max-width:880px;margin:0 auto;text-align:center}.pinfo .pnote{text-align:left;font-size:23px;line-height:1.26;letter-spacing:-.01em}
/* questions */
.fq{padding:90px 0}.fqg{display:grid;grid-template-columns:523fr 653fr;gap:124px;padding:0 70px}.fqh h2{font-size:34.5px;line-height:1.2;letter-spacing:-.018em;font-weight:400}
.qa{position:relative}.qa::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:linear-gradient(90deg,transparent,var(--accon),transparent);opacity:.75}
.qa summary{display:flex;justify-content:space-between;align-items:center;gap:18px;padding:32px 0;cursor:pointer;list-style:none;font-size:22.5px;line-height:1.46;letter-spacing:-.018em}.qa summary::-webkit-details-marker{display:none}
.pls-i{flex:none;transition:transform .3s cubic-bezier(.39,.575,.565,1)}.qa[open] .pls-i{transform:rotate(45deg)}.an{padding:0 32px 32px}.an p{font-size:18px;line-height:1.4;letter-spacing:.02em}
.qa::details-content{height:0;overflow:hidden;transition:height .35s cubic-bezier(.19,1,.22,1),content-visibility .35s allow-discrete}.qa[open]::details-content{height:auto}.qa[open] .an{animation:an .3s cubic-bezier(.39,.575,.565,1) both}@keyframes an{from{opacity:0;transform:translateY(-4px)}}
/* close and foot: one deep panel with a notch in its top edge */
.ft{background:var(--panel);color:var(--ptx);padding:230px 70px 20px;clip-path:__FT__}.ft.notop{padding-top:110px}.fh{display:flex;flex-direction:column;align-items:center;text-align:center}.fh .t70{line-height:.95;max-width:825px}.ftx{font-size:18px;line-height:1.4;letter-spacing:.02em;color:var(--pmute);max-width:560px;margin-top:28px}.fh .btn{margin-top:67px}.fh .ftx+.btn{margin-top:44px}
.fg{display:grid;grid-template-columns:548fr 438fr 314fr;gap:0;padding-top:225px}.ft.notop .fg{padding-top:0}.flg .logo{font-size:30px}.flg .logo img{height:37px}.flg .logo img.wm{height:30px}.fnote{font-size:13px;line-height:1.5;color:var(--pmute);max-width:423px;margin-top:60px}
.fcs{display:grid;grid-template-columns:1fr 1fr;gap:15px}.fc li{margin-bottom:6px}.fc a{display:inline-block;font-size:20px;line-height:1.46;letter-spacing:-.01em;transition:color .3s}.fc a:hover,.fll a:hover{color:var(--pacc)}
.fb2{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-top:95px;font-size:12px;line-height:1.24;letter-spacing:-.01em;color:var(--pmute)}.fll{display:flex;gap:18px}
@media (max-width:1180px){.nav{display:none}.pg,.intro,.cg,.pls{padding-left:40px;padding-right:40px}.fqg{gap:60px;padding:0 40px}.ft{padding-left:40px;padding-right:40px}.t70{font-size:56px}.st{font-size:68px}.st.long{font-size:56px}}
@media (max-width:900px){
.hd{top:25px}.bar{width:100%;padding:20px 26px;justify-content:space-between}.bar>.acts,.nav{display:none}.menu{display:block}.logo{font-size:20px}.logo img{height:24px}.logo img.wm{height:20px}
.t70{font-size:40px;letter-spacing:-.03em}.t48{font-size:40px;letter-spacing:-.02em}
.scene{padding:120px 20px 60px}.st{font-size:58px;letter-spacing:0;max-width:351px}.st.long{font-size:44px}.sep{clip-path:__SEPM__}
.pg{padding:90px 20px 60px}.pgi{margin-bottom:48px}.pgg,.pgg.n2{grid-template-columns:1fr;gap:20px}.pc{padding:32px}.pc h3{font-size:24px}.tile{aspect-ratio:286/260}
.intro{padding:100px 20px}.calc .intro,.fsec .intro{padding-bottom:60px}.ip{margin-top:32px}
.cg{grid-template-columns:1fr;gap:32px;padding:40px 20px 48px}.lead{font-size:20px}.rows{grid-template-columns:1fr;gap:16px}.rows li{min-height:0;padding-top:10px}.res{margin:0 -20px;border-radius:0;min-height:0;clip-path:__RESM__}.resin{padding:64px 20px 36px}.amt{font-size:40px}.amtl{font-size:16px}.brk{margin-top:36px}.rr{flex-direction:column;gap:2px;padding:8px 0}.rr dt{font-size:14px}.rr dd{font-size:20px;white-space:normal}
.fst{margin:0;display:block;border-radius:0;overflow:hidden}.fbg{position:absolute;inset:0;height:auto;top:0;border-radius:0}.fb{height:340px}.fst.dark .fbg{background:var(--dark)}.fst.light .fbg{background:var(--light)}
.fst.dark .fveil{background:linear-gradient(180deg,rgba(var(--darka),0),rgba(var(--darka),0) 150px,rgba(var(--darka),.9) 262px,rgba(var(--darka),1) 338px)}.fst.light .fveil{background:linear-gradient(180deg,rgba(var(--lighta),0),rgba(var(--lighta),0) 150px,rgba(var(--lighta),.9) 262px,rgba(var(--lighta),1) 338px)}
.fcol{padding:270px 0 48px;max-width:none}.odo{display:none}.fl{flex-direction:row;gap:0;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding:0 20px;scroll-padding:0 20px}.fl::-webkit-scrollbar{display:none}.fi{flex:none;width:298px;max-width:78vw;padding-right:30px;font-size:20px;letter-spacing:-.01em;font-weight:400;scroll-snap-align:start}.fi strong{margin-bottom:24px}.lit .fi .c,.lit.light .fi .c{opacity:1}
.fprog{display:block;margin:40px 20px 0;height:2px;background:rgba(127,127,127,.4)}.fprog i{display:block;height:100%;width:25%;background:currentColor;transform-origin:left;transition:width .3s}
.car{padding:64px 0 100px;gap:32px}.tw{padding:0;flex-direction:column;align-items:stretch}.tabs{padding:3px 20px}.arr{order:3;justify-content:flex-end;padding:0 20px}.car{display:flex}.car .tw{display:contents}.car .tabs{order:1}.car .cw{order:2}.car .arr{order:3}
.cw{gap:8px;padding:0 20px;scroll-snap-type:x mandatory;scroll-padding:0 20px}.cd{width:calc(100vw - 40px);height:auto;min-height:438px;scroll-snap-align:start;transition:none}
.cc{padding:24px;gap:24px}.ct{font-size:24px;line-height:1.46;letter-spacing:-.015em}.cs{width:auto;max-width:100%;flex:none}.csi{max-height:300px}.cb .btn{min-width:210px}
.qt{clip-path:none}.qq{font-size:32px}
.pls{padding:48px 20px;gap:32px}.plg,.plg.n3{grid-template-columns:1fr;gap:20px}.pl{padding:28px}.pp{font-size:40px}.pline{font-size:20px}.pnote{font-size:16px;text-align:left}.pinfo{padding:0}
.fq{padding:90px 0}.fqg{grid-template-columns:1fr;gap:40px;padding:0 20px}.fqh h2{font-size:32px}.qa summary{font-size:24px;padding:28px 0}.an{padding:0 0 28px}
.ft{padding:125px 20px 33px;clip-path:__FTM__}.fh .t70{font-size:30px;letter-spacing:-.01em}.fh .btn{margin-top:42px;width:100%;max-width:306px}.fg{grid-template-columns:1fr;gap:56px;padding-top:120px}.fnote{margin-top:32px}.fcs{grid-template-columns:1fr 1fr;gap:10px}.fb2{flex-direction:column;align-items:flex-start;margin-top:64px}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition-duration:.01ms!important;animation-duration:.01ms!important;transition-delay:0s!important}html{scroll-behavior:auto}}
"""

JS = r"""
(function(){var D=document,R=D.documentElement,rm=matchMedia('(prefers-reduced-motion:reduce)').matches,$=function(s,c){return [].slice.call((c||D).querySelectorAll(s))};
function split(el){var n=0;[].slice.call(el.childNodes).forEach(function(t){if(t.nodeType!==3)return;var f=D.createDocumentFragment();t.textContent.split(/(\s+)/).forEach(function(w){if(!w)return;if(/^\s+$/.test(w)){f.appendChild(D.createTextNode(' '));return}var s=D.createElement('span');s.className='wd';for(var i=0;i<w.length;i++){var c=D.createElement('span');c.className='c';c.textContent=w[i];s.appendChild(c);n++}f.appendChild(s)});el.replaceChild(f,t)});return n}
/* menu */
var mb=D.querySelector('.menu'),mn=D.getElementById('mnav');if(mb&&mn){mb.addEventListener('click',function(){var o=mb.getAttribute('aria-expanded')==='true';mb.setAttribute('aria-expanded',o?'false':'true');mn.hidden=o});D.addEventListener('keydown',function(e){if(e.key==='Escape'&&!mn.hidden){mn.hidden=true;mb.setAttribute('aria-expanded','false');mb.focus()}})}
/* headings: words come up one after another */
if(!rm&&'IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.remove('wait');io.unobserve(x.target)}})},{rootMargin:'0px 0px -12% 0px'});
$('.aw').forEach(function(h){var ws=h.textContent.split(/\s+/).filter(Boolean);h.setAttribute('aria-label',h.textContent);h.textContent='';ws.forEach(function(w,i){var s=D.createElement('span');s.className='w';s.style.setProperty('--i',i);s.textContent=w;s.setAttribute('aria-hidden','true');h.appendChild(s);if(i<ws.length-1)h.appendChild(D.createTextNode(' '))});h.classList.add('wait');io.observe(h)})}
/* opening: pinned; each statement is set letter by letter over two thirds of a screen, then taken away from its start */
var op=D.querySelector('.open'),sts=[];
if(op&&!rm){$('.st',op).forEach(function(s){s.setAttribute('aria-label',s.textContent);var k=split(s);$('.wd',s).forEach(function(w){w.setAttribute('aria-hidden','true')});sts.push({el:s,cs:$('.c',s),n:k,a:-1,b:-1,sc:s.parentNode})});R.classList.add('scrub')}
/* features: letters light as the entry is read; the picture and the counter follow the entry */
var fst=D.querySelector('.fst'),fis=[],fbs=[],os=null,cur=-1;
if(fst){fbs=$('.fb',fst);os=fst.querySelector('.os');$('.fi',fst).forEach(function(li){var cs=[];if(!rm){var t=li.querySelector('.fx');if(t){split(t);cs=$('.c',t)}}fis.push({el:li,cs:cs,k:-1})});if(!rm)fst.classList.add('lit')}
function setcur(i){if(i===cur)return;cur=i;if(fbs.length)fbs.forEach(function(b,j){b.classList.toggle('on',j===i%fbs.length)});if(os)os.style.setProperty('--k',i)}
var mq=matchMedia('(max-width:900px)'),tick=false;
function frame(){tick=false;var vh=innerHeight,y=scrollY;
 if(sts.length){var top=op.offsetTop,P=vh*.667,p=(y-top)/P,k=Math.max(0,Math.min(sts.length-1,Math.floor(p))),f=p-k;if(p<0)f=0;if(p>=sts.length)f=1;
  sts.forEach(function(s,i){var a=0,b=0;if(i===k){a=Math.round(Math.max(0,Math.min(1,(f-.17)/.55))*s.n);b=Math.round(Math.max(0,Math.min(1,(f-.76)/.24))*s.n)}
   if(a!==s.a||b!==s.b){for(var j=0;j<s.n;j++){var c=s.cs[j];c.classList.toggle('s',j<a&&j>=b);c.classList.toggle('h',j===a-1&&a<s.n)}s.a=a;s.b=b}
   s.sc.classList.toggle('on',i===k)});
  var tot=sts.length*P,z=Math.max(0,Math.min(1,(y-top)/tot)),over=Math.max(0,y-top-tot);op.style.setProperty('--z',(1+z*.1).toFixed(4));op.firstChild.style.transform=over?'translateY('+(over*.5).toFixed(1)+'px)':''}
 if(fis.length&&!mq.matches){var act=0;fis.forEach(function(it,i){var t=it.el.getBoundingClientRect().top,pr=Math.max(0,Math.min(1,(vh*.58-t)/(vh*.45)));if(i===0)pr=Math.max(0,Math.min(1,(vh*1.1-t)/(vh*.62)));if(pr>0)act=i;
   var n=Math.round(pr*it.cs.length);if(n!==it.k){for(var j=0;j<it.cs.length;j++)it.cs[j].classList.toggle('s',j<n);it.k=n}});setcur(act)}}
function req(){if(!tick){tick=true;requestAnimationFrame(frame)}}
addEventListener('scroll',req,{passive:true});addEventListener('resize',req);frame();
/* features on a phone: swiped sideways; the line below shows where you are */
var fl=D.querySelector('.fl'),fp=D.querySelector('.fprog i');if(fl&&fis.length){fl.addEventListener('scroll',function(){if(!mq.matches)return;var w=fis[0].el.offsetWidth||1,i=Math.max(0,Math.min(fis.length-1,Math.round(fl.scrollLeft/w)));setcur(i);if(fp)fp.style.width=((i+1)/fis.length*100)+'%'},{passive:true});if(fp)fp.style.width=(100/fis.length)+'%'}
/* cards: a tab, an arrow or a press on a closed card opens it and brings it to the left edge */
var cw=D.querySelector('.cw');if(cw){var cds=$('.cd',cw),tabs=$('.car .tab'),pv=D.querySelector('.ab.prev'),nx=D.querySelector('.ab.next'),ci=0;
 function go(i,foc){i=Math.max(0,Math.min(cds.length-1,i));ci=i;cds.forEach(function(c,j){c.classList.toggle('on',j===i)});tabs.forEach(function(t,j){t.classList.toggle('on',j===i);t.setAttribute('aria-selected',j===i?'true':'false')});if(pv)pv.disabled=i===0;if(nx)nx.disabled=i===cds.length-1;
  var pad=parseFloat(getComputedStyle(cw).paddingLeft)||0,gap=parseFloat(getComputedStyle(cw).columnGap)||0,x=0;for(var j=0;j<i;j++)x+=(mq.matches?cds[j].offsetWidth:580)+gap;cw.scrollTo({left:x,behavior:rm?'auto':'smooth'});if(tabs[i]&&tabs[i].scrollIntoView&&mq.matches)tabs[i].parentNode.scrollTo({left:tabs[i].offsetLeft-20,behavior:'smooth'})}
 tabs.forEach(function(t,i){t.addEventListener('click',function(){go(i)});t.addEventListener('keydown',function(e){if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();var n=Math.max(0,Math.min(tabs.length-1,i+(e.key==='ArrowRight'?1:-1)));tabs[n].focus();go(n)}})});
 cds.forEach(function(c,i){c.addEventListener('click',function(e){if(!c.classList.contains('on')&&!mq.matches){e.preventDefault();go(i)}})});
 if(pv)pv.addEventListener('click',function(){go(ci-1)});if(nx)nx.addEventListener('click',function(){go(ci+1)});
 cw.addEventListener('scroll',function(){if(!mq.matches)return;var w=cds[0].offsetWidth+8,i=Math.round(cw.scrollLeft/w);if(i!==ci){ci=i;tabs.forEach(function(t,j){t.classList.toggle('on',j===i);t.setAttribute('aria-selected',j===i?'true':'false')});if(pv)pv.disabled=i===0;if(nx)nx.disabled=i===cds.length-1}},{passive:true})}
})();
"""


def render(d: dict) -> str:
    b = d.get('brand') or {}
    hero = d.get('hero') or {}
    css = (CSS.replace('__SEP__', notch(top=('15.4%', '84.6%', 40, 60))).replace('__SEPM__', notch(top=('8%', '92%', 22, 34)))
           .replace('__RES__', notch(top=('47.2%', '92.8%', 30, 36), left=('43%', '77%', 30, 30))).replace('__RESM__', notch(top=('34%', '100% + 40px', 28, 34)))
           .replace('__QT__', notch(bottom=('15.4%', '84.6%', 20, 60)))
           .replace('__FT__', notch(top=('14.1%', '85.9%', 30, 96))).replace('__FTM__', notch(top=('8%', '92%', 20, 40))))
    body = ''.join(f(d) for f in (s_header, s_open, s_logos, s_cards, s_calc, s_feats, s_car, s_quote, s_plans, s_faq))
    title = e(b.get('name', '')) + (' — ' + e(hero['title']) if hero.get('title') else '')
    desc = e(hero.get('text') or hero.get('title') or '')
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="%s"><style>:root{%s}%s</style></head><body><script>document.documentElement.className+=" js"</script><main>%s</main>%s<script>%s</script></body></html>') % (
        e(d.get('lang') or 'en'), title, desc, FONTS, _theme(d.get('palette') or {}), css, body, s_foot(d), JS)
