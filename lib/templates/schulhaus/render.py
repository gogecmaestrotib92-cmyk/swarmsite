"""schulhaus/render.py — one pure function: render(d) -> a complete page. A template for PLACES, type-led.

The build (five-column grid, measures, type scale, spacing, the tile and its text face, the bar at the foot of the
window, the phone build, motion) was measured on the reference's home page and on its rooms, food and contact pages
at 1440 and 390 on 2026-11-12 (see NOTES.md). Nothing of the reference's code, words, pictures, logo or typefaces is
here. The client's data fills it; a section whose data is missing is left out whole. No model call, no file reads.
"""
import html

FONTS = ('https://fonts.googleapis.com/css2?family=Courier+Prime&family=Instrument+Serif:ital@0;1'
         '&family=Tinos:ital@0;1&display=swap')
WORDS = {'es': ('Menú', 'Cerrar'), 'en': ('Menu', 'Close'), 'de': ('Menü', 'Schließen'), 'fr': ('Menu', 'Fermer'),
         'it': ('Menu', 'Chiudi'), 'pt': ('Menu', 'Fechar'), 'sr': ('Meni', 'Zatvori'), 'sl': ('Meni', 'Zapri')}


def e(s):
    return html.escape(str(s or ''), quote=True)


# ───────────────────────── colour: one saturated ground for the whole page, one ink (the reference's relation)
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
    """The reference's page is its brand colour edge to edge with black type on it (8.3:1). So: ground = the client's
    accent, ink = the client's ink when it reads 7:1 on that, else black or white, whichever reads better; a mid-tone
    accent on which neither reaches 7:1 is moved away from the ink until it does."""
    g = p.get('accent') or p.get('ground') or '#ffffff'
    ink = p.get('ink') or '#000000'
    if _con(ink, g) < 7:
        ink = '#000000' if _con('#000000', g) >= _con('#ffffff', g) else '#ffffff'
    pole, t = ('#ffffff' if _lum(ink) < .5 else '#000000'), 0.0
    while _con(ink, _mix(pole, g, t)) < 7 and t < 1:
        t += .02
    return _mix(pole, g, min(t, 1)), ink


# ───────────────────────── the name as the mark: size from the measured width of the reference's mark
_NARROW, _WIDE = set("iljtfrI1.,:;!'|"), set('mwMW@&%')


def _em(s):
    """advance of a line in ems, Instrument Serif (calibrated in the browser on the two test names, see NOTES.md)"""
    w = 0.0
    for c in s:
        w += (.2 if c == ' ' else .24 if c in _NARROW else .66 if c in _WIDE else .56 if c.isupper()
              else .44 if c.isdigit() else .41)
    return w


def _mark(name):
    """one line when it fits the two columns at four fifths of the reference's size, else two balanced lines"""
    words = name.split()
    lines = [name]
    if _em(name) > 5.32 / .8 and len(words) > 1:
        cut = min(range(1, len(words)), key=lambda i: max(_em(' '.join(words[:i])), _em(' '.join(words[i:]))))
        lines = [' '.join(words[:cut]), ' '.join(words[cut:])]
    longest = max(_em(x) for x in lines)
    return lines, min(6.97, 37.08 / longest), min(11.37, 87.7 / longest)


# ───────────────────────── pictures
def _img(ph, cls='', sizes='40vw'):
    return ('<img%s src="../../%s" width="%d" height="%d" alt="%s" decoding="async" sizes="%s">'
            % (' class="%s"' % cls if cls else '', e(ph['src']), ph.get('w') or 4, ph.get('h') or 3, e(ph.get('alt')), sizes))


def _fits(ph, w, h):
    """may this photograph fill a w×h frame at 1440 without being drawn beyond its own pixels (10 % allowed; none
    for a picture marked small)?"""
    k = max(w / max(ph.get('w') or 1, 1), h / max(ph.get('h') or 1, 1))
    return k <= (1.0 if ph.get('small') else 1.1)


def _subject(ph):
    """what a photograph is of, as far as the data says: its file name without a trailing number, and the head of its
    description (up to the first colon or comma)"""
    stem = (ph.get('src') or '').rsplit('/', 1)[-1].rsplit('.', 1)[0]
    while stem and stem[-1].isdigit():
        stem = stem[:-1]
    head = (ph.get('alt') or '').replace(':', ',').split(',')[0].strip().lower()
    return stem.rstrip('-_'), head


def _same(a, b):
    """two shots of one thing: the same file name but for a trailing number, or the same head of the description"""
    (sa, ha), (sb, hb) = _subject(a), _subject(b)
    return sa == sb or bool(ha and ha == hb)


def _spend(pool, ph):
    """a photograph is shown once, and a second shot of the same thing is not shown on the page with it"""
    pool[:] = [p for p in pool if p is not ph and not _same(p, ph)]
    return ph


def _take(pool, w, h, roles=None, upright=False):
    """the first unused photograph that can fill the frame, preferring the given roles and, for the tall frames, the
    most upright one"""
    c = [p for p in pool if _fits(p, w, h)]
    if not c:
        return None
    if upright:
        c.sort(key=lambda p: (p.get('w') or 1) / (p.get('h') or 1))
    if roles:
        c.sort(key=lambda p: 0 if p.get('role') in roles else 1)
    return _spend(pool, c[0])


def _link(t, h, cls='ar'):
    if not t:
        return ''
    return '<a class="%s" href="%s"><span>%s</span></a>' % (cls, e(h), e(t)) if h else '<span class="%s nol"><span>%s</span></span>' % (cls, e(t))


def _seal(d):
    """the round house stamp of the reference, centred on the page: the client's own logo when there is one, else
    the name, the year and the town set in the page's faces"""
    b, pl = d.get('brand') or {}, d.get('place') or {}
    if b.get('logo'):
        return '<div class="seal" data-slot="seal"><img src="../../%s" alt="%s" width="192" height="192"></div>' % (e(b['logo']), e(b.get('name')))
    rows = ['<span class="s-n">%s</span>' % e(b.get('name'))] if b.get('name') else []
    if pl.get('since'):
        rows.append('<span class="s-y">%s</span>' % e(pl['since']))
    if (pl.get('address') or {}).get('city'):
        rows.append('<span class="s-n">%s</span>' % e(pl['address']['city']))
    return '<div class="seal" data-slot="seal" aria-hidden="true">%s</div>' % ''.join(rows) if rows else ''


# ───────────────────────── sections
def _links(d):
    return [x for x in (d.get('links') or []) if x.get('t')]


def _match_tiles(d, pool):
    """a tile's picture is one that belongs to it: a photograph from the page the tile leads to (`page` on the photograph,
    when the capture recorded it), or a dish for the tile that leads to the menu. Small pictures first — the large ones
    are needed by the tall frames further down."""
    menu_h = ((d.get('place') or {}).get('menu') or {}).get('h')
    got = {}
    for i, x in enumerate(_links(d)):
        is_menu = bool(menu_h and x.get('h') == menu_h)
        c = [p for p in pool if _fits(p, 266, 355) and ((x.get('h') and p.get('page') == x['h']) or (is_menu and p.get('role') == 'dish'))]
        if not c:
            continue
        c.sort(key=lambda p: (0 if (p.get('role') == 'dish') == is_menu else 1, 0 if p.get('small') else 1))
        got[i] = _spend(pool, c[0])
    return got


def _tiles(d, got, pool):
    """the tiles of the first screen: one per entry of `links`. A tile with a picture of its own shows it; one without
    shows the tile's text face (the reference's card: label at the top, sentence at the foot); one with neither picture
    nor sentence takes a picture of the place that is still unused, and failing that stays in the bar only."""
    out = []
    for i, x in enumerate(_links(d)):
        ph, face = got.get(i), ''
        if not ph and not x.get('d'):
            c = sorted((p for p in pool if p.get('role') != 'dish' and _fits(p, 266, 355)), key=lambda p: 0 if p.get('small') else 1)
            if not c:
                continue
            ph = _spend(pool, c[0])
        if x.get('d'):
            face = '<span class="face"><span class="f-t">%s</span><span class="f-d">%s</span></span>' % (e(x['t']), e(x['d']))
        if ph:
            out.append('<figure class="cell" data-slot="tile"><a class="tile pic%s" href="%s"%s>%s<span class="front">%s</span></a>'
                       '<figcaption>%s</figcaption></figure>'
                       % (' flip' if face else '', e(x.get('h')), '' if face else ' aria-label="%s"' % e(x['t']), face,
                          _img(ph, sizes='(min-width:1024px) 19vw, 36vw'), e(x['t'])))
        else:
            out.append('<div class="cell" data-slot="tile"><a class="tile txt" href="%s">%s</a></div>' % (e(x.get('h')), face))
    return out


def _opening(d, got, pool):
    b, h = d.get('brand') or {}, d.get('hero') or {}
    lines, fd, fm = _mark(b.get('name') or h.get('title') or '')
    tiles = _tiles(d, got, pool)
    a = ''.join('<p class="lg">%s</p>' % e(x) if x else '<span></span>' for x in (h.get('kicker'), h.get('title') if h.get('title') != b.get('name') else ''))
    intro = ''.join('<p class="lg">%s</p>' % e(x) for x in (h.get('text'), h.get('text2')) if x)
    h1 = '<h1 class="mark" style="--fd:%.3fvw;--fm:%.3fvw">%s</h1>' % (fd, fm, '<br>'.join(e(x) for x in lines))
    if tiles:
        tiles[0] = tiles[0].replace('class="cell"', 'class="cell t1"', 1)
    if len(tiles) > 1:
        tiles[1] = tiles[1].replace('class="cell"', 'class="cell t2"', 1)
    return ('<section class="op" data-slot="opening"><div class="op-g%s%s"><div class="op-a"><div class="op-l">%s</div>%s</div>'
            '%s<div class="op-p">%s</div>%s</div></section>'
            % ('' if tiles else ' not1', ' odd' if (len(tiles) - 1) % 2 else '', a, h1, tiles[0] if tiles else '', intro, ''.join(tiles[1:])))


def _statement(d):
    s = d.get('statement') or {}
    ps = [x for x in (s.get('title'), s.get('text')) if x]
    return '<section class="st" data-slot="statement">%s</section>' % ''.join('<p class="xl">%s</p>' % e(x) for x in ps) if ps else ''


def _tall(pool, roles, only=False):
    """a picture for a tall frame at the window's edge (596×900 at 1440), or for the same frame at 3:4; with `only`,
    pictures of the given roles are tried at both proportions before any other picture is"""
    if only:
        own = [p for p in pool if p.get('role') in roles]
        for hgt, cls in ((900, 'tall'), (795, 'tall t34')):
            t = _take(own, 596, hgt, None, True)
            if t:
                return _spend(pool, t), cls
    t = _take(pool, 596, 900, roles, True)
    return (t, 'tall') if t else (_take(pool, 596, 795, roles), 'tall t34')


def _house(d, tall, tall_c, small):
    """two short lines, a small picture, the stamp, and a tall picture to the window's edge"""
    s = d.get('steps') or {}
    seal = _seal(d)
    if not (s.get('title') or s.get('text') or tall or small or seal):
        return ''
    return ('<section class="ho%s" data-slot="house"><div class="ho-l">%s%s<div class="ho-b">%s%s</div></div>%s</section>'
            % ('' if tall else ' nopic', '<p class="lg ho-1">%s</p>' % e(s['title']) if s.get('title') else '',
               '<figure class="ho-s" data-slot="small">%s</figure>' % _img(small, sizes='(min-width:1024px) 23vw, 53vw') if small else '',
               '<p class="lg ho-2">%s</p>' % e(s['text']) if s.get('text') else '<span></span>', seal,
               '<figure class="%s" data-slot="tall">%s</figure>' % (tall_c, _img(tall, sizes='(min-width:1024px) 42vw, 77vw')) if tall else ''))


def _match_cards(d, pool):
    """one dish for each part of the menu that has a photograph from its own page"""
    got = {}
    for i, sec in enumerate(((d.get('place') or {}).get('menu') or {}).get('sections') or []):
        c = [p for p in pool if sec.get('h') and p.get('page') == sec['h'] and p.get('role') == 'dish' and _fits(p, 266, 355)]
        if c:
            got[i] = _spend(pool, c[0])
    return got


def _menu(d, tall, tall_c, small, cards):
    """the food block: tall picture at the left edge, small picture, a sentence, the link to the menu; under them the
    menu itself as the reference sets its lists (small label, arrowed lines)"""
    pl = d.get('place') or {}
    m = pl.get('menu') or {}
    secs, lists = m.get('sections') or [], m.get('lists') or []
    label = next((x.get('t') for x in (d.get('nav') or []) + (d.get('links') or []) if m.get('h') and x.get('h') == m['h']), None)
    text = ', '.join(pl.get('cuisine') or [])
    take = pl.get('takeaway') or {}
    if not (m.get('h') or secs or lists or text):
        return ''

    def row(name, h, right=''):
        inner = '<span>%s</span>%s' % (e(name), '<span class="r">%s</span>' % e(right) if right else '')
        return '<li>%s</li>' % ('<a href="%s">%s</a>' % (e(h), inner) if h else '<span class="x">%s</span>' % inner)
    groups, plain = [], [row(s.get('t'), s.get('h'), s.get('count') or '') for s in secs if s.get('t') and not s.get('items')]
    if plain:
        groups.append('<div class="grp">%s<ul>%s</ul></div>' % ('<h2 class="sm">%s</h2>' % e(label) if label else '', ''.join(plain)))
    for s in secs:
        its = [i for i in (s.get('items') or []) if i.get('name')]
        if not its:
            continue
        notes = {i.get('note') or '' for i in its}
        one = notes.pop() if len(notes) == 1 else ''
        groups.append('<div class="grp"><h2 class="sm">%s</h2><ul>%s</ul>%s</div>' % (
            e(s.get('t')), ''.join(row(i['name'] + ('' if one or not i.get('note') else ' (%s)' % i['note']), i.get('h'), i.get('price') or '') for i in its),
            '<p class="sm note">%s</p>' % e(one) if one else ''))
    if lists:
        groups.append('<div class="grp">%s<ul>%s</ul></div>' % ('' if plain or not label else '<h2 class="sm">%s</h2>' % e(label),
                                                              ''.join(row(x.get('t'), x.get('h'), x.get('count') or '') for x in lists if x.get('t'))))
    links = _link(label or (d.get('hero') or {}).get('secondary', {}).get('t') if m.get('h') else '', m.get('h'))
    if take.get('t'):
        links += _link(take['t'], take.get('h'))
    grid = ''.join('<figure class="cell" data-slot="dish"><a class="tile pic" href="%s" aria-label="%s"><span class="front">%s</span></a><figcaption>%s</figcaption></figure>'
                   % (e(secs[i].get('h')), e(secs[i].get('t')), _img(ph, sizes='(min-width:1024px) 19vw, 36vw'), e(secs[i].get('t'))) for i, ph in sorted(cards.items()))
    return ('<section class="me%s" data-slot="menu" id="menu">%s<div class="me-r"><div class="me-top">%s%s</div>'
            '%s%s</div></section>%s'
            % ('' if tall else ' nopic', '<figure class="%s" data-slot="tall">%s</figure>' % (tall_c, _img(tall, sizes='(min-width:1024px) 42vw, 77vw')) if tall else '',
               '<figure class="me-s" data-slot="small">%s</figure>' % _img(small, sizes='(min-width:1024px) 19vw, 53vw') if small else '',
               '<p class="lg">%s</p>' % e(text) if text else '', '<p class="me-a">%s</p>' % links if links else '',
               '<div class="me-l">%s</div>' % ''.join(groups) if groups else '',
               '<div class="me-g%s" data-slot="dishes">%s</div>' % (' odd' if len(cards) % 2 else '', grid) if grid else ''))


def _rooms(d, by_src):
    """the rooms, as the reference sets its houses: three columns, a small paragraph, the name, the picture under it"""
    sp = [s for s in ((d.get('place') or {}).get('spaces') or []) if s.get('title') or s.get('text')]
    if not sp:
        return ''
    phs = [by_src.get(s.get('img')) for s in sp]
    small = next((p for p in phs if p and (p.get('small') or not _fits(p, 414, 552))), None)
    ar = '%d/%d' % (small['w'], small['h']) if small else '3/4'       # one small picture sets the frame for the row
    cols = []
    for s, ph in zip(sp, phs):
        cols.append('<div class="ro-c"><p class="sm-t">%s</p>%s%s</div>' % (
            e(s.get('text')), '<p class="ro-n">%s</p>' % _link(s.get('title'), s.get('h')) if s.get('title') else '',
            '<figure data-slot="room" style="aspect-ratio:%s;max-width:%dpx">%s</figure>' % (ar, ph['w'], _img(ph, sizes='(min-width:1024px) 29vw, 88vw')) if ph else ''))
    return '<section class="ro" data-slot="rooms" style="--n:%d">%s</section>' % (min(len(cols), 3), ''.join(cols))


def _close(d, mid, mid_c, s1, s2):
    """a paragraph at the left, a tall picture, two small ones and a link at the right"""
    c = d.get('close') or {}
    ps = [x for x in (c.get('title'), c.get('text')) if x]
    cta = c.get('cta') or {}
    if not (ps or cta.get('t')):
        return ''
    return ('<section class="cl%s" data-slot="close"><div class="cl-t">%s</div>%s<div class="cl-r">%s%s%s</div></section>'
            % ('' if mid else ' nopic', ''.join('<p class="xl">%s</p>' % e(x) for x in ps),
               '<figure class="cl-m%s" data-slot="tall">%s</figure>' % (mid_c, _img(mid, sizes='(min-width:1024px) 38vw, 88vw')) if mid else '',
               '<figure class="cl-s" data-slot="small">%s</figure>' % _img(s1, sizes='(min-width:1024px) 17vw, 36vw') if s1 else '',
               '<p class="cl-a">%s</p>' % _link(cta.get('t'), cta.get('h')) if cta.get('t') else '',
               '<figure class="cl-s" data-slot="small">%s</figure>' % _img(s2, sizes='(min-width:1024px) 17vw, 36vw') if s2 else ''))


def _asks(d):
    """questions and answers, set as the reference sets what a guest should know: small label, then short paragraphs"""
    f = d.get('faq') or {}
    its = [x for x in (f.get('items') or []) if x.get('q')]
    if not its:
        return ''
    return ('<section class="fq" data-slot="faq">%s<div class="fq-l">%s</div></section>'
            % ('<h2 class="sm">%s</h2>' % e(f['title']) if f.get('title') else '',
               ''.join('<div class="fq-i"><h3 class="lg">%s</h3><p>%s</p></div>' % (e(x['q']), e(x.get('a'))) for x in its)))


def _plans(d):
    """prices, in the three columns of the reference's houses: small paragraph, name, the price large, what it holds"""
    pl = d.get('plans') or {}
    its = [x for x in (pl.get('items') or []) if x.get('name')]
    if not its:
        return ''
    cols = ''.join('<div class="pl-c"><h3 class="sm">%s</h3><p class="x3">%s%s</p>%s%s%s</div>' % (
        e(x['name']), e(x.get('price')), ' <span class="sm">%s</span>' % e(x['per']) if x.get('per') else '',
        '<p class="sm-t">%s</p>' % e(x['line']) if x.get('line') else '',
        '<ul class="pl-r">%s</ul>' % ''.join('<li><span class="x"><span>%s</span></span></li>' % e(r) for r in x.get('rows') or []) if x.get('rows') else '',
        '<p class="pl-a">%s</p>' % _link((x.get('cta') or {}).get('t') if isinstance(x.get('cta'), dict) else x.get('cta'), (x.get('cta') or {}).get('h') if isinstance(x.get('cta'), dict) else None) if x.get('cta') else '') for x in its)
    head = ''.join('<p class="%s">%s</p>' % (c, e(v)) for c, v in (('xl', pl.get('title')), ('lg', pl.get('text'))) if v)
    return ('<section class="pl" data-slot="plans">%s<div class="pl-g">%s</div>%s</section>'
            % ('<div class="pl-h">%s</div>' % head if head else '', cols, '<p class="sm pl-n">%s</p>' % e(pl['note']) if pl.get('note') else ''))


def _contact(d):
    """the reference's contact page: sentences at the left; hours, telephone and mail large at the right, the address
    under them; the booking where its form stands"""
    pl, b = d.get('place') or {}, d.get('brand') or {}
    left = []
    for ev in pl.get('events') or []:
        rows = [e(x) for x in (ev.get('when'), ev.get('what'), ev.get('price'), ev.get('where')) if x]
        cta = ev.get('cta') or {}
        if rows:
            left.append('<p class="lg">%s</p>%s' % ('<br>'.join(rows), '<p class="ev-a">%s</p>' % _link(cta.get('t'), cta.get('h')) if cta.get('t') else ''))
    note = (d.get('hero') or {}).get('note')
    if note:
        left.append('<p class="lg">%s</p>' % e(note))
    right = []
    hours = [x for x in (pl.get('hours') or []) if x.get('days')]
    if hours:
        right.append('<p class="x3">%s</p>' % '<br>'.join('%s <span class="nb">%s</span>' % (e(x['days']), e('–'.join(v for v in (x.get('open'), x.get('close')) if v))) for x in hours))
    ph = pl.get('phone') or {}
    if ph.get('t'):
        right.append('<p class="x3">%s</p>' % ('<a href="%s">%s</a>' % (e(ph['h']), e(ph['t'])) if ph.get('h') else e(ph['t'])))
    if pl.get('email'):
        right.append('<p class="x3"><a href="mailto:%s">%s</a></p>' % (e(pl['email']), e(pl['email'])))
    ad = pl.get('address') or {}
    l2 = ', '.join(x for x in (ad.get('street'), ' '.join(x for x in (ad.get('postcode'), ad.get('city')) if x), ad.get('region') or ad.get('country')) if x)
    if l2:
        right.append('<p class="lg ad">%s<br>%s</p>' % (e(ad.get('name') or b.get('name')), e(l2)))
    bk = pl.get('booking') or d.get('cta') or {}
    soc = [x for x in (pl.get('social') or []) if x.get('t')]
    if not (left or right or bk.get('t')):
        return ''
    return ('<section class="co" data-slot="contact" id="contact"><div class="co-l">%s</div><div class="co-r">%s%s%s</div></section>'
            % (''.join(left), ''.join(right),
               '<p class="co-a">%s</p>' % ''.join(_link(x['t'], x.get('h')) for x in soc) if soc else '',
               '<p class="co-b">%s</p>' % _link(bk.get('t'), bk.get('h'), 'ar bk') if bk.get('t') else ''))


def _foot(d):
    pl, f = d.get('place') or {}, d.get('foot') or {}
    nots = []
    for n in pl.get('notices') or []:
        im = ('<img src="../../%s" width="%d" height="%d" alt="" style="max-width:min(271px,%dpx)">' % (e(n['img']), n.get('w') or 4, n.get('h') or 3, n.get('w') or 271)) if n.get('img') else ''
        nots.append('<div class="no" data-slot="notice">%s<div>%s</div></div>' % (im, ''.join('<p>%s</p>' % e(t) for t in n.get('text') or [])))
    small = ''.join('<p class="sm">%s</p>' % e(x) for x in (f.get('text'), f.get('legal')) if x)
    return '<footer class="ft" data-slot="foot">%s%s</footer>' % (''.join(nots), small) if (nots or small) else ''


def _bar(d, words):
    """the reference's navigation: one line fixed to the foot of the window, entries divided by commas; on a phone a
    bordered button at the top right that lets a full panel down"""
    pl, f = d.get('place') or {}, d.get('foot') or {}
    prim = [x for x in (d.get('nav') or []) if x.get('t')]
    cta = d.get('cta') or pl.get('booking') or {}
    sec, seen = [], set()
    for x in (f.get('links') or []) + (pl.get('social') or []):
        if x.get('t') and x.get('h') not in seen:
            seen.add(x.get('h'))
            sec.append(x)
    li = lambda xs, c='': ''.join('<li%s><a href="%s">%s</a></li>' % (c, e(x.get('h')), e(x['t'])) for x in xs)
    p = li(prim) + (li([cta], ' class="end"') if cta.get('t') else '')
    if not (p or sec):
        return ''
    return ('<header class="bar"><div class="bar-top"></div><button class="mb" type="button" aria-expanded="false" aria-controls="nav" aria-label="%s" data-open="%s" data-close="%s"><i></i><i></i></button>'
            '<nav class="nv" id="nav" aria-label="%s"><ul class="n1">%s</ul><div class="n-b">%s%s</div></nav></header>'
            % (e(words[0]), e(words[0]), e(words[1]), e(words[0]), p, '<div class="n-seal">%s</div>' % _seal(d).replace(' data-slot="seal"', ''),
               '<ul class="n2">%s</ul>' % li(sec) if sec else ''))


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--ink);font-family:Tinos,'Times New Roman',Times,serif;font-size:16px;line-height:1.5;-webkit-font-smoothing:antialiased;overflow-x:hidden}
p,h1,h2,ul,figure{margin:0;padding:0}ul{list-style:none}
img{display:block;width:100%;height:100%;object-fit:cover}
a{color:inherit;text-decoration:none}
a:focus-visible,button:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
.lg{font-size:20px;line-height:1.42;letter-spacing:.48px}
.xl{font-size:26px;line-height:1.25;letter-spacing:.32px}
.nb{display:inline-block;white-space:nowrap}
.x3{font-size:clamp(28px,10.5vw,41px);line-height:1.2;letter-spacing:.32px;overflow-wrap:anywhere}
.sm,.ar,figcaption,.f-t,.me-l .r{font-family:'Courier Prime','Courier New',monospace;font-size:12px;line-height:1.42;letter-spacing:.48px;font-weight:400}
.sm-t{font-size:12px;line-height:1.42}
main{padding:80px 0 0}
section{position:relative}
/* the name */
.mark{font-family:'Instrument Serif','Times New Roman',serif;font-weight:400;font-size:var(--fm);line-height:.86;letter-spacing:-.01em;margin:47px 0 33px;white-space:nowrap}
/* arrowed links: the arrow moves 4px on hover, .3s ease-out (measured) */
.ar{display:inline-flex;align-items:center}
.ar>span{text-decoration:underline;text-underline-offset:2px}.ar.nol>span{text-decoration:none}
a.ar::after,.me-l li>*::before{content:"";flex:none;width:14px;height:10px;background:currentColor;-webkit-mask:var(--arw) center/contain no-repeat;mask:var(--arw) center/contain no-repeat}
a.ar::after{margin-left:4px;transition:transform .3s ease-out}
a.ar:hover::after{transform:translateX(4px)}
/* opening */
.op{padding:0 24px}
.op-g{display:grid;grid-template-columns:1fr 1fr;column-gap:68px}
.op-a{display:contents}
.op-l{grid-column:1/3;grid-row:1;display:grid;grid-template-columns:1fr 1fr;column-gap:68px;align-items:start;margin-bottom:12px}
.op-p{grid-column:1;grid-row:2;align-self:start}.op-p p+p{margin-top:1.42em}
.not1 .op-p{grid-column:1/3}
.t1{grid-column:2;grid-row:2;align-self:end}
.op-g .mark{grid-column:1/3;grid-row:3}
.op-g>.cell:not(.t1){margin-bottom:15px}
.op-g.odd>.cell:last-child:not(.t1){grid-column:2}
.cell{position:relative;min-width:0}
.tile{display:block;position:relative;aspect-ratio:3/4;perspective:2800px}
.tile .front{position:absolute;inset:0;z-index:1;display:block;transform-origin:left center;backface-visibility:hidden;transition:transform .7s}
.tile.pic .face{display:none}
.face{position:absolute;inset:0;display:flex;flex-direction:column}
.f-t{display:block;padding-bottom:8px}
.f-d{display:block;margin-top:auto;font-size:13px;line-height:1.38;overflow-wrap:break-word}
figcaption{margin-top:10px;min-height:17px}
/* statement */
.st{padding:67px 24px 0}.st p+p{margin-top:31px}
/* house */
.ho{padding:32px 0 0}
.ho-l{padding:0 24px}
.ho-s{width:205px;aspect-ratio:3/4;margin:48px auto 47px}
.ho-b{display:flex;flex-direction:column;gap:29px}
.ho-1+.ho-b{margin-top:29px}
.seal{width:137px;margin:0 auto;text-align:center;display:flex;flex-direction:column;align-items:center}
.seal{mix-blend-mode:var(--blend)}.seal img{width:auto;height:78px;object-fit:contain}
.s-n{font-family:'Courier Prime','Courier New',monospace;font-size:12px;line-height:1.3;letter-spacing:1.6px}
.s-y{font-family:'Instrument Serif',serif;font-style:italic;font-size:26px;line-height:1.1}
.tall{width:76.4vw;aspect-ratio:298/397;margin:28px 0 0 auto;position:relative;z-index:1}
.me .tall{margin:0 auto 0 0}
/* menu */
.me{padding:32px 0 0}
.me-r{padding:0 24px}
.me-s{width:205px;aspect-ratio:3/4;margin:43px auto 44px}
.me.nopic .me-top>.lg:first-child{margin-top:0}
.me-a{margin-top:16px;display:flex;flex-wrap:wrap;gap:8px 24px}
.me-l{margin-top:48px;display:grid;gap:32px}
.grp h2{margin-bottom:16px}
.me-l li{font-size:14px;line-height:1.42}
.me-l li>*{display:flex;align-items:baseline;gap:6px;padding:0}
.me-l li>*::before{align-self:center}
.me-l li>*>span:first-of-type{flex:1;min-width:0}
.me-l a:hover>span:first-of-type{text-decoration:underline;text-underline-offset:2px}
.me-l .r{white-space:nowrap;font-variant-numeric:tabular-nums}
.note{margin-top:12px}
/* dishes: the reference's five-column card grid */
.me-g{display:grid;grid-template-columns:1fr 1fr;gap:15px 68px;padding:48px 24px 0}
.me-g.odd>.cell:last-child{grid-column:2}
/* questions, prices */
.fq,.pl{padding:64px 24px 0}
.fq>h2{margin-bottom:16px}
.fq-i+.fq-i{margin-top:24px}
.fq-i p,.pl-r li{font-size:14px;line-height:1.42}
.fq-i p{margin-top:8px}
.pl-h>*+*{margin-top:16px}.pl-g{display:grid;gap:48px;margin-top:32px}
.pl-c>*+*{margin-top:12px}
.pl-r li>*{display:flex;align-items:baseline;gap:6px}
.pl-r li>*::before{content:"";flex:none;align-self:center;width:14px;height:10px;background:currentColor;-webkit-mask:var(--arw) center/contain no-repeat;mask:var(--arw) center/contain no-repeat}
.pl-n{margin-top:24px}
/* rooms */
.ro{padding:64px 24px 0;display:grid;gap:60px}
.ro-n{margin-top:16px}
.ro figure{margin-top:20px;width:100%}
/* close */
.cl{padding:32px 24px 0;display:grid;grid-template-columns:1fr 1fr;column-gap:68px}
.cl-t,.cl-m,.cl-r{grid-column:1/3}
.cl-t p+p{margin-top:.6em}
.cl-m{aspect-ratio:3/4;margin-top:12px}.cl-m.sq{aspect-ratio:1}.cl-m.l32{aspect-ratio:3/2}
.cl-r{display:grid;grid-template-columns:1fr 1fr;column-gap:68px;margin-top:36px}
.cl-s{aspect-ratio:3/4}
.cl-a{grid-column:1/3;grid-row:2;margin-top:17px}
.cl-r:not(:has(.cl-s)){margin-top:0}
/* contact */
.co{padding:64px 24px 0}
.co-l>*+*{margin-top:16px}
.co-l .ev-a{margin-top:12px}
.co-r{text-align:right;margin-top:24px}
.co-l:empty+.co-r{margin-top:0}
.co-r .x3+.x3{margin-top:11px}
.co-r .x3 a{text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:4px}
.ad{margin-top:17px}
.co-a{margin-top:16px;display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px 20px}
.co-b{margin-top:40px}
.bk{border:1px solid var(--ink);padding:9px 10px;min-height:36px}
.bk>span{text-decoration:none}
/* foot */
.ft{padding:64px 24px 0}
.no{display:grid;gap:20px}.no img{height:auto;object-fit:contain}
.no p{font-size:14px;line-height:1.42}.no p+p{margin-top:.71em}
.ft>.sm{margin-top:24px;overflow-wrap:anywhere}.ft>.sm+.sm{margin-top:4px}
body::after{content:"";display:block;height:48px}
/* navigation on a phone: button top right, panel let down in .7s cubic-bezier(.4,0,.2,1) (measured) */
.bar-top{position:fixed;left:0;top:0;width:100%;height:80px;background:var(--g);z-index:10}
.mb{position:fixed;right:24px;top:24px;z-index:50;width:55px;height:30px;border:1px solid var(--ink);background:var(--g);color:inherit;padding:0;cursor:pointer;display:none;border-radius:0}
.js .mb{display:block}
.mb i{position:absolute;left:14px;right:14px;height:1px;background:var(--ink);top:11px;transition:transform .3s}
.mb i+i{top:17px}
.mb[aria-expanded=true] i{transform:translateY(3px) rotate(28deg)}
.mb[aria-expanded=true] i+i{transform:translateY(-3px) rotate(-28deg)}
.nv{background:var(--g)}
.js .nv{position:fixed;left:0;top:0;width:100%;z-index:30;height:0;overflow:hidden;visibility:hidden;display:flex;flex-direction:column;justify-content:space-between;padding:0 24px;transition:height .7s cubic-bezier(.4,0,.2,1),padding .7s cubic-bezier(.4,0,.2,1),visibility 0s .7s}
.js .nv.open{height:100vh;height:100dvh;padding:80px 24px 40px;visibility:visible;overflow-y:auto;transition:height .7s cubic-bezier(.4,0,.2,1),padding .7s cubic-bezier(.4,0,.2,1)}
html:not(.js) .bar-top{display:none}html:not(.js) .nv{padding:48px 24px 0}html:not(.js) .n-seal{display:none}
.n1 li{font-size:20px;line-height:1.25;letter-spacing:.32px}.n1 li+li{margin-top:8px}
.n1 li.end{text-align:right}
.n-seal{margin:32px 0}
.n2{display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px 20px;font-size:14px;line-height:1.42;letter-spacing:.48px}
html:not(.js) .n2{margin-top:24px}
@media (min-width:600px) and (max-width:1023.9px){
.ho-s,.me-s{width:36vw}.seal{width:167px}
}
@media (min-width:1024px){
main{padding:26px 0 0}
.lg{line-height:1.25;letter-spacing:.32px}
.xl{line-height:1.2}
.x3{font-size:41px;line-height:1.22}
.mark{font-size:var(--fd);margin:0 0 6px}
.op{padding:0 30px}
.op-g{grid-template-columns:repeat(5,minmax(0,1fr));gap:48px 12px}
.op-a{grid-column:1/3;grid-row:1;display:flex;flex-direction:column;justify-content:space-between;min-height:calc((100vw - 108px)/5*4/3 + 6px)}
.op-l{grid-template-columns:60% 40%;column-gap:0;margin:0}
.op-l p:first-child{padding-right:24px}
.t1{grid-column:3;grid-row:1;align-self:start}
.op-p,.not1 .op-p{grid-column:4;grid-row:1;padding:0 0 0 8px}.op-p p+p{margin-top:1.25em}
.t2{grid-column:5;grid-row:1}
.op-g .mark{grid-column:auto;grid-row:auto}
.op-g>.cell:not(.t1){margin-bottom:0}
.op-g.odd>.cell:last-child:not(.t1){grid-column:auto}
.cell{padding-bottom:6px}
figcaption{position:absolute;left:0;top:100%;margin-top:12px;font-size:14px;white-space:nowrap}
.f-t{font-size:14px}.f-d{font-size:20px;line-height:1.25;letter-spacing:.32px}
.tile.pic.flip .face{display:flex}
.st{padding:121px 30px 0}
.ho{padding:56px 0 0;display:flex;align-items:stretch}
.ho-l{flex:1;min-width:0;padding:0 0 0 30px;display:flex;flex-direction:column;justify-content:space-between;position:relative}
.ho-1{max-width:325px}
.ho-s{width:22.57vw;margin:48px 0 48px 30%}
.ho:not(.nopic) .ho-s{margin-top:auto;margin-bottom:auto}
.ho-b{flex-direction:row;align-items:flex-end;justify-content:space-between;gap:24px;min-height:101px}
.ho-1+.ho-b{margin-top:48px}
.ho-2{max-width:534px;padding-bottom:16px}
.seal{width:167px;margin:0;position:absolute;left:calc(50vw - 30px);bottom:0;transform:translateX(-50%)}
.ho .seal{left:50vw}
.seal img{height:101px}
.s-y{font-size:30px}
.tall{flex:none;width:41.39vw;aspect-ratio:596/900;margin:0}
.tall.t34{aspect-ratio:3/4;align-self:flex-start}
.me{padding:64px 0 0;display:flex;align-items:flex-start}
.me-r{flex:1;min-width:0;padding:0 30px 0 0}
.me.nopic .me-r{margin-left:41.39vw}
.me-top{display:flex;align-items:flex-end;gap:20px}
.me-s{flex:none;width:18.82vw;margin:0}
.me-top>.lg{max-width:399px}
.me.nopic .me-top:not(:has(.me-s))>.lg,.me-top:not(:has(.me-s))>.lg{padding-left:20px}
.me-a{margin-top:47px;padding-left:20px;gap:8px 32px}
.me-top:empty+.me-a{margin-top:0}
.me-l{margin-top:64px;padding-left:20px;display:block;columns:2;column-gap:40px}
.me-top:empty+.me-l{margin-top:0}
.grp{break-inside:avoid;margin-bottom:32px}
.me-g{grid-template-columns:repeat(5,minmax(0,1fr));gap:48px 12px;padding:64px 30px 0}
.me-g.odd>.cell:last-child{grid-column:auto}
.me-g+*{margin-top:26px}
.fq,.pl{padding:64px 30px 0}
.fq-l{columns:2;column-gap:12px;max-width:1120px}.fq-i{break-inside:avoid;margin:0 0 24px!important;max-width:554px}
.pl-g{grid-template-columns:repeat(3,minmax(0,1fr));gap:48px 12px;padding-left:7.92vw}
.ro{padding:64px 30px 0 calc(30px + 7.92vw);grid-template-columns:repeat(3,minmax(0,1fr));gap:0 12px}.ro-c+.ro-c+.ro-c+.ro-c{margin-top:48px}
.ro-c{display:grid;grid-template-rows:subgrid;grid-row:span 3}
.ro-n{align-self:end}
.cl{padding:64px 30px 0;grid-template-columns:29.2fr 39.8fr 29.2fr;column-gap:12px;align-items:stretch}
.cl-t{grid-column:1}.cl-m{grid-column:2;aspect-ratio:549/900;margin:0}.cl-m.t34{aspect-ratio:3/4;align-self:start}.cl-m.sq{aspect-ratio:1;align-self:start}.cl-m.l32{aspect-ratio:3/2;align-self:start}
.cl-r{grid-column:3;display:flex;flex-direction:column;justify-content:space-between;align-items:flex-end;margin:0}
.cl-s{width:60%}
.cl-a{width:60%;margin:24px 0}
.cl.nopic{grid-template-columns:29.2fr 39.8fr 29.2fr}
.co{padding:64px 30px 0;display:grid;grid-template-columns:554fr 806fr;column-gap:12px;align-items:start}
.co-r{margin:0;padding-right:8px}
.co-r .x3+.x3{margin-top:20px}
.ad{margin-top:32px}
.co-b{margin-top:48px}
.ft{padding:64px 30px 0}
.no{grid-template-columns:271px minmax(0,554px);align-items:start}
body::after{height:97px}
/* navigation: one line fixed to the foot of the window */
.bar-top,.mb,.js .mb,.n-seal{display:none}
.bar .nv,.js .bar .nv{position:fixed;left:0;right:0;top:auto;bottom:0;z-index:20;height:auto;width:auto;visibility:visible;overflow:visible;display:flex;flex-direction:row-reverse;flex-wrap:wrap;justify-content:space-between;align-items:flex-start;gap:4px 24px;padding:16px 30px;transition:none}
.n1,.n2{display:flex;flex-wrap:wrap;margin:0!important}
.n1 li,.n2 li,.n2{font-family:'Courier Prime','Courier New',monospace;font-size:12px;line-height:1.42;letter-spacing:.48px}
.n1 li+li{margin-top:0}
.n1 li,.n2 li{position:relative;margin-right:8px}
.n1 li:last-child,.n2 li:last-child{margin-right:0}
.n1 li:not(:last-child) a::after,.n2 li:not(:last-child) a::after{content:","}
.n1 li::after,.n2 li::after{content:"";position:absolute;left:0;bottom:0;width:100%;height:1px;background:var(--ink);opacity:0;transition:opacity .3s}
.n1 li:hover::after,.n2 li:hover::after,.n1 li:focus-within::after,.n2 li:focus-within::after{opacity:1}
.n2{gap:0}
}
@media (min-width:1024px) and (max-width:1279.9px){.n1 li,.n2 li{font-size:10px;line-height:1.7}}
@media (min-width:1024px) and (hover:hover) and (prefers-reduced-motion:no-preference){
.tile.flip:hover .front,.tile.flip:focus-visible .front{transform:rotateY(-90deg)}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}}
"""

JS = r"""(function(){var D=document,b=D.querySelector('.mb'),n=D.getElementById('nav');if(!b||!n)return;
function set(o){n.classList.toggle('open',o);b.setAttribute('aria-expanded',o?'true':'false');b.setAttribute('aria-label',o?b.dataset.close:b.dataset.open);}
b.addEventListener('click',function(){set(!n.classList.contains('open'));});
D.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&n.classList.contains('open')){set(false);b.focus();}});
n.addEventListener('click',function(ev){if(ev.target.closest('a'))set(false);});
})();"""


def render(d: dict) -> str:
    b, h = d.get('brand') or {}, d.get('hero') or {}
    lang = (d.get('lang') or 'en')[:2].lower()
    words = WORDS.get(lang, WORDS['en'])
    g, ink = _theme(d.get('palette') or {})
    photos = [p for p in ((d.get('media') or {}).get('photos') or []) if p.get('src')]
    by_src = {p['src']: p for p in photos}
    room_srcs = {s.get('img') for s in ((d.get('place') or {}).get('spaces') or [])}
    pool = [p for p in photos if p['src'] not in room_srcs]      # a room's picture stands with its room
    c = d.get('close') or {}
    has_close = bool(c.get('title') or c.get('text') or (c.get('cta') or {}).get('t'))
    # the two tall frames at the window's edge first (few photographs can fill them), then each tile and each part of
    # the menu its own picture, then the frames of the closing block and the small frames from what is left
    ht, htc = _tall(pool, ('exterior', 'bar', 'room', 'people', 'other'))
    mt, mtc = _tall(pool, ('dish',), True)
    got = _match_tiles(d, pool)
    cards = _match_cards(d, pool)
    opening = _opening(d, got, pool)
    cm, cmc = None, ''
    if has_close:                      # the closing block's frame keeps its width and gives up height until a picture fills it
        for hgt, cls in ((900, ''), (732, ' t34'), (549, ' sq'), (366, ' l32')):
            cm, cmc = _take(pool, 549, hgt, ('room', 'exterior', 'bar', 'people', 'other'), hgt == 900), cls
            if cm:
                break
    dishes = [p for p in pool if p.get('role') == 'dish']            # the two small frames show food, or nothing
    hs = _take(dishes, 325, 434)
    ms = _take(dishes, 271, 362)
    for x in (hs, ms):
        if x:
            _spend(pool, x)
    c1, c2 = (_take(pool, 242, 323, ('room', 'exterior', 'bar', 'people')), _take(pool, 242, 323, ('room', 'exterior', 'bar', 'people'))) if has_close else (None, None)
    body = ''.join((opening, _statement(d), _house(d, ht, htc, hs), _menu(d, mt, mtc, ms, cards), _rooms(d, by_src),
                    _close(d, cm, cmc, c1, c2), _asks(d), _plans(d), _contact(d), _foot(d)))
    arw = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 14 10'%3E%3Cpath d='M0 5h13M9 1l4 4-4 4' "
           "fill='none' stroke='%23000' stroke-width='1'/%3E%3C/svg%3E\")")
    title = b.get('name') or h.get('title') or ''
    desc = h.get('text') or ''
    return ('<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>%s</title>\n%s<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="%s">\n<style>:root{--g:%s;--ink:%s;--blend:%s;--arw:%s}%s</style>\n'
            '<script>document.documentElement.className="js"</script>\n</head>\n<body>\n%s<main id="main">%s</main>\n<script>%s</script>\n</body>\n</html>\n'
            % (e(lang), e(title), '<meta name="description" content="%s">\n' % e(desc) if desc else '', FONTS, g, ink,
               'multiply' if _lum(ink) < .5 else 'normal', arw, CSS, _bar(d, words), body, JS))
