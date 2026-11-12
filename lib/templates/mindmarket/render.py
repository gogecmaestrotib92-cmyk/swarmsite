"""mindmarket/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type, spacing, radii, motion, phone layout) was measured on the reference's
home page and, for plans / numbered tiles / questions, on its pricing page, at 1440 and 390 on 2026-11-12 (NOTES.md).
Nothing of the reference's code, words, pictures, illustrations, icons, logos or colours-as-a-brand is here. The
client's data fills it; a section whose data is missing is left out whole. No model call, no file read, no client logic.
"""
import html

FONTS = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap'


# ───────────────────────── colour: the reference's relations (accent field, quiet ground, lighter cards, a deeper block,
# a second strong field for the foot, coloured buttons) applied to the client's palette
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


def _field(c, ink, ground, floor=4.6):
    """a colour used as a field, and the text that reads on it: whichever of ink/ground reads better; the field is
    pushed away from that text until body text holds the floor."""
    tx = ink if _con(ink, c) >= _con(ground, c) else ground
    far = '#000000' if _lum(tx) > .5 else '#ffffff'
    n = 0
    while _con(tx, c) < floor and n < 20:
        c = _mix(far, c, .08)
        n += 1
    return c, tx


def _soft(tx, bg, t, floor=4.6):
    """text at t of its colour on bg (the reference's 60–80 % texts), raised until it reads"""
    while _con(_mix(tx, bg, t), bg) < floor and t < 1:
        t += .03
    return _mix(tx, bg, min(t, 1))


def _palette(d):
    p = d.get('palette') or {}
    g, ink, acc = p.get('ground') or '#f5f1e4', p.get('ink') or '#2c2e2a', p.get('accent') or '#2c2e2a'
    light = _lum(g) > .4
    card = _mix('#ffffff', g, 1.0 if _con('#ffffff', g) >= 1.06 else .0) if light else _mix(ink, g, .10)
    if light and card == g:
        card = _mix(ink, g, .05)
    deep = _mix(ink, g, .09) if light else _mix(ink, g, .045)
    acc, onacc = _field(acc, ink, g)
    cols = []
    for c in p.get('extra') or []:
        try:
            if _con(c, g) < 1.25 or _con(c, acc) < 1.15:
                continue
            cols.append(_field(c, ink, g))
        except ValueError:
            continue
    if not cols:
        cols = [(acc, onacc)]
    foot = cols[1 % len(cols)] if len(cols) > 1 else _field(_mix(ink, g, .88), ink, g)
    # the first number card is the card colour with its figure in a colour (the reference: white card, blue figure)
    stat = next((c for c in [p.get('accent') or acc] + [c for c, _ in cols] if _con(c, card) >= 4.5), ink)
    return {'g': g, 'ink': ink, 'card': card, 'deep': deep, 'acc': acc, 'onacc': onacc, 'cols': cols, 'foot': foot,
            'stat': stat, 'light': light, 'line': _mix(ink, g, .2),
            'soft': _soft(ink, card, .75), 'softg': _soft(ink, g, .75), 'softd': _soft(ink, deep, .8),
            'softf': _soft(foot[1], foot[0], .6)}


# ───────────────────────── small parts
def e(s):
    return html.escape(str(s or ''), quote=True)


def _nb(s):
    """escaped text in which a hyphenated word is kept on one line (a display line never breaks at its hyphen)"""
    return ' '.join('<span class="nb">%s</span>' % e(w) if '-' in w.strip('-') else e(w) for w in str(s or '').split(' '))


def _m(src):
    return '../../' + src if src and not src.startswith(('http:', 'https:', 'data:', '/')) else (src or '')


ARROW = ('<svg viewBox="0 0 20 20" width="1em" height="1em" aria-hidden="true" focusable="false"><path d="M8 5l5 5-5 5" '
         'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def _btn(link, bg, tx, disc, ondisc, cls=''):
    if not link or not link.get('t'):
        return ''
    st = '--bb:%s;--bt:%s;--bc:%s;--bi:%s' % (bg, tx, disc, ondisc)
    return ('<a class="btn %s" href="%s" style="%s"><span class="bi h" aria-hidden="true">%s</span><span class="bl">%s</span>'
            '<span class="bi d" aria-hidden="true">%s</span></a>') % (cls, e(link.get('h') or '#'), st, ARROW, e(link['t']), ARROW)


def _step(n, steps):
    """type steps down by length so a long line holds the reference's block"""
    for limit, v in steps:
        if n <= limit:
            return v
    return steps[-1][1]


def _find(d, src):
    m = d.get('media') or {}
    for k in ('phones', 'photos', 'screens'):
        for x in m.get(k) or []:
            if x.get('src') == src:
                return x
    return None


def _img(x, cls='', lazy=True):
    wh = (' width="%d" height="%d"' % (x['w'], x['h'])) if x.get('w') and x.get('h') else ''
    return '<img class="%s" src="%s" alt="%s"%s%s decoding="async">' % (cls, e(_m(x.get('src'))), e(x.get('alt')), wh,
                                                                     ' loading="lazy"' if lazy else '')


def _land(d, P, order):
    """one motif on the page — the landscape series. Picks by index in the given order; a large ground never takes a
    picture whose tone is against the page's (a light picture on a dark page, a dark one on a light page) while one of
    the page's own tone is there."""
    land = ((d.get('media') or {}).get('made') or {}).get('land') or []
    xs = [land[i] for i in order if i < len(land) and land[i].get('src')]
    want = 'light' if P['light'] else 'dark'
    own = [x for x in xs if x.get('tone') == want]
    if own:
        return own
    return [] if not P['light'] else xs


# ───────────────────────── sections
def _nav(d, P):
    b = d.get('brand') or {}
    logo = ''
    if b.get('logo'):
        logo = '<img src="%s" alt="%s" class="lg%s">' % (e(_m(b['logo'])), e(b.get('name')) if b.get('logo_wordmark') else '',
                                                        ' wm' if b.get('logo_wordmark') else '')
    name = '' if (b.get('logo') and b.get('logo_wordmark')) else '<span class="bn">%s</span>' % e(b.get('name'))
    links = list(d.get('nav') or [])
    if (d.get('signin') or {}).get('t'):
        links.append(d['signin'])
    li = ''.join('<li><a href="%s"><span>%s</span></a></li>' % (e(x.get('h') or '#'), e(x.get('t'))) for x in links if x.get('t'))
    cta = d.get('cta') or {}
    quote = _btn(cta, P['card'], P['ink'], P['acc'], P['onacc'], 'q') if cta.get('t') else ''
    mob = ''
    if li or quote:
        mob = ('<details class="mm"><summary aria-label="Menu"><span class="bg" aria-hidden="true"><i></i><i></i></span></summary>'
               '<div class="mp"><ul>%s</ul>%s</div></details>') % (li, _btn(cta, P['acc'], P['onacc'], P['card'], P['ink'], 'w') if cta.get('t') else '')
    return ('<header class="nav"><div class="bar"><a class="logo" href="%s">%s%s</a>%s%s</div>%s</header>'
            % (e(b.get('home') or '#'), logo, name, '<nav aria-label="Main"><ul>%s</ul></nav>' % li if li else '', mob, quote))


def _hero(d, P):
    h = d.get('hero') or {}
    if not h.get('title'):
        return ''
    n = len(h['title'])
    cls = _step(n, [(20, 't1'), (34, 't2'), (999, 't3')])
    tag = '<p class="tag rise r1">%s</p>' % e(h['kicker']) if h.get('kicker') else ''
    return ('<section class="hero"><div class="hpin"><div class="hstick"><div class="hc" data-hc>'
            '<h1 class="%s rise r2">%s</h1>%s</div></div></div></section>' % (cls, _nb(h['title']), tag))


def _timeline(d, P, used):
    h = d.get('hero') or {}
    m = d.get('media') or {}
    out = []
    # the picture that stands at the foot of the opening and stays while the panel slides over it
    pic = (m.get('screens') or [None])[0]
    intro_txt = ' '.join(x for x in (h.get('text'), h.get('text2')) if x)
    btn = _btn(h.get('primary') or d.get('cta'), P['card'], P['ink'], P['acc'], P['onacc'])
    pich = ''
    if pic and pic.get('w') and pic.get('h'):
        used.add(pic['src'])
        a = pic['w'] / pic['h']
        pich = ('<div class="pw" aria-hidden="false"><div class="ps"><div class="pp" data-pp data-slot="opening-picture" '
                'style="--a:%.4f">%s</div></div></div>' % (a, _img(pic, '', False)))
    if intro_txt or btn or pich:
        out.append('<div class="intro%s">%s<div class="wrap in"><div class="it">%s%s</div></div>%s</div>'
                   % ('' if pich else ' np', pich, '<p class="xs">%s</p>' % e(intro_txt) if intro_txt else '', btn,
                      '<div class="ghost"></div>' if pich else ''))
    items = [x for x in ((d.get('steps') or {}).get('items') or []) if x.get('title')]
    rows = []
    for i, it in enumerate(items):
        c, tx = P['cols'][i % len(P['cols'])]
        pos = ('r', 'l', 'c')[i % 3]
        pic = ''
        if it.get('img'):
            x = _find(d, it['img']) or {'src': it['img'], 'alt': ''}
            used.add(it['img'])
            pic = '<div class="tp %s" data-par="18" data-slot="step-picture">%s</div>' % (e(it.get('shape') or ''), _img(x, ''))
        cta = _btn(it.get('cta'), c, tx, P['card'], P['ink'])
        rows.append('<div class="row %s"><div class="tc" data-par="90"><div class="tile" data-in><span class="tb k" style="background:%s"></span>'
                    '<span class="tb w"></span><div class="ti"><h3>%s</h3>%s%s</div></div></div>%s</div>'
                    % (pos, c, e(it['title']), '<p>%s</p>' % e(it['text']) if it.get('text') else '',
                       '<div class="tcta">%s</div>' % cta if cta else '', pic))
    bg = ''
    if rows:
        # the story is carried by one picture of the series, pinned behind it while the tiles pass (the reference: an
        # illustrated path fills this whole section)
        bx = (_land(d, P, (1, 5, 2)) or [None])[0]
        if bx:
            bg = ('<div class="rbg" aria-hidden="true"><div class="rs"><img src="%s" alt="" width="%d" height="%d" loading="lazy" '
                  'decoding="async" data-slot="story-backdrop"></div></div>' % (e(_m(bx['src'])), bx.get('w') or 3, bx.get('h') or 2))
        out.append('<div class="wrap rows%s">%s%s</div>' % (' hb' if bg else '', bg, ''.join(rows)))
    if not out:
        return ''
    return '<section class="tl%s">%s</section>' % (' hb' if bg else '', ''.join(out))


def _callout(d, P):
    c = d.get('close') or {}
    if not c.get('title'):
        return ''
    cls = _step(len(c['title']), [(20, 't1'), (34, 't2'), (999, 't3')])
    trust = [t for t in (d.get('trust') or []) if t][:3]
    tr = '<ul class="three">%s</ul>' % ''.join('<li>%s</li>' % e(t) for t in trust) if len(trust) == 3 else ''
    return ('<section class="call"><div class="wrap"><h2 class="huge %s">%s</h2><div class="cb">%s%s</div>%s</div></section>'
            % (cls, _nb(c['title']), '<p class="xs">%s</p>' % e(c['text']) if c.get('text') else '',
               _btn(c.get('cta') or d.get('cta'), P['card'], P['ink'], P['acc'], P['onacc']), tr))


def _photo(d, P):
    land = ((d.get('media') or {}).get('made') or {}).get('land') or []
    if not land:
        return ''
    x = land[0]
    return ('<section class="photo" data-slot="band-picture" aria-hidden="true"><div class="pi" data-photo><img src="%s" alt="" '
            'width="%d" height="%d" loading="lazy" decoding="async"></div></section>' % (e(_m(x['src'])), x.get('w') or 16, x.get('h') or 9))


def _numbers(d, P):
    figs = [f for f in (d.get('figures') or []) if f.get('v')]
    if not figs:
        return ''
    s = d.get('statement') or {}
    left = ''
    if s.get('title') or s.get('text'):
        left = '<div class="nl"><div class="ns">%s%s</div></div>' % (
            '<h2 class="lg">%s</h2>' % e(s['title']) if s.get('title') else '',
            '<p class="md">%s</p>' % e(s['text']) if s.get('text') else '')
    fields = [(P['card'], P['stat'], P['stat'])] + [(P['acc'], P['onacc'], P['onacc'])] + [(c, t, t) for c, t in P['cols']]
    cards = []
    n = len(figs)
    for i, f in enumerate(figs):
        bg, st, tx = fields[i % len(fields)]
        if i % len(fields) == 0:
            tx = st if _con(st, bg) >= 4.5 else P['ink']
        size = _step(len(str(f['v'])), [(3, 's1'), (5, 's2'), (7, 's3'), (999, 's4')])
        cards.append('<div class="ni" style="--i:%d"><div class="nc" data-nc="%d" style="background:%s;color:%s">'
                     '<p class="stat %s" style="color:%s">%s</p>%s</div></div>'
                     % (i + 1, i, bg, tx, size, st, e(f['v']), '<p class="nd">%s</p>' % e(f['l']) if f.get('l') else ''))
    return ('<section class="nums%s" style="--n:%d"><div class="wrap ng">%s<div class="nlist">%s</div></div></section>'
            % ('' if left else ' solo', n, left, ''.join(cards)))


def _gallery(d, P, used):
    m = d.get('media') or {}
    made = m.get('made') or {}
    grounds = _land(d, P, (4, 3))[:1]
    port = [x for x in (m.get('phones') or []) + (m.get('photos') or []) if x.get('src') not in used and x.get('w') and x.get('h')]
    land = [x for x in (m.get('screens') or []) if x.get('src') not in used and x.get('w') and x.get('h')]
    v = m.get('video')
    picks = []
    if port:
        picks.append(port.pop(0))
    if v and v.get('src'):
        picks.append(dict(v, video=True))
    while len(picks) < 4 and (land or port):
        picks.append(land.pop(0) if land else port.pop(0))
    if not picks:
        return ''
    if len(picks) > 1 and picks[0]['w'] > picks[0]['h']:
        pass
    tiles = []
    for i, x in enumerate(picks):
        bg = ''
        if grounds:
            # one soft square of the series (the water surface) under every tile, in another crop each time, held quiet
            # toward the block's ground
            bx = grounds[i % len(grounds)]
            bg = ('<img class="gb" src="%s" alt="" width="%d" height="%d" loading="lazy" decoding="async" data-slot="tile-ground" '
                  'style="object-position:%s">' % (e(_m(bx['src'])), bx.get('w') or 1, bx.get('h') or 1, ('50% 50%', '50% 30%', '20% 80%', '80% 70%')[i % 4]))
        if x.get('video'):
            med = ('<video class="gm" src="%s" poster="%s" width="%d" height="%d" muted loop playsinline preload="none" data-auto '
                   'aria-label="%s"></video>' % (e(_m(x['src'])), e(_m(x.get('poster'))), x['w'], x['h'], e(x.get('alt'))))
        else:
            med = _img(x, 'gm')
        cap = '<figcaption>%s</figcaption>' % e(x['alt']) if x.get('alt') else ''
        tiles.append('<li class="g%d"><figure><div class="gt" style="--ma:%.4f">%s%s</div>%s</figure></li>'
                     % (i, x['w'] / x['h'], bg, med, cap))
    return '<div class="gal"><ul class="gl n%d">%s</ul></div>' % (len(picks), ''.join(tiles))


def _rails(d, P):
    logos = [x for x in (d.get('logos') or []) if x]
    if not logos:
        return ''

    def pill(x):
        if isinstance(x, dict):
            im = '<span class="rv"><img src="%s" alt="" loading="lazy"></span>' % e(_m(x['src'])) if x.get('src') else ''
            return '<div class="rp%s">%s<p>%s</p></div>' % ('' if im else ' nt', im, e(x.get('name') or x.get('alt')))
        return '<div class="rp nt"><p>%s</p></div>' % e(x)
    k = max(1, (len(logos) + 2) // 3) if len(logos) > 5 else len(logos)
    rows = [logos[i:i + k] for i in range(0, len(logos), k)][:3]
    out = ''
    for i, r in enumerate(rows):
        pat = ''.join(pill(x) for x in r)
        out += ('<div class="rail%s"><div class="rc" data-rail><div class="rpat">%s</div><div class="rpat" aria-hidden="true">%s</div>'
                '</div></div>' % (' rev' if i % 2 == 0 else '', pat * 3, pat * 3))
    return '<div class="rails">%s</div>' % out


def _features(d, P):
    f = d.get('features') or {}
    items = [x for x in (f.get('items') or []) if x.get('t')]
    if not items:
        return ''
    sq = [(P['acc'], P['onacc'])] + P['cols'] + [(P['deep'], P['ink'])]
    li = ''
    for i, x in enumerate(items):
        c, t = sq[i % len(sq)]
        li += '<li><span class="no" style="background:%s;color:%s">%d</span><h3>%s</h3>%s</li>' % (
            c, t, i + 1, e(x['t']), '<p>%s</p>' % e(x['d']) if x.get('d') else '')
    return ('<section class="feat"><div class="wrap">%s%s<ol class="fl">%s</ol></div></section>'
            % ('<h2 class="mdh">%s</h2>' % e(f['title']) if f.get('title') else '',
               '<p class="md fx">%s</p>' % e(f['text']) if f.get('text') else '', li))


def _plans(d, P):
    p = d.get('plans') or {}
    items = [x for x in (p.get('items') or []) if x.get('name')]
    if not items:
        return ''
    cards = ''
    cols = [(P['acc'], P['onacc'])] + P['cols']
    for i, x in enumerate(items):
        c, t = cols[i % len(cols)]
        rows = ''.join('<li>%s</li>' % e(r) for r in (x.get('rows') or []) if r)
        price = ''
        if x.get('price'):
            price = '<p class="pr"><b>%s</b>%s</p>' % (e(x['price']), '<span>%s</span>' % e(x['per']) if x.get('per') else '')
        cards += ('<article class="pc%s" style="--pk:%s"><h3>%s</h3>%s%s%s<div class="pb">%s</div></article>'
                  % (' mk' if x.get('marked') else '', c, e(x['name']), '<p class="pl">%s</p>' % e(x['line']) if x.get('line') else '',
                     price, '<ul>%s</ul>' % rows if rows else '', _btn(x.get('cta'), c, t, P['card'], P['ink'])))
    return ('<section class="plans"><div class="wrap">%s%s<div class="pg n%d">%s</div>%s</div></section>'
            % ('<h2 class="mdh">%s</h2>' % e(p['title']) if p.get('title') else '',
               '<p class="md fx">%s</p>' % e(p['text']) if p.get('text') else '', min(len(items), 3), cards,
               '<p class="pn">%s</p>' % e(p['note']) if p.get('note') else ''))


def _faq(d, P):
    f = d.get('faq') or {}
    items = [x for x in (f.get('items') or []) if x.get('q') and x.get('a')]
    if not items:
        return ''
    rows = ''.join('<details class="qa"><summary><span class="qt">%s</span><span class="qi" aria-hidden="true"></span></summary>'
                   '<div class="an"><p>%s</p></div></details>' % (e(x['q']), e(x['a'])) for x in items)
    return ('<section class="faq"><div class="wrap">%s<div class="ql">%s</div></div></section>'
            % ('<h2 class="mdh">%s</h2>' % e(f['title']) if f.get('title') else '', rows))


def _foot(d, P):
    b = d.get('brand') or {}
    h = d.get('hero') or {}
    f = d.get('foot') or {}
    fc, ft = P['foot']
    seen, c1, c2 = set(), [], []
    for x in list(d.get('nav') or []):
        if x.get('t') and x['t'] not in seen:
            seen.add(x['t'])
            c1.append(x)
    for x in list(d.get('links') or []) + ([d['signin']] if (d.get('signin') or {}).get('t') else []):
        if x.get('t') and x['t'] not in seen:
            seen.add(x['t'])
            c2.append(x)
    ul = lambda xs: '<ul>%s</ul>' % ''.join('<li><a href="%s">%s</a></li>' % (e(x.get('h') or '#'), e(x['t'])) for x in xs) if xs else ''
    name = b.get('name') or ''
    cls = _step(len(name), [(7, 't1'), (11, 't2'), (999, 't3')])
    legal = ''.join('<li><a href="%s">%s</a></li>' % (e(x.get('h') or '#'), e(x.get('t'))) for x in (f.get('links') or []) if x.get('t'))
    return ('<footer class="foot" style="--fc:%s;--ft:%s;--fs:%s"><div class="wrap f1"><div class="fa">%s%s</div>%s</div>'
            '<div class="wrap"><div class="f2">%s%s</div><div class="f3"><span>%s</span>%s</div></div></footer>'
            % (fc, ft, P['softf'], '<p class="lgp">%s</p>' % e(h['note']) if h.get('note') else '',
               _btn(d.get('cta'), P['card'], P['ink'], fc, ft),
               '<nav aria-label="Footer">%s%s</nav>' % (ul(c1), ul(c2)) if (c1 or c2) else '',
               '<p class="huge %s" aria-hidden="true">%s</p>' % (cls, e(name)) if name else '',
               '<p class="fx2">%s</p>' % e(f['text']) if f.get('text') else '',
               e(f.get('legal')), '<ul>%s</ul>' % legal if legal else ''))


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{font-size:16.0767px;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--ink);font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;font-weight:500;font-size:1rem;line-height:1.5;-webkit-font-smoothing:antialiased;overflow-x:clip}
h1,h2,h3,p,ul,ol,figure{margin:0;padding:0}ul,ol{list-style:none}a{color:inherit;text-decoration:none}img,video{display:block;max-width:100%;height:auto}
:root{--m:20px;--R:35px;--eb:cubic-bezier(.17,.67,.3,1.33);--ez:cubic-bezier(.5,0,0,1);--eio:cubic-bezier(.455,.03,.515,.955)}
.wrap{padding-inline:var(--m)}
:focus-visible{outline:2px solid var(--ink);outline-offset:4px;box-shadow:0 0 0 4px var(--g);border-radius:6px}
/* type */
.huge,h1{font-weight:500;line-height:.95;letter-spacing:-.06em;text-wrap:balance}
h1.t1,.huge.t1{font-size:66.9px}h1.t2,.huge.t2{font-size:54px}h1.t3,.huge.t3{font-size:45px}
.lg{font-size:46.6px;line-height:.95;letter-spacing:-.06em;font-weight:500;text-wrap:balance}
.mdh{font-size:35.35px;line-height:1.15;letter-spacing:-.06em;font-weight:500;text-wrap:balance}
.xs{font-size:27px;line-height:1.2;letter-spacing:-.06em;text-wrap:balance}
.md{font-size:16.15px;line-height:1.25;letter-spacing:-.04em}.nb{white-space:nowrap}
/* button: label 18/1.5, round disc 43, r10; on hover a disc grows at the left, the label moves 51px, the right disc shrinks */
.btn{position:relative;display:inline-flex;align-items:center;gap:8px;padding:10px;border-radius:10px;background:var(--bb);color:var(--bt);font-size:16.15px;line-height:1.5;font-weight:500;transition:transform .15s var(--ez);max-width:100%}
.btn .bl{padding:0 10px;transition:transform .4s var(--eb)}
.btn .bi{flex:none;width:40px;height:40px;border-radius:50%;background:var(--bc);color:var(--bi);display:flex;align-items:center;justify-content:center;font-size:20px;transition:transform .4s var(--eb)}
.btn .bi.h{position:absolute;left:10px;top:50%;margin-top:-20px;transform:scale(0)}
@media(hover:hover){.btn:hover .bi.h{transform:scale(1)}.btn:hover .bl{transform:translateX(48px)}.btn:hover .bi.d{transform:scale(0)}}
.btn:focus-visible .bi.h{transform:scale(1)}.btn:focus-visible .bl{transform:translateX(48px)}.btn:focus-visible .bi.d{transform:scale(0)}
.btn:active{transform:scale(.97)}
/* nav: card-coloured bar r10 + a separate button, fixed 16/17 from the top */
.nav{position:fixed;z-index:100;top:16px;left:16px;right:16px;display:flex;gap:20px;align-items:flex-start}
.bar{flex:1;min-height:60px;background:var(--card);border-radius:10px;display:flex;align-items:center;justify-content:space-between;padding:0 8px 0 12px;position:relative}
.logo{display:flex;align-items:center;gap:10px;font-size:20px;letter-spacing:-.04em;font-weight:500;min-height:44px}
.logo .lg{height:27px;width:auto;max-width:none;font-size:0}.logo .lg.wm{height:20px}
.bar nav{display:none}.nav>.btn.q{display:none}
.mm summary{list-style:none;cursor:pointer;width:44px;height:44px;display:flex;align-items:center;justify-content:center;border-radius:50%}
.mm summary::-webkit-details-marker{display:none}
.mm .bg{width:40px;height:40px;border-radius:50%;background:var(--acc);display:flex;flex-direction:column;gap:5px;align-items:center;justify-content:center;transition:transform .4s var(--eb)}
.mm .bg i{display:block;width:16px;height:2px;border-radius:1px;background:var(--onacc);transition:transform .2s var(--ez)}
.mm[open] .bg i:first-child{transform:translateY(3.5px) rotate(45deg)}.mm[open] .bg i:last-child{transform:translateY(-3.5px) rotate(-45deg)}
.mp{position:absolute;left:0;right:0;top:64px;background:var(--card);border-radius:10px;padding:16px;max-height:calc(100vh - 100px);overflow:auto}
.mp li a{display:flex;align-items:center;min-height:58px;font-size:27px;letter-spacing:-.06em}
.mp .btn{margin-top:8px;width:100%;justify-content:space-between}
/* opening: accent field, one viewport */
.hero{position:relative;height:100vh;height:100svh;min-height:560px;background:var(--acc);color:var(--onacc);overflow:hidden}
.hstick{height:100vh;height:100svh;min-height:560px;display:flex;align-items:center;justify-content:center;padding:100px 20px 195px}
.hc{display:flex;flex-direction:column;gap:48px;text-align:center;max-width:100%}
.tag{font-size:24.4px;line-height:1.2;letter-spacing:-.06em}
/* the panel that slides over the opening */
.tl{position:relative;z-index:1;background:var(--g);border-radius:var(--R) var(--R) 0 0;padding-bottom:84px}
.intro{position:relative;padding-top:43px}
.pw{position:absolute;left:0;right:0;top:-100vh;top:-100svh;bottom:0;pointer-events:none}
.ps{position:sticky;top:0;height:100vh;height:100svh;display:flex;align-items:flex-end;justify-content:center}
.pp{--pw:min(100vw - 24px,560px,60vh*var(--a));width:var(--pw);margin-bottom:calc(var(--pw)/var(--a)*-.19);transform-origin:50% 100%}
.pp img{width:100%;border-radius:10px}
.in{position:relative;z-index:1}.it{display:flex;flex-direction:column;gap:36px;align-items:flex-start}
.ghost{height:calc(min(100vw - 24px,560px)*.62 + 60px)}
.intro.np{padding-bottom:20px}
.rows{position:relative;display:flex;flex-direction:column;gap:56px;padding-top:120px}
.tl.hb{padding-bottom:0}.rows.hb{padding-bottom:84px}
.rbg{position:absolute;inset:0;z-index:0;pointer-events:none}
.rs{position:sticky;top:0;height:100vh;height:100lvh;overflow:hidden}
.rs img{width:100%;height:100%;object-fit:cover}
.rs::after{content:"";position:absolute;inset:0;background:var(--g);opacity:var(--rv)}
.rbg::before{content:"";position:absolute;z-index:1;left:0;right:0;top:0;height:60vh;background:linear-gradient(var(--g),transparent)}
.rows .row{position:relative;z-index:1}
.intro.np+.rows,.rows:first-child{padding-top:60px}
.row{display:flex;flex-direction:column;gap:56px;align-items:center}
.tc{width:100%}
.tile{position:relative}
.tb{position:absolute;inset:0;border-radius:10px;background:var(--card)}.tb.k{inset:1px}
.ti{position:relative;z-index:1;display:flex;flex-direction:column;gap:25px;padding:25px 20px}
.ti h3{font-size:35.35px;line-height:1.15;letter-spacing:-.06em;font-weight:500;text-wrap:balance}
.ti p{font-size:18.63px;line-height:1.25;letter-spacing:-.04em;text-wrap:balance}
.tp img{max-height:420px;width:auto;max-width:min(100%,300px);border-radius:6px;box-shadow:0 0 0 1px var(--line)}
.tp.phone img{border-radius:22px}
/* tiles arrive: colour, then card over it, then the words (only when scripts run) */
.js .tile:not(.in) .tb{transform:scale(0)}.js .tile .tb{transition:transform .6s var(--eb)}.js .tile .tb.w{transition-delay:.2s}
.js .tile .ti>*{transition:transform .4s var(--eio),opacity .4s var(--eio)}
.js .tile:not(.in) .ti>*{opacity:0}.js .tile:not(.in) .ti>p,.js .tile:not(.in) .ti>.tcta{transform:translateY(-10px)}
.js .tile .ti>h3{transition-delay:.3s}.js .tile .ti>p{transition-delay:.35s}.js .tile .ti>.tcta{transition-delay:.45s}
/* the call */
.call{position:relative;background:var(--acc);color:var(--onacc);border-radius:0 0 var(--R) var(--R);padding:131px 0;text-align:center}
.tl+.call{margin-top:-1px}
.cb{margin-top:58px;display:flex;flex-direction:column;align-items:center;gap:24px}
.cb .xs{font-size:24.4px;max-width:25rem}
.three{display:none}
/* the picture band */
.photo{position:relative;aspect-ratio:2268/1350;overflow:hidden;border-radius:var(--R);background:var(--deep)}
.pi{position:absolute;inset:-12% 0}.pi img{width:100%;height:100%;object-fit:cover}
/* numbers */
.nums{background:var(--g);border-radius:var(--R);padding:84px 0 131px}
.ns{display:flex;flex-direction:column;gap:33px}
.nlist{margin-top:20px}
.ni{position:sticky;top:60px;transform:translateY(calc(var(--i)*41.4px))}
.nc{height:400px;border-radius:35px;padding:24.7px;display:flex;flex-direction:column;justify-content:space-between;will-change:transform}
.stat{font-weight:400;line-height:.95;letter-spacing:-.06em;padding-top:60px;white-space:nowrap}
.stat.s1{font-size:105.3px}.stat.s2{font-size:84px}.stat.s3{font-size:62px}.stat.s4{font-size:46px;white-space:normal}
.nd{font-size:18.63px;line-height:1.25;letter-spacing:-.04em;text-wrap:balance}
.nlist{padding-bottom:calc(var(--n)*41.4px)}
/* the deeper block: pictures */
.gal{background:var(--deep);border-radius:var(--R);padding:84px 0 33px}
.gl{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;padding:0 20px 20px 0;scrollbar-width:none}
.gl::-webkit-scrollbar{display:none}
.gl li{flex:none;width:324px;padding-left:20px;scroll-snap-align:start}
.gl.n1 li{width:100%}
.gt{position:relative;height:260px;border-radius:15px;overflow:hidden;background:var(--card);display:flex;align-items:center;justify-content:center}
.gb{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .6s cubic-bezier(.38,.005,.215,1)}
.gt:has(.gb)::before{content:"";position:absolute;inset:0;z-index:1;background:var(--deep);opacity:var(--gv)}.gm{z-index:2}
.gm{position:relative;width:auto;height:auto;max-width:82%;max-height:80%;border-radius:8px}
.gt .gm{aspect-ratio:var(--ma)}
@media(hover:hover){.gt:hover .gb{transform:scale(1.05) rotate(2deg)}}
.gl figcaption{padding-top:10px;font-size:18.63px;line-height:1.25;letter-spacing:-.04em;text-wrap:balance}
/* rails (only with logos) */
.rails{background:var(--deep);padding:60px 0 131px;display:flex;flex-direction:column;gap:16px;overflow:hidden}
.gal+.rails{margin-top:calc(var(--R)*-1);border-radius:0 0 var(--R) var(--R);padding-top:calc(60px + var(--R))}
.rail{overflow:hidden}.rc{display:flex;width:max-content}
.rpat{display:flex;gap:16px;padding-right:16px}
.rp{display:flex;align-items:center;gap:20px;padding:20px 40px 20px 20px;border-radius:64px;background:var(--g);white-space:nowrap;min-height:100px}
.rp.nt{padding-left:40px}.rv{width:60px;height:60px;border-radius:50%;background:var(--card);display:flex;align-items:center;justify-content:center;padding:16px}
.rp p{font-size:18.63px;letter-spacing:-.04em}
.js .rc{animation:rail var(--rd,90s) linear infinite}.js .rail.rev .rc{animation-direction:reverse}
@keyframes rail{to{transform:translateX(-50%)}}
/* numbered tiles */
.feat{padding:84px 0}
.fx{margin-top:16px;max-width:38rem;color:var(--softg)}
.fl{margin-top:40px;display:grid;gap:16px}
.fl li{background:var(--card);border-radius:20px;padding:24px}
.no{display:flex;width:34px;height:34px;align-items:center;justify-content:center;border-radius:10px;font-size:16px;font-weight:700;margin-bottom:12px}
.fl h3{font-size:18.63px;line-height:1.25;letter-spacing:-.04em;font-weight:500;margin-bottom:6px}
.fl p{font-size:16.15px;line-height:1.25;letter-spacing:-.04em;color:var(--soft)}
/* plans */
.plans{background:var(--deep);border-radius:var(--R);padding:84px 0}
.plans .fx{color:var(--softd)}
.pg{margin-top:40px;display:grid;gap:20px}
.pc{background:var(--card);border-radius:20px;padding:28px;display:flex;flex-direction:column;border:2px solid transparent}
.pc.mk{border-color:var(--pk)}
.pc h3{font-size:27px;line-height:1.2;letter-spacing:-.06em;font-weight:500}
.pl{margin-top:4px;font-size:14.9px;line-height:1.25;letter-spacing:-.04em;color:var(--soft)}
.pr{margin-top:20px}.pr b{display:block;font-size:27px;line-height:1.2;letter-spacing:-.025em;font-weight:700}
.pr span{font-size:14.9px;line-height:1.25;letter-spacing:-.04em;color:var(--soft)}
.pc ul{margin-top:17px;font-size:16.15px;line-height:1.25;letter-spacing:-.04em}
.pc li{position:relative;padding:4px 0 4px 27px}.pc li::before{content:"";position:absolute;left:3px;top:.55em;width:10px;height:10px;border-radius:50%;background:var(--pk);box-shadow:0 0 0 1px var(--line)}
.pb{margin-top:auto;padding-top:25px}
.pn{margin-top:28px;font-size:14.9px;line-height:1.25;letter-spacing:-.04em;color:var(--softd)}
/* questions */
.faq{padding:84px 0}
.ql{margin-top:40px;max-width:800px}
.qa{background:var(--deep);border-radius:10px;margin:5px 0}
.qa summary{list-style:none;cursor:pointer;display:flex;gap:20px;align-items:center;justify-content:space-between;padding:15px 10px 15px 20px;border-radius:10px}
.qa summary::-webkit-details-marker{display:none}
.qt{font-size:20px;line-height:1.2;letter-spacing:-.06em;padding-bottom:4px}
.qi{flex:none;position:relative;width:40px;height:40px;border-radius:50%;background:var(--card);transition:transform .4s var(--eb)}
.qi::before,.qi::after{content:"";position:absolute;left:50%;top:50%;width:12px;height:2px;margin:-1px 0 0 -6px;border-radius:1px;background:var(--ink)}
.qi::after{transform:rotate(90deg);transition:transform .2s var(--ez)}
.qa[open] .qi::after{transform:rotate(0)}
@media(hover:hover){.qa summary:hover .qi{transform:scale(1.08)}}
.an{padding:8px 30px 40px 20px;font-size:1rem;line-height:1.5}
/* foot: a second strong field */
.foot{background:var(--fc);color:var(--ft);border-radius:var(--R);overflow:hidden;padding:58px 0 36px;display:flex;flex-direction:column;gap:58px}
.foot :focus-visible{outline-color:var(--ft);box-shadow:0 0 0 4px var(--fc)}
.f1{display:grid;gap:58px}
.fa{display:flex;flex-direction:column;align-items:flex-start;gap:17px}
.lgp{font-size:24.4px;line-height:1.2;letter-spacing:-.06em;max-width:450px}
.foot nav{display:grid;grid-template-columns:1fr 1fr;column-gap:20px;row-gap:10px}
.foot nav ul{display:flex;flex-direction:column;gap:6px}
.foot nav a,.f3 a{display:inline-block;padding:1px 0}.foot nav a:hover,.f3 a:hover{text-decoration:underline}
.f2{display:grid;gap:41px;padding-top:32px;border-top:1px solid color-mix(in srgb,var(--ft) 20%,transparent)}
.f2 .huge{margin-left:-.07em;overflow-wrap:anywhere}
.fx2{font-size:16.15px;line-height:1.25;color:var(--fs);max-width:30rem}
.f3{margin-top:41px;display:flex;flex-wrap:wrap;gap:12px 32px;justify-content:space-between}
.f3 ul{display:flex;gap:24px}

/* ─────────── 1000 and up: the 16-column page, 17px root at 1440 */
@media(min-width:1000px){
html{font-size:clamp(14px,1.18056vw,20px)}
:root{--m:calc(40px + (100vw - 340px)/16);--R:50px}
h1.t1,.huge.t1{font-size:8.2165rem}h1.t2,.huge.t2{font-size:6.4rem}h1.t3,.huge.t3{font-size:5.3rem}
.lg{font-size:4.75rem}.mdh{font-size:3.125rem}.xs{font-size:1.75rem}.md{font-size:1.0625rem}
.btn{gap:.5rem;padding:.625rem;font-size:1.0625rem}.btn .bl{padding:0 .625rem}
.btn .bi{width:2.53rem;height:2.53rem;font-size:1.235rem}.btn .bi.h{left:.625rem;margin-top:-1.265rem}
@media(hover:hover){.btn:hover .bl{transform:translateX(3rem)}}.btn:focus-visible .bl{transform:translateX(3rem)}
.nav{top:17px;left:var(--m);right:var(--m)}
.bar{min-height:4rem;padding:0 .625rem 0 1rem}
.logo{gap:1rem;font-size:1.5rem}.logo .lg{height:30px}.logo .lg.wm{height:28px}
.mm{display:none}
.bar nav{display:block}.bar nav ul{display:flex;gap:.25rem}
.bar nav a{position:relative;display:inline-flex;align-items:center;min-height:2.75rem;padding:0 1rem;border-radius:50px;font-size:1.0625rem;line-height:1.25;letter-spacing:-.04em}
.bar nav a::before{content:"";position:absolute;inset:0;border-radius:50px;background:var(--g);opacity:0;transform:scale(.8);transition:transform .4s var(--eb),opacity .1s var(--ez)}
.bar nav a span{position:relative}
.bar nav a:hover::before,.bar nav a:focus-visible::before{opacity:1;transform:scale(1)}.bar nav a:active::before{transform:scale(.9)}
.nav>.btn.q{display:inline-flex;min-height:4rem}
.hero{overflow:visible;min-height:0}
.hpin{position:absolute;left:0;right:0;top:0;height:200vh}
.hstick{position:sticky;top:0;min-height:0;padding:6.625rem 20px 14.8rem;background:var(--acc)}
.hc{gap:3rem;width:min(100%,56.94rem);will-change:transform}
.tag{font-size:1.75rem}
.tl{padding-bottom:10rem}.tl.hb{padding-bottom:0}.rows.hb{padding-bottom:10rem}
.intro{padding-top:6.4rem}
.pp{--pw:min(44rem,32.2rem*var(--a),62vh*var(--a));margin-bottom:calc(var(--pw)/var(--a)*-.38)}
.it{gap:2.25rem;max-width:36rem}
.ghost{height:20.2rem}
.rows{gap:8.5rem;padding-top:calc(44rem/1.6*.38 + 9rem)}
.intro.np+.rows,.rows:first-child{padding-top:8rem}
.row{display:grid;grid-template-columns:repeat(14,1fr);column-gap:20px;align-items:center;min-height:30rem}
.row .tc{grid-row:1}.row .tp{grid-row:1;justify-self:center}
.row.r .tc{grid-column:9/15}.row.r .tp{grid-column:2/7}
.row.l .tc{grid-column:1/7}.row.l .tp{grid-column:9/14}
.row.c .tc{grid-column:5/11}.row.c .tp{grid-column:11/15;align-self:start;margin-top:12rem}
.ti{gap:1.5625rem;padding:3.125rem}
.ti h3{font-size:2.375rem;line-height:1.2}.ti p{font-size:1.1875rem}
.tp img{max-height:37.6rem;max-width:min(100%,25.4rem)}.tp.phone img{border-radius:2rem}
.call{padding:10rem 0}
.cb{margin-top:5rem;gap:1.5rem}.cb .xs{font-size:1.75rem;max-width:35rem}
.three{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:15rem;font-size:1.0625rem;line-height:1.25;letter-spacing:-.04em}
.nums{padding:8rem 0 10rem}
.ng{display:grid;grid-template-columns:repeat(14,1fr);column-gap:20px}
.nl{grid-column:1/9}.ns{position:sticky;top:9.3rem;min-height:26.5rem;justify-content:space-between;gap:2.5rem}
.ns .md{max-width:20.9rem}
.nlist{grid-column:10/15;margin:0 0 10rem;padding:20rem 0 0}
.nums.solo .nlist{grid-column:5/11;padding-top:0}
.ni{top:6.8rem;transform:translateY(calc(var(--i)*3.5rem))}
.nc{height:min(32.35rem,100vh - 6.8rem - var(--n)*3.5rem - 1rem);min-height:22rem;border-radius:50px;padding:2rem}
.stat{padding-top:3.76rem}.stat.s1{font-size:8.47rem}.stat.s2{font-size:6.6rem}.stat.s3{font-size:4.9rem}.stat.s4{font-size:3.4rem}
.nd{font-size:1.1875rem}
.gal{padding:10rem var(--m) 5rem}
.gl{display:grid;grid-template-columns:601fr 291fr 291fr;gap:20px;overflow:visible;padding:0}
.gl li{width:auto;padding:0 0 5rem;position:relative}
.gl figcaption{position:absolute;left:0;right:0;top:calc(100% - 5rem);padding-top:.625rem;font-size:1.1875rem}
.gt{height:auto;border-radius:20px}
.gl .g0{grid-column:1;grid-row:1/3;align-self:end}.gl .g0 .gt{aspect-ratio:601/863}.gl .g0 figcaption{font-size:1.75rem;line-height:1.2;letter-spacing:-.06em}
.gl .g1{grid-column:2/4}.gl .g1 .gt{aspect-ratio:601/515}
.gl .g2,.gl .g3{grid-row:2}.gl .g2 .gt,.gl .g3 .gt{aspect-ratio:291/249}
.gl.n3 .g2{grid-column:2/4}.gl.n3 .g2 .gt{aspect-ratio:601/249}
.gl.n2 .g0{grid-row:1}.gl.n2 .g1 .gt{aspect-ratio:601/863}
.gl.n1{grid-template-columns:1fr}.gl.n1 .g0 .gt{aspect-ratio:1223/600}
.gm{max-width:78%;max-height:78%;border-radius:10px}
.gl .g0 .gm{max-height:84%}
.rails{padding:5rem 0 10rem;gap:1rem}.rp{min-height:6.25rem;padding:1.25rem 2.5rem 1.25rem 1.25rem;gap:1.25rem}.rp.nt{padding-left:2.5rem}.rp p{font-size:1.1875rem}
.rv{width:3.76rem;height:3.76rem}
.feat,.faq{padding:8rem 0}
.fx{margin-top:1rem}
.fl{margin-top:2.5rem;grid-template-columns:repeat(3,1fr);gap:1rem}
.fl li{padding:1.5rem}.no{width:2rem;height:2rem;font-size:1rem;margin-bottom:.75rem}
.fl h3{font-size:1.1875rem;margin-bottom:.375rem}.fl p{font-size:1.0625rem}
.plans{padding:8rem 0}
.pg{margin-top:5rem;gap:1.25rem;align-items:stretch}.pg.n2{grid-template-columns:repeat(2,1fr)}.pg.n3{grid-template-columns:repeat(3,1fr)}.pg.n1{grid-template-columns:minmax(0,23.1rem)}
.pc{padding:1.75rem}.pc.mk{margin-top:-2.5rem}
.pc h3,.pr b{font-size:1.75rem}.pl,.pr span,.pn{font-size:.875rem}.pr{margin-top:1.25rem}
.pc ul{margin-top:1rem;font-size:1.0625rem}.pc li{padding:.25rem 0 .25rem 1.625rem}.pb{padding-top:1.5rem}
.ql{margin-top:2.5rem}.qa summary{padding:.94rem .625rem .94rem 1.25rem}.qt{font-size:1.5rem}.qi{width:2.53rem;height:2.53rem}
.an{padding:.6rem 6rem 3.125rem 1.25rem}
.foot{padding:8rem 0 2.25rem;gap:5rem}
.f1{grid-template-columns:repeat(14,1fr);column-gap:20px}
.fa{grid-column:1/6;gap:1.5rem}.lgp{font-size:1.1875rem;line-height:1.25;letter-spacing:-.04em;max-width:19.7rem}
.foot nav{grid-column:10/14}
.f2{grid-template-columns:repeat(14,1fr);column-gap:20px;padding-top:2rem;border-top:0;align-items:start}
.f2 .huge{grid-column:1/10;white-space:nowrap}.fx2{grid-column:10/14;font-size:1.0625rem;padding-top:.4rem}
.f3{margin-top:3.5rem}
}
/* load: the bar comes down, the lines rise 80px (only when scripts run) */
.js .nav{transform:translateY(calc(-100% - 20px))}.js.on .nav{transform:none;transition:transform .4s var(--ez) .2s}
.js .rise{transform:translateY(80px)}.js.on .rise{transform:none;transition:transform .8s var(--ez)}
.js.on .rise.r1{transition-delay:.1s}.js.on .rise.r2{transition-delay:.2s}
@media(prefers-reduced-motion:reduce){
*,*::before,*::after{transition:none!important;animation:none!important}
.js .nav,.js .rise{transform:none}
.js .tile:not(.in) .tb{transform:none}.js .tile:not(.in) .ti>*{opacity:1;transform:none}
.rc{flex-wrap:wrap;width:auto;justify-content:center;gap:16px}.rpat[aria-hidden]{display:none}.rpat{flex-wrap:wrap;justify-content:center;padding:0 20px}
}
"""

JS = r"""
(function(){var D=document,H=D.documentElement,W=window,rm=W.matchMedia('(prefers-reduced-motion:reduce)').matches;
requestAnimationFrame(function(){requestAnimationFrame(function(){H.classList.add('on')})});
D.addEventListener('keydown',function(ev){if(ev.key==='Escape'){var m=D.querySelector('.mm[open]');if(m){m.open=false;m.querySelector('summary').focus()}}});
var tiles=[].slice.call(D.querySelectorAll('[data-in]'));
if(!('IntersectionObserver' in W)||rm){tiles.forEach(function(t){t.classList.add('in')})}
else{var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}})},{rootMargin:'0px 0px -12% 0px'});tiles.forEach(function(t){io.observe(t)})}
[].forEach.call(D.querySelectorAll('[data-rail]'),function(r){r.style.setProperty('--rd',Math.max(20,r.scrollWidth/2/22)+'s')});
if(rm)return;
[].forEach.call(D.querySelectorAll('video[data-auto]'),function(v){v.autoplay=true;var p=v.play();if(p&&p.catch)p.catch(function(){})});
var hc=D.querySelector('[data-hc]'),pp=D.querySelector('[data-pp]'),pars=[].slice.call(D.querySelectorAll('[data-par]')),
ph=D.querySelector('[data-photo]'),ncs=[].slice.call(D.querySelectorAll('[data-nc]')),wide=W.matchMedia('(min-width:1000px)'),tick=false;
pars.forEach(function(p){p._t=0});
function cl(v){return v<0?0:v>1?1:v}
function run(){tick=false;var y=W.scrollY,vh=W.innerHeight,w=wide.matches;
if(hc)hc.style.transform=w?'scale('+(1-.2*cl(y/vh)).toFixed(4)+')':'';
if(pp)pp.style.transform=w?'scale('+(.913+.087*cl(y/(vh*.83))).toFixed(4)+')':'';
pars.forEach(function(p){if(!w){if(p._t){p.style.transform='';p._t=0}return}var r=p.getBoundingClientRect(),top=r.top-p._t;if(top>vh*1.5||top+r.height<-vh*.5)return;
var a=+p.getAttribute('data-par'),t=a-2*a*cl((vh-top)/(vh+r.height));p._t=t;p.style.transform='translate3d(0,'+t.toFixed(2)+'px,0)'});
if(ph){var s=ph.parentNode.getBoundingClientRect();if(s.top<vh&&s.bottom>0)ph.style.transform='translate3d(0,'+(-.1*s.top).toFixed(2)+'px,0)'}
ncs.forEach(function(c){if(!w){c.style.transform='';return}var it=c.parentNode,i=+c.getAttribute('data-nc'),rem=parseFloat(getComputedStyle(H).fontSize),
stuck=6.8*rem+(i+1)*3.5*rem,top=it.getBoundingClientRect().top,p=cl((top-stuck-146)/536),sg=i%2?1:-1;
c.style.transform=p?'translate3d(0,'+(110*p).toFixed(1)+'px,0) rotate('+(sg*10*p).toFixed(2)+'deg)':''});}
function req(){if(!tick){tick=true;requestAnimationFrame(run)}}
W.addEventListener('scroll',req,{passive:true});W.addEventListener('resize',req);run();
})();
"""


def render(d: dict) -> str:
    P = _palette(d)
    b = d.get('brand') or {}
    h = d.get('hero') or {}
    used = set()
    tl = _timeline(d, P, used)
    body = ''.join([
        _nav(d, P), '<main>', _hero(d, P), tl, _callout(d, P), _photo(d, P), _numbers(d, P),
        _gallery(d, P, used), _rails(d, P), _features(d, P), _plans(d, P), _faq(d, P), '</main>', _foot(d, P)])
    var = '--rv:%s;--gv:%s;' % (('.5', '.45') if P['light'] else ('.45', '.5'))
    var += '--g:%s;--ink:%s;--card:%s;--deep:%s;--acc:%s;--onacc:%s;--line:%s;--soft:%s;--softg:%s;--softd:%s' % (
        P['g'], P['ink'], P['card'], P['deep'], P['acc'], P['onacc'], P['line'], P['soft'], P['softg'], P['softd'])
    title = ' — '.join(x for x in (b.get('name'), h.get('title')) if x)
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title>%s<meta name="theme-color" content="%s">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="%s"><style>:root{%s}%s</style>'
            '<script>document.documentElement.classList.add("js")</script></head><body>%s<script>%s</script></body></html>'
            % (e(d.get('lang') or 'en'), e(title), '<meta name="description" content="%s">' % e(h['text']) if h.get('text') else '',
               P['acc'], FONTS, var, CSS, body, JS))
