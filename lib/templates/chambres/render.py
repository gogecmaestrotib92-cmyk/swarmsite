"""chambres — a template for places, rebuilt from chambresdamis.be (measured 2026-11-12 at 1440 and 390).

render(d) -> one self-contained page. Pure: no file reads, no clock, no model. See NOTES.md for the measures.
The build: a two-column page (62.2 % / 37.8 %), photographs bleeding to the page edges in a stepped collage, the name
set as a split wordmark that stays fixed (first part top left, last part bottom right), small sans text in narrow
columns, serif capitals for headings, underlined serif links ending in a guillemet.
"""
from html import escape as _e

# advance widths of Bodoni Moda 500 (opsz 36) capitals per 1000 units, measured in the browser (probe/glyphs.json)
_CW = {"0": 631, "1": 451, "2": 563, "3": 534, "4": 607, "5": 510, "6": 574, "7": 514, "8": 564, "9": 573, "A": 754, "B": 652, "C": 683,
       "D": 719, "E": 599, "F": 578, "G": 727, "H": 755, "I": 380, "J": 456, "K": 706, "L": 585, "M": 848, "N": 741, "O": 737, "P": 634,
       "Q": 737, "R": 712, "S": 566, "T": 660, "U": 708, "V": 753, "W": 1010, "X": 751, "Y": 716, "Z": 570, "Á": 754, "É": 599, "Í": 380,
       "Ó": 737, "Ú": 708, "Ü": 708, "Ñ": 741, "Ç": 683, "À": 754, "È": 599, "Ì": 380, "Ò": 737, "Ù": 708, "Â": 754, "Ê": 599, "Î": 380,
       "Ô": 737, "Û": 708, "Ä": 754, "Ë": 599, "Ï": 380, "Ö": 737, "&": 820, "@": 1010, "'": 216, "’": 231, ".": 216, ",": 232, "-": 360,
       "–": 541, "·": 215, "!": 333, "?": 559, "/": 521, "+": 530, ":": 215, " ": 250}
_LEFT, _RIGHT, _PAD = 62.2, 37.8, 2.5          # the reference's columns and page inset, in vw
_MAXFS = 12.0                                   # the reference's mark: 128 px high drawing at 1440 ≈ 12 vw of type
_WORDS = {'es': ('Menú', 'Cerrar'), 'en': ('Menu', 'Close'), 'fr': ('Menu', 'Fermer'), 'de': ('Menü', 'Schließen'),
          'it': ('Menu', 'Chiudi'), 'pt': ('Menu', 'Fechar'), 'nl': ('Menu', 'Sluiten'), 'sr': ('Meni', 'Zatvori')}


def _rgb(h):
    h = (h or '').lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (255, 255, 255)


def _lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def _con(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _mix(a, b, t):
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


def _hex(c):
    return '#%02x%02x%02x' % tuple(c)


def _veil(ink, ground, want=5.2):
    """least share of the ground colour that, laid over the worst pixel a picture can have, still carries the ink"""
    worst = (0, 0, 0) if _lum(ink) < _lum(ground) else (255, 255, 255)
    for i in range(40, 93):
        if _con(ink, _mix(worst, ground, i / 100)) >= want:
            return i / 100
    return .92


def _quiet(ink, ground):
    """the reference's grey small print, held at 4.6:1 on the ground"""
    for i in range(55, -1, -5):
        c = _mix(ink, ground, i / 100)
        if _con(c, ground) >= 4.6:
            return c
    return ink


def _width(s):
    return sum(_CW.get(ch, 720) - 20 for ch in s.upper()) / 1000


def _mark(name):
    """the name as the reference sets its own: a first part top left inside the left column (one or two lines), the last
    part bottom right inside the right column, both at one size — the largest at which every line fits its column."""
    words = [w for w in (name or '').split() if w]
    if not words:
        return [], '', 6.0
    best = None
    for i in range(1, len(words) + 1):
        p1, p2 = words[:i], words[i:]
        if len(words) > 1 and not p2:
            continue
        for j in [None] + list(range(1, len(p1))):
            l1 = [' '.join(p1)] if j is None else [' '.join(p1[:j]), ' '.join(p1[j:])]
            fits = [(_LEFT - 2 * _PAD) / _width(x) for x in l1]
            if p2:
                fits.append((_RIGHT - 2 * _PAD) / _width(' '.join(p2)))
            fs = min(min(fits) * .97, _MAXFS)
            key = (round(fs, 2), -len(l1))
            if best is None or key > best[0]:
                best = (key, l1, ' '.join(p2), fs)
    return best[1], best[2], best[3]


def _a(link, cls='', extra=''):
    """a link from the data; without an address it is plain text"""
    if not link or not link.get('t'):
        return ''
    c = (' class="%s"' % cls) if cls else ''
    if link.get('h'):
        return '<a%s href="%s"%s>%s</a>' % (c, _e(link['h'], quote=True), extra, _e(link['t']))
    return '<span%s>%s</span>' % (c, _e(link['t']))


def _buttons(links):
    links = [l for l in links if l and l.get('t') and l.get('h')]
    if not links:
        return ''
    return '<ul class="buttons">%s</ul>' % ''.join('<li>%s</li>' % _a(l, 'button rv') for l in links)


def _fig(p, col, slot_ar, cls='', eager=False):
    """one photograph in a column. `col` is the column's width in px at 1440 (896 / 544). The frame keeps the slot's
    proportion unless that would ask for more height than the picture has; a small picture is never wider than its pixels."""
    w, h = p['w'], p['h']
    ar = max(slot_ar, col / h)
    ar = min(ar, max(w / h, slot_ar)) if p.get('small') else ar
    style = 'aspect-ratio:%.4f' % ar
    if p.get('small'):
        style += ';max-width:%dpx' % w
    return ('<figure class="fig rv %s" style="%s"><img src="../../%s" width="%d" height="%d" alt="%s" %s decoding="async"></figure>'
            % (cls, style, _e(p['src'], quote=True), w, h, _e(p.get('alt') or '', quote=True), 'fetchpriority="high"' if eager else 'loading="lazy"'))


def render(d: dict) -> str:
    g = lambda *k: _get(d, *k)
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    lang = (d.get('lang') or 'en')[:2]
    w_menu, w_close = _WORDS.get(lang, _WORDS['en'])
    pal = d.get('palette') or {}
    ground, ink = _rgb(pal.get('ground') or '#f4f1ec'), _rgb(pal.get('ink') or '#1f1e1c')
    if _con(ink, ground) < 7:
        ink = (20, 20, 20) if _lum(ground) > .4 else (245, 245, 245)
    va = _veil(ink, ground)
    quiet = _quiet(ink, ground)
    place = d.get('place') or {}
    hero = d.get('hero') or {}
    nav = [n for n in (d.get('nav') or []) if n.get('t') and n.get('h')]
    cta = d.get('cta') if (d.get('cta') or {}).get('t') else (place.get('booking') or {})
    booking = place.get('booking') if (place.get('booking') or {}).get('h') else cta
    used_h = set()

    # ───────────── photographs: who stands where (see NOTES "Image slots")
    photos = [p for p in (g('media', 'photos') or []) if p.get('src') and p.get('w') and p.get('h')]
    taken = set()

    def big(p):
        return not p.get('small') and min(p['w'], p['h']) >= 700

    def stem(p):   # 'maridaje-copa-2.jpg' and 'maridaje-copa.jpg' are one subject; so are 'pulpo' and 'pulpo-perejil'
        s = p['src'].rsplit('/', 1)[-1].rsplit('.', 1)[0].lower()
        while s and (s[-1].isdigit() or s[-1] in '-_'):
            s = s[:-1]
        return s
    stems = []

    def fresh(p):
        s = stem(p)
        return p['src'] not in taken and not any(s.startswith(t) or t.startswith(s) for t in stems)

    def take(p):
        taken.add(p['src'])
        stems.append(stem(p))
        return p

    def pick(*tests):
        for ok in (fresh, lambda p: p['src'] not in taken):   # the same subject a second time only when nothing else is left
            for t in tests:
                for p in photos:
                    if ok(p) and t(p):
                        return take(p)
        return None

    role = lambda *r: (lambda p: p.get('role') in r)
    fills = lambda p: p['w'] >= 560                       # fills the 544 column at 1440 without being enlarged
    space_src = [s.get('img') for s in (place.get('spaces') or []) if s.get('img')]
    tall = sorted([p for p in photos if big(p)], key=lambda p: (-p['h'], -p['h'] / p['w']))
    place_tall = [p for p in tall if p.get('role') in ('room', 'bar', 'exterior')]
    L = [None, None, None]
    for i, pool in enumerate(((place_tall + tall), ([p for p in tall if p.get('role') != 'dish'] + tall), None)):
        if pool is None:   # the picture above the rooms' text: a room of the client's own list first
            pool = [p for p in tall if p['src'] in space_src] + [p for p in tall if p.get('role') != 'dish'] + tall
        for p in pool:
            if fresh(p):
                L[i] = take(p)
                break
    any_ = lambda p: True
    R = [pick(lambda p: role('dish')(p) and big(p), lambda p: big(p) and p['src'] not in space_src, lambda p: role('dish')(p) and fills(p), big, fills, any_) if photos else None,
         pick(lambda p: role('people', 'other', 'bar')(p) and big(p), big, lambda p: not role('dish')(p) and fills(p), fills, any_),
         pick(lambda p: role('room', 'exterior', 'bar')(p) and fills(p), big, fills, any_),
         pick(lambda p: role('dish')(p) and fills(p), fills, any_)]

    # ───────────── the wordmark
    l1, l2, fs = _mark(name)
    n1 = len(l1) or 1
    top_h = '%.3fvw' % (_PAD + n1 * .86 * fs)                 # where the first part ends
    m2_h = '%.3fvw' % (2 * _PAD + .86 * fs) if l2 else '0px'  # the block the last part stands in
    mark1 = ('<a class="mk mk1" data-m href="#top" aria-label="%s">%s</a>' % (_e(name, quote=True), ''.join('<span>%s</span>' % _e(x) for x in l1))) if l1 else ''
    mark2 = ('<a class="mk mk2" data-m href="#top" aria-hidden="true" tabindex="-1"><span>%s</span></a>' % _e(l2)) if l2 else ''

    # ───────────── navigation: three links beside the toggle, the whole list in the panel
    row = nav[:2] + ([booking] if (booking or {}).get('h') and all(n['h'] != booking['h'] for n in nav[:2]) else nav[2:3])
    full, seen = [], set()
    for n in nav + [l for l in (d.get('links') or []) if l.get('t') and l.get('h')] + ([booking] if (booking or {}).get('h') else []):
        if n['h'] not in seen and n['t'].lower() not in {x['t'].lower() for x in full}:
            seen.add(n['h'])
            full.append(n)
    social = [s for s in (place.get('social') or []) if s.get('t') and s.get('h')]
    navrow = '<nav class="nv" data-m aria-label="%s"><ul>%s</ul></nav>' % (_e(w_menu, quote=True), ''.join('<li>%s</li>' % _a(n) for n in row)) if row else ''
    toggle = ('<button class="tg" type="button" aria-expanded="false" aria-controls="panel" aria-label="%s"><i></i></button>' % _e(w_menu, quote=True)) if full else ''
    panel = ('<aside class="pn" id="panel" aria-label="%s" hidden><ul class="pl">%s</ul>%s</aside>' % (
        _e(w_menu, quote=True), ''.join('<li>%s</li>' % _a(n) for n in full),
        ('<ul class="ps">%s</ul>' % ''.join('<li>%s</li>' % _a(s, '', ' rel="noopener"') for s in social)) if social else '')) if full else ''

    # ───────────── the notice that opens over the first screen: the client's next event
    ev = next((e for e in (place.get('events') or []) if e.get('what')), None)
    popup = ''
    if ev:
        lines = [x for x in (ev.get('when'), ev.get('price'), ev.get('where')) if x]
        popup = ('<div class="pp" id="notice" role="dialog" aria-modal="true" aria-labelledby="nt" hidden><div class="pf">'
                 '<button class="px" type="button" aria-label="%s">×</button><h3 id="nt">%s</h3><div class="pt">%s</div>%s</div></div>'
                 % (_e(w_close, quote=True), _e(ev['what']), ''.join('<p>%s</p>' % _e(x) for x in lines), _buttons([ev.get('cta')]).replace(' rv', '')))

    S = []
    # ───────────── 1 · opening: two photographs, the name over and under them
    if L[0] or R[0]:
        left = _fig(L[0], 896, 3 / 4, 'h0 hl', True).replace(' rv ', ' ') if L[0] else ''
        right = ''
        if R[0]:
            right = _fig(R[0], 544, 3 / 4, 'h0 hr' + (' hfix' if big(R[0]) else ''), True).replace(' rv ', ' ')
        S.append('<section class="sc intro"><div class="left">%s</div><div class="right">%s</div></section>' % (left, right))
    else:
        S.append('<section class="sc intro none" aria-hidden="true"></section>')

    # ───────────── 2 · the line and the booking link
    title = hero.get('title') or ((d.get('statement') or {}).get('title')) or name
    kick = hero.get('kicker') or ''
    lead = hero.get('primary') if (hero.get('primary') or {}).get('h') else booking
    if (lead or {}).get('h'):
        used_h.add(lead['h'])
    S.append('<section class="slogan"><div class="text rv"><h1>%s%s</h1>%s</div></section>'
             % (_e(title), ('<br><em>%s</em>' % _e(kick)) if kick and kick != title else '', _a(lead, 'button')))

    # ───────────── 3 · a pair of photographs, the right one standing on the left one's foot
    if L[1] or R[1]:
        S.append('<section class="sc vibe"><div class="left">%s</div><div class="right">%s</div></section>'
                 % (_fig(L[1], 896, 3 / 4) if L[1] else '', _fig(R[1], 544, 3 / 4) if R[1] else ''))

    # ───────────── 4 · the house in its own words, one narrow column
    st = d.get('statement') or {}
    paras, seen_p = [], {title, kick}
    for x in (hero.get('text'), hero.get('text2'), st.get('text'), hero.get('note')):
        if x and x not in seen_p:
            seen_p.add(x)
            paras.append(x)
    h2a = st.get('title') if st.get('title') and st.get('title') != title else ''
    menu = place.get('menu') or {}
    menu_label = next((n['t'] for n in nav + (d.get('links') or []) if n.get('h') and n.get('h') == menu.get('h')), '')
    b4 = []
    sec = hero.get('secondary') or {}
    if sec.get('h') and sec['h'] not in used_h:
        b4.append(sec)
        used_h.add(sec['h'])
    tk = place.get('takeaway') or {}
    if tk.get('h') and tk['h'] not in used_h:
        b4.append(tk)
        used_h.add(tk['h'])
    has_single = bool(h2a or paras)
    if has_single:
        S.append('<section class="sc one"><div class="single"><div class="text rv">%s%s%s</div></div></section>'
                 % (('<h2>%s</h2>' % _e(h2a)) if h2a else '', ''.join('<p>%s</p>' % _e(x) for x in paras), _buttons(b4)))

    # ───────────── 5–6 · two photographs stepping down the page: right, then left
    if R[2]:
        S.append('<section class="sc imgone%s"><div class="left"></div><div class="right">%s</div></section>' % (' up' if has_single else '', _fig(R[2], 544, 3 / 4)))
    if L[2]:
        S.append('<section class="sc imgtwo%s"><div class="left">%s</div><div class="right"></div></section>' % (' up' if R[2] else '', _fig(L[2], 896, 3 / 4)))

    # ───────────── the menu, set as the reference sets its own (its menu page): italic serif section names, dish and price
    secs = [s for s in (menu.get('sections') or []) if s.get('t')]
    lists = [s for s in (menu.get('lists') or []) if s.get('t')]
    if secs or lists:
        out = []
        head = menu_label or (d.get('features') or {}).get('title') or ''
        if head:
            out.append('<h2>%s</h2>' % _e(head))
        plain = [s for s in secs if not s.get('items')] + lists
        out += ['<p class="ml">%s</p>' % _a({'t': s['t'], 'h': s.get('h')}) for s in plain]
        for s in secs:
            items = [i for i in (s.get('items') or []) if i.get('name')]
            if not items:
                continue
            out.append('<h3><em>%s</em></h3>' % _e(s['t']))
            notes = {i.get('note') or '' for i in items}
            for i in items:
                nm = _a({'t': i['name'], 'h': i.get('h')})
                out.append('<p class="dish">%s%s%s</p>' % (nm, (' <em>%s</em>' % _e(i['price'])) if i.get('price') else '',
                                                             (' <em>%s</em>' % _e(i['note'])) if i.get('note') and len(notes) > 1 else ''))
            if len(notes) == 1 and '' not in notes:
                out.append('<p><em>%s</em></p>' % _e(notes.pop()))
        if menu.get('h') and menu['h'] not in used_h and menu_label:
            out.append(_buttons([{'t': menu_label, 'h': menu['h']}]))
            used_h.add(menu['h'])
        # beside the list, in the right column, the way the reference steps a photograph beside its text: one dish at the
        # head of the list and, when the list is long, a second at its foot
        dish = lambda p: role('dish')(p) and fills(p)
        side = [pick(dish, fills)] + ([pick(dish, fills)] if len(out) > 12 else [])
        side = ''.join(_fig(p, 544, 3 / 4) for p in side if p)
        S.append('<section class="sc one menu" id="menu"><div class="single"><div class="text rv">%s</div></div>%s</section>'
                 % (''.join(out), ('<div class="right mr">%s</div>' % side) if side else ''))

    # ───────────── 7 · a last photograph, wide, in the right column
    if R[3]:
        S.append('<section class="sc imgthree"><div class="left"></div><div class="right">%s</div></section>' % _fig(R[3], 544, 4 / 3))

    # ───────────── 8 · the rooms: a heading across, text in two columns
    steps = d.get('steps') or {}
    items = [i for i in (steps.get('items') or []) if i.get('title')]
    if not items:
        items = [{'title': s.get('title'), 'text': s.get('text')} for s in (place.get('spaces') or []) if s.get('title')]
    if steps.get('title') or items:
        ps = ['<p>%s</p>' % _e(steps['text'])] if steps.get('text') else []
        for i in items:
            k = i.get('k') if i.get('k') and i.get('k') != i.get('title') else ''
            c = i.get('cta') or {}
            if c.get('h'):
                used_h.add(c['h'])
            kk = ''
            if k:
                kk = ' <em>%s</em>' % (_a({'t': k, 'h': c.get('h')}) if c.get('h') else _e(k))
            elif c.get('h') and c.get('t'):
                kk = ' <em>%s</em>' % _a(c)
            ps.append('<p><strong>%s</strong>%s%s</p>' % (_e(i['title']), kk, ('<br>' + _e(i['text'])) if i.get('text') else ''))
        more = [l for l in (d.get('links') or []) if l.get('t') and l.get('h') and l['h'] not in used_h and l['h'] != menu.get('h')][:2]
        if not more and ((d.get('close') or {}).get('cta') or {}).get('h'):
            more = [d['close']['cta']]
        for l in more:
            used_h.add(l['h'])
        S.append('<section class="sc two%s"><div class="left"><div class="double"><div class="text rv">%s%s%s</div></div></div></section>'
                 % (' up' if R[3] else '', ('<h2>%s</h2>' % _e(steps['title'])) if steps.get('title') else '', ''.join(ps), _buttons(more)))

    # ───────────── prices and questions, when the client has them: the same two-column text, and the reference's own accordion
    plans = d.get('plans') or {}
    pl = [p for p in (plans.get('items') or []) if p.get('name')]
    if pl:
        ps = ['<p>%s</p>' % _e(plans['text'])] if plans.get('text') else []
        for p in pl:
            price = ' '.join(x for x in (p.get('price'), p.get('per')) if x)
            rows = ''.join('<br>' + _e(r) for r in (p.get('rows') or []) if r)
            ps.append('<p><strong>%s</strong>%s%s%s</p>%s' % (_e(p['name']), (' <em>%s</em>' % _e(price)) if price else '',
                                                             ('<br>' + _e(p['line'])) if p.get('line') else '', rows, _buttons([p.get('cta')])))
        if plans.get('note'):
            ps.append('<p><em>%s</em></p>' % _e(plans['note']))
        S.append('<section class="sc two"><div class="left"><div class="double"><div class="text rv">%s%s</div></div></div></section>'
                 % (('<h2>%s</h2>' % _e(plans['title'])) if plans.get('title') else '', ''.join(ps)))
    faq = d.get('faq') or {}
    qs = [q for q in (faq.get('items') or []) if q.get('q') and q.get('a')]
    if qs:
        S.append('<section class="faq"><div class="text rv">%s%s</div></section>' % (
            ('<h2>%s</h2>' % _e(faq['title'])) if faq.get('title') else '',
            ''.join('<details><summary>%s</summary><div class="ans"><p>%s</p></div></details>' % (_e(q['q']), _e(q['a'])) for q in qs)))

    # ───────────── notices the law asks for, above the foot
    for n in (place.get('notices') or []):
        img = ''
        if n.get('img') and n.get('w') and n.get('h'):
            img = '<img class="ni" src="../../%s" width="%d" height="%d" alt="" loading="lazy" style="max-width:min(100%%,%dpx)">' % (_e(n['img'], quote=True), n['w'], n['h'], min(n['w'], 270))
        txt = ''.join('<p>%s</p>' % _e(t) for t in (n.get('text') or []) if t)
        if img or txt:
            S.append('<section class="sc two notice"><div class="left"><div class="double"><div class="text rv">%s%s</div></div></div></section>' % (img, txt))

    # ───────────── foot: one screen high, three small columns on its floor, the name standing over it
    ad = place.get('address') or {}
    ph = place.get('phone') or {}
    c1 = []
    if name:
        c1.append(_e(name))
    if ad.get('street'):
        c1.append('<em>%s</em>' % _e(ad['street']))
    town = ' '.join(x for x in (ad.get('postcode'), ad.get('city')) if x)
    if town:
        c1.append(_e(town))
    if ph.get('t'):
        c1.append(_a(ph) + ((' ' + _e(ph['note'])) if ph.get('note') and ph.get('h') else ''))
    if place.get('email'):
        c1.append('<a href="mailto:%s">%s</a>' % (_e(place['email'], quote=True), _e(place['email'])))
    foot = d.get('foot') or {}
    if not (ad or ph) and foot.get('text'):
        c1.append(_e(foot['text']))
    flinks = [l for l in (foot.get('links') or []) if l.get('t') and l.get('h') and l['h'] not in {s['h'] for s in social}]
    c2 = ''
    if social:
        c2 += '<ul>%s</ul>' % ''.join('<li>%s</li>' % _a(s, '', ' rel="noopener"') for s in social)
    if flinks:
        c2 += '<ul>%s</ul>' % ''.join('<li>%s</li>' % _a(l) for l in flinks)
    c3 = ''.join('<p>%s<br>%s</p>' % (_e(h.get('days') or ''), _e('–'.join(x for x in (h.get('open'), h.get('close')) if x)))
                 for h in (place.get('hours') or []) if h.get('days') or h.get('open'))
    if (booking or {}).get('h'):
        c3 += '<p>%s</p>' % _a(booking)
    if foot.get('legal'):
        c3 += '<p class="legal">%s</p>' % _e(foot['legal'])
    footer = ('<footer class="ft"><div class="fl"><div class="fc contact" data-o>%s</div><div class="fc soc" data-o>%s</div><div class="fc hours" data-o>%s</div></div></footer>'
              % ('<br>'.join(c1), c2, c3))

    G, I, Q = _hex(ground), _hex(ink), _hex(quiet)
    gr = '%d,%d,%d' % ground
    css = _CSS.replace('__G__', G).replace('__I__', I).replace('__Q__', Q).replace('__GR__', gr).replace('__VA__', '%.2f' % va) \
        .replace('__FS__', '%.3fvw' % fs).replace('__TOP__', top_h).replace('__M2__', m2_h).replace('__PA__', '%.2f' % min(.92, va + .12))
    desc = hero.get('text') or st.get('text') or ''
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title>%s<script>document.documentElement.className="js"</script>'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Arimo:ital,wght@0,400;0,500;1,400&family=Bodoni+Moda:opsz,wght@6..96,500&family=Old+Standard+TT:ital,wght@0,400;1,400&display=swap" rel="stylesheet">'
            '<style>%s</style></head><body id="top"><header>%s%s%s%s%s</header><main>%s</main>%s%s<script>%s</script></body></html>'
            % (_e(lang, quote=True), _e(name), ('<meta name="description" content="%s">' % _e(desc, quote=True)) if desc else '',
               css, mark1, navrow, toggle, panel, mark2, ''.join(S), footer, popup, _JS))


def _get(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


_CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:__G__;color:__I__;font:400 14px/1.5 Arimo,"Helvetica Neue",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
:root{--g:__G__;--i:__I__;--fs:__FS__;--top:__TOP__;--m2:__M2__;--L:62.2%;--R:37.8%}
a{color:inherit;text-underline-offset:.1rem;text-decoration-thickness:1px;transition:text-underline-offset .6s,text-decoration-color .6s}
a:hover{text-underline-offset:.3rem}
:focus-visible{outline:2px solid __I__;outline-offset:3px;border-radius:1px}
strong{font-weight:500}
figure{margin:0}
h1,h2,h3{font-family:"Old Standard TT","Old Standard",Georgia,serif;font-weight:400;margin:.83em 0}
h1,h2{font-size:34px;line-height:1.3;letter-spacing:-.05em;text-transform:uppercase}
h1{margin:.67em 0}
h1 em{font-style:italic}
p{margin:14px 0;min-height:10px}

/* the name, fixed: first part top left, last part bottom right */
.mk{position:fixed;z-index:1;display:block;font:500 var(--fs)/.86 "Bodoni Moda","Old Standard TT",Didot,serif;font-variation-settings:"opsz" 36;letter-spacing:-.02em;text-transform:uppercase;white-space:nowrap;text-decoration:none;color:__I__;transition:opacity .6s,visibility 0s}
.mk span{display:block}
.mk1{top:0;left:0;padding:2.5vw 2.5vw 0}
.mk2{bottom:0;right:0;padding:2.5vw;text-align:right}
.nv{position:fixed;z-index:1;top:var(--top);left:0;width:62.2vw;padding:1.5vw calc(2.5vw + 33px) 0 2.5vw;display:flex;justify-content:flex-end;transition:opacity .6s,visibility 0s}
.nv ul{list-style:none;margin:0;padding:0;display:flex}
.nv li{margin-right:30px}
.nv a{text-transform:uppercase;text-decoration:underline 0 transparent;text-underline-offset:.1rem}
.nv a:hover{text-underline-offset:.3rem;text-decoration-thickness:1px;text-decoration-color:__I__}
.hid{opacity:0;visibility:hidden;transition:opacity .6s,visibility 0s .6s}
.tg{position:fixed;z-index:6;top:calc(var(--top) + 1.5vw + 4px);left:calc(62.2vw - 2.5vw - 33px);width:33px;height:13px;padding:0;border:0;background:none;cursor:pointer}
/* three hairlines in the ink, each with a hairline of the ground round it, so the button is seen on any photograph that passes under it */
.tg::before,.tg::after,.tg i{content:"";position:absolute;left:0;right:0;height:1px;background:__I__;box-shadow:0 0 0 1px rgba(__GR__,.85);transition:.6s}
.tg::before{top:0}.tg i{top:6px}.tg::after{bottom:0}
.tg[aria-expanded=true]::before{transform:rotate(25deg);top:6px}
.tg[aria-expanded=true] i{opacity:0}
.tg[aria-expanded=true]::after{transform:rotate(-25deg);bottom:6px}
.tg:focus-visible{outline:2px solid __I__;outline-offset:8px;box-shadow:0 0 0 8px rgba(__GR__,.85)}
.pn{position:fixed;z-index:5;inset:0 0 0 62.2vw;padding:2.5vw;display:flex;flex-direction:column;overflow-y:auto;background:rgba(__GR__,0);-webkit-backdrop-filter:blur(0);backdrop-filter:blur(0);opacity:0;pointer-events:none;transition:.6s}
.pn[hidden]{display:none}
.pn.open{opacity:1;pointer-events:all;background:rgba(__GR__,__PA__);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px)}
.pn ul{list-style:none;margin:0;padding:0}
.pl{padding-top:14px!important}
.pl li{padding-bottom:20px}
.pl a{font:400 30px/1.3 "Old Standard TT",Georgia,serif;letter-spacing:-.05em;text-transform:uppercase;text-decoration:underline 0 transparent}
.pl a:hover{text-underline-offset:.5rem;text-decoration-thickness:1px;text-decoration-color:__I__}
.ps{margin:auto 0 30px!important;padding-top:40px!important}
.ps li{margin:10px 0}
.ps a{text-transform:uppercase}

/* sections: the reference's two columns */
.sc{display:grid;grid-template-columns:var(--L) var(--R)}
.sc>div{min-width:0}
.fig{position:relative;z-index:2;width:100%;overflow:hidden;background:rgba(__GR__,1)}
.fig img{display:block;width:100%;height:100%;object-fit:cover}
.right .fig{margin-left:auto}
.h0{z-index:0}
.intro.none{min-height:calc(var(--top) + 6vw)}
.intro .hl{min-height:100vh;min-height:100dvh;max-height:150vh;max-height:150dvh}
.intro .hfix{height:calc(100vh - var(--m2));height:calc(100dvh - var(--m2));aspect-ratio:auto!important}
/* the veil that lets the name and the links be read on any photograph: it stays with them (fixed), and is seen only on the opening pictures */
.hl::after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(to bottom,rgba(__GR__,__VA__) 0,rgba(__GR__,__VA__) calc(var(--top) + 1.5vw + 30px),rgba(__GR__,0) calc(var(--top) + 1.5vw + 30px + 9vw)) fixed}
.text{position:relative;z-index:2;background:__G__}
.slogan{min-height:80vh;min-height:80dvh;display:flex;flex-direction:column;justify-content:flex-end;padding:2.5% 2.5% 5%}
.slogan .text{padding-top:1px;align-self:flex-start;max-width:calc(62.2vw - 5vw)}
.slogan h1{text-wrap:balance}
.vibe .right{margin-top:auto}
.one{margin-top:20vh;margin-top:20dvh}
.single{grid-column:1;width:50%;margin-left:auto}
.single .text{padding-right:22.5%}
.single .text>:first-child{margin-top:0}
.imgone.up .right{margin-top:-30%}
.imgtwo.up .left{margin-top:-20%}
.two.up{margin-top:-7%}
.double{padding:4%}
.double .text{padding-right:12.5%;columns:2;column-gap:5%}
.double .text h2{column-span:all}
.double .text p{break-inside:avoid}
.double .text h2+p,.double .text>p:first-child{margin-top:0}
.button{font:400 20px/1.05 "Old Standard TT",Georgia,serif;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.8rem;transition:.3s;padding-bottom:0}
.button::after{content:" »"}
.button:hover{text-underline-offset:.6rem;padding-bottom:.02rem}
.buttons{list-style:none;padding:0;margin:0;break-inside:avoid}
.buttons li{margin:20px 0 0;line-height:250%}
.slogan .button{display:inline-block;padding-bottom:.8rem}
.mr{display:flex;flex-direction:column;justify-content:space-between;gap:40px}
.menu h3{font-size:28px;line-height:1.3;margin:90px 0 28px}
.menu h3 em{font-style:italic}
.menu h2+h3{margin-top:40px}
.menu .ml a,.menu .dish a{text-decoration:underline 0 transparent}
.menu .ml a:hover,.menu .dish a:hover{text-decoration-thickness:1px;text-decoration-color:__I__}
.menu .dish em{white-space:nowrap}
.faq{padding:4% 2.5%;width:62.2%}
.faq .text>h2{margin-top:0}
.faq summary{font:italic 400 24px/1.2 "Old Standard TT",Georgia,serif;padding:20px 0;cursor:pointer;list-style:none}
.faq summary::-webkit-details-marker{display:none}
.faq .ans{max-width:600px;padding-bottom:14px}
.notice .ni{display:block;height:auto;margin:0 0 20px}
.notice{margin-top:10vh}

/* foot */
.ft{position:relative;padding:2.5%}
.fl{width:62.2%;min-height:calc(100vh - 5vw);min-height:calc(100dvh - 5vw);display:grid;grid-template-columns:repeat(3,1fr);gap:2.5%;align-items:end;padding-right:2.5%}
.fc{position:relative;z-index:2}
.contact{text-transform:uppercase}
.contact a{text-decoration-color:transparent}
.contact a:hover{text-decoration-color:__I__}
.soc{text-transform:uppercase}
.soc ul{list-style:none;margin:0;padding:0 0 20px}
.soc ul:last-child{padding-bottom:0}
.soc li{margin:6px 0}
.hours p{margin:0 0 14px}
.hours p:last-child{margin-bottom:0}
.legal{font-size:10px;letter-spacing:.03em;text-transform:uppercase;color:__Q__;margin-top:12px!important}

/* the notice over the first screen */
.pp{position:fixed;inset:0;z-index:9;display:flex;overflow-y:auto;transition:.6s}
.pp[hidden]{display:none}
.pp.closing{opacity:0;filter:blur(20px);pointer-events:none}
.pf{position:relative;margin:auto;width:100%;max-width:672px;padding:36px;display:flex;flex-direction:column;background:rgba(__GR__,__PA__);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px);box-shadow:0 0 20px rgba(31,30,28,.2);border-radius:3px}
.px{position:absolute;top:10px;right:10px;width:24px;height:24px;padding:0;border:0;background:none;color:__I__;font-size:20px;line-height:20px;cursor:pointer}
.pf h3{font-size:28px;line-height:1.3;letter-spacing:-.05em;text-transform:uppercase;margin:0 0 80px;padding-right:24px}
.pt{max-width:400px}
.pf .buttons{margin-top:40px;margin-left:auto}

/* arrival: 28 px up out of a 5 px blur, one second */
.js .rv{opacity:0;filter:blur(5px);transform:translateY(28px);transition:opacity 1s,filter 1s,transform 1s}
.js .rv.in{opacity:1;filter:blur(0);transform:none}
.js a.button.rv{transition:opacity 1s,filter 1s,transform 1s,text-underline-offset .3s}

@media (max-width:1300px){.single{width:100%;padding:4%}.single .text{padding:0;max-width:500px}.double .text{padding-right:0}}
@media (max-width:1000px){.double .text{columns:1;max-width:500px}.fl{display:flex;flex-direction:column;align-items:normal;gap:20px}.fl .contact{margin-top:auto}}
@media (max-width:800px){
 h1,h2{font-size:24px}
 .sc{display:block}
 .nv{display:none}
 .tg{left:auto;right:2.5vw;top:calc(2.5vw + (var(--top) - 2.5vw - 13px)/2)}
 .pn{inset:0;padding:2.5vw;padding-top:calc(var(--top) + 4vw)}
 .pl{padding-top:0!important}
 .right .fig{margin-left:0}
 .intro .hl{min-height:100vh;max-height:none}
 .intro .hfix{height:auto;aspect-ratio:3/4!important}
 .h0::after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(to bottom,rgba(__GR__,__VA__) 0,rgba(__GR__,__VA__) calc(var(--top) + 2.5vw),rgba(__GR__,0) calc(var(--top) + 16vw),rgba(__GR__,0) calc(100vh - var(--m2) - 14vw),rgba(__GR__,__VA__) calc(100vh - var(--m2)),rgba(__GR__,__VA__) 100vh) fixed}
 .slogan{min-height:60vh;padding:2.5% 2.5% 10%}
 .slogan .text{max-width:none}
 .one{margin-top:20vh}
 .single,.double{padding:2.5% 2.5% 10%}
 .imgone.up .right,.imgtwo.up .left{margin-top:0}
 .two.up,.two{margin-top:20vh}
 .faq{width:auto;padding:2.5% 2.5% 10%}
 .ft{padding-bottom:max(100px,calc(var(--m2) + 30px))}
 .fl{width:auto;padding-right:0;min-height:calc(100vh - 100px)}
 .pf{padding:50px 30px;margin:auto 2.5vw}
 .pf h3{font-size:24px}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}.js .rv{opacity:1;filter:none;transform:none}}
"""

_JS = r"""(function(){
var D=document,R=D.documentElement,q=function(s){return [].slice.call(D.querySelectorAll(s))};
/* arrival */
var rv=q('.rv');
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -6% 0px'});rv.forEach(function(e){io.observe(e)})}
else rv.forEach(function(e){e.classList.add('in')});
/* the fixed name and links step back while a photograph or a block of text is under them, and return on the bare ground */
var fx=q('[data-m]'),ob=q('.fig:not(.h0),.text,[data-o]'),tick=0;
function upd(){tick=0;var rs=ob.map(function(e){return e.getBoundingClientRect()}).filter(function(r){return r.bottom>0&&r.top<innerHeight&&r.width>0});
 fx.forEach(function(m){var a=(m.querySelector('ul')||m).getBoundingClientRect(),p=m.classList.contains('mk')?parseFloat(getComputedStyle(m).paddingLeft)||0:0;
  var x0=a.left+p,x1=a.right-p,y0=a.top+(m.classList.contains('mk1')?p:0),y1=a.bottom-(m.classList.contains('mk2')?p:0);
  var hit=rs.some(function(r){return r.left<x1&&r.right>x0&&r.top<y1+6&&r.bottom>y0-6});m.classList.toggle('hid',hit)})}
function ask(){if(!tick)tick=requestAnimationFrame(upd)}
addEventListener('scroll',ask,{passive:true});addEventListener('resize',ask);addEventListener('load',ask);upd();
/* panel */
var tg=D.querySelector('.tg'),pn=D.getElementById('panel');
function panel(o){if(!pn)return;if(o){pn.hidden=false;pn.offsetWidth}pn.classList.toggle('open',o);tg.setAttribute('aria-expanded',o?'true':'false');R.classList.toggle('menu',o);
 if(!o)setTimeout(function(){if(!pn.classList.contains('open'))pn.hidden=true},620)}
if(tg){tg.addEventListener('click',function(){panel(tg.getAttribute('aria-expanded')!=='true')});pn.addEventListener('click',function(e){if(e.target.closest('a'))panel(false)})}
/* notice */
var pp=D.getElementById('notice'),seen=0;try{seen=sessionStorage.getItem('notice')}catch(e){}
function shut(){if(!pp||pp.hidden)return;pp.classList.add('closing');try{sessionStorage.setItem('notice','1')}catch(e){}setTimeout(function(){pp.hidden=true},620)}
if(pp&&!seen){pp.hidden=false;pp.querySelector('.px').addEventListener('click',shut);pp.addEventListener('click',function(e){if(e.target===pp)shut()})}
addEventListener('keydown',function(e){if(e.key==='Escape'){if(pp&&!pp.hidden)shut();else if(tg&&tg.getAttribute('aria-expanded')==='true'){panel(false);tg.focus()}}});
})();"""
