"""pcnw/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type, spacing, motion, phone layout) was measured on the reference's home page,
its rates page (the ruled price table) and its classes page (the two-across outlined cards, the band of outlined
links) at 1440 and 390 on 2026-11-12 — see NOTES.md. Nothing of the reference's code, words, pictures, icons, logos or
typefaces is here. The client's data fills it; a section whose data is missing is left out whole. No model call.
"""
import html
import re

FONTS = ('https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,400;0,700;1,400'
         '&family=Barlow+Condensed:wght@700&display=swap')
WORDS = {  # accessible names only (never visible): the data has no words for these controls
    'en': ('Menu', 'Previous', 'Next'), 'es': ('Menú', 'Anterior', 'Siguiente'), 'de': ('Menü', 'Zurück', 'Weiter'),
    'fr': ('Menu', 'Précédent', 'Suivant'), 'it': ('Menu', 'Precedente', 'Successivo'), 'sr': ('Meni', 'Prethodno', 'Sledeće')}


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


def _on(c, ground, ink):
    """the colour of words on a filled ground c: the page's ground or its ink, whichever reads; else white/black"""
    best = max((ground, ink, '#ffffff', '#0b0b0b'), key=lambda x: (_con(x, c) >= 4.5, x in (ground, ink), _con(x, c)))
    return best


def _fl(a, b):
    """a px at 390 wide → b px at 1440 wide (the two widths that were measured)"""
    if a == b:
        return '%gpx' % a
    lo, hi = min(a, b), max(a, b)
    return 'clamp(%gpx,calc(%gpx + %g*(100vw - 390px)/1050),%gpx)' % (lo, a, b - a, hi)


def _m(src):
    return '../../' + src if src and not re.match(r'(https?:|data:|/|\.\./)', src) else (src or '')


def _a(h, inner, cls='', extra=''):
    c = ' class="%s"' % cls if cls else ''
    if h:
        return '<a%s href="%s"%s>%s</a>' % (c, e(h), extra, inner)
    return '<span%s%s>%s</span>' % (c, extra, inner)


def _head(title, text='', link=None, tag='h2'):
    """the reference's section head: a 44.8px bold line (its part before a colon in the leading colour), one line of
    running text, a hairline"""
    if not title:
        return ''
    m = re.match(r'^([^:]{2,40}:)\s+(.+)$', title)
    t = '<span class="pre">%s</span> %s' % (e(m.group(1)), e(m.group(2))) if m else e(title)
    p = ''
    if text or link:
        l = ' <a class="tl" href="%s">%s</a>' % (e(link['h']), e(link['t'])) if link and link.get('h') and link.get('t') else ''
        p = '<p>%s%s</p>' % (e(text), l)
    return '<header class="sh"><%s>%s</%s>%s</header>' % (tag, t, tag, p)


# ───────────────────────── the page
def render(d: dict) -> str:
    brand = d.get('brand') or {}
    lang = (d.get('lang') or 'en')[:2]
    words = WORDS.get(lang, WORDS['en'])
    pal = d.get('palette') or {}
    ground, ink = pal.get('ground') or '#ffffff', pal.get('ink') or '#000000'
    if _con(ground, ink) < 4.5:
        ink = '#000000' if _lum(ground) > .4 else '#ffffff'
    # the reference's colours are deep ones that carry white words (green leads, orange second, then teal, purple):
    # here the palette's colours that read at 4.5:1 on the ground, in the palette's order; the ink closes the list
    cand = [c for c in [pal.get('accent')] + list(pal.get('extra') or []) if c]
    deep = []
    for c in cand + [ink]:
        if _con(c, ground) >= 4.5 and all(_con(c, x) < 1.25 or True for x in deep) and c.lower() not in [x.lower() for x in deep]:
            deep.append(c)
    P = deep[0]
    S = deep[1] if len(deep) > 1 else P
    lights = [c for c in cand if _con(c, ground) < 4.5 and _con(c, ground) >= 1.25]   # a light accent (yellow, gold)
    hot = lights[0] if lights else None
    SF = deep[1] if len(deep) > 1 else (hot or P)   # the second colour as a filled ground: a light accent may carry dark words
    onP, onS, onI = _on(P, ground, ink), _on(SF, ground, ink), _on(ink, ground, ink)
    tintP = _mix(onP, P, .5)      # the pale arrow on the slider's round buttons (and their ground under the pointer)
    t = .5
    while t < 1 and _con(tintP, P) < 3:      # an arrow is a control: 3:1 against the button it sits on
        t += .04
        tintP = _mix(onP, P, min(t, 1))
    # the disc behind the start of the closing call's label (drawn at .6, .75 under the pointer): the label is read on
    # it, so it is the reference's pale disc only as far as the label still reads 4.5:1 on it at .75; when that leaves
    # no visible disc, it goes the other way (darker under light words, paler under dark ones), which only adds contrast
    t = .5
    while t > 0 and _con(onP, _mix(onP, P, .75 * t)) < 4.5:
        t -= .02
    discP = _mix(onP, P, t) if t > 0 else P
    if _con(_mix(discP, P, .6), P) < 1.2:
        discP = _mix('#000000' if _lum(onP) > _lum(P) else '#ffffff', P, .5)
    tintS = _mix(onS, SF, .45)                                            # the large quotation mark
    btnh = next((c for c in deep if c.lower() != ink.lower()), None)     # the dark button's ground under the pointer
    btnh_on = _on(btnh, ground, ink) if btnh else None
    if not btnh:
        btnh = hot or _mix(ink, ground, .7)
        btnh_on = _on(btnh, ground, ink)
    cyc = deep[:4]

    media = d.get('media') or {}
    photos = [p for p in (media.get('photos') or []) if p.get('src')]
    team = d.get('team') or {}
    people = list(team.get('items') or [])
    for gr in team.get('groups') or []:
        people += [dict(p, _g=gr.get('t')) for p in gr.get('items') or []]
    taken = {p.get('img') for p in people if p.get('img')}
    taken |= {c.get('img') for c in d.get('credentials') or [] if c.get('img')}
    free = [p for p in photos if p['src'] not in taken and p.get('role') != 'portrait']
    is_small = lambda p: bool(p.get('small')) or max(p.get('w') or 0, p.get('h') or 0) < 1000
    wide = [p for p in free if not is_small(p) and (p.get('w') or 0) >= 1600 and (p.get('w') or 0) >= (p.get('h') or 0)]
    hero_ph = wide[0] if wide else None
    band_ph = wide[1] if len(wide) > 1 else None
    close_ph = wide[2] if len(wide) > 2 else None
    used = {p['src'] for p in (hero_ph, band_ph, close_ph) if p}
    group_ph = next((p for p in free if p['src'] not in used and not is_small(p) and p.get('role') == 'people'
                     and (p.get('w') or 0) >= 1000 and (p.get('w') or 0) > (p.get('h') or 0)), None)
    if group_ph:
        used.add(group_ph['src'])
    rest = [p for p in free if p['src'] not in used and (p.get('w') or 0) >= 240 and (p.get('w') or 0) >= (p.get('h') or 0)]
    strip = ([p for p in rest if p.get('role') == 'room'] + [p for p in rest if p.get('role') != 'room'])[:6]
    by_src = {p['src']: p for p in photos}

    hero = d.get('hero') or {}
    place = d.get('place') or {}
    contact = d.get('contact') or {}
    phone = contact.get('phone') or place.get('phone') or {}
    email = contact.get('email') or place.get('email')
    cta = d.get('cta') or hero.get('primary') or {}
    out = []

    # ── 0 notice: the black band of two bold centred lines above everything
    t2, note = (hero.get('text2') or '').strip(), (hero.get('note') or '').strip()
    lines = [x for x in ([t2] if t2 and len(t2) <= 60 else []) + [note] if x]
    if lines:
        def nl(x):
            return '<a href="%s">%s</a>' % (e(phone['h']), e(x)) if phone.get('h') and x == phone.get('t') else e(x)
        out.append('<div class="nt"><div class="nt-i">%s</div></div>' % ''.join('<p>%s</p>' % nl(x) for x in lines))

    # ── 1 the small row: telephone, mail, the other doors — where the reference keeps three small links and its social marks
    ut = []
    if phone.get('t'):
        ut.append(_a(phone.get('h'), e(phone['t'])))
    if email:
        ut.append('<a href="mailto:%s">%s</a>' % (e(email), e(email)))
    sg = d.get('signin') or {}
    if sg.get('t') and sg.get('h'):
        ut.append(_a(sg['h'], e(sg['t'])))
    social = [s for s in place.get('social') or [] if s.get('t') and s.get('h')]
    ut += ['<a href="%s" rel="noopener">%s</a>' % (e(s['h']), e(s['t'])) for s in social]
    if ut:
        out.append('<div class="ut">%s</div>' % ''.join(ut))

    # ── 2 header: mark left, capitals spread across, the dark button right; ruled above and below; scrolls away
    nav = [n for n in d.get('nav') or [] if n.get('t')]
    logo = ('<img src="%s" alt="%s">' % (e(_m(brand['logo'])), e(brand.get('name') or '')) if brand.get('logo')
            else '<b>%s</b>' % e(brand.get('name') or ''))
    navl = ''.join('<a href="%s">%s</a>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav)
    btn = '<a class="bt" href="%s">%s</a>' % (e(cta.get('h') or '#'), e(cta['t'])) if cta.get('t') else ''
    out.append('<header class="hd"><a class="lg" href="%s">%s</a><nav class="nv">%s</nav>%s'
               '<details class="mn"><summary aria-label="%s"><i></i></summary><div class="mp">%s%s%s</div></details></header>'
               % (e(brand.get('home') or '#'), logo, navl, btn, e(words[0]), navl, btn,
                  '<p>%s</p>' % ' '.join(ut[:2]) if ut else ''))

    # ── 3 opening: the picture across the page (¾ of the screen high), words set left at mid height
    title = (hero.get('title') or brand.get('name') or '').strip()
    hp = ''
    if hero_ph:
        hp = '<div class="bg" data-slot="hero" style="background-image:url(\'%s\');max-width:%dpx"></div>' % (e(_m(hero_ph['src'])), hero_ph['w'])
    out.append('<section class="hr%s">%s<div class="hr-i">%s<h1 class="%s">%s</h1>%s</div></section>'
               % ('' if hero_ph else ' plain', hp,
                  '<p class="kk">%s</p>' % e(hero['kicker']) if hero.get('kicker') else '',
                  'big' if len(title) <= 22 else '', e(title),
                  '<p class="ld">%s</p>' % e(hero['text']) if hero.get('text') else ''))
    hb = [b for b in (hero.get('primary'), hero.get('secondary')) if b and b.get('t')]
    if hb:
        out.append('<div class="pr">%s</div>' % ''.join('<a class="ob" href="%s">%s</a>' % (e(b.get('h') or '#'), e(b['t'])) for b in hb))

    # ── 4 the centred statement
    st = d.get('statement') or {}
    figures = [f for f in d.get('figures') or [] if f.get('v')]
    quotes = [q for q in d.get('quotes') or [] if q.get('q')]
    figs = lambda cls: '<dl class="fg %s">%s</dl>' % (cls, ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(f['v']), e(f.get('l') or '')) for f in figures))
    if st.get('title') or st.get('text'):
        out.append('<section class="in fx">%s%s%s</section>'
                   % ('<h2>%s</h2>' % e(st['title']) if st.get('title') else '',
                      '<p>%s</p>' % e(st['text']) if st.get('text') else '',
                      figs('fg-in') if figures and quotes else ''))

    # ── 5 the outlined cards (four across; two across, the classes-page build, when they are many or long)
    ft = d.get('features') or {}
    fi = [f for f in ft.get('items') or [] if f.get('t')]
    if fi:
        four = len(fi) == 4 and max(len(f.get('d') or '') for f in fi) <= 150
        cards = []
        for i, f in enumerate(fi):
            c = cyc[i % len(cyc)]
            back = ''
            if f.get('h'):
                back = '<a class="bk" href="%s"><b>%s</b>%s</a>' % (e(f['h']), e(f['t']), '<span>%s</span>' % e(f['cta']) if f.get('cta') else '')
            cards.append('<div class="cd%s%s" style="--c:%s;--o:%s"><h3>%s</h3>%s%s</div>'
                         % ('' if back else ' nb', ' last' if not four and len(fi) % 2 and i == len(fi) - 1 else '',
                            c, _on(c, ground, ink), e(f['t']), '<p>%s</p>' % e(f['d']) if f.get('d') else '', back))
        out.append('<section class="cs fx">%s<div class="cg %s">%s</div></section>'
                   % (_head(ft.get('title'), ft.get('text')), 'c4' if four else 'c2', ''.join(cards)))

    # ── 6 the price list: the band of outlined links (classes page) as its index, then the ruled table (rates page)
    cat = d.get('catalogue') or {}
    groups = [x for x in cat.get('groups') or [] if x.get('items')]
    if groups:
        idx = ''
        if len(groups) > 1:
            idx = '<div class="ix">%s</div>' % ''.join('<a class="wb" href="#g%d">%s <i>→</i></a>' % (n, e(x.get('t') or '')) for n, x in enumerate(groups) if x.get('t'))
        out.append('<section class="cb fx" id="prices"><h2>%s</h2>%s%s</section>'
                   % (e(cat.get('title') or ''), '<p>%s</p>' % e(cat['text']) if cat.get('text') else '', idx))
        rows = []
        has_note = any(i.get('note') for x in groups for i in x['items'])
        has_price = any(i.get('price') or i.get('prices') for x in groups for i in x['items'])
        cols = 1 + has_note + has_price
        colg = '<colgroup><col>%s%s</colgroup>' % ('<col class="k2">' if has_note else '', '<col class="k3">' if has_price else '')
        for n, x in enumerate(groups):
            its = x['items']
            g_note = any(i.get('note') for i in its)
            g_price = any(i.get('price') or i.get('prices') for i in its)
            if x.get('t'):
                rows.append('<tr class="gt" id="g%d"><th colspan="%d" scope="colgroup">%s</th></tr>' % (n, cols, _a(x.get('h'), e(x['t']))))
            if x.get('text'):
                rows.append('<tr class="gx"><td colspan="%d">%s</td></tr>' % (cols, e(x['text'])))
            for k, it in enumerate(its):
                z = ' class="z"' if k % 2 == 0 else ''
                nm = _a(it.get('h'), e(it.get('name') or ''))
                if it.get('state'):
                    nm += ' <em>%s</em>' % e(it['state'])
                if it.get('rows'):
                    nm += '<ul>%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in it['rows'])
                span = 1 + (has_note and not g_note) + (has_price and not g_price)
                tds = '<td class="n1"%s>%s</td>' % (' colspan="%d"' % span if span > 1 else '', nm)
                if g_note:
                    tds += '<td>%s</td>' % e(it.get('note') or '')
                if g_price:
                    pr = e(it.get('price') or '')
                    if it.get('prices'):
                        pr = '<br>'.join('%s %s' % (e(q.get('label') or ''), e(q.get('price') or '')) for q in it['prices'])
                    tds += '<td class="pz">%s</td>' % pr
                rows.append('<tr%s>%s</tr>' % (z, tds))
                if it.get('text'):
                    rows.append('<tr class="%s"><td colspan="%d">%s</td></tr>' % ('sb z' if z else 'sb', cols, e(it['text'])))
        out.append('<section class="tb"><table>%s%s</table>%s</section>'
                   % (colg, ''.join(rows), '<p class="tn">%s</p>' % e(cat['note']) if cat.get('note') else ''))

    # ── 7 the filled tiles (two in the first row at 60/40, three in the next), words at mid height
    def tiles(block, items):
        if not items:
            return
        rows, i, pat = [], 0, 2
        while i < len(items):
            n = min(pat, len(items) - i)
            if len(items) - i - n == 1 and n == 2 and pat == 2 and len(items) - i == 3:
                n = 3
            rows.append(items[i:i + n])
            i += n
            pat = 3 if pat == 2 else 2
        h = []
        for r, row in enumerate(rows):
            cells = []
            for c, it in enumerate(row):
                ph = by_src.get(it.get('img') or '')
                bgs = ''
                if ph and not is_small(ph) and (ph.get('w') or 0) >= 900 and ph['src'] not in used:
                    used.add(ph['src'])
                    bgs = ' style="background-image:url(\'%s\')"' % e(_m(ph['src']))
                col = SF if (r == 0 and c == 0 and SF != P) else P
                inner = ('%s<h3>%s</h3>%s%s' % ('<p class="k">%s</p>' % e(it['k']) if it.get('k') and it.get('k') != it.get('title') else '',
                                                 e(it.get('title') or ''), '<p>%s</p>' % e(it['text']) if it.get('text') else '',
                                                 '<p class="go">%s <i>→</i></p>' % e(it['cta']['t']) if (it.get('cta') or {}).get('t') else ''))
                href = (it.get('cta') or {}).get('h')
                cells.append('<%s class="tl%s"%s%s><span class="ov" style="--c:%s"></span><span class="tx" style="color:%s">%s</span></%s>'
                             % ('a' if href else 'div', ' ph' if bgs else '', ' href="%s"' % e(href) if href else '', bgs, col,
                                _on(col, ground, ink), inner, 'a' if href else 'div'))
            h.append('<div class="tr n%d%s">%s</div>' % (len(row), ' alt' if r % 2 else '', ''.join(cells)))
        out.append('<section class="ev fx">%s%s</section>' % (_head(block.get('title'), block.get('text')), ''.join(h)))

    sp = d.get('steps') or {}
    tiles(sp, [s for s in sp.get('items') or [] if s.get('title')])
    evs = [{'k': v.get('when'), 'title': v.get('what'), 'text': ' · '.join(x for x in (v.get('where'), v.get('price')) if x), 'cta': v.get('cta')}
           for v in place.get('events') or [] if v.get('what')]
    tiles({}, evs)

    # ── 8 the colour band: said words (else the figures); the photograph runs under the whole band, the colour over it
    if quotes or figures:
        bp = ''
        if band_ph:
            bp = '<div class="bg" data-slot="band" style="background-image:url(\'%s\');max-width:%dpx"></div>' % (e(_m(band_ph['src'])), band_ph['w'])
        if quotes:
            body = '<span class="qm" aria-hidden="true">”</span>' + ''.join(
                '<figure><blockquote>%s</blockquote><figcaption>— %s</figcaption></figure>'
                % (e(q['q']), e(', '.join(x for x in (q.get('name'), q.get('role')) if x))) for q in quotes)
        else:
            body = figs('fg-bd')
        out.append('<section class="qb fx%s">%s<div class="qb-i">%s</div></section>' % (' ph' if bp else '', bp, body))

    # ── 9 ruled rows of links (heading in the second colour, an arrow at the far end, a 2px rule under each)
    def rowlist(items, cls):
        r = []
        for it in items:
            t = '<h3>%s</h3>' % _a(it.get('h'), e(it['t']) + (' <i>→</i>' if it.get('h') else ''))
            im = ''
            if it.get('img'):
                im = '<img src="%s" alt="%s" loading="lazy"%s>' % (e(_m(it['img'])), e(it['t']), '')
            sub = '<p class="yr">%s</p>' % e(it['year']) if it.get('year') else ''
            r.append('<div class="rw">%s%s%s%s</div>' % (im, t, sub, '<p>%s</p>' % e(it['d']) if it.get('d') else ''))
        return '<div class="rl %s">%s</div>' % (cls, ''.join(r))

    links = [l for l in d.get('links') or [] if l.get('t')]
    if links:
        out.append('<section class="lk fx">%s</section>' % rowlist(links, ''))

    # ── 10 people: section head, the group photograph across, portraits four across on a track, the others in type
    if people:
        with_p = [p for p in people if p.get('img')]
        without = [p for p in people if not p.get('img')]

        def person(p, pic):
            im = ''
            if pic:
                ph = by_src.get(p['img']) or {}
                im = '<img src="%s" alt="%s" loading="lazy" width="%s" height="%s">' % (e(_m(p['img'])), e(p.get('name') or ''), ph.get('w') or 1, ph.get('h') or 1)
            ct = ''.join(x for x in ('<a href="tel:%s">%s</a>' % (e(re.sub(r'[^\d+]', '', p['phone'])), e(p['phone'])) if p.get('phone') else '',
                                     '<a href="mailto:%s">%s</a>' % (e(p['email']), e(p['email'])) if p.get('email') else ''))
            return ('<li class="pp">%s<h3>%s</h3>%s%s%s</li>'
                    % (im, _a(p.get('h'), e(p.get('name') or '')), '<p class="rl2">%s</p>' % e(p['role']) if p.get('role') else '',
                       '<p>%s</p>' % e(p['text']) if p.get('text') else '', '<p class="ct">%s</p>' % ct if ct else ''))
        s = _head(team.get('title'), team.get('text'))
        if group_ph:
            s += ('<img class="gp" data-slot="team" src="%s" alt="%s" width="%d" height="%d" style="max-width:min(100%%,%dpx)" loading="lazy">'
                  % (e(_m(group_ph['src'])), e(group_ph.get('alt') or ''), group_ph['w'], group_ph['h'], group_ph['w']))
        if with_p:
            ph0 = by_src.get(with_p[0]['img']) or {}
            ar = max(1.0, min(1.6, (ph0.get('h') or 1) / (ph0.get('w') or 1)))
            s += '<div class="cr" style="--ar:%.3f"><ul class="ck">%s</ul>' % (1 / ar, ''.join(person(p, True) for p in with_p))
            if len(with_p) > 4:
                s += ('<button class="ar pv" type="button" aria-label="%s"><i>←</i></button><button class="ar nx" type="button" aria-label="%s"><i>→</i></button>'
                      % (e(words[1]), e(words[2])))
            s += '</div>'
        if without:
            s += '<ul class="pg">%s</ul>' % ''.join(person(p, False) for p in without)
        out.append('<section class="tm fx">%s</section>' % s)

    # ── 11 rooms: a centred capital line and the row of six small pictures edge to edge (the reference's picture strip)
    spaces = [x for x in place.get('spaces') or [] if x.get('title')]
    if strip and len(strip) >= 3 or spaces:
        s = ''
        if spaces:
            s += '<h2 class="st">%s</h2>%s' % (e(spaces[0]['title']), '<p class="sx">%s</p>' % e(spaces[0]['text']) if spaces[0].get('text') else '')
        if len(strip) >= 3:
            s += '<div class="sr n%d" data-slot="strip">%s</div>' % (len(strip), ''.join(
                '<img src="%s" alt="%s" width="%d" height="%d" style="max-width:%dpx" loading="lazy">' % (e(_m(p['src'])), e(p.get('alt') or ''), p['w'], p['h'], p['w']) for p in strip))
        if spaces[1:]:
            s += rowlist([{'t': x['title'], 'd': x.get('text')} for x in spaces[1:]], 'pl' if len(spaces) > 2 else 'pl one')
        out.append('<section class="sp fx">%s</section>' % s)

    # ── 12 plans (the two-across outlined cards of the classes page) and questions (the ruled rows, opening)
    pl = d.get('plans') or {}
    pit = [x for x in pl.get('items') or [] if x.get('name')]
    if pit:
        cards = []
        for i, x in enumerate(pit):
            c = cyc[i % len(cyc)]
            b = x.get('cta') or {}
            cards.append('<div class="cd pn%s%s" style="--c:%s;--o:%s"><h3>%s</h3>%s%s%s%s</div>'
                         % (' mk' if x.get('marked') else '', ' last' if len(pit) % 2 and i == len(pit) - 1 else '', c, _on(c, ground, ink), e(x['name']),
                            '<p class="pc">%s%s</p>' % (e(x['price']), ' <small>%s</small>' % e(x['per']) if x.get('per') else '') if x.get('price') else '',
                            '<p>%s</p>' % e(x['line']) if x.get('line') else '',
                            '<ul>%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in x['rows']) if x.get('rows') else '',
                            '<a class="cbn" href="%s">%s <i>→</i></a>' % (e(b.get('h') or '#'), e(b['t'])) if b.get('t') else ''))
        out.append('<section class="cs fx" id="plans">%s<div class="cg c2">%s</div>%s</section>'
                   % (_head(pl.get('title'), pl.get('text')), ''.join(cards), '<p class="tn">%s</p>' % e(pl['note']) if pl.get('note') else ''))
    fq = d.get('faq') or {}
    qs = [x for x in fq.get('items') or [] if x.get('q')]
    if qs:
        out.append('<section class="lk fq fx" id="faq">%s<div class="rl one">%s</div></section>'
                   % (_head(fq.get('title')), ''.join('<details class="rw"><summary><h3>%s</h3><i>+</i></summary><p>%s</p></details>' % (e(x['q']), e(x.get('a') or '')) for x in qs)))

    # ── 13 credentials: the same ruled rows
    creds = [c for c in d.get('credentials') or [] if c.get('t')]
    if creds:
        out.append('<section class="lk cr2 fx">%s</section>' % rowlist([{'t': c['t'], 'd': c.get('text'), 'h': c.get('h'), 'year': c.get('year'), 'img': c.get('img')} for c in creds], 'p'))

    # ── 14 the closing band: capitals, one line, the call on its pale disc; the photograph under the band, shown at the right
    cl = d.get('close') or {}
    if cl.get('title'):
        cp = ''
        if close_ph:
            cp = '<div class="bg" data-slot="close" style="background-image:url(\'%s\');max-width:%dpx"></div>' % (e(_m(close_ph['src'])), close_ph['w'])
        b = cl.get('cta') or {}
        tx = cl.get('text') or ''
        out.append('<section class="cl fx%s">%s<div class="cl-i"><h2>%s</h2>%s%s</div></section>'
                   % (' ph' if cp else '', cp, e(cl['title']), '<p class="%s">%s</p>' % ('up' if len(tx) <= 90 else '', e(tx)) if tx else '',
                      '<a class="sb2" href="%s"><span>%s</span> <i>→</i></a>' % (e(b.get('h') or '#'), e(b['t'])) if b.get('t') else ''))

    # ── 15 foot: ruled above; a wide first column and narrow ones; the dark bar under it
    foot = d.get('foot') or {}
    cols = []
    trust = [t for t in d.get('trust') or [] if t]
    if brand.get('name') or trust:
        cols.append('<div class="fc w"><h4>%s</h4>%s</div>' % (e(brand.get('name') or ''), ''.join('<p>%s</p>' % e(t) for t in trust)))

    def addr(a):
        if not a:
            return ''
        l2 = ' '.join(x for x in (a.get('postcode'), a.get('city')) if x)
        return '<br>'.join(e(x) for x in (a.get('street'), l2, ', '.join(x for x in (a.get('region'), a.get('country')) if x)) if x)

    def hours(hs):
        return ''.join('<p>%s<br>%s</p>' % (e(h.get('days') or ''), e(' – '.join(x for x in (h.get('open'), h.get('close')) if x))) for h in hs or [] if h.get('days') or h.get('open'))
    locs = [l for l in d.get('locations') or [] if l.get('name')]
    if locs:
        for l in locs:
            ph = l.get('phone')
            cols.append('<div class="fc"><h4>%s</h4><p>%s%s%s</p>%s%s</div>'
                        % (_a(l.get('h'), e(l['name'])), addr(l.get('address')),
                           '<br><a href="tel:%s">%s</a>' % (e(re.sub(r'[^\d+]', '', ph)), e(ph)) if ph else '',
                           '<br><a href="mailto:%s">%s</a>' % (e(l['email']), e(l['email'])) if l.get('email') else '',
                           hours(l.get('hours')), '<p>%s</p>' % e(l['note']) if l.get('note') else ''))
    elif place.get('address') or phone.get('t') or email:
        a = place.get('address') or {}
        cols.append('<div class="fc"><h4>%s</h4><p>%s%s%s</p>%s</div>'
                    % (e(a.get('city') or brand.get('name') or ''), addr(a),
                       '<br>%s' % _a(phone.get('h'), e(phone['t'])) if phone.get('t') else '',
                       '<br><a href="mailto:%s">%s</a>' % (e(email), e(email)) if email else '', hours(place.get('hours'))))
    form = contact.get('form') or {}
    routes = [r for r in contact.get('routes') or [] if r.get('t')]
    if form.get('t') or routes:
        cols.append('<div class="fc"><h4>%s</h4>%s%s</div>'
                    % (_a(form.get('h'), e(form.get('t') or '')) if form.get('t') else e(phone.get('t') or ''),
                       ''.join('<p>%s%s</p>' % (_a(r.get('h'), e(r['t'])), '<br>%s' % e(r['note']) if r.get('note') else '') for r in routes),
                       '<p class="so">%s</p>' % ''.join('<a href="%s" rel="noopener">%s</a>' % (e(s['h']), e(s['t'])) for s in social) if social else ''))
    elif social:
        cols.append('<div class="fc"><p class="so">%s</p></div>' % ''.join('<a href="%s" rel="noopener">%s</a>' % (e(s['h']), e(s['t'])) for s in social))
    fl = [l for l in foot.get('links') or [] if l.get('t')]
    notices = ''.join('<p>%s</p>' % e(' '.join(n.get('text') or [])) for n in place.get('notices') or [] if n.get('text'))
    bar = foot.get('legal') or (foot.get('text') if not (place.get('address') or locs) else '') or ''
    out.append('<footer class="ft">%s</footer><div class="bb"><p>%s</p>%s%s</div>'
               % ('<div class="fg2">%s</div>' % ''.join(cols) if cols else '', e(bar),
                  '<p class="bl">%s</p>' % ''.join('<a href="%s">%s</a>' % (e(l.get('h') or '#'), e(l['t'])) for l in fl) if fl else '', notices))

    v = {'g': ground, 'i': ink, 'p': P, 's': S, 'sf': SF, 'op': onP, 'os': onS, 'oi': onI, 'tp': tintP, 'dp': discP, 'ts': tintS, 'bh': btnh, 'bho': btnh_on,
         'ln': _mix(ink, ground, .38), 'zb': _mix(ink, ground, .05), 'ph': _mix(onP, P, .28), 'sh': _mix(onS, S, .4),
         'dk': _mix('#000000', P, .45)}
    css = CSS.replace('/*VARS*/', ';'.join('--%s:%s' % kv for kv in v.items()))
    for k, (a, b) in SIZES.items():
        css = css.replace('{%s}' % k, _fl(a, b))
    desc = hero.get('text') or st.get('text') or ''
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="%s"><style>%s</style><script>document.documentElement.className="js"</script></head>'
            '<body>%s<script>%s</script></body></html>'
            % (e(lang), e(' — '.join(x for x in (brand.get('name'), title) if x)), e(desc[:160]), FONTS, css, ''.join(out), JS))


def _dig(o, keys):
    for k in keys:
        if not isinstance(o, dict):
            return None
        o = o.get(k)
    return o


# measured pairs: (390 wide, 1440 wide), px
SIZES = {
    'h1': (49.6, 67.2), 'h1b': (59.2, 96), 'h1l': (59.5, 94), 'inh': (35.2, 60.8), 'inl': (42.24, 72.96), 'inp': (19.2, 24), 'inpl': (24.96, 31.2),
    'sh': (33.6, 44.8), 'shl': (36.96, 49.28), 'cdh': (20.8, 24), 'cdl': (27.04, 31.2), 'tlh': (20.8, 28.8), 'tll': (23, 31.68),
    'tlk': (12.8, 14.4), 'tlp': (10, 50), 'tlH': (439, 468), 'q': (19.2, 24), 'ql': (24.96, 31.2), 'qc': (12.8, 14.4), 'qm': (192, 240),
    'rwh': (20.8, 24), 'rwp': (37, 50), 'clh': (51.2, 67.2), 'cll': (51.2, 94), 'ntf': (17, 25), 'ntH': (188, 138), 'gapS': (47, 100.8),
    'hrp': (19.5, 72), 'pad': (15.6, 57.6), 'pad3': (15.6, 43.2), 'ftp': (58.5, 72),
}

CSS = r"""
:root{/*VARS*/;--f:'Barlow','DIN Alternate','Helvetica Neue',Arial,sans-serif;--fc:'Barlow Condensed','Barlow','Arial Narrow',sans-serif;--pad:{pad}}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--i);font:400 17.6px/22.88px var(--f);letter-spacing:-.2px;overflow-x:hidden}
img{display:block;max-width:100%;height:auto}
a{color:inherit;text-decoration:none;transition:color .3s,background-color .3s,border-color .3s}
h1,h2,h3,h4,p,ul,dl,dd,figure,blockquote{margin:0;padding:0}
ul{list-style:none}
i{font-style:normal}
:focus-visible{outline:2px solid var(--i);outline-offset:2px;box-shadow:0 0 0 4px var(--g)}
.bg{position:absolute;inset:0;background-size:cover;background-position:50% 35%}
/* notice */
.nt{background:var(--i);color:var(--oi);min-height:{ntH};display:flex;align-items:center;justify-content:center;padding:10px 20px 15px;overflow:hidden;margin-bottom:20px}
.nt-i{text-align:center;font:700 {ntf}/1.3 var(--f);animation:ntin 1.25s both}
.nt p+p{margin-top:11px}
.nt a{text-decoration:underline;text-underline-offset:4px}
@keyframes ntin{from{opacity:0;transform:translate3d(100%,0,0)}to{opacity:1;transform:none}}
/* small row */
.ut{display:flex;justify-content:flex-end;flex-wrap:wrap;padding:0 40px 0 20px;min-height:44px}
.ut a,.ut span{font:700 12.8px/17.92px var(--f);letter-spacing:.2px;padding:13px 20px}
.ut a:hover{color:var(--s)}
/* header */
.hd{display:flex;align-items:center;gap:32px;min-height:117px;padding:15px 55px 15px 50px;border-top:1px solid var(--i);border-bottom:1px solid var(--i);position:relative}
.lg{flex:none;display:flex;align-items:center}
.lg img{height:85px;width:auto;max-width:220px;object-fit:contain}
.lg b{font:700 22px/1.05 var(--f);letter-spacing:.3px;text-transform:uppercase;max-width:11em;display:block}
.nv{flex:1;display:flex;justify-content:space-evenly;gap:10px 28px;flex-wrap:wrap}
.nv a{font:700 16px/40px var(--f);letter-spacing:.08px;text-transform:uppercase}
.nv a:hover{color:var(--s)}
.bt{flex:none;background:var(--i);color:var(--oi);border:2px solid var(--i);padding:12px 24px;font:700 14.4px/20.16px var(--f);letter-spacing:.8px;text-transform:uppercase;text-align:center}
.bt:hover{background:var(--bh);border-color:var(--bh);color:var(--bho)}
.mn{display:none;margin-left:auto}
.mn summary{list-style:none;cursor:pointer;width:48px;height:48px;display:flex;align-items:center;justify-content:center}
.mn summary::-webkit-details-marker{display:none}
.mn summary i,.mn summary i::before,.mn summary i::after{display:block;width:32px;height:3px;border-radius:4px;background:var(--i);position:relative}
.mn summary i::before,.mn summary i::after{content:"";position:absolute;left:0;top:-9px}
.mn summary i::after{top:9px}
.mp{position:absolute;left:0;right:0;top:100%;z-index:20;background:var(--g);border-bottom:1px solid var(--i);border-top:1px solid var(--i);padding:14px 20px 26px;display:flex;flex-direction:column}
.mp>a:not(.bt){font:700 16px/48px var(--f);text-transform:uppercase;border-bottom:1px solid var(--ln)}
.mp .bt{margin-top:22px}
.mp p{margin-top:18px;font:700 12.8px/2 var(--f);display:flex;flex-wrap:wrap;gap:0 20px}
/* opening */
.hr{position:relative;min-height:75vh;display:flex;align-items:center;padding:60px {hrp};background:#000;color:#fff;overflow:hidden}
.hr.plain{background:var(--i);color:var(--oi)}
.hr .bg{margin:0 auto}
.hr:not(.plain)::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.66) 0,rgba(0,0,0,.62) 62%,rgba(0,0,0,.21) 92%)}
.hr-i{position:relative;z-index:1;width:100%}
.kk{font:700 19.2px/24.96px var(--fc);letter-spacing:.8px;text-transform:uppercase;margin-bottom:20px}
h1{font:700 {h1}/1.2 var(--f);letter-spacing:-.2px;max-width:13em;text-wrap:balance}
h1.big{font-size:{h1b};line-height:{h1l};text-transform:uppercase}
.ld{font:400 {inp}/{inpl} var(--f);max-width:34em;margin-top:26px}
.pr{display:flex;justify-content:center;flex-wrap:wrap;gap:14px;padding:30px 20px 10px}
.ob,.cbn{display:inline-block;border:2px solid var(--i);padding:12px 24px;font:700 14.4px/18.72px var(--fc);letter-spacing:.6px;text-transform:uppercase;text-align:center}
.ob:hover{background:var(--i);color:var(--oi)}
/* statement */
.in{padding:50px 30px 0;text-align:center}
.in h2{font:700 {inh}/{inl} var(--f);max-width:1030px;margin:0 auto;text-wrap:balance}
.in h2+p{margin-top:39px}
.in>p{font:400 {inp}/{inpl} var(--f);max-width:1030px;margin-left:auto;margin-right:auto}
.fg{display:grid;gap:34px 40px}
.fg dt{font:700 {sh}/{shl} var(--f)}
.fg dd{margin-top:8px}
.fg-in{grid-template-columns:repeat(auto-fit,minmax(170px,1fr));max-width:1230px;margin:56px auto 0;text-align:center}
.fg-in dt{color:var(--p)}
/* section head */
.sh{margin-bottom:36px;padding-bottom:30px;border-bottom:1px solid var(--i)}
.sh h2{font:700 {sh}/{shl} var(--f)}
.sh .pre{color:var(--p)}
.sh p{margin-top:18px}
.sh .tl{color:var(--p)}
.sh .tl:hover{color:var(--s)}
/* outlined cards */
.cs{padding:0 {pad3};margin-top:{gapS}}
.in+.cs{margin-top:28.8px}
.cs>.sh{margin-left:calc(var(--pad) - {pad3});margin-right:calc(var(--pad) - {pad3})}
.cg{display:grid;gap:10px}
.cg.c4{grid-template-columns:repeat(4,1fr)}
.cg.c2{grid-template-columns:repeat(2,1fr);gap:20px;margin:0 calc(var(--pad) - {pad3})}
.cd{position:relative;border:2px solid var(--c);min-height:270px;padding:35px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;transition:background-color .6s ease-in-out,color .6s ease-in-out}
.c2 .cd{min-height:300px;padding:44px 40px}
.c2 .cd.last{grid-column:1/-1}
.cd h3{font:700 {cdh}/{cdl} var(--f);letter-spacing:.3px;text-transform:uppercase}
.cd p{margin-top:20px;max-width:46em}
.cd.nb:hover{background:var(--c);color:var(--o)}
.bk{position:absolute;inset:-2px;background:var(--c);color:var(--o);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:30px;padding:35px;opacity:0;transition:opacity .6s ease-in-out}
.bk b{font:700 {cdh}/{cdl} var(--f);letter-spacing:.3px;text-transform:uppercase}
.bk span{border:1px solid currentColor;padding:12px 24px;font:700 12.8px/17.92px var(--fc);letter-spacing:.8px;text-transform:uppercase}
.cd:hover .bk,.bk:focus-visible{opacity:1}
.pn .pc{font:700 {sh}/{shl} var(--f);color:var(--c)}
.pn .pc small{font:400 17.6px/1 var(--f);color:var(--i)}
.pn ul{margin-top:20px}
.pn li{padding:6px 0}
.pn.mk{background:var(--c);color:var(--o)}
.pn.mk .pc,.pn.mk .pc small{color:inherit}
.cbn{margin-top:34px;border-color:var(--c);color:var(--c)}
.cbn:hover{background:var(--c);color:var(--o)}
.pn.mk .cbn{border-color:currentColor;color:inherit}
.tn{max-width:1230px;margin:15px auto 0;font-style:italic}
/* price list */
.cb{margin-top:{gapS};background:var(--sf);color:var(--os);text-align:center;padding:clamp(60px,8vw,115px) var(--pad) clamp(60px,8vw,118px)}
.cb h2{font:700 {sh}/{shl} var(--f)}
.cb p{margin-top:18px}
.ix{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;max-width:1230px;margin:44px auto 0}
.wb{border:2px solid currentColor;padding:15px 18px;font:700 14.4px/20px var(--fc);letter-spacing:.8px;text-transform:uppercase;display:flex;align-items:center;justify-content:center;gap:12px}
.wb:hover{background:var(--os);color:var(--sf);border-color:var(--os)}
.tb{padding:0 var(--pad);margin-top:60px}
table{width:100%;max-width:1230px;margin:0 auto;border-collapse:collapse;font:400 15.84px/23.76px var(--f);table-layout:fixed}
td,th{border:1px solid var(--ln);padding:15px;text-align:left;vertical-align:top;overflow-wrap:break-word}
.gt th{font-weight:700;text-transform:uppercase;scroll-margin-top:20px}
.gt a:hover,.n1 a:hover{color:var(--s)}
.n1 a{text-decoration:underline;text-decoration-color:var(--ln);text-underline-offset:3px}
tr.z td{background:var(--zb)}
.k2{width:29.4%}
.k3{width:19%}
.pz{font-weight:700}
.n1 em{font-weight:700}
.n1 ul{margin-top:6px;font-style:italic}
tr.sb td{border-top:0;padding-top:0;font-style:italic}
tr:has(+tr.sb) td{border-bottom:0}
/* tiles */
.ev{padding:0 var(--pad);margin-top:{gapS}}
.tr{display:grid;gap:20px;margin-top:20px}
.sh+.tr{margin-top:0}
.tr.n2{grid-template-columns:60.25fr 39.75fr}
.tr.n2.alt{grid-template-columns:39.75fr 60.25fr}
.tr.n3{grid-template-columns:repeat(3,1fr)}
.tl{position:relative;min-height:{tlH};display:flex;align-items:center;padding:40px {tlp};background-size:cover;background-position:50% 50%;overflow:hidden}
.ov{position:absolute;inset:0;background:var(--c);transition:background-color .3s,opacity .3s}
a.tl:hover .ov{filter:brightness(.72)}
.tl.ph:hover .ov{background:#000;opacity:.62}
.tx{position:relative;display:block;max-width:680px}
.tx .k{font:700 {tlk}/1.4 var(--f);letter-spacing:.8px;text-transform:uppercase;margin-bottom:22px}
.tx h3{font:700 {tlh}/{tll} var(--f)}
.tx h3+p{margin-top:20px}
.tx .go{margin-top:22px;font:700 14.4px/18.72px var(--fc);letter-spacing:.8px;text-transform:uppercase}
.tl.ph:hover .tx{color:#fff!important}
/* colour band */
.qb{position:relative;margin-top:{gapS};min-height:547px;background:var(--sf);color:var(--os);display:flex;align-items:center;overflow:hidden}
.qb.ph .bg{right:auto;width:47%;background-position:50% 30%}
.qb.ph::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent 0,transparent 33%,var(--sf) 44%)}
.qb-i{position:relative;z-index:1;margin-left:47%;width:53%;padding:70px 140px 70px 0}
.qb:not(.ph) .qb-i{margin:0 auto;width:min(100%,1040px);padding:70px var(--pad)}
.qm{position:absolute;right:41px;top:-34px;font:700 {qm}/1 var(--f);color:var(--ts);pointer-events:none}
.qb figure+figure{margin-top:46px}
blockquote{font:italic 400 {q}/{ql} var(--f)}
blockquote::before{content:"“"}
blockquote::after{content:"”"}
figcaption{margin-top:35px;text-align:right;font:700 {qc}/1.4 var(--f);letter-spacing:.8px;text-transform:uppercase}
.fg-bd{grid-template-columns:repeat(2,1fr)}
/* rows */
.lk{padding:0 var(--pad);margin-top:{gapS}}
.rl{display:grid;grid-template-columns:repeat(2,1fr);gap:0 clamp(40px,8vw,115px)}
.rl.one{grid-template-columns:1fr;max-width:1230px}
.rw{padding:{rwp} 0;border-bottom:2px solid var(--s)}
.rl.p .rw{border-color:var(--p)}
.rw h3{font:700 {rwh}/1.1 var(--f);text-transform:uppercase;color:var(--s)}
.rl.p .rw h3{color:var(--p)}
.rw h3 a,.rw summary{display:flex;justify-content:space-between;align-items:flex-start;gap:24px}
.rw h3 a:hover{color:var(--sh)}
.rl.p .rw h3 a:hover{color:var(--ph)}
.rw h3 i,.rw summary i{flex:none;font-weight:700}
.rw p{margin-top:23px;max-width:529px}
.rw .yr{margin-top:10px;font:700 14.4px/1.4 var(--f);letter-spacing:.8px}
.rw .yr+p{margin-top:12px}
.rw img{width:min(100%,302px);margin-bottom:26px}
.rw summary{list-style:none;cursor:pointer;font:700 {rwh}/1.1 var(--f);color:var(--s)}
.rw summary::-webkit-details-marker{display:none}
.rw summary h3{font:inherit}
.rw[open] summary i{transform:rotate(45deg)}
.fq .rw p,.pl.one .rw p{max-width:60em}
.rl.pl .rw{border-color:var(--i)}
.rl.pl .rw h3{color:var(--i)}
/* people */
.tm{padding:0 var(--pad);margin-top:calc({gapS} * 1.286)}
.gp{width:100%;margin:0 auto 46px}
.cr{position:relative;padding-top:10px;padding-bottom:80px}
.ck{display:grid;grid-auto-flow:column;grid-auto-columns:calc((100% - 73.5px)/4);gap:24.5px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}
.ck::-webkit-scrollbar{display:none}
.pp{scroll-snap-align:start;min-width:0}
.pp img{width:100%;aspect-ratio:var(--ar);object-fit:cover;margin-bottom:19px;transition:opacity .5s}
.pp h3{border-top:1px solid var(--i);padding-top:17px;font:400 25.6px/33.28px var(--f)}
.pp h3 a:hover{color:var(--p)}
.pp .rl2{margin-top:8px;font:700 14.4px/1.4 var(--f);letter-spacing:.8px;text-transform:uppercase}
.pp p{margin-top:10px}
.pp .ct{font-size:14.4px;line-height:20.16px;display:flex;flex-direction:column;overflow-wrap:anywhere}
.pp .ct a:hover{color:var(--p)}
.ar{position:absolute;bottom:10px;width:48px;height:48px;border-radius:100px;border:0;background:var(--p);color:var(--tp);font:700 24px/48px var(--f);cursor:pointer;transition:all .5s;padding:0}
.ar:hover{background:var(--tp);color:var(--p)}
.pv{left:1px}.nx{right:1px}
.pg{display:grid;grid-template-columns:repeat(4,1fr);gap:46px 24.5px}
.cr+.pg{margin-top:30px}
/* rooms */
.sp{margin-top:calc({gapS} * .857)}
.st{font:700 22.4px/29.12px var(--f);text-transform:uppercase;text-align:center;padding:0 30px}
.sx{text-align:center;max-width:44em;margin:14px auto 0;padding:0 30px}
.sr{display:flex;justify-content:center;gap:4px;margin-top:31px}
.sr img{flex:1 1 0;min-width:0;aspect-ratio:4/3;object-fit:cover}
.sp .rl{padding:0 var(--pad);margin-top:10px}
/* closing band */
.cl{position:relative;margin-top:{gapS};min-height:600px;background:var(--p);color:var(--op);display:flex;align-items:center;overflow:hidden}
.cl .bg{left:auto;width:42%;background-position:50% 30%}
.cl.ph::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,var(--p) 0,var(--p) 61%,transparent 72%)}
.cl-i{position:relative;z-index:1;width:min(100%,902px);padding:60px 90px 60px {hrp}}
.cl h2{font:700 {clh}/1.12 var(--f);text-transform:uppercase}
.cl p{margin-top:20px;max-width:740px}
.cl p.up{text-transform:uppercase}
.sb2{position:relative;display:inline-flex;align-items:center;gap:12px;margin-top:20px;padding:61px 40px 58px;font:700 19.2px/26.88px var(--fc);letter-spacing:.8px;text-transform:uppercase}
.sb2::before{content:"";position:absolute;left:0;top:50%;width:76.8px;height:76.8px;border-radius:50%;background:var(--dp);opacity:.6;transform:translateY(-50%);transition:transform .5s,opacity .5s}
.sb2:hover::before{transform:translateY(-50%) scale(1.2);opacity:.75}
.sb2 span,.sb2 i{position:relative}
/* foot */
.ft{border-top:1px solid var(--i);padding:{ftp} {pad3} 43.2px;margin-top:{gapS}}
.cl+.ft,.sp+.ft{margin-top:0}
.sp+.ft{margin-top:10px}
.fg2{display:flex;flex-wrap:wrap;gap:40px 0;justify-content:space-between}
.fc{flex:0 0 17.5%;padding-right:30px;font-size:14.4px;line-height:20.16px}
.fc.w{flex-basis:30%;padding-right:81px}
.fc h4{font:700 20.8px/27.04px var(--f);text-transform:uppercase;margin-bottom:20px}
.fc p+p{margin-top:10px}
.fc a:hover{color:var(--s)}
.so{display:flex;flex-wrap:wrap;gap:6px 18px;font-weight:700}
.bb{background:var(--i);color:var(--oi);padding:22px {pad3};font-size:12.8px;line-height:17.92px;display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px 40px}
.bb p{max-width:70em}
.bl{display:flex;flex-wrap:wrap;gap:6px 22px}
.bb a:hover{text-decoration:underline}
/* arriving: each section fades in over 1.25s when it comes into view (only when scripts run) */
.js .fx{opacity:0}
.js .fx.on{opacity:1;animation:fin 1.25s both}
@keyframes fin{from{opacity:0}to{opacity:1}}
@media (max-width:1100px){
.nv,.hd>.bt{display:none}.mn{display:block}
.cg.c4{grid-template-columns:repeat(2,1fr)}
.ix{grid-template-columns:repeat(2,1fr)}
.ck{grid-auto-columns:calc((100% - 49px)/3)}
.pg{grid-template-columns:repeat(3,1fr)}
.qb-i{padding-right:var(--pad)}
.fc{flex-basis:33.33%}.fc.w{flex-basis:100%;padding-right:0}
}
@media (max-width:767px){
.ut{display:none}
.hr:not(.plain)::after{background:rgba(0,0,0,.66)}
.hd{padding:15px 20px}
.cg.c4,.cg.c2{grid-template-columns:1fr;gap:21px}
.cd,.c2 .cd{min-height:338px;padding:30px 22px}
.ix{grid-template-columns:1fr;gap:14px}
table{font-size:15px}
td,th{padding:12px 10px}
.k2{width:30%}.k3{width:27%}
.tr.n2,.tr.n2.alt,.tr.n3{grid-template-columns:1fr}
.qb{display:block;min-height:0}
.qb.ph{padding-top:300px}
.qb.ph .bg{bottom:auto;height:330px;width:100%}
.qb.ph::after{background:linear-gradient(180deg,transparent 0,transparent 200px,var(--sf) 318px)}
.qb-i,.qb:not(.ph) .qb-i{margin:0;width:100%;padding:50px 20px 40px}
.qm{right:-9px;top:-34px}
.qb.ph .qm{top:266px}
.fg-bd{grid-template-columns:1fr 1fr;gap:28px 20px}
.rl{grid-template-columns:1fr}
.ck{grid-auto-columns:100%}
.cr{padding-bottom:90px}
.ar{width:50px;height:50px}
.pg{grid-template-columns:1fr;gap:34px}
.sr{flex-wrap:wrap}
.sr img{flex:0 0 calc((100% - 8px)/3)}
.cl{display:block;min-height:0}
.cl.ph{padding-top:245px}
.cl.ph .bg{bottom:auto;height:275px;width:100%}
.cl.ph::after{background:linear-gradient(180deg,transparent 0,transparent 170px,var(--p) 262px)}
.cl-i{padding:48px 39px 40px 31px}
.fc,.fc.w{flex-basis:50%;padding-right:20px}.fc.w{flex-basis:100%}
.bb{justify-content:center;text-align:center}
}
@media (prefers-reduced-motion:reduce){
*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}
.js .fx{opacity:1}
}
"""

JS = r"""(function(){var R=matchMedia('(prefers-reduced-motion:reduce)').matches,fx=[].slice.call(document.querySelectorAll('.fx'));
if(R||!('IntersectionObserver' in window)){fx.forEach(function(x){x.classList.add('on')})}else{var io=new IntersectionObserver(function(es){es.forEach(function(n){if(n.isIntersecting){n.target.classList.add('on');io.unobserve(n.target)}})},{rootMargin:'0px 0px -8% 0px'});fx.forEach(function(x){io.observe(x)})}
[].forEach.call(document.querySelectorAll('.cr'),function(c){var k=c.querySelector('.ck'),pv=c.querySelector('.pv'),nx=c.querySelector('.nx');if(!k||!nx)return;
function step(){var a=k.children[0],b=k.children[1];return b?b.offsetLeft-a.offsetLeft:k.clientWidth}
function go(d){var max=k.scrollWidth-k.clientWidth,x=k.scrollLeft+d*step();if(x>max+4)x=0;if(x<-4)x=max;k.scrollTo({left:x,behavior:R?'auto':'smooth'})}
nx.addEventListener('click',function(){go(1)});pv.addEventListener('click',function(){go(-1)});
if(!R){var hold=false;['mouseenter','focusin','touchstart'].forEach(function(v){c.addEventListener(v,function(){hold=true},{passive:true})});['mouseleave','focusout'].forEach(function(v){c.addEventListener(v,function(){hold=false})});setInterval(function(){if(!hold&&!document.hidden)go(1)},8000)}});
[].forEach.call(document.querySelectorAll('.mp a'),function(a){a.addEventListener('click',function(){var d=a.closest('details');if(d)d.open=false})});
})();"""
