"""tengile/render.py — one pure function: render(d) -> a complete page. A template for PLACES.

The build (section order, 12-column grid, measures, type scale, spacing, motion, phone build) was measured on the
reference's home page at 1440 and 390 on 2026-11-12 (see NOTES.md). Nothing of the reference's code, words, pictures,
ornament, logo or typefaces is here. The client's data fills it; a section whose data is missing is left out whole.
No model call, no file reads, no client logic.
"""
import html
import math
import re

FONTS = ('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,200..400'
         '&family=Inter:wght@400;500&display=swap')
BACKDROP_ROLES = ('exterior', 'room', 'bar', 'people', 'other')
PLACE_ROLES = ('exterior', 'room', 'bar')


# ───────────────────────── colour: the reference's relations (ground / ink / accent text / deep slab / pills)
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


def _toward(col, pole, against, want):
    """col moved toward pole (black or white) until it reads `want`:1 against `against`."""
    t = 0.0
    while t < 1 and _con(_mix(pole, col, t), against) < want:
        t += .02
    return _mix(pole, col, min(t, 1))


def _theme(p):
    g, ink, acc = p.get('ground') or '#ffffff', p.get('ink') or '#111111', p.get('accent') or p.get('ink') or '#111111'
    light_page = _lum(g) >= _lum(ink)
    lite, dark = (g, ink) if light_page else (ink, g)
    v = {
        'g': g, 'ink': ink, 'lite': lite, 'dark': dark,
        # the reference's large green paragraphs: accent as text, held at 4.5:1 on the ground
        'acct': _toward(acc, '#000000' if light_page else '#ffffff', g, 4.6),
        # its footer slab: the accent as a ground that carries the light ink at 5.5:1 (reference: 5.6:1)
        'deep': _toward(acc, '#000000', lite, 5.5),
        'pill': _mix(ink, g, .10),          # the quiet pill and the ground under a picture that has not loaded
        'pillon': _mix('#ffffff', lite, .5) if light_page else lite,   # the pill on pictures and on the slab
        'mute': _toward(_mix(ink, g, .45), ink, g, 4.6),
        # the slab's second text tone: the light ink 15 % toward the slab, then moved back toward the light ink until it
        # still reads 4.6:1 on the slab (a 15 % mix alone fell to 4.48:1 on an orange slab)
        'sub': _toward(_mix(lite, _toward(acc, '#000000', lite, 5.5), .85), lite, _toward(acc, '#000000', lite, 5.5), 4.6),
        'veil': '%d,%d,%d' % _rgb(_mix('#000000', dark, .5)),
    }
    return ';'.join('--%s:%s' % kv for kv in v.items())


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def _src(s):
    return e(s if str(s).startswith(('http:', 'https:', 'data:', '/')) else '../../' + str(s))


ARROW = ('<svg viewBox="0 0 30 30" width="30" height="30" aria-hidden="true"><path d="M9.5 15h11m-4-4 4 4-4 4" fill="none" '
         'stroke="currentColor" stroke-width="1"/></svg>')
WORDS = {'es': ('Menú', 'Cerrar', 'Anterior', 'Siguiente'), 'en': ('Menu', 'Close', 'Previous', 'Next'),
         'fr': ('Menu', 'Fermer', 'Précédent', 'Suivant'), 'de': ('Menü', 'Schließen', 'Zurück', 'Weiter'),
         'it': ('Menu', 'Chiudi', 'Precedente', 'Successivo'), 'pt': ('Menu', 'Fechar', 'Anterior', 'Seguinte')}


def pill(link, tone=''):
    if not link or not link.get('t') or not link.get('h'):
        return ''
    return '<a class="pill %s" href="%s"><span class="pl">%s</span><span class="pi">%s</span></a>' % (tone, e(link['h']), e(link['t']), ARROW)


def media(p, cls='', ratio=None, px=True, eager=False, style=''):
    """A picture in its clipping frame. `ratio` is the frame's (w, h); the picture covers it and drifts inside (data-px)."""
    w, h = ratio or (p.get('w') or 4, p.get('h') or 3)
    if p.get('w') and p.get('h') and 'max-width' not in style:   # a frame is never larger than its picture's own pixels
        style = 'max-width:%dpx;%s' % (min(p['w'], p['h'] * w / h), style)
    return ('<div class="m %s" style="aspect-ratio:%s/%s;%s"><img%s src="%s" alt="%s" width="%s" height="%s"%s decoding="async"></div>'
            % (cls, w, h, style, ' data-px' if px else '', _src(p['src']), e(p.get('alt', '')), p.get('w') or '', p.get('h') or '',
               '' if eager else ' loading="lazy"'))


def _split(words, k):
    """words into k consecutive lines, the longest line as short as possible."""
    k = max(1, min(k, len(words)))
    best = None

    def rec(i, left, cur):
        nonlocal best
        if left == 1:
            lines = cur + [words[i:]]
            m = max(len(' '.join(x)) for x in lines)
            if best is None or m < best[0]:
                best = (m, lines)
            return
        for j in range(i + 1, len(words) - left + 2):
            rec(j, left - 1, cur + [words[i:j]])
    rec(0, k, [])
    return best[1]


def _title(text):
    """The opening title: upper case, set in lines; first line from the left inset, last line to the right inset.
    Every letter rises out of its word's clip. On a phone each line may break again (≤ 12 letters)."""
    words = str(text).split()
    n = len(' '.join(words))
    lines = _split(words, 2 if n <= 24 else 3 if n <= 60 else 4)
    out, dmax, mmax = [], 1, 1
    for line in lines:
        dmax = max(dmax, len(' '.join(line)))
        subs, cur = [], []
        for w in line:
            if cur and len(' '.join(cur + [w])) > 12:
                subs.append(cur)
                cur = []
            cur.append(w)
        subs.append(cur)
        sub_html = []
        for sub in subs:
            mmax = max(mmax, len(' '.join(sub)))
            ws = []
            for w in sub:
                ws.append('<span class="w">%s</span>' % ''.join(
                    '<span class="c" style="--i:%d">%s</span>' % (min(i, 8), e(ch)) for i, ch in enumerate(w)))
            sub_html.append('<span class="l">%s</span>' % ' '.join(ws))
        out.append('<span class="L">%s</span>' % ' '.join(sub_html))
    cw = .74                                     # mean advance of a capital in the display face, in em (measured on the build)
    fd = min(8.333, 81.0 / (cw * dmax))          # 120 px at 1440; the line must fit between the insets
    fm = min(12.5, 90.0 / (cw * mmax))           # 48.75 px at 390
    return ('<h1 class="ht" aria-label="%s" style="--fd:%.3fvw;--fm:%.3fvw"><span aria-hidden="true">%s</span></h1>'
            % (e(text), fd, fm, ''.join(out)))


# ───────────────────────── pictures: who gets which (no picture is shown twice)
def _by_page(photos, href, taken, dish_first=False):
    """The photograph the client's own site shows on the page a card links to (`photos[].page` == the link): the data's
    only statement of which picture belongs to which room or menu section. First view before a second, large before small."""
    if not href:
        return None
    c = [p for p in photos if p.get('page') and p['page'].rstrip('/') == href.rstrip('/') and p.get('src') not in taken and p.get('w') and p.get('h')]
    c.sort(key=lambda p: ((p.get('role') == 'dish') != dish_first, bool(re.search(r'-\d+\.\w+$', p['src'])), bool(p.get('small')), -(p['w'] * p['h'])))
    return c[0] if c else None


def _allocate(d, spaces, only_hero=False, hero_src=None):
    """Chooses a photograph for each slot by role, size and proportion. Each picture is used once; a second view of the
    same subject (file name ending -2, -3) is taken only when nothing else is left; most of a large set is never shown."""
    photos = [p for p in (d.get('media') or {}).get('photos') or [] if p.get('src') and p.get('w') and p.get('h')]
    taken = {s.get('img') for s in spaces if s.get('img')}
    free = [p for p in photos if p['src'] not in taken]
    h, pl = d.get('hero') or {}, d.get('place') or {}
    big = lambda p: not p.get('small')
    wide = lambda p: p['w'] >= p['h']
    dish = lambda p: p.get('role') == 'dish'
    area = lambda p: p['w'] * p['h']
    order = lambda p: PLACE_ROLES.index(p.get('role')) if p.get('role') in PLACE_ROLES else len(PLACE_ROLES)
    cover_of = lambda p, w, hh: min(p['w'], w) * min(p['h'], hh) / float(w * hh)       # share of a w x h frame it fills at its own size
    stem = lambda p: p['src'].rsplit('/', 1)[-1].rsplit('.', 1)[0]
    subject = lambda p: re.sub(r'-\d+$', '', stem(p))
    a = {'hero': None, 'cover': None, 'double': [], 'gallery': [], 'story': [], 'marquee': [], 'cloud': []}

    def take(pred, n=1, key=None, spread=False):
        c = [p for p in free if pred(p)]
        c.sort(key=lambda p: (any(subject(p) == subject(q) and q is not p for q in used), key(p) if key else 0, subject(p) != stem(p)))
        one = []
        for p in c:                     # one view of each subject
            if not any(subject(p) == subject(q) for q in one):
                one.append(p)
        if spread and len(one) > n:     # from a long set, evenly through it rather than its first n (not five desserts in a row)
            lead = [p for p in one if (key(p) if key else 0) == (key(one[0]) if key else 0) and not any(subject(p) == subject(q) for q in used)]
            if len(lead) > n:
                one = [lead[int(i * len(lead) / float(n))] for i in range(n)]
        out = one[:n]
        for p in out:
            free.remove(p)
            used.append(p)
        return out
    used = [p for p in photos if p['src'] in taken]
    if hero_src:
        free[:] = [p for p in free if p['src'] != hero_src]
        used += [p for p in photos if p['src'] == hero_src]
    # the opening backdrop: the place itself (outside, room, bar) that fills most of a 1440x900 screen at its own size
    hero = take(lambda p: big(p) and not dish(p), 1, key=lambda p: (order(p) >= len(PLACE_ROLES), -round(cover_of(p, 1440, 900) * 10), order(p), -area(p)))
    if not hero:    # only dishes, or every large picture belongs to a space
        hero = take(big, 1, key=lambda p: -area(p)) or sorted([p for p in photos if big(p)], key=lambda p: (dish(p), -area(p)))[:1]
    a['hero'] = hero[0] if hero else None
    if hero_src:
        if hero and hero[0]['src'] != hero_src:
            free.append(hero[0])
            used.remove(hero[0])
        a['hero'] = next((p for p in photos if p['src'] == hero_src), None)
    if only_hero:
        return a
    # the closing cover: a wide picture of the place or its people, at least 700 high
    c = take(lambda p: big(p) and wide(p) and not dish(p) and p['h'] >= 700, 1, key=lambda p: (order(p) >= len(PLACE_ROLES) and p.get('role') != 'people', -cover_of(p, 1440, 1270)))
    a['cover'] = c[0] if c else None
    # the pair after the heading: the two large pictures that best fill 696x840 and 577x735
    a['double'] = take(big, 2, key=lambda p: -cover_of(p, 696, 840))
    # the large gallery: wide pictures of the place, at least two
    if len([p for p in free if big(p) and wide(p) and not dish(p)]) >= 2:
        a['gallery'] = take(lambda p: big(p) and wide(p) and not dish(p), 6, key=lambda p: -area(p))
    # the event's two pictures (340 wide: small ones are welcome), rooms before dishes, the taller first
    if [x for x in pl.get('events') or [] if x.get('what')] and len([p for p in free if p['w'] >= 340 and p['h'] >= 340]) >= 2:
        a['story'] = take(lambda p: p['w'] >= 340 and p['h'] >= 340, 2, key=lambda p: (dish(p), -p['h']))
    # the moving strip (464 wide each): dishes and details first, at most eight
    if len([p for p in free if p['w'] >= 464]) >= 4:
        a['marquee'] = take(lambda p: p['w'] >= 464, 8, key=lambda p: (not dish(p), order(p)), spread=True)
    # the six small pictures round the centred block
    if (h.get('text2') or (h.get('secondary') or {}).get('h')) and len(free) >= 4:
        a['cloud'] = take(lambda p: p['w'] >= 180 and p['h'] >= 200, 6, key=lambda p: (not dish(p), order(p)), spread=True)
    return a


# ───────────────────────── sections
def _header(d, words):
    b = d.get('brand') or {}
    logo = ('<img class="logo" src="%s" alt="%s">' % (_src(b['logo']), e(b.get('name', ''))) if b.get('logo')
            else '<span class="wm">%s</span>' % e(b.get('name', '')))
    cta = d.get('cta') or (d.get('place') or {}).get('booking') or {}
    right = '<a class="hl" href="%s">%s</a>' % (e(cta['h']), e(cta['t'])) if cta.get('t') and cta.get('h') else '<span></span>'
    has_menu = bool(d.get('nav') or d.get('links'))
    left = ('<button class="hl mb" type="button" aria-expanded="false" aria-controls="menu" aria-label="%s"><i></i><i></i></button>'
            % e(words[0]) if has_menu else '<span></span>')
    return '<header class="hd" id="hd">%s<a class="brand" href="%s">%s</a>%s</header>' % (left, e(b.get('home') or '#'), logo, right)


def _menu(d, spaces, words):
    nav = [n for n in d.get('nav') or [] if n.get('t') and n.get('h')]
    seen = {n['h'] for n in nav}
    more = [l for l in d.get('links') or [] if l.get('t') and l.get('h') and l['h'] not in seen]
    if not nav and not more:
        return ''
    prim = ''.join('<li><a href="%s">%s</a></li>' % (e(n['h']), e(n['t'])) for n in nav)
    sec = ''.join('<li><a href="%s">%s</a></li>' % (e(l['h']), e(l['t'])) for l in more)
    cards = [s for s in spaces if s.get('img')]
    side = ''
    if cards:
        side = '<div class="mn-side">%s</div>' % ''.join(
            '<div class="mn-card">%s<p class="h3">%s</p></div>' % (
                media({'src': s['img'], 'alt': s.get('title', ''), 'w': s.get('_w'), 'h': s.get('_h')}, ratio=(s.get('_w') or 4, s.get('_h') or 3)
                      if s.get('_small') else (339, 413), px=False, style='max-width:%spx' % s['_w'] if s.get('_small') else ''),
                e(s.get('title', ''))) for s in cards)
    return ('<div class="mn" id="menu" aria-hidden="true"><div class="mn-bd" data-close></div>'
            '<div class="mn-panel%s" role="dialog" aria-modal="true" aria-label="%s">'
            '<div class="mn-main"><button class="mn-x" type="button" data-close aria-label="%s"><i></i><i></i></button>'
            '%s%s</div>%s</div></div>') % (
        ' has-side' if side else '', e(words[0]), e(words[1]),
        '<nav class="mn-a" aria-label="%s"><ul>%s</ul></nav>' % (e(words[0]), prim) if prim else '',
        '<ul class="mn-b">%s</ul>' % sec if sec else '', side)


def _hero(d, pic):
    h = d.get('hero') or {}
    if not h.get('title'):
        return ''
    back = ('<div class="hero-media"><div class="pin" style="--pw:%spx;--ph:%spx"><img src="%s" alt="%s" width="%s" height="%s" fetchpriority="high"></div></div>'
            % (pic.get('w') or 9999, pic.get('h') or 9999, _src(pic['src']), e(pic.get('alt', '')), pic.get('w') or '', pic.get('h') or '') if pic else '')
    desc = ''
    if h.get('text') or h.get('primary'):
        desc = '<div class="hero-desc">%s%s</div>' % ('<p>%s</p>' % e(h['text']) if h.get('text') else '', pill(h.get('primary'), 'on'))
    return '<section class="hero%s" data-slot="hero">%s<div class="wrap hero-in" data-hero>%s%s</div></section>' % (
        ' has-pic' if pic else '', back, _title(h['title']), desc)


def _intro(d, double):
    h, st = d.get('hero') or {}, d.get('statement') or {}
    if not st.get('title') and not st.get('text'):
        return ''
    two = len(double) == 2
    small = '<p class="body">%s</p>' % e(st['text']) if st.get('text') and st.get('title') else ''
    out = ('<section class="sec"><div class="wrap g12 heading">%s<div class="heading-c">%s%s</div></div></section>' % (
        '<h2 class="sup">%s</h2>' % e(h['kicker']) if h.get('kicker') else '',
        '<p class="t32">%s</p>' % e(st.get('title') or st.get('text')), '' if two else small))
    if two:     # the reference's pair: a caption top left, one picture lower left, a larger one upper right
        out += ('<section class="sec"><div class="wrap g12 dbl"><div class="dbl-l">%s%s</div><div class="dbl-r">%s</div></div></section>'
                % (small.replace('class="body"', 'class="body dbl-t"'), media(double[1], ratio=(577, 735)), media(double[0], ratio=(696, 840))))
    elif double:  # one picture: it stands alone in the right half at its own proportion; no text beside it
        out += '<section class="sec"><div class="wrap g12 dbl"><div class="dbl-r">%s</div></div></section>' % media(double[0])
    return out


def _statement(d):
    s = d.get('steps') or {}
    if not s.get('title'):
        return ''
    return '<section class="sec"><div class="wrap"><p class="t48">%s</p></div></section>' % e(s['title'])


def _card(s, small_ratio):
    link = s.get('cta') or {}
    href = link.get('h')
    title = e(s.get('title', ''))
    text = '<p class="body card-t">%s</p>' % e(s['text']) if s.get('text') else ''
    if s.get('img'):
        p = {'src': s['img'], 'alt': s.get('alt') or s.get('title', ''), 'w': s.get('_w'), 'h': s.get('_h')}
        over = ('<span class="card-over" aria-hidden="true">%s<span class="cp cp-i">%s</span></span>'
                % ('<span class="cp">%s</span>' % e(link['t']) if link.get('t') else '', ARROW) if href else '')
        pic = '<div class="card-in">%s%s</div>' % (over, media(p, ratio=small_ratio or (460, 560)))
        head = '<h3 class="h3">%s</h3>' % ('<a class="card-a" href="%s">%s</a>' % (e(href), title) if href else title)
        return '<article class="card%s">%s%s%s</article>' % (' is-link' if href else '', pic, head, text)
    return '<article class="card card-x"><h3 class="h3">%s</h3>%s%s</article>' % (title, text, pill(link, 'q'))


def _spaces(d, spaces):
    s = d.get('steps') or {}
    if not spaces:
        return ''
    smalls = [x for x in spaces if x.get('_small')]
    ratio, cap = None, ''
    if smalls:      # a small picture is never wider than its own pixels: the whole row takes its proportion and width
        m = min(smalls, key=lambda x: x['_w'])
        ratio, cap = (m['_w'], m['_h']), ' style="--cap:%dpx"' % m['_w']
    head = '<header class="g12 grp-h"><div class="grp-l"><p class="body">%s</p></div></header>' % e(s['text']) if s.get('text') else ''
    pics = any(x.get('img') for x in spaces)
    return '<section class="sec grp" data-slot="spaces"><div class="wrap">%s<div class="cards%s"%s>%s</div></div></section>' % (
        head, '' if pics else ' cards-x', cap, ''.join(_card(x, ratio) for x in spaces))


def _carta(d, pics=None):
    pics = pics or {}
    menu = (d.get('place') or {}).get('menu') or {}
    f = d.get('features') or {}
    secs = [s for s in menu.get('sections') or [] if s.get('t')]
    seen = {s.get('h') for s in secs}
    lists = [l for l in menu.get('lists') or [] if l.get('t') and l.get('h') not in seen and l.get('h') != menu.get('h')]
    if not secs and not lists:
        return ''
    cards, shown = [], []
    for s in secs:      # a section whose page shows a photograph is a picture card, as the reference's second group is
        p = pics.get(s.get('h'))
        if p and not s.get('items'):
            shown.append(_card({'title': s['t'], 'img': p['src'], 'alt': p.get('alt'), '_w': p['w'], '_h': p['h'], 'cta': {'h': s['h']}}, None))
    for s in secs + lists:
        if pics.get(s.get('h')) and not s.get('items') and s in secs:
            continue
        title = e(s['t'])
        if s.get('h'):
            title = '<a class="xa" href="%s">%s<span class="pi">%s</span></a>' % (e(s['h']), title, ARROW)
        rows, note = '', ''
        items = [i for i in s.get('items') or [] if i.get('name')]
        if items:
            notes = {i.get('note') for i in items}
            same = len(notes) == 1 and items[0].get('note')
            rows = '<table class="dish"><tbody>%s</tbody></table>' % ''.join(
                '<tr><th scope="row">%s%s</th><td>%s</td></tr>' % (
                    '<a href="%s">%s</a>' % (e(i['h']), e(i['name'])) if i.get('h') else e(i['name']),
                    '' if same or not i.get('note') else ' <small>%s</small>' % e(i['note']), e(i.get('price', ''))) for i in items)
            note = '<p class="dish-n">%s</p>' % e(items[0]['note']) if same else ''
        cards.append('<article class="card card-x"><h3 class="h3">%s</h3>%s%s</article>' % (title, rows, note))
    sec = d.get('hero', {}).get('secondary') or {}
    more = pill(sec, 'q') if sec.get('h') == menu.get('h') else ''
    head = ('<header class="g12 grp-h"><div class="grp-l">%s%s</div></header>' % ('<h2 class="sup">%s</h2>' % e(f['title']) if f.get('title') else '', more)
            if f.get('title') or more else '')
    row = '<div class="cards cards-g" style="--k:%d">%s</div>' % (len(shown) if len(shown) <= 4 else 3, ''.join(shown)) if shown else ''
    return '<section class="sec grp" data-slot="menu"><div class="wrap">%s%s%s</div></section>' % (
        head, row, '<div class="cards cards-x%s">%s</div>' % (' after' if row else '', ''.join(cards)) if cards else '')


def _quote(d):
    q = (d.get('quotes') or [None])[0]
    if not q:
        return ''
    if isinstance(q, str):
        q = {'text': q}
    text = q.get('text') or q.get('q') or q.get('quote')
    if not text:
        return ''
    who, what = q.get('name') or q.get('author') or q.get('by'), q.get('role') or q.get('source') or q.get('where')
    cite = '<footer class="q-c">%s%s</footer>' % ('<span class="sup">%s</span>' % e(who) if who else '',
                                                  '<span class="sup q-m">%s</span>' % e(what) if what else '') if who or what else ''
    return '<section class="sec quote"><div class="wrap g12"><blockquote class="q"><p class="t48">%s</p>%s</blockquote></div></section>' % (e(text), cite)


def _gallery(pics, words):
    if not pics:
        return ''
    slides = ''.join('<div class="gs%s"><div class="gs-in">%s</div></div>' % (' on' if i == 0 else '', media(p, ratio=(16, 9), px=False))
                     for i, p in enumerate(pics))
    ctl = ''
    if len(pics) > 1:
        ctl = ('<button class="gb gb-p" type="button" aria-label="%s"></button><button class="gb gb-n" type="button" aria-label="%s"></button>'
               '<span class="g-n" aria-live="polite"><b>1</b> / %d</span><span class="g-cur" aria-hidden="true">%s</span>'
               % (e(words[2]), e(words[3]), len(pics), ARROW))
    return '<section class="sec gal" data-slot="gallery"><div class="wrap"><div class="g-box" data-gal>%s%s</div></div></section>' % (slides, ctl)


def _story(d, pics):
    ev = [x for x in (d.get('place') or {}).get('events') or [] if x.get('what')]
    if not ev:
        return ''
    x = ev[0]
    facts = ' · '.join(e(v) for v in (x.get('price'), x.get('where')) if v)
    inner = '<div class="st-in">%s%s</div>' % ('<p class="body">%s</p>' % facts if facts else '', pill(x.get('cta'), 'q'))
    if len(pics) == 2:
        body = '<div class="g12 st-c">%s%s%s</div>' % (media(pics[0], 'st-a', ratio=(340, 500)), media(pics[1], 'st-b', ratio=(1, 1)), inner)
    else:
        body = '<div class="g12 st-c st-c0">%s</div>' % inner
    return ('<section class="sec story" data-slot="event"><div class="wrap"><header class="g12 st-h">%s<p class="t32">%s</p></header>%s</div></section>'
            % ('<h2 class="sup">%s</h2>' % e(x['when']) if x.get('when') else '', e(x['what']), body))


def _cloud(d, pics, in_menu):
    h = d.get('hero') or {}
    sec = h.get('secondary') or {}
    btn = '' if in_menu else pill(sec, 'q')
    if not h.get('text2') and not btn:
        return ''
    ims = ''
    for i, (p, a) in enumerate(zip(pics, (-47, -118, -146, 142, 82, 40))):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        ims += '<div class="cl-i%s" data-a="%d" style="--x:%.0fpx;--y:%.0fpx;--mx:%.0fpx;--my:%.0fpx">%s</div>' % (
            ' cl-s' if i in (1, 5) else '', a, c * 372, s * 300, c * 200, s * 262, media(p, ratio=(180, 200)))
    return ('<section class="sec cloud%s"%s><div class="cl-c">%s%s</div>%s</section>' % (
        ' has-pics' if ims else '', ' data-cloud' if ims else '',
        '<h2 class="t32">%s</h2>' % e(h['text2']) if h.get('text2') else '', btn, '<div class="cl-m" aria-hidden="true">%s</div>' % ims if ims else ''))


def _marquee(pics):
    if not pics:
        return ''
    row = ''.join('<div class="mq-i">%s</div>' % media(p, px=False) for p in pics)
    return ('<section class="sec mq" data-slot="marquee"><div class="mq-w"><div class="mq-t">%s<div class="mq-d" aria-hidden="true">%s</div></div></div></section>'
            % (row, row.replace(' alt="', ' alt="" data-alt="')))


def _cta(d, pic):
    c, h = d.get('close') or {}, d.get('hero') or {}
    link = c.get('cta') or (d.get('place') or {}).get('booking')
    if not c.get('title') and not link:
        return ''
    body = ''.join('<p class="body">%s</p>' % e(t) for t in (c.get('text'), h.get('note')) if t)
    back = '<div class="cv-m">%s</div>' % media(pic, ratio=(1440, 1270), style='max-width:none;') if pic else ''
    return ('<section class="cv%s" data-slot="close"%s>%s<div class="wrap g12 cv-w"><div class="cv-c">%s%s%s</div></div></section>' % (
        ' has-pic' if pic else '', ' style="max-width:%spx;--car:%s/%s;--cph:%spx;margin:0 auto"' % (((pic['w'], pic['w'], pic['h']) if pic['w'] * 1270 > pic['h'] * 1440 else (min(pic['w'], pic['h'] * 1440 // 1270), 1440, 1270)) + (pic['h'],)) if pic else '', back, '<h2 class="t32">%s</h2>' % e(c['title']) if c.get('title') else '',
        '<div class="cv-b">%s</div>' % body if body else '', pill(link, 'on')))


def _footer(d):
    pl, f, b = d.get('place') or {}, d.get('foot') or {}, d.get('brand') or {}
    nav = [n for n in d.get('nav') or [] if n.get('t') and n.get('h')]
    social = [s for s in pl.get('social') or [] if s.get('t') and s.get('h')]
    sh = {s['h'] for s in social}
    legal = [l for l in f.get('links') or [] if l.get('t') and l.get('h') and l['h'] not in sh]
    ul = lambda items: '<ul>%s</ul>' % ''.join('<li><a href="%s">%s</a></li>' % (e(i['h']), e(i['t'])) for i in items)
    groups = []
    if nav:
        groups.append(('fg1', ul(nav)))
    if social:
        groups.append(('fg2', ul(social)))
    a = pl.get('address') or {}
    lines = [a.get('name') or b.get('name'), a.get('street'), ' '.join(x for x in (a.get('postcode'), a.get('city')) if x),
             ', '.join(x for x in (a.get('region') if a.get('region') != a.get('city') else None, a.get('country')) if x)]
    addr = ''
    if a:
        addr = '<address>%s</address>' % '<br>'.join(e(x) for x in lines if x)
    elif f.get('text'):
        addr = '<p>%s</p>' % e(f['text'])
    ph = pl.get('phone') or {}
    contact = []
    if ph.get('t'):
        # a note beside the phone is printed only when the client's own page says the same words (the data's note
        # can be a remark about the capture, e.g. balamo's)
        own = ' '.join(str(x or '') for x in ((d.get('hero') or {}).get('note'), (d.get('hero') or {}).get('text'), (d.get('close') or {}).get('text'), f.get('text'))).lower()
        note = ' <span class="f-n">%s</span>' % e(ph['note']) if ph.get('note') and str(ph['note']).lower() in own else ''
        contact.append('<li>%s%s</li>' % ('<a href="%s">%s</a>' % (e(ph['h']), e(ph['t'])) if ph.get('h') else e(ph['t']), note))
    if pl.get('email'):
        contact.append('<li><a href="mailto:%s">%s</a></li>' % (e(pl['email']), e(pl['email'])))
    if addr or contact:
        groups.append(('fg3', addr + ('<ul class="f-ct">%s</ul>' % ''.join(contact) if contact else '')))
    hours = [x for x in pl.get('hours') or [] if x.get('days')]
    if hours:
        groups.append(('fg4', '<table class="f-h"><tbody>%s</tbody></table>' % ''.join(
            '<tr><th scope="row">%s</th><td>%s</td></tr>' % (e(x['days']), ' – '.join(e(v) for v in (x.get('open'), x.get('close')) if v)) for x in hours)))
    book = pl.get('booking') or d.get('cta')
    if book and book.get('t') and book.get('h'):
        groups.append(('fg5', pill(book, 'on')))
    notices = ''
    for n in pl.get('notices') or []:
        img = ('<img src="%s" alt="" width="%s" height="%s" loading="lazy" style="max-width:min(100%%,%spx)">'
               % (_src(n['img']), n.get('w') or '', n.get('h') or '', min(n.get('w') or 240, 240)) if n.get('img') else '')
        notices += '<div class="f-nt">%s<div>%s</div></div>' % (img, ''.join('<p>%s</p>' % e(t) for t in n.get('text') or []))
    bottom = '<div class="f-b"><p>%s</p>%s</div>' % (e(f.get('legal') or ''), ul(legal) if legal else '') if f.get('legal') or legal else ''
    if not groups and not bottom and not notices:
        return ''
    return '<footer class="ft" data-foot><div class="ft-in"><div class="wrap"><div class="g12 f-g">%s</div>%s%s</div></div></footer>' % (
        ''.join('<div class="fg %s">%s</div>' % g for g in groups), notices, bottom)


# ───────────────────────── the page
CSS = r'''
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--ink);font:400 16px/1.25 Inter,system-ui,sans-serif;letter-spacing:-.01em;-webkit-font-smoothing:antialiased;overflow-x:clip}
img{display:block;max-width:100%;height:auto}
a{color:inherit;text-decoration:none}
h1,h2,h3,p,ul,blockquote,address,table{margin:0;padding:0;font:inherit}
ul{list-style:none}address{font-style:normal}
:focus-visible{outline:2px solid currentColor;outline-offset:3px;border-radius:2px}
.skip{position:absolute;left:-9999px;top:0;background:var(--pillon);color:var(--dark);padding:9px 12px;outline-offset:-4px;border-radius:2px;z-index:50;font:500 14px/1 Inter,sans-serif}
.skip:focus{left:8px;top:8px}
.wrap{padding-left:16px;padding-right:16px}
.g12{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:16px}
.sup{font:500 14px/1 Inter,system-ui,sans-serif;letter-spacing:-.01em;text-transform:uppercase}
.t32{font-family:Fraunces,Georgia,serif;font-optical-sizing:auto;font-weight:310;font-size:32px;line-height:1.15;letter-spacing:0;text-wrap:pretty}
.t48{font-family:Fraunces,Georgia,serif;font-weight:220;font-size:48px;line-height:1.1;letter-spacing:0;color:var(--acct);text-wrap:pretty}
.h3{font-family:Fraunces,Georgia,serif;font-weight:310;font-size:20px;line-height:1.2;letter-spacing:0}
.body{max-width:459px;text-wrap:pretty}

/* pictures: a clipping frame; the picture inside is 12 % larger and drifts ±6 % as the frame crosses the screen */
.m{position:relative;overflow:hidden;background:var(--pill);width:100%}
.m img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;will-change:transform}

/* pill buttons: a label and a square arrow, 24 high, 2 radius, 4 apart; both fill with the accent on hover (.3s) */
.pill{display:inline-flex;gap:4px;font:500 14px/1 Inter,system-ui,sans-serif;letter-spacing:-.01em;color:var(--ink);vertical-align:top;max-width:100%}
.pill .pl,.pi,.cp{background:var(--pill);border-radius:2px;transition:background-color .3s,color .3s}
.pill .pl{display:flex;align-items:center;padding:5px 8px;min-height:24px}
.pi{display:inline-flex;align-items:center;justify-content:center;width:30px;height:24px;flex:none;overflow:hidden}
.pi svg{margin:-3px 0}
.pill.on{color:var(--dark)}.pill.on .pl,.pill.on .pi{background:var(--pillon)}
.pill:hover .pl,.pill:hover .pi,.pill:focus-visible .pl,.pill:focus-visible .pi,.xa:hover .pi{background:var(--deep);color:var(--lite)}
.pill.on:hover .pl,.pill.on:hover .pi{background:var(--dark);color:var(--lite)}
.pill:active .pl,.pill:active .pi{opacity:.8}
.pill.on:focus-visible{outline-color:var(--lite)}

/* header: lies on the opening picture; leaves when the page goes down, returns as a solid bar when it comes back up */
.hd{position:absolute;top:0;left:0;right:0;z-index:20;display:grid;grid-template-columns:1fr auto 1fr;align-items:start;padding:4px;color:var(--lite);
 transition:transform .3s cubic-bezier(.25,.46,.45,.94),background-color .15s cubic-bezier(.25,.46,.45,.94)}
.hd.fx{position:fixed}.hd.hide{transform:translateY(-101%)}
.hd.solid{background:var(--g);color:var(--ink)}
.hl{display:inline-flex;align-items:center;justify-self:start;min-height:38px;padding:12px;font:500 14px/1 Inter,system-ui,sans-serif;letter-spacing:-.01em;text-transform:uppercase;
 background:none;border:0;color:inherit;cursor:pointer;transition:color .3s}
a.hl{justify-self:end}
.mb{flex-direction:column;justify-content:center;gap:5px;width:54px}
.mb i,.mn-x i{display:block;width:26px;height:1px;background:currentColor}
.brand{justify-self:center;align-self:center;padding:8px 12px;text-align:center}
.wm{display:block;font-family:Fraunces,Georgia,serif;font-weight:310;font-size:17px;line-height:1.05;letter-spacing:.06em;text-transform:uppercase;max-width:15em;text-wrap:balance}
.logo{height:44px;width:auto}
.hd.solid .logo{height:30px}.hd.solid .brand{padding:4px 12px}.hd.solid .wm{font-size:13px;max-width:none}
.logo{border-radius:2px}

/* menu: a panel 8 from the edges, the large list, the small list, the spaces as cards in a second column */
.mn{position:fixed;inset:0;z-index:40;visibility:hidden;transition:visibility 0s .8s}
.mn.open{visibility:visible;transition-delay:0s}
.mn-bd{position:absolute;inset:0;background:rgba(var(--veil),.5);opacity:0;transition:opacity .6s cubic-bezier(.25,.46,.45,.94)}
.mn.open .mn-bd{opacity:1}
.mn-panel{position:absolute;left:8px;top:8px;bottom:8px;width:467px;max-width:calc(100% - 16px);display:flex;background:var(--g);border-radius:4px;overflow:hidden;
 transform:translateX(calc(-100% - 16px));transition:transform .8s cubic-bezier(.77,0,.175,1)}
.mn-panel.has-side{width:839px}
.mn.open .mn-panel{transform:none}
.mn-main{flex:0 0 467px;max-width:100%;padding:80px 32px 32px;overflow:auto;position:relative}
.mn-x{position:absolute;left:10px;top:10px;width:50px;height:38px;background:none;border:0;color:var(--acct);cursor:pointer}
.mn-x i{position:absolute;left:12px;top:18px;transform:rotate(45deg)}.mn-x i+i{transform:rotate(-45deg)}
.mn-a a{display:block;font-family:Fraunces,Georgia,serif;font-weight:220;font-size:40px;line-height:1;padding:4px 0;transition:color .3s}
.mn-a a:hover,.mn-b a:hover{color:var(--acct)}
.mn-b{margin-top:40px}.mn-b a{display:block;padding:4px 0;transition:color .3s}
.mn-side{flex:1;min-width:0;overflow:auto;padding:16px;border-left:1px solid var(--pill);display:flex;flex-direction:column;gap:22px}
.mn-card .h3{margin-top:12px}

/* hero: one screen; the picture is pinned behind and the text leaves at half the page's speed */
.hero{position:relative;z-index:0;min-height:100vh;min-height:100svh;display:flex;align-items:center;overflow:clip;background:var(--deep);color:var(--lite)}
.hero-media{position:absolute;left:0;top:0;width:100%;height:200%;z-index:-1}
.hero.has-pic{background:var(--dark)}
/* the opening picture is never shown above its own pixels: on a screen wider or higher than it, the frame stops at its size */
.pin{position:sticky;top:0;height:100vh;height:100svh;max-width:var(--pw);max-height:var(--ph);margin:0 auto;overflow:hidden}
.pin img{width:100%;height:100%;object-fit:cover;animation:cover 2s cubic-bezier(.19,1,.22,1) both}
.pin::after{content:"";position:absolute;inset:0;background:linear-gradient(rgba(var(--veil),.68),rgba(var(--veil),.63) 30%,rgba(var(--veil),.65))}
.hero-in{width:100%;display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:16px;row-gap:100px;padding-top:96px;padding-bottom:96px}
.ht{grid-column:1/-1;font-family:Fraunces,Georgia,serif;font-weight:220;font-size:var(--fd);line-height:.9;letter-spacing:-.02em;text-transform:uppercase;word-spacing:.16em;padding:0 8.333vw}
.ht .L{display:block;text-align:center}.ht .L:first-child{text-align:left}.ht .L:last-child:not(:first-child){text-align:right}
.ht .w{display:inline-block;overflow:hidden;overflow:clip;padding:.14em .03em 0;margin:-.14em -.03em 0;vertical-align:top;white-space:nowrap}
.ht .c{display:inline-block;animation:rise 1.6s cubic-bezier(.19,1,.22,1) both;animation-delay:calc(var(--i)*.05s)}
.hero-desc{grid-column:7/span 4;max-width:340px;animation:blurin 1s cubic-bezier(.165,.84,.44,1) .5s both}
.hero-desc p{font-family:Fraunces,Georgia,serif;font-weight:310;font-size:18px;line-height:1.1;letter-spacing:0;margin-bottom:41px}
@keyframes rise{from{transform:translateY(105%);filter:blur(6px)}to{transform:none;filter:blur(0)}}
@keyframes blurin{from{opacity:0;filter:blur(10px)}to{opacity:1;filter:blur(0)}}
@keyframes cover{from{transform:scale(1.2)}to{transform:none}}

/* the page under the hero: sections 100 apart */
.flow{position:relative;z-index:1;background:var(--g);display:flex;flex-direction:column;gap:100px;padding:100px 0 0}
.flow>.sec:last-child{margin-bottom:100px}
.heading>.sup{grid-column:1/span 2}
.heading-c{grid-column:7/span 6;display:grid;gap:40px}
.heading>.heading-c:first-child{grid-column:7/span 6}
.dbl-l{grid-column:1/span 5}.dbl-r{grid-column:7/span 6}
.dbl-t{max-width:346px}.dbl-l .m{margin-top:320px}.dbl-l .dbl-t+.m{margin-top:320px}
.grp{padding:16px 0}
.grp-h{margin-bottom:32px}
.grp-l{grid-column:1/span 4;display:flex;flex-direction:column;align-items:flex-start;gap:32px}
.cards{display:flex;gap:16px;align-items:flex-start}
.card{flex:1 1 0;min-width:0;max-width:var(--cap,none);display:flex;flex-direction:column;gap:12px;position:relative}
.card-in{position:relative;overflow:hidden}
.card-t{margin-top:-4px}
.card-a::after{content:"";position:absolute;inset:0;z-index:2}
.card-over{position:absolute;left:8px;right:8px;top:8px;z-index:1;display:flex;justify-content:space-between;gap:4px;overflow:hidden;pointer-events:none;font:500 14px/1 Inter,sans-serif}
.cp{display:inline-flex;align-items:center;min-height:24px;padding:5px 8px;background:var(--pillon);color:var(--dark);transform:translateY(calc(100% + 2px));transition:transform .4s cubic-bezier(.19,1,.22,1)}
.cp-i{padding:0;width:24px;border-radius:50%;justify-content:center;overflow:hidden}.cp-i svg{flex:none}
.card:hover .cp,.card:focus-within .cp{transform:none}
.cards-x{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:48px 16px}
.cards-g{display:grid;grid-template-columns:repeat(var(--k),minmax(0,1fr));gap:48px 16px}.cards-g .card{max-width:none}.cards-x.after{margin-top:64px}
.card-x{max-width:none;align-items:flex-start}
.card-x .pill{margin-top:8px}
.xa{display:inline-flex;align-items:center;gap:12px}.xa .pi{color:var(--ink)}
.dish{width:100%;max-width:459px;border-collapse:collapse;margin-top:4px}
.dish th{font-weight:400;text-align:left;padding:6px 16px 6px 0;border-top:1px solid var(--pill)}
.dish td{text-align:right;white-space:nowrap;padding:6px 0;border-top:1px solid var(--pill);font-variant-numeric:tabular-nums}
.dish a:hover{color:var(--acct)}.dish small,.dish-n{font-size:14px;color:var(--mute)}
.quote{padding:80px 0}
.q{grid-column:2/span 10}
.q-c{display:flex;gap:8px;margin-top:32px;padding:16px 0}.q-m{color:var(--mute)}
.gal{padding:16px 0}
.g-box{position:relative;aspect-ratio:16/9;overflow:hidden;background:var(--pill)}
.gs{position:absolute;inset:0;overflow:hidden;z-index:0;visibility:hidden}
.gs.on{z-index:2;visibility:visible}.gs.was{z-index:1;visibility:visible}
.gs .m{height:100%;aspect-ratio:auto!important}
.gs.in{animation:wipe 1.2s cubic-bezier(.19,1,.22,1) both}.gs.in .gs-in{animation:cover 1.2s cubic-bezier(.19,1,.22,1) both}
.gs-in{height:100%}
@keyframes wipe{from{clip-path:inset(0 0 0 100%)}to{clip-path:inset(0)}}
.gs.in.rev{animation-name:wiper}@keyframes wiper{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0)}}
.gb{position:absolute;top:0;bottom:0;width:50%;z-index:4;background:none;border:0;padding:0;cursor:pointer}
.gb-p{left:0}.gb-n{right:0}
.gb:focus-visible{outline:2px solid var(--lite);outline-offset:-6px}
.g-n{position:absolute;right:12px;bottom:12px;z-index:5;color:var(--lite);font:500 14px/1 Inter,sans-serif;padding:5px 8px;border-radius:2px;background:rgba(var(--veil),.64);pointer-events:none}
.g-n b{font-weight:500}
.g-cur{position:absolute;left:0;top:0;z-index:5;display:none;width:30px;height:24px;align-items:center;justify-content:center;background:var(--pillon);color:var(--dark);border-radius:2px;pointer-events:none;overflow:hidden}
.g-cur svg{flex:none;transition:transform .5s cubic-bezier(.165,.84,.44,1)}.g-cur.p svg{transform:scaleX(-1)}
.story{padding:16px 0}
.st-h{padding:80px 0}.st-h>.sup{grid-column:1/span 2}.st-h>.t32{grid-column:7/span 6}
.st-c{grid-template-rows:auto 1fr;row-gap:20px;padding:16px 0}
.st-a{grid-column:7/span 3;grid-row:1/span 2}.st-b{grid-column:10/span 3}
.st-in{grid-column:10/span 3;align-self:end;display:flex;flex-direction:column;align-items:flex-start;gap:32px}
.st-c0{padding:0;margin-top:-40px}.st-c0 .st-in{grid-column:7/span 6}
.cloud{position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden;padding:16px}
.cloud.has-pics{height:882px}
.cl-c{position:relative;z-index:3;display:flex;flex-direction:column;align-items:center;gap:40px;text-align:center;max-width:563px}
.cl-m{position:absolute;inset:0}
.cl-i{position:absolute;left:50%;top:50%;width:180px;margin:-100px 0 0 -90px;z-index:2;transform:translate(var(--x),var(--y))}
.cl-s{width:140px;margin:-80px 0 0 -70px;z-index:1}
.mq{padding-bottom:0}
.mq-w{overflow:hidden}
.mq-t{display:flex;width:max-content;animation:mq 120s linear infinite}
.mq-t:hover{animation-play-state:paused}
.mq-d{display:flex}
.mq-i{width:480px;padding:0 8px;flex:none}
@keyframes mq{to{transform:translateX(-50%)}}

/* the closing cover and the slab under it */
.cv{position:relative;z-index:1;display:flex;align-items:flex-end;background:var(--deep);color:var(--lite);overflow:hidden}
.cv.has-pic{aspect-ratio:var(--car,1440/1270)}
.cv-m{position:absolute;inset:0}.cv-m .m{height:100%;aspect-ratio:auto!important}
.cv-m::after{content:"";position:absolute;inset:0;background:linear-gradient(rgba(var(--veil),.2),rgba(var(--veil),.66) 55%)}
.cv-w{position:relative;width:100%;padding-top:140px;padding-bottom:80px}
.cv-c{grid-column:7/span 4;display:flex;flex-direction:column;align-items:flex-start;gap:32px}
.cv-b{display:grid;gap:8px}
.ft{position:relative;z-index:0;background:var(--deep);color:var(--lite);overflow:clip}
.cv:not(.has-pic)+.ft .ft-in{padding-top:0}
.ft-in{padding:80px 0 25px;will-change:transform}
.f-g{row-gap:40px;min-height:234px}
.fg{grid-column:span 2}.fg3{grid-column:span 3}.fg4{grid-column:span 3}.fg5{grid-column:span 2;justify-self:end}
.fg li+li{margin-top:4px}.fg a:hover{color:var(--sub)}
.fg a,.f-b a{transition:color .3s}
.f-ct{margin-top:20px}.f-n{color:var(--sub)}
.f-h{border-collapse:collapse}.f-h th{font-weight:400;text-align:left;padding:0 16px 4px 0;vertical-align:top}.f-h td{padding:0 0 4px;white-space:nowrap;vertical-align:top;font-variant-numeric:tabular-nums}
.f-nt{display:flex;gap:16px;align-items:flex-start;margin-top:56px;font-size:14px;line-height:1.3;color:var(--sub)}
.f-nt img{flex:none;width:auto;border-radius:2px}.f-nt div{max-width:696px;display:grid;gap:8px}
.f-b{display:flex;justify-content:space-between;gap:16px 32px;flex-wrap:wrap;margin-top:56px;font-size:14px;line-height:1.25;color:var(--sub)}
.f-b ul{display:flex;gap:4px 12px;flex-wrap:wrap}.f-b a{color:var(--lite)}.f-b a:hover{color:var(--sub)}

@media (max-width:899px){
 .g12{grid-template-columns:repeat(4,minmax(0,1fr))}
 .t32{font-size:28px}.t48{font-size:24px;font-weight:310}.quote .t48{font-size:32px;font-weight:220}.h3{font-size:18px}
 .hd{padding:4px 4px}.hl{min-height:40px}
 .mn-panel,.mn-panel.has-side{left:0;top:0;bottom:0;width:100%;max-width:100%;border-radius:0;flex-direction:column;transform:translateX(-100%)}
 .mn-main{flex:1 1 auto;padding:100px 16px 24px}
 .mn-a a{padding:6px 0}.mn-b{display:grid;grid-template-columns:1fr 1fr;gap:0 16px}.mn-b a{padding:10px 0}
 .mn-side{flex:none;flex-direction:row;border-left:0;padding:16px;gap:16px}.mn-card{flex:0 0 171px}.mn-card .h3{font-size:15.6px}
 .hero-in{grid-template-columns:repeat(4,minmax(0,1fr))}
 .ht{font-size:var(--fm);padding:0}
 .ht .L{text-align:left!important}.ht .l{display:block}.ht .L:last-child:not(:first-child) .l,.ht .L:only-child .l:last-child:not(:first-child){text-align:right}
 .hero-desc{grid-column:2/span 3;max-width:265px}.hero-desc p{margin-bottom:32px}
 .flow{gap:80px;padding-top:80px}.flow>.sec:last-child{margin-bottom:80px}
 .heading>.sup,.heading-c,.heading>.heading-c:first-child,.dbl-l,.dbl-r,.grp-l,.q,.st-h>.sup,.st-h>.t32,.cv-c{grid-column:1/-1}
 .heading{row-gap:32px}.heading-c{gap:32px}
 .dbl{row-gap:16px}.dbl-l .m,.dbl-l .dbl-t+.m{margin-top:64px}.dbl-l .m:first-child{margin-top:0}
 .cards{flex-direction:column;gap:32px}.card{flex:none;width:100%}
 .cards-x,.cards-g{grid-template-columns:1fr;gap:32px}
 .cp{transform:none}
 .quote{padding:64px 0}
 .g-box{aspect-ratio:4/5;overflow:visible;margin-bottom:38px}
 .g-n{right:auto;left:50%;bottom:-36px;transform:translateX(-50%);background:var(--pill);color:var(--ink);border-radius:100px;padding:4px 10px}
 .st-h{padding:64px 0;row-gap:32px}
 .st-a{grid-column:1/span 2;grid-row:auto}.st-b{grid-column:3/span 2}.st-in,.st-c0 .st-in{grid-column:1/-1;margin-top:20px}
 .st-c0{margin-top:-32px}
 .cloud.has-pics{height:722px}.cl-c{gap:32px}
 .cl-i{width:120px;margin:-70px 0 0 -60px;transform:translate(var(--mx),var(--my))}.cl-s{width:120px;margin:-70px 0 0 -60px}
 .mq-i{width:293px}
 .cv.has-pic{aspect-ratio:390/840;max-height:var(--cph)}.cv-w{padding-top:96px;padding-bottom:40px}
 .ft-in{padding:64px 0 16px}
 .fg,.fg3,.fg4,.fg5{grid-column:1/-1;justify-self:start}.fg li+li{margin-top:0}.fg a:not(.pill){display:inline-block;padding:10px 0}.f-ct{margin-top:8px}
 .f-nt{flex-direction:column}.f-b{margin-top:48px}.f-b a{display:inline-block;padding:8px 0}
}
@media (hover:none){.cp{transform:none}}
@media (prefers-reduced-motion:reduce){
 *,*::before,*::after{animation:none!important;transition:none!important}
 .mq-w{overflow-x:auto}
}
'''

JS = r'''
(function(){
var R=matchMedia('(prefers-reduced-motion: reduce)').matches,D=document,W=window,$=function(s,c){return (c||D).querySelector(s)},$$=function(s,c){return [].slice.call((c||D).querySelectorAll(s))};
/* header */
var hd=$('#hd'),ly=0;if(hd){hd.classList.add('fx');var onH=function(){var y=W.scrollY;hd.classList.toggle('solid',y>40);hd.classList.toggle('hide',y>40&&y>ly);ly=y};}
/* menu */
var mn=$('#menu'),mb=$('.mb');
if(mn&&mb){var last=null,setM=function(o){mn.classList.toggle('open',o);mn.setAttribute('aria-hidden',o?'false':'true');mb.setAttribute('aria-expanded',o?'true':'false');D.documentElement.style.overflow=o?'hidden':'';
 if(o){last=D.activeElement;var x=$('.mn-x',mn);x&&x.focus()}else if(last){last.focus()}};
 mn.inert=true;var sm=setM;setM=function(o){mn.inert=!o;sm(o)};
 mb.addEventListener('click',function(){setM(true)});$$('[data-close]',mn).forEach(function(b){b.addEventListener('click',function(){setM(false)})});
 D.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&mn.classList.contains('open'))setM(false)});
 $$('a',mn).forEach(function(a){a.addEventListener('click',function(){setM(false)})});}
/* gallery: the next picture wipes in over 1.2s while it settles from 1.2 to 1 */
$$('[data-gal]').forEach(function(g){var s=$$('.gs',g),i=0,n=$('.g-n b',g),cur=$('.g-cur',g);if(s.length<2)return;
 var go=function(k){var j=(i+k+s.length)%s.length;s.forEach(function(x){x.classList.remove('was','in','rev')});s[i].classList.remove('on');s[i].classList.add('was');
  s[j].classList.add('on');if(!R){void s[j].offsetWidth;s[j].classList.add('in');if(k<0)s[j].classList.add('rev')}i=j;if(n)n.textContent=j+1};
 $('.gb-p',g).addEventListener('click',function(){go(-1)});$('.gb-n',g).addEventListener('click',function(){go(1)});
 if(cur&&matchMedia('(hover:hover)').matches){g.addEventListener('pointermove',function(ev){var r=g.getBoundingClientRect(),x=ev.clientX-r.left,y=ev.clientY-r.top;cur.style.display='flex';
  cur.style.transform='translate('+(x+14)+'px,'+(y+14)+'px)';cur.classList.toggle('p',x<r.width/2)});g.addEventListener('pointerleave',function(){cur.style.display='none'})}});
/* cards that lead somewhere: the pills follow the pointer down the picture */
if(matchMedia('(hover:hover)').matches)$$('.card.is-link').forEach(function(c){var o=$('.card-over',c),b=$('.card-in',c);if(!o||!b)return;
 c.addEventListener('pointermove',function(ev){var r=b.getBoundingClientRect();o.style.transform='translateY('+Math.max(0,Math.min(r.height-40,ev.clientY-r.top-20))+'px)'});
 c.addEventListener('pointerleave',function(){o.style.transform=''})});
if(R){if(hd){addEventListener('scroll',onH,{passive:true});onH()}return}
var px=$$('img[data-px]'),hero=$('[data-hero]'),cloud=$('[data-cloud]'),ci=cloud?$$('.cl-i',cloud):[],foot=$('[data-foot]'),fin=foot&&$('.ft-in',foot),tick=false;
/* a picture drifts only when its own pixels cover the 12 % larger frame: none is ever shown above its own size */
function fits(i,r){var w=+i.getAttribute('width')||1e9,h=+i.getAttribute('height')||1e9;return w>=r.width*1.12&&h>=r.height*1.12}
px.forEach(function(i){if(fits(i,i.parentNode.getBoundingClientRect()))i.style.transform='scale(1.12)'});
function frame(){tick=false;var vh=W.innerHeight,y=W.scrollY;
 if(hd)onH();
 if(hero)hero.style.transform=y<vh*1.2?'translate3d(0,'+(y*.5).toFixed(1)+'px,0)':'';
 for(var k=0;k<px.length;k++){var f=px[k].parentNode,r=f.getBoundingClientRect();if(r.bottom<-80||r.top>vh+80)continue;
  if(!fits(px[k],r)){px[k].style.transform='';continue}
  var p=(r.top+r.height/2-vh/2)/(vh/2+r.height/2);px[k].style.transform='translate3d(0,'+(-p*5.4).toFixed(2)+'%,0) scale(1.12)'}
 if(cloud){var cr=cloud.getBoundingClientRect();if(cr.bottom>-200&&cr.top<vh+200){var t=(vh-cr.top)/(vh+cr.height),m=W.innerWidth<900,rx=m?200:372,ry=m?262:300;
  for(var q=0;q<ci.length;q++){var a=(parseFloat(ci[q].getAttribute('data-a'))+(t-.5)*56)*Math.PI/180;ci[q].style.transform='translate3d('+(Math.cos(a)*rx).toFixed(1)+'px,'+(Math.sin(a)*ry).toFixed(1)+'px,0)'}}}
 if(fin&&!held){if(W.innerWidth>=900){var fr=foot.getBoundingClientRect(),v=Math.max(0,Math.min(fr.height,vh-fr.top));fin.style.transform=fr.top<vh+40?'translate3d(0,'+(-(fr.height-v)*.8).toFixed(1)+'px,0)':''}else fin.style.transform=''}}
/* keyboard focus inside the foot: it stops sliding and stands where it is laid out, so the focused link is never under the page */
var held=false;if(foot&&fin)foot.addEventListener('focusin',function(ev){if(!ev.target.matches(':focus-visible'))return;held=true;fin.style.transform='';ev.target.scrollIntoView({block:'nearest'})});
function ask(){if(!tick){tick=true;requestAnimationFrame(frame)}}
addEventListener('scroll',ask,{passive:true});addEventListener('resize',ask);addEventListener('load',ask);frame();
})();
'''


def render(d: dict) -> str:
    lang = (d.get('lang') or 'en')[:2].lower()
    words = WORDS.get(lang, WORDS['en'])
    place = d.get('place') or {}
    by_src = {p.get('src'): p for p in (d.get('media') or {}).get('photos') or []}
    spaces = []
    for s in place.get('spaces') or []:
        if not s.get('title'):
            continue
        s = dict(s)
        p = by_src.get(s.get('img')) or {}
        s['_w'], s['_h'], s['_small'], s['alt'] = p.get('w') or 4, p.get('h') or 3, bool(p.get('small')), p.get('alt')
        spaces.append(s)
    photos = [p for p in (d.get('media') or {}).get('photos') or [] if p.get('src')]
    # the opening picture is chosen first (it needs the one photograph that can fill a screen); cards then take theirs
    hero = _allocate(d, [s for s in spaces if s.get('img')], only_hero=True)['hero']
    if not spaces:      # no spaces listed: the client's own doors (steps) take the cards; each takes the photograph its own page shows
        spaces, got = [], set()
        for s in (d.get('steps') or {}).get('items') or []:
            if not s.get('title'):
                continue
            s = dict(s, img=None)
            p = _by_page(photos, (s.get('cta') or {}).get('h'), got | ({hero['src']} if hero else set()))
            if p:
                got.add(p['src'])
                s.update(img=p['src'], _w=p['w'], _h=p['h'], _small=bool(p.get('small')), alt=p.get('alt'))
            spaces.append(s)
        if not all(s.get('img') for s in spaces):       # a row is pictures or words, not a mix
            spaces = [dict(s, img=None) for s in spaces]
    claimed = {s['img'] for s in spaces if s.get('img')} | ({hero['src']} if hero else set())
    sec_pics = {}
    for s in (place.get('menu') or {}).get('sections') or []:
        p = _by_page(photos, s.get('h'), claimed, dish_first=True) if s.get('t') and not s.get('items') else None
        if p:
            sec_pics[s['h']] = p
            claimed.add(p['src'])
    a = _allocate(d, [{'img': x} for x in claimed if not hero or x != hero['src']], hero_src=hero['src'] if hero else None)
    menu_h = (place.get('menu') or {}).get('h')
    sec = (d.get('hero') or {}).get('secondary') or {}
    carta = _carta(d, sec_pics)
    flow = ''.join((_intro(d, a['double']), _statement(d), _spaces(d, spaces), carta, _quote(d), _gallery(a['gallery'], words),
                    _story(d, a['story']), _cloud(d, a['cloud'], bool(carta) and sec.get('h') == menu_h), _marquee(a['marquee'])))
    b = d.get('brand') or {}
    title = b.get('name') or (d.get('hero') or {}).get('title') or ''
    desc = (d.get('hero') or {}).get('text') or ''
    head = ('<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>%s</title>\n%s<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link href="%s" rel="stylesheet">\n<style>%s</style>\n</head>\n') % (
        e(lang), e(title), '<meta name="description" content="%s">\n' % e(desc) if desc else '', FONTS, CSS)
    body = ('<body style="%s">\n<a class="skip" href="#main">%s</a>\n%s\n%s\n<main id="main">\n%s\n<div class="flow">%s</div>\n%s\n</main>\n%s\n<script>%s</script>\n</body>\n</html>\n') % (
        _theme(d.get('palette') or {}), e(title), _header(d, words), _menu(d, spaces, words), _hero(d, a['hero']), flow, _cta(d, a['cover']), _footer(d), JS)
    return head + body
