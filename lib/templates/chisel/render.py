"""chisel/render.py — one pure function: render(d) -> a complete page.

The build (section order and anatomy, the 12-column grid, measures, type scale, spacing, the light/dark/accent
relations, motion, the phone build) was measured on the reference's home page and on its team, capital, about and
contact pages at 1440 and 390 on 2026-11-12 (see NOTES.md). Nothing of the reference's code, words, pictures, icons,
logo or commercial typefaces is here. The client's data fills it; a section whose data is missing is left out whole.
No model call, no file read, no client logic.
"""
import html
import re

FONTS = ('https://fonts.googleapis.com/css2?family=Alegreya+Sans:wght@400;500;700'
         '&family=Albert+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap')
PRE = '../../'


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


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
    x, y = sorted((_lum(a), _lum(b)), reverse=True)
    return (x + .05) / (y + .05)


def _tone(fg, bg, t, floor=4.6):
    """fg at t over bg (the reference's ink/65, cream/60 …), raised until it reads at 4.6:1 on this client's ground."""
    while _con(_mix(fg, bg, t), bg) < floor and t < 1:
        t += .02
    return _mix(fg, bg, min(t, 1))


def _reach(c, bg, toward, floor=4.6):
    n = 0
    while _con(c, bg) < floor and n < 30:
        c = _mix(toward, c, .08)
        n += 1
    return c


def _theme(pal):
    """The reference's relations: a light page ground, a second warmer light ground, a dark ground that is also the
    text colour, a slightly lifted dark for panels, one accent (bright on dark, deepened on light)."""
    g, i = pal.get('ground') or '#ffffff', pal.get('ink') or '#171717'
    L, D = (g, i) if _lum(g) >= _lum(i) else (i, g)
    if _con(L, D) < 7:
        D = _reach(D, L, '#000000', 7)
    acc = pal.get('accent') or D
    L2 = None
    for c in pal.get('extra') or []:
        try:
            if 1.04 <= _con(c, L) <= 1.4 and _con(c, D) >= 7:
                L2 = c
                break
        except Exception:
            continue
    L2 = L2 or _mix(D, L, .07)
    D2 = _mix(L, D, .07)
    accD = _reach(acc, D2, L)
    accL = _reach(acc, L2, D)
    onacc = D if _con(D, acc) >= _con(L, acc) else L
    accfill = acc if _con(onacc, acc) >= 4.6 else _reach(acc, onacc, L if onacc == D else D)

    def ground(bg, fg, a, raw_ok):
        return {'bg': bg, 'fg': fg, 'm85': _tone(fg, bg, .85), 'm75': _tone(fg, bg, .75), 'm65': _tone(fg, bg, .65),
                'm60': _tone(fg, bg, .60), 'm50': _tone(fg, bg, .50), 'line': _mix(fg, bg, .13),
                'line2': _mix(fg, bg, .22), 'acc': a, 'mark': acc if raw_ok else a}
    grounds = {'l': ground(L, D, accL, _con(acc, L) >= 1.7), 'b': ground(L2, D, accL, _con(acc, L2) >= 1.7),
               'd': ground(D, L, accD, _con(acc, D) >= 1.7), 'a': ground(D2, L, accD, _con(acc, D2) >= 1.7)}
    css = ''.join('.g-%s{%s}' % (k, ';'.join('--%s:%s' % kv for kv in v.items())) for k, v in grounds.items())
    root = ':root{--L:%s;--D:%s;--D2:%s;--accfill:%s;--onacc:%s;--acch:%s;--dv:%d,%d,%d;--lv:%d,%d,%d}' % (
        (L, D, D2, accfill, onacc, _reach(acc, D, L, 8)) + _rgb(D) + _rgb(L))
    return root + css


def _first_sentence(s, limit=140):
    s = (s or '').strip()
    m = re.match(r'^(.+?[.!?])(\s|$)', s)
    out = m.group(1) if m else s
    return out if len(out) <= limit else ''


def _link(t, h, cls=''):
    c = ' class="%s"' % cls if cls else ''
    return '<a%s href="%s">%s</a>' % (c, e(h), e(t)) if h else '<span%s>%s</span>' % (c, e(t))


def _img(p, cls='', eager=False, sizes='100vw'):
    return '<img%s src="%s%s" alt="%s" width="%s" height="%s" %s decoding="async">' % (
        ' class="%s"' % cls if cls else '', PRE, e(p['src']), e(p.get('alt') or ''), e(p.get('w') or ''),
        e(p.get('h') or ''), 'fetchpriority="high"' if eager else 'loading="lazy"')


def _addr(a):
    if not a:
        return ''
    return ', '.join(str(a[k]) for k in ('street', 'city', 'region', 'postcode', 'country') if a.get(k))


def _hours(hs):
    out = []
    for h in hs or []:
        t = ' – '.join(x for x in (h.get('open'), h.get('close')) if x)
        line = ' '.join(x for x in (h.get('days'), t) if x)
        if line:
            out.append(line)
    return out


def _tel(s):
    return 'tel:' + re.sub(r'[^\d+]', '', re.sub(r'\(0\)', '', str(s)))


def _acts(primary, secondary, cls=''):
    out = ''
    if primary and primary.get('t'):
        out += '<a class="btn" href="%s">%s</a>' % (e(primary.get('h') or '#'), e(primary['t']))
    if secondary and secondary.get('t'):
        out += '<a class="arr" href="%s">%s <span aria-hidden="true">→</span></a>' % (e(secondary.get('h') or '#'), e(secondary['t']))
    return '<div class="acts %s">%s</div>' % (cls, out) if out else ''


# ───────────────────────── pictures: chosen by role, size and proportion; each once
class _Pics:
    def __init__(self, d):
        m = d.get('media') or {}
        self.all = [p for p in (m.get('photos') or []) if p.get('src')]
        self.by = {p['src']: p for p in self.all}
        self.used = set()
        self.kept = set()          # portraits of people and badges: never a backdrop
        team = d.get('team') or {}
        people = list(team.get('items') or []) + [x for g in team.get('groups') or [] for x in g.get('items') or []]
        for x in people:
            if x.get('img'):
                self.kept.add(x['img'])

    def get(self, src):
        return self.by.get(src) if src else None

    def take(self, src):
        self.used.add(src)
        return self.by.get(src)

    def free(self, p):
        return p and p['src'] not in self.used and p['src'] not in self.kept and p.get('role') != 'portrait'

    def big(self, p, w=0, h=0):
        return bool(p) and not p.get('small') and (p.get('w') or 0) >= w and (p.get('h') or 0) >= h

    def half(self, src):
        """a photograph that can stand as an edge-to-edge half, as tall as its section"""
        p = self.get(src)
        if self.free(p) and self.big(p, 800, 800):
            return self.take(src)
        return None

    def wide(self, min_w=1600, prefer=()):
        """a landscape photograph wide enough to run edge to edge at its own pixels"""
        c = [p for p in self.all if self.free(p) and self.big(p, min_w, 600) and p['w'] >= p['h'] * 1.2]
        if not c:
            return None
        c.sort(key=lambda p: 0 if p.get('role') in prefer else 1)
        return self.take(c[0]['src'])


# ───────────────────────── parts
def _eyebrow(n, label=''):
    return '<p class="eye">%02d%s</p>' % (n, ' · ' + e(label) if label else '')


def _plist(rows):
    rows = [r for r in rows or [] if r]
    return '<ul class="pl">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in rows) if rows else ''


def _prices(it):
    ps = [p for p in it.get('prices') or [] if p.get('price')]
    if not ps:
        return ''
    return '<ul class="pl pr">%s</ul>' % ''.join(
        '<li><span>%s</span><b>%s</b></li>' % (e(p.get('label') or ''), e(p['price'])) for p in ps)


def _state(it):
    return ' <span class="st">%s</span>' % e(it['state']) if it.get('state') else ''


def _item_body(it, lead=True):
    out = ''
    if it.get('note') and lead:
        out += '<p class="nt">%s</p>' % e(it['note'])
    if it.get('text'):
        out += '<p>%s</p>' % e(it['text'])
    return out + _plist(it.get('rows')) + _prices(it)


def _name(it):
    return _link(it.get('name') or '', it.get('h'))


def _rows_diamond(items, start=1):
    out = ''
    for k, it in enumerate(items):
        price = '<span class="pv">%s</span>' % e(it['price']) if it.get('price') else ''
        out += ('<div class="drow"><span class="dia"><span>%02d</span></span><div class="db"><h3>%s%s%s</h3>%s</div></div>'
                % (k + start, _name(it), _state(it), price, _item_body(it)))
    return '<div class="drows">%s</div>' % out


def _rows_ruled(items):
    out = ''
    for it in items:
        out += '<div class="rrow"><h3>%s%s</h3><div class="rb">%s</div></div>' % (_name(it), _state(it), _item_body(it))
    return '<div class="rrows">%s</div>' % out


def _rows_price(items):
    out = ''
    long = any(len(str(it.get('price') or '')) > 9 for it in items)
    for it in items:
        note = ' <span class="fn">· %s</span>' % e(it['note']) if it.get('note') else ''
        out += ('<div class="frow"><span class="fv">%s</span><div class="fl"><p class="fgt">%s%s%s</p>%s</div></div>'
                % (e(it.get('price') or ''), _name(it), _state(it), note, _item_body(it, lead=False)))
    return '<div class="figs%s">%s</div>' % (' stack' if long else '', out)


def _rows_for(items, variant):
    if variant == 0:
        return _rows_diamond(items)
    priced = [it for it in items if it.get('price')]
    if priced and len(priced) == len(items):
        return _rows_price(items)
    if priced:
        return _rows_price(priced) + _rows_ruled([it for it in items if not it.get('price')])
    return _rows_ruled(items)


def _half(p, side):
    ar = max(.8, min(1.5, (p.get('w') or 4) / (p.get('h') or 5)))
    return '<div class="half half-%s" style="--ar:%.3f" data-slot="half">%s</div>' % (side, ar, _img(p))


def _band(p, text, cite, quote=False, head=False):
    t = '“%s”' % e(text.strip('“”"')) if quote else e(text)
    c = ('<h2>%s</h2>' if head else '<cite>%s</cite>') % e(cite) if cite else ''
    return ('<div class="band g-d" data-slot="band">%s<div class="bv"></div><div class="w"><blockquote class="c-band">'
            '<p>%s</p>%s</blockquote></div></div>' % (_img(p), t, c))


def _cells(items, cls, cols):
    n = len(items)
    rest = n % cols
    out = ''
    for k, it in enumerate(items):
        span = ' style="grid-column:span %d"' % (cols - rest + 1) if rest and k == n - 1 and cols - rest + 1 > 1 else ''
        out += it.replace('<@>', span, 1)
    return '<div class="%s k%d">%s</div>' % (cls, cols, out)


# ───────────────────────── the page
def render(d: dict) -> str:
    d = d or {}
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    hero = d.get('hero') or {}
    place = d.get('place') or {}
    contact = d.get('contact') or {}
    cta = d.get('cta') or {}
    pics = _Pics(d)
    cat = d.get('catalogue') or {}
    groups = [g for g in cat.get('groups') or [] if g.get('t') or g.get('items')]
    feats = [f for f in (d.get('features') or {}).get('items') or [] if f.get('t')]
    steps = d.get('steps') or {}
    sitems = [s for s in steps.get('items') or [] if s.get('title') or s.get('text')]
    projects = [p for p in d.get('projects') or [] if p.get('title') or p.get('text')]
    quotes = [q for q in d.get('quotes') or [] if q.get('q')]
    kicker = hero.get('kicker') or ''
    phone = contact.get('phone') or place.get('phone') or {}
    email = contact.get('email') or place.get('email') or ''
    n = 0
    S = []          # (ground, html)

    # pictures held by a section of their own are set aside before the open slots choose
    for pr in projects:
        for s in (pr.get('photos') or [])[:1]:
            if pics.get(s):
                pics.kept.add(s)
    for c in d.get('credentials') or []:
        if c.get('img') and pics.get(c['img']):
            pics.kept.add(c['img'])
    step_pic = None
    for s in sitems:
        p = pics.get(s.get('img'))
        if pics.free(p) and pics.big(p, 1000, 600):
            step_pic = p
            pics.kept.add(p['src'])
            break
    group_pic = {}
    for k, g in enumerate(groups):
        if k % 3 and g.get('img'):
            p = pics.half(g['img'])
            if p:
                group_pic[k] = p

    # ── header
    nav = [x for x in d.get('nav') or [] if x.get('t')]
    top = [x for x in nav if x.get('h') != cta.get('h')][:5 if cta.get('t') else 6]
    if cta.get('t'):
        top.append(cta)
    allnav = nav + ([cta] if cta.get('t') and all(x.get('h') != cta.get('h') for x in nav) else [])
    logo = ('<img src="%s%s" alt="%s">' % (PRE, e(brand['logo']), e(name))) if brand.get('logo') else e(name)
    header = ('<header class="hd"><div class="w"><a class="bm" href="%s">%s</a><nav class="nv">%s</nav>'
              '<details class="mn"><summary aria-label="Menu"><i></i><i></i></summary><nav class="mp">%s</nav></details></div></header>'
              % (e(brand.get('home') or '#'), logo, ''.join(_link(x['t'], x.get('h')) for x in top),
                 ''.join(_link(x['t'], x.get('h')) for x in allnav)))

    # ── opening: full-height picture under three veils, type at the foot, three linked cells
    hp = pics.wide(1600, prefer=('workshop', 'exterior', 'room', 'work', 'action', 'people', 'landscape', 'machine', 'bar'))
    if hero.get('title') or name:
        cards = ''
        src = [(g.get('t'), _first_sentence(g.get('text')), '#g%d' % (k + 1)) for k, g in enumerate(groups) if g.get('t')][:3]
        if not src:
            src = [(f['t'], _first_sentence(f.get('d')), '#features') for f in feats][:3]
        for t, tx, h in src:
            cards += ('<a href="%s"><span class="ct"><i></i><b>%s</b></span>%s<span class="cl" aria-hidden="true">→</span></a>'
                      % (h, e(t), '<span class="cx">%s</span>' % e(tx) if tx else ''))
        cards = '<div class="hc rise r2 n%d">%s</div>' % (len(src), cards) if cards else ''
        pic = ('<div class="hz" data-slot="hero">%s<div class="v1"></div><div class="v2"></div><div class="v3"></div></div>'
               % _img(hp, eager=True)) if hp else ''
        S.append(('d', '<section class="hero g-d">%s<div class="hx">%s<h1>%s</h1>%s%s%s</div></section>' % (
            pic, '<p class="eye rise">%s</p>' % e(kicker) if kicker else '', e(hero.get('title') or name),
            '<p class="hl">%s</p>' % e(hero['text']) if hero.get('text') else '', cards,
            '' if cards else _acts(hero.get('primary'), hero.get('secondary')))))

    # ── the numbered sections: one per catalogue group, cycling the reference's three builds
    for k, g in enumerate(groups):
        n += 1
        v = k % 3
        gr = 'lbd'[0 if v == 0 else (2 if v == 1 else 1)]
        items = [it for it in g.get('items') or [] if it.get('name') or it.get('price')]
        head = _eyebrow(n, cat.get('title')) + '<h2>%s</h2>' % _link(g.get('t') or '', None)
        if k == 0 and cat.get('text'):
            head += '<p class="ld">%s</p>' % e(cat['text'])
        if g.get('text'):
            head += '<p class="%s">%s</p>' % ('bd' if k == 0 and cat.get('text') else 'ld', e(g['text']))
        rows = _rows_for(items, v) if items else ''
        note = '<p class="cn">%s</p>' % e(cat['note']) if cat.get('note') and k == len(groups) - 1 else ''
        p = group_pic.get(k)
        if v == 1 and p:
            body = '<div class="c-l col">%s%s%s</div>' % (head, rows, note)
            inner = '<div class="w">%s</div>%s' % (body, _half(p, 'r'))
        elif v == 2 and p:
            body = '<div class="c-r col">%s%s%s</div>' % (head, rows, note)
            inner = '%s<div class="w">%s</div>' % (_half(p, 'l'), body)
        else:
            inner = '<div class="w"><div class="c-l col">%s</div><div class="c-r">%s%s</div></div>' % (head, rows, note)
        S.append((gr, '<section class="sec pil g-%s%s" id="g%d">%s</section>' % (gr, ' hashalf' if p else '', k + 1, inner)))

    # ── plans, when the client has them: the reference's three dark panels
    plans = d.get('plans') or {}
    pitems = [p for p in plans.get('items') or [] if p.get('name') or p.get('price')]
    if pitems:
        n += 1
        cs = ''
        np_, rest = len(pitems), len(pitems) % 3
        for k, p in enumerate(pitems):
            span = ''
            if np_ > 4 and rest and k >= np_ - rest:
                span = ' style="--sp:span %d"' % (6 // rest)
            rows = ''.join('<li>%s</li>' % e(r) for r in p.get('rows') or [] if r)
            pc = p.get('cta') if isinstance(p.get('cta'), dict) else None
            cs += ('<div class="pn g-a%s"%s><i></i><h3><span>%s</span> %s%s</h3>%s%s%s</div>' % (
                ' mk' if p.get('marked') else '', span, e(p.get('name') or ''), e(p.get('price') or ''),
                ' <small>%s</small>' % e(p['per']) if p.get('per') else '',
                '<p>%s</p>' % e(p['line']) if p.get('line') else '', '<ul class="pl">%s</ul>' % rows if rows else '',
                '<a class="btn" href="%s">%s</a>' % (e(pc.get('h') or '#'), e(pc['t'])) if pc and pc.get('t') else ''))
        S.append(('d', '<section class="sec g-d" id="plans"><div class="w"><div class="c-all hd2">%s%s%s</div>'
                  '<div class="c-all pns p%d">%s</div>%s</div></section>' % (
                      _eyebrow(n), '<h2>%s</h2>' % e(plans['title']) if plans.get('title') else '',
                      '<p class="ld">%s</p>' % e(plans['text']) if plans.get('text') else '', min(np_, 5), cs,
                      '<p class="c-all cn">%s</p>' % e(plans['note']) if plans.get('note') else '')))

    # ── statement, figures, and the panel of credentials
    st = d.get('statement') or {}
    figs = [f for f in d.get('figures') or [] if f.get('v')]
    creds = [c for c in d.get('credentials') or [] if c.get('t')]
    trust = [t for t in d.get('trust') or [] if t]
    if st.get('title') or figs or creds:
        n += 1
        left = _eyebrow(n)
        sp = pics.wide(1600, prefer=('detail', 'product', 'work', 'machine')) if st.get('title') and st.get('text') else None
        if sp:
            S.append(('p', _band(sp, st['text'], st['title'], head=True)))
            if hero.get('text2'):
                left += '<p class="ld">%s</p>' % e(hero['text2'])
        else:
            if st.get('title'):
                left += '<h2>%s</h2>' % e(st['title'])
            if st.get('text'):
                left += '<p class="ld">%s</p>' % e(st['text'])
            if hero.get('text2'):
                left += '<p class="bd">%s</p>' % e(hero['text2'])
        fr = ''
        if figs:
            long = any(len(str(f['v'])) > 9 for f in figs)
            fr = '<div class="figs%s">%s</div>' % (' stack' if long else '', ''.join(
                '<div class="frow"><span class="fv">%s</span><div class="fl"><p class="fgt">%s</p></div></div>'
                % (e(f['v']), e(f.get('l') or '')) for f in figs))
        acts = _acts(hero.get('primary'), hero.get('secondary'), 'full') if S and 'class="hc' in S[0][1] else ''
        rows = ''
        for k, c in enumerate(creds):
            badge = ''
            if c.get('img') and not pics.get(c['img']):
                badge = '<img class="bg" src="%s%s" alt="" loading="lazy">' % (PRE, e(c['img']))
            rows += '<li><span class="cy">%s</span><div><p class="c1">%s</p>%s</div>%s</li>' % (
                e(c.get('year') or '%02d' % (k + 1)), _link(c['t'], c.get('h')),
                '<p class="c2">%s</p>' % e(c['text']) if c.get('text') else '', badge)
        if not rows:
            rows = ''.join('<li><span class="cy">%02d</span><div><p class="c1">%s</p></div></li>' % (k + 1, e(t))
                           for k, t in enumerate(trust))
        card = ''
        if rows:
            card = ('<div class="card g-a"><div class="ch"><span><i></i>%s</span>%s</div><ul>%s</ul></div>'
                    % (e(name), '<em>%s</em>' % e(place['since']) if place.get('since') else '', rows))
        if card:
            inner = '<div class="c-l col">%s%s%s</div><div class="c-r mid">%s</div>' % (left, fr, acts, card)
        else:
            inner = '<div class="c-l col">%s%s</div><div class="c-r">%s</div>' % (left, acts, fr)
        S.append(('d', '<section class="sec g-d" id="about"><div class="w">%s</div></section>' % inner))

    # ── features: ruled cells with a short accent bar
    if feats:
        n += 1
        fe = d.get('features') or {}
        cols = 2 if len(feats) in (1, 2, 4) else 3
        cells = _cells(['<div class="cell"<@>><i></i><h3>%s</h3>%s</div>' % (
            e(f['t']), '<p>%s</p>' % e(f['d']) if f.get('d') else '') for f in feats], 'cells', cols)
        S.append(('l', '<section class="sec g-l" id="features"><div class="w"><div class="c-all hd2">%s%s%s</div>'
                  '<div class="c-all">%s</div></div></section>' % (
                      _eyebrow(n), '<h2>%s</h2>' % e(fe['title']) if fe.get('title') else '',
                      '<p class="ld">%s</p>' % e(fe['text']) if fe.get('text') else '', cells)))

    # ── steps: a history with its years as ruled rows, or a numbered walk
    if sitems:
        n += 1
        keyed = any(s.get('k') and s.get('k') != s.get('title') and not re.fullmatch(r'\d{1,2}', str(s['k'])) for s in sitems)
        flat = step_pic and step_pic['w'] >= step_pic['h'] * 2.2 and pics.big(step_pic, 1600)
        tall = step_pic and not flat and pics.big(step_pic, 800, 800)
        band = ''
        lede = '<p class="ld">%s</p>' % e(steps['text']) if steps.get('text') else ''
        if flat and steps.get('text'):
            band, lede = _band(step_pic, steps['text'], name), ''
        head = _eyebrow(n) + ('<h2>%s</h2>' % e(steps['title']) if steps.get('title') else '') + lede
        if keyed:
            rows = '<div class="rrows">%s</div>' % ''.join(
                '<div class="rrow"><h3>%s</h3><div class="rb">%s%s</div></div>' % (
                    e(s.get('k') or ''), '<p class="rt">%s</p>' % e(s['title']) if s.get('title') else '',
                    '<p>%s</p>' % e(s['text']) if s.get('text') else '') for s in sitems)
        else:
            rows = _rows_diamond([{'name': s.get('title'), 'text': s.get('text')} for s in sitems])
        if tall:
            inner = '%s<div class="w"><div class="c-r col">%s%s</div></div>' % (_half(step_pic, 'l'), head, rows)
        else:
            inner = '<div class="w"><div class="c-l col">%s</div><div class="c-r">%s</div></div>' % (head, rows)
        if band:
            S.append(('p', band))
        S.append(('b', '<section class="sec pil g-b%s" id="story">%s</section>' % (' hashalf' if tall else '', inner)))

    # ── what clients say: one over a wide photograph, the rest in ruled cells
    if quotes:
        qs = list(quotes)
        bp = pics.wide(1600, prefer=('product', 'detail', 'work', 'workshop', 'machine'))
        if bp:
            k = next((i for i, q in enumerate(qs) if len(q['q']) <= 200), None)
            if k is None:
                pics.used.discard(bp['src'])
            else:
                q = qs.pop(k)
                S.append(('p', _band(bp, q['q'], ' · '.join(x for x in (q.get('name'), q.get('role')) if x), quote=True)))
        qs = qs[:6]
        if qs:
            cols = 2 if len(qs) in (2, 4) else (1 if len(qs) == 1 else 3)
            cells = _cells(['<figure<@>><span class="qm" aria-hidden="true">“</span><blockquote>%s</blockquote>'
                            '<figcaption>%s%s</figcaption></figure>' % (
                                e(q['q'].strip('“”"')), '<b>%s</b>' % e(q['name']) if q.get('name') else '',
                                '<span>%s</span>' % e(q['role']) if q.get('role') else '') for q in qs], 'qcells', cols)
            S.append(('b', '<section class="sec g-b" id="quotes"><div class="w"><div class="c-all">%s</div></div></section>' % cells))

    # ── the people
    team = d.get('team') or {}
    people = list(team.get('items') or [])
    for g in team.get('groups') or []:
        people += [dict(x, role=x.get('role') or g.get('t')) for x in g.get('items') or []]
    people = [x for x in people if x.get('name')]
    if people:
        n += 1

        def reach(x):
            out = []
            if x.get('phone'):
                out.append('<a href="%s">%s</a>' % (e(_tel(x['phone'])), e(x['phone'])))
            if x.get('email'):
                out.append('<a href="mailto:%s">%s</a>' % (e(x['email']), e(x['email'])))
            return '<p class="tc">%s</p>' % ' '.join(out) if out else ''
        withp = [x for x in people if pics.get(x.get('img'))]
        without = [x for x in people if not pics.get(x.get('img'))]
        grid = ''
        for x in withp:
            grid += '<div class="tm"><div class="tp">%s</div><h3>%s</h3>%s%s%s</div>' % (
                _img(pics.get(x['img'])), _link(x['name'], x.get('h')),
                '<span class="tr">%s</span>' % e(x['role']) if x.get('role') else '',
                '<p class="tx">%s</p>' % e(x['text']) if x.get('text') else '', reach(x))
        wordy = any(len(x.get('text') or '') > 120 for x in withp)
        grid = '<div class="c-all tg%s">%s</div>' % (' one' if wordy else '', grid) if grid else ''
        lst = ''
        for x in without:
            lst += '<div class="tl"><h3>%s</h3><div>%s%s%s</div></div>' % (
                _link(x['name'], x.get('h')), '<span class="tr">%s</span>' % e(x['role']) if x.get('role') else '',
                '<p class="tx">%s</p>' % e(x['text']) if x.get('text') else '', reach(x))
        lst = '<div class="c-all tls%s">%s</div>' % ('' if len(without) > 1 else ' solo', lst) if lst else ''
        S.append(('d', '<section class="sec g-d" id="team"><div class="w"><div class="c-all hd2">%s%s%s</div>%s%s</div></section>' % (
            _eyebrow(n), '<h2>%s</h2>' % e(team['title']) if team.get('title') else '',
            '<p class="ld">%s</p>' % e(team['text']) if team.get('text') else '', grid, lst)))

    # ── named work: one piece as a picture half, several as a row of two
    if projects:
        n += 1
        pp = [(pr, pics.get((pr.get('photos') or [None])[0])) for pr in projects]
        if len(pp) == 1:
            pr, p = pp[0]
            head = _eyebrow(n) + '<h2>%s</h2>' % _link(pr.get('title') or '', pr.get('h')) + (
                '<p class="ld">%s</p>' % e(pr['text']) if pr.get('text') else '')
            if p and pics.big(p, 800, 800):
                inner = '%s<div class="w"><div class="c-r col">%s</div></div>' % (_half(p, 'l'), head)
                S.append(('b', '<section class="sec pil g-b hashalf" id="work">%s</section>' % inner))
            else:
                S.append(('b', '<section class="sec g-b" id="work"><div class="w"><div class="c-l col">%s</div></div></section>' % head))
        else:
            figs2 = ''
            for pr, p in pp:
                figs2 += '<figure>%s<figcaption><span>%s</span>%s</figcaption></figure>' % (
                    '<div class="fp">%s</div>' % _img(p) if p and not p.get('small') else '',
                    _link(pr.get('title') or '', pr.get('h')), '<p>%s</p>' % e(pr['text']) if pr.get('text') else '')
            S.append(('b', '<section class="sec g-b" id="work"><div class="w"><div class="c-all">%s</div><div class="c-all two">%s</div></div></section>' % (_eyebrow(n), figs2)))

    # ── questions
    faq = d.get('faq') or {}
    qa = [q for q in faq.get('items') or [] if q.get('q')]
    if qa:
        n += 1
        rows = '<div class="drows nod">%s</div>' % ''.join(
            '<div class="drow"><div class="db"><h3>%s</h3>%s</div></div>' % (e(q['q']), '<p>%s</p>' % e(q['a']) if q.get('a') else '') for q in qa)
        S.append(('l', '<section class="sec g-l" id="faq"><div class="w"><div class="c-l col">%s%s</div><div class="c-r">%s</div></div></section>' % (
            _eyebrow(n), '<h2>%s</h2>' % e(faq['title']) if faq.get('title') else '', rows)))

    # ── how to reach and find them
    locs = [l for l in d.get('locations') or [] if l.get('name') or l.get('address')]
    links = [l for l in d.get('links') or [] if l.get('t')]
    routes = [r for r in contact.get('routes') or [] if r.get('t')]
    form = contact.get('form') or {}
    addr = _addr(place.get('address'))
    hours = _hours(place.get('hours'))
    if phone or email or addr or routes or locs or links:
        n += 1
        ctitle = form.get('t') or cta.get('t') or ''
        left = _eyebrow(n) + ('<h2 class="h2c">%s</h2>' % _link(ctitle, form.get('h') or cta.get('h')) if ctitle else '')
        det = ''
        if phone.get('t'):
            det += '<div>%s<a class="ul" href="%s">%s</a></div>' % (
                '<span class="lb">%s</span>' % e(phone['note']) if phone.get('note') else '', e(phone.get('h') or _tel(phone['t'])), e(phone['t']))
        if email:
            det += '<div><a class="ul" href="mailto:%s">%s</a></div>' % (e(email), e(email))
        if addr:
            det += '<div><span class="pv2">%s</span></div>' % e(addr)
        if hours:
            det += '<div>%s</div>' % ''.join('<span class="pv2">%s</span>' % e(h) for h in hours)
        soc = [s for s in place.get('social') or [] if s.get('t') and s.get('h')]
        if soc:
            det += '<div class="so">%s</div>' % ''.join('<a class="ul" href="%s">%s</a>' % (e(s['h']), e(s['t'])) for s in soc)
        left += '<div class="det">%s</div>' % det if det else ''
        bk = place.get('booking') or {}
        left += _acts(bk if bk.get('t') and bk.get('h') else None, None)
        right = ''
        if routes:
            rr = ''
            for r in routes:
                h = r.get('h') or ''
                shown = h[7:] if h.startswith('mailto:') else ''
                rr += '<div class="rrow"><h3>%s</h3><div class="rb">%s%s</div></div>' % (
                    _link(r['t'], h if not shown else None), '<p>%s</p>' % e(r['note']) if r.get('note') else '',
                    '<p><a class="ul" href="%s">%s</a></p>' % (e(h), e(shown)) if shown else '')
            right = '<div class="rrows">%s</div>' % rr
        extra = ''
        if locs:
            lc = []
            for l in locs:
                b = ''
                a = _addr(l.get('address'))
                if a:
                    b += '<p>%s</p>' % e(a)
                ph = l.get('phone')
                ph = ph.get('t') if isinstance(ph, dict) else ph
                if ph:
                    b += '<p><a class="ul" href="%s">%s</a></p>' % (e(_tel(ph)), e(ph))
                if l.get('email'):
                    b += '<p><a class="ul" href="mailto:%s">%s</a></p>' % (e(l['email']), e(l['email']))
                for h in _hours(l.get('hours')):
                    b += '<p>%s</p>' % e(h)
                if l.get('note'):
                    b += '<p class="sm">%s</p>' % e(l['note'])
                lc.append('<div class="cell"<@>><i></i><h3>%s</h3>%s</div>' % (_link(l.get('name') or '', l.get('h')), b))
            extra += '<div class="c-all gap">%s</div>' % _cells(lc, 'cells', 2 if len(lc) in (1, 2, 4) else 3)
        if links:
            lk = ['<a class="gc" href="%s"<@>><b>%s</b>%s</a>' % (e(l.get('h') or '#'), e(l['t']),
                  '<span>%s</span>' % e(l['d']) if l.get('d') else '') for l in links]
            extra += '<div class="c-all gap">%s</div>' % _cells(lk, 'gcells', 4 if len(lk) > 3 else len(lk))
        S.append(('l', '<section class="sec g-l" id="contact"><div class="w"><div class="c-l col">%s</div><div class="c-r">%s</div>%s</div></section>' % (left, right, extra)))

    # ── close
    cl = d.get('close') or {}
    if cl.get('title'):
        S.append(('d', '<section class="sec fin g-d"><div class="w"><div class="c-all">%s<h2>%s</h2>%s%s</div></div></section>' % (
            '<p class="eye">%s</p>' % e(kicker) if kicker else '', e(cl['title']),
            '<p class="ld">%s</p>' % e(cl['text']) if cl.get('text') else '',
            _acts(cl.get('cta') if isinstance(cl.get('cta'), dict) else None,
                  {'t': phone['t'], 'h': phone.get('h') or _tel(phone['t'])} if phone.get('t') else None))))

    # two neighbours on the same ground are parted by a hairline
    body = ''
    prev = None
    for gr, h in S:
        if gr == prev and gr != 'p':
            h = h.replace('class="sec ', 'class="sec rule ', 1)
        body += h
        prev = gr

    # ── foot
    foot = d.get('foot') or {}
    cols = []
    if allnav:
        cols.append((name, [(x['t'], x.get('h')) for x in allnav]))
    if groups:
        cols.append((cat.get('title') or '', [(g['t'], '#g%d' % (k + 1)) for k, g in enumerate(groups) if g.get('t')]))
    rl = [(r['t'], r['h']) for r in routes if r.get('h')] + [(l['name'], l['h']) for l in locs if l.get('name') and l.get('h')]
    if rl:
        cols.append((form.get('t') or cta.get('t') or '', rl))
    fcols = ''.join('<div><span class="eye">%s</span><ul>%s</ul></div>' % (e(t) if t else '&nbsp;', ''.join(
        '<li>%s</li>' % _link(a, b) for a, b in ls)) for t, ls in cols)
    soc = [s for s in place.get('social') or [] if s.get('t') and s.get('h')]
    fl = ''.join(' <span aria-hidden="true">·</span> ' + _link(x['t'], x.get('h')) for x in foot.get('links') or [] if x.get('t'))
    footer = ('<footer class="ft g-d%s"><div class="w"><div class="fa"><a class="bm" href="%s">%s</a>%s%s%s%s</div>'
              '<nav class="fb k%d">%s</nav></div><div class="w fz"><p>%s%s</p>%s</div></footer>' % (
                  '', e(brand.get('home') or '#'), logo,
                  '<p class="tg2">%s</p>' % e(hero['title']) if hero.get('title') else '',
                  '<p class="fx">%s</p>' % e(foot['text']) if foot.get('text') else '',
                  '<a class="ul" href="mailto:%s">%s</a>' % (e(email), e(email)) if email else '',
                  '<div class="so">%s</div>' % ''.join('<a href="%s">%s</a>' % (e(s['h']), e(s['t'])) for s in soc) if soc else '',
                  max(1, len(cols)), fcols, e(foot.get('legal') or name), fl,
                  '<p class="fk">%s</p>' % e(kicker) if kicker else ''))

    title = ' — '.join(x for x in (name, kicker or hero.get('title')) if x)
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s"><link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="%s">'
            '<style>%s%s</style></head><body class="g-l">%s<main>%s</main>%s</body></html>' % (
                e(d.get('lang') or 'en'), e(title), e(hero.get('text') or ''), FONTS, _theme(d.get('palette') or {}), CSS,
                header, body, footer))


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--L);color:var(--D);font:400 16px/1.5 "Albert Sans",system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased;overflow-x:clip}
img{max-width:100%;display:block}
a{color:inherit;text-decoration:none}
h1,h2,h3,p,ul,figure,blockquote{margin:0;padding:0}
ul{list-style:none}
h1,h2,h3{font-family:"Alegreya Sans","Albert Sans",sans-serif;font-weight:500;overflow-wrap:break-word}
:focus-visible{outline:2px solid var(--acc,currentColor);outline-offset:3px}
[class*="g-"]{background:var(--bg);color:var(--fg)}
.w{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));column-gap:24px;padding:20px;width:100%}
.c-l,.c-r,.c-all{grid-column:1/-1;min-width:0}
.c-l{margin-bottom:48px}
.c-l:last-child{margin-bottom:0}
.col{display:flex;flex-direction:column;gap:24px;align-items:flex-start}
.col>*{max-width:100%}
.col>.figs,.col>.rrows,.col>.drows,.col>.det{align-self:stretch}
.sec{padding:50px 0;position:relative;scroll-margin-top:24px}
.sec.rule{border-top:1px solid var(--line)}
.eye{font:500 .7rem/1.5 "JetBrains Mono",ui-monospace,monospace;letter-spacing:.18em;text-transform:uppercase;color:var(--acc)}
h2{font-size:2.15rem;line-height:1.1;letter-spacing:-.03em;text-wrap:pretty}
.ld{font-size:1.25rem;line-height:1.4;color:var(--m65);max-width:48ch}
.bd{font-size:1rem;line-height:1.625;color:var(--m60);max-width:60ch}
.hd2{display:flex;flex-direction:column;gap:16px;margin-bottom:48px}
.hd2 h2{max-width:11em}
.hd2 .ld{max-width:52ch;margin-top:8px}
.cn{font-size:.875rem;line-height:1.45;color:var(--m60);margin-top:24px}

/* buttons: square, 2px line; the fill and ink change places at once, as measured */
.btn{display:inline-block;padding:12px 32px;border:2px solid var(--fg);font:500 1rem/1.5 "Albert Sans",sans-serif;color:var(--fg);text-align:center;max-width:100%;overflow-wrap:anywhere}
.arr{display:inline-flex;align-items:center;gap:8px;padding:12px 8px;font-weight:500;color:var(--fg);max-width:100%}
.arr span,.cl{color:var(--acc);transition:transform .3s cubic-bezier(.4,0,.2,1)}
.acts{display:flex;flex-direction:column;gap:16px;align-items:flex-start;margin-top:8px;max-width:100%}
.acts.full{align-self:stretch;align-items:stretch}
@media (hover:hover){.btn:hover{background:var(--fg);color:var(--bg)}.arr:hover span,a:hover>.cl{transform:translateX(4px)}}
.btn:active{background:var(--fg);color:var(--bg)}
.ul{border-bottom:1px solid var(--line2);padding-bottom:2px;transition:border-color .3s cubic-bezier(.4,0,.2,1);overflow-wrap:anywhere}
@media (hover:hover){.ul:hover{border-color:var(--fg)}}

/* header: rides over the opening and leaves with it */
.hd{position:absolute;top:0;left:0;width:100%;z-index:20;background:transparent;color:var(--L);transition:background-color .3s cubic-bezier(.4,0,.2,1),color .3s cubic-bezier(.4,0,.2,1)}
.hd .w{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:20px;min-height:72px}
.bm{font:700 1.125rem/1.15 "Albert Sans",sans-serif;letter-spacing:-.01em;max-width:68vw}
.bm img{height:20px;width:auto}
.nv{display:none}
.mn summary{list-style:none;cursor:pointer;width:32px;height:32px;border-radius:2px;background:var(--accfill);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}
.mn summary::-webkit-details-marker{display:none}
.mn summary i{display:block;width:12px;height:1px;background:var(--onacc)}
.mn[open] summary{outline:1px solid var(--onacc)}
.mp{position:absolute;left:0;top:100%;width:100%;background:var(--accfill);color:var(--onacc);padding:28px 20px 36px;display:flex;flex-direction:column;align-items:center;gap:34px;font:500 1rem/1.5 "Albert Sans",sans-serif;text-align:center;animation:fade .3s cubic-bezier(.4,0,.2,1) both}
.hd:has(.mn[open]){background:var(--accfill);color:var(--onacc)}
@keyframes fade{from{opacity:0}to{opacity:1}}

/* opening */
.hero{position:relative;display:flex;flex-direction:column;justify-content:flex-end;min-height:100svh;padding:0 20px 50px;overflow:hidden}
.hz{position:absolute;inset:0;z-index:0;animation:zoom 2s cubic-bezier(.16,1,.3,1) both;will-change:transform}
.hz img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center}
.hz div{position:absolute;inset:0}
.v1{background:linear-gradient(to top,rgb(var(--dv)) 0,rgba(var(--dv),.9) 50%,rgba(var(--dv),.84) 100%)}
.v2{background:linear-gradient(to right,rgba(var(--dv),.92) 0,rgba(var(--dv),.8) 30%,rgba(var(--dv),.45) 55%,rgba(var(--dv),0) 100%)}
.hz .v3{bottom:auto;height:176px;background:linear-gradient(rgba(var(--dv),.88) 0,rgba(var(--dv),.86) 50%,rgba(var(--dv),0) 100%)}
.hx{position:relative;z-index:1;width:100%;max-width:1180px;margin-top:72px}
.hx .eye{margin-bottom:24px;color:var(--acch)}
h1{font-size:clamp(2.4rem,5.5vw,6rem);line-height:1.05;letter-spacing:-.02em;max-width:8.9em;text-wrap:balance}
.hl{margin-top:20px;font-size:1.125rem;line-height:1.56;color:var(--m85);max-width:52ch}
.hc{margin-top:32px;display:grid;grid-template-columns:1fr;gap:1px;background:rgba(var(--lv),.15);border:1px solid rgba(var(--lv),.15);max-width:920px}
.hc a{display:flex;flex-direction:column;gap:10px;padding:24px;background:rgba(var(--dv),.7);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);transition:background-color .3s cubic-bezier(.4,0,.2,1)}
@media (hover:hover){.hc a:hover{background:rgba(var(--dv),.9)}}
.hc a:active{background:rgba(var(--dv),.9)}
.ct{display:flex;align-items:center;gap:10px}
.ct i{flex:none;width:8px;height:8px;background:var(--mark);transform:rotate(45deg)}
.ct b{font:500 1.125rem/1.55 "Alegreya Sans",sans-serif}
.cx{font-size:.875rem;line-height:1.375;color:var(--m75)}
.cl{margin-top:auto;padding-top:4px;font:500 .875rem/1.43 "Albert Sans",sans-serif;align-self:flex-start}
.hero .acts{margin-top:36px}
.rise{animation:rise .7s cubic-bezier(.16,1,.3,1) both}
.r2{animation-delay:.15s}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes zoom{from{transform:scale(1.08)}to{transform:scale(1)}}

/* numbered rows with a turned square */
.drow{display:flex;gap:24px;align-items:flex-start;padding:28px 0;border-top:1px solid var(--line)}
.drow:first-child{border-top:0}
.dia{flex:none;width:36px;height:36px;margin-top:4px;border:2px solid var(--mark);transform:rotate(45deg);display:flex;align-items:center;justify-content:center}
.dia span{transform:rotate(-45deg);font:700 .875rem/1.43 "Albert Sans",sans-serif;color:var(--acc)}
.db{flex:1;min-width:0;display:flex;flex-direction:column;gap:8px}
.db h3{font-size:1.25rem;line-height:1.4;display:flex;flex-wrap:wrap;justify-content:space-between;gap:4px 20px}
.db p{font-size:1rem;line-height:1.625;color:var(--m60)}
.pv{color:var(--acc)}
.nt{color:var(--m75)!important}
.st{font:400 .7rem/1.5 "JetBrains Mono",monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--m60)}
.pl{margin-top:8px;border-top:1px solid var(--line)}
.pl li{padding:10px 0;border-bottom:1px solid var(--line);font-size:1rem;line-height:1.375;color:var(--m75)}
.pl.pr li{display:flex;justify-content:space-between;gap:20px}
.pl.pr b{font-weight:500;color:var(--fg);text-align:right}

/* ruled rows: a name and what belongs to it */
.rrows{border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.rrow{display:flex;flex-direction:column;gap:4px;padding:16px 0;border-top:1px solid var(--line)}
.rrow:first-child{border-top:0}
.rrow h3{font-size:1.125rem;line-height:1.55}
.rb{flex:1;min-width:0;display:flex;flex-direction:column;gap:8px}
.rb p{font-size:1rem;line-height:1.375;color:var(--m60)}
.rb .rt{color:var(--fg);font-weight:500}

/* figure rows: a value in the accent, its meaning beside it */
.figs{display:grid;grid-template-columns:fit-content(46%) minmax(0,1fr);column-gap:20px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.frow{display:grid;grid-template-columns:subgrid;grid-column:1/-1;align-items:baseline;padding:14px 0;border-top:1px solid var(--line)}
.frow:first-child{border-top:0}
.fv{font:500 1.5rem/1.33 "Alegreya Sans",sans-serif;color:var(--acc);min-width:92px}
.fl{min-width:0;display:flex;flex-direction:column;gap:8px}
.fgt{font-size:1rem;line-height:1.5;color:var(--m85)}
.fn{color:var(--m60)}
.fl>p:not(.fgt){font-size:1rem;line-height:1.375;color:var(--m60)}
.figs.stack{display:block}
.figs.stack .frow{display:flex;flex-direction:column;gap:4px}

/* the panel */
.card{border:1px solid var(--line);border-radius:14px;padding:24px;box-shadow:0 25px 50px -12px rgba(0,0,0,.25)}
.ch{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-bottom:20px;border-bottom:1px solid var(--line)}
.ch span{display:flex;align-items:center;gap:12px;font-size:.875rem;line-height:1.43;font-weight:500}
.ch i{flex:none;width:10px;height:10px;border-radius:50%;background:var(--mark)}
.ch em{font:500 .75rem/1.33 "JetBrains Mono",monospace;letter-spacing:.2em;font-style:normal;color:var(--m60)}
.card li{display:flex;gap:16px;padding:16px 0;border-top:1px solid var(--line)}
.card li:first-child{border-top:0}
.card li:last-child{padding-bottom:0}
.card li>div{flex:1;min-width:0}
.cy{flex:none;width:44px;padding-top:4px;font:500 .65rem/1.5 "JetBrains Mono",monospace;letter-spacing:.15em;color:var(--acc)}
.c1{font-size:.875rem;line-height:1.375}
.c2{font-size:.875rem;line-height:1.375;color:var(--m65);margin-top:4px}
.card .bg{flex:none;height:44px;width:auto;align-self:center}

/* ruled cells */
.cells,.qcells,.gcells{display:grid;grid-template-columns:1fr;gap:1px;background:var(--line);border:1px solid var(--line)}
.cell{background:var(--bg);padding:28px;display:flex;flex-direction:column;gap:12px}
.cell i{width:40px;height:4px;border-radius:4px;background:var(--mark)}
.cell h3{font-size:1.25rem;line-height:1.4}
.cell p{font-size:1rem;line-height:1.625;color:var(--m60)}
.cell .sm{font-size:.875rem;line-height:1.45}
.qcells figure{background:var(--bg);padding:32px;display:flex;flex-direction:column;gap:24px}
.qm{font:400 3rem/1 "Alegreya Sans",sans-serif;color:var(--acc);height:28px}
.qcells blockquote{font:400 1.125rem/1.375 "Alegreya Sans",sans-serif;flex:1}
.qcells figcaption{display:flex;flex-direction:column;gap:2px;padding-top:16px;border-top:1px solid var(--line2)}
.qcells b{font-weight:500}
.qcells figcaption span{font:400 .7rem/1.5 "JetBrains Mono",monospace;letter-spacing:.18em;text-transform:uppercase;color:var(--m60)}
.gcells{grid-template-columns:1fr 1fr}
.gc{background:var(--bg);padding:20px;display:flex;flex-direction:column;gap:4px;transition:background-color .3s cubic-bezier(.4,0,.2,1)}
.gc b{font:500 1.125rem/1.375 "Alegreya Sans",sans-serif}
.gc span{font-size:.875rem;line-height:1.4;color:var(--m60)}
@media (hover:hover){.gc:hover{background:var(--line)}}
.gap{margin-top:48px}

/* a photograph as tall as its section, bleeding off the page edge */
.half{position:relative;aspect-ratio:var(--ar);width:100%;overflow:clip;background:var(--D2)}
.half img{width:100%;height:100%;object-fit:cover}
.half-l{margin:0 0 30px}
.half-r{margin:30px 0 0}

/* a wide photograph with a line of type on its calm side */
.band{position:relative;overflow:hidden;display:flex;align-items:flex-start;min-height:320px}
.band>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.bv{position:absolute;inset:0;background:rgba(var(--dv),.88)}
.band .w{position:relative;background:none;padding-top:50px;padding-bottom:50px}
.c-band{grid-column:1/-1;display:flex;flex-direction:column;gap:24px}
.c-band p{font:500 1.5rem/1.2 "Albert Sans",sans-serif;letter-spacing:-.02em;text-wrap:pretty}
.c-band cite,.c-band h2{font:500 .875rem/1.43 "JetBrains Mono",monospace;letter-spacing:.25em;text-transform:uppercase;font-style:normal;color:var(--m75)}
.c-band{flex-direction:column}.c-band h2{order:2}

/* people */
.tg{display:grid;grid-template-columns:1fr 1fr;gap:40px 20px}
.tg.one{grid-template-columns:1fr}
.tp{position:relative;aspect-ratio:433/542;background:var(--D2);overflow:hidden;margin-bottom:20px}
.tp img{width:100%;height:100%;object-fit:cover;object-position:50% 0;filter:grayscale(.15)}
.tp::after{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(var(--dv),.45),rgba(var(--dv),0))}
.tm h3,.tl h3{font-size:1.25rem;line-height:1.4}
.tr{display:block;margin-top:6px;font:400 .7rem/1.5 "JetBrains Mono",monospace;letter-spacing:.18em;text-transform:uppercase;color:var(--acc)}
.tx{margin-top:12px;font-size:1rem;line-height:1.5;color:var(--m65)}
.tc{margin-top:10px;font-size:.875rem;line-height:1.6;color:var(--m75);display:flex;flex-wrap:wrap;gap:2px 16px}
.tc a{border-bottom:1px solid var(--line2);overflow-wrap:anywhere}
.tls{margin-top:56px;border-bottom:1px solid var(--line)}
.tg+.tls{margin-top:64px}
.hd2+.tls{margin-top:0}
.tl{display:flex;flex-direction:column;gap:4px;padding:16px 0;border-top:1px solid var(--line)}
.tl .tr{margin-top:0}
.tl .tx{margin-top:6px;font-size:.9375rem}

/* named work */
.two{display:grid;grid-template-columns:1fr;gap:32px;margin-top:32px}
.fp{aspect-ratio:16/9;background:var(--D2);overflow:hidden;margin-bottom:16px}
.fp img{width:100%;height:100%;object-fit:cover}
.two figcaption{display:flex;flex-direction:column;gap:8px}
.two figcaption span{font:500 .7rem/1.5 "JetBrains Mono",monospace;letter-spacing:.18em;text-transform:uppercase;color:var(--acc)}
.two p{font-size:1rem;line-height:1.625;color:var(--m60);max-width:60ch}

/* plans */
.pns{display:grid;grid-template-columns:1fr;gap:24px}
.pns>*{grid-column:auto!important}
.pn{border:1px solid var(--line);border-radius:12px;padding:32px;display:flex;flex-direction:column;gap:20px;align-items:flex-start}
.pn.mk{border-color:var(--acc)}
.pn>i{width:40px;height:1px;background:var(--mark)}
.pn h3{font-size:1.5rem;line-height:1.25}
.pn h3 span{color:var(--acc)}
.pn h3 small{font:400 .875rem/1.4 "Albert Sans",sans-serif;color:var(--m65)}
.pn p{font-size:1rem;line-height:1.625;color:var(--m75)}
.pn .pl{align-self:stretch;margin-top:0}
.pn .btn{margin-top:auto}
.nod .drow{padding:24px 0}

/* contact */
.h2c{font-size:2.4rem;line-height:1.08;letter-spacing:-.03em}
.det{display:flex;flex-direction:column;gap:16px;padding-top:24px;border-top:1px solid var(--line)}
.det>div{display:flex;flex-direction:column;gap:4px;align-items:flex-start}
.lb{font:400 .7rem/1.5 "JetBrains Mono",monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--m60)}
.det a{font-weight:500}
.pv2{color:var(--m75)}
.so{flex-direction:row!important;flex-wrap:wrap;gap:8px 20px!important}

/* close */
.fin{padding:100px 0;text-align:center}
.fin .c-all{display:flex;flex-direction:column;align-items:center;gap:24px}
.fin h2{max-width:18ch}
.fin .ld{max-width:52ch}
.fin .acts{align-items:center;margin-top:16px}

/* foot */
.ft{padding:100px 0 50px}
.ft.rule{border-top:1px solid var(--line)}
.ft .w{row-gap:48px}
.fa{grid-column:1/-1;display:flex;flex-direction:column;gap:24px;align-items:flex-start}
.ft .bm{font-size:1.5rem;max-width:100%}
.ft .bm img{height:34px}
.tg2{font:400 1.25rem/1.375 "Alegreya Sans",sans-serif;color:var(--m85);max-width:22ch}
.fx{font-size:.95rem;line-height:1.5;color:var(--m75);max-width:38ch}
.fa .ul{color:var(--m75);transition:color .3s cubic-bezier(.4,0,.2,1)}
.fa .so{display:flex;gap:16px}
.fa .so a,.fb a{color:var(--m75);transition:color .3s cubic-bezier(.4,0,.2,1)}
@media (hover:hover){.fa a:hover,.fb a:hover,.fz a:hover{color:var(--fg)}.nv a:hover{opacity:.7}}
.fb{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:40px 24px}
.fb div{display:flex;flex-direction:column;gap:16px;min-width:0}
.fb .eye{color:var(--acc);overflow-wrap:anywhere}
.fb ul{display:flex;flex-direction:column;gap:12px}
.fb a,.fb li>span{font-size:.95rem;line-height:1.5;color:var(--m75);overflow-wrap:anywhere}
.fz{margin-top:64px;padding-top:24px;border-top:1px solid var(--line);row-gap:16px!important}
.fz p{grid-column:span 2;font:400 .7rem/1.5 "JetBrains Mono",monospace;letter-spacing:.18em;text-transform:uppercase;color:var(--m60)}
.fz a{transition:color .3s cubic-bezier(.4,0,.2,1)}
.fz .fk{text-align:right}

@media (min-width:640px){
 .hc.n3{grid-template-columns:repeat(3,1fr)}.hc.n2{grid-template-columns:repeat(2,1fr);max-width:614px}.hc.n1{max-width:307px}
 .acts{flex-direction:row;align-items:center}.acts.full{align-self:auto;align-items:center}
 .rrow{flex-direction:row;align-items:baseline;gap:20px}.rrow h3{flex:0 0 8.7em}
 .tl{flex-direction:row;align-items:baseline;gap:20px}.tl h3{flex:0 0 9.5em}.tl>div{flex:1;min-width:0}
 .figs.stack{display:grid}.figs.stack .frow{display:grid}
 .cells.k2,.cells.k3,.qcells.k2,.qcells.k3{grid-template-columns:1fr 1fr}
 .gcells.k4{grid-template-columns:repeat(4,1fr)}.gcells.k3{grid-template-columns:repeat(3,1fr)}.gcells.k1{grid-template-columns:1fr}
 .two{grid-template-columns:1fr 1fr}
 .pns.p2,.pns.p3,.pns.p4,.pns.p5{grid-template-columns:1fr 1fr}
 .fb{grid-template-columns:repeat(4,1fr)}
 .tg.one{grid-template-columns:1fr 1fr}
}
@media (max-width:639.9px){.cells>*,.qcells>*,.gcells.k1>*{grid-column:auto!important}.gcells>[style]{grid-column:1/-1!important}}
@media (min-width:640px) and (max-width:1023.9px){.cells>[style],.qcells>[style]{grid-column:auto!important}.cells>:last-child:nth-child(odd),.qcells>:last-child:nth-child(odd){grid-column:1/-1!important}}
@media (min-width:768px){
 h2{font-size:3rem}.ld{font-size:1.33rem}.hl{font-size:1.25rem;line-height:1.4}
 .c-band p{font-size:1.875rem}.band{min-height:400px}
}
@media (min-width:1024px){
 .w{grid-template-columns:repeat(12,minmax(0,1fr));padding:50px}
 .c-l{grid-column:1/span 5;margin-bottom:0}.c-r{grid-column:7/span 6}.c-r.mid{align-self:center}
 h2{font-size:4rem}.ld{font-size:1.5rem;line-height:1.6}.bd{font-size:1.125rem}
 .hd2{margin-bottom:64px}
 .hd .w{padding:24px 50px;min-height:126px}
 .bm{font-size:1.5rem;max-width:24ch}.bm img{height:32px}
 .mn{display:none}
 .nv{display:flex;align-items:center;gap:clamp(24px,3.47vw,50px);font:500 1.25rem/1.5 "Albert Sans",sans-serif;white-space:nowrap}
 .nv a{transition:opacity .3s cubic-bezier(.4,0,.2,1)}
 .hero{padding:0 50px 50px}.hx{margin-top:150px}
 .v1{background:linear-gradient(to top,rgb(var(--dv)) 0,rgba(var(--dv),.7) 50%,rgba(var(--dv),.25) 100%)}
 .hc{margin-top:40px}.hc a{padding:28px}.ct b{font-size:1.25rem;line-height:1.4}
 .db h3{font-size:1.5rem;line-height:1.33}.db p{font-size:1.125rem}
 .rrow h3{font-size:1.25rem;line-height:1.4}
 .fv{font-size:1.875rem;line-height:1.2;min-width:114px}.fgt{font-size:1.125rem;line-height:1.55}
 .card{padding:32px}.c1{font-size:1rem}
 .cells.k3,.qcells.k3{grid-template-columns:repeat(3,1fr)}
 .cell{padding:32px}.cell h3{font-size:1.5rem;line-height:1.33}.cell p{font-size:1.125rem}
 .qcells figure{padding:36px}.qcells blockquote{font-size:1.25rem}
 .gap{margin-top:64px}
 .pil.hashalf{min-height:780px;display:flex;align-items:center}
 .half{position:absolute;top:0;bottom:0;margin:0;aspect-ratio:auto}
 .half-l{left:0;width:calc((100% - 364px)*5/12 + 146px)}
 .half-r{right:0;width:calc((100% - 364px)*6/12 + 170px)}
 .half img{position:sticky;top:0;height:min(100%,100vh)}
 .bv{background:linear-gradient(to right,rgb(var(--dv)) 0,rgba(var(--dv),.86) 50%,rgba(var(--dv),.4) 100%)}
 .band{min-height:460px}.c-band{grid-column:1/span 8}.c-band p{font-size:2.125rem}
 .tg,.tg.one{grid-template-columns:repeat(3,1fr)}.tm h3{font-size:1.5rem;line-height:1.33}
 .tls{display:grid;grid-template-columns:1fr 1fr;column-gap:24px}.tls.solo{grid-template-columns:1fr}
 .h2c{font-size:4.05rem}
 .fa{grid-column:1/span 4}.fb{grid-column:6/span 7}.fb.k1{grid-column:12/span 1;grid-template-columns:1fr}.fb.k2{grid-column:9/span 4;grid-template-columns:1fr 1fr}.fb.k3{grid-column:7/span 6;grid-template-columns:repeat(3,1fr)}
 .ft .w{padding-top:50px}.tg2{font-size:1.5rem}.fz{margin-top:80px}.fz p{grid-column:span 6}
 .pn h3{font-size:1.875rem}.pn p{font-size:1.125rem}
 .pns.p2{grid-template-columns:repeat(2,1fr)}.pns.p3{grid-template-columns:repeat(3,1fr)}.pns.p4{grid-template-columns:repeat(4,1fr)}
 .pns.p5{grid-template-columns:repeat(6,1fr)}.pns.p5>*{grid-column:span 2!important}.pns.p5>[style]{grid-column:var(--sp)!important}
}
@media (min-width:1280px){h2{font-size:5rem}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.rise,.hz,.mp{animation:none}*,*::before,*::after{transition:none!important}}
"""
