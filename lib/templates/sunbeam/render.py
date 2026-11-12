"""sunbeam/render.py — one pure function: render(d) -> a complete page for a PLACE (café, restaurant, shop with a door).

The build (section order, grid, measures, type scale, radii, dashed cards, the pill fixed at the foot of the window,
motion, phone layout) was measured on the reference's home page at 1440 and 390 on 2026-11-12 (see NOTES.md). Nothing of
the reference's code, words, pictures, cut-outs, icons or logo is here. Its commercial faces are replaced by open ones.
The client's data fills it; a section whose data is missing is left out whole. No model call, no file read.
"""
import colorsys
import html
import re

FONTS = ('https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@700&family=Caprasimo'
         '&family=DM+Mono:wght@500&family=Yesteryear&display=swap')

# Caprasimo advance widths per 1000 units, measured in Chrome 2026-11-12 — used to size display lines from their own
# words (longest word must fit the measure; long titles step down) without measuring anything in the browser.
_CS = " abcdefghijklmnopqrstuvwxyzáéíóúñüABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÑ0123456789&@.,!?¡¿-·«»€'/:"
_CW = dict(zip(_CS, [250, 571, 632, 512, 650, 505, 424, 578, 679, 356, 369, 734, 365, 964, 671, 564, 666, 636, 538, 477,
                     463, 678, 627, 989, 602, 619, 514, 567, 516, 356, 602, 678, 671, 678, 827, 717, 720, 802, 691, 661,
                     794, 802, 414, 627, 827, 633, 884, 830, 778, 684, 781, 776, 645, 701, 820, 803, 1040, 795, 780, 686,
                     827, 691, 414, 778, 820, 830, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 869, 799, 300, 300,
                     308, 482, 308, 482, 284, 250, 534, 534, 600, 228, 472, 300]))
# the one string the template adds: the spoken name of the phone's menu button (the reference prints the word; it is
# not in the data, so it is not printed here)
_MENU_WORD = {'es': 'Menú', 'ca': 'Menú', 'pt': 'Menu', 'fr': 'Menu', 'it': 'Menu', 'de': 'Menü', 'en': 'Menu'}
_TOP_WORD = {'es': 'Arriba', 'ca': 'Amunt', 'pt': 'Topo', 'fr': 'Haut', 'it': 'Su', 'de': 'Nach oben', 'en': 'Top'}


def e(s):
    return html.escape(str(s or ''), quote=True)


def _em(text):
    return sum(_CW.get(c, 650) for c in str(text)) / 1000


def _longest(text):
    return max([_em(w) for w in str(text).split()] or [1])


# ───────────────────────── colour: the reference's relations applied to the client's palette
def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def _cr(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _reads(c, grounds, want=4.6):
    """c moved along its own hue, darker first, then lighter, until it reads on every ground given."""
    for target in ((0, 0, 0), (255, 255, 255)):
        for i in range(0, 21):
            k = _mix(c, target, i / 20)
            if all(_cr(k, g) >= want for g in grounds):
                return k
    return (0, 0, 0) if sum(_lum(g) for g in grounds) / len(grounds) > .3 else (255, 255, 255)


def _shift(c, dh, dl):
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in c])
    r, g, b = colorsys.hls_to_rgb((h + dh / 360) % 1, max(0, min(.82, l + dl)), s)
    return (r * 255, g * 255, b * 255)


def _sat(c):
    return colorsys.rgb_to_hls(*[v / 255 for v in c])[2]


def _palette(d):
    p = d.get('palette') or {}
    ground, ink, a = _rgb(p.get('ground') or '#ffffff'), _rgb(p.get('ink') or '#111111'), _rgb(p.get('accent') or '#d43a2c')
    # reference: band runs from hsl(28,100%,63%) at the top to its brand red hsl(3,90%,56%) at the foot, so the client's
    # accent is the foot and the top is the accent 25° on and 7 points lighter
    a2 = _shift(a, 25, .07)
    third = None
    for x in p.get('extra') or []:
        c = _rgb(x)
        if _sat(c) > .25 and .06 < _lum(c) < .8:
            third = c
            break
    if third is None:
        third = _mix(a2, ground, .5)                      # the reference's third colour is a pale one
    # card ground: third at .25 with multiply — but the card is its own isolated group (isolation:isolate, so that its
    # ::before stays above the band), and in an empty group multiply has nothing under it and draws as a plain .25 layer.
    # The colour the text is read against is therefore the stop mixed a quarter toward the third colour (measured).
    tint = lambda c: _mix(c, third, .25)
    white = (255, 255, 255)
    dark = ink if _lum(ink) < .2 else (20, 20, 20)
    # A gradient that carries text has one ink for all of it. When neither white nor the dark ink reads on every stop
    # (a mid-tone accent whose lighter neighbour is too light for white and whose foot is too dark for the ink, or a
    # third colour far lighter than the accent), the stops are moved together along their own hues — toward black
    # under white text or toward white under the dark ink, whichever is the shorter way — until one ink reads on all.
    # The relations stay: lighter top, accent at the foot, the third colour at the end of the pill.
    def hold(stops, grounds_of):
        for k in range(0, 21):
            for target, want in (((0, 0, 0), 'white'), ((255, 255, 255), 'dark')):
                st = [_mix(c, target, k / 20) for c in stops]
                gr = grounds_of(st)
                if want == 'white':
                    if all(_cr(white, g) >= 4.6 for g in gr):
                        return st, white
                else:
                    k2 = _reads(dark, gr)
                    if all(_cr(k2, g) >= 4.6 for g in gr):
                        return st, k2
        return [_mix(c, (0, 0, 0), .7) for c in stops], white
    (ba, ba2), on = hold([a, a2], lambda st: st + [tint(c) for c in st])     # bands: both stops and the cards on them
    (pa, pa2, pt), on_pill = hold([a, a2, third], lambda st: st)             # the pill and the hover grounds of buttons
    deep = _reads(a, [ground, white] if _lum(ground) > .3 else [ground])        # script line, buttons with light text
    deep_on = white if _cr(white, deep) >= 4.5 else _reads(ink, [deep])
    return dict(g=_hex(ground), ink=_hex(_reads(ink, [ground])), a=_hex(a), a2=_hex(a2), t=_hex(third), on=_hex(on),
                ba=_hex(ba), ba2=_hex(ba2), pa=_hex(pa), pa2=_hex(pa2), pt=_hex(pt),
                onp=_hex(on_pill), ad=_hex(deep), ado=_hex(deep_on),
                pile=_hex(_mix(ground, a2, .14)),
                ovl=_hex(_mix(a2, ground, .35)), ovl2=_hex(_mix(a, ground, .25)),
                ovl_on=_hex(_reads(ink, [_mix(a2, ground, .35), _mix(a, ground, .25)])))


# ───────────────────────── small parts
def _src(s):
    return '../../' + s if s and not s.startswith(('http:', 'https:', 'data:', '../')) else s


def _a(h, inner, cls='', extra=''):
    if h:
        return f'<a class="{cls}" href="{e(h)}"{extra}>{inner}</a>'
    return f'<span class="{cls}"{extra}>{inner}</span>'


_ARROW = ('<svg class="arw" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M3 12h17M13 5l7 7-7 7" '
          'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
_ARROW_UP = ('<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M12 21V4M5 11l7-7 7 7" '
             'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def _display(tag, text, cls, base_em=16.0, extra=''):
    """A display heading sized from its own words: the longest word must fit the measure (--lw), and a title longer
    than the reference's steps down (--k) so that it stays about the reference's number of lines."""
    total = _em(text)
    k = 1 if total <= base_em else max(.6, (base_em / total) ** .5)
    return f'<{tag} class="{cls}" style="--lw:{_longest(text) * 1.04:.3f};--k:{k:.3f}"{extra}>{e(text)}</{tag}>'


def _menu_label(d, h):
    """the shortest label in the data that points at the menu"""
    if not h:
        return ''
    cands = [(d.get('hero') or {}).get('secondary'), (d.get('hero') or {}).get('primary'), d.get('cta')]
    cands += list(d.get('nav') or []) + list(d.get('links') or [])
    labels = [c['t'] for c in cands if c and c.get('h') == h and c.get('t')]
    return min(labels, key=len) if labels else ''


def _groups(names, limit=36):
    """names set as short sentences ("Arroces. Carnes a la brasa.") in groups that fit about two display lines"""
    out, cur = [], []
    for n in names:
        n = str(n).strip().rstrip('.')
        if not n:
            continue
        if cur and len(' '.join(cur + [n])) + len(cur) + 1 > limit:
            out.append(cur)
            cur = []
        cur.append(n)
    if cur:
        out.append(cur)
    return [' '.join(x + '.' for x in g) for g in out]


def _wordmark(name, avail, max_h, cap):
    """font-size in vw for the big name: the largest size at which the name, broken into 1–3 lines, fits the width
    and the block is no taller than max_h vw (the reference's name is one 21vw line)."""
    words = name.split()
    best = 0
    n = len(words)
    for lines in range(1, min(3, n) + 1):
        # all ways to cut n words into `lines` contiguous runs
        def cuts(start, left):
            if left == 1:
                yield [words[start:]]
                return
            for i in range(start + 1, n - left + 2):
                for rest in cuts(i, left - 1):
                    yield [words[start:i]] + rest
        for cut in cuts(0, lines):
            widest = max(_em(' '.join(run)) for run in cut)
            best = max(best, min(avail / (widest * 1.03), max_h / lines, cap))
    return best


# ───────────────────────── the page
def render(d: dict) -> str:
    P = _palette(d)
    lang = d.get('lang') or 'en'
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    hero = d.get('hero') or {}
    place = d.get('place') or {}
    menu = place.get('menu') or {}
    addr = place.get('address') or {}
    hours = [h for h in (place.get('hours') or []) if h.get('days') or h.get('open')]
    phone = place.get('phone') or {}
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    cta = d.get('cta') or {}
    statement = d.get('statement') or {}
    steps = d.get('steps') or {}
    foot = d.get('foot') or {}
    close = d.get('close') or {}

    # ── photographs: the template CHOOSES for each slot by role, size and proportion; each picture is used once; a
    # small one is never a backdrop and never shown above its own pixels; a slot that finds no fitting picture is left out.
    photos = [dict(p) for p in ((d.get('media') or {}).get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
    by_src = {p['src']: p for p in photos}
    used, stems = set(), set()
    area = lambda p: p['w'] * p['h']
    stem = lambda p: re.sub(r'(-\d+)?\.\w+$', '', p['src'].rsplit('/', 1)[-1])     # "arroz-2.jpg" is "arroz" again

    def use(p):
        used.add(p['src'])
        stems.add(stem(p))
        return p

    def free(pred=lambda p: True, fresh=True):
        return [p for p in photos if p['src'] not in used and (not fresh or stem(p) not in stems) and pred(p)]

    def fits(p, w, h):                                   # can p cover a w×h box without being enlarged?
        return p['w'] >= w and p['h'] >= h

    def by_page(h, w=379, hh=300):
        """a picture the client's own site shows on the page this item links to"""
        c = free(lambda p: h and p.get('page') == h and fits(p, w, hh), fresh=False)
        return use(max(c, key=area)) if c else None

    sections = [s for s in (menu.get('sections') or []) if s.get('t')]
    lists = [s for s in (menu.get('lists') or []) if s.get('t')]
    spaces = [dict(s) for s in (place.get('spaces') or [])]
    if not spaces:
        spaces = [dict(title=i.get('title'), text=i.get('text') or i.get('k'), img=i.get('img'), cta=i.get('cta'))
                  for i in (steps.get('items') or []) if i.get('title')]
    spaces = spaces[:6]
    for s in spaces:                                    # a room keeps the picture the data gives it
        if s.get('img') in by_src:
            use(by_src[s['img']])
    # opening backdrop: the largest picture of the place (room or outside, then bar, then anything that is not a dish)
    # that covers 1440×900 with the least enlarging (none if possible, never more than a quarter, under the veil)
    hero_ph = None
    for roles in (('room', 'exterior'), ('bar',), ('people', 'other')):
        c = [(max(1440 / p['w'], 900 / p['h'], 1), -area(p), p) for p in free(lambda p: not p.get('small') and p.get('role') in roles)]
        c = [x for x in c if x[0] <= 1.25]
        if c:
            hero_ph = use(min(c, key=lambda x: x[:2])[2])
            break
    # the band under the changing heading (1440×587): a landscape picture at least as wide as the page — a dish first,
    # then someone serving, then anything else; a dish a little narrower (1100px) only when there is nothing wider
    band_ph = None
    order = {'dish': 0, 'people': 1, 'other': 2, 'bar': 3}
    c = free(lambda p: not p.get('small') and p['w'] >= 1398 and p['w'] / p['h'] >= 1.3 and p.get('role') in order)
    if c:
        band_ph = use(min(c, key=lambda p: (order[p['role']], -area(p))))
    else:
        c = free(lambda p: not p.get('small') and p['w'] >= 1100 and p['w'] / p['h'] >= 1.3 and p.get('role') == 'dish')
        if c:
            band_ph = use(max(c, key=area))
    # rooms without a picture of their own, menu sections and priced dishes take a picture from the page they link to
    for s in spaces:
        if not s.get('img') or s['img'] not in by_src:
            p = by_page((s.get('cta') or {}).get('h'))
            s['img'] = p['src'] if p else None
    sec_ph = {}
    for i, s in enumerate(sections):
        if not s.get('items'):
            p = by_page(s.get('h'))
            if p:
                sec_ph[i] = p
    item_ph = {}
    for s in sections:
        for it in s.get('items') or []:
            slug = (it.get('h') or '').rstrip('/').rsplit('/', 1)[-1]
            # the dish's own address ("…/la-tarta-de-queso/") against the picture's file name ("postre-tarta-de-queso.jpg"):
            # one must contain the other (the file name without its first word), six letters at least
            def same(p):
                st = stem(p)
                tail_ = st.split('-', 1)[1] if '-' in st else st
                return len(slug) >= 6 and (slug in st or (len(tail_) >= 6 and tail_ in slug))
            c = free(lambda p: same(p) and fits(p, 379, 300), fresh=False)
            if c:
                item_ph[id(it)] = use(max(c, key=area))
    # the moving strip: four to eight pictures, dishes first, no dish twice
    c = sorted(free(lambda p: min(p['w'], p['h']) >= 300), key=lambda p: (p.get('role') != 'dish', -min(area(p), 360000)))
    strip = []
    for p in c:
        if len(strip) < 8 and stem(p) not in stems:
            strip.append(use(p))
    if len(strip) < 4:
        for p in strip:
            used.discard(p['src'])
            stems.discard(stem(p))
        strip = []
    # the loose pile: six to fourteen of what is left, the largest first (they take the largest frames), a second
    # view of a dish only after every dish has been seen once
    collage = []
    for fresh in (True, False):
        for p in sorted(free(lambda p: min(p['w'], p['h']) >= 150, fresh=False), key=lambda p: -area(p)):
            if len(collage) < 15 and p['src'] not in used and (not fresh or stem(p) not in stems):
                collage.append(use(p))
    collage.sort(key=lambda p: -area(p))
    if len(collage) < 6:
        for p in collage:
            used.discard(p['src'])
        collage = []
    social = [s for s in (place.get('social') or []) if s.get('t') and s.get('h')]
    dishes = [band_ph] if band_ph else []

    menu_h = menu.get('h')
    menu_t = _menu_label(d, menu_h)
    booking = place.get('booking') or hero.get('primary') or cta or {}
    main = dict(t=menu_t, h=menu_h) if menu_t else booking
    second = booking if (booking.get('h') and booking.get('h') != main.get('h')) else (place.get('takeaway') or {})
    if second.get('h') == main.get('h'):
        second = {}

    # ── top bar
    if hours:
        h0 = hours[0]
        left = ' '.join(x for x in [h0.get('days'), '–'.join(x for x in [h0.get('open'), h0.get('close')] if x)] if x)
    else:
        left = phone.get('t') or ''
    city = ', '.join(x for x in [addr.get('city'), addr.get('region')] if x)
    where = hero.get('text2') if (hero.get('text2') and len(hero['text2']) <= 36) else (city or hero.get('text2') or '')
    bem = max(_em(name), 1)
    logo = brand.get('logo') if not hero_ph else None    # a mark of unknown tone is not laid on a photograph
    brand_html = (f'<img class="mark" src="{e(_src(logo))}" alt="" width="58" height="58">' if logo else '') + \
        f'<span class="bn" style="font-size:min(40px,{330 / bem:.1f}px,{(62 if not logo else 46) / bem:.2f}vw)">{e(name)}</span>'
    top = f'''<div class="top">
<div class="side">{e(left)}</div>
<div class="mid"><i class="dash"></i>{_a(brand.get('home'), brand_html, 'brand')}<i class="dash"></i></div>
<div class="side r">{e(where)}</div>
</div>'''

    # ── 1 opening
    title = hero.get('title') or name
    bg = ''
    if hero_ph:
        bg = (f'<div class="bg" data-slot="opening"><img src="{e(_src(hero_ph["src"]))}" alt="{e(hero_ph.get("alt"))}" '
              f'width="{hero_ph["w"]}" height="{hero_ph["h"]}" fetchpriority="high"></div><div class="veil"></div>')
    btn = ''
    if main.get('t'):
        btn = _a(main.get('h'), f'<span>{e(main["t"])}</span>{_ARROW}', 'gbtn')
    drop = _a(second.get('h'), e(second.get('t')), 'tlink') if second.get('t') else ''
    s_hero = f'''<header class="hero{'' if hero_ph else ' plain'}">
{bg}{top}
<div class="hw"><div class="hrow">{_display('h1', title, 'h1')}{f'<div class="hb">{btn}</div>' if btn else ''}</div>
{f'<p class="hwhere">{e(where)}</p>' if where else ''}</div>
{f'<div class="drop">{drop}</div>' if drop else ''}
</header>'''

    # ── 2 what is served: a script line, a heading that changes every two seconds, the dish photograph as a band
    names = [s.get('t') for s in (menu.get('sections') or []) if s.get('t')]
    groups = _groups(names) or _groups(place.get('cuisine') or []) or _groups(d.get('trust') or [])
    script = statement.get('title') or hero.get('kicker') or ''
    if not groups and script:
        groups, script = [script], (hero.get('kicker') or '')
    s_daily = ''
    if groups:
        lw = max(_longest(g) for g in groups) * 1.04
        tot = max(_em(g) for g in groups)
        k = 1 if tot <= 19 else max(.6, (19 / tot) ** .5)
        hid = ' aria-hidden="true"'
        gs = ''.join(f'<span class="g{" on" if i == 0 else ""}"{hid if i else ""}>{e(g)}</span>' for i, g in enumerate(groups))
        pic = ''
        if dishes:
            pic = '<div class="dpic" data-slot="served">' + ''.join(
                f'<img class="{"on" if i == 0 else ""}" src="{e(_src(p["src"]))}" alt="{e(p.get("alt"))}" width="{p["w"]}" '
                f'height="{p["h"]}" loading="lazy">' for i, p in enumerate(dishes)) + '</div>'
        s_daily = f'''<section class="daily{'' if dishes else ' nopic'}">
<div class="dhead">{f'<p class="script">{e(script)}</p>' if script else ''}
<h2 class="h2c" style="--lw:{lw:.3f};--k:{k:.3f}">{gs}</h2>
{f'<p class="dtext">{e(hero.get("text"))}</p>' if hero.get('text') else ''}</div>
{pic}</section>'''

    def spans(n):
        """columns go three to a row as in the reference; a last row of two shares the width, and four are two and two"""
        if n <= 3:
            return ['' for _ in range(n)]
        halves = 2 if n % 3 == 2 else (4 if n % 3 == 1 else 0)
        return ['' for _ in range(n - halves)] + [' half' for _ in range(halves)]

    # ── 3 the coloured band: rooms (picture over a dashed card), the moving strip, the menu, the rows
    blocks = []
    if spaces:
        pics = [by_src[s['img']] for s in spaces if s.get('img') in by_src]
        # no picture is enlarged: every picture box takes the reference's 400px, or less when one of them is lower
        ph_h = min([400] + [p['h'] for p in pics])
        cols = []
        for s in spaces:
            p = by_src.get(s.get('img'))
            pic = ''
            if p:
                cap = f' style="max-width:{p["w"]}px"' if p['w'] < 760 else ''
                pic = (f'<div class="ph" data-slot="room"{cap}><img src="{e(_src(p["src"]))}" alt="{e(p.get("alt") or s.get("title"))}" '
                       f'width="{p["w"]}" height="{p["h"]}" loading="lazy"></div>')
            c = s.get('cta') or {}
            ttl = _a(c.get('h'), e(s.get('title')), 'cl') if c.get('h') else e(s.get('title'))
            txt = f'<p>{e(s.get("text"))}</p>' if s.get('text') else ''
            cols.append(f'<div class="col{spans(len(spaces))[len(cols)]} rv r50">{pic}<div class="card"><h3>{ttl}</h3>{txt}</div></div>')
        stamp_bits = [x for x in [name, place.get('since'), city] if x]
        stamp = ''
        if len(stamp_bits) >= 2:
            top_t, mid_t, bot_t = (stamp_bits + [''])[:3] if len(stamp_bits) == 3 else (stamp_bits[0], '', stamp_bits[1])
            stamp = f'''<svg class="stamp rv r164" viewBox="0 0 300 300" aria-hidden="true"><defs><path id="sa" d="M30 150a120 120 0 0 1 240 0"/><path id="sb" d="M62 172a92 92 0 0 1 176 0"/><path id="sc" d="M52 150a98 98 0 0 0 196 0"/></defs>
<text style="font-size:{min(23, 350 / (.74 * max(len(str(top_t)), 1))):.1f}px"><textPath href="#sa" startOffset="50%" text-anchor="middle">{e(str(top_t).upper())}</textPath></text>
<text class="s2"><textPath href="#sb" startOffset="50%" text-anchor="middle">{e(str(mid_t).upper())}</textPath></text>
<text style="font-size:{min(23, 290 / (.74 * max(len(str(bot_t)), 1))):.1f}px"><textPath href="#sc" startOffset="50%" text-anchor="middle">{e(str(bot_t).upper())}</textPath></text></svg>'''
        head = _display('h2', steps.get('title'), 'h2b rv r1') if steps.get('title') else ''
        sub = f'<p class="bsub">{e(steps.get("text"))}</p>' if steps.get('text') else ''
        blocks.append(f'''<div class="blk">{stamp}{head}{sub}
<div class="cols{' few' if len(cols) < 3 else ''}" style="--ph:{ph_h}px">{''.join(cols)}</div></div>''')

    if strip:
        items = []
        for i, p in enumerate(strip):
            thin = p['h'] > p['w'] * 1.15                       # upright pictures take the reference's narrow tilted frame
            w, h = (245, 312) if thin else (350, 300)
            if p.get('small'):
                w, h = min(w, p['w']), min(h, p['h'])
            items.append((w, f'<div class="mi{" thin" if thin else ""}" style="width:{w}px;height:{h}px"><img src="{e(_src(p["src"]))}" '
                             f'alt="{e(p.get("alt"))}" width="{p["w"]}" height="{p["h"]}" loading="lazy"></div>'))
        while sum(w + 40 for w, _ in items) < 1960:             # one run is as long as the reference's (1960px)
            items = items + items[:len(strip)]
        run = sum(w + 40 for w, _ in items)
        one = ''.join(h for _, h in items)
        two = one.replace('alt="', 'aria-hidden="true" data-alt="').replace('<div class="mi', '<div aria-hidden="true" class="mi')
        blocks.append(f'<div class="marq" data-slot="strip"><div class="mtrack" style="--run:{run}px;--dur:{run / 56.3:.1f}s;--durm:{run / 28.3:.1f}s">{one}{two}</div></div>')

    if sections or lists:
        def pcol(p, title, line, slot, half=''):
            cap = f' style="max-width:{p["w"]}px"' if p['w'] < 760 else ''
            return (f'<div class="col{half}"><div class="ph" data-slot="{slot}"{cap}><img src="{e(_src(p["src"]))}" alt="{e(p.get("alt"))}" '
                    f'width="{p["w"]}" height="{p["h"]}" loading="lazy"></div><div class="card"><h3>{title}</h3>{line}</div></div>')
        parts = []
        # sections with a picture of their own: the reference's column (picture over the dashed card)
        pc = []
        for i, s in enumerate(sections):
            if i in sec_ph:
                n = f'<p>{e(s.get("count"))}</p>' if s.get('count') not in (None, '') else ''
                pc.append(pcol(sec_ph[i], _a(s.get('h'), e(s['t']), 'cl') if s.get('h') else e(s['t']), n, 'menu',
                               spans(len(sec_ph))[len(pc)]))
        if pc:
            parts.append(f'<div class="cols rv r20" style="--ph:{min([400] + [p["h"] for p in sec_ph.values()])}px">{"".join(pc)}</div>')
        cards = []
        for i, s in enumerate(sections):
            if i not in sec_ph and not s.get('items'):
                n = f'<span class="n">{e(s.get("count"))}</span>' if s.get('count') not in (None, '') else ''
                cards.append(_a(s.get('h'), f'<h3>{e(s["t"])}</h3>{n}', 'card mc'))
        if cards:
            parts.append(f'<div class="mgrid rv r20">{"".join(cards)}</div>')
        for s in [s for s in sections if s.get('items')]:
            its = [i for i in s['items'] if i.get('name')]
            head = f'<h3 class="mh">{_a(s.get("h"), e(s["t"]), "cl") if s.get("h") else e(s["t"])}</h3>'
            with_p = [i for i in its if id(i) in item_ph]
            if with_p:
                ic = []
                for i in with_p:
                    line = ' · '.join(x for x in [i.get('price'), i.get('note')] if x)
                    ic.append(pcol(item_ph[id(i)], _a(i.get('h'), e(i['name']), 'cl') if i.get('h') else e(i['name']),
                                   f'<p>{e(line)}</p>' if line else '', 'dish', spans(len(with_p))[len(ic)]))
                parts.append(f'{head}<div class="cols rv r20" style="--ph:{min([400] + [item_ph[id(i)]["h"] for i in with_p])}px">{"".join(ic)}</div>')
                head = ''
            rest_i = [i for i in its if id(i) not in item_ph]
            if rest_i:
                rws = ''.join(f'<li>{_a(i.get("h"), e(i.get("name")), "nm")}<i></i><span class="pr">{e(i.get("price"))}</span></li>' for i in rest_i)
                notes = sorted({i.get('note') for i in rest_i if i.get('note')})
                note = f'<p class="note">{e(notes[0])}</p>' if len(notes) == 1 else ''
                parts.append(f'{head}<div class="mgrid rv r20"><div class="card ml"><ul>{rws}</ul>{note}</div></div>')
        if lists:
            rws = ''.join(f'<li>{_a(s.get("h"), e(s["t"]), "nm")}<i></i><span class="pr">{e(s.get("count"))}</span></li>'
                          if s.get('count') not in (None, '') else f'<li>{_a(s.get("h"), e(s["t"]), "nm")}</li>' for s in lists)
            parts.append(f'<div class="mgrid rv r20"><div class="card ml"><ul>{rws}</ul></div></div>')
        mt = menu_t or (d.get('features') or {}).get('title') or ''
        mhead = _display('h2', mt, 'h2b rv r1') if mt else ''
        mbtn = _a(menu_h, f'<span>{e(menu_t)}</span>{_ARROW}', 'sbtn') if menu_h and menu_t else ''
        more = f'<p class="mmore">{mbtn}</p>' if mbtn else ''
        blocks.append(f'<div class="blk menu" id="menu">{mhead}{"".join(parts)}{more}</div>')

    # questions and answers (the reference has none; a client's are never dropped): the reference's dashed card, one
    # per question, on the menu's grid
    fq = [q for q in ((d.get('faq') or {}).get('items') or []) if q.get('q') and q.get('a')]
    if fq:
        ft = (d.get('faq') or {}).get('title')
        fh = _display('h2', ft, 'h2b rv r1') if ft else ''
        fc = ''.join(f'<div class="card fq"><h3>{e(q["q"])}</h3><p>{e(q["a"])}</p></div>' for q in fq)
        blocks.append(f'<div class="blk">{fh}<div class="mgrid rv r20">{fc}</div></div>')

    rows = []                                           # three rows, as the reference: an event, links, the closing
    seen = {main.get('h')} if menu_t and (sections or lists) else set()
    ch = (close.get('cta') or {}).get('h')
    tail = []
    if close.get('title'):
        c = close.get('cta') or {}
        tail.append((close['title'], close.get('text'), c.get('t'), c.get('h')))
    for ev in (place.get('events') or [])[:1]:
        if ev.get('what'):
            c = ev.get('cta') or {}
            line = ' · '.join(x for x in [ev.get('when'), ev.get('price'), ev.get('where')] if x)
            rows.append((ev['what'], line, c.get('t'), c.get('h')))
    for l in sorted((d.get('links') or []), key=lambda l: 0 if l.get('d') else 1):
        if len(rows) + len(tail) >= 3:
            break
        if not l.get('t') or not l.get('h') or l['h'] in seen or l['h'] == ch or len(l.get('d') or '') > 160:
            continue
        seen.add(l['h'])
        rows.append((l['t'], l.get('d'), None, l['h']))
    rows += tail
    if rows:
        out = []
        for t, p, bt, bh in rows:
            if bh and bt:
                b = _a(bh, f'<span>{e(bt)}</span>{_ARROW}', 'sbtn')
            elif bh:
                b = _a(bh, _ARROW, 'sbtn ico', f' aria-label="{e(t)}"')
            else:
                b = ''
            pp = f'<p class="rv r20">{e(p)}</p>' if p else '<span></span>'
            bb = f'<div class="rv r20">{b}</div>' if b else ''
            out.append(f'<div class="row">{_display("h2", t, "h2r rv r05", 13.5)}<div class="r2">{pp}{bb}</div></div>')
        blocks.append(f'<div class="rows">{"".join(out)}</div>')
    s_band = f'<section class="band">{"".join(blocks)}</section>' if blocks else ''

    # ── 4 the loose pile of photographs (only with six photographs to spare)
    s_collage = ''
    if collage:
        # the reference's frames, largest first (measured places and turns; the one over the middle link is left out)
        slots = [(1072, 294, 380, 380, 4), (1104, 64, 339, 383, .7), (848, 47, 372, 266, -2.9), (542, 620, 376, 260, -.35),
                 (58, 193, 307, 307, 1), (273, -4, 242, 359, -1.9), (67, 408, 290, 290, -2.1), (536, 3, 370, 224, .7),
                 (258, 612, 295, 214, 4.3), (908, 594, 251, 251, -.2), (143, 592, 203, 308, -.1), (1079, 675, 229, 229, -2.2),
                 (1022, 468, 226, 165, 4.9), (6, 126, 206, 146, 2.3), (-2, 487, 155, 155, 1.9)]
        its = []
        for i, p in enumerate(collage):
            x, y, w, h, r = slots[i]
            if p.get('small'):
                w, h = min(w, p['w']), min(h, p['h'])
            its.append(f'<div class="ci" style="left:{x / 14.4:.2f}%;top:{y / 9:.2f}%;--w:{w}px;aspect-ratio:{w}/{h};--r:{r}deg;z-index:{i + 1}">'
                       f'<img src="{e(_src(p["src"]))}" alt="{e(p.get("alt"))}" width="{p["w"]}" height="{p["h"]}" loading="lazy" draggable="false"></div>')
        link = _a(social[0]['h'], e(social[0]['t']), 'clink') if social else ''
        s_collage = f'<section class="collage" data-slot="pile">{"".join(its)}{link}</section>'

    # ── 5 foot: the name at full width, two dashed cards (where / when), the last line
    c1 = []
    if city or addr.get('street'):
        if addr.get('city'):
            c1.append(f'<h3>{e(addr["city"])}</h3>')
        lines = [addr.get('street'), ' '.join(x for x in [addr.get('postcode'), addr.get('region') if addr.get('region') != addr.get('city') else ''] if x)]
        c1.append('<p>' + '<br>'.join(e(x) for x in lines if x) + '</p>')
    if phone.get('t'):
        c1.append(f'<p>{_a(phone.get("h"), e(phone["t"]), "ul")}</p>')
    if place.get('email'):
        c1.append(f'<p>{_a("mailto:" + place["email"], e(place["email"]), "ul")}</p>')
    c2 = []
    for h in hours:
        c2.append(f'<h3>{e(h.get("days"))}</h3><p>{e(" – ".join(x for x in [h.get("open"), h.get("close")] if x))}</p>')
    if social:
        c2.append('<p class="soc">' + ''.join(_a(s['h'], e(s['t']), 'ul') for s in social) + '</p>')
    cards = ''.join(f'<div class="fc rv r100"><div>{"".join(c)}</div></div>' for c in (c1, c2) if c)
    fsd, fsm = _wordmark(name, 92, 24, 21) if name else 0, _wordmark(name, 88, 40, 18) if name else 0
    legal = foot.get('legal') or foot.get('text') or ''
    flinks = ''.join(_a(l.get('h'), e(l.get('t')), 'ul') for l in (foot.get('links') or []) if l.get('t'))
    notices = ''
    for n in place.get('notices') or []:
        img = (f'<img src="{e(_src(n["img"]))}" alt="" width="{n.get("w") or ""}" height="{n.get("h") or ""}" loading="lazy" '
               f'style="max-width:min(100%,{min(int(n.get("w") or 320), 320)}px)">') if n.get('img') else ''
        notices += f'<div class="notice">{img}<div>{"".join(f"<p>{e(t)}</p>" for t in (n.get("text") or []))}</div></div>'
    s_foot = f'''<footer class="foot">
{f'<p class="wm rv r100" style="--fsd:{fsd:.2f}vw;--fsm:{fsm:.2f}vw">{e(name)}</p>' if name else ''}
{f'<div class="fcs">{cards}</div>' if cards else ''}
<div class="fl rv r20"><p>{e(legal)}</p><div class="flr">{flinks}<a class="up" href="#top" aria-label="{e(_TOP_WORD.get(lang, 'Top'))}">{_ARROW_UP}</a></div></div>
{notices}
</footer>'''

    # ── the pill fixed at the foot of the window
    links = list(nav)
    if cta.get('t') and cta.get('h') and all(n.get('h') != cta['h'] for n in links):
        links.append(cta)
    s_nav = ''
    if links:
        ll = ''.join(_a(n.get('h'), e(n['t']), 'nl') for n in links)
        word = e(_MENU_WORD.get(lang, 'Menu'))
        s_nav = f'''<div class="pillw" id="pill"><nav class="pill wide" aria-label="{word}">{ll}</nav>
<details class="pm"><summary class="pill" aria-label="{word}"><i class="bars"></i></summary>
<div class="ovl"><p class="obn">{e(name)}</p><nav aria-label="{word}">{ll}</nav></div></details></div>'''

    css = _CSS
    # the pill shows its links in a row only while the row fits the window (DM Mono at 18px is 10.8px a letter)
    pill_w = sum(len(n['t']) for n in links) * 10.8 + 20 * max(len(links) - 1, 0) + 120
    if pill_w + 40 > 992:
        css += ('@media (max-width:%dpx){.pill.wide{display:none}.pm{display:block;pointer-events:auto}'
                '.pillw.lift{bottom:60px}.pillw:has(.pm[open]){bottom:30px}}' % int(pill_w + 40))
    for k_, v in P.items():
        css = css.replace('{{' + k_ + '}}', v)
    desc = hero.get('text') or statement.get('text') or ''
    return f'''<!doctype html>
<html lang="{e(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)}</title>
<meta name="description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>{css}</style>
</head>
<body id="top">
{s_hero}
<main>
{s_daily}
{s_band}
{s_collage}
</main>
{s_foot}
{s_nav}
<script>{_JS}</script>
</body>
</html>
'''


_CSS = r'''
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:{{g}};color:{{ink}};font:500 15px/1.8 "DM Mono",ui-monospace,Menlo,monospace;overflow-x:hidden}
img{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
h1,h2,h3,p,ul{margin:0;padding:0}
ul{list-style:none}
:focus-visible{outline:3px solid currentColor;outline-offset:4px;border-radius:4px}
.h1,.h2b,.h2c,.h2r,.wm,.bn,.obn{font-family:Caprasimo,"Cooper Black",Georgia,serif;font-weight:400;line-height:1;letter-spacing:0}

/* 1 opening — 100vh, the photograph behind a black veil at .67, top bar, h1 on the grid's third column */
.hero{position:relative;min-height:100vh;display:flex;flex-direction:column;justify-content:center;color:#fff;overflow:hidden;padding:150px 0 130px}
.hero.plain{background:linear-gradient({{ba2}},{{ba}});color:{{on}}}
.hero .bg,.hero .veil{position:absolute;inset:0}
.hero .bg img{width:100%;height:100%;object-fit:cover}
.hero .veil{background:#000;opacity:.67}
.top{position:absolute;left:0;right:0;top:0;padding:50px 90px 0;display:flex;justify-content:space-between;align-items:center;gap:20px;font-size:14px;line-height:21px}
.top .side{flex:0 1 300px;min-width:0}
.top .mid{flex:1 1 auto;display:flex;align-items:center;justify-content:center;gap:10px;min-width:0}
.top .dash{flex:0 1 173px;min-width:24px;border-bottom:2px dashed currentColor}
.brand{display:flex;align-items:center;gap:12px;min-height:58px;white-space:nowrap}
.brand .mark{width:58px;height:58px;object-fit:contain;mix-blend-mode:multiply}
.hw{position:relative;padding:0 9.09vw;width:100%}
.hrow{display:flex;flex-wrap:wrap;align-items:flex-end;gap:24px 40px}
.h1{--cap:8vw;--avail:81.8vw;font-size:min(calc(var(--cap)*var(--k,1)),calc(var(--avail)/var(--lw)));max-width:100%}
.hb{padding-bottom:10px}
.hwhere{display:none;font-size:14px;line-height:1.4;margin-top:10px}
.gbtn{position:relative;display:inline-flex;align-items:center;gap:10px;padding:25px 40px;border-radius:14px;font-size:18px;line-height:24px;-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);color:inherit;isolation:isolate}
.gbtn::before{content:"";position:absolute;inset:0;border-radius:14px;padding:4px;background:linear-gradient(102deg,{{a}} 5%,{{a2}} 50.7%,{{t}} 92%);-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask:linear-gradient(#000 0 0) content-box exclude,linear-gradient(#000 0 0);transition:opacity .2s ease;z-index:-1}
.gbtn::after{content:"";position:absolute;inset:0;border-radius:14px;background:linear-gradient(45deg,{{pa}},{{pa2}},{{pt}},{{pa}},{{pa2}},{{pt}});opacity:0;transition:opacity .3s ease;z-index:-1}
.gbtn:hover,.gbtn:focus-visible{color:{{onp}}}
.gbtn:hover::after,.gbtn:focus-visible::after{opacity:1}
.gbtn .arw{transform:rotate(-45deg)}
.gbtn:active,.sbtn:active{transform:scale(.97)}
.drop{position:absolute;left:30px;bottom:55px}
.tlink{display:inline-block;padding:9px 0;font-size:15px;line-height:22.5px;border-bottom:2px solid {{a}};transition:border-color .2s ease}
.hero.plain .tlink{border-color:currentColor}
.tlink:hover{border-color:currentColor}

/* 2 what is served — script line tilted 2°, the changing heading at 8vw centred, the dish as a band where the
   reference turns its wheel of cut-outs */
.daily{background:{{g}};padding-top:100px;overflow:hidden}
.daily.nopic{padding-bottom:120px}
.dhead{padding:0 30px;text-align:center}
.script{font:400 60px/1 Yesteryear,"Brush Script MT",cursive;color:{{ad}};transform:rotate(-2deg);margin-bottom:-6px;padding:0 0 6px}
.h2c{--cap:8vw;--avail:calc(100vw - 60px);font-size:min(calc(var(--cap)*var(--k,1)),calc(var(--avail)/var(--lw)));display:grid;text-wrap:balance}
.h2c .g{grid-area:1/1;opacity:0;transition:opacity .2s ease}
.h2c .g.on{opacity:1}
.dtext{max-width:700px;margin:34px auto 0}
.dpic{position:relative;height:40.8vw;margin-top:60px}
.dpic img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .5s ease-in-out}
.dpic img.on{opacity:1}

/* 3 the coloured band — gradient top to foot, 15vw of air, content on a 22-column grid (side 9.09vw) */
.band{background:linear-gradient({{ba2}},{{ba}});color:{{on}};padding:15vw 0;position:relative;overflow:hidden}
.blk{position:relative;margin:0 9.09vw}
.blk+.blk,.marq+.blk{margin-top:200px}
.h2b{--cap:8vw;--avail:81.8vw;font-size:min(calc(var(--cap)*var(--k,1)),calc(var(--avail)/var(--lw)));max-width:72%;padding-top:20px;position:relative}
.bsub{max-width:700px;margin-top:22px;position:relative}
.stamp{position:absolute;right:12px;top:-91px;width:306px;height:306px;opacity:.14;fill:currentColor;font:500 23px "DM Mono",monospace;letter-spacing:.14em;rotate:14deg;pointer-events:none}
.stamp .s2{font-size:27px}
.cols{display:grid;grid-template-columns:repeat(6,1fr);gap:20px;margin-top:50px}
.col{grid-column:span 2}
.col.half{grid-column:span 3}
.col{display:flex;flex-direction:column;gap:20px;min-width:0}
.ph{height:var(--ph,400px);border-radius:15px;overflow:hidden;width:100%}
.ph img{width:100%;height:100%;object-fit:cover}
.card{position:relative;border:1px dashed currentColor;border-radius:15px;padding:80px 55px;overflow:hidden;flex:1;isolation:isolate}
.card::before{content:"";position:absolute;inset:0;background:{{t}};opacity:.25;mix-blend-mode:multiply;z-index:-1}
.card h3,.fc h3{font:700 26px/30px "Archivo Narrow","Arial Narrow",sans-serif;text-transform:uppercase}
.card h3+p{margin-top:10px}
.cl{border-bottom:2px solid transparent;transition:border-color .2s ease}
.cl:hover{border-color:currentColor}
.marq{padding-top:200px;overflow:hidden}
.mtrack{display:flex;gap:40px;width:max-content;align-items:center;animation:marq var(--dur) linear infinite}
.mi{flex:none;border-radius:10px;overflow:hidden}
.mi.thin{transform:rotate(-3deg)}
.mi img{width:100%;height:100%;object-fit:cover}
@keyframes marq{to{transform:translateX(calc(-1*var(--run)))}}
.mgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:50px}
.mc{display:flex;justify-content:space-between;align-items:baseline;gap:16px;padding:34px 55px;transition:background-color .2s ease}
.mc .n{font-size:15px}
a.mc:hover::before{opacity:.5}
.ml{grid-column:1/-1;padding:55px}
.ml ul{columns:2;column-gap:60px;margin-top:14px}
.ml ul:first-child{margin-top:0}
.ml li{display:flex;align-items:baseline;gap:10px;break-inside:avoid;padding:3px 0}
.ml li i{flex:1;border-bottom:2px dashed currentColor;opacity:.55;min-width:20px;transform:translateY(-4px)}
.ml .nm{border-bottom:2px solid transparent;transition:border-color .2s ease}
.ml a.nm:hover{border-color:currentColor}
.ml .note{font-size:13px;margin-top:14px}
.mmore{margin-top:40px}
.fq{grid-column:1/-1;padding:45px 55px}
.mh{font:700 26px/30px "Archivo Narrow","Arial Narrow",sans-serif;text-transform:uppercase;margin-top:70px}
.mh+.cols,.mh+.mgrid{margin-top:20px}
.menu .cols+.mgrid,.menu .mgrid+.mgrid,.menu .cols+.cols,.menu .mgrid+.cols{margin-top:20px}
.ph{margin:0 auto}
.rows{margin:0 13.61vw;padding-top:200px}
.row{position:relative;border-bottom:2px dashed currentColor;padding:50px 0 31px}
.row:first-child{padding-top:50px}
.h2r{--cap:6vw;--avail:72.7vw;font-size:min(calc(var(--cap)*var(--k,1)),calc(var(--avail)/var(--lw)))}
.r2{display:flex;justify-content:space-between;align-items:flex-end;gap:10px 40px;margin-top:51px;min-height:58px}
.r2 p{max-width:700px}
.sbtn{display:inline-flex;align-items:center;justify-content:center;gap:10px;position:relative;padding:15px 30px;border:2px solid {{ad}};border-radius:10px;background:{{ad}};color:{{ado}};font-size:16px;line-height:24px;white-space:nowrap;isolation:isolate;transition:border-color .3s ease,color .3s ease}
.sbtn.ico{padding:15px 17px}
.sbtn::after{content:"";position:absolute;inset:-2px;border-radius:10px;background:linear-gradient(45deg,{{pa}},{{pa2}},{{pt}},{{pa}},{{pa2}},{{pt}});opacity:0;transition:opacity .3s ease;z-index:-1}
.sbtn:hover,.sbtn:focus-visible{color:{{onp}};border-color:{{on}}}
.sbtn:hover::after,.sbtn:focus-visible::after{opacity:1}

/* 4 the pile — one screen high, pictures laid loose (radius 20, a few degrees), may be dragged */
.collage{position:relative;height:900px;background:{{pile}};overflow:hidden;display:flex;align-items:center;justify-content:center}
.ci{position:absolute;width:var(--w);border-radius:20px;overflow:hidden;transform:rotate(var(--r));cursor:grab;touch-action:none;user-select:none}
.ci.drag{cursor:grabbing}
.ci img{width:100%;height:100%;object-fit:cover;pointer-events:none}
.clink{position:relative;z-index:40;font:700 26px/1 "Archivo Narrow","Arial Narrow",sans-serif;text-transform:uppercase;color:{{ad}};background:{{pile}};padding:10px 14px 6px;border-bottom:2px solid {{ad}}}

/* 5 foot */
.foot{background:linear-gradient({{ba2}},{{ba}});color:{{on}};overflow:hidden;padding-bottom:110px}
.wm{font-size:var(--fsd);text-align:center;padding:30px 2vw 121px;text-wrap:balance}
.fcs{display:flex;justify-content:flex-end;gap:15px;margin:0 65px}
.fc{position:relative;flex:0 0 320px;min-height:288px;border:2px dashed currentColor;border-radius:15px;padding:50px 30px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:14px;line-height:20px;isolation:isolate}
.fc::before{content:"";position:absolute;inset:0;border-radius:13px;background:{{t}};opacity:.25;mix-blend-mode:multiply;z-index:-1}
.fc h3{font-size:22px;line-height:22px;margin:20px 0 15px}
.fc h3:first-child{margin-top:0}
.fc p+p{margin-top:20px}
.fc .soc{display:flex;flex-wrap:wrap;justify-content:center;gap:6px 18px}
.fc p+.soc,.fc h3+.soc{margin-top:22px}
.ul{border-bottom:2px solid transparent;transition:border-color .2s ease}
a.ul:hover{border-color:currentColor}
.fl{display:flex;justify-content:space-between;align-items:center;gap:20px 30px;margin:185px 65px 0;min-height:50px;font-size:14px;line-height:20px}
.fcs+.fl{margin-top:185px}
.flr{display:flex;align-items:center;gap:10px 30px;flex-wrap:wrap;justify-content:flex-end}
.up{flex:none;width:50px;height:50px;border:2px solid currentColor;border-radius:50%;display:flex;align-items:center;justify-content:center;transition:background-color .3s ease}
.notice{display:flex;gap:30px;align-items:flex-start;margin:70px 65px 0;font-size:13px;line-height:20px}
.notice img{flex:none;border-radius:6px;height:auto}
.notice p+p{margin-top:8px}
.notice div{max-width:760px}

/* the pill — fixed at the foot of the window, lifts 30px once the page is scrolled, sits back down at the foot */
.pillw{position:fixed;left:0;right:0;bottom:0;display:flex;justify-content:center;z-index:60;pointer-events:none;transition:bottom .2s ease}
.pillw.lift{bottom:30px}
.pill{pointer-events:auto;display:flex;align-items:center;gap:20px;padding:20px 60px;border-radius:10px;background:linear-gradient(102deg,{{pa}} 5%,{{pa2}} 50%,{{pt}} 92%);color:{{onp}};font-size:18px;line-height:1;max-width:calc(100vw - 20px)}
.nl{padding-bottom:5px;border-bottom:3px solid transparent;white-space:nowrap;transition:border-color .2s ease}
.nl:hover{border-color:currentColor}
.pm{display:none}
.pm summary{list-style:none;cursor:pointer;padding:10px 30px;position:relative;z-index:2}
.pm summary::-webkit-details-marker{display:none}
.bars{display:block;width:24px;height:18px;background:linear-gradient(currentColor,currentColor) 0 0/100% 2px no-repeat,linear-gradient(currentColor,currentColor) 0 50%/100% 2px no-repeat,linear-gradient(currentColor,currentColor) 0 100%/100% 2px no-repeat}
.pm[open] .bars{background:linear-gradient(currentColor,currentColor) 50% 50%/100% 2px no-repeat;transform:rotate(45deg);position:relative}
.pm[open] .bars::after{content:"";position:absolute;inset:0;background:linear-gradient(currentColor,currentColor) 50% 50%/100% 2px no-repeat;transform:rotate(90deg)}
.pm[open] summary{background:none;color:{{ovl_on}}}
.ovl{position:fixed;inset:0;background:linear-gradient({{ovl}},{{ovl2}});color:{{ovl_on}};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;padding:60px 20px 110px;overflow:auto;pointer-events:auto;animation:ovl .4s ease}
.ovl nav{display:flex;flex-direction:column;align-items:center;gap:14px;text-align:center}
.ovl .nl{font-size:min(36px,7.6vw);line-height:1.25;white-space:normal}
.obn{font-size:min(40px,9vw);text-align:center;margin-bottom:10px}
@keyframes ovl{from{opacity:0}}

/* entrances (measured: each rises its own height, or half, or 20px, and fades in once, about .7s) — only with scripts */
html.js .rv{opacity:0;transform:translateY(var(--ry,20px));transition:opacity .7s cubic-bezier(.22,.61,.36,1),transform .7s cubic-bezier(.22,.61,.36,1)}
html.js .rv.r1{--ry:1em}
html.js .rv.r05{--ry:.5em}
html.js .rv.r50{--ry:50%}
html.js .rv.r100{--ry:100%}
html.js .rv.r164{--ry:164px;opacity:.14}
html.js .rv.in{opacity:1;transform:none}
html.js .stamp.rv.in{opacity:.14}

@media (max-width:991px){
  .pill.wide{display:none}
  .pm{display:block;pointer-events:auto}
  .pillw.lift{bottom:60px}
  .pillw:has(.pm[open]){bottom:30px}
  .cols{grid-template-columns:repeat(6,1fr)}
  .col,.col.half{grid-column:span 3}
  .mgrid{grid-template-columns:repeat(2,1fr)}
  .top{padding:50px 30px 0}
  .fcs{justify-content:center}
}
@media (max-width:767px){
  .hero{padding:212px 0 150px;justify-content:center}
  .top{flex-direction:column-reverse;gap:30px;padding:50px 30px 0}
  .top .side{flex:none;text-align:center}
  .top .side.r{display:none}
  .top .mid{width:100%}
  .top .dash{flex:1 1 30px;max-width:60px}
  .hw{padding:0 20px}
  .h1{--cap:16.67vw;--avail:calc(100vw - 40px)}
  .hb{display:none}
  .hwhere{display:block}
  .drop{bottom:50px}
  .daily{padding-top:80px}
  .daily.nopic{padding-bottom:80px}
  .script{font-size:40px;transform:rotate(-3deg)}
  .h2c{--cap:13vw}
  .dtext{margin-top:24px}
  .dpic{height:57.7vw;margin-top:40px}
  .blk{margin:0 20px}
  .blk+.blk,.marq+.blk{margin-top:80px}
  .h2b{--cap:11.54vw;--avail:calc(100vw - 40px);max-width:100%}
  .stamp{width:210px;height:210px;right:7px;top:-21px}
  .cols,.mgrid{grid-template-columns:1fr;margin-top:35px}
  .col,.col.half{grid-column:auto}
  .ph{height:min(var(--ph,275px),275px)}
  .card{padding:50px 35px}
  .mc{padding:26px 35px}
  .ml{padding:40px 35px}
  .ml ul{columns:1}
  .marq{padding-top:80px}
  .mtrack{animation-duration:var(--durm)}
  .rows{margin:0 20px;padding-top:50px}
  .h2r{--cap:10.26vw;--avail:calc(100vw - 40px)}
  .r2{flex-direction:column;align-items:flex-start;gap:20px;margin-top:20px}
  .collage{height:844px}
  .ci{width:calc(var(--w)*.62)}
  .foot{padding-top:70px;padding-bottom:120px}
  .wm{font-size:var(--fsm);padding:30px 20px 0}
  .fcs{flex-direction:column;margin:15px 20px 0}
  .fc{flex:none;min-height:0;padding:30px}
  .fl,.fcs+.fl{flex-direction:column-reverse;margin:50px 20px 0;gap:21px;text-align:center}
  .flr{flex-direction:column-reverse;justify-content:center;gap:19px}
  .notice{flex-direction:column;margin:50px 20px 0}
}
@media (prefers-reduced-motion:reduce){

  *,*::before,*::after{transition:none!important;animation:none!important}
}
'''

_JS = r'''(function(){
var D=document,R=D.documentElement,still=matchMedia('(prefers-reduced-motion:reduce)').matches;
/* the pill lifts once the page is scrolled and sits down again when the foot is on screen */
var pill=D.getElementById('pill'),foot=D.querySelector('.foot');
function lift(){if(!pill)return;var end=foot&&foot.getBoundingClientRect().top<innerHeight-170;pill.classList.toggle('lift',scrollY>75&&!end)}
addEventListener('scroll',lift,{passive:true});lift();
var pm=D.querySelector('.pm');if(pm){pm.addEventListener('click',function(ev){if(ev.target.closest('.ovl a'))pm.open=false});D.addEventListener('keydown',function(ev){if(ev.key==='Escape')pm.open=false})}
/* the pile: every picture can be dragged; the one taken comes to the top */
var z=20;[].forEach.call(D.querySelectorAll('.ci'),function(el){var sx,sy,ox=0,oy=0,on=false;
el.addEventListener('pointerdown',function(ev){on=true;sx=ev.clientX-ox;sy=ev.clientY-oy;el.style.zIndex=++z<39?z:(z=20);el.classList.add('drag');el.setPointerCapture(ev.pointerId)});
el.addEventListener('pointermove',function(ev){if(!on)return;ox=ev.clientX-sx;oy=ev.clientY-sy;el.style.translate=ox+'px '+oy+'px'});
function end(){on=false;el.classList.remove('drag')}el.addEventListener('pointerup',end);el.addEventListener('pointercancel',end)});
if(still)return;
R.classList.add('js');
/* entrances, once */
var rv=[].slice.call(D.querySelectorAll('.rv'));
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}})},{rootMargin:'0px 0px -12% 0px'});
rv.forEach(function(el){var p=el.parentElement;io.observe(el.classList.contains('r100')||el.classList.contains('r50')||el.classList.contains('r164')?p:el);if(p!==el&&(el.classList.contains('r100')||el.classList.contains('r50')||el.classList.contains('r164'))){new IntersectionObserver(function(es,o){es.forEach(function(x){if(x.isIntersecting){el.classList.add('in');o.disconnect()}})},{rootMargin:'0px 0px -12% 0px'}).observe(p)}})}
else rv.forEach(function(el){el.classList.add('in')});
setTimeout(function(){rv.forEach(function(el){if(el.getBoundingClientRect().top<0)el.classList.add('in')})},1200);
addEventListener('scroll',function(){rv.forEach(function(el){if(!el.classList.contains('in')&&el.parentElement.getBoundingClientRect().top<innerHeight*.5)el.classList.add('in')})},{passive:true});
/* the heading changes every two seconds (measured), the dish with it when there are several */
var gs=D.querySelectorAll('.h2c .g'),ps=D.querySelectorAll('.dpic img'),i=0;
if(gs.length>1)setInterval(function(){gs[i].classList.remove('on');if(ps.length>1)ps[i%ps.length].classList.remove('on');i=(i+1)%gs.length;gs[i].classList.add('on');if(ps.length>1)ps[i%ps.length].classList.add('on')},2000);
})();'''
