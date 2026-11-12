"""odyssee — template rebuilt from odysseeclinic.com.au (measured 2026-11-12 at 1440 and 390; see NOTES.md).
render(d) -> one self-contained page. Pure: no file reads, no model call. The picture family is the client's own
photographs (media.made is never read). Fonts: Instrument Serif for PS Times, Hanken Grotesk for Basel Grotesk."""
from html import escape as _e

M = '../../'
BACK = ('room', 'exterior', 'bar', 'people', 'work', 'workshop', 'landscape', 'action', 'other', None, '')
ENL = 1.3  # a photograph is never enlarged more than this at 1440; one too small to afford the 8.5 % the scroll movement needs stands still


def e(s):
    return _e(str(s or ''), quote=True)


def _rgb(c):
    c = (c or '#000').lstrip('#')
    if len(c) == 3:
        c = ''.join(ch * 2 for ch in c)
    try:
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 0, 0)


def _hex(t):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in t)


def _lum(t):
    f = lambda v: (v / 255) / 12.92 if v / 255 <= .03928 else ((v / 255 + .055) / 1.055) ** 2.4
    r, g, b = (f(v) for v in t)
    return .2126 * r + .7152 * g + .0722 * b


def _con(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _muted(ink, ground):
    """the reference sets secondary words at 30 % opacity (2:1); ours is the lightest mix that still holds 4.6:1"""
    best = ink
    for i in range(1, 60):
        c = _mix(ink, ground, i / 100)
        if _con(c, ground) < 4.6:
            break
        best = c
    return best


def _tint(deep):
    """the colour the duotone tiles are multiplied with: the deep colour, lifted until white 12px words hold 4.5:1 on its lightest pixel"""
    c = deep
    for i in range(0, 100):
        c2 = _mix(deep, (255, 255, 255), i / 100)
        if _lum(c2) > .155:
            break
        c = c2
    return c


def words(s, tag, cls='', indent=False):
    """a heading set word by word, as the reference does (each word rises 10px and fades in, one after the other)"""
    ws = str(s or '').split()
    out = ''.join('<span class="w" style="--i:%d">%s</span> ' % (min(i, 30), e(w)) for i, w in enumerate(ws))
    return '<%s class="rv %s">%s%s</%s>' % (tag, cls, '<i class="ind"></i>' if indent else '', out.strip(), tag)


def link(o, cls='cap dot'):
    if not o or not o.get('t'):
        return ''
    return '<a class="%s" href="%s">%s</a>' % (cls, e(o.get('h') or '#'), e(o['t']))


def render(d: dict) -> str:
    g = lambda k, default=None: d.get(k) if d.get(k) is not None else (default if default is not None else {})
    brand, hero, pal = g('brand'), g('hero'), g('palette')
    place, contact = g('place'), g('contact')
    lang = d.get('lang') or 'en'
    ground, ink = _rgb(pal.get('ground') or '#ffffff'), _rgb(pal.get('ink') or '#111111')
    if _con(ground, ink) < 7:
        ink = (20, 20, 20) if _lum(ground) > .4 else (245, 245, 245)
    accent = _rgb(pal.get('accent') or _hex(ink))
    deep = ink if _lum(ink) < _lum(ground) else ground
    tint, muted = _tint(deep), _muted(ink, ground)
    on_deep = (255, 255, 255)
    name = brand.get('name') or ''

    # ---------- photographs: each once, by role, size and proportion ----------
    media = g('media')
    photos = [p for p in (media.get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
    by_src = {p['src']: p for p in photos}
    steps, team, cat = g('steps'), g('team'), g('catalogue')
    people = list(team.get('items') or [])
    tgroups = [x for x in (team.get('groups') or []) if x.get('items')]
    if not people and tgroups:
        people = [p for x in tgroups for p in x['items']]
    taken = set()
    for it in (steps.get('items') or []):
        taken.add(it.get('img'))
    for p in people:
        taken.add(p.get('img'))
    for gr in (cat.get('groups') or []):
        taken.add(gr.get('img'))
        for it in (gr.get('items') or []):
            taken.add(it.get('img'))
    for sp in (place.get('spaces') or []):
        taken.add(sp.get('img'))
    for c in (g('credentials', []) or []):
        taken.add(c.get('img'))
    free = [p for p in photos if p['src'] not in taken and p.get('role') != 'portrait']
    big = [p for p in free if not p.get('small') and p['w'] >= 1200 and p['h'] >= 560]
    small = [p for p in free if p not in big]
    back = [p for p in big if p.get('role') in BACK]
    detail = [p for p in big if p.get('role') not in BACK]
    slot = {}
    ranked = sorted(back or big, key=lambda p: -p['w'] * p['h'])
    if ranked:
        slot['heroA'] = ranked[0]
    if len(big) >= 7 and len(ranked) > 1:
        slot['heroB'] = ranked[1]
    pool = [p for p in back + detail if p not in slot.values()]
    if len(pool) >= 5 and detail and detail[0] in pool:  # the closing band takes a detail, as the reference's does
        slot['foot'] = detail[0]
        pool.remove(detail[0])
    if pool:
        slot['band'] = pool.pop(0)
    if len(pool) >= 2:
        slot['tile1'], slot['tile2'] = pool.pop(0), pool.pop(0)
    if pool:
        slot['method'] = pool.pop(0)
    if pool and 'foot' not in slot:
        slot['foot'] = pool.pop(0)
    if len(pool) >= 2:
        slot['ap1'], slot['ap2'] = pool.pop(0), pool.pop(0)
    s_cat = pool.pop(0) if pool else None
    small = small + [p for p in pool if p['w'] / p['h'] <= 1.8]
    p0 = None  # a portrait stands with its person in the team part only (each photograph once)
    s_stat = small.pop(0) if small and not p0 and hero.get('text') else None
    s_meth = small.pop(0) if small and slot.get('method') else None
    s_menu = small.pop(0) if small and small[0]['w'] / small[0]['h'] <= 1.8 else None

    def img(p, cls='', lazy=True, sizes=None):
        return '<img class="%s" src="%s%s" width="%d" height="%d" alt="%s"%s>' % (
            cls, M, e(p['src']), p['w'], p['h'], e(p.get('alt') or ''), ' loading="lazy" decoding="async"' if lazy else '')

    def moves(p, ref_h):
        return p['h'] * ENL >= min(ref_h, 900) * 1.085

    def cap(p, ref_h):
        """slot height in px: the reference's, unless that would enlarge the photograph more than ENL"""
        return int(min(ref_h, p['h'] * ENL / (1.085 if moves(p, ref_h) else 1)))

    def par(p, ref_h):
        return ' data-par' if moves(p, ref_h) else ''

    # ---------- navigation ----------
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    cta = d.get('cta') or hero.get('primary') or place.get('booking') or {}
    home = (brand.get('home') or '').rstrip('/')
    nav_in = [n for n in nav if (n.get('h') or '').rstrip('/') != home and n.get('h') != cta.get('h')]
    row_nav = [n for n in nav_in if len(n['t']) <= 14][:3]
    sec = hero.get('secondary') or {}
    head_link = sec if sec.get('t') and len(sec['t']) <= 24 else (row_nav[0] if row_nav else {})
    logo = brand.get('logo')
    brand_head = ('<img class="logo" src="%s%s" alt="%s">' % (M, e(logo), e(name))) if logo else '<span class="bn">%s</span>' % e(name)

    addr = place.get('address') or {}
    addr_lines = [x for x in [addr.get('street'), ' '.join(x for x in [addr.get('postcode'), addr.get('city')] if x), ', '.join(x for x in [addr.get('region'), addr.get('country')] if x)] if x]
    phone = place.get('phone') or contact.get('phone') or {}
    email = place.get('email') or contact.get('email')
    form = contact.get('form') or {}
    social = [s for s in (place.get('social') or []) + (contact.get('routes') or []) if s.get('t')]
    hours = [h for h in (place.get('hours') or []) if h.get('days')]

    def contact_rows():
        r = ''
        if addr_lines:
            r += '<tr><th scope="row">A.</th><td><address>%s</address></td></tr>' % '<br>'.join(e(x) for x in addr_lines)
        elif g('foot').get('text'):
            r += '<tr><th scope="row">A.</th><td>%s</td></tr>' % e(g('foot')['text'])
        c = []
        if email:
            c.append('<a class="ul" href="mailto:%s">%s</a>' % (e(email), e(email)))
        if phone.get('t'):
            c.append('<a class="ul" href="%s">%s</a>' % (e(phone.get('h') or 'tel:' + phone['t'].replace(' ', '')), e(phone['t'])))
        if form.get('t'):
            c.append('<a class="ul" href="%s">%s</a>' % (e(form.get('h') or '#'), e(form['t'])))
        if c:
            r += '<tr><th scope="row">C.</th><td>%s</td></tr>' % '<br>'.join(c)
        if social:
            r += '<tr><th scope="row">S.</th><td>%s</td></tr>' % ' / '.join('<a class="ul" href="%s">%s</a>' % (e(s.get('h') or '#'), e(s['t'])) for s in social)
        return r

    crow = contact_rows()

    # ---------- menu ----------
    menu_items = nav or [l for l in (d.get('links') or []) if l.get('t')]
    if cta.get('t') and not any(n.get('t') == cta['t'] for n in menu_items):
        menu_items = menu_items + [cta]
    menu = ''
    if menu_items:
        lis = ''.join('<li><a href="%s">%s</a></li>' % (e(n.get('h') or '#'), e(n['t'])) for n in menu_items[:9])
        mpic = ''
        if hero.get('kicker') and hero.get('kicker') != name:
            mp = s_menu
            mpic = '<div class="mnote">%s<p>%s</p></div>' % (('<div class="mp" data-slot="menu">%s</div>' % img(mp)) if mp and mp['w'] / mp['h'] <= 1.8 else '', e(hero['kicker']))
        menu = ('<div class="menu" id="menu" role="dialog" aria-label="Menu"><a class="cap mclose" href="#top" id="mclose">%s</a>'
                '<ol>%s</ol>%s%s</div><div class="mbk" id="mbk"></div>') % ({'de': 'Schließen', 'fr': 'Fermer', 'es': 'Cerrar', 'it': 'Chiudi', 'sr': 'Zatvori'}.get(lang, 'Close'), lis, mpic,
                                           '<table class="mct">%s</table>' % crow if crow else '')
    menu_word = {'de': 'Menü', 'es': 'Menú', 'sr': 'Meni'}.get(lang, 'Menu')
    mbtn = '<a class="navl mopen" href="#menu" role="button" aria-controls="menu">%s</a>' % menu_word if menu else ''

    header = '<header class="hd" id="top"><div class="g"><a class="brand" href="%s">%s</a><nav>%s%s%s</nav></div></header>' % (
        e(brand.get('home') or '#'), brand_head, mbtn,
        '<a class="navl dk" href="%s">%s</a>' % (e(head_link.get('h') or '#'), e(head_link['t'])) if head_link.get('t') else '',
        '<a class="navl%s" href="%s">%s</a>' % ('' if len(cta['t']) <= 10 else ' dk', e(cta.get('h') or '#'), e(cta['t'])) if cta.get('t') else '')

    # ---------- 1 first screen(s) ----------
    A, B = slot.get('heroA'), slot.get('heroB')
    hs = ''
    for i, p in enumerate([x for x in (A, B) if x]):
        hs += '<div class="hs" data-slot="hero-%d" style="height:min(100svh,%dpx)"><div class="par"%s>%s</div></div>' % (i + 1, cap(p, 4000), par(p, 900), img(p, lazy=i > 0))
    row = ('<div class="hrw"><div class="hrow g"><a class="hb" href="%s">%s</a>%s<nav>%s%s%s</nav></div></div>') % (
        e(brand.get('home') or '#'), e(name), '<h1>%s</h1>%s' % (e(hero.get('title') or name), '<a class="cap hc" href="%s">%s</a>' % (e(cta.get('h') or '#'), e(cta['t'])) if cta.get('t') else ''),
        ''.join('<a class="navl dk" href="%s">%s</a>' % (e(n.get('h') or '#'), e(n['t'])) for n in row_nav),
        '<a class="navl" href="%s">%s</a>' % (e(cta.get('h') or '#'), e(cta['t'])) if cta.get('t') else '',
        mbtn.replace('mopen', 'mopen pho') if mbtn else '')
    first = '<section class="hero%s">%s%s</section>' % ('' if hs else ' plain', hs, row)

    # ---------- 2 opening statement ----------
    S = ''
    lead = hero.get('text') or ''
    if lead:
        pic = ''
        if p0:
            ph = by_src[p0['img']]
            pic = '<figure class="spic rvb" data-slot="statement" style="max-width:%dpx">%s<figcaption>%s%s</figcaption></figure>' % (
                ph['w'], img(ph), e(p0.get('name')), '<span>%s</span>' % e(p0['role']) if p0.get('role') else '')
        elif s_stat:
            ph = s_stat
            pic = '<figure class="spic rvb" data-slot="statement" style="max-width:%dpx;--a:%.3f">%s</figure>' % (ph['w'], max(.66, min(1.78, ph['w'] / ph['h'])), img(ph))
        sub = ''
        if hero.get('text2'):
            sub += '<p>%s</p>' % e(hero['text2'])
        if hero.get('note'):
            sub += '<p>%s</p>' % ('<a class="ul" href="%s">%s</a>' % (e(phone['h']), e(hero['note'])) if phone.get('h') and phone.get('t') == hero['note'] else e(hero['note']))
        sub += link(hero.get('primary') or cta)
        S = '<section class="st g">%s<div class="stx">%s%s</div></section>' % (
            pic, words(lead, 'h2', 'big' if len(lead) <= 170 else 'mid', True), '<div class="sub rvb">%s</div>' % sub if sub else '')

    # ---------- 3 the pinned list ----------
    W = ''
    its = [x for x in (steps.get('items') or []) if x.get('title')][:6]
    if its:
        withpic = all(x.get('img') in by_src for x in its)
        arts = ''
        for i, x in enumerate(its):
            arts += '<article class="it%s">%s<div class="tx"><span>(%d).</span><div><h3>%s</h3>%s</div></div></article>' % (
                ' on' if i == 0 else '', '<div class="md" data-slot="step-%d">%s</div>' % (i + 1, img(by_src[x['img']])) if withpic else '', i + 1, e(x['title']),
                '<div class="more">%s%s</div>' % ('<p>%s</p>' % e(x['text']) if x.get('text') else '', link(x.get('cta'))) if x.get('text') or x.get('cta') else '')
        W = ('<section class="why" style="--n:%d;--k:%d"><div class="pin"><div class="wi"><div class="wh g"><span class="cap cnt"><b>1</b> : %d</span>%s'
             '<div class="prog"><i></i></div></div><div class="its">%s</div></div></div></section>') % (
            max(3, len(its)), len(its), len(its), '<h2 class="cap">%s</h2>' % e(steps['title']) if steps.get('title') else '', arts)

    # ---------- 4 two tiles, edge to edge ----------
    def tile(o, p, k, ref_h):
        return '<li class="tile%s" data-slot="%s"%s>%s<span class="sc"></span><span class="mu"></span><a href="%s"><span class="cap">%s</span></a></li>' % (
            '' if p else ' flat', k, ' style="--h:%dpx"' % cap(p, ref_h) if p else '', '<div class="par"%s>%s</div>' % (par(p, ref_h), img(p)) if p else '', e(o.get('h') or '#'), e(o['t']))

    tl = [{'t': x['t'], 'h': x.get('h')} for x in (cat.get('groups') or []) if x.get('t') and x.get('h')]
    links = [l for l in (d.get('links') or []) if l.get('t')] or nav_in
    if len(tl) < 2:
        tl = links[:2]
    T = ''
    if len(tl) >= 2:
        tl = tl[:2]
        T = '<section class="tiles"><ul>%s%s</ul></section>' % (tile(tl[0], slot.get('tile1'), 'tile-1', 4000), tile(tl[1], slot.get('tile2'), 'tile-2', 4000))
    used_h = {x.get('h') for x in tl} | {cta.get('h')}

    # ---------- 5 statement with label ----------
    stt = g('statement')
    P = ''
    if stt.get('text') or stt.get('title'):
        body = stt.get('text') or stt.get('title')
        P = '<section class="ph g">%s<div class="r">%s%s</div></section>' % (
            '<p class="cap l rvb">%s</p>' % e(stt['title']) if stt.get('text') and stt.get('title') else '',
            words(body, 'h2', 'mid', True), link(sec) if sec.get('t') else '')

    # ---------- the list part (reference: treatments page) — catalogue, questions ----------
    def lst(label, intro, groups, note, kind, pic=None):
        out, n, first_open = '', 0, True
        total = sum(len(x['items']) for x in groups)
        for gr in groups:
            rows = ''
            for it in gr['items']:
                n += 1
                extra = ''
                if it.get('text'):
                    extra += '<p>%s</p>' % e(it['text'])
                if it.get('prices'):
                    extra += '<dl>%s</dl>' % ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(x.get('label')), e(x.get('price'))) for x in it['prices'])
                if it.get('rows'):
                    extra += '<ul>%s</ul>' % ''.join('<li>%s</li>' % e(x) for x in it['rows'])
                if it.get('note'):
                    extra += '<p class="mut">%s</p>' % e(it['note'])
                if it.get('h') and it.get('text'):
                    extra += '<a class="ul" href="%s">%s</a>' % (e(it['h']), e(it['name']))
                pr = ''
                if it.get('price'):
                    pr = '<span class="pr">%s</span>' % e(it['price'])
                if it.get('state'):
                    pr += '<span class="pr mut">%s</span>' % e(it['state'])
                hd = '<span class="no">%02d</span><span class="nm">%s</span>%s' % (n, e(it['name']), pr)
                if extra:
                    rows += '<li><details%s><summary>%s</summary><div class="bd">%s</div></details></li>' % (' open' if first_open else '', hd, extra)
                    first_open = False
                else:
                    rows += '<li><div class="rw">%s</div></li>' % hd
            gh = ''
            if gr.get('t'):
                gh = '<h3>%s</h3>' % ('<a href="%s">%s</a>' % (e(gr['h']), e(gr['t'])) if gr.get('h') else e(gr['t']))
            if gr.get('text'):
                gh += '<p class="gi">%s</p>' % e(gr['text'])
            out += '<div class="grp">%s<ol>%s</ol></div>' % (gh, rows)
        return '<section class="ls g%s" data-part="%s">%s<div class="r">%s%s%s</div>%s</section>' % (
            ' pic' if pic else (' two' if total >= 8 else ''), kind, '<h2 class="cap l">%s</h2>' % e(label) if label else '', '<p class="in">%s</p>' % e(intro) if intro else '', out,
            '<p class="mut nt">%s</p>' % e(note) if note else '',
            '<div class="lp" data-slot="list"><div style="aspect-ratio:%.3f">%s</div></div>' % (max(1.25, min(1.6, pic['w'] / pic['h'])), img(pic)) if pic else '')

    C = ''
    cgroups = [{'t': x.get('t'), 'h': x.get('h'), 'text': x.get('text'), 'items': [i for i in (x.get('items') or []) if i.get('name')]} for x in (cat.get('groups') or [])]
    cgroups = [x for x in cgroups if x['items']]
    if cgroups:
        C = lst(cat.get('title'), cat.get('text'), cgroups, cat.get('note'), 'catalogue', s_cat)
    elif (g('features').get('items')):
        C = lst(g('features').get('title'), g('features').get('text'), [{'items': [{'name': f.get('t'), 'text': f.get('d')} for f in g('features')['items'] if f.get('t')]}], None, 'features')
    faq = g('faq')
    Q = ''
    if faq.get('items'):
        Q = lst(faq.get('title'), None, [{'items': [{'name': f.get('q'), 'text': f.get('a')} for f in faq['items'] if f.get('q')]}], None, 'faq')

    # ---------- 6 tall picture, small picture with lines, heading at the foot ----------
    close = g('close')
    trust = [t for t in (d.get('trust') or []) if t]
    Mth = ''
    mb = slot.get('method')
    ms = None
    if mb or close.get('title'):
        ms = s_meth
        capt = '<ul>%s</ul>' % ''.join('<li>%s</li>' % e(t) for t in trust[:6]) if trust else ''
        Mth = '<section class="me%s"><div class="g">%s%s%s</div></section>' % (
            '' if mb else ' nopic',
            words(close['title'], 'h2', 'big') if close.get('title') else '',
            '<div class="mbig" data-slot="method" style="--h:%dpx"><div class="clip"><div class="par"%s>%s</div></div></div>' % (cap(mb, 1233), par(mb, 1233), img(mb)) if mb else '',
            '<div class="msm rvb">%s%s</div>' % ('<div class="mp" data-slot="method-small" style="max-width:%dpx;--a:%.3f">%s</div>' % (ms['w'], max(.8, min(1.6, ms['w'] / ms['h'])), img(ms)) if ms else '', capt) if (ms or capt) else '')

    # ---------- the people (reference: about page) ----------
    def person(p, rowform):
        ph = by_src.get(p.get('img'))
        pic = '<div class="pp" style="max-width:%dpx;--a:%.3f">%s</div>' % (min(ph['w'], 342), max(.75, min(1.0, ph['w'] / ph['h'])), img(ph)) if ph else ''
        nm = '<h3>%s</h3>' % ('<a href="%s">%s</a>' % (e(p['h']), e(p.get('name'))) if p.get('h') else e(p.get('name')))
        meta = ''.join(x for x in [
            '<p class="role">%s</p>' % e(p['role']) if p.get('role') else '',
            '<p><a class="ul" href="tel:%s">%s</a></p>' % (e(str(p['phone']).replace(' ', '')), e(p['phone'])) if p.get('phone') else '',
            '<p><a class="ul" href="mailto:%s">%s</a></p>' % (e(p['email']), e(p['email'])) if p.get('email') else ''])
        if rowform:
            return '<li class="prow g">%s<div class="c2">%s</div><div class="c3">%s</div><div class="c4"><p>%s</p></div></li>' % (nm, pic, meta, e(p.get('text')))
        return '<li class="pc">%s%s%s</li>' % (pic, nm, meta)

    Tm = ''
    if people:
        def block(items):
            full = [p for p in items if p.get('text')]
            short = [p for p in items if not p.get('text')]
            return ('<ul class="prows">%s</ul>' % ''.join(person(p, True) for p in full) if full else '') + \
                   ('<ul class="pgrid">%s</ul>' % ''.join(person(p, False) for p in short) if short else '')
        if tgroups:
            inner = ''.join('<p class="cap gl">%s</p>%s' % (e(x.get('t')), block(x['items'])) for x in tgroups)
        else:
            inner = block(people)
        Tm = '<section class="tm">%s%s</section>' % ('<div class="g th">%s</div>' % words(team['title'], 'h2', 'big') if team.get('title') else '', inner)

    # ---------- 7 band with three words ----------
    Bd = ''
    bp = slot.get('band')
    ks = [x.get('k') for x in its if x.get('k') and len(x['k']) <= 14][:3]
    if bp:
        Bd = '<section class="band" data-slot="band" style="height:min(110svh,%dpx)"><div class="par"%s>%s</div></section>%s' % (
            cap(bp, 4000), par(bp, 990), img(bp), '<p class="bw g">%s</p>' % ''.join('<span>%s</span>' % e(k) for k in ks) if len(ks) >= 2 else '')
    Af = ''
    if steps.get('text'):
        Af = '<section class="af g">%s</section>' % words(steps['text'], 'h2', 'mid', True)

    # ---------- 8 words, and two tiles ----------
    Ap = ''
    rest_links = [l for l in links if l.get('h') not in used_h][:2]
    if close.get('text') or len(rest_links) == 2:
        tiles2 = ''
        if len(rest_links) == 2 and not (slot.get('ap1') and slot.get('ap2')):
            tiles2 = '<ul class="tl">%s</ul>' % ''.join('<li>%s</li>' % link(l) for l in rest_links)
        elif len(rest_links) == 2:
            tiles2 = '<ul class="t2">%s%s</ul>' % (tile(rest_links[0], slot.get('ap1'), 'approach-1', 429), tile(rest_links[1], slot.get('ap2'), 'approach-2', 429))
        Ap = '<section class="ap g">%s<div class="c rvb%s">%s%s</div>%s</section>' % (
            '<h2 class="cap l">%s</h2>' % e(hero['kicker']) if hero.get('kicker') else '', ' wide' if len(close.get('text') or '') > 300 else '',
            '<p>%s</p>' % e(close['text']) if close.get('text') else '', link(close.get('cta') or cta), tiles2)

    # ---------- the row part (reference: about page, the person row) — plans, credentials, quotes, other doors ----------
    def rows(kind, label, items):
        return '<section class="rs" data-part="%s">%s<ul>%s</ul></section>' % (kind, '<div class="g"><h2 class="cap l">%s</h2></div>' % e(label) if label else '', ''.join(items))

    Pl = ''
    plans = g('plans')
    if plans.get('items'):
        li = []
        for p in plans['items']:
            li.append('<li class="prow g%s"><h3>%s</h3><div class="c2"><p class="price">%s%s</p></div><div class="c3">%s%s</div><div class="c4">%s</div></li>' % (
                ' mk' if p.get('marked') else '', e(p.get('name')), e(p.get('price')), ' <span>%s</span>' % e(p['per']) if p.get('per') else '',
                '<p>%s</p>' % e(p['line']) if p.get('line') else '', '<ul class="pl">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in p['rows']) if p.get('rows') else '',
                link(p.get('cta') if isinstance(p.get('cta'), dict) else ({'t': p['cta'], 'h': cta.get('h')} if p.get('cta') else None))))
        Pl = rows('plans', plans.get('title'), li)
        if plans.get('text') or plans.get('note'):
            Pl = Pl.replace('</section>', '<div class="g"><p class="mut nt2">%s</p></div></section>' % e(' '.join(x for x in [plans.get('text'), plans.get('note')] if x)))
    Cr = ''
    creds = [c for c in (g('credentials', []) or []) if c.get('t')]
    if creds:
        Cr = rows('credentials', None, ['<li class="prow g"><h3>%s</h3><div class="c2">%s</div><div class="c3 w">%s%s</div></li>' % (
            ('<a href="%s">%s</a>' % (e(c['h']), e(c['t'])) if c.get('h') else e(c['t'])), '<p class="role">%s</p>' % e(c['year']) if c.get('year') else '',
            '<p>%s</p>' % e(c['text']) if c.get('text') else '', '') for c in creds])
    Lo = ''
    locs = [l for l in (g('locations', []) or []) if l.get('name')]
    if locs:
        def loc(l):
            a = l.get('address') or {}
            al = [x for x in [a.get('street'), ' '.join(x for x in [a.get('postcode'), a.get('city')] if x)] if x]
            hh = ''.join('<p>%s %s</p>' % (e(h.get('days')), e(' – '.join(x for x in [h.get('open'), h.get('close')] if x))) for h in (l.get('hours') or []))
            ph = l.get('phone')
            ph = ph.get('t') if isinstance(ph, dict) else ph
            return '<li class="prow g"><h3>%s</h3><div class="c2"><address>%s</address></div><div class="c3">%s%s</div><div class="c4">%s%s</div></li>' % (
                ('<a href="%s">%s</a>' % (e(l['h']), e(l['name'])) if l.get('h') else e(l['name'])), '<br>'.join(e(x) for x in al),
                '<p>%s</p>' % e(ph) if ph else '', '<p>%s</p>' % e(l['email']) if l.get('email') else '', hh, '<p class="mut">%s</p>' % e(l['note']) if l.get('note') else '')
        Lo = rows('locations', None, [loc(l) for l in locs])
    Qu = ''
    qs = [q for q in (d.get('quotes') or []) if q.get('q')][:4]
    if qs:
        def quote(q):
            who = ' · '.join(x for x in [q.get('name'), q.get('role')] if x)
            return '<figure><figcaption class="rvb">%s%s</figcaption><blockquote>%s</blockquote></figure>' % (
                '<p class="cap">%s</p>' % e(who) if who else '', '<p class="qt">%s</p>' % e(q['title']) if q.get('title') else '',
                words('“' + q['q'].strip('“”"') + '”' if lang != 'de' else '„' + q['q'].strip('„“"') + '“', 'p', 'mid', True))
        Qu = '<section class="qu g%s">%s</section>' % (' one' if len(qs) == 1 else '', ''.join(quote(q) for q in qs))

    # ---------- foot ----------
    foot = g('foot')
    hrs = ''
    if hours:
        hrs = '<table class="hr"><tbody>%s</tbody></table>' % ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (e(h['days']), e(' – '.join(x for x in [h.get('open'), h.get('close')] if x))) for h in hours)
    if phone.get('note'):
        hrs += '<p class="hn">%s</p>' % e(phone['note'])
    fl = ''.join('<a class="ul" href="%s">%s</a>' % (e(l.get('h') or '#'), e(l['t'])) for l in (foot.get('links') or []) if l.get('t'))
    F = '<footer class="ft"><div class="g">%s%s%s<p class="cp">%s</p>%s</div></footer>' % (
        '<p class="tag">%s</p>' % e(hero.get('title') or name), '<table class="ct"><tbody>%s</tbody></table>' % crow if crow else '',
        '<div class="hw">%s</div>' % hrs if hrs else '', e(foot.get('legal') or ('© ' + name)), '<nav class="fl">%s</nav>' % fl if fl else '')
    fp = slot.get('foot')
    Fb = ''
    if fp:
        Fb = '<div class="fb" data-slot="foot" style="height:min(75svh,%dpx)"><div class="par" data-zoom>%s</div>%s</div>' % (
            cap(fp, 4000), img(fp), '')

    V = dict(ground=_hex(ground), ink=_hex(ink), accent=_hex(accent), deep=_hex(deep), tint=_hex(tint), muted=_hex(muted), ond=_hex(on_deep),
             line='color-mix(in srgb,%s 20%%,%s)' % (_hex(ink), _hex(ground)))
    css = CSS
    for k, v in V.items():
        css = css.replace('$' + k, v)
    return ('<!doctype html><html lang="%s" class="nojs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500&family=Instrument+Serif&display=swap" rel="stylesheet">'
            '<style>%s</style><script>document.documentElement.className="js"</script></head><body>%s<div class="pg">%s<main>%s</main></div><div class="fw">%s%s</div>%s<script>%s</script></body></html>') % (
        e(lang), e(' — '.join(x for x in [name, hero.get('title')] if x)), css, menu, header,
        first + S + W + T + P + C + Mth + Tm + Bd + Af + Ap + Pl + Q + Qu + Cr + Lo, F, Fb, '', JS)


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-padding-top:60px}
body{margin:0;background:$ground;color:$ink;font:400 15px/1.3 "Hanken Grotesk",system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:clip}
h1,h2,h3,p,ul,ol,figure,blockquote,dl,dd,table{margin:0;padding:0}ul,ol{list-style:none}table{border-collapse:collapse}th{font-weight:400;text-align:left;vertical-align:top}td{vertical-align:top}address{font-style:normal}
img{display:block;max-width:100%}a{color:inherit;text-decoration:none}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
.g{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:10px;padding:0 20px}
.cap{font-size:12px;line-height:1;letter-spacing:.03em;text-transform:uppercase;font-weight:400}
.mut{color:$muted}
.big,.mid,.tag,.it h3,.ls h3,.ls .nm,.prow h3,.pc h3,.menu ol a,.hrow h1,.hb,.bn{font-family:"Instrument Serif","Times New Roman",serif;font-weight:400;letter-spacing:0}
.big{font-size:52px;line-height:1}.mid{font-size:35px;line-height:1.05}
.ind{display:inline-block;width:120px}
.w{display:inline-block}
.ul{background:linear-gradient(currentColor,currentColor) 0 100%/100% 1px no-repeat;transition:background-size .4s cubic-bezier(.16,1,.3,1)}
.ul:hover{background-size:0 1px;background-position:100% 100%}
/* the dot that comes in from the left on hover (reference: 7px, .5s) */
.dot,.navl{position:relative;display:inline-block;transition:padding .5s cubic-bezier(.4,0,.2,1)}
.dot::before,.navl::before{content:"";position:absolute;left:0;top:50%;width:7px;height:7px;margin-top:-4px;border-radius:50%;background:$accent;opacity:0;transform:scale(0);transition:opacity .5s cubic-bezier(.4,0,.2,1),transform .5s cubic-bezier(.4,0,.2,1)}
.dot{padding-right:12px}.dot:hover,.dot:focus-visible{padding-left:12px;padding-right:0}
.dot:hover::before,.dot:focus-visible::before,.navl:hover::before,.navl:focus-visible::before{opacity:1;transform:none}
.navl{font-size:14px;line-height:1;letter-spacing:.028em;text-transform:uppercase;padding:17.5px 0 17.5px 14px;white-space:nowrap}
.pg{position:relative;z-index:2;background:$ground}
/* header: 46 high, stays at the top, lies under the first screens */
.hd{position:sticky;top:0;z-index:20;height:46px;background:$ground}
.hd .g{align-items:center;height:46px}
.brand{grid-column:1/span 4;display:inline-flex;align-items:center;justify-self:start}
.logo{height:26px;width:auto;max-width:200px;object-fit:contain}.bn{font-size:21px;line-height:1;white-space:nowrap}
.hd nav{grid-column:5/-1;display:flex;justify-content:flex-end;gap:46px}
/* first screens */
.hero{position:relative;z-index:30;margin-top:-46px;background:$ground;overflow:clip}
.hs{position:relative;overflow:clip}
.hs::after{content:"";position:absolute;inset:0;background:rgba(0,0,0,.12);pointer-events:none}
.par{position:absolute;inset:0;will-change:transform}.par img{width:100%;height:100%;object-fit:cover}
.hrw{position:absolute;inset:0;z-index:2;pointer-events:none}
.hrow{position:sticky;top:calc(50svh - 23px);min-height:46px;align-items:center;color:#fff;pointer-events:auto}
.hrow::before{content:"";position:absolute;left:0;right:0;top:calc(23px - 50svh);height:100svh;z-index:-1;pointer-events:none;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.1) 18%,rgba(0,0,0,.3) 33%,rgba(0,0,0,.46) 43%,rgba(0,0,0,.5) 47%,rgba(0,0,0,.5) 53%,rgba(0,0,0,.46) 57%,rgba(0,0,0,.3) 67%,rgba(0,0,0,.1) 82%,rgba(0,0,0,0))}
.hb{grid-column:1/span 2;font-size:19px;line-height:1.1}
.hrow h1{grid-column:3/span 3;font-size:19px;line-height:1.1;letter-spacing:.02em}
.hrow nav{grid-column:6/-1;display:flex;justify-content:flex-end;gap:47px}
.hrow .navl{font-size:13px;padding:16.25px 0 16.25px 13px}.hrow .navl::before{background:#fff}
.hero.plain{margin-top:0;z-index:1}.hero.plain .hrw{position:static}.hero.plain .hrow{position:static;color:$ink;padding-top:22vh;padding-bottom:22vh}.hero.plain .hrow::before{display:none}.hero.plain .navl::before{background:$accent}
.pho,.hc{display:none}
/* opening statement */
.st{padding-top:40px;row-gap:28px}
.spic{grid-column:1/span 2;align-self:start}
.spic img{width:100%;height:auto;aspect-ratio:var(--a,auto);object-fit:cover}
.spic figcaption{margin-top:10px}.spic figcaption span{display:block;color:$muted}
.stx{grid-column:4/-1}
.sub{margin-top:36px;max-width:312px}.sub p+p{margin-top:12px}.sub .cap{margin-top:24px;display:block;width:max-content;max-width:100%}
/* pinned list */
.why{margin-top:60px;padding:0 20px}
.wh{padding:0;row-gap:20px}.wh .cnt{grid-column:1/span 2;font-variant-numeric:tabular-nums}.wh .cnt b{font-weight:400}.wh h2{grid-column:3/-1}
.prog{grid-column:1/-1;height:1px;background:$line}.prog i{display:block;height:100%;background:$ink;transform-origin:0 50%;transform:scaleX(var(--p,1))}
.its{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));margin-top:21px}
.it .md{position:relative;aspect-ratio:350/263;overflow:hidden}.it .md img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.it .tx{display:grid;grid-template-columns:55px minmax(0,1fr);margin-top:20px;padding-right:72px}
.it h3{font-size:19px;line-height:1.1}.it .more p{margin-top:12px}.it .more .cap{margin-top:16px}
.js .why{height:calc(100svh + var(--k)*20vh)}
.js .why .pin{position:sticky;top:0;height:100svh;display:flex;align-items:center}
.js .why .wi{width:100%}
.js .it{opacity:.1;transition:opacity .3s cubic-bezier(.16,1,.3,1)}.js .it .more{opacity:0;transition:opacity .3s cubic-bezier(.16,1,.3,1)}
.js .it.on,.js .it:focus-within{opacity:1}.js .it.on .more,.js .it:focus-within .more{opacity:1}
/* tiles */
.tiles ul{display:grid;grid-template-columns:1fr 1fr}
.tile{position:relative;height:min(100svh,var(--h,900px));overflow:hidden;isolation:isolate;background:$tint;color:$ond}
.tile .par{transition:opacity .3s cubic-bezier(.4,0,.2,1)}.tile .par img{filter:grayscale(1);transition:filter .3s cubic-bezier(.4,0,.2,1)}
.tile .sc,.tile .mu{position:absolute;inset:0;transition:opacity .3s cubic-bezier(.4,0,.2,1);pointer-events:none}
.tile .sc{background:$deep;mix-blend-mode:screen;opacity:.8}.tile .mu{background:$tint;mix-blend-mode:multiply}
.tile.flat .sc,.tile.flat .mu{display:none}.tiles .tile.flat{height:429px}
.tile a{position:absolute;inset:0;z-index:4;padding:20px;text-align:center}
.tile a .cap{position:sticky;top:50svh;display:inline-block;padding:0 12px;transition:opacity .3s cubic-bezier(.4,0,.2,1)}
.tile a .cap::before{content:"";position:absolute;left:0;top:50%;width:7px;height:7px;margin:-4px 0 0 -4px;border-radius:50%;background:#fff;opacity:0;transition:opacity .3s}
@media(hover:hover){
.tile:not(.flat):hover .sc{opacity:0}.tile:not(.flat):hover .mu{opacity:.38}.tile:not(.flat):hover .par img{filter:none}.tile:hover a .cap::before{opacity:1}.tile:not(.flat):hover a .cap{text-shadow:0 1px 8px rgba(0,0,0,.6)}
ul:hover>.tile:not(:hover) .par{opacity:.3}ul:hover>.tile:not(:hover) .sc,ul:hover>.tile:not(:hover) .mu{opacity:0}ul:hover>.tile:not(:hover){background:$ground}ul:hover>.tile:not(:hover) a .cap{opacity:0}
}
/* statement with label */
.ph,.af,.ap,.ls,.me,.tm,.rs{margin-top:120px}
.ph{display:grid}.ph .l{grid-column:1/span 6}.ph .r{grid-column:7/-1}.ph .r .cap{display:block;width:max-content;max-width:100%;margin-top:36px}
.qu{margin-top:120px;row-gap:72px}.qu figure{grid-column:span 6;padding-right:40px}.qu.one figure{grid-column:7/-1}.qu figcaption{margin-bottom:28px}.qu .qt{margin-top:12px}
/* list part */
.ls .l{grid-column:1/span 3}.ls .r{grid-column:4/-1}
.ls .in{max-width:520px;margin-bottom:40px}
.ls .grp+.grp{margin-top:72px}.ls h3{font-size:31px;line-height:1.1;margin-bottom:18px}.ls .gi{max-width:520px;margin:-6px 0 18px}
.ls ol>li{border-top:1px solid $line;break-inside:avoid}
.ls.two .l{grid-column:1/-1;margin-bottom:28px}.ls.two .r{grid-column:1/-1}.ls.two ol{columns:2;column-gap:10px}
.ls.pic .l{grid-column:1/span 6;margin-bottom:28px}.ls.pic .r{grid-column:1/span 6;grid-row:2}.ls.pic .lp{grid-column:7/-1;grid-row:1/span 2}.lp>div{position:sticky;top:66px;overflow:hidden}.lp img{width:100%;height:100%;object-fit:cover}
.ls summary,.ls .rw{display:grid;grid-template-columns:55px minmax(0,1fr) auto;column-gap:0;align-items:baseline;padding:13px 0 12px;position:relative}
.ls summary{cursor:pointer;list-style:none;transition:padding .5s cubic-bezier(.4,0,.2,1)}.ls summary::-webkit-details-marker{display:none}
.ls summary::after{content:"";position:absolute;right:0;top:50%;width:7px;height:7px;margin-top:-4px;border-radius:50%;background:$accent;opacity:0;transform:scale(0);transition:opacity .5s,transform .5s}
.ls summary:hover::after,.ls details[open] summary::after{opacity:1;transform:none}
.ls .no{font-size:12px;letter-spacing:.03em;font-variant-numeric:tabular-nums}.ls .nm{font-size:21px;line-height:1.1}.ls .pr{padding-left:24px;white-space:nowrap}
.ls details .pr{padding-right:20px}
.ls .bd{padding:2px 0 22px 55px;max-width:645px}.ls .bd p+p,.ls .bd ul,.ls .bd dl,.ls .bd a{margin-top:10px}.ls .bd a{display:inline-block}
.ls .bd dl div{display:flex;justify-content:space-between;gap:24px;max-width:320px}.ls .bd ul li{padding-left:14px;position:relative}.ls .bd ul li::before{content:"–";position:absolute;left:0}
.ls .nt{margin-top:18px;max-width:520px}
/* tall picture */
.me{overflow:clip}.me .g{column-gap:0;grid-template-rows:auto}
.me h2{grid-column:1/span 4;grid-row:1;align-self:end;padding-bottom:108px}
.mbig{grid-column:7/-1;grid-row:1;padding-bottom:108px}
.mbig .clip{position:relative;overflow:hidden;height:min(1233px,var(--h))}
.msm{grid-column:5/span 2;grid-row:1;align-self:start;position:sticky;top:30svh;padding-right:10px}
.msm .mp img{width:100%;height:auto;aspect-ratio:var(--a);object-fit:cover}.msm ul{margin-top:10px}.msm li+li{margin-top:6px}
.me.nopic h2{padding-bottom:0}.me.nopic .msm{position:static;grid-column:7/span 3;align-self:end}
/* people */
.th h2{grid-column:10/-1}
.tm .gl{padding:0 20px;margin-top:60px}
.prows,.rs>ul{margin-top:60px}
.prow{border-top:1px solid $line;padding-top:10px;padding-bottom:60px}
.prow h3{grid-column:1/span 3;font-size:31px;line-height:1.05}.prow .c2{grid-column:4/span 2}.prow .pp{max-width:225px!important}.prow .c3{grid-column:7/span 2}.prow .c3.w{grid-column:7/span 4}.prow .c4{grid-column:10/-1}
.prow .role,.pc .role{font-size:12px;line-height:1.3}.prow p+p{margin-top:8px}
.prow .price{font:400 31px/1.05 "Instrument Serif",serif}.prow .price span{font:400 15px/1.3 "Hanken Grotesk",sans-serif}
.prow.mk h3::before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:$accent;margin-right:10px;vertical-align:middle}
.prow .pl li{padding-left:14px;position:relative}.prow .pl li::before{content:"–";position:absolute;left:0}
.pp img{width:100%;height:auto;aspect-ratio:var(--a);object-fit:cover}
.pgrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));row-gap:60px;border-top:1px solid $line;padding-top:20px;margin:60px 20px 0}
.pc{padding-right:8px}.pc h3{font-size:21px;line-height:1.1;margin-top:14px}.pc .role{margin-top:6px;color:$muted}.pc p{margin-top:4px}
.nt2{grid-column:1/span 6;margin-top:18px}
/* band with words */
.band{position:relative;overflow:hidden;margin-top:120px;display:flex;align-items:center}
.bw{text-transform:uppercase;display:flex;justify-content:space-between;align-items:center;margin-top:20px}.bw+.af{margin-top:72px}
.af{margin-top:24px}.af h2{grid-column:1/span 6}
.band+.ap,.band+.rs,.band+.ls{margin-top:120px}
/* words and two tiles */
.ap .l{grid-column:1/span 2}.ap .c{grid-column:3/span 2}.ap .c.wide{grid-column:3/span 3}.ap .c .cap{display:block;width:max-content;max-width:100%;margin-top:24px}
.tl{grid-column:7/span 3;align-self:start}.tl li+li{margin-top:14px}
.t2{grid-column:7/-1;display:grid;grid-template-columns:1fr 1fr;align-self:start}
.t2 .tile{height:auto;aspect-ratio:348/429;max-height:var(--h,429px)}.t2 .tile a{display:flex;align-items:center;justify-content:center}.t2 .tile a .cap{position:relative;top:auto}
/* foot */
.fw{position:relative}.ft{padding-top:160px;position:relative;z-index:2;background:$ground}
.ft .tag{grid-column:1/-1;font-size:19px;line-height:1.1;margin-bottom:100px}
.ct{grid-column:1/span 3;display:block;margin-bottom:100px}.ct tbody,.mct tbody{display:flex;flex-direction:column;gap:16px}.ct tr,.mct tr{display:flex}.ct th,.mct th{flex:0 0 54px}
.hw{grid-column:4/span 4;margin-bottom:100px}.hr th{padding:0 40px 4px 0}.hr td{padding:0 0 4px}.hn{margin-top:8px;color:$muted}
.cp{grid-column:1/span 6;padding-bottom:16px}.fl{grid-column:7/-1;display:flex;justify-content:flex-end;gap:52px;font-size:13px;color:$muted;padding-bottom:16px}
/* the band the foot uncovers */
.fb{position:sticky;bottom:0;z-index:1;overflow:hidden}
.fbl{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff}
.fbl span{padding:110px 0;width:100%;text-align:center;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.58) 38%,rgba(0,0,0,.58) 62%,rgba(0,0,0,0))}
/* menu */
.mbk{position:fixed;inset:0;z-index:90;background:color-mix(in srgb,$ground 55%,transparent);-webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);opacity:0;visibility:hidden;transition:opacity 1s cubic-bezier(.4,0,.2,1),visibility 0s 1s}
.menu{position:fixed;z-index:100;top:0;right:20px;width:363px;max-height:100svh;overflow:auto;background:$ground;padding:20px 20px 0;transform:translateY(-101%);visibility:hidden;transition:transform 1.2s cubic-bezier(.16,1,.3,1),visibility 0s 1.2s}
.menu:target,.menu.open{transform:none;visibility:visible;transition:transform 1.2s cubic-bezier(.16,1,.3,1),visibility 0s}
.menu:target+.mbk,.mbk.open{opacity:1;visibility:visible;transition:opacity 1s cubic-bezier(.4,0,.2,1),visibility 0s}
.mclose{display:inline-block;padding:0 0 0 0}
.menu ol{margin-top:64px;counter-reset:m;padding-bottom:92px}.menu ol li{counter-increment:m;display:grid;grid-template-columns:50px 1fr;align-items:baseline}
.menu ol li::before{content:counter(m) ".";font-size:11px}.menu ol a{font-size:30px;line-height:1.1;transition:padding .5s cubic-bezier(.4,0,.2,1)}.menu ol a:hover{padding-left:6px}
.mnote{display:flex;gap:10px;padding-bottom:24px}.mnote .mp{flex:0 0 101px}.mnote .mp img{width:101px;height:178px;object-fit:cover}
.mct{display:block;margin:0 -20px;padding:20px;background:$deep;color:$ond}
/* reveal: words and blocks rise 10px and fade (reference: about .6s each, one after the other) */
.js .rv .w{opacity:0;transform:translateY(10px);transition:opacity .6s cubic-bezier(.16,1,.3,1) calc(var(--i)*18ms),transform .6s cubic-bezier(.16,1,.3,1) calc(var(--i)*18ms)}
.js .rv.in .w{opacity:1;transform:none}
.js .rvb{opacity:0;transform:translateY(10px);transition:opacity .6s cubic-bezier(.16,1,.3,1) .35s,transform .6s cubic-bezier(.16,1,.3,1) .35s}
.js .rvb.in{opacity:1;transform:none}
@media(max-width:1023px){
body{font-size:13px}
.g{grid-template-columns:repeat(6,minmax(0,1fr));column-gap:8px;padding:0 16px}
.big{font-size:35px}.mid{font-size:26px}.ind{width:60px}
.dk{display:none!important}.hrow .pho{display:inline-block}.hrow .hc{display:block;grid-column:1/-1;grid-row:3;width:max-content;padding:8px 0;text-decoration:underline;text-underline-offset:4px}
.brand{grid-column:1/span 4;min-width:0}.bn{font-size:18px;white-space:normal;line-height:1.05}.logo{max-width:150px}
.hd nav{grid-column:5/-1;gap:18px}
.hrow{top:calc(50svh - 70px);row-gap:10px;padding-top:6px;padding-bottom:6px}.hrow::before{top:calc(70px - 50svh)}
.hb{grid-column:1/span 4;grid-row:1}.hrow nav{grid-column:5/-1;grid-row:1;gap:0}.hrow nav .navl:not(.pho){display:none}
.hrow h1{grid-column:1/-1;grid-row:2;font-size:19px}
.hrow .navl{font-size:14px}
.st{row-gap:28px}.spic{grid-column:1/span 3}.stx{grid-column:1/-1}.sub{max-width:none;margin-top:36px}
.why{margin-top:40px;padding:0 16px}.wh .cnt{grid-column:1/span 1}.wh h2{grid-column:2/-1}
.its{grid-template-columns:minmax(0,1fr);row-gap:40px}
.js .its>.it{grid-area:1/1}.js .it{opacity:0;pointer-events:none}.js .it.on{pointer-events:auto}
.it .md{aspect-ratio:358/269}
.tiles ul{grid-template-columns:1fr;padding:0 16px}.tile{height:auto;aspect-ratio:358/347;max-height:var(--h,347px)}
.tile a{display:flex;align-items:flex-end;justify-content:center}.tile a .cap{position:relative;top:auto}
.ph,.af,.ap,.ls,.me,.tm,.rs,.band,.qu{margin-top:96px}.qu figure,.qu.one figure{grid-column:1/-1;padding-right:0}.af{margin-top:24px}
.ph .l,.ph .r{grid-column:1/-1}.ph .l{margin-bottom:28px}
.ls .l,.ls .r,.ls.pic .l,.ls.pic .r,.ls.pic .lp{grid-column:1/-1}.ls.pic .r{grid-row:auto}.ls.pic .lp{grid-row:auto;margin-top:28px}.lp>div{position:static}.ls.two ol{columns:1}.ls .l{margin-bottom:28px}.ls summary,.ls .rw{grid-template-columns:36px minmax(0,1fr) auto}.ls .bd{padding-left:36px}.ls h3{font-size:26px}.ls .nm{font-size:19px}
.me h2{grid-column:1/-1;grid-row:3;padding:28px 0 0}.mbig{grid-column:1/-1;grid-row:1;padding:0}.mbig .clip{height:min(512px,var(--h))}
.msm{grid-column:1/span 3;grid-row:2;position:static;margin-top:0}.msm ul{margin-bottom:0}
.me.nopic .msm{grid-column:1/-1;grid-row:2;margin-top:20px}.me.nopic h2{grid-row:1;padding:0}
.th h2{grid-column:1/-1}.prows,.rs>ul,.pgrid{margin-top:36px}
.prow{row-gap:14px;padding-bottom:36px}.prow h3,.prow .c3,.prow .c3.w,.prow .c4{grid-column:1/-1}.prow .c2{grid-column:1/span 3}.prow h3{font-size:26px}
.pgrid{grid-template-columns:repeat(2,minmax(0,1fr));column-gap:8px;row-gap:36px;margin-left:16px;margin-right:16px}.pc{padding-right:8px}.pc h3{font-size:19px}
.bw{font-size:13px;margin-top:16px}.bw+.af{margin-top:56px}
.af h2{grid-column:1/-1}
.ap .l,.ap .c,.ap .c.wide{grid-column:1/-1}.ap .l{margin-bottom:20px}.tl{grid-column:1/-1;margin-top:28px}.t2{grid-column:1/-1;grid-template-columns:1fr;margin-top:28px}.t2 .tile{aspect-ratio:358/347}.t2 .tile a{align-items:flex-end}
.ct,.hw{grid-column:1/-1;margin-bottom:24px}.ct th{flex-basis:52px}.hw{margin-bottom:80px}.ft .tag{margin-bottom:100px}
.cp{grid-column:1/-1;padding-bottom:10px}.fl{grid-column:1/-1;justify-content:space-between;gap:16px;flex-wrap:wrap}
.menu{left:16px;right:16px;width:auto;padding:16px 16px 0}.mct{margin:0 -16px;padding:16px}.menu ol a{font-size:26px}
}
@media(prefers-reduced-motion:reduce){
*,*::before,*::after{transition-duration:.01ms!important;transition-delay:0s!important;animation:none!important}
.js .rv .w,.js .rvb{opacity:1;transform:none}
.js .why{height:auto}.js .why .pin{position:static;height:auto;display:block}.js .it,.js .it .more{opacity:1;pointer-events:auto}
.js .its>.it{grid-area:auto}.prog i{transform:none}
}
"""

JS = r"""
(function(){
var D=document,R=D.documentElement,still=matchMedia('(prefers-reduced-motion:reduce)').matches,wide=matchMedia('(min-width:1024px)');
/* menu */
var m=D.getElementById('menu'),bk=D.getElementById('mbk'),last=null;
function mset(o){if(!m)return;m.classList.toggle('open',o);bk.classList.toggle('open',o);if(o){var c=D.getElementById('mclose');c&&c.focus({preventScroll:true})}else if(last){last.focus({preventScroll:true})}}
if(m){[].forEach.call(D.querySelectorAll('.mopen'),function(b){b.addEventListener('click',function(ev){ev.preventDefault();last=b;mset(true)})});
D.getElementById('mclose').addEventListener('click',function(ev){ev.preventDefault();mset(false)});bk.addEventListener('click',function(){mset(false)});
D.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&m.classList.contains('open'))mset(false)});
m.addEventListener('click',function(ev){if(ev.target.closest('ol a'))mset(false)})}
/* reveal */
var rv=[].slice.call(D.querySelectorAll('.rv,.rvb'));
if('IntersectionObserver' in window&&!still){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}})},{rootMargin:'0px 0px -8% 0px'});rv.forEach(function(x){io.observe(x)})}
else rv.forEach(function(x){x.classList.add('in')});
/* scroll-bound parts */
var why=D.querySelector('.why'),its=why?[].slice.call(why.querySelectorAll('.it')):[],cnt=why&&why.querySelector('.cnt b'),prog=why&&why.querySelector('.prog i');
var pars=[].slice.call(D.querySelectorAll('[data-par]')),clip=D.querySelector('.mbig .clip'),zoom=D.querySelector('[data-zoom]'),ft=D.querySelector('.ft'),tick=false,cur=-1;
function frame(){tick=false;var vh=innerHeight;
 if(why&&!still){var r=why.getBoundingClientRect(),len=r.height-vh,p=len>0?Math.min(1,Math.max(0,-r.top/len)):1,i=Math.min(its.length-1,Math.floor(p*its.length));
  prog.style.setProperty('--p',p.toFixed(4));if(i!==cur){cur=i;its.forEach(function(a,k){a.classList.toggle('on',k===i)});cnt.textContent=i+1}}
 if(still)return;
 var on=wide.matches;
 pars.forEach(function(el){var b=el.parentNode.getBoundingClientRect();if(!on){if(el.style.transform)el.style.transform='';return}if(b.bottom<-200||b.top>vh+200)return;
  var t=(b.top+b.height/2-vh/2)/(vh/2+b.height/2);t=Math.max(-1,Math.min(1,t));el.style.transform='translate3d(0,'+(-t*4).toFixed(2)+'%,0) scale(1.085)'});
 if(clip){var c=clip.getBoundingClientRect();if(on){var q=Math.min(1,Math.max(0,(vh-c.top)/(vh*.55)));clip.style.clipPath='inset(0 '+((1-q)*20).toFixed(2)+'% 0 0)'}else clip.style.clipPath=''}
 if(zoom&&ft){var f=ft.getBoundingClientRect();if(on){var z=Math.min(1,Math.max(0,(vh-f.bottom)/(vh*.75)));zoom.style.transform='scale('+(1.5-.5*z).toFixed(4)+')'}else zoom.style.transform=''}
}
addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(frame)}},{passive:true});addEventListener('resize',frame);frame();
})();
"""
