"""ptw/render.py — one pure function: render(d) -> a complete page.

The build (section order, 12-column grid, measures, type scale, spacing, grounds, motion, the phone build) was measured
on the reference's home, people and contact pages at 1440 and 390 on 2026-11-12 (see NOTES.md). Nothing of the
reference's code, words, pictures, drawings, icons, logo or typefaces is here. Where the reference shows a pen drawing
the client's own photograph stands (as a wide band, never a box beside text) or the slot stays plain.
A section whose data is missing is left out whole. No model call, no file reads, no client logic.
"""
import html
import json
import re

FONTS = ('https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Tinos:ital,wght@0,400;0,700;1,400'
         '&family=Inter:wght@200;300;400&family=Courier+Prime&family=Cinzel:wght@400&display=swap')

# words of the interface itself (not client copy); a language not listed falls back to signs only
UI = {'en': {'menu': 'Menu', 'close': 'Close', 'next': 'Next', 'prev': 'Back', 'skip': 'Skip to content'},
      'de': {'menu': 'Menü', 'close': 'Schließen', 'next': 'Weiter', 'prev': 'Zurück', 'skip': 'Zum Inhalt'}}


# ───────────────────────── colour: the reference's relations of ground / lighter zone / tint band / dark band / accent
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


def _toward(col, target, grounds, floor):
    """col moved toward target in its own hue until it reads at `floor` on every ground given"""
    t = 0.0
    out = col
    while min(_con(out, g) for g in grounds) < floor and t < 1:
        t += .04
        out = _mix(target, col, t)
    return out


def _palette(p):
    g, k, a = p.get('ground') or '#ffffff', p.get('ink') or '#111111', p.get('accent') or p.get('ink') or '#111111'
    dark_page = _lum(g) < .45
    if dark_page:                                   # not seen on a test client; relations kept the same way round
        alt = _mix('#ffffff', g, .06)
        deep, deep_ink = _mix('#000000', g, .45), k
    else:
        # the reference: a soft grey ground and a brighter zone for the quotations. A client ground that is already
        # white cannot go brighter, so the zone goes 5 % toward the ink instead.
        alt = _mix(k, g, .05) if _lum(g) > .85 else _mix('#ffffff', g, .6)
        deep, deep_ink = (k, g) if _lum(k) < .2 else (_mix('#000000', k, .35), g)
    tint = _mix(a, g, .26)
    while _con(k, tint) < 7 and _con(tint, g) > 1.02:
        tint = _mix(g, tint, .2)
    # accent as large type (the wordmark, the hovered service, the band's link): its own hue, deepened to 3.2:1
    acc = _toward(a, '#ffffff' if dark_page else '#000000', [g, alt, tint], 3.2)
    acc_small = _toward(a, '#ffffff' if dark_page else '#000000', [g, alt, tint], 4.6)
    acc_deep = _toward(a, '#ffffff', [deep], 3.2)
    acc_deep_small = _toward(a, '#ffffff', [deep], 4.6)
    v = {'g': g, 'k': k, 'alt': alt, 'tint': tint, 'deep': deep, 'dk': deep_ink, 'acc': acc, 'accs': acc_small,
         'accd': acc_deep, 'accds': acc_deep_small, 'mute': _toward(_mix(k, g, .6), k, [g, alt, tint], 4.6), 'line': k}
    return ';'.join('--%s:%s' % kv for kv in v.items())


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def _paras(s):
    return [x.strip() for x in re.split(r'\n\s*\n', str(s or '')) if x.strip()]


def _p(s, cls=''):
    c = ' class="%s"' % cls if cls else ''
    return ''.join('<p%s>%s</p>' % (c, e(x).replace('\n', '<br>')) for x in _paras(s))


def _src(s):
    s = str(s or '')
    return s if re.match(r'^(https?:|data:|/)', s) else '../../' + s


def _tel(s):
    return 'tel:' + re.sub(r'[^\d+]', '', str(s or ''))


def _btn(c, cls=''):
    if not c or not c.get('t'):
        return ''
    return '<a class="btn %s" href="%s" data-type><span class="btx">%s</span></a>' % (cls, e(c.get('h') or '#'), e(c['t']))


ARROW = ('<svg class="arw" viewBox="0 0 32 18" aria-hidden="true"><path d="M0 9h30M22 1l8 8-8 8" fill="none" '
         'stroke="currentColor" stroke-width="1.6"/></svg>')


def _addr(a):
    if not a:
        return ''
    if isinstance(a, str):
        return e(a)
    l2 = ' '.join(x for x in (a.get('postcode'), a.get('city')) if x)
    if a.get('city') and a.get('postcode') and re.match(r'^[A-Za-z]', str(a['postcode'])):
        l2 = '%s %s' % (a['city'], a['postcode'])            # letters-first postcodes are written after the town
    return '<br>'.join(e(x) for x in (a.get('street'), l2, a.get('region'), a.get('country')) if x)


def _hours(hs):
    rows = ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (
        e(h.get('days')), e(' – '.join(x for x in (h.get('open'), h.get('close')) if x))) for h in hs or [] if h.get('days'))
    return '<table class="hrs">%s</table>' % rows if rows else ''


def _pick_photos(d):
    """Photographs by role, each once: one opens the page, one stands over the people, one over the way to the door,
    one over the firm's own words. Portraits stay with their people; a small picture is never a band."""
    m = d.get('media') or {}
    taken = set()
    for it in ((d.get('steps') or {}).get('items') or []):
        taken.add(it.get('img'))
    team = d.get('team') or {}
    for it in (team.get('items') or []) + [i for g in team.get('groups') or [] for i in g.get('items') or []]:
        taken.add(it.get('img'))
    for c in d.get('credentials') or []:
        taken.add(c.get('img'))
    for g in (d.get('catalogue') or {}).get('groups') or []:
        taken.add(g.get('img'))
        for it in g.get('items') or []:
            taken.add(it.get('img'))
    pool = [p for p in m.get('photos') or [] if p.get('src') and p['src'] not in taken and not p.get('small')
            and p.get('role') != 'portrait' and (p.get('w') or 0) >= 1000 and (p.get('w') or 1) / (p.get('h') or 1) >= 1.2]
    out = {}

    def take(key, roles=None, avoid=()):
        for p in pool:
            if roles and p.get('role') not in roles:
                continue
            if p.get('role') in avoid:
                continue
            pool.remove(p)
            out[key] = p
            return

    lead = ('people', 'room', 'work', 'workshop', 'action', 'exterior', 'landscape', 'bar', 'product', 'dish', 'other')
    take('hero', lead, avoid=('detail',))
    if 'hero' not in out:
        take('hero')
    take('team', ('people',))
    take('door', ('exterior',))
    take('about', avoid=('detail',))
    if 'about' not in out:
        take('about')
    return out


def _band(p, slot):
    if not p:
        return ''
    w, h = p.get('w') or 1600, p.get('h') or 900
    r = w / h
    return ('<figure class="band" data-slot="%s" style="--r:%.3f;--rm:%.3f;--mw:%dpx"><img src="%s" width="%d" height="%d" '
            'alt="%s" loading="lazy"></figure>') % (slot, min(max(r, 2.2), 3.4), min(max(r, 1.3), 2.0), round(w * 1.2),
                                                   e(_src(p['src'])), w, h, e(p.get('alt') or ''))


# ───────────────────────── sections
def _head(d, ui):
    b = d.get('brand') or {}
    nav = [n for n in d.get('nav') or [] if n.get('t')]
    cta = d.get('cta') or {}
    right = nav[-2:] if len(nav) > 3 else []
    left = nav[:len(nav) - len(right)]
    lk = lambda n, c='': '<a class="%s" href="%s">%s</a>' % (c, e(n.get('h') or '#'), e(n['t']))
    place, contact = d.get('place') or {}, d.get('contact') or {}
    ph = contact.get('phone') or place.get('phone') or {}
    mail = contact.get('email') or place.get('email')
    logo = ''
    more = ''
    if ph.get('t') or mail:
        more = '<div class="mcontact">%s%s</div>' % (
            '<a href="%s">%s</a>' % (e(ph.get('h') or _tel(ph.get('t'))), e(ph['t'])) if ph.get('t') else '',
            '<a href="mailto:%s">%s</a>' % (e(mail), e(mail)) if mail else '')
    allnav = nav + ([cta] if cta.get('t') else [])
    return ('<a class="skip" href="#main">%s</a><header class="hd" id="hd"><nav class="nl" aria-label="1">%s</nav>%s'
            '<nav class="nr" aria-label="2">%s%s</nav>'
            '<details class="mn"><summary aria-label="%s"><i></i><i></i><i></i></summary><div class="mp"><nav>%s</nav>%s</div></details>'
            '</header>') % (e(ui.get('skip', '↓')), ''.join(lk(n) for n in left), logo, ''.join(lk(n) for n in right),
                            lk(cta) if cta.get('t') else '', e(ui.get('menu', '≡')), ''.join(lk(n) for n in allnav), more)


def _wordmark(name, tag='div', cls=''):
    words = [w for w in str(name or '').split() if w]
    n = max(sum(len(w) for w in words) + 1.3 * max(len(words) - 1, 0), 6)
    # The accent is deepened only to 3.2:1, which holds for type from 24 px. The name is sized to the width, so a long
    # name sets smaller: the smallest size it takes in each build (desktop from 1000 px, phone from 320 px, as the CSS
    # below) decides whether it may keep the large-type accent or takes the 4.6:1 one.
    small = [x for x, sz in (('sd', min(62, (1000 - 60) / (n * .86))), ('sm', min(26, (320 - 24) / (n * .86)))) if sz < 24]
    return '<%s class="wm %s" style="--n:%.1f">%s</%s>' % (tag, ' '.join([cls] + small).strip(), n, ''.join('<span>%s</span> ' % e(w) for w in words), tag)


def _hero_pic(p):
    if not p:
        return ''
    w, h = p.get('w') or 1600, p.get('h') or 900
    r = w / h
    return ('<div class="hero" data-slot="hero" style="--r:%.3f;--rm:%.3f"><img src="%s" width="%d" height="%d" alt="%s" '
            'fetchpriority="high"></div>') % (max(r, 1.6), max(.73, r / 2), e(_src(p['src'])), w, h, e(p.get('alt') or ''))


def _services(d):
    cat, feats = d.get('catalogue') or {}, d.get('features') or {}
    groups = [g for g in cat.get('groups') or [] if g.get('t')]
    priced = any(it.get('price') or it.get('prices') for g in groups for it in g.get('items') or [])
    rows, label = [], ''
    if groups and not priced:
        label = cat.get('title') or feats.get('title')
        for g in groups:
            subs = ''.join('<li>%s</li>' % ('<a href="%s">%s</a>' % (e(it['h']), e(it.get('name'))) if it.get('h') else e(it.get('name')))
                           for it in g.get('items') or [] if it.get('name'))
            t = '<h3>%s</h3>' % e(g['t'])
            desc = '<span class="sd">%s</span>' % e(g['text']) if g.get('text') else ''
            head = '<a class="sv" href="%s">%s%s</a>' % (e(g['h']), t, desc) if g.get('h') else '<div class="sv">%s%s</div>' % (t, desc)
            rows.append((1 + .42 * len(g.get('items') or []), '<li class="rv">%s%s</li>' % (head, '<ul class="sub">%s</ul>' % subs if subs else '')))
    elif feats.get('items'):
        label = feats.get('title')
        for it in feats['items']:
            if not it.get('t'):
                continue
            desc = '<span class="sd">%s</span>' % e(it['d']) if it.get('d') else ''
            rows.append((1, '<li class="rv"><div class="sv" tabindex="0"><h3>%s</h3>%s</div></li>' % (e(it['t']), desc)))
    if not rows:
        return ''
    total, acc, cut = sum(w for w, _ in rows), 0, len(rows)
    for i, (w, _) in enumerate(rows):
        acc += w
        if acc >= total / 2:
            cut = i + 1
            break
    cols = [rows[:cut], rows[cut:]]
    flat = all(w == 1 for w, _ in rows)
    intro = feats.get('text') if label == feats.get('title') else cat.get('text')
    return ('<section class="sec svc" id="services">%s%s<div class="g12 svcols">%s</div></section>') % (
        '<h2 class="lbl">%s</h2>' % e(label) if label else '',
        '<div class="svintro">%s</div>' % _p(intro) if intro else '',
        ('<ul class="svl flat" style="--rows:%d">%s</ul>' % (cut, ''.join(r for _, r in rows))) if flat else
        ''.join('<ul class="svl">%s</ul>' % ''.join(r for _, r in c) for c in cols if c))


def _block_a(title, text, extra='', band='', tag='h2', after='', cls='', sid=''):
    if not (title or text):
        return ''
    return ('<section class="sec ba %s"%s>%s<div class="g12"><div class="c5">%s<div class="tx">%s</div>%s</div></div>%s</section>') % (
        cls, ' id="%s"' % sid if sid else '', band, '<%s class="h">%s</%s>' % (tag, e(title), tag) if title else '', _p(text), extra, after)


def _fees(d):
    cat = d.get('catalogue') or {}
    groups = [g for g in cat.get('groups') or [] if g.get('items')]
    if not any(it.get('price') or it.get('prices') for g in groups for it in g.get('items') or []):
        return ''
    out = []
    for g in groups:
        rows = ''
        for it in g['items']:
            prices = ''
            if it.get('price'):
                prices += '<span class="pr">%s</span>' % e(it['price'])
            for pp in it.get('prices') or []:
                prices += '<span class="pr"><small>%s</small> %s</span>' % (e(pp.get('label')), e(pp.get('price')))
            if it.get('state'):
                prices += '<span class="meta">%s</span>' % e(it['state'])
            name = '<a href="%s">%s</a>' % (e(it['h']), e(it.get('name'))) if it.get('h') else e(it.get('name'))
            rows += ('<li><div class="fl"><h4>%s</h4>%s%s%s</div><div class="fr">%s</div></li>') % (
                name, '<span class="meta">%s</span>' % e(it['note']) if it.get('note') else '',
                '<div class="tx">%s</div>' % _p(it['text']) if it.get('text') else '',
                '<ul class="inc">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in it['rows']) if it.get('rows') else '', prices)
        out.append('<div class="g12 fg"><div class="c5"><h3>%s</h3><div class="tx">%s</div></div><ul class="c7 frows">%s</ul></div>' % (
            e(g.get('t')), _p(g.get('text')), rows))
    return ('<section class="sec bb fees" id="fees">%s<div class="g12"><div class="c5 tx">%s</div></div>%s%s</section>') % (
        '<h2 class="h">%s</h2>' % e(cat['title']) if cat.get('title') else '', _p(cat.get('text')), ''.join(out),
        '<div class="g12"><div class="c5 tx note">%s</div></div>' % _p(cat['note']) if cat.get('note') else '')


def _plans(d):
    pl = d.get('plans') or {}
    items = [i for i in pl.get('items') or [] if i.get('name')]
    if not items:
        return ''
    rows = ''
    for it in items:
        price = ' '.join(str(x) for x in (it.get('price'), it.get('per')) if x)
        rows += ('<li><div class="fl"><h4>%s</h4>%s%s%s</div><div class="fr">%s</div></li>') % (
            e(it['name']), '<div class="tx">%s</div>' % _p(it['line']) if it.get('line') else '',
            '<ul class="inc">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in it['rows']) if it.get('rows') else '',
            _btn(it.get('cta'), 'sm'), '<span class="pr">%s</span>' % e(price) if price else '')
    return ('<section class="sec bb fees" id="plans"><div class="g12 fg"><div class="c5">%s<div class="tx">%s%s</div></div>'
            '<ul class="c7 frows">%s</ul></div></section>') % (
        '<h2 class="h">%s</h2>' % e(pl['title']) if pl.get('title') else '', _p(pl.get('text')),
        _p(pl.get('note'), 'note'), rows)


def _block_b(title, intro, items, sid='', cols=None):
    """the reference's long text column: a heading across, then bold sub-heads each over its paragraph"""
    lst = lambda its: ''.join('<div class="si"><h3>%s</h3>%s%s</div>' % (e(t), _p(x), extra) for t, x, extra in its if t or x)
    if cols:
        body = '<div class="g12">%s</div>' % ''.join(
            '<div class="c6 tx">%s%s</div>' % ('<h3 class="gh">%s</h3>' % e(t) if t else '', lst(its)) for t, its in cols)
    else:
        body = '<div class="g12"><div class="c5 tx">%s%s</div></div>' % (_p(intro), lst(items))
        intro = ''
    if not (title or items or cols):
        return ''
    return '<section class="sec bb"%s>%s%s%s</section>' % (
        ' id="%s"' % sid if sid else '', '<h2 class="h">%s</h2>' % e(title) if title else '',
        '<div class="g12"><div class="c5 tx">%s</div></div>' % _p(intro) if intro else '', body)


def _steps(d):
    st = d.get('steps') or {}
    items = [i for i in st.get('items') or [] if i.get('title') or i.get('text')]
    if not items:
        return ''
    photos = {p.get('src'): p for p in (d.get('media') or {}).get('photos') or []}
    if any(i.get('img') in photos and not photos[i['img']].get('small') for i in items):
        out, lead = [], st.get('text')
        if st.get('title') and st['title'] != items[0].get('title'):
            out.append(_block_a(st['title'], lead))
            lead = ''
        for n, it in enumerate(items):
            p = photos.get(it.get('img'))
            text = (lead + '\n\n' if lead and n == 0 else '') + (it.get('text') or '')
            out.append(_block_a(it.get('title'), text, _btn(it.get('cta')), _band(p, 'step') if p and not p.get('small') else ''))
        return ''.join(out)
    return _block_b(st.get('title'), st.get('text'), [(i.get('title'), i.get('text'), _btn(i.get('cta'), 'sm')) for i in items], 'values')


def _details(d):
    """service descriptions of an unpriced catalogue, group by group, in the long-text part"""
    cat = d.get('catalogue') or {}
    groups = [g for g in cat.get('groups') or [] if g.get('items')]
    if any(it.get('price') or it.get('prices') for g in groups for it in g.get('items') or []):
        groups = []
    cols = [(g.get('t'), [(it.get('name'), it.get('text'), '') for it in g['items'] if it.get('text')]) for g in groups]
    cols = [c for c in cols if c[1]]
    if cols:
        return _block_b(None, None, None, 'details', cols)
    names = {it.get('name') for g in cat.get('groups') or [] for it in g.get('items') or []}
    feats = d.get('features') or {}
    shown_as_list = not (groups and not cols) and not cols and feats.get('items')
    if shown_as_list:
        return ''                      # the features stand in the overview with their sentence
    rest = [(i.get('t'), i.get('d'), '') for i in feats.get('items') or [] if i.get('t') not in names and i.get('d')]
    return _block_b(feats.get('title'), feats.get('text'), rest) if rest else ''


def _person(it, portrait=True):
    img = ''
    if portrait and it.get('img'):
        img = '<img src="%s" alt="" width="89" height="118" loading="lazy">' % e(_src(it['img']))
    name = '<a href="%s">%s</a>' % (e(it['h']), e(it.get('name'))) if it.get('h') else e(it.get('name'))
    em = it.get('email')
    return ('<li class="pp%s">%s<div><h3>%s</h3>%s%s%s%s</div></li>') % (
        '' if img else ' np', img, name, '<p class="role">%s</p>' % e(it['role']) if it.get('role') else '',
        '<p class="bio">%s</p>' % e(it['text']) if it.get('text') else '',
        '<a class="ct" href="%s">%s</a>' % (e(_tel(it['phone'])), e(it['phone'])) if it.get('phone') else '',
        '<a class="ct em" href="mailto:%s">%s</a>' % (e(em), e(em).replace('@', '<wbr>@')) if em else '')


def _team(d, band):
    tm = d.get('team') or {}
    groups = tm.get('groups') or ([{'t': None, 'items': tm.get('items')}] if tm.get('items') else [])
    groups = [g for g in groups if g.get('items')]
    if not groups:
        return ''
    body = ''
    for g in groups:
        withp = [i for i in g['items'] if i.get('img') and i.get('name')]
        nop = [i for i in g['items'] if not i.get('img') and i.get('name')]
        body += '<h3 class="gh">%s</h3>' % e(g['t']) if g.get('t') else ''
        body += '<ul class="ppl">%s</ul>' % ''.join(_person(i) for i in withp) if withp else ''
        body += '<ul class="ppl np">%s</ul>' % ''.join(_person(i, False) for i in nop) if nop else ''
    return ('<section class="sec team" id="team">%s%s%s%s</section>') % (
        band, '<h2 class="h">%s</h2>' % e(tm['title']) if tm.get('title') else '',
        '<div class="g12"><div class="c5 tx">%s</div></div>' % _p(tm['text']) if tm.get('text') else '', body)


def _faq(d):
    fq = d.get('faq') or {}
    items = [(i.get('q'), i.get('a'), '') for i in fq.get('items') or [] if i.get('q')]
    return _block_b(fq.get('title'), None, items, 'faq') if items else ''


def _quotes(d, ui):
    qs = [q for q in d.get('quotes') or [] if q.get('q')]
    if not qs:
        return ''
    its = ''
    for i, q in enumerate(qs):
        who = '<br>'.join(e(x) for x in (q.get('name'), q.get('role')) if x)
        its += '<figure class="q%s"><blockquote>%s</blockquote>%s</figure>' % (
            ' on' if i == 0 else '', e('“' + q['q'].strip('“”"') + '”'), '<figcaption>%s</figcaption>' % who if who else '')
    nxt = ('<button class="btn qn" type="button" hidden data-type><span class="btx">%s</span></button>' % e(ui.get('next', '→'))) if len(qs) > 1 else ''
    return '<section class="sec qz" id="quotes" data-zone="alt"><div class="ql">%s</div>%s</section>' % (its, nxt)


def _tintband(d):
    hero, place, contact = d.get('hero') or {}, d.get('place') or {}, d.get('contact') or {}
    ph = contact.get('phone') or place.get('phone') or {}
    cta = place.get('booking') or d.get('cta') or {}
    line = hero.get('text2') or cta.get('t')
    if ph.get('t'):
        link = '<a href="%s"><span>%s</span>%s</a>' % (e(ph.get('h') or _tel(ph['t'])), e(ph['t']), ARROW)
    elif cta.get('t') and line != cta.get('t'):
        link = '<a href="%s"><span>%s</span>%s</a>' % (e(cta.get('h') or '#'), e(cta['t']), ARROW)
    else:
        link = ''
    if not (line and link):
        return ''
    if hero.get('text2') or not cta.get('h'):
        first = '<span>%s</span>' % e(line)
    else:
        first = '<a class="pl" href="%s">%s</a>' % (e(cta['h']), e(line))
    return '<section class="tb" id="call"><p>%s%s</p></section>' % (first, link)


def _find(d, band):
    b, place, contact = d.get('brand') or {}, d.get('place') or {}, d.get('contact') or {}
    locs = [l for l in d.get('locations') or [] if l.get('name') or l.get('address')]
    ph = contact.get('phone') or place.get('phone') or {}
    mail = contact.get('email') or place.get('email')
    left = ''
    if ph.get('t'):
        left += '<p class="big"><a href="%s">%s</a></p>%s' % (e(ph.get('h') or _tel(ph['t'])), e(ph['t']),
                                                              '<p class="meta">%s</p>' % e(ph['note']) if ph.get('note') else '')
    if mail:
        left += '<p class="row"><a href="mailto:%s">%s</a></p>' % (e(mail), e(mail))
    for r in contact.get('routes') or []:
        if r.get('t'):
            t = '<a href="%s">%s</a>' % (e(r['h']), e(r['t'])) if r.get('h') else e(r['t'])
            left += '<p class="row">%s%s</p>' % (t, ' <span class="meta">%s</span>' % e(r['note']) if r.get('note') else '')
    for s in place.get('social') or []:
        if s.get('t') and s.get('h'):
            left += '<p class="row"><a href="%s">%s</a></p>' % (e(s['h']), e(s['t']))
    form = contact.get('form') or {}
    act = _btn({'t': form.get('t'), 'h': form.get('h')}) if form.get('t') else _btn(place.get('booking'))
    right = ''
    if locs:
        for l in locs:
            det = ''.join('<p class="row">%s</p>' % x for x in (
                _addr(l.get('address')),
                '<a href="%s">%s</a>' % (e(_tel(l['phone'])), e(l['phone'])) if l.get('phone') else '',
                '<a href="mailto:%s">%s</a>' % (e(l['email']), e(l['email'])) if l.get('email') else '') if x)
            name = '<a href="%s">%s</a>' % (e(l['h']), e(l.get('name'))) if l.get('h') else e(l.get('name'))
            right += '<div class="loc"><h3>%s</h3><div class="ld">%s%s</div>%s</div>' % (
                name, det, _hours(l.get('hours')), '<div class="tx">%s</div>' % _p(l['note']) if l.get('note') else '')
    else:
        a, hrs = _addr(place.get('address')), _hours(place.get('hours'))
        if a or hrs:
            right = '<div class="loc one">%s<div class="ld">%s</div>%s</div>' % (
                '<h3>%s</h3>' % e((place.get('address') or {}).get('city')) if isinstance(place.get('address'), dict) and place['address'].get('city') else '',
                '<p class="row">%s</p>' % a if a else '', hrs)
    if not (left or right):
        return ''
    return ('<section class="sec find" id="contact">%s<div class="g12"><div class="c5 reach"><h2 class="h3">%s</h2>%s%s</div>'
            '%s</div></section>') % (band, ('<img class="lh" src="%s" alt="%s">' % (e(_src(b['logo'])), e(b.get('name')))) if b.get('logo') else e(b.get('name')), left, act, '<div class="c7 panel">%s</div>' % right if right else '')


def _cards(d, ui):
    cr = [c for c in d.get('credentials') or [] if c.get('t')]
    if not cr:
        return ''
    cr = sorted(cr, key=lambda c: 0 if c.get('img') else 1)          # pictures first, so the titles line up
    out = ''
    for c in cr:
        img = '<span class="ci"><img src="%s" alt="" loading="lazy"></span>' % e(_src(c['img'])) if c.get('img') else ''
        meta = ''.join('<span>%s</span>' % e(x) for x in (c.get('year'),) if x)
        body = '%s<h3>%s</h3>%s%s' % (img, e(c['t']), '<p class="cx">%s</p>' % e(c['text']) if c.get('text') else '',
                                    '<p class="meta">%s</p>' % meta if meta else '')
        out += '<li>%s</li>' % ('<a href="%s">%s</a>' % (e(c['h']), body) if c.get('h') else '<div>%s</div>' % body)
    return ('<section class="cards" id="credentials"><ul class="cl" tabindex="0">%s</ul><div class="ca" hidden>'
            '<button type="button" class="cb" data-dir="-1" aria-label="%s">%s</button>'
            '<button type="button" class="cb" data-dir="1" aria-label="%s">%s</button></div></section>') % (
        out, e(ui.get('prev', '←')), ARROW, e(ui.get('next', '→')), ARROW)


def _foot(d):
    b, ft, place, contact, hero = d.get('brand') or {}, d.get('foot') or {}, d.get('place') or {}, d.get('contact') or {}, d.get('hero') or {}
    ph = contact.get('phone') or place.get('phone') or {}
    mail = contact.get('email') or place.get('email')
    a = place.get('address')
    left = ''.join('<li>%s</li>' % x for x in (
        '<a href="%s">%s</a>' % (e(ph.get('h') or _tel(ph.get('t'))), e(ph['t'])) if ph.get('t') else '',
        '<a href="mailto:%s">%s</a>' % (e(mail), e(mail)) if mail else '',
        _addr(a).replace('<br>', ', ') if a else '') if x)
    if not left and ft.get('text'):
        left = '<li>%s</li>' % e(ft['text'])
    lk = lambda l: '<li><a href="%s">%s</a></li>' % (e(l.get('h') or '#'), e(l['t']))
    c1 = ''.join(lk(l) for l in d.get('links') or [] if l.get('t'))
    c2 = ''.join(lk(l) for l in ft.get('links') or [] if l.get('t'))
    c3 = ''.join(lk(l) for l in place.get('social') or [] if l.get('t') and l.get('h'))
    notices = ''.join('<p>%s</p>' % '<br>'.join(e(t) for t in n.get('text') or []) for n in place.get('notices') or [] if n.get('text'))
    return ('<footer class="ft" id="ft">%s<div class="g12 fb"><div class="c5"><ul class="fc">%s</ul>%s</div>'
            '<div class="c7 fls">%s%s%s</div></div>%s</footer>') % (
        _wordmark(b.get('name'), 'p', 'fw'), left, '<p class="tag">%s</p>' % e(hero['kicker']) if hero.get('kicker') else '',
        '<ul>%s</ul>' % c1 if c1 else '', '<ul>%s</ul>' % c2 if c2 else '', '<ul>%s</ul>' % c3 if c3 else '',
        '<div class="lg">%s%s</div>' % (_p(ft.get('legal')), notices) if ft.get('legal') or notices else '')


CSS = r"""
*,*::before,*::after{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-padding-top:190px}
body{margin:0;background:var(--g);color:var(--k);font:400 15.2px/1.2 Tinos,'Times New Roman',Times,serif;
 transition:background-color .35s cubic-bezier(.19,1,.22,1);overflow-x:hidden}
body.alt{background:var(--alt)}
img{display:block;max-width:100%}a{color:inherit;text-decoration:none}ul{list-style:none;margin:0;padding:0}
h1,h2,h3,h4,p,figure,blockquote{margin:0;font-weight:inherit}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
.skip{position:fixed;left:3vw;top:-80px;z-index:200;background:var(--k);color:var(--g);padding:10px 14px;font:300 16px Inter,Arial,sans-serif}
.skip:focus{top:8px}
:root{--m:3vw;--gap:2vw;--pad:116.48px;--hh:88px;--wh:84px;--c:cubic-bezier(.19,1,.22,1)}
.sans,.hd,.lbl,.btn,.meta,.pp,.row,.hrs,.ft,.big{font-family:Inter,'Helvetica Neue',Arial,sans-serif}
.ser{font-family:'Instrument Serif','Times New Roman',serif}

/* header: 88 high, held at the top, takes the page's ground as it changes; light on the dark band */
.hd{position:fixed;inset:0 0 auto 0;height:var(--hh);z-index:100;display:flex;align-items:flex-start;justify-content:space-between;
 padding:33px var(--m) 0;background-color:inherit;font-weight:300;font-size:20px;line-height:22px;transition:color .35s var(--c)}
body.deep .hd{background:var(--deep);color:var(--dk)}
.hd nav{display:flex;gap:25px;white-space:nowrap}.hd a:hover{text-decoration:underline;text-underline-offset:4px}
.hlogo{position:absolute;left:50%;top:22px;transform:translateX(-50%)}.hlogo img{height:44px;width:auto;max-width:240px;object-fit:contain}
body.deep .hlogo{visibility:hidden}
.mn{display:none}
.wrap{background-color:inherit;position:relative}
main{display:block;padding-top:var(--hh);background-color:inherit}

/* first screen: the picture alone on the ground, the name across the foot of the window */
.hero{height:calc(100svh - var(--hh) - var(--wh));min-height:380px;margin:0 var(--m);display:flex;align-items:center;justify-content:center;overflow:hidden}
.hero{padding-bottom:22px}.hero img{width:100%;height:100%;max-height:calc((100vw - 2*var(--m))/var(--r));object-fit:cover}
.wmb{position:sticky;top:var(--hh);z-index:90;height:var(--wh);background-color:inherit;padding:0 var(--m)}
.wm{display:flex;justify-content:space-between;align-items:flex-start;white-space:nowrap;overflow:hidden;margin:0;
 font:400 min(62px,calc((100vw - 2*var(--m))/(var(--n)*.86)))/.84 Cinzel,'Times New Roman',serif;text-transform:uppercase;color:var(--acc);height:51px;padding-top:2px}
.wm span:only-child{margin:0}
@media (min-width:1000px){.wm.sd{color:var(--accs)}.ft .wm.sd{color:var(--accds)}}

.sec{padding:var(--pad) var(--m)}
.g12{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gap)}
.c5{grid-column:1/span 5;max-width:547px}.c6{grid-column:span 6}.c7{grid-column:7/span 6}
.lbl{font-weight:300;font-size:30px;line-height:33px;letter-spacing:3px;text-transform:uppercase}
.h,.svl h3,.tb p,.fg h3,.h3,.loc h3,.cl h3,.frows h4,.pr,.h6,.gh{font-family:'Instrument Serif','Times New Roman',serif;font-weight:400}
.h{font-size:52px;line-height:1;letter-spacing:-.005em;max-width:16.5em;text-wrap:balance}
.tx{margin-top:33px}.tx p+p{margin-top:18.24px}.h+.g12 .tx,.h+.tx{margin-top:33px}
.ba .c5>.tx:first-child,.c5.tx:empty{margin-top:0}
.tx a,.lg a{text-decoration:underline;text-underline-offset:2px}
.h6{font-size:26px;line-height:1;margin-top:67px;max-width:453px;display:block}
.h6 a:hover{color:var(--acc)}

/* services overview: two columns of 52px names; the sentence under a name comes up on hover (0.35s) */
.svc .lbl+.g12,.svintro+.g12{margin-top:25px}.svintro{max-width:547px;margin-top:20px;margin-bottom:34px}.svintro .tx,.svintro p{margin-top:0}
.svl{grid-column:span 6}
.svl.flat{grid-column:1/-1;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(var(--rows),1fr);grid-auto-flow:column;column-gap:var(--gap)}
.svl>li{margin-bottom:4.16px}
.sv{display:flex;flex-direction:column;align-items:flex-start}
.svl h3{font-size:52px;line-height:1;margin-bottom:8.32px;transition:color .35s var(--c)}
.sd{display:block;max-width:600px;margin-bottom:7px;min-height:18.24px;opacity:0;transform:translateY(-30px);transition:opacity .35s var(--c),transform .35s var(--c);pointer-events:none}
.sv:hover h3,.sv:focus-visible h3,.sub a:hover{color:var(--acc)}
.sv:hover .sd,.sv:focus-visible .sd,.sv:focus-within .sd{opacity:1;transform:translateY(-7px)}
@media (hover:none){.sd{opacity:1;transform:none;margin-top:-4px;margin-bottom:14px}}
.sub{margin:0 0 22px;padding-left:25px;list-style:disc;font:400 30px/1 'Instrument Serif','Times New Roman',serif}
.sub li{margin-bottom:4.4px}.sub li::marker{font-size:.6em}.sub a{transition:color .35s var(--c)}
.js .rv{opacity:0;transform:translateX(-40px)}.js .rv.in{opacity:1;transform:none;transition:opacity .5s cubic-bezier(.25,.8,.3,1),transform .5s cubic-bezier(.25,.8,.3,1)}

/* a photograph where the reference has a drawing: a band across the columns, never a box beside the text */
.band{margin:0 0 49.92px;aspect-ratio:var(--r);max-width:min(100%,var(--mw));overflow:hidden}
.band img{width:100%;height:100%;object-fit:cover}

/* buttons: 49 high, hairline, their words typed in letter by letter when they come into view */
.btn{display:inline-flex;align-items:center;height:49px;padding:0 16.64px;border:1px solid currentColor;background:transparent;color:inherit;
 font-weight:300;font-size:16px;line-height:1;cursor:pointer;white-space:nowrap;border-radius:0}
.btn.sm{margin-top:18px}.btx i{font-style:normal;opacity:0}.btx i.on{opacity:1}
.acts{display:flex;flex-wrap:wrap;gap:16px;margin-top:26px}
.c5>.btn{margin-top:26px}

/* fee list: rules kept for the table */
.fg{margin-top:66px}.fg h3{font-size:30px;line-height:1}.fg .c5 .tx{margin-top:14px}
.frows{border-top:1px solid var(--line)}
.frows>li{display:flex;justify-content:space-between;gap:28px;align-items:baseline;padding:15px 0 14px;border-bottom:1px solid var(--line)}
.frows h4{font-size:26px;line-height:1}.fl{min-width:0;max-width:440px}.fl .tx{margin-top:9px}.fl .meta{margin-top:7px}
.fr{text-align:right;flex:none;display:flex;flex-direction:column;gap:6px;align-items:flex-end}
.pr{font-size:26px;line-height:1;white-space:nowrap}.pr small{font:200 10px/1 Inter,Arial,sans-serif;letter-spacing:1px;text-transform:uppercase}
.inc{list-style:disc;padding-left:18px;margin-top:9px}.inc li{margin-top:3px}
.meta{display:block;font:300 10px/1.4 Inter,Arial,sans-serif;letter-spacing:1px;text-transform:uppercase;color:var(--k)}
.note{margin-top:33px;color:var(--k)}
.fees .h+.g12 .tx:empty{display:none}

/* long text: bold sub-heads over their paragraphs */
.si{margin-top:18.24px}.si h3{font:700 16.5px/1.2 Tinos,'Times New Roman',serif}.si p+p{margin-top:18.24px}
.gh{font-size:30px;line-height:1;margin:0 0 6px}.c6.tx{margin-top:0;padding-right:8.33%}
.bb .h+.g12{margin-top:0}

/* people: the reference's grid from its people page */
.team .h+.g12+.ppl,.team .h+.ppl,.team .band+.ppl{margin-top:33px}.team .g12+.ppl{margin-top:44px}.team .gh{margin-top:50px}
.ppl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));column-gap:var(--gap);row-gap:40px}
.ppl+.ppl{margin-top:56px}.ppl.np{grid-template-columns:repeat(4,minmax(0,1fr));row-gap:34px}
.pp{display:flex;gap:45px;align-items:flex-start;font-weight:300;font-size:12px;line-height:13.2px;letter-spacing:1.2px;text-transform:uppercase}
.pp img{width:89px;height:118px;object-fit:cover;flex:none}.pp>div{min-width:0;padding-top:4px}
.pp h3{font-weight:400;font-size:12px;line-height:13.2px}.pp .role{margin-top:4px}
.pp .bio{font:400 14px/16.8px Tinos,'Times New Roman',serif;letter-spacing:0;text-transform:none;margin-top:10px;max-width:270px}
.pp .ct{display:block;margin-top:9px;font-weight:400}.pp .ct+.ct{margin-top:6px}.pp .em{text-transform:none;letter-spacing:.4px;overflow-wrap:anywhere}
.pp a:hover{text-decoration:underline;text-underline-offset:3px}

/* quotations: the brighter zone, typewriter face, centred */
.qz{display:flex;flex-direction:column;align-items:center;text-align:center}
.ql{display:grid;max-width:880px}.q{grid-area:1/1;display:flex;flex-direction:column;align-items:center}
.q blockquote{font:400 18px/23.4px 'Courier Prime','Courier New',monospace}.q figcaption{margin-top:49px}
.js .q{visibility:hidden}.js .q.on{visibility:visible}
.q+.q{margin-top:60px}.js .q+.q{margin-top:0}
.q b{font-weight:400;opacity:0;transition:opacity 1.2s var(--c)}.q b.on{opacity:1}
.qn{margin-top:54px}

/* the floating call: held at the foot of the window from the second screen to the end of the main part */
.fl8{position:sticky;bottom:0;height:82px;margin-top:-82px;padding:0 var(--m);display:flex;justify-content:flex-end;align-items:flex-start;pointer-events:none;z-index:80;background:none}
.fl8 .btn{pointer-events:auto;background-color:var(--g);transition:background-color .35s var(--c),opacity .35s var(--c),visibility .35s}
body.alt .fl8 .btn{background-color:var(--alt)}
.js .fl8 .btn{opacity:0;visibility:hidden}.js .fl8.on .btn{opacity:1;visibility:visible}

/* the tinted band */
.tb{background:var(--tint);padding:49.92px var(--m);text-align:center}
.tb p{font-size:52px;line-height:1;display:flex;flex-direction:column;align-items:center}
.tb a{color:var(--acc);display:inline-flex;align-items:center;gap:8px}.tb a.pl{color:inherit}.tb a:hover span,.tb a.pl:hover{text-decoration:underline;text-underline-offset:6px;text-decoration-thickness:1.5px}
.arw{width:27px;height:16px;flex:none;margin-top:6px}

/* where to find them: the reference's contact page — details at the left, a tinted panel that runs to the right edge */
.find{padding-bottom:var(--pad)}.find .g12{align-items:start}
.h3{font-size:30px;line-height:1}.lh{height:56px;width:auto;max-width:100%;object-fit:contain;object-position:left;margin-bottom:22px}.reach .big{font:400 52px/1 'Instrument Serif','Times New Roman',serif;color:var(--acc);margin-top:6px}
.reach .meta{margin-top:8px}.row{font-weight:300;font-size:16px;line-height:22px;margin-top:10px}.reach .big+.row,.reach .meta+.row{margin-top:30px}
.row a:hover,.big a:hover{text-decoration:underline;text-underline-offset:4px}.row .meta{display:inline;margin-left:8px}
.reach .btn{margin-top:34px}
.panel{background:var(--tint);margin-right:calc(-1*var(--m));padding:24px var(--m) 30px 28.8px}
.loc{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:var(--gap);padding:20px 0 24px;border-top:1px solid var(--line)}
.loc:first-child{border-top:0;padding-top:4px}.loc h3{grid-column:1/-1;font-size:30px;line-height:1;margin-bottom:6px}
.loc .tx{margin-top:10px;font-size:14px;line-height:16.8px}.loc .ld .row:first-child{margin-top:10px}
.hrs{border-collapse:collapse;font-weight:300;font-size:16px;line-height:22px;margin-top:10px}.hrs th{font-weight:300;text-align:left;padding:0 22px 0 0}.hrs td{padding:0}
.loc.one .hrs{margin-top:10px}

/* cards: the reference's row of article cards, taken by what the client can prove */
.cards{padding:49.92px 0 49.92px var(--m)}
.cl{display:flex;gap:48px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding-right:var(--m)}.cl::-webkit-scrollbar{display:none}
.cl>li{flex:0 0 263.5px;scroll-snap-align:start}.cl>li>*{display:block}
.ci{display:block;border:1px solid var(--line);margin-bottom:17px}.ci img{width:100%;height:auto}
.cl h3{font-size:26px;line-height:1}.cx{margin-top:8px}.cl .meta{margin-top:8px}
.cl a:hover h3{color:var(--acc)}
.ca{display:flex;justify-content:space-between;padding:30px var(--m) 0 0}.ca[hidden]{display:none}
.cb{width:33px;height:33px;border-radius:50%;border:0;background:var(--deep);color:var(--dk);display:grid;place-items:center;cursor:pointer;padding:0;transition:opacity .35s var(--c)}
.cb .arw{width:17px;height:10px;margin:0}.cb[data-dir="-1"] .arw{transform:scaleX(-1)}.cb:disabled{opacity:.35;cursor:default}

/* the dark band */
.ft{background:var(--deep);color:var(--dk);padding:var(--hh) var(--m) 33.28px}
.ft .wm{color:var(--accd)}
.fb{margin-top:150px;align-items:end;font-weight:300;font-size:10px;line-height:11px;letter-spacing:1px;text-transform:uppercase}
.fc li{margin-bottom:9px}.fc li:last-child{margin:0}.ft a:hover{text-decoration:underline;text-underline-offset:3px}
.tag{font-size:16px;line-height:17.6px;letter-spacing:.6px;margin-top:42px}
.fls{display:flex;gap:var(--gap);justify-content:flex-end;align-items:flex-start}.fls ul{flex:0 1 190px}.fls li{margin-bottom:13px}
.lg{margin-top:44px;max-width:760px;font:300 12px/1.5 Inter,Arial,sans-serif}.lg p+p{margin-top:8px}

@media (max-width:1099px){
 .hd nav{display:none}.hd{padding-top:0;align-items:center}
 .mn{display:block}.mn summary{list-style:none;cursor:pointer;width:44px;height:44px;margin-left:-12px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:6px}
 .mn summary::-webkit-details-marker{display:none}.mn summary i{display:block;width:20px;height:1px;background:currentColor;transition:transform .35s var(--c),opacity .2s}
 .mn[open] summary{position:fixed;left:var(--m);top:10px;z-index:3;color:var(--dk)}
 .mn[open] summary i:nth-child(1){transform:translateY(7px) rotate(45deg)}.mn[open] summary i:nth-child(2){opacity:0}.mn[open] summary i:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
 .mp{position:fixed;inset:0;z-index:2;background:var(--deep);color:var(--dk);padding:104px var(--m) 40px;overflow:auto}
 .mp nav{display:flex;flex-direction:column;gap:32px;font-size:14px;line-height:15.4px;letter-spacing:1.4px;text-transform:uppercase;white-space:normal}
 .mcontact{margin-top:68px;display:flex;flex-direction:column;gap:12px;font-size:14px;line-height:15.4px}
 .hlogo{top:50%;transform:translate(-50%,-50%)}.hlogo img{height:30px;max-width:190px}
}
@media (max-width:999px){
 :root{--m:12px;--gap:12px;--pad:64px;--hh:64px;--wh:34px}
 body{font-size:14px}
 .hero{margin:0;min-height:0;padding-bottom:0}.hero img{height:auto;max-height:none;aspect-ratio:var(--rm)}
 .wm{font-size:min(26px,calc((100vw - 24px)/(var(--n)*.86)));height:18px;padding-top:1px}
 .wm.sm{color:var(--accs)}.ft .wm.sm{color:var(--accds)}.h6 a:hover,.sub a:hover{color:var(--accs)}
 .g12{display:block}.c5{max-width:none}
 .h{font-size:30px}.tx{margin-top:32px}.tx p+p,.si p+p,.si{margin-top:16.8px}.h6{font-size:22px;margin-top:64px}
 .svl.flat{display:block}.svl h3{font-size:30px;margin-bottom:0}.svl>li{margin-bottom:20px}.sd{display:none}
 .sub{font-size:20px;padding-left:24px;margin:10px 0 0}.sub li{margin-bottom:4px}
 .band{aspect-ratio:var(--rm);margin-bottom:32px;max-width:100%}
 .fg{margin-top:48px}.frows{margin-top:24px}.frows>li{gap:14px}.frows h4,.pr{font-size:22px}.pr{white-space:normal}
 .c6.tx{padding:0}.c6.tx+.c6.tx{margin-top:48px}
 .ppl,.ppl.np{grid-template-columns:1fr;row-gap:34px}.pp{gap:25px}.pp img{width:103px;height:135px}.pp .bio{max-width:none}
 .q blockquote{font-size:14px;line-height:18.2px}.q figcaption{margin-top:48px}
 .fl8{bottom:0;height:61px;margin-top:-61px}
 .tb{padding:48px var(--m)}.tb p{font-size:30px}.arw{width:18px;height:11px;margin-top:3px}
 .reach .big{font-size:30px}.panel{margin:40px calc(-1*var(--m)) 0;padding:20px var(--m) 24px}.loc{display:block}
 .cards{padding:48px 0 48px var(--m)}.cl{gap:50px}.cl>li{flex-basis:282px}.cl h3{font-size:22px}
 .ft{padding-top:82px}.fb{margin-top:110px}.fls{justify-content:flex-start;margin-top:34px;flex-wrap:wrap}.fls ul{flex:1 1 150px}.tag{font-size:12px;margin-top:30px}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important;scroll-behavior:auto!important}
 .js .rv{opacity:1;transform:none}.btx i,.q b{opacity:1}}
"""

JS = r"""
(function(){
var R=matchMedia('(prefers-reduced-motion:reduce)').matches,B=document.body,$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
/* letters typed in: measured about 60 ms a letter after a quarter second, once, when the button enters the window */
function type(el){var t=el.querySelector('.btx');if(!t||t.dataset.d)return;t.dataset.d=1;var s=t.textContent;el.setAttribute('aria-label',s);t.textContent='';
 s.split('').forEach(function(ch){var i=document.createElement('i');i.textContent=ch;i.setAttribute('aria-hidden','true');t.appendChild(i)});
 return function(){$('i',t).forEach(function(i,n){setTimeout(function(){i.classList.add('on')},R?0:250+n*60)})}}
var io=('IntersectionObserver' in window)?new IntersectionObserver(function(es){es.forEach(function(x){if(!x.isIntersecting)return;io.unobserve(x.target);
 if(x.target._go)x.target._go();x.target.classList.add('in')})},{rootMargin:'0px 0px -4% 0px'}):null;
$('[data-type]').forEach(function(b){if(R||!io)return;if(b.closest('.fl8')||b.classList.contains('qn'))return;var go=type(b);if(go){b._go=go;io.observe(b)}});
$('.rv').forEach(function(l){if(io&&!R)io.observe(l);else l.classList.add('in')});
/* quotations: one at a time, its words coming up one after another (1.2 s each) */
var qs=$('.q'),qn=document.querySelector('.qn'),qi=0;
function words(q){var bq=q.querySelector('blockquote');if(!bq.dataset.d){bq.dataset.d=1;var s=bq.textContent;bq.setAttribute('aria-label',s);bq.textContent='';
  s.split(/\s+/).forEach(function(w,n){var b=document.createElement('b');b.textContent=w;b.setAttribute('aria-hidden','true');if(n)bq.appendChild(document.createTextNode(' '));bq.appendChild(b)})}
 $('b',bq).forEach(function(b,n){b.classList.remove('on');b.style.transitionDelay=(R?0:n*45)+'ms'});void bq.offsetWidth;$('b',bq).forEach(function(b){b.classList.add('on')})}
if(qs.length){words(qs[0]);if(qn){qn.hidden=false;var g=type(qn);if(g)g();qn.addEventListener('click',function(){qs[qi].classList.remove('on');qi=(qi+1)%qs.length;qs[qi].classList.add('on');words(qs[qi])})}}
/* cards: arrows only when the row is wider than the window; one card a step, 0.3 s */
var cl=document.querySelector('.cl'),ca=document.querySelector('.ca');
if(cl&&ca){var cbs=$('.cb',ca),upd=function(){var over=cl.scrollWidth>cl.clientWidth+4;ca.hidden=!over;cbs[0].disabled=cl.scrollLeft<4;cbs[1].disabled=cl.scrollLeft>cl.scrollWidth-cl.clientWidth-4};
 cbs.forEach(function(b){b.addEventListener('click',function(){var li=cl.children[0],st=li?li.getBoundingClientRect().width+parseFloat(getComputedStyle(cl).columnGap||48):311;cl.scrollBy({left:st*+b.dataset.dir,behavior:R?'auto':'smooth'})})});
 cl.addEventListener('scroll',upd,{passive:true});addEventListener('resize',upd);upd()}
/* the ground changes under the quotations, the header goes light on the dark band, the call appears after the first screen */
var zone=document.querySelector('[data-zone=alt]'),ft=document.getElementById('ft'),fl=document.querySelector('.fl8'),flb=fl&&fl.querySelector('.btn'),flgo=flb&&!R?type(flb):null,tick=0;
function onS(){tick=0;var vh=innerHeight,hh=document.getElementById('hd').offsetHeight;
 if(zone){var r=zone.getBoundingClientRect();B.classList.toggle('alt',r.top<vh*.8&&r.bottom>hh+40)}
 if(ft){B.classList.toggle('deep',ft.getBoundingClientRect().top<=hh)}
 if(fl){var on=scrollY>vh*.6;if(on&&!fl.classList.contains('on')&&flgo){flgo();flgo=null}fl.classList.toggle('on',on)}}
addEventListener('scroll',function(){if(!tick)tick=requestAnimationFrame(onS)},{passive:true});addEventListener('resize',onS);onS();
/* the phone menu closes on a choice and on Escape */
var mn=document.querySelector('.mn');if(mn){mn.addEventListener('click',function(ev){if(ev.target.closest('.mp a'))mn.open=false});addEventListener('keydown',function(ev){if(ev.key==='Escape')mn.open=false})}
})();
"""


def render(d: dict) -> str:
    b, hero = d.get('brand') or {}, d.get('hero') or {}
    lang = (d.get('lang') or 'en')[:2]
    ui = UI.get(lang, {})
    ph = _pick_photos(d)
    cta = d.get('cta') or {}

    acts = ''.join(_btn(c) for c in (hero.get('primary'), hero.get('secondary')) if c)
    extra = ('<div class="acts">%s</div>' % acts if acts else '')
    if hero.get('note'):
        note = e(hero['note'])
        if re.match(r'^[\d\s+()./-]{6,}$', hero['note']):
            note = '<a href="%s">%s</a>' % (e(_tel(hero['note'])), note)
        extra += '<p class="h6">%s</p>' % note
    opening = _block_a(hero.get('title'), hero.get('text'), extra, tag='h1', sid='about')
    st = d.get('statement') or {}
    about = _block_a(st.get('title'), st.get('text'), band=_band(ph.get('about'), 'about'))
    cl = d.get('close') or {}
    close = _block_a(cl.get('title'), cl.get('text'), _btn(cl.get('cta')), sid='close')

    main = ''.join((
        _services(d), opening, _fees(d), _plans(d), about, _steps(d), _details(d),
        _team(d, _band(ph.get('team'), 'team')), _faq(d), close, _quotes(d, ui)))
    floating = '<div class="fl8">%s</div>' % _btn(cta) if cta.get('t') else ''
    name_tag = 'div' if hero.get('title') else 'h1'
    title = ' — '.join(x for x in (b.get('name'), hero.get('title')) if x)
    desc = (hero.get('text') or st.get('text') or '')[:300]

    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="%s"><style>:root{%s}%s</style>'
            '<script>document.documentElement.className="js"</script></head><body>%s'
            '<main id="main"><div class="wrap">%s<div class="wmb">%s</div>%s%s</div>%s%s%s</main>%s'
            '<script>%s</script></body></html>') % (
        e(lang), e(title), e(desc), FONTS, _palette(d.get('palette') or {}), CSS, _head(d, ui),
        _hero_pic(ph.get('hero')), _wordmark(b.get('name'), name_tag), main, floating,
        _tintband(d), _find(d, _band(ph.get('door'), 'door')), _cards(d, ui), _foot(d), JS)
