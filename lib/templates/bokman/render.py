"""bokman/render.py — one pure function: render(d) -> a complete page. A template for PLACES.

The build (section order, 12-column grid, measures, type scale, spacing, motion, phone build) was measured on the
reference's home page (and, for text modules without a picture and for label/content rows, on its about and contact
pages) at 1440 and 390 on 2026-11-12 — see NOTES.md. Nothing of the reference's code, words, pictures, logo, seal or
typeface is here. The client's data fills it; a section whose data is missing is left out whole.
No model call, no file reads, no client logic.
"""
import html

FONTS = 'https://fonts.googleapis.com/css2?family=Arimo:ital,wght@0,400;0,700;1,400&display=swap'
MEDIA = '../../'


# ───────────────────────── colour: the reference is ONE colour and the ground (text in it, a band of it)
def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def _con(a, b):
    x, y = _lum(a), _lum(b)
    return (max(x, y) + .05) / (min(x, y) + .05)


def _chroma(h):
    c = _rgb(h)
    return max(c) - min(c)


def _reads(col, ground, want=4.9):
    """the colour moved along its own hue (toward black on a light ground, toward white on a dark one) until it
    reads on the ground at `want`:1 — the same colour then also carries ground-coloured text as a band"""
    c = list(_rgb(col))
    dark_ground = _lum(ground) < .2
    for _ in range(60):
        if _con(_hex(c), ground) >= want:
            break
        c = [v + (255 - v) * .06 for v in c] if dark_ground else [v * .95 for v in c]
    return _hex(c)


# ───────────────────────── fitting the wordmark: advance widths of Arimo Bold capitals (per 1000 units)
_W = dict(A=722, B=722, C=722, D=722, E=667, F=611, G=778, H=722, I=278, J=556, K=722, L=611, M=833, N=722, O=778,
          P=667, Q=778, R=722, S=667, T=611, U=722, V=667, W=944, X=667, Y=667, Z=611)
_W.update({' ': 278, '&': 722, '@': 975, '.': 278, ',': 278, '-': 333, "'": 238, '!': 333, '?': 611, ':': 333,
           '/': 278, '·': 333, '«': 556, '»': 556, '€': 556, '+': 584})
_FOLD = str.maketrans('ÁÀÂÄÃÅÉÈÊËÍÌÎÏÓÒÔÖÕÚÙÛÜÑÇ', 'AAAAAAEEEEIIIIOOOOOUUUUNC')
TRACK = -.01           # em, the wordmark's tracking


def _em(s):
    s = s.upper().translate(_FOLD)
    return sum(_W.get(ch, 556) for ch in s) / 1000 + TRACK * len(s)


def _fit(text, slot_px, max_lines=3, tall_px=236, cap_px=155, lh=.86):
    """break `text` into the lines that give the largest size with the widest line filling `slot_px`
    (measured at 1440: the reference's wordmark fills its 684px column and its capitals are 111px high).
    Returns (lines, size_px at 1440)."""
    words = text.split()
    best = ([text], 0)
    n = len(words)

    def splits(k, start=0):
        if k == 1:
            yield [' '.join(words[start:])]
            return
        for i in range(start + 1, n - k + 2):
            for rest in splits(k - 1, i):
                yield [' '.join(words[start:i])] + rest
    for k in range(1, min(max_lines, n) + 1):
        for lines in splits(k):
            size = min(slot_px / max(_em(x) for x in lines) * .975, cap_px, tall_px / (k * lh))
            if size > best[1] * 1.12:          # another line only when it buys real size
                best = (lines, size)
        if best[1] >= cap_px * .6:             # large enough: the reference's is one line; do not stack further
            break
    return best


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def _a(t, h, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<a{c} href="{e(h)}">{e(t)}</a>' if h else f'<span{c}>{e(t)}</span>'


def _img(p, cls='', lazy=True, alt=None):
    a = e(p.get('alt', '') if alt is None else alt)
    return (f'<img{(" class=" + chr(34) + cls + chr(34)) if cls else ""} src="{MEDIA}{e(p["src"])}" width="{p["w"]}" '
            f'height="{p["h"]}" alt="{a}"{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""} decoding="async">')


def _clampr(p):
    return max(.75, min(4 / 3, p['w'] / p['h']))


def _stem(p):
    import re
    return re.sub(r'[-_]?\d+$', '', p['src'].rsplit('/', 1)[-1].rsplit('.', 1)[0])


def _pick_nohalf(photos):
    return _pick([dict(p, _nohalf=True) for p in photos])


def _pick(photos):
    """which photograph stands where — returns (opening pair, wide picture, strip, strip height desk, phone).
    Opening: two that are large enough for a half-screen column (the reference's are 684×729 at 1440): a dish on the
    left as in the reference, the most upright picture of another kind on the right.
    Wide: up to two landscapes of at least 1200px, each only while a strip of three is still left.
    Strip: up to eight, at the reference's 480px (phone 320) and its two shapes (3:4, 4:3) when at least four
    pictures are tall enough for that; otherwise all that is left, at their own shape, as high as the lowest of them."""
    big = [p for p in photos if not p.get('small') and p.get('h', 0) >= 700 and p.get('w', 0) >= 680]
    # the half beside the text (reference: 684×912, here bled to the page edge: 708 wide at 1440, as tall as the module)
    # takes a photograph that fills it at its own pixels, the building or a room first, the most upright of them —
    # but only when two large ones are still left for the opening.
    half = None
    fills = [p for p in big if p['w'] >= 950 and p['h'] >= 912]
    if fills and len(big) >= 3 and not photos[0].get('_nohalf'):
        order = ('exterior', 'room', 'bar')
        fills.sort(key=lambda p: (order.index(p['role']) if p.get('role') in order else 9, -p['h'] / p['w']))
        half = fills[0]
        big = [p for p in big if p is not half and _stem(p) != _stem(half)]
    intro = []
    if len(big) >= 2:
        left = next((p for p in big if p.get('role') == 'dish'), None) or next((p for p in big if p.get('role') == 'other'), big[0])
        rest = [p for p in big if p is not left and _stem(p) != _stem(left)] or [p for p in big if p is not left]
        other = [p for p in rest if p.get('role') != left.get('role')] or rest
        right = max(other, key=lambda p: p['h'] / p['w'])
        intro = [left, right]
    elif half:
        half = None
        return _pick_nohalf(photos)
    rest = [p for p in photos if p not in intro and p is not half]
    wides = [p for p in rest if not p.get('small') and p['w'] >= 1200 and p['w'] / p['h'] >= 1.3]
    wides.sort(key=lambda p: p.get('role') not in ('room', 'exterior', 'bar'))
    wide = []
    for p in wides[:(1 if half else 2)]:         # with the half in place one band closes the page; without it, two
        if len(rest) - len(wide) - 1 >= 3:
            wide.append(p)
    rest = [p for p in rest if p not in wide]
    seen, uniq = {_stem(p) for p in intro + wide + ([half] if half else [])}, []
    for p in rest:                               # a second shot of the same thing is not shown beside the first
        if _stem(p) not in seen:
            seen.add(_stem(p))
            uniq.append(p)
    tall = [p for p in uniq if p['h'] >= 480 and p['w'] >= 480 * _clampr(p) - 1]
    if len(tall) >= 4:
        roles = []
        for p in tall:
            if p.get('role') not in roles:
                roles.append(p.get('role'))
        by = {r: [p for p in tall if p.get('role') == r] for r in roles}
        take = {r: 0 for r in roles}
        n = min(8, len(tall))
        while sum(take.values()) < n:
            for r in roles:
                if take[r] < len(by[r]) and sum(take.values()) < n:
                    take[r] += 1
        chosen = {r: [by[r][int(i * len(by[r]) / take[r])] for i in range(take[r])] for r in roles}
        strip = []
        while any(chosen.values()):
            for r in roles:
                if chosen[r]:
                    strip.append(chosen[r].pop(0))
        return intro, wide, [(p, _clampr(p)) for p in strip], 480, 320, half
    hmin = min([p['h'] for p in uniq] or [480])
    return intro, wide, [(p, max(.75, min(2.4, p['w'] / p['h']))) for p in uniq[:8]], min(480, hmin), min(320, hmin), half


# ───────────────────────── the page
def render(d: dict) -> str:
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    pal = d.get('palette') or {}
    G = pal.get('ground') or '#ffffff'
    C = _reads(pal.get('accent') or pal.get('ink') or '#222222', G)          # the one colour
    extra = [x for x in (pal.get('extra') or []) if _chroma(x) > 40]
    S = _reads(extra[0], G) if extra else _reads(pal.get('ink') or '#000000', G)   # the hover colour (reference: blue)
    light_ground = _lum(G) > .5
    hero = d.get('hero') or {}
    place = d.get('place') or {}
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    cta = place.get('booking') or d.get('cta') or hero.get('primary') or {}
    photos = [p for p in ((d.get('media') or {}).get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
    intro, wide, strip, strip_h, strip_hm, half = _pick(photos)
    logo = brand.get('logo')

    # ── opening: the name, and a second line in the place of the reference's second wordmark
    title = hero.get('title') or ''
    second = title if title and name.lower() not in title.lower() else (hero.get('kicker') or '')
    l1, s1 = _fit(name, 684)
    l2, s2 = _fit(second, 684 - (131 if logo else 0)) if second else ([], 0)

    def wm(lines, size, tag, cls):
        if not lines:
            return ''
        inner = ''.join(f'<span>{e(x)}</span>' for x in lines)
        return (f'<{tag} class="wm {cls}" style="--s:{size / 14.4:.3f}vw;--sv:{size / 9:.3f}vh">{inner}</{tag}>')
    mark = f'<img class="seal" src="{MEDIA}{e(logo)}" alt="" width="111" height="111">' if logo else ''
    wm1 = wm(l1, s1, 'h1', 'wm1')
    wm2 = f'<div class="wm2row">{wm(l2, s2, "p", "wm2")}{mark}</div>' if (l2 or mark) else ''
    if intro:
        opening = (f'<section class="intro pin" data-intro>'
                   f'<div class="col colL">{wm1}<div class="pic picL" data-slot="photo">{_img(intro[0], lazy=False)}</div></div>'
                   f'<div class="col colR"><div class="pic picR" data-slot="photo">{_img(intro[1], lazy=False)}</div>{wm2}</div>'
                   f'<div class="curtain" aria-hidden="true"></div></section>')
    else:
        opening = f'<section class="intro flat"><div class="col colL">{wm1}</div><div class="col colR">{wm2}</div></section>'

    # ── header
    def roll(t):
        return f'<span>{e(t)}</span><span aria-hidden="true">{e(t)}</span>'
    links = ''.join(f'<a class="roll" href="{e(n.get("h") or "#")}">{roll(n["t"])}</a>' for n in nav)
    book = f'<a class="pill" href="{e(cta.get("h") or "#")}">{e(cta["t"])}</a>' if cta.get('t') else ''
    logo_em = max(_em(name), 1)
    nav_txt = sum(_em(n['t']) for n in nav) * 14 * 1.01
    pill_w = (_em(cta['t']) + .143 * len(cta['t'])) * 14 + 42 if cta.get('t') else 0
    n_gaps = len(nav) - (0 if cta.get('t') else 1) + 1

    def head(w):                                # (gap, logo size) of the header row at width w
        free = w - 48 - 24 - nav_txt - pill_w
        gap = max(18, min(42, 42 * w / 1440, (free - logo_em * 26) / max(n_gaps, 1)))
        return gap, min(36, (free - n_gaps * gap) / logo_em)
    gap0, size0 = head(1440)

    def need(w):                                # the row as the stylesheet scales it between the turn and 1440
        size = max(19, min(36, size0 * w / 1440))
        gap = max(18, min(42, gap0 * w / 1440))
        return 48 + logo_em * size + 24 + nav_txt + pill_w + n_gaps * gap
    bp = 1448 if need(1440) > 1440 or size0 < 19 else 1440
    while bp == 1448 and bp < 2400 and need(bp) > bp:
        bp += 8
    while 768 < bp <= 1440 and need(bp - 8) <= bp - 8:
        bp -= 8
    bp = max(768, bp)
    header = (f'<header class="hdr" style="--lw:{logo_em:.3f};--ls:{size0 / 14.4:.3f}vw;--ng:{gap0 / 14.4:.3f}vw"><a class="logo" href="{e(brand.get("home") or "#")}">{e(name)}</a>'
              f'<nav class="nav" aria-label="{e(name)}">{links}{book}</nav>'
              f'<button class="trig" type="button" aria-expanded="false" aria-controls="ov" aria-label="{e(nav[0]["t"] if nav else name)}">'
              f'<svg viewBox="0 0 90 16" width="90" height="16" aria-hidden="true"><rect width="90" height="2"/><rect y="7" width="90" height="2"/><rect y="14" width="90" height="2"/></svg></button></header>')

    # ── phone overlay (reference: a full-screen panel of the one colour, rows ruled in the ground colour)
    addr = place.get('address') or {}
    addr_line = ' '.join(x for x in [addr.get('street'), addr.get('postcode'), addr.get('city')] if x)
    phone = place.get('phone') or {}
    rows = ''.join(f'<a class="ovr" href="{e(n.get("h") or "#")}"><span>{e(n["t"])}</span></a>' for n in nav)
    if cta.get('t'):
        rows += f'<a class="ovr" href="{e(cta.get("h") or "#")}"><span>{e(cta["t"])}</span></a>'
    small = ''
    if phone.get('t'):
        small += (f'<a class="ovs" href="{e(phone["h"])}"><span>{e(phone["t"])}</span></a>' if phone.get('h')
                  else f'<div class="ovs"><span>{e(phone["t"])}</span></div>')
    if addr_line:
        small += f'<div class="ovs"><span>{e(addr_line)}</span></div>'
    overlay = (f'<div class="ov" id="ov"><div class="ovh"><span class="ovn">{e(name)}</span>'
               f'<button class="ovx" type="button" aria-label="×"><svg viewBox="0 0 40 40" width="40" height="40" aria-hidden="true">'
               f'<path d="M1 1l38 38M39 1L1 39" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button></div>'
               f'<div class="ovl">{rows}</div><div class="ovb">{small}</div></div>')

    # ── band: one sentence large, then the strip of photographs
    band = ''
    if hero.get('text') or strip:
        hs = [strip_h, strip_hm]
        cells = ''.join(
            f'<div class="cell" data-slot="photo" style="--r:{r:.4f}">{_img(p)}</div>' for p, r in strip)
        gal = (f'<div class="strip" data-strip style="--h:{hs[0]}px;--hm:{hs[1]}px"><div class="track">{cells}</div></div>'
               if strip else '')
        copy = f'<p class="lede">{e(hero["text"])}</p>' if hero.get('text') else ''
        band = f'<section class="band{"" if strip else " bare"}">{copy}{gal}</section>'

    # ── text modules: headed blocks at 36px over 18px text, six columns of twelve
    def block(h, body):
        return f'<div class="blk"><h2>{e(h)}</h2>{body}</div>' if h and body else (f'<div class="blk">{body}</div>' if body else '')

    def find_label(href, fallback=''):
        for src in (nav, d.get('links') or []):
            for n in src:
                if href and n.get('h') == href and n.get('t'):
                    return n['t']
        return fallback

    st = d.get('statement') or {}
    b_about = block(st.get('title'), f'<p>{e(st["text"])}</p>' if st.get('text') else ('<p></p>' if st.get('title') else ''))
    if st.get('title') and not st.get('text'):
        b_about = f'<div class="blk"><h2>{e(st["title"])}</h2></div>'

    b_events = ''
    for ev in place.get('events') or []:
        if not ev.get('what'):
            continue
        ps = ''
        wl = ' · '.join(x for x in [ev.get('when'), ev.get('price')] if x)
        if wl:
            ps += f'<p>{e(wl)}</p>'
        if ev.get('where'):
            ps += f'<p>{e(ev["where"])}</p>'
        c = ev.get('cta') or {}
        if c.get('t') and c.get('h'):
            ps += f'<p>{_a(c["t"], c["h"])}</p>'
        b_events += f'<div class="blk"><h2>{e(ev["what"])}</h2>{ps}</div>'

    ps = ''
    hours = [h for h in (place.get('hours') or []) if h.get('days')]
    if hours:
        ps += '<p>' + '<br>'.join(
            e(h['days']) + ((' ' + e(h.get('open', '')) + '–' + e(h.get('close', ''))) if h.get('open') else '') for h in hours) + '</p>'
    if phone.get('t'):
        ps += f'<p>{_a(phone["t"], phone.get("h"))}{(" " + e(phone["note"])) if phone.get("note") and phone.get("h") else ""}</p>'
    if place.get('email'):
        ps += f'<p>{_a(place["email"], "mailto:" + place["email"])}</p>'
    al = [addr.get('street'), ' '.join(x for x in [addr.get('postcode'), addr.get('city')] if x),
          ', '.join(x for x in [addr.get('region'), addr.get('country')] if x)]
    al = [x for x in al if x]
    if al:
        ps += '<p>' + '<br>'.join(e(x) for x in al) + '</p>'
    elif (d.get('foot') or {}).get('text'):
        ps += f'<p>{e(d["foot"]["text"])}</p>'
    tk = place.get('takeaway') or {}
    mn = place.get('menu') or {}
    has_rows = any(x.get('t') for x in (mn.get('sections') or []) + (mn.get('lists') or []))
    ml = {'t': next((n['t'] for n in nav + (d.get('links') or []) if n.get('h') == mn.get('h') and n.get('t')), ''), 'h': mn.get('h')}
    lk = [_a(x['t'], x['h']) for x in ((cta, tk) if has_rows else (ml, cta, tk)) if x.get('t') and x.get('h')]
    if lk:
        ps += '<p>' + '<br>'.join(lk) + '</p>'
    contact_label = next((n['t'] for n in nav + (d.get('links') or []) if 'contact' in (n.get('h') or '').lower()), '') \
        or addr.get('name') or name
    b_contact = block(contact_label, ps)

    def rows_block(title, rws, tail=''):
        body = ''.join(f'<div class="row"><h3>{lab}</h3><div>{con}</div></div>' for lab, con in rws if con)
        return f'<div class="blk">{f"<h2>{e(title)}</h2>" if title else ""}<div class="rows">{body}</div>{tail}</div>' if body else ''

    steps = d.get('steps') or {}
    sp = []
    for s in (place.get('spaces') or steps.get('items') or []):
        c = s.get('cta') or {}
        con = e(s.get('text') or '') or (_a(c.get('t'), c.get('h')) if c.get('t') else '')
        if s.get('title') and con:
            sp.append((e(s['title']), con))
    b_spaces = rows_block(steps.get('title'), sp)

    menu = place.get('menu') or {}

    def line(l, r, h=None):
        return f'<div class="ln"><span>{_a(l, h)}</span>{f"<span class=num>{e(r)}</span>" if r not in (None, "") else ""}</div>'
    mr = []
    counted = [s for s in (menu.get('sections') or []) if s.get('t') and not s.get('items')]
    if counted:
        mr.append((e((d.get('features') or {}).get('title') or ''), ''.join(line(s['t'], s.get('count'), s.get('h')) for s in counted)))
    for s in (menu.get('sections') or []):
        its = [i for i in (s.get('items') or []) if i.get('name')]
        if not (s.get('t') and its):
            continue
        notes = {i.get('note') for i in its}
        con = ''.join(line(i['name'], i.get('price'), i.get('h')) for i in its)
        if len(notes) == 1 and its[0].get('note'):
            con += f'<div class="ln note"><span>{e(its[0]["note"])}</span></div>'
        mr.append((e(s['t']), con))
    lists = [s for s in (menu.get('lists') or []) if s.get('t')]
    if lists:
        mr.append(('', ''.join(line(s['t'], s.get('count'), s.get('h')) for s in lists)))
    sec = hero.get('secondary') or {}
    m_link = sec.get('t') if sec.get('h') == menu.get('h') and sec.get('t') else find_label(menu.get('h'))
    b_menu = rows_block(find_label(menu.get('h'), (d.get('features') or {}).get('title') or ''), mr,
                        f'<p class="more">{_a(m_link, menu.get("h"))}</p>' if m_link and menu.get('h') else '')

    faq = d.get('faq') or {}
    fq = [(e(q['q']), e(q.get('a') or '')) for q in (faq.get('items') or []) if q.get('q') and q.get('a')]
    b_faq = rows_block(faq.get('title') or '', fq) if fq else ''
    plans = d.get('plans') or {}
    pr = []
    for pl in plans.get('items') or []:
        if not pl.get('name'):
            continue
        con = line(pl.get('line') or pl['name'], ' '.join(x for x in [pl.get('price'), pl.get('per')] if x))
        con += ''.join(f'<div class="ln"><span>{e(r)}</span></div>' for r in (pl.get('rows') or []))
        c = pl.get('cta') or {}
        if c.get('t') and c.get('h'):
            con += f'<div class="ln"><span>{_a(c["t"], c["h"])}</span></div>'
        pr.append((e(pl['name']), con))
    b_plans = rows_block(plans.get('title') or '', pr, f'<p class="more">{e(plans["note"])}</p>' if plans.get('note') else '') if pr else ''

    # the reference's lower module is a picture in the left six columns and headed text in the right six. A picture is
    # never boxed beside text here (owner's rule), so the left six columns take the rows (rooms, menu) instead.
    right = ''.join(x for x in (b_about, b_events, b_contact) if x)
    left = ''.join(x for x in (b_spaces, b_menu, b_plans, b_faq) if x)
    if half and (right or left):
        # as the reference: the photograph is the left half, from the page edge to the middle gutter and as tall as
        # the module; all the text is the right six columns
        tm = (f'<section class="tm half"><div class="txt r">{right}{left}</div>'
              f'<div class="halfpic" data-slot="photo" style="--ph:{half["h"]}px">{_img(half)}</div></section>')
    else:
        if not right:
            right, left = left, ''
        lcol = '<div class="txt l">' + left + '</div>' if left else ''      # client text is never %-formatted
        tm = (f'<section class="tm"><div class="txt r">{right}</div>{lcol}</section>'
              if right else '')
    def band_pic(p):
        return (f'<section class="wide" data-slot="photo" style="--w:{p["w"]}px;--r:{max(1.5, min(16 / 9, p["w"] / p["h"])):.4f}">'
                f'{_img(p)}</section>')
    # the picture that stood beside the text stands above it across the page; a second one closes the page
    if half:
        mods = [band, tm, band_pic(wide[0]) if wide else '']
    else:
        mods = [band, band_pic(wide[0]) if wide else '', tm, band_pic(wide[1]) if len(wide) > 1 else '']
    main = f'<main class="mods">{"".join(m for m in mods if m)}</main>'

    # ── foot: one ruled-less row of small upper-case links on the twelve columns; then legally required notices
    foot = d.get('foot') or {}
    fl, seen = [], set()
    for x in (foot.get('links') or []) + (place.get('social') or []):
        if x.get('t') and x.get('h') and x['h'] not in seen:
            seen.add(x['h'])
            fl.append(x)
    cells = [f'<a href="{e(x["h"])}">{e(x["t"])}</a>' for x in fl]
    if len(cells) > 3 or logo:
        cells.insert(min(3, len(cells)), f'<span class="fmark">{f"<img src={chr(34)}{MEDIA}{e(logo)}{chr(34)} alt={chr(34)}{chr(34)} width=20 height=20>" if logo else ""}</span>')
    if foot.get('legal'):
        cells.append(f'<span class="legal">{e(foot["legal"])}</span>')
    notices = ''
    for n in place.get('notices') or []:
        im = (f'<img src="{MEDIA}{e(n["img"])}" width="{n.get("w", "")}" height="{n.get("h", "")}" alt="" loading="lazy" '
              f'style="max-width:min(100%,{min(int(n.get("w") or 330), 330)}px)">') if n.get('img') else ''
        tx = ''.join(f'<p>{e(t)}</p>' for t in (n.get('text') or []))
        if im or tx:
            notices += f'<div class="notice">{im}{tx}</div>'
    footer = (f'<footer class="ft">{f"<div class=frow>{chr(10).join(cells)}</div>" if cells else ""}'
              f'{f"<div class=notices>{notices}</div>" if notices else ""}</footer>') if (cells or notices) else ''

    desc = hero.get('text') or st.get('text') or ''
    return f'''<!doctype html>
<html lang="{e(d.get('lang') or 'en')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)}</title>
<meta name="description" content="{e(desc)}">
<script>document.documentElement.className='js'</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>
:root{{--g:{G};--c:{C};--s:{S};--m:24px;--gut:24px}}
*,*::before,*::after{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--g);color:var(--c);font:400 18px/22px Arimo,"Helvetica Neue",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:clip}}
img{{display:block;max-width:100%;height:auto}}
a{{color:inherit;text-underline-offset:.12em;transition:opacity .3s,color .3s}}
a:hover{{opacity:.8}}
a:active,button:active{{opacity:.6}}
:focus-visible{{outline:2px solid currentColor;outline-offset:3px}}
::selection{{background:var(--c);color:var(--g)}}
h1,h2,h3,p{{margin:0;font-weight:400}}
button{{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}}

/* opening — pinned; two columns of six, 20px above and below, the name over one picture, the second line under the other */
.intro{{background:var(--g);display:grid;grid-template-columns:1fr 1fr;gap:0 var(--gut);padding:20px var(--m)}}
.intro.pin{{position:sticky;top:0;height:100vh;height:100svh;overflow:hidden;z-index:0}}
.col{{display:flex;flex-direction:column;gap:20px;min-width:0;min-height:0}}
.pic{{flex:1 1 0;min-height:0;overflow:hidden}}
.pic img{{width:100%;height:100%;object-fit:cover}}
.wm{{font-weight:700;text-transform:uppercase;letter-spacing:{TRACK}em;font-size:min(var(--s),var(--sv));line-height:.86;margin:0;padding-top:.07em;flex:none}}
.intro.flat .wm{{font-size:var(--s)}}
.wm span{{display:block;white-space:nowrap}}
.wm2row{{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;flex:none}}
.intro.flat .wm2row{{align-items:flex-start}}
.seal{{width:min(111px,7.7vw);height:auto;flex:none;margin-left:auto{";mix-blend-mode:multiply" if light_ground else ""}}}
.curtain{{display:none}}
.picL{{translate:0 calc(var(--e,0) * var(--dl,0px))}}
.picR{{translate:0 calc(var(--e,0) * var(--dr,0px))}}
.pin .wm2row{{translate:0 calc(var(--e,0) * var(--dw,0px))}}

/* header — sticks to the top once the opening has been scrolled over */
.hdr{{position:sticky;top:0;z-index:10;background:var(--g);display:flex;align-items:center;justify-content:space-between;gap:var(--gut);height:72px;padding:12px var(--m)}}
.logo{{font-weight:700;text-transform:uppercase;letter-spacing:{TRACK}em;font-size:clamp(19px,var(--ls),36px);line-height:1;text-decoration:none;white-space:nowrap}}
.nav{{display:flex;align-items:center;gap:clamp(18px,var(--ng),42px);font-size:14px;line-height:24px;text-transform:uppercase}}
.roll{{display:grid;height:24px;overflow:hidden;text-decoration:none;white-space:nowrap}}
.roll span{{display:block;height:24px;transition:transform .3s}}
.roll:hover span,.roll:focus-visible span{{transform:translateY(-24px)}}
.pill{{display:block;border:1px solid;border-radius:24px;padding:0 20px;line-height:24px;letter-spacing:.143em;text-decoration:none;white-space:nowrap;text-align:center}}
.trig{{display:none}}
.ov{{display:none}}

/* everything after the opening rides over it on the ground colour */
.mods{{position:relative;z-index:1;background:var(--g);display:grid;gap:96px;padding-bottom:96px}}
.band{{background:var(--c);color:var(--g);overflow:hidden;padding-bottom:120px}}
.band.bare{{padding-bottom:58px}}
.lede{{font-size:40px;line-height:42px;padding:90px var(--m) 32px;text-wrap:pretty}}
.strip{{overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}}
.strip::-webkit-scrollbar{{display:none}}
.track{{display:flex;gap:24px;width:max-content;padding:0 var(--m)}}
.cell{{height:var(--h);aspect-ratio:var(--r);flex:none;overflow:hidden}}
.cell img{{width:100%;height:100%;object-fit:cover;-webkit-user-drag:none;user-select:none}}
.strip.run{{overflow:hidden;cursor:grab;touch-action:pan-y}}
.strip.run .track{{padding:0;will-change:transform}}
.strip.drag{{cursor:grabbing}}

.tm{{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);padding:0 var(--m)}}
.tm .txt{{grid-column:7 / 13;grid-row:1}}
.tm .txt.l{{grid-column:1 / 7}}
.tm.half{{min-height:63.33vw}}
.tm.half .txt{{align-self:center;padding:56px 0}}
.halfpic{{grid-column:1 / 7;grid-row:1;margin-left:calc(-1 * var(--m));position:relative;min-height:63.33vw;max-height:var(--ph);overflow:hidden}}
.halfpic img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.blk + .blk{{margin-top:50px}}
.blk h2{{font-size:36px;line-height:1;margin-bottom:38px;text-wrap:balance}}
.blk p + p,.blk .rows + p{{margin-top:22px}}
.blk a:hover{{color:var(--s)}}
.rows{{display:grid;gap:22px}}
.row{{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));column-gap:var(--gut)}}
.row h3{{grid-column:1 / 3;font-size:inherit;line-height:inherit}}
.row > div{{grid-column:3 / 7}}
.ln{{display:flex;justify-content:space-between;gap:24px}}
.ln > span:first-child{{min-width:0;flex:1 1 auto}}
.ln .num{{font-variant-numeric:tabular-nums;flex:0 1 auto;max-width:60%;text-align:right}}
.blk{{overflow-wrap:anywhere}}
.wide{{padding:0 var(--m)}}
.wide img{{width:100%;max-width:var(--w);aspect-ratio:var(--r);object-fit:cover}}

.ft{{position:relative;z-index:1;background:var(--g);font-size:12px;line-height:16px;text-transform:uppercase}}
.frow{{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);row-gap:0;padding:0 var(--m)}}
.frow > *{{grid-column:span 2;padding:8px 0;text-decoration:none}}
.frow .fmark{{grid-column:span 1;padding:6px 0}}
.frow .fmark img{{width:20px;height:20px{";mix-blend-mode:multiply" if light_ground else ""}}}
.frow .legal{{grid-column:span 4 / -1;text-align:right}}
.notices{{padding:48px var(--m) 32px;text-transform:none;display:grid;gap:32px}}
.notice{{max-width:684px}}
.notice img{{margin-bottom:16px}}
.notice p + p{{margin-top:8px}}

/* phone build (the reference turns at 768; the nav row of a longer name needs the turn earlier) */
@media (max-width:767px){{
 :root{{--m:16px;--gut:16px}}
 body{{font-size:16px;line-height:18px}}
 .intro{{display:block;padding:0}}
 .intro.pin{{display:flex;flex-direction:column}}
 .intro .col{{display:block;flex:1 1 0;min-height:0}}
 .intro.pin .col{{display:flex}}
 .pic{{width:100%}}
 .picL,.picR{{translate:none}}
 .picL{{clip-path:inset(calc(var(--e,0) * 100%) 0 0 0)}}
 .picR{{clip-path:inset(0 0 calc(var(--e,0) * 100%) 0)}}
 .wm1{{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}}
 .wm2row{{display:none}}
 .mods{{gap:48px;padding-bottom:48px}}
 .band{{padding-bottom:20px}}
 .band.bare{{padding-bottom:0}}
 .lede{{font-size:25px;line-height:30px;padding:16px 16px 32px}}
 .track{{gap:16px}}
 .cell{{height:var(--hm)}}
 .tm{{display:block;padding:0 16px 20px}}
 .wide img{{aspect-ratio:3 / 4}}
 .tm.half{{min-height:0}}
 .tm.half .txt{{padding:0}}
 .halfpic{{margin:20px 0 0;min-height:0;max-height:none;aspect-ratio:3 / 4}}
 .blk + .blk,.txt + .txt{{margin-top:36px}}
 .blk h2{{font-size:32px;margin-bottom:30px}}
 .blk p + p,.blk .rows + p{{margin-top:18px}}
 .rows{{gap:18px}}
 .frow{{grid-template-columns:repeat(3,1fr);column-gap:0;padding:0;border-top:1px solid}}
 .frow > *,.frow .fmark,.frow .legal{{grid-column:span 1;padding:10px 10px 6px 16px;border-bottom:1px solid;border-right:1px solid;min-height:33px;text-align:left;overflow-wrap:anywhere}}
 .frow > :nth-child(3n){{border-right:0}}
 .frow .legal{{grid-column:1 / -1;border-right:0}}
 .notices{{padding:32px 16px}}
}}
/* the header turns to the phone's (name on a line, three rules, a full-screen list) as soon as its row no longer fits */
@media (max-width:{bp - 1}px){{
 .hdr{{display:block;height:auto;min-height:100px;padding:20px var(--m) 12px;text-align:center}}
 .logo{{display:block;text-align:left;font-size:min(46px,calc((100vw - 2 * var(--m)) / var(--lw)));line-height:1.05;min-height:35px;padding-top:.08em}}
 .nav{{display:none}}
 .trig{{display:inline-block;height:33px;padding:8px 0;margin:0 auto}}
 .trig svg{{display:block;fill:currentColor}}
 .ov{{display:block;background:var(--c);color:var(--g)}}
 .ovh{{display:none}}
 .ovr,.ovs{{display:block;text-decoration:none;border-bottom:2px solid var(--g);overflow:hidden}}
 .ovr{{padding:16px;font-size:24px;line-height:24px;text-transform:uppercase}}
 .ovs{{padding:9px 16px 7px;font-size:16px;line-height:18px}}
 .ovr span,.ovs span{{display:block}}
 .js .ov{{position:fixed;inset:0;z-index:30;display:flex;flex-direction:column;transform:translateY(-100%);visibility:hidden;transition:transform .5s cubic-bezier(.65,0,.35,1),visibility 0s .5s;overflow:auto}}
 .js .ov.open{{transform:none;visibility:visible;transition:transform .5s cubic-bezier(.65,0,.35,1)}}
 .js .ovh{{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;padding:20px 16px 32px;border-bottom:2px solid var(--g);font-weight:700;font-size:24px;line-height:40px;text-transform:uppercase}}
 .js .ovn{{line-height:1.05;padding-top:8px}}
 .js .ovx{{flex:none;width:40px;height:40px}}
 .js .ovb{{margin-top:auto;border-top:2px solid var(--g)}}
 .js .ovb .ovs:last-child{{border-bottom:0}}
 .js .ov span{{transform:translateY(30px);transition:transform 0s .5s}}
 .js .ov .ovn{{transform:none}}
 .js .ov.open .ovr span,.js .ov.open .ovs span{{transform:none;transition:transform 1s cubic-bezier(.22,1,.36,1) calc(.2s + var(--i,0) * .2s)}}
}}

/* load: a curtain of the one colour leaves to the left while the two lines come in from outside, then the pictures */
@media (prefers-reduced-motion:no-preference) and (min-width:768px){{
 .js:not(.in) .pin .curtain{{display:block;position:absolute;inset:0;z-index:5;background:var(--c);transform:translateX(-101%);animation:cur .9s cubic-bezier(.65,0,.35,1) both}}
 .js:not(.in) .pin .wm1{{animation:dn .9s cubic-bezier(.65,0,.35,1) .1s both}}
 .js:not(.in) .pin .wm2row{{animation:up .9s cubic-bezier(.65,0,.35,1) .1s both}}
 .js:not(.in) .pin .picL{{animation:pu .65s cubic-bezier(.22,.8,.3,1) .9s both}}
 .js:not(.in) .pin .picR{{animation:pd .65s cubic-bezier(.22,.8,.3,1) .9s both}}
}}
@keyframes cur{{from{{transform:none;visibility:visible}}to{{transform:translateX(-101%);visibility:hidden}}}}
@keyframes dn{{from{{transform:translateY(-40vh)}}to{{transform:none}}}}
@keyframes up{{from{{transform:translateY(40vh)}}to{{transform:none}}}}
@keyframes pu{{from{{transform:translateY(100vh)}}to{{transform:none}}}}
@keyframes pd{{from{{transform:translateY(-100vh)}}to{{transform:none}}}}
@media (prefers-reduced-motion:reduce){{
 *,*::before,*::after{{transition:none!important;animation:none!important}}
 .picL,.picR,.pin .wm2row{{translate:none!important;clip-path:none!important}}
}}
</style>
</head>
<body>
{opening}
{header}
{overlay}
{main}
{footer}
<script>
(function(){{
 var still=matchMedia('(prefers-reduced-motion:reduce)').matches,root=document.documentElement;
 /* phone menu */
 var ov=document.getElementById('ov'),tr=document.querySelector('.trig'),x=document.querySelector('.ovx');
 if(ov&&tr){{[].forEach.call(ov.querySelectorAll('.ovr,.ovs'),function(r,i){{r.style.setProperty('--i',i)}});
  var set=function(o){{ov.classList.toggle('open',o);tr.setAttribute('aria-expanded',o);if(o&&x)x.focus();else if(!o)tr.focus({{preventScroll:true}})}};
  tr.addEventListener('click',function(){{set(true)}});if(x)x.addEventListener('click',function(){{set(false)}});
  ov.addEventListener('click',function(ev){{if(ev.target.closest('a'))ov.classList.remove('open')}});
  document.addEventListener('keydown',function(ev){{if(ev.key==='Escape'&&ov.classList.contains('open'))set(false)}});}}
 /* opening: while the page rides over it, the pictures leave (one down, one up) and the second line rises to the top row;
    on a phone the two pictures close toward the line between them. Progress is eased cubic-out over one screen. */
 var it=document.querySelector('[data-intro]');
 if(it&&!still){{var L=it.querySelector('.picL'),R=it.querySelector('.picR'),W=it.querySelector('.wm2row'),vh=1;
  var measure=function(){{vh=it.offsetHeight;
   if(L)it.style.setProperty('--dl',(vh-L.offsetTop)+'px');
   if(R)it.style.setProperty('--dr',(-(R.offsetTop+R.offsetHeight))+'px');
   if(W)it.style.setProperty('--dw',(-(W.offsetTop-20))+'px');tick()}};
  var tick=function(){{var p=Math.max(0,Math.min(1,scrollY/vh));it.style.setProperty('--e',(1-Math.pow(1-p,3)).toFixed(4))}};
  addEventListener('scroll',tick,{{passive:true}});addEventListener('resize',measure);addEventListener('load',measure);if('ResizeObserver' in window){{var ro=new ResizeObserver(measure);[it,L,R,W].forEach(function(n){{if(n)ro.observe(n)}})}}
  if(R)R.addEventListener('animationend',function(){{root.classList.add('in')}});setTimeout(function(){{root.classList.add('in')}},2600);measure();}}
 /* strip: drifts left at 33px a second and can be dragged; it only loops when one round of pictures is wide enough
    that no picture is ever on screen twice — otherwise it stays a row that can be pushed sideways */
 [].forEach.call(document.querySelectorAll('[data-strip]'),function(st){{
  var tk=st.firstElementChild,kids=[].slice.call(tk.children),gap=parseFloat(getComputedStyle(tk).columnGap)||24;
  var start=function(){{if(st.classList.contains('run'))return;
   var w=0,mx=0;kids.forEach(function(k){{w+=k.offsetWidth+gap;mx=Math.max(mx,k.offsetWidth)}});
   if(still||!w||w<innerWidth+mx+gap){{
    var sx=null,sl=0;st.addEventListener('mousedown',function(ev){{sx=ev.clientX;sl=st.scrollLeft;ev.preventDefault()}});
    addEventListener('mousemove',function(ev){{if(sx!==null)st.scrollLeft=sl-(ev.clientX-sx)}});addEventListener('mouseup',function(){{sx=null}});
    if(st.scrollWidth>st.clientWidth+2)st.style.cursor='grab';return;}}
   kids.forEach(function(k){{var c=k.cloneNode(true);c.setAttribute('aria-hidden','true');var im=c.querySelector('img');if(im){{im.alt='';im.loading='eager'}}tk.appendChild(c)}});
   tk.style.columnGap=gap+'px';st.classList.add('run');
   var xp=-gap*2,last=0,held=false,px=0,vis=true;
   var put=function(){{xp=((xp%w)-w)%w;tk.style.transform='translate3d('+xp.toFixed(2)+'px,0,0)'}};
   var loop=function(t){{if(last&&!held&&vis)xp-=Math.min(64,t-last)*.033;last=t;put();requestAnimationFrame(loop)}};
   st.addEventListener('pointerdown',function(ev){{if(ev.pointerType==='touch')return;held=true;px=ev.clientX;st.classList.add('drag');st.setPointerCapture(ev.pointerId);ev.preventDefault()}});
   st.addEventListener('pointermove',function(ev){{if(held){{xp+=ev.clientX-px;px=ev.clientX}}}});
   var up=function(){{held=false;st.classList.remove('drag')}};st.addEventListener('pointerup',up);st.addEventListener('pointercancel',up);
   var tx=null;st.addEventListener('touchstart',function(ev){{tx=ev.touches[0].clientX;held=true}},{{passive:true}});
   st.addEventListener('touchmove',function(ev){{var n=ev.touches[0].clientX;xp+=n-tx;tx=n}},{{passive:true}});
   st.addEventListener('touchend',function(){{held=false}});
   if('IntersectionObserver' in window)new IntersectionObserver(function(en){{vis=en[0].isIntersecting}}).observe(st);
   requestAnimationFrame(loop);}};
  if(document.readyState==='complete')start();else addEventListener('load',start);}});
}})();
</script>
</body>
</html>
'''
